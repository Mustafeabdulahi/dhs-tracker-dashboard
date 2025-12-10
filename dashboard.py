#!/usr/bin/env python3
"""
DHS Worst of the Worst - Interactive Dashboard
Beautiful, modern interface for searching and analyzing arrest data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO

# Page config
st.set_page_config(
    page_title="DHS Worst of the Worst Tracker",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #1e3a8a;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .person-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_database():
    """Load the historical database"""
    db_path = Path('data/historical_arrests.json')
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    return {'records': {}, 'metadata': {}}


def load_image(url, placeholder=True):
    """Load image from URL with caching"""
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        if placeholder:
            # Return a placeholder
            return None
        return None


def create_metrics_row(db_data):
    """Create KPI metrics row"""
    records = db_data['records']
    metadata = db_data['metadata']
    
    active_count = sum(1 for r in records.values() if r.get('status') == 'active')
    
    # Count countries
    countries = set(r.get('country') for r in records.values() if r.get('status') == 'active')
    
    # Count states
    states = set()
    for r in records.values():
        if r.get('status') == 'active' and r.get('arrested_location'):
            location = r.get('arrested_location', '')
            if ',' in location:
                state = location.split(',')[-1].strip()
                states.add(state)
    
    # Recent additions (last 7 days)
    today = datetime.now()
    week_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    recent = sum(1 for r in records.values() if r.get('first_seen_date', '9999') >= week_ago)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Active Records", f"{active_count:,}", help="Currently listed on DHS website")
    
    with col2:
        st.metric("Countries Represented", len(countries), help="Unique countries of origin")
    
    with col3:
        st.metric("US States Affected", len(states), help="States where arrests occurred")
    
    with col4:
        st.metric("New This Week", recent, help="Added to database in last 7 days")


def search_page():
    """Main search page"""
    st.markdown('<div class="main-header">🚨 DHS Worst of the Worst Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Track and search criminal alien arrest records</div>', unsafe_allow_html=True)
    
    # Load data
    db_data = load_database()
    
    if not db_data['records']:
        st.warning("⚠️ No data available. Please run the scraper first: `python dhs_tracker.py`")
        return
    
    # Metrics
    create_metrics_row(db_data)
    
    st.markdown("---")
    
    # Search and filters
    st.subheader("🔍 Search for a Person")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "Enter name to search",
            placeholder="e.g., Rodriguez, Garcia, Mohamed",
            help="Search by person's name"
        )
    
    with col2:
        search_type = st.selectbox(
            "Search by",
            ["Name", "Date Range"],
            help="Choose search method"
        )
    
    # Date range filters
    if search_type == "Date Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "From date",
                value=datetime.now() - timedelta(days=30),
                help="When they might have been arrested"
            )
        with col2:
            end_date = st.date_input(
                "To date",
                value=datetime.now(),
                help="When they might have been arrested"
            )
    
    # Additional filters
    with st.expander("🔽 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            countries = sorted(set(r.get('country', 'Unknown') for r in db_data['records'].values() if r.get('status') == 'active'))
            selected_countries = st.multiselect("Country", countries)
        
        with col2:
            states = set()
            for r in db_data['records'].values():
                if r.get('status') == 'active' and r.get('arrested_location'):
                    location = r.get('arrested_location', '')
                    if ',' in location:
                        state = location.split(',')[-1].strip()
                        states.add(state)
            selected_states = st.multiselect("State", sorted(states))
        
        with col3:
            status_filter = st.selectbox("Status", ["Active", "All", "Removed"])
    
    # Search button
    if st.button("🔍 Search", type="primary"):
        results = []
        
        # Filter records
        for record in db_data['records'].values():
            # Status filter
            if status_filter == "Active" and record.get('status') != 'active':
                continue
            if status_filter == "Removed" and record.get('status') != 'removed':
                continue
            
            # Name search
            if search_type == "Name" and search_query:
                if search_query.lower() not in record.get('name', '').lower():
                    continue
            
            # Date range search
            if search_type == "Date Range":
                first_seen = record.get('first_seen_date', '')
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
                if not (start_str <= first_seen <= end_str):
                    continue
            
            # Country filter
            if selected_countries and record.get('country') not in selected_countries:
                continue
            
            # State filter
            if selected_states:
                location = record.get('arrested_location', '')
                if ',' in location:
                    state = location.split(',')[-1].strip()
                    if state not in selected_states:
                        continue
                else:
                    continue
            
            results.append(record)
        
        # Display results
        st.markdown("---")
        st.subheader(f"📋 Results: {len(results)} records found")
        
        if results:
            # Sort by date
            results.sort(key=lambda x: x.get('first_seen_date', ''), reverse=True)
            
            # Display as cards
            for record in results[:50]:  # Limit to 50 results
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        # Try to load image
                        img_url = record.get('image_url')
                        if img_url:
                            try:
                                st.image(img_url, width=150)
                            except:
                                st.image("https://via.placeholder.com/150", width=150)
                        else:
                            st.image("https://via.placeholder.com/150", width=150)
                    
                    with col2:
                        st.markdown(f"### {record.get('name', 'Unknown')}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.markdown(f"**Country:** {record.get('country', 'N/A')}")
                        with col_b:
                            st.markdown(f"**Location:** {record.get('arrested_location', 'N/A')}")
                        with col_c:
                            status = record.get('status', 'unknown')
                            status_emoji = "🟢" if status == 'active' else "🔴"
                            st.markdown(f"**Status:** {status_emoji} {status.title()}")
                        
                        st.markdown(f"**Charges:** {record.get('convicted_of', 'N/A')}")
                        
                        col_d, col_e = st.columns(2)
                        with col_d:
                            st.caption(f"📅 First seen: {record.get('first_seen_date', 'Unknown')}")
                        with col_e:
                            st.caption(f"🔄 Last seen: {record.get('last_seen_date', 'Unknown')}")
                    
                    st.markdown("---")
            
            if len(results) > 50:
                st.info(f"ℹ️ Showing first 50 of {len(results)} results. Refine your search for better results.")
        else:
            st.warning("No results found. Try adjusting your search criteria.")


def analytics_page():
    """Analytics and visualizations page"""
    st.markdown('<div class="main-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    db_data = load_database()
    
    if not db_data['records']:
        st.warning("⚠️ No data available.")
        return
    
    # Filter active records
    active_records = [r for r in db_data['records'].values() if r.get('status') == 'active']
    
    # Country distribution
    st.subheader("🌍 Arrests by Country")
    country_counts = {}
    for r in active_records:
        country = r.get('country', 'Unknown')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    country_df = pd.DataFrame(list(country_counts.items()), columns=['Country', 'Count'])
    country_df = country_df.sort_values('Count', ascending=False).head(15)
    
    fig = px.bar(country_df, x='Country', y='Count', 
                 title='Top 15 Countries', 
                 color='Count',
                 color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # State distribution
        st.subheader("📍 Arrests by State")
        state_counts = {}
        for r in active_records:
            location = r.get('arrested_location', '')
            if ',' in location:
                state = location.split(',')[-1].strip()
                state_counts[state] = state_counts.get(state, 0) + 1
        
        state_df = pd.DataFrame(list(state_counts.items()), columns=['State', 'Count'])
        state_df = state_df.sort_values('Count', ascending=False).head(10)
        
        fig = px.bar(state_df, x='State', y='Count',
                     title='Top 10 States',
                     color='Count',
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Timeline of additions
        st.subheader("📈 Additions Over Time")
        date_counts = {}
        for r in active_records:
            date = r.get('first_seen_date', 'Unknown')
            if date != 'Unknown':
                date_counts[date] = date_counts.get(date, 0) + 1
        
        if date_counts:
            date_df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Count'])
            date_df = date_df.sort_values('Date')
            
            fig = px.line(date_df, x='Date', y='Count',
                         title='New Additions Per Day',
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    # Crime types (simplified)
    st.subheader("⚖️ Common Crime Categories")
    crime_categories = {
        'Assault': 0,
        'Sexual Crimes': 0,
        'Drug Related': 0,
        'Theft/Burglary': 0,
        'DUI': 0,
        'Other': 0
    }
    
    for r in active_records:
        crime = r.get('convicted_of', '').lower()
        if 'assault' in crime:
            crime_categories['Assault'] += 1
        elif 'sex' in crime or 'rape' in crime or 'child' in crime:
            crime_categories['Sexual Crimes'] += 1
        elif 'drug' in crime or 'narcotic' in crime:
            crime_categories['Drug Related'] += 1
        elif 'theft' in crime or 'burglary' in crime or 'robbery' in crime:
            crime_categories['Theft/Burglary'] += 1
        elif 'dui' in crime or 'driving' in crime:
            crime_categories['DUI'] += 1
        else:
            crime_categories['Other'] += 1
    
    crime_df = pd.DataFrame(list(crime_categories.items()), columns=['Category', 'Count'])
    fig = px.pie(crime_df, names='Category', values='Count',
                 title='Crime Distribution',
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)


def about_page():
    """About page with instructions"""
    st.markdown('<div class="main-header">ℹ️ About This Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## What is this?
    
    This dashboard tracks criminal aliens arrested by U.S. Immigration and Customs Enforcement (ICE) 
    and listed on the DHS "Worst of the Worst" database.
    
    ## How it works
    
    1. **Automated Scraping**: The system scrapes https://www.dhs.gov/wow daily
    2. **Historical Tracking**: Tracks when each person first appears on the database
    3. **Date Approximation**: Since DHS doesn't provide arrest dates, we track when they were added
    4. **Search Capability**: Search by name, date range, country, and more
    
    ## Finding Someone
    
    If you're looking for someone who was recently detained:
    
    1. Go to the **Search** page
    2. Select "Date Range" search
    3. Choose the approximate dates (±7 days around expected arrest)
    4. Add name if known
    5. Filter by location if helpful
    
    **Important**: The "first seen date" is when we first saw them on the website, 
    which is typically 1-7 days after their actual arrest.
    
    ## Running the Scraper
    
    To update data:
    ```bash
    python dhs_tracker.py --max-pages 50
    ```
    
    For daily automation:
    ```bash
    # Add to crontab (Linux/Mac)
    0 2 * * * cd /path/to/app && python dhs_tracker.py --max-pages 50
    ```
    
    ## Data Fields
    
    - **Name**: Person's full name
    - **Country**: Country of origin
    - **Convicted Of**: Charges/crimes
    - **Location**: Where arrested (City, State)
    - **First Seen**: When first appeared in database
    - **Last Seen**: Last time seen in database
    - **Status**: Active (still listed) or Removed
    
    ## Privacy & Ethics
    
    This is **public information** published by the U.S. Department of Homeland Security.
    All data is sourced directly from official government websites.
    
    ## Support
    
    For issues or questions, please check the documentation or run:
    ```bash
    python dhs_tracker.py --help
    ```
    """)


def main():
    """Main app"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.dhs.gov/profiles/dhsd8_gov/themes/custom/dhs_uswds_subtheme/images/dhs_logo.svg", width=150)
        
        st.markdown("## Navigation")
        page = st.radio("Go to", ["🔍 Search", "📊 Analytics", "ℹ️ About"])
        
        st.markdown("---")
        
        # Database info
        db_data = load_database()
        if db_data.get('metadata'):
            st.markdown("### 📁 Database Info")
            metadata = db_data['metadata']
            st.caption(f"Last updated: {metadata.get('last_updated', 'Never')[:10]}")
            st.caption(f"Total records: {metadata.get('total_records', 0):,}")
            st.caption(f"Active: {metadata.get('active_records', 0):,}")
            st.caption(f"Total scrapes: {metadata.get('total_scrapes', 0)}")
        
        st.markdown("---")
        st.caption("Data source: DHS.gov")
        st.caption("Updated daily")
    
    # Route to pages
    if page == "🔍 Search":
        search_page()
    elif page == "📊 Analytics":
        analytics_page()
    else:
        about_page()


if __name__ == "__main__":
    main()
