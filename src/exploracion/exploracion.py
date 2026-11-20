"""Funciones básicas para explorar el conjunto de datos."""

def mostrar_primeros_registros(datos, cantidad=5):
    """Muestra los primeros registros del conjunto."""
    return datos.head(cantidad)


def mostrar_dimensiones(datos):
    """Devuelve la cantidad de filas y columnas."""
    return datos.shape


def mostrar_columnas(datos):
    """Devuelve los nombres de las columnas."""
    return datos.columns.tolist()


def mostrar_tipos_datos(datos):
    """Muestra los tipos de datos de cada columna."""
    return datos.dtypes


def mostrar_resumen(datos):
    """Muestra un resumen general de las variables."""
    return datos.describe(include="all")
