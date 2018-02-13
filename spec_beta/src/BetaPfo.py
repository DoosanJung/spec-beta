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

class BetaPfo(object):

    def __init__(self, start_mo, end_mo):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit
        self.start_mo = start_mo
        self.end_mo = end_mo

    def create_pre_ranking_beta_pfos(self):
        '''
        '''
        logger.info("Trying to get all necessary data")
        try:
            # Data Preparation
            rdp = ReturnDataPrep(start_mo = self.start_mo, end_mo = self.end_mo)
            mdp = MiscDataPrep()

            # Stock symbols # 751 companies in KSE
            symbols_lst = rdp.symbols_lst

            # Regression month list # 2010-01-01 ~ 2016-09-01
            reg_mo_lst = rdp.reg_mo_lst

            # Excess return data
            E_Rm = rdp.get_E_Rm_wo_wknds()
            E_Ri = rdp.get_E_Ri_wo_wknds()

            # Miscellaneous data
            m_stock_level_disp = mdp.get_m_stock_level_disp(reg_mo_lst)    # Monthly Stock-level disagreement # 2010-01-01 ~ 2016-09-01
            m_mkt_cap = mdp.get_monthly_mkt_cap(reg_mo_lst)     # Monthly Market_cap # 2010-01-31 ~ 2016-09-30
            m_vol = mdp.get_monthly_vol(reg_mo_lst)     # Monthly Vol # 2010-01-31 ~ 2016-09-30
            logger.info("Succeed in getting all necessary data")
        except:
            logger.error("Failed to get all necessary data")
            raise

        logger.info("Trying to calculate pre-ranking betas & assign each stock to beta pfos")
        try:
            # calculate pre_ranking_beta, assign companies into beta-sorted pfos
            prb = PreRankingBeta(start_mo = self.start_mo, end_mo = self.end_mo)
            beta_pfos_lst = []
            pre_ranking_pfo_lst = []

            # each month, rebalance the beta sorted portfilos
            for i, mo in enumerate(reg_mo_lst):
                # calculate pre_ranking_beta for each stock for the month "mo"
                pre_ranking_beta_df, E_Ri_ret = prb.pre_ranking_beta(i = i, \
                                                mo = mo, \
                                                E_Rm = E_Rm, \
                                                E_Ri = E_Ri, \
                                                symbols_lst = symbols_lst, \
                                                m_stock_level_disp = m_stock_level_disp, \
                                                m_mkt_cap = m_mkt_cap, \
                                                m_vol = m_vol)
                pre_ranking_pfo_lst.append(pre_ranking_beta_df)

                # assign companies into twenty beta-sorted portfolios
                pfos = prb.assign_beta_pfo(df = pre_ranking_beta_df, \
                                                mo = mo, \
                                                E_Ri_ret = E_Ri_ret)
                beta_pfos_lst.append(pfos)
                twenty_beta_pfos = pd.concat(beta_pfos_lst)
                pre_ranking_pfos = pd.concat(pre_ranking_pfo_lst)
            logger.info("Succed in assigning each stock to beta pfos")
            return twenty_beta_pfos, pre_ranking_pfos
        except:
            logger.error("Failed to calculate pre-ranking betas & assign each stock to beta pfos")
            raise

if __name__=="__main__":
    bp = BetaPfo(201001,201709)
    twenty_beta_pfos, pre_ranking_pfos = bp.create_pre_ranking_beta_pfos()
