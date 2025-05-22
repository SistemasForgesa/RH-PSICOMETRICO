from flask import Blueprint, render_template, request, redirect, url_for

apply_bp = Blueprint('apply', __name__)

@apply_bp.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        # Aquí manejaremos la lógica cuando se envíe el formulario
        nombre_aspirante = request.form.get('nombre_aspirante')
        edad = request.form.get('edad')
        puesto = request.form.get('puesto')
        escolaridad = request.form.get('escolaridad')
        examenes_seleccionados = request.form.getlist('examenes')

        # TODO: Guardar los datos del aspirante y los exámenes seleccionados
        # TODO: Redirigir a la página para realizar los exámenes

        print(f"Datos del aspirante: {nombre_aspirante}, {edad}, {puesto}, {escolaridad}")
        print(f"Exámenes seleccionados: {examenes_seleccionados}")

        # Por ahora, solo redirigimos a una página de confirmación temporal
        return redirect(url_for('apply.confirmation'))

    # TODO: Obtener la lista de exámenes disponibles para mostrar en el formulario
    examenes_disponibles = ["Examen de Dinamismo", "Examen de Liderazgo"] # Datos de ejemplo

    return render_template('apply.html', examenes=examenes_disponibles)

@apply_bp.route('/apply/confirmation')
def confirmation():
    return "Formulario recibido. ¡Continuaremos con la aplicación del examen!"
