import flask
import logging

error_routes = flask.Blueprint('save', __name__, url_prefix='/api')


@error_routes.app_errorhandler(Exception)
def handle_invalid_usage(error):
    sys_msg = f'An unhandled error of type {type(error)} occurred. Error message: {str(error)}. ' \
              f'From url: {flask.request.url}'
    logging.exception(sys_msg)
    return flask.jsonify(sys_msg), 500
