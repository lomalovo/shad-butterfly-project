import json
import os

import numpy as np
from PIL import Image, ImageOps


def load_image(path):
    return ImageOps.exif_transpose(Image.open(path)).convert('RGB')


def parse_id(stem):
    return int(stem) if stem.isdigit() else stem


def list_images(images_dir):
    items = []
    for name in sorted(os.listdir(images_dir)):
        stem, ext = os.path.splitext(name)
        if ext.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
            items.append((parse_id(stem), os.path.join(images_dir, name)))
    return items


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def append_jsonl(path, row):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


def to_xyxy(boxes):
    arr = np.array([[b['left'], b['top'], b['left'] + b['width'], b['top'] + b['height']] for b in boxes], dtype=float)
    return arr.reshape(-1, 4)


def iou_matrix(a, b):
    a, b = to_xyxy(a), to_xyxy(b)
    x1 = np.maximum(a[:, None, 0], b[None, :, 0])
    y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    x2 = np.minimum(a[:, None, 2], b[None, :, 2])
    y2 = np.minimum(a[:, None, 3], b[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    area_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
    area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    union = area_a[:, None] + area_b[None, :] - inter
    return np.where(union > 0, inter / np.maximum(union, 1e-12), 0.0)


def clip_box(box):
    x1 = min(max(box['left'], 0.0), 1.0)
    y1 = min(max(box['top'], 0.0), 1.0)
    x2 = min(max(box['left'] + box['width'], 0.0), 1.0)
    y2 = min(max(box['top'] + box['height'], 0.0), 1.0)
    if x2 <= x1 or y2 <= y1:
        return None
    return dict(box, left=x1, top=y1, width=x2 - x1, height=y2 - y1)


def norm_box(x1, y1, x2, y2, w, h, score=None, label=None):
    box = {'left': x1 / w, 'top': y1 / h, 'width': (x2 - x1) / w, 'height': (y2 - y1) / h, 'score': score, 'label': label}
    return clip_box(box)
