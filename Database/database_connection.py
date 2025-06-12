import re
import yaml
import logging
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self, credentials_path="env/db_credentials.yml"):
        """Initialize database connection with credentials from YAML file."""
        self.credentials = self._load_credentials(credentials_path)
        self.engine = self._create_engine()

    def _load_credentials(self, credentials_path):
        """Load database credentials from YAML file."""
        try:
            with open(credentials_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {credentials_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing credentials file: {e}")
            raise

    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling for MySQL or SQL Server."""
        try:
            db_type = self.credentials.get("database_type", "mysql").lower()

            if db_type == "sqlserver" or db_type == "mssql":
                connection_string = self._create_sqlserver_connection_string()
                connect_args = {
                    "timeout": 30,
                    "autocommit": True,
                    "fast_executemany": True,  # Improves performance for bulk operations
                }
            else:  # Default to MySQL
                connection_string = self._create_mysql_connection_string()
                connect_args = {"charset": "utf8mb4", "use_unicode": True}

            return create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,  # Important for detecting stale connections
                echo=self.credentials.get("echo", False),
                connect_args=connect_args,
            )
        except Exception as e:
            logger.error(f"Error creating database engine: {e}")
            raise

    def _create_mysql_connection_string(self):
        """Create MySQL connection string."""
        return (
            f"mysql+pymysql://{self.credentials['username']}:{self.credentials['password']}@"
            f"{self.credentials['host']}:{self.credentials.get('port', 3306)}/"
            f"{self.credentials['database']}?charset=utf8mb4"
        )

    def _create_sqlserver_connection_string(self):
        """Create SQL Server connection string with proper error handling for WinError 10054."""
        driver = self.credentials.get("driver", "ODBC Driver 18 for SQL Server")
        port = self.credentials.get("port", 1433)

        # Handle different authentication methods
        if self.credentials.get("trusted_connection", False):
            # Windows Authentication
            connection_params = (
                f"DRIVER={{{driver}}};"
                f"SERVER={self.credentials['host']},{port};"
                f"DATABASE={self.credentials['database']};"
                f"Trusted_Connection=yes;"
            )
        else:
            # SQL Server Authentication
            connection_params = (
                f"DRIVER={{{driver}}};"
                f"SERVER={self.credentials['host']},{port};"
                f"DATABASE={self.credentials['database']};"
                f"UID={self.credentials['username']};"
                f"PWD={self.credentials['password']};"
            )

        # Add additional parameters to prevent WinError 10054
        additional_params = [
            "TrustServerCertificate=yes",  # Bypass certificate validation
            "Encrypt=yes",  # Force encryption
            "Connection Timeout=30",  # Connection timeout
            "Command Timeout=30",  # Command timeout
            "APP=SQLAlchemy",  # Application name for monitoring
        ]

        # Add optional parameters from credentials
        if self.credentials.get("mars_connection", True):
            additional_params.append("MARS_Connection=yes")

        connection_params += ";".join(additional_params)

        # URL encode the connection string
        quoted = urllib.parse.quote_plus(connection_params)
        return f"mssql+pyodbc:///?odbc_connect={quoted}"

    def connect(self):
        """Establish database connection and return a connection object."""
        try:
            conn = self.engine.connect()
            db_type = self.credentials.get("database_type", "mysql").lower()
            logger.info(f"Connected to {db_type} database successfully")
            return conn
        except SQLAlchemyError as e:
            logger.error(f"Error while connecting to database: {e}")
            # Add specific handling for WinError 10054
            if "10054" in str(e) or "Connection reset by peer" in str(e):
                logger.error(
                    "Connection reset error (10054) detected. This may be due to:"
                )
                logger.error("1. TLS/SSL protocol mismatch")
                logger.error("2. Outdated ODBC driver")
                logger.error("3. Network connectivity issues")
                logger.error("Consider updating to ODBC Driver 18 for SQL Server")
            raise

    def close(self, conn):
        """Close database connection."""
        try:
            if conn:
                conn.close()
                logger.info("Database connection closed")
        except SQLAlchemyError as e:
            logger.error(f"Error closing database connection: {e}")

    def execute_sql_file(self, sql_filepath_or_query, params=None):
        """Execute SQL commands from a file or raw query and return results as a DataFrame."""
        try:
            # Check if input is a file path or raw SQL
            if isinstance(sql_filepath_or_query, str) and os.path.isfile(
                sql_filepath_or_query
            ):
                with open(sql_filepath_or_query, "r", encoding="utf-8") as file:
                    sql_commands = file.read()
            else:
                sql_commands = sql_filepath_or_query

            if params:
                sql_commands = sql_commands.format(**params)

            with self.engine.connect() as conn:
                result = pd.read_sql(text(sql_commands), conn)
                return result

        except SQLAlchemyError as e:
            logger.error(f"Error executing SQL: {e}")
            if "10054" in str(e):
                logger.error(
                    "Connection reset during SQL execution. Retrying with new connection..."
                )
                # Optionally implement retry logic here
            raise

    def comment_out_line(self, sql_filepath, keyword):
        """Comment out lines containing a specific keyword in SQL file."""
        modified_lines = []
        try:
            with open(sql_filepath, "r", encoding="utf-8") as file:
                for line in file:
                    if keyword in line:
                        modified_lines.append("-- " + line)
                    else:
                        modified_lines.append(line)

            modified_query = "".join(modified_lines)
            return modified_query

        except Exception as e:
            logger.error(f"Error modifying SQL file {sql_filepath}: {e}")
            raise

    def execute_query(self, query, params=None):
        """Execute a raw SQL query and return results as a DataFrame."""
        try:
            with self.engine.connect() as conn:
                result = pd.read_sql(text(query), conn, params=params)
                return result
        except SQLAlchemyError as e:
            logger.error(f"Error executing query: {e}")
            if "10054" in str(e):
                logger.error(
                    "Connection reset during query execution. Check network stability and TLS configuration."
                )
            raise

    def test_connection(self):
        """Test database connection and return connection info."""
        try:
            with self.engine.connect() as conn:
                db_type = self.credentials.get("database_type", "mysql").lower()

                if db_type in ["sqlserver", "mssql"]:
                    # Test query for SQL Server
                    result = conn.execute(
                        text("SELECT @@VERSION as version, @@SERVERNAME as server_name")
                    )
                    row = result.fetchone()
                    logger.info(f"SQL Server Version: {row.version}")
                    logger.info(f"Server Name: {row.server_name}")
                else:
                    # Test query for MySQL
                    result = conn.execute(text("SELECT VERSION() as version"))
                    row = result.fetchone()
                    logger.info(f"MySQL Version: {row.version}")

                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Create a singleton instance
db = DatabaseConnection()

# Example usage:
if __name__ == "__main__":
    conn = None
    try:
        # Test connection first
        if db.test_connection():
            logger.info("Database connection test successful")

        # Connect to database
        conn = db.connect()

        dfs = {}
        # Check if sql directory exists
        if os.path.exists("sql"):
            # load all sql files that start with a number
            for file in os.listdir("sql"):
                if re.match(r"^\d+", file) and file.endswith(".sql"):
                    file_name = file.split(".")[0]

                    # Check if replace file exists
                    replace_file = f"sql/{file_name}_replace.yml"
                    if os.path.exists(replace_file):
                        # load replace yml using unicode decode
                        with open(replace_file, "r", encoding="utf-8") as f:
                            replace_dict = yaml.safe_load(f)

                        # replace parameters in sql file
                        with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
                            sql_commands = sql_file.read()
                        sql_commands = sql_commands.format(**replace_dict)
                    else:
                        # Load SQL file without parameter replacement
                        with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
                            sql_commands = sql_file.read()

                    dfs[file] = db.execute_query(sql_commands)
                    logger.info(f"Executed SQL file: {file}")

            print(f"Processed {len(dfs)} SQL files")
        else:
            logger.warning("SQL directory not found")

    except Exception as e:
        logger.error(f"Error in database operations: {e}")
    finally:
        if conn:
            db.close(conn)
