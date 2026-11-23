import argparse

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--per-image', default='outputs/eval/per_image.csv')
    parser.add_argument('--a', required=True)
    parser.add_argument('--b', required=True)
    parser.add_argument('--n', type=int, default=5)
    args = parser.parse_args()

    df = pd.read_csv(args.per_image)
    a = df[df.run == args.a].set_index('photo_id')
    b = df[df.run == args.b].set_index('photo_id')
    both = a.add_suffix('_a').join(b.add_suffix('_b'))
    cols = ['n_gt_a', 'n_pred_a', 'tp50_a', 'fp50_a', 'fn50_a', 'n_pred_b', 'tp50_b', 'fp50_b', 'fn50_b']

    print(f'\n{args.a} finds more butterflies than {args.b}:')
    print(both[both.tp50_a > both.tp50_b][cols].head(args.n).to_string())
    print(f'\n{args.b} finds more butterflies than {args.a}:')
    print(both[both.tp50_b > both.tp50_a][cols].head(args.n).to_string())
    print(f'\n{args.a} has fewer false boxes than {args.b}:')
    print(both[both.fp50_a < both.fp50_b].sort_values('fp50_b', ascending=False)[cols].head(args.n).to_string())
    print(f'\n{args.b} has fewer false boxes than {args.a}:')
    print(both[both.fp50_b < both.fp50_a].sort_values('fp50_a', ascending=False)[cols].head(args.n).to_string())
    for name, part in ((args.a, a), (args.b, b)):
        print(f'\n{name}: box found but IoU < 0.5 (fp and fn on the same photo):')
        print(part[(part.fp50 > 0) & (part.fn50 > 0)][['n_gt', 'n_pred', 'tp50', 'fp50', 'fn50']].head(args.n).to_string())


if __name__ == '__main__':
    main()
