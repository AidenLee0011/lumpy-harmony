# Paper 9 PLAN v1 (2026-09-02): Approximate predictive sufficiency of harmonic labels, with a repair classification

Working brand: **Lumpy** (lumpability of harmonic labels). Status: sol P72 p9 rounds 1-2 done; round-3 controls running. Rules: STANDARDS/paperops.md §31 (logic part = theorem + exact certificate; experiment part = deterministic corpus computation, optional small learned-model robustness appendix; zero LLM judging), no in-person venues.

## 0. Four axes (paper_topic_axes.md), after round 2
| Axis | Score | Evidence |
|---|---:|---|
| C ceiling | 2 now, 3 conditional | Theorem core is standard (CMI = log-loss regret; zero residue iff predictive lumpability); the contribution must be the constrained repair classification + exact corpus certificate + the sonata exception surviving controls |
| P pain | 4 | Geometry (Tymoczko, Callender-Quinn-Tymoczko) vs tonal function / grammar (Rohrmeier, Jacoby) is the live dispute in formal harmony; DCML corpora are the field's shared instrument |
| A asset fit | 2 now, 3 conditional | Hierarchical prequential coder is basic; e-process + partition-refinement machinery can carry the repair and evidence layer |
| F feasibility | 5 | 188 movements, all computations minutes on CPU, LLM 0 |
Gates: 6 (logic-based) pass; 7 (venue) pass with TISMIR / JMM. C x P gate: not passed until the round-3 controls hold.

## 1. One claim (option (a), sol r2)
Under a specified prequential coding protocol, reducing the current Roman-numeral content to (local chromatic root degree, chord type, local mode) loses at most 0.045 bits per chord in the Annotated Beethoven Corpus (quartets) and the Mozart piano sonatas for context depth m <= 3, but 0.114 to 0.130 bits per chord in the Beethoven piano sonatas; a constrained repair over predefined Roman distinctions identifies which distinctions carry the residue.

Title candidates: "How Much of Roman-Numeral Harmony Is Just the Local Key? Approximate Predictive Sufficiency and a Repair Classification on 188 Classical Movements".

## 2. Novelty record (§31 rule 3)
Nearest works + delta: Tymoczko 2006 / CQT 2008 (geometric chord spaces; no information-theoretic sufficiency test) · Rohrmeier 2011 (tonal grammar; not the exact information missing from geometry) · Pearce-Wiggins 2012 IDyOM (predictive information for expectation; no representation-quotient comparison) · Hentschel et al. 2021 ABC (the labels; no sufficiency theorem) · Kemeny-Snell lumpability / probabilistic bisimulation (the mathematics; no musical state construction or constrained repair).
Kill sentence (JMM): "the standard equivalence among CMI, log-loss sufficiency and predictive lumpability, while the music-specific repair theorem and minimality remain unproved." Kill sentence (TISMIR): "once local key, analyzed root and chord type are supplied, Roman syntax contributes at most 0.045 bits in two corpora, the sonata effect may be corpus-specific, and the ranking changes with the coder."
Reduction attempts recorded: Theorem 1 = standard; contribution must be (i) the constrained repair classification with an MDL-charged held-out partition, (ii) the exact integer-count certificate, (iii) the controls-surviving corpus contrast.
arXiv occupancy (data/occupancy_r1.json, 2026-09-02): all 10 candidate-3 queries return 0 hits except "harmony AND minimum description length" = 1.

## 3. Corpora (pinned)
DCML `ABC` (70 movements, CC BY-NC-SA 4.0), `mozart_piano_sonatas` (54), `beethoven_piano_sonatas` (64); clone 2026-09-02 (record commit SHAs in software.lock before freeze). WJazzD (456 solos, CC BY-NC-SA 3.0) as out-of-domain contrast only (no Roman labels). music21 Bach chorales 430 as a further contrast (labels by music21 romanNumeralFromChord, not human).

## 4. Results so far (deterministic, code in this directory)
| computation | result |
|---|---|
| pilot_residue.py full (back-off β=1, LOMO) | residue func vs localrel: ABC 0.012/0.040/0.045 (m=1/2/3), Mozart 0.003/0.025/0.032, Beethoven sonatas 0.114/0.130/0.118; func vs global-key baseline +0.45 to +0.60 everywhere |
| plain KT (no back-off) | ranking inverts (geom best) = sparsity artefact; reported |
| residue_decompose.py | feature attribution: relativeroot carries most of the sonata residue at m=1 (0.046 of 0.114); figbass/changes hurt (dilution); form 0 |
| transfer.py | residue is a property of the target corpus: any training corpus -> sonatas gives 0.10 to 0.15; -> ABC/Mozart gives <= 0.053 |
| jazz_contrast.py (WJazzD) | key-relative chord content gain over geometry 2.1 to 2.8 bits/chord (vs 0.4 to 0.6 classical); postbop 2.80, hardbop 2.16 |
| controls_r3.py | running: rootfree geometry, no-collapse, full Roman syntax, fixed alphabet + UNK, target without current chord, β sensitivity |

## 5. Decisive rule (round 3, sol)
Proceed iff the sonata residue survives rootfree + fullroman + fixedalpha + nocollapse controls and cross-corpus transfer, and predefined Roman distinctions explain >= 80% of it on held-out movements with an MDL-charged partition. Otherwise stop.

## 6. Two-part structure (§31 rule 2)
Logic part: Theorem 1 (sufficiency iff lumpability, exact integer certificate), Theorem 2 (coarsest constrained repair, MDL-charged held-out version), Pinsker calibration of ε. Experiment part: 188-movement deterministic coding study + controls + transfer + jazz/Bach contrasts; optional robustness appendix = one small Transformer (10 seeds, matched tokenisation) checking the representation ordering (sol: +0 to 2 pp).

## 7. Venue
TISMIR (no presentation; conditional 24% after controls) primary; JMM (16%) secondary. ICLR/ICML: not a fit.
