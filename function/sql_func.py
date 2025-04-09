import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .short_utilities import *
import re

def locate_sql(name=False,path=False):
    #v2.0 20230617
    if not path:
        path=os.getcwd()
    
    if name==False:
        name = sys.argv[0].split('.')[0]
        # PATH=os.getcwd()
        files=[]
        
        for file in os.listdir(path):
            # if file.startswith(name):
            if file.endswith('.sql'):
                files.append(file)

    else:
        files=[]
        for file in os.listdir(path):
            if file.startswith(name):
                if file.endswith('.sql'):
                    files.append(file)

    if len(files)==1:
        files=files[0]
    return files

def open_sql(file_name,cursor):
    file=open(file_name,'r')
    Q=file.read()
    file.close()

    cursor.execute(Q)
    df=pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
    return df

def normalize_stores(df_source,col_to_be_normalized,groupby='part_id'):
    df_source.dealer_id=df_source.dealer_id.astype(int)

    _df_info_gp=df_source.groupby(groupby).agg({groupby:np.size})
    _df_info_gp.columns=['cnt']
    _df_info_gp=_df_info_gp.reset_index()
    # _df_info_gp.dealer_id=_df_info_gp.dealer_id.astype(int)

    df_source=pd.merge(left=df_source,right=_df_info_gp,on=groupby)

    dfs_dealer={}
    cnt1=xloc(df_source,'cnt',1)
    # for v in cnt1.dealer_id.unique():
    v=1126
    dfs_dealer[str(v)]=xloc(cnt1,col_to_be_normalized,v).copy()
    dfs_dealer[str(v)].dealer_id=1226
    v=1226
    dfs_dealer[str(v)]=xloc(cnt1,col_to_be_normalized,v).copy()
    dfs_dealer[str(v)].dealer_id=1126

    df_source=pd.concat([df_source,concat_df_indict(dfs_dealer)])

    return df_source

def date_folder():
    _date={}
    _date['m']=datetime.today().month
    _date['d']=datetime.today().day
    for v in _date.keys():
        if _date[v] <10:
            _date[v]='0'+str(_date[v])
        else:
            _date[v]=str(_date[v])

    tdy_date=str(datetime.today().year)+_date['m']+_date['d']+'/'
    return tdy_date

def get_gl_replace(gl_acc,dealer_id=['1126','1226']):
    #get acc
    if isinstance(gl_acc,str):
        if re.search('-',gl_acc):
            acc=[]
            min=int(gl_acc.split('-')[0])
            max=int(gl_acc.split('-')[-1])+1
            for n in range(min,max):
                acc.append(str(n))
        else:
            acc=gl_acc.split(',')
    else:
        acc=gl_acc
    a=[]
    # join with dealerid
    for dealer in dealer_id:
        for v in acc:
            a.append(dealer+'_'+v)
    #change to syntax of sql query
    b=[]
    for v in a:
        v="'"+v+"'"
        b.append(v)
    gl_replace="("+",".join(b)+")"

    return gl_replace