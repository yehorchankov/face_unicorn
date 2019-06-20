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
import const
import matplotlib.pyplot as plt
from io import BytesIO
import flask
from matplotlib.backends.backend_agg import FigureCanvasAgg

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
        file_numbers = [int(os.path.basename(x).split('_')[1]) for x in glob.glob(os.path.join(save_dir, filename_mask))]
        return max(file_numbers) + 1


def image_to_ndarray(file):
    extension = file.filename.split('.')[1]
    return image.imread(io.BytesIO(file.read()), extension)


def predict_result(file_to_compare, names, face_encodings, rescale_factor):
    results = []
    locations = []

    file_to_compare = cv2.resize(file_to_compare, (0, 0), fx=rescale_factor, fy=rescale_factor)
    unk_face_locations = face_recognition.face_locations(file_to_compare)
    unk_face_encodings = face_recognition.face_encodings(file_to_compare, unk_face_locations)

    for unk_face_encoding, unk_face_location in zip(unk_face_encodings, unk_face_locations):
        face_distances = face_recognition.face_distance(face_encodings, unk_face_encoding)
        top_result = get_top_result(names, face_distances)
        results.append(top_result)
        locations.append(unk_face_location)
        logger.info(f'Face predicted: {top_result}')

    return results, locations


def flatten_candidates(candidates, rescale_factor):
    names = []
    face_encodings = []
    for name, faces_list in candidates.items():
        for face in faces_list:
            small_frame = cv2.resize(face, (0, 0), fx=rescale_factor, fy=rescale_factor)
            face_locations = face_recognition.face_locations(small_frame)
            face_encoding = face_recognition.face_encodings(small_frame, face_locations)
            names.append(name)
            face_encodings.append(face_encoding[0])
            logger.info(f'predict_result - face encoding for {name}\n{face_encoding[0]}')
    return names, face_encodings


def get_top_result(names, probas, threshold=0.6):
    logger.info(f'get_top_result\n{names}\n{probas}')
    idx = np.argmin(np.array(probas))
    logger.info(f'get_top_result\n{idx}')
    if probas[idx] > threshold:
        return const.unknown_face
    return names[idx]


def render_name_frames(image, names, locations, rescale_factor):
    for (top, right, bottom, left), name in zip(locations, names):
        # Scale back up face locations since the frame we detected in was scaled to rescale_factor size
        top /= rescale_factor
        right /= rescale_factor
        bottom /= rescale_factor
        left /= rescale_factor

        # Draw a box around the face
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        logging.info(f'Image {image}')
    return image


def prepare_flask_image_response(plt_figure, mimetype='image/png'):
    canvas = FigureCanvasAgg(plt_figure)
    output = BytesIO()
    canvas.print_png(output)
    response = flask.make_response(output.getvalue())
    response.mimetype = mimetype
    return response


def array2image(img_array):
    plt.ioff()
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    ax.imshow(img_array)
    fig.add_axes(ax)
    return fig
