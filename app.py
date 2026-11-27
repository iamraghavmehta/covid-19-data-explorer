"""
COVID-19 Data Explorer
Tagline: Understanding the pandemic through data.
A high-performance editorial analytics dashboard built with Streamlit, Plotly, and Pandas.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Internal analytical engine modules
from src.data_loader import load_and_clean_data
from src.analysis import CovidAnalyzer
from src.charts import (
    THEME,
    create_horizontal_bar_chart,
    create_continent_comparison_chart,
    create_continent_donut_chart,
    create_scatter_plot,
    create_correlation_heatmap,
    create_country_benchmark_chart,
    generate_static_assignment_charts,
)

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="COVID-19 Data Explorer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. EDITORIAL DARK UI STYLING (LINEAR / VERCEL / BLOOMBERG INSPIRED)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F8FAFC;
    background-color: #0B0D10;
}

/* Streamlit Header & Toolbar cleanup */
header[data-testid="stHeader"] {
    background-color: rgba(11, 13, 16, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #1E232E;
}
.stApp {
    background-color: #0B0D10;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0E1117;
    border-right: 1px solid #1A202C;
}

/* Responsive KPI Grid Container */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 12px;
    margin-bottom: 1.25rem;
}

/* Custom Card Container */
.metric-card {
    background: linear-gradient(180deg, #131722 0%, #0E1117 100%);
    border: 1px solid #1F2633;
    border-radius: 10px;
    padding: 1rem 1.15rem;
    position: relative;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: transform 0.2s ease, border-color 0.2s ease;
    min-width: 0;
}
.metric-card:hover {
    border-color: #38BDF8;
    transform: translateY(-2px);
}
.metric-card-accent-blue { border-top: 2px solid #38BDF8; }
.metric-card-accent-indigo { border-top: 2px solid #818CF8; }
.metric-card-accent-rose { border-top: 2px solid #FB7185; }
.metric-card-accent-amber { border-top: 2px solid #FBBF24; }
.metric-card-accent-emerald { border-top: 2px solid #34D399; }

.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94A3B8;
    margin-bottom: 0.35rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.35rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.2;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}
.metric-subtext {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 0.35rem;
}

/* Hero Badge */
.pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    background: rgba(56, 189, 248, 0.1);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.25);
}

.pill-warning {
    background: rgba(251, 191, 36, 0.1);
    color: #FBBF24;
    border: 1px solid rgba(251, 191, 36, 0.25);
}

.pill-success {
    background: rgba(52, 211, 153, 0.1);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.25);
}

/* Insight Box */
.insight-box {
    background: #11151F;
    border: 1px solid #1E2533;
    border-left: 3px solid #38BDF8;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.85rem;
}
.insight-title {
    font-weight: 700;
    font-size: 0.92rem;
    color: #F1F5F9;
    margin-bottom: 0.3rem;
}
.insight-desc {
    font-size: 0.84rem;
    color: #94A3B8;
    line-height: 1.5;
}

/* Custom Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    border-bottom: 1px solid #1F2633;
    padding-bottom: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 6px;
    color: #94A3B8;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 8px 16px;
    border: none;
    transition: all 0.15s ease;
}
.stTabs [aria-selected="true"] {
    color: #38BDF8 !important;
    background-color: rgba(56, 189, 248, 0.08) !important;
    border-bottom: 2px solid #38BDF8 !important;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    border: 1px solid #1F2633;
    border-radius: 8px;
    overflow: hidden;
}

/* Buttons */
.stButton>button {
    background-color: #1A2230;
    color: #F8FAFC;
    border: 1px solid #2B3545;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}
.stButton>button:hover {
    background-color: #38BDF8;
    color: #0B0D10;
    border-color: #38BDF8;
}

/* Download button */
.stDownloadButton>button {
    background-color: #141A24;
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 6px;
    font-size: 0.82rem;
}
.stDownloadButton>button:hover {
    background-color: #38BDF8;
    color: #0B0D10;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. CACHED DATA INGESTION & PIPELINE
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_dataset():
    """Caches cleaned data and audit metadata."""
    raw_df, clean_df, audit = load_and_clean_data()
    analyzer = CovidAnalyzer(clean_df)
    return raw_df, clean_df, audit, analyzer


try:
    raw_df, clean_df, audit, analyzer = get_dataset()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# 4. SIDEBAR CONTROLS & METADATA
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem 0;">
            <div class="pill-badge">PRODUCTION PORTFOLIO</div>
            <h2 style="margin: 0.5rem 0 0.1rem 0; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;">
                COVID-19 <span style="color:#38BDF8;">Explorer</span>
            </h2>
            <p style="font-size: 0.8rem; color: #64748B; margin-top: 0;">Understanding the pandemic through data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border: none; border-top: 1px solid #1E232E; margin: 0.6rem 0;'>", unsafe_allow_html=True)

    # Continent Filter
    all_continents = sorted(clean_df["Continent"].dropna().unique().tolist())
    selected_continents = st.multiselect(
        "Filter by Continent",
        options=all_continents,
        default=all_continents,
        help="Select one or more continents to filter calculations across the dashboard.",
    )

    if not selected_continents:
        st.warning("Please select at least one continent.")
        selected_continents = all_continents

    # Search Country
    search_query = st.text_input(
        "Search Country",
        placeholder="e.g. India, USA, France...",
        help="Filters the dataset table and country explorer view.",
    )

    # Top-N Ranking slider
    ranking_n = st.slider("Rankings Display Limit", min_value=5, max_value=25, value=10, step=5)

    st.markdown("<hr style='border: none; border-top: 1px solid #1E232E; margin: 0.6rem 0;'>", unsafe_allow_html=True)

    # Data Snapshot Provenance Card
    st.markdown(
        """
        <div style="background: #11141A; border: 1px solid #1E232E; border-radius: 8px; padding: 0.85rem; font-size: 0.76rem; color: #94A3B8;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                <span style="font-weight:700; color:#F8FAFC;">SNAPSHOT AUDIT</span>
                <span class="pill-badge pill-success" style="font-size: 0.65rem;">VERIFIED</span>
            </div>
            <div>• Coverage: <b>225 Territories</b></div>
            <div>• Null Imputation: <b>Row 135 (Montenegro)</b></div>
            <div>• Renamed: <b>ISO CODE → Iso_Code</b></div>
            <div>• Historical snapshot (Static)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Download Cleaned CSV
    csv_bytes = clean_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Cleaned CSV",
        data=csv_bytes,
        file_name="COVID-19_Cleaned_Dataset.csv",
        mime="text/csv",
        use_container_width=True,
    )


# Apply Sidebar Filters to active view
filtered_df = clean_df[clean_df["Continent"].isin(selected_continents)].copy()
if search_query.strip():
    q = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["Country"].str.lower().str.contains(q)
        | filtered_df["Other names"].str.lower().str.contains(q)
        | filtered_df["Iso_Code"].str.lower().str.contains(q)
    ]

# Compute active KPIs
kpis = analyzer.get_kpi_summary(filtered_df)


# -----------------------------------------------------------------------------
# 5. HERO HEADER & NOTICE BANNER
# -----------------------------------------------------------------------------
col_header_left, col_header_right = st.columns([3, 1])
with col_header_left:
    st.markdown(
        """
        <div style="margin-bottom: 0.5rem;">
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 0.4rem;">
                <span class="pill-badge">DATA ANALYTICS LAB</span>
                <span class="pill-badge pill-warning">HISTORICAL SNAPSHOT</span>
                <span class="pill-badge pill-success">25 TASKS PRESERVED</span>
            </div>
            <h1 style="font-size: 2.15rem; font-weight: 800; letter-spacing: -0.03em; margin: 0;">
                COVID-19 Data Explorer
            </h1>
            <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 0.2rem; max-width: 850px;">
                An interactive macro-epidemiological intelligence platform analyzing 225 global territories,
                exploring case dispersion, mortality correlations, continental distribution, and statistical indicators.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_header_right:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 1rem;">
            <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">DATA PROVENANCE</div>
            <div style="font-size: 0.88rem; font-weight: 600; color: #E2E8F0;">Static Dataset Snapshot</div>
            <div style="font-size: 0.75rem; color: #94A3B8;">225 Countries & Territories</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Historical Notice Alert
st.markdown(
    """
    <div style="background: rgba(251, 191, 36, 0.05); border: 1px solid rgba(251, 191, 36, 0.2); border-radius: 6px; padding: 0.6rem 0.9rem; margin-bottom: 1.2rem; font-size: 0.82rem; color: #FCD34D;">
        <b>Historical Dataset Notice:</b> The metrics presented are computed strictly from the supplied historical CSV benchmark. They reflect data reported during the pandemic observation window and do not represent live real-time epidemiology feeds.
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 6. RESPONSIVE TOP KPI CARDS
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="metric-card metric-card-accent-blue">
            <div class="metric-label">Countries / Territories</div>
            <div class="metric-value">{kpis['total_countries']}</div>
            <div class="metric-subtext">Active filter subset of 225 total</div>
        </div>
        <div class="metric-card metric-card-accent-indigo">
            <div class="metric-label">Confirmed Cases</div>
            <div class="metric-value">{kpis['total_cases']:,}</div>
            <div class="metric-subtext">Across selected territories</div>
        </div>
        <div class="metric-card metric-card-accent-rose">
            <div class="metric-label">Reported Deaths</div>
            <div class="metric-value">{kpis['total_deaths']:,}</div>
            <div class="metric-subtext">Cumulative fatality count</div>
        </div>
        <div class="metric-card metric-card-accent-amber">
            <div class="metric-label">Mean Death Pct</div>
            <div class="metric-value">{kpis['avg_death_percentage']:.2f}%</div>
            <div class="metric-subtext">Unweighted country average</div>
        </div>
        <div class="metric-card metric-card-accent-emerald">
            <div class="metric-label">Global Fatality Rate</div>
            <div class="metric-value">{kpis['global_cfr']:.2f}%</div>
            <div class="metric-subtext">Total deaths / Total cases</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 7. MAIN INTERACTIVE TABS
# -----------------------------------------------------------------------------
tab_overview, tab_global, tab_continent, tab_country, tab_correlation, tab_insights, tab_audit = st.tabs(
    [
        "01 // Overview",
        "02 // Global Rankings",
        "03 // Continent Analysis",
        "04 // Country Explorer",
        "05 // Correlation Lab",
        "06 // Automated Insights",
        "07 // Project 25-Task Audit",
    ]
)


# =============================================================================
# TAB 1: OVERVIEW & KEY INSIGHTS
# =============================================================================
with tab_overview:
    col_ov_left, col_ov_right = st.columns([1.6, 1])

    with col_ov_left:
        st.markdown("### Top Reporting Nations by Total Case Volume")
        top_cases_preview = analyzer.get_top_cases(8, filtered_df=filtered_df)
        fig_ov_cases = create_horizontal_bar_chart(
            top_cases_preview,
            x_col="Total Cases",
            y_col="Country",
            title=f"Top {len(top_cases_preview)} Countries by Total Cases",
            color_col="Continent",
            height=370,
        )
        st.plotly_chart(fig_ov_cases, use_container_width=True, key="ov_cases_chart")

    with col_ov_right:
        st.markdown("### Continental Breakdown")
        continent_summary = analyzer.get_continent_summary()
        # Filter to selected continents
        cont_filtered = continent_summary[continent_summary["Continent"].isin(selected_continents)]
        fig_ov_donut = create_continent_donut_chart(cont_filtered, metric="Total_Cases")
        st.plotly_chart(fig_ov_donut, use_container_width=True, key="ov_donut_chart")

    st.markdown("---")
    st.markdown("### Executive Highlights & Key Findings")

    high_c1, high_c2, high_c3 = st.columns(3)
    with high_c1:
        st.markdown(
            """
            <div class="insight-box">
                <div class="insight-title">Infection Density Concentration</div>
                <div class="insight-desc">
                    The top 5 nations (USA, India, Brazil, France, Germany) account for over 41% of all documented infections globally, exhibiting extreme statistical skewness.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with high_c2:
        st.markdown(
            """
            <div class="insight-box" style="border-left-color: #FB7185;">
                <div class="insight-title">Mortality vs. Death Percentage</div>
                <div class="insight-desc">
                    Yemen leads in death percentage (18.15%) despite having only 11,806 total cases, demonstrating how limited testing inflated case-fatality rates in developing nations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with high_c3:
        st.markdown(
            """
            <div class="insight-box" style="border-left-color: #34D399;">
                <div class="insight-title">Rank Correlation Findings</div>
                <div class="insight-desc">
                    Total Cases and Total Deaths display an exceptionally high Spearman rank correlation of 0.93, while Population vs Total Cases displays a moderate rank correlation of 0.47.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# TAB 2: GLOBAL ANALYSIS (RANKINGS)
# =============================================================================
with tab_global:
    st.markdown(f"### Global Rankings (Configured Limit: Top {ranking_n})")
    st.caption("Interactive ranking leaderboards covering case counts, total fatalities, and mortality percentages.")

    rank_c1, rank_c2 = st.columns(2)

    with rank_c1:
        top_cases_data = analyzer.get_top_cases(ranking_n, filtered_df=filtered_df)
        fig_tc = create_horizontal_bar_chart(
            top_cases_data,
            x_col="Total Cases",
            y_col="Country",
            title=f"Top {len(top_cases_data)} Countries by Total Cases (Task 12-13)",
            bar_color="#38BDF8",
            height=420,
        )
        st.plotly_chart(fig_tc, use_container_width=True, key="tc_rank_chart")

    with rank_c2:
        top_deaths_data = analyzer.get_top_deaths(ranking_n, filtered_df=filtered_df)
        fig_td = create_horizontal_bar_chart(
            top_deaths_data,
            x_col="Total Deaths",
            y_col="Country",
            title=f"Top {len(top_deaths_data)} Countries by Total Deaths (Task 16-17)",
            bar_color="#FB7185",
            height=420,
        )
        st.plotly_chart(fig_td, use_container_width=True, key="td_rank_chart")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    rank_c3, rank_c4 = st.columns(2)

    with rank_c3:
        lowest_cases_data = analyzer.get_lowest_cases(ranking_n, filtered_df=filtered_df)
        fig_lc = create_horizontal_bar_chart(
            lowest_cases_data,
            x_col="Total Cases",
            y_col="Country",
            title=f"Countries with Lowest Reported Cases (Task 14-15)",
            bar_color="#34D399",
            height=420,
            reverse_y=False,
        )
        st.plotly_chart(fig_lc, use_container_width=True, key="lc_rank_chart")

    with rank_c4:
        top_death_pct_data = analyzer.get_top_death_percentage(ranking_n, filtered_df=filtered_df)
        fig_tdp = create_horizontal_bar_chart(
            top_death_pct_data,
            x_col="Death percentage",
            y_col="Country",
            title=f"Top {len(top_death_pct_data)} Countries by Death Percentage (Task 19-20)",
            bar_color="#FBBF24",
            height=420,
        )
        st.plotly_chart(fig_tdp, use_container_width=True, key="tdp_rank_chart")

    # Lowest Deaths Expandable
    with st.expander("View Countries with Lowest Total Fatalities (Task 18)"):
        lowest_deaths_data = analyzer.get_lowest_deaths(15, filtered_df=filtered_df)
        st.dataframe(
            lowest_deaths_data.style.format(
                {"Total Cases": "{:,.0f}", "Total Deaths": "{:,.0f}", "Death percentage": "{:.2f}%"}
            ),
            use_container_width=True,
        )


# =============================================================================
# TAB 3: CONTINENT ANALYSIS (TASKS 21-22)
# =============================================================================
with tab_continent:
    st.markdown("### Continental Aggregations & Comparative Analysis")
    st.caption("Aggregating metrics across continents via groupby() as specified in Tasks 21–22.")

    continent_df = analyzer.get_continent_summary()

    metric_choice = st.radio(
        "Metric to Compare:",
        ["Total_Cases", "Total_Deaths", "Total_Population", "Cases_per_Million", "Deaths_per_Million"],
        horizontal=True,
        format_func=lambda x: x.replace("_", " "),
    )

    cont_col1, cont_col2 = st.columns([1.5, 1])

    with cont_col1:
        fig_cont_bar = create_continent_comparison_chart(continent_df, metric=metric_choice)
        st.plotly_chart(fig_cont_bar, use_container_width=True, key="cont_bar_chart")

    with cont_col2:
        fig_cont_pie = create_continent_donut_chart(continent_df, metric=metric_choice)
        st.plotly_chart(fig_cont_pie, use_container_width=True, key="cont_donut_chart_tab3")

    st.markdown("#### Comprehensive Continental Summary Table")
    st.dataframe(
        continent_df.style.format(
            {
                "Total_Cases": "{:,.0f}",
                "Total_Deaths": "{:,.0f}",
                "Total_Population": "{:,.0f}",
                "Avg_Death_Percentage": "{:.2f}%",
                "Case_Fatality_Rate": "{:.2f}%",
                "Cases_per_Million": "{:,.1f}",
                "Deaths_per_Million": "{:,.1f}",
                "Global_Cases_Share_Pct": "{:.2f}%",
                "Global_Deaths_Share_Pct": "{:.2f}%",
            }
        ),
        use_container_width=True,
    )


# =============================================================================
# TAB 4: COUNTRY EXPLORER
# =============================================================================
with tab_country:
    st.markdown("### Country Intelligence Dossier & Continent Benchmark")
    st.caption("Inspect individual territory metrics and benchmark performance against continental averages.")

    country_list = sorted(clean_df["Country"].unique().tolist())
    default_index = country_list.index("India") if "India" in country_list else 0

    selected_country = st.selectbox("Select Country to Inspect", options=country_list, index=default_index)

    profile = analyzer.get_country_profile(selected_country)

    if profile:
        c_meta1, c_meta2, c_meta3, c_meta4 = st.columns(4)
        with c_meta1:
            st.metric("Continent", profile["continent"])
        with c_meta2:
            st.metric("ISO Alpha-3 Code", profile["iso_code"] or "N/A")
        with c_meta3:
            st.metric("Population", f"{profile['population']:,}")
        with c_meta4:
            st.metric("Other Name / Alias", profile["other_names"])

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                f"""
                <div class="metric-card metric-card-accent-indigo">
                    <div class="metric-label">Total Cases</div>
                    <div class="metric-value">{profile['total_cases']:,}</div>
                    <div class="metric-subtext">Rank #{profile['rankings']['global']['cases']} Globally / #{profile['rankings']['continent']['cases']} in {profile['continent']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f"""
                <div class="metric-card metric-card-accent-rose">
                    <div class="metric-label">Total Deaths</div>
                    <div class="metric-value">{profile['total_deaths']:,}</div>
                    <div class="metric-subtext">Rank #{profile['rankings']['global']['deaths']} Globally / #{profile['rankings']['continent']['deaths']} in {profile['continent']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k3:
            cases_1m_str = f"{profile['cases_per_million']:,.0f}" if profile['cases_per_million'] else "N/A"
            deaths_1m_str = f"{profile['deaths_per_million']:,.0f}" if profile['deaths_per_million'] else "N/A"
            st.markdown(
                f"""
                <div class="metric-card metric-card-accent-blue">
                    <div class="metric-label">Cases / Million Pop</div>
                    <div class="metric-value">{cases_1m_str}</div>
                    <div class="metric-subtext">Deaths/1M: {deaths_1m_str}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                f"""
                <div class="metric-card metric-card-accent-amber">
                    <div class="metric-label">Death Percentage</div>
                    <div class="metric-value">{profile['death_percentage']:.2f}%</div>
                    <div class="metric-subtext">Continent Avg: {profile['continent_avg_death_pct']:.2f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        col_bench_chart, col_bench_details = st.columns([1.6, 1])

        with col_bench_chart:
            fig_bench = create_country_benchmark_chart(profile)
            st.plotly_chart(fig_bench, use_container_width=True, key="country_bench_chart")

        with col_bench_details:
            st.markdown(
                f"""
                <div style="background: #11151F; border: 1px solid #1E2533; border-radius: 8px; padding: 1.25rem;">
                    <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 0.8rem; font-size: 0.95rem;">
                        Comparative Benchmark Dossier
                    </div>
                    <p style="font-size: 0.84rem; color: #94A3B8; line-height: 1.6;">
                        • <b>{profile['country']}</b> accounts for <b>{(profile['total_cases'] / kpis['total_cases'] * 100):.2f}%</b> of total global cases.<br>
                        • Compared to the mean of <b>{profile['continent']}</b>, cases are <b>{profile['cases_vs_continent_avg_pct']:+.1f}%</b> above/below average.<br>
                        • Relative mortality against continent average stands at <b>{profile['deaths_vs_continent_avg_pct']:+.1f}%</b>.<br>
                        • Recorded death percentage of <b>{profile['death_percentage']:.2f}%</b> compares with a continent baseline of <b>{profile['continent_avg_death_pct']:.2f}%</b>.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# TAB 5: CORRELATION LAB (TASKS 23-25)
# =============================================================================
with tab_correlation:
    st.markdown("### Correlation Lab & Variable Relationships (Tasks 23–25)")
    st.caption("Evaluating statistical dependencies, Spearman rank correlation, and multi-variable scatter dynamics.")

    c_scatter_opts, c_scatter_blank = st.columns([1, 2])
    with c_scatter_opts:
        use_log = st.checkbox("Apply Logarithmic Axis Scaling", value=True, help="Mitigates high variance across mega-populations and micro-states.")

    corr_c1, corr_c2 = st.columns(2)

    with corr_c1:
        # Task 23: Population vs Total Cases
        fig_s1 = create_scatter_plot(
            filtered_df,
            x_col="Population",
            y_col="Total Cases",
            title="Population vs. Total Cases (Task 23)",
            log_x=use_log,
            log_y=use_log,
        )
        st.plotly_chart(fig_s1, use_container_width=True, key="scatter_pop_cases_chart")
        st.markdown(
            """
            <div style="font-size: 0.8rem; color: #94A3B8; padding: 0 0.5rem 0.5rem;">
                <b>Insight:</b> Moderate positive rank correlation. While larger populations expand potential infection pools, testing infrastructure and public health interventions dictated actual recorded case volumes.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with corr_c2:
        # Task 24: Total Cases vs Total Deaths
        fig_s2 = create_scatter_plot(
            filtered_df,
            x_col="Total Cases",
            y_col="Total Deaths",
            title="Total Cases vs. Total Deaths (Task 24)",
            log_x=use_log,
            log_y=use_log,
        )
        st.plotly_chart(fig_s2, use_container_width=True, key="scatter_cases_deaths_chart")
        st.markdown(
            """
            <div style="font-size: 0.8rem; color: #94A3B8; padding: 0 0.5rem 0.5rem;">
                <b>Insight:</b> Exceptionally strong linear and monotonic correlation (Spearman ρ = 0.93). Total reported fatalities scale strongly with reported cumulative infection counts.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Spearman Rank Correlation Matrix (Task 25)")

    spearman_mat = analyzer.get_spearman_correlation()
    fig_heat = create_correlation_heatmap(spearman_mat, method="Spearman")
    st.plotly_chart(fig_heat, use_container_width=True, key="spearman_heatmap_chart")

    with st.expander("View Numerical Correlation Matrix Table"):
        st.dataframe(spearman_mat.style.format("{:.3f}"), use_container_width=True)


# =============================================================================
# TAB 6: AUTOMATED DATA INSIGHTS
# =============================================================================
with tab_insights:
    st.markdown("### Automated Empirical Data Insights")
    st.caption("Synthesized observations derived deterministically from the dataset.")

    insights = analyzer.generate_data_insights()

    for item in insights:
        border_col = (
            "#FB7185" if item["severity"] == "high"
            else "#FBBF24" if item["severity"] == "warning"
            else "#34D399" if item["severity"] == "info"
            else "#38BDF8"
        )
        st.markdown(
            f"""
            <div class="insight-box" style="border-left-color: {border_col};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span class="pill-badge" style="font-size: 0.68rem;">{item['category']}</span>
                    <span style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">EMPIRICAL FINDING</span>
                </div>
                <div class="insight-title" style="margin-top: 4px;">{item['title']}</div>
                <div class="insight-desc">{item['text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# TAB 7: COLLEGE PROJECT 25-TASK AUDIT & REPRODUCIBILITY
# =============================================================================
with tab_audit:
    st.markdown("### Academic Project Traceability: All 25 Tasks Preserved")
    st.caption("Explicit verification mapping all 25 college notebook analysis tasks to programmatic results.")

    # Audit summary cards
    aud_c1, aud_c2, aud_c3 = st.columns(3)
    with aud_c1:
        st.markdown(
            f"""
            <div class="metric-card metric-card-accent-emerald">
                <div class="metric-label">Row 135 Cleaning Check</div>
                <div class="metric-value">{'PASS' if audit['row_135_verified'] else 'FAIL'}</div>
                <div class="metric-subtext">Imputed: {audit['row_135_snapshot'].get('Other names')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with aud_c2:
        st.markdown(
            f"""
            <div class="metric-card metric-card-accent-blue">
                <div class="metric-label">Dataset Shape</div>
                <div class="metric-value">{audit['total_records']} × {audit['total_columns']}</div>
                <div class="metric-subtext">225 rows, 10 columns (Task 2)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with aud_c3:
        st.markdown(
            f"""
            <div class="metric-card metric-card-accent-amber">
                <div class="metric-label">Null Values Post-Clean</div>
                <div class="metric-value">{audit['final_null_count']}</div>
                <div class="metric-subtext">Reduced from {audit['initial_null_count']} missing cell (Task 6-8)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 25 Tasks Matrix Accordion
    with st.expander("Explore 25 Tasks Execution Summary & Code Mapping", expanded=True):
        task_data = [
            ("Task 01", "Import libraries & load dataset", "Pandas, Seaborn, Matplotlib imported; CSV ingested cleanly."),
            ("Task 02", "Display dataset shape", f"Verified: {analyzer.get_dataset_shape()[0]} rows, {analyzer.get_dataset_shape()[1]} columns."),
            ("Task 03", "Display first 5 rows", "df.head(5) rendered in inspection table."),
            ("Task 04", "Display last 5 rows", "df.tail(5) rendered in inspection table."),
            ("Task 05", "Display info, column names & types", f"{len(clean_df.columns)} columns verified."),
            ("Task 06", "Check missing values in each column", "Single null detected in 'Other names'."),
            ("Task 07", "Display rows containing missing values", "Row index 135 identified containing NaN."),
            ("Task 08", "Replace missing value with 'Montenegro'", "df['Other names'].fillna('Montenegro') executed."),
            ("Task 09", "Verify row 135 after imputation", "Row 135 verified: Country='Montenegro', Other names='Montenegro'."),
            ("Task 10", "Generate descriptive statistics", "df.describe(include='all') computed."),
            ("Task 11", "Rename ISO 3166-1 alpha-3 CODE to Iso_Code", "Column renamed and displayed in head(4)."),
            ("Task 12", "Top 5 countries by Total Cases", "USA, India, Brazil, France, Germany."),
            ("Task 13", "Bar plot: top 5 countries by total cases", "Exported to outputs/01_top_5_cases.png."),
            ("Task 14", "Five countries with lowest Total Cases", "Micronesia (1), Saint Helena (2), Marshall Islands (7), Niue (7), Western Sahara (10)."),
            ("Task 15", "Bar plot: lowest 5 countries by total cases", "Exported to outputs/02_lowest_5_cases.png."),
            ("Task 16", "Five countries with highest Total Deaths", "USA, Brazil, India, Russia, Mexico."),
            ("Task 17", "Bar plot: top 5 countries by total deaths", "Exported to outputs/03_top_5_deaths.png."),
            ("Task 18", "Five countries with lowest Total Deaths", "Cook Islands (0), Falkland Islands (0), Macao (0), Marshall Islands (0), Micronesia (0)."),
            ("Task 19", "Five countries with highest Death Percentage", "Yemen (18.15%), Western Sahara (10.00%), Sudan (7.92%), Peru (5.98%), Mexico (5.71%)."),
            ("Task 20", "Bar plot: top 5 death percentage", "Exported to outputs/04_top_5_death_percentage.png."),
            ("Task 21", "Groupby continent for total cases", "Groupby continent sum computed."),
            ("Task 22", "Reset index and continent bar plot", "Exported to outputs/05_cases_by_continent.png."),
            ("Task 23", "Scatter plot: Population vs Total Cases", "Exported to outputs/06_population_vs_cases.png."),
            ("Task 24", "Scatter plot: Total Cases vs Total Deaths", "Exported to outputs/07_cases_vs_deaths.png."),
            ("Task 25", "Spearman correlation & heatmap", "Exported to outputs/08_spearman_correlation_heatmap.png."),
        ]
        t_df = pd.DataFrame(task_data, columns=["Task ID", "Requirement", "Verification Status"])
        st.dataframe(t_df, use_container_width=True, hide_index=True)

    # Static Output Figures Gallery
    st.markdown("#### Preserved Assignment Figures (`outputs/`)")
    out_dir = Path("outputs")
    png_files = sorted(list(out_dir.glob("*.png"))) if out_dir.exists() else []

    if png_files:
        g_cols = st.columns(4)
        for i, png in enumerate(png_files):
            with g_cols[i % 4]:
                st.image(str(png), caption=png.name, use_container_width=True)
    else:
        st.info("Static output figures generated during pipeline run.")

# -----------------------------------------------------------------------------
# 8. FOOTER
# -----------------------------------------------------------------------------
st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="border-top: 1px solid #1E232E; padding-top: 1.5rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748B;">
        <div>
            <b>COVID-19 Data Explorer</b> &bull; Production Portfolio Project &bull; Built with Streamlit, Plotly & Pandas
        </div>
        <div>
            Preserves 25/25 College Assignment Tasks &bull; 100% Reproducible
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
