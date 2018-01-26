#!/usr/bin/env python
'''
'''
import pandas as pd
import logging
from logging import config
from datetime import date, timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep
from spec_beta.src.MiscDataPrep import MiscDataPrep

logger = logging.getLogger()


class RegPrep(object):
    '''
    Regressors
    '''
    def __init__(self):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit

    #######################################################################
    #TODO: below

    def get_reg_mo_lst(self, start_mo, end_mo):
        '''
        OUTPUT: Monthly regression months
        '''
        mo_lst = pd.read_csv(self.home_path + self.file_path['year_and_month],header=None, names='m')
        mo_lst = mo_lst.m.apply(lambda mo: datetime.strptime(str(mo), "%Y%m"))
        reg_mo_lst = mo_lst[(mo_lst >= datetime.strptime(str(start_mo), "%Y%m"))&(mo_lst <= datetime.strptime(str(end_mo), "%Y%m"))]
        reg_mo_lst = reg_mo_lst.reset_index(drop=True)
        # reg_mo_lst = reg_mo_lst[:81]
        reg_mo_lst = reg_mo_lst[reg_mo_lst <= datetime.strptime(str(end_mo), "%Y%m") - relativedelta(years=1)]
        return reg_mo_lst

    # Each month...
    def get_regressor(self, E_Rm,mo):
        '''
        INPUT: month (t) , convert decimal >> percent
        OUTPUT: Daily Dimson(1979) regressor:  Rm(t) + 5 lags of Rm(t)
        '''
        # Init regressor_Rm
        regressor_Rm = pd.DataFrame()
        # no lag (previous 12 months)
        E_Rm_t = E_Rm[(E_Rm.index < mo)& (E_Rm.index >= mo-relativedelta(years=1))]
        # Save the idx
        regressor_idx = E_Rm_t.index
        # Drop the idx
        E_Rm_t = E_Rm_t.reset_index(drop=True)
        # concat no lag
        regressor_Rm = pd.concat([regressor_Rm, E_Rm_t],axis=1, ignore_index=True)
        # concat from lag 1 to lag 5
        for i in xrange(1,6):
            E_Rm_t_lag = E_Rm[(E_Rm.index < mo+timedelta(days=i+5))&(E_Rm.index >= mo-relativedelta(years=1)+timedelta(days=i))]
            # Drop the idx for lag 1 to lag 5
            # E_Rm_t_lag = E_Rm_t_lag.shift(periods=-i)
            E_Rm_t_lag = E_Rm_t_lag[:len(E_Rm_t)]
            E_Rm_t_lag = E_Rm_t_lag.reset_index(drop=True)
            regressor_Rm = pd.concat([regressor_Rm, E_Rm_t_lag],ignore_index=True, axis=1)
        regressor_Rm['mo'] = regressor_idx
        regressor_Rm.set_index('mo',inplace=True)
        regressor_Rm = regressor_Rm*100
        regressor_Rm = sm.add_constant(regressor_Rm)
        return regressor_Rm

    # Full sample period
    def get_regressor_full_sample(self, E_Rm, R_pfo_df, decimal_unit):
        '''
        INPUT: Full sample period ( R_pfo_df.index )
        OUTPUT: Daily Dimson(1979) regressor:  Rm(t) + 5 lags of Rm(t)
        '''
        # Init regressor_Rm
        regressor_Rm = pd.DataFrame()
        # Save the idx
        E_Rm_t = E_Rm[    (E_Rm.index >= R_pfo_df.index.min())   & (E_Rm.index <= R_pfo_df.index.max())   ] # 2010-01-01 ~ 2016-09-30
        regressor_idx = E_Rm_t.index
        # Drop the idx
        E_Rm_t = E_Rm_t.reset_index(drop=True)
        # concat no lag
        regressor_Rm = pd.concat([regressor_Rm, E_Rm_t],axis=1, ignore_index=True)
        # concat from lag 1 to lag 5
        for i in xrange(1,6):
            E_Rm_t_lag = E_Rm[    (E_Rm.index >= datetime.strptime(R_pfo_df.index.min(),'%Y-%m-%d') + timedelta(days=i)) \
                                &  (E_Rm.index <= datetime.strptime(R_pfo_df.index.max(),'%Y-%m-%d') + timedelta(days=i+5))   ]
            # Drop the idx for lag 1 to lag 5
            # E_Rm_t_lag = E_Rm_t_lag.shift(periods=-i)
            E_Rm_t_lag = E_Rm_t_lag[:len(E_Rm_t)]
            E_Rm_t_lag = E_Rm_t_lag.reset_index(drop=True)
            regressor_Rm = pd.concat([regressor_Rm, E_Rm_t_lag],ignore_index=True, axis=1)
        regressor_Rm['mo'] = regressor_idx
        regressor_Rm.set_index('mo',inplace=True)
        regressor_Rm = regressor_Rm*100
        regressor_Rm = sm.add_constant(regressor_Rm)
