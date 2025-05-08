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
        "chart1-data-store": get_MachineUsage_data(db),
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
