"""chicago_rat_project: preprocess Chicago rodent baiting data into a GeoDataFrame."""

from .analysis import build_community_area_table, plot_regression, run_regression
from .community_areas import (
    COMMUNITY_AREAS,
    NAME_TO_NUMBER,
    community_area_number,
    load_median_income,
    load_population_density,
)
from .features import add_time_features
from .mapping import load_chicago_boundary, plot_on_chicago
from .preprocess import preprocess_rodent_data

__all__ = ["preprocess_rodent_data", "add_time_features",
    "COMMUNITY_AREAS", "NAME_TO_NUMBER", "community_area_number",
    "load_median_income", "load_population_density",
    "build_community_area_table", "run_regression", "plot_regression", "load_chicago_boundary", "plot_on_chicago"]
__version__ = "0.1.0"
