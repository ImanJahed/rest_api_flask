from app.extensions import db


class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(0), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)

    store = db.relationship('StoreModel', back_populates='items')
    tags = db.relationship('TagModel', back_populates='items', secondary='items_tags')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} - {self.name})'
