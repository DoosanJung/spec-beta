'''
'''

import logging
from logging import config
import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
from tqdm import tqdm
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

        # Data Preparation
        rdp = ReturnDataPrep(start_mo = self.start_mo, end_mo = self.end_mo)
        mdp = MiscDataPrep(start_mo = self.start_mo, end_mo = self.end_mo)

        # Stock symbols # 751 companies in KSE
        symbols_lst = rdp.symbols_lst

        # Regression month list # 2010-01-01 ~ 2016-09-01
        reg_mo_lst = rdp.reg_mo_lst

        # Excess return data
        E_Rm = rdp.get_E_Rm_wo_wknds()
        E_Ri = rdp.get_E_Ri_wo_wknds()

        # Miscellaneous data
        m_stock_level_disp = mdp.get_m_stock_level_disp()    # Monthly Stock-level disagreement # 2010-01-01 ~ 2016-09-01
        m_mkt_cap = mdp.get_monthly_mkt_cap()     # Monthly Market_cap # 2010-01-31 ~ 2016-09-30
        m_vol = mdp.get_monthly_vol()     # Monthly Vol # 2010-01-31 ~ 2016-09-30

        #
        prb = PreRankingBeta(start_mo = self.start_mo, end_mo = self.end_mo)
        Twenty_Beta_Pfos = []
        AggDisp_wo_wknds = []
        for i, mo in tqdm(enumerate(reg_mo_lst)):
            # calculate pre_ranking_E_Ri_retbeta for each stock for the month "mo"
            pre_ranking_beta_df, E_Ri_ret = prb.pre_ranking_beta(i, mo, \
                                            E_Rm = E_Rm, \
                                            E_Ri = E_Ri, \
                                            symbols_lst = symbols_lst, \
                                            m_stock_level_disp = m_stock_level_disp, \
                                            m_mkt_cap = m_mkt_cap, \
                                            m_vol = m_vol)
            AggDisp_wo_wknds.append(pre_ranking_beta_df)

            # monthly table1
            # for the month mo
            pfos, pfo_idx = assign_beta_pfo(pre_ranking_beta_df, mo, E_Ri_ret, to_csv)
            Twenty_Beta_Pfos.append(pfos)
            Table1_df_monthly_wo_wknds = pd.concat(Twenty_Beta_Pfos)
            AggDisp_df_wo_wknds = pd.concat(AggDisp_wo_wknds)



if __name__=="__main__":
    prb = PreRankingBeta(201001,201709)
    prb.create_pre_ranking_beta_pfos()
