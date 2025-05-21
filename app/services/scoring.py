def puntaje_opcion(letra: str) -> int:
    """Asignar valor numérico a cada opción."""
    return {"a": 1, "b": 2, "c": 3, "d": 4}.get(letra.lower(), 0)

def nivel_promedio(p: float):
    """Clasificar promedio a nivel y riesgo."""
    if p >= 75:
        return ("Alto", "Ninguno")
    if p >= 60:
        return ("Medio", "Bajo")
    return ("Bajo", "Alto")

def generar_resultados(respuestas: dict):
    """
    Calcular promedios por examen a partir de respuestas:
    respuestas = { "DINAMISMO": {"p1":"a", "p2":"b", ...}, ... }
    """
    resultados = {}
    for examen, resp in respuestas.items():
        vals = [puntaje_opcion(v) for v in resp.values()]
        if not vals:
            continue
        promedio = round(sum(vals) * 25 / len(vals), 2)  # Escala 0-100
        nivel, riesgo = nivel_promedio(promedio)
        resultados[examen] = {
            "promedio": promedio,
            "nivel": nivel,
            "riesgo": riesgo,
            "interpretacion": f"Promedio {nivel} ⇒ Riesgo {riesgo}",
            "subfactores": {}   # Se puede rellenar más adelante
        }
    return resultados
