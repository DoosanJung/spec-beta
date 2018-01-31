#!/usr/bin/env python
'''
From EPS forcest to Standard deviation of EPS Long Term Growth Rate
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
    '''
    def __init__(self):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.symbols_lst = self.get_symbols_lst()
        self.col_lst = SpecBetaConfig.EPS_Raw_data_cols

    def create_EPS_LTG(self):
        '''
            create standard deviation of EPS growth rate
        '''
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
                csv_name = self.home_path + self.file_path['EPS_STDEV'] + symbol + '_EPS_stdev.csv'
                if self.to_csv == True:
                    EPS_stdev_df.to_csv(csv_name,index=True)
        return EPS_stdev_df

    def get_symbols_lst(self):
        '''
            Stock symbols
        '''
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
        Frame=[]
        for fn in glob.iglob(self.home_path + self.file_path['Raw_data_eps']+ symbol + '/*.xlsx'):
            print fn
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
                print 'NO ESTIMATES! NO SUM DF'
                sum_df = pd.DataFrame()
        return sum_df

    def get_EPS_gr_df(self, sum_df, anal_lst, symbol):
        '''
            EPS growth rate
        '''
        EPS_gr_lst=[]
        for anal in anal_lst:
            print anal
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
            return EPS_gr_df
        else:
            print 'NO EPS GR DF'

    def get_stdev(self, EPS_gr_df):
        '''
            Standard deviation of EPS growth rate
        '''
        yrmo_grpd = EPS_gr_df.groupby('yrmo')
        yrmo_lst  = EPS_gr_df.yrmo.sort_values().unique()
        EPS_stdev_dict={}
        for yrmo in yrmo_lst:
            EPS_stdev_dict[yrmo] = np.nanstd(yrmo_grpd.get_group(yrmo).drop(['Company_code','yrmo'], 1).values)
        return EPS_stdev_dict

if __name__=="__main__":
    rde = RawDataEPS()
    EPS_stdev_df = rde.create_EPS_LTG()
