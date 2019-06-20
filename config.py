import os
from logic import utils


host = utils.get_config('PROD', 'HOST')
port = utils.get_config('PROD', 'PORT')
save_dir = utils.get_config('PROD', 'SAVEDIR')
root_dir = os.path.dirname(os.path.realpath(__file__))
redis_host = utils.get_config('REDIS', 'HOST')
redis_port = utils.get_config('REDIS', 'PORT')
redis_db = utils.get_config('REDIS', 'DB')
