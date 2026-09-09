"""
Diagrama de Pareto: identifica que causas concentran la mayoria de los
problemas (regla 80/20). Es la primera herramienta a aplicar cuando hay
multiples causas y se necesita priorizar en donde actuar primero.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class AnalisisPareto:
    """Encapsula el calculo y la graficacion de un diagrama de Pareto."""

    def __init__(self, df: pd.DataFrame, columna_categoria: str = "causa_retraso"):
        self.df = df
        self.columna_categoria = columna_categoria
        self.tabla = None  # se llena al ejecutar analizar()

    def analizar(self) -> pd.DataFrame:
        """
        Calcula la frecuencia de cada categoria, el porcentaje individual
        y el porcentaje acumulado. Retorna la tabla ordenada de mayor a
        menor frecuencia (insumo estandar de un Pareto).
        """
        datos = self.df[self.df[self.columna_categoria] != ""]
        conteo = (
            datos[self.columna_categoria]
            .value_counts()
            .rename_axis("causa")
            .reset_index(name="frecuencia")
        )
        conteo["porcentaje"] = 100 * conteo["frecuencia"] / conteo["frecuencia"].sum()
        conteo["porcentaje_acumulado"] = conteo["porcentaje"].cumsum()
        self.tabla = conteo
        return conteo

    def causas_vitales(self, corte: float = 80.0) -> pd.DataFrame:
        """
        Devuelve el subconjunto de causas "vitales": las primeras que,
        acumuladas, alcanzan el porcentaje de corte (80% por defecto).
        """
        if self.tabla is None:
            self.analizar()
        idx_corte = self.tabla[self.tabla["porcentaje_acumulado"] >= corte].index.min()
        return self.tabla.loc[:idx_corte]

    def graficar(self, ruta_salida: str,
                 titulo: str = "Diagrama de Pareto - Causas de retraso") -> str:
        """
        Genera el diagrama de Pareto: barras de frecuencia + linea de
        porcentaje acumulado, con la marca del 80% para ubicar el corte.
        """
        if self.tabla is None:
            self.analizar()

        tabla = self.tabla
        fig, ax1 = plt.subplots(figsize=(10, 6))

        colores = ["#c0392b" if p <= 80 else "#95a5a6" for p in tabla["porcentaje_acumulado"]]
        ax1.bar(tabla["causa"], tabla["frecuencia"], color=colores)
        ax1.set_ylabel("Frecuencia (numero de envios)")
        ax1.set_xlabel("Causa de retraso")
        ax1.tick_params(axis="x", rotation=40)
        for tick in ax1.get_xticklabels():
            tick.set_ha("right")

        ax2 = ax1.twinx()
        ax2.plot(tabla["causa"], tabla["porcentaje_acumulado"], color="#2c3e50",
                  marker="o", linewidth=2, label="% acumulado")
        ax2.axhline(80, color="#e67e22", linestyle="--", linewidth=1.5, label="Corte 80%")
        ax2.set_ylabel("Porcentaje acumulado (%)")
        ax2.set_ylim(0, 110)
        ax2.legend(loc="lower right")

        plt.title(titulo)
        fig.tight_layout()

        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_salida, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return ruta_salida

    def interpretar(self, corte: float = 80.0) -> str:
        """
        Genera un texto interpretativo automatico: cuantas causas y
        cuales concentran el X% de los problemas.
        """
        if self.tabla is None:
            self.analizar()
        vitales = self.causas_vitales(corte)
        nombres = ", ".join(vitales["causa"].tolist())
        n_vitales = len(vitales)
        n_total = len(self.tabla)
        pct_acumulado = vitales["porcentaje_acumulado"].iloc[-1]

        texto = (
            "DIAGRAMA DE PARETO\n"
            f"{'-' * 50}\n"
            f"Se identificaron {n_total} causas distintas de retraso.\n"
            f"De estas, {n_vitales} causa(s) ('pocas vitales') concentran "
            f"el {pct_acumulado:.1f}% de los envios retrasados:\n"
            f"  -> {nombres}\n\n"
            "Segun la regla de Pareto (80/20), enfocar los esfuerzos de "
            f"mejora en estas {n_vitales} causa(s) deberia tener el mayor "
            "impacto sobre el problema total, en lugar de repartir "
            f"recursos entre las {n_total - n_vitales} causas restantes "
            "('muchas triviales').\n"
        )
        return texto
