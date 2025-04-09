import sys
import datetime
import os
import re

# def get_output(store,xl,excel_path,yearmonth_train,name_test,test_stores):

#     if store in test_stores:
#         # input_path=excel_path[xl]
#         suffix=str(yearmonth_train)+'.xlsx'
#         name=excel_path[xl].removesuffix(suffix)+name_test[2]
#         name=name.split('/')[-1]
#         output_path=os.getcwd()+'/output/'+name

#     return output_path


def append_datetime(output_path):
    # v1.0
    extention = output_path.rsplit(".", 1)[-1]
    name = output_path.rsplit(".", 1)[0]
    cnt = 1
    now = datetime.datetime.now()
    PATH = f"{name}-D{now:%d}_V{cnt}.{extention}"
    return PATH


def append_version(output_path):
    extention = output_path.rsplit(".", 1)[-1]
    name = output_path.rsplit(".", 1)[0]
    now = datetime.datetime.now()
    if re.search(f"-D{now:%d_V}", name):
        cnt = int(name.split(f"-D{now:%d_V}")[-1])
        name = name.split(f"-D{now:%d_V}")[0]
        cnt = cnt + 1
        PATH = f"{name}-D{now:%d}_V{cnt}.{extention}"
    return PATH


def option_2(output_path):
    # if option=='2':
    # print()
    confirm = input("\n---OVERWRITE Please Confirm(y/n)---")
    if confirm.lower() == "y":
        return output_path
    else:
        return False


def save_as_new(output_path):
    if os.path.exists(output_path):
        output_path = append_datetime(output_path)

        while os.path.exists(output_path):
            output_path = append_version(output_path)
    else:
        pass
    return output_path


# def save_option(output_path,always_save_as_new):

#     # if os.path.isfile(output_path):
#     if always_save_as_new:
#         result=option_3(output_path)
#     else:
#         while True:
#             option=input('     [%s]       already exist. \n\nPlease select:\n1.skip / 2.overwrite / 3.Save As New File\n\n'
#                 %output_path.split('/')[-1])
#             run={'1':False,
#                 # 'skip':False,
#                 '2':option_2(output_path),
#                 #  'overwrite':option_2(output_path,option),
#                 '3':option_3(output_path)}
#                 #  'save as new':option_3(output_path)}
#             if option in run.keys():
#                 result=run[option]
#                 break
#             else:
#                 print('Invalid option. Please enter 1 OR 2 OR 3')

#         result=run[option]


#     return result
