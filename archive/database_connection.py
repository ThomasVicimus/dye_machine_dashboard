import re
import yaml
import logging
import pandas as pd
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
        """Create SQLAlchemy engine with connection pooling."""
        try:
            connection_string = (
                f"mysql+pymysql://{self.credentials['username']}:{self.credentials['password']}@"
                f"{self.credentials['host']}:{self.credentials['port']}/{self.credentials['database']}"
                "?charset=utf8mb4"
            )

            return create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False,
                connect_args={"charset": "utf8mb4", "use_unicode": True},
            )
        except Exception as e:
            logger.error(f"Error creating database engine: {e}")
            raise

    def connect(self):
        """Establish database connection and return a connection object."""
        try:
            conn = self.engine.connect()
            logger.info("Connected to database successfully")
            return conn
        except SQLAlchemyError as e:
            logger.error(f"Error while connecting to database: {e}")
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
            raise

    def comment_out_line(self, sql_filepath, keyword):
        """Comment out lines containing a specific keyword in SQL file."""
        modified_lines = []
        try:
            with open(sql_filepath, "r") as file:
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
            raise


# Create a singleton instance

# Example usage:
db = DatabaseConnection()
if __name__ == "__main__":
    conn = None
    try:
        # Connect to database
        conn = db.connect()

        dfs = {}
        # load all sql startswith number
        for file in os.listdir("sql"):
            if re.match(r"^\d+", file) and file.endswith(".sql"):
                file_name = file.split(".")[0]
                # load replace yml using unicodedecode
                with open(f"sql/{file_name}_replace.yml", "r", encoding="utf-8") as f:
                    replace_dict = yaml.safe_load(f)
                # replace period_replace in sql file
                with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
                    sql_commands = sql_file.read()
                sql_commands = sql_commands.format(**replace_dict)
                dfs[file] = db.execute_query(
                    sql_commands
                )  # Use execute_query instead of execute_sql_file

        print(dfs)

    except Exception as e:
        logger.error(f"Error in database operations: {e}")
    finally:
        if conn:
            db.close(conn)
