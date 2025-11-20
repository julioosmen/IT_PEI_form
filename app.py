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
df_ue["codigo"] = df_ue["codigo"].astype(str).str.strip()
df_ue["NG"] = df_ue["NG"].astype(str).str.strip()

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
    #st.success(f"Seleccionaste: {seleccion}")
    #codigo = seleccion.split(" - ")[0]
    codigo = seleccion.split(" - ")[0].strip()  # ✔️ ahora sí existe
    # Filtrar la fila correspondiente
    fila = df_ue[df_ue["codigo"] == codigo]

    if not fila.empty:
        sector = fila["sector"].iloc[0]
        nivel_gob = fila["NG"].iloc[0]
        responsable = fila["Responsable_Institucional"].iloc[0] if "Responsable_Institucional" in fila.columns else "No registrado"

        # TARJETA HTML
        st.markdown(
            f"""
            <div style="
                padding: 14px 18px;
                border-radius: 10px;
                background-color: #F5F7FA;
                margin-top: 10px;
                border: 1px solid #E0E6ED;
                font-size: 14px;
                color: #333;
            ">
                    **Información del pliego seleccionado**

                    Sector: {sector}
                    Nivel de gobierno: {nivel_gob}
                    Responsable institucional: {responsable}
            </div>
            """,
            unsafe_allow_html=True
        )

 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📌 Historial PEI"):
            st.session_state["modo"] = "historial"

    with col2:
        if st.button("📝 Nuevo registro"):
            st.session_state["modo"] = "nuevo"

# ================================
# Procesamiento según opción
# ================================
if "modo" in st.session_state and seleccion:
    codigo = seleccion.split(" - ")[0]

    if st.session_state["modo"] == "historial":
        st.subheader("📌 Último PEI registrado")

        #data = supabase.table("pei").select("*") \
        #              .eq("codigo_ue", codigo) \
        #              .order("id", desc=True) \
        #              .limit(1).execute().data

        #if data:
        #    st.json(data[0])
        #else:
        #    st.info("No existe historial para esta UE.")

        historial = pd.read_excel("data/historial_it_pei.xlsx")
    
        #df_ue = historial[historial["codigo_ue"] == codigo]
        df_historial = historial[historial["codigo_ue"].astype(str) == str(codigo)]

        if df_historial.empty:
            st.info("No existe historial para este pliego.")
        else:
            ultimo = df_historial.sort_values("fecha_recepcion", ascending=False).iloc[0]
            st.success("Último registro encontrado:")
            st.json(ultimo.to_dict())

    #elif st.session_state["modo"] == "nuevo":
        #st.subheader("📝 Crear nuevo registro PEI")
        #st.write("Aquí va tu formulario de nuevo PEI...")

    elif st.session_state["modo"] == "nuevo":
        st.subheader("📝 Crear nuevo registro PEI")
    
        with st.form("form_pei"):
    
            st.write("## Datos de identificación y revisión")
    
            col1, col2, col3, col4 = st.columns([1, 1, 1.3, 1])
            #col1, col2, col3, col4 = st.columns(4, gap="medium")

            # ======================
            # col1
            # ======================
            with col1:
                year_now = datetime.now().year
                año = st.text_input("Año", value=str(year_now), disabled=True)
    
                tipo_pei = st.selectbox("Tipo de PEI", [
                    "Actualizado", "Ampliado", "Formulado"
                ])
    
                etapa_revision = st.selectbox("Etapas de revisión", [
                    "IT Emitido",
                    "Para emisión de IT",
                    "Revisión DNCP",
                    "Revisión DNSE",
                    "Revisión DNPE",
                    "Subsanación del pliego"
                ])
    
            # ======================
            # col2
            # ======================
            with col2:
                fecha_recepcion = st.date_input("Fecha de recepción")
    
                # Nivel de gobierno
                nivel = df_ue.loc[df_ue["codigo"] == codigo, "NG"].values[0]
    
                if nivel == "Gobierno regional":
                    opciones_articulacion = ["PEDN 2050", "PDRC"]
                elif nivel == "Gobierno nacional":
                    opciones_articulacion = ["PEDN 2050", "PESEM NO vigente", "PESEM vigente"]
                elif nivel in ["Municipalidad distrital", "Municipalidad provincial"]:
                    opciones_articulacion = ["PEDN 2050", "PDRC", "PDLC Provincial", "PDLC Distrital"]
                else:
                    opciones_articulacion = []
    
                articulacion = st.selectbox("Articulación", opciones_articulacion)
    
                fecha_derivacion = st.date_input("Fecha de derivación")
    
            # ======================
            # col3
            # ======================
            with col3:
                periodo = st.text_input("Periodo PEI (ej: 2025-2027)")
                cantidad_revisiones = st.number_input("Cantidad de revisiones", min_value=0, step=1)
                
                comentario = st.text_area("Comentario adicional / Emisor de IT", height=140)

            # ======================
            # col4
            # ======================
            with col4:
                vigencia = st.selectbox("Vigencia", ["Sí", "No"])
    
                estado = st.selectbox("Estado", [
                    "Emitido",
                    "En proceso"
                ])
     
            # =========================================
            #     PARTE 2 — DATOS DEL INFORME TÉCNICO
            # =========================================
            st.write("## Datos del Informe Técnico")
    
            colA, colB, colC = st.columns(3)
    
            with colA:
                expediente = st.text_input("Expediente (SGD)")
    
            with colB:
                fecha_it = st.date_input("Fecha de I.T")
                fecha_oficio = st.date_input("Fecha del Oficio")
    
            with colC:
                numero_it = st.text_input("Número de I.T")
                numero_oficio = st.text_input("Número del Oficio")
    
            # ======================
            # Responsable
            # ======================
            responsables = pd.read_excel("data/responsables.xlsx")["nombre"].tolist()
    
            responsable = st.selectbox(
                "Responsable Institucional",
                responsables,
                index=None,
                placeholder="Escribe tu nombre..."
            )
    
            # ======================
            # SUBMIT
            # ======================
            submitted = st.form_submit_button("💾 Guardar Registro")
    
            if submitted:
                nombre_ue = seleccion.split(" - ")[1]
    
                nuevo = {
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
                    "expediente": expediente,
                    "fecha_it": str(fecha_it),
                    "numero_it": numero_it,
                    "fecha_oficio": str(fecha_oficio),
                    "numero_oficio": numero_oficio
                }
    
                st.session_state["nuevo_registro"] = nuevo
                st.success("✔ Registro listo para guardar en Excel")
