# -*- coding: utf-8 -*-
"""Paper 10 round-2 (sol P72_p10_r1 §5): does the score persist on bidirectionally observed edges?
Training-defined bilateral support B_{f,r} = {(i,j): c_ij >= r and c_ji >= r} with r in {1,2,5}; smoothing alpha in {0.01,0.1,0.5,1,2};
retained event mass rho_r, retained-total score, conditional bilateral score, work LCB (excluded edges = 0). Folds: Bach by chorale; WJazzD by
COMPOSITION (compid) so multiple solos on one tune never cross folds. Also reports uncollapsed-event scores.
Pass (sol): r=1 WJazzD retained-total >= 50% of the all-edge score and retained-total work LCB > 0.50 for alpha in {0.1,0.5,1}.
  python -X utf8 irrev_support.py --source bach|wjazzd
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, sqlite3, statistics
from pathlib import Path
import irrev_bach as IB
H = Path(__file__).resolve().parent; D9 = H.parent / "p9_harmony" / "data"


def groups(source, works):
    if source != "wjazzd":
        return {w: w for w in works}
    c = sqlite3.connect(str(D9 / "wjazzd.db"))
    comp = {("wjazzd/%d" % melid): str(compid) for melid, compid in c.execute("select melid, compid from solo_info")}
    return {w: comp.get(w, w) for w in works}


def run(source, collapse=True):
    works = IB.load(source) if collapse else IB.load_uncollapsed(source)
    grp = groups(source, works)
    gids = sorted(set(grp.values()), key=lambda g: hashlib.sha256(g.encode()).hexdigest()); gfold = {g: i % 5 for i, g in enumerate(gids)}
    fold = {w: gfold[grp[w]] for w in works}
    names = sorted(works)
    out = {"source": source, "collapsed": collapse, "works": len(works), "groups": len(gids), "results": {}}
    for alpha in (0.01, 0.1, 0.5, 1.0, 2.0):
        for r in (0, 1, 2, 5):   # r=0 = all edges
            per_work = []; tot = 0.0; ret = 0; N = 0; zero_works = 0
            for k in range(5):
                train = collections.Counter(e for w in names if fold[w] != k for e in IB.edges(works[w]))
                for w in names:
                    if fold[w] != k:
                        continue
                    es = IB.edges(works[w]); s = 0.0; kept = 0
                    for (i, j) in es:
                        if r == 0 or (train[(i, j)] >= r and train[(j, i)] >= r):
                            s += math.log2((train[(i, j)] + alpha) / (train[(j, i)] + alpha)); kept += 1
                    if es:
                        per_work.append(s / len(es)); tot += s; N += len(es); ret += kept; zero_works += 1 if kept == 0 else 0
            m = statistics.mean(per_work); sd = statistics.stdev(per_work); lcb = m - 1.96 * sd / math.sqrt(len(per_work))
            key = "alpha=%g|r=%d" % (alpha, r)
            out["results"][key] = dict(rho=round(ret / N, 4), retained_total=round(tot / N, 4), conditional=round(tot / max(ret, 1), 4), work_mean=round(m, 4), work_LCB95=round(lcb, 4), zero_works=zero_works)
    for alpha in (0.1, 0.5, 1.0):
        a = out["results"]["alpha=%g|r=0" % alpha]["retained_total"]; b = out["results"]["alpha=%g|r=1" % alpha]
        out["gate_alpha=%g" % alpha] = dict(all_edges=a, r1_total=b["retained_total"], share=round(b["retained_total"] / a, 3) if a else None, r1_LCB=b["work_LCB95"], pass_share=b["retained_total"] >= 0.5 * a, pass_lcb=b["work_LCB95"] > 0.5)
    print(json.dumps({k: v for k, v in out.items() if k != "results"}, indent=1))
    for k in ("alpha=0.5|r=0", "alpha=0.5|r=1", "alpha=0.5|r=2", "alpha=0.5|r=5", "alpha=0.01|r=1", "alpha=2|r=1"):
        print(k, out["results"][k])
    (H / ("irrev_support_%s%s.json" % (source, "" if collapse else "_uncollapsed"))).write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="wjazzd"); ap.add_argument("--uncollapsed", action="store_true"); a = ap.parse_args()
    run(a.source, collapse=not a.uncollapsed)
