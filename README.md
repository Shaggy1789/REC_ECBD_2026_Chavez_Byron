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

## Estructura del repositorio

```
REC_ECDB_2026_ChavezMolina_Byron/
├── README.md                              # Este documento: guía de lectura y explicación del proyecto
├── requirements.txt                       # Librerías de Python necesarias
├── .gitignore                             # Archivos y carpetas que Git ignora (entorno, caché, etc.)
├── dashboard/
│   └── app.py                             # Dashboard interactivo con Streamlit
├── data/
│   ├── raw/
│   │   └── online_shoppers_intention.csv  # Dataset original (no se modifica)
│   └── processed/
│       ├── clean/
│       │   └── online_shoppers_intention_clean.csv   # Dataset limpio (salida del ETL)
│       ├── clustering/
│       │   └── sesiones_clusterizadas.csv            # Sesiones con su cluster asignado
│       └── pca/
│           └── coordenadas_pca.csv                   # Coordenadas PCA para graficar
├── docs/
│   ├── etl/
│   │   └── borrador_informe_final.md    # Borrador del informe final del curso
│   ├── data_mart/
│   │   └── diagrama_data_mart.md        # Esquema estrella del Data Mart (Mermaid)
│   └── evidencias/
│       └── pca_clusters.png             # Gráfica de clusters PCA
├── modelos/
│   ├── regresion/
│   │   └── regresion_product_duration.joblib  # Modelo entrenado: predicción de duración
│   ├── clasificacion/
│   │   └── clasificacion_revenue.joblib       # Modelo entrenado: predicción de compra
│   ├── clustering/
│   │   ├── kmeans_sesiones.joblib             # Modelo entrenado: agrupamiento K-Means
│   │   └── pca_sesiones.joblib                # Modelo entrenado: transformación PCA
│   └── metricas/
│       ├── metricas_clasificacion.csv         # Métricas del modelo de clasificación
│       ├── metricas_regresion.csv             # Métricas del modelo de regresión
│       ├── metricas_kmeans.csv                # Métricas del modelo K-Means
│       └── varianza_pca.csv                   # Varianza explicada por cada componente PCA
├── notebooks/
│   ├── unidad_ii_exploracion/
│   │   ├── 01_revision_datos.ipynb           # Revisión inicial del dataset
│   │   ├── 02_Limpieza de datos.ipynb        # Limpieza paso a paso: duplicados, estandarización de meses, validaciones
│   │   └── ChavezMolina_Byron_U2_AE1_Exploracion.ipynb  # Exploración y diagnóstico completo
│   ├── unidad_ii_datamart/
│   │   ├── 00_reiniciar_datamart_python.ipynb  # NUEVO: Notebook para reiniciar Data Mart con Python
│   │   └── 02_diseno_base_datos_datamart.ipynb  # Diseño del Data Mart (actualizado)
│   ├── unidad_iii_supervisado/
│   │   └── 03_modelos_supervisados.ipynb     # Regresión y clasificación
│   └── unidad_iv_no_supervisado/
│       └── 04_clustering_pca.ipynb           # Clustering y PCA
├── sql/
│   ├── ddl/
│   │   ├── 00_reiniciar_datamart.sql         # NUEVO: Script SQL idempotente para reiniciar Data Mart
│   │   └── 01_crear_base_y_datamart.sql      # Crea la base y las tablas del esquema estrella
│   └── dml/
│       └── 02_cargar_dataset.sql             # Carga el CSV y popula dimensiones y hechos
└── src/
    ├── etl/
    │   ├── etl.py               # Orquesta la lectura, limpieza y guardado del dataset procesado
    │   ├── limpieza.py          # Funciones de limpieza y diagnóstico de datos
    │   └── reset_datamart.py    # NUEVO: Script Python (pyodbc) para reiniciar Data Mart
    ├── exploracion/
    │   └── exploracion.py       # Funciones básicas de exploración (head, shape, columnas, etc.)
    └── visualizacion/
        └── visualizacion.py     # Gráficas exploratorias con matplotlib y seaborn
```

---

## Los datos

| Archivo | Descripción |
|---------|-------------|
| `data/raw/online_shoppers_intention.csv` | Dataset original con 12,330 filas y 18 variables. No se modifica. |
| `data/processed/clean/online_shoppers_intention_clean.csv` | Dataset limpio con 12,205 filas y 18 variables. Resultado del ETL. |
| `data/processed/clustering/sesiones_clusterizadas.csv` | Igual al limpio, pero con una columna extra `Cluster` (asignación de K-Means). |
| `data/processed/pca/coordenadas_pca.csv` | Coordenadas de las sesiones en los dos componentes principales de PCA. |

**Limpieza realizada (`src/etl/limpieza.py` y documentada en `notebooks/unidad_ii_exploracion/02_Limpieza de datos.ipynb`):**
- Se eliminan **filas duplicadas exactas** (se detectaron 125 duplicados).
- Se normaliza la columna `Month`: se reemplaza `"June"` por `"Jun"` para homogeneizar los nombres de mes.
- Se verifica que no queden valores faltantes ni valores negativos inesperados en columnas numéricas.
- Se validan las categorías de todas las variables categóricas.

El ETL (`src/etl/etl.py`) lee el archivo original, aplica la limpieza y guarda el resultado en `data/processed/clean/online_shoppers_intention_clean.csv`.

---

## Código fuente (`src/`)

Aquí va una explicación línea por línea de lo que hace cada módulo, para que lo sepas de memoria.

### `src/etl/etl.py` — Orquestador del ETL
Es el punto de entrada para procesar los datos. Al ejecutarlo:
1. Lee `data/raw/online_shoppers_intention.csv`.
2. Llama a `limpiar_datos()` de `src/etl/limpieza.py`.
3. Crea la carpeta `data/processed/clean/` si no existe.
4. Guarda el resultado en `data/processed/clean/online_shoppers_intention_clean.csv`.
5. Imprime un resumen: filas originales, duplicados eliminados, filas finales y faltantes restantes.

### `src/etl/limpieza.py` — Limpieza y diagnóstico
Contiene funciones reutilizables para inspeccionar y limpiar el dataset (el proceso completo está documentado paso a paso en `notebooks/unidad_ii_exploracion/02_Limpieza de datos.ipynb`):

- `revisar_valores_faltantes(datos)` → devuelve cuántos y qué porcentaje de faltantes hay por columna.
- `revisar_duplicados(datos)` → cuenta filas duplicadas exactas.
- `revisar_valores_negativos(datos)` → cuenta valores negativos por columna numérica.
- `revisar_categorias(datos)` → lista los valores únicos de cada columna categórica.
- `limpiar_datos(datos)` → función principal: copia los datos, elimina duplicados, normaliza `Month` y devuelve el DataFrame limpio junto con un resumen de cambios.

### `src/exploracion/exploracion.py` — Exploración básica
Funciones pequeñas para entender el dataset al inicio:

- `mostrar_primeros_registros(datos, cantidad=5)` → muestra las primeras filas (`head`).
- `mostrar_dimensiones(datos)` → devuelve filas y columnas (`shape`).
- `mostrar_columnas(datos)` → devuelve los nombres de las columnas.
- `mostrar_tipos_datos(datos)` → devuelve el tipo de cada columna (`dtypes`).
- `mostrar_resumen(datos)` → devuelve estadísticas descriptivas (`describe`).

### `src/visualizacion/visualizacion.py` — Gráficas exploratorias
Gráficas iniciales con matplotlib y seaborn:

- `grafica_tipo_visitante(datos)` → barras de sesiones por tipo de visitante.
- `grafica_compras(datos)` → barras de sesiones que terminaron en compra vs. no compra.
- `histograma_duracion_productos(datos)` → histograma del tiempo en páginas de productos.

---

## SQL y Data Mart (`sql/`)

Se diseña un **esquema estrella** con una tabla de hechos y seis dimensiones. El grano de `FactSesion` es **una sesión**.

### Archivos SQL

- `sql/ddl/01_crear_base_y_datamart.sql` — Crea la base de datos `ECBD_Compradores`, las tablas de dimensiones y la tabla de hechos con sus claves primarias y foráneas.
- `sql/dml/02_cargar_dataset.sql` — **Validación** de la carga realizada desde Python. Verifica conteos, integridad referencial y muestra una muestra de datos.

### Carga de datos

La carga del CSV procesado a SQL Server se realiza mediante Python:

```powershell
.venv\Scripts\python.exe -m src.etl.etl --cargar-sql
```

Este comando:
1. Lee `data/processed/clean/online_shoppers_intention_clean.csv`.
2. Inserta los datos en `StgSesiones` (staging).
3. Pobla las 6 dimensiones con `MERGE` (upsert) para evitar duplicados.
4. Inserta en `FactSesion` usando consultas parametrizadas por lotes.
5. Valida que el conteo de staging coincida con `FactSesion`.

> No se usa `BULK INSERT` ni SQL puro para la carga. El script SQL `sql/dml/02_cargar_dataset.sql` solo valida.

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

Cada notebook es ejecutable y corresponde a una parte del proyecto, organizado por unidades:

| Notebook | Qué hace |
|----------|----------|
| `unidad_ii_exploracion/01_revision_datos.ipynb` | Revisión inicial del dataset: dimensiones, tipos, faltantes, duplicados, primeras filas. |
| `unidad_ii_exploracion/02_Limpieza de datos.ipynb` | Limpieza documentada paso a paso: eliminación de 125 duplicados, normalización `June`→`Jun`, validación de dominio (sin negativos), validación de categorías, guardado en `data/processed/clean/`. |
| `unidad_ii_exploracion/ChavezMolina_Byron_U2_AE1_Exploracion.ipynb` | Exploración y diagnóstico completo con diccionario de variables. |
| `unidad_ii_datamart/02_diseno_base_datos_datamart.ipynb` | Documenta el diseño del esquema estrella y el Data Mart. |
| `unidad_iii_supervisado/03_modelos_supervisados.ipynb` | Entrena modelos de regresión y clasificación; guarda modelos y métricas en `modelos/`. |
| `unidad_iv_no_supervisado/04_clustering_pca.ipynb` | Ejecuta K-Means (K=2 a K=6) y PCA; guarda clusterizaciones, coordenadas y gráfica. |

---

## Modelos supervisados (`modelos/` y `notebooks/unidad_iii_supervisado/03_modelos_supervisados.ipynb`)

Se entrenaron dos modelos con Random Forest:

### 1. Regresión: predecir `ProductRelated_Duration`
- **Objetivo:** estimar cuántos segundos pasará un visitante navegando en páginas de producto.
- **Métricas en prueba:** MAE ≈ 510.76 s, R² ≈ 0.715.
- **Archivo guardado:** `modelos/regresion/regresion_product_duration.joblib`.

### 2. Clasificación: predecir `Revenue` (¿compra o no?)
- **Objetivo:** predecir si una sesión termina en compra.
- **Métricas en prueba:** F1 ≈ 0.688, recall de compra ≈ 0.730, ROC AUC ≈ 0.929.
- **Regresión logística:** recall de compra ≈ 0.796.
- **Archivo guardado:** `modelos/clasificacion/clasificacion_revenue.joblib`.

Todas las métricas se guardan en CSV dentro de `modelos/metricas/` para que el dashboard las pueda leer.

---

## Análisis no supervisado (`notebooks/unidad_iv_no_supervisado/04_clustering_pca.ipynb` y `docs/`)

- **K-Means:** se probó de K=2 a K=6 clusters. K=2 obtuvo silhouette muestrado de 0.934.
- **PCA:** se transformaron y escalaron las variables sesgadas; dos componentes explican el 99.9% de la varianza.
- **Resultados:**
  - `data/processed/clustering/sesiones_clusterizadas.csv` — cada sesión con su cluster.
  - `data/processed/pca/coordenadas_pca.csv` — coordenadas para graficar.
  - `docs/evidencias/pca_clusters.png` — gráfica de los clusters en el espacio PCA.

---

## Dashboard interactivo (`dashboard/app.py`)

Aplicación de Streamlit para explorar los resultados con filtros y gráficas.

**Cómo se ejecuta:**
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

### 2. Ejecutar el ETL (limpieza de datos y carga a SQL Server)
```powershell
.venv\Scripts\python.exe -m src.etl.etl --cargar-sql
```
Esto genera `data/processed/clean/online_shoppers_intention_clean.csv` **y** carga los datos a SQL Server.

> **Nota:** El ETL se ejecuta como módulo (`-m src.etl.etl`) porque utiliza importaciones relativas (`from .limpieza import limpiar_datos`).
> El flag `--cargar-sql` activa la carga a SQL Server mediante `src/etl/cargar_sql.py`.

### 3. Crear la base de datos (SQL Server)
1. Abrir SQL Server Management Studio (SSMS).
2. Ejecutar `sql/ddl/01_crear_base_y_datamart.sql`.
   - Esto crea la base `ECBD_Compradores`, la tabla `StgSesiones`, las 6 dimensiones y `FactSesion`.
   - **Debe ejecutarse antes de la carga desde Python.**

### 4. Validar la carga (opcional)
En SSMS, ejecutar `sql/dml/02_cargar_dataset.sql` para verificar:
- Conteo de filas en staging, hechos y dimensiones.
- Integridad referencial (FK sin correspondencia).
- Muestra de datos en `FactSesion`.

### 4. Entrenar modelos (opcional, si quieres regenerarlos)
Abrir y ejecutar todas las celdas de `notebooks/unidad_iii_supervisado/03_modelos_supervisados.ipynb`.

### 5. Ejecutar clustering y PCA (opcional)
Abrir y ejecutar todas las celdas de `notebooks/unidad_iv_no_supervisado/04_clustering_pca.ipynb`.

### 6. Abrir el dashboard
```powershell
.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

---

## Guía rápida: ¿qué responder si te preguntan?

| Pregunta | Respuesta breve |
|----------|-----------------|
| ¿De qué trata el proyecto? | Analizar sesiones de compras online para predecir si hay compra y cuánto duran en páginas de producto, usando ETL, Data Mart, modelos supervisados, clustering y un dashboard. |
| ¿Qué hace `src/etl/etl.py`? | Lee el CSV original, aplica limpieza (duplicados y normalización de mes) y guarda el archivo procesado. |
| ¿Qué hace `src/etl/limpieza.py`? | Tiene funciones para diagnosticar faltantes, duplicados, negativos y categorías, y la función principal `limpiar_datos()`. |
| ¿Qué modelo usaste para predecir compra? | Random Forest (clasificación), con F1 ≈ 0.688 y ROC AUC ≈ 0.929. |
| ¿Qué modelo usaste para predecir duración? | Random Forest (regresión), con MAE ≈ 510.76 s y R² ≈ 0.715. |
| ¿Qué hace el dashboard? | Muestra KPIs, gráficas por mes/visitante/cluster y métricas de modelos, con filtros interactivos. |
| ¿Cuál es el esquema de la base? | Esquema estrella: una tabla de hechos `FactSesion` (una fila por sesión) y seis dimensiones (mes, visitante, SO, navegador, región, tráfico). |
| ¿Quién escribió el código? | Desarrollé el proyecto con asistencia de Codex (IA); yo revisé, ejecuté y validé cada componente. |

---

## Reinicio del Data Mart (NUEVO: Scripts SQL y Python)

Para facilitar el desarrollo del ETL en **SSIS (Visual Studio)**, se añadieron scripts idempotentes que permiten eliminar y reconstruir las tablas del Data Mart sin borrar la base de datos completa. Esto es útil para hacer "reset" limpio antes de cada prueba del paquete SSIS.

### Archivos nuevos

| Archivo | Descripción |
|---------|-------------|
| `sql/ddl/00_reiniciar_datamart.sql` | Script SQL idempotente para ejecutar en SSMS (F5) |
| `src/etl/reset_datamart.py` | Script Python (pyodbc) ejecutable desde terminal/CI/CD |
| `notebooks/unidad_ii_datamart/00_reiniciar_datamart_python.ipynb` | Notebook que documenta y ejecuta la versión Python |

### Qué hacen (ambas versiones son equivalentes)

1. **Conectan** a la base `ECBD_Compradores` en LocalDB.
2. **Eliminan** las 8 tablas en orden correcto (respetando FK):
   - `FactSesion` (6 FK) → 6 dimensiones → `StgSesiones`
3. **Recrean** las 8 tablas con la definición exacta del diseño original:
   - `StgSesiones`: 18 columnas, tipos adaptados al CSV (texto para booleanos/tasas)
   - 6 dimensiones: PK sustituta `*Key INT IDENTITY(1,1)` + `UNIQUE` en atributo natural
   - `FactSesion`: PK `SesionKey BIGINT IDENTITY`, 6 FK, medidas e indicadores
4. **Validan** la creación (tablas, PK, FK, UNIQUE).
5. Son **idempotentes**: se pueden ejecutar las veces que se quiera sin errores.

### Ejecución del script SQL (SSMS)

```powershell
# 1. Abrir SSMS y conectar a (localdb)\MSSQLLocalDB
# 2. Archivo > Abrir > sql/ddl/00_reiniciar_datamart.sql
# 3. Pulsar F5 (Ejecutar)
# 4. Verificar en pestaña "Mensajes" que aparecen las 8 tablas creadas
```

### Ejecución del script Python (terminal)

```powershell
# Desde la raíz del proyecto
python -m src.etl.reset_datamart
# O directamente:
python src/etl/reset_datamart.py
```

**Requisitos previos:**
- `pyodbc` instalado (`pip install pyodbc` — ya en requirements.txt)
- LocalDB corriendo: `sqllocaldb start MSSQLLocalDB`
- Base `ECBD_Compradores` existe (ejecutar `sql/ddl/01_crear_base_y_datamart.sql` una vez)

### Ejecución desde el notebook

Abrir `notebooks/unidad_ii_datamart/00_reiniciar_datamart_python.ipynb` y ejecutar la celda de código. El notebook configura automáticamente el `PYTHONPATH` y el directorio de trabajo para encontrar `src.etl`.

### Salida esperada (ejemplo)

```
======================================================================
REINICIO DEL DATA MART - ECBD_Compradores
======================================================================

Conectando a: (localdb)\MSSQLLocalDB / ECBD_Compradores
  [OK] Conexión establecida

--- ELIMINANDO TABLAS EXISTENTES ---
  -> Eliminando Tabla de hechos (tiene 6 FK hacia dimensiones) (dbo.FactSesion)
    [OK] dbo.FactSesion eliminada
  -> Eliminando Dimensión Mes (dbo.DimMes)
    [OK] dbo.DimMes eliminada
  ... (6 dimensiones más) ...
  -> Eliminando Tabla de staging (sin FK) (dbo.StgSesiones)
    [OK] dbo.StgSesiones eliminada

--- CREANDO TABLA DE STAGING ---
  -> Creando dbo.StgSesiones
    [OK] dbo.StgSesiones creada
  -> Ajustando tipo de BounceRates a NVARCHAR(32)
  ...

--- CREANDO DIMENSIONES ---
  -> Creando dbo.DimMes
    [OK] dbo.DimMes creada (PK=MesKey, UNIQUE=Mes)
  ... (5 dimensiones más) ...

--- CREANDO TABLA DE HECHOS ---
  -> Creando dbo.FactSesion
    [OK] dbo.FactSesion creada (PK=SesionKey, 6 FK, medidas e indicadores)

--- VALIDACIÓN FINAL ---
Tablas creadas (8): DimMes, DimNavegador, DimRegion, DimSistemaOperativo, DimTipoTrafico, DimTipoVisitante, FactSesion, StgSesiones
Foreign Keys en FactSesion (6):
  - FK_FactSesion_DimMes -> DimMes
  - FK_FactSesion_DimNavegador -> DimNavegador
  ...
PK y UNIQUE constraints:
  - DimMes.PK_DimMes (PK)
  - DimMes.UQ_DimMes_Mes (UNIQUE)
  ...

======================================================================
PROCESO COMPLETADO CON ÉXITO
======================================================================
```

---

## Actualizaciones al notebook del Data Mart (`02_diseno_base_datos_datamart.ipynb`)

Se completó la documentación según las observaciones del profesor y se corrigieron dos puntos clave.

### 1. Secciones añadidas (documentación completa)

| Sección | Qué contiene |
|---------|--------------|
| **1.1 Diccionario de variables (18 variables)** | Tabla completa: nombre, descripción, tipo estadístico (cuantitativa/cualitativa), escala (ratio/nominal/ordinal), tipo SQL sugerido, justificación. |
| **2.1 Variables por modelo** | Detalle de target y predictores para cada uno de los 3 modelos:<br>• **Regresión**: target `ProductRelated_Duration` — 16 predictores (excluye `Revenue` Y `ProductRelated_Duration`)<br>• **Clasificación**: target `Revenue` — 17 predictores (todas menos el target)<br>• **Clustering**: 10 variables comportamentales; `Revenue` excluido del entrenamiento, usado solo *post-hoc* para etiquetar clusters |
| **2 (Limpieza) — Duplicados** | Aclaración: se eliminaron **125 duplicados exactos** (12,330 → 12,205 filas), pero **no se asume** que sean la misma sesión real; `SesionKey` en el Data Mart es clave sustituta (surrogate key). |
| **3.1 Grano de FactSesion** | Redefinido como **"una fila por registro procesado del dataset"**, no "una fila por sesión única". |
| **3.6 Staging** | Definición completa de `StgSesiones` con 18 columnas y tipos adaptados. |
| **3.7 Seis dimensiones** | DDL de `DimMes`, `DimTipoVisitante`, `DimSistemaOperativo`, `DimNavegador`, `DimRegion`, `DimTipoTrafico` con PK `IDENTITY`, `UNIQUE` en atributo natural. |
| **3.8 Tabla de hechos FactSesion** | DDL completa: PK `SesionKey BIGINT IDENTITY`, 6 FK, medidas (duraciones, conteos, tasas, `PageValues`), indicadores (`SpecialDay`, `Weekend BIT`, `Revenue BIT`). |
| **3.10 Tabla de verificación DDL vs Diseño** | 8 controles de validación (tablas, PK, FK, UNIQUE, IDENTITY, tipos, NOT NULL, grano). |
| **4.1 Power BI y dimensiones** | Aclaración: Power BI usa subconjunto de tablas; **no borra dimensiones** ni datos maestros. |
| **7 Estado del proyecto** | Tablas de estado: implementado / documentado / pendiente (Data Mart, ETL Python, ETL SSIS, Modelos, Dashboard, Informe). |

### 2. Correcciones específicas realizadas

| Punto | Antes | Después (corregido) |
|-------|-------|---------------------|
| **Regresión: predictores** | Se mencionaban 17 predictores (excluyendo solo `Revenue`) | **16 predictores**: se excluyen `Revenue` **Y** `ProductRelated_Duration` (el target no puede ser predictor) |
| **Grano de FactSesion** | "Una fila por sesión única" | **"Una fila por registro procesado del dataset"** (evita contradicción con el hecho de que `SesionKey` es surrogate key y no hay clave natural de sesión en el dataset original) |

---

## Cómo ejecutar todo, paso a paso (actualizado)

### 1. Instalar dependencias
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Ejecutar el ETL (limpieza + carga a SQL Server)
```powershell
.venv\Scripts\python.exe -m src.etl.etl --cargar-sql
```

### 3. Crear/reiniciar la base de datos (SQL Server)

**Opción A — Primera vez (crear todo):**
```powershell
# En SSMS: ejecutar sql/ddl/01_crear_base_y_datamart.sql
```

**Opción B — Reinicio durante desarrollo SSIS (ya existe la base):**
```powershell
# SQL (SSMS):
#   Ejecutar sql/ddl/00_reiniciar_datamart.sql  (F5)

# Python (terminal):
python -m src.etl.reset_datamart

# Notebook:
#   Abrir notebooks/unidad_ii_datamart/00_reiniciar_datamart_python.ipynb y ejecutar
```

### 4. Validar la carga (opcional)
En SSMS, ejecutar `sql/dml/02_cargar_dataset.sql`.

### 5. Entrenar modelos (opcional)
Ejecutar `notebooks/unidad_iii_supervisado/03_modelos_supervisados.ipynb`.

### 6. Clustering y PCA (opcional)
Ejecutar `notebooks/unidad_iv_no_supervisado/04_clustering_pca.ipynb`.

### 7. Dashboard
```powershell
.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

---

## Guía rápida: ¿qué responder si te preguntan? (actualizada)

| Pregunta | Respuesta breve |
|----------|-----------------|
| ¿De qué trata el proyecto? | Analizar sesiones de compras online para predecir si hay compra y cuánto duran en páginas de producto, usando ETL, Data Mart, modelos supervisados, clustering y un dashboard. |
| ¿Qué hace `src/etl/etl.py`? | Lee el CSV original, aplica limpieza (duplicados y normalización de mes) y guarda el archivo procesado. |
| ¿Qué hace `src/etl/limpieza.py`? | Tiene funciones para diagnosticar faltantes, duplicados, negativos y categorías, y la función principal `limpiar_datos()`. |
| **¿Qué hace `src/etl/reset_datamart.py`?** | **Elimina y reconstruye las 8 tablas del Data Mart (hechos + 6 dimensiones + staging) en orden correcto de FK, de forma idempotente, para permitir "reset" limpio durante desarrollo SSIS.** |
| **¿Qué hace `sql/ddl/00_reiniciar_datamart.sql`?** | **Versión SQL del reset idempotente; se ejecuta en SSMS (F5) y hace lo mismo que el script Python.** |
| ¿Qué modelo usaste para predecir compra? | Random Forest (clasificación), con F1 ≈ 0.688 y ROC AUC ≈ 0.929. |
| ¿Qué modelo usaste para predecir duración? | Random Forest (regresión), con MAE ≈ 510.76 s y R² ≈ 0.715. |
| ¿Qué hace el dashboard? | Muestra KPIs, gráficas por mes/visitante/cluster y métricas de modelos, con filtros interactivos. |
| ¿Cuál es el esquema de la base? | Esquema estrella: una tabla de hechos `FactSesion` (una fila por registro procesado) y seis dimensiones (mes, visitante, SO, navegador, región, tráfico). |
| **¿Cuántos predictores usa la regresión?** | **16** (excluye `Revenue` y `ProductRelated_Duration`). |
| **¿Cuál es el grano de FactSesion?** | **Una fila por registro procesado del dataset** (clave sustituta `SesionKey`, no hay clave natural de sesión única). |
| ¿Quién escribió el código? | Desarrollé el proyecto con asistencia de Codex (IA); yo revisé, ejecuté y validé cada componente. |

---

## Pendiente para el cierre

- Borrador ampliado y versión PDF del informe final.
- Conclusiones y recomendaciones finales revisadas.
- Defensa oral: ejecutar y explicar limpieza, ETL, Data Mart, métricas, clusters y dashboard.
- Revisar observaciones del docente y actualizar los notebooks en consecuencia.

---
