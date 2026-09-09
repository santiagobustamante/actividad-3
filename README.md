# Herramientas de Calidad - Actividad de Aprendizaje 3

Aplicacion en Python que implementa las 7 herramientas basicas de
calidad para analizar un problema de proceso, producto o servicio.

**Problema analizado por defecto:** retrasos en la entrega de pedidos
de una empresa de logistica / e-commerce.

## Instalacion

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar una sola herramienta (genera dataset de ejemplo automaticamente)
python main.py --tool pareto

# Ejecutar todas las herramientas de una sola vez
python main.py --tool all

# Usar tu propio CSV en lugar del dataset de ejemplo
python main.py --tool all --data mis_datos.csv

# Cambiar la carpeta de salida y la descripcion del problema
python main.py --tool pareto --output resultados --problema "Devoluciones en e-commerce"
```

Herramientas disponibles en `--tool`:

| Valor             | Herramienta                          |
|-------------------|---------------------------------------|
| `pareto`          | Diagrama de Pareto (regla 80/20)      |
| `ishikawa`        | Diagrama de causa-efecto (6M)         |
| `checksheet`      | Hoja de verificacion (conteo cruzado) |
| `histograma`      | Histograma de distribucion            |
| `dispersion`      | Diagrama de dispersion / correlacion  |
| `control`         | Grafico de control (limites 3 sigma)  |
| `estratificacion` | Estratificacion por categoria         |
| `all`             | Ejecuta las 7 anteriores              |

## Salidas generadas

- `output/graphs/*.png` : graficas en alta resolucion (300 dpi) de cada herramienta.
- `output/hoja_verificacion.csv` : tabla cruzada de la hoja de verificacion.
- `output/interpretation.txt` : resumen interpretativo consolidado + propuesta de mejora,
  listo para copiar en el informe.

## Tu propio CSV

Si usas `--data`, el CSV debe traer (idealmente) estas columnas:

- `causa_retraso` (texto): categoria/causa del problema (para Pareto, Ishikawa, hoja de verificacion).
- `categoria_6m` (texto): una de `Mano de Obra`, `Metodo`, `Maquina`, `Material`, `Medio Ambiente`, `Medicion` (para Ishikawa).
- `tiempo_retraso_horas` (numero): variable numerica del problema (para histograma, dispersion, estratificacion).
- `distancia_km` (numero): segunda variable numerica (para el diagrama de dispersion).
- `region` o `transportador` (texto): variable de segmentacion (para estratificacion y hoja de verificacion).
- `fecha` (fecha) y `retrasado` (booleano): para el grafico de control (se agrega por dia).

Puedes adaptar los nombres de columnas pasando otros parametros directamente
a las clases en `quality_tools/` si tu dataset usa nombres distintos.

## Estructura del proyecto

```
actividad-3/
├── main.py                  # CLI principal
├── requirements.txt
├── quality_tools/
│   ├── data_loader.py        # carga CSV o genera dataset de ejemplo
│   ├── pareto.py
│   ├── ishikawa.py
│   ├── checksheet.py
│   ├── histogram.py
│   ├── scatter.py
│   ├── control_chart.py
│   ├── stratification.py
│   └── report.py             # arma interpretation.txt
└── output/
    ├── graphs/
    └── interpretation.txt
```

## Como usar esto en el informe de la actividad

Cada herramienta ejecutada imprime en consola y guarda en
`interpretation.txt` un bloque de texto ya redactado con:

1. Que se calculo (resultado).
2. Como se interpreta (interpretacion).

Puedes copiar cada bloque directamente en la seccion correspondiente de
tu informe, y usar el PNG de `output/graphs/` como figura de apoyo.
Recuerda completar tu propia justificacion de por que elegiste esa
herramienta para el problema, ya que esa parte es criterio tuyo como
estudiante.
