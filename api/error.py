import flask
import logging

error_routes = flask.Blueprint('error', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@error_routes.app_errorhandler(Exception)
def handle_invalid_usage(error):
    sys_msg = f'An unhandled error of type {type(error)} occurred. Error message: {str(error)}. ' \
              f'From url: {flask.request.url}'
    logger.exception(sys_msg)
    return flask.jsonify(sys_msg), 500
