import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard.models import EncuestadoChile, ParticipanteUCI

COLUMNAS_CHILE = {
    "RESPONDENT_SERIAL": "id_encuestado", "EDAD": "edad", "SEXO": "sexo",
    "REGION": "region", "FACTOR_EXPANSION": "factor_expansion",
    "ST_2": "tabaco_alguna_vez", "ST_5": "tabaco_ultima_vez",
    "OH_1": "alcohol_alguna_vez", "OH_4": "alcohol_ultima_vez",
    "MAR_1": "marihuana_alguna_vez", "MAR_4": "marihuana_ultima_vez",
    "COC_1": "cocaina_alguna_vez", "COC_4": "cocaina_ultima_vez",
}
# El archivo UCI no trae encabezados: sus columnas siguen el orden del modelo
CAMPOS_UCI = [campo.name for campo in ParticipanteUCI._meta.fields]


def leer_encuestados_chile():
    ruta = settings.CARPETA_DATOS / "enpg_2024_reducida.csv"
    with open(ruta, encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            datos = {campo: fila[columna] for columna, campo in COLUMNAS_CHILE.items()}
            # El CSV guarda estos enteros con decimal ("63.0")
            datos["id_encuestado"] = int(float(datos["id_encuestado"]))
            datos["edad"] = int(float(datos["edad"]))
            yield EncuestadoChile(**datos)


def leer_participantes_uci():
    ruta = settings.CARPETA_DATOS / "drug_consumption.data"
    with open(ruta, encoding="utf-8", newline="") as archivo:
        for fila in csv.reader(archivo):
            yield ParticipanteUCI(**dict(zip(CAMPOS_UCI, fila)))


class Command(BaseCommand):
    help = "Carga los dos datasets de la carpeta datos/ en la base de datos SQLite."

    def handle(self, *args, **opciones):
        # Si algo falla, la transacción deja la base como estaba
        with transaction.atomic():
            EncuestadoChile.objects.all().delete()
            ParticipanteUCI.objects.all().delete()
            EncuestadoChile.objects.bulk_create(leer_encuestados_chile(), batch_size=500)
            ParticipanteUCI.objects.bulk_create(leer_participantes_uci(), batch_size=500)
        self.stdout.write(self.style.SUCCESS(
            f"Datos cargados: {EncuestadoChile.objects.count()} encuestados de Chile "
            f"y {ParticipanteUCI.objects.count()} participantes UCI."))
