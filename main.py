import flask
import logging
from config import utils
import config
import os

app = flask.Flask(__name__)
utils.register_blueprints(app)
logging.basicConfig(filename='log.log')


if __name__ == '__main__':
    logging.info('Running application through python..')
    save_dir_full = os.path.join(config.root_dir, config.save_dir)
    if not os.path.exists(save_dir_full):
        os.makedirs(save_dir_full)
        logging.info(f'Creating dir {save_dir_full}')

    app.run(host=config.host, port=config.port, debug=True)
