# Paper 9 PLAN v2 (2026-09-02, after sol rounds 1-3): Predictive Sufficiency and Selective Roman-Numeral Repair in Annotated Harmonic Corpora

Brand: **Lumpy** (https://github.com/AidenLee0011/lumpy-harmony). Rules: STANDARDS/paperops.md §31 (logic part + experiment part; zero LLM judging; no in-person venue). Sol ledger: `_sol/p72/P72_p9_r1..r3.md`.

## 0. Four axes (after round 3)
| Axis | Score | Evidence |
|---|---:|---|
| C | 3 now, 4 conditional | Theorems are standard; distinctiveness = controls-surviving selective-quotient result + exact certificate + preregistered MDL repair (round 4) |
| P | 4 | Geometry vs function is the live formal-harmony dispute; DCML corpora are the shared instrument |
| A | 3 | Coder/controls/e-process machinery; both theorems standard |
| F | 5 | 188 movements, minutes on CPU, LLM 0 |
Gates 6 (logic) and 7 (venue: TISMIR/JMM) pass. C x P gate passes only if round 4 confirms.

## 1. One claim (sol r3)
Under a fixed leave-one-movement-out prequential code, local chromatic root degree, chord type and mode are approximately sufficient in ABC and Mozart, whereas a selective Roman-numeral quotient retains a sonata-corpus advantage of 0.086 to 0.096 bits/chord under root-free geometry and 0.047 to 0.056 under a separate no-current-shape target control; unrestricted full Roman syntax does not improve finite-sample code length.

## 2. What it is / is not
Representation-sufficiency + constrained-repair paper on a finite corpus, selective-quotient result, corpus-level contrast. Not "Roman function beats geometry", not a population theorem, not complete-syntax, not a composer contrast (ABC is also Beethoven).

## 3. Theorems
T1 predictive sufficiency: R_Z - R_F = I(Y;F|G,Z) >= 0; zero iff Y ⟂ F | (G,Z) iff kernels identical within (G,Z) blocks iff predictive lumpability. Code differences estimate this and may be negative (finite coder).
T2 repair decomposition: I(Y;F|G,Z) = I(Y;R|G,Z) + I(Y;F|G,R); kernel-equivalence classes = unique coarsest exact repair; MDL-selected 5-feature repair minimal only within the 32-node lattice.

## 4. Exact certificate (11 components, sol r3 §3): provenance hashes, canonical events, nestedness table h:F->Z, integer count tensors, cross-product equality audit, empirical CMI expression, coding ledger, exact code ratio Q, movement certificates, repair certificate, negative controls.

## 5. Results (data/*.json, regenerable)
See README table; controls_r3 (rootfree 0.086/0.096; nocur 0.056/0.047; fullroman 0.006/-0.096), transfer (adapted; source-only running), residue_decompose (spelled3 = func exactly; relabel3 recovers 61%/52%), jazz 2.43.

## 6. Round-4 confirmatory (running: repair_lattice.py)
32-node lattice S/C/M/A/I over Z; work-grouped 5 folds (SHA256 round robin); training-prequential MDL selection D(B)=3+ceil(log2 C(5,r)); held-out per-movement reset scoring; rho = G_repair/G_ref >= 0.80 at m=1,2; >=70% movements positive; ABC false-positive <= 0.05; 4/5 fold stability. Fail => kill the repair claim (report as failure), no custom distinctions.

## 7. Experiment part (appendix): 2-layer Transformer d=96, 4 heads, FFN 192; conditions geom/localrel/func with padded condition vocab; 5 work folds, 10 seeds; success = median D_NN > 0 (deterministic D_det = 0.0754).

## 8. Venue: TISMIR (28% conditional) / JMM (15%); kill probability 0.40. Paper 10: WJazzD contrast is not yet a paper (sol r3 §5).

## 9. Figures (5): controls forest, prevalence, attribution, MDL lattice (gates submission), transfer + jazz.
