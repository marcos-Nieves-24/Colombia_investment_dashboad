import pandas as pd
from pathlib import Path
import unicodedata


# ==============================
# 1. rutas
# ==============================

base_path = Path(__file__).resolve().parent.parent

input_file = base_path / "data" / "raw_data" / "gasto_presidentes.csv"
output_file = base_path / "data" / "raw_data" / "processed_data" / "gastos_presidentes_limpio.csv"

# ==============================
# 3. cargar datos
# ==============================
import pandas as pd

# 📥 cargar datos
df = pd.read_csv(input_file,
    sep=";",
    encoding="utf-8"
)

print("Shape original:", df.shape)

# 🧹 limpiar nombres columnas
df.columns = df.columns.str.strip()

# 🧹 eliminar filas vacías (sin año)
df = df[df["año"].notna()]

# 🧹 convertir año a entero
df["año"] = df["año"].astype(int)

# 🧹 limpiar inflación
df["tasa_inflacion_por_ano"] = (
    df["tasa_inflacion_por_ano"]
    .astype(str)
    .str.replace("%", "")
    .str.replace(",", ".")
)

df["tasa_inflacion_por_ano"] = pd.to_numeric(
    df["tasa_inflacion_por_ano"],
    errors="coerce"
)

# 🧹 limpiar inflación acumulada
df["tasa_inflacion_acumulada _por_periodo"] = (
    df["tasa_inflacion_acumulada _por_periodo"]
    .astype(str)
    .str.replace("%", "")
    .str.replace(",", ".")
)

df["tasa_inflacion_acumulada _por_periodo"] = pd.to_numeric(
    df["tasa_inflacion_acumulada _por_periodo"],
    errors="coerce"
)

# 🧹 convertir columnas numéricas
cols_numericas = [
    "presupuesto_por_ano_constante",
    "presupuesto_por_periodo_constante",
    "presupuesto_por_ano_corriente",
    "presupuesto_por_periodo_corriente"
]

for col in cols_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 💾 guardar limpio
df.to_csv(output_file, index=False)

print("Shape limpio:", df.shape)
print(df.head())