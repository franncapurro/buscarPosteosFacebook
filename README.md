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
- page_name: en caso de que se desee obtener posts mediante la página de búsqueda, introducir acá el término a buscar.
- amount_posts: en caso de que se desee obtener posts mediante la página de búsqueda, introducir acá la cantidad de posteos deseada.

## Ejecución

Para realizar scrapping de posteos desde la búsqueda de Facebook:

```
python .\src\search_for_facebook_posts.py search_page
```

Para realizar scrapping de posteos desde una página de Facebook pública (una fanpage):

```
python .\src\search_for_facebook_posts.py public_page id_de_la_pagina cantidad_de_posteos
```
