import pandas as pd 

def revisar_valores_faltantes(datos):
    """Muestra la cantidad de valores daltantes por columna"""
    faltantes = datos.isnull().sum()
    porcentaje = (faltantes / len(datos)) * 100

    resultado = pd.DataFrame({
        "Valores Faltantes": faltantes,
        "Porcentaje": porcentaje
    })

    return resultado

def revisar_duplicados(datos):
    """Cuenta los registros duplicados"""
    return datos.duplicated().sum()

def revisar_valores_negativos(datos):
    columnas_numericas = datos.select_dtypes(include = "numer").columns

    negativos = {}

    for columna in columnas_numericas:
        cantidad = (datos[columna] < 0).sum()

        if cantidad > 0:
            negativos[columna] = cantidad

        return negativos

def revisar_categorias(datos):
    """Muestra los valores unicos de las columnas categoricas"""
    columnas_categoricas = datos.select_dtypes(
        include = ["object","bool"]
    ).columns

    categorias = {}

    for columna in columnas_categoricas:
        categorias[columna] = datos[columna].unique().tolist()

    return categorias