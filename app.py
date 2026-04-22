import streamlit as st
import pandas as pd
import base64
import os

# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Dashboard Corporativo Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. ESTILOS / FONDO
# =========================================================
def set_bg(img_file):
    background_style = ""
    if os.path.exists(img_file):
        with open(img_file, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        ext = img_file.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
        background_style = f'background-image: url("data:{mime};base64,{b64_encoded}");'
    else:
        st.sidebar.warning(f"Imagen no encontrada: {img_file}")

    st.markdown(f"""
        <style>
        .stApp {{
            {background_style}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main-title {{
            text-align: center; color: black; font-weight: 900;
            font-size: 52px; margin-bottom: 6px;
        }}
        .sub-title {{
            text-align: center; font-weight: 700; font-size: 20px;
            color: #004a99; margin-bottom: 25px;
        }}
        .kpi-wrapper {{
            display: flex; flex-direction: column; align-items: center; margin-top: 20px;
        }}
        .box-header-dc {{
            background: linear-gradient(135deg, #0f4287, #2563eb); color: white;
            width: 320px; padding: 18px 22px; border-radius: 22px; text-align: center;
            font-weight: 900; font-size: 16px; margin-bottom: 18px;
            box-shadow: 0 18px 40px rgba(15,66,135,0.18);
            letter-spacing: 0.08em; text-transform: uppercase;
        }}
        .box-header-tt {{
            background: linear-gradient(135deg, #6d0b8c, #9333ea); color: white;
            width: 320px; padding: 18px 22px; border-radius: 22px; text-align: center;
            font-weight: 900; font-size: 16px; margin-bottom: 18px;
            box-shadow: 0 18px 40px rgba(109,11,140,0.18);
            letter-spacing: 0.08em; text-transform: uppercase;
        }}
        .data-card-dc {{
            background-color: rgba(255,255,255,0.96); width: 320px; padding: 24px;
            border-radius: 24px; border: 2px solid #0f4287; text-align: center;
            margin-bottom: 16px; box-shadow: 0 16px 40px rgba(0,0,0,0.08);
        }}
        .data-card-tt {{
            background-color: rgba(255,255,255,0.96); width: 320px; padding: 24px;
            border-radius: 24px; border: 2px solid #6d0b8c; text-align: center;
            margin-bottom: 16px; box-shadow: 0 16px 40px rgba(0,0,0,0.08);
        }}
        .label {{
            color: #4b5563; font-weight: 800; font-size: 13px; text-transform: uppercase;
            display: block; letter-spacing: 0.1em; margin-bottom: 8px;
        }}
        .value {{
            color: #111827; font-size: 42px; font-weight: 900;
            display: block; line-height: 1.05;
        }}
        .section-title-dc {{ color: #004a99; font-size: 38px; font-weight: 900; margin-bottom: 10px; }}
        .section-title-tt {{ color: #70008f; font-size: 38px; font-weight: 900; margin-bottom: 10px; }}
        .small-subtitle-dc {{ color: #004a99; font-weight: 800; font-size: 18px; margin-bottom: 10px; }}
        .small-subtitle-tt {{ color: #70008f; font-weight: 800; font-size: 18px; margin-bottom: 10px; }}
        .block-filter {{
            background-color: rgba(255,255,255,0.85); padding: 16px; border-radius: 16px;
            border: 1px solid #d9d9d9; margin-top: 20px; margin-bottom: 20px;
        }}
        .stExpander {{ border-radius: 12px !important; overflow: hidden; }}
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# 3. CONSTANTES
# =========================================================
DATA_DIR = "."

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}
MESES_MAP = {v.lower(): k for k, v in MESES_ES.items()}


# =========================================================
# 4. CARGA DE DATOS
# =========================================================
@st.cache_data
def cargar_csv(nombre_archivo):
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    encodings = ["latin-1", "utf-8-sig", "utf-8", "cp1252", "iso-8859-1"]
    separadores = [";", ",", "\t"]
    for enc in encodings:
        for sep in separadores:
            try:
                df = pd.read_csv(ruta, encoding=enc, sep=sep,
                                on_bad_lines="skip", engine="python")
                df.columns = df.columns.str.strip()
                if len(df.columns) > 1:
                    return df
            except FileNotFoundError:
                st.warning(f"Archivo no encontrado: {ruta}")
                return pd.DataFrame()
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
    st.error(f"No se pudo leer {nombre_archivo}")
    return pd.DataFrame()


def get_tabla_fija(nombre_tabla):
    mapa = {
        "dbo.CLARO_DC_FIJA":       "CLARO_DC_FIJA.csv",
        "dbo.CLARO_TELETALK_FIJA": "CLARO_TELETALK_FIJA.csv",
    }
    return cargar_csv(mapa.get(nombre_tabla, nombre_tabla + ".csv"))


def get_tabla_movil(nombre_tabla):
    """
    DC MOVIL y TELETALK MOVIL son CSVs (separador ;, encoding latin-1).
    FECHA CARGA está vacía en DC → usamos FECHA OPERACION para DC.
    TELETALK tiene ambas: FECHA OPERACION y FECHA CARGA.
    """
    mapa = {
        "dbo.CLARO_DC_MOVIL":       "CLARO_DC_MOVIL.csv",
        "dbo.CLARO_TELETALK_MOVIL": "CLARO_TELETALK_MOVIL.csv",
    }
    return cargar_csv(mapa.get(nombre_tabla, nombre_tabla + ".csv"))


def get_maestro(nombre_tabla):
    mapa = {
        "[DATA DEVELZ].dbo.FIJA_DC":       "FIJA_DC.csv",
        "[DATA DEVELZ].dbo.FIJA_TELETALK": "FIJA_TELETALK.csv",
    }
    return cargar_csv(mapa.get(nombre_tabla, nombre_tabla.split(".")[-1] + ".csv"))


def preparar_fechas_fija(df):
    for col in ["FECHA INSTALACION", "FECHA GENERACION"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    return df


def preparar_fechas_movil(df):
    """
    Soporta formatos mixtos:
    - 2025-12-02
    - 14/12/2025
    """
    for col in ["FECHA OPERACION", "FECHA CARGA"]:
        if col in df.columns:
            serie = df[col].astype(str).str.strip()

            es_iso = serie.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)
            es_lat = serie.str.match(r"^\d{1,2}/\d{1,2}/\d{4}$", na=False)

            fechas = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")

            if es_iso.any():
                fechas.loc[es_iso] = pd.to_datetime(
                    serie.loc[es_iso],
                    format="%Y-%m-%d",
                    errors="coerce"
                )

            if es_lat.any():
                fechas.loc[es_lat] = pd.to_datetime(
                    serie.loc[es_lat],
                    dayfirst=True,
                    errors="coerce"
                )

            otros = ~(es_iso | es_lat)
            if otros.any():
                fechas.loc[otros] = pd.to_datetime(
                    serie.loc[otros],
                    errors="coerce",
                    dayfirst=True
                )

            df[col] = fechas
    return df


def encontrar_columna(df, posibles):
    for n in posibles:
        if n in df.columns:
            return n
    return None


def obtener_comision_fija(df):
    col = encontrar_columna(df, ["COMISION", "COMISIÓN", "Comision", "Comisión",
                                "comision", "comisión", "COMIS", "MONTO"])
    if col:
        return pd.to_numeric(df[col], errors="coerce").fillna(0)
    return pd.Series([0.0] * len(df))


def obtener_comision_movil(df):
    col = encontrar_columna(df, ["COMISION TOTAL", "COMISIÓN TOTAL",
                                "Comision Total", "COMISION", "MONTO"])
    if col:
        return pd.to_numeric(df[col], errors="coerce").fillna(0)
    return pd.Series([0.0] * len(df))


# =========================================================
# 5. FUNCIONES AUXILIARES
# =========================================================
def formatear_moneda(valor):
    try:
        return f"S/ {float(valor):,.2f}"
    except:
        return "S/ 0.00"


def parse_mes_anio(fecha_texto):
    if not fecha_texto or fecha_texto == "Todos los meses":
        return None, None
    parts = fecha_texto.strip().lower().split()
    if len(parts) == 2 and parts[0] in MESES_MAP and parts[1].isdigit():
        return MESES_MAP[parts[0]], int(parts[1])
    return None, None


def filtrar_por_mes_anio(df, columna, fecha_texto):
    month_num, year = parse_mes_anio(fecha_texto)
    if month_num and year and columna in df.columns:
        return df[
            (df[columna].dt.month == month_num) &
            (df[columna].dt.year == year)
        ].copy()
    return df.copy()


def porta_si(serie):
    return serie.str.upper().str.strip().str.replace('Í', 'I', regex=False).isin(['SI', 'YES', 'Y'])


# =========================================================
# 6. OBTENER MESES DISPONIBLES
# =========================================================
@st.cache_data(ttl=300)
def obtener_meses_fija(columna):
    try:
        dfs = [
            preparar_fechas_fija(cargar_csv("CLARO_DC_FIJA.csv")),
            preparar_fechas_fija(cargar_csv("CLARO_TELETALK_FIJA.csv"))
        ]
        meses = set()
        for df in dfs:
            if columna in df.columns:
                for fecha in df[columna].dropna():
                    meses.add(f"{MESES_ES[fecha.month].capitalize()} {fecha.year}")
        if not meses:
            return ["Todos los meses"]
        return ["Todos los meses"] + sorted(meses,
            key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0)))
    except:
        return ["Todos los meses"]


@st.cache_data(ttl=300)
def obtener_meses_movil(columna, archivos):
    meses = set()
    for archivo in archivos:
        df = preparar_fechas_movil(cargar_csv(archivo))
        if columna in df.columns:
            df_valid = df[df[columna].notna()]
            for fecha in df_valid[columna]:
                etiqueta = f"{MESES_ES[fecha.month].lower()} {fecha.year}"
                meses.add(etiqueta.capitalize())

    if not meses:
        return ["Todos los meses"]

    return ["Todos los meses"] + sorted(
        meses,
        key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0))
    )


# =========================================================
# 7. FUNCIONES FIJA (con corrección drop_duplicates)
# =========================================================
@st.cache_data(ttl=300)
def obtener_metricas_fija(tabla, f_inst, f_gene):
    try:
        df = preparar_fechas_fija(get_tabla_fija(tabla))
        if df.empty:
            return 0, 0.0
        if f_inst != "Todos los meses":
            df = filtrar_por_mes_anio(df, "FECHA INSTALACION", f_inst)
        if f_gene != "Todos los meses":
            df = filtrar_por_mes_anio(df, "FECHA GENERACION", f_gene)
        ventas = df["SOT"].nunique() if "SOT" in df.columns else 0
        comision = obtener_comision_fija(df).sum()
        return int(ventas), float(comision)
    except:
        return 0, 0.0


@st.cache_data(ttl=300)
def obtener_reporte_liquidado(ventas_tabla, maestro_tabla, fecha_instalacion):
    cols_vacias = ["SOT", "ASESOR", "Nombre del Cliente", "COMISION", "COMISIONES", "¿Pagado?"]
    try:
        df_v = preparar_fechas_fija(get_tabla_fija(ventas_tabla))
        df_m = get_maestro(maestro_tabla)
        if df_v.empty:
            return pd.DataFrame(columns=cols_vacias)
        df_v = filtrar_por_mes_anio(df_v, "FECHA INSTALACION", fecha_instalacion)
        df_v["SOT"] = df_v["SOT"].astype(str).str.strip()
        if not df_m.empty and "Back Office - Sot" in df_m.columns:
            df_m["Back Office - Sot"] = df_m["Back Office - Sot"].astype(str).str.strip()
            df = df_v.merge(df_m, left_on="SOT", right_on="Back Office - Sot", how="left")
        else:
            df = df_v.copy()
        if "USUARIO" in df.columns:
            df["ASESOR"] = df["USUARIO"].replace("", pd.NA).fillna("Sin Asesor")
        else:
            df["ASESOR"] = "Sin Asesor"
        nom = df.get("Cliente - Nombre", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
        ape = df.get("Cliente - Apellido Paterno", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
        df["Nombre del Cliente"] = (nom + " " + ape).str.strip().replace("", "Sin Datos").fillna("Sin Datos")
        df["COMISION"] = obtener_comision_fija(df)
        df["¿Pagado?"] = df["COMISION"].apply(lambda x: "SÍ" if x > 0 else "NO")
        return df[cols_vacias]
    except Exception as e:
        st.error(f"Error reporte liquidado: {e}")
        return pd.DataFrame(columns=cols_vacias)


@st.cache_data(ttl=300)
def obtener_factor_instalacion_resumen(tabla, fecha_instalacion="Todos los meses"):
    cols_vacias = ["Año", "Mes", "Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."]
    try:
        df = preparar_fechas_fija(get_tabla_fija(tabla))
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)
        df = filtrar_por_mes_anio(df, "FECHA INSTALACION", fecha_instalacion)
        df["COMISION"] = obtener_comision_fija(df)
        df["_porta"] = porta_si(df.get("PORTABILIDAD", pd.Series([""] * len(df))).fillna("").astype(str))
        servicio = df.get("SERVICIO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        tipo = df.get("TIPO TRABAJO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        df["_ftth"] = servicio.str.contains("FTTH") | tipo.str.contains("FTTH")
        df["_hfc"]  = servicio.str.contains("HFC")  | tipo.str.contains("HFC")
        df["_anio"] = df["FECHA INSTALACION"].dt.year
        df["_mes"]  = df["FECHA INSTALACION"].dt.month

        df_sot = df.drop_duplicates(subset=["SOT", "_anio", "_mes"])
        grp = df_sot.groupby(["_anio", "_mes"]).agg(
            Ventas=("SOT", "nunique"),
            **{"PORTABILIDAD SI": ("_porta", "sum")},
            **{"PORTABILIDAD NO": ("_porta", lambda x: (~x).sum())},
            FTTH=("_ftth", "sum"),
            HFC=("_hfc", "sum"),
        ).reset_index()
        comision_grp = df.groupby(["_anio", "_mes"])["COMISION"].sum().reset_index()
        comision_grp.columns = ["_anio", "_mes", "S/."]
        grp = grp.merge(comision_grp, on=["_anio", "_mes"], how="left")
        grp.columns = ["Año", "MesNum", "Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum"])
        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor instalación: {e}")
        return pd.DataFrame(columns=cols_vacias)


@st.cache_data(ttl=300)
def obtener_factor_instalacion_detallado(tabla, fecha_instalacion="Todos los meses"):
    cols_vacias = ["Año", "Mes", "MesNum", "Dia", "Ventas", "Porta_SI", "Porta_NO", "FTTH", "HFC", "Monto"]
    try:
        df = preparar_fechas_fija(get_tabla_fija(tabla))
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)
        df = filtrar_por_mes_anio(df, "FECHA INSTALACION", fecha_instalacion)
        df["COMISION"] = obtener_comision_fija(df)
        df["_porta"] = porta_si(df.get("PORTABILIDAD", pd.Series([""] * len(df))).fillna("").astype(str))
        servicio = df.get("SERVICIO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        tipo = df.get("TIPO TRABAJO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        df["_ftth"] = servicio.str.contains("FTTH") | tipo.str.contains("FTTH")
        df["_hfc"]  = servicio.str.contains("HFC")  | tipo.str.contains("HFC")
        df["_anio"] = df["FECHA INSTALACION"].dt.year
        df["_mes"]  = df["FECHA INSTALACION"].dt.month
        df["_dia"]  = df["FECHA INSTALACION"].dt.day

        df_sot = df.drop_duplicates(subset=["SOT", "_anio", "_mes", "_dia"])
        grp = df_sot.groupby(["_anio", "_mes", "_dia"]).agg(
            Ventas=("SOT", "nunique"),
            Porta_SI=("_porta", "sum"),
            Porta_NO=("_porta", lambda x: (~x).sum()),
            FTTH=("_ftth", "sum"),
            HFC=("_hfc", "sum"),
        ).reset_index()
        monto_grp = df.groupby(["_anio", "_mes", "_dia"])["COMISION"].sum().reset_index()
        monto_grp.columns = ["_anio", "_mes", "_dia", "Monto"]
        grp = grp.merge(monto_grp, on=["_anio", "_mes", "_dia"], how="left")
        grp.columns = ["Año", "MesNum", "Dia", "Ventas", "Porta_SI", "Porta_NO", "FTTH", "HFC", "Monto"]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum", "Dia"], ascending=[False, False, True])
        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor instalación detallado: {e}")
        return pd.DataFrame(columns=cols_vacias)


@st.cache_data(ttl=300)
def obtener_factor_fecha_venta_resumen(tabla, fecha_generacion="Todos los meses"):
    cols_vacias = ["Año", "Mes", "Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."]
    try:
        df = preparar_fechas_fija(get_tabla_fija(tabla))
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)
        df = filtrar_por_mes_anio(df, "FECHA GENERACION", fecha_generacion)
        df["COMISION"] = obtener_comision_fija(df)
        df["_porta"] = porta_si(df.get("PORTABILIDAD", pd.Series([""] * len(df))).fillna("").astype(str))
        servicio = df.get("SERVICIO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        tipo = df.get("TIPO TRABAJO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        df["_ftth"] = servicio.str.contains("FTTH") | tipo.str.contains("FTTH")
        df["_hfc"]  = servicio.str.contains("HFC")  | tipo.str.contains("HFC")
        df["_anio"] = df["FECHA GENERACION"].dt.year
        df["_mes"]  = df["FECHA GENERACION"].dt.month

        df_sot = df.drop_duplicates(subset=["SOT", "_anio", "_mes"])
        grp = df_sot.groupby(["_anio", "_mes"]).agg(
            Ventas=("SOT", "nunique"),
            **{"PORTABILIDAD SI": ("_porta", "sum")},
            **{"PORTABILIDAD NO": ("_porta", lambda x: (~x).sum())},
            FTTH=("_ftth", "sum"),
            HFC=("_hfc", "sum"),
        ).reset_index()
        comision_grp = df.groupby(["_anio", "_mes"])["COMISION"].sum().reset_index()
        comision_grp.columns = ["_anio", "_mes", "S/."]
        grp = grp.merge(comision_grp, on=["_anio", "_mes"], how="left")
        grp.columns = ["Año", "MesNum", "Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum"])
        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor fecha venta: {e}")
        return pd.DataFrame(columns=cols_vacias)


@st.cache_data(ttl=300)
def obtener_factor_fecha_venta_detallado(tabla, fecha_generacion="Todos los meses"):
    cols_vacias = ["Año", "Mes", "MesNum", "Dia", "Ventas", "Porta_SI", "Porta_NO", "FTTH", "HFC", "Monto"]
    try:
        df = preparar_fechas_fija(get_tabla_fija(tabla))
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)
        df = filtrar_por_mes_anio(df, "FECHA GENERACION", fecha_generacion)
        df["COMISION"] = obtener_comision_fija(df)
        df["_porta"] = porta_si(df.get("PORTABILIDAD", pd.Series([""] * len(df))).fillna("").astype(str))
        servicio = df.get("SERVICIO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        tipo = df.get("TIPO TRABAJO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
        df["_ftth"] = servicio.str.contains("FTTH") | tipo.str.contains("FTTH")
        df["_hfc"]  = servicio.str.contains("HFC")  | tipo.str.contains("HFC")
        df["_anio"] = df["FECHA GENERACION"].dt.year
        df["_mes"]  = df["FECHA GENERACION"].dt.month
        df["_dia"]  = df["FECHA GENERACION"].dt.day

        df_sot = df.drop_duplicates(subset=["SOT", "_anio", "_mes", "_dia"])
        grp = df_sot.groupby(["_anio", "_mes", "_dia"]).agg(
            Ventas=("SOT", "nunique"),
            Porta_SI=("_porta", "sum"),
            Porta_NO=("_porta", lambda x: (~x).sum()),
            FTTH=("_ftth", "sum"),
            HFC=("_hfc", "sum"),
        ).reset_index()
        monto_grp = df.groupby(["_anio", "_mes", "_dia"])["COMISION"].sum().reset_index()
        monto_grp.columns = ["_anio", "_mes", "_dia", "Monto"]
        grp = grp.merge(monto_grp, on=["_anio", "_mes", "_dia"], how="left")
        grp.columns = ["Año", "MesNum", "Dia", "Ventas", "Porta_SI", "Porta_NO", "FTTH", "HFC", "Monto"]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum", "Dia"], ascending=[False, False, True])
        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor fecha venta detallado: {e}")
        return pd.DataFrame(columns=cols_vacias)


# =========================================================
# 8. FUNCIONES MÓVIL
# =========================================================
# Notas de estructura:
#   CLARO_DC_MOVIL.csv     → TRANSACCION: 'PORTABILIDAD' / 'ALTA NUEVA'
#                            FECHA CARGA: vacía → usar FECHA OPERACION para ambas vistas
#   CLARO_TELETALK_MOVIL.csv → TRANSACCION: 'PORTABILIDAD' / 'ALTA'
#                              FECHA OPERACION para Factor Instalación
#                              FECHA CARGA para Factor F. Venta
#   CF > 69.90  → columna CF
#   DIAS PORTADAS > 90 → columna DIAS PORTADAS
#   Comisión pagada → COMISION TOTAL

def _es_portabilidad_movil(serie):
    return serie.str.upper().str.strip().str.replace('Í','I',regex=False) == "PORTABILIDAD"

def _es_alta_movil(serie):
    s = serie.str.upper().str.strip().str.replace('Í','I',regex=False)
    return s.isin(["ALTA NUEVA", "ALTA"])


@st.cache_data(ttl=300)
def obtener_metricas_movil(tabla, filtro_fecha, col_fecha):
    """
    Retorna (ventas, portas, altas, comision_total)
    Ventas = recuento de filas del período filtrado.
    """
    try:
        df = preparar_fechas_movil(get_tabla_movil(tabla))
        if df.empty:
            return 0, 0, 0, 0.0

        df = filtrar_por_mes_anio(df, col_fecha, filtro_fecha)
        if df.empty:
            return 0, 0, 0, 0.0

        transaccion = df.get("TRANSACCION", pd.Series([""] * len(df), index=df.index)).fillna("").astype(str)
        ventas = int(len(df))
        portas = int(_es_portabilidad_movil(transaccion).sum())
        altas = int(_es_alta_movil(transaccion).sum())
        comision = obtener_comision_movil(df).sum()

        return ventas, portas, altas, float(comision)
    except Exception:
        return 0, 0, 0, 0.0

        df = filtrar_por_mes_anio(df, col_fecha, filtro_fecha)
        if df.empty:
            return 0, 0, 0, 0.0

        transaccion = df.get("TRANSACCION", pd.Series([""] * len(df))).fillna("").astype(str)
        ventas = int(len(df))
        portas = int(_es_portabilidad_movil(transaccion).sum())
        altas = int(_es_alta_movil(transaccion).sum())
        comision = obtener_comision_movil(df).sum()

        return ventas, portas, altas, float(comision)
    except Exception:
        return 0, 0, 0, 0.0
        df = filtrar_por_mes_anio(df, col_fecha, filtro_fecha)
        transaccion = df.get("TRANSACCION", pd.Series([""] * len(df))).fillna("").astype(str)
        portas = int(_es_portabilidad_movil(transaccion).sum())
        altas  = int(_es_alta_movil(transaccion).sum())
        total  = portas + altas
        comision = obtener_comision_movil(df).sum()
        return total, portas, altas, float(comision)
    except:
        return 0, 0, 0, 0.0


@st.cache_data(ttl=300)
def obtener_factor_movil_resumen(tabla, filtro_fecha, col_fecha):
    """
    Resumen agrupado por mes.
    Ventas = recuento real de filas.
    """
    cols_vacias = ["Año", "Mes", "Ventas", "PORTABILIDAD", "ALTA",
                "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90", "S/."]
    try:
        df = preparar_fechas_movil(get_tabla_movil(tabla))
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)

        df = filtrar_por_mes_anio(df, col_fecha, filtro_fecha)
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)

        df["_comision"] = obtener_comision_movil(df)
        transaccion = df.get("TRANSACCION", pd.Series([""] * len(df), index=df.index)).fillna("").astype(str)
        df["_porta"] = _es_portabilidad_movil(transaccion)
        df["_alta"] = _es_alta_movil(transaccion)

        cf_serie = pd.to_numeric(df.get("CF", pd.Series([0.0] * len(df), index=df.index)), errors="coerce").fillna(0)
        df["_cf_mayor"] = cf_serie > 69.90
        df["_cf_menor"] = cf_serie <= 69.90

        dias_serie = pd.to_numeric(df.get("DIAS PORTADAS", pd.Series([0.0] * len(df), index=df.index)), errors="coerce").fillna(0)
        df["_dias_mayor"] = dias_serie > 90
        df["_dias_menor"] = dias_serie <= 90

        df["_anio"] = df[col_fecha].dt.year.astype("Int64")
        df["_mes"] = df[col_fecha].dt.month.astype("Int64")

        grp = df.groupby(["_anio", "_mes"]).agg(
            Ventas=("TRANSACCION", "size"),
            PORTABILIDAD=("_porta", "sum"),
            ALTA=("_alta", "sum"),
            **{"CF>69.90": ("_cf_mayor", "sum")},
            **{"CF<=69.90": ("_cf_menor", "sum")},
            **{"Dias>90": ("_dias_mayor", "sum")},
            **{"Dias<=90": ("_dias_menor", "sum")},
            **{"S/.": ("_comision", "sum")},
        ).reset_index()

        grp.columns = ["Año", "MesNum", "Ventas", "PORTABILIDAD", "ALTA",
                    "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90", "S/."]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum"])

        cols_int = ["Año", "MesNum", "Ventas", "PORTABILIDAD", "ALTA", "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90"]
        for col in cols_int:
            grp[col] = pd.to_numeric(grp[col], errors="coerce").fillna(0).astype(int)

        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor móvil resumen: {e}")
        return pd.DataFrame(columns=cols_vacias)
        df = filtrar_por_mes_anio(df, col_fecha, filtro_fecha)
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)

        df["_comision"] = obtener_comision_movil(df)
        transaccion = df.get("TRANSACCION", pd.Series([""] * len(df))).fillna("").astype(str)
        df["_porta"] = _es_portabilidad_movil(transaccion)
        df["_alta"]  = _es_alta_movil(transaccion)

        cf_serie = pd.to_numeric(df.get("CF", pd.Series([0.0]*len(df))), errors="coerce").fillna(0)
        df["_cf_mayor"] = cf_serie > 69.90
        df["_cf_menor"] = cf_serie <= 69.90

        dias_serie = pd.to_numeric(df.get("DIAS PORTADAS", pd.Series([0.0]*len(df))), errors="coerce").fillna(0)
        df["_dias_mayor"] = dias_serie > 90
        df["_dias_menor"] = dias_serie <= 90

        df["_anio"] = df[col_fecha].dt.year
        df["_mes"]  = df[col_fecha].dt.month

        grp = df.groupby(["_anio", "_mes"]).agg(
            Ventas=("_porta", lambda x: len(x)),
            PORTABILIDAD=("_porta", "sum"),
            ALTA=("_alta", "sum"),
            **{"CF>69.90":  ("_cf_mayor", "sum")},
            **{"CF<=69.90": ("_cf_menor", "sum")},
            **{"Dias>90":   ("_dias_mayor", "sum")},
            **{"Dias<=90":  ("_dias_menor", "sum")},
            **{"S/.":       ("_comision", "sum")},
        ).reset_index()

        grp.columns = ["Año", "MesNum", "Ventas", "PORTABILIDAD", "ALTA",
                    "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90", "S/."]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum"])
        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor móvil resumen: {e}")
        return pd.DataFrame(columns=cols_vacias)


@st.cache_data(ttl=300)
def obtener_factor_movil_detallado(tabla, filtro_fecha, col_fecha):
    """
    Detalle diario agrupado solo por días con ventas.
    """
    cols_vacias = ["Año", "Mes", "MesNum", "Dia", "Ventas", "PORTABILIDAD", "ALTA",
                "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90", "Monto"]
    try:
        df = preparar_fechas_movil(get_tabla_movil(tabla))
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)

        df = filtrar_por_mes_anio(df, col_fecha, filtro_fecha)
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)

        df["_comision"] = obtener_comision_movil(df)
        transaccion = df.get("TRANSACCION", pd.Series([""] * len(df), index=df.index)).fillna("").astype(str)
        df["_porta"] = _es_portabilidad_movil(transaccion)
        df["_alta"] = _es_alta_movil(transaccion)

        cf_serie = pd.to_numeric(df.get("CF", pd.Series([0.0] * len(df), index=df.index)), errors="coerce").fillna(0)
        df["_cf_mayor"] = cf_serie > 69.90
        df["_cf_menor"] = cf_serie <= 69.90

        dias_serie = pd.to_numeric(df.get("DIAS PORTADAS", pd.Series([0.0] * len(df), index=df.index)), errors="coerce").fillna(0)
        df["_dias_mayor"] = dias_serie > 90
        df["_dias_menor"] = dias_serie <= 90

        df["_anio"] = df[col_fecha].dt.year.astype("Int64")
        df["_mes"] = df[col_fecha].dt.month.astype("Int64")
        df["_dia"] = df[col_fecha].dt.day.astype("Int64")

        grp = df.groupby(["_anio", "_mes", "_dia"]).agg(
            Ventas=("TRANSACCION", "size"),
            PORTABILIDAD=("_porta", "sum"),
            ALTA=("_alta", "sum"),
            **{"CF>69.90": ("_cf_mayor", "sum")},
            **{"CF<=69.90": ("_cf_menor", "sum")},
            **{"Dias>90": ("_dias_mayor", "sum")},
            **{"Dias<=90": ("_dias_menor", "sum")},
            Monto=("_comision", "sum"),
        ).reset_index()

        grp.columns = ["Año", "MesNum", "Dia", "Ventas", "PORTABILIDAD", "ALTA",
                    "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90", "Monto"]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum", "Dia"], ascending=[False, False, True])

        cols_int = ["Año", "MesNum", "Dia", "Ventas", "PORTABILIDAD", "ALTA", "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90"]
        for col in cols_int:
            grp[col] = pd.to_numeric(grp[col], errors="coerce").fillna(0).astype(int)

        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor móvil detallado: {e}")
        return pd.DataFrame(columns=cols_vacias)
        df = filtrar_por_mes_anio(df, col_fecha, filtro_fecha)
        if df.empty:
            return pd.DataFrame(columns=cols_vacias)

        df["_comision"] = obtener_comision_movil(df)
        transaccion = df.get("TRANSACCION", pd.Series([""] * len(df))).fillna("").astype(str)
        df["_porta"] = _es_portabilidad_movil(transaccion)
        df["_alta"]  = _es_alta_movil(transaccion)

        cf_serie = pd.to_numeric(df.get("CF", pd.Series([0.0]*len(df))), errors="coerce").fillna(0)
        df["_cf_mayor"] = cf_serie > 69.90
        df["_cf_menor"] = cf_serie <= 69.90

        dias_serie = pd.to_numeric(df.get("DIAS PORTADAS", pd.Series([0.0]*len(df))), errors="coerce").fillna(0)
        df["_dias_mayor"] = dias_serie > 90
        df["_dias_menor"] = dias_serie <= 90

        df["_anio"] = df[col_fecha].dt.year
        df["_mes"]  = df[col_fecha].dt.month
        df["_dia"]  = df[col_fecha].dt.day

        grp = df.groupby(["_anio", "_mes", "_dia"]).agg(
            Ventas=("_porta", lambda x: len(x)),
            PORTABILIDAD=("_porta", "sum"),
            ALTA=("_alta", "sum"),
            **{"CF>69.90":  ("_cf_mayor", "sum")},
            **{"CF<=69.90": ("_cf_menor", "sum")},
            **{"Dias>90":   ("_dias_mayor", "sum")},
            **{"Dias<=90":  ("_dias_menor", "sum")},
            Monto=("_comision", "sum"),
        ).reset_index()

        grp.columns = ["Año", "MesNum", "Dia", "Ventas", "PORTABILIDAD", "ALTA",
                    "CF>69.90", "CF<=69.90", "Dias>90", "Dias<=90", "Monto"]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        grp = grp.sort_values(["Año", "MesNum", "Dia"], ascending=[False, False, True])
        return grp[cols_vacias]
    except Exception as e:
        st.error(f"Error factor móvil detallado: {e}")
        return pd.DataFrame(columns=cols_vacias)


# =========================================================
# 9. FUNCIONES DE RANKING FIJA
# =========================================================
def construir_ranking_asesores(df_filtrado):
    if df_filtrado.empty:
        return pd.DataFrame(columns=["Rank","ASESOR","Cantidad_Ventas",
                                    "Ventas_Pagadas","Ventas_No_Pagadas","Total_Comision"])
    df_filtrado = df_filtrado.copy()
    comisiones_norm = (df_filtrado["COMISIONES"].astype(str)
                    .str.upper().str.replace('Í','I',regex=False).str.strip())
    df_filtrado["COMISIONES_NORMALIZADO"] = comisiones_norm
    ranking = (
        df_filtrado.groupby("ASESOR", dropna=False)
        .agg(
            Total_Comision=("COMISION", "sum"),
            Ventas_Pagadas=("SOT", lambda x: x[df_filtrado.loc[x.index,"COMISIONES_NORMALIZADO"]=="SI"].nunique()),
            Ventas_No_Pagadas=("SOT", lambda x: x[df_filtrado.loc[x.index,"COMISIONES_NORMALIZADO"]=="NO"].nunique())
        )
        .reset_index()
        .sort_values(by="Total_Comision", ascending=False)
    )
    ranking["Rank"] = ranking["Total_Comision"].rank(method="dense", ascending=False).astype(int)
    ranking["Cantidad_Ventas"] = ranking["Ventas_Pagadas"] + ranking["Ventas_No_Pagadas"]
    ranking = ranking[["Rank","ASESOR","Cantidad_Ventas","Ventas_Pagadas","Ventas_No_Pagadas","Total_Comision"]]
    total_row = pd.DataFrame([{
        "Rank": "Total", "ASESOR": "",
        "Cantidad_Ventas": ranking["Cantidad_Ventas"].sum(),
        "Ventas_Pagadas": ranking["Ventas_Pagadas"].sum(),
        "Ventas_No_Pagadas": ranking["Ventas_No_Pagadas"].sum(),
        "Total_Comision": ranking["Total_Comision"].sum()
    }])
    return pd.concat([ranking, total_row], ignore_index=True)


def mostrar_tabla_ranking(ranking_con_total):
    if ranking_con_total.empty:
        st.warning("No se encontraron datos para el ranking.")
        return
    ranking_style = (
        ranking_con_total.style
        .format({"Total_Comision": "S/ {:,.2f}"})
        .set_table_attributes('style="width:1000px; table-layout:fixed; background-color:white;"')
        .set_table_styles([
            {"selector":"th","props":[("text-align","center"),("font-size","14px"),("padding","8px"),("background-color","white")]},
            {"selector":"td","props":[("padding","8px"),("font-size","13px"),("white-space","nowrap"),("overflow","hidden"),("text-overflow","ellipsis"),("background-color","white")]},
        ])
        .set_properties(**{"text-align":"center"}, subset=["Rank","Cantidad_Ventas","Ventas_Pagadas","Ventas_No_Pagadas","Total_Comision"])
        .set_properties(**{"text-align":"left"}, subset=["ASESOR"])
    )
    st.table(ranking_style)


# =========================================================
# 10. HELPERS DE VISUALIZACIÓN
# =========================================================
def mostrar_expanders_fija(df_detalle, color="dc"):
    if df_detalle.empty:
        st.warning("No se encontraron datos para mostrar.")
        return
    periodos = (df_detalle[["Año","Mes","MesNum"]].drop_duplicates()
                .sort_values(by=["Año","MesNum"], ascending=[False,False]))
    for _, p in periodos.iterrows():
        datos_mes = df_detalle[
            (df_detalle["Año"]==p["Año"]) &
            (df_detalle["Mes"]==p["Mes"]) &
            (df_detalle["MesNum"]==p["MesNum"])
        ].copy()
        total_ventas = int(datos_mes["Ventas"].sum())
        total_monto  = float(datos_mes["Monto"].sum() or 0)
        icono = "🔵" if color == "dc" else "🟣"
        with st.expander(
            f"{icono} {p['Mes']} {p['Año']}  |  Ventas: {total_ventas}  |  Total: {formatear_moneda(total_monto)}",
            expanded=False
        ):
            df_tab = datos_mes[["Dia","Ventas","Porta_SI","Porta_NO","FTTH","HFC","Monto"]].copy()
            df_tab["Monto"] = df_tab["Monto"].map(formatear_moneda)
            st.table(df_tab)


def mostrar_expanders_movil(df_detalle, color="dc"):
    if df_detalle.empty:
        st.warning("No se encontraron datos para mostrar.")
        return
    periodos = (df_detalle[["Año","Mes","MesNum"]].drop_duplicates()
                .sort_values(by=["Año","MesNum"], ascending=[False,False]))
    for _, p in periodos.iterrows():
        datos_mes = df_detalle[
            (df_detalle["Año"]==p["Año"]) &
            (df_detalle["Mes"]==p["Mes"]) &
            (df_detalle["MesNum"]==p["MesNum"])
        ].copy()
        total_ventas = int(datos_mes["Ventas"].sum())
        total_monto  = float(datos_mes["Monto"].sum() or 0)
        icono = "🔵" if color == "dc" else "🟣"
        with st.expander(
            f"{icono} {p['Mes']} {p['Año']}  |  Ventas: {total_ventas}  |  Total: {formatear_moneda(total_monto)}",
            expanded=False
        ):
            df_tab = datos_mes[["Dia","Ventas","PORTABILIDAD","ALTA",
                                "CF>69.90","CF<=69.90","Dias>90","Dias<=90","Monto"]].copy()
            df_tab["Monto"] = df_tab["Monto"].map(formatear_moneda)
            st.table(df_tab)


def tabla_movil_resumen_style(df_display, color):
    header_color = "#0f4287" if color == "dc" else "#70008f"
    return (
        df_display.style
        .set_table_styles([
            {"selector":"th","props":[("background-color","white"),("color",header_color),
                                    ("font-size","13px"),("text-align","center"),("border-bottom","2px solid #ddd")]},
            {"selector":"td","props":[("padding","10px 8px"),("font-size","13px"),
                                    ("border-bottom","1px solid #eee"),("background-color","white")]},
        ])
        .set_properties(subset=["Año","Mes"], **{"text-align":"left"})
        .set_properties(subset=["Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","S/."],
                        **{"text-align":"center"})
    )


# =========================================================
# 11. RUTAS DE IMÁGENES
# =========================================================
ruta_base    = "."
img_caratula = os.path.join(ruta_base, "caratula.png.jpg")
img_dc       = os.path.join(ruta_base, "34bab75f-2b2e-455e-8935-377abf566b76.jpg")
img_tt       = os.path.join(ruta_base, "ab3ac40e-1612-430f-bb3a-817d24b709db.jpg")


# =========================================================
# 12. SIDEBAR / NAVEGACIÓN
# =========================================================
st.sidebar.title("MENU DE REPORTES")

st.sidebar.markdown("### 📡 FIJA")
opcion = st.sidebar.radio("", [
    "Inicio: Reporte Comparativo",
    "D&C Factor Instalación",
    "D&C Factor F. Venta",
    "D&C IAE ASESOR",
    "Teletalk Factor Instalación",
    "Teletalk Factor F. Venta",
    "Teletalk IAE ASESOR",
], key="radio_fija")

st.sidebar.markdown("### 📱 MÓVIL")
opcion_movil = st.sidebar.radio("", [
    "Inicio: Reporte Comparativo MOVIL",
    
    "D&C Factor F. Venta MOVIL",
    "D&C IAE ASESOR MOVIL",
    
    "Teletalk Factor F. Venta MOVIL",
    "Teletalk IAE ASESOR MOVIL",
], key="radio_movil")

# Determinar cuál radio fue seleccionado último
# Streamlit no tiene estado de "cuál fue el último", usamos session_state
if "ultima_seccion" not in st.session_state:
    st.session_state["ultima_seccion"] = "fija"

# Detectar cambio comparando con valores anteriores
prev_fija  = st.session_state.get("prev_fija",  opcion)
prev_movil = st.session_state.get("prev_movil", opcion_movil)

if opcion != prev_fija:
    st.session_state["ultima_seccion"] = "fija"
elif opcion_movil != prev_movil:
    st.session_state["ultima_seccion"] = "movil"

st.session_state["prev_fija"]  = opcion
st.session_state["prev_movil"] = opcion_movil

seccion = st.session_state["ultima_seccion"]

# Diagnóstico
with st.sidebar.expander("🔍 Ver columnas de CSVs"):
    for nombre in ["CLARO_DC_FIJA.csv","CLARO_TELETALK_FIJA.csv",
                "CLARO_DC_MOVIL.csv","CLARO_TELETALK_MOVIL.csv"]:
        df_test = cargar_csv(nombre)
        if not df_test.empty:
            st.write(f"**{nombre}:**")
            st.write(list(df_test.columns))
        else:
            st.write(f"**{nombre}:** ❌ no cargado")


# =========================================================
# 13. VISTAS FIJA
# =========================================================
if seccion == "fija":

    # ── INICIO FIJA ──────────────────────────────────────
    if opcion == "Inicio: Reporte Comparativo":
        set_bg(img_caratula)
        st.markdown('<div class="main-title">REPORTE COMPARATIVO</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-title">D&C DIGITAL GROUP <span style="color:black">vs</span> '
            '<span style="color:#70008f">TELETALK CONTACT CENTER</span></div>',
            unsafe_allow_html=True)

        col_dc, col_filtros, col_tt = st.columns([1, 1.2, 1])
        meses_inst = obtener_meses_fija("FECHA INSTALACION")
        meses_gene = obtener_meses_fija("FECHA GENERACION")

        with col_filtros:
            st.markdown('<div class="block-filter">', unsafe_allow_html=True)
            sel_inst = st.selectbox("FECHA INSTALACIÓN", meses_inst, key="fija_sel_inst")
            sel_gene = st.selectbox("FECHA DE VENTA",    meses_gene, key="fija_sel_gene")
            st.markdown('</div>', unsafe_allow_html=True)

        v_dc, c_dc = obtener_metricas_fija("dbo.CLARO_DC_FIJA",       sel_inst, sel_gene)
        v_tt, c_tt = obtener_metricas_fija("dbo.CLARO_TELETALK_FIJA", sel_inst, sel_gene)

        with col_dc:
            st.markdown(f"""
                <div class="kpi-wrapper">
                    <div class="box-header-dc">D&C DIGITAL GROUP</div>
                    <div class="data-card-dc">
                        <span class="label">Acumulado soles</span>
                        <span class="value">{formatear_moneda(c_dc)}</span>
                    </div>
                    <div class="data-card-dc">
                        <span class="label">Ventas totales</span>
                        <span class="value">{v_dc:,}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col_tt:
            st.markdown(f"""
                <div class="kpi-wrapper">
                    <div class="box-header-tt">TELETALK CONTACT CENTER</div>
                    <div class="data-card-tt">
                        <span class="label">Acumulado soles</span>
                        <span class="value">{formatear_moneda(c_tt)}</span>
                    </div>
                    <div class="data-card-tt">
                        <span class="label">Ventas totales</span>
                        <span class="value">{v_tt:,}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── D&C FACTOR INSTALACIÓN FIJA ──────────────────────
    elif opcion == "D&C Factor Instalación":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C Factor Instalación</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-dc">AVANCE DE FACTOR ANUAL POR FECHA DE INSTALACIÓN</div>', unsafe_allow_html=True)
        st.write("---")
        meses_inst = obtener_meses_fija("FECHA INSTALACION")
        filtro_inst = st.selectbox("Fecha de Instalación", meses_inst, key="dc_fi_inst")
        col1, col2 = st.columns([1.1, 1.6])
        with col1:
            st.markdown("### Resumen")
            df_f = obtener_factor_instalacion_resumen("dbo.CLARO_DC_FIJA", filtro_inst)
            if df_f.empty:
                st.warning("Sin datos.")
            else:
                total_row = pd.DataFrame([{"Año":"Total","Mes":"",
                    "Ventas":df_f["Ventas"].sum(),"PORTABILIDAD SI":df_f["PORTABILIDAD SI"].sum(),
                    "PORTABILIDAD NO":df_f["PORTABILIDAD NO"].sum(),"FTTH":df_f["FTTH"].sum(),
                    "HFC":df_f["HFC"].sum(),"S/.":df_f["S/."].sum()}])
                df_d = pd.concat([df_f, total_row], ignore_index=True)
                df_d["S/."] = df_d["S/."].map(formatear_moneda)
                st.table(df_d.style.set_table_styles([
                    {"selector":"th","props":[("background-color","white"),("color","#0f4287"),("font-size","13px"),("text-align","center"),("border-bottom","2px solid #ddd")]},
                    {"selector":"td","props":[("padding","10px 8px"),("font-size","13px"),("border-bottom","1px solid #eee"),("background-color","white")]},
                ]).set_properties(subset=["Año","Mes"],**{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."],**{"text-align":"center"}))
        with col2:
            st.markdown("### Detalle desplegable")
            mostrar_expanders_fija(obtener_factor_instalacion_detallado("dbo.CLARO_DC_FIJA", filtro_inst), color="dc")

    # ── D&C FACTOR F. VENTA FIJA ─────────────────────────
    elif opcion == "D&C Factor F. Venta":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C Factor F. Venta</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-dc">AVANCE DE FACTOR ANUAL POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        meses_gene = obtener_meses_fija("FECHA GENERACION")
        filtro_gene = st.selectbox("Fecha de Venta", meses_gene, key="dc_fv_gene")
        col1, col2 = st.columns([1.1, 1.6])
        with col1:
            st.markdown("### Resumen")
            df_f = obtener_factor_fecha_venta_resumen("dbo.CLARO_DC_FIJA", filtro_gene)
            if df_f.empty:
                st.warning("Sin datos.")
            else:
                total_row = pd.DataFrame([{"Año":"Total","Mes":"",
                    "Ventas":df_f["Ventas"].sum(),"PORTABILIDAD SI":df_f["PORTABILIDAD SI"].sum(),
                    "PORTABILIDAD NO":df_f["PORTABILIDAD NO"].sum(),"FTTH":df_f["FTTH"].sum(),
                    "HFC":df_f["HFC"].sum(),"S/.":df_f["S/."].sum()}])
                df_d = pd.concat([df_f, total_row], ignore_index=True)
                df_d["S/."] = df_d["S/."].map(formatear_moneda)
                st.table(df_d.style.set_table_styles([
                    {"selector":"th","props":[("background-color","white"),("color","#0f4287"),("font-size","13px"),("text-align","center"),("border-bottom","2px solid #ddd")]},
                    {"selector":"td","props":[("padding","10px 8px"),("font-size","13px"),("border-bottom","1px solid #eee"),("background-color","white")]},
                ]).set_properties(subset=["Año","Mes"],**{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."],**{"text-align":"center"}))
        with col2:
            st.markdown("### Detalle desplegable")
            mostrar_expanders_fija(obtener_factor_fecha_venta_detallado("dbo.CLARO_DC_FIJA", filtro_gene), color="dc")

    # ── D&C IAE ASESOR FIJA ───────────────────────────────
    elif opcion == "D&C IAE ASESOR":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C IAE ASESOR</div>', unsafe_allow_html=True)
        st.write("---")
        meses_inst = obtener_meses_fija("FECHA INSTALACION")
        filt_inst = st.selectbox("Fecha de Instalación", meses_inst, key="dc_iae_inst")
        df_liq = obtener_reporte_liquidado("dbo.CLARO_DC_FIJA","[DATA DEVELZ].dbo.FIJA_DC", filt_inst)
        if df_liq.empty:
            st.warning("Sin datos.")
        else:
            asesores = ["Todos"] + sorted(df_liq["ASESOR"].fillna("Sin Asesor").unique().tolist())
            filtro_asesor = st.selectbox("Selecciona Asesor", asesores, key="dc_iae_asesor")
            df_filtrado = df_liq[df_liq["ASESOR"]==filtro_asesor].copy() if filtro_asesor != "Todos" else df_liq.copy()
            st.markdown("### Ranking de Asesores")
            mostrar_tabla_ranking(construir_ranking_asesores(df_filtrado))

    # ── TELETALK FACTOR INSTALACIÓN FIJA ─────────────────
    elif opcion == "Teletalk Factor Instalación":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor Instalación</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE INSTALACIÓN</div>', unsafe_allow_html=True)
        st.write("---")
        meses_inst = obtener_meses_fija("FECHA INSTALACION")
        filtro_inst = st.selectbox("Fecha de Instalación", meses_inst, key="tt_fi_inst")
        col1, col2 = st.columns([1.1, 1.6])
        with col1:
            st.markdown("### Resumen")
            df_f = obtener_factor_instalacion_resumen("dbo.CLARO_TELETALK_FIJA", filtro_inst)
            if df_f.empty:
                st.warning("Sin datos.")
            else:
                total_row = pd.DataFrame([{"Año":"Total","Mes":"",
                    "Ventas":df_f["Ventas"].sum(),"PORTABILIDAD SI":df_f["PORTABILIDAD SI"].sum(),
                    "PORTABILIDAD NO":df_f["PORTABILIDAD NO"].sum(),"FTTH":df_f["FTTH"].sum(),
                    "HFC":df_f["HFC"].sum(),"S/.":df_f["S/."].sum()}])
                df_d = pd.concat([df_f, total_row], ignore_index=True)
                df_d["S/."] = df_d["S/."].map(formatear_moneda)
                st.table(df_d.style.set_table_styles([
                    {"selector":"th","props":[("background-color","white"),("color","#70008f"),("font-size","13px"),("text-align","center"),("border-bottom","2px solid #ddd")]},
                    {"selector":"td","props":[("padding","10px 8px"),("font-size","13px"),("border-bottom","1px solid #eee"),("background-color","white")]},
                ]).set_properties(subset=["Año","Mes"],**{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."],**{"text-align":"center"}))
        with col2:
            st.markdown("### Detalle desplegable")
            mostrar_expanders_fija(obtener_factor_instalacion_detallado("dbo.CLARO_TELETALK_FIJA", filtro_inst), color="tt")

    # ── TELETALK FACTOR F. VENTA FIJA ────────────────────
    elif opcion == "Teletalk Factor F. Venta":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor F. Venta</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        meses_gene = obtener_meses_fija("FECHA GENERACION")
        filtro_gene = st.selectbox("Fecha de Venta", meses_gene, key="tt_fv_gene")
        col1, col2 = st.columns([1.1, 1.6])
        with col1:
            st.markdown("### Resumen")
            df_f = obtener_factor_fecha_venta_resumen("dbo.CLARO_TELETALK_FIJA", filtro_gene)
            if df_f.empty:
                st.warning("Sin datos.")
            else:
                total_row = pd.DataFrame([{"Año":"Total","Mes":"",
                    "Ventas":df_f["Ventas"].sum(),"PORTABILIDAD SI":df_f["PORTABILIDAD SI"].sum(),
                    "PORTABILIDAD NO":df_f["PORTABILIDAD NO"].sum(),"FTTH":df_f["FTTH"].sum(),
                    "HFC":df_f["HFC"].sum(),"S/.":df_f["S/."].sum()}])
                df_d = pd.concat([df_f, total_row], ignore_index=True)
                df_d["S/."] = df_d["S/."].map(formatear_moneda)
                st.table(df_d.style.set_table_styles([
                    {"selector":"th","props":[("background-color","white"),("color","#70008f"),("font-size","13px"),("text-align","center"),("border-bottom","2px solid #ddd")]},
                    {"selector":"td","props":[("padding","10px 8px"),("font-size","13px"),("border-bottom","1px solid #eee"),("background-color","white")]},
                ]).set_properties(subset=["Año","Mes"],**{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."],**{"text-align":"center"}))
        with col2:
            st.markdown("### Detalle desplegable")
            mostrar_expanders_fija(obtener_factor_fecha_venta_detallado("dbo.CLARO_TELETALK_FIJA", filtro_gene), color="tt")

    # ── TELETALK IAE ASESOR FIJA ──────────────────────────
    elif opcion == "Teletalk IAE ASESOR":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk IAE ASESOR</div>', unsafe_allow_html=True)
        st.write("---")
        meses_inst = obtener_meses_fija("FECHA INSTALACION")
        filt_inst = st.selectbox("Fecha de Instalación", meses_inst, key="tt_iae_inst")
        df_liq = obtener_reporte_liquidado("dbo.CLARO_TELETALK_FIJA","[DATA DEVELZ].dbo.FIJA_TELETALK", filt_inst)
        if df_liq.empty:
            st.warning("Sin datos.")
        else:
            asesores = ["Todos"] + sorted(df_liq["ASESOR"].fillna("Sin Asesor").unique().tolist())
            filtro_asesor = st.selectbox("Selecciona Asesor", asesores, key="tt_iae_asesor")
            df_filtrado = df_liq[df_liq["ASESOR"]==filtro_asesor].copy() if filtro_asesor != "Todos" else df_liq.copy()
            st.markdown("### Ranking de Asesores")
            mostrar_tabla_ranking(construir_ranking_asesores(df_filtrado))


# =========================================================
# 14. VISTAS MÓVIL
# =========================================================
else:  # seccion == "movil"

    # ── INICIO MÓVIL ─────────────────────────────────────
    if opcion_movil == "Inicio: Reporte Comparativo MOVIL":
        set_bg(img_caratula)
        st.markdown('<div class="main-title">REPORTE COMPARATIVO MÓVIL</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-title">D&C DIGITAL GROUP <span style="color:black">vs</span> '
            '<span style="color:#70008f">TELETALK CONTACT CENTER</span></div>',
            unsafe_allow_html=True)

        meses_operacion_dc = obtener_meses_movil("FECHA OPERACION", ["CLARO_DC_MOVIL.csv"])
        meses_operacion_tt = obtener_meses_movil("FECHA OPERACION", ["CLARO_TELETALK_MOVIL.csv"])

        df_dc_tmp = preparar_fechas_movil(cargar_csv("CLARO_DC_MOVIL.csv"))
        if "FECHA CARGA" in df_dc_tmp.columns and df_dc_tmp["FECHA CARGA"].notna().any():
            meses_carga_dc = obtener_meses_movil("FECHA CARGA", ["CLARO_DC_MOVIL.csv"])
        else:
            meses_carga_dc = obtener_meses_movil("FECHA OPERACION", ["CLARO_DC_MOVIL.csv"])

        meses_carga_tt = obtener_meses_movil("FECHA CARGA", ["CLARO_TELETALK_MOVIL.csv"])

        todos_operacion = sorted(
            set(meses_operacion_dc + meses_operacion_tt) - {"Todos los meses"},
            key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0))
        )
        todos_carga = sorted(
            set(meses_carga_dc + meses_carga_tt) - {"Todos los meses"},
            key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0))
        )

        meses_operacion = ["Todos los meses"] + todos_operacion
        meses_carga = ["Todos los meses"] + todos_carga

        col_dc, col_filtros, col_tt = st.columns([1, 1.2, 1])
        with col_filtros:
            st.markdown('<div class="block-filter">', unsafe_allow_html=True)
            sel_operacion = st.selectbox("FECHA DE VENTA", meses_operacion, key="movil_comp_fecha_operacion")
            sel_carga = st.selectbox("FECHA DE ACTIVACION", meses_carga, key="movil_comp_fecha_carga")
            st.markdown('</div>', unsafe_allow_html=True)

        def aplicar_filtros_comparativo_movil(df, fecha_operacion, fecha_carga, respaldo_carga=False):
            df = preparar_fechas_movil(df.copy())

            if fecha_operacion != "Todos los meses" and "FECHA OPERACION" in df.columns:
                df = filtrar_por_mes_anio(df, "FECHA OPERACION", fecha_operacion)

            if fecha_carga != "Todos los meses":
                if "FECHA CARGA" in df.columns and df["FECHA CARGA"].notna().any():
                    df = filtrar_por_mes_anio(df, "FECHA CARGA", fecha_carga)
                elif respaldo_carga and "FECHA OPERACION" in df.columns:
                    df = filtrar_por_mes_anio(df, "FECHA OPERACION", fecha_carga)

            return df

        df_dc_cmp = aplicar_filtros_comparativo_movil(
            get_tabla_movil("dbo.CLARO_DC_MOVIL"),
            sel_operacion,
            sel_carga,
            respaldo_carga=True
        )
        df_tt_cmp = aplicar_filtros_comparativo_movil(
            get_tabla_movil("dbo.CLARO_TELETALK_MOVIL"),
            sel_operacion,
            sel_carga,
            respaldo_carga=False
        )

        trans_dc = df_dc_cmp.get("TRANSACCION", pd.Series([""] * len(df_dc_cmp))).fillna("").astype(str)
        p_dc = int(_es_portabilidad_movil(trans_dc).sum())
        a_dc = int(_es_alta_movil(trans_dc).sum())
        t_dc = p_dc + a_dc
        c_dc = float(obtener_comision_movil(df_dc_cmp).sum()) if not df_dc_cmp.empty else 0.0

        trans_tt = df_tt_cmp.get("TRANSACCION", pd.Series([""] * len(df_tt_cmp))).fillna("").astype(str)
        p_tt = int(_es_portabilidad_movil(trans_tt).sum())
        a_tt = int(_es_alta_movil(trans_tt).sum())
        t_tt = p_tt + a_tt
        c_tt = float(obtener_comision_movil(df_tt_cmp).sum()) if not df_tt_cmp.empty else 0.0

        with col_dc:
            st.markdown(f"""
                <div class="kpi-wrapper">
                    <div class="box-header-dc">D&C DIGITAL GROUP</div>
                    <div class="data-card-dc">
                        <span class="label">Comisión pagada</span>
                        <span class="value">{formatear_moneda(c_dc)}</span>
                    </div>
                    <div class="data-card-dc">
                        <span class="label">Total ventas</span>
                        <span class="value">{t_dc:,}</span>
                    </div>
                    <div class="data-card-dc">
                        <span class="label">Portabilidades</span>
                        <span class="value">{p_dc:,}</span>
                    </div>
                    <div class="data-card-dc">
                        <span class="label">Altas nuevas</span>
                        <span class="value">{a_dc:,}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col_tt:
            st.markdown(f"""
                <div class="kpi-wrapper">
                    <div class="box-header-tt">TELETALK CONTACT CENTER</div>
                    <div class="data-card-tt">
                        <span class="label">Comisión pagada</span>
                        <span class="value">{formatear_moneda(c_tt)}</span>
                    </div>
                    <div class="data-card-tt">
                        <span class="label">Total ventas</span>
                        <span class="value">{t_tt:,}</span>
                    </div>
                    <div class="data-card-tt">
                        <span class="label">Portabilidades</span>
                        <span class="value">{p_tt:,}</span>
                    </div>
                    <div class="data-card-tt">
                        <span class="label">Altas nuevas</span>
                        <span class="value">{a_tt:,}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── D&C FACTOR INSTALACIÓN MÓVIL ─────────────────────
    # DC no tiene FECHA CARGA → usa FECHA OPERACION en ambas vistas
    elif opcion_movil == "D&C Factor F. Venta MOVIL":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C Factor F. Venta MÓVIL</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-dc">AVANCE POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        meses = obtener_meses_movil("FECHA OPERACION", ["CLARO_DC_MOVIL.csv"])
        filtro = st.selectbox("Fecha de Venta", meses, key="dc_movil_fv")
        col1, col2 = st.columns([1.2, 1.6])
        with col1:
            st.markdown("### Resumen")
            df_r = obtener_factor_movil_resumen("dbo.CLARO_DC_MOVIL", filtro, "FECHA OPERACION")
            if df_r.empty:
                st.warning("Sin datos.")
            else:
                total_row = pd.DataFrame([{
                    "Año":"Total","Mes":"",
                    "Ventas":df_r["Ventas"].sum(),"PORTABILIDAD":df_r["PORTABILIDAD"].sum(),
                    "ALTA":df_r["ALTA"].sum(),"CF>69.90":df_r["CF>69.90"].sum(),
                    "CF<=69.90":df_r["CF<=69.90"].sum(),"Dias>90":df_r["Dias>90"].sum(),
                    "Dias<=90":df_r["Dias<=90"].sum(),"S/.":df_r["S/."].sum(),
                }])
                df_d = pd.concat([df_r, total_row], ignore_index=True)
                df_d["S/."] = df_d["S/."].map(formatear_moneda)
                st.table(tabla_movil_resumen_style(df_d, "dc"))
        with col2:
            st.markdown("### Detalle desplegable")
            mostrar_expanders_movil(
                obtener_factor_movil_detallado("dbo.CLARO_DC_MOVIL", filtro, "FECHA OPERACION"),
                color="dc")

    # ── D&C IAE ASESOR MÓVIL ─────────────────────────────
    elif opcion_movil == "D&C IAE ASESOR MOVIL":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C IAE ASESOR MÓVIL</div>', unsafe_allow_html=True)
        st.write("---")
        meses = obtener_meses_movil("FECHA OPERACION", ["CLARO_DC_MOVIL.csv"])
        filtro = st.selectbox("Fecha de Operación", meses, key="dc_movil_iae")

        df_m = preparar_fechas_movil(get_tabla_movil("dbo.CLARO_DC_MOVIL"))
        df_m = filtrar_por_mes_anio(df_m, "FECHA OPERACION", filtro)

        if df_m.empty:
            st.warning("Sin datos.")
        else:
            df_m["_comision"] = obtener_comision_movil(df_m)
            transaccion = df_m.get("TRANSACCION", pd.Series([""] * len(df_m))).fillna("").astype(str)
            df_m["_porta"] = _es_portabilidad_movil(transaccion)
            df_m["_alta"]  = _es_alta_movil(transaccion)

            col_asesor = encontrar_columna(df_m, ["USUARIO","ASESOR","VENDEDOR","DISTRIBUIDOR"])
            df_m["ASESOR"] = df_m[col_asesor].fillna("Sin Asesor") if col_asesor else "Sin Asesor"

            asesores = ["Todos"] + sorted(df_m["ASESOR"].unique().tolist())
            filtro_asesor = st.selectbox("Selecciona Asesor", asesores, key="dc_movil_iae_asesor")
            df_f = df_m[df_m["ASESOR"]==filtro_asesor].copy() if filtro_asesor != "Todos" else df_m.copy()

            st.markdown("### Ranking de Asesores")
            ranking = (
                df_f.groupby("ASESOR").agg(
                    Total_Ventas=("_porta", lambda x: len(x)),
                    Portabilidades=("_porta", "sum"),
                    Altas=("_alta", "sum"),
                    Comision_Total=("_comision", "sum"),
                ).reset_index()
                .sort_values("Comision_Total", ascending=False)
            )
            ranking["Rank"] = ranking["Comision_Total"].rank(method="dense", ascending=False).astype(int)
            ranking = ranking[["Rank","ASESOR","Total_Ventas","Portabilidades","Altas","Comision_Total"]]
            total_row = pd.DataFrame([{
                "Rank":"Total","ASESOR":"",
                "Total_Ventas":ranking["Total_Ventas"].sum(),
                "Portabilidades":ranking["Portabilidades"].sum(),
                "Altas":ranking["Altas"].sum(),
                "Comision_Total":ranking["Comision_Total"].sum(),
            }])
            ranking_final = pd.concat([ranking, total_row], ignore_index=True)
            st.table(ranking_final.style
                    .format({"Comision_Total": "S/ {:,.2f}"})
                    .set_properties(**{"text-align":"center"})
                    .set_properties(subset=["ASESOR"], **{"text-align":"left"}))

    # ── TELETALK FACTOR INSTALACIÓN MÓVIL ────────────────
    # Teletalk Factor Instalación → FECHA OPERACION
    elif opcion_movil == "Teletalk Factor F. Venta MOVIL":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor F. Venta MÓVIL</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        meses = obtener_meses_movil("FECHA OPERACION", ["CLARO_TELETALK_MOVIL.csv"])
        filtro = st.selectbox("Fecha de Venta", meses, key="tt_movil_fv")
        col1, col2 = st.columns([1.2, 1.6])
        with col1:
            st.markdown("### Resumen")
            df_r = obtener_factor_movil_resumen("dbo.CLARO_TELETALK_MOVIL", filtro, "FECHA OPERACION")
            if df_r.empty:
                st.warning("Sin datos.")
            else:
                total_row = pd.DataFrame([{
                    "Año":"Total","Mes":"",
                    "Ventas":df_r["Ventas"].sum(),"PORTABILIDAD":df_r["PORTABILIDAD"].sum(),
                    "ALTA":df_r["ALTA"].sum(),"CF>69.90":df_r["CF>69.90"].sum(),
                    "CF<=69.90":df_r["CF<=69.90"].sum(),"Dias>90":df_r["Dias>90"].sum(),
                    "Dias<=90":df_r["Dias<=90"].sum(),"S/.":df_r["S/."].sum(),
                }])
                df_d = pd.concat([df_r, total_row], ignore_index=True)
                df_d["S/."] = df_d["S/."].map(formatear_moneda)
                st.table(tabla_movil_resumen_style(df_d, "tt"))
        with col2:
            st.markdown("### Detalle desplegable")
            mostrar_expanders_movil(
                obtener_factor_movil_detallado("dbo.CLARO_TELETALK_MOVIL", filtro, "FECHA OPERACION"),
                color="tt")
    # ── TELETALK IAE ASESOR MÓVIL ─────────────────────────
    elif opcion_movil == "Teletalk IAE ASESOR MOVIL":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk IAE ASESOR MÓVIL</div>', unsafe_allow_html=True)
        st.write("---")
        meses = obtener_meses_movil("FECHA CARGA", ["CLARO_TELETALK_MOVIL.csv"])
        filtro = st.selectbox("Fecha de Carga", meses, key="tt_movil_iae")

        df_m = preparar_fechas_movil(get_tabla_movil("dbo.CLARO_TELETALK_MOVIL"))
        df_m = filtrar_por_mes_anio(df_m, "FECHA CARGA", filtro)

        if df_m.empty:
            st.warning("Sin datos.")
        else:
            df_m["_comision"] = obtener_comision_movil(df_m)
            transaccion = df_m.get("TRANSACCION", pd.Series([""] * len(df_m))).fillna("").astype(str)
            df_m["_porta"] = _es_portabilidad_movil(transaccion)
            df_m["_alta"]  = _es_alta_movil(transaccion)

            col_asesor = encontrar_columna(df_m, ["USUARIO","ASESOR","VENDEDOR","DISTRIBUIDOR"])
            df_m["ASESOR"] = df_m[col_asesor].fillna("Sin Asesor") if col_asesor else "Sin Asesor"

            asesores = ["Todos"] + sorted(df_m["ASESOR"].unique().tolist())
            filtro_asesor = st.selectbox("Selecciona Asesor", asesores, key="tt_movil_iae_asesor")
            df_f = df_m[df_m["ASESOR"]==filtro_asesor].copy() if filtro_asesor != "Todos" else df_m.copy()

            st.markdown("### Ranking de Asesores")
            ranking = (
                df_f.groupby("ASESOR").agg(
                    Total_Ventas=("_porta", lambda x: len(x)),
                    Portabilidades=("_porta", "sum"),
                    Altas=("_alta", "sum"),
                    Comision_Total=("_comision", "sum"),
                ).reset_index()
                .sort_values("Comision_Total", ascending=False)
            )
            ranking["Rank"] = ranking["Comision_Total"].rank(method="dense", ascending=False).astype(int)
            ranking = ranking[["Rank","ASESOR","Total_Ventas","Portabilidades","Altas","Comision_Total"]]
            total_row = pd.DataFrame([{
                "Rank":"Total","ASESOR":"",
                "Total_Ventas":ranking["Total_Ventas"].sum(),
                "Portabilidades":ranking["Portabilidades"].sum(),
                "Altas":ranking["Altas"].sum(),
                "Comision_Total":ranking["Comision_Total"].sum(),
            }])
            ranking_final = pd.concat([ranking, total_row], ignore_index=True)
            st.table(ranking_final.style
                    .format({"Comision_Total": "S/ {:,.2f}"})
                    .set_properties(**{"text-align":"center"})
                    .set_properties(subset=["ASESOR"], **{"text-align":"left"}))