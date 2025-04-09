from function.clf_func import *
from function.log_func import *


def load_yhat_to_xl(
    dfs: pd.core.frame.DataFrame,
    col_dfs: pd.core.frame.DataFrame,
    output_paths: dict,
    clf_config: dict,
    assigned_yearmonth: str,
    json_output: dict,
):
    try:
        for store in output_paths.keys():
            output_path = output_paths[store]
            df = dfs[store]
            if len(df) > 0:
                """Source: Source OG // Source #: Source No(Number Only)"""
                df_R = get_colseq(df, col_dfs, "df_R")

                # df_R=clean_source(df_R)

                df_L = get_colseq(df, col_dfs, "df_L")
                df_L["Post Date"] = pd.to_datetime(df_L["Post Date"])

                duplicate = check_duplicate(
                    output_path, df_L, clf_config["data_sheetname"]
                )

                if duplicate:

                    output_path = replace_data(
                        store,
                        df_L,
                        df_R,
                        output_paths,
                        assigned_yearmonth,
                        clf_config["data_sheetname"],
                    )
                else:
                    output_path = append_data_openpyxl(
                        store,
                        df_L,
                        df_R,
                        output_paths,
                        assigned_yearmonth,
                        clf_config["data_sheetname"],
                    )
                info = f"TRACE: {output_path}"
                json_output["LOG"].append(info)
        return json_output
    except Exception:
        e = get_error_info()

        info = f"FATAL: {clf_config['acc_name_short']}\n{e}"
        json_output["LOG"].append(info)
        return json_output
