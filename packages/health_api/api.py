from flask import Flask, Blueprint, abort, jsonify
from flask_cors import CORS

from health_api.resources import all_resources, cached_resource


__all__ = [
    'HealthAPI'
]


class HealthAPI(Flask):

    def __init__(self):
        super(HealthAPI, self).__init__(__name__)
        # register blueprints
        self.register_blueprint(api)
        # apply CORS settings
        CORS(self)


api = Blueprint('api', __name__)


@api.route('/')
def _all():
    res = {}
    for resource in all_resources:
        res.update(cached_resource(resource))
    return jsonify(res)


@api.route('/<string:resource>')
def _partial(resource: str):
    try:
        return jsonify(cached_resource(resource))
    finally:
        abort(404)
