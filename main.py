import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup


app = Flask(__name__)
app.debug = True

# 1. Utilizar una variable constante en lugar de construir la URL en cada llamada a la API.
UF_URL_TEMPLATE = "https://www.sii.cl/valores_y_fechas/uf/uf{}.htm"

# 2. Utilizar una variable para almacenar la tabla de valores de UF por año en lugar de descargar la tabla cada vez que se realiza una llamada a la API.
UF_TABLES = {}


def get_uf_value(date_str: str) -> float:
    """Obtiene el valor de la UF para la fecha especificada."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("La fecha especificada no tiene el formato correcto")

    today = datetime.today()
    # Verificar que la fecha no sea más antigua de 365 días
    if date < (today - timedelta(days=365)):
        raise ValueError("La fecha consultada es demasiado antigua")

    # Verificar si la tabla de valores de UF para el año especificado está en caché
    year = date.year
    if year not in UF_TABLES:
        url = UF_URL_TEMPLATE.format(year)
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("No se pudo obtener el valor de la Unidad de Fomento")

        # Almacenar la tabla de valores de UF en caché
        html = response.content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        UF_TABLES[year] = soup.find("div", {"id": "mes_all"}).find("table")

    # Verificar que el año esté en la tabla
    if year not in UF_TABLES:
        raise ValueError("No se tienen valores de UF para el año especificado")

    # Busca la fila y columna correspondiente a la fecha específica
    day = date.day
    month = date.month 
    row = UF_TABLES[year].find_all("tr")[day]

    # Verificar que el día esté dentro del rango de días para ese mes y año
    # if day_int < 1 or day_int > row.find_all("td")[1].text.strip():
    #     raise ValueError("La fecha especificada está fuera del rango de fechas para las que se tienen valores de UF")

    value = row.find_all("td")[month-1].text.strip()
    value = float(value.replace(".", "").replace(",", "."))
    return value



@app.route("/uf/<date>")
def get_uf(date):
    """Obtiene el valor de la UF para la fecha especificada."""
    try:
        print("date", date) 
        value = get_uf_value(date)
        return jsonify({"date":date, "value": value})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

