# API para consultar la Unidad de Fomento en Python

## Descripción

Esta API permite consultar el valor de la Unidad de Fomento (UF) de Chile para una fecha específica. La UF es una unidad de cuenta reajustable que se utiliza en Chile para calcular el valor de contratos, tasas de interés y otros aspectos financieros.

La información de la UF se obtiene del sitio web del Servicio de Impuestos Internos (SII) de Chile mediante scraping. Se mantiene una tabla actualizada con los valores de la UF para cada año, y se actualiza la tabla cada vez que se consulta una fecha que no se encuentra en ella.

## Uso

Para utilizar esta API, se debe enviar una petición HTTP GET a la siguiente URL:

```
/uf/<date>
```

Donde `date` es la fecha que se desea consultar en formato "YYYY-MM-DD".

La API devolverá un objeto JSON con la fecha consultada y el valor de la UF correspondiente:

```json
{
  "date": "2023-05-17",
  "value": 30181.23
}
```

Si la fecha consultada no se encuentra dentro del rango de fechas para las que se tienen valores de UF, la API devolverá un error con un mensaje correspondiente:

```json
{
  "error": "La fecha especificada está fuera del rango de fechas para las que se tienen valores de UF"
}
```

Si la fecha consultada tiene un formato inválido, la API devolverá un error con un mensaje correspondiente:

```json
{
  "error": "La fecha especificada no tiene el formato correcto"
}
```

## Ejemplo

### Petición

```
GET /uf/2023-03-06
```

### Respuesta

```json
{
  "date": "2023-03-06",
  "value": 30103.23
}
```

## Pruebas

Se han incluido pruebas unitarias en el archivo `test_main.py`. Para ejecutar las pruebas, se debe ejecutar el siguiente comando en la terminal:

```
python test_main.py
```

Las pruebas verifican que se devuelve un error cuando no se puede obtener el valor de la UF desde el sitio web del SII, y que se obtiene el valor correcto de la UF para una fecha específica.
"""
