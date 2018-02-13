#!/usr/bin/env python
'''
'''

import unittest
import pandas as pd
import logging
from logging import config
from datetime import datetime
from dateutil.relativedelta import relativedelta
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep
from spec_beta.src.MiscDataPrep import MiscDataPrep

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()

class DataPrepTestCase(unittest.TestCase):
    '''
    Data preparation uniittest
    '''
    def test_return_data_prep(self):
        '''
        test to fetch return data
        '''
        result = False
        start_mo = 201001
        end_mo = 201709

        rdp = ReturnDataPrep(start_mo, end_mo)
        rdp.home_path = SpecBetaConfig.HOME_PATH
        rdp.file_path = SpecBetaConfig.FILE_PATH

        try:
            logger.info("Trying to get symbols")
            rdp.symbols_lst = rdp.get_symbols_lst()

            logger.info("Trying to get regression months")
            rdp.reg_mo_lst = rdp.get_reg_mo_lst()

            logger.info("Trying to get daily stock returns")
            rdp.RET_D_KSE = rdp.get_Ri_wo_wknds()

            logger.info("Trying to get daily market returns")
            rdp.RET_MKT_D_KSE = rdp.get_Rm_wo_wknds()

            logger.info("Trying to get daily risk-free returns")
            rdp.RF_CALL1 = rdp.get_Rf_wo_wknds()

            logger.info("Trying to get exccess daily stock returns")
            E_Ri = rdp.get_E_Ri_wo_wknds()

            logger.info("Trying to get excess daily market returns")
            E_Rm = rdp.get_E_Rm_wo_wknds()

            result = True
        except:
            raise

        self.assertEqual(True,result)


    def test_misc_data_prep(self):
        '''
        test to fetch miscellaneous data
        '''
        result = False
        reg_mo_lst = pd.Series(pd.date_range('20100101','20160901', freq='MS'))

        mdp = MiscDataPrep()
        mdp.home_path = SpecBetaConfig.HOME_PATH
        mdp.file_path = SpecBetaConfig.FILE_PATH

        try:
            logger.info("Trying to get daily stock-level disagreement")
            mdp.m_stock_level_disp = mdp.get_m_stock_level_disp(reg_mo_lst)

            logger.info("Trying to get monthly mkt cap")
            mdp.m_mkt_cap = mdp.get_monthly_mkt_cap(reg_mo_lst)

            logger.info("Trying to get monthly vol")
            mdp.m_vol = mdp.get_monthly_vol(reg_mo_lst)

            logger.info("Trying to get SMB, HML, UMD")
            mdp.SMB_HML_UMD = mdp.get_smb_hml_umd(reg_mo_lst)

            logger.info("Trying to get Dividend/Price_ratio")
            mdp.monthly_DP = mdp.get_D_P(reg_mo_lst)

            logger.info("Trying to get Monthly CPI yearly inflation")
            mdp.monthly_CPI_yearly_inflation = mdp.get_inflation(reg_mo_lst)

            logger.info("Trying to get Monthly CP - CD spread")
            mdp.m_CP_CD_spread = mdp.get_CP_CD_spread(reg_mo_lst)

            result = True
        except:
            raise

        self.assertEqual(True,result)

if __name__=="__main__":
    unittest.main()
