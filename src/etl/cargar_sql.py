"""
Módulo para cargar el dataset procesado a SQL Server.

Utiliza pyodbc y pandas para insertar los datos mediante consultas parametrizadas,
evitando BULK INSERT y cargas mediante SQL puro.
"""

import pyodbc
import pandas as pd
from pathlib import Path


# Configuración de conexión a SQL Server LocalDB
# Ajusta SERVER si tu instancia tiene otro nombre
CONEXION_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=ECBD_Compradores;"
    "Trusted_Connection=yes;"
)

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
ARCHIVO_PROCESADO = (
    RAIZ_PROYECTO / "data" / "processed" / "clean" / "online_shoppers_intention_clean.csv"
)

# Columnas esperadas en el CSV procesado (orden exacto)
COLUMNAS_ESPERADAS = [
    "Administrative",
    "Administrative_Duration",
    "Informational",
    "Informational_Duration",
    "ProductRelated",
    "ProductRelated_Duration",
    "BounceRates",
    "ExitRates",
    "PageValues",
    "SpecialDay",
    "Month",
    "OperatingSystems",
    "Browser",
    "Region",
    "TrafficType",
    "VisitorType",
    "Weekend",
    "Revenue",
]


def obtener_conexion():
    """Crea y devuelve una conexión a la base de datos."""
    return pyodbc.connect(CONEXION_STR, autocommit=False, timeout=30)


def truncar_tabla(conexion, nombre_tabla):
    """Trunca una tabla para recargarla desde cero."""
    cursor = conexion.cursor()
    cursor.execute(f"TRUNCATE TABLE dbo.{nombre_tabla}")
    cursor.close()


def validar_columnas_csv(datos):
    """Verifica que el CSV tenga exactamente las 18 columnas esperadas en orden."""
    columnas_actuales = list(datos.columns)
    if columnas_actuales != COLUMNAS_ESPERADAS:
        raise ValueError(
            f"Columnas del CSV no coinciden.\n"
            f"  Esperadas: {COLUMNAS_ESPERADAS}\n"
            f"  Encontradas: {columnas_actuales}"
        )


def validar_bool_str(valor, nombre_campo):
    """
    Valida que un valor string sea 'True' o 'False' (case-insensitive).
    Devuelve 1 para True, 0 para False.
    Lanza ValueError si el valor no es válido.
    """
    v = str(valor).strip().lower()
    if v in ("true", "1", "yes", "t", "y"):
        return 1
    elif v in ("false", "0", "no", "f", "n"):
        return 0
    else:
        raise ValueError(
            f"Valor inválido en {nombre_campo}: '{valor}'. "
            f"Se esperaba 'True' o 'False'."
        )


def insertar_dimensiones(conexion, datos):
    """
    Inserta los valores distintos en cada tabla de dimensión.
    Usa MERGE (upsert) para evitar duplicados si se ejecuta varias veces.
    Las columnas naturales tienen restricción UNIQUE en el DDL.
    """
    cursor = conexion.cursor()

    # DimMes - columna natural: Mes (NVARCHAR(3))
    for mes in datos["Month"].unique():
        cursor.execute(
            """
            MERGE dbo.DimMes AS target
            USING (SELECT ? AS Mes) AS source
            ON target.Mes = source.Mes
            WHEN NOT MATCHED THEN INSERT (Mes) VALUES (source.Mes);
            """,
            mes,
        )

    # DimTipoVisitante - columna natural: TipoVisitante (NVARCHAR(30))
    for vt in datos["VisitorType"].unique():
        cursor.execute(
            """
            MERGE dbo.DimTipoVisitante AS target
            USING (SELECT ? AS TipoVisitante) AS source
            ON target.TipoVisitante = source.TipoVisitante
            WHEN NOT MATCHED THEN INSERT (TipoVisitante) VALUES (source.TipoVisitante);
            """,
            vt,
        )

    # DimSistemaOperativo - columna natural: CodigoSistemaOperativo (INT)
    for so in datos["OperatingSystems"].unique():
        cursor.execute(
            """
            MERGE dbo.DimSistemaOperativo AS target
            USING (SELECT ? AS CodigoSistemaOperativo) AS source
            ON target.CodigoSistemaOperativo = source.CodigoSistemaOperativo
            WHEN NOT MATCHED THEN INSERT (CodigoSistemaOperativo) VALUES (source.CodigoSistemaOperativo);
            """,
            int(so),
        )

    # DimNavegador - columna natural: CodigoNavegador (INT)
    for nav in datos["Browser"].unique():
        cursor.execute(
            """
            MERGE dbo.DimNavegador AS target
            USING (SELECT ? AS CodigoNavegador) AS source
            ON target.CodigoNavegador = source.CodigoNavegador
            WHEN NOT MATCHED THEN INSERT (CodigoNavegador) VALUES (source.CodigoNavegador);
            """,
            int(nav),
        )

    # DimRegion - columna natural: CodigoRegion (INT)
    for reg in datos["Region"].unique():
        cursor.execute(
            """
            MERGE dbo.DimRegion AS target
            USING (SELECT ? AS CodigoRegion) AS source
            ON target.CodigoRegion = source.CodigoRegion
            WHEN NOT MATCHED THEN INSERT (CodigoRegion) VALUES (source.CodigoRegion);
            """,
            int(reg),
        )

    # DimTipoTrafico - columna natural: CodigoTipoTrafico (INT)
    for tt in datos["TrafficType"].unique():
        cursor.execute(
            """
            MERGE dbo.DimTipoTrafico AS target
            USING (SELECT ? AS CodigoTipoTrafico) AS source
            ON target.CodigoTipoTrafico = source.CodigoTipoTrafico
            WHEN NOT MATCHED THEN INSERT (CodigoTipoTrafico) VALUES (source.CodigoTipoTrafico);
            """,
            int(tt),
        )

    cursor.close()


def obtener_mapas_dimensiones(conexion):
    """
    Recupera los mapas de valor natural -> llave sustituta para cada dimensión.
    Devuelve un diccionario con 6 mapas.
    """
    cursor = conexion.cursor()

    mapas = {}

    cursor.execute("SELECT MesKey, Mes FROM dbo.DimMes")
    mapas["mes"] = {row.Mes: row.MesKey for row in cursor.fetchall()}

    cursor.execute("SELECT TipoVisitanteKey, TipoVisitante FROM dbo.DimTipoVisitante")
    mapas["visitante"] = {row.TipoVisitante: row.TipoVisitanteKey for row in cursor.fetchall()}

    cursor.execute("SELECT SistemaOperativoKey, CodigoSistemaOperativo FROM dbo.DimSistemaOperativo")
    mapas["so"] = {row.CodigoSistemaOperativo: row.SistemaOperativoKey for row in cursor.fetchall()}

    cursor.execute("SELECT NavegadorKey, CodigoNavegador FROM dbo.DimNavegador")
    mapas["navegador"] = {row.CodigoNavegador: row.NavegadorKey for row in cursor.fetchall()}

    cursor.execute("SELECT RegionKey, CodigoRegion FROM dbo.DimRegion")
    mapas["region"] = {row.CodigoRegion: row.RegionKey for row in cursor.fetchall()}

    cursor.execute("SELECT TipoTraficoKey, CodigoTipoTrafico FROM dbo.DimTipoTrafico")
    mapas["trafico"] = {row.CodigoTipoTrafico: row.TipoTraficoKey for row in cursor.fetchall()}

    cursor.close()
    return mapas


def preparar_fila_fact(row, mapas):
    """
    Convierte una fila del DataFrame en una tupla lista para insertar en FactSesion.
    Valida Weekend y Revenue estrictamente.
    """
    weekend_bit = validar_bool_str(row["Weekend"], "Weekend")
    revenue_bit = validar_bool_str(row["Revenue"], "Revenue")

    # BounceRates: en staging es NVARCHAR, en FactSesion es DECIMAL(12,8)
    bounce = float(row["BounceRates"])

    return (
        mapas["mes"][row["Month"]],
        mapas["visitante"][row["VisitorType"]],
        mapas["so"][int(row["OperatingSystems"])],
        mapas["navegador"][int(row["Browser"])],
        mapas["region"][int(row["Region"])],
        mapas["trafico"][int(row["TrafficType"])],
        int(row["Administrative"]),
        float(row["Administrative_Duration"]),
        int(row["Informational"]),
        float(row["Informational_Duration"]),
        int(row["ProductRelated"]),
        float(row["ProductRelated_Duration"]),
        bounce,
        float(row["ExitRates"]),
        float(row["PageValues"]),
        float(row["SpecialDay"]),
        weekend_bit,
        revenue_bit,
    )


def insertar_fact_sesion(conexion, datos, mapas, tamano_lote=1000):
    """
    Inserta todas las filas en FactSesion usando lotes de 1000 con executemany.
    No hace commit aquí; la transacción se confirma al final de toda la carga.
    """
    cursor = conexion.cursor()

    sql = """
    INSERT INTO dbo.FactSesion (
        MesKey, TipoVisitanteKey, SistemaOperativoKey, NavegadorKey, RegionKey, TipoTraficoKey,
        Administrative, Administrative_Duration, Informational, Informational_Duration,
        ProductRelated, ProductRelated_Duration, BounceRates, ExitRates, PageValues,
        SpecialDay, Weekend, Revenue
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    lote = []
    total = 0

    for _, row in datos.iterrows():
        lote.append(preparar_fila_fact(row, mapas))
        if len(lote) >= tamano_lote:
            cursor.executemany(sql, lote)
            total += len(lote)
            lote = []

    if lote:
        cursor.executemany(sql, lote)
        total += len(lote)

    cursor.close()
    return total


def validar_carga(conexion):
    """
    Verifica que la carga sea correcta:
    - Conteo de filas en staging y hechos (deben coincidir y ser 12,205)
    - Conteo en cada dimensión
    - Integridad referencial: 6 FKs sin registros huérfanos
    Devuelve diccionario con conteos. Lanza ValueError si algo falla.
    """
    cursor = conexion.cursor()

    # Conteos básicos
    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.StgSesiones")
    staging = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.FactSesion")
    hechos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.DimMes")
    dim_mes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.DimTipoVisitante")
    dim_vt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.DimSistemaOperativo")
    dim_so = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.DimNavegador")
    dim_nav = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.DimRegion")
    dim_reg = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT_BIG(*) FROM dbo.DimTipoTrafico")
    dim_tt = cursor.fetchone()[0]

    # Validar integridad referencial (FKs)
    # Cada consulta debe devolver 0 (ningún registro en FactSesion sin dimensión correspondiente)
    fk_checks = [
        ("FK_FactSesion_DimMes", "MesKey", "DimMes", "MesKey"),
        ("FK_FactSesion_DimTipoVisitante", "TipoVisitanteKey", "DimTipoVisitante", "TipoVisitanteKey"),
        ("FK_FactSesion_DimSistemaOperativo", "SistemaOperativoKey", "DimSistemaOperativo", "SistemaOperativoKey"),
        ("FK_FactSesion_DimNavegador", "NavegadorKey", "DimNavegador", "NavegadorKey"),
        ("FK_FactSesion_DimRegion", "RegionKey", "DimRegion", "RegionKey"),
        ("FK_FactSesion_DimTipoTrafico", "TipoTraficoKey", "DimTipoTrafico", "TipoTraficoKey"),
    ]

    for fk_name, fk_col, dim_table, dim_pk in fk_checks:
        cursor.execute(
            f"""
            SELECT COUNT_BIG(*)
            FROM dbo.FactSesion f
            LEFT JOIN dbo.{dim_table} d ON f.{fk_col} = d.{dim_pk}
            WHERE d.{dim_pk} IS NULL
            """
        )
        huérfanos = cursor.fetchone()[0]
        if huérfanos > 0:
            cursor.close()
            raise ValueError(
                f"Integridad referencial rota: {fk_name} tiene {huérfanos} registros huérfanos"
            )

    cursor.close()

    return {
        "staging": staging,
        "hechos": hechos,
        "dim_mes": dim_mes,
        "dim_visitante": dim_vt,
        "dim_so": dim_so,
        "dim_navegador": dim_nav,
        "dim_region": dim_reg,
        "dim_trafico": dim_tt,
    }


def cargar_a_sql_server():
    """
    Función principal: lee el CSV procesado y lo carga en SQL Server.
    Una sola transacción para toda la carga: commit al final, rollback si error.
    """
    print("Leyendo dataset procesado...")
    datos = pd.read_csv(ARCHIVO_PROCESADO)
    print(f"  Filas a cargar: {len(datos):,}")
    print(f"  Columnas: {list(datos.columns)}")

    # Validar columnas antes de continuar
    validar_columnas_csv(datos)

    print("Conectando a SQL Server...")
    conn = obtener_conexion()

    try:
        print("Truncando tablas...")
        truncar_tabla(conn, "StgSesiones")
        truncar_tabla(conn, "FactSesion")

        print("Insertando en staging (StgSesiones)...")
        cursor = conn.cursor()
        staging_sql = """
        INSERT INTO dbo.StgSesiones (
            Administrative, Administrative_Duration, Informational, Informational_Duration,
            ProductRelated, ProductRelated_Duration, BounceRates, ExitRates, PageValues,
            SpecialDay, [Month], OperatingSystems, Browser, Region, TrafficType,
            VisitorType, Weekend, Revenue
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        staging_data = []
        for _, row in datos.iterrows():
            staging_data.append((
                int(row["Administrative"]),
                float(row["Administrative_Duration"]),
                int(row["Informational"]),
                float(row["Informational_Duration"]),
                int(row["ProductRelated"]),
                float(row["ProductRelated_Duration"]),
                str(row["BounceRates"]),      # StgSesiones: NVARCHAR(32)
                float(row["ExitRates"]),      # StgSesiones: DECIMAL(12,8)
                float(row["PageValues"]),     # StgSesiones: DECIMAL(14,6)
                float(row["SpecialDay"]),     # StgSesiones: DECIMAL(8,6)
                str(row["Month"]),            # StgSesiones: NVARCHAR(3)
                int(row["OperatingSystems"]), # StgSesiones: INT
                int(row["Browser"]),          # StgSesiones: INT
                int(row["Region"]),           # StgSesiones: INT
                int(row["TrafficType"]),      # StgSesiones: INT
                str(row["VisitorType"]),      # StgSesiones: NVARCHAR(30)
                str(row["Weekend"]),          # StgSesiones: NVARCHAR(5) 'True'/'False'
                str(row["Revenue"]),          # StgSesiones: NVARCHAR(5) 'True'/'False'
            ))

        cursor.executemany(staging_sql, staging_data)
        cursor.close()
        print(f"  Filas en staging: {len(staging_data):,}")

        print("Poblando dimensiones (MERGE upsert)...")
        insertar_dimensiones(conn, datos)

        print("Obteniendo mapas de llaves dimensionales...")
        mapas = obtener_mapas_dimensiones(conn)

        print("Insertando en tabla de hechos (FactSesion)...")
        total_fact = insertar_fact_sesion(conn, datos, mapas)
        print(f"  Filas en FactSesion: {total_fact:,}")

        print("Validando carga...")
        counts = validar_carga(conn)
        print(f"  Staging: {counts['staging']:,} | FactSesion: {counts['hechos']:,}")
        print(f"  Dimensiones: Mes={counts['dim_mes']}, Visitante={counts['dim_visitante']}, "
              f"SO={counts['dim_so']}, Navegador={counts['dim_navegador']}, "
              f"Region={counts['dim_region']}, Trafico={counts['dim_trafico']}")

        if counts["staging"] != counts["hechos"]:
            raise ValueError(
                f"Conteo inconsistente: staging={counts['staging']}, hechos={counts['hechos']}"
            )
        if counts["staging"] != len(datos):
            raise ValueError(
                f"Se esperaban {len(datos):,} filas, se cargaron {counts['staging']:,}"
            )

        # Commit único al final de toda la carga
        conn.commit()
        print("Carga completada exitosamente. Commit realizado.")

    except Exception as e:
        conn.rollback()
        print(f"Error durante la carga: {e}")
        print("Rollback realizado.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    cargar_a_sql_server()