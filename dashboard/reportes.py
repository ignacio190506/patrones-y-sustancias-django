"""
Reportes del análisis. Son datos fijos escritos en el código: no se guardan en la
base de datos y no se pueden crear, editar ni eliminar desde la página.

Se construyen igual que en la guía 2: una clase Python y una lista de objetos.
"""


class Reporte:
    def __init__(self, pregunta, titulo, descripcion, fuente, destacado):
        self.pregunta = pregunta
        self.titulo = titulo
        self.descripcion = descripcion
        self.fuente = fuente
        self.destacado = destacado  # True: aparece en la página de inicio


REPORTES = [
    Reporte("P1", "El orden de recencia coincide en ambas fuentes",
            "Alcohol, tabaco, marihuana y cocaína aparecen en el mismo orden en Chile y en la muestra "
            "internacional. En Chile, 31,2 % declara consumo de alcohol en los últimos 30 días, 25,0 % de "
            "tabaco, 4,7 % de marihuana y 0,2 % de cocaína.",
            "Ambas fuentes", True),
    Reporte("P2", "La edad es la variable que más ordena el consumo",
            "El consumo reciente de marihuana se concentra en los grupos jóvenes: en Chile llega a 10,1 % "
            "en 25-34 años y 10,0 % en 18-24, y cae de forma sostenida con la edad.",
            "Ambas fuentes", True),
    Reporte("P2", "Brecha estable entre hombres y mujeres",
            "Los hombres presentan mayores porcentajes de consumo en las cuatro sustancias. En UCI, el "
            "consumo reciente de marihuana es 55,6 % en hombres frente a 28,0 % en mujeres.",
            "Ambas fuentes", False),
    Reporte("P3", "Los rasgos se asocian a familias de sustancias",
            "La búsqueda de sensaciones se asocia a marihuana e inhalables, la apertura a la experiencia a "
            "los alucinógenos (LSD, hongos) y el neuroticismo al crack. Chocolate y cafeína quedan neutros "
            "como control.",
            "Muestra internacional UCI", True),
    Reporte("P4", "La impulsividad crece con la recencia de consumo",
            "El percentil promedio de impulsividad sube de 36,3 (nunca consumió marihuana) a 59,2 (últimos "
            "30 días), aunque con alto solapamiento entre grupos.",
            "Muestra internacional UCI", True),
    Reporte("P5", "El policonsumo se concentra en hombres jóvenes",
            "En Chile el policonsumo de 2 o más sustancias es máximo en hombres de 25-34 años (26,7 %) y baja "
            "hasta 7,7 % en hombres de 65+. En UCI llega a 86,0 % en hombres de 18-24.",
            "Ambas fuentes", True),
    Reporte("P5", "Perfil psicológico del policonsumo",
            "El grupo de 3-4 sustancias es el más alto en apertura (62,7), búsqueda de sensaciones (67,7) e "
            "impulsividad (61,8), y el más bajo en responsabilidad (40,5).",
            "Muestra internacional UCI", False),
]
