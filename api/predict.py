import logging
import flask
from logic import preprocess
import const

predict_routes = flask.Blueprint('predict', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@predict_routes.route('/predict', methods=['POST'])
def predict():
    logger.info('Predict request started')

    file = preprocess.get_image_from_request()
    file_array = preprocess.image_to_ndarray(file)
    candidates = preprocess.load_photos()
    names, face_encodings = preprocess.flatten_candidates(candidates, const.rescale_factor)
    names, locations = preprocess.predict_result(file_array, names, face_encodings, const.rescale_factor)
    image = preprocess.render_name_frames(file, names, locations, const.rescale_factor)
    image_response = preprocess.prepare_flask_image_response(image)

    logger.info('Predict request finished')
    return image_response, 200
