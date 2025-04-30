import pandas as pd
import logging
import json
from io import StringIO

logger = logging.getLogger(__name__)


# Helper function to serialize DataFrames within a nested dictionary
def serialize_dataframe_dict(data_dict):
    serialized = {}
    for period, period_data in data_dict.items():
        serialized_period = {}
        for key, value in period_data.items():
            if isinstance(value, pd.DataFrame):
                # Use orient='split' for better round-tripping
                serialized_period[key] = value.to_json(
                    orient="split", date_format="iso"
                )
            else:
                # Keep non-DataFrame values as is (if any)
                serialized_period[key] = value
        serialized[period] = serialized_period
    return serialized


# Helper function to deserialize DataFrame JSON strings within a nested dictionary
def deserialize_dataframe_dict(serialized_dict):
    deserialized = {}
    if not isinstance(serialized_dict, dict):
        logger.error(
            f"Expected a dictionary for deserialization, got {type(serialized_dict)}"
        )
        return None  # Or raise an error

    for period, period_data in serialized_dict.items():
        deserialized_period = {}
        if not isinstance(period_data, dict):
            logger.warning(
                f"Skipping deserialization for period '{period}', expected dict, got {type(period_data)}"
            )
            deserialized[period] = period_data  # Keep as is if not a dict
            continue

        for key, value in period_data.items():
            if isinstance(value, str):
                try:
                    # Wrap the JSON string in StringIO to avoid FutureWarning
                    deserialized_period[key] = pd.read_json(
                        StringIO(value), orient="split"
                    )
                except (ValueError, TypeError) as e:
                    # If it fails, it might not be a DataFrame JSON string, keep as is
                    logger.debug(
                        f"Value for key '{key}' in period '{period}' is not DataFrame JSON: {e}. Keeping original value."
                    )
                    deserialized_period[key] = value
            else:
                # Keep non-string values as is
                deserialized_period[key] = value
        deserialized[period] = deserialized_period
    return deserialized
