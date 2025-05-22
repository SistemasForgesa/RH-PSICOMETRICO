from flask import Blueprint, render_template, request, redirect, url_for
# TODO: Importar MongoClient y ObjectId si aún no están importados en este archivo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from app.services.exam_parser import parse_exam_html # <--- Agrega esta línea


# Cargar variables de entorno
load_dotenv()

# Configurar la conexión a MongoDB
# Asegúrate de que MONGO_URI esté configurada en tu archivo .env o en tu entorno
client = MongoClient(os.getenv("MONGO_URI"))
db = client["rh"] # Reemplaza "rh" si tu base de datos tiene otro nombre
exams_collection = db["exams"]
candidates_collection = db["candidates"] # Colección para guardar datos de aspirantes y sus respuestas

apply_bp = Blueprint('apply', __name__)

@apply_bp.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        nombre_aspirante = request.form.get('nombre_aspirante')
        edad = request.form.get('edad')
        puesto = request.form.get('puesto')
        escolaridad = request.form.get('escolaridad')
        examenes_seleccionados_ids = request.form.getlist('examenes')

        # TODO: Validar que se seleccionaron exámenes y que los datos del aspirante son válidos

        # Guardar los datos iniciales del aspirante en la base de datos
        aspirante_data = {
            "nombre": nombre_aspirante,
            "edad": edad,
            "puesto": puesto,
            "escolaridad": escolaridad,
            "examenes_pendientes": examenes_seleccionados_ids, # Guardamos los IDs de los exámenes a realizar
            "resultados": {} # Aquí guardaremos los resultados una vez finalizados los exámenes
        }
        insert_result = candidates_collection.insert_one(aspirante_data)
        aspirant_id = str(insert_result.inserted_id)

        # Redirigir para resolver el primer examen seleccionado
        if examenes_seleccionados_ids:
            primer_examen_id = examenes_seleccionados_ids[0]
            return redirect(url_for('apply.solve_exam', aspirant_id=aspirant_id, exam_id=primer_examen_id))
        else:
            # Manejar el caso donde no se seleccionan exámenes (aunque el frontend debería validarlo)
            return "Error: No se seleccionaron exámenes para aplicar.", 400

    # Obtener la lista de exámenes disponibles (ID y nombre) de la base de datos
    examenes_disponibles_cursor = exams_collection.find({}, {"_id": 1, "nombre": 1})
    examenes_disponibles = [{"id": str(examen["_id"]), "nombre": examen["nombre"]} for examen in examenes_disponibles_cursor]


    return render_template('apply.html', examenes=examenes_disponibles)

# Nueva ruta para resolver un examen
@apply_bp.route('/apply/solve/<aspirant_id>/<exam_id>', methods=['GET', 'POST'])
def solve_exam(aspirant_id, exam_id):
    # TODO: Añadir manejo de errores si aspirant_id o exam_id no son válidos

    aspirante = candidates_collection.find_one({"_id": ObjectId(aspirant_id)})
    if not aspirante:
        return "Error: Aspirante no encontrado.", 404

    examen = exams_collection.find_one({"_id": ObjectId(exam_id)})
    if not examen:
        return "Error: Examen no encontrado.", 404

    if request.method == 'POST':
        # Recolectar las respuestas del formulario para el examen actual
        respuestas_examen_actual = {}
        # Iterar sobre las preguntas esperadas del examen para recolectar las respuestas
        # Esto asume que la estructura del examen en DB incluye las preguntas y sus IDs/nombres
        # TODO: Asegurar que la estructura de las preguntas en la DB permita identificar las respuestas del formulario
        for key, value in request.form.items():
             # TODO: Implementar lógica para asociar claves del formulario con preguntas del examen
             # Por ahora, guardamos todo el formulario para este examen ID
             respuestas_examen_actual[key] = value


        # TODO: Validar y procesar las respuestas
        # TODO: Guardar las respuestas para este examen asociadas al aspirante
        # TODO: Calcular o preparar para calcular la calificación de este examen
        # TODO: Remover el examen de la lista de 'examenes_pendientes' del aspirante

        # Lógica para avanzar al siguiente examen o finalizar
        examenes_pendientes = aspirante.get("examenes_pendientes", [])
        try:
             examenes_pendientes.remove(exam_id) # Removemos el examen actual de la lista

             # TODO: Guardar las respuestas parciales y la lista actualizada de examenes_pendientes
             # candidates_collection.update_one(
             #     {"_id": ObjectId(aspirant_id)},
             #     {"$set": {"examenes_pendientes": examenes_pendientes, f"respuestas.{exam_id}": respuestas_examen_actual}} # Ejemplo de cómo guardar respuestas
             # )


             if examenes_pendientes:
                 siguiente_examen_id = examenes_pendientes[0]
                 # Redirigir al siguiente examen
                 return redirect(url_for('apply.solve_exam', aspirant_id=aspirant_id, exam_id=siguiente_examen_id))
             else:
                 # Si no hay más exámenes pendientes, finalizar el proceso y redirigir a resultados o confirmación
                 # TODO: Implementar lógica de finalización (calificación total, etc.)
                 return redirect(url_for('apply.application_complete', aspirant_id=aspirant_id)) # Redirigir a una página de finalización


        except ValueError:
             # Manejar el caso si el exam_id no estaba en examenes_pendientes (posible error o acceso directo)
             return "Error: Este examen ya no está pendiente para este aspirante.", 400


    # Método GET: Mostrar las preguntas del examen
    # El contenido del examen (HTML convertido) está en examen["contenido_html"]
    # Necesitamos parsear este HTML para extraer preguntas y opciones

    # TODO: Implementar la lógica para parsear examen["contenido_html"] y extraer preguntas y opciones
    # Esto dependerá de cómo se estructuró el HTML durante la conversión de .docx

    # Datos de ejemplo para la plantilla (deberían venir del parseo del HTML del examen)
    examen_para_plantilla = {
        "nombre": examen.get("nombre", "Examen sin nombre"),
        "preguntas": [
            {"id": "q1", "texto": "¿Cuál es la capital de Francia?", "opciones": ["París", "Londres", "Berlín"]},
            {"id": "q2", "texto": "¿Cuánto es 2 + 2?", "opciones": ["3", "4", "5"]}
        ]
    }


    return render_template('solve_exam.html',
                           examen=examen_para_plantilla,
                           aspirant_id=aspirant_id,
                           exam_id=exam_id)


# Nueva ruta para manejar la finalización de la aplicación de exámenes
@apply_bp.route('/apply/complete/<aspirant_id>')
def application_complete(aspirant_id):
     # TODO: Mostrar un mensaje de finalización o redirigir a la vista de resultados (si aplica inmediatamente)
     # TODO: Trigger la calificación final de todos los exámenes del aspirante

     aspirante = candidates_collection.find_one({"_id": ObjectId(aspirant_id)})
     if not aspirante:
         return "Error: Aspirante no encontrado.", 404

     return render_template('application_complete.html', aspirante=aspirante) # Necesitaremos crear esta plantilla


@apply_bp.route('/apply/confirmation')
def confirmation():
    return "Formulario de datos iniciales recibido." # Mensaje actualizado


# ... (otras rutas si existen)
