import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_restful import Api
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from main.extensions import db
import main.models

from main.resources import (
    EjercicioResource,
    EjercicioRutinaResource,
    EjerciciosResource,
    EjerciciosRutinaResource,
    FichaResource,
    FichasResource,
    LoginResource,
    LogoutResource,
    NotificacionResource,
    NotificacionesResource,
    PlanesResource,
    PlanResource,
    RegisterResource,
    RutinaResource,
    RutinasResource,
    SesionResource,
    SesionesResource,
    UsuarioResource,
    UsuariosResource,
)

load_dotenv()

app = Flask(__name__)
api = Api(app)

database_path = os.getenv("DATABASE_PATH", "DB/")
database_name = os.getenv("DATABASE_NAME", "kinesiologia.db")
database_file = os.path.join(database_path, database_name)

if not os.path.exists(database_file):
    os.makedirs(database_path, exist_ok=True)
    with open(database_file, "a", encoding="utf-8"):
        pass

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.abspath(database_file).replace("\\", "/")
)
db.init_app(app)

api.add_resource(PlanResource, "/plan/<int:id>")
api.add_resource(PlanesResource, "/planes")
api.add_resource(UsuarioResource, "/usuario/<int:id>")
api.add_resource(UsuariosResource, "/usuarios")
api.add_resource(NotificacionResource, "/notificacion/<int:id>")
api.add_resource(NotificacionesResource, "/notificaciones")
api.add_resource(FichaResource, "/ficha/<int:id>")
api.add_resource(FichasResource, "/fichas")
api.add_resource(RutinaResource, "/rutina/<int:id>")
api.add_resource(RutinasResource, "/rutinas")
api.add_resource(SesionResource, "/sesion/<int:id>")
api.add_resource(SesionesResource, "/sesiones")
api.add_resource(LoginResource, "/login")
api.add_resource(LogoutResource, "/logout")
api.add_resource(RegisterResource, "/register")
api.add_resource(EjercicioResource, "/ejercicio/<int:id>")
api.add_resource(EjerciciosResource, "/ejercicios")
api.add_resource(
    EjerciciosRutinaResource,
    "/rutina/<int:id_rutina>/ejercicios",
)
api.add_resource(
    EjercicioRutinaResource,
    "/rutina/<int:id_rutina>/ejercicio/<int:id_ejercicio>",
)

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
    """Comprueba el acceso a la base de datos con SQLAlchemy."""
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return jsonify({"api": "ok", "base_de_datos": "error"}), 503

    return jsonify({"api": "ok", "base_de_datos": "ok"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=port,
        debug=debug,
    )
