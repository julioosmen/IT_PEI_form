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

st.title("IT_PEI formulario")

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
        if st.button("📌 Buscar último PEI"):
            st.session_state["modo"] = "buscar"

    with col2:
        if st.button("📝 Nuevo registro"):
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

    #elif st.session_state["modo"] == "nuevo":
        #st.subheader("📝 Crear nuevo registro PEI")
        #st.write("Aquí va tu formulario de nuevo PEI...")

    elif st.session_state["modo"] == "nuevo":
        st.subheader("📝 Crear nuevo registro PEI")
    
        # ----------------------------------------
        # FORMULARIO COMPLETO
        # ----------------------------------------
        with st.form("form_pei"):
    
            st.write("### Datos de identificación")
    
            col1, col2 = st.columns(2)
            with col1:
                año = st.number_input("Año", min_value=2000, max_value=2100, step=1)
                periodo = st.text_input("Periodo PEI (ej: 2025-2027)")
                #vigencia = st.text_input("Vigencia")
                vigencia = st.selectbox("Vigencia", ["Sí", "No"])
                tipo_pei = st.selectbox("Tipo de PEI", ["Actualizado", "Ampliado", "Formulado", "Modificado"])
            with col2:
                estado = st.selectbox("Estado", [
                    "Emitido",
                    "En proceso"
                ])
                cantidad_revisiones = st.number_input("Cantidad de revisiones", min_value=0, step=1)
                etapa_revision = st.selectbox("Etapas de revisión", [
                    "IT Emitido",
                    "Para emisión de IT",
                    "Revisión DNCP",
                    "Revisión DNSE",
                    "Revisión DNPE",
                    "Subsanación del pliego"
                ])
                #articulacion = st.text_input("Articulación")
                articulacion = st.selectbox("Articulación", [
                    "PDLC Distrital",
                    "PDLC Provincial",
                    "PDRC",
                    "PEDN 2050",
                    "PESEM NO vigente",
                    "PESEM vigente"
                ])
            
            st.write("### Fechas y documentos")
    
            col3, col4 = st.columns(2)
            with col3:
                fecha_recepcion = st.date_input("Fecha de recepción")
                fecha_derivacion = st.date_input("Fecha de derivación")
            with col4:
                fecha_it = st.date_input("Fecha de I.T")
                numero_it = st.text_input("Número de I.T")
    
            comentario = st.text_area("Comentario adicional / Emisor de IT")
            #responsable = st.text_input("Responsable Institucional")
            responsables = pd.read_excel("data/responsables.xlsx")["nombre"].tolist()
            
            responsable = st.selectbox(
                "Responsable Institucional",
                responsables,
                index=None,
                placeholder="Escribe tu nombre..."
            )
            
            # Submit
            submitted = st.form_submit_button("💾 Guardar Registro")
    
            if submitted:
                codigo = seleccion.split(" - ")[0]
                nombre_ue = seleccion.split(" - ")[1]
    
                data = {
                    "codigo_ue": codigo,
                    "nombre_ue": nombre_ue,
                    "año": año,
                    "periodo": periodo,
                    "vigencia": vigencia,
                    "tipo_pei": tipo_pei,
                    "estado": estado,
                    "responsable_institucional": responsable,
                    "cantidad_revisiones": cantidad_revisiones,
                    "fecha_recepcion": str(fecha_recepcion),
                    "fecha_derivacion": str(fecha_derivacion),
                    "etapa_revision": etapa_revision,
                    "comentario": comentario,
                    "articulacion": articulacion,
                    "expediente": "",
                    "fecha_it": str(fecha_it),
                    "numero_it": numero_it
                }
    
                resp = supabase.table("pei").insert(data).execute()
    
                if resp.data:
                    st.success("Registro guardado correctamente 🎉")
                else:
                    st.error("Hubo un problema al guardar el registro")
