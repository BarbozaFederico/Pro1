from datetime import date, datetime

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from main.extensions import db
from main.models import PacienteModel, ProfesionalModel


def buscar_usuario(id, tipo=None):
    if tipo == "paciente":
        return db.session.get(PacienteModel, id), "paciente"

    if tipo == "profesional":
        return db.session.get(ProfesionalModel, id), "profesional"

    if tipo:
        return None, "tipo_invalido"

    paciente = db.session.get(PacienteModel, id)
    profesional = db.session.get(ProfesionalModel, id)

    if paciente and profesional:
        return None, "ambiguo"

    if paciente:
        return paciente, "paciente"

    if profesional:
        return profesional, "profesional"

    return None, None


def siguiente_id_usuario():
    ultimo_paciente = db.session.query(
        db.func.max(PacienteModel.id_paciente)
    ).scalar()
    ultimo_profesional = db.session.query(
        db.func.max(ProfesionalModel.id_profesional)
    ).scalar()

    return max(ultimo_paciente or 0, ultimo_profesional or 0) + 1


def usuario_a_json(usuario, tipo):
    usuario_json = usuario.to_json()
    usuario_json["tipo"] = tipo

    if tipo == "paciente":
        usuario_json["id"] = usuario.id_paciente
        usuario_json["rol"] = "USER"
    else:
        usuario_json["id"] = usuario.id_profesional

    return usuario_json


def existe_en_otra_tabla(datos, tipo):
    email = datos.get("email")
    dni = datos.get("dni")

    if tipo == "paciente":
        modelo = ProfesionalModel
    else:
        modelo = PacienteModel

    if email and db.session.query(modelo).filter_by(email=email).first():
        return True

    if dni and db.session.query(modelo).filter_by(dni=dni).first():
        return True

    return False


def crear_paciente(datos, id_usuario):
    fecha_nacimiento = date.fromisoformat(datos["fecha_nacimiento"])
    if fecha_nacimiento > date.today():
        raise ValueError

    return PacienteModel(
        id_paciente=id_usuario,
        id_profesional_validador=datos.get("id_profesional_validador"),
        dni=datos["dni"],
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        fecha_nacimiento=fecha_nacimiento,
        domicilio=datos["domicilio"],
        telefono=datos["telefono"],
        email=datos["email"],
        password_hash=generate_password_hash(datos["password"]),
        estado=datos.get("estado", "pendiente"),
        fecha_registro=datetime.now(),
        fecha_validacion=None,
    )


def crear_profesional(datos, id_usuario):
    return ProfesionalModel(
        id_profesional=id_usuario,
        dni=datos["dni"],
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        matricula=datos["matricula"],
        especialidad=datos["especialidad"],
        email=datos["email"],
        telefono=datos["telefono"],
        password_hash=generate_password_hash(datos["password"]),
        rol=datos.get("rol", "PROFESIONAL").upper(),
        estado=datos.get("estado", "activo"),
        fecha_alta=datetime.now(),
    )


class usuario(Resource):
    def get(self, id):
        usuario_encontrado, tipo = buscar_usuario(id, request.args.get("tipo"))

        if tipo == "tipo_invalido":
            return {"mensaje": "El tipo debe ser paciente o profesional"}, 400

        if tipo == "ambiguo":
            return {
                "mensaje": "Indique ?tipo=paciente o ?tipo=profesional"
            }, 409

        if not usuario_encontrado:
            return {"mensaje": "Usuario no encontrado"}, 404

        return usuario_a_json(usuario_encontrado, tipo), 200

    def put(self, id):
        usuario_encontrado, tipo = buscar_usuario(id, request.args.get("tipo"))

        if tipo == "tipo_invalido":
            return {"mensaje": "El tipo debe ser paciente o profesional"}, 400

        if tipo == "ambiguo":
            return {
                "mensaje": "Indique ?tipo=paciente o ?tipo=profesional"
            }, 409

        if not usuario_encontrado:
            return {"mensaje": "Usuario no encontrado"}, 404

        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        if existe_en_otra_tabla(datos, tipo):
            return {"mensaje": "El DNI o email pertenece a otro usuario"}, 400

        try:
            if tipo == "paciente":
                campos = {
                    "id_profesional_validador",
                    "dni",
                    "nombre",
                    "apellido",
                    "domicilio",
                    "telefono",
                    "email",
                    "estado",
                }

                if "id_profesional_validador" in datos:
                    id_validador = datos["id_profesional_validador"]
                    if id_validador is not None and not db.session.get(
                        ProfesionalModel, id_validador
                    ):
                        return {"mensaje": "Profesional no encontrado"}, 404

                for campo, valor in datos.items():
                    if campo in campos:
                        setattr(usuario_encontrado, campo, valor)

                if "fecha_nacimiento" in datos:
                    fecha_nacimiento = date.fromisoformat(
                        datos["fecha_nacimiento"]
                    )
                    if fecha_nacimiento > date.today():
                        raise ValueError
                    usuario_encontrado.fecha_nacimiento = fecha_nacimiento

                if "fecha_validacion" in datos:
                    valor = datos["fecha_validacion"]
                    usuario_encontrado.fecha_validacion = (
                        datetime.fromisoformat(valor) if valor else None
                    )

            else:
                campos = {
                    "dni",
                    "nombre",
                    "apellido",
                    "matricula",
                    "especialidad",
                    "email",
                    "telefono",
                    "rol",
                    "estado",
                }

                for campo, valor in datos.items():
                    if campo in campos:
                        setattr(usuario_encontrado, campo, valor)

            if "password" in datos:
                usuario_encontrado.password_hash = generate_password_hash(
                    datos["password"]
                )

            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Hay una fecha con formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "El DNI, email o matrícula ya existe"}, 400

        return usuario_a_json(usuario_encontrado, tipo), 200

    def delete(self, id):
        usuario_encontrado, tipo = buscar_usuario(id, request.args.get("tipo"))

        if tipo == "tipo_invalido":
            return {"mensaje": "El tipo debe ser paciente o profesional"}, 400

        if tipo == "ambiguo":
            return {
                "mensaje": "Indique ?tipo=paciente o ?tipo=profesional"
            }, 409

        if not usuario_encontrado:
            return {"mensaje": "Usuario no encontrado"}, 404

        try:
            usuario_encontrado.estado = "suspendido"
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "No se pudo suspender el usuario"}, 400

        return {
            "mensaje": "Usuario suspendido con éxito",
            "usuario": usuario_a_json(usuario_encontrado, tipo),
        }, 200


class usuarios(Resource):
    def get(self):
        pacientes = db.session.query(PacienteModel).all()
        profesionales = db.session.query(ProfesionalModel).all()

        listado = []

        for paciente in pacientes:
            listado.append(usuario_a_json(paciente, "paciente"))

        for profesional in profesionales:
            listado.append(usuario_a_json(profesional, "profesional"))

        return {"usuarios": listado}, 200

    def post(self):
        datos = request.get_json() or {}
        if not isinstance(datos, dict):
            return {"mensaje": "El JSON debe ser un objeto"}, 400

        tipo = datos.get("tipo", "paciente")
        if not isinstance(tipo, str):
            return {"mensaje": "El tipo debe ser paciente o profesional"}, 400

        tipo = tipo.lower()

        try:
            id_usuario = siguiente_id_usuario()

            if tipo == "paciente":
                id_validador = datos.get("id_profesional_validador")
                if id_validador is not None and not db.session.get(
                    ProfesionalModel, id_validador
                ):
                    return {"mensaje": "Profesional no encontrado"}, 404

                nuevo_usuario = crear_paciente(datos, id_usuario)
            elif tipo == "profesional":
                nuevo_usuario = crear_profesional(datos, id_usuario)
            else:
                return {
                    "mensaje": "El tipo debe ser paciente o profesional"
                }, 400

            if existe_en_otra_tabla(datos, tipo):
                return {"mensaje": "El DNI o email ya está registrado"}, 400

            db.session.add(nuevo_usuario)
            db.session.commit()
        except KeyError as error:
            db.session.rollback()
            return {"mensaje": f"Falta el campo {error.args[0]}"}, 400
        except (TypeError, ValueError):
            db.session.rollback()
            return {"mensaje": "Hay una fecha con formato incorrecto"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "El DNI, email o matrícula ya existe"}, 400

        return usuario_a_json(nuevo_usuario, tipo), 201
