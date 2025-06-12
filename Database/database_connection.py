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
        """Initialize MS SQL Server database connection with credentials from YAML file."""
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
        """Create SQLAlchemy engine with connection pooling for MS SQL Server."""
        try:
            # Get ODBC driver preference from credentials, default to ODBC Driver 18
            driver = self.credentials.get("driver", "ODBC Driver 18 for SQL Server")

            # Build connection string for SQL Server
            server = self.credentials["host"]
            port = self.credentials.get("port", 1433)
            database = self.credentials["database"]
            username = self.credentials["username"]
            password = self.credentials["password"]

            # Additional connection parameters to handle WinError 10054
            connection_params = {
                "DRIVER": driver,
                "SERVER": f"{server},{port}",
                "DATABASE": database,
                "UID": username,
                "PWD": password,
                "TrustServerCertificate": "yes",  # Important for TLS issues
                "Connection Timeout": "30",
                "Command Timeout": "30",
                "ApplicationIntent": "ReadWrite",
                "ConnectRetryCount": "3",
                "ConnectRetryInterval": "10",
                "Encrypt": "yes",  # Force encryption
                "MultipleActiveResultSets": "False",
                "Packet Size": "4096",
            }

            # Add authentication method
            auth_method = self.credentials.get("authentication", "sql")
            if auth_method.lower() == "windows":
                connection_params["Trusted_Connection"] = "yes"
                # Remove username/password for Windows auth
                del connection_params["UID"]
                del connection_params["PWD"]

            # Build connection string
            connection_string_parts = []
            for key, value in connection_params.items():
                connection_string_parts.append(f"{key}={value}")

            connection_string = ";".join(connection_string_parts)
            quoted_conn_str = urllib.parse.quote_plus(connection_string)

            # Create SQLAlchemy connection URL
            sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={quoted_conn_str}"

            logger.info(
                f"Connecting to SQL Server: {server}:{port}, Database: {database}"
            )

            return create_engine(
                sqlalchemy_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,  # Recycle connections every 30 minutes
                pool_pre_ping=True,  # Verify connections before use
                echo=False,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                },
                execution_options={"isolation_level": "READ_COMMITTED"},
            )
        except Exception as e:
            logger.error(f"Error creating SQL Server database engine: {e}")
            raise

    def connect(self):
        """Establish database connection and return a connection object."""
        try:
            conn = self.engine.connect()
            logger.info("Connected to SQL Server database successfully")
            return conn
        except SQLAlchemyError as e:
            logger.error(f"Error while connecting to SQL Server database: {e}")
            # Log specific error codes that might help with debugging
            if "10054" in str(e):
                logger.error(
                    "WinError 10054 detected - Connection was forcibly closed by remote host"
                )
                logger.error(
                    "This may be due to TLS/SSL configuration, firewall, or network issues"
                )
            elif "18456" in str(e):
                logger.error("SQL Server login failed - Check username/password")
            elif "2" in str(e):
                logger.error(
                    "SQL Server not found - Check server name and network connectivity"
                )
            raise

    def close(self, conn):
        """Close database connection."""
        try:
            if conn:
                conn.close()
                logger.info("SQL Server database connection closed")
        except SQLAlchemyError as e:
            logger.error(f"Error closing SQL Server database connection: {e}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = self.connect()
            yield conn
        except Exception as e:
            logger.error(f"Error in database connection context: {e}")
            raise
        finally:
            if conn:
                self.close(conn)

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

            with self.get_connection() as conn:
                result = pd.read_sql(text(sql_commands), conn, params=params)
                return result

        except SQLAlchemyError as e:
            logger.error(f"Error executing SQL: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing SQL: {e}")
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
            with self.get_connection() as conn:
                result = pd.read_sql(text(query), conn, params=params)
                return result
        except SQLAlchemyError as e:
            logger.error(f"Error executing query: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise

    def execute_non_query(self, query, params=None):
        """Execute a non-query SQL command (INSERT, UPDATE, DELETE) and return affected rows."""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Error executing non-query: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing non-query: {e}")
            raise

    def test_connection(self):
        """Test the database connection and return connection info."""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    text(
                        "SELECT @@VERSION as version, @@SERVERNAME as server_name, DB_NAME() as database_name"
                    )
                )
                info = result.fetchone()
                logger.info(f"Connection test successful: {info}")
                return {
                    "version": info[0],
                    "server_name": info[1],
                    "database_name": info[2],
                    "status": "Connected",
                }
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {"status": "Failed", "error": str(e)}


# Create a singleton instance
db = DatabaseConnection()

# Example usage:
if __name__ == "__main__":
    try:
        # Test connection first
        connection_info = db.test_connection()
        print("Connection Info:", connection_info)

        if connection_info["status"] == "Connected":
            dfs = {}

            # Check if sql directory exists
            if os.path.exists("sql"):
                # Load all SQL files that start with a number
                for file in os.listdir("sql"):
                    if re.match(r"^\d+", file) and file.endswith(".sql"):
                        file_name = file.split(".")[0]

                        # Check if replace file exists
                        replace_file = f"sql/{file_name}_replace.yml"
                        if os.path.exists(replace_file):
                            # Load replace dictionary
                            with open(replace_file, "r", encoding="utf-8") as f:
                                replace_dict = yaml.safe_load(f)

                            # Load and process SQL file
                            with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
                                sql_commands = sql_file.read()

                            sql_commands = sql_commands.format(**replace_dict)
                            dfs[file] = db.execute_query(sql_commands)
                        else:
                            # Execute SQL file without replacements
                            dfs[file] = db.execute_sql_file(f"sql/{file}")

                print("Query results:", dfs)
            else:
                logger.warning("SQL directory not found. Skipping SQL file execution.")
        else:
            logger.error(
                "Database connection failed. Please check your credentials and server configuration."
            )

    except Exception as e:
        logger.error(f"Error in database operations: {e}")
