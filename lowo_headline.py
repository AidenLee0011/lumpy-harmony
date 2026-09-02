# -*- coding: utf-8 -*-
"""Paper 9 round-4 item 1: leave-one-WORK-out for every headline representation and target (sol P72_p9_r4 §3).
Gate: at both m, Beethoven-sonata base residue minus max(ABC, Mozart) residue > 0.05; combined clean sonata residue > 0.
Also item 3: work-level bounded betting e-process on sonata work gains vs H0: E[d] <= 0.05 (clipped to [-B, B], B = 0.3, lambda grid mixture).
  python -X utf8 lowo_headline.py --m 1,2
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, re, statistics, sys
from pathlib import Path
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
import repair_lattice as R  # noqa: E402

CORP = ["beethoven_piano_sonatas", "ABC", "mozart_piano_sonatas"]


def work_groups(movs):
    g = collections.defaultdict(list)
    for stem, work, mv in movs:
        g[work].append((stem, mv))
    return g


def lowo(corpus, m, target):
    movs = R.load(corpus); groups = work_groups(movs)
    rows = {stem: R.build(mv, m, target) for stem, w, mv in movs}
    tot = collections.Counter(); N = 0; per_work = []
    for work, members in groups.items():
        train = [r for stem2, w2, mv2 in movs if w2 != work for r in rows[stem2]]
        alphabet = {r[4] for r in train}
        held = [rows[stem] for stem, _ in members]
        L = {k: R.code(train, None, k, alphabet, reset_per_movement=held) for k in ("geom", "Z", "Fsel")}
        n = sum(len(h) for h in held); N += n
        for k in L:
            tot[k] += L[k]
        per_work.append((L["Z"] - L["Fsel"]) / n)
    return dict(corpus=corpus, m=m, target=target, works=len(groups), N=N, bits={k: round(v / N, 4) for k, v in tot.items()}, residue=round((tot["Z"] - tot["Fsel"]) / N, 4),
                work_gains=[round(x, 4) for x in per_work], work_mean=round(statistics.mean(per_work), 4), works_positive=round(sum(1 for x in per_work if x > 0) / len(per_work), 3))


def betting_e(gains, tau=0.05, B=0.3):
    """mixture over lambda in {0.25,0.5,1,2}/B of exp(lambda*sum(x) - lambda^2 n B^2/2), x = clip(d,-B,B) - tau; fixed SHA order of works."""
    xs = [max(-B, min(B, d)) - tau for d in gains]
    lams = [0.25 / B, 0.5 / B, 1.0 / B, 2.0 / B]
    Emax = 0.0; path = []
    s = 0.0
    for n, x in enumerate(xs, 1):
        s += x
        E = sum(math.exp(l * s - l * l * n * B * B / 2) for l in lams) / len(lams)
        path.append(round(E, 3)); Emax = max(Emax, E)
    return dict(E_final=round(path[-1], 3) if path else None, E_max=round(Emax, 3), n=len(xs), reject_20=Emax >= 20)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--m", default="1,2"); a = ap.parse_args()
    out = {"lowo": [], "gate": {}}
    for m in [int(x) for x in a.m.split(",")]:
        res = {c: {t: lowo(c, m, t) for t in ("base", "clean")} for c in CORP}
        for c in CORP:
            for t in ("base", "clean"):
                out["lowo"].append(res[c][t]); print(c, "m=%d" % m, t, "residue", res[c][t]["residue"], "works+", res[c][t]["works_positive"], flush=True)
        margin = res["beethoven_piano_sonatas"]["base"]["residue"] - max(res["ABC"]["base"]["residue"], res["mozart_piano_sonatas"]["base"]["residue"])
        gains = res["beethoven_piano_sonatas"]["base"]["work_gains"]
        out["gate"]["m=%d" % m] = dict(base_margin=round(margin, 4), base_margin_gt_0_05=margin > 0.05, clean_sonata_residue=res["beethoven_piano_sonatas"]["clean"]["residue"],
                                       clean_gt_0=res["beethoven_piano_sonatas"]["clean"]["residue"] > 0, betting_e_base_tau005=betting_e(gains), betting_e_clean_tau0=betting_e(res["beethoven_piano_sonatas"]["clean"]["work_gains"], tau=0.0))
        print("GATE", "m=%d" % m, out["gate"]["m=%d" % m], flush=True)
    (D / "lowo_headline.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
