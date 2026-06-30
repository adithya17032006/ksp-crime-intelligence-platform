import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
from datetime import datetime, timedelta

from api_client import KSPAPIClient
from config import API_BASE_URL

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KSP Crime Intelligence Platform",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0a0f1e; }
h1, h2, h3, h4, h5, h6    { font-family: 'Outfit', sans-serif; }
#MainMenu, footer          { visibility: hidden; }

/* Auth form container */
.auth-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8);
}
.ksp-brand {
    text-align: center;
    padding: 20px 0 30px 0;
}
.ksp-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1e3a8a, #1e40af);
    border: 2px solid #eab308;
    border-radius: 50%;
    width: 80px; height: 80px;
    line-height: 80px;
    font-size: 36px;
    margin-bottom: 16px;
}

/* Metric cards */
.metric-card-hover { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.metric-card-hover:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,0.5); }

/* Chat bubbles */
.chat-officer {
    background: rgba(59,130,246,0.15); border: 1px solid #3B82F6;
    border-radius: 12px 12px 2px 12px; padding: 10px 15px;
    margin: 6px 0; color: #e2e8f0; font-size: 14px; text-align: right;
}
.chat-ai {
    background: rgba(16,185,129,0.1); border: 1px solid #10b981;
    border-radius: 12px 12px 12px 2px; padding: 10px 15px;
    margin: 6px 0; color: #e2e8f0; font-size: 14px;
}

/* Rank badge */
.rank-badge {
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
    text-transform: uppercase;
}
.rank-5 { background: rgba(234,179,8,0.2);  color: #eab308; border: 1px solid #eab308; }
.rank-4 { background: rgba(139,92,246,0.2); color: #a78bfa; border: 1px solid #a78bfa; }
.rank-3 { background: rgba(59,130,246,0.2); color: #60a5fa; border: 1px solid #60a5fa; }
.rank-2 { background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid #34d399; }
.rank-1 { background: rgba(148,163,184,0.2);color: #94a3b8; border: 1px solid #94a3b8; }

/* Input styling */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > textarea {
    background-color: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────
if "officer" not in st.session_state:
    st.session_state.officer = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"
if "general_chat_history" not in st.session_state:
    st.session_state.general_chat_history = []
if "case_chat_history" not in st.session_state:
    st.session_state.case_chat_history = []

API_URL = API_BASE_URL

# ─────────────────────────────────────────────────────────
# HELPER: DESIGNATION BADGE
# ─────────────────────────────────────────────────────────
def rank_badge(designation: str, access_level: int) -> str:
    return f'<span class="rank-badge rank-{access_level}">{designation}</span>'

# ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
#  AUTH PAGES (shown when not logged in)
# ══════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────
def render_login_page():
    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown("""
        <div class="ksp-brand">
            <div class="ksp-badge">🚨</div>
            <h1 style="color:#ffffff; font-size:28px; font-weight:800; margin:0;">
                KARNATAKA STATE POLICE
            </h1>
            <p style="color:#94a3b8; font-size:14px; margin:4px 0 0 0;">
                Crime Intelligence Platform — Secure Officer Portal
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown("### 🔐 Officer Login")
            st.markdown("<p style='color:#64748b; font-size:13px; margin-top:-8px;'>Use your registered email and password to access the portal.</p>", unsafe_allow_html=True)

            email    = st.text_input("Official Email Address", placeholder="officer@ksp.gov.in", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

            col_btn1, col_btn2 = st.columns([3, 2])
            with col_btn1:
                login_btn = st.button("🔓 Login to Portal", use_container_width=True, type="primary", key="login_btn")
            with col_btn2:
                if st.button("📝 Register", use_container_width=True, key="go_register"):
                    st.session_state.auth_page = "register"
                    st.rerun()

            if login_btn:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        try:
                            resp = requests.post(
                                f"{API_URL}/api/auth/login",
                                json={"email": email, "password": password},
                                timeout=15
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                st.session_state.officer = data["officer"]
                                st.session_state.officer["allowed_modules"] = data["allowed_modules"]
                                st.success(f"✅ Welcome, {data['officer']['full_name']}!")
                                st.rerun()
                            else:
                                detail = resp.json().get("detail", "Login failed.")
                                st.error(f"❌ {detail}")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Cannot connect to the backend API. Please ensure the server is running.")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

            st.markdown("</div>", unsafe_allow_html=True)

        # Designation access legend
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🏛️ Access Levels by Designation")
        tiers = [
            ("SP", 5, "Full Admin — All Modules"),
            ("DSP", 4, "All Operational Modules"),
            ("Inspector", 3, "Cases, FIR, Predictions, Dashboards"),
            ("SI / PSI", 2, "FIR Processing, Cases, Dashboards"),
            ("HC / PC", 1, "AI Assistant Only"),
        ]
        cols = st.columns(len(tiers))
        for col, (desig, lvl, desc) in zip(cols, tiers):
            with col:
                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.8); border:1px solid #334155; border-radius:10px;
                            padding:14px 10px; text-align:center; border-top:3px solid
                            {'#eab308' if lvl==5 else '#a78bfa' if lvl==4 else '#60a5fa' if lvl==3 else '#34d399' if lvl==2 else '#94a3b8'};">
                    <div style="font-size:22px; margin-bottom:6px;">
                        {'👑' if lvl==5 else '⭐' if lvl==4 else '🎖️' if lvl==3 else '🛡️' if lvl==2 else '🪖'}
                    </div>
                    <div class="rank-badge rank-{lvl}" style="margin-bottom:8px;">{desig}</div><br>
                    <span style="color:#64748b; font-size:11px;">{desc}</span>
                </div>
                """, unsafe_allow_html=True)


def render_register_page():
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
        <div class="ksp-brand">
            <div class="ksp-badge">🚨</div>
            <h1 style="color:#ffffff; font-size:28px; font-weight:800; margin:0;">OFFICER REGISTRATION</h1>
            <p style="color:#94a3b8; font-size:14px; margin:4px 0 0 0;">Karnataka State Police — New Officer Enrollment</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("### 📋 New Officer Registration")
        st.markdown("<p style='color:#64748b; font-size:13px; margin-top:-8px;'>All fields marked * are required. Use your official police email.</p>", unsafe_allow_html=True)

        with st.form("registration_form", clear_on_submit=False):
            st.markdown("#### 👤 Personal Information")
            rc1, rc2 = st.columns(2)
            with rc1:
                full_name = st.text_input("Full Name *", placeholder="e.g., Ramesh Kumar")
                police_id = st.text_input("Police ID / Service Number *", placeholder="e.g., KSP/2024/001")
                badge_number = st.text_input("Badge Number", placeholder="e.g., B-4521")
            with rc2:
                phone = st.text_input("Mobile Number *", placeholder="e.g., 9876543210")
                designation = st.selectbox("Designation *", [
                    "SP — Superintendent of Police",
                    "DSP — Deputy Superintendent of Police",
                    "Inspector",
                    "SI — Sub-Inspector",
                    "PSI — Police Sub-Inspector",
                    "HC — Head Constable",
                    "PC — Police Constable",
                ])
                joined_date = st.date_input("Date of Joining", value=datetime.now().date())

            st.markdown("#### 🏢 Posting Details")
            pc1, pc2 = st.columns(2)
            with pc1:
                district = st.selectbox("District / Division *", [
                    "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Hassan",
                    "Mangaluru", "Hubballi-Dharwad", "Belagavi", "Kalaburagi",
                    "Bagalkot", "Vijayapura", "Shivamogga", "Tumakuru",
                    "Davanagere", "Ballari", "Raichur", "Koppal", "Gadag",
                    "Dharwad", "Uttara Kannada", "Udupi", "Chikkamagaluru",
                    "Kodagu", "Chamarajanagar", "Mandya", "Ramanagara",
                    "Chikkaballapur", "Kolar", "Chitradurga", "Bidar", "Yadgir"
                ])
            with pc2:
                police_station = st.text_input("Police Station *", placeholder="e.g., Jayanagar PS")

            st.markdown("#### 🔒 Account Credentials")
            ac1, ac2 = st.columns(2)
            with ac1:
                email = st.text_input("Official Email Address *", placeholder="officer@ksp.gov.in")
                password = st.text_input("Create Password *", type="password", placeholder="Min 8 characters")
            with ac2:
                confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")

            st.markdown("<br>", unsafe_allow_html=True)
            submit_col1, submit_col2 = st.columns([3, 2])
            with submit_col1:
                submitted = st.form_submit_button("✅ Register Officer Account", use_container_width=True, type="primary")
            with submit_col2:
                go_login = st.form_submit_button("← Back to Login", use_container_width=True)

            if go_login:
                st.session_state.auth_page = "login"
                st.rerun()

            if submitted:
                # Validation
                errors = []
                if not full_name: errors.append("Full Name is required.")
                if not police_id: errors.append("Police ID is required.")
                if not phone or not phone.isdigit() or len(phone) != 10:
                    errors.append("Valid 10-digit mobile number is required.")
                if not district: errors.append("District is required.")
                if not police_station: errors.append("Police Station is required.")
                if not email or "@" not in email: errors.append("Valid email is required.")
                if not password or len(password) < 8: errors.append("Password must be at least 8 characters.")
                if password != confirm_password: errors.append("Passwords do not match.")

                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    # Clean designation value (strip label suffix)
                    desig_map = {
                        "SP — Superintendent of Police": "SP",
                        "DSP — Deputy Superintendent of Police": "DSP",
                        "Inspector": "Inspector",
                        "SI — Sub-Inspector": "SI",
                        "PSI — Police Sub-Inspector": "PSI",
                        "HC — Head Constable": "HC",
                        "PC — Police Constable": "PC",
                    }
                    desig_clean = desig_map[designation]

                    with st.spinner("Creating your account..."):
                        try:
                            resp = requests.post(
                                f"{API_URL}/api/auth/register",
                                json={
                                    "email": email,
                                    "password": password,
                                    "police_id": police_id,
                                    "full_name": full_name,
                                    "designation": desig_clean,
                                    "badge_number": badge_number,
                                    "district": district,
                                    "police_station": police_station,
                                    "phone": phone,
                                },
                                timeout=20
                            )
                            if resp.status_code == 201:
                                st.success(f"✅ Registration successful! Welcome, {full_name}. Please check your email to verify your account, then log in.")
                                st.balloons()
                                st.session_state.auth_page = "login"
                            else:
                                detail = resp.json().get("detail", "Registration failed.")
                                st.error(f"❌ {detail}")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Cannot connect to the backend. Please ensure the API server is running.")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# RENDER AUTH GATE — show login/register if not authenticated
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.officer is None:
    if st.session_state.auth_page == "login":
        render_login_page()
    else:
        render_register_page()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  AUTHENTICATED PORTAL
# ══════════════════════════════════════════════════════════════════════════════
officer         = st.session_state.officer
access_level    = officer.get("access_level", 1)
allowed_modules = officer.get("allowed_modules", ["🧠 AI Assistant & FIR Processing"])
full_name       = officer.get("full_name", "Officer")
designation     = officer.get("designation", "PC")
police_id       = officer.get("police_id", "—")
district        = officer.get("district", "—")
station         = officer.get("police_station", "—")

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b); border-bottom:2px solid #eab308;
            padding:20px 15px 15px 15px; margin:-20px -15px 15px -15px;">
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="background:linear-gradient(135deg,#1e3a8a,#1e40af); border:2px solid #eab308;
                    border-radius:50%; width:48px; height:48px; display:flex; align-items:center;
                    justify-content:center; font-size:22px; flex-shrink:0;">🚨</div>
        <div>
            <div style="color:#ffffff; font-weight:800; font-size:14px; font-family:'Outfit';">KSP INTELLIGENCE</div>
            <div style="color:#94a3b8; font-size:11px;">Command Portal v3.0</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Officer info card
rank_colors = {5: "#eab308", 4: "#a78bfa", 3: "#60a5fa", 2: "#34d399", 1: "#94a3b8"}
rcolor = rank_colors.get(access_level, "#94a3b8")
st.sidebar.markdown(f"""
<div style="background:rgba(15,23,42,0.8); border:1px solid #334155; border-left:4px solid {rcolor};
            border-radius:8px; padding:14px; margin-bottom:15px;">
    <div style="color:#f8fafc; font-weight:700; font-size:14px;">{full_name}</div>
    <div style="margin:4px 0;">
        <span class="rank-badge rank-{access_level}">{designation}</span>
    </div>
    <div style="color:#64748b; font-size:11px; margin-top:6px;">
        🪪 {police_id} &nbsp;|&nbsp; 📍 {district}
    </div>
    <div style="color:#64748b; font-size:11px;">🏢 {station}</div>
</div>
""", unsafe_allow_html=True)

# API Status
api_client   = KSPAPIClient(base_url=API_BASE_URL)
api_connected = api_client.check_health()
status_html = """<div style="background:rgba(16,185,129,0.15); border:1px solid #10b981; padding:8px;
    border-radius:6px; text-align:center; color:#10b981; font-weight:700; font-size:12px; margin-bottom:12px;">
    🟢 Backend Connected</div>""" if api_connected else \
    """<div style="background:rgba(239,68,68,0.15); border:1px solid #ef4444; padding:8px;
    border-radius:6px; text-align:center; color:#ef4444; font-weight:700; font-size:12px; margin-bottom:12px;">
    🔴 Backend Offline</div>"""
st.sidebar.markdown(status_html, unsafe_allow_html=True)

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("<hr style='border-color:#334155; margin:12px 0;'>", unsafe_allow_html=True)

# Navigation — filtered by allowed_modules
st.sidebar.markdown("**🧭 Navigation**")
page = st.sidebar.radio("Select Module", allowed_modules, label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-color:#334155; margin:12px 0;'>", unsafe_allow_html=True)

# Logout
if st.sidebar.button("🚪 Logout", use_container_width=True):
    token = officer.get("access_token", "")
    try:
        requests.post(f"{API_BASE_URL}/api/auth/logout", json={"access_token": token}, timeout=5)
    except Exception:
        pass
    st.session_state.officer = None
    st.session_state.general_chat_history = []
    st.session_state.case_chat_history = []
    st.rerun()

# ─────────────────────────────────────────────────────────
# LOAD DATA (non-auth pages need it)
# ─────────────────────────────────────────────────────────
df_all = api_client.fetch_incidents()
filtered_df = pd.DataFrame()
selected_district = "All Districts"
selected_crime = "All Categories"

if not df_all.empty:
    st.sidebar.markdown("<hr style='border-color:#334155; margin:12px 0;'>", unsafe_allow_html=True)
    st.sidebar.markdown("**🔍 Query Filters**")
    districts = ["All Districts"] + sorted(list(df_all["District"].unique()))
    selected_district = st.sidebar.selectbox("Jurisdiction", districts)
    crime_categories = ["All Categories"] + sorted(list(df_all["Crime Category"].unique()))
    selected_crime = st.sidebar.selectbox("Offense Category", crime_categories)
    time_filter = st.sidebar.selectbox("Reporting Period", ["All Time", "Last 12 Months", "Last 6 Months", "Last 30 Days"])

    filtered_df = df_all.copy()
    max_date = df_all["Date"].max()
    if time_filter == "Last 12 Months":
        filtered_df = filtered_df[filtered_df["Date"] >= max_date - timedelta(days=365)]
    elif time_filter == "Last 6 Months":
        filtered_df = filtered_df[filtered_df["Date"] >= max_date - timedelta(days=180)]
    elif time_filter == "Last 30 Days":
        filtered_df = filtered_df[filtered_df["Date"] >= max_date - timedelta(days=30)]
    if selected_district != "All Districts":
        filtered_df = filtered_df[filtered_df["District"] == selected_district]
    if selected_crime != "All Categories":
        filtered_df = filtered_df[filtered_df["Crime Category"] == selected_crime]


# ─────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────
def render_header(title_suffix):
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,#1e3a8a 0%,#0f172a 100%); padding:18px 25px;
                border-radius:10px; border-bottom:4px solid #eab308; margin-bottom:25px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <div>
                <h1 style="color:#fff; margin:0; font-family:'Outfit'; font-size:26px; font-weight:800;">
                    🚨 KARNATAKA STATE POLICE</h1>
                <p style="color:#93c5fd; margin:4px 0 0 0; font-size:13px;">
                    Crime Intelligence Platform &amp; Predictive Analytics Center</p>
            </div>
            <div>
                <div style="background:rgba(234,179,8,0.15); border:1px solid #eab308; padding:6px 14px;
                            border-radius:20px; color:#facc15; font-size:12px; font-weight:700;
                            text-transform:uppercase; letter-spacing:.5px;">{title_suffix}</div>
                <div style="margin-top:6px; text-align:right;">
                    <span class="rank-badge rank-{access_level}">{designation}</span>
                    <span style="color:#64748b; font-size:11px; margin-left:8px;">{full_name}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def draw_kpi_card(title, value, subtitle, border_color="#3B82F6"):
    st.markdown(f"""
    <div class="metric-card-hover" style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);
         border-top:4px solid {border_color}; border-radius:8px; padding:20px;
         box-shadow:0 4px 15px rgba(0,0,0,.3); border:1px solid #334155;
         border-top-color:{border_color}; height:100%;">
        <h4 style="margin:0; color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase;">{title}</h4>
        <h2 style="margin:10px 0 4px 0; font-size:28px; font-weight:800; color:#f8fafc; font-family:'Outfit';">{value}</h2>
        <p style="margin:0; color:#38bdf8; font-size:12px;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def handle_api_error(err_msg):
    if err_msg:
        st.warning(f"⚠️ {err_msg}")


def plot_layout(fig, height=400):
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='#94a3b8', margin=dict(l=20,r=20,t=10,b=20), height=height)
    return fig


# ══════════════════════════════════════════════════════════
#  PAGE ROUTING
# ══════════════════════════════════════════════════════════

# ─── Executive Dashboard ───────────────────────────────────
if page == "📊 Executive Dashboard":
    render_header("Executive Dashboard")
    df_anomalies, err_an = api_client.fetch_anomalies()
    df_centroids, err_ce = api_client.fetch_hotspot_centroids(filtered_df)
    df_risk, err_rk = api_client.fetch_district_risk()
    handle_api_error(err_an or err_ce or err_rk)
    if filtered_df.empty:
        st.warning("⚠️ **The Incidents Database is currently empty or no data matches the filters.**")
        st.info("To proceed, please upload your Crime Incidents CSV file to populate the database.")
        
        csv_file = st.file_uploader("Upload Crime Incidents (CSV)", type=["csv"], key="csv_upload_main")
        if csv_file:
            if st.button("🚀 Load Data to Database", type="primary", use_container_width=True):
                with st.spinner("Uploading and processing CSV..."):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/api/incidents/upload",
                            files={"file": (csv_file.name, csv_file.getvalue(), "text/csv")},
                            timeout=60
                        )
                        if r.status_code == 201:
                            st.success(f"✅ Data loaded successfully! {r.json().get('message')}")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {r.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    else:
        total = len(filtered_df)
        hotspots = len(df_centroids) if not df_centroids.empty else 0
        anomalies_n = len(df_anomalies[df_anomalies["district"].isin(filtered_df["District"].unique())]) if not df_anomalies.empty else 0
        critical = len(df_risk[df_risk["Risk_Level"] == "Critical"]) if not df_risk.empty else 0
        c1, c2, c3, c4 = st.columns(4)
        with c1: draw_kpi_card("Total Crimes", f"{total:,}", "Registered incidents", "#3B82F6")
        with c2: draw_kpi_card("Hotspots", f"{hotspots}", "Active cluster centers", "#EF4444")
        with c3: draw_kpi_card("Anomalies", f"{anomalies_n}", "High priority alerts", "#F59E0B")
        with c4: draw_kpi_card("Critical Districts", f"{critical}", "CRI Critical status", "#10B981")
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📢 Critical Alert Log")
        if not df_anomalies.empty:
            fa = df_anomalies[df_anomalies["district"].isin(filtered_df["District"].unique())].head(5)
            if not fa.empty:
                st.dataframe(fa[["Incident ID","date","district","police_station","crime_type","status"]].rename(
                    columns={"date":"Date","district":"District","police_station":"Station","crime_type":"Crime","status":"Status"}
                ), use_container_width=True, hide_index=True)
            else:
                st.success("No anomalous patterns in current scope.")
        else:
            st.info("No anomaly data from API.")


# ─── Crime Risk Dashboard ──────────────────────────────────
elif page == "⚠️ Crime Risk Dashboard":
    render_header("Crime Risk Index")
    df_risk, err_rk = api_client.fetch_district_risk()
    handle_api_error(err_rk)
    if not df_risk.empty:
        disp = df_risk[df_risk["district"] == selected_district] if selected_district != "All Districts" else df_risk
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📋 District Risk Standings")
            st.dataframe(disp[["district","crime_count","repeat_offenders","CRI","Risk_Level"]].rename(
                columns={"district":"District","crime_count":"Crimes","repeat_offenders":"Recidivists","CRI":"CRI Score","Risk_Level":"Risk Level"}
            ), use_container_width=True, hide_index=True)
        with c2:
            st.subheader("📊 CRI Comparison")
            fig = px.bar(disp.sort_values("CRI"), x="CRI", y="district", orientation="h", color="Risk_Level",
                         color_discrete_map={"Critical":"#EF4444","High":"#F59E0B","Medium":"#3B82F6","Low":"#10B981"})
            st.plotly_chart(plot_layout(fig), use_container_width=True)
    else:
        st.info("Risk data unavailable.")


# ─── Hotspot Dashboard ─────────────────────────────────────
elif page == "🔥 Hotspot Intelligence Dashboard":
    render_header("Hotspot Intelligence")
    df_h, err_h = api_client.fetch_hotspots()
    handle_api_error(err_h)
    if not df_h.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📋 Cluster Analytics")
            st.dataframe(df_h.rename(columns={"cluster":"Cluster ID","crime_count":"Cases"}), use_container_width=True, hide_index=True)
        with c2:
            st.subheader("📊 Incidents per Cluster")
            fig = px.bar(df_h, x="cluster", y="crime_count", color="crime_count", color_continuous_scale="Reds")
            fig.update_layout(xaxis=dict(type='category'), coloraxis_showscale=False)
            st.plotly_chart(plot_layout(fig), use_container_width=True)
    else:
        st.info("Hotspot data unavailable.")


# ─── Patrol Recommendations ────────────────────────────────
elif page == "🛡️ Patrol Recommendation Dashboard":
    render_header("Patrol Recommendations")
    df_p, err_p = api_client.fetch_patrol_priority()
    handle_api_error(err_p)
    if not df_p.empty:
        c1, c2 = st.columns([10, 8])
        with c1:
            st.subheader("📋 Patrol Ranking")
            st.dataframe(df_p[["district","patrol_rank","anomaly_count","priority_score","recommendation"]].rename(
                columns={"district":"District","patrol_rank":"Rank","anomaly_count":"Anomalies","priority_score":"Priority","recommendation":"Action"}
            ), use_container_width=True, hide_index=True)
        with c2:
            st.subheader("📊 Top Priority Districts")
            fig = px.bar(df_p.sort_values("priority_score").tail(10), x="priority_score", y="district",
                         orientation="h", color="priority_score", color_continuous_scale="Oranges")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(plot_layout(fig), use_container_width=True)
    else:
        st.info("Patrol data unavailable.")


# ─── Temporal Trends ───────────────────────────────────────
elif page == "📅 Temporal Trend Dashboard":
    render_header("Temporal Trends")
    df_m, err_m = api_client.fetch_monthly_trends()
    df_w, err_w = api_client.fetch_weekday_trends()
    handle_api_error(err_m or err_w)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Monthly Trajectory")
        if not df_m.empty:
            fig = px.line(df_m, x="month_name", y="crime_count", color_discrete_sequence=["#3B82F6"])
            fig.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=8, color="#facc15"))
            st.plotly_chart(plot_layout(fig), use_container_width=True)
        else:
            st.info("Monthly data unavailable.")
    with c2:
        st.subheader("📅 Weekday Patterns")
        if not df_w.empty:
            fig = px.bar(df_w, x="weekday", y="crime_count", color="crime_count", color_continuous_scale="Purples")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(plot_layout(fig), use_container_width=True)
        else:
            st.info("Weekday data unavailable.")


# ─── GIS Map ───────────────────────────────────────────────
elif page == "📍 GIS Map Dashboard":
    render_header("GIS Map Dashboard")
    st.subheader("🗺️ Spatial Distribution & Cluster Mapping")
    map_sel = st.selectbox("Select GIS Layer", [
        "🚨 General Crime Incidents Map (crime_map.html)",
        "🔥 Crime Hotspots Clusters Map (crime_hotspots.html)",
        "🌡️ Crime Kernel Density Heatmap (crime_heatmap.html)",
        "⚠️ Anomaly Detection Zones Map (crime_anomalies.html)",
    ])
    layer_key = {"🚨 General Crime Incidents Map (crime_map.html)":"crime_map",
                 "🔥 Crime Hotspots Clusters Map (crime_hotspots.html)":"crime_hotspots",
                 "🌡️ Crime Kernel Density Heatmap (crime_heatmap.html)":"crime_heatmap",
                 "⚠️ Anomaly Detection Zones Map (crime_anomalies.html)":"crime_anomalies"}[map_sel]
    tab_html, tab_cent = st.tabs(["🗺️ Folium HTML", "📍 Centroid Map"])
    with tab_html:
        html_str = api_client.fetch_gis_map_layer(layer_key)
        if html_str and len(html_str) > 100:
            st.components.v1.html(html_str, height=550, scrolling=True)
        else:
            st.error(f"Map '{layer_key}' not found. Run the GIS pipeline first.")
    with tab_cent:
        df_c, err_c = api_client.fetch_hotspot_centroids(filtered_df)
        if not df_c.empty:
            fig = px.scatter_mapbox(df_c, lat="centroid_latitude", lon="centroid_longitude",
                                    size="crime_count", color="cluster", hover_name="cluster",
                                    mapbox_style="carto-darkmatter", zoom=6)
            st.plotly_chart(plot_layout(fig, 550), use_container_width=True)
        else:
            st.info("No centroid data available.")


# ─── Crime Prediction (Level ≥ 2) ─────────────────────────
elif page == "🔮 Crime Prediction":
    render_header("Crime Prediction — Live ML")
    if not api_connected:
        st.error("Backend offline.")
    else:
        CRIMES = ["ASSAULT","BURGLARY","CYBERCRIME","FRAUD","HOMICIDE","IDENTITY THEFT","KIDNAPPING","PUBLIC INTOXICATION","ROBBERY","THEFT","TRAFFIC VIOLATION"]
        CITIES = ["AHMEDABAD","BAGALKOT","CHENNAI","GHAZIABAD","HASSAN","LUDHIANA","MUMBAI","PUNE"]
        col_in, col_out = st.columns([1,1])
        with col_in:
            st.markdown("##### 📝 Input Parameters")
            p_city  = st.selectbox("City / District", CITIES)
            p_crime = st.selectbox("Offense Type", CRIMES)
            p_date  = st.date_input("Incident Date", datetime.now())
            p_hour  = st.slider("Incident Hour", 0, 23, 20)
            p_age   = st.number_input("Victim Age", 1, 100, 30)
            run_btn = st.button("🔮 Run Prediction", use_container_width=True, type="primary")
        with col_out:
            st.markdown("##### 📈 Risk Assessment")
            if run_btn:
                payload = {"timestamp": f"{p_date} {p_hour:02d}:00:00", "crime_description": p_crime, "city": p_city, "victim_age": p_age}
                with st.spinner("Running Random Forest Inference..."):
                    try:
                        r = requests.post(f"{API_BASE_URL}/predict-crime", json=payload, timeout=15)
                        if r.status_code == 200:
                            res = r.json().get("analytics_prediction", {})
                            code = res.get("risk_level_code", 0)
                            label = res.get("risk_level_label", "Unknown")
                            prob = res.get("probability_score", 0) * 100
                            gcolor = "#EF4444" if code == 1 else "#10B981"
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number", value=round(prob, 1),
                                title={"text": f"Risk: {label}", "font": {"color": gcolor, "size": 15}},
                                number={"suffix": "%", "font": {"color": gcolor, "size": 36}},
                                gauge={"axis": {"range": [0,100]}, "bar": {"color": gcolor}, "bgcolor": "#1e293b",
                                       "steps": [{"range":[0,40],"color":"rgba(16,185,129,.15)"},
                                                 {"range":[40,70],"color":"rgba(245,158,11,.15)"},
                                                 {"range":[70,100],"color":"rgba(239,68,68,.15)"}]}
                            ))
                            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', height=270, margin=dict(l=20,r=20,t=50,b=20))
                            st.plotly_chart(fig, use_container_width=True)
                            st.markdown(f"""<div style="background:{'rgba(239,68,68,.1)' if code==1 else 'rgba(16,185,129,.1)'}; border:1px solid {gcolor}; padding:12px; border-radius:8px;">
                                <strong style="color:{gcolor}; font-size:16px;">{'⚠️ HIGH RISK' if code==1 else '✅ LOW RISK'}</strong><br/>
                                <span style="color:#94a3b8;">Confidence: {prob:.1f}% | {p_city} | {p_crime}</span></div>""", unsafe_allow_html=True)
                        else:
                            st.error(f"API Error: {r.text}")
                    except Exception as e:
                        st.error(f"Failed: {e}")
            else:
                st.markdown("""<div style="background:rgba(30,41,59,.5); border:1px dashed #334155; padding:40px;
                    border-radius:8px; text-align:center; color:#64748b;">
                    <div style="font-size:40px; margin-bottom:12px;">🔮</div>
                    <p>Set parameters and click Run Prediction</p></div>""", unsafe_allow_html=True)


# ─── Feature Importance ────────────────────────────────────
elif page == "🧬 Feature Importance":
    render_header("Feature Importance — Live ML")
    with st.spinner("Fetching from ML model..."):
        try:
            r = requests.get(f"{API_BASE_URL}/feature-importance", timeout=15)
            if r.status_code == 200:
                rankings = r.json().get("feature_rankings", [])
                df_f = pd.DataFrame(rankings)
                c1, c2 = st.columns([3,2])
                with c1:
                    fig = px.bar(df_f.sort_values("importance_weight"), x="importance_weight", y="feature",
                                 orientation="h", color="importance_weight", color_continuous_scale="Viridis",
                                 title="Random Forest Feature Importance")
                    fig.update_layout(coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_color='#94a3b8', height=420, margin=dict(l=20,r=20,t=50,b=20))
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    st.markdown("##### 📋 Feature Weights")
                    df_f["importance_weight"] = df_f["importance_weight"].apply(lambda x: f"{x:.4f}")
                    df_f.columns = ["Feature","Weight"]
                    st.dataframe(df_f, use_container_width=True, hide_index=True)
                    if rankings:
                        top = rankings[0]
                        st.markdown(f"""<div style="background:rgba(59,130,246,.1); border:1px solid #3B82F6;
                            padding:15px; border-radius:8px; margin-top:10px;">
                            <h4 style="color:#60a5fa; margin:0;">🏆 Top Predictor</h4>
                            <p style="color:#e2e8f0; font-size:20px; font-weight:700; margin:8px 0 0;">{top['feature']}</p>
                            </div>""", unsafe_allow_html=True)
            else:
                st.error(f"API error: {r.text}")
        except Exception as e:
            st.error(f"Failed: {e}")


# ─── Case Management ───────────────────────────────────────
elif page == "📂 Case Management System":
    render_header("Case Management System")
    try:
        cases_r = requests.get(f"{API_BASE_URL}/api/cases/", timeout=15)
        all_cases = cases_r.json() if cases_r.status_code == 200 else []
    except Exception as e:
        st.error(f"Failed to load cases: {e}")
        all_cases = []

    col_list, col_detail = st.columns([2, 3])
    with col_list:
        st.markdown("#### 📋 All Cases")
        if not all_cases:
            st.info("No cases in database. Process an FIR to create one.")
        else:
            if "selected_case_id" not in st.session_state:
                st.session_state.selected_case_id = None
            for case in all_cases:
                ri = "🔴" if case.get("risk_level_label") == "High Risk" else "🟢"
                label = f"{ri} Case #{case['id']} | {case['crime_description']} | {case['city']} | {case['timestamp']}"
                if st.button(label, key=f"c_{case['id']}", use_container_width=True):
                    st.session_state.selected_case_id = case["id"]
                    st.session_state.case_chat_history = []

    with col_detail:
        if not st.session_state.get("selected_case_id"):
            st.markdown("""<div style="background:rgba(30,41,59,.5); border:1px dashed #334155;
                padding:60px; border-radius:8px; text-align:center; color:#64748b;">
                <div style="font-size:48px; margin-bottom:12px;">📂</div>
                <p>Select a case to view details, upload documents, and consult AI.</p></div>""", unsafe_allow_html=True)
        else:
            sid = st.session_state.selected_case_id
            sc = next((c for c in all_cases if c["id"] == sid), None)
            if sc:
                rc = "#EF4444" if sc.get("risk_level_label") == "High Risk" else "#10B981"
                st.markdown(f"""<div style="background:linear-gradient(135deg,#0f172a,#1e293b);
                    border:1px solid #334155; border-left:5px solid {rc}; border-radius:8px; padding:18px; margin-bottom:15px;">
                    <h3 style="color:#f8fafc; margin:0;">Case #{sc['id']} — {sc['crime_description']}</h3>
                    <p style="color:#94a3b8; margin:6px 0 0;">📍 {sc['city']} &nbsp;|&nbsp; 📅 {sc['timestamp']} &nbsp;|&nbsp;
                       <span style="color:{rc};">⚡ {sc['risk_level_label']}</span> &nbsp;|&nbsp;
                       👮 {sc.get('assigned_officer') or 'Unassigned'}</p>
                </div>""", unsafe_allow_html=True)

                t1, t2, t3 = st.tabs(["📑 Documents", "📤 Upload", "🤖 AI Assistant"])

                with t1:
                    docs = sc.get("documents", [])
                    if docs:
                        for d in docs:
                            st.markdown(f"""<div style="background:rgba(30,41,59,.7); border:1px solid #334155;
                                padding:10px 14px; border-radius:6px; margin-bottom:6px;">
                                📄 <strong style="color:#e2e8f0;">{d['filename']}</strong><br>
                                <span style="color:#64748b; font-size:11px;">By {d.get('uploaded_by','?')} on {d.get('uploaded_at','')}</span>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("No documents attached.")

                with t2:
                    # Check upload permission (access_level ≥ 2 can upload)
                    if access_level >= 2:
                        st.caption(f"Uploading as: **{full_name}** ({designation})")
                        uf = st.file_uploader("Select file", type=["pdf","jpg","png","txt","docx"], key=f"uf_{sid}")
                        if st.button("📤 Upload to Case", use_container_width=True, key=f"ubtn_{sid}"):
                            if uf:
                                with st.spinner("Uploading..."):
                                    try:
                                        up_r = requests.post(
                                            f"{API_BASE_URL}/api/cases/{sid}/upload",
                                            files={"file": (uf.name, uf.getvalue(), uf.type)},
                                            params={"officer_name": full_name}, timeout=30
                                        )
                                        if up_r.status_code == 200:
                                            st.success(f"✅ Uploaded '{uf.name}'")
                                            st.rerun()
                                        else:
                                            st.error(f"Upload failed: {up_r.text}")
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                            else:
                                st.warning("Select a file first.")
                    else:
                        st.warning("🚫 Your designation (HC/PC) does not have upload permissions.")

                with t3:
                    st.caption(f"AI is context-aware of Case #{sid}")
                    for msg in st.session_state.case_chat_history:
                        css = "chat-officer" if msg["role"] == "officer" else "chat-ai"
                        icon = "👮" if msg["role"] == "officer" else "🤖"
                        st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
                    cq = st.text_input("Ask about this case...", key=f"cq_{sid}")
                    if st.button("Send to AI", use_container_width=True, key=f"caib_{sid}"):
                        if cq:
                            with st.spinner("Consulting AI..."):
                                try:
                                    ai_r = requests.post(f"{API_BASE_URL}/api/assistant/chat",
                                                         json={"message": cq, "fir_id": sid}, timeout=30)
                                    if ai_r.status_code == 200:
                                        at = ai_r.json().get("response","")
                                        st.session_state.case_chat_history.append({"role":"officer","content":cq})
                                        st.session_state.case_chat_history.append({"role":"ai","content":at})
                                        st.rerun()
                                    else:
                                        st.error(f"AI error: {ai_r.text}")
                                except Exception as e:
                                    st.error(f"Error: {e}")


# ─── AI Assistant & FIR Processing ────────────────────────
elif page == "🧠 AI Assistant & FIR Processing":
    render_header("AI Assistant & FIR Processing")
    t1, t2 = st.tabs(["💬 KSP Chat Assistant", "📝 FIR Document Processing"])

    with t1:
        st.subheader("Generative AI Law Enforcement Assistant")
        st.info("Ask questions about crime patterns, patrol routes, or tactical advice.")
        for msg in st.session_state.general_chat_history:
            css = "chat-officer" if msg["role"] == "officer" else "chat-ai"
            icon = "👮" if msg["role"] == "officer" else "🤖"
            st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
        uq = st.text_input("Message Assistant...", placeholder="E.g., High risk areas in Hassan?", key="gchat")
        if st.button("Send", use_container_width=True, key="gsendbtn"):
            if uq:
                with st.spinner("Consulting AI..."):
                    try:
                        r = requests.post(f"{API_BASE_URL}/api/assistant/chat", json={"message": uq}, timeout=30)
                        if r.status_code == 200:
                            at = r.json().get("response","")
                            st.session_state.general_chat_history.append({"role":"officer","content":uq})
                            st.session_state.general_chat_history.append({"role":"ai","content":at})
                            st.rerun()
                        else:
                            st.error(f"AI error: {r.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter a message first.")

    with t2:
        st.subheader("FIR Document Processing — PDF Upload")
        st.info("Upload a PDF FIR. Gemini AI extracts fields, ML predicts risk, and the record is saved to PostgreSQL.")
        ff = st.file_uploader("Upload FIR (PDF)", type=["pdf"], key="fir_upload")
        if ff:
            st.markdown(f"**Selected:** `{ff.name}` ({ff.size/1024:.1f} KB)")
        if st.button("🚀 Process FIR & Save to Database", use_container_width=True, type="primary"):
            if ff:
                with st.spinner("Extracting PDF → Gemini AI → ML Prediction → PostgreSQL..."):
                    try:
                        r = requests.post(f"{API_BASE_URL}/api/fir/predict-and-save",
                                          files={"file": (ff.name, ff.getvalue(), "application/pdf")}, timeout=60)
                        if r.status_code == 200:
                            data = r.json()
                            st.success(f"✅ Saved — Case ID: #{data.get('database_id')}")
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown("**📋 Gemini AI Extraction**")
                                st.json(data.get("extracted_data", {}))
                            with c2:
                                st.markdown("**🔮 ML Risk Prediction**")
                                pred = data.get("prediction", {})
                                st.json(pred)
                                rc2 = "#EF4444" if pred.get("risk_level_code",0)==1 else "#10B981"
                                rl = pred.get("risk_level_label","Unknown")
                                st.markdown(f"""<div style="background:{'rgba(239,68,68,.1)' if pred.get('risk_level_code',0)==1 else 'rgba(16,185,129,.1)'};
                                    border:1px solid {rc2}; padding:12px; border-radius:8px; margin-top:8px;">
                                    <strong style="color:{rc2}; font-size:16px;">
                                    {'⚠️ HIGH RISK' if pred.get('risk_level_code',0)==1 else '✅ LOW RISK'}</strong></div>""",
                                    unsafe_allow_html=True)
                        else:
                            st.error(f"Failed: {r.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Upload a PDF first.")


# ─── Admin Panel (SP only) ─────────────────────────────────
elif page == "⚙️ Admin Panel":
    render_header("Admin Panel — SP Access Only")
    if access_level < 5:
        st.error("🚫 Insufficient privileges. This module is restricted to SP (Superintendent of Police) only.")
    else:
        st.markdown("### 👮 Registered Officers Overview")
        st.info("This panel shows all officers registered in the system.")
        try:
            r = requests.get(f"{API_BASE_URL}/api/auth/officers", timeout=10)
            if r.status_code == 200:
                officers = r.json()
                if officers:
                    df_off = pd.DataFrame(officers)
                    keep = [c for c in ["police_id","full_name","designation","access_level","district","police_station","phone","created_at"] if c in df_off.columns]
                    st.dataframe(df_off[keep].rename(columns={
                        "police_id":"Police ID","full_name":"Name","designation":"Designation",
                        "access_level":"Level","district":"District","police_station":"Station",
                        "phone":"Phone","created_at":"Registered On"
                    }), use_container_width=True, hide_index=True)
                    st.metric("Total Officers", len(officers))
                else:
                    st.info("No officers registered yet.")
            else:
                st.error("Failed to load officers from backend.")
        except Exception as e:
            st.error(f"Failed to load officer registry: {e}")
            
        st.markdown("---")
        st.markdown("### 🗄️ Database Management")
        st.info("Upload a CSV file to permanently load crime incidents into the PostgreSQL database. **This will overwrite existing incidents.**")
        
        csv_file = st.file_uploader("Upload Crime Incidents (CSV)", type=["csv"], key="csv_upload_db")
        if csv_file:
            if st.button("🚀 Load Data to Database", type="primary", use_container_width=True):
                with st.spinner("Uploading and processing CSV..."):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/api/incidents/upload",
                            files={"file": (csv_file.name, csv_file.getvalue(), "text/csv")},
                            timeout=60
                        )
                        if r.status_code == 201:
                            st.success(f"✅ Data loaded successfully! {r.json().get('message')}")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {r.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")


# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:#334155; font-size:12px;'>"
    f"KSP Crime Intelligence Platform — Datathon 2026 &nbsp;|&nbsp; "
    f"Logged in as <strong style='color:#64748b;'>{full_name} ({designation})</strong> "
    f"&nbsp;|&nbsp; All data from PostgreSQL</p>",
    unsafe_allow_html=True
)
