"""
Los cuatro reportes del proyecto. Cada uno reúne su tabla de datos (una función de
analisis.py), los gráficos relacionados y los textos que explican la información.
"""
from . import analisis

ORIGEN_CHILE = ("Chile: Décimo Sexto Estudio Nacional de Drogas en Población General (ENPG 2024) de SENDA, "
                "una encuesta probabilística aplicada en hogares. Se usan las personas de 18 años o más. "
                "Los registros se leen desde la tabla de encuestados de Chile de la base de datos SQLite.")
ORIGEN_UCI = ("Muestra internacional: dataset Drug Consumption (Quantified) del UCI Machine Learning "
              "Repository, con 1.885 participantes reclutados por internet entre 2010 y 2016. "
              "Los registros se leen desde la tabla de participantes UCI de la base de datos SQLite.")
ADVERTENCIA_FUENTES = ("Los niveles de ambas fuentes no se comparan directamente: UCI es una muestra "
                       "autoseleccionada y no representativa, mientras que la ENPG 2024 es probabilística. "
                       "Lo comparable es el orden y la forma de los patrones.")


class Reporte:
    def __init__(self, titulo, resumen, tabla, graficos, origen, variables, calculos,
                 interpretacion, hallazgos, usa_filtros=False):
        self.titulo = titulo
        self.resumen = resumen
        self.tabla = tabla              # función que devuelve (columnas, filas)
        self.graficos = graficos        # {nombre de la ruta: texto del enlace}
        self.origen = origen
        self.variables = variables
        self.calculos = calculos
        self.interpretacion = interpretacion
        self.hallazgos = hallazgos
        self.usa_filtros = usa_filtros

    def secciones(self):
        """Explicaciones del reporte: las mismas se muestran en pantalla y en el PDF."""
        return [
            ("Origen de los datos", self.origen),
            ("Variables utilizadas", self.variables),
            ("Filtros, agrupaciones y cálculos", self.calculos),
            ("Interpretación", self.interpretacion),
            ("Hallazgos principales", self.hallazgos),
        ]


def formatear(valor):
    """Convierte un valor de la tabla a texto con formato chileno: 17.616 y 31,2."""
    if isinstance(valor, float):
        return f"{valor:.1f}".replace(".", ",")
    if isinstance(valor, int):
        return f"{valor:,}".replace(",", ".")
    return str(valor)


def lectura_de_maximos(filas):
    """Frase que resume la tabla del reporte 4: el grupo de edad con mayor consumo por fuente."""
    frases = []
    for fuente in [analisis.FUENTE_CHILE, analisis.FUENTE_UCI]:
        filas_fuente = [fila for fila in filas if fila[1] == fuente]
        if filas_fuente:
            grupo, _, _, _, porcentaje = max(filas_fuente, key=lambda fila: fila[4])
            frases.append(f"En {fuente}, el mayor consumo está en el grupo de {grupo} años "
                          f"({formatear(porcentaje)} %).")
    return " ".join(frases)


REPORTES = {
    1: Reporte(
        titulo="Recencia de consumo por sustancia y fuente",
        resumen="¿Cuáles son las sustancias con mayor recencia de consumo en cada fuente?",
        tabla=analisis.tabla_recencia,
        graficos={"grafico1": "Gráfico de barras · Recencia por sustancia"},
        origen=[ORIGEN_CHILE, ORIGEN_UCI],
        variables=[
            "Sustancia: alcohol, tabaco, marihuana y cocaína, las cuatro que existen en ambas fuentes.",
            "Fuente: indica de cuál de los dos datasets proviene la fila.",
            "Respuestas válidas: personas que respondieron la pregunta de esa sustancia.",
            "Últimos 30 días, Último año y Alguna vez: porcentaje de personas que consumió dentro de cada periodo.",
        ],
        calculos=[
            "En Chile la recencia se construye con dos preguntas de la encuesta: si consumió alguna vez y "
            "cuándo fue la última vez. En UCI se agrupan las clases CL0 a CL6 en los mismos cuatro niveles: "
            "nunca, hace más de un año, último año y últimos 30 días.",
            "Los periodos son acumulados: 'Último año' incluye a quienes consumieron en los últimos 30 días "
            "y 'Alguna vez' incluye a los dos anteriores. Cada porcentaje se calcula sobre las respuestas "
            "válidas, es decir, sin contar a quienes no saben o no contestan.",
            "Filtro aplicado: solo personas de 18 años o más. Agrupación: sustancia y fuente.",
        ],
        interpretacion=[
            "El orden de las sustancias es el mismo en las dos fuentes: alcohol, tabaco, marihuana y cocaína. "
            "El alcohol es la sustancia más extendida y la cocaína la menos frecuente en cualquier periodo.",
            "La diferencia entre 'Alguna vez' y 'Últimos 30 días' muestra cuánta gente probó una sustancia "
            "pero no la consume actualmente. En Chile esa distancia es muy grande para la marihuana.",
            ADVERTENCIA_FUENTES,
        ],
        hallazgos=[
            "En Chile, 31,2 % consumió alcohol en los últimos 30 días, 25,0 % tabaco, 4,7 % marihuana y 0,2 % cocaína.",
            "En Chile, 70,0 % ha consumido alcohol alguna vez, pero menos de la mitad lo hizo en el último mes.",
            "En Chile, 27,5 % ha probado marihuana alguna vez y solo 4,7 % la consumió en los últimos 30 días.",
            "En la muestra UCI, 82,3 % consumió alcohol y 41,8 % marihuana en los últimos 30 días.",
        ],
    ),
    2: Reporte(
        titulo="Consumo en los últimos 30 días por edad y sexo (Chile)",
        resumen="¿Cómo varía el consumo de sustancias según la edad y el sexo?",
        tabla=analisis.tabla_edad_sexo,
        graficos={"grafico2": "Gráfico de líneas · Consumo por edad",
                  "grafico6": "Gráfico de burbujas · Policonsumo por edad y sexo"},
        origen=[ORIGEN_CHILE],
        variables=[
            "Grupo de edad: la edad en años se agrupa en seis tramos, de 18-24 a 65 o más.",
            "Sexo: hombre o mujer, según lo declarado en la encuesta.",
            "Personas: cantidad de encuestados que pertenece a cada combinación de edad y sexo.",
            "Alcohol, Tabaco, Marihuana y Cocaína: porcentaje del grupo que consumió cada sustancia en los últimos 30 días.",
            "2 o más sustancias: porcentaje del grupo que consumió al menos dos de las cuatro sustancias en "
            "los últimos 30 días (policonsumo).",
        ],
        calculos=[
            "Filtro aplicado: personas de 18 años o más de la ENPG 2024. Agrupación: grupo de edad y sexo, "
            "lo que entrega doce filas.",
            "Para cada grupo se calcula el porcentaje de respuestas válidas con consumo en los últimos 30 días. "
            "El policonsumo se obtiene contando, por persona, en cuántas de las cuatro sustancias declaró "
            "consumo reciente, y luego calculando qué porcentaje del grupo llega a dos o más.",
        ],
        interpretacion=[
            "La edad es la variable que más ordena el consumo reciente: la marihuana se concentra en los "
            "grupos de 18 a 34 años y cae de forma sostenida en los tramos mayores, mientras que el alcohol "
            "se mantiene más estable entre grupos.",
            "Los hombres superan a las mujeres en prácticamente todas las sustancias y tramos de edad. "
            "La brecha es más marcada en alcohol y marihuana.",
            "El policonsumo sigue el mismo patrón: es mayor en hombres jóvenes y disminuye con la edad.",
        ],
        hallazgos=[
            "El policonsumo es máximo en hombres de 25-34 años (26,7 %).",
            "El consumo de alcohol más alto está en hombres de 35-44 años (47,1 %).",
            "La marihuana llega a 15,2 % en hombres de 25-34 años y baja a 1,3 % en hombres de 55-64.",
            "En mujeres de 18-24 años el consumo de marihuana (7,0 %) es la mitad que en hombres de la misma edad (13,8 %).",
        ],
    ),
    3: Reporte(
        titulo="Perfil psicológico según nivel de policonsumo (UCI)",
        resumen="¿Qué rasgos de personalidad presentan los grupos con mayor consumo?",
        tabla=analisis.tabla_perfil_psicologico,
        graficos={"grafico3": "Gráfico de dispersión · Impulsividad y búsqueda de sensaciones",
                  "grafico5": "Mapa de calor · Personalidad y sustancias",
                  "grafico7": "Gráfico de radar · Perfil psicológico"},
        origen=[ORIGEN_UCI, "La ENPG 2024 no mide rasgos de personalidad, por eso este reporte usa solo la muestra UCI."],
        variables=[
            "Nivel de policonsumo: cuántas de las cuatro sustancias comparables (alcohol, tabaco, marihuana y "
            "cocaína) consumió el participante en los últimos 30 días.",
            "Participantes: cantidad de personas en cada nivel.",
            "Rasgos de personalidad: neuroticismo, extraversión, apertura, amabilidad y responsabilidad "
            "(modelo de los cinco grandes), más impulsividad y búsqueda de sensaciones.",
        ],
        calculos=[
            "UCI entrega cada rasgo como un puntaje estandarizado. Para facilitar la lectura se transforma en "
            "percentil dentro de la muestra, de 0 a 100: un percentil 50 corresponde al participante promedio.",
            "Agrupación: los 1.885 participantes se dividen en cuatro niveles de policonsumo. "
            "Cálculo: en cada nivel se promedia el percentil de cada rasgo.",
        ],
        interpretacion=[
            "A mayor número de sustancias consumidas, mayores son la apertura a la experiencia, la búsqueda "
            "de sensaciones y la impulsividad, y menores la responsabilidad y la amabilidad.",
            "El grupo de una sustancia corresponde en la práctica a quienes solo consumen alcohol, y su "
            "perfil es cercano al promedio de la muestra.",
            "Es una asociación entre promedios de grupos con mucho solapamiento: no permite clasificar a una "
            "persona ni afirmar que un rasgo cause el consumo.",
        ],
        hallazgos=[
            "El grupo de 3 o 4 sustancias tiene el percentil más alto en búsqueda de sensaciones (67,7), "
            "apertura (62,7) e impulsividad (61,8).",
            "El mismo grupo tiene el percentil más bajo en responsabilidad (40,5).",
            "La impulsividad y la búsqueda de sensaciones están correlacionadas entre sí (cerca de 0,62).",
        ],
    ),
    4: Reporte(
        titulo="Consumo por grupo de edad según filtros",
        resumen="Datos del gráfico dinámico: elige la sustancia, el periodo, el sexo y el rango de edad.",
        tabla=analisis.tabla_consumo_filtrado,
        graficos={"grafico4": "Gráfico dinámico · Consumo por edad según filtros"},
        origen=[ORIGEN_CHILE, ORIGEN_UCI],
        variables=[
            "Grupo de edad y Fuente: identifican a qué tramo y a cuál dataset corresponde la fila.",
            "Respuestas válidas: personas del grupo que respondieron la pregunta de la sustancia elegida.",
            "Consumidores: personas del grupo que consumieron la sustancia dentro del periodo elegido.",
            "Consumo (%): consumidores dividido por respuestas válidas, multiplicado por 100.",
        ],
        calculos=[
            "Filtros disponibles: sustancia (alcohol, tabaco, marihuana o cocaína), periodo de consumo "
            "(últimos 30 días, último año o alguna vez), sexo (todos, hombre o mujer) y rango de grupos de "
            "edad (desde y hasta).",
            "Agrupación: grupo de edad y fuente. Los grupos sin respuestas válidas no se muestran; si la "
            "selección completa no tiene datos, se muestra un mensaje en lugar de la tabla.",
            "El gráfico dinámico y este reporte usan la misma función de cálculo, por lo que sus valores "
            "coinciden siempre que se apliquen los mismos filtros.",
        ],
        interpretacion=[
            "La tabla permite comparar cómo cambia el consumo de una sustancia a lo largo de la edad en "
            "cada fuente. En general, las sustancias ilegales se concentran en los grupos jóvenes y el "
            "alcohol se reparte de forma más pareja.",
            ADVERTENCIA_FUENTES,
        ],
        hallazgos=[
            "Con los filtros iniciales (marihuana, últimos 30 días, todos), el consumo en Chile es de 10,1 % "
            "en 18-24 años y 10,2 % en 25-34, y baja en cada tramo siguiente.",
            "Al cambiar el periodo a 'Alguna vez' los porcentajes suben en todos los grupos, porque se "
            "incluye a quienes probaron la sustancia hace más de un año.",
            "Al filtrar por sexo, los hombres muestran porcentajes más altos que las mujeres en casi todos los grupos.",
        ],
        usa_filtros=True,
    ),
}
