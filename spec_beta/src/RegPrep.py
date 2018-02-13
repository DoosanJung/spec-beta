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
        # determine which regressor
        if isinstance(mo, tuple):
            logger.info("Trying to make a regressor for full sample period")
            log_str = "full sample period"
        else:
            logger.info("Trying to make a regressor for a month")
            log_str = "a month"

        try:
            if isinstance(mo, tuple):
                first_mo, last_mo = mo
                if first_mo > last_mo:
                    logger.error("ValueError: First month should be earlier than the last month")
                    raise
                # no lag (full sample period)
                E_Rm_t = E_Rm[(E_Rm.index < last_mo) & (E_Rm.index >= first_mo)]
            else:
                # no lag (previous 12 months)
                E_Rm_t = E_Rm[(E_Rm.index < mo) & (E_Rm.index >= mo-relativedelta(years=1))]

            # Initialize regressor_Rm
            regressor_Rm = pd.DataFrame()
            # Save the idx
            regressor_idx = E_Rm_t.index
            # Drop the idx
            E_Rm_t = E_Rm_t.reset_index(drop=True)
            # concatenate no lag
            regressor_Rm = pd.concat([regressor_Rm, E_Rm_t], axis=1, ignore_index=True)
            # concat from lag 1 to lag 5
            for i in xrange(1,6):
                if isinstance(mo, tuple):
                    E_Rm_t_lag = E_Rm[(E_Rm.index < last_mo + timedelta(days=i+5)) \
                                & (E_Rm.index >= first_mo + timedelta(days=i))]
                else:
                    E_Rm_t_lag = E_Rm[(E_Rm.index < mo+timedelta(days=i+5)) & \
                                (E_Rm.index >= mo-relativedelta(years=1)+timedelta(days=i))]
                # Drop the idx for lag 1 to lag 5
                E_Rm_t_lag = E_Rm_t_lag[:len(E_Rm_t)]
                E_Rm_t_lag = E_Rm_t_lag.reset_index(drop=True)
                regressor_Rm = pd.concat([regressor_Rm, E_Rm_t_lag],ignore_index=True, axis=1)

            regressor_Rm['mo'] = regressor_idx
            regressor_Rm.set_index('mo',inplace=True)
            regressor_Rm = regressor_Rm*100
            # add constant 1 to the regressor
            regressor_Rm = sm.add_constant(regressor_Rm)
            logger.info("Succeed in making a regressor for {}".format(log_str))
            return regressor_Rm
        except:
            logger.error("Failed to make a regressor for {}".format(log_str))
            raise

    @staticmethod
    def run_ols(y, x, pfunc):
        model = sm.OLS(y,x).fit()
        summary = model.summary()
        if pfunc == True:
            print summary
        else:
            pass
        return model
