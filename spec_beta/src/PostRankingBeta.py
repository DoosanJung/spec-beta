#!/usr/bin/env python
'''
'''
import logging
from logging import config
import pandas as pd
import numpy as np
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.RegPrep import RegPrep

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class PostRankingBeta(object):
    '''
    Regression to calculate post ranking Betas
    '''
    def __init__(self, start_mo, end_mo):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit
        self.start_mo = start_mo
        self.end_mo = end_mo

    def post_ranking_beta(self, E_Rm, pfo_rets):
        '''
        '''
        logger.info("Trying to calculate post_ranking betas")
        try:
            # OLS each beta pfo
            post_betas = {}

            # X + constant: independent variables
            # Percent unit for regression
            regressor_Rm = RegPrep.get_regressor(E_Rm = E_Rm, \
                                                first_mo = self.start_mo, \
                                                last_mo = self.end_mo)

            # Y : a dependent varialbe
            pfo_lst = pfo_rets.columns.tolist()
            for i, pfo in enumerate(pfo_lst):
                y = pfo_rets[pfo]*100 # to make percent unit
                models = RegPrep.run_ols(y, regressor_Rm, pfunc=False)
                sum_beta = np.sum(models.params)
                post_betas[i] = sum_beta

            post_betas_df = pd.DataFrame(post_betas, index=['post_beta']).transpose()
            renamed_pfo_lst = [u'pfo_00', u'pfo_01', u'pfo_02', u'pfo_03', u'pfo_04', u'pfo_05', \
                            u'pfo_06', u'pfo_07', u'pfo_08', u'pfo_09', u'pfo_10', u'pfo_11', u'pfo_12',\
                             u'pfo_13', u'pfo_14', u'pfo_15', u'pfo_16', u'pfo_17', u'pfo_18', u'pfo_19',]
            post_betas_df.index = renamed_pfo_lst
            logger.info("Succeed in calculating post_ranking betas")
            return post_betas_df
        except:
            logger.error("Failed to calculate post_ranking betas")
            raise
