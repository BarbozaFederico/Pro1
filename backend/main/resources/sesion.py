from datetime import datetime

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from main.extensions import db
from main.models import FichaModel, SesionModel


def siguiente_id_sesion():
    ultimo_id = db.session.query(db.func.max(SesionModel.id_sesion)).scalar()
    return (ultimo_id or 0) + 1


def convertir_escala_dolor(valor):
    if valor is None:
        return None

    escala = int(valor)
    if escala < 0 or escala > 10:
        raise ValueError

    return escala


class sesiones(Resource):
    def get(self):
        consulta = db.session.query(SesionModel)

        if "id_ficha" in request.args:
            consulta = consulta.filter_by(id_ficha=request.args["id_ficha"])

        sesiones_encontradas = consulta.all()

        return {
            "sesiones": [sesion.to_json() for sesion in sesiones_encontradas]
        }, 200

    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            ficha = db.session.get(FichaModel, datos["id_ficha"])
            if not ficha:
                return {"mensaje": "Ficha no encontrada"}, 404

            valor_fecha = datos.get("fecha_hora")

            nueva_sesion = SesionModel(
                id_sesion=siguiente_id_sesion(),
                id_ficha=datos["id_ficha"],
                fecha_hora=(
                    datetime.fromisoformat(valor_fecha)
                    if valor_fecha
                    else datetime.now()
                ),
                nota_evolucion=datos["nota_evolucion"],
                escala_dolor=convertir_escala_dolor(
                    datos.get("escala_dolor")
                ),
                observaciones=datos.get("observaciones", ""),
            )

            db.session.add(nueva_sesion)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "La fecha o la escala de dolor es incorrecta"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo crear la sesión"}, 400

        return nueva_sesion.to_json(), 201


class sesion(Resource):
    def get(self, id):
        sesion_encontrada = db.session.get(SesionModel, id)

        if not sesion_encontrada:
            return {"mensaje": "Sesión no encontrada"}, 404

        return sesion_encontrada.to_json(), 200

    def put(self, id):
        sesion_encontrada = db.session.get(SesionModel, id)

        if not sesion_encontrada:
            return {"mensaje": "Sesión no encontrada"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        if "id_ficha" in datos:
            return {"mensaje": "No se puede cambiar la ficha de la sesión"}, 400

        campos = {"nota_evolucion", "observaciones"}

        try:
            for campo, valor in datos.items():
                if campo in campos:
                    setattr(sesion_encontrada, campo, valor)

            if "fecha_hora" in datos:
                sesion_encontrada.fecha_hora = datetime.fromisoformat(
                    datos["fecha_hora"]
                )

            if "escala_dolor" in datos:
                sesion_encontrada.escala_dolor = convertir_escala_dolor(
                    datos["escala_dolor"]
                )

            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "La fecha o la escala de dolor es incorrecta"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo actualizar la sesión"}, 400

        return sesion_encontrada.to_json(), 200

    def delete(self, id):
        sesion_encontrada = db.session.get(SesionModel, id)

        if not sesion_encontrada:
            return {"mensaje": "Sesión no encontrada"}, 404

        try:
            db.session.delete(sesion_encontrada)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo eliminar la sesión"}, 400

        return {"mensaje": "Sesión eliminada con éxito"}, 200
