# -*- coding: utf-8 -*-
"""Paper 10 round 5 (sol P72_p10_r4 §4): mode-composition audit of the held-out C12 -> D12 allocation.
Estimates Delta_inv share on major-only and minor-only held-out events (training on all), plus the observed mixture and a common-mode-weighted mixture
(weights = pooled major/minor event shares across both corpora). alpha in {0.1, 0.5, 1}.  python -X utf8 irrev_mode.py
"""
import collections, hashlib, json, math, statistics
from pathlib import Path
import irrev_bach as IB
from irrev_inversion import kappa, hfib
H = Path(__file__).resolve().parent


def scores(source, alpha):
    works = IB.load(source); grp = IB.groups(source, works)
    gids = sorted(set(grp.values()), key=lambda g: hashlib.sha256(g.encode()).hexdigest()); gfold = {g: i % 5 for i, g in enumerate(gids)}; fold = {w: gfold[grp[w]] for w in works}
    names = sorted(works); ev = []  # (group, mode, sC, dI, kappa_edge_in_training_support)
    for f in range(5):
        train = collections.Counter(e for w in names if fold[w] != f for e in IB.edges(works[w]))
        keys = set(train) | {(j, i) for (i, j) in train}; Z = sum(train[e] + alpha for e in keys)
        def pC(e): return (train[e] + alpha) / Z if e in keys else alpha / Z
        fib = collections.defaultdict(float)
        for e in keys:
            fib[hfib(e)] += pC(e)
        def pD(e):
            ff = hfib(e); ke = (kappa(e[0]), kappa(e[1]))
            return fib[ff] if ff in fib else pC(e) + (pC(ke) if ke != e else 0.0)
        for w in names:
            if fold[w] != f:
                continue
            for (i, j) in IB.edges(works[w]):
                sc = math.log2(pC((i, j)) / pC((j, i))); sd = math.log2(pD((i, j)) / pD((j, i)))
                ke = (kappa(i), kappa(j)); ev.append((grp[w], i[1], sc, sc - sd, int(ke in keys and ke != (i, j))))
    return ev


def summ(ev):
    if not ev:
        return None
    N = len(ev); sC = sum(e[2] for e in ev) / N; dI = sum(e[3] for e in ev) / N
    per = collections.defaultdict(lambda: [0.0, 0])
    for g, _, _, d, _k in ev:
        per[g][0] += d; per[g][1] += 1
    gi = [v[0] / v[1] for v in per.values()]; m = statistics.mean(gi); s = statistics.stdev(gi) if len(gi) > 1 else 0.0
    return dict(events=N, kappa_support_share=round(sum(e[4] for e in ev) / N, 4), sigma_C=round(sC, 4), Delta_inv=round(dI, 4), share=round(dI / sC, 4) if sC else None, groups=len(gi), group_mean=round(m, 4), group_LCB95=round(m - 1.645 * s / math.sqrt(len(gi)), 4))


if __name__ == "__main__":
    out = {"alpha": {}}
    for alpha in (0.1, 0.5, 1.0):
        E = {c: scores(c, alpha) for c in ("bach", "wjazzd")}
        modes = sorted({e[1] for c in E for e in E[c]})
        pooled = collections.Counter(e[1] for c in E for e in E[c]); tot = sum(pooled.values()); wcom = {m: pooled[m] / tot for m in modes}
        res = {}
        for c in E:
            r = {"observed": summ(E[c]), "by_mode": {str(m): summ([e for e in E[c] if e[1] == m]) for m in modes}}
            r["mode_mix"] = {str(m): round(sum(1 for e in E[c] if e[1] == m) / len(E[c]), 4) for m in modes}
            bm = r["by_mode"]; cw = {m: wcom[m] for m in modes if bm[str(m)]}; zc = sum(cw.values())
            r["common_weighted"] = dict(Delta_inv=round(sum(cw[m] / zc * bm[str(m)]["Delta_inv"] for m in cw), 4), sigma_C=round(sum(cw[m] / zc * bm[str(m)]["sigma_C"] for m in cw), 4))
            r["common_weighted"]["share"] = round(r["common_weighted"]["Delta_inv"] / r["common_weighted"]["sigma_C"], 4)
            res[c] = r
        out["alpha"]["%g" % alpha] = dict(common_weights={str(m): round(wcom[m], 4) for m in modes}, corpora=res)
        print(alpha, json.dumps(res, indent=None)[:1500], flush=True)
    (H / "irrev_mode.json").write_text(json.dumps(out, indent=1), encoding="utf-8"); print("written")
