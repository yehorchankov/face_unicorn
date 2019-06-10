import configparser
import api

config = configparser.ConfigParser()
config.read('config.ini')


def get_config(env, key, default=None, type=None):
    if env not in config:
        raise KeyError(f'Key "{env}" not found in config.ini')

    if key not in config[env]:
        if default:
            return default

        if type == str:
            return ''
        elif type == bool:
            return False
        else:
            return None

    result = config[env][key]
    if type == bool:
        if result.lower() == 'true':
            return True
        elif result.lower() == 'false':
            return False
        elif default:
            return default
        else:
            return None

    if type:
        return type(result)
    else:
        return result


def register_blueprints(app):
    for blueprint in api.routes:
        app.register_blueprint(blueprint)
