'''
main.py shd get var by:
kwargs = {k:v for k,v in locals().items() if k in deploy_FS.__code__.co_varnames}
depoly_FS(kwargs)
depoly FS value to excel
'''

from function.fs_func import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
# warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
# import pandas as pd
# import numpy as np
# import os
# import sys
# sys.path.insert(0, '../../_templates/function/')
from function.short_utilities import *
# from function.clf_func import *
# from function.save_option import *
# from function.utilities import *
# from function.clf_func import *
# from function.save_option import *
# from function.script_schedule import *
import xlwings as xw
import json
# import logging

def depoly_fs(
        # force_start : bool,
              fs_config : dict,
              assigned_store : list,
              assigned_yearmonth : str,
              first_n_month_of_year : bool,
              output_paths : dict,
              config : dict):

    print('Data Validation from Financial Statement Starts')   

    year=int(assigned_yearmonth[0:4])
    lastyear=year-1
    thisyear=year
    rawdata=[]
    FS_PATH='..\\../raw_data/FS/'
    for file in os.listdir(FS_PATH):
        if (file.endswith('.xlsm')) |(file.endswith('.xlsx')):
            rawdata.append(file)
    rawdata=filter_fs_by_date(rawdata,assigned_yearmonth)

    fs={}
    fs=sort_fs_by_store(rawdata,fs,assigned_store)

    if not 'extract_fs_amt_by_name' in fs_config.keys():
        fs_config['extract_fs_amt_by_name']=False

    for store in assigned_store:

        if first_n_month_of_year:
            year_list=[lastyear,thisyear]
            modify_pivot_table_years(output_paths[store], fs_config['fs_sheetname'], 'Years')
        else:
            year_list=[thisyear]

        fs_by_year=separate_by_year(fs[store],year_list)

        amt_by_year={}
        for y in year_list:
            fs_type=sort_fs_by_type(fs_by_year[y],fs_config['type_by_store'][store])
        
            amt_by_type={}
            for key_type in fs_config['type_by_store'][store]:


                files=fs_type[key_type]
                
                amt_={}
                for file in files:
                    fs_yearmonth=re.findall(r'\d{6}',file)[0]
                    fs_year=fs_yearmonth[0:4]
                    df_fs=pd.read_excel(FS_PATH+file,sheet_name='Page 2')          
                    # if fs_year==str(y):
                    if not fs_config['extract_fs_amt_by_name']:
                        df_fs=clean_fs(df_fs,key_type)
                        _df=extract_amt(df_fs,fs_yearmonth,fs_config['acc_by_type'][key_type])
                    else:
                        df_fs=clean_fs_with_name(df_fs,key_type)
                        _df=extract_amt_with_name(df_fs,fs_yearmonth,fs_config['acc_by_type'][key_type])

                    amt_[fs_yearmonth]=_df

                amt_by_type[key_type]=concat_df_indict(amt_,1)
            amt_by_year[y]= concat_df_indict(amt_by_type.copy(),0)
            if fs_config['drop_tot']:
                amt_by_year[y]=amt_by_year[y].drop(index='tot')


        app=xw.App()
        app.display_alerts = False
        wb=app.books.open(output_paths[store],read_only=False)

        wb.sheets[fs_config['fs_sheetname']].select()
        pvt_name=[pt.Name for pt in wb.api.ActiveSheet.PivotTables()]
        wb.api.ActiveSheet.PivotTables(pvt_name[0]).PivotCache().Refresh()
        wb.save(output_paths[store])

        sht=wb.sheets(fs_config['fs_sheetname'])
        if first_n_month_of_year:
            remove_FS_cell_value(wb,fs_config['fs_sheetname'],config['FS_cells'][store])
            sht[fs_config['LY_cell']].value=amt_by_year[lastyear].values
            # sht[LY_cell].options(pd.DataFrame,index=False,header=False,expand='table').value=amt_by_year[lastyear]
        # print(amt_by_year[thisyear][0:-1])
        sht[fs_config['TY_cell']].value=amt_by_year[thisyear].values
        # sht[TY_cell].options(pd.DataFrame,index=False,header=False,expand='table').value=amt_by_year[thisyear]
        
        sht[fs_config['grandtotal_cell'][store]].options(pd.DataFrame,index=False,header=False,expand='table').value=get_grandtotal_v2(output_paths[store],fs_config['fs_sheetname'],0).iloc[0:,fs_config['grand_tot_cell_for_iloc']:]
        # sht[fs_config['grandtotal_cell'][store]].value=get_grandtotal_v2(output_paths[store],fs_config['fs_sheetname'],0).iloc[0:,fs_config['grand_tot_cell_for_iloc']:]

        wb.api.ActiveSheet.PivotTables(pvt_name[0]).PivotCache().Refresh()
        wb.save(output_paths[store])
        app.quit()
        print(json.dumps(output_paths[store]))


    print('Data Validation Completed!')