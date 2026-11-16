from pathlib import Path

import pandas as pd

from limpieza import limpiar_datos

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
ARCHIVO_ORIGINAL = RAIZ_PROYECTO / "data" / "raw" / "online_shoppers_intention.csv"
ARCHIVO_PROCESADO = (
    RAIZ_PROYECTO / "data" / "processed" / "online_shoppers_intention_clean.csv"
)

def ejecutar_etl():
    datos_originales = pd.read_csv(ARCHIVO_ORIGINAL)
    datos_limpios, resumen = limpiar_datos(datos_originales)

    ARCHIVO_PROCESADO.parent.mkdir(parents=True, exist_ok=True)
    datos_limpios.to_csv(ARCHIVO_PROCESADO, index=False)

    print("ETL terminado")
    print(f"Archivo generado: {ARCHIVO_PROCESADO}")
    print(f"Resumen: {resumen}")


if __name__ == "__main__":
    ejecutar_etl()