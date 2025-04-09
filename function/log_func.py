"""
create logger that append new log at the top
make it easier to read

archive log Info from last week

Trunicate log Info if > 60 days
"""

import logging
import os
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import functools
import json
import sys
import traceback
from function.python_onedrive_func import *

# Global variables for configuration
LOG_PATH = None
CREDENTIALS = None
SP_CONFIG = None
SP_CONFIG_PATH = None


class BeginningOfFileHandler(logging.FileHandler):
    def emit(self, record):
        with open(self.baseFilename, "r") as file:
            contents = file.read()
        msg = self.format(record)
        with open(self.baseFilename, "w") as file:
            file.write(msg + os.linesep + contents)


def set_log_path(path):
    global LOG_PATH
    LOG_PATH = path


def set_sharepoint_config(credentials, sp_config=None, sp_config_path=None):
    """Set global SharePoint configuration variables"""
    global CREDENTIALS, SP_CONFIG, SP_CONFIG_PATH
    CREDENTIALS = credentials
    SP_CONFIG = sp_config if sp_config else {"var": {}}
    SP_CONFIG_PATH = sp_config_path


def log_wrapper():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # * LOG_PATH will be define when calling the primary func BY set_log_path()
            global LOG_PATH

            if not LOG_PATH:
                LOG_PATH = "temp_files/temp.log"

            # * separate LOGs info : different logger for different level
            loggers = {}
            for suffix in ["FATAL", "ERROR", "STARTEND", "INFO", "TRACE"]:
                logger = logging.getLogger(f"[{suffix}] [{func.__name__}]")
                logger.handlers = []  # Clear any existing handlers
                log_dir = os.path.join(os.path.dirname(LOG_PATH), suffix)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                log_path = os.path.join(
                    log_dir,
                    os.path.basename(LOG_PATH).replace(".log", f"-{suffix}.log"),
                )
                handler = BeginningOfFileHandler(log_path)
                handler.setLevel(logging.DEBUG)
                time_format = "%Y-%m-%d %H:%M:%S"
                formatter = logging.Formatter(
                    f"%(asctime)s %(name)s - %(message)s",
                    datefmt=time_format,
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                loggers[suffix] = logger

            loggers["STARTEND"].error("Starting")

            results = func(*args, **kwargs)

            if results is None:
                loggers["STARTEND"].error("Ending")
                return None

            # * Always treat the last item as json_output
            if isinstance(results, tuple):
                other_results, json_output = results[:-1], results[-1]
            else:
                other_results, json_output = None, results

            # Ensure json_output is a dictionary
            if not isinstance(json_output, dict):
                try:
                    json_output = json.loads(json_output)
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, wrap the result in a dict
                    json_output = {"result": json_output}

            if "LOG" in json_output:
                for log in json_output["LOG"]:
                    for info_cate in ["FATAL", "ERROR", "INFO", "TRACE"]:
                        if log.startswith(info_cate):
                            # Remove the prefix and any leading/trailing whitespace
                            clean_log = log.replace(f"{info_cate}:", "", 1).strip()
                            loggers[info_cate].error(clean_log)
                            break

            loggers["STARTEND"].error("Ending")

            # Process json_output
            processed_json_output = json_output.get("json_output", json_output)

            # if "json_output" in json_output:
            #     return json_output["json_output"]
            # else:
            #     return json_output
            # * Return other results untouched, along with the processed json_output
            if other_results:
                return (*other_results, processed_json_output)
            else:
                return processed_json_output

        return wrapper

    return decorator


def read_log_file(file_path):
    """Reads a log file and returns a list of log entries."""
    with open(file_path, "r") as file:
        return file.readlines()


def parse_log_entries(entries):
    """
    Parses log entries and returns two lists: timestamps and messages.
    A '\n' is added at the end of each complete message after processing all entries.
    """
    timestamps = []
    messages = []
    current_timestamp = None
    current_message = ""

    timestamp_pattern = r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"

    for entry in entries:
        entry = entry.rstrip()  # Remove trailing whitespace but keep leading whitespace
        if not entry:
            if current_message:
                current_message += "\n"  # Preserve empty lines within a message
            continue

        match = re.match(timestamp_pattern, entry)
        if match:
            # This is a new log entry
            if current_timestamp:
                # Save the previous entry if exists
                timestamps.append(current_timestamp)
                messages.append(current_message)

            current_timestamp = match.group(1)
            current_message = entry
        else:
            # This is a continuation of the previous message
            if current_message:
                current_message += "\n" + entry

    # Add the last entry if exists
    if current_timestamp:
        timestamps.append(current_timestamp)
        messages.append(current_message)

    # Add '\n' at the end of each message
    messages = [message.rstrip() + "\n" for message in messages]

    return timestamps, messages


def older_than_n_days(timestamp, n_days):
    """Checks if a timestamp is from last week."""
    if timestamp:
        # now = datetime.now()
        n_days_earlier = datetime.today() + relativedelta(days=-n_days)
        entry_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return entry_date <= n_days_earlier
    else:
        return True


def is_file_older_than_days(file_path, days):
    """Check if a file is older than specified number of days"""
    if not os.path.exists(file_path):
        return False
    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
    days_ago = datetime.now() - relativedelta(days=days)
    return file_mtime < days_ago


def create_ndays_log(LOG_PATH, ndays):
    """create folder of log files not older than n days and upload to SharePoint"""
    global CREDENTIALS, SP_CONFIG, SP_CONFIG_PATH

    if not all([CREDENTIALS, SP_CONFIG_PATH]):
        raise ValueError(
            "SharePoint configuration not set. Call set_sharepoint_config first."
        )
    log_folder = os.path.dirname(LOG_PATH)
    client = os.path.basename(log_folder)
    des_log_folder = log_folder.replace(client, f"{ndays}days_log/{client}")
    os.makedirs(des_log_folder, exist_ok=True)

    # First pass: Remove files older than 90 days
    for root, _, files in os.walk(log_folder):
        files = [file for file in files if file.endswith(".log")]
        for file in files:
            filepath = os.path.join(root, file)
            if is_file_older_than_days(filepath, 90):
                try:
                    os.remove(filepath)
                    print(f"Removed old log file: {filepath}")
                except Exception as e:
                    print(f"Error removing {filepath}: {str(e)}")

    # Second pass: Create filtered log folder
    for root, _, files in os.walk(log_folder):
        files = [file for file in files if file.endswith(".log")]
        for file in files:
            filepath = os.path.join(root, file)
            # Skip files older than 30 days
            if is_file_older_than_days(filepath, 30):
                continue

            entries = read_log_file(filepath)
            new_root = root.replace(client, f"{ndays}days_log/{client}")
            os.makedirs(new_root, exist_ok=True)
            trunicate_log_entries(
                entries, file_path=os.path.join(new_root, file), n_days=ndays
            )

    # Upload logs to SharePoint
    access_token = get_sharepoint_access_token(CREDENTIALS["credentials"])
    sharepoint_dealergroup_name = "onedrive"

    upload_log(
        access_token,
        CREDENTIALS,
        SP_CONFIG,
        SP_CONFIG_PATH,
        sharepoint_dealergroup_name,
        des_log_folder,
    )

    return des_log_folder


def trunicate_log_entries(entries, file_path, n_days):
    """remove log entries older than n days"""

    with open(file_path, "w") as source:
        timestamps, messages = parse_log_entries(entries)
        for timestamp, message in zip(timestamps, messages):
            if not older_than_n_days(timestamp, n_days):
                source.write(message + "\n")


def get_error_info():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_list = traceback.extract_tb(exc_traceback)

    main_line = None
    func_line = None
    main_file = os.path.basename(sys.argv[0])  # Get the filename of the main script

    for frame in tb_list:
        if frame.filename.endswith(main_file) and main_line is None:
            main_line = frame.lineno
        elif not frame.filename.endswith(main_file) and func_line is None:
            func_line = frame.lineno
            func_file = os.path.basename(frame.filename)

    error_msg = f"Error in {main_file}, line {main_line}"
    if func_line:
        error_msg += f"\n  Called function in {func_file}, line {func_line}"
    error_msg += f"\n{exc_type.__name__}: {str(exc_value)}"

    return error_msg
