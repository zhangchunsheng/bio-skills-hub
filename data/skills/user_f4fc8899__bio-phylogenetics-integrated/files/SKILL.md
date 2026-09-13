---
slug: bio-phylogenetics-integrated
version: 1.0.0
displayName: "系统发育 / Phylogenetic tree construction and manipulation"
name: bio-phylogenetics-integrated
summary: >-
  中文：系统发育综合技能，整合 8 个相关专题，覆盖系统发育树构建与操作：ML树（IQ-TREE2、RAxML-NG）、贝叶斯推断（BEAST2、MrBayes）、分歧时间定年。 English: Integrated Phylogenetic tree construction and manipulation skill covering 8 related topics, including Phylogenetic tree construction and manipulation: ML trees (IQ-TREE2, RAxML-NG), Bayesian inference (BEAST2, MrBayes), divergence dating.
description: >-
  中文：这是一个面向系统发育的综合生物信息学 Skill，整合当前分类下 8 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：系统发育树构建与操作：ML树（IQ-TREE2、RAxML-NG）、贝叶斯推断（BEAST2、MrBayes）、分歧时间定年。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ASTRAL-III, BEAST2, Bio.Phylo。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Phylogenetic tree construction and manipulation, combining 8 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Phylogenetic tree construction and manipulation: ML trees (IQ-TREE2, RAxML-NG), Bayesian inference (BEAST2, MrBayes), divergence dating. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ASTRAL-III, BEAST2, Bio.Phylo. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# phylogenetics 分类 Skill 整合版

> 本文件整合同一主分类目录下 8 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: phylogenetics -->

## 子目录：phylogenetics/bayesian-inference

<!-- BEGIN FILE: phylogenetics/bayesian-inference/SKILL.md -->
---
name: bio-phylo-bayesian-inference
description: Frames Bayesian phylogenetics as approximating a posterior distribution over trees conditioned on data AND priors via an MCMC that must be proven to have converged, using MrBayes, BEAST2, RevBayes, and PhyloBayes-MPI. Covers why convergence (ESS, PSRF, ASDSF, topology vs scalar) is the load-bearing claim, why posterior probabilities are systematically higher than bootstrap and overconfident under model misspecification, why the default branch-length prior inflates tree length, why the harmonic-mean estimator must never select models (use stepping-stone), and when site-heterogeneous CAT-GTR is required at depth. Use when needing posterior clade support, model averaging, marginal-likelihood model comparison, or CAT models for deep phylogeny. Routes topology-only ML to modern-tree-inference, divergence times to divergence-dating, and tree summarization to tree-io.
tool_type: mixed
primary_tool: MrBayes
---

## Version Compatibility

Reference examples tested with: MrBayes 3.2.7+, BEAST2 2.7+, RevBayes 1.2+, PhyloBayes MPI 1.9+, Tracer 1.7+. R diagnostics: RWTY, coda. Python: BioPython 1.83+, NumPy, pandas.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mb --version`, `beast -version`, `rb --version`, `pb_mpi` then check the help banner to confirm flags
- R: `packageVersion('rwty')` then `?analyze.rwty` to verify parameters
- Python: `pip show biopython` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The MrBayes default branch-length prior changed at 3.2.3 from `unconstrained:exp(10)` to the compound `unconstrained:gammadir`; do not assume the old default on any version. `stoprule`/`stopval` auto-halt on ASDSF.

# Bayesian Phylogenetic Inference -- A Posterior Over Trees Conditioned on Priors; an Unconverged Run Is Confident Nonsense

**"Run a Bayesian phylogenetic analysis"** -> Approximate the posterior distribution over trees and parameters by MCMC, then prove convergence before trusting any clade posterior.
- CLI: `mb` (MrBayes), `beast`/BEAUti (BEAST2), `rb` (RevBayes), `pb_mpi`/`bpcomp`/`tracecomp` (PhyloBayes)
- Diagnostics: Tracer (visual ESS/trace), RWTY/coda (R), MrBayes `sump`/`sumt`, BioPython for parsing output trees

Scope: the posterior-over-trees + MCMC-convergence + prior + marginal-likelihood-model-comparison spine, plus site-heterogeneous CAT models. Topology-only ML, bootstrap, IC model selection -> modern-tree-inference. Divergence times, clock models, node/tip calibration, fossilized birth-death -> divergence-dating. Multispecies-coalescent species trees under ILS -> species-trees. Reading/converting/summarizing the annotated output trees without dropping posteriors and HPDs -> tree-io.

## The Single Most Important Modern Insight

A Bayesian phylogeny is not a tree. It is a posterior distribution over trees (topologies AND branch lengths AND model parameters) conditioned on the data AND on the priors, approximated by a finite MCMC sample that may not have converged. The deliverable is a distribution WITH diagnostics, not a point estimate; the consensus tree with clade posteriors is a lossy summary of that distribution. Three load-bearing facts:

1. The posterior is conditional on priors that may not have been chosen deliberately. Default priors are not neutral: the MrBayes default branch-length prior before 3.2.3 (`exp(10)` per branch) systematically inflates tree length, and that inflation can feed back into topology and node support (Brown 2010; Zhang 2012). A run that converged beautifully can be confidently wrong because it converged to the posterior implied by a bad prior. "Converged" answers "did the MCMC sample the target distribution?" -- not "was the target distribution the right one?".
2. The approximation quality is unknown until diagnostics are run. Most Bayesian-phylogenetics results in the wild are non-convergence reported as a result. Convergence is not a checkbox; it is the load-bearing claim. Without ESS, PSRF/ASDSF, and topological convergence, the output is a candidate, not a result.
3. Posterior probabilities are systematically higher (closer to 0 or 1) than bootstrap support and are overconfident under model misspecification (Suzuki 2002; Erixon 2003). PP=1.0 is routine and is not proof. Under the correct model PP is roughly calibrated but more decisive than the bootstrap; under an under-parameterized model PP becomes anti-conservative, assigning high support to wrong clades. This is structural: a Bayesian analysis conditions on the model being true, so a false model has no mechanism to express doubt. Support is not accuracy.

## When to Use Bayesian vs ML

| Factor | ML (modern-tree-inference) | MrBayes | BEAST2 | RevBayes | PhyloBayes-MPI |
|--------|----------------------------|---------|--------|----------|----------------|
| Reach for it when | topology, fast, IC model selection, bootstrap | posterior clade PP on a standard alignment; easiest entry; model averaging | TIME trees, tip-dating, demographics, phylodynamics | the model is not a built-in option; full graphical-model control | DEEP phylogeny with compositional heterogeneity / LBA |
| Output | point tree + bootstrap | posterior + clade PP | dated posterior + HPDs | posterior, custom | posterior under CAT/CAT-GTR |
| Speed | fast | moderate | slow | moderate | brutal (days-weeks, MPI) |
| Multi-run | automatic resampling | `nruns=2` default | run seeds independently | manual | run chains independently |
| Citation | Minh 2020 | Ronquist 2012 | Bouckaert 2019 | Hohna 2016 | Lartillot 2013 |

Default recommendation: start with ML (modern-tree-inference) for the topology, then move to Bayesian when posterior probabilities, model averaging, divergence times, or site-heterogeneous models are specifically needed. Need TIMES -> divergence-dating. Need a coalescent species tree -> species-trees.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| MrBayes 3.2 | Ronquist 2012 | NEXUS `lset`/`prset`; native MC3 + 2 runs; live ASDSF | general-purpose first choice for a concatenated alignment; partitioned data; `nst=mixed` model averaging |
| BEAST2 | Bouckaert 2019 | BEAUti -> XML; operator tuning; no MC3 by default | TIME trees, tip-dating, coalescent/birth-death demographics, phylodynamics (-> divergence-dating) |
| RevBayes | Hohna 2016 | Rev probabilistic-graphical-model scripting | a model that is not a checkbox: novel mixtures, custom hierarchical priors, biogeography |
| PhyloBayes-MPI | Lartillot 2013 (CAT: Lartillot 2004) | data-augmentation MCMC, MPI-parallel; CAT/CAT-GTR | deep phylogeny, compositional heterogeneity, LBA; `bpcomp`/`tracecomp` convergence |

Decision tree: standard alignment wanting clade PP, easiest path -> MrBayes (gammadir brlenspr, nruns>=2, gate on ASDSF<0.01). Need divergence TIMES -> BEAST2 (-> divergence-dating). Need a model that is not built-in -> RevBayes. Deep phylogeny with suspected compositional heterogeneity / LBA -> PhyloBayes CAT-GTR (or IQ-TREE C60/PMSF in modern-tree-inference if too big for CAT or fast bootstrap is wanted).

## MCMC Convergence -- the Heart

Almost all Bayesian-phylo failures live here, and the non-obvious core is that scalar-parameter convergence and tree-topology convergence are DIFFERENT problems. Continuous parameters (tree length, gamma shape, rates, frequencies) live in a smooth low-dimensional space that mixes well; topology lives in the vast discrete space of (2n-5)!! unrooted trees where a chain can get stuck on one island, mix perfectly within it, post a beautiful trace and ESS for every scalar, and never visit a competing topological peak. Diagnose BOTH; topology is the harder, more-often-skipped one.

- Question A (scalars converged?): ESS, autocorrelation, PSRF on the `.p`/`.log` traces. Tools: Tracer, coda, MrBayes `sump`.
- Question B (the TREE distribution converged?): between-run split-frequency agreement (ASDSF, max split-freq diff), topological ESS. Tools: MrBayes `sumt` (live ASDSF), PhyloBayes `bpcomp`, RWTY (Warren 2017). Passing A and stopping is the single most common silent error.

What each diagnostic measures:
- ESS (effective sample size) = N / integrated autocorrelation time. Check PER parameter (the likelihood can have ESS=2000 while a nuisance rate has ESS=12). Tracer flags <200 yellow, <100 red.
- PSRF (Gelman-Rubin Rhat) compares between-run to within-run variance across >=2 runs; PSRF -> 1.00 at convergence. Requires multiple runs. Scalar-only (Question A).
- ASDSF (average standard deviation of split frequencies) = THE between-run topology metric in MrBayes, computed automatically when `nruns>=2`: for each bipartition above a minimum frequency, take the SD of its frequency across runs and average. Converged runs give the same frequency in both -> ASDSF -> 0. Printed live during `mcmc`; `stoprule=yes stopval=0.01` auto-halts. Companion: the MAX split-freq diff (worst single split) catches one unsettled clade that a low average hides.
- Multiple independent runs are mandatory: PSRF and ASDSF are between-run metrics, undefined with one run, and a single run can look perfectly stationary on a local peak. A single long run is never sufficient evidence of convergence.
- MC3 (Metropolis-coupled MCMC) is MrBayes' defense against tree-space trapping: 1 cold chain (sampled) + heated chains whose flattened posterior crosses valleys, with periodic state swaps. Tuning signal is the chain-swap acceptance rate (target ~20-70%); if near 0, chains too far apart -> lower `temp`; near 100%, too similar -> raise `temp`. BEAST2 and PhyloBayes do not use MC3 by default.

Convergence checklist (all must pass before shipping):
1. Run >= 2 independent runs from different starting trees.
2. ESS > 200 for EVERY parameter (posterior, prior, likelihood, and all model params), not just the likelihood.
3. PSRF ~ 1.00 (<= 1.01) for all scalars (MrBayes `sump`).
4. Trace plots stationary and well-mixed ("fuzzy caterpillar"), independent runs overlay (Tracer).
5. Topology converged: ASDSF < 0.01 (MrBayes) / bpcomp maxdiff < 0.1 (PhyloBayes), and check RWTY tree-space MDS that runs overlap (not separate clouds).
6. Burn-in set from the trace / cumulative split-freq plots, not a dogmatic percentage. If any check fails, run longer; do NOT just increase thinning.

## Priors That Bite

Defaults are not neutral. The branch-length prior is the one that changes conclusions. The classic MrBayes default before 3.2.3 put an i.i.d. Exponential(10) prior on each branch with no control over the SUM, so as taxon number grows the implied prior on total tree length grows and the posterior is pulled toward implausibly long trees with degraded mixing -- and the inflation can feed back into TOPOLOGY and node support, so it is not cosmetic (Brown 2010). The fix is the compound (gamma-)Dirichlet prior (Zhang 2012): a diffuse Gamma on the whole tree length, partitioned among branches by a Dirichlet, decoupling "how long is the tree" from "how is length distributed". It yields posterior tree lengths close to the ML estimate and is robust to its hyperparameters; it became the MrBayes default at 3.2.3+. Rule: never trust a default `exp(10)` brlenspr on datasets with many taxa or long branches -- use `unconstrained:gammadir(...)`; inflated tree length vs an ML reference points first at the branch-length prior. Two further notes: a uniform topology prior is NOT uniform on clades; and Bayes-factor model comparison is only valid under PROPER priors (an unbounded "uninformative" prior leaves the marginal likelihood undefined).

The star-tree paradox and short-internode overconfidence: when the true internal branch is near zero (an effective polytomy), PP does NOT settle toward the uninformative 1/3 among the three resolutions as data accumulate -- it behaves erratically and can drive toward HIGH support for an arbitrary resolution (Lewis 2005; the theory in Yang 2007). So a high PP on a clade subtended by a very short internal branch is exactly where Bayesian support is least trustworthy. Treat near-zero internodes as soft, cross-check against bootstrap, and consider a polytomy-allowing reversible-jump prior (Lewis 2005).

## Model Comparison Done Right

Bayesian model comparison compares MARGINAL likelihoods (the data probability integrated over all parameters under the model's priors) via Bayes factors. The marginal likelihood is a hard high-dimensional integral. The correct estimators are stepping-stone (Xie 2011) and path sampling, which sample a series of power posteriors interpolating prior (beta=0) to posterior (beta=1); stepping-stone is more accurate per step and is the default recommendation. Baele 2012 showed by simulation and empirically that both substantially outperform the harmonic-mean estimator.

The harmonic-mean estimator (HME) is discredited and must never select a model. It is dominated by the smallest likelihoods in the posterior sample (the prior-favored tail the posterior rarely visits), giving it effectively infinite variance -- it does not converge as samples are added, is unstable run-to-run, systematically overstates the marginal likelihood, and favors over-parameterized models. Interpret Bayes factors on the 2*ln(BF) scale (Kass & Raftery 1995): 2-6 positive, 6-10 strong, >10 very strong/decisive, where 2 lnBF = 2*(lnML_1 - lnML_2). BFs require proper priors. The reversible-jump alternative `lset nst=mixed` sidesteps explicit BFs by sampling the substitution model itself (the 203 GTR rate-class groupings) and reporting each model's posterior probability -- the principled way to account for substitution-model uncertainty by averaging.

### Run MrBayes and Verify Convergence Before Trusting the Tree

**Goal:** Produce a Bayesian phylogeny whose clade posteriors are trustworthy, gated on proven convergence rather than a single stationary-looking run.

**Approach:** Set a multiple-hit-correcting model and the compound-Dirichlet branch-length prior, run two MC3 runs, watch live ASDSF, then summarize only after the topology and scalar diagnostics pass.

```
begin mrbayes;
    lset nst=6 rates=invgamma;                          [ GTR+I+G; nst=mixed = rjMCMC model averaging ]
    prset brlenspr=unconstrained:gammadir(1,0.1,1,1);   [ compound Dirichlet, NOT exp(10): avoids tree-length inflation ]
    mcmc ngen=10000000 nruns=2 nchains=4 temp=0.1       [ 2 runs x (1 cold + 3 heated MC3 chains) ]
         samplefreq=1000 printfreq=1000 diagnfreq=5000
         stoprule=yes stopval=0.01;                     [ auto-halt when ASDSF < 0.01 (topology converged) ]
    sump burninfrac=0.25 relburnin=yes;                 [ scalar PSRF + ESS, discarding first 25% ]
    sumt burninfrac=0.25 relburnin=yes;                 [ consensus tree + clade PP + ASDSF ]
end;
```

After the run: confirm `sump` PSRF ~ 1.00 and ESS > 200 for every parameter, `sumt` ASDSF < 0.01 with a small max split-freq diff, and check tree-space convergence with RWTY (`analyze.rwty(list(run1=..., run2=...), burnin=25)`, then `makeplot.treespace`). Distrust any clade where PP is high but the bootstrap or concordance factor (modern-tree-inference) is low.

### Compare Two Models by Stepping-Stone

**Goal:** Select between two models (e.g. GTR+G vs GTR+I+G, or partition schemes) by marginal likelihood, never by the harmonic mean.

**Approach:** Estimate each model's marginal log-likelihood by stepping-stone sampling, then convert the difference to a Kass-Raftery Bayes factor.

```
[ run once per model on the same proper priors; nsteps = power-posterior stones ]
ss ngen=1000000 nsteps=50 diagnfreq=1000;
[ MrBayes prints the stepping-stone marginal log-likelihood; record it per model ]
[ 2 lnBF = 2 * (lnML_model1 - lnML_model2); interpret on the Kass-Raftery scale ]
```

BEAST2: install the `MODEL_SELECTION` package and run `PathSampler` (path sampling / stepping-stone); RevBayes: `powerPosterior()` + `steppingStoneSampler()`. All require proper priors, or the marginal likelihood is undefined.

## Site-Heterogeneous CAT Models for Deep Phylogeny

Standard models (GTR+G, LG/WAG+G) assume all sites share one set of equilibrium frequencies -- they are site-HOMOGENEOUS. Real proteins are not: a buried hydrophobic site and a surface charged site have different profiles. At DEEP timescales this misleads, because saturated sites convergently acquire similar compositions in unrelated lineages and a homogeneous model misreads convergent composition as shared ancestry -> long-branch attraction with HIGH PP (the overconfidence-under-misspecification mechanism made concrete). The answer is CAT / CAT-GTR (Lartillot 2004): an infinite-mixture (Dirichlet-process) model assigning sites to an unknown number of categories, each with its own amino-acid frequency profile, all inferred from the data; CAT-GTR adds one shared GTR exchangeability matrix (the PhyloBayes default with 4-category gamma). It is far more robust to LBA at depth than homogeneous models, at the cost of slow convergence (millions of cycles, days-weeks), which is why PhyloBayes-MPI parallelizes it (Lartillot 2013).

CAT chains converge slowly, so diagnostics are mandatory (run >= 2 chains with different names): `bpcomp -x <burnin> <every> chain1 chain2` reports maxdiff (the largest bipartition-frequency discrepancy across chains, the topology metric) and writes a pooled consensus; `tracecomp -x <burnin> chain1 chain2` reports per-statistic effsize and rel_diff (a PSRF analog). Thresholds: maxdiff < 0.1 AND effsize > 300 = converged; maxdiff < 0.3 AND effsize > 50 = acceptable; otherwise keep running. The ML treatment of the same artifact is IQ-TREE C60/PMSF (Wang 2018): fit the C60 profile mixture once, fix each site's posterior-mean profile, then do fast tree search and bootstrap. CAT-GTR gives a posterior (slow, MPI); PMSF gives bootstrap (fast, scales to huge matrices) -- different output, same disease. Routes to modern-tree-inference.

```bash
mpirun -np 8 pb_mpi -d alignment.phy -cat -gtr -dgam 4 chain1   # CAT-GTR + discrete gamma
mpirun -np 8 pb_mpi -d alignment.phy -cat -gtr -dgam 4 chain2   # second independent chain
bpcomp -x 1000 10 chain1 chain2     # maxdiff (topology); writes bpcomp.con.tre
tracecomp -x 1000 chain1 chain2     # effsize + rel_diff (scalars)
```

## Per-Method Failure Modes

### Non-Convergence Reported as a Result
**Trigger:** A single short chain, a stationary-looking trace, a point estimate shipped with no ESS / PSRF / ASDSF and no second run.
**Mechanism:** The "result" is an arbitrary draw from a chain that never demonstrably sampled the posterior; the clade PPs are an artifact of where the chain happened to sit.
**Symptom:** No diagnostics reported; or low ESS / PSRF > 1.05 / ASDSF > 0.01 quietly ignored.
**Fix:** Always >= 2 runs; gate on ESS > 200 (all params) AND ASDSF < 0.01 / maxdiff < 0.1; inspect in Tracer/RWTY; never ship without the diagnostics.

### Scalar Convergence Mistaken for Topology Convergence
**Trigger:** Every scalar has ESS > 1000 and PSRF = 1.00, so convergence is declared.
**Mechanism:** The chain is trapped on one tree-space island, mixing perfectly within it while never sampling a competing topology; scalars are necessary but not sufficient.
**Symptom:** Perfect Tracer traces but ASDSF stuck high, or RWTY tree-space MDS shows two separate clouds for the two runs.
**Fix:** Always run a TOPOLOGY diagnostic (ASDSF / bpcomp maxdiff / RWTY MDS), not just Tracer.

### Branch-Length Prior Inflation (Prior Domination)
**Trigger:** Default `exp(10)` brlen prior (old MrBayes) on many taxa or long branches, or a too-strong tree/clock prior on weak data.
**Mechanism:** The i.i.d.-per-branch prior places mass on long total tree length; the posterior converges to the WRONG distribution, and inflated branch lengths can distort topology and support.
**Symptom:** Posterior tree length far exceeds the ML estimate; topology shifts when the prior is changed.
**Fix:** Use `unconstrained:gammadir(...)`; do a prior-sensitivity check (sample the prior alone, vary hyperparameters); compare tree length to an ML reference.

### Harmonic-Mean Model Selection
**Trigger:** Selecting a substitution/clock/partition model by HME (or AICM) Bayes factors.
**Mechanism:** The HME has effectively infinite variance, is unstable, and favors over-parameterized models -> the wrong model is chosen.
**Symptom:** Bayes factors that change on rerun, or a consistent preference for the most complex model.
**Fix:** Stepping-stone or path sampling for marginal likelihoods; interpret with Kass-Raftery 2lnBF thresholds; ensure proper priors.

### PP Overconfidence Under Misspecification
**Trigger:** Reporting PP = 1.0 as proof, especially site-heterogeneous data analyzed under a homogeneous model.
**Mechanism:** A Bayesian analysis conditions on the model; a misspecified model has no way to hedge, so the posterior concentrates with false confidence on LBA-driven clades.
**Symptom:** PP = 1.0 where the bootstrap is 55%, or two conflicting topologies each with high PP across analyses.
**Fix:** Report the model; cross-check PP against bootstrap (sharp disagreement = warning); use CAT-GTR / PMSF for deep data; treat PP = 1.0 as "decisive under THIS model", not truth.

### CAT Non-Convergence at Scale
**Trigger:** Stopping a PhyloBayes CAT run too early because wall-clock budget ran out.
**Mechanism:** CAT chains converge slowly (millions of cycles); maxdiff is still ~0.3 and effsize < 50 when the tree is read out.
**Symptom:** bpcomp maxdiff well above 0.1, tracecomp effsize below 300.
**Fix:** Run long, >= 2 chains, gate on maxdiff < 0.1 AND effsize > 300; budget days-weeks of MPI time; consider removing the fastest sites or recoding.

## Quantitative Thresholds

| Quantity | Threshold | Source |
|----------|-----------|--------|
| ESS per parameter | > 200 (floor 100; 500-1000 for reported point estimates) | Rambaut 2018 |
| PSRF / Rhat | ~ 1.00, accept <= 1.01; > 1.05 = not converged | Ronquist 2012 |
| ASDSF (MrBayes between-run topology) | < 0.01 for a confident result; < 0.05 adequate for hard data | Ronquist 2012 |
| Max split-freq diff | small, consistent with ASDSF < 0.01 | Ronquist 2012 |
| bpcomp maxdiff (PhyloBayes topology) | < 0.1 good; < 0.3 acceptable | Lartillot 2013 |
| tracecomp effsize (PhyloBayes scalars) | > 300 good; > 50 acceptable; rel_diff small (<~0.1) | Lartillot 2013 |
| Burn-in | discard 10-25% (data-driven; up to 50% for slow chains) | Ronquist 2012 |
| MC3 chain-swap acceptance | ~20-70% between adjacent chains; tune `temp` if outside | Ronquist 2012 |
| Bayes factor (2 lnBF) | 2-6 positive, 6-10 strong, > 10 very strong/decisive | Kass & Raftery 1995 |
| Independent runs | minimum 2 (4 for difficult data) | Ronquist 2012 |
| Posterior probability | >= 0.95 nominal but overconfident under misspecification; PP = 1.0 != proof | Suzuki 2002 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Convergence declared on one run | PSRF/ASDSF undefined with a single run | run nruns >= 2; gate on between-run metrics |
| Perfect ESS but wrong PPs | tree-space trapping not caught by scalars | add a topology diagnostic (ASDSF / bpcomp / RWTY MDS) |
| Posterior tree length >> ML | default `exp(10)` branch-length prior | switch to `unconstrained:gammadir(...)` |
| Model choice flips on rerun | harmonic-mean estimator used | use stepping-stone / path sampling |
| Bayes factor is undefined / arbitrary | an improper "uninformative" prior | make all priors proper before SS/PS |
| PP = 1.0 on an LBA clade at depth | site-heterogeneous data under a homogeneous model | use PhyloBayes CAT-GTR or IQ-TREE PMSF |
| High PP on a near-zero internode | star-tree paradox fabricates resolution | treat the internode as soft; consider a polytomy prior |
| Low ESS after thinning more | thinning discards information, does not raise ESS | run more generations, not higher samplefreq |

## References

Ronquist F, Teslenko M, van der Mark P, Ayres DL, Darling A, Hohna S, Larget B, Liu L, Suchard MA, Huelsenbeck JP. 2012. MrBayes 3.2: efficient Bayesian phylogenetic inference and model choice across a large model space. *Systematic Biology* 61(3):539-542.
Bouckaert R, Vaughan TG, Barido-Sottani J, Duchene S, Fourment M, et al. 2019. BEAST 2.5: an advanced software platform for Bayesian evolutionary analysis. *PLoS Computational Biology* 15(4):e1006650.
Hohna S, Landis MJ, Heath TA, Boussau B, Lartillot N, Moore BR, Huelsenbeck JP, Ronquist F. 2016. RevBayes: Bayesian phylogenetic inference using graphical models and an interactive model-specification language. *Systematic Biology* 65(4):726-736.
Lartillot N, Philippe H. 2004. A Bayesian mixture model for across-site heterogeneities in the amino-acid replacement process. *Molecular Biology and Evolution* 21(6):1095-1109.
Lartillot N, Rodrigue N, Stubbs D, Richer J. 2013. PhyloBayes MPI: phylogenetic reconstruction with infinite mixtures of profiles in a parallel environment. *Systematic Biology* 62(4):611-615.
Wang HC, Minh BQ, Susko E, Roger AJ. 2018. Modeling site heterogeneity with posterior mean site frequency profiles accelerates accurate phylogenomic estimation. *Systematic Biology* 67(2):216-235.
Warren DL, Geneva AJ, Lanfear R. 2017. RWTY (R We There Yet): an R package for examining convergence of Bayesian phylogenetic analyses. *Molecular Biology and Evolution* 34(4):1016-1020.
Rambaut A, Drummond AJ, Xie D, Baele G, Suchard MA. 2018. Posterior summarization in Bayesian phylogenetics using Tracer 1.7. *Systematic Biology* 67(5):901-904.
Xie W, Lewis PO, Fan Y, Kuo L, Chen MH. 2011. Improving marginal likelihood estimation for Bayesian phylogenetic model selection. *Systematic Biology* 60(2):150-160.
Baele G, Lemey P, Bedford T, Rambaut A, Suchard MA, Alekseyenko AV. 2012. Improving the accuracy of demographic and molecular clock model comparison while accommodating phylogenetic uncertainty. *Molecular Biology and Evolution* 29(9):2157-2167.
Kass RE, Raftery AE. 1995. Bayes factors. *Journal of the American Statistical Association* 90(430):773-795.
Brown JM, Hedtke SM, Lemmon AR, Lemmon EM. 2010. When trees grow too long: investigating the causes of highly inaccurate Bayesian branch-length estimates. *Systematic Biology* 59(2):145-161.
Zhang C, Rannala B, Yang Z. 2012. Robustness of compound Dirichlet priors for Bayesian inference of branch lengths. *Systematic Biology* 61(5):779-784.
Suzuki Y, Glazko GV, Nei M. 2002. Overcredibility of molecular phylogenies obtained by Bayesian phylogenetics. *PNAS* 99(25):16138-16143.
Erixon P, Svennblad B, Britton T, Oxelman B. 2003. Reliability of Bayesian posterior probabilities and bootstrap frequencies in phylogenetics. *Systematic Biology* 52(5):665-673.
Lewis PO, Holder MT, Holsinger KE. 2005. Polytomies and Bayesian phylogenetic inference. *Systematic Biology* 54(2):241-253.
Yang Z. 2007. Fair-balance paradox, star-tree paradox, and Bayesian phylogenetics. *Molecular Biology and Evolution* 24(8):1639-1655.

## Related Skills

- modern-tree-inference - ML inference, bootstrap/SH-aLRT support, concordance factors, and IQ-TREE C60/PMSF
- divergence-dating - BEAST2 clock models, calibration, and time-scaled posteriors
- species-trees - coalescent species-tree estimation when ILS dominates
- tree-io - reading and summarizing MrBayes/BEAST2 trees without dropping posteriors and HPDs
<!-- END FILE: phylogenetics/bayesian-inference/SKILL.md -->

## 子目录：phylogenetics/distance-calculations

<!-- BEGIN FILE: phylogenetics/distance-calculations/SKILL.md -->
---
name: bio-phylo-distance-calculations
description: Build model-corrected evolutionary distance matrices and distance trees (NJ, BIONJ, FastME, UPGMA) with Biopython Bio.Phylo plus R ape/phangorn/FastME. Covers why a distance is a model-corrected estimate of substitutions per site that undercounts raw because of multiple/back/parallel hits (saturation); why the matrix discards the per-site information ML keeps; the LogDet/paralinear fix for compositional heterogeneity; the UPGMA molecular-clock trap; and the Bio.Phylo landmine that DistanceCalculator offers only identity/matrix distances, not JC/K80/TN93. Use when computing a distance matrix, building a fast NJ/FastME tree, seeding an ML search, barcoding, or testing substitution saturation before a deep tree. Routes ML and starting-tree work to modern-tree-inference, alignment quality to alignment/alignment-io, and tree I/O to tree-io.
tool_type: mixed
primary_tool: Bio.Phylo.TreeConstruction
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+. Model-corrected alternatives: ape 5.8+, phangorn, FastME, scikit-bio.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(module.function)` to check signatures
- R: `packageVersion('ape')` then `?dist.dna` to verify model strings
- CLI: `fastme --version` then `fastme --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Bio.Phylo `DistanceCalculator` offers only identity / substitution-matrix distances and has NO model-based JC/K80/TN93; for model-corrected DNA distances use ape `dist.dna(model=...)` (introspect its model list and `gamma=` support if the version differs).

# Distance Calculations -- Distance Erases the Information ML Keeps; the Correction Is the Model

**"Build a tree from my alignment"** -> Estimate model-corrected pairwise distances, then cluster them into a tree, knowing the correction is where the biology lives and the matrix discards what ML uses.
- Python: `DistanceCalculator(...).get_distance(aln)` then `DistanceTreeConstructor().nj(dm)` (Bio.Phylo, identity-only)
- R: `dist.dna(x, model='TN93')` then `fastme.bal(d)` / `nj(d)` (ape, model-corrected)

Scope: computing evolutionary distance matrices and building/bootstrapping distance trees (NJ, BIONJ, FastME, UPGMA), and testing saturation before trusting them. ML inference, model selection, and where NJ seeds an ML search -> modern-tree-inference. Alignment quality and trimming, which gate every distance -> alignment/alignment-io. Reading/writing/converting the trees these methods emit -> tree-io. Rooting and pruning -> tree-manipulation.

## The Single Most Important Modern Insight

A distance-based phylogeny is built in two lossy steps and both losses are silent. First, a distance is a model-corrected estimate of expected substitutions per site, not the observed proportion of differing sites; second, the matrix collapses each sequence pair to one scalar and discards the site-pattern information that maximum likelihood evaluates. Distance methods are therefore fast but doubly limited -- by how good the correction is, and by what a matrix of scalars can encode -- and they are structurally incapable of using the per-site signal that makes ML the gold standard for hard problems. Three load-bearing facts:

1. **The correction is the whole biological content.** The raw p-distance (proportion of differing sites) systematically UNDERCOUNTS true divergence because every site that mutated twice (back-substitution), in parallel on both lineages, or to a third state (multiple hit) is missed, and the gap grows without bound toward saturation. The algorithm downstream (NJ, FastME) is just arithmetic on the numbers handed to it; feed it p-distances on divergent data and it returns a confidently wrong tree, fast.
2. **The matrix throws away what ML keeps.** Two completely different alignments can produce the same distance matrix and therefore the same tree. ML never collapses the data, so it cannot be fooled this way; once the matrix exists, which sites drove the divergence, among-site rate heterogeneity, and competing site-pattern signal are gone.
3. **Consistency is conditional, not a guarantee.** NJ is statistically consistent -- it returns the true tree as sequence length grows -- but only if the input distances are additive and correctly estimated. A consistent algorithm fed biased (saturated, misspecified) distances converges confidently on the WRONG tree. "I used NJ so it is consistent" is not a defense; the correction is exactly what most users get wrong.

## Distance Corrections

Every nucleotide correction inverts the probability that a site differs under a model, so as p approaches the equilibrium difference (0.75 for equal base frequencies under JC) the correction diverges to infinity and its variance explodes -- the mathematical face of saturation.

| Correction | Corrects for | When to use | ape model |
|---|---|---|---|
| p-distance (raw / Hamming) | nothing | very shallow / barcoding; saturation plots | `'raw'`, `'N'` |
| Jukes-Cantor (JC69) | multiple hits, one rate | minimal correction, quick sanity tree | `'JC69'` |
| Kimura 2-param (K80) | + transition/transversion bias | default DNA quick distance | `'K80'` (default) |
| Tamura-Nei (TN93) | + two transition rates + unequal base freqs | mtDNA, richest closed-form | `'TN93'` |
| LogDet / paralinear | COMPOSITIONAL heterogeneity (non-stationary, general Markov) | GC drift across taxa; compositional attraction suspected | `'logdet'`, `'paralin'` |
| Gamma-corrected | among-site rate variation (ASRV) | alpha small (< ~1); long branches | `dist.dna(..., gamma=alpha)` |
| Protein matrix (LG/WAG/JTT/PAM) | amino-acid replacement, multiple hits | protein data (use phangorn `dist.ml`) | n/a (LG/WAG modern; PAM legacy) |

LogDet / paralinear (Lockhart et al. 1994; Lake 1994) is the non-obvious one: JC/K80/TN93 all assume stationarity (constant base composition across the tree), and when composition drifts (thermophiles, AT-rich insect mtDNA, GC-rich chloroplasts) every stationary correction groups taxa by base composition rather than ancestry -- compositional attraction, a sibling of long-branch attraction that fools NJ and stationary-model ML alike. LogDet is computed from the determinant of the 4x4 pairwise divergence matrix and is consistent under the general Markov model, at the cost of needing long sequences and not easily taking gamma. If a topology flips between JC and LogDet, suspect compositional heterogeneity.

## Algorithm Decision

| Algorithm | Criterion | Clock? | Cost | Use / pitfall |
|---|---|---|---|---|
| UPGMA | average-linkage clustering | ASSUMES strict clock (ultrametric) | O(n^2) | avoid for molecular phylo; wrong TOPOLOGY under rate variation; serotyping/dendrograms only |
| NJ (Saitou & Nei 1987) | greedy balanced minimum evolution (Q-matrix) | no | O(n^3) | fast default; consistent ONLY if distances correct/additive; barcoding, large n |
| BIONJ (Gascuel 1997) | NJ + variance-weighted reduction | no | O(n^3) | better than NJ on large/noisy distances; a common ML starting-tree generator (IQ-TREE2/RAxML-NG default to parsimony starts) |
| FastME (Lefort et al. 2015) | balanced minimum evolution + NNI/SPR search | no | ~NJ-speed | the modern best distance tree; actively searches, not a single greedy pass |

UPGMA is the key warning: it forces every tip equidistant from the root, which molecular data essentially never satisfies because lineages evolve at different rates. A fast-evolving lineage gets pulled toward the tips and grouped by total divergence rather than true ancestry -- a clustering-by-rate artifact analogous to long-branch attraction. Flat rule: do not use UPGMA for molecular phylogeny unless a clock is independently established. NJ does not assume a clock because its Q-matrix corrects each pairwise distance for that taxon's average divergence to everyone else. NJ/BIONJ/FastME can seed ML searches: some ML programs build a BIONJ or ME starting tree in O(n^3) before likelihood NNI/SPR (though IQ-TREE2 and RAxML-NG default to parsimony starting trees), so this machinery still has a place in an all-ML pipeline.

## Tool Taxonomy

| Tool (lang) | Distance step | Tree step | Note |
|---|---|---|---|
| Bio.Phylo.TreeConstruction (Py) | `DistanceCalculator` identity / BLOSUM / PAM matrices ONLY | `DistanceTreeConstructor().nj()` / `.upgma()` | NO JC/K80/TN93; `'identity'` is p-distance, named matrices are score distances |
| ape (R) | `dist.dna(model=, gamma=)` -- full menu incl. LogDet, gamma | `nj()`, `bionj()`, `fastme.bal()`, `fastme.ols()` | the reference engine for real corrections |
| phangorn (R) | `dist.ml(model=)` -- DNA JC69/F81 only, but all protein matrices | `upgma()`, `NJ()` | the natural choice for protein distances |
| FastME (CLI) | JC/K2P/F84/TN93/LogDet/protein | NJ/BIONJ/BME/OLS-ME + NNI/SPR + bootstrap | standalone for very large n; `-m B` = balanced ME |
| scikit-bio (Py) | none (requires a pre-corrected matrix) | `skbio.tree.nj(dm)` | pure-Python NJ; `neg_as_zero=` since 0.6.3 |

Loud flag, the second flat rule: Bio.Phylo and scikit-bio do NOT correct for multiple hits -- their built-in distance is p-distance or score-based. Presenting Bio.Phylo's `'identity'` distance as a "Jukes-Cantor tree" is a common and wrong shortcut. For a real correction, compute the matrix in ape/FastME (or compute it yourself) and pass it in.

## Build a Model-Corrected Distance Matrix and NJ Tree

**Goal:** Turn an alignment into a tree, contrasting Bio.Phylo's identity-only path against ape's model-corrected path.

**Approach:** In Python use Bio.Phylo for the NJ/UPGMA algorithm and pure-Python I/O, but treat its distance as an uncorrected p-distance; for any divergent data move the distance step to ape `dist.dna`, then cluster with FastME (best) or NJ.

```python
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

aln = AlignIO.read('alignment.fasta', 'fasta')
calc = DistanceCalculator('identity')        # identity-only: this is a p-distance, NOT a JC/K80 correction
dm = calc.get_distance(aln)                   # multiple/back/parallel hits are NOT corrected here
tree = DistanceTreeConstructor().nj(dm)       # NJ algorithm is correct; the DISTANCES are the limitation
# For a model-corrected distance, build the matrix in ape (below) and pass it to skbio/Bio.Phylo, or stay in R.
```

```r
library(ape)
aln <- read.dna('alignment.fasta', format = 'fasta')
d <- dist.dna(aln, model = 'TN93', gamma = 0.5)   # model-corrected; gamma applies ASRV (alpha < 1 = strong)
tree <- fastme.bal(d, nni = TRUE, spr = TRUE)     # balanced minimum evolution: the modern best distance tree
# nj(d) / bionj(d) are the faster single-pass alternatives; bionj seeds ML searches
```

## Pre-flight: Test Substitution Saturation

**Goal:** Decide whether the data retain phylogenetic signal before trusting any deep distance tree.

**Approach:** Compute Xia's index of substitution saturation Iss and compare it to the simulation-derived critical value Iss.c; a saturation plot of transitions against a corrected distance is the visual companion.

```r
library(ape)                    # the formal entropy-based Iss vs Iss.c test lives in DAMBE; this is the ape/base-R saturation plot
d_jc  <- dist.dna(aln, model = 'JC69')
ts_tv <- dist.dna(aln, model = 'TS')   # transitions; plot against d_jc -- a PLATEAU means saturated, signal erased
plot(d_jc, ts_tv)                       # unsaturated = roughly linear; bent-over transition curve = drop those sites
# Interpretation gate (Xia 2003): Iss < Iss.c => signal retained (usable); Iss >= Iss.c => substantially saturated, do not use.
```

## Bootstrap a Distance Tree

**Goal:** Quantify how reproducible each clade is under resampling -- precision, not accuracy.

**Approach:** Resample alignment columns with replacement, recompute the matrix with the SAME correction, rebuild with the SAME algorithm, and summarize clade frequencies on a majority-rule consensus.

```r
library(ape)
boot <- boot.phylo(tree, aln, function(x) fastme.bal(dist.dna(x, model = 'TN93')), B = 500)
# 100-1000 replicates standard; support measures SAMPLING stability only -- it cannot detect a bias in the distances
```

In Python, Bio.Phylo's `bootstrap_consensus(aln, 100, DistanceTreeConstructor(calc, 'nj'), majority_consensus)` does the same on the identity distance (same correction caveat).

## When Distance Is Legitimate vs a Trap

Legitimate or preferred: a quick exploratory / sanity tree before a long ML run; very large n (thousands+ tips) where ML is infeasible (large-scale barcoding, OTU/pangenome trees); barcoding and population-level shallow data, where saturation is negligible and the per-site information ML keeps adds little (NJ on K2P distances is the literal DNA-barcoding standard); and as the starting tree for ML/Bayesian search.

A trap, do not: publication-grade deep phylogeny or formal hypothesis testing (dating, selection, contested deep nodes) -- use ML or Bayesian with model selection; any dataset that fails a saturation test (Xia Iss >= Iss.c), which no algorithm rescues; data with strong compositional heterogeneity unless using LogDet/paralinear; and mistaking consistency for a guarantee -- NJ is consistent only with correct distances, and saturation/misspecification break it exactly as they break ML.

## Per-Method Failure Modes

### Saturation Makes Distances Plateau and Mislead at Depth
**Trigger:** Deep divergences with many pairwise p-distances above ~0.5; transitions exhausted while transversions still climb.
**Mechanism:** So many superimposed substitutions accumulate that observed differences approach the random expectation; the correction inflates violently near its singularity and carries no remaining signal about deep splits.
**Symptom:** Corrected distances explode and become unstable; the saturation plot's transition curve flattens; deep nodes are unstable across models.
**Fix:** Run the Xia Iss test; exclude transitions, third codon positions, or saturated partitions; do not build a deep distance (or ML) tree on saturated data.

### UPGMA Returns the Wrong Topology Under Rate Variation
**Trigger:** Lineages evolving at different rates analyzed with UPGMA.
**Mechanism:** UPGMA forces an ultrametric tree (clock), so a fast-evolving lineage is pushed toward the tips and grouped by total divergence, not ancestry.
**Symptom:** Topology differs from an NJ tree on the same matrix; fast lineages cluster together.
**Fix:** Use NJ or FastME; never UPGMA for molecular phylogeny without an independently established clock.

### Identity / Uncorrected Distance Model on Divergent Data
**Trigger:** Bio.Phylo `'identity'` or ape `'raw'` on anything beyond shallow divergence; calling it a "JC tree".
**Mechanism:** No multiple-hit correction, so divergence is undercounted nonlinearly and worst on the longest branches, amplifying long-branch artifacts.
**Symptom:** Branch lengths and topology shift when a real correction is applied; long-branch taxa attract.
**Fix:** Use ape `dist.dna(model='TN93')` or a gamma correction; for compositional skew use LogDet; for protein use phangorn `dist.ml(model='LG')`.

### Bootstrap on a Method That Discarded the Per-Site Information
**Trigger:** High distance-NJ bootstrap on saturated or compositionally biased data.
**Mechanism:** Resampling removes sampling noise, not a systematic bias baked into the distances, so the wrong split reproduces every replicate.
**Symptom:** Confident, reproducible support on a clade that moves when the correction or saturated sites change.
**Fix:** Bootstrap measures precision, not accuracy; fix the distances (model + saturation) first.

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|---|---|---|
| p-distance saturation onset | unstable as nucleotide p -> ~0.5-0.6; singularity at 0.75 (equal base freqs) | many pairwise p > ~0.5 = red flag, run a saturation test |
| Xia substitution-saturation test | Iss < Iss.c => usable; Iss >= Iss.c (esp. asymmetric Iss.c, the stricter bar) => do not use | Xia et al. 2003 (DAMBE) |
| JC/correction singularity | log argument -> 0 as p -> 0.75 | d and its variance diverge to infinity |
| Gamma shape | alpha < ~1 = strong ASRV, materially changes distances/topology | ignoring ASRV inflates long-branch artifacts |
| ts/tv ratio | commonly 2-15 (~15 primate mtDNA control region) | large ratios make K80/TN93 over JC matter (Tamura & Nei 1993) |
| Bootstrap replicates | 100-1000; clades < ~70% conventionally unsupported | precision not truth (Hillis & Bull 1993) |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| NJ tree on `model='identity'` called a Jukes-Cantor tree | DistanceCalculator does NOT do JC/K80/TN93 | compute the corrected matrix in ape/FastME, pass it as a matrix |
| Corrected distances explode / `NaN` | p near or above 0.75 singularity (saturation) | test saturation; drop saturated sites; do not trust deep distances |
| UPGMA tree disagrees with NJ | UPGMA clock assumption violated by rate variation | use NJ/FastME for molecular data |
| Unrelated GC-rich taxa group together; topology flips JC vs LogDet | non-stationary composition under a stationary correction | use LogDet/paralinear or a non-stationary ML model |
| LogDet returns `NaN` / undefined | short sequences drive det(F) <= 0 | use longer alignments or a stationary correction |
| High bootstrap on a wrong clade | resampling masks a systematic bias in the distances | fix the model/saturation; support is precision, not accuracy |

## References

Saitou N, Nei M. 1987. The neighbor-joining method: a new method for reconstructing phylogenetic trees. *Molecular Biology and Evolution* 4(4):406-425.
Gascuel O. 1997. BIONJ: an improved version of the NJ algorithm based on a simple model of sequence data. *Molecular Biology and Evolution* 14(7):685-695.
Lefort V, Desper R, Gascuel O. 2015. FastME 2.0: a comprehensive, accurate, and fast distance-based phylogeny inference program. *Molecular Biology and Evolution* 32(10):2798-2800.
Xia X, Xie Z, Salemi M, Chen L, Wang Y. 2003. An index of substitution saturation and its application. *Molecular Phylogenetics and Evolution* 26(1):1-7.
Lockhart PJ, Steel MA, Hendy MD, Penny D. 1994. Recovering evolutionary trees under a more realistic model of sequence evolution. *Molecular Biology and Evolution* 11(4):605-612.
Lake JA. 1994. Reconstructing evolutionary trees from DNA and protein sequences: paralinear distances. *PNAS* 91(4):1455-1459.
Tamura K, Nei M. 1993. Estimation of the number of nucleotide substitutions in the control region of mitochondrial DNA in humans and chimpanzees. *Molecular Biology and Evolution* 10(3):512-526.
Schliep KP. 2011. phangorn: phylogenetic analysis in R. *Bioinformatics* 27(4):592-593.
Hillis DM, Bull JJ. 1993. An empirical test of bootstrapping as a method for assessing confidence in phylogenetic analysis. *Systematic Biology* 42(2):182-192.

## Related Skills

- modern-tree-inference - ML inference, model selection, and where a BIONJ/ME distance tree seeds the ML search
- tree-manipulation - rooting and pruning the unrooted trees NJ/FastME emit
- tree-io - reading, writing, and converting the trees these methods produce
- alignment/alignment-io - the alignment whose quality gates every distance; filter ambiguous blocks first
<!-- END FILE: phylogenetics/distance-calculations/SKILL.md -->

## 子目录：phylogenetics/divergence-dating

<!-- BEGIN FILE: phylogenetics/divergence-dating/SKILL.md -->
---
name: bio-phylo-divergence-dating
description: Estimate divergence times under molecular-clock models with BEAST2, MCMCTree/PAML, TreePL, and LSD2, framing a date as a product of the calibration prior and the clock model far more than of the sequence data. Covers why branch length = rate x time is nonidentifiable so only calibrations convert relative rate-time into absolute age; why the effective (marginal) prior on a calibrated node differs from the density specified, mandating a sample-from-prior run; the fossil-as-minimum rule, soft bounds, tip-dating, and the fossilized birth-death process; the temporal-signal check (TempEst root-to-tip regression + date-randomization) required before dating viruses or ancient DNA; and clock-model choice via the coefficient of variation. Use when dating nodes, calibrating with fossils or sampling dates, choosing a clock or dating engine, or routing topology to modern-tree-inference, posteriors to bayesian-inference, and rooting to tree-manipulation.
tool_type: mixed
primary_tool: BEAST2
---

## Version Compatibility

Reference examples tested with: BEAST2 2.7+, MCMCTree/PAML 4.10+, TreePL 1.0+, TempEst 1.5+, LSD2 (IQ-TREE 2.2+ `--date`).

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `beast -version`, `mcmctree` (PAML), `treePL`, `iqtree2 --version` then the tool's `-help`/`--help` to confirm flags
- Python: `pip show biopython dendropy` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

BEAST2 prior-only is `sampleFromPrior="true"`; the MCMCTree equivalent is `usedata = 0`. MCMCTree calibration syntax is `B()/L()/U()` in the tree file, not `>`/`<`. FBD tip-dating needs the BEAST2 SA package.

# Divergence Time Estimation -- A Date Is Mostly the Calibration Prior, Not the Sequence

**"Estimate when these lineages diverged"** -> Convert a relative rate-time tree into absolute ages using external calibrations, then report the posterior, not a point.
- CLI: BEAST2 (BEAUti XML) for full posteriors, FBD, and tip-dating
- CLI: MCMCTree (PAML) for genome-scale data via approximate likelihood
- CLI: TreePL / LSD2 for very large trees (point estimates / fast phylodynamics)

Scope: converting a rooted, branch-length tree into absolute node ages -- clock models, calibrations, dating engines, and the temporal-signal and effective-prior checks. Topology, model selection, and support -> modern-tree-inference. Posterior distributions, MCMC convergence, and site-heterogeneous models -> bayesian-inference. The clock-based rooting concept and re-rooting -> tree-manipulation. Reading/writing the dated MCC tree without dropping HPD intervals -> tree-io. Phylodynamic population-size / Re estimation -> epidemiological-genomics/phylodynamics.

## The Single Most Important Modern Insight

A divergence date is a product of the calibration priors and the clock model far more than of the sequence data. A branch length is the product b = rate x time (expected substitutions per site); the likelihood depends on b alone, so the pair (rate, time) is nonidentifiable -- doubling every rate and halving every time leaves the likelihood unchanged. Sequences therefore carry information about the relative rate-time tree only, and calibrations are the one thing that converts it to absolute millions of years. The posterior on a node age is consequently dominated by the (often subjective) calibration prior and by how the tree prior and neighboring calibrations reshape it. Three load-bearing facts:

1. **More sequence data does not escape the calibration.** Adding genes sharpens the relative tree but the residual uncertainty in node ages is bounded below by calibration uncertainty; a precise posterior on a badly placed fossil is a precise estimate of the wrong age (dos Reis and Yang 2011; see the infinite-sites plot below).
2. **The honest practice is to run the MCMC sampling from the prior (no data) and report the effective prior.** Topological ordering and neighboring calibrations truncate each specified density, so the marginal (effective) prior the model actually uses is generically NOT the density typed in (Heled and Drummond 2012; Warnock et al. 2012). Report three numbers per calibrated node: specified prior, effective prior, posterior.
3. **A tight credible interval is not evidence the data nailed the age.** If the posterior coincides with the effective prior, the data added nothing and the prior is being reported back; tightness usually traces to a tight (or mutually truncating) prior, not to the molecular signal (Brown and Smith 2018).

## Clock Model Selection

The clock governs how substitution rate varies across branches; choosing it wrong biases dates and misstates their uncertainty. Choose by testing clocklikeness, not by defaulting either way.

| Model | Assumption | When | Diagnostic |
|-------|------------|------|------------|
| Strict | one rate for the whole tree | clocklike data: intraspecific, or short-timescale viral, when a clock test does not reject | most efficient; tightest justified CIs |
| UCLN (uncorrelated lognormal) | each branch rate drawn independently from a lognormal | field default for multi-species data with rate variation | the `ucld.stdev` / coefficient-of-variation diagnostic |
| UCED (uncorrelated exponential) | branch rates drawn from an exponential | larger, less-Gaussian rate swings | available; rarely the first choice |
| Autocorrelated (ACLN) | descendant rate centered on parent (Brownian log-rate; Thorne et al. 1998) | deep trees where rate is heritable (generation time, metabolism); MCMCTree default | rate-variance `sigma2` (MCMCTree) |
| Random local clocks | a few inferred, discrete rate-shift points | episodic / clade-specific rate shifts (Drummond and Suchard 2010) | estimates where and how many shifts |

Relaxed-clock work was established by Drummond et al. 2006 (uncorrelated relaxed clocks, "dating with confidence"). The single most useful BEAST2 relaxed-clock diagnostic is the coefficient of variation (CoV) of branch rates, derived from `ucld.stdev`: a CoV posterior abutting 0 (`ucld.stdev` near 0) means rates are effectively constant and a strict clock suffices (gain precision by simplifying); a CoV clearly above 0 with 0 excluded means the relaxed clock is doing necessary work and a strict clock would be falsely precise. If the `ucld.stdev` posterior just recovers its prior, the data cannot indicate how clocklike the lineages are -- report that. Use the CoV for a quick read, but decide strict-vs-relaxed formally by marginal-likelihood comparison (path sampling / stepping-stone).

## Calibration Strategy

Calibrations are the dominant input. The bedrock rule: a fossil is a MINIMUM, not a point -- a clade is at least as old as a fossil assigned to it, and the true divergence is older, so a near-delta prior on a fossil age forces a guaranteed-too-young, falsely precise node.

| Strategy | Encodes | When | Pitfall |
|----------|---------|------|---------|
| Lognormal (offset) node prior | offset = fossil minimum; true age = min + a modest+ gap | one well-justified fossil, modest gap expected | mean/SD chosen by feel sets the answer |
| Exponential (offset) node prior | firm minimum, agnostic about gap size | good minimum, weak idea of the maximum | long tail can pull the node very old |
| Uniform + soft bounds | min from fossil, max from absence/strat, both leaky (Yang and Rannala 2006) | a defensible minimum AND maximum | hard bounds (no tail) over-dictate |
| Total-evidence / tip dating | fossils as dated, morphologically scored tips (Ronquist et al. 2012) | morphology available; want data-driven fossil placement | the morphological clock is shaky |
| Fossilized birth-death (FBD) | all fossils as samples of one diversification process (Heath et al. 2014) | several fossils; want coherent calibration | needs lambda/mu/psi/rho; sampled-ancestor handling |
| Tip dates (sampling times) | calibration from collection dates | measurably-evolving populations: viruses, ancient DNA | requires a verified temporal-signal check first |

Soft bounds (Yang and Rannala 2006) make a bound a quantile, not a wall: a small canonical 0.025 tail of probability is allowed beyond each soft min/max so one bad fossil cannot dominate. Justify every fossil per Parham et al. 2012 (specimen identity, apomorphy-based placement, geochronologic basis, monophyly of the calibration clade, stated reasoning). The total-evidence approach (Ronquist et al. 2012) includes fossils as dated tips scored for morphology so the data, not the user, place each fossil. The fossilized birth-death process (Heath et al. 2014) is the modern coherent tree prior: it models speciation, extinction, and fossil sampling jointly, uses ALL fossils, allows sampled ancestors, and replaces the incoherent practice of multiplying ad hoc node densities. Prefer FBD when several fossils exist; use simple node densities only for one or two transparent constraints. Secondary calibrations (an age borrowed from another study) launder uncertainty -- never use a point, use the full distribution, and flag it.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| BEAST2 | Bouckaert et al. 2019 | full hierarchical Bayesian MCMC; FBD, tip-dating, total-evidence, phylodynamic priors | need a posterior, fossils-as-tips, or complex models; 10s-100s taxa |
| MCMCTree / PAML | dos Reis and Yang 2011 | approximate likelihood: a two-step BASEML gradient + Hessian, then MCMC over a Taylor approximation | genome-scale / many loci where full BEAST is infeasible |
| TreePL / r8s | Smith and O'Meara 2012; Sanderson 2002 | penalized-likelihood point estimate; roughness penalty `lambda` set by cross-validation | very large trees (1000s-10000s taxa); accept point estimates + bootstrap CIs |
| LSD2 / treedater | To et al. 2016 | least-squares dating; native tip-dating, very fast | huge tip-dated viral trees; fast rooting and sanity check before a Bayesian run |

MCMCTree's approximate likelihood does the expensive Felsenstein pruning once (computing branch-length MLEs, gradient, and Hessian per partition) rather than every MCMC step, which is what makes thousands of loci tractable; check that BASEML converged because unreliable per-partition branch lengths (saturated/short loci) corrupt the approximation. The infinite-sites plot (dos Reis and Yang 2011) plots posterior CI width against posterior mean age across nodes: under infinite data the relationship becomes linear through the origin, with the residual width set entirely by calibration uncertainty -- if real-data points already hug that line, more sequence data will NOT narrow the dates and the answer is better fossils, not more sites. TreePL and r8s return one number per node and produce NO uncertainty; a bare PL date is a failure mode, not a result -- bootstrap for CIs and cross-validate `lambda`.

## Temporal Signal Before Tip-Dating

When samples are collected at different times and the population evolves fast enough to accumulate measurable substitutions between dates (a measurably-evolving population: viruses, ancient DNA), the sampling-date differences themselves are the calibrations -- no fossil needed. Verifying temporal signal first is non-negotiable; a short-time-span dataset frequently has no signal yet a Bayesian run will return a tight, entirely prior-driven date.

- **Root-to-tip regression (TempEst, Rambaut et al. 2016):** build a rough ML tree, regress each tip's root-to-tip genetic distance against its sampling date. A genuine signal gives a positive slope (the slope estimates the rate); a negative slope means no usable signal or a wrong root. R^2 is exploratory only (tips are non-independent): treat near-zero / much-below ~0.2 as a red flag, not a formal pass. The x-intercept estimates the TMRCA as a sanity check; large-residual tips are date/contamination/recombination outliers to investigate before dating.
- **Date-randomization test (Duchene et al. 2015):** the formal test. Re-run the dating with tip dates shuffled many times; the real-data clock-rate estimate must fall OUTSIDE the distribution of randomized replicates (no CI overlap). If the real estimate sits inside that cloud, there is no temporal signal and any date is an artifact of the prior.

## Run Prior-Only to Expose the Effective Prior

**Goal:** Determine whether the molecular data inform each calibrated node, or whether the reported posterior is just a truncated prior reflected back.

**Approach:** Run the same model first with no sequence data to obtain the effective (marginal) prior, then with data; compare specified-vs-effective-vs-posterior on every calibrated node.

```bash
# BEAST2: edit the XML so the MCMC samples from the prior only (no likelihood)
# set <run ... sampleFromPrior="true"> (BEAUti: MCMC panel, "Sample From Prior")
beast -seed 1 -prefix prioronly prioronly.xml      # effective prior on every node
beast -seed 1 -prefix withdata  withdata.xml       # full posterior

# MCMCTree: usedata=0 gives the effective prior; usedata=2 the approx-likelihood posterior
mcmctree mcmctree_prior.ctl    # control file has usedata = 0
mcmctree mcmctree_post.ctl     # control file has usedata = 2
```

```python
from Bio import Phylo

prior = Phylo.read('prioronly.mcc.tree', 'nexus')   # effective prior summary
post = Phylo.read('withdata.mcc.tree', 'nexus')      # posterior summary
for c_prior, c_post in zip(prior.get_nonterminals(), post.get_nonterminals()):
    # if the posterior median and HPD ~ the effective prior, the data did not inform this node
    print(c_prior.confidence, c_post.confidence)     # compare per-node summaries side by side
```

## Check Temporal Signal Before Tip-Dating

**Goal:** Confirm a heterochronous (virus / ancient-DNA) dataset actually contains clock signal before committing to a Bayesian tip-dated run.

**Approach:** Regress root-to-tip distance on sampling date (positive slope, sane intercept, outliers flagged), then run a date-randomization test; only date if the real estimate sits outside the randomized cloud.

```bash
# Build a quick ML tree to feed TempEst (modern-tree-inference)
iqtree2 -s seqs.fa -m GTR+G -T AUTO --prefix rttree
# TempEst (GUI): load rttree.treefile + a tab file of tip sampling dates;
# read the root-to-tip regression -- require a POSITIVE slope; inspect R^2 and residual outliers.

# Fast non-Bayesian tip-dating + CI as a cross-check (LSD2 via IQ-TREE)
iqtree2 -s seqs.fa -m GTR+G --date dates.tsv --date-ci 100 --prefix lsd2   # dates.tsv: tip <tab> date
```

## Per-Method Failure Modes

### Effective Prior Is Not the Specified Prior, Unchecked
**Trigger:** Several calibration densities plus a tree prior (Yule / birth-death / FBD), run straight to the posterior.
**Mechanism:** Every node must be older than its descendants, so a parent and child density truncate each other, and the tree prior is multiplied in; the marginal prior can look nothing like either typed density (Heled and Drummond 2012; Warnock et al. 2012).
**Symptom:** A tight posterior credible interval is read as "the data nailed it," when it is really the (truncated) prior.
**Fix:** Always run prior-only (`sampleFromPrior="true"` / `usedata=0`); report specified-vs-effective-vs-posterior per node; if posterior ~ effective prior, the data did not inform it.

### Fossil Treated as a Point, Not a Minimum
**Trigger:** A near-delta calibration density centered on a fossil age.
**Mechanism:** A fossil only bounds a clade from below; the true origin is older by an unknown gap, so a point prior forces a guaranteed-too-young age.
**Symptom:** Falsely precise, systematically too-young dates that propagate across the tree.
**Fix:** Use the fossil as the offset/minimum with a backward tail (lognormal/exponential or soft bounds); never a point.

### No Temporal-Signal Check Before Tip-Dating
**Trigger:** Tip-dating a short-time-span virus or ancient-DNA dataset without TempEst + a date-randomization test.
**Mechanism:** With too little accumulated substitution between sampling dates, the data carry no rate information and the prior drives the date.
**Symptom:** Plausible-looking but entirely prior-driven dates; tight HPDs on data that cannot support them.
**Fix:** Root-to-tip regression (positive slope) AND a date-randomization test (real estimate outside the randomized cloud) before any dating run.

### Penalized-Likelihood Point Estimate Reported With No Uncertainty
**Trigger:** A TreePL / r8s date reported as a single number.
**Mechanism:** PL maximizes a penalized likelihood and returns a point; it produces no posterior or CI, and `lambda` controls how clocklike the tree is forced to be.
**Symptom:** "Clade X is 45 Ma" with no interval, and a `lambda` chosen by default rather than cross-validation.
**Fix:** Cross-validate `lambda` (TreePL `prime` + `cv`); bootstrap sites/input trees and re-run to get CIs; never report a bare PL date.

### Over-Tight Calibrations Drive the Posterior
**Trigger:** One or two narrow calibration densities dominating the timescale.
**Mechanism:** A narrow density propagates through the clock and tree prior to set ages everywhere; the data barely move them.
**Symptom:** The posterior barely differs from the prior, and conclusions reverse when a single calibration is tweaked.
**Fix:** Widen / soften bounds, sensitivity-analyze each calibration one at a time, and prefer FBD for coherence across many fossils.

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| ESS (posterior, prior, likelihood, every reported parameter) | > 200 | Rambaut et al. 2018 (Tracer); below ~100 unusable |
| Independent MCMC chains | >= 2, posteriors must overlap | convergence cannot be judged from one chain |
| Burn-in discarded | >= 10% (confirm by trace, not rote) | standard practice; verify stationarity |
| Soft-bound tail probability | 0.025 per bound | Yang and Rannala 2006; MCMCTree `pL = pU = 0.025` |
| Root-to-tip R^2 (TempEst) | exploratory; near-zero / << ~0.2 = weak signal; positive slope mandatory | Rambaut et al. 2016 (tips non-independent, not a formal test) |
| Date-randomization test | real-data rate estimate outside the randomized distribution (no CI overlap) | Duchene et al. 2015 |
| Coefficient of variation of branch rates | abutting 0 -> strict adequate; clearly > 0 (0 excluded) -> relaxed needed | Drummond et al. 2006 |
| Infinite-sites plot | points on the linear CI-width-vs-age line -> more sites will not help | dos Reis and Yang 2011 |
| MCMCTree acceptance proportion | ~20-40% (target ~30%); tune `finetune` if outside | PAML practice |
| Smoothing `lambda` (TreePL/r8s) | set by cross-validation, never default | Sanderson 2002; Smith and O'Meara 2012 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| MCMCTree refuses to run | no root calibration | set `RootAge` in the control file or a calibration on the root node |
| MCMCTree calibration silently ignored | used `>`/`<` notation (parsing bug) | use `B()`/`L()`/`U()` in the tree file |
| Posterior ~ prior for a node age | data uninformative for that node | report it honestly; do not claim the data estimated the age |
| Wide CIs on both rate and root age | rate-time confounding from too few calibrations | add a well-justified calibration; check the rate-vs-root-age correlation |
| Times off by 100x in MCMCTree | unit confusion (no fixed time unit; the user picks one, 100 Myr conventional so ages are O(1)) | keep calibrations and `rgene_gamma` in that same unit; then 0.6 = 60 Ma |
| Dates conflict wildly with independent evidence | unjustified fossil placement | apply the Parham et al. 2012 checklist; recheck the assigned clade |
| Deep dates biased | substitution saturation at fast sites | use slower markers, amino acids, or codon models; remove saturated partitions |

## References

Bouckaert R, Vaughan TG, Barido-Sottani J, Duchene S, Fourment M, et al. 2019. BEAST 2.5: an advanced software platform for Bayesian evolutionary analysis. *PLoS Computational Biology* 15(4):e1006650.
Drummond AJ, Ho SYW, Phillips MJ, Rambaut A. 2006. Relaxed phylogenetics and dating with confidence. *PLoS Biology* 4(5):e88.
Thorne JL, Kishino H, Painter IS. 1998. Estimating the rate of evolution of the rate of molecular evolution. *Molecular Biology and Evolution* 15(12):1647-1657.
Drummond AJ, Suchard MA. 2010. Bayesian random local clocks, or one rate to rule them all. *BMC Biology* 8:114.
Heath TA, Huelsenbeck JP, Stadler T. 2014. The fossilized birth-death process for coherent calibration of divergence-time estimates. *PNAS* 111(29):E2957-E2966.
Ronquist F, Klopfstein S, Vilhelmsen L, Schulmeister S, Murray DL, Rasnitsyn AP. 2012. A total-evidence approach to dating with fossils, applied to the early radiation of the Hymenoptera. *Systematic Biology* 61(6):973-999.
Dos Reis M, Yang Z. 2011. Approximate likelihood calculation on a phylogeny for Bayesian estimation of divergence times. *Molecular Biology and Evolution* 28(7):2161-2172.
Yang Z, Rannala B. 2006. Bayesian estimation of species divergence times under a molecular clock using multiple fossil calibrations with soft bounds. *Molecular Biology and Evolution* 23(1):212-226.
Sanderson MJ. 2002. Estimating absolute rates of molecular evolution and divergence times: a penalized likelihood approach. *Molecular Biology and Evolution* 19(1):101-109.
Smith SA, O'Meara BC. 2012. treePL: divergence time estimation using penalized likelihood for large phylogenies. *Bioinformatics* 28(20):2689-2690.
To T-H, Jung M, Lycett S, Gascuel O. 2016. Fast dating using least-squares criteria and algorithms. *Systematic Biology* 65(1):82-97.
Rambaut A, Lam TT, Carvalho LM, Pybus OG. 2016. Exploring the temporal structure of heterochronous sequences using TempEst (formerly Path-O-Gen). *Virus Evolution* 2(1):vew007.
Duchene S, Duchene D, Holmes EC, Ho SYW. 2015. The performance of the date-randomization test in phylogenetic analyses of time-structured virus data. *Molecular Biology and Evolution* 32(7):1895-1906.
Parham JF, Donoghue PCJ, Bell CJ, Calway TD, Head JJ, et al. 2012. Best practices for justifying fossil calibrations. *Systematic Biology* 61(2):346-359.
Heled J, Drummond AJ. 2012. Calibrated tree priors for relaxed phylogenetics and divergence time estimation. *Systematic Biology* 61(1):138-149.
Warnock RCM, Yang Z, Donoghue PCJ. 2012. Exploring uncertainty in the calibration of the molecular clock. *Biology Letters* 8(1):156-159.
Brown JW, Smith SA. 2018. The past sure is tense: on interpreting phylogenetic divergence time estimates. *Systematic Biology* 67(2):340-353.
Dos Reis M, Donoghue PCJ, Yang Z. 2016. Bayesian molecular clock dating of species divergences in the genomics era. *Nature Reviews Genetics* 17(2):71-80.
Rambaut A, Drummond AJ, Xie D, Baele G, Suchard MA. 2018. Posterior summarization in Bayesian phylogenetics using Tracer 1.7. *Systematic Biology* 67(5):901-904.

## Related Skills

- bayesian-inference - MCMC convergence, ESS, marginal-likelihood model comparison, and site-heterogeneous models
- modern-tree-inference - the rooted, branch-length ML tree and model selection that dating consumes
- tree-manipulation - rooting as a separate inference and the input tree required before dating
- tree-io - reading and writing the dated MCC tree without dropping HPD intervals on node ages
- epidemiological-genomics/phylodynamics - effective population size and Re estimation downstream of tip-dated trees
<!-- END FILE: phylogenetics/divergence-dating/SKILL.md -->

## 子目录：phylogenetics/modern-tree-inference

<!-- BEGIN FILE: phylogenetics/modern-tree-inference/SKILL.md -->
---
name: bio-phylo-modern-tree-inference
description: Infers maximum-likelihood phylogenetic trees with IQ-TREE2 and RAxML-NG -- model selection (ModelFinder), branch support (UFBoot2, SH-aLRT), concordance factors (gCF/sCF), partitioning, topology tests, and long-branch-attraction control. Covers why an ML tree inherits every flaw of the assumed model and the fixed alignment, why reported support measures repeatability under resampling and not correctness, why UFBoot uses a >=95 cutoff and not the bootstrap-70 rule, and why a node with UFBoot 100 but gCF ~35 is essentially unresolved ILS rather than a clade. Use when inferring an ML tree, selecting a substitution or partition model, choosing or interpreting support measures, testing an a-priori topology, or diagnosing LBA. Routes model-free distance trees to distance-calculations, posteriors to bayesian-inference, and species trees under ILS to species-trees.
tool_type: cli
primary_tool: IQ-TREE2
---

## Version Compatibility

Reference examples tested with: IQ-TREE 2.2+ / 2.3+, RAxML-NG 1.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `iqtree2 --version` then `iqtree2 --help` to confirm flags
- CLI: `raxml-ng --version` then `raxml-ng --help` to confirm flags

If code throws an unrecognized-argument or model-parse error, introspect the installed tool and adapt the example to match the actual API rather than retrying.

IQ-TREE2 uses single-dash documented forms (`-alrt`, `-bnni`, `-B`); `-B`/`-T` are v2.x (v1.x used `-bb`/`-nt`). Do NOT write `--alrt`. The likelihood site-concordance flag `--scfl` requires IQ-TREE 2.2.2+ (older builds have only the parsimony `--scf`).

# Modern ML Tree Inference -- ML Support Measures Repeatability, Not Correctness

**"Build a maximum-likelihood tree with support from my alignment"** -> Select a substitution model, search topology and branch lengths that maximize the likelihood, then attach support that quantifies repeatability and concordance that quantifies genealogical agreement.
- CLI: `iqtree2 -s aln.fasta -m MFP -B 1000 -bnni -alrt 1000` (model selection + dual support, all built in)
- CLI: `raxml-ng --all --msa aln.fasta --model GTR+G --bs-metric fbp,tbe` (very large trees, transfer bootstrap, precise branch lengths)

Scope: ML estimation of topology, branch lengths, model selection, branch support, concordance factors, partitioning, topology tests, and LBA control. Model-free distance/NJ trees and distance correction -> distance-calculations. Posterior distributions, MCMC, and CAT-GTR -> bayesian-inference. Per-locus gene trees summarized into a species tree under ILS -> species-trees. Time-scaled trees -> divergence-dating.

## The Single Most Important Modern Insight

An ML tree is the topology and branch lengths that maximize the likelihood under an ASSUMED substitution model, conditioned on a FIXED multiple-sequence alignment. It inherits every flaw of both: a misaligned column is a fabricated character the model dutifully fits, and a misspecified model biases the point estimate toward a wrong topology that more data only sharpens. The reported support measures REPEATABILITY under resampling, not correctness. Three load-bearing facts:

1. **High support is consistent with being wrong.** Bootstrap, UFBoot, SH-aLRT, and aBayes all ask whether a branch reappears when the data or tree is perturbed. Under model misspecification every replicate reproduces the same bias, so support climbs toward 100% precisely as the inference becomes more wrong. At genome scale, sampling error vanishes and UFBoot ~100 on most branches is the default, not a signal.
2. **More data fixes variance, not bias.** Adding sites shrinks sampling error and makes the estimate more confident, but the systematic error from saturation, compositional heterogeneity, and ILS is bias that CONCENTRATES with scale. The cure for confident-wrong trees is better models, better alignments, and better diagnostics -- never more bootstrap replicates.
3. **Concordance factors are the honest measure at genome scale.** gCF/sCF ask what FRACTION of genes or sites actually contains a branch. A node with UFBoot 100 and gCF 35 means the concatenated likelihood is certain but only ~35% of loci endorse that branch -- biologically unresolved (ILS or introgression), and the bootstrap answered a question nobody should have asked. Report CFs on every phylogenomic tree; treat bootstrap as necessary-not-sufficient.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| IQ-TREE2 | Minh 2020 | ML search + ModelFinder + UFBoot2 + SH-aLRT + gCF/sCF + AU test + C60/PMSF, all built in | the default for almost all work |
| RAxML-NG | Kozlov 2019 | ML search, transfer bootstrap, terrace-aware, MPI/checkpointing | very large trees, TBE, precise branch lengths, long HPC runs |
| PhyML | Guindon 2010 | ML search, origin of SH-aLRT | legacy/teaching; SH-aLRT is now in IQ-TREE2 |
| FastTree | Price 2010 | approximate ML, single-pass NNI/SPR | a fast first-pass tree on thousands of sequences; not for final support |

IQ-TREE2 vs RAxML-NG (both hill-climb the same likelihood; they differ in built-in features and scaling, not correctness):

| Need | Use |
|------|-----|
| Model selection, UFBoot2, SH-aLRT, concordance factors, AU test, mixture/PMSF | IQ-TREE2 (built in; nothing else bundles all of this) |
| Very large trees (thousands of taxa), low memory, MPI | RAxML-NG |
| Transfer bootstrap (TBE) for rogue-taxon mega-trees | RAxML-NG (`--bs-metric tbe`) |
| Most precise branch lengths for downstream dating | RAxML-NG |
| Robust checkpoint/restart on long runs | RAxML-NG |

Common production pattern: model-select, compute CFs, and topology-test in IQ-TREE2; do heavy bootstrap on a mega-tree in RAxML-NG with `--bs-metric fbp,tbe`.

## Model Selection

ModelFinder (Kalyaanamoorthy 2017) scores the substitution matrix and the rate-heterogeneity model jointly, including FreeRate categories the old jModelTest/ProtTest generation never tested, and ranks by BIC (the default; k*ln(n) penalty favors simpler models that generalize on large n).

- `-m MFP` -- ModelFinder Plus: test all models by BIC, then search with the winner. The standard. (`-m MF` selects only; avoid `-m TEST`/`-m TESTONLY`, the legacy jModelTest-style limited set.)
- **+G vs +R.** `+G` (discrete Gamma, one alpha) is the workhorse for single short genes. `+R` (FreeRate) freely estimates each category's rate AND weight, capturing the non-Gamma, often multimodal rate distributions of concatenated phylogenomic data; expect `+R3` to `+R6` to win on BIC at scale.
- **The +I+G trap.** The invariant-sites proportion (+I) and the Gamma shape (+G) describe overlapping rate distributions, so the likelihood surface has a flat ridge: the two estimates are individually near-meaningless and start-dependent. Prefer `+R` (its slowest category absorbs near-invariant sites); use `+G` alone unless BIC genuinely demands +I+G.
- **Partition model selection.** `-m MFP+MERGE` fits per-partition models AND greedily merges partitions that fit the same model (BIC-chosen scheme, the successor to PartitionFinder greedy). Pair with `-rcluster 10` (relaxed clustering: only test the top 10% most-similar pairs) for many partitions.
- **Site-heterogeneous mixtures for deep data.** Empirical matrices (LG, WAG) assume one residue-frequency vector for the whole alignment; real proteins do not, and that across-site compositional heterogeneity is the chief driver of deep LBA. The ML answer is the C10..C60 profile-mixture series (`LG+C60+F+G`), made tractable by PMSF (Wang 2018): a guide-tree pass computes one posterior-mean profile per site, and the real search uses those frozen profiles. PMSF is the standard recommendation for deep / LBA-prone protein phylogenomics.

## Branch Support -- the Heart

Five measures, three different questions; the cardinal sin is cross-comparing their cutoffs.

| Metric | What it perturbs / measures | Strong cutoff | Tool / flag | Failure mode |
|--------|------------------------------|---------------|-------------|--------------|
| Standard bootstrap (FBP) | resample sites; clade frequency (binary) | >=70 (folklore) | RAxML-NG `--bs-metric fbp`; IQ-TREE `-b` | slow; crushed by rogue taxa in big trees |
| Ultrafast bootstrap 2 (UFBoot) | RELL-resampled log-Ls; ~unbiased clade prob | **>=95 (NOT 70)** | IQ-TREE2 `-B 1000` (+`-bnni`) | inflates under model violation -> use `-bnni` |
| SH-aLRT | local NNI likelihood ratio (no resampling) | >=80 | IQ-TREE2 `-alrt 1000` | conservative on very short branches |
| aBayes | posterior from 3 NNI Ls, flat prior | >=0.95 | IQ-TREE2 `-abayes` | anti-conservative; never the sole criterion |
| Transfer bootstrap (TBE) | gradual transfer distance under resampling | no fixed cutoff; > FBP | RAxML-NG `--bs-metric tbe` | permissive; "fuzzy" branch identity |

UFBoot2 (Hoang 2018) uses the RELL trick (resample site log-likelihoods, reuse a candidate tree set) to run hundreds of times faster than the Felsenstein bootstrap (1985), and its values are CLOSER to unbiased clade probabilities -- which is exactly why the strong-support cutoff is 95, not the conservative-bootstrap 70. Treating UFBoot 70 as "good" is a category error. `-bnni` re-optimizes each replicate tree by NNI to rein in the inflation that model violation causes; use `-B 1000 -bnni` routinely. UFBoot is on a DIFFERENT scale from the standard bootstrap -- never read it with the BP-70 rule.

SH-aLRT (Guindon 2010) does not resample data; for each branch it tests whether the ML likelihood beats its two best NNI rearrangements. UFBoot (data perturbation) and SH-aLRT (tree perturbation) have different failure modes, so the community-standard joint criterion requires both:

> A branch is strongly supported iff SH-aLRT >= 80% AND UFBoot >= 95%.

For large rogue-taxon-prone trees, the binary Felsenstein bootstrap lets a single wandering tip crush an otherwise-recovered deep branch; transfer bootstrap (TBE, Lemoine 2018, RAxML-NG `--bs-metric tbe`) replaces the in/out indicator with a gradual transfer distance and rescues those branches, at the cost of being more permissive.

## Concordance Factors

Bootstrap quantifies statistical confidence given the concatenated data; concordance factors (Minh 2020) quantify how much of the actual data carries a branch.

- **gCF (gene concordance factor):** the percentage of decisive single-locus gene trees that contain the exact branch. Needs per-locus gene trees.
- **sCF (site concordance factor):** the percentage of decisive sites supporting the branch, from sampled quartets; works on a single concatenated alignment with no gene trees.
- **sCFL (likelihood sCF, Mo 2023):** uses ancestral-state likelihoods rather than parsimony quartet counting, substantially reducing (not abolishing) homoplasy and taxon-sampling bias. Prefer `--scfl` over the old `--scf` on IQ-TREE 2.2.2+.

```bash
# one gene tree per locus from a directory of locus alignments (-S = separate, no concatenation)
iqtree2 -S loci_dir -m MFP -B 1000 -T AUTO --prefix loci   # -B 1000 = UFBoot per gene tree, needed to contract weak branches before ASTRAL

# gene + likelihood site concordance against a fixed concatenated tree (-te fixes the tree)
iqtree2 -te concat.treefile -s concat.fasta --gcf loci.treefile --scfl 100 -T 4 --prefix concord
#  --gcf loci.treefile   per-locus gene trees for gCF
#  --scfl 100            100 sampled quartets per branch for likelihood sCF (higher = more stable)
```

Outputs `concord.cf.tree` (Newick with gCF/sCF labels) and `concord.cf.stat` (per-branch gCF, gDF1, gDF2, gDFP, sCF). A node with UFBoot 100 but gCF ~35 (gDF1 ~33, gDF2 ~30) is genes split three ways: the concatenated point estimate barely edges the alternatives and the node is biologically unresolved -- the signature of ILS or introgression, not a clade. Report CFs alongside support on every phylogenomic tree.

## Topology Tests

For testing an a-priori hypothesis ("can I reject that X and Y are monophyletic?") against the ML tree, by comparing a set of fixed trees. Build the constrained tree with `-g constraint.tree`, then evaluate both trees:

```bash
# trees.nex holds the unconstrained ML tree + the constrained/alternative trees
iqtree2 -s aln.fasta -m <model> -z trees.nex -n 0 -zb 10000 -au --prefix autest
#  -z trees.nex   trees to compare        -n 0   no fresh search, just evaluate
#  -zb 10000      RELL replicates (>=1000) -au    add the AU test (must accompany -zb)
```

The AU test (Shimodaira 2002) uses multiscale bootstrap resampling to correct both the selection bias of the KH test (invalid on the data-selected ML tree) and the over-conservatism of the SH test (which rejects less as the candidate set is padded). Use AU by default. **p-AU < 0.05 means that tree is REJECTED**; p-AU >= 0.05 means it is in the 95% confidence set (failure to reject is not acceptance -- weak data fails to reject many trees). Report SH/KH only for completeness.

## Partitioning

When splitting an alignment into partitions, the branch-length linkage choice is what people get wrong:

| Mode | Flag | Branch lengths | Use when |
|------|------|----------------|----------|
| Edge-equal | `-q part.nex` | identical across partitions | partitions share rate (rare, restrictive) |
| Edge-linked proportional | `-p part.nex` | shared topology, per-partition rate multiplier | DEFAULT -- genes evolve at different speeds, share history |
| Edge-unlinked | `-Q part.nex` | fully independent per partition | genuine heterotachy; parameter-hungry, overfits |

`-p` (edge-linked proportional) is the standard: one rate multiplier per partition over a shared topology. Over-partitioning spends degrees of freedom without bias reduction and inflates variance; the antidote is to start fine (gene x codon position) and let `-m MFP+MERGE -rcluster 10` find the coarsest BIC-justified scheme. Prefer a merged scheme over a hand-picked maximal one; prefer `-p` over `-Q`.

## Per-Method Failure Modes

### Long-Branch Attraction
**Trigger:** Two or more independently fast-evolving lineages on long branches separated by a short internode.
**Mechanism:** Convergent/homoplastic substitutions on the long branches look like shared ancestry; a site-homogeneous model cannot separate convergence from homology and groups them -- bias that GROWS with more sites.
**Symptom:** Fast taxa group with the outgroup or each other at 100% bootstrap; the grouping collapses under a better model or when a long-branch taxon is removed.
**Fix:** Site-heterogeneous model (C60/PMSF) first; remove the fastest sites and watch the node; drop the long-branch taxon or use a closer outgroup; cross-check with SR4/Dayhoff recoding. Believe a deep node only when it survives all of these, not when it merely has UFBoot 100 under LG+G.

### Model Underspecification
**Trigger:** A single inadequate model on heterogeneous data; the best site-homogeneous model by BIC still inadequate at depth.
**Mechanism:** Wrong matrix, missing rate heterogeneity, or no partitioning biases the topology while support stays high.
**Symptom:** Biologically implausible nodes with full support that move under a richer model.
**Fix:** `-m MFP` (+MERGE for multi-locus), FreeRate `+R`, and at amino-acid depth a C60/PMSF mixture. Best-by-BIC among site-homogeneous models is not sufficient deep in the tree.

### Over-Partitioning
**Trigger:** Hundreds of hand-defined partitions, especially under `-Q`.
**Mechanism:** Each partition's model is estimated from too little data; parameter and branch-length estimates get noisy without reducing bias.
**Symptom:** Slow runs, noisy estimates, degraded support.
**Fix:** `-m MFP+MERGE -rcluster 10` to the coarsest BIC-justified scheme; use `-p`, not `-Q`.

### The Support-Accuracy Gap
**Trigger:** UFBoot/bootstrap ~100 everywhere, including implausible or conflicting nodes.
**Mechanism:** Support measures repeatability of a possibly-biased estimate; concatenation pools conflicting gene signals so the likelihood is certain while the loci disagree.
**Symptom:** Full support but gCF ~33 / sCF near its ~33% floor on contested nodes.
**Fix:** Compute gCF/sCFL; treat UFBoot 100 + gCF ~33 as UNRESOLVED; require SH-aLRT >=80 AND UFBoot >=95; use `-bnni`. If most genes reject the ML resolution, route to a coalescent species tree -> species-trees.

## Quantitative Thresholds

| Quantity | Threshold | Source |
|----------|-----------|--------|
| UFBoot strong support | >=95 (NOT the bootstrap 70) | Hoang 2018 |
| SH-aLRT strong support | >=80 | Guindon 2010 |
| Joint rule | SH-aLRT >=80 AND UFBoot >=95 | community standard |
| Standard bootstrap "good" | >=70 (different metric, folklore) | Felsenstein 1985 / Hillis 1993 |
| aBayes strong | >=0.95 (anti-conservative; never alone) | Anisimova 2011 |
| Bootstrap replicates | UFBoot `-B` >=1000; SH-aLRT `-alrt` >=1000; AU `-zb` 10000 | IQ-TREE docs |
| gCF reading | >~75 agree; ~50 conflicted; ~33 effective polytomy; <33 with higher alternative = possible wrong resolution | Minh 2020 |
| sCF floor | ~33% (three quartet resolutions); ~33 = no site signal | Minh 2020 |
| AU test | p-AU < 0.05 => tree REJECTED | Shimodaira 2002 |
| Model selection | rank by BIC (`-m MFP` default), k*ln(n) penalty | Kalyaanamoorthy 2017 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `Unknown argument --alrt` | wrote the GNU double-dash form | IQ-TREE2 uses single-dash `-alrt`, `-bnni`, `-B` |
| `-bb` / `-nt` not recognized | v1.x flags on a v2.x binary | use `-B` (bootstrap) and `-T` (threads) in 2.x |
| Reading UFBoot 80 as "supported" | applied the bootstrap-70 rule to a different scale | use UFBoot >=95 AND SH-aLRT >=80 |
| Fully-supported deep node distrusted by reviewer | no concordance factors reported | compute gCF/sCFL; treat high-support/low-CF as unresolved |
| `--scfl` unrecognized | IQ-TREE older than 2.2.2 | upgrade, or fall back to parsimony `--scf` |
| Concatenated tree confidently wrong on a rapid radiation | ILS; concatenation is inconsistent in the anomaly zone | infer per-locus gene trees and a coalescent species tree -> species-trees |
| AU test "fails to reject" the alternative | weak data, or candidate set padded | do not pad the set; failure to reject is not acceptance |

## References

Felsenstein J. 1978. Cases in which parsimony or compatibility methods will be positively misleading. *Systematic Zoology* 27(4):401-410.
Felsenstein J. 1985. Confidence limits on phylogenies: an approach using the bootstrap. *Evolution* 39(4):783-791.
Guindon S, Dufayard J-F, Lefort V, Anisimova M, Hordijk W, Gascuel O. 2010. New algorithms and methods to estimate maximum-likelihood phylogenies: assessing the performance of PhyML 3.0. *Systematic Biology* 59(3):307-321.
Price MN, Dehal PS, Arkin AP. 2010. FastTree 2: approximately maximum-likelihood trees for large alignments. *PLoS ONE* 5(3):e9490.
Anisimova M, Gil M, Dufayard J-F, Dessimoz C, Gascuel O. 2011. Survey of branch support methods demonstrates accuracy, power, and robustness of fast likelihood-based approximation schemes. *Systematic Biology* 60(5):685-699.
Shimodaira H. 2002. An approximately unbiased test of phylogenetic tree selection. *Systematic Biology* 51(3):492-508.
Kalyaanamoorthy S, Minh BQ, Wong TKF, von Haeseler A, Jermiin LS. 2017. ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods* 14(6):587-589.
Wang H-C, Minh BQ, Susko E, Roger AJ. 2018. Modeling site heterogeneity with posterior mean site frequency profiles accelerates accurate phylogenomic estimation. *Systematic Biology* 67(2):216-235.
Hoang DT, Chernomor O, von Haeseler A, Minh BQ, Vinh LS. 2018. UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution* 35(2):518-522.
Lemoine F, Domelevo Entfellner J-B, Wilkinson E, Correia D, Davila Felipe M, De Oliveira T, Gascuel O. 2018. Renewing Felsenstein's phylogenetic bootstrap in the era of big data. *Nature* 556(7702):452-456.
Kozlov AM, Darriba D, Flouri T, Morel B, Stamatakis A. 2019. RAxML-NG: a fast, scalable and user-friendly tool for maximum likelihood phylogenetic inference. *Bioinformatics* 35(21):4453-4455.
Minh BQ, Schmidt HA, Chernomor O, Schrempf D, Woodhams MD, von Haeseler A, Lanfear R. 2020. IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution* 37(5):1530-1534.
Minh BQ, Hahn MW, Lanfear R. 2020. New methods to calculate concordance factors for phylogenomic datasets. *Molecular Biology and Evolution* 37(9):2727-2733.
Mo YK, Lanfear R, Hahn MW, Minh BQ. 2023. Updated site concordance factors minimize effects of homoplasy and taxon sampling. *Bioinformatics* 39(1):btac741.

## Related Skills

- distance-calculations - model-corrected distances and fast NJ trees as a model-free alternative
- bayesian-inference - posteriors, MCMC convergence, and CAT-GTR site-heterogeneous models
- species-trees - coalescent species-tree estimation when concordance factors reveal ILS
- divergence-dating - time-scaled trees from the ML topology
- tree-manipulation - rooting, pruning, and collapsing low-support nodes
- alignment/alignment-io - the alignment whose homology assumption the ML tree trusts as fixed
<!-- END FILE: phylogenetics/modern-tree-inference/SKILL.md -->

## 子目录：phylogenetics/species-trees

<!-- BEGIN FILE: phylogenetics/species-trees/SKILL.md -->
---
name: bio-phylo-species-trees
description: Estimates species trees under the multispecies coalescent from per-locus gene trees with the modern ASTER astral binary (ASTRAL-III/wASTRAL/ASTRAL-Pro), plus SVDQuartets, BPP, and StarBEAST2. Covers why a species tree is not a gene tree, why each locus has its own genealogy that disagrees by incomplete lineage sorting (ILS) even with zero error, why concatenation is statistically inconsistent and positively misleading in the anomaly zone where more loci converge on the wrong tree with full support, why gene-tree estimation error biases summary methods, that localPP is not bootstrap and ASTRAL branch lengths are coalescent units, and how minority-quartet symmetry separates ILS from introgression. Use when multi-locus discordance, rapid radiations, anomaly-zone risk, concordance-factor interpretation, or concatenation-vs-coalescent choice arise. Routes per-locus gene-tree inference and gCF/sCF to modern-tree-inference, dating to divergence-dating, orthology to comparative-genomics/ortholog-inference.
tool_type: mixed
primary_tool: ASTRAL-III
---

## Version Compatibility

Reference examples tested with: ASTER 1.15+ (provides astral/ASTRAL-III, wastral, astral-pro), IQ-TREE 2.2+ (concordance factors), PAUP* 4.0a168+ (SVDQuartets), BPP 4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `astral --version` then `astral --help` to confirm flags
- CLI: `iqtree2 --version` then `iqtree2 --help` to confirm flags
- CLI: PAUP* prints its version at startup; BPP reads a control file

If code throws an error, introspect the installed version and adapt flags rather than retrying.

The modern binary is `astral` from the ASTER package; input is a file of gene-tree Newick strings, one tree per line. The classic-Java ASTRAL uses `-t` for ANNOTATION level, but the ASTER `astral` uses `-t` for THREADS and `-u` for annotation -- copying a Java `-t 8` (quartet support) into ASTER silently requests 8 threads with no annotation. Confirm which interface is installed before scripting.

# Coalescent Species-Tree Estimation -- A Species Tree Is Not a Gene Tree, and Concatenation Is Inconsistent in the Anomaly Zone

**"Estimate the species tree from my multi-locus phylogenomic data"** -> Treat the dataset as a distribution of genealogies, not one tree, and estimate the species tree most consistent with that distribution under the multispecies coalescent.
- CLI: per-locus gene trees (modern-tree-inference) then `astral -i gene_trees.nwk -o species.tre` (ASTER)
- CLI: gene and site concordance factors via `iqtree2 ... --gcf ... --scfl` (shared with modern-tree-inference)

Scope: choosing and running a coalescent species-tree method, contracting noisy gene trees, and reading discordance honestly. Per-locus gene-tree inference and model selection -> modern-tree-inference. Computing and plotting gCF/sCF -> modern-tree-inference, tree-visualization. Single-copy vs multi-copy orthology upstream -> comparative-genomics/ortholog-inference. Dated species trees -> divergence-dating. Rooting -> tree-manipulation.

## The Single Most Important Modern Insight

A species tree is not a gene tree. Each locus has its own genealogy, and under the multispecies coalescent (MSC) those genealogies disagree with the species tree -- and with each other -- by incomplete lineage sorting (ILS) alone, with zero estimation error. The disagreement is not noise to average away; it is signal generated by the coalescent running inside the species tree. Three load-bearing facts:

1. **The most probable gene tree can be the wrong species tree.** When two short speciation events occur in quick succession, the single most common gene-tree topology is not the species tree -- this is the anomaly zone (Degnan and Rosenberg 2006), and such gene trees are anomalous gene trees. A plurality vote across loci then converges on the wrong tree.
2. **Concatenation is statistically inconsistent and positively misleading under ILS.** It pretends all loci share one tree and behaves like a vote dominated by the most-supported site pattern; in the anomaly zone that pattern reflects the anomalous genealogy, so adding loci raises bootstrap support for the wrong topology toward 100% (Kubatko and Degnan 2007; Roch and Steel 2015). More data makes the error more confident, not less. The support is the trap.
3. **The honest question is the distribution, not the tree.** Coalescent summary methods (ASTRAL family) stay consistent because they ask "what species tree is most consistent with having generated this gene-tree distribution under the MSC?" -- and they work at the quartet level, where the matching topology is always the plurality and no anomaly zone exists. Concatenation answers a different, wrong question, and both outputs look identically resolved and supported.

## When Concatenation Fails

Concatenation is consistent and efficient only when ILS is low. It is actively wrong in three coupled regimes, all driven by short internodes measured in coalescent units (generations / 2Ne):

1. **Short internodes plus large ancestral Ne.** A short branch gives lineages little time to coalesce before the next deeper population, so many survive and sort randomly. For a rooted triple, P(gene tree matches) = 1 - (2/3)e^(-tau) in coalescent units tau: at tau = 1 about 25% of gene trees are discordant, at tau = 0.3 about 50%, at tau = 0.1 about 60%. Large Ne shortens tau for the same number of years, inflating ILS.
2. **The anomaly zone (Degnan and Rosenberg 2006).** With two or more short successive internal branches (both well under ~1, especially under ~0.1-0.2 coalescent units), the most probable gene tree differs from the species tree. The zone grows with taxon number and with shorter, more clustered internodes.
3. **Rapid radiations.** Successive speciation in quick succession is built from exactly those short internodes, so radiations routinely show a majority of gene trees conflicting with the species tree. This is the canonical case for a coalescent method.

## Method Taxonomy

| Method | Citation | Type / role | When |
|--------|----------|-------------|------|
| ASTRAL-III (`astral`) | Zhang 2018 | Summary, quartet-based; consistent under MSC; localPP, polytomy test, q1/q2/q3 | Default genome-scale species tree from single-copy gene trees |
| wASTRAL (`wastral`/astral-hybrid) | Zhang and Mirarab 2022 | Summary, weighted quartets; down-weights weak gene-tree branches | Current best-accuracy summary method for real (noisy) gene trees |
| ASTRAL-Pro (`astral-pro`) | Zhang 2020 | Summary, quartet-based on MULTI-COPY gene-family trees | Paralog-rich families; uses families without pre-orthology |
| SVDQuartets | Chifman and Kubatko 2014 | Site-based quartets from site patterns; NO gene trees | Short loci (RADseq/UCE/SNP); when gene trees are unreliable |
| BPP | Flouri 2018 | Full-likelihood Bayesian MSC; integrates gene-tree uncertainty | Small high-stakes datasets; species delimitation; introgression (MSci) |
| StarBEAST2 | Ogilvie 2017 | Full Bayesian co-estimation of species tree, gene trees, dates | Dated species tree with full posterior uncertainty |
| Concatenation (IQ-TREE/RAxML) | -- | Supermatrix ML; assumes ONE tree | Low ILS / high gCF only; never in or near the anomaly zone |

Summary methods take estimated gene trees as input and assume they are true -- the central caveat (see failure modes). Site-based (SVDQuartets) and full-likelihood (BPP, StarBEAST2) skip that assumption but pay in scale: roughly tens of taxa for the full-likelihood methods. The speed/scale order (most scalable first) is concatenation < ASTRAL/wASTRAL < SVDQuartets < StarBEAST2 < BPP; model completeness runs the opposite way. Pick the most scalable method whose assumptions the data do not badly violate. Introgression detection (HyDe, Blischak 2018, Syst Biol; QuIBL, Edelman 2019, Science; the D-statistic) lives downstream of the symmetry diagnostic below.

## Concatenation vs Coalescent Decision

| Situation / diagnostic | Recommended |
|------------------------|-------------|
| Low ILS: long internodes (>>1 coalescent unit), gCF high (>~70), few discordant gene trees | Concatenation fine; coalescent agrees and adds no advantage |
| Moderate ILS: gCF ~50-70, some short branches | Run wASTRAL; check gCF/sCF and the polytomy test on short branches |
| High ILS / rapid radiation: short successive internodes, gCF <50 (esp. <33), q2 ~ q3 | Coalescent REQUIRED; concatenation is anomaly-zone wrong; quartet consistency holds |
| Low per-locus signal / unreliable gene trees | wASTRAL or contract gene-tree branches <10% support; or SVDQuartets (no gene trees); BPP integrates uncertainty |
| Paralog-rich gene families | ASTRAL-Pro (no pre-orthology); concatenation cannot use them |
| Need dated tree or delimitation | StarBEAST2 (dating) or BPP (delimitation); coalescent-unit lengths are not time |
| Suspected introgression (q2 != q3, D significant) | Model the reticulation (HyDe/QuIBL/BPP-MSci/PhyloNet); a tree masks it |

Do not reflexively coalescent-everything: where ILS is low the two trees agree and concatenation pools weak per-locus signal robustly. The deliverable is concordance, not a single best method -- run both, compute gCF/sCF, and trust the coalescent tree exactly where the two disagree on low-gCF branches.

## Estimate the Species Tree from Gene Trees

**Goal:** Turn per-locus gene trees into a species tree that is consistent under the MSC, after removing gene-tree noise that would bias the quartet counts.

**Approach:** Infer one gene tree per locus with branch support (modern-tree-inference), contract branches below ~10% support to polytomies (which ASTRAL handles correctly), then run wASTRAL as the primary estimate and `astral` for the classic localPP / polytomy-test workflow.

```bash
# Per-locus gene trees with support live upstream in modern-tree-inference:
#   iqtree2 -S loci_dir -m MFP -B 1000 -T AUTO --prefix loci   # one tree per locus
# Contract gene-tree branches below 10% support (Newick tools / nw_ed) -> polytomies,
# then concatenate into one file, one Newick per line:
#   cat loci/*.contracted.treefile > gene_trees.nwk

# Primary estimate: wASTRAL weights quartets by gene-tree support+length (noisy gene trees)
wastral -i gene_trees.nwk -o species_wastral.tre 2> species_wastral.log

# Classic ASTRAL-III for localPP + polytomy test. In ASTER, -t is THREADS, -u is annotation:
astral -t 8 -i gene_trees.nwk -o species.tre 2> species.log     # -t 8 = 8 threads here
astral -u 2 -i gene_trees.nwk -o species_annot.tre              # full localPP + q1/q2/q3 for all 3 resolutions
astral --root OUTGROUP -i gene_trees.nwk -o species_rooted.tre  # rooting improves branch-length estimation

# Multi-copy gene families (no pre-orthology) -> ASTRAL-Pro:
astral-pro -i family_trees.nwk -o species_pro.tre
```

ASTRAL returns an UNROOTED tree; root with an outgroup afterward. Branch lengths are in coalescent units (not time, not substitutions), and tip lengths are undefined in that mode. The classic Java `astral.5.7.8.jar` inverts the flags: there `-t` is the annotation level (`-t 2` full, `-t 8` quartet support, `-t 10` polytomy test) and there is no `-u`.

## Compute and Read Concordance Factors

**Goal:** Replace a single bootstrap/localPP per branch with how much of the actual data agrees, and read ILS-vs-introgression off the quartet symmetry.

**Approach:** Compute gene and site concordance factors against the species tree, then inspect the two minority quartet frequencies (q2, q3) at each contested branch.

```bash
# gCF = % of decisive gene trees containing a branch; sCF = % of decisive sites supporting it
iqtree2 -te species.tre --gcf gene_trees.nwk -s concat.fasta --scfl 100 --prefix cf   # -te fixes the topology for likelihood sCF
# cf.cf.tree carries gCF/sCF on node labels; cf.cf.stat has per-branch q1/q2/q3 counts
```

Then read each contested branch: under pure ILS the two minority topologies are equally probable (q2 ~ q3); introgression breaks that symmetry by inflating the one matching the direction of gene flow. A high-bootstrap branch with gCF ~ 25 is a branch where the data are screaming disagreement that the bootstrap hides.

## Interpreting Concordance and Discordance

- **gCF / sCF (Minh 2020) are the honest support.** Bootstrap and localPP saturate near their ceiling at genome scale even when most loci disagree; gCF/sCF report the actual conflict. Report them on every phylogenomic tree.
- **localPP (Sayyari and Mirarab 2016) is NOT a bootstrap.** It is a coalescent posterior computed from the quartet frequencies around a branch. localPP = 1.0 is common and expected on resolved branches and does not mean "100 of 100 bootstraps"; localPP ~ 0.33 means the three quartet resolutions are tied (no resolution).
- **The polytomy test (Sayyari and Mirarab 2018) is the principled alternative to staring at low support.** It tests the null q1 = q2 = q3 (an effectively simultaneous speciation); failing to reject means a resolved bifurcation cannot be claimed -- collapse the branch.
- **Quartet symmetry separates ILS from introgression.** Symmetric minority quartets (q2 ~ q3) = ILS; handle with a coalescent tree. Asymmetric (q2 != q3, significant D-statistic / ABBA-BABA, HyDe gamma != 0, or QuIBL favoring the introgression component) = gene flow; a bifurcating tree cannot represent it -- model the reticulation. Confirm the asymmetry before invoking introgression.

## Per-Method Failure Modes

### Gene-Tree Estimation Error Biasing ASTRAL
**Trigger:** Short, low-information loci (e.g. <500 bp exons) fed to ASTRAL/wASTRAL as if their gene trees were truth.
**Mechanism:** MSC consistency assumes the input gene trees are correct; estimation error is a non-coalescent noise source that biases quartet counts in finite samples and can make the coalescent tree worse than concatenation.
**Symptom:** Coalescent tree noisier or worse than concatenation; unstable across locus subsets; low localPP everywhere; gCF far below sCF.
**Fix:** Contract gene-tree branches below ~10% bootstrap before ASTRAL (they become polytomies that contribute no spurious quartet similarity); better, use wASTRAL (continuous weighting); or drop to SVDQuartets (no gene trees) or BPP (integrates gene-tree uncertainty).

### Treating localPP as Bootstrap Support
**Trigger:** Reporting ASTRAL branch labels as bootstrap proportions, or demanding ">95% bootstrap" of an ASTRAL tree.
**Mechanism:** localPP is a coalescent posterior from quartet frequencies, on a different scale; it saturates at 1.0 on resolved branches.
**Symptom:** Over-confident reading of localPP = 1.0 as "100/100 BS"; ignoring that localPP ~ 0.33 is a near-tie.
**Fix:** Interpret localPP on its own scale; report gCF/sCF for honest conflict; use the polytomy test to decide whether to collapse a branch.

### Concatenating In or Near the Anomaly Zone
**Trigger:** Rapid radiation with several short successive internodes, analyzed by supermatrix ML with "100% bootstrap" reported as resolution.
**Mechanism:** Concatenation is inconsistent and positively misleading under high ILS; the plurality genealogy is anomalous, so adding loci converges on the wrong tree with rising support.
**Symptom:** Rock-solid bootstrap but gCF < 33 on focal branches; concatenated and coalescent trees disagree exactly there.
**Fix:** Use wASTRAL/ASTRAL (quartet-level consistency holds in the anomaly zone); report gCF/sCF; trust the coalescent topology on low-gCF branches; consider a true near-polytomy via the polytomy test.

### Ignoring Paralogy
**Trigger:** Discarding all multi-copy families to feed single-copy ASTRAL, or treating paralogs as orthologs.
**Mechanism:** Standard ASTRAL assumes single-copy gene trees; mis-assigned paralogs inject quartets reflecting the duplication history, not speciation.
**Symptom:** Massive data loss (most families dropped), or spurious clades / inflated discordance from hidden paralogy.
**Fix:** Use ASTRAL-Pro on the multi-copy gene-family trees (it models orthology/paralogy without pre-orthology); audit orthology upstream (comparative-genomics/ortholog-inference).

### Mistaking Introgression for ILS (or Vice Versa)
**Trigger:** Assuming all discordance is ILS and fitting a tree, OR over-calling gene flow from any discordance.
**Mechanism:** ILS produces symmetric minority topologies (q2 ~ q3); introgression breaks the symmetry. A bifurcating tree cannot represent reticulate history.
**Symptom:** Asymmetric q2/q3 on a discordant branch; significant D-statistic / HyDe gamma; QuIBL favoring the introgression component -- but a tree-only analysis hides it.
**Fix:** Test minority-quartet symmetry (D-statistic / ABBA-BABA, HyDe, QuIBL, ASTRAL q1/q2/q3) before interpreting; if asymmetric, model the reticulation rather than forcing a tree.

## Quantitative Thresholds

| Quantity | Threshold | Meaning / action | Source |
|----------|-----------|------------------|--------|
| Internode (coalescent units) | < ~1.0 | >25% of gene trees discordant; ILS material | P(concordant)=1-(2/3)e^(-tau) |
| Internode (coalescent units) | < ~0.3 | ~50% discordant; coalescent method required | same |
| Two+ successive internodes | both < ~0.1-0.2 | Anomaly-zone risk; concatenation positively misleading | Degnan and Rosenberg 2006 |
| Gene-tree branch support to contract before ASTRAL | < ~10% bootstrap (or use wASTRAL) | Collapse to polytomy to cut gene-tree-error bias | ASTRAL practice / Zhang and Mirarab 2022 |
| gCF | < 50 | Most loci disagree; distrust concatenation here | Minh 2020 |
| gCF | < 33 | Near the ILS coin-flip floor; effectively unresolved | Minh 2020 |
| sCF | ~33 | Random-resolution floor (three quartet resolutions); no site signal | Minh 2020 |
| localPP | ~0.95+ to call "well-supported" | Strong coalescent support, NOT a bootstrap | Sayyari and Mirarab 2016 |
| localPP | ~0.33 | Three quartet resolutions tied; candidate polytomy | Sayyari and Mirarab 2016 |
| Polytomy test p | fail to reject (e.g. p > 0.05) | Cannot claim a resolved bifurcation; collapse | Sayyari and Mirarab 2018 |

The gCF/sCF cutoffs of 50/33 are practical heuristics relative to the dataset (a branch at gCF 45 amid branches at 90 is the weak one), not significance tests. The 10% contraction is a widely-used default, not a derived optimum; wASTRAL removes the need to pick it.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| ASTER `astral` ignores the annotation flag | Used Java `-t 8` (annotation); ASTER `-t` is threads | Use `-u 2` in ASTER; `-t 8` only in classic Java |
| Coalescent tree worse than concatenation | Noisy gene trees fed in as truth | Contract <10% branches; use wASTRAL; or SVDQuartets |
| localPP = 1.0 reported as bootstrap | localPP is a coalescent posterior on its own scale | Report gCF/sCF; do not apply a BS cutoff |
| Coalescent-unit branch read as time | Branch lengths are coalescent units, tips undefined | State units; for dates use StarBEAST2 / divergence-dating |
| High bootstrap, low gCF, called resolved | Concatenation in the anomaly zone | Run coalescent; trust it on low-gCF branches; polytomy test |
| Most gene families dropped | Forced single-copy orthology | Use ASTRAL-Pro on multi-copy family trees |
| Network claimed from any discordance | ILS also produces discordance | Confirm q2 != q3 (D / HyDe / QuIBL) before invoking gene flow |

## References

Degnan JH, Rosenberg NA. 2006. Discordance of species trees with their most likely gene trees. *PLoS Genetics* 2(5):e68.
Degnan JH, Rosenberg NA. 2009. Gene tree discordance, phylogenetic inference and the multispecies coalescent. *Trends in Ecology & Evolution* 24(6):332-340.
Kubatko LS, Degnan JH. 2007. Inconsistency of phylogenetic estimates from concatenated data under coalescence. *Systematic Biology* 56(1):17-24.
Roch S, Steel M. 2015. Likelihood-based tree reconstruction on a concatenation of aligned sequence data sets can be statistically inconsistent. *Theoretical Population Biology* 100:56-62.
Mirarab S, Reaz R, Bayzid MS, Zimmermann T, Swenson MS, Warnow T. 2014. ASTRAL: genome-scale coalescent-based species tree estimation. *Bioinformatics* 30(17):i541-i548.
Zhang C, Rabiee M, Sayyari E, Mirarab S. 2018. ASTRAL-III: polynomial time species tree reconstruction from partially resolved gene trees. *BMC Bioinformatics* 19(Suppl 6):153.
Zhang C, Mirarab S. 2022. Weighting by gene tree uncertainty improves accuracy of quartet-based species trees. *Molecular Biology and Evolution* 39(12):msac215.
Zhang C, Scornavacca C, Molloy EK, Mirarab S. 2020. ASTRAL-Pro: quartet-based species-tree inference despite paralogy. *Molecular Biology and Evolution* 37(11):3292-3307.
Zhang C, Nielsen R, Mirarab S. 2025. ASTER: a package for large-scale phylogenomic reconstructions. *Molecular Biology and Evolution* 42(8):msaf172.
Sayyari E, Mirarab S. 2016. Fast coalescent-based computation of local branch support from quartet frequencies. *Molecular Biology and Evolution* 33(7):1654-1668.
Sayyari E, Mirarab S. 2018. Testing for polytomies in phylogenetic species trees using quartet frequencies. *Genes* 9(3):132.
Chifman J, Kubatko L. 2014. Quartet inference from SNP data under the coalescent model. *Bioinformatics* 30(23):3317-3324.
Flouri T, Jiao X, Rannala B, Yang Z. 2018. Species tree inference with BPP using genomic sequences and the multispecies coalescent. *Molecular Biology and Evolution* 35(10):2585-2593.
Ogilvie HA, Bouckaert RR, Drummond AJ. 2017. StarBEAST2 brings faster species tree inference and accurate estimates of substitution rates. *Molecular Biology and Evolution* 34(8):2101-2114.
Minh BQ, Hahn MW, Lanfear R. 2020. New methods to calculate concordance factors for phylogenomic datasets. *Molecular Biology and Evolution* 37(9):2727-2733.
Blischak PD, Chifman J, Wolfe AD, Kubatko LS. 2018. HyDe: a Python package for genome-scale hybridization detection. *Systematic Biology* 67(5):821-829.
Edelman NB, Frandsen PB, Miyagi M, et al. 2019. Genomic architecture and introgression shape a butterfly radiation. *Science* 366(6465):594-599.

## Related Skills

- modern-tree-inference - per-locus ML gene trees (ASTRAL input) and gCF/sCF computation
- bayesian-inference - full Bayesian co-estimation; StarBEAST2 for species tree plus dates
- divergence-dating - turning a coalescent-unit species tree into a dated tree
- tree-io - reading and writing the Newick gene-tree files ASTRAL consumes
- comparative-genomics/ortholog-inference - single-copy vs multi-copy decision upstream (ASTRAL vs ASTRAL-Pro)
<!-- END FILE: phylogenetics/species-trees/SKILL.md -->

## 子目录：phylogenetics/tree-io

<!-- BEGIN FILE: phylogenetics/tree-io/SKILL.md -->
---
name: bio-phylo-tree-io
description: Read, write, and convert phylogenetic tree files with Biopython Bio.Phylo, and choose an annotation-preserving parser (treeio, DendroPy) when metadata matters. Covers why a tree file is a lossy serialization, why format conversion silently drops BEAST/MrBayes node annotations (posteriors, HPD intervals, rates), the Newick support-vs-label ambiguity that mislabels bootstrap values, and the Nexus TRANSLATE and rooted/unrooted traps. Use when parsing Newick, Nexus, NHX, phyloXML, or NeXML, converting between formats, handling posterior tree sets, or moving annotated BEAST trees without losing the credible intervals. Routes annotation-critical reads to DendroPy or treeio and orthology/alignment context to sibling skills.
tool_type: python
primary_tool: Bio.Phylo
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+. Annotation-preserving alternatives: DendroPy 5+ (Python), treeio 1.26+ / ape 5.8+ (R).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(module.function)` to check signatures
- R: `packageVersion('treeio')` then `?read.beast` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Bio.Phylo stores a Newick `[&...]` bracket as opaque `.comment` text and does NOT parse BEAST key-values; DendroPy `extract_comment_metadata=True` and treeio `read.beast` do.

# Tree I/O -- A Tree File Is a Lossy Serialization

**"Read and convert my tree files"** -> Parse a tree into an in-memory object and re-serialize it, knowing which annotations each format and parser preserves.
- Python: `Phylo.read('tree.nwk', 'newick')`, `Phylo.convert(...)` (Bio.Phylo)
- Annotation-critical: `dendropy.Tree.get(..., extract_comment_metadata=True)` or treeio `read.beast()`

Scope: reading, writing, converting, and inspecting tree files, and selecting a parser that keeps the annotations the analysis needs. Rooting, pruning, collapsing -> tree-manipulation. Plotting and mapping annotations onto branches -> tree-visualization. Producing BEAST/MrBayes annotated trees -> bayesian-inference, divergence-dating. Taxon-name sanitization shares the whitespace traps in sequence-io/read-sequences.

## The Single Most Important Modern Insight

A tree file is a lossy serialization of a richer in-memory object. The biologist cares about the topology plus its annotations -- branch supports, posterior probabilities, 95% HPD intervals on node heights, per-branch rates, divergence dates, taxon metadata -- and formats differ enormously in which of these they can hold, while parsers differ in which they actually read back. Three load-bearing facts:

1. **Conversion is a silent data-destroying operation.** Reading a BEAST MCC tree and writing plain Newick produces a topologically identical tree that plots fine, but the HPD intervals, clade posteriors, and per-branch rates are gone and unrecoverable without re-running a multi-day MCMC. The loss is invisible until a reviewer asks where the credible intervals went.
2. **The tool, not the format string, decides whether `[&...]` metadata survives.** In Python the naive default (Bio.Phylo) drops BEAST key-values; in R the naive default (`ape::read.nexus`) drops them; the tools built to preserve them are DendroPy (`extract_comment_metadata=True`) and treeio (`read.beast`). Route annotated trees through those.
3. **In plain Newick a bare number has no fixed meaning.** In `(A,B)95:0.3` the `95` could be a bootstrap, a posterior, an internal clade name, or a second branch length. Only the tool that wrote the file knows; a parser that guesses wrong turns supports into names silently. IQ-TREE overloads the slot further, writing `SH-aLRT/UFBoot` (e.g. `87.5/98`), which a single-value parser truncates or chokes on.

## Tool Taxonomy

| Tool (lang) | BEAST `[&...]` | NHX | phyloXML richness | When |
|-------------|----------------|-----|-------------------|------|
| treeio (R) | YES, structured (`read.beast`/`read.mrbayes`/`read.iqtree`) | YES | via tidytree/ggtree | the default whenever annotations matter; feeds ggtree |
| DendroPy (Py) | YES, structured (`.annotations`) | YES | no | Python work needing metadata, posterior sets, tree distances, conversion with annotations |
| ETE3/ETE4 (Py) | partial (custom features) | YES, native | no | reconciliation, NHX round-trips, programmatic node features |
| Bio.Phylo (Py) | NO key-value parse (opaque `.comment`) | no | YES, richest | general pipelines, conversion among its 5 formats, phyloXML annotation |
| ape (R) | NO (drops `[&...]`) | no | no | fast topology/branch-length analysis; pair with treeio for annotated files |

References: Bio.Phylo Talevich 2012; DendroPy Sukumaran 2010; ETE3 Huerta-Cepas 2016; ape Paradis 2019; treeio Wang 2020.

One-line decision rule: if the file came from BEAST, MrBayes, or RevBayes or carries `[&...]`/`&&NHX` that matters, read it with treeio (R) or DendroPy (Py); otherwise Bio.Phylo (Py) or ape (R) is fine. Never route a BEAST MCC tree through `Bio.Phylo` or `ape::read.nexus` when the HPDs are needed.

## Format Capability (What Each Format Can Hold)

| Capability | Newick | NHX | Nexus (BEAST-annotated) | phyloXML | NeXML |
|------------|--------|-----|-------------------------|----------|-------|
| Topology + branch lengths | yes | yes | yes | yes | yes |
| One support value | ambiguous slot | `B=` tag | comment key | typed `<confidence>` | typed meta |
| Multiple supports per node | no (single slot) | tags | comment keys | yes (n elements) | yes |
| Posterior / HPD intervals | no | no | yes (`_95%_HPD={}`) | via property | via meta |
| Per-branch rates / dates | no | tags | yes | yes | yes |
| Taxonomy (NCBI id/rank) | no | `S=`/`T=` | no | yes, typed | yes |
| Schema-validated | no | no | loose | yes (XSD) | yes (XSD) |

Newick/NHX are compact and grep-able; phyloXML/NeXML are verbose XML (often 5-20x larger) but typed and validatable -- prefer XML for archiving/exchange where machine-checkable semantics matter, Newick/Nexus for pipeline interchange. BEAST/FigTree metadata rides inside a Nexus (or Newick) `[&...]` comment, so "it is a Nexus file" says nothing about whether annotations survive -- only the parser does.

## Reading, Writing, and Converting (Bio.Phylo)

**Goal:** Move trees between formats and inspect them without assuming a single tree or losing annotations.

**Approach:** Use `Phylo.read` for exactly one tree and `Phylo.parse` for many (posterior sets); use `Phylo.convert` only among formats of equal or greater capability; check `.confidence` vs `.name` to confirm support was read into the right slot.

```python
from Bio import Phylo

tree = Phylo.read('tree.nwk', 'newick')          # exactly one tree; raises if 0 or >1
posterior = list(Phylo.parse('run.trees', 'nexus'))   # many trees: posterior/bootstrap set
Phylo.write(tree, 'tree.xml', 'phyloxml')        # phyloXML is Bio.Phylo's richest format

Phylo.convert('tree.nex', 'nexus', 'tree.nwk', 'newick')   # WARNING: Newick cannot hold [&...]; annotations dropped

for clade in tree.get_nonterminals():
    print(clade.confidence, clade.name)          # confirm the support landed in .confidence, not .name
```

Supported format strings: `newick`, `nexus`, `phyloxml`, `nexml`, `cdao`. Colors and branch widths persist only in phyloXML.

## Preserve BEAST/MrBayes Annotations Before Down-Converting

**Goal:** Keep posteriors, HPD intervals, and rates when a downstream tool wants plain Newick.

**Approach:** Read with an annotation-aware parser, extract the numbers into a side table that travels with the analysis, and only then write a stripped topology -- never down-convert first.

```python
import dendropy

tree = dendropy.Tree.get(path='mcc.tree', schema='nexus', extract_comment_metadata=True)
for node in tree:
    if node.annotations.get_value('posterior') is not None:
        post = node.annotations.get_value('posterior')
        hpd = node.annotations.get_value('height_95%_HPD')   # raw BEAST key; treeio typically exposes it as height_0.95_HPD (exact name varies by source program and version -- introspect the columns)
        # persist post/hpd to a side table keyed by the clade before any conversion
tree.write(path='topology.nwk', schema='newick', suppress_annotations=True)   # intentional, after extraction
```

In R the equivalent is treeio `read.beast('mcc.tree')` then `get.data()` / `as_tibble()`, feeding ggtree (tree-visualization); `write.beast()` re-serializes with annotations intact.

## Per-Method Failure Modes

### BEAST/MrBayes MCC to Plain Newick Erases the Credible Intervals
**Trigger:** `Phylo.convert`, `ape::read.nexus` + `write.tree`, or any "just give me the topology" step on an annotated tree.
**Mechanism:** The HPDs, posteriors, and rates live only in the `[&...]` comments, which plain Newick cannot hold and stripping parsers discard.
**Symptom:** The output plots fine but the credible intervals are gone, irrecoverable without re-running the MCMC.
**Fix:** Read with treeio `read.beast` or DendroPy `extract_comment_metadata=True`; extract the numbers to a side table; keep the original `.tree` as the source of truth.

### Support Value Read as a Node Name (or Truncated)
**Trigger:** Parsing a tree whose internal-node slot holds a bootstrap, a posterior, a clade name, or IQ-TREE's `SH-aLRT/UFBoot` dual value.
**Mechanism:** The Newick grammar gives one slot for all of these; the parser must be told which it is, and a single-value reader truncates the `/`-delimited dual support.
**Symptom:** Supports appear as `.name` strings, or only one of two IQ-TREE values survives, or the parse errors on `/`.
**Fix:** Know what wrote the file; in Bio.Phylo inspect `.confidence` vs `.name`; in treeio use `read.iqtree`/`read.raxml`, which split dual support correctly.

### Whitespace, Underscore, or Non-ASCII Taxon Names
**Trigger:** Tip names with spaces, parentheses, commas, or accented characters; reliance on the Newick underscore-space convention.
**Mechanism:** Naive CLI tools split unquoted spaces, and underscore-to-space auto-conversion silently desyncs tip labels from a metadata join key.
**Symptom:** Downstream tools error or a metadata merge matches nothing.
**Fix:** Sanitize to `[A-Za-z0-9_.]`, single-quote when spaces are unavoidable, and round-trip-test the labels against the metadata table before any join.

### Nexus TRANSLATE-Table Desync and Rooted/Unrooted Confusion
**Trigger:** Hand-editing or merging Nexus tree blocks; assuming topology shape implies rootedness.
**Mechanism:** The integer-to-name TRANSLATE map can decouple from the tree and silently relabel tips; Newick does not flag rootedness (a basal trifurcation conventionally signals unrooted, but tools disagree), while Nexus carries an explicit `[&R]`/`[&U]`.
**Symptom:** Tips are mislabeled after a merge, or a rooting-sensitive analysis runs on the wrong assumption without erroring.
**Fix:** Parse with a translate-aware reader (treeio/DendroPy/ape apply it); verify tip-label sets match across merged trees; set rootedness explicitly rather than trusting topology shape.

## Quantitative and Practical Notes

| Item | Guidance | Why |
|------|----------|-----|
| Support-value scales | bootstrap/UFBoot in [0,100], posterior in [0,1], SH-aLRT in [0,100] | a number is meaningless without knowing which test produced it; preserve provenance, not just the value |
| Multi-tree files | use `Phylo.parse` / DendroPy `TreeList` / treeio `read.beast`; check object length | a single-tree reader on a `.trees` posterior returns only the first or errors |
| Round-trip test | read -> write -> read and diff the annotations, not just the topology | topology almost always survives and gives false confidence |
| Posterior set vs MCC | `.trees` is the full posterior; `.tree`/`.mcc` is the single annotated summary | `read.beast` on a full posterior is huge; usually the MCC is wanted |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| HPD bars missing after conversion | converted a BEAST tree to Newick | extract annotations with treeio/DendroPy first |
| `Phylo.read` raises on a `.trees` file | multiple trees in the file | use `Phylo.parse` and iterate |
| Bootstrap values show up as taxon names | node-label slot read as `.name` | set/inspect confidence parsing; use a software-specific reader |
| Metadata join matches nothing | underscore/space relabeling of tips | sanitize and round-trip-test labels before joining |
| Parser errors on `[` | strict parser chokes on FigTree comment | strip comments only after extracting needed metadata |

## References

Cock PJA, Antao T, Chang JT, et al. 2009. Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics* 25(11):1422-1423.
Talevich E, Invergo BM, Cock PJA, Chapman BA. 2012. Bio.Phylo: a unified toolkit for processing, analyzing and visualizing phylogenetic trees in Biopython. *BMC Bioinformatics* 13:209.
Sukumaran J, Holder MT. 2010. DendroPy: a Python library for phylogenetic computing. *Bioinformatics* 26(12):1569-1571.
Huerta-Cepas J, Serra F, Bork P. 2016. ETE 3: reconstruction, analysis, and visualization of phylogenomic data. *Molecular Biology and Evolution* 33(6):1635-1638.
Paradis E, Schliep K. 2019. ape 5.0: an environment for modern phylogenetics and evolutionary analyses in R. *Bioinformatics* 35(3):526-528.
Wang L-G, Lam TT-Y, Xu S, et al. 2020. Treeio: an R package for phylogenetic tree input and output with richly annotated and associated data. *Molecular Biology and Evolution* 37(2):599-603.
Maddison DR, Swofford DL, Maddison WP. 1997. NEXUS: an extensible file format for systematic information. *Systematic Biology* 46(4):590-621.
Han MV, Zmasek CM. 2009. phyloXML: XML for evolutionary biology and comparative genomics. *BMC Bioinformatics* 10:356.
Vos RA, Balhoff JP, Caravas JA, et al. 2012. NeXML: rich, extensible, and verifiable representation of comparative data and metadata. *Systematic Biology* 61(4):675-689.

## Related Skills

- tree-manipulation - rooting, pruning, and collapsing where rooted/unrooted and polytomy choices bite
- tree-visualization - ggtree and ETE consume the annotations preserved here
- bayesian-inference - produces the BEAST/MrBayes annotated trees whose metadata must survive
- divergence-dating - produces MCC trees with HPD intervals on node ages
- sequence-io/read-sequences - taxon-name sanitization shares the whitespace and non-ASCII traps
<!-- END FILE: phylogenetics/tree-io/SKILL.md -->

## 子目录：phylogenetics/tree-manipulation

<!-- BEGIN FILE: phylogenetics/tree-manipulation/SKILL.md -->
---
name: bio-phylo-tree-manipulation
description: Edit phylogenetic tree structure with Biopython Bio.Phylo, and treat rooting as a separate statistical inference rather than a display choice. Covers why most inference returns an unrooted tree so placing the root creates every ancestor/descendant and basal claim; why a distant or lonely outgroup misroots inside the ingroup via long-branch attraction; the outgroup/midpoint/MAD/MinVar/non-reversible-likelihood rooting tradeoffs; why pruning must suppress degree-2 nodes and sum their branch lengths or all patristic distances silently corrupt; and why collapsing by support makes SOFT (uncertainty) polytomies, not HARD (radiation) ones. Use when rooting, re-rooting, pruning or subsetting taxa, extracting a clade or induced subtree, collapsing low-support branches, resolving polytomies, or ladderizing. Routes clock-based rooting to divergence-dating, inference to modern-tree-inference, and reading/plotting to tree-io and tree-visualization.
tool_type: mixed
primary_tool: Bio.Phylo
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+. Alternatives: ape 5.8+ / phangorn / phytools (R), DendroPy 5+ and ete3 (Python), Newick Utilities 1.6+, MAD and RootDigger as standalone CLIs.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(module.function)` to check signatures
- R: `packageVersion('ape')` then `?drop.tip` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

ape has NO midpoint function of its own (use phangorn::midpoint or phytools::midpoint.root); ete3 prune drops branch lengths unless preserve_branch_length=True; ape di2multi filters by branch LENGTH (tol), not support.

# Tree Manipulation -- Rooting Is an Inference, Not a Cosmetic Operation

**"Root and prune my tree"** -> Edit an existing tree object, treating the root placement as a separate statistical inference and every structural edit as potentially distance-corrupting.
- Python: `tree.root_with_outgroup(...)`, `tree.root_at_midpoint()`, `tree.prune(...)`, `tree.collapse_all(...)` (Bio.Phylo)
- R: `root()`, `phangorn::midpoint()`, `drop.tip()`, `di2multi()` (ape/phangorn); CLI: `nw_reroot`, `nw_prune` (Newick Utilities); outgroup-free rooters: `mad`, `FastRoot.py`, `rootdigger`

Scope: editing an existing tree -- rooting, pruning/subsetting, extracting clades or induced subtrees, collapsing branches into polytomies, resolving polytomies, ladderizing. Reading/writing/converting tree files -> tree-io. Plotting and mapping annotations -> tree-visualization. Inferring the tree in the first place -> modern-tree-inference. Clock-based or Bayesian rooting co-estimated with dates -> divergence-dating.

## The Single Most Important Modern Insight

Rooting is a separate statistical inference layered on top of the topology, and it is the highest-error decision in the entire tree. Nearly every inference method (ML under a time-reversible model, neighbor-joining, most Bayesian runs) returns an UNROOTED tree: a reversible model is blind to the direction of time, so the likelihood is identical wherever the root sits. The unrooted tree states which taxa are neighbors; it is silent about who is ancestor and who is descendant. Placing the root is what converts a neighbor-graph into an evolutionary narrative, and it CREATES every "X is basal", every "the common ancestor had trait T", every character-polarity, every divergence ordering. Three load-bearing facts:

1. **Rooting needs its own justification and its own uncertainty statement, distinct from branch support.** Bootstrap 95 on an ingroup clade says nothing about whether the root is in the right place. The relationships can be robust while the root -- the thing every downstream story hangs on -- is the least reliable part of the figure.
2. **The deep nodes near an outgroup-defined root are the LEAST trustworthy.** A distant outgroup sits on a long branch, and long branches attract each other (long-branch attraction): the outgroup pulls the fastest ingroup taxon toward the root and makes it look artifactually "basal". Accuracy degrades monotonically as outgroup distance grows.
3. **The choice of rooting METHOD is a modeling choice with assumptions** (clock? outgroup monophyly? non-reversible model?), and the wrong method silently fabricates basal lineages. Pruning, collapsing, and ladderizing are comparatively mechanical -- but each has its own silent traps (distance corruption, soft/hard polytomy conflation, perceived trends).

## Rooting Method Decision

| Method | Core assumption | Needs | Robust to rate variation | Gives root uncertainty | Best when | Avoid when |
|--------|-----------------|-------|--------------------------|------------------------|-----------|------------|
| Outgroup (multiple, close) | outgroup truly outside ingroup, not LBA-misplaced | a priori outgroup taxa + sequences | moderate (depends on outgroup branch) | weakly (via ingroup-monophyly check) | closely related, balanced, monophyletic outgroups exist | only a distant/lonely outgroup available |
| Outgroup (single) | same, but one long branch | one outgroup taxon | poor (max LBA exposure) | no | a close single sister exists, nothing better | only a distant/lonely outgroup (one long branch, max LBA exposure) |
| Midpoint | strict molecular clock | tree with branch lengths | no | no | shallow, clock-like, intraspecific/viral data | deep trees, heterotachy, any long branch |
| MinVar | clock deviations are random/unbiased | tree with branch lengths | better than midpoint | no | outgroup-free, noise looks like unbiased clock scatter | strong lineage-specific rate shifts |
| MAD | minimal relative ancestor deviation | tree with branch lengths | yes (tolerates heterotachy) | yes (root ambiguity index) | outgroup-free deep/prokaryotic trees; default no-outgroup choice | strongly structured rate variation |
| Non-reversible likelihood (RootDigger / IQ-TREE) | non-reversible model carries directional signal | tree + ALIGNMENT; enough data | yes (model-based) | yes (per-branch likelihood confidence) | the alignment is available and a root confidence is needed | little data; weak signal; compute-limited |
| Relaxed clock (BEAST) -> divergence-dating | explicit clock + tree prior | alignment + calibrations/tip dates; MCMC | yes | yes (posterior over roots) | time-scaled / dated / phylodynamic analyses | a quick structural edit, no dating intended |

Rule: never report a root from a single method without a sanity check. If a close, monophyletic outgroup is available, use it. If not, run MAD and MinVar and prefer agreement; disagreement means the root is poorly determined and all "basal" claims must be hedged. With an alignment and a need for a confidence value, use RootDigger (Bettisworth and Stamatakis 2021) or non-reversible IQ-TREE. MAD = Tria et al. 2017; MinVar = Mai et al. 2017; outgroup-free CLIs and Newick Utilities = Junier and Zdobnov 2010.

## Tool Taxonomy

| Tool (lang) | Rooting | Pruning / clade | Collapse / resolve | When |
|-------------|---------|-----------------|--------------------|------|
| Bio.Phylo (Py) | `root_with_outgroup`, `root_at_midpoint` | `prune`, `common_ancestor` | `collapse_all` | general Python pipelines; the default here |
| ape / phangorn / phytools (R) | `root`, `phangorn::midpoint`, `phytools::midpoint.root` | `drop.tip`, `extract.clade` | `di2multi`, `multi2di` | R workflows; `drop.tip` sums suppressed branch lengths correctly |
| DendroPy (Py) | `reroot_at_edge`, `reroot_at_midpoint` | `retain_taxa_with_labels(suppress_unifurcations=True)` | edge collapse, `resolve_polytomies` | metadata-aware edits, posterior tree sets |
| ete3 (Py) | `set_outgroup`, `set_outgroup(get_midpoint_outgroup())` | `prune([...], preserve_branch_length=True)`, `detach` | `delete`, `resolve_polytomy` | NHX features; MUST pass preserve_branch_length |
| Newick Utilities (CLI) | `nw_reroot` | `nw_prune`, `nw_clade` | `nw_ed`, `nw_condense` | streaming/Unix-pipeline edits on many trees |
| MAD / MinVar / RootDigger (CLI) | `mad`, `FastRoot.py`, `rootdigger` | -- | -- | outgroup-free or likelihood rooting when no trustworthy outgroup exists |

## Root with an Outgroup (Multiple, Monophyletic)

**Goal:** Root the tree using known sister-group taxa, preferring multiple close outgroups and verifying ingroup monophyly first.

**Approach:** Confirm the outgroup taxa form a monophyletic group, root on the branch separating them from the ingroup, then check the ingroup is recovered as monophyletic -- if not, the rooting is suspect.

```python
from Bio import Phylo

tree = Phylo.read('tree.nwk', 'newick')
outgroup = [{'name': 'OutA'}, {'name': 'OutB'}]      # multiple close outgroups beat a single long branch

if tree.is_monophyletic([tree.find_any(name='OutA'), tree.find_any(name='OutB')]):
    tree.root_with_outgroup(*outgroup)               # root_with_outgroup, NOT root_with_midpoint
else:
    print('outgroup not monophyletic: root placement is unreliable, re-check taxon choice')
```

## Root at the Midpoint (Clock-Limited Fallback)

**Goal:** Root an outgroup-free tree where evolution is approximately clock-like (shallow/viral data).

**Approach:** Place the root at the midpoint of the longest tip-to-tip path; trust it only when no single long branch can hijack that path. For deep trees with rate variation prefer MAD/MinVar.

```python
tree = Phylo.read('tree.nwk', 'newick')
tree.root_at_midpoint()                              # assumes a clock; a long branch slides the root onto the fast lineage
# Outgroup-free and clock-relaxed (deep trees): standalone CLIs run on the Newick file
# MAD:    mad tree.nwk           -> tree.nwk.rooted   (per-branch root ambiguity index)
# MinVar: FastRoot.py -i tree.nwk -m MV -o rooted.nwk
```

## Prune Taxa With Branch-Length Preservation

**Goal:** Remove tips and keep every surviving patristic distance unchanged.

**Approach:** Drop the tip and SUPPRESS the resulting degree-2 ("knee") node, ADDING its branch length to the child so path lengths are conserved. Bio.Phylo `prune` and ape `drop.tip` do this by default; ete3 `prune` needs `preserve_branch_length=True`.

```python
tree = Phylo.read('tree.nwk', 'newick')
keep = {'Human', 'Chimp', 'Mouse'}

for term in list(tree.get_terminals()):
    if term.name not in keep:
        tree.prune(term)                             # collapses the degree-2 parent and sums branch lengths
# ape (R):   drop.tip(phy, c('X','Y'))               # sums suppressed branch lengths by default
# ete3 (Py): tree.prune(list(keep), preserve_branch_length=True)   # the flag is mandatory, else distances shrink
```

Non-monophyletic targets cannot be "extracted as a clade" -- there is no node whose descendants are exactly those taxa. Prune to the taxon set to get the induced subtree instead; `common_ancestor` of non-monophyletic taxa returns an MRCA whose clade contains EXTRA taxa.

## Collapse Low-Support Branches Into SOFT Polytomies

**Goal:** Replace poorly-supported resolved nodes with multifurcations that honestly say "unresolved".

**Approach:** Collapse any internal branch whose support is below a stated cutoff. The result is a SOFT (uncertainty) polytomy, never a HARD (simultaneous-radiation) one -- label it as such.

```python
tree = Phylo.read('tree.nwk', 'newick')              # support parsed into clade.confidence

tree.collapse_all(lambda c: c.confidence is not None and c.confidence < 70)   # 70 for std bootstrap; use 95 for UFBoot2
tree.collapse_all(lambda c: c.branch_length is not None and c.branch_length < 1e-8)   # collapse genuinely-zero branches
# ape (R): di2multi filters by LENGTH (tol), not support -> zero out low-support branch lengths first, THEN di2multi(phy)
```

Resolving the inverse direction (`multi2di` / `resolve_polytomy`) invents an arbitrary order with zero-length branches; analyzing one random resolution treats an arbitrary choice as fact. If a binary tree is required, integrate over many random resolutions and treat the inserted zero-length branches as "no information", not instantaneous divergence.

## Per-Method Failure Modes

### Distant Outgroup Roots Inside the Ingroup
**Trigger:** A single distant outgroup, or many outgroups all far from the ingroup, used to root.
**Mechanism:** The long outgroup branch attracts the fastest ingroup taxon (LBA), pulling the root into the ingroup; far outgroups attach at essentially random positions (DeSalle et al. 2023).
**Symptom:** Ingroup not recovered as monophyletic; a fast taxon appears "basal"; the root jumps as the outgroup set changes.
**Fix:** Use multiple CLOSELY-related, monophyletic, roughly-equidistant outgroups; verify ingroup monophyly; treat a lonely distant outgroup as a red flag.

### Single Distant Outgroup -- Long-Branch Misrooting
**Trigger:** Rooting on one distant outgroup taxon.
**Mechanism:** One unbroken long branch maximizes LBA exposure, with no way to subdivide it or check ingroup monophyly, so the root is drawn toward other long branches.
**Symptom:** The root lands inside the ingroup or on a spurious deep branch; deep nodes near the root are unstable across analyses.
**Fix:** Add multiple closer, monophyletic outgroups to subdivide the long branch and enable a monophyly check, or use an outgroup-free method (MAD/MinVar).

### Midpoint Misroots Under Rate Variation
**Trigger:** Midpoint rooting a deep tree with heterotachy or any long branch.
**Mechanism:** Midpoint assumes a clock; a long branch hijacks the longest path and slides the root onto the fast lineage.
**Symptom:** A rate-elevated taxon appears earliest-diverging; the root sits on a suspiciously long branch.
**Fix:** Use MAD or MinVar (clock-relaxed) or a close outgroup; report root uncertainty and hedge "basal".

### Soft vs Hard Polytomy Conflation
**Trigger:** Collapsing branches below a support threshold, then describing the multifurcation as a radiation.
**Mechanism:** Threshold-collapse encodes UNCERTAINTY (soft polytomy = "we cannot resolve the order"); a hard polytomy is a biological claim of simultaneous divergence -- different meanings.
**Symptom:** A paper claims simultaneous divergence from what is just unresolved data.
**Fix:** Label threshold-collapsed nodes as unresolved/soft; never read them as a biological radiation.

### Pruning Leaves a Spurious Node or Drops Distances
**Trigger:** A tool that leaves the degree-2 node in place, or removes it without summing branch lengths (notably ete3 `prune` without `preserve_branch_length=True`).
**Mechanism:** The suppressed knee's branch length is not added to its child, so every path through that lineage shortens.
**Symptom:** Patristic distances shrink; subsequent midpoint/MAD/MinVar rooting on the pruned tree is now wrong.
**Fix:** Use Bio.Phylo `prune` / ape `drop.tip` (correct by default) or pass ete3 `preserve_branch_length=True`; verify a known pairwise distance is unchanged.

### Randomly Resolving a Polytomy Biases Downstream
**Trigger:** `multi2di` / `resolve_polytomy` to satisfy a binary-tree requirement, then analyzing the single tree.
**Mechanism:** An arbitrary order with zero-length branches is invented; the downstream result depends on a topology the data never supported.
**Symptom:** Results that change under a different random resolution.
**Fix:** Integrate over many resolutions and summarize; treat zero-length branches as "no info", not instantaneous divergence.

### Ladderizing Manufactures an Apparent Trend
**Trigger:** Ladderizing a figure so one lineage sits visually at the top/bottom.
**Mechanism:** Rotation about internal nodes changes no topology, branch lengths, or bipartitions, but readers unconsciously read the staircase as an early-to-late sequence.
**Symptom:** Reviewers infer a basal-to-derived trend that does not exist.
**Fix:** Ladderize only for legibility; state that rotation changes no biology. -> tree-visualization.

## Quantitative Thresholds

| Quantity | Value | Source / rationale |
|----------|-------|--------------------|
| Midpoint root recovery, single-outgroup source data | ~54% (barely a coin flip) | Hess and Russo 2007 |
| Midpoint root recovery, multiple-outgroup source data | ~82% (inconsistent) to ~94% (consistent) | Hess and Russo 2007 |
| MAD accuracy on benchmarks | >~70%, beating midpoint | Tria et al. 2017 |
| MinVar vs midpoint | matched or beat midpoint in all simulated conditions | Mai et al. 2017 |
| Bootstrap collapse cutoff | <50% (near-uninformative floor) or <70% (reliability boundary); state which | common practice |
| UFBoot2 collapse cutoff | <95% (a different scale from bootstrap -- not 70) | Hoang 2018 |
| Bayesian posterior collapse cutoff | <0.95 | common practice |
| Zero-length collapse tolerance | ~1e-8 (or machine epsilon) | removes genuinely-zero branches without deleting real short ones |
| Outgroup distance | accuracy degrades monotonically with distance | prefer the closest credible outgroup |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `ape::midpoint` function-not-found | midpoint is not in base ape | use `phangorn::midpoint` or `phytools::midpoint.root` |
| Pruned tree has wrong distances | degree-2 node not suppressed / not summed | Bio.Phylo `prune` / ape `drop.tip` default, or ete3 `preserve_branch_length=True` |
| "Extract the clade of X,Y,Z" returns extra taxa or None | X,Y,Z are not monophyletic | prune to the taxon set (induced subtree) instead of extracting a clade |
| `di2multi(tol)` did not drop low-support nodes | `tol` filters branch LENGTH, not support | zero out low-support branch lengths first, then `di2multi` |
| Bootstrap re-read as support for a pruned subtree | support was computed on the full taxon set | re-run inference on the subset for valid support |
| MAD and MinVar disagree on the root | the root is genuinely poorly determined | treat as uncertain; seek a close outgroup or RootDigger confidence; hedge all ancestral claims |
| `root_with_midpoint` AttributeError | no such method | the methods are `root_at_midpoint()` and `root_with_outgroup()` |

## References

Tria FDK, Landan G, Dagan T. 2017. Phylogenetic rooting using minimal ancestor deviation. *Nature Ecology & Evolution* 1:0193.
Mai U, Sayyari E, Mirarab S. 2017. Minimum variance rooting of phylogenetic trees and implications for species tree reconstruction. *PLOS ONE* 12(8):e0182238.
Bettisworth B, Stamatakis A. 2021. Root Digger: a root placement program for phylogenetic trees. *BMC Bioinformatics* 22:225.
Hess PN, De Moraes Russo CA. 2007. An empirical test of the midpoint rooting method. *Biological Journal of the Linnean Society* 92(4):669-674.
DeSalle R, Narechania A, Tessler M. 2023. Multiple outgroups can cause random rooting in phylogenomics. *Molecular Phylogenetics and Evolution* 184:107806.
Junier T, Zdobnov EM. 2010. The Newick utilities: high-throughput phylogenetic tree processing in the Unix shell. *Bioinformatics* 26(13):1669-1670.
Huerta-Cepas J, Serra F, Bork P. 2016. ETE 3: reconstruction, analysis, and visualization of phylogenomic data. *Molecular Biology and Evolution* 33(6):1635-1638.
Paradis E, Schliep K. 2019. ape 5.0: an environment for modern phylogenetics and evolutionary analyses in R. *Bioinformatics* 35(3):526-528.

## Related Skills

- tree-io - reading and writing the trees these edits consume and produce, without dropping annotations
- tree-visualization - ladderize is a perception choice; mapping support onto branches
- divergence-dating - clock-based and Bayesian rooting co-estimated with node ages, not bolted on by midpoint
- modern-tree-inference - produces the unrooted ML tree and the support values these edits act on
<!-- END FILE: phylogenetics/tree-manipulation/SKILL.md -->

## 子目录：phylogenetics/tree-visualization

<!-- BEGIN FILE: phylogenetics/tree-visualization/SKILL.md -->
---
name: bio-phylo-tree-visualization
description: Draw and export phylogenetic trees with Bio.Phylo plus matplotlib, and route rich figures to ggtree, ETE4, or iTOL. Covers why a tree figure is an argument not a neutral picture, the cladogram-vs-phylogram-vs-chronogram choice that hides or reveals rate and time, how ladderization manufactures a false arrow of progress, why an unlabeled support number always flatters the result (bootstrap vs posterior vs SH-aLRT vs UFBoot are different scales), why Bio.Phylo silently drops BEAST HPD bars so annotated Bayesian trees must go through treeio plus ggtree, and the tip-count and raster-vs-vector thresholds for legible publication figures. Use when drawing a tree, choosing a layout, coloring branches, showing or labeling support, exporting vector figures, or deciding a drawing tool. Routes annotation-preserving reads to tree-io, and rooting and ladderizing to tree-manipulation.
tool_type: python
primary_tool: Bio.Phylo
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, matplotlib 3.8+. Rich-figure alternatives: ggtree 3.12+ / treeio 1.28+ / ggtreeExtra 1.14+ (Bioconductor), ete4 4.x (Python), iTOL v6 (web), FigTree (desktop).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Phylo.draw)` to check signatures
- R: `packageVersion('ggtree')` then `?ggtree` to verify layout and geom arguments

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Bio.Phylo `draw()` renders rectangular layouts only and parses no BEAST/MrBayes annotation block; circular/fan/unrooted layouts and HPD bars require ggtree, ETE4, or iTOL. The ETE3->ETE4 migration changed APIs; introspect rather than assume ETE3 signatures.

# Tree Visualization -- A Figure Is an Argument

**"Draw and export my tree figure"** -> Render a topology under a chosen layout and branch-length encoding, decide which support to show and how to label it, and export in a format that survives print.
- Python quick look: `Phylo.draw(tree, axes=ax)` (Bio.Phylo + matplotlib)
- Publication with metadata, rich support, or BEAST HPD bars: ggtree + treeio (R)

Scope: drawing, styling, annotating, and exporting tree figures, and choosing the drawing tool. Reading/converting files and preserving `[&...]` annotations before plotting -> tree-io. Rooting, ladderizing, pruning, collapsing low-support nodes -> tree-manipulation. ggplot2 grammar, themes, and `ggsave` underlying ggtree -> data-visualization/ggplot2-fundamentals. Composing a tree plus aligned panels into one figure -> data-visualization/multipanel-figures.

## The Single Most Important Modern Insight

A phylogenetic tree figure is a rhetorical and modeling artifact, not a neutral picture of the data. A Newick or Nexus file encodes a topology, optionally branch lengths, optionally one node label; it does NOT encode which child is drawn on top, whether the horizontal axis means evolutionary distance or just nesting depth, where the root sits, the aspect ratio, or which of several support measures a bare "95" refers to. Every one of those is supplied by the person drawing the tree, so the figure is the data filtered through a dozen interpretive choices the reader cannot see. Four argument-level decisions dominate, and the same file can be drawn to tell mutually contradictory stories that are all technically correct renderings of one topology:

1. **The geometry is a claim about what the lengths mean.** A cladogram asserts only nesting; a phylogram asserts nesting plus amount of change (substitutions per site); a chronogram asserts timing and demands a clock model plus calibrations. Drawing a phylogram as a cladogram erases rate variation, the very signal that flags long-branch attraction; drawing untrusted branch lengths as a phylogram fabricates a quantitative claim.
2. **Ladderization implies a directionality that is not there.** Sibling subclades are unordered, so any node rotation is the same tree, but the eye reads top-to-bottom ordering as a march of progress toward the bottom-most tip. Rotation can also bury non-monophyly: a paraphyletic group can be rotated to look contiguous, or a clean clade made to look scattered.
3. **Which support is shown, and whether it is labeled, changes the conclusion.** Support is not accuracy, and the measures are not interchangeable: a posterior of 0.95 is generally weaker evidence than a bootstrap of 95 for the same data, and UFBoot 95, SH-aLRT 80, and TBE live on different scales. A bare integer with no legend is the quietest lie because the reader assumes bootstrap and the ambiguity always flatters the result.
4. **The drawing tool is decided by the I/O layer, not the surrounding language.** If the tree carries BEAST/MrBayes HPD intervals and posteriors, only a tool whose data model can carry those annotations (treeio + ggtree) can plot them; Bio.Phylo flattens the tree to topology + length + one label and silently drops the uncertainty that was the result.

The skill's job is to make these choices conscious and DECLARE them in the caption, not to default into them. Default ladderization plus cladogram-ish rendering plus unlabeled nodes is the path of least resistance, and it is an argument the user did not intend to make.

## Tool Taxonomy

The central decision is which drawing tool to reach for, and it is coupled to the I/O decision: a tool that flattens the tree to topology plus one label cannot draw BEAST HPD bars or posteriors it cannot represent. The plotting path through treeio + ggtree is the same I/O choice made in tree-io.

| Tool (lang) | Citation | Layouts and annotation power | When to choose |
|-------------|----------|------------------------------|----------------|
| Bio.Phylo + matplotlib (Py) | Talevich 2012 | rectangular phylogram/cladogram only; one label per node via `label_func`/`branch_labels`; no circular/unrooted, no BEAST-block parse | a fast scripted look inside a Python pipeline; headless/CI rendering of simple trees; NOT publication figures with metadata or HPD bars |
| ggtree + treeio + ggtreeExtra (R) | Yu 2017; Wang 2020; Xu 2021 | rectangular, slanted, circular, fan, radial/unrooted; `%<+%` attaches a data.frame, `geom_tiplab`/`geom_nodelab`/`geom_cladelab`, `gheatmap`, `geom_facet` (Cartesian) or `geom_fruit` rings (circular); treeio reads BEAST/MrBayes/IQ-TREE so HPD bars and posterior plot directly | the publication standard whenever a figure integrates metadata, rich/dual support, HPD bars, or aligned panels; the only clean path for BEAST HPD bars and posterior |
| ETE4 (Py; ETE3 paper) | Huerta-Cepas 2016 | rectangular and circular; programmatic per-node `NodeStyle`/faces and layout functions; integrated NCBI taxonomy | styling thousands of nodes by rule, taxonomy-driven annotation, or rendering many trees headlessly in Python |
| iTOL v6 (web) | Letunic 2024 | rectangular, circular, unrooted, very large trees; tab-delimited dataset templates for color strips, heatmaps, bars, binary symbols, clade collapse; SVG/PDF/PNG/EPS export | large trees and template-based metadata with no code; collaborative web-driven polished figures |
| FigTree (desktop GUI) | Rambaut (software) | rectangular, polar, radial; reads BEAST NEXUS node annotations to display HPD bars and posterior on screen; manual rotate/collapse/color | interactive inspection of a single BEAST/MrBayes tree before scripting the final figure; not reproducible, use for exploration not the pipeline |

Decision rule: large tree or no-code web annotation -> iTOL v6. Publication figure with metadata, dual support, HPD bars, or aligned heatmaps -> ggtree + treeio (+ ggtreeExtra for circular rings). Programmatic styling of thousands of nodes or NCBI-taxonomy annotation -> ETE4. Fast topology look from a Python script -> Bio.Phylo. Interactive rooting/inspection of one BEAST tree -> FigTree, then move the reproducible figure to ggtree. The recurring mistake is defaulting to Bio.Phylo because the pipeline is Python, then discovering it cannot draw a circular layout, place a heatmap, or show the BEAST HPD bars that are the whole point.

## What Each Layout Reveals and Hides

| Layout | Reveals | Hides or distorts | Good for | Bad for |
|--------|---------|-------------------|----------|---------|
| Rectangular phylogram | branch lengths read directly off a linear axis; honest distance comparison | tip labels overplot past a few hundred tips; uses vertical space | the default when length matters and tip count is moderate (<~150) | very large trees |
| Slanted / triangular | compactness; quick topology read | the diagonal implies a ladder/progression; imprecise length reading | quick schematic topology views | precise branch-length comparison |
| Circular / fan | hundreds to thousands of tips in one panel; metadata rings | radial distortion -- the same length subtends a larger arc near the rim, so distance is perceptually compressed near the root; near-root structure cramped | big trees where the message is broad structure plus aligned metadata | quantitative branch-length comparison |
| Unrooted / radial | honestly shows NO assumed root or time direction; overall shape and long-branch outliers | no time direction; clade membership harder to trace; clusters over-read as clades | exploratory views, "no root committed" | directional stories; any "basal/early-diverging" claim |
| Chronogram (time-tree) | node timing on a time axis | requires a clock model and calibrations the reader must trust; without HPD bars timing looks falsely precise | dated BEAST/treePL/MCMCtree trees where timing is the message | any tree lacking a clock; never draw without age uncertainty bars |

Circular is still a ROOTED tree bent into a ring (center = root = past); unrooted/radial explicitly refuses a root. Presenting an unrooted radial tree and narrating "X is basal" is a contradiction.

## Bio.Phylo + matplotlib Recipes

Quick text and ASCII inspection, no figure needed:

```python
from Bio import Phylo

tree = Phylo.read('tree.nwk', 'newick')
print(tree)                  # indented text summary
Phylo.draw_ascii(tree)       # ASCII-art diagram, useful in a terminal or log
```

Draw to a vector file (always pass an axes and `do_show=False` for headless/scripted use):

```python
from Bio import Phylo
import matplotlib.pyplot as plt

tree = Phylo.read('tree.nwk', 'newick')
tree.ladderize()             # legibility only; ordering carries NO phylogenetic meaning -- say so in the caption

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax, do_show=False)
ax.set_title('Phylogenetic tree (phylogram, branch length = subs/site)')
fig.savefig('tree.pdf', bbox_inches='tight')   # vector: text and lines stay sharp at any size
plt.close(fig)
```

Label tips, and show support with its measure named (never a bare integer):

```python
def tip_only(clade):
    return clade.name if clade.is_terminal() else ''

def support_label(clade):
    # the measure MUST be stated in the legend/caption; here values are bootstrap percentages
    if not clade.is_terminal() and clade.confidence is not None:
        return f'{clade.confidence:.0f}'
    return ''

fig, ax = plt.subplots(figsize=(12, 10))
Phylo.draw(tree, axes=ax, do_show=False, label_func=tip_only, branch_labels=support_label)
ax.set_title('Bootstrap support shown at internal nodes')
fig.savefig('supported_tree.svg', bbox_inches='tight')
plt.close(fig)
```

Color branches by group (convert to phyloXML for native color support):

```python
from Bio.Phylo.PhyloXML import BranchColor

xtree = tree.as_phyloxml()                     # phyloXML carries branch color through draw()
for clade in xtree.find_clades():
    if clade.name and clade.name.startswith('Homo'):
        clade.color = BranchColor.from_name('red')

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(xtree, axes=ax, do_show=False)
fig.savefig('colored_tree.pdf', bbox_inches='tight')
plt.close(fig)
```

Scale the panel to tip count so labels stay legible, and drop the axis frame:

```python
n_tips = len(tree.get_terminals())
height = max(8, n_tips * 0.25)                  # ~0.25 in/tip keeps ~6-8 pt labels from colliding

fig, ax = plt.subplots(figsize=(10, height))
Phylo.draw(tree, axes=ax, do_show=False)
ax.axis('off')
fig.savefig('scaled_tree.pdf', bbox_inches='tight')
plt.close(fig)
```

For circular/fan/unrooted layouts, metadata heatmaps, dual support, or BEAST HPD bars, Bio.Phylo cannot help -- route to ggtree + treeio (R), ETE4, or iTOL.

## Per-Method Failure Modes

### Drawing Meaningless Branch Lengths as a Phylogram
**Trigger:** Rendering a constraint tree, a supertree, or a tree whose lengths are non-comparable with the horizontal axis proportional to length.
**Mechanism:** The phylogram geometry asserts a quantitative claim about evolutionary distance that the lengths do not support.
**Symptom:** A topology-only or arbitrary-length tree appears to make precise distance statements.
**Fix:** Draw as a cladogram and SAY so (`branch.length='none'` in ggtree); or, if lengths are real, keep them and state the unit (subs/site vs time) plus a scale bar.

### Unlabeled or Mislabeled Support
**Trigger:** A node shows "98" with no legend, or two measures are printed without saying which is which.
**Mechanism:** The reader defaults to assuming bootstrap, but it may be a posterior (much weaker for the same number), an SH-aLRT (cutoff 80), a UFBoot (cutoff 95, not the BP-70 scale), or a TBE.
**Symptom:** A weakly resolved bush reads as a confident comb because the displayed number is over-read.
**Fix:** Always state the measure(s) and their order (e.g. "SH-aLRT/UFBoot" at each node); collapse nodes below threshold into polytomies rather than drawing fake resolution, since bootstrap, posterior, SH-aLRT, and UFBoot sit on different scales.

### Tip-Label Overplotting on Large Trees
**Trigger:** A rectangular layout past a few hundred tips.
**Mechanism:** Horizontal labels collide into an unreadable black band; authors then shrink the font to illegibility or silently drop labels.
**Symptom:** Tip labels are unreadable or missing.
**Fix:** Rotate labels, switch to circular/fan with radial labels, collapse uninformative clades, annotate by colored strips/rings (ggtreeExtra, iTOL datasets) instead of text, or move to iTOL which is built for large trees.

### Non-Monophyly Hidden by Ladderization or Rotation
**Trigger:** Rotating nodes to make a paraphyletic or polyphyletic group look contiguous (or a clade look scattered).
**Mechanism:** Node rotation is information-free with respect to the tree, but the eye reads contiguity as a clade and ordering as direction.
**Symptom:** A group that is not monophyletic appears unified, or a directional narrative is implied.
**Fix:** Color by group and let the topology speak; never narrate ordering as meaning; state "tips ladderized for legibility, ordering carries no phylogenetic meaning."

### Chronogram Without Age Uncertainty
**Trigger:** Drawing a BEAST/MrBayes time-tree with point-estimate node ages and no HPD bars.
**Mechanism:** The 95% HPD intervals on node heights ARE the result; omitting them asserts false precision.
**Symptom:** Node ages look known to the day; a reviewer asks where the credible intervals went.
**Fix:** Draw the HPD bars via treeio `read.beast()` -> ggtree `geom_range('height_0.95_HPD')` (introspect the column name; it varies by source program and treeio version), or enable node bars in FigTree; never draw an annotated Bayesian tree with Bio.Phylo, which drops the annotations silently.

### Raster Export for Publication
**Trigger:** Saving a tree as a 150-dpi PNG for a paper.
**Mechanism:** Raster pixelates thin branches and small tip labels at print size.
**Symptom:** Fuzzy labels and pixelated branches; journal rejection or blurry print.
**Fix:** Export SVG/PDF/EPS (vector) so text and lines stay sharp at any scale; only if forced to rasterize, do so at final size with >=600 dpi for line art.

## Quantitative Thresholds

These are operational defaults for a standard portrait panel with ~6-8 pt labels; adapt to font, page, and journal specs.

| Quantity | Threshold | Rationale / source |
|----------|-----------|--------------------|
| Tips, rectangular horizontal labels comfortable | <=~50 | labels do not collide at legible font |
| Tips, start rotating/shrinking labels | ~50-150 | label height x tip count approaches panel height |
| Tips, switch to circular/fan or collapse clades | ~150-500 | rectangular labels collide; radial labels recover space |
| Tips, per-tip text impractical; use strips/rings | >~500-1000 | annotate by color/groups (iTOL, ggtreeExtra); iTOL is built for large trees |
| Publication export | vector (SVG/PDF/EPS) | text and lines stay sharp at any scale; the default |
| Forced raster, line-art/tree | >=600 dpi (many journals 600-1200) | ~300 dpi is the photo floor but too coarse for thin branches and small labels |
| Scale bar on any phylogram | mandatory (subs/site or a time axis) | without it the reader cannot recover true distances under aspect-ratio distortion |
| Bootstrap strong | >=95 (>=70 moderate) | Hillis-Bull heuristic; state the measure (Felsenstein 1985) |
| UFBoot strong | >=95 (not the BP-70 scale) | recalibrated; IQ-TREE joint rule SH-aLRT>=80 AND UFBoot>=95 |
| SH-aLRT strong | >=80 | IQ-TREE recommendation |
| Posterior probability strong | >=0.95, but WEAKER than bootstrap 95 | PP systematically higher for the same data; do not equate |

Lock the branch-length scale; do not let the figure engine non-uniformly stretch a phylogram to fill a fixed panel, which distorts the lengths the figure exists to communicate.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| BEAST HPD bars absent from a Python figure | drew an annotated tree with Bio.Phylo | route through treeio `read.beast` + ggtree `geom_range` |
| Figure not saving / blank | `do_show=True` opens a window instead of writing | pass `do_show=False`, then `fig.savefig(...)` |
| Branch colors not appearing | plain Newick tree has no color slot | convert with `tree.as_phyloxml()` and set `clade.color` |
| Labels overlap into a black band | too many tips for rectangular layout | increase panel height, rotate labels, or switch to circular/iTOL |
| "Basal" claim on a radial tree | narrated an unrooted layout as if rooted | root explicitly (tree-manipulation) and show the root before any directional claim |
| Support number misread | bare integer with no measure stated | label the measure(s) and order; collapse sub-threshold nodes to polytomies |
| `Phylo.draw` has no circular option | Bio.Phylo is rectangular-only | use ggtree `layout='circular'`, ETE4, or iTOL |

## References

Talevich E, Invergo BM, Cock PJA, Chapman BA. 2012. Bio.Phylo: a unified toolkit for processing, analyzing and visualizing phylogenetic trees in Biopython. *BMC Bioinformatics* 13:209.
Yu G, Smith DK, Zhu H, Guan Y, Lam TT-Y. 2017. ggtree: an R package for visualization and annotation of phylogenetic trees with their covariates and other associated data. *Methods in Ecology and Evolution* 8(1):28-36.
Yu G. 2020. Using ggtree to visualize data on tree-like structures. *Current Protocols in Bioinformatics* 69(1):e96.
Wang L-G, Lam TT-Y, Xu S, Dai Z, Zhou L, Feng T, Guo P, Dunn CW, Jones BR, Bradley T, Zhu H, Guan Y, Jiang Y, Yu G. 2020. treeio: an R package for phylogenetic tree input and output with richly annotated and associated data. *Molecular Biology and Evolution* 37(2):599-603.
Xu S, Dai Z, Guo P, Fu X, Liu S, Zhou L, Tang W, Feng T, Chen M, Zhan L, Wu T, Hu E, Jiang Y, Bo X, Yu G. 2021. ggtreeExtra: compact visualization of richly annotated phylogenetic data. *Molecular Biology and Evolution* 38(9):4039-4042.
Huerta-Cepas J, Serra F, Bork P. 2016. ETE 3: reconstruction, analysis, and visualization of phylogenomic data. *Molecular Biology and Evolution* 33(6):1635-1638.
Letunic I, Bork P. 2024. Interactive Tree of Life (iTOL) v6: recent updates to the phylogenetic tree display and annotation tool. *Nucleic Acids Research* 52(W1):W78-W82.
Felsenstein J. 1985. Confidence limits on phylogenies: an approach using the bootstrap. *Evolution* 39(4):783-791.

## Related Skills

- tree-io - parsing and preserving BEAST/MrBayes/IQ-TREE annotations so they survive into the figure; the tightest coupling
- tree-manipulation - rooting, ladderizing, pruning, and collapsing low-support nodes before drawing
- data-visualization/ggplot2-fundamentals - the grammar, themes, and ggsave vector export underlying ggtree
- data-visualization/multipanel-figures - composing a tree plus aligned metadata panels into one figure
<!-- END FILE: phylogenetics/tree-visualization/SKILL.md -->

<!-- END CATEGORY: phylogenetics -->

