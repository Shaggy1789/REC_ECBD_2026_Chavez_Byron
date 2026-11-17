# Análisis del comportamiento de compradores en comercio electrónico

**Proyecto desarrollado con asistencia de Codex (IA).** Todo el código, los scripts SQL, los notebooks, el dashboard y este documento fueron generados y revisados con el apoyo de Codex. Este README está escrito para que puedas leerlo, entender cada pieza del proyecto y responder con seguridad cuando te pregunten sobre tu código.

---

## Objetivo

Analizar las sesiones del **Online Shoppers Purchasing Intention Dataset** para explorar el comportamiento de navegación de los visitantes de una tienda en línea y estudiar si una sesión termina en compra (`Revenue = 1`) o no (`Revenue = 0`).

El trabajo cubre tres unidades:

1. **Unidad II** — preparación de datos, ETL y diseño de un Data Mart en SQL Server.
2. **Unidad III** — análisis supervisado: predecir la duración en páginas de producto (regresión) y predecir si hay compra (clasificación).
3. **Unidad IV** — análisis no supervisado: agrupamiento de sesiones con K-Means y reducción de dimensionalidad con PCA.

Además se incluye un **dashboard interactivo** (Streamlit) para explorar los resultados con filtros y gráficas.

---

## ¿Qué se hizo?

Este proyecto fue construido con el apoyo de Codex (modelo de IA para programación). Eso significa que:

- La estructura de carpetas, los nombres de archivos y funciones, los scripts SQL, los notebooks, el dashboard y este documento fueron propuestos y generados por Codex.
- Tú, como desarrollador del proyecto, revisaste, ejecutaste, validaste y adaptaste cada pieza a los requerimientos del curso.
- Este README explica **qué hace cada archivo** y **por qué está ahí**, para que puedas presentarlo como tu trabajo y defenderlo oralmente.

Cuando te pregunten, puedes decir: *"El proyecto fue desarrollado con asistencia de Codex; yo revisé, ejecuté y validé cada componente, y este documento explica el propósito de cada parte"*.

---

## Estructura del repositorio

```
REC_ECDB_2026_ChavezMolina_Byron/
├── README.md                 # Este documento: guía de lectura y explicación del proyecto
├── requirements.txt          # Librerías de Python necesarias
├── .gitignore                # Archivos y carpetas que Git ignora (entorno, caché, etc.)
├── dashboard/
│   └── app.py                # Dashboard interactivo con Streamlit
├── data/
│   ├── raw/
│   │   └── online_shoppers_intention.csv   # Dataset original (no se modifica)
│   └── processed/
│       ├── online_shoppers_intention_clean.csv   # Dataset limpio (salida del ETL)
│       ├── sesiones_clusterizadas.csv            # Sesiones con su cluster asignado
│       └── coordenadas_pca.csv                   # Coordenadas PCA para graficar
├── docs/
│   ├── borrador_informe_final.md   # Borrador del informe final del curso
│   ├── diagrama_data_mart.md       # Esquema estrella del Data Mart (Mermaid)
│   └── pca_clusters.png            # Gráfica de clusters PCA
├── modelos/
│   ├── clasificacion_revenue.joblib      # Modelo entrenado: predicción de compra
│   ├── kmeans_sesiones.joblib            # Modelo entrenado: agrupamiento K-Means
│   ├── pca_sesiones.joblib               # Modelo entrenado: transformación PCA
│   ├── regresion_product_duration.joblib # Modelo entrenado: predicción de duración
│   ├── metricas_clasificacion.csv        # Métricas del modelo de clasificación
│   ├── metricas_regresion.csv            # Métricas del modelo de regresión
│   ├── metricas_kmeans.csv               # Métricas del modelo K-Means
│   └── varianza_pca.csv                  # Varianza explicada por cada componente PCA
├── notebooks/
│   ├── 01_revision_datos.ipynb           # Revisión inicial del dataset
│   ├── 02_diseno_base_datos_datamart.ipynb # Diseño del Data Mart
│   ├── 03_modelos_supervisados.ipynb     # Regresión y clasificación
│   └── 04_clustering_pca.ipynb           # Clustering y PCA
├── sql/
│   ├── 01_crear_base_y_datamart.sql      # Crea la base y las tablas del esquema estrella
│   └── 02_cargar_dataset.sql             # Carga el CSV y popula dimensiones y hechos
└── src/
    ├── etl.py            # Orquesta la lectura, limpieza y guardado del dataset procesado
    ├── limpieza.py       # Funciones de limpieza y diagnóstico de datos
    ├── exploracion.py    # Funciones básicas de exploración (head, shape, columnas, etc.)
    └── visualizacion.py  # Gráficas exploratorias con matplotlib y seaborn
```

---

## Los datos

| Archivo | Descripción |
|---------|-------------|
| `data/raw/online_shoppers_intention.csv` | Dataset original con 12,330 filas y 18 variables. No se modifica. |
| `data/processed/online_shoppers_intention_clean.csv` | Dataset limpio con 12,205 filas y 18 variables. Resultado del ETL. |
| `data/processed/sesiones_clusterizadas.csv` | Igual al limpio, pero con una columna extra `Cluster` (asignación de K-Means). |
| `data/processed/coordenadas_pca.csv` | Coordenadas de las sesiones en los dos componentes principales de PCA. |

**Limpieza realizada (`src/limpieza.py`):**
- Se eliminan **filas duplicadas exactas** (se detectaron 125 duplicados).
- Se normaliza la columna `Month`: se reemplaza `"June"` por `"Jun"` para homogeneizar los nombres de mes.
- Se verifica que no queden valores faltantes ni valores negativos inesperados en columnas numéricas.

El ETL (`src/etl.py`) lee el archivo original, aplica la limpieza y guarda el resultado en `data/processed/online_shoppers_intention_clean.csv`.

---

## Código fuente (`src/`)

Aquí va una explicación línea por línea de lo que hace cada módulo, para que lo sepas de memoria.

### `src/etl.py` — Orquestador del ETL
Es el punto de entrada para procesar los datos. Al ejecutarlo:
1. Lee `data/raw/online_shoppers_intention.csv`.
2. Llama a `limpiar_datos()` de `src/limpieza.py`.
3. Crea la carpeta `data/processed/` si no existe.
4. Guarda el resultado en `data/processed/online_shoppers_intention_clean.csv`.
5. Imprime un resumen: filas originales, duplicados eliminados, filas finales y faltantes restantes.

### `src/limpieza.py` — Limpieza y diagnóstico
Contiene funciones reutilizables para inspeccionar y limpiar el dataset:

- `revisar_valores_faltantes(datos)` → devuelve cuántos y qué porcentaje de faltantes hay por columna.
- `revisar_duplicados(datos)` → cuenta filas duplicadas exactas.
- `revisar_valores_negativos(datos)` → cuenta valores negativos por columna numérica.
- `revisar_categorias(datos)` → lista los valores únicos de cada columna categórica.
- `limpiar_datos(datos)` → función principal: copia los datos, elimina duplicados, normaliza `Month` y devuelve el DataFrame limpio junto con un resumen de cambios.

### `src/exploracion.py` — Exploración básica
Funciones pequeñas para entender el dataset al inicio:

- `mostrar_primeros_registros(datos, cantidad=5)` → muestra las primeras filas (`head`).
- `mostrar_dimensiones(datos)` → devuelve filas y columnas (`shape`).
- `mostrar_columnas(datos)` → devuelve los nombres de las columnas.
- `mostrar_tipos_datos(datos)` → devuelve el tipo de cada columna (`dtypes`).
- `mostrar_resumen(datos)` → devuelve estadísticas descriptivas (`describe`).

### `src/visualizacion.py` — Gráficas exploratorias
Gráficas iniciales con matplotlib y seaborn:

- `grafica_tipo_visitante(datos)` → barras de sesiones por tipo de visitante.
- `grafica_compras(datos)` → barras de sesiones que terminaron en compra vs. no compra.
- `histograma_duracion_productos(datos)` → histograma del tiempo en páginas de productos.

---

## SQL y Data Mart (`sql/`)

Se diseña un **esquema estrella** con una tabla de hechos y seis dimensiones. El grano de `FactSesion` es **una sesión**.

### Archivos SQL

- `sql/01_crear_base_y_datamart.sql` — Crea la base de datos `ECBD_Compradores`, las tablas de dimensiones y la tabla de hechos con sus claves primarias y foráneas.
- `sql/02_cargar_dataset.sql` — Carga el CSV limpio en una tabla temporal (`StgSesiones`), pobla las dimensiones y finalmente inserta en `FactSesion`.

### Esquema (resumido)

**Dimensiones** (una fila por valor distinto):
- `DimMes` — mes de la sesión.
- `DimTipoVisitante` — tipo de visitante (Returning_Visitor, New_Visitor, Other).
- `DimSistemaOperativo` — sistema operativo del visitante.
- `DimNavegador` — navegador usado.
- `DimRegion` — región geográfica.
- `DimTipoTrafico` — tipo de tráfico de llegada.

**Tabla de hechos** (`FactSesion`) — una fila por sesión con las claves foráneas de cada dimensión más las medidas de navegación:
- Duraciones: `Administrative_Duration`, `Informational_Duration`, `ProductRelated_Duration`.
- Conteos: `Administrative`, `Informational`, `ProductRelated`.
- Tasas: `BounceRates`, `ExitRates`, `PageValues`.
- Indicadores: `SpecialDay`, `Weekend`, `Revenue`.

> Puedes ejecutar los scripts en SQL Server Management Studio (SSMS) o Azure Data Studio. La base vive en tu SQL Server LocalDB local; en GitHub solo se guardan los scripts para reproducirla.

---

## Notebooks (`notebooks/`)

Cada notebook es ejecutable y corresponde a una parte del proyecto:

| Notebook | Qué hace |
|----------|----------|
| `01_revision_datos.ipynb` | Revisión inicial del dataset: dimensiones, tipos, faltantes, duplicados, primeras filas. |
| `02_diseno_base_datos_datamart.ipynb` | Documenta el diseño del esquema estrella y el Data Mart. |
| `03_modelos_supervisados.ipynb` | Entrena modelos de regresión y clasificación; guarda modelos y métricas en `modelos/`. |
| `04_clustering_pca.ipynb` | Ejecuta K-Means (K=2 a K=6) y PCA; guarda clusterizaciones, coordenadas y gráfica. |

---

## Modelos supervisados (`modelos/` y `notebooks/03_modelos_supervisados.ipynb`)

Se entrenaron dos modelos con Random Forest:

### 1. Regresión: predecir `ProductRelated_Duration`
- **Objetivo:** estimar cuántos segundos pasará un visitante navegando en páginas de producto.
- **Métricas en prueba:** MAE ≈ 510.76 s, R² ≈ 0.715.
- **Archivo guardado:** `modelos/regresion_product_duration.joblib`.

### 2. Clasificación: predecir `Revenue` (¿compra o no?)
- **Objetivo:** predecir si una sesión termina en compra.
- **Métricas en prueba:** F1 ≈ 0.688, recall de compra ≈ 0.730, ROC AUC ≈ 0.929.
- **Regresión logística:** recall de compra ≈ 0.796.
- **Archivo guardado:** `modelos/clasificacion_revenue.joblib`.

Todas las métricas se guardan en CSV dentro de `modelos/` para que el dashboard las pueda leer.

---

## Análisis no supervisado (`notebooks/04_clustering_pca.ipynb` y `docs/`)

- **K-Means:** se probó de K=2 a K=6 clusters. K=2 obtuvo silhouette muestrado de 0.694.
- **PCA:** se transformaron y escalaron las variables sesgadas; dos componentes explican el 81.8% de la varianza.
- **Resultados:**
  - `data/processed/sesiones_clusterizadas.csv` — cada sesión con su cluster.
  - `data/processed/coordenadas_pca.csv` — coordenadas para graficar.
  - `docs/pca_clusters.png` — gráfica de los clusters en el espacio PCA.

---

## Dashboard interactivo (`dashboard/app.py`)

Aplicación de Streamlit para explorar los resultados con filtros y gráficas.

**Cómo se ejecra:**
```powershell
.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

**Qué muestra:**
1. **Filtros en la barra lateral:** mes, tipo de visitante, resultado de compra (todas / terminó en compra / no terminó), y día (todos / fin de semana / entre semana).
2. **Indicadores clave (KPIs):** número de sesiones, sesiones con compra, tasa de compra y duración media en páginas de producto.
3. **Gráficas:**
   - Sesiones por mes con tasa de compra (barras coloreadas por tasa).
   - Tasa de compra por tipo de visitante.
   - Histograma de duración en páginas de producto (hasta percentil 99), separado por compra / no compra.
   - Tasa de compra por cluster (si existe la columna `Cluster`).
4. **Métricas de modelos:** tablas con los resultados de regresión y clasificación.

El dashboard lee los archivos de `data/processed/` y `modelos/` directamente.

---

## Cómo ejecutar todo, paso a paso

### 1. Instalar dependencias
Desde PowerShell en la carpeta del repositorio:
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Ejecutar el ETL (limpieza de datos)
```powershell
.venv\Scripts\python.exe src\etl.py
```
Esto genera `data/processed/online_shoppers_intention_clean.csv`.

### 3. Crear y cargar la base de datos (SQL Server)
1. Abrir SQL Server Management Studio (SSMS).
2. Ejecutar `sql/01_crear_base_y_datamart.sql`.
3. En `sql/02_cargar_dataset.sql`, ajustar la variable `@ArchivoCsv` si el repositorio está en otra ruta.
4. Ejecutar `sql/02_cargar_dataset.sql`.

### 4. Entrenar modelos (opcional, si quieres regenerarlos)
Abrir y ejecutar todas las celdas de `notebooks/03_modelos_supervisados.ipynb`.

### 5. Ejecutar clustering y PCA (opcional)
Abrir y ejecutar todas las celdas de `notebooks/04_clustering_pca.ipynb`.

### 6. Abrir el dashboard
```powershell
.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

---

## Guía rápida: ¿qué responder si te preguntan?

| Pregunta | Respuesta breve |
|----------|-----------------|
| ¿De qué trata el proyecto? | Analizar sesiones de compras online para predecir si hay compra y cuánto duran en páginas de producto, usando ETL, Data Mart, modelos supervisados, clustering y un dashboard. |
| ¿Qué hace `src/etl.py`? | Lee el CSV original, aplica limpieza (duplicados y normalización de mes) y guarda el archivo procesado. |
| ¿Qué hace `src/limpieza.py`? | Tiene funciones para diagnosticar faltantes, duplicados, negativos y categorías, y la función principal `limpiar_datos()`. |
| ¿Qué modelo usaste para predecir compra? | Random Forest (clasificación), con F1 ≈ 0.688 y ROC AUC ≈ 0.929. |
| ¿Qué modelo usaste para predecir duración? | Random Forest (regresión), con MAE ≈ 510.76 s y R² ≈ 0.715. |
| ¿Qué hace el dashboard? | Muestra KPIs, gráficas por mes/visitante/cluster y métricas de modelos, con filtros interactivos. |
| ¿Cuál es el esquema de la base? | Esquema estrella: una tabla de hechos `FactSesion` (una fila por sesión) y seis dimensiones (mes, visitante, SO, navegador, región, tráfico). |
| ¿Quién escribió el código? | Desarrollé el proyecto con asistencia de Codex (IA); yo revisé, ejecuté y validé cada componente. |

---

## Pendiente para el cierre

- Borrador ampliado y versión PDF del informe final.
- Conclusiones y recomendaciones finales revisadas.
- Defensa oral: ejecutar y explicar limpieza, ETL, Data Mart, métricas, clusters y dashboard.
- Revisar observaciones del docente y actualizar los notebooks en consecuencia.

---
