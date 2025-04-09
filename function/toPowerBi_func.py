from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import re
import os
from .short_utilities import *
from .log_func import *
import sys


def get_sharepoint_date_folder(YYMMDD: str):
    datetime_list = list(map(int, YYMMDD.split("-")))
    date = datetime(*datetime_list)
    year = date.year + 2000
    date_folder = str(year)
    # if year == datetime.today().year:
    #     date_folder='Current'
    # else:
    #     date_folder=str(year)
    return date_folder


def get_mod_date(target_yearmonth):
    """
    get max Modifited Date (%Y%m) the source_data should have
    """
    target_year = target_yearmonth.year
    target_month = target_yearmonth.month
    TM = datetime.now()
    if (target_year == TM.year) and (target_month == TM.month):
        check_date = (TM + relativedelta(days=-1)).date()
    else:
        # year=target_yearmonth.year
        # month=target_yearmonth.month
        max_day = calendar.monthrange(target_year, target_month)[1]
        check_date = datetime(target_year, target_month, max_day).date()
    return check_date


def check_white_space(value):
    if re.search(f"\s+$", value):
        return True
    else:
        return False


def select_file_by_yearmonth(extension=False, search_by=False, dir=os.getcwd()):
    # Get list of files
    if extension:
        files = [file for file in os.listdir(dir) if file.endswith(extension)]
    else:
        files = os.listdir(dir)

    # Filter files by search term if provided
    if search_by:
        files = [file for file in files if re.search(search_by, file)]

    # Function to extract datetime from filename
    def extract_datetime(filename):
        match = re.search(r"(\d{4})(\d{2})", filename)
        if match:
            year, month = match.groups()
            return datetime(int(year), int(month), 1)  # Day is set to 1
        return datetime.min  # Return minimum datetime if no match found

    # Sort files by extracted datetime, in descending order
    sorted_files = sorted(files, key=extract_datetime, reverse=True)

    # Return the file with the maximum datetime (first in sorted list)
    if sorted_files:
        return sorted_files[0]
    else:
        return None  # Return None if no files found


def transform_to_powerbi(
    df: pd.DataFrame,
    target_yearmonth_dt: datetime,
    client: str,
    mainstore: str,
    github_path: str,
    col_dfs: pd.DataFrame,
    json_output: dict,
):
    try:
        # * Select Data by Date
        year = target_yearmonth_dt.year
        month = target_yearmonth_dt.month
        output_ymd = target_yearmonth_dt.strftime("%y-%m-01")

        mask = (df["Accounting Date"].dt.year == int(year)) & (
            df["Accounting Date"].dt.month == int(month)
        )
        df_yearmonth = df.loc[mask].copy()

        # * split Category
        df_yearmonth["Predicted Class"] = df_yearmonth["Predicted Group"].apply(
            lambda x: x.split(" - ")[-1]
        )
        source_cate_cnt = df_yearmonth["Predicted Class"].count()
        df_yearmonth["Predicted Group"] = df_yearmonth["Predicted Group"].apply(
            lambda x: x.split(" - ")[0]
        )

        class_map = df_yearmonth.set_index("uid")["Predicted Class"].to_dict()
        group_map = df_yearmonth.set_index("uid")["Predicted Group"].to_dict()

        # * Load United Format GL in local
        ref_csv = f"{mainstore} {output_ymd}.csv"
        ref_filepath = os.path.join(
            github_path, f"output/{client}/GL-data/{mainstore}", ref_csv
        )
        if not os.path.exists(ref_filepath):
            merge = None
            export_path = None
            info = f"ERROR: GL data not exist: [{mainstore}] [{ref_filepath}]"
            json_output["LOG"].append(info)

            return merge, export_path, json_output

        ref_df = pd.read_csv(ref_filepath)
        ref_df["Accounting Date"] = pd.to_datetime(ref_df["Accounting Date"])
        # * filter by date
        mask = (ref_df["Accounting Date"].dt.year == int(year)) & (
            ref_df["Accounting Date"].dt.month == int(month)
        )
        ref_df = ref_df.loc[mask]

        # * Map Predictions
        merge = ref_df.copy()
        merge["Predicted Class"] = merge["uid"].map(class_map)
        merge["Predicted Group"] = merge["uid"].map(group_map)
        des_cate_cnt = merge["Predicted Class"].count()

        if source_cate_cnt != des_cate_cnt:
            # * save store-yearmonth as trigger, to trigger CLF next time
            trigger_filepath = f'raw_data/GL/_skip_folder/trigger/{mainstore}-{target_yearmonth_dt.strftime("%Y%m")}.txt'
            # makedir_for_file(trigger_filepath)
            with open(trigger_filepath, "w") as f:
                f.write(f"{target_yearmonth_dt.strftime('%Y%m')}")

            info = f"ERROR: Cate Count Error - [{mainstore}-{target_yearmonth_dt.strftime('%Y%m')}]\n source_cate_cnt != des_cate_cnt\n"
            if source_cate_cnt > des_cate_cnt:
                missing_uid = [id for id in class_map.keys() if id not in merge["uid"]]
                if len(missing_uid) < 20:
                    info = info + f"\n{missing_uid=}"

            json_output["LOG"].append(info)

        # merge['Source']=merge['Source'].apply(int_to_str)
        # merge['Source Name']=merge['Source'].replace(source_map_dms)
        # merge['Source Name']=merge['Source'].replace(source_map_common)

        # * export
        export_csv_name = f"{mainstore} {output_ymd}.csv"

        merge = fix_col_by_coltbl(merge, col_dfs, "export_PowerBi")
        merge = get_colseq(merge, col_dfs, "PowerBi_colseq")

        merge["Accounting Date"] = pd.to_datetime(merge["Accounting Date"]).dt.strftime(
            "%Y-%m-%d"
        )

        # *export to temp_files
        export_path = os.path.join(f"Predicted_GL/{mainstore}", export_csv_name)
        makedir_for_file(export_path)
        merge.to_csv(export_path, index=False)
        json_output["LOG"].append(f"TRACE: {export_path}")

    except Exception:
        e = get_error_info()
        info = f"FATAL: {mainstore=} // {target_yearmonth_dt.strftime('%Y%m')=}\n{e}"
        json_output["LOG"].append(info)
        return None, None, json_output

    return merge, export_path, json_output


def check_amt_error(
    merge: pd.DataFrame,
    mainstore: str,
    target_yearmonth_dt: datetime,
    json_output: dict,
):
    ### check amt
    merge_accounts = merge.loc[
        ~merge["Account Type"].isin(["COUNT ACCOUNT", "COUNT ACCOUNTS"])
    ]
    amt = merge_accounts.Amount.sum()
    if abs(amt) > 1:
        info = f"ERROR: to PBI - {mainstore}-{target_yearmonth_dt.strftime('%Y%m')=} Amount Balanace Large than 1(NOT Balance)"
        json_output["LOG"].append(info)
    return json_output
