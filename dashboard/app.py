import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import statsmodels.api as sm
import json
import unicodedata

st.markdown("""
<style>
/* Fondo general */
.main {
    background-color: #0E1117;
}

/* KPI cards */
[data-testid="metric-container"] {
    background-color: #1c1f26;
    border-radius: 10px;
    padding: 15px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111418;
}

/* Títulos */
h1, h2, h3 {
    color: #EAEAEA;
}

/* Espaciado */
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# 📌 Configuración
st.set_page_config(page_title="Inversión en investigación y educación superior - Colombia", layout="wide")

st.title("Inversión en investigación y educación superior en Colombia (2002-2025)")

# ubicación del dataset limpio
base_path = Path(__file__).resolve().parent.parent

input_file = base_path / "data" / "raw_data" / "processed_data" / "gastos_presidentes_limpio.csv"

# 📥 Cargar datos
df = pd.read_csv(input_file,
        sep=None,
        encoding="utf-8",
        engine="python"
    )

pib_dict = {
    2002: 330,
    2003: 360,
    2004: 400,
    2005: 450,
    2006: 500,
    2007: 550,
    2008: 620,
    2009: 630,
    2010: 700,
    2011: 780,
    2012: 850,
    2013: 900,
    2014: 950,
    2015: 1000,
    2016: 1050,
    2017: 1100,
    2018: 976,
    2019: 1000,
    2020: 1065,
    2021: 1177,
    2022: 1420,
    2023: 1593,
    2024: 1700,
    2025: 1800
}

df["PIB"] = df["año"].map(pib_dict)

df["presupuesto_billones"] = df["presupuesto_por_ano_constante"] / 1_000_000_000_000

df["gasto_pct_pib"] = (
    df["presupuesto_billones"] / df["PIB"]
) * 100

# 🎛️ FILTROS
st.sidebar.header("Filtros")

presidentes = st.sidebar.multiselect(
    "Selecciona presidente",
    options=df["presidente"].unique(),
    default=df["presidente"].unique()
)

df_filtrado = df[df["presidente"].isin(presidentes)]

# 📊 KPIs
col1, col2, col3, col4 = st.columns(4)

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

col4.metric(
    "Gasto % PIB",
    f"{df_filtrado['gasto_pct_pib'].mean():.2f}%"
)

COLOR_PALETTE = px.colors.qualitative.Set2

# 📈 GRAFICO 1: Gasto por año
st.subheader("Presupuesto por Año")

fig1 = px.line(
    df_filtrado,
    x="año",
    y="presupuesto_por_ano_constante",
    color="presidente",
    markers=True,
    color_discrete_sequence=COLOR_PALETTE,
    title="Evolución del presupuesto presidencial en I+D (2002-2025)",
    labels={
        "año": "Año",
        "presupuesto_por_ano_constante": "Presupuesto ejecutado en mil millones (COP)"
    }
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
    color="presidente",
    color_discrete_sequence=COLOR_PALETTE,
    labels={
        "presidente": "Presidente",
        "presupuesto_por_ano_constante": "Presupuesto acumulado en mil millones (COP)"
    }
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
    line_shape="spline",
    labels={
        "año": "Año",
        "tasa_inflacion_por_ano": "Tasa de inlación por año"
    }
)

# display the figure
st.plotly_chart(fig3, use_container_width=True)

# 📊 GRAFICO 4: Relación inflación vs gasto
st.subheader("Impacto de la inflación en el presupuesto")

fig4 = px.scatter(
    df_filtrado,
    x="tasa_inflacion_por_ano",
    y="presupuesto_por_ano_constante",
    color="presidente",
    color_discrete_sequence=COLOR_PALETTE,
    trendline="ols",
        labels={
        "presupuesto_por_ano_constante": "Presupuesto por año constante (mil millones)",
        "tasa_inflacion_por_ano": "Tasa de inlación por año"
    }
)

st.write(df[["año", "gasto_pct_pib"]].head(10))

fig_pib = px.line(
    df_filtrado,
    x="año",
    y="gasto_pct_pib",
    color="presidente",
    markers=True,
    labels={
        "gasto_pct_pib": "% del PIB",
        "año": "Año"
    }
)

fig_pib.update_layout(
    template="plotly_white"
)

fig_pib.update_yaxes(
    title_text="% del PIB",
    ticksuffix="%"
)

st.plotly_chart(fig_pib, use_container_width=True)

# display the figure
st.plotly_chart(fig4, use_container_width=True)

# estilos personalizados
fig1.update_layout(
    template="plotly_white",  
    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Arial",
        size=12,
        color="#2C2C2C"
    ),

    margin=dict(l=40, r=40, t=40, b=40),

    xaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    )
)

fig1.update_layout(
    xaxis_title="Año",
    yaxis_title="Presupuesto (COP)"
)

fig2.update_layout(
    template="plotly_white",  
    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Arial",
        size=12,
        color="#2C2C2C"
    ),

    margin=dict(l=40, r=40, t=40, b=40),

    xaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    )
)

fig2.update_traces(
    texttemplate='%{y:,.0f}',
    textposition='outside'
)

fig3.update_layout(
    template="plotly_white",  
    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Arial",
        size=12,
        color="#2C2C2C"
    ),

    margin=dict(l=40, r=40, t=40, b=40),

    xaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    )
)

fig4.update_layout(
    template="plotly_white",  
    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Arial",
        size=12,
        color="#2C2C2C"
    ),

    margin=dict(l=40, r=40, t=40, b=40),

    xaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#E5E5E5"
    )
)

# 📋 Tabla
st.subheader("Resumen de inversión en investigación")

st.markdown("Tabla de datos")
# 1. Renombrar columnas (aquí nace df_display)
df_display = df_filtrado.rename(columns={
    "presidente": "Presidente",
    "año": "Año",
    "presupuesto_por_ano_constante": "Presupuesto (mil millones COP)",
    "tasa_inflacion_por_ano": "Inflación (%)"
})

# 2. Seleccionar columnas importantes
df_display = df_display[
    ["Presidente", "Año", "Presupuesto (mil millones COP)", "Inflación (%)"]
]

# 3. Ordenar (opcional pero pro)
df_display = df_display.sort_values(by="Presupuesto (mil millones COP)", ascending=False)

# 4. Aplicar estilo (🔥 lo importante)
styled_df = (
    df_display.style
    .format({
        "Presupuesto (mil millones COP)": "${:,.0f}",
        "Inflación (%)": "{:.2f}%"
    })
    .background_gradient(subset=["Presupuesto (mil millones COP)"], cmap="Blues")
    .background_gradient(subset=["Inflación (%)"], cmap="Reds")
    .bar(subset=["Presupuesto (mil millones COP)"], color="#5DADE2")
)


st.dataframe(styled_df, use_container_width=True)

st.markdown("""
<style>
[data-testid="stDataFrame"] {
    background-color: #0E1117;
    border-radius: 12px;
    padding: 10px;
}

thead tr th {
    background-color: #1c1f26 !important;
    color: #EAEAEA !important;
    font-weight: bold;
}

tbody tr:hover {
    background-color: #262730 !important;
}
</style>
""", unsafe_allow_html=True)



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


df_map = df_geo[["departamento", year]].copy()


fig_mapa = px.choropleth(
    df_map,
    geojson=geojson,
    locations="departamento",
    featureidkey="properties.NOMBRE_DPT",
    color=year,
    color_continuous_scale="Plasma"  # 🔥 mejor que Viridis para contraste
)

fig_mapa.update_layout(
    template="plotly_dark",
    margin={"r":0,"t":0,"l":0,"b":0}
)


fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_traces(marker_line_width=0.5, marker_line_color="white")
st.plotly_chart(fig_mapa, use_container_width=True)

