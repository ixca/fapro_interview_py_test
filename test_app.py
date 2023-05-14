import unittest
from main import app

class TestApp(unittest.TestCase):

    def test_get_uf(self):
        # Verificar que se devuelve un error cuando no se puede obtener el valor de la UF desde el sitio web del SII
        # with app.test_client() as client:
        #     response = client.get("/uf/2023-05-14")
        #     self.assertEqual(response.status_code, 500)
        #     self.assertEqual(response.json["error"], "No se pudo obtener el valor de la Unidad de Fomento")
        #     print("done err 500")
        # Verificar que se obtiene el valor correcto de la UF para una fecha específica
        with app.test_client() as client:
            response = client.get("/uf/2023-03-06")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["date"], "2023-03-06")
            self.assertAlmostEqual(response.json["value"], 35570.37)

        # Verificar que se devuelve un error cuando se intenta obtener el valor de la UF para una fecha demasiado antigua
        with app.test_client() as client:
            response = client.get("/uf/2012-12-31")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "La fecha consultada es demasiado antigua")

        # Verificar que se utiliza el valor en caché cuando se consulta una fecha que ya ha sido consultada previamente
        with app.test_client() as client:
            response = client.get("/uf/2023-05-10")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["date"], "2023-05-10")
            self.assertAlmostEqual(response.json["value"], 35959.84)
