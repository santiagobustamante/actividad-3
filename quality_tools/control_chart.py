"""
Grafico de control: monitorea una variable en el tiempo, calculando la
linea central y los limites de control (superior e inferior) a 3
desviaciones estandar, y marca los puntos que caen fuera de control.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class GraficoControl:
    """Construye un grafico de control tipo X (promedios) con limites a 3 sigma."""

    def __init__(self, serie: pd.DataFrame, columna_valor: str = "valor_promedio",
                 columna_tiempo: str = "fecha"):
        self.serie = serie.reset_index(drop=True)
        self.columna_valor = columna_valor
        self.columna_tiempo = columna_tiempo
        self.estadisticas = None

    def analizar(self) -> dict:
        """
        Calcula la linea central (promedio general), los limites de
        control a 3 sigma y detecta los puntos fuera de esos limites.
        """
        valores = self.serie[self.columna_valor]
        linea_central = valores.mean()
        sigma = valores.std()
        lcs = linea_central + 3 * sigma
        lci = max(linea_central - 3 * sigma, 0)

        fuera_de_control = self.serie[(valores > lcs) | (valores < lci)]

        self.estadisticas = {
            "linea_central": linea_central,
            "sigma": sigma,
            "lcs": lcs,
            "lci": lci,
            "n_puntos": len(valores),
            "puntos_fuera_de_control": fuera_de_control,
        }
        return self.estadisticas

    def graficar(self, ruta_salida: str,
                 titulo: str = "Grafico de control - Tiempo promedio de retraso diario") -> str:
        if self.estadisticas is None:
            self.analizar()

        e = self.estadisticas
        valores = self.serie[self.columna_valor]
        eje_x = range(len(valores))

        fig, ax = plt.subplots(figsize=(11, 6))
        ax.plot(eje_x, valores, marker="o", color="#2980b9", linewidth=1.5, label="Valor observado")
        ax.axhline(e["linea_central"], color="#27ae60", linestyle="-", label="Linea central")
        ax.axhline(e["lcs"], color="#c0392b", linestyle="--", label="LCS (3 sigma)")
        ax.axhline(e["lci"], color="#c0392b", linestyle="--", label="LCI (3 sigma)")

        fuera = e["puntos_fuera_de_control"]
        if not fuera.empty:
            ax.scatter(fuera.index, fuera[self.columna_valor], color="red", s=100,
                       zorder=5, label="Fuera de control")

        ax.set_xlabel("Periodo (dia)")
        ax.set_ylabel(self.columna_valor)
        ax.legend(loc="upper right")
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
        n_fuera = len(e["puntos_fuera_de_control"])

        texto = (
            "GRAFICO DE CONTROL\n"
            f"{'-' * 50}\n"
            f"Periodos analizados: {e['n_puntos']}\n"
            f"Linea central = {e['linea_central']:.2f} | "
            f"LCS = {e['lcs']:.2f} | LCI = {e['lci']:.2f}\n"
        )
        if n_fuera == 0:
            texto += (
                "No se detectaron puntos fuera de los limites de control: "
                "el proceso se comporta de manera estable y predecible "
                "(bajo control estadistico).\n"
            )
        else:
            fechas_fuera = e["puntos_fuera_de_control"][self.columna_tiempo].tolist()
            texto += (
                f"Se detectaron {n_fuera} punto(s) fuera de los limites de "
                f"control en: {fechas_fuera}.\n"
                "Esto indica causas especiales (no aleatorias) que deben "
                "investigarse puntualmente, en lugar de tratarse como "
                "variacion normal del proceso.\n"
            )
        return texto
