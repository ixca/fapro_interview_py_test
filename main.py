import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

UF_URL_TEMPLATE = "https://www.sii.cl/valores_y_fechas/uf/uf{}.htm"
UF_TABLES = {}
UF_MAX_UPDATED_DATE = None

def get_uf_value(date_str: str) -> float:
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("La fecha especificada no tiene el formato correcto")

    today = datetime.today()

    if date < (today - timedelta(days=365)):
        raise ValueError("La fecha consultada es demasiado antigua")

    year = date.year

    if year not in UF_TABLES or not is_table_up_to_date(year, date):
        uf_table = fetch_uf_table(year)
        UF_TABLES[year] = uf_table
        update_max_updated_date(uf_table)

    if year not in UF_TABLES:
        raise ValueError("No se tienen valores de UF para el año especificado")

    value = find_uf_value(UF_TABLES[year], date_str)

    if value is None:
        raise ValueError("La fecha especificada está fuera del rango de fechas para las que se tienen valores de UF")

    return value

def fetch_uf_table(year: int):
    url = UF_URL_TEMPLATE.format(year)
    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError("No se pudo obtener el valor de la Unidad de Fomento")

    html = response.content.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("div", {"id": "mes_all"}).find("table")
    uf_table = parse_table(table, year)

    return uf_table

def parse_table(table, year: int):
    """Convierte la tabla HTML de valores de UF en un diccionario."""
    uf_table = {}
    rows = table.find_all("tr")
    for row in rows[1:]:
        cells = row.find_all()
        current_day = cells[0].text.strip()

        for key_cell, cell in enumerate(cells):
            date_str = str(year) + "-" + str(key_cell).zfill(2) + "-" + str(current_day).zfill(2)
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
    
def is_table_up_to_date(year: int, date: datetime) -> bool:
    """Verifica si la tabla de valores de UF para el año está actualizada."""
    global UF_MAX_UPDATED_DATE
    if UF_MAX_UPDATED_DATE is not None:
        uf_last_updated_date_obj = datetime.strptime(UF_MAX_UPDATED_DATE, "%Y-%m-%d")
        if uf_last_updated_date_obj <= date:
            return True
    return False

def update_max_updated_date(uf_table):
    global UF_MAX_UPDATED_DATE
    for date_str in uf_table.keys():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if UF_MAX_UPDATED_DATE is None or date_obj > datetime.strptime(UF_MAX_UPDATED_DATE, "%Y-%m-%d"):
            UF_MAX_UPDATED_DATE = date_str

def find_uf_value(uf_table, date: datetime) -> float:
    if date in uf_table:
        return uf_table[date]
    return None

def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False    
@app.route("/uf/<date>")
def uf_value(date):
    try:
        uf = get_uf_value(date)
        response = {"date": date, "value": uf}
        return jsonify(response)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()
