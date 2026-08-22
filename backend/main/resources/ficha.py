from datetime import datetime

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from main.extensions import db
from main.models import FichaModel, PacienteModel, ProfesionalModel


def siguiente_id_ficha():
    ultimo_id = db.session.query(db.func.max(FichaModel.id_ficha)).scalar()
    return (ultimo_id or 0) + 1


class ficha(Resource):
    def get(self, id):
        ficha_encontrada = db.session.get(FichaModel, id)

        if not ficha_encontrada:
            return {"mensaje": "Ficha no encontrada"}, 404

        return ficha_encontrada.to_json(), 200

    def put(self, id):
        ficha_encontrada = db.session.get(FichaModel, id)

        if not ficha_encontrada:
            return {"mensaje": "Ficha no encontrada"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        if "id_paciente" in datos or "id_profesional_creador" in datos:
            return {
                "mensaje": "No se pueden cambiar los usuarios de la ficha"
            }, 400

        campos = {
            "diagnostico",
            "antecedentes",
            "objetivos",
            "observaciones",
            "estado",
        }

        try:
            for campo, valor in datos.items():
                if campo in campos:
                    setattr(ficha_encontrada, campo, valor)

            if "fecha_creacion" in datos:
                ficha_encontrada.fecha_creacion = datetime.fromisoformat(
                    datos["fecha_creacion"]
                )

            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "La fecha tiene un formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "El paciente ya tiene una ficha"}, 400

        return ficha_encontrada.to_json(), 200

    def delete(self, id):
        ficha_encontrada = db.session.get(FichaModel, id)

        if not ficha_encontrada:
            return {"mensaje": "Ficha no encontrada"}, 404

        try:
            db.session.delete(ficha_encontrada)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {
                "mensaje": "No se puede eliminar una ficha que tiene datos asociados"
            }, 400

        return {"mensaje": "Ficha eliminada con éxito"}, 200


class fichas(Resource):
    def get(self):
        fichas_encontradas = db.session.query(FichaModel).all()

        return {
            "fichas": [
                ficha_encontrada.to_json()
                for ficha_encontrada in fichas_encontradas
            ]
        }, 200

    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            paciente = db.session.get(PacienteModel, datos["id_paciente"])
            if not paciente:
                return {"mensaje": "Paciente no encontrado"}, 404

            profesional = db.session.get(
                ProfesionalModel, datos["id_profesional_creador"]
            )
            if not profesional:
                return {"mensaje": "Profesional no encontrado"}, 404

            fecha_creacion = datos.get("fecha_creacion")

            nueva_ficha = FichaModel(
                id_ficha=siguiente_id_ficha(),
                id_paciente=datos["id_paciente"],
                id_profesional_creador=datos["id_profesional_creador"],
                fecha_creacion=(
                    datetime.fromisoformat(fecha_creacion)
                    if fecha_creacion
                    else datetime.now()
                ),
                diagnostico=datos["diagnostico"],
                antecedentes=datos.get("antecedentes", ""),
                objetivos=datos.get("objetivos", ""),
                observaciones=datos.get("observaciones", ""),
                estado=datos.get("estado", "activa"),
            )

            db.session.add(nueva_ficha)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "La fecha tiene un formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "El paciente ya tiene una ficha"}, 400

        return nueva_ficha.to_json(), 201
