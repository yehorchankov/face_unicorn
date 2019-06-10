import face_recognition
from flask import request
import os
import config
import glob
from matplotlib import image
import io
import numpy as np
import cv2


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
    filename = get_filename(filename, 0, ext)
    # If the photo is first of a kind
    if not os.path.isfile(os.path.join(config.root_dir, config.save_dir, filename)):
        return 0
    else:
        filename_mask = filename + '_*_' + ext
        file_numbers = [int(x.split('_')[1]) for x in glob.glob(filename_mask)]
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
    unk_face_encoding = face_recognition.face_encodings(file_to_compare, [face_locations])

    for name, faces_list in candidates:
        for face in faces_list:
            small_frame = cv2.resize(face, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_frame)
            face_locations = face_locations[0]  # Take only one face from pic
            face_encoding = face_recognition.face_encodings(small_frame, [face_locations])
            names.append(name)
            face_encodings.append(face_encoding)

    # matches = face_recognition.compare_faces(face_encodings, unk_face_encoding)

    face_distances = face_recognition.face_distance(face_encodings, unk_face_encoding)
    face_distances = 1 / face_distances

    return names, face_distances


def get_top_result(names, probas):
    idx = np.argmax(np.array(probas))
    return names[idx] if type(idx) is int else names[idx[0]]