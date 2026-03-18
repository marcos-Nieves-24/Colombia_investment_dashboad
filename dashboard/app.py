import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import statsmodels.api as sm
import json
import unicodedata

st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
</style>
""", unsafe_allow_html=True)


# 📌 Configuración
st.set_page_config(page_title="Inversión en Educación - Colombia", layout="wide")

st.title("Inversión en Educación en Colombia (2002-2025)")

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
    "Gasto total (constante)",
    f"{df_filtrado['presupuesto_por_ano_constante'].sum():,.0f}"
)

col2.metric(
    "Promedio inflación",
    f"{df_filtrado['tasa_inflacion_por_ano'].mean():.2f}%"
)

col3.metric(
    "Años analizados",
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

# --------------------------
# dashboard geomap Colombia
# ---------------------------
base_path = Path(__file__).resolve().parent.parent

input_file = base_path / "data" / "raw_data" / "colombia.geo.json"

geo_file = base_path / "data" / "raw_data" / "distribucion.csv"

# -----------------
# carga del dataset
# -----------------
df_geo = pd.read_csv(geo_file, sep=";", encoding="utf-8", header=1)

df_geo.columns = df_geo.columns.astype(str).str.strip()


# ----------------
# renombrar columnas
# ----------------

df_geo.rename(columns={df_geo.columns[0]: "departamento"}, inplace=True)

# carga del geojson
with open(input_file) as f:
    geojson = json.load(f)

# -----------------------------
# Clean data
# -----------------------------

# Clean column names
df_geo.columns = df_geo.columns.str.strip().str.lower()

    
# Clean department names
df_geo["departamento"] = df_geo["departamento"].astype(str)
df_geo["departamento"] = df_geo["departamento"].str.upper().str.strip()

# Remove empty rows
df_geo = df_geo[df_geo["departamento"].notna()]

# Fix known mismatches
df_geo["departamento"] = df_geo["departamento"].replace({
    "BOGOTA": "BOGOTA D.C."})

# -----------------------------
# reparar nombres de departamentos
# -----------------------------

def clean_text(text):
    text = str(text).upper().strip()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return text

df_geo["departamento"] = df_geo["departamento"].apply(clean_text)

for f in geojson["features"]:
    f["properties"]["NOMBRE_DPT"] = clean_text(f["properties"]["NOMBRE_DPT"])

# -----------------------------
# Departamentos no encontrados en el geojson
# ------------------------------

geo_names = [f["properties"]["NOMBRE_DPT"] for f in geojson["features"]]
missing = [name for name in df_geo["departamento"].unique() if name not in geo_names]


# limpiar los años (convertir a numérico)
for col in df_geo.columns:
    if col != "departamento":
        df_geo[col] = (
            df_geo[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )
        df_geo[col] = pd.to_numeric(df_geo[col], errors="coerce")



# -----------------------------
# UI
# -----------------------------
st.markdown("---")
st.title("Mapa de distribución de educación en Colombia")

# selección de año
years = [col for col in df_geo.columns if col.isdigit()]

year = st.sidebar.selectbox("Seleccionar el año", sorted(years))

# -----------------------------
# Mapa de calor
# -----------------------------
#debug
df_geo.columns = (
    df_geo.columns
    .astype(str)
    .str.strip()
    .str.replace("\n", "")
)

df_geo = df_geo.drop(columns=["unnamed: 1"], errors="ignore")

df_geo = df_geo[["departamento"] + sorted(
    [col for col in df_geo.columns if col != "departamento"],
    key=lambda x: int(x)
)]

df_long = df_geo.melt(
    id_vars="departamento",
    var_name="year",
    value_name="value"
)


df_long["year"] = df_long["year"].astype(int)
df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

st.write(df.head())
st.write(df_long.head(20))

st.write("Columnas DEBUG:")
for col in df_geo.columns:
    st.write(f"'{col}'")

df_map = df_geo[["departamento", year]].copy()



fig_mapa = px.choropleth(
    df_map,
    geojson=geojson,
    locations="departamento",
    featureidkey="properties.NOMBRE_DPT",
    color=year,
    color_continuous_scale="Viridis",
    title="Distribución de educación en Colombia - {year}".format(year=year)
)

fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_traces(marker_line_width=0.5, marker_line_color="white")
st.plotly_chart(fig_mapa, use_container_width=True)