import pandas as pd
import numpy as np
import seaborn as sns
import warnings
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
import streamlit as st

warnings.filterwarnings('ignore')
data = pd.read_csv('https://olympus.mygreatlearning.com/courses/96080/files/11055029/download?verifier=ECNvbt1T3Pqlektc0L4EeablXmlQ9wquu2OsZFGp&wrap=1')
data['Sales'] = data['Bottles.Sold'] * data['State.Bottle.Retail']

# --- Dashboard with Streamlit ---
st.set_page_config(
    page_title="Iowa top Alcohol products",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

st.header('Iowa Alcohol Products - Least Performing 🍾', divider='rainbow')
col = st.columns(4, gap='medium')

# Left Column: Overview Metrics
def format_large_numbers(number):
    if number >= 1_000_000_000:
        return f"{number/1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number/1_000:.1f}K"
    else:
        return str(number)
    
st.markdown(""" 
<style>
    .css-1v3fvcr {
        font-size: 30px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Overview Metrics (showing least aspects)
total_sales = data['Sales'].sum()
total_bottles = data['Bottles.Sold'].sum()
avg_sales_per_bottle = total_sales / total_bottles
least_category = data.groupby('Category.Name')['Bottles.Sold'].sum().idxmin().capitalize()

col[0].metric("Total Sales", format_large_numbers(total_sales))
col[1].metric("Total Bottles Sold", format_large_numbers(total_bottles))
col[2].metric("Average Sales/Bottle", f"${avg_sales_per_bottle:.2f}")
col[3].metric("Least Category", least_category)

# Middle Column: Least Performing Products
col = st.columns(3, gap='medium')
with col[0]:
    st.header("Least Selling Products")
    least_products = data.groupby('Category.Name')['Bottles.Sold'].sum().sort_values(ascending=True).head(15).reset_index()

    fig = px.bar(
        least_products,
        y='Category.Name',  # Use the column directly from the DataFrame
        x='Bottles.Sold',
        labels={'x': 'Bottles Sold', 'y': 'Type of Alcohol'},
        color='Bottles.Sold',
        color_continuous_scale='reds',  # Red color scale for negative performance
        log_x=True
    )

    # Reverse the y-axis to show the smallest values at the top
    fig.update_layout(
        yaxis=dict(
            autorange="reversed",  # Reverse the order of the y-axis
            tickfont=dict(size=10)  # Adjust font size for readability
        ),
        xaxis_title='', 
        yaxis_title=''
    )
    st.plotly_chart(fig)

# Right Column: Least Performing Geographic Sales
with col[1]:
    st.header("Geographic Sales Distribution - Least Performing Counties")
    county_sales = data.groupby('County')['Sales'].sum().reset_index().sort_values('Sales',ascending=True).head(10)
    fig = px.bar(
        county_sales,
        x='County',
        y='Sales',
        labels={"County": "County", "Sales": "Sales ($)"},
        color='Sales',
        color_continuous_scale='reds',  # Red color scale for low sales
    )
    fig.update_layout(xaxis_tickangle=-45)  # Rotate labels if necessary
    st.plotly_chart(fig)

# Right Column: Least Performing Stores (Tree Map)
with col[2]:
    st.header("Least Performing Stores (American Vodkas)")
    filtered_data = data[data['Category.Name'].isin(['AMERICAN VODKAS'])]
    least_stores = filtered_data.groupby('Store.Name')['Sales'].sum().sort_values(ascending=True).head(10).reset_index()

    fig = px.treemap(
        least_stores,
        path=['Store.Name'],
        values='Sales',
        labels={'Sales': 'Total Sales ($)', 'Store.Name': 'Store Name'},
        color='Sales',
        color_continuous_scale='reds',  # Red color scale for low sales in stores
    )
    st.plotly_chart(fig)

# Bottom Vendor Contribution (Pie Chart)
col = st.columns(3)
with col[0]:
    st.header("Least Vendor Contribution")
    vendor_sales = filtered_data.groupby('Vendor.Name')['Sales'].sum().reset_index().sort_values('Sales', ascending=True).head(10)
    
    # Use a different color palette for better distinction between vendors
    fig_vendor = px.pie(
        vendor_sales,
        values='Sales',
        names='Vendor.Name',
        title='Vendor Contribution to Total Sales',
        color='Vendor.Name',  # Differentiate colors based on Vendor
        color_discrete_sequence=px.colors.colorbrewer.Reds  # Use a palette with distinct colors
    )
    st.plotly_chart(fig_vendor)

# Sales Evolution (showing declining sales)
with col[1]:
    st.header('Sales Evolution')
    data['Date'] = pd.to_datetime(data['Date'])
    sales_trend = data.groupby('Date')['Sales'].sum().reset_index()
    fig = px.line(
        sales_trend,
        x='Date',
        y='Sales',
        labels={"Sales": "Sales ($)", "Date": "Date"},
        line_shape='linear',
        color_discrete_sequence=['red']  # Use red for declining trends
    )
    st.plotly_chart(fig)
