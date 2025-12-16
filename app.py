import re
import streamlit as st
import pandas as pd
from datetime import datetime
#from supabase import create_client

# =====================================
# ✅ PARTE INTEGRADA (colocar al inicio)
# =====================================
HISTORIAL_PATH = "data/historial_it_pei.xlsx"

FORM_DEFAULTS = {
    "tipo_pei": "Formulado",
    "etapa_revision": "IT Emitido",
    "fecha_recepcion": None,
    "articulacion": "",
    "fecha_derivacion": None,
    "periodo": "",
    "cantidad_revisiones": 0,
    "comentario": "",
    "vigencia": "Sí",
    "estado": "En proceso",
    "expediente": "",
    "fecha_it": None,
    "fecha_oficio": None,
    "numero_it": "",
    "numero_oficio": "",
}

FORM_STATE_KEY = "pei_form_data"  # ✅ NUEVA KEY (ya no choca con st.form)

def init_form_state():
    st.session_state.setdefault(FORM_STATE_KEY, FORM_DEFAULTS.copy())

def reset_form_state():
    st.session_state[FORM_STATE_KEY] = FORM_DEFAULTS.copy()

def index_of(options, value, fallback=0):
    try:
        return options.index(value)
    except Exception:
        return fallback

def set_form_state_from_row(row: pd.Series):
    form = FORM_DEFAULTS.copy()

    def _safe_str(x): return "" if pd.isna(x) else str(x)
    def _safe_int(x):
        try: return int(x)
        except Exception: return 0

    def _safe_date(x):
        if pd.isna(x) or x is None or str(x).strip() == "":
            return None
        try:
            return pd.to_datetime(x).date()
        except Exception:
            return None

    form["tipo_pei"] = _safe_str(row.get("tipo_pei", FORM_DEFAULTS["tipo_pei"])) or FORM_DEFAULTS["tipo_pei"]
    form["etapa_revision"] = _safe_str(row.get("etapa_revision", FORM_DEFAULTS["etapa_revision"])) or FORM_DEFAULTS["etapa_revision"]
    form["fecha_recepcion"] = _safe_date(row.get("fecha_recepcion"))
    form["articulacion"] = _safe_str(row.get("articulacion", ""))
    form["fecha_derivacion"] = _safe_date(row.get("fecha_derivacion"))
    form["periodo"] = _safe_str(row.get("periodo", ""))
    form["cantidad_revisiones"] = _safe_int(row.get("cantidad_revisiones", 0))
    form["comentario"] = _safe_str(row.get("comentario", ""))
    form["vigencia"] = _safe_str(row.get("vigencia", FORM_DEFAULTS["vigencia"])) or FORM_DEFAULTS["vigencia"]
    form["estado"] = _safe_str(row.get("estado", FORM_DEFAULTS["estado"])) or FORM_DEFAULTS["estado"]
    form["expediente"] = _safe_str(row.get("expediente", ""))
    form["fecha_it"] = _safe_date(row.get("fecha_it"))
    form["numero_it"] = _safe_str(row.get("numero_it", ""))
    form["fecha_oficio"] = _safe_date(row.get("fecha_oficio"))
    form["numero_oficio"] = _safe_str(row.get("numero_oficio", ""))

    st.session_state[FORM_STATE_KEY] = form


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
#st.subheader(" Buscar Pliego")

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
                    Información del pliego seleccionado

                    Sector: {sector}
                    Nivel de gobierno: {nivel_gob}
                    Responsable institucional: {responsable}
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📌 Historial PEI"):
            st.session_state["modo"] = "historial"

    with col2:
        if st.button("📝 Nuevo registro"):
            st.session_state["modo"] = "nuevo"
            reset_form_state()
            st.rerun()


# ================================
# Procesamiento según opción
# ================================
if "modo" in st.session_state and seleccion:
    codigo = seleccion.split(" - ")[0].strip()
    codigo_norm = str(codigo).strip().lstrip("0")

    if st.session_state["modo"] == "historial":
        st.subheader("📌 Último PEI registrado")

        try:
            historial = pd.read_excel(HISTORIAL_PATH, engine="openpyxl")
            historial["codigo_ue_norm"] = (
            historial["codigo_ue"]
            .astype(str)
            .str.strip()
            .str.lstrip("0")   # 🔥 elimina ceros a la izquierda
        )
            
            # Normalizar nombres de columnas
            historial.columns = (
                historial.columns.astype(str)
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
            )
            
            # Diagnóstico rápido (temporal)
            st.write("Columnas detectadas en historial:", historial.columns.tolist())
            
            # Normalizar codigo_ue si existe
            if "codigo_ue" in historial.columns:
                historial["codigo_ue"] = historial["codigo_ue"].astype(str).str.strip()
            else:
                st.error("El historial no tiene la columna 'codigo_ue'. Revisa el Excel.")
                st.stop()
        except FileNotFoundError:
            st.error(f"No se encontró el archivo: {HISTORIAL_PATH}")
            historial = pd.DataFrame()

        if historial.empty:
            st.info("No hay historial disponible.")
        else:
            #df_historial = historial[historial["codigo_ue"].astype(str) == str(codigo)]
            #df_historial = historial[historial["codigo_ue"] == str(codigo).strip()]
            df_historial = historial[historial["codigo_ue_norm"] == codigo_norm]

            st.write("Filas encontradas para este pliego:", len(df_historial))
            if not df_historial.empty:
                st.dataframe(df_historial.tail(5), use_container_width=True)
            if df_historial.empty:
                st.info("No existe historial para este pliego.")
            else:
                # Asegurar orden por fecha
                if "fecha_recepcion" in df_historial.columns:
                    df_historial = df_historial.copy()
                    df_historial["fecha_recepcion"] = pd.to_datetime(df_historial["fecha_recepcion"], errors="coerce")

                ultimo = df_historial.sort_values("fecha_recepcion", ascending=False).iloc[0]
                st.success("Último registro encontrado.")

                colx, coly = st.columns([1, 2])
                with colx:
                    if st.button("⬇️ Cargar este registro al formulario", type="primary"):
                        init_form_state()
                        set_form_state_from_row(ultimo)
                        st.session_state["modo"] = "nuevo"   # Reutiliza el mismo formulario
                        st.rerun()

                with coly:
                    st.caption("Vista rápida del registro (solo verificación):")
                    st.json(ultimo.to_dict())

    elif st.session_state["modo"] == "nuevo":
        st.subheader("📝 Crear nuevo registro PEI")
    
        # ✅ Asegura que exista el estado del formulario (precarga desde historial)
        init_form_state()
        form = st.session_state[FORM_STATE_KEY]
        with st.form("form_pei"):
    
            st.write("## Datos de identificación y revisión")
    
            col1, col2, col3, col4 = st.columns([1, 1, 1.3, 1])
    
            # ======================
            # col1
            # ======================
            with col1:
                year_now = datetime.now().year
                año = st.text_input("Año", value=str(year_now), disabled=True)
    
                tipo_pei_opts = ["Formulado", "Ampliado", "Actualizado"]
                tipo_pei = st.selectbox(
                    "Tipo de PEI",
                    tipo_pei_opts,
                    index=index_of(tipo_pei_opts, form["tipo_pei"], 0)
                )
    
                etapas_opts = [
                    "IT Emitido",
                    "Para emisión de IT",
                    "Revisión DNCP",
                    "Revisión DNSE",
                    "Revisión DNPE",
                    "Subsanación del pliego"
                ]
                etapa_revision = st.selectbox(
                    "Etapas de revisión",
                    etapas_opts,
                    index=index_of(etapas_opts, form["etapa_revision"], 0)
                )
    
            # ======================
            # col2
            # ======================
            with col2:
                fecha_recepcion = st.date_input(
                    "Fecha de recepción",
                    value=form["fecha_recepcion"] if form["fecha_recepcion"] else datetime.now().date()
                )
    
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
    
                articulacion = st.selectbox(
                    "Articulación",
                    opciones_articulacion,
                    index=index_of(opciones_articulacion, form["articulacion"], 0) if opciones_articulacion else 0
                )
    
                fecha_derivacion = st.date_input(
                    "Fecha de derivación",
                    value=form["fecha_derivacion"] if form["fecha_derivacion"] else datetime.now().date()
                )
    
            # ======================
            # col3
            # ======================
            with col3:
                periodo = st.text_input(
                    "Periodo PEI (ej: 2025-2027)",
                    value=form["periodo"]
                )
    
                pattern = r"^\d{4}-\d{4}$"
                if periodo and not re.match(pattern, periodo):
                    st.error("⚠️ Formato inválido. Usa el formato: 2025-2027")
    
                cantidad_revisiones = st.number_input(
                    "Cantidad de revisiones",
                    min_value=0,
                    step=1,
                    value=int(form["cantidad_revisiones"] or 0)
                )
    
                comentario = st.text_area(
                    "Comentario adicional / Emisor de IT",
                    height=140,
                    value=form["comentario"]
                )
    
            # ======================
            # col4
            # ======================
            with col4:
                vigencia_opts = ["Sí", "No"]
                vigencia = st.selectbox(
                    "Vigencia",
                    vigencia_opts,
                    index=index_of(vigencia_opts, form["vigencia"], 0)
                )
    
                estado_opts = ["En proceso", "Emitido"]
                estado = st.selectbox(
                    "Estado",
                    estado_opts,
                    index=index_of(estado_opts, form["estado"], 0)
                )
    
            # =========================================
            #     PARTE 2 — DATOS DEL INFORME TÉCNICO
            # =========================================
            st.write("## Datos del Informe Técnico")
    
            colA, colB, colC = st.columns(3)
    
            with colA:
                expediente = st.text_input(
                    "Expediente (SGD)",
                    value=form["expediente"]
                )
    
            with colB:
                fecha_it = st.date_input(
                    "Fecha de I.T",
                    value=form["fecha_it"] if form["fecha_it"] else datetime.now().date()
                )
                fecha_oficio = st.date_input(
                    "Fecha del Oficio",
                    value=form["fecha_oficio"] if form["fecha_oficio"] else datetime.now().date()
                )
    
            with colC:
                numero_it = st.text_input(
                    "Número de I.T",
                    value=form["numero_it"]
                )
                numero_oficio = st.text_input(
                    "Número del Oficio",
                    value=form["numero_oficio"]
                )
    
            # ======================
            # SUBMIT
            # ======================
            submitted = st.form_submit_button("💾 Guardar Registro")
    
            if submitted:
                nombre_ue = seleccion.split(" - ")[1].strip()
    
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
