#!/usr/bin/env python
'''
'''
import pandas as pd
import logging
from logging import config
from dateutil.relativedelta import relativedelta
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class ReturnDataPrep(object):
    '''
    Return data such as excess stock return, excess market return
    '''
    def __init__(self):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit

    def get_symbols_lst(self):
        '''
            Stock symbols
        '''
        try:
            symbols = pd.read_csv(self.home_path + self.file_path['symbols'])
            symbols_lst = symbols.columns.tolist()
            logger.info("Success to get the symbol list")
        except:
            logger.error('Failed to get the symbol list')
            raise
        return symbols_lst

    #######################################################################    
    #TODO: below

    def get_Ri_wo_wknds(self, decimal_unit):
        '''
        OUTPUT: Daily stock return (weekends removed)
        '''
        try:
            RET_D_KSE = pd.read_csv(self.home_path + self.file_path['daily_stock_return'],index_col=0)
            RET_D_KSE.index = pd.to_datetime(RET_D_KSE.index, dayfirst=True)
            if decimal_unit==True:
                RET_D_KSE = RET_D_KSE/100 # percentage to decimal
                return RET_D_KSE
            else:
                return RET_D_KSE # percentage
        except:
            logger.error('Failed to get stock return')
            raise

    def get_Rm_wo_wknds(self, decimal_unit):
        '''
        OUTPUT: Daily market return (weekends removed)
        '''
        RET_MKT_D_KSE = pd.read_csv(self.home_path + file_path['daily_market_return'],\
                                    index_col=0, header=None, names=['Rm'])
        RET_MKT_D_KSE.index = pd.to_datetime(RET_MKT_D_KSE.index, dayfirst=True)
        if decimal_unit==True:
            RET_MKT_D_KSE = RET_MKT_D_KSE/100 # percentage to decimal
            return RET_MKT_D_KSE
        else:
            return RET_MKT_D_KSE # percentage

    def get_Rf_wo_wknds(self, decimal_unit, reg_mo_lst):
        '''
        OUTPUT: Daily risk-free return (weekends removed)
        '''
        RF_CALL1 = pd.read_csv(self.home_path + file_path['risk_free_return'],\
                                index_col=0, header=None, names=['RF_CALL1'])
        RF_CALL1.index = pd.to_datetime(RF_CALL1.index)
        RF_CALL1 = RF_CALL1[RF_CALL1.index >= reg_mo_lst.min()-relativedelta(years=1)]
        if decimal_unit==True:
            RF_CALL1 = RF_CALL1/100 # percentage to decimal
            return RF_CALL1
        else:
            return RF_CALL1 # percentage

    def get_E_Ri_wo_wknds(self, RET_D_KSE, RF_CALL1, symbols_lst, reg_mo_lst):
        '''
        OUTPUT: Daily excess stock return (weekends removed)
        '''
        # R_f to R_f DataFrame
        RF_CALL1_df = RF_CALL1.assign(**{str(i):RF_CALL1['RF_CALL1'] for i in range(len(symbols_lst)-1)})
        RF_CALL1_df.columns = symbols_lst
        RET_D_KSE = RET_D_KSE[RET_D_KSE.index >= reg_mo_lst.min()-relativedelta(years=1)]
        E_Ri = RET_D_KSE.subtract(RF_CALL1_df)
        return E_Ri

    def get_E_Rm_wo_wknds(self, RET_MKT_D_KSE, RF_CALL1, reg_mo_lst):
        '''
        OUTPUT: Daily excess market return (weekends removed)
        '''
        RET_MKT_D_KSE = RET_MKT_D_KSE[RET_MKT_D_KSE.index >= reg_mo_lst.min()-relativedelta(years=1)]
        E_Rm = RET_MKT_D_KSE.Rm - RF_CALL1.RF_CALL1
        E_Rm.index = pd.to_datetime(E_Rm.index)
        return E_Rm
