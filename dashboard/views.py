from functools import wraps

from django.http import FileResponse, Http404
from django.shortcuts import render

from . import analisis, exportar, graficos
from .forms import leer_filtros
from .models import EncuestadoChile, ParticipanteUCI
from .reportes import REPORTES, formatear, lectura_de_maximos

TIPO_PDF = "application/pdf"
TIPO_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Textos de cada gráfico, la función que lo dibuja y el número de su reporte
GRAFICOS = {
    "grafico1": {
        "funcion": graficos.grafico_barras, "reporte": 1, "pregunta": "P1", "tipo": "Gráfico de barras",
        "titulo": "Sustancias con mayor recencia de consumo",
        "texto": "¿Cuáles son las sustancias con mayor recencia de consumo en la muestra?",
        "explicacion": "Cada barra es el porcentaje de personas de 18 años o más que consumió la sustancia "
                       "dentro de la ventana indicada. Azul = Chile (ENPG 2024), coral = muestra "
                       "internacional (UCI). Los tres paneles van de la ventana más corta (últimos 30 días) "
                       "a la más amplia (alguna vez); las ventanas son acumuladas.",
        "interpretacion": "El orden de recencia es idéntico en ambas fuentes: alcohol, tabaco, marihuana y "
                          "cocaína. Los niveles de la muestra internacional son mucho más altos, pero no deben "
                          "leerse como que una población consume más: UCI es una muestra autoseleccionada por "
                          "internet y ENPG 2024 es una encuesta probabilística. Lo comparable es el orden.",
    },
    "grafico2": {
        "funcion": graficos.grafico_lineas, "reporte": 2, "pregunta": "P2", "tipo": "Gráfico de líneas",
        "titulo": "Consumo según grupo de edad",
        "texto": "¿Cómo varía el consumo de sustancias según la edad?",
        "explicacion": "Cada línea es una sustancia y cada punto es el porcentaje de personas de ese grupo "
                       "de edad que la consumió en los últimos 30 días. Se usan líneas porque los grupos de "
                       "edad tienen un orden natural y la pendiente muestra la tendencia.",
        "interpretacion": "En ambas fuentes el consumo de marihuana y cocaína baja con fuerza a medida que "
                          "aumenta la edad, mientras que el alcohol se mantiene más estable entre grupos. La "
                          "edad es la variable sociodemográfica que más ordena el consumo reciente.",
    },
    "grafico3": {
        "funcion": graficos.grafico_dispersion, "reporte": 3, "pregunta": "P4", "tipo": "Gráfico de dispersión",
        "titulo": "Impulsividad, búsqueda de sensaciones y consumo",
        "texto": "¿Existe una relación entre el nivel de impulsividad y la recencia de consumo?",
        "explicacion": "Cada punto es un participante de la muestra UCI. El eje X es su percentil de "
                       "impulsividad y el eje Y su percentil de búsqueda de sensaciones. El color indica "
                       "cuándo consumió marihuana por última vez. Se agrega un pequeño desplazamiento "
                       "a cada punto porque ambas escalas tienen pocos valores posibles y sin él los puntos se superpondrían.",
        "interpretacion": "Los puntos suben de izquierda a derecha: ambos rasgos están correlacionados "
                          "(cerca de 0,62). Los puntos coral (consumo en los últimos 30 días) se concentran "
                          "arriba a la derecha, y los grises (nunca) y verdes (hace más de 1 año) abajo a la izquierda. Hay mucho "
                          "solapamiento: es una asociación, no permite clasificar a una persona ni afirmar causa.",
    },
    "grafico4": {
        "funcion": graficos.grafico_dinamico, "reporte": 4, "dinamico": True,
        "pregunta": "P2", "tipo": "Gráfico dinámico",
        "titulo": "Consumo por grupo de edad según filtros",
        "texto": "¿Cómo cambia el consumo por edad al variar la sustancia, el periodo o el sexo?",
        "explicacion": "Eje X: grupo de edad. Eje Y: porcentaje de personas del grupo que consumió la "
                       "sustancia elegida dentro del periodo elegido. Cada color es una fuente: azul = Chile "
                       "(ENPG 2024), coral = muestra internacional (UCI). Los filtros permiten cambiar la "
                       "sustancia, el periodo de consumo, el sexo y el rango de grupos de edad; el gráfico "
                       "se vuelve a calcular en la vista con cada selección.",
        "interpretacion": "Las sustancias ilegales se concentran en los grupos jóvenes y disminuyen con la "
                          "edad, mientras que el alcohol se reparte de forma más pareja. Los niveles de UCI son "
                          "más altos porque es una muestra autoseleccionada por internet: lo comparable entre "
                          "fuentes es la forma de la curva, no su altura.",
    },
    # Análisis complementarios
    "grafico5": {
        "funcion": graficos.grafico_mapa_calor, "reporte": 3, "pregunta": "P3", "tipo": "Mapa de calor",
        "titulo": "Rasgos de personalidad y consumo",
        "texto": "¿Existe una relación entre los rasgos de personalidad y el consumo de determinadas sustancias?",
        "explicacion": "Cada celda es la diferencia de percentil promedio entre quienes consumieron la "
                       "sustancia en los últimos 30 días y quienes no. Rojo = los consumidores están más "
                       "arriba en ese rasgo; azul = más abajo.",
        "interpretacion": "Los rasgos se asocian a familias de sustancias: búsqueda de sensaciones a "
                          "marihuana e inhalables, apertura a alucinógenos y neuroticismo a crack. Chocolate "
                          "y cafeína funcionan como control y quedan casi neutros.",
    },
    "grafico6": {
        "funcion": graficos.grafico_burbujas, "reporte": 2, "pregunta": "P5", "tipo": "Gráfico de burbujas",
        "titulo": "Dónde se concentra el policonsumo",
        "texto": "¿Qué características sociodemográficas se presentan en los grupos con mayor consumo?",
        "explicacion": "Cada burbuja cruza un grupo de edad con un sexo. Su tamaño y color muestran el % de "
                       "personas que consumió 2 o más sustancias en los últimos 30 días. Ambos paneles "
                       "comparten la escala 0-100 para poder compararlos.",
        "interpretacion": "En ambas fuentes el policonsumo se concentra en hombres jóvenes y baja con la "
                          "edad. En Chile el máximo está en hombres de 25-34 años (26,7 %).",
    },
    "grafico7": {
        "funcion": graficos.grafico_radar, "reporte": 3, "pregunta": "P5", "tipo": "Gráfico de radar",
        "titulo": "Perfil psicológico del policonsumo",
        "texto": "¿Qué características psicológicas presentan los grupos con mayor consumo?",
        "explicacion": "Cada polígono es un grupo según cuántas sustancias consumió en los últimos 30 días; "
                       "cada eje es un rasgo de personalidad medido en percentil (0 a 100).",
        "interpretacion": "A mayor policonsumo, mayor apertura, búsqueda de sensaciones e impulsividad, y "
                          "menor responsabilidad y amabilidad. El grupo de 1 sustancia corresponde en la "
                          "práctica a quienes solo consumen alcohol.",
    },
}


def requiere_datos(vista):
    """Decorador: si las tablas están vacías, muestra cómo cargarlas en vez de un error."""
    @wraps(vista)
    def vista_protegida(request, *args, **kwargs):
        try:
            return vista(request, *args, **kwargs)
        except analisis.DatosNoEncontrados as error:
            return render(request, "dashboard/sin_datos.html", {"tabla": str(error)}, status=503)
    return vista_protegida


class Dataset:
    def __init__(self, nombre, fuente, periodo, modelo):
        self.nombre = nombre
        self.fuente = fuente
        self.periodo = periodo
        self.tabla = modelo._meta.db_table
        self.registros = formatear(modelo.objects.count())


def lista_datasets():
    return [
        Dataset("ENPG 2024 · Décimo Sexto Estudio Nacional de Drogas", "SENDA", "2024", EncuestadoChile),
        Dataset("Drug Consumption (Quantified)", "UCI Machine Learning Repository", "2010-2016", ParticipanteUCI),
    ]


# ---------------------------------------------------------------------------
# Página de inicio
# ---------------------------------------------------------------------------
@requiere_datos
def index(request):
    tarjetas = []
    for nombre_ruta, info in GRAFICOS.items():
        filtros = analisis.FILTROS_INICIALES if info.get("dinamico") else {}
        tarjetas.append({"ruta": nombre_ruta, "info": info, "grafico": info["funcion"](**filtros)})
    contexto = {
        "kpis": {nombre: formatear(valor) for nombre, valor in analisis.indicadores().items()},
        "tarjetas": tarjetas,
        "circular": graficos.grafico_circular_policonsumo(),
        "datasets": lista_datasets(),
        "reportes": REPORTES,
    }
    return render(request, "dashboard/index.html", contexto)


# ---------------------------------------------------------------------------
# Gráficos: una vista y una ruta por gráfico
# ---------------------------------------------------------------------------
@requiere_datos
def _mostrar_grafico(request, nombre_ruta):
    info = GRAFICOS[nombre_ruta]
    # Solo el gráfico dinámico lee filtros desde la URL (?sustancia=...&sexo=...)
    form, filtros = leer_filtros(request.GET) if info.get("dinamico") else (None, {})
    contexto = {"info": info, "form": form, "grafico": info["funcion"](**filtros)}
    return render(request, "dashboard/grafico.html", contexto)


def grafico1(request):
    return _mostrar_grafico(request, "grafico1")


def grafico2(request):
    return _mostrar_grafico(request, "grafico2")


def grafico3(request):
    return _mostrar_grafico(request, "grafico3")


def grafico4(request):
    return _mostrar_grafico(request, "grafico4")


def grafico5(request):
    return _mostrar_grafico(request, "grafico5")


def grafico6(request):
    return _mostrar_grafico(request, "grafico6")


def grafico7(request):
    return _mostrar_grafico(request, "grafico7")


# ---------------------------------------------------------------------------
# Reportes: la página, el PDF y el Excel comparten los mismos datos
# ---------------------------------------------------------------------------
def _datos_reporte(request, numero):
    if numero not in REPORTES:
        raise Http404("El reporte no existe.")
    reporte = REPORTES[numero]
    form, filtros = leer_filtros(request.GET) if reporte.usa_filtros else (None, {})
    columnas, filas = reporte.tabla(**filtros)
    secciones = reporte.secciones()
    if reporte.usa_filtros and filas:
        secciones.append(("Lectura de la selección actual", [lectura_de_maximos(filas)]))
    return {
        "numero": numero,
        "reporte": reporte,
        "form": form,
        "seleccion": form.resumen() if form else "",
        "columnas": columnas,
        "filas": filas,
        "filas_texto": [[formatear(valor) for valor in fila] for fila in filas],
        "secciones": secciones,
    }


@requiere_datos
def reporte(request, numero):
    return render(request, "dashboard/reporte.html", _datos_reporte(request, numero))


@requiere_datos
def reporte_pdf(request, numero):
    datos = _datos_reporte(request, numero)
    archivo = exportar.generar_pdf(datos["reporte"].titulo, datos["columnas"], datos["filas_texto"],
                                   datos["secciones"], datos["seleccion"])
    return FileResponse(archivo, as_attachment=True, filename=f"reporte{numero}.pdf",
                        content_type=TIPO_PDF)


@requiere_datos
def reporte_excel(request, numero):
    datos = _datos_reporte(request, numero)
    archivo = exportar.generar_excel(f"Reporte {numero}", datos["columnas"], datos["filas"])
    return FileResponse(archivo, as_attachment=True, filename=f"reporte{numero}.xlsx",
                        content_type=TIPO_EXCEL)
