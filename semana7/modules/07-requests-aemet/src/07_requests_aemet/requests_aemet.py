import requests
import os
from dotenv import load_dotenv

url_estaciones = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

def get_request_data(r):
    data = requests.get(r.json()["datos"])
    data.raise_for_status()
    return data.json()

load_dotenv()
api_key = os.getenv("API_KEY")

r = requests.get(url_estaciones, headers={"api_key": api_key})
r.raise_for_status()
data = get_request_data(r)

idema = None
for estacion in data:
    if estacion.get("nombre") == "MADRID, CIUDAD UNIVERSITARIA":
        idema = estacion.get("indicativo")
        break

if idema is None:
    raise ValueError(f"Nombre de estación no encontrado: MADRID, CIUDAD UNIVERSITARIA")

fechaIniStr = "2019-10-01T00:00:00UTC"
fechaFinStr = "2019-10-30T23:59:59UTC"
climatologias = requests.get(
    f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}",
    headers={
      "api_key": api_key
    }
)
climatologias.raise_for_status()

print(get_request_data(climatologias))

