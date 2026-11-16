// Envía el formulario de filtros apenas cambia una opción, sin esperar el botón Actualizar.
const formulario = document.getElementById("formulario-filtros");

formulario.addEventListener("change", function () {
  formulario.submit();
});
