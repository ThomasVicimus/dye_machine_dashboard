"""
Simple Mapping :
clf_config['enable_Type_col'] indict the col to act as index 
map = {enable_col_mapping : Category}
"""

import pandas as pd
from .clf_func import *
from dateutil.relativedelta import relativedelta
import sys
from .log_func import *


def simple_map(
    clf_config: dict,
    col_dfs: dict,
    train_excels: dict,
    output_paths: dict,
    excel_paths: dict,
    test_data_dict: dict,
    json_output: dict,
):
    try:
        print(">>>>>Classification : Simple Mapping Starts.")

        ###* clean train // remove data older than 2years
        train_df = merge_train(excel_paths, train_excels, clf_config["data_sheetname"])
        two_years_ago = datetime(
            (datetime.today() + relativedelta(years=-1)).year, 1, 1
        )
        train_df["Post Date"] = pd.to_datetime(train_df["Post Date"])
        train_df = train_df.loc[train_df["Post Date"] >= two_years_ago]

        ###* simple mapping // get Category Mapping against provided col
        cate_map, info = get_cate_map(
            train_df, clf_config["clf_option"], clf_config["enable_col_mapping"]
        )
        if info:
            info = info.replace("__acc_replace", clf_config["acc_name_short"])
            json_output["LOG"].append(info)

        # * Type_col
        if clf_config["enable_Type_col"]:
            cate_type_map = train_df.set_index(["Category"])["Type"].to_dict()

        dfs = {}
        for store in output_paths.keys():
            test_data_csv = test_data_dict[store]
            df = pd.read_csv(excel_paths[test_data_csv])

            if clf_config["enable_find_dept"]:
                df.Department = df.Department.fillna(
                    find_dept(df["Account Number"], df.Department)
                )

            df = fix_col_by_coltbl(df, col_dfs, "ExtractedData_to_CLF")
            df["store"] = store
            df["Post Date"] = pd.to_datetime(df["Post Date"]).dt.strftime("%Y-%m-%d")

            # * CLF
            df[clf_config["enable_col_mapping"]] = df[
                clf_config["enable_col_mapping"]
            ].apply(int_to_str)

            df["Category"] = df[clf_config["enable_col_mapping"]].map(cate_map)

            if clf_config["enable_Type_col"]:
                df["Type"] = Type_col_mapping(
                    df["Type"],
                    df["Category"],
                    cate_type_map,
                    clf_config["default_Type_value"],
                )
            else:
                df["Type"] = np.nan

            # * Return Result
            dfs[store] = df

        return dfs, json_output

    except Exception:
        e = get_error_info()

        info = f"FATAL: {clf_config['acc_name_short']}\n{e}"
        json_output["LOG"].append(info)
        return json_output
