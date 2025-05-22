from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from app.services.exam_parser import parse_exam_html # Importamos la función de parseo
# TODO: Importar funciones de calificación cuando estén listas
# from app.services.scoring import generar_resultados

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
        if not nombre_aspirante or not edad or not puesto or not escolaridad or not examenes_seleccionados_ids:
             return "Error: Faltan datos o no se seleccionaron exámenes.", 400


        # Guardar los datos iniciales del aspirante en la base de datos
        aspirante_data = {
            "nombre": nombre_aspirante,
            "edad": edad,
            "puesto": puesto,
            "escolaridad": escolaridad,
            "fecha_aplicacion": datetime.now(), # TODO: Importar datetime
            "examenes_pendientes": examenes_seleccionados_ids, # Guardamos los IDs de los exámenes a realizar
            "respuestas": {}, # Aquí guardaremos las respuestas por ID de examen
            "resultados": {} # Aquí guardaremos los resultados una vez finalizados los exámenes
        }
        insert_result = candidates_collection.insert_one(aspirante_data)
        aspirant_id = str(insert_result.inserted_id)

        # Redirigir para resolver el primer examen seleccionado
        if examenes_seleccionados_ids:
            primer_examen_id = examenes_seleccionados_ids[0]
            return redirect(url_for('apply.solve_exam', aspirant_id=aspirant_id, exam_id=primer_examen_id))
        else:
            # Esto no debería ocurrir si la validación anterior es correcta, pero es un fallback
            return "Error: No se seleccionaron exámenes para aplicar.", 400

    # Obtener la lista de exámenes disponibles (ID y nombre) de la base de datos
    examenes_disponibles_cursor = exams_collection.find({}, {"_id": 1, "nombre": 1})
    examenes_disponibles = [{"id": str(examen["_id"]), "nombre": examen["nombre"]} for examen in examenes_disponibles_cursor]


    return render_template('apply.html', examenes=examenes_disponibles)

# Nueva ruta para resolver un examen
@apply_bp.route('/apply/solve/<aspirant_id>/<exam_id>', methods=['GET', 'POST'])
def solve_exam(aspirant_id, exam_id):
    # TODO: Añadir manejo de errores si aspirant_id o exam_id no son válidos (por ejemplo, no son ObjectId válidos)
    try:
        aspirant_obj_id = ObjectId(aspirant_id)
        exam_obj_id = ObjectId(exam_id)
    except:
        return "Error: ID de aspirante o examen no válido.", 400

    aspirante = candidates_collection.find_one({"_id": aspirant_obj_id})
    if not aspirante:
        return "Error: Aspirante no encontrado.", 404

    examen = exams_collection.find_one({"_id": exam_obj_id})
    if not examen:
        return "Error: Examen no encontrado.", 404

    # Verificar si este examen está en la lista de pendientes del aspirante
    if exam_id not in aspirante.get("examenes_pendientes", []):
         # Redirigir si el examen ya fue completado o no estaba asignado
         # TODO: Podrías redirigir a una página de error o a la de resultados si ya terminó
         return f"Error: El examen con ID {exam_id} no está pendiente para este aspirante.", 400


    if request.method == 'POST':
        # Recolectar las respuestas del formulario para el examen actual
        respuestas_examen_actual = {}
        # Itera a través de los datos del formulario
        for key, value in request.form.items():
             # Captura solo las claves que empiezan con 'respuesta_pregunta_'
             if key.startswith('respuesta_pregunta_'):
                 # Extrae el ID de la pregunta del nombre de la clave
                 pregunta_id = key.replace('respuesta_pregunta_', '')
                 respuestas_examen_actual[pregunta_id] = value # Guarda la respuesta


        # TODO: Validar que se respondieron todas las preguntas del examen actual


        # Guardar las respuestas para este examen asociadas al aspirante y remover de pendientes
        examenes_pendientes = aspirante.get("examenes_pendientes", [])
        try:
             examenes_pendientes.remove(exam_id) # Removemos el examen actual de la lista

             # Construye la actualización para agregar las respuestas y actualizar pendientes
             update_data = {
                 "$set": {
                     "examenes_pendientes": examenes_pendientes,
                     f"respuestas.{exam_id}": respuestas_examen_actual # Guarda respuestas bajo la clave 'respuestas' y el ID del examen
                 }
             }

             candidates_collection.update_one(
                 {"_id": aspirant_obj_id},
                 update_data
             )


             if examenes_pendientes:
                 siguiente_examen_id = examenes_pendientes[0]
                 # Redirigir al siguiente examen
                 return redirect(url_for('apply.solve_exam', aspirant_id=aspirant_id, exam_id=siguiente_examen_id))
             else:
                 # Si no hay más exámenes pendientes, finalizar el proceso
                 # TODO: Trigger la calificación final de todos los exámenes del aspirante
                 # resultado_final = generar_resultados(aspirante["respuestas"]) # Llama a la función de calificación

                 # TODO: Guardar el resultado final en la base de datos
                 # candidates_collection.update_one(
                 #     {"_id": aspirant_obj_id},
                 #     {"$set": {"resultados": resultado_final}}
                 # )

                 return redirect(url_for('apply.application_complete', aspirant_id=aspirant_id)) # Redirigir a la página de finalización


        except ValueError:
             # Manejar el caso si el exam_id no estaba en examenes_pendientes (posible error o acceso directo)
             return "Error: Este examen ya no está pendiente para este aspirante.", 400


    # Método GET: Mostrar las preguntas del examen
    # El contenido del examen (HTML convertido) está en examen["html"] (o la clave que uses)
    html_content = examen.get("html") # Asegúrate de que la clave sea correcta


    if not html_content:
        return "Error: Contenido HTML del examen no encontrado.", 500

    # Llamar a la función de parseo para obtener la estructura del examen
    examen_para_plantilla = parse_exam_html(html_content)

    # TODO: Podrías precargar respuestas si el aspirante ya había empezado este examen


    return render_template('solve_exam.html',
                           examen=examen_para_plantilla,
                           aspirant_id=aspirant_id,
                           exam_id=exam_id)


# Nueva ruta para manejar la finalización de la aplicación de exámenes
@apply_bp.route('/apply/complete/<aspirant_id>')
def application_complete(aspirant_id):
     # TODO: Mostrar un mensaje de finalización o redirigir a la vista de resultados (si aplica inmediatamente)
     # TODO: Trigger la calificación final de todos los exámenes del aspirante (si no se hizo al terminar el último examen)

     try:
         aspirant_obj_id = ObjectId(aspirant_id)
     except:
         return "Error: ID de aspirante no válido.", 400

     aspirante = candidates_collection.find_one({"_id": aspirant_obj_id})
     if not aspirante:
         return "Error: Aspirante no encontrado.", 404

     # TODO: Renderizar una plantilla que muestre un mensaje de finalización
     # O redirigir a la página de resultados si ya está implementada y quieres mostrar los resultados inmediatamente
     return f"¡Exámenes completados para {aspirante.get('nombre', 'el aspirante')}! Resultados en proceso." # Mensaje temporal, crear application_complete.html


# Ruta de confirmación inicial (puede no ser necesaria a largo plazo)
@apply_bp.route('/apply/confirmation')
def confirmation():
    return "Formulario de datos iniciales recibido."


# TODO: Importar datetime al principio del archivo si lo necesitas para la fecha de aplicación
from datetime import datetime
