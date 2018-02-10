#!/usr/bin/env python
'''
'''
import logging
from logging import config
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class MiscDataPrep(object):
    '''
    Miscellaneous data such as stock-level dispersion, market cap, etc.
    '''

    def __init__(self):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit

    def get_m_stock_level_disp(self, reg_mo_lst):
        '''
            Daily stock-level disagreement
        '''
        try:
            m_stock_level_disp = pd.read_csv(self.home_path + self.file_path['EPS_LTG_stdev'],index_col=0)
            m_stock_level_disp.index = pd.Series(m_stock_level_disp.index).apply(lambda mo: datetime.strptime(str(mo), '%Y%m'))
            self.m_stock_level_disp = m_stock_level_disp[m_stock_level_disp.index < reg_mo_lst.iloc[-1]+relativedelta(months=1)]
            logger.info("Succeed in getting monthly stock-level dispersion")
            return self.m_stock_level_disp
        except:
            logger.error('Failed to get monthly stock-level dispersion')
            raise

    def get_monthly_mkt_cap(self, reg_mo_lst):
        '''
            Monthly mkt cap
        '''
        try:
            mkt_cap = pd.read_csv(self.home_path + self.file_path['market_cap'],index_col=0)
            mkt_cap.index = pd.to_datetime(mkt_cap.index)
            mkt_cap = mkt_cap[(mkt_cap.index >= reg_mo_lst[0]) & (mkt_cap.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

            # mkt cap at last day of the months
            self.m_mkt_cap = mkt_cap.groupby([lambda x: x.year,lambda x: x.month]).last()
            self.m_mkt_cap.index = reg_mo_lst.apply(lambda x : x + relativedelta(months=1) - timedelta(days=1))
            if self.to_csv == True:
                self.m_mkt_cap.to_csv('m_mkt_cap.csv')
            logger.info("Succeed in getting monthly market capitalization")
            return self.m_mkt_cap
        except:
            logger.error('Failed to get monthly market capitalization')
            raise

    def get_monthly_vol(self, reg_mo_lst):
        '''
            Monthly volatility
        '''
        try:
            vol = pd.read_csv(self.home_path + self.file_path['volatility'],index_col=0)
            vol.index = pd.to_datetime(vol.index, dayfirst=True)
            vol = vol[(vol.index >= reg_mo_lst[0]) & (vol.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

            # vol at last day of the months
            self.m_vol = vol.groupby([lambda x: x.year,lambda x: x.month]).last()
            self.m_vol.index = reg_mo_lst.apply(lambda x : x + relativedelta(months=1) - timedelta(days=1))
            if self.to_csv == True:
                self.m_vol.to_csv('m_vol_wo_wknds.csv')
            logger.info("Succeed in monthly stock return volatility")
            return self.m_vol
        except:
            logger.error('Failed to get monthly stock return volatility')
            raise

    def get_smb_hml_umd(self, reg_mo_lst):
        '''
            Daily SMB, HML, UMD portfolio returns (without weekends)
        '''
        try:
            SMB_HML_wo_wknds = pd.read_csv(self.home_path + self.file_path['SMB_HML'] , index_col=0) # percent_unit
            SMB_HML_wo_wknds.index = pd.to_datetime(SMB_HML_wo_wknds.index)
            SMB_wo_wknds = SMB_HML_wo_wknds['SMB']
            HML_wo_wknds = SMB_HML_wo_wknds['HML']
            SMB_wo_wknds = SMB_wo_wknds[(SMB_wo_wknds.index >= reg_mo_lst[0]) & (SMB_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
            HML_wo_wknds = HML_wo_wknds[(HML_wo_wknds.index >= reg_mo_lst[0]) & (HML_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

            SMB_MOM_wo_wknds = pd.read_csv(self.home_path + self.file_path['SMB_MOM'], index_col=0) # percent_unit
            SMB_MOM_wo_wknds.index = pd.to_datetime(SMB_MOM_wo_wknds.index)
            UMD_wo_wknds = SMB_MOM_wo_wknds['UMD']
            UMD_wo_wknds = UMD_wo_wknds[(UMD_wo_wknds.index >= reg_mo_lst[0]) & (UMD_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
            self.SMB_HML_UMD_df_wo_wknds = pd.DataFrame([SMB_wo_wknds, HML_wo_wknds, UMD_wo_wknds]).transpose()
            if self.decimal_unit == True:
                self.SMB_HML_UMD_df_wo_wknds = self.SMB_HML_UMD_df_wo_wknds/100 # percentage to decimal
            if self.to_csv == True:
                self.SMB_HML_UMD_df_wo_wknds.to_csv('SMB_HML_UMD_df_wo_wknds.csv')
            logger.info("Succeed in getting daily SMB, HML, UMD portfolio returns")
            return self.SMB_HML_UMD_df_wo_wknds
        except:
            logger.error('Failed to get daily SMB, HML, UMD portfolio returns')
            raise

    def get_D_P(self, reg_mo_lst):
        '''
            Monthly Dividend/Price_ratio
        '''
        try:
            monthly_DP_KOSPI = pd.read_csv(self.home_path + self.file_path['dividend_price_yield'],index_col=0)
            monthly_DP_KOSPI = monthly_DP_KOSPI['KOSPI']
            monthly_DP_KOSPI.index = pd.to_datetime(monthly_DP_KOSPI.index)
            monthly_DP_KOSPI = monthly_DP_KOSPI[(monthly_DP_KOSPI.index >= reg_mo_lst[0]) & (monthly_DP_KOSPI.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
            self.monthly_DP_KOSPI = pd.DataFrame(monthly_DP_KOSPI)
            self.monthly_DP_KOSPI.columns = ['DP_ratio']
            if self.decimal_unit == True:
                self.monthly_DP_KOSPI = self.monthly_DP_KOSPI/100 # percentage to decimal
            if self.to_csv == True:
                self.monthly_DP_KOSPI.to_csv('monthly_DP_KOSPI.csv')
            logger.info("Succeed in getting monthly dividend_price_yield")
            return self.monthly_DP_KOSPI
        except:
            logger.error('Failed to get monthly dividend_price_yield')
            raise

    def get_inflation(self, reg_mo_lst):
        '''
            Monthly CPI yearly inflation
        '''
        try:
            monthly_CPI_yearly_inflation = pd.read_csv(self.home_path + self.file_path['inflation'],index_col=0)
            monthly_CPI_yearly_inflation.index = pd.to_datetime(monthly_CPI_yearly_inflation.index)
            self.monthly_CPI_yearly_inflation = monthly_CPI_yearly_inflation[(monthly_CPI_yearly_inflation.index >= reg_mo_lst[0]) \
                                            & (monthly_CPI_yearly_inflation.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
            if self.decimal_unit == True:
                self.monthly_CPI_yearly_inflation = self.monthly_CPI_yearly_inflation/100 # percentage to decimal
            if self.to_csv == True:
                self.monthly_CPI_yearly_inflation.to_csv('monthly_CPI_yearly_inflation.csv')
            logger.info("Succeed in getting monthly CPI yearly inflation")
            return pd.DataFrame(monthly_CPI_yearly_inflation)
        except:
            logger.error('Failed to get monthly CPI yearly inflation')
            raise

    def get_CP_CD_spread(self, reg_mo_lst):
        '''
            Monthly CP - CD spread
        '''
        try:
            CP_CD_spread = pd.read_csv(self.home_path + self.file_path['CP_CD_spread'],index_col=0)
            CP_CD_spread = CP_CD_spread['CP91'] - CP_CD_spread['CD91']
            CP_CD_spread.index = pd.to_datetime(CP_CD_spread.index, dayfirst=True)
            CP_CD_spread = CP_CD_spread[(CP_CD_spread.index >= reg_mo_lst[0]) & (CP_CD_spread.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

            # last day of the month
            m_CP_CD_spread = CP_CD_spread.groupby([lambda x: x.year,lambda x: x.month]).last()
            m_CP_CD_spread.index = reg_mo_lst.apply(lambda x : x + relativedelta(months=1) - timedelta(days=1))
            self.m_CP_CD_spread = pd.DataFrame(m_CP_CD_spread)
            self.m_CP_CD_spread.columns = ['m_CP_CD_spread']
            if self.decimal_unit == True:
                self.m_CP_CD_spread = self.m_CP_CD_spread/100 # percentage to decimal
            if self.to_csv == True:
                self.m_CP_CD_spread.to_csv('m_CP_CD_spread.csv')
            logger.info("Succeed in getting monthly CP CD spread")
            return self.m_CP_CD_spread
        except:
            logger.error('Failed to get monthly CP CD spread')
            raise
