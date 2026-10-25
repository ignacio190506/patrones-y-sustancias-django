from django.shortcuts import render

from . import analisis
from . import graficos
from .reportes import REPORTES


# ---------------------------------------------------------------------------
# Clase Python temporal (guía 2): describe los datasets sin usar la base de datos
# ---------------------------------------------------------------------------
class Dataset:
    def __init__(self, nombre, fuente, periodo, filas, columnas, unidad):
        self.nombre = nombre
        self.fuente = fuente
        self.periodo = periodo
        self.filas = filas
        self.columnas = columnas
        self.unidad = unidad


def lista_datasets():
    datasets = []
    datasets.append(Dataset("Drug Consumption (Quantified)", "UCI Machine Learning Repository",
                            "2010-2016", "1.885", 32, "Participante de la encuesta"))
    datasets.append(Dataset("ENPG 2024 · Décimo Sexto Estudio Nacional de Drogas", "SENDA",
                            "2024", "18.668", 402, "Persona encuestada"))
    return datasets


# Información de cada gráfico: tipo, pregunta, explicación e interpretación
GRAFICOS = {
    "grafico1": {
        "funcion": graficos.grafico_barras, "pregunta": "P1", "tipo": "Gráfico de barras",
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
        "funcion": graficos.grafico_lineas, "pregunta": "P2", "tipo": "Gráfico de líneas",
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
        "funcion": graficos.grafico_dispersion, "pregunta": "P4", "tipo": "Gráfico de dispersión",
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
        "funcion": graficos.grafico_p3, "pregunta": "P3", "tipo": "Mapa de calor",
        "titulo": "Rasgos de personalidad y consumo",
        "texto": "¿Existe una relación entre los rasgos de personalidad y el consumo de determinadas sustancias?",
        "explicacion": "Cada celda es la diferencia de percentil promedio entre quienes consumieron la "
                       "sustancia en los últimos 30 días y quienes no. Rojo = los consumidores están más "
                       "arriba en ese rasgo; azul = más abajo.",
        "interpretacion": "Los rasgos se asocian a familias de sustancias: búsqueda de sensaciones a "
                          "marihuana e inhalables, apertura a alucinógenos y neuroticismo a crack. Chocolate "
                          "y cafeína funcionan como control y quedan casi neutros.",
    },
    "grafico5": {
        "funcion": graficos.grafico_p5a, "pregunta": "P5", "tipo": "Gráfico de burbujas",
        "titulo": "Dónde se concentra el policonsumo",
        "texto": "¿Qué características sociodemográficas se presentan en los grupos con mayor consumo?",
        "explicacion": "Cada burbuja cruza un grupo de edad con un sexo. Su tamaño y color muestran el % de "
                       "personas que consumió 2 o más sustancias en los últimos 30 días. Ambos paneles "
                       "comparten la escala 0-100 para poder compararlos.",
        "interpretacion": "En ambas fuentes el policonsumo se concentra en hombres jóvenes y baja con la "
                          "edad. En Chile el máximo está en hombres de 25-34 años (26,7 %).",
    },
    "grafico6": {
        "funcion": graficos.grafico_p5b, "pregunta": "P5", "tipo": "Gráfico de radar",
        "titulo": "Perfil psicológico del policonsumo",
        "texto": "¿Qué características psicológicas presentan los grupos con mayor consumo?",
        "explicacion": "Cada polígono es un grupo según cuántas sustancias consumió en los últimos 30 días; "
                       "cada eje es un rasgo de personalidad medido en percentil (0 a 100).",
        "interpretacion": "A mayor policonsumo, mayor apertura, búsqueda de sensaciones e impulsividad, y "
                          "menor responsabilidad y amabilidad. El grupo de 1 sustancia corresponde en la "
                          "práctica a quienes solo consumen alcohol.",
    },
}

# Información de cada listado: función que arma la tabla y explicación
LISTADOS = {
    "listado1": {
        "funcion": analisis.listado_recencia, "pregunta": "P1",
        "titulo": "Recencia de consumo por sustancia y fuente",
        "explicacion": "Muestra, para cada sustancia comparable y cada fuente, el porcentaje de personas de "
                       "18 años o más que la consumió en los últimos 30 días, en el último año o alguna vez. "
                       "Las ventanas son acumuladas: 'Alguna vez' incluye a quienes consumieron en el último "
                       "año. 'Respuestas válidas' excluye a quienes no saben o no contestan.",
        "lectura": "El alcohol encabeza ambas fuentes y la cocaína es la menos frecuente. Los niveles de UCI "
                   "son más altos, pero no se comparan directamente: es una muestra reclutada por internet "
                   "y no representativa, mientras que ENPG 2024 es probabilística.",
    },
    "listado2": {
        "funcion": analisis.listado_edad_sexo, "pregunta": "P2",
        "titulo": "Consumo en los últimos 30 días por edad y sexo (Chile)",
        "explicacion": "Cada fila es un grupo de edad y sexo de la ENPG 2024 (18 años o más). Se indica "
                       "cuántas personas tiene el grupo, el % que consumió cada sustancia en los últimos "
                       "30 días y el % que consumió 2 o más sustancias en ese periodo (policonsumo).",
        "lectura": "Los hombres superan a las mujeres en todos los tramos, y el consumo de marihuana y el "
                   "policonsumo son mayores en los grupos de 18 a 34 años.",
    },
    "listado3": {
        "funcion": analisis.listado_perfil_psicologico, "pregunta": "P5",
        "titulo": "Perfil psicológico según nivel de policonsumo (UCI)",
        "explicacion": "Agrupa a los 1.885 participantes de UCI según cuántas de las cuatro sustancias "
                       "comparables consumieron en los últimos 30 días, y muestra el percentil promedio de "
                       "cada rasgo de personalidad (50 = promedio de la muestra).",
        "lectura": "El grupo de 3 o 4 sustancias tiene los percentiles más altos en apertura, búsqueda de "
                   "sensaciones e impulsividad, y los más bajos en responsabilidad y amabilidad.",
    },
}


def _pagina_sin_datos(request, error):
    return render(request, "dashboard/sin_datos.html", {"archivo": str(error)})


# ---------------------------------------------------------------------------
# Dashboard principal
# ---------------------------------------------------------------------------
def index(request):
    try:
        kpis = analisis.indicadores()
        tarjetas = []
        for nombre_ruta, info in GRAFICOS.items():
            tarjetas.append({"ruta": nombre_ruta, "titulo": info["titulo"], "tipo": info["tipo"],
                             "pregunta": info["pregunta"], "grafico": info["funcion"]()})
        circular = graficos.grafico_circular_policonsumo()
    except analisis.DatosNoEncontrados as error:
        return _pagina_sin_datos(request, error)

    contexto = {
        "kpis": kpis,
        "tarjetas": tarjetas,
        "circular": circular,
        "datasets": lista_datasets(),
        "destacados": [r for r in REPORTES if r.destacado],
    }
    return render(request, "dashboard/index.html", contexto)


# ---------------------------------------------------------------------------
# Páginas de cada gráfico (guías 4, 5 y 6): una vista y una ruta por gráfico
# ---------------------------------------------------------------------------
def _mostrar_grafico(request, nombre_ruta):
    info = GRAFICOS[nombre_ruta]
    try:
        grafico = info["funcion"]()
    except analisis.DatosNoEncontrados as error:
        return _pagina_sin_datos(request, error)
    contexto = {
        "grafico": grafico,
        "info": info,
        # Reportes que responden la misma pregunta de investigación
        "reportes": [r for r in REPORTES if r.pregunta == info["pregunta"]],
    }
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


# ---------------------------------------------------------------------------
# Listados de datos: la vista arma la tabla y la envía a la plantilla
# ---------------------------------------------------------------------------
def _mostrar_listado(request, nombre_ruta):
    info = LISTADOS[nombre_ruta]
    try:
        columnas, filas = info["funcion"]()
    except analisis.DatosNoEncontrados as error:
        return _pagina_sin_datos(request, error)
    contexto = {"info": info, "columnas": columnas, "filas": filas}
    return render(request, "dashboard/listado.html", contexto)


def listado1(request):
    return _mostrar_listado(request, "listado1")


def listado2(request):
    return _mostrar_listado(request, "listado2")


def listado3(request):
    return _mostrar_listado(request, "listado3")


# ---------------------------------------------------------------------------
# Reportes: listado de solo lectura
# ---------------------------------------------------------------------------
def reporte_lista(request):
    return render(request, "dashboard/reporte_lista.html", {"reportes": REPORTES})
