"""Vizro data_manager registration — wraps data_access.py functions.

Import this module to register all data sources with Vizro's data_manager.
data_manager["name"] = load_fn  (function reference, NOT call — lazy evaluation).
"""

from vizro.managers import data_manager

from dashboard.data_access import load_forecast_data, load_mart

_MARTS = [
    "mart_price_trends",
    "mart_price_trends_national",
    "mart_seasonal_patterns",
    "mart_geo_disparity",
    "mart_commodity_correlation",
    "mart_correlation_summary",
]

for _name in _MARTS:
    data_manager[_name] = lambda name=_name: load_mart(name)

data_manager["forecast"] = load_forecast_data
