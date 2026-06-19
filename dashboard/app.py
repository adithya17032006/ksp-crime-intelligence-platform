import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
from datetime import datetime, timedelta

# Import the API client and config settings
from api_client import KSPAPIClient
from config import API_BASE_URL

# ----------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="KSP Crime Intelligence Platform",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Custom CSS Styles
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* Main layout adjustment */
    .reportview-container .main .block-container {
        padding-top: 1.5rem;
    }
    
    /* Custom fonts */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hide Streamlit footer and menu for cleaner presentation */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hover micro-animation for metric cards */
    .metric-card-hover {
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .metric-card-hover:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# 3. Sidebar Configuration, Status Indicators & API Client
# ----------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 15px 0 5px 0;">
    <h2 style="color: #eab308; font-size: 20px; font-weight: 800; margin: 0; font-family: 'Outfit';">KSP INTELLIGENCE</h2>
    <p style="color: #94a3b8; font-size: 12px; margin: 0;">Command Portal v2.5</p>
</div>
<hr style="margin-top: 10px; margin-bottom: 20px; border-color: #334155;" />
""", unsafe_allow_html=True)

# 3.1 Connection settings for backend API microservices
st.sidebar.subheader("🔌 API Port Connections")
api_host = st.sidebar.text_input("Target API Host", API_BASE_URL, key="api_host_setting")

# Instantiate central API client
api_client = KSPAPIClient(base_url=api_host)

# 3.2 Backend Status Indicator
api_connected = api_client.check_health()
if api_connected:
    st.sidebar.markdown("""
    <div style="background-color: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; color: #10b981; font-size: 13px; margin-bottom: 15px;">
        🟢 connected
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; color: #ef4444; font-size: 13px; margin-bottom: 15px;">
        🔴 offline / csv fallback
    </div>
    """, unsafe_allow_html=True)

# 3.3 Refresh Data Button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("<hr style='border-color: #334155; margin: 15px 0;' />", unsafe_allow_html=True)

# 3.4 Main Navigation Menu (Matching exactly the requested dashboards + upcoming placeholders)
st.sidebar.subheader("🧭 Navigation Menu")
page = st.sidebar.radio(
    "Select System Module",
    [
        "📊 Executive Dashboard",
        "⚠️ Crime Risk Dashboard",
        "🔥 Hotspot Intelligence Dashboard",
        "🛡️ Patrol Recommendation Dashboard",
        "📅 Temporal Trend Dashboard",
        "📍 GIS Map Dashboard",
        "🔮 Crime Prediction (Upcoming)",
        "🧬 Feature Importance (Upcoming)"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr style='border-color: #334155; margin: 15px 0;' />", unsafe_allow_html=True)

# Fetch base dataset using API Client
df_all = api_client.fetch_incidents()

if df_all.empty:
    st.error("Unable to load crime dataset. Please verify database path configuration.")
    st.stop()

# 3.5 Query Filters
st.sidebar.subheader("🔍 Query Filters")

# District Filter
districts = ["All Districts"] + sorted(list(df_all["District"].unique()))
selected_district = st.sidebar.selectbox("Jurisdiction", districts)

# Crime Category Filter
crime_categories = ["All Categories"] + sorted(list(df_all["Crime Category"].unique()))
selected_crime = st.sidebar.selectbox("Offense Category", crime_categories)

# Time Frame Filter
time_filter = st.sidebar.selectbox(
    "Reporting Period",
    ["All Time", "Last 12 Months", "Last 6 Months", "Last 30 Days"]
)

# Apply Filter logic
filtered_df = df_all.copy()

# Date filtering (relative to max date in database for robust handling of static data)
max_date = df_all["Date"].max()
if time_filter == "Last 12 Months":
    cutoff = max_date - timedelta(days=365)
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]
elif time_filter == "Last 6 Months":
    cutoff = max_date - timedelta(days=180)
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]
elif time_filter == "Last 30 Days":
    cutoff = max_date - timedelta(days=30)
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]

# District filter
if selected_district != "All Districts":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

# Crime Category filter
if selected_crime != "All Categories":
    filtered_df = filtered_df[filtered_df["Crime Category"] == selected_crime]


# ----------------------------------------------------
# 4. Header Bar
# ----------------------------------------------------
def render_header(title_suffix):
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e3a8a 0%, #0f172a 100%); padding: 18px 25px; border-radius: 10px; border-bottom: 4px solid #eab308; margin-bottom: 25px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 style="color: #ffffff; margin: 0; font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">🚨 KARNATAKA STATE POLICE</h1>
                <p style="color: #93c5fd; margin: 4px 0 0 0; font-size: 14px; font-weight: 400; font-family: 'Inter', sans-serif;">Crime Intelligence Platform & Predictive Analytics Center</p>
            </div>
            <div style="background-color: rgba(234, 179, 8, 0.15); border: 1px solid #eab308; padding: 6px 14px; border-radius: 20px; font-weight: 700; color: #facc15; font-size: 13px; letter-spacing: 0.5px; text-transform: uppercase;">
                {title_suffix}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Custom KPI Card Helper
def draw_kpi_card(title, value, subtitle, border_color="#3B82F6"):
    st.markdown(f"""
    <div class="metric-card-hover" style="
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-top: 4px solid {border_color};
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-left: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
        height: 100%;
    ">
        <h4 style="margin: 0; color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{title}</h4>
        <h2 style="margin: 12px 0 6px 0; font-size: 28px; font-weight: 800; color: #f8fafc; font-family: 'Outfit', sans-serif;">{value}</h2>
        <p style="margin: 0; color: #38bdf8; font-size: 12px; font-weight: 500;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# User-friendly API alert handler
def handle_api_error(err_msg: str | None):
    if err_msg:
        st.warning(f"⚠️ API Pipeline Warning: {err_msg}")


# ----------------------------------------------------
# 5. Page 1: Executive Dashboard
# ----------------------------------------------------
if page == "📊 Executive Dashboard":
    render_header("Executive Dashboard")
    
    # Fetch data streams
    df_anomalies, err_an = api_client.fetch_anomalies()
    df_centroids, err_ce = api_client.fetch_hotspot_centroids(filtered_df)
    df_risk, err_rk = api_client.fetch_district_risk()
    
    # Handle user-friendly warnings
    handle_api_error(err_an or err_ce or err_rk)
    
    # Core calculations
    total_crimes = len(filtered_df)
    hotspots_count = len(df_centroids) if not df_centroids.empty else 0
    anomalies_count = len(df_anomalies[df_anomalies["district"].isin(filtered_df["District"].unique())]) if not df_anomalies.empty else 0
    high_risk_districts = len(df_risk[df_risk["Risk_Level"] == "Critical"]) if not df_risk.empty else 0
    
    # KPI Metric Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        draw_kpi_card("Total Crimes", f"{total_crimes:,}", "Registered incidents", "#3B82F6")
    with kpi_col2:
        draw_kpi_card("Hotspots Detected", f"{hotspots_count}", "Active clustering centers", "#EF4444")
    with kpi_col3:
        draw_kpi_card("Anomalies Flagged", f"{anomalies_count}", "High priority alert logs", "#F59E0B")
    with kpi_col4:
        draw_kpi_card("Critical Districts", f"{high_risk_districts}", "CRI Critical severity status", "#10B981")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Executive Highlights
    st.subheader("📢 Critical System Alert Log")
    if not df_anomalies.empty:
        # Filter anomalies by active query filters
        filtered_anomalies = df_anomalies[df_anomalies["district"].isin(filtered_df["District"].unique())].head(5)
        if not filtered_anomalies.empty:
            st.dataframe(
                filtered_anomalies[["Incident ID", "date", "district", "police_station", "crime_type", "status"]].rename(
                    columns={"date": "Date Detected", "district": "District", "police_station": "Station", "crime_type": "Incident Type", "status": "Case Status"}
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No anomalous patterns detected in current query scope.")
    else:
        st.info("No anomalies database available.")


# ----------------------------------------------------
# 6. Page 2: Crime Risk Dashboard
# ----------------------------------------------------
elif page == "⚠️ Crime Risk Dashboard":
    render_header("Crime Risk Index (CRI)")
    
    df_risk, err_rk = api_client.fetch_district_risk()
    handle_api_error(err_rk)
    
    if not df_risk.empty:
        # Filter risk scores by selected filters if applicable
        if selected_district != "All Districts":
            disp_risk = df_risk[df_risk["district"] == selected_district]
        else:
            disp_risk = df_risk
            
        col_table, col_chart = st.columns([1, 1])
        
        with col_table:
            st.subheader("📋 District Risk Standings")
            st.dataframe(
                disp_risk[["district", "crime_count", "repeat_offenders", "CRI", "Risk_Level"]].rename(
                    columns={"district": "District", "crime_count": "Total Crimes", "repeat_offenders": "Recidivists", "CRI": "CRI Score", "Risk_Level": "Risk Level"}
                ),
                use_container_width=True,
                hide_index=True
            )
            
        with col_chart:
            st.subheader("📊 Crime Risk Index Comparison")
            fig_cri = px.bar(
                disp_risk.sort_values(by="CRI", ascending=True),
                x="CRI",
                y="district",
                orientation="h",
                color="Risk_Level",
                color_discrete_map={"Critical": "#EF4444", "High": "#F59E0B", "Medium": "#3B82F6", "Low": "#10B981"},
                labels={"CRI": "CRI Score", "district": "District", "Risk_Level": "Risk Level"}
            )
            fig_cri.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                margin=dict(l=20, r=20, t=10, b=20),
                height=400
            )
            st.plotly_chart(fig_cri, use_container_width=True)
    else:
        st.info("District Crime Risk Index database not found.")


# ----------------------------------------------------
# 7. Page 3: Hotspot Intelligence Dashboard
# ----------------------------------------------------
elif page == "🔥 Hotspot Intelligence Dashboard":
    render_header("Hotspot Intelligence")
    
    df_hotspots, err_ht = api_client.fetch_hotspots()
    handle_api_error(err_ht)
    
    if not df_hotspots.empty:
        col_table, col_chart = st.columns([1, 1])
        
        with col_table:
            st.subheader("📋 Hotspot Cluster Analytics")
            st.dataframe(
                df_hotspots.rename(
                    columns={"cluster": "Cluster ID", "crime_count": "Registered Cases"}
                ),
                use_container_width=True,
                hide_index=True
            )
            
        with col_chart:
            st.subheader("📊 Incident Counts per Hotspot Cluster")
            fig_hot = px.bar(
                df_hotspots,
                x="cluster",
                y="crime_count",
                labels={"cluster": "Cluster ID", "crime_count": "Incidents count"},
                color="crime_count",
                color_continuous_scale="Reds"
            )
            fig_hot.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                coloraxis_showscale=False,
                xaxis=dict(type='category'),
                margin=dict(l=20, r=20, t=10, b=20),
                height=400
            )
            st.plotly_chart(fig_hot, use_container_width=True)
    else:
        st.info("Hotspot statistics are currently unavailable.")


# ----------------------------------------------------
# 8. Page 4: Patrol Recommendation Dashboard
# ----------------------------------------------------
elif page == "🛡️ Patrol Recommendation Dashboard":
    render_header("Patrol Recommendations")
    
    df_priority, err_pr = api_client.fetch_patrol_priority()
    handle_api_error(err_pr)
    
    if not df_priority.empty:
        col_table, col_chart = st.columns([10, 8])
        
        with col_table:
            st.subheader("📋 Operational Patrol Ranking")
            st.dataframe(
                df_priority[["district", "patrol_rank", "anomaly_count", "priority_score", "recommendation"]].rename(
                    columns={"district": "District", "patrol_rank": "Rank Priority", "anomaly_count": "Anomalies", "priority_score": "Priority Index", "recommendation": "Patrol Action Required"}
                ),
                use_container_width=True,
                hide_index=True
            )
            
        with col_chart:
            st.subheader("📊 Top Priority Patrol Districts")
            fig_pat = px.bar(
                df_priority.sort_values(by="priority_score", ascending=True).tail(10),
                x="priority_score",
                y="district",
                orientation="h",
                color="priority_score",
                color_continuous_scale="Oranges",
                labels={"priority_score": "Priority Index", "district": "District"}
            )
            fig_pat.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=10, b=20),
                height=400
            )
            st.plotly_chart(fig_pat, use_container_width=True)
    else:
        st.info("Patrol priority allocations are currently unavailable.")


# ----------------------------------------------------
# 9. Page 5: Temporal Trend Dashboard
# ----------------------------------------------------
elif page == "📅 Temporal Trend Dashboard":
    render_header("Temporal Trends")
    
    df_month, err_mo = api_client.fetch_monthly_trends()
    df_week, err_we = api_client.fetch_weekday_trends()
    handle_api_error(err_mo or err_we)
    
    col_mo, col_we = st.columns([1, 1])
    
    with col_mo:
        st.subheader("📈 Monthly Crime Trajectory")
        if not df_month.empty:
            fig_mo = px.line(
                df_month,
                x="month_name",
                y="crime_count",
                labels={"month_name": "Month", "crime_count": "Incidents"},
                color_discrete_sequence=["#3B82F6"]
            )
            fig_mo.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=8, color="#facc15"))
            fig_mo.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                margin=dict(l=20, r=20, t=10, b=20),
                height=400
            )
            st.plotly_chart(fig_mo, use_container_width=True)
        else:
            st.info("Monthly trends not available.")
            
    with col_we:
        st.subheader("📅 Weekday Crime Load Patterns")
        if not df_week.empty:
            fig_we = px.bar(
                df_week,
                x="weekday",
                y="crime_count",
                labels={"weekday": "Day of Week", "crime_count": "Crime Incidents"},
                color="crime_count",
                color_continuous_scale="Purples"
            )
            fig_we.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=10, b=20),
                height=400
            )
            st.plotly_chart(fig_we, use_container_width=True)
        else:
            st.info("Weekday trends not available.")


# ----------------------------------------------------
# 10. Page 6: GIS Map Dashboard (Centroids Upgraded)
# ----------------------------------------------------
elif page == "📍 GIS Map Dashboard":
    render_header("GIS Map Dashboard")
    
    st.subheader("🗺️ Spatial Distribution & Cluster Mapping")
    st.markdown(
        "Interactive GIS tracking dashboard utilizing spatial coordinate feeds. "
        "The primary GIS view displays Folium HTML layers compiled and delivered via our GIS team's APIs."
    )
    
    # Active selector dropdown for actual HTML files pushed to Git
    map_layer = st.selectbox(
        "Select Active GIS Map Layer",
        [
            "🚨 General Crime Incidents Map (crime_map.html)",
            "🔥 Crime Hotspots Clusters Map (crime_hotspots.html)",
            "🌡️ Crime Kernel Density Heatmap (crime_heatmap.html)",
            "⚠️ Anomaly Detection Zones Map (crime_anomalies.html)"
        ]
    )
    
    layer_key = {
        "🚨 General Crime Incidents Map (crime_map.html)": "crime_map",
        "🔥 Crime Hotspots Clusters Map (crime_hotspots.html)": "crime_hotspots",
        "🌡️ Crime Kernel Density Heatmap (crime_heatmap.html)": "crime_heatmap",
        "⚠️ Anomaly Detection Zones Map (crime_anomalies.html)": "crime_anomalies"
    }[map_layer]
    
    # Tab to swap between the static HTML layer and interactive Plotly centroid mapping
    tab_html, tab_centroids = st.tabs(["🗺️ Folium HTML Layer", "📍 Hotspot Centroid Mapping"])
    
    with tab_html:
        with st.spinner(f"Requesting '{layer_key}' HTML Layer..."):
            folium_html_str = api_client.fetch_gis_map_layer(layer_key)
            
        if folium_html_str and len(folium_html_str) > 100:
            st.components.v1.html(folium_html_str, height=550, scrolling=True)
        else:
            st.error(f"Failed to load map layer '{layer_key}' from GIS pipeline. Verify the file exists under gis/outputs/maps/.")
            
    with tab_centroids:
        # Fetch Centroids from API
        df_centroids, err_ce = api_client.fetch_hotspot_centroids(filtered_df)
        handle_api_error(err_ce)
        
        if not df_centroids.empty:
            st.markdown("#### Hotspot Cluster Centroids Mapping")
            st.markdown(
                "Interactive centroids mapping coordinates representing spatial cluster centers. "
                "Hover or click markers below to see popup telemetry metrics."
            )
            # Render hotspots Mapbox using Plotly with custom popup/hover metrics
            fig_cent = px.scatter_mapbox(
                df_centroids,
                lat="centroid_latitude",
                lon="centroid_longitude",
                size="crime_count",
                color="cluster",
                hover_name="cluster",
                hover_data={
                    "cluster": True,
                    "crime_count": True,
                    "centroid_latitude": True,
                    "centroid_longitude": True
                },
                mapbox_style="carto-darkmatter",
                zoom=6.0,
                title="DBSCAN Hotspot Centroids"
            )
            fig_cent.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                margin=dict(l=0, r=0, t=30, b=0),
                height=550
            )
            st.plotly_chart(fig_cent, use_container_width=True)
        else:
            st.info("No hotspots centroids available to map.")


# ----------------------------------------------------
# 11. Page 7: Crime Prediction (ML Placeholder)
# ----------------------------------------------------
elif page == "🔮 Crime Prediction (Upcoming)":
    render_header("Crime Prediction Assessor")
    
    st.subheader("🔮 ML Crime Predictor Pipeline")
    st.info("📡 Pipeline Status: Pending integration with ML team API service endpoint: POST /predict-crime")
    
    st.markdown("""
    <div style="background-color: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 25px; border-radius: 8px;">
        <h4 style="margin-top:0; color:#facc15;">Crime Forecast Predictor Simulation</h4>
        <p style="color:#cbd5e1; font-size:14px;">Once the ML microservice goes live, this panel will send offender parameters, time vectors, and coordinates to the backend classifier to compute local event probabilities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.markdown("##### 📝 Predictor Input Params")
        st.selectbox("Select Target District", sorted(list(df_all["District"].unique())))
        st.selectbox("Select Target Offense Class", sorted(list(df_all["Crime Category"].unique())))
        st.date_input("Target Date Range", datetime.now() + timedelta(days=1))
        st.slider("Target Hour of Day", 0, 23, 12)
        st.button("Run Prediction Models", disabled=True)
        
    with col_out:
        st.markdown("##### 📈 Predicted Threat Probability")
        # Renders a simulated gauge representing the upcoming model output
        fig_sim_g = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 45,
            title = {'text': "Predicted Incident Probability (Demo Output)", 'font': {'color': '#94a3b8', 'size': 14}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#3B82F6"},
                'bgcolor': "#1e293b",
                'borderwidth': 2,
                'bordercolor': "#475569"
            }
        ))
        fig_sim_g.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "white"},
            height=250,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_sim_g, use_container_width=True)


# ----------------------------------------------------
# 12. Page 8: Feature Importance (ML Placeholder)
# ----------------------------------------------------
elif page == "🧬 Feature Importance (Upcoming)":
    render_header("Feature Importance (SHAP)")
    
    st.subheader("🧬 ML Model Feature Attribution & Importance Analysis")
    st.info("📡 Pipeline Status: Pending integration with ML team API service endpoint: GET /feature-importance")
    
    st.markdown("""
    <div style="background-color: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
        <h4 style="margin-top:0; color:#facc15;">Explainable AI & SHAP Global Summary</h4>
        <p style="color:#cbd5e1; font-size:14px;">Attributing model features representing historical variables and their impact on global prediction outcomes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simulates a SHAP summary bar chart
    features = ["Prior Convictions", "Offender Age", "District Density", "Unemployment Rate", "Rehab Completion", "Time of Day"]
    importance = [0.38, 0.22, 0.18, 0.12, 0.08, 0.04]
    
    fig_shap = px.bar(
        x=importance,
        y=features,
        orientation="h",
        labels={"x": "Global SHAP Value (Impact)", "y": "Feature Name"},
        color=importance,
        color_continuous_scale="Viridis",
        title="SHAP Global Feature Importance Attribution (Demo Mode)"
    )
    fig_shap.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#94a3b8',
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    st.plotly_chart(fig_shap, use_container_width=True)


# ----------------------------------------------------
# 13. Footer
# ----------------------------------------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>KSP Crime Intelligence Platform – Datathon 2026</p>", unsafe_allow_html=True)
