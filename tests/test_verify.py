import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PIL import Image

from postprocess import process
from verify import crop


def test_crop_adds_padding():
    img = Image.new('RGB', (1000, 500))
    b = {'left': 0.2, 'top': 0.2, 'width': 0.1, 'height': 0.2}
    assert crop(img, b, 0.1).size == (120, 120)


def test_crop_stays_inside_image():
    img = Image.new('RGB', (1000, 500))
    b = {'left': 0.0, 'top': 0.9, 'width': 0.5, 'height': 0.1}
    assert crop(img, b, 0.1).size == (550, 55)


def test_low_verify_score_is_dropped():
    boxes = [{'left': 0.1, 'top': 0.1, 'width': 0.2, 'height': 0.2, 'score': 0.01, 'label': 'butterfly'},
             {'left': 0.5, 'top': 0.1, 'width': 0.2, 'height': 0.2, 'score': 0.9, 'label': 'moth'}]
    out = process({'photo_id': 1, 'error': None, 'boxes': boxes}, 0.02, 0.3, ['butterfly', 'moth'])
    assert len(out['boxes']) == 1 and out['boxes'][0]['left'] == 0.5
