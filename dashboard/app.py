import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Ad Spend Optimizer",
    page_icon="📈",
    layout="wide"
)

# 2. Load Data (LITE VERSION)
@st.cache_data
def load_data():
    try:
        # Load the full file
        df = pd.read_csv('data/processed/cleaned_ads_data.csv')
        
        # PERFORMANCE FIX: Sample 10,000 rows immediately
        # This makes the app snappy while keeping the statistical patterns
        if len(df) > 10000:
            df = df.sample(n=10000, random_state=42)
            
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("Error: Could not find 'data/processed/cleaned_ads_data.csv'.")
    st.stop()

# 3. Sidebar Filters
st.sidebar.header("🎯 Campaign Filters")
st.sidebar.info(f"⚡ Performance Mode: Analyzing {len(df):,} random campaigns.")

# Channel Filter
all_channels = sorted(df['Channel_Used'].unique())
selected_channel = st.sidebar.multiselect(
    "Select Channels",
    options=all_channels,
    default=all_channels
)

# Goal Filter
all_goals = sorted(df['Campaign_Goal'].unique())
selected_goal = st.sidebar.multiselect(
    "Select Campaign Goal",
    options=all_goals,
    default=all_goals
)

# Apply Filters
filtered_df = df[
    (df['Channel_Used'].isin(selected_channel)) &
    (df['Campaign_Goal'].isin(selected_goal))
]

# 4. Dashboard Main
st.title("🚀 Marketing Campaign Optimization Engine")

# KPI Row
if not filtered_df.empty:
    total_spend = filtered_df['Acquisition_Cost'].sum()
    avg_roi = filtered_df['ROI'].mean()
    avg_conversion = filtered_df['Conversion_Rate'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Est. Ad Spend (Sampled)", f"${total_spend:,.0f}")
    col2.metric("📈 Average ROI", f"{avg_roi:.2f}")
    col3.metric("🎯 Avg Conversion Rate", f"{avg_conversion:.1%}")
else:
    st.warning("No data selected. Please check your filters.")

st.divider()

# 5. Charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Performance by Channel")
    if not filtered_df.empty:
        fig_channel = px.box(
            filtered_df, 
            x='Channel_Used', 
            y='ROI', 
            color='Channel_Used',
            title="ROI Distribution by Channel"
        )
        st.plotly_chart(fig_channel, use_container_width=True)

with col_right:
    st.subheader("Spend vs. Returns")
    if not filtered_df.empty:
        # No extra sampling needed here because we already sampled the whole app
        fig_scatter = px.scatter(
            filtered_df,
            x='Acquisition_Cost',
            y='ROI',
            color='Campaign_Goal',
            size='Clicks',
            title="ROI vs. Cost"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# 6. Strategy Table
st.subheader("🏆 Top Performing Strategies")
if not filtered_df.empty:
    top = filtered_df.groupby(['Channel_Used', 'Campaign_Goal'])[['ROI', 'Conversion_Rate']].mean()
    st.dataframe(top.sort_values('ROI', ascending=False), use_container_width=True)