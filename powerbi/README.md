# Power BI Dashboard - ECBD Compradores

Este documento describe la construccion completa del dashboard **ECBD_Compradores_Dashboard.pbix** conectado al Data Mart **ECBD_Compradores** en SQL Server LocalDB.

---

## 1. Modelo de datos y relaciones

### Tablas utilizadas (subconjunto del esquema estrella)

| Tabla | Tipo | Descripción |
|-------|------|-------------|
| FactSesion | Hechos | 12,205 filas - una fila por registro procesado del dataset |
| DimMes | Dimensión | 10 meses (Feb, Mar, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec) |
| DimTipoVisitante | Dimensión | 3 tipos: New_Visitor, Returning_Visitor, Other |
| DimRegion | Dimensión | 9 regiones (codigos 1-9) |

**Tablas EXCLUIDAS** (no se importan a Power BI):
- DimSistemaOperativo (8 codigos)
- DimNavegador (13 codigos)
- DimTipoTrafico (20 codigos)

### Relaciones en Power BI (Modelo en estrella)

DimMes (1) ──────>* FactSesion
DimTipoVisitante (1) ──────>* FactSesion
DimRegion (1) ──────>* FactSesion

- Cardinalidad: Uno a muchos (1:*)
- Direccion de filtro: Simple (de dimension a hecho)
- Activar relacion: Si (todas)

### Columna de orden para meses (DimMes)

La tabla DimMes en SQL Server solo tiene MesKey (1-10) y Mes (abreviatura de 3 letras).
Para ordenar cronologicamente en Power BI **sin alterar los datos originales**, se anade una **columna calculada** en Power BI:

MesOrden = SWITCH(DimMes[Mes], "Feb", 1, "Mar", 2, "May", 3, "Jun", 4, "Jul", 5, "Aug", 6, "Sep", 7, "Oct", 8, "Nov", 9, "Dec", 10, 99)

Luego en la vista Modelo -> seleccionar DimMes[Mes] -> pestaña Herramientas de columna -> Ordenar por columna -> elegir MesOrden.

### Columna de etiqueta legible para region (DimRegion)

La tabla DimRegion tiene RegionKey y CodigoRegion (1-9).
Para mostrar Region 1, Region 2, etc. (sin inventar nombres geograficos):

RegionEtiqueta = "Region " & DimRegion[CodigoRegion]

Usar RegionEtiqueta en ejes y leyendas; CodigoRegion para ordenar.

---

## 2. Medidas DAX

Todas las medidas son simples y validas. No se crean medidas individuales por mes o region; se usa la medida general Tasa de Conversion y el contexto de filtro de cada visual hace el resto.

### Medidas base (hechos)

Total Sesiones = COUNTROWS(FactSesion)
Sesiones con Compra = CALCULATE([Total Sesiones], FactSesion[Revenue] = 1)
Sesiones sin Compra = CALCULATE([Total Sesiones], FactSesion[Revenue] = 0)
Tasa de Conversion = DIVIDE([Sesiones con Compra], [Total Sesiones], 0)
Promedio PageValues = AVERAGE(FactSesion[PageValues])
Promedio ProductRelated_Duration = AVERAGE(FactSesion[ProductRelated_Duration])
Promedio Administrative_Duration = AVERAGE(FactSesion[Administrative_Duration])
Promedio Informational_Duration = AVERAGE(FactSesion[Informational_Duration])
Promedio BounceRates = AVERAGE(FactSesion[BounceRates])
Promedio ExitRates = AVERAGE(FactSesion[ExitRates])
Promedio SpecialDay = AVERAGE(FactSesion[SpecialDay])

### Medidas de conteo por categoria (para evitar conclusiones engañosas)

Conteo por Tipo Visitante = CALCULATE([Total Sesiones], ALLEXCEPT(DimTipoVisitante, DimTipoVisitante[TipoVisitante]))
Conteo por Region = CALCULATE([Total Sesiones], ALLEXCEPT(DimRegion, DimRegion[CodigoRegion]))
Conteo por Mes = CALCULATE([Total Sesiones], ALLEXCEPT(DimMes, DimMes[Mes]))

### Medidas de porcentaje (con base en el contexto actual)

% Sesiones con Compra = DIVIDE([Sesiones con Compra], [Total Sesiones], 0)
% Sesiones sin Compra = DIVIDE([Sesiones sin Compra], [Total Sesiones], 0)

### Medias condicionadas (para analisis de compras)

PageValues | Compra = CALCULATE(AVERAGE(FactSesion[PageValues]), FactSesion[Revenue] = 1)
PageValues | Sin Compra = CALCULATE(AVERAGE(FactSesion[PageValues]), FactSesion[Revenue] = 0)
ProductRelated_Duration | Compra = CALCULATE(AVERAGE(FactSesion[ProductRelated_Duration]), FactSesion[Revenue] = 1)
ProductRelated_Duration | Sin Compra = CALCULATE(AVERAGE(FactSesion[ProductRelated_Duration]), FactSesion[Revenue] = 0)
---

## 3. Paginas del dashboard

### Pagina 1: Resumen General

**Objetivo**: Vista ejecutiva de alto nivel.

| Visual | Tipo | Configuracion |
|--------|------|---------------|
| KPI Total Sesiones | Tarjeta | Valor: [Total Sesiones] |
| KPI Sesiones con Compra | Tarjeta | Valor: [Sesiones con Compra] |
| KPI Tasa de Conversion | Tarjeta | Valor: [Tasa de Conversion] -> Formato: Porcentaje (1 decimal) |
| KPI PageValues Promedio | Tarjeta | Valor: [Promedio PageValues] -> Formato: Numero (2 decimales) - Etiqueta: PageValues Promedio (metrica de valor de pagina) |
| Sesiones por Mes | Grafico de columnas agrupadas | Eje X: DimMes[Mes] (ordenado por MesOrden), Valores: [Total Sesiones], Leyenda: FactSesion[Revenue] |
| Tasa de Conversion por Mes | Grafico de lineas | Eje X: DimMes[Mes] (ordenado por MesOrden), Valores: [Tasa de Conversion] |
| Sesiones por Tipo de Visitante | Grafico de columnas apiladas | Eje X: DimTipoVisitante[TipoVisitante], Valores: [Total Sesiones], Leyenda: FactSesion[Revenue], Anadir etiquetas con [Conteo por Tipo Visitante] |
| Sesiones por Region | Grafico de barras | Eje Y: DimRegion[RegionEtiqueta] (ordenado por CodigoRegion), Valores: [Total Sesiones], Leyenda: FactSesion[Revenue], Anadir etiquetas con [Conteo por Region] |

**Filtros de pagina (slicers)**:
- DimMes[Mes] (lista desplegable, orden cronologico)
- DimTipoVisitante[TipoVisitante] (lista)
- DimRegion[RegionEtiqueta] (lista)
- FactSesion[Weekend] (True/False)
- FactSesion[Revenue] (True/False)

---

### Pagina 2: Comportamiento de Visitantes

**Objetivo**: Analizar patrones de navegacion y engagement.

| Visual | Tipo | Configuracion |
|--------|------|---------------|
| Duracion Promedio en Paginas de Producto | Tarjeta | Valor: [Promedio ProductRelated_Duration] -> Formato: Numero entero (segundos) |
| Duracion Promedio Administrativa | Tarjeta | Valor: [Promedio Administrative_Duration] |
| Duracion Promedio Informacional | Tarjeta | Valor: [Promedio Informational_Duration] |
| Bounce Rate Promedio | Tarjeta | Valor: [Promedio BounceRates] -> Formato: Porcentaje (2 decimales) |
| Exit Rate Promedio | Tarjeta | Valor: [Promedio ExitRates] -> Formato: Porcentaje (2 decimales) |
| ProductRelated_Duration por Mes | Grafico de lineas | Eje X: DimMes[Mes] (ordenado por MesOrden), Valores: [Promedio ProductRelated_Duration], Leyenda: FactSesion[Revenue] |
| Bounce Rate vs Exit Rate por Tipo Visitante | Grafico de dispersion | Eje X: [Promedio BounceRates], Eje Y: [Promedio ExitRates], Leyenda: DimTipoVisitante[TipoVisitante], Detalle: FactSesion[SesionKey] |
| PageValues por Tipo Visitante | Grafico de caja y bigotes | Eje X: DimTipoVisitante[TipoVisitante], Valores: FactSesion[PageValues], Leyenda: FactSesion[Revenue] |
| Administrative vs ProductRelated Duration | Grafico de dispersion | Eje X: FactSesion[Administrative_Duration], Eje Y: FactSesion[ProductRelated_Duration], Leyenda: FactSesion[Revenue], Detalle: FactSesion[SesionKey] |

**Filtros de pagina**: mismos que Pagina 1.

---

### Pagina 3: Analisis de Compras

**Objetivo**: Comparar sesiones con compra vs sin compra.

| Visual | Tipo | Configuracion |
|--------|------|---------------|
| PageValues: Compra vs Sin Compra | Tarjetas multiples | Valores: [PageValues | Compra], [PageValues | Sin Compra], Etiqueta: PageValues (metrica de valor de pagina, no ingreso real) |
| ProductRelated_Duration: Compra vs Sin Compra | Grafico de barras agrupadas | Eje X: FactSesion[Revenue] (True/False), Valores: [ProductRelated_Duration | Compra], [ProductRelated_Duration | Sin Compra] |
| SpecialDay: Compra vs Sin Compra | Grafico de columnas agrupadas | Eje X: FactSesion[SpecialDay], Valores: [Total Sesiones], Leyenda: FactSesion[Revenue] |
| Tasa de Conversion por Region | Grafico de barras | Eje Y: DimRegion[RegionEtiqueta] (ordenado por CodigoRegion), Valores: [Tasa de Conversion], Etiquetas: [Conteo por Region] |
| Tasa de Conversion por Tipo Visitante | Grafico de barras | Eje Y: DimTipoVisitante[TipoVisitante], Valores: [Tasa de Conversion], Etiquetas: [Conteo por Tipo Visitante] |
| Distribucion PageValues (Compra vs Sin Compra) | Histograma | Valores: FactSesion[PageValues], Leyenda: FactSesion[Revenue] |
| Weekend vs Compra | Grafico de columnas apiladas 100% | Eje X: FactSesion[Weekend], Valores: [Total Sesiones], Leyenda: FactSesion[Revenue] |

**Filtros de pagina**: mismos que Pagina 1.

---

### Pagina 4: Caracteristicas de Visitantes

**Objetivo**: Perfil demografico/tecnico (con las dimensiones permitidas).

| Visual | Tipo | Configuracion |
|--------|------|---------------|
| Sesiones por Tipo Visitante (Totales) | Grafico de anillo | Valores: [Total Sesiones], Leyenda: DimTipoVisitante[TipoVisitante], Etiquetas: categoria + valor + porcentaje |
| Sesiones por Region (Totales) | Grafico de anillo | Valores: [Total Sesiones], Leyenda: DimRegion[RegionEtiqueta], Etiquetas: categoria + valor + porcentaje |
| Tasa de Conversion por Mes y Tipo Visitante | Matriz | Filas: DimMes[Mes] (ordenado por MesOrden), Columnas: DimTipoVisitante[TipoVisitante], Valores: [Tasa de Conversion], [Total Sesiones] |
| Tasa de Conversion por Region y Mes | Matriz / Heatmap | Filas: DimRegion[RegionEtiqueta] (ordenado por CodigoRegion), Columnas: DimMes[Mes] (ordenado por MesOrden), Valores: [Tasa de Conversion], Formato condicional: escala de color |
| Comportamiento por Tipo Visitante | Grafico de columnas agrupadas | Eje X: DimTipoVisitante[TipoVisitante], Valores: [Promedio ProductRelated_Duration], [Promedio Administrative_Duration], [Promedio Informational_Duration], Leyenda: FactSesion[Revenue] |
| PageValues por Region | Grafico de caja y bigotes | Eje X: DimRegion[RegionEtiqueta] (ordenado por CodigoRegion), Valores: FactSesion[PageValues], Leyenda: FactSesion[Revenue] |

**Filtros de pagina**: mismos que Pagina 1.
---

## 4. Pasos para construir el archivo .pbix

### Paso 1: Abrir Power BI Desktop y conectar a la base de datos

1. **Obtener datos** -> **SQL Server**
2. Servidor: (localdb)\MSSQLLocalDB
3. Base de datos: ECBD_Compradores
4. Modo: **Importar** (recomendado para este tamaño)
5. Seleccionar **solo** estas tablas:
   - dbo.FactSesion
   - dbo.DimMes
   - dbo.DimTipoVisitante
   - dbo.DimRegion
6. Clic en **Cargar** (no Transformar - los datos ya estan limpios).

### Paso 2: Verificar relaciones (Vista Modelo)

1. Ir a la pestaña **Modelo** (icono de diagrama a la izquierda).
2. Verificar que existan estas relaciones (se crean automaticamente por nombre de columna):
   - DimMes[MesKey] 1:* FactSesion[MesKey]
   - DimTipoVisitante[TipoVisitanteKey] 1:* FactSesion[TipoVisitanteKey]
   - DimRegion[RegionKey] 1:* FactSesion[RegionKey]
3. **Eliminar** cualquier relacion hacia tablas no importadas (no deberia haber ninguna).
4. Confirmar: **Cardinalidad 1:\***, **Direccion de filtro simple**, **Activa = Si**.

### Paso 3: Crear columnas calculadas para orden y etiquetas

En la vista **Datos** (icono de tabla), tabla por tabla:

**DimMes** -> Nueva columna:
`
MesOrden = SWITCH(DimMes[Mes], "Feb", 1, "Mar", 2, "May", 3, "Jun", 4, "Jul", 5, "Aug", 6, "Sep", 7, "Oct", 8, "Nov", 9, "Dec", 10, 99)
`
Luego: seleccionar columna Mes -> pestaña **Herramientas de columna** -> **Ordenar por columna** -> MesOrden.

**DimRegion** -> Nueva columna:
`
RegionEtiqueta = "Region " & DimRegion[CodigoRegion]
`
Luego: seleccionar columna RegionEtiqueta -> **Ordenar por columna** -> CodigoRegion.

**FactSesion** -> Verificar que Revenue y Weekend sean tipo **True/False** (booleano). Si aparecen como 1/0, cambiar tipo de dato a **True/False**.

### Paso 4: Crear todas las medidas DAX

En la vista **Modelo** o **Datos**, clic derecho en FactSesion -> **Nueva medida**. Copiar cada medida de la seccion **2. Medidas DAX** arriba.

**Convencion de nombres**: usar exactamente los nombres entre corchetes [...] para que las formulas funcionen.

### Paso 5: Construir cada pagina

Para cada una de las 4 paginas:
1. Clic en **+** (nueva pagina) en la barra inferior.
2. Renombrar la pestana: "Resumen General", "Comportamiento de Visitantes", "Analisis de Compras", "Caracteristicas de Visitantes".
3. Insertar visuales segun las tablas de la **Seccion 3**.
4. Configurar ejes, valores, leyendas y tooltips.
5. **Importante**: En graficos de dispersion, arrastrar FactSesion[SesionKey] al pozo **Detalles** para que cada punto = un registro (no se sumen indebidamente).
6. Anadir **slicers** (filtros) en cada pagina o usar **Sincronizar segmentaciones** (Vista -> Sincronizar segmentaciones) para que los filtros apliquen a todas las paginas.

### Paso 6: Formato y pulido

- **Tasa de Conversion**: formato Porcentaje, 1 decimal.
- **PageValues**: formato Numero, 2 decimales. Anadir nota: "Metrica de valor de pagina, no ingreso monetario real".
- **Duraciones**: formato Numero entero (segundos).
- **Bounce/Exit Rates**: formato Porcentaje, 2 decimales.
- **Colores**: usar paleta coherente (ej. azul para sesiones, verde para compra, rojo/gris para sin compra).
- **Titulos descriptivos** en cada visual.
- **Tooltips** personalizados con medidas adicionales (conteo, promedios).

### Paso 7: Validaciones finales (checklist)

- [ ] **Totales coinciden**: Tarjeta [Total Sesiones] = 12,205 (igual que FactSesion en SQL).
- [ ] **Compra/No compra**: [Sesiones con Compra] = 3,053; [Sesiones sin Compra] = 9,152 (suma = 12,205).
- [ ] **Tasa de Conversion global** = 3,053 / 12,205 ≈ 25.0%.
- [ ] **Meses en orden cronologico**: Feb -> Mar -> May -> Jun -> Jul -> Aug -> Sep -> Oct -> Nov -> Dec.
- [ ] **Filtros funcionan**: Seleccionar un mes en slicer -> todos los graficos se filtran.
- [ ] **Regiones como "Region 1".."Region 9"**: sin nombres geograficos inventados.
- [ ] **Graficos de dispersion**: cada punto = un SesionKey (verificar en Detalles).
- [ ] **Conteos visibles**: en comparaciones por categoria, se muestra numero de registros.
- [ ] **No hay relaciones ambiguas**: solo 3 dimensiones conectadas a FactSesion.
- [ ] **PageValues no descrito como ingreso**: etiquetas claras en visuales.

### Paso 8: Guardar

Archivo -> Guardar como -> C:\Users\chave\REC_ECDB_2026_ChavezMolina_Byron\powerbi\ECBD_Compradores_Dashboard.pbix

---

## 5. Actualizacion de datos (Refresh)

### Desde Power BI Desktop
- Boton **Actualizar** (cinta Inicio) -> vuelve a consultar SQL Server LocalDB.

### Si cambian los datos en el Data Mart
1. Ejecutar el ETL Python (python src/etl/cargar_sql.py) o el paquete SSIS.
2. En Power BI Desktop: **Actualizar**.

### Publicacion en Power BI Service (opcional)
1. Publicar -> Mi espacio de trabajo.
2. Configurar **Gateway de datos local** (on-premises data gateway) para SQL Server LocalDB.
3. Programar actualizacion diaria.

---

## 6. Notas para la defensa oral

- **Grano de FactSesion**: "Una fila por registro procesado del dataset" (12,205 filas). SesionKey es clave sustituta (surrogate key), no hay clave natural de sesion unica en el dataset original.
- **PageValues**: Es una metrica de *valor de pagina* calculada en el dataset original (no es ingreso real ni revenue).
- **Regiones**: Codigos 1-9 del dataset original. No tienen mapeo geografico real; se muestran como "Region 1" a "Region 9".
- **Orden de meses**: Configurado via columna MesOrden en Power BI, sin alterar la tabla DimMes en SQL.
- **Medida unica de conversion**: Tasa de Conversion respeta el contexto de filtro (mes, region, tipo visitante, weekend, etc.). No hay medidas duplicadas por dimension.
- **Dimensiones excluidas**: DimSistemaOperativo, DimNavegador, DimTipoTrafico existen en el Data Mart pero no se usan en este dashboard por decision de alcance.

---

## 7. Estructura de archivos final

`
powerbi/
├── ECBD_Compradores_Dashboard.pbix   # Archivo principal (creado tras seguir esta guia)
└── README.md                         # Este documento
`

---

*Documento generado para el proyecto REC_ECDB_2026_ChavezMolina_Byron. El dashboard se construye manualmente en Power BI Desktop siguiendo estos pasos; este README sirve como guia y documentacion del diseno.*
