from scipy.optimize import linear_sum_assignment

from common import iou_matrix


def match_counts(gt, pred, thr):
    if len(gt) == 0 or len(pred) == 0:
        return 0, len(pred), len(gt)
    hit = (iou_matrix(gt, pred) >= thr).astype(float)
    rows, cols = linear_sum_assignment(hit, maximize=True)
    tp = int(hit[rows, cols].sum())
    return tp, len(pred) - tp, len(gt) - tp


def prf(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else float('nan')
    recall = tp / (tp + fn) if tp + fn else float('nan')
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else float('nan')
    return precision, recall, f1


def per_image(golden, preds, thresholds=(0.5, 0.75)):
    rows = []
    for pid, gt in golden.items():
        pred = preds.get(pid)
        error = pred is None or pred['error'] is not None
        boxes = [] if error else pred['boxes']
        row = {'photo_id': pid, 'n_gt': len(gt), 'n_pred': len(boxes), 'error': error}
        for thr in thresholds:
            tp, fp, fn = match_counts(gt, boxes, thr)
            key = int(thr * 100)
            row[f'tp{key}'], row[f'fp{key}'], row[f'fn{key}'] = tp, fp, fn
        rows.append(row)
    return rows


def summarize(rows):
    res = {'n_images': len(rows)}
    for key in (50, 75):
        tp = sum(r[f'tp{key}'] for r in rows)
        fp = sum(r[f'fp{key}'] for r in rows)
        fn = sum(r[f'fn{key}'] for r in rows)
        p, r_, f1 = prf(tp, fp, fn)
        res.update({f'f1_{key}': f1, f'precision_{key}': p, f'recall_{key}': r_,
                    f'tp_{key}': tp, f'fp_{key}': fp, f'fn_{key}': fn})
    neg = [r for r in rows if r['n_gt'] == 0]
    res['neg_images'] = len(neg)
    res['neg_fp_boxes'] = sum(r['n_pred'] for r in neg)
    res['neg_fp_images'] = sum(r['n_pred'] > 0 for r in neg)
    res['errors'] = sum(r['error'] for r in rows)
    return res
