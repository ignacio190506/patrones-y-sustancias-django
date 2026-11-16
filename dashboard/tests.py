from io import BytesIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from . import analisis
from .reportes import REPORTES

FILTROS = {"sustancia": "Alcohol", "ventana": "Alguna vez", "sexo": "Mujer",
           "edad_desde": "25-34", "edad_hasta": "45-54"}
FILTROS_SIN_DATOS = dict(FILTROS, edad_desde="65+", edad_hasta="18-24")


def contenido(respuesta):
    return b"".join(respuesta.streaming_content)


class SinDatosTests(TestCase):
    def test_tablas_vacias_muestran_como_cargar_los_datos(self):
        analisis.obtener_datos.cache_clear()
        respuesta = self.client.get(reverse("index"))
        self.assertContains(respuesta, "cargar_datos", status_code=503)


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_datos", verbosity=0)
        analisis.obtener_datos.cache_clear()

    def test_inicio_y_siete_graficos_responden(self):
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)
        for numero in range(1, 8):
            respuesta = self.client.get(reverse(f"grafico{numero}"))
            self.assertContains(respuesta, "data:image/png;base64")
            self.assertContains(respuesta, "Ver reporte")

    def test_cada_reporte_tiene_tabla_explicacion_y_botones(self):
        for numero, reporte in REPORTES.items():
            respuesta = self.client.get(reverse("reporte", args=[numero]))
            self.assertContains(respuesta, reporte.titulo)
            self.assertContains(respuesta, "Origen de los datos")
            self.assertContains(respuesta, "Descarga en PDF")
            self.assertContains(respuesta, "Descarga en Excel")

    def test_reporte_inexistente_devuelve_404(self):
        self.assertEqual(self.client.get(reverse("reporte", args=[9])).status_code, 404)

    def test_pdf_valido_en_cada_reporte(self):
        for numero in REPORTES:
            respuesta = self.client.get(reverse("reporte_pdf", args=[numero]))
            self.assertEqual(respuesta["Content-Type"], "application/pdf")
            self.assertTrue(contenido(respuesta).startswith(b"%PDF"))

    def test_excel_coincide_con_la_tabla_y_guarda_numeros(self):
        for numero, reporte in REPORTES.items():
            filtros = FILTROS if reporte.usa_filtros else {}
            columnas, filas = reporte.tabla(**filtros)
            respuesta = self.client.get(reverse("reporte_excel", args=[numero]), filtros)
            hoja = load_workbook(BytesIO(contenido(respuesta))).active
            valores = [list(fila) for fila in hoja.iter_rows(values_only=True)]
            self.assertEqual(valores[0], columnas)
            self.assertEqual(valores[1:], filas)
            self.assertIsInstance(valores[1][-1], (int, float))

    def test_reporte4_respeta_los_filtros(self):
        respuesta = self.client.get(reverse("reporte", args=[4]), FILTROS)
        grupos = {fila[0] for fila in respuesta.context["filas"]}
        self.assertEqual(grupos, {"25-34", "35-44", "45-54"})
        self.assertContains(respuesta, "Sustancia: Alcohol")

    def test_seleccion_sin_datos_muestra_mensaje(self):
        for ruta in [reverse("grafico4"), reverse("reporte", args=[4])]:
            respuesta = self.client.get(ruta, FILTROS_SIN_DATOS)
            self.assertContains(respuesta, "No hay datos para la selección")
        respuesta = self.client.get(reverse("reporte_pdf", args=[4]), FILTROS_SIN_DATOS)
        self.assertTrue(contenido(respuesta).startswith(b"%PDF"))
