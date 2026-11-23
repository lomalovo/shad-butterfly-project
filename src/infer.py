import argparse
import json
import os
import platform
import re
import subprocess
import time
import traceback

os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')

import torch
import transformers
import yaml

from common import append_jsonl, list_images, load_image, norm_box, read_jsonl, write_jsonl

DTYPES = {'float32': torch.float32, 'float16': torch.float16, 'bfloat16': torch.bfloat16}
BBOX_RE = re.compile(r'"bbox_2d"\s*:\s*\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]'
                     r'(?:\s*,\s*"label"\s*:\s*"([^"]*)")?')


class GroundingDino:
    def __init__(self, cfg):
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
        self.cfg = cfg
        self.processor = AutoProcessor.from_pretrained(cfg['model_id'], revision=cfg['revision'])
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(
            cfg['model_id'], revision=cfg['revision'], dtype=DTYPES[cfg['dtype']]).to(cfg['device']).eval()
        self.phrases = [p.strip() for p in cfg['prompt'].split('.') if p.strip()]

    def phrase_spans(self, input_ids):
        dot = self.processor.tokenizer.convert_tokens_to_ids('.')
        spans, start = [], 1
        for i, t in enumerate(input_ids.tolist()):
            if t == dot:
                spans.append((start, i))
                start = i + 1
        assert len(spans) == len(self.phrases)
        return spans

    def predict(self, img):
        w, h = img.size
        inputs = self.processor(images=img, text=self.cfg['prompt'], return_tensors='pt').to(self.cfg['device'])
        with torch.no_grad():
            outputs = self.model(**inputs)
        t = self.cfg['raw_threshold']
        res = self.processor.post_process_grounded_object_detection(
            outputs, inputs.input_ids, threshold=t, text_threshold=t, target_sizes=[(h, w)])[0]
        probs = outputs.logits[0].sigmoid().float().cpu()
        keep = probs.max(-1).values > t
        spans = self.phrase_spans(inputs.input_ids[0])
        phrase_probs = torch.stack([probs[keep][:, a:b].max(-1).values for a, b in spans], -1)
        labels = [self.phrases[i] for i in phrase_probs.argmax(-1).tolist()]
        assert len(labels) == len(res['scores'])
        boxes = []
        for box, score, label in zip(res['boxes'].tolist(), res['scores'].tolist(), labels):
            b = norm_box(*box, w, h, score=round(score, 5), label=label)
            if b:
                boxes.append(b)
        return {'boxes': boxes}


class Owlv2:
    def __init__(self, cfg):
        from transformers import Owlv2ForObjectDetection, Owlv2Processor
        self.cfg = cfg
        self.processor = Owlv2Processor.from_pretrained(cfg['model_id'], revision=cfg['revision'])
        self.model = Owlv2ForObjectDetection.from_pretrained(
            cfg['model_id'], revision=cfg['revision'], dtype=DTYPES[cfg['dtype']]).to(cfg['device']).eval()

    def predict(self, img):
        w, h = img.size
        s = max(w, h)
        queries = self.cfg['queries']
        inputs = self.processor(text=[queries], images=img, return_tensors='pt').to(self.cfg['device'])
        with torch.no_grad():
            outputs = self.model(**inputs)
        res = self.processor.post_process_grounded_object_detection(
            outputs, threshold=self.cfg['raw_threshold'], target_sizes=[(s, s)])[0]
        boxes = []
        for box, score, label in zip(res['boxes'].tolist(), res['scores'].tolist(), res['labels'].tolist()):
            b = norm_box(*box, w, h, score=round(score, 5), label=queries[label])
            if b:
                boxes.append(b)
        return {'boxes': boxes}


def parse_qwen(text):
    s = text.strip()
    s = re.sub(r'^```(json)?', '', s).strip()
    s = re.sub(r'```$', '', s).strip()
    try:
        data = json.loads(s)
        if isinstance(data, dict):
            data = [data]
        return [([float(v) for v in d['bbox_2d']], d.get('label')) for d in data]
    except Exception:
        found = [([float(v) for v in m[:4]], m[4] or None) for m in BBOX_RE.findall(text)]
        if not found:
            raise ValueError('cannot parse model answer')
        return found


class QwenVL:
    def __init__(self, cfg):
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration
        self.cfg = cfg
        self.processor = AutoProcessor.from_pretrained(cfg['model_id'], revision=cfg['revision'])
        self.processor.image_processor.size = {'shortest_edge': cfg['min_pixels'], 'longest_edge': cfg['max_pixels']}
        self.model = Qwen3VLForConditionalGeneration.from_pretrained(
            cfg['model_id'], revision=cfg['revision'], dtype=DTYPES[cfg['dtype']]).to(cfg['device']).eval()

    def predict(self, img):
        w, h = img.size
        messages = [{'role': 'user', 'content': [{'type': 'image'}, {'type': 'text', 'text': self.cfg['prompt']}]}]
        text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=[img], return_tensors='pt').to(self.cfg['device'])
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=self.cfg['max_new_tokens'], do_sample=False)
        new_tokens = out[0, inputs.input_ids.shape[1]:]
        raw_text = self.processor.decode(new_tokens, skip_special_tokens=True)
        truncated = len(new_tokens) >= self.cfg['max_new_tokens']
        try:
            coords = parse_qwen(raw_text)
        except ValueError as e:
            raise ValueError(f'{e}; raw_text={raw_text!r}')
        boxes, dropped = [], []
        for c, label in coords:
            if len(c) != 4 or min(c) < 0 or max(c) > 1000 or c[2] <= c[0] or c[3] <= c[1]:
                dropped.append(c)
                continue
            x1, y1, x2, y2 = c
            b = norm_box(x1 / 1000 * w, y1 / 1000 * h, x2 / 1000 * w, y2 / 1000 * h, w, h, label=label)
            if b:
                boxes.append(b)
        return {'boxes': boxes, 'raw_text': raw_text, 'dropped': dropped, 'truncated': truncated}


MODELS = {'grounding_dino': GroundingDino, 'owlv2': Owlv2, 'qwen3_vl': QwenVL}


def env_info(cfg):
    try:
        cpu = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
    except Exception:
        cpu = platform.processor()
    return {
        'config': cfg,
        'torch': torch.__version__,
        'transformers': transformers.__version__,
        'python': platform.python_version(),
        'platform': platform.platform(),
        'cpu': cpu,
        'device': cfg['device'],
        'dtype': cfg['dtype'],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--images', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--errors', default='outputs/logs/errors.jsonl')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--attempts', type=int, default=2)
    args = parser.parse_args()

    cfg = yaml.safe_load(open(args.config))
    run = os.path.splitext(os.path.basename(args.out))[0]
    items = list_images(args.images)[:args.limit]

    done = {}
    if os.path.exists(args.out):
        for row in read_jsonl(args.out):
            done[row['photo_id']] = row
    todo = [(pid, path) for pid, path in items if pid not in done or done[pid]['error'] is not None]
    print(f'{run}: {len(items)} images, {len(todo)} to process')

    model = MODELS[cfg['model']](cfg)
    start = time.time()
    for i, (pid, path) in enumerate(todo):
        row = None
        for attempt in range(1, args.attempts + 1):
            t0 = time.perf_counter()
            try:
                img = load_image(path)
                res = model.predict(img)
                row = {'photo_id': pid, 'error': None, 'time_s': round(time.perf_counter() - t0, 3),
                       'width': img.size[0], 'height': img.size[1], 'attempt': attempt, **res}
                if res.get('dropped') or res.get('truncated'):
                    append_jsonl(args.errors, {'run': run, 'photo_id': pid, 'attempt': attempt, 'kind': 'warning',
                                               'dropped': res.get('dropped'), 'truncated': res.get('truncated')})
                break
            except Exception as e:
                msg = f'{type(e).__name__}: {e}'
                append_jsonl(args.errors, {'run': run, 'photo_id': pid, 'attempt': attempt, 'kind': 'error',
                                           'error': msg, 'traceback': traceback.format_exc()[-2000:]})
                row = {'photo_id': pid, 'boxes': None, 'error': msg, 'time_s': round(time.perf_counter() - t0, 3),
                       'attempt': attempt}
                if cfg['device'] == 'mps':
                    torch.mps.empty_cache()
        done[pid] = row
        append_jsonl(args.out, row)
        if (i + 1) % 20 == 0 or i + 1 == len(todo):
            print(f'{i + 1}/{len(todo)} {time.time() - start:.0f}s', flush=True)

    rows = [done[pid] for pid, _ in items if pid in done]
    write_jsonl(args.out, rows)
    info = env_info(cfg)
    info['images'] = len(rows)
    info['errors'] = sum(r['error'] is not None for r in rows)
    info['total_time_s'] = round(sum(r['time_s'] for r in rows), 1)
    with open(args.out.replace('.jsonl', '.meta.json'), 'w') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(f'errors: {info["errors"]}, total time {info["total_time_s"]}s')


if __name__ == '__main__':
    main()
