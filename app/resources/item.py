from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import ItemModel
from app.models.stores import StoreModel
from app.schema.schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("items", __name__, description="Operation on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    """Dispatches request for specific item."""

    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Return specific item."""

        item = ItemModel.query.get_or_404(item_id)

        return item

    @jwt_required()
    def delete(self, item_id):
        """Delete specific item."""

        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        item = ItemModel.query.get_or_404(item_id)

        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemUpdateSchema)
    def put(self, item_data, item_id):
        """Update specific item."""

        item = ItemModel.query.get(item_id)

        if item:
            for field, value in item_data.items():
                setattr(item, field, value)

        else:
            store_id = item_data.get("store_id")
            store = StoreModel.query.get(store_id)
            store_data = item_data.pop("store")

            if store:
                item = ItemModel(**item_data)

            else:
                store = StoreModel(id=store_id, name=store_data["name"])
                db.session.add(store)

                item = ItemModel(**item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    """Dispatches request for return all items and create item."""

    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """Return All Items."""

        items = ItemModel.query.all()

        return items

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        """Create item."""

        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="Error occurred when create item")

        return item
