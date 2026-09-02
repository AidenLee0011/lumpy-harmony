# -*- coding: utf-8 -*-
"""Deterministic first-pass statistics on the unified harmony caches (no LLM): key-relative chord vocab, transition
entropy, root-interval distributions, per-corpus. Output data/basic_stats.json (grounding numbers for sol rounds)."""
import json, math, collections
from pathlib import Path
D = Path(__file__).resolve().parent / "data"


def load(name):
    p = D / ("cache_%s.jsonl" % name)
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def rel(r):
    """key-relative chord token: (root - key_root) mod 12 + quality"""
    if r.get("root") is None or r.get("key_root") is None:
        return None
    return "%d:%s" % ((r["root"] - r["key_root"]) % 12, r.get("quality"))


def stats(recs, name):
    by_piece = collections.defaultdict(list)
    for r in recs:
        if r.get("idx", -1) >= 0:
            by_piece[r["piece"]].append(r)
    uni = collections.Counter(); big = collections.Counter(); ival = collections.Counter(); qual = collections.Counter()
    for p, rs in by_piece.items():
        toks = [rel(r) for r in rs]
        toks = [t for t in toks if t]
        uni.update(toks); big.update(zip(toks, toks[1:]))
        roots = [r["root"] for r in rs if r.get("root") is not None]
        ival.update(((b - a) % 12) for a, b in zip(roots, roots[1:]))
        qual.update(r.get("quality") for r in rs if r.get("quality"))
    n = sum(uni.values())
    H1 = -sum(c / n * math.log2(c / n) for c in uni.values()) if n else 0
    # conditional entropy H(next | current)
    cur_tot = collections.Counter(); H2 = 0.0; m = sum(big.values())
    for (a, b), c in big.items():
        cur_tot[a] += c
    for (a, b), c in big.items():
        H2 -= c / m * math.log2(c / cur_tot[a])
    top_ival = {str(k): round(v / max(1, sum(ival.values())), 4) for k, v in sorted(ival.items())}
    return dict(corpus=name, pieces=len(by_piece), events=n, vocab=len(uni), H_unigram_bits=round(H1, 3), H_cond_bits=round(H2, 3),
                top_tokens=uni.most_common(15), root_interval_dist=top_ival, qualities=qual.most_common(12),
                mode_share={k: v for k, v in collections.Counter(r.get("key_mode") for r in recs).items()})


if __name__ == "__main__":
    out = {}
    for name in ("dcml", "wjazzd", "bach"):
        recs = load(name)
        if recs:
            out[name] = stats(recs, name)
            s = out[name]; print(name, "pieces", s["pieces"], "events", s["events"], "vocab", s["vocab"], "H1", s["H_unigram_bits"], "H(next|cur)", s["H_cond_bits"])
            print("   top", s["top_tokens"][:8]); print("   root ivals", s["root_interval_dist"])
    (D / "basic_stats.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
