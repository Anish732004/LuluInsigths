
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LuLu UAE Sales Insights Dashboard", layout="wide")

@st.cache_data
def load_data():
    import os
    # Dynamically locate the CSV even if path changes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "lulu_uae_master_2000.csv")
    df = pd.read_csv(data_path)
    return df
    
df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")
if 'city' in df.columns:
    city_filter = st.sidebar.multiselect("Select City", df['city'].unique(), default=df['city'].unique())
    df = df[df['city'].isin(city_filter)]

if 'channel' in df.columns:
    channel_filter = st.sidebar.multiselect("Select Channel", df['channel'].unique(), default=df['channel'].unique())
    df = df[df['channel'].isin(channel_filter)]

if 'order_month' in df.columns:
    month_filter = st.sidebar.multiselect("Select Month", df['order_month'].unique(), default=df['order_month'].unique())
    df = df[df['order_month'].isin(month_filter)]

# Define safe groupby helper
def safe_groupby(data, col):
    if col in data.columns:
        return data.groupby(col, as_index=False).size().rename(columns={'size': 'count'})
    else:
        return pd.DataFrame()

# Page Navigation
page = st.sidebar.radio("Navigate to", ["Channel & City Breakdown", "Customer Insights", "Marketing Performance", "Operational Metrics"])

# --- Channel & City Breakdown ---
if page == "Channel & City Breakdown":
    st.title("📊 Channel & City Breakdown")
    if {'channel', 'city', 'line_value_aed'}.issubset(df.columns):
        sales_summary = df.groupby(['channel', 'city'], as_index=False)['line_value_aed'].sum()
        fig = px.bar(sales_summary, x='city', y='line_value_aed', color='channel', title="Sales by City & Channel")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Required columns not found in dataset.")

# --- Customer Insights ---
elif page == "Customer Insights":
    st.title("🧍 Customer Insights")
    col1, col2 = st.columns(2)

    with col1:
        if {'gender', 'line_value_aed'}.issubset(df.columns):
            gender_sales = df.groupby('gender', as_index=False)['line_value_aed'].sum()
            st.plotly_chart(px.pie(gender_sales, values='line_value_aed', names='gender', title="Sales by Gender"), use_container_width=True)

    with col2:
        if {'age', 'line_value_aed'}.issubset(df.columns):
            age_bins = [0, 20, 30, 40, 50, 60, 100]
            df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=['<20', '20-29', '30-39', '40-49', '50-59', '60+'])
            age_sales = df.groupby('age_group', as_index=False)['line_value_aed'].sum()
            st.plotly_chart(px.bar(age_sales, x='age_group', y='line_value_aed', title="Spending by Age Group"), use_container_width=True)

    if {'category', 'line_value_aed'}.issubset(df.columns):
        top_categories = df.groupby('category', as_index=False)['line_value_aed'].sum().sort_values(by='line_value_aed', ascending=False).head(10)
        st.plotly_chart(px.bar(top_categories, x='category', y='line_value_aed', title="Top 10 Categories by Sales"), use_container_width=True)

# --- Marketing Performance ---
elif page == "Marketing Performance":
    st.title("📣 Marketing Performance")

    if {'ad_channel', 'line_value_aed'}.issubset(df.columns):
        ad_perf = df.groupby('ad_channel', as_index=False)['line_value_aed'].sum()
        st.plotly_chart(px.bar(ad_perf, x='ad_channel', y='line_value_aed', title="Sales by Ad Channel"), use_container_width=True)

    if {'promo_code_type', 'promo_used', 'line_value_aed'}.issubset(df.columns):
        promo_perf = df[df['promo_used'] == True].groupby('promo_code_type', as_index=False)['line_value_aed'].sum()
        st.plotly_chart(px.pie(promo_perf, values='line_value_aed', names='promo_code_type', title="Promo Type ROI"), use_container_width=True)

# --- Operational Metrics ---
elif page == "Operational Metrics":
    st.title("⚙️ Operational Metrics")
    col1, col2 = st.columns(2)

    with col1:
        if 'returned' in df.columns:
            returns_data = safe_groupby(df, 'returned')
            st.plotly_chart(px.bar(returns_data, x='returned', y='count', title="Return Status"), use_container_width=True)

        if 'stock_out_flag' in df.columns:
            stock_data = safe_groupby(df, 'stock_out_flag')
            st.plotly_chart(px.bar(stock_data, x='stock_out_flag', y='count', title="Stock-Outs"), use_container_width=True)

    with col2:
        if 'delivery_type' in df.columns:
            del_data = safe_groupby(df, 'delivery_type')
            st.plotly_chart(px.bar(del_data, x='delivery_type', y='count', title="Delivery Types"), use_container_width=True)

        if 'payment_method' in df.columns:
            pay_data = safe_groupby(df, 'payment_method')
            st.plotly_chart(px.bar(pay_data, x='payment_method', y='count', title="Payment Methods"), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("LuLu Hypermarket UAE – Sales Dashboard v2.0")
