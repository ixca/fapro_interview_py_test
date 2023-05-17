import requests
from datetime import datetime, timedelta
from flask import Flask,jsonify
from bs4 import BeautifulSoup


app = Flask(__name__)

# Utilizar una variable constante en lugar de construir la URL en cada llamada a la API.
UF_URL_TEMPLATE = "https://www.sii.cl/valores_y_fechas/uf/uf{}.htm"

# Utilizar una variable para almacenar la tabla de valores de UF por año en lugar de descargar la tabla cada vez.
UF_TABLES = {}
UF_MAX_UPDATED_DATE = None


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

    year = date.year
    # Verificar si la tabla de valores de UF para el año especificado está en caché
    if year not in UF_TABLES or not is_table_up_to_date(year, date):
        url = UF_URL_TEMPLATE.format(year)
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("No se pudo obtener el valor de la Unidad de Fomento")

        # Almacenar la tabla de valores de UF en caché
        html = response.content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("div", {"id": "mes_all"}).find("table")
        #Actualiza la tabla de valores de UF
        uf_table = parse_table(table, year)
        UF_TABLES[year] = uf_table
        #Actualiza la fecha de última 
        update_max_updated_date(uf_table)

    # Verificar que el año esté en la tabla
    if year not in UF_TABLES:
        raise ValueError("No se tienen valores de UF para el año especificado")

    # Buscar el valor de UF correspondiente a la fecha específica
    value = find_uf_value(UF_TABLES[year], date_str)
    if value is None:
        raise ValueError("La fecha especificada está fuera del rango de fechas para las que se tienen valores de UF")

    return value


def is_table_up_to_date(year: int, date: datetime) -> bool:
    """Verifica si la tabla de valores de UF para el año está actualizada."""
    global UF_MAX_UPDATED_DATE
    if UF_MAX_UPDATED_DATE is not None:
        uf_last_updated_date_obj = datetime.strptime(UF_MAX_UPDATED_DATE, "%Y-%m-%d")
        if uf_last_updated_date_obj <= date:
            return True
    return False


def parse_table(table, year: int):
    """Convierte la tabla HTML de valores de UF en un diccionario."""
    uf_table = {}
    rows = table.find_all("tr")
    for row in rows[1:]:
        cells = row.find_all()

        for key_cell, cell in enumerate(cells):
            date_str = str(year) + "-" + str(key_cell).zfill(2) + "-" + str(cells[0].text.strip()).zfill(2)
            value = cell.text.strip().replace(".", "").replace(",", ".")
            if is_valid_date(date_str):
                # validar que el valor del string value no esté vacío ni sea espacio en blanco
                stripped_value = value.strip()
                if stripped_value:
                    try:
                        float_value = float(stripped_value)
                        uf_table[date_str] = float_value

                    except ValueError:
                        pass

    return uf_table


def update_max_updated_date (uf_table):
    """Actualiza la fecha de maxima fecha actualizada de UF si corresponde."""
    global UF_MAX_UPDATED_DATE
    for date_str in uf_table.keys():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if UF_MAX_UPDATED_DATE is None or date_obj > datetime.strptime(UF_MAX_UPDATED_DATE, "%Y-%m-%d"):
            UF_MAX_UPDATED_DATE = date_str


def find_uf_value(uf_table, date: datetime) -> float:
    """Encuentra el valor de UF correspondiente a la fecha en la tabla."""
    if date in uf_table:
        return uf_table[date]
    return None

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False    
@app.route("/uf/<date>")
def get_uf(date):
    """Obtiene el valor de la UF para la fecha especificada."""
    try:
        value = get_uf_value(date)
        return jsonify({"date": date, "value": value})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
