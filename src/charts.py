"""
Visualization Module for COVID-19 Data Explorer.
Provides both high-performance interactive Plotly visualizations
styled for dark editorial UI and static Matplotlib/Seaborn generators
for reproducible report figure exports.
"""

from pathlib import Path
from typing import Optional, Union
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/CLI safety
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns


# UI Design Palette - Dark Luxury Editorial
THEME = {
    "bg_dark": "#0B0D10",
    "surface": "#12161F",
    "surface_elevated": "#1A202C",
    "border": "#232A36",
    "text_primary": "#F8FAFC",
    "text_muted": "#94A3B8",
    "text_subtle": "#64748B",
    "accent_blue": "#38BDF8",     # Cyan / Sky
    "accent_indigo": "#818CF8",   # Electric Indigo
    "accent_purple": "#A855F7",   # Violet
    "accent_rose": "#FB7185",     # Coral / Rose
    "accent_emerald": "#34D399",  # Emerald
    "accent_amber": "#FBBF24",    # Amber
}

CONTINENT_COLORS = {
    "Europe": "#38BDF8",
    "Asia": "#818CF8",
    "Northern America": "#F472B6",
    "Latin America and the Caribbean": "#FB7185",
    "Africa": "#FBBF24",
    "Oceania": "#34D399",
}


def apply_dark_layout(fig: go.Figure, height: int = 450) -> go.Figure:
    """Applies sleek dark-first design layout to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", color=THEME["text_muted"], size=12),
        margin=dict(l=40, r=40, t=50, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor=THEME["surface_elevated"],
            bordercolor=THEME["border"],
            font=dict(color=THEME["text_primary"], size=12),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor=THEME["border"],
            tickcolor=THEME["border"],
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor=THEME["border"],
            tickcolor=THEME["border"],
            zeroline=False,
        ),
    )
    return fig


# =============================================================================
# 1. INTERACTIVE PLOTLY CHARTS
# =============================================================================

def create_horizontal_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: Optional[str] = None,
    color_scale: str = "Blues",
    bar_color: Optional[str] = None,
    height: int = 420,
    reverse_y: bool = True,
) -> go.Figure:
    """Generates an editorial horizontal bar chart with formatted values and tooltips."""
    data = df.copy()
    if reverse_y:
        data = data.iloc[::-1]  # Top rank displayed at the top

    if color_col and color_col in data.columns:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            orientation="h",
            color=color_col,
            color_discrete_map=CONTINENT_COLORS if color_col == "Continent" else None,
            title=title,
        )
    else:
        color = bar_color or THEME["accent_blue"]
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            orientation="h",
            title=title,
        )
        fig.update_traces(marker_color=color, marker_line_width=0)

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(color=THEME["text_primary"], size=15),
            x=0.01,
            y=0.98,
        ),
        xaxis_title="",
        yaxis_title="",
        showlegend=False,  # Keep charts sleek and minimal without crowded legends
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>" + f"{x_col}: " + "%{x:,.2f}<extra></extra>"
        if "percentage" in x_col.lower()
        else "<b>%{y}</b><br>" + f"{x_col}: " + "%{x:,}<extra></extra>"
    )

    return apply_dark_layout(fig, height=height)


def create_continent_comparison_chart(continent_df: pd.DataFrame, metric: str = "Total_Cases") -> go.Figure:
    """Creates a dual comparative visualization of continent breakdown."""
    metric_label = metric.replace("_", " ")
    data = continent_df.sort_values(by=metric, ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=data["Continent"],
            x=data[metric],
            orientation="h",
            marker=dict(
                color=[CONTINENT_COLORS.get(c, THEME["accent_blue"]) for c in data["Continent"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>" + f"{metric_label}: " + "%{x:,}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Distribution of {metric_label} Across Continents</b>",
            font=dict(color=THEME["text_primary"], size=15),
            x=0.01,
            y=0.96,
        ),
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
    )
    return apply_dark_layout(fig, height=380)


def create_continent_donut_chart(continent_df: pd.DataFrame, metric: str = "Total_Cases") -> go.Figure:
    """Creates an editorial donut chart for continent proportions."""
    metric_label = metric.replace("_", " ")
    fig = go.Figure(
        data=[
            go.Pie(
                labels=continent_df["Continent"],
                values=continent_df[metric],
                hole=0.62,
                marker=dict(colors=[CONTINENT_COLORS.get(c, "#94A3B8") for c in continent_df["Continent"]]),
                textinfo="percent",
                hoverinfo="label+value+percent",
                textfont=dict(size=12, color=THEME["text_primary"]),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text=f"<b>{metric_label} Share by Continent</b>",
            font=dict(color=THEME["text_primary"], size=15),
            x=0.01,
            y=0.96,
        ),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color=THEME["text_muted"]),
        ),
        annotations=[
            dict(
                text=metric_label.split()[0].upper(),
                x=0.5,
                y=0.5,
                font=dict(size=14, color=THEME["text_muted"], family="monospace"),
                showarrow=False,
            )
        ],
    )
    return apply_dark_layout(fig, height=380)


def create_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    log_x: bool = True,
    log_y: bool = True,
    height: int = 480,
) -> go.Figure:
    """Creates an interactive scatter plot with hover metadata and continent coloring."""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="Continent",
        color_discrete_map=CONTINENT_COLORS,
        hover_name="Country",
        hover_data={
            "Continent": True,
            "Population": ":,",
            "Total Cases": ":,",
            "Total Deaths": ":,",
            "Death percentage": ":.2f",
        },
        log_x=log_x,
        log_y=log_y,
        title=title,
    )

    fig.update_traces(
        marker=dict(size=8, opacity=0.82, line=dict(width=0.6, color="rgba(255,255,255,0.4)")),
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(color=THEME["text_primary"], size=14),
            x=0.01,
            y=0.98,
        ),
        xaxis_title=f"{x_col} {'(Log Scale)' if log_x else ''}",
        yaxis_title=f"{y_col} {'(Log Scale)' if log_y else ''}",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
        margin=dict(l=45, r=25, t=55, b=65),
    )
    return apply_dark_layout(fig, height=height)


def create_correlation_heatmap(corr_matrix: pd.DataFrame, method: str = "Spearman") -> go.Figure:
    """Creates an interactive correlation matrix heatmap with clear value labels."""
    z_values = corr_matrix.values
    x_labels = corr_matrix.columns.tolist()
    y_labels = corr_matrix.index.tolist()

    text_values = np.around(z_values, decimals=2).astype(str)

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=x_labels,
            y=y_labels,
            text=text_values,
            texttemplate="%{text}",
            textfont=dict(size=12, color=THEME["text_primary"]),
            colorscale=[
                [0.0, "#0284C7"],    # Cool blue for negative
                [0.5, "#1E293B"],    # Neutral slate for zero
                [1.0, "#F43F5E"],    # Warm rose for strong positive
            ],
            zmin=-1,
            zmax=1,
            colorbar=dict(
                title=dict(text=f"{method} r", font=dict(color=THEME["text_muted"], size=11)),
                tickfont=dict(color=THEME["text_muted"], size=10),
                thickness=12,
                len=0.85,
            ),
            hoverongaps=False,
            hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{method} Rank Correlation Heatmap</b>",
            font=dict(color=THEME["text_primary"], size=15),
            x=0.01,
            y=0.96,
        ),
        xaxis=dict(tickangle=-30),
        yaxis=dict(autorange="reversed"),
    )
    return apply_dark_layout(fig, height=480)


def create_country_benchmark_chart(country_profile: dict) -> go.Figure:
    """Creates a comparative benchmark bar comparing country metrics to continent averages."""
    country_name = country_profile["country"]
    continent = country_profile["continent"]

    categories = ["Total Cases", "Total Deaths", "Death Pct (%)"]
    country_vals = [
        country_profile["total_cases"],
        country_profile["total_deaths"],
        country_profile["death_percentage"],
    ]
    continent_vals = [
        country_profile["continent_avg_cases"],
        country_profile["continent_avg_deaths"],
        country_profile["continent_avg_death_pct"],
    ]

    # Normalize to ratio of continent average (Continent Avg = 100%)
    c_ratios = [
        (c / cont * 100) if cont > 0 else 0
        for c, cont in zip(country_vals, continent_vals)
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=country_name,
            x=categories,
            y=c_ratios,
            marker_color=THEME["accent_blue"],
            hovertemplate=f"<b>{country_name}</b>: %{{y:.1f}}% of continent average<extra></extra>",
        )
    )

    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=THEME["accent_amber"],
        annotation_text=f"{continent} Average (100%)",
        annotation_position="top left",
        annotation_font_color=THEME["accent_amber"],
        annotation_font_size=11,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{country_name} vs. {continent} Average (100% Benchmark)</b>",
            font=dict(color=THEME["text_primary"], size=14),
            x=0.01,
            y=0.96,
        ),
        yaxis_title="Relative Benchmark (%)",
        yaxis=dict(ticksuffix="%"),
    )
    return apply_dark_layout(fig, height=360)


# =============================================================================
# 2. STATIC MATPLOTLIB / SEABORN FIGURE EXPORTERS (TASKS 13, 15, 17, 20, 22, 23, 24, 25)
# =============================================================================

def generate_static_assignment_charts(df: pd.DataFrame, output_dir: Union[str, Path]) -> dict:
    """
    Renders and exports all 8 canonical figures from the assignment requirements
    into the designated outputs directory using Matplotlib and Seaborn.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    generated_files = {}

    sns.set_theme(style="whitegrid", context="notebook")

    # 1. Top 5 cases (Task 13)
    top_cases = df.nlargest(5, "Total Cases")[["Country", "Total Cases"]]
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_cases, x="Total Cases", y="Country", color="#2878B5")
    plt.title("Top 5 Countries by Total COVID-19 Cases", fontsize=14, weight="bold")
    plt.xlabel("Total cases", fontsize=12)
    plt.ylabel("Country", fontsize=12)
    plt.tight_layout()
    f1 = out_path / "01_top_5_cases.png"
    plt.savefig(f1, dpi=200)
    plt.close()
    generated_files["01_top_5_cases"] = str(f1)

    # 2. Lowest 5 cases (Task 15)
    lowest_cases = df.nsmallest(5, "Total Cases")[["Country", "Total Cases"]]
    plt.figure(figsize=(10, 6))
    sns.barplot(data=lowest_cases, x="Total Cases", y="Country", color="#59A14F")
    plt.title("5 Countries with the Lowest Total COVID-19 Cases", fontsize=14, weight="bold")
    plt.xlabel("Total cases", fontsize=12)
    plt.ylabel("Country", fontsize=12)
    plt.tight_layout()
    f2 = out_path / "02_lowest_5_cases.png"
    plt.savefig(f2, dpi=200)
    plt.close()
    generated_files["02_lowest_5_cases"] = str(f2)

    # 3. Top 5 deaths (Task 17)
    top_deaths = df.nlargest(5, "Total Deaths")[["Country", "Total Deaths"]]
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_deaths, x="Total Deaths", y="Country", color="#E15759")
    plt.title("Top 5 Countries by Total COVID-19 Deaths", fontsize=14, weight="bold")
    plt.xlabel("Total deaths", fontsize=12)
    plt.ylabel("Country", fontsize=12)
    plt.tight_layout()
    f3 = out_path / "03_top_5_deaths.png"
    plt.savefig(f3, dpi=200)
    plt.close()
    generated_files["03_top_5_deaths"] = str(f3)

    # 4. Top 5 death percentage (Task 20)
    top_death_pct = df.nlargest(5, "Death percentage")[["Country", "Death percentage"]]
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_death_pct, x="Death percentage", y="Country", color="#F28E2B")
    plt.title("Top 5 Countries by COVID-19 Death Percentage", fontsize=14, weight="bold")
    plt.xlabel("Death percentage (%)", fontsize=12)
    plt.ylabel("Country", fontsize=12)
    plt.tight_layout()
    f4 = out_path / "04_top_5_death_percentage.png"
    plt.savefig(f4, dpi=200)
    plt.close()
    generated_files["04_top_5_death_percentage"] = str(f4)

    # 5. Continent total cases (Task 22)
    continent_cases = df.groupby("Continent")["Total Cases"].sum().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=continent_cases, x="Continent", y="Total Cases", color="#76B7B2")
    plt.title("Total COVID-19 Cases by Continent", fontsize=14, weight="bold")
    plt.xlabel("Continent", fontsize=12)
    plt.ylabel("Total cases", fontsize=12)
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    f5 = out_path / "05_cases_by_continent.png"
    plt.savefig(f5, dpi=200)
    plt.close()
    generated_files["05_cases_by_continent"] = str(f5)

    # 6. Population vs Total Cases (Task 23)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="Population", y="Total Cases", hue="Continent", alpha=0.8)
    plt.title("Population vs Total COVID-19 Cases", fontsize=14, weight="bold")
    plt.xlabel("Population", fontsize=12)
    plt.ylabel("Total cases", fontsize=12)
    plt.legend(title="Continent", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    f6 = out_path / "06_population_vs_cases.png"
    plt.savefig(f6, dpi=200)
    plt.close()
    generated_files["06_population_vs_cases"] = str(f6)

    # 7. Total Cases vs Total Deaths (Task 24)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="Total Cases", y="Total Deaths", hue="Continent", alpha=0.8)
    plt.title("Total COVID-19 Cases vs Total Deaths", fontsize=14, weight="bold")
    plt.xlabel("Total cases", fontsize=12)
    plt.ylabel("Total deaths", fontsize=12)
    plt.legend(title="Continent", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    f7 = out_path / "07_cases_vs_deaths.png"
    plt.savefig(f7, dpi=200)
    plt.close()
    generated_files["07_cases_vs_deaths"] = str(f7)

    # 8. Spearman heatmap (Task 25)
    numeric_df = df.select_dtypes(include=[np.number])
    spearman_corr = numeric_df.corr(method="spearman")
    plt.figure(figsize=(11, 8))
    sns.heatmap(
        spearman_corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
        square=True,
    )
    plt.title("Spearman Rank Correlation Heatmap", fontsize=14, weight="bold")
    plt.tight_layout()
    f8 = out_path / "08_spearman_correlation_heatmap.png"
    plt.savefig(f8, dpi=200)
    plt.close()
    generated_files["08_spearman_correlation_heatmap"] = str(f8)

    return generated_files
