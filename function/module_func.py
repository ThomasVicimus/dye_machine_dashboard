from .short_utilities import *

def get_stores_to_run(yearmonth):
    path=f'raw_data/GL/_skip_folder/{yearmonth}.csv'
    if not os.path.exists(path):
        return False
    else:
        df=pd.read_csv(path)
        df=df.dropna(subset=['stores_to_run'],axis=0)
        if len(df)>0:
            df.stores_to_run=df.stores_to_run.str.split(';')
            stores_to_run=df.set_index('Account')['stores_to_run'].to_dict()
            return stores_to_run
        else:
            return False


def ipy_argv():
    task={'yy':[True,True],'yn':[True,False],'ny':[False,True],'n':[False,False]}
    text='Input argv for Store-YearMonth: yy/yn/ny/n'
    option=inputv2(text,task)
    if option[0]:
        assigned_store=keyin_argv_store(input('Input Store'))
    else:
        assigned_store=False

    if option[1]:
        assigned_yearmonth=keyin_argv_yearmonth(input('Input YearMonth'))
    else:
        assigned_yearmonth=datetime.now().strftime('%Y%m')
    #no skipping
    force_start=True
    return assigned_store,assigned_yearmonth,force_start
