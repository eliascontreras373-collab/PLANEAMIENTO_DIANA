import pyodbc

# Usamos la IP local y el puerto 1433 que activaste
# Esta es la forma más directa y profesional de conectar
servidor = '127.0.0.1,1433' 
base_de_datos = 'DATA CLARO' 
driver = '{ODBC Driver 17 for SQL Server}'

try:
    print(f"--- Intentando entrar por la 'puerta' 1433 a: {base_de_datos} ---")
    
    conn = pyodbc.connect(
        f'DRIVER={driver};'
        f'SERVER={servidor};'
        f'DATABASE={base_de_datos};'
        'Trusted_Connection=yes;'
        'Encrypt=no;' 
    )
    
    print("¡CONEXIÓN EXITOSA!")
    print("Por fin, Diana. El puente está cruzado.")
    
    # Listamos tus tablas de DATA CLARO
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.tables")
    tablas = cursor.fetchall()
    
    print(f"\nTablas encontradas:")
    for t in tablas:
        print(f"  > {t[0]}")
    
    conn.close()

except Exception as e:
    print(f"Sigue habiendo un detalle con la red. Error:\n{e}")

input("\nPresiona Enter para cerrar...")