from flask import Flask, jsonify

from app.blocklist import BLOCKLIST
from app.extensions import api, db, jwt
from app.resources.item import blp as item_blp
from app.resources.store import blp as store_blp
from app.resources.tag import blp as tag_blp
from app.resources.user import blp as user_blp


def blueprint_register(api):
    """Register blueprint"""
    api.register_blueprint(store_blp)
    api.register_blueprint(item_blp)
    api.register_blueprint(tag_blp)
    api.register_blueprint(user_blp)


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    api.init_app(app)
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired."}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(
            {"message": "Signature verification failed", "error": "invalid_token."}
        ), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "Authorization required.",
            }
        ), 401

    @jwt.additional_claims_loader
    def add_claim_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    # for logout operation we check jwt in blocklist or not
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked."}
        ), 401

    # -------------------------------------

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify(
            {"description": "The token is not fresh", "error": "fresh_token_required."}
        ), 401

    with app.app_context():
        db.create_all()

    blueprint_register(api)

    return app
