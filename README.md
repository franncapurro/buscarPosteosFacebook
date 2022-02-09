# buscarPosteosFacebook

buscarPosteosFacebook es una herramienta escrita en Python que permite acceder automáticamente a Facebook, extraer un conjunto de publicaciones y volcar la información recolectada en un archivo de Excel (_.xlsx_).

De cada publicación encontrada se obtienen los siguientes atributos:
- type (si contiene un link o si es un video)
- medio (nombre de la página de Facebook publicadora)
- by (ID de la página de Facebook publicadora)
- post_id (ID de la publicación)
- post_link (Link hacia la publicación)
- post_message (Cuerpo de la publicación)
- link (link compartido en la publicación)
- post_published (fecha y hora en la que la publicación fue realizada)
- like_count_fb (cantidad de likes)
- comments_count_fb (cantidad de comentarios)
- reactions_count_fb (cantidad de reacciones)
- shares_count_fb (cantidad de veces que fue compartida)
- rea_LIKE (cantidad de likes)
- rea_LOVE (cantidad de "Me encanta")
- rea_WOW (cantidad de "Me sorprende")
- rea_HAHA (cantidad de "Me entretiene")
- rea_SAD (cantidad de "Me entristece")
- rea_ANGRY (cantidad de "Me enoja")
- rea_CARE (cantidad de "Me preocupa")

## Instalación

### Linux

1. Instalar la última versión de Python 3.
2. Crear un entorno virtual de Python (por ejemplo, usando [pyenv](https://github.com/pyenv/pyenv) y [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)).
3. Activado el entorno virtual, instalar las bibliotecas de Python necesarias con `pip install -r requirements.txt`.
4. Instalar la última versión de [Mozilla Firefox](https://www.mozilla.org/es-AR).
5. Abrir el archivo `config.json` e ingresar usuario y contraseña de Facebook.

### Windows

1. Descargar [Python para Windows](https://www.microsoft.com/es-ar/p/python-39/9p7qfqmjrfp7).
2. Abrir una ventana de terminal, situarse en el directorio de la herramienta y ejecutar `pip install -r requirements.txt`. Esperar a que se instalen las bibliotecas de Python.
3. Instalar la última versión de [Mozilla Firefox](https://www.mozilla.org/es-AR).
4. Abrir el archivo `config.json` e ingresar usuario y contraseña de Facebook.

### MacOS

Mismas instrucciones que para Linux.

## Configuración

El archivo config.json permite configurar algunos parámetros de la herramienta.
Los parámetros que se pueden configurar son:
- output_filename: prefijo con el que se nombrará al archivo de salida del listado de posteos recuperado.
- firefox_windows_path: (Sólo para Windows) Ruta al archivo exe del navegador Firefox.
- user y password: Usuario y Contraseña de Facebook para el login.

**Los archivos de salida siempre se guardarán en el directorio de la herramienta.**

## Ejecución

### Ejemplos comunes

Escritos en powershell.

#### Obtener todas las publicaciones de una página pública de Facebook hechas en un intervalo de tiempo

Ejemplo: si queremos todas las publicaciones hechas por "[El Resaltador](https://www.facebook.com/ElResaltadorCba)" entre el día 8 de febrero a las 15:00 y el día 10 de febrero a las 4:00, ambos del año 2022, deberíamos escribir:

```powershell
--source public_page --word 'ElResaltadorCba' --since '2022-02-08 15:00:00' --until '2022-02-10 04:00:00'
```

#### Obtener todas las publicaciones de una página pública de Facebook hechas a partir de una fecha y hora particulares

Ejemplo: si queremos todas las publicaciones hechas por "[El Resaltador](https://www.facebook.com/ElResaltadorCba)" desde el día 8 de febrero de 2022 a las 15 h hasta el día de hoy a la hora actual deberíamos escribir:

```powershell
--source public_page --word 'ElResaltadorCba' --since '2022-02-08 15:00:00'
```

#### Obtener las últimas publicaciones realizadas de una página pública de Facebook

Ejemplo: si queremos las últimas 37 publicaciones hechas por "[El Resaltador](https://www.facebook.com/ElResaltadorCba)" deberíamos escribir:

```powershell
--source public_page --word 'ElResaltadorCba' --amount 37
```


### Parámetros

- `--source`: No es opcional. Se debe elegir entre `--source search_page`, para realizar scrapping desde la página de búsqueda, o `--source public_page`, para realizar scrapping desde una página pública.

- `--word`: No es opcional. Si se eligió `--source search_page`, entonces este parámetro será el término de búsqueda. Si se eligió `--source public_page`, será el ID de la página pública.

- `--since`: Es opcional, pero si no se indica entonces debe ser usado el parámetro `--amount`. Es la fecha a partir de la cual se desean obtener publicaciones (esto es, un límite inferior). Ejemplo: `--since 2022-01-23`.

- `--until`: Es opcional, pero si no se indica entonces debe ser usado el parámetro `--amount`. Es la fecha hasta la cual se desean obtener publicaciones (esto es, un límite superior). Ejemplo: `--since 2022-01-25`.

- `--amount`: Es opcional, pero si no se indica entonces debe ser usados los parámetros `--since` y `--until`. Es la cantidad de posts que se desean obtener.

Los parámetros `--since`, `--until` y `--amount` pueden ser usados de manera combinada. Ejemplos:

Obtener todas las publicaciones de la página pública de El Resaltador entre el día 2022-01-23 y el día 2022-01-25.

```powershell
python .\src\search_for_facebook_posts.py --source public_page --word 'ElResaltadorCba' --since 2022-01-25 --until 2022-01-25
```

Obtener 8 publicaciones a partir del día 2022-01-25 de la página pública de La Voz del Interior.

```powershell
python .\src\search_for_facebook_posts.py --source public_page --word 'LaVoz.com.ar' --amount 8 --since 2022-01-25
```

## FAQs

### ¿Cómo encuentro el ID de una página pública?

Por ejemplo, al acceder a la página de La Voz del Interior vemos que su URL es `https://www.facebook.com/LaVoz.com.ar`, entonces su ID es `LaVoz.com.ar`.
