"""
Lectura y limpieza de los dos datasets guardados en SQLite.

obtener_datos() consulta las tablas con el ORM de Django, las convierte en DataFrames
y crea las variables derivadas (recencia, grupo de edad, percentiles y policonsumo).
Las funciones tabla_...() arman las tablas que usan los reportes.
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from .models import EncuestadoChile, ParticipanteUCI

COLOR_CHILE = "#406AB4"
COLOR_UCI = "#E25E6B"
FUENTE_CHILE = "Chile ENPG 2024"
FUENTE_UCI = "Muestra internacional UCI"

ORDEN_RECENCIA = ["Nunca", "Hace más de 1 año", "Último año", "Últimos 30 días"]
ETIQUETAS_EDAD = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
LIMITES_EDAD = [18, 25, 35, 45, 55, 65, np.inf]
SEXOS = ["Hombre", "Mujer"]

# Las ventanas son acumuladas: "Alguna vez" incluye a quienes consumieron el último año
VENTANAS = {
    "Últimos 30 días": ["Últimos 30 días"],
    "Último año": ["Últimos 30 días", "Último año"],
    "Alguna vez": ["Últimos 30 días", "Último año", "Hace más de 1 año"],
}

# Sustancias presentes en ambas fuentes y su columna de recencia
SUSTANCIAS_COMPARABLES = {
    "Alcohol": "alcohol_recencia",
    "Tabaco": "tabaco_recencia",
    "Marihuana": "marihuana_recencia",
    "Cocaína": "cocaina_recencia",
}
COLUMNAS_RECENCIA = list(SUSTANCIAS_COMPARABLES.values())

SUSTANCIAS_UCI = {
    "Alcohol": "alcohol", "Marihuana": "marihuana", "Cocaína": "cocaina",
    "Tabaco / Nicotina": "tabaco_nicotina", "Anfetaminas": "anfetaminas",
    "Benzodiazepinas": "benzodiazepinas", "Éxtasis": "extasis", "LSD": "lsd",
    "Hongos alucinógenos": "hongos_alucinogenos", "Ketamina": "ketamina",
    "Metanfetaminas": "metanfetaminas", "Heroína": "heroina", "Crack": "crack",
    "Drogas sintéticas": "drogas_sinteticas", "Poppers": "poppers",
    "Inhalables volátiles": "inhalables_volatiles", "Cafeína": "cafeina",
    "Chocolate": "chocolate",
}
# UCI codifica la recencia de CL0 (nunca) a CL6 (último día)
CLASES_RECIENTES = ["CL4", "CL5", "CL6"]

RASGOS = {
    "neuroticismo": "Neuroticismo", "extraversion": "Extraversión",
    "apertura_experiencia": "Apertura", "amabilidad": "Amabilidad",
    "responsabilidad": "Responsabilidad", "impulsividad": "Impulsividad",
    "busqueda_sensaciones": "Búsqueda de sensaciones",
}

NIVELES_POLICONSUMO = {
    "0 sustancias": lambda cantidad: cantidad == 0,
    "1 sustancia": lambda cantidad: cantidad == 1,
    "2 sustancias": lambda cantidad: cantidad == 2,
    "3 o 4 sustancias": lambda cantidad: cantidad >= 3,
}

FILTROS_INICIALES = {"sustancia": "Marihuana", "ventana": "Últimos 30 días", "sexo": "Todos",
                     "edad_desde": ETIQUETAS_EDAD[0], "edad_hasta": ETIQUETAS_EDAD[-1]}


class DatosNoEncontrados(Exception):
    """Se lanza cuando una tabla de la base de datos todavía no tiene registros."""


def _leer_tabla(modelo):
    df = pd.DataFrame(list(modelo.objects.values()))
    if df.empty:
        raise DatosNoEncontrados(modelo._meta.verbose_name_plural)
    return df


def _contar_policonsumo(df):
    return sum((df[columna] == "Últimos 30 días").astype(int) for columna in COLUMNAS_RECENCIA)


# ---------------------------------------------------------------------------
# Dataset internacional (UCI)
# ---------------------------------------------------------------------------
def _preparar_uci():
    df = _leer_tabla(ParticipanteUCI)

    for rasgo in RASGOS:
        df[rasgo + "_percentil"] = (df[rasgo].rank(pct=True) * 100).round(1)

    # UCI publica edad y género como códigos numéricos
    codigos_edad = {-0.95197: "18-24", -0.07854: "25-34", 0.49788: "35-44",
                    1.09449: "45-54", 1.82213: "55-64", 2.59171: "65+"}
    df["grupo_edad"] = df["edad"].round(5).map(codigos_edad)
    df["sexo"] = df["genero"].round(5).map({-0.48246: "Hombre", 0.48246: "Mujer"})

    # Las 7 clases de UCI se reducen a los 4 niveles comparables con Chile
    clases_a_recencia = {"CL0": "Nunca", "CL1": "Hace más de 1 año",
                         "CL2": "Hace más de 1 año", "CL3": "Último año",
                         "CL4": "Últimos 30 días", "CL5": "Últimos 30 días",
                         "CL6": "Últimos 30 días"}
    for sustancia in ["alcohol", "marihuana", "cocaina"]:
        df[sustancia + "_recencia"] = df[sustancia].map(clases_a_recencia)
    df["tabaco_recencia"] = df["tabaco_nicotina"].map(clases_a_recencia)

    df["policonsumo_30d"] = _contar_policonsumo(df)
    return df


# ---------------------------------------------------------------------------
# Dataset Chile (ENPG 2024)
# ---------------------------------------------------------------------------
def _recencia_chile(alguna_vez, ultima_vez):
    """Combina las dos preguntas de la encuesta. Queda vacío (NaN) si no sabe o no contesta."""
    recencia = pd.Series(np.nan, index=alguna_vez.index, dtype="object")
    recencia[alguna_vez == "No"] = "Nunca"
    recencia[ultima_vez == "Hace más de un año"] = "Hace más de 1 año"
    recencia[ultima_vez == "Hace más de un mes, pero menos de un año"] = "Último año"
    recencia[ultima_vez == "Durante los últimos 30 días"] = "Últimos 30 días"
    return recencia


def _preparar_chile():
    df = _leer_tabla(EncuestadoChile)
    df["sexo"] = df["sexo"].str.strip().str.title()
    for sustancia in ["alcohol", "marihuana", "cocaina", "tabaco"]:
        df[sustancia + "_recencia"] = _recencia_chile(
            df[sustancia + "_alguna_vez"], df[sustancia + "_ultima_vez"])
    df["grupo_edad"] = pd.cut(df["edad"], bins=LIMITES_EDAD,
                              labels=ETIQUETAS_EDAD, right=False).astype("object")
    df["policonsumo_30d"] = _contar_policonsumo(df)
    return df


@lru_cache(maxsize=1)
def obtener_datos():
    """Devuelve (df_chile, df_chile_18, df_uci). lru_cache guarda el resultado para
    consultar la base una sola vez mientras el servidor esté encendido."""
    df_uci = _preparar_uci()
    df_chile = _preparar_chile()
    df_chile_18 = df_chile[df_chile["edad"] >= 18].copy()
    return df_chile, df_chile_18, df_uci


def porcentaje_recencia(serie, ventana):
    """Devuelve (% que consumió dentro de la ventana, respuestas válidas)."""
    validos = serie.dropna()
    if len(validos) == 0:
        return 0.0, 0
    return float(round(validos.isin(ventana).mean() * 100, 1)), len(validos)


def _porcentaje_policonsumo(df):
    return float(round((df["policonsumo_30d"] >= 2).mean() * 100, 1))


def indicadores():
    """Indicadores (KPI) de la parte superior del dashboard."""
    df_chile, df_chile_18, df_uci = obtener_datos()
    ultimos_30_dias = VENTANAS["Últimos 30 días"]
    return {
        "encuestados_chile": len(df_chile),
        "participantes_uci": len(df_uci),
        "poblacion_millones": float(df_chile["factor_expansion"].sum() / 1_000_000),
        "alcohol_30d": porcentaje_recencia(df_chile_18["alcohol_recencia"], ultimos_30_dias)[0],
        "marihuana_30d": porcentaje_recencia(df_chile_18["marihuana_recencia"], ultimos_30_dias)[0],
        "poli_chile": _porcentaje_policonsumo(df_chile_18),
        "poli_uci": _porcentaje_policonsumo(df_uci),
    }


# ---------------------------------------------------------------------------
# Tablas de los reportes: cada función devuelve (columnas, filas)
# ---------------------------------------------------------------------------
def tabla_recencia():
    """Reporte 1: % de personas por ventana de recencia, sustancia y fuente."""
    _, df_chile_18, df_uci = obtener_datos()
    filas = []
    for sustancia, columna in SUSTANCIAS_COMPARABLES.items():
        for fuente, df in [(FUENTE_CHILE, df_chile_18), (FUENTE_UCI, df_uci)]:
            _, validos = porcentaje_recencia(df[columna], VENTANAS["Alguna vez"])
            porcentajes = [porcentaje_recencia(df[columna], ventana)[0] for ventana in VENTANAS.values()]
            filas.append([sustancia, fuente, validos] + porcentajes)
    columnas = ["Sustancia", "Fuente", "Respuestas válidas"] + [v + " (%)" for v in VENTANAS]
    return columnas, filas


def tabla_edad_sexo():
    """Reporte 2: consumo en los últimos 30 días por grupo de edad y sexo (Chile 18+)."""
    _, df_chile_18, _ = obtener_datos()
    filas = []
    for grupo in ETIQUETAS_EDAD:
        for sexo in SEXOS:
            personas = df_chile_18[(df_chile_18["grupo_edad"] == grupo) & (df_chile_18["sexo"] == sexo)]
            porcentajes = [porcentaje_recencia(personas[columna], VENTANAS["Últimos 30 días"])[0]
                           for columna in COLUMNAS_RECENCIA]
            filas.append([grupo, sexo, len(personas)] + porcentajes + [_porcentaje_policonsumo(personas)])
    columnas = (["Grupo de edad", "Sexo", "Personas"]
                + [sustancia + " (%)" for sustancia in SUSTANCIAS_COMPARABLES] + ["2 o más sustancias (%)"])
    return columnas, filas


def tabla_perfil_psicologico():
    """Reporte 3: percentil promedio de cada rasgo según nivel de policonsumo (UCI)."""
    _, _, df_uci = obtener_datos()
    filas = []
    for nivel, pertenece in NIVELES_POLICONSUMO.items():
        participantes = df_uci[pertenece(df_uci["policonsumo_30d"])]
        promedios = [float(round(participantes[rasgo + "_percentil"].mean(), 1)) for rasgo in RASGOS]
        filas.append([nivel, len(participantes)] + promedios)
    columnas = ["Nivel de policonsumo", "Participantes"] + list(RASGOS.values())
    return columnas, filas


def tabla_consumo_filtrado(sustancia, ventana, sexo, edad_desde, edad_hasta):
    """Reporte 4 y gráfico dinámico: consumo por grupo de edad y fuente según los filtros.
    Si la selección no tiene personas, la lista de filas queda vacía."""
    _, df_chile_18, df_uci = obtener_datos()
    columna = SUSTANCIAS_COMPARABLES[sustancia]
    grupos = ETIQUETAS_EDAD[ETIQUETAS_EDAD.index(edad_desde):ETIQUETAS_EDAD.index(edad_hasta) + 1]
    filas = []
    for grupo in grupos:
        for fuente, df in [(FUENTE_CHILE, df_chile_18), (FUENTE_UCI, df_uci)]:
            personas = df[df["grupo_edad"] == grupo]
            if sexo != "Todos":
                personas = personas[personas["sexo"] == sexo]
            porcentaje, validos = porcentaje_recencia(personas[columna], VENTANAS[ventana])
            if validos > 0:
                consumidores = int(personas[columna].isin(VENTANAS[ventana]).sum())
                filas.append([grupo, fuente, validos, consumidores, porcentaje])
    columnas = ["Grupo de edad", "Fuente", "Respuestas válidas", "Consumidores", "Consumo (%)"]
    return columnas, filas
