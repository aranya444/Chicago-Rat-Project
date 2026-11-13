"""Preprocessing for the Chicago Rodent Baiting - Historical dataset."""

from __future__ import annotations

import geopandas as gpd
import pandas as pd

DEFAULT_DROP_COLUMNS = (
    "Street Address",
    "X Coordinate",
    "Y Coordinate",
    "Location",
    "Ward",
    "Community Area",
    "Current Activity",
    "Type of Service Request",
)

# Columns whose missing values are tolerated by dropna (none by default).
DEFAULT_DROPNA_IGNORE = ()


def preprocess_rodent_data(
    data: str | pd.DataFrame,
    drop_columns=DEFAULT_DROP_COLUMNS,
    exclude_status: str | None = "Completed",
    crs: str = "EPSG:4326",
    dropna_ignore=DEFAULT_DROPNA_IGNORE,
    output_path: str | None = None,
) -> gpd.GeoDataFrame:
    """Clean the rodent baiting data and attach point geometry.

    Steps:
      1. Load the CSV (or copy the DataFrame passed in).
      2. Drop unneeded columns.
      3. Remove rows whose ``Status`` equals ``exclude_status``
         (pass ``None`` to keep all rows).
      4. Drop rows with missing values in any column except ``dropna_ignore``
         (by default none).
      5. Build a GeoDataFrame with Point geometry from Longitude/Latitude.

    Parameters
    ----------
    data : path to the CSV, or an already-loaded DataFrame.
    drop_columns : columns to remove (missing columns are ignored).
    exclude_status : Status value to filter out.
    crs : coordinate reference system of Latitude/Longitude.
    dropna_ignore : columns whose missing values do not cause a row to be dropped.

    output_path : if given, save the GeoDataFrame there (GeoPackage, ``.gpkg``;
        the format is inferred from the extension by geopandas/pyogrio).

    Returns
    -------
    geopandas.GeoDataFrame
    """
    df = pd.read_csv(data, low_memory=False) if isinstance(data, (str, bytes)) or hasattr(data, "__fspath__") else data.copy()

    df = df.drop(columns=list(drop_columns), errors="ignore")
    if exclude_status is not None:
        df = df[df["Status"] != exclude_status]
    subset = [c for c in df.columns if c not in set(dropna_ignore)]
    df = df.dropna(subset=subset)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs=crs,
    )
    if output_path is not None:
        gdf.to_file(output_path)
    return gdf
