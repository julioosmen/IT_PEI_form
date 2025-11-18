import streamlit as st
import pandas as pd
from datetime import datetime
#from supabase import create_client

# =====================================
# 🏛️ Carga y búsqueda de unidades ejecutoras
# =====================================
@st.cache_data
def cargar_unidades_ejecutoras():
    return pd.read_excel("data/unidades_ejecutoras.xlsx", engine="openpyxl")

df_ue = cargar_unidades_ejecutoras()

#st.image("logo.png", width=160)   # Mostrar logo centrado - Ajusta el tamaño si deseas
st.title("Registro de IT del Plan Estratégico Institucional (PEI)")
st.subheader(" Buscar Pliego")

# Crear opciones combinadas para búsqueda
opciones = [
    f"{str(row['codigo'])} - {row['nombre']}"
    for _, row in df_ue.iterrows()
]

# Selectbox con búsqueda tanto por código como por nombre
seleccion = st.selectbox(
    "🔍 Selecciona o escribe el código o nombre del pliego",
    opciones,
    index=None,
    placeholder="Escribe el código o nombre..."
)

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
                #año = st.number_input("Año", min_value=2000, max_value=2100, step=1)
                year_now = datetime.now().year
                año = st.text_input(
                    "Año",
                    value=str(year_now),
                    disabled=True
                )
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
