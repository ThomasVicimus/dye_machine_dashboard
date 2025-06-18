import numpy as np
from Database.database_connection import DatabaseConnection
import pandas as pd
import yaml
import logging
from Database.serialize_df import serialize_dataframe_dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

db = DatabaseConnection()


def get_all_charts_data(db) -> dict:
    """
    Get all charts data from the database.(unserialized dataframes// serializing in layout.py)
    """
    dfs = {
        "chart-1-data-store": get_MachineUsage_data(db),
        "chart-2-data-store": get_MachineStatus_data(db),
        "chart-3-data-store": get_chart3_data(db),
        "chart-4-data-store": get_chart4_data(db),
        "chart-5-data-store": get_chart5_data(db),
        "chart-6-data-store": get_chart6_data(db),
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
        for key, df_val in df_dict.items():
            df_val = df_val.rename(columns=col_rename[lang])
            dfs[mobile_option][key] = df_val

    return dfs


def get_chart3_data(db) -> dict:
    """
    Get machine production data from the database for chart 3.
    Data is processed to include all dates in the 7-day and 30-day periods
    ending on the latest available date, with missing 'weight_kg' filled with 0.
    """
    sql_file_path = "sql/3_machine_production.sql"
    with open(sql_file_path, "r", encoding="utf-8") as f:
        Q = f.read()

    df = db.execute_query(Q)
    unique_machine_names = df["machine_name"].unique()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df.date.isna().sum() > 0:
        logger.warning("Chart 3: Some dates were not converted to datetime.")
        df.dropna(
            subset=["date"], inplace=True
        )  # Remove rows where date conversion failed

    latest_date = df["date"].max()

    # Define date ranges
    start_date_30days = latest_date - pd.Timedelta(days=29)
    all_dates_30days_index = pd.date_range(
        start=start_date_30days, end=latest_date, freq="D", name="date"
    )

    df_for_reindex = df.set_index("date")

    # Prepare for reindexing by setting index
    # Drop rows where date or machine_name became NaN after initial processing, if any, before setting index
    df.dropna(subset=["date", "machine_name"], inplace=True)
    if df.empty:
        return _create_empty_chart3_data()

    # Handle potential duplicate (date, machine_name) pairs by summing weight_kg.
    # This ensures set_index doesn't fail on duplicates.
    df = df.groupby(["date", "machine_name"], as_index=False)["weight_kg"].sum()

    df_indexed = df.set_index(["date", "machine_name"])

    # Create the complete multi-index for all dates and all unique machines
    multi_idx = pd.MultiIndex.from_product(
        [all_dates_30days_index, unique_machine_names], names=["date", "machine_name"]
    )

    # Reindex to ensure all date-machine combinations exist, fill missing weights with random number
    df_30days = df_indexed["weight_kg"].reindex(
        # multi_idx, fill_value=np.random.randint(20, 200)
        multi_idx,
        fill_value=0,
    )
    df_30days = df_30days.reset_index()  # 'date' and 'machine_name' become columns

    # Add 'mmdd' column using user's specified format
    df_30days["mmdd"] = df_30days["date"].dt.strftime("%m/%d")

    # Ensure correct column order
    df_30days_processed = df_30days[["date", "machine_name", "mmdd", "weight_kg"]]

    # Extract 7-day data from the processed 30-day data
    start_date_7days = latest_date - pd.Timedelta(days=6)
    df_7days_processed = df_30days_processed[
        df_30days_processed["date"] >= start_date_7days
    ].copy()

    return {
        "今天": {"all_machine": df_7days_processed.copy()},
        "本周": {"all_machine": df_7days_processed.copy()},
        "本月": {"all_machine": df_30days_processed.copy()},
    }


def _create_empty_chart3_data() -> dict:
    """Helper function to create the default empty data structure for chart 3."""
    empty_df = pd.DataFrame(columns=["date", "machine_name", "mmdd", "weight_kg"])
    logger.error("Chart 3: Empty data in use.")
    return {
        "今天": {"all_machine": empty_df.copy()},
        "本周": {"all_machine": empty_df.copy()},
        "本月": {"all_machine": empty_df.copy()},
    }


def get_chart4_data(db) -> pd.DataFrame:
    """
    Get machine usage data from the database.

    Returns:
        pd.DataFrame: DataFrame containing machine usage data
    """

    dfs = {}
    # load chart 1 sql
    chartname = "4_machine_waste"
    file = f"{chartname}.sql"
    file_name = file.split(".")[0]
    # load replace yml using unicodedecode
    with open(f"sql/{file_name}_replace.yml", "r", encoding="utf-8") as f:
        replace_dict = yaml.safe_load(f)
    # replace period_replace in sql file
    with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
        sql_commands = sql_file.read()

    # Process each period
    for period in replace_dict["period_replace"]:
        Q = sql_commands.format(period_replace=period)
        df = db.execute_query(Q)

        # Log the raw data for debugging
        logger.debug(f"Raw data for period {period}:")
        logger.debug(df.to_string())

        # Get average, best, and worst machine data
        if not 0 in df["order_index"].unique():
            avg = get_avg_chart4(df)
        else:
            avg = df[df["order_index"] == 0]

        best = (
            df[df["order_index"] == 1]
            .sort_values(by=["steam_ton", "power_kwh", "water_ton"], ascending=True)
            .iloc[0:1]
        )
        worst = (
            df[df["order_index"] == 1]
            .sort_values(by=["steam_ton", "power_kwh", "water_ton"], ascending=False)
            .iloc[0:1]
        )
        all_machine = df[df["order_index"] == 1].sort_values(
            by=["steam_ton", "power_kwh", "water_ton"], ascending=True
        )
        for col in ["water_ton", "power_kwh", "steam_ton"]:
            for df_label in [best, worst, all_machine]:
                df_label[col] = df_label[col].fillna(0)

        dfs[period] = {
            "avg": avg,
            "best": best,
            "worst": worst,
            "all_machine": all_machine,
        }

    return dfs


def get_avg_chart4(df):
    # * calculate the average of each cols in the df in form of df
    mask = df["order_index"] == 1
    _df = df[mask]
    for col in ["water_ton", "power_kwh", "steam_ton"]:
        _df[col] = _df[col].fillna(0)
    df_avg = pd.DataFrame(
        columns=["water_ton", "power_kwh", "steam_ton", "period", "machine_name"]
    )
    df_avg.loc[0, "water_ton"] = _df["water_ton"].mean()
    df_avg.loc[0, "power_kwh"] = _df["power_kwh"].mean()
    df_avg.loc[0, "steam_ton"] = _df["steam_ton"].mean()
    df_avg.loc[0, "period"] = df["period"].iloc[0]
    df_avg.loc[0, "machine_name"] = pd.NA
    return df_avg


def get_chart5_data(db) -> dict:
    """
    Get machine batch queued data from the database for different time windows.
    The time windows are:
    - 24_hrs: Current time +/- 12 hours.
    - 48_hrs: Window starts 24 hours before current time, ends 24 hours after current time. (48h duration)
    - 72_hrs: Window starts 24 hours before current time, ends 48 hours after current time. (72h duration)
    """
    sql_file_path = "sql/5_batch_queued.sql"
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            Q_template = f.read()
    except FileNotFoundError:
        logger.error(f"SQL file not found: {sql_file_path}")
        # Return empty data for all options if SQL file is missing
        # pandas (pd) is imported at the module level
        empty_df = pd.DataFrame()
        return {
            "24_hrs": {"all_machine": empty_df.copy()},
            "48_hrs": {"all_machine": empty_df.copy()},
            "72_hrs": {"all_machine": empty_df.copy()},
        }

    results = {}
    # TODO change back to now
    # now = datetime.now()
    now = datetime.strptime("2025-04-07 05:00:00", "%Y-%m-%d %H:%M:%S")
    # Standard SQL datetime format, ensure your database expects this format
    time_format = "%Y-%m-%d %H:%M:%S"

    time_configs = {
        "24_hrs": {  # current time +/- 12 hours
            "min_offset_from_now": timedelta(hours=-12),
            "max_offset_from_now": timedelta(hours=12),
        },
        "48_hrs": {  # starts 24 hours ago, duration 48 hours (ends +24h from now)
            "min_offset_from_now": timedelta(hours=-24),
            "max_offset_from_now": timedelta(hours=24),
        },
        "72_hrs": {  # starts 24 hours ago, duration 72 hours (ends +48h from now)
            "min_offset_from_now": timedelta(hours=-24),
            "max_offset_from_now": timedelta(hours=48),
        },
    }

    for option, config in time_configs.items():
        min_start_time_dt = now + config["min_offset_from_now"]
        max_start_time_dt = now + config["max_offset_from_now"]

        min_start_time_str = min_start_time_dt.strftime(time_format)
        max_start_time_str = max_start_time_dt.strftime(time_format)

        # Ensure the SQL template is correctly expecting these named placeholders
        try:
            Q = Q_template.format(
                min_start_time=min_start_time_str, max_start_time=max_start_time_str
            )
        except KeyError as e:
            logger.error(f"Missing placeholder in SQL template {sql_file_path}: {e}")
            # Fallback to empty DataFrame for this option if formatting fails
            df = pd.DataFrame()
        else:
            df = db.execute_query(Q)

        results[option] = {"all_machine": df}

    return results


def get_chart6_data(db) -> dict:
    """
    Get stop reasons data from the database for chart 6.

    For each period:
    1. Drop columns: central_id, central_name, period, date, refresh_time, write_time, if exists
    2. Pick the machine_avg, the machine with order_index = 1
    3. For order_index = 0, pick the machine with highest sum_hour and lowest sum_hour
    4. Also, get the count of machine with order_index = 0
    5. df_overall is [machine_avg['sum_hour'], machine_avg['sum_hour']/machine_count]
    6. For highest & lowest machine, pick the top 5 reason, among all columns starts with 'reason' of each machine, drop the rest of the
    columns, except machine name and the top 5 reasons
    7. Put them into {period: {avg: machine_avg, highest: machine_highest, lowest: machine_lowest}}
    """
    dfs = {}

    # Load replace yml using unicode decode
    with open("sql/1_machine_usage_replace.yml", "r", encoding="utf-8") as f:
        replace_dict = yaml.safe_load(f)

    # Load SQL file
    sql_file_path = "sql/6_stop_reason.sql"
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    # Process each period
    for period in replace_dict["period_replace"]:
        try:
            # Replace period in SQL query
            Q = sql_commands.format(period_replace=period)
            df = db.execute_query(Q)

            if df is None or df.empty:
                logger.warning(f"Chart6: No data returned for period {period}")
                continue

            # Step 1: Drop specified columns if they exist
            columns_to_drop = [
                "central_id",
                "central_name",
                "period",
                "date",
                "refresh_time",
                "write_time",
            ]
            existing_columns_to_drop = [
                col for col in columns_to_drop if col in df.columns
            ]
            if existing_columns_to_drop:
                df = df.drop(columns=existing_columns_to_drop)

            # Step 2: Get machine_avg (order_index = 1)
            machine_avg = (
                df[df["order_index"] == 1].copy()
                if "order_index" in df.columns
                else df.copy()
            )
            machine_all = (
                df[df["order_index"] == 0].copy()
                if "order_index" in df.columns
                else df.copy()
            )

            # Step 3 & 4: For order_index = 0, get highest and lowest sum_hour machines and count
            if "order_index" in df.columns and 0 in df["order_index"].values:
                order_0_machines = df[df["order_index"] == 0].copy()
                machine_count = len(order_0_machines)

                if (
                    not order_0_machines.empty
                    and "sum_hour" in order_0_machines.columns
                ):
                    # Highest sum_hour machine
                    highest_machine = (
                        order_0_machines.loc[order_0_machines["sum_hour"].idxmax()]
                        .to_frame()
                        .T
                    )
                    # Lowest sum_hour machine
                    lowest_machine = (
                        order_0_machines.loc[order_0_machines["sum_hour"].idxmin()]
                        .to_frame()
                        .T
                    )
                else:
                    highest_machine = pd.DataFrame()
                    lowest_machine = pd.DataFrame()
            else:
                machine_count = len(df) if not df.empty else 0
                # If no order_index = 0, use the data as is for highest/lowest
                if not df.empty and "sum_hour" in df.columns:
                    highest_machine = df.loc[df["sum_hour"].idxmax()].to_frame().T
                    lowest_machine = df.loc[df["sum_hour"].idxmin()].to_frame().T
                else:
                    highest_machine = pd.DataFrame()
                    lowest_machine = pd.DataFrame()

            # Step 5: Create df_overall
            if not machine_avg.empty and "sum_hour" in machine_avg.columns:
                avg_sum_hour = machine_avg["sum_hour"].mean()
                avg_per_machine = (
                    avg_sum_hour / machine_count if machine_count > 0 else 0
                )
                df_overall = pd.DataFrame(
                    {
                        "total_sum_hour": [avg_sum_hour],
                        "avg_per_machine": [avg_per_machine],
                        "machine_count": [machine_count],
                    }
                )
            else:
                df_overall = pd.DataFrame()

            # Step 6: For highest & lowest machine, pick top 5 reasons
            def process_machine_reasons(machine_df):
                if machine_df.empty:
                    return machine_df

                # Find columns that start with 'reason'
                reason_columns = [
                    col for col in machine_df.columns if col.startswith("reason")
                ]

                if not reason_columns:
                    # If no reason columns, return machine_name and sum_hour if available
                    keep_cols = ["machine_name"]
                    if "sum_hour" in machine_df.columns:
                        keep_cols.append("sum_hour")
                    return machine_df[keep_cols] if keep_cols else machine_df

                # Get top 5 reasons by value for each machine
                processed_machines = []
                for idx, row in machine_df.iterrows():
                    # Start with basic machine data
                    machine_data = {"machine_name": row.get("machine_name", "Unknown")}
                    if "sum_hour" in row:
                        machine_data["sum_hour"] = row["sum_hour"]

                    # Get reason values and sort them
                    reason_values = {}
                    for col in reason_columns:
                        if pd.notna(row[col]) and row[col] != 0:
                            reason_values[col] = row[col]

                    # Sort by value and take top 5
                    top_reasons = sorted(
                        reason_values.items(), key=lambda x: x[1], reverse=True
                    )[:5]

                    # Add top 5 reason columns with their original names and values
                    for reason_col, value in top_reasons:
                        machine_data[reason_col] = value

                    processed_machines.append(machine_data)

                return pd.DataFrame(processed_machines)

            highest_processed = process_machine_reasons(highest_machine)
            lowest_processed = process_machine_reasons(lowest_machine)

            # Step 7: Store in the result dictionary
            dfs[period] = {
                "all_machine": machine_all,
                "highest": highest_processed,
                "lowest": lowest_processed,
                "overall": df_overall,
            }

            logger.info(f"Chart6: Successfully processed data for period {period}")

        except Exception as e:
            logger.error(
                f"Chart6: Error processing data for period {period}: {str(e)}",
                exc_info=True,
            )
            # Create empty dataframes for this period
            dfs[period] = {
                "all_machine": pd.DataFrame(),
                "highest": pd.DataFrame(),
                "lowest": pd.DataFrame(),
                "overall": pd.DataFrame(),
            }

    return dfs
