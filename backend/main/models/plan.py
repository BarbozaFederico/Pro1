from main.extensions import db


class Plan(db.Model):
    __tablename__ = "plan"

    id_plan = db.Column(db.BigInteger, primary_key=True)
    id_ficha = db.Column(
        db.BigInteger,
        db.ForeignKey("ficha.id_ficha"),
        unique=True,
        nullable=False,
    )
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    objetivo = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)
    estado = db.Column(db.String(20), nullable=False)
    observaciones = db.Column(db.Text, nullable=False)

    ficha = db.relationship("Ficha", back_populates="plan")

    def to_json(self):
        plan_json = {
            "id_plan": self.id_plan,
            "id_ficha": self.id_ficha,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "objetivo": self.objetivo,
            "fecha_inicio": self.fecha_inicio.isoformat()
            if self.fecha_inicio
            else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "estado": self.estado,
            "observaciones": self.observaciones,
        }
        return plan_json
