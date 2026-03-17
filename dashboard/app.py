import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import statsmodels.api as sm
import json


st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
</style>
""", unsafe_allow_html=True)

# 📌 Configuración
st.set_page_config(page_title="Inversión en Educación - Colombia", layout="wide")

st.title("📊 Inversión en Educación en Colombia (2002-2025)")

# ubicación del dataset limpio
base_path = Path(__file__).resolve().parent.parent

input_file = base_path / "data" / "raw_data" / "processed_data" / "gastos_presidentes_limpio.csv"

# 📥 Cargar datos
df = pd.read_csv(input_file,
        sep=None,
        encoding="utf-8",
        engine="python"
    )


# 🎛️ FILTROS
st.sidebar.header("Filtros")

presidentes = st.sidebar.multiselect(
    "Selecciona presidente",
    options=df["presidente"].unique(),
    default=df["presidente"].unique()
)

df_filtrado = df[df["presidente"].isin(presidentes)]

# 📊 KPIs
col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Gasto total (constante)",
    f"{df_filtrado['presupuesto_por_ano_constante'].sum():,.0f}"
)

col2.metric(
    "📈 Promedio inflación",
    f"{df_filtrado['tasa_inflacion_por_ano'].mean():.2f}%"
)

col3.metric(
    "📅 Años analizados",
    df_filtrado["año"].nunique()
)

# 📈 GRAFICO 1: Gasto por año
st.subheader("Presupuesto por Año")

fig1 = px.line(
    df_filtrado,
    x="año",
    y="presupuesto_por_ano_constante",
    color="presidente",
    markers=True,
    title="Evolución del presupuesto (pesos constantes)"
)

# display the figure
st.plotly_chart(fig1, use_container_width=True)

# 📊 GRAFICO 2 Comparación por presidente
st.subheader("Gasto total por presidente")

df_group = df_filtrado.groupby("presidente")["presupuesto_por_ano_constante"].sum().reset_index()

fig2 = px.bar(
    df_group,
    x="presidente",
    y="presupuesto_por_ano_constante",
    title="Gasto total por presidente"
)

# display the figure
st.plotly_chart(fig2, use_container_width=True)

# 📉 GRAFICO 3: Inflación
st.subheader("Inflación por año")

fig3 = px.line(
    df_filtrado,
    x="año",
    y="tasa_inflacion_por_ano",
    markers=True,
    title="Inflación anual (%)"
)

# display the figure
st.plotly_chart(fig3, use_container_width=True)

# 📊 GRAFICO 4: Relación inflación vs gasto
st.subheader("Relación inflación vs presupuesto")

fig4 = px.scatter(
    df_filtrado,
    x="tasa_inflacion_por_ano",
    y="presupuesto_por_ano_constante",
    color="presidente",
    trendline="ols",
    title="¿La inflación afecta el gasto?"
)

# display the figure
st.plotly_chart(fig4, use_container_width=True)

# estilos personalizados
fig1.update_layout(
    template="plotly_dark",
    title_font_size=20
)
fig2.update_layout(
    template="plotly_dark",
    title_font_size=20
)
fig3.update_layout(
    template="plotly_dark",
    title_font_size=20
)
fig4.update_layout(
    template="plotly_dark",
    title_font_size=20
)


# 📋 Tabla
st.subheader("Datos filtrados")

st.dataframe(df_filtrado)

#dashboard geomap colombia
base_path = Path(__file__).resolve().parent.parent

input_file = base_path / "data" / "raw_data" / "colombia.geo.json"

# carga del geojson
with open(input_file) as f:
    geojson = json.load(f)

# Clean department names (IMPORTANT)
df["departamento"] = df["departamento"].str.upper()
df["departamento"] = df["departamento"].str.strip()

# Select a year column (example: 2023)
year = st.selectbox("Select year", [col for col in df.columns if col.isdigit()])

# Prepare data
df_map = df[["departamento", year]].copy()
df_map = df_map.dropna()

# Create map
fig = px.choropleth(
    df_map,
    geojson=geojson,
    locations="departamento",
    featureidkey="properties.NOMBRE_DPT",
    color=year,
    color_continuous_scale="Blues",
    title=f"Colombia Map - {year}"
)

fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)

