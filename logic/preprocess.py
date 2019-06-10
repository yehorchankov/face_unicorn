import face_recognition
from flask import request
import os
import config
import glob
from matplotlib import image
import io
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)


def get_image_from_request():
    return request.files['image']


def save_photo():
    file = get_image_from_request()
    filename = request.form['name']
    extension = '.' + file.filename.split('.')[1]
    file_number = get_next_photo_number(filename, extension)
    filename = get_filename(filename, file_number, extension)
    file.save(os.path.join(config.root_dir, config.save_dir, filename))


def load_photos():
    save_dir = os.path.join(config.root_dir, config.save_dir)
    result = {}
    files = os.listdir(save_dir)
    for filename in files:
        name = filename.split('_')[0]
        result[name] = list()
    for filename in files:
        name = filename.split('_')[0]
        result[name].append(face_recognition.load_image_file(os.path.join(save_dir, filename)))
    return result


def get_filename(name, number, ext):
    return name + '_' + str(number) + '_' + ext


def get_next_photo_number(filename, ext='.png'):
    filename_zero = get_filename(filename, 0, ext)
    save_dir = os.path.join(config.root_dir, config.save_dir)
    # If the photo is first of a kind
    if not os.path.isfile(os.path.join(save_dir, filename_zero)):
        return 0
    else:
        filename_mask = filename + '_*_' + ext
        file_numbers = [int(x.split('_')[1]) for x in glob.glob(os.path.join(save_dir, filename_mask))]
        return max(file_numbers) + 1


def image_to_ndarray(file):
    extension = file.filename.split('.')[1]
    return image.imread(io.BytesIO(file.read()), extension)


def predict_result(file_to_compare, candidates):
    names = []
    face_encodings = []

    file_to_compare = cv2.resize(file_to_compare, (0, 0), fx=0.25, fy=0.25)
    face_locations = face_recognition.face_locations(file_to_compare)
    face_locations = face_locations[0]  # Take only one face from pic
    unk_face_encoding = face_recognition.face_encodings(file_to_compare, [face_locations])[0]

    for name, faces_list in candidates.items():
        for face in faces_list:
            small_frame = cv2.resize(face, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_frame)
            face_locations = face_locations[0]  # Take only one face from pic
            face_encoding = face_recognition.face_encodings(small_frame, [face_locations])[0]
            names.append(name)
            face_encodings.append(face_encoding)
            logger.info(f'predict_result - face encoding for {name}\n{face_encoding}')
    # matches = face_recognition.compare_faces(face_encodings, unk_face_encoding)

    face_distances = face_recognition.face_distance(np.array(face_encodings), unk_face_encoding)
    logger.info(f'predict_result - inverse predict_result\n{face_distances}')
    return names, face_distances


def get_top_result(names, probas, threshold=0.4):
    logger.info(f'get_top_result\n{names}\n{probas}')
    idx = np.argmin(np.array(probas))
    logger.info(f'get_top_result\n{idx}')

    if probas[idx] > threshold:
        return 'No such face in database'

    return names[idx[0]] if type(idx) is np.array else names[idx]
