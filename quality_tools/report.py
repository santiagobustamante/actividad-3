"""
Modulo de reporte: combina los textos interpretativos de cada
herramienta ejecutada en un unico archivo de texto plano, listo para
copiar en el informe de la actividad.
"""

from datetime import datetime
from pathlib import Path

ENCABEZADO = """{sep}
RESUMEN DE ANALISIS DE CALIDAD
Problema analizado: {problema}
Fecha de generacion: {fecha}
{sep}

"""


def generar_interpretation_txt(secciones: dict, ruta_salida: str,
                                problema: str = "Retrasos en la entrega de pedidos") -> str:
    """
    Recibe un diccionario {nombre_herramienta: texto_interpretacion} y
    escribe un archivo de texto plano con todo consolidado, listo para
    pegar en el informe (secciones de resultado + interpretacion).
    """
    sep = "=" * 60
    contenido = ENCABEZADO.format(sep=sep, problema=problema,
                                   fecha=datetime.now().strftime("%Y-%m-%d %H:%M"))

    for texto in secciones.values():
        contenido += texto + "\n\n"

    contenido += (
        f"{sep}\n"
        "PROPUESTA DE MEJORA (borrador automatico)\n"
        f"{sep}\n"
        "Con base en los resultados anteriores, se recomienda:\n"
        "1. Atacar primero las causas 'vitales' identificadas en el Pareto, "
        "ya que concentran la mayoria de los retrasos.\n"
        "2. Usar las categorias del Ishikawa con mas causas asociadas como "
        "guia para profundizar el analisis de causa raiz (ej. con 5 porques).\n"
        "3. Si el grafico de control mostro puntos fuera de limite, "
        "investigar que evento especial ocurrio en esas fechas y "
        "documentar una accion correctiva puntual.\n"
        "4. Si la estratificacion mostro un estrato claramente peor, "
        "priorizar ahi un plan de accion focalizado antes de una solucion "
        "generalizada.\n"
        "5. Repetir esta medicion despues de implementar mejoras para "
        "verificar el impacto (ciclo PHVA: Planear-Hacer-Verificar-Actuar).\n"
    )

    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido)

    return ruta_salida
