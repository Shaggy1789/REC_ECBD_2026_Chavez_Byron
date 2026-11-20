# Informe final - borrador

## Análisis del comportamiento de compradores en comercio electrónico

### 1. Problema y objetivo

Las sesiones de una tienda en línea no terminan todas en compra. El proyecto explora cómo navegan los visitantes, prepara un Data Mart de sesiones y desarrolla modelos para estimar duración de navegación y clasificar si una sesión termina en compra.

### 2. Datos y preparación

Se utilizó el **Online Shoppers Purchasing Intention Dataset**, con 12,330 sesiones y 18 variables. El archivo original se conserva en `data/raw/`. En el diagnóstico se observaron cero valores faltantes, 125 filas duplicadas exactas y variables con distribuciones asimétricas. La preparación conservó el original, eliminó los 125 duplicados exactos y normalizó el valor de mes `June` a `Jun`. El dataset procesado contiene 12,205 filas y 18 variables, sin duplicados exactos ni faltantes.

La eliminación de duplicados reduce el conjunto a sesiones únicas por sus valores observados; dado que el archivo no contiene un identificador de sesión, filas idénticas podrían representar sesiones distintas indistinguibles. Esta limitación debe explicarse al presentar la limpieza.

### 3. ETL y Data Mart

El ETL de Python genera el archivo procesado. La base local `ECBD_Compradores` recibe las 18 variables en `StgSesiones`; el Data Mart organiza los datos en seis dimensiones (`DimMes`, `DimTipoVisitante`, `DimSistemaOperativo`, `DimNavegador`, `DimRegion`, `DimTipoTrafico`) y una tabla de hechos `FactSesion`.

El grano del hecho es una fila por sesión. La llave sustituta se genera en SQL y las llaves foráneas relacionan cada sesión con sus categorías. La carga ejecutada dejó 12,205 filas en staging y 12,205 en hechos. Las dimensiones contienen los valores distintos identificados en el dataset procesado.

### 4. Análisis supervisado

#### Regresión

Se estimó `ProductRelated_Duration` en segundos. En una partición reproducible de 80/20 con semilla 42, Random Forest obtuvo MAE de 510.76 segundos, RMSE de 1,141.95 segundos y R² de 0.715. El baseline que siempre predice la mediana obtuvo MAE de 1,003.86 segundos. El resultado mejora al baseline, aunque el RMSE evidencia errores grandes en algunas sesiones de duración extrema.

#### Clasificación

Se predijo `Revenue=True` como la clase de compra. En el conjunto de prueba, Random Forest obtuvo accuracy de 0.896, precisión de compra de 0.650, recall de compra de 0.730, F1 de 0.688 y ROC AUC de 0.929. Regresión logística obtuvo recall de compra de 0.796 y F1 de 0.618. El baseline de clase mayoritaria tuvo accuracy de 0.844, pero recall de compra de 0.0; por eso la exactitud aislada no es suficiente ante clases desbalanceadas.

### 5. Análisis no supervisado

K-Means se ajustó sin utilizar `Revenue`, con variables de navegación escaladas de forma robusta (RobustScaler). Entre K=2 y K=6, K=2 alcanzó silhouette muestreado de 0.934. El grupo mayor (Cluster 0) reunió 11,949 sesiones y tuvo tasa de compra de 15.4%; el grupo pequeño (Cluster 1) reunió 256 sesiones y tuvo tasa de compra de 27.7%, mediana de 57 páginas de producto y duración mediana de 2,362.9 segundos. Esto sugiere un grupo de sesiones con alta interacción y mayor intención de compra.

Los dos primeros componentes de PCA explicaron 99.9% de la varianza después del escalado robusto. PC1 explicó 98.2% y su mayor carga absoluta correspondió a `BounceRates`.

### 6. Dashboard

El dashboard local permite filtrar por mes, tipo de visitante, resultado de compra y fin de semana. Presenta conteos de sesiones, compras, tasa de compra, duración, perfil por visitante, segmentos y métricas supervisadas. Las sesiones extremas se conservan en los datos; la gráfica de duración limita el eje al percentil 99 para facilitar su lectura.

### 7. Limitaciones

- El dataset representa sesiones y no incluye identificadores personales o de visitante para reconstruir trayectorias individuales.
- La partición de entrenamiento/prueba usa una sola semilla; las métricas pueden variar bajo otros cortes y deben validarse antes de extrapolarlas.
- Los grupos dependen de las variables, transformaciones y K seleccionados; no representan segmentos comerciales confirmados.
- Los resultados son asociaciones descriptivas y predictivas, no evidencia de que una conducta cause una compra.
- La base de datos ejecutada está en SQL Server LocalDB de la computadora del proyecto; los scripts reproducen su estructura y carga.

### 8. Conclusiones y recomendaciones preliminares

El conjunto procesado permite estudiar la relación entre navegación y compra a nivel de sesión. El modelo de regresión mejora claramente al baseline para estimar duración, y los modelos de clasificación detectan parte de las sesiones que terminan en compra. La regresión logística recupera más compras que Random Forest, mientras que Random Forest logra mayor F1; la selección final debe depender del costo de no detectar una compra frente a generar alertas innecesarias.

El cluster pequeño tiene una tasa de compra mucho menor y señales de interacción casi nula. Una recomendación preliminar sería investigar fricciones en sesiones que abandonan rápidamente y mejorar la navegación hacia productos. El equipo debe validar esta hipótesis con datos adicionales y evitar atribuir causalidad a estas asociaciones.

### 9. Evidencia del proyecto

- Exploración: `notebooks/unidad_ii_exploracion/01_revision_datos.ipynb` y `notebooks/unidad_ii_exploracion/ChavezMolina_Byron_U2_AE1_Exploracion.ipynb`.
- Diseño de base y Data Mart: `notebooks/unidad_ii_datamart/02_diseno_base_datos_datamart.ipynb`.
- Modelos supervisados: `notebooks/unidad_iii_supervisado/03_modelos_supervisados.ipynb`.
- Clustering y PCA: `notebooks/unidad_iv_no_supervisado/04_clustering_pca.ipynb`.
- SQL: `sql/ddl/01_crear_base_y_datamart.sql` y `sql/dml/02_cargar_dataset.sql`.
- Dashboard: `dashboard/app.py`.
- Diagrama: `docs/data_mart/diagrama_data_mart.md`.

Este documento es un borrador. Debe revisarse con las observaciones del docente y complementarse con las decisiones finales y la defensa oral.
