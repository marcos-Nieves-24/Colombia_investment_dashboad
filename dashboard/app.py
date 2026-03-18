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

geo_file = base_path / "data" / "raw_data" / "distribucion.csv"

df_geo = pd.read_csv(geo_file, sep=";", encoding="utf-8", engine="python", header=[0,1])
df_geo.columns = [
    f"{col[0]}_{col[1]}" if col[1] != '' else col[0]
    for col in df_geo.columns
]

#Columnas del dataset
st.write("Columnas:", df_geo.columns)
st.write(df_geo.head())

# carga del geojson
with open(input_file) as f:
    geojson = json.load(f)

# Clean columns
df_geo.columns = df_geo.columns.str.strip()

df_geo.columns = [
    col[1] if "departamento" in col[1] else f"{col[0]}_{col[1]}"
    for col in df_geo.columns
]

# Remove empty rows
df_geo = df_geo[df_geo["departamento"].notna()]

# Normalize names
df_geo["departamento"] = df_geo["departamento"].str.upper().str.strip()

df_geo = df_geo.rename(columns={"departamento": "departamento"})

df_geo = df_geo.loc[:, ~df_geo.columns.str.contains("Unnamed")]

# Fix known names
df_geo["departamento"] = df_geo["departamento"].replace({
    "BOGOTA": "BOGOTA D.C.",
    "SAN ANDRES": "ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA"
})

#cleaning numeric columns
for col in df_geo.columns:
    if "_" in col:
        df_geo[col] = (
            df_geo[col]
            .astype(str)
            .str.replace(",", ".")   # fix decimals
            .str.replace("%", "")    # remove %
        )
        df_geo[col] = pd.to_numeric(df_geo[col], errors="coerce")

# Select a year column (example: 2023)
presidentes = sorted(set(col.split("_")[0] for col in df_geo.columns if "_" in col))

presidente = st.selectbox("Select president", presidentes)

cols_presidente = [col for col in df_geo.columns if col.startswith(presidente)]

years = [col.split("_")[1] for col in cols_presidente]

year = st.selectbox("Select year", years)

selected_col = f"{presidente}_{year}"

# Prepare data
df_map = df_geo[["departamento", selected_col]].copy()
df_map = df_map.dropna()

# Create map
fig = px.choropleth(
    df_map,
    geojson=geojson,
    locations="departamento",
    featureidkey="properties.NOMBRE_DPT",
    color=selected_col,
    color_continuous_scale="Reds",
    title=f"{presidente} - {year}"
)

fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)

