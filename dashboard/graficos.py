"""
Gráficos del dashboard. Cada función dibuja una figura con Matplotlib y devuelve
el PNG codificado en base64, igual que grafico1..grafico5 de las guías 4, 5 y 6.

La única diferencia con las guías es que el bloque BytesIO/base64, que antes se
repetía en cada vista, aquí está escrito una sola vez en figura_a_base64().
"""
import base64
from functools import lru_cache
from io import BytesIO

import matplotlib
matplotlib.use("Agg")  # Dibujar sin abrir una ventana gráfica (antes de pyplot)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

from . import analisis as an

GRIS = "#6B7280"
plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.edgecolor": "#C9CDD3",
    "axes.labelcolor": "#374151",
    "xtick.color": "#4B5563",
    "ytick.color": "#4B5563",
})


def figura_a_base64(figura, ajustar=True):
    """Guardar la figura como PNG en memoria y convertirla a texto base64."""
    if ajustar:
        figura.tight_layout()
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=110)
    plt.close(figura)  # Liberar la figura después de guardarla
    buffer.seek(0)
    grafico = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return grafico


def _fmt(valor):
    return f"{valor:.1f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Gráfico de BARRAS · P1 · Barras horizontales agrupadas (guías 4 y 6)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def grafico_barras():
    _, df_chile_18, df_mundo = an.obtener_datos()
    sustancias = list(an.SUSTANCIAS_COMPARABLES.keys())
    posiciones = np.arange(len(sustancias))
    alto = 0.38

    figura, ejes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
    for eje, (nombre_ventana, ventana) in zip(ejes, an.VENTANAS.items()):
        chile = [an.porcentaje_recencia(df_chile_18[c], ventana)[0]
                 for c in an.SUSTANCIAS_COMPARABLES.values()]
        uci = [an.porcentaje_recencia(df_mundo[c], ventana)[0]
               for c in an.SUSTANCIAS_COMPARABLES.values()]
        b1 = eje.barh(posiciones - alto / 2, chile, alto, color=an.COLOR_CHILE, label="Chile ENPG 2024")
        b2 = eje.barh(posiciones + alto / 2, uci, alto, color=an.COLOR_UCI, label="Muestra internacional UCI")
        eje.bar_label(b1, labels=[_fmt(v) + "%" for v in chile], padding=3, fontsize=8)
        eje.bar_label(b2, labels=[_fmt(v) + "%" for v in uci], padding=3, fontsize=8)
        eje.set_title(nombre_ventana)
        eje.set_xlim(0, 115)
        eje.set_xlabel("% de personas")
        eje.set_yticks(posiciones, sustancias)
        eje.invert_yaxis()
    ejes[0].legend(loc="lower right", fontsize=8, frameon=False)
    figura.suptitle("Recencia de consumo por sustancia y fuente (18+ años)", fontweight="bold")
    return figura_a_base64(figura)


# ---------------------------------------------------------------------------
# Gráfico de LÍNEAS · P2 · Consumo en los últimos 30 días por grupo de edad
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def grafico_lineas():
    _, df_chile_18, df_mundo = an.obtener_datos()
    ventana = an.VENTANAS["Últimos 30 días"]
    colores = {"Alcohol": "#73C96A", "Tabaco": "#969798", "Marihuana": an.COLOR_CHILE, "Cocaína": an.COLOR_UCI}

    figura, ejes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for eje, (nombre, df) in zip(ejes, [("Chile ENPG 2024", df_chile_18),
                                        ("Muestra internacional UCI", df_mundo)]):
        for sustancia, columna in an.SUSTANCIAS_COMPARABLES.items():
            valores = [an.porcentaje_recencia(df.loc[df["Grupo_Edad"] == g, columna], ventana)[0]
                       for g in an.ETIQUETAS_EDAD]
            eje.plot(an.ETIQUETAS_EDAD, valores, marker="o", linewidth=2,
                     color=colores[sustancia], label=sustancia)
        eje.set_title(nombre)
        eje.set_xlabel("Grupo de edad")
        eje.set_ylim(0, 100)
        eje.grid(True, alpha=0.3)
    ejes[0].set_ylabel("% con consumo en los últimos 30 días")
    ejes[0].legend(title="Sustancia", frameon=False, loc="upper right", ncol=2)
    figura.suptitle("Consumo en los últimos 30 días según grupo de edad", fontweight="bold")
    return figura_a_base64(figura)


# ---------------------------------------------------------------------------
# Gráfico 3 · P3 · Mapa de calor rasgo × sustancia
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def grafico_p3():
    _, _, df_mundo = an.obtener_datos()
    sustancias = list(an.SUSTANCIAS_UCI.items())
    matriz = np.zeros((len(sustancias), len(an.RASGOS)))
    for i, (_, columna) in enumerate(sustancias):
        consume = df_mundo[columna].isin(an.CLASES_RECIENTES)
        for j, rasgo in enumerate(an.RASGOS):
            percentil = df_mundo[rasgo + "_Percentil"]
            matriz[i, j] = percentil[consume].mean() - percentil[~consume].mean() if consume.any() else 0

    figura, eje = plt.subplots(figsize=(10, 8.5))
    imagen = eje.imshow(matriz, cmap="RdBu_r", norm=TwoSlopeNorm(vmin=-20, vcenter=0, vmax=20), aspect="auto")
    eje.set_xticks(range(len(an.RASGOS)), list(an.RASGOS.values()), rotation=30, ha="right")
    eje.set_yticks(range(len(sustancias)), [s for s, _ in sustancias])
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            valor = matriz[i, j]
            eje.text(j, i, f"{valor:+.0f}", ha="center", va="center", fontsize=8,
                     color="white" if abs(valor) > 13 else "#1F2937")
    barra = figura.colorbar(imagen, ax=eje, shrink=0.8)
    barra.set_label("Diferencia de percentil (consumidores − no consumidores)")
    eje.set_title("Brecha de personalidad entre quienes consumen (últimos 30 días) y quienes no (UCI)")
    for borde in eje.spines.values():
        borde.set_visible(False)
    return figura_a_base64(figura)


# ---------------------------------------------------------------------------
# Gráfico de DISPERSIÓN · P4 · Impulsividad vs búsqueda de sensaciones
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def grafico_dispersion():
    _, _, df_mundo = an.obtener_datos()
    colores = {"Nunca": "#969798", "Hace más de 1 año": "#73C96A",
               "Último año": an.COLOR_CHILE, "Últimos 30 días": an.COLOR_UCI}
    # Pequeño desplazamiento aleatorio (jitter): ambas escalas tienen pocos
    # valores posibles y sin él muchos puntos quedarían uno encima del otro
    rng = np.random.default_rng(42)

    figura, eje = plt.subplots(figsize=(10, 6))
    for nivel in an.ORDEN_RECENCIA:
        sub = df_mundo[df_mundo["Marihuana_Recencia"] == nivel]
        x = sub["Impulsividad_Percentil"] + rng.uniform(-3.5, 3.5, len(sub))
        y = sub["Busqueda_Sensaciones_Percentil"] + rng.uniform(-3, 3, len(sub))
        eje.scatter(x, y, s=16, alpha=0.6,
                    color=colores[nivel], edgecolors="none", label=f"{nivel} (n={len(sub)})")
    eje.set_xlim(-3, 103)
    eje.set_ylim(-3, 103)
    eje.set_xlabel("Percentil de impulsividad")
    eje.set_ylabel("Percentil de búsqueda de sensaciones")
    eje.set_title("Impulsividad y búsqueda de sensaciones por participante (UCI)")
    eje.grid(True, alpha=0.3)
    eje.legend(title="Último consumo de marihuana", frameon=False, loc="upper left",
               bbox_to_anchor=(1.01, 1), markerscale=1.6)
    return figura_a_base64(figura)


# ---------------------------------------------------------------------------
# Gráfico 5 · P5a · Burbujas edad × sexo (dispersión de la guía 5)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def grafico_p5a():
    _, df_chile_18, df_mundo = an.obtener_datos()
    figura, ejes = plt.subplots(1, 2, figsize=(13, 4.4), sharey=True)
    for eje, (nombre, df) in zip(ejes, [("Chile ENPG 2024", df_chile_18),
                                        ("Muestra internacional UCI", df_mundo)]):
        xs, ys, valores = [], [], []
        for i, grupo in enumerate(an.ETIQUETAS_EDAD):
            for j, sexo in enumerate(["Mujer", "Hombre"]):
                sub = df[(df["Grupo_Edad"] == grupo) & (df["Sexo"] == sexo)]
                pct = (sub["Policonsumo_30d"] >= 2).mean() * 100 if len(sub) else 0
                xs.append(i); ys.append(j); valores.append(pct)
        puntos = eje.scatter(xs, ys, s=[60 + v * 22 for v in valores], c=valores,
                             cmap="plasma", vmin=0, vmax=100, edgecolors="white", linewidths=1)
        for x, y, v in zip(xs, ys, valores):
            eje.annotate(_fmt(v) + "%", (x, y), textcoords="offset points", xytext=(0, -26),
                         ha="center", fontsize=8, color="#374151")
        eje.set_xticks(range(len(an.ETIQUETAS_EDAD)), an.ETIQUETAS_EDAD)
        eje.set_yticks([0, 1], ["Mujer", "Hombre"])
        eje.set_ylim(-0.7, 1.5)
        eje.set_xlim(-0.6, len(an.ETIQUETAS_EDAD) - 0.4)
        eje.set_xlabel("Grupo de edad")
        eje.set_title(nombre)
    figura.colorbar(puntos, ax=ejes, shrink=0.85, label="% con 2 o más sustancias (30 días)")
    figura.suptitle("Policonsumo (2 o más sustancias en los últimos 30 días) por edad y sexo", fontweight="bold")
    figura.subplots_adjust(left=0.06, right=0.82, bottom=0.14, top=0.85, wspace=0.08)
    return figura_a_base64(figura, ajustar=False)


# ---------------------------------------------------------------------------
# Gráfico 6 · P5b · Radar de perfil psicológico por nivel de policonsumo
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def grafico_p5b():
    _, _, df_mundo = an.obtener_datos()
    grupos = {
        "0 sustancias": (df_mundo["Policonsumo_30d"] == 0, "#969798"),
        "1 sustancia": (df_mundo["Policonsumo_30d"] == 1, "#73C96A"),
        "2 sustancias": (df_mundo["Policonsumo_30d"] == 2, an.COLOR_CHILE),
        "3 o 4 sustancias": (df_mundo["Policonsumo_30d"] >= 3, an.COLOR_UCI),
    }
    etiquetas = list(an.RASGOS.values())
    angulos = np.linspace(0, 2 * np.pi, len(etiquetas), endpoint=False).tolist()
    angulos += angulos[:1]  # Cerrar el polígono repitiendo el primer vértice

    figura, eje = plt.subplots(figsize=(8, 7), subplot_kw={"polar": True})
    for nombre, (filtro, color) in grupos.items():
        valores = [df_mundo.loc[filtro, r + "_Percentil"].mean() for r in an.RASGOS]
        valores += valores[:1]
        eje.plot(angulos, valores, color=color, linewidth=2, label=f"{nombre} (n={int(filtro.sum())})")
        eje.fill(angulos, valores, color=color, alpha=0.08)
    eje.set_xticks(angulos[:-1], etiquetas)
    eje.set_ylim(0, 80)
    eje.set_yticks([20, 40, 60, 80], ["20", "40", "60", "80"], color=GRIS, fontsize=8)
    eje.set_title("Perfil psicológico promedio (percentil) según nivel de policonsumo (UCI)", pad=24)
    eje.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False, fontsize=9)
    return figura_a_base64(figura)


# ---------------------------------------------------------------------------
# Gráfico circular del dashboard (guía 5) · Distribución del policonsumo
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def grafico_circular_policonsumo():
    _, df_chile_18, _ = an.obtener_datos()
    conteo = df_chile_18["Policonsumo_30d"].clip(upper=3).value_counts().sort_index()
    etiquetas = {0: "Ninguna", 1: "1 sustancia", 2: "2 sustancias", 3: "3 o 4"}
    figura, eje = plt.subplots(figsize=(5.5, 4.2))
    eje.pie(conteo.values, autopct=lambda p: f"{p:.1f}%" if p >= 3 else "",
            startangle=90, colors=["#C9CDD3", "#73C96A", an.COLOR_CHILE, an.COLOR_UCI][:len(conteo)],
            wedgeprops={"edgecolor": "white", "linewidth": 2}, pctdistance=0.78,
            textprops={"fontsize": 9})
    eje.axis("equal")  # Mantener el círculo sin deformaciones
    eje.legend([etiquetas[i] for i in conteo.index], loc="center left",
               bbox_to_anchor=(1, 0.5), frameon=False, fontsize=9)
    return figura_a_base64(figura)
