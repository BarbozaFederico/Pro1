from main.extensions import db


class Profesional(db.Model):
    __tablename__ = "profesional"

    id_profesional = db.Column(db.BigInteger, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    matricula = db.Column(db.String(40), unique=True, nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha_alta = db.Column(db.DateTime, nullable=False)

    pacientes_validados = db.relationship(
        "Paciente", back_populates="profesional_validador"
    )
    fichas_creadas = db.relationship(
        "Ficha", back_populates="profesional_creador"
    )

    def to_json(self):
        profesional_json = {
            "id_profesional": self.id_profesional,
            "dni": self.dni,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "matricula": self.matricula,
            "especialidad": self.especialidad,
            "email": self.email,
            "telefono": self.telefono,
            "rol": self.rol,
            "estado": self.estado,
            "fecha_alta": self.fecha_alta.isoformat() if self.fecha_alta else None,
        }
        return profesional_json
