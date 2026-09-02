# Lumpy

<img src="brand/lumpy.svg" width="520" alt="Lumpy, a round blob who lumps Roman numerals into one warm local key">

**How much of Roman-numeral harmony is just the local key?**

Lumpy is a deterministic corpus study (zero LLM calls) with a small set of theorems. It asks a blunt question about harmonic analysis:
if you already know the *local key*, the *chord type*, and the *voice-leading geometry* of a progression, how many bits per chord does the
Roman-numeral label still add when predicting the next chord move?

Answer so far (188 classical movements, DCML corpora, leave-one-movement-out prequential coding):

| corpus | Roman label gain over global-key content | Roman residue beyond local-key content |
|---|---:|---:|
| Annotated Beethoven Corpus (string quartets, 70 mvts) | +0.45 to +0.52 bits/chord | 0.01 to 0.05 |
| Mozart piano sonatas (54 mvts) | +0.39 to +0.60 | 0.00 to 0.03 |
| Beethoven piano sonatas (64 mvts) | +0.45 to +0.58 | **0.11 to 0.13** |

So Roman labels are almost "lumpable" to (local scale degree, chord type) in two corpora, and carry a real extra 0.1 bit in the sonata corpus.
The residue survives root-free geometry, no event collapsing, a fixed target alphabet, and coder smoothing from 0.25 to 4; it halves when the
prediction target drops the current chord shape. Whichever corpus you train on, the sonata corpus keeps its residue.

Jazz contrast (Weimar Jazz Database, 456 solos, chord symbols): key-relative chord content improves next-move prediction by **2.4 bits/chord**,
five times the classical gain.

## What is in here
- `corpora.py` unified loaders (DCML TSV, WJazzD sqlite, music21 Bach chorales) -> one event schema
- `pilot_residue.py` the coding experiment (geometry / global-key / local-key / Roman contexts, KT and back-off coders)
- `controls_r3.py` robustness controls, `transfer.py` cross-corpus transfer, `residue_decompose.py` feature attribution + e-process, `jazz_contrast.py`
- `repair_lattice.py` the preregistered 32-node MDL repair (failed; reported as a negative result), `lowo_headline.py` / `lowo_nested.py` leave-one-work-out, `nesting_check.py` the machine check that a richer label really refines the baseline (prints every counterexample), `certificate.py` the integer-count certificate
- `data/*.json` every number in the tables above, regenerable
- `p10/` the companion study on time irreversibility of harmonic transition laws (Bach chorales vs WJazzD): support-controlled held-out reversal scores, the exact C12 -> D12 inversion-quotient allocation, alphabet-matching and mode-composition controls, spanning-forest cycle circulation, and its own `build_paper.py`
- `PLAN.md` the preregistration-style plan, novelty record and kill rules
- `brand/lumpy.svg` the mascot

## Data and licenses
DCML corpora (ABC, mozart_piano_sonatas, beethoven_piano_sonatas): CC BY-NC-SA 4.0, https://github.com/DCMLab. Weimar Jazz Database: CC BY-NC-SA 3.0,
https://jazzomat.hfm-weimar.de. Bach chorales via music21's bundled corpus. This repository redistributes only derived counts and code.

## Status
Research in progress (2026-09). Target venue: a journal without a presentation requirement (TISMIR / Journal of Mathematics and Music).

Current corrected claims. Paper A (this directory): a genuine Roman refinement of local chord content adds at most 0.049 bits/chord in three DCML corpora; the larger selective-label gain is applied-chord lumping, not extra syntax; the preregistered MDL repair failed. Paper B (`p10/`): inversion orientation carries 16% of the held-out reversal score in Bach chorales and 4% in WJazzD, but the Bach share is a minor-mode quantity (major 0.1%, minor 30%); alphabet matching does not remove the contrast, mode composition partly does; no genre effect is claimed.
Nothing here is peer reviewed yet. The mascot is friendly; the reviewers will not be.
