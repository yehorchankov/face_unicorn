import logging
import flask
import os
import config

photos_routes = flask.Blueprint('photos', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@photos_routes.route('/photos', methods=['DELETE'])
def delete_photos():
    save_dir = os.path.join(config.root_dir, config.save_dir)
    removed = []
    for filename in os.listdir(save_dir):
        os.unlink(os.path.join(save_dir, filename))
        removed.append(filename)
    return flask.jsonify({'removed': removed}), 200
