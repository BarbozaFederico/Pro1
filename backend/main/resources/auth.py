import secrets
from datetime import date, datetime

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from main.extensions import db
from main.models import PacienteModel, ProfesionalModel


TOKENS = {}


def siguiente_id_usuario():
    ultimo_paciente = db.session.query(
        db.func.max(PacienteModel.id_paciente)
    ).scalar()
    ultimo_profesional = db.session.query(
        db.func.max(ProfesionalModel.id_profesional)
    ).scalar()

    return max(ultimo_paciente or 0, ultimo_profesional or 0) + 1


class login(Resource):
    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        email = datos.get("email")
        password = datos.get("password")

        if not email or not password:
            return {"mensaje": "Email y password son obligatorios"}, 400

        usuario_encontrado = db.session.query(PacienteModel).filter_by(
            email=email
        ).first()
        tipo = "paciente"
        rol = "USER"

        if not usuario_encontrado:
            usuario_encontrado = db.session.query(ProfesionalModel).filter_by(
                email=email
            ).first()
            tipo = "profesional"
            rol = usuario_encontrado.rol if usuario_encontrado else None

        if not usuario_encontrado or not check_password_hash(
            usuario_encontrado.password_hash, password
        ):
            return {"mensaje": "Email o password incorrectos"}, 401

        if usuario_encontrado.estado.lower() in {
            "inactivo",
            "pendiente",
            "suspendido",
        }:
            return {"mensaje": "El usuario todavía no está habilitado"}, 403

        usuario_json = usuario_encontrado.to_json()
        if tipo == "paciente":
            id_usuario = usuario_encontrado.id_paciente
        else:
            id_usuario = usuario_encontrado.id_profesional

        usuario_json["id"] = id_usuario
        usuario_json["tipo"] = tipo
        usuario_json["rol"] = rol

        token = secrets.token_hex(32)
        TOKENS[token] = {
            "id": id_usuario,
            "tipo": tipo,
            "rol": rol,
        }

        return {
            "token": token,
            "tipo": tipo,
            "rol": rol,
            "usuario": usuario_json,
        }, 200


class Register(Resource):
    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        try:
            profesional_con_email = db.session.query(
                ProfesionalModel
            ).filter_by(email=datos["email"]).first()
            profesional_con_dni = db.session.query(
                ProfesionalModel
            ).filter_by(dni=datos["dni"]).first()

            if profesional_con_email or profesional_con_dni:
                return {"mensaje": "El DNI o email ya está registrado"}, 400

            fecha_nacimiento = date.fromisoformat(datos["fecha_nacimiento"])
            if fecha_nacimiento > date.today():
                return {
                    "mensaje": "La fecha de nacimiento no puede ser futura"
                }, 400

            nuevo_paciente = PacienteModel(
                id_paciente=siguiente_id_usuario(),
                id_profesional_validador=None,
                dni=datos["dni"],
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                fecha_nacimiento=fecha_nacimiento,
                domicilio=datos["domicilio"],
                telefono=datos["telefono"],
                email=datos["email"],
                password_hash=generate_password_hash(datos["password"]),
                estado="pendiente",
                fecha_registro=datetime.now(),
                fecha_validacion=None,
            )

            db.session.add(nuevo_paciente)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "La fecha tiene un formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "El DNI o email ya está registrado"}, 400

        paciente_json = nuevo_paciente.to_json()
        paciente_json["id"] = nuevo_paciente.id_paciente
        paciente_json["tipo"] = "paciente"
        paciente_json["rol"] = "USER"

        return paciente_json, 201


class logout(Resource):
    def post(self):
        autorizacion = request.headers.get("Authorization", "")

        if not autorizacion.startswith("Bearer "):
            return {"mensaje": "Token inválido"}, 401

        token = autorizacion[7:].strip()

        if not token or token not in TOKENS:
            return {"mensaje": "Token inválido"}, 401

        del TOKENS[token]

        return {"mensaje": "Sesión cerrada con éxito"}, 200
