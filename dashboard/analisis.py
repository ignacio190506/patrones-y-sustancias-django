"""
Carga y limpieza de los dos datasets del notebook Proyecto_Nuevo.ipynb.

Este archivo reúne, en un solo lugar, la limpieza que el notebook hace paso a paso:
renombrar columnas, estandarizar categorías, decodificar el dataset UCI, crear la
variable de recencia y el índice de policonsumo. Las vistas solo llaman a
obtener_datos() y reciben los dos DataFrames listos para graficar.
"""
from functools import lru_cache

import numpy as np
import pandas as pd
from django.conf import settings

ARCHIVO_MUNDO = "drug_consumption.data"
ARCHIVO_CHILE = "Base_Publica_ENPG_2024.dta"
ARCHIVO_CHILE_CSV = "enpg_2024_reducida.csv"

# ---------------------------------------------------------------------------
# Constantes compartidas (las mismas del notebook)
# ---------------------------------------------------------------------------
COLOR_CHILE = "#406AB4"
COLOR_UCI = "#E25E6B"
FUENTES = {"Chile ENPG 2024": COLOR_CHILE, "Muestra internacional UCI": COLOR_UCI}

ORDEN_RECENCIA = ["Nunca", "Hace más de 1 año", "Último año", "Últimos 30 días"]
ETIQUETAS_EDAD = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
LIMITES_EDAD = [18, 25, 35, 45, 55, 65, np.inf]

VENTANAS = {
    "Últimos 30 días": ["Últimos 30 días"],
    "Último año": ["Últimos 30 días", "Último año"],
    "Alguna vez": ["Últimos 30 días", "Último año", "Hace más de 1 año"],
}

SUSTANCIAS_COMPARABLES = {
    "Alcohol": "Alcohol_Recencia",
    "Tabaco": "Tabaco_Recencia",
    "Marihuana": "Marihuana_Recencia",
    "Cocaína": "Cocaina_Recencia",
}
COLUMNAS_RECENCIA = list(SUSTANCIAS_COMPARABLES.values())

SUSTANCIAS_UCI = {
    "Alcohol": "Alcohol", "Marihuana": "Marihuana", "Cocaína": "Cocaina",
    "Tabaco / Nicotina": "Tabaco_Nicotina", "Anfetaminas": "Anfetaminas",
    "Benzodiazepinas": "Benzodiazepinas", "Éxtasis": "Extasis", "LSD": "LSD",
    "Hongos alucinógenos": "Hongos_Alucinogenos", "Ketamina": "Ketamina",
    "Metanfetaminas": "Metanfetaminas", "Heroína": "Heroina", "Crack": "Crack",
    "Drogas sintéticas": "Drogas_Sinteticas", "Poppers": "Poppers",
    "Inhalables volátiles": "Inhalables_Volatiles", "Cafeína": "Cafeina",
    "Chocolate": "Chocolate",
}
CLASES_RECIENTES = ["CL4", "CL5", "CL6"]
CLASES_ULTIMO_ANO = ["CL3", "CL4", "CL5", "CL6"]
CLASES_ALGUNA_VEZ = ["CL1", "CL2", "CL3", "CL4", "CL5", "CL6"]

RASGOS = {
    "Neuroticismo": "Neuroticismo", "Extraversion": "Extraversión",
    "Apertura_Experiencia": "Apertura", "Amabilidad": "Amabilidad",
    "Responsabilidad": "Responsabilidad", "Impulsividad": "Impulsividad",
    "Busqueda_Sensaciones": "Búsqueda de sensaciones",
}

EDUCACION_ORDEN = ["Secundaria o menor", "Superior incompleta / técnica",
                   "Universitaria", "Posgrado"]


class DatosNoEncontrados(Exception):
    """Se lanza cuando falta alguno de los archivos en la carpeta datos/."""


# ---------------------------------------------------------------------------
# Dataset internacional (UCI)
# ---------------------------------------------------------------------------
def _cargar_mundo():
    nombres_columnas = [
        "id", "age", "gender", "education", "country", "ethnicity",
        "nscore", "escore", "oscore", "ascore", "cscore", "impulsive", "ss",
        "Alcohol", "Amphet", "Amyl", "Benzos", "Caff", "Cannabis", "Choc",
        "Coke", "Crack", "Ecstasy", "Heroin", "Ketamine", "Legalh", "LSD",
        "Meth", "Mushrooms", "Nicotine", "Semer", "VSA",
    ]
    ruta = settings.CARPETA_DATOS / ARCHIVO_MUNDO
    if not ruta.exists():
        raise DatosNoEncontrados(ARCHIVO_MUNDO)
    df = pd.read_csv(ruta, header=None, names=nombres_columnas)

    df = df.rename(columns={
        "id": "ID_Participante", "age": "Edad", "gender": "Genero",
        "education": "Nivel_Educacion", "country": "Pais", "ethnicity": "Etnia",
        "nscore": "Neuroticismo", "escore": "Extraversion",
        "oscore": "Apertura_Experiencia", "ascore": "Amabilidad",
        "cscore": "Responsabilidad", "impulsive": "Impulsividad",
        "ss": "Busqueda_Sensaciones", "Amphet": "Anfetaminas", "Amyl": "Poppers",
        "Benzos": "Benzodiazepinas", "Caff": "Cafeina", "Cannabis": "Marihuana",
        "Choc": "Chocolate", "Coke": "Cocaina", "Ecstasy": "Extasis",
        "Heroin": "Heroina", "Ketamine": "Ketamina", "Legalh": "Drogas_Sinteticas",
        "Meth": "Metanfetaminas", "Mushrooms": "Hongos_Alucinogenos",
        "Nicotine": "Tabaco_Nicotina", "Semer": "Droga_Ficticia_Control",
        "VSA": "Inhalables_Volatiles",
    })

    # Puntajes psicológicos: z-score -> percentil (0 a 100)
    for rasgo in RASGOS:
        df[rasgo + "_Percentil"] = (df[rasgo].rank(pct=True) * 100).round(1)

    # Decodificar edad, sexo y educación
    mapa_edad = {-0.95197: "18-24", -0.07854: "25-34", 0.49788: "35-44",
                 1.09449: "45-54", 1.82213: "55-64", 2.59171: "65+"}
    df["Grupo_Edad"] = df["Edad"].round(5).map(mapa_edad)
    df["Sexo"] = df["Genero"].round(5).map({-0.48246: "Hombre", 0.48246: "Mujer"})
    mapa_educacion = {
        -2.43591: "Secundaria o menor", -1.73790: "Secundaria o menor",
        -1.43719: "Secundaria o menor", -1.22751: "Secundaria o menor",
        -0.61113: "Superior incompleta / técnica",
        -0.05921: "Superior incompleta / técnica",
        0.45468: "Universitaria", 1.16365: "Posgrado", 1.98437: "Posgrado",
    }
    df["Educacion_Comun"] = df["Nivel_Educacion"].round(5).map(mapa_educacion)

    # Recencia comparable con Chile (CL0..CL6 -> 4 niveles)
    mapa_recencia = {"CL0": "Nunca", "CL1": "Hace más de 1 año",
                     "CL2": "Hace más de 1 año", "CL3": "Último año",
                     "CL4": "Últimos 30 días", "CL5": "Últimos 30 días",
                     "CL6": "Últimos 30 días"}
    equivalencias = {"Alcohol_Recencia": "Alcohol", "Marihuana_Recencia": "Marihuana",
                     "Cocaina_Recencia": "Cocaina", "Tabaco_Recencia": "Tabaco_Nicotina"}
    for destino, origen in equivalencias.items():
        df[destino] = df[origen].map(mapa_recencia)

    df["Policonsumo_30d"] = sum(
        (df[c] == "Últimos 30 días").astype(int) for c in COLUMNAS_RECENCIA)
    return df


# ---------------------------------------------------------------------------
# Dataset Chile (ENPG 2024)
# ---------------------------------------------------------------------------
def _crear_recencia_chile(alguna_vez, ultima_vez):
    resultado = pd.Series(np.nan, index=alguna_vez.index, dtype="object")
    resultado[alguna_vez == "No"] = "Nunca"
    resultado[ultima_vez == "Hace más de un año"] = "Hace más de 1 año"
    resultado[ultima_vez == "Hace más de un mes, pero menos de un año"] = "Último año"
    resultado[ultima_vez == "Durante los últimos 30 días"] = "Últimos 30 días"
    return resultado


def _cargar_chile():
    columnas = ["RESPONDENT_SERIAL", "EDAD", "SEXO", "REGION", "FACTOR_EXPANSION",
                "ST_2", "ST_5", "OH_1", "OH_4", "MAR_1", "MAR_4", "COC_1", "COC_4"]
    ruta_dta = settings.CARPETA_DATOS / ARCHIVO_CHILE
    ruta_csv = settings.CARPETA_DATOS / ARCHIVO_CHILE_CSV
    if ruta_csv.exists():
        # Versión reducida (solo las 13 columnas usadas) para poder subirla a GitHub
        df = pd.read_csv(ruta_csv, encoding="utf-8")
    elif ruta_dta.exists():
        # columns= lee solo lo necesario: la base completa tiene 402 columnas
        df = pd.read_stata(ruta_dta, columns=columnas)
    else:
        raise DatosNoEncontrados(ARCHIVO_CHILE_CSV)
    df = df.drop_duplicates(subset=["RESPONDENT_SERIAL"])
    df = df.rename(columns={
        "RESPONDENT_SERIAL": "ID_Encuestado", "EDAD": "Edad", "SEXO": "Sexo",
        "REGION": "Region", "FACTOR_EXPANSION": "Factor_Expansion",
        "ST_2": "Tabaco_Alguna_Vez", "ST_5": "Tabaco_Ultima_Vez",
        "OH_1": "Alcohol_Alguna_Vez", "OH_4": "Alcohol_Ultima_Vez",
        "MAR_1": "Marihuana_Alguna_Vez", "MAR_4": "Marihuana_Ultima_Vez",
        "COC_1": "Cocaina_Alguna_Vez", "COC_4": "Cocaina_Ultima_Vez",
    })

    df["Edad"] = pd.to_numeric(df["Edad"], errors="coerce")
    df["Sexo"] = df["Sexo"].astype("object").str.strip().str.title()
    for columna in [c for c in df.columns if "_Alguna_Vez" in c or "_Ultima_Vez" in c]:
        df[columna] = (df[columna].astype("object")
                       .replace({"No sabe": "Sin información",
                                 "No contesta": "Sin información"}))

    for sustancia in ["Alcohol", "Marihuana", "Cocaina", "Tabaco"]:
        df[sustancia + "_Recencia"] = _crear_recencia_chile(
            df[sustancia + "_Alguna_Vez"], df[sustancia + "_Ultima_Vez"])

    df["Grupo_Edad"] = pd.cut(df["Edad"], bins=LIMITES_EDAD,
                              labels=ETIQUETAS_EDAD, right=False).astype("object")
    df["Policonsumo_30d"] = sum(
        (df[c] == "Últimos 30 días").astype(int) for c in COLUMNAS_RECENCIA)
    return df


@lru_cache(maxsize=1)
def obtener_datos():
    """Devuelve (df_chile, df_chile_18, df_mundo). Se calcula una sola vez
    mientras el servidor esté encendido, porque leer el .dta toma varios segundos."""
    df_mundo = _cargar_mundo()
    df_chile = _cargar_chile()
    df_chile_18 = df_chile[df_chile["Edad"] >= 18].copy()
    return df_chile, df_chile_18, df_mundo


# ---------------------------------------------------------------------------
# Funciones de porcentaje (iguales a las del notebook)
# ---------------------------------------------------------------------------
def porcentaje_recencia(serie, ventana):
    validos = serie.dropna()
    if len(validos) == 0:
        return 0.0, 0
    return round(validos.isin(ventana).mean() * 100, 1), int(len(validos))


def porcentaje_uci(serie, clases=CLASES_RECIENTES):
    validos = serie.dropna()
    if len(validos) == 0:
        return 0.0, 0
    return round(validos.isin(clases).mean() * 100, 1), int(len(validos))


def indicadores():
    """KPIs que se muestran en la parte superior del dashboard."""
    df_chile, df_chile_18, df_mundo = obtener_datos()
    alcohol_cl, _ = porcentaje_recencia(df_chile_18["Alcohol_Recencia"], VENTANAS["Últimos 30 días"])
    marihuana_cl, _ = porcentaje_recencia(df_chile_18["Marihuana_Recencia"], VENTANAS["Últimos 30 días"])
    poli_cl = round((df_chile_18["Policonsumo_30d"] >= 2).mean() * 100, 1)
    poli_uci = round((df_mundo["Policonsumo_30d"] >= 2).mean() * 100, 1)
    return {
        "encuestados_chile": f"{len(df_chile):,}".replace(",", "."),
        "participantes_uci": f"{len(df_mundo):,}".replace(",", "."),
        "poblacion": f"{df_chile['Factor_Expansion'].sum() / 1_000_000:.1f}".replace(".", ","),
        "alcohol_30d": str(alcohol_cl).replace(".", ","),
        "marihuana_30d": str(marihuana_cl).replace(".", ","),
        "poli_chile": str(poli_cl).replace(".", ","),
        "poli_uci": str(poli_uci).replace(".", ","),
    }


# ---------------------------------------------------------------------------
# Listados de datos (tablas que las vistas envían a las plantillas)
# ---------------------------------------------------------------------------
def _num(valor):
    return f"{valor:.1f}".replace(".", ",")


def listado_recencia():
    """Listado 1: % de personas por ventana de recencia, sustancia y fuente."""
    _, df_chile_18, df_mundo = obtener_datos()
    filas = []
    for sustancia, columna in SUSTANCIAS_COMPARABLES.items():
        for fuente, df in [("Chile ENPG 2024", df_chile_18), ("Muestra internacional UCI", df_mundo)]:
            pct_30, n = porcentaje_recencia(df[columna], VENTANAS["Últimos 30 días"])
            pct_ano, _ = porcentaje_recencia(df[columna], VENTANAS["Último año"])
            pct_vida, _ = porcentaje_recencia(df[columna], VENTANAS["Alguna vez"])
            filas.append([sustancia, fuente, f"{n:,}".replace(",", "."),
                          _num(pct_30) + " %", _num(pct_ano) + " %", _num(pct_vida) + " %"])
    columnas = ["Sustancia", "Fuente", "Respuestas válidas",
                "Últimos 30 días", "Último año", "Alguna vez"]
    return columnas, filas


def listado_edad_sexo():
    """Listado 2: consumo en los últimos 30 días por grupo de edad y sexo (Chile 18+)."""
    _, df_chile_18, _ = obtener_datos()
    filas = []
    for grupo in ETIQUETAS_EDAD:
        for sexo in ["Hombre", "Mujer"]:
            sub = df_chile_18[(df_chile_18["Grupo_Edad"] == grupo) & (df_chile_18["Sexo"] == sexo)]
            fila = [grupo, sexo, f"{len(sub):,}".replace(",", ".")]
            for columna in SUSTANCIAS_COMPARABLES.values():
                pct, _ = porcentaje_recencia(sub[columna], VENTANAS["Últimos 30 días"])
                fila.append(_num(pct) + " %")
            fila.append(_num((sub["Policonsumo_30d"] >= 2).mean() * 100) + " %")
            filas.append(fila)
    columnas = ["Grupo de edad", "Sexo", "Personas"] + list(SUSTANCIAS_COMPARABLES.keys()) + ["2+ sustancias"]
    return columnas, filas


def listado_perfil_psicologico():
    """Listado 3: percentil promedio de cada rasgo según nivel de policonsumo (UCI)."""
    _, _, df_mundo = obtener_datos()
    grupos = {
        "0 sustancias": df_mundo["Policonsumo_30d"] == 0,
        "1 sustancia": df_mundo["Policonsumo_30d"] == 1,
        "2 sustancias": df_mundo["Policonsumo_30d"] == 2,
        "3 o 4 sustancias": df_mundo["Policonsumo_30d"] >= 3,
    }
    filas = []
    for nombre, filtro in grupos.items():
        fila = [nombre, str(int(filtro.sum()))]
        for rasgo in RASGOS:
            fila.append(_num(df_mundo.loc[filtro, rasgo + "_Percentil"].mean()))
        filas.append(fila)
    columnas = ["Nivel de policonsumo", "Participantes"] + list(RASGOS.values())
    return columnas, filas
