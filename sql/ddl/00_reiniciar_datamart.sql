/*
================================================================================
Script: 00_reiniciar_datamart.sql
Proyecto: Análisis del comportamiento de compradores en comercio electrónico
Motor: Microsoft SQL Server / SQL Server LocalDB
Propósito: Eliminar y reconstruir las tablas del Data Mart (esquema estrella)
         sin borrar la base de datos completa.
================================================================================

QUÉ HACE ESTE SCRIPT
--------------------
1. Cambia al contexto de la base de datos ECBD_Compradores.
2. Elimina las 8 tablas del Data Mart en el orden correcto para respetar
   las claves foráneas (primero la tabla de hechos, luego las dimensiones,
   por último la tabla de staging).
3. Vuelve a crear las 8 tablas con exactamente la misma definición que
   el script original 01_crear_base_y_datamart.sql.
4. Es idempotente: se puede ejecutar cuantas veces se quiera sin errores
   por "tabla inexistente" ni por "tabla ya existe".

POR QUÉ ES NECESARIO
--------------------
- Durante el desarrollo del ETL en SSIS es frecuente necesitar vaciar y
  recrear las tablas para probar cargas limpias.
- Permite restablecer el Data Mart a un estado conocido sin tener que
  borrar y recrear la base de datos completa (lo que ahorra tiempo y
  evita problemas de permisos).
- Sirve como "reset" antes de cada ejecución de prueba del paquete SSIS.

CÓMO EJECUTARLO DESDE SQL SERVER MANAGEMENT STUDIO (SSMS)
----------------------------------------------------------
1. Abrir SSMS y conectarse a la instancia (LocalDB o servidor).
2. Archivo > Abrir > Archivo... > seleccionar este script
   (sql/ddl/00_reiniciar_datamart.sql).
3. Pulsar F5 o el botón "Ejecutar".
4. Verificar en la pestaña "Mensajes" que no hay errores y que al final
   aparecen las 8 tablas listadas.

NOTAS IMPORTANTES
-----------------
- NO elimina la base de datos ECBD_Compradores.
- NO toca los datos de data/raw/ ni data/processed/.
- Respeta exactamente el diseño actual: nombres, tipos, PK, FK, UNIQUE,
  IDENTITY y NOT NULL tal como están en 01_crear_base_y_datamart.sql.
- El orden de DROP es: FactSesion → 6 dimensiones → StgSesiones.
- El orden de CREATE es: StgSesiones → 6 dimensiones → FactSesion.
================================================================================
*/

-- 1. Contexto: usar la base de datos del Data Mart
USE ECBD_Compradores;
GO

-- =============================================================================
-- 2. ELIMINACIÓN DE TABLAS (orden inverso a las dependencias FK)
-- =============================================================================
-- FactSesion tiene 6 FK hacia las dimensiones → se elimina PRIMERA
IF OBJECT_ID(N'dbo.FactSesion', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.FactSesion;
    PRINT 'Tabla eliminada: dbo.FactSesion';
END;
GO

-- Las 6 dimensiones no tienen FK entre sí → orden indiferente
IF OBJECT_ID(N'dbo.DimMes', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.DimMes;
    PRINT 'Tabla eliminada: dbo.DimMes';
END;
GO

IF OBJECT_ID(N'dbo.DimTipoVisitante', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.DimTipoVisitante;
    PRINT 'Tabla eliminada: dbo.DimTipoVisitante';
END;
GO

IF OBJECT_ID(N'dbo.DimSistemaOperativo', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.DimSistemaOperativo;
    PRINT 'Tabla eliminada: dbo.DimSistemaOperativo';
END;
GO

IF OBJECT_ID(N'dbo.DimNavegador', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.DimNavegador;
    PRINT 'Tabla eliminada: dbo.DimNavegador';
END;
GO

IF OBJECT_ID(N'dbo.DimRegion', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.DimRegion;
    PRINT 'Tabla eliminada: dbo.DimRegion';
END;
GO

IF OBJECT_ID(N'dbo.DimTipoTrafico', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.DimTipoTrafico;
    PRINT 'Tabla eliminada: dbo.DimTipoTrafico';
END;
GO

-- StgSesiones no tiene FK → se elimina al final (o al principio, da igual)
IF OBJECT_ID(N'dbo.StgSesiones', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.StgSesiones;
    PRINT 'Tabla eliminada: dbo.StgSesiones';
END;
GO

PRINT '--- Todas las tablas del Data Mart eliminadas ---';
GO

-- =============================================================================
-- 3. RECREACIÓN DE TABLAS (orden respetando dependencias FK)
-- =============================================================================

-- 3.1 Tabla de staging: recibe el CSV tal cual, sin PK ni FK
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
PRINT 'Tabla creada: dbo.StgSesiones';
GO

-- Asegurar tipos correctos en staging (el CSV trae texto para algunos campos)
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.StgSesiones') AND name = N'BounceRates' AND system_type_id <> TYPE_ID(N'nvarchar'))
    ALTER TABLE dbo.StgSesiones ALTER COLUMN BounceRates NVARCHAR(32) NOT NULL;
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.StgSesiones') AND name = N'Weekend' AND system_type_id <> TYPE_ID(N'nvarchar'))
    ALTER TABLE dbo.StgSesiones ALTER COLUMN Weekend NVARCHAR(5) NOT NULL;
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.StgSesiones') AND name = N'Revenue' AND system_type_id <> TYPE_ID(N'nvarchar'))
    ALTER TABLE dbo.StgSesiones ALTER COLUMN Revenue NVARCHAR(5) NOT NULL;
GO

-- 3.2 Seis dimensiones: cada una con PK sustituta (IDENTITY) y UNIQUE en atributo natural
CREATE TABLE dbo.DimMes (
    MesKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimMes PRIMARY KEY,
    Mes NVARCHAR(3) NOT NULL CONSTRAINT UQ_DimMes_Mes UNIQUE
);
PRINT 'Tabla creada: dbo.DimMes';
GO

CREATE TABLE dbo.DimTipoVisitante (
    TipoVisitanteKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimTipoVisitante PRIMARY KEY,
    TipoVisitante NVARCHAR(30) NOT NULL CONSTRAINT UQ_DimTipoVisitante UNIQUE
);
PRINT 'Tabla creada: dbo.DimTipoVisitante';
GO

CREATE TABLE dbo.DimSistemaOperativo (
    SistemaOperativoKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimSistemaOperativo PRIMARY KEY,
    CodigoSistemaOperativo INT NOT NULL CONSTRAINT UQ_DimSistemaOperativo UNIQUE
);
PRINT 'Tabla creada: dbo.DimSistemaOperativo';
GO

CREATE TABLE dbo.DimNavegador (
    NavegadorKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimNavegador PRIMARY KEY,
    CodigoNavegador INT NOT NULL CONSTRAINT UQ_DimNavegador UNIQUE
);
PRINT 'Tabla creada: dbo.DimNavegador';
GO

CREATE TABLE dbo.DimRegion (
    RegionKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimRegion PRIMARY KEY,
    CodigoRegion INT NOT NULL CONSTRAINT UQ_DimRegion UNIQUE
);
PRINT 'Tabla creada: dbo.DimRegion';
GO

CREATE TABLE dbo.DimTipoTrafico (
    TipoTraficoKey INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimTipoTrafico PRIMARY KEY,
    CodigoTipoTrafico INT NOT NULL CONSTRAINT UQ_DimTipoTrafico UNIQUE
);
PRINT 'Tabla creada: dbo.DimTipoTrafico';
GO

-- 3.3 Tabla de hechos: PK sustituta + 6 FK hacia las dimensiones
CREATE TABLE dbo.FactSesion (
    SesionKey BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_FactSesion PRIMARY KEY,
    -- Llaves foráneas (6 dimensiones)
    MesKey INT NOT NULL,
    TipoVisitanteKey INT NOT NULL,
    SistemaOperativoKey INT NOT NULL,
    NavegadorKey INT NOT NULL,
    RegionKey INT NOT NULL,
    TipoTraficoKey INT NOT NULL,
    -- Medidas de navegación
    Administrative INT NOT NULL,
    Administrative_Duration DECIMAL(14, 6) NOT NULL,
    Informational INT NOT NULL,
    Informational_Duration DECIMAL(14, 6) NOT NULL,
    ProductRelated INT NOT NULL,
    ProductRelated_Duration DECIMAL(14, 6) NOT NULL,
    -- Tasas y valor
    BounceRates DECIMAL(12, 8) NOT NULL,
    ExitRates DECIMAL(12, 8) NOT NULL,
    PageValues DECIMAL(14, 6) NOT NULL,
    -- Indicadores
    SpecialDay DECIMAL(8, 6) NOT NULL,
    Weekend BIT NOT NULL,      -- 1 = fin de semana, 0 = entre semana
    Revenue BIT NOT NULL,      -- 1 = compra, 0 = no compra
    -- Restricciones de integridad referencial
    CONSTRAINT FK_FactSesion_DimMes FOREIGN KEY (MesKey) REFERENCES dbo.DimMes(MesKey),
    CONSTRAINT FK_FactSesion_DimTipoVisitante FOREIGN KEY (TipoVisitanteKey) REFERENCES dbo.DimTipoVisitante(TipoVisitanteKey),
    CONSTRAINT FK_FactSesion_DimSistemaOperativo FOREIGN KEY (SistemaOperativoKey) REFERENCES dbo.DimSistemaOperativo(SistemaOperativoKey),
    CONSTRAINT FK_FactSesion_DimNavegador FOREIGN KEY (NavegadorKey) REFERENCES dbo.DimNavegador(NavegadorKey),
    CONSTRAINT FK_FactSesion_DimRegion FOREIGN KEY (RegionKey) REFERENCES dbo.DimRegion(RegionKey),
    CONSTRAINT FK_FactSesion_DimTipoTrafico FOREIGN KEY (TipoTraficoKey) REFERENCES dbo.DimTipoTrafico(TipoTraficoKey)
);
PRINT 'Tabla creada: dbo.FactSesion';
GO

-- =============================================================================
-- 4. VALIDACIÓN FINAL: listar tablas creadas
-- =============================================================================
SELECT DB_NAME() AS BaseDeDatosActual;
SELECT name AS Tabla
FROM sys.tables
WHERE schema_id = SCHEMA_ID(N'dbo')
ORDER BY name;
GO

PRINT '--- Data Mart reiniciado correctamente ---';