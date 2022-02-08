# buscarPosteosFacebook

Script Python que permite acceder automáticamente a Facebook, extraer un conjunto de posteos y volcar la información recolectada en un archivo .xlsx.
Esta herramienta está conformada por un script en lenguaje Python. El mismo navega y recupera automáticamente el código HTML de cada posteo para luego procesarlo y exportar los siguientes datos:

- type
- medio
- by
- post_id
- post_link
- post_message
- link
- post_published
- like_count_fb
- comments_count_fb
- reactions_count_fb
- shares_count_fb
- rea_LIKE
- rea_LOVE
- rea_WOW
- rea_HAHA
- rea_SAD
- rea_ANGRY
- rea_CARE

## Configuración

El archivo config.json, permite configurar la herramienta para recuperar los posteos.
Las opciones que se pueden configurar son:
- base_path: indica la ruta/directorio donde se guardaran los archivos de salida. La ruta debe ser la de un directorio existente. Por ejemplo: `C:\\`.
- output_filename: prefijo con el que se nombrará al archivo de salida del listado de posteos recuperado.
- gecko_binary: Ruta al archivo exe del navegador Firefox.
- user y password: Usuario y Contraseña de Facebook para el login.

## Ejecución

### Ejemplos

Para realizar scrapping de posteos desde la búsqueda de Facebook.

```powershell
python .\src\search_for_facebook_posts.py --source search_page --word 'palabras a buscar' --amount 10
```

Para realizar scrapping de posteos desde una página de Facebook pública (una fanpage):

```powershell
python .\src\search_for_facebook_posts.py --source public_page --word 'LaVoz.com.ar' --amount 8
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
