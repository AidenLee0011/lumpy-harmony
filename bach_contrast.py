# -*- coding: utf-8 -*-
"""Paper 9 third classical contrast: music21 Bach chorales (430), labels = music21 romanNumeralFromChord (machine analysis, not human).
Same coder as pilot_residue: geom vs keyrel (= local key here, one key per chorale) vs func (Roman figure|mode|quality). LOMO, back-off beta=1.
  python -X utf8 bach_contrast.py --m 1,2
"""
import argparse, collections, json, sys
from pathlib import Path
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
from pilot_residue import backoff_bits, transition  # noqa: E402

QT = {"major": (0, 4, 7), "minor": (0, 3, 7), "diminished": (0, 3, 6), "augmented": (0, 4, 8)}


def load():
    recs = [json.loads(l) for l in (D / "cache_bach.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    by = collections.defaultdict(list)
    for r in recs:
        if r.get("idx", -1) < 0 or r.get("root") is None or r.get("key_root") is None:
            continue
        q = r.get("quality"); pcs = tuple(sorted((r["root"] + t) % 12 for t in QT.get(q, (0, 4, 7))))
        e = dict(pcs=pcs, root=r["root"], keyrel="%d|%s|%s" % ((r["root"] - r["key_root"]) % 12, q, r["key_mode"]), func="%s|%s|%s" % (str(r.get("raw")).split("/")[0], r["key_mode"], q))
        if by[r["piece"]] and by[r["piece"]][-1]["pcs"] == pcs:
            continue
        by[r["piece"]].append(e)
    return {k: v for k, v in by.items() if len(v) >= 8}


def seqs(mov, m):
    trans = [transition(mov[i], mov[i + 1]) for i in range(len(mov) - 1)]
    return [(tuple(trans[t - m:t]), (tuple(trans[t - m:t]), mov[t]["keyrel"]), (tuple(trans[t - m:t]), mov[t]["func"]), trans[t]) for t in range(m, len(trans))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--m", default="1,2"); a = ap.parse_args()
    movs = load(); out = {"chorales": len(movs)}
    for m in [int(x) for x in a.m.split(",")]:
        rows = {k: seqs(v, m) for k, v in movs.items()}; tot = collections.Counter(); n = 0; pos = 0; k = 0
        for name in rows:
            test = rows[name]; train = [r for kk, v in rows.items() if kk != name for r in v]
            if not test:
                continue
            b = {"geom": backoff_bits(train, test, 0), "keyrel": backoff_bits(train, test, 1), "func": backoff_bits(train, test, 2)}
            for key in b:
                tot[key] += b[key]
            n += len(test); k += 1; pos += 1 if b["keyrel"] > b["func"] else 0
        out["m=%d" % m] = dict(n=n, bits_per_chord={key: round(v / n, 4) for key, v in tot.items()}, residue_func_vs_keyrel=round((tot["keyrel"] - tot["func"]) / n, 4), gain_keyrel_vs_geom=round((tot["geom"] - tot["keyrel"]) / n, 4), pos_share=round(pos / k, 3))
        print("m=%d" % m, out["m=%d" % m], flush=True)
    (D / "bach_contrast.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
