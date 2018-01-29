#!/usr/bin/env python
'''
'''
import logging
from logging import config
import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep
from spec_beta.src.MiscDataPrep import MiscDataPrep

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class RegPrep(object):
    '''
    Regressors
    '''

    @staticmethod
    def get_regressor(E_Rm, mo):
        '''
            :return: Daily Dimson(1979) regressor:  Rm(t) + 5 lags of Rm(t)
        '''
        # Initialize regressor_Rm
        regressor_Rm = pd.DataFrame()
        # no lag (previous 12 months)
        E_Rm_t = E_Rm[(E_Rm.index < mo)& (E_Rm.index >= mo-relativedelta(years=1))]
        # Save the idx
        regressor_idx = E_Rm_t.index
        # Drop the idx
        E_Rm_t = E_Rm_t.reset_index(drop=True)
        # concatenate no lag
        regressor_Rm = pd.concat([regressor_Rm, E_Rm_t],axis=1, ignore_index=True)
        # concat from lag 1 to lag 5
        for i in xrange(1,6):
            E_Rm_t_lag = E_Rm[(E_Rm.index < mo+timedelta(days=i+5))&(E_Rm.index >= mo-relativedelta(years=1)+timedelta(days=i))]
            # Drop the idx for lag 1 to lag 5
            E_Rm_t_lag = E_Rm_t_lag[:len(E_Rm_t)]
            E_Rm_t_lag = E_Rm_t_lag.reset_index(drop=True)
            regressor_Rm = pd.concat([regressor_Rm, E_Rm_t_lag],ignore_index=True, axis=1)
        regressor_Rm['mo'] = regressor_idx
        regressor_Rm.set_index('mo',inplace=True)
        regressor_Rm = regressor_Rm*100
        regressor_Rm = sm.add_constant(regressor_Rm)
        return regressor_Rm
