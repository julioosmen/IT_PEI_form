import re
import streamlit as st
import pandas as pd
import os
from datetime import datetime
#from supabase import create_client

def guardar_en_historial_excel(nuevo: dict, path: str):
    """
    Guarda un nuevo registro en el Excel historial_it_pei.xlsx
    - Si el archivo no existe, lo crea
    - Si existe, agrega una nueva fila
    """

    # Normalización robusta del código
    def normalizar_codigo(x):
        if pd.isna(x) or x is None:
            return ""
        try:
            return str(int(float(x)))   # 23.0 -> "23"
        except Exception:
            return str(x).strip()

    # 1) Dict -> DataFrame (1 fila)
    df_nuevo = pd.DataFrame([nuevo])

    # 2) Asegurar columna normalizada
    df_nuevo["codigo_ue_norm"] = df_nuevo["codigo"].apply(normalizar_codigo)

    # 3) Crear archivo si no existe
    if not os.path.exists(path):
        df_nuevo.to_excel(path, index=False, engine="openpyxl")
        return

    # 4) Leer historial existente
    df_hist = pd.read_excel(path, engine="openpyxl")
    df_hist.columns = df_hist.columns.astype(str).str.strip()

    # 5) Concatenar y sobrescribir
    df_final = pd.concat([df_hist, df_nuevo], ignore_index=True, sort=False)
    df_final.to_excel(path, index=False, engine="openpyxl")

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

    # ================================
    # MODO: HISTORIAL
    # ================================
    if st.session_state["modo"] == "historial":
        st.subheader("📌 Historial PEI")

        try:
            # 1) Cargar historial
            historial = pd.read_excel(HISTORIAL_PATH, engine="openpyxl")

            # 2) Normalizar nombres de columnas (primero)
            historial.columns = (
                historial.columns.astype(str)
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
            )

            # 3) Validar columna clave
            if "codigo" not in historial.columns:
                st.error("❌ El historial no tiene la columna 'codigo'. Revisa el Excel.")
                st.write("Columnas detectadas:", historial.columns.tolist())
                st.stop()

            # 4) Crear columna normalizada para comparar (desde 'codigo')
            def normalizar_codigo(x):
                if pd.isna(x):
                    return ""
                try:
                    return str(int(float(x)))  # 23.0 → "23"
                except Exception:
                    return str(x).strip()
    
            historial["codigo_ue_norm"] = historial["codigo"].apply(normalizar_codigo)

        except FileNotFoundError:
            st.error(f"No se encontró el archivo: {HISTORIAL_PATH}")
            st.stop()
        except Exception as e:
            st.error(f"Error al leer el historial: {e}")
            st.stop()

        codigo_norm = normalizar_codigo(codigo)

        # ================================
        # 🔎 DIAGNÓSTICO DE CÓDIGOS
        # ================================
        #st.markdown("### 🔎 Diagnóstico de coincidencia de códigos")
        #st.write("Código seleccionado (raw):", codigo)
        #st.write("Código seleccionado (normalizado):", codigo_norm)

        # Muestra algunos valores reales del historial para verificar si hay match
        #st.write(
        #    "Códigos únicos en historial (raw, primeros 15):",
        #    historial["codigo"].astype(str).unique()[:15]
        #)
        #st.write(
        #    "Códigos únicos en historial (normalizados, primeros 15):",
        #    historial["codigo_ue_norm"].unique()[:15]
        #)

        # (Opcional) muestra filas donde el código normalizado coincide parcialmente
        # útil si el código viene con prefijos/sufijos o formatos distintos
        #try:
            #posibles = historial[historial["codigo"].astype(str).str.contains(str(codigo), na=False)].head(10)
            #if not posibles.empty:
                #st.write("Posibles coincidencias por 'contains' (primeras 10 filas):")
                #st.dataframe(posibles, use_container_width=True, hide_index=True)
        #except Exception:
            #pass

        # ================================
        # 5) Filtrar historial por pliego/UE
        # ================================
        df_historial = historial[historial["codigo_ue_norm"] == codigo_norm].copy()

        st.write("Filas encontradas para este pliego:", len(df_historial))

        if df_historial.empty:
            st.info("No existe historial para este pliego (según la clave de comparación).")
        else:
            # Asegurar orden por fecha
            if "fecha_recepcion" in df_historial.columns:
                df_historial["fecha_recepcion"] = pd.to_datetime(
                    df_historial["fecha_recepcion"], errors="coerce"
                )

            # Mostrar vista
            st.dataframe(df_historial.tail(5), use_container_width=True, hide_index=True)

            # Tomar último por fecha
            if "fecha_recepcion" in df_historial.columns:
                ultimo = df_historial.sort_values("fecha_recepcion", ascending=False).iloc[0]
            else:
                ultimo = df_historial.iloc[-1]

            st.success("Último registro encontrado.")

            colx, coly = st.columns([1, 2])
            with colx:
                if st.button("⬇️ Cargar último registro disponible al formulario", type="primary"):
                    init_form_state()
                    set_form_state_from_row(ultimo)
                    st.session_state["modo"] = "nuevo"   # Reutiliza el mismo formulario
                    st.rerun()

            #with coly:
                #st.caption("Vista rápida del registro (solo verificación):")
                #st.json(ultimo.to_dict())

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

            # Reglas para habilitar "Emitido"
            expediente_ok = bool(str(expediente).strip())
            fecha_it_ok = fecha_it is not None
            numero_it_ok = bool(str(numero_it).strip())
            
            puede_emitir = expediente_ok and fecha_it_ok and numero_it_ok

            if estado == "Emitido" and not puede_emitir:
                st.caption(
                    "⚠️ Para marcar como *Emitido* debes registrar: "
                    "Expediente (SGD), Fecha de I.T y Número de I.T."
                )
            
            # ======================
            # SUBMIT
            # ======================
            submitted = st.form_submit_button("💾 Guardar Registro")

            if submitted:
                if estado == "Emitido" and not puede_emitir:
                    st.error("❌ No se puede guardar como 'Emitido'. Completa Expediente (SGD), Fecha de I.T y Número de I.T.")
                    st.stop()

            if submitted:
                nombre_ue = seleccion.split(" - ")[1].strip()
    
                nuevo = {
                    "codigo": codigo,
                    "nombre": nombre_ue,
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
    
                #st.session_state["nuevo_registro"] = nuevo
                #st.success("✔ Registro listo para guardar en Excel")
                try:
                    guardar_en_historial_excel(nuevo, HISTORIAL_PATH)
                    st.success("✅ Registro guardado en el historial.")
                    st.session_state["modo"] = "historial"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar en el Excel: {e}")

                st.write("📄 HISTORIAL_PATH:", HISTORIAL_PATH)
                st.write("📍 Ruta absoluta:", os.path.abspath(HISTORIAL_PATH))
                
                if os.path.exists(HISTORIAL_PATH):
                    st.write("✅ Existe en este entorno.")
                    st.write("🕒 Última modificación (mtime):", datetime.fromtimestamp(os.path.getmtime(HISTORIAL_PATH)))
                    st.write("📦 Tamaño (bytes):", os.path.getsize(HISTORIAL_PATH))
                else:
                    st.write("❌ No existe en este entorno.")
