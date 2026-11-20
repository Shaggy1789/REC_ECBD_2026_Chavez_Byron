/*
Carga completa del CSV procesado al staging y al Data Mart.
Ajusta @ArchivoCsv si el repositorio está en otra ubicación.
Se puede volver a ejecutar: staging se recarga y FactSesion se reconstruye.
*/
USE ECBD_Compradores;
GO

DECLARE @ArchivoCsv NVARCHAR(4000) = N'C:\Users\chave\REC_ECDB_2026_ChavezMolina_Byron\data\processed\clean\online_shoppers_intention_clean.csv';
DECLARE @Comando NVARCHAR(MAX);

TRUNCATE TABLE dbo.StgSesiones;

SET @Comando =
    N'BULK INSERT dbo.StgSesiones FROM ''' + REPLACE(@ArchivoCsv, N'''', N'''''') + N''' ' +
    N'WITH (FORMAT = ''CSV'', FIRSTROW = 2, CODEPAGE = ''65001'', TABLOCK);';
EXEC sys.sp_executesql @Comando;

IF EXISTS (SELECT 1 FROM dbo.StgSesiones WHERE TRY_CONVERT(float, BounceRates) IS NULL)
    THROW 51003, 'BounceRates contiene valores no numericos.', 1;
IF EXISTS (SELECT 1 FROM dbo.StgSesiones WHERE UPPER(LTRIM(RTRIM(Weekend))) NOT IN (N'TRUE', N'FALSE', N'1', N'0'))
    THROW 51001, 'Weekend contiene valores distintos de True/False.', 1;
IF EXISTS (SELECT 1 FROM dbo.StgSesiones WHERE UPPER(LTRIM(RTRIM(Revenue))) NOT IN (N'TRUE', N'FALSE', N'1', N'0'))
    THROW 51002, 'Revenue contiene valores distintos de True/False.', 1;
GO

SET XACT_ABORT ON;
BEGIN TRY
    BEGIN TRANSACTION;

    /* Las dimensiones tienen baja cardinalidad. Los bucles TOP (1) evitan requerir grants de memoria para DISTINCT en LocalDB. */
    DECLARE @Mes NVARCHAR(3);
    WHILE EXISTS (SELECT 1 FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimMes AS d WHERE d.Mes = s.[Month]))
    BEGIN
        SELECT TOP (1) @Mes = s.[Month] FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimMes AS d WHERE d.Mes = s.[Month]);
        INSERT INTO dbo.DimMes (Mes) VALUES (@Mes);
    END;

    DECLARE @TipoVisitante NVARCHAR(30);
    WHILE EXISTS (SELECT 1 FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimTipoVisitante AS d WHERE d.TipoVisitante = s.VisitorType))
    BEGIN
        SELECT TOP (1) @TipoVisitante = s.VisitorType FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimTipoVisitante AS d WHERE d.TipoVisitante = s.VisitorType);
        INSERT INTO dbo.DimTipoVisitante (TipoVisitante) VALUES (@TipoVisitante);
    END;

    DECLARE @SistemaOperativo INT;
    WHILE EXISTS (SELECT 1 FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimSistemaOperativo AS d WHERE d.CodigoSistemaOperativo = s.OperatingSystems))
    BEGIN
        SELECT TOP (1) @SistemaOperativo = s.OperatingSystems FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimSistemaOperativo AS d WHERE d.CodigoSistemaOperativo = s.OperatingSystems);
        INSERT INTO dbo.DimSistemaOperativo (CodigoSistemaOperativo) VALUES (@SistemaOperativo);
    END;

    DECLARE @Navegador INT;
    WHILE EXISTS (SELECT 1 FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimNavegador AS d WHERE d.CodigoNavegador = s.Browser))
    BEGIN
        SELECT TOP (1) @Navegador = s.Browser FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimNavegador AS d WHERE d.CodigoNavegador = s.Browser);
        INSERT INTO dbo.DimNavegador (CodigoNavegador) VALUES (@Navegador);
    END;

    DECLARE @Region INT;
    WHILE EXISTS (SELECT 1 FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimRegion AS d WHERE d.CodigoRegion = s.Region))
    BEGIN
        SELECT TOP (1) @Region = s.Region FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimRegion AS d WHERE d.CodigoRegion = s.Region);
        INSERT INTO dbo.DimRegion (CodigoRegion) VALUES (@Region);
    END;

    DECLARE @TipoTrafico INT;
    WHILE EXISTS (SELECT 1 FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimTipoTrafico AS d WHERE d.CodigoTipoTrafico = s.TrafficType))
    BEGIN
        SELECT TOP (1) @TipoTrafico = s.TrafficType FROM dbo.StgSesiones AS s WHERE NOT EXISTS (SELECT 1 FROM dbo.DimTipoTrafico AS d WHERE d.CodigoTipoTrafico = s.TrafficType);
        INSERT INTO dbo.DimTipoTrafico (CodigoTipoTrafico) VALUES (@TipoTrafico);
    END;

    TRUNCATE TABLE dbo.FactSesion;

    INSERT INTO dbo.FactSesion (
        MesKey, TipoVisitanteKey, SistemaOperativoKey, NavegadorKey, RegionKey, TipoTraficoKey,
        Administrative, Administrative_Duration, Informational, Informational_Duration,
        ProductRelated, ProductRelated_Duration, BounceRates, ExitRates, PageValues,
        SpecialDay, Weekend, Revenue
    )
    SELECT
        dm.MesKey,
        dtv.TipoVisitanteKey,
        dso.SistemaOperativoKey,
        dn.NavegadorKey,
        dr.RegionKey,
        dtt.TipoTraficoKey,
        s.Administrative,
        s.Administrative_Duration,
        s.Informational,
        s.Informational_Duration,
        s.ProductRelated,
        s.ProductRelated_Duration,
        CONVERT(decimal(12, 8), TRY_CONVERT(float, s.BounceRates)),
        s.ExitRates,
        s.PageValues,
        s.SpecialDay,
        TRY_CONVERT(bit, s.Weekend),
        TRY_CONVERT(bit, s.Revenue)
    FROM dbo.StgSesiones AS s
    INNER JOIN dbo.DimMes AS dm ON dm.Mes = s.[Month]
    INNER JOIN dbo.DimTipoVisitante AS dtv ON dtv.TipoVisitante = s.VisitorType
    INNER JOIN dbo.DimSistemaOperativo AS dso ON dso.CodigoSistemaOperativo = s.OperatingSystems
    INNER JOIN dbo.DimNavegador AS dn ON dn.CodigoNavegador = s.Browser
    INNER JOIN dbo.DimRegion AS dr ON dr.CodigoRegion = s.Region
    INNER JOIN dbo.DimTipoTrafico AS dtt ON dtt.CodigoTipoTrafico = s.TrafficType
    OPTION (LOOP JOIN, MAXDOP 1);

    IF (SELECT COUNT_BIG(*) FROM dbo.StgSesiones) <> (SELECT COUNT_BIG(*) FROM dbo.FactSesion)
        THROW 51000, 'La cantidad de filas de staging y FactSesion no coincide.', 1;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
GO

SELECT N'StgSesiones' AS Tabla, COUNT_BIG(*) AS Filas FROM dbo.StgSesiones
UNION ALL
SELECT N'FactSesion', COUNT_BIG(*) FROM dbo.FactSesion;
GO

