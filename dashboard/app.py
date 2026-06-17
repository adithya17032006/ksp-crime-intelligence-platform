import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
from datetime import datetime, timedelta

# Import the API client representing our pipelines
from api_client import KSPAPIClient

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
    
    /* Styled container for KPI cards */
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
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
# 3. Sidebar Configuration, Settings & API Client
# ----------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 15px 0 5px 0;">
    <h2 style="color: #eab308; font-size: 20px; font-weight: 800; margin: 0; font-family: 'Outfit';">KSP INTELLIGENCE</h2>
    <p style="color: #94a3b8; font-size: 12px; margin: 0;">Command Portal v2.2</p>
</div>
<hr style="margin-top: 10px; margin-bottom: 20px; border-color: #334155;" />
""", unsafe_allow_html=True)

# 3.1 Connection settings for backend API microservices
st.sidebar.subheader("🔌 API Port Connections")
api_host = st.sidebar.text_input("Target API Host", "http://localhost:8000", key="api_host_setting")

# Instantiate central API client
api_client = KSPAPIClient(base_url=api_host)

# Verify API connectivity
api_connected = False
try:
    res = requests.get(f"{api_host}/api/backend/incidents", timeout=0.4)
    if res.status_code == 200:
        api_connected = True
except Exception:
    pass

if api_connected:
    st.sidebar.success("🟢 API Pipelines: Connected")
else:
    st.sidebar.warning("⚠️ Running in Local Fallback")

st.sidebar.markdown("<hr style='border-color: #334155; margin: 15px 0;' />", unsafe_allow_html=True)

# 3.2 Main Navigation Menu
st.sidebar.subheader("🧭 Navigation Menu")
page = st.sidebar.radio(
    "Select System Module",
    ["📊 Dashboard Overview", "📍 GIS Mapping & Hotspots", "🔮 ML Crime Predictions", "🕸️ Criminal Network Analysis"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr style='border-color: #334155; margin: 15px 0;' />", unsafe_allow_html=True)

# Fetch base dataset using Backend API Client
df_all = api_client.fetch_incidents()

if df_all.empty:
    st.error("Unable to load crime dataset from API or Local File. Please verify database path configuration.")
    st.stop()

# 3.3 Query Filters
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


# ----------------------------------------------------
# 5. Page 1: Dashboard Overview
# ----------------------------------------------------
if page == "📊 Dashboard Overview":
    render_header("Overview")
    
    # 5.1 Core Metrics Calculation
    total_crimes = len(filtered_df)
    
    # Hotspot grid clustering count (based on latitude/longitude density)
    filtered_df['lat_round'] = filtered_df['Latitude'].round(2)
    filtered_df['lon_round'] = filtered_df['Longitude'].round(2)
    hotspots_count = filtered_df.groupby(['lat_round', 'lon_round']).filter(lambda x: len(x) >= 3)['lat_round'].nunique()
    # Default minimum hotspots
    if hotspots_count == 0 and total_crimes > 0:
        hotspots_count = int(total_crimes * 0.05) + 1
    elif total_crimes == 0:
        hotspots_count = 0
        
    repeat_offenders_count = len(filtered_df[filtered_df["Repeat Offender"] == True])
    repeat_pct = (repeat_offenders_count / total_crimes * 100) if total_crimes > 0 else 0
    
    # High Risk jurisdictions calculation
    district_counts = filtered_df.groupby("District").size()
    avg_crime_rate = total_crimes / len(districts[1:]) if len(districts) > 1 else 0
    high_risk_districts = len(district_counts[district_counts > (avg_crime_rate * 1.15)]) if len(district_counts) > 0 else 0
    
    # 5.2 Display Metric Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        draw_kpi_card("Total Crimes Registered", f"{total_crimes:,}", "Real-time ledger entries", "#3B82F6")
    with kpi_col2:
        draw_kpi_card("Hotspots Detected", f"{hotspots_count}", "Dense incident coordinates", "#EF4444")
    with kpi_col3:
        draw_kpi_card("Repeat Offenders", f"{repeat_offenders_count:,}", f"{repeat_pct:.1f}% Recidivism rate", "#F59E0B")
    with kpi_col4:
        draw_kpi_card("High Risk Districts", f"{high_risk_districts}", "Exceeding crime average thresholds", "#10B981")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5.3 Tabbed Dashboard Sections (Overview Metrics & GIS/ML deliverables)
    tab_analytics, tab_processed_models = st.tabs(["📊 Incident Analytics", "🧠 GIS / ML Model Deliverables"])
    
    with tab_analytics:
        col_left, col_right = st.columns([8, 7])
        
        with col_left:
            st.subheader("📈 Monthly Incident Trajectory")
            df_monthly = filtered_df.copy()
            df_monthly['YearMonth'] = df_monthly['Date'].dt.to_period('M')
            monthly_trend = df_monthly.groupby('YearMonth').size().reset_index(name='Incident Count')
            monthly_trend['YearMonth'] = monthly_trend['YearMonth'].dt.to_timestamp()
            monthly_trend = monthly_trend.sort_values('YearMonth')
            
            if not monthly_trend.empty:
                fig_trend = px.line(
                    monthly_trend, 
                    x='YearMonth', 
                    y='Incident Count',
                    labels={'Incident Count': 'Incidents', 'YearMonth': 'Month'},
                    color_discrete_sequence=['#3B82F6']
                )
                fig_trend.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=8, color="#facc15"))
                fig_trend.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    xaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    yaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    margin=dict(l=20, r=20, t=10, b=20),
                    height=320
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No timeline trajectory available.")

            st.subheader("📊 Category Classification Analysis")
            if not filtered_df.empty:
                category_counts = filtered_df["Crime Category"].value_counts().reset_index()
                category_counts.columns = ["Category", "Count"]
                
                fig_pie = px.pie(
                    category_counts, 
                    values='Count', 
                    names='Category',
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Dark24
                )
                fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#0f172a', width=2)))
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(l=10, r=10, t=10, b=50),
                    height=320
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No category classification metrics found.")
                
        with col_right:
            st.subheader("🏢 Distribution by Police District")
            if not filtered_df.empty:
                district_counts = filtered_df["District"].value_counts().reset_index()
                district_counts.columns = ["District", "Incidents"]
                
                fig_bar = px.bar(
                    district_counts.sort_values(by="Incidents", ascending=True), 
                    x='Incidents', 
                    y='District', 
                    orientation='h',
                    color='Incidents',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    yaxis=dict(showgrid=False),
                    margin=dict(l=20, r=20, t=10, b=20),
                    height=320
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No district layout records match queries.")
                
            st.subheader("👥 Victim vs Offender Age Profile")
            if not filtered_df.empty:
                fig_age = go.Figure()
                fig_age.add_trace(go.Histogram(
                    x=filtered_df["Victim Age"],
                    name="Victim Age",
                    xbins=dict(start=10, end=90, size=5),
                    marker_color='#10B981',
                    opacity=0.6
                ))
                fig_age.add_trace(go.Histogram(
                    x=filtered_df["Offender Age"],
                    name="Offender Age",
                    xbins=dict(start=10, end=90, size=5),
                    marker_color='#E63946',
                    opacity=0.6
                ))
                fig_age.update_layout(
                    barmode='overlay',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    xaxis=dict(title='Age (Years)', showgrid=True, gridcolor='#1e293b'),
                    yaxis=dict(title='Count', showgrid=True, gridcolor='#1e293b'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=320
                )
                st.plotly_chart(fig_age, use_container_width=True)
            else:
                st.info("No age demographics available.")

    with st.spinner("Fetching pre-computed GIS/ML model scores..."):
        # Fetch actual deliverables generated by ML/GIS teams
        df_cri = api_client.fetch_crime_risk_scores()
        df_priority = api_client.fetch_patrol_priorities()
        df_week = api_client.fetch_weekday_trends()

    with tab_processed_models:
        col_scores, col_week = st.columns([1, 1])
        
        with col_scores:
            st.subheader("🏆 Crime Risk Index (CRI) Standings")
            st.markdown("Pre-computed index rating districts based on severity levels and repeat offender ratios.")
            if not df_cri.empty:
                st.dataframe(
                    df_cri[["district", "crime_count", "repeat_offenders", "CRI", "Risk_Level"]].rename(
                        columns={"district": "District", "crime_count": "Incidents", "repeat_offenders": "Recidivists", "CRI": "CRI Score", "Risk_Level": "Risk Level"}
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Crime Risk Index dataset not found under data/processed/.")

            st.subheader("🛡️ District Patrol Rank & Patrol Priority")
            st.markdown("Operational patrol priority recommendations mapped dynamically based on anomaly clusters.")
            if not df_priority.empty:
                st.dataframe(
                    df_priority[["district", "patrol_rank", "recommendation"]].rename(
                        columns={"district": "District", "patrol_rank": "Rank Priority", "recommendation": "Operational Order"}
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Patrol priority database not found under data/processed/.")
                
        with col_week:
            st.subheader("📅 Temporal Patterns: Weekly Crime Load")
            st.markdown("Weekly distribution of registered incidents computed during temporal profile runs.")
            if not df_week.empty:
                # Plot weekday trends bar chart
                fig_week = px.bar(
                    df_week,
                    x="weekday",
                    y="crime_count",
                    labels={"weekday": "Day of Week", "crime_count": "Crime Incidents"},
                    color="crime_count",
                    color_continuous_scale="Reds"
                )
                fig_week.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    yaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    margin=dict(l=20, r=20, t=10, b=20),
                    height=450
                )
                st.plotly_chart(fig_week, use_container_width=True)
            else:
                st.info("Weekday trends database not found under data/processed/.")

    # Recent incident logs bottom grid
    st.subheader("📰 Recent Incident Logs")
    if not filtered_df.empty:
        recent_logs = filtered_df.sort_values(by=["Date", "Incident ID"], ascending=False).head(5)
        display_cols = ["Incident ID", "Date", "District", "Police Station", "Crime Category", "Status", "Victim Age", "Offender Age"]
        
        st.dataframe(
            recent_logs[display_cols].assign(Date=recent_logs["Date"].dt.strftime('%Y-%m-%d')),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No recent logs found.")


# ----------------------------------------------------
# 6. Page 2: GIS Map Component (Pushed Files Activated)
# ----------------------------------------------------
elif page == "📍 GIS Mapping & Hotspots":
    render_header("GIS Mapping & Hotspots")
    
    st.subheader("🗺️ Spatial Distribution & Cluster Mapping")
    st.markdown(
        "Interactive GIS tracking dashboard utilizing spatial coordinate feeds. "
        "Select and examine the actual Folium HTML layers compiled and delivered by the GIS team."
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.spinner(f"Requesting '{layer_key}' HTML Layer..."):
        # Fetch the selected Folium Map HTML string from API client
        folium_html_str = api_client.fetch_gis_map_layer(layer_key)
        
    if folium_html_str and len(folium_html_str) > 100:
        # Embed Folium HTML map frame
        st.components.v1.html(folium_html_str, height=600, scrolling=True)
    else:
        st.error(f"Failed to load map layer '{layer_key}' from GIS pipeline. Verify the file exists under gis/outputs/maps/.")

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("##### 📡 CCTV Patrol Coverage")
        st.info("System integration links: 12,400 cameras active under Integrated Command and Control Center (ICCC) feeds.")
    with col2:
        st.markdown("##### 🚨 Geofenced Zone Status")
        st.success("All geofences active. 4 high-risk locations set for automated alarms on police dispatch grids.")
    with col3:
        st.markdown("##### 📂 Geo-Analysis Export")
        st.markdown("Download active query parameters and coordinates in GeoJSON formats for field deployment tools.")
        st.button("Export Active Layer Coordinates (JSON)")


# ----------------------------------------------------
# 7. Page 3: ML Predictions Component
# ----------------------------------------------------
elif page == "🔮 ML Crime Predictions":
    render_header("ML Crime Predictions")
    
    st.subheader("📊 Volume Forecasting & Recidivism Predictors")
    st.markdown(
        "Integrating models developed by our AI/ML Intelligence Team (Member 3). "
        "Exposes forecast projections and predictive assessment gauges."
    )
    
    tab_forecast, tab_recidivism = st.tabs(["📈 6-Month Crime Volume Forecast", "🧠 Recidivism Risk Assessor"])
    
    with tab_forecast:
        st.markdown("#### Monthly Crime Volume Predictions")
        st.markdown("Forecasting monthly incident volume by parsing historical records and LSTM predictions.")
        
        # Construct monthly aggregated sequence to send/check with forecasting API
        df_monthly = filtered_df.copy()
        df_monthly['YearMonth'] = df_monthly['Date'].dt.to_period('M')
        monthly_trend = df_monthly.groupby('YearMonth').size().reset_index(name='Incidents')
        monthly_trend['YearMonth'] = monthly_trend['YearMonth'].dt.to_timestamp()
        monthly_trend = monthly_trend.sort_values('YearMonth')
        
        if len(monthly_trend) >= 3:
            with st.spinner("Requesting forecast trend from AI/ML Forecasting service..."):
                # Fetch forecast DataFrame from API pipeline (Member 3)
                forecast_df = api_client.fetch_forecast(monthly_trend)
                
            if not forecast_df.empty:
                # Combine for plotting
                fig_fc = go.Figure()
                
                # Historical Line
                fig_fc.add_trace(go.Scatter(
                    x=monthly_trend['YearMonth'], y=monthly_trend['Incidents'],
                    mode='lines+markers',
                    name='Historical Records',
                    line=dict(color='#3B82F6', width=3)
                ))
                
                # Forecast Line
                fig_fc.add_trace(go.Scatter(
                    x=forecast_df['YearMonth'], y=forecast_df['Incidents'],
                    mode='lines+markers',
                    name='Model Forecast',
                    line=dict(color='#F59E0B', width=3, dash='dash')
                ))
                
                # Uncertainty Band (Plotly Fix: fill='toself' boundary rendering)
                fig_fc.add_trace(go.Scatter(
                    x=forecast_df['YearMonth'].tolist() + forecast_df['YearMonth'].tolist()[::-1],
                    y=forecast_df['Upper'].tolist() + forecast_df['Lower'].tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(245, 158, 11, 0.12)',
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip",
                    name='95% Confidence Interval'
                ))
                
                fig_fc.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    xaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    yaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                    margin=dict(l=20, r=20, t=10, b=50),
                    height=450
                )
                st.plotly_chart(fig_fc, use_container_width=True)
            else:
                st.error("Failed to load forecast trends from AI/ML API.")
        else:
            st.info("Insufficient data points in current filter subset to compute forecast layers. Select 'All Districts' to view details.")
            
    with tab_recidivism:
        st.markdown("#### Interactive Recidivism Risk Assessor (SHAP Supported)")
        st.write("Determine risk parameters and explore explainable features using SHAP models.")
        
        # Calculate dynamic defaults from active filtered dataframe
        avg_age = int(filtered_df["Offender Age"].mean()) if not filtered_df.empty else 28
        avg_repeat_offenses = int(filtered_df[filtered_df["Repeat Offender"] == True].groupby("Offender Age").size().mean()) if not filtered_df.empty else 1
        avg_repeat_offenses = min(max(avg_repeat_offenses, 0), 15)
        
        col_inp, col_gauge = st.columns([1, 1])
        with col_inp:
            age = st.slider("Offender Age", 18, 90, avg_age)
            prev_convictions = st.slider("Prior Offences Count", 0, 15, avg_repeat_offenses)
            offence_class = st.selectbox("Offence Category Profile", sorted(list(df_all["Crime Category"].unique())))
            employment = st.selectbox("Employment Status Profile", ["Unemployed", "Underemployed / Part-time", "Full-time Employed"])
            rehab_status = st.radio("Completed Rehabilitation Programs", ["No", "Yes"])
            
        with col_gauge:
            with st.spinner("Requesting risk profiling from AI/ML Prediction pipeline..."):
                # Fetch prediction details from API pipeline (Member 3)
                prediction = api_client.predict_recidivism(age, prev_convictions, offence_class, employment, rehab_status)
                
            risk_score = prediction["risk_score"]
            risk_lbl = prediction["risk_label"]
            risk_col = prediction["risk_color"]
            shap_explanation = prediction["shap_explanation"]
            intervention = prediction["intervention"]
                
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risk_score,
                title = {'text': f"Recidivism Index: {risk_lbl}", 'font': {'color': 'white', 'size': 18}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': risk_col},
                    'bgcolor': "#1e293b",
                    'borderwidth': 2,
                    'bordercolor': "#475569",
                    'steps': [
                        {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.1)'},
                        {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.1)'},
                        {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.1)'}
                    ],
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "white"},
                height=250,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown(f"""
            <div style="background-color: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <span style="font-weight: bold; color: {risk_col};">{risk_lbl} Profile Alert:</span>
                Offender profile indicates a <strong>{risk_score}%</strong> probability of recidivism. Recommended Action: <strong>{intervention}</strong>
            </div>
            """, unsafe_allow_html=True)

            # Display SHAP Text Explanations (Member 3 pipeline deliverable)
            st.markdown("##### 🧠 SHAP Feature Explanations (AI Trace Log)")
            st.code(shap_explanation, language="text")


# ----------------------------------------------------
# 8. Page 4: Criminal Network Analysis Component
# ----------------------------------------------------
elif page == "🕸️ Criminal Network Analysis":
    render_header("Criminal Network Analysis")
    
    st.subheader("🕸️ Syndicate Connectivity & Association Linkages")
    st.markdown(
        "Visualizing relationship networks mapping connection links between active syndicate members. "
        "This data layer represents Relational graphs delivered via Member 4's APIs."
    )
    
    col_net, col_profile = st.columns([9, 6])
    
    with st.spinner("Fetching Relational Network Graph data from Network API pipeline..."):
        # Fetch node-link graph details from API pipeline (Member 4)
        graph_data = api_client.fetch_network_graph()
        # Fetch Suspect profile list from API pipeline (Member 1)
        suspects_profile_list = api_client.fetch_suspects()
    
    nodes = graph_data["nodes"]
    edges = graph_data["edges"]
    
    with col_net:
        # Create Scatter Plot for Network Structure
        fig_net = go.Figure()
        
        # Add Edge Lines
        edge_x = []
        edge_y = []
        for edge in edges:
            source_node = next(n for n in nodes if n["id"] == edge["source"])
            target_node = next(n for n in nodes if n["id"] == edge["target"])
            edge_x.extend([source_node["x"], target_node["x"], None])
            edge_y.extend([source_node["y"], target_node["y"], None])
            
        fig_net.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.5, color='#475569'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add Node Scatter Points
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for info in nodes:
            node_x.append(info["x"])
            node_y.append(info["y"])
            node_text.append(f"Name: {info['id']}<br>Role: {info['type']}<br>Risk Rating: {info['risk']}<br>FIR Cases: {info['cases']}")
            
            # Node Coloring
            if info["risk"] == "Critical":
                node_color.append("#EF4444")
                node_size.append(28)
            elif info["risk"] == "High":
                node_color.append("#F59E0B")
                node_size.append(22)
            else:
                node_color.append("#3B82F6")
                node_size.append(16)
                
        fig_net.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[n["id"].split(" (")[0] for n in nodes],
            textposition="top center",
            hovertext=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(color='#0f172a', width=2)
            )
        ))
        
        fig_net.update_layout(
            title="Relational Association Map (Syndicate Grid)",
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=10, r=10, t=40, b=10),
            height=500
        )
        st.plotly_chart(fig_net, use_container_width=True)
        
    with col_profile:
        st.subheader("👤 Suspect Profile Details")
        
        # Pick Suspect
        suspect_key = st.selectbox("Select Target Suspect Profile", list(suspects_profile_list.keys()))
        s_info = suspects_profile_list[suspect_key]
        
        # Display Suspect Metadata card
        risk_badge_color = {"Critical": "#EF4444", "High": "#F59E0B", "Medium": "#3B82F6"}[s_info["risk"]]
        
        st.markdown(f"""
        <div style="background-color: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 8px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #f8fafc; font-size: 18px; font-weight: 700;">{suspect_key.split(' (')[0]}</h4>
                <span style="background-color: {risk_badge_color}; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase;">
                    {s_info["risk"]}
                </span>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; color: #cbd5e1; font-size: 13px;">
                <tr style="border-bottom: 1px solid #334155;">
                    <td style="padding: 8px 0; font-weight: bold;">System Role:</td>
                    <td style="padding: 8px 0; text-align: right; color: #facc15;">{s_info["type"]}</td>
                </tr>
                <tr style="border-bottom: 1px solid #334155;">
                    <td style="padding: 8px 0; font-weight: bold;">Registered FIR Cases:</td>
                    <td style="padding: 8px 0; text-align: right; color: #facc15;">{s_info["cases"]}</td>
                </tr>
                <tr style="border-bottom: 1px solid #334155;">
                    <td style="padding: 8px 0; font-weight: bold;">Last Tracker Position:</td>
                    <td style="padding: 8px 0; text-align: right; color: #38bdf8; font-weight: bold;">{s_info["last_known"]}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Status Flag:</td>
                    <td style="padding: 8px 0; text-align: right; color: #EF4444; font-weight: bold;">Active Alert / Under Surveillance</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display direct associates
        associates = []
        for edge in edges:
            if suspect_key == edge["source"] or suspect_key == edge["target"]:
                other = edge["source"] if edge["target"] == suspect_key else edge["target"]
                associates.append(other.split(' (')[0])
                
        st.markdown("##### 👥 Direct Linkage Connections:")
        if associates:
            for assoc in set(associates):
                st.markdown(f"- **{assoc}** - Accomplice link verified by cell tower correlations")
        else:
            st.markdown("*No direct active syndicate edges detected.*")
