import logging
import flask
from logic import preprocess
from flask import jsonify

predict_routes = flask.Blueprint('predict', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@predict_routes.route('/predict', methods=['POST'])
def predict():
    logger.info('Predict request started')

    file = preprocess.get_image_from_request()
    file_array = preprocess.image_to_ndarray(file)
    candidates = preprocess.load_photos()
    names, probas = preprocess.predict_result(file_array, candidates)
    top_result = preprocess.get_top_result(names, probas)

    logger.info('Predict request finished')
    return jsonify({'result': top_result, 'name': list(names), 'probas': list(probas)}), 200
