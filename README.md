# Análisis del comportamiento de compradores en comercio electrónico

## Objetivo

Analizar las sesiones del **Online Shoppers Purchasing Intention Dataset** para explorar el comportamiento de navegación y estudiar si una sesión termina en compra.

## Datos

- Dataset original: `data/raw/online_shoppers_intention.csv` (12,330 filas, 18 variables); se conserva sin cambios.
- Dataset procesado: `data/processed/online_shoppers_intention_clean.csv` (12,205 filas, 18 variables).
- El ETL elimina 125 duplicados exactos y normaliza `Month` (`June` a `Jun`). El CSV procesado revisado tiene cero duplicados y cero valores faltantes.

## Avance del proyecto

### Unidad II: preparación, ETL y Data Mart

- Exploración y diagnóstico en `notebooks/ChavezMolina_Byron_U2_AE1_Exploracion.ipynb` y el informe de `docs/`.
- Funciones de exploración, limpieza, visualización y ETL en `src/`.
- Diseño y ejecución documentados en `notebooks/02_diseno_base_datos_datamart.ipynb`.
- Scripts SQL en `sql/`: creación de la base, staging, seis dimensiones, tabla de hechos y carga completa.
- Diagrama dimensional: `docs/diagrama_data_mart.md`.
- Base local `ECBD_Compradores`: staging y `FactSesion` tienen 12,205 filas cada una.

### Unidad III: análisis supervisado

- Notebook ejecutable: `notebooks/03_modelos_supervisados.ipynb`.
- Regresión: `ProductRelated_Duration`; el bosque aleatorio obtuvo MAE de 510.76 s y R² de 0.715 en la partición de prueba.
- Clasificación: `Revenue`; el bosque aleatorio obtuvo F1 de 0.688, recall de compra de 0.730 y ROC AUC de 0.929. Regresión logística obtuvo recall de compra de 0.796.
- Modelos serializados y métricas: `modelos/`.

### Unidad IV: análisis no supervisado

- Notebook ejecutable: `notebooks/04_clustering_pca.ipynb`.
- K-Means comparó K=2 a K=6; K=2 obtuvo silhouette muestreado de 0.694.
- Dos componentes de PCA explican 81.8% de la varianza tras transformar y escalar las variables sesgadas.
- Asignaciones y coordenadas: `data/processed/`; modelos y métricas: `modelos/`; gráfica: `docs/pca_clusters.png`.

### Dashboard

- Aplicación interactiva: `dashboard/app.py`.
- Muestra indicadores de sesiones, compras y tasa de conversión; permite filtrar por mes, tipo de visitante, resultado de compra y fin de semana; incluye vistas mensuales, perfil de visitantes, duración y clusters, además de las métricas de los modelos.

## Cómo ejecutar

Desde PowerShell en la carpeta del repositorio:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe src\etl.py
```

En SQL Server Management Studio:

1. Ejecutar `sql/01_crear_base_y_datamart.sql`.
2. Ajustar `@ArchivoCsv` en `sql/02_cargar_dataset.sql` si el repositorio está en otra ruta.
3. Ejecutar `sql/02_cargar_dataset.sql`.

Para abrir el dashboard local:

```powershell
.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

La base `ECBD_Compradores` vive en la instancia SQL Server LocalDB de esta computadora. GitHub conserva los scripts para reproducirla; no se suben los archivos internos de la base.

## Pendiente para el cierre

- Borrador ampliado y versión PDF del informe final.
- Conclusiones y recomendaciones finales revisadas.
- Defensa oral: ejecutar y explicar limpieza, ETL, Data Mart, métricas, clusters y dashboard.
- Revisar observaciones del docente y actualizar los notebooks en consecuencia.
