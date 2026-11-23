import argparse
import json
import os

import pandas as pd

from common import parse_id, read_jsonl
from metrics import per_image, summarize

GROUP_COLUMNS = ['provisional_group', 'small_object', 'occluded', 'edge_cut', 'complex_background', 'blur',
                 'poor_light', 'close_objects', 'wings', 'view', 'background']


def load_golden(path):
    golden = {}
    for row in read_jsonl(path):
        pid = parse_id(str(row['photo_id']))
        if row.get('error') is not None or row.get('boxes') is None:
            raise ValueError(f'golden row without boxes: {row}')
        golden[pid] = row['boxes']
    return golden


def load_preds(path):
    return {parse_id(str(r['photo_id'])): r for r in read_jsonl(path)}


def run_name(pred_path):
    return os.path.splitext(os.path.basename(pred_path))[0]


def timing(raw_dir, name):
    meta_path = os.path.join(raw_dir, name.split('__')[0] + '.meta.json')
    if not os.path.exists(meta_path):
        return {}
    meta = json.load(open(meta_path))
    return {'total_time_s': meta['total_time_s'], 'mean_time_s': round(meta['total_time_s'] / meta['images'], 3),
            'hardware': f'{meta["cpu"]}, {meta["device"]}, {meta["dtype"]}'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--golden', required=True)
    parser.add_argument('--preds', nargs='+', required=True)
    parser.add_argument('--meta', default='data/preliminary_annotations.csv')
    parser.add_argument('--raw-dir', default='outputs/raw')
    parser.add_argument('--out', default='outputs/eval')
    args = parser.parse_args()

    golden = load_golden(args.golden)
    meta = pd.read_csv(args.meta, encoding='utf-8-sig').set_index('photo_id')
    os.makedirs(args.out, exist_ok=True)

    board, groups, images = [], [], []
    for path in args.preds:
        name = run_name(path)
        rows = per_image(golden, load_preds(path))
        df = pd.DataFrame(rows)
        df.insert(0, 'run', name)
        images.append(df)
        board.append({'run': name, **summarize(rows), **timing(args.raw_dir, name)})
        df = df.join(meta[GROUP_COLUMNS], on='photo_id')
        for col in GROUP_COLUMNS:
            for value, part in df.groupby(col, dropna=False):
                groups.append({'run': name, 'column': col, 'value': value,
                               **summarize(part.to_dict('records'))})

    board = pd.DataFrame(board).sort_values('f1_50', ascending=False)
    board.to_csv(os.path.join(args.out, 'leaderboard.csv'), index=False)
    cols = ['run', 'f1_50', 'precision_50', 'recall_50', 'f1_75', 'tp_50', 'fp_50', 'fn_50',
            'neg_fp_boxes', 'neg_fp_images', 'neg_images', 'errors', 'total_time_s', 'mean_time_s']
    cols = [c for c in cols if c in board.columns]
    with open(os.path.join(args.out, 'leaderboard.md'), 'w') as f:
        f.write(board[cols].to_markdown(index=False, floatfmt='.3f'))
        if 'hardware' in board.columns:
            f.write('\n\nhardware: ' + '; '.join(sorted(set(board['hardware'].dropna()))) + '\n')
    pd.DataFrame(groups).to_csv(os.path.join(args.out, 'groups.csv'), index=False)
    pd.concat(images).to_csv(os.path.join(args.out, 'per_image.csv'), index=False)
    print(board[cols].to_string(index=False))


if __name__ == '__main__':
    main()
