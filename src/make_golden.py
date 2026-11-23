import argparse
import json
import os

from common import write_jsonl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', default='Все-результаты-ШАД-817')
    parser.add_argument('--out', default='data/golden')
    args = parser.parse_args()

    prov = json.load(open(os.path.join(args.export, 'golden/provenance.json')))
    flagged = {c['photo_id'] for c in prov if c['low_control_reviewer']}
    rows = []
    for line in open(os.path.join(args.export, 'golden/candidate-golden.jsonl')):
        r = json.loads(line)
        boxes = [{k: b[k] for k in ('left', 'top', 'width', 'height')} for b in r['boxes']]
        rows.append({'photo_id': r['photo_id'], 'boxes': boxes, 'error': None})
    rows.sort(key=lambda r: r['photo_id'])
    strict = [r for r in rows if r['photo_id'] not in flagged]
    os.makedirs(args.out, exist_ok=True)
    write_jsonl(os.path.join(args.out, 'candidate_339.jsonl'), rows)
    write_jsonl(os.path.join(args.out, 'candidate_282.jsonl'), strict)
    for name, part in (('candidate_339', rows), ('candidate_282', strict)):
        empty = sum(len(r['boxes']) == 0 for r in part)
        boxes = sum(len(r['boxes']) for r in part)
        print(f'{name}: photos={len(part)} empty={empty} boxes={boxes}')


if __name__ == '__main__':
    main()
