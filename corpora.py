# -*- coding: utf-8 -*-
"""Paper 9/10 (harmony) unified corpus loaders. Deterministic, no LLM.

Common record per chord event: dict(piece, idx, root (pc 0-11 or None), quality (str), bass (pc or None), key_root, key_mode, dur, raw)
Sources:
  dcml(): DCML harmonies TSV (mozart_piano_sonatas, beethoven_piano_sonatas, ABC)  -> Roman numerals resolved to absolute roots via localkey + relativeroot ignored (root column already given in scale degrees of local key)
  wjazzd(): Weimar Jazz Database beats.chord symbols (e.g. 'Bb7', 'C-7', 'Ebj7', 'F#o7', 'G7alt') per solo, key from solo_info
  bach(): music21 Bach chorales, chordified per beat, root/quality by music21 chord analysis (slow; cached)
  python -X utf8 corpora.py  -> summary counts + cache in data/cache_*.jsonl
"""
from __future__ import annotations
import glob, json, re, sqlite3, sys
from pathlib import Path
H = Path(__file__).resolve().parent
D = H / "data"
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pc(name):
    """'Bb' -> 10, 'F#' -> 6, 'Cb' -> 11"""
    if not name:
        return None
    m = re.match(r"([A-Ga-g])([#b]*)", name)
    if not m:
        return None
    v = NOTE[m.group(1).upper()]
    for a in m.group(2):
        v += 1 if a == "#" else -1
    return v % 12


# ---------------- DCML
def _dcml_key(k):
    if not isinstance(k, str) or not k:
        return None, None
    mode = "minor" if k[0].islower() else "major"
    return pc(k), mode


def dcml():
    import pandas as pd
    out = []
    for f in sorted(glob.glob(str(D / "*" / "harmonies" / "*.tsv"))):
        corpus = Path(f).parents[1].name
        df = pd.read_csv(f, sep="\t", low_memory=False)
        piece = corpus + "/" + Path(f).stem.replace(".harmonies", "")
        gk, gmode = _dcml_key(df["globalkey"].iloc[0] if "globalkey" in df else None)
        for i, r in df.iterrows():
            lk = r.get("localkey"); numeral = r.get("numeral"); root_sd = r.get("root"); ctype = r.get("chord_type")
            if not isinstance(numeral, str) or numeral in ("", "@none"):
                continue
            # localkey is a Roman numeral relative to globalkey; DCML also gives root as scale degree (semitones from local tonic)
            lk_pc = None
            if isinstance(lk, str) and gk is not None:
                lk_pc = _roman_to_pc(lk, gk, gmode)
            root = (lk_pc + 7 * int(float(root_sd))) % 12 if (lk_pc is not None and root_sd == root_sd and str(root_sd) not in ("", "nan")) else None  # DCML root = tonal pitch class in fifths from local tonic
            out.append(dict(piece=piece, idx=int(i), root=root, quality=str(ctype) if isinstance(ctype, str) else None, bass=None,
                            key_root=lk_pc, key_mode=("minor" if bool(r.get("localkey_is_minor")) else "major"), dur=float(r.get("duration_qb") or 0), raw=str(r.get("label"))))
    return out


_ROMAN = {"i": 0, "ii": 2, "iii": 4, "iv": 5, "v": 7, "vi": 9, "vii": 11}
_ROMAN_MIN = {"i": 0, "ii": 2, "iii": 3, "iv": 5, "v": 7, "vi": 8, "vii": 10}


def _roman_to_pc(rn, key_pc, key_mode):
    """Roman numeral (with #/b prefixes) relative to key -> absolute pc. Case = mode of the target chord, not used for pc."""
    m = re.match(r"([#b]*)([ivIV]+)", rn)
    if not m:
        return None
    acc, deg = m.groups()
    table = _ROMAN_MIN if key_mode == "minor" else _ROMAN
    v = table.get(deg.lower())
    if v is None:
        return None
    for a in acc:
        v += 1 if a == "#" else -1
    return (key_pc + v) % 12


# ---------------- WJazzD
_Q = [("-7b5", "hdim7"), ("o7", "dim7"), ("-6", "min6"), ("-7", "min7"), ("-", "min"), ("j7", "maj7"), ("6", "maj6"), ("7alt", "dom7alt"), ("7", "dom7"), ("+", "aug"), ("sus", "sus"), ("o", "dim"), ("", "maj")]


def parse_jazz(sym):
    """'Bb7' -> (10,'dom7'), 'C-7' -> (0,'min7'), 'Ebj7' -> (3,'maj7'), 'F#o7' -> (6,'dim7'), 'NC' -> (None,'NC')"""
    if not sym or sym == "NC":
        return None, "NC"
    m = re.match(r"([A-G][#b]?)(.*)", sym)
    if not m:
        return None, "unk"
    root = pc(m.group(1)); rest = m.group(2).split("/")[0]
    rest = re.sub(r"(9|11|13|b9|#9|#11|b13|#5|b5)+$", "", rest) if rest not in ("-7b5",) else rest
    for k, q in _Q:
        if rest.startswith(k) if k else True:
            return root, q
    return root, "unk"


def wjazzd():
    c = sqlite3.connect(str(D / "wjazzd.db"))
    solos = {r[0]: r for r in c.execute("select melid, title, performer, style, key from solo_info")}
    out = []
    for melid, onset, bar, beat, chord in c.execute("select melid, onset, bar, beat, chord from beats where chord is not null and chord!='' order by melid, onset"):
        root, q = parse_jazz(chord)
        s = solos.get(melid, (melid, "", "", "", ""))
        kr, km = (None, None)
        if s[4]:
            kk = s[4].split("-"); kr = pc(kk[0]); km = "minor" if len(kk) > 1 and kk[1].startswith("min") else "major"
        out.append(dict(piece="wjazzd/%d" % melid, idx=len(out), root=root, quality=q, bass=None, key_root=kr, key_mode=km, dur=1.0, raw=chord, style=s[3]))
    # collapse consecutive identical chords within a solo
    coll = []
    for r in out:
        if coll and coll[-1]["piece"] == r["piece"] and coll[-1]["raw"] == r["raw"]:
            coll[-1]["dur"] += 1.0
        else:
            coll.append(dict(r))
    return coll


# ---------------- Bach (music21)
def bach(limit=None):
    from music21 import corpus, key as m21key, roman
    out = []
    files = corpus.getComposer("bach")
    if limit:
        files = files[:limit]
    for f in files:
        try:
            s = corpus.parse(f)
            k = s.analyze("key")
            ch = s.chordify()
            for i, c in enumerate(ch.recurse().getElementsByClass("Chord")):
                rn = roman.romanNumeralFromChord(c, k)
                out.append(dict(piece="bach/" + Path(str(f)).stem, idx=i, root=c.root().pitchClass if c.root() else None,
                                quality=c.quality, bass=c.bass().pitchClass if c.bass() else None, key_root=k.tonic.pitchClass,
                                key_mode=k.mode, dur=float(c.quarterLength), raw=rn.figure))
        except Exception as e:
            out.append(dict(piece="bach/" + Path(str(f)).stem, idx=-1, error=str(e)[:80]))
    return out


def summary(recs, name):
    pieces = {r["piece"] for r in recs}
    roots = sum(1 for r in recs if r.get("root") is not None)
    print("%s: events %d, pieces %d, with root %d, qualities %s" % (name, len(recs), len(pieces), roots,
          sorted({r.get("quality") for r in recs if r.get("quality")})[:14]))


if __name__ == "__main__":
    d = dcml(); summary(d, "DCML")
    (D / "cache_dcml.jsonl").write_text("\n".join(json.dumps(r) for r in d), encoding="utf-8")
    w = wjazzd(); summary(w, "WJazzD")
    (D / "cache_wjazzd.jsonl").write_text("\n".join(json.dumps(r) for r in w), encoding="utf-8")
    if "--bach" in sys.argv:
        b = bach(); summary(b, "Bach")
        (D / "cache_bach.jsonl").write_text("\n".join(json.dumps(r) for r in b), encoding="utf-8")
