import mysql.connector
from mysql.connector import Error


def db(
    login_param={
        "host": "localhost",
        "database": "phateton",
        "user": "root",
        "password": "password",
    }
):

    try:
        conn = mysql.connector.connect(**login_param)
        if conn.is_connected():
            db_Info = conn.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)

    except Error as e:
        print("Error while connecting to MySQL", e)
    return conn


def comment_out_line(sql_filepath, keyword):
    modified_lines = []
    # Open the SQL file in read mode
    with open(sql_filepath, "r") as file:
        # Read through each line in the file
        for line in file:
            # Check if the keyword is in the current line
            if keyword in line:
                # Comment out the line by adding '--' at the beginning
                modified_lines.append("-- " + line)
            else:
                # If the keyword is not found, add the line as it is
                modified_lines.append(line)
        # Join all the modified lines to form the full modified SQL query
    modified_query = "".join(modified_lines)
    return modified_query
