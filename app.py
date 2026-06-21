# ==============================
# TRAFFIC ACCIDENT ANALYSIS DASHBOARD
# PART 1 (Lines 1-300)
# Streamlit + Plotly
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="Traffic Accident Analysis Dashboard",
    page_icon="🚗",
    layout="wide"
)

# ----------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f8f9fa;
}

.metric-card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}

h1,h2,h3 {
    color:#1f2937;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# TITLE
# ----------------------------------------------------

st.title("🚗 Traffic Accident Analysis Dashboard")
st.markdown("---")

# ----------------------------------------------------
# DATA LOADING
# ----------------------------------------------------

@st.cache_data
def load_data(uploaded_file):

    df = pd.read_csv(uploaded_file)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


# ----------------------------------------------------
# FILE UPLOAD
# ----------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload Traffic Accident CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload your traffic accident CSV file.")
    st.stop()

df = load_data(uploaded_file)

# ----------------------------------------------------
# DATA CLEANING
# ----------------------------------------------------

if "crash_date" in df.columns:

    df["crash_date"] = pd.to_datetime(
        df["crash_date"],
        errors="coerce"
    )

# ----------------------------------------------------
# KPI CALCULATIONS
# ----------------------------------------------------

def get_total_accidents():

    return len(df)


def get_total_injuries():

    if "injuries_total" in df.columns:

        return int(
            df["injuries_total"]
            .fillna(0)
            .sum()
        )

    return 0


def get_total_fatalities():

    if "injuries_fatal" in df.columns:

        return int(
            df["injuries_fatal"]
            .fillna(0)
            .sum()
        )

    return 0


def get_avg_units():

    if "num_units" in df.columns:

        return round(
            df["num_units"]
            .fillna(0)
            .mean(),
            2
        )

    return 0


def get_peak_hour():

    if "crash_hour" in df.columns:

        return int(
            df["crash_hour"]
            .mode()[0]
        )

    return "N/A"


def get_top_cause():

    if "prim_contributory_cause" in df.columns:

        return (
            df["prim_contributory_cause"]
            .mode()[0]
        )

    return "N/A"

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

st.sidebar.title("📊 Dashboard Menu")

page = st.sidebar.radio(
    "Select Section",
    [
        "Dashboard Overview",
        "Data Quality Report",
        "Time Analysis",
        "Weather Analysis",
        "Severity Analysis",
        "Cause Analysis",
        "Road Condition Analysis",
        "Crash Type Analysis",
        "Advanced Heatmaps",
        "Correlation Analysis",
        "Export Report"
    ]
)

# ====================================================
# DASHBOARD OVERVIEW
# ====================================================

if page == "Dashboard Overview":

    st.header("📈 Dashboard Overview")

    total_accidents = get_total_accidents()
    total_injuries = get_total_injuries()
    total_fatalities = get_total_fatalities()
    avg_units = get_avg_units()

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Accidents",
            f"{total_accidents:,}"
        )

    with col2:
        st.metric(
            "Total Injuries",
            f"{total_injuries:,}"
        )

    with col3:
        st.metric(
            "Fatalities",
            f"{total_fatalities:,}"
        )

    with col4:
        st.metric(
            "Avg Vehicles",
            avg_units
        )

    st.markdown("---")

    col5,col6 = st.columns(2)

    with col5:

        st.info(
            f"🚨 Most Common Cause: "
            f"{get_top_cause()}"
        )

    with col6:

        st.info(
            f"⏰ Peak Accident Hour: "
            f"{get_peak_hour()}:00"
        )

    st.markdown("---")

    # --------------------------------
    # Top Accident Causes
    # --------------------------------

    if "prim_contributory_cause" in df.columns:

        top_causes = (
            df["prim_contributory_cause"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_causes.columns = [
            "Cause",
            "Count"
        ]

        fig = px.bar(
            top_causes,
            x="Count",
            y="Cause",
            orientation="h",
            title="Top 10 Accident Causes"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------
    # Severity Pie Chart
    # --------------------------------

    if "most_severe_injury" in df.columns:

        severity = (
            df["most_severe_injury"]
            .value_counts()
            .reset_index()
        )

        severity.columns = [
            "Severity",
            "Count"
        ]

        fig = px.pie(
            severity,
            names="Severity",
            values="Count",
            title="Severity Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ====================================================
# DATA QUALITY REPORT
# ====================================================

elif page == "Data Quality Report":

    st.header("🧹 Data Quality Report")

    col1,col2,col3 = st.columns(3)

    with col1:

        st.metric(
            "Rows",
            df.shape[0]
        )

    with col2:

        st.metric(
            "Columns",
            df.shape[1]
        )

    with col3:

        st.metric(
            "Duplicate Rows",
            df.duplicated().sum()
        )

    st.markdown("---")

    st.subheader("Missing Values")

    missing = pd.DataFrame({

        "Column": df.columns,

        "Missing Values":
        df.isnull().sum().values,

        "Missing %":
        (
            df.isnull().sum()
            / len(df)
            * 100
        ).round(2)

    })

    st.dataframe(
        missing,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("Data Types")

    dtypes = pd.DataFrame({

        "Column":
        df.columns,

        "Datatype":
        df.dtypes.astype(str)

    })

    st.dataframe(
        dtypes,
        use_container_width=True
    )

# ====================================================
# TIME ANALYSIS
# ====================================================

elif page == "Time Analysis":

    st.header("⏰ Time Analysis")

    if "crash_hour" in df.columns:

        hourly = (
            df["crash_hour"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        hourly.columns = [
            "Hour",
            "Accidents"
        ]

        fig = px.line(
            hourly,
            x="Hour",
            y="Accidents",
            markers=True,
            title="Accidents by Hour"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "crash_day_of_week" in df.columns:

        daily = (
            df["crash_day_of_week"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        daily.columns = [
            "Day",
            "Accidents"
        ]

        fig = px.bar(
            daily,
            x="Day",
            y="Accidents",
            title="Accidents by Day"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "crash_month" in df.columns:

        monthly = (
            df["crash_month"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        monthly.columns = [
            "Month",
            "Accidents"
        ]

        fig = px.line(
            monthly,
            x="Month",
            y="Accidents",
            markers=True,
            title="Monthly Accident Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        # ====================================================
# WEATHER ANALYSIS
# ====================================================

elif page == "Weather Analysis":

    st.header("🌦 Weather Analysis")

    if "weather_condition" in df.columns:

        weather = (
            df["weather_condition"]
            .fillna("Unknown")
            .value_counts()
            .head(15)
            .reset_index()
        )

        weather.columns = [
            "Weather",
            "Accidents"
        ]

        fig = px.bar(
            weather,
            x="Accidents",
            y="Weather",
            orientation="h",
            title="Top Weather Conditions"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig2 = px.pie(
            weather,
            names="Weather",
            values="Accidents",
            title="Weather Distribution"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ====================================================
# SEVERITY ANALYSIS
# ====================================================

elif page == "Severity Analysis":

    st.header("🚨 Severity Analysis")

    if "most_severe_injury" in df.columns:

        severity = (
            df["most_severe_injury"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        severity.columns = [
            "Severity",
            "Count"
        ]

        fig = px.bar(
            severity,
            x="Severity",
            y="Count",
            title="Severity Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig2 = px.pie(
            severity,
            names="Severity",
            values="Count",
            title="Severity Share"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ====================================================
# CAUSE ANALYSIS
# ====================================================

elif page == "Cause Analysis":

    st.header("💥 Cause Analysis")

    if "prim_contributory_cause" in df.columns:

        cause = (
            df["prim_contributory_cause"]
            .fillna("Unknown")
            .value_counts()
            .head(15)
            .reset_index()
        )

        cause.columns = [
            "Cause",
            "Count"
        ]

        fig = px.bar(
            cause,
            x="Count",
            y="Cause",
            orientation="h",
            title="Top 15 Accident Causes"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ====================================================
# ROAD CONDITION ANALYSIS
# ====================================================

elif page == "Road Condition Analysis":

    st.header("🛣 Road Condition Analysis")

    if "roadway_surface_cond" in df.columns:

        road = (
            df["roadway_surface_cond"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        road.columns = [
            "Road Condition",
            "Count"
        ]

        fig = px.bar(
            road,
            x="Road Condition",
            y="Count",
            title="Road Surface Condition"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ====================================================
# CRASH TYPE ANALYSIS
# ====================================================

elif page == "Crash Type Analysis":

    st.header("🚗 Crash Type Analysis")

    if "first_crash_type" in df.columns:

        crash = (
            df["first_crash_type"]
            .fillna("Unknown")
            .value_counts()
            .head(15)
            .reset_index()
        )

        crash.columns = [
            "Crash Type",
            "Count"
        ]

        fig = px.bar(
            crash,
            x="Count",
            y="Crash Type",
            orientation="h",
            title="Top Crash Types"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ====================================================
# ADVANCED HEATMAPS
# ====================================================

elif page == "Advanced Heatmaps":

    st.header("🔥 Advanced Heatmaps")

    # Hour vs Day

    if (
        "crash_hour" in df.columns
        and
        "crash_day_of_week" in df.columns
    ):

        heat = pd.crosstab(
            df["crash_day_of_week"],
            df["crash_hour"]
        )

        fig = px.imshow(
            heat,
            aspect="auto",
            title="Hour vs Day Heatmap"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Cause vs Severity

    if (
        "prim_contributory_cause" in df.columns
        and
        "most_severe_injury" in df.columns
    ):

        cause_sev = pd.crosstab(
            df["prim_contributory_cause"],
            df["most_severe_injury"]
        )

        cause_sev = cause_sev.head(15)

        fig2 = px.imshow(
            cause_sev,
            aspect="auto",
            title="Cause vs Severity"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ====================================================
# CORRELATION ANALYSIS
# ====================================================

elif page == "Correlation Analysis":

    st.header("📊 Correlation Analysis")

    numeric_df = df.select_dtypes(
        include=np.number
    )

    if len(numeric_df.columns) > 1:

        corr = numeric_df.corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            title="Correlation Matrix"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            corr,
            use_container_width=True
        )

# ====================================================
# EXPORT REPORT
# ====================================================

elif page == "Export Report":

    st.header("📥 Export Excel Report")

    summary = pd.DataFrame({

        "Metric": [

            "Total Accidents",
            "Total Injuries",
            "Fatalities",
            "Average Vehicles",
            "Peak Hour"

        ],

        "Value": [

            get_total_accidents(),
            get_total_injuries(),
            get_total_fatalities(),
            get_avg_units(),
            get_peak_hour()

        ]
    })

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        if "prim_contributory_cause" in df.columns:

            (
                df["prim_contributory_cause"]
                .value_counts()
                .reset_index()
            ).to_excel(
                writer,
                sheet_name="Top Causes",
                index=False
            )

        if "weather_condition" in df.columns:

            (
                df["weather_condition"]
                .value_counts()
                .reset_index()
            ).to_excel(
                writer,
                sheet_name="Weather Analysis",
                index=False
            )

        if "most_severe_injury" in df.columns:

            (
                df["most_severe_injury"]
                .value_counts()
                .reset_index()
            ).to_excel(
                writer,
                sheet_name="Severity Analysis",
                index=False
            )

    st.success(
        "Report Ready!"
    )

    st.download_button(
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name="traffic_analysis_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ====================================================
# FOOTER
# ====================================================

st.markdown("---")

st.caption(
    "Traffic Accident Analysis Dashboard | Streamlit + Plotly + Pandas"
)
