"""
Diagrama de dispersion: evalua si existe relacion (correlacion) entre
dos variables numericas, por ejemplo distancia del envio y tiempo de
retraso.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


class DiagramaDispersion:
    """Analiza y grafica la correlacion entre dos variables numericas."""

    def __init__(self, df: pd.DataFrame, columna_x: str = "distancia_km",
                 columna_y: str = "tiempo_retraso_horas"):
        self.df = df
        self.columna_x = columna_x
        self.columna_y = columna_y
        self.datos = None
        self.estadisticas = None

    def analizar(self) -> dict:
        datos = self.df[[self.columna_x, self.columna_y]].dropna()
        datos = datos[datos[self.columna_y] > 0]
        self.datos = datos

        coef_pearson, valor_p = stats.pearsonr(datos[self.columna_x], datos[self.columna_y])
        pendiente, intercepto = np.polyfit(datos[self.columna_x], datos[self.columna_y], 1)

        self.estadisticas = {
            "n": len(datos),
            "coeficiente_pearson": coef_pearson,
            "valor_p": valor_p,
            "pendiente": pendiente,
            "intercepto": intercepto,
        }
        return self.estadisticas

    def graficar(self, ruta_salida: str,
                 titulo: str = "Dispersion - Distancia vs Tiempo de retraso") -> str:
        if self.estadisticas is None:
            self.analizar()

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.scatter(self.datos[self.columna_x], self.datos[self.columna_y],
                   alpha=0.5, color="#8e44ad", edgecolor="white", s=40)

        x_linea = np.linspace(self.datos[self.columna_x].min(), self.datos[self.columna_x].max(), 100)
        y_linea = self.estadisticas["pendiente"] * x_linea + self.estadisticas["intercepto"]
        ax.plot(x_linea, y_linea, color="#c0392b", linewidth=2,
                label=f"r = {self.estadisticas['coeficiente_pearson']:.2f}")

        ax.set_xlabel(self.columna_x)
        ax.set_ylabel(self.columna_y)
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
        r = e["coeficiente_pearson"]

        r_abs = abs(r)
        if r_abs < 0.3:
            fuerza = "debil o nula"
        elif r_abs < 0.7:
            fuerza = "moderada"
        else:
            fuerza = "fuerte"
        direccion = "positiva" if r > 0 else "negativa"

        significancia = (
            "estadisticamente significativa (p < 0.05)" if e["valor_p"] < 0.05
            else "no estadisticamente significativa (p >= 0.05)"
        )

        texto = (
            "DIAGRAMA DE DISPERSION\n"
            f"{'-' * 50}\n"
            f"Variables: {self.columna_x} (X) vs {self.columna_y} (Y), n = {e['n']}\n"
            f"Coeficiente de correlacion de Pearson: r = {r:.3f} ({significancia})\n"
            f"Se observa una correlacion {fuerza} y {direccion} entre las dos variables.\n"
        )
        if r_abs >= 0.3:
            texto += (
                f"Esto sugiere que a mayor {self.columna_x}, "
                f"{'mayor' if r > 0 else 'menor'} tiende a ser {self.columna_y}, "
                "por lo que esta variable deberia considerarse en el analisis "
                "de causas del problema.\n"
            )
        return texto
