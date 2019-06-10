import flask
import logging
from logic import preprocess

save_routes = flask.Blueprint('save', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@save_routes.route('/save', methods=['POST'])
def save_result():
    logger.info('Save request started')
    preprocess.save_photo()
    logger.info('Save request finished')
    return 'ok', 200

