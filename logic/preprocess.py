import face_recognition
from flask import request
import os
import config
import glob
from matplotlib.image import imread
import io
import numpy as np
import cv2
import logging
import const
from PIL import ImageFont, ImageDraw, Image
from base64 import b64encode


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
    return f'{name}_{number}_{ext}'


def get_next_photo_number(filename, ext='.png'):
    filename_zero = get_filename(filename, 0, ext)
    save_dir = os.path.join(config.root_dir, config.save_dir)
    # If the photo is first of a kind
    if not os.path.isfile(os.path.join(save_dir, filename_zero)):
        return 0
    else:
        filename_mask = f'{filename}_*_{ext}'
        file_numbers = [int(os.path.basename(x).split('_')[1]) for x in glob.glob(os.path.join(save_dir, filename_mask))]
        return max(file_numbers) + 1


def image_to_ndarray(file):
    extension = file.filename.split('.')[1]
    return imread(io.BytesIO(file.read()), extension), extension


def to_pil(img_array):
    return Image.fromarray(img_array)


def to_np(img_pil):
    logger.info(f'Converting to np {img_pil.size}')
    return np.array(img_pil)


def predict_result(file_to_compare, names, face_encodings):
    results = []
    locations = []

    file_to_compare_np = to_np(file_to_compare)
    unk_face_locations = face_recognition.face_locations(file_to_compare_np)
    unk_face_encodings = face_recognition.face_encodings(file_to_compare_np, unk_face_locations)

    logger.info(f'Predicting {len(unk_face_encodings)} faces')

    for unk_face_encoding, unk_face_location in zip(unk_face_encodings, unk_face_locations):
        face_distances = face_recognition.face_distance(face_encodings, unk_face_encoding)
        top_result = get_top_result(names, face_distances)
        results.append(top_result)
        locations.append(unk_face_location)
        logger.info(f'Face predicted: {top_result}')

    return results, locations


def flatten_candidates(candidates, rescale_factor):
    names = []
    result_encodings = []
    for name, faces_list in candidates.items():
        for face in faces_list:
            small_frame = cv2.resize(face, (0, 0), fx=rescale_factor, fy=rescale_factor)
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)
            if len(face_encodings) > 0:
                names.append(name)
                result_encodings.append(face_encodings[0])
                logger.info(f'name: {name} | face len: {len(face)} - flattened')
    return names, result_encodings


def get_top_result(names, probas, threshold=0.6):
    logger.info(f'get_top_result\n{names}\n{probas}')
    idx = np.argmin(np.array(probas))
    logger.info(f'get_top_result\n{idx}')
    if probas[idx] > threshold:
        return const.unknown_face
    return names[idx]


def render_name_frames(img_pil, names, locations):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(const.font, 30)

    logger.info(f'Rendering frames for {len(locations)} faces')

    for (top, right, bottom, left), name in zip(locations, names):
        # Scale back up face locations since the frame we detected in was scaled to rescale_factor size
        top = int(top)
        right = int(right)
        bottom = int(bottom)
        left = int(left)
        # Draw a box around the face
        draw.rectangle([left, top, right, bottom], fill=None, outline=(0, 0, 255), width=5)
        draw.rectangle([left, bottom - 34, right, bottom], fill=(0, 0, 255), outline=(0, 0, 255))
        # Draw a label with a name below the face
        draw.text((left + 6, bottom - 40), name, font=font, fill=(255, 255, 255, 255))
    del draw

    return img_pil


def get_rescale_factor(pil_img):
    factor = 1
    min_size = min(pil_img.size[0], pil_img.size[1])
    max_size = max(pil_img.size[0], pil_img.size[1])
    if min_size < 1000:
        factor = 1000 / min_size
    elif max_size > 2000:
        factor = 2000 / max_size
    return factor


def rescale_image(pil_img, factor):
    rescaled_w = pil_img.size[0] * factor
    rescaled_h = pil_img.size[1] / pil_img.size[0] * rescaled_w
    logger.info(f'Rescaling image with size of {pil_img.size} to {rescaled_w} x {rescaled_h}')
    return pil_img.resize((int(rescaled_w), int(rescaled_h)), Image.ANTIALIAS)


def return_flask_image_response(pil_img):
    img_io = io.BytesIO()
    pil_img.save(img_io, 'PNG')
    data = b64encode(img_io.getvalue()).decode('ascii')
    return data
