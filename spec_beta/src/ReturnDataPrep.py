#!/usr/bin/env python
'''
'''
import logging
from logging import config
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class ReturnDataPrep(object):
    '''
    Return data such as excess stock return, excess market return
    '''
    def __init__(self, start_mo, end_mo):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit
        self.start_mo = start_mo
        self.end_mo = end_mo
        self.reg_mo_lst = self.get_reg_mo_lst()
        self.symbols_lst = self.get_symbols_lst()

    def get_symbols_lst(self):
        '''
            Stock symbols
        '''
        try:
            symbols = pd.read_csv(self.home_path + self.file_path['symbols'])
            symbols_lst = symbols.columns.tolist()
            logger.info("Succeed in getting the symbol list")
            return symbols_lst
        except:
            logger.error('Failed to get the symbol list')
            raise

    def get_reg_mo_lst(self):
        '''
            Monthly regression months
        '''
        try:
            mo_lst = pd.read_csv(self.home_path + self.file_path['year_and_month'],header=None, names='m')
            mo_lst = mo_lst.m.apply(lambda mo: datetime.strptime(str(mo), "%Y%m"))
            reg_mo_lst = mo_lst[(mo_lst >= datetime.strptime(str(self.start_mo), "%Y%m"))&(mo_lst <= datetime.strptime(str(self.end_mo), "%Y%m"))]
            reg_mo_lst = reg_mo_lst.reset_index(drop=True)
            # reg_mo_lst = reg_mo_lst[:81]
            reg_mo_lst = reg_mo_lst[reg_mo_lst <= datetime.strptime(str(self.end_mo), "%Y%m") - relativedelta(years=1)]
            logger.info("Succeed in getting the regression month list")
            return reg_mo_lst
        except:
            logger.info("Failed to get the regression month list")
            raise

    def get_Ri_wo_wknds(self):
        '''
            Daily stock return (weekends removed)
        '''
        try:
            RET_D_KSE = pd.read_csv(self.home_path + self.file_path['daily_stock_return'],index_col=0)
            RET_D_KSE.index = pd.to_datetime(RET_D_KSE.index, dayfirst=True)
            logger.info("Succeed in getting the stock return")
            if self.decimal_unit==True:
                RET_D_KSE = RET_D_KSE/float(100) # percentage to decimal
                return RET_D_KSE
            else:
                return RET_D_KSE # percentage
        except:
            logger.error('Failed to get stock return')
            raise

    def get_Rm_wo_wknds(self):
        '''
            Daily market return (weekends removed)
        '''
        try:
            RET_MKT_D_KSE = pd.read_csv(self.home_path + self.file_path['daily_market_return'],\
                                        index_col=0, header=None, names=['Rm'])
            RET_MKT_D_KSE.index = pd.to_datetime(RET_MKT_D_KSE.index, dayfirst=True)
            logger.info("Succeed in getting market return")
            if self.decimal_unit==True:
                RET_MKT_D_KSE = RET_MKT_D_KSE/float(100) # percentage to decimal
                return RET_MKT_D_KSE
            else:
                return RET_MKT_D_KSE # percentage
        except:
            logger.info("Failed to get market return")
            raise

    def get_Rf_wo_wknds(self):
        '''
            Daily risk-free return (weekends removed)
        '''
        try:
            RF_CALL1 = pd.read_csv(self.home_path + self.file_path['risk_free_return'],\
                                    index_col=0, header=None, names=['RF_CALL1'])
            RF_CALL1.index = pd.to_datetime(RF_CALL1.index)
            RF_CALL1 = RF_CALL1[RF_CALL1.index >= self.reg_mo_lst.min()-relativedelta(years=1)]
            logger.info("Succeed in getting the risk free return")
            if self.decimal_unit==True:
                RF_CALL1 = RF_CALL1/float(100) # percentage to decimal
                return RF_CALL1
            else:
                return RF_CALL1 # percentage
        except:
            logger.info("Failed to get risk free return")
            raise

    def get_E_Ri_wo_wknds(self):
        '''
            Daily excess stock return (weekends removed)
        '''
        try:
            RF_CALL1 = self.get_Rf_wo_wknds()
            RET_D_KSE = self.get_Ri_wo_wknds()
            # duplicate RF_CALL1 to match the number of columns in RET_D_KSE
            RF_CALL1_df = RF_CALL1.assign(**{str(i):RF_CALL1['RF_CALL1'] for i in range(len(self.symbols_lst)-1)})
            RF_CALL1_df.columns = self.symbols_lst
            RET_D_KSE = RET_D_KSE[RET_D_KSE.index >= self.reg_mo_lst.min()-relativedelta(years=1)]
            self.E_Ri = RET_D_KSE.subtract(RF_CALL1_df)
            logger.info("Succeed in getting excess stock return")
            return self.E_Ri
        except:
            logger.info("Failed to get excess stock return")
            raise

    def get_E_Rm_wo_wknds(self):
        '''
            Daily excess market return (weekends removed)
        '''
        try:
            RF_CALL1 = self.get_Rf_wo_wknds()
            RET_MKT_D_KSE = self.get_Rm_wo_wknds()
            RET_MKT_D_KSE = RET_MKT_D_KSE[RET_MKT_D_KSE.index >= self.reg_mo_lst.min()-relativedelta(years=1)]
            self.E_Rm = RET_MKT_D_KSE.Rm - RF_CALL1.RF_CALL1
            self.E_Rm.index = pd.to_datetime(self.E_Rm.index)
            logger.info("Succeed in getting excess market return")
            return self.E_Rm
        except:
            logger.info("Failed to get excess market return")
            raise
