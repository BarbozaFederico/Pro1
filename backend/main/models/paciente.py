from main.extensions import db


class Paciente(db.Model):
    __tablename__ = "paciente"

    id_paciente = db.Column(db.BigInteger, primary_key=True)
    id_profesional_validador = db.Column(
        db.BigInteger,
        db.ForeignKey("profesional.id_profesional"),
        nullable=True,
    )
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    domicilio = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(25), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)
    fecha_validacion = db.Column(db.DateTime, nullable=True)

    profesional_validador = db.relationship(
        "Profesional", back_populates="pacientes_validados"
    )
    ficha = db.relationship("Ficha", back_populates="paciente", uselist=False)
    notificaciones = db.relationship("Notificacion", back_populates="paciente")

    def to_json(self):
        paciente_json = {
            "id_paciente": self.id_paciente,
            "id_profesional_validador": self.id_profesional_validador,
            "dni": self.dni,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "fecha_nacimiento": self.fecha_nacimiento.isoformat()
            if self.fecha_nacimiento
            else None,
            "domicilio": self.domicilio,
            "telefono": self.telefono,
            "email": self.email,
            "estado": self.estado,
            "fecha_registro": self.fecha_registro.isoformat()
            if self.fecha_registro
            else None,
            "fecha_validacion": self.fecha_validacion.isoformat()
            if self.fecha_validacion
            else None,
        }
        return paciente_json
