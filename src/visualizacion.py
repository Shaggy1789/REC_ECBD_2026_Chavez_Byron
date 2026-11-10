"""Gráficas iniciales para el análisis exploratorio."""
import matplotlib.pyplot as plt
import seaborn as sns


def grafica_tipo_visitante(datos):
    """Grafica la cantidad de sesiones por tipo de visitante."""
    plt.figure(figsize=(8, 5))
    sns.countplot(data=datos, x="VisitorType")
    plt.title("Sesiones por tipo de visitante")
    plt.xlabel("Tipo de visitante")
    plt.ylabel("Cantidad de sesiones")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()


def grafica_compras(datos):
    """Grafica las sesiones que terminaron o no en compra."""
    plt.figure(figsize=(6, 4))
    sns.countplot(data=datos, x="Revenue")
    plt.title("Sesiones que terminaron en compra")
    plt.xlabel("¿Se realizó una compra?")
    plt.ylabel("Cantidad de sesiones")
    plt.tight_layout()
    plt.show()


def histograma_duracion_productos(datos):
    """Muestra la distribución del tiempo en páginas de productos."""
    plt.figure(figsize=(8, 5))
    sns.histplot(data=datos, x="ProductRelated_Duration", bins=30)
    plt.title("Tiempo de navegación en páginas de productos")
    plt.xlabel("Duración (segundos)")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.show()
