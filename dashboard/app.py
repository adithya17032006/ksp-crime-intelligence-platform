import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

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
# 3. Helper Functions & Mock Data Generation
# ----------------------------------------------------
@st.cache_data
def generate_mock_data():
    """Generates realistic mock crime data for Karnataka State Police."""
    districts = ["Bengaluru City", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi"]
    crime_categories = ["Theft", "Cyber Crime", "Assault", "Narcotics", "Robbery"]
    
    # Set seed for reproducibility
    np.random.seed(1703)
    start_date = datetime.now() - timedelta(days=365)
    
    # Coordinates mapping for districts
    coords = {
        "Bengaluru City": (12.9716, 77.5946),
        "Mysuru": (12.2958, 76.6394),
        "Hubballi-Dharwad": (15.3647, 75.1240),
        "Mangaluru": (12.9141, 74.8560),
        "Belagavi": (15.8497, 74.4977),
        "Kalaburagi": (17.3297, 76.8343)
    }
    
    records = []
    for i in range(1200):
        district = np.random.choice(districts)
        base_lat, base_lon = coords[district]
        
        # Add random scatter to form clusters/hotspots
        lat = base_lat + np.random.normal(0, 0.06)
        lon = base_lon + np.random.normal(0, 0.06)
        
        crime = np.random.choice(crime_categories)
        days_offset = np.random.randint(0, 365)
        date = start_date + timedelta(days=days_offset)
        
        severity = np.random.choice(["Low", "Medium", "High"], p=[0.45, 0.35, 0.20])
        repeat_offender = np.random.choice([True, False], p=[0.22, 0.78])
        status = np.random.choice(["Solved", "Under Investigation", "Unsolved"], p=[0.60, 0.30, 0.10])
        
        records.append({
            "Incident ID": f"FIR-{date.strftime('%Y')}-{i:04d}",
            "Date": date,
            "District": district,
            "Crime Category": crime,
            "Latitude": lat,
            "Longitude": lon,
            "Severity": severity,
            "Repeat Offender": repeat_offender,
            "Status": status
        })
        
    df = pd.DataFrame(records)
    # Severity value for mapping sized bubbles
    df["Severity_Val"] = df["Severity"].map({"Low": 6, "Medium": 12, "High": 22})
    return df

# Load mock data
df_all = generate_mock_data()


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
# 5. Sidebar Configuration & Filters
# ----------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 15px 0 5px 0;">
    <h2 style="color: #eab308; font-size: 20px; font-weight: 800; margin: 0; font-family: 'Outfit';">KSP INTELLIGENCE</h2>
    <p style="color: #94a3b8; font-size: 12px; margin: 0;">Command Portal v1.2</p>
</div>
<hr style="margin-top: 10px; margin-bottom: 20px; border-color: #334155;" />
""", unsafe_allow_html=True)

st.sidebar.subheader("🧭 Navigation Menu")
page = st.sidebar.radio(
    "Select System Module",
    ["📊 Dashboard Overview", "📍 GIS Mapping & Hotspots", "🔮 ML Crime Predictions", "🕸️ Criminal Network Analysis"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr style='border-color: #334155; margin: 20px 0;' />", unsafe_allow_html=True)
st.sidebar.subheader("🔍 Query Filters")

# District Filter
districts = ["All Districts"] + list(df_all["District"].unique())
selected_district = st.sidebar.selectbox("Jurisdiction", districts)

# Crime Class Filter
crime_categories = ["All Categories"] + list(df_all["Crime Category"].unique())
selected_crime = st.sidebar.selectbox("Offense Category", crime_categories)

# Time Frame Filter
time_filter = st.sidebar.selectbox(
    "Reporting Period",
    ["Last 12 Months", "Last 6 Months", "Last 30 Days"]
)

# Apply Filter logic
filtered_df = df_all.copy()

# Date filter
if time_filter == "Last 6 Months":
    cutoff = datetime.now() - timedelta(days=180)
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]
elif time_filter == "Last 30 Days":
    cutoff = datetime.now() - timedelta(days=30)
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]

# District filter
if selected_district != "All Districts":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

# Crime Category filter
if selected_crime != "All Categories":
    filtered_df = filtered_df[filtered_df["Crime Category"] == selected_crime]


# ----------------------------------------------------
# 6. Page 1: Dashboard Overview
# ----------------------------------------------------
if page == "📊 Dashboard Overview":
    render_header("Overview")
    
    # 6.1 Core Metrics Calculation
    total_crimes = len(filtered_df)
    
    # Let's count Hotspots based on density approximation
    # Group coordinates to round values representing dense areas
    filtered_df['lat_round'] = filtered_df['Latitude'].round(2)
    filtered_df['lon_round'] = filtered_df['Longitude'].round(2)
    hotspots_count = filtered_df.groupby(['lat_round', 'lon_round']).filter(lambda x: len(x) >= 6)['lat_round'].nunique()
    # Default minimum hotspots
    if hotspots_count == 0 and total_crimes > 0:
        hotspots_count = int(total_crimes * 0.03) + 1
    elif total_crimes == 0:
        hotspots_count = 0
        
    repeat_offenders_count = len(filtered_df[filtered_df["Repeat Offender"] == True])
    repeat_pct = (repeat_offenders_count / total_crimes * 100) if total_crimes > 0 else 0
    
    # Districts status calculation
    district_counts = filtered_df.groupby("District").size()
    high_risk_districts = len(district_counts[district_counts > (total_crimes / len(districts) * 1.1)]) if len(district_counts) > 0 else 0
    
    # 6.2 Display Metric Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        draw_kpi_card("Total Crimes Registered", f"{total_crimes:,}", "↓ 4.2% from prior period", "#3B82F6")
    with kpi_col2:
        draw_kpi_card("Hotspots Detected", f"{hotspots_count}", "Active high-risk clusters", "#EF4444")
    with kpi_col3:
        draw_kpi_card("Repeat Offenders", f"{repeat_offenders_count:,}", f"{repeat_pct:.1f}% Recidivism rate", "#F59E0B")
    with kpi_col4:
        draw_kpi_card("High Risk Jurisdictions", f"{high_risk_districts}", "Under critical surveillance", "#10B981")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 6.3 Charts Section
    col_left, col_right = st.columns([8, 7])
    
    with col_left:
        st.subheader("📈 Monthly Incident Trajectory")
        
        # Monthly aggregates for line chart
        df_monthly = filtered_df.copy()
        df_monthly['YearMonth'] = df_monthly['Date'].dt.to_period('M')
        monthly_trend = df_monthly.groupby('YearMonth').size().reset_index(name='Incident Count')
        monthly_trend['YearMonth'] = monthly_trend['YearMonth'].dt.to_timestamp()
        
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
            st.info("No data available for the selected filters.")

        st.subheader("📊 Category Classification Analysis")
        # Donut Chart for crime classes
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
            st.info("No category data available.")
            
    with col_right:
        st.subheader("🏢 Distribution by Police District")
        
        # Bar chart for districts
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
            st.info("No district data available.")
            
        st.subheader("📰 Recent Incident Logs")
        if not filtered_df.empty:
            recent_logs = filtered_df.sort_values(by="Date", ascending=False).head(5)
            # Style table representation
            st.dataframe(
                recent_logs[["Incident ID", "Date", "District", "Crime Category", "Severity", "Status"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No logs found.")


# ----------------------------------------------------
# 7. Page 2: GIS Map Placeholder
# ----------------------------------------------------
elif page == "📍 GIS Mapping & Hotspots":
    render_header("GIS Mapping & Hotspots")
    
    st.subheader("🗺️ Spatial Distribution & Cluster Mapping")
    st.markdown(
        "Interactive GIS tracking dashboard utilizing simulated GPS telemetry from emergency responder networks. "
        "Filter and analyze clustering patterns to allocate patrol assets efficiently."
    )
    
    # 7.1 Selection Tabs
    tab_scatter, tab_heatmap = st.tabs(["🔴 Incident Location Mapping", "🔥 Crime Density Heatmap"])
    
    with tab_scatter:
        if not filtered_df.empty:
            # Mapbox Scatter Plot
            fig_map = px.scatter_mapbox(
                filtered_df, 
                lat="Latitude", 
                lon="Longitude", 
                color="Crime Category", 
                size="Severity_Val",
                hover_name="Incident ID", 
                hover_data=["District", "Severity", "Status"],
                zoom=6.8, 
                mapbox_style="carto-darkmatter",
                color_discrete_sequence=px.colors.qualitative.Set1,
                title="Geographical Plot of Registered Incidents"
            )
            fig_map.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                margin=dict(l=0, r=0, t=30, b=0),
                height=550
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No incidents map coordinates match your query filter criteria.")
            
    with tab_heatmap:
        if not filtered_df.empty:
            # Mapbox Density Heatmap
            fig_heatmap = px.density_mapbox(
                filtered_df,
                lat="Latitude",
                lon="Longitude",
                z="Severity_Val",
                radius=18,
                zoom=6.8,
                mapbox_style="carto-darkmatter",
                color_continuous_scale="Viridis",
                title="High-Density Crime Hotspots (Kernel Density Approximation)"
            )
            fig_heatmap.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                margin=dict(l=0, r=0, t=30, b=0),
                height=550
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("No incident coordinates available to run density modeling.")

    # 7.2 Auxiliary Information
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
# 8. Page 3: ML Predictions Placeholder
# ----------------------------------------------------
elif page == "🔮 ML Crime Predictions":
    render_header("ML Crime Predictions")
    
    st.subheader("📊 Volume Forecasting & Recidivism Predictors")
    st.markdown(
        "Leveraging historical datasets and ensemble regression algorithms, this interface projects future crime rates "
        "and assesses individual recidivism risk factors."
    )
    
    tab_forecast, tab_recidivism = st.tabs(["📈 6-Month Crime Volume Forecast", "🧠 Recidivism Risk Assessor"])
    
    with tab_forecast:
        st.markdown("#### Monthly Crime Volume Predictions")
        st.markdown("Forecasting regional crime rates based on ARIMA-LSTM hybrid network model runs.")
        
        # 8.1 Construct Forecast Graph
        df_monthly = filtered_df.copy()
        df_monthly['YearMonth'] = df_monthly['Date'].dt.to_period('M')
        monthly_trend = df_monthly.groupby('YearMonth').size().reset_index(name='Incidents')
        monthly_trend['YearMonth'] = monthly_trend['YearMonth'].dt.to_timestamp()
        monthly_trend = monthly_trend.sort_values('YearMonth')
        
        if len(monthly_trend) >= 3:
            last_date = monthly_trend['YearMonth'].iloc[-1]
            forecast_dates = [last_date + timedelta(days=31*i) for i in range(1, 7)]
            last_val = monthly_trend['Incidents'].iloc[-1]
            
            # Simulated model forecast with uncertainty
            forecast_vals = []
            upper_bound = []
            lower_bound = []
            
            curr = last_val
            for i in range(6):
                # Simulated trend with slight variance
                curr = curr * np.random.uniform(0.97, 1.04)
                forecast_vals.append(curr)
                # Expand uncertainty bounds over time
                variance = curr * 0.15 * (i + 1)
                upper_bound.append(curr + variance)
                lower_bound.append(max(0, curr - variance))
                
            forecast_df = pd.DataFrame({
                'YearMonth': forecast_dates,
                'Incidents': forecast_vals,
                'Upper': upper_bound,
                'Lower': lower_bound
            })
            
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
            
            # Uncertainty Band
            fig_fc.add_trace(go.Scatter(
                x=forecast_df['YearMonth'].tolist() + forecast_df['YearMonth'].tolist()[::-1],
                y=forecast_df['Upper'].tolist() + forecast_df['Lower'].tolist()[::-1],
                fill='between',
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
            st.info("Insufficient data points in current filter subset to compute ARIMA forecast layers. Select 'All Districts' to view details.")
            
    with tab_recidivism:
        st.markdown("#### Interactive Recidivism Risk Profiler")
        st.write("Determine risk parameters based on demographic, historical offender profiles and environmental factors.")
        
        col_inp, col_gauge = st.columns([1, 1])
        with col_inp:
            age = st.slider("Offender Age", 18, 90, 27)
            prev_convictions = st.slider("Prior Offences Count", 0, 15, 3)
            offence_class = st.selectbox("Offence Category Profile", ["Theft", "Cyber Crime", "Assault", "Narcotics", "Robbery"])
            employment = st.selectbox("Employment Status Profile", ["Unemployed", "Underemployed / Part-time", "Full-time Employed"])
            rehab_status = st.radio("Completed Rehabilitation Programs", ["No", "Yes"])
            
        with col_gauge:
            # Deterministic calculation + slight variance for risk score mapping
            base_score = 15 + (prev_convictions * 12) - (age - 18) * 0.7
            if employment == "Full-time Employed":
                base_score -= 18
            elif employment == "Unemployed":
                base_score += 12
                
            if offence_class in ["Robbery", "Narcotics"]:
                base_score += 15
                
            if rehab_status == "Yes":
                base_score -= 15
                
            risk_score = min(max(int(base_score), 5), 98)
            
            if risk_score < 35:
                risk_lbl = "LOW RISK"
                risk_col = "#10B981"
            elif risk_score < 70:
                risk_lbl = "MODERATE RISK"
                risk_col = "#F59E0B"
            else:
                risk_lbl = "HIGH RISK"
                risk_col = "#EF4444"
                
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
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown(f"""
            <div style="background-color: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 15px; border-radius: 8px; text-align: center;">
                <span style="font-weight: bold; color: {risk_col};">{risk_lbl} Profile Alert:</span>
                Based on historical patterns, this offender profile shows a <strong>{risk_score}%</strong> likelihood of re-offending. Recommended intervention: 
                {"Standard monitoring check-ins." if risk_score < 35 else "Mandatory community counseling." if risk_score < 70 else "Intense supervision and probation alert list."}
            </div>
            """, unsafe_allow_html=True)


# ----------------------------------------------------
# 9. Page 4: Criminal Network Analysis Placeholder
# ----------------------------------------------------
elif page == "🕸️ Criminal Network Analysis":
    render_header("Criminal Network Analysis")
    
    st.subheader("🕸️ Syndicate Connectivity & Association Linkages")
    st.markdown(
        "Mapping syndicate associations, accomplice communication vectors, and financial linkages. "
        "Identify kingpins and bridge connections in active investigations."
    )
    
    col_net, col_profile = st.columns([9, 6])
    
    # 9.1 Syndicate Network Setup
    nodes = {
        "Vijay Gowda (Kingpin)": {"pos": (0, 0), "type": "Leader", "risk": "Critical", "cases": 12},
        "Rohan D'Souza (Finance)": {"pos": (1.2, 0.8), "type": "Lieutenant", "risk": "High", "cases": 8},
        "Anand Kumar (Operations)": {"pos": (-1.2, 0.8), "type": "Lieutenant", "risk": "High", "cases": 9},
        "Shabir Ahmed (Logistics)": {"pos": (1.2, -0.8), "type": "Lieutenant", "risk": "High", "cases": 5},
        "Chethan S. (Enforcer)": {"pos": (-1.2, -0.8), "type": "Lieutenant", "risk": "High", "cases": 11},
        "Raghu Gowda (Associate)": {"pos": (2.3, 1.4), "type": "Associate", "risk": "Medium", "cases": 4},
        "Sunil P. (Associate)": {"pos": (2.0, -1.5), "type": "Associate", "risk": "Medium", "cases": 3},
        "Imran Ali (Associate)": {"pos": (-2.3, -1.4), "type": "Associate", "risk": "Medium", "cases": 2},
        "Appu Swamy (Associate)": {"pos": (-2.0, 1.5), "type": "Associate", "risk": "Medium", "cases": 4}
    }
    
    edges = [
        ("Vijay Gowda (Kingpin)", "Rohan D'Souza (Finance)"),
        ("Vijay Gowda (Kingpin)", "Anand Kumar (Operations)"),
        ("Vijay Gowda (Kingpin)", "Shabir Ahmed (Logistics)"),
        ("Vijay Gowda (Kingpin)", "Chethan S. (Enforcer)"),
        ("Rohan D'Souza (Finance)", "Raghu Gowda (Associate)"),
        ("Shabir Ahmed (Logistics)", "Sunil P. (Associate)"),
        ("Chethan S. (Enforcer)", "Imran Ali (Associate)"),
        ("Anand Kumar (Operations)", "Appu Swamy (Associate)"),
        ("Anand Kumar (Operations)", "Rohan D'Souza (Finance)"),
        ("Shabir Ahmed (Logistics)", "Chethan S. (Enforcer)")
    ]
    
    with col_net:
        # Create Scatter Plot for Network Structure
        fig_net = go.Figure()
        
        # Add Edge Lines
        edge_x = []
        edge_y = []
        for edge in edges:
            x0, y0 = nodes[edge[0]]["pos"]
            x1, y1 = nodes[edge[1]]["pos"]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
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
        
        for name, info in nodes.items():
            x, y = info["pos"]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Name: {name}<br>Role: {info['type']}<br>Risk Rating: {info['risk']}<br>FIR Cases: {info['cases']}")
            
            # Node Coloring
            if info["risk"] == "Critical":
                node_color.append("#EF4444")  # Red
                node_size.append(28)
            elif info["risk"] == "High":
                node_color.append("#F59E0B")  # Amber
                node_size.append(22)
            else:
                node_color.append("#3B82F6")  # Blue
                node_size.append(16)
                
        fig_net.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[n.split(" (")[0] for n in nodes.keys()],
            textposition="top center",
            hovertext=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(color='#0f172a', width=2)
            )
        ))
        
        fig_net.update_layout(
            title="Interactive Link-Node Gang Association Map",
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
        suspect_key = st.selectbox("Select Target Suspect Profile", list(nodes.keys()))
        s_info = nodes[suspect_key]
        
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
                    <td style="padding: 8px 0; text-align: right;">{selected_district if selected_district != "All Districts" else "Bengaluru Area"}</td>
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
            if suspect_key in edge:
                other = edge[0] if edge[1] == suspect_key else edge[1]
                associates.append(other.split(' (')[0])
                
        st.markdown("##### 👥 Direct Linkage Connections:")
        if associates:
            for assoc in set(associates):
                st.markdown(f"- **{assoc}** - Accomplice link verified by cell tower correlations")
        else:
            st.markdown("*No direct active syndicate edges detected.*")
