from app.extensions import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    items = db.relationship(
        "ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete"
    )

    tags = db.relationship('TagModel', back_populates='store', lazy="dynamic")


    def __repr__(self):
        return f"{self.__class__.__name__}({self.id} - {self.name})"
