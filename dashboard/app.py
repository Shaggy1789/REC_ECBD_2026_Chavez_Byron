"""Dashboard local del análisis de compradores ecommerce."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_CSV = ROOT / "data" / "processed" / "clean" / "online_shoppers_intention_clean.csv"
CLUSTER_CSV = ROOT / "data" / "processed" / "clustering" / "sesiones_clusterizadas.csv"
CLASS_METRICS = ROOT / "modelos" / "metricas" / "metricas_clasificacion.csv"
REG_METRICS = ROOT / "modelos" / "metricas" / "metricas_regresion.csv"

st.set_page_config(
    page_title="Compradores ecommerce",
    page_icon="🛍️",
    layout="wide",
)


@st.cache_data

def cargar_datos():
    """Carga el archivo segmentado si existe; si no, usa el procesado."""
    ruta = CLUSTER_CSV if CLUSTER_CSV.exists() else PROCESSED_CSV
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el dataset: {ruta}")
    datos = pd.read_csv(ruta)
    datos["Revenue"] = datos["Revenue"].astype(bool)
    datos["Weekend"] = datos["Weekend"].astype(bool)
    return datos


def cargar_metricas(ruta):
    if ruta.exists():
        return pd.read_csv(ruta)
    return pd.DataFrame()


datos = cargar_datos()

st.title("Análisis del comportamiento de compradores")
st.caption(
    "Online Shoppers Purchasing Intention Dataset · "
    "12,205 sesiones procesadas · indicadores descriptivos, modelos y segmentos"
)

with st.sidebar:
    st.header("Filtros")
    meses_disponibles = sorted(datos["Month"].dropna().unique().tolist())
    meses = st.multiselect("Mes", meses_disponibles, default=meses_disponibles)
    visitantes_disponibles = sorted(datos["VisitorType"].dropna().unique().tolist())
    visitantes = st.multiselect(
        "Tipo de visitante", visitantes_disponibles, default=visitantes_disponibles
    )
    compra = st.selectbox(
        "Resultado de la sesión",
        ["Todas", "Terminó en compra", "No terminó en compra"],
    )
    fin_semana = st.selectbox(
        "Día de visita", ["Todos", "Fin de semana", "Entre semana"]
    )

filtrado = datos[
    datos["Month"].isin(meses) & datos["VisitorType"].isin(visitantes)
].copy()
if compra == "Terminó en compra":
    filtrado = filtrado[filtrado["Revenue"]]
elif compra == "No terminó en compra":
    filtrado = filtrado[~filtrado["Revenue"]]
if fin_semana == "Fin de semana":
    filtrado = filtrado[filtrado["Weekend"]]
elif fin_semana == "Entre semana":
    filtrado = filtrado[~filtrado["Weekend"]]

if filtrado.empty:
    st.warning("No hay sesiones para la combinación de filtros seleccionada.")
    st.stop()

sesiones = len(filtrado)
compras = int(filtrado["Revenue"].sum())
tasa_conversion = compras / sesiones
promedio_duracion = filtrado["ProductRelated_Duration"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Sesiones", f"{sesiones:,}")
k2.metric("Sesiones con compra", f"{compras:,}")
k3.metric("Tasa de compra", f"{tasa_conversion:.1%}")
k4.metric("Duración media en páginas de producto", f"{promedio_duracion:,.0f} s")

st.divider()
left, right = st.columns(2)

with left:
    orden_meses = ["Feb", "Mar", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    por_mes = (
        filtrado.groupby("Month", as_index=False)
        .agg(Sesiones=("Revenue", "size"), Compras=("Revenue", "sum"))
    )
    por_mes["Tasa de compra"] = por_mes["Compras"] / por_mes["Sesiones"]
    por_mes["Month"] = pd.Categorical(por_mes["Month"], categories=orden_meses, ordered=True)
    por_mes = por_mes.sort_values("Month")
    fig_mes = px.bar(
        por_mes, x="Month", y="Sesiones", color="Tasa de compra",
        color_continuous_scale="Blues", title="Sesiones por mes y tasa de compra",
        hover_data={"Compras": True, "Tasa de compra": ":.1%"},
    )
    st.plotly_chart(fig_mes, use_container_width=True)

with right:
    por_visitante = (
        filtrado.groupby("VisitorType", as_index=False)
        .agg(Sesiones=("Revenue", "size"), Compras=("Revenue", "sum"))
    )
    por_visitante["Tasa de compra"] = por_visitante["Compras"] / por_visitante["Sesiones"]
    fig_visitante = px.bar(
        por_visitante, x="VisitorType", y="Tasa de compra",
        color="VisitorType", text=por_visitante["Tasa de compra"].map(lambda x: f"{x:.1%}"),
        title="Tasa de compra por tipo de visitante",
        hover_data={"Sesiones": True, "Compras": True, "Tasa de compra": ":.1%"},
    )
    fig_visitante.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_visitante, use_container_width=True)

left, right = st.columns(2)
with left:
    limite = filtrado["ProductRelated_Duration"].quantile(0.99)
    hist = filtrado[filtrado["ProductRelated_Duration"] <= limite]
    fig_duracion = px.histogram(
        hist, x="ProductRelated_Duration", color="Revenue", nbins=35,
        barmode="overlay", opacity=0.7,
        labels={"ProductRelated_Duration": "Duración (segundos)", "Revenue": "Compra"},
        title="Duración en páginas de productos (hasta percentil 99)",
    )
    st.plotly_chart(fig_duracion, use_container_width=True)
    st.caption("La gráfica limita el eje al percentil 99; las sesiones extremas siguen en los datos.")

with right:
    if "Cluster" in filtrado.columns:
        por_cluster = (
            filtrado.groupby("Cluster", as_index=False)
            .agg(Sesiones=("Revenue", "size"), Compras=("Revenue", "sum"))
        )
        por_cluster["Tasa de compra"] = por_cluster["Compras"] / por_cluster["Sesiones"]
        fig_cluster = px.bar(
            por_cluster, x="Cluster", y="Tasa de compra", color="Cluster",
            text=por_cluster["Tasa de compra"].map(lambda x: f"{x:.1%}"),
            title="Tasa de compra por cluster",
            hover_data={"Sesiones": True, "Compras": True, "Tasa de compra": ":.1%"},
        )
        fig_cluster.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_cluster, use_container_width=True)
    else:
        st.info("Ejecuta `notebooks/unidad_iv_no_supervisado/04_clustering_pca.ipynb` para agregar el análisis por cluster.")

st.subheader("Resultados de modelos supervisados")
reg, clas = st.columns(2)
with reg:
    st.markdown("**Regresión: duración en páginas de producto**")
    metricas_reg = cargar_metricas(REG_METRICS)
    if not metricas_reg.empty:
        st.dataframe(metricas_reg.round(3), hide_index=True, use_container_width=True)
    else:
        st.info("Ejecuta `notebooks/unidad_iii_supervisado/03_modelos_supervisados.ipynb` para generar métricas.")
with clas:
    st.markdown("**Clasificación: resultado de compra**")
    metricas_clas = cargar_metricas(CLASS_METRICS)
    if not metricas_clas.empty:
        st.dataframe(metricas_clas.round(3), hide_index=True, use_container_width=True)
    else:
        st.info("Ejecuta `notebooks/unidad_iii_supervisado/03_modelos_supervisados.ipynb` para generar métricas.")

st.caption(
    "Las tasas describen asociaciones en las sesiones seleccionadas; no demuestran que una variable cause la compra. "
    "La clasificación se evalúa en una partición de prueba y no representa rendimiento garantizado en otros datos."
)

