"""
Diagrama de causa-efecto (Ishikawa / espina de pescado): organiza las
posibles causas de un problema en 6 categorias clasicas (6M) para
facilitar el analisis de causa raiz.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CATEGORIAS_6M = ["Mano de Obra", "Metodo", "Maquina", "Material", "Medio Ambiente", "Medicion"]


class DiagramaIshikawa:
    """Construye un diagrama de Ishikawa a partir de causas categorizadas en 6M."""

    def __init__(self, df: pd.DataFrame, columna_causa: str = "causa_retraso",
                 columna_categoria: str = "categoria_6m"):
        self.df = df
        self.columna_causa = columna_causa
        self.columna_categoria = columna_categoria
        self.causas_por_categoria = None

    def analizar(self) -> dict:
        """
        Agrupa las causas unicas presentes en los datos segun su
        categoria 6M. Retorna un diccionario {categoria: [causas]}.
        """
        datos = self.df[self.df[self.columna_causa] != ""]
        agrupado = (
            datos[[self.columna_categoria, self.columna_causa]]
            .drop_duplicates()
            .groupby(self.columna_categoria)[self.columna_causa]
            .apply(list)
            .to_dict()
        )
        self.causas_por_categoria = {cat: agrupado.get(cat, []) for cat in CATEGORIAS_6M}
        return self.causas_por_categoria

    def graficar(self, ruta_salida: str,
                 problema: str = "Retrasos en la entrega de pedidos") -> str:
        """
        Dibuja el diagrama de espina de pescado: una linea central hacia
        el "problema" (cabeza del pez), con una espina por cada
        categoria 6M y las causas encontradas listadas sobre cada espina.
        """
        if self.causas_por_categoria is None:
            self.analizar()

        fig, ax = plt.subplots(figsize=(14, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

        # Columna vertebral (linea central) hacia la "cabeza" del pez.
        ax.plot([0.5, 9], [5, 5], color="black", linewidth=2)
        ax.text(9.3, 5, problema, fontsize=12, fontweight="bold", va="center",
                bbox=dict(boxstyle="round", facecolor="#f9e79f"))

        categorias = list(self.causas_por_categoria.keys())
        mitad = len(categorias) // 2
        superiores = categorias[:mitad]
        inferiores = categorias[mitad:]

        posiciones_x = np.linspace(1.5, 8, max(len(superiores), len(inferiores)))

        def dibujar_espina(categoria, x, arriba: bool):
            y_base = 5
            y_punta = 8.5 if arriba else 1.5
            ax.plot([x, x + 1.2 if arriba else x - 1.2], [y_punta, y_base],
                    color="#2980b9", linewidth=1.5)
            ax.text(x, y_punta + (0.3 if arriba else -0.3), categoria,
                    fontsize=11, fontweight="bold", ha="center", color="#1a5276")
            causas = self.causas_por_categoria.get(categoria, [])
            for j, causa in enumerate(causas):
                y_texto = y_punta + (-0.5 - j * 0.4 if arriba else 0.5 + j * 0.4)
                ax.text(x + (0.2 if arriba else -0.2), y_texto, f"- {causa}",
                        fontsize=8, ha="left" if arriba else "right")

        for x, cat in zip(posiciones_x, superiores):
            dibujar_espina(cat, x, arriba=True)
        for x, cat in zip(posiciones_x, inferiores):
            dibujar_espina(cat, x, arriba=False)

        plt.title("Diagrama de Ishikawa (Causa - Efecto)", fontsize=14, fontweight="bold")

        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_salida, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return ruta_salida

    def interpretar(self) -> str:
        if self.causas_por_categoria is None:
            self.analizar()

        lineas = ["DIAGRAMA DE ISHIKAWA (CAUSA-EFECTO)", "-" * 50]
        categorias_con_causas = {k: v for k, v in self.causas_por_categoria.items() if v}
        lineas.append(
            f"Se identificaron causas en {len(categorias_con_causas)} de las 6 "
            "categorias clasicas (6M):\n"
        )
        for categoria, causas in self.causas_por_categoria.items():
            if causas:
                lineas.append(f"  * {categoria}: {', '.join(causas)}")

        categoria_mas_cargada = max(
            self.causas_por_categoria, key=lambda k: len(self.causas_por_categoria[k])
        )
        lineas.append(
            f"\nLa categoria con mas causas identificadas es '{categoria_mas_cargada}', "
            "lo que sugiere que ahi hay una linea de investigacion prioritaria "
            "para el analisis de causa raiz.\n"
        )
        return "\n".join(lineas)
