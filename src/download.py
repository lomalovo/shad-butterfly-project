import argparse
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
from PIL import Image, ImageOps


def fetch(row, out_dir):
    path = os.path.join(out_dir, f'{row.photo_id}.jpg')
    if not os.path.exists(path):
        for attempt in range(3):
            try:
                r = requests.get(row.original_url, timeout=60)
                r.raise_for_status()
                with open(path, 'wb') as f:
                    f.write(r.content)
                break
            except Exception as e:
                print(row.photo_id, 'attempt', attempt, e)
    if not os.path.exists(path):
        return row.photo_id, 'missing', None, None, None
    data = open(path, 'rb').read()
    sha = hashlib.sha256(data).hexdigest()
    img = Image.open(path)
    orientation = img.getexif().get(274, 1)
    w, h = ImageOps.exif_transpose(img).size
    sha_ok = sha == row.sha256 if hasattr(row, 'sha256') else 'no column'
    size_ok = (w, h) == (row.width, row.height) if hasattr(row, 'width') else 'no column'
    return row.photo_id, sha_ok, size_ok, orientation, img.size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default='data/preliminary_annotations.csv')
    parser.add_argument('--jsonl', default=None)
    parser.add_argument('--out', default='data/images')
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if args.jsonl:
        df = pd.read_json(args.jsonl, lines=True).rename(columns={'photo_url': 'original_url'})
    else:
        df = pd.read_csv(args.csv, encoding='utf-8-sig')
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda r: fetch(r, args.out), df.itertuples()))
    res = pd.DataFrame(results, columns=['photo_id', 'sha_ok', 'size_ok', 'orientation', 'raw_size'])
    print('files:', len(res))
    print('sha mismatch:', res[res.sha_ok == False].photo_id.tolist())
    print('size mismatch:', res[res.size_ok == False][['photo_id', 'raw_size']].values.tolist())
    print('missing:', res[res.sha_ok == 'missing'].photo_id.tolist())
    print('exif orientation != 1:', res[res.orientation != 1][['photo_id', 'orientation']].values.tolist())


if __name__ == '__main__':
    main()
