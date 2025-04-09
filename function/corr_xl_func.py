from datetime import datetime
import shutil
from function.short_utilities import *
import time


def correct_cate(df, cate_map):
    cate = df.Index.map(cate_map)
    cate = cate.fillna(df["Category"])
    df["Category"] = cate

    return df


def modify_pivot_table_years(sheet_name, field_name, workbook):
    worksheet = workbook.Sheets(sheet_name)
    # exclude & include years
    TY = str(datetime.today().year)
    LY = str(datetime.today().year - 1)
    # Create Excel application
    # excel_app.Visible = True  # Set to True if you want to see Excel in action

    # Open the workbook

    for pvt in worksheet.PivotTables():
        for item in pvt.PivotFields(field_name).PivotItems():
            try:
                time.sleep(0.5)
                pvt.PivotFields(field_name).PivotItems(item.Name).Visible = False
            except Exception:
                pass
        pvt.PivotFields(field_name).PivotItems(TY).Visible = True
        pvt.PivotFields(field_name).PivotItems(LY).Visible = True
    # Save and close the workbook
    workbook.Save()


def remove_by_yearmonth(output_path, data_sheetname, date_col_name, yearmonth_list):
    """
    same func as in clf_func.py
    yearmonth_list : [yyyymm]
    """
    df = pd.read_excel(output_path, sheet_name=data_sheetname)
    df[date_col_name] = pd.to_datetime(df[date_col_name])

    for yearmonth in yearmonth_list:
        year = int(yearmonth[0:4])
        month = int(yearmonth[4:])
        mask = (df[date_col_name].dt.year == year) & (
            df[date_col_name].dt.month == month
        )
        df = df.loc[~mask]

    wb = load_workbook(output_path)
    ws = wb[data_sheetname]

    ws.delete_rows(2, ws.max_row)
    wb.save(output_path)
    wb.close()
    paste_df_to_xl(output_path, data_sheetname, "A2", df)


def archive_train_data(train_path):
    train_path = os.path.abspath(train_path)
    directory = os.path.join(os.path.dirname(train_path), "archive")
    filename = os.path.basename(train_path).split(".")[0]
    if not os.path.exists(directory):
        os.makedirs(directory)

    modified_time = datetime.fromtimestamp(os.path.getmtime(train_path)).strftime(
        "%Y%m%d %H%M%S"
    )
    filename = filename + "-" + modified_time + ".xlsx"
    shutil.copyfile(train_path, os.path.join(directory, filename))
