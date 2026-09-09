"""
Hoja de verificacion (check sheet): conteo estructurado de ocurrencias
de un evento, cruzando dos dimensiones (por ejemplo, causa de retraso x
region), para facilitar la recoleccion y lectura de datos.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class HojaVerificacion:
    """Genera una tabla de conteo cruzado (hoja de verificacion) entre dos variables categoricas."""

    def __init__(self, df: pd.DataFrame, columna_filas: str = "causa_retraso",
                 columna_columnas: str = "region"):
        self.df = df
        self.columna_filas = columna_filas
        self.columna_columnas = columna_columnas
        self.tabla = None

    def analizar(self) -> pd.DataFrame:
        """Construye la tabla cruzada de conteos con totales por fila y columna."""
        datos = self.df[self.df[self.columna_filas] != ""]
        tabla = pd.crosstab(
            datos[self.columna_filas], datos[self.columna_columnas],
            margins=True, margins_name="Total",
        )
        self.tabla = tabla
        return tabla

    def guardar_csv(self, ruta_salida: str) -> str:
        """Guarda la hoja de verificacion como CSV, lista para pegar en el informe."""
        if self.tabla is None:
            self.analizar()
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        self.tabla.to_csv(ruta_salida)
        return ruta_salida

    def graficar(self, ruta_salida: str,
                 titulo: str = "Hoja de verificacion - Causa vs Region") -> str:
        """Representa la hoja de verificacion como un mapa de calor de conteos."""
        if self.tabla is None:
            self.analizar()
        datos_grafica = self.tabla.drop(index="Total", errors="ignore").drop(columns="Total", errors="ignore")

        fig, ax = plt.subplots(figsize=(9, 6))
        im = ax.imshow(datos_grafica.values, cmap="Reds", aspect="auto")
        ax.set_xticks(range(len(datos_grafica.columns)))
        ax.set_xticklabels(datos_grafica.columns, rotation=40, ha="right")
        ax.set_yticks(range(len(datos_grafica.index)))
        ax.set_yticklabels(datos_grafica.index)

        for i in range(datos_grafica.shape[0]):
            for j in range(datos_grafica.shape[1]):
                ax.text(j, i, datos_grafica.iloc[i, j], ha="center", va="center", color="black")

        fig.colorbar(im, ax=ax, label="Frecuencia")
        plt.title(titulo)
        fig.tight_layout()

        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_salida, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return ruta_salida

    def interpretar(self) -> str:
        if self.tabla is None:
            self.analizar()
        datos = self.tabla.drop(index="Total", errors="ignore").drop(columns="Total", errors="ignore")
        celda_max = datos.stack().idxmax()
        valor_max = datos.stack().max()

        texto = (
            "HOJA DE VERIFICACION\n"
            f"{'-' * 50}\n"
            f"Se cruzo '{self.columna_filas}' contra '{self.columna_columnas}'.\n"
            "La combinacion con mayor frecuencia es "
            f"'{celda_max[0]}' en '{celda_max[1]}' con {valor_max} ocurrencias.\n"
            "Esta hoja permite ver rapidamente en que combinacion causa-segmento "
            "se deberian concentrar los esfuerzos de verificacion y control.\n"
        )
        return texto
