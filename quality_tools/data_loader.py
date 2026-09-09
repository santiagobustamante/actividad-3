"""
Modulo de carga y generacion de datos para el analisis de calidad.

Este modulo se encarga de:
1. Generar un dataset sintetico pero realista sobre retrasos en entregas
   de una empresa de logistica/e-commerce, para cuando no se tiene un
   dataset propio.
2. Cargar un CSV externo que el usuario ya tenga, validando que traiga
   al menos las columnas minimas que las herramientas de calidad usan.
"""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Catalogo de causas de retraso con su peso relativo (frecuencia), su
# categoria dentro del diagrama de Ishikawa (6M) y la duracion promedio
# de retraso que suele generar. Los pesos estan definidos para que se
# cumpla la regla 80/20: pocas causas concentran la mayoria de los
# retrasos, tal como pasa en un proceso logistico real.
CAUSAS_RETRASO = [
    # (nombre_causa, peso, categoria_6m, media_horas_retraso)
    ("Trafico o congestion vial",             0.30, "Medio Ambiente", 3.0),
    ("Falta de stock en bodega",               0.23, "Material",       6.0),
    ("Direccion incorrecta o incompleta",      0.14, "Mano de Obra",   5.0),
    ("Retraso en aduana o documentacion",      0.10, "Metodo",         10.0),
    ("Mal etiquetado del paquete",             0.08, "Mano de Obra",   4.0),
    ("Sobrecarga del centro de distribucion",  0.06, "Metodo",         7.0),
    ("Falla mecanica del vehiculo",            0.04, "Maquina",        8.0),
    ("Condiciones climaticas adversas",        0.03, "Medio Ambiente", 9.0),
    ("Error en sistema de rastreo (GPS/WMS)",  0.02, "Medicion",       5.0),
]

REGIONES = ["Norte", "Sur", "Centro", "Oriente", "Occidente"]
TRANSPORTADORES = ["Transportador A", "Transportador B", "Transportador C"]

COLUMNAS_MINIMAS = {"causa_retraso", "tiempo_retraso_horas"}


def generar_dataset_ejemplo(n_envios: int = 700, semilla: int = 42) -> pd.DataFrame:
    """
    Genera un dataset sintetico de envios de una empresa de logistica,
    simulando un problema real de retrasos en entregas.

    Parametros
    ----------
    n_envios : cantidad de envios a simular.
    semilla : semilla aleatoria para que el dataset sea reproducible.

    Retorna
    -------
    DataFrame con un registro por envio.
    """
    rng = np.random.default_rng(semilla)

    # 1. Decidir cuales envios se retrasaron (35% del total, una tasa
    #    tipica de un proceso con oportunidad de mejora).
    tasa_retraso_base = 0.35
    retrasado = rng.random(n_envios) < tasa_retraso_base

    # 2. Fechas distribuidas en un mes de operacion.
    fecha_inicio = pd.Timestamp("2026-01-01")
    dias = rng.integers(0, 30, size=n_envios)
    fecha = fecha_inicio + pd.to_timedelta(dias, unit="D")

    # 3. Insertar dos "dias criticos" (ej. paro de transportadores,
    #    tormenta) donde la tasa de retraso se dispara. Esto es clave
    #    para que el grafico de control tenga puntos fuera de limite
    #    que detectar, en vez de una serie perfectamente plana.
    dias_criticos = {9, 21}
    for i in range(n_envios):
        if dias[i] in dias_criticos:
            retrasado[i] = rng.random() < 0.75

    nombres = [c[0] for c in CAUSAS_RETRASO]
    pesos = np.array([c[1] for c in CAUSAS_RETRASO])
    pesos = pesos / pesos.sum()
    categorias_6m = {c[0]: c[2] for c in CAUSAS_RETRASO}
    medias_horas = {c[0]: c[3] for c in CAUSAS_RETRASO}

    causa_retraso = np.full(n_envios, "", dtype=object)
    idx_retrasados = np.where(retrasado)[0]
    causas_asignadas = rng.choice(nombres, size=len(idx_retrasados), p=pesos)
    causa_retraso[idx_retrasados] = causas_asignadas

    categoria_6m = np.array(
        [categorias_6m.get(c, "") for c in causa_retraso], dtype=object
    )

    # 4. Tiempo de retraso en horas: se genera con una distribucion
    #    gamma (asimetrica a la derecha), tipica en tiempos de proceso
    #    -la mayoria de los retrasos son cortos, pocos son muy largos-.
    tiempo_base = np.zeros(n_envios)
    for i, causa in zip(idx_retrasados, causas_asignadas):
        media = medias_horas[causa]
        tiempo_base[i] = rng.gamma(shape=2.0, scale=media / 2.0)

    # 5. Distancia del envio (km): se correlaciona con el tiempo de
    #    retraso para que el diagrama de dispersion tenga sentido.
    distancia_km = rng.uniform(5, 150, size=n_envios)
    ruido = rng.normal(0, 1.5, size=n_envios)
    tiempo_retraso_horas = np.where(
        retrasado,
        np.clip(tiempo_base + distancia_km * 0.03 + ruido, 0.1, None),
        0.0,
    )

    # 6. Region y transportador (para estratificacion). La region
    #    "Centro" concentra mas trafico, para que la estratificacion
    #    muestre una diferencia real entre grupos.
    prob_region = np.array([0.15, 0.15, 0.35, 0.20, 0.15])
    region = rng.choice(REGIONES, size=n_envios, p=prob_region)
    transportador = rng.choice(TRANSPORTADORES, size=n_envios, p=[0.5, 0.3, 0.2])

    df = pd.DataFrame({
        "id_envio": [f"ENV-{i + 1:05d}" for i in range(n_envios)],
        "fecha": fecha,
        "region": region,
        "transportador": transportador,
        "distancia_km": np.round(distancia_km, 1),
        "retrasado": retrasado,
        "causa_retraso": causa_retraso,
        "categoria_6m": categoria_6m,
        "tiempo_retraso_horas": np.round(tiempo_retraso_horas, 2),
    })

    return df


def cargar_datos(ruta_csv: Optional[str] = None, n_envios: int = 700,
                  semilla: int = 42) -> pd.DataFrame:
    """
    Carga el dataset a analizar. Si `ruta_csv` es None, genera el
    dataset de ejemplo. Si se entrega una ruta, la carga desde disco y
    valida que traiga las columnas minimas requeridas.
    """
    if ruta_csv is None:
        print(
            "No se especifico un CSV: generando dataset de ejemplo "
            "(retrasos en entregas de una empresa de logistica)..."
        )
        return generar_dataset_ejemplo(n_envios=n_envios, semilla=semilla)

    ruta = Path(ruta_csv)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {ruta_csv}")

    df = pd.read_csv(ruta)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    faltantes = COLUMNAS_MINIMAS - set(df.columns)
    if faltantes:
        print(
            f"Aviso: el CSV no trae las columnas {faltantes}. "
            "Algunas herramientas podrian no funcionar correctamente."
        )
    return df


def generar_serie_diaria_control(df: pd.DataFrame,
                                  columna_valor: str = "tiempo_retraso_horas") -> pd.DataFrame:
    """
    Agrega el dataset por dia para alimentar el grafico de control:
    calcula el promedio diario de la variable indicada (por defecto,
    el tiempo de retraso en horas) sobre los envios retrasados.
    """
    datos = df[df["retrasado"]] if "retrasado" in df.columns else df
    serie = datos.groupby(datos["fecha"].dt.date)[columna_valor].mean().reset_index()
    serie.columns = ["fecha", "valor_promedio"]
    return serie
