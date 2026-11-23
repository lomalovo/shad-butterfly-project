import argparse
import json
import math
import os
import sys

import pandas as pd

from common import list_images, parse_id


def expected_ids(path):
    if os.path.isdir(path):
        return [pid for pid, _ in list_images(path)]
    if path.endswith('.jsonl'):
        return [json.loads(line)['photo_id'] for line in open(path, encoding='utf-8') if line.strip()]
    if path.endswith('.csv'):
        return [parse_id(str(x)) for x in pd.read_csv(path, encoding='utf-8-sig')['photo_id']]
    return [parse_id(line.strip()) for line in open(path) if line.strip()]


def no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError(f'duplicate keys {keys}')
    return dict(pairs)


def bad_constant(name):
    raise ValueError(f'not a finite number: {name}')


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate(sub_path, ids):
    problems = []
    size = os.path.getsize(sub_path)
    if size > 5 * 1024 * 1024:
        problems.append(f'file is {size} bytes, more than 5 MiB')
    seen = {}
    with open(sub_path, encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line, object_pairs_hook=no_duplicate_keys, parse_constant=bad_constant)
            except ValueError as e:
                problems.append(f'line {n}: bad json: {e}')
                continue
            pid = row.get('photo_id')
            if not isinstance(pid, int) or isinstance(pid, bool):
                problems.append(f'line {n}: photo_id {pid!r} is not an integer')
            seen[pid] = seen.get(pid, 0) + 1
            extra = set(row) - {'photo_id', 'photo_url', 'boxes', 'error'}
            if extra:
                problems.append(f'line {n}: extra fields {sorted(extra)}')
            if row.get('error') is not None:
                problems.append(f'line {n}: photo {pid} has error {row["error"]!r}')
            boxes = row.get('boxes')
            if not isinstance(boxes, list):
                problems.append(f'line {n}: photo {pid} boxes is not a list')
                continue
            for b in boxes:
                if not isinstance(b, dict) or set(b) != {'left', 'top', 'width', 'height'}:
                    problems.append(f'line {n}: photo {pid} bad box {b}')
                    continue
                l, t, w, h = b['left'], b['top'], b['width'], b['height']
                if not all(is_number(v) for v in (l, t, w, h)):
                    problems.append(f'line {n}: photo {pid} non-numeric box {b}')
                elif w <= 0 or h <= 0 or l < 0 or t < 0 or l > 1 or t > 1 or w > 1 or h > 1 or l + w > 1 + 1e-9 or t + h > 1 + 1e-9:
                    problems.append(f'line {n}: photo {pid} box out of range {b}')
    ids = set(ids)
    missing = ids - set(seen)
    unknown = set(seen) - ids
    dups = [pid for pid, c in seen.items() if c > 1]
    if missing:
        problems.append(f'{len(missing)} ids missing, e.g. {sorted(map(str, missing))[:5]}')
    if unknown:
        problems.append(f'{len(unknown)} unknown ids, e.g. {sorted(map(str, unknown))[:5]}')
    if dups:
        problems.append(f'{len(dups)} duplicated ids, e.g. {dups[:5]}')
    return problems, len(seen), size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sub', required=True)
    parser.add_argument('--ids', required=True)
    args = parser.parse_args()
    ids = expected_ids(args.ids)
    problems, n, size = validate(args.sub, ids)
    for p in problems[:50]:
        print('ERROR', p)
    if problems:
        print(f'FAILED: {len(problems)} problems')
        sys.exit(1)
    print(f'OK: {n} photos (expected {len(ids)}), {size / 1024:.1f} KiB')


if __name__ == '__main__':
    main()
