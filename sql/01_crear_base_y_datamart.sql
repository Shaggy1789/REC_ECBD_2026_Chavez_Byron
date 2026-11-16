/*
Proyecto: Analisis del comportamiento de compradores en comercio electronico
Motor: Microsoft SQL Server / SQL Server LocalDB
Proposito: crear la base, staging y esquema estrella del Data Mart.
*/

IF DB_ID(N'ECBD_Compradores') IS NULL
BEGIN
    CREATE DATABASE ECBD_Compradores;
END;
GO

USE ECBD_Compradores;
GO

/* Staging conserva las 18 columnas del CSV procesado. */
IF OBJECT_ID(N'dbo.StgSesiones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.StgSesiones (
        Administrative INT NOT NULL,
        Administrative_Duration DECIMAL(14, 6) NOT NULL,
        Informational INT NOT NULL,
        Informational_Duration DECIMAL(14, 6) NOT NULL,
        ProductRelated INT NOT NULL,
        ProductRelated_Duration DECIMAL(14, 6) NOT NULL,
        BounceRates NVARCHAR(32) NOT NULL,
        ExitRates DECIMAL(12, 8) NOT NULL,
        PageValues DECIMAL(14, 6) NOT NULL,
        SpecialDay DECIMAL(8, 6) NOT NULL,
        [Month] NVARCHAR(3) NOT NULL,
        OperatingSystems INT NOT NULL,
        Browser INT NOT NULL,
        Region INT NOT NULL,
        TrafficType INT NOT NULL,
        VisitorType NVARCHAR(30) NOT NULL,
        Weekend NVARCHAR(5) NOT NULL,
        Revenue NVARCHAR(5) NOT NULL
    );
END;
GO

-- El CSV contiene True/False como texto; conservarlos asi en staging.
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.StgSesiones') AND name = N'BounceRates' AND system_type_id <> TYPE_ID(N'nvarchar'))
    ALTER TABLE dbo.StgSesiones ALTER COLUMN BounceRates NVARCHAR(32) NOT NULL;
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.StgSesiones') AND name = N'Weekend' AND system_type_id <> TYPE_ID(N'nvarchar'))
    ALTER TABLE dbo.StgSesiones ALTER COLUMN Weekend NVARCHAR(5) NOT NULL;
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.StgSesiones') AND name = N'Revenue' AND system_type_id <> TYPE_ID(N'nvarchar'))
    ALTER TABLE dbo.StgSesiones ALTER COLUMN Revenue NVARCHAR(5) NOT NULL;
GO

IF OBJECT_ID(N'dbo.DimMes', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimMes (
        MesKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimMes PRIMARY KEY,
        Mes NVARCHAR(3) NOT NULL CONSTRAINT UQ_DimMes_Mes UNIQUE
    );
END;
GO

IF OBJECT_ID(N'dbo.DimTipoVisitante', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimTipoVisitante (
        TipoVisitanteKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimTipoVisitante PRIMARY KEY,
        TipoVisitante NVARCHAR(30) NOT NULL CONSTRAINT UQ_DimTipoVisitante UNIQUE
    );
END;
GO

IF OBJECT_ID(N'dbo.DimSistemaOperativo', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimSistemaOperativo (
        SistemaOperativoKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimSistemaOperativo PRIMARY KEY,
        CodigoSistemaOperativo INT NOT NULL CONSTRAINT UQ_DimSistemaOperativo UNIQUE
    );
END;
GO

IF OBJECT_ID(N'dbo.DimNavegador', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimNavegador (
        NavegadorKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimNavegador PRIMARY KEY,
        CodigoNavegador INT NOT NULL CONSTRAINT UQ_DimNavegador UNIQUE
    );
END;
GO

IF OBJECT_ID(N'dbo.DimRegion', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimRegion (
        RegionKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimRegion PRIMARY KEY,
        CodigoRegion INT NOT NULL CONSTRAINT UQ_DimRegion UNIQUE
    );
END;
GO

IF OBJECT_ID(N'dbo.DimTipoTrafico', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimTipoTrafico (
        TipoTraficoKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimTipoTrafico PRIMARY KEY,
        CodigoTipoTrafico INT NOT NULL CONSTRAINT UQ_DimTipoTrafico UNIQUE
    );
END;
GO

IF OBJECT_ID(N'dbo.FactSesion', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.FactSesion (
        SesionKey BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_FactSesion PRIMARY KEY,
        MesKey INT NOT NULL,
        TipoVisitanteKey INT NOT NULL,
        SistemaOperativoKey INT NOT NULL,
        NavegadorKey INT NOT NULL,
        RegionKey INT NOT NULL,
        TipoTraficoKey INT NOT NULL,
        Administrative INT NOT NULL,
        Administrative_Duration DECIMAL(14, 6) NOT NULL,
        Informational INT NOT NULL,
        Informational_Duration DECIMAL(14, 6) NOT NULL,
        ProductRelated INT NOT NULL,
        ProductRelated_Duration DECIMAL(14, 6) NOT NULL,
        BounceRates DECIMAL(12, 8) NOT NULL,
        ExitRates DECIMAL(12, 8) NOT NULL,
        PageValues DECIMAL(14, 6) NOT NULL,
        SpecialDay DECIMAL(8, 6) NOT NULL,
        Weekend BIT NOT NULL,
        Revenue BIT NOT NULL,
        CONSTRAINT FK_FactSesion_DimMes FOREIGN KEY (MesKey) REFERENCES dbo.DimMes(MesKey),
        CONSTRAINT FK_FactSesion_DimTipoVisitante FOREIGN KEY (TipoVisitanteKey) REFERENCES dbo.DimTipoVisitante(TipoVisitanteKey),
        CONSTRAINT FK_FactSesion_DimSistemaOperativo FOREIGN KEY (SistemaOperativoKey) REFERENCES dbo.DimSistemaOperativo(SistemaOperativoKey),
        CONSTRAINT FK_FactSesion_DimNavegador FOREIGN KEY (NavegadorKey) REFERENCES dbo.DimNavegador(NavegadorKey),
        CONSTRAINT FK_FactSesion_DimRegion FOREIGN KEY (RegionKey) REFERENCES dbo.DimRegion(RegionKey),
        CONSTRAINT FK_FactSesion_DimTipoTrafico FOREIGN KEY (TipoTraficoKey) REFERENCES dbo.DimTipoTrafico(TipoTraficoKey)
    );
END;
GO

SELECT DB_NAME() AS BaseDeDatosCreada;
SELECT name AS Tabla
FROM sys.tables
WHERE schema_id = SCHEMA_ID(N'dbo')
ORDER BY name;
GO

