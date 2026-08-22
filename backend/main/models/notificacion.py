from main.extensions import db


class Notificacion(db.Model):
    __tablename__ = "notificacion"

    id_notificacion = db.Column(db.BigInteger, primary_key=True)
    id_paciente = db.Column(
        db.BigInteger,
        db.ForeignKey("paciente.id_paciente"),
        nullable=False,
    )
    titulo = db.Column(db.String(150), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    fecha_lectura = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(20), nullable=False)

    paciente = db.relationship("Paciente", back_populates="notificaciones")

    def to_json(self):
        notificacion_json = {
            "id_notificacion": self.id_notificacion,
            "id_paciente": self.id_paciente,
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "tipo": self.tipo,
            "fecha_creacion": self.fecha_creacion.isoformat()
            if self.fecha_creacion
            else None,
            "fecha_lectura": self.fecha_lectura.isoformat()
            if self.fecha_lectura
            else None,
            "estado": self.estado,
        }
        return notificacion_json
