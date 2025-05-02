# FiltraTodo - Sistema de Filtrado de Datos

FiltraTodo es una aplicación web simple que te permite subir archivos CSV o Excel y filtrarlos por diferentes criterios como nombre, edad o fecha.

## Requisitos previos

Para ejecutar esta aplicación necesitarás:

- Python 3.7 o superior
- Flask (framework web)
- Pandas (para procesamiento de datos)

## Instalación

1. Crea un entorno virtual (recomendado):

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

2. Instala las dependencias necesarias:

```bash
pip install flask pandas openpyxl
```

Nota: `openpyxl` es necesario para que pandas pueda leer archivos Excel.

## Estructura de archivos

Asegúrate de tener la siguiente estructura de archivos:

```
- app.py
- templates/
  - index.html
- uploads/ (se creará automáticamente)
```

## Ejecución

1. Ejecuta la aplicación Flask:

```bash
python app.py
```

2. Abre tu navegador web y visita:

```
http://127.0.0.1:5000/
```

## Uso

1. **Subir archivo**: Selecciona un archivo CSV o Excel (.xlsx, .xls)
2. **Filtrar datos**: Elige uno de los criterios de filtrado (nombre, edad o fecha)
3. **Resultados**: Visualiza una vista previa de los datos filtrados y descarga el archivo resultante

## Características

- Detección automática de columnas según el tipo de filtro
- Ordenamiento de datos según el criterio seleccionado
- Vista previa de resultados
- Descarga de archivos filtrados

## Solución de problemas

Si encuentras algún error:

1. Verifica que los archivos tengan el formato correcto (CSV o Excel)
2. Asegúrate de que tus archivos tengan columnas con nombres adecuados para los filtros (como "nombre", "edad", "fecha")
3. Revisa la consola del servidor para ver mensajes de error detallados

---

¡Disfruta utilizando FiltraTodo para tus necesidades de filtrado de datos!