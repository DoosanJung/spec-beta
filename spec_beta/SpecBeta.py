#!/usr/bin/env python
'''
'''
import logging
from logging import config
from spec_beta.src.BetaPfo import BetaPfo

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()

class SpecBeta(object):
    '''
    '''
    def __init__(self, start_mo, end_mo):
        self.start_mo = start_mo
        self.end_mo = end_mo

    def create_beta_sorted_pfos(self):
        '''
        1st stage: create beta-sorted portfilos
        '''
        logger.info('creating beta-sorted portfolios')
        try:
            bp = BetaPfo(self.start_mo,self.end_mo)

            # calculate pre_ranking beta, assign each stock into beta_sorted portfolios
            beta_sorted_pfos, pfo_rets_ew, pfo_rets_vw = bp.create_pre_ranking_beta_pfos()

            # calculate post_ranking beta for each beta_sorted portfolios
            post_betas_ew = bp.create_post_ranking_betas(pfo_rets_ew)
            post_betas_vw = bp.create_post_ranking_betas(pfo_rets_vw)

            # summary tables
            self.Table_df_ew = bp.summarize_beta_pfos(df =beta_sorted_pfos, \
                                            post_betas = post_betas_ew, \
                                            ew="equal weighted")
            self.Table_df_vw = bp.summarize_beta_pfos(df =beta_sorted_pfos, \
                                            post_betas = post_betas_vw, \
                                            vw="value weighted")
            # visualize
            bp.visualize(self.Table_df_ew, self.Table_df_vw)

            logger.info("Succeed in creating beta-sorted portfolios")
        except:
            logger.error("Failed to create beta-sorted portfolios")
            raise

    def create_aggregated_disagreement(self):
        '''
        2nd stage: aggregated investors' disagreement on EPS Long-term Growth Rate
        '''
        pass


if __name__=='__main__':
    # sample period: 2010-01-01 ~ 2017-09-01
    specBeta = SpecBeta('201001', '201709')
    specBeta.create_beta_sorted_pfos()
    Table_df_ew = specBeta.Table_df_ew
    Table_df_vw = specBeta.Table_df_vw
