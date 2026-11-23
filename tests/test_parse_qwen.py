import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infer import parse_qwen


def test_plain_json():
    assert parse_qwen('[{"bbox_2d": [10, 20, 30, 40], "label": "butterfly"}]') == [([10, 20, 30, 40], 'butterfly')]


def test_fenced_json():
    text = '```json\n[{"bbox_2d": [1, 2, 3, 4], "label": "butterfly"}]\n```'
    assert parse_qwen(text) == [([1, 2, 3, 4], 'butterfly')]


def test_empty_list():
    assert parse_qwen('```json\n[]\n```') == []


def test_truncated_json_keeps_full_objects():
    text = '[{"bbox_2d": [1, 2, 3, 4], "label": "moth"}, {"bbox_2d": [5, 6, 7'
    assert parse_qwen(text) == [([1, 2, 3, 4], 'moth')]


def test_truncated_without_label():
    text = '[{"bbox_2d": [1, 2, 3, 4]}, {"bbox_2d": [5, 6, 7'
    assert parse_qwen(text) == [([1, 2, 3, 4], None)]


def test_single_object():
    assert parse_qwen('{"bbox_2d": [1, 2, 3, 4], "label": "other insect"}') == [([1, 2, 3, 4], 'other insect')]


def test_garbage_is_error():
    with pytest.raises(ValueError):
        parse_qwen('There is a butterfly on the flower.')
