from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import ItemModel, StoreModel, TagModel
from app.schema.schemas import ItemAndTagSchema, TagSchema

blp = Blueprint("Tags", "tags", description="Operation on tags")


@blp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        """Return all tags of the store"""

        store = StoreModel.query.get_or_404(store_id)
        tags = store.tags.all()

        return tags

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        """Create tag for the store."""

        if TagModel.query.filter(
            TagModel.store_id == store_id, TagModel.name == tag_data["name"]
        ).first():
            abort(400, message="A Tag with that name already exists.")

        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()

        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        """Return specific tag with given id."""

        tag = TagModel.query.get_or_404(tag_id)

        return tag

    @blp.response(
        202,
        description="Deletes a tag if is tagged with it",
        example={"message": "Tag deleted."},
    )
    @blp.alt_response(404, description="Tag Not Found")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. in this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": " Tag deleted."}

        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any items, then try again.",
        )


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag in item.tags:
            abort(400, message="tag already exists for that item")

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.add(tag)
            db.session.commit()

        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return item

    @blp.response(200, ItemAndTagSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        store_tag = tag.store.id
        store_item = item.store.id

        if tag not in item.tags.all():
            abort(400, message="A tag not associate with that item")

        if store_item != store_tag:
            abort(400, message="A tag not associate with that item store")

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError as e:
            abort(500, message=str(e))
