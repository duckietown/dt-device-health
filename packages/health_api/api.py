import uuid
import logging
from typing import Union

from flask import Flask, Blueprint, abort, jsonify, request
from flask_cors import CORS

from battery_drivers import Battery
from dt_triggers_utils import set_trigger
from health_api.constants import DEBUG
from health_api.knowledge_base import KnowledgeBase
from health_api.resources import all_resources, cached_resource


__all__ = [
    'HealthAPI'
]

__battery__: Union[None, Battery] = None


class HealthAPI(Flask):

    def __init__(self, app):
        global __battery__
        super(HealthAPI, self).__init__(__name__)
        # keep a link to the Battery object
        __battery__ = app.battery
        # create token for privileged operations
        KnowledgeBase.set('trigger/shutdown', str(uuid.uuid4()), ttl=-1)
        KnowledgeBase.set('trigger/reboot', str(uuid.uuid4()), ttl=-1)
        # register blueprints
        self.register_blueprint(api)
        # apply CORS settings
        CORS(self)
        # configure logging
        logging.getLogger('werkzeug').setLevel(logging.DEBUG if DEBUG else logging.WARNING)


api = Blueprint('api', __name__)


@api.route('/')
def _all():
    res = {}
    for resource in all_resources:
        value = cached_resource(resource)
        res.update(value)
    return jsonify(res)


@api.route('/trigger/<string:trigger>')
def _trigger(trigger: str):
    if not KnowledgeBase.has(f'trigger/{trigger}'):
        return jsonify({'status': 'error', 'message': f"Trigger '{trigger}' not supported"})
    # check token or provide one if wrong/none was given
    right_token = KnowledgeBase.get(f'trigger/{trigger}')
    given_token = request.args.get('token', default=None)
    if given_token != right_token:
        return jsonify({'status': 'needs-confirmation', 'token': right_token})
    # set trigger
    try:
        set_trigger(trigger, 'health-api')
    except FileNotFoundError as e:
        return jsonify({'status': 'error', 'message': str(e)})
    # special case: trigger == shutdown
    if trigger == 'shutdown':
        # shutdown the battery as well
        timeout = request.args.get('timeout', default=20)
        __battery__.turn_off(timeout)
    # ---
    return jsonify({'status': 'ok'})


@api.route('/battery/history')
def _battery_history():
    return jsonify({'history': __battery__.history() if __battery__ else []})


@api.route('/battery/info')
def _battery_info():
    info = __battery__.info or {"FirmwareVersion": "ND", "BootData": "ND", "SerialNumber": "ND"}
    return jsonify(info)


@api.route('/<string:resource>')
def _partial(resource: str):
    try:
        return jsonify(cached_resource(resource))
    except KeyError:
        abort(404)
    except BaseException as e:
        return str(e)
