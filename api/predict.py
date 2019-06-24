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
    file_array, extension = preprocess.image_to_ndarray(file)
    pil_image = preprocess.to_pil(file_array)
    rescale_factor = preprocess.get_rescale_factor(pil_image)
    pil_image = preprocess.rescale_image(pil_image, rescale_factor)
    candidates = preprocess.load_photos()
    names, face_encodings = preprocess.flatten_candidates(candidates, const.rescale_factor)
    names, locations = preprocess.predict_result(pil_image, names, face_encodings)
    image = preprocess.render_name_frames(pil_image, names, locations)
    logger.info('Predict request finished')
    return preprocess.return_flask_image_response(image)
