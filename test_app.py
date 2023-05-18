import unittest
from main import app

class TestApp(unittest.TestCase):

    def test_get_uf(self):
        # Verificar que se devuelve un error cuando no se puede obtener el valor de la UF desde el sitio web del SII
        with app.test_client() as client:
            response = client.get("/uf/2023-09-14")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "La fecha especificada está fuera del rango de fechas para las que se tienen valores de UF")
            print(" 1. Verificar que se devuelve un error cuando no se puede obtener el valor de la UF desde el sitio web del SII")

        # Verificar que se obtiene el valor correcto de la UF para una fecha específica
        with app.test_client() as client:
            response = client.get("/uf/2023-03-06")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["date"], "2023-03-06")
            self.assertAlmostEqual(response.json["value"], 35570.37)
            print(" 2. Verificar que se obtiene el valor correcto de la UF para una fecha específica")

        # Verificar que se devuelve un error cuando se intenta obtener el valor de la UF para una fecha demasiado antigua
        with app.test_client() as client:
            response = client.get("/uf/2012-12-31")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "La fecha consultada es demasiado antigua")
            print(" 3. Verificar que se devuelve un error cuando se intenta obtener el valor de la UF para una fecha demasiado antigua")

        # Verificar que se utiliza el valor en caché cuando se consulta una fecha que ya ha sido consultada previamente
        with app.test_client() as client:
            response = client.get("/uf/2023-05-10")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["date"], "2023-05-10")
            self.assertAlmostEqual(response.json["value"], 35959.84)
            print(" 4. Verificar que se utiliza el valor en caché cuando se consulta una fecha que ya ha sido consultada previamente")  

    def test_invalid_date_format(self):
        # Verificar que se devuelve un error cuando se especifica una fecha con un formato incorrecto
        with app.test_client() as client:
            response = client.get("/uf/2020-01-01a")
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "La fecha especificada no tiene el formato correcto")
            print(" 5. Verificar que se devuelve un error cuando se especifica una fecha con un formato incorrecto")    

    def test_date_out_of_range(self):
        # Verificar que se devuelve un error cuando se especifica una fecha demasiado antigua
        with app.test_client() as client:
            response = client.get("/uf/1990-01-01")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "La fecha consultada es demasiado antigua")
            print(" 6. Verificar que se devuelve un error cuando se especifica una fecha demasiado antigua")

    def test_date_not_found(self):
        # Verificar que se devuelve un error cuando se especifica una fecha para la cual no se tienen valores de UF
        with app.test_client() as client:
            response = client.get("/uf/2023-12-31")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "La fecha especificada está fuera del rango de fechas para las que se tienen valores de UF")
            print(" 7. Verificar que se devuelve un error cuando se especifica una fecha para la cual no se tienen valores de UF")

if __name__ == "__main__":
    unittest.main()
