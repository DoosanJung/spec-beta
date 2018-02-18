#!/usr/bin/env python
'''
'''
import re
import logging
from logging import config
import pandas as pd
from itertools import compress
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep
from spec_beta.src.MiscDataPrep import MiscDataPrep
from spec_beta.src.RegPrep import RegPrep
from spec_beta.src.PreRankingBeta import PreRankingBeta
from spec_beta.src.PostRankingBeta import PostRankingBeta

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()

class BetaPfo(object):
    '''
    Construct twenty beta-sorted portfolios
    '''
    def __init__(self, start_mo, end_mo):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit
        self.start_mo = start_mo
        self.end_mo = end_mo

    def create_pre_ranking_beta_pfos(self):
        '''
            get pre ranking betas for each stock
            by regressing excess stock return on excess market return
            for previous one year
        '''
        logger.info("Trying to get all necessary data")
        try:
            # Data Preparation
            return_data = ReturnDataPrep(start_mo = self.start_mo, end_mo = self.end_mo)
            misc_data = MiscDataPrep()

            # Stock symbols # 751 companies in KSE
            symbols_lst = return_data.symbols_lst

            # Regression month list # 2010-01-01 ~ 2016-09-01
            reg_mo_lst = return_data.reg_mo_lst

            # Excess return data
            self.E_Rm = return_data.get_E_Rm_wo_wknds()
            E_Ri = return_data.get_E_Ri_wo_wknds()

            # Miscellaneous data
            m_stock_level_disp = misc_data.get_m_stock_level_disp(reg_mo_lst)    # Monthly Stock-level disagreement # 2010-01-01 ~ 2016-09-01
            m_mkt_cap = misc_data.get_monthly_mkt_cap(reg_mo_lst)     # Monthly Market_cap # 2010-01-31 ~ 2016-09-30
            m_vol = misc_data.get_monthly_vol(reg_mo_lst)     # Monthly Vol # 2010-01-31 ~ 2016-09-30
            logger.info("Succeed in getting all necessary data")
        except:
            logger.error("Failed to get all necessary data")
            raise

        logger.info("Trying to calculate pre-ranking betas & assign each stock to beta pfos")
        try:
            # calculate pre_ranking_beta, assign companies into beta-sorted pfos
            pre_betas = PreRankingBeta(start_mo = self.start_mo, end_mo = self.end_mo)
            beta_sorted_pfos = {}
            pre_ranking_pfos = {}
            pfo_rets_ew = {}
            pfo_rets_vw = {}
            # each month, rebalance the beta sorted portfilos
            for i, mo in enumerate(reg_mo_lst):
                # calculate pre_ranking_beta for each stock for the month "mo"
                pre_ranking_beta_df, E_Ri_ret = pre_betas.pre_ranking_beta(i = i, \
                                                mo = mo, \
                                                E_Rm = self.E_Rm, \
                                                E_Ri = E_Ri, \
                                                symbols_lst = symbols_lst, \
                                                m_stock_level_disp = m_stock_level_disp, \
                                                m_mkt_cap = m_mkt_cap, \
                                                m_vol = m_vol)

                # assign companies into twenty beta-sorted portfolios
                pfos = pre_betas.assign_beta_pfo(df = pre_ranking_beta_df, \
                                                mo = mo, \
                                                E_Ri_ret = E_Ri_ret)
                beta_sorted_pfos[mo.strftime('%Y%m')] = pfos

                # portfolio daily returns
                if i < (len(reg_mo_lst)-1):
                    # one month daily return
                    pfo_rets_ew[mo.strftime('%Y%m')] = pre_betas.ret1_ew
                    pfo_rets_vw[mo.strftime('%Y%m')] = pre_betas.ret1_vw
                elif i == (len(reg_mo_lst)-1):
                    # for last month, one year daily returns needed
                    pfo_rets_ew[mo.strftime('%Y%m')] = pre_betas.ret12_ew
                    pfo_rets_vw[mo.strftime('%Y%m')] = pre_betas.ret12_vw

                if self.to_csv==True:
                    logger.info("Saving csv files..")
                    pd.concat(beta_sorted_pfos).to_csv('beta_sorted_pfos.csv')
                    pd.concat(pre_ranking_pfos).to_csv('pre_ranking_pfos.csv')
                else:
                    pass
            beta_sorted_pfos = pd.concat(beta_sorted_pfos, names = [u'yrmo',u'field'])
            pfo_rets_ew = pd.concat(pfo_rets_ew, names= [u'yrmo',u'datetime'])
            pfo_rets_vw = pd.concat(pfo_rets_vw, names= [u'yrmo',u'datetime'])
            logger.info("Succeed in assigning each stock to beta pfos")
            return beta_sorted_pfos,  pfo_rets_ew, pfo_rets_vw
        except:
            logger.error("Failed to calculate pre-ranking betas & assign each stock to beta pfos")
            raise

    def create_post_ranking_betas(self, pfo_rets):
        '''
            get post ranking betas for each beta-sorted portfolio
            by regressing each portfilo's excess return on excess market return
            for a full sample period
        '''
        logger.info("Trying to create post-ranking betas for each portfolio")
        try:
            pfo_rets = pfo_rets.reset_index().set_index('datetime').drop('yrmo', axis=1)
            post_betas = PostRankingBeta(start_mo = self.start_mo, end_mo = self.end_mo)
            post_betas_df = post_betas.post_ranking_beta(self.E_Rm, pfo_rets)
            logger.info("Succeed in creating post-ranking betas for each portfilo")
            return post_betas_df
        except:
            logger.error("Failed to create post-ranking betas for each portfolio")
            raise

    def summarize_beta_pfos(self, df, post_betas, **kwargs):
        '''
            create a table describing the beta-sorted portfolios
        '''
        logger.info("Trying to create a summary table ")
        lst = SpecBetaConfig.Beta_pfos_cols
        try:
            if (kwargs.has_key("ew") and not kwargs.has_key("vw")):
                cols = compress(lst, [not(re.search("vw",x)) for x in lst])
            elif (kwargs.has_key("vw") and not kwargs.has_key("ew")):
                cols = compress(lst, [not(re.search("ew",x)) for x in lst])

            df = df.reset_index().set_index('field').drop("yrmo", axis=1)
            Table_df = self.get_Table(df=df, cols=cols)
            Table_df = pd.concat([Table_df, post_betas.transpose()])
            logger.info("Succeed in creating a summary table")
            logger.info(Table_df)
            return Table_df
        except:
            logger.error("Failed to create a summary table")
            raise

    def get_Table(self, df, cols):
        try:
            Table={}
            for col in cols:
                Table[col]=df.transpose()[col].mean(axis=1)
            Table_df = pd.DataFrame(Table)
            return Table_df.transpose()
        except:
            raise

if __name__=="__main__":
    bp = BetaPfo(201001,201709)
    beta_sorted_pfos, pfo_rets_ew, pfo_rets_vw = bp.create_pre_ranking_beta_pfos()
    post_betas_ew = bp.create_post_ranking_betas(pfo_rets_ew))
    post_betas_vw = bp.create_post_ranking_betas(pfo_rets_vw))
    Table_df_ew = summarize_beta_pfos(beta_sorted_pfos, post_betas_ew, ew="equal weighted")
    Table_df_vw = summarize_beta_pfos(beta_sorted_pfos, post_betas_vw, vw="value weighted")
