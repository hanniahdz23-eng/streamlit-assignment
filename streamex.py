import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import streamlit.components.v1 as components

# Setting up the page configuration and title
st.set_page_config(page_title="Sellers Dashboard", layout="wide")
st.title("📊 Sellers Dashboard — Excel ➜ CSV Converter")

# -------------------------
# File uploading section
# -------------------------
uploaded_file = st.file_uploader("Upload sellers.xlsx file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Reads excel into a dataframe
    df = pd.read_excel(uploaded_file)

    # Converting Excel to a CSV
    csv_data = df.to_csv(index=False).encode('utf-8')

    # Download button for CSV
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_data,
        file_name="sellers_converted.csv",
        mime="text/csv"
    )

    # Table of data
    st.subheader("🧾 Data Preview")
    st.dataframe(df.head())

    # Filter: Region
    st.markdown("### 🌎 Filter by Region")
    region_options = df["REGION"].unique()
    selected_region = st.selectbox("Select a Region:", ["All"] + list(region_options))

    if selected_region != "All":
        filtered_df = df[df["REGION"] == selected_region]
    else:
        filtered_df = df

    st.write(f"### Showing data for: {selected_region}")
    st.dataframe(filtered_df)

# -------------------------
# Sales Metrics Visuals
# -------------------------
    st.markdown("## 📈 Sales Metrics")

    col1, col2, col3 = st.columns(3)

# Barcharts for Sales Metrics, they are ordered alphabetically by name
    with col1:
        units_chart = alt.Chart(filtered_df).mark_bar().encode(
            x="NAME",
            y="SOLD UNITS",
            color="REGION"
        ).properties(title="Units Sold by Seller")
        st.altair_chart(units_chart, use_container_width=True)

    with col2:
        total_chart = alt.Chart(filtered_df).mark_bar().encode(
            x="NAME",
            y="TOTAL SALES",
            color="REGION"
        ).properties(title="Total Sales by Seller")
        st.altair_chart(total_chart, use_container_width=True)

    with col3:
        avg_chart = alt.Chart(filtered_df).mark_bar().encode(
            x="NAME",
            y="SALES AVERAGE",
            color="REGION"
        ).properties(title="Average Sales by Seller")
        st.altair_chart(avg_chart, use_container_width=True)

    # Inidividual Seller Filter
    st.markdown("## 🔍 Seller Details")
    vendor_list = filtered_df["NAME"].unique()
    selected_vendor = st.selectbox("Select a Seller:", vendor_list)

    vendor_data = filtered_df[filtered_df["NAME"] == selected_vendor]
    st.dataframe(vendor_data)

# -------------------------------------
# Individual Sales Summary Dashboard
# -------------------------------------
st.markdown("## 💳 Individual Sales Summary")

seller_name = vendor_data["NAME"].iloc[0]
region_name = vendor_data["REGION"].iloc[0]
units_sold = int(vendor_data["SOLD UNITS"].sum())
total_sales = vendor_data["TOTAL SALES"].sum()
avg_sales = vendor_data["SALES AVERAGE"].mean()



# Average Sales Card: Average Sales Increment/Decrement by Color Logic
overall_avg = df["SALES AVERAGE"].mean()
if avg_sales >= overall_avg:
    avg_color = "#16a34a"  # green
    arrow = "↑"
else:
    avg_color = "#dc2626"  # red
    arrow = "↓"

# HTML Code for Cards
# Title card in dark blue color with seller name and region
# Units sold and total sales, divided by a line
# Average sales with color-coded increment/decrement arrow

html_code = f"""
<style>
.card-wrapper {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 1.5rem;
    font-family: 'Inter', sans-serif;
}}
.card {{
    border-radius: 16px;
    padding: 1.75rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    flex: 1 1 280px;
    text-align: center;
}}
.card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}}
.card-blue {{
    background: linear-gradient(145deg, #1e3a8a, #1d4ed8);
    color: white;
}}
.card-white {{
    background: #ffffff;
    color: #1e3a8a;
    border: 1px solid #e2e8f0;
}}
.card-avg {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: #1e293b;
}}
.divider {{
    height: 1px;
    width: 60%;
    background-color: #e2e8f0;
    margin: 0.75rem auto;
}}
h2, h3, p {{
    margin: 0.25rem 0;
}}
</style>

<div class="card-wrapper">

    <div class="card card-blue">
        <h3 style="margin-bottom:0.3rem;">{seller_name}</h3>
        <p style="opacity:0.8;">{region_name}</p>
    </div>

    <div class="card card-white">
        <p style="font-weight:600;">Units Sold</p>
        <h2>{units_sold}</h2>
        <div class="divider"></div>
        <p style="font-weight:600;">Total Sales</p>
        <h2>${total_sales:,.0f}</h2>
    </div>

    <div class="card card-avg">
        <p style="font-weight:600;">Average Sales</p>
        <h2 style="color:{avg_color}; font-weight:700;">{arrow} {avg_sales:.4f}</h2>
        <p style="opacity:0.6;">vs overall avg</p>
    </div>

</div>
"""

components.html(html_code, height=400, scrolling=False)
