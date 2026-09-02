# -*- coding: utf-8 -*-
"""Paper 9 candidate 3 pilot (sol P72_p9_r1 §3 day 2): functional residue of voice leading, deterministic, zero LLM.

Representations per chord event t (DCML corpora: ABC, Mozart, Beethoven sonatas):
  pcs_t   : pitch-class set of the chord (from chord_tones in fifths relative to local key -> absolute pcs)
  geom O_m: transposition-invariant local voice-leading orbit of the last m transitions =
            tuple over the last m steps of (interval class profile of the transition) where a transition is canonicalised as
            (normalised prev pcs with prev root -> 0, root interval to next mod 12, normalised next pcs, minimal voice-leading cost)
  keyrel  : geometry + global-key-relative pitch content (root scale degree in the *global* key, mode), no Roman syntax
  func    : geometry + Roman-numeral function F_t (numeral + local key mode), i.e. the DCML label content
Target Y_t = next transition orbit (m = 1 canonical transition). Coder = Krichevsky-Trofimov / add-1/2 sequential (prequential) code,
context counts from the other movements (leave-one-movement-out). Reports bits per eligible chord per representation and m.
  python -X utf8 pilot_residue.py [--corpus ABC,mozart_piano_sonatas] [--m 1,2,3,4] [--pilot 10]
"""
from __future__ import annotations
import argparse, collections, itertools, json, math, sys
from pathlib import Path
import pandas as pd
H = Path(__file__).resolve().parent
D = H / "data"
sys.path.insert(0, str(H))
from corpora import _dcml_key, _roman_to_pc  # noqa: E402


def fifths_to_pc(x):
    return (7 * int(float(x))) % 12


def load_movements(corpus, limit=None):
    files = sorted((D / corpus / "harmonies").glob("*.tsv"))
    if limit:
        files = files[:limit]
    movs = []
    for f in files:
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
            # function label: numeral + local-key mode + chord_type (Roman syntax content, no absolute pitch)
            func = "%s|%s|%s" % (numeral, lmode, r.get("chord_type"))
            # key-relative pitch content without Roman syntax: root scale degree in GLOBAL key + chord type + global mode
            keyrel = "%d|%s|%s" % ((root - gk) % 12, r.get("chord_type"), gmode)
            # local-key-relative pitch content (scale degree in the LOCAL key + chord type + local mode), still no Roman syntax
            localrel = "%d|%s|%s" % ((root - lk_pc) % 12, r.get("chord_type"), lmode)
            ev.append(dict(pcs=tones, root=root, func=func, keyrel=keyrel, localrel=localrel))
        # collapse repeated identical chords (same pcs) to chord changes
        coll = []
        for e in ev:
            if coll and coll[-1]["pcs"] == e["pcs"]:
                continue
            coll.append(e)
        if len(coll) >= 8:
            movs.append((corpus + "/" + f.stem.replace(".harmonies", ""), coll))
    return movs


def vl_cost(a, b):
    """minimal total pitch-class displacement between two pc sets (unequal sizes allowed: min over injections of the smaller)"""
    a, b = list(a), list(b)
    if len(a) > len(b):
        a, b = b, a
    best = None
    for perm in itertools.permutations(b, len(a)):
        c = sum(min((y - x) % 12, (x - y) % 12) for x, y in zip(a, perm))
        best = c if best is None else min(best, c)
    return best or 0


def transition(prev, cur):
    """transposition-invariant canonical transition: normalise prev root to 0"""
    r = prev["root"]
    p = tuple(sorted((x - r) % 12 for x in prev["pcs"])); c = tuple(sorted((x - r) % 12 for x in cur["pcs"]))
    return (p, (cur["root"] - r) % 12, c, vl_cost(prev["pcs"], cur["pcs"]))


def sequences(mov, m):
    """yield (context_geom, context_keyrel, context_func, Y) for each eligible t (needs m prior transitions and one next)"""
    ev = mov
    trans = [transition(ev[i], ev[i + 1]) for i in range(len(ev) - 1)]      # trans[i] = ev[i] -> ev[i+1]
    out = []
    for t in range(m, len(trans)):                                          # predict trans[t] from trans[t-m..t-1] (+ labels of ev[t])
        geom = tuple(trans[t - m:t])
        out.append((geom, (geom, ev[t]["keyrel"]), (geom, ev[t]["func"]), trans[t], (geom, ev[t]["localrel"])))
    return out


def backoff_bits(train_rows, test_rows, ctx_index, beta=1.0):
    """hierarchical smoothing: p(y | geom+label) = (c_fl[y] + beta * p_kt(y | geom)) / (n_fl + beta); label-augmented contexts
    back off to the geometry-only KT predictor, so extra labels can never cost more than the escape mass (fair comparison)."""
    alphabet = {r[3] for r in train_rows} | {r[3] for r in test_rows}
    K = len(alphabet)
    cg = collections.defaultdict(collections.Counter); cf = collections.defaultdict(collections.Counter)
    for r in train_rows:
        cg[r[0]][r[3]] += 1; cf[r[ctx_index]][r[3]] += 1
    bits = 0.0
    for r in test_rows:
        g = cg[r[0]]; ng = sum(g.values()); pg = (g[r[3]] + 0.5) / (ng + 0.5 * K)
        if ctx_index == 0:
            p = pg
        else:
            fl = cf[r[ctx_index]]; nf = sum(fl.values()); p = (fl[r[3]] + beta * pg) / (nf + beta)
        bits += -math.log2(p)
        g[r[3]] += 1; cf[r[ctx_index]][r[3]] += 1
    return bits


def kt_bits(train_rows, test_rows, ctx_index):
    """add-1/2 (KT) code length in bits of test Y given context counts from train; alphabet = all Y seen in train+test."""
    alphabet = {r[3] for r in train_rows} | {r[3] for r in test_rows}
    K = len(alphabet)
    counts = collections.defaultdict(collections.Counter)
    for r in train_rows:
        counts[r[ctx_index]][r[3]] += 1
    bits = 0.0
    for r in test_rows:
        c = counts[r[ctx_index]]; n = sum(c.values())
        p = (c[r[3]] + 0.5) / (n + 0.5 * K)
        bits += -math.log2(p)
        c[r[3]] += 1          # prequential update on the held-out movement itself
    return bits


BACKOFF = True


def run(corpora, ms, pilot):
    res = {}
    for corpus in corpora:
        movs = load_movements(corpus, pilot)
        res[corpus] = {"movements": len(movs), "chords": sum(len(m) for _, m in movs)}
        for m in ms:
            rows = {name: sequences(mov, m) for name, mov in movs}
            tot = {"geom": 0.0, "keyrel": 0.0, "func": 0.0, "localrel": 0.0}; n = 0; per_mov = []
            for name in rows:
                test = rows[name]; train = [r for k, v in rows.items() if k != name for r in v]
                if not test:
                    continue
                coder = backoff_bits if BACKOFF else kt_bits
                b = {"geom": coder(train, test, 0), "keyrel": coder(train, test, 1), "func": coder(train, test, 2), "localrel": coder(train, test, 4)}
                for k in tot:
                    tot[k] += b[k]
                n += len(test)
                per_mov.append(dict(mov=name, n=len(test), gain_func_vs_keyrel=(b["keyrel"] - b["func"]) / len(test), gain_func_vs_geom=(b["geom"] - b["func"]) / len(test), gain_func_vs_localrel=(b["localrel"] - b["func"]) / len(test)))
            gains = [x["gain_func_vs_localrel"] for x in per_mov]
            res[corpus]["m=%d" % m] = dict(n_eligible=n, bits_per_chord={k: round(v / n, 4) for k, v in tot.items()},
                                          gain_func_vs_keyrel=round((tot["keyrel"] - tot["func"]) / n, 4), gain_func_vs_geom=round((tot["geom"] - tot["func"]) / n, 4), gain_func_vs_localrel=round((tot["localrel"] - tot["func"]) / n, 4),
                                          share_movements_positive=round(sum(1 for g in gains if g > 0) / len(gains), 3), per_movement=per_mov)
            print(corpus, "m=%d" % m, "n", n, res[corpus]["m=%d" % m]["bits_per_chord"], "gain func-vs-localrel", res[corpus]["m=%d" % m]["gain_func_vs_localrel"], "pos share(localrel)", res[corpus]["m=%d" % m]["share_movements_positive"], flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="ABC,mozart_piano_sonatas"); ap.add_argument("--m", default="1,2,3,4"); ap.add_argument("--pilot", type=int, default=10); ap.add_argument("--kt", action="store_true", help="plain KT without back-off")
    a = ap.parse_args()
    if a.kt:
        BACKOFF = False
    res = run(a.corpus.split(","), [int(x) for x in a.m.split(",")], a.pilot or None)
    (D / ("pilot_residue_%s%s.json" % ("pilot%d" % a.pilot if a.pilot else "full", "_kt" if a.kt else "_backoff"))).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
