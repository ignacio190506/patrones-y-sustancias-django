# Patrones y Sustancias · Dashboard Django · Certamen 3

Sitio web del proyecto semestral: consumo de sustancias en Chile (SENDA, ENPG 2024) y en una
muestra internacional (UCI Drug Consumption). Continúa el proyecto del Certamen 2.

## Integrantes

- Ignacio Cruz
- Andrés Pérez
- Antonia Espinoza
- Juan Diego Smith

## Enlaces de la entrega

| Elemento | Enlace |
|---|---|
| Video único: proceso de despliegue + presentación del software y del código | https://drive.google.com/drive/folders/1sbmu1iDnd-lS2RRwEqbwMr3MF8MIDKV3?usp=sharing |
| Dirección del sitio en AWS | `http://IP_PUBLICA:8000/dashboard/` · en el despliegue se usó `http://184.73.87.213:8000/dashboard/` |
| Guía de despliegue paso a paso | [docs/Guia_Django_Parte_11_Despliegue_AWS.docx](docs/Guia_Django_Parte_11_Despliegue_AWS.docx) |

El sitio corre en una instancia EC2 de AWS Academy Learner Lab. Ese entorno detiene la instancia al
cerrar la sesión del laboratorio y le asigna otra dirección IP pública al volver a iniciarla, por lo
que el sitio está disponible solo mientras el laboratorio está abierto. El funcionamiento desde un
navegador externo queda registrado en el video.

Los dos videos que pide la pauta se entregan en **un solo video**: en la misma grabación se muestra
el proceso de despliegue en AWS y se presenta el software con la explicación de su código.

## Requerimientos y dónde están

| Requerimiento | Dónde |
|---|---|
| Gráficos de barras, líneas y dispersión (Certamen 2) | `/dashboard/grafico1`, `grafico2`, `grafico3` |
| Nuevo gráfico dinámico con filtros | `/dashboard/grafico4` |
| Gráficos complementarios (mapa de calor, burbujas, radar) | `/dashboard/grafico5`, `grafico6`, `grafico7` |
| Cuatro reportes, cada uno con su ruta | `/dashboard/reporte1` … `/dashboard/reporte4` |
| Nuevo reporte con los datos del gráfico dinámico | `/dashboard/reporte4` (mismos filtros) |
| Descarga en PDF de cada reporte | `/dashboard/reporteN/pdf` · `dashboard/exportar.py` |
| Descarga en Excel de cada reporte | `/dashboard/reporteN/excel` · `dashboard/exportar.py` |
| Datasets guardados en SQLite | `dashboard/models.py` · `python manage.py cargar_datos` |
| Lectura de la base de datos desde AWS | sección "Despliegue en AWS" de este archivo |

Cada gráfico tiene un botón que lleva a su reporte, y el menú lateral tiene un enlace directo a
cada reporte y a cada gráfico.

## Estructura del proyecto

```
manage.py
requirements.txt
proyecto/                  configuración (settings.py, urls.py)
datos/                     archivos originales que se cargan una vez a SQLite
dashboard/
    models.py              tablas EncuestadoChile y ParticipanteUCI
    management/commands/cargar_datos.py    lleva los archivos de datos/ a SQLite
    analisis.py            lee SQLite, limpia los datos y arma las tablas de los reportes
    graficos.py            dibuja los gráficos con Matplotlib
    reportes.py            textos y definición de los cuatro reportes
    forms.py               formulario de filtros del gráfico dinámico y del reporte 4
    exportar.py            genera el PDF (ReportLab) y el Excel (openpyxl)
    views.py               vistas: envían los datos a las plantillas
    urls.py                rutas de la aplicación
    templates/dashboard/   plantillas HTML
    static/dashboard/      CSS y JavaScript propios
    tests.py               pruebas automáticas
```

## Dependencias

Python 3.12 o superior y los paquetes de `requirements.txt`:

| Paquete | Uso |
|---|---|
| Django 5.1 | Framework web y ORM sobre SQLite |
| pandas, numpy | Limpieza y cálculo de los datos |
| matplotlib | Gráficos |
| reportlab | Descarga en PDF |
| openpyxl | Descarga en Excel |
| whitenoise, gunicorn | Servir el sitio en AWS |

## Instalación local (Windows, PowerShell)

```powershell
py -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py cargar_datos
py manage.py createsuperuser
py manage.py runserver
```

Abrir http://127.0.0.1:8000/dashboard/

- `migrate` crea las tablas en `db.sqlite3`.
- `cargar_datos` lee los dos archivos de `datos/` y guarda 18.668 encuestados de Chile y 1.885
  participantes UCI en SQLite. Desde ese momento el sitio solo consulta la base de datos.
- `createsuperuser` crea el usuario para entrar a `/admin/`, donde también se ven las dos tablas.

Pruebas automáticas: `py manage.py test`

## Despliegue en AWS (EC2 con SQLite)

SQLite no es un servidor: la base de datos es un archivo. Por eso se crea **dentro de la instancia
EC2**, en su disco (volumen EBS), y Django la lee desde ahí. La ubicación del archivo se indica con
la variable de entorno `DJANGO_DB_PATH`.

### 1. Crear la instancia

En la consola de AWS → EC2 → *Launch instance*:

- Sistema: Ubuntu Server 24.04 LTS. Tipo: `t3.micro` (o `t2.micro`).
- Par de claves: crear uno nuevo y guardar el archivo `.pem`.
- Grupo de seguridad (reglas de entrada): SSH puerto 22 desde "Mi IP" y TCP personalizado
  puerto 8000 desde `0.0.0.0/0`.

Anotar la **dirección IPv4 pública** de la instancia.

### 2. Conectarse e instalar

```bash
ssh -i clave.pem ubuntu@IP_PUBLICA
sudo apt update
sudo apt install -y python3-venv python3-pip git sqlite3
git clone https://github.com/ignacio190506/patrones-y-sustancias-django.git
cd patrones-y-sustancias-django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Django para el servidor

Crear el archivo `/home/ubuntu/patrones.env` (`nano ~/patrones.env`) con estas cuatro líneas,
reemplazando la IP y la clave:

```
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=IP_PUBLICA
DJANGO_SECRET_KEY=CLAVE_GENERADA
DJANGO_DB_PATH=/home/ubuntu/base_datos/db.sqlite3
```

La clave se genera con `python -c "import secrets; print(secrets.token_urlsafe(50))"`.

| Variable | Configuración de `settings.py` | Para qué |
|---|---|---|
| `DJANGO_ALLOWED_HOSTS` | `ALLOWED_HOSTS` | Permite abrir el sitio desde la dirección del servidor |
| `DJANGO_DEBUG` | `DEBUG` | Desactiva el modo de desarrollo |
| `DJANGO_SECRET_KEY` | `SECRET_KEY` | Clave propia del servidor |
| `DJANGO_DB_PATH` | `DATABASES["default"]["NAME"]` | Ubicación del archivo SQLite en la instancia |

### 4. Crear y cargar la base de datos en la instancia

```bash
mkdir ~/base_datos
set -a; source ~/patrones.env; set +a
python manage.py migrate
python manage.py cargar_datos
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

Comprobar que la base existe y tiene los datos:

```bash
sqlite3 ~/base_datos/db.sqlite3 "SELECT COUNT(*) FROM dashboard_encuestadochile;"
sqlite3 ~/base_datos/db.sqlite3 "SELECT COUNT(*) FROM dashboard_participanteuci;"
```

Deben responder 18668 y 1885.

### 5. Dejar el sitio funcionando

Crear el servicio (`sudo nano /etc/systemd/system/patrones.service`):

```ini
[Unit]
Description=Patrones y Sustancias (Django)
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/patrones-y-sustancias-django
EnvironmentFile=/home/ubuntu/patrones.env
ExecStart=/home/ubuntu/patrones-y-sustancias-django/.venv/bin/gunicorn proyecto.wsgi --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now patrones
sudo systemctl status patrones
```

### 6. Comprobar desde un navegador externo

Abrir `http://IP_PUBLICA:8000/dashboard/` desde otro computador o desde el teléfono y revisar:
el gráfico dinámico con sus filtros, el reporte 4 y las descargas en PDF y Excel de los cuatro
reportes.

Para actualizar el sitio después de un cambio en GitHub: `git pull`, repetir `collectstatic` y
`sudo systemctl restart patrones`.

## Datos

- `datos/drug_consumption.data`: UCI Machine Learning Repository, Drug Consumption (Quantified).
- `datos/enpg_2024_reducida.csv`: SENDA, Décimo Sexto Estudio Nacional de Drogas en Población
  General 2024, solo con las 13 columnas usadas (la base original pesa 54 MB).
