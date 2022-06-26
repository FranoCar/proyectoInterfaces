# Proyecto Interfaces: Plataforma de Distribución de Videojuegos

## Contenidos importantes ##
1. [Archivo de Arranque(run.py)](#run)
2. [Archivo de Rutas(routes.py)](#routes)
3. [Archivo de Inicialización de la Dependencia(__init__.py)](#module)
<a name="run"></a>
## Archivo de Arranque(run.py) ##
- Localización: `/proyecto/run.py`
- Funcionalidad: Este archivo solo importa el módulo creado `app` y corre el proyecto
- Cómo usar: ejecutar en consola `python run.py`

<a name="routes"></a>
## Archivo de Rutas(routes.py) ##
- Localización: `/proyecto/app/routes.py`
- Funcionalidad: Manejar todas las rutas de la aplicación
- Cómo usar: Mantener los cambios del archivo limitados a todo lo que esté debajo de cada función para cada ruta, e importar los paquetes necesarios desde app.

<a name="module"></a>
## Archivo de Inicialización de la Dependencia(__init__.py) ##
- Localización: `/proyecto/__init__.py`
- Funcionalidad: Importar módulos, alojar funciones y variables globales.
- Cómo usar: Mantener todos los imports del programa, funciones y variables globales aquí para luego impotarlas a routes.py desde app.
