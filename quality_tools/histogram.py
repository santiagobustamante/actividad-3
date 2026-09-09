"""
Histograma: muestra la distribucion de frecuencias de una variable
numerica y ayuda a identificar su forma (normal, sesgada, bimodal, etc.).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats


class Histograma:
    """Analiza y grafica la distribucion de una variable numerica."""

    def __init__(self, df: pd.DataFrame, columna: str = "tiempo_retraso_horas"):
        self.df = df
        self.columna = columna
        self.datos = None
        self.estadisticas = None

    def analizar(self) -> dict:
        """
        Calcula estadisticos descriptivos (media, mediana, desviacion,
        asimetria, curtosis) y una prueba de normalidad (Shapiro-Wilk).
        """
        serie = self.df[self.columna]
        self.datos = serie[serie > 0].dropna()

        asimetria = stats.skew(self.datos)
        curtosis = stats.kurtosis(self.datos)
        # Shapiro-Wilk funciona bien hasta ~5000 datos; si hay mas, se
        # toma una muestra aleatoria para no romper la prueba.
        muestra = self.datos.sample(min(len(self.datos), 5000), random_state=42)
        estadistico_sw, valor_p = stats.shapiro(muestra)

        self.estadisticas = {
            "n": len(self.datos),
            "media": self.datos.mean(),
            "mediana": self.datos.median(),
            "desviacion_estandar": self.datos.std(),
            "minimo": self.datos.min(),
            "maximo": self.datos.max(),
            "asimetria": asimetria,
            "curtosis": curtosis,
            "shapiro_estadistico": estadistico_sw,
            "shapiro_valor_p": valor_p,
            "es_normal": valor_p > 0.05,
        }
        return self.estadisticas

    def graficar(self, ruta_salida: str,
                 titulo: str = "Histograma - Tiempo de retraso (horas)") -> str:
        if self.estadisticas is None:
            self.analizar()

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.hist(self.datos, bins="auto", color="#2980b9", edgecolor="white", alpha=0.85)

        ax.axvline(self.estadisticas["media"], color="#c0392b", linestyle="--",
                   linewidth=2, label=f"Media = {self.estadisticas['media']:.2f}")
        ax.axvline(self.estadisticas["mediana"], color="#27ae60", linestyle="--",
                   linewidth=2, label=f"Mediana = {self.estadisticas['mediana']:.2f}")

        ax.set_xlabel(self.columna)
        ax.set_ylabel("Frecuencia")
        ax.legend()
        plt.title(titulo)
        fig.tight_layout()

        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_salida, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return ruta_salida

    def interpretar(self) -> str:
        if self.estadisticas is None:
            self.analizar()
        e = self.estadisticas

        if abs(e["asimetria"]) < 0.5:
            forma = "aproximadamente simetrica"
        elif e["asimetria"] > 0:
            forma = "sesgada a la derecha (cola hacia valores altos)"
        else:
            forma = "sesgada a la izquierda (cola hacia valores bajos)"

        normalidad = (
            "no se puede rechazar la normalidad (p > 0.05); los datos "
            "son compatibles con una distribucion normal."
            if e["es_normal"] else
            "se rechaza la normalidad (p <= 0.05); los datos NO siguen "
            "una distribucion normal."
        )

        texto = (
            "HISTOGRAMA\n"
            f"{'-' * 50}\n"
            f"Variable analizada: {self.columna} (n = {e['n']})\n"
            f"Media = {e['media']:.2f} | Mediana = {e['mediana']:.2f} | "
            f"Desv. estandar = {e['desviacion_estandar']:.2f}\n"
            f"Rango: [{e['minimo']:.2f}, {e['maximo']:.2f}]\n"
            f"La distribucion es {forma} (asimetria = {e['asimetria']:.2f}).\n"
            "Prueba de normalidad (Shapiro-Wilk): estadistico = "
            f"{e['shapiro_estadistico']:.3f}, p-valor = {e['shapiro_valor_p']:.4f} "
            f"-> {normalidad}\n"
        )
        return texto
