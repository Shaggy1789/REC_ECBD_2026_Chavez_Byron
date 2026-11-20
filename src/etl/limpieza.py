import pandas as pd 

def revisar_valores_faltantes(datos):
    faltantes = datos.isna().sum()
    return pd.DataFrame({
        "Valores faltantes": faltantes,
        "Porcentaje": (faltantes/len(datos) * 100).round(2),
    })

def revisar_duplicados(datos):
    """Devuelve la cantidad de filas duplicadas exactas."""
    return int(datos.duplicated().sum())

def revisar_valores_negativos(datos):
    """Devuelve el conteo de negativos por columna numerica"""
    columnas_numericas = datos.select_dtypes(include="number").columns
    negativos = (datos[columnas_numericas] < 0).sum()
    return negativos[negativos > 0].to_dict()


def revisar_categorias(datos):
    columnas_categoricas = datos.select_dtypes(
        include=["object","bool","string"]
    ).columns

    return{
        columna: datos[columna].dropna().unique().tolist()
        for columna in columnas_categoricas
    }

def limpiar_datos(datos):
    """Devuelve una copia limpia y un resumen de los cambios."""
    datos_limpios = datos.copy()
    filas_originales = len(datos_limpios)
    duplicados = revisar_duplicados(datos_limpios)

    datos_limpios = datos_limpios.drop_duplicates().copy()

    if "Month" in datos_limpios.columns:
        datos_limpios["Month"] = datos_limpios["Month"].replace({"June": "Jun"})

    resumen = {
        "filas_originales": filas_originales,
        "duplicados_detectados": duplicados,
        "filas_finales": len(datos_limpios),
        "filas_eliminadas": filas_originales - len(datos_limpios),
        "valores_faltantes_finales": int(datos_limpios.isna().sum().sum()),
    }

    return datos_limpios, resumen