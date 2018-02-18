#!/usr/bin/env python
'''
'''

import glob
import logging
import numpy as np
import pandas as pd
from logging import config
from datetime import datetime
from dateutil.relativedelta import relativedelta
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()

class RawDataEPS(object):
    '''
    From EPS forcest to Standard deviation of EPS Long Term Growth Rate
    '''
    def __init__(self):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.symbols_lst = self.get_symbols_lst()
        self.col_lst = SpecBetaConfig.EPS_Raw_data_cols

    def calc_EPS_LTG_stdev(self):
        '''
            create EPS Long-Term Growth rate
        '''
        logger.info("Trying to create EPS growth rate")
        try:
            for symbol in self.symbols_lst[0]:
                EPS_stdev_lst = []
                sum_df = self.get_sum_df(symbol)
                if sum_df.empty:
                    continue
                else:
                    # analyst list for a company
                    anal_lst = sum_df['Analyst'].sort_values().unique()
                    # EPS growth rate
                    EPS_gr_df = self.get_EPS_gr_df(sum_df, anal_lst, symbol)
                    # Standard deviation of the EPS growth rate
                    EPS_stdev_lst.append(self.get_stdev(EPS_gr_df))
                    EPS_stdev_df = pd.DataFrame(EPS_stdev_lst).transpose()
                    EPS_stdev_df.columns = ['STDEV']
                    EPS_stdev_df['Company_code'] = symbol

                    if self.to_csv == True:
                        logger.info("Saving a csv file..")
                        csv_name = self.home_path + self.file_path['EPS_STDEV'] + symbol + '_EPS_stdev.csv'
                        EPS_stdev_df.to_csv(csv_name,index=True)
            logger.info("Succeed in creating EPS growth rate")
            return EPS_stdev_df
        except:
            logger.error('Failed to create EPS growth rate')
            raise

    def get_symbols_lst(self):
        '''
            Stock symbols
        '''
        logger.info("Trying to get stock symbolss")
        try:
            symbols = pd.read_csv(self.home_path + self.file_path['symbols'])
            symbols_lst = symbols.columns.tolist()
            logger.info("Succeed in getting the symbol list")
            return symbols_lst
        except:
            logger.error('Failed to get the symbol list')
            raise

    def get_sum_df(self, symbol):
        '''
            Merge EPS forecast files into a file
        '''
        logger.info("Trying to merge EPS forecast files into a file")
        try:
            Frame=[]
            for fn in glob.iglob(self.home_path + self.file_path['Raw_data_eps']+ symbol + '/*.xlsx'):
                logger.info("Getting EPS file: {}".format(fn))
                df = pd.read_excel(fn, 'Sheet1', index_col=2, names=self.col_lst)
                target_yr = df['Analyst'][df.index=='Accounting Std.'].item()
                df = df[pd.notnull(df.index)]
                df2 = df.iloc[8:,:].copy()
                df2['Company_code'] = symbol
                df2['target_yr'] = target_yr
                Frame.append(df2)
                if Frame:
                    sum_df = pd.concat(Frame)
                    sum_df = sum_df[sum_df['EPS'].notnull()]
                    sum_df['yrmo'] = sum_df.index.map(lambda x: 100*x.year + x.month)
                else:
                    logger.error('Failed to make EPS merged files')
                    raise
            return sum_df
        except:
            logger.error('Failed to make EPS merged files')
            raise

    def get_EPS_gr_df(self, sum_df, anal_lst, symbol):
        '''
            EPS growth rate
        '''
        logger.info("Trying to get EPS growth late")
        try:
            EPS_gr_lst=[]
            for anal in anal_lst:
                logger.info("Getting an analyst: {}".format(anal))
                EPS_gr_dict={}
                anal_df = sum_df[sum_df['Analyst']==anal].sort_index()
                anal_grpd = anal_df.groupby(anal_df.index)
                for idx in anal_df.index.unique():
                    EPS_forecasts = anal_grpd.get_group(idx).sort_values(by='target_yr')['EPS']
                    EPS_forecasts = EPS_forecasts[EPS_forecasts!=0]
                    if EPS_forecasts.shape[0]>1:
                        EPS_gr_dict[EPS_forecasts.index.unique().strftime('%Y-%m-%d').item()] = float(EPS_forecasts[-1]-EPS_forecasts[0])/EPS_forecasts[0]
                    else:
                        EPS_gr_dict[EPS_forecasts.index.unique().strftime('%Y-%m-%d').item()] = 0.0
                EPS_gr_lst.append(EPS_gr_dict)
            if EPS_gr_lst:
                EPS_gr_df = pd.DataFrame(EPS_gr_lst).transpose()
                EPS_gr_df['Company_code'] = symbol
                EPS_gr_df.index = pd.to_datetime(EPS_gr_df.index)
                EPS_gr_df['yrmo'] = EPS_gr_df.index.map(lambda x: 100*x.year + x.month)
                logger.info("Succeed in getting EPS growth rate")
                return EPS_gr_df
            else:
                logger.error('Failed to make EPS growth rate')
        except:
            logger.error('Failed to make EPS growth rate')
            raise

    def get_stdev(self, EPS_gr_df):
        '''
            Calculate standard deviation
        '''
        logger.info("Trying to calculate stdev")
        try:
            yrmo_grpd = EPS_gr_df.groupby('yrmo')
            yrmo_lst  = EPS_gr_df.yrmo.sort_values().unique()
            EPS_stdev_dict={}
            for yrmo in yrmo_lst:
                EPS_stdev_dict[yrmo] = np.nanstd(yrmo_grpd.get_group(yrmo).drop(['Company_code','yrmo'], 1).values)
            logger.info("Succeed in calculating stdev")
            return EPS_stdev_dict
        except:
            logger.error('Failed to calculate stdev')
            raise

if __name__=="__main__":
    rde = RawDataEPS()
    EPS_stdev_df = rde.calc_EPS_LTG_stdev()
