/*
Validación de la carga realizada desde Python.

La carga de datos (CSV -> Staging -> Dimensiones -> FactSesion)
se realiza ahora mediante el script Python: src/etl/cargar_sql.py

Este script SQL solo valida que la carga sea correcta.
Se puede ejecutar en SSMS o Azure Data Studio después de correr el ETL con --cargar-sql.
*/
USE ECBD_Compradores;
GO

-- Verificar conteos
SELECT N'StgSesiones' AS Tabla, COUNT_BIG(*) AS Filas FROM dbo.StgSesiones
UNION ALL
SELECT N'FactSesion', COUNT_BIG(*) FROM dbo.FactSesion
UNION ALL
SELECT N'DimMes', COUNT_BIG(*) FROM dbo.DimMes
UNION ALL
SELECT N'DimTipoVisitante', COUNT_BIG(*) FROM dbo.DimTipoVisitante
UNION ALL
SELECT N'DimSistemaOperativo', COUNT_BIG(*) FROM dbo.DimSistemaOperativo
UNION ALL
SELECT N'DimNavegador', COUNT_BIG(*) FROM dbo.DimNavegador
UNION ALL
SELECT N'DimRegion', COUNT_BIG(*) FROM dbo.DimRegion
UNION ALL
SELECT N'DimTipoTrafico', COUNT_BIG(*) FROM dbo.DimTipoTrafico;
GO

-- Verificar integridad referencial (FK sin correspondencia)
SELECT N'FactSinMes' AS Check, COUNT_BIG(*) AS Cantidad
FROM dbo.FactSesion f LEFT JOIN dbo.DimMes d ON f.MesKey = d.MesKey WHERE d.MesKey IS NULL
UNION ALL
SELECT N'FactSinVisitante', COUNT_BIG(*)
FROM dbo.FactSesion f LEFT JOIN dbo.DimTipoVisitante d ON f.TipoVisitanteKey = d.TipoVisitanteKey WHERE d.TipoVisitanteKey IS NULL
UNION ALL
SELECT N'FactSinSO', COUNT_BIG(*)
FROM dbo.FactSesion f LEFT JOIN dbo.DimSistemaOperativo d ON f.SistemaOperativoKey = d.SistemaOperativoKey WHERE d.SistemaOperativoKey IS NULL
UNION ALL
SELECT N'FactSinNavegador', COUNT_BIG(*)
FROM dbo.FactSesion f LEFT JOIN dbo.DimNavegador d ON f.NavegadorKey = d.NavegadorKey WHERE d.NavegadorKey IS NULL
UNION ALL
SELECT N'FactSinRegion', COUNT_BIG(*)
FROM dbo.FactSesion f LEFT JOIN dbo.DimRegion d ON f.RegionKey = d.RegionKey WHERE d.RegionKey IS NULL
UNION ALL
SELECT N'FactSinTrafico', COUNT_BIG(*)
FROM dbo.FactSesion f LEFT JOIN dbo.DimTipoTrafico d ON f.TipoTraficoKey = d.TipoTraficoKey WHERE d.TipoTraficoKey IS NULL;
GO

-- Muestra de datos cargados
SELECT TOP (10) * FROM dbo.FactSesion;
GO

