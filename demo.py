import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="User Geographic Distribution",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stSelectbox {
        background-color: #262730;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Global User Distribution")

# Create sample data (replace this with your actual data)
@st.cache_data
def load_data():
    data = {
        'Country': ['United States', 'China', 'India', 'Germany', 'Brazil'],
        'Users': [150000, 120000, 90000, 60000, 45000],
        'Active_Users': [100000, 80000, 60000, 40000, 30000],
        'Year': [2023] * 5
    }
    return pd.DataFrame(data)

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Year selector
selected_year = st.sidebar.slider(
    "Select Year",
    min_value=2020,
    max_value=datetime.now().year,
    value=2023
)

# Metrics selection
metrics = st.sidebar.multiselect(
    "Select Metrics",
    ["Total Users", "Active Users"],
    default=["Total Users"]
)

# Main layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    # Create choropleth map
    fig = px.choropleth(
        df,
        locations='Country',
        locationmode='country names',
        color='Users',
        hover_name='Country',
        color_continuous_scale='Reds',
        title='Geographic Distribution of Users'
    )
    
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)'
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Data table
    st.subheader("Top Countries by Users")
    
    # Format data for display
    display_df = df.copy()
    display_df['Users'] = display_df['Users'].apply(lambda x: f"{x:,}")
    display_df['Active_Users'] = display_df['Active_Users'].apply(lambda x: f"{x:,}")
    
    st.dataframe(
        display_df[['Country', 'Users', 'Active_Users']],
        use_container_width=True,
        hide_index=True
    )

    # Key metrics
    st.subheader("Key Metrics")
    total_users = df['Users'].sum()
    active_users = df['Active_Users'].sum()
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        st.metric("Total Users", f"{total_users:,}")
    with col2_2:
        st.metric("Active Users", f"{active_users:,}")

# Add download button for data
st.download_button(
    label="Download Data",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name=f'user_distribution_{selected_year}.csv',
    mime='text/csv'
)