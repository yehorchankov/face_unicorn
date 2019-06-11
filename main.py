import os
import flask
from flask_cors import CORS
import logging
import config
from config import utils

app = flask.Flask(__name__)
CORS(app)
utils.register_blueprints(app)
logging.basicConfig(filename='log.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logger.info('Running application through python..')
    save_dir_full = os.path.join(config.root_dir, config.save_dir)
    if not os.path.exists(save_dir_full):
        os.makedirs(save_dir_full)
        logger.info(f'Creating dir {save_dir_full}')

    app.run(host=config.host, port=config.port, debug=True)
