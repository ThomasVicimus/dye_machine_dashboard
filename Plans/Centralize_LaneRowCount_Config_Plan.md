# Centralize Lane/Row Count Configuration Plan

## Goal

Create a single configuration file that controls the number of rows/lanes displayed for Chart 2 (DataTable) and Chart 5 (Timeline Gantt). These two charts should share the same lane count for visual consistency across the dashboard.

---

## 1. Current State – Where Row/Lane Counts Are Set

### Chart 2 (Machine Status DataTable)

| File | Function/Parameter | Default Value | Notes |
|------|-------------------|---------------|-------|
| `ChartFactory/chartfactory_chart2.py` | `create_chart2_figure(..., desktop_row_count=8, mobile_row_count=4)` | 8 / 4 | **Defines** the parameter with a default; actual value comes from caller |
| `PlotCharts/PlotChart_MachineStatus.py` | `create_chart2_layout(..., desktop_row_count=8, mobile_row_count=4)` | 8 / 4 | **Caller** that passes the value down to factory |
| `layouts/mobile_dashboard_layout.py` | `create_chart2_layout(...)` | Uses defaults | Does **not** override; relies on PlotChart defaults |
| `layouts/desktop_dashboard_layout.py` | `create_chart2_layout(...)` | Uses defaults | Same as above |
| `callbacks/refresher_callback.py` | `register_chart2_page_turner(app)` | None | Uses `page_count` from DataTable component – **no hardcoded row count** |

**Summary for Chart 2:**  
Primary source of truth is `PlotCharts/PlotChart_MachineStatus.py` function signature defaults. The factory in `ChartFactory/chartfactory_chart2.py` has matching defaults but is always called *via* the PlotChart layer.

---

### Chart 5 (Machine Activity Timeline)

| File | Function/Parameter | Default Value | Notes |
|------|-------------------|---------------|-------|
| `ChartFactory/chart_factory_chart5.py` | `create_chart5_figure(..., page_size=None)` | None | Only used if passed explicitly |
| `PlotCharts/PlotChart_chart5.py` | `create_chart5_layout(..., page_size=8, mobile_page_size=4)` | 8 / 4 | **Initial render** uses these defaults |
| `callbacks/select_time_period_callback.py` | `register_chart5_timeframe_callbacks(..., page_size_mobile=4, page_size_desktop=8)` | 4 / 8 | **Primary control** – slices dataframe before rendering |
| `mobile_app.py` | `register_chart5_timeframe_callbacks(...)` | Uses defaults | Does **not** override |
| `desktop_app.py` | `register_chart5_timeframe_callbacks(...)` | Uses defaults | Does **not** override |

**Summary for Chart 5:**  
The callback function in `callbacks/select_time_period_callback.py` is the *primary* driver because it slices the dataframe and regenerates the figure on every update. The PlotChart only controls *initial* render before callbacks fire.

---

## 2. Problem

1. **Scattered defaults** – values appear in 4–5 files, making changes error-prone.
2. **Inconsistency risk** – Chart 2 and Chart 5 may diverge if edited independently.
3. **Hardcoded in Python** – non-developers cannot easily adjust without editing source code.
4. **Future expansion** – other tunables (refresh intervals, theme colors, data fetch intervals) will face the same issue.

---

## 3. Proposed Solution

### 3.1 Create a central YAML config file

**File:** `env/dashboard_config.yml`

```yaml
# Dashboard Configuration
# This file controls tunable parameters for the Dye Machine Dashboard.
# Changes here take effect on next app restart.

# -------------------------------------------------------------------
# Lane / Row Counts (Chart 2 Table & Chart 5 Timeline)
# -------------------------------------------------------------------
charts:
  lane_count:
    desktop: 8      # rows/lanes shown on desktop dashboard
    mobile: 4       # rows/lanes shown on mobile dashboard

# -------------------------------------------------------------------
# Chart 2 Specific
# -------------------------------------------------------------------
chart2:
  page_interval_seconds: 15   # seconds between auto page turns (desktop only)

# -------------------------------------------------------------------
# Chart 5 Specific
# -------------------------------------------------------------------
chart5:
  default_timeframe: "24_hrs"   # initial timeframe: 24_hrs | 48_hrs | 72_hrs

# -------------------------------------------------------------------
# Data Refresh
# -------------------------------------------------------------------
data_refresh:
  interval_seconds: 60   # how often to poll the database for new data

# -------------------------------------------------------------------
# Theme
# -------------------------------------------------------------------
theme:
  default_color: "black"   # black | dark_blue
  default_lang: "zh_cn"    # zh_cn | zh_hk | en
```

### 3.2 Create a config loader module

**File:** `function/dashboard_config.py`

```python
"""
Centralized dashboard configuration loader.

All tunable dashboard parameters should be loaded from here.
"""

import os
import yaml
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "env", "dashboard_config.yml")
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
```

### 3.3 Refactor consuming files

**Files to update:**

| File | Change |
|------|--------|
| `PlotCharts/PlotChart_MachineStatus.py` | Import `get_lane_count`, `get_chart2_page_interval`; use as defaults |
| `PlotCharts/PlotChart_chart5.py` | Import `get_lane_count`; use as defaults for `page_size` / `mobile_page_size` |
| `callbacks/select_time_period_callback.py` | Import `get_lane_count`; use for `page_size_mobile` / `page_size_desktop` defaults in `register_chart5_timeframe_callbacks` |
| `layouts/mobile_dashboard_layout.py` | (Optional) Import `get_chart5_default_timeframe` for initial Chart 5 period |
| `layouts/desktop_dashboard_layout.py` | Same as above |
| `mobile_app.py` | Import `get_default_theme`, `get_default_lang`; use in `create_mobile_layout(...)` |
| `desktop_app.py` | Same as above |

**Example refactor (PlotCharts/PlotChart_MachineStatus.py):**

```python
from function.dashboard_config import get_lane_count, get_chart2_page_interval

def create_chart2_layout(
    dfs: dict,
    chart_id: str = "chart-2",
    page_interval: int = None,
    desktop_row_count: int = None,
    mobile_row_count: int = None,
    mobile: bool = False,
    theme: str = "black",
):
    # Apply config defaults if not explicitly passed
    if page_interval is None:
        page_interval = get_chart2_page_interval()
    if desktop_row_count is None:
        desktop_row_count = get_lane_count("desktop")
    if mobile_row_count is None:
        mobile_row_count = get_lane_count("mobile")
    ...
```

---

## 4. Implementation Steps

| Step | Description | Files |
|------|-------------|-------|
| 1 | Create `env/dashboard_config.yml` with initial values | New file |
| 2 | Create `function/dashboard_config.py` loader module | New file |
| 3 | Refactor `PlotCharts/PlotChart_MachineStatus.py` | Existing |
| 4 | Refactor `PlotCharts/PlotChart_chart5.py` | Existing |
| 5 | Refactor `callbacks/select_time_period_callback.py` | Existing |
| 6 | (Optional) Refactor `mobile_app.py` / `desktop_app.py` for theme/lang defaults | Existing |
| 7 | Update README documentation | `README/Chart2_MachineStatus.md`, `README/Chart5.md` |
| 8 | Test both desktop and mobile apps | Manual |

---

## 5. Future Enhancements

Once the config infrastructure is in place, the following can be added to `dashboard_config.yml`:

- **Database connection** (currently in `env/db_credentials.yml` – could be merged or left separate for security)
- **Port / host settings** for `mobile_app.py` / `desktop_app.py`
- **Chart colors / palettes**
- **Text card display options**
- **Detail page figure heights**
- **Auto-refresh toggle** (enable/disable)

---

## 6. Optional: Config Editor Script

For future use (not in initial scope):

**File:** `scripts/edit_config.py`

A CLI or simple TUI (using `inquirer` or `questionary`) that:

1. Reads `env/dashboard_config.yml`
2. Presents current values
3. Prompts user to change values
4. Writes back to file

This allows non-developers on the factory floor to adjust dashboard settings without editing YAML manually.

Example:

```bash
python scripts/edit_config.py
# > Dashboard Configuration Editor
# > Current lane count (desktop): 8
# > New value (Enter to keep): 10
# > Current lane count (mobile): 4
# > New value (Enter to keep): 6
# > ...
# > Config saved!
```

---

## 7. Done Criteria

- [ ] `env/dashboard_config.yml` exists with documented fields
- [ ] `function/dashboard_config.py` loads and caches config
- [ ] Chart 2 and Chart 5 use config for lane/row counts
- [ ] Changing the YAML value and restarting the app changes the dashboard behavior
- [ ] Documentation updated in README files

---

## Appendix: Current Defaults Summary

| Parameter | Desktop | Mobile |
|-----------|---------|--------|
| Chart 2 `page_size` | 8 | 4 |
| Chart 5 `page_size` | 8 | 4 |
| Chart 2 `page_interval` | 15s | (not used on mobile) |
| Data refresh interval | 60s | 60s |

