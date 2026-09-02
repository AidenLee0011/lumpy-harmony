# -*- coding: utf-8 -*-
"""Paper 10 round 3 (sol P72_p10_r2 §4.6): held-out C12 -> D12 decomposition. sigma_C = sigma_D + Delta_inv, per event, exactly.
State x = key-relative (mask, mode) (C12 quotient by tonic anchoring); inversion kappa: mask -> reflect pcs (p -> -p mod 12); D12 fiber h(x) = {x, kappa x}.
Training law p_C from counts + alpha (edges); p_D = pushforward (sum over fiber). Held-out per-edge scores s_C = log2 p_C(x)/p_C(rx), s_D = log2 p_D(hx)/p_D(h rx),
delta = s_C - s_D. Groups: Bach by chorale, WJazzD by composition id. Reports sigma_C, sigma_D, Delta_inv, closure error, group LCB, alpha sensitivity,
inversion-fixed fiber mass; also the uncollapsed-event control.
  python -X utf8 irrev_inversion.py --source bach|wjazzd
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, random, statistics
from pathlib import Path
import irrev_bach as IB
from irrev_bach import groups, load_uncollapsed
H = Path(__file__).resolve().parent; D9 = H.parent / "p9_harmony" / "data"


def inv_mask(mask):
    return sum(1 << ((-p) % 12) for p in range(12) if mask >> p & 1)


def kappa(x):
    return (inv_mask(x[0]), x[1])


def hfib(e):
    """D12 fiber representative of an edge: min over identity/inversion applied to both endpoints"""
    a = e; b = (kappa(e[0]), kappa(e[1]))
    return min(a, b)


def run(source, collapse=True):
    works = IB.load(source) if collapse else load_uncollapsed(source)
    grp = groups(source, works); gids = sorted(set(grp.values()), key=lambda g: hashlib.sha256(g.encode()).hexdigest()); gfold = {g: i % 5 for i, g in enumerate(gids)}
    fold = {w: gfold[grp[w]] for w in works}; names = sorted(works)
    out = {"source": source, "collapsed": collapse, "works": len(works), "groups": len(gids), "alpha": {}}
    for alpha in (0.1, 0.5, 1.0):
        sC = sD = sI = 0.0; N = 0; closure = 0.0; fixed_mass = 0; per_group = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0])
        for k in range(5):
            train = collections.Counter(e for w in names if fold[w] != k for e in IB.edges(works[w]))
            # C12 law over all observed edges (train + reversed keys) with alpha; D12 law by pushforward over fibers
            keys = set(train) | {(j, i) for (i, j) in train}
            Z = sum(train[e] + alpha for e in keys)          # normaliser over the support of observed edges and their reversals
            def pC(e):
                return (train[e] + alpha) / Z if e in keys else alpha / Z
            fib = collections.defaultdict(float)
            for e in keys:
                fib[hfib(e)] += pC(e)
            def pD(e):
                f = hfib(e)
                return fib[f] if f in fib else (pC(e) + (pC((kappa(e[0]), kappa(e[1]))) if (kappa(e[0]), kappa(e[1])) != e else 0.0))
            for w in names:
                if fold[w] != k:
                    continue
                for (i, j) in IB.edges(works[w]):
                    x = (i, j); rx = (j, i)
                    sc = math.log2(pC(x) / pC(rx)); sd = math.log2(pD(x) / pD(rx)); di = sc - sd
                    sC += sc; sD += sd; sI += di; N += 1; closure = max(closure, abs(sc - (sd + di)))
                    if hfib(x) == hfib(rx):
                        fixed_mass += 1
                    g = per_group[grp[w]]; g[0] += sc; g[1] += sd; g[2] += di; g[3] += 1
        gi = [v[2] / v[3] for v in per_group.values() if v[3]]
        m = statistics.mean(gi); sd_ = statistics.stdev(gi); lcb = m - 1.96 * sd_ / math.sqrt(len(gi))
        # cluster (group) bootstrap of the event-weighted quantities: resample groups with replacement, no refit (held-out scores fixed)
        G = [v for v in per_group.values() if v[3]]; rng = random.Random(20260903); bd = []; bs = []
        for _ in range(2000):
            smp = [G[rng.randrange(len(G))] for _ in G]; tC = sum(g[0] for g in smp); tI = sum(g[2] for g in smp); tn = sum(g[3] for g in smp)
            bd.append(tI / tn); bs.append((tI / tn) / (tC / tn))
        bd.sort(); bs.sort(); q = lambda arr, p: arr[int(p * (len(arr) - 1))]
        boot = dict(Delta_inv_p05=round(q(bd, 0.05), 4), Delta_inv_p95=round(q(bd, 0.95), 4), share_p05=round(q(bs, 0.05), 4), share_p95=round(q(bs, 0.95), 4), B=2000)
        out["alpha"]["%g" % alpha] = dict(N=N, sigma_C=round(sC / N, 4), sigma_D=round(sD / N, 4), Delta_inv=round(sI / N, 4), residual_share=round((sI / N) / (sC / N), 4) if sC else None,
                                          closure_max_err=closure, inversion_fixed_fiber_share=round(fixed_mass / N, 4), groups=len(gi), group_mean=round(m, 4), group_sd=round(sd_, 4), group_LCB95=round(lcb, 4), group_bootstrap=boot)
        print(source, "collapsed" if collapse else "uncollapsed", "alpha", alpha, out["alpha"]["%g" % alpha], flush=True)
    out["M_min_LCB"] = min(v["group_LCB95"] for v in out["alpha"].values()); out["C4_gate_M_gt_0_10"] = out["M_min_LCB"] > 0.10
    (H / ("irrev_inversion_%s%s.json" % (source, "" if collapse else "_uncollapsed"))).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="bach"); ap.add_argument("--uncollapsed", action="store_true"); a = ap.parse_args()
    run(a.source, collapse=not a.uncollapsed)
