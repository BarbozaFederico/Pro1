import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_restful import Api

from main.resources import (
    FichaResource,
    FichasResource,
    LoginResource,
    NotificacionesResource,
    PlanesResource,
    PlanResource,
    RegisterResource,
    UsuarioResource,
    UsuariosResource,
    EjerciciosResource,
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
api = Api(app)

api.add_resource(PlanResource, "/plan/<int:id>")
api.add_resource(PlanesResource, "/planes")
api.add_resource(UsuarioResource, "/usuario/<int:id>")
api.add_resource(UsuariosResource, "/usuarios")
api.add_resource(NotificacionesResource, "/notificaciones")
api.add_resource(FichaResource, "/ficha/<int:id>")
api.add_resource(FichasResource, "/fichas")
api.add_resource(LoginResource, "/login")
api.add_resource(RegisterResource, "/register")
api.add_resource(EjerciciosResource, "/ejercicios")


def database_path():
    """Devuelve la ruta absoluta de la base configurada."""
    configured_path = Path(os.getenv("DATABASE_PATH", "DB/kinesiologia.db"))
    if configured_path.is_absolute():
        return configured_path
    return BASE_DIR / configured_path


@app.get("/")
def index():
    """Informa que la API se encuentra disponible."""
    return jsonify(
        {
            "aplicacion": "API del Centro de Kinesiologia",
            "estado": "activa",
        }
    )


@app.get("/health")
def health():
    """Comprueba el acceso a la base de datos SQLite."""
    try:
        with sqlite3.connect(database_path()) as connection:
            connection.execute("SELECT 1")
    except sqlite3.Error:
        return jsonify({"api": "ok", "base_de_datos": "error"}), 503

    return jsonify({"api": "ok", "base_de_datos": "ok"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=port,
        debug=debug,
    )
