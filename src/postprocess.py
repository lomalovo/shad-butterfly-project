import argparse

import numpy as np
import yaml

from common import clip_box, iou_matrix, read_jsonl, write_jsonl


def nms(boxes, iou_thr):
    order = sorted(range(len(boxes)), key=lambda i: -(boxes[i]['score'] or 0))
    boxes = [boxes[i] for i in order]
    if not boxes:
        return boxes
    iou = iou_matrix(boxes, boxes)
    keep = []
    removed = np.zeros(len(boxes), dtype=bool)
    for i in range(len(boxes)):
        if removed[i]:
            continue
        keep.append(boxes[i])
        removed |= iou[i] > iou_thr
    return keep


def process(row, threshold, nms_iou, keep_labels=None):
    if row['error'] is not None:
        return {'photo_id': row['photo_id'], 'boxes': None, 'error': row['error']}
    boxes = [b for b in row['boxes'] if b['score'] is None or b['score'] >= threshold]
    if keep_labels:
        boxes = [b for b in boxes if str(b['label']).lower().strip() in keep_labels]
    boxes = [b for b in map(clip_box, boxes) if b]
    if nms_iou is not None:
        boxes = nms(boxes, nms_iou)
    out = [{k: round(b[k], 6) for k in ('left', 'top', 'width', 'height')} for b in boxes]
    return {'photo_id': row['photo_id'], 'boxes': out, 'error': None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--config', default=None)
    parser.add_argument('--threshold', type=float, default=None)
    parser.add_argument('--nms', default=None)
    args = parser.parse_args()

    cfg = yaml.safe_load(open(args.config)) if args.config else {}
    threshold = args.threshold if args.threshold is not None else cfg.get('threshold', 0.0)
    nms_value = args.nms if args.nms is not None else cfg.get('nms', 'off')
    nms_iou = None if str(nms_value) == 'off' else float(nms_value)

    rows = [process(r, threshold, nms_iou, cfg.get('keep_labels')) for r in read_jsonl(args.raw)]
    write_jsonl(args.out, rows)
    n_boxes = sum(len(r['boxes']) for r in rows if r['boxes'] is not None)
    n_err = sum(r['error'] is not None for r in rows)
    print(f'{args.out}: threshold={threshold} nms={nms_value} images={len(rows)} boxes={n_boxes} errors={n_err}')


if __name__ == '__main__':
    main()
