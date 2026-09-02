# -*- coding: utf-8 -*-
"""Paper 9: jazz contrast on WJazzD (chord symbols, no Roman labels). Same coder; contexts geom (transposition-invariant transition
orbits built from quality templates) vs keyrel (root scale degree in the solo's key + quality). Per-style breakdown.
  python -X utf8 jazz_contrast.py --m 1,2
"""
import argparse, collections, json, sys
from pathlib import Path
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
from pilot_residue import backoff_bits, transition  # noqa: E402

TEMPL = {"maj": (0, 4, 7), "maj7": (0, 4, 7, 11), "maj6": (0, 4, 7, 9), "min": (0, 3, 7), "min7": (0, 3, 7, 10), "min6": (0, 3, 7, 9), "dom7": (0, 4, 7, 10), "dom7alt": (0, 4, 8, 10),
         "hdim7": (0, 3, 6, 10), "dim7": (0, 3, 6, 9), "dim": (0, 3, 6), "aug": (0, 4, 8), "sus": (0, 5, 7, 10)}


def load():
    recs = [json.loads(l) for l in (D / "cache_wjazzd.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    by = collections.defaultdict(list)
    for r in recs:
        if r.get("root") is None or r.get("quality") not in TEMPL or r.get("key_root") is None:
            continue
        pcs = tuple(sorted((r["root"] + t) % 12 for t in TEMPL[r["quality"]]))
        by[r["piece"]].append(dict(pcs=pcs, root=r["root"], keyrel="%d|%s|%s" % ((r["root"] - r["key_root"]) % 12, r["quality"], r["key_mode"]), style=r.get("style")))
    return {k: v for k, v in by.items() if len(v) >= 8}


def seqs(mov, m):
    trans = [transition(mov[i], mov[i + 1]) for i in range(len(mov) - 1)]
    return [((tuple(trans[t - m:t])), (tuple(trans[t - m:t]), mov[t]["keyrel"]), None, trans[t]) for t in range(m, len(trans))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--m", default="1,2"); a = ap.parse_args()
    movs = load(); out = {"solos": len(movs)}
    for m in [int(x) for x in a.m.split(",")]:
        rows = {k: seqs(v, m) for k, v in movs.items()}; style = {k: v[0]["style"] for k, v in movs.items()}
        tot = collections.defaultdict(float); n = 0; per_style = collections.defaultdict(lambda: [0.0, 0.0, 0])
        for name in rows:
            test = rows[name]; train = [r for k, v in rows.items() if k != name for r in v]
            if not test:
                continue
            bg = backoff_bits(train, test, 0); bk = backoff_bits(train, test, 1)
            tot["geom"] += bg; tot["keyrel"] += bk; n += len(test)
            ps = per_style[style[name]]; ps[0] += bg; ps[1] += bk; ps[2] += len(test)
        out["m=%d" % m] = dict(n=n, geom=round(tot["geom"] / n, 4), keyrel=round(tot["keyrel"] / n, 4), gain_keyrel=round((tot["geom"] - tot["keyrel"]) / n, 4),
                               per_style={s: dict(n=v[2], geom=round(v[0] / v[2], 4), keyrel=round(v[1] / v[2], 4), gain=round((v[0] - v[1]) / v[2], 4)) for s, v in per_style.items() if v[2] > 200})
        print("m=%d" % m, out["m=%d" % m]["n"], "geom", out["m=%d" % m]["geom"], "keyrel", out["m=%d" % m]["keyrel"], "gain", out["m=%d" % m]["gain_keyrel"], flush=True)
        for s, v in out["m=%d" % m]["per_style"].items():
            print("   ", s, v)
    (D / "jazz_contrast.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
