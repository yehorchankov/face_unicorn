import flask
import logging
from logic import preprocess

save_routes = flask.Blueprint('save', __name__, url_prefix='/api')


@save_routes.route('/save', methods=['POST'])
def save_result():
    logging.info('Save request started')
    preprocess.save_photo()
    logging.info('Save request finished')
    return 'ok', 200

