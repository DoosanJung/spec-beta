'''
(1)
```bash
head -1 ff20170802aa_duplicate_.csv > ff20170802_duplicate_.csv
for filename in $(ls ff*.csv); do sed 1d $filename >> ff20170802_duplicate_.csv; done
```

(2)
Manually edit pfo_1 >> pfo_01

(3)
```python
df = df.reindex_axis(sorted(df.columns), axis=1)
```
'''

from module1 import *

if __name__=="__main__":

    # Control
    # ew = True
    to_csv = False
    decimal_unit = True

    # data
    symbols_lst = get_symbols_lst()    # Stock symbols
    reg_mo_lst = get_reg_mo_lst(201001,201709)     # Regression month list # 2010-01-01 ~ 2016-09-01
    RET_D_KSE, RET_MKT_D_KSE, RF_CALL1, E_Ri, E_Rm = get_return_data(decimal_unit, symbols_lst, 'd')
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

    Table1_monthly = []
    AggDisp = []
    for i, mo in tqdm(enumerate(reg_mo_lst)):
        # calculate pre_ranking_beta for each stock
        # for the month mo
        pre_ranking_beta_df, E_Ri_ret = pre_ranking_beta(E_Ri, E_Rm, i, mo, symbols_lst, m_mkt_cap, m_vol, m_stock_level_disp, to_csv)
        AggDisp.append(pre_ranking_beta_df)

        # monthly table1
        # for the month mo
        pfos, pfo_idx = assign_beta_pfo(pre_ranking_beta_df, mo, E_Ri_ret, to_csv)
        Table1_monthly.append(pfos)
        Table1_df_monthly = pd.concat(Table1_monthly)
        AggDisp_df = pd.concat(AggDisp)

    # TO SAVE AS CSV
    if to_csv == True:
        Table1_df_monthly.to_csv('Table1_df_monthly.csv')
        AggDisp_df.to_csv('AggDisp_df.csv')
    else:
        pass

    # TO SAVE AS CSV
    Table1_df = get_Table1(Table1_df_monthly, pfo_idx)
    if to_csv == True:
        Table1_df.to_csv('Table1_df.csv')
