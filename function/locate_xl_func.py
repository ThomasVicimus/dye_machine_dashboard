import os


def locate_test_data(
    assigned_yearmonth, assigned_store, clf_config, RAWDATA_PATH, excel_paths
):
    _rawdata_path = os.path.join(
        RAWDATA_PATH,
        clf_config["acc_name_short"],
        f"{clf_config['acc_name_short']}-Data-{assigned_yearmonth}",
    )
    files = [file for file in os.listdir(_rawdata_path) if file.endswith(".csv")]

    new_excel_paths = {file: os.path.join(_rawdata_path, file) for file in files}
    excel_paths.update(new_excel_paths)

    test_data_dict = {
        store: next((file for file in files if file.startswith(store)), None)
        for store in assigned_store
    }
    test_store_without_data = [
        store for store, file in test_data_dict.items() if file is None
    ]

    if len(test_store_without_data) > 0:
        for store in test_store_without_data:
            test_data_dict.pop(store)
    return test_data_dict, test_store_without_data, excel_paths
