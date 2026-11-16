from django import forms

from . import analisis


def _opciones(valores):
    return [(valor, valor) for valor in valores]


class FiltroConsumoForm(forms.Form):
    """Filtros compartidos por el gráfico dinámico y el reporte 4."""
    sustancia = forms.ChoiceField(choices=_opciones(analisis.SUSTANCIAS_COMPARABLES))
    ventana = forms.ChoiceField(label="Periodo de consumo", choices=_opciones(analisis.VENTANAS))
    sexo = forms.ChoiceField(choices=_opciones(["Todos"] + analisis.SEXOS))
    edad_desde = forms.ChoiceField(label="Edad desde", choices=_opciones(analisis.ETIQUETAS_EDAD))
    edad_hasta = forms.ChoiceField(label="Edad hasta", choices=_opciones(analisis.ETIQUETAS_EDAD))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-select"

    def resumen(self):
        """Texto con la selección vigente, para mostrarla en pantalla y en el PDF."""
        return " · ".join(f"{campo.label}: {campo.value()}" for campo in self)


def leer_filtros(parametros):
    """Valida los filtros de la URL. Si faltan o no son válidos, usa los iniciales."""
    form = FiltroConsumoForm(parametros)
    if not form.is_valid():
        form = FiltroConsumoForm(analisis.FILTROS_INICIALES)
        form.is_valid()
    return form, form.cleaned_data
