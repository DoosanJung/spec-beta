#!/usr/bin/env python
'''
'''
import os

class SpecBetaConfig(object):
    '''
    SpecBeta config file
    '''
    HOME_PATH = os.path.expanduser('~/projects/spec_beta')
    to_csv = False
    decimal_unit = True
    FILE_PATH = {
    "symbols":"/spec_beta/data/symbol.csv",
    "daily_stock_return":'/spec_beta/data/RET_D_KSE_wo_wknds.csv',
    "daily_market_return":"/spec_beta/data/RET_MKT_D_KSE_wo_wknds.csv",
    "risk_free_return":"/spec_beta/data/RF_CALL1_wo_wknds.csv",
    "EPS_LTG_stdev":"/spec_beta/data/EPS_STDEV_df.csv",
    "market_cap":"/spec_beta/data/MKT_CAP_KSE.csv",
    "volatility":"/spec_beta/data/VOL_D_5D_KSE.csv",
    "SMB_HML":"/spec_beta/data/SMB_HML_wo_wknds.csv",
    "SMB_MOM":"/spec_beta/data/SMB_MOM_wo_wknds.csv",
    "dividend_price_yield":"/spec_beta/data/monthly_DP_KOSPI_200401_201709.csv",
    #"inflation":"/spec_beta/data/monthly_CPI_yearly_inflation.csv",
    "CP_CD_spread":"/spec_beta/data/CP_CD_SPREAD_wo_wknds.csv",
    "year_and_month":"/spec_beta/data/yrmo.csv"
    }
