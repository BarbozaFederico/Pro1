from datetime import datetime

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from main.extensions import db
from main.models import NotificacionModel, PacienteModel


def siguiente_id_notificacion():
    ultimo_id = db.session.query(
        db.func.max(NotificacionModel.id_notificacion)
    ).scalar()
    return (ultimo_id or 0) + 1


class notificaciones(Resource):
    def get(self):
        consulta = db.session.query(NotificacionModel)

        if "id_paciente" in request.args:
            consulta = consulta.filter_by(
                id_paciente=request.args["id_paciente"]
            )

        if "estado" in request.args:
            consulta = consulta.filter_by(estado=request.args["estado"])

        notificaciones_encontradas = consulta.all()

        return {
            "notificaciones": [
                notificacion.to_json()
                for notificacion in notificaciones_encontradas
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

            fecha_creacion = datos.get("fecha_creacion")
            fecha_lectura = datos.get("fecha_lectura")
            fecha_creacion_convertida = (
                datetime.fromisoformat(fecha_creacion)
                if fecha_creacion
                else datetime.now()
            )
            fecha_lectura_convertida = (
                datetime.fromisoformat(fecha_lectura)
                if fecha_lectura
                else None
            )

            if (
                fecha_lectura_convertida
                and fecha_lectura_convertida < fecha_creacion_convertida
            ):
                return {
                    "mensaje": "La lectura no puede ser anterior a la creación"
                }, 400

            nueva_notificacion = NotificacionModel(
                id_notificacion=siguiente_id_notificacion(),
                id_paciente=datos["id_paciente"],
                titulo=datos["titulo"],
                mensaje=datos["mensaje"],
                tipo=datos.get("tipo", "sistema"),
                fecha_creacion=fecha_creacion_convertida,
                fecha_lectura=fecha_lectura_convertida,
                estado=datos.get("estado", "pendiente"),
            )

            db.session.add(nueva_notificacion)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Hay una fecha con formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo crear la notificación"}, 400

        return nueva_notificacion.to_json(), 201


class notificacion(Resource):
    def get(self, id):
        notificacion_encontrada = db.session.get(NotificacionModel, id)

        if not notificacion_encontrada:
            return {"mensaje": "Notificación no encontrada"}, 404

        return notificacion_encontrada.to_json(), 200

    def put(self, id):
        notificacion_encontrada = db.session.get(NotificacionModel, id)

        if not notificacion_encontrada:
            return {"mensaje": "Notificación no encontrada"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        if "id_paciente" in datos:
            return {
                "mensaje": "No se puede cambiar el paciente de la notificación"
            }, 400

        campos = {"titulo", "mensaje", "tipo", "estado"}

        try:
            for campo, valor in datos.items():
                if campo in campos:
                    setattr(notificacion_encontrada, campo, valor)

            if "fecha_lectura" in datos:
                valor = datos["fecha_lectura"]
                notificacion_encontrada.fecha_lectura = (
                    datetime.fromisoformat(valor) if valor else None
                )
            elif datos.get("estado") == "leida":
                notificacion_encontrada.fecha_lectura = datetime.now()

            if (
                notificacion_encontrada.fecha_lectura
                and notificacion_encontrada.fecha_lectura
                < notificacion_encontrada.fecha_creacion
            ):
                db.session.rollback()
                return {
                    "mensaje": "La lectura no puede ser anterior a la creación"
                }, 400

            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "La fecha tiene un formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo actualizar la notificación"}, 400

        return notificacion_encontrada.to_json(), 200

    def delete(self, id):
        notificacion_encontrada = db.session.get(NotificacionModel, id)

        if not notificacion_encontrada:
            return {"mensaje": "Notificación no encontrada"}, 404

        try:
            db.session.delete(notificacion_encontrada)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo eliminar la notificación"}, 400

        return {"mensaje": "Notificación eliminada con éxito"}, 200
