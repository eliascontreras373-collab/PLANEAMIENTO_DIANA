import pyodbc
import pandas as pd

datos_conexion = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=127.0.0.1,1433;"
    "DATABASE=DATA CLARO;" 
    "Trusted_Connection=yes;"
    "Encrypt=no;"
)

try:
    conn = pyodbc.connect(datos_conexion)
    print("CONEXION EXITOSA")

    # 1. Cargar tablas
    print("Leyendo tablas para cruce por SOT...")
    df_claro = pd.read_sql("SELECT * FROM dbo.CLARO_DC_FIJA", conn)
    df_develz = pd.read_sql("SELECT * FROM [DATA DEVELZ].dbo.FIJA_DC", conn)

    # 2. Limpieza de las columnas de SOT (Convertir a texto y quitar espacios)
    # Esto asegura que "12345" sea igual a " 12345"
    df_claro['SOT'] = df_claro['SOT'].astype(str).str.strip()
    df_develz['Back Office - Sot'] = df_develz['Back Office - Sot'].astype(str).str.strip()

    # 3. EL CRUCE POR SOT
    print("Cruzando informacion por SOT...")
    
    df_final = pd.merge(
        df_claro, 
        df_develz, 
        left_on='SOT', 
        right_on='Back Office - Sot', 
        how='inner'
    )

    # 4. Finalizacion
    if len(df_final) > 0:
        print(f"PROCESO TERMINADO CON EXITO")
        print(f"Se encontraron {len(df_final)} coincidencias por SOT.")
        
        # Guardar resultado
        df_final.to_excel("Cruce_SOT_Final.xlsx", index=False)
        print("Archivo 'Cruce_SOT_Final.xlsx' guardado con exito.")
    else:
        print("AVISO: No se encontraron coincidencias. Revisa si los SOT en ambas bases tienen el mismo formato.")

except Exception as e:
    print("HUBO UN ERROR:")
    print(str(e))

if 'conn' in locals():
    conn.close()

input("\nPresiona Enter para finalizar...")
