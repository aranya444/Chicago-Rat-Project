"""Community-area level regression of response time on income, density and rat premises."""

from __future__ import annotations

import pandas as pd
import statsmodels.api as sm

from .community_areas import COMMUNITY_AREAS, load_median_income, load_population_density


def build_community_area_table(gdf, income_path, density_path) -> pd.DataFrame:
    """One row per community area: mean response time, mean premises with rats, income, density.

    ``gdf`` is the output of :func:`preprocess_rodent_data` (needs 'Community Area',
    'Time to completion', 'Number of Premises with Rats'). Community area 0 (not a real
    area) and areas without data are excluded.
    """
    per_area = (
        gdf.groupby("Community Area")
        .agg(
            **{
                "Time to completion": ("Time to completion", "mean"),
                "Premises with rats": ("Number of Premises with Rats", "mean"),
                "Reports": ("Time to completion", "size"),
            }
        )
        .reset_index()
    )
    per_area = per_area[per_area["Community Area"].isin(COMMUNITY_AREAS)]
    table = (
        per_area.merge(load_median_income(income_path)[["Community Area", "Median income"]], on="Community Area")
        .merge(load_population_density(density_path)[["Community Area", "Population density"]], on="Community Area")
    )
    table.insert(1, "Community Area Name", table["Community Area"].map(COMMUNITY_AREAS))
    return table


def run_regression(table: pd.DataFrame):
    """OLS: Time to completion ~ median income + population density + premises with rats.

    Income is expressed in $1,000s and density in 1,000 people/sq mi so coefficients are readable.
    Returns the fitted statsmodels results.
    """
    X = pd.DataFrame(
        {
            "Median income ($1,000s)": table["Median income"] / 1000,
            "Population density (1,000/sq mi)": table["Population density"] / 1000,
            "Premises with rats (mean per report)": table["Premises with rats"],
        }
    )
    return sm.OLS(table["Time to completion"], sm.add_constant(X)).fit()


def plot_regression(table: pd.DataFrame, results, path=None):
    """Partial regression (added-variable) plots, one panel per predictor.

    Each panel shows the relationship between a predictor and time to completion with the
    other two predictors held constant; the line slope equals that predictor's coefficient.
    Points are community areas. Saves to ``path`` if given and returns the figure.
    """
    import matplotlib.pyplot as plt

    names = [n for n in results.params.index if n != "const"]
    fig, axes = plt.subplots(1, len(names), figsize=(15, 4.5), sharey=True)
    for ax, name in zip(axes, names):
        others = [n for n in names if n != name]
        exog = results.model.exog_names
        X = pd.DataFrame(results.model.exog, columns=exog)
        y = pd.Series(results.model.endog)
        ry = sm.OLS(y, X[["const"] + others]).fit().resid
        rx = sm.OLS(X[name], X[["const"] + others]).fit().resid
        ax.scatter(rx, ry, s=28, color="#2a6f97", alpha=0.8)
        slope = results.params[name]
        xs = pd.Series([rx.min(), rx.max()])
        ax.plot(xs, slope * xs, color="#c1121f", lw=2)
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_xlabel(f"{name} | others")
        ax.set_title(f"coef = {slope:.4f}, p = {results.pvalues[name]:.3f}", fontsize=10)
    axes[0].set_ylabel("Time to completion (weekdays) | others")
    fig.suptitle(
        f"Community-area regression of time to completion (n = {int(results.nobs)}, R² = {results.rsquared:.2f})"
    )
    fig.tight_layout()
    if path is not None:
        fig.savefig(path, dpi=150)
    return fig
