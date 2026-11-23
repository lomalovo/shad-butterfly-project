import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from postprocess import process


def box(left, score, label):
    return {'left': left, 'top': 0.1, 'width': 0.2, 'height': 0.2, 'score': score, 'label': label}


def test_keep_labels_drops_other_labels():
    row = {'photo_id': 1, 'error': None, 'boxes': [box(0.1, 0.9, 'butterfly'), box(0.5, 0.8, 'caterpillar')]}
    out = process(row, 0.2, None, ['butterfly'])
    assert out['boxes'] == [{'left': 0.1, 'top': 0.1, 'width': 0.2, 'height': 0.2}]


def test_dropped_label_does_not_suppress_butterfly_in_nms():
    row = {'photo_id': 1, 'error': None, 'boxes': [box(0.1, 0.9, 'caterpillar'), box(0.11, 0.5, 'butterfly')]}
    out = process(row, 0.2, 0.3, ['butterfly'])
    assert len(out['boxes']) == 1 and out['boxes'][0]['left'] == 0.11


def test_error_row_stays_error():
    row = {'photo_id': 1, 'error': 'boom', 'boxes': None}
    assert process(row, 0.2, 0.3, ['butterfly']) == {'photo_id': 1, 'boxes': None, 'error': 'boom'}


def test_keep_labels_ignores_case():
    row = {'photo_id': 1, 'error': None, 'boxes': [box(0.1, None, 'Butterfly'), box(0.5, None, 'other insect')]}
    assert len(process(row, 0.0, None, ['butterfly', 'moth'])['boxes']) == 1
