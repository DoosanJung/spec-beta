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


class MiscDataPrep(object):
    '''
    Miscellaneous data such as stock-level dispersion, market cap, etc.
    '''
    def __init__(self):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit

    #######################################################################
    #TODO: below

    def get_m_stock_level_disp(self, reg_mo_lst):
        '''
        INPUT: regression months
        OUTPUT: Daily stock-level disagreement
        '''
        m_stock_level_disp = pd.read_csv(self.home_path + file_path['EPS_LTG_stdev'],index_col=0)
        # m_stock_level_disp = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/EPS_stdev_df_cv_lastone.csv',index_col=0)
        m_stock_level_disp.index = pd.Series(m_stock_level_disp.index).apply(lambda mo: datetime.strptime(str(mo), '%Y%m'))
        m_stock_level_disp = m_stock_level_disp[m_stock_level_disp.index < reg_mo_lst.iloc[-1]+relativedelta(months=1)]
        return m_stock_level_disp

    def get_monthly_mkt_cap(self, reg_mo_lst, to_csv):
        '''
        INPUT: regression months
        OUTPUT: monthly mkt cap
        '''
        mkt_cap = pd.read_csv(self.home_path + file_path['market_cap'],index_col=0)
        # mkt_cap.index = pd.Series(mkt_cap.index).apply(lambda mo: datetime.strptime(mo,'%Y-%m-%d %H:%M:%S'))
        mkt_cap.index = pd.to_datetime(mkt_cap.index)
        mkt_cap = mkt_cap[(mkt_cap.index >= reg_mo_lst[0]) & (mkt_cap.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

        # mkt cap at last day of the months
        m_mkt_cap = mkt_cap.groupby([lambda x: x.year,lambda x: x.month]).last()
        m_mkt_cap.index = reg_mo_lst.apply(lambda x : x + relativedelta(months=1) - timedelta(days=1))
        # if to_csv == True:
        #     m_mkt_cap.to_csv('m_mkt_cap.csv')
        # else:
        #     pass
        return m_mkt_cap

    def get_monthly_vol(self, reg_mo_lst, to_csv):
        '''
        INPUT: regression months
        OUTPUT: monthly vol
        '''
        vol = pd.read_csv(self.home_path + file_path['volatility'],index_col=0)
        vol.index = pd.to_datetime(vol.index, dayfirst=True)
        vol = vol[(vol.index >= reg_mo_lst[0]) & (vol.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

        # vol at last day of the months
        m_vol = vol.groupby([lambda x: x.year,lambda x: x.month]).last()
        m_vol.index = reg_mo_lst.apply(lambda x : x + relativedelta(months=1) - timedelta(days=1))
        # if to_csv == True:
        #     m_vol.to_csv('m_vol_wo_wknds.csv')
        # else:
        #     pass
        return m_vol

    def get_smb_hml_umd(self, reg_mo_lst, to_csv, decimal_unit):
        '''
        INPUT: regression months
        OUTPUT: monthly SMB, HML, UMD
        '''
        SMB_HML_wo_wknds = pd.read_csv(self.home_path + file_path['SMB_HML'] , index_col=0) # percent_unit
        SMB_HML_wo_wknds.index = pd.to_datetime(SMB_HML_wo_wknds.index)
        SMB_wo_wknds = SMB_HML_wo_wknds['SMB']
        HML_wo_wknds = SMB_HML_wo_wknds['HML']
        SMB_wo_wknds = SMB_wo_wknds[(SMB_wo_wknds.index >= reg_mo_lst[0]) & (SMB_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
        HML_wo_wknds = HML_wo_wknds[(HML_wo_wknds.index >= reg_mo_lst[0]) & (HML_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

        SMB_MOM_wo_wknds = pd.read_csv(self.home_path + file_path['SMB_MOM'], index_col=0) # percent_unit
        SMB_MOM_wo_wknds.index = pd.to_datetime(SMB_MOM_wo_wknds.index)
        UMD_wo_wknds = SMB_MOM_wo_wknds['UMD']
        UMD_wo_wknds = UMD_wo_wknds[(UMD_wo_wknds.index >= reg_mo_lst[0]) & (UMD_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
        SMB_HML_UMD_df_wo_wknds = pd.DataFrame([SMB_wo_wknds, HML_wo_wknds, UMD_wo_wknds]).transpose()
        if decimal_unit == True:
            SMB_HML_UMD_df_wo_wknds = SMB_HML_UMD_df_wo_wknds/100 # percentage to decimal
        if to_csv == True:
            SMB_HML_UMD_df_wo_wknds.to_csv('SMB_HML_UMD_df_wo_wknds.csv')
        return SMB_HML_UMD_df_wo_wknds

    def get_D_P(self, reg_mo_lst, to_csv, decimal_unit):
        '''
        INPUT: regression months
        OUTPUT: monthly Dividend/Price_ratio
        '''
        monthly_DP_KOSPI = pd.read_csv(self.home_path + file_path['dividend_price_yield'],index_col=0)
        monthly_DP_KOSPI = monthly_DP_KOSPI['KOSPI']
        monthly_DP_KOSPI.index = pd.to_datetime(monthly_DP_KOSPI.index)
        monthly_DP_KOSPI = monthly_DP_KOSPI[(monthly_DP_KOSPI.index >= reg_mo_lst[0]) & (monthly_DP_KOSPI.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
        monthly_DP_KOSPI = pd.DataFrame(monthly_DP_KOSPI)
        monthly_DP_KOSPI.columns = ['DP_ratio']
        if decimal_unit == True:
            monthly_DP_KOSPI = monthly_DP_KOSPI/100 # percentage to decimal
        if to_csv == True:
            monthly_DP_KOSPI.to_csv('monthly_DP_KOSPI.csv')
        return monthly_DP_KOSPI

    def get_inflation(self, reg_mo_lst, to_csv, decimal_unit):
        '''
        INPUT: regression months
        OUTPUT:
        '''
        monthly_CPI_yearly_inflation = pd.read_csv(self.home_path + file_path['inflation'],index_col=0)
        monthly_CPI_yearly_inflation.index = pd.to_datetime(monthly_CPI_yearly_inflation.index)
        monthly_CPI_yearly_inflation = monthly_CPI_yearly_inflation[(monthly_CPI_yearly_inflation.index >= reg_mo_lst[0]) \
                                        & (monthly_CPI_yearly_inflation.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
        if decimal_unit == True:
            monthly_CPI_yearly_inflation = monthly_CPI_yearly_inflation/100 # percentage to decimal
        if to_csv == True:
            monthly_CPI_yearly_inflation.to_csv(self.home_path + '/spec_beta/data/monthly_CPI_yearly_inflation.csv')
        return pd.DataFrame(monthly_CPI_yearly_inflation)

    def get_CP_CD_spread(self, reg_mo_lst, to_csv, decimal_unit):
        '''
        INPUT: regression months
        OUTPUT:
        '''
        CP_CD_spread = pd.read_csv(self.home_path + file_path['CP_CD_spread'],index_col=0)
        CP_CD_spread = CP_CD_spread['CP91'] - CP_CD_spread['CD91']
        CP_CD_spread.index = pd.to_datetime(CP_CD_spread.index, dayfirst=True)
        CP_CD_spread = CP_CD_spread[(CP_CD_spread.index >= reg_mo_lst[0]) & (CP_CD_spread.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

        # MAKE IT MONTHLY
        # last day of the month
        m_CP_CD_spread = CP_CD_spread.groupby([lambda x: x.year,lambda x: x.month]).last()
        m_CP_CD_spread.index = reg_mo_lst.apply(lambda x : x + relativedelta(months=1) - timedelta(days=1))
        m_CP_CD_spread = pd.DataFrame(m_CP_CD_spread)
        m_CP_CD_spread.columns = ['m_CP_CD_spread']
        if decimal_unit == True:
            m_CP_CD_spread = m_CP_CD_spread/100 # percentage to decimal
        if to_csv == True:
            m_CP_CD_spread.to_csv('m_CP_CD_spread.csv')
        return m_CP_CD_spread
