from main.extensions import db


class Ficha(db.Model):
    __tablename__ = "ficha"

    id_ficha = db.Column(db.BigInteger, primary_key=True)
    id_paciente = db.Column(
        db.BigInteger,
        db.ForeignKey("paciente.id_paciente"),
        unique=True,
        nullable=False,
    )
    id_profesional_creador = db.Column(
        db.BigInteger,
        db.ForeignKey("profesional.id_profesional"),
        nullable=False,
    )
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    diagnostico = db.Column(db.String(500), nullable=False)
    antecedentes = db.Column(db.Text, nullable=False)
    objetivos = db.Column(db.Text, nullable=False)
    observaciones = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    paciente = db.relationship("Paciente", back_populates="ficha")
    profesional_creador = db.relationship(
        "Profesional", back_populates="fichas_creadas"
    )
    plan = db.relationship("Plan", back_populates="ficha", uselist=False)
    sesiones = db.relationship("Sesion", back_populates="ficha")
    rutinas = db.relationship("Rutina", back_populates="ficha")

    def to_json(self):
        ficha_json = {
            "id_ficha": self.id_ficha,
            "id_paciente": self.id_paciente,
            "id_profesional_creador": self.id_profesional_creador,
            "fecha_creacion": self.fecha_creacion.isoformat()
            if self.fecha_creacion
            else None,
            "diagnostico": self.diagnostico,
            "antecedentes": self.antecedentes,
            "objetivos": self.objetivos,
            "observaciones": self.observaciones,
            "estado": self.estado,
        }
        return ficha_json
