# -*- coding: utf-8 -*-
"""Apply sol P72_p9_r4 §2 manuscript corrections to paper_text.py (title, abstract, propositions, certificate wording, repair framing, no Transformer)."""
import pathlib
p = pathlib.Path(__file__).resolve().parent / "paper_text.py"; s = p.read_text(encoding="utf-8")
B = chr(92)
rep = [
 (B + "title{Predictive Sufficiency and Selective Roman-Numeral Repair in Annotated Harmonic Corpora}", B + "title{Roman-Numeral Information Beyond Local Chord Content: Predictive Sufficiency and a Failed Preregistered Repair}"),
 ("we find that local chromatic root degree, chord type and mode are approximately sufficient in the Annotated Beethoven Corpus (string quartets) and the Mozart piano sonatas: the selective Roman label adds at most %(maxABC)s bits per chord.",
  "the maximum observed selective-label residue is %(maxABC)s bits per chord in the Annotated Beethoven Corpus (string quartets) and %(maxMoz)s in the Mozart piano sonatas, meeting our operational, finite-corpus criterion of at most $0.05$ bits per chord."),
 ("In the Beethoven piano sonatas it adds %(s1)s to %(s2)s bits per chord, and this advantage survives root-free geometry (%(rf1)s to %(rf2)s), reinterpretation-preserving events, a fixed target alphabet and smoothing from $" + B + "beta=0.25$ to $4$; it halves under a target that removes the current chord shape (%(nc1)s to %(nc2)s).",
  "In the Beethoven piano sonatas the selective label gains %(s1)s to %(s2)s bits per chord on the base target and %(nc1)s to %(nc2)s on a separate no-current-shape control; under the combined root-free, fixed-alphabet, no-current-shape held-out protocol the residue is %(cl1)s at $m=1$ and %(cl2)s at $m=2$. Functional relabelling of applied chords accounts for %(rlp1)s" + B + "%% and %(rlp2)s" + B + "%% of the base residue."),
 ("We state the sufficiency and repair theorems that make the quantities exact, release an integer-count certificate, and report a preregistered MDL repair over five label features.",
  "We use two standard log-loss identities to define the oracle quantities, report finite prequential code contrasts, provide an archival integer-count certificate, and document the failure of a preregistered five-feature MDL repair, which recovered %(rho1)s of the clean residue at $m=1$ with unstable feature selection and %(rhob1)s to %(rhob2)s of the base residue."),
 (B + "begin{theorem}[predictive sufficiency]", B + "begin{proposition}[predictive sufficiency; standard]"),
 (B + "end{theorem}" + chr(10) + B + "begin{theorem}[repair decomposition]", B + "end{proposition}" + chr(10) + B + "begin{proposition}[repair decomposition; standard]"),
 (B + "end{theorem}" + chr(10) + "Both statements are standard", B + "end{proposition}" + chr(10) + "Both statements are standard"),
 (B + "newtheorem{theorem}{Theorem}" + B + "newtheorem{definition}{Definition}", B + "newtheorem{proposition}{Proposition}" + B + "newtheorem{definition}{Definition}"),
 ("Both statements are standard (log-loss regret equals conditional mutual information; kernel equality is Kemeny--Snell lumpability). Their role here is to fix what is being measured.",
  "Both statements are background identities (log-loss regret equals conditional mutual information; kernel equality is Kemeny--Snell lumpability), not contributions of this paper. Their role is to fix what is being measured."),
 ("Every table below is regenerated from released integer counts:", "At submission every table will be regenerated from an archived manifest containing, for each corpus, $m$, target and context:"),
 ("The build fails if any headline number changes.", "The build fails if any headline number changes. Until the archive and its hashes are public this is an intended certificate, not a released one."),
 ("Root-free geometry retains %(rfpct1)s" + B + "%% and %(rfpct2)s" + B + "%% of the base sonata residue; the no-current-shape target retains %(ncpct1)s" + B + "%% and %(ncpct2)s" + B + "%%.",
  "Considered separately, root-free geometry retains %(rfpct1)s" + B + "%% and %(rfpct2)s" + B + "%% of the base sonata residue and the no-current-shape target retains %(ncpct1)s" + B + "%% and %(ncpct2)s" + B + "%%; under the combined root-free, fixed-alphabet, no-current-shape held-out protocol the sonata residues are %(cl1)s and %(cl2)s bits per chord."),
 ("Relabelling only the applied chords by their functional degree, again at the same arity, recovers %(rl1)s and %(rl2)s bits, that is %(rlp1)s" + B + "%% and %(rlp2)s" + B + "%% of the residue.",
  "At the same arity, functional relabelling of applied chords yields code gains of %(rl1)s and %(rl2)s bits, equal to %(rlp1)s" + B + "%% and %(rlp2)s" + B + "%% of the displayed selective contrast; this does not by itself establish a causal syntactic effect or a feature interaction."),
 (B + "section{Preregistered MDL repair}", B + "section{A failed preregistered MDL repair}"),
 ("the success criterion was $" + B + "rho" + B + "ge0.80$.}", "the preregistered rule required $" + B + "rho" + B + "ge0.80$ at both $m=1,2$ plus 4-of-5 fold stability; it failed because clean $m=1$ reached only %(rho1)s without stability and the base-target recoveries were %(rhob1)s and %(rhob2)s. Recovery is n/a where $G_{" + B + "mathrm{ref}}" + B + "le 0$.}"),
 ("Training the coder on one corpus and coding another, the sonata corpus keeps its residue whichever corpus supplies the counts, and the other two corpora stay at or below $0.053$",
  "Training the coder on one corpus and coding another, sonata-target residues remain the largest under both adapted and source-only scoring, and the other targets stay at or below $0.053$"),
]
for a, b in rep:
    assert a in s, a[:70]
    s = s.replace(a, b, 1)
i = s.index(B + "section{Learned-model robustness (appendix study)}"); j = s.index(B + "section{Scope and limitations}")
s = s[:i] + B + "section{Learned-model robustness}" + chr(10) + "Learned-model robustness was not tested; coder dependence remains a limitation (plain KT without back-off inverts the ranking, and the sonata residue moves between %(b025)s and %(b4)s bits at $m=1$ as the smoothing mass varies from 0.25 to 4)." + chr(10) + chr(10) + s[j:]
old_keys = 'Ddet=f(((r(S, 1, "rootfree")'
new_keys = ('maxMoz=f(max(g(Mo, m, "gain_func_vs_localrel") for m in (1, 2, 3))), '
            'cl1=f(_rep(rep, S, 1, "clean")["G_ref"], 4), cl2=f(_rep(rep, S, 2, "clean")["G_ref"], 4), rho1=str(_rep(rep, S, 1, "clean")["recovery_rho"]), '
            'rhob1=str(_rep(rep, S, 1, "base")["recovery_rho"]), rhob2=str(_rep(rep, S, 2, "base")["recovery_rho"]), b025=f(r(S, 1, "beta0.25")), b4=f(r(S, 1, "beta4")), ' + old_keys)
assert old_keys in s; s = s.replace(old_keys, new_keys, 1)
s = s.replace('def render(M):', 'def _rep(rep, corpus, m, target):\n    return [x for x in (rep or []) if x["corpus"] == corpus and x["m"] == m and x["target"] == target][0]\n\n\ndef render(M):', 1)
s = s.replace('(str(x["recovery_rho"]) if x["recovery_rho"] is not None else "--"), ", ".join(s or "Z" for s in x["selected_masks"])',
              '(str(x["recovery_rho"]) if (x["recovery_rho"] is not None and x["G_ref"] > 0) else "n/a"), ", ".join(s or "none" for s in x["selected_masks"])')
p.write_text(s, encoding="utf-8"); print("paper_text patched")
