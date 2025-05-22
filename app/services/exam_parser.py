from bs4 import BeautifulSoup

def parse_exam_html(html_content: str) -> dict:
    """
    Parsea el contenido HTML de un examen para extraer preguntas y opciones.

    Args:
        html_content: El contenido HTML del examen como una cadena de texto.

    Returns:
        Un diccionario con la estructura del examen, incluyendo nombre y preguntas.
        Ejemplo:
        {
            "nombre": "Nombre del Examen",
            "preguntas": [
                {"id": "q1", "texto": "¿Pregunta 1?", "opciones": ["a) Opción A", "b) Opción B"]},
                {"id": "q2", "texto": "¿Pregunta 2?", "opciones": ["a) Opción X", "b) Opción Y", "c) Opción Z"]}
            ]
        }
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # TODO: Implementar la lógica de parseo específica para la estructura HTML de tus exámenes.
    # Esto dependerá de cómo el conversor de .docx a HTML genera la estructura.
    # Deberás identificar cómo se marcan las preguntas y las opciones en el HTML.

    # Ejemplo básico (tendrás que adaptarlo a tu HTML real):
    # Buscar, por ejemplo, todos los párrafos (<p>) o encabezados (<h2>) que representen preguntas,
    # y las listas (<ul>/<ol>) o elementos de lista (<li>) que representen opciones.

    examen_parsed = {
        "nombre": "Nombre del Examen (Parseado)", # TODO: Extraer el nombre real del examen del HTML si está presente
        "preguntas": []
    }

    # Ejemplo de cómo encontrar preguntas (esto es muy genérico y probablemente necesite ajuste)
    # Supongamos que cada pregunta es un párrafo con una clase específica o sigue un patrón.
    # for paragraph in soup.find_all('p'):
    #     if 'clase_pregunta' in paragraph.get('class', []): # Ejemplo: buscar por clase CSS
    #         pregunta_texto = paragraph.get_text().strip()
    #         pregunta_id = f"q{len(examen_parsed['preguntas']) + 1}" # Generar un ID simple
    #         opciones = []
    #         # TODO: Encontrar las opciones asociadas a esta pregunta (puede ser la siguiente lista, etc.)
    #         # Por ahora, un ejemplo de opciones fijas:
    #         opciones = ["Opción 1", "Opción 2", "Opción 3"] # Esto DEBE obtenerse del HTML real


    #         examen_parsed["preguntas"].append({
    #             "id": pregunta_id,
    #             "texto": pregunta_texto,
    #             "opciones": opciones
    #         })

    # Este es un parser de ejemplo MUY BÁSICO y DEBES ADAPTARLO
    # a la estructura HTML generada por tu conversor de .docx.
    # Necesitas examinar el HTML de un examen convertido para entender su estructura.

    # Placeholder: Simplemente devolvemos la estructura de ejemplo por ahora
    # Para que la plantilla no falle con datos vacíos al inicio.
    if not examen_parsed["preguntas"]:
         examen_parsed["preguntas"] = [
             {"id": "q1", "texto": "Pregunta de Ejemplo 1 (Adaptar parser)", "opciones": ["Opción A", "Opción B"]},
             {"id": "q2", "texto": "Pregunta de Ejemplo 2 (Adaptar parser)", "opciones": ["Opción X", "Opción Y", "Opción Z"]}
         ]


    return examen_parsed

# Ejemplo de uso (puedes ejecutar este archivo directamente para probar el parser con un HTML de ejemplo)
if __name__ == '__main__':
    html_ejemplo = """
    <html>
    <body>
        <h1>Nombre del Examen de Prueba</h1>
        <p>Esta es la primera pregunta:</p>
        <ul>
            <li>Opción A</li>
            <li>Opción B</li>
            <li>Opción C</li>
        </ul>
        <p>Aquí viene la segunda pregunta:</p>
        <ol>
            <li>Opción 1</li>
            <li>Opción 2</li>
        </ol>
    </body>
    </html>
    """
    parsed_data = parse_exam_html(html_ejemplo)
    import json
    print(json.dumps(parsed_data, indent=4))
