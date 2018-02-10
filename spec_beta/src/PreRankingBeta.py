#!/usr/bin/env python
'''
'''
import logging
from logging import config
import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import numpy as np
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep
from spec_beta.src.MiscDataPrep import MiscDataPrep
from spec_beta.src.RegPrep import RegPrep

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class PreRankingBeta(object):
    '''
    Regression to calculate Betas
    '''
    def __init__(self, start_mo, end_mo):
        self.home_path = SpecBetaConfig.HOME_PATH
        self.file_path = SpecBetaConfig.FILE_PATH
        self.to_csv = SpecBetaConfig.to_csv
        self.decimal_unit = SpecBetaConfig.decimal_unit
        self.start_mo = start_mo
        self.end_mo = end_mo
        # rdp = ReturnDataPrep(self.start_mo, self.end_mo)
        # self.E_Rm = rdp.get_E_Rm_wo_wknds()
        # self.E_Ri = rdp.get_E_Ri_wo_wknds()
        # self.symbols_lst = rdp.symbols_lst

    # Each month...
    def pre_ranking_beta(self, i, mo, E_Rm, E_Ri, symbols_lst, m_stock_level_disp, m_mkt_cap, m_vol):
        '''
            Monthly # symbol, sum_beta, ret1,3,6,12  pfo_number, mo, mkt_cap, vol, disp.

            REGRESSION: ALL PERCENTAGE UNIT (regressor_Rm and E_Ri_t)
            RETURN CALCULATION: decimal_unit (E_Ri_ret)
        '''
        # X + constant: independent variables
        regressor_Rm = RegPrep.get_regressor(E_Rm = E_Rm, mo = mo)
        # Percent unit for regression

        # Y : a dependent varialbe
        E_Ri_t = E_Ri[(E_Ri.index < mo )& (E_Ri.index >= mo - relativedelta(years=1))]
        # Percent unit for regression
        E_Ri_t = E_Ri_t*100

        # To calculate individual return: decimal unit
        E_Ri_ret = E_Ri[(E_Ri.index >= mo )& (E_Ri.index < mo + relativedelta(years=1))]

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
                        model = RegPrep.run_ols(OLS_df[symbol] , OLS_df.drop(symbol, axis=1) , pfunc=False)
                        sum_beta = np.sum(model.params.drop('const'))
                    sum_beta_dict['sum_beta'] = sum_beta # sum_beta
                    pre_ranking_beta_Frame.append(sum_beta_dict)
                else:
                    raise ValueError
            except:
                print "WARNING!!! ",symbol

        pre_ranking_beta_df = pd.DataFrame(pre_ranking_beta_Frame, index = symbols_lst)
        # [symbols] x [mo, sum_beta, symbol]
        # 751 x 3

        # individual vol from monthly table
        pre_ranking_beta_df['m_vol'] = m_vol.transpose().iloc[:,i]   # [symbol] x [months]

        # individual mkt_cap from monthly table
        pre_ranking_beta_df['m_mkt_cap'] = m_mkt_cap.transpose().iloc[:,i] # mo 2010-01-31 ~ 2016-09-30

        # individual Stock-level disagreement from monthly table
        pre_ranking_beta_df['m_stock_level_disp'] =m_stock_level_disp.transpose().iloc[:,i]

        if self.to_csv==True:
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
    def assign_beta_pfo(self, df, mo, E_Ri_ret):
        '''

        '''
        percentile_lst = zip(np.arange(0,1,0.05), np.arange(0.05,1.05,0.05))
        pfo_N_stocks={}
        pfo_median_vol={}
        pfo_stock_disp={}
        pfo_perc_mkt_cap={}
        pfo_avg_of_sumbeta={}
        Total_m_mkt_cap = df.m_mkt_cap.sum() # of this month mo

        d_ret_ew={}
        d_ret_vw={}
        for month in [1,3,6,12]:
            for k, (bottom,top) in enumerate(percentile_lst):
                indicator = 0
                if indicator == 0:
                    pfo_k = df[(df['sum_beta'] >= df['sum_beta'].quantile(bottom)) & (df['sum_beta'] <= df['sum_beta'].quantile(top))]

                    pfo_N_stocks["pfo_{0}".format(('0'+str(k))[-2:])] = df[(df['sum_beta'] > df['sum_beta'].quantile(bottom)) & (df['sum_beta'] <= df['sum_beta'].quantile(top))].shape[0]
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

                # equal-weighting schema
                ew_df = pfo_k_ret/len(pfo_k_ret.columns)
                d_ret_ew["pfo_{0}".format(k)] = ew_df.sum(axis=1)

                # value-weighting schema
                mkt_cap = pd.read_csv(self.home_path + self.file_path['market_cap'],index_col=0)
                mkt_cap.index = pd.to_datetime(mkt_cap.index)
                mkt_cap = mkt_cap[mkt_cap.index.isin(E_Ri_ret_lag.index)]
                mkt_cap = mkt_cap[pfo_k.index.tolist()]
                vw_mkt_cap = mkt_cap.divide(mkt_cap.sum(axis=1),axis=0)
                vw_df = pfo_k_ret.multiply(vw_mkt_cap)
                d_ret_vw["pfo_{0}".format(k)] = vw_df.sum(axis=1)

            d_ret_df_ew = pd.DataFrame(d_ret_ew)
            d_ret_df_ew = self.rearrange_d_ret_df(d_ret_df_ew)
            d_ret_df_vw = pd.DataFrame(d_ret_vw)
            d_ret_df_vw = self.rearrange_d_ret_df(d_ret_df_vw)

            if self.to_csv==True:
                d_ret_df_ew.to_csv('d_ret_df_ew_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds.csv')
                d_ret_df_vw.to_csv('d_ret_df_vw_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds.csv')
            else:
                pass

            if month ==1:
                ret1_ew = d_ret_df_ew
                ret1_vw = d_ret_df_vw
                ret1_ew_mean = (ret1_ew+1).drop_duplicates().product()-1
                ret1_vw_mean = (ret1_vw+1).drop_duplicates().product()-1

            elif month==3:
                ret3_ew = d_ret_df_ew
                ret3_vw = d_ret_df_vw
                ret3_ew_mean = (ret3_ew+1).drop_duplicates().product()-1
                ret3_vw_mean = (ret3_vw+1).drop_duplicates().product()-1

            elif month==6:
                ret6_ew = d_ret_df_ew
                ret6_vw = d_ret_df_vw
                ret6_ew_mean = (ret6_ew+1).drop_duplicates().product()-1
                ret6_vw_mean = (ret6_vw+1).drop_duplicates().product()-1

            elif month==12:
                ret12_ew = d_ret_df_ew
                ret12_vw = d_ret_df_vw
                ret12_ew_mean = (ret12_ew+1).drop_duplicates().product()-1
                ret12_vw_mean = (ret12_vw+1).drop_duplicates().product()-1
            else:
                pass


        pfo_idx = SpecBetaConfig.Beta_pfos_cols
        return pd.DataFrame([pfo_N_stocks, pfo_median_vol, pfo_stock_disp, pfo_perc_mkt_cap, pfo_avg_of_sumbeta, \
                    ret1_ew_mean, ret1_vw_mean, ret3_ew_mean, ret3_vw_mean, ret6_ew_mean, ret6_vw_mean, \
                    ret12_ew_mean, ret12_vw_mean],\
                     index = pfo_idx)

    def rearrange_d_ret_df(self, d_ret_df):
        '''
        rename pfo return dfs
        '''
        renamed_pfo_lst = [u'pfo_00', u'pfo_01', u'pfo_10', u'pfo_11', u'pfo_12', u'pfo_13',
           u'pfo_14', u'pfo_15', u'pfo_16', u'pfo_17', u'pfo_18', u'pfo_19',
           u'pfo_02', u'pfo_03', u'pfo_04', u'pfo_05', u'pfo_06', u'pfo_07', u'pfo_08', u'pfo_09']
        d_ret_df.columns = renamed_pfo_lst
        d_ret_df = d_ret_df.reindex_axis(sorted(d_ret_df.columns), axis=1)
        return d_ret_df
