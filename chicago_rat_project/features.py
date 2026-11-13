"""Date-based features: weekday-only time to completion and creation month."""

from __future__ import annotations

import calendar

import numpy as np
import pandas as pd
from PyWeekends import Weekend, WeekendStart

DATE_FORMAT = "%m/%d/%Y"


def _weekend_dates(years) -> np.ndarray:
    """All Saturday/Sunday dates (as datetime64[D]) in the given years, via PyWeekends."""
    dates = []
    for year in years:
        by_month = Weekend(year=int(year), weekend_start=WeekendStart.SATURDAY).all_weekends().to_original()
        for month, days in by_month.items():
            dates += [f"{year}-{int(month):02d}-{int(day):02d}" for day in days]
    return np.array(dates, dtype="datetime64[D]")


def add_time_features(
    df: pd.DataFrame,
    creation_col: str = "Creation Date",
    completion_col: str = "Completion Date",
) -> pd.DataFrame:
    """Add 'Time to completion' and 'Creation Month' columns (returns a copy).

    * ``Time to completion``: number of weekdays (Mon-Fri) elapsed from the creation
      date to the completion date, i.e. the weekdays in (creation, completion].
      Weekends are identified with the PyWeekends package. A request completed on
      the day it was created is 0. Rows with a missing/unparseable date get NaN.
    * ``Creation Month``: month name (January ... December) of the creation date,
      as an ordered categorical with all 12 months.

    Both date columns are expected as ``mm/dd/yyyy`` strings; the originals are left unchanged.
    """
    out = df.copy()
    created = pd.to_datetime(out[creation_col], format=DATE_FORMAT, errors="coerce")
    completed = pd.to_datetime(out[completion_col], format=DATE_FORMAT, errors="coerce")

    # Cumulative weekday count over the full calendar span, so each row is an O(1) lookup.
    valid = created.notna() & completed.notna()
    days_elapsed = pd.Series(np.nan, index=out.index)
    if valid.any():
        lo = min(created[valid].min(), completed[valid].min())
        hi = max(created[valid].max(), completed[valid].max())
        span = pd.date_range(f"{lo.year}-01-01", f"{hi.year}-12-31", freq="D")
        is_weekend = np.isin(span.values.astype("datetime64[D]"), _weekend_dates(range(lo.year, hi.year + 1)))
        cum_weekdays = pd.Series((~is_weekend).cumsum(), index=span)
        days_elapsed[valid] = (
            cum_weekdays.reindex(completed[valid]).to_numpy() - cum_weekdays.reindex(created[valid]).to_numpy()
        )
    out["Time to completion"] = days_elapsed

    months = list(calendar.month_name)[1:]
    out["Creation Month"] = pd.Categorical(
        created.dt.month_name(), categories=months, ordered=True
    )
    return out
