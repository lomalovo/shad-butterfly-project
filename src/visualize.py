import argparse
import os

from PIL import ImageDraw

from common import list_images, load_image, parse_id, read_jsonl

COLORS = ['red', 'deepskyblue', 'orange', 'magenta']


def draw(img, boxes, color, width):
    d = ImageDraw.Draw(img)
    w, h = img.size
    for b in boxes:
        x1, y1 = b['left'] * w, b['top'] * h
        x2, y2 = x1 + b['width'] * w, y1 + b['height'] * h
        d.rectangle([x1, y1, x2, y2], outline=color, width=width)
        if b.get('score') is not None:
            d.text((x1 + 4, y1 + 2), f'{b["score"]:.2f}', fill=color)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', required=True)
    parser.add_argument('--preds', nargs='+', required=True)
    parser.add_argument('--golden', default=None)
    parser.add_argument('--ids', nargs='*', default=None)
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    paths = dict(list_images(args.images))
    runs = [{r['photo_id']: r for r in read_jsonl(p)} for p in args.preds]
    golden = {r['photo_id']: r['boxes'] for r in read_jsonl(args.golden)} if args.golden else {}
    ids = [parse_id(x) for x in args.ids] if args.ids else list(paths)[:args.limit]
    for pid in ids:
        img = load_image(paths[pid])
        img.thumbnail((1024, 1024))
        if pid in golden:
            draw(img, golden[pid], 'lime', 5)
        for run, color in zip(runs, COLORS):
            row = run.get(pid)
            if row and row['boxes']:
                draw(img, row['boxes'], color, 2)
        img.save(os.path.join(args.out, f'{pid}.jpg'), quality=85)
    print('saved', len(ids), 'images to', args.out)


if __name__ == '__main__':
    main()
