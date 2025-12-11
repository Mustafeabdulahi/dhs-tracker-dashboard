#!/usr/bin/env python3
"""
DHS Worst of the Worst - Professional Dashboard (Visual Polish)
Matches the design from the reference mockup (Image 1)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path
from collections import Counter
import textwrap

# Page config
st.set_page_config(
    page_title="DHS WoW Dashboard",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# CSS Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* GLOBAL RESET & TYPOGRAPHY */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Background colors */
    .stApp {
        background-color: #f8fafc; /* Light gray background */
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
        background-color: #f8fafc;
    }
    
    /* Ensure consistent spacing throughout */
    .stApp > div > div > div {
        background-color: #f8fafc;
    }
    
    /* RE-ENABLE HEADER FOR SIDEBAR TOGGLE - Match sidebar color */
    header[data-testid="stHeader"] {
        background-color: #1e3a8a !important;
        background-image: linear-gradient(to right, #1e3a8a, #1e3a8a) !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    /* Keep sidebar toggle visible with white color */
    button[data-testid="baseButton-header"] {
        color: white !important;
    }
    button[data-testid="baseButton-header"] svg {
        fill: white !important;
    }
    div[data-testid="stDecoration"] {
        background-color: #1e3a8a !important;
    }
    
    /* -------------------------------------------------------------------------
       SIDEBAR STYLING
       ------------------------------------------------------------------------- */
    section[data-testid="stSidebar"] {
        background-color: #1e3a8a;
        background-image: linear-gradient(#1e3a8a, #162e6c); /* Navy gradient */
        color: white;
    }
    
    /* Sidebar text color override */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label {
        color: white;
    }

    /* Sidebar Title Card */
    .sidebar-title-card {
        background-color: white;
        border-radius: 12px;
        padding: 28px 24px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    .sidebar-title-text {
        color: #1e3a8a !important; /* Match header color */
        font-weight: 800;
        font-size: 20px;
        line-height: 1.3;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Stats Overview Card (Dark Blue Background) */
    .sidebar-stats-card {
        background-color: rgba(30, 58, 138, 0.4); /* Dark Navy Transparent */
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .sidebar-stats-header {
        font-size: 15px;
        font-weight: 600;
        color: white !important;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    
    .sidebar-big-stat {
        font-size: 42px;
        font-weight: 700;
        color: white !important;
        line-height: 1;
        margin-bottom: 4px;
    }
    
    .sidebar-stat-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        font-size: 14px;
        align-items: center;
    }
    .sidebar-stat-row:last-child {
        border-bottom: none;
    }
    
    /* Search & Filter Card (REMOVED BACKGROUND) */
    .sidebar-search-card {
        background-color: transparent;
        padding: 0px;
        margin-bottom: 24px;
        box-shadow: none;
    }
    
    .sidebar-search-header {
        font-size: 18px;
        font-weight: 700;
        color: white !important; /* Make header white */
        margin-bottom: 16px;
    }
    
    /* Search Input Styling (Top) */
    .top-search-container {
        margin-bottom: 24px;
    }
    .top-search-input {
        background-color: white;
        border-radius: 8px;
        padding: 12px 16px;
        width: 100%;
        border: none;
        color: #0f172a;
        font-size: 14px;
        display: flex;
        align-items: center;
    }
    
    /* Force inputs to be white with dark text - targeting Sidebar specifically */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] .stDateInput input,
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
        background-color: white !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    
    /* Ensure the text inside the inputs is visible (dark) */
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stDateInput input {
         color: #0f172a !important;
         background-color: white !important;
         caret-color: #0f172a; /* Cursor color */
    }

    /* Fix selectbox selected text to be visible (dark text) */
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
        color: #0f172a !important;
    }
    
    /* Fix the MultiSelect tag/chip colors - blue highlight */
    section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* Force labels to be white in sidebar */
    section[data-testid="stSidebar"] label {
        color: white !important;
        font-size: 13px;
        font-weight: 500;
    }
    
    /* -------------------------------------------------------------------------
       MAIN CONTENT STYLING
       ------------------------------------------------------------------------- */
       
    /* Header Bar - Clean and Consistent */
    .header-bar {
        background-color: white !important;
        padding: 2rem 2rem;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0 0 2rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 6px solid #1e3a8a;
    }
    
    .header-title {
        color: #1e3a8a !important;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        text-transform: uppercase;
    }
    
    .header-subtitle {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 4px;
    }
    
    /* Standard White Card */
    .white-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        height: 100%;
        margin-bottom: 16px;
        display: flex;
        flex-direction: column;
        min-height: 140px; /* Ensure uniform height for KPI cards */
        justify-content: center;
        border: 1px solid #e2e8f0;
        transition: box-shadow 0.2s ease;
    }
    
    .white-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    /* KPI Card specific */
    .kpi-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        color: #1e293b;
        font-size: 32px;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    
    .kpi-value.green {
        color: #16a34a;
        font-size: 24px; /* Slightly smaller for text */
    }
    
    .kpi-sub {
        color: #94a3b8;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Table Styling */
    .table-header {
        display: grid;
        grid-template-columns: 80px 2.5fr 1.5fr 3fr 2fr 1.5fr;
        gap: 1.5rem;
        padding: 16px 24px;
        background-color: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
        font-weight: 600;
        color: #475569;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .table-row {
        display: grid;
        grid-template-columns: 80px 2.5fr 1.5fr 3fr 2fr 1.5fr;
        gap: 1.5rem;
        padding: 16px 24px;
        border-bottom: 1px solid #f1f5f9;
        align-items: center;
        font-size: 14px;
        color: #334155;
        transition: background-color 0.1s;
    }
    
    /* Prevent text overflow in table cells */
    .table-row > div {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .table-row:hover {
        background-color: #f8fafc;
    }
    
    /* Person name link styling */
    .person-name-link {
        color: #1e3a8a !important;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
        border-bottom: 2px solid transparent;
    }
    
    .person-name-link:hover {
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb;
    }
    
    .person-name-no-link {
        color: #1e293b;
        font-weight: 500;
    }
    
    .mugshot-container {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        overflow: hidden;
        background-color: #e2e8f0;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .mugshot-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Streamlit Button Override */
    div.stButton > button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        width: 100%;
        margin-top: 16px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 14px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
    }
    div.stButton > button:hover {
        background-color: #162e6c;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(30, 58, 138, 0.3);
    }
    
    /* Reduce gap between columns */
    div[data-testid="column"] {
        padding: 0 0.5rem;
    }

</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Logic & Data
# -----------------------------------------------------------------------------


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_database():
    """Load the historical database"""
    db_path = Path("data/historical_arrests.json")
    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    return {"records": {}, "metadata": {}}


def extract_state_from_location(location):
    """Extract state abbreviation or name from location string"""
    if not location:
        return None

    state_abbrev = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
        "DC": "District of Columbia",
    }

    parts = location.split(",")
    if len(parts) >= 2:
        state = parts[-1].strip().upper()
        if state in state_abbrev:
            return state_abbrev[state]
        state_names = list(state_abbrev.values())
        for name in state_names:
            if name.upper() == state:
                return name

    location_upper = location.strip().upper()
    if location_upper in state_abbrev:
        return state_abbrev[location_upper]
    return location.strip()


def get_most_common_crime(records):
    """Determine the most common crime category"""
    crime_keywords = {
        "Drug Trafficking": [
            "drug",
            "narcotic",
            "trafficking",
            "cocaine",
            "heroin",
            "meth",
        ],
        "Sexual Assault": ["sex", "rape", "sexual", "assault", "child", "abuse"],
        "Murder": ["murder", "homicide", "manslaughter", "kill"],
        "Assault": ["assault", "battery"],
        "DUI": ["dui", "dwi", "driving", "influence"],
        "Theft": ["theft", "burglary", "robbery", "larceny"],
    }

    crime_counts = Counter()
    for record in records:
        crime_text = record.get("convicted_of", "").lower()
        found = False
        for category, keywords in crime_keywords.items():
            if any(keyword in crime_text for keyword in keywords):
                crime_counts[category] += 1
                found = True
                break
        if not found and crime_text:
            crime_counts["Other"] += 1

    if crime_counts:
        return crime_counts.most_common(1)[0][0]
    return "N/A"


def main():
    db_data = load_database()
    if not db_data["records"]:
        st.error("⚠️ No data available. Please run the scraper first.")
        return
    
    # Compact Info Navbar
    last_updated = db_data.get("metadata", {}).get("last_updated")
    if last_updated:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(last_updated)
            formatted_date = dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            formatted_date = last_updated
    else:
        formatted_date = "Unknown"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); 
                padding: 12px 24px; 
                border-radius: 8px; 
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;">
        <div style="color: white; display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
            <span style="font-weight: 600; font-size: 14px;">
                ⚠️ Data from DHS.gov | Arrest dates ±1-7 days
            </span>
            <span style="font-weight: 500; font-size: 13px; opacity: 0.9;">
                ✅ Updated: {formatted_date}
            </span>
        </div>
        <div style="display: flex; gap: 15px;">
            <a href="https://github.com/Mustafeabdulahi/dhs-tracker-dashboard/issues" 
               target="_blank" 
               style="color: white; text-decoration: none; font-size: 13px; font-weight: 500; opacity: 0.9; transition: opacity 0.2s;"
               onmouseover="this.style.opacity='1'" 
               onmouseout="this.style.opacity='0.9'">
                📧 Report Issue
            </a>
            <a href="https://github.com/Mustafeabdulahi/dhs-tracker-dashboard" 
               target="_blank" 
               style="color: white; text-decoration: none; font-size: 13px; font-weight: 500; opacity: 0.9; transition: opacity 0.2s;"
               onmouseover="this.style.opacity='1'" 
               onmouseout="this.style.opacity='0.9'">
                💻 Source Code
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_records = list(db_data["records"].values())
    active_records = [r for r in all_records if r.get("status") == "active"]

    # Pre-calculate lists for filters
    all_countries = sorted(
        list(set(r.get("country", "") for r in active_records if r.get("country")))
    )
    # Extract states and filter out None/empty before sorting
    states_set = set(
        extract_state_from_location(r.get("arrested_location", ""))
        for r in active_records
    )
    all_states = sorted([s for s in states_set if s])

    # -------------------------------------------------------------------------
    # LAYOUT
    # -------------------------------------------------------------------------

    # Header removed for single-page view

    # SIDEBAR CONTENT
    with st.sidebar:
        # A. Title Card
        st.markdown(
            """
        <div class="sidebar-title-card">
            <div class="sidebar-title-text">DHS Worst<br>of the Worst</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # D. Search & Filter Card
        st.markdown('<div class="sidebar-search-card">', unsafe_allow_html=True)

        # Date Filter (Moved Up)
        date_range = st.date_input(
            "Date Range",
            value=(datetime(2025, 12, 10), datetime.now()),
            key="s_date_range",
        )
        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="sidebar-search-header">Search & Filter</div>',
            unsafe_allow_html=True,
        )

        # Grid inputs
        f_name = st.text_input("Name", placeholder="Name", key="s_name")

        f_country = st.selectbox("Country", ["All"] + all_countries, key="s_country")

        f_state = st.selectbox("State", ["All"] + all_states, key="s_state")

        f_crimes = st.multiselect(
            "Crime Type",
            ["Drug Trafficking", "Sexual Assault", "Murder", "Assault", "Theft"],
            default=[],
            key="s_crime",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        do_search = st.button("Search")

        st.markdown("</div>", unsafe_allow_html=True)  # End search card
        
        # Disclaimer in Sidebar
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.warning("""
        **⚠️ Disclaimer**
        
        Data from DHS.gov. Arrest dates are approximated (±1-7 days). 
        
        For official information, contact ICE or consult legal counsel.
        
        Dashboard for informational purposes only.
        """)
        
        # Footer
        st.markdown("""
        ---
        <div style="text-align: center; color: #cbd5e1; font-size: 11px;">
        Built by Mustafe Abdulahi<br>
        <a href="https://github.com/Mustafeabdulahi/dhs-tracker-dashboard" target="_blank" style="color: #93c5fd;">GitHub</a>
        </div>
        """, unsafe_allow_html=True)

    # MAIN AREA

    # Filter Logic
    filtered_records = active_records.copy()

    # Date Filtering
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
        temp_date_list = []
        for r in filtered_records:
            d_str = r.get("first_seen_date")
            if d_str:
                try:
                    r_date = datetime.strptime(d_str, "%Y-%m-%d").date()
                    if start_d <= r_date <= end_d:
                        temp_date_list.append(r)
                except ValueError:
                    pass
        filtered_records = temp_date_list

    if f_name:
        filtered_records = [
            r for r in filtered_records if f_name.lower() in r.get("name", "").lower()
        ]

    if f_country != "All":
        filtered_records = [
            r for r in filtered_records if r.get("country") == f_country
        ]

    if f_state != "All":
        filtered_records = [
            r
            for r in filtered_records
            if extract_state_from_location(r.get("arrested_location")) == f_state
        ]

    # Simple crime filter (keyword based for the multiselect)
    if f_crimes:
        temp_list = []
        for r in filtered_records:
            c_text = r.get("convicted_of", "").lower()
            # Match ANY of the selected categories
            match = False
            for cat in f_crimes:
                # Re-use logic or simplify
                keywords = []
                if cat == "Drug Trafficking":
                    keywords = ["drug", "narcotic", "trafficking"]
                elif cat == "Sexual Assault":
                    keywords = ["sex", "rape", "assault", "abuse"]
                elif cat == "Murder":
                    keywords = ["murder", "homicide", "manslaughter"]
                elif cat == "Assault":
                    keywords = ["assault", "battery"]
                elif cat == "Theft":
                    keywords = ["theft", "robbery"]

                if any(k in c_text for k in keywords):
                    match = True
                    break
            if match:
                temp_list.append(r)
        filtered_records = temp_list

    # Row 1: KPI Cards
    k1, k2, k3, k4 = st.columns(4)

    # Calc Metrics
    metric_total = len(filtered_records)
    metric_countries = len(
        set(r.get("country") for r in filtered_records if r.get("country"))
    )

    # Calc Top State
    m_state_counts = Counter(
        extract_state_from_location(r.get("arrested_location"))
        for r in filtered_records
    )
    m_top_state = m_state_counts.most_common(1)[0] if m_state_counts else ("N/A", 0)

    # Calc Most Common Crime
    m_crime = get_most_common_crime(filtered_records)

    with k1:
        st.markdown(
            f"""
        <div class="white-card">
            <div class="kpi-label">Total Arrests</div>
            <div class="kpi-value">{metric_total:,}</div>
            <div class="kpi-sub" style="opacity: 0;">Spacer</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            f"""
        <div class="white-card">
            <div class="kpi-label">Countries</div>
            <div class="kpi-value">{metric_countries}</div>
            <div class="kpi-sub">
                <span style="color: #cbd5e1; font-size: 16px;">🌐</span> Global
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            f"""
        <div class="white-card">
            <div class="kpi-label">Top State</div>
            <div class="kpi-value">{m_top_state[0]}</div>
            <div class="kpi-sub"><span style="color: #1e3a8a; font-weight:600;">{m_top_state[1]:,}</span> cases</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            f"""
        <div class="white-card">
            <div class="kpi-label">Most Common Crime</div>
            <div class="kpi-value green">{m_crime}</div>
            <div class="kpi-sub" style="opacity: 0;">Spacer</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Row 2: Charts - Two columns
    c_map, c_bar = st.columns([1.5, 1])

    with c_map:
        # Prepare Map Data
        map_counts = Counter()
        for r in filtered_records:
            s = extract_state_from_location(r.get("arrested_location"))
            if s:
                map_counts[s] += 1

        df_map = pd.DataFrame([{"state": k, "count": v} for k, v in map_counts.items()])

        state_to_code = {
            "Alabama": "AL",
            "Alaska": "AK",
            "Arizona": "AZ",
            "Arkansas": "AR",
            "California": "CA",
            "Colorado": "CO",
            "Connecticut": "CT",
            "Delaware": "DE",
            "Florida": "FL",
            "Georgia": "GA",
            "Hawaii": "HI",
            "Idaho": "ID",
            "Illinois": "IL",
            "Indiana": "IN",
            "Iowa": "IA",
            "Kansas": "KS",
            "Kentucky": "KY",
            "Louisiana": "LA",
            "Maine": "ME",
            "Maryland": "MD",
            "Massachusetts": "MA",
            "Michigan": "MI",
            "Minnesota": "MN",
            "Mississippi": "MS",
            "Missouri": "MO",
            "Montana": "MT",
            "Nebraska": "NE",
            "Nevada": "NV",
            "New Hampshire": "NH",
            "New Jersey": "NJ",
            "New Mexico": "NM",
            "New York": "NY",
            "North Carolina": "NC",
            "North Dakota": "ND",
            "Ohio": "OH",
            "Oklahoma": "OK",
            "Oregon": "OR",
            "Pennsylvania": "PA",
            "Rhode Island": "RI",
            "South Carolina": "SC",
            "South Dakota": "SD",
            "Tennessee": "TN",
            "Texas": "TX",
            "Utah": "UT",
            "Vermont": "VT",
            "Virginia": "VA",
            "Washington": "WA",
            "West Virginia": "WV",
            "Wisconsin": "WI",
            "Wyoming": "WY",
            "District of Columbia": "DC",
        }

        if not df_map.empty:
            df_map["code"] = df_map["state"].apply(
                lambda x: state_to_code.get(x, x[:2].upper())
            )

            fig_map = go.Figure(
                data=go.Choropleth(
                    locations=df_map["code"],
                    z=df_map["count"],
                    locationmode="USA-states",
                    colorscale=[[0, "#e0f2fe"], [1, "#1e40af"]],  # Light blue to Navy
                    marker_line_color="white",
                    marker_line_width=1.5,
                    showscale=False,  # Hide colorbar to match clean look
                )
            )
            fig_map.update_layout(
                geo=dict(
                    scope="usa",
                    projection=go.layout.geo.Projection(type="albers usa"),
                    bgcolor="rgba(0,0,0,0)",
                    showlakes=False,
                    landcolor="#f1f5f9",
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="white",  # Set chart background to white
                plot_bgcolor="white",  # Set plot background to white
                height=300,
            )
        else:
            fig_map = go.Figure()

        # REMOVED chart-card-wrapper as requested
        st.markdown(
            '<div class="kpi-label" style="font-size:16px; color:#1e293b; margin-bottom: 24px;">Arrests by State</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fig_map, use_container_width=True, config={"displayModeBar": False}
        )

    with c_bar:
        # Prepare Bar Data
        bar_counts = Counter(
            r.get("country") for r in filtered_records if r.get("country")
        )
        top_countries = bar_counts.most_common(10)
        df_bar = pd.DataFrame(top_countries, columns=["Country", "Count"]).sort_values(
            "Count", ascending=True
        )

        fig_bar = go.Figure(
            go.Bar(
                x=df_bar["Count"],
                y=df_bar["Country"],
                orientation="h",
                marker_color="#10b981",  # Green
                text=df_bar["Count"],
                textposition="outside",
            )
        )

        fig_bar.update_layout(
            margin=dict(l=0, r=40, t=0, b=0),  # Right margin for outside text
            paper_bgcolor="white",  # Set chart background to white
            plot_bgcolor="white",  # Set plot background to white
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(
                    family="Inter, sans-serif", size=13, color="#334155"
                ),  # Fix text visibility
            ),
            font=dict(family="Inter, sans-serif", color="#334155"),
            height=300,
            uniformtext_minsize=10,
            uniformtext_mode="hide",
        )

        # REMOVED chart-card-wrapper as requested
        st.markdown(
            '<div class="kpi-label" style="font-size:16px; color:#1e293b; margin-bottom: 24px;">Top 10 Countries</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fig_bar, use_container_width=True, config={"displayModeBar": False}
        )

    # Row 3: Data Table
    st.markdown(
        '<div class="white-card" style="padding: 0; overflow: hidden; min-height: auto;">',
        unsafe_allow_html=True,
    )

    # Pagination Logic
    ITEMS_PER_PAGE = 5
    if "page" not in st.session_state:
        st.session_state.page = 1

    total_pages = max(1, (len(filtered_records) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

    # Ensure page is valid
    if st.session_state.page > total_pages:
        st.session_state.page = total_pages
    if st.session_state.page < 1:
        st.session_state.page = 1

    start_idx = (st.session_state.page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_data = filtered_records[start_idx:end_idx]

    # Render Table Header
    st.markdown(
        """
    <div class="table-header">
        <div>Photo</div>
        <div>Name</div>
        <div>Country</div>
        <div>Crime</div>
        <div>Location</div>
        <div>Date Seen</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Render Rows
    for row in page_data:
        # Format Date
        date_str = row.get("first_seen_date", "")
        try:
            d_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_fmt = d_obj.strftime("%b %d, %Y")
        except:
            date_fmt = date_str

        # Truncate Crime
        crime = row.get("convicted_of", "")
        if len(crime) > 30:
            crime = crime[:30] + "..."

        mugshot_html = f"""
        <div class="mugshot-container">
            <img src="{row.get("image_url", "")}" class="mugshot-img" onerror="this.style.display='none'">
        </div>
        """

        # Create clickable name with press release link
        press_url = row.get("press_release_url", "")
        if press_url:
            name_html = f'<a href="{press_url}" target="_blank" rel="noopener noreferrer" class="person-name-link">{row.get("name", "")}</a>'
        else:
            name_html = f'<span class="person-name-no-link">{row.get("name", "")} <span style="font-size: 11px; color: #94a3b8;">(No details)</span></span>'

        st.markdown(
            f"""
        <div class="table-row">
            <div>{mugshot_html}</div>
            <div style="font-weight: 500;">{name_html}</div>
            <div>{row.get("country", "").title()}</div>
            <div title="{row.get("convicted_of", "")}">{crime}</div>
            <div title="{row.get("arrested_location", "")}">{row.get("arrested_location", "")}</div>
            <div>{date_fmt}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Pagination Footer
    st.markdown(
        """<div style="padding: 16px; background-color: white;">""",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Previous", disabled=st.session_state.page == 1):
            st.session_state.page -= 1
            st.rerun()
    with col2:
        st.markdown(
            f"<div style='text-align:center; padding-top: 14px; color: #64748b; font-weight: 500;'>Page {st.session_state.page} of {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with col3:
        if st.button("Next", disabled=st.session_state.page == total_pages):
            st.session_state.page += 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # End table card


if __name__ == "__main__":
    main()
