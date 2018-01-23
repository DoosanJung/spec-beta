'''
THIS MODULE IS FOR
- Spec v.s Non-spec
- Pre_ranking_pfo
- Pre_ranking_pfo_aggdisp
- Figure5
- get_Table4
'''
from module1_wo_wknds import *

def pre_ranking_beta_spnsp(E_Ri, E_Rm, i, mo, symbols_lst, m_mkt_cap, m_vol, m_stock_level_disp, to_csv):
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

    pre_ranking_beta_df_spec = pd.DataFrame(pre_ranking_beta_Frame, index=symbols_lst)
    # [symbols] x [mo, sum_beta, symbol]
    # 751 x 3

    # tmp_df = pd.DataFrame()
    # individual vol from monthly table
    pre_ranking_beta_df_spec['m_vol'] = m_vol.transpose().iloc[:,i]   # [symbol] x [months]

    # individual mkt_cap from monthly table
    pre_ranking_beta_df_spec['m_mkt_cap'] = m_mkt_cap.transpose().iloc[:,i] # mo 2010-01-31 ~ 2016-09-30

    # individual Stock-level disagreement from monthly table
    pre_ranking_beta_df_spec['m_stock_level_disp'] = m_stock_level_disp.transpose().iloc[:,i]

    #
    pre_ranking_beta_df_spec['sum_beta_median_vol_ratio'] = pre_ranking_beta_df_spec['sum_beta'] / pre_ranking_beta_df_spec['m_vol']

    if to_csv==True:
        pre_ranking_beta_df_spec.to_csv('pre_ranking_beta_df_spec_wo_wknds.csv')
    else:
        pass
    return pre_ranking_beta_df_spec, E_Ri_ret




# each month...
def assign_beta_pfo_spnsp(result, mo, E_Ri_ret, to_csv, spnsp):
    percentile_lst = zip(np.arange(0,1,0.05), np.arange(0.05,1.05,0.05))
    pfo_N_stocks={}
    pfo_median_vol={}
    pfo_stock_disp={}
    pfo_perc_mkt_cap={}
    pfo_avg_of_sumbeta={}
    pfo_sum_beta_median_vol_ratio={}
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
                pfo_sum_beta_median_vol_ratio["pfo_{0}".format(('0'+str(k))[-2:])] = pfo_k.sum_beta_median_vol_ratio.median()
                # value-weighting schema for AggDisp
                s = pfo_k.sum_beta
                m = pfo_k.m_stock_level_disp
                c = pfo_k.m_mkt_cap
                vw = c/np.sum(c) # weighting schema
                pfo_stock_disp["pfo_{0}".format(('0'+str(k))[-2:])] =  np.nansum(m.multiply(vw, fill_value=0))
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
            if spnsp == 'sp':
                d_ret_df_ew.to_csv('d_ret_df_ew_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds_sp.csv')
                d_ret_df_vw.to_csv('d_ret_df_vw_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds_sp.csv')
            else:
                d_ret_df_ew.to_csv('d_ret_df_ew_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds_nsp.csv')
                d_ret_df_vw.to_csv('d_ret_df_vw_' + mo.strftime('%Y%m') + '_' + str(month) + '_wo_wknds_nsp.csv')
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


    pfo_idx = ['pfo_N_stocks', 'pfo_median_vol', 'pfo_stock_disp', 'pfo_perc_mkt_cap', 'pfo_avg_of_sumbeta', 'pfo_sum_beta_median_vol_ratio',\
                'ret1_ew', 'ret1_vw', 'ret3_ew', 'ret3_vw','ret6_ew', 'ret6_vw', 'ret12_ew', 'ret12_vw']
    return pd.DataFrame([pfo_N_stocks, pfo_median_vol, pfo_stock_disp, pfo_perc_mkt_cap, pfo_avg_of_sumbeta, pfo_sum_beta_median_vol_ratio,\
                ret1_ew_mean, ret1_vw_mean, ret3_ew_mean, ret3_vw_mean, ret6_ew_mean, ret6_vw_mean, \
                ret12_ew_mean, ret12_vw_mean],\
                 index = pfo_idx), pfo_idx


def get_Table4(Table4_df_monthly, pfo_idx):
    Table4={}
    for col in pfo_idx:
        Table4[col]=Table4_df_monthly.transpose()[col].mean(axis=1)
    Table4_df = pd.DataFrame(Table4)
    return Table4_df.transpose()
