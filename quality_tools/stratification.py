"""
Estratificacion: separa los datos en subgrupos (por ejemplo region o
transportador) para revisar si el problema se concentra en algun
segmento particular, algo que un analisis global puede esconder.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class Estratificacion:
    """Segmenta una variable numerica segun una variable categorica (estrato)."""

    def __init__(self, df: pd.DataFrame, columna_valor: str = "tiempo_retraso_horas",
                 columna_estrato: str = "region"):
        self.df = df
        self.columna_valor = columna_valor
        self.columna_estrato = columna_estrato
        self.resumen = None

    def analizar(self) -> pd.DataFrame:
        datos = self.df
        if self.columna_valor == "tiempo_retraso_horas":
            datos = datos[datos[self.columna_valor] > 0]
        resumen = (
            datos.groupby(self.columna_estrato)[self.columna_valor]
            .agg(n="count", media="mean", desviacion="std")
            .reset_index()
            .sort_values("media", ascending=False)
        )
        self.resumen = resumen
        return resumen

    def graficar(self, ruta_salida: str,
                 titulo: str = "Estratificacion - Tiempo de retraso por region") -> str:
        if self.resumen is None:
            self.analizar()

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.bar(self.resumen[self.columna_estrato], self.resumen["media"],
               yerr=self.resumen["desviacion"], capsize=5, color="#16a085")
        ax.set_xlabel(self.columna_estrato)
        ax.set_ylabel(f"{self.columna_valor} (promedio)")
        plt.title(titulo)
        fig.tight_layout()

        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_salida, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return ruta_salida

    def interpretar(self) -> str:
        if self.resumen is None:
            self.analizar()
        r = self.resumen
        peor = r.iloc[0]
        mejor = r.iloc[-1]

        texto = (
            "ESTRATIFICACION\n"
            f"{'-' * 50}\n"
            f"Variable '{self.columna_valor}' segmentada por '{self.columna_estrato}'.\n"
            f"El estrato con peor desempeno es '{peor[self.columna_estrato]}' "
            f"(promedio = {peor['media']:.2f}, n = {peor['n']}).\n"
            f"El estrato con mejor desempeno es '{mejor[self.columna_estrato]}' "
            f"(promedio = {mejor['media']:.2f}, n = {mejor['n']}).\n"
            "Esta diferencia sugiere que el problema no esta distribuido de "
            f"forma homogenea: conviene investigar que hace distinto a "
            f"'{peor[self.columna_estrato]}' frente a los demas estratos.\n"
        )
        return texto
