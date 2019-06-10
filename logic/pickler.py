import pickle as pkl
import logging


def save(data, path):
    try:
        with open(path, 'wb') as dest:
            pkl.dump(data, dest)
    except Exception as e:
        logging.warning('Error saving data')


def load(path):
    result = None
    try:
        with open(path, 'rb') as dest:
            result = pkl.load(dest)
    except Exception as e:
        logging.warning('Error loading data')
    finally:
        return result
