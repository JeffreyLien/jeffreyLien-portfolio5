"""Create the GitHub-facing executive analytics dashboard."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ASSETS = ROOT / "assets"


def money_millions(value, _position=None):
    return f"${value / 1_000_000:.0f}M"


def main() -> None:
    monthly = pd.read_csv(PROCESSED / "portfolio_monthly_kpis.csv")
    asset = pd.read_csv(PROCESSED / "asset_summary.csv")
    forecast = pd.read_csv(PROCESSED / "forecast_results.csv", parse_dates=["date"])

    generation = monthly.generation_mwh.sum()
    gross_margin = monthly.gross_margin_usd.sum()
    availability = asset.availability.mean()
    forecast_mape = forecast.ape.mean()
    opportunity = monthly.estimated_incremental_margin_usd.sum()

    navy = "#102A43"
    blue = "#1479B8"
    teal = "#00A6A6"
    orange = "#F28E2B"
    light = "#F4F7FA"
    grid = "#D8E1E8"

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.labelsize": 10,
    })
    fig = plt.figure(figsize=(18, 10), facecolor="white")
    gs = fig.add_gridspec(3, 12, height_ratios=[1.0, 3.1, 3.2], hspace=0.48, wspace=0.85)
    fig.suptitle("Power Portfolio — Executive Commercial Analytics", x=0.06, y=0.975,
                 ha="left", fontsize=25, fontweight="bold", color=navy)
    fig.text(0.06, 0.936, "Synthetic six-month operating portfolio | January–June 2026",
             ha="left", fontsize=11, color="#52606D")

    cards = [
        ("GENERATION", f"{generation / 1_000_000:.2f}M MWh", "Portfolio output"),
        ("GROSS MARGIN", f"${gross_margin / 1_000_000:.1f}M", "Modeled commercial margin"),
        ("AVAILABILITY", f"{availability:.1%}", "Average across assets"),
        ("JUNE FORECAST MAPE", f"{forecast_mape:.1%}", "Daily portfolio generation"),
        ("SCREENED OPPORTUNITY", f"${opportunity / 1_000_000:.1f}M", "Simplified margin proxy"),
    ]
    starts = [0, 2.4, 4.8, 7.2, 9.6]
    for (label, value, note), start in zip(cards, starts):
        ax = fig.add_subplot(gs[0, int(start):int(start + 2.4)])
        ax.set_facecolor(light)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(0.06, 0.76, label, transform=ax.transAxes, fontsize=9, fontweight="bold", color="#627D98")
        ax.text(0.06, 0.39, value, transform=ax.transAxes, fontsize=22, fontweight="bold", color=navy)
        ax.text(0.06, 0.10, note, transform=ax.transAxes, fontsize=8.5, color="#7B8794")
        ax.axvline(0.015, color=teal, linewidth=4)

    ax_month = fig.add_subplot(gs[1, 0:6])
    month_labels = pd.to_datetime(monthly.month).dt.strftime("%b")
    ax_month.plot(month_labels, monthly.gross_margin_usd, color=blue, marker="o", linewidth=2.5)
    ax_month.fill_between(range(len(monthly)), monthly.gross_margin_usd, alpha=0.10, color=blue)
    ax_month.set_title("Monthly Gross Margin", loc="left", color=navy)
    ax_month.yaxis.set_major_formatter(FuncFormatter(money_millions))
    ax_month.set_ylabel("USD")
    ax_month.grid(axis="y", color=grid, linewidth=0.8)
    ax_month.spines[["top", "right"]].set_visible(False)

    ax_asset = fig.add_subplot(gs[1, 6:12])
    ranked = asset.sort_values("gross_margin_usd", ascending=True)
    colors = [orange if tech in {"CCGT", "CT"} else teal for tech in ranked.technology]
    ax_asset.barh(ranked.asset_name, ranked.gross_margin_usd, color=colors)
    ax_asset.set_title("Gross Margin by Asset", loc="left", color=navy)
    ax_asset.xaxis.set_major_formatter(FuncFormatter(money_millions))
    ax_asset.grid(axis="x", color=grid, linewidth=0.8)
    ax_asset.set_axisbelow(True)
    ax_asset.spines[["top", "right", "left"]].set_visible(False)
    ax_asset.tick_params(axis="y", length=0)

    ax_forecast = fig.add_subplot(gs[2, :])
    ax_forecast.plot(forecast.date, forecast.generation_mwh, label="Actual", color=navy, linewidth=2.2)
    ax_forecast.plot(forecast.date, forecast.predicted_generation_mwh, label="Forecast", color=orange, linewidth=2.2)
    ax_forecast.set_title("June Daily Generation — Actual vs Forecast", loc="left", color=navy)
    ax_forecast.set_ylabel("MWh")
    ax_forecast.grid(color=grid, linewidth=0.8)
    ax_forecast.spines[["top", "right"]].set_visible(False)
    ax_forecast.legend(frameon=False, ncol=2, loc="upper right")

    fig.text(0.06, 0.02,
             "All figures are synthetic. Opportunity values are screening estimates, not dispatch recommendations.",
             fontsize=9, color="#7B8794")
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / "executive_overview.png", dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Executive dashboard created.")


if __name__ == "__main__":
    main()
