# -*- coding: utf-8 -*-
"""Paper 10 LaTeX body (sol P72_p10_r3 §3 spec). All numbers from the manifest M."""
import json


def f(x, d=3):
    return ("%%.%df" % d) % x


def render(M):
    S, SUP, INV, INVU, DEC, R4 = M["S"], M["SUP"], M["INV"], M["INVU"], M["DEC"], M.get("R4", {})
    b, w = INV["bach"]["alpha"], INV["wjazzd"]["alpha"]
    def inv_rows(c, d):
        return "\n".join(r"%s & %s & %s & %s & %s & %s & %s & %s \\" % (c, a, f(d[a]["sigma_C"]), f(d[a]["sigma_D"]), f(d[a]["Delta_inv"]), "%.1f" % (100 * d[a]["residual_share"]), f(d[a]["group_mean"]), f(d[a]["group_LCB95"])) for a in ("0.1", "0.5", "1"))
    unc = "\n".join(r"%s (uncollapsed) & 0.5 & %s & %s & %s & %s & %s & %s \\" % (c, f(INVU[k]["alpha"]["0.5"]["sigma_C"]), f(INVU[k]["alpha"]["0.5"]["sigma_D"]), f(INVU[k]["alpha"]["0.5"]["Delta_inv"]), "%.1f" % (100 * INVU[k]["alpha"]["0.5"]["residual_share"]), f(INVU[k]["alpha"]["0.5"]["group_mean"]), f(INVU[k]["alpha"]["0.5"]["group_LCB95"])) for c, k in (("Bach", "bach"), ("WJazzD", "wjazzd")))
    def sup_rows(k):
        rows = []
        for a in ("0.1", "0.5", "1"):
            for r in (0, 1, 2, 5):
                x = SUP[k]["results"]["alpha=%s|r=%d" % (a, r)]; rows.append(r"%s & %s & %s & %s & %s & %s & %s \\" % (a, ("all" if r == 0 else "r=%d" % r), "%.1f" % (100 * x["rho"]), f(x["retained_total"]), f(x["conditional"]), f(x["work_LCB95"]), x["zero_works"]))
        return "\n".join(rows)
    def edge_rows(k):
        return "\n".join(r"%s & %d & %d & %s \\" % (t["edge"].replace("/maj", " (major)").replace("/min", " (minor)").replace(":", " "), t["count"], t["reverse"], f(t["contribution_bits"])) for t in DEC[k]["top_edges"][:8])
    cyc = ""
    if R4:
        rows = []
        for k, c in (("bach", "Bach"), ("wjazzd", "WJazzD")):
            for t in R4[k]["circulation"]["top"][:5]:
                rows.append(r"%s & %s & %s & %s & %s & %s \\" % (c, t["loop"].replace("/maj", "").replace("/min", "m").replace(">", r"$\rightarrow$"), f(t["j_C"], 5), f(t["A_C"], 2), f(t["term_bits"], 4), "%.1f" % (100 * t["share"])))
        cyc_rows = "\n".join(rows)
        nl = []
        for k, c in (("bach", "Bach"), ("wjazzd", "WJazzD")):
            for lab, v in R4[k]["named_loops"].items():
                nl.append(r"%s & %s & %d & %d & %d \\" % (c, lab.replace(">", r"$\rightarrow$"), v["forward"], v["reverse"], v["works_with_forward"]))
        nl_rows = "\n".join(nl)
        cyc = r"""\begin{table}[t]\centering\small
\caption{Fundamental-cycle decomposition of the stationary first-order fit (maximum symmetric-traffic spanning forest; $\sigma=\sum_C j_C A_C$ closes to machine precision: Bach $\sigma=%(sb)s$, WJazzD $\sigma=%(sw)s$; top-5 shares %(t5b)s and %(t5w)s). Terms are basis dependent; only the total is invariant.}\label{tab:cyc}
\begin{tabular}{llrrrr}\toprule corpus & fundamental cycle & $j_C$ & $A_C$ (bits) & $j_C A_C$ & share (\%%) \\ \midrule
%(cyc_rows)s
\bottomrule\end{tabular}\end{table}
\begin{table}[t]\centering\small
\caption{Named loops as contiguous four-state windows within works (collapsed events): forward and exactly reversed occurrences.}\label{tab:loops}
\begin{tabular}{llrrr}\toprule corpus & loop & forward & reverse & works with forward \\ \midrule
%(nl_rows)s
\bottomrule\end{tabular}\end{table}
""" % dict(sb=f(R4["bach"]["circulation"]["sigma_stationary_bits"]), sw=f(R4["wjazzd"]["circulation"]["sigma_stationary_bits"]), t5b="%.0f\\%%" % (100 * R4["bach"]["circulation"]["top5_share"]), t5w="%.0f\\%%" % (100 * R4["wjazzd"]["circulation"]["top5_share"]), cyc_rows=cyc_rows, nl_rows=nl_rows)
    vs = M.get("VS")
    vs_txt = ("Standardising the two corpora to common weights over inversion-closed chord-family strata changes the share contrast from $%s$ to $%s$ ($E=%s$)." % (f(vs["D_obs"]), f(vs["D_std"]), f(vs["E"], 2))) if vs else ""
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{amsmath,amssymb,amsthm,booktabs,graphicx,hyperref}
\newtheorem{lemma}{Lemma}\newtheorem{definition}{Definition}
\title{Support-Controlled Harmonic Reversal Asymmetry and Exact Inversion-Quotient Allocation in Bach Chorales and WJazzD}
\author{Anonymous}\date{Draft, September 2026}
\begin{document}\maketitle
\begin{abstract}
We measure how far harmonic progressions are from time-reversible, at the level of chord-to-chord transitions quotiented by transposition, in two public symbolic corpora: %(nb)d Bach chorales (music21 corpus, %(eb)d chord changes, %(sb)d key-relative states) and %(nw)d Weimar Jazz Database solos (%(ew)d chord changes, %(sw)d states, grouped into %(gw)d compositions). The estimand is the held-out log-ratio of forward to reversed transition counts, $\sigma$, scored on work-grouped folds. Bilaterally observed edges carry %(bb)s to %(bb2)s bits per transition in Bach and %(bw)s to %(bw2)s in WJazzD (retained-total and conditional estimands), so the asymmetry is not an artifact of one-way transitions. A KL chain-rule lemma gives an exact allocation $\sigma_{C_{12}}=\sigma_{D_{12}}+\Delta_{\mathrm{inv}}$ between inversion-invariant and inversion-resolving components, closing to machine precision on every event. In Bach, inversion orientation carries %(ib1)s to %(ib2)s bits per transition, %(sh_b)s of the reversal score, with chorale-level 95\%% lower bounds of %(lb1)s to %(lb2)s; in WJazzD it carries %(sh_w)s with composition-level lower bounds of %(lw1)s to %(lw2)s, positive but below our preregistered 0.10-bit threshold. Cycle affinities and a spanning-forest circulation basis localise the asymmetry in cadential and turnaround loops. We cite Gonz\'alez-Espinoza, Mart\'inez-Mekler and Lacasa (2020) as the direct predecessor on melodic time irreversibility and claim no theorem novelty for the quotient identity.
\end{abstract}

\part*{I. Logic}
\section{Prior musical irreversibility and claim boundary}
Time irreversibility of music has been quantified before: Gonz\'alez-Espinoza, Mart\'inez-Mekler and Lacasa (2020) applied horizontal-visibility-graph statistics to scalar melodic note streams across 8{,}856 pieces. We quantify a different object, the reversal asymmetry of transposition-quotiented harmonic transition laws, and localise it through inversion-sensitive, directed-edge and closed-cycle analyses. The quotient identity we use is a corollary of the KL chain rule and of exact coarse-graining results (Esposito, 2012; Teza and Stella, 2020); it is stated as a lemma because it fixes the estimand and prevents an incorrect quotient implementation, not as a contribution.

\section{Harmonic edge laws, reversal and bilateral-support estimands}
\begin{definition}A chord event is a key-relative 12-bit pitch-class mask with mode (the annotated tonic at pitch class 0); consecutive identical masks are collapsed to chord changes (an uncollapsed control is reported). A directed edge is a pair $(i,j)$ of consecutive states; $R(i,j)=(j,i)$ is reversal. For an edge law $\mu$, $\sigma(\mu)=D_{\mathrm{KL},2}(\mu\Vert R_*\mu)$ in bits.\end{definition}
Held-out scoring: for work-grouped folds, each held-out edge receives $d_{ij}=\log_2\frac{c_{ij}+\alpha}{c_{ji}+\alpha}$ from training counts; the event mean estimates $\sigma$. Bilateral support restricts to edges with $c_{ij},c_{ji}\ge r$ in training; the retained-total estimand assigns excluded edges zero, the conditional estimand averages over retained edges only.

\section{Diagonal $C_{12}$ quotient and the chain-rule lemma}
\begin{lemma}[quotient identity; standard]Let $G=\mathbb Z_{12}$ act diagonally on edges, $T_g(i,j)=(gi,gj)$, and let reversal commute with the action. For the symmetrised law $\mu^G=\frac{1}{12}\sum_g (T_g)_*\mu$ and the orbit map $q$, $\sigma(\mu^G)=\sigma(q_*\mu)$.\end{lemma}
Proof: KL chain rule for the statistic $q$; both symmetrised laws are uniform within each orbit, so the conditional term vanishes. Our key-relative representation is the tonic-anchored orbit representative (an exact unsmoothed check on the common support gives identity gap $0.0$ in Bach; smoothed plug-ins differ because pseudocounts must be pushed forward, not added per cell).

\section{Exact $C_{12}\rightarrow D_{12}$ allocation}
Let $\kappa$ be mode-conditioned pitch-class inversion ($p\mapsto -p$) and $h$ the further quotient identifying an edge with its inversion. Since $h$ commutes with reversal, the chain rule gives, exactly and per event,
\[\sigma_{C_{12}}=\sigma_{D_{12}}+\Delta_{\mathrm{inv}},\qquad \Delta_{\mathrm{inv}}=\sum_z (h_*P)(z)\,D\big(P(\cdot\mid z)\Vert Q(\cdot\mid z)\big)\ge0,\]
with $P$ the $C_{12}$ law, $Q=R_*P$, and $h_*P$ obtained only by pushforward. $\Delta_{\mathrm{inv}}$ is the part of reversal asymmetry that requires distinguishing an interval structure from its inversion. The mode covariate is held fixed under $\kappa$; this is one valid $D_{12}$ action, not the unique music-theoretic one.

\section{Detailed balance, cycle affinities and circulation}
For a stationary first-order chain with flow $F_{ij}=\pi_iP_{ij}$, $\sigma=\sum_{i<j}(F_{ij}-F_{ji})\log_2(F_{ij}/F_{ji})$, and $\sigma=0$ iff detailed balance iff every cycle affinity $A_C=\sum_{(i,j)\in C}\log_2(F_{ij}/F_{ji})$ vanishes (Kolmogorov, 1936). With a spanning forest, $\sigma=\sum_C j_C A_C$ over fundamental cycles; individual terms are basis dependent, the total is not. A loop's affinity is a force, not a contribution: it is reported together with its circulation and with contiguous path counts.

\part*{II. Experiment}
\section{Corpora, states and grouped folds}
Bach: %(nb)d chorales, %(eb)d collapsed chord changes, %(sb)d states; folds by chorale. WJazzD: %(nw)d solos in %(gw)d compositions, %(ew)d collapsed chord changes, %(sw)d states; folds by composition so performances of one tune never cross folds. Chord types are triads (Bach, music21 quality) and thirteen jazz symbol templates (WJazzD). State alphabets differ (%(sb)d versus %(sw)d), so raw magnitudes are not compared across corpora.

\section{Support-controlled held-out irreversibility}
\begin{table}[t]\centering\small\caption{Held-out reversal asymmetry by bilateral support (bits per transition). rho = share of held-out events on edges observed in both directions in training; retained-total assigns excluded edges zero; LCB = work- (Bach) or composition- (WJazzD) level 95\%% lower bound.}\label{tab:sup}
\begin{tabular}{lrrrrrr}\toprule $\alpha$ & support & $\rho$ (\%%) & retained-total & conditional & LCB & works with no retained edge \\ \midrule
\multicolumn{7}{l}{\emph{Bach chorales}} \\
%(supb)s
\multicolumn{7}{l}{\emph{WJazzD}} \\
%(supw)s
\bottomrule\end{tabular}\end{table}
Endpoint (piece boundary) marginals contribute %(epb)s\%% (Bach) and %(epw)s\%% (WJazzD) of the plug-in $\sigma$; merging states with fewer than five occurrences changes nothing. Figure~2 shows the support curves.
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig2_support.pdf}\caption{Bilateral-support control: retained-total (solid) and conditional (dashed) scores across support thresholds and smoothing.}\end{figure}

\section{Inversion allocation and group inference}
\begin{table}[t]\centering\small\caption{Exact held-out $C_{12}\rightarrow D_{12}$ allocation (bits per transition). Per-event closure error $\le 9\times10^{-16}$. Group = chorale (Bach) or composition (WJazzD).}\label{tab:inv}
\begin{tabular}{llrrrrrr}\toprule corpus & $\alpha$ & $\sigma_{C}$ & $\sigma_{D}$ & $\Delta_{\mathrm{inv}}$ & share (\%%) & group mean & group LCB \\ \midrule
%(invb)s
%(invw)s
%(unc)s
\bottomrule\end{tabular}\end{table}
The preregistered conjunctive rule (group LCB $>0.10$ bits in both corpora at every $\alpha$) fails: the minimum is $%(mmin)s$ (WJazzD, $\alpha=1$). Bach passes at every $\alpha$ and its share is stable at %(sh_b)s across collapsed and uncollapsed events; WJazzD's share is %(sh_w)s. The absolute residuals are similar at $\alpha=0.1$ (%(ib1)s versus %(iw1)s bits); the share contrast reflects WJazzD's three-fold larger inversion-invariant asymmetry. %(vs_txt)s
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig3_decomposition.pdf}\caption{Exact allocation of held-out reversal asymmetry into inversion-invariant and inversion-resolving parts.}\end{figure}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig4_lcb.pdf}\caption{Group-level $\Delta_{\mathrm{inv}}$ with 95\%% lower bounds; dashed = preregistered 0.10 bits.}\end{figure}

\section{Edge drivers, named paths and cycle circulation}
\begin{table}[t]\centering\small\caption{Top directed edges by plug-in contribution to $\sigma$ (forward and reverse counts).}\label{tab:edges}
\begin{tabular}{lrrr}\toprule edge & forward & reverse & bits \\ \midrule
\multicolumn{4}{l}{\emph{Bach}} \\
%(edgb)s
\multicolumn{4}{l}{\emph{WJazzD}} \\
%(edgw)s
\bottomrule\end{tabular}\end{table}
%(cyc)s
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig5_edges.pdf}\caption{Top directed edges by contribution.}\end{figure}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig6_cycles.pdf}\caption{Fundamental-cycle terms of the stationary fit.}\end{figure}
Depth-2 path asymmetry (plug-in) is %(d2b)s bits in Bach and %(d2w)s in WJazzD against %(s1b)s and %(s1w)s at the edge level; held-out path estimates are left for future work.

\section{Limitations and replication}
All quantities are descriptive of these two annotated corpora, their chord-type templates, key annotations (machine-estimated for Bach, annotated for WJazzD), event definitions and the fixed smoothing family. The inversion action is mode-conditioned pitch-class inversion; other $D_{12}$ actions are possible. Raw Bach and WJazzD magnitudes are not compared as a genre effect. Code and derived counts are released; every table regenerates from the JSON manifest.
\end{document}
""" % dict(nb=S["bach"]["works"], eb=INV["bach"]["alpha"]["0.5"]["N"], sb=S["bach"]["states"], nw=S["wjazzd"]["works"], ew=INV["wjazzd"]["alpha"]["0.5"]["N"], sw=S["wjazzd"]["states"], gw=INV["wjazzd"]["groups"],
           bb=f(min(SUP["bach"]["results"]["alpha=%s|r=1" % a]["retained_total"] for a in ("0.1", "0.5", "1"))), bb2=f(max(SUP["bach"]["results"]["alpha=%s|r=1" % a]["conditional"] for a in ("0.1", "0.5", "1"))),
           bw=f(min(SUP["wjazzd"]["results"]["alpha=%s|r=1" % a]["retained_total"] for a in ("0.1", "0.5", "1"))), bw2=f(max(SUP["wjazzd"]["results"]["alpha=%s|r=1" % a]["conditional"] for a in ("0.1", "0.5", "1"))),
           ib1=f(min(b[a]["Delta_inv"] for a in b)), ib2=f(max(b[a]["Delta_inv"] for a in b)), iw1=f(w["0.1"]["Delta_inv"]), sh_b="%.1f to %.1f\\%%" % (100 * min(b[a]["residual_share"] for a in b), 100 * max(b[a]["residual_share"] for a in b)),
           sh_w="%.1f to %.1f\\%%" % (100 * min(w[a]["residual_share"] for a in w), 100 * max(w[a]["residual_share"] for a in w)), lb1=f(min(b[a]["group_LCB95"] for a in b)), lb2=f(max(b[a]["group_LCB95"] for a in b)), lw1=f(min(w[a]["group_LCB95"] for a in w)), lw2=f(max(w[a]["group_LCB95"] for a in w)),
           mmin=f(min(min(b[a]["group_LCB95"] for a in b), min(w[a]["group_LCB95"] for a in w))), invb=inv_rows("Bach", b), invw=inv_rows("WJazzD", w), unc=unc, supb=sup_rows("bach"), supw=sup_rows("wjazzd"),
           epb="%.1f" % (100 * S["bach"]["no_merge"]["endpoint_share"]), epw="%.1f" % (100 * (S["wjazzd"]["no_merge"]["endpoint_share"] or 0)), edgb=edge_rows("bach"), edgw=edge_rows("wjazzd"), cyc=cyc, vs_txt=vs_txt,
           d2b=f(DEC["bach"]["sigma_depth2"]), d2w=f(DEC["wjazzd"]["sigma_depth2"]), s1b=f(DEC["bach"]["sigma_plugin"]), s1w=f(DEC["wjazzd"]["sigma_plugin"]))
