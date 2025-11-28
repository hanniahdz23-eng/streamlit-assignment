# COVID Dashboard: Mexico & Latin America
import streamlit as st
import pandas as pd
import os
import pycountry
import warnings
import plotly.express as px
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

st.set_page_config(page_title="COVID Dashboard", layout="wide", initial_sidebar_state="auto")

def to_iso3(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

base_path = r"/Users/hanniahdz58/Desktop/Streamlit/data/"
vax_path = os.path.join(base_path, "WHO_COVID_daily_data.csv")
pol2024_path = os.path.join(base_path, "COV_VAC_POLICY_2024.csv")
uptake2024_path = os.path.join(base_path, "COV_VAC_UPTAKE_2024.csv")
uptake2123_path = os.path.join(base_path, "COV_VAC_UPTAKE_2021_2023.csv")

@st.cache_data
def load_data():
    return (pd.read_csv(vax_path),
            pd.read_csv(pol2024_path),
            pd.read_csv(uptake2024_path),
            pd.read_csv(uptake2123_path))

vaxdf, policy24, uptake24, uptake2123 = load_data()

# Convert date columns
vaxdf['DATE'] = pd.to_datetime(vaxdf['Date_reported'], errors='coerce')
policy24['DATE'] = pd.to_datetime(policy24['DATE'], errors='coerce')
uptake24['DATE'] = pd.to_datetime(uptake24['DATE'], errors='coerce')
uptake2123['DATE'] = pd.to_datetime(uptake2123['DATE'], errors='coerce')

# Sidebar filters
st.sidebar.image("whoicon.png", width=150)
st.sidebar.markdown("## World Health Organization Dashboard")
st.sidebar.text("Data is from the official WHO website. Some data may be unavailable for filtered years.")
st.sidebar.subheader("Filter Options")

country_list = sorted(vaxdf["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect("Select Countries", country_list, default=["Mexico", "Brazil"])

years = sorted(vaxdf["DATE"].dt.year.unique())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=int(vaxdf['DATE'].dt.year.min()),
    max_value=int(vaxdf['DATE'].dt.year.max()),
    value=(int(vaxdf['DATE'].dt.year.min()), int(vaxdf['DATE'].dt.year.max()))
)

filtered_vax = vaxdf[
    (vaxdf["Country"].isin(selected_countries)) &
    (vaxdf["DATE"].dt.year.between(selected_years[0], selected_years[1]))
]

# Page header
st.markdown("<h1 style='font-size:42px;'>🏥 Mexico's COVID-19 Vaccination Strategy: A Comparative Analysis with Latin America</h1>", unsafe_allow_html=True)
st.write("""The COVID19 Dashboard provides a comparative analysis of Mexico against key Latin American peers, using official WHO data. The prime objective is to highlight the impact of different national strategies on reported outcomes in response to vaccine and policy rollout.
         \n """)
st.divider()

# KPI Cards
st.markdown("""
<style>
.kpi-card {padding:20px 25px; border-radius:12px; box-shadow:0 2px 4px rgba(0,0,0,0.05);}
.kpi-title {font-size:16px; font-weight:700; padding-bottom:4px; margin-bottom:5px;}
.kpi-value {font-size:26px; font-weight:400; text-align:right; margin-top:8px;}
.mexico-card {background-color:#28b6ed; color:white;}
.country-card {background-color:white; color:#28b6ed;}
.country-card .kpi-title {border-bottom:1px solid #28b6ed;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:left; font-size:30px;'>Country Health Performance Indicators</h2>", unsafe_allow_html=True)

# Mexico KPIs
if "Mexico" in selected_countries:
    vax_mex = filtered_vax[filtered_vax["Country"] == "Mexico"]
    cols = st.columns(4)
    mex_kpis = {
        "Country": "Mexico",
        "Total Cases": vax_mex['New_cases'].sum(),
        "Total Deaths": vax_mex['New_deaths'].sum(),
        "Case Fatality Rate": round(vax_mex['New_deaths'].sum()/vax_mex['New_cases'].sum()*100,2) if vax_mex['New_cases'].sum()>0 else 0
    }
    for i, (title, value) in enumerate(mex_kpis.items()):
        with cols[i]:
            st.markdown(f"<div class='kpi-card mexico-card'><div class='kpi-title'>{title}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

# Filtered countries KPIs
for country in [c for c in selected_countries if c != "Mexico"]:
    country_df = filtered_vax[filtered_vax["Country"] == country]
    cols = st.columns(4)
    country_kpis = {
        "Country": country,
        "Total Cases": country_df['New_cases'].sum(),
        "Total Deaths": country_df['New_deaths'].sum(),
        "Case Fatality Rate": round(country_df['New_deaths'].sum()/country_df['New_cases'].sum()*100,2) if country_df['New_cases'].sum()>0 else 0
    }
    for i, (title, value) in enumerate(country_kpis.items()):
        with cols[i]:
            st.markdown(f"<div class='kpi-card country-card'><div class='kpi-title'>{title}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)

# Daily COVID-19 Cases
st.markdown("### Daily COVID-19 Cases", unsafe_allow_html=True)
if not filtered_vax.empty:
    plot_df = filtered_vax.copy()
    palette = pc.qualitative.Set2
    countries = plot_df["Country"].unique()
    color_map = {c: "#28b6ed" if c=="Mexico" else palette[i % len(palette)] for i,c in enumerate(countries)}
    fig = px.line(plot_df.sort_values("DATE"), x="DATE", y="New_cases", color="Country", labels={"New_cases":"Daily New Cases"})
    fig.for_each_trace(lambda t: t.update(line_color=color_map[t.name], line_width=2))

    # Updated annotations

    # Omicron spike (max in Feb 2022)
    feb_mask = (plot_df["DATE"] >= "2022-02-01") & (plot_df["DATE"] <= "2022-02-28")
    if feb_mask.any():
        feb_df = plot_df[feb_mask]
        omicron_point = feb_df.loc[feb_df["New_cases"].idxmax()]
        omicron_x = omicron_point["DATE"]
        omicron_y = omicron_point["New_cases"]
    else:
        omicron_x = "2022-02-01"
        omicron_y = plot_df["New_cases"].max() * 0.8

    # Endemic transition (around 2023)
    end_date = plot_df["DATE"].max()
    endemic_y = plot_df["New_cases"].max() * 0.6

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        margin=dict(t=20,b=40,l=40,r=20),
        annotations=[
            dict(
                x=omicron_x,
                y=omicron_y,
                text="Omicron Wave Peak (Feb 2022)",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                bgcolor="rgba(255,255,255,0.75)",
                bordercolor="black",
                borderwidth=1
            ),
            dict(
                x=end_date,
                y=endemic_y,
                text="Shift to Endemic Phase (~2023)",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                bgcolor="rgba(255,255,255,0.75)",
                bordercolor="black",
                borderwidth=1
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for plotting daily cases.")

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

# Storytelling Section
st.subheader("COVID-19 Vaccination & Cases Overview")
filtered_non_mex = [c for c in selected_countries if c!="Mexico"]
if not filtered_non_mex:
    st.info("Select at least one comparison country other than Mexico.")
else:
    comp_country = filtered_non_mex[0]
    country_df = filtered_vax[filtered_vax["Country"]==comp_country]
    mexico_df = filtered_vax[filtered_vax["Country"]=="Mexico"]

    country_total_cases = int(country_df["New_cases"].sum())
    country_total_vacc = int(uptake24[(uptake24["COUNTRY"]==to_iso3(comp_country)) & (uptake24["DATE"].dt.year.between(selected_years[0], selected_years[1]))]["COVID_VACCINE_ADM_1D"].sum())
    mexico_total_cases = int(mexico_df["New_cases"].sum())
    mexico_total_vacc = int(uptake24[(uptake24["COUNTRY"]==to_iso3("Mexico")) & (uptake24["DATE"].dt.year.between(selected_years[0], selected_years[1]))]["COVID_VACCINE_ADM_1D"].sum())

    left_col, divider_col, right_col = st.columns([1,0.02,1])
    section_style = "background-color:#f8f9fa; padding:20px; border-radius:12px;"
    text_style = "font-size:18px; line-height:1.6;"
    country_text_style = "font-size:24px; line-height:1.6;"

    with left_col:
        st.markdown(f"<div style='{section_style}'><p style='{text_style}'>In the year(s) spanning from {selected_years[0]} - {selected_years[1]}</p><p style='{country_text_style}'>Mexico</p><p style='{text_style}'>Administered <span style='color:#28b6ed'>{mexico_total_vacc:,}</span> vaccine doses</p>", unsafe_allow_html=True)

    with right_col:
        st.markdown(f"<div style='{section_style}'><p style='{text_style}'>In the year(s) spanning from {selected_years[0]} - {selected_years[1]}</p><p style='{country_text_style}'>{comp_country}</p><p style='{text_style}'>Administered <span style='color:#2ca02c'>{country_total_vacc:,}</span> vaccine doses</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)

# Vaccine Rollout & Policy Timeline
st.markdown("<h3 style='text-align:left; margin-bottom:15px;'>Vaccine Rollout & Policy Timeline</h3>", unsafe_allow_html=True)

uptake_all = pd.concat([uptake2123, uptake24])
uptake_filtered = uptake_all[(uptake_all['COUNTRY'].isin([to_iso3(c) for c in selected_countries])) & (uptake_all['DATE'].dt.year.between(selected_years[0], selected_years[1]))]
uptake_agg = uptake_filtered.groupby(['COUNTRY','DATE']).agg({'COVID_VACCINE_ADM_1D':'sum'}).reset_index()

policy_filtered = policy24[(policy24['COUNTRY'].isin([to_iso3(c) for c in selected_countries])) & (policy24['DATE'].dt.year.between(selected_years[0], selected_years[1]))].copy()
policy_filtered['Country_name'] = policy_filtered['COUNTRY'].map({to_iso3(c): c for c in selected_countries})

colors = {"Mexico":"#28b6ed", selected_countries[1]:"#2ca02c"}

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7,0.2], vertical_spacing=0.05, subplot_titles=("Daily Vaccine Doses Administered","Policy Rollout Timeline"))

for c in selected_countries:
    c_iso = to_iso3(c)
    dfc = uptake_agg[uptake_agg['COUNTRY']==c_iso].sort_values('DATE')
    fig.add_trace(go.Scatter(x=dfc['DATE'], y=dfc['COVID_VACCINE_ADM_1D'], mode='lines+markers', name=f"{c} Vaccinations", line=dict(color=colors[c], width=3), marker=dict(size=5)), row=1, col=1)

timeline_y = 0.5
fig.add_trace(go.Scatter(x=[uptake_filtered['DATE'].min(), uptake_filtered['DATE'].max()], y=[timeline_y,timeline_y], mode='lines', line=dict(color='lightgrey', width=2), showlegend=False), row=2, col=1)

offsets = {"Mexico": timeline_y+0.05, selected_countries[1]: timeline_y-0.05}
for c in selected_countries:
    dfp = policy_filtered[policy_filtered['Country_name']==c]
    if not dfp.empty:
        fig.add_trace(go.Scatter(x=dfp['DATE'], y=[offsets[c]]*len(dfp), mode='markers', marker=dict(symbol='circle', size=12, color=colors[c]), name=f"{c} Policy", hoverinfo='skip'), row=2, col=1)

fig.update_yaxes(title_text="Daily Vaccine Doses", row=1, col=1)
fig.update_yaxes(visible=False, row=2, col=1)
fig.update_layout(template='plotly_white', hovermode=False, height=500, margin=dict(t=20,b=40,l=40,r=20))

st.plotly_chart(fig, use_container_width=True)

# Insights Structured:
st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
st.subheader("🇲🇽 Mexico vs 🇧🇷 Brazil Key Insights")
st.write("""
         - **Brazil** reported **5x more COVID-19 cases** to the WHO than Mexico, which is partly explained by Brazil's larger population (214M vs 130M) but is primarily due to **significant differences in national testing and surveillance policies**.
         \n - **Mexico's higher CFR of 4.39%** compared to Brazil's 1.86% indicates posssible **case underreporting** in Mexico, meaning data availability was probably limited to only the most severe cases.
         \n - For both the Vaccine Rollout and Policy Timeline graphs, the data suddenly **begins in the first quarter of 2024**, confirming the **loss of all historical 2020-2023 data** due to the WHO file structure.
         \n - In February 2022, there is a noticable peak, signaling to the global Omicron wave: **Brazil reported approx. 184k aily cases**, while **Mexico reported approx. 20k daily cases**, further demonstrating Mexico's limited testing capacity during major surges.
         \n - In terms of vaccine rollout, based on the timeline and its available data, Mexico began administering vaccinations faster than Brazil, the empty space between trend lines most likely lies in the population differences.
         """)

st.divider()

st.subheader("❗️ Data Discrepancies")
st.write("""
         - Data availability for certain datasets is inconsistent in terms of dates.
         \n - For Daily Covid-19 Cases, data stops around 2023.
         \n - For Vaccine Rollout & Policy Timeline, data starts in the first quarter of 2024.
         \n- Datasets are found in the Official WHO Website: https://data.who.int/dashboards/covid19/data?n=o/""")
