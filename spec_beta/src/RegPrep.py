#!/usr/bin/env python
'''
'''
import logging
from logging import config
import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import datetime
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class RegPrep(object):
    '''
    Regressors and the OLS regression
    '''
    @staticmethod
    def get_regressor(E_Rm, **kwargs):
        '''
        Prepare the regressor for Ordinary least squares regression

        :return: Daily Dimson(1979) regressor:  Rm(t) + 5 lags of Rm(t)
        '''
        # determine which regressor
        if (kwargs.has_key('mo') and not (kwargs.has_key("first_mo") or kwargs.has_key("last_mo"))):
            logger.info("Trying to make a regressor for a month")
            log_str = "a month"
        elif (kwargs.has_key("first_mo") and kwargs.has_key("last_mo")):
            logger.info("Trying to make a regressor for full sample period")
            log_str = "full sample period"
        else:
            raise

        try:
            if (kwargs.has_key("first_mo") and kwargs.has_key("last_mo")):
                first_mo = datetime.strptime(kwargs["first_mo"],'%Y%m')
                last_mo = datetime.strptime(kwargs["last_mo"],'%Y%m')
                if first_mo > last_mo:
                    logger.error("First month should be earlier than the last month")
                    raise
                # no lag (full sample period)
                E_Rm_t = E_Rm[(E_Rm.index < last_mo) & (E_Rm.index >= first_mo)]
            else:
                # no lag (previous 12 months)
                mo = kwargs["mo"]
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
                if (kwargs.has_key('mo') and not (kwargs.has_key("first_mo") or kwargs.has_key("last_mo"))):
                    E_Rm_t_lag = E_Rm[(E_Rm.index < mo + BDay(i+5)) & \
                                (E_Rm.index >= mo-relativedelta(years=1) + BDay(i))]
                else:
                    E_Rm_t_lag = E_Rm[(E_Rm.index < last_mo + BDay(i+5)) \
                                & (E_Rm.index >= first_mo + BDay(i))]
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
        '''
        Run ordinary least squares regression
        '''
        try:
            model = sm.OLS(y,x).fit()
            summary = model.summary()
            if pfunc == True:
                print summary
            else:
                pass
            return model
        except:
            logger.error("Failed to run an OLS regression")
            raise
