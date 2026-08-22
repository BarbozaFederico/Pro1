from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from main.extensions import db
from main.models import EjercicioModel, EjercicioRutinaModel, RutinaModel


def convertir_numero(datos, campo, obligatorio=False):
    valor = datos.get(campo)

    if valor is None:
        if obligatorio:
            raise KeyError(campo)
        return None

    numero = int(valor)
    if numero < 0:
        raise ValueError

    return numero


def asignacion_a_json(asignacion):
    asignacion_json = asignacion.to_json()

    if asignacion.ejercicio:
        asignacion_json["ejercicio"] = asignacion.ejercicio.to_json()

    return asignacion_json


class ejercicios_rutina(Resource):
    def get(self, id_rutina):
        rutina = db.session.get(RutinaModel, id_rutina)

        if not rutina:
            return {"mensaje": "Rutina no encontrada"}, 404

        asignaciones = db.session.query(EjercicioRutinaModel).filter_by(
            id_rutina=id_rutina
        ).order_by(EjercicioRutinaModel.orden).all()

        return {
            "ejercicios": [
                asignacion_a_json(asignacion) for asignacion in asignaciones
            ]
        }, 200

    def post(self, id_rutina):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            rutina = db.session.get(RutinaModel, id_rutina)
            if not rutina:
                return {"mensaje": "Rutina no encontrada"}, 404

            ejercicio = db.session.get(EjercicioModel, datos["id_ejercicio"])
            if not ejercicio:
                return {"mensaje": "Ejercicio no encontrado"}, 404

            if not ejercicio.activo:
                return {"mensaje": "El ejercicio está inactivo"}, 400

            nueva_asignacion = EjercicioRutinaModel(
                id_rutina=id_rutina,
                id_ejercicio=datos["id_ejercicio"],
                orden=convertir_numero(datos, "orden", obligatorio=True),
                series=convertir_numero(datos, "series"),
                repeticiones=convertir_numero(datos, "repeticiones"),
                duracion_segundos=convertir_numero(
                    datos, "duracion_segundos"
                ),
                descanso_segundos=convertir_numero(
                    datos, "descanso_segundos"
                ),
                carga=datos.get("carga", ""),
                observaciones=datos.get("observaciones", ""),
            )

            db.session.add(nueva_asignacion)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Los números no pueden ser negativos"}, 400
        except IntegrityError:
            db.session.rollback()
            return {
                "mensaje": "El ejercicio o el orden ya existe en la rutina"
            }, 400

        return asignacion_a_json(nueva_asignacion), 201


class ejercicio_rutina(Resource):
    def get(self, id_rutina, id_ejercicio):
        asignacion = db.session.get(
            EjercicioRutinaModel, (id_rutina, id_ejercicio)
        )

        if not asignacion:
            return {"mensaje": "Ejercicio no asignado a la rutina"}, 404

        return asignacion_a_json(asignacion), 200

    def put(self, id_rutina, id_ejercicio):
        asignacion = db.session.get(
            EjercicioRutinaModel, (id_rutina, id_ejercicio)
        )

        if not asignacion:
            return {"mensaje": "Ejercicio no asignado a la rutina"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            campos_numericos = {
                "orden",
                "series",
                "repeticiones",
                "duracion_segundos",
                "descanso_segundos",
            }

            for campo in campos_numericos:
                if campo in datos:
                    valor = convertir_numero(
                        datos, campo, obligatorio=campo == "orden"
                    )
                    setattr(asignacion, campo, valor)

            if "carga" in datos:
                asignacion.carga = datos["carga"]

            if "observaciones" in datos:
                asignacion.observaciones = datos["observaciones"]

            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Los números no pueden ser negativos"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ese orden ya existe en la rutina"}, 400

        return asignacion_a_json(asignacion), 200

    def delete(self, id_rutina, id_ejercicio):
        asignacion = db.session.get(
            EjercicioRutinaModel, (id_rutina, id_ejercicio)
        )

        if not asignacion:
            return {"mensaje": "Ejercicio no asignado a la rutina"}, 404

        try:
            db.session.delete(asignacion)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo quitar el ejercicio"}, 400

        return {"mensaje": "Ejercicio quitado de la rutina"}, 200
