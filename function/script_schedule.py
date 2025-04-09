from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


def last_n_day_on_month(n=3):
    month = (datetime.now()).month
    year = (datetime.now()).year
    max_day = calendar.monthrange(year, month)[1]
    min_day = max_day - n
    ts_tdy = datetime.now().timestamp()
    ts_min = datetime(year, month, min_day, 0, 0, 0, 0).timestamp()
    ts_max = datetime(year, month, max_day, 23, 59, 59, 999).timestamp()
    # time_replace=str(max_time_replace)
    return (ts_tdy <= ts_max) & (ts_tdy >= ts_min)


def first_n_day_on_month(n=10):
    month = (datetime.now()).month
    year = (datetime.now()).year
    max_day = n
    min_day = 1
    ts_tdy = datetime.now().timestamp()
    ts_min = datetime(year, month, min_day, 0, 0, 0, 0).timestamp()
    ts_max = datetime(year, month, max_day, 23, 59, 59, 999).timestamp()
    # time_replace=str(max_time_replace)
    return (ts_tdy <= ts_max) & (ts_tdy >= ts_min)


def get_assigned_yearmonth(current_month_as_opening_month: bool):
    if current_month_as_opening_month:
        return (datetime.now() + relativedelta(months=-1)).strftime("%Y%m")
    else:
        return datetime.now().strftime("%Y%m")
