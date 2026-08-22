from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from main.extensions import db
from main.models import EjercicioModel


def siguiente_id_ejercicio():
    ultimo_id = db.session.query(
        db.func.max(EjercicioModel.id_ejercicio)
    ).scalar()
    return (ultimo_id or 0) + 1


class ejercicios(Resource):
    def get(self):
        consulta = db.session.query(EjercicioModel)
        parametros = request.args

        if "categoria" in parametros:
            consulta = consulta.filter_by(categoria=parametros["categoria"])

        if "activo" in parametros:
            activo = parametros["activo"].lower() == "true"
            consulta = consulta.filter_by(activo=activo)
        else:
            consulta = consulta.filter_by(activo=True)

        ejercicios_encontrados = consulta.all()

        return {
            "ejercicios": [
                ejercicio.to_json() for ejercicio in ejercicios_encontrados
            ]
        }, 200

    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            nuevo_ejercicio = EjercicioModel(
                id_ejercicio=siguiente_id_ejercicio(),
                nombre=datos["nombre"],
                descripcion=datos.get("descripcion", ""),
                instrucciones=datos["instrucciones"],
                categoria=datos["categoria"],
                url_video=datos.get("url_video", ""),
                activo=datos.get("activo", True),
            )

            db.session.add(nuevo_ejercicio)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ya existe un ejercicio con ese nombre"}, 400

        return nuevo_ejercicio.to_json(), 201


class ejercicio(Resource):
    def get(self, id):
        ejercicio_encontrado = db.session.get(EjercicioModel, id)

        if not ejercicio_encontrado:
            return {"mensaje": "Ejercicio no encontrado"}, 404

        return ejercicio_encontrado.to_json(), 200

    def put(self, id):
        ejercicio_encontrado = db.session.get(EjercicioModel, id)

        if not ejercicio_encontrado:
            return {"mensaje": "Ejercicio no encontrado"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        campos = {
            "nombre",
            "descripcion",
            "instrucciones",
            "categoria",
            "url_video",
            "activo",
        }

        try:
            for campo, valor in datos.items():
                if campo in campos:
                    setattr(ejercicio_encontrado, campo, valor)

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ya existe un ejercicio con ese nombre"}, 400

        return ejercicio_encontrado.to_json(), 200

    def delete(self, id):
        ejercicio_encontrado = db.session.get(EjercicioModel, id)

        if not ejercicio_encontrado:
            return {"mensaje": "Ejercicio no encontrado"}, 404

        ejercicio_encontrado.activo = False
        db.session.commit()

        return {
            "mensaje": "Ejercicio desactivado con éxito",
            "ejercicio": ejercicio_encontrado.to_json(),
        }, 200
