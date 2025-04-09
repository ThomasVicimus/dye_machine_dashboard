# import pandas as pd
# import numpy as np
from .short_utilities import *
import calendar
from dateutil.relativedelta import relativedelta

#! Sync THIS FILE After Update


def combine_col(df: pd.DataFrame, base_col: str, extra_col: str):
    mask = pd.isna(df[extra_col])
    _df = df.loc[~mask].copy()
    if len(_df) == 0:
        # If all values in extra_col are NaN, return NaN series
        return pd.Series([np.nan] * len(df))

    _df[extra_col] = _df[extra_col].apply(int_to_str)
    try:
        _df[extra_col] = _df[extra_col].str.strip()
    except AttributeError:
        _df[extra_col] = _df[extra_col]
    text_col = _df[base_col] + "|" + _df[extra_col].str.strip()
    text_col = text_col.str.strip()

    # Create a series with NaN for rows where extra_col is NaN
    result = pd.Series(index=df.index)
    result.loc[~mask] = text_col
    result.loc[mask] = df.loc[mask, base_col]

    # Remove trailing separators and check if result equals base_col
    result = result.str.rstrip("|")
    base_mask = result == df[base_col]
    result[base_mask] = np.nan

    return result


def transform_data_by_dms(df, dms):
    _df = df.copy()
    _df["DMS"] = dms

    if dms == "Reynolds":
        # * ADD JNL Schedule
        _df["JNL Schedule"] = _df["Control No"]
        # * Fix RO Number
        mask = _df["Source Name"] == "Repair Order Sales"
        ro_no = _df.loc[mask, "Reference No"].apply(
            lambda x: re.search(r"\d{4,}", x).group()
        )
        _df["RO Number"] = _df["RO Number"].fillna(ro_no)
        # * add Stock No
        _df["Stock No"] = pd.NA
        mask = _df["Account Type"].isin(["ASSETS", "LIABILITIES", "NET WORTH"])
        _df.loc[mask, "Stock No"] = _df["Control No"]
        _df.loc[~mask, "Stock No"] = _df["Reference No"]

    elif dms == "Tekion":
        # * Add JNL Schedule
        _df["JNL Schedule"] = _df["Vendor No"]

        # * Insert a merged column 'AccID1' by combining 'AccID' with '@'
        sales_data = _df[_df["Account Type"] == "SALE"].copy()
        sales_data["AccID"] = sales_data["AccID"].apply(int_to_str) + "@"
        _df = pd.concat([_df, sales_data], axis=0)

    return _df


# def create_store_transaction(df):

#     # mask = df["dms"] == "Tekion"
#     _df = df.copy()
#     stores = _df.dealer.unique()
#     dfs_stores = {}
#     for store in stores:
#         df_store = _df[_df["dealer"] == store].copy()
#         df_store = df_store[
#             [
#                 "Dealership",
#                 "Account No",
#                 "Account Name",
#                 "Source Name",
#                 "Reference No",
#                 "Accounting Date",
#                 "Amount",
#                 "Vendor No",
#                 "Vendor Name",
#                 "Control No",
#                 "Description",
#                 "Count",
#             ]
#         ]
#         # * fix col values
#         df_store["Account No"] = df_store["Account No"].apply(int_to_str)
#         df_store["Dealership"] = df_store["Dealership"].apply(int_to_str) + "|"
#         # * fix col names
#         df_store.columns = [
#             "BranchID",
#             "Acc No",
#             "Acc Name",
#             "JNL Type",
#             "JNL Reference",
#             "JNL Date",
#             "Amount",
#             "Control 2",
#             "Control Description",
#             "Control",
#             "JNL Description",
#             "Count",
#         ]
#         # * store in dict
#         dfs_stores[store] = df_store
#     return dfs_stores


def map_monthlike_values(series):
    month_mapping = {}

    for month in range(1, 13):
        month_str = str(month).zfill(2)  # Zero-pad the month number
        month_abbr = calendar.month_abbr[month]
        month_mapping[f"01-{month_abbr}"] = f"{month_str}/01"

    series.replace(month_mapping, inplace=True)
    return series


def clean_branch_get_dealer(branch_series):
    branch_series = branch_series.apply(int_to_str)
    branch_series = branch_series.replace(
        {
            "01-Jan": "01/01",
            "01-Mar": "03/01",
            "02-Jan": "01/02",
            "1126": "07/01",
            "1226": "04/01",
        }
    )

    # Replacing values in 'Dealer' column
    dealer_series = branch_series.replace(
        {"01/01": "TTL", "01/02": "LOL", "03/01": "RHT", "04/01": "RHH", "07/01": "THH"}
    )
    # Reverting one replacement in 'Branch'
    branch_series = branch_series.replace({"01/02": "01/01"})
    return branch_series, dealer_series


def archive_N_months_old_data(current_df, n_months=11, date_col="RO Date"):
    months_ago = datetime.today() - relativedelta(months=n_months)
    date_filter = datetime(months_ago.year, months_ago.month, 1)
    rodate_datetime = pd.to_datetime(current_df[date_col])
    archive_df = current_df.loc[rodate_datetime < date_filter]
    _current_df = current_df.loc[rodate_datetime >= date_filter]

    if len(archive_df) > 0:
        # archive_df = pd.concat([history_df,archive_df],axis=0)
        return _current_df, archive_df
    else:
        return _current_df, None


#! Sync THIS FILE After Update
