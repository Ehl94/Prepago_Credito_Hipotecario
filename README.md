# Simulador de Crédito Hipotecario

Este proyecto permite simular créditos hipotecarios, comparar escenarios con y sin prepago, y visualizar resultados en gráficos y archivos exportables.

## Funcionalidades

- Resumen de crédito hipotecario actual.
- Simulación de planes de prepago (límite anual y frecuencia).
- Comparación gráfica de escenarios (sin y con prepago).
- Exportación de cronogramas a CSV y Excel.
- Generación de gráficos en PNG.

## Requisitos

- Python 3.8+
- pandas
- numpy
- matplotlib
- openpyxl (para exportar a Excel)

Instala dependencias con:

```bash
pip install pandas numpy matplotlib openpyxl
```

## Uso

Ejecuta el simulador desde la terminal:

```bash
python prepago_revC.py
```

Sigue las instrucciones en pantalla para seleccionar la función deseada.

## Archivos generados

- `mortgage_summary.csv` / `mortgage_summary.xlsx`
- `mortgage_prepayment_plan.csv` / `mortgage_prepayment_plan.xlsx`
- `mortgage_summary.png`
- `mortgage_simulation.png`
- `mortgage_comparison.png`

## Autor

Emilio Huerta

## Licencia

MIT
