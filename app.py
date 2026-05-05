import streamlit as st
import pandas as pd
import base64
import os
from io import BytesIO

# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(page_title="Dashboard Corporativo Pro", layout="wide", initial_sidebar_state="expanded")

# =========================================================
# 2. ESTILOS / FONDO
# =========================================================
def set_bg(img_file):
    bg = ""
    if os.path.exists(img_file):
        with open(img_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = img_file.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
        bg = f'background-image: url("data:{mime};base64,{b64}");'
    else:
        st.sidebar.warning(f"Imagen no encontrada: {img_file}")
    st.markdown(f"""<style>
        .stApp {{ {bg} background-size:cover; background-position:center; background-attachment:fixed; }}
        .main-title {{ text-align:center; color:black; font-weight:900; font-size:52px; margin-bottom:6px; }}
        .sub-title {{ text-align:center; font-weight:700; font-size:20px; color:#004a99; margin-bottom:25px; }}
        .kpi-wrapper {{ display:flex; flex-direction:column; align-items:center; margin-top:20px; }}
        .box-header-dc {{ background:linear-gradient(135deg,#0f4287,#2563eb); color:white; width:320px; padding:18px 22px; border-radius:22px; text-align:center; font-weight:900; font-size:16px; margin-bottom:18px; box-shadow:0 18px 40px rgba(15,66,135,.18); letter-spacing:.08em; text-transform:uppercase; }}
        .box-header-tt {{ background:linear-gradient(135deg,#6d0b8c,#9333ea); color:white; width:320px; padding:18px 22px; border-radius:22px; text-align:center; font-weight:900; font-size:16px; margin-bottom:18px; box-shadow:0 18px 40px rgba(109,11,140,.18); letter-spacing:.08em; text-transform:uppercase; }}
        .data-card-dc {{ background-color:rgba(255,255,255,.96); width:320px; padding:24px; border-radius:24px; border:2px solid #0f4287; text-align:center; margin-bottom:16px; box-shadow:0 16px 40px rgba(0,0,0,.08); }}
        .data-card-tt {{ background-color:rgba(255,255,255,.96); width:320px; padding:24px; border-radius:24px; border:2px solid #6d0b8c; text-align:center; margin-bottom:16px; box-shadow:0 16px 40px rgba(0,0,0,.08); }}
        .label {{ color:#4b5563; font-weight:800; font-size:13px; text-transform:uppercase; display:block; letter-spacing:.1em; margin-bottom:8px; }}
        .value {{ color:#111827; font-size:42px; font-weight:900; display:block; line-height:1.05; }}
        .section-title-dc {{ color:#004a99; font-size:38px; font-weight:900; margin-bottom:10px; }}
        .section-title-tt {{ color:#70008f; font-size:38px; font-weight:900; margin-bottom:10px; }}
        .small-subtitle-dc {{ color:#004a99; font-weight:800; font-size:18px; margin-bottom:10px; }}
        .small-subtitle-tt {{ color:#70008f; font-weight:800; font-size:18px; margin-bottom:10px; }}
        .block-filter {{ background-color:rgba(255,255,255,.85); padding:16px; border-radius:16px; border:1px solid #d9d9d9; margin-top:20px; margin-bottom:20px; }}
        .stExpander {{ border-radius:12px !important; overflow:hidden; }}
    </style>""", unsafe_allow_html=True)

# =========================================================
# 3. CONSTANTES
# =========================================================
DATA_DIR = "."
MESES_ES = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',
            7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}
MESES_MAP = {v.lower(): k for k, v in MESES_ES.items()}

CSV_MAP = {
    "dbo.CLARO_DC_FIJA":              "CLARO_DC_FIJA.csv",
    "dbo.CLARO_TELETALK_FIJA":        "CLARO_TELETALK_FIJA.csv",
    "dbo.CLARO_DC_MOVIL":             "CLARO_DC_MOVIL.csv",
    "dbo.CLARO_TELETALK_MOVIL":       "CLARO_TELETALK_MOVIL.csv",
    "[DATA DEVELZ].dbo.FIJA_DC":      "FIJA_DC.csv",
    "[DATA DEVELZ].dbo.FIJA_TELETALK":"FIJA_TELETALK.csv",
}

TIPIS_ESTADO_MAP = {
    "ATENDIDA/CONFORME":"Conforme","CONFORME PODIO":"Conforme","ATENDIDA - REASIGNACION":"Conforme",
    "CONFORME":"Conforme","ATENDIDA/OBSERVADO":"Conforme","AUDIO LOTEADO":"Conforme",
    "CONFORME - REASIGNACION":"Conforme","AUDIO KO":"1era Caída","SOT CON OTRO DAC":"1era Caída",
    "SEC SIN CORRECCIÓN":"1era Caída","SEC SIN CORRECCION":"1era Caída","OTROS":"1era Caída",
    "EDIFICIO NO LIBERADO PC":"1era Caída","SIN COBERTURA PC":"1era Caída","FICHA DUPLICADA":"1era Caída",
    "SEC CON EXCLUSIVIDAD":"1era Caída","NO ADJUNTA SUSTENTO":"1era Caída","NO ENVIA SUSTENTO":"1era Caída",
    "VENTA CARRUSEL":"1era Caída","DIRECCIÓN CON SERVICIO DE BAJA":"1era Caída",
    "DIRECCION CON SERVICIO DE BAJA":"1era Caída","FACILIDADES TECNICAS":"2da Caída",
    "CLIENTE NO DESEA":"2da Caída","FALTA CONTACTO":"2da Caída","CLIENTE NO CALIFICA":"2da Caída",
    "PRUEBA - CANCELADA":"2da Caída","DIRECCION INCORRECTA":"2da Caída","DIRECCIÓN INCORRECTA":"2da Caída",
    "MALA OFERTA":"2da Caída","RED SATURADA":"2da Caída","FRAUDE":"2da Caída","VIAJE O MUDANZA":"2da Caída",
    "CONTRA OFERTA":"2da Caída","FALTA INFRAESTRUCTURA":"2da Caída","EDIFICIO NO LIBERADO":"2da Caída",
    "EJECUCION - AUDIO LOTEADO":"Ejecución","EJECUCION - AUDIO CONFORME":"Ejecución",
    "PENDIENTE AUDIO OK":"Ejecución","EJECUCION":"Ejecución","EJECUCION - SIN AUDIO":"Ejecución",
    "PENDIENTE SOT":"Ejecución","PENDIENTE AUDIO KO":"Ejecución","EJECUCION - AUDIO OBSERVADO":"Ejecución",
    "PENDIENTE PRE - AUDITORIA":"Ejecución","EJECUCION - REASIGNACION":"Ejecución",
    "EJECUCION - AUDITADO":"Ejecución",
}

ruta_base    = "."
img_caratula = os.path.join(ruta_base, "caratula.png.jpg")
img_dc       = os.path.join(ruta_base, "34bab75f-2b2e-455e-8935-377abf566b76.jpg")
img_tt       = os.path.join(ruta_base, "ab3ac40e-1612-430f-bb3a-817d24b709db.jpg")

# =========================================================
# 4. CARGA DE DATOS
# =========================================================
@st.cache_data
def cargar_csv(nombre):
    ruta = os.path.join(DATA_DIR, nombre)
    for enc in ["latin-1","utf-8-sig","utf-8","cp1252","iso-8859-1"]:
        for sep in [";",",","\t"]:
            try:
                df = pd.read_csv(ruta, encoding=enc, sep=sep, on_bad_lines="skip", engine="python")
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
    st.error(f"No se pudo leer {nombre}")
    return pd.DataFrame()

def get_tabla(nombre):
    return cargar_csv(CSV_MAP.get(nombre, nombre.split(".")[-1] + ".csv"))

def preparar_fechas_fija(df):
    for col in ["FECHA INSTALACION", "FECHA GENERACION"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    return df

def preparar_fechas_movil(df):
    for col in ["FECHA OPERACION", "FECHA CARGA"]:
        if col not in df.columns:
            continue
        serie = df[col].astype(str).str.strip()
        es_iso = serie.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)
        es_lat = serie.str.match(r"^\d{1,2}/\d{1,2}/\d{4}$", na=False)
        fechas = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
        if es_iso.any(): fechas.loc[es_iso] = pd.to_datetime(serie.loc[es_iso], format="%Y-%m-%d", errors="coerce")
        if es_lat.any(): fechas.loc[es_lat] = pd.to_datetime(serie.loc[es_lat], dayfirst=True, errors="coerce")
        otros = ~(es_iso | es_lat)
        if otros.any(): fechas.loc[otros] = pd.to_datetime(serie.loc[otros], errors="coerce", dayfirst=True)
        df[col] = fechas
    return df

def encontrar_columna(df, posibles):
    return next((n for n in posibles if n in df.columns), None)

def obtener_comision_fija(df):
    col = encontrar_columna(df, ["COMISION","COMISIÓN","Comision","Comisión","comision","comisión","COMIS","MONTO"])
    return pd.to_numeric(df[col], errors="coerce").fillna(0) if col else pd.Series([0.0]*len(df))

def obtener_comision_movil(df):
    col = encontrar_columna(df, ["COMISION TOTAL","COMISIÓN TOTAL","Comision Total","COMISION","MONTO"])
    return pd.to_numeric(df[col], errors="coerce").fillna(0) if col else pd.Series([0.0]*len(df))

def formatear_moneda(v):
    try: return f"S/ {float(v):,.2f}"
    except: return "S/ 0.00"

def parse_mes_anio(txt):
    if not txt or txt == "Todos los meses": return None, None
    p = txt.strip().lower().split()
    if len(p) == 2 and p[0] in MESES_MAP and p[1].isdigit(): return MESES_MAP[p[0]], int(p[1])
    return None, None

def filtrar_por_mes_anio(df, col, txt):
    m, y = parse_mes_anio(txt)
    if m and y and col in df.columns:
        return df[(df[col].dt.month == m) & (df[col].dt.year == y)].copy()
    return df.copy()

def porta_si(serie):
    return serie.str.upper().str.strip().str.replace('Í','I',regex=False).isin(['SI','YES','Y'])

def _es_portabilidad_movil(serie):
    return serie.str.upper().str.strip().str.replace('Í','I',regex=False) == "PORTABILIDAD"

def _es_alta_movil(serie):
    return serie.str.upper().str.strip().str.replace('Í','I',regex=False).isin(["ALTA NUEVA","ALTA"])

# =========================================================
# 5. MESES DISPONIBLES
# =========================================================
@st.cache_data(ttl=300)
def obtener_meses_fija(col):
    meses = set()
    for nombre in ["CLARO_DC_FIJA.csv","CLARO_TELETALK_FIJA.csv"]:
        df = preparar_fechas_fija(cargar_csv(nombre))
        if col in df.columns:
            meses.update(f"{MESES_ES[f.month].capitalize()} {f.year}" for f in df[col].dropna())
    return (["Todos los meses"] +
            sorted(meses, key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0))))

@st.cache_data(ttl=300)
def obtener_meses_movil(col, archivos):
    meses = set()
    for a in archivos:
        df = preparar_fechas_movil(cargar_csv(a))
        if col in df.columns:
            meses.update(f"{MESES_ES[f.month].lower()} {f.year}".capitalize()
                         for f in df[df[col].notna()][col])
    return (["Todos los meses"] +
            sorted(meses, key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0))))

# =========================================================
# 6. MÉTRICAS Y REPORTES FIJA
# =========================================================
@st.cache_data(ttl=300)
def obtener_metricas_fija(tabla, f_inst, f_gene):
    try:
        df = preparar_fechas_fija(get_tabla(tabla))
        if df.empty: return 0, 0.0
        if f_inst != "Todos los meses": df = filtrar_por_mes_anio(df, "FECHA INSTALACION", f_inst)
        if f_gene != "Todos los meses": df = filtrar_por_mes_anio(df, "FECHA GENERACION", f_gene)
        return int(df["SOT"].nunique() if "SOT" in df.columns else 0), float(obtener_comision_fija(df).sum())
    except: return 0, 0.0

@st.cache_data(ttl=300)
def obtener_reporte_liquidado(ventas_tabla, maestro_tabla, fecha_inst):
    cols = ["SOT","ASESOR","Nombre del Cliente","COMISION","COMISIONES","¿Pagado?"]
    try:
        df_v = preparar_fechas_fija(get_tabla(ventas_tabla))
        df_m = get_tabla(maestro_tabla)
        if df_v.empty: return pd.DataFrame(columns=cols)
        df_v = filtrar_por_mes_anio(df_v, "FECHA INSTALACION", fecha_inst)
        df_v["SOT"] = df_v["SOT"].astype(str).str.strip()
        if not df_m.empty and "Back Office - Sot" in df_m.columns:
            df_m["Back Office - Sot"] = df_m["Back Office - Sot"].astype(str).str.strip()
            df = df_v.merge(df_m, left_on="SOT", right_on="Back Office - Sot", how="left")
        else:
            df = df_v.copy()
        df["ASESOR"] = df.get("USUARIO", pd.Series([""] * len(df))).replace("", pd.NA).fillna("Sin Asesor")
        nom = df.get("Cliente - Nombre", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
        ape = df.get("Cliente - Apellido Paterno", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
        df["Nombre del Cliente"] = (nom + " " + ape).str.strip().replace("", "Sin Datos").fillna("Sin Datos")
        df["COMISION"] = obtener_comision_fija(df)
        df["¿Pagado?"] = df["COMISION"].apply(lambda x: "SÍ" if x > 0 else "NO")
        return df[cols]
    except Exception as e:
        st.error(f"Error reporte liquidado: {e}")
        return pd.DataFrame(columns=cols)

# =========================================================
# 7. FACTOR FIJA
# =========================================================
def _base_factor_fija(df, col_fecha):
    df["COMISION"] = obtener_comision_fija(df)
    df["_porta"] = porta_si(df.get("PORTABILIDAD", pd.Series([""] * len(df))).fillna("").astype(str))
    srv = df.get("SERVICIO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
    tip = df.get("TIPO TRABAJO", pd.Series([""] * len(df))).fillna("").astype(str).str.upper()
    df["_ftth"] = srv.str.contains("FTTH") | tip.str.contains("FTTH")
    df["_hfc"]  = srv.str.contains("HFC")  | tip.str.contains("HFC")
    df["_anio"] = df[col_fecha].dt.year
    df["_mes"]  = df[col_fecha].dt.month
    return df

@st.cache_data(ttl=300)
def obtener_factor_fija_resumen(tabla, col_fecha, filtro):
    cols = ["Año","Mes","Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."]
    try:
        df = preparar_fechas_fija(get_tabla(tabla))
        if df.empty: return pd.DataFrame(columns=cols)
        df = filtrar_por_mes_anio(df, col_fecha, filtro)
        df = _base_factor_fija(df, col_fecha)
        ds = df.drop_duplicates(subset=["SOT","_anio","_mes"])
        grp = ds.groupby(["_anio","_mes"]).agg(
            Ventas=("SOT","nunique"), **{"PORTABILIDAD SI":("_porta","sum")},
            **{"PORTABILIDAD NO":("_porta", lambda x: (~x).sum())},
            FTTH=("_ftth","sum"), HFC=("_hfc","sum"),
        ).reset_index()
        com = df.groupby(["_anio","_mes"])["COMISION"].sum().reset_index()
        com.columns = ["_anio","_mes","S/."]
        grp = grp.merge(com, on=["_anio","_mes"], how="left")
        grp.columns = ["Año","MesNum","Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        return grp.sort_values(["Año","MesNum"])[cols]
    except Exception as e:
        st.error(f"Error factor fija resumen: {e}")
        return pd.DataFrame(columns=cols)

@st.cache_data(ttl=300)
def obtener_factor_fija_detallado(tabla, col_fecha, filtro):
    cols = ["Año","Mes","MesNum","Dia","Ventas","Porta_SI","Porta_NO","FTTH","HFC","Monto"]
    try:
        df = preparar_fechas_fija(get_tabla(tabla))
        if df.empty: return pd.DataFrame(columns=cols)
        df = filtrar_por_mes_anio(df, col_fecha, filtro)
        df = _base_factor_fija(df, col_fecha)
        df["_dia"] = df[col_fecha].dt.day
        ds = df.drop_duplicates(subset=["SOT","_anio","_mes","_dia"])
        grp = ds.groupby(["_anio","_mes","_dia"]).agg(
            Ventas=("SOT","nunique"), Porta_SI=("_porta","sum"),
            Porta_NO=("_porta", lambda x: (~x).sum()), FTTH=("_ftth","sum"), HFC=("_hfc","sum"),
        ).reset_index()
        com = df.groupby(["_anio","_mes","_dia"])["COMISION"].sum().reset_index()
        com.columns = ["_anio","_mes","_dia","Monto"]
        grp = grp.merge(com, on=["_anio","_mes","_dia"], how="left")
        grp.columns = ["Año","MesNum","Dia","Ventas","Porta_SI","Porta_NO","FTTH","HFC","Monto"]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        return grp.sort_values(["Año","MesNum","Dia"], ascending=[False,False,True])[cols]
    except Exception as e:
        st.error(f"Error factor fija detallado: {e}")
        return pd.DataFrame(columns=cols)

# =========================================================
# 8. FACTOR MÓVIL
# =========================================================
def _base_factor_movil(df, col_fecha):
    df["_comision"] = obtener_comision_movil(df)
    tr = df.get("TRANSACCION", pd.Series([""] * len(df), index=df.index)).fillna("").astype(str)
    df["_porta"] = _es_portabilidad_movil(tr)
    df["_alta"]  = _es_alta_movil(tr)
    cf   = pd.to_numeric(df.get("CF",   pd.Series([0.0]*len(df), index=df.index)), errors="coerce").fillna(0)
    dias = pd.to_numeric(df.get("DIAS PORTADAS", pd.Series([0.0]*len(df), index=df.index)), errors="coerce").fillna(0)
    df["_cf_mayor"]   = cf > 69.90;   df["_cf_menor"]   = cf <= 69.90
    df["_dias_mayor"] = dias > 90;    df["_dias_menor"]  = dias <= 90
    df["_anio"] = df[col_fecha].dt.year.astype("Int64")
    df["_mes"]  = df[col_fecha].dt.month.astype("Int64")
    return df

@st.cache_data(ttl=300)
def obtener_factor_movil_resumen(tabla, filtro, col_fecha):
    cols = ["Año","Mes","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","S/."]
    try:
        df = preparar_fechas_movil(get_tabla(tabla))
        if df.empty: return pd.DataFrame(columns=cols)
        df = filtrar_por_mes_anio(df, col_fecha, filtro)
        if df.empty: return pd.DataFrame(columns=cols)
        df = _base_factor_movil(df, col_fecha)
        grp = df.groupby(["_anio","_mes"]).agg(
            Ventas=("TRANSACCION","size"), PORTABILIDAD=("_porta","sum"), ALTA=("_alta","sum"),
            **{"CF>69.90":("_cf_mayor","sum")}, **{"CF<=69.90":("_cf_menor","sum")},
            **{"Dias>90":("_dias_mayor","sum")}, **{"Dias<=90":("_dias_menor","sum")},
            **{"S/.":("_comision","sum")},
        ).reset_index()
        grp.columns = ["Año","MesNum","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","S/."]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        int_cols = ["Año","MesNum","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90"]
        for c in int_cols: grp[c] = pd.to_numeric(grp[c], errors="coerce").fillna(0).astype(int)
        return grp.sort_values(["Año","MesNum"])[cols]
    except Exception as e:
        st.error(f"Error factor móvil resumen: {e}")
        return pd.DataFrame(columns=cols)

@st.cache_data(ttl=300)
def obtener_factor_movil_detallado(tabla, filtro, col_fecha):
    cols = ["Año","Mes","MesNum","Dia","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","Monto"]
    try:
        df = preparar_fechas_movil(get_tabla(tabla))
        if df.empty: return pd.DataFrame(columns=cols)
        df = filtrar_por_mes_anio(df, col_fecha, filtro)
        if df.empty: return pd.DataFrame(columns=cols)
        df = _base_factor_movil(df, col_fecha)
        df["_dia"] = df[col_fecha].dt.day.astype("Int64")
        grp = df.groupby(["_anio","_mes","_dia"]).agg(
            Ventas=("TRANSACCION","size"), PORTABILIDAD=("_porta","sum"), ALTA=("_alta","sum"),
            **{"CF>69.90":("_cf_mayor","sum")}, **{"CF<=69.90":("_cf_menor","sum")},
            **{"Dias>90":("_dias_mayor","sum")}, **{"Dias<=90":("_dias_menor","sum")},
            Monto=("_comision","sum"),
        ).reset_index()
        grp.columns = ["Año","MesNum","Dia","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","Monto"]
        grp["Mes"] = grp["MesNum"].map(MESES_ES)
        int_cols = ["Año","MesNum","Dia","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90"]
        for c in int_cols: grp[c] = pd.to_numeric(grp[c], errors="coerce").fillna(0).astype(int)
        return grp.sort_values(["Año","MesNum","Dia"], ascending=[False,False,True])[cols]
    except Exception as e:
        st.error(f"Error factor móvil detallado: {e}")
        return pd.DataFrame(columns=cols)

# =========================================================
# 9. RANKING / VISUALIZACIÓN
# =========================================================
def construir_ranking_asesores(df):
    if df.empty:
        return pd.DataFrame(columns=["Rank","ASESOR","Cantidad_Ventas","Ventas_Pagadas","Ventas_No_Pagadas","Total_Comision"])
    df = df.copy()
    cn = df["COMISIONES"].astype(str).str.upper().str.replace('Í','I',regex=False).str.strip()
    df["_cn"] = cn
    r = (df.groupby("ASESOR", dropna=False).agg(
        Total_Comision=("COMISION","sum"),
        Ventas_Pagadas=("SOT", lambda x: x[df.loc[x.index,"_cn"] == "SI"].nunique()),
        Ventas_No_Pagadas=("SOT", lambda x: x[df.loc[x.index,"_cn"] == "NO"].nunique()),
    ).reset_index().sort_values("Total_Comision", ascending=False))
    r["Rank"] = r["Total_Comision"].rank(method="dense", ascending=False).astype(int)
    r["Cantidad_Ventas"] = r["Ventas_Pagadas"] + r["Ventas_No_Pagadas"]
    r = r[["Rank","ASESOR","Cantidad_Ventas","Ventas_Pagadas","Ventas_No_Pagadas","Total_Comision"]]
    total = pd.DataFrame([{"Rank":"Total","ASESOR":"","Cantidad_Ventas":r["Cantidad_Ventas"].sum(),
        "Ventas_Pagadas":r["Ventas_Pagadas"].sum(),"Ventas_No_Pagadas":r["Ventas_No_Pagadas"].sum(),
        "Total_Comision":r["Total_Comision"].sum()}])
    return pd.concat([r, total], ignore_index=True)

def mostrar_tabla_ranking(ranking):
    if ranking.empty: st.warning("No se encontraron datos para el ranking."); return
    st.table(ranking.style.format({"Total_Comision":"S/ {:,.2f}"})
        .set_table_attributes('style="width:1000px;table-layout:fixed;background-color:white;"')
        .set_table_styles([
            {"selector":"th","props":[("text-align","center"),("font-size","14px"),("padding","8px"),("background-color","white")]},
            {"selector":"td","props":[("padding","8px"),("font-size","13px"),("white-space","nowrap"),("overflow","hidden"),("text-overflow","ellipsis"),("background-color","white")]},
        ])
        .set_properties(**{"text-align":"center"}, subset=["Rank","Cantidad_Ventas","Ventas_Pagadas","Ventas_No_Pagadas","Total_Comision"])
        .set_properties(**{"text-align":"left"}, subset=["ASESOR"]))

def _style_tabla(color):
    hc = "#0f4287" if color == "dc" else "#70008f"
    return [
        {"selector":"th","props":[("background-color","white"),("color",hc),("font-size","13px"),("text-align","center"),("border-bottom","2px solid #ddd")]},
        {"selector":"td","props":[("padding","10px 8px"),("font-size","13px"),("border-bottom","1px solid #eee"),("background-color","white")]}
    ]

def mostrar_expanders_fija(df_det, color="dc"):
    if df_det.empty: st.warning("No se encontraron datos."); return
    icono = "🔵" if color == "dc" else "🟣"
    for _, p in (df_det[["Año","Mes","MesNum"]].drop_duplicates()
                 .sort_values(["Año","MesNum"], ascending=[False,False])).iterrows():
        dm = df_det[(df_det["Año"] == p["Año"]) & (df_det["Mes"] == p["Mes"])].copy()
        with st.expander(f"{icono} {p['Mes']} {p['Año']}  |  Ventas: {int(dm['Ventas'].sum())}  |  Total: {formatear_moneda(dm['Monto'].sum())}", expanded=False):
            t = dm[["Dia","Ventas","Porta_SI","Porta_NO","FTTH","HFC","Monto"]].copy()
            t["Monto"] = t["Monto"].map(formatear_moneda)
            st.table(t)

def mostrar_expanders_movil(df_det, color="dc"):
    if df_det.empty: st.warning("No se encontraron datos."); return
    icono = "🔵" if color == "dc" else "🟣"
    for _, p in (df_det[["Año","Mes","MesNum"]].drop_duplicates()
                 .sort_values(["Año","MesNum"], ascending=[False,False])).iterrows():
        dm = df_det[(df_det["Año"] == p["Año"]) & (df_det["Mes"] == p["Mes"])].copy()
        with st.expander(f"{icono} {p['Mes']} {p['Año']}  |  Ventas: {int(dm['Ventas'].sum())}  |  Total: {formatear_moneda(dm['Monto'].sum())}", expanded=False):
            t = dm[["Dia","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","Monto"]].copy()
            t["Monto"] = t["Monto"].map(formatear_moneda)
            st.table(t)

def mostrar_factor_fija(tabla, col_fecha, filtro, color):
    col1, col2 = st.columns([1.1, 1.6])
    with col1:
        st.markdown("### Resumen")
        df_f = obtener_factor_fija_resumen(tabla, col_fecha, filtro)
        if df_f.empty: st.warning("Sin datos.")
        else:
            total = pd.DataFrame([{"Año":"Total","Mes":"","Ventas":df_f["Ventas"].sum(),
                "PORTABILIDAD SI":df_f["PORTABILIDAD SI"].sum(),"PORTABILIDAD NO":df_f["PORTABILIDAD NO"].sum(),
                "FTTH":df_f["FTTH"].sum(),"HFC":df_f["HFC"].sum(),"S/.":df_f["S/."].sum()}])
            d = pd.concat([df_f, total], ignore_index=True)
            d["S/."] = d["S/."].map(formatear_moneda)
            st.table(d.style.set_table_styles(_style_tabla(color))
                .set_properties(subset=["Año","Mes"], **{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."], **{"text-align":"center"}))
    with col2:
        st.markdown("### Detalle desplegable")
        mostrar_expanders_fija(obtener_factor_fija_detallado(tabla, col_fecha, filtro), color=color)

def mostrar_factor_movil(tabla, col_fecha, filtro, color):
    col1, col2 = st.columns([1.2, 1.6])
    with col1:
        st.markdown("### Resumen")
        df_r = obtener_factor_movil_resumen(tabla, filtro, col_fecha)
        if df_r.empty: st.warning("Sin datos.")
        else:
            total = pd.DataFrame([{"Año":"Total","Mes":"","Ventas":df_r["Ventas"].sum(),
                "PORTABILIDAD":df_r["PORTABILIDAD"].sum(),"ALTA":df_r["ALTA"].sum(),
                "CF>69.90":df_r["CF>69.90"].sum(),"CF<=69.90":df_r["CF<=69.90"].sum(),
                "Dias>90":df_r["Dias>90"].sum(),"Dias<=90":df_r["Dias<=90"].sum(),"S/.":df_r["S/."].sum()}])
            d = pd.concat([df_r, total], ignore_index=True)
            d["S/."] = d["S/."].map(formatear_moneda)
            st.table(d.style.set_table_styles(_style_tabla(color))
                .set_properties(subset=["Año","Mes"], **{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","S/."], **{"text-align":"center"}))
    with col2:
        st.markdown("### Detalle desplegable")
        mostrar_expanders_movil(obtener_factor_movil_detallado(tabla, filtro, col_fecha), color=color)

def mostrar_iae_movil(tabla, col_fecha, filtro, key_asesor, color):
    df_m = preparar_fechas_movil(get_tabla(tabla))
    df_m = filtrar_por_mes_anio(df_m, col_fecha, filtro)
    if df_m.empty: st.warning("Sin datos."); return
    df_m["_comision"] = obtener_comision_movil(df_m)
    tr = df_m.get("TRANSACCION", pd.Series([""] * len(df_m))).fillna("").astype(str)
    df_m["_porta"] = _es_portabilidad_movil(tr)
    df_m["_alta"]  = _es_alta_movil(tr)
    col_a = encontrar_columna(df_m, ["USUARIO","ASESOR","VENDEDOR","DISTRIBUIDOR"])
    df_m["ASESOR"] = df_m[col_a].fillna("Sin Asesor") if col_a else "Sin Asesor"
    filtro_a = st.selectbox("Selecciona Asesor", ["Todos"] + sorted(df_m["ASESOR"].unique().tolist()), key=key_asesor)
    df_f = df_m[df_m["ASESOR"] == filtro_a].copy() if filtro_a != "Todos" else df_m.copy()
    st.markdown("### Ranking de Asesores")
    r = (df_f.groupby("ASESOR").agg(
        Total_Ventas=("_porta", lambda x: len(x)), Portabilidades=("_porta","sum"),
        Altas=("_alta","sum"), Comision_Total=("_comision","sum"),
    ).reset_index().sort_values("Comision_Total", ascending=False))
    r["Rank"] = r["Comision_Total"].rank(method="dense", ascending=False).astype(int)
    r = r[["Rank","ASESOR","Total_Ventas","Portabilidades","Altas","Comision_Total"]]
    total = pd.DataFrame([{"Rank":"Total","ASESOR":"","Total_Ventas":r["Total_Ventas"].sum(),
        "Portabilidades":r["Portabilidades"].sum(),"Altas":r["Altas"].sum(),"Comision_Total":r["Comision_Total"].sum()}])
    st.table(pd.concat([r, total], ignore_index=True).style.format({"Comision_Total":"S/ {:,.2f}"})
        .set_properties(**{"text-align":"center"}).set_properties(subset=["ASESOR"], **{"text-align":"left"}))

# =========================================================
# 10. HELPERS DEVELZ (compartidos)
# =========================================================
def _normalizar_texto(txt):
    return str(txt).upper().strip().replace("Í","I").replace("Á","A").replace("É","E").replace("Ó","O").replace("Ú","U")

def _estado_desde_tipis(tipis_txt):
    return TIPIS_ESTADO_MAP.get(_normalizar_texto(tipis_txt), "Otros")

def _normalizar_sot_series(serie):
    s = serie.fillna("").astype(str).str.strip().str.replace(r"\.0$","",regex=True)
    return s.replace(["nan","NaN","None","NONE","null","NULL"], "")

# --- Obtención de campos DEVELZ ---
def _obtener_sot_develz(df):
    col = encontrar_columna(df, ["Back Office - Sot","Back Office - SOT","SOT","sot","Sot"])
    return df[col].fillna("").astype(str).str.strip() if col else pd.Series([""] * len(df), index=df.index)

def _obtener_fecha_inst_develz(df):
    col = encontrar_columna(df, ["Back Office - Fecha Instalacion","Back Office - Fecha Instalación",
                                  "FECHA INSTALACION","Fecha Instalacion","Fecha Instalación"])
    return pd.to_datetime(df[col], errors="coerce", dayfirst=True) if col else pd.Series(pd.NaT, index=df.index)

def _obtener_supervisor_develz(df):
    col = encontrar_columna(df, ["Datos Adicionales - Supervisor","Datos adicionales - Supervisor",
                                  "SUPERVISOR","Supervisor","supervisor","USUARIO","Usuario"])
    return (df[col].fillna("Sin Supervisor").astype(str).str.strip().replace("","Sin Supervisor")
            if col else pd.Series(["Sin Supervisor"] * len(df), index=df.index))

def _obtener_asesor_creador_develz(df):
    col = encontrar_columna(df, ["CREADOR","Creador","creador","Usuario Creador","USUARIO CREADOR",
                                  "Datos Adicionales - Creador","Datos adicionales - Creador"])
    return (df[col].fillna("Sin Asesor").astype(str).str.strip().replace("","Sin Asesor")
            if col else pd.Series(["Sin Asesor"] * len(df), index=df.index))

def _obtener_nombre_cliente_develz(df):
    nom = (df[encontrar_columna(df,["Cliente - Nombre","NOMBRE","Nombre","CLIENTE"])].fillna("").astype(str).str.strip()
           if encontrar_columna(df,["Cliente - Nombre","NOMBRE","Nombre","CLIENTE"]) else pd.Series([""],index=df.index))
    ape_pat = (df[encontrar_columna(df,["Cliente - Apellido Paterno","Apellido Paterno","APELLIDO PATERNO"])].fillna("").astype(str).str.strip()
               if encontrar_columna(df,["Cliente - Apellido Paterno","Apellido Paterno","APELLIDO PATERNO"]) else pd.Series([""],index=df.index))
    ape_mat = (df[encontrar_columna(df,["Cliente - Apellido Materno","Apellido Materno","APELLIDO MATERNO"])].fillna("").astype(str).str.strip()
               if encontrar_columna(df,["Cliente - Apellido Materno","Apellido Materno","APELLIDO MATERNO"]) else pd.Series([""],index=df.index))
    return (nom + " " + ape_pat + " " + ape_mat).str.strip().replace("","Sin Datos").fillna("Sin Datos")

def _obtener_departamento_develz(df):
    col = encontrar_columna(df, ["Datos Instalación - Departamento","Datos Instalacion - Departamento",
                                  "DEPARTAMENTO","Departamento","departamento"])
    return (df[col].fillna("Sin Datos").astype(str).str.strip().replace("","Sin Datos")
            if col else pd.Series(["Sin Datos"] * len(df), index=df.index))

def _obtener_tipis_develz(df):
    col = encontrar_columna(df, ["TIPIS","Tipis","tipis","Estados - Venta Especificacion",
                                  "Estados - Venta Especificación","Estado - Venta Especificacion",
                                  "Estado - Venta Especificación","ESTADO OPERATIVO","Estado Operativo","estado operativo"])
    return (df[col].fillna("Sin TIPIS").astype(str).str.strip().replace("","Sin TIPIS")
            if col else pd.Series(["Sin TIPIS"] * len(df), index=df.index))

def _obtener_documento_develz(df):
    col = encontrar_columna(df, ["Cliente - Documento","Cliente - Nro Documento"])
    return df[col].fillna("").astype(str).str.strip() if col else pd.Series([""] * len(df), index=df.index)

# =========================================================
# 10A. DETALLE FIJA GENERAL — BASE DEVELZ COMPLETA
# =========================================================
@st.cache_data(ttl=300)
def _base_claro_pago(tabla_ventas):
    df_c = preparar_fechas_fija(get_tabla(tabla_ventas))
    cols = ["SOT","COMISION_CLARO","COMISIONES_CLARO"]
    if df_c.empty or "SOT" not in df_c.columns:
        return pd.DataFrame(columns=cols)
    df_c = df_c.copy()
    df_c["SOT"] = df_c["SOT"].fillna("").astype(str).str.strip()
    df_c = df_c[df_c["SOT"] != ""]
    df_c["COMISION_CLARO"] = obtener_comision_fija(df_c)
    df_c["COMISIONES_CLARO"] = (df_c["COMISIONES"].fillna("").astype(str).str.upper().str.strip().str.replace("Í","I",regex=False)
                                 if "COMISIONES" in df_c.columns else "")
    df_c["_pagada_flag"] = (df_c["COMISIONES_CLARO"] == "SI") | (df_c["COMISION_CLARO"] > 0)
    resumen = df_c.groupby("SOT", as_index=False).agg(
        COMISION_CLARO=("COMISION_CLARO","sum"), PAGADA_FLAG=("_pagada_flag","max"))
    resumen["COMISIONES_CLARO"] = resumen["PAGADA_FLAG"].apply(lambda x: "SI" if x else "NO")
    return resumen[cols]

@st.cache_data(ttl=300)
def construir_detalle_fija_develz(tabla_maestro, tabla_claro, canal, filtro_mes):
    cols_salida = ["Canal","SOT","Documento","SUPERVISOR","ASESOR","Nombre del Cliente","Departamento",
                   "FECHA INSTALACION","TIPIS","Estado Operativo","COMISION","Estado Pago"]
    try:
        df_m = get_tabla(tabla_maestro)
        if df_m.empty: return pd.DataFrame(columns=cols_salida)
        df_m = df_m.copy()
        df_m["Canal"] = canal
        df_m["SOT"] = _obtener_sot_develz(df_m)
        df_m["Documento"] = _obtener_documento_develz(df_m)
        df_m["_FECHA_DT"] = _obtener_fecha_inst_develz(df_m)
        if filtro_mes != "Todos los meses":
            m, y = parse_mes_anio(filtro_mes)
            if m and y:
                df_m = df_m[(df_m["_FECHA_DT"].dt.month == m) & (df_m["_FECHA_DT"].dt.year == y)].copy()
        if df_m.empty: return pd.DataFrame(columns=cols_salida)
        df_m["SUPERVISOR"] = _obtener_supervisor_develz(df_m)
        df_m["ASESOR"] = _obtener_asesor_creador_develz(df_m)
        df_m["Nombre del Cliente"] = _obtener_nombre_cliente_develz(df_m)
        df_m["Departamento"] = _obtener_departamento_develz(df_m)
        df_m["TIPIS"] = _obtener_tipis_develz(df_m)
        df_m["Estado Operativo"] = df_m["TIPIS"].apply(_estado_desde_tipis)
        df_pago = _base_claro_pago(tabla_claro)
        df = df_m.merge(df_pago, on="SOT", how="left")
        df["COMISION"] = pd.to_numeric(df.get("COMISION_CLARO", 0), errors="coerce").fillna(0)
        df["COMISIONES_CLARO"] = df.get("COMISIONES_CLARO","").fillna("").astype(str).str.upper().str.strip().str.replace("Í","I",regex=False)
        df["Estado Pago"] = "CAÍDA"
        df.loc[(df["COMISIONES_CLARO"] == "SI") | (df["COMISION"] > 0), "Estado Pago"] = "PAGADA"
        df["FECHA INSTALACION"] = df["_FECHA_DT"].dt.strftime("%d/%m/%Y").fillna("")
        for col in cols_salida:
            if col not in df.columns: df[col] = ""
        return df[cols_salida].reset_index(drop=True)
    except Exception as e:
        st.error(f"Error construyendo detalle DEVELZ {canal}: {e}")
        return pd.DataFrame(columns=cols_salida)

@st.cache_data(ttl=300)
def construir_detalle_fija_general(filtro_mes):
    df_dc = construir_detalle_fija_develz("[DATA DEVELZ].dbo.FIJA_DC", "dbo.CLARO_DC_FIJA", "D&C", filtro_mes)
    df_tt = construir_detalle_fija_develz("[DATA DEVELZ].dbo.FIJA_TELETALK", "dbo.CLARO_TELETALK_FIJA", "Teletalk", filtro_mes)
    return pd.concat([df_dc, df_tt], ignore_index=True)

def kpi_detalle_fija(df):
    if df.empty: return 0, 0, 0, 0.0, 0.0
    total   = int(len(df))
    pagadas = int((df["Estado Pago"] == "PAGADA").sum())
    caidas  = int((df["Estado Pago"] == "CAÍDA").sum())
    comision = pd.to_numeric(df["COMISION"], errors="coerce").fillna(0).sum()
    return total, pagadas, caidas, comision, (pagadas / total * 100) if total > 0 else 0

def ranking_departamentos_df(df):
    if df.empty or "Departamento" not in df.columns: return pd.DataFrame()
    grp = df.groupby("Departamento").agg(
        Total=("Estado Pago","count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
    ).reset_index().sort_values("Pagadas", ascending=False)
    tot_v = grp["Total"].sum(); tot_p = grp["Pagadas"].sum()
    tot_c = grp["Caidas"].sum(); tot_com = pd.to_numeric(grp["Comision"], errors="coerce").fillna(0).sum()
    grp["% Participación"] = ((grp["Pagadas"] / tot_p * 100).round(2).astype(str) + "%" if tot_p > 0 else "0%")
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"
    grp["Comision"] = grp["Comision"].map(formatear_moneda)
    total_row = pd.DataFrame([{"Departamento":"TOTAL","Total":tot_v,"Pagadas":tot_p,"Caidas":tot_c,
        "Comision":formatear_moneda(tot_com),
        "% Participación":"100.00%" if tot_p > 0 else "0%",
        "% Efectividad":f"{(tot_p/tot_v*100):.2f}%" if tot_v > 0 else "0%"}])
    return pd.concat([grp, total_row], ignore_index=True)[
        ["Departamento","Total","Pagadas","Caidas","Comision","% Participación","% Efectividad"]]

def ranking_asesores_detalle(df):
    if df.empty or "SUPERVISOR" not in df.columns: return pd.DataFrame()
    grp = df.groupby("SUPERVISOR").agg(
        Total=("Estado Pago","count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
    ).reset_index().sort_values(["Comision","Total"], ascending=[False,False]).reset_index(drop=True)
    grp.insert(0,"Rank", grp.index + 1)
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"
    total_row = pd.DataFrame([{"Rank":"TOTAL","SUPERVISOR":"","Total":grp["Total"].sum(),
        "Pagadas":grp["Pagadas"].sum(),"Caidas":grp["Caidas"].sum(),
        "% Efectividad":"","Comision":grp["Comision"].sum()}])
    return pd.concat([grp, total_row], ignore_index=True)


def ranking_asesores_por_supervisor_df(df, supervisor):
    cols = ["Rank","ASESOR","Total","Pagadas","Caidas","Comision","% Efectividad"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    base = df.copy()
    if "SUPERVISOR" not in base.columns:
        base["SUPERVISOR"] = "Sin Supervisor"
    if "ASESOR" not in base.columns:
        base["ASESOR"] = "Sin Asesor"
    base["SUPERVISOR"] = base["SUPERVISOR"].fillna("Sin Supervisor").astype(str).str.strip().replace("", "Sin Supervisor")
    base["ASESOR"] = base["ASESOR"].fillna("Sin Asesor").astype(str).str.strip().replace("", "Sin Asesor")
    base["COMISION"] = pd.to_numeric(base.get("COMISION", 0), errors="coerce").fillna(0)
    base = base[base["SUPERVISOR"] == supervisor].copy()
    if base.empty:
        return pd.DataFrame(columns=cols)
    grp = base.groupby("ASESOR", dropna=False).agg(
        Total=("Estado Pago","count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION","sum"),
    ).reset_index().sort_values(["Comision","Pagadas","Total"], ascending=[False,False,False]).reset_index(drop=True)
    grp.insert(0, "Rank", grp.index + 1)
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"
    total = pd.DataFrame([{"Rank":"TOTAL","ASESOR":"","Total":int(grp["Total"].sum()),
        "Pagadas":int(grp["Pagadas"].sum()),"Caidas":int(grp["Caidas"].sum()),
        "Comision":float(grp["Comision"].sum()),"% Efectividad":""}])
    return pd.concat([grp[cols], total[cols]], ignore_index=True)

def mostrar_ranking_supervisores_con_asesores(df):
    rank_df = ranking_asesores_detalle(df)
    if rank_df.empty:
        st.warning("Sin datos para el ranking.")
        return

    rank_sin_total = rank_df[rank_df["Rank"].astype(str) != "TOTAL"].copy()
    total_row = rank_df[rank_df["Rank"].astype(str) == "TOTAL"].copy()

    st.caption("Haz clic en el ➕ de cada supervisor para ver el detalle de asesores.")

    for _, row in rank_sin_total.iterrows():
        supervisor = str(row.get("SUPERVISOR", "Sin Supervisor")).strip() or "Sin Supervisor"
        etiqueta = (
            f"➕ {row['Rank']} | {supervisor} | "
            f"Total: {int(row['Total']):,} | Pagadas: {int(row['Pagadas']):,} | "
            f"Caídas: {int(row['Caidas']):,} | Comisión: {formatear_moneda(row['Comision'])} | "
            f"Efectividad: {row['% Efectividad']}"
        )
        with st.expander(etiqueta, expanded=False):
            detalle_asesor = ranking_asesores_por_supervisor_df(df, supervisor)
            if detalle_asesor.empty:
                st.info("Este supervisor no tiene asesores asociados con los filtros actuales.")
            else:
                st.dataframe(
                    detalle_asesor.style.format({"Comision": lambda x: formatear_moneda(x) if isinstance(x, (int, float)) else x})
                    .set_properties(**{"text-align":"center"})
                    .set_properties(subset=["ASESOR"], **{"text-align":"left"}),
                    use_container_width=True,
                    height=min(420, 80 + 36 * len(detalle_asesor))
                )

    if not total_row.empty:
        st.markdown("##### Total general")
        st.table(total_row.style
            .format({"Comision": lambda x: formatear_moneda(x) if isinstance(x,(int,float)) else x})
            .set_properties(**{"text-align":"center"})
            .set_properties(subset=["SUPERVISOR"], **{"text-align":"left"}))

def ranking_asesores_fija_develz(df):
    cols = ["Rank","ASESOR","Total","Pagadas","Caidas","% Efectividad","Comision"]
    if df.empty or "ASESOR" not in df.columns: return pd.DataFrame(columns=cols)
    base = df.copy()
    base["ASESOR"] = base["ASESOR"].fillna("Sin Asesor").astype(str).str.strip().replace("","Sin Asesor")
    base["COMISION"] = pd.to_numeric(base.get("COMISION",0), errors="coerce").fillna(0)
    grp = base.groupby("ASESOR", dropna=False).agg(
        Total=("Estado Pago","count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION","sum"),
    ).reset_index().sort_values(["Comision","Pagadas","Total"], ascending=[False,False,False]).reset_index(drop=True)
    grp.insert(0,"Rank", grp.index + 1)
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"
    total = pd.DataFrame([{"Rank":"TOTAL","ASESOR":"","Total":int(grp["Total"].sum()),
        "Pagadas":int(grp["Pagadas"].sum()),"Caidas":int(grp["Caidas"].sum()),
        "% Efectividad":"","Comision":float(grp["Comision"].sum())}])
    return pd.concat([grp[cols], total[cols]], ignore_index=True)

def mostrar_iae_asesor_fija_develz(tabla_maestro, tabla_claro, canal, filtro_mes, key_asesor, color):
    df_det = construir_detalle_fija_develz(tabla_maestro, tabla_claro, canal, filtro_mes)
    if df_det.empty: st.warning("Sin datos."); return

    for campo, defecto in [("ASESOR","Sin Asesor"),("SUPERVISOR","Sin Supervisor"),("TIPIS","Sin TIPIS")]:
        if campo not in df_det.columns: df_det[campo] = defecto
        df_det[campo] = df_det[campo].fillna(defecto).astype(str).str.strip()
        df_det.loc[df_det[campo].eq(""), campo] = defecto

    f1, f2, f3 = st.columns(3)
    with f1: filtro_a  = st.selectbox("Asesor / Creador", ["Todos"] + sorted(df_det["ASESOR"].unique().tolist()), key=key_asesor)
    with f2: filtro_su = st.selectbox("Supervisor",       ["Todos"] + sorted(df_det["SUPERVISOR"].unique().tolist()), key=f"{key_asesor}_supervisor")
    with f3: filtro_ti = st.selectbox("Tipificación",     ["Todos"] + sorted(df_det["TIPIS"].unique().tolist()), key=f"{key_asesor}_tipificacion")

    df_f = df_det.copy()
    if filtro_a  != "Todos": df_f = df_f[df_f["ASESOR"]      == filtro_a]
    if filtro_su != "Todos": df_f = df_f[df_f["SUPERVISOR"]   == filtro_su]
    if filtro_ti != "Todos": df_f = df_f[df_f["TIPIS"]        == filtro_ti]

    total, pagadas, caidas, comision, pct = kpi_detalle_fija(df_f)
    color_borde = "#0f4287" if color == "dc" else "#70008f"

    def _card(col, label, valor, sub=""):
        with col:
            st.markdown(
                f'<div style="background:rgba(255,255,255,.95);padding:14px;border-radius:16px;'
                f'border:2px solid {color_borde};text-align:center;margin-bottom:8px;min-height:86px;">'
                f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;display:block;">{label}</span>'
                f'<span style="color:{color_borde};font-size:24px;font-weight:900;display:block;line-height:1.1;">{valor}</span>'
                f'<span style="color:#6b7280;font-size:10px;">{sub}</span></div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    _card(k1,"Total Ventas",f"{total:,}","Base DEVELZ")
    _card(k2,"Pagadas",f"{pagadas:,}","Cruzan con CLARO")
    _card(k3,"Caídas",f"{caidas:,}","No pagadas / sin SOT")
    _card(k4,"% Efectividad",f"{pct:.2f}%","Pagadas / Total")
    _card(k5,"Comisión",formatear_moneda(comision),"CLARO pagado")

    st.write("---")
    st.markdown("### 🏆 Ranking de Asesores")
    ranking = ranking_asesores_fija_develz(df_f)
    if ranking.empty: st.warning("No se encontraron datos para el ranking.")
    else:
        st.dataframe(ranking.style.format({"Comision": lambda x: formatear_moneda(x) if isinstance(x,(int,float)) else x}),
                     use_container_width=True, height=460)

    csv_export = df_f.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(label="⬇️ Descargar base filtrada IAE asesor", data=csv_export,
        file_name=f"iae_asesor_fija_{canal}_{filtro_mes.replace(' ','_')}.csv", mime="text/csv",
        key=f"dl_iae_asesor_{canal}_{key_asesor}")

def estados_operativos_df(df):
    if df.empty: return pd.DataFrame()
    base = df.copy()
    if "Estado Operativo" not in base.columns: base["Estado Operativo"] = "Sin TIPIS"
    base["Estado Operativo"] = base["Estado Operativo"].fillna("Sin TIPIS").astype(str).str.strip()
    base.loc[base["Estado Operativo"].eq(""), "Estado Operativo"] = "Sin TIPIS"
    total = len(base)
    grp = base.groupby("Estado Operativo").agg(N_Ventas=("Estado Pago","count")).reset_index()
    grp["% del total"] = (grp["N_Ventas"] / total * 100).round(2).astype(str) + "%" if total > 0 else "0%"
    orden = {"Conforme":0,"1era Caída":1,"2da Caída":2,"Ejecución":3,"Otros":4,"Sin TIPIS":5}
    grp["_ord"] = grp["Estado Operativo"].map(orden).fillna(99)
    return grp.sort_values("_ord")[["Estado Operativo","N_Ventas","% del total"]]

def ventas_por_dia_df(df):
    cols = ["Fecha","Total Ventas","Pagadas","Caidas","Comision","% Efectividad"]
    if df.empty or "FECHA INSTALACION" not in df.columns: return pd.DataFrame(columns=cols)
    base = df.copy()
    base["_FECHA_DIA"] = pd.to_datetime(base["FECHA INSTALACION"], errors="coerce", dayfirst=True)
    hoy = pd.Timestamp.today().normalize()
    base = base[(base["_FECHA_DIA"] >= pd.Timestamp("2020-01-01")) & (base["_FECHA_DIA"] <= hoy)].copy()
    if base.empty: return pd.DataFrame(columns=cols)
    grp = base.groupby(base["_FECHA_DIA"].dt.date).agg(
        **{"Total Ventas":("Estado Pago","count"),
           "Pagadas":("Estado Pago", lambda x: (x == "PAGADA").sum()),
           "Caidas":("Estado Pago",  lambda x: (x == "CAÍDA").sum()),
           "Comision":("COMISION",   lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum())}
    ).reset_index().rename(columns={"_FECHA_DIA":"Fecha"})
    grp["Fecha"] = pd.to_datetime(grp["Fecha"])
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total Ventas"] * 100).round(2).astype(str) + "%"
    return grp.sort_values("Fecha")[cols]

# --- Conciliación helpers ---
def _df_develz_para_conciliacion(tabla_maestro, canal, filtro_mes):
    df = get_tabla(tabla_maestro)
    empty = pd.DataFrame(columns=["Canal","SOT","Fecha_Develz","Supervisor","Cliente","Departamento","TIPIS"])
    if df.empty: return empty
    df = df.copy()
    df["Canal"] = canal
    df["SOT"] = _normalizar_sot_series(_obtener_sot_develz(df))
    df["_FECHA_DT"] = _obtener_fecha_inst_develz(df)
    if filtro_mes != "Todos los meses":
        m, y = parse_mes_anio(filtro_mes)
        if m and y:
            df = df[(df["_FECHA_DT"].dt.month == m) & (df["_FECHA_DT"].dt.year == y)].copy()
    if df.empty: return empty
    df["Fecha_Develz"] = df["_FECHA_DT"].dt.strftime("%d/%m/%Y").fillna("")
    df["Supervisor"]   = _obtener_supervisor_develz(df)
    df["Cliente"]      = _obtener_nombre_cliente_develz(df)
    df["Departamento"] = _obtener_departamento_develz(df)
    df["TIPIS"]        = _obtener_tipis_develz(df)
    df["Documento"]    = _obtener_documento_develz(df)
    return df[["Canal","SOT","Fecha_Develz","Supervisor","Cliente","Documento","Departamento","TIPIS"]].copy()

def _df_claro_para_conciliacion(tabla_claro, canal, filtro_mes):
    df = preparar_fechas_fija(get_tabla(tabla_claro))
    empty = pd.DataFrame(columns=["Canal","SOT","Fecha_Claro","Cliente","Documento","Comision_Claro","Comisiones_Claro"])
    if df.empty or "SOT" not in df.columns: return empty
    df = df.copy()
    df["Canal"] = canal
    df["SOT"] = _normalizar_sot_series(df["SOT"])
    df = df[df["SOT"] != ""]
    if filtro_mes != "Todos los meses" and "FECHA INSTALACION" in df.columns:
        df = filtrar_por_mes_anio(df, "FECHA INSTALACION", filtro_mes)
    if df.empty: return empty
    df["Comision_Claro"] = obtener_comision_fija(df)
    df["Comisiones_Claro"] = (df["COMISIONES"].fillna("").astype(str).str.upper().str.strip().str.replace("Í","I",regex=False)
                               if "COMISIONES" in df.columns else "")
    df["Fecha_Claro"] = (df["FECHA INSTALACION"].dt.strftime("%d/%m/%Y").fillna("")
                          if "FECHA INSTALACION" in df.columns else "")
    col_doc = encontrar_columna(df, ["NRO DOCUMENTO","DOCUMENTO","DNI"])
    df["Documento"] = df[col_doc].fillna("").astype(str).str.strip() if col_doc else ""
    col_cli = encontrar_columna(df, ["CLIENTE","Cliente","NOMBRE CLIENTE","Nombre Cliente","NOMBRE","Nombre","Nombre del Cliente"])
    df["Cliente"] = df[col_cli].fillna("").astype(str).str.strip() if col_cli else ""
    df_res = df.groupby(["Canal","SOT"], as_index=False).agg(
        Fecha_Claro=("Fecha_Claro","first"), Cliente=("Cliente","first"), Documento=("Documento","first"),
        Comision_Claro=("Comision_Claro","sum"),
        Comisiones_Claro=("Comisiones_Claro", lambda x: "SI" if (x.astype(str).str.upper().str.strip() == "SI").any() else "NO"))
    return df_res[["Canal","SOT","Fecha_Claro","Cliente","Documento","Comision_Claro","Comisiones_Claro"]].copy()

def obtener_claro_pagado_no_develz(filtro_mes, filtro_canal):
    pares = [("D&C","[DATA DEVELZ].dbo.FIJA_DC","dbo.CLARO_DC_FIJA"),
             ("Teletalk","[DATA DEVELZ].dbo.FIJA_TELETALK","dbo.CLARO_TELETALK_FIJA")]
    salida = []
    for canal, tabla_dev, tabla_claro in pares:
        if filtro_canal != "Todos" and canal != filtro_canal: continue
        dev   = _df_develz_para_conciliacion(tabla_dev, canal, filtro_mes)
        claro = _df_claro_para_conciliacion(tabla_claro, canal, filtro_mes)
        if claro.empty: continue
        dev_sot = set(dev[dev["SOT"] != ""]["SOT"].unique()) if not dev.empty else set()
        claro["PAGADA_CLARO"] = (
            (claro["Comisiones_Claro"].fillna("").astype(str).str.upper().str.strip() == "SI") |
            (pd.to_numeric(claro["Comision_Claro"], errors="coerce").fillna(0) > 0))
        faltantes = claro[(claro["PAGADA_CLARO"]) & (~claro["SOT"].isin(dev_sot))].copy()
        if not faltantes.empty:
            faltantes["Motivo"] = "Claro lo paga, pero el SOT no aparece en DEVELZ"
            salida.append(faltantes)
    if not salida:
        return pd.DataFrame(columns=["Canal","SOT","Fecha_Claro","Cliente","Documento","Comision_Claro","Comisiones_Claro","Motivo"])
    df_out = pd.concat(salida, ignore_index=True)
    for col in ["Cliente","Documento"]:
        if col not in df_out.columns: df_out[col] = ""
    return df_out[["Canal","SOT","Fecha_Claro","Cliente","Documento","Comision_Claro","Comisiones_Claro","Motivo"]]

def mostrar_claro_pagado_no_develz(filtro_mes, filtro_canal):
    st.write("---")
    st.markdown("#### 🔴 Ventas pagadas por CLARO que NO aparecen en DEVELZ")
    st.caption("Este cuadro explica la diferencia entre el número pagado de CLARO y el detalle basado en DEVELZ.")
    df_faltantes = obtener_claro_pagado_no_develz(filtro_mes, filtro_canal)
    if df_faltantes.empty:
        st.success("No hay SOT pagados por CLARO faltantes en DEVELZ con los filtros seleccionados.")
        return
    total_sot     = df_faltantes["SOT"].nunique()
    total_comision = pd.to_numeric(df_faltantes["Comision_Claro"], errors="coerce").fillna(0).sum()

    def _mini(col, label, valor, color):
        with col:
            st.markdown(f'<div style="background:rgba(255,255,255,.96);padding:14px;border-radius:14px;'
                        f'border:2px solid {color};text-align:center;margin-bottom:8px;">'
                        f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;">{label}</span>'
                        f'<span style="color:{color};font-size:26px;font-weight:900;display:block;">{valor}</span>'
                        f'</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    _mini(c1,"SOT pagados no encontrados",f"{total_sot:,}","#dc2626")
    _mini(c2,"Comisión no conciliada",formatear_moneda(total_comision),"#dc2626")

    df_show = df_faltantes.copy()
    for col in ["Cliente","Documento"]:
        if col not in df_show.columns: df_show[col] = ""
    df_show["Comision_Claro"] = pd.to_numeric(df_show["Comision_Claro"], errors="coerce").fillna(0).map(formatear_moneda)
    st.dataframe(df_show, use_container_width=True, height=260)
    csv_export = df_faltantes.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("⬇️ Descargar SOT pagados por CLARO no encontrados en DEVELZ", data=csv_export,
        file_name=f"claro_pagado_no_develz_{filtro_mes.replace(' ','_')}_{filtro_canal}.csv",
        mime="text/csv", key="dl_claro_pagado_no_develz_detalle")

def _kpi_card_html(col, label, valor, sub, color_borde, color_val="inherit"):
    with col:
        st.markdown(
            f'<div style="background:rgba(255,255,255,.95);padding:16px;border-radius:16px;'
            f'border:2px solid {color_borde};text-align:center;margin-bottom:8px;min-height:92px;">'
            f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;'
            f'letter-spacing:.1em;display:block;margin-bottom:6px;">{label}</span>'
            f'<span style="color:{color_val};font-size:24px;font-weight:900;display:block;line-height:1.05;">{valor}</span>'
            f'<span style="color:#6b7280;font-size:10px;">{sub}</span></div>', unsafe_allow_html=True)

def _grafico_barras_agrupado(chart_melt, sort_order, x_title, bar_size=18):
    import altair as alt
    # ✅ Seguridad extra: evita error narwhals.exceptions.DuplicateError por nombres duplicados
    chart_melt = chart_melt.loc[:, ~chart_melt.columns.duplicated()].copy()
    base = alt.Chart(chart_melt).encode(
        x=alt.X("Fecha:N", title=x_title, sort=sort_order,
                 axis=alt.Axis(labelAngle=0, labelFontSize=11, titleFontSize=12)),
        xOffset=alt.XOffset("Indicador:N"),
        y=alt.Y("Cantidad:Q", title="Ventas", axis=alt.Axis(labelFontSize=12, titleFontSize=12, grid=True)),
        color=alt.Color("Indicador:N",
                         scale=alt.Scale(domain=["Total Ventas","Pagadas"], range=["#123f7a","#10a06f"]),
                         legend=alt.Legend(title="Indicador", orient="top-right")),
        tooltip=[alt.Tooltip("Fecha:N", title=x_title), alt.Tooltip("Indicador:N"), alt.Tooltip("Cantidad:Q", format=",.0f")]
    )
    barras    = base.mark_bar(size=bar_size, cornerRadiusTopLeft=6, cornerRadiusTopRight=6, opacity=0.92)
    etiquetas = base.mark_text(align="center", baseline="bottom", dy=-6, fontSize=10, fontWeight="bold", color="#111827"
                               ).encode(text=alt.Text("Cantidad:Q", format=".0f"))
    return (barras + etiquetas).properties(
        height=430, padding={"left":10,"right":25,"top":15,"bottom":10}
    ).configure_axis(labelFontSize=11, titleFontSize=12, grid=True, gridColor="#e5e7eb", domain=False
    ).configure_view(strokeWidth=0
    ).configure_legend(titleFontSize=12, labelFontSize=12, orient="top-right", symbolSize=120)

def mostrar_detalle_fija_general():
    color_titulo = "#004a99"; color_borde = "#0f4287"
    set_bg(img_caratula)
    st.markdown(f'<div style="color:{color_titulo};font-size:34px;font-weight:900;margin-bottom:4px;">Detalle FIJA General</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{color_titulo};font-weight:800;font-size:16px;margin-bottom:16px;">D&C + TELETALK · BASE DEVELZ COMPLETA · CAÍDA REAL · PAGADA VS CAÍDA</div>', unsafe_allow_html=True)
    st.write("---")

    col_f1,col_f2,col_f3,col_f4,col_f5 = st.columns([1.2,1.1,1.1,1.4,1.6])
    with col_f1: filtro_mes   = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="det_general_mes")
    with col_f2: filtro_canal = st.selectbox("Canal", ["Todos","D&C","Teletalk"], key="det_general_canal")
    with col_f3: filtro_estado= st.selectbox("Estado de Pago", ["Todos","PAGADA","CAÍDA"], key="det_general_estado")

    with st.spinner("Cargando todas las ventas desde DEVELZ y cruzando con Claro..."):
        df_det = construir_detalle_fija_general(filtro_mes)

    if df_det.empty:
        st.warning("No se encontraron datos. Verifica que FIJA_DC.csv, FIJA_TELETALK.csv y los archivos Claro estén en la carpeta correcta.")
        return
    if "Documento" not in df_det.columns: df_det["Documento"] = ""
    if filtro_canal != "Todos": df_det = df_det[df_det["Canal"] == filtro_canal]
    if "TIPIS" in df_det.columns:
        df_det["TIPIS"] = df_det["TIPIS"].fillna("Sin TIPIS").astype(str).str.strip()
        df_det.loc[df_det["TIPIS"].eq(""), "TIPIS"] = "Sin TIPIS"
    else: df_det["TIPIS"] = "Sin TIPIS"

    with col_f4:
        filtro_supervisor = st.selectbox("Supervisor", ["Todos"] + sorted(df_det["SUPERVISOR"].fillna("Sin Supervisor").unique().tolist()), key="det_general_supervisor")
    with col_f5:
        filtro_tipificacion = st.selectbox("Tipificación", ["Todos"] + sorted(df_det["TIPIS"].fillna("Sin TIPIS").astype(str).unique().tolist()), key="det_general_tipificacion")

    df_filtrado = df_det.copy()
    if filtro_estado     != "Todos": df_filtrado = df_filtrado[df_filtrado["Estado Pago"]  == filtro_estado]
    if filtro_supervisor != "Todos": df_filtrado = df_filtrado[df_filtrado["SUPERVISOR"]   == filtro_supervisor]
    if filtro_tipificacion != "Todos": df_filtrado = df_filtrado[df_filtrado["TIPIS"]      == filtro_tipificacion]

    total, pagadas, caidas, comision, pct = kpi_detalle_fija(df_filtrado)
    st.markdown("### Resumen General")
    k1,k2,k3,k4,k5 = st.columns(5)
    _kpi_card_html(k1,"Total Ventas",  f"{total:,}",          "Base DEVELZ",   color_borde, color_borde)
    _kpi_card_html(k2,"Pagadas",       f"{pagadas:,}",         "Cruza con Claro","#059669","#059669")
    _kpi_card_html(k3,"Caídas",        f"{caidas:,}",          "Sin pago / sin SOT","#dc2626","#dc2626")
    _kpi_card_html(k4,"% Efectividad", f"{pct:.2f}%",          "Pagadas / Total",color_borde,"#059669" if pct>=75 else "#d97706")
    _kpi_card_html(k5,"Comisión Total",formatear_moneda(comision),"Pagada",     color_borde, color_borde)
    st.write("---")

    tab1,tab2,tab3,tab4,tab5 = st.tabs(["📋 Detalle Ventas","📆 Ventas por Día","🏆 Ranking Asesores","📍 Ranking Departamentos","📊 Estados Operativos"])

    with tab1:
        st.markdown("#### Detalle de ventas DEVELZ con estado final")
        def _colorear_estado(val):
            if val == "PAGADA": return "background-color:#dcfce7;color:#166534;font-weight:700"
            if val == "CAÍDA":  return "background-color:#fee2e2;color:#991b1b;font-weight:700"
            return ""
        cols_mostrar = ["Canal","SOT","Documento","SUPERVISOR","Nombre del Cliente","Departamento",
                        "FECHA INSTALACION","TIPIS","Estado Operativo","COMISION","Estado Pago"]
        for col in cols_mostrar:
            if col not in df_filtrado.columns: df_filtrado[col] = ""
        df_show = df_filtrado[cols_mostrar].copy()
        df_show["COMISION"] = pd.to_numeric(df_show["COMISION"], errors="coerce").fillna(0).map(formatear_moneda)
        st.dataframe(df_show.style.map(_colorear_estado, subset=["Estado Pago"]), use_container_width=True, height=450)
        csv_export = df_filtrado.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇️ Descargar CSV completo", data=csv_export,
            file_name=f"detalle_fija_develz_{filtro_mes.replace(' ','_')}_{filtro_canal}.csv",
            mime="text/csv", key="dl_det_general")
        mostrar_claro_pagado_no_develz(filtro_mes, filtro_canal)

    with tab2:
        st.markdown("#### Ventas por día — Total vs Pagadas")
        df_dia = ventas_por_dia_df(df_filtrado)
        if df_dia.empty:
            st.warning("No hay fechas válidas para mostrar ventas por día.")
        else:
            if filtro_mes == "Todos los meses":
                df_tmp = df_filtrado.copy()
                df_tmp["_FECHA_GRAFICO"] = pd.to_datetime(df_tmp["FECHA INSTALACION"], errors="coerce", dayfirst=True)
                hoy = pd.Timestamp.today().normalize()
                df_tmp = df_tmp[(df_tmp["_FECHA_GRAFICO"] >= pd.Timestamp("2020-01-01")) & (df_tmp["_FECHA_GRAFICO"] <= hoy)].copy()
                if df_tmp.empty:
                    st.warning("No hay fechas válidas para mostrar el gráfico por mes.")
                else:
                    df_chart = df_tmp.groupby(df_tmp["_FECHA_GRAFICO"].dt.to_period("M")).agg(
                        **{"Total Ventas":("Estado Pago","count"),
                           "Pagadas":("Estado Pago", lambda x: (x=="PAGADA").sum()),
                           "Caidas":("Estado Pago",  lambda x: (x=="CAÍDA").sum()),
                           "Comision":("COMISION",   lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum())}
                    ).reset_index()
                    df_chart["Fecha_dt"]  = df_chart["_FECHA_GRAFICO"].dt.to_timestamp()
                    df_chart["Fecha"]     = df_chart["Fecha_dt"].dt.strftime("%m/%y")
                    df_chart["% Efectividad"] = (df_chart["Pagadas"]/df_chart["Total Ventas"]*100).round(2).astype(str)+"%"
                    chart_melt = df_chart.melt(id_vars=["Fecha_dt","Fecha"], value_vars=["Total Ventas","Pagadas"],
                                               var_name="Indicador", value_name="Cantidad")
                    chart_melt = chart_melt.rename(columns={"Fecha":"Fecha"})
                    st.altair_chart(_grafico_barras_agrupado(chart_melt, df_chart["Fecha"].tolist(), "Mes", bar_size=32), use_container_width=True)
                    tabla_dia = df_chart[["Fecha","Total Ventas","Pagadas","Caidas","Comision","% Efectividad"]].copy()
                    tabla_dia = tabla_dia.rename(columns={"Fecha":"Mes"})
                    tabla_dia["Comision"] = pd.to_numeric(tabla_dia["Comision"], errors="coerce").fillna(0).map(formatear_moneda)
                    total_row = pd.DataFrame([{"Mes":"TOTAL","Total Ventas":tabla_dia["Total Ventas"].sum(),
                        "Pagadas":tabla_dia["Pagadas"].sum(),"Caidas":tabla_dia["Caidas"].sum(),
                        "Comision":formatear_moneda(pd.to_numeric(df_chart["Comision"], errors="coerce").fillna(0).sum()),
                        "% Efectividad":f"{(tabla_dia['Pagadas'].sum()/tabla_dia['Total Ventas'].sum()*100):.2f}%" if tabla_dia["Total Ventas"].sum()>0 else "0%"}])
                    st.markdown("#### Tabla mensual")
                    st.dataframe(pd.concat([tabla_dia,total_row],ignore_index=True), use_container_width=True, height=420)
            else:
                chart_base = df_dia.copy()
                chart_base["Fecha"] = pd.to_datetime(chart_base["Fecha"])
                chart_base["Fecha_txt"] = chart_base["Fecha"].dt.strftime("%d/%m")
                # ✅ CORRECCIÓN: Altair/Narwhals no acepta columnas duplicadas.
                # Antes se enviaba Fecha y Fecha_txt, luego Fecha_txt se renombraba a Fecha,
                # quedando 2 columnas llamadas Fecha. Aquí usamos solo la fecha visible del gráfico.
                chart_melt = chart_base.melt(id_vars=["Fecha_txt"], value_vars=["Total Ventas","Pagadas"],
                                             var_name="Indicador", value_name="Cantidad")
                chart_melt = chart_melt.rename(columns={"Fecha_txt":"Fecha"})
                chart_melt = chart_melt.loc[:, ~chart_melt.columns.duplicated()].copy()
                st.altair_chart(_grafico_barras_agrupado(chart_melt, chart_base["Fecha_txt"].tolist(), "Fecha"), use_container_width=True)
                tabla_dia = df_dia.copy()
                tabla_dia["Fecha"] = pd.to_datetime(tabla_dia["Fecha"]).dt.strftime("%d/%m/%Y")
                tabla_dia["Comision"] = pd.to_numeric(tabla_dia["Comision"], errors="coerce").fillna(0).map(formatear_moneda)
                total_row = pd.DataFrame([{"Fecha":"TOTAL","Total Ventas":tabla_dia["Total Ventas"].sum(),
                    "Pagadas":tabla_dia["Pagadas"].sum(),"Caidas":tabla_dia["Caidas"].sum(),
                    "Comision":formatear_moneda(pd.to_numeric(df_dia["Comision"], errors="coerce").fillna(0).sum()),
                    "% Efectividad":f"{(tabla_dia['Pagadas'].sum()/tabla_dia['Total Ventas'].sum()*100):.2f}%" if tabla_dia["Total Ventas"].sum()>0 else "0%"}])
                st.markdown("#### Tabla diaria")
                st.dataframe(pd.concat([tabla_dia,total_row],ignore_index=True), use_container_width=True, height=420)

    with tab3:
        st.markdown("#### Ranking de Supervisores — PAGADA vs CAÍDA")
        mostrar_ranking_supervisores_con_asesores(df_filtrado)

    with tab4:
        st.markdown("#### Ranking por Departamento de Instalación")
        st.caption("Fuente: columna `Datos Instalación - Departamento` de DEVELZ")
        rank_dpto = ranking_departamentos_df(df_filtrado)
        if rank_dpto.empty:
            st.warning("No se encontró columna de departamento.")
        else:
            import altair as alt
            df_chart = rank_dpto[rank_dpto["Departamento"] != "TOTAL"].copy()
            if not df_chart.empty:
                chart_data_melt = df_chart[["Departamento","Pagadas","Caidas"]].melt("Departamento", var_name="Estado", value_name="Cantidad")
                chart = alt.Chart(chart_data_melt).mark_bar().encode(
                    x=alt.X("Cantidad:Q", title="Ventas"),
                    y=alt.Y("Departamento:N", sort="-x", title=""),
                    color=alt.Color("Estado:N", scale=alt.Scale(domain=["Pagadas","Caidas"], range=["#059669","#dc2626"])),
                    tooltip=["Departamento","Estado","Cantidad"]
                ).properties(height=max(200, len(df_chart)*40)).configure_axis(labelFontSize=12, titleFontSize=13)
                st.altair_chart(chart, use_container_width=True)
            st.markdown("**Tabla de detalle por departamento**")
            st.table(rank_dpto)

    with tab5:
        st.markdown("#### Estados Operativos (TIPIS agrupado)")
        estados_df = estados_operativos_df(df_filtrado)
        if estados_df.empty: st.warning("No se encontraron datos de TIPIS.")
        else:
            col_e1, col_e2 = st.columns([1, 1.5])
            with col_e1: st.table(estados_df)
            with col_e2:
                if "TIPIS" in df_filtrado.columns:
                    for estado_grupo in ["Conforme","1era Caída","2da Caída","Ejecución","Otros","Sin TIPIS"]:
                        df_grupo = df_filtrado[df_filtrado["Estado Operativo"] == estado_grupo]
                        if df_grupo.empty: continue
                        tipis_count = df_grupo["TIPIS"].fillna("Sin TIPIS").replace("","Sin TIPIS").value_counts().reset_index()
                        tipis_count.columns = ["TIPIS","Cantidad"]
                        with st.expander(f"{estado_grupo}  ({len(df_grupo)} ventas)", expanded=False):
                            st.table(tipis_count)

# =========================================================
# =========================================================
# =========================================================
# =========================================================
# =========================================================
# 10B. DETALLE MÓVIL GENERAL — TELETALK CRUCE REAL POR NÚMERO
# =========================================================
# LÓGICA FINAL:
# - La BASE es CLARO_TELETALK_MOVIL.csv.
# - En la BASE el número está en la columna TELEFONO.
# - La 2DA CAÍDA es CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv.
# - La 3RA CAÍDA es CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv.
# - El universo SIEMPRE es la BASE CLARO_TELETALK_MOVIL.csv.
# - Base Pagados se cuenta desde CLARO_TELETALK_MOVIL.csv.
# - 2da caída = clientes de la BASE cuyo DNI CLIENTE cruza con DNI RUC de CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv y COMISION > 0.
# - 3ra caída = filas de la BASE cuyo TELEFONO aparece en MSISDN de tercera caída.
# - Fecha de Venta:
#   * Base Pagados y 2da Caída se filtran con la fecha de la BASE CLARO_TELETALK_MOVIL.csv.
#   * 3ra Caída se filtra con FEC ACTIV CTR del archivo CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv.
# - Se cuenta por líneas/registros, no por clientes únicos.
# - Se eliminan las tarjetas adicionales dentro del tab; queda solo tabla + gráfico.

ARCHIVOS_TELETALK_MOVIL_CAIDAS = [
    {
        "archivo": "CLARO_TELETALK_MOVIL.csv",
        "etapa": "Base Pagados",
        "orden": 1,
        "descripcion": "Base principal pagada",
        "columnas_numero": ["TELEFONO", "TELÉFONO", "Telefono", "Teléfono", "NUMERO", "NÚMERO", "MSISDN"],
    },
    {
        "archivo": "CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv",
        "etapa": "2da Caída - 3 meses",
        "orden": 2,
        "descripcion": "Números pagados a 3 meses",
        "columnas_numero": ["MSISDN", "TELEFONO", "TELÉFONO", "Telefono", "Teléfono", "NUMERO", "NÚMERO"],
    },
    {
        "archivo": "CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv",
        "etapa": "3ra Caída - 6 meses",
        "orden": 3,
        "descripcion": "Números pagados a 6 meses",
        "columnas_numero": ["MSISDN", "TELEFONO", "TELÉFONO", "Telefono", "Teléfono", "NUMERO", "NÚMERO"],
    },
]


def _limpiar_numero_movil(serie):
    s = (
        serie.fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\D", "", regex=True)
    )
    return s.replace(["", "nan", "NaN", "None", "NONE", "null", "NULL"], pd.NA)




def _limpiar_documento_movil(serie):
    s = (
        serie.fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\D", "", regex=True)
    )
    return s.replace(["", "nan", "NaN", "None", "NONE", "null", "NULL"], pd.NA)


def _obtener_documento_por_columnas(df, posibles):
    col = encontrar_columna(df, posibles)
    if col:
        return _limpiar_documento_movil(df[col]), col
    return pd.Series([pd.NA] * len(df), index=df.index), ""


def _obtener_numero_por_columnas(df, posibles):
    col = encontrar_columna(df, posibles)
    if col:
        return _limpiar_numero_movil(df[col]), col
    return pd.Series([pd.NA] * len(df), index=df.index), ""


def _obtener_fecha_teletalk_movil(df):
    col = encontrar_columna(df, [
        # ✅ Para CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv el filtro de Fecha de Venta
        # debe salir de FEC ACTIV CTR. Se coloca primero para darle prioridad.
        "FEC ACTIV CTR", "FEC. ACTIV CTR", "FECHA ACTIV CTR", "FECHA ACTIVACION CTR",
        "FECHA ACTIVACIÓN CTR", "Fec Activ Ctr", "FEC ACTIVACIÓN CTR",
        "FECHA OPERACION", "FECHA OPERACIÓN",
        "FECHA CARGA", "FECHA VENTA",
        "Fecha Operacion", "Fecha Operación",
        "Fecha Carga", "Fecha Venta"
    ])
    if col:
        return pd.to_datetime(df[col], errors="coerce", dayfirst=True), col
    return pd.Series(pd.NaT, index=df.index), ""


def _obtener_campo_movil_seguro(df, posibles, defecto="Sin datos"):
    col = encontrar_columna(df, posibles)
    if col:
        return df[col].fillna(defecto).astype(str).str.strip().replace("", defecto)
    return pd.Series([defecto] * len(df), index=df.index)


def _obtener_cliente_movil_teletalk(df):
    col_cliente = encontrar_columna(df, [
        "CLIENTE", "Cliente", "NOMBRE CLIENTE", "Nombre Cliente",
        "NOMBRE", "Nombre", "Nombre del Cliente"
    ])
    if col_cliente:
        return df[col_cliente].fillna("Sin Cliente").astype(str).str.strip().replace("", "Sin Cliente")

    nombre = _obtener_campo_movil_seguro(df, ["Cliente - Nombre", "NOMBRE"], "")
    apepat = _obtener_campo_movil_seguro(df, ["Cliente - Apellido Paterno", "APELLIDO PATERNO"], "")
    apemat = _obtener_campo_movil_seguro(df, ["Cliente - Apellido Materno", "APELLIDO MATERNO"], "")
    return (nombre + " " + apepat + " " + apemat).str.strip().replace("", "Sin Cliente")


def _obtener_numero_movil(df, posibles):
    col = encontrar_columna(df, posibles)
    if col:
        return pd.to_numeric(df[col], errors="coerce").fillna(0)
    return pd.Series([0.0] * len(df), index=df.index)


def _preparar_archivo_teletalk_movil(item):
    nombre_archivo = item["archivo"]
    etapa = item["etapa"]
    orden = item["orden"]
    descripcion = item["descripcion"]
    columnas_numero = item["columnas_numero"]

    cols_salida = [
        "Etapa", "Orden", "Archivo", "Descripción",
        "NUMERO_LINEA", "COLUMNA_NUMERO",
        "FECHA_ORIGINAL", "FECHA_BASE",
        "ASESOR", "Cliente", "Documento",
        "Departamento", "Transaccion", "Plan", "CF",
        "DIAS PORTADAS", "COMISION", "Estado Pago"
    ]

    df = cargar_csv(nombre_archivo)
    if df.empty:
        return pd.DataFrame(columns=cols_salida + ["_FECHA_ORIGINAL_DT", "_FECHA_BASE_DT"])

    df = df.copy()

    numero, col_numero = _obtener_numero_por_columnas(df, columnas_numero)
    fecha_dt, _ = _obtener_fecha_teletalk_movil(df)

    df["NUMERO_LINEA"] = numero
    df["COLUMNA_NUMERO"] = col_numero if col_numero else "NO ENCONTRADA"

    df["_FECHA_ORIGINAL_DT"] = fecha_dt
    df["_FECHA_BASE_DT"] = fecha_dt

    df["FECHA_ORIGINAL"] = df["_FECHA_ORIGINAL_DT"].dt.strftime("%d/%m/%Y").fillna("Sin fecha")
    df["FECHA_BASE"] = df["_FECHA_BASE_DT"].dt.strftime("%d/%m/%Y").fillna("Sin fecha")

    df["Etapa"] = etapa
    df["Orden"] = orden
    df["Archivo"] = nombre_archivo
    df["Descripción"] = descripcion

    df["Documento"] = _obtener_campo_movil_seguro(df, [
        "DNI CLIENTE", "DNI RUC", "DNI", "RUC", "DOCUMENTO", "NRO DOCUMENTO", "NRO. DOCUMENTO"
    ], "")

    df["ASESOR"] = _obtener_campo_movil_seguro(df, [
        "USUARIO", "ASESOR", "VENDEDOR", "DISTRIBUIDOR",
        "EJECUTIVO", "CREADOR", "Usuario", "Asesor"
    ], "Sin Asesor")

    df["Cliente"] = _obtener_cliente_movil_teletalk(df)

    df["Departamento"] = _obtener_campo_movil_seguro(df, [
        "DEPARTAMENTO", "Departamento", "departamento",
        "DPTO", "REGION", "REGIÓN", "Región",
        "Datos Instalación - Departamento",
        "Datos Instalacion - Departamento"
    ], "Sin Departamento")

    df["Transaccion"] = _obtener_campo_movil_seguro(df, [
        "TRANSACCION", "TRANSACCIÓN", "Transaccion", "Transacción",
        "TIPO TRANSACCION", "TIPO DE VENTA", "Tipo Transaccion"
    ], "Sin Transacción")

    df["Plan"] = _obtener_campo_movil_seguro(df, [
        "PLAN", "Plan", "PRODUCTO", "Producto", "SERVICIO", "Servicio"
    ], "Sin Plan")

    df["CF"] = _obtener_numero_movil(df, ["CF", "Cargo Fijo", "CARGO FIJO"])
    df["DIAS PORTADAS"] = _obtener_numero_movil(df, ["DIAS PORTADAS", "DÍAS PORTADAS", "Dias Portadas"])

    df["COMISION"] = obtener_comision_movil(df)
    df["Estado Pago"] = "PAGADA"

    return df[cols_salida + ["_FECHA_ORIGINAL_DT", "_FECHA_BASE_DT"]].reset_index(drop=True)


@st.cache_data(ttl=300)
def _cargar_bases_teletalk_por_numero():
    base = _preparar_archivo_teletalk_movil(ARCHIVOS_TELETALK_MOVIL_CAIDAS[0])
    segunda = _preparar_archivo_teletalk_movil(ARCHIVOS_TELETALK_MOVIL_CAIDAS[1])
    tercera = _preparar_archivo_teletalk_movil(ARCHIVOS_TELETALK_MOVIL_CAIDAS[2])
    return base, segunda, tercera


def _filtrar_base_por_mes(base, filtro_mes):
    if base.empty:
        return base

    if filtro_mes != "Todos los meses":
        m, y = parse_mes_anio(filtro_mes)
        if m and y:
            return base[
                (base["_FECHA_BASE_DT"].dt.month == m) &
                (base["_FECHA_BASE_DT"].dt.year == y)
            ].copy()

    return base.copy()


@st.cache_data(ttl=300)
def construir_detalle_movil_teletalk_caidas(filtro_mes="Todos los meses"):
    base, segunda, tercera = _cargar_bases_teletalk_por_numero()

    if base.empty:
        return pd.DataFrame()

    base_filtrada = _filtrar_base_por_mes(base, filtro_mes)

    # ✅ Para 3ra caída el filtro de Fecha de Venta NO debe usar la fecha de la base.
    # Debe usar FEC ACTIV CTR del archivo CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv.
    tercera_filtrada = _filtrar_base_por_mes(tercera, filtro_mes)

    # ✅ LÓGICA CORRECTA SOLICITADA:
    # Base Pagados: se queda igual desde CLARO_TELETALK_MOVIL.csv
    # 2da Caída: cruza DNI CLIENTE de CLARO_TELETALK_MOVIL.csv
    #             contra DNI RUC de CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv
    #             y SOLO cuenta cuando COMISION > 0
    # 3ra Caída: se mantiene por TELEFONO de base contra MSISDN de tercera caída
    df_base_raw = cargar_csv("CLARO_TELETALK_MOVIL.csv")
    df_segunda_raw = cargar_csv("CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv")

    doc_base_full, col_doc_base = _obtener_documento_por_columnas(df_base_raw, ["DNI CLIENTE"]) if not df_base_raw.empty else (pd.Series(dtype="object"), "")

    # ✅ NUEVA REGLA DE NEGOCIO:
    # La 2da caída SOLO cuenta cuando el cliente cruza por DNI y en el archivo
    # CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv la columna COMISION es mayor a cero.
    # Si COMISION está vacía, en cero o no es numérica, NO se cuenta en 2da caída.
    col_comision_segunda = encontrar_columna(df_segunda_raw, [
        "COMISION", "COMISIÓN", "Comision", "Comisión", "comision", "comisión",
        "COMISION TOTAL", "COMISIÓN TOTAL", "Comision Total", "MONTO"
    ]) if not df_segunda_raw.empty else None

    if not df_segunda_raw.empty and col_comision_segunda:
        comision_segunda = pd.to_numeric(df_segunda_raw[col_comision_segunda], errors="coerce").fillna(0)
        df_segunda_raw = df_segunda_raw[comision_segunda > 0].copy()
    elif not df_segunda_raw.empty:
        # Si no existe columna de comisión, no contamos nada en 2da caída para no inflar el KPI.
        df_segunda_raw = df_segunda_raw.iloc[0:0].copy()

    doc_segunda, col_doc_segunda = _obtener_documento_por_columnas(df_segunda_raw, ["DNI RUC"]) if not df_segunda_raw.empty else (pd.Series(dtype="object"), "")

    # ✅ Comisión adicional real de 2da caída:
    # Se toma desde CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv, columna COMISION.
    # Se agrupa por DNI RUC para no duplicar montos cuando el mismo cliente aparece más de una vez.
    if not df_segunda_raw.empty and col_comision_segunda and len(doc_segunda) > 0:
        df_segunda_comision = pd.DataFrame({
            "_DNI_CLIENTE_CRUCE": doc_segunda,
            "_COMISION_ADICIONAL_2DA": pd.to_numeric(df_segunda_raw[col_comision_segunda], errors="coerce").fillna(0)
        })
        df_segunda_comision = df_segunda_comision.dropna(subset=["_DNI_CLIENTE_CRUCE"])
        df_segunda_comision["_DNI_CLIENTE_CRUCE"] = df_segunda_comision["_DNI_CLIENTE_CRUCE"].astype(str)
        df_segunda_comision = (
            df_segunda_comision
            .groupby("_DNI_CLIENTE_CRUCE", as_index=False)["_COMISION_ADICIONAL_2DA"]
            .sum()
        )
    else:
        df_segunda_comision = pd.DataFrame(columns=["_DNI_CLIENTE_CRUCE", "_COMISION_ADICIONAL_2DA"])

    # Como base_filtrada viene de la misma base y conserva el índice original, usamos ese índice para traer el DNI CLIENTE exacto.
    base_filtrada = base_filtrada.copy()
    if len(doc_base_full) > 0:
        base_filtrada["_DNI_CLIENTE_CRUCE"] = doc_base_full.reindex(base_filtrada.index)
    else:
        base_filtrada["_DNI_CLIENTE_CRUCE"] = _limpiar_documento_movil(base_filtrada.get("Documento", pd.Series([""] * len(base_filtrada), index=base_filtrada.index)))
    base_filtrada["_DNI_CLIENTE_CRUCE"] = base_filtrada["_DNI_CLIENTE_CRUCE"].astype(str)

    docs_segunda = set(df_segunda_comision["_DNI_CLIENTE_CRUCE"].dropna().astype(str).tolist()) if not df_segunda_comision.empty else set()
    nums_tercera = set(tercera_filtrada["NUMERO_LINEA"].dropna().astype(str).tolist()) if not tercera_filtrada.empty else set()

    base_out = base_filtrada.copy()
    base_out["Etapa"] = "Base Pagados"
    base_out["Orden"] = 1
    base_out["Descripción"] = "Base principal pagada"
    base_out["Coincide Base"] = "SI"
    base_out["Criterio Cruce"] = "Base CLARO_TELETALK_MOVIL"

    segunda_out = base_filtrada[base_filtrada["_DNI_CLIENTE_CRUCE"].astype(str).isin(docs_segunda)].copy()
    if not segunda_out.empty:
        segunda_out = segunda_out.merge(df_segunda_comision, on="_DNI_CLIENTE_CRUCE", how="left")
        segunda_out["_COMISION_ADICIONAL_2DA"] = pd.to_numeric(
            segunda_out["_COMISION_ADICIONAL_2DA"], errors="coerce"
        ).fillna(0)
        # Evita duplicar el monto si el mismo DNI aparece varias veces en la base filtrada.
        segunda_out["_ORDEN_DNI_2DA"] = segunda_out.groupby("_DNI_CLIENTE_CRUCE").cumcount()
        segunda_out["COMISION"] = segunda_out.apply(
            lambda r: r["_COMISION_ADICIONAL_2DA"] if r["_ORDEN_DNI_2DA"] == 0 else 0,
            axis=1
        )
        segunda_out["COMISION ADICIONAL 2DA"] = segunda_out["COMISION"]
    else:
        segunda_out["COMISION ADICIONAL 2DA"] = 0
    segunda_out["Etapa"] = "2da Caída - 3 meses"
    segunda_out["Orden"] = 2
    segunda_out["Descripción"] = "Cliente de la base cuyo DNI CLIENTE cruza con DNI RUC de 2da caída y COMISION > 0"
    segunda_out["Archivo"] = "CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv"
    segunda_out["Coincide Base"] = "SI"
    segunda_out["Criterio Cruce"] = f"{col_doc_base or 'DNI CLIENTE'} vs {col_doc_segunda or 'DNI RUC'} | comisión tomada de CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA"

    # ✅ 3ra caída: se toma el universo de la BASE, pero el mes se controla con FEC ACTIV CTR
    # del archivo CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv. Así el filtro Fecha de Venta
    # sí jala para la tercera caída aunque la fecha de la base sea diferente.
    tercera_out = base[base["NUMERO_LINEA"].astype(str).isin(nums_tercera)].copy()

    if not tercera_out.empty and not tercera_filtrada.empty:
        fechas_tercera = (
            tercera_filtrada[["NUMERO_LINEA", "FECHA_BASE", "_FECHA_BASE_DT", "FECHA_ORIGINAL", "_FECHA_ORIGINAL_DT"]]
            .dropna(subset=["NUMERO_LINEA"])
            .drop_duplicates(subset=["NUMERO_LINEA"], keep="first")
            .rename(columns={
                "FECHA_BASE": "FECHA_BASE_TERCERA",
                "_FECHA_BASE_DT": "_FECHA_BASE_DT_TERCERA",
                "FECHA_ORIGINAL": "FECHA_ORIGINAL_TERCERA",
                "_FECHA_ORIGINAL_DT": "_FECHA_ORIGINAL_DT_TERCERA",
            })
        )
        tercera_out = tercera_out.merge(fechas_tercera, on="NUMERO_LINEA", how="left")
        tercera_out["FECHA_BASE"] = tercera_out["FECHA_BASE_TERCERA"].fillna(tercera_out["FECHA_BASE"])
        tercera_out["FECHA_ORIGINAL"] = tercera_out["FECHA_ORIGINAL_TERCERA"].fillna(tercera_out["FECHA_ORIGINAL"])
        tercera_out["_FECHA_BASE_DT"] = tercera_out["_FECHA_BASE_DT_TERCERA"].fillna(tercera_out["_FECHA_BASE_DT"])
        tercera_out["_FECHA_ORIGINAL_DT"] = tercera_out["_FECHA_ORIGINAL_DT_TERCERA"].fillna(tercera_out["_FECHA_ORIGINAL_DT"])
        tercera_out = tercera_out.drop(columns=[
            "FECHA_BASE_TERCERA", "_FECHA_BASE_DT_TERCERA",
            "FECHA_ORIGINAL_TERCERA", "_FECHA_ORIGINAL_DT_TERCERA"
        ], errors="ignore")

    tercera_out["Etapa"] = "3ra Caída - 6 meses"
    tercera_out["Orden"] = 3
    tercera_out["Descripción"] = "Línea de la base que aparece en MSISDN de 3ra caída filtrada por FEC ACTIV CTR"
    tercera_out["Archivo"] = "CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv"
    tercera_out["Coincide Base"] = "SI"
    tercera_out["Criterio Cruce"] = "TELEFONO vs MSISDN | Fecha de Venta = FEC ACTIV CTR"

    df_all = pd.concat([base_out, segunda_out, tercera_out], ignore_index=True)

    return df_all.reset_index(drop=True)


@st.cache_data(ttl=300)
def obtener_meses_teletalk_movil_caidas():
    base, _, tercera = _cargar_bases_teletalk_por_numero()
    meses = set()

    # Base Pagados / 2da Caída: meses desde la fecha de la base.
    if not base.empty:
        for f in base["_FECHA_BASE_DT"].dropna():
            meses.add(f"{MESES_ES[f.month].capitalize()} {f.year}")

    # 3ra Caída: meses desde FEC ACTIV CTR de CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv.
    if not tercera.empty:
        for f in tercera["_FECHA_BASE_DT"].dropna():
            meses.add(f"{MESES_ES[f.month].capitalize()} {f.year}")

    return ["Todos los meses"] + sorted(
        meses,
        key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0))
    )


def _lineas_etapa(df, etapa):
    if df.empty:
        return 0
    return int((df["Etapa"] == etapa).sum())


def _comision_etapa(df, etapa):
    if df.empty:
        return 0.0
    return float(
        pd.to_numeric(
            df.loc[df["Etapa"] == etapa, "COMISION"],
            errors="coerce"
        ).fillna(0).sum()
    )



def _agregar_lineas_por_cliente_teletalk(df):
    """Agrega cuántas líneas tiene cada cliente dentro de cada etapa.

    Base Pagados: cuenta TELEFONO de CLARO_TELETALK_MOVIL.
    2da Caída: cuenta MSISDN de CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.
    3ra Caída: cuenta MSISDN/NUMERO_LINEA de la tercera caída cuando exista en el detalle.
    """
    if df.empty:
        df["Lineas Cliente"] = 0
        return df

    base = df.copy()
    for col in ["Etapa", "Documento", "NUMERO_LINEA"]:
        if col not in base.columns:
            base[col] = ""

    base["Documento"] = base["Documento"].fillna("").astype(str).str.strip()
    base["NUMERO_LINEA"] = base["NUMERO_LINEA"].fillna("").astype(str).str.strip()

    # Conteo estándar por etapa usando el número que ya trae cada fila.
    conteo_general = (
        base[(base["Documento"] != "") & (base["NUMERO_LINEA"] != "")]
        .drop_duplicates(subset=["Etapa", "Documento", "NUMERO_LINEA"])
        .groupby(["Etapa", "Documento"], as_index=False)["NUMERO_LINEA"]
        .nunique()
        .rename(columns={"NUMERO_LINEA": "Lineas Cliente"})
    )

    base = base.merge(conteo_general, on=["Etapa", "Documento"], how="left")
    base["Lineas Cliente"] = pd.to_numeric(base["Lineas Cliente"], errors="coerce").fillna(0).astype(int)

    # Regla especial para 2da caída: el conteo de líneas debe venir del MSISDN del archivo segunda caída.
    try:
        df_segunda_raw = cargar_csv("CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv")
        if not df_segunda_raw.empty:
            col_doc_seg = encontrar_columna(df_segunda_raw, ["DNI RUC", "DNI", "RUC", "DOCUMENTO", "NRO DOCUMENTO"])
            col_msidn_seg = encontrar_columna(df_segunda_raw, ["MSISDN", "TELEFONO", "TELÉFONO", "Telefono", "Teléfono", "NUMERO", "NÚMERO"])
            col_com_seg = encontrar_columna(df_segunda_raw, [
                "COMISION", "COMISIÓN", "Comision", "Comisión", "comision", "comisión",
                "COMISION TOTAL", "COMISIÓN TOTAL", "Comision Total", "MONTO"
            ])
            if col_doc_seg and col_msidn_seg and col_com_seg:
                temp = df_segunda_raw.copy()
                temp["Documento"] = _limpiar_documento_movil(temp[col_doc_seg]).astype(str)
                temp["MSISDN_LIMPIO"] = _limpiar_numero_movil(temp[col_msidn_seg]).astype(str)
                temp["COMISION_NUM"] = pd.to_numeric(temp[col_com_seg], errors="coerce").fillna(0)
                temp = temp[(temp["COMISION_NUM"] > 0) & (temp["Documento"] != "") & (temp["MSISDN_LIMPIO"] != "")]
                conteo_segunda = (
                    temp.drop_duplicates(subset=["Documento", "MSISDN_LIMPIO"])
                    .groupby("Documento", as_index=False)["MSISDN_LIMPIO"]
                    .nunique()
                    .rename(columns={"MSISDN_LIMPIO": "Lineas Cliente Segunda"})
                )
                if not conteo_segunda.empty:
                    base = base.merge(conteo_segunda, on="Documento", how="left")
                    mask_seg = base["Etapa"].eq("2da Caída - 3 meses")
                    base.loc[mask_seg, "Lineas Cliente"] = pd.to_numeric(
                        base.loc[mask_seg, "Lineas Cliente Segunda"], errors="coerce"
                    ).fillna(base.loc[mask_seg, "Lineas Cliente"]).astype(int)
                    base = base.drop(columns=["Lineas Cliente Segunda"], errors="ignore")
    except Exception:
        pass

    return base

def _resumen_etapas_teletalk(df):
    cols = ["Etapa", "Líneas", "Comision", "% Sobre Base"]
    if df.empty:
        return pd.DataFrame(columns=cols)

    base_lineas = _lineas_etapa(df, "Base Pagados")
    segunda_lineas = _lineas_etapa(df, "2da Caída - 3 meses")
    tercera_lineas = _lineas_etapa(df, "3ra Caída - 6 meses")

    def pct_sobre_base(valor):
        if base_lineas <= 0:
            return "0.00%"
        return f"{(valor / base_lineas * 100):.2f}%"

    resumen = pd.DataFrame([
        {
            "Etapa": "Base Pagados",
            "Líneas": base_lineas,
            "Comision": _comision_etapa(df, "Base Pagados"),
            "% Sobre Base": "100.00%" if base_lineas > 0 else "0.00%",
        },
        {
            "Etapa": "2da Caída - 3 meses",
            "Líneas": segunda_lineas,
            "Comision": _comision_etapa(df, "2da Caída - 3 meses"),
            "% Sobre Base": pct_sobre_base(segunda_lineas),
        },
        {
            "Etapa": "3ra Caída - 6 meses",
            "Líneas": tercera_lineas,
            "Comision": _comision_etapa(df, "3ra Caída - 6 meses"),
            "% Sobre Base": pct_sobre_base(tercera_lineas),
        },
    ])

    return resumen[cols]


def _excel_bytes_teletalk_etapa(df_export):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Detalle")
    output.seek(0)
    return output.getvalue()


def _detalle_clientes_por_etapa_teletalk(df, etapa):
    cols_salida = ["Cliente", "Documento", "Lineas Cliente", "COMISION"]
    if df.empty:
        return pd.DataFrame(columns=cols_salida)

    base = df[df["Etapa"] == etapa].copy()
    if base.empty:
        return pd.DataFrame(columns=cols_salida)

    base = _agregar_lineas_por_cliente_teletalk(base)

    for col in ["Cliente", "Documento", "Lineas Cliente", "COMISION"]:
        if col not in base.columns:
            base[col] = 0 if col in ["Lineas Cliente", "COMISION"] else ""

    detalle = base[["Cliente", "Documento", "Lineas Cliente", "COMISION"]].copy()
    detalle["Cliente"] = detalle["Cliente"].fillna("Sin Datos").astype(str).str.strip().replace("", "Sin Datos")
    detalle["Documento"] = detalle["Documento"].fillna("").astype(str).str.strip()
    detalle["Lineas Cliente"] = pd.to_numeric(detalle["Lineas Cliente"], errors="coerce").fillna(0).astype(int)
    detalle["COMISION"] = pd.to_numeric(detalle["COMISION"], errors="coerce").fillna(0)

    # Cliente único: suma comisión y conserva el mayor conteo de líneas calculado para ese DNI.
    detalle = (
        detalle.groupby(["Cliente", "Documento"], as_index=False)
        .agg({"Lineas Cliente": "max", "COMISION": "sum"})
        .sort_values(["Lineas Cliente", "COMISION"], ascending=[False, False])
        .reset_index(drop=True)
    )
    return detalle[cols_salida]

def mostrar_resumen_etapas_expandible_teletalk(df, resumen, filtro_mes):
    etapas = ["Base Pagados", "2da Caída - 3 meses", "3ra Caída - 6 meses"]

    for etapa in etapas:
        fila = resumen[resumen["Etapa"] == etapa]
        cantidad = int(fila["Líneas"].iloc[0]) if not fila.empty else 0
        comision = float(pd.to_numeric(fila["Comision"], errors="coerce").fillna(0).iloc[0]) if not fila.empty else 0.0
        pct = str(fila["% Sobre Base"].iloc[0]) if not fila.empty else "0.00%"

        with st.expander(f"➕ {etapa} | {cantidad:,} clientes | {formatear_moneda(comision)} | {pct}", expanded=False):
            detalle = _detalle_clientes_por_etapa_teletalk(df, etapa)

            if detalle.empty:
                st.warning("Sin clientes para esta etapa con los filtros seleccionados.")
                continue

            detalle_show = detalle.copy()
            detalle_show["COMISION"] = detalle_show["COMISION"].map(formatear_moneda)
            st.dataframe(detalle_show, use_container_width=True, height=320)

            archivo_etapa = (
                etapa.lower()
                .replace(" ", "_")
                .replace("í", "i")
                .replace("á", "a")
                .replace("é", "e")
                .replace("ó", "o")
                .replace("ú", "u")
                .replace("-", "")
            )
            archivo_mes = filtro_mes.replace(" ", "_")

            st.download_button(
                label=f"⬇️ Exportar {etapa} en Excel",
                data=_excel_bytes_teletalk_etapa(detalle),
                file_name=f"teletalk_movil_{archivo_etapa}_{archivo_mes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_excel_tt_movil_{archivo_etapa}_{archivo_mes}"
            )


def _ranking_asesores_teletalk(df):
    cols = ["Rank", "ASESOR", "Líneas", "Comision", "% Participación"]
    if df.empty:
        return pd.DataFrame(columns=cols)

    base = df.copy()
    r = (
        base.groupby("ASESOR", as_index=False)
        .agg(
            **{
                "Líneas": ("Etapa", "count"),
                "Comision": ("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum())
            }
        )
        .sort_values(["Líneas", "Comision"], ascending=[False, False])
        .reset_index(drop=True)
    )

    if r.empty:
        return pd.DataFrame(columns=cols)

    r.insert(0, "Rank", r.index + 1)
    total = int(r["Líneas"].sum())
    r["% Participación"] = (r["Líneas"] / total * 100).round(2).astype(str) + "%" if total > 0 else "0%"

    total_row = pd.DataFrame([{
        "Rank": "TOTAL",
        "ASESOR": "",
        "Líneas": total,
        "Comision": float(r["Comision"].sum()),
        "% Participación": "100.00%" if total > 0 else "0%"
    }])

    return pd.concat([r[cols], total_row[cols]], ignore_index=True)


def _kpi_movil_teletalk_card(col, titulo, valor, subtitulo, color="#6d0b8c"):
    with col:
        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,.96);
                padding:18px;
                border-radius:18px;
                border:2px solid {color};
                text-align:center;
                min-height:104px;
                box-shadow:0 12px 28px rgba(0,0,0,.08);
                margin-bottom:10px;">
                <div style="font-size:11px;font-weight:900;color:#4b5563;text-transform:uppercase;letter-spacing:.08em;">
                    {titulo}
                </div>
                <div style="font-size:30px;font-weight:900;color:{color};line-height:1.1;margin-top:6px;">
                    {valor}
                </div>
                <div style="font-size:11px;color:#6b7280;margin-top:4px;">
                    {subtitulo}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def _grafico_resumen_etapa_gerencial(resumen):
    import altair as alt

    chart_df = resumen.copy()
    chart_df["Líneas"] = pd.to_numeric(chart_df["Líneas"], errors="coerce").fillna(0)

    base_val = int(chart_df.loc[chart_df["Etapa"] == "Base Pagados", "Líneas"].sum())
    chart_df["% Num"] = chart_df["Líneas"].apply(
        lambda v: (v / base_val * 100) if base_val > 0 else 0
    )
    chart_df.loc[chart_df["Etapa"] == "Base Pagados", "% Num"] = 100 if base_val > 0 else 0

    chart_df["Etiqueta"] = chart_df.apply(
        lambda r: f"{int(r['Líneas']):,} líneas · {r['% Num']:.2f}%",
        axis=1
    )

    chart_df["Orden"] = chart_df["Etapa"].map({
        "Base Pagados": 1,
        "2da Caída - 3 meses": 2,
        "3ra Caída - 6 meses": 3
    })

    chart_df["Color"] = chart_df["Etapa"].map({
        "Base Pagados": "Base",
        "2da Caída - 3 meses": "3 meses",
        "3ra Caída - 6 meses": "6 meses"
    })

    barras = (
        alt.Chart(chart_df)
        .mark_bar(
            cornerRadiusTopRight=12,
            cornerRadiusBottomRight=12,
            height=42
        )
        .encode(
            y=alt.Y(
                "Etapa:N",
                sort=alt.SortField("Orden", order="ascending"),
                title="",
                axis=alt.Axis(labelFontSize=13, labelFontWeight="bold")
            ),
            x=alt.X(
                "Líneas:Q",
                title="Líneas",
                axis=alt.Axis(labelFontSize=12, titleFontSize=12, grid=True)
            ),
            color=alt.Color(
                "Color:N",
                scale=alt.Scale(
                    domain=["Base", "3 meses", "6 meses"],
                    range=["#059669", "#d97706", "#dc2626"]
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip("Etapa:N", title="Etapa"),
                alt.Tooltip("Líneas:Q", title="Líneas", format=",.0f"),
                alt.Tooltip("% Num:Q", title="% sobre base", format=".2f"),
                alt.Tooltip("Comision:Q", title="Comisión", format=",.2f"),
            ]
        )
    )

    etiquetas = (
        alt.Chart(chart_df)
        .mark_text(
            align="left",
            baseline="middle",
            dx=8,
            fontSize=13,
            fontWeight="bold",
            color="#111827"
        )
        .encode(
            y=alt.Y("Etapa:N", sort=alt.SortField("Orden", order="ascending"), title=""),
            x=alt.X("Líneas:Q"),
            text="Etiqueta:N"
        )
    )

    grafico = (
        (barras + etiquetas)
        .properties(
            height=285,
            title="Recuperación móvil Teletalk sobre la base por número"
        )
        .configure_title(
            fontSize=18,
            fontWeight="bold",
            color="#111827",
            anchor="start"
        )
        .configure_axis(
            gridColor="#e5e7eb",
            domain=False,
            tickColor="#e5e7eb"
        )
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(grafico, use_container_width=True)


def mostrar_detalle_movil_general():
    color_titulo = "#70008f"
    color_borde = "#6d0b8c"

    set_bg(img_caratula)

    st.markdown(
        f'<div style="color:{color_titulo};font-size:36px;font-weight:900;margin-bottom:4px;">'
        f'Detalle MÓVIL TELETALK</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="color:{color_titulo};font-weight:800;font-size:16px;margin-bottom:16px;">'
        f'Cruce real: Base pagados + 2da caída por DNI; 3ra caída filtrada por FEC ACTIV CTR</div>',
        unsafe_allow_html=True
    )
    st.write("---")

    meses = obtener_meses_teletalk_movil_caidas()

    f1, f2, f3 = st.columns([1.2, 1.2, 1.4])
    with f1:
        filtro_mes = st.selectbox("Fecha de Venta", meses, key="tt_movil_caidas_mes")
    with f2:
        filtro_etapa = st.selectbox(
            "Etapa",
            ["Todas", "Base Pagados", "2da Caída - 3 meses", "3ra Caída - 6 meses"],
            key="tt_movil_caidas_etapa"
        )

    with st.spinner("Cargando base y cruzando TELEFONO contra MSISDN..."):
        df = construir_detalle_movil_teletalk_caidas(filtro_mes)

    if df.empty:
        st.warning(
            "No se encontraron datos. Verifica que estén estos archivos en la carpeta del app.py: "
            "CLARO_TELETALK_MOVIL.csv, CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA.csv y "
            "CLARO_TELETALK_MOVIL_TERCERA_CAIDA.csv"
        )
        return

    if df["NUMERO_LINEA"].isna().any():
        st.warning(
            "Hay filas sin número. La 3ra caída cruza TELEFONO vs MSISDN y se filtra por FEC ACTIV CTR; la 2da caída cruza DNI CLIENTE vs DNI RUC y solo cuenta COMISION > 0."
        )

    with f3:
        filtro_asesor = st.selectbox(
            "Asesor",
            ["Todos"] + sorted(df["ASESOR"].fillna("Sin Asesor").astype(str).unique().tolist()),
            key="tt_movil_caidas_asesor"
        )

    df_filtrado = df.copy()

    if filtro_etapa != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Etapa"] == filtro_etapa].copy()

    if filtro_asesor != "Todos":
        df_filtrado = df_filtrado[df_filtrado["ASESOR"] == filtro_asesor].copy()

    base_lineas = _lineas_etapa(df_filtrado, "Base Pagados")
    segunda_lineas = _lineas_etapa(df_filtrado, "2da Caída - 3 meses")
    tercera_lineas = _lineas_etapa(df_filtrado, "3ra Caída - 6 meses")
    comision_total = pd.to_numeric(df_filtrado["COMISION"], errors="coerce").fillna(0).sum()

    st.markdown("### Resumen Ejecutivo")
    k1, k2, k3, k4 = st.columns(4)
    _kpi_movil_teletalk_card(k1, "Base Pagados", f"{base_lineas:,}", "Total líneas de la base", "#059669")
    _kpi_movil_teletalk_card(k2, "2da Caída", f"{segunda_lineas:,}", "DNI cruza; comisión 2da", "#d97706")
    _kpi_movil_teletalk_card(k3, "3ra Caída", f"{tercera_lineas:,}", "Base que cruzó con MSISDN 6M", "#dc2626")
    _kpi_movil_teletalk_card(k4, "Comisión Total", formatear_moneda(comision_total), "Base + adicional 2da/3ra", color_borde)

    st.write("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resumen por Etapa",
        "📋 Ver 2da y 3ra Caída",
        "🏆 Ranking Asesores",
        "⬇️ Descargar Base"
    ])

    with tab1:
        st.markdown("#### 📊 Resumen Ejecutivo por Etapa")
        st.caption("Cruce correcto: Base pagados desde CLARO_TELETALK_MOVIL. La 2da caída cruza DNI CLIENTE de la base contra DNI RUC de segunda caída y su comisión se toma desde CLARO_TELETALK_MOVIL_SEGUNDA_CAIDA. La 3ra caída se mantiene por TELEFONO vs MSISDN y el filtro Fecha de Venta usa FEC ACTIV CTR.")

        resumen = _resumen_etapas_teletalk(df_filtrado)

        if resumen.empty:
            st.warning("No hay datos para mostrar en el resumen por etapa.")
        else:
            resumen_show = resumen.copy()
            resumen_show["Comision"] = pd.to_numeric(
                resumen_show["Comision"], errors="coerce"
            ).fillna(0).map(formatear_moneda)

            st.dataframe(
                resumen_show,
                use_container_width=True,
                height=180
            )

            st.markdown("#### ➕ Detalle de clientes por etapa")
            st.caption("Abre cada etapa para ver Nombre, DNI, cuántas líneas tiene el cliente y Comisión. También puedes exportar cada etapa en Excel.")
            mostrar_resumen_etapas_expandible_teletalk(df_filtrado, resumen, filtro_mes)

            try:
                _grafico_resumen_etapa_gerencial(resumen)
            except Exception as e:
                st.warning(f"No se pudo mostrar el gráfico gerencial: {e}")

    with tab2:
        st.markdown("#### Vista directa de Segunda Caída y Tercera Caída")
        st.caption("Se muestran líneas de la base que cruzaron; en 2da caída la comisión es el pago adicional tomado del archivo SEGUNDA_CAIDA.")
        df_caidas = df_filtrado[df_filtrado["Etapa"].isin(["2da Caída - 3 meses", "3ra Caída - 6 meses"])].copy()

        if df_caidas.empty:
            st.warning("No hay datos de segunda o tercera caída con los filtros seleccionados.")
        else:
            cols = [
                "Etapa", "FECHA_BASE", "ASESOR", "Cliente", "Documento", "NUMERO_LINEA",
                "Departamento", "Transaccion", "Plan", "CF",
                "DIAS PORTADAS", "COMISION", "COMISION ADICIONAL 2DA", "Archivo"
            ]
            for c in cols:
                if c not in df_caidas.columns:
                    df_caidas[c] = ""
            df_show = df_caidas[cols].copy()
            df_show["COMISION"] = pd.to_numeric(df_show["COMISION"], errors="coerce").fillna(0).map(formatear_moneda)
            if "COMISION ADICIONAL 2DA" in df_show.columns:
                df_show["COMISION ADICIONAL 2DA"] = pd.to_numeric(df_show["COMISION ADICIONAL 2DA"], errors="coerce").fillna(0).map(formatear_moneda)
            st.dataframe(df_show, use_container_width=True, height=500)

            st.download_button(
                "⬇️ Descargar solo 2da y 3ra caída",
                data=df_caidas.drop(columns=["_FECHA_ORIGINAL_DT", "_FECHA_BASE_DT"], errors="ignore").to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"teletalk_movil_2da_3ra_caida_{filtro_mes.replace(' ', '_')}.csv",
                mime="text/csv",
                key="dl_tt_movil_2da_3ra"
            )

    with tab3:
        st.markdown("#### Ranking de asesores por líneas")
        ranking = _ranking_asesores_teletalk(df_filtrado)
        if ranking.empty:
            st.warning("No hay datos para ranking.")
        else:
            ranking_show = ranking.copy()
            ranking_show["Comision"] = ranking_show["Comision"].apply(
                lambda x: formatear_moneda(x) if isinstance(x, (int, float)) else x
            )
            st.dataframe(ranking_show, use_container_width=True, height=420)

    with tab4:
        st.markdown("#### Descargar base completa filtrada")
        df_export = df_filtrado.drop(columns=["_FECHA_ORIGINAL_DT", "_FECHA_BASE_DT"], errors="ignore").copy()
        df_show = df_export.copy()
        if "COMISION" in df_show.columns:
            df_show["COMISION"] = pd.to_numeric(df_show["COMISION"], errors="coerce").fillna(0).map(formatear_moneda)
        st.dataframe(df_show, use_container_width=True, height=420)

        st.download_button(
            "⬇️ Descargar base filtrada TELETALK móvil",
            data=df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            file_name=f"detalle_movil_teletalk_cruce_numero_{filtro_mes.replace(' ', '_')}.csv",
            mime="text/csv",
            key="dl_tt_movil_base_filtrada"
        )


# =========================================================
# 11. SIDEBAR / NAVEGACIÓN
# =========================================================
OPCIONES_FIJA = [
    "Inicio: Reporte Comparativo","Detalle Fija General",
    "D&C Factor Instalación","D&C Factor F. Venta","D&C IAE ASESOR",
    "Teletalk Factor Instalación","Teletalk Factor F. Venta","Teletalk IAE ASESOR",
]
OPCIONES_MOVIL = [
    "Inicio: Reporte Comparativo MOVIL","Detalle Móvil General",
    "D&C Factor F. Venta MOVIL","D&C IAE ASESOR MOVIL",
    "Teletalk Factor F. Venta MOVIL","Teletalk IAE ASESOR MOVIL",
]
SEP_FIJA="📡 FIJA"; SEP_MOVIL="📱 MÓVIL"
SEPARADORES = {SEP_FIJA, SEP_MOVIL}
todas_opciones = [SEP_FIJA] + OPCIONES_FIJA + [SEP_MOVIL] + OPCIONES_MOVIL

idx_sep_fija  = 0
idx_sep_movil = len(OPCIONES_FIJA) + 1

st.markdown(f"""<style>
div[data-testid="stSidebarNav"] {{display:none}}
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_fija+1}),
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_movil+1}) {{
    pointer-events:none; cursor:default; margin-top:14px; margin-bottom:2px; }}
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_fija+1}) input,
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_movil+1}) input {{ display:none !important; }}
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_fija+1}) div[data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_movil+1}) div[data-testid="stMarkdownContainer"] p {{
    font-weight:900 !important; font-size:15px !important; color:#1e3a5f !important;
    letter-spacing:0.05em; text-transform:uppercase; }}
</style>""", unsafe_allow_html=True)

st.sidebar.title("MENU DE REPORTES")
seleccion = st.sidebar.radio("MENU DE REPORTES", todas_opciones, key="radio_unico", label_visibility="collapsed")

if seleccion in SEPARADORES:
    seleccion = st.session_state.get("ultima_seleccion", "Inicio: Reporte Comparativo")
else:
    st.session_state["ultima_seleccion"] = seleccion

opcion       = seleccion if seleccion in OPCIONES_FIJA  else "Inicio: Reporte Comparativo"
opcion_movil = seleccion if seleccion in OPCIONES_MOVIL else "Inicio: Reporte Comparativo MOVIL"
seccion      = "movil" if seleccion in OPCIONES_MOVIL else "fija"

with st.sidebar.expander("🔍 Ver columnas de CSVs"):
    for nombre in ["FIJA_DC.csv","FIJA_TELETALK.csv","CLARO_DC_FIJA.csv","CLARO_TELETALK_FIJA.csv","CLARO_DC_MOVIL.csv","CLARO_TELETALK_MOVIL.csv"]:
        df_test = cargar_csv(nombre)
        if not df_test.empty: st.write(f"**{nombre}:**"); st.write(list(df_test.columns))
        else: st.write(f"**{nombre}:** ❌ no cargado")

# =========================================================
# 12. VISTAS FIJA
# =========================================================
if seccion == "fija":

    if opcion == "Inicio: Reporte Comparativo":
        set_bg(img_caratula)
        st.markdown('<div class="main-title">REPORTE COMPARATIVO</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">D&C DIGITAL GROUP <span style="color:black">vs</span> <span style="color:#70008f">TELETALK CONTACT CENTER</span></div>', unsafe_allow_html=True)
        col_dc, col_filtros, col_tt = st.columns([1,1.2,1])
        with col_filtros:
            st.markdown('<div class="block-filter">', unsafe_allow_html=True)
            sel_inst = st.selectbox("FECHA INSTALACIÓN", obtener_meses_fija("FECHA INSTALACION"), key="fija_sel_inst")
            sel_gene = st.selectbox("FECHA DE VENTA", obtener_meses_fija("FECHA GENERACION"), key="fija_sel_gene")
            st.markdown('</div>', unsafe_allow_html=True)
        v_dc, c_dc = obtener_metricas_fija("dbo.CLARO_DC_FIJA", sel_inst, sel_gene)
        v_tt, c_tt = obtener_metricas_fija("dbo.CLARO_TELETALK_FIJA", sel_inst, sel_gene)
        with col_dc:
            st.markdown(f'<div class="kpi-wrapper"><div class="box-header-dc">D&C DIGITAL GROUP</div><div class="data-card-dc"><span class="label">Acumulado soles</span><span class="value">{formatear_moneda(c_dc)}</span></div><div class="data-card-dc"><span class="label">Ventas totales</span><span class="value">{v_dc:,}</span></div></div>', unsafe_allow_html=True)
        with col_tt:
            st.markdown(f'<div class="kpi-wrapper"><div class="box-header-tt">TELETALK CONTACT CENTER</div><div class="data-card-tt"><span class="label">Acumulado soles</span><span class="value">{formatear_moneda(c_tt)}</span></div><div class="data-card-tt"><span class="label">Ventas totales</span><span class="value">{v_tt:,}</span></div></div>', unsafe_allow_html=True)

    elif opcion == "Detalle Fija General":
        mostrar_detalle_fija_general()

    elif opcion == "D&C Factor Instalación":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C Factor Instalación</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-dc">AVANCE DE FACTOR ANUAL POR FECHA DE INSTALACIÓN</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="dc_fi_inst")
        mostrar_factor_fija("dbo.CLARO_DC_FIJA", "FECHA INSTALACION", filtro, "dc")

    elif opcion == "D&C Factor F. Venta":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C Factor F. Venta</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-dc">AVANCE DE FACTOR ANUAL POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Venta", obtener_meses_fija("FECHA GENERACION"), key="dc_fv_gene")
        mostrar_factor_fija("dbo.CLARO_DC_FIJA", "FECHA GENERACION", filtro, "dc")

    elif opcion == "D&C IAE ASESOR":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C IAE ASESOR</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-dc">BASE FIJA_DC · ASESOR = CREADOR · CRUCE SOT CON CLARO_DC_FIJA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="dc_iae_inst")
        mostrar_iae_asesor_fija_develz("[DATA DEVELZ].dbo.FIJA_DC","dbo.CLARO_DC_FIJA","D&C",filtro,"dc_iae_asesor","dc")

    elif opcion == "Teletalk Factor Instalación":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor Instalación</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE INSTALACIÓN</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="tt_fi_inst")
        mostrar_factor_fija("dbo.CLARO_TELETALK_FIJA","FECHA INSTALACION",filtro,"tt")

    elif opcion == "Teletalk Factor F. Venta":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor F. Venta</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Venta", obtener_meses_fija("FECHA GENERACION"), key="tt_fv_gene")
        mostrar_factor_fija("dbo.CLARO_TELETALK_FIJA","FECHA GENERACION",filtro,"tt")

    elif opcion == "Teletalk IAE ASESOR":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk IAE ASESOR</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">BASE FIJA_TELETALK · ASESOR = CREADOR · CRUCE SOT CON CLARO_TELETALK_FIJA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="tt_iae_inst")
        mostrar_iae_asesor_fija_develz("[DATA DEVELZ].dbo.FIJA_TELETALK","dbo.CLARO_TELETALK_FIJA","Teletalk",filtro,"tt_iae_asesor","tt")

# =========================================================
# 13. VISTAS MÓVIL
# =========================================================
else:

    if opcion_movil == "Detalle Móvil General":
        mostrar_detalle_movil_general()

    elif opcion_movil == "Inicio: Reporte Comparativo MOVIL":
        set_bg(img_caratula)
        st.markdown('<div class="main-title">REPORTE COMPARATIVO MÓVIL</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">D&C DIGITAL GROUP <span style="color:black">vs</span> <span style="color:#70008f">TELETALK CONTACT CENTER</span></div>', unsafe_allow_html=True)

        df_dc_tmp = preparar_fechas_movil(cargar_csv("CLARO_DC_MOVIL.csv"))
        meses_carga_dc = (obtener_meses_movil("FECHA CARGA",["CLARO_DC_MOVIL.csv"])
            if "FECHA CARGA" in df_dc_tmp.columns and df_dc_tmp["FECHA CARGA"].notna().any()
            else obtener_meses_movil("FECHA OPERACION",["CLARO_DC_MOVIL.csv"]))

        todos_op = sorted(set(obtener_meses_movil("FECHA OPERACION",["CLARO_DC_MOVIL.csv"]) +
            obtener_meses_movil("FECHA OPERACION",["CLARO_TELETALK_MOVIL.csv"])) - {"Todos los meses"},
            key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0)))
        todos_ca = sorted(set(meses_carga_dc + obtener_meses_movil("FECHA CARGA",["CLARO_TELETALK_MOVIL.csv"])) - {"Todos los meses"},
            key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0)))

        col_dc, col_filtros, col_tt = st.columns([1,1.2,1])
        with col_filtros:
            st.markdown('<div class="block-filter">', unsafe_allow_html=True)
            sel_op = st.selectbox("FECHA DE VENTA",     ["Todos los meses"]+todos_op, key="movil_comp_fecha_operacion")
            sel_ca = st.selectbox("FECHA DE ACTIVACION", ["Todos los meses"]+todos_ca, key="movil_comp_fecha_carga")
            st.markdown('</div>', unsafe_allow_html=True)

        def filtrar_cmp(df, f_op, f_ca, respaldo=False):
            df = preparar_fechas_movil(df.copy())
            if f_op != "Todos los meses" and "FECHA OPERACION" in df.columns:
                df = filtrar_por_mes_anio(df, "FECHA OPERACION", f_op)
            if f_ca != "Todos los meses":
                if "FECHA CARGA" in df.columns and df["FECHA CARGA"].notna().any():
                    df = filtrar_por_mes_anio(df, "FECHA CARGA", f_ca)
                elif respaldo and "FECHA OPERACION" in df.columns:
                    df = filtrar_por_mes_anio(df, "FECHA OPERACION", f_ca)
            return df

        df_dc_c = filtrar_cmp(get_tabla("dbo.CLARO_DC_MOVIL"), sel_op, sel_ca, respaldo=True)
        df_tt_c = filtrar_cmp(get_tabla("dbo.CLARO_TELETALK_MOVIL"), sel_op, sel_ca)

        def kpi_movil(df):
            tr = df.get("TRANSACCION", pd.Series([""] * len(df))).fillna("").astype(str)
            p = int(_es_portabilidad_movil(tr).sum()); a = int(_es_alta_movil(tr).sum())
            return p+a, p, a, float(obtener_comision_movil(df).sum()) if not df.empty else 0.0

        t_dc,p_dc,a_dc,c_dc = kpi_movil(df_dc_c)
        t_tt,p_tt,a_tt,c_tt = kpi_movil(df_tt_c)

        with col_dc:
            st.markdown(f'<div class="kpi-wrapper"><div class="box-header-dc">D&C DIGITAL GROUP</div><div class="data-card-dc"><span class="label">Comisión pagada</span><span class="value">{formatear_moneda(c_dc)}</span></div><div class="data-card-dc"><span class="label">Total ventas</span><span class="value">{t_dc:,}</span></div><div class="data-card-dc"><span class="label">Portabilidades</span><span class="value">{p_dc:,}</span></div><div class="data-card-dc"><span class="label">Altas nuevas</span><span class="value">{a_dc:,}</span></div></div>', unsafe_allow_html=True)
        with col_tt:
            st.markdown(f'<div class="kpi-wrapper"><div class="box-header-tt">TELETALK CONTACT CENTER</div><div class="data-card-tt"><span class="label">Comisión pagada</span><span class="value">{formatear_moneda(c_tt)}</span></div><div class="data-card-tt"><span class="label">Total ventas</span><span class="value">{t_tt:,}</span></div><div class="data-card-tt"><span class="label">Portabilidades</span><span class="value">{p_tt:,}</span></div><div class="data-card-tt"><span class="label">Altas nuevas</span><span class="value">{a_tt:,}</span></div></div>', unsafe_allow_html=True)

    elif opcion_movil == "D&C Factor F. Venta MOVIL":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C Factor F. Venta MÓVIL</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-dc">AVANCE POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Venta", obtener_meses_movil("FECHA OPERACION",["CLARO_DC_MOVIL.csv"]), key="dc_movil_fv")
        mostrar_factor_movil("dbo.CLARO_DC_MOVIL","FECHA OPERACION",filtro,"dc")

    elif opcion_movil == "D&C IAE ASESOR MOVIL":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C IAE ASESOR MÓVIL</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Operación", obtener_meses_movil("FECHA OPERACION",["CLARO_DC_MOVIL.csv"]), key="dc_movil_iae")
        mostrar_iae_movil("dbo.CLARO_DC_MOVIL","FECHA OPERACION",filtro,"dc_movil_iae_asesor","dc")

    elif opcion_movil == "Teletalk Factor F. Venta MOVIL":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor F. Venta MÓVIL</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Venta", obtener_meses_movil("FECHA OPERACION",["CLARO_TELETALK_MOVIL.csv"]), key="tt_movil_fv")
        mostrar_factor_movil("dbo.CLARO_TELETALK_MOVIL","FECHA OPERACION",filtro,"tt")

    elif opcion_movil == "Teletalk IAE ASESOR MOVIL":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk IAE ASESOR MÓVIL</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Carga", obtener_meses_movil("FECHA CARGA",["CLARO_TELETALK_MOVIL.csv"]), key="tt_movil_iae")
        mostrar_iae_movil("dbo.CLARO_TELETALK_MOVIL","FECHA CARGA",filtro,"tt_movil_iae_asesor","tt")