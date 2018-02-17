#!/usr/bin/env python
'''
'''

import logging
from logging import config
import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep
from spec_beta.src.MiscDataPrep import MiscDataPrep
from spec_beta.src.RegPrep import RegPrep
from spec_beta.src.PreRankingBeta import PreRankingBeta


config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()

class RetCal(object):
    '''
    Calculate returns for various portfolios
    '''
    def __init__(self):
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit

    def calc_ret(self, df, col):
        '''
        '''
        logger.info("Trying to caclulate returns")
        try:
            calc_ret={}
            df_grpd = df.groupby('yrmo')
            for yrmo in df.yrmo.unique():
                calc_ret[yrmo] = (df_grpd.get_group(yrmo)[col] + 1).dropna().product()-1
            calc_ret_df = pd.DataFrame(calc_ret, index=[col+'_rm12mo']).transpose()
            calc_ret_df.index = pd.to_datetime(calc_ret_df.index, format='%Y%m')
            logger.info("Succeed in calculating calc_ret")
            return calc_ret_df
        except:
            logger.error("Failed to calculate returns")
            raise

    def get_ret_12mo(self, ret, reg_mo_lst, decimal_unit, to_csv):
        '''
        '''
        ret_12mo = ret[  (ret.index >= reg_mo_lst.min()-relativedelta(years=1)) \
                                    & (ret.index < reg_mo_lst.max()+relativedelta(months=1)) ]
        ret_12mo_mo_df = pd.Series(ret_12mo.index).to_frame('idx')
        ret_12mo_mo_df['yrmo'] = ret_12mo_mo_df.idx.apply(lambda x: datetime.strftime(x, '%Y%m'))
        # ret_12mo_mo_df['rm_mo'] = ret_12mo_mo_df.idx.apply(lambda x: datetime.strftime(x, '%Y%m'))
        ret_12mo_mo_df = ret_12mo_mo_df.set_index('idx')
        ret_12mo_df = pd.concat([ret_12mo,ret_12mo_mo_df],axis=1)

        result = calc_ret(ret_12mo_df,'Rm')
        if self.decimal_unit==True:
            if self.to_csv==True:
                result.to_csv('result.csv')
            return result
        else:
            return result*100
            if self.to_csv==True:
                result_perc = result*100
                result_perc.to_csv('return_12month_df_perc.csv')
