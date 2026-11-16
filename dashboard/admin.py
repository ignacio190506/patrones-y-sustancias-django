from django.contrib import admin

from .models import EncuestadoChile, ParticipanteUCI


@admin.register(EncuestadoChile)
class EncuestadoChileAdmin(admin.ModelAdmin):
    list_display = ["id_encuestado", "edad", "sexo", "region"]
    list_filter = ["sexo", "region"]


@admin.register(ParticipanteUCI)
class ParticipanteUCIAdmin(admin.ModelAdmin):
    list_display = ["id_participante", "alcohol", "tabaco_nicotina", "marihuana", "cocaina"]
