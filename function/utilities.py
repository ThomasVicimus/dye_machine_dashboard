import os
import shutil
import re
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import threading
# import calendar
import yaml
# import pythoncom
import win32com.client
import json
import zipfile

def add_mod_time_suffix(filepath):
    modified_time=datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y%m%d %H%M%S')
    dir=os.path.dirname(filepath)
    filename=os.path.basename(filepath)
    ext=filename.split('.')[-1]
    name=filename.split('.')[0]
    newname=name + '-' +modified_time + '.' +ext
    return os.path.join(dir,newname)

def backup(folder_prefix):
    #v1.0
    #define var
    target_folders=[]
    backup_cnt = 0
    skip_backup_cnt=0
    ignore_cnt = 0
    
    PATH=os.getcwd()
    PATH=PATH+'/raw_data/'
    folders= os.listdir(PATH)
    for folder in folders:
        if folder.startswith(folder_prefix):
            target_folders.append(folder)
    for folder in target_folders:
        files=os.listdir(PATH+folder)
        if 'pythonignore' not in files:
                if 'backup' not in files :
                    backup_cnt=backup_cnt+ 1
                    print(backup_cnt,' folder backuping')
                    os.mkdir(PATH+folder+'/backup/')
                    for file in files:
                        if not file.startswith('~$'):
                        #backup
                            shutil.copyfile(PATH+folder+'/'+file, PATH+folder+'/backup/'+file)
                    print(backup_cnt,'folder saved')
                else:
                    skip_backup_cnt=skip_backup_cnt+1
                    print(skip_backup_cnt,' folder skipped')
        else:
            ignore_cnt=ignore_cnt+1
            print(ignore_cnt,' folder ignored')
            
    print('back up process finished')

def locate_excel(path,excel_path,delimiter='-'):
    #v1.2
    excels=[]
    stores=[]
    # global excel_path

    for file in os.listdir(path):
        if not file.startswith('~$'):
            if file.endswith('.xlsx'):
                excels.append(file)
                names=file.split(delimiter)
                stores.append(names[0])
                excel_path[file]=(path+'/'+file)
    stores=np.unique(stores)
    return excels,excel_path,stores,names

# def locate_folders(folder_prefix,keyword='',upper_layer=False):
#     #v2.0 20230622 locate in upper layer
#     folders=[]
#     PATHs=[]
#     # path=os.getcwd()
#     rawdata_path='/raw_data/'
#     if upper_layer:
#         rawdata_path='../raw_data/'
#     for folder in os.listdir(rawdata_path+folder_prefix):
#         if folder.startswith(keyword):
#             folders.append(folder)  
#             PATH=rawdata_path+folder_prefix+folder
#             PATHs.append(PATH)
    
#     return (folders,PATHs)

def locate_folders(folder_prefix,rawdata_path,keyword=''):
    #v2.0 20230622 locate in upper layer
    folders=[]
    PATHs=[]
    # path=os.getcwd()
    # rawdata_path='/raw_data/'
    # if upper_layer:
        # rawdata_path='../raw_data/'
    _path=os.path.join(rawdata_path,folder_prefix)
    for folder in os.listdir(_path):
        if folder.startswith(keyword):
            folders.append(folder)  
            PATH=os.path.join(_path,folder)
            PATHs.append(PATH)
    
    return (folders,PATHs)


def latest_month(folders,paths):
    #v1.0
    yearmonth=[]
    target={}
    for folder, path in zip(folders,paths):
        # v=int(re.findall(r'/d+',folder))
        v=int(re.findall(r'\d+',folder)[0])
        yearmonth.append(v)
        target[v]=path
    v=max(yearmonth)
    return target[v],v

def date_match(excel,position,folder_date):
    #v1.0
    xl_date=excel.split('-')[position]
    try:
        if int(xl_date)!=int(folder_date):
            print('\n\n-----WARNING: folder date:{}, excel date:{}, DO NOT MATCH!-----\n\n'.format(folder_date,xl_date))
    except Exception:
        print('\n\n-----WARNING: date_match do not function properly ------\n-----Classification Continue-----\n\n')

def select_month(folders,paths,yearmonth):
    #v1.0
    # yearmonth=[]
    target={}
    for folder, path in zip(folders,paths):
        if re.search(yearmonth,folder):
            v=folder
            target[v]=path
        # v=int(re.findall(r'/d+',folder))
        # v=int(re.findall(r'\d+',folder)[0])
        # yearmonth.append(v)
        # target[v]=path
    # v=max(yearmonth)
    folder_name=v
    return target[v],folder_name

def warn_txt(store,name,text,text_inside=False,OUTPUT_PATH='/output/'):
    #v1.1
    print("\n\n-----WARNING: {} in {}-----\n\n".format(text,store))
    with open(OUTPUT_PATH+'{}-{}.txt'.format(store,name), 'w') as f:
        if text_inside:
            f.write(text_inside)
        else:
            f.write('-----WARNING: {}-----'.format(text))
        
def renamer(path,file,name,keyword):
    #v1.2 20230608
    extension='.'+file.split('.')[1]
    for store in ['RHH','THH','RHT','LOL','TTL','WOK']:
        if re.search(store,file.upper()):
            store=store
            break
    if re.search(keyword.lower(),file.lower()):
        for yearmonth in ['\d{6}','\d{4}_\d{2}','\d{4}-\d{2}']:
            if re.search(yearmonth,file):
                yearmonth=re.findall(yearmonth,file)[0]
                yearmonth=yearmonth.replace('-','').replace('_','')
                break
    
        new_name=store+'-'+name+'-'+yearmonth+extension
        os.rename(path+file,path+new_name)
    # print(new_name)
  
def keyin_argv_store(argv):
    argv=argv.upper()
    option={'THH':['THH'],
            'RHH':['RHH'],
            'RHT':['RHT'],
            'TTL':['TTL'],
            'LOL':['LOL'],
            'WOK':['WOK'],
            'CORR':['corr'],
            'HY':['THH','RHH'],
            'TY':['RHT'],
            'TORONTO':['RHH','RHT','THH'],
            'LONDON':['TTL','LOL','WOK'],
            'TOR':['RHH','RHT','THH'],
            'LON':['TTL','LOL','WOK']
            }
    
    keywords=option[argv.upper()]
    if argv in option.keys():
        assigned_store=option[argv]
    else:
        while True:
            argv=input('wrong arguement. Please enter store Code.\n').upper()
            if argv in ['Q','QUIT']:
                quit()
            elif argv in option.keys():
                assigned_store=option[argv]
                break
    return assigned_store

def keyin_argv_yearmonth(argv):
    if re.search(r'\d{6}',argv):
        assigned_yearmonth=argv
    else:
        while True:
            option=input('wrong arguement. Please enter YearMonth ie: 202301\n').upper()
            if option in ['Q','QUIT']:
                quit()
            elif re.search(r'\d{6}',option):
                assigned_yearmonth=option
                break
    return assigned_yearmonth

def keyin_argv(argv):
    # REC version 20231010
    assigned_store=False
    assigned_yearmonth=False
    argv_yearmonth=False
    # with time
    argv=argv.upper()
    if re.search('-',argv):
        argv_split=argv.split('-')
        if len(argv_split)==2:
            argv=argv_split[0]
            argv_yearmonth=argv_split[1]
    if argv.upper() in ['RHH','THH','RHT']:
        assigned_store=[argv]
        assigned_yearmonth=False
    elif re.search(r'\d{6}',argv):
        assigned_yearmonth=argv      
        assigned_store=False
    else:
        while True:
            argv=input('wrong arguement. Please enter StoreCode OR YeaMonth OR StoreCode-YearMonth.\n').upper()
            argv_split=argv.split('-')

            if len(argv_split)==2:
                argv=argv_split[0]
                argv_yearmonth=argv_split[1]

            if argv in ['Q','QUIT']:
                quit()
            elif argv.upper() in ['RHH','THH','RHT']:
                assigned_store=[argv]
                assigned_yearmonth=False
                break
            elif re.search(r'\d{6}',argv):
                assigned_yearmonth=[argv]        
                assigned_store=False
                break
    if argv_yearmonth:
        while True:
            if re.search(r'\d{6}',argv_yearmonth):
                assigned_yearmonth=[argv_yearmonth]
                break
            else:
                argv_yearmonth=input('wrong arguement for YearMonth. Please re-enter YearMonth.\n')
                # assigned_yearmonth=argv

    return assigned_store,assigned_yearmonth

def inputv2(text='',task={'y':True,'n':False}):
    while True:
        option=input(text).lower()
        if option in task.keys():
            break
        else:
            print('Invalid option. Please Re-Enter.')
    return task[option]

def concat_df_indict(_dict,n=0):
    # v1.0
    cnt=0
    for key in _dict.keys():
        if cnt==0:
            df=_dict[key]
            cnt=cnt+1
        else:
            df2=_dict[key]
            df=pd.concat([df,df2],axis=n)
    return df

def xloc(df,col,v):
    return df.loc[df[col]==v]

def Xloc_reverse(df,col,v):
    return df.loc[df[col]!=v]

def castdate(df, col, just_date=True):
    # Convert column to int64 to handle timestamps correctly
    series = df[col].astype('int64')
    
    # Use vectorized operation to convert timestamps to dates
    series = series.map(lambda x: datetime.fromtimestamp(x/1000) if isinstance(x, int) else 'str error', na_action='ignore')

    if just_date:
        return series.dt.date
    else:
        return series
    
def create_if_not_exist(folder, path):

    if not os.path.exists(path+folder):
        os.makedirs(path+folder)

class InputTimeoutError(Exception):
    pass

def input_with_timeout(prompt, default_value, timeout=5):
    print(prompt, end='')
    sys.stdout.flush()

    # Create an event to signal input received
    input_event = threading.Event()

    # Define a function to be called on timeout
    def timeout_handler():
        input_event.set()

    # Start the timer thread
    timer_thread = threading.Timer(timeout, timeout_handler)

    timer_thread.start()
    # Read input in a separate thread
    input_text = None

    def input_thread_func():
        nonlocal input_text
        input_text = sys.stdin.readline().strip()
        input_event.set()

    input_thread = threading.Thread(target=input_thread_func)
    input_thread.start()

    # Wait for input or timeout
    input_event.wait()

    # Cancel the timer thread
    timer_thread.cancel()

    if input_text:
        return input_text
    else:
        # If no input is received, return the default value
        print(f"\nNo input received. Using default value: {default_value}")
        return default_value

def select_yearmonth_folder_timeout(PATH):
    folders=os.listdir(PATH)
    folders.sort(reverse=True)

    # Usage example
    no = input_with_timeout("Select folder (in 5 sec):\n"+','.join(folders)+'\n', "0")
    return folders[int(no)]

def load_config(file_path='config.yml'):
    with open(file_path, "r") as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    return config

def select_file(extention=False,search_by=False,auto_select=False):
    files=os.listdir()
    if extention:
        _files=[]
        for file in files:
            if file.endswith(extention):
                if search_by:
                    if re.search(search_by,file):
                        _files.append(file)
                else:
                    _files.append(file)
        files=_files
    sorted_files=sorted(files,key=lambda x: os.path.getmtime(x),reverse=True)
    if auto_select:
        excel=sorted_files[0] 
    else:   
        selected_file=input('Select Analysis to be corrected:\n{}'.format(' , '.join(sorted_files))+'\n')
        excel=sorted_files[int(selected_file)]
    return excel
# def select_file(search_by=False,extention=False):
#     files=os.listdir()
#     _files=[]
#     if search_by:
#         option={'THH':['THH'],
#                 'RHH':['RHH'],
#                 'RHT':['RHT'],
#                 'CORR':['corr'],
#                 'HY':['THH','RHH'],
#                 'TY':['RHT']}
        
#         keywords=option[search_by.upper()]
#         for keyword in keywords:
#             _files=[]
#             for file in files:
#                 if re.search(keyword,file):
#                     _files.append(file)
            
#             files=_files

#             if extention:
#                 _files=[]
#                 for file in files:
#                     if file.endswith(extention):
#                         _files.append(file)
#                 files=_files


#             sorted_files=sorted(files,key=lambda x: os.path.getmtime(x),reverse=True)
#             selected_file=input('Select Analysis to be corrected:\n{}'.format(' , '.join(sorted_files))+'\n')
#             excel=sorted_files[int(selected_file)]
#             return excel
#     else:
#         if extention:
#             _files=[]
#             for file in files:
#                 if file.endswith(extention):
#                     _files.append(file)
#             files=_files
#         sorted_files=sorted(files,key=lambda x: os.path.getmtime(x),reverse=True)
#         selected_file=input('Select Analysis to be corrected:\n{}'.format(' , '.join(sorted_files))+'\n')
#         excel=sorted_files[int(selected_file)]
    
#     return excel

def archive_train_data(train_path):
    train_path=os.path.abspath(train_path)
    directory=os.path.join(os.path.dirname(train_path),'archive')
    filename=os.path.basename(train_path).split('.')[0]
    if not os.path.exists(directory):
        os.makedirs(directory)

    modified_time=datetime.fromtimestamp(os.path.getmtime(train_path)).strftime('%Y%m%d %H%M%S')
    filename=filename+'-'+modified_time+'.xlsx'
    shutil.copyfile(train_path,os.path.join(directory,filename))

def recover_from_archive(archive_path,des_path,yearmonth,stores=['THH','RHH','RHT','TTL','LOL','WOK']):
#archive_path='..\\{}\\function\\training_data\\archive'
# yearmonth=input('yearmonth:\n')
# des_path='..\\{}\\function\\training_data\\'
    files=os.listdir(archive_path)
    for store in stores:
        file_store=[]
        for file in files:
            if (re.search(store,file)) and re.search('-'+yearmonth+'-',file):
                file_store.append(file)
        
        sorted_files=sorted(file_store,reverse=True)
        des_filename=store+'-ans-{}.xlsx'.format(yearmonth)
    
        shutil.copyfile(archive_path+sorted_files[0],des_path+des_filename)

def int_to_str(x):
    try:
        return str(int(float(x)))
    except ValueError: 
        return x
    except TypeError:
        return x
    
def create_shortcut(excel_file_path, shortcut_dir):
    shortcut_dir=shortcut_dir.replace('/','\\')
    excel_file_path=os.path.abspath(excel_file_path)

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(os.path.join(shortcut_dir, os.path.basename(excel_file_path) + '.lnk'))
    shortcut.Targetpath = excel_file_path
    shortcut.save()

def setup_col_table(df,shtname):
    cols=df.columns
    new_cols=[]
    for col in cols:
        col=col.replace(' ','_').lower()
        new_cols.append(col)
    col_df=pd.DataFrame([new_cols],columns=list(cols))
    col_df.to_excel('Col_table.xlsx',index=False,sheet_name=shtname)
    
def get_df_from_coltbs(coltbl_path,file_path):
    filename=os.path.basename(file_path)
    if file_path.endswith('.xlsx'):
        df=pd.read_excel(filename)
    else:
        df=pd.read_csv(file_path)
    col_df=pd.read_excel(coltbl_path,sheet_name=filename)
    col_df=col_df.dropna(axis=1)
    for col in df.columns:
        if col not in col_df.columns:
            df.pop(col)
    df.columns=col_df.loc[0]
    return df

def load_col_dfs(coltbl_path):
    col_dfs={sht:pd.read_excel(coltbl_path, sheet_name=sht) for sht in get_excel_sheet_names(coltbl_path)}
    return col_dfs

def fix_col_by_coltbl(df , coltbl : str,sht_name:str):
    '''
    coltbl :str -> coltbl_path
    coltbl :dict -> dict contain all df_col in coltbl
    '''
    df=df.copy()

    if type(coltbl)==str:   
        col_df=pd.read_excel(coltbl,sheet_name=sht_name)
    elif type(coltbl)==dict:   
        col_df=coltbl[sht_name]

    col_df=col_df.dropna(axis=1,how='all')

    for col in df.columns:
        if not col in col_df.columns:
            df.pop(col)
    for n in range(1,len(col_df)):
        dup_col_df=pd.DataFrame([col_df.loc[n]])
        dup_col_df=dup_col_df.dropna(axis=1)
        for old_col,add_col in zip(dup_col_df.columns,dup_col_df.values[0]):
            df[add_col]=df[old_col]
        col_df=col_df.drop(index=n)
    rename_map=dict(zip(col_df.columns.to_list(),col_df.values[0]))
    df=df.rename(columns=rename_map)
    for col in rename_map.values():
        if not col in df.columns:
            df[col]=pd.NA
    return df

def get_colseq(df,coltbl : str,sht_name:str):
    if type(coltbl)==str:   
        colseq=pd.read_excel(coltbl,sheet_name=sht_name)
    elif type(coltbl)==dict:   
        colseq=coltbl[sht_name]
    cols=colseq.columns.to_list()
    df=df[cols].copy()
    return df
def fix_dtype_by_tbl(df,dtypetbl_path,sht_name):
    df=df.copy()
    df_dtype=pd.read_excel(dtypetbl_path,sheet_name=sht_name)
    df_dtype=df_dtype.dropna(axis=1)
    data={
        'cols':df_dtype.columns.to_list(),
        'dtypes':df_dtype.loc[0].values
    }
    df_dtype=pd.DataFrame(data)

    mask=df_dtype['dtypes'].isin(['str','int','float'])
    for col, d in zip(df_dtype.loc[mask,'cols'],df_dtype.loc[mask,'dtypes']):
        mask=df[col].isna()
        df.loc[~mask,col]=df.loc[~mask,col].astype(d)

    mask=df_dtype['dtypes']=='int_to_str'
    for col in df_dtype.loc[mask,'cols']:
        df[col]=df[col].apply(int_to_str)

    mask=df_dtype['dtypes']=='date'
    for col in df_dtype.loc[mask,'cols']:
        df[col]=pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
        
    mask=df_dtype['dtypes']=='time'
    for col in df_dtype.loc[mask,'cols']:
        df[col]=pd.to_datetime(df[col]).dt.strftime('%H:%M:%S')

    mask=df_dtype['dtypes']=='datetime'
    for col in df_dtype.loc[mask,'cols']:
        df[col]=pd.to_datetime(df[col])

    return df

def load_json_data(output):
    # Split the output into lines
    lines = output.split("\n")

    # Look for the line containing the JSON data and parse it
    json_data = None
    for line in lines:
        if line.strip():
            try:
                json_data = json.loads(line)
                break  # Stop searching when the JSON is found
            except json.JSONDecodeError:
                pass  # Ignore non-JSON lines
    return json_data

def writeORappend_error(error_txt_path,text):
    with open(error_txt_path, 'a+') as f:
        f.seek(0)
        line=f.read(100)
        if len(line)>0:
            f.write('\n')    
        f.write(text)

def get_excel_sheet_names(file_path):
    sheets = []
    with zipfile.ZipFile(file_path, 'r') as zip_ref: xml = zip_ref.read("xl/workbook.xml").decode("utf-8")
    for s_tag in  re.findall("<sheet [^>]*", xml) : sheets.append(  re.search('name="[^"]*', s_tag).group(0)[6:])
    return sheets

def parse_argv(argvs,func_list_when_True, otherwise_if_fasle):
    
    while len(argvs)<=(len(func_list_when_True)):
        argvs.append(False)
    if len(argvs)>len(func_list_when_True):
        ''' If provided argvs MORE than function_list, Return the apply Function on the Pasred_argvs + extra argv(Without changing anything) '''
        parsing_argv=argvs[1:len(func_list_when_True)+1]
        extra_argvs=argvs[len(func_list_when_True)+1:]
    else:
        parsing_argv=argvs[1:]
        extra_argvs=[]
    parsed_argv=[argvs[0]] # argvs[0] being the name of the script
    for n, argv in enumerate(parsing_argv):
        if argv:
            if func_list_when_True[n]:
                parsed_argv.append(func_list_when_True[n](argv))
            else:
                parsed_argv.append(argv)
        else:
            parsed_argv.append(otherwise_if_fasle[n])
    return parsed_argv+extra_argvs

def keyin_truefalse_argv(argv):
    task={'y':True,'n':False,'True':True,'False':False}
    return task[argv]