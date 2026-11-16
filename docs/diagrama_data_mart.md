# Diagrama del Data Mart

## Grano

Una fila de `FactSesion` representa una sesión del dataset procesado. La llave sustituta `SesionKey` se genera en la base y no existe en el CSV original.

## Esquema estrella

```mermaid
erDiagram
    DimMes ||--o{ FactSesion : clasifica
    DimTipoVisitante ||--o{ FactSesion : clasifica
    DimSistemaOperativo ||--o{ FactSesion : clasifica
    DimNavegador ||--o{ FactSesion : clasifica
    DimRegion ||--o{ FactSesion : clasifica
    DimTipoTrafico ||--o{ FactSesion : clasifica

    DimMes {
        int MesKey PK
        string Mes UK
    }
    DimTipoVisitante {
        int TipoVisitanteKey PK
        string TipoVisitante UK
    }
    DimSistemaOperativo {
        int SistemaOperativoKey PK
        int CodigoSistemaOperativo UK
    }
    DimNavegador {
        int NavegadorKey PK
        int CodigoNavegador UK
    }
    DimRegion {
        int RegionKey PK
        int CodigoRegion UK
    }
    DimTipoTrafico {
        int TipoTraficoKey PK
        int CodigoTipoTrafico UK
    }
    FactSesion {
        bigint SesionKey PK
        int MesKey FK
        int TipoVisitanteKey FK
        int SistemaOperativoKey FK
        int NavegadorKey FK
        int RegionKey FK
        int TipoTraficoKey FK
        int Administrative
        decimal Administrative_Duration
        int Informational
        decimal Informational_Duration
        int ProductRelated
        decimal ProductRelated_Duration
        decimal BounceRates
        decimal ExitRates
        decimal PageValues
        decimal SpecialDay
        bit Weekend
        bit Revenue
    }
```

`StgSesiones` recibe las 18 columnas del CSV antes de poblar el esquema estrella. `FactSesion` conserva las medidas de navegación y los indicadores de fin de semana y compra.

## Implementación

- Creación de base y tablas: `sql/01_crear_base_y_datamart.sql`.
- Carga CSV, dimensiones y hechos: `sql/02_cargar_dataset.sql`.
- Dataset fuente de la carga: `data/processed/online_shoppers_intention_clean.csv`.
