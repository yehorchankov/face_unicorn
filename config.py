import os
from logic import utils


host = utils.get_config('PROD', 'HOST')
port = utils.get_config('PROD', 'PORT')
save_dir = utils.get_config('PROD', 'SAVEDIR')
root_dir = os.path.dirname(os.path.realpath(__file__))
