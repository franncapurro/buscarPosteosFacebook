# buscarPosteosFacebook


Script Python que permite acceder automáticamente a la búsqueda avanzada de Facebook, extraer un conjunto de posteos y volcar la información recolectada en un archivo.


Esta herramienta está conformada por un script en lenguaje Python. El mismo navega y recupera automáticamente el código HTML de cada posteo para luego procesarlo mediante la biblioteca Beautiful Soup y exportar los siguientes datos:


- type (si contiene un link, una imagen o un video)
- medio (nombre de la página de Facebook)
- by (identificador de la página en la URL)
- post_id (identificador de la publicación en la URL)
- post_link (link a la publicación)
- post_message (texto de la publicación)
- link (link compartido)
- post_published (fecha y hora en la que fue publicado)
- like_count_fb (cantidad de "Me gusta")
- comments_count_fb (cantidad de comentarios)
- reactions_count_fb (cantidad de reacciones)
- shares_count_fb (cantidad de veces que fue compartido)
- rea_LIKE (cantidad de "Me gusta")
- rea_LOVE (cantidad de "Me encanta")
- rea_WOW (cantidad de "Me sorprende")
- rea_HAHA (cantidad de "Me divierte")
- rea_SAD (cantidad de "Me entristece")
- rea_ANGRY (cantidad de "Me enoja")


## Dependencias para poder ejecutar este software


### En Mac Os


#### 1. Instalar Python 3


Primero verificar si no está ya instalado. Ejecutar en la terminal: `python3 --version`.


Descargar la última versión de Python 3: https://www.python.org/downloads/ (web oficial).
Ejecutar el archivo .pkg descargado y completar la instalación.


#### 2. Configurar un entorno virtual de Python


Para esto necesitamos utilizar dos programas: [pyenv](https://github.com/pyenv/pyenv) y [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv).


Necesitamos tener instaladas las Xcode Command Line Tools. Para instalarlas: `xcode-select --install`.


Necesitamos tener instalado Homebrew. Para instalarlo: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.


Luego instalar las siguientes dependencias: `brew install openssl readline sqlite3 xz zlib`.


Finalmente instalamos pyenv: 


```
brew update
brew install pyenv
```


y pyenv-virtualenv:


```
brew install pyenv-virtualenv
```


Descargamos la versión de Python que queremos usar en nuestro entorno virtual: `pyenv install 3.9.9`.
Creamos un entorno virtual: `pyenv virtualenv 3.9.9 entorno-virtual-buscar-posteos-fb`.
Lo activamos: `pyenv activate entorno-virtual-buscar-posteos-fb`.
Y procedemos a instalar las dependencias que son libs de Python: `pip install -r requirements.txt`.


### En Windows
Para ejecutar en windows hay que instalar el driver de selenium primero. Se puede usar la siguiente Guia: https://medium.com/ananoterminal/install-selenium-on-windows-f4b6bc6747e4
Una vez instalado el driver, en el archivo de configuracion hay
que ajustar los parametros gecko_binary y gecko_driver_exe con las rutas de los exes de Firefox y del driver respectivamente.


### En Linux


Para utilizar el script es necesario configurar el venv e instalar las librerias necesarias con:
- $ py -m venv env (Donde env es el nombre del ambiente virtual)
- $ py -m pip install -r requirements.txt (Intalar todas las librerias necesarias)


## Configuración necesaria antes de que sea ejecutado
El archivo config.json, permite configurar este software para recuperar los posts.
Las opciones que se pueden configurar son:


- base_path: indica la ruta/directorio donde se guardaran los archivos de salida. Se debe escribir la ruta del directorio de este repositorio.
- output_filename: nombre del archivo de salida del listado de posteos recuperado.
- gecko_binary: Ruta al archivo del navegador Firefox.
- user y password: Usuario y Contraseña de Facebook para el login.
- page_name: Nombre de la página de Facebook para buscar posts. 

## Ejecución


### En Mac OS


### En Windows


