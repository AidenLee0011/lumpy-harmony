# -*- coding: utf-8 -*-
"""Paper 9: cross-corpus transfer of the residue. Train contexts on one corpus, code another (no leave-one-out inside the test corpus,
prequential updates still applied on the test stream). Reports bits per chord for geom / keyrel / localrel / func and the residues.
  python -X utf8 transfer.py --m 1,2
"""
import argparse, json, sys
from pathlib import Path
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
import pilot_residue as P  # noqa: E402

CORP = ["ABC", "mozart_piano_sonatas", "beethoven_piano_sonatas"]


def rows(corpus, m):
    return [r for _, mov in P.load_movements(corpus, None) for r in P.sequences(mov, m)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--m", default="1,2"); a = ap.parse_args()
    out = {}
    cache = {}
    for m in [int(x) for x in a.m.split(",")]:
        for c in CORP:
            cache[(c, m)] = rows(c, m)
        for tr in CORP:
            for te in CORP:
                if tr == te:
                    continue
                train, test = cache[(tr, m)], cache[(te, m)]
                b = {"geom": P.backoff_bits(train, test, 0), "keyrel": P.backoff_bits(train, test, 1), "func": P.backoff_bits(train, test, 2), "localrel": P.backoff_bits(train, test, 4)}
                n = len(test); r = {k: round(v / n, 4) for k, v in b.items()}
                r["residue_func_vs_localrel"] = round((b["localrel"] - b["func"]) / n, 4); r["gain_localrel_vs_keyrel"] = round((b["keyrel"] - b["localrel"]) / n, 4); r["n"] = n
                out["%s->%s m=%d" % (tr, te, m)] = r
                print("%s->%s m=%d" % (tr, te, m), r, flush=True)
    (D / "transfer.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
