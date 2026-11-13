import joblib

from app.config import MODEL_PATH
from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada

# Orden en el que el modelo espera las variables
VARIABLES = [
    "edad",
    "ingresos_mensuales",
    "importe_prestamo",
    "plazo_meses",
    "antiguedad_laboral_anios",
    "impagos_previos",
]

# cargar el modelo joblib una sola vez, al importar el modulo
# funcion decidir(probabilidad) -> "aprobar", "revisar" o "rechazar" (umbrales en el enunciado)
# funcion predecir(entrada) -> PrediccionSalida, usando VARIABLES para ordenar los valores
model = joblib.load(MODEL_PATH)

def decidir(probabilidad) -> str:
    if probabilidad < 0.2:
        return "aprobar"
    elif probabilidad < 0.5:
        return "revisar"
    else:
        return "rechazar"

def predecir(entrada: PrestamoEntrada) -> PrediccionSalida:
    valores = [
        entrada.edad,
        entrada.ingresos_mensuales,
        entrada.importe_prestamo,
        entrada.plazo_meses,
        entrada.antiguedad_laboral_anios,
        entrada.impagos_previos,
    ]
    probabilidad = model.predict_proba([valores])[0][1]
    return PrediccionSalida(
        probabilidad_impago=float(probabilidad),
        decision=decidir(probabilidad),
    )