import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metrics import match_counts, per_image, prf, summarize


def box(x1, y1, x2, y2, scale=0.05, shift=0.2):
    return {'left': x1 * scale + shift, 'top': y1 * scale + shift,
            'width': (x2 - x1) * scale, 'height': (y2 - y1) * scale}


def test_empty_vs_empty():
    assert match_counts([], [], 0.5) == (0, 0, 0)


def test_empty_gt_with_prediction():
    assert match_counts([], [box(0, 0, 10, 10)], 0.5) == (0, 1, 0)


def test_missed_box():
    assert match_counts([box(0, 0, 10, 10)], [], 0.5) == (0, 0, 1)


def test_exact_match():
    assert match_counts([box(0, 0, 10, 10)], [box(0, 0, 10, 10)], 0.5) == (1, 0, 0)


def test_low_overlap_is_fp_and_fn():
    assert match_counts([box(0, 0, 10, 10)], [box(5, 0, 15, 10)], 0.5) == (0, 1, 1)


def test_duplicate_prediction_counts_once():
    gt = [box(0, 0, 10, 10)]
    pred = [box(0, 0, 10, 10), box(0, 0, 10, 9)]
    assert match_counts(gt, pred, 0.5) == (1, 1, 0)


def test_iou_threshold_75():
    gt = [box(0, 0, 10, 10)]
    pred = [box(0, 0, 10, 7)]
    assert match_counts(gt, pred, 0.5) == (1, 0, 0)
    assert match_counts(gt, pred, 0.75) == (0, 1, 1)


def test_maximum_matching_beats_greedy():
    gt = [box(0, 0, 10, 10), box(2, 0, 12, 10)]
    pred = [box(1, 0, 11, 10), box(-2, 0, 8, 10)]
    assert match_counts(gt, pred, 0.5) == (2, 0, 0)


def test_overlapping_objects_each_matched():
    gt = [box(0, 0, 10, 10), box(6, 0, 16, 10)]
    pred = [box(6, 0, 16, 10), box(0, 0, 10, 10)]
    assert match_counts(gt, pred, 0.5) == (2, 0, 0)


def test_counts_summed_over_dataset():
    golden = {1: [box(0, 0, 10, 10)], 2: []}
    preds = {1: {'boxes': [box(0, 0, 10, 10)], 'error': None},
             2: {'boxes': [box(0, 0, 5, 5)], 'error': None}}
    res = summarize(per_image(golden, preds))
    assert (res['tp_50'], res['fp_50'], res['fn_50']) == (1, 1, 0)
    assert math.isclose(res['f1_50'], 2 / 3)
    assert res['neg_fp_boxes'] == 1 and res['neg_fp_images'] == 1


def test_error_is_counted_and_not_treated_as_correct_empty():
    golden = {1: [], 2: [box(0, 0, 10, 10)]}
    preds = {1: {'boxes': None, 'error': 'boom'}}
    res = summarize(per_image(golden, preds))
    assert res['errors'] == 2
    assert res['fn_50'] == 1


def test_prf():
    p, r, f1 = prf(3, 1, 2)
    assert math.isclose(p, 0.75) and math.isclose(r, 0.6) and math.isclose(f1, 6 / 9)
