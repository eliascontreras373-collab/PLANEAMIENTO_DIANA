import streamlit as st
import pandas as pd
import base64
import os

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
        mime = "image/jpeg" if ext in ["jpg","jpeg"] else "image/png"
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
    "dbo.CLARO_DC_FIJA":       "CLARO_DC_FIJA.csv",
    "dbo.CLARO_TELETALK_FIJA": "CLARO_TELETALK_FIJA.csv",
    "dbo.CLARO_DC_MOVIL":      "CLARO_DC_MOVIL.csv",
    "dbo.CLARO_TELETALK_MOVIL":"CLARO_TELETALK_MOVIL.csv",
    "[DATA DEVELZ].dbo.FIJA_DC":      "FIJA_DC.csv",
    "[DATA DEVELZ].dbo.FIJA_TELETALK":"FIJA_TELETALK.csv",
}

# Mapa TIPIS → ESTADO OPERATIVO (basado en la tabla de la imagen)
TIPIS_ESTADO_MAP = {
    "ATENDIDA/CONFORME":           "Conforme",
    "CONFORME PODIO":              "Conforme",
    "ATENDIDA - REASIGNACION":     "Conforme",
    "CONFORME":                    "Conforme",
    "ATENDIDA/OBSERVADO":          "Conforme",
    "AUDIO LOTEADO":               "Conforme",
    "CONFORME - REASIGNACION":     "Conforme",
    "AUDIO KO":                    "1era Caída",
    "SOT CON OTRO DAC":            "1era Caída",
    "SEC SIN CORRECCIÓN":          "1era Caída",
    "SEC SIN CORRECCION":          "1era Caída",
    "OTROS":                       "1era Caída",
    "EDIFICIO NO LIBERADO PC":     "1era Caída",
    "SIN COBERTURA PC":            "1era Caída",
    "FICHA DUPLICADA":             "1era Caída",
    "SEC CON EXCLUSIVIDAD":        "1era Caída",
    "NO ADJUNTA SUSTENTO":         "1era Caída",
    "NO ENVIA SUSTENTO":           "1era Caída",
    "VENTA CARRUSEL":              "1era Caída",
    "DIRECCIÓN CON SERVICIO DE BAJA":"1era Caída",
    "DIRECCION CON SERVICIO DE BAJA":"1era Caída",
    "FACILIDADES TECNICAS":        "2da Caída",
    "CLIENTE NO DESEA":            "2da Caída",
    "FALTA CONTACTO":              "2da Caída",
    "CLIENTE NO CALIFICA":         "2da Caída",
    "PRUEBA - CANCELADA":          "2da Caída",
    "DIRECCION INCORRECTA":        "2da Caída",
    "DIRECCIÓN INCORRECTA":        "2da Caída",
    "MALA OFERTA":                 "2da Caída",
    "RED SATURADA":                "2da Caída",
    "FRAUDE":                      "2da Caída",
    "VIAJE O MUDANZA":             "2da Caída",
    "CONTRA OFERTA":               "2da Caída",
    "FALTA INFRAESTRUCTURA":       "2da Caída",
    "EDIFICIO NO LIBERADO":        "2da Caída",
    "EJECUCION - AUDIO LOTEADO":   "Ejecución",
    "EJECUCION - AUDIO CONFORME":  "Ejecución",
    "PENDIENTE AUDIO OK":          "Ejecución",
    "EJECUCION":                   "Ejecución",
    "EJECUCION - SIN AUDIO":       "Ejecución",
    "PENDIENTE SOT":               "Ejecución",
    "PENDIENTE AUDIO KO":          "Ejecución",
    "EJECUCION - AUDIO OBSERVADO": "Ejecución",
    "PENDIENTE PRE - AUDITORIA":   "Ejecución",
    "EJECUCION - REASIGNACION":    "Ejecución",
    "EJECUCION - AUDITADO":        "Ejecución",
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

def get_tabla(nombre): return cargar_csv(CSV_MAP.get(nombre, nombre.split(".")[-1]+".csv"))

def preparar_fechas_fija(df):
    for col in ["FECHA INSTALACION","FECHA GENERACION"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    return df

def preparar_fechas_movil(df):
    for col in ["FECHA OPERACION","FECHA CARGA"]:
        if col not in df.columns: continue
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
    for n in posibles:
        if n in df.columns: return n
    return None

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
    if len(p)==2 and p[0] in MESES_MAP and p[1].isdigit(): return MESES_MAP[p[0]], int(p[1])
    return None, None

def filtrar_por_mes_anio(df, col, txt):
    m, y = parse_mes_anio(txt)
    if m and y and col in df.columns:
        return df[(df[col].dt.month==m)&(df[col].dt.year==y)].copy()
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
            for f in df[col].dropna():
                meses.add(f"{MESES_ES[f.month].capitalize()} {f.year}")
    if not meses: return ["Todos los meses"]
    return ["Todos los meses"] + sorted(meses, key=lambda s:(int(s.split()[1]),MESES_MAP.get(s.split()[0].lower(),0)))

@st.cache_data(ttl=300)
def obtener_meses_movil(col, archivos):
    meses = set()
    for a in archivos:
        df = preparar_fechas_movil(cargar_csv(a))
        if col in df.columns:
            for f in df[df[col].notna()][col]:
                meses.add(f"{MESES_ES[f.month].lower()} {f.year}".capitalize())
    if not meses: return ["Todos los meses"]
    return ["Todos los meses"] + sorted(meses, key=lambda s:(int(s.split()[1]),MESES_MAP.get(s.split()[0].lower(),0)))

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
        df["Nombre del Cliente"] = (nom+" "+ape).str.strip().replace("","Sin Datos").fillna("Sin Datos")
        df["COMISION"] = obtener_comision_fija(df)
        df["¿Pagado?"] = df["COMISION"].apply(lambda x: "SÍ" if x > 0 else "NO")
        return df[cols]
    except Exception as e:
        st.error(f"Error reporte liquidado: {e}")
        return pd.DataFrame(columns=cols)

# =========================================================
# 7. FACTOR FIJA (resumen + detallado, genérico)
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
            **{"PORTABILIDAD NO":("_porta",lambda x:(~x).sum())},
            FTTH=("_ftth","sum"), HFC=("_hfc","sum"),
        ).reset_index()
        com = df.groupby(["_anio","_mes"])["COMISION"].sum().reset_index()
        com.columns=["_anio","_mes","S/."]
        grp = grp.merge(com, on=["_anio","_mes"], how="left")
        grp.columns=["Año","MesNum","Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."]
        grp["Mes"]=grp["MesNum"].map(MESES_ES)
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
            Porta_NO=("_porta",lambda x:(~x).sum()), FTTH=("_ftth","sum"), HFC=("_hfc","sum"),
        ).reset_index()
        com = df.groupby(["_anio","_mes","_dia"])["COMISION"].sum().reset_index()
        com.columns=["_anio","_mes","_dia","Monto"]
        grp = grp.merge(com, on=["_anio","_mes","_dia"], how="left")
        grp.columns=["Año","MesNum","Dia","Ventas","Porta_SI","Porta_NO","FTTH","HFC","Monto"]
        grp["Mes"]=grp["MesNum"].map(MESES_ES)
        return grp.sort_values(["Año","MesNum","Dia"],ascending=[False,False,True])[cols]
    except Exception as e:
        st.error(f"Error factor fija detallado: {e}")
        return pd.DataFrame(columns=cols)

# =========================================================
# 8. FACTOR MÓVIL (resumen + detallado, genérico)
# =========================================================
def _base_factor_movil(df, col_fecha):
    df["_comision"] = obtener_comision_movil(df)
    tr = df.get("TRANSACCION", pd.Series([""] * len(df), index=df.index)).fillna("").astype(str)
    df["_porta"] = _es_portabilidad_movil(tr)
    df["_alta"]  = _es_alta_movil(tr)
    cf   = pd.to_numeric(df.get("CF", pd.Series([0.0]*len(df), index=df.index)), errors="coerce").fillna(0)
    dias = pd.to_numeric(df.get("DIAS PORTADAS", pd.Series([0.0]*len(df), index=df.index)), errors="coerce").fillna(0)
    df["_cf_mayor"] = cf > 69.90;   df["_cf_menor"] = cf <= 69.90
    df["_dias_mayor"] = dias > 90;  df["_dias_menor"] = dias <= 90
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
        grp.columns=["Año","MesNum","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","S/."]
        grp["Mes"]=grp["MesNum"].map(MESES_ES)
        for c in ["Año","MesNum","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90"]:
            grp[c]=pd.to_numeric(grp[c],errors="coerce").fillna(0).astype(int)
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
        grp.columns=["Año","MesNum","Dia","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","Monto"]
        grp["Mes"]=grp["MesNum"].map(MESES_ES)
        for c in ["Año","MesNum","Dia","Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90"]:
            grp[c]=pd.to_numeric(grp[c],errors="coerce").fillna(0).astype(int)
        return grp.sort_values(["Año","MesNum","Dia"],ascending=[False,False,True])[cols]
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
        Ventas_Pagadas=("SOT", lambda x: x[df.loc[x.index,"_cn"]=="SI"].nunique()),
        Ventas_No_Pagadas=("SOT", lambda x: x[df.loc[x.index,"_cn"]=="NO"].nunique()),
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
    hc = "#0f4287" if color=="dc" else "#70008f"
    return [{"selector":"th","props":[("background-color","white"),("color",hc),("font-size","13px"),("text-align","center"),("border-bottom","2px solid #ddd")]},
            {"selector":"td","props":[("padding","10px 8px"),("font-size","13px"),("border-bottom","1px solid #eee"),("background-color","white")]}]

def mostrar_expanders_fija(df_det, color="dc"):
    if df_det.empty: st.warning("No se encontraron datos."); return
    for _, p in (df_det[["Año","Mes","MesNum"]].drop_duplicates().sort_values(["Año","MesNum"],ascending=[False,False])).iterrows():
        dm = df_det[(df_det["Año"]==p["Año"])&(df_det["Mes"]==p["Mes"])].copy()
        icono = "🔵" if color=="dc" else "🟣"
        with st.expander(f"{icono} {p['Mes']} {p['Año']}  |  Ventas: {int(dm['Ventas'].sum())}  |  Total: {formatear_moneda(dm['Monto'].sum())}", expanded=False):
            t = dm[["Dia","Ventas","Porta_SI","Porta_NO","FTTH","HFC","Monto"]].copy()
            t["Monto"] = t["Monto"].map(formatear_moneda)
            st.table(t)

def mostrar_expanders_movil(df_det, color="dc"):
    if df_det.empty: st.warning("No se encontraron datos."); return
    for _, p in (df_det[["Año","Mes","MesNum"]].drop_duplicates().sort_values(["Año","MesNum"],ascending=[False,False])).iterrows():
        dm = df_det[(df_det["Año"]==p["Año"])&(df_det["Mes"]==p["Mes"])].copy()
        icono = "🔵" if color=="dc" else "🟣"
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
                .set_properties(subset=["Año","Mes"],**{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD SI","PORTABILIDAD NO","FTTH","HFC","S/."],**{"text-align":"center"}))
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
                .set_properties(subset=["Año","Mes"],**{"text-align":"left"})
                .set_properties(subset=["Ventas","PORTABILIDAD","ALTA","CF>69.90","CF<=69.90","Dias>90","Dias<=90","S/."],**{"text-align":"center"}))
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
    filtro_a = st.selectbox("Selecciona Asesor", ["Todos"]+sorted(df_m["ASESOR"].unique().tolist()), key=key_asesor)
    df_f = df_m[df_m["ASESOR"]==filtro_a].copy() if filtro_a != "Todos" else df_m.copy()
    st.markdown("### Ranking de Asesores")
    r = (df_f.groupby("ASESOR").agg(
        Total_Ventas=("_porta",lambda x:len(x)), Portabilidades=("_porta","sum"),
        Altas=("_alta","sum"), Comision_Total=("_comision","sum"),
    ).reset_index().sort_values("Comision_Total",ascending=False))
    r["Rank"] = r["Comision_Total"].rank(method="dense",ascending=False).astype(int)
    r = r[["Rank","ASESOR","Total_Ventas","Portabilidades","Altas","Comision_Total"]]
    total = pd.DataFrame([{"Rank":"Total","ASESOR":"","Total_Ventas":r["Total_Ventas"].sum(),
        "Portabilidades":r["Portabilidades"].sum(),"Altas":r["Altas"].sum(),"Comision_Total":r["Comision_Total"].sum()}])
    st.table(pd.concat([r,total],ignore_index=True).style.format({"Comision_Total":"S/ {:,.2f}"})
        .set_properties(**{"text-align":"center"}).set_properties(subset=["ASESOR"],**{"text-align":"left"}))

# =========================================================
# 10. DETALLE FIJA GENERAL — BASE DEVELZ COMPLETA
# =========================================================

# IMPORTANTE:
# Esta vista toma como base FIJA_DC + FIJA_TELETALK (DEVELZ),
# por eso entran TODAS las ventas: con SOT, sin SOT, cruzadas y no cruzadas.
# Solo hay 2 estados finales:
#   - PAGADA: cuando el SOT cruza con Claro y tiene COMISIONES = SI o COMISION > 0
#   - CAÍDA: todo lo demás, incluyendo ventas sin SOT

def _normalizar_texto(txt):
    return str(txt).upper().strip().replace("Í", "I").replace("Á", "A").replace("É", "E").replace("Ó", "O").replace("Ú", "U")

def _normalizar_tipis(txt):
    return _normalizar_texto(txt)

def _estado_desde_tipis(tipis_txt):
    key = _normalizar_tipis(tipis_txt)
    return TIPIS_ESTADO_MAP.get(key, "Otros")

def _obtener_sot_develz(df):
    col_sot = encontrar_columna(df, ["Back Office - Sot", "Back Office - SOT", "SOT", "sot", "Sot"])
    if col_sot:
        return df[col_sot].fillna("").astype(str).str.strip()
    return pd.Series([""] * len(df), index=df.index)

def _obtener_fecha_inst_develz(df):
    col_fecha = encontrar_columna(df, [
        "Back Office - Fecha Instalacion", "Back Office - Fecha Instalación",
        "FECHA INSTALACION", "Fecha Instalacion", "Fecha Instalación"
    ])
    if col_fecha:
        return pd.to_datetime(df[col_fecha], errors="coerce", dayfirst=True)
    return pd.Series(pd.NaT, index=df.index)

def _obtener_supervisor_develz(df):
    col_sup = encontrar_columna(df, [
        "Datos Adicionales - Supervisor", "Datos adicionales - Supervisor",
        "SUPERVISOR", "Supervisor", "supervisor", "USUARIO", "Usuario"
    ])
    if col_sup:
        return df[col_sup].fillna("Sin Supervisor").astype(str).str.strip().replace("", "Sin Supervisor")
    return pd.Series(["Sin Supervisor"] * len(df), index=df.index)

def _obtener_nombre_cliente_develz(df):
    nom_col = encontrar_columna(df, ["Cliente - Nombre", "NOMBRE", "Nombre", "CLIENTE"])
    ape_pat_col = encontrar_columna(df, ["Cliente - Apellido Paterno", "Apellido Paterno", "APELLIDO PATERNO"])
    ape_mat_col = encontrar_columna(df, ["Cliente - Apellido Materno", "Apellido Materno", "APELLIDO MATERNO"])

    nom = df[nom_col].fillna("").astype(str).str.strip() if nom_col else pd.Series([""] * len(df), index=df.index)
    ape_pat = df[ape_pat_col].fillna("").astype(str).str.strip() if ape_pat_col else pd.Series([""] * len(df), index=df.index)
    ape_mat = df[ape_mat_col].fillna("").astype(str).str.strip() if ape_mat_col else pd.Series([""] * len(df), index=df.index)

    nombre = (nom + " " + ape_pat + " " + ape_mat).str.strip()
    nombre = nombre.replace("", "Sin Datos").fillna("Sin Datos")
    return nombre

def _obtener_departamento_develz(df):
    col_dpto = encontrar_columna(df, [
        "Datos Instalación - Departamento", "Datos Instalacion - Departamento",
        "DEPARTAMENTO", "Departamento", "departamento"
    ])
    if col_dpto:
        return df[col_dpto].fillna("Sin Datos").astype(str).str.strip().replace("", "Sin Datos")
    return pd.Series(["Sin Datos"] * len(df), index=df.index)

def _obtener_tipis_develz(df):
    col_tipis = encontrar_columna(df, [
        "TIPIS", "Tipis", "tipis",
        "Estados - Venta Especificacion", "Estados - Venta Especificación",
        "Estado - Venta Especificacion", "Estado - Venta Especificación",
        "ESTADO OPERATIVO", "Estado Operativo", "estado operativo"
    ])
    if col_tipis:
        tipis = df[col_tipis].fillna("Sin TIPIS").astype(str).str.strip()
        tipis = tipis.replace("", "Sin TIPIS")
        return tipis
    return pd.Series(["Sin TIPIS"] * len(df), index=df.index)

@st.cache_data(ttl=300)
def _base_claro_pago(tabla_ventas):
    """Base Claro resumida por SOT para saber si se pagó y cuánto se comisionó."""
    df_c = preparar_fechas_fija(get_tabla(tabla_ventas))
    cols = ["SOT", "COMISION_CLARO", "COMISIONES_CLARO"]
    if df_c.empty or "SOT" not in df_c.columns:
        return pd.DataFrame(columns=cols)

    df_c = df_c.copy()
    df_c["SOT"] = df_c["SOT"].fillna("").astype(str).str.strip()
    df_c = df_c[df_c["SOT"] != ""]
    df_c["COMISION_CLARO"] = obtener_comision_fija(df_c)

    if "COMISIONES" in df_c.columns:
        df_c["COMISIONES_CLARO"] = df_c["COMISIONES"].fillna("").astype(str).str.upper().str.strip().str.replace("Í", "I", regex=False)
    else:
        df_c["COMISIONES_CLARO"] = ""

    df_c["_pagada_flag"] = (df_c["COMISIONES_CLARO"] == "SI") | (df_c["COMISION_CLARO"] > 0)

    resumen = df_c.groupby("SOT", as_index=False).agg(
        COMISION_CLARO=("COMISION_CLARO", "sum"),
        PAGADA_FLAG=("_pagada_flag", "max")
    )
    resumen["COMISIONES_CLARO"] = resumen["PAGADA_FLAG"].apply(lambda x: "SI" if x else "NO")
    return resumen[["SOT", "COMISION_CLARO", "COMISIONES_CLARO"]]

@st.cache_data(ttl=300)
def construir_detalle_fija_develz(tabla_maestro, tabla_claro, canal, filtro_mes):
    """Construye detalle desde DEVELZ, no desde Claro. Incluye ventas sin SOT."""
    cols_salida = [
        "Canal", "SOT", "Documento", "SUPERVISOR", "Nombre del Cliente", "Departamento",
        "FECHA INSTALACION", "TIPIS", "Estado Operativo",
        "COMISION", "Estado Pago"
    ]

    try:
        df_m = get_tabla(tabla_maestro)
        if df_m.empty:
            return pd.DataFrame(columns=cols_salida)

        df_m = df_m.copy()
        df_m["Canal"] = canal
        df_m["SOT"] = _obtener_sot_develz(df_m)
        df_m["Documento"] = _obtener_documento_develz(df_m)
        df_m["_FECHA_DT"] = _obtener_fecha_inst_develz(df_m)

        if filtro_mes != "Todos los meses":
            m, y = parse_mes_anio(filtro_mes)
            if m and y:
                df_m = df_m[(df_m["_FECHA_DT"].dt.month == m) & (df_m["_FECHA_DT"].dt.year == y)].copy()

        if df_m.empty:
            return pd.DataFrame(columns=cols_salida)

        df_m["SUPERVISOR"] = _obtener_supervisor_develz(df_m)
        df_m["Nombre del Cliente"] = _obtener_nombre_cliente_develz(df_m)
        df_m["Departamento"] = _obtener_departamento_develz(df_m)
        df_m["TIPIS"] = _obtener_tipis_develz(df_m)
        df_m["Estado Operativo"] = df_m["TIPIS"].apply(_estado_desde_tipis)

        # Cruce con Claro solamente para saber si está pagada y traer comisión.
        df_pago = _base_claro_pago(tabla_claro)
        df = df_m.merge(df_pago, on="SOT", how="left")
        df["COMISION"] = pd.to_numeric(df.get("COMISION_CLARO", 0), errors="coerce").fillna(0)
        df["COMISIONES_CLARO"] = df.get("COMISIONES_CLARO", "").fillna("").astype(str).str.upper().str.strip().str.replace("Í", "I", regex=False)

        # SOLO DOS CATEGORÍAS:
        # PAGADA: cruza con Claro y tiene COMISIONES = SI o comisión > 0
        # CAÍDA: todo lo demás, incluyendo sin SOT
        df["Estado Pago"] = "CAÍDA"
        df.loc[(df["COMISIONES_CLARO"] == "SI") | (df["COMISION"] > 0), "Estado Pago"] = "PAGADA"

        df["FECHA INSTALACION"] = df["_FECHA_DT"].dt.strftime("%d/%m/%Y").fillna("")

        # Asegurar columnas de salida para evitar KeyError
        for col in cols_salida:
            if col not in df.columns:
                df[col] = ""

        return df[cols_salida].reset_index(drop=True)

    except Exception as e:
        st.error(f"Error construyendo detalle DEVELZ {canal}: {e}")
        return pd.DataFrame(columns=cols_salida)

@st.cache_data(ttl=300)
def construir_detalle_fija_general(filtro_mes):
    """Une todas las ventas de DEVELZ: D&C + Teletalk."""
    df_dc = construir_detalle_fija_develz("[DATA DEVELZ].dbo.FIJA_DC", "dbo.CLARO_DC_FIJA", "D&C", filtro_mes)
    df_tt = construir_detalle_fija_develz("[DATA DEVELZ].dbo.FIJA_TELETALK", "dbo.CLARO_TELETALK_FIJA", "Teletalk", filtro_mes)
    return pd.concat([df_dc, df_tt], ignore_index=True)

def kpi_detalle_fija(df):
    """KPIs sobre TODAS las ventas de DEVELZ. No usa SOT único porque también hay ventas sin SOT."""
    if df.empty:
        return 0, 0, 0, 0.0, 0.0

    total = int(len(df))
    pagadas = int((df["Estado Pago"] == "PAGADA").sum())
    caidas = int((df["Estado Pago"] == "CAÍDA").sum())
    comision = pd.to_numeric(df["COMISION"], errors="coerce").fillna(0).sum()
    pct = (pagadas / total * 100) if total > 0 else 0
    return total, pagadas, caidas, comision, pct

def ranking_departamentos_df(df):
    """Ranking de departamentos con PAGADA, CAÍDA y % participación sobre total pagadas."""
    if df.empty or "Departamento" not in df.columns:
        return pd.DataFrame()

    grp = df.groupby("Departamento").agg(
        Total=("Estado Pago", "count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
    ).reset_index().sort_values("Pagadas", ascending=False)

    total_ventas = grp["Total"].sum()
    total_pagadas = grp["Pagadas"].sum()
    total_caidas = grp["Caidas"].sum()
    total_comision = pd.to_numeric(grp["Comision"], errors="coerce").fillna(0).sum()

    # % Participación = Pagadas del departamento / Total pagadas general
    # Ejemplo: Lima 697 pagadas / 1193 total pagadas = 58.42%
    grp["% Participación"] = (
        (grp["Pagadas"] / total_pagadas * 100).round(2).astype(str) + "%"
        if total_pagadas > 0 else "0%"
    )

    # % Efectividad = Pagadas / Total ventas del mismo departamento
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"

    grp["Comision"] = grp["Comision"].map(formatear_moneda)

    total_row = pd.DataFrame([{
        "Departamento": "TOTAL",
        "Total": total_ventas,
        "Pagadas": total_pagadas,
        "Caidas": total_caidas,
        "Comision": formatear_moneda(total_comision),
        "% Participación": "100.00%" if total_pagadas > 0 else "0%",
        "% Efectividad": f"{(total_pagadas / total_ventas * 100):.2f}%" if total_ventas > 0 else "0%",
    }])

    cols_orden = ["Departamento", "Total", "Pagadas", "Caidas", "Comision", "% Participación", "% Efectividad"]
    return pd.concat([grp, total_row], ignore_index=True)[cols_orden]

def ranking_asesores_detalle(df):
    """Ranking de supervisores con solo PAGADA y CAÍDA."""
    if df.empty or "SUPERVISOR" not in df.columns:
        return pd.DataFrame()

    grp = df.groupby("SUPERVISOR").agg(
        Total=("Estado Pago", "count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
    ).reset_index().sort_values(["Comision", "Total"], ascending=[False, False]).reset_index(drop=True)

    grp.insert(0, "Rank", grp.index + 1)
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"

    total_row = pd.DataFrame([{
        "Rank": "TOTAL",
        "SUPERVISOR": "",
        "Total": grp["Total"].sum(),
        "Pagadas": grp["Pagadas"].sum(),
        "Caidas": grp["Caidas"].sum(),
        "% Efectividad": "",
        "Comision": grp["Comision"].sum(),
    }])
    return pd.concat([grp, total_row], ignore_index=True)

def estados_operativos_df(df):
    """Resumen de estados operativos TIPIS agrupado. Nunca debe salir vacío si hay datos."""
    if df.empty:
        return pd.DataFrame()

    base = df.copy()
    if "Estado Operativo" not in base.columns:
        base["Estado Operativo"] = "Sin TIPIS"

    base["Estado Operativo"] = base["Estado Operativo"].fillna("Sin TIPIS").astype(str).str.strip()
    base.loc[base["Estado Operativo"].eq(""), "Estado Operativo"] = "Sin TIPIS"

    total = len(base)
    grp = base.groupby("Estado Operativo").agg(N_Ventas=("Estado Pago", "count")).reset_index()
    grp["% del total"] = (grp["N_Ventas"] / total * 100).round(2).astype(str) + "%" if total > 0 else "0%"

    orden = {"Conforme": 0, "1era Caída": 1, "2da Caída": 2, "Ejecución": 3, "Otros": 4, "Sin TIPIS": 5}
    grp["_ord"] = grp["Estado Operativo"].map(orden).fillna(99)
    return grp.sort_values("_ord")[["Estado Operativo", "N_Ventas", "% del total"]]

def ventas_por_dia_df(df):
    """Resumen diario: total de ventas, pagadas, caídas, comisión y efectividad."""
    cols = ["Fecha", "Total Ventas", "Pagadas", "Caidas", "Comision", "% Efectividad"]
    if df.empty or "FECHA INSTALACION" not in df.columns:
        return pd.DataFrame(columns=cols)

    base = df.copy()
    base["_FECHA_DIA"] = pd.to_datetime(base["FECHA INSTALACION"], errors="coerce", dayfirst=True)
    base = base[base["_FECHA_DIA"].notna()].copy()

    # Limpieza gerencial de fechas:
    # - elimina fechas antiguas erradas tipo 04/69
    # - elimina fechas futuras tipo 05/26 o 12/26 si aún no corresponde
    hoy = pd.Timestamp.today().normalize()
    base = base[(base["_FECHA_DIA"] >= pd.Timestamp("2020-01-01")) & (base["_FECHA_DIA"] <= hoy)].copy()

    if base.empty:
        return pd.DataFrame(columns=cols)

    grp = base.groupby(base["_FECHA_DIA"].dt.date).agg(
        **{
            "Total Ventas": ("Estado Pago", "count"),
            "Pagadas": ("Estado Pago", lambda x: (x == "PAGADA").sum()),
            "Caidas": ("Estado Pago", lambda x: (x == "CAÍDA").sum()),
            "Comision": ("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
        }
    ).reset_index().rename(columns={"_FECHA_DIA": "Fecha"})

    grp["Fecha"] = pd.to_datetime(grp["Fecha"])
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total Ventas"] * 100).round(2).astype(str) + "%"
    grp = grp.sort_values("Fecha")

    return grp[cols]



def obtener_claro_pagado_no_develz(filtro_mes, filtro_canal):
    """SOT que Claro está pagando pero que no aparecen en DEVELZ."""
    pares = [
        ("D&C", "[DATA DEVELZ].dbo.FIJA_DC", "dbo.CLARO_DC_FIJA"),
        ("Teletalk", "[DATA DEVELZ].dbo.FIJA_TELETALK", "dbo.CLARO_TELETALK_FIJA"),
    ]

    salida = []

    for canal, tabla_dev, tabla_claro in pares:
        if filtro_canal != "Todos" and canal != filtro_canal:
            continue

        dev = _df_develz_para_conciliacion(tabla_dev, canal, filtro_mes)
        claro = _df_claro_para_conciliacion(tabla_claro, canal, filtro_mes)

        if claro.empty:
            continue

        dev_sot = set(dev[dev["SOT"] != ""]["SOT"].unique()) if not dev.empty else set()

        # Solo pagadas en Claro
        claro["PAGADA_CLARO"] = (
            (claro["Comisiones_Claro"].fillna("").astype(str).str.upper().str.strip() == "SI") |
            (pd.to_numeric(claro["Comision_Claro"], errors="coerce").fillna(0) > 0)
        )

        faltantes = claro[(claro["PAGADA_CLARO"]) & (~claro["SOT"].isin(dev_sot))].copy()

        if not faltantes.empty:
            faltantes["Motivo"] = "Claro lo paga, pero el SOT no aparece en DEVELZ"
            salida.append(faltantes)

    if not salida:
        return pd.DataFrame(columns=["Canal", "SOT", "Fecha_Claro", "Comision_Claro", "Comisiones_Claro", "Motivo"])

    df_out = pd.concat(salida, ignore_index=True)

    if "Cliente" not in df_out.columns:
        df_out["Cliente"] = ""
    if "Documento" not in df_out.columns:
        df_out["Documento"] = ""

    return df_out[["Canal", "SOT", "Fecha_Claro", "Cliente", "Documento", "Comision_Claro", "Comisiones_Claro", "Motivo"]]


def mostrar_claro_pagado_no_develz(filtro_mes, filtro_canal):
    """Cuadro debajo del detalle: pagadas en Claro que no figuran en DEVELZ."""
    st.write("---")
    st.markdown("#### 🔴 Ventas pagadas por CLARO que NO aparecen en DEVELZ")
    st.caption("Este cuadro explica la diferencia entre el número pagado de CLARO y el detalle basado en DEVELZ.")

    df_faltantes = obtener_claro_pagado_no_develz(filtro_mes, filtro_canal)

    if df_faltantes.empty:
        st.success("No hay SOT pagados por CLARO faltantes en DEVELZ con los filtros seleccionados.")
        return

    total_sot = df_faltantes["SOT"].nunique()
    total_comision = pd.to_numeric(df_faltantes["Comision_Claro"], errors="coerce").fillna(0).sum()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div style="background:rgba(255,255,255,.96);padding:14px;border-radius:14px;'
            f'border:2px solid #dc2626;text-align:center;margin-bottom:8px;">'
            f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;">SOT pagados no encontrados</span>'
            f'<span style="color:#dc2626;font-size:26px;font-weight:900;display:block;">{total_sot:,}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div style="background:rgba(255,255,255,.96);padding:14px;border-radius:14px;'
            f'border:2px solid #dc2626;text-align:center;margin-bottom:8px;">'
            f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;">Comisión no conciliada</span>'
            f'<span style="color:#dc2626;font-size:26px;font-weight:900;display:block;">{formatear_moneda(total_comision)}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    df_show = df_faltantes.copy()

    for col in ["Cliente", "Documento"]:
        if col not in df_show.columns:
            df_show[col] = ""

    df_show["Comision_Claro"] = pd.to_numeric(df_show["Comision_Claro"], errors="coerce").fillna(0).map(formatear_moneda)

    st.dataframe(df_show, use_container_width=True, height=260)

    csv_export = df_faltantes.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇️ Descargar SOT pagados por CLARO no encontrados en DEVELZ",
        data=csv_export,
        file_name=f"claro_pagado_no_develz_{filtro_mes.replace(' ', '_')}_{filtro_canal}.csv",
        mime="text/csv",
        key="dl_claro_pagado_no_develz_detalle"
    )



def mostrar_detalle_fija_general():
    """Vista única: D&C + Teletalk, basada en DEVELZ completo."""

    color_titulo = "#004a99"
    color_borde = "#0f4287"

    set_bg(img_caratula)
    st.markdown(
        f'<div style="color:{color_titulo};font-size:34px;font-weight:900;margin-bottom:4px;">'
        f'Detalle FIJA General</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="color:{color_titulo};font-weight:800;font-size:16px;margin-bottom:16px;">'
        f'D&C + TELETALK · BASE DEVELZ COMPLETA · CAÍDA REAL · PAGADA VS CAÍDA</div>',
        unsafe_allow_html=True
    )
    st.write("---")

    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([1.2, 1.1, 1.1, 1.4, 1.6])
    with col_f1:
        filtro_mes = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="det_general_mes")
    with col_f2:
        filtro_canal = st.selectbox("Canal", ["Todos", "D&C", "Teletalk"], key="det_general_canal")
    with col_f3:
        filtro_estado = st.selectbox("Estado de Pago", ["Todos", "PAGADA", "CAÍDA"], key="det_general_estado")
    with col_f4:
        filtro_supervisor_key = "det_general_supervisor"
    with col_f5:
        filtro_tipificacion_key = "det_general_tipificacion"

    with st.spinner("Cargando todas las ventas desde DEVELZ y cruzando con Claro..."):
        df_det = construir_detalle_fija_general(filtro_mes)

    if df_det.empty:
        st.warning("No se encontraron datos. Verifica que FIJA_DC.csv, FIJA_TELETALK.csv y los archivos Claro estén en la carpeta correcta.")
        return

    # Asegurar columna Documento aunque algún origen no la tenga
    if "Documento" not in df_det.columns:
        df_det["Documento"] = ""

    if filtro_canal != "Todos":
        df_det = df_det[df_det["Canal"] == filtro_canal]

    # Normalizar TIPIS para que el filtro de tipificaciones no salga vacío
    if "TIPIS" in df_det.columns:
        df_det["TIPIS"] = df_det["TIPIS"].fillna("Sin TIPIS").astype(str).str.strip()
        df_det.loc[df_det["TIPIS"].eq(""), "TIPIS"] = "Sin TIPIS"
    else:
        df_det["TIPIS"] = "Sin TIPIS"

    supervisores_disponibles = ["Todos"] + sorted(df_det["SUPERVISOR"].fillna("Sin Supervisor").unique().tolist())
    tipificaciones_disponibles = ["Todos"] + sorted(df_det["TIPIS"].fillna("Sin TIPIS").astype(str).unique().tolist())

    with col_f4:
        filtro_supervisor = st.selectbox("Supervisor", supervisores_disponibles, key=filtro_supervisor_key)

    with col_f5:
        filtro_tipificacion = st.selectbox("Tipificación", tipificaciones_disponibles, key=filtro_tipificacion_key)

    df_filtrado = df_det.copy()
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado Pago"] == filtro_estado]
    if filtro_supervisor != "Todos":
        df_filtrado = df_filtrado[df_filtrado["SUPERVISOR"] == filtro_supervisor]
    if filtro_tipificacion != "Todos":
        df_filtrado = df_filtrado[df_filtrado["TIPIS"] == filtro_tipificacion]

    total, pagadas, caidas, comision, pct = kpi_detalle_fija(df_filtrado)

    st.markdown("### Resumen General")
    k1, k2, k3, k4, k5 = st.columns(5)

    def _kpi_card(col, label, valor, sub="", color_val="inherit"):
        with col:
            st.markdown(
                f'<div style="background:rgba(255,255,255,.95);padding:16px;border-radius:16px;'
                f'border:2px solid {color_borde};text-align:center;margin-bottom:8px;min-height:92px;">'
                f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;'
                f'letter-spacing:.1em;display:block;margin-bottom:6px;">{label}</span>'
                f'<span style="color:{color_val};font-size:24px;font-weight:900;display:block;line-height:1.05;">{valor}</span>'
                f'<span style="color:#6b7280;font-size:10px;">{sub}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    _kpi_card(k1, "Total Ventas", f"{total:,}", "Base DEVELZ", color_borde)
    _kpi_card(k2, "Pagadas", f"{pagadas:,}", "Cruza con Claro", "#059669")
    _kpi_card(k3, "Caídas", f"{caidas:,}", "Sin pago / sin SOT", "#dc2626")
    _kpi_card(k4, "% Efectividad", f"{pct:.2f}%", "Pagadas / Total", "#059669" if pct >= 75 else "#d97706")
    _kpi_card(k5, "Comisión Total", formatear_moneda(comision), "Pagada", color_borde)

    st.write("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Detalle Ventas",
        "📆 Ventas por Día",
        "🏆 Ranking Asesores",
        "📍 Ranking Departamentos",
        "📊 Estados Operativos"
    ])

    with tab1:
        st.markdown("#### Detalle de ventas DEVELZ con estado final")

        def _colorear_estado(val):
            if val == "PAGADA":
                return "background-color:#dcfce7;color:#166534;font-weight:700"
            if val == "CAÍDA":
                return "background-color:#fee2e2;color:#991b1b;font-weight:700"
            return ""

        cols_mostrar = [
            "Canal", "SOT", "Documento", "SUPERVISOR", "Nombre del Cliente", "Departamento",
            "FECHA INSTALACION", "TIPIS", "Estado Operativo", "COMISION", "Estado Pago"
        ]

        # Evita error si alguna columna no existe en algún CSV
        for col in cols_mostrar:
            if col not in df_filtrado.columns:
                df_filtrado[col] = ""

        df_show = df_filtrado[cols_mostrar].copy()
        df_show["COMISION"] = pd.to_numeric(df_show["COMISION"], errors="coerce").fillna(0).map(formatear_moneda)

        st.dataframe(
            df_show.style.map(_colorear_estado, subset=["Estado Pago"]).format({"COMISION": lambda x: x}),
            use_container_width=True,
            height=450
        )

        csv_export = df_filtrado.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="⬇️ Descargar CSV completo",
            data=csv_export,
            file_name=f"detalle_fija_develz_{filtro_mes.replace(' ', '_')}_{filtro_canal}.csv",
            mime="text/csv",
            key="dl_det_general"
        )

        # Cuadro adicional para explicar diferencias:
        # SOT pagados en CLARO que no aparecen en DEVELZ
        mostrar_claro_pagado_no_develz(filtro_mes, filtro_canal)

    with tab2:
        st.markdown("#### Ventas por día — Total vs Pagadas")
        df_dia = ventas_por_dia_df(df_filtrado)

        if df_dia.empty:
            st.warning("No hay fechas válidas para mostrar ventas por día.")
        else:
            import altair as alt

            # =====================================================
            # GRÁFICO DINÁMICO:
            # - Si Fecha de Instalación = "Todos los meses": muestra por MES (03/25)
            # - Si seleccionas un mes específico: muestra por DÍA (01/03)
            # =====================================================

            if filtro_mes == "Todos los meses":
                df_tmp = df_filtrado.copy()
                df_tmp["_FECHA_GRAFICO"] = pd.to_datetime(
                    df_tmp["FECHA INSTALACION"],
                    errors="coerce",
                    dayfirst=True
                )
                df_tmp = df_tmp[df_tmp["_FECHA_GRAFICO"].notna()].copy()

                # Limpieza gerencial de fechas:
                # elimina fechas antiguas erradas y meses futuros no cerrados
                hoy = pd.Timestamp.today().normalize()
                df_tmp = df_tmp[(df_tmp["_FECHA_GRAFICO"] >= pd.Timestamp("2020-01-01")) & (df_tmp["_FECHA_GRAFICO"] <= hoy)].copy()

                if df_tmp.empty:
                    st.warning("No hay fechas válidas para mostrar el gráfico por mes.")
                else:
                    df_chart = df_tmp.groupby(df_tmp["_FECHA_GRAFICO"].dt.to_period("M")).agg(
                        **{
                            "Total Ventas": ("Estado Pago", "count"),
                            "Pagadas": ("Estado Pago", lambda x: (x == "PAGADA").sum()),
                            "Caidas": ("Estado Pago", lambda x: (x == "CAÍDA").sum()),
                            "Comision": ("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
                        }
                    ).reset_index()

                    df_chart["Fecha_dt"] = df_chart["_FECHA_GRAFICO"].dt.to_timestamp()
                    df_chart["Fecha_txt"] = df_chart["Fecha_dt"].dt.strftime("%m/%y")
                    df_chart["% Efectividad"] = (df_chart["Pagadas"] / df_chart["Total Ventas"] * 100).round(2).astype(str) + "%"
                    titulo_grafico = "Ventas realizadas por mes vs ventas pagadas"
                    titulo_tabla = "Tabla mensual"

                    chart_melt = df_chart.melt(
                        id_vars=["Fecha_dt", "Fecha_txt"],
                        value_vars=["Total Ventas", "Pagadas"],
                        var_name="Indicador",
                        value_name="Cantidad"
                    )

                    base_chart = alt.Chart(chart_melt).encode(
                        x=alt.X(
                            "Fecha_txt:N",
                            title="Mes",
                            sort=df_chart["Fecha_txt"].tolist(),
                            axis=alt.Axis(labelAngle=0, labelFontSize=12, titleFontSize=12)
                        ),
                        xOffset=alt.XOffset("Indicador:N"),
                        y=alt.Y(
                            "Cantidad:Q",
                            title="Ventas",
                            axis=alt.Axis(labelFontSize=12, titleFontSize=12, grid=True)
                        ),
                        color=alt.Color(
                            "Indicador:N",
                            scale=alt.Scale(
                                domain=["Total Ventas", "Pagadas"],
                                range=["#123f7a", "#10a06f"]
                            ),
                            legend=alt.Legend(title="Indicador", orient="top-right")
                        ),
                        tooltip=[
                            alt.Tooltip("Fecha_txt:N", title="Mes"),
                            alt.Tooltip("Indicador:N", title="Indicador"),
                            alt.Tooltip("Cantidad:Q", title="Cantidad", format=",.0f")
                        ]
                    )

                    # =====================================================
                    # GRÁFICO GERENCIAL PRO - BARRAS AGRUPADAS
                    # =====================================================
                    barras = base_chart.mark_bar(
                        size=32,
                        cornerRadiusTopLeft=7,
                        cornerRadiusTopRight=7,
                        opacity=0.92
                    )

                    etiquetas = base_chart.mark_text(
                        align="center",
                        baseline="bottom",
                        dy=-6,
                        fontSize=11,
                        fontWeight="bold",
                        color="#111827"
                    ).encode(
                        text=alt.Text("Cantidad:Q", format=".0f")
                    )

                    chart = (barras + etiquetas).properties(
                        height=430,
                        
                        padding={"left": 10, "right": 25, "top": 15, "bottom": 10}
                    ).configure_title(
                        fontSize=19,
                        fontWeight="bold",
                        anchor="start",
                        color="#111827"
                    ).configure_axis(
                        labelFontSize=12,
                        titleFontSize=12,
                        grid=True,
                        gridColor="#e5e7eb",
                        domain=False
                    ).configure_view(
                        strokeWidth=0
                    ).configure_legend(
                        titleFontSize=12,
                        labelFontSize=12,
                        orient="top-right",
                        symbolSize=120
                    )

                    st.altair_chart(chart, use_container_width=True)

                    tabla_dia = df_chart[["Fecha_txt", "Total Ventas", "Pagadas", "Caidas", "Comision", "% Efectividad"]].copy()
                    tabla_dia = tabla_dia.rename(columns={"Fecha_txt": "Mes"})
                    tabla_dia["Comision"] = pd.to_numeric(tabla_dia["Comision"], errors="coerce").fillna(0).map(formatear_moneda)

                    total_row = pd.DataFrame([{
                        "Mes": "TOTAL",
                        "Total Ventas": tabla_dia["Total Ventas"].sum(),
                        "Pagadas": tabla_dia["Pagadas"].sum(),
                        "Caidas": tabla_dia["Caidas"].sum(),
                        "Comision": formatear_moneda(pd.to_numeric(df_chart["Comision"], errors="coerce").fillna(0).sum()),
                        "% Efectividad": f"{(tabla_dia['Pagadas'].sum() / tabla_dia['Total Ventas'].sum() * 100):.2f}%" if tabla_dia["Total Ventas"].sum() > 0 else "0%"
                    }])

                    tabla_dia = pd.concat([tabla_dia, total_row], ignore_index=True)

                    st.markdown(f"#### {titulo_tabla}")
                    st.dataframe(tabla_dia, use_container_width=True, height=420)

            else:
                chart_base = df_dia.copy()
                chart_base["Fecha"] = pd.to_datetime(chart_base["Fecha"])
                chart_base["Fecha_txt"] = chart_base["Fecha"].dt.strftime("%d/%m")
                chart_melt = chart_base.melt(
                    id_vars=["Fecha", "Fecha_txt"],
                    value_vars=["Total Ventas", "Pagadas"],
                    var_name="Indicador",
                    value_name="Cantidad"
                )

                base_chart = alt.Chart(chart_melt).encode(
                    x=alt.X(
                        "Fecha_txt:N",
                        title="Fecha",
                        sort=chart_base["Fecha_txt"].tolist(),
                        axis=alt.Axis(labelAngle=0, labelFontSize=11, titleFontSize=12)
                    ),
                    xOffset=alt.XOffset("Indicador:N"),
                    y=alt.Y(
                        "Cantidad:Q",
                        title="Ventas",
                        axis=alt.Axis(labelFontSize=12, titleFontSize=12, grid=True)
                    ),
                    color=alt.Color(
                        "Indicador:N",
                        scale=alt.Scale(
                            domain=["Total Ventas", "Pagadas"],
                            range=["#123f7a", "#10a06f"]
                        ),
                        legend=alt.Legend(title="Indicador", orient="top-right")
                    ),
                    tooltip=[
                        alt.Tooltip("Fecha:T", title="Fecha", format="%d/%m/%Y"),
                        alt.Tooltip("Indicador:N", title="Indicador"),
                        alt.Tooltip("Cantidad:Q", title="Cantidad", format=",.0f")
                    ]
                )

                # =====================================================
                # GRÁFICO GERENCIAL PRO - BARRAS AGRUPADAS
                # =====================================================
                barras = base_chart.mark_bar(
                    size=18,
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6,
                    opacity=0.92
                )

                etiquetas = base_chart.mark_text(
                    align="center",
                    baseline="bottom",
                    dy=-6,
                    fontSize=10,
                    fontWeight="bold",
                    color="#111827"
                ).encode(
                    text=alt.Text("Cantidad:Q", format=".0f")
                )

                chart = (barras + etiquetas).properties(
                    height=430,
                    
                    padding={"left": 10, "right": 25, "top": 15, "bottom": 10}
                ).configure_title(
                    fontSize=19,
                    fontWeight="bold",
                    anchor="start",
                    color="#111827"
                ).configure_axis(
                    labelFontSize=11,
                    titleFontSize=12,
                    grid=True,
                    gridColor="#e5e7eb",
                    domain=False
                ).configure_view(
                    strokeWidth=0
                ).configure_legend(
                    titleFontSize=12,
                    labelFontSize=12,
                    orient="top-right",
                    symbolSize=120
                )

                st.altair_chart(chart, use_container_width=True)

                tabla_dia = df_dia.copy()
                tabla_dia["Fecha"] = pd.to_datetime(tabla_dia["Fecha"]).dt.strftime("%d/%m/%Y")
                tabla_dia["Comision"] = pd.to_numeric(tabla_dia["Comision"], errors="coerce").fillna(0).map(formatear_moneda)

                total_row = pd.DataFrame([{
                    "Fecha": "TOTAL",
                    "Total Ventas": tabla_dia["Total Ventas"].sum(),
                    "Pagadas": tabla_dia["Pagadas"].sum(),
                    "Caidas": tabla_dia["Caidas"].sum(),
                    "Comision": formatear_moneda(pd.to_numeric(df_dia["Comision"], errors="coerce").fillna(0).sum()),
                    "% Efectividad": f"{(tabla_dia['Pagadas'].sum() / tabla_dia['Total Ventas'].sum() * 100):.2f}%" if tabla_dia["Total Ventas"].sum() > 0 else "0%"
                }])

                tabla_dia = pd.concat([tabla_dia, total_row], ignore_index=True)

                st.markdown("#### Tabla diaria")
                st.dataframe(tabla_dia, use_container_width=True, height=420)

    with tab3:
        st.markdown("#### Ranking de Supervisores — PAGADA vs CAÍDA")
        rank_df = ranking_asesores_detalle(df_filtrado)
        if rank_df.empty:
            st.warning("Sin datos para el ranking.")
        else:
            st.table(
                rank_df.style
                    .format({"Comision": lambda x: formatear_moneda(x) if isinstance(x, (int, float)) else x})
                    .set_properties(**{"text-align": "center"})
                    .set_properties(subset=["SUPERVISOR"], **{"text-align": "left"})
            )

    with tab4:
        st.markdown("#### Ranking por Departamento de Instalación")
        st.caption("Fuente: columna `Datos Instalación - Departamento` de DEVELZ")
        rank_dpto = ranking_departamentos_df(df_filtrado)
        if rank_dpto.empty:
            st.warning("No se encontró columna de departamento. Verifica que DEVELZ tenga 'Datos Instalación - Departamento'.")
        else:
            df_chart = rank_dpto[rank_dpto["Departamento"] != "TOTAL"].copy()
            if not df_chart.empty:
                import altair as alt
                chart_data = df_chart[["Departamento", "Pagadas", "Caidas"]].copy()
                chart_data_melt = chart_data.melt("Departamento", var_name="Estado", value_name="Cantidad")
                chart = alt.Chart(chart_data_melt).mark_bar().encode(
                    x=alt.X("Cantidad:Q", title="Ventas"),
                    y=alt.Y("Departamento:N", sort="-x", title=""),
                    color=alt.Color("Estado:N", scale=alt.Scale(
                        domain=["Pagadas", "Caidas"],
                        range=["#059669", "#dc2626"]
                    )),
                    tooltip=["Departamento", "Estado", "Cantidad"]
                ).properties(height=max(200, len(df_chart) * 40)).configure_axis(labelFontSize=12, titleFontSize=13)
                st.altair_chart(chart, use_container_width=True)

            st.markdown("**Tabla de detalle por departamento**")
            st.table(rank_dpto)

    with tab5:
        st.markdown("#### Estados Operativos (TIPIS agrupado)")
        estados_df = estados_operativos_df(df_filtrado)
        if estados_df.empty:
            st.warning("No se encontraron datos de TIPIS.")
        else:
            col_e1, col_e2 = st.columns([1, 1.5])
            with col_e1:
                st.table(estados_df)
            with col_e2:
                if "TIPIS" in df_filtrado.columns:
                    for estado_grupo in ["Conforme", "1era Caída", "2da Caída", "Ejecución", "Otros", "Sin TIPIS"]:
                        df_grupo = df_filtrado[df_filtrado["Estado Operativo"] == estado_grupo]
                        if df_grupo.empty:
                            continue
                        tipis_count = df_grupo["TIPIS"].fillna("Sin TIPIS").replace("", "Sin TIPIS").value_counts().reset_index()
                        tipis_count.columns = ["TIPIS", "Cantidad"]
                        with st.expander(f"{estado_grupo}  ({len(df_grupo)} ventas)", expanded=False):
                            st.table(tipis_count)



# =========================================================
# 10B. DETALLE MÓVIL GENERAL — D&C + TELETALK
# =========================================================

def _obtener_fecha_movil_general(df):
    col_fecha = encontrar_columna(df, [
        "FECHA OPERACION", "FECHA OPERACIÓN",
        "FECHA CARGA", "Fecha Operacion", "Fecha Operación", "Fecha Carga"
    ])
    if col_fecha:
        return pd.to_datetime(df[col_fecha], errors="coerce", dayfirst=True), col_fecha
    return pd.Series(pd.NaT, index=df.index), ""

def _obtener_asesor_movil(df):
    col = encontrar_columna(df, [
        "USUARIO", "ASESOR", "VENDEDOR", "DISTRIBUIDOR", "EJECUTIVO", "Usuario", "Asesor"
    ])
    if col:
        return df[col].fillna("Sin Asesor").astype(str).str.strip().replace("", "Sin Asesor")
    return pd.Series(["Sin Asesor"] * len(df), index=df.index)

def _obtener_cliente_movil(df):
    col_cliente = encontrar_columna(df, [
        "CLIENTE", "Cliente", "NOMBRE CLIENTE", "Nombre Cliente", "NOMBRE", "Nombre"
    ])
    if col_cliente:
        return df[col_cliente].fillna("Sin Datos").astype(str).str.strip().replace("", "Sin Datos")
    return pd.Series(["Sin Datos"] * len(df), index=df.index)

def _obtener_documento_movil(df):
    col_doc = encontrar_columna(df, [
        "NRO DOCUMENTO", "DOCUMENTO", "DNI", "NRO DNI", "N° DOCUMENTO", "NRO. DOCUMENTO"
    ])
    if col_doc:
        return df[col_doc].fillna("").astype(str).str.strip()
    return pd.Series([""] * len(df), index=df.index)

def _obtener_transaccion_movil(df):
    col = encontrar_columna(df, ["TRANSACCION", "TRANSACCIÓN", "TIPO TRANSACCION", "Tipo Transaccion"])
    if col:
        return df[col].fillna("Sin Transacción").astype(str).str.strip().replace("", "Sin Transacción")
    return pd.Series(["Sin Transacción"] * len(df), index=df.index)

def _obtener_departamento_movil(df):
    col = encontrar_columna(df, [
        "DEPARTAMENTO", "Departamento", "DPTO", "REGION", "Región", "REGIÓN"
    ])
    if col:
        return df[col].fillna("Sin Datos").astype(str).str.strip().replace("", "Sin Datos")
    return pd.Series(["Sin Datos"] * len(df), index=df.index)

@st.cache_data(ttl=300)
def construir_detalle_movil_general(filtro_mes):
    """Une CLARO_DC_MOVIL + CLARO_TELETALK_MOVIL."""
    cols_salida = [
        "Canal", "FECHA", "ASESOR", "Cliente", "Documento", "Departamento",
        "Transaccion", "COMISION", "Estado Pago"
    ]

    bases = [
        ("D&C", "dbo.CLARO_DC_MOVIL"),
        ("Teletalk", "dbo.CLARO_TELETALK_MOVIL"),
    ]

    dfs = []

    for canal, tabla in bases:
        df = preparar_fechas_movil(get_tabla(tabla))
        if df.empty:
            continue

        df = df.copy()
        df["Canal"] = canal
        df["_FECHA_DT"], col_fecha = _obtener_fecha_movil_general(df)

        if filtro_mes != "Todos los meses":
            m, y = parse_mes_anio(filtro_mes)
            if m and y:
                df = df[(df["_FECHA_DT"].dt.month == m) & (df["_FECHA_DT"].dt.year == y)].copy()

        if df.empty:
            continue

        df["ASESOR"] = _obtener_asesor_movil(df)
        df["Cliente"] = _obtener_cliente_movil(df)
        df["Documento"] = _obtener_documento_movil(df)
        df["Departamento"] = _obtener_departamento_movil(df)
        df["Transaccion"] = _obtener_transaccion_movil(df)
        df["COMISION"] = obtener_comision_movil(df)

        # Misma lógica que fija: solo dos estados
        # PAGADA = comisión mayor a 0
        # CAÍDA = todo lo demás
        df["Estado Pago"] = df["COMISION"].apply(lambda x: "PAGADA" if float(x) > 0 else "CAÍDA")
        df["FECHA"] = df["_FECHA_DT"].dt.strftime("%d/%m/%Y").fillna("")

        dfs.append(df[cols_salida])

    if not dfs:
        return pd.DataFrame(columns=cols_salida)

    return pd.concat(dfs, ignore_index=True)

@st.cache_data(ttl=300)
def obtener_meses_movil_general():
    meses = set()
    for archivo in ["CLARO_DC_MOVIL.csv", "CLARO_TELETALK_MOVIL.csv"]:
        df = preparar_fechas_movil(cargar_csv(archivo))
        if df.empty:
            continue

        col_fecha = "FECHA OPERACION" if "FECHA OPERACION" in df.columns else ("FECHA CARGA" if "FECHA CARGA" in df.columns else None)
        if col_fecha and col_fecha in df.columns:
            for f in df[col_fecha].dropna():
                meses.add(f"{MESES_ES[f.month]} {f.year}")

    if not meses:
        return ["Todos los meses"]

    return ["Todos los meses"] + sorted(meses, key=lambda s: (int(s.split()[1]), MESES_MAP.get(s.split()[0].lower(), 0)))

def kpi_detalle_movil(df):
    if df.empty:
        return 0, 0, 0, 0.0, 0.0

    total = int(len(df))
    pagadas = int((df["Estado Pago"] == "PAGADA").sum())
    caidas = int((df["Estado Pago"] == "CAÍDA").sum())
    comision = pd.to_numeric(df["COMISION"], errors="coerce").fillna(0).sum()
    pct = (pagadas / total * 100) if total > 0 else 0
    return total, pagadas, caidas, comision, pct

def ranking_asesores_movil_df(df):
    if df.empty:
        return pd.DataFrame()

    grp = df.groupby("ASESOR").agg(
        Total=("Estado Pago", "count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
    ).reset_index().sort_values(["Comision", "Total"], ascending=[False, False]).reset_index(drop=True)

    grp.insert(0, "Rank", grp.index + 1)
    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"
    grp["Comision"] = grp["Comision"].map(formatear_moneda)

    return grp

def ranking_transaccion_movil_df(df):
    if df.empty:
        return pd.DataFrame()

    grp = df.groupby("Transaccion").agg(
        Total=("Estado Pago", "count"),
        Pagadas=("Estado Pago", lambda x: (x == "PAGADA").sum()),
        Caidas=("Estado Pago", lambda x: (x == "CAÍDA").sum()),
        Comision=("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
    ).reset_index().sort_values("Total", ascending=False)

    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total"] * 100).round(2).astype(str) + "%"
    grp["Comision"] = grp["Comision"].map(formatear_moneda)

    return grp

def ventas_movil_por_periodo_df(df, filtro_mes):
    cols = ["Fecha", "Total Ventas", "Pagadas", "Caidas", "Comision", "% Efectividad"]
    if df.empty or "FECHA" not in df.columns:
        return pd.DataFrame(columns=cols)

    base = df.copy()
    base["_FECHA_GRAFICO"] = pd.to_datetime(base["FECHA"], errors="coerce", dayfirst=True)
    base = base[base["_FECHA_GRAFICO"].notna()].copy()

    hoy = pd.Timestamp.today().normalize()
    base = base[(base["_FECHA_GRAFICO"] >= pd.Timestamp("2020-01-01")) & (base["_FECHA_GRAFICO"] <= hoy)].copy()

    if base.empty:
        return pd.DataFrame(columns=cols)

    if filtro_mes == "Todos los meses":
        grp = base.groupby(base["_FECHA_GRAFICO"].dt.to_period("M")).agg(
            **{
                "Total Ventas": ("Estado Pago", "count"),
                "Pagadas": ("Estado Pago", lambda x: (x == "PAGADA").sum()),
                "Caidas": ("Estado Pago", lambda x: (x == "CAÍDA").sum()),
                "Comision": ("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
            }
        ).reset_index()

        grp["Fecha_dt"] = grp["_FECHA_GRAFICO"].dt.to_timestamp()
        grp["Fecha"] = grp["Fecha_dt"].dt.strftime("%m/%y")
        grp = grp.sort_values("Fecha_dt")
    else:
        grp = base.groupby(base["_FECHA_GRAFICO"].dt.date).agg(
            **{
                "Total Ventas": ("Estado Pago", "count"),
                "Pagadas": ("Estado Pago", lambda x: (x == "PAGADA").sum()),
                "Caidas": ("Estado Pago", lambda x: (x == "CAÍDA").sum()),
                "Comision": ("COMISION", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()),
            }
        ).reset_index().rename(columns={"_FECHA_GRAFICO": "Fecha_dt"})

        grp["Fecha_dt"] = pd.to_datetime(grp["Fecha_dt"])
        grp["Fecha"] = grp["Fecha_dt"].dt.strftime("%d/%m")
        grp = grp.sort_values("Fecha_dt")

    grp["% Efectividad"] = (grp["Pagadas"] / grp["Total Ventas"] * 100).round(2).astype(str) + "%"
    return grp[["Fecha", "Total Ventas", "Pagadas", "Caidas", "Comision", "% Efectividad"]]

def mostrar_grafico_barras_movil(df_periodo, filtro_mes):
    if df_periodo.empty:
        st.warning("No hay datos válidos para el gráfico.")
        return

    import altair as alt

    chart_melt = df_periodo.melt(
        id_vars=["Fecha"],
        value_vars=["Total Ventas", "Pagadas"],
        var_name="Indicador",
        value_name="Cantidad"
    )

    base_chart = alt.Chart(chart_melt).encode(
        x=alt.X(
            "Fecha:N",
            title="Mes" if filtro_mes == "Todos los meses" else "Fecha",
            sort=df_periodo["Fecha"].tolist(),
            axis=alt.Axis(labelAngle=0, labelFontSize=11, titleFontSize=12)
        ),
        xOffset=alt.XOffset("Indicador:N"),
        y=alt.Y(
            "Cantidad:Q",
            title="Ventas",
            axis=alt.Axis(labelFontSize=12, titleFontSize=12, grid=True)
        ),
        color=alt.Color(
            "Indicador:N",
            scale=alt.Scale(
                domain=["Total Ventas", "Pagadas"],
                range=["#123f7a", "#10a06f"]
            ),
            legend=alt.Legend(title="Indicador", orient="top-right")
        ),
        tooltip=[
            alt.Tooltip("Fecha:N", title="Periodo"),
            alt.Tooltip("Indicador:N", title="Indicador"),
            alt.Tooltip("Cantidad:Q", title="Cantidad", format=",.0f")
        ]
    )

    barras = base_chart.mark_bar(
        size=26 if filtro_mes == "Todos los meses" else 18,
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6,
        opacity=0.92
    )

    etiquetas = base_chart.mark_text(
        align="center",
        baseline="bottom",
        dy=-6,
        fontSize=10,
        fontWeight="bold",
        color="#111827"
    ).encode(
        text=alt.Text("Cantidad:Q", format=".0f")
    )

    chart = (barras + etiquetas).properties(
        height=430,
        padding={"left": 10, "right": 25, "top": 15, "bottom": 10}
    ).configure_axis(
        labelFontSize=11,
        titleFontSize=12,
        grid=True,
        gridColor="#e5e7eb",
        domain=False
    ).configure_view(
        strokeWidth=0
    ).configure_legend(
        titleFontSize=12,
        labelFontSize=12,
        orient="top-right",
        symbolSize=120
    )

    st.altair_chart(chart, use_container_width=True)

def mostrar_detalle_movil_general():
    """Vista única móvil: D&C + Teletalk."""
    color_titulo = "#70008f"
    color_borde = "#6d0b8c"

    set_bg(img_tt)

    st.markdown(
        f'<div style="color:{color_titulo};font-size:34px;font-weight:900;margin-bottom:4px;">'
        f'Detalle MÓVIL General</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="color:{color_titulo};font-weight:800;font-size:16px;margin-bottom:16px;">'
        f'D&C + TELETALK · PAGADA VS CAÍDA · COMISIÓN MÓVIL</div>',
        unsafe_allow_html=True
    )
    st.write("---")

    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([1.2, 1.1, 1.1, 1.4, 1.4])

    with col_f1:
        filtro_mes = st.selectbox("Fecha de Venta", obtener_meses_movil_general(), key="movil_general_mes")
    with col_f2:
        filtro_canal = st.selectbox("Canal", ["Todos", "D&C", "Teletalk"], key="movil_general_canal")
    with col_f3:
        filtro_estado = st.selectbox("Estado de Pago", ["Todos", "PAGADA", "CAÍDA"], key="movil_general_estado")
    with col_f4:
        filtro_asesor_key = "movil_general_asesor"
    with col_f5:
        filtro_transaccion_key = "movil_general_transaccion"

    with st.spinner("Cargando ventas móviles D&C + Teletalk..."):
        df_det = construir_detalle_movil_general(filtro_mes)

    if df_det.empty:
        st.warning("No se encontraron datos móviles. Verifica CLARO_DC_MOVIL.csv y CLARO_TELETALK_MOVIL.csv.")
        return

    if filtro_canal != "Todos":
        df_det = df_det[df_det["Canal"] == filtro_canal]

    asesores = ["Todos"] + sorted(df_det["ASESOR"].fillna("Sin Asesor").astype(str).unique().tolist())
    transacciones = ["Todos"] + sorted(df_det["Transaccion"].fillna("Sin Transacción").astype(str).unique().tolist())

    with col_f4:
        filtro_asesor = st.selectbox("Asesor", asesores, key=filtro_asesor_key)
    with col_f5:
        filtro_transaccion = st.selectbox("Transacción", transacciones, key=filtro_transaccion_key)

    df_filtrado = df_det.copy()
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado Pago"] == filtro_estado]
    if filtro_asesor != "Todos":
        df_filtrado = df_filtrado[df_filtrado["ASESOR"] == filtro_asesor]
    if filtro_transaccion != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Transaccion"] == filtro_transaccion]

    total, pagadas, caidas, comision, pct = kpi_detalle_movil(df_filtrado)

    st.markdown("### Resumen General")
    k1, k2, k3, k4, k5 = st.columns(5)

    def _kpi_card(col, label, valor, sub="", color_val="inherit"):
        with col:
            st.markdown(
                f'<div style="background:rgba(255,255,255,.95);padding:16px;border-radius:16px;'
                f'border:2px solid {color_borde};text-align:center;margin-bottom:8px;min-height:92px;">'
                f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;'
                f'letter-spacing:.1em;display:block;margin-bottom:6px;">{label}</span>'
                f'<span style="color:{color_val};font-size:24px;font-weight:900;display:block;line-height:1.05;">{valor}</span>'
                f'<span style="color:#6b7280;font-size:10px;">{sub}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    _kpi_card(k1, "Total Ventas", f"{total:,}", "Móvil", color_borde)
    _kpi_card(k2, "Pagadas", f"{pagadas:,}", "Comisión > 0", "#059669")
    _kpi_card(k3, "Caídas", f"{caidas:,}", "Sin pago", "#dc2626")
    _kpi_card(k4, "% Efectividad", f"{pct:.2f}%", "Pagadas / Total", "#059669" if pct >= 75 else "#d97706")
    _kpi_card(k5, "Comisión Total", formatear_moneda(comision), "Pagada", color_borde)

    st.write("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Detalle Ventas",
        "📆 Ventas por Día/Mes",
        "🏆 Ranking Asesores",
        "📊 Transacciones"
    ])

    with tab1:
        st.markdown("#### Detalle de ventas móviles")
        cols_mostrar = [
            "Canal", "FECHA", "ASESOR", "Cliente", "Documento",
            "Departamento", "Transaccion", "COMISION", "Estado Pago"
        ]
        df_show = df_filtrado[cols_mostrar].copy()
        df_show["COMISION"] = pd.to_numeric(df_show["COMISION"], errors="coerce").fillna(0).map(formatear_moneda)

        st.dataframe(df_show, use_container_width=True, height=450)

        csv_export = df_filtrado.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="⬇️ Descargar CSV móvil completo",
            data=csv_export,
            file_name=f"detalle_movil_general_{filtro_mes.replace(' ', '_')}_{filtro_canal}.csv",
            mime="text/csv",
            key="dl_det_movil_general"
        )

    with tab2:
        st.markdown("#### Ventas móviles — Total vs Pagadas")
        df_periodo = ventas_movil_por_periodo_df(df_filtrado, filtro_mes)
        mostrar_grafico_barras_movil(df_periodo, filtro_mes)

        if not df_periodo.empty:
            tabla = df_periodo.copy()
            tabla["Comision"] = pd.to_numeric(tabla["Comision"], errors="coerce").fillna(0).map(formatear_moneda)

            total_row = pd.DataFrame([{
                "Fecha": "TOTAL",
                "Total Ventas": tabla["Total Ventas"].sum(),
                "Pagadas": tabla["Pagadas"].sum(),
                "Caidas": tabla["Caidas"].sum(),
                "Comision": formatear_moneda(pd.to_numeric(df_periodo["Comision"], errors="coerce").fillna(0).sum()),
                "% Efectividad": f"{(tabla['Pagadas'].sum() / tabla['Total Ventas'].sum() * 100):.2f}%" if tabla["Total Ventas"].sum() > 0 else "0%"
            }])

            tabla = pd.concat([tabla, total_row], ignore_index=True)
            st.markdown("#### Tabla")
            st.dataframe(tabla, use_container_width=True, height=420)

    with tab3:
        st.markdown("#### Ranking de asesores móviles")
        rank_asesor = ranking_asesores_movil_df(df_filtrado)
        if rank_asesor.empty:
            st.warning("Sin datos para asesores.")
        else:
            st.dataframe(rank_asesor, use_container_width=True, height=450)

    with tab4:
        st.markdown("#### Resumen por transacción")
        rank_transaccion = ranking_transaccion_movil_df(df_filtrado)
        if rank_transaccion.empty:
            st.warning("Sin datos para transacciones.")
        else:
            st.dataframe(rank_transaccion, use_container_width=True, height=450)




# =========================================================
# 10C. CONCILIACIÓN EXACTA FIJA — DEVELZ VS CLARO
# =========================================================

def _normalizar_sot_series(serie):
    """Normaliza SOT para cruces exactos."""
    s = serie.fillna("").astype(str).str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    s = s.replace(["nan", "NaN", "None", "NONE", "null", "NULL"], "")
    return s



def _obtener_documento_develz(df):
    """Obtiene DNI desde DEVELZ (Cliente - Documento)."""
    if "Cliente - Documento" in df.columns:
        return df["Cliente - Documento"].fillna("").astype(str).str.strip()

    if "Cliente - Nro Documento" in df.columns:
        return df["Cliente - Nro Documento"].fillna("").astype(str).str.strip()

    return pd.Series([""] * len(df), index=df.index)


def _df_develz_para_conciliacion(tabla_maestro, canal, filtro_mes):
    """Base DEVELZ para conciliación. Devuelve todas las ventas, incluso sin SOT."""
    df = get_tabla(tabla_maestro)
    if df.empty:
        return pd.DataFrame(columns=["Canal", "SOT", "Fecha_Develz", "Supervisor", "Cliente", "Departamento", "TIPIS"])

    df = df.copy()
    df["Canal"] = canal
    df["SOT"] = _normalizar_sot_series(_obtener_sot_develz(df))
    df["_FECHA_DT"] = _obtener_fecha_inst_develz(df)

    if filtro_mes != "Todos los meses":
        m, y = parse_mes_anio(filtro_mes)
        if m and y:
            df = df[(df["_FECHA_DT"].dt.month == m) & (df["_FECHA_DT"].dt.year == y)].copy()

    if df.empty:
        return pd.DataFrame(columns=["Canal", "SOT", "Fecha_Develz", "Supervisor", "Cliente", "Departamento", "TIPIS"])

    df["Fecha_Develz"] = df["_FECHA_DT"].dt.strftime("%d/%m/%Y").fillna("")
    df["Supervisor"] = _obtener_supervisor_develz(df)
    df["Cliente"] = _obtener_nombre_cliente_develz(df)
    df["Departamento"] = _obtener_departamento_develz(df)
    df["TIPIS"] = _obtener_tipis_develz(df)

    df["Documento"] = _obtener_documento_develz(df)
    return df[["Canal", "SOT", "Fecha_Develz", "Supervisor", "Cliente", "Documento", "Departamento", "TIPIS"]].copy()

def _df_claro_para_conciliacion(tabla_claro, canal, filtro_mes):
    """Base CLARO para conciliación, filtrada por fecha instalación si aplica."""
    df = preparar_fechas_fija(get_tabla(tabla_claro))
    if df.empty or "SOT" not in df.columns:
        return pd.DataFrame(columns=["Canal", "SOT", "Fecha_Claro", "Cliente", "Documento", "Comision_Claro", "Comisiones_Claro"])

    df = df.copy()
    df["Canal"] = canal
    df["SOT"] = _normalizar_sot_series(df["SOT"])
    df = df[df["SOT"] != ""].copy()

    if filtro_mes != "Todos los meses" and "FECHA INSTALACION" in df.columns:
        df = filtrar_por_mes_anio(df, "FECHA INSTALACION", filtro_mes)

    if df.empty:
        return pd.DataFrame(columns=["Canal", "SOT", "Fecha_Claro", "Cliente", "Documento", "Comision_Claro", "Comisiones_Claro"])

    df["Comision_Claro"] = obtener_comision_fija(df)

    if "COMISIONES" in df.columns:
        df["Comisiones_Claro"] = df["COMISIONES"].fillna("").astype(str).str.upper().str.strip().str.replace("Í", "I", regex=False)
    else:
        df["Comisiones_Claro"] = ""

    if "FECHA INSTALACION" in df.columns:
        df["Fecha_Claro"] = df["FECHA INSTALACION"].dt.strftime("%d/%m/%Y").fillna("")
    else:
        df["Fecha_Claro"] = ""

    # DNI en CLARO: prioridad NRO DOCUMENTO
    if "NRO DOCUMENTO" in df.columns:
        df["Documento"] = df["NRO DOCUMENTO"].fillna("").astype(str).str.strip()
    elif "DOCUMENTO" in df.columns:
        df["Documento"] = df["DOCUMENTO"].fillna("").astype(str).str.strip()
    elif "DNI" in df.columns:
        df["Documento"] = df["DNI"].fillna("").astype(str).str.strip()
    else:
        df["Documento"] = ""

    # Nombre de cliente en CLARO, si existe
    col_cli = encontrar_columna(df, [
        "CLIENTE", "Cliente", "NOMBRE CLIENTE", "Nombre Cliente",
        "NOMBRE", "Nombre", "Nombre del Cliente"
    ])
    if col_cli:
        df["Cliente"] = df[col_cli].fillna("").astype(str).str.strip()
    else:
        df["Cliente"] = ""

    df_res = df.groupby(["Canal", "SOT"], as_index=False).agg(
        Fecha_Claro=("Fecha_Claro", "first"),
        Cliente=("Cliente", "first"),
        Documento=("Documento", "first"),
        Comision_Claro=("Comision_Claro", "sum"),
        Comisiones_Claro=("Comisiones_Claro", lambda x: "SI" if (x.astype(str).str.upper().str.strip() == "SI").any() else "NO")
    )

    return df_res[["Canal", "SOT", "Fecha_Claro", "Cliente", "Documento", "Comision_Claro", "Comisiones_Claro"]].copy()


@st.cache_data(ttl=300)
def construir_conciliacion_fija(filtro_mes):
    """Conciliación exacta por canal entre CLARO y DEVELZ."""
    pares = [
        ("D&C", "[DATA DEVELZ].dbo.FIJA_DC", "dbo.CLARO_DC_FIJA"),
        ("Teletalk", "[DATA DEVELZ].dbo.FIJA_TELETALK", "dbo.CLARO_TELETALK_FIJA"),
    ]

    resumen = []
    faltan_develz = []
    faltan_claro = []
    cruce_ok = []

    for canal, tabla_dev, tabla_claro in pares:
        dev = _df_develz_para_conciliacion(tabla_dev, canal, filtro_mes)
        claro = _df_claro_para_conciliacion(tabla_claro, canal, filtro_mes)

        dev_sot = dev[dev["SOT"] != ""].copy()
        claro_sot = claro[claro["SOT"] != ""].copy()

        set_dev = set(dev_sot["SOT"].unique())
        set_claro = set(claro_sot["SOT"].unique())

        sot_claro_no_develz = sorted(set_claro - set_dev)
        sot_develz_no_claro = sorted(set_dev - set_claro)
        sot_ok = sorted(set_claro & set_dev)

        dev_sin_sot = int((dev["SOT"] == "").sum()) if not dev.empty else 0
        total_develz = int(len(dev))
        total_develz_con_sot = int(dev_sot["SOT"].nunique()) if not dev_sot.empty else 0
        total_claro = int(claro_sot["SOT"].nunique()) if not claro_sot.empty else 0

        resumen.append({
            "Canal": canal,
            "Total ventas DEVELZ": total_develz,
            "DEVELZ con SOT único": total_develz_con_sot,
            "DEVELZ sin SOT": dev_sin_sot,
            "Total SOT CLARO": total_claro,
            "SOT cruzados": len(sot_ok),
            "CLARO no está en DEVELZ": len(sot_claro_no_develz),
            "DEVELZ no está en CLARO": len(sot_develz_no_claro),
            "% Cruce CLARO vs DEVELZ": f"{(len(sot_ok) / total_claro * 100):.2f}%" if total_claro > 0 else "0%",
        })

        if sot_claro_no_develz:
            temp = claro_sot[claro_sot["SOT"].isin(sot_claro_no_develz)].copy()
            temp["Observación"] = "Está en CLARO, pero NO está en DEVELZ"
            faltan_develz.append(temp)

        if sot_develz_no_claro:
            temp = dev_sot[dev_sot["SOT"].isin(sot_develz_no_claro)].copy()
            temp["Observación"] = "Está en DEVELZ, pero NO está en CLARO"
            faltan_claro.append(temp)

        if sot_ok:
            temp = claro_sot[claro_sot["SOT"].isin(sot_ok)].merge(
                dev_sot[["Canal", "SOT", "Fecha_Develz", "Supervisor", "Cliente", "Documento", "Departamento", "TIPIS"]],
                on=["Canal", "SOT"],
                how="left"
            )
            temp["Observación"] = "Cruza correctamente"
            cruce_ok.append(temp)

    df_resumen = pd.DataFrame(resumen)
    df_faltan_develz = pd.concat(faltan_develz, ignore_index=True) if faltan_develz else pd.DataFrame()
    df_faltan_claro = pd.concat(faltan_claro, ignore_index=True) if faltan_claro else pd.DataFrame()
    df_ok = pd.concat(cruce_ok, ignore_index=True) if cruce_ok else pd.DataFrame()

    return df_resumen, df_faltan_develz, df_faltan_claro, df_ok

def mostrar_conciliacion_fija(filtro_mes, filtro_canal):
    """Pestaña visual de conciliación exacta."""
    st.markdown("#### Conciliación exacta CLARO vs DEVELZ")
    st.caption("Aquí se explican las diferencias entre lo que aparece en CLARO y lo que cruza contra DEVELZ.")

    df_resumen, df_faltan_develz, df_faltan_claro, df_ok = construir_conciliacion_fija(filtro_mes)

    if filtro_canal != "Todos":
        df_resumen = df_resumen[df_resumen["Canal"] == filtro_canal]
        if not df_faltan_develz.empty:
            df_faltan_develz = df_faltan_develz[df_faltan_develz["Canal"] == filtro_canal]
        if not df_faltan_claro.empty:
            df_faltan_claro = df_faltan_claro[df_faltan_claro["Canal"] == filtro_canal]
        if not df_ok.empty:
            df_ok = df_ok[df_ok["Canal"] == filtro_canal]

    if df_resumen.empty:
        st.warning("No hay datos para conciliar con los filtros seleccionados.")
        return

    total_claro = int(df_resumen["Total SOT CLARO"].sum())
    total_develz = int(df_resumen["Total ventas DEVELZ"].sum())
    total_ok = int(df_resumen["SOT cruzados"].sum())
    total_falta_dev = int(df_resumen["CLARO no está en DEVELZ"].sum())
    total_falta_claro = int(df_resumen["DEVELZ no está en CLARO"].sum())

    c1, c2, c3, c4, c5 = st.columns(5)

    def _mini_kpi(col, label, value, color):
        with col:
            st.markdown(
                f'<div style="background:rgba(255,255,255,.96);padding:14px;border-radius:14px;'
                f'border:2px solid {color};text-align:center;margin-bottom:8px;min-height:80px;">'
                f'<span style="color:#4b5563;font-weight:800;font-size:10px;text-transform:uppercase;display:block;">{label}</span>'
                f'<span style="color:{color};font-size:24px;font-weight:900;display:block;">{value:,}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    _mini_kpi(c1, "SOT CLARO", total_claro, "#0f4287")
    _mini_kpi(c2, "Ventas DEVELZ", total_develz, "#6d0b8c")
    _mini_kpi(c3, "Cruzan OK", total_ok, "#059669")
    _mini_kpi(c4, "Claro no en Develz", total_falta_dev, "#dc2626")
    _mini_kpi(c5, "Develz no en Claro", total_falta_claro, "#d97706")

    st.markdown("##### Resumen por canal")
    st.dataframe(df_resumen, use_container_width=True, height=160)

    sub1, sub2, sub3 = st.tabs([
        "🔴 CLARO no está en DEVELZ",
        "🟠 DEVELZ no está en CLARO",
        "🟢 Cruzan correctamente"
    ])

    with sub1:
        st.caption("Estos son los SOT que explican por qué CLARO puede tener más ventas que el detalle basado en DEVELZ.")
        if df_faltan_develz.empty:
            st.success("No hay SOT de CLARO faltantes en DEVELZ.")
        else:
            df_show = df_faltan_develz.copy()
            if "Comision_Claro" in df_show.columns:
                df_show["Comision_Claro"] = pd.to_numeric(df_show["Comision_Claro"], errors="coerce").fillna(0).map(formatear_moneda)
            st.dataframe(df_show, use_container_width=True, height=360)

            csv_1 = df_faltan_develz.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇️ Descargar CLARO no está en DEVELZ",
                data=csv_1,
                file_name=f"conciliacion_claro_no_develz_{filtro_mes.replace(' ', '_')}.csv",
                mime="text/csv",
                key="dl_claro_no_develz"
            )

    with sub2:
        st.caption("Estos son SOT registrados en DEVELZ que no tienen coincidencia en CLARO.")
        if df_faltan_claro.empty:
            st.success("No hay SOT de DEVELZ faltantes en CLARO.")
        else:
            st.dataframe(df_faltan_claro, use_container_width=True, height=360)

            csv_2 = df_faltan_claro.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇️ Descargar DEVELZ no está en CLARO",
                data=csv_2,
                file_name=f"conciliacion_develz_no_claro_{filtro_mes.replace(' ', '_')}.csv",
                mime="text/csv",
                key="dl_develz_no_claro"
            )

    with sub3:
        if df_ok.empty:
            st.warning("No hay cruces correctos con los filtros seleccionados.")
        else:
            df_show = df_ok.copy()
            if "Comision_Claro" in df_show.columns:
                df_show["Comision_Claro"] = pd.to_numeric(df_show["Comision_Claro"], errors="coerce").fillna(0).map(formatear_moneda)
            st.dataframe(df_show, use_container_width=True, height=360)





# =========================================================
# 11. SIDEBAR / NAVEGACIÓN
# =========================================================
OPCIONES_FIJA = [
    "Inicio: Reporte Comparativo",
    "Detalle Fija General",
    "D&C Factor Instalación", "D&C Factor F. Venta", "D&C IAE ASESOR",
    "Teletalk Factor Instalación", "Teletalk Factor F. Venta", "Teletalk IAE ASESOR",
]
OPCIONES_MOVIL = [
    "Inicio: Reporte Comparativo MOVIL",
    "Detalle Móvil General",
    "D&C Factor F. Venta MOVIL", "D&C IAE ASESOR MOVIL",
    "Teletalk Factor F. Venta MOVIL", "Teletalk IAE ASESOR MOVIL",
]

SEP_FIJA  = "📡 FIJA"
SEP_MOVIL = "📱 MÓVIL"
SEPARADORES = {SEP_FIJA, SEP_MOVIL}

todas_opciones = (
    [SEP_FIJA]  + OPCIONES_FIJA +
    [SEP_MOVIL] + OPCIONES_MOVIL
)

idx_sep_fija  = 0
idx_sep_movil = len(OPCIONES_FIJA) + 1

st.markdown(f"""
<style>
div[data-testid="stSidebarNav"] {{display:none}}

section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_fija + 1}),
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_movil + 1}) {{
    pointer-events: none;
    cursor: default;
    margin-top: 14px;
    margin-bottom: 2px;
}}
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_fija + 1}) input,
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_movil + 1}) input {{
    display: none !important;
}}
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_fija + 1}) div[data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] .stRadio > div > label:nth-child({idx_sep_movil + 1}) div[data-testid="stMarkdownContainer"] p {{
    font-weight: 900 !important;
    font-size: 15px !important;
    color: #1e3a5f !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("MENU DE REPORTES")

seleccion = st.sidebar.radio(
    "MENU DE REPORTES",
    todas_opciones,
    key="radio_unico",
    label_visibility="collapsed",
)

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
        v_dc, c_dc = obtener_metricas_fija("dbo.CLARO_DC_FIJA",       sel_inst, sel_gene)
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
        st.write("---")
        filtro = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="dc_iae_inst")
        df_liq = obtener_reporte_liquidado("dbo.CLARO_DC_FIJA","[DATA DEVELZ].dbo.FIJA_DC", filtro)
        if df_liq.empty: st.warning("Sin datos.")
        else:
            filtro_a = st.selectbox("Selecciona Asesor", ["Todos"]+sorted(df_liq["ASESOR"].fillna("Sin Asesor").unique().tolist()), key="dc_iae_asesor")
            df_f = df_liq[df_liq["ASESOR"]==filtro_a].copy() if filtro_a!="Todos" else df_liq.copy()
            st.markdown("### Ranking de Asesores")
            mostrar_tabla_ranking(construir_ranking_asesores(df_f))

    elif opcion == "Teletalk Factor Instalación":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor Instalación</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE INSTALACIÓN</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="tt_fi_inst")
        mostrar_factor_fija("dbo.CLARO_TELETALK_FIJA", "FECHA INSTALACION", filtro, "tt")

    elif opcion == "Teletalk Factor F. Venta":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor F. Venta</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Venta", obtener_meses_fija("FECHA GENERACION"), key="tt_fv_gene")
        mostrar_factor_fija("dbo.CLARO_TELETALK_FIJA", "FECHA GENERACION", filtro, "tt")

    elif opcion == "Teletalk IAE ASESOR":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk IAE ASESOR</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Instalación", obtener_meses_fija("FECHA INSTALACION"), key="tt_iae_inst")
        df_liq = obtener_reporte_liquidado("dbo.CLARO_TELETALK_FIJA","[DATA DEVELZ].dbo.FIJA_TELETALK", filtro)
        if df_liq.empty: st.warning("Sin datos.")
        else:
            filtro_a = st.selectbox("Selecciona Asesor", ["Todos"]+sorted(df_liq["ASESOR"].fillna("Sin Asesor").unique().tolist()), key="tt_iae_asesor")
            df_f = df_liq[df_liq["ASESOR"]==filtro_a].copy() if filtro_a!="Todos" else df_liq.copy()
            st.markdown("### Ranking de Asesores")
            mostrar_tabla_ranking(construir_ranking_asesores(df_f))

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

        todos_op = sorted(set(obtener_meses_movil("FECHA OPERACION",["CLARO_DC_MOVIL.csv"])+
            obtener_meses_movil("FECHA OPERACION",["CLARO_TELETALK_MOVIL.csv"]))-{"Todos los meses"},
            key=lambda s:(int(s.split()[1]),MESES_MAP.get(s.split()[0].lower(),0)))
        todos_ca = sorted(set(meses_carga_dc+obtener_meses_movil("FECHA CARGA",["CLARO_TELETALK_MOVIL.csv"]))-{"Todos los meses"},
            key=lambda s:(int(s.split()[1]),MESES_MAP.get(s.split()[0].lower(),0)))

        col_dc, col_filtros, col_tt = st.columns([1,1.2,1])
        with col_filtros:
            st.markdown('<div class="block-filter">', unsafe_allow_html=True)
            sel_op = st.selectbox("FECHA DE VENTA", ["Todos los meses"]+todos_op, key="movil_comp_fecha_operacion")
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

        t_dc, p_dc, a_dc, c_dc = kpi_movil(df_dc_c)
        t_tt, p_tt, a_tt, c_tt = kpi_movil(df_tt_c)

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
        mostrar_factor_movil("dbo.CLARO_DC_MOVIL", "FECHA OPERACION", filtro, "dc")

    elif opcion_movil == "D&C IAE ASESOR MOVIL":
        set_bg(img_dc)
        st.markdown('<div class="section-title-dc">D&C IAE ASESOR MÓVIL</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Operación", obtener_meses_movil("FECHA OPERACION",["CLARO_DC_MOVIL.csv"]), key="dc_movil_iae")
        mostrar_iae_movil("dbo.CLARO_DC_MOVIL", "FECHA OPERACION", filtro, "dc_movil_iae_asesor", "dc")

    elif opcion_movil == "Teletalk Factor F. Venta MOVIL":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk Factor F. Venta MÓVIL</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-subtitle-tt">AVANCE POR FECHA DE VENTA</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Venta", obtener_meses_movil("FECHA OPERACION",["CLARO_TELETALK_MOVIL.csv"]), key="tt_movil_fv")
        mostrar_factor_movil("dbo.CLARO_TELETALK_MOVIL", "FECHA OPERACION", filtro, "tt")

    elif opcion_movil == "Teletalk IAE ASESOR MOVIL":
        set_bg(img_tt)
        st.markdown('<div class="section-title-tt">Teletalk IAE ASESOR MÓVIL</div>', unsafe_allow_html=True)
        st.write("---")
        filtro = st.selectbox("Fecha de Carga", obtener_meses_movil("FECHA CARGA",["CLARO_TELETALK_MOVIL.csv"]), key="tt_movil_iae")
        mostrar_iae_movil("dbo.CLARO_TELETALK_MOVIL", "FECHA CARGA", filtro, "tt_movil_iae_asesor", "tt")
