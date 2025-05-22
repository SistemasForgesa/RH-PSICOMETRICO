from flask import Flask, render_template
# ... otras importaciones
from app.routes.rh import rh_bp # Si ya tienes este
from app.routes.results import results_bp # Si ya tienes este
from app.routes.apply import apply_bp # <--- Agrega esta línea

app = Flask(__name__)
# ... otras configuraciones

app.register_blueprint(rh_bp, url_prefix='/rh') # Si ya tienes este
app.register_blueprint(results_bp, url_prefix='/results') # Si ya tienes este
app.register_blueprint(apply_bp) # <--- Agrega esta línea

@app.route('/')
def home():
    return render_template('home.html')

# ... otras rutas
