"""Helpers for loading Chicago's boundary and mapping rodent baiting records."""

from __future__ import annotations

from importlib.resources import files

import geopandas as gpd
import matplotlib.pyplot as plt


def load_chicago_boundary(crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Return the City of Chicago boundary (bundled with the package) as a GeoDataFrame."""
    path = files("chicago_rat_project") / "data" / "chicago_boundary.geojson"
    return gpd.read_file(str(path)).to_crs(crs)


def plot_on_chicago(gdf: gpd.GeoDataFrame, n: int | None = 10, ax=None, title=None):
    """Plot the first ``n`` rows of ``gdf`` (all rows if ``n`` is None) on a Chicago map.

    Returns the matplotlib Axes.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 10))
    load_chicago_boundary(gdf.crs).plot(ax=ax, color="whitesmoke", edgecolor="black")
    (gdf if n is None else gdf.head(n)).plot(ax=ax, color="red", markersize=40, zorder=3)
    ax.set_title(title or f"Rodent baiting records in Chicago (first {n})")
    ax.set_axis_off()
    return ax
