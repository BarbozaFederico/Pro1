from main.extensions import db


class Sesion(db.Model):
    __tablename__ = "sesion"

    id_sesion = db.Column(db.BigInteger, primary_key=True)
    id_ficha = db.Column(
        db.BigInteger, db.ForeignKey("ficha.id_ficha"), nullable=False
    )
    fecha_hora = db.Column(db.DateTime, nullable=False)
    nota_evolucion = db.Column(db.Text, nullable=False)
    escala_dolor = db.Column(db.SmallInteger, nullable=True)
    observaciones = db.Column(db.Text, nullable=False)

    ficha = db.relationship("Ficha", back_populates="sesiones")

    def to_json(self):
        sesion_json = {
            "id_sesion": self.id_sesion,
            "id_ficha": self.id_ficha,
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "nota_evolucion": self.nota_evolucion,
            "escala_dolor": self.escala_dolor,
            "observaciones": self.observaciones,
        }
        return sesion_json
