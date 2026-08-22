from main.extensions import db


class Rutina(db.Model):
    __tablename__ = "rutina"

    id_rutina = db.Column(db.BigInteger, primary_key=True)
    id_ficha = db.Column(
        db.BigInteger, db.ForeignKey("ficha.id_ficha"), nullable=False
    )
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)
    frecuencia = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    ficha = db.relationship("Ficha", back_populates="rutinas")
    asignaciones_ejercicios = db.relationship(
        "Ejercicio_Rutina", back_populates="rutina"
    )

    def to_json(self):
        rutina_json = {
            "id_rutina": self.id_rutina,
            "id_ficha": self.id_ficha,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "fecha_inicio": self.fecha_inicio.isoformat()
            if self.fecha_inicio
            else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "frecuencia": self.frecuencia,
            "estado": self.estado,
        }
        return rutina_json
