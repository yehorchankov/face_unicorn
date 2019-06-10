import logging
import flask
from logic import preprocess

predict_routes = flask.Blueprint('predict', __name__, url_prefix='/api')


@predict_routes.route('/predict', methods=['POST'])
def predict():
    logging.info('Predict request started')

    file = preprocess.get_image_from_request()
    file_array = preprocess.image_to_ndarray(file)
    candidates = preprocess.load_photos()
    names, probas = preprocess.predict_result(file_array, candidates)
    top_result = preprocess.get_top_result(names, probas)

    logging.info('Predict request finished')
    return {'result': top_result, 'name': names, 'probas': probas}
