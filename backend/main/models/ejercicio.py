from main.extensions import db


class Ejercicio(db.Model):
    __tablename__ = "ejercicio"

    id_ejercicio = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    instrucciones = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    url_video = db.Column(db.String(500), nullable=False)
    activo = db.Column(db.Boolean, nullable=False)

    asignaciones_rutinas = db.relationship(
        "Ejercicio_Rutina", back_populates="ejercicio"
    )

    def to_json(self):
        ejercicio_json = {
            "id_ejercicio": self.id_ejercicio,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "instrucciones": self.instrucciones,
            "categoria": self.categoria,
            "url_video": self.url_video,
            "activo": self.activo,
        }
        return ejercicio_json
