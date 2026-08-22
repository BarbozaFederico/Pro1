from datetime import date

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from main.extensions import db
from main.models import FichaModel, PlanModel


def siguiente_id_plan():
    ultimo_id = db.session.query(db.func.max(PlanModel.id_plan)).scalar()
    return (ultimo_id or 0) + 1


class planes(Resource):
    def get(self):
        planes_encontrados = db.session.query(PlanModel).all()

        return {
            "planes": [
                plan_encontrado.to_json()
                for plan_encontrado in planes_encontrados
            ]
        }, 200

    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            ficha = db.session.get(FichaModel, datos["id_ficha"])
            if not ficha:
                return {"mensaje": "Ficha no encontrada"}, 404

            fecha_inicio = date.fromisoformat(datos["fecha_inicio"])
            valor_fecha_fin = datos.get("fecha_fin")
            fecha_fin = (
                date.fromisoformat(valor_fecha_fin)
                if valor_fecha_fin
                else None
            )

            if fecha_fin and fecha_fin < fecha_inicio:
                return {
                    "mensaje": "La fecha de fin no puede ser anterior al inicio"
                }, 400

            nuevo_plan = PlanModel(
                id_plan=siguiente_id_plan(),
                id_ficha=datos["id_ficha"],
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                objetivo=datos["objetivo"],
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=datos.get("estado", "activo"),
                observaciones=datos.get("observaciones", ""),
            )

            db.session.add(nuevo_plan)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Hay una fecha con formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "La ficha ya tiene un plan"}, 400

        return nuevo_plan.to_json(), 201


class plan(Resource):
    def get(self, id):
        plan_encontrado = db.session.get(PlanModel, id)

        if not plan_encontrado:
            return {"mensaje": "Plan no encontrado"}, 404

        return plan_encontrado.to_json(), 200

    def put(self, id):
        plan_encontrado = db.session.get(PlanModel, id)

        if not plan_encontrado:
            return {"mensaje": "Plan no encontrado"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        if "id_ficha" in datos:
            return {"mensaje": "No se puede cambiar la ficha del plan"}, 400

        campos = {
            "nombre",
            "descripcion",
            "objetivo",
            "estado",
            "observaciones",
        }

        try:
            for campo, valor in datos.items():
                if campo in campos:
                    setattr(plan_encontrado, campo, valor)

            if "fecha_inicio" in datos:
                plan_encontrado.fecha_inicio = date.fromisoformat(
                    datos["fecha_inicio"]
                )

            if "fecha_fin" in datos:
                valor = datos["fecha_fin"]
                plan_encontrado.fecha_fin = (
                    date.fromisoformat(valor) if valor else None
                )

            if (
                plan_encontrado.fecha_fin
                and plan_encontrado.fecha_fin < plan_encontrado.fecha_inicio
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
            return {"mensaje": "No se pudo actualizar el plan"}, 400

        return plan_encontrado.to_json(), 200

    def delete(self, id):
        plan_encontrado = db.session.get(PlanModel, id)

        if not plan_encontrado:
            return {"mensaje": "Plan no encontrado"}, 404

        try:
            db.session.delete(plan_encontrado)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo eliminar el plan"}, 400

        return {"mensaje": "Plan eliminado con éxito"}, 200
