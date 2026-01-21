"""
Centralized dashboard configuration loader.

All tunable dashboard parameters should be loaded from here.
"""

import os
import yaml
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Use absolute path relative to this file to avoid issues with current working directory
_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "env", "dashboard_config.yml")
)
_config_cache: Dict[str, Any] = {}


def load_config(force_reload: bool = False) -> Dict[str, Any]:
    """Load configuration from YAML file (cached)."""
    global _config_cache
    if _config_cache and not force_reload:
        return _config_cache

    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            _config_cache = yaml.safe_load(f) or {}
        logger.info("Dashboard config loaded from %s", _CONFIG_PATH)
    except FileNotFoundError:
        logger.warning("Config file not found at %s, using defaults", _CONFIG_PATH)
        _config_cache = {}
    except yaml.YAMLError as e:
        logger.error("Error parsing config file: %s", e)
        _config_cache = {}
    return _config_cache


def get_lane_count(platform: str = "desktop") -> int:
    """Return the lane/row count for the specified platform."""
    cfg = load_config()
    lane_cfg = cfg.get("charts", {}).get("lane_count", {})
    if platform == "mobile":
        return lane_cfg.get("mobile", 4)
    return lane_cfg.get("desktop", 8)


def get_chart2_page_interval() -> int:
    """Return the page interval in seconds for Chart 2 auto page turning."""
    cfg = load_config()
    return cfg.get("chart2", {}).get("page_interval_seconds", 15)


def get_chart5_default_timeframe() -> str:
    """Return the default timeframe for Chart 5."""
    cfg = load_config()
    return cfg.get("chart5", {}).get("default_timeframe", "24_hrs")


def get_data_refresh_interval() -> int:
    """Return the data refresh interval in seconds."""
    cfg = load_config()
    return cfg.get("data_refresh", {}).get("interval_seconds", 60)


def get_default_theme() -> str:
    """Return the default color theme."""
    cfg = load_config()
    return cfg.get("theme", {}).get("default_color", "black")


def get_default_lang() -> str:
    """Return the default language."""
    cfg = load_config()
    return cfg.get("theme", {}).get("default_lang", "zh_cn")

