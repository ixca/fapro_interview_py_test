import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup


app = Flask(__name__)

CACHE = {}


@app.route("/uf/<date>")
def get_uf(date):
    # Verificar si la fecha está en caché
    if date in CACHE:
        print("La fecha está en caché")
        value = CACHE[date]
    else:
        # Verificar que la fecha sea válida
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            today = datetime.today()
            # Verificar que la fecha no sea más antigua de 365 días
            if date_obj < (today - timedelta(days=365)):
                return jsonify({"error": "La fecha consultada es demasiado antigua"}), 400
        except ValueError as error:
            return jsonify({"error": str(error)}), 400


        # Obtener el valor de la Unidad de Fomento para la fecha especificada
        url = f"https://www.sii.cl/valores_y_fechas/uf/uf{date_obj.year}.htm"
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "No se pudo obtener el valor de la Unidad de Fomento"}), 500
        
        html = response.content.decode("iso-8859-1")
        # value = html.split(str(date_obj.day).zfill(2))[1].split("</td>")[0].split(">")[-1]
        # CACHE[date] = value

        # Busca la tabla que contiene los valores de la UF
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("div", {"id": "mes_all"}).find("table")

        # Extrae los valores de la tabla
        rows = table.find_all("tr")[1:]
        # cols = rows[0].find_all("td")[1:]

        # Busca la fila y columna correspondiente a la fecha específica
        day = date_obj.day
        month = date_obj.month - 1
        value = rows[day - 1].find_all("td")[month].text.strip()
        value = float(value.replace(".", "").replace(",", "."))

        # Guarda el valor de la UF en caché
        CACHE[date] = value

    # Devolver la respuesta en formato JSON
    return jsonify({"date": date, "value": value})


if __name__ == "__main__":
    app.run(debug=True)
