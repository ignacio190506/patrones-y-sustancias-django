from django.db import models


class EncuestadoChile(models.Model):
    """Una persona encuestada en la ENPG 2024 de SENDA."""
    id_encuestado = models.IntegerField(primary_key=True)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=10)
    region = models.CharField(max_length=30)
    factor_expansion = models.FloatField()
    tabaco_alguna_vez = models.CharField(max_length=20)
    tabaco_ultima_vez = models.CharField(max_length=50, blank=True)
    alcohol_alguna_vez = models.CharField(max_length=20)
    alcohol_ultima_vez = models.CharField(max_length=50, blank=True)
    marihuana_alguna_vez = models.CharField(max_length=20)
    marihuana_ultima_vez = models.CharField(max_length=50, blank=True)
    cocaina_alguna_vez = models.CharField(max_length=20)
    cocaina_ultima_vez = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "encuestado Chile (ENPG 2024)"
        verbose_name_plural = "encuestados Chile (ENPG 2024)"


class ParticipanteUCI(models.Model):
    """Un participante del dataset Drug Consumption (UCI).
    Los campos siguen el mismo orden que las columnas del archivo original."""
    id_participante = models.IntegerField(primary_key=True)
    edad = models.FloatField()
    genero = models.FloatField()
    nivel_educacion = models.FloatField()
    pais = models.FloatField()
    etnia = models.FloatField()
    neuroticismo = models.FloatField()
    extraversion = models.FloatField()
    apertura_experiencia = models.FloatField()
    amabilidad = models.FloatField()
    responsabilidad = models.FloatField()
    impulsividad = models.FloatField()
    busqueda_sensaciones = models.FloatField()
    alcohol = models.CharField(max_length=3)
    anfetaminas = models.CharField(max_length=3)
    poppers = models.CharField(max_length=3)
    benzodiazepinas = models.CharField(max_length=3)
    cafeina = models.CharField(max_length=3)
    marihuana = models.CharField(max_length=3)
    chocolate = models.CharField(max_length=3)
    cocaina = models.CharField(max_length=3)
    crack = models.CharField(max_length=3)
    extasis = models.CharField(max_length=3)
    heroina = models.CharField(max_length=3)
    ketamina = models.CharField(max_length=3)
    drogas_sinteticas = models.CharField(max_length=3)
    lsd = models.CharField(max_length=3)
    metanfetaminas = models.CharField(max_length=3)
    hongos_alucinogenos = models.CharField(max_length=3)
    tabaco_nicotina = models.CharField(max_length=3)
    droga_ficticia_control = models.CharField(max_length=3)
    inhalables_volatiles = models.CharField(max_length=3)

    class Meta:
        verbose_name = "participante UCI"
        verbose_name_plural = "participantes UCI"
