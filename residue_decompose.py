# -*- coding: utf-8 -*-
"""Paper 9: decompose the Roman-numeral residue beyond local-key content into label features, and test it with an e-process.

Contexts (all = geom O_m + local-key scale degree + chord type + local mode, i.e. 'localrel') plus ONE extra DCML label feature:
  +relativeroot (applied-chord target, e.g. V/V), +form (chord form: o, %, +, M...), +figbass (inversion), +changes (added/altered tones),
  +numeral_case (upper/lower numeral, i.e. chord mode as written), +cadence (cadence label at this chord), +phraseend, and 'func' (full label).
Coder = same back-off prequential coder as pilot_residue.py. Also: movement-level gain e-process against H0: E[gain_i] <= tau (tau = 0.05 bits),
bounded gains clipped to [-b, b], E_n = exp(lambda * sum(d_i - tau) - lambda^2 n b^2 / 2).
  python -X utf8 residue_decompose.py --corpus ABC,mozart_piano_sonatas,beethoven_piano_sonatas --m 1,2
"""
from __future__ import annotations
import argparse, collections, json, math, sys
from pathlib import Path
import pandas as pd
H = Path(__file__).resolve().parent
D = H / "data"
sys.path.insert(0, str(H))
from corpora import _dcml_key, _roman_to_pc  # noqa: E402
from pilot_residue import fifths_to_pc, transition  # noqa: E402

FEATS = ["relativeroot", "form", "figbass", "changes", "numeral_case", "cadence", "phraseend", "applied_flag", "spelled", "spelled+applied", "spelled+relativeroot"]


def load_movements(corpus):
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
            feats = {"relativeroot": str(r.get("relativeroot")), "form": str(r.get("form")), "figbass": str(r.get("figbass")), "changes": str(r.get("changes")),
                     "numeral_case": "U" if numeral[:1].isupper() else "l", "cadence": str(r.get("cadence")), "phraseend": str(r.get("phraseend")),
                     "applied_flag": "A" if isinstance(r.get("relativeroot"), str) and r.get("relativeroot") not in ("", "nan") else "-",
                     "spelled": numeral, "spelled+applied": numeral + ("/A" if isinstance(r.get("relativeroot"), str) and r.get("relativeroot") not in ("", "nan") else ""),
                     "spelled+relativeroot": numeral + "/" + str(r.get("relativeroot"))}
            func = "%s|%s|%s" % (numeral, lmode, r.get("chord_type"))
            applied = isinstance(r.get("relativeroot"), str) and r.get("relativeroot") not in ("", "nan")
            # same arity as localrel: chromatic degree, except applied chords are relabelled by their functional degree (numeral) in the applied key
            relabel = "%s|%s|%s" % ((numeral if applied else str((root - lk_pc) % 12)), r.get("chord_type"), lmode)
            # spelled degree only (numeral string) + type + mode: same arity, no relativeroot info
            spelled3 = "%s|%s|%s" % (numeral, r.get("chord_type"), lmode)
            ev.append(dict(pcs=tones, root=root, base=base, func=func, feats=feats, relabel=relabel, spelled3=spelled3))
        coll = []
        for e in ev:
            if coll and coll[-1]["pcs"] == e["pcs"]:
                continue
            coll.append(e)
        if len(coll) >= 8:
            movs.append((corpus + "/" + f.stem.replace(".harmonies", ""), coll))
    return movs


def rows_for(mov, m):
    trans = [transition(mov[i], mov[i + 1]) for i in range(len(mov) - 1)]
    out = []
    for t in range(m, len(trans)):
        geom = tuple(trans[t - m:t]); e = mov[t]
        ctx = {"geom": geom, "localrel": (geom, e["base"]), "func": (geom, e["func"]), "relabel3": (geom, e["relabel"]), "spelled3": (geom, e["spelled3"])}
        for f in FEATS:
            ctx["+" + f] = (geom, e["base"], e["feats"][f])
        out.append((ctx, trans[t]))
    return out


def backoff_bits(train, test, key, beta=1.0):
    alphabet = {y for _, y in train} | {y for _, y in test}; K = len(alphabet)
    cg = collections.defaultdict(collections.Counter); cf = collections.defaultdict(collections.Counter)
    for ctx, y in train:
        cg[ctx["geom"]][y] += 1; cf[ctx[key]][y] += 1
    bits = 0.0
    for ctx, y in test:
        g = cg[ctx["geom"]]; ng = sum(g.values()); pg = (g[y] + 0.5) / (ng + 0.5 * K)
        if key == "geom":
            p = pg
        else:
            fl = cf[ctx[key]]; nf = sum(fl.values()); p = (fl[y] + beta * pg) / (nf + beta)
        bits += -math.log2(p); g[y] += 1; cf[ctx[key]][y] += 1
    return bits


def eprocess(gains, tau=0.05, b=0.5, lam=None):
    """test supermartingale for H0: E[d_i] <= tau with |d_i| <= b (clipped); fixed lambda = 1/(2b) unless given"""
    lam = lam or 1.0 / (2 * b)
    s = 0.0; n = 0; E = []
    for d in gains:
        d = max(-b, min(b, d)); n += 1; s += (d - tau)
        E.append(math.exp(lam * s - lam * lam * n * b * b / 2))
    return E


def run(corpora, ms):
    res = {}
    for corpus in corpora:
        movs = load_movements(corpus); res[corpus] = {"movements": len(movs)}
        for m in ms:
            rows = {name: rows_for(mov, m) for name, mov in movs}
            keys = ["geom", "localrel", "func", "relabel3", "spelled3"] + ["+" + f for f in FEATS]
            tot = {k: 0.0 for k in keys}; n = 0; gains_func = []
            for name in rows:
                test = rows[name]; train = [r for k, v in rows.items() if k != name for r in v]
                if not test:
                    continue
                b = {k: backoff_bits(train, test, k) for k in keys}
                for k in keys:
                    tot[k] += b[k]
                n += len(test); gains_func.append((b["localrel"] - b["func"]) / len(test))
            bpc = {k: round(v / n, 4) for k, v in tot.items()}
            E = eprocess(gains_func); Emax = max(E)
            res[corpus]["m=%d" % m] = dict(n=n, bits_per_chord=bpc,
                                          residue_by_feature={k: round(bpc["localrel"] - bpc[k], 4) for k in keys if k.startswith("+") or k in ("relabel3", "spelled3")},
                                          residue_full_func=round(bpc["localrel"] - bpc["func"], 4),
                                          eprocess_tau005={"E_final": round(E[-1], 3), "E_max": round(Emax, 3), "n_movements": len(E), "reject_at_20": Emax >= 20},
                                          eprocess_tau0={"E_final": round(eprocess(gains_func, tau=0.0)[-1], 3), "E_max": round(max(eprocess(gains_func, tau=0.0)), 3)})
            print(corpus, "m=%d" % m, "residue full", res[corpus]["m=%d" % m]["residue_full_func"], "by feature", res[corpus]["m=%d" % m]["residue_by_feature"],
                  "E(tau=.05) max", round(Emax, 2), "E(tau=0) max", res[corpus]["m=%d" % m]["eprocess_tau0"]["E_max"], flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="ABC,mozart_piano_sonatas,beethoven_piano_sonatas"); ap.add_argument("--m", default="1,2")
    a = ap.parse_args()
    res = run(a.corpus.split(","), [int(x) for x in a.m.split(",")])
    (D / "residue_decompose.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
