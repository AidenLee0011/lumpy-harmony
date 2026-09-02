# -*- coding: utf-8 -*-
"""Paper 9 round-3 controls (sol P72_p9_r2 §4 items 1-7): does the Beethoven-sonata residue survive?

Variants (each on ABC and beethoven_piano_sonatas, m in {1,2}):
  base      : as pilot (root-normalised geometry, pcs-collapse, transductive alphabet, func = numeral|mode|type, beta=1)
  rootfree  : geometry canonicalised WITHOUT the analysed root: transition = (prime-form-normalised prev pcs by its lowest pc,
              pc shift between lowest pcs, next pcs relative to prev lowest, vl cost) -> no analyst root in the geometry
  nocollapse: keep every DCML event (no pitch-set collapse) so reinterpretations/relabelings survive
  fullroman : func = numeral|mode|chord_type|relativeroot|figbass|changes|form (complete label content)
  fixedalpha: target alphabet fixed from the training movements + UNK (held-out unseen orbits coded as UNK), no transductive alphabet
  target_nocur: target = (root displacement, vl cost) only, dropping the next pcs shape
  beta in {0.25, 0.5, 2, 4}: coder sensitivity
Output: data/controls_r3.json with bits/chord for geom, localrel, func and residue = localrel - func per variant.
"""
from __future__ import annotations
import argparse, collections, itertools, json, math, sys
from pathlib import Path
import pandas as pd
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
from corpora import _dcml_key, _roman_to_pc  # noqa: E402
from pilot_residue import fifths_to_pc, vl_cost  # noqa: E402


def load(corpus, collapse=True):
    movs = []
    for f in sorted((D / corpus / "harmonies").glob("*.tsv")):
        df = pd.read_csv(f, sep="\t", low_memory=False)
        gk, gmode = _dcml_key(df["globalkey"].iloc[0])
        ev = []
        for _, r in df.iterrows():
            numeral = r.get("numeral"); ct = r.get("chord_tones"); lk = r.get("localkey")
            if not isinstance(numeral, str) or not isinstance(ct, str) or not isinstance(lk, str) or gk is None:
                continue
            lk_pc = _roman_to_pc(lk, gk, gmode)
            if lk_pc is None:
                continue
            try:
                tones = tuple(sorted({(lk_pc + fifths_to_pc(t)) % 12 for t in ct.split(",") if t.strip() != ""}))
            except ValueError:
                continue
            if not tones:
                continue
            root = (lk_pc + fifths_to_pc(r.get("root"))) % 12 if str(r.get("root")) not in ("nan", "") else tones[0]
            lmode = "m" if bool(r.get("localkey_is_minor")) else "M"
            base = "%d|%s|%s" % ((root - lk_pc) % 12, r.get("chord_type"), lmode)
            func = "%s|%s|%s" % (numeral, lmode, r.get("chord_type"))
            full = func + "|%s|%s|%s|%s" % (r.get("relativeroot"), r.get("figbass"), r.get("changes"), r.get("form"))
            nested = func + "|%s" % r.get("relativeroot")   # numeral + relativeroot + mode + type determines the chromatic degree: a genuine refinement of Z
            ev.append(dict(pcs=tones, root=root, base=base, func=func, full=full, nested=nested))
        if collapse:
            coll = []
            for e in ev:
                if coll and coll[-1]["pcs"] == e["pcs"]:
                    continue
                coll.append(e)
            ev = coll
        if len(ev) >= 8:
            movs.append((f.stem, ev))
    return movs


def trans_root(prev, cur):
    r = prev["root"]
    return (tuple(sorted((x - r) % 12 for x in prev["pcs"])), (cur["root"] - r) % 12, tuple(sorted((x - r) % 12 for x in cur["pcs"])), vl_cost(prev["pcs"], cur["pcs"]))


def trans_rootfree(prev, cur):
    """normalise by the transposition that sends prev pcs to its lexicographically smallest rotation (prime-form style), no analyst root"""
    best = None
    for s in range(12):
        cand = tuple(sorted((x + s) % 12 for x in prev["pcs"]))
        if best is None or cand < best[0]:
            best = (cand, s)
    p, s = best
    c = tuple(sorted((x + s) % 12 for x in cur["pcs"]))
    return (p, c, vl_cost(prev["pcs"], cur["pcs"]))


def build_rows(mov, m, tfun, label_key, target_nocur):
    trans = [tfun(mov[i], mov[i + 1]) for i in range(len(mov) - 1)]
    tgt = [(t[1], t[-1]) if target_nocur else t for t in trans]     # (displacement or shape, cost) when nocur
    out = []
    for t in range(m, len(trans)):
        geom = tuple(trans[t - m:t]); e = mov[t]
        out.append(({"geom": geom, "localrel": (geom, e["base"]), "func": (geom, e[label_key])}, tgt[t]))
    return out


def code(train, test, key, beta, fixed_alpha):
    if fixed_alpha:
        alphabet = {y for _, y in train}; UNK = "UNK"
        def sym(y): return y if y in alphabet else UNK
        K = len(alphabet) + 1
    else:
        alphabet = {y for _, y in train} | {y for _, y in test}; K = len(alphabet)
        def sym(y): return y
    cg = collections.defaultdict(collections.Counter); cf = collections.defaultdict(collections.Counter)
    for ctx, y in train:
        cg[ctx["geom"]][sym(y)] += 1; cf[ctx[key]][sym(y)] += 1
    bits = 0.0
    for ctx, y in test:
        y = sym(y); g = cg[ctx["geom"]]; ng = sum(g.values()); pg = (g[y] + 0.5) / (ng + 0.5 * K)
        p = pg if key == "geom" else (cf[ctx[key]][y] + beta * pg) / (sum(cf[ctx[key]].values()) + beta)
        bits += -math.log2(p); g[y] += 1; cf[ctx[key]][y] += 1
    return bits


def evaluate(movs, m, tfun, label_key, target_nocur, beta, fixed_alpha):
    rows = {n: build_rows(mv, m, tfun, label_key, target_nocur) for n, mv in movs}
    tot = collections.Counter(); n = 0; pos = 0; k = 0
    for name in rows:
        test = rows[name]; train = [r for kk, v in rows.items() if kk != name for r in v]
        if not test:
            continue
        b = {key: code(train, test, key, beta, fixed_alpha) for key in ("geom", "localrel", "func")}
        for key in b:
            tot[key] += b[key]
        n += len(test); k += 1; pos += 1 if b["localrel"] > b["func"] else 0
    return dict(n=n, geom=round(tot["geom"] / n, 4), localrel=round(tot["localrel"] / n, 4), func=round(tot["func"] / n, 4), residue=round((tot["localrel"] - tot["func"]) / n, 4), pos_share=round(pos / k, 3))


VARIANTS = {
    "base": dict(collapse=True, tfun=trans_root, label="func", nocur=False, beta=1.0, fixed=False),
    "rootfree": dict(collapse=True, tfun=trans_rootfree, label="func", nocur=False, beta=1.0, fixed=False),
    "nocollapse": dict(collapse=False, tfun=trans_root, label="func", nocur=False, beta=1.0, fixed=False),
    "fullroman": dict(collapse=True, tfun=trans_root, label="full", nocur=False, beta=1.0, fixed=False),
    "fixedalpha": dict(collapse=True, tfun=trans_root, label="func", nocur=False, beta=1.0, fixed=True),
    "target_nocur": dict(collapse=True, tfun=trans_root, label="func", nocur=True, beta=1.0, fixed=False),
    "beta0.25": dict(collapse=True, tfun=trans_root, label="func", nocur=False, beta=0.25, fixed=False),
    "beta4": dict(collapse=True, tfun=trans_root, label="func", nocur=False, beta=4.0, fixed=False),
    "rootfree+fixedalpha+fullroman": dict(collapse=True, tfun=trans_rootfree, label="full", nocur=False, beta=1.0, fixed=True),
    "nested": dict(collapse=True, tfun=trans_root, label="nested", nocur=False, beta=1.0, fixed=False),
    "nested+rootfree+fixedalpha": dict(collapse=True, tfun=trans_rootfree, label="nested", nocur=False, beta=1.0, fixed=True),
    "nested+clean": dict(collapse=True, tfun=trans_rootfree, label="nested", nocur=True, beta=1.0, fixed=True),
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="beethoven_piano_sonatas,ABC"); ap.add_argument("--m", default="1,2"); ap.add_argument("--only", default=""); a = ap.parse_args()
    out = {}
    for corpus in a.corpus.split(","):
        cache = {c: load(corpus, c) for c in (True, False)}
        for m in [int(x) for x in a.m.split(",")]:
            for name, v in VARIANTS.items():
                if a.only and name not in a.only.split(","):
                    continue
                r = evaluate(cache[v["collapse"]], m, v["tfun"], v["label"], v["nocur"], v["beta"], v["fixed"])
                out["%s|m=%d|%s" % (corpus, m, name)] = r
                print(corpus, "m=%d" % m, name.ljust(30), "residue", r["residue"], "pos", r["pos_share"], "geom/localrel/func", r["geom"], r["localrel"], r["func"], flush=True)
    (D / ("controls_r3_nested.json" if a.only else "controls_r3.json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
