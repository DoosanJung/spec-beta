'''
'''

import logging
from logging import config
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig
from spec_beta.src.ReturnDataPrep import ReturnDataPrep
from spec_beta.src.MiscDataPrep import MiscDataPrep
from spec_beta.src.RegPrep import RegPrep

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()

class PreRankingBeta(object):

    #######################################################################
    #TODO: below

    return_data_prep = ReturnDataPrep()

    # Stock symbols
    symbols_lst = return_data_prep.get_symbols_lst()


    # Regression month list # 2010-01-01 ~ 2016-09-01
    reg_mo_lst = get_reg_mo_lst(201001,201709)

    # return data
    RET_D_KSE = get_Ri_wo_wknds(decimal_unit)
    RET_MKT_D_KSE = get_Rm_wo_wknds(decimal_unit)
    RF_CALL1 = get_Rf_wo_wknds(decimal_unit, reg_mo_lst)
    E_Ri = get_E_Ri_wo_wknds(RET_D_KSE, RF_CALL1, symbols_lst, reg_mo_lst)
    E_Rm = get_E_Rm_wo_wknds(RET_MKT_D_KSE, RF_CALL1, reg_mo_lst)
    return RET_D_KSE, RET_MKT_D_KSE, RF_CALL1, E_Ri, E_Rm







if __name__=="__main__":

    # Control
    # ew = True
    to_csv = False
    decimal_unit = True

    # data
    symbols_lst = get_symbols_lst()    # Stock symbols
    reg_mo_lst = get_reg_mo_lst(201001,201709)     # Regression month list # 2010-01-01 ~ 2016-09-01
    RET_D_KSE, RET_MKT_D_KSE, RF_CALL1, E_Ri, E_Rm = get_return_data_wo_wknds(decimal_unit, symbols_lst, reg_mo_lst, 'd')
    # RET_D_KSE              returns 2009-01-01 ~ 2017-11-03
    # RET_MKT_D_KSE          returns 2008-01-01 ~ 2017-11-03
    # RF_CALL1               returns 2009-01-01 ~ 2017-11-03
    # E_Ri                   returns 2009-01-01 ~ 2017-11-03
    # E_Rm                   returns 2009-01-01 ~ 2017-11-03

    m_stock_level_disp = get_m_stock_level_disp(reg_mo_lst)    # Monthly Stock-level disagreement # 2010-01-01 ~ 2016-09-01
    m_mkt_cap = get_monthly_mkt_cap(reg_mo_lst, to_csv)     # Monthly Market_cap # 2010-01-31 ~ 2016-09-30
    # m_mkt_cap = pd.read_csv('m_mkt_cap.csv',index_col=0)
    m_vol = get_monthly_vol(reg_mo_lst, to_csv)     # Monthly Vol
    # m_vol = pd.read_csv('m_vol.csv', index_col=0)

    Table1_monthly_wo_wknds = []
    AggDisp_wo_wknds = []
    for i, mo in tqdm(enumerate(reg_mo_lst)):
        # calculate pre_ranking_beta for each stock
        # for the month mo
        pre_ranking_beta_df, E_Ri_ret = pre_ranking_beta(E_Ri, E_Rm, i, mo, symbols_lst, m_mkt_cap, m_vol, m_stock_level_disp, to_csv)
        AggDisp_wo_wknds.append(pre_ranking_beta_df)

        # monthly table1
        # for the month mo
        pfos, pfo_idx = assign_beta_pfo(pre_ranking_beta_df, mo, E_Ri_ret, to_csv)
        Table1_monthly_wo_wknds.append(pfos)
        Table1_df_monthly_wo_wknds = pd.concat(Table1_monthly_wo_wknds)
        AggDisp_df_wo_wknds = pd.concat(AggDisp_wo_wknds)

    # TO SAVE AS CSV
    if to_csv == True:
        # Table1_df_monthly_wo_wknds.to_csv('Table1_df_monthly_wo_wknds.csv')
        # AggDisp_df_wo_wknds.to_csv('AggDisp_df_wo_wknds.csv')
        Table1_df_monthly_wo_wknds.to_csv('Table1_df_monthly_wo_wknds_new.csv')
        AggDisp_df_wo_wknds.to_csv('AggDisp_df_wo_wknds_new.csv')
    else:
        pass

    # TO SAVE AS CSV
    Table1_df_wo_wknds = get_Table1(Table1_df_monthly_wo_wknds, pfo_idx)
    if to_csv == True:
        # Table1_df_wo_wknds.to_csv('Table1_df_wo_wknds.csv')
        Table1_df_wo_wknds.to_csv('Table1_df_wo_wknds_new.csv')
