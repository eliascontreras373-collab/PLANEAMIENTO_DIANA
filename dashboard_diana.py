import streamlit as st
import pandas as pd
import pyodbc
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
        background_style = f'background-image: url("data:image/png;base64,{b64_encoded}");'

    st.markdown(f"""
        <style>
        .stApp {{
            {background_style}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .main-title {{
            text-align: center;
            color: black;
            font-weight: 900;
            font-size: 52px;
            margin-bottom: 6px;
        }}

        .sub-title {{
            text-align: center;
            font-weight: 700;
            font-size: 20px;
            color: #004a99;
            margin-bottom: 25px;
        }}

        .kpi-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 20px;
        }}

        .box-header-dc {{
            background: linear-gradient(135deg, #0f4287, #2563eb);
            color: white;
            width: 320px;
            padding: 18px 22px;
            border-radius: 22px;
            text-align: center;
            font-weight: 900;
            font-size: 16px;
            margin-bottom: 18px;
            box-shadow: 0 18px 40px rgba(15,66,135,0.18);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .box-header-tt {{
            background: linear-gradient(135deg, #6d0b8c, #9333ea);
            color: white;
            width: 320px;
            padding: 18px 22px;
            border-radius: 22px;
            text-align: center;
            font-weight: 900;
            font-size: 16px;
            margin-bottom: 18px;
            box-shadow: 0 18px 40px rgba(109,11,140,0.18);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .data-card-dc {{
            background-color: rgba(255,255,255,0.96);
            width: 320px;
            padding: 24px 24px;
            border-radius: 24px;
            border: 2px solid #0f4287;
            text-align: center;
            margin-bottom: 16px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.08);
        }}

        .data-card-tt {{
            background-color: rgba(255,255,255,0.96);
            width: 320px;
            padding: 24px 24px;
            border-radius: 24px;
            border: 2px solid #6d0b8c;
            text-align: center;
            margin-bottom: 16px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.08);
        }}

        .label {{
            color: #4b5563;
            font-weight: 800;
            font-size: 13px;
            text-transform: uppercase;
            display: block;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
        }}

        .value {{
            color: #111827;
            font-size: 42px;
            font-weight: 900;
            display: block;
            line-height: 1.05;
        }}

        .section-title-dc {{
            color: #004a99;
            font-size: 38px;
            font-weight: 900;
            margin-bottom: 10px;
        }}

        .section-title-tt {{
            color: #70008f;
            font-size: 38px;
            font-weight: 900;
            margin-bottom: 10px;
        }}

        .small-subtitle-dc {{
            color: #004a99;
            font-weight: 800;
            font-size: 18px;
            margin-bottom: 10px;
        }}

        .small-subtitle-tt {{
            color: #70008f;
            font-weight: 800;
            font-size: 18px;
            margin-bottom: 10px;
        }}

        .block-filter {{
            background-color: rgba(255,255,255,0.85);
            padding: 16px;
            border-radius: 16px;
            border: 1px solid #d9d9d9;
            margin-top: 20px;
            margin-bottom: 20px;
        }}

        .stExpander {{
            border-radius: 12px !important;
            overflow: hidden;
        }}
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# 3. CONEXIÓN
# =========================================================
def conectar():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=127.0.0.1,1433;"
        "DATABASE=DATA CLARO;"
        "Trusted_Connection=yes;"
    )


# =========================================================
# 4. FUNCIONES AUXILIARES
# =========================================================
def formatear_moneda(valor):
    try:
        return f"S/ {float(valor):,.2f}"
    except:
        return "S/ 0.00"


def parse_mes_anio(fecha_texto):
    meses_map = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }

    if not fecha_texto or fecha_texto == "Todos los meses":
        return None, None

    parts = fecha_texto.strip().lower().split()
    if len(parts) == 2 and parts[0] in meses_map and parts[1].isdigit():
        return meses_map[parts[0]], int(parts[1])

    return None, None


# =========================================================
# 5. CONSULTAS SQL
# =========================================================
@st.cache_data(ttl=300)
def obtener_meses(columna):
    try:
        conn = conectar()
        query = f"""
            SELECT DISTINCT FORMAT([{columna}], 'MMMM yyyy', 'es-ES') AS Mes
            FROM dbo.CLARO_DC_FIJA
            WHERE [{columna}] IS NOT NULL

            UNION

            SELECT DISTINCT FORMAT([{columna}], 'MMMM yyyy', 'es-ES') AS Mes
            FROM dbo.CLARO_TELETALK_FIJA
            WHERE [{columna}] IS NOT NULL
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            return ["Todos los meses"]

        meses = [m for m in df["Mes"].dropna().tolist() if str(m).strip() != ""]
        return ["Todos los meses"] + sorted(meses)
    except:
        return ["Todos los meses"]


@st.cache_data(ttl=300)
def obtener_metricas(tabla, f_inst, f_gene):
    try:
        conn = conectar()
        condiciones = []

        if f_inst != "Todos los meses":
            condiciones.append(f"FORMAT([FECHA INSTALACION], 'MMMM yyyy', 'es-ES') = '{f_inst}'")

        if f_gene != "Todos los meses":
            condiciones.append(f"FORMAT([FECHA GENERACION], 'MMMM yyyy', 'es-ES') = '{f_gene}'")

        where_clause = " WHERE " + " AND ".join(condiciones) if condiciones else ""

        query = f"""
            SELECT
                COUNT(DISTINCT SOT) AS V,
                SUM(TRY_CAST(COMISION AS DECIMAL(18,2))) AS C
            FROM {tabla}
            {where_clause}
        """
        df = pd.read_sql(query, conn)
        conn.close()

        return int(df["V"].iloc[0] or 0), float(df["C"].iloc[0] or 0.0)
    except:
        return 0, 0.0


@st.cache_data(ttl=300)
def obtener_reporte_liquidado(ventas_tabla="dbo.CLARO_DC_FIJA",
                              maestro_tabla="[DATA DEVELZ].dbo.FIJA_DC",
                              fecha_instalacion="Todos los meses"):
    try:
        conn = conectar()
        filtro_inst = ""

        month_num, year = parse_mes_anio(fecha_instalacion)
        if month_num and year:
            filtro_inst = f"""
                WHERE MONTH(v.[FECHA INSTALACION]) = {month_num}
                  AND YEAR(v.[FECHA INSTALACION]) = {year}
            """

        query = f"""
            SELECT
                v.SOT,
                COALESCE(NULLIF(m.USUARIO, ''), 'Sin Asesor') AS ASESOR,
                COALESCE(
                    NULLIF(
                        LTRIM(RTRIM(
                            ISNULL(m.[Cliente - Nombre], '') + ' ' +
                            ISNULL(m.[Cliente - Apellido Paterno], '')
                        )),
                        ''
                    ),
                    'Sin Datos'
                ) AS [Nombre del Cliente],
                TRY_CAST(v.COMISION AS DECIMAL(18,2)) AS COMISION,
                v.COMISIONES,
                CASE
                    WHEN TRY_CAST(v.COMISION AS DECIMAL(18,2)) > 0 THEN N'SÍ'
                    ELSE N'NO'
                END AS [¿Pagado?]
            FROM {ventas_tabla} AS v
            LEFT JOIN {maestro_tabla} AS m
                ON LTRIM(RTRIM(v.SOT)) = LTRIM(RTRIM(m.[Back Office - Sot]))
            {filtro_inst}
        """

        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    except Exception as e:
        st.error(f"Error al cargar el reporte liquidado: {e}")
        return pd.DataFrame(columns=["SOT", "ASESOR", "Nombre del Cliente", "COMISION", "COMISIONES", "¿Pagado?"])


@st.cache_data(ttl=300)
def obtener_factor_instalacion_resumen(tabla, fecha_instalacion="Todos los meses"):
    try:
        conn = conectar()
        filtro_inst = ""

        month_num, year = parse_mes_anio(fecha_instalacion)
        if month_num and year:
            filtro_inst = f"""
                WHERE MONTH([FECHA INSTALACION]) = {month_num}
                  AND YEAR([FECHA INSTALACION]) = {year}
            """

        query = f"""
            SELECT
                YEAR([FECHA INSTALACION]) AS Año,
                FORMAT([FECHA INSTALACION], 'MMMM', 'es-ES') AS Mes,
                COUNT(DISTINCT SOT) AS Ventas,
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) IN ('SI', 'SÍ', 'YES', 'Y')
                    THEN 1 ELSE 0 END) AS [PORTABILIDAD SI],
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) NOT IN ('SI', 'SÍ', 'YES', 'Y')
                    OR [PORTABILIDAD] IS NULL
                    THEN 1 ELSE 0 END) AS [PORTABILIDAD NO],
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%FTTH%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%FTTH%'
                    THEN 1 ELSE 0 END) AS FTTH,
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%HFC%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%HFC%'
                    THEN 1 ELSE 0 END) AS HFC,
                SUM(TRY_CAST([COMISION] AS DECIMAL(18,2))) AS [S/.]
            FROM {tabla}
            {filtro_inst}
            GROUP BY
                YEAR([FECHA INSTALACION]),
                MONTH([FECHA INSTALACION]),
                FORMAT([FECHA INSTALACION], 'MMMM', 'es-ES')
            ORDER BY
                YEAR([FECHA INSTALACION]),
                MONTH([FECHA INSTALACION]);
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df["Mes"] = df["Mes"].str.capitalize()

        return df

    except Exception as e:
        st.error(f"Error al cargar el factor de instalación: {e}")
        return pd.DataFrame(columns=["Año", "Mes", "Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."])


@st.cache_data(ttl=300)
def obtener_factor_instalacion_detallado(tabla, fecha_instalacion="Todos los meses"):
    try:
        conn = conectar()
        filtro_inst = ""

        month_num, year = parse_mes_anio(fecha_instalacion)
        if month_num and year:
            filtro_inst = f"""
                WHERE MONTH([FECHA INSTALACION]) = {month_num}
                  AND YEAR([FECHA INSTALACION]) = {year}
            """

        query = f"""
            SELECT
                YEAR([FECHA INSTALACION]) AS Año,
                FORMAT([FECHA INSTALACION], 'MMMM', 'es-ES') AS Mes,
                MONTH([FECHA INSTALACION]) AS MesNum,
                DAY([FECHA INSTALACION]) AS Dia,
                COUNT(DISTINCT SOT) AS Ventas,
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) IN ('SI', 'SÍ', 'YES', 'Y')
                    THEN 1 ELSE 0 END) AS Porta_SI,
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) NOT IN ('SI', 'SÍ', 'YES', 'Y')
                      OR [PORTABILIDAD] IS NULL
                    THEN 1 ELSE 0 END) AS Porta_NO,
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%FTTH%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%FTTH%'
                    THEN 1 ELSE 0 END) AS FTTH,
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%HFC%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%HFC%'
                    THEN 1 ELSE 0 END) AS HFC,
                SUM(TRY_CAST([COMISION] AS DECIMAL(18,2))) AS Monto
            FROM {tabla}
            {filtro_inst}
            GROUP BY
                YEAR([FECHA INSTALACION]),
                MONTH([FECHA INSTALACION]),
                FORMAT([FECHA INSTALACION], 'MMMM', 'es-ES'),
                DAY([FECHA INSTALACION])
            ORDER BY
                YEAR([FECHA INSTALACION]) DESC,
                MONTH([FECHA INSTALACION]) DESC,
                DAY([FECHA INSTALACION]) ASC;
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df["Mes"] = df["Mes"].str.capitalize()

        return df

    except Exception as e:
        st.error(f"Error al cargar el factor de instalación detallado: {e}")
        return pd.DataFrame(columns=["Año", "Mes", "MesNum", "Dia", "Ventas", "Porta_SI", "Porta_NO", "FTTH", "HFC", "Monto"])



@st.cache_data(ttl=300)
def obtener_factor_fecha_venta_resumen(tabla, fecha_generacion="Todos los meses"):
    try:
        conn = conectar()
        filtro_gene = ""

        month_num, year = parse_mes_anio(fecha_generacion)
        if month_num and year:
            filtro_gene = f"""
                WHERE MONTH([FECHA GENERACION]) = {month_num}
                  AND YEAR([FECHA GENERACION]) = {year}
            """

        query = f"""
            SELECT
                YEAR([FECHA GENERACION]) AS Año,
                FORMAT([FECHA GENERACION], 'MMMM', 'es-ES') AS Mes,
                COUNT(DISTINCT SOT) AS Ventas,
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) IN ('SI', 'SÍ', 'YES', 'Y')
                    THEN 1 ELSE 0 END) AS [PORTABILIDAD SI],
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) NOT IN ('SI', 'SÍ', 'YES', 'Y')
                    OR [PORTABILIDAD] IS NULL
                    THEN 1 ELSE 0 END) AS [PORTABILIDAD NO],
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%FTTH%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%FTTH%'
                    THEN 1 ELSE 0 END) AS FTTH,
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%HFC%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%HFC%'
                    THEN 1 ELSE 0 END) AS HFC,
                SUM(TRY_CAST([COMISION] AS DECIMAL(18,2))) AS [S/.]
            FROM {tabla}
            {filtro_gene}
            GROUP BY
                YEAR([FECHA GENERACION]),
                MONTH([FECHA GENERACION]),
                FORMAT([FECHA GENERACION], 'MMMM', 'es-ES')
            ORDER BY
                YEAR([FECHA GENERACION]),
                MONTH([FECHA GENERACION]);
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df["Mes"] = df["Mes"].str.capitalize()

        return df

    except Exception as e:
        st.error(f"Error al cargar el factor de fecha de venta: {e}")
        return pd.DataFrame(columns=["Año", "Mes", "Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."])


@st.cache_data(ttl=300)
def obtener_factor_fecha_venta_detallado(tabla, fecha_generacion="Todos los meses"):
    try:
        conn = conectar()
        filtro_gene = ""

        month_num, year = parse_mes_anio(fecha_generacion)
        if month_num and year:
            filtro_gene = f"""
                WHERE MONTH([FECHA GENERACION]) = {month_num}
                  AND YEAR([FECHA GENERACION]) = {year}
            """

        query = f"""
            SELECT
                YEAR([FECHA GENERACION]) AS Año,
                FORMAT([FECHA GENERACION], 'MMMM', 'es-ES') AS Mes,
                MONTH([FECHA GENERACION]) AS MesNum,
                DAY([FECHA GENERACION]) AS Dia,
                COUNT(DISTINCT SOT) AS Ventas,
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) IN ('SI', 'SÍ', 'YES', 'Y')
                    THEN 1 ELSE 0 END) AS Porta_SI,
                SUM(CASE
                    WHEN UPPER(LTRIM(RTRIM([PORTABILIDAD]))) NOT IN ('SI', 'SÍ', 'YES', 'Y')
                      OR [PORTABILIDAD] IS NULL
                    THEN 1 ELSE 0 END) AS Porta_NO,
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%FTTH%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%FTTH%'
                    THEN 1 ELSE 0 END) AS FTTH,
                SUM(CASE
                    WHEN UPPER(ISNULL([SERVICIO], '')) LIKE '%HFC%'
                      OR UPPER(ISNULL([TIPO TRABAJO], '')) LIKE '%HFC%'
                    THEN 1 ELSE 0 END) AS HFC,
                SUM(TRY_CAST([COMISION] AS DECIMAL(18,2))) AS Monto
            FROM {tabla}
            {filtro_gene}
            GROUP BY
                YEAR([FECHA GENERACION]),
                MONTH([FECHA GENERACION]),
                FORMAT([FECHA GENERACION], 'MMMM', 'es-ES'),
                DAY([FECHA GENERACION])
            ORDER BY
                YEAR([FECHA GENERACION]) DESC,
                MONTH([FECHA GENERACION]) DESC,
                DAY([FECHA GENERACION]) ASC;
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df["Mes"] = df["Mes"].str.capitalize()

        return df

    except Exception as e:
        st.error(f"Error al cargar el factor fecha de venta detallado: {e}")
        return pd.DataFrame(columns=["Año", "Mes", "MesNum", "Dia", "Ventas", "Porta_SI", "Porta_NO", "FTTH", "HFC", "Monto"])


def construir_ranking_asesores(df_filtrado):
    if df_filtrado.empty:
        return pd.DataFrame(columns=[
            "Rank", "ASESOR", "Cantidad_Ventas",
            "Ventas_Pagadas", "Ventas_No_Pagadas", "Total_Comision"
        ])

    df_filtrado = df_filtrado.copy()
    comisiones_norm = (
        df_filtrado["COMISIONES"]
        .astype(str)
        .str.upper()
        .str.replace('Í', 'I', regex=False)
        .str.strip()
    )
    df_filtrado["COMISIONES_NORMALIZADO"] = comisiones_norm

    ranking = (
        df_filtrado.groupby("ASESOR", dropna=False)
        .agg(
            Total_Comision=("COMISION", "sum"),
            Ventas_Pagadas=("SOT", lambda x: x[df_filtrado.loc[x.index, "COMISIONES_NORMALIZADO"] == "SI"].nunique()),
            Ventas_No_Pagadas=("SOT", lambda x: x[df_filtrado.loc[x.index, "COMISIONES_NORMALIZADO"] == "NO"].nunique())
        )
        .reset_index()
        .sort_values(by="Total_Comision", ascending=False)
    )

    ranking["Rank"] = ranking["Total_Comision"].rank(method="dense", ascending=False).astype(int)
    ranking["Cantidad_Ventas"] = ranking["Ventas_Pagadas"] + ranking["Ventas_No_Pagadas"]

    ranking = ranking[[
        "Rank", "ASESOR", "Cantidad_Ventas",
        "Ventas_Pagadas", "Ventas_No_Pagadas", "Total_Comision"
    ]]

    total_row = pd.DataFrame([{
        "Rank": "Total",
        "ASESOR": "",
        "Cantidad_Ventas": ranking["Cantidad_Ventas"].sum(),
        "Ventas_Pagadas": ranking["Ventas_Pagadas"].sum(),
        "Ventas_No_Pagadas": ranking["Ventas_No_Pagadas"].sum(),
        "Total_Comision": ranking["Total_Comision"].sum()
    }])

    ranking_con_total = pd.concat([ranking, total_row], ignore_index=True)
    return ranking_con_total


def mostrar_tabla_ranking(ranking_con_total):
    if ranking_con_total.empty:
        st.warning("No se encontraron datos para el ranking.")
        return

    ranking_style = (
        ranking_con_total.style
        .format({"Total_Comision": "S/ {:,.2f}"})
        .set_table_attributes('style="width:1000px; table-layout: fixed; background-color: white;"')
        .set_table_styles([
            {"selector": "th", "props": [("text-align", "center"), ("font-size", "14px"), ("padding", "8px"), ("background-color", "white")]},
            {"selector": "td", "props": [("padding", "8px"), ("font-size", "13px"), ("white-space", "nowrap"), ("overflow", "hidden"), ("text-overflow", "ellipsis"), ("background-color", "white")]},
            {"selector": "th.col0, td.col0", "props": [("width", "60px"), ("text-align", "center")]},
            {"selector": "th.col1, td.col1", "props": [("width", "220px"), ("text-align", "left")]},
            {"selector": "th.col2, td.col2", "props": [("width", "90px"), ("text-align", "center")]},
            {"selector": "th.col3, td.col3", "props": [("width", "110px"), ("text-align", "center")]},
            {"selector": "th.col4, td.col4", "props": [("width", "110px"), ("text-align", "center")]},
            {"selector": "th.col5, td.col5", "props": [("width", "120px"), ("text-align", "center")]},
        ])
        .set_properties(**{"text-align": "center"}, subset=["Rank", "Cantidad_Ventas", "Ventas_Pagadas", "Ventas_No_Pagadas", "Total_Comision"])
        .set_properties(**{"text-align": "left"}, subset=["ASESOR"])
    )
    st.table(ranking_style)


def mostrar_expanders_factor_instalacion(df_detalle, color="dc"):
    if df_detalle.empty:
        st.warning("No se encontraron datos para mostrar.")
        return

    periodos = (
        df_detalle[["Año", "Mes", "MesNum"]]
        .drop_duplicates()
        .sort_values(by=["Año", "MesNum"], ascending=[False, False])
    )

    for _, p in periodos.iterrows():
        datos_mes = df_detalle[
            (df_detalle["Año"] == p["Año"]) &
            (df_detalle["Mes"] == p["Mes"]) &
            (df_detalle["MesNum"] == p["MesNum"])
        ].copy()

        total_ventas = int(datos_mes["Ventas"].sum())
        total_monto = float(datos_mes["Monto"].sum() or 0)

        icono = "🔵" if color == "dc" else "🟣"

        with st.expander(
            f"{icono} {p['Mes']} {p['Año']}  |  Ventas: {total_ventas}  |  Total: {formatear_moneda(total_monto)}",
            expanded=False
        ):
            df_tab = datos_mes[["Dia", "Ventas", "Porta_SI", "Porta_NO", "FTTH", "HFC", "Monto"]].copy()
            df_tab["Monto"] = df_tab["Monto"].map(formatear_moneda)
            st.table(df_tab)


# =========================================================
# 6. RUTAS DE IMÁGENES
# =========================================================
ruta_base = "C:/Users/Lenovo/Desktop/DIANA PYTHON/"
img_caratula = ruta_base + "caratula.png.jpg"
img_dc = ruta_base + "34bab75f-2b2e-455e-8935-377abf566b76.jpg"
img_tt = ruta_base + "ab3ac40e-1612-430f-bb3a-817d24b709db.jpg"


# =========================================================
# 7. SIDEBAR / NAVEGACIÓN
# =========================================================
st.sidebar.title("MENU DE REPORTES")
opcion = st.sidebar.radio("Ir a:", [
    "Inicio: Reporte Comparativo",
    "D&C Factor Instalación",
    "D&C Factor F. Venta",
    "D&C IAE ASESOR",
    "Teletalk Factor Instalación",
    "Teletalk Factor F. Venta",
    "Teletalk IAE ASESOR"
])


# =========================================================
# 8. VISTAS
# =========================================================

# ---------------------------------------------------------
# INICIO
# ---------------------------------------------------------
if opcion == "Inicio: Reporte Comparativo":
    set_bg(img_caratula)

    st.markdown('<div class="main-title">REPORTE COMPARATIVO</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">D&C DIGITAL GROUP <span style="color:black">vs</span> '
        '<span style="color:#70008f">TELETALK CONTACT CENTER</span></div>',
        unsafe_allow_html=True
    )

    col_dc, col_filtros, col_tt = st.columns([1, 1.2, 1])

    meses_inst = obtener_meses("FECHA INSTALACION")
    meses_gene = obtener_meses("FECHA GENERACION")

    with col_filtros:
        st.markdown('<div class="block-filter">', unsafe_allow_html=True)
        sel_inst = st.selectbox("FECHA INSTALACIÓN", meses_inst, key="sel_inst")
        sel_gene = st.selectbox("FECHA DE VENTA", meses_gene, key="sel_gene")
        st.markdown('</div>', unsafe_allow_html=True)

    v_dc, c_dc = obtener_metricas("dbo.CLARO_DC_FIJA", sel_inst, sel_gene)
    v_tt, c_tt = obtener_metricas("dbo.CLARO_TELETALK_FIJA", sel_inst, sel_gene)

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
            </div>
        """, unsafe_allow_html=True)

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
            </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# D&C FACTOR INSTALACIÓN
# ---------------------------------------------------------
elif opcion == "D&C Factor Instalación":
    set_bg(img_dc)

    st.markdown('<div class="section-title-dc">D&C Factor Instalación</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-subtitle-dc">AVANCE DE FACTOR ANUAL POR FECHA DE INSTALACIÓN</div>', unsafe_allow_html=True)
    st.write("---")

    meses_inst = obtener_meses("FECHA INSTALACION")
    filtro_inst = st.selectbox("Fecha de Instalación", meses_inst, key="filtro_inst_factor_instalacion")

    col1, col2 = st.columns([1.1, 1.6])

    with col1:
        st.markdown("### Resumen")
        df_factor = obtener_factor_instalacion_resumen("dbo.CLARO_DC_FIJA", filtro_inst)

        if df_factor.empty:
            st.warning("No se encontraron datos para la vista de Factor Instalación.")
        else:
            total_row = pd.DataFrame([{
                "Año": "Total",
                "Mes": "",
                "Ventas": df_factor["Ventas"].sum(),
                "PORTABILIDAD SI": df_factor["PORTABILIDAD SI"].sum(),
                "PORTABILIDAD NO": df_factor["PORTABILIDAD NO"].sum(),
                "FTTH": df_factor["FTTH"].sum(),
                "HFC": df_factor["HFC"].sum(),
                "S/.": df_factor["S/."].sum()
            }])

            df_display = pd.concat([df_factor, total_row], ignore_index=True)
            df_display["S/."] = df_display["S/."].map(formatear_moneda)

            table_style = (
                df_display.style
                .set_table_styles([
                    {"selector": "th", "props": [("background-color", "white"), ("color", "#0f4287"), ("font-size", "13px"), ("text-align", "center"), ("border-bottom", "2px solid #ddd")]},
                    {"selector": "td", "props": [("padding", "10px 8px"), ("font-size", "13px"), ("border-bottom", "1px solid #eee"), ("background-color", "white")]},
                ])
                .set_properties(subset=["Año", "Mes"], **{"text-align": "left"})
                .set_properties(subset=["Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."], **{"text-align": "center"})
            )

            st.table(table_style)

    with col2:
        st.markdown("### Detalle desplegable")
        df_detalle = obtener_factor_instalacion_detallado("dbo.CLARO_DC_FIJA", filtro_inst)
        mostrar_expanders_factor_instalacion(df_detalle, color="dc")


# ---------------------------------------------------------
# D&C FACTOR F. VENTA
# ---------------------------------------------------------
elif opcion == "D&C Factor F. Venta":
    set_bg(img_dc)

    st.markdown('<div class="section-title-dc">D&C Factor F. Venta</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-subtitle-dc">AVANCE DE FACTOR ANUAL POR FECHA DE VENTA</div>', unsafe_allow_html=True)
    st.write("---")

    meses_gene = obtener_meses("FECHA GENERACION")
    filtro_gene = st.selectbox("Fecha de Venta", meses_gene, key="filtro_gene_factor_venta")

    col1, col2 = st.columns([1.1, 1.6])

    with col1:
        st.markdown("### Resumen")
        df_factor_venta = obtener_factor_fecha_venta_resumen("dbo.CLARO_DC_FIJA", filtro_gene)

        if df_factor_venta.empty:
            st.warning("No se encontraron datos para la vista de Factor Fecha de Venta.")
        else:
            total_row = pd.DataFrame([{
                "Año": "Total",
                "Mes": "",
                "Ventas": df_factor_venta["Ventas"].sum(),
                "PORTABILIDAD SI": df_factor_venta["PORTABILIDAD SI"].sum(),
                "PORTABILIDAD NO": df_factor_venta["PORTABILIDAD NO"].sum(),
                "FTTH": df_factor_venta["FTTH"].sum(),
                "HFC": df_factor_venta["HFC"].sum(),
                "S/.": df_factor_venta["S/."].sum()
            }])

            df_display_venta = pd.concat([df_factor_venta, total_row], ignore_index=True)
            df_display_venta["S/."] = df_display_venta["S/."].map(formatear_moneda)

            table_style_venta = (
                df_display_venta.style
                .set_table_styles([
                    {"selector": "th", "props": [("background-color", "white"), ("color", "#0f4287"), ("font-size", "13px"), ("text-align", "center"), ("border-bottom", "2px solid #ddd")]},
                    {"selector": "td", "props": [("padding", "10px 8px"), ("font-size", "13px"), ("border-bottom", "1px solid #eee"), ("background-color", "white")]},
                ])
                .set_properties(subset=["Año", "Mes"], **{"text-align": "left"})
                .set_properties(subset=["Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."], **{"text-align": "center"})
            )

            st.table(table_style_venta)

    with col2:
        st.markdown("### Detalle desplegable")
        df_detalle_venta = obtener_factor_fecha_venta_detallado("dbo.CLARO_DC_FIJA", filtro_gene)
        mostrar_expanders_factor_instalacion(df_detalle_venta, color="dc")


# ---------------------------------------------------------
# D&C IAE ASESOR
# ---------------------------------------------------------
elif opcion == "D&C IAE ASESOR":
    set_bg(img_dc)
    st.markdown('<div class="section-title-dc">D&C IAE ASESOR</div>', unsafe_allow_html=True)
    st.write("---")

    meses_inst = obtener_meses("FECHA INSTALACION")
    filt_inst = st.selectbox("Fecha de Instalación", meses_inst, key="filtro_inst_iae")

    df_liquidado = obtener_reporte_liquidado(
        ventas_tabla="dbo.CLARO_DC_FIJA",
        maestro_tabla="[DATA DEVELZ].dbo.FIJA_DC",
        fecha_instalacion=filt_inst
    )

    if df_liquidado.empty:
        st.warning("No se encontraron datos para el reporte liquidado.")
    else:
        asesores = ["Todos"] + sorted(df_liquidado["ASESOR"].fillna("Sin Asesor").unique().tolist())
        filtro_asesor = st.selectbox("Selecciona Asesor", asesores, key="filtro_asesor_iae")

        if filtro_asesor != "Todos":
            df_filtrado = df_liquidado[df_liquidado["ASESOR"] == filtro_asesor].copy()
        else:
            df_filtrado = df_liquidado.copy()

        st.markdown("### Ranking de Asesores")
        ranking_con_total = construir_ranking_asesores(df_filtrado)
        mostrar_tabla_ranking(ranking_con_total)



# ---------------------------------------------------------
# TELETALK FACTOR INSTALACIÓN
# ---------------------------------------------------------
elif opcion == "Teletalk Factor Instalación":
    set_bg(img_tt)

    st.markdown('<div class="section-title-tt">Teletalk Factor Instalación</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE INSTALACIÓN</div>', unsafe_allow_html=True)
    st.write("---")

    meses_inst = obtener_meses("FECHA INSTALACION")
    filtro_inst_tt = st.selectbox("Fecha de Instalación", meses_inst, key="filtro_inst_factor_instalacion_tt")

    col1, col2 = st.columns([1.1, 1.6])

    with col1:
        st.markdown("### Resumen")
        df_factor_tt = obtener_factor_instalacion_resumen("dbo.CLARO_TELETALK_FIJA", filtro_inst_tt)

        if df_factor_tt.empty:
            st.warning("No se encontraron datos para la vista de Factor Instalación.")
        else:
            total_row = pd.DataFrame([{
                "Año": "Total",
                "Mes": "",
                "Ventas": df_factor_tt["Ventas"].sum(),
                "PORTABILIDAD SI": df_factor_tt["PORTABILIDAD SI"].sum(),
                "PORTABILIDAD NO": df_factor_tt["PORTABILIDAD NO"].sum(),
                "FTTH": df_factor_tt["FTTH"].sum(),
                "HFC": df_factor_tt["HFC"].sum(),
                "S/.": df_factor_tt["S/."].sum()
            }])

            df_display_tt = pd.concat([df_factor_tt, total_row], ignore_index=True)
            df_display_tt["S/."] = df_display_tt["S/."].map(formatear_moneda)

            table_style_tt = (
                df_display_tt.style
                .set_table_styles([
                    {"selector": "th", "props": [("background-color", "white"), ("color", "#70008f"), ("font-size", "13px"), ("text-align", "center"), ("border-bottom", "2px solid #ddd")]},
                    {"selector": "td", "props": [("padding", "10px 8px"), ("font-size", "13px"), ("border-bottom", "1px solid #eee"), ("background-color", "white")]},
                ])
                .set_properties(subset=["Año", "Mes"], **{"text-align": "left"})
                .set_properties(subset=["Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."], **{"text-align": "center"})
            )

            st.table(table_style_tt)

    with col2:
        st.markdown("### Detalle desplegable")
        df_detalle_tt = obtener_factor_instalacion_detallado("dbo.CLARO_TELETALK_FIJA", filtro_inst_tt)
        mostrar_expanders_factor_instalacion(df_detalle_tt, color="tt")


# ---------------------------------------------------------
# TELETALK FACTOR F. VENTA
# ---------------------------------------------------------
elif opcion == "Teletalk Factor F. Venta":
    set_bg(img_tt)

    st.markdown('<div class="section-title-tt">Teletalk Factor F. Venta</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-subtitle-tt">AVANCE DE FACTOR ANUAL POR FECHA DE VENTA</div>', unsafe_allow_html=True)
    st.write("---")

    meses_gene_tt = obtener_meses("FECHA GENERACION")
    filtro_gene_tt = st.selectbox("Fecha de Venta", meses_gene_tt, key="filtro_gene_factor_venta_tt")

    col1, col2 = st.columns([1.1, 1.6])

    with col1:
        st.markdown("### Resumen")
        df_factor_venta_tt = obtener_factor_fecha_venta_resumen("dbo.CLARO_TELETALK_FIJA", filtro_gene_tt)

        if df_factor_venta_tt.empty:
            st.warning("No se encontraron datos para la vista de Factor Fecha de Venta.")
        else:
            total_row = pd.DataFrame([{
                "Año": "Total",
                "Mes": "",
                "Ventas": df_factor_venta_tt["Ventas"].sum(),
                "PORTABILIDAD SI": df_factor_venta_tt["PORTABILIDAD SI"].sum(),
                "PORTABILIDAD NO": df_factor_venta_tt["PORTABILIDAD NO"].sum(),
                "FTTH": df_factor_venta_tt["FTTH"].sum(),
                "HFC": df_factor_venta_tt["HFC"].sum(),
                "S/.": df_factor_venta_tt["S/."].sum()
            }])

            df_display_venta_tt = pd.concat([df_factor_venta_tt, total_row], ignore_index=True)
            df_display_venta_tt["S/."] = df_display_venta_tt["S/."].map(formatear_moneda)

            table_style_venta_tt = (
                df_display_venta_tt.style
                .set_table_styles([
                    {"selector": "th", "props": [("background-color", "white"), ("color", "#70008f"), ("font-size", "13px"), ("text-align", "center"), ("border-bottom", "2px solid #ddd")]},
                    {"selector": "td", "props": [("padding", "10px 8px"), ("font-size", "13px"), ("border-bottom", "1px solid #eee"), ("background-color", "white")]},
                ])
                .set_properties(subset=["Año", "Mes"], **{"text-align": "left"})
                .set_properties(subset=["Ventas", "PORTABILIDAD SI", "PORTABILIDAD NO", "FTTH", "HFC", "S/."], **{"text-align": "center"})
            )

            st.table(table_style_venta_tt)

    with col2:
        st.markdown("### Detalle desplegable")
        df_detalle_venta_tt = obtener_factor_fecha_venta_detallado("dbo.CLARO_TELETALK_FIJA", filtro_gene_tt)
        mostrar_expanders_factor_instalacion(df_detalle_venta_tt, color="tt")


# ---------------------------------------------------------
# TELETALK IAE ASESOR
# ---------------------------------------------------------
elif opcion == "Teletalk IAE ASESOR":
    set_bg(img_tt)
    st.markdown('<div class="section-title-tt">Teletalk IAE ASESOR</div>', unsafe_allow_html=True)
    st.write("---")

    meses_inst = obtener_meses("FECHA INSTALACION")
    filt_inst_tt = st.selectbox("Fecha de Instalación", meses_inst, key="filtro_inst_teletalk_iae")

    df_liquidado_tt = obtener_reporte_liquidado(
        ventas_tabla="dbo.CLARO_TELETALK_FIJA",
        maestro_tabla="[DATA DEVELZ].dbo.FIJA_TELETALK",
        fecha_instalacion=filt_inst_tt
    )

    if df_liquidado_tt.empty:
        st.warning("No se encontraron datos para el reporte liquidado.")
    else:
        asesores_tt = ["Todos"] + sorted(df_liquidado_tt["ASESOR"].fillna("Sin Asesor").unique().tolist())
        filtro_asesor_tt = st.selectbox("Selecciona Asesor", asesores_tt, key="filtro_asesor_teletalk_iae")

        if filtro_asesor_tt != "Todos":
            df_filtrado_tt = df_liquidado_tt[df_liquidado_tt["ASESOR"] == filtro_asesor_tt].copy()
        else:
            df_filtrado_tt = df_liquidado_tt.copy()

        st.markdown("### Ranking de Asesores")
        ranking_con_total_tt = construir_ranking_asesores(df_filtrado_tt)
        mostrar_tabla_ranking(ranking_con_total_tt)