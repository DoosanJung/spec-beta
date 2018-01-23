'''
THIS MODULE IS FOR
- Pre_ranking_pfo
- Pre_ranking_pfo_aggdisp
- Figure5
- get_Table1
'''

'''
Revised
- RET_D_KSE_wo_wknds
- RET_MKT_D_KSE_wo_wknds
- RF_CALL1_wo_wknds


Added
- SMB_HML_wo_wknds
- SMB_MOM_wo_wknds
- VOL_D_5D_KSE
- CP_CD_SPREAD_wo_wknds
- monthly_CPI_yearly_inflation
- monthly_DP_KOSPI_200401_201709
'''



import pandas as pd
import numpy as np
from datetime import date, timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
from tqdm import tqdm
import matplotlib.pyplot as plt
import os

def get_symbols_lst():
    symbols = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/symbol.csv')
    symbols_lst = symbols.columns.tolist()
    return symbols_lst

def get_Ri_wo_wknds(decimal_unit):
    '''
    OUTPUT: Daily stock return
    idx == 'datetime64[ns]' 2000-01-03 ~ 2017-11-15
    shape == (4663, 751)
    '''
    RET_D_KSE = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/RET_D_KSE_wo_wknds.csv',index_col=0)
    RET_D_KSE.index = pd.to_datetime(RET_D_KSE.index, dayfirst=True)
    if decimal_unit==True:
        RET_D_KSE = RET_D_KSE/100 # percentage to decimal
        return RET_D_KSE
    else:
        return RET_D_KSE # percentage

def get_Rm_wo_wknds(decimal_unit):
    '''
    OUTPUT: Daily market return
    idx == 'datetime64[ns]' 2001-01-01 ~ 2017-11-15
    shape == (4403, 1)
    '''
    RET_MKT_D_KSE = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/RET_MKT_D_KSE_wo_wknds.csv',\
                                index_col=0, header=None, names=['Rm'])
    RET_MKT_D_KSE.index = pd.to_datetime(RET_MKT_D_KSE.index, dayfirst=True)
    if decimal_unit==True:
        RET_MKT_D_KSE = RET_MKT_D_KSE/100 # percentage to decimal
        return RET_MKT_D_KSE
    else:
        return RET_MKT_D_KSE # percentage

def get_Rf_wo_wknds(decimal_unit, reg_mo_lst):
    '''
    OUTPUT: Daily risk-free return
    idx == 'datetime64[ns]' 2000-01-03 ~ 2017-11-15
    shape == (2315, 1)
    '''
    RF_CALL1 = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/RF_CALL1_wo_wknds.csv',index_col=0, header=None, names=['RF_CALL1'])
    RF_CALL1.index = pd.to_datetime(RF_CALL1.index)
    RF_CALL1 = RF_CALL1[RF_CALL1.index >= reg_mo_lst.min()-relativedelta(years=1)]
    if decimal_unit==True:
        RF_CALL1 = RF_CALL1/100 # percentage to decimal
        return RF_CALL1
    else:
        return RF_CALL1 # percentage

def get_E_Ri_wo_wknds(RET_D_KSE, RF_CALL1, symbols_lst, reg_mo_lst):
    '''
    OUTPUT: Daily excess stock return
    idx == 'datetime64[ns]'  2001-01-01 ~ 2017-11-15
    shape == (2315, 751)
    '''
    # R_f to R_f DataFrame
    RF_CALL1_df = RF_CALL1.assign(**{str(i):RF_CALL1['RF_CALL1'] for i in range(len(symbols_lst)-1)})
    RF_CALL1_df.columns = symbols_lst
    RET_D_KSE = RET_D_KSE[RET_D_KSE.index >= reg_mo_lst.min()-relativedelta(years=1)]
    # Somthing is wrong...
    # E_Ri = RET_D_KSE.subtract(RF_CALL1_df)

    # Instead
    E_Ri = RET_D_KSE
    return E_Ri

def get_E_Rm_wo_wknds(RET_MKT_D_KSE, RF_CALL1, reg_mo_lst):
    '''
    OUTPUT: Daily excess market return
    idx == 'datetime64[ns]'
    shape == (2315, 751)
    '''
    RET_MKT_D_KSE = RET_MKT_D_KSE[RET_MKT_D_KSE.index >= reg_mo_lst.min()-relativedelta(years=1)]
    E_Rm = RET_MKT_D_KSE.Rm - RF_CALL1.RF_CALL1
    E_Rm.index = pd.to_datetime(E_Rm.index)
    return E_Rm

def get_return_data_wo_wknds(decimal_unit, symbols_lst, reg_mo_lst, freq):
    '''
    OUTPUT: Excess returns, returns
    idx == 'datetime64[ns]'
    '''
    if freq == 'd':
        RET_D_KSE = get_Ri_wo_wknds(decimal_unit)
        RET_MKT_D_KSE = get_Rm_wo_wknds(decimal_unit)
        RF_CALL1 = get_Rf_wo_wknds(decimal_unit, reg_mo_lst)
        E_Ri = get_E_Ri_wo_wknds(RET_D_KSE, RF_CALL1, symbols_lst, reg_mo_lst)
        E_Rm = get_E_Rm_wo_wknds(RET_MKT_D_KSE, RF_CALL1, reg_mo_lst)
        return RET_D_KSE, RET_MKT_D_KSE, RF_CALL1, E_Ri, E_Rm
    elif freq == 'm':
        pass
    elif freq == 'q':
        pass
    elif freq == 'y':
        pass

def get_reg_mo_lst(start_mo, end_mo):
    '''
    OUTPUT: Monthly regression months
    dtype == datetime64[ns]
    '''
    mo_lst = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/yrmo.csv',header=None, names='m')
    mo_lst = mo_lst.m.apply(lambda mo: datetime.strptime(str(mo), "%Y%m"))
    reg_mo_lst = mo_lst[(mo_lst >= datetime.strptime(str(start_mo), "%Y%m"))&(mo_lst <= datetime.strptime(str(end_mo), "%Y%m"))]
    reg_mo_lst = reg_mo_lst.reset_index(drop=True)
    # reg_mo_lst = reg_mo_lst[:81]
    reg_mo_lst = reg_mo_lst[reg_mo_lst <= datetime.strptime(str(end_mo), "%Y%m") - relativedelta(years=1)]
    return reg_mo_lst

# Each month...
def get_regressor(E_Rm,mo):
    '''
    INPUT: month (t) , convert decimal >> percent
    OUTPUT: Daily Dimson(1979) regressor:  Rm(t) + 5 lags of Rm(t)
    idx == 'datetime64[ns]' 2009-01-01 ~ ... ~ 2016-08-31
    '''
    # Init regressor_Rm
    regressor_Rm = pd.DataFrame()
    # no lag (previous 12 months)
    E_Rm_t = E_Rm[(E_Rm.index < mo)& (E_Rm.index >= mo-relativedelta(years=1))]
    # Save the idx
    regressor_idx = E_Rm_t.index
    # Drop the idx
    E_Rm_t = E_Rm_t.reset_index(drop=True)
    # concat no lag
    regressor_Rm = pd.concat([regressor_Rm, E_Rm_t],axis=1, ignore_index=True)
    # concat from lag 1 to lag 5
    for i in xrange(1,6):
        E_Rm_t_lag = E_Rm[(E_Rm.index < mo+timedelta(days=i+5))&(E_Rm.index >= mo-relativedelta(years=1)+timedelta(days=i))]
        # Drop the idx for lag 1 to lag 5
        # E_Rm_t_lag = E_Rm_t_lag.shift(periods=-i)
        E_Rm_t_lag = E_Rm_t_lag[:len(E_Rm_t)]
        E_Rm_t_lag = E_Rm_t_lag.reset_index(drop=True)
        regressor_Rm = pd.concat([regressor_Rm, E_Rm_t_lag],ignore_index=True, axis=1)
    regressor_Rm['mo'] = regressor_idx
    regressor_Rm.set_index('mo',inplace=True)
    regressor_Rm = regressor_Rm*100
    regressor_Rm = sm.add_constant(regressor_Rm)
    return regressor_Rm

# Full sample period
def get_regressor_full_sample(E_Rm, R_pfo_df, decimal_unit):
    '''
    INPUT: Full sample period ( R_pfo_df.index )
    OUTPUT: Daily Dimson(1979) regressor:  Rm(t) + 5 lags of Rm(t)
    idx == 'datetime64[ns]'
    '''
    # Init regressor_Rm
    regressor_Rm = pd.DataFrame()
    # Save the idx
    E_Rm_t = E_Rm[    (E_Rm.index >= R_pfo_df.index.min())   & (E_Rm.index <= R_pfo_df.index.max())   ] # 2010-01-01 ~ 2016-09-30
    regressor_idx = E_Rm_t.index
    # Drop the idx
    E_Rm_t = E_Rm_t.reset_index(drop=True)
    # concat no lag
    regressor_Rm = pd.concat([regressor_Rm, E_Rm_t],axis=1, ignore_index=True)
    # concat from lag 1 to lag 5
    for i in xrange(1,6):
        E_Rm_t_lag = E_Rm[    (E_Rm.index >= datetime.strptime(R_pfo_df.index.min(),'%Y-%m-%d') + timedelta(days=i)) \
                            &  (E_Rm.index <= datetime.strptime(R_pfo_df.index.max(),'%Y-%m-%d') + timedelta(days=i+5))   ]
        # Drop the idx for lag 1 to lag 5
        # E_Rm_t_lag = E_Rm_t_lag.shift(periods=-i)
        E_Rm_t_lag = E_Rm_t_lag[:len(E_Rm_t)]
        E_Rm_t_lag = E_Rm_t_lag.reset_index(drop=True)
        regressor_Rm = pd.concat([regressor_Rm, E_Rm_t_lag],ignore_index=True, axis=1)
    regressor_Rm['mo'] = regressor_idx
    regressor_Rm.set_index('mo',inplace=True)
    regressor_Rm = regressor_Rm*100
    regressor_Rm = sm.add_constant(regressor_Rm)
    return regressor_Rm



def run_ols(y, x, pfunc):
    model = sm.OLS(y,x).fit()
    summary = model.summary()
    if pfunc == True:
        print summary
    else:
        pass
    return model

def get_m_stock_level_disp(reg_mo_lst):
    '''
    INPUT: regression months
    OUTPUT: Daily stock-level disagreement
    idx == 'datetime64[ns]' 2010-01-01 ~ 2016-09-01
    shape == (81, 751)
    '''
    m_stock_level_disp = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/EPS_stdev_df.csv',index_col=0)
    # m_stock_level_disp = pd.read_csv('/Users/streamlyzer/DSJ/sb/data/EPS_stdev_df_cv_lastone.csv',index_col=0)
    m_stock_level_disp.index = pd.Series(m_stock_level_disp.index).apply(lambda mo: datetime.strptime(str(mo), '%Y%m'))
    m_stock_level_disp = m_stock_level_disp[m_stock_level_disp.index < reg_mo_lst.iloc[-1]+relativedelta(months=1)]
    return m_stock_level_disp

def get_monthly_mkt_cap(reg_mo_lst, to_csv):
    '''
    INPUT: regression months
    OUTPUT: monthly mkt cap
    idx == 'datetime64[ns]' 2010-01-31 ~ 2016-09-30
    shape == (81, 751)
    '''
    mkt_cap = pd.read_csv('MKT_CAP_KSE.csv',index_col=0)
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

def get_monthly_vol(reg_mo_lst, to_csv):
    '''
    INPUT: regression months
    OUTPUT: monthly vol
    idx == 'datetime64[ns]' 2010-01-31 ~ 2016-09-30
    shape == (81, 751)
    '''
    vol = pd.read_csv('VOL_D_5D_KSE.csv',index_col=0)
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

def get_smb_hml_umd(reg_mo_lst, to_csv, decimal_unit):
    '''
    INPUT: regression months
    OUTPUT: monthly SMB, HML, UMD
    idx == 'datetime64[ns]' 2010-01-31 ~ 2016-09-30
    shape == (2315, 3)
    '''
    SMB_HML_wo_wknds = pd.read_csv('SMB_HML_wo_wknds.csv', index_col=0) # percent_unit
    SMB_HML_wo_wknds.index = pd.to_datetime(SMB_HML_wo_wknds.index)
    SMB_wo_wknds = SMB_HML_wo_wknds['SMB']
    HML_wo_wknds = SMB_HML_wo_wknds['HML']
    SMB_wo_wknds = SMB_wo_wknds[(SMB_wo_wknds.index >= reg_mo_lst[0]) & (SMB_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
    HML_wo_wknds = HML_wo_wknds[(HML_wo_wknds.index >= reg_mo_lst[0]) & (HML_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]

    SMB_MOM_wo_wknds = pd.read_csv('SMB_MOM_wo_wknds.csv', index_col=0) # percent_unit
    SMB_MOM_wo_wknds.index = pd.to_datetime(SMB_MOM_wo_wknds.index)
    UMD_wo_wknds = SMB_MOM_wo_wknds['UMD']
    UMD_wo_wknds = UMD_wo_wknds[(UMD_wo_wknds.index >= reg_mo_lst[0]) & (UMD_wo_wknds.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
    SMB_HML_UMD_df_wo_wknds = pd.DataFrame([SMB_wo_wknds, HML_wo_wknds, UMD_wo_wknds]).transpose()
    if decimal_unit == True:
        SMB_HML_UMD_df_wo_wknds = SMB_HML_UMD_df_wo_wknds/100 # percentage to decimal
    if to_csv == True:
        SMB_HML_UMD_df_wo_wknds.to_csv('SMB_HML_UMD_df_wo_wknds.csv')
    return SMB_HML_UMD_df_wo_wknds

def get_D_P(reg_mo_lst, to_csv, decimal_unit):
    '''
    INPUT: regression months
    OUTPUT: monthly Dividend/Price_ratio
    idx == 'datetime64[ns]' 2010-01-31 ~ 2016-09-30
    shape == (2315, 3)
    '''
    monthly_DP_KOSPI = pd.read_csv('monthly_DP_KOSPI_200401_201709.csv',index_col=0)
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

def get_inflation(reg_mo_lst, to_csv, decimal_unit):
    '''
    INPUT: regression months
    OUTPUT:
    idx == 'datetime64[ns]' 2010-01-31 ~ 2016-09-30
    shape ==
    '''
    monthly_CPI_yearly_inflation = pd.read_csv('monthly_CPI_yearly_inflation.csv',index_col=0)
    monthly_CPI_yearly_inflation.index = pd.to_datetime(monthly_CPI_yearly_inflation.index)
    monthly_CPI_yearly_inflation = monthly_CPI_yearly_inflation[(monthly_CPI_yearly_inflation.index >= reg_mo_lst[0]) \
                                    & (monthly_CPI_yearly_inflation.index < reg_mo_lst.iloc[-1]+relativedelta(months=1))]
    if decimal_unit == True:
        monthly_CPI_yearly_inflation = monthly_CPI_yearly_inflation/100 # percentage to decimal
    if to_csv == True:
        monthly_CPI_yearly_inflation.to_csv('monthly_CPI_yearly_inflation.csv')
    return pd.DataFrame(monthly_CPI_yearly_inflation)

def get_CP_CD_spread(reg_mo_lst, to_csv, decimal_unit):
    '''
    INPUT: regression months
    OUTPUT:
    idx == 'datetime64[ns]' 2010-01-31 ~ 2016-09-30
    shape ==
    '''
    CP_CD_spread = pd.read_csv('CP_CD_SPREAD_wo_wknds.csv',index_col=0)
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

def rearrange_d_ret_df(d_ret_df):
    renamed_pfo_lst = [u'pfo_00', u'pfo_01', u'pfo_10', u'pfo_11', u'pfo_12', u'pfo_13',
       u'pfo_14', u'pfo_15', u'pfo_16', u'pfo_17', u'pfo_18', u'pfo_19',
       u'pfo_02', u'pfo_03', u'pfo_04', u'pfo_05', u'pfo_06', u'pfo_07', u'pfo_08', u'pfo_09']
    d_ret_df.columns = renamed_pfo_lst
    d_ret_df = d_ret_df.reindex_axis(sorted(d_ret_df.columns), axis=1)
    return d_ret_df

# Each month...
def pre_ranking_beta(E_Ri, E_Rm, i, mo, symbols_lst, m_mkt_cap, m_vol, m_stock_level_disp, to_csv):
    '''
    INPUT: month (t)
    OUTPUT: monthly # symbol, sum_beta, ret1,3,6,12  pfo_number, mo, mkt_cap, vol, disp.
    idx == 'datetime64[ns]'

    REGRESSION: ALL PERCENTAGE UNIT (regressor_Rm and E_Ri_t)
    RETURN CALCULATION: decimal_unit (E_Ri_ret)
    '''
    # X + const
    regressor_Rm = get_regressor(E_Rm,mo)
    # Percent unit for regression
    # reg_mo_lst[0]: returns 2009-01-01 ~ 2009-12-31
    # reg_mo_lst.iloc[-1]: returns 2015-09-01 ~ 2016-08-31

    # Y
    E_Ri_t = E_Ri[(E_Ri.index < mo )& (E_Ri.index >= mo - relativedelta(years=1))]
    E_Ri_t = E_Ri_t*100
    # Percent unit for regression
    # reg_mo_lst[0]: returns 2009-01-01 ~ 2009-12-31
    # reg_mo_lst.iloc[-1]: 2015-09-01 ~ 2016-08-31

    # To calculate individual return
    E_Ri_ret = E_Ri[(E_Ri.index >= mo )& (E_Ri.index < mo + relativedelta(years=1))]
    # reg_mo_lst[0]: returns 2009-01-01 ~ 2009-12-31
    # reg_mo_lst.iloc[-1]: 2016-09-01 ~ 2017-08-31

    pre_ranking_beta_Frame=[]
    for symbol in symbols_lst:
        try:
            sum_beta_dict={}
            sum_beta_dict['mo'] = mo # mo
            sum_beta_dict['symbol'] = symbol # symbol
            if E_Ri_t.shape[0] == regressor_Rm.shape[0]:
                if all(E_Ri_t[symbol].isnull()):
                    sum_beta = np.nan
                else:
                    OLS_df = pd.concat([regressor_Rm, E_Ri_t[symbol]], axis=1).dropna()
                    model = run_ols( OLS_df[symbol] , OLS_df.drop(symbol, axis=1) , pfunc=False)
                    sum_beta = np.sum(model.params.drop('const'))
                sum_beta_dict['sum_beta'] = sum_beta # sum_beta
                pre_ranking_beta_Frame.append(sum_beta_dict)
            else:
                raise ValueError
        except:
            print "WARNING!!! ",symbol

    pre_ranking_beta_df = pd.DataFrame(pre_ranking_beta_Frame, index=symbols_lst)
    # [symbols] x [mo, sum_beta, symbol]
    # 751 x 3

    # tmp_df = pd.DataFrame()
    # individual vol from monthly table
    pre_ranking_beta_df['m_vol'] = m_vol.transpose().iloc[:,i]   # [symbol] x [months]

    # individual mkt_cap from monthly table
    pre_ranking_beta_df['m_mkt_cap'] = m_mkt_cap.transpose().iloc[:,i] # mo 2010-01-31 ~ 2016-09-30

    # individual Stock-level disagreement from monthly table
    pre_ranking_beta_df['m_stock_level_disp'] =m_stock_level_disp.transpose().iloc[:,i]
    #

    if to_csv==True:
        pre_ranking_beta_df.to_csv('pre_ranking_beta_df_wo_wknds.csv')
    else:
        pass
    return pre_ranking_beta_df, E_Ri_ret

    # pre_ranking_beta_df
    #                mo  sum_beta   symbol    m_vol    m_mkt_cap   m_stock_level_disp
    # A005930 2010-01-01  1.049569  A005930  0.32464  127196228.0               NaN
    # A000660 2010-01-01  1.302807  A000660  0.58167   13414848.0               NaN
    # A005380 2010-01-01  1.245278  A005380  0.43688   27451444.0               NaN
    # A051910 2010-01-01  0.881518  A051910  0.42450   13824863.0               NaN
    # A035420 2010-01-01  0.271555  A035420  0.42987    8326093.0               NaN


# each month...
def assign_beta_pfo(result, mo, E_Ri_ret, to_csv):
    percentile_lst = zip(np.arange(0,1,0.05), np.arange(0.05,1.05,0.05))
    pfo_N_stocks={}
    pfo_median_vol={}
    pfo_stock_disp={}
    pfo_perc_mkt_cap={}
    pfo_avg_of_sumbeta={}
    Total_m_mkt_cap = result.m_mkt_cap.sum() # of this month mo

    d_ret_ew={}
    d_ret_vw={}
    for month in [1,3,6,12]:
        for k, (bottom,top) in enumerate(percentile_lst):
            indicator = 0
            if indicator == 0:
                pfo_k = result[(result['sum_beta'] >= result['sum_beta'].quantile(bottom)) & (result['sum_beta'] <= result['sum_beta'].quantile(top))]

                pfo_N_stocks["pfo_{0}".format(('0'+str(k))[-2:])] = result[(result['sum_beta'] > result['sum_beta'].quantile(bottom)) & (result['sum_beta'] <= result['sum_beta'].quantile(top))].shape[0]
                pfo_median_vol["pfo_{0}".format(('0'+str(k))[-2:])] = pfo_k.m_vol.median()

                # value-weighting schema for AggDisp
                s = pfo_k.sum_beta
                m = pfo_k.m_stock_level_disp
                c = pfo_k.m_mkt_cap
                vw = c/np.sum(c) # weighting schema
                # pfo_stock_disp["pfo_{0}".format(('0'+str(k))[-2:])] =  np.nansum(m.multiply(vw, fill_value=0))
                pfo_stock_disp["pfo_{0}".format(('0'+str(k))[-2:])] =  np.nansum(m.multiply(s, fill_value=0))
                pfo_perc_mkt_cap["pfo_{0}".format(('0'+str(k))[-2:])] = float(pfo_k.m_mkt_cap.sum())/Total_m_mkt_cap
                pfo_avg_of_sumbeta["pfo_{0}".format(('0'+str(k))[-2:])] = \
                                        np.nansum(pfo_k.sum_beta)/pfo_N_stocks["pfo_{0}".format(('0'+str(k))[-2:])] # divide this later
                indicator += 1
            else:
                pass
            # calculate returns
            E_Ri_ret_lag = E_Ri_ret[ (E_Ri_ret.index >= mo) & (E_Ri_ret.index < mo + relativedelta(months=month))]
            # only in pfo_k
            pfo_k_ret = E_Ri_ret_lag[pfo_k.index.tolist()]

            # if ew == True:
            # equal-weighting schema
            ew_df = pfo_k_ret/len(pfo_k_ret.columns)
            d_ret_ew["pfo_{0}".format(k)] = ew_df.sum(axis=1)
            # d_ret.append(d_ew_ret)
            #tmp_df["ret_{0}".format(month)] = E_Ri_ret_lag.add(1).product()-1 # ret 1, 3, 6, 12

            # else:
            mkt_cap = pd.read_csv('MKT_CAP_KSE.csv',index_col=0)
            mkt_cap.index = pd.to_datetime(mkt_cap.index)
            # mkt_cap = mkt_cap[ (mkt_cap.index >= mo) & (mkt_cap.index < mo + relativedelta(months=month))]
            mkt_cap = mkt_cap[mkt_cap.index.isin(E_Ri_ret_lag.index)]
            mkt_cap = mkt_cap[pfo_k.index.tolist()]
#            mkt_cap.sum(axis=1)
            # value-weighting schema
            vw_mkt_cap = mkt_cap.divide(mkt_cap.sum(axis=1),axis=0)
            vw_df = pfo_k_ret.multiply(vw_mkt_cap)
            d_ret_vw["pfo_{0}".format(k)] = vw_df.sum(axis=1)

        d_ret_df_ew = pd.DataFrame(d_ret_ew)
        d_ret_df_ew = rearrange_d_ret_df(d_ret_df_ew)
        d_ret_df_vw = pd.DataFrame(d_ret_vw)
        d_ret_df_vw = rearrange_d_ret_df(d_ret_df_vw)

        if to_csv==True:
            # if ew == True:
            d_ret_df_ew.to_csv('d_ret_df_ew_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds.csv')
            # else:
            d_ret_df_vw.to_csv('d_ret_df_vw_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds.csv')
        else:
            pass

        if month ==1:
            ret1_ew = d_ret_df_ew
            ret1_vw = d_ret_df_vw
            # ret1_ew_mean = ret1_ew.dropna().mean()
            # ret1_vw_mean = ret1_vw.dropna().mean()
            ret1_ew_mean = (ret1_ew+1).drop_duplicates().product()-1
            ret1_vw_mean = (ret1_vw+1).drop_duplicates().product()-1

        elif month==3:
            ret3_ew = d_ret_df_ew
            ret3_vw = d_ret_df_vw
            # ret3_ew_mean = ret3_ew.dropna().mean()
            # ret3_vw_mean = ret3_vw.dropna().mean()
            ret3_ew_mean = (ret3_ew+1).drop_duplicates().product()-1
            ret3_vw_mean = (ret3_vw+1).drop_duplicates().product()-1

        elif month==6:
            ret6_ew = d_ret_df_ew
            ret6_vw = d_ret_df_vw
            # ret6_ew_mean = ret6_ew.dropna().mean()
            # ret6_vw_mean = ret6_vw.dropna().mean()
            ret6_ew_mean = (ret6_ew+1).drop_duplicates().product()-1
            ret6_vw_mean = (ret6_vw+1).drop_duplicates().product()-1

        elif month==12:
            ret12_ew = d_ret_df_ew
            ret12_vw = d_ret_df_vw
            # ret12_ew_mean = ret12_ew.dropna().mean()
            # ret12_vw_mean = ret12_vw.dropna().mean()
            ret12_ew_mean = (ret12_ew+1).drop_duplicates().product()-1
            ret12_vw_mean = (ret12_vw+1).drop_duplicates().product()-1
        else:
            pass


    pfo_idx = ['pfo_N_stocks', 'pfo_median_vol', 'pfo_stock_disp', 'pfo_perc_mkt_cap', 'pfo_avg_of_sumbeta', \
                'ret1_ew', 'ret1_vw', 'ret3_ew', 'ret3_vw','ret6_ew', 'ret6_vw', 'ret12_ew', 'ret12_vw']
    return pd.DataFrame([pfo_N_stocks, pfo_median_vol, pfo_stock_disp, pfo_perc_mkt_cap, pfo_avg_of_sumbeta, \
                ret1_ew_mean, ret1_vw_mean, ret3_ew_mean, ret3_vw_mean, ret6_ew_mean, ret6_vw_mean, \
                ret12_ew_mean, ret12_vw_mean],\
                 index = pfo_idx), pfo_idx


def get_Table1(Table1_df_monthly, pfo_idx):
    Table1={}
    for col in pfo_idx:
        Table1[col]=Table1_df_monthly.transpose()[col].mean(axis=1)
    Table1_df = pd.DataFrame(Table1)
    return Table1_df.transpose()

def get_12mo_ret(ret12mo_df,col):
    return_12month={}
    ret12mo_df_grpd = ret12mo_df.groupby('yrmo')
    for yrmo in ret12mo_df.yrmo.unique():
        return_12month[yrmo] = (ret12mo_df_grpd.get_group(yrmo)[col] + 1).dropna().product()-1
    return_12month_df = pd.DataFrame(return_12month, index=[col+'_rm12mo']).transpose()
    return_12month_df.index = pd.to_datetime(return_12month_df.index, format='%Y%m')
    return return_12month_df

def get_market_return_12month(RET_MKT_D_KSE, reg_mo_lst, decimal_unit, to_csv):
    '''
    INPUT: daily mkt ret
    OUTPUT: monthly mkt ret 12 mo
    idx == 'datetime64[ns]'
    '''
    RET_MKT_D_KSE_ret12mo = RET_MKT_D_KSE[  (RET_MKT_D_KSE.index >= reg_mo_lst.min()-relativedelta(years=1)) \
                                & (RET_MKT_D_KSE.index < reg_mo_lst.max()+relativedelta(months=1)) ]
    RET_MKT_D_KSE_ret12mo_mo_df = pd.Series(RET_MKT_D_KSE_ret12mo.index).to_frame('idx')
    RET_MKT_D_KSE_ret12mo_mo_df['yrmo'] = RET_MKT_D_KSE_ret12mo_mo_df.idx.apply(lambda x: datetime.strftime(x, '%Y%m'))
    # RET_MKT_D_KSE_ret12mo_mo_df['rm_mo'] = RET_MKT_D_KSE_ret12mo_mo_df.idx.apply(lambda x: datetime.strftime(x, '%Y%m'))
    RET_MKT_D_KSE_ret12mo_mo_df = RET_MKT_D_KSE_ret12mo_mo_df.set_index('idx')
    RET_MKT_D_KSE_ret12mo_df = pd.concat([RET_MKT_D_KSE_ret12mo,RET_MKT_D_KSE_ret12mo_mo_df],axis=1)

    market_return_12month_df = get_12mo_ret(RET_MKT_D_KSE_ret12mo_df,'Rm')
    if decimal_unit==True:
        return market_return_12month_df
        if to_csv==True:
            market_return_12month_df.to_csv('market_return_12month_df.csv')
    else:
        return market_return_12month_df*100
        if to_csv==True:
            market_return_12month_df_perc = market_return_12month_df*100
            market_return_12month_df_perc.to_csv('market_return_12month_df_perc.csv')

def SMB_HML_UMD_ret12(SMB_HML_UMD_df_wo_wknds, reg_mo_lst, to_csv, decimal_unit):
    '''
    INPUT:
    OUTPUT:
    idx == 'datetime64[ns]'
    '''
    SMB_HML_UMD_df_wo_wknds.index = pd.to_datetime(SMB_HML_UMD_df_wo_wknds.index)
    SMB_HML_UMD_df_wo_wknds = SMB_HML_UMD_df_wo_wknds[  (SMB_HML_UMD_df_wo_wknds.index >= reg_mo_lst.min()-relativedelta(years=1)) \
                                & (SMB_HML_UMD_df_wo_wknds.index < reg_mo_lst.max()+relativedelta(months=1)) ]
    SMB_HML_UMD_df_wo_wknds_mo_df = pd.Series(SMB_HML_UMD_df_wo_wknds.index).to_frame('idx')
    SMB_HML_UMD_df_wo_wknds_mo_df['yrmo'] = SMB_HML_UMD_df_wo_wknds_mo_df.idx.apply(lambda x: datetime.strftime(x, '%Y%m'))
    SMB_HML_UMD_df_wo_wknds_mo_df = SMB_HML_UMD_df_wo_wknds_mo_df.set_index('idx')
    SMB_HML_UMD_df_wo_wknds_df = pd.concat([SMB_HML_UMD_df_wo_wknds,SMB_HML_UMD_df_wo_wknds_mo_df],axis=1)

    SMB12 = get_12mo_ret(SMB_HML_UMD_df_wo_wknds_df[['SMB','yrmo']], 'SMB')
    HML12 = get_12mo_ret(SMB_HML_UMD_df_wo_wknds_df[['HML','yrmo']], 'HML')
    UMD12 = get_12mo_ret(SMB_HML_UMD_df_wo_wknds_df[['UMD','yrmo']], 'UMD')

    if decimal_unit==True:
        if to_csv==True:
            SMB12.to_csv('SMB12.csv')
            HML12.to_csv('HML12.csv')
            UMD12.to_csv('UMD12.csv')
        return SMB12, HML12, UMD12

    else:
        if to_csv==True:
            SMB12_perc, SMB12_perc, SMB12_perc = SMB12*100, HML12*100, UMD12*100
            SMB12_perc.to_csv('SMB12_perc.csv')
            HML12_perc.to_csv('HML12_perc.csv')
            UMD12_perc.to_csv('UMD12_perc.csv')
        return SMB12*100, HML12*100, UMD12*100
