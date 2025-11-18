import streamlit as st
import pandas as pd
from supabase import create_client

# ================================
# CARGA DEL EXCEL DE UNIDADES EJECUTORAS
# ================================
@st.cache_data
def cargar_unidades_ejecutoras():
    df = pd.read_excel("data/unidades_ejecutoras.xlsx")
    df["codigo"] = df["codigo"].astype(str)
    df["nombre"] = df["nombre"].astype(str)
    return df

df_ue = cargar_unidades_ejecutoras()

# ================================
# Credenciales Supabase
# ================================
url = st.secrets.get("SUPABASE_URL", "")
key = st.secrets.get("SUPABASE_KEY", "")
supabase = create_client(url, key)

st.title("Gestor PEI")

# ================================
# Búsqueda de UE
# ================================
st.header("🔎 Buscar Unidad Ejecutora")

query = st.text_input("Ingresa código o nombre de la Unidad Ejecutora")

if query:
    resultados = df_ue[
        df_ue.apply(lambda row: query.lower() in row["codigo"].lower()
                    or query.lower() in row["nombre"].lower(), axis=1)
    ]

    st.write("Resultados encontrados:", len(resultados))

    if not resultados.empty:
        seleccion = st.selectbox(
            "Selecciona una unidad ejecutora:",
            resultados.apply(lambda r: f"{r['codigo']} - {r['nombre']}", axis=1)
        )
    else:
        st.warning("No se encontraron coincidencias")
        seleccion = None
else:
    seleccion = None

# ================================
# Opciones
# ================================
if seleccion:
    st.success(f"Seleccionaste: {seleccion}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📌 Buscar Último PEI"):
            st.session_state["modo"] = "buscar"

    with col2:
        if st.button("📝 Nuevo Registro"):
            st.session_state["modo"] = "nuevo"

# ================================
# Procesamiento según opción
# ================================
if "modo" in st.session_state and seleccion:
    codigo = seleccion.split(" - ")[0]

    if st.session_state["modo"] == "buscar":
        st.subheader("📌 Último PEI registrado")

        data = supabase.table("pei").select("*") \
                      .eq("codigo_ue", codigo) \
                      .order("id", desc=True) \
                      .limit(1).execute().data

        if data:
            st.json(data[0])
        else:
            st.info("No existe historial para esta UE.")

    elif st.session_state["modo"] == "nuevo":
        st.subheader("📝 Crear nuevo registro PEI")
        st.write("Aquí va tu formulario de nuevo PEI...")
