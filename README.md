# Análisis del comportamiento de compradores en comercio electrónico

## Descripción
Este proyecto analiza el comportamiento de los visitantes de un sitio de comercio electrónico para identificar características relacionadas con las compras.

## Objetivo
Explorar los datos de las visitas, encontrar patrones y preparar información que permita aplicar modelos para estudiar o predecir si una sesión termina en una compra.

## Conjunto de datos
Se utiliza el **Online Shoppers Purchasing Intention Dataset**, obtenido del repositorio UCI Machine Learning Repository.

El conjunto contiene 12,330 registros y 18 variables relacionadas con las páginas visitadas, el tiempo de navegación, el tipo de visitante y si se realizó una compra.

El archivo original se conserva en `data/raw/online_shoppers_intention.csv`.

## Herramientas utilizadas
- Python
- Jupyter Notebook
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Git y GitHub

Otras herramientas, como Scikit-learn, SQL Server y Power BI, se consideran para las siguientes etapas del proyecto.

## Estructura del proyecto
- `data/raw`: conjunto de datos original.
- `data/processed`: espacio para guardar los datos después de su preparación.
- `notebooks`: notebooks utilizados para la revisión y exploración.
- `src`: módulos de código Python que se desarrollarán para organizar el proceso.
- `sql`: consultas y objetos de base de datos.
- `modelos`: modelos que se generarán durante el proyecto.
- `dashboard`: tablero para presentar los resultados.
- `docs`: documentos y evidencias del proyecto.

## Avance actual
Se cuenta con el conjunto de datos original y se realizó una primera exploración en Jupyter Notebook. En esta revisión se analizaron las dimensiones, los tipos de datos, los valores faltantes, los registros duplicados, algunas estadísticas descriptivas, los valores atípicos y las primeras gráficas.

## Siguientes etapas
1. Organizar el código de exploración en módulos dentro de `src`.
2. Revisar y preparar los datos, conservando el archivo original.
3. Diseñar el proceso de transformación y almacenamiento.
4. Aplicar modelos de análisis y aprendizaje automático.
5. Elaborar el dashboard y documentar los resultados.
