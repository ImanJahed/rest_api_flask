from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import StoreModel
from app.schema.schemas import StoreSchema, StoreUpdateSchema

blp = Blueprint("stores", __name__, description="Operation on store")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    """Dispatches request to specific store."""

    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        """Return a specific store."""

        store = StoreModel.query.get_or_404(store_id)

        return store

    @jwt_required()
    def delete(self, store_id):
        """Delete specific store."""
        store = StoreModel.query.get_or_404(store_id)

        db.session.delete(store)
        db.session.commit()

        return {"message": "Store deleted."}, 204

    @jwt_required()
    @blp.arguments(StoreUpdateSchema)
    @blp.response(200, StoreUpdateSchema)
    def put(self, store_data, store_id):
        """Update specific store if exists otherwise created."""

        store = StoreModel.query.get(store_id)

        if store:
            for field, value in store_data.items():
                if hasattr(store, field):
                    setattr(store, field, value)

        else:
            store = StoreModel(**store_data)

        db.session.add(store)
        db.session.commit()

        return store


@blp.route("/store")
class StoreList(MethodView):
    """Dispatches request for return all store and create store."""

    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        """Return All Store."""
        stores = StoreModel.query.all()

        return stores

    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        """Create a store."""

        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()

        except IntegrityError:
            abort(400, message="Store already exists")

        except SQLAlchemyError:
            abort(500, message="Error occurred when create store")

        return store
