# -*- coding: utf-8 -*-
"""Paper 9 round-4 confirmatory repair (sol P72_p9_r3 §2): 32-node feature lattice over Z = (chromatic local degree, chord type, local mode)
with an MDL-charged, work-grouped 5-fold held-out selection. Deterministic, zero LLM.

Feature blocks parsed from the DCML label (preregistered encodings):
  S spelled degree  = diatonic numeral head (1..7) + signed alteration (-2..2), case/applied/inversion stripped
  C case            = UPPER / lower / OTHER
  M mixture         = DIATONIC if the spelled degree+alteration is diatonic in the local mode (major or natural minor with raised 7 for V/vii in minor) else ALTERED
  A applied         = NONE / one-level applied with denominator head (d,a) / deeper -> OTHER
  I inversion       = ROOT/FIRST/SECOND/THIRD from figbass ('', '6' or '65' -> FIRST, '64' or '43' -> SECOND, '2' or '42' -> THIRD, else UNKNOWN)
Targets: 'clean' = root-free geometry + fixed training alphabet + no-current-shape target (root displacement + vl cost); 'base' = pilot target.
Protocol: works = movement file stem prefix (e.g. K279, op.18 no.1); folds = SHA256 of work id, round robin 5; per outer fold: score all 32 subsets on
training movements (prequential, fixed movement order), description cost D(B)=3+ceil(log2 C(5,r)); select argmin D+L; refit on training, score held-out
movements independently (reset to training counts per movement); aggregate; recovery rho = G_repair / G_ref where G_ref = L(Z)-L(F_sel).
  python -X utf8 repair_lattice.py --corpus beethoven_piano_sonatas --m 1,2 [--target clean|base]
"""
from __future__ import annotations
import argparse, collections, hashlib, itertools, json, math, re, sys
from pathlib import Path
import pandas as pd
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
from corpora import _dcml_key, _roman_to_pc  # noqa: E402
from pilot_residue import fifths_to_pc, vl_cost  # noqa: E402
from controls_r3 import trans_rootfree, trans_root  # noqa: E402

FEATS = ["S", "C", "M", "A", "I"]
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7}
DIATONIC_MAJ = {(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)}
DIATONIC_MIN = {(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (7, 1)}   # raised leading tone allowed


def parse_head(numeral):
    m = re.match(r"([#b]*)([ivIV]+)", numeral or "")
    if not m:
        return None
    acc, deg = m.groups()
    d = ROMAN.get(deg.lower())
    if d is None:
        return None
    a = sum(1 if c == "#" else -1 for c in acc)
    a = max(-2, min(2, a))
    case = "UPPER" if deg.isupper() else ("lower" if deg.islower() else "OTHER")
    return d, a, case


def features(r, lmode):
    numeral = str(r.get("numeral")); rr = r.get("relativeroot"); fb = str(r.get("figbass")) if str(r.get("figbass")) not in ("nan", "None") else ""
    h = parse_head(numeral)
    if h is None:
        return None
    d, a, case = h
    S = "%d%+d" % (d, a); C = case
    dia = DIATONIC_MIN if lmode == "m" else DIATONIC_MAJ
    M = "DIATONIC" if (d, a) in dia else "ALTERED"
    if isinstance(rr, str) and rr not in ("", "nan"):
        parts = rr.split("/")
        hh = parse_head(parts[0])
        A = ("APP:%d%+d" % (hh[0], hh[1])) if (hh and len(parts) == 1) else "OTHER"
    else:
        A = "NONE"
    I = {"": "ROOT", "7": "ROOT", "6": "FIRST", "65": "FIRST", "64": "SECOND", "43": "SECOND", "2": "THIRD", "42": "THIRD"}.get(fb, "UNKNOWN")
    return {"S": S, "C": C, "M": M, "A": A, "I": I}


def load(corpus):
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
            fe = features(r, lmode)
            if fe is None:
                continue
            Z = "%d|%s|%s" % ((root - lk_pc) % 12, r.get("chord_type"), lmode)
            Fsel = "%s|%s|%s" % (numeral, lmode, r.get("chord_type"))
            ev.append(dict(pcs=tones, root=root, Z=Z, Fsel=Fsel, fe=fe))
        coll = []
        for e in ev:
            if coll and coll[-1]["pcs"] == e["pcs"]:
                continue
            coll.append(e)
        if len(coll) >= 8:
            stem = f.stem.replace(".harmonies", "")
            work = re.split(r"[-_]", stem)[0] if corpus != "ABC" else re.sub(r"_?\d+$", "", stem.rsplit("_", 1)[0]) if "_" in stem else stem[:6]
            movs.append((stem, work, coll))
    return movs


def build(mov, m, target):
    tf = trans_rootfree if target == "clean" else trans_root
    trans = [tf(mov[i], mov[i + 1]) for i in range(len(mov) - 1)]
    if target == "clean":   # no current-shape: (next pcs relative shift is dropped) -> keep (shift of lowest pc, vl cost)
        tgt = [(t[1][0] if t[1] else None, t[2]) for t in trans]  # first element of next normalised pcs (its lowest pc) + cost
    else:
        tgt = trans
    rows = []
    for t in range(m, len(trans)):
        geom = tuple(trans[t - m:t]); e = mov[t]
        rows.append((geom, e["Z"], e["Fsel"], e["fe"], tgt[t]))
    return rows


def ctx_key(row, mask):
    geom, Z, Fsel, fe, _ = row
    if mask == "Z":
        return (geom, Z)
    if mask == "Fsel":
        return (geom, Fsel)
    return (geom, Z) + tuple(fe[f] for f in FEATS if f in mask)


def code(train, test, mask, alphabet, beta=1.0, reset_per_movement=None):
    """back-off to geometry; alphabet fixed from training (+UNK). If reset_per_movement is a list of test movements, each is scored from the same training counts."""
    K = len(alphabet) + 1
    def sym(y): return y if y in alphabet else "UNK"
    cg0 = collections.defaultdict(collections.Counter); cf0 = collections.defaultdict(collections.Counter)
    for r in train:
        cg0[r[0]][sym(r[4])] += 1; cf0[ctx_key(r, mask)][sym(r[4])] += 1
    def score(rows):
        cg = collections.defaultdict(collections.Counter, {k: v.copy() for k, v in cg0.items()}); cf = collections.defaultdict(collections.Counter, {k: v.copy() for k, v in cf0.items()})
        bits = 0.0
        for r in rows:
            y = sym(r[4]); g = cg[r[0]]; ng = sum(g.values()); pg = (g[y] + 0.5) / (ng + 0.5 * K)
            if mask == "geom":
                p = pg
            else:
                c = cf[ctx_key(r, mask)]; p = (c[y] + beta * pg) / (sum(c.values()) + beta)
            bits += -math.log2(p); g[y] += 1; cf[ctx_key(r, mask)][y] += 1
        return bits
    if reset_per_movement is None:
        return score(test)
    return sum(score(mv) for mv in reset_per_movement)


def D_bits(mask):
    r = len(mask); return 3 + math.ceil(math.log2(math.comb(5, r))) if r not in (0, 5) else 3


def run(corpus, m, target, control_corpus=None):
    movs = load(corpus)
    folds = collections.defaultdict(list)
    works = sorted({w for _, w, _ in movs}, key=lambda w: hashlib.sha256(w.encode()).hexdigest())
    fold_of = {w: i % 5 for i, w in enumerate(works)}
    rows_by_mov = {stem: build(mv, m, target) for stem, w, mv in movs}
    mov_fold = {stem: fold_of[w] for stem, w, mv in movs}
    masks = ["".join(c) for r in range(0, 6) for c in itertools.combinations(FEATS, r)]
    res = {"corpus": corpus, "m": m, "target": target, "works": len(works), "movements": len(movs), "folds": {}}
    tot = collections.Counter(); N = 0; selected = []
    for k in range(5):
        train_m = [s for s in rows_by_mov if mov_fold[s] != k]; held = [s for s in rows_by_mov if mov_fold[s] == k]
        train = [r for s in train_m for r in rows_by_mov[s]]
        alphabet = {r[4] for r in train}
        # inner selection: prequential score on training movements in fixed SHA order, no held-out access
        order = sorted(train_m, key=lambda s: hashlib.sha256(s.encode()).hexdigest())
        train_ordered = [r for s in order for r in rows_by_mov[s]]
        scores = {}
        for mask in masks:
            # training code: code training stream itself prequentially from empty counts
            scores[mask] = D_bits(mask) + code([], train_ordered, mask, alphabet)
        best = min(masks, key=lambda mk: (scores[mk], len(mk), D_bits(mk), mk))
        selected.append(best)
        held_rows = [rows_by_mov[s] for s in held]
        L = {"Z": code(train, None, "Z", alphabet, reset_per_movement=held_rows), "Fsel": code(train, None, "Fsel", alphabet, reset_per_movement=held_rows),
             "repair": code(train, None, best, alphabet, reset_per_movement=held_rows), "geom": code(train, None, "geom", alphabet, reset_per_movement=held_rows),
             "all5": code(train, None, "SCMAI", alphabet, reset_per_movement=held_rows)}
        n = sum(len(r) for r in held_rows); N += n
        for key in L:
            tot[key] += L[key]
        tot["D"] += D_bits(best)
        res["folds"][k] = dict(selected=best, n=n, held_bits_per_chord={key: round(v / n, 4) for key, v in L.items()}, train_scores_top5=sorted(((round(v, 1), mk) for mk, v in scores.items()))[:5])
        print(corpus, "m=%d" % m, target, "fold", k, "selected", best or "(Z only)", {key: round(v / n, 4) for key, v in L.items()}, flush=True)
    G_ref = (tot["Z"] - tot["Fsel"]) / N; G_rep = (tot["Z"] - tot["repair"] - tot["D"]) / N
    res["summary"] = dict(N=N, bits_per_chord={key: round(tot[key] / N, 4) for key in ("geom", "Z", "Fsel", "repair", "all5")}, G_ref=round(G_ref, 4), G_repair_net=round(G_rep, 4),
                          recovery_rho=round(G_rep / G_ref, 3) if G_ref else None, selected_masks=selected, stable_4of5=max(collections.Counter(selected).values()) >= 4)
    print("SUMMARY", corpus, "m=%d" % m, target, res["summary"], flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="beethoven_piano_sonatas,ABC"); ap.add_argument("--m", default="1,2"); ap.add_argument("--target", default="clean,base")
    a = ap.parse_args(); out = []
    for corpus in a.corpus.split(","):
        for m in [int(x) for x in a.m.split(",")]:
            for tgt in a.target.split(","):
                out.append(run(corpus, m, tgt))
    (D / "repair_lattice.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
