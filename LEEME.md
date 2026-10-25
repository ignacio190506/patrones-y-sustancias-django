# Dashboard Django · Certamen 2

Página web del proyecto semestral (notebook Proyecto_Nuevo.ipynb): consumo de sustancias
en Chile (SENDA, ENPG 2024) y en una muestra internacional (UCI Drug Consumption).

## Requisitos de la pauta y dónde están

| Criterio | Dónde |
|---|---|
| Menú con desplegables "Listados de datos" y "Gráficos" | `dashboard/templates/dashboard/menu.html` |
| Listado 1, 2 y 3 en tablas con explicación | `/dashboard/listado1`, `listado2`, `listado3` |
| Gráfico de barras | `/dashboard/grafico1` |
| Gráfico de líneas | `/dashboard/grafico2` |
| Gráfico de dispersión | `/dashboard/grafico3` |
| Datos enviados desde las vistas a las plantillas | `dashboard/views.py` (contexto de `render`) |

Extras: mapa de calor, burbujas y radar; página de Reportes (solo lectura, definidos en `dashboard/reportes.py`).

## Ejecutar (Windows, VS Code, terminal PowerShell)

    py -m venv .venv
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    py manage.py migrate
    py manage.py createsuperuser
    py manage.py runserver

Abrir http://127.0.0.1:8000/dashboard/

## Datos

- `datos/drug_consumption.data`: UCI Machine Learning Repository, Drug Consumption (Quantified).
- `datos/enpg_2024_reducida.csv`: SENDA, Décimo Sexto Estudio Nacional de Drogas en Población
  General 2024, solo con las 13 columnas usadas (la base original pesa 54 MB).
