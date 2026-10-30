import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada, ChatEntrada
from app.schemas.prestamo import PrestamoEntrada, PrediccionSalida
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


# definir_tool() -> dict con la definicion de la tool, sacando "parameters" de PrestamoEntrada
# ejecutar_tool(nombre, argumentos_json) -> dict con "ok" True/False
#       (tool desconocida, JSON roto, datos invalidos o campos inventados -> ok False con el error)
# TODO: responder(mensajes, llm) -> ChatSalida, con el bucle LLM -> tool -> LLM (maximo MAX_VUELTAS)

def definir_tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": NOMBRE_TOOL,
            "description": "Calcula el riesgo de impago de una solicitud",
            "parameters": PrestamoEntrada.model_json_schema()
        }
    }

def ejecutar_tool(nombre, argumentos_json) -> dict:
    argumentos: PrestamoEntrada
    try:
        argumentos = PrestamoEntrada.model_validate(leer_argumentos(argumentos_json))
    except (ValidationError) as e:
        return {"ok": False, "error": e}

    if nombre != NOMBRE_TOOL:
        return {"ok": False, "error": "Nombre de tool incorrecto"}

    prediccion: PrediccionSalida= predecir(argumentos)

    return {
        "ok": True,
        "probabilidad_impago": prediccion.probabilidad_impago,
        "decision": prediccion.decision
    }


def responder(mensajes: ChatEntrada, llm) -> ChatSalida:
    pass