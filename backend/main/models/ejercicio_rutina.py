from main.extensions import db


class Ejercicio_Rutina(db.Model):
    __tablename__ = "rutina_ejercicio"

    id_rutina = db.Column(
        db.BigInteger,
        db.ForeignKey("rutina.id_rutina"),
        primary_key=True,
    )
    id_ejercicio = db.Column(
        db.BigInteger,
        db.ForeignKey("ejercicio.id_ejercicio"),
        primary_key=True,
    )
    orden = db.Column(db.SmallInteger, nullable=False)
    series = db.Column(db.SmallInteger, nullable=True)
    repeticiones = db.Column(db.SmallInteger, nullable=True)
    duracion_segundos = db.Column(db.Integer, nullable=True)
    descanso_segundos = db.Column(db.Integer, nullable=True)
    carga = db.Column(db.String(50), nullable=False)
    observaciones = db.Column(db.Text, nullable=False)

    rutina = db.relationship("Rutina", back_populates="asignaciones_ejercicios")
    ejercicio = db.relationship("Ejercicio", back_populates="asignaciones_rutinas")

    __table_args__ = (
        db.UniqueConstraint("id_rutina", "orden", name="uq_rutina_orden"),
    )

    def to_json(self):
        ejercicio_rutina_json = {
            "id_rutina": self.id_rutina,
            "id_ejercicio": self.id_ejercicio,
            "orden": self.orden,
            "series": self.series,
            "repeticiones": self.repeticiones,
            "duracion_segundos": self.duracion_segundos,
            "descanso_segundos": self.descanso_segundos,
            "carga": self.carga,
            "observaciones": self.observaciones,
        }
        return ejercicio_rutina_json
