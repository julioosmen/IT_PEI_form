# ============================================
# adapters/historial_sharepoint.py
# ============================================
import re
import pandas as pd

# SharePoint (historial_it_pei) -> Estándar interno de la app
MAP_HIST_SP_TO_STD = {
    # 🔑 Clave para filtrar historial (tu app la llama 'codigo')
    "Id_UE": "codigo",

    # Identificación / contexto
    "Año": "año",
    "Responsable Institucional": "responsable_institucional",

    # Flujo PEI
    "Fecha de recepción": "fecha_recepcion",
    "Periodo PEI": "periodo",
    "Vigencia": "vigencia",
    "Tipo de PEI": "tipo_pei",
    "Estado": "estado",
    "Cantidad de revisiones": "cantidad_revisiones",
    "Fecha de derivación": "fecha_derivacion",
    "Etapas de revisión": "etapa_revision",
    "Comentario adicional/ Emisor de I.T": "comentario",
    "Articulación": "articulacion",

    # Informe Técnico
    "Expediente": "expediente",
    "Fecha de I.T": "fecha_it",
    "Número de I.T": "numero_it",

    # Oficio
    "Fecha Oficio": "fecha_oficio",
    "Número Oficio": "numero_oficio",
}

def adaptar_historial_sharepoint(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte el DataFrame leído desde el Excel de SharePoint (historial_it_pei)
    a los nombres de columnas estándar que usa tu app (minúsculas con '_').

    - Tolera espacios al inicio/fin en encabezados
    - Colapsa espacios múltiples
    - Renombra según MAP_HIST_SP_TO_STD
    - Normaliza columnas a lower + underscores
    - Valida presencia de 'codigo'
    """
    df = df_raw.copy()

    # A) Normalizar encabezados originales (SharePoint puede traer espacios extra)
    def _norm_col(c: str) -> str:
        c = str(c)
        c = c.strip()
        c = re.sub(r"\s+", " ", c)  # colapsa espacios múltiples
        return c

    df.columns = [_norm_col(c) for c in df.columns]

    # B) Renombrar SharePoint -> estándar app
    df = df.rename(columns=MAP_HIST_SP_TO_STD)

    # C) Normalización final (convención interna)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # D) Validación mínima
    if "codigo" not in df.columns:
        raise ValueError(
            "Historial SharePoint inválido: falta columna clave 'codigo' "
            "(debe venir de 'Id_UE')."
        )

    return df
