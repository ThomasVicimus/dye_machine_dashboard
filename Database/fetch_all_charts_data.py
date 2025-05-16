from Database.database_connection import DatabaseConnection
import pandas as pd
import yaml
import logging
from Database.serialize_df import serialize_dataframe_dict

logger = logging.getLogger(__name__)

db = DatabaseConnection()


def get_all_charts_data(db) -> dict:
    """
    Get all charts data from the database.(unserialized dataframes// serializing in layout.py)
    """
    dfs = {
        "chart-1-data-store": get_MachineUsage_data(db),
        "chart-2-data-store": get_MachineStatus_data(db),
        "chart-3-data-store": get_MachineUsage_data(db),
    }
    # No serialization here, done inside get_MachineUsage_data
    return dfs


def get_MachineUsage_data(db) -> pd.DataFrame:
    """
    Get machine usage data from the database.

    Returns:
        pd.DataFrame: DataFrame containing machine usage data
    """

    dfs = {}
    # load chart 1 sql
    chartname = "machine_usage"
    file = f"1_{chartname}.sql"
    file_name = file.split(".")[0]
    # load replace yml using unicodedecode
    with open(f"sql/{file_name}_replace.yml", "r", encoding="utf-8") as f:
        replace_dict = yaml.safe_load(f)
    # replace period_replace in sql file
    with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
        sql_commands = sql_file.read()
    # for period in replace_dict["period_replace"]:
    #     Q = sql_commands.format(period_replace=period)
    #     dfs_machine_usage[period] = db.execute_query(Q)

    # Process each period
    for period in replace_dict["period_replace"]:
        Q = sql_commands.format(period_replace=period)
        df = db.execute_query(Q)

        # Log the raw data for debugging
        logger.debug(f"Raw data for period {period}:")
        logger.debug(df.to_string())

        # Get average, best, and worst machine data
        if not 0 in df["order_index"].unique():
            avg = get_avg_chart1(df)
            # print(f"avg: {avg}")
        else:
            avg = df[df["order_index"] == 0]

        best = (
            df[df["order_index"] == 1].sort_values(by="run", ascending=False).iloc[0:1]
        )
        worst = (
            df[df["order_index"] == 1].sort_values(by="run", ascending=True).iloc[0:1]
        )
        all_machine = df[df["order_index"] == 1].sort_values(by="run", ascending=True)
        dfs[period] = {
            "avg": avg,
            "best": best,
            "worst": worst,
            "all_machine": all_machine,
        }

    return dfs


def get_avg_chart1(df):
    # * calculate the average of each cols in the df in form of df
    mask = df["order_index"] == 1
    _df = df[mask]
    df_avg = pd.DataFrame(
        columns=["run", "idle", "down", "repair", "period", "machine_name"]
    )
    df_avg.loc[0, "run"] = _df["run"].mean()
    df_avg.loc[0, "idle"] = _df["idle"].mean()
    df_avg.loc[0, "down"] = _df["down"].mean()
    df_avg.loc[0, "repair"] = _df["repair"].mean()
    df_avg.loc[0, "period"] = df["period"].iloc[0]
    df_avg.loc[0, "machine_name"] = pd.NA
    return df_avg


def get_MachineStatus_data(db, lang: str = "zh_cn") -> pd.DataFrame:
    """
    Get machine usage data from the database.

    Returns:
        pd.DataFrame: DataFrame containing machine usage data
    """
    col_rename = {
        "zh_hant": {
            "machine_name": "機號",
            "state": "狀態",
            "user_prompt": "叫人",
            "num_of_alarms": "警報",
            "mt_temperature": "溫度C",
            "batch_no": "批次號",
            "program_name": "程序名",
            "current_step": "當前步驟",
            "next_step": "下一步",
            "minutes_run": "運行(分鐘)",
            "expected_finish_time": "預計完成時間",
            "steps": "步驟",
        },
        "zh_cn": {
            "machine_name": "机号",
            "state": "状态",
            "user_prompt": "叫人",
            "num_of_alarms": "警报",
            "mt_temperature": "温度C",
            "batch_no": "批次号",
            "program_name": "程序名",
            "current_step": "当前步骤",
            "next_step": "下一步",
            "minutes_run": "运行(分钟)",
            "expected_finish_time": "预计完成时间",
            "steps": "步骤",
        },
        "en": {
            "pass": "pass",
        },
    }
    dfs = {}
    # load chart 1 sql
    chartname = "machine_status"
    # * Desktop version
    file = f"2_{chartname}_desktop.sql"
    # replace period_replace in sql file
    with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
        Q = sql_file.read()

    df = db.execute_query(Q)
    dfs["desktop"] = {"all_machine": df}

    # * Mobile version
    file = f"2_{chartname}_mobile.sql"
    # replace period_replace in sql file
    with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
        Q = sql_file.read()

    df_mobile = db.execute_query(Q)
    for col in [
        "total_steps_cnt",
        "current_step_cnt",
    ]:
        df_mobile[col] = df_mobile[col].astype(str)
    df_mobile["steps"] = (
        df_mobile["total_steps_cnt"] + "/" + df_mobile["current_step_cnt"]
    )
    cols = [
        "machine_name",
        "state",
        "batch_no",
        "steps",
        # "expected_finish_time",
    ]
    dfs["mobile"] = {"all_machine": df_mobile[cols]}

    for mobile_option, df_dict in dfs.items():
        for key, df in df_dict.items():
            df = df.rename(columns=col_rename[lang])
            dfs[mobile_option][key] = df

    return dfs
