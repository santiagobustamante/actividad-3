"""
Punto de entrada de la aplicacion de herramientas de calidad.

Uso basico:
    python main.py --tool pareto
    python main.py --tool all --data mis_datos.csv
    python main.py --tool ishikawa --output resultados/

Si no se especifica --data, se genera automaticamente un dataset de
ejemplo sobre retrasos en entregas de una empresa de logistica.
"""

import argparse
from pathlib import Path

from quality_tools.checksheet import HojaVerificacion
from quality_tools.control_chart import GraficoControl
from quality_tools.data_loader import cargar_datos, generar_serie_diaria_control
from quality_tools.histogram import Histograma
from quality_tools.ishikawa import DiagramaIshikawa
from quality_tools.pareto import AnalisisPareto
from quality_tools.report import generar_interpretation_txt
from quality_tools.scatter import DiagramaDispersion
from quality_tools.stratification import Estratificacion


def ejecutar_pareto(df, carpeta_graficos):
    analisis = AnalisisPareto(df)
    analisis.analizar()
    ruta = analisis.graficar(str(carpeta_graficos / "pareto.png"))
    print(f"Grafica de Pareto guardada en: {ruta}")
    return analisis.interpretar()


def ejecutar_ishikawa(df, carpeta_graficos):
    diagrama = DiagramaIshikawa(df)
    diagrama.analizar()
    ruta = diagrama.graficar(str(carpeta_graficos / "ishikawa.png"))
    print(f"Diagrama de Ishikawa guardado en: {ruta}")
    return diagrama.interpretar()


def ejecutar_checksheet(df, carpeta_graficos):
    hoja = HojaVerificacion(df)
    hoja.analizar()
    ruta_png = hoja.graficar(str(carpeta_graficos / "hoja_verificacion.png"))
    ruta_csv = hoja.guardar_csv(str(carpeta_graficos.parent / "hoja_verificacion.csv"))
    print(f"Hoja de verificacion guardada en: {ruta_png} y {ruta_csv}")
    return hoja.interpretar()


def ejecutar_histograma(df, carpeta_graficos):
    hist = Histograma(df)
    hist.analizar()
    ruta = hist.graficar(str(carpeta_graficos / "histograma.png"))
    print(f"Histograma guardado en: {ruta}")
    return hist.interpretar()


def ejecutar_dispersion(df, carpeta_graficos):
    disp = DiagramaDispersion(df)
    disp.analizar()
    ruta = disp.graficar(str(carpeta_graficos / "dispersion.png"))
    print(f"Diagrama de dispersion guardado en: {ruta}")
    return disp.interpretar()


def ejecutar_control(df, carpeta_graficos):
    serie = generar_serie_diaria_control(df)
    control = GraficoControl(serie)
    control.analizar()
    ruta = control.graficar(str(carpeta_graficos / "control.png"))
    print(f"Grafico de control guardado en: {ruta}")
    return control.interpretar()


def ejecutar_estratificacion(df, carpeta_graficos):
    estrato = Estratificacion(df)
    estrato.analizar()
    ruta = estrato.graficar(str(carpeta_graficos / "estratificacion.png"))
    print(f"Grafica de estratificacion guardada en: {ruta}")
    return estrato.interpretar()


EJECUTORES = {
    "pareto": ejecutar_pareto,
    "ishikawa": ejecutar_ishikawa,
    "checksheet": ejecutar_checksheet,
    "histograma": ejecutar_histograma,
    "dispersion": ejecutar_dispersion,
    "control": ejecutar_control,
    "estratificacion": ejecutar_estratificacion,
}

HERRAMIENTAS_DISPONIBLES = list(EJECUTORES.keys()) + ["all"]


def main():
    parser = argparse.ArgumentParser(
        description="Herramientas de calidad para analizar un problema de proceso/producto/servicio."
    )
    parser.add_argument("--tool", choices=HERRAMIENTAS_DISPONIBLES, default="pareto",
                        help="Herramienta de calidad a aplicar (default: pareto).")
    parser.add_argument("--data", default=None,
                        help="Ruta a un CSV propio. Si no se indica, se genera un dataset de ejemplo.")
    parser.add_argument("--output", default="output",
                        help="Carpeta donde se guardan las graficas y el interpretation.txt (default: output).")
    parser.add_argument("--problema", default="Retrasos en la entrega de pedidos",
                        help="Descripcion corta del problema, usada en los titulos y el reporte.")
    args = parser.parse_args()

    carpeta_salida = Path(args.output)
    carpeta_graficos = carpeta_salida / "graphs"
    carpeta_graficos.mkdir(parents=True, exist_ok=True)

    df = cargar_datos(args.data)
    print(f"Dataset cargado: {len(df)} registros.\n")

    herramientas_a_ejecutar = list(EJECUTORES.keys()) if args.tool == "all" else [args.tool]

    secciones = {}
    for nombre in herramientas_a_ejecutar:
        print(f"--- Ejecutando: {nombre} ---")
        texto = EJECUTORES[nombre](df, carpeta_graficos)
        secciones[nombre] = texto
        print(texto)

    ruta_interpretacion = generar_interpretation_txt(
        secciones, str(carpeta_salida / "interpretation.txt"), problema=args.problema
    )
    print(f"\nResumen interpretativo consolidado en: {ruta_interpretacion}")


if __name__ == "__main__":
    main()
