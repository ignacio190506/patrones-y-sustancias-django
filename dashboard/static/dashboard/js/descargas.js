// Controla los botones "Descarga en PDF" y "Descarga en Excel" de los reportes.
// Cada botón indica en sus atributos data- la URL, el nombre y el tipo del archivo.
const botones = document.querySelectorAll(".boton-descarga");
const estado = document.getElementById("estado-descarga");
const ventana = document.getElementById("aviso-descarga");
const mensaje = document.getElementById("mensaje-descarga");

for (const boton of botones) {
  boton.addEventListener("click", async function () {
    const textoOriginal = boton.textContent;
    for (const otro of botones) otro.disabled = true;
    boton.textContent = "Preparando archivo...";
    estado.textContent = "Generando el archivo. Espere un momento.";
    try {
      const respuesta = await fetch(boton.dataset.url, { cache: "no-store" });
      const archivo = await respuesta.blob();
      if (!respuesta.ok || archivo.type !== boton.dataset.tipo) {
        throw new Error("La respuesta no contiene el archivo esperado");
      }
      // Enlace temporal para que el navegador guarde el archivo recibido
      const enlace = document.createElement("a");
      enlace.href = URL.createObjectURL(archivo);
      enlace.download = boton.dataset.nombre;
      enlace.click();
      setTimeout(() => URL.revokeObjectURL(enlace.href), 60000);
      estado.textContent = "Archivo listo. Se inició la descarga.";
      mensaje.textContent = "Se inició la descarga de " + boton.dataset.nombre +
        ". Revise la carpeta Descargas de su navegador.";
    } catch (error) {
      estado.textContent = "No se pudo descargar el archivo.";
      mensaje.textContent = "No se pudo obtener el reporte. Revise la conexión e intente nuevamente.";
    } finally {
      for (const otro of botones) otro.disabled = false;
      boton.textContent = textoOriginal;
    }
    ventana.showModal();
  });
}
