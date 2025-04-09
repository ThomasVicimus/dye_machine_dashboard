import pandas as pd 
import warnings
import re
import win32com
from datetime import datetime
import os
import time
warnings.simplefilter(action='ignore', category=UserWarning)

def filter_fs_by_date(rawdata,yearmonth):
    for file in rawdata:
        # print(file)
        fs_date=re.findall(r'\d{6}',file)[0]
        fs_year=int(fs_date[0:4])
        year=int(yearmonth[0:4])
        if fs_year+1<year:
            rawdata.remove(file)
    return rawdata    

def sort_fs_by_store(rawdata,fs,stores):
    # rawdata_dict={}
    for store in stores:
        fs[store]=[]
        # rawdata_dict[store]=[]
    for store in stores:
        for file in rawdata:
            if file.startswith(store):
                fs[store].append(file)
    
    return fs
def separate_by_year(fs_by_store,years,fs_by_year={}):
    for y in years:
        fs_by_year[y]=[]
        for file in fs_by_store:
            fs_yearmonth=re.findall(r'\d{6}',file)[0]
            fs_year=fs_yearmonth[0:4]
            # df_fs=pd.read_excel(FS_PATH+file,sheet_name='Page 2')          
            if fs_year==str(y):
                fs_by_year[y].append(file)
    return fs_by_year

def sort_fs_by_type(fs_in_year,_type,fs_type={}):
    for key in _type:
        fs_type[key]=[]
    for file in fs_in_year:
        if bool((re.search('FS-HY',file))) & ('FS-HY'in _type):
            fs_type['FS-HY'].append(file)
        elif bool((re.search('FS-TY',file))) & ('FS-TY'in _type):
            fs_type['FS-TY'].append(file)
        elif bool((re.search('FS',file))) & ('FS'in _type):
            fs_type['FS'].append(file)
    return fs_type

def sort_fs_by_sys(fs_by_type,sys,fs_sys={}):
    for key in sys:
        fs_sys[key]=[]
    for file in fs_by_type:
        if file.endswith('.xlsm'):
            fs_sys['RR'].append(file)
        else:
            fs_sys['Te'].append(file)
    return fs_sys

def clean_fs(df_fs,key_type):
    if key_type=='FS-TY':
        df_fs=df_fs.loc[7:]
        cols=[]
        for col in df_fs.columns:
            cols.append(col.replace('Unnamed: ','col'))
        cols = list(map(lambda x: x.replace('col2', 'name'), cols))
        cols = list(map(lambda x: x.replace('col4', 'acc'), cols))
        cols = list(map(lambda x: x.replace('col5', 'amt'), cols))
        
        df_fs.columns=cols
        df_fs=df_fs[['name','acc','amt']]
        df_fs=df_fs.dropna(axis=0,subset='acc')
        df_fs.acc=df_fs.acc.astype(str)
    elif key_type=='FS-HY':
        df_fs=df_fs.loc[8:]
        cols=[]
        for col in df_fs.columns:
            cols.append(col.replace('Unnamed: ','col'))
        cols = list(map(lambda x: x.replace('col0', 'name'), cols))
        cols = list(map(lambda x: x.replace('col3', 'acc'), cols))
        cols = list(map(lambda x: x.replace('col4', 'amt'), cols))

        df_fs.columns=cols
        df_fs=df_fs[['name','acc','amt']]
        df_fs=df_fs.dropna(axis=0,subset='acc')
        df_fs.acc=df_fs.acc.apply(lambda x : ('0'+str(x)) if len(str(x))<2 else str(x))
    elif key_type=='FS':
        df_fs=df_fs.loc[7:]
        cols=[]
        for col in df_fs.columns:
            cols.append(col.replace('Unnamed: ','col'))
        cols = list(map(lambda x: x.replace('col2', 'name'), cols))
        cols = list(map(lambda x: x.replace('col4', 'acc'), cols))
        cols = list(map(lambda x: x.replace('col5', 'amt'), cols))
        
        df_fs.columns=cols
        df_fs=df_fs[['name','acc','amt']]
        df_fs=df_fs.dropna(axis=0,subset='acc')
        df_fs.acc=df_fs.acc.astype(str)

    return df_fs

def clean_fs_with_name(df_fs,key_type):
    if key_type=='FS-TY':
        df_fs=df_fs.loc[7:]
        cols=[]
        for col in df_fs.columns:
            cols.append(col.replace('Unnamed: ','col'))
        cols = list(map(lambda x: x.replace('col2', 'name'), cols))
        cols = list(map(lambda x: x.replace('col4', 'acc'), cols))
        cols = list(map(lambda x: x.replace('col5', 'amt'), cols))
        
        df_fs.columns=cols
        df_fs=df_fs[['name','acc','amt']]
        df_fs=df_fs.dropna(axis=0,subset='amt')
        df_fs.acc=df_fs.acc.astype(str)
    elif key_type=='FS-HY':
        df_fs=df_fs.loc[8:]
        cols=[]
        for col in df_fs.columns:
            cols.append(col.replace('Unnamed: ','col'))
        cols = list(map(lambda x: x.replace('col0', 'name'), cols))
        cols = list(map(lambda x: x.replace('col3', 'acc'), cols))
        cols = list(map(lambda x: x.replace('col4', 'amt'), cols))

        df_fs.columns=cols
        df_fs=df_fs[['name','acc','amt']]
        df_fs=df_fs.dropna(axis=0,subset='amt')
        df_fs.acc=df_fs.acc.apply(lambda x : ('0'+str(x)) if len(str(x))<2 else str(x))
    elif key_type=='FS':
        df_fs=df_fs.loc[7:]
        cols=[]
        for col in df_fs.columns:
            cols.append(col.replace('Unnamed: ','col'))
        cols = list(map(lambda x: x.replace('col2', 'name'), cols))
        cols = list(map(lambda x: x.replace('col4', 'acc'), cols))
        cols = list(map(lambda x: x.replace('col5', 'amt'), cols))
        
        df_fs.columns=cols
        df_fs=df_fs[['name','acc','amt']]
        df_fs=df_fs.dropna(axis=0,subset='amt')
        df_fs.acc=df_fs.acc.astype(str)

    return df_fs

def extract_amt(df_fs,fs_yearmonth,acc_list):
    mask=df_fs.acc.isin(acc_list)
    _df=df_fs.loc[mask][['amt']].reset_index(drop=True)
    _df.loc['tot']=pd.Series(_df.amt.sum(),index=['amt'])
    _df.columns=[fs_yearmonth]
  
    return _df

def extract_amt_with_name(df_fs,fs_yearmonth,name_list):
    mask=df_fs.name.isin(name_list)
    _df=df_fs.loc[mask][['amt']].reset_index(drop=True)
    _df.loc['tot']=pd.Series(_df.amt.sum(),index=['amt'])
    _df.columns=[fs_yearmonth]
  
    return _df

def convert_to_negative_RR(_df,index_no):
    # col=_df.columns[0]
    
    _df.iloc[index_no]=-_df.iloc[index_no]
    return _df

def cal_total(amt_of_each_year,store):
    if store in ['RHH','THH']:
        amt_of_each_year=amt_of_each_year.reset_index(drop=True)
        amt_of_each_year.iloc[2]=amt_of_each_year.iloc[0]+amt_of_each_year.iloc[1]
        amt_of_each_year.iloc[6]=amt_of_each_year.iloc[3:6].sum()
    return amt_of_each_year

def get_grandtotal(output,fs_sheetname):
    _df=pd.read_excel(output,sheet_name=fs_sheetname)
    # _df=pd.read_excel(output)
    row=len(_df)
    cols=_df.columns
    grandtotal=_df.iloc[[row-1]][cols[2:]].copy()
    return grandtotal

def get_grandtotal_v2(output,fs_sheetname,_grand_tot_col_no):
    _df=pd.read_excel(output,sheet_name=fs_sheetname)
    mask=_df.iloc[:,_grand_tot_col_no]=='Grand Total'
    grandtotal=_df.loc[mask]
    if len(grandtotal)>1:
        grandtotal=grandtotal.iloc[1:,0:]
    
    return grandtotal

def remove_FS_cell_value(wb,fs_sheetname,config__FS_cells__store):
    ws=wb.sheets(fs_sheetname)
    for range in config__FS_cells__store:
        ws.range(range).value=None
    wb.save()
    

def modify_pivot_table_years(excel_file_path, sheet_name, field_name):
    # exclude & include years
    TY=str(datetime.today().year)
    LY=str(datetime.today().year-1)   
    # Create Excel application
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = True  # Set to True if you want to see Excel in action

    # Open the workbook
    workbook = excel_app.Workbooks.Open(os.path.abspath(excel_file_path))
    worksheet = workbook.Sheets(sheet_name)

    for pvt in worksheet.PivotTables():
        for item in pvt.PivotFields(field_name).PivotItems():
            try:
                time.sleep(0.5)
                pvt.PivotFields(field_name).PivotItems(item.Name).Visible = False
            except Exception:
                pass
        pvt.PivotFields(field_name).PivotItems(TY).Visible = True
        pvt.PivotFields(field_name).PivotItems(LY).Visible = True
    # Save and close the workbook
    workbook.Save()
    excel_app.Quit()