"""
================================================================================
Script: reset_datamart.py
Proyecto: Análisis del comportamiento de compradores en comercio electrónico
Motor: Microsoft SQL Server / SQL Server LocalDB
Propósito: Eliminar y reconstruir las tablas del Data Mart (esquema estrella)
         usando Python y pyodbc, sin borrar la base de datos completa.
================================================================================

QUÉ HACE ESTE SCRIPT
--------------------
1. Conecta a la base de datos ECBD_Compradores.
2. Elimina las 8 tablas del Data Mart en el orden correcto para respetar
   las claves foráneas (primero la tabla de hechos, luego las dimensiones,
   por último la tabla de staging).
3. Vuelve a crear las 8 tablas con exactamente la misma definición que
   el script original 01_crear_base_y_datamart.sql.
4. Es idempotente: se puede ejecutar cuantas veces se quiera sin errores
   por "tabla inexistente" ni por "tabla ya existe".

POR QUÉ ES NECESARIO
--------------------
- Durante el desarrollo del ETL en SSIS es frecuente necesitar vaciar y
  recrear las tablas para probar cargas limpias.
- Permite restablecer el Data Mart a un estado conocido sin tener que
  borrar y recrear la base de datos completa.
- Sirve como "reset" antes de cada ejecución de prueba del paquete SSIS.
- Al estar en Python, se puede integrar fácilmente en pipelines de CI/CD
  o llamar desde notebooks.

CÓMO EJECUTARLO
---------------
Desde la raíz del proyecto:
    python -m src.etl.reset_datamart

O directamente:
    python src/etl/reset_datamart.py

REQUISITOS
----------
- pyodbc instalado (pip install pyodbc)
- SQL Server LocalDB o servidor accesible
- Base de datos ECBD_Compradores ya creada (la crea 01_crear_base_y_datamart.sql)
================================================================================
"""

import pyodbc
import sys
from pathlib import Path


def get_connection_string():
    """
    Construye la cadena de conexión para SQL Server LocalDB.
    Ajusta SERVER si usas otra instancia.
    """
    return (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;"
        "DATABASE=ECBD_Compradores;"
        "Trusted_Connection=yes;"
    )


def execute_sql(cursor, sql, description=""):
    """
    Ejecuta una sentencia SQL y maneja errores de forma clara.
    """
    try:
        if description:
            print(f"  -> {description}")
        cursor.execute(sql)
        return True
    except pyodbc.Error as e:
        print(f"  [ERROR] Error: {e}")
        return False


def drop_tables(cursor):
    """
    Elimina las tablas en orden inverso a las dependencias FK.
    FactSesion → 6 dimensiones → StgSesiones
    """
    print("\n--- ELIMINANDO TABLAS EXISTENTES ---")

    tables_to_drop = [
        ("dbo.FactSesion", "Tabla de hechos (tiene 6 FK hacia dimensiones)"),
        ("dbo.DimMes", "Dimensión Mes"),
        ("dbo.DimTipoVisitante", "Dimensión Tipo de Visitante"),
        ("dbo.DimSistemaOperativo", "Dimensión Sistema Operativo"),
        ("dbo.DimNavegador", "Dimensión Navegador"),
        ("dbo.DimRegion", "Dimensión Región"),
        ("dbo.DimTipoTrafico", "Dimensión Tipo de Tráfico"),
        ("dbo.StgSesiones", "Tabla de staging (sin FK)"),
    ]

    for table, desc in tables_to_drop:
        sql = f"IF OBJECT_ID(N'{table}', N'U') IS NOT NULL DROP TABLE {table};"
        if execute_sql(cursor, sql, f"Eliminando {desc} ({table})"):
            print(f"    [OK] {table} eliminada")


def create_staging(cursor):
    """
    Crea la tabla de staging con las 18 columnas del CSV procesado.
    Tipos adaptados para recibir el CSV tal cual (texto para booleanos y tasas).
    """
    print("\n--- CREANDO TABLA DE STAGING ---")

    sql = """
    CREATE TABLE dbo.StgSesiones (
        Administrative INT NOT NULL,
        Administrative_Duration DECIMAL(14, 6) NOT NULL,
        Informational INT NOT NULL,
        Informational_Duration DECIMAL(14, 6) NOT NULL,
        ProductRelated INT NOT NULL,
        ProductRelated_Duration DECIMAL(14, 6) NOT NULL,
        BounceRates NVARCHAR(32) NOT NULL,
        ExitRates DECIMAL(12, 8) NOT NULL,
        PageValues DECIMAL(14, 6) NOT NULL,
        SpecialDay DECIMAL(8, 6) NOT NULL,
        [Month] NVARCHAR(3) NOT NULL,
        OperatingSystems INT NOT NULL,
        Browser INT NOT NULL,
        Region INT NOT NULL,
        TrafficType INT NOT NULL,
        VisitorType NVARCHAR(30) NOT NULL,
        Weekend NVARCHAR(5) NOT NULL,
        Revenue NVARCHAR(5) NOT NULL
    );
    """
    execute_sql(cursor, sql, "Creando dbo.StgSesiones")
    print("    [OK] dbo.StgSesiones creada")

    # Asegurar tipos correctos (el CSV trae texto para algunos campos)
    fixes = [
        ("BounceRates", "NVARCHAR(32)"),
        ("Weekend", "NVARCHAR(5)"),
        ("Revenue", "NVARCHAR(5)"),
    ]
    for col, dtype in fixes:
        sql = f"""
        IF EXISTS (
            SELECT 1 FROM sys.columns
            WHERE object_id = OBJECT_ID(N'dbo.StgSesiones')
              AND name = N'{col}'
              AND system_type_id <> TYPE_ID(N'{dtype}')
        )
            ALTER TABLE dbo.StgSesiones ALTER COLUMN {col} {dtype} NOT NULL;
        """
        execute_sql(cursor, sql, f"  Ajustando tipo de {col} a {dtype}")


def create_dimensions(cursor):
    """
    Crea las 6 dimensiones del esquema estrella.
    Cada una tiene:
    - PK sustituta: *Key INT IDENTITY(1,1) PRIMARY KEY
    - UNIQUE en atributo natural (el valor que viene del CSV)
    """
    print("\n--- CREANDO DIMENSIONES ---")

    dimensions = [
        ("DimMes", "MesKey", "Mes", "NVARCHAR(3)"),
        ("DimTipoVisitante", "TipoVisitanteKey", "TipoVisitante", "NVARCHAR(30)"),
        ("DimSistemaOperativo", "SistemaOperativoKey", "CodigoSistemaOperativo", "INT"),
        ("DimNavegador", "NavegadorKey", "CodigoNavegador", "INT"),
        ("DimRegion", "RegionKey", "CodigoRegion", "INT"),
        ("DimTipoTrafico", "TipoTraficoKey", "CodigoTipoTrafico", "INT"),
    ]

    for table, pk, natural_col, natural_type in dimensions:
        sql = f"""
        CREATE TABLE dbo.{table} (
            {pk} INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_{table} PRIMARY KEY,
            {natural_col} {natural_type} NOT NULL CONSTRAINT UQ_{table} UNIQUE
        );
        """
        execute_sql(cursor, sql, f"Creando dbo.{table}")
        print(f"    [OK] dbo.{table} creada (PK={pk}, UNIQUE={natural_col})")


def create_fact_table(cursor):
    """
    Crea la tabla de hechos FactSesion con:
    - PK sustituta: SesonKey BIGINT IDENTITY(1,1) PRIMARY KEY
    - 6 FK hacia las dimensiones
    - Medidas e indicadores (todos NOT NULL)
    """
    print("\n--- CREANDO TABLA DE HECHOS ---")

    sql = """
    CREATE TABLE dbo.FactSesion (
        SesionKey BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_FactSesion PRIMARY KEY,
        -- Llaves foráneas (6 dimensiones)
        MesKey INT NOT NULL,
        TipoVisitanteKey INT NOT NULL,
        SistemaOperativoKey INT NOT NULL,
        NavegadorKey INT NOT NULL,
        RegionKey INT NOT NULL,
        TipoTraficoKey INT NOT NULL,
        -- Medidas de navegación
        Administrative INT NOT NULL,
        Administrative_Duration DECIMAL(14, 6) NOT NULL,
        Informational INT NOT NULL,
        Informational_Duration DECIMAL(14, 6) NOT NULL,
        ProductRelated INT NOT NULL,
        ProductRelated_Duration DECIMAL(14, 6) NOT NULL,
        -- Tasas y valor
        BounceRates DECIMAL(12, 8) NOT NULL,
        ExitRates DECIMAL(12, 8) NOT NULL,
        PageValues DECIMAL(14, 6) NOT NULL,
        -- Indicadores
        SpecialDay DECIMAL(8, 6) NOT NULL,
        Weekend BIT NOT NULL,
        Revenue BIT NOT NULL,
        -- Restricciones de integridad referencial
        CONSTRAINT FK_FactSesion_DimMes FOREIGN KEY (MesKey) REFERENCES dbo.DimMes(MesKey),
        CONSTRAINT FK_FactSesion_DimTipoVisitante FOREIGN KEY (TipoVisitanteKey) REFERENCES dbo.DimTipoVisitante(TipoVisitanteKey),
        CONSTRAINT FK_FactSesion_DimSistemaOperativo FOREIGN KEY (SistemaOperativoKey) REFERENCES dbo.DimSistemaOperativo(SistemaOperativoKey),
        CONSTRAINT FK_FactSesion_DimNavegador FOREIGN KEY (NavegadorKey) REFERENCES dbo.DimNavegador(NavegadorKey),
        CONSTRAINT FK_FactSesion_DimRegion FOREIGN KEY (RegionKey) REFERENCES dbo.DimRegion(RegionKey),
        CONSTRAINT FK_FactSesion_DimTipoTrafico FOREIGN KEY (TipoTraficoKey) REFERENCES dbo.DimTipoTrafico(TipoTraficoKey)
    );
    """
    execute_sql(cursor, sql, "Creando dbo.FactSesion")
    print("    [OK] dbo.FactSesion creada (PK=SesionKey, 6 FK, medidas e indicadores)")


def verify_creation(cursor):
    """
    Valida que las 8 tablas existan y tengan la estructura esperada.
    """
    print("\n--- VALIDACIÓN FINAL ---")

    # Listar tablas
    cursor.execute("""
        SELECT name AS Tabla
        FROM sys.tables
        WHERE schema_id = SCHEMA_ID(N'dbo')
          AND name IN ('StgSesiones','DimMes','DimTipoVisitante','DimSistemaOperativo',
                       'DimNavegador','DimRegion','DimTipoTrafico','FactSesion')
        ORDER BY name;
    """)
    tables = [row.Tabla for row in cursor.fetchall()]
    print(f"Tablas creadas ({len(tables)}): {', '.join(tables)}")

    # Verificar FK en FactSesion
    cursor.execute("""
        SELECT fk.name AS FK_Name, tr.name AS Referenced_Table
        FROM sys.foreign_keys fk
        INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
        WHERE OBJECT_NAME(fk.parent_object_id) = 'FactSesion'
        ORDER BY fk.name;
    """)
    fks = cursor.fetchall()
    print(f"Foreign Keys en FactSesion ({len(fks)}):")
    for fk in fks:
        print(f"  - {fk.FK_Name} -> {fk.Referenced_Table}")

    # Verificar PK y UNIQUE en dimensiones
    cursor.execute("""
        SELECT t.name AS Table_Name, i.name AS Index_Name, i.is_unique
        FROM sys.indexes i
        INNER JOIN sys.tables t ON i.object_id = t.object_id
        WHERE t.name IN ('DimMes','DimTipoVisitante','DimSistemaOperativo',
                         'DimNavegador','DimRegion','DimTipoTrafico','FactSesion')
          AND (i.is_primary_key = 1 OR i.is_unique = 1)
        ORDER BY t.name, i.name;
    """)
    indexes = cursor.fetchall()
    print("PK y UNIQUE constraints:")
    for idx in indexes:
        tipo = "PK" if idx.is_unique and "PK_" in idx.Index_Name else "UNIQUE"
        print(f"  - {idx.Table_Name}.{idx.Index_Name} ({tipo})")

    expected = 8
    if len(tables) == expected and len(fks) == 6:
        print(f"\n[OK] VALIDACIÓN EXITOSA: Data Mart reiniciado correctamente ({expected} tablas, 6 FK)")
        return True
    else:
        print(f"\n[ERROR] VALIDACIÓN FALLIDA: esperado {expected} tablas y 6 FK")
        return False


def main():
    """
    Función principal: conecta, borra, crea y valida.
    """
    print("=" * 70)
    print("REINICIO DEL DATA MART - ECBD_Compradores")
    print("=" * 70)

    conn_str = get_connection_string()

    try:
        print(f"\nConectando a: (localdb)\\MSSQLLocalDB / ECBD_Compradores")
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        print("  [OK] Conexión establecida")

    except pyodbc.Error as e:
        print(f"\n[ERROR] ERROR DE CONEXIÓN: {e}")
        print("  Verifica que:")
        print("  - SQL Server LocalDB esté corriendo (sqllocaldb start MSSQLLocalDB)")
        print("  - La base ECBD_Compradores exista (ejecuta 01_crear_base_y_datamart.sql primero)")
        print("  - pyodbc esté instalado (pip install pyodbc)")
        sys.exit(1)

    try:
        # 1. Eliminar tablas existentes
        drop_tables(cursor)

        # 2. Crear staging
        create_staging(cursor)

        # 3. Crear dimensiones
        create_dimensions(cursor)

        # 4. Crear tabla de hechos
        create_fact_table(cursor)

        # 5. Validar
        success = verify_creation(cursor)

        print("\n" + "=" * 70)
        if success:
            print("PROCESO COMPLETADO CON ÉXITO")
        else:
            print("PROCESO COMPLETADO CON ERRORES")
        print("=" * 70)

    except pyodbc.Error as e:
        print(f"\n[ERROR] ERROR DURANTE LA EJECUCIÓN: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()