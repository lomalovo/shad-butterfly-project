import argparse
import json
import os
import time

import torch
import yaml

from common import list_images, load_image, read_jsonl, write_jsonl
from infer import QwenVL, env_info


def crop(img, b, pad):
    w, h = img.size
    x1 = (b['left'] - pad * b['width']) * w
    y1 = (b['top'] - pad * b['height']) * h
    x2 = (b['left'] + (1 + pad) * b['width']) * w
    y2 = (b['top'] + (1 + pad) * b['height']) * h
    return img.crop((max(0, round(x1)), max(0, round(y1)), min(w, round(x2)), min(h, round(y2))))


class Verifier(QwenVL):
    def __init__(self, cfg):
        super().__init__(cfg)
        tok = self.processor.tokenizer
        self.yes = [tok.convert_tokens_to_ids(t) for t in ('yes', 'Yes')]
        self.no = [tok.convert_tokens_to_ids(t) for t in ('no', 'No')]

    def score(self, img):
        messages = [{'role': 'user', 'content': [{'type': 'image'}, {'type': 'text', 'text': self.cfg['verify_prompt']}]}]
        text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=[img], return_tensors='pt').to(self.cfg['device'])
        with torch.no_grad():
            logits = self.model(**inputs).logits[0, -1].float()
        probs = logits.softmax(-1)
        p_yes = probs[self.yes].sum().item()
        p_no = probs[self.no].sum().item()
        return p_yes / (p_yes + p_no)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--images', required=True)
    parser.add_argument('--raw', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    cfg = yaml.safe_load(open(args.config))
    keep_labels = cfg['keep_labels']
    paths = dict(list_images(args.images))
    rows = read_jsonl(args.raw)
    model = Verifier(cfg)
    start = time.time()
    n_boxes = 0
    for i, row in enumerate(rows):
        if row['error'] is not None:
            continue
        t0 = time.perf_counter()
        img = load_image(paths[row['photo_id']])
        for b in row['boxes']:
            if str(b['label']).lower().strip() in keep_labels:
                b['score'] = round(model.score(crop(img, b, cfg['verify_pad'])), 5)
                n_boxes += 1
        row['verify_time_s'] = round(time.perf_counter() - t0, 3)
        if (i + 1) % 50 == 0 or i + 1 == len(rows):
            print(f'{i + 1}/{len(rows)} {time.time() - start:.0f}s', flush=True)
    write_jsonl(args.out, rows)
    info = env_info(cfg)
    info['images'] = len(rows)
    info['errors'] = sum(r['error'] is not None for r in rows)
    info['verified_boxes'] = n_boxes
    info['total_time_s'] = round(sum(r['time_s'] + r.get('verify_time_s', 0) for r in rows), 1)
    info['verify_time_s'] = round(sum(r.get('verify_time_s', 0) for r in rows), 1)
    with open(args.out.replace('.jsonl', '.meta.json'), 'w') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(f'verified {n_boxes} boxes, {info["verify_time_s"]}s')


if __name__ == '__main__':
    main()
