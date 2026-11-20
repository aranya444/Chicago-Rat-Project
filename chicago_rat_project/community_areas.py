"""Community area lookup shared across all data files.
"""

from __future__ import annotations

import re

import pandas as pd

COMMUNITY_AREAS: dict[int, str] = {
    1: "Rogers Park",
    2: "West Ridge",
    3: "Uptown",
    4: "Lincoln Square",
    5: "North Center",
    6: "Lake View",
    7: "Lincoln Park",
    8: "Near North Side",
    9: "Edison Park",
    10: "Norwood Park",
    11: "Jefferson Park",
    12: "Forest Glen",
    13: "North Park",
    14: "Albany Park",
    15: "Portage Park",
    16: "Irving Park",
    17: "Dunning",
    18: "Montclare",
    19: "Belmont Cragin",
    20: "Hermosa",
    21: "Avondale",
    22: "Logan Square",
    23: "Humboldt Park",
    24: "West Town",
    25: "Austin",
    26: "West Garfield Park",
    27: "East Garfield Park",
    28: "Near West Side",
    29: "North Lawndale",
    30: "South Lawndale",
    31: "Lower West Side",
    32: "Loop",
    33: "Near South Side",
    34: "Armour Square",
    35: "Douglas",
    36: "Oakland",
    37: "Fuller Park",
    38: "Grand Boulevard",
    39: "Kenwood",
    40: "Washington Park",
    41: "Hyde Park",
    42: "Woodlawn",
    43: "South Shore",
    44: "Chatham",
    45: "Avalon Park",
    46: "South Chicago",
    47: "Burnside",
    48: "Calumet Heights",
    49: "Roseland",
    50: "Pullman",
    51: "South Deering",
    52: "East Side",
    53: "West Pullman",
    54: "Riverdale",
    55: "Hegewisch",
    56: "Garfield Ridge",
    57: "Archer Heights",
    58: "Brighton Park",
    59: "McKinley Park",
    60: "Bridgeport",
    61: "New City",
    62: "West Elsdon",
    63: "Gage Park",
    64: "Clearing",
    65: "West Lawn",
    66: "Chicago Lawn",
    67: "West Englewood",
    68: "Englewood",
    69: "Greater Grand Crossing",
    70: "Ashburn",
    71: "Auburn Gresham",
    72: "Beverly",
    73: "Washington Heights",
    74: "Mount Greenwood",
    75: "Morgan Park",
    76: "O'Hare",
    77: "Edgewater",
}


def normalize_name(name: str) -> str:
    """Lower-case a name, drop any parenthetical (e.g. "New City (Back of the Yards)"),
    and strip everything but letters/digits."""
    name = re.sub(r"\(.*?\)", "", str(name).lower())
    return re.sub(r"[^a-z0-9]", "", name)


# normalised name -> community area number (works for any spelling/case variant)
NAME_TO_NUMBER: dict[str, int] = {normalize_name(v): k for k, v in COMMUNITY_AREAS.items()}


def community_area_number(name: str) -> int | None:
    """Community area number for a name in any common spelling, or None if unknown."""
    return NAME_TO_NUMBER.get(normalize_name(name))


def _read_ranking(path, value_name: str) -> pd.DataFrame:
    """Read a 'citywide comparison' ranking spreadsheet into (Community Area, value, rank)."""
    raw = pd.read_excel(path, sheet_name="Data", header=2)
    out = pd.DataFrame(
        {
            "Community Area": raw["Community Area"].map(community_area_number),
            value_name: pd.to_numeric(
                raw["Community Area Value"].astype(str).str.replace(r"[$,]", "", regex=True),
                errors="coerce",
            ),
            f"{value_name} rank": raw["Rank"],
        }
    )
    unmatched = raw.loc[out["Community Area"].isna(), "Community Area"].tolist()
    if unmatched:
        raise ValueError(f"Unrecognised community area names in {path}: {unmatched}")
    out["Community Area"] = out["Community Area"].astype(int)
    return out


def load_median_income(path) -> pd.DataFrame:
    """Median household income per community area (columns: Community Area, Median income, rank)."""
    return _read_ranking(path, "Median income")


def load_population_density(path) -> pd.DataFrame:
    """Population density (people/sq mi) per community area."""
    return _read_ranking(path, "Population density")
