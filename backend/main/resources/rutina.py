from datetime import date

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from main.extensions import db
from main.models import EjercicioRutinaModel, FichaModel, RutinaModel


def siguiente_id_rutina():
    ultimo_id = db.session.query(db.func.max(RutinaModel.id_rutina)).scalar()
    return (ultimo_id or 0) + 1


class rutinas(Resource):
    def get(self):
        consulta = db.session.query(RutinaModel)

        if "id_ficha" in request.args:
            consulta = consulta.filter_by(id_ficha=request.args["id_ficha"])

        if "estado" in request.args:
            consulta = consulta.filter_by(estado=request.args["estado"])

        rutinas_encontradas = consulta.all()

        return {
            "rutinas": [rutina.to_json() for rutina in rutinas_encontradas]
        }, 200

    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            ficha = db.session.get(FichaModel, datos["id_ficha"])
            if not ficha:
                return {"mensaje": "Ficha no encontrada"}, 404

            valor_inicio = datos.get("fecha_inicio")
            valor_fin = datos.get("fecha_fin")
            fecha_inicio = date.fromisoformat(valor_inicio) if valor_inicio else None
            fecha_fin = date.fromisoformat(valor_fin) if valor_fin else None

            if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
                return {
                    "mensaje": "La fecha de fin no puede ser anterior al inicio"
                }, 400

            nueva_rutina = RutinaModel(
                id_rutina=siguiente_id_rutina(),
                id_ficha=datos["id_ficha"],
                nombre=datos["nombre"],
                descripcion=datos.get("descripcion", ""),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                frecuencia=datos["frecuencia"],
                estado=datos.get("estado", "activa"),
            )

            db.session.add(nueva_rutina)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Hay una fecha con formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo crear la rutina"}, 400

        return nueva_rutina.to_json(), 201


class rutina(Resource):
    def get(self, id):
        rutina_encontrada = db.session.get(RutinaModel, id)

        if not rutina_encontrada:
            return {"mensaje": "Rutina no encontrada"}, 404

        return rutina_encontrada.to_json(), 200

    def put(self, id):
        rutina_encontrada = db.session.get(RutinaModel, id)

        if not rutina_encontrada:
            return {"mensaje": "Rutina no encontrada"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        if "id_ficha" in datos:
            return {"mensaje": "No se puede cambiar la ficha de la rutina"}, 400

        campos = {"nombre", "descripcion", "frecuencia", "estado"}

        try:
            for campo, valor in datos.items():
                if campo in campos:
                    setattr(rutina_encontrada, campo, valor)

            if "fecha_inicio" in datos:
                valor = datos["fecha_inicio"]
                rutina_encontrada.fecha_inicio = (
                    date.fromisoformat(valor) if valor else None
                )

            if "fecha_fin" in datos:
                valor = datos["fecha_fin"]
                rutina_encontrada.fecha_fin = (
                    date.fromisoformat(valor) if valor else None
                )

            if (
                rutina_encontrada.fecha_inicio
                and rutina_encontrada.fecha_fin
                and rutina_encontrada.fecha_fin < rutina_encontrada.fecha_inicio
            ):
                db.session.rollback()
                return {
                    "mensaje": "La fecha de fin no puede ser anterior al inicio"
                }, 400

            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Hay una fecha con formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo actualizar la rutina"}, 400

        return rutina_encontrada.to_json(), 200

    def delete(self, id):
        rutina_encontrada = db.session.get(RutinaModel, id)

        if not rutina_encontrada:
            return {"mensaje": "Rutina no encontrada"}, 404

        try:
            asignaciones = db.session.query(EjercicioRutinaModel).filter_by(
                id_rutina=id
            ).all()

            for asignacion in asignaciones:
                db.session.delete(asignacion)

            db.session.delete(rutina_encontrada)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo eliminar la rutina"}, 400

        return {"mensaje": "Rutina eliminada con éxito"}, 200
