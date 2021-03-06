from flask import Flask, Blueprint, abort, jsonify
from flask_cors import CORS

from health_api.resources import all_resources, cached_resource


__all__ = [
    'HealthAPI'
]

__battery__ = None


class HealthAPI(Flask):

    def __init__(self, app):
        global __battery__
        super(HealthAPI, self).__init__(__name__)
        # keep a link to the Battery object
        __battery__ = app.battery
        # register blueprints
        self.register_blueprint(api)
        # apply CORS settings
        CORS(self)


api = Blueprint('api', __name__)


@api.route('/')
def _all():
    res = {}
    for resource in all_resources:
        value = cached_resource(resource)
        res.update(value)
    return jsonify(res)


@api.route('/battery/history')
def _battery_history():
    return jsonify({'history': __battery__.history() if __battery__ else []})


@api.route('/<string:resource>')
def _partial(resource: str):
    try:
        return jsonify(cached_resource(resource))
    except KeyError:
        abort(404)
    except BaseException as e:
        return str(e)
