import argparse

import numpy as np
import pandas as pd

from evaluate import load_golden, load_preds
from metrics import per_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--golden', required=True)
    parser.add_argument('--a', required=True)
    parser.add_argument('--b', required=True)
    parser.add_argument('--n', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()

    golden = load_golden(args.golden)
    a = pd.DataFrame(per_image(golden, load_preds(args.a)))
    b = pd.DataFrame(per_image(golden, load_preds(args.b)))
    rng = np.random.default_rng(args.seed)
    idx = rng.integers(0, len(a), size=(args.n, len(a)))
    cols = ['tp50', 'fp50', 'fn50']
    sa = {c: a[c].to_numpy()[idx].sum(1) for c in cols}
    sb = {c: b[c].to_numpy()[idx].sum(1) for c in cols}
    fa = 2 * sa['tp50'] / (2 * sa['tp50'] + sa['fp50'] + sa['fn50'])
    fb = 2 * sb['tp50'] / (2 * sb['tp50'] + sb['fp50'] + sb['fn50'])
    diff = fb - fa
    full_a = 2 * a.tp50.sum() / (2 * a.tp50.sum() + a.fp50.sum() + a.fn50.sum())
    full_b = 2 * b.tp50.sum() / (2 * b.tp50.sum() + b.fp50.sum() + b.fn50.sum())
    print(f'{len(a)} photos, F1@0.5: a={full_a:.3f} b={full_b:.3f} diff={full_b - full_a:+.3f}')
    print(f'bootstrap {args.n}: diff 95% interval [{np.quantile(diff, 0.025):+.3f}, {np.quantile(diff, 0.975):+.3f}], '
          f'b better in {(diff > 0).mean():.1%}, equal in {(diff == 0).mean():.1%}')


if __name__ == '__main__':
    main()
