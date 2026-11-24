"""
Módulo ETL: Extracción, Transformación y Carga de datos.

Componentes:
- limpieza: Funciones de limpieza y validación de datos
- cargar_sql: Carga del dataset procesado a SQL Server
- etl: Orquestación completa del pipeline ETL
- reset_datamart: Reinicio del Data Mart (esquema estrella)
"""

# Importaciones diferidas para evitar advertencias de importación circular
# al ejecutar `python -m src.etl.etl`
from .limpieza import limpiar_datos
from .cargar_sql import cargar_a_sql_server

__all__ = [
    "limpiar_datos",
    "cargar_a_sql_server",
]