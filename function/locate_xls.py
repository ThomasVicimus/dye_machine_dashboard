"""
handle skip / force_start
locate training xl
locate testing data
copy ans to OUTPUT_PATH
get OUTPUT_PATH
"""

from function.short_utilities import *
import shutil

from function.clf_func import *
from function.save_option import *
from function.script_schedule import *
from function.locate_xl_func import *
from function.log_func import *


def locate_xls(
    min_store: dict.keys,
    assigned_yearmonth: str,
    clf_config: dict,
    assigned_store: list,
    OUTPUT_PATH: str,
    RAWDATA_PATH: str,
    json_output: dict,
):
    try:
        train_excels, excel_paths = locate_train(min_store)
        test_data_dict, test_store_without_data, excel_paths = locate_test_data(
            assigned_yearmonth, assigned_store, clf_config, RAWDATA_PATH, excel_paths
        )
        # * excel_paths should contain paths for train_excels and test_data_csvs
        if len(test_store_without_data) > 0:
            info = f'FATAL: locate_xl - no TEST data for assigned_store {test_store_without_data} in {clf_config["acc_name_short"]}/n Scripts Continues'
            json_output["LOG"].append(info)

        output_paths = {}
        for store in test_data_dict.keys():

            output_filename = (
                f"{store}-{clf_config['acc_name_full']}-{assigned_yearmonth}.xlsx"
            )
            output_path = os.path.join(OUTPUT_PATH, output_filename)

            output_path = save_as_new(output_path)
            output_paths[store] = output_path

            shutil.copyfile(excel_paths[train_excels[store]], output_paths[store])

        return output_paths, train_excels, test_data_dict, excel_paths, json_output
    except Exception:
        e = get_error_info()

        info = f"FATAL: {min_store=}\n{e}"
        json_output["LOG"].append(info)
        return json_output
