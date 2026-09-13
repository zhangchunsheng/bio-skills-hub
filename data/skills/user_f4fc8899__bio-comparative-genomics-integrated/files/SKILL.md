---
slug: bio-comparative-genomics-integrated
version: 1.0.1
displayName: "比较基因组学 / Comparative genomics"
name: bio-comparative-genomics-integrated
summary: "中文：比较基因组学综合技能，整合 13 个相关专题，覆盖比较基因组学：OrthoFinder直系同源、PAML/HyPhy正选择、MCScanX共线性、WGD定年。 English: Integrated Comparative genomics skill covering 13 related topics, including Comparative genomics: OrthoFinder orthology, PAML/HyPhy positive selection, MCScanX synteny, whole-genome duplication dating."
description: "中文：这是一个面向比较基因组学的综合生物信息学 Skill，整合当前分类下 13 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：比较基因组学：OrthoFinder直系同源、PAML/HyPhy正选择、MCScanX共线性、WGD定年。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ALE, CAFE5, Cactus。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Comparative genomics, combining 13 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Comparative genomics: OrthoFinder orthology, PAML/HyPhy positive selection, MCScanX synteny, whole-genome duplication dating. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ALE, CAFE5, Cactus. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# comparative-genomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 13 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: comparative-genomics -->

## 子目录：comparative-genomics/ancestral-reconstruction

<!-- BEGIN FILE: comparative-genomics/ancestral-reconstruction/SKILL.md -->
---
name: bio-comparative-genomics-ancestral-reconstruction
description: Reconstruct ancestral states at internal phylogenetic nodes for sequences (PAML codeml, IQ-TREE --ancestral, GRASP, FastML), discrete traits (corHMM hidden-rate Markov, ape::ace, phytools::make.simmap stochastic mapping, BayesTraits), and continuous traits (phytools::fastAnc, geiger Brownian/OU, RPANDA). Use when designing constructs for ancestral protein resurrection, tracing trait evolution along a tree, performing stochastic character mapping, testing models of trait evolution (BM vs OU vs EB), inferring ancestral genome content via Dollo or DTL reconciliation, or quantifying ancestral-state uncertainty for downstream comparative analyses.
tool_type: mixed
primary_tool: PAML
---

## Version Compatibility

Reference examples tested with: PAML 4.10.7+, IQ-TREE 2.3.6+, GRASP 2024+ (web/CLI), FastML 3.11+, RevBayes 1.2.4+, BayesTraits V4.1+, R 4.4+, ape 5.8+, phytools 2.3+, corHMM 2.9+, geiger 2.0.11+, phangorn 2.12+, RERconverge 0.3.0+, BioPython 1.84+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('corHMM')` then `?ancRECON`, `?make.simmap`, `?ace`
- CLI: `codeml` (no `--version`; check `paml -h` or examine `Phylip.tre` example), `iqtree2 --version`, `revbayes --version`
- Python: `pip show biopython`; check `Bio.Phylo.PAML.codeml` API

If code throws `AttributeError`, `ImportError`, missing slot errors on R S4 objects, or PAML `mlc` parsing failures, introspect the installed package (`?` in R, `help()` in Python) and adapt the example rather than retrying. PAML output formats are stable across 4.9 -> 4.10; IQ-TREE's `--ancestral` flag replaced `-asr` in v2.0+.

# Ancestral State Reconstruction

**"What did this gene / trait / genome look like at an internal node?"** -> Choose the reconstruction framework that matches the data class (sequence / discrete trait / continuous trait / gene content) and the inference question (point estimate vs full posterior; marginal vs joint vs scaled-conditional). The single most common mistake is reconstructing under a site-independent or trait-stationary model when the underlying biology demands a hidden-rate or epistatic model -- the resulting "ancestor" is mathematically optimal under the wrong model and is silently wrong (Beaulieu & O'Meara 2016 Syst Biol 65:583; Boyko & Beaulieu 2021 MEE 12:468).

- Sequence ASR (protein resurrection): PAML codeml `RateAncestor=1`; IQ-TREE2 `--ancestral`; GRASP (graph-based, handles indels); FastML (Bayesian)
- Discrete traits: R `ape::ace(type='discrete')`; `corHMM::corHMM()` (rate categories); `phytools::make.simmap()` stochastic mapping; BayesTraits MultiState/Discrete
- Continuous traits: `phytools::fastAnc()`; `phytools::contMap()`; `geiger::fitContinuous(model='BM'|'OU'|'EB')`; RPANDA `fit_t_env()`
- Ancestral gene content (presence/absence): `ape::ace(type='discrete', model='ARD')`; Dollo parsimony in phangorn; ALE/GeneRax for full DTL (see [[gene-tree-species-tree-reconciliation]])

## Algorithmic Taxonomy

| Framework | Data class | Inference | Strength | Fails when |
|-----------|------------|-----------|----------|------------|
| ML marginal (codeml RateAncestor=1; IQ-TREE --ancestral) | Sequence / discrete | Site-by-site MAP + posterior | Per-site uncertainty; fast (Yang 1995 Genetics 141:1641; Pupko 2000 MBE 17:890) | Strong epistasis; site-independent assumption violated |
| ML joint (Pupko 2000 MBE 17:890; IQ-TREE marginal+joint output) | Sequence / discrete | Single most-likely joint history across all nodes | Internally consistent ancestral sequence | Loses per-site uncertainty; epistasis hidden |
| Stochastic mapping (Nielsen 2002 Syst Biol 51:729; Huelsenbeck 2003 Syst Biol 52:131; phytools::make.simmap) | Discrete | Full posterior over character histories along branches | Quantifies transition timing and rates per branch; supports posterior arithmetic | Long trees (mixing slow); rare-state biases |
| Bayesian MCMC (RevBayes, BayesTraits, MrBayes) | Sequence / discrete / continuous | Full posterior; supports model averaging | Honest uncertainty; rate-variable; hierarchical | Slow; convergence diagnostics required (ESS > 200) |
| Parsimony (Fitch 1971 Syst Zool 20:406; Dollo) | Discrete | MP states at nodes | Fast; assumption-light | Felsenstein-zone LBA artifact; biased toward fast change (Felsenstein 1978 Syst Zool 27:401) |
| Hidden Markov / hidden rates (corHMM; HiSSE; HMM) | Discrete | State + rate-class jointly | Captures rate heterogeneity across the tree; non-stationarity (Beaulieu 2013 Syst Biol 62:725) | Requires enough state changes to identify hidden rates |
| Threshold model (Felsenstein 2012 Am Nat 179:145; phytools::threshBayes) | Binary on continuous liability | MCMC on latent liabilities | Models polygenic / underlying-quantitative discrete traits | Slow MCMC; complex liability covariance |
| BM / OU / EB on continuous (geiger::fitContinuous) | Continuous | Phylogenetic regression on BM, OU mean-reverting, EB time-decay | Standard for body-size / niche-shape continuous traits | Model adequacy ignored (Boettiger 2012 Evolution 66:2240; Cooper 2016 Biol J Linn Soc 118:64) |
| Multi-rate BM / OUwie (Beaulieu 2012 Evolution 66:2369) | Continuous | Rate / optimum varies by clade or discrete regime | Models regime shifts; integrates with discrete trait history | Regime mismapping cascades to spurious rate differences |
| Phylogenetic generalized least squares (PGLS) | Continuous (multivariate) | Mean expected under BM; covariance from tree | Tests for correlation while controlling shared ancestry (Felsenstein 1985 Am Nat 125:1) | Strong evolutionary rate heterogeneity; non-BM trait |
| DTL reconciliation for gene content (ALE, GeneRax) | Gene tree / orthogroup | Ancestral gene presence + duplications/transfers/losses | Joint sequence + gene-content posterior | See [[gene-tree-species-tree-reconciliation]] |
| Indel-aware ASR (GRASP, FastML) | Sequence | Treats gaps as a separate process | Handles indel evolution explicitly; supports protein engineering | Slower; limited model families |

Methodology evolves; verify the latest `corHMM` / `phytools` vignettes before locking on a single approach. For continuous-trait macroevolution, consult Cooper 2016 model-adequacy reviews.

## Decision Tree by Experimental Scenario

| Scenario | Recommended method | Why |
|----------|---------------------|-----|
| Protein resurrection (~50-500 Myr divergences) | IQ-TREE2 `--ancestral` + GRASP indel reconstruction | Per-site marginal probabilities for alt-construct design; GRASP fixes indel ambiguity that PAML treats as missing data |
| Codon-level sequence ASR with selection inference | PAML codeml `RateAncestor=1`, model M0 (single omega), `seqtype=1` | Codon model native; integrates with branch reconstruction; produces `rst` with BEB-style site probs |
| Deep eukaryote / archaeal ASR (> 1 Bya) | Bayesian (RevBayes / PhyloBayes-MPI CAT-GTR) | Site-heterogeneous CAT model corrects compositional LBA (Szánthó 2023 Syst Biol 72:767); ML site-homogeneous models fail at this depth |
| Binary discrete trait with 5-30 taxa | `ape::ace(type='discrete', model='ARD')` + bootstrap | Standard for simple binary; ER/SYM/ARD model comparison via AIC |
| Binary discrete trait with 30+ taxa, suspected rate variation | `corHMM(rate.cat=2)` HMM | Hidden rates capture rate heterogeneity; mandatory if Beaulieu 2013 sensitivity test fails |
| State-dependent diversification (correlation with speciation/extinction) | HiSSE (Beaulieu & O'Meara 2016) NOT BiSSE | BiSSE has catastrophic Type-I rate when rate heterogeneity is misattributed (Rabosky & Goldberg 2015 Syst Biol 64:340); HiSSE is the required null |
| Multi-state with phylogenetic uncertainty | `phytools::make.simmap(nsim=1000)` over a tree distribution | Marginalize over tree + state uncertainty; report posterior probabilities |
| Continuous trait, single regime | `phytools::fastAnc()` + `contMap` | Fast BM ML reconstruction; visual continuous reconstruction along branches |
| Continuous trait, suspected regime shifts | OUwie or `bayou` (Uyeda 2014 Syst Biol 63:902) | Multi-optimum OU models infer optimum shifts and their tree positions |
| Binary trait expected to be polygenic underlying | Threshold model `phytools::threshBayes` | Models latent liability properly; binary -> continuous bridge (Felsenstein 2012) |
| Ancestral gene family content | DTL reconciliation (ALE / GeneRax) | See [[gene-tree-species-tree-reconciliation]]; full posterior over D/T/L events |
| Ancestral genome architecture (gene order) | AGORA (Muffato 2023 Nat Eco Evo 7:355); DeCoSTAR | Joint reconciliation + adjacency posterior |
| Convergent rate shifts in noncoding | PhyloAcc (Hu 2019 MBE 36:1086); Thomas 2024 update | Bayesian Markov model on conserved noncoding elements |
| Convergent amino-acid substitutions | CSUBST (Fukushima & Pollock 2023 Nat Eco Evo 7:155) | Combinatorial substitution ratio omega_C; null-corrected |
| Categorical trait correlated rates | RERconverge (Kowalczyk 2019; Redlich 2024 MBE 41:msae210) | Relative evolutionary rates linked to a binary or categorical phenotype |

## Per-Tool Failure Modes

### Long-branch attraction (LBA) at deep nodes

**Trigger:** Tree with two long terminal branches separated by a short internal branch; mixed amino-acid compositions across taxa.

**Mechanism:** Site-homogeneous models (LG, WAG, JTT) assume constant amino-acid equilibrium frequencies across the tree. When real compositions differ (e.g. thermophiles vs mesophiles), models underestimate the probability of convergent substitutions at compositionally-constrained sites, producing apparent shared derived states between long branches (Szánthó 2023 Syst Biol 72:767). The reconstructed ancestor at the deep node is biased toward whichever long-branch composition the model favors.

**Symptom:** Bootstrap support at the contested node remains high under site-homogeneous models but collapses under CAT-GTR / CAT-PMSF. Posterior predictive checks for compositional homogeneity reject the model (Foster 2004 Syst Biol 53:485).

**Fix:** Move to PhyloBayes-MPI with CAT-GTR or IQ-TREE2 with CAT-PMSF (`-m LG+C60+F+R` then `-ft <tree>` for posterior mean site frequencies). For ASR specifically, use ancestral reconstruction only when the model passes compositional adequacy. Slow-fast site removal (recoded amino acids; Susko & Roger 2007 MBE 24:2139) is an alternative.

### Epistasis breaking site-independent ASR

**Trigger:** Multiple sites in the same protein evolve under coupled constraints (compensatory pairs in RNA secondary structure; buried-residue covariance; allosteric networks).

**Mechanism:** ML/Bayesian ASR assumes sites are independent given the tree; the joint ancestral sequence is the product of per-site posteriors. Real proteins evolve through compensatory substitutions where a destabilizing mutation at site i is compensated by a mutation at site j (Pollock 2012 PNAS 109:E1352; Shah 2015 PNAS 112:E3226). The ML ancestral sequence can contain a never-tested combination of states.

**Symptom:** The reconstructed protein fails to fold or is non-functional when expressed; positions flagged ambiguous (P < 0.9) are non-random and cluster in 3D space when mapped to structure.

**Fix:** Use GRASP indel-aware reconstruction; design 4-8 alternative constructs varying ambiguous positions (P < 0.9), prioritizing residues that are structurally coupled to high-confidence ML states; experimentally test each construct; report the range of functional reconstructions, not the single ML sequence. Hochberg & Thornton 2017 Annu Rev Biophys 46:247 review epistasis strategies.

### Root placement error cascading to deep ancestors

**Trigger:** Trees rooted by midpoint, outgroup with very long branch, or `--prefix` auto-root.

**Mechanism:** Marginal ASR posteriors at internal nodes depend on the root's position because the root defines the time direction of substitution. A wrong root flips state inferences for deep nodes (especially when ancestral state is asymmetric, e.g. presence -> absence is more common than reverse).

**Symptom:** Re-rooting the tree changes the inferred ancestral state at the deepest node by > 0.2 posterior probability; STRIDE rooting (Emms 2017 MBE 34:3267) disagrees with outgroup rooting.

**Fix:** Run ASR over a set of candidate roots; report robust nodes (state invariant) and root-sensitive nodes separately. For phylogenomic-scale data, use STRIDE / MAD rooting (Tria 2017 Nat Eco Evo 1:0193) or ALE-rooting (Williams 2017 PNAS 114:E4602) and document the rooting strategy.

### BiSSE false-positive in state-dependent diversification

**Trigger:** Testing whether a discrete trait influences speciation/extinction using BiSSE (Maddison 2007 Syst Biol 56:701).

**Mechanism:** BiSSE attributes ALL rate variation to the focal trait. When real diversification heterogeneity is caused by a hidden character correlated with the focal trait, BiSSE reports a spurious significant association (Rabosky-Goldberg 2015 Syst Biol 64:340 -- ~40% Type-I rate at moderate trees).

**Symptom:** BiSSE LRT highly significant but biological mechanism unclear; HiSSE rejects BiSSE in favor of a hidden-state model with the focal trait neutral.

**Fix:** Run HiSSE as the required null model (Beaulieu & O'Meara 2016 Syst Biol 65:583). Report BiSSE only if HiSSE-null is rejected. For traits with deep clade structure, use FiSSE (Rabosky & Goldberg 2017 Evolution 71:1432) which is robust to model misspecification by design.

### Parsimony vs ML on asymmetric rates (Felsenstein bias)

**Trigger:** Trait has strongly asymmetric forward vs reverse rates (e.g. gene loss > gene gain).

**Mechanism:** Parsimony minimizes total changes, implicitly assuming symmetric rates. ML/Bayesian methods estimate the rate matrix from the data and reconstruct accordingly. Under strong asymmetry, parsimony over-reconstructs the rarer state at ancestors (Cunningham 1999 Syst Biol 48:665).

**Symptom:** Parsimony and ML reconstructions disagree at > 30% of nodes; ML rates fit AIC-better with ARD (all-rates-different) than ER (equal-rates).

**Fix:** Always run ER vs SYM vs ARD model comparison via `ape::ace(model='...')` AIC; use ARD when asymmetry is supported. For gene-content evolution, Dollo parsimony (gain rare, loss common) is often the better prior than equal-rates ML.

### Continuous-trait BM-only model with non-BM evolution

**Trigger:** Fitting `phytools::fastAnc()` (which assumes BM) to a trait with strong directional or stabilizing selection.

**Mechanism:** fastAnc returns the BM-MLE ancestral state, which is a weighted mean of descendant values with weights from the BM covariance matrix. If the trait evolved under OU (stabilizing), real ancestor values were closer to the optimum than fastAnc returns; if under EB (early burst), real ancestors were more variable than fastAnc returns.

**Symptom:** BM model fits with `geiger::fitContinuous(model='BM')` give AIC > 4 above OU or EB; phylogenetic signal Pagel's lambda < 0.5; Blomberg's K significantly < 1 (Blomberg 2003 Evolution 57:717).

**Fix:** Run `fitContinuous` with multiple models (BM/OU/EB/lambda/kappa/delta); use the best AIC model's ancestral reconstruction. For OU, use `OUwie::ace()`; for regime shifts, `bayou::bayou.mcmc`. Always report Pagel's lambda alongside ancestral estimates as a phylogenetic-signal indicator. Boettiger 2012 Evolution 66:2240 and Cooper 2016 Biol J Linn Soc 118:64 detail model-adequacy testing.

### Alignment error propagating to ASR

**Trigger:** Using `MUSCLE` or default MAFFT alignment on highly diverged sequences (< 30% identity).

**Mechanism:** Misaligned columns place non-homologous residues into the same column. ML ASR treats those residues as states of the same character, producing impossible ancestral inferences (Vialle 2018 MBE 35:1783).

**Symptom:** Ambiguous regions of the alignment correspond to low-confidence ASR sites; gappy columns dominate the low-confidence set; alignment scoring (TCS, Guidance2) marks the same regions as poorly aligned.

**Fix:** Filter alignment with HmmCleaner (Di Franco 2019 BMC Evol Biol 19:21) or PREQUAL (Whelan et al 2018 Bioinformatics 34:3929) before ASR. Segment-level filtering outperforms block-level filtering (Gblocks, trimAl) for downstream evolutionary inference. For ASR specifically, mask ambiguous columns (treat as missing) rather than removing them, to preserve coordinates.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| ASR site high confidence | posterior >= 0.95 | Standard convention (Yang 1995); above this treat state as fixed |
| ASR site moderate confidence | 0.80 <= posterior < 0.95 | Worth alternative-construct testing in resurrection studies |
| ASR site ambiguous | posterior < 0.80 | Design alternative constructs; cluster against structure |
| Pagel's lambda interpretation | lambda > 0.7 strong signal; 0.3-0.7 moderate; < 0.3 weak (ad-hoc operational convention; Pagel 1999 introduced lambda but did not prescribe these cutoffs) | Pagel 1999 Nature 401:877 (method); community convention (thresholds) |
| Blomberg K interpretation | K > 1 conserved; K = 1 BM; K < 1 weak signal | Blomberg 2003 Evolution 57:717 |
| Bootstrap support for ancestral clade | >= 70% before trusting the state at that node | Standard; below this, root-sensitivity tests required |
| MCMC ESS for Bayesian ASR | ESS >= 200 per parameter; ASRV at least 200 | RevBayes / Tracer convention; Lakner 2008 Syst Biol 57:86 |
| Stochastic mapping nsim | >= 1000 simulations per tree | Operational convention (Bollback 2006 BMC Bioinf 7:88 SIMMAP method); for asymmetric rates raise to >= 5000 |
| Tree depth limit for protein ASR | dS / branch length < 1.0 at deepest node | Above this, signal saturated; Yang 2007 PAML manual |
| Codon ASR minimum sequences | >= 8 with sufficient divergence (~0.5 substitutions/site total) | Operational convention; below this, codon-model parameters poorly constrained |
| Minimum taxa for binary trait ER vs ARD AIC | >= 20 tips; below this, rates often unidentifiable | Beaulieu 2016 |
| GRASP indel posterior threshold | >= 0.8 to call indel present at node | GRASP documentation; below this, both states tested experimentally |
| OUwie regime requires | >= 10 tips per regime | Beaulieu 2012 Evolution 66:2369; below this, optima unidentifiable |
| HMM rate categories | start with rate.cat=2; AIC compare against 1 | Boyko & Beaulieu 2021 MEE 12:468 |

## PAML codeml Ancestral Reconstruction

**Goal:** Reconstruct ancestral codon or protein states at internal nodes using ML under a stationary codon/protein model.

**Approach:** Build a codon-aware alignment (PRANK or MACSE) -> infer rooted ML tree with the same model intended for ASR -> create codeml control file with `RateAncestor=1` -> run codeml -> parse `rst` for per-site posteriors and ancestral sequences.

```python
'''PAML codeml ancestral reconstruction with site-confidence parsing'''

import subprocess
import re
import os
from collections import defaultdict


def write_codeml_ctl(alignment, tree, out_dir, seqtype='codon', model='M0'):
    '''Write codeml control file for ancestral reconstruction.

    seqtype: 1=codon, 2=aa, 3=codon translated
    For protein resurrection use seqtype=2 with model=3 (empirical+gamma).
    RateAncestor=1 produces rst file with per-site posteriors.
    '''
    if seqtype == 'codon':
        ctl = f'''
      seqfile = {alignment}
     treefile = {tree}
      outfile = {out_dir}/mlc
      runmode = 0
      seqtype = 1
    CodonFreq = 2
        model = 0
      NSsites = 0
        kappa = 2
    fix_omega = 0
        omega = 0.4
 RateAncestor = 1
    cleandata = 0
   getSE = 1
'''
    else:
        ctl = f'''
      seqfile = {alignment}
     treefile = {tree}
      outfile = {out_dir}/mlc
      runmode = 0
      seqtype = 2
        model = 3
   aaRatefile = lg.dat
       alpha = 0.5
        ncatG = 4
 RateAncestor = 1
    cleandata = 0
'''
    ctl_path = os.path.join(out_dir, 'codeml.ctl')
    open(ctl_path, 'w').write(ctl)
    return ctl_path


def parse_rst_posteriors(rst_file):
    '''Parse rst file. Returns per-node, per-site (state, prob) records.
    PAML rst section headers: "Prob distribution at node X" and "List of extant and reconstructed sequences".
    '''
    text = open(rst_file).read()
    node_posteriors = defaultdict(list)

    for block in re.finditer(r'Prob distribution at node (\d+)(.*?)(?=Prob distribution at node|\Z)', text, re.DOTALL):
        node = int(block.group(1))
        for ln in block.group(2).splitlines():
            m = re.match(r'\s*(\d+)\s+\S+:\s*(\w)\((\d\.\d+)\)', ln)
            if m:
                site, state, prob = int(m.group(1)), m.group(2), float(m.group(3))
                node_posteriors[node].append({'site': site, 'state': state, 'prob': prob})
    return node_posteriors


def summarize_node_confidence(node_posteriors, ambig_cutoff=0.8):
    '''Per-node confidence summary for protein-resurrection construct design.'''
    summary = {}
    for node, sites in node_posteriors.items():
        probs = [s['prob'] for s in sites]
        n_high = sum(p >= 0.95 for p in probs)
        n_amb = sum(p < ambig_cutoff for p in probs)
        summary[node] = {
            'mean_post': sum(probs) / len(probs),
            'frac_high': n_high / len(probs),
            'n_ambiguous': n_amb,
            'ambiguous_sites': [s['site'] for s in sites if s['prob'] < ambig_cutoff]
        }
    return summary
```

## IQ-TREE2 Marginal Reconstruction

**Goal:** Faster ASR with native model selection, for protein/DNA alignments where PAML is too slow.

**Approach:** Run IQ-TREE with `-m TEST` to pick model -> `--ancestral` produces `.state` table of per-site posteriors; output rooted by `-o <outgroup>`.

```bash
iqtree2 -s alignment.fasta -m MFP --ancestral -o outgroup_taxon -B 1000 -nt AUTO --prefix asr_iqtree
# .state columns: Node | Site | State | p_A | p_C | p_G | p_T  (DNA)
# or            : Node | Site | State | p_A p_R p_N ...        (protein)
```

```python
import pandas as pd

def load_iqtree_state(state_file):
    '''Returns dict[node] -> DataFrame[site, state, max_post, all_post].'''
    df = pd.read_csv(state_file, sep='\t', comment='#')
    df.columns = [c.strip() for c in df.columns]
    state_cols = [c for c in df.columns if c.startswith('p_')]
    df['max_post'] = df[state_cols].max(axis=1)
    return df.groupby('Node')
```

## Stochastic Mapping (phytools::make.simmap)

**Goal:** Sample full character histories along branches for a discrete trait; quantify ancestral state probabilities with proper uncertainty.

**Approach:** Fit Mk rate matrix -> sample `nsim` simulated maps under the posterior -> summarize state probabilities per node and transitions per branch.

```r
library(phytools)
library(corHMM)

tree <- read.tree('species_tree.nwk')
traits <- read.csv('traits.csv', row.names = 1)
x <- setNames(traits$state, rownames(traits))

# Fit Mk model and pick ARD vs SYM vs ER by AIC
fit_er <- fitMk(tree, x, model = 'ER')
fit_sym <- fitMk(tree, x, model = 'SYM')
fit_ard <- fitMk(tree, x, model = 'ARD')
aic <- sapply(list(fit_er, fit_sym, fit_ard), AIC)
best_model <- c('ER', 'SYM', 'ARD')[which.min(aic)]

# Stochastic mapping under best model, nsim >= 1000 (raise for asymmetric rates)
smaps <- make.simmap(tree, x, model = best_model, nsim = 1000, pi = 'fitzjohn')
node_pp <- summary(smaps)$ace          # posterior probabilities per state per node

# Hidden-rate alternative for clade-rate heterogeneity
hmm_fit <- corHMM(phy = tree, data = data.frame(species = names(x), trait = x),
                   rate.cat = 2, model = 'ARD', node.states = 'marginal')
hmm_fit$states                          # marginal ancestral state matrix (rows: nodes)
```

`pi='fitzjohn'` uses the Fitzjohn 2009 Syst Biol 58:595 root prior (root-state prior weighted by the likelihood of the observed tip data given each root state), preferable to `pi='estimated'` which fixes the prior to the estimated equilibrium distribution and can over-fit, or `pi='equal'` which can bias toward the rarer state when data are asymmetric.

## Continuous-Trait ASR with Model Adequacy

**Goal:** Reconstruct ancestral values for a continuous trait while honestly reporting which model class the data support.

**Approach:** Fit BM/OU/EB/lambda models -> AIC compare -> reconstruct under best model -> report Pagel's lambda and Blomberg's K as signal quality.

```r
library(phytools); library(geiger)

trait <- setNames(traits$mass, rownames(traits))
tree_p <- multi2di(tree)               # phytools/geiger require fully bifurcating

models <- c('BM', 'OU', 'EB', 'lambda', 'kappa', 'delta')
fits <- lapply(models, function(m) fitContinuous(tree_p, trait, model = m))
aic_tbl <- data.frame(model = models, AIC = sapply(fits, function(f) f$opt$aic))
best <- aic_tbl$model[which.min(aic_tbl$AIC)]

# Phylogenetic signal
lambda_fit <- phylosig(tree_p, trait, method = 'lambda', test = TRUE)
K_fit <- phylosig(tree_p, trait, method = 'K', test = TRUE)

if (best == 'BM') {
    asr <- fastAnc(tree_p, trait, CI = TRUE)        # BM ML ancestral with 95% CI
} else if (best == 'OU') {
    # Use OUwie for proper OU ancestral with regime
    library(OUwie)
    df <- data.frame(species = names(trait), regime = rep(1, length(trait)), trait = trait)
    asr_ou <- OUwie.anc(OUwie(tree_p, df, model = 'OU1'), data = df)
} else {
    # phytools::contMap can use lambda/EB rescaled tree
    asr_contmap <- contMap(tree_p, trait, method = 'fastAnc', plot = FALSE)
}
```

Report Pagel's lambda alongside ancestral values: lambda > 0.7 indicates BM-like, signal supports tree-based reconstruction; lambda < 0.3 indicates ecology rather than phylogeny drives variance and ASR is poorly constrained.

## GRASP Indel-Aware Sequence ASR (Protein Resurrection Workflow)

**Goal:** Reconstruct ancestral protein sequence INCLUDING indel states, for experimental resurrection.

**Approach:** GRASP (Foley 2022 PLoS Comp Biol 18:e1010633) uses a partial-order alignment graph to model indels probabilistically; outputs alternative reconstructions and explicit indel uncertainty.

```bash
grasp -aln alignment.fasta -tree species.nwk -out grasp_run --inference joint --threads 8
# Produces:
#   grasp_run/asr.fasta      ancestral sequences at every internal node
#   grasp_run/asr_posterior  per-site, per-state posterior
#   grasp_run/asr_indels     indel posterior per node per gap-block
```

**Construct-design protocol:** (1) Take ML sequence as primary construct. (2) For each site with max posterior < 0.8 and a second state with posterior > 0.2, build a single-mutant alternative. (3) For each indel block with posterior < 0.8, build a present and an absent alternative. (4) Order constructs by structural compactness (avoid surface loops first). Typical batch: 4-8 constructs per ancestral node. Hochberg & Thornton 2017 Annu Rev Biophys 46:247 review the operational pipeline.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Parsimony and ML disagree at > 30% nodes | Strongly asymmetric rates | Trust ML with ARD model after AIC support; check Felsenstein 1978 LBA zone |
| BiSSE highly significant, HiSSE neutral | Hidden trait drives diversification | Report HiSSE as primary (Rabosky-Goldberg 2015) |
| Codeml marginal and joint disagree at deep node | Strong epistasis or model misspecification | Test alternative constructs; consider GRASP and BAli-Phy joint inference |
| Site-homogeneous LG agrees with PhyloBayes CAT-GTR at all nodes | No deep compositional heterogeneity | Site-homogeneous is fine; report both as confirmation |
| Site-homogeneous LG and CAT-GTR disagree at deep node | Compositional LBA | CAT-GTR is correct; report CAT-PMSF for fast follow-up |
| Marginal and stochastic-map states disagree | Asymmetric rate matrix; root prior matters | Use `pi='fitzjohn'`; trust stochastic map for asymmetric cases |
| BM ASR vs OU ASR disagree on direction of trait change at root | Trait under stabilizing selection | OU model is correct if AIC supports; reconstruct toward the optimum, not the BM weighted mean |
| Reconstruction at deepest node flips under re-rooting | Insufficient outgroup support; LBA | Run STRIDE / MAD rooting; report deep-node state with uncertainty |
| GRASP indel and PAML "missing-data" reconstructions disagree | PAML ignores indels | GRASP is correct for protein resurrection; PAML codon-only is fine for selection analysis |

**Operational rule for publication:** Reconstruct under multiple models (at minimum: ER/SYM/ARD for discrete; BM/OU/EB for continuous; site-homogeneous + CAT-PMSF or PhyloBayes for sequence ASR at deep nodes); report only nodes whose state is invariant across models OR explicitly flag model-sensitive nodes. Single-model claims should be downgraded.

## Cohort Gotchas

- **Polyploid species in continuous-trait analyses:** body size, genome size, gene count are confounded with ploidy; assign subgenomes (see [[whole-genome-duplication]]) and treat as separate tips, or use multilabel-tree methods.
- **Hybrid taxa break the bifurcating-tree assumption:** ape and phytools assume strict bifurcations; for hybrids, use phylogenetic networks (phangorn, RevBayes admixture) or remove hybrid tips before ASR.
- **Tip-dated trees from molecular clock require careful root prior:** RevBayes / BEAST2 with calibrated tip dates produce trees in absolute time; PAML/IQ-TREE work in relative substitutions. Match the time unit when integrating across tools.
- **OrthoFinder species trees from gene-tree summary (STAG):** branch lengths are coalescent-units when used for ASR; convert to substitutions via concatenated alignment if downstream tools require it.

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why marginal not joint reconstruction?" | Marginal exposes per-site uncertainty necessary for resurrection construct design; joint is internally consistent but hides ambiguity (Pupko 2000 MBE 17:890) |
| "How was epistasis handled?" | Designed and tested N alternative constructs at ambiguous (P < 0.8) sites; report functional range, not just ML sequence (Hochberg & Thornton 2017) |
| "Why these models?" | AIC compared ER/SYM/ARD for discrete; BM/OU/EB/lambda for continuous; site-homogeneous + CAT-PMSF for deep sequence ASR; reported ancestral state only at model-invariant nodes |
| "Phylogenetic signal?" | Pagel's lambda = X; Blomberg's K = Y; signal supports tree-based ASR (or: signal weak, ASR exploratory only) |
| "Effect of rooting?" | Reconstructed under multiple rootings; state at root invariant across STRIDE / MAD / outgroup, or explicit caveat for root-sensitive nodes |
| "Multiple-testing across nodes?" | Ancestral states are estimated quantities, not tested hypotheses; report posteriors per node, no multiplicity correction needed |
| "Why not BiSSE for trait-diversification correlation?" | HiSSE replaces BiSSE per Rabosky-Goldberg 2015; BiSSE Type-I rate ~40% on simulated data |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `codeml` rst file missing posteriors section | `RateAncestor` set to 0 or not set | Set `RateAncestor=1` in control file |
| IQ-TREE `--ancestral` empty `.state` file | Tree not rooted | Specify outgroup with `-o`; IQ-TREE requires rooting for ancestral output |
| `make.simmap` chains never mix | Asymmetric rate matrix with sparse data | Increase nsim to 5000+; switch root prior to `pi='fitzjohn'` |
| `ape::ace` fails with `NA/NaN/Inf in foreign function call` | Polytomies in tree | `multi2di()` to resolve to bifurcating; or use `ape::ace(method='ML')` with phytools |
| GRASP runs but produces empty asr.fasta | Alignment includes stop codons or X characters | Strip non-canonical residues; check that the alignment passes Bio.SeqIO validation |
| `fitContinuous(model='OU')` returns lambda = 0 | OU collapsed to white noise (no signal) | Trait variance unexplained by tree; reconsider whether continuous-trait ASR is meaningful |
| Stochastic mapping returns all-or-nothing at deep nodes | Insufficient signal; pi='equal' default | Use `pi='fitzjohn'`; check that taxa span both states |
| HiSSE convergence failures | `bound.par` too restrictive; hessian singular | Use `starting.vals=NULL`, restart with `output.liks=TRUE`; switch to `BiSSE-ness` (Magnuson-Ford & Otto 2012 Am Nat 180:225) as fallback |
| codeml omega = 0 or 999 at branch | Saturation or alignment artifact | Increase model complexity (M0 -> M3); check dS at branch; if dS > 3, ASR unreliable on that branch |
| Ancestral genome content reconstruction inflated | Assembly fragmentation produces false absences | Use BUSCO-completeness-corrected presence/absence; or run [[gene-tree-species-tree-reconciliation]] which handles loss-vs-missing |

## Tool Installation Notes

```bash
# CLI
conda install -c bioconda paml iqtree
# RevBayes via source build (https://revbayes.github.io/download) or homebrew on macOS
# GRASP from https://github.com/bodenlab/GRASP (Java)
# FastML web at fastml.tau.ac.il or CLI binary

# R
install.packages(c('ape', 'phytools', 'geiger', 'corHMM', 'phangorn', 'OUwie', 'bayou', 'RERconverge'))
remotes::install_github('thej022214/hisse')

# Python
pip install biopython ete4
```

For protein resurrection workflows, GRASP is the modern standard; for selection-context codon ASR, PAML remains the reference; for trait macroevolution, phytools + corHMM + OUwie are the working tier; for Bayesian rigor with model uncertainty, RevBayes is required.

## References

- Yang Z et al 1995 Genetics 141:1641 (marginal ASR likelihood framework)
- Pupko T et al 2000 MBE 17:890 (joint ASR efficient algorithm)
- Nielsen R 2002 Syst Biol 51:729 (stochastic mapping)
- Huelsenbeck JP et al 2003 Syst Biol 52:131 (Bayesian stochastic mapping)
- Felsenstein J 1985 Am Nat 125:1 (phylogenetic independent contrasts)
- Felsenstein J 2012 Am Nat 179:145 (threshold model)
- Pagel M 1999 Nature 401:877 (lambda phylogenetic signal)
- Blomberg SP et al 2003 Evolution 57:717 (K statistic)
- Beaulieu JM et al 2013 Syst Biol 62:725 (hidden Markov state-rate decoupling)
- Beaulieu JM & O'Meara BC 2016 Syst Biol 65:583 (HiSSE)
- Rabosky DL & Goldberg EE 2015 Syst Biol 64:340 (BiSSE Type-I rates)
- Boyko JD & Beaulieu JM 2021 MEE 12:468 (generalized HMM corHMM)
- Bollback JP 2006 BMC Bioinf 7:88 (SIMMAP)
- Pollock DD et al 2012 PNAS 109:E1352 (compensatory epistasis)
- Shah P et al 2015 PNAS 112:E3226 (contingency and entrenchment epistasis)
- Hochberg GKA & Thornton JW 2017 Annu Rev Biophys 46:247 (ASR for protein resurrection)
- Foley G et al 2022 PLoS Comp Biol 18:e1010633 (GRASP indel-aware ASR)
- Szánthó LL et al 2023 Syst Biol 72(4):767-780 (compositional LBA; CAT-PMSF) -- DOI 10.1093/sysbio/syad013
- Boettiger C et al 2012 Evolution 66:2240 (model adequacy for continuous-trait macroevolution)
- Cooper N et al 2016 Biol J Linn Soc 118:64 (cautionary note OU)
- Cunningham CW 1999 Syst Biol 48:665 (asymmetric rate parsimony bias)
- Felsenstein J 1978 Syst Zool 27:401 (long branch attraction)
- Maddison WP et al 2007 Syst Biol 56:701 (BiSSE)
- Beaulieu JM et al 2012 Evolution 66:2369 (OUwie)
- Uyeda JC & Harmon LJ 2014 Syst Biol 63:902 (bayou)
- FitzJohn RG 2009 Syst Biol 58:595 (root prior)
- Whelan S et al 2018 Bioinformatics 34:3929 (PREQUAL)
- Di Franco A et al 2019 BMC Evol Biol 19:21 (HmmCleaner)
- Emms DM & Kelly S 2017 MBE 34:3267 (STRIDE rooting)
- Tria FDK et al 2017 Nat Eco Evo 1:0193 (MAD rooting)
- Williams TA et al 2017 PNAS 114:E4602 (ALE-rooting of deep phylogenies)
- Hu Z et al 2019 MBE 36:1086 (PhyloAcc)
- Fukushima K & Pollock DD 2023 Nat Eco Evo 7:155 (CSUBST)
- Muffato M et al 2023 Nat Eco Evo 7:355 (AGORA)

## Related Skills

- comparative-genomics/positive-selection - Branch- and site-level selection inference on ancestral branches
- comparative-genomics/ortholog-inference - Define orthogroups whose alignments feed ASR
- comparative-genomics/gene-tree-species-tree-reconciliation - DTL-aware ancestral gene-content inference; root inference via ALE
- comparative-genomics/whole-genome-duplication - Ks-dating provides time scale for ancestral state inference
- comparative-genomics/comparative-annotation-projection - Project ancestral CDS to descendants for validation
- phylogenetics/modern-tree-inference - Generate rooted ML/Bayesian trees as ASR scaffold
- phylogenetics/bayesian-inference - RevBayes / MrBayes priors for Bayesian ASR
- phylogenetics/divergence-dating - Time-calibrated trees as input for absolute-time ASR
- alignment/multiple-alignment - PRANK / MACSE indel-aware alignment before sequence ASR
- alignment/alignment-trimming - PREQUAL / HmmCleaner filtering before ASR
<!-- END FILE: comparative-genomics/ancestral-reconstruction/SKILL.md -->

## 子目录：comparative-genomics/comparative-annotation-projection

<!-- BEGIN FILE: comparative-genomics/comparative-annotation-projection/SKILL.md -->
---
name: bio-comparative-genomics-comparative-annotation-projection
description: Project gene annotations across genomes using TOGA (Kirilenko 2023 whole-genome-alignment chain-based projection with intactness classification), CESAR 2.0 (Sharma, Schwede & Hiller 2017 codon-aware exon projection), LiftOff (Shumate & Salzberg 2021 reference-based annotation transfer), Liftover (UCSC), GeMoMa (Keilwagen 2019 evidence-based projection), and Comparative Annotation Toolkit (CAT). Use when transferring annotations from a well-annotated reference to query genome(s), classifying gene-loss vs gene-intact across many genomes at scale, building Zoonomia-style comparative annotations across hundreds of mammals or birds (Kirilenko 2023), detecting pseudogenization, projecting alternative isoforms, or selecting between WGA-anchored (TOGA) vs ortholog-based (LiftOff) annotation transfer strategies.
tool_type: cli
primary_tool: TOGA
---

## Version Compatibility

Reference examples tested with: TOGA 1.1.7+ (hillerlab/TOGA; Kirilenko 2023 Science 380:eabn3107), CESAR 2.0 (Sharma, Schwede & Hiller 2017 Bioinformatics 33:3985), LiftOff 1.6.3+ (Shumate & Salzberg 2021 Bioinformatics 37(12):1639-1643), Comparative Annotation Toolkit (CAT) 2.4+, GeMoMa 1.9+ (Keilwagen 2019 Methods Mol Biol 1962:161), UCSC liftOver 2024+, Cactus 2.9.1+ (for HAL input), HAL toolkit 2.3+, NextFlow 24+ for TOGA pipeline, BUSCO 5.7+ / Compleasm 0.2.7+ for QC, Luigi + Toil for CAT, R 4.4+. The current TOGA expects HAL from Cactus 2.5+; older HAL formats may fail.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `toga.py --help`; `cesar --help`; `liftoff --version`
- Python: `pip show liftoff`
- Java: `gemoma --help` (Java 11+)

If code throws `TOGA chain file missing`, `CESAR fragment not found`, `LiftOff annotation not parsed`, the toolchain expects specific input formats: TOGA needs HAL or chain/net files from Cactus / LASTZ; CESAR needs exon-level GFF; LiftOff needs reference GFF and aligned FASTA. Pre-process with the appropriate format conversion.

# Comparative Annotation Projection

**"Annotate this new genome using my well-annotated reference"** -> Annotation projection from a reference is the modern alternative to de novo gene prediction; it produces high-quality, comparable annotations across genomes by leveraging evolutionary conservation. The 2023-era standard is **TOGA + CESAR 2.0** (Kirilenko 2023 Science 380:eabn3107), which uses whole-genome alignment chains + ML classification + codon-aware exon projection to scale to hundreds of genomes (Zoonomia: 488 mammals; Bird10000 Genomes: 501 birds). For ortholog-based projection (no WGA needed), **LiftOff** (Shumate & Salzberg 2021 Bioinformatics 37(12):1639) is the standard. The critical decision is **WGA-anchored (TOGA) vs ortholog-anchored (LiftOff)**: TOGA explicitly classifies gene intactness vs loss using the alignment chains, LiftOff relies on reciprocal-best-hit equivalents.

- CLI: `toga.py --chain chain.bb --bed ref.bed --tDB target.2bit --qDB query.2bit --pn project_name` -- WGA-based projection
- CLI: `cesar -i exons.fa -d 4 -o output.aln` -- codon-aware exon alignment (used internally by TOGA)
- CLI: `liftoff -g ref.gff query.fa ref.fa -o query.gff` -- ortholog-based projection
- CLI: `gemoma` -- evidence-based comparative annotation (Java)
- CLI: `cat` (Comparative Annotation Toolkit) -- multi-species annotation projection

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| TOGA (Kirilenko 2023 Science 380:eabn3107) | Cactus HAL or LASTZ chains -> ML projection + intactness classifier | Per-gene I/PI/UL/L/M/PM codes; orthology classification; coding annotation via CESAR 2.0 | Modern paradigm; explicit gene-loss detection at scale; Zoonomia / Bird10000 standard | Requires Cactus WGA; not for prokaryotes |
| CESAR 2.0 (Sharma, Schwede & Hiller 2017 Bioinformatics 33:3985) | HMM-based codon-aware exon projection | Aligned exons + frame preservation | Most accurate exon projection from WGA; preserves frame across indels | Used internally by TOGA; standalone use more rare |
| LiftOff (Shumate & Salzberg 2021 Bioinformatics 37(12):1639-1643) | Read-mapping-style ortholog detection + GFF transfer | Lifted GFF | Fast; no WGA required; standard for query-vs-reference pairs | Tandem duplicates ambiguous; not for gene loss detection |
| UCSC liftOver | Coordinate-based lift using chain files | Coordinate-lifted regions | Standard for coordinate transfers; not for gene annotations | Doesn't handle gene structure changes |
| Comparative Annotation Toolkit (CAT) | Luigi + Toil workflow integrating TransMap + AUGUSTUS (TM/TMR/CGP/PB) + homGeneMapping | Per-species comparative annotation | Integrates de novo + projection | Requires Cactus HAL input; Toil/Luigi setup complex |
| GeMoMa (Keilwagen 2019 Methods Mol Biol 1962:161) | Reference protein homology + evidence integration | Comparative gene annotation | Combines multiple reference species evidence | Slower; less popular than TOGA / LiftOff |
| AUGUSTUS (Stanke 2008) | De novo prediction; not strictly projection | Per-genome annotation | Augments projection with de novo | Standalone de novo; lower comparative accuracy |
| BRAKER3 (Gabriel 2024) | Augustus + GeneMark-ETP + RNA-Seq + protein | Comparative-aware de novo | Modern de novo with evidence | Not strictly projection |
| Funannotate (palmer lab) | Multi-evidence annotation including LiftOff | Funannotate annotations | Integrates evidence | Setup complex |
| Comparative Annotation Pipeline (CAP) | Earlier WGA-based annotation | Per-species per-gene | Historical; replaced by TOGA | Use TOGA |
| TransMap | UCSC genome browser annotation lifter | Per-locus lift | Tool for UCSC tracks | Tool-specific |
| Maker (Cantarel 2008) | Evidence-based de novo + projection | Per-genome annotation | Combines evidence | Maker is for novel genomes; LiftOff for transfer |

Methodology evolves; the Kirilenko 2023 TOGA paradigm (WGA-anchored + intactness classification) is the gold standard for vertebrate-scale comparative annotation. For pairwise transfers, LiftOff is the modern standard. Verify the current TOGA documentation (hillerlab/TOGA) before locking on a single approach.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Annotate hundreds of mammal / bird genomes | TOGA with Cactus HAL | Scales to Zoonomia / Bird10000 |
| Annotate single new genome from reference | LiftOff | Fast; no WGA required |
| Detect gene loss across mammals | TOGA intactness classification | Explicit I/PI/UL/L/M/PM codes |
| Project alternative isoforms | TOGA (preserves multiple transcripts) | Standard |
| Project annotations to assembly with high N50 + chromosome-level | TOGA | Requires good assembly |
| Project to fragmented draft assembly | LiftOff (more tolerant) | LiftOff works on draft assemblies |
| Multi-species annotation pipeline | CAT (Luigi + Toil) | Integrated workflow |
| Annotate plant genome from Arabidopsis | LiftOff with plant-specific options | Standard for plant work |
| Pseudogenization detection at scale | TOGA + intactness analysis | Designed for this |
| Reference-free gene prediction | BRAKER3 or AUGUSTUS | De novo; not projection |
| Comparative annotation of multiple references | GeMoMa | Multi-reference evidence integration |
| UCSC genome browser coordinate transfer | liftOver tool | Coordinate-specific |
| Annotation transfer to closely related strain (>95% ANI) | LiftOff | High accuracy at close divergence |
| Annotation transfer to deep divergence (mammal to fish) | TOGA + manual review | Requires WGA; expect lower coverage |
| Project annotations with WGD-aware handling | AnchorWave + TOGA-like or custom workflow | WGD-aware tools |
| Annotate non-coding RNAs | Specialized tools (Rfam, ncRNA-specific) | RNA detection different problem |
| Annotate immune / repetitive genes (MHC, OR) | PGR-TK MAP graph or manual | Repetitive regions; use [[pangenome-analysis]] |
| Annotate transposable elements | RepeatMasker / RepeatModeler | TE annotation different problem |
| Validate projected annotations | RNA-Seq alignment to projected | RNA-Seq evidence is gold standard |

## Per-Tool Failure Modes

### TOGA chain file missing or incompatible

**Trigger:** Running TOGA on Cactus HAL without proper chain file extraction.

**Mechanism:** TOGA requires UCSC-style chain files derived from Cactus HAL or LASTZ chains/nets pipeline. Cactus HAL doesn't directly produce chain files; conversion via halSynteny + chainNet + axtChain is required.

**Symptom:** TOGA fails with "chain file not found" or "no syntenic blocks for query."

**Fix:** Use `halSynteny` (HAL toolkit) to extract syntenic blocks; convert to chain format via `axtChain` and `chainNet`. The TOGA Nextflow wrapper handles this automatically; for manual runs, see UCSC kentUtils chain documentation.

### CESAR exon-fragment misalignment in highly divergent species

**Trigger:** Projecting from mouse to fish (~400 Myr divergence); many exons fail CESAR projection.

**Mechanism:** CESAR's HMM model is calibrated for vertebrate divergence (< 100 Myr typical). At deep divergence, exon boundaries shift; CESAR may misalign or fail to project.

**Symptom:** Many genes in mouse have TOGA "M" (missing) or "PI" (partial-intact) classification in fish; coverage of expected genes is low.

**Fix:** TOGA documentation recommends < 300 Myr divergence for reliable projection. For deeper divergence, manual review of failed exons; consider GeMoMa with multiple reference species. Some genes won't project because they're truly absent (orphan genes); others fail due to alignment limitations.

### LiftOff tandem duplicate ambiguity

**Trigger:** LiftOff on genomes with extensive tandem duplications (e.g., NLR clusters in plants, olfactory receptors in mammals).

**Mechanism:** LiftOff uses ortholog detection similar to OrthoFinder; tandem duplicates create many similar sequences, making reciprocal-best-hit identification ambiguous.

**Symptom:** LiftOff reports many "multimapped" genes; tandem clusters have one-to-many or many-to-one orthology calls.

**Fix:** Pre-collapse tandem duplicates manually; or use LiftOff with `-mismatch 5` and `-flank 0.5` for more relaxed mapping; or use TOGA which has tandem-aware classification.

### TOGA intactness classification false negatives

**Trigger:** TOGA classifies a gene as "Lost" when it is actually intact.

**Mechanism:** TOGA uses ML classifier on chain features + frame preservation; assembly gaps, short alignment fractions, or CESAR projection failures can cause false-loss calls.

**Symptom:** TOGA "Lost" gene actually present in independent validation (RNA-Seq, manual inspection); known biology contradicts loss.

**Fix:** Manual review of TOGA "Lost" calls in the loss_summ_data.tsv; cross-validate with RNA-Seq mapping; use ID + biology to verify. TOGA's classifier is calibrated for mammals/birds; non-canonical genome architectures may produce false losses.

### Reference choice bias

**Trigger:** Projecting from one reference (e.g., mouse) produces different annotation than from another (e.g., human).

**Mechanism:** Each reference's annotation has its own biases (gene structures, splice variants, missing genes). Projection inherits these biases; different references produce somewhat different annotations.

**Symptom:** Mouse-reference TOGA annotation has gene X missing in query; human-reference TOGA has it present; or different exon structures.

**Fix:** Project from multiple references; consensus annotation. CAT integrates multi-reference projection; manual review of inconsistencies. Document reference choice impact.

### Pseudogenization vs gene loss distinction

**Trigger:** Reporting a "lost" gene that retains coding sequence (frame may be conserved but expression lost).

**Mechanism:** TOGA detects loss of coding capacity (intactness), but doesn't directly identify pseudogenization (loss of expression). A pseudogene with intact reading frame may be classified "Intact" by TOGA.

**Symptom:** TOGA "Intact" annotation but the gene is pseudogene per RNA-Seq + Ribo-Seq evidence.

**Fix:** Combine TOGA intactness with expression data (RNA-Seq from species of interest); apply PseudoPipe (Zhang 2006 Bioinformatics 22:1437) or RetroFinder (Baertsch 2008 BMC Genomics 9:466) for systematic pseudogene detection.

### Splice variant inconsistency across projections

**Trigger:** Projecting genes with extensive alternative splicing.

**Mechanism:** Reference may have alternative splice variants; projection of alternative isoforms requires per-isoform alignment which may fail for some variants.

**Symptom:** Query species has fewer projected isoforms than reference; canonical isoform present but alternatives missing.

**Fix:** TOGA projects each transcript independently; manual review of dropped isoforms. RNA-Seq from species of interest for novel splice variants.

### Annotation pipeline reference quality affecting projection

**Trigger:** Projecting from an outdated or buggy reference annotation.

**Mechanism:** Errors in reference annotation propagate to all projections. A wrong exon boundary in mouse is propagated to all mammals.

**Symptom:** Same exon boundary error appears across many projected annotations.

**Fix:** Verify reference annotation quality via BUSCO + manual gene model review; use updated Ensembl / NCBI releases (current 2024-Q4).

### Polyploid query genome handling

**Trigger:** Projecting annotations onto a polyploid query without subgenome consideration.

**Mechanism:** Projection sees multiple homeologous regions; ortholog detection ambiguous between subgenomes.

**Symptom:** Polyploid query annotation has ~2x the genes expected; many "redundant" projections from homeologs.

**Fix:** Assign subgenomes before projection (see [[whole-genome-duplication]]); project to each subgenome separately. AnchorWave proali handles ploidy; LiftOff doesn't natively.

### Chromosome-level vs scaffold-level reference

**Trigger:** Projecting from chromosome-level reference to scaffold-level query.

**Mechanism:** Scaffold-level query has gaps and ambiguous gene assignments; projection mostly succeeds but some genes split across scaffolds.

**Symptom:** Projected GFF has fragmented gene models; some genes have 2-3 entries across scaffolds.

**Fix:** Pre-scaffold query (Hi-C scaffolding if possible); or accept partial annotations; document fragmentation rate. TOGA reports "Partial Intact" for these cases.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| TOGA intactness classes (loss_summ_data.tsv) | I (intact), PI (partial intact), UL (uncertain loss), L (lost), M (missing/assembly gap), PM (partial missing) | Kirilenko 2023 + TOGA repo |
| TOGA orthology relationships (orthology_classification.tsv) | one2one, one2many, many2one, many2many, PG (paralogous projection / no orthologous chain) | Kirilenko 2023 |
| TOGA "Intact" classification confidence | ML classifier posterior > 0.9 | Kirilenko 2023 supp |
| LiftOff coverage | >=80% of reference gene length aligned | Default |
| LiftOff identity | >=70% nucleotide identity (default) | Default |
| Maximum divergence for TOGA | ~300 Myr (vertebrate); validate per clade | Kirilenko 2023 |
| Maximum divergence for LiftOff | ~80% nucleotide identity | Empirical |
| Maximum divergence for CESAR | ~150 Myr (vertebrate) | Sharma, Schwede & Hiller 2017 |
| Reference annotation BUSCO completeness | >= 95% | Standard QC |
| Assembly N50 for projection | >= 1 Mb; chromosome-level preferred | Standard |
| Annotation transfer success rate | 90-95% for closely related (< 50 Myr); 60-80% for moderately diverged | Empirical |
| Multi-reference consensus | >= 2 references agreeing | Manual standard |
| Pseudogene classification threshold | TOGA "Lost" + no RNA-Seq evidence | Operational |
| Tandem cluster window for LiftOff | 50 kb default | Default |
| GeMoMa minimum protein identity | 60% | Default |
| CAT pipeline runtime per genome | 1-5 hours on 16 cores | Empirical |
| TOGA per-genome runtime | 30 min - 5 hr on 16 cores | Empirical |
| Nextflow scaling | scales with cores | Standard |
| Reference annotation version | Ensembl / NCBI release 2024-Q4 minimum | Standard |
| Splice variant count | report; per-transcript projection | Variable |

## TOGA Standard Workflow

**Goal:** Project annotations from reference to query genome(s), classifying gene-loss / intactness.

**Approach:** Cactus WGA -> halSynteny + chainNet -> TOGA Nextflow pipeline.

```bash
# Prerequisites: Cactus HAL file from [[whole-genome-alignment]]
# OR LASTZ chain/net pipeline output

# 1. Extract syntenic blocks from HAL
halSynteny output.hal reference query --queryGenome query > query.synteny.psl

# 2. Convert PSL to UCSC chain format
axtChain -psl -linearGap=loose query.synteny.psl reference.2bit query.2bit chains/query.chain.gz
# Note: `-psl` is correct here only if the input is PSL. When the input comes from
# `lastz --format=axt`, drop the `-psl` flag (or emit PSL from LASTZ first).

# 3. Run TOGA. The canonical invocation is `python toga.py` from the TOGA checkout;
# the Nextflow-style command shown below mirrors the same arguments but may not be
# the standard entry point in your release -- verify against the hillerlab/TOGA README.
python toga.py \
    chains/query.chain.gz \
    reference_annotation.bed \
    reference.2bit \
    query.2bit \
    --pn project_name \
    --cpus 32

# Output:
#   project_name/loss_summ_data.tsv           Per-gene intactness call
#   project_name/orthology_classification.tsv One-to-one / one-to-many / many-to-many
#   project_name/query_annotation.bed         Lifted gene annotation
#   project_name/query_annotation.gff         GFF format
#   project_name/cesar_alignment/             CESAR exon alignments
```

```python
'''Parse TOGA loss summary to identify gene loss vs intact.'''
import pandas as pd


def load_toga_loss(loss_summary_path):
    '''loss_summary_data.tsv columns: TRANSCRIPT, STATUS, IS_INTACT, ...'''
    df = pd.read_csv(loss_summary_path, sep='\t')
    return df


def classify_genes(df):
    '''Standard TOGA classification: I/PI/UL/L/M/PM'''
    return df.groupby('STATUS')['TRANSCRIPT'].count()


def filter_high_confidence_intact(df):
    '''Filter to high-confidence intact (I) only. PI is partial-intact; L is Lost.'''
    return df[df['STATUS'] == 'I']
```

## LiftOff for Pairwise Annotation Transfer

**Goal:** Transfer reference annotation to query genome via ortholog mapping.

**Approach:** Minimap2-based ortholog detection -> per-gene transfer.

```bash
# Standard LiftOff (verify flags with `liftoff --help`)
liftoff -g reference.gff \
    query.fa reference.fa \
    -o query.gff \
    -u unmapped.txt \
    -copies \
    -overlap 0.5 \
    -mismatch 2 \
    -gap 5 \
    -threads 16

# Output:
#   query.gff             Lifted annotations
#   unmapped.txt          Genes failed to lift
```

For closely related species, default settings suffice. For divergent (75-90% identity), use `-mismatch 5 -gap 10`. For tandem-rich regions, `-copies` allows multiple projections.

## Comparative Annotation Toolkit (CAT)

```bash
# Setup
git clone https://github.com/ComparativeGenomicsToolkit/Comparative-Annotation-Toolkit
cd Comparative-Annotation-Toolkit && pip install .

# Edit the CAT config file with reference + query genomes; input is a Cactus HAL alignment
# CAT is orchestrated by Luigi (task graph) on top of Toil (execution); launch the RunCat module
luigi --module cat RunCat --hal=alignment.hal --ref-genome=mm10 --config=cat.config \
      --work-dir work --out-dir out --workers=10 --local-scheduler \
      --augustus --augustus-cgp --augustus-pb --assembly-hub > log.txt
```

CAT projects the reference annotation across the Cactus alignment with TransMap, then integrates AUGUSTUS (TM/TMR/CGP/PB) and homGeneMapping; output is multi-species comparative annotation.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| TOGA "Lost" vs LiftOff "Mapped" | LiftOff more permissive; doesn't check frame preservation | Trust TOGA for loss claims; LiftOff for pairwise transfer |
| TOGA "Partial Intact" vs LiftOff "Mapped" | Frame disruption | Cross-validate; consider biology |
| Mouse-reference annotation vs human-reference | Reference choice bias | Multi-reference consensus |
| TOGA "Intact" but no RNA-Seq evidence | Possible pseudogene with intact ORF | Add expression evidence; reclassify |
| CESAR fails exon | Deep divergence or assembly gap | Manual review; consider GeMoMa alternative |
| GeMoMa vs LiftOff disagree | Evidence integration vs ortholog-based | GeMoMa for evidence-rich; LiftOff for fast pairwise |
| TOGA chain doesn't cover gene | Cactus alignment quality issue | Re-run Cactus with adjusted parameters; verify assembly |
| LiftOff produces duplicate transfers | Tandem cluster | Use `-copies` or restrict; manual review |
| CAT pipeline integrates de novo + projection | Combined evidence | Trust integrated; better than single tool |
| BUSCO of projected annotation low | Missing core genes | Likely tool failure; re-run with relaxed parameters |

**Operational rule for publication:** TOGA + Cactus HAL for clade-level annotation (Zoonomia-style); LiftOff for pairwise transfer to closely related (<100 Myr); BRAKER3 / Funannotate for de novo where projection fails; manual review of TOGA "Lost" / "PI" calls.

## Cohort Gotchas

- **Plant comparative annotation:** GENESPACE handles synteny-aware ortholog detection; project via plant-specific tools
- **Bacterial annotation:** different problem; use [[pangenome-analysis]] with Bakta consistent annotation
- **Single-cell expression data:** RNA-Seq evidence for projected genes essential
- **Repetitive genes (MHC, OR):** projection unreliable; use [[pangenome-analysis]] with PGR-TK
- **Recently diverged strains:** LiftOff with strict parameters; high accuracy
- **Polyploid query:** assign subgenomes first ([[whole-genome-duplication]])
- **Distantly related to reference (>300 Myr):** projection rate drops; consider de novo with comparative evidence
- **Fragmented draft genomes:** projection works on contigs but gene splits possible
- **Reference annotation quality:** verify BUSCO before propagating to all projections
- **Non-canonical genomes (B chromosomes, supernumerary):** typically excluded from projection

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Reference annotation quality?" | BUSCO completeness reported; updated to current Ensembl / NCBI release |
| "Maximum divergence for TOGA?" | < 300 Myr for vertebrate; documented and respected |
| "Tandem duplicate handling?" | LiftOff `-copies`; or pre-collapse for TOGA |
| "Gene loss detection?" | TOGA intactness classification (I/PI/UL/L/M/PM); cross-validated with RNA-Seq |
| "Pseudogenization?" | TOGA "Intact" classification verified against RNA-Seq + Ribo-Seq |
| "Cactus WGA quality?" | Pre-filtered repeats; BUSCO on reference and query; Toil reproducibility |
| "Multi-reference?" | Consensus annotation from 2-3 reference species; documented disagreements |
| "Polyploid?" | Subgenomes assigned via [[whole-genome-duplication]]; per-subgenome projection |
| "Annotation transfer rate?" | Per-species coverage reported (e.g. 85% projection success) |
| "Splice variants?" | Per-transcript projection; missing isoforms documented |
| "BUSCO of projected annotation?" | >= 90% complete; reported |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| TOGA "chain file not found" | Cactus HAL not converted to chain | Use halSynteny + axtChain |
| TOGA stops with "no syntenic blocks" | Genome unrelated to reference | Verify Cactus alignment is non-empty |
| LiftOff produces empty GFF | Reference / query genome mismatch | Verify both are FASTA; check identifier consistency |
| GeMoMa OOM | Java heap insufficient | Increase via `-Xmx32g` |
| CESAR fragment-not-found | Exon GFF malformed | Verify GFF format; convert if needed |
| TOGA Nextflow hangs | Cluster resource issue | Restart with `-resume`; check Nextflow config |
| BUSCO of projected annotation low | Missing core genes | Likely projection failure; manual review |
| Many "PI" classifications | Assembly fragmentation | Improve assembly; or accept partial intactness |
| CAT Luigi/Toil step fails | Conda env or Toil jobstore issue | Re-create conda envs; inspect the Toil jobstore and Luigi task logs |
| LiftOff "no overlap" | Reference / query coordinate systems differ | Verify same genome version |
| TOGA intactness disagrees with biology | Edge case; manual review needed | Inspect CESAR alignment; cross-validate with RNA-Seq |

## Tool Installation Notes

```bash
# TOGA
conda env create -f https://raw.githubusercontent.com/hillerlab/TOGA/master/toga_env.yml
# Requires Nextflow and nf-core

# CESAR 2.0 (bundled with TOGA)
git clone https://github.com/hillerlab/CESAR2.0

# LiftOff
pip install liftoff

# UCSC liftOver
conda install -c bioconda ucsc-liftover

# Comparative Annotation Toolkit (CAT)
git clone https://github.com/ComparativeGenomicsToolkit/Comparative-Annotation-Toolkit
cd Comparative-Annotation-Toolkit && pip install .

# GeMoMa
wget https://gemoma.de/jcag/gemoma.zip && unzip gemoma.zip

# Comparative tools
conda install -c bioconda cactus busco compleasm

# De novo annotation (alternative)
conda install -c bioconda braker3 funannotate maker
```

For TOGA pipeline at vertebrate-scale, use Nextflow with proper HPC config (Slurm / Kubernetes); allocate >= 32 cores per genome.

## References

- Kirilenko BM et al 2023 Science 380:eabn3107 (TOGA; Zoonomia + Bird10000 standard)
- Sharma V, Schwede P & Hiller M 2017 Bioinformatics 33:3985 (CESAR 2.0)
- Shumate A & Salzberg SL 2021 Bioinformatics 37(12):1639-1643 (LiftOff)
- Hickey G et al 2013 Bioinformatics 29:1341 (HAL toolkit)
- Keilwagen J et al 2019 Methods Mol Biol 1962:161 (GeMoMa)
- Gabriel L, Brůna T et al 2024 Genome Res 34:769 (BRAKER3)
- Cantarel BL et al 2008 Genome Res 18:188 (MAKER)
- Stanke M et al 2008 Bioinformatics 24:637 (AUGUSTUS)
- Zhang Z et al 2006 Bioinformatics 22:1437 (PseudoPipe)
- Armstrong J et al 2020 Nature 587:246 (Progressive Cactus)
- Baertsch R et al 2008 BMC Genomics 9:466 (RetroFinder)
- Liao W-W et al 2023 Nature 617:312 (HPRC draft pangenome; relevant context)
- Fiddes IT et al 2018 Genome Res 28:1029 (Comparative Annotation Toolkit)
- Salzberg SL 2019 Genome Biol 20:92 (next-gen annotation pipelines)
- Comparative Genomics Toolkit (CGT) GitHub
- TimeTree (database) for divergence dates

## Related Skills

- comparative-genomics/whole-genome-alignment - Cactus WGA precedes TOGA
- comparative-genomics/synteny-analysis - Synteny detection from WGA
- comparative-genomics/ortholog-inference - TOGA orthology classification
- comparative-genomics/pangenome-analysis - PGR-TK for repetitive / clinical genes
- comparative-genomics/whole-genome-duplication - Subgenome assignment for polyploid query
- genome-annotation/eukaryotic-gene-prediction - BRAKER3 / Funannotate de novo alternative
- genome-annotation/functional-annotation - Function assignment downstream
- genome-annotation/annotation-transfer - Related skill on annotation transfer mechanisms
- genome-annotation/prokaryotic-annotation - Bakta for prokaryote annotation
- read-qc/rnaseq-qc - RNA-Seq evidence to validate projected annotations
- read-alignment/star-alignment - RNA-Seq alignment for validation
<!-- END FILE: comparative-genomics/comparative-annotation-projection/SKILL.md -->

## 子目录：comparative-genomics/gene-family-evolution

<!-- BEGIN FILE: comparative-genomics/gene-family-evolution/SKILL.md -->
---
name: bio-comparative-genomics-gene-family-evolution
description: Model gene-family birth-death dynamics across a species tree using CAFE5 (Mendes et al 2020 Bioinformatics 36:5516 gamma-distributed rate categories), CAFE5-error (annotation-error-aware), Count (Csurös 2010 ancestral state reconstruction), BadiRate (Librado 2012 likelihood + parsimony), DupliPHY-Family, and ALE/AleRax (for per-family DTL; see [[gene-tree-species-tree-reconciliation]]). Test lineage-specific gene-family expansions and contractions, distinguish biological dynamics from annotation artifacts, account for assembly fragmentation, identify functional enrichment in expanded / contracted families. Use when correlating gene-family changes with phenotype evolution, ranking lineages by adaptive gene-family-rate shifts, post-WGD dosage-balance analysis, or building Birth-death models from OrthoFinder presence/absence matrices.
tool_type: cli
primary_tool: CAFE5
---

## Version Compatibility

Reference examples tested with: CAFE5 5.1.0+ (Mendes et al 2020 Bioinformatics 36(22-23):5516-5518), Count 11.0319+ (Csurös 2010 Bioinformatics 26:1910), BadiRate 1.35+ (Librado 2012 Bioinformatics 28:279), DupliPHY-Family (Ames et al 2012), CAFExp (legacy CAFE 4.2 -- DEPRECATED; use CAFE5), OrthoFinder 3.0+ for HOG input, R 4.4+, mclust 6.1+, phytools 2.3+, ETE4 4.1.0+ for tree manipulation. ALE/GeneRax/AleRax in companion skill [[gene-tree-species-tree-reconciliation]].

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `cafe5 --help`; `Count.exe` (Java); `badirate --help`
- R: `packageVersion('phytools')`
- Python: `pip show ete4`

If code throws `CAFE5: lambda did not converge`, `Count negative branch length`, `BadiRate gamma not initialized`, the most common causes are: (1) annotation heterogeneity inflating family sizes, (2) saturated families (CAFE5 needs reasonable rate variation), (3) negative branch lengths in input tree (Count requires ultrametric). Pre-process: filter OG matrix to families present in >= 50% of species; resolve polytomies; ultrametricize tree.

# Gene Family Evolution

**"Which gene families expanded or contracted in which lineages?"** -> Birth-death models on phylogeny (Hahn 2005; Csurös 2010) treat each orthogroup's per-species count as evolving under a stochastic birth-death process; lineage-specific rate shifts are detected as departures from a global rate. **Annotation heterogeneity is the single largest confounder**: different annotation pipelines predict different numbers of genes per family, producing apparent lineage-specific expansions that are artifacts of annotation choice (Tonkin-Hill 2020 demonstrated this for bacterial pangenomes). Consistent annotation + BUSCO/Compleasm completeness filtering are mandatory before any birth-death model interpretation. CAFE5 (Mendes et al 2020 Bioinformatics 36:5516) replaces older CAFE versions with gamma-distributed rate categories for more biologically realistic modeling.

- CLI: `cafe5 -i orthogroup_counts.tsv -t species_tree.nwk -p` -- main CAFE5 workflow
- CLI: `cafe5 -e` -- error-aware mode for annotation uncertainty
- CLI: `Count` -- Java GUI / CLI for parsimony + likelihood ASR
- CLI: `badirate -t tree.nwk -d counts.tsv` -- likelihood birth-death + branch parsimony

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| CAFE5 (Mendes et al 2020 Bioinformatics 36(22-23):5516-5518) | Birth-death with gamma rate categories | Global / per-family lambda + significant rate shifts | Modern standard; handles rate heterogeneity; explicit Type-I control | Annotation heterogeneity confounds; needs > 100 families |
| CAFE5-error | Annotation-error-aware extension | Same plus error estimates | Critical for noisy annotations | Manual error-rate specification or estimation |
| Count (Csurös 2010 Bioinformatics 26:1910) | Both ML and parsimony ASR | Branch event counts (D, L) per family | Comprehensive output; GUI | Slower than CAFE5; less modern UX |
| BadiRate (Librado 2012 Bioinformatics 28:279) | Likelihood birth-death + branch parsimony | Lineage-specific rate shifts | Combines stochastic + parsimony | Less commonly used; older |
| DupliPHY-Family (Ames et al 2012) | Per-family birth-death | Ancestral counts per family | Family-level granularity | Older; less integrated with modern OrthoFinder |
| ALE / GeneRax / AleRax (Szöllősi 2013; Morel 2024) | Per-family DTL reconciliation | Per-family D/T/L event counts | Direct integration with [[gene-tree-species-tree-reconciliation]] | Slower; per-family rather than across-family |
| CAFExp / CAFE 4.2 (DEPRECATED) | Earlier CAFE | -- | Historical | Use CAFE5 |
| Whale.jl with WGD (Zwaenepoel 2019) | Bayesian DL+WGD | WGD-aware family dynamics | Native WGD integration | Julia ecosystem |
| Functional enrichment downstream | clusterProfiler / topGO on expanded/contracted | GO/KEGG enrichment | Standard | Multiple testing across families |

Methodology evolves; CAFE5 is the modern standard; verify the current CAFE5 manual (hahnlab/CAFE5) and Hahn lab papers before locking on a single approach.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Standard CAFE-style birth-death analysis | CAFE5 with gamma rate categories | Modern standard; handles rate variation |
| Annotation-pipeline-heterogeneity | CAFE5-error mode | Explicit error modeling |
| Post-WGD retention bias | CAFE5 + DupGen_finder classification + functional enrichment | Combine birth-death with WGD-specific analysis |
| Lineage-specific gene-family-rate shifts correlated with phenotype | CAFE5 with binary phenotype | Standard CAFE workflow |
| Ancestral gene-family counts at internal nodes | Count ASR | Per-node count posteriors |
| Test for "fast-evolving" family on specific lineage | CAFE5 lambda-tree (per-clade lambda) | Compares lambdas across clades |
| Functional enrichment in expanded families | clusterProfiler / topGO on expansion lists | Standard |
| HGT-affected families (prokaryotes) | ALE / GeneRax per-family DTL (see [[gene-tree-species-tree-reconciliation]]) | DTL framework explicit |
| Test if all families share single lambda | CAFE5 global lambda hypothesis | Restricted model |
| Specific family analysis (e.g. immune gene family) | ALE / AleRax per-family | Per-family detail |
| Distinguish gain from loss as primary driver | Count separate D and L counts | Standard parsimony |
| Convergent gene-family-rate shifts | RERconverge on family-count vectors | Trait-correlated rate shifts |
| Identify ancestral pan-clade family complement | CAFE5 ASR at MRCA | Pre-radiation family complement |
| Sub-clade-specific expansions in plant genomes | CAFE5 with clade-specific lambda | Compare angiosperm to gymnosperm |

## Per-Tool Failure Modes

### Annotation heterogeneity inflating expansions / contractions

**Trigger:** Running CAFE5 on counts from genomes annotated by different pipelines (Augustus, MAKER, BRAKER, NCBI).

**Mechanism:** Different annotation tools predict different numbers of genes per family; the same biological gene family may be annotated with 5 genes in BRAKER and 8 in MAKER. CAFE5 sees the difference as an "expansion" in the MAKER-annotated species (Tonkin-Hill 2020 documented this for bacterial pangenomes; same principle in eukaryotes).

**Symptom:** "Most expanded families" cluster in species annotated by a single pipeline (often more permissive tool); per-species "expansion rate" correlates with annotation pipeline rather than biology.

**Fix:** Re-annotate all genomes with a single pipeline (currently BRAKER3 or Funannotate for eukaryotes; Bakta for bacteria) before CAFE5. Alternatively use CAFE5-error mode with explicit error rates per species. Document annotation pipeline + version per species.

### Assembly fragmentation creating false contractions

**Trigger:** Including draft assemblies with low N50 in CAFE5 analysis.

**Mechanism:** Fragmented assemblies miss genes; the same family appears with fewer genes than expected. CAFE5 reports this as a contraction in the affected species.

**Symptom:** "Contracted" families in fragmented assemblies; correlation between BUSCO completeness and CAFE5 "contraction" rate; per-species missing-gene count varies 5-10x.

**Fix:** Require >= 90% BUSCO/Compleasm completeness for inclusion. Exclude species with > 5% lower BUSCO than median. Document N50 + BUSCO per assembly. For unavoidably fragmented assemblies, exclude from CAFE5 or use CAFE5-error with empirical error estimates.

### CAFE5 lambda non-convergence

**Trigger:** CAFE5 reports "lambda did not converge"; lambda jumps between values across runs.

**Mechanism:** Insufficient data (< 100 families); strong rate heterogeneity not captured; or input tree non-ultrametric.

**Symptom:** lambda estimate unstable; AIC of model selection variable.

**Fix:** Require >= 100 orthogroups (preferably > 1000) in input. Ensure tree is ultrametric (`ape::chronos()` or `treePL`); CAFE5 expects time-scaled tree. Use gamma rate categories (CAFE5 default `-k 4`) for rate heterogeneity. If still non-convergent, restrict to single-copy or small families; check tree branch lengths for negative values.

### Gamma rate-category misinterpretation

**Trigger:** Reporting "gamma rate categories" as biological gene-family clusters.

**Mechanism:** CAFE5 gamma categories are statistical buckets representing rate heterogeneity across families; they're not "fast-evolving family clusters" with biological meaning per se.

**Symptom:** Confusion in interpretation; "category-1 families are special."

**Fix:** Treat gamma categories as a statistical device. Report per-family lambda (estimated under per-family rate model) or per-clade lambda. Functional interpretation comes from family-level statistical tests, not category assignment.

### Multiple-testing across many families

**Trigger:** Reporting "significant" expansions / contractions without correction.

**Mechanism:** With ~10,000 families tested, ~500 will be significant at p=0.05 under H0. Without correction, false-discovery rate is high.

**Symptom:** Long lists of "expanded" families; functional enrichment dominated by chance hits.

**Fix:** Apply FDR (Benjamini-Hochberg) across families; or restrict to a priori hypothesized families. CAFE5 reports per-family p-values; FDR-correct downstream.

### Tree non-ultrametric / negative branches

**Trigger:** Using ML tree directly (substitutions per site) as input to CAFE5.

**Mechanism:** CAFE5 expects ultrametric (time-calibrated) tree; substitution-based branch lengths are not time-calibrated and may even have negative branches after rate variation.

**Symptom:** CAFE5 errors with "negative branch length"; or produces unreliable lambda estimates.

**Fix:** Time-calibrate the tree: use `ape::chronos()`, treePL (Smith & O'Meara 2012 Bioinformatics 28:2689), or LSD2 (To et al 2016 Syst Biol 65:82; gascuel-lab/LSD2) for fast NP-like calibration. Or use existing time-calibrated tree from TimeTree database.

### Outlier-family-driven lambda estimate

**Trigger:** Including extreme-size families (e.g., NLR resistance gene clusters in plants with 500+ members) in CAFE5.

**Mechanism:** Birth-death model's likelihood is dominated by large families; one or two outlier families can overwhelm the global lambda estimate.

**Symptom:** Excluding the top-5 largest families changes lambda by > 30%; lambda confidence intervals huge.

**Fix:** Robust analysis: report lambda with and without outliers; consider per-family lambda for largest families. Functional annotation of outliers reveals if they're biologically expected expansions (rapidly evolving gene families).

### Convergent gene-family-rate shifts not captured

**Trigger:** Phylogenomic question is whether multiple independent lineages show similar gene-family-rate shifts.

**Mechanism:** CAFE5 doesn't natively test for convergent rate shifts; per-clade lambda is the closest analog.

**Symptom:** Manual inspection of expansions across independent lineages shows pattern; CAFE5 doesn't formalize it.

**Fix:** Combine CAFE5 per-family lambdas with RERconverge (Redlich et al 2024 MBE 41:msae210) for trait-correlated rate shifts; use CSUBST (Fukushima 2023 Nat Eco Evo 7:155) for convergent substitution patterns.

### CAFE5 vs ALE for HGT-affected family

**Trigger:** Applying CAFE5 to bacterial families where transfer is common.

**Mechanism:** CAFE5 models birth-death (D, L) only; ignores transfer (T). For HGT-affected families, the dynamics include T events that CAFE5 cannot capture.

**Symptom:** CAFE5 lambda for bacterial families is implausibly high; family counts don't fit birth-death model.

**Fix:** Use ALE / GeneRax / AleRax for HGT-affected families ([[gene-tree-species-tree-reconciliation]]); CAFE5 is appropriate for vertical-inheritance-dominated families. Combine: CAFE5 for the bulk; ALE for HGT-confirmed families.

### Family classification (single-copy / multi-copy) affecting interpretation

**Trigger:** Treating single-copy orthogroups (always = 1 per species) and multi-copy uniformly.

**Mechanism:** Single-copy OGs have no count variation; including them dilutes the analysis. Multi-copy families show meaningful variation.

**Symptom:** Including single-copy OGs lowers lambda; per-family results dominated by them.

**Fix:** Restrict CAFE5 input to multi-copy orthogroups (max count >= 2 in any species). Filter via OrthoFinder HOG-classification single-copy column.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Minimum orthogroups for CAFE5 | >= 100; preferably > 1000 | Mendes et al 2020 Bioinformatics 36:5516 |
| Maximum gene-family count | depends on tree depth; typical < 1000 per family | Practical |
| BUSCO/Compleasm completeness | >= 90% for inclusion | Standard |
| FDR for expansions / contractions | q < 0.05 (Benjamini-Hochberg) | Standard |
| Significant lambda shift | LRT p < 0.05 / corrected for clade tests | CAFE5 LRT |
| Gamma categories | 4 default (`-k 4`) | CAFE5 docs |
| Tree ultrametricity | required; calibrate with ape::chronos or treePL | CAFE5 requirement |
| Per-clade lambda significance | LRT vs global lambda | CAFE5 docs |
| Annotation pipeline | one pipeline across all species; document version | Best practice |
| Functional enrichment q-value | q < 0.05 (BH-corrected) | Standard |
| Multi-copy family filter | max count across species >= 2 | Practical |
| Tree time-calibration source | TimeTree, treePL, LSD2 | Standard alternatives |
| Excluded singletons | yes, in some workflows | Standard |
| Outlier family exclusion threshold | top 5% by max count, exclude or per-family lambda | Robust |
| Convergent shift detection | RERconverge or CSUBST | Companion methods |

## CAFE5 Standard Workflow

**Goal:** Identify gene families with lineage-specific rate shifts (expansions / contractions).

**Approach:** Prepare ortholog count matrix -> ultrametricize tree -> run CAFE5 with gamma categories -> FDR-correct -> annotate.

```bash
# 1. Generate ortholog matrix from OrthoFinder v3 HOG file (inline Python; no external script needed)
python3 <<'PY'
import pandas as pd
hog = pd.read_csv('Phylogenetic_Hierarchical_Orthogroups/N0.tsv', sep='\t')
sp_cols = [c for c in hog.columns if c not in ('HOG', 'OG', 'Gene Tree Parent Clade')]
counts = pd.DataFrame({sp: hog[sp].fillna('').apply(
    lambda x: len(str(x).split(',')) if x and ',' in str(x) else (1 if str(x).strip() else 0)
) for sp in sp_cols})
counts.insert(0, 'family_id', hog['HOG'])
counts.insert(0, 'Description', '(null)')
counts.to_csv('cafe_input.tsv', sep='\t', index=False)
PY

# Output format: Description  family_id  Species1  Species2  ... (counts per species)

# 2. Ultrametricize tree
Rscript -e "
library(ape)
tree <- read.tree('SpeciesTree_rooted.txt')
tree_ultra <- chronos(tree)
write.tree(tree_ultra, 'tree_ultrametric.nwk')
"

# 3. Run CAFE5 with gamma categories
cafe5 \
    -i cafe_input.tsv \
    -t tree_ultrametric.nwk \
    -p \
    -k 4 \
    -e \
    -o cafe_output
# `-e` (no argument) lets CAFE5 estimate a global error model. To supply a pre-built
# error model file, use `-eerror.txt` (CAFE5 concatenates the flag and argument).
# Verify with `cafe5 --help`.

# Output:
#   cafe_output/Base_results.txt        Per-family results
#   cafe_output/Base_clade_results.txt   Per-clade lambda
#   cafe_output/Base_asr.tre            ASR tree
#   cafe_output/Base_clade_results.txt   LRT against null

# 4. FDR-correct across families (inline Python; see filter_significant_families() below)
```

```python
'''Filter expanded / contracted families with FDR-correction.'''
import pandas as pd
from statsmodels.stats.multitest import multipletests


def filter_significant_families(cafe_results_path, change_table_path, fdr_threshold=0.05):
    '''Identify families with significant rate shifts and their per-branch expansion/contraction direction.

    CAFE5 outputs (Base_family_results.txt or similar) include a per-family p-value (vs the null
    of a single global lambda). The per-branch expansion/contraction comes from a separate
    `Base_change.tab` file (per-family x per-branch count change). Per-family lambda is NOT
    a column in Base_family_results.txt; that's a global parameter.
    '''
    df = pd.read_csv(cafe_results_path, sep='\t')
    pcol = 'p-value' if 'p-value' in df.columns else 'pvalue'
    df['fdr'] = multipletests(df[pcol].fillna(1.0), method='fdr_bh')[1]
    significant = df[df['fdr'] < fdr_threshold]

    # Pair with per-branch change table; positive cell = expansion on that branch
    changes = pd.read_csv(change_table_path, sep='\t')
    return {'significant_families': significant, 'per_branch_changes': changes}
```

## CAFE5-error for Annotation Heterogeneity

```bash
# Prepare per-species error rates (from BUSCO completeness or empirical)
cat > error_rates.tsv << 'EOF'
species_id    error_rate
Species_A     0.05
Species_B     0.08
Species_C     0.03
EOF

# Run with error-aware mode (supply pre-built error model file).
# CAFE5 concatenates the -e flag with its argument (no space): -e<error_model_file>
cafe5 \
    -i cafe_input.tsv \
    -t tree_ultrametric.nwk \
    -p \
    -k 4 \
    -eerror_model.txt \
    -o cafe_error_output
```

## Count for Per-Branch Ancestral State

```bash
# Count requires Java
java -jar Count.jar -i count_format.tsv -t species_tree.nwk \
    -o count_output --ancestral_counts

# Per-branch D and L counts in count_output/branch_events.tsv
```

## Functional Enrichment Downstream

```r
library(clusterProfiler)
library(org.Hs.eg.db)  # or appropriate species DB

# Enrichment of expanded families
expanded_genes <- read.csv('expanded_genes.tsv', stringsAsFactors = FALSE)$gene_id

go_enrich <- enrichGO(gene = expanded_genes,
                      OrgDb = org.Hs.eg.db,
                      ont = 'BP',
                      pAdjustMethod = 'BH',
                      pvalueCutoff = 0.05)

kegg_enrich <- enrichKEGG(gene = expanded_genes,
                          organism = 'hsa',
                          pvalueCutoff = 0.05)
```

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| CAFE5 significant; ALE shows no DTL signal | CAFE5 detects count change; ALE detects events | Both can be true; CAFE5 is count-level, ALE is event-level |
| CAFE5 significant in bacterial family | Possibly HGT-driven; CAFE5 ignores T | Re-run with ALE for HGT-affected families |
| Per-clade lambda differs in CAFE5 vs uniform lambda | Real rate heterogeneity | Trust per-clade |
| Annotation heterogeneity hypothesis | Re-annotation eliminates "expansion" | Confirm annotation artifact; report as such |
| CAFE5 + RERconverge agree on expansion + trait shift | Convergent biological mechanism | Strong evidence |
| Outlier-family-driven global lambda | Top-5 families distort estimate | Report robust lambda; manually flag outliers |
| CAFE5 expansion in fragmented species | False; assembly fragmentation | Re-assess BUSCO; exclude or correct |
| Single-copy family flagged as significant | Statistical artifact; no variation | Exclude single-copy OGs; restrict to multi-copy |
| Whale.jl WGD branch shows D burst, CAFE5 shows expansion | Same event; WGD modeling preferred | Whale.jl is more biological for known WGD |
| Count parsimony vs CAFE5 likelihood disagree | Parsimony underestimates losses | Trust CAFE5 likelihood |

**Operational rule for publication:** CAFE5 with gamma rate categories + annotation pipeline normalized + BUSCO completeness > 90% + FDR-corrected significance + functional enrichment of expanded/contracted + (for bacteria) ALE complement = publication-grade gene-family evolution analysis.

## Cohort Gotchas

- **WGD lineages:** post-WGD retention bias; gene balance hypothesis (Birchler & Veitia 2007); analyze with [[whole-genome-duplication]] context
- **Plant gene families:** NLR clusters (resistance) and ribosomal proteins are inherently large; expect lineage variation
- **Mammalian gene families:** olfactory receptors are highly variable; expect lineage-specific changes
- **Bacterial gene families:** HGT-driven dynamics; use ALE/AleRax instead of CAFE5
- **Polyploid species:** subgenome assignment first; analyze each subgenome separately
- **Rapidly evolving lineages:** higher branch-specific rates; per-clade lambda model
- **Conserved species (e.g., extant cyanobacteria):** lambda may be very low; few changes to detect
- **Recent radiations:** insufficient time for divergence; CAFE5 may have low power
- **Highly fragmented MAGs:** include only high-quality MAGs

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Annotation pipeline?" | Single pipeline (BRAKER3 / Funannotate / Bakta) across all species; version pinned |
| "BUSCO completeness?" | >= 90% required; per-species reported |
| "Assembly fragmentation?" | N50 reported; species with > 5% lower BUSCO than median excluded |
| "Multiple testing?" | FDR (Benjamini-Hochberg) applied across families |
| "Lambda non-convergence?" | CAFE5 with -k 4 gamma categories; tree ultrametricized |
| "Outlier families?" | Robust analysis with and without; outliers individually annotated |
| "HGT in bacteria?" | ALE / GeneRax cross-checked for HGT-affected families |
| "Functional enrichment?" | clusterProfiler / topGO with FDR; pathway-level interpretation |
| "Tree time-calibration?" | TimeTree-based or treePL/LSD2; documented |
| "WGD effects?" | DupGen_finder + WGD-specific analysis; subgenome-aware |
| "Convergent shifts?" | RERconverge complementary analysis |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| CAFE5 "lambda did not converge" | Insufficient data or non-ultrametric tree | Ultrametricize; increase families; check tree |
| CAFE5 "negative branch length" | ML tree input | Time-calibrate with chronos / treePL / LSD2 |
| CAFE5 errors on input format | Wrong column order | Check OrthoFinder HOG format; species in column 2 onward |
| Count GUI hangs | Java memory | Increase Java heap: `java -Xmx16G -jar Count.jar` |
| BadiRate gamma errors | Initialization issue | Use default `-g 1` or specify per family |
| Per-clade lambda implausibly high | Outlier family or tree issue | Exclude top families; re-run |
| All families significant | No FDR correction | Apply BH correction |
| Annotation heterogeneity not addressed | Mixed pipelines | Re-annotate consistently |
| Family with 0 count for all species | Annotation issue | Filter rows with all zeros |
| Highly variable family count (e.g. 500-5000) | Real biological variation or annotation | Annotate manually; consider exclusion |

## Tool Installation Notes

```bash
# CAFE5
conda install -c bioconda cafe
# Or: git clone https://github.com/hahnlab/CAFE5

# Count
wget http://www.iro.umontreal.ca/~csuros/gene_content/count.tar.gz
tar xf count.tar.gz

# BadiRate
git clone https://github.com/PauloRoldan/badirate

# DupliPHY-Family
# Web only; no public CLI

# Whale.jl (Julia) -- see [[gene-tree-species-tree-reconciliation]]
julia -e 'using Pkg; Pkg.add("Whale")'

# R packages
install.packages(c('ape', 'phytools', 'clusterProfiler', 'org.Hs.eg.db'))

# Time calibration
conda install -c bioconda treepl
# Or use ape::chronos (R)

# For OrthoFinder input
conda install -c bioconda orthofinder
```

For Funannotate / BRAKER3 reannotation (essential pre-CAFE5):
```bash
conda install -c bioconda funannotate braker3
```

## References

- Hahn MW et al 2005 Genome Res 15:1153 (CAFE original framework)
- Mendes FK et al 2020 Bioinformatics 36:5516 (CAFE5)
- Csurös M 2010 Bioinformatics 26:1910 (Count)
- Librado P et al 2012 Bioinformatics 28:279 (BadiRate)
- Ames RM et al 2012 Bioinformatics 28:48 (DupliPHY-Family)
- Tonkin-Hill G et al 2020 Genome Biol 21:180 (Panaroo; annotation heterogeneity)
- Smith SA & Dunn CW 2008 Bioinformatics 24:715 (Phyutility)
- Smith SA & O'Meara BC 2012 Bioinformatics 28:2689 (treePL)
- To T-H, Jung M, Lycett S & Gascuel O 2016 Syst Biol 65:82 (LSD2)
- Birchler JA & Veitia RA 2007 Plant Cell 19:395 (gene balance)
- Redlich R et al 2024 MBE 41:msae210 (RERconverge categorical)
- Fukushima K & Pollock DD 2023 Nat Eco Evo 7:155 (CSUBST)
- Lynch M & Conery JS 2000 Science 290:1151 (gene duplication mechanism)
- Force A et al 1999 Genetics 151:1531 (subfunctionalization)
- De Bie T et al 2006 Bioinformatics 22:1269 (CAFE original software)
- Han MV et al 2013 MBE 30:1987 (CAFE 3)
- Otto SP & Whitton J 2000 Annu Rev Genet 34:401 (polyploidy mechanisms)
- TimeTree (database, http://www.timetree.org)

## Related Skills

- comparative-genomics/ortholog-inference - OrthoFinder HOG matrix is CAFE5 input
- comparative-genomics/gene-tree-species-tree-reconciliation - ALE per-family DTL, complement to CAFE5
- comparative-genomics/whole-genome-duplication - Post-WGD retention bias context
- comparative-genomics/positive-selection - Selection within expanded families
- comparative-genomics/ancestral-reconstruction - Ancestral count reconstruction
- phylogenetics/divergence-dating - Time-calibrated tree for CAFE5
- phylogenetics/modern-tree-inference - Species tree input
- pathway-analysis/go-enrichment - Functional enrichment of expanded families
- pathway-analysis/gsea - GSEA on family expansions
- single-cell/cell-annotation - Cell-type-specific gene-family expansions
<!-- END FILE: comparative-genomics/gene-family-evolution/SKILL.md -->

## 子目录：comparative-genomics/gene-tree-species-tree-reconciliation

<!-- BEGIN FILE: comparative-genomics/gene-tree-species-tree-reconciliation/SKILL.md -->
---
name: bio-comparative-genomics-gene-tree-species-tree-reconciliation
description: Reconcile gene trees against a species tree under probabilistic models of duplication, transfer, and loss (DTL) using ALE (Szöllősi 2013 amalgamated likelihood), GeneRax (Morel 2020 ML reconciliation), AleRax (Morel 2024 co-estimation), Whale.jl (Bayesian DL+WGD), RANGER-DTL 2 parsimony, NOTUNG, ecceTERA, and Treerecs. Use when inferring ancestral gene-family content, distinguishing duplication from horizontal transfer from differential loss, rooting deep species trees from gene-content signals (STRIDE / Williams 2017 ALE-rooting), counting DTL events per branch, refining noisy gene trees against a species tree, modeling WGD events jointly with DTL, or producing publication-grade gene-family histories for phylogenomic / comparative analyses.
tool_type: cli
primary_tool: ALE
---

## Version Compatibility

Reference examples tested with: ALE 1.0+ (ssolo/ALE github), GeneRax 2.1.3+ (BenoitMorel/GeneRax), AleRax 1.2.0+ (BenoitMorel/AleRax; Morel 2024 Bioinformatics 40:btae162), Whale.jl 2.0+ (arzwa/Whale.jl), RANGER-DTL 2.0+ (Bansal lab; Bansal 2018 Bioinformatics 34:3214), NOTUNG 2.9.1.5+ (Stolzer 2012; Chen 2000), ecceTERA 1.2.5+, Treerecs 1.2+, IQ-TREE 2.3.6+, MrBayes 3.2.7+, BUSCO 5.7+, ete4 4.1.0+, BioPython 1.84+. Open Tree of Life and NCBI Taxonomy reference databases at 2024-Q3 minimum for species-tree-aware inference.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `ALEml_undated --help`, `ALEml --help` (dated), `generax --help`, `alerax --help`
- Julia: `using Whale; Whale.WhaleProblem`; `]status` for package versions
- Python: `pip show ete4`; `ete4 --help`

If code throws `species tree mismatch`, `gene tree taxa not in species tree`, or `MPI process pool failure`, these reconciliation tools share strict label-consistency requirements: species labels must match exactly across the species tree and gene trees (case-sensitive, no whitespace), and gene IDs typically encode species via prefix (`species|gene_id` separator convention). Use `sed` / `awk` normalization scripts before reconciliation.

# Gene Tree Species Tree Reconciliation

**"Where did this gene family come from, and what events shaped its history?"** -> Reconcile gene trees against species trees under explicit probabilistic models of duplication (D), horizontal transfer (T), and loss (L). The reconciliation framework converts gene-tree-species-tree discordance into a quantitative history of evolutionary events. Modern probabilistic methods (ALE, GeneRax, AleRax) **distinguish gene-tree-error-driven discordance from biological discordance** by integrating over gene-tree uncertainty -- a critical advance over parsimony reconciliation (NOTUNG, RANGER) which treats input gene trees as fixed and inflates duplication/loss counts from gene-tree noise (Boussau 2013 Genome Res 23:323; Morel 2020 MBE 37:2763).

- CLI: `ALEobserve` + `ALEml_undated` -- Bayesian DTL on a sample of gene trees (amalgamated likelihood)
- CLI: `generax` -- ML reconciliation; refines gene trees jointly with reconciliation
- CLI: `alerax` -- co-estimation of gene and species trees + DTL rates (Morel 2024)
- Julia: `using Whale` -- Bayesian DL + WGD modeling
- CLI: `ranger-dtl` -- parsimony DTL with cost weights
- CLI: `notung` -- duplication-loss only (DL); user-friendly GUI; legacy

## Algorithmic Taxonomy

| Tool | Approach | Events modeled | Inference | Strength | Fails when |
|------|----------|----------------|-----------|----------|------------|
| ALE undated (Szöllősi 2013 Syst Biol 62:901) | Amalgamated likelihood over gene-tree distribution; species-tree-aware | D, T, L | Bayesian | Posterior over D/T/L events at every species-tree branch; integrates over gene-tree uncertainty | Requires gene-tree posterior sample (>= 100 bootstrap/UFBoot trees); slow for many families |
| ALE dated | Same as undated but uses time-calibrated species tree | D, T, L | Bayesian | Time-aware; better donor inference | Requires dated species tree (BEAST2 / RevBayes calibration) |
| GeneRax (Morel 2020 MBE 37:2763) | ML reconciliation + joint gene-tree refinement | D, T, L | ML | Faster than ALE; refines noisy gene trees; species-tree-aware | Less uncertainty quantification than ALE |
| AleRax (Morel 2024 Bioinformatics 40:btae162) | Co-estimation of gene tree, species tree, and DTL rates | D, T, L | Bayesian / ML hybrid | Gold standard 2024; corrects gene-tree-error feedback into species tree | Computationally heaviest; needs >= 20 species |
| Whale.jl (Zwaenepoel & Van de Peer 2019 MBE 36:1384) | Bayesian DL + WGD via amalgamated likelihood | D, L, WGD | Bayesian (Turing.jl) | Native WGD modeling; modern Bayesian framework | Julia ecosystem dependency |
| RANGER-DTL 2.0 (Bansal 2018 Bioinformatics 34:3214) | Parsimony DTL with user cost weights (D-cost, T-cost, L-cost) | D, T, L | Parsimony | Fast; deterministic; many gene families per minute | Cost weights are user choices; results sensitive to costs |
| NOTUNG (Chen 2000 JCB 7:429; Stolzer 2012 Bioinformatics 28:i409) | Parsimony DL; HGT extension | D, L (optional T) | Parsimony | User-friendly GUI; widely used | DL-only by default; HGT extension less rigorous than ALE |
| ecceTERA (Jacox 2016 Bioinformatics 32:2056) | DTL on input set of trees; sampled + unsampled ("dead") lineages | D, T, L | Parsimony / DP | Transfers from extinct/unsampled lineages; cost-sweep mode | No ILS model; less popular than ALE; smaller community |
| Treerecs (Comte 2020 Bioinformatics 36:4822) | Gene-tree correction/rooting against a fixed species tree | D, L | ML | Refines gene trees by species-tree constraint | No HGT; eukaryote-focused |
| DLCpar (Wu 2014 GR 24:475) | DLC parsimony for DL + coalescence (ILS) | D, L, C | Parsimony | Models ILS explicitly | No HGT; older |
| GraphDTL (Tofigh 2011) | Graph algorithm for DTL | D, T, L | Parsimony | Fast on small instances | Less used today |
| Phyldog (Boussau 2013 GR 23:323) | Joint species-tree-gene-tree DL with site-rate variation | D, L | ML | Joint inference; refines gene trees | Bacteria-unfriendly; eukaryote-only |

Methodology evolves; verify the AleRax / ALE documentation before locking on a single approach. The probabilistic ALE / GeneRax / AleRax tools have largely superseded parsimony reconciliation for serious phylogenomic work; parsimony is fine for screening but not for publication-grade DTL inference.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Bacterial / archaeal phylogenomics, 50-500 genomes | GeneRax (refinement) -> ALE undated (posterior) | Two-stage: GeneRax refines, ALE provides posterior |
| Eukaryote DL inference, no HGT expected | NOTUNG (legacy) or Treerecs | DL is the dominant signal; HGT rare in animals |
| Mixed prokaryote/eukaryote with HGT | ALE undated | Probabilistic D/T/L; ALE-rooting (Williams 2017) for deep questions |
| Plant comparative genomics with WGD | Whale.jl | Native WGD modeling; Bayesian |
| Need uncertainty quantification | ALE or AleRax | Posteriors on every branch; ML methods give point estimates only |
| Need fastest possible per-family analysis | RANGER-DTL parsimony | Deterministic; multi-gene parallel |
| Co-estimate species tree from many gene families | AleRax | Modern gold-standard; corrects gene-tree-error |
| Root a deep species tree from DTL signal | ALE undated rooting (Williams 2017 method) | Root inference from D/T/L event distribution |
| Detect ancient HGT in archaea / bacteria | ALE undated | Probabilistic T detection at each branch; donor inferred |
| Identify ancestral gene family content | ALE; report origination events per branch | Posterior over presence/absence at internal nodes |
| Test specific HGT hypothesis (e.g. plant -> nematode) | ALE on filtered OG set; manual gene tree inspection | Quantitative T posterior |
| Distinguish HGT from differential gene loss | ALE event posteriors (T vs L on candidate branch) | Probabilistic ratio between alternatives |
| WGD detection alongside DTL | Whale.jl explicit WGD modeling | Joint inference; replaces post hoc Ks plotting |
| Refine noisy gene trees against species tree | GeneRax `--strategy SPR` | Species-tree-aware gene-tree refinement |
| Gene family birth-death modeling | See [[gene-family-evolution]] (CAFE5) | Reconciliation is per-family; CAFE5 is across families |
| Single gene of interest, single species | Manual gene-tree placement; ALE not needed | Reconciliation framework is genome-scale |

## Per-Tool Failure Modes

### Gene-tree-error feedback inflating duplications

**Trigger:** Using GeneRax or ALE with poorly-supported gene trees (low bootstrap, short alignments).

**Mechanism:** Noisy gene trees show spurious topology that, when reconciled, produces apparent duplications-followed-by-losses or transfers. The reconciliation framework cannot distinguish gene-tree noise from real DTL events; the output is biased toward more events (Boussau 2013).

**Symptom:** D + T + L event counts exceed reasonable rates (e.g. > 5 events per gene per Myr in eukaryotes); per-branch event posteriors are diffuse; ALE convergence (in `_uTs` files) is slow.

**Fix:** Use ALE (which integrates over gene-tree posterior sample) rather than GeneRax (which uses a single ML tree). For GeneRax users, provide UFBoot trees with high (`-B 1000`) bootstraps, and refine via `--strategy SPR`. AleRax (Morel 2024) co-estimates gene trees + species tree + DTL rates, addressing this feedback directly.

### Species labels and gene IDs mismatch

**Trigger:** Different naming conventions across gene trees, species tree, and orthology files.

**Mechanism:** Reconciliation tools require species labels in the species tree to match a defined prefix or suffix in each gene ID. Inconsistencies cause silent failures or partial reconciliation.

**Symptom:** ALE fails with "taxon not in species tree"; or runs but produces zero reconciliation events; or reconciliation matrix is sparse.

**Fix:** Strict normalization before reconciliation. ALE convention: gene IDs as `species|gene_id` (pipe separator); species labels match the species tree leaf names exactly. Pre-process all gene trees with:
```bash
for tree in gene_trees/*.nwk; do
    sed -i 's/_gene_/|/g' "$tree"   # adjust separator
done
```
Verify with `nw_labels -I species_tree.nwk` vs `nw_labels -I gene_trees/OG0000001.nwk` -- both species sets must be subsets of the species tree leaves.

### Cost-weight sensitivity in parsimony reconciliation (RANGER)

**Trigger:** Running RANGER-DTL with default costs (D=2, T=3, L=1).

**Mechanism:** Parsimony reconciliation minimizes total cost; the inferred D / T / L event count depends linearly on these costs. Default costs are biased toward favoring duplication-loss explanations over transfer.

**Symptom:** RANGER reports fewer transfers than ALE/GeneRax on the same data; sensitivity-analysis varies event counts dramatically with cost changes.

**Fix:** Run RANGER with cost sensitivity sweep: D in {1, 2, 3, 4}, T in {1, 2, 3, 4, 5}, L = 1. Report consensus events appearing in all cost combinations. Or move to probabilistic ALE/GeneRax which infers rates from data, not user costs. ecceTERA also allows cost-sweep mode.

### Root sensitivity in ALE undated

**Trigger:** ALE on a species tree with poorly-supported root.

**Mechanism:** ALE undated treats the species tree root as fixed; event posteriors at deepest branches depend on the root location. Wrong root flips D vs T inference at deep nodes.

**Symptom:** Running ALE under multiple candidate rootings (STRIDE, MAD, outgroup) produces qualitatively different event histories at deep branches.

**Fix:** Run ALE under multiple rootings; report only robust events. For deep phylogenomic questions, use ALE-rooting (Williams 2017 PNAS 114:E4602): run ALE under all possible rootings, choose the root maximizing the joint likelihood. AleRax can co-estimate the root, removing this issue.

### WGD events misattributed as duplications

**Trigger:** Reconciliation on a clade with known WGD (vertebrates 2R, fish 3R, salmonids Ss4R, plant lineages).

**Mechanism:** Standard DTL models (ALE, GeneRax) treat WGD as a series of individual duplications; the posterior at the WGD branch is dominated by D events but the joint event is whole-genome.

**Symptom:** D events at the WGD branch are 10-100x higher than other branches; many "duplications" cluster temporally.

**Fix:** Use Whale.jl which natively models WGD as a single event with a flexible retention parameter (Zwaenepoel 2019 MBE 36:1384). Otherwise, post hoc identify clusters of synchronized duplications and label as WGD.

### Saturation at deep timescales

**Trigger:** Reconciliation on extremely deep clades (>1 Gyr divergence in bacteria; >500 Myr in eukaryotes).

**Mechanism:** Gene families have undergone many cycles of D, T, L; the observed pattern is consistent with many DTL histories. Parameter identifiability is lost.

**Symptom:** ALE convergence requires hundreds of cycles; posterior on D/T/L rates is uninformative; branch event posteriors are diffuse.

**Fix:** Restrict to subclades with more recent divergence for quantitative DTL claims; for deep questions, qualitative event-class identification only (e.g. "transfers occurred along this branch" without precise count). Williams 2017 PNAS 114:E4602 demonstrates how ALE on deep archaeal phylogeny still resolves event class.

### MPI parallelization failures in GeneRax

**Trigger:** Running GeneRax on cluster with many gene families.

**Mechanism:** GeneRax uses MPI to parallelize per-family analysis; misconfigured MPI environment (wrong `srun`/`mpirun`/`mpiexec`, wrong allocator) silently runs serial or hangs.

**Symptom:** GeneRax progresses through few families per hour; cluster CPU usage shows only 1 core per node.

**Fix:** Verify MPI: `mpirun -n 8 hostname` should show 8 different hostnames or threads. Use `--per-family-rates` and proper MPI launch: `mpirun -n $SLURM_NTASKS generax ...`. Reduce `--threads` to 1 per family (let MPI handle parallelism). AleRax uses the same convention.

### ILS misattributed as transfers

**Trigger:** Reconciliation on rapidly radiated clade (incomplete lineage sorting expected).

**Mechanism:** ILS produces gene-tree-species-tree discordance indistinguishable from HGT at short internodes. ALE / GeneRax cannot separate them.

**Symptom:** Many "transfers" at short internal branches; transfer rate per branch correlates with branch length (more transfers at short branches).

**Fix:** Use DLCpar, which models deep coalescence (ILS) jointly with duplication and loss; or pre-screen for ILS-likely loci via Dsuite ABBA-BABA (see [[introgression-detection]]); restrict ALE to gene families where ILS unlikely (long internodes). For phylogenomic-scale ILS, use an ASTRAL-Pro2 coalescent species tree as the fixed input to reconciliation.

### Multifurcations in the species tree

**Trigger:** Using a species tree with polytomies (unresolved nodes).

**Mechanism:** ALE / GeneRax / AleRax assume strictly bifurcating species trees; multifurcations break the inference.

**Symptom:** Tool fails with "polytomy detected" or runs but produces nonsensical results at multifurcating nodes.

**Fix:** Resolve polytomies before reconciliation via `ape::multi2di()` (random resolution) or with an outgroup-informed resolution (RAxML / ASTRAL-Pro2 on more data). Document the resolution.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| ALE gene-tree sample size | >= 100 bootstrap or UFBoot trees per family | ALE documentation; below this, posterior poorly resolved |
| Bacterial transfer rate (per gene per branch) | typically 0.001-0.05 in ALE inferences | Szöllősi 2013; varies clade |
| Eukaryote duplication rate | typically 0.0001-0.005 | eukaryote-specific convention; calibrate per clade |
| Branch-wise DTL event posterior | > 0.5 for "called" event | ssolo/ALE convention |
| Minimum gene families for AleRax | >= 100 families; >= 20 species | Morel 2024 |
| Minimum species for species-tree rooting via ALE | >= 30 species across the clade | Williams 2017 |
| GeneRax `--strategy` choices | EVAL only (no refinement), SPR (refinement), HYBRID (random + SPR) | GeneRax docs |
| RANGER cost weights default | D=2, T=3, L=1 (Bansal 2018) | Sensitivity sweep recommended |
| Whale.jl MCMC burn-in | >= 1000 samples; convergence by ESS >= 200 | Whale.jl docs |
| Reasonable runtime per family (ALE) | 1-30 minutes | Modern CPU; varies with gene-tree count |
| Reasonable runtime per family (GeneRax) | 0.1-5 minutes | Modern CPU; SPR is slower than EVAL |
| Maximum families per AleRax run | < 5000 (computational) | Above this, partition |
| Species labels case-sensitivity | strict; case mismatch = silent failure | Universal convention |
| Gene-ID separator | ALE / GeneRax accept a single-character separator via `separators="X"` (commonly `|` or `_`); Whale.jl uses a mapping file. Verify per-tool. | Tool-specific |
| Transfer branch detection minimum support | branch posterior > 0.5 + AU test on alternative placement | Conservative publication-grade |
| Distinguish T from L | T posterior - L posterior on candidate branch | Subtraction approach; ALE outputs both |

## ALE Standard Workflow

**Goal:** Quantify D/T/L events per branch of a species tree, integrating gene-tree uncertainty.

**Approach:** Build UFBoot gene trees per orthogroup -> `ALEobserve` to encode tree samples -> `ALEml_undated` for reconciliation -> aggregate per-branch event posteriors.

```bash
# 1. Build UFBoot gene trees per orthogroup
mkdir -p gene_trees
for og in orthogroups/*.fa; do
    base=$(basename $og .fa)
    iqtree2 -s $og -m TEST -B 1000 -nt 2 --prefix gene_trees/$base
done

# 2. Encode for ALE
for ufb in gene_trees/*.ufboot; do
    ALEobserve $ufb
done
# Produces gene_trees/*.ale files

# 3. Reconcile against species tree
mkdir -p reconciled
for ale in gene_trees/*.ale; do
    ALEml_undated species_tree.nwk $ale \
        separators="|" \
        sample=100 \
        output_format=newick
    mv ${ale%.*}_*.uml ${ale%.*}.uml
    mv ${ale%.*}_*.uTs ${ale%.*}.uTs
done

# 4. Aggregate branch-wise events
python aggregate_ale_events.py reconciled/ > branch_events.tsv
```

```python
'''Aggregate ALE outputs per species-tree branch.'''
import glob
from collections import defaultdict
import pandas as pd


def parse_uts(path):
    '''ALE _uTs format: branch  duplications  transfers  losses  originations  speciations.'''
    rows = []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith('#') or not ln.strip():
                continue
            parts = ln.split()
            if len(parts) >= 5:
                rows.append({
                    'branch_id': parts[0],
                    'duplications': float(parts[1]),
                    'transfers': float(parts[2]),
                    'losses': float(parts[3]),
                    'originations': float(parts[4]),
                })
    return pd.DataFrame(rows)


def aggregate(reconciled_dir):
    agg = defaultdict(lambda: defaultdict(float))
    for uts in glob.glob(f'{reconciled_dir}/*.uTs'):
        df = parse_uts(uts)
        family = uts.split('/')[-1].split('.')[0]
        for _, row in df.iterrows():
            for event in ('duplications', 'transfers', 'losses', 'originations'):
                agg[row['branch_id']][event] += row[event]
    return pd.DataFrame(agg).T.fillna(0)


branch_events = aggregate('reconciled')
print(branch_events.sort_values('transfers', ascending=False).head(20))
```

## GeneRax for ML Reconciliation with Refinement

**Goal:** Reconcile gene trees against a species tree while jointly refining noisy gene trees.

**Approach:** Provide gene trees + alignments + species tree -> GeneRax SPR strategy refines each gene tree -> reconciliation produces D/T/L history.

```bash
# Prepare families file (one line per family with paths)
cat > families.txt << 'EOF'
[FAMILIES]
- OG0000001
starting_gene_tree = gene_trees/OG0000001.nwk
alignment = alignments/OG0000001.fa
mapping = mapping.txt
subst_model = GTR+G
- OG0000002
starting_gene_tree = gene_trees/OG0000002.nwk
alignment = alignments/OG0000002.fa
mapping = mapping.txt
subst_model = GTR+G
EOF

# Mapping file: gene_id  species_label
# One line per gene
generate_mapping.py orthogroups.tsv > mapping.txt

# Run GeneRax with SPR refinement
mpirun -n 16 generax \
    --families families.txt \
    --species-tree species_tree.nwk \
    --rec-model UndatedDTL \
    --strategy SPR \
    --prefix generax_run \
    --per-family-rates \
    --max-spr-radius 5

# Output:
#   generax_run/results/<family>/inferredGeneTree.newick  refined gene tree
#   generax_run/results/<family>/reconciliation.nhx       reconciliation in NHX format
#   generax_run/species_trees/species_tree.newick         species tree (with optional re-rooting)
#   generax_run/families.txt                              refined families
```

## AleRax Co-Estimation

**Goal:** Co-estimate gene trees, species tree, and DTL rates from gene-family alignments.

**Approach:** Provide alignments + initial species tree -> AleRax runs joint Bayesian / ML co-estimation.

```bash
# Prepare AleRax families file (similar to GeneRax but with bootstrap trees)
cat > families.txt << 'EOF'
[FAMILIES]
- OG0000001
starting_gene_tree = gene_trees/OG0000001.ufboot
alignment = alignments/OG0000001.fa
mapping = mapping.txt
subst_model = GTR+G
EOF

mpirun -n 32 alerax \
    --families families.txt \
    --species-tree initial_species_tree.nwk \
    --rec-model UndatedDTL \
    --output alerax_run \
    --gene-tree-samples 100 \
    --species-tree-samples 1
```

AleRax outputs include `alerax_run/inferred_species_tree.nwk` (possibly re-rooted; D/T/L-aware) and per-family reconciled gene trees.

## Whale.jl Bayesian DL + WGD

**Goal:** Bayesian DTL inference with explicit WGD modeling.

**Approach:** Define species tree with WGD nodes -> Whale.jl posterior over D/L + WGD retention.

```julia
# IMPORTANT: Whale.jl public API evolves; verify against current docs at
# https://github.com/arzwa/Whale.jl before scripting. The sketch below is
# illustrative; introspect via `?WhaleModel`, `?WhaleProblem`, `?read_ale`.
using Whale, NewickTree, Distributions, DynamicHMC

# Read species tree (Whale uses readnw or SlicedTree)
species_tree = readnw(read("species_with_wgd.nwk", String))

# Define rates model and WGD retention parameters
# Whale parameterization: λ (duplication), μ (loss), q (WGD retention per WGD node), ρ (sampling)
# The exact constructor signature is package-version-dependent; see ?WhaleModel
rates = ConstantDLWGD(λ=0.1, μ=0.1, q=Dict(1=>0.3), η=0.66)

# Read amalgamated gene-tree distributions (a directory of .ale files)
ale_dir = "families/"
ale_data = read_ale(ale_dir, species_tree)

# Build problem and sample with DynamicHMC (verify with current Whale.jl examples)
problem = WhaleProblem(ale_data, species_tree, rates)
results = mcmc(problem, n=1000)
```

**Operational note:** the Whale.jl 2.x DSL has moved between releases; do NOT copy-paste this without verifying with `?` on the actual installed version. Reference examples live in the upstream `examples/` directory.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ALE high transfer posterior, RANGER low | Cost weights in RANGER bias against T | Trust ALE; sensitivity-sweep RANGER costs |
| GeneRax fewer events than ALE | GeneRax uses ML on single tree; ALE integrates over tree distribution | Trust ALE; GeneRax may have underestimated due to gene-tree uncertainty |
| AleRax revises species tree from initial guess | Gene-tree-error feedback was biasing initial estimate | Trust AleRax (co-estimation corrects feedback) |
| Whale.jl WGD posterior high; ALE shows duplication burst | Same event; Whale models as WGD with retention parameter | Whale.jl interpretation is more biological for clades with known WGD |
| NOTUNG DL reconciliation contradicts ALE | NOTUNG ignores T; ALE includes T | Trust ALE for HGT-affected clades |
| Same family: D in one tool, T in another | Boundary case; both events possible | Report both with explicit caveats; or use AleRax for joint co-estimation |
| Many "transfers" at short internal branches | ILS confounded with T | Switch to DLCpar (or an ASTRAL-Pro2 coalescent species tree) for ILS-aware inference |
| ALE posterior diffuse across branches | Saturated; very ancient family or short tree | Restrict to subclade; or report event class only |
| GeneRax fails on 1% of families | Specific orthology / alignment issue | Inspect failed families manually; often related to species-label mismatch |

**Operational rule for publication:** ALE with 100+ bootstrap gene trees + Bayesian event posteriors > 0.5 + multiple-rooting robustness + biological corroboration (e.g. HGT predictions cross-checked with composition / [[hgt-detection]]) = publication-grade DTL inference. Single parsimony reconciliation (RANGER, NOTUNG) is appropriate for screening but should be backed by ALE for published claims.

## Cohort Gotchas

- **Bacterial clades with rampant HGT (e.g. Enterobacteriaceae, Streptomyces):** ALE transfer posteriors will dominate; calibrate expected per-branch transfer rate against published values (Szöllősi 2013; Williams 2017)
- **Endosymbionts with genome reduction (Buchnera, Wolbachia):** rampant gene loss; loss rates may exceed all other events; calibrate against known biology
- **Salmonid 4R Ss4R WGD:** add WGD node to species tree before reconciliation; use Whale.jl with native WGD parameter; treating Ss4R as duplication burst inflates DL counts
- **Plant tetraploids:** subgenome assignment first ([[whole-genome-duplication]]); reconcile each subgenome lineage separately
- **Rapid radiations (cichlids, Drosophila species groups, hominoids):** ILS confounded with transfers; use ASTRAL-Pro2 coalescent species tree as input; or apply DLCpar for explicit duplication-loss-coalescence reconciliation
- **Polyploid lineages with WGD-derived "extra" genes:** appear as duplications in DTL methods; AleRax with WGD node specification handles this; Whale.jl native

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Gene-tree uncertainty?" | ALE integrates over 100+ UFBoot trees per family; AleRax co-estimates |
| "Species tree rooting?" | ALE-rooting (Williams 2017) under multiple candidate rooting hypotheses; events robust across rootings reported |
| "ILS vs HGT?" | Tested via ABBA-BABA / Dsuite; or used DLCpar for joint duplication-loss-coalescence inference |
| "WGD vs DL?" | Whale.jl native WGD modeling for known-WGD lineages; otherwise WGD node added explicitly |
| "Why ALE over RANGER?" | RANGER is cost-sensitive parsimony; ALE provides posterior probabilities |
| "Why AleRax over ALE?" | AleRax co-estimates gene tree + species tree + DTL rates, correcting gene-tree-error feedback; preferred for publication-grade work since 2024 |
| "ILS at rapid radiation?" | ILS-aware reconciliation (DLCpar); or restrict to gene families with long internodes |
| "Cost weight sensitivity (RANGER)?" | If RANGER used, sensitivity sweep across cost weights performed; consensus events reported |
| "Contamination?" | Pre-filtered with FCS-GX / BlobTools (cross-ref [[hgt-detection]]) |
| "Gene-tree quality?" | UFBoot bootstrap >= 95 average; PREQUAL / HmmCleaner alignment filter applied |
| "Species sampling?" | At least 30 species for ALE-rooting; clade-balanced sampling reported |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| ALEml "taxon not found" | Species label mismatch | Normalize labels exactly; verify with `nw_labels` |
| GeneRax MPI hangs | Wrong MPI launcher; per-thread vs per-process confusion | Use `mpirun -n $NTASKS generax --threads 1`; check `mpirun -n 4 hostname` |
| ALE convergence slow / never | Insufficient gene-tree samples | Increase UFBoot samples to 1000; verify each `.ale` file has >= 100 trees |
| Whale.jl Turing sampling fails | NUTS step-size; tree dimension high | Try `HMC()` with manual tuning; or scale down number of WGD nodes |
| RANGER outputs single most-parsimonious history | One MPR returned by default | Run with `--explore-mpr` for multiple equally parsimonious histories |
| AleRax species tree differs from initial | Co-estimation revised it (intended) | Use AleRax's tree; report initial vs refined |
| Reconciliation gives 1000 events on a 5-gene family | Numerical instability or bad input | Inspect family for paralog confusion or sequence error |
| Per-branch event posterior > 1.0 | Multiple events on same branch | Expected for high-DTL-rate branches; sum over event classes |
| NOTUNG DL counts vastly exceed ALE D + L counts | NOTUNG attributes T events to L (no T model) | Use ALE for HGT-affected clades |
| DLCpar over-calls deep coalescence (ILS) across many nodes | ILS/coalescence cost too permissive | Restrict ILS-aware analysis to known short-internode regions; re-check cost settings |

## Tool Installation Notes

```bash
# ALE (C++)
git clone https://github.com/ssolo/ALE && cd ALE && mkdir build && cd build && cmake .. && make
# Or via bioconda
conda install -c bioconda ale

# GeneRax (with MPI)
git clone --recursive https://github.com/BenoitMorel/GeneRax && cd GeneRax && ./install.sh

# AleRax
git clone --recursive https://github.com/BenoitMorel/AleRax && cd AleRax && ./install.sh

# Whale.jl (Julia)
julia -e 'using Pkg; Pkg.add("Whale")'

# RANGER-DTL
wget https://compbio.engr.uconn.edu/software/RANGER-DTL/RANGER-DTL-Linux.tar.gz
tar xf RANGER-DTL-Linux.tar.gz

# NOTUNG
wget https://www.cs.cmu.edu/~durand/Notung/download/Notung-2.9.1.5.tar.gz

# ecceTERA
git clone https://github.com/cchauve/ecceTERA && cd ecceTERA && make

# Treerecs
conda install -c bioconda treerecs

# Newick utilities (label inspection)
conda install -c bioconda newick_utils
```

For cluster deployment, AleRax / GeneRax require MPI; verify `mpicc --version` and run a small `hostname` test before deploying to genome-scale data.

## References

- Szöllősi GJ et al 2013 Syst Biol 62:901 (ALE undated)
- Szöllősi GJ et al 2015 Syst Biol 64:e42 (ALE rooting concept)
- Morel B et al 2020 MBE 37:2763 (GeneRax)
- Morel B et al 2024 Bioinformatics 40:btae162 (AleRax co-estimation)
- Williams TA et al 2017 PNAS 114:E4602 (ALE-rooting of the archaeal tree of life)
- Zwaenepoel A & Van de Peer Y 2019 MBE 36:1384 (Whale.jl Bayesian DL+WGD)
- Bansal MS et al 2018 Bioinformatics 34:3214 (RANGER-DTL 2.0)
- Chen K et al 2000 J Comp Biol 7:429 (NOTUNG)
- Stolzer M et al 2012 Bioinformatics 28:i409 (NOTUNG-HGT extension)
- Jacox E et al 2016 Bioinformatics 32:2056 (ecceTERA)
- Comte N et al 2020 Bioinformatics 36:4822 (Treerecs)
- Wu Y-C et al 2014 GR 24:475 (DLCpar)
- Boussau B et al 2013 Genome Res 23:323 (Phyldog joint inference)
- Sjöstrand J et al 2012 Bioinformatics 28:2994 (PrIME-DLRS Bayesian)
- Tofigh A, Hallett M & Lagergren J 2011 IEEE/ACM TCBB 8:517 (DTL graph algorithm)
- Maddison WP 1997 Syst Biol 46:523 (gene tree discordance causes)
- Rabier C-E et al 2014 MBE 31:750 (rate inference under WGD)
- Tria FDK et al 2017 Nat Eco Evo 1:0193 (MAD rooting alternative)
- Emms DM & Kelly S 2017 MBE 34:3267 (STRIDE rooting)

## Related Skills

- comparative-genomics/hgt-detection - DTL reconciliation underlies probabilistic HGT inference
- comparative-genomics/ortholog-inference - Orthogroups feed reconciliation pipeline
- comparative-genomics/gene-family-evolution - CAFE5 birth-death across families (complementary to per-family reconciliation)
- comparative-genomics/whole-genome-duplication - WGD modeling in Whale.jl
- comparative-genomics/ancestral-reconstruction - DTL informs ancestral gene-content inference
- phylogenetics/modern-tree-inference - UFBoot bootstrap gene trees for ALE input
- phylogenetics/bayesian-inference - MrBayes / RevBayes alternative gene-tree posteriors
- phylogenetics/species-trees - ASTRAL-Pro2 coalescent species tree as ALE/AleRax input
- alignment/multiple-alignment - High-quality MSA precedes gene-tree inference
- alignment/alignment-trimming - PREQUAL / HmmCleaner for clean gene trees
<!-- END FILE: comparative-genomics/gene-tree-species-tree-reconciliation/SKILL.md -->

## 子目录：comparative-genomics/genome-distance-and-species-delineation

<!-- BEGIN FILE: comparative-genomics/genome-distance-and-species-delineation/SKILL.md -->
---
name: bio-comparative-genomics-genome-distance-and-species-delineation
description: Compute genome-to-genome distances (ANI, AAI, dDDH, k-mer Mash) and assign taxonomic classifications using skani (Shaw 2023), FastANI (Jain 2018), pyani / pyANI ANIb / ANIm, OrthoANI (Lee 2016), AAI (amino-acid identity), dDDH via TYGS / GGDC, GTDB-Tk (Chaumeil 2020 standard prokaryote taxonomy), and Mash MinHash (Ondov 2016). Use when delineating prokaryote species (95% ANI threshold; Jain 2018 Nat Commun 9:5114), assigning genomes to GTDB taxonomy with ANI radius, computing genome similarity matrices for clustering, classifying archaea, evaluating MAG (metagenome-assembled genome) species assignment, applying skani for fast metagenomic ANI screening, or reconciling 16S rRNA-based taxonomy with whole-genome ANI.
tool_type: cli
primary_tool: skani
---

## Version Compatibility

Reference examples tested with: skani 0.2.5+ (Shaw & Yu 2023 Nat Methods 20:1661; bluenote-1577/skani), FastANI 1.34+ (Jain 2018 Nat Commun 9:5114), pyani 0.3.0+ (Pritchard 2016 Anal Methods 8:12), pyskani 0.1+ (Larralde 2025), OrthoANI 1.40+ (Lee 2016 Int J Syst Evol Microbiol 66:1100), OrthoANIu 1.2+, GTDB-Tk 2.7.1+ (Chaumeil 2022 Bioinformatics 38:5315), GTDB release 220 (2024-Q3+), TYGS web (Meier-Kolthoff & Goker 2019 Nat Commun 10:2182), GGDC v3.0 (web), Mash 2.3+ (Ondov 2016 Genome Biol 17:132), Dashing 2 (Baker & Langmead 2023 Genome Res 33:1218), CompareM 0.1.2+ for AAI (Parks/Cherubini), pyANI 0.3.1+, BLAT 36+, DIAMOND 2.1+. JSpeciesWS web (Richter et al 2016 Bioinformatics 32:929).

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `skani --version`; `fastANI --version`; `gtdbtk --version`; `mash --version`; `pyani --version`
- Python: `pip show gtdbtk pyani`

If code throws `GTDB-Tk database not found`, `skani sketch incompatible`, `Mash sketch version`, these tools have database-version coupling: GTDB-Tk requires the GTDB release matched to the binary version; Mash/skani sketches are forward-compatible but not always backward. Check `gtdbtk check_install` for database completeness.

# Genome Distance and Species Delineation

**"Are these genomes the same species, and what species are they?"** -> Prokaryote species delineation has shifted from 16S rRNA identity (now considered insufficient at < 98.7%) to **whole-genome ANI** at a 95% threshold (Jain 2018 Nat Commun 9:5114; corroborating Goris 2007 and Konstantinidis 2005). The modern operational standard for taxonomy is **GTDB-Tk** (Chaumeil 2020/2022 Bioinformatics 38:5315), which assigns genomes to the Genome Taxonomy Database (GTDB) using ANI radius + marker-gene placement. **skani** (Shaw & Yu 2023 Nat Methods 20:1661) has replaced FastANI as the default ANI tool in GTDB-Tk 2.4+ for being 20-30x faster while maintaining accuracy. The 95% ANI threshold is robust but not absolute -- the species circumscription radius varies by genus (Parks 2018 Nat Biotech 36:996).

- CLI: `skani dist genomes1.fa genomes2.fa -t 16` -- fast ANI computation
- CLI: `fastANI -q query.fa -r reference.fa -o output.txt` -- standard ANI
- CLI: `gtdbtk classify_wf --genome_dir genomes/ --out_dir gtdbtk_out --cpus 32` -- GTDB classification
- CLI: `mash dist *.fa` -- k-mer MinHash distance
- Web: TYGS (https://tygs.dsmz.de/) and GGDC (https://ggdc.dsmz.de/) for dDDH

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| skani (Shaw & Yu 2023 Nat Methods 20:1661) | Sparse chaining on minimizers; ANI estimation | ANI percent + alignment fraction | 20-30x faster than FastANI; default in GTDB-Tk 2.4+; supports MAGs | Currently no AAI; not for cross-domain (archaea vs bacteria) |
| FastANI (Jain 2018 Nat Comm 9:5114) | Mashmap-based fragment alignment | ANI percent + orthologous fraction | Standard ANI tool 2018-2023; well-validated | Slower than skani; designed for >=80% identity |
| pyani / pyANI (Pritchard 2016 Anal Methods 8:12) | Multi-method ANI: ANIb (BLASTN), ANIm (MUMmer), TETRA | ANI matrix + visualization | Multiple algorithm consensus; reproducible | Slower than skani / FastANI; legacy for many studies |
| OrthoANI / OrthoANIu (Lee 2016 IJSEM 66:1100) | Reciprocal-best-orthologs ANI | ANI percent (more robust than blast-based) | Considered more precise than ANIb | Slower; less integrated |
| GTDB-Tk (Chaumeil 2020/2022 Bioinformatics 38:5315) | Marker-gene phylogeny + ANI radius (skani; was FastANI v2.3.x) | Taxonomic classification at all ranks (GTDB nomenclature) | Modern prokaryote taxonomy standard | Specific to GTDB; some classifications differ from NCBI |
| TYGS (Meier-Kolthoff & Goker 2019 Nat Commun 10:2182) | dDDH (digital DNA-DNA hybridization) | Pairwise dDDH + species delineation | Most rigorous species delineation (vs traditional DDH) | Web-only; rate-limited; specific platform |
| GGDC (Auch 2010 Stand Genomic Sci 2:117; v3 web) | Digital DDH calculation | dDDH percent + thresholds | Validated against laboratory DDH | Web-only; computational cost |
| Mash (Ondov 2016 Genome Biol 17:132) | MinHash k-mer sketches | Approximate distance (1 - similarity) | Extremely fast for large-scale clustering | k-mer-based; loses biological interpretation |
| Dashing 2 (Baker & Langmead 2023 GR 33:1218) | Sketching with Bloom filter optimization | Same as Mash but faster | 5-10x faster than Mash | Newer; less broadly used |
| pyskani (Larralde 2025 NAR Genom Bioinform) | Python wrapper around skani | ANI in Python | Programmatic access; CI/CD friendly | Newer; ecosystem still developing |
| CompareM | All-vs-all AAI (amino acid identity) | AAI percent | Cross-genus comparison via protein | Slow; needs all proteomes |
| JSpeciesWS (web; Richter et al 2016) | ANIb / ANIm | Web ANI + species delineation | Standard for clinical microbiology | Web rate limits; slow |
| ANI Calculator (CGB Korea) | Web ANI | Web ANI | Quick check | Web-only |

Methodology evolves; verify GTDB release (currently r220 / 2024-Q3) and GTDB-Tk version compatibility. The 95% ANI species threshold has been confirmed across 90,000+ prokaryote genomes (Jain 2018; Parks 2018 demonstrating clear bimodality).

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Classify a bacterial genome to species | GTDB-Tk classify_wf | Standard prokaryote taxonomy; ANI + marker-gene placement |
| Compute ANI between two genomes | skani | Fast (vs FastANI); accurate |
| Compute ANI for 1000+ genome pairs | skani all-vs-all | Scales; preferred for screening |
| Verify species delineation publication | TYGS + GGDC dDDH | Gold standard for novel species |
| MAG species assignment | GTDB-Tk + skani; CheckM2 first for completeness | MAGs need quality assessment + taxonomy |
| Bacterial strain typing | ANIb or dDDH; 99-99.99% for same strain | Strain resolution requires ANI > 99% |
| Sub-species / serotype level | ANI > 99.5% + epidemiological context | Sub-species requires biology + ANI |
| Across deep prokaryote divergence | AAI (CompareM); ANI saturates below 75% | AAI better for cross-genus |
| Cross-archaeal vs bacterial taxonomy | Skani-archaea-aware OR separate analysis | Default skani doesn't differentiate domains explicitly |
| Fast metagenomic taxonomy screen | Mash or Dashing 2 | k-mer-based; sketches reusable |
| Distance for genome clustering | skani matrix -> hierarchical clustering or NJ | Standard workflow |
| Reconcile 16S vs genome taxonomy | Run both; check for inter-genus conflicts | 16S < 98.7% typically inadequate |
| Build a reference database for ANI lookup | skani sketches indexed; query against | Pre-sketched reference for repeated queries |
| Phylogenetic placement | GTDB-Tk + IQ-TREE on extracted markers | Place new genome in known tree |
| AAI for genera-level comparison | CompareM or aai.rb (KBase) | AAI < ANI signal at deep divergence |
| Subspecies-level pathogenicity | ANI > 99% + virulence-gene annotation | ANI alone insufficient |
| Type-strain comparison | TYGS automatic type-strain matching | Built-in type-strain database |

## Per-Tool Failure Modes

### skani / FastANI ANI saturating below 75%

**Trigger:** Computing ANI between two genomes at < 75% nucleotide identity.

**Mechanism:** ANI is computed only on alignable regions; at < 75% identity, alignment fraction drops dramatically (< 50%); the few alignable regions are biased toward conserved regions, inflating apparent ANI.

**Symptom:** Reported ANI 75-80% with alignment fraction < 50%; meaningless biologically.

**Fix:** Below 75% ANI, switch to AAI (amino-acid identity from translated proteins); AAI is more meaningful at deep divergence (~50% AAI between distant genera). For ANI matrix at long range, use Mash distance (k-mer-based, no alignment).

### GTDB-Tk database version mismatch

**Trigger:** Using GTDB-Tk binary with mismatched GTDB reference data version.

**Mechanism:** GTDB releases (r207, r214, r220, ...) include reference trees, marker-gene HMMs, and ANI sketch files; GTDB-Tk versions are aligned to specific releases. Mismatch causes silent or loud failures.

**Symptom:** GTDB-Tk fails with "marker gene HMM not found" or runs but produces inconsistent classifications.

**Fix:** Check release compatibility: `gtdbtk check_install` shows the expected vs found versions. Pin via `conda env`. Download the matching release from data.gtdb.ecogenomic.org.

### Below-95% ANI but same species (genus-specific radius)

**Trigger:** Strict 95% ANI threshold; rejecting closely related genomes as different species.

**Mechanism:** Parks 2018 demonstrated species-circumscription radius varies (typically 95-99% but tighter for some clonal lineages). For some genera (e.g., Pseudomonas), the species threshold is 94% per genus-specific analysis.

**Symptom:** Two clearly biologically-related strains (epidemiologically connected outbreak) have ANI 94%; using strict 95% calls them different species.

**Fix:** Use GTDB-Tk's species radius approach which uses genus-specific cutoffs. For novel-species naming, consider 95% as primary + ecology + biology. Report ANI alongside additional context (gene content, phenotype, ecology).

### High alignment fraction required (AF >= 0.5)

**Trigger:** ANI reported without alignment fraction; or AF < 0.5.

**Mechanism:** A 95% ANI with 20% AF (only 20% of genome alignable) is biologically meaningless; the comparison covers a small fraction of the genomes. Standard species delineation requires AF >= 0.5 + ANI >= 95%.

**Symptom:** ANI calls "same species" but only 20-30% of genome aligned.

**Fix:** Require AF >= 0.5 + ANI >= 95% for species call. Below this, classification is ambiguous; consider AAI or HGT (e.g. a phage-rich genome will have low AF to its actual species).

### MAG contamination / incompleteness

**Trigger:** Running GTDB-Tk on MAGs without CheckM2 pre-screening.

**Mechanism:** Low-completeness MAGs (< 50%) may have marker-gene gaps that break GTDB-Tk's placement; high-contamination MAGs (> 5%) place anomalously.

**Symptom:** GTDB-Tk reports "no genome retained" or makes implausible classifications.

**Fix:** Pre-filter MAGs with CheckM2 (Chklovski 2023 Nat Methods 20:1203): require >= 70% completeness, < 5% contamination, < 10% strain heterogeneity for species-level. For lower-quality MAGs, report genus-level only or exclude.

### Mash distance vs ANI inconsistency

**Trigger:** Using Mash distance for species delineation directly.

**Mechanism:** Mash distance = 1 - (Mash similarity) is correlated with 1 - ANI but is not the same metric. The 0.05 Mash distance threshold (sometimes cited as "5% Mash = 95% ANI") is approximate; exact ANI varies +-0.5%.

**Symptom:** Genomes with Mash distance 0.04-0.06 inconsistently called "same species" or not.

**Fix:** Use Mash for fast screening + clustering, but verify species delineation with ANI on candidate pairs. Mash 0.05 ~ ANI 95% is a rough heuristic; not a publishable threshold.

### Ortholog-based ANI conservative vs alignment-based

**Trigger:** Comparing OrthoANI / OrthoANIu to FastANI / skani.

**Mechanism:** OrthoANI uses reciprocal-best-orthologs; FastANI uses fragment alignment. They differ by 0.5-2% systematically; OrthoANI is more conservative.

**Symptom:** OrthoANI = 94.5%, FastANI = 96% on same pair; different "same species" calls.

**Fix:** Document tool used; for taxonomy, use the tool aligned to the reference database (GTDB-Tk uses skani; NCBI uses FastANI). Cross-validation for unclear cases.

### Tetranucleotide bias inflating Mash for low-GC genomes

**Trigger:** Comparing genomes with extreme GC content (Streptomyces ~70% vs Mycoplasma ~25%) via Mash.

**Mechanism:** k-mer frequency distributions are GC-dependent; Mash distance between extreme-GC genomes is inflated by background composition rather than biology.

**Symptom:** Two unrelated extreme-GC genomes (e.g. Mycoplasma + Mycoplasma) appear closer than they biologically are.

**Fix:** Use ANI / AAI for cross-GC comparisons; Mash is reliable only within a GC-comparable range. Document GC range when reporting Mash distances.

### Type strain conflicts in TYGS

**Trigger:** Submitting genome to TYGS where type strain is missing or misclassified.

**Mechanism:** TYGS depends on type strain database; if the type strain is genome-sequenced incompletely or misclassified, the placement may be incorrect.

**Symptom:** TYGS reports unexpected nearest type strain.

**Fix:** Cross-validate with GTDB-Tk; check type-strain genome quality. For novel-species naming, TYGS report should be supplemented with manual taxonomic check.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Species delineation ANI | >= 95% (Jain 2018) | Standard; based on 90,000 prokaryote genomes |
| Genus-specific species ANI radius | 94-99% (varies by clade) | Parks 2018 Nat Biotech 36:996 |
| Alignment fraction (AF) for ANI | >= 0.5 | Operational convention (GTDB-Tk / skani); below this, comparison too small |
| Strain delineation ANI | >= 99% (typical); >= 99.5% strict | Operational |
| Sub-species delineation | >= 99% ANI + epidemiology | Manual |
| AAI species delineation | >= 70% | Operational convention; varies clade |
| AAI genus delineation | >= 60% | Standard |
| dDDH species delineation | >= 70% | Goris 2007; matches ANI 95% |
| dDDH genus delineation | >= 50% | Auch 2010 |
| 16S rRNA species threshold (deprecated) | >= 98.7% | Stackebrandt 2006; superseded by ANI |
| Mash distance ~ ANI heuristic | 0.05 ~ 95% ANI | Ondov 2016; rough |
| GTDB-Tk completeness for placement | >= 50% (CheckM2 OBLIGATE >= 70%) | Chaumeil 2022 |
| GTDB-Tk contamination | < 10% (< 5% for species-level) | Chaumeil 2022 |
| MAG quality for taxonomy | CheckM2 >= 70% comp, < 5% cont, < 10% strain het | Chklovski 2023 |
| skani CLI threads | up to 64; scales linearly | skani docs |
| skani sketch size | default 1000 minimizers; tunable | skani docs |
| FastANI default fragment | 3000 bp; varies | Jain 2018 default |
| GTDB-Tk classify_wf time per genome | 2-30 min on 16 CPUs | Empirical |
| Type strain ANI uncertainty | +- 1% | Operational |

## skani Standard Workflow

**Goal:** Compute ANI between query and reference set; classify species.

**Approach:** Build skani sketch -> compute distances -> apply species delineation logic.

```bash
# 1. Pre-sketch reference set
skani sketch reference_genomes/*.fa -o reference_sketches

# 2. Compute ANI for a single query
skani dist query.fa reference_sketches/* -t 16 \
    --robust --slow > query_distances.tsv

# 3. Compute all-vs-all matrix (large set)
skani triangle genomes/*.fa -t 32 --robust --sparse -o ani_matrix.tsv
# --sparse emits tabular Ref_file Query_file ANI Align_fraction_ref Align_fraction_query;
# without --sparse, `skani triangle` emits a Phylip-style square matrix.

# 4. Filter and visualize
awk '$3 >= 95 && $5 >= 50' query_distances.tsv > species_matches.tsv
```

```python
'''Apply 95% ANI species delineation with AF >= 0.5 constraint.'''
import pandas as pd
import numpy as np


def parse_skani(path):
    '''skani output: Ref_file Query_file ANI Align_fraction_ref Align_fraction_query'''
    df = pd.read_csv(path, sep='\t')
    df.columns = ['ref_file', 'query_file', 'ani', 'af_ref', 'af_query']
    return df


def species_delineate(df, ani_threshold=95.0, af_threshold=0.5):
    '''Return genome pairs called same species.'''
    df['min_af'] = df[['af_ref', 'af_query']].min(axis=1)
    same_species = df[(df['ani'] >= ani_threshold) & (df['min_af'] >= af_threshold)]
    return same_species
```

## GTDB-Tk Classification Workflow

**Goal:** Assign GTDB taxonomy (kingdom -> species) to a set of bacterial/archaeal genomes.

**Approach:** GTDB-Tk classify_wf identifies markers, builds tree placement, calculates ANI radius, returns full taxonomy.

```bash
# Set environment
export GTDBTK_DATA_PATH=/path/to/release220_data

# Verify install
gtdbtk check_install

# Run classify_wf
gtdbtk classify_wf \
    --genome_dir genomes/ \
    --out_dir gtdbtk_out \
    --cpus 32 \
    --extension fa \
    --skip_ani_screen   # Skip if want phylogeny-based only

# Output:
#   gtdbtk_out/classify/gtdbtk.bac120.summary.tsv   bacterial classifications
#   gtdbtk_out/classify/gtdbtk.ar53.summary.tsv     archaeal classifications
#   gtdbtk_out/identify/                              marker gene tables
#   gtdbtk_out/align/                                 multiple sequence alignments
```

```python
'''Parse GTDB-Tk summary for ranked classification.'''
import pandas as pd


def parse_gtdbtk_summary(path):
    '''GTDB-Tk summary columns include: user_genome, classification, classification_method, ani, msa_percent'''
    df = pd.read_csv(path, sep='\t')
    df['classification_split'] = df['classification'].str.split(';')
    df['kingdom'] = df['classification_split'].str[0].str.replace('d__', '')
    df['phylum'] = df['classification_split'].str[1].str.replace('p__', '')
    df['class'] = df['classification_split'].str[2].str.replace('c__', '')
    df['order'] = df['classification_split'].str[3].str.replace('o__', '')
    df['family'] = df['classification_split'].str[4].str.replace('f__', '')
    df['genus'] = df['classification_split'].str[5].str.replace('g__', '')
    df['species'] = df['classification_split'].str[6].str.replace('s__', '')
    return df


df = parse_gtdbtk_summary('gtdbtk_out/classify/gtdbtk.bac120.summary.tsv')
df_species_level = df[df['species'] != '']  # Species-level classification
df_high_quality = df[df['msa_percent'] > 80]
```

## TYGS / GGDC for dDDH

For publication-grade novel-species naming, dDDH is required. Use the TYGS web service (https://tygs.dsmz.de/) or GGDC (https://ggdc.dsmz.de/). Submit FASTA -> receive dDDH against type strains + phylogeny.

## Mash for Fast Clustering

```bash
# Sketch all genomes (do once)
mash sketch -p 16 -o all_sketches genomes/*.fa

# All-vs-all distance
mash dist -p 16 all_sketches.msh all_sketches.msh > mash_distances.tsv

# Cluster via NJ or hierarchical clustering
python -c "
import pandas as pd
from scipy.cluster import hierarchy
df = pd.read_csv('mash_distances.tsv', sep='\t', header=None,
                 names=['ref', 'query', 'distance', 'pvalue', 'shared_hashes'])
matrix = df.pivot('ref', 'query', 'distance').fillna(0)
linkage = hierarchy.linkage(matrix.values, method='average')
hierarchy.dendrogram(linkage, labels=matrix.columns)
"
```

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| skani says 96%, FastANI says 95.5% | Tool difference; both > 95% threshold | Consistent species call |
| skani says 95.2%, FastANI says 94.8% | Borderline case, tool difference | Cross-validate with OrthoANI; check GTDB-Tk |
| ANI = 94%, dDDH = 70% | Different metrics; both borderline same-species | Standard concordant ambiguous; report both |
| 16S rRNA same; ANI < 95% | 16S insufficient for species (Stackebrandt 2006) | Trust ANI; reclassify |
| GTDB says species X, NCBI says species Y | GTDB taxonomy differs from NCBI for ~10% of species | Use GTDB for genome-based; cite both if external comparison |
| ANI 96%, AF 0.3 | Insufficient alignment fraction | Same-species call invalid; report cautious |
| ANI 99%, AF 0.9 | Same species, high confidence | Robust species call |
| Mash 0.04 distance, FastANI 94.5% ANI | Different units; both around species threshold | Use ANI for definitive call |
| OrthoANI 94%, FastANI 96% | Method variation | Cross-check with skani; report range |
| GTDB-Tk classifies but MSA % < 50 | Low-quality placement | Report at higher rank (genus) only |
| TYGS gives unexpected nearest type strain | Type-strain database issue | Verify type-strain quality; cross-validate with GTDB |
| MAG GTDB-Tk classify fails | Incomplete MAG; missing markers | Improve assembly; report at family or order only |

**Operational rule for publication:** GTDB-Tk classify_wf as primary classification + ANI to nearest type strain (skani or FastANI) + AF >= 0.5 + report Tettelin partition where relevant + cross-validate with dDDH (TYGS) for novel-species claims.

## Cohort Gotchas

- **Archaea:** GTDB has separate ar53 marker set; specify `--archaea` or let GTDB-Tk auto-detect
- **Cyanobacteria:** large genomes, sometimes split GTDB-Tk markers; cross-validate
- **MAGs from metagenomes:** require CheckM2 quality filter first
- **Strain-level resolution:** ANI > 99% needed; epidemiological context useful
- **Endosymbionts:** small / reduced genomes; ANI may be unreliable
- **High-GC genomes (Streptomyces, Mycobacterium):** GTDB-Tk specific markers handle these
- **Type strains:** authoritative anchor for taxonomy; TYGS automatic
- **Pre-2017 ANI publications:** likely used 30-fold lower-precision tools; verify current ANI
- **Sub-species naming:** ANI 99% + biology + epidemiology; not standardized
- **Cross-domain comparisons (Bacteria vs Archaea):** rarely meaningful; AAI better

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why 95% ANI?" | Jain 2018 Nat Comm 9:5114; 90,000 prokaryote genomes demonstrate clear bimodality at 95% |
| "Genus-specific radius?" | GTDB-Tk uses genus-specific ANI radius; ranges 94-99% per genus |
| "AF >= 0.5 reported?" | Yes; standard convention; sub-0.5 invalidates species call |
| "Tool choice?" | skani 2.4+ default in GTDB-Tk; FastANI for verification; OrthoANI as third check for borderline cases |
| "GTDB vs NCBI?" | GTDB taxonomy is genome-based; NCBI is heritage; cite GTDB primary, NCBI secondary |
| "Type strain comparison?" | TYGS automatic type-strain matching; reported alongside ANI |
| "MAG quality?" | CheckM2 >= 70% completeness, < 5% contamination required; reported per MAG |
| "dDDH for novel species?" | TYGS performed; dDDH >= 70% threshold for same species |
| "Multiple methods agree?" | skani + FastANI + OrthoANI converged within 1% on candidate pairs |
| "GTDB release version?" | r220 (2024-Q3); database version pinned |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| skani "sketch incompatible" | Old sketch + new skani | Rebuild sketches; use same skani version |
| GTDB-Tk "marker not found" | Wrong GTDB version | Update GTDB-Tk + database to matching release |
| FastANI "no alignment" | < 75% ANI | Switch to AAI or Mash |
| pyani memory exhaustion | > 50 genomes | Use skani or pre-cluster with Mash |
| Mash distance pvalue uninformative | Default | Use NA filter; trust distance directly |
| TYGS web rate limit | Submitting too many genomes | Batch submissions; use offline GGDC if available |
| GTDB-Tk classify_wf classification empty | Genomes < 50% complete | Filter MAGs with CheckM2 first |
| OrthoANI very slow | All-vs-all on > 50 genomes | Use skani for screening |
| skani sketch GTDB databases | GTDB-Tk auto-sketches | Don't re-sketch separately |
| Custom species ID needed | TYGS supports type-strain comparison + GGDC for dDDH | Use both |
| ANI vs 16S contradict | 16S insufficient | Trust ANI |
| Subspecies confusion | ANI > 99% + biology required | Standardize naming |

## Tool Installation Notes

```bash
# skani
conda install -c bioconda skani

# FastANI
conda install -c bioconda fastani

# GTDB-Tk
conda install -c bioconda gtdbtk
# Download database
wget https://data.gtdb.ecogenomic.org/releases/release220/220.0/auxillary_files/gtdbtk_r220_data.tar.gz
tar xf gtdbtk_r220_data.tar.gz
export GTDBTK_DATA_PATH=$PWD/release220

# pyani / pyANI
pip install pyani-plus

# Mash + Dashing 2
conda install -c bioconda mash
conda install -c bioconda dashing2

# CheckM2 for MAG QC
conda install -c bioconda checkm2

# OrthoANI / OrthoANIu
git clone https://github.com/EzbioCloud-Bioinformatics-Team/OrthoANIu
```

For 1000+ genome scans, use cluster with 64+ cores; skani all-vs-all on 1000 genomes runs in ~10-30 minutes; GTDB-Tk classify_wf runs in ~20-60 min per 100 genomes.

## References

- Jain C et al 2018 Nat Commun 9:5114 (FastANI; 95% ANI threshold)
- Shaw J & Yu YW 2023 Nat Methods 20:1661 (skani)
- Chaumeil P-A et al 2020 Bioinformatics 36:1925 (GTDB-Tk v1)
- Chaumeil P-A et al 2022 Bioinformatics 38:5315 (GTDB-Tk v2)
- Parks DH et al 2018 Nat Biotech 36:996 (GTDB establishment)
- Parks DH et al 2022 Nucleic Acids Res 50:D785 (GTDB r207)
- Meier-Kolthoff JP & Goker M 2019 Nat Commun 10:2182 (TYGS)
- Auch AF et al 2010 Stand Genomic Sci 2:117 (GGDC)
- Ondov BD et al 2016 Genome Biol 17:132 (Mash MinHash)
- Baker DN & Langmead B 2023 Genome Res 33:1218 (Dashing 2)
- Pritchard L et al 2016 Anal Methods 8:12 (pyani)
- Lee I et al 2016 IJSEM 66:1100 (OrthoANI)
- Richter M et al 2016 Bioinformatics 32:929 (JSpeciesWS web server)
- Goris J et al 2007 IJSEM 57:81 (ANI threshold validation)
- Konstantinidis KT & Tiedje JM 2005 PNAS 102:2567 (species definition via ANI + gene content)
- Stackebrandt E & Ebers J 2006 Microbiol Today 33:152 (16S thresholds; superseded)
- Chklovski A et al 2023 Nat Methods 20:1203 (CheckM2)
- Olm MR et al 2017 ISME J 11:2864 (dRep; ANI clustering)
- Rodriguez-R LM & Konstantinidis KT 2014 Microbe 9:111 (ANI reference)
- Yoon S-H et al 2017 IJSEM 67:1613 (EzBioCloud database)
- Larralde M et al 2025 NAR Genom Bioinform 7:lqaf095 (pyskani, pyfastani, pyorthoani)

## Related Skills

- comparative-genomics/pangenome-analysis - ANI-based clustering precedes pangenome construction
- comparative-genomics/ortholog-inference - Cross-species ANI as orthology benchmark
- comparative-genomics/hgt-detection - High-ANI same-species genomes for HGT context
- comparative-genomics/gene-tree-species-tree-reconciliation - Species-tree construction precedes ANI species delineation
- phylogenetics/species-trees - Marker-gene tree alongside ANI
- metagenomics/kraken-classification - Metagenomic classification different problem
- metagenomics/metaphlan-profiling - Profile vs taxonomic placement
- genome-assembly/assembly-qc - Quality before classification
- read-qc/quality-reports - CheckM2 on MAGs
- variant-calling/clinical-interpretation - Pathogen typing context
<!-- END FILE: comparative-genomics/genome-distance-and-species-delineation/SKILL.md -->

## 子目录：comparative-genomics/hgt-detection

<!-- BEGIN FILE: comparative-genomics/hgt-detection/SKILL.md -->
---
name: bio-comparative-genomics-hgt-detection
description: Detect horizontal gene transfer (HGT / LGT) using compositional methods (GC%, codon usage, tetranucleotide z-scores via SIGI-HMM, AlienHunter, IslandViewer 4, IslandPath-DIMOB), phylogenetic-incongruence methods (AvP, HGTphyloDetect, ALE / GeneRax / AleRax reconciliation, RANGER-DTL), and BLAST-distribution methods (HGTector v2, DarkHorse, Alien Index). Use when screening prokaryote genomes for genomic islands and HGT events, distinguishing HGT from incomplete lineage sorting / differential gene loss / hybridization, mapping donor lineages via phylogenetic placement, separating eukaryotic HGT from contamination, ruling out gBGC as a false signal, or quantifying DTL rates with ALE/GeneRax on bacterial trees.
tool_type: mixed
primary_tool: HGTector
---

## Version Compatibility

Reference examples tested with: HGTector 2.0b3+, AvP 1.0.4+, HGTphyloDetect 1.0+, ALE 1.0+ (ssolo/ALE github), GeneRax 2.1.3+, AleRax 1.2.0+ (Morel 2024), RANGER-DTL 2.0+, IslandViewer 4 (web), mobileOG-db 1.0+, MetaCHIP 1.10+, IQ-TREE 2.3.6+, BioPython 1.84+, DIAMOND 2.1.10+. Open Tree of Life and NCBI Taxonomy reference databases updated 2024-Q3 minimum for HGTector/AvP.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show hgtector` then `hgtector search --help`
- CLI: `ALEml_undated --help`, `generax --help`, `alerax --help`
- DB: `hgtector database --check` for taxonomy version

If code throws `Taxonomy ID not found`, `database version mismatch`, or `KeyError` on NCBI taxids, refresh the local taxonomy dump (NCBI updates monthly). ALE/GeneRax expect newick gene trees with bootstraps; AleRax expects gene-tree distributions (uniform bootstrap samples or UFBoot trees).

# Horizontal Gene Transfer Detection

**"Are these genes horizontally acquired, and from where?"** -> HGT signal lives in three orthogonal signal classes: composition (recent transfers carry donor codon usage; erodes by Lawrence-Ochman 1998 amelioration in ~50-200 Myr), phylogeny (gene tree nests within distant clade), and phyletic distribution (patchy taxonomic presence). No single class proves HGT; **claims require concordance across at least two classes** plus mandatory exclusion of contamination and differential gene loss (DGL). The most consequential failure mode in eukaryotic HGT detection is contamination passing all three classes silently (Boothby 2015 tardigrade "17% HGT" refuted by Koutsovoulos 2016; Crisp 2015 human "145 HGTs" refuted by Salzberg 2017 GB 18:85).

- Python: `hgtector search` -> `hgtector analyze` for BLAST-distribution screen
- Python: `AvP` (Koutsovoulos 2022 PLoS Comp Biol 18:e1010686) for eukaryotic phylogenetic HGT with automated tree workflow
- CLI: `ALEml_undated` (Szöllősi 2013 Syst Biol 62:901), `generax` (Morel 2020 MBE 37:2763), `alerax` (Morel 2024 Bioinformatics 40:btae162) for prokaryote DTL reconciliation
- Web: IslandViewer 4 (Bertelli 2017 NAR 45:W30) for bacterial genomic islands
- CLI: `metachip` (Song 2019 Microbiome 7:36) for metagenomic HGT inference

## Algorithmic Taxonomy

| Method class | Tool | Signal | Strength | Fails when |
|--------------|------|--------|----------|------------|
| Composition (parametric) | SIGI-HMM (Waack 2006 BMC Bioinf 7:142) | HMM on codon-usage anomaly | Recent transfers (<50 Myr); single-locus resolution | Amelioration eroded composition; native composition heterogeneous (Streptomyces, Borrelia) |
| Composition (parametric) | AlienHunter (Vernikos & Parkhill 2006 Bioinformatics 22:2196) | Variable-window tetranucleotide IVOM | Recent island detection; window-size aware | Old transfers; high-variance native composition |
| Composition (parametric) | IslandPath-DIMOB (Bertelli 2017) | Dinucleotide bias + mobility genes | Combines composition + mobile-element signature | Mobile-element-free transfers |
| Composition aggregator | IslandViewer 4 web (Bertelli 2017 NAR 45:W30) | Consensus of IslandPath / SIGI / IslandPick | Best single-genome bacterial screen; curated benchmark | Recent radiations; close-relative donors |
| BLAST-distribution | HGTector v2 (Zhu 2014 BMC Genomics 15:717) | Close vs distal BLAST hit ratio against full taxonomy | No tree required; scales to thousands of genomes | Close-relative donors (similar lineage hits); incomplete taxonomic sampling |
| BLAST-distribution | DarkHorse (Podell & Gaasterland 2007 GB 8:R16) | Lineage Probability Index (LPI) | Quantifies taxonomic prior of best hits | Same lineage-coverage caveat as HGTector |
| BLAST-distribution | Alien Index (Gladyshev 2008 Science 320:1210; recent: AI tools) | Best hit metazoan vs non-metazoan score | Standard for eukaryote HGT screen | False positives from rapid evolution / contamination |
| Phylogenetic incongruence | AvP (Koutsovoulos 2022) | Automated tree-building + AU test on candidate HGTs | End-to-end eukaryote pipeline; orthogroup-aware | Poor taxon sampling at putative donor lineage |
| Phylogenetic incongruence | HGTphyloDetect (Yuan 2023 Brief Bioinform 24:bbad035) | Web-friendly; Bayesian incongruence test | Modern eukaryote-friendly | Computationally heavy at genome scale |
| Probabilistic DTL reconciliation | ALE (Szöllősi 2013) | Amalgamated likelihood over gene-tree sample | Bayesian-posterior over D/T/L events; explicit donor inference | Requires gene tree distribution (bootstrap or UFBoot) |
| Probabilistic DTL reconciliation | GeneRax (Morel 2020) | ML reconciliation; species-tree-aware | Faster than ALE; refines noisy gene trees | Less uncertainty quantification than ALE |
| Probabilistic DTL reconciliation | AleRax (Morel 2024) | Co-estimates gene + species trees + DTL rates | Gold standard 2024; corrects gene-tree-error feedback | Computationally heavy; needs >= 20 species |
| Parsimony reconciliation | RANGER-DTL 2.0 (Bansal 2018 Bioinformatics 34:3214) | Min-cost DTL parsimony | Fast; deterministic; many trees | No likelihood; sensitive to event-cost choice |
| Metagenome HGT | MetaCHIP (Song 2019 Microbiome 7:36) | BLAST + phylogeny on MAG-pairs | Designed for metagenome-assembled genomes | Requires high-quality MAGs (>= 90% complete) |
| HGT-aware species tree | ASTRAL-Pro2 (Zhang & Mirarab 2022 Bioinformatics 38:4949) | Quartet-coalescent with paralog handling | Robust to HGT-inflated gene-tree discord | Still assumes ILS-coalescent; not explicit HGT model |

Methodology evolves; verify the current AleRax / AvP documentation before committing to a single approach. ALE/GeneRax/AleRax have largely superseded older parsimony reconciliation for bacterial phylogenomics.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Single bacterial genome, recent HGT screen | IslandViewer 4 (web) + HGTector v2 | Composition + BLAST distribution; standard 1-genome workflow |
| 5-200 bacterial genomes, ancient HGT focus | ALE or AleRax on orthogroup trees | Probabilistic DTL; recovers ancient transfers obscured by amelioration |
| 200+ bacterial genomes, phylogenomic HGT rates | GeneRax (faster) -> ALE (validation on top candidates) | Scales; ALE only for the candidates needing posterior support |
| Eukaryote genome, suspected HGT | **Contamination check first** (see below); then AvP or HGTphyloDetect | Eukaryote HGT field is dominated by contamination false positives |
| Metagenome / MAG analysis | MetaCHIP (Song 2019) | Designed for MAGs; tolerates fragmentation |
| Gene-family-level HGT rate inference | ALE/AleRax with site-rate variation | Posterior over D/T/L rates; quantitative inference |
| Donor inference (which lineage was the source) | ALE branch-wise D/T/L map; AvP donor placement | Both attach donor branch posterior |
| Plant-plant HGT (parasitic-host) | AvP with broader plant taxa; manual gene-tree inspection | Standard methods often miss plant-plant transfers |
| Putative HGT correlated with antibiotic resistance | IslandViewer + AMRFinderPlus + mobileOG-db | Combine HGT detection with mobile-element + resistance annotation |
| Phage-mediated transfer screen | PHASTER / PhageBoost + IslandViewer | Phage detection orthogonal to general HGT |
| Endosymbiotic gene transfer (organelle -> nucleus) | Custom: BLAST nuclear proteome against mitochondrial/plastid proteome; tree per hit | Standard HGT tools miss EGT context; expect ~5-15% of nuclear plant proteome is plastid-derived |
| Putative HGT shows incongruence but no other evidence | Test against ILS, DGL, hybridization | Phylogenetic discordance has biological alternatives (Maddison 1997 Syst Biol 46:523) |

## Per-Tool Failure Modes

### Contamination masquerading as eukaryotic HGT (THE critical failure)

**Trigger:** Eukaryote genome assembly, especially from non-axenic culture, microbiome-associated organism, or low-coverage shotgun.

**Mechanism:** Bacterial DNA in the sample is assembled as contigs separate from the eukaryote nuclear contigs but is reported as part of the assembly. Genes on contaminant contigs phylogenetically nest within bacteria, compositionally differ from the eukaryote, and have patchy phyletic distribution -- triggering all three HGT signal classes simultaneously.

**Symptom:** "HGT" genes are concentrated on short, low-coverage contigs; have GC% dramatically different from the bulk genome; show codon usage indistinguishable from bacteria; cluster on contigs lacking eukaryotic gene order; the genome assembly's BUSCO completeness anomaly indicates contamination (e.g. tardigrade Hypsibius dujardini: Boothby 2015 PNAS 112:15976 -> Koutsovoulos 2016 PNAS 113:5053 contamination refutation).

**Fix:** MANDATORY contamination filter before any eukaryotic HGT analysis. Use BlobTools2 (Challis 2020 G3) coverage-vs-GC visualization to identify contaminant blobs; Kraken2 (Wood 2019 GB 20:257) or Conterminator (Steinegger 2020 GB 21:115) to taxonomically classify contigs; FCS-GX (Astashyn 2024 GB 25:60) is the NCBI tool now required for GenBank submission. Apply these BEFORE running AvP / HGTector / Alien Index. After cleaning, re-screen. Crisp 2015 Genome Biol 16:50 "145 HGT in humans" was nearly all refuted by Salzberg 2017 GB 18:85 contamination-aware reanalysis (only known mitochondrial and retroviral insertions survive).

### Amelioration eroding compositional signal

**Trigger:** Compositional-only HGT calls on bacterial genomes diverged > 50 Myr from donor.

**Mechanism:** After transfer, point mutations occur under host mutation bias (e.g. AT bias in obligate symbionts), driving codon usage and GC% toward host values (Lawrence & Ochman 1997 J Mol Evol 44:383; 1998 PNAS 95:9413). Half-life of compositional signal in bacteria is roughly 50-200 Myr depending on mutation rate and selection. Ancient transfers are compositionally indistinguishable from native genes.

**Symptom:** Phylogenetic methods detect transfer but composition-based tools (SIGI, IslandPath) miss it; GC anomaly is weak (|z| < 2); codon adaptation index resembles native genes.

**Fix:** For HGT older than ~50 Myr, rely on phylogenetic methods (ALE / AvP); composition is informative only as supporting evidence for recent transfers. Report transfer age estimate from ALE branch posterior alongside composition.

### Differential gene loss mimicking HGT

**Trigger:** Gene present in distantly related taxa but absent in immediate sister lineages.

**Mechanism:** An ancestral gene is independently lost in multiple intermediate lineages; the surviving taxa appear "incompatible" with the species tree. Phylogenetic incongruence and patchy taxonomic distribution are identical to HGT signatures (Maddison 1997 Syst Biol 46:523).

**Symptom:** Gene-tree topology actually matches species-tree topology of the surviving taxa, just with intermediate taxa missing. Composition matches the recipient genome (no HGT amelioration to explain). ALE infers high loss rate at branches and may favor a "transfer + loss" or "duplication + losses" event class depending on cost weights.

**Fix:** Inspect ALE event-class posteriors (D vs T vs L); when loss rate inference is non-negligible at sister branches, prefer the loss-explanation. Check independently sequenced relatives if available. Quantify Dollo-parsimony loss vs ML-DTL event likelihoods. RANGER-DTL with loss cost = 1, transfer cost = 3 favors loss; rerun with transfer cost = 1.5 to see sensitivity.

### Hybridization / reticulate evolution

**Trigger:** Sister species suspected to have hybridized or share recent introgression; rapid radiations.

**Mechanism:** Gene flow between closely related lineages produces gene-tree species-tree discordance indistinguishable from HGT at short divergence times. Phylogenetic networks (not trees) are required.

**Symptom:** Multiple genes show identical pattern of incongruence (same direction, same sister); D-statistic (see [[introgression-detection]]) significantly different from zero between candidate hybrid and its inferred sister.

**Fix:** Run ABBA-BABA / Dsuite for the candidate (see [[introgression-detection]]); if introgression signal is uniform across the genome, prefer hybridization explanation. ALE on bacterial trees can handle this via transfer-with-replacement; for eukaryotes, phylogenetic networks (e.g. PhyloNetworks / SNaQ via Solis-Lemus & Ane 2016 PLoS Genet 12:e1005896, or NakhlehLab PhyloNet) properly model reticulation.

### gBGC-driven AT->GC substitution bias

**Trigger:** Mammalian / vertebrate gene with apparent unusual nucleotide composition triggering compositional HGT call.

**Mechanism:** GC-biased gene conversion (gBGC) in regions of high recombination drives Weak->Strong (AT->GC) fixation independently of selection (Galtier & Duret 2007 Trends Genet 23:273). Sub-telomeric and recombination-hot regions show elevated GC indistinguishable from a GC-rich HGT donor at the composition level.

**Symptom:** "HGT" candidates cluster in sub-telomeric regions or high-recombination zones; W->S substitution bias is elevated; phylogenetic placement is consistent with host species; selection scans (BUSTED) show no signal.

**Fix:** Test for gBGC explicitly via W->S vs S->W substitution ratios (Capra 2013 PLoS Genet 9:e1003684); require non-zero phylogenetic incongruence in addition to composition; exclude regions with recombination rate > 90th percentile.

### Close-relative donor making BLAST methods fail

**Trigger:** Transfer between species in the same genus or family (genus-level transfer).

**Mechanism:** HGTector / DarkHorse / Alien Index compare close vs distal BLAST hits; when donor is closely related, hits cluster in "close" and the method reports no anomaly.

**Symptom:** HGTector hgt_score near zero, but the gene shows clear phylogenetic placement within a sister taxon rather than expected vertical inheritance.

**Fix:** Use phylogenetic methods (ALE on orthogroup trees) for genus-level HGT; BLAST-distribution methods are designed for inter-phylum transfer. Restrict HGTector taxonomic comparison level (`--rank order` or higher).

### Poor sampling of donor lineage

**Trigger:** Putative HGT phylogenetically places "near" a poorly sampled taxon (e.g. Archaea or candidate phyla).

**Mechanism:** Long branches in the donor clade attract the query gene by LBA (Felsenstein 1978 Syst Zool 27:401); poor sampling means real intermediate relatives are absent, and the gene appears nested within the wrong clade.

**Symptom:** AU/SH topology test rejects alternative placements only marginally (p ~ 0.05); adding any newly available genome from the candidate donor lineage changes placement substantially.

**Fix:** Use site-heterogeneous models (CAT-PMSF, PhyloBayes-MPI) to mitigate LBA at deep nodes; add taxa from undersampled lineages where possible; report donor inference with explicit support-level caveats. Cross-check with ALE branch posterior, which integrates over alternative donor lineages probabilistically.

### Tetranucleotide z-score thresholding in heterogeneous genomes

**Trigger:** Applying generic |z| > 2 cutoff to genomes with naturally high composition variance (Streptomyces, Burkholderia, Halophiles).

**Mechanism:** rRNA operons, prophage remnants, and CRISPR arrays have native composition anomalies; generic z-score thresholds flag them as HGT.

**Symptom:** "HGT" calls concentrate in rRNA-flanking regions, ribosomal protein operons, or annotated prophages.

**Fix:** Mask known native-anomaly features (rRNA, tRNA, CRISPR) before composition analysis; use genome-specific thresholds calibrated against confirmed native genes; raise |z| threshold to 3 for high-variance genomes.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| HGT call requires concordance | >= 2 of 3 signal classes (composition, phylogeny, distribution) | Standard convention (Ravenhall 2015 PLoS Comp Biol 11:e1004095) |
| HGTector hgt_score | > 0.5 moderate; > 1.0 strong | HGTector documentation; Zhu 2014 |
| Alien Index | AI > 45 (P_metazoan / P_non-metazoan) | Gladyshev 2008 Science 320:1210; modern eukaryote default |
| GC z-score generic threshold | |z| > 2 suggestive; > 3 strong | But raise to >= 3 for high-variance genomes |
| Genomic island minimum size | >= 5 contiguous genes / >= 8 kb | IslandViewer 4 default |
| ALE D/T/L event posterior | branch-wise event > 0.5 to call transfer | ssolo/ALE convention |
| AU test for tree-topology rejection | p < 0.05 to reject vertical inheritance topology | Shimodaira 2002 Syst Biol 51:492 |
| Tree-based HGT minimum sequences | >= 8 taxa per gene tree; >= 4 from putative recipient clade | Below this, donor inference unreliable |
| Required contamination-screen completeness | FCS-GX or BlobTools applied; documented in methods | NCBI GenBank now requires FCS-GX for new submissions |
| ALE undated vs dated | Use undated for ancient comparisons; dated for time-calibrated trees | Szöllősi 2013; AleRax recommends dated when sub-clade times are available |
| Bayesian gene-tree sample size for ALE | >= 100 bootstrap or UFBoot trees | ALE convention |
| Donor lineage minimum sampling | >= 5 genomes from candidate donor order | Below this, donor inference is exploratory |
| Eukaryotic HGT post-cleanup threshold | Re-screen after FCS-GX / BlobTools; expect 10-50x reduction | Boothby->Koutsovoulos 2016 (17.5% -> ~0.4% genes); Crisp->Salzberg 2017 (145 -> ~0, near-total refutation) |
| MetaCHIP MAG quality | >= 90% complete, < 5% contamination (CheckM2) | Song 2019 |

## HGTector v2 Workflow

**Goal:** Identify HGT candidates in a prokaryote genome via taxonomic BLAST hit distribution.

**Approach:** Build / download taxonomy database -> `hgtector search` to run DIAMOND against reference proteomes -> `hgtector analyze` to score close-vs-distal taxonomic distribution -> rank candidates by score.

```python
'''HGTector v2 wrapper with quality filters'''

import subprocess
import pandas as pd


def run_hgtector(proteome_faa, out_dir, db_dir, threads=8, rank='order'):
    '''HGTector v2 search + analyze.

    rank: NCBI taxonomic rank below which hits are "close"; "order" is default.
    Use "family" to detect family-level transfers, "phylum" only for ancient inter-phylum HGT.
    '''
    subprocess.run([
        'hgtector', 'search', '-i', proteome_faa, '-o', f'{out_dir}/search',
        '-m', 'diamond', '-d', f'{db_dir}/db.dmnd', '-t', str(threads),
        '--queries-per-batch', '200'
    ], check=True)
    subprocess.run([
        'hgtector', 'analyze', '-i', f'{out_dir}/search', '-o', f'{out_dir}/analyze',
        '-t', f'{db_dir}/taxdump', '--rank-self', rank,
        '--rank-close', rank, '--bandwidth', 'auto'
    ], check=True)
    return f'{out_dir}/analyze'


def parse_hgtector(analyze_dir, min_score=0.5):
    '''HGTector outputs scores.tsv with: gene, hits, close, distal, ...
    distal > close indicates likely foreign origin.
    '''
    df = pd.read_csv(f'{analyze_dir}/scores.tsv', sep='\t')
    df['hgt_score'] = df['distal'] - df['close']
    df['confidence'] = pd.cut(df['hgt_score'], bins=[-1e9, 0.5, 1.0, 1e9],
                              labels=['low', 'moderate', 'strong'])
    return df[df['hgt_score'] > min_score].sort_values('hgt_score', ascending=False)
```

## ALE Probabilistic DTL Reconciliation

**Goal:** Quantify D / T / L events with branch-wise posterior on a bacterial / archaeal species tree.

**Approach:** Infer per-orthogroup gene-tree bootstrap distributions (UFBoot from IQ-TREE) -> observe (encode as `.ale` files) -> run `ALEml_undated` to reconcile against species tree -> extract per-branch transfer count posteriors.

```bash
# 1. Build per-orthogroup UFBoot trees
for og in orthogroups/*.fa; do
    iqtree2 -s $og -m TEST -B 1000 -nt 2 --prefix ${og%.fa}_ufb
done

# 2. Observe and reconcile
for tree in orthogroups/*_ufb.ufboot; do
    ALEobserve $tree
    ALEml_undated species_tree.nwk ${tree}.ale separators="|" sample=100
done

# 3. Aggregate D/T/L counts per species-tree branch
python aggregate_ale.py orthogroups/*_uTs > dtl_branchwise.tsv
```

```python
'''Aggregate ALE outputs into branch-wise event tables.'''
import re
from collections import defaultdict
import pandas as pd

def parse_ale_uts(uts_file):
    '''ALE _uTs format: per-branch D/T/L counts (mean over sampled reconciliations).'''
    branch_events = {}
    with open(uts_file) as fh:
        for line in fh:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 5:
                branch_id = parts[0]
                # columns: branch  duplications  transfers  losses  originations
                branch_events[branch_id] = {
                    'duplications': float(parts[1]),
                    'transfers': float(parts[2]),
                    'losses': float(parts[3]),
                    'originations': float(parts[4])
                }
    return branch_events
```

Bacterial datasets characteristically show transfers >> duplications, while opisthokonts (eukaryotes) show the opposite (Szöllősi 2013). ALE-rooting of species trees (Williams 2017 PNAS 114:E4602) is now a standard rooting approach for deep archaeal/prokaryote phylogenomics.

## AvP Eukaryotic HGT Phylogenetic Workflow

**Goal:** Detect HGT in eukaryotic proteomes with automated phylogenetic-tree validation.

**Approach:** `avp prepare` builds taxonomic database from candidate hits -> `avp detect` builds gene trees per candidate -> `avp classify` runs AU/SH tests on alternative placements.

```bash
avp prepare -t taxonomy.tsv -d nr.fasta -o database
avp detect -i query_proteome.fasta -d database -o avp_results -threads 8
avp classify -i avp_results -d database --au-test --bootstrap 1000
```

The output `avp_results/classification.tsv` reports per-gene: HGT / putative-HGT / unknown / non-HGT, donor lineage assignment, gene-tree support, and AU-test p-value. **Apply only after FCS-GX or BlobTools contamination filter.**

## IslandViewer 4 + mobileOG-db Integration

For single-genome bacterial analysis, the combined workflow is: IslandViewer 4 (web; submit assembly, returns islands via IslandPath-DIMOB / SIGI-HMM / IslandPick consensus) -> annotate genes with mobileOG-db (Brown 2022 Appl Environ Microbiol 88:e0099122) for mobile element families -> cross-check candidate islands for integrase / transposase / phage signatures -> if AMR is annotated, cross-reference with AMRFinderPlus or CARD.

The five most reliable island indicators in order of strength: (1) integrase / transposase / phage protein co-located; (2) tRNA gene at one boundary (integration hotspot); (3) GC% deviation > 2 SD from genome mean; (4) absence in close relatives; (5) DNA recognition sites for known integrases (e.g. attL/attR).

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| HGTector positive, ALE rejects transfer at any branch | Sequencing artifact, BLAST distribution skewed by uneven taxonomic sampling | Trust ALE (phylogenetic, posterior-based); investigate HGTector's "distal" hit composition |
| Composition positive, phylogeny negative | Native compositional outlier (rRNA region, prophage native to lineage) | Mask known features; treat as native unless mobile-element signature corroborates |
| Composition negative, phylogeny positive (ancient HGT) | Amelioration completed | Trust phylogeny; report transfer age from ALE branch posterior |
| ALE high transfer posterior, RANGER-DTL low | Cost-weight sensitivity in RANGER | Trust ALE (likelihood-based); RANGER costs are user choice |
| Multiple methods positive, but candidate is on low-coverage contig | Contamination | Apply FCS-GX; re-screen post-cleanup |
| AvP positive in eukaryote, but candidate is single-exon, no introns | Contamination (bacterial-origin) or recent bacterial gene without intron acquisition | Inspect contig genome architecture; eukaryote-genomic flanking required |
| HGT signal in tardigrade / human / sponge / Nematoda | Suspect contamination | Re-examine assembly quality; FCS-GX mandatory (Boothby 2015 / Crisp 2015 lessons) |
| Putative HGT in a clade with known hybridization | Reticulate evolution, not HGT | Switch to phylogenetic networks (PhyloNet); D-stat across the clade |
| Donor placement weak (AU p ~ 0.05) | Poor donor sampling or LBA | Add available genomes from candidate donor; switch to CAT-PMSF model |

**Operational rule for publication:** Concordant evidence from 2+ signal classes + contamination-cleared assembly + donor lineage with > 5 sampled relatives + ALE/AvP phylogenetic support with AU p < 0.05 + DGL ruled out by sister-lineage inspection. Single-method (especially composition-only) claims should be downgraded to "candidate" status.

## Cohort Gotchas

- **Genome MAGs from metagenomes:** completeness and contamination matter more than for isolates. Apply CheckM2 first; HGT detection on incomplete MAGs is unreliable.
- **Streptomyces, Borrelia, Mollicutes:** genomes with extreme GC variance or unusual replication; composition methods produce many false positives. Raise z-threshold to 3 and rely more on phylogenetic methods.
- **Endosymbionts (Buchnera, Wolbachia):** strong AT bias from genome reduction; gene from external donor with normal composition appears as HGT but may be ancestral. Use AleRax with reduced-effective-population-size aware priors.
- **Plant genomes:** plastid-to-nucleus EGT is widespread (~5-18% of nuclear plant proteome plastid-derived per Martin 2002 PNAS 99:12246); standard HGT tools detect these but they are not "horizontal" in the prokaryote sense.
- **Animal microbiome-associated organisms:** consortium contamination is common in non-axenic cultures; pre-2010 published "HGTs" in such organisms require FCS-GX re-screening.
- **Single-cell amplified genomes (SAGs):** chimeric MDA artifacts mimic HGT; require co-assembly validation before HGT calls.

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Contamination?" | FCS-GX applied; BlobTools coverage-vs-GC plot showed no contaminant blobs; HGT candidates re-screened post-cleanup |
| "Why is this transfer, not differential gene loss?" | ALE branch-wise event posteriors favor transfer (posterior > 0.5); sister taxa show no trace of gene; loss-only model fits AIC-worse |
| "Why not just composition?" | Amelioration window is ~50-200 Myr (Lawrence-Ochman 1998); for older transfers, phylogenetic methods are required; we report composition only as supporting evidence |
| "How was donor inferred?" | ALE branch transfer posterior > X on donor branch; AU test rejects alternative placements (p < 0.05); >= 5 genomes sampled from donor order |
| "ILS not explanation?" | Tested via Dsuite D-statistic (introgression-detection); not significant; gene-tree incongruence cannot be explained by recent ILS at the divergence depth involved |
| "gBGC?" | W->S substitution bias not elevated; gene is not in high-recombination region; selection scan (positive-selection) is null |
| "Hybridization?" | D-statistic and f4 between candidate donor / recipient pair tested; non-significant; or, if significant, reported as introgression not HGT |
| "Mobile element signature?" | Integrase / transposase co-located OR adjacent tRNA gene OR attL/attR; or, if none, explicitly flagged as composition+phylogeny-only evidence |
| "Why ALE over RANGER?" | ALE provides posterior probabilities; RANGER is parsimony with arbitrary cost weights |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| HGTector "Taxonomy ID X not found" | Outdated `taxdump` | `hgtector database --update`; ensure taxdump is < 6 months old |
| AvP runs but no candidates | Strict default cutoffs | Relax `--alien-index-cutoff` (default 45 -> try 30); inspect intermediate files |
| ALE rejects all gene trees | Gene-tree taxon names don't match species tree | Use orthogroup-consistent species labels; check separator ' \t' not '_' |
| GeneRax MPI hangs | One CPU per tree; thread-count too high | Reduce `--threads` to match cores actually allocated by scheduler |
| AleRax "no parameter convergence" | Too few gene trees or species | Need >= 20 species and >= 100 gene families; convergence is hard for small datasets |
| FCS-GX returns 0 contaminants when external evidence suggests contamination | Reference DB outdated or strain-specific | Update FCS-GX reference; cross-check with BlobTools and Kraken2 |
| IslandViewer returns nothing | Genome < 1 Mb or fragmented | Use stand-alone IslandPath-DIMOB or SIGI on full assembly; manual annotation of small genomes |
| Codon usage CAI all near 1.0 | Reference codon usage from same gene set | Use external highly-expressed-gene reference (ribosomal genes) for CAI scaling |
| RANGER-DTL "transfer cost too low gives transfers everywhere" | Default cost balance | Run with cost-sensitivity sweep (T cost 1-5, L cost 1, D cost 1-2); report robust events only |
| Eukaryotic HGT call from contig < 50 kb | Likely contaminant | Filter for HGT calls on contigs > 100 kb with >= 5 native eukaryote genes flanking |

## Tool Installation Notes

```bash
# HGTector v2
pip install hgtector
hgtector database --output ~/hgtector_db --reference refseq --rank species

# AvP
git clone https://github.com/GDKO/AvP && cd AvP && pip install .
# Requires DIAMOND, IQ-TREE, mafft on PATH

# ALE + GeneRax + AleRax
conda install -c bioconda ale generax
# AleRax: build from source per https://github.com/BenoitMorel/AleRax
git clone --recursive https://github.com/BenoitMorel/AleRax && cd AleRax && ./install.sh

# Contamination tools (REQUIRED for eukaryote HGT)
conda install -c bioconda fcs-gx blobtoolkit kraken2
pip install conterminator

# Mobile elements
git clone https://github.com/clb21565/mobileOG-db
conda install -c bioconda amrfinder
```

NCBI now mandates FCS-GX screening for new eukaryote genome submissions to GenBank (Astashyn 2024 GB 25:60); apply it to any pre-2023 published eukaryote assembly before HGT analysis.

## References

- Lawrence JG & Ochman H 1997 J Mol Evol 44:383 (amelioration concept)
- Lawrence JG & Ochman H 1998 PNAS 95:9413 (amelioration quantification)
- Maddison WP 1997 Syst Biol 46:523 (gene tree species tree discordance causes)
- Felsenstein J 1978 Syst Zool 27:401 (LBA)
- Galtier N & Duret L 2007 Trends Genet 23:273 (gBGC review)
- Vernikos GS & Parkhill J 2006 Bioinformatics 22:2196 (AlienHunter)
- Waack S et al 2006 BMC Bioinf 7:142 (SIGI-HMM)
- Podell S & Gaasterland T 2007 Genome Biol 8:R16 (DarkHorse)
- Gladyshev EA et al 2008 Science 320:1210 (Alien Index; bdelloid rotifer HGT)
- Szöllősi GJ et al 2013 Syst Biol 62:901 (ALE undated)
- Bansal MS et al 2018 Bioinformatics 34:3214 (RANGER-DTL 2.0)
- Bertelli C et al 2017 NAR 45:W30 (IslandViewer 4)
- Williams TA et al 2017 PNAS 114:E4602 (ALE rooting of the archaeal tree of life)
- Boothby TC et al 2015 PNAS 112:15976 (tardigrade HGT claim)
- Koutsovoulos G et al 2016 PNAS 113:5053 (tardigrade contamination refutation)
- Crisp A et al 2015 Genome Biol 16:50 (human HGT claim)
- Salzberg SL 2017 Genome Biol 18:85 (human HGT contamination refutation)
- Zhu Q, Kosoy M & Dittmar K 2014 BMC Genomics 15:717 (HGTector)
- Koutsovoulos G et al 2022 PLoS Comp Biol 18:e1010686 (AvP)
- Yuan L et al 2023 Brief Bioinform 24:bbad035 (HGTphyloDetect)
- Morel B et al 2020 MBE 37:2763 (GeneRax)
- Morel B et al 2024 Bioinformatics 40:btae162 (AleRax co-estimation)
- Brown CL et al 2022 Appl Environ Microbiol 88:e0099122 (mobileOG-db)
- Song W et al 2019 Microbiome 7:36 (MetaCHIP)
- Astashyn A et al 2024 GB 25:60 (FCS-GX)
- Wood DE et al 2019 GB 20:257 (Kraken2)
- Steinegger M et al 2020 GB 21:115 (Conterminator)
- Challis R et al 2020 G3 10:1361 (BlobTools2)
- Ravenhall M et al 2015 PLoS Comp Biol 11:e1004095 (HGT inference review)
- Martin W et al 2002 PNAS 99:12246 (plastid EGT)
- Capra JA et al 2013 PLoS Genet 9:e1003684 (gBGC quantification)
- Solis-Lemus C & Ane C 2016 PLoS Genet 12:e1005896 (SNaQ / PhyloNetworks reticulation)
- Shimodaira H 2002 Syst Biol 51:492 (AU test)

## Related Skills

- comparative-genomics/gene-tree-species-tree-reconciliation - Deep DTL methodology (ALE / GeneRax / AleRax)
- comparative-genomics/ortholog-inference - Orthogroup construction for ALE input
- comparative-genomics/introgression-detection - Distinguish HGT from hybridization via D-statistic
- comparative-genomics/genome-distance-and-species-delineation - ANI / dDDH for donor-recipient distance
- comparative-genomics/pangenome-analysis - Bacterial pangenome assembly for accessory-gene HGT analysis
- phylogenetics/modern-tree-inference - Gene-tree inference with UFBoot for ALE
- phylogenetics/bayesian-inference - PhyloBayes-MPI CAT-GTR for deep-node LBA mitigation
- alignment/multiple-alignment - Codon-aware alignment for compositional analyses
- metagenomics/amr-detection - Mobile element / resistance gene context for HGT candidates
- genome-annotation/prokaryotic-annotation - Mobile-element annotation alongside gene annotation
<!-- END FILE: comparative-genomics/hgt-detection/SKILL.md -->

## 子目录：comparative-genomics/introgression-detection

<!-- BEGIN FILE: comparative-genomics/introgression-detection/SKILL.md -->
---
name: bio-comparative-genomics-introgression-detection
description: Detect introgression and admixture between species or populations using Dsuite (Malinsky 2021 fast D-statistics), Patterson's D / ABBA-BABA test (Green 2010; Durand 2011), f4-ratio and f-branch statistic (Malinsky 2018), TreeMix (Pickrell & Pritchard 2012), HyDe (Blischak 2018), QuIBL (Edelman 2019), sprime (Browning 2018), Twisst (Martin 2017), PhyloNet (Than 2008) for explicit phylogenetic networks, and qpAdm / qpGraph (Patterson 2012). Distinguish introgression from incomplete lineage sorting (ILS), ancestral structure, ghost-lineage admixture, and rate variation. Use when testing inter-species gene flow, dating admixture events, identifying introgressed segments, building phylogenetic networks for reticulate evolution, or applying the ABBAclustering (Koppetsch-Malinsky-Matschiner 2024) framework for divergent-species gene flow.
tool_type: cli
primary_tool: Dsuite
---

## Version Compatibility

Reference examples tested with: Dsuite 0.5+ (millanek/Dsuite; Malinsky 2021 Mol Ecol Res 21:584; ABBAclustering option from Koppetsch-Malinsky-Matschiner 2024 Syst Biol), HyDe 0.4.3+ (Blischak 2018 Syst Biol 67:821), QuIBL (Edelman 2019 Science 366:594), TreeMix 1.13+ (Pickrell & Pritchard 2012 PLoS Genet 8:e1002967), sprime (Browning 2018 Cell 173:53), Twisst (Martin & Van Belleghem 2017 Genetics 206:429), PhyloNet 3.8.2+ (NakhlehLab/PhyloNet; Than-Ruths-Nakhleh 2008 BMC Bioinf 9:322) and PhyloNetworks 0.16+ (JuliaPhylo/PhyloNetworks; Solis-Lemus, Bastide & Ane 2017 MBE 34:3292), qpAdm / qpGraph (AdmixTools v2.0+; Maier 2023), ADMIXTOOLS2 R wrapper (Maier 2023 eLife 12:e85492), MaCS-like simulators (msprime 1.3+ for testing), bcftools 1.21+, samtools 1.21+, vcftools 0.1.16+, R 4.4+. See upstream Dsuite docs for visualization helpers.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `Dsuite --version`; `treemix --help`; `qpDstat --help` (AdmixTools)
- Python: `pip show msprime hyde`
- R: `packageVersion('admixtools')`

If code throws `Dsuite SETS file format error`, `TreeMix matrix singular`, `qpAdm rotation failed`, these tools share strict input requirements: Dsuite needs a SETS file mapping samples to populations + an outgroup; TreeMix needs allele-frequency matrix; qpAdm needs ind / snp / geno trio (EIGENSTRAT format).

# Introgression and Admixture Detection

**"Has there been gene flow between these species / populations?"** -> Tests for inter-population admixture span site-frequency (ABBA-BABA, f4), tree-topology (Dsuite f-branch, QuIBL, Twisst), explicit-network (PhyloNet), and haplotype-tract (sprime) approaches. The fundamental confounder is **incomplete lineage sorting (ILS)**: under a symmetric tree with no gene flow, the ABBA and BABA patterns occur with equal frequency from ancestral polymorphism. **A significant D-statistic indicates EITHER (a) introgression, OR (b) ancestral structure, OR (c) sampling from a ghost lineage** -- additional evidence is required to distinguish (Green 2010 Science 328:710; Durand 2011 MBE 28:2239; Eriksson & Manica 2012 PNAS 109:13956). For high-confidence claims, combine D-statistic with **f-branch** mapping (assigns admixture to specific branches), Twisst / QuIBL topology-weighting, and TreeMix migration edges.

- CLI: `Dsuite Dtrios` -- standard D-statistic for trios of populations
- CLI: `Dsuite Fbranch` -- assign admixture signal to specific tree branches
- CLI: `treemix -i freq.gz -k 1000 -m 0 -o out` -- migration edges
- CLI: `qpAdm` (AdmixTools) -- rotation-based admixture proportion testing
- R: `admixtools::qpadm()` modern wrapper
- CLI: `HyDe -i sequences -t taxa.txt --hyptest` -- hybridization detection at site level
- CLI: `python QuIBL.py inputfile.txt` (config file with treefile path + parameters) -- topology weighting for ILS vs introgression

## Algorithmic Taxonomy

| Tool / Statistic | Approach | Output | Strength | Fails when |
|------------------|----------|--------|----------|------------|
| Patterson's D / ABBA-BABA (Green 2010 Science 328:710; Durand 2011 MBE 28:2239) | Counts ABBA vs BABA site patterns in fixed tree (((P1, P2), P3), Out) | D = (ABBA - BABA) / (ABBA + BABA) | Standard introgression test; tractable | D > 0 means EITHER admixture OR ancestral structure OR ghost lineage |
| Dsuite Dtrios (Malinsky 2021 Mol Ecol Res 21:584) | Fast D for all population trios | D + jackknife SE + p-value | Scales to many populations; integrated with phylogenetic tree | Inherits ABBA-BABA assumptions; symmetric tree only |
| f4-ratio statistic (Patterson 2012 Genetics 192:1065) | Quartet-based admixture proportion | Admixture proportion alpha | Cleaner than D for inferring admixture amount | Requires correct phylogeny; ILS confound |
| Dsuite Fbranch (Malinsky 2018 Nat Eco Evo 2:1940) | Tree-aware f4-ratio mapping | Branch-specific admixture signal | Best at distinguishing admixture among related lineages | Tree must be reliable; ghost branches not detectable |
| ABBAclustering (Koppetsch-Malinsky-Matschiner 2024 Syst Biol) | Dsuite option for divergent-species gene flow | Cluster-based admixture | Designed for cases where standard ABBA-BABA fails | Newer; specific use case |
| TreeMix (Pickrell & Pritchard 2012 PLoS Genet 8:e1002967) | ML tree with migration edges from drift covariance | Tree + migration edges with weights | Visualizes complex admixture | Migration-edge selection subjective; allele-frequency-based |
| qpAdm (Patterson 2012; AdmixTools v2.0; Maier 2023 eLife 12:e85492) | Tests if target derives from sources via rotation | Pass/fail per source set + admixture proportion | Robust statistical framework; rotation control | Source population sampling critical |
| qpGraph (Patterson 2012) | ML phylogenetic graph with admixture | Best-fit graph with admixture nodes | Quantitative; explicit tree+admixture model | Computationally heavy; manual graph topology design |
| HyDe (Blischak 2018 Syst Biol 67:821) | Site-level hybridization detection | Per-site / per-locus hybrid evidence | Sensitive to recent hybridization | Less specific to ancient admixture |
| QuIBL (Edelman 2019 Science 366:594) | Topology weighting on gene trees | Per-tree-weight relative to alternative | Distinguishes ILS from introgression at locus level | Per-locus inference; cross-validation needed |
| Twisst (Martin & Van Belleghem 2017 Genetics 206:429) | Topology weighting on phylogenetic trees | Tree topology weights per genomic window | Visualize topology variation across genome | Computational cost; tree-window decisions |
| PhyloNetworks (Solis-Lemus, Bastide & Ane 2017 MBE 34:3292; Julia, JuliaPhylo/PhyloNetworks) | SNaQ pseudo-likelihood network inference from gene trees / concordance factors | Explicit reticulation network | Modern Julia ecosystem; SNaQ scales well | Different software than the Java "PhyloNet" |
| PhyloNet (Than-Ruths-Nakhleh 2008 BMC Bioinf 9:322; Java, NakhlehLab/PhyloNet) | ML / MP / Bayesian network inference | Explicit reticulation network | Mature Java tool; many inference modes | Computationally heavy; Maven build |
| sprime (Browning 2018 Cell 173:53) | Per-individual archaic introgression detection | Introgressed haplotype tracts | Designed for archaic-human-like cases | Specific to closely related introgression source |
| Relate (Speidel 2019 Nat Genet 51:1321) | Phasing-aware genome-wide genealogy reconstruction | Coalescence times dating introgression segments | Modern haplotype-aware method; times admixture via tract coalescence | Requires phased data; genealogy timing indirect for admixture |
| F3 statistic (Patterson 2012) | Three-population test for admixture | F3 with SE | Specifically detects admixture (vs negative drift) | F3 < 0 indicates admixture; mixed signals |
| F4-statistic (Patterson 2012) | Four-population test | F4 + p-value | Generalizes D; allows variable outgroup distance | Symmetric assumption |

Methodology evolves; verify the Dsuite documentation and Malinsky 2024 review (eLife) before locking on a single approach. The combination of (1) Dsuite D + Fbranch + (2) Twisst / QuIBL + (3) network method (PhyloNet) is the modern best practice for publication-grade introgression claims.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Test for introgression between two species, outgroup available | Dsuite Dtrios + Fbranch | Standard ABBA-BABA + tree-aware branch mapping |
| Multi-population complex admixture inference | TreeMix + qpAdm | Migration edges + rotation tests |
| Distinguish introgression from ILS | QuIBL + Twisst across many loci | Topology weighting at locus level |
| Date the admixture event | Relate (Speidel 2019) + Twisst window analysis | Genealogy reconstruction + haplotype-length-distribution dating + topology |
| Quantify admixture proportion alpha | f4-ratio (Patterson 2012) or qpAdm | Standard framework |
| Identify introgressed genomic regions | sprime + Twisst | Per-individual + per-window |
| Explicit phylogenetic network | PhyloNet with model selection (DLRS-NL or InferNetwork_MP) | Quantitative reticulation |
| Test for ghost-lineage admixture | qpGraph manual topology + AdmixTools rotation | Compare alternative graphs |
| Recent hybridization | HyDe + per-individual analysis | Site-level hybrid evidence |
| Ancient introgression | Dsuite + qpAdm; Patterson f-statistics for archaic | Tree-aware methods preferred |
| Plant-plant hybridization with parental polyploidy | HyDe + sprime + chromosome-level analysis | Polyploid context |
| Human-archaic introgression (Neanderthal, Denisovan) | sprime + qpAdm + ChromoPainter | Sample-specific haplotype analysis |
| Cichlid radiation | Dsuite + TreeMix + QuIBL (Malinsky 2018 Nat Eco Evo 2:1940) | Established workflow |
| Drosophila species group | Dsuite + Twisst + qpAdm | Standard workflow |
| Genomic regions of introgression vs vertical inheritance | Twisst per-window + chromosome painting | Visualization of variation across genome |
| Test for introgression direction (P1 -> P2 vs P2 -> P1) | qpAdm rotation; Twisst directionality from phasing | qpAdm handles direction better than D |
| Symmetric phylogeny violation (no clear outgroup) | f3 statistic + qpGraph topology | Avoid D-statistic if outgroup unclear |
| Suspect ABBA-BABA ILS-confounded | Switch to QuIBL or Twisst for locus-level discrimination | These distinguish ILS from introgression |

## Per-Method Failure Modes

### ILS confounded with introgression in D-statistic

**Trigger:** D-statistic significantly different from zero for a population trio.

**Mechanism:** Under symmetric phylogeny with no gene flow, ABBA and BABA patterns occur with equal frequency from ancestral polymorphism (ILS). Random allele sorting in descendant lineages produces the same site patterns as introgression. D > 0 is therefore consistent with introgression OR with asymmetric ILS OR with ancestral structure (Eriksson & Manica 2012 PNAS 109:13956).

**Symptom:** Many tested trios show D > 0 with low effect size; Twisst / QuIBL on the same loci shows mixed topologies; phylogenetic distance to outgroup is large.

**Fix:** Use Dsuite f-branch (Malinsky 2018) to assign admixture to specific branches; verify with QuIBL or Twisst topology weighting at the locus level. ABBAclustering (Koppetsch-Malinsky-Matschiner 2024) specifically handles divergent-species gene flow.

### Ghost lineage admixture mimicking signal

**Trigger:** Inferring P1 -> P2 admixture without considering that the admixed lineage could come from an unsampled extinct sister to P3.

**Mechanism:** D > 0 with P3 as donor is identical to D > 0 with a ghost sister of P3 as donor. The data cannot distinguish without explicit modeling.

**Symptom:** Hypothesized donor population doesn't match expected geography or ecology; qpGraph cannot fit a parsimonious admixture model without invoking ghost lineages.

**Fix:** Build qpGraph with potential ghost lineages explicitly; report multiple compatible scenarios; consult known paleontology / biogeography to constrain possibilities. The Neanderthal-Denisovan-anatomically-modern-human framework is heavily ghost-lineage-aware (Slon 2018; Mafessoni 2020).

### Ancestral structure (population subdivision before admixture)

**Trigger:** Significant D-statistic in a recently diverged radiation.

**Mechanism:** Ancestral subdivision in the ancestor of (P1, P2, P3) produces D > 0 from biased ancestral allele inheritance, not from gene flow between descendants.

**Symptom:** D positive across multiple trios but pattern not consistent with simple admixture; effect size differs from f-statistic predictions; rapid radiation context.

**Fix:** Examine F-statistics framework (f3, f4); use qpGraph with structured ancestry; consider PhyloNet for explicit reticulate model. Eriksson & Manica 2012 PNAS 109:13956 documents this confound.

### Outgroup-distance effect on D-statistic

**Trigger:** Using a distantly related outgroup (>200 Myr) for the D-test.

**Mechanism:** Long branches to the outgroup accumulate convergent substitutions; some sites called ABBA / BABA are actually convergent across branches, not true ABBA / BABA patterns.

**Symptom:** D-statistic at convergent-evolution-prone sites is elevated; D varies with outgroup choice.

**Fix:** Use a closer outgroup (< 100 Myr); avoid extremely deep outgroups. Mask sites with extreme conservation across the four taxa. Standard practice in animal species groups uses Drosophila simulans / yakuba for D. melanogaster trios.

### Sample-size bias in D-statistic

**Trigger:** P1 and P2 have very different sample sizes (e.g. 1 vs 50).

**Mechanism:** Allele frequencies in small samples are more extreme; counting ABBA/BABA across genome is dominated by the population with larger sample.

**Symptom:** D-statistic dominated by the larger-sample population; jackknife SE underestimated.

**Fix:** Use one individual per population (Dsuite default for Dtrios); or downsample to consistent N; report effective per-population sample size.

### TreeMix migration-edge selection

**Trigger:** Choosing number of migration edges via likelihood ratio or AIC alone.

**Mechanism:** TreeMix likelihood increases with each migration edge added (more parameters); the "right" number requires statistical justification, but published criteria vary.

**Symptom:** Different selection criteria yield different optimal migration edge counts; results sensitive to k-block size (in jackknife).

**Fix:** Use OptM (Fitak 2021 Biol Methods Protoc 6:bpab017) for principled migration-edge selection; report cross-validation across k-block sizes. Combine with qpAdm rotation tests as independent corroboration.

### qpAdm rotation failures

**Trigger:** qpAdm reporting "rotation rejected" for proposed source population set.

**Mechanism:** qpAdm tests whether target population can be modeled as admixture of source populations; rotation tests check that swapping sources for the outgroup set doesn't break the model. Rotation failure means the proposed sources don't capture the actual admixture.

**Symptom:** qpAdm fits with feasible-sounding sources, but rotation indicates poor fit; admixture proportions sum to weird values.

**Fix:** Reconsider source populations; include "right" populations representing ancestral structures; document rotation results. AdmixTools v2.0 (Maier 2023) provides better diagnostics.

### Multiple-testing correction across population trios

**Trigger:** Running Dsuite Dtrios across all population trios genome-wide and reporting significant ones.

**Mechanism:** With N populations, there are N choose 4 quartets to test; with 50 populations, ~1.5M tests. Naive 5% Type-I gives 75,000 false positives.

**Symptom:** Many "significant" trios reported but with low effect sizes; biological interpretation impossible.

**Fix:** Apply FDR correction across trios; or restrict to a priori hypothesized trios. Dsuite computes Bonferroni-corrected p-values via `-c` flag.

### Genomic-window choice in Twisst / QuIBL

**Trigger:** Running Twisst on 50 kb windows vs 100 kb windows giving different results.

**Mechanism:** Smaller windows have more topology stochasticity; larger windows average across recombination events. The "correct" window depends on local recombination rate.

**Symptom:** Twisst conclusions reverse with window size; spatial pattern of introgression unstable.

**Fix:** Choose windows matching local LD decay (typically 10-100 kb for vertebrates; 5-20 kb for Drosophila). Report sensitivity to window choice. Combine with Twisst-explore.py for spatial visualization.

### Phylogenetic network not unique

**Trigger:** PhyloNet inferring different reticulation networks with similar likelihood.

**Mechanism:** Phylogenetic networks are non-unique; multiple networks can have similar likelihoods. PhyloNet's MP / ML criterion doesn't disambiguate beyond a tolerance.

**Symptom:** PhyloNet returns several networks within delta-LRT = 5; biological interpretation differs.

**Fix:** Report top-N networks; combine with f-statistics (qpAdm / qpGraph) as independent confirmation; use biological knowledge (geography, ecology) to constrain.

### sprime contamination from non-archaic introgression source

**Trigger:** sprime applied to populations with both ancient and recent admixture sources.

**Mechanism:** sprime detects archaic-like haplotypes by comparing to outgroup; haplotype tracts from any non-outgroup-resembling source produce false positives.

**Symptom:** sprime calls many haplotype tracts in populations with known recent introgression that's not from the "archaic" target.

**Fix:** Use sprime only when sources are well-characterized; cross-validate with paired analysis using known archaic vs known recent sources separately.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Patterson's D significance | jackknife z-score |z| > 3 (Bonferroni-corrected) | Green 2010; standard |
| D-statistic interpretation | |D| > 0 with sig z is admixture OR ILS OR ghost | Green 2010 caveat |
| f4-ratio admixture proportion | 0 <= alpha <= 1 | Patterson 2012 |
| Dsuite Fbranch significance | jackknife z > 3 per branch | Malinsky 2018 |
| TreeMix migration weight | typically 0.05-0.30 for biologically relevant | Pickrell 2012 |
| TreeMix k-block size | 500-1000 SNPs default | Empirical |
| qpAdm sources passing rotation | rotation-corrected p > 0.05 | Patterson 2012; Maier 2023 |
| qpAdm admixture proportion | 0 <= alpha <= 1 with SE | Standard |
| QuIBL trio test | best-trio topology weight > 0.5 + significant z | Edelman 2019 |
| Twisst window size | 10-100 kb (vertebrate); 5-20 kb (Drosophila) | Empirical |
| Per-window Twisst topology weight | dominant topology > 50% | Standard |
| HyDe per-individual significance | LRT p < 0.05 vs no-hybridization | Blischak 2018 |
| sprime archaic haplotype length | > 50 kb typical archaic; < 20 kb questionable | Browning 2018 |
| Sample size per population (Dsuite) | 1+ (defaults to one per pop); 5+ preferred | Empirical |
| Outgroup distance for D-stat | < 100 Myr (close); 50-200 Myr (typical) | Empirical |
| FDR threshold across trios | q < 0.05 (BH) | Standard |
| Bonferroni for N choose 4 trios | adjust per number tested | Standard |
| f3 statistic for admixture | f3 < 0 indicates admixture | Patterson 2012 |
| ABBAclustering threshold | depends on clustering algorithm | Koppetsch 2024 |
| Phylogenetic network tolerance | delta-LRT < 2-5 for "similar" | Standard |

## Dsuite Standard Workflow

**Goal:** Compute Patterson's D and Fbranch across all population trios from a VCF.

**Approach:** Prepare SETS file mapping samples to populations -> Dsuite Dtrios -> Dsuite Fbranch -> visualize.

```bash
# 1. Prepare SETS file (samples to populations)
cat > SETS.tsv << 'EOF'
sample_id    population
A1           Population_A
A2           Population_A
B1           Population_B
B2           Population_B
C1           Population_C
D1           Outgroup
EOF

# 2. Run Dsuite Dtrios
# Real CLI flags (verify with `Dsuite Dtrios --help` against installed version):
#   -t/--tree=FILE      species tree (Newick)
#   -o/--out-prefix=    output prefix
#   -k/--no-f4-ratio    skip f4-ratio computation
#   -c/--no-combine     do not write the _combine.txt file
# Fbranch is its own subcommand (`Dsuite Fbranch`); no Dtrios flag toggles it.
Dsuite Dtrios \
    --tree=species_tree.nwk \
    -o trios_run \
    population_genotypes.vcf.gz \
    SETS.tsv

# Output: trios_run_BBAA.txt, trios_run_Dmin.txt, trios_run_tree.txt, trios_run_combine.txt

# 3. Run Fbranch for tree-aware admixture mapping
Dsuite Fbranch species_tree.nwk trios_run_tree.txt > trios_run_fbranch.txt

# 4. ABBAclustering test (Koppetsch-Malinsky-Matschiner 2024).
# Implementation specifics depend on the Dsuite branch / fork distributing the ABBAclustering option;
# consult the Koppetsch 2024 supplement and `Dsuite --help` for current invocation. The option may
# be exposed as a subcommand or per-trio flag rather than a global Dtrios switch.
```

```python
'''Parse Dsuite output for per-trio admixture signal.'''
import pandas as pd


def load_dsuite_trios(path):
    '''SETS.tsv_BBAA.txt columns: P1, P2, P3, D, p-value, Z, BBAA, ABBA, BABA, f_d, f_dM, df, ...'''
    df = pd.read_csv(path, sep='\t')
    df['admixture_signal'] = (df['Z'] > 3) & (df['p_value'] < 0.05)
    return df


def filter_top_admixture(df, by='Z', top=20):
    return df.sort_values(by, ascending=False).head(top)
```

## TreeMix for Population Tree with Migration Edges

**Goal:** Build a population tree with migration edges showing admixture.

**Approach:** Convert VCF to allele-frequency matrix -> run TreeMix -> select migration count via OptM.

```bash
# 1. Convert VCF to TreeMix input
python tree_mix_input.py --vcf population.vcf.gz --popmap popmap.tsv \
    --output input.frq.gz

# 2. Run TreeMix
treemix -i input.frq.gz -m 0 -bootstrap -k 1000 -o output_m0
for m in 1 2 3 4 5; do
    treemix -i input.frq.gz -m $m -bootstrap -k 1000 -o output_m${m}
done

# 3. Select optimal m via OptM (R)
Rscript -e "
library(OptM)
# optM(folder, method, ...): folder is the TreeMix output directory (not the input frq.gz).
# Accepts method='Evanno' (delta-m), 'linear', or 'SiZer'. See ?OptM::optM for details.
optM_result <- optM(folder='.', method='Evanno', tsv=NULL)
"
```

## QuIBL for Locus-Level ILS vs Introgression

**Goal:** Distinguish ILS from introgression at the locus level via topology weighting.

**Approach:** Build per-locus phylogenetic trees -> QuIBL on tree list.

```bash
# Build per-locus gene trees
for region in regions/*.fa; do
    iqtree2 -s $region -m GTR+G -B 1000 -nt 2 --prefix gene_trees/$(basename $region .fa)
done

# Combine into tree list
cat gene_trees/*.treefile > combined_trees.txt

# Run QuIBL: input is a config file pointing at the tree list + parameters
cat > quibl_input.txt << 'EOF'
treefile: combined_trees.txt
outputfile: quibl_results.txt
likelihoodthresh: 0.01
gradascentscalar: 0.5
totaloutgroup: outgroup_taxon
overallnumlambda: 2
EOF
python QuIBL.py quibl_input.txt
```

## qpAdm Rotation Test

**Goal:** Test if target population is admixed from candidate sources.

**Approach:** Define source set + outgroups; AdmixTools qpAdm rotation tests source population set.

```bash
# AdmixTools formatted input: ind / snp / geno (EIGENSTRAT)
# Or use admixtools R wrapper

# In R:
Rscript -e "
library(admixtools)
# Setup left (sources) + right (outgroups)
left <- c('SourceA', 'SourceB')
right <- c('Outgroup1', 'Outgroup2', 'Outgroup3')
target <- 'AdmixedPop'

results <- qpadm(prefix='eigenstrat_data', target=target,
                 left=left, right=right)
results$rankdrop  # rotation test rejection
results$weights   # admixture proportions
"
```

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| D-statistic significant, Twisst dominant topology supports species tree | ILS confound | Trust Twisst; D was ILS-driven |
| D significant, Fbranch attributes to specific branch | True introgression | Confirmed admixture |
| qpAdm fails rotation; TreeMix doesn't show migration edge | Inconsistent admixture scenarios; insufficient data | Reconsider sources; report exploratory |
| QuIBL supports introgression, D-statistic null | D-statistic underpowered or sample-size biased | Trust QuIBL locus-level |
| TreeMix migration edge with TreeMix likelihood gain only with high m | Overfitting | Use OptM; restrict to robust edges |
| PhyloNet network is non-unique | Multiple valid reticulation models | Report all; use prior knowledge to constrain |
| sprime calls many tracts in non-archaic-source population | False positive from non-archaic | Restrict sprime to populations with known archaic source |
| HyDe site-level signal at conserved genes | Convergent evolution masquerading as hybridization | Filter conserved sites; verify with non-coding regions |
| D-statistic stable; Fbranch shows nothing | All admixture attributable to a single ghost branch | Ghost-lineage candidate |

**Operational rule for publication:** Patterson D + Fbranch + Twisst/QuIBL window-level + at least one network method (PhyloNet or qpGraph) agreeing on admixture; multiple-testing correction across trios; ILS quantified via Twisst or coalescent simulation; explicit acknowledgement of ghost-lineage / ancestral-structure alternatives.

## Cohort Gotchas

- **Recent radiations:** ILS confounded with introgression; require additional evidence beyond D-statistic
- **Hybridization vs introgression:** hybridization is contemporary; introgression is ancestral admixture
- **Plant polyploids:** subgenome assignment first; cross-subgenome "introgression" is typically homeologous
- **Reduced-genome organisms:** low marker density; ABBA-BABA underpowered
- **Sex chromosomes:** non-recombining; restrict introgression tests to autosomal data
- **Distantly related introgression source (>200 Myr):** sample more carefully; convergent substitutions confounding
- **Cytonuclear discordance:** mtDNA introgression may differ from autosomal; report separately
- **Migration vs introgression:** D-statistic detects allele introgression; demographic models needed for migration history
- **Rapid radiation example:** cichlids (Malinsky 2018 Nat Eco Evo 2:1940); standard workflow documented

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "ILS vs introgression?" | Multi-method approach: D + Fbranch + Twisst + QuIBL; ILS-confounded loci identified |
| "Ghost lineage?" | qpGraph models tested with potential ghost lineages; biological context constrains; report alternatives |
| "Ancestral structure?" | qpAdm rotation rules out simple admixture from sampled sources; Eriksson & Manica 2012 alternative explicitly considered |
| "Outgroup choice?" | Outgroup distance reported; sensitivity tested with multiple outgroups |
| "Multiple-testing correction?" | FDR across population trios; or restricted to a priori hypothesized |
| "TreeMix migration count?" | OptM Evanno method; cross-validated across k-block sizes |
| "qpAdm sources?" | Rotation tests passed; multiple alternative source sets evaluated |
| "Twisst window size?" | Matched local LD decay; sensitivity tested |
| "Direction of introgression?" | qpAdm directional + Twisst phasing data |
| "Date of admixture?" | Relate genealogy + tract-length-distribution-based dating; CIs reported |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Dsuite SETS file empty | Missing samples in VCF | Verify VCF + SETS sample names |
| TreeMix matrix singular | Insufficient SNPs or perfect collinearity | Increase k-block size; remove duplicates |
| qpDstat AdmixTools fails | EIGENSTRAT format issue | Re-convert with convertf |
| HyDe per-individual no result | Default thresholds too strict | Relax --signal threshold |
| QuIBL slow | Many trees | Parallelize; reduce per-tree size |
| Twisst output empty | Window-tree mismatch | Verify gene trees for each window |
| PhyloNet OOM | Many taxa; network complexity | Reduce taxon set; restrict to candidate reticulations |
| sprime no haplotypes | Phasing or outgroup issue | Verify input phased; check outgroup |
| D-statistic sign confused | Allele orientation issue | Use derived alleles consistently |
| qpAdm convergence failure | Source overlap or rare alleles | Filter MAF > 0.05; check source overlap |

## Tool Installation Notes

```bash
# Dsuite
git clone https://github.com/millanek/Dsuite && cd Dsuite && make
# Or: conda install -c bioconda dsuite

# TreeMix
conda install -c bioconda treemix

# AdmixTools (qpDstat, qpAdm, qpGraph)
git clone https://github.com/DReichLab/AdmixTools && cd AdmixTools && make

# Modern AdmixTools v2 (R)
remotes::install_github('uqrmaie1/admixtools')

# HyDe
git clone https://github.com/pblischak/HyDe && cd HyDe && pip install -e .

# QuIBL
git clone https://github.com/miriamtnzr/QuIBL

# Twisst
git clone https://github.com/simonhmartin/twisst && pip install -e .

# PhyloNet
git clone https://github.com/NakhlehLab/PhyloNet && cd PhyloNet && mvn package

# sprime
conda install -c bioconda sprime
```

For population-genetic analyses, the Dsuite + AdmixTools v2 (R) + TreeMix combination is standard. PhyloNet is heavier and requires Maven build.

## References

- Green RE et al 2010 Science 328:710 (Patterson D / ABBA-BABA, Neanderthal admixture)
- Durand EY et al 2011 MBE 28:2239 (D-statistic theoretical framework)
- Patterson N et al 2012 Genetics 192:1065 (f-statistics framework)
- Maier R et al 2023 eLife 12:e85492 (AdmixTools v2 / admixtools R)
- Pickrell JK & Pritchard JK 2012 PLoS Genet 8:e1002967 (TreeMix)
- Malinsky M et al 2021 Mol Ecol Resources 21:584 (Dsuite)
- Malinsky M et al 2018 Nat Eco Evo 2:1940 (f-branch statistic; Lake Malawi cichlid radiation)
- Koppetsch T et al 2024 Syst Biol (ABBAclustering)
- Edelman NB et al 2019 Science 366:594 (QuIBL)
- Martin SH & Van Belleghem SM 2017 Genetics 206:429 (Twisst)
- Blischak PD, Chifman J, Wolfe AD & Kubatko LS 2018 Syst Biol 67:821 (HyDe)
- Solis-Lemus C, Bastide P & Ane C 2017 MBE 34:3292 (PhyloNetworks / SNaQ)
- Than C, Ruths D & Nakhleh L 2008 BMC Bioinf 9:322 (PhyloNet)
- Browning SR et al 2018 Cell 173:53 (sprime archaic introgression)
- Eriksson A & Manica A 2012 PNAS 109:13956 (ancestral structure produces D-stat without admixture); Soraggi S et al 2018 G3 8:551 (D-statistic with low-coverage data)
- Slon V et al 2018 Nature 561:113 (Denisovan-Neanderthal hybrid)
- Mafessoni F et al 2020 PNAS 117:15132 (high-coverage Chagyrskaya Neanderthal genome)
- Speidel L et al 2019 Nat Genet 51:1321 (Relate genealogy)
- Fitak RR 2021 Biol Methods Protoc 6:bpab017 (OptM)
- Lawson DJ et al 2012 PLoS Genet 8:e1002453 (ChromoPainter; haplotype-based admixture)
- Patin E et al 2017 Science 356:543 (sub-Saharan admixture example)
- Frantz LAF et al 2019 PNAS 116:17231 (animal domestication admixture)

## Related Skills

- comparative-genomics/hgt-detection - Distinguish HGT from hybridization in microbes
- comparative-genomics/gene-tree-species-tree-reconciliation - Reconciliation alternative for introgression
- comparative-genomics/synteny-analysis - Per-window topology analysis
- population-genetics/population-structure - PCA / ADMIXTURE precedes introgression testing
- population-genetics/selection-statistics - Selection on introgressed regions
- population-genetics/linkage-disequilibrium - LD haplotype context for sprime
- phylogenetics/modern-tree-inference - Gene-tree inference for QuIBL / Twisst
- phylogenetics/species-trees - Coalescent species tree under ILS
- causal-genomics/heritability-partitioning - Inheritance partitioning by genomic region
- variant-calling/joint-calling - Multi-sample VCF for introgression analysis
- read-alignment/bwa-alignment - Alignment underlies variant calling for D-statistic
<!-- END FILE: comparative-genomics/introgression-detection/SKILL.md -->

## 子目录：comparative-genomics/ortholog-inference

<!-- BEGIN FILE: comparative-genomics/ortholog-inference/SKILL.md -->
---
name: bio-comparative-genomics-ortholog-inference
description: Infer orthologous genes and gene families across species using OrthoFinder3 (HOG-based phylogenetic orthology), SonicParanoid2, Broccoli, ProteinOrtho, OMA / FastOMA hierarchical orthologous groups, eggNOG-mapper, JustOrthologs, and TOGA whole-genome-alignment orthology. Use when building single-copy ortholog sets for phylogenomics, classifying co-orthologs and in/out-paralogs after gene duplication, propagating functional annotation via orthology with awareness of the ortholog conjecture, distinguishing speciation from duplication via gene-tree species-tree reconciliation, computing Quest-for-Orthologs benchmark performance, or running synteny-aware ortholog detection in WGD-affected lineages.
tool_type: mixed
primary_tool: OrthoFinder
---

## Version Compatibility

Reference examples tested with: OrthoFinder 3.0+ (Emms et al 2026 Nat Methods 23:1327), SonicParanoid 2.0.8+ (Cosentino 2024), Broccoli 1.2+ (Derelle 2020), ProteinOrtho 6.3.0+ (Lechner 2011 + recent), OMA standalone 2.6.0+, FastOMA 0.3.5+ (Majidian 2025), eggNOG-mapper 2.1.12+, JustOrthologs 2.0+, DIAMOND 2.1.10+, MMseqs2 17-b804f+, IQ-TREE 2.3.6+, BUSCO 5.7+, Compleasm 0.2.7+, BioPython 1.84+, R 4.4+ for downstream tree-based reconciliation.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `orthofinder --help`; `sonicparanoid --help`; `oma --help`
- Python: `pip show eggnog-mapper`; `which fastoma`

If code throws `Diamond requires N more sequences than provided`, `KeyError on species tree taxa`, `STAG branch length 0`, or `HOG file format mismatch`, the OrthoFinder v2 -> v3 file layout changed (Orthogroups/ -> Phylogenetic_Hierarchical_Orthogroups/; rooted gene trees are now per-HOG); update parsing accordingly.

# Ortholog Inference

**"Find the orthologs of my gene(s) across these species"** -> Choose between graph-based (RBH / similarity-clustering: fast, lower recall) and tree-based (gene-tree reconciliation: higher accuracy, slower) frameworks; recognize that "orthology" splits into 1:1, 1:many, many:many, and the practical unit for most pipelines is the **HOG (Hierarchical Orthologous Group)** -- a maximal cluster of genes descended from a single ancestral gene at a defined taxonomic level (Altenhoff 2013 PLoS ONE 8:e53786). The "ortholog conjecture" (orthologs more functionally similar than paralogs) is supported but weakly (Altenhoff 2012 PLoS Comp Biol 8:e1002514); don't treat 1:1 ortholog labeling as automatic functional equivalence.

- CLI: `orthofinder -f proteomes/ -t 16 -M msa` -- HOG output in v3 layout
- CLI: `sonicparanoid -i proteomes/ -o output --mode default` -- ML predictor + protein language model
- CLI: `broccoli.py -dir proteomes/ -threads 16` -- direct OG with chimeric handling
- CLI: `oma standalone` HOG inference at every taxonomic level
- CLI: `proteinortho6.pl --project=run proteomes/*.faa` -- graph clustering with optional synteny
- CLI: `emapper.py -i proteins.faa --output project --cpu 16` -- eggNOG annotation transfer

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| OrthoFinder3 (Emms et al 2026 Nat Methods) | DIAMOND2-ultra search -> gene trees -> rooted via STRIDE -> HOG inference at every node | HOGs at every taxonomic level, orthologs, species tree, gene-duplication events | Best Quest-for-Orthologs benchmark (Altenhoff 2024); HOGs are ~7% more accurate than v2 orthogroups (5-7% higher f-score); outgroup inclusion further improves accuracy | Slow with > 200 species without `-c 1` clustering pre-step; new file layout breaks old parsers |
| SonicParanoid2 (Cosentino 2024 GB 25:195) | RBH + ML classifier with protein language model embeddings | Pairwise orthologs + orthogroups | Best accuracy among graph methods at competitive speed; ML correction reduces InParanoid errors | InParanoid lineage still has paralogy confusion in WGD clades; close-relative duplications hard to resolve |
| Broccoli (Derelle 2020 MBE 37:3389) | k-mer similarity -> directed graph -> chimera-aware OG inference | OGs + chimera flagging | Robust to chimeric assemblies; runs without species tree | Less accurate than OrthoFinder on benchmark; no HOG output |
| ProteinOrtho 6 (Lechner 2011 BMC Bioinf 12:124) | Pairwise BLAST/DIAMOND + connectivity graph; optional synteny module | Orthogroups + synteny option | Fast; scales to 1000+ genomes; `-synteny` enables co-linear-anchor filtering | Lower recall than tree-based; synteny module slow and requires GFFs |
| OMA standalone (Altenhoff 2019 GR 29:1152) | Strict RBH + verification + HOG inference | HOG database; orthologs at each taxonomic level | Conservative; highest precision in QfO benchmarks; "Fast" mode for prefiltering | Lowest recall among methods (Altenhoff 2024); slow for large datasets |
| FastOMA (Majidian 2025 Nat Methods 22:269) | OMA HOG inference with GPU-accelerated DIAMOND + Roothap | Same HOG output as OMA, 10-100x faster | Scales OMA to 1000+ genomes | Newer; less benchmarked in production |
| eggNOG-mapper 2 (Cantalapiedra 2021 MBE 38:5825) | DIAMOND/MMseqs2 against eggNOG 5 -> map to precomputed orthogroups | OGs + functional annotation (GO/KEGG/COG) | Standard for functional annotation propagation; phylogeny-aware | Pre-computed OGs; cannot add novel species coherently; only as fresh as eggNOG release |
| JustOrthologs (Miller 2019 Bioinformatics 35:546) | DNA-based; exon-aware; close-species RBH | Pairwise orthologs | Extremely fast for closely related species (same family); preserves splice variants | Only suitable for closely related species |
| TOGA (Kirilenko 2023 Science 380:eabn3107) | Whole-genome-alignment chain -> ML projection + intactness classification | Per-query orthologs with intact/lost/missing call | Modern paradigm for vertebrate-scale orthology; handles gene loss explicitly; integrates with CESAR 2.0 | Requires WGA (Cactus); not designed for prokaryotes or fungi |
| HOGENOM / HOGsuite (Penel 2009 BMC Bioinf 10:S3) | Tree-based HOGs in databases | Pre-computed HOG database | Legacy; for downstream use of stored HOGs | Not for new computation; outdated taxon sampling |

Methodology evolves; Quest-for-Orthologs benchmarks (Altenhoff 2024 NAR Genom Bioinform 6:lqae167) refresh annually. Verify the current QfO benchmark results before locking on a single tool for novel benchmarking-grade work.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| 5-50 vertebrate / animal genomes for phylogenomics | OrthoFinder3 `-M msa -A mafft -T iqtree` | HOG quality at moderate scale; species tree included |
| 50-200 genomes, any clade | OrthoFinder3 default; SonicParanoid2 as second method | Cross-validate consensus HOGs |
| 200-1000 genomes, scaling required | FastOMA or SonicParanoid2 | OrthoFinder3 slow; cluster-first option (`-c 1`) helps |
| 1000+ bacterial genomes (pangenome scope) | Use [[pangenome-analysis]] pipeline; OrthoFinder unsuitable | Pangenome-specific tools needed |
| Closely related strains / same family | JustOrthologs or ProteinOrtho with synteny | Fast; preserves splice variants |
| WGD-affected lineage (plants, salmonids, teleosts) | OrthoFinder3 + synteny verification (see [[synteny-analysis]]); or GENESPACE | WGD inflates paralogy; synteny anchoring required |
| Functional annotation transfer | eggNOG-mapper 2 | Pre-computed; phylogeny-aware; integrates GO/KEGG |
| Single-copy orthologs for concatenation phylogenomics | OrthoFinder3 `Phylogenetic_Hierarchical_Orthogroups/N0.tsv` filter for 1:1 | Most rigorous HOG layer; standard concatenation input |
| Gene-loss detection across mammals/birds at scale | TOGA + CESAR 2.0 | Explicit intact/lost classification; handles assembly-gap noise |
| Functional annotation transfer in poorly characterized genome | eggNOG-mapper + OrthoFinder3 single-copy orthologs cross-validated | Functional priors + phylogenetic confidence |
| Ortholog detection in highly fragmented assembly | BUSCO/Compleasm first to assess completeness; flag affected OGs | Assembly fragmentation creates false absence -> spurious lineage-specific losses |
| Distant homolog detection (50-200 Myr divergence) | MMseqs2 sensitive (`-s 7.5`) + OrthoFinder3 | Default DIAMOND misses distant homologs; sensitive search needed |
| Phylogenetic orthology with paralog-tolerant species trees | ASTRAL-Pro2 on OrthoFinder gene trees | Coalescent species tree from gene trees; handles paralogy explicitly |
| HOG-level functional propagation across many species | OMA standalone HOG database | Strict hierarchical orthology; supports functional propagation per taxonomic level |
| Synteny-anchored orthology in repeat-heavy genome | ProteinOrtho `-synteny` or GENESPACE | Filters tandem duplicates; uses gene order to disambiguate paralogs |

## Per-Method Failure Modes

### Hidden paralogy from missing outgroup

**Trigger:** OrthoFinder run without a sufficiently distant outgroup; only ingroup taxa included.

**Mechanism:** OrthoFinder roots gene trees via STRIDE / STAG using outgroup-based duplication signals. Without an outgroup, the root inferred for each gene tree may be internal, mistakenly classifying a duplication-then-loss pattern as orthology. The "1:1 orthologs" returned may actually be hidden paralogs (Emms & Kelly 2017 MBE 34:3267 STRIDE).

**Symptom:** Phylogenomic concatenation produces low-bootstrap species tree; per-gene trees show inconsistent rooting; same-clade species show longer-than-expected branches in single-copy ortholog trees.

**Fix:** Include >= 1 outgroup taxon at the next-higher taxonomic level (sister phylum / class / order). For vertebrates, use cyclostomes (lamprey) as outgroup for jawed vertebrates; for plants, use a non-flowering plant for angiosperms. Re-run with outgroup; cross-check HOG file `Phylogenetic_Hierarchical_Orthogroups/N0.tsv` for 1:1 stability.

### Splice isoforms inflating copy number

**Trigger:** Proteome FASTA contains multiple isoforms per gene (Ensembl, RefSeq with `-NR` flag).

**Mechanism:** OrthoFinder / SonicParanoid / OMA treat each protein sequence as a gene; isoforms are clustered together within orthogroups but inflate the apparent gene count per species, producing artifactual "co-orthologs" that are just isoforms of one gene.

**Symptom:** Per-species gene count > 2x what gene-annotation pipeline reported; orthogroups contain multiple proteins from same gene; gene names contain isoform suffixes (`.1`, `-iso1`, etc.).

**Fix:** Pre-filter proteomes to longest isoform per gene. Use `agat_sp_keep_longest_isoform.pl` (AGAT toolkit), Biopython snippet on Ensembl gene-isoform mapping, or `Trinotate` longest-ORF picker. OrthoFinder3 ships a wrapper `tools/primary_transcript.py` for Ensembl/UniProt format.

### Annotation heterogeneity inflating lineage-specific OGs

**Trigger:** Genomes annotated by different pipelines (Augustus, MAKER, Funannotate, NCBI RefSeq) mixed in one analysis.

**Mechanism:** Pipelines differ in handling of intron predictions, gene boundaries, and small-gene filtering. A gene predicted by Augustus but missed by MAKER appears as an apparent lineage-specific gene in the MAKER-annotated species, producing spurious "species-specific" orthogroups.

**Symptom:** CAFE (gene family evolution) shows extreme expansions / contractions for species with different annotation pipelines; per-species "unique" gene count varies 5-10x between technically similar genomes.

**Fix:** Re-annotate all genomes with one pipeline (e.g. BRAKER3 or Funannotate) before orthology. When re-annotation isn't possible, normalize via BUSCO/Compleasm completeness (filter OGs absent from species with < 95% BUSCO complete). Document annotation pipeline per species in methods.

### Ortholog conjecture violations

**Trigger:** Transferring GO/KEGG functional annotation from 1:1 ortholog without testing functional divergence.

**Mechanism:** Studies show orthologs are *weakly* more functionally similar than paralogs (Altenhoff 2012 PLoS Comp Biol 8:e1002514), though Stamboulian 2020 (Bioinformatics 36:i219) finds paralogs often comparable predictors; effect size is small and dependent on evolutionary distance. Subfunctionalization (Force 1999 Genetics 151:1531), neofunctionalization, and dosage subfunctionalization can rapidly differentiate 1:1 orthologs.

**Symptom:** Transferred annotation contradicts species-specific experimental data; ortholog has fold-change different expression patterns; rapid evolution (dN/dS > 0.3) on one branch only.

**Fix:** For high-confidence annotation transfer, require: (1) 1:1 orthology AND (2) low branch dN/dS (< 0.2 for both branches) AND (3) GO evidence code ISO with experimental support upstream. Tag annotation as "predicted from ortholog" rather than equating function. eggNOG ortholog-conjecture-aware mode provides confidence scoring.

### RBH symmetric-but-wrong errors

**Trigger:** Reciprocal best hits (RBH) method on a gene that has been replaced by a paralog in one lineage.

**Mechanism:** Lineage A retains the original ortholog; Lineage B lost the ortholog and replaced its function with a paralog (xenologous replacement). RBH between A and B identifies the paralog as the "ortholog" because it's the best hit.

**Symptom:** dN/dS on RBH ortholog pair > 1 on the B branch (suggesting positive selection but actually paralog substitution); gene tree shows the B sequence is sister to other paralogs of the A gene, not to A.

**Fix:** Use tree-based methods (OrthoFinder3, OMA HOGs) for organisms with extensive paralog history. RBH is appropriate for orthogroup pre-screening only. JustOrthologs is explicitly an RBH method, so it's affected by this; reserve for closely related species.

### Synteny ignored in WGD lineages

**Trigger:** Plant, yeast, fish, or salmonid analysis where one or more ancient WGD events occurred.

**Mechanism:** WGD doubles all genes; subsequent gene loss is biased toward certain functional categories (Dosage Balance Hypothesis; Birchler & Veitia 2007 Plant Cell 19:395). Sequence-only orthology cannot distinguish "ortholog" (single ancestral gene) from "homeolog" (paralog from WGD). In hexaploids (wheat, Brassica), this triples the confusion.

**Symptom:** Multiple co-orthologs per species in orthogroups for WGD-affected lineages; rate variation across "co-orthologs" suggests one is the true ortholog and the others are recent duplicates.

**Fix:** Use synteny-aware methods (GENESPACE -- Lovell 2022 eLife 11:e78526; ProteinOrtho `-synteny`; OrthoFinder3 + post-hoc synteny verification). Restrict 1:1 ortholog phylogenomics to genes in single-copy syntenic regions. For deep WGD ancestry (e.g. 2R vertebrate WGD), modern orthologs of post-2R paralogs (ohnologs) can no longer be unambiguously identified by sequence; use synteny + duplication-dating.

### MAFFT-only alignment in OrthoFinder MSA mode

**Trigger:** `orthofinder -M msa -A mafft` default; very divergent orthogroups (deep taxonomy).

**Mechanism:** MAFFT default settings choose accurate-but-fast iterative refinement. For sequences with >50% divergence, MAFFT's auto choice may downgrade to FFT-NS-2, producing alignments with > 30% poorly aligned columns that distort gene-tree inference and downstream HOG construction.

**Symptom:** Per-OG MAFFT logs show "FFT-NS-2 selected"; gene trees have unstable rooting; bootstrap support < 60% for many internal branches.

**Fix:** Force `mafft-linsi` or specify `-A mafft --thread -1 --localpair --maxiterate 1000`. For deeply divergent OGs, run PRANK or MUSCLE5 post-hoc on critical OGs and re-build gene trees with IQ-TREE. PREQUAL or HmmCleaner segment-filtering improves resulting trees (Di Franco 2019 BMC Evol Biol 19:21).

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| QfO benchmark adoption | 100% within-species ortholog pairs identified | Altenhoff 2024 NAR Genom Bioinform 6:lqae167; minimum competence threshold |
| BUSCO/Compleasm completeness for inclusion | >= 90% complete (single + duplicated) before orthology run | Below this, expect inflated lineage-specific OGs |
| OrthoFinder3 outgroup distance | >= one sister taxonomic level (sister phylum / class / order) | Emms & Kelly 2017 MBE 34:3267 STRIDE rooting |
| Single-copy ortholog filter for phylogenomics | Present in >= 90% of species, exactly 1 copy each | Standard convention; below this, missing data biases tree inference |
| MMseqs2 sensitivity for divergent homologs | `-s 7.5` for > 50% divergence | mmseqs2 documentation; default `-s 4.0` misses distant homologs |
| ProteinOrtho `--conn` (connectivity) | >= 0.1 default; 0.2 stricter for less paralogy confusion | Lechner 2011 |
| OMA HOG inclusion criterion | RBH + Smith-Waterman score and pairwise stability | OMA convention; sub-clade HOGs nested in supergroup HOGs |
| Ortholog age threshold for functional transfer | divergence < 200 Myr OR dN/dS < 0.2 | Operational convention (ortholog conjecture weaker at higher divergence) |
| Annotation pipeline normalization | All species annotated with same pipeline OR BUSCO-completeness within 5% | Avoid annotation-heterogeneity bias on CAFE |
| eggNOG-mapper minimum score | bit score / e-value defaults; check `--seed_ortholog_score` | eggNOG-mapper docs |
| TOGA intactness classes (loss_summ_data.tsv) | I (intact), PI (partial intact), UL (uncertain loss), L (lost), M (missing/assembly gap), PM (partial missing) | Kirilenko 2023 + TOGA repo |
| TOGA orthology relationships (orthology_classification.tsv) | one2one, one2many, many2one, many2many, PG (paralogous projection) | Kirilenko 2023 |
| SonicParanoid2 confidence | >= 0.9 high-confidence orthologs; 0.5-0.9 moderate | Cosentino 2024 docs |
| Reasonable expected runtime (200 species, 16 cores) | OrthoFinder3 default ~8-24h; SonicParanoid2 ~2-6h; FastOMA ~3-8h | Hardware-dependent benchmarks |

## OrthoFinder3 Standard Workflow

**Goal:** Produce HOG-based orthology with species tree and gene-duplication events for any clade.

**Approach:** Prepare cleaned per-species proteomes (longest isoforms) -> include outgroup -> run with MSA + IQ-TREE option -> parse HOG output at appropriate taxonomic level.

```bash
# Pre-clean proteomes: longest isoform per gene
for f in raw_proteomes/*.faa; do
    python tools/primary_transcript.py $f > cleaned/$(basename $f)
done

# OrthoFinder v3 with MSA + IQ-TREE for tree-based HOG inference
orthofinder \
    -f cleaned/ \
    -t 16 \
    -a 4 \
    -M msa \
    -A mafft \
    -T iqtree \
    -S diamond_ultra_sens \
    -y \
    -o orthofinder_run

# Output of interest (v3 layout):
# orthofinder_run/Results_<date>/Phylogenetic_Hierarchical_Orthogroups/N0.tsv  (root-level HOGs)
# orthofinder_run/Results_<date>/Single_Copy_Orthologue_Sequences/             (single-copy MSA-ready)
# orthofinder_run/Results_<date>/Species_Tree/SpeciesTree_rooted.txt
# orthofinder_run/Results_<date>/Gene_Duplication_Events/                       (per-branch dup counts)
```

```python
'''Parse OrthoFinder v3 HOG output for downstream analysis.'''

import pandas as pd
from pathlib import Path


def load_hogs(results_dir, level='N0'):
    '''HOG file path differs from v2: Phylogenetic_Hierarchical_Orthogroups/{level}.tsv.'''
    p = Path(results_dir) / 'Phylogenetic_Hierarchical_Orthogroups' / f'{level}.tsv'
    df = pd.read_csv(p, sep='\t')
    return df.set_index('HOG')


def _is_present(v):
    '''OrthoFinder v3 HOG cells are either NaN (older versions), '' (newer), or a comma-separated gene list.'''
    return not (pd.isna(v) or v == '' or str(v).strip() == '')

def single_copy_hogs(hog_df, min_species_fraction=0.9):
    '''Return HOG IDs where every present species has exactly 1 gene and >= fraction of species present.'''
    sp_cols = [c for c in hog_df.columns if c not in ('OG', 'Gene Tree Parent Clade')]
    is_single = hog_df[sp_cols].apply(
        lambda r: all((not _is_present(v)) or ',' not in str(v) for v in r), axis=1
    )
    n_present = hog_df[sp_cols].apply(lambda r: sum(_is_present(v) for v in r), axis=1)
    keep = is_single & (n_present >= min_species_fraction * len(sp_cols))
    return hog_df.index[keep].tolist()


def classify_orthology(hog_df, sp_pair):
    '''Per-HOG classify pairwise orthology between two species.

    Returns one of: '1-1', '1-many', 'many-1', 'many-many', 'absent', 'sp1-only', 'sp2-only'.
    '''
    sp1, sp2 = sp_pair
    types = {}
    for hog, row in hog_df.iterrows():
        v1, v2 = row.get(sp1), row.get(sp2)
        n1 = 0 if not _is_present(v1) else len(str(v1).split(','))
        n2 = 0 if not _is_present(v2) else len(str(v2).split(','))
        if n1 == 0 and n2 == 0: types[hog] = 'absent'
        elif n1 == 0:           types[hog] = 'sp2-only'
        elif n2 == 0:           types[hog] = 'sp1-only'
        elif n1 == 1 and n2 == 1: types[hog] = '1-1'
        elif n1 == 1 and n2 > 1: types[hog] = '1-many'
        elif n1 > 1 and n2 == 1: types[hog] = 'many-1'
        else:                     types[hog] = 'many-many'
    return types
```

## SonicParanoid2 + Cross-Validation

**Goal:** Run a second orthology method to cross-validate OrthoFinder3 calls (consensus increases QfO benchmark precision).

**Approach:** SonicParanoid2 with default ML predictor -> intersect orthogroups with OrthoFinder HOGs at the root level -> compute Jaccard agreement.

```bash
sonicparanoid -i cleaned/ -o sp2_run --mode default --threads 16 --pfam pre-computed
# Output: sp2_run/runs/<date>/orthogroups/flat.ortholog_groups.tsv
```

```python
from itertools import combinations
import pandas as pd

def jaccard_ogs(ogs_a, ogs_b):
    '''Compute mean Jaccard between two orthogroup sets keyed by gene IDs.
    Each og is a frozenset of gene IDs.'''
    set_a = {gene: og for og in ogs_a for gene in og}
    set_b = {gene: og for og in ogs_b for gene in og}
    common = set(set_a) & set(set_b)
    jacs = []
    for g in common:
        a = set_a[g]
        b = set_b[g]
        j = len(a & b) / len(a | b) if a | b else 0
        jacs.append(j)
    return sum(jacs) / len(jacs) if jacs else 0
```

Consensus single-copy HOGs (1:1 in both methods) are the highest-confidence input for downstream phylogenomic concatenation or selection analyses.

## TOGA for Vertebrate-Scale Orthology with Gene-Loss

**Goal:** Identify orthologs and classify gene-loss/intactness across hundreds of mammal or bird genomes.

**Approach:** Run Progressive Cactus whole-genome alignment (see [[whole-genome-alignment]]) -> TOGA projects reference genes through chains -> classifies each query gene as I/PI/UL/L/M/PM.

```bash
# After Cactus alignment producing reference-query chain files
toga.py \
    --chain cactus_chain.bb \
    --bed reference_genes.bed \
    --tDB target.2bit \
    --qDB query.2bit \
    --nextflow_dir nf_pipeline_dir \
    --pn project_name \
    --cpu 64 \
    --quiet

# Output:
#   project_name/loss_summ_data.tsv          per-gene intactness call
#   project_name/orthology_classification.tsv  one-to-one / one-to-many / many-to-many
```

TOGA emits eight classes per gene in `loss_summ_data.tsv`: I (intact), PI (partial intact), UL (uncertain loss), L (lost), M (missing under assembly gap), PM (partial missing), PG (paralogous projection / no orthologous chain found), N (no data). For evolutionary analysis, treat I as functional; PI as fragmented (often functional but caveat); L + UL as candidates for true gene loss after manual review of read coverage; M / PM are assembly-quality issues, not biology; PG indicates the algorithm found only paralogous chains. CESAR 2.0 provides exon-aware coding annotation projection used internally.

## Functional Annotation Transfer with eggNOG-mapper

**Goal:** Propagate GO / KEGG / EC annotations from curated orthologs to a novel proteome.

**Approach:** Run eggNOG-mapper with appropriate evolutionary level -> integrate with OrthoFinder HOGs for confidence stratification.

```bash
emapper.py \
    --output project \
    -i novel_proteome.faa \
    --cpu 16 \
    --decorate_gff genome.gff \
    --tax_scope auto \
    --target_orthologs all \
    --evidence_type experimental \
    --pfam_realign denovo
```

Output `project.emapper.annotations` includes per-gene: best ortholog, taxonomic scope of OG, GO terms, KEGG pathways, COG category. Confidence stratification: experimental-evidence GO (EXP, IDA, IPI, IMP, IGI, IEP) > non-experimental (ISO from 1:1 close ortholog) > IEA (electronic). Tag annotation transfer evidence in output.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| OrthoFinder 1:1; SonicParanoid 1:many | Recent duplication in one lineage; OrthoFinder collapsed | Inspect gene tree; if duplication post-speciation, both are co-orthologs (correct in SP2) |
| OrthoFinder 1:1; ProteinOrtho merges into single OG | Different connectivity threshold | OrthoFinder HOG is more granular; both correct at different levels |
| OMA "1:1 across all species"; OrthoFinder "split orthogroups" | OMA more conservative (strict RBH) | Use OMA for stringent comparative analyses; OrthoFinder for broader recall |
| OrthoFinder OG contains tandem duplicates | Tandem duplications not collapsed | Use ProteinOrtho `-synteny` or GENESPACE post-filter; or apply MCScanX tandem detection (default 5-gene window) |
| eggNOG ortholog disagrees with OrthoFinder | eggNOG uses fixed reference set; OrthoFinder uses the sampled species | Trust OrthoFinder for sampled-species 1:1; trust eggNOG for functional annotation from curated references |
| TOGA reports "Lost" but OrthoFinder finds ortholog | TOGA chain-projection failed; assembly gap | Re-check assembly contig at locus; if gap, treat as missing (M) not lost (L) |
| All methods disagree on a single OG | Likely tandem duplicates, chimeric assembly, or hidden paralogy | Manual gene-tree inspection; treat OG as low-confidence |

**Operational rule for publication:** Cross-validate single-copy orthologs across 2+ methods (OrthoFinder3 + SonicParanoid2 or OrthoFinder3 + OMA); use consensus HOG set for phylogenomics. Functional annotation transfer requires either 1:1 orthology + low branch dN/dS, or eggNOG ISO/EXP evidence. Report annotation pipeline normalization in methods.

## Cohort Gotchas

- **WGD lineages:** Salmonids (recent Ss4R WGD), teleosts (Ts3R), plants (1-4 rounds), yeast (2 rounds), opisthokonts (1-2 ancient) -- require synteny-aware orthology
- **Highly fragmented assemblies:** N50 < 100 kb produces extensive false absence; flag affected species and exclude from CAFE
- **Polyploids:** modern polyploids are multi-genome individuals; assign subgenomes before orthology (see [[whole-genome-duplication]])
- **Genome size variation:** Drosophila ~150 Mb vs Locust ~5 Gb -- repeat-dominated large genomes have inflated false positive rates from TE-derived proteins; filter TE proteins before orthology
- **Domain rearrangements:** chimeric gene-fusion proteins (e.g. Jumonji-domain) place into multiple OGs; OrthoFinder3 + Broccoli chimera detection helpful
- **HGT-affected genes (prokaryotes):** standard orthology returns "vertical orthologs" that may not exist; use ALE-aware approaches (see [[gene-tree-species-tree-reconciliation]])

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why this orthology method?" | OrthoFinder3 / OMA / SonicParanoid2 chosen based on QfO benchmark (Altenhoff 2024) and clade-appropriate scale; consensus single-copy HOGs reported |
| "Outgroup?" | Outgroup taxon X from sister taxonomic level included; STRIDE-rooted gene trees |
| "Isoforms?" | Longest-isoform-per-gene pre-filter applied via AGAT / OrthoFinder primary_transcript.py |
| "Annotation pipeline heterogeneity?" | All species annotated with Y pipeline OR BUSCO completeness within Z% across species |
| "WGD?" | Acknowledged; synteny-aware verification via GENESPACE / ProteinOrtho synteny |
| "Functional transfer evidence?" | 1:1 ortholog + dN/dS < 0.2 + eggNOG EXP/IDA evidence + tagged as predicted |
| "Cross-validation?" | OrthoFinder3 + second method (SonicParanoid2 / OMA); consensus single-copy HOGs used |
| "Ortholog conjecture caveat?" | Acknowledged (Altenhoff 2012; Stamboulian 2020); high-confidence single-copy 1:1 within short divergence; functional divergence flagged |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| OrthoFinder "no orthogroups found" | Proteomes empty or wrong path | Check FASTA non-empty; default file extension `.fa` `.faa` `.fasta` recognized |
| HOG file Phylogenetic_Hierarchical_Orthogroups missing | v3 layout new; parser expects v2 path | Use `Phylogenetic_Hierarchical_Orthogroups/N0.tsv` for v3; OrthoFinder v2 used `Orthogroups/Orthogroups.tsv` |
| All single-copy HOGs are tiny (1-2 genes) | Outgroup too distant; only paralog-free genes survive | Add intermediate outgroup; relax single-copy fraction to 0.7-0.8 |
| SonicParanoid2 ML model fails to download | Network or model registry issue | Pre-download with `sonicparanoid-get-test-data`; use `--mode legacy` as fallback |
| OMA "infinity recursion in HOG" | Self-referential HOG (rare bug) | Update to latest OMA; bug reports on GitHub for known cases |
| eggNOG-mapper says "no hits" for half the proteome | Default DIAMOND sensitivity too low | Add `--sensmode more-sensitive` or use `--sensmode ultra-sensitive` |
| TOGA "no chain file" | Cactus output not properly converted | Use `halSynteny` and `chainNet` UCSC pipeline; verify chain file format |
| Gene IDs in HOG have unexpected suffix `__rev` | Synteny strand convention | Strip the suffix; check OrthoFinder log for the convention applied |
| Per-species gene count radically different from annotation | Isoforms not filtered | Re-filter to longest isoform per gene |
| Annotation transfer says "Hypothetical" everywhere | eggNOG version mismatch with proteome | Update eggNOG database to current; v5 vs v6 has different OG layout |
| ProteinOrtho synteny option times out | Slow synteny module on huge genomes | Skip synteny for screening; run only on candidate OGs |

## Tool Installation Notes

```bash
# OrthoFinder3
conda install -c bioconda orthofinder=3.0
# Or via Python wrapper: pip install orthofinder3

# SonicParanoid2
conda install -c bioconda sonicparanoid

# Broccoli
git clone https://github.com/rderelle/Broccoli && cd Broccoli && pip install .

# ProteinOrtho 6
conda install -c bioconda proteinortho

# OMA standalone (Linux)
wget https://omabrowser.org/standalone/OMA.tgz && tar xf OMA.tgz && cd OMA && ./install.sh
# FastOMA
pip install fastoma

# eggNOG-mapper 2
conda install -c bioconda eggnog-mapper

# JustOrthologs
git clone https://github.com/ridgelab/justOrthologs && cd justOrthologs && python setup.py install

# TOGA
conda env create -f https://raw.githubusercontent.com/hillerlab/TOGA/master/toga_env.yml
# Requires nf-core and Nextflow

# Quality control
conda install -c bioconda busco compleasm
```

For Quest-for-Orthologs benchmark submission, follow https://orthology.benchmarkservice.org/ instructions; the benchmark refreshes annually.

## References

- Fitch WM 1970 Syst Zool 19:99 (ortholog / paralog definitions)
- Sonnhammer EL & Koonin EV 2002 Trends Genet 18:619 (in-paralog / out-paralog)
- Altenhoff AM & Dessimoz C 2009 PLoS Comp Biol 5:e1000262 (orthology-method benchmark/assessment)
- Altenhoff AM et al 2012 PLoS Comp Biol 8:e1002514 (ortholog conjecture quantification)
- Altenhoff AM et al 2013 PLoS ONE 8:e53786 (HOGs from orthologous gene pairs, GETHOGs)
- Altenhoff AM et al 2019 Genome Res 29:1152 (OMA standalone)
- Altenhoff AM et al 2024 NAR Genom Bioinform 6:lqae167 (Quest for Orthologs benchmark)
- Emms DM & Kelly S 2019 Genome Biol 20:238 (OrthoFinder 2)
- Emms DM & Kelly S 2017 MBE 34:3267 (STRIDE rooting)
- Emms DM et al 2026 Nat Methods 23:1327 (OrthoFinder 3)
- Cosentino S, Sriswasdi S & Iwasaki W 2024 Genome Biol 25:195 (SonicParanoid2)
- Derelle R et al 2020 MBE 37:3389 (Broccoli)
- Lechner M et al 2011 BMC Bioinf 12:124 (ProteinOrtho)
- Majidian S et al 2025 Nat Methods 22:269 (FastOMA)
- Cantalapiedra CP et al 2021 MBE 38:5825 (eggNOG-mapper 2)
- Miller JB et al 2019 Bioinformatics 35:546 (JustOrthologs)
- Kirilenko BM et al 2023 Science 380:eabn3107 (TOGA + CESAR)
- Sharma V, Schwede P & Hiller M 2017 Bioinformatics 33:3985 (CESAR 2.0)
- Stamboulian M et al 2020 Bioinformatics 36:i219 (ortholog conjecture revisited)
- Force A et al 1999 Genetics 151:1531 (subfunctionalization)
- Birchler JA & Veitia RA 2007 Plant Cell 19:395 (gene balance hypothesis)
- Nehrt NL et al 2011 PLoS Comp Biol 7:e1002073 (ortholog conjecture challenge)
- Studer RA & Robinson-Rechavi M 2009 Trends Genet 25:210 (ortholog conjecture critique)
- Penel S et al 2009 BMC Bioinf 10(Suppl 6):S3 (HOGENOM)
- Zhang C & Mirarab S 2022 Bioinformatics 38:4949 (ASTRAL-Pro2)
- Di Franco A et al 2019 BMC Evol Biol 19:21 (alignment filtering improves trees)

## Related Skills

- comparative-genomics/synteny-analysis - Synteny-anchored ortholog disambiguation in WGD lineages
- comparative-genomics/whole-genome-duplication - Distinguishing ohnologs (WGD paralogs) from orthologs
- comparative-genomics/gene-family-evolution - Birth-death modeling on OG counts requires consistent orthology
- comparative-genomics/gene-tree-species-tree-reconciliation - DTL-aware orthology for prokaryotes / HGT-affected lineages
- comparative-genomics/positive-selection - Selection analysis on single-copy ortholog alignments
- comparative-genomics/comparative-annotation-projection - TOGA / CESAR projects orthology with gene-loss classification
- phylogenetics/modern-tree-inference - Single-copy concatenation phylogenomics input
- phylogenetics/species-trees - Coalescent species-tree from OrthoFinder gene trees
- alignment/multiple-alignment - MSA quality affects OrthoFinder MSA-mode HOG output
- genome-annotation/functional-annotation - Functional annotation propagation via eggNOG / orthology
- read-qc/quality-reports - BUSCO / Compleasm completeness affects orthology reliability
<!-- END FILE: comparative-genomics/ortholog-inference/SKILL.md -->

## 子目录：comparative-genomics/pangenome-analysis

<!-- BEGIN FILE: comparative-genomics/pangenome-analysis/SKILL.md -->
---
name: bio-comparative-genomics-pangenome-analysis
description: Build and analyze pangenomes for prokaryotes (Panaroo, PPanGGOLiN, PEPPAN, GET_HOMOLOGUES, anvi'o pangenomics) and eukaryotes (Minigraph-Cactus, PGGB, vg pangenome graphs). Implement Tettelin core/accessory/cloud genome decomposition (Tettelin 2005), Heap's law open/closed pangenome modeling, gene presence/absence GWAS (Scoary, pyseer), pangenome graph variant calling (vg, PanGenie), and structural-variation graph indexing. Use when assembling species- or genus-level pan-gene catalogs, separating core from accessory/shell/cloud genes, testing gene-content associations with phenotypes, building pangenome graphs from haplotype-resolved assemblies, calling SVs from pangenome graphs, or selecting between bacterial-pangenome and eukaryotic-pangenome workflows.
tool_type: cli
primary_tool: Panaroo
---

## Version Compatibility

Reference examples tested with: Panaroo 1.5.1+ (Tonkin-Hill 2020 Genome Biol 21:180), PPanGGOLiN 2.2.0+ (Gautreau 2020 PLoS Comp Biol 16:e1007732), PEPPAN 1.0.5+ (Zhou 2020 GR 30:1667), GET_HOMOLOGUES 25102023+, anvi'o 8.0+ (Eren 2021 Nat Microbiol 6:3), Minigraph-Cactus (Hickey 2024 Nat Biotech 42:663; bundled with Cactus 2.5+), PGGB 0.7.5+ (Garrison 2024 Nat Methods 21:2008), vg 1.59.0+ (Sirén J et al 2024 Nat Methods 21:2017), PanGenie 3.1.0+ (Ebler 2022 Nat Genet 54:518), PGR-TK 0.3.6+ (Chin 2023 Nat Methods 20:1213; cschin/pgr-tk; repo archived April 2026 transitioning to PANGEA), PANGEA (in development by DGI / Diploid Genomics as PGR-TK's successor for pangenome graph exploration + analysis -- check https://github.com/cschin/pgr-tk for current repository pointer), Bakta 1.10.4+ (annotation for input), Roary 3.13.0+ (DEPRECATED; use Panaroo), Scoary 1.6.16+, pyseer 1.3.11+, BUSCO 5.7+, FastTree 2.1.11+, RAxML-NG 1.2+. Python 3.10+ required for Panaroo / PPanGGOLiN.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `panaroo --version`; `ppanggolin --version`; `peppan --help`; `cactus-pangenome --help`; `pggb --version`; `vg version`
- Python: `pip show panaroo ppanggolin`

If code throws `Bakta annotation incompatible`, `GFA file inconsistent`, `vg index version mismatch`, the bacterial pangenome ecosystem expects consistent annotation; re-annotate all input genomes with the same tool and version before pangenome analysis.

# Pangenome Analysis

**"What genes are universal vs accessory across this set of genomes?"** -> The pangenome is the union of all genes across a sampled group; the **Tettelin partition** (Tettelin 2005 PNAS 102:13950) splits it into core (universal), shell (in many but not all), cloud (rare), and species-specific (private) genes. The fundamental dichotomy is **bacterial pangenome** (clusters genes into orthogroups; Panaroo / PPanGGOLiN / PEPPAN for compact genomes) vs **eukaryotic pangenome** (graph-based; Minigraph-Cactus / PGGB / vg for haplotype-resolved sequences). The choice depends on what's being represented: bacterial pangenome captures gene-content variation in a species/genus; eukaryotic pangenome graph captures haplotype-level structural and sequence variation. **Roary (Page 2015) is now deprecated** in favor of Panaroo, which handles annotation-error noise that previously inflated bacterial pangenomes substantially.

- CLI: `panaroo -i annotated_gffs/ -o panaroo_out --clean-mode strict --remove-invalid-genes` -- bacterial pangenome
- CLI: `ppanggolin workflow --fasta fasta_list.tsv --output ppanggolin_out` -- partitioned bacterial pangenome
- CLI: `peppan -i genomes.gff -o peppan_out` -- genus-scale bacterial pangenome
- CLI: `cactus-pangenome jobStore seqFile.txt --reference name --vcf --gfa` -- Minigraph-Cactus pangenome
- CLI: `pggb -i genomes.fa.gz -n 90 -t 32 -o pggb_out` -- PGGB pangenome graph
- CLI: `vg autoindex --workflow giraffe -r ref.fa -v variants.vcf.gz` -- vg pangenome indexing

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| Panaroo (Tonkin-Hill 2020 GB 21:180) | Graph-based ortholog clustering + annotation-error correction | Core, shell, accessory pangenome with cleaned annotations | Best for clonal bacteria (Mtb 413-genome benchmark; Tonkin-Hill 2020) | Slow for > 10000 genomes; assumes Prokka/Bakta input |
| PPanGGOLiN (Gautreau 2020 PLoS CB 16:e1007732) | Hidden Markov partition: persistent/shell/cloud | Partitioned pangenome with HMM-based class assignment | Scales to many genomes; interpretable partitions | Probabilistic class boundaries differ from strict Tettelin |
| PEPPAN (Zhou 2020 GR 30:1667) | Bacterial pangenome for diverse genera | Pan + core genomes from 1000s of genomes | Designed for high diversity (whole genus) | Slower than newer alternatives at small scales |
| Roary (Page 2015; DEPRECATED) | Original bacterial pangenome | Same outputs as Panaroo | Legacy; widely cited | Inflates accessory substantially due to annotation-error tolerance; use Panaroo |
| GET_HOMOLOGUES (Contreras-Moreira 2013) | Multi-algorithm consensus (OrthoMCL, BDBH, COG) | Consensus pangenome | Cross-validates across methods | Slower; multi-program output integration |
| anvi'o pangenomics (Eren 2021 Nat Microbiol 6:3) | Interactive pangenome with metadata | Visual pangenome browsing + integration | Standard for interactive microbial pangenome | Less automated; manual curation expected |
| Minigraph-Cactus (Hickey 2024 Nat Biotech 42:663) | Cactus base-level + minigraph SV-graph integration | Pangenome graph (GFA, VCF, GBZ) | Production-grade for HPRC-scale haplotypes | Requires reference; designed for intra-species pangenome |
| PGGB (Garrison 2024 Nat Methods 21:2008) | All-vs-all wfmash + seqwish | Pangenome graph (GFA) | Modern reference-free graph; HPRC-validated | Computationally heavy at > 100 genomes |
| vg pangenome (Sirén J et al 2024 Nat Methods 21:2017) | Pangenome graph indexing + Giraffe / GiraffeY mapping | Mapped reads to graph + variant calling | vg ecosystem standard for graph-based variant calling | Setup complex; learning curve |
| PanGenie (Ebler 2022 Nat Genet 54:518) | Pangenome-graph-based genotyping | SV genotype calls | Efficient genotyping from short reads via graph | Requires pre-built pangenome graph |
| PGR-TK (Chin 2023 Nat Methods 20:1213; cschin/pgr-tk) | Minimizer Anchored Pangenome (MAP) graph + principal bundle decomposition | Multiscale pangenome graph; bundle SVGs; AGC-backed sequence db | Designed for repetitive / clinically-relevant genes (MHC class II, DAZ1-4, OPN1LW/OPN1MW); decomposes tangled graph into interpretable bundles; complements Minigraph-Cactus by exposing fine-grained allele structure | Repo archived April 2026 -> PANGEA succession; pinned to Peregrine-assembler-derived workflow; not a drop-in for variant-calling pipelines |
| PANGEA (in development by DGI / Diploid Genomics; succeeds PGR-TK; check cschin/pgr-tk for current pointer) | Next-generation MAP-graph framework | Same conceptual outputs as PGR-TK with modernized API | Active development 2026+; expected to add tighter integration with HPRC / T2T workflows | API surface in flux; pin specific version when scripting |
| Heaps law / Tettelin (Tettelin 2005 PNAS 102:13950) | Statistical model of pangenome openness | Open / closed pangenome classification | Foundational framework | Class boundaries depend on sampling |
| Scoary (Brynildsrud 2016) | Pan-GWAS on gene presence/absence | Phenotype-gene associations | Standard bacterial pan-GWAS tool | Limited to binary phenotypes |
| pyseer (Lees 2018 Bioinformatics 34:4310) | Continuous + binary phenotype association on k-mers/genes | Pan-GWAS with k-mer / gene-content units | More flexible than Scoary | Computational cost |
| pirate (Bayliss 2019) | Bacterial pangenome from multiple methods | Cross-method consensus | Alternative to GET_HOMOLOGUES | Less popular now |

Methodology evolves; verify the current Panaroo and PPanGGOLiN manuals + the 2024-2025 microbial pangenome reviews. The HPRC draft pangenome (Liao 2023 Nature 617:312) sets the modern eukaryotic pangenome standard; for bacterial work, Panaroo + PPanGGOLiN is the standard combination.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Bacterial strain set (5-1000 genomes) of one species | Panaroo + PPanGGOLiN | Cross-validation; Panaroo's annotation-cleaning + PPanGGOLiN's partition |
| Bacterial genus-level pangenome (> 1000 genomes) | PEPPAN | Designed for high genus-level diversity |
| Mycobacterium tuberculosis (clonal) | Panaroo | Tonkin-Hill 2020 benchmark; clonal pangenomes |
| E. coli (highly diverse) | PPanGGOLiN or PEPPAN | High accessory diversity |
| Eukaryotic intra-species pangenome (e.g. human, soybean) | Minigraph-Cactus or PGGB | Graph-based; SV-aware |
| HPRC-style 90 haplotype graph | Minigraph-Cactus | Production-grade for HPRC scale |
| Reference-free eukaryotic pangenome | PGGB | All-vs-all alignment-free graph |
| Pangenome graph for variant calling | vg autoindex -> vg giraffe | Standard graph-aligner ecosystem |
| Bacterial pan-GWAS for phenotype | Panaroo + Scoary or pyseer | Pangene matrix from Panaroo; pan-GWAS tool |
| Visualize pangenome interactively | anvi'o pangenomics workflow | Standard for interactive analysis |
| Distinguish core / shell / cloud genes | PPanGGOLiN (HMM-partitioned) or Tettelin manual partition on Panaroo output | Standard Tettelin framework |
| Open vs closed pangenome (Heaps law) | wgd v2 statistical fit OR custom mclust on Panaroo output | Tettelin 2005 framework |
| Detect HGT-acquired accessory genes | Cross-reference with [[hgt-detection]] | Pangenome + phylogeny |
| Eukaryotic structural-variation indexing | Minigraph-Cactus -> vg + PanGenie | SV-aware genotyping pipeline |
| Bacterial functional pangenome | Panaroo + eggNOG-mapper + KEGG | Functional annotation |
| Pangenome-aware reference for read alignment | vg giraffe with pangenome graph | Reduces reference bias |
| Genome-graph-based fine-mapping | vg + GraphAligner or vg giraffe | SV-aware short-read alignment |
| Repetitive / clinically relevant gene (MHC class II, DAZ1-4, OPN1LW/OPN1MW) | PGR-TK MAP graph + principal bundle decomposition | Built for tangled repeat graphs; bundle decomposition reveals haplotype-allele structure that linear refs collapse |
| Next-gen pangenome graph exploration (2026+) | PANGEA (PGR-TK successor, in development by DGI / Diploid Genomics) | Modernized successor to PGR-TK; check cschin/pgr-tk pointer for current repo |
| HLA / KIR / immune-locus pangenome | PGR-TK + manual bundle inspection | Standard tools collapse repeat alleles; PGR-TK's bundle decomposition preserves them |

## Per-Tool Failure Modes

### Annotation heterogeneity inflating accessory genome

**Trigger:** Running Panaroo on Prokka- vs Bakta- vs RefSeq- annotated genomes mixed.

**Mechanism:** Different annotation tools predict different gene boundaries; the same gene is annotated slightly differently across tools, appearing as separate orthogroups. Roary's tolerance of these differences inflated the bacterial accessory genome substantially -- nearly an order of magnitude on the clonal M. tuberculosis benchmark (Tonkin-Hill 2020 GB 21:180). Panaroo's graph-based correction reduces this but cannot eliminate it.

**Symptom:** Per-strain "accessory" gene count is inflated relative to known biology; comparison to a single-pipeline reference reveals substantial spurious gene-content differences.

**Fix:** Re-annotate ALL genomes with one pipeline (currently Bakta 1.10.4+ for bacteria; Bakta is GenBank-compliant and faster than Prokka). Use `panaroo --clean-mode strict --remove-invalid-genes` to apply graph cleaning. Document annotation pipeline + version in methods.

### Tettelin partition class boundary artifacts

**Trigger:** Reporting "core genome" vs "accessory" as percent-of-strains thresholds (e.g. 99% = core).

**Mechanism:** Tettelin 2005 used 100%-presence = core; pragmatic studies use 95%-99%. The class boundary is arbitrary; small variation in the threshold dramatically changes core/accessory ratio.

**Symptom:** Core genome size varies 10-30% depending on whether threshold is 95% or 99%.

**Fix:** Report core/shell/cloud at multiple thresholds; PPanGGOLiN's HMM partition is more principled but still has tunable parameters. Standard reporting: core = present in >=95% (or >=99%); shell = 15-95%; cloud = < 15%. Document threshold.

### Roary's annotation-error noise (DEPRECATED tool)

**Trigger:** Using Roary in new analyses.

**Mechanism:** Roary tolerates annotation errors (low-identity matches; protein-vs-DNA matches), producing thousands of artifactual accessory genes. Panaroo's introduction (Tonkin-Hill 2020) demonstrated this by re-analyzing 413 Mtb genomes and finding Panaroo's accessory genome was nearly an order of magnitude smaller than the inflated tools' (Roary included).

**Symptom:** Roary output has many "lineage-specific genes" with poor evidence (single-strain hits, short proteins, no functional annotation).

**Fix:** Migrate to Panaroo. Panaroo can read Roary's input format; for legacy projects, re-run with Panaroo and compare. Panaroo's `--clean-mode strict` enforces strict graph-based quality control.

### Pangenome graph reference bias (eukaryote)

**Trigger:** Using Minigraph-Cactus with a single reference; calling variants against the "reference" path.

**Mechanism:** Minigraph-Cactus is reference-anchored; the chosen reference appears throughout the graph as a privileged path. Variants are called relative to the reference path; non-reference haplotypes are under-represented in the variant calling.

**Symptom:** Variant call density on non-reference haplotypes is lower than on reference; allele frequencies skewed toward reference.

**Fix:** Use PGGB (reference-free) for less reference-biased analysis. Alternatively, treat the reference choice as a methodological parameter and document. For HPRC, multiple references can be used and results pooled.

### Heaps law misapplied

**Trigger:** Concluding "open pangenome" from a single Heaps-law fit on insufficient data.

**Mechanism:** Heaps law parameter alpha distinguishes open (alpha < 1) from closed (alpha > 1) pangenome; estimation requires sampling many genomes. Few genomes give unstable estimates.

**Symptom:** Heaps-law alpha varies by > 0.2 across resampling; conclusions about pangenome openness flip.

**Fix:** Require >= 50 genomes (preferably > 100) for Heaps-law estimation; report 95% CI from resampling. Tettelin 2005 demonstrated open Streptococcus agalactiae; Vernikos 2015 reviews open vs closed across taxa.

### PGGB memory exhaustion at many genomes

**Trigger:** Running PGGB with > 30 large eukaryotic genomes on a single node.

**Mechanism:** PGGB's wfmash all-vs-all step has O(N^2) memory pattern; large eukaryotic genomes (> 1 Gb) make memory prohibitive for > 30 input genomes.

**Symptom:** PGGB OOMs at the wfmash stage; cluster job killed by OOM-killer.

**Fix:** Use Minigraph-Cactus for > 30 genomes (it scales better); or split PGGB into chromosomes/regions. PGGB recommendation is <= 20 large genomes per run.

### vg index version mismatch breaking giraffe

**Trigger:** Pre-built vg index used with a different vg version for read alignment.

**Mechanism:** vg index format evolved; pre-built indexes from one version may not be compatible with another.

**Symptom:** vg giraffe fails with "index version" error.

**Fix:** Rebuild vg index with current version; or pin vg version for an analysis. Future vg releases promise backward compatibility but verify.

### PanGenie genotype false positives in repetitive regions

**Trigger:** PanGenie on highly repetitive regions (centromeres, segmental duplications).

**Mechanism:** Pangenome-graph-based genotyping requires unique paths in the graph; highly repetitive regions create graph-spaghetti paths that are difficult to genotype reliably.

**Symptom:** PanGenie calls many heterozygous SVs in known-repetitive regions; quality scores low.

**Fix:** Restrict PanGenie to non-repetitive regions; combine with traditional read-based SV callers (DELLY, Manta) for repeat regions. The HPRC paper documents this limitation (Liao 2023).

### Bacterial pangenome with frequent gene-content recombination

**Trigger:** Building a pangenome of a species with extensive recombination (e.g. Neisseria, Streptococcus pneumoniae).

**Mechanism:** Frequent recombination breaks the "vertical inheritance" assumption underlying ortholog clustering; the same gene appears in many phylogenetic positions across strains, complicating orthology and inflating accessory genome.

**Symptom:** Phylogenetic trees from core genome are unstable; per-gene trees show extensive incongruence; pangenome accessory genome appears artificially large.

**Fix:** Use ClonalFrameML (Didelot 2015 PLoS Comp Biol 11:e1004041) to identify recombinant regions; mask them before pangenome analysis. Restrict core genome analysis to non-recombinant regions.

### Annotation density variation across genomes

**Trigger:** Mixing well-annotated reference genomes with newly assembled, draft-annotation genomes.

**Mechanism:** Draft annotations miss small genes, pseudogenes, and lineage-specific genes; well-annotated genomes have these. Comparing them inflates "accessory" in draft genomes.

**Symptom:** Draft genomes have 200-500 fewer accessory genes than expected; per-genome BUSCO completeness > annotation completeness.

**Fix:** Re-annotate all genomes consistently with Bakta + Prodigal; document BUSCO completeness for each. Exclude genomes with > 5% lower BUSCO than median.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Core genome threshold | >=95% (relaxed) to 100% (strict) of strains | Tettelin 2005; pragmatic |
| Shell genome | 15-95% (or 5-95% per PPanGGOLiN) | PPanGGOLiN docs |
| Cloud genome | < 15% of strains | Tettelin 2005 |
| Heaps law alpha (open) | < 1 | Tettelin 2005 |
| Heaps law alpha (closed) | > 1 | Tettelin 2005 |
| Minimum genomes for Heaps law fit | >= 50; >= 100 preferred | Vernikos 2015 |
| Panaroo gene cluster identity | >=70% (default); stricter for clonal | Panaroo defaults |
| PPanGGOLiN coverage | 80% gene-length coverage in clustering | Default |
| PEPPAN BLAT threshold | identity >= 70% | Zhou 2020 |
| Mycobacterium tuberculosis core | ~3500-3700 genes (Tonkin-Hill 2020 Mtb benchmark) | Bench results |
| E. coli pangenome (open) | core ~2400; pangenome >15000 | Reference |
| Plasmodium falciparum core | ~5300 genes (eukaryotic prokaryote-like) | Reference |
| Minimum strains for bacterial pangenome | >= 5; >= 20 for shell/cloud meaningful | Empirical |
| HPRC pangenome size | 90 haplotypes, ~6.4M variants | Liao 2023 |
| PGGB recommended max genomes | <= 20 large eukaryotic; 100+ for compact | Garrison 2024 |
| PanGenie minimum k-mer | k = 31 default | Ebler 2022 |
| vg index Haplotype Sampling | --haplotype-sampling YES for multi-pop graph | Sirén J et al 2024 Nat Methods 21:2017 |
| Scoary pan-GWAS p-value threshold | Bonferroni-corrected p < 0.05 | Brynildsrud 2016 |
| pyseer continuous-trait power | requires > 1000 isolates for solid signal | Lees 2018 |
| anvi'o pangenome minimum | 5+ genomes for non-trivial visualization | Eren 2021 |

## Panaroo Bacterial Pangenome Workflow

**Goal:** Construct a high-quality bacterial pangenome with annotation-error correction.

**Approach:** Annotate genomes consistently with Bakta -> run Panaroo strict mode -> partition with PPanGGOLiN.

```bash
# 1. Annotate all genomes with Bakta (consistent annotation)
mkdir -p annotated
for fa in genomes/*.fa; do
    name=$(basename $fa .fa)
    bakta --db /path/to/bakta-db --threads 16 \
        --output annotated/${name} --prefix $name \
        --genus Escherichia --species coli \
        $fa
done

# 2. Run Panaroo
panaroo -i annotated/*.gff -o panaroo_out -t 16 \
    --clean-mode strict --remove-invalid-genes

# 3. Extract pangenome matrix
# panaroo_out/gene_presence_absence.csv      strains x genes matrix
# panaroo_out/core_gene_alignment.aln        core gene MSA for phylogeny
# panaroo_out/pan_genome_reference.fa        consensus pangenome sequence

# 4. Tettelin partition (custom)
python tettelin_partition.py \
    --presence panaroo_out/gene_presence_absence.csv \
    --core-threshold 0.99 --shell-threshold 0.15 \
    --output panaroo_out/tettelin_classification.tsv

# 5. PPanGGOLiN HMM partition (alternative)
# PPanGGOLiN expects a TSV index: `genome_name<TAB>path/to.gff3` per row
for f in annotated/*.gff3; do
    printf "%s\t%s\n" "$(basename "$f" .gff3)" "$(realpath "$f")"
done > gff_list.tsv
ppanggolin all --anno gff_list.tsv -o ppanggolin_out --threads 16
# Output: ppanggolin_out/pangenome.h5 (HDF5 with HMM-partitioned genes)
```

```python
'''Tettelin core/shell/cloud partition from Panaroo gene presence/absence matrix.'''
import pandas as pd


def tettelin_partition(presence_matrix, core_threshold=0.99,
                       shell_threshold=0.15):
    '''Returns DataFrame[gene_name] -> Tettelin class.'''
    # presence_matrix: rows = genes, cols = strains, 0/1 entries
    n_strains = presence_matrix.shape[1]
    fraction = presence_matrix.sum(axis=1) / n_strains
    classes = pd.cut(fraction,
                     bins=[-0.01, shell_threshold, core_threshold, 1.01],
                     labels=['cloud', 'shell', 'core'])
    return pd.DataFrame({'fraction': fraction, 'class': classes})


def heaps_law(presence_matrix, n_iters=100):
    '''Estimate Heaps law alpha from genome sampling order.'''
    import numpy as np
    n_strains = presence_matrix.shape[1]
    pan_sizes = []
    for _ in range(n_iters):
        order = np.random.permutation(n_strains)
        pan = set()
        sizes = []
        for i in order:
            genes_in_i = presence_matrix.iloc[:, i] == 1
            pan.update(genes_in_i.index[genes_in_i].tolist())
            sizes.append(len(pan))
        pan_sizes.append(sizes)
    pan_array = np.array(pan_sizes)  # n_iters x n_strains
    n_sampled = np.arange(1, n_strains + 1)
    # Fit log-log
    mean_pan = pan_array.mean(axis=0)
    log_n = np.log(n_sampled)
    log_pan = np.log(mean_pan)
    alpha = np.polyfit(log_n, log_pan, 1)[0]
    return alpha
```

## Minigraph-Cactus for Eukaryotic Pangenome

**Goal:** Build pangenome graph from haplotype-resolved assemblies.

**Approach:** Provide reference + haplotypes -> Minigraph-Cactus produces GFA + VCF + GBZ for downstream genotyping.

```bash
# Prepare seqFile (Cactus convention)
cat > pangenome_seqs.txt << 'EOF'
GRCh38      GRCh38.fa
HG002.hap1  HG002.hap1.fa
HG002.hap2  HG002.hap2.fa
HG003.hap1  HG003.hap1.fa
HG003.hap2  HG003.hap2.fa
EOF

cactus-pangenome jobStore_path pangenome_seqs.txt \
    --outDir hprc_pangenome \
    --outName hprc_pangenome \
    --reference GRCh38 \
    --vcf \
    --gfa \
    --gbz \
    --indexCores 32 \
    --mapCores 32

# Outputs:
#   hprc_pangenome/hprc_pangenome.full.hal      Full Cactus HAL
#   hprc_pangenome/hprc_pangenome.gfa.gz        Graph Fragment Assembly format
#   hprc_pangenome/hprc_pangenome.vcf.gz        Short variants relative to GRCh38
#   hprc_pangenome/hprc_pangenome.gbz           GBZ compressed graph
#   hprc_pangenome/hprc_pangenome.giraffe.gbz   Giraffe-indexed graph for mapping
```

## vg Pangenome Genotyping

**Goal:** Genotype short reads against a pre-built pangenome graph.

**Approach:** Pre-built pangenome -> vg autoindex -> vg giraffe (fast mapping) -> vg call variants.

```bash
# Pre-build index
vg autoindex --workflow giraffe --threads 16 \
    --ref-graph hprc_pangenome.gfa.gz \
    --output hprc_index

# Map reads
vg giraffe \
    --gbz-name hprc_index.giraffe.gbz \
    --dist-name hprc_index.dist \
    --minimizer-name hprc_index.min \
    --fastq-in sample.R1.fq.gz \
    --fastq-in sample.R2.fq.gz \
    --output-format GAM \
    --threads 16 \
    > sample.gam

# Pack alignment information
vg pack -x hprc_index.giraffe.gbz -g sample.gam -o sample.pack

# Call variants
vg call hprc_index.giraffe.gbz -k sample.pack -a > sample.vcf
```

## Pan-GWAS with Scoary

**Goal:** Identify gene presence/absence associated with a phenotype.

**Approach:** Panaroo presence/absence matrix + phenotype file -> Scoary -> phenotype-gene associations.

```bash
# Run Scoary
scoary \
    --gene-presence-absence panaroo_out/gene_presence_absence.csv \
    --traits phenotypes.tsv \
    --output scoary_out \
    --threads 16 \
    --upgma-tree

# Output:
#   scoary_out/*_results.csv   per-trait gene associations
```

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Panaroo accessory >> PPanGGOLiN accessory | Panaroo "accessory" includes singleton; PPanGGOLiN "cloud" is a separate class | Compare strict mode definitions; Panaroo + PPanGGOLiN cross-validate |
| Roary accessory >> Panaroo accessory | Roary annotation-error inflation | Trust Panaroo; Roary deprecated |
| PEPPAN core != Panaroo core | Different clustering thresholds | Panaroo for clonal; PEPPAN for genus-scale; consistent within method |
| Minigraph-Cactus VCF and Cactus pairwise differ | Pangenome integrates SV; pairwise is direct | Minigraph-Cactus for variant-aware pangenome |
| PGGB and Minigraph-Cactus disagree on graph topology | PGGB reference-free; MC reference-anchored | Both valid; report both for transparency |
| Heaps-law alpha differs across resampling | Stochasticity; insufficient sampling | Require > 100 genomes; report 95% CI |
| PanGenie genotype contradicts read-based SV caller | Repetitive region (graph-spaghetti) | Trust read-based for repetitive; PanGenie for unique regions |
| Bakta and Prokka annotation give different gene counts | Different gene-prediction defaults | Use Bakta (GenBank-compliant); document |
| Scoary and pyseer disagree on top genes | Different statistical assumptions | Cross-validate; trust consensus |

**Operational rule for publication:** Bacterial pangenome uses Panaroo + PPanGGOLiN cross-validation; eukaryotic pangenome uses Minigraph-Cactus (HPRC scale) or PGGB (reference-free). Document annotation pipeline + version; report core/shell/cloud at multiple thresholds; verify Heaps-law on > 100 genomes for openness claims.

## Cohort Gotchas

- **Endosymbiont genomes (Buchnera, Wolbachia, mitochondria):** core genome is dominant; accessory is minimal; pangenome analysis less informative
- **Hypothetical proteins:** unknown function genes dominate "accessory" in non-model species; functional analysis needed
- **Phage genes:** prophages contribute to accessory; mask prophages for "core species genes"
- **Mobile genetic elements:** plasmids/IS elements appear in accessory; tag with mobileOG-db
- **Highly recombinogenic species (Neisseria, S. pneumoniae):** core genome unstable; restrict to non-recombinant regions
- **Plasmids:** chromosome vs plasmid distinction matters for pangenome; classify with PlasmidFinder
- **Polyploid eukaryotic pangenome:** subgenomes must be assigned first (see [[whole-genome-duplication]])
- **Pangenome graph for SV detection:** PanGenie + graph aligners; reference-anchored variant callers miss SVs

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Annotation pipeline?" | Bakta 1.10+ on all genomes; consistent settings; BUSCO completeness reported per strain |
| "Why Panaroo over Roary?" | Panaroo's annotation-error correction reduces accessory inflation substantially (nearly an order of magnitude on the Mtb benchmark; Tonkin-Hill 2020) |
| "Tettelin thresholds?" | Reported at multiple thresholds (95%, 99%); PPanGGOLiN HMM partition as cross-validation |
| "Heaps law inference?" | >= 100 genomes; resampling 95% CI reported |
| "Recombination?" | ClonalFrameML applied; recombinant regions masked or analyzed separately |
| "Why Minigraph-Cactus?" | HPRC standard; production-grade for haplotype-resolved pangenomes |
| "Reference bias?" | Reference choice documented; PGGB cross-validation for reference-free comparison |
| "Pan-GWAS multiple testing?" | Bonferroni-corrected across genes; or pyseer with k-mer-based |
| "Open vs closed pangenome?" | Heaps-law alpha reported with CI; openness claim conditional on alpha < 1 |
| "Annotation density consistency?" | BUSCO completeness verified per strain; outliers excluded |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Panaroo "input format error" | GFF3 missing required fields | Verify GFF3 from Bakta has correct attribute fields |
| PPanGGOLiN HDF5 unreadable | Version mismatch | Pin PPanGGOLiN version; rebuild |
| Roary used (legacy script) | Roary deprecated | Migrate to Panaroo |
| PEPPAN OOM | Too many genomes | Reduce to representative subset; or use PEPPAN with chunking |
| Cactus pangenome unrelated to expectation | Wrong seqFile syntax | Tabs not spaces; correct file paths |
| PGGB wfmash hangs | Too many large genomes | Reduce to <= 20 eukaryotic genomes |
| vg autoindex memory error | Insufficient RAM | Increase to 200+ GB; or split by chromosome |
| PanGenie genotype empty | Index mismatch between graph + reads | Re-build vg index with same vg version |
| Scoary "no significant traits" | Few strains or low effect | Increase strains; verify phenotype variance |
| pyseer p-values uniform | Population structure inflation | Use --lmm flag with kinship matrix |
| anvi'o display error | Database version mismatch | Re-create with current anvi'o version |
| Minigraph-Cactus runs but VCF empty | All inputs identical | Verify inputs differ |
| Bakta annotation gives 0 genes | Reference data not configured | Set BAKTA_DB env or use `--db /path` |

## Tool Installation Notes

```bash
# Bacterial pangenome
conda install -c bioconda panaroo ppanggolin peppan get_homologues anvio

# Eukaryotic pangenome
conda install -c bioconda cactus pggb vg pangenie

# PGR-TK (repeat-rich / clinical gene focus)
conda install -c bioconda pgr-tk
# Or: cargo install pgrtk; or Docker quay.io/cschin/pgr-tk
# Note: cschin/pgr-tk archived April 2026; transitioning to PANGEA (developed by DGI / Diploid Genomics; check upstream repo for pointer)

# Annotation
conda install -c bioconda bakta prokka

# Pan-GWAS
conda install -c bioconda scoary pyseer

# Recombination
conda install -c bioconda clonalframeml

# Mobile elements
git clone https://github.com/clb21565/mobileOG-db

# QC
conda install -c bioconda busco compleasm
```

For HPRC-scale eukaryotic pangenome, use cluster with >= 500 GB RAM and HPC scheduler integration via Toil (see [[whole-genome-alignment]]).

## References

- Tettelin H et al 2005 PNAS 102:13950 (core/accessory pangenome framework)
- Tonkin-Hill G et al 2020 Genome Biol 21:180 (Panaroo)
- Gautreau G et al 2020 PLoS Comp Biol 16:e1007732 (PPanGGOLiN)
- Zhou Z et al 2020 Genome Res 30:1667 (PEPPAN)
- Page AJ et al 2015 Bioinformatics 31:3691 (Roary; DEPRECATED)
- Contreras-Moreira B & Vinuesa P 2013 Appl Environ Microbiol 79:7696 (GET_HOMOLOGUES)
- Eren AM et al 2021 Nat Microbiol 6:3 (anvi'o pangenomics)
- Hickey G et al 2024 Nat Biotech 42:663 (Minigraph-Cactus)
- Garrison E et al 2024 Nat Methods 21:2008 (PGGB)
- Sirén J et al 2024 Nat Methods 21:2017 (vg pangenome update)
- Ebler J et al 2022 Nat Genet 54:518 (PanGenie)
- Liao W-W et al 2023 Nature 617:312 (HPRC draft pangenome)
- Brynildsrud O et al 2016 Genome Biol 17:238 (Scoary)
- Lees JA et al 2018 Bioinformatics 34:4310 (pyseer)
- Didelot X & Wilson DJ 2015 PLoS Comp Biol 11:e1004041 (ClonalFrameML)
- Schwengers O et al 2021 Microb Genom 7 (Bakta)
- Vernikos GS et al 2015 Curr Opin Microbiol 23:148 (pangenome openness review)
- Brown CL et al 2022 Appl Environ Microbiol 88:e0099122 (mobileOG-db)
- Mikheenko A et al 2018 Bioinformatics 34:i142 (QUAST-LG; long-read assembly evaluation -- earlier "pangenome review" attribution was incorrect; QUAST-LG benchmarks large-scale assembly QC).
- Chin C-S et al 2023 Nat Methods 20:1213 (PGR-TK; MAP graphs + principal bundle decomposition for repeat-rich / clinical genes; MHC, DAZ1-4, OPN1LW/OPN1MW examples)
- cschin/pgr-tk GitHub (repo; archived April 2026, transitioning to PANGEA developed by DGI / Diploid Genomics; consult upstream README for PANGEA pointer)

## Related Skills

- comparative-genomics/whole-genome-alignment - Minigraph-Cactus builds on Cactus; PGGB underlies eukaryotic pangenome
- comparative-genomics/ortholog-inference - Pangenome clusters are bacterial orthologs at species/genus level
- comparative-genomics/hgt-detection - Accessory genes often HGT-derived; mobile-element annotation cross-references
- comparative-genomics/gene-family-evolution - CAFE5 modeling on Panaroo presence/absence matrix
- genome-annotation/prokaryotic-annotation - Bakta annotation is pangenome input
- genome-annotation/repeat-annotation - Repeat masking before eukaryotic pangenome
- variant-calling/structural-variant-calling - Pangenome graph SV calling complements read-based callers
- variant-calling/joint-calling - vg + graph variant calling integrates with traditional VCF
- metagenomics/amr-detection - AMR genes often in bacterial accessory
- metagenomics/strain-tracking - Strain-specific accessory genes for tracking
- population-genetics/association-testing - Pan-GWAS for phenotype-gene-content association
<!-- END FILE: comparative-genomics/pangenome-analysis/SKILL.md -->

## 子目录：comparative-genomics/positive-selection

<!-- BEGIN FILE: comparative-genomics/positive-selection/SKILL.md -->
---
name: bio-comparative-genomics-positive-selection
description: Detect positive (diversifying / episodic / pervasive) selection using codon dN/dS frameworks. Implements PAML codeml site models (M0/M1a/M2a/M7/M8/M8a), branch models, branch-site model A (Zhang 2005), and HyPhy methods (BUSTED, BUSTED-S, BUSTED-MH, BUSTED-PH, MEME, FEL, FUBAR, aBSREL, SLAC, RELAX, GARD, FUBAR-MH). Includes McDonald-Kreitman framework (asymptotic alpha, impMKT, polyDFE, DFE-alpha, GRAPES) for within-species + divergence inference, RERconverge for trait-correlated rate shifts, CSUBST for convergent substitution, and PhyloAcc for accelerated noncoding evolution. Use when testing adaptive evolution at codons, branches, or full gene; running GARD recombination pre-screen; controlling alignment-error and gBGC false positives; reconciling PAML vs HyPhy results; or performing genome-scale selection scans.
tool_type: mixed
primary_tool: PAML
---

## Version Compatibility

Reference examples tested with: PAML 4.10.7+, HyPhy 2.5.62+ (BUSTED-MH from Lucaci 2023 MBE 40:msad150; FUBAR-MH from same), datamonkey.org 2024+ for web jobs, IQ-TREE 2.3.6+, MACSE V2.07+, PRANK 170427+, MAFFT 7.526+, PREQUAL 1.02+, HmmCleaner 0.243+, GARD (HyPhy bundled), RDP5 5.59+, ete4 4.1.0+, BioPython 1.84+, scipy 1.13+, polyDFE 2.0+, DFE-alpha 2.16+, GRAPES 1.1.1+, RERconverge 0.3.0+, CSUBST 1.6.0+, PhyloAcc 2.4.0+. Quest-for-Selection benchmark refreshed annually.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `codeml` (PAML; check by `codeml /dev/null` -- prints version banner), `hyphy --version`, `gard --help`
- Python: `pip show pyhyphy`; introspect ete4 API for tree-labeling
- R: `packageVersion('RERconverge')`; `?correlateWithBinaryPhenotype`

If code throws `branch-site test LRT non-positive`, `omega2 hit upper bound 999`, `MEME ML mixed gradient`, the most common cause is alignment error or saturated dS -- inspect alignment with TCS / Guidance2 and dS-vs-divergence-time. PAML 4.10 changed several control-file keywords from 4.9 (`getSE = 1` syntax tightened).

# Positive Selection Analysis

**"Is this gene / branch / site under positive selection?"** -> dN/dS (omega = nonsynonymous-to-synonymous substitution rate ratio) framework with explicit choice of WHICH question is being asked (gene-wide / branch-specific / site-specific / episodic) and WHICH null is being rejected. The "test failed because of selection" claim has more known confounders than any other comparative-genomics inference; **mandatory pre-screens are: recombination (GARD), alignment errors (PREQUAL or HmmCleaner), saturation (dS distribution), and gBGC (W->S substitution bias)**. Skipping any one inflates Type-I error to ~20-50% (Anisimova & Yang 2007 MBE 24:1219; Pond 2006 Mol Biol Evol 23:1891).

- CLI: `codeml` PAML site, branch, branch-site models
- CLI: `hyphy busted` `hyphy meme` `hyphy fel` `hyphy fubar` `hyphy absrel` `hyphy relax` `hyphy gard`
- Web: datamonkey.org for HyPhy jobs without local install
- R: `RERconverge::correlateWithBinaryPhenotype()` for trait-rate associations
- CLI: `csubst analyze` for convergent substitution
- R/CLI: `phyloacc` for noncoding accelerated evolution

## Algorithmic Taxonomy

| Method | Question | Null model | Strength | Fails when |
|--------|----------|------------|----------|------------|
| PAML codeml M0 (Yang 1997 CABIOS 13:555) | Gene-wide single-omega estimate | -- (point estimate) | Standard reference omega; baseline test | Site heterogeneity (use M3+) |
| codeml M1a vs M2a (Yang 2000 Genetics 155:431) | Any site under selection? | Nearly neutral, 2-category | Conservative; LRT df=2 | Low power for episodic selection |
| codeml M7 vs M8 | More-sensitive site test | Beta(0,1) | Higher power than M1a/M2a | Higher false-positive rate; relaxed-constraint mimics selection |
| codeml M8 vs M8a (Swanson 2003 MBE 20:18) | Conservative site test (omega2 = 1 null) | Beta + omega2=1 | Cleanest LRT df=1; preferred site test | Lower power than M7 vs M8 |
| codeml branch-site mod A (Zhang 2005 MBE 22:2472) | Selection on pre-specified foreground branch | A1 (omega2=1 fixed) | Most powerful for episodic per-branch selection | Foreground specified post hoc -> Type-I inflation |
| codeml clade model (Bielawski & Yang 2004 J Mol Evol 59:121) | Different omega between named clades | M3 with shared categories | Tests for shifted selection regime | Requires clade pre-specification |
| codeml free-ratio | Per-branch omega estimates (exploratory) | M0 | Visualizes branch-wise variation | Unidentifiable for short branches; no formal LRT |
| HyPhy BUSTED (Murrell 2015 MBE 32:1365) | Any episodic selection on any branch site? | No omega+ class | Site + branch joint; foreground assignable | Sensitive to alignment errors |
| HyPhy BUSTED-S (Wisotsky 2020 MBE 37:2430) | BUSTED with synonymous-rate variation | -- | Corrects for SRV; reduces false positives | Slightly less power than BUSTED |
| HyPhy BUSTED-MH (Lucaci 2023 MBE 40:msad150) | BUSTED with multi-nucleotide substitutions | -- | Captures complex (multi-hit) substitutions; reduces false positives from MNMs | Newer; limited benchmarking |
| HyPhy BUSTED-PH | Two phenotypes; selection on one not other | -- | Tests phenotype-specific selection | Requires phenotype branch label |
| HyPhy MEME (Murrell 2012 PLoS Genet 8:e1002764) | Per-site episodic selection | FEL | Detects sites under episodic positive selection | Higher false-positive rate at p threshold |
| HyPhy FEL (Kosakovsky Pond 2005 MBE 22:1208) | Per-site pervasive selection | -- | Fast; counts substitutions per site | No episodic detection |
| HyPhy FUBAR (Murrell 2013 MBE 30:1196) | Bayesian per-site pervasive selection | -- | Scales to 1000s of sequences; posterior probability | No episodic detection |
| HyPhy SLAC | Counting-based fast estimator | -- | Very fast; rough estimate | Lower power; no statistical model |
| HyPhy aBSREL (Smith 2015 MBE 32:1342) | Branch-specific selection without pre-specification | -- | Adaptive per-branch omega categories; corrects multiple testing | Multiple-testing burden across many branches |
| HyPhy RELAX (Wertheim 2015 MBE 32:820) | Selection relaxation (k<1) or intensification (k>1) | -- | Detects RELAXED selection; cannot be done by other tests | Not designed for adaptive evolution per se |
| HyPhy GARD (Pond 2006 MBE 23:1891) | Recombination breakpoint detection | No recombination | MANDATORY pre-screen for any selection test | Computationally heavy; > 50 sequences slow |
| McDonald-Kreitman (McDonald & Kreitman 1991 Nature 351:652) | Adaptive substitution rate alpha from poly + div data | Neutral mutation accumulation | Per-gene alpha; population genetics native | Slightly deleterious bias (downward); fixed by asymptotic alpha |
| Asymptotic alpha (Messer & Petrov 2013 PNAS 110:8615) | MK with slightly deleterious correction | -- | Unbiased alpha; works at low MAF SFS | Requires SFS data |
| impMKT (Murga-Moreno 2022 G3 12:jkac206) | MK with conservative imputation | -- | Gene-level evidence; faster than alpha asymptotic | Less unbiased than asymptotic alpha |
| polyDFE (Tataru & Bataillon 2019 Bioinformatics 35:2868) | Full DFE + alpha jointly | -- | Quantifies the distribution of fitness effects | Computational cost; requires polymorphism data |
| DFE-alpha (Eyre-Walker & Keightley 2009 MBE 26:2097) | Faster DFE method | -- | Standard DFE inference; many simulated DFEs | Requires demographic correction |
| GRAPES (Galtier 2016 PLoS Genet 12:e1005774) | DFE on neutral + selected sites | -- | Joint demography + alpha; robust | Genome-scale dataset required |
| RERconverge (Kowalczyk 2019 Bioinformatics 35:4815; Redlich 2024 MBE 41:msae210) | Relative-rate shifts correlated with categorical phenotype | -- | Phylogenome-wide trait associations | Inherits all dN/dS confounders |
| CSUBST (Fukushima & Pollock 2023 Nat Eco Evo 7:155) | Convergent substitutions across independent lineages | -- | Combinatorial-substitution omegaC ratio; null-corrected | Requires multi-clade dataset |
| PhyloAcc (Hu 2019 MBE 36:1086; Thomas 2024) | Bayesian convergent accelerated noncoding rate | -- | For noncoding elements (CNEs); convergent rate shifts | CDS analyses prefer codon-based methods |
| phyloP (Pollard 2010 GR 20:110) | Per-site noncoding rate test | -- | Simple; widely used for noncoding | No convergence; site-by-site |
| PRANK + codeml pipeline | Codon-aware MSA + codeml | -- | Standard publication-grade workflow | Slow for large datasets |

Methodology evolves; verify the latest HyPhy / PAML manuals and the Álvarez-Carretero "Beginner's Guide" (Álvarez-Carretero et al 2023 MBE 40:msad041) before locking on a single method. The BUSTED-MH and FUBAR-MH (multi-hit) extensions specifically address known Type-I inflation from multi-nucleotide substitutions and are now recommended over basic BUSTED / FUBAR.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Single gene, mammalian (~60 Myr), pre-specified foreground branch | codeml branch-site mod A AND HyPhy aBSREL on foreground | Mutual validation; mod A LRT df=1 + aBSREL adaptive site classes |
| Single gene, deep eukaryote (~500+ Myr), no foreground hypothesis | GARD pre-screen -> BUSTED-MH gene-wide -> MEME for sites | Episodic-selection-only methods; saturation-aware (HyPhy under MG94 codon model) |
| Genome-wide scan, vertebrates | codeml M7 vs M8 OR HyPhy FUBAR-MH per gene; FDR-correct | Pervasive-selection sites; multi-hit correction critical at scale |
| Episodic selection scan | HyPhy MEME genome-wide (per gene); FDR-correct | Site-level episodic detection |
| Branch-specific selection on unspecified branches | HyPhy aBSREL | Adaptive per-branch test with built-in multiple-testing |
| Comparing selection regimes between two phenotypes | HyPhy BUSTED-PH or RELAX | Phenotype-specific or relaxation-detection |
| Recently diverged species (low divergence) | MK / asymptotic alpha (population genetics) | Codon dN/dS unreliable at low divergence; SFS-based instead |
| Within-species, dense polymorphism + divergence | polyDFE / GRAPES / asymptotic-MK | Full DFE + alpha jointly; preferred for adaptive-substitution rate |
| Coding selection genome-wide, with SFS available | grapes -m AUTO_ALL | Demography-aware alpha; standard population-genetics-aware adaptive-substitution scan |
| Noncoding accelerated evolution (CNEs / ECRs) | PhyloAcc, phyloP-acc | Codon-based unsuitable; PhyloAcc Bayesian convergence |
| Convergent substitutions across independent lineages | CSUBST | Combinatorial-substitution omegaC; null-corrected |
| Trait-correlated rate shifts genome-wide | RERconverge | Categorical / binary phenotype; correlates RERs across thousands of genes |
| Suspected positive selection but dS > 2 | Use protein-level method or reduce taxon sampling | Codon-based methods unreliable at saturation; protein-only ASR can still work |
| Recombination expected (immune genes, viral genomes) | GARD pre-screen mandatory | Recombination + tree-based selection -> false positives (Anisimova 2003) |
| Convergent codon substitution at specific sites | TDG09 (Tamuri 2009) or PCOC (Rey 2018) | TDG09 detects site-specific shifts in selective constraint between trait-defined lineage groups; PCOC detects convergent amino-acid substitution |
| Drug-target evolution screen | aBSREL on candidate genes; cross-validate with MEME | Recent positive selection at drug-target loci |
| Pathogen / immune-evasion gene with high dS variation | BUSTED-S (synonymous rate variation aware) | dS variation across sites violates basic BUSTED assumptions |
| Plasmodium / Trypanosoma / Plasmid analysis | BUSTED-MH (multi-hit aware) | Multi-nucleotide substitutions common in these; basic BUSTED inflates false positives |

## Per-Method Failure Modes

### Recombination producing false positive selection

**Trigger:** Running codeml or BUSTED on a gene with recombination breakpoints (viral genes, immune genes, paralog families).

**Mechanism:** All single-tree codon models assume one phylogeny across all sites. Recombination produces different trees for different segments; treating them as one tree forces the model to invent rate variation that mimics positive selection (Anisimova et al 2003 Genetics 164:1229).

**Symptom:** PAML M8 strongly rejects M7 (LRT > 50), with omega2 = 999 (PAML upper bound) at several "selected sites"; HyPhy BUSTED highly significant; sites clustered in specific gene regions.

**Fix:** **MANDATORY: run GARD before any positive selection test.** If GARD detects breakpoints (p < 0.05), partition the alignment at breakpoints and analyze each segment separately, or use the recombination-aware MEME with the partitioned tree set. RDP5 (Martin 2021 Virus Evol 7:veaa087) is an alternative for viral genomes. GARD output `.json` lists breakpoint positions and posterior support.

### Alignment errors producing false positives

**Trigger:** Using default MAFFT or MUSCLE alignment on divergent CDS sequences; skipping codon-aware aligner.

**Mechanism:** Frame-shifted or misaligned codons introduce apparent non-synonymous substitutions at every position; codon-aware tools see these as positive selection (Schneider 2009 GBE 1:114; Markova-Raina & Petrov 2011 GR 21:863).

**Symptom:** "Selected sites" cluster in alignment regions with > 30% gaps; per-site posteriors in BEB / FUBAR concentrate in ambiguous columns; PREQUAL or Guidance2 marks these regions as poorly aligned; protein alignment shows obvious mismatches.

**Fix:** Use codon-aware aligner: **PRANK** (Loytynoja 2014 Methods Mol Biol 1079:155) is the standard for selection analysis (correctly models insertions); MACSE V2 (Ranwez 2018 MBE 35:2582) handles frameshifts and pseudogenes natively; OMM_MACSE wrapper combines them. After alignment, filter with PREQUAL (segment-level) or HmmCleaner (Di Franco 2019 BMC Evol Biol 19:21); do NOT use block-filtering (Gblocks, trimAl) which removes informative sites. Segment-level filtering preferred for selection (Di Franco 2019).

### Saturated synonymous sites

**Trigger:** Comparing distantly related taxa (deep eukaryotic divergence, > 100 Myr); dS > 3 across most pairs.

**Mechanism:** Synonymous sites have undergone multiple substitutions; the observed dS underestimates true dS. The model can't recover the true rate; omega = dN/dS becomes unstable at the upper bound or low (depending on which direction the bias goes).

**Symptom:** PAML M0 omega = 999 or near-zero; per-branch dS variance huge; sites with omega > 1 in M8 BEB are at conserved residues (paradox).

**Fix:** Reduce taxon sampling to species with dS < 2 on internal branches. For deep selection inference on conserved residues, use protein-level methods (BUSTED with `--model GTR` AA codon translation; aBSREL with protein model option) or restrict to subclade with reasonable saturation. Yang 2007 PAML manual recommends dS < 1.5 per branch.

### gBGC inflating apparent positive selection

**Trigger:** Mammalian / vertebrate gene with W->S substitution bias on a fast-evolving lineage.

**Mechanism:** GC-biased gene conversion fixes A/T -> G/C alleles preferentially in regions of high recombination, independent of selection (Galtier & Duret 2007 Trends Genet 23:273; Capra 2013 PLoS Genet 9:e1003684). Standard codon models attribute this to positive selection because nonsynonymous substitutions are unequally distributed across codon positions.

**Symptom:** Branch with apparent positive selection sits in high-recombination region; W->S / S->W substitution ratio > 1.5; selected sites concentrate at non-degenerate codon positions; HyPhy MEME-MH and BUSTED-MH attribute signal to multi-hit rather than positive selection.

**Fix:** Test for gBGC: W->S substitution rates on selected branch / S->W rates; report ratio. Re-run selection analysis with HyPhy BUSTED-MH (multi-hit aware); if signal vanishes, the original "selection" was gBGC + multi-hit substitutions. For genome-wide scans, mask sub-telomeric / high-recombination regions.

### Branch-site test foreground specification

**Trigger:** Running codeml branch-site mod A after looking at the data to choose foreground branch.

**Mechanism:** The branch-site test is designed for a single a priori foreground; post hoc specification inflates Type-I by ~5x because the choice was informed by the data.

**Symptom:** Branch-site test highly significant for the "interesting" branch; aBSREL on same data shows no significant branch (aBSREL has built-in multiple-testing correction).

**Fix:** Specify foreground branches in registered protocol before looking at data. For exploratory branch-wise analysis, use aBSREL (Smith 2015 MBE 32:1342) which adaptively assigns branch-specific omega classes with multiple-testing built in. If branch-site test was post hoc, apply Bonferroni correction across all branches tested + report explicitly.

### LRT critical value confusion

**Trigger:** Computing branch-site test p-value using standard chi-square df=2.

**Mechanism:** The branch-site test compares mod A (4 omega classes) against mod A1 (omega2 fixed at 1). The LRT statistic distribution is a 50:50 mixture of point-mass-at-0 and chi-square(df=1), not chi-square(df=2) (Self & Liang 1987 JASA 82:605; Zhang 2005 MBE 22:2472; Wong 2004 Genetics 168:1041). Using df=2 makes the test conservative; using df=1 standard makes it anticonservative.

**Symptom:** Branch-site p-values incorrectly inflated or deflated; users report finding selection at very stringent thresholds.

**Fix:** Use the 50:50 mixture critical value: 2.71 at p=0.05 (NOT 3.84). PAML's `chi2 1 LRT` command applies the mixture. Many published applications use chi-square df=2 conservatively, which loses power but doesn't inflate; chi-square df=1 directly is wrong and inflates Type-I.

### omega2 hitting upper bound (999)

**Trigger:** PAML codeml output shows omega2 = 999 for an "under selection" site class.

**Mechanism:** PAML codeml uses an internal upper bound of 999 (= "infinity" in single precision). Hitting it indicates numerical issue: extremely few synonymous sites in the selected class, dS underestimation, or numerical optimization failure.

**Symptom:** Sites flagged as positive selection have omega2 = 999; BEB posteriors for those sites are weirdly distributed.

**Fix:** Re-run with multiple starting values of omega (`fix_omega=0`, vary `omega = 0.1, 0.5, 1.0, 2.0, 5.0` across runs); check that all converge to same omega. Inspect alignment at flagged sites for unusual residue conservation. If omega = 999 persists, the gene may have rare-substitution patterns; switch to BUSTED-MH which accounts for multi-hit substitutions.

### Multiple-testing burden in genome scans

**Trigger:** Running selection tests across thousands of genes without correction.

**Mechanism:** With ~5000 protein-coding genes in a typical analysis, 250 will be significant at p=0.05 under H0. The false-discovery rate without correction is 50%.

**Symptom:** Implausibly large gene lists "under selection"; functional categories enriched are non-specific (e.g. all immune genes by FDR).

**Fix:** Apply FDR correction (Benjamini-Hochberg). Genes in syntenic regions are non-independent; use Benjamini-Yekutieli for stronger control under dependence. For HyPhy site-level methods, the per-site p < 0.1 default is a starting point; multiple-test correction within a gene is typically not applied (sites within a gene are dependent), but cross-gene correction is necessary. Holm-Bonferroni for strict Type-I.

### Convergent substitution misinterpreted as positive selection

**Trigger:** Lineage-specific selection found at a residue that has independently changed in multiple unrelated lineages.

**Mechanism:** Convergent substitutions at the same site in independent lineages produce signals in branch-site and other tests; this is convergence, not adaptive evolution per se (though convergent residues often ARE adaptive).

**Symptom:** Same residue flagged in multiple unrelated lineages by branch-site test; alignment shows convergent substitutions.

**Fix:** Switch from selection test to convergence test: CSUBST (Fukushima & Pollock 2023 Nat Eco Evo 7:155) for combinatorial substitution analysis; RERconverge (Redlich 2024 MBE 41:msae210) for relative-rate-vs-phenotype across categorical traits; PCOC (Rey 2018) for biophysical convergence. Report both convergence test and selection test results.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| dN/dS interpretation | omega < 1 purifying; omega = 1 neutral; omega > 1 positive (per site, branch, or gene depending on model) | Yang & Bielawski 2000 TREE 15:496; foundational |
| Branch-site test LRT critical value | 2.71 at p=0.05 (50:50 mixture chi^2) | Self-Liang 1987 JASA 82:605; Zhang 2005 MBE 22:2472 |
| Site-level p-value default | p <= 0.1 (FEL, MEME, FUBAR); FUBAR posterior >= 0.9 | Murrell 2012/2013; Datamonkey conventions |
| BEB posterior probability | >= 0.95 significant; >= 0.99 highly significant | Yang & Bielawski 2000 |
| dS upper limit for reliability | dS < 1.5 per branch; dS < 3 overall | Yang 2007 PAML manual |
| Minimum sequences for codeml | >= 8 with sufficient divergence | Anisimova et al 2001 MBE 18:1585 |
| Branch-site test minimum lineages | >= 20 in tree; >= 4 background branches | Yang 2007 |
| GARD breakpoint significance | p < 0.05 to partition alignment | Pond 2006; mandatory pre-screen |
| MK alpha threshold | alpha > 0 indicates adaptive substitutions; report 95% CI | Smith & Eyre-Walker 2002 |
| Asymptotic alpha minimum SFS density | >= 50 sites per frequency bin | Messer & Petrov 2013 |
| FDR genome-wide selection scan | q < 0.05 Benjamini-Hochberg | Standard |
| MEME minimum site-level support | p < 0.1; +/-3 sequences with substitutions | Murrell 2012 |
| aBSREL p-value | p < 0.05 (corrected by Holm-Bonferroni internally) | Smith 2015 |
| RELAX k interpretation | k < 1 relaxed; k > 1 intensified | Wertheim 2015 |
| Codon usage bias ENC | ENC < 35 high bias; consider effect on dS | Wright 1990 Gene 87:23 |
| W->S substitution ratio for gBGC | > 1.5 suggests gBGC | Operational convention |
| BUSTED-MH multi-hit threshold | omega_DH > 1 indicates multi-hit pattern | Lucaci 2023 |
| HyPhy SRV (Synonymous Rate Variation) | Use BUSTED-S when dS varies across sites > 2x | Wisotsky 2020 |

## Selection Scan Standard Pipeline

**Goal:** Test all coding genes in a clade for evidence of positive selection, with full quality control.

**Approach:** Align with PRANK -> filter with PREQUAL -> pre-screen with GARD -> run BUSTED-MH (gene-wide) + MEME (sites) + aBSREL (branches); FDR-correct across genes; verify top candidates pass alignment / saturation / gBGC checks.

```bash
# Per-gene pipeline (parallelizable)
for og in orthogroups/*.fa; do
    base=$(basename $og .fa)

    # 1. Codon-aware MSA
    prank -d=$og -o=msa/$base.prank -codon -F

    # 2. Filter alignment errors (segment-level)
    PREQUAL -i msa/$base.prank.best.fas -o msa_filt/$base

    # 3. Recombination pre-screen
    hyphy gard --alignment msa_filt/$base.filtered --output gard/$base.json
    # If breakpoints found: partition and treat per-segment

    # 4. Gene-wide test (multi-hit aware)
    hyphy busted --alignment msa_filt/$base.filtered \
        --tree species_tree.nwk --output busted_mh/$base.json \
        --srv Yes --multiple-hits Double+Triple

    # 5. Site-level
    hyphy meme --alignment msa_filt/$base.filtered \
        --tree species_tree.nwk --output meme/$base.json

    # 6. Branch-level
    hyphy absrel --alignment msa_filt/$base.filtered \
        --tree species_tree.nwk --output absrel/$base.json
done

# 7. Aggregate and FDR
python aggregate_selection_scan.py busted_mh/ meme/ absrel/ > selection_results.tsv
```

```python
'''Aggregate genome-wide selection scan results; FDR-correct.'''
import json, glob, pandas as pd
from scipy.stats import false_discovery_control

def parse_busted(p):
    d = json.load(open(p))
    return {'p_value': d.get('test results', {}).get('p-value'),
            'LRT': d.get('test results', {}).get('LRT'),
            'omega_DH': d.get('fits', {}).get('Unconstrained model', {}).get('omega3')}

def count_meme_sig(p, alpha=0.1):
    d = json.load(open(p))
    mle = d.get('MLE', {}).get('content', {}).get('0', {})
    headers = [h[0] for h in d.get('MLE', {}).get('headers', [[]])]
    pi = headers.index('p-value') if 'p-value' in headers else -1
    return sum(1 for v in mle.values() if pi >= 0 and v[pi] < alpha)

rows = []
for path in glob.glob('busted_mh/*.json'):
    gene = path.split('/')[-1].replace('.json', '')
    rows.append({'gene': gene, **parse_busted(path),
                 'meme_sig_sites': count_meme_sig(f'meme/{gene}.json')})
df = pd.DataFrame(rows)
df['busted_fdr'] = false_discovery_control(df['p_value'].fillna(1.0), method='bh')
df['adaptive'] = (df['busted_fdr'] < 0.05) & (df['meme_sig_sites'] > 0)
df.sort_values('busted_fdr').to_csv('selection_results.tsv', sep='\t', index=False)
```

## PAML Branch-Site Test (Operational)

**Goal:** Test for episodic positive selection on a pre-specified foreground branch.

**Approach:** Mark foreground in newick (`#1`) -> codeml branch-site mod A vs A1 -> LRT against 50:50 mixture chi^2(0):chi^2(1).

```bash
# Mark foreground branch: use ete4 or manually
python -c "
from ete4 import Tree
t = Tree('species_tree.nwk', format=1)
target = t.search_nodes(name='target_species')[0]
target.name = target.name + ' #1'
print(t.write(format=1))
" > foreground.nwk

# Branch-site mod A (alternative)
cat > codeml_modA.ctl << 'EOF'
seqfile = alignment.phy
treefile = foreground.nwk
outfile = mod_A.mlc
runmode = 0
seqtype = 1
CodonFreq = 2
model = 2
NSsites = 2
fix_kappa = 0
kappa = 2
fix_omega = 0
omega = 0.4
RateAncestor = 1
cleandata = 0
EOF
codeml codeml_modA.ctl

# Null model A1 (omega_2 = 1)
cp codeml_modA.ctl codeml_modA1.ctl
sed -i 's/^omega = 0.4/omega = 1/' codeml_modA1.ctl
sed -i 's/^fix_omega = 0/fix_omega = 1/' codeml_modA1.ctl
sed -i 's/outfile = mod_A.mlc/outfile = mod_A1.mlc/' codeml_modA1.ctl
codeml codeml_modA1.ctl
```

```python
'''Branch-site test LRT with 50:50 mixture critical value.'''
from scipy.stats import chi2

def branch_site_lrt(lnL_alt, lnL_null):
    lrt = 2 * (lnL_alt - lnL_null)
    if lrt <= 0:
        return {'LRT': lrt, 'p_value': 0.5}
    # 50:50 mixture of chi^2(0) and chi^2(1)
    p = 0.5 * (1 - chi2.cdf(lrt, df=1))
    return {'LRT': lrt, 'p_value': p}
```

Foreground branch must be specified before viewing data; for genome-wide screens with no a priori branch, use aBSREL instead. Bayes Empirical Bayes (BEB) sites with posterior > 0.95 on positive-selection class are the per-site call.

## McDonald-Kreitman with Asymptotic Alpha

**Goal:** Estimate adaptive substitution rate alpha = 1 - (Ds Pn) / (Dn Ps), corrected for slightly deleterious bias.

**Approach:** Compute counts of synonymous and nonsynonymous polymorphisms (P) and divergences (D); fit asymptotic alpha by binning by minor-allele frequency and extrapolating.

```r
# Standard MK
mk_alpha <- function(Dn, Ds, Pn, Ps) {
    1 - (Ds * Pn) / (Dn * Ps)
}

# Asymptotic alpha via the Messer-Petrov 2013 web tool
# (https://benhaller.com/messerlab/asymptoticMK.html) or the impMKT R package
# (Murga-Moreno 2022 G3 12:jkac206) which wraps the asymptotic computation.
library(impMKT)
# Inputs: per-frequency-bin (Pn, Ps) plus genome-wide (Dn, Ds)
freq_bins <- seq(0.01, 0.5, 0.01)
pn_by_freq <- c(...)  # nonsyn polymorphism count per bin
ps_by_freq <- c(...)  # syn polymorphism count per bin
fit <- asymptoticMK(
    Dn = total_dn, Ds = total_ds,
    Pn = pn_by_freq, Ps = ps_by_freq,
    x = freq_bins
)
fit$alpha_asymptotic       # adaptive substitution rate, corrected
fit$alpha_original         # original MK (biased)
```

For full DFE inference (alpha + distribution of fitness effects), use polyDFE (Tataru-Bataillon 2019):

```bash
polyDFE -d data.txt -m C -i estimates.init -o output_basename
```

DFE-alpha (Eyre-Walker 2009) and GRAPES (Galtier 2016) are alternatives; GRAPES is most robust for genome-wide adaptive-substitution scans.

## RERconverge for Trait-Correlated Rate Shifts

**Goal:** Identify genes whose evolutionary rate correlates with a binary or categorical phenotype across the species tree.

**Approach:** Compute per-gene relative evolutionary rates -> correlate against phenotype -> Bonferroni or FDR-correct across genes.

```r
library(RERconverge)

# Read alignments and tree
trees <- readTrees('orthogroup_trees.txt', minSpecies = 10)
rer <- getAllResiduals(trees, useSpecies = species_names, transform = 'sqrt',
                       weighted = TRUE, scale = TRUE)

# Define binary phenotype (e.g., echolocation in mammals)
phen_paths <- foreground2Paths(c('Bat1', 'Bat2', 'Dolphin'), trees, clade = 'terminal')
phen_vec <- foreground2Tree(c('Bat1', 'Bat2', 'Dolphin'), trees, clade = 'terminal')

# Correlate
cors <- correlateWithBinaryPhenotype(rer, phen_paths, min.sp = 10, min.pos = 2,
                                      weighted = 'auto')
top_genes <- cors[order(cors$P), ][1:50, ]
```

For categorical traits (more than binary), Redlich 2024 MBE 41:msae210 extends RERconverge.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| codeml M8 significant, BUSTED null | M8 vs M7 inflated by relaxed constraint mimicking selection | Trust BUSTED; check M8a vs M8 instead (stricter null) |
| codeml branch-site significant, aBSREL null | Branch-site test foreground post hoc | aBSREL with built-in multiple-testing is correct; downgrade claim |
| BUSTED significant, MEME no sites | Episodic at sites BUSTED can't pinpoint; or basic BUSTED detected SRV not selection | Run BUSTED-S; if signal vanishes, was SRV; if persists, gene-wide episodic |
| MEME positive, FEL null | Episodic selection (MEME-specific) | Trust MEME for episodic; FEL only detects pervasive |
| Multiple tests positive at same site | High-confidence site under selection | Report; consider experimental validation |
| Test positive but PREQUAL flagged 20% of alignment | Alignment artifact | Re-filter (HmmCleaner); re-test; downgrade if positive site is in filtered region |
| Test positive but in high-recombination region | gBGC | W->S substitution test; if gBGC-attributable, downgrade |
| BUSTED-MH null where BUSTED significant | Multi-hit substitutions misattributed | Trust BUSTED-MH; original positive was multi-hit pattern |
| RELAX k > 1 with branch-site test null | Selection regime intensification (more purifying) | RELAX captures regime shift; branch-site missed because foreground different |
| Branch-site significant on Drosophila branch but no signal in mammals | Lineage-specific adaptation; or dS saturation in mammals | Inspect dS distribution; if mammals dS < 0.5 across branch, signal is real; if dS > 2, saturation explanation |
| asymptotic alpha < 0 | DFE has high deleterious load; or demographic violation | Check polyDFE / GRAPES with demographic correction |

**Operational rule for publication:** GARD pre-screen documented as negative + PREQUAL/HmmCleaner filtering applied + dS < 1.5 per branch + W->S ratio not elevated + BUSTED-MH significant (gene-wide) + MEME flags sites + aBSREL flags branches with consistent direction = publication-ready evidence. Single-method significance (especially M8 vs M7 alone) should be downgraded.

## Cohort Gotchas

- **Immune / MHC loci:** intra-genic recombination is high; GARD pre-screen mandatory; high apparent positive selection often reflects gene conversion between alleles, not adaptive change
- **Viral genomes:** rapid evolution + recombination + multi-hit substitutions common; BUSTED-MH and FUBAR-MH essential; use RDP5 for recombination detection
- **Plasmodium / Trypanosoma:** high codon-usage bias and multi-hit substitutions; use BUSTED-MH and BUSTED-S
- **Mammalian X-chromosome:** higher dS than autosomes (male-driven evolution); gBGC asymmetry by chromosome; reduce dS threshold for X-linked genes
- **Recent human / population genetics:** dS dramatically underestimated at recent divergence; use SFS-based methods (asymptotic alpha, polyDFE)
- **Convergent evolution traits (echolocation, marine):** RERconverge / CSUBST / PhyloAcc-noncoding designed for these; codon-based methods alone miss the convergent signal

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "GARD pre-screen?" | Yes; no breakpoints (or partitioned at p < 0.05 breakpoints); per-segment results consistent |
| "Alignment filtering?" | PRANK codon-aware MSA; PREQUAL segment filter applied; Guidance2 scores reported |
| "Saturation?" | dS distribution shown; max per-branch dS < 1.5; analysis restricted to subclades meeting this |
| "Branch-site test foreground post hoc?" | Foreground pre-registered OR exploratory analysis acknowledged + aBSREL with built-in multiple-testing used |
| "Multiple-testing correction?" | FDR (Benjamini-Hochberg) across genes; per-site within gene not corrected (dependence) |
| "gBGC?" | W->S substitution ratio not elevated; non-sub-telomeric; BUSTED-MH null in candidates rules out |
| "Multi-hit?" | BUSTED-MH used; if signal persists, robust to multi-hit confounder |
| "Why this LRT df?" | Branch-site test uses 50:50 mixture (Self-Liang 1987; Zhang 2005); critical value 2.71 at p=0.05 |
| "Sensitivity to model choice?" | Cross-validated PAML vs HyPhy; consistent across both; reported both p-values |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| codeml runs but rst file empty | `RateAncestor = 0` or path not writable | Set `RateAncestor = 1`; check output directory |
| codeml omega2 = 999 | Numerical pathology / saturated dS | Vary starting omega; reduce taxon sampling to dS < 2 |
| codeml LRT negative (-0.001) | Numerical noise at convergence | Round; treat as no signal; rerun with different starting values |
| HyPhy "tree branches don't match alignment" | Mismatched taxa names | Use exact same labels in tree and alignment |
| HyPhy MEME returns "no sites significant" | High alignment uncertainty; or no episodic selection | Re-filter alignment; try BUSTED-S for gene-wide signal |
| GARD takes forever | > 50 sequences | Reduce to representative subset; or use RDP5 for viral data |
| MK alpha negative | Demographic issue or DFE has many slightly deleterious | Use polyDFE / GRAPES with demography correction |
| RERconverge "too few species per gene" | Stringent default | Reduce `min.sp = 5`; document |
| CSUBST omega_C unstable | Few combinations; small clade | Need >= 5 clades for stable convergence estimate |
| PhyloAcc convergence failure | Insufficient lineages | Re-run with relaxed prior; check input MAF distribution |

## Tool Installation Notes

```bash
conda install -c bioconda paml hyphy gard prank prequal hmmcleaner
# RDP5: http://web.cbio.uct.ac.za/~darren/rdp.html
# MACSE V2: wget https://bioweb.supagro.inra.fr/macse/releases/macse_v2.07.jar
pip install ete4 pyhyphy csubst
Rscript -e "install.packages(c('asymptoticMK', 'polyDFE'))"
Rscript -e "remotes::install_github('nclark-lab/RERconverge')"
# polyDFE / GRAPES / DFE-alpha source binaries at respective github / bioconda channels
```

For genome-wide scans (> 5000 genes), parallelize per-gene analyses with Snakemake / Nextflow.

## References

- Yang Z 1997 CABIOS 13:555 (PAML codeml)
- Yang Z et al 2000 Genetics 155:431 (codon models M0-M8)
- Yang Z & Bielawski JP 2000 TREE 15:496 (codon model framework)
- Zhang J et al 2005 MBE 22:2472 (branch-site mod A); Wong WSW et al 2004 Genetics 168:1041 (LRT mixture); Self SG & Liang K-Y 1987 JASA 82:605 (LRT boundary)
- Swanson WJ et al 2003 MBE 20:18 (M8a null); Bielawski JP & Yang Z 2004 J Mol Evol 59:121 (clade models)
- Anisimova M & Yang Z 2007 MBE 24:1219 (multiple-testing / branch-site power); Anisimova M et al 2003 Genetics 164:1229 (recombination FP); Anisimova M, Bielawski JP & Yang Z 2001 MBE 18:1585 (LRT power)
- Pond SLK et al 2006 MBE 23:1891 (GARD); Martin DP et al 2021 Virus Evol 7:veaa087 (RDP5)
- Kosakovsky Pond SL & Frost SDW 2005 MBE 22:1208 (FEL); Murrell B et al 2012 PLoS Genet 8:e1002764 (MEME); Murrell B et al 2013 MBE 30:1196 (FUBAR)
- Murrell B et al 2015 MBE 32:1365 (BUSTED); Wisotsky SR et al 2020 MBE 37:2430 (BUSTED-S); Lucaci AG et al 2023 MBE 40:msad150 (BUSTED-MH)
- Smith MD et al 2015 MBE 32:1342 (aBSREL); Wertheim JO et al 2015 MBE 32:820 (RELAX)
- McDonald JH & Kreitman M 1991 Nature 351:652 (MK); Smith NGC & Eyre-Walker A 2002 Nature 415:1022 (alpha); Messer PW & Petrov DA 2013 PNAS 110:8615 (asymptotic alpha)
- Murga-Moreno J et al 2022 G3 12:jkac206 (impMKT); Tataru P & Bataillon T 2019 Bioinformatics 35:2868 (polyDFE); Eyre-Walker A & Keightley PD 2009 MBE 26:2097 (DFE-alpha); Galtier N 2016 PLoS Genet 12:e1005774 (GRAPES)
- Galtier N & Duret L 2007 Trends Genet 23:273 (gBGC); Capra JA et al 2013 PLoS Genet 9:e1003684 (gBGC genome-scale)
- Schneider A et al 2009 GBE 1:114 + Markova-Raina P & Petrov D 2011 GR 21:863 (alignment-error FP)
- Loytynoja A 2014 Methods Mol Biol 1079:155 (PRANK); Ranwez V et al 2018 MBE 35:2582 (MACSE V2); Whelan S et al 2018 Bioinformatics 34:3929 (PREQUAL); Di Franco A et al 2019 BMC Evol Biol 19:21 (HmmCleaner)
- Yang Z 2007 PAML manual; Álvarez-Carretero S et al 2023 MBE 40:msad041 (Beginner's Guide PAML)
- Kowalczyk A et al 2019 Bioinformatics 35:4815 + Redlich R et al 2024 MBE 41:msae210 (RERconverge)
- Fukushima K & Pollock DD 2023 Nat Eco Evo 7:155 (CSUBST); Hu Z et al 2019 MBE 36:1086 (PhyloAcc); Pollard KS et al 2010 GR 20:110 (phyloP); Rey C et al 2018 MBE 35:2296 (PCOC)

## Related Skills

- comparative-genomics/ortholog-inference - Single-copy ortholog alignments as input
- comparative-genomics/ancestral-reconstruction - Branch-specific ancestral sequence inference
- comparative-genomics/gene-tree-species-tree-reconciliation - Reconciled gene trees as PAML input
- alignment/multiple-alignment - PRANK / MACSE codon-aware MSA
- alignment/alignment-trimming - PREQUAL / HmmCleaner segment filtering
- phylogenetics/modern-tree-inference - Tree inference required for codeml
- population-genetics/selection-statistics - SFS-based alpha + DFE methods
- causal-genomics/heritability-partitioning - LDSC partition includes positive-selection annotations
- variant-calling/variant-annotation - Functional annotation of selected sites
<!-- END FILE: comparative-genomics/positive-selection/SKILL.md -->

## 子目录：comparative-genomics/synteny-analysis

<!-- BEGIN FILE: comparative-genomics/synteny-analysis/SKILL.md -->
---
name: bio-comparative-genomics-synteny-analysis
description: Detect syntenic blocks and structural rearrangements between genomes using MCScanX (Wang 2012), JCVI/MCScan (Tang 2008 Python), GENESPACE (Lovell 2022) for orthology-anchored riparian visualization, SyRI for structural variation, AnchorWave for sequence-level synteny, i-ADHoRe 3.0 for highly diverged species, SynNet for synteny networks, and ntSynt for multi-genome macrosynteny. Use when identifying collinear gene blocks across species, distinguishing macrosynteny from microsynteny, detecting inversions/translocations/duplications, anchoring orthology in WGD lineages, producing publication riparian plots, computing synteny block age via Ks (cross-references whole-genome-duplication), or running synteny-aware ortholog inference in polyploids.
tool_type: mixed
primary_tool: MCScanX
---

## Version Compatibility

Reference examples tested with: MCScanX 1.0+ (wyp1125/MCScanX commit 2020+), JCVI 1.4.21+ (Python port of MCScan), GENESPACE 1.4.0+ (Lovell 2022 eLife 11:e78526), SyRI 1.7.1+ (Goel 2019 Genome Biol 20:277), plotsr 1.1.1+, AnchorWave 1.2.5+ (Song 2022 PNAS 119:e2113075119), i-ADHoRe 3.0.01+, SynNet (Zhao 2017 Plant Cell 29:1278), ntSynt 1.0.4+ (2024), minimap2 2.28+, MUMmer 4.0.0+, OrthoFinder 3.0+, R 4.4+. plotsr requires pysam 0.22+ and seaborn 0.13+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `MCScanX -h`; `syri --version`; `python -m jcvi.compara.catalog ortholog --help`
- R: `packageVersion('GENESPACE')`; `?run_genespace`
- Python: `pip show jcvi`

If code throws `MCScanX: argument bad format`, `syri: input alignment file missing required columns`, or `GENESPACE: GFF parse error`, these tools have brittle input parsing: MCScanX requires 4-column `species_chr  gene  start  end` BED (non-standard), JCVI expects 4-column simple BED, GENESPACE requires GFF3 with `gene` feature type. Pre-process with `jcvi.formats.gff bed` or custom AWK.

# Synteny Analysis

**"Compare genome architecture between these species"** -> Detect conserved gene order (synteny) and infer rearrangement history. Synteny is NOT the same as collinearity: synteny is "genes on same chromosome", collinearity is "same order on same chromosome" (modern usage often conflates them). The choice of tool depends on whether the question is **gene-level co-linearity** (MCScanX, JCVI), **whole-genome structural rearrangements** (SyRI, AnchorWave), **multi-genome macrosynteny** (GENESPACE, ntSynt), or **synteny-aware orthology** (GENESPACE, ProteinOrtho-synteny). Repeat-masking quality is the dominant determinant of result reliability -- unmasked TEs produce ~100x more false anchor pairs than real syntenic anchors.

- CLI: `MCScanX` for collinear gene blocks via dynamic programming
- CLI: `python -m jcvi.compara.catalog ortholog A B` for JCVI/MCScan Python pipeline
- R: `run_genespace()` (Lovell 2022) for orthology-anchored riparian plots + pan-gene tracks
- CLI: `syri` for inversion / translocation / duplication detection
- CLI: `anchorwave proali` for sequence-level WGD-aware synteny

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| MCScanX (Wang 2012 NAR 40:e49) | Dynamic programming on BLAST hits with collinearity scoring | `.collinearity` blocks; tandem duplications collapsed | Most widely used; 14 downstream tools; well-benchmarked | Repeat-derived false BLAST hits; brittle 4-column input |
| MCScanX-h | Within-genome variant for WGD detection | Self-comparison blocks | Standard for paranome construction; WGD-aware | Same input fragility |
| JCVI / MCScan Python (Tang 2008 GR 18:1944) | Re-implementation of MCScanX with anchor stringency control | Publication-grade dotplots, karyotype, riparian | Best plotting; `--cscore` reciprocal-hit control | Slower than MCScanX C version on huge genomes |
| GENESPACE (Lovell 2022 eLife 11:e78526) | OrthoFinder + MCScanX orthogroup-constrained synteny | Riparian plots; pan-gene tracks; CNV across genomes | Modern standard for plant comparative; integrates orthology | Slow at > 30 genomes; less rigorous for non-plant clades |
| i-ADHoRe 3.0 (Proost 2012 NAR 40:e11) | Iterative ordered-gene-list detection | Ghost gene families; deeply diverged synteny | Catches ancient synteny obscured by rearrangements | Computationally heavy at genome scale |
| AnchorWave (Song 2022 PNAS 119:e2113075119) | CDS/exon anchors -> wave-front alignment | Whole-genome alignment with WGD awareness; SVs | Best for plant WGD analyses with known ploidy | CDS-anchored only; intergenic resolution limited |
| SyRI (Goel 2019 GB 20:277) | Pairwise WGA -> syntenic-path identification -> SV calls | INV / TRANS / DUP / SYN / INS / DEL annotated | Comprehensive SV detection; works on chromosome-level assemblies | Requires chromosome-level assemblies; pairwise only |
| plotsr (Goel 2022 Bioinformatics 38:2922) | Multi-genome SyRI visualization | Stacked synteny + SV maps across N genomes | Best for visualizing 3-10 genome rearrangement histories | Inherits SyRI's pairwise input limitation |
| ntSynt (2024) | Minimizer-based alignment-free synteny | Multi-genome macrosynteny blocks | Alignment-free; handles > 15% divergence | Macrosynteny only; misses microsynteny |
| SynNet (Zhao 2017 Plant Cell 29:1278) | Synteny block adjacency graphs | Synteny networks across many genomes | Phylogenetic network from synteny; detects deep ancestry | Less standard than block-based methods |
| Satsuma / progressive Cactus | Reference-free WGA | Whole-genome alignment (HAL format) | Underlies large-scale orthology; sequence-level synteny | See [[whole-genome-alignment]] |
| LASTZ chain/net (UCSC; Kent 2003 PNAS 100:11484 chains/nets; Schwartz 2003 GR 13:103 BLASTZ) | Pairwise WGA with chains and nets | Chains + nets in UCSC genome browser | Reference-anchored synteny; standard for UCSC tracks | See [[whole-genome-alignment]] |
| nucmer + dnadiff (MUMmer4; Marçais 2018 PLoS Comp Biol 14:e1005944) | MUM-anchored pairwise alignment | Whole-genome alignment with SV summary | Fast pairwise WGA for closely related | Sensitive only above ~70% identity |
| MashMap (Jain 2018 Bioinformatics 34:i748) | Approximate mapping for fragment-fragment synteny | Pairwise mappings with identity | Scales to thousands of genomes | Coarse (window-based); no SV inference |

Methodology evolves; GENESPACE has emerged as the de facto standard for plant comparative genomics (2022-2026). For non-plant clades, MCScanX or JCVI remain the workhorses. Whole-genome alignment for synteny is increasingly delegated to Cactus / Minigraph-Cactus and HAL toolkit (see [[whole-genome-alignment]]).

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Plant comparative genomics, 2-20 species | GENESPACE | Integrated orthology + synteny + visualization; modern standard |
| Animal / fungal, 2 species comparison | JCVI/MCScan | Best plots; flexible; widely cited |
| Animal / fungal, 10+ species | OrthoFinder + MCScanX + custom plot OR JCVI multi-genome | Avoid plant-specific GENESPACE assumptions |
| Bacterial / prokaryote synteny | progressiveMauve OR MCScanX-bacterial | Tools designed for compact genomes |
| Chromosome-level rearrangement inventory | SyRI + plotsr | Comprehensive SV (INV/TRANS/DUP) with publication viz |
| Polyploid genome analysis | AnchorWave proali mode with ploidy | WGD-aware synteny; subgenome-aware |
| Closely related strains (>= 95% identity) | nucmer + dnadiff | Faster than chromosome-level WGA; appropriate sensitivity |
| Distantly related species (< 70% identity) | i-ADHoRe 3.0 or LASTZ chains/nets | Sequence-level approaches lose power; ordered-list methods retain it |
| Ancient WGD detection | See [[whole-genome-duplication]] | wgd v2, KsRates; Ks-based dating outside synteny scope |
| WGA at clade-level (10+ vertebrates) | Cactus / Minigraph-Cactus -> halSynteny | See [[whole-genome-alignment]]; multi-genome reference-free |
| Pan-genome of bacterial strains | See [[pangenome-analysis]] | Panaroo / PPanGGOLiN / PEPPAN; different problem |
| Synteny-aware ortholog disambiguation | ProteinOrtho `-synteny` or GENESPACE | Tandem duplicates collapsed; co-orthologs assigned to syntenic position |
| Reference-guided assembly bias check | DO NOT use synteny across reference-guided scaffolds | Reference-guided scaffolds propagate scaffold assumptions; circular reasoning |
| Microsynteny network analysis | SynNet | Network from many genomes; detects ancient micro-conserved clusters |
| Synteny across > 15% divergent genomes | ntSynt or i-ADHoRe | Alignment-free or ordered-list approaches |
| Identifying syntelogs (syntenic orthologs only) | GENESPACE `riparian()` output; or MCScanX filtered by chr-pair | Syntelog tracks only same-chromosome-pair orthologs |

## Per-Tool Failure Modes

### Repeat-derived false synteny

**Trigger:** Running BLAST input for MCScanX/JCVI without softmasking repeats; or weak softmasking.

**Mechanism:** Transposable elements occupy 30-80% of plant and animal genomes; unmasked TEs produce millions of paralogous BLAST hits forming "synteny" blocks that are TE-driven, not real ancestry. The dynamic programming sees long apparent collinear blocks of TE-encoded proteins.

**Symptom:** MCScanX/JCVI output dominated by short (5-10 anchor) blocks; blocks cluster in TE-rich regions (heterochromatin, centromeric); BLAST hit count > 10x what is expected for the divergence.

**Fix:** Softmask genomes with RepeatModeler2 (de novo TE library) + RepeatMasker before BLAST; report softmasking statistics. For MCScanX, set `-e 1e-10` (stricter) for close species, `-e 1e-5` for distant. JCVI `--cscore 0.95` enforces near-reciprocal-best-hit, dramatically reducing TE-driven blocks. Always check that block size distribution drops at 5-10 anchors (TE-driven) vs proper > 20 anchor blocks (real synteny).

### Reference-guided assembly creating circular synteny

**Trigger:** Comparing a de novo assembly with a reference-guided scaffold of the same / related species.

**Mechanism:** Reference-guided scaffolding orders contigs based on synteny to the reference. Comparing the resulting scaffold to that same reference produces "synteny" that is actually the imposed reference order, not biological gene order. The comparison is circular.

**Symptom:** Suspicious uniformity in synteny across most chromosomes; visualization shows reference and query as perfectly parallel; SyRI reports few SVs where divergence-time-appropriate counts would predict many.

**Fix:** Verify assembly method via metadata. For reference-guided assemblies, treat synteny inferences with the reference as suspect; use a sister species reference or pure de novo assembly. Hi-C-scaffolded assemblies are not "reference-guided" in this sense and are safe.

### Fragmented assemblies underestimating macrosynteny

**Trigger:** Running synteny on draft assemblies with N50 < 1 Mb.

**Mechanism:** Macrosynteny detection requires that syntenic blocks be on single contigs; if contigs are short, blocks are artificially truncated. JCVI reports show artifactual "synteny loss" between species when one assembly is fragmented.

**Symptom:** Synteny "loss" correlates with assembly N50; per-chromosome dotplots show dotted lines where solid diagonals expected; SyRI reports excessive INVs / TRANS where the divergence is actually low.

**Fix:** Require minimum N50 of 1 Mb for cross-species synteny; chromosome-level assemblies preferred for SyRI. For fragmented assemblies, restrict analysis to long-contig regions or use SyRI's contig-level mode with caveats.

### Tandem duplicate inflation

**Trigger:** Including tandemly duplicated genes in synteny anchor input.

**Mechanism:** Tandem duplicates produce many same-region BLAST hits between species; the dynamic programming includes them as multiple anchors per gene position, artificially inflating block size and confidence.

**Symptom:** "High-confidence" synteny blocks in regions known for tandem expansions (NLR clusters in plants, OR genes in mammals); blocks anchored largely on adjacent tandem duplicates of the same gene.

**Fix:** MCScanX automatically collapses tandem duplicates (within 5 genes by default; `-w` parameter). Verify in the output the tandem-collapse step ran. JCVI `--tandem_Nmax 10` is more aggressive. For NLR / OR genes specifically, manual tandem filtering before BLAST is preferred.

### Cross-genome chromosome name mismatch

**Trigger:** GFF and FASTA from different sources with different chromosome naming (`chr1` vs `Chr1` vs `1` vs `NC_001234.5`).

**Mechanism:** MCScanX requires chromosomes to be named consistently; mismatch causes empty output or partial blocks.

**Symptom:** MCScanX completes but `.collinearity` file is small or empty; warnings about unknown chromosome IDs.

**Fix:** Normalize chromosome names with `awk` or `samtools faidx --regions` to unify naming convention; verify GFF + FASTA share the same names. For NCBI assemblies, use `datasets` to download with consistent labels.

### SyRI complaining about inversions in absence of true inversions

**Trigger:** Running SyRI on alignments with many small-scale rearrangements; or when one genome has been re-ordered (different convention for which strand is "+").

**Mechanism:** SyRI's syntenic-path algorithm penalizes any rearrangement; high-divergence pairs accumulate small-scale rearrangements that are not "real" inversions but inheritance differences.

**Symptom:** SyRI reports thousands of small "inversions" (< 1 kb); blocks dominate the SV count; total INV length unrealistic.

**Fix:** Filter SyRI output by size: real biologically-relevant INVs are typically > 5 kb. Tighten minimap2 sensitivity (`-x asm5` for close species; `-x asm10` or `-x asm20` for more divergent). Reverse-complement one assembly's chromosomes if the strand convention differs.

### GENESPACE OrthoFinder version mismatch

**Trigger:** Running GENESPACE with an outdated bundled OrthoFinder.

**Mechanism:** GENESPACE bundles a specific OrthoFinder version; if user's installed OrthoFinder is newer (v3 vs v2.5), the HOG output layout differs and GENESPACE parsing fails.

**Symptom:** GENESPACE reports "Phylogenetic_Hierarchical_Orthogroups not found" or similar; orthogroup table is empty.

**Fix:** Use the OrthoFinder version GENESPACE expects (currently OrthoFinder 2.5.4 for GENESPACE 1.4.x). Pin via `conda env`. Future GENESPACE versions will adapt to OrthoFinder 3 layout (Lovell update expected).

### Microsynteny vs macrosynteny conflation

**Trigger:** Reporting "synteny" without specifying scale.

**Mechanism:** Macrosynteny (same chromosome) is detectable across hundreds of millions of years but decays as rearrangements accumulate; microsynteny (same order within local region) can be deeply conserved even when macrosynteny is lost. Conflating them produces misleading "synteny loss" claims.

**Symptom:** Reports of "synteny lost between species X and Y" when both share microsyntenic gene clusters; or vice versa.

**Fix:** Always specify scale. SynNet (Zhao 2017) explicitly separates the two. MCScanX `-s` parameter (minimum block anchors) at 5 = microsynteny; at 20+ = macrosynteny. Report block-size distribution.

### Polyploid / WGD-affected genome ambiguity

**Trigger:** Running MCScanX on a polyploid (e.g. allohexaploid wheat) without subgenome assignment.

**Mechanism:** WGD doubles all genes; synteny is between subgenomes within the polyploid AND across to outgroup. Without subgenome assignment, all paralogs and orthologs collapse into the same blocks.

**Symptom:** Many "1:many" or "many:many" synteny relationships; per-chromosome synteny counts indicate doubled or tripled blocks; Ks distribution multimodal.

**Fix:** Use AnchorWave proali with explicit ploidy specification. Alternatively, run synteny twice: within polyploid (subgenome-vs-subgenome) and across to outgroup. See [[whole-genome-duplication]] for subgenome assignment workflow.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Assembly N50 for synteny | >= 1 Mb | Below this, results tool-dependent and unreliable; chromosome-level strongly preferred |
| MCScanX -s (minimum anchors per block) | 5 default; 10 stringent; 3 sensitive | Standard configuration; 5 is balance |
| MCScanX -m (maximum gaps between anchors) | 25 default | Higher for distant species; lower for recent |
| MCScanX -k (match score per anchor) | 50 default | Higher rewards longer blocks |
| MCScanX -e (BLAST e-value) | 1e-5 default; 1e-10 for close species | Stricter for recent radiations |
| BLAST evalue threshold | 1e-5 to 1e-10 typical | Depends on divergence |
| JCVI --cscore for reciprocal best | 0.7 default; 0.95 near-RBH; 0.99 RBH-only | Higher = fewer false positives, fewer hits |
| Tandem duplicate window | 5-10 genes (MCScanX default 5; JCVI 10) | Wang 2012; species-specific tuning |
| SyRI INV minimum size for biological significance | >= 5 kb | Below this, alignment noise dominates |
| SyRI TRANS minimum size | >= 1 kb | Standard convention |
| GENESPACE minimum syntenic block | 5 orthogroups | Lovell 2022 default |
| Synteny block decay (macrosynteny half-life) | ~150 Myr in vertebrates | Approximate convention |
| Microsynteny conservation | up to 1 Gyr for metabolic gene clusters | Stated convention; verify per-clade |
| minimap2 preset for synteny | -x asm5 for < 5% divergence; asm10 for ~10%; asm20 for ~20% | minimap2 docs |
| MUMmer nucmer maxmatch | --maxmatch for SyRI; --mum default | MUMmer4 manual |
| Ks for syntenic block age (cross-references WGD) | Ks 0.1-0.5 recent; 0.5-1.5 older; > 1.5 saturated | See [[whole-genome-duplication]] for Ks plot interpretation |
| Repeat masking minimum | >= 90% of known TE families masked (RepeatMasker `.tbl`) | Below this, expect spurious synteny |

## MCScanX Standard Pipeline

**Goal:** Detect collinear gene blocks between two genomes.

**Approach:** Prepare 4-column BED with species prefix -> all-vs-all BLASTP -> run MCScanX -> parse `.collinearity` -> classify blocks.

```bash
# 1. Prepare MCScanX-format BED (species_chr  gene  start  end)
python -m jcvi.formats.gff bed --type=gene --key=ID species_A.gff > A.gff.tmp
python -m jcvi.formats.gff bed --type=gene --key=ID species_B.gff > B.gff.tmp
awk 'BEGIN{OFS="\t"}{print "A"$1, $4, $2, $3}' A.gff.tmp > work/A.gff
awk 'BEGIN{OFS="\t"}{print "B"$1, $4, $2, $3}' B.gff.tmp > work/B.gff
cat work/A.gff work/B.gff > work/A_B.gff

# 2. All-vs-all DIAMOND BLAST (faster than BLAST+)
diamond makedb --in species_A.faa --db work/A.dmnd
diamond makedb --in species_B.faa --db work/B.dmnd
diamond blastp --db work/A.dmnd --query species_A.faa --threads 16 \
    --outfmt 6 --evalue 1e-10 --max-target-seqs 5 --out work/AA.blast
diamond blastp --db work/B.dmnd --query species_B.faa --threads 16 \
    --outfmt 6 --evalue 1e-10 --max-target-seqs 5 --out work/BB.blast
diamond blastp --db work/B.dmnd --query species_A.faa --threads 16 \
    --outfmt 6 --evalue 1e-10 --max-target-seqs 5 --out work/AB.blast
diamond blastp --db work/A.dmnd --query species_B.faa --threads 16 \
    --outfmt 6 --evalue 1e-10 --max-target-seqs 5 --out work/BA.blast
cat work/AA.blast work/BB.blast work/AB.blast work/BA.blast > work/A_B.blast

# 3. Run MCScanX
cd work && MCScanX -s 5 -m 25 -k 50 -e 1e-10 A_B
# Output: A_B.collinearity (block table), A_B.tandem (tandem clusters), A_B.html (browsing)
```

```python
'''Parse MCScanX .collinearity and classify synteny relationships.'''
import re
from collections import defaultdict


def parse_collinearity(path):
    '''Returns list of dicts: {block_id, n_anchors, e_value, score, gene_pairs: [(g1, g2), ...]}'''
    blocks = []
    current = None
    with open(path) as fh:
        for line in fh:
            if line.startswith('## Alignment'):
                if current:
                    blocks.append(current)
                m = re.match(r'## Alignment (\d+): score=([0-9.]+) e_value=([0-9.e\-]+) N=(\d+)', line)
                if m:
                    current = {
                        'block_id': int(m.group(1)),
                        'score': float(m.group(2)),
                        'e_value': float(m.group(3)),
                        'n_anchors': int(m.group(4)),
                        'gene_pairs': []
                    }
            elif current and ':' in line and '\t' in line:
                parts = line.strip().split()
                if len(parts) >= 3:
                    current['gene_pairs'].append((parts[1], parts[2]))
    if current:
        blocks.append(current)
    return blocks


def classify_chromosome_synteny(blocks, gene_to_chr):
    '''Classify syntenic chromosome relationships: 1-1, 1-many, many-many.'''
    a_partners = defaultdict(set)
    for blk in blocks:
        for g1, g2 in blk['gene_pairs']:
            c1, c2 = gene_to_chr.get(g1), gene_to_chr.get(g2)
            if c1 and c2:
                a_partners[c1].add(c2)
    result = {}
    for chr_a, partners in a_partners.items():
        n = len(partners)
        result[chr_a] = '1-1' if n == 1 else ('1-many' if n <= 3 else 'many-many')
    return result
```

## GENESPACE Plant-Focused Pipeline

**Goal:** Build pan-gene tracks across N plant genomes with orthology-anchored synteny visualization.

**Approach:** Format input: per-species GFF + protein FASTA -> initialize -> run -> riparian plot.

```r
library(GENESPACE)

dir.create('work_dir')
parsedPaths <- parse_annotations(
    rawGenomeRepo = 'raw_genomes/',
    genomeDirs = list.dirs('raw_genomes/', recursive = FALSE),
    headerEntryIndex = 1,
    gffString = 'gff',
    faString = 'protein.faa',
    genespaceWd = 'work_dir/'
)

gpar <- init_genespace(
    wd = 'work_dir/',
    nCores = 8,
    rawOrthofinderDir = NULL,  # GENESPACE bundles OrthoFinder 2.5.x
    onewayBlast = TRUE
)

out <- run_genespace(gsParam = gpar, overwrite = TRUE)

# Riparian plot for 5 genomes vs reference
ripDat <- plot_riparian(
    gsParam = out,
    refGenome = 'Reference_species',
    useOrder = FALSE,
    backgroundColor = 'white'
)
```

GENESPACE outputs include `results/syntenicHits.txt` (anchor pairs), `results/pangenes.txt` (pan-gene presence/absence matrix), and `results/riparian.pdf` (riparian visualization). Pan-gene tracks across species are particularly useful for identifying lineage-specific genes (cf. pangenome-analysis for bacterial scope).

## SyRI for Structural Rearrangement Inventory

**Goal:** Identify INVs, TRANSs, DUPs, INS, DEL between two chromosome-level genome assemblies.

**Approach:** Align with minimap2 -x asm5 -> filter to chromosome-level mappings -> run SyRI -> visualize with plotsr.

```bash
# 1. Whole-genome alignment with minimap2
minimap2 -ax asm5 --eqx -t 16 reference.fa query.fa | \
    samtools sort -@ 8 -O bam - > work/aln.bam
samtools index work/aln.bam

# 2. SyRI on the alignment
syri -c work/aln.bam -r reference.fa -q query.fa -F B --prefix work/syri_out -k

# Outputs:
#   syri_out.syri.out      structural variant table (SYN/INV/TRANS/DUP/INS/DEL)
#   syri_out.syri.vcf      VCF-format variants
#   syri_out.syri.summary  block-level summary

# 3. Visualize with plotsr
echo "ref_species  query_species" > work/genome_pairs.txt
plotsr --sr work/syri_out.syri.out --genomes work/genome_pairs.txt \
    --output work/syri_plot.png --markers gene_markers.bed
```

For multi-genome rearrangement: run SyRI pairwise for each adjacent species in a phylogeny, then plotsr stacks the panel.

## JCVI / MCScan Python for Publication Plots

**Goal:** Produce publication-grade dotplots, karyotype, and synteny visualization.

**Approach:** Use JCVI's catalog ortholog workflow to derive anchors -> generate dotplot or karyotype directly.

```bash
# 1. Detect orthologs and synteny
python -m jcvi.formats.gff bed --type=mRNA --key=Name species_A.gff > A.bed
python -m jcvi.formats.gff bed --type=mRNA --key=Name species_B.gff > B.bed
python -m jcvi.formats.fasta format species_A.faa A.fasta
python -m jcvi.formats.fasta format species_B.faa B.fasta

python -m jcvi.compara.catalog ortholog --no_strip_names A B
# Produces A.B.lifted.anchors and other files

# 2. Dotplot
python -m jcvi.graphics.dotplot A.B.anchors --dpi 300 --output dotplot.png

# 3. Karyotype (chromosome-level synteny)
# Layout file: each row = species  chr  start  end  reverse
cat > layout.csv << 'EOF'
A.chr1 species_A 1 50000000 1
B.chr2 species_B 1 60000000 1
EOF
python -m jcvi.graphics.karyotype seqids.txt layout.csv

# 4. Microsynteny block plot
python -m jcvi.graphics.synteny blocks.layout
```

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MCScanX many blocks, GENESPACE few | GENESPACE uses orthogroup-constrained anchors (more conservative) | GENESPACE excludes non-orthogroup hits; MCScanX includes any high BLAST hit; trust GENESPACE for orthology-anchored synteny |
| GENESPACE 1:1 syntelog, MCScanX 1:many | Tandem duplicates in MCScanX collapsed at different granularity | Trust GENESPACE for clear syntelogs; MCScanX 1:many often reflects tandem expansions |
| SyRI reports many INVs, plotsr shows mostly SYN | Small INVs below biological-relevance threshold | Filter SyRI INVs < 5 kb; SyRI was correct, just noisy |
| MCScanX block on chromosomes that JCVI doesn't pair | JCVI `--cscore 0.7` more restrictive | Lower JCVI cscore to 0.5 OR raise MCScanX -e to 1e-10 |
| AnchorWave finds collinearity in WGD region, MCScanX doesn't | AnchorWave WGD-aware; MCScanX treats all anchors equally | AnchorWave correct for WGD lineages |
| ntSynt macrosynteny across genus, MCScanX microsynteny only | Different scales | Both correct at their scale; report both with explicit scale labels |
| SyRI calls "translocation" but it's a known chromosome split | Centromere break / Robertsonian translocation | Manual cytogenetic context; SyRI's mechanical detection is correct but may not be biologically novel |
| Recent species pair has > 1000 SVs in SyRI | Either real chromosome instability OR assembly errors | Check assembly QC (telomere completeness; BUSCO); cross-check with PacBio long-read SVs |
| Synteny on reference-guided scaffold | Circular reasoning | Discard synteny calls between scaffold and its reference |

**Operational rule for publication:** Synteny block annotation requires (1) BUSCO/Compleasm > 90% complete on both genomes; (2) softmasked repeats verified; (3) at least one cross-validation tool (MCScanX vs JCVI or MCScanX vs GENESPACE); (4) microsynteny vs macrosynteny scale explicit; (5) for SV calls, plotsr / SyRI followed by manual review of large rearrangements with read-coverage support.

## Cohort Gotchas

- **Polyploid plants:** WGD events confound 1:1 synteny; use AnchorWave or subgenome-assigned analysis
- **Salmonids / fish 4R:** Ts3R + Ss4R WGD events; ohnologs (WGD paralogs) appear as syntenic but not orthologous; cross-reference [[whole-genome-duplication]]
- **Mammalian X chromosome:** Massive recombination suppression; "synteny" sometimes inverted in opposite sex; verify strand convention
- **Centromeric regions:** generally unalignable; synteny tools may produce false breaks near centromeres
- **Telomeres:** assembly often incomplete; synteny calls near telomere boundaries unreliable
- **Sex chromosomes:** rapidly evolving; lower synteny signal than autosomes
- **Plant B chromosomes:** supernumerary; exclude from synteny analysis

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Assembly completeness?" | BUSCO/Compleasm > 90%; N50 reported per assembly; chromosome-level (or scaffold N50 > 1 Mb) |
| "Repeat masking?" | RepeatModeler2 de novo TE library + RepeatMasker; > 90% of known TE families masked; softmasked, not hardmasked |
| "Reference-guided scaffolding?" | Verified de novo OR Hi-C scaffolded; no reference-guided steps |
| "Tandem duplicates?" | Collapsed by MCScanX automatic detection (window 5); JCVI tandem_Nmax 10 |
| "Cross-validation?" | MCScanX results validated against JCVI (or GENESPACE) at consistent stringency |
| "Microsynteny vs macrosynteny?" | Reported both scales; minimum block size 5 anchors for microsynteny, 20+ for macrosynteny |
| "WGD-aware?" | AnchorWave proali with ploidy specification (for polyploids); or restricted to non-WGD lineages |
| "SV calling sensitivity?" | SyRI INVs > 5 kb; cross-validated with PacBio long-read SV calls where available |
| "Synteny block age (Ks)?" | Ks plotted per block; saturation threshold (Ks > 2) applied; see [[whole-genome-duplication]] |
| "Bacterial pangenome reference?" | Not applicable here; see [[pangenome-analysis]] for prokaryotes |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| MCScanX produces empty .collinearity | 4-column BED format wrong (extra columns, wrong delimiter, missing prefix) | Check exact 4-column format: `species_prefix_chr  gene_id  start  end`; tabs only |
| MCScanX dumps "no matches" message | BLAST e-value too strict; or gene IDs don't match BED | Verify gene IDs in BED match BLAST input; relax e-value |
| GENESPACE "OrthoFinder version mismatch" | Bundled OrthoFinder version conflict | Pin OrthoFinder 2.5.x for GENESPACE 1.4.x; or update GENESPACE |
| JCVI dotplot empty | `--cscore` too strict; few anchors survive | Lower cscore to 0.5; or check BLAST hit count |
| SyRI "no chromosomes match" | Reference and query use different chromosome IDs | Normalize names: `samtools faidx --regions` to extract by name |
| SyRI INVs appear in all assemblies | Strand convention issue OR repeat-driven | Reverse-complement one assembly's chromosomes if convention differs; mask repeats |
| AnchorWave proali times out | Genome > 1 Gb with high TE density | Pre-mask repeats; consider GENESPACE / MCScanX alternative |
| GENESPACE riparian plot too crowded | > 10 genomes | Subset to representative species or use multi-page riparian |
| Per-chromosome BLAST hit count > 100,000 | Unmasked repeats | Softmask before BLAST; verify by counting TE-encoded protein hits |
| Synteny blocks on Y chromosome appear absent | Y not assembled fully; or sex-specific | Document assembly limitation; exclude Y from synteny analysis |

## Tool Installation Notes

```bash
# MCScanX
git clone https://github.com/wyp1125/MCScanX && cd MCScanX && make
# JCVI / MCScan Python
pip install jcvi
# GENESPACE
remotes::install_github('jtlovell/GENESPACE')
# SyRI + plotsr
conda install -c bioconda syri plotsr
# AnchorWave
conda install -c bioconda anchorwave
# i-ADHoRe
git clone https://github.com/VIB-PSB/i-ADHoRe && cd i-ADHoRe && mkdir build && cd build && cmake .. && make
# ntSynt
pip install ntsynt
# minimap2 + MUMmer4
conda install -c bioconda minimap2 mummer4

# Repeat masking
conda install -c bioconda repeatmodeler repeatmasker
```

For GENESPACE, OrthoFinder 2.5.x must be pinned; install via `conda install -c bioconda orthofinder=2.5.5`. JCVI is the most generally useful Python toolkit; install per-project alongside specific synteny tools.

## References

- Wang Y et al 2012 NAR 40:e49 (MCScanX)
- Tang H et al 2008 GR 18:1944 (synteny / MCScan Python)
- Lovell JT et al 2022 eLife 11:e78526 (GENESPACE)
- Proost S et al 2012 NAR 40:e11 (i-ADHoRe 3.0)
- Song B et al 2022 PNAS 119:e2113075119 (AnchorWave)
- Goel M et al 2019 Genome Biol 20:277 (SyRI)
- Goel M et al 2022 Bioinformatics 38:2922 (plotsr)
- Zhao T et al 2017 Plant Cell 29:1278 (SynNet synteny network)
- Marçais G et al 2018 PLoS Comp Biol 14:e1005944 (MUMmer4)
- Kent WJ et al 2003 PNAS 100:11484 (chains and nets)
- Schwartz S et al 2003 GR 13:103 (BLASTZ pairwise aligner)
- Jain C et al 2018 Bioinformatics 34:i748 (MashMap)
- Li H 2018 Bioinformatics 34:3094 (minimap2)
- Holland PWH et al 1994 Development Suppl:125 (2R hypothesis)
- Vanneste K et al 2013 MBE 30:177 (Ks saturation)
- Birchler JA & Veitia RA 2007 Plant Cell 19:395 (gene balance)
- Force A et al 1999 Genetics 151:1531 (subfunctionalization)
- Zhao T & Schranz ME 2017 Curr Opin Plant Biol 36:129 (synteny network for phylogeny)

## Related Skills

- comparative-genomics/whole-genome-duplication - Ks-based WGD detection, paranome construction, KsRates
- comparative-genomics/whole-genome-alignment - Cactus / Minigraph-Cactus / LASTZ chains-and-nets for sequence-level synteny
- comparative-genomics/ortholog-inference - GENESPACE depends on OrthoFinder; synteny verifies orthology in WGD lineages
- comparative-genomics/pangenome-analysis - Bacterial pangenome (different problem; for prokaryotes)
- comparative-genomics/comparative-annotation-projection - TOGA + CESAR project genes through WGA-derived synteny
- comparative-genomics/positive-selection - Selection on syntenic gene pairs (1:1 syntelogs)
- phylogenetics/modern-tree-inference - Phylogenetic context for synteny block dating
- genome-assembly/assembly-qc - BUSCO / Compleasm assembly completeness check before synteny
- alignment/structural-alignment - Sequence-level alignment underlying SyRI
- variant-calling/structural-variant-calling - SV detection from short reads (orthogonal to SyRI WGA-based)
<!-- END FILE: comparative-genomics/synteny-analysis/SKILL.md -->

## 子目录：comparative-genomics/whole-genome-alignment

<!-- BEGIN FILE: comparative-genomics/whole-genome-alignment/SKILL.md -->
---
name: bio-comparative-genomics-whole-genome-alignment
description: Build whole-genome alignments using Progressive Cactus (Armstrong 2020 reference-free clade-level WGA), Minigraph-Cactus (Hickey 2024 pangenome-aware), LASTZ chain/net (UCSC pipeline), MUMmer4 (Marçais 2018 pairwise), minimap2 -x asm5/10/20 (Li 2018 fast pairwise), AnchorWave (Song 2022 WGD-aware), and Mauve / progressiveMauve (bacterial). Operates the HAL toolkit (Hickey 2013) for downstream extraction including halSynteny, halLiftover, halBranchMutations, and hal2maf. Use when constructing multi-species alignments for comparative-annotation projection (TOGA), synteny detection, conservation analyses (phyloP / PhastCons), or pangenome graph construction; selecting between reference-free (Cactus) and reference-anchored (LASTZ chains/nets) approaches; tuning sensitivity for closely vs distantly related genomes; or producing HAL files for genome-wide downstream tools.
tool_type: cli
primary_tool: Cactus
---

## Version Compatibility

Reference examples tested with: Progressive Cactus 2.9.1+ (ComparativeGenomicsToolkit/cactus; Armstrong 2020 Nature 587:246), Minigraph-Cactus (Hickey 2024 Nat Biotech 42:663; bundled with Cactus 2.5+), HAL toolkit 2.3+ (Hickey 2013 Bioinformatics 29:1341), LASTZ 1.04.22+, UCSC kentUtils for chain/net (Kent 2003 PNAS 100:11484), MUMmer 4.0.0+, minimap2 2.28+, AnchorWave 1.2.5+, progressiveMauve 2.4.0+, sibeliaz 1.2.5+, winnowmap 2.03+ (Jain 2022 Nat Methods 19:705). Toil workflow runner 6.0+ for Cactus on HPC/cloud.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `cactus --help`, `cactus-pangenome --help`, `halStats --help`, `lastz --version`, `nucmer --version`, `minimap2 --version`
- Python: `pip show toil`, `toil --version`

If code throws `Toil workflow restart failure`, `HAL file corrupted`, `WDL workflow missing`, the Cactus pipeline is Toil-based and requires careful checkpointing; failed runs must be restarted with `--restart`. HAL file versions differ across hal-toolkit releases; pin the version that produced the file.

# Whole Genome Alignment

**"Align these multiple genomes at the base-pair level"** -> Choose between **reference-free** progressive alignment (Cactus / Minigraph-Cactus: produces HAL, no privileged reference) and **reference-anchored** pairwise alignment (LASTZ chains/nets, MUMmer, minimap2: one genome is the reference, queries align to it). The fundamental tradeoff is **scale vs structure**: pairwise pipelines scale linearly per pair but lose multi-way relationships; progressive Cactus scales linearly with a tree but quadratically without and produces ancestrally-coherent alignments. For comparative genomics at vertebrate / mammal scale, Cactus is now the standard substrate (Zoonomia, Christmas 2023 Science 380:eabn3943; Bird10000 Genomes); for pangenome graph construction, Minigraph-Cactus (Hickey 2024) is the production pipeline.

- CLI: `cactus jobStore seqFile.txt output.hal --binariesMode local` -- reference-free progressive WGA
- CLI: `cactus-pangenome --reference ref name --vcf` -- pangenome graph from genomes
- CLI: `lastz target.fa[multiple] query.fa` then UCSC chain-net pipeline -- pairwise to a reference
- CLI: `minimap2 -ax asm5 ref.fa query.fa | samtools sort` -- fast pairwise for closely related
- CLI: `nucmer --maxmatch ref.fa query.fa` then `dnadiff` -- MUMmer4 pairwise
- CLI: `anchorwave proali --ploidy 4` -- WGD-aware sequence-level synteny alignment

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| Progressive Cactus (Armstrong 2020 Nature 587:246) | LASTZ pairwise -> CAF graph -> BAR -> ancestral assembly per node | HAL multi-genome alignment | Reference-free; scales to 1000s of genomes with phylogenetic tree; ancestral assembly at every internal node | Quadratic without tree; ALSO scaling problems if branch_scale and chaining parameters mis-tuned (Armstrong 2020 Supp Methods) |
| Minigraph-Cactus (Hickey 2024 Nat Biotech 42:663) | minigraph SV graph base + Cactus base-level resolution | Pangenome graph (VCF, GFA, BAM) | Combines structural variation (minigraph) with base-level alignment (Cactus); HPRC standard | Requires reference; designed for intra-species pangenomes (90 human haplotypes) |
| LASTZ + UCSC chain/net (Kent 2003 PNAS 100:11484) | LASTZ local alignments -> chains (collinear) -> nets (one-to-one selection) | Reference-anchored alignment (chain, net, MAF) | Standard for UCSC genome browser tracks; well-validated; pairwise interpretable | Reference-bias; quadratic scaling for N genomes; per-pair manual chain/net pipeline |
| MUMmer4 nucmer (Marçais 2018 PLoS Comp Biol 14:e1005944) | Maximal exact matches -> clustering -> alignment extension | Pairwise alignment (delta format) | Fast for closely related (>= 70% identity); robust | Slow at low identity; pairwise only |
| minimap2 (Li 2018 Bioinformatics 34:3094) | Minimizer-based seeding + base-level alignment | SAM / PAF pairwise | Very fast; preset `-x asm5/10/20` for divergence | Lower accuracy at < 70% identity vs LASTZ |
| AnchorWave (Song 2022 PNAS 119:e2113075119) | CDS/exon anchors -> wavefront alignment | Sequence-level synteny + SV | WGD-aware (ploidy parameter); plant-friendly | CDS-anchored; intergenic resolution limited |
| Progressive Mauve (Darling 2010 PLoS One 5:e11147) | Local collinear blocks (LCBs) -> progressive alignment | Multi-genome bacterial alignment | Bacterial-friendly; handles inversions natively | Slow for > 30 genomes; less common today |
| SibeliaZ (Minkin & Medvedev 2020 Nat Commun 11:6327) | de Bruijn graph + colinear blocks | Bacterial / closely related multi-genome alignment | Scales to 100+ genomes | Highly diverged genomes lose recall |
| HAL toolkit (Hickey 2013 Bioinformatics 29:1341) | Hierarchical Alignment Format | Index, slice, project, extract from HAL | Standard substrate for downstream Cactus tools (TOGA, halSynteny, halLiftover) | HAL file version pinning required |
| Winnowmap2 (Jain 2022 Nat Methods 19:705) | minimap2-derived with masked repetitive minimizers | SAM / PAF | Optimized for highly repetitive regions (centromeres, telomeres) | Niche; for repeat-rich pairwise alignment |
| BLASTZ (legacy) | LASTZ predecessor | Local alignments | Historical; superseded by LASTZ | Use LASTZ instead |
| Multiz (Blanchette 2004 Genome Res 14:708) | Reference-anchored chain-merging | Multi-species MAF | UCSC's older multi-species pipeline | Superseded by Cactus |
| Lagan / mLagan (Brudno 2003) | Local-global hybrid alignment | Pairwise / multi-species | Historical; not actively developed | Use Cactus or LASTZ chain/net |

Methodology evolves; Cactus / Minigraph-Cactus / HAL are now the dominant production pipelines for vertebrate / mammal / plant WGA. LASTZ chains/nets remain the standard for adding a single new species to a reference-anchored ecosystem (UCSC, Ensembl).

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Vertebrate clade WGA, 10-500 genomes | Progressive Cactus | Reference-free; phylogenetic-tree guided; HAL output |
| Mammalian Zoonomia-scale WGA, 500-2000 genomes | Progressive Cactus with `--branchScale` tuning + HPC | Cactus scales to 1000s with proper Toil config |
| Plant clade WGA, with WGD | AnchorWave proali OR Cactus | AnchorWave WGD-aware; Cactus more general |
| Bacterial / archaeal genome alignment | progressiveMauve OR SibeliaZ | Designed for compact, rearrangement-rich genomes |
| Single new species added to reference (e.g. UCSC, Ensembl track) | LASTZ + chain/net | Standard reference-anchored pipeline; interpretable |
| Closely related strains / haplotypes (~95% identity) | minimap2 `-x asm5` or MUMmer nucmer | Fast pairwise; sufficient accuracy |
| Cross-species ~70-90% identity | LASTZ with `--strategy` tuned | minimap2 loses accuracy below ~70% |
| Cross-species ~50% identity (e.g. human vs zebrafish) | LASTZ with HoxD55 matrix | Specialized parameters for distant genomes |
| Pangenome graph for variant calling | Minigraph-Cactus or PGGB | See [[pangenome-analysis]] for graph-based variant calling |
| Repeat-rich genome (large mammal, plant) | Cactus with masked input | Pre-mask repeats with RepeatMasker/RepeatModeler2 |
| Centromeric / telomeric alignment | Winnowmap2 | Optimized for repetitive minimizers |
| Comparative annotation projection | Cactus -> TOGA + CESAR (see [[comparative-annotation-projection]]) | Cactus HAL is TOGA input |
| Conservation analysis (phyloP, PhastCons) | Cactus -> hal2maf to MAF for phyloP | MAF format from HAL is the substrate |
| Pairwise alignment for synteny | minimap2 `-x asm5` -> SyRI | See [[synteny-analysis]] |
| Long-read assembly pairwise validation | nucmer + dnadiff | Standard for assembly QC |
| Reference-to-pangenome lift-over | halLiftover or vg paths | HAL coordinate-system tools |

## Per-Tool Failure Modes

### Cactus running quadratically without species tree

**Trigger:** Running `cactus` without `--guide-tree` or with a poorly-resolved guide tree.

**Mechanism:** Cactus is designed as a progressive aligner: it aligns siblings, then their ancestor, recursively up the species tree. Without a guide tree, it tries all-vs-all alignment, which is O(N^2) and explodes for > 10 genomes.

**Symptom:** Cactus job time scales as N^2; cluster runs hit wall time before completing.

**Fix:** Always provide a guide tree in `seqFile.txt`:
```
(((human:0.05, chimp:0.05):0.05, macaque:0.1):0.2, mouse:0.5);
human    /path/to/human.fa
chimp    /path/to/chimp.fa
macaque  /path/to/macaque.fa
mouse    /path/to/mouse.fa
```
Branch lengths in substitutions per site; need not be precise but must reflect relative divergence. For poorly-resolved trees, use STAR (concatenation) tree from a few hundred concatenated single-copy orthologs (cf. [[ortholog-inference]]).

### Branch-scale parameter mis-tuned

**Trigger:** Cactus alignment producing very few or very many alignment columns relative to expected.

**Mechanism:** Cactus uses `--branchScale` to scale internal-branch lengths for LASTZ chaining parameters. Default scaling assumes vertebrate-like substitution rates; plants, bacteria, and viruses need adjustment. Wrong scaling produces under-aligned (too low) or over-merged (too high) blocks.

**Symptom:** HAL file shows alignment column count vastly different from expected; halStats reports unusual coverage; comparative annotation downstream fails.

**Fix:** Adjust `--branchScale` per clade: vertebrates default 1.0; plants 0.5-0.7; bacteria 0.3-0.5; viruses 0.1-0.3. Validate against known orthologs (BUSCO single-copies should align across all genomes).

### Toil checkpoint restart failures

**Trigger:** Cactus job interrupted (cluster timeout, OOM, node failure) and restart.

**Mechanism:** Cactus uses Toil's job store for checkpointing. Restart requires identical `jobStore` path, identical config, and pointing to the same machine type (some cloud-stored jobs require AWS / Google Cloud credentials).

**Symptom:** Cactus restart errors with "job store inconsistent" or "missing intermediate file."

**Fix:** Use `cactus --restart jobStore seqFile.txt output.hal`. For HPC, ensure the jobStore path is on shared storage accessible to all nodes. For cloud, use S3 or Google Cloud Storage with proper credentials. If restart fails, restart from scratch with a new jobStore.

### Reference bias in LASTZ chain/net

**Trigger:** Reporting "human-chimp synteny" from LASTZ chains/nets with human as reference.

**Mechanism:** Chain/net is reference-anchored; the alignment is biased toward the reference's genomic context. Repeat-content differences and assembly-quality differences between reference and query produce alignment artifacts.

**Symptom:** Different chains/nets from different reference choices show inconsistent SV calls; e.g. mouse-as-reference and human-as-reference produce different INV counts.

**Fix:** For multi-genome questions, use Cactus (reference-free). For pairwise questions, run chain/net both directions (A-on-B and B-on-A) and report consistent calls. Document reference choice in methods. SyRI on minimap2 alignments has similar issues; cross-validate.

### minimap2 sensitivity loss at < 70% identity

**Trigger:** Running `minimap2 -x asm10` or `-x asm20` between distantly related species.

**Mechanism:** Minimap2's minimizer-based seeding loses sensitivity at lower identity; many regions never anchor and produce gaps in alignment.

**Symptom:** Alignment coverage low (< 50% of query mapped); SyRI / SV-calling on this alignment reports few or no SVs; high-identity regions align but mid-identity regions don't.

**Fix:** Switch to LASTZ for < 70% identity; LASTZ uses 6-bp seeds with scoring matrices designed for distant comparison (HoxD55 for human-fish). For minimap2, try `-x asm20` with manual sensitivity tuning (`-k 19 -w 19`) but expect inferior performance vs LASTZ. minimap2 documentation recommends presets up to 20% divergence.

### Cactus producing wrong topology in ancestor assembly

**Trigger:** Cactus is asked to assemble an ancestral sequence at an internal node, but the input tree has wrong topology.

**Mechanism:** Cactus uses the guide tree to determine which descendants align to which ancestor. Wrong topology produces incorrect ancestor sequence at internal nodes.

**Symptom:** Ancestor sequences inconsistent with biological expectation; downstream phylogenetic analyses on Cactus ancestor sequences disagree with concatenation phylogenies.

**Fix:** Validate species tree before Cactus alignment using `phylogenetics/modern-tree-inference` on concatenated single-copy orthologs. If topology is uncertain, use a more conservative resolution (e.g. polytomy resolved via STRIDE).

### Repeats inflating LASTZ chain count

**Trigger:** Running LASTZ on unmasked or weakly masked genomes.

**Mechanism:** Unmasked TEs produce millions of paralogous LASTZ alignments; chains form from these, creating false-positive synteny / alignment.

**Symptom:** Chain count >> 100,000 per pair; many short chains in TE-rich regions; chain/net pipeline produces excessive chains where biology predicts few.

**Fix:** Softmask both genomes (RepeatModeler2 + RepeatMasker) before LASTZ. LASTZ honors softmasked sequences in its seeding step (lowercase = ignored at seeding, full alignment after extension). Hardmasking (N's) is too aggressive and breaks LASTZ scoring.

### HAL version mismatch breaking downstream tools

**Trigger:** Using HAL files generated with one version of Cactus / HAL toolkit with downstream tools using a different version.

**Mechanism:** HAL file format is versioned; minor version mismatch usually OK, major version mismatch causes silent or loud failures.

**Symptom:** halStats / TOGA / halLiftover errors about "unrecognized HAL version."

**Fix:** Use the HAL toolkit version that wrote the file (check via `halStats --filter halVersion` or git log of the run). For shared HAL files, pin Cactus version in documentation.

### Insufficient masking before Cactus

**Trigger:** Cactus on unmasked vertebrate genomes.

**Mechanism:** Cactus's CAF/BAR algorithms identify candidate alignment columns; without masking, TE-derived blocks dominate. Memory consumption explodes and alignment results are mostly TE pseudo-alignments.

**Symptom:** Cactus runs out of memory; HAL file is huge (> 100 GB for what should be 10 GB); halStats shows enormous column count.

**Fix:** Mask all genomes with RepeatMasker (or species-specific RepeatModeler2 library) before Cactus. Soft-masking is acceptable; Cactus handles lowercase appropriately. Document masking strategy.

### AnchorWave WGD parameter mis-set

**Trigger:** AnchorWave proali with wrong `--ploidy` value for the query genome.

**Mechanism:** AnchorWave's WGD-aware alignment matches each query CDS to ploidy-many reference CDS regions; wrong ploidy causes either undermatching (low ploidy) or overmatching (high ploidy).

**Symptom:** Reported alignment count inconsistent with biology (e.g. hexaploid wheat reports diploid-level matches).

**Fix:** Set `--ploidy` to query genome's ploidy (1 for haploid reference, 2 for diploid query when reference is diploid, 4 for tetraploid query vs diploid reference). Check with `python -m jcvi.compara.synteny depth` on output anchors.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Cactus runtime scaling | Linear with tree-balanced clade; quadratic without tree | Armstrong 2020 Supp Methods |
| Cactus memory per genome (vertebrate, masked) | 8-32 GB | Armstrong 2020 |
| Cactus minimum genome assembly N50 | >= 1 Mb for reliable WGA; chromosome-level preferred | Standard convention |
| Branch scale for vertebrates | 1.0 default | Cactus docs |
| Branch scale for plants | 0.5-0.7 | Tuning convention |
| Branch scale for bacteria | 0.3-0.5 | Tuning convention |
| LASTZ identity range | 60-99% practical; 50% with HoxD55 matrix | LASTZ docs |
| minimap2 -x asm5 | <= 5% divergence | minimap2 docs |
| minimap2 -x asm10 | <= 10% divergence | minimap2 docs |
| minimap2 -x asm20 | <= 20% divergence | minimap2 docs |
| MUMmer nucmer recommended identity | >= 70% | Marçais 2018 |
| Soft-masking required for WGA | >= 90% of TE families masked | Standard QC |
| HAL file size, vertebrate 100-genome | ~100-500 GB per HAL | Approximate; varies with masking |
| Cactus per-job CPU requirement | 4-16 cores per leaf | Cactus docs |
| Minigraph-Cactus haplotype count | tested at 90 human haplotypes | Hickey 2024 |
| LASTZ chain-net minimum chain length | 5000 bp default; tunable | UCSC convention |
| Toil retry limit | --retryCount 3 typical | Toil docs |
| Cactus dustmasking sensitivity | default sensitive; adjust per clade | Cactus configs |
| AnchorWave anchor minimum identity | 80% default; lower for distant species | AnchorWave docs |
| progressiveMauve maximum genomes (practical) | 20-30 | Darling 2010 |
| SibeliaZ minimum block size | 50 bp default; tunable | Minkin 2020 |
| HAL toolkit halLiftover precision | base-level for collinear; gap-aware for SV | Hickey 2013 |

## Progressive Cactus Standard Workflow

**Goal:** Build a multi-species reference-free WGA from N genomes.

**Approach:** Provide guide tree + per-species genome FASTA in `seqFile.txt` -> run `cactus` with Toil job store -> produce HAL -> extract MAF / synteny / annotation as needed.

```bash
# 1. Pre-mask genomes (softmask)
for fa in genomes/*.fa; do
    species=$(basename $fa .fa)
    BuildDatabase -name ${species}_DB $fa
    RepeatModeler -database ${species}_DB -threads 16
    RepeatMasker -lib ${species}_DB-families.fa -xsmall -pa 16 $fa
done

# 2. Prepare seqFile (tree + paths)
cat > seqFile.txt << 'EOF'
(((human:0.05, chimp:0.05):0.05, macaque:0.1):0.2, mouse:0.5);
human    genomes/human.fa.masked
chimp    genomes/chimp.fa.masked
macaque  genomes/macaque.fa.masked
mouse    genomes/mouse.fa.masked
EOF

# 3. Run Cactus
cactus jobStore_path seqFile.txt output.hal \
    --binariesMode local \
    --workDir /tmp/cactus_work \
    --maxCores 64 \
    --logFile cactus.log

# 4. Inspect HAL
halStats output.hal
# Reports: genome count, chromosome / contig count per genome, alignment column count

# 5. Extract MAF for downstream phyloP / conservation
hal2maf output.hal reference_genome ucsc.maf --refGenome human --chunkSize 1000000
```

For HPC deployment, use Toil's `--batchSystem slurm` or `--batchSystem kubernetes` for cluster-scale runs.

## LASTZ + UCSC Chain/Net Standard Pipeline

**Goal:** Pairwise WGA of a query genome to a reference, producing UCSC-format chain and net files.

**Approach:** LASTZ pairwise -> axtChain -> chainNet -> netSyntenic.

```bash
# 1. LASTZ pairwise alignment per chromosome
for chr in $(cut -f1 reference.fa.fai); do
    lastz reference.fa[multiple,unmask] query.fa[multiple,unmask] \
        --hspthresh=3000 --ydrop=9400 --gappedthresh=3000 \
        --ambiguous=iupac --inner=2000 --score=$LASTZ_PARAMS \
        --format=axt \
        > pairwise/${chr}.axt
done

# 2. Build chains. `axtChain` reads PSL when given `-psl`; for AXT input from lastz
# (`--format=axt`) drop the `-psl` flag, or emit PSL from LASTZ with `--format=psl` upstream.
for axt in pairwise/*.axt; do
    chr=$(basename $axt .axt)
    axtChain -linearGap=loose $axt reference.2bit query.2bit chains/${chr}.chain
done

# 3. Merge chains
chainMergeSort chains/*.chain > merged.chain
chainPreNet merged.chain reference.size query.size pre.chain

# 4. Build net (one-to-one selection)
chainNet pre.chain reference.size query.size \
    target.net query.net
netSyntenic target.net target.syntenic.net

# 5. Filter and convert
netToAxt target.syntenic.net pre.chain reference.2bit query.2bit final.axt
axtToMaf final.axt reference.size query.size final.maf
```

## Minigraph-Cactus for Pangenome Construction

**Goal:** Build a pangenome graph from related genomes (intra-species or sister-species).

**Approach:** Provide reference + alternative genomes -> minigraph for SV graph -> Cactus for base-level alignment.

```bash
# Prepare seqFile (similar to Cactus but designates reference)
cat > pangenome_seqs.txt << 'EOF'
reference   human.fa
hap1        haplotype1.fa
hap2        haplotype2.fa
hap3        haplotype3.fa
EOF

# Run minigraph-cactus
cactus-pangenome jobStore_path pangenome_seqs.txt \
    --outDir output_pangenome \
    --outName pangenome \
    --reference reference \
    --vcf \
    --gfa \
    --gbz \
    --indexCores 32 \
    --mapCores 32

# Outputs:
#   pangenome.gbz       Genome Browser Z compressed graph
#   pangenome.gfa.gz    Graph Fragment Assembly format
#   pangenome.vcf.gz    VCF for short variants from graph
#   pangenome.full.hal  Full Cactus HAL for downstream tools
```

For HPRC-scale (90 haplotypes), use `--mapCores 64 --indexCores 64` on a high-memory node. See [[pangenome-analysis]] for downstream graph analysis.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Cactus alignment column count >> LASTZ pairwise | Cactus includes ancestral alignment; pairwise is direct only | Cactus is expected to have more columns when integrating across siblings |
| minimap2 aligns 60%; LASTZ aligns 80% | Sensitivity differs at low identity | Use LASTZ for distant comparisons |
| LASTZ chain/net A-on-B differs from B-on-A | Reference bias | Use Cactus reference-free for unbiased multi-genome questions |
| Cactus HAL vs Multiz MAF disagree at deep node | Cactus reference-free; Multiz reference-anchored | Cactus is the modern standard; Multiz mostly superseded |
| AnchorWave finds collinearity in WGD region, LASTZ doesn't | AnchorWave WGD-aware; LASTZ unaware | AnchorWave correct for WGD lineages |
| Minigraph-Cactus VCF and Cactus pairwise differ | Pangenome graph integrates SV; pairwise reports relative to reference | Minigraph-Cactus is for variant-aware pangenome work |
| nucmer (MUMmer) and minimap2 disagree at 80% identity | nucmer more sensitive at higher identity; minimap2 faster | Either is fine; cross-validate |
| Cactus runs but HAL file empty for some genomes | Genome misnamed in seqFile or masking issue | Verify seqFile genome names match FASTA headers; verify masking |
| progressiveMauve / SibeliaZ vs Cactus on bacteria | Bacterial-specific aligners better-tuned for compact genomes | progressiveMauve / SibeliaZ preferred for bacterial work; Cactus is overkill |

**Operational rule for publication:** Multi-species WGA for comparative genomics uses Progressive Cactus with documented guide tree, masking, and Toil configuration. Pairwise reference alignments use LASTZ chain/net for UCSC tracks or minimap2 for fast pangenomics. Document choice of alignment tool, reference (if applicable), parameter values, and any non-default settings.

## Cohort Gotchas

- **Highly repetitive genomes (large mammals, plants):** memory consumption explodes; ensure >= 256 GB RAM per node
- **Centromeric / telomeric regions:** unalignable in most assemblies; Winnowmap2 for explicit telomere-to-telomere work; otherwise mask
- **Sex chromosomes:** different content; Cactus aligns where possible; downstream analyses must respect sex-chromosome specifics
- **Recently diverged inbred strains (e.g. mouse strains):** > 99% identity; minimap2 -x asm5 is fine; Cactus overkill
- **Pangenome with structural variants:** Minigraph-Cactus preferred over straight Cactus
- **Multi-region polyploids:** AnchorWave proali with ploidy specification; subgenome-aware

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Reference bias?" | Cactus is reference-free; or for pairwise pipelines, both directions reported |
| "Guide tree?" | Provided in seqFile; built from concatenated single-copy orthologs |
| "Masking?" | RepeatModeler2 species-specific + RepeatMasker softmask before WGA |
| "Tool choice?" | Cactus for multi-species (reference-free, scalable); LASTZ chain/net for single-pair (UCSC standard) |
| "Branch scale?" | Set to 1.0 for vertebrates; 0.5 for plants; documented |
| "Assembly quality?" | N50 reported; BUSCO completeness reported; chromosome-level preferred |
| "WGD?" | AnchorWave proali with explicit ploidy; or Cactus with subgenome assignment |
| "Reproducibility?" | Cactus version + Toil version + branch scale documented; jobStore path retained for restart |
| "HAL downstream?" | TOGA for annotation projection; hal2maf for phyloP / PhastCons; halSynteny for SV |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Cactus fails with "guide tree mismatch" | seqFile genome names don't match tree leaves | Verify exact name match in seqFile lines vs newick |
| Cactus memory exhaustion | Unmasked repeats | Pre-mask with RepeatMasker softmask |
| Toil restart fails | jobStore corruption | Restart from scratch with new jobStore |
| LASTZ produces 0 alignments | Sensitivity too strict | Lower `--hspthresh`; check seed-and-extend params |
| MAF from hal2maf huge | Default chunkSize too small | Increase `--chunkSize 10000000` for large genome |
| minimap2 SAM file empty | Wrong preset for divergence | Try `-x asm20` or LASTZ for distant comparison |
| HAL file unreadable in another tool | HAL version mismatch | Pin HAL toolkit version |
| Cactus produces many tiny alignment blocks | Branch scale too low | Increase `--branchScale` to 1.0 |
| nucmer maxmatch slow | Many MUMs (unmasked repeats) | Use `--mum` (unique) or mask repeats |
| AnchorWave reports few anchors | CDS GFF parsing issue | Verify GFF3 with `gene` and `CDS` features |
| TOGA fails with "no chain" | Cactus HAL not converted to chain | Use halSynteny + UCSC chain conversion |
| Cactus dead-locks on shared filesystem | Toil multi-node sync issue | Use AWS S3 / GCS jobStore for cloud |

## Tool Installation Notes

```bash
# Progressive Cactus (Docker / Singularity preferred for reproducibility)
docker pull quay.io/comparative-genomics-toolkit/cactus:latest
# Or via virtualenv
python3 -m venv cactus_env && source cactus_env/bin/activate && pip install cactus

# HAL toolkit (usually bundled with Cactus)
git clone https://github.com/ComparativeGenomicsToolkit/hal && cd hal && make

# LASTZ + UCSC kentUtils
conda install -c bioconda lastz ucsc-axt-chain ucsc-chain-merge-sort ucsc-chain-pre-net ucsc-chain-net ucsc-net-syntenic ucsc-net-to-axt

# MUMmer4
conda install -c bioconda mummer

# minimap2 + winnowmap2
conda install -c bioconda minimap2 winnowmap

# AnchorWave
conda install -c bioconda anchorwave

# progressiveMauve
conda install -c bioconda mauve

# SibeliaZ
conda install -c bioconda sibeliaz

# RepeatMasker / RepeatModeler2 (for masking)
conda install -c bioconda repeatmasker repeatmodeler

# Toil for HPC / cloud
pip install toil[all]
```

For Cactus on HPC, set up Toil with the appropriate batch system (`--batchSystem slurm`); for cloud, use Toil's S3/GCS support and a job store on shared cloud storage.

## References

- Armstrong J et al 2020 Nature 587:246 (Progressive Cactus)
- Hickey G et al 2024 Nat Biotech 42:663 (Minigraph-Cactus)
- Hickey G et al 2013 Bioinformatics 29:1341 (HAL toolkit)
- Kent WJ et al 2003 PNAS 100:11484 (UCSC chain/net)
- Schwartz S et al 2003 Genome Res 13:103 (LASTZ)
- Marçais G et al 2018 PLoS Comp Biol 14:e1005944 (MUMmer4)
- Li H 2018 Bioinformatics 34:3094 (minimap2)
- Li H 2021 Bioinformatics 37:4572 (minimap2 long-read updates)
- Song B et al 2022 PNAS 119:e2113075119 (AnchorWave)
- Darling AE et al 2010 PLoS One 5:e11147 (progressiveMauve)
- Minkin I & Medvedev P 2020 Nat Commun 11:6327 (SibeliaZ)
- Jain C et al 2022 Nat Methods 19:705 (Winnowmap2)
- Blanchette M et al 2004 Genome Res 14:708 (Multiz)
- Brudno M et al 2003 GR 13:721 (LAGAN)
- Liao W-W et al 2023 Nature 617:312 (HPRC draft pangenome)
- Sirén J et al 2024 Nat Methods 21:2017 (vg personalized pangenome references). The vg-Giraffe pangenome mapper is Sirén J et al 2021 Science 374:abg8871.
- Garrison E et al 2024 Nat Methods 21:2008 (PGGB)
- Paten B et al 2011 Genome Res 21:1512 (Cactus algorithm)
- ComparativeGenomicsToolkit Cactus + HAL toolkit documentation (https://github.com/ComparativeGenomicsToolkit)

## Related Skills

- comparative-genomics/synteny-analysis - Synteny detection from WGA (Cactus -> halSynteny)
- comparative-genomics/comparative-annotation-projection - TOGA + CESAR uses Cactus HAL
- comparative-genomics/pangenome-analysis - Minigraph-Cactus / PGGB for pangenome graph construction
- comparative-genomics/whole-genome-duplication - Ks-dating uses WGA-derived gene pair alignments
- alignment/multiple-alignment - MAFFT / MUSCLE for protein MSA from WGA-derived orthologs
- alignment/pairwise-alignment - LASTZ / minimap2 / MUMmer for sequence-level comparison
- alignment/structural-alignment - WGA-extracted protein orthologs for downstream alignment
- genome-assembly/assembly-qc - BUSCO / Compleasm checks before WGA
- variant-calling/structural-variant-calling - WGA-based SV detection from genome assemblies
- causal-genomics/heritability-partitioning - LDSC partitioning using phyloP scores from Cactus HAL
<!-- END FILE: comparative-genomics/whole-genome-alignment/SKILL.md -->

## 子目录：comparative-genomics/whole-genome-duplication

<!-- BEGIN FILE: comparative-genomics/whole-genome-duplication/SKILL.md -->
---
name: bio-comparative-genomics-whole-genome-duplication
description: Detect, date, and contextualize whole-genome duplication (WGD / paleopolyploidy) events using wgd v2 (Chen et al 2024), KsRates (Sensalari 2022 substitution-rate-corrected Ks dating), DupGen_finder (Qiao 2019), MAPS (Li 2018 phylogenomic), POInT (Conant 2008 ordered-block), SLEDGe (2024 ML-based), Whale.jl (Bayesian DL+WGD), and synteny-anchored paranome construction. Use when identifying ancient polyploidy from Ks distributions and synteny block analysis, positioning WGD events relative to speciation, distinguishing tandem from segmental from WGD duplications, dating the 2R/3R vertebrate / fish / salmonid WGDs, building paranome and Ks-age mixture models, applying KsRates substitution-rate correction across lineages, or testing alternative biased-fractionation / dosage-balance models post-WGD.
tool_type: mixed
primary_tool: wgd
---

## Version Compatibility

Reference examples tested with: wgd v2.0.31+ (heche-psb/wgd; Chen et al 2024 Bioinformatics 40:btae272), KsRates 1.1.3+ (VIB-PSB/ksrates; Sensalari 2022 Bioinformatics 38:530), DupGen_finder (Qiao 2019 Genome Biol 20:38), MAPS 1.0 (Li 2018), POInT (Conant lab), SLEDGe (bioRxiv 2024.01.17.574559), Whale.jl 2.0+, ksrates pip 1.1+, MCScanX 1.0+, PAML 4.10+ (yn00/codeml for Ks), BLAT 36+, DIAMOND 2.1+, R 4.4+, mclust 6.1+ (for mixture models). Python 3.10+ required for wgd v2.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `wgd --version`; `ksrates --version`; `wgd ksd --help`
- Python: `pip show wgd ksrates`
- R: `packageVersion('mclust')`

If code throws `wgd ksd: cannot find PAML output`, `KsRates: insufficient sister species`, `MAPS: missing tree`, these tools have specific input expectations: wgd needs codon-aware MAFFT/MUSCLE alignment; KsRates needs configured `config_ksrates.txt`; MAPS needs nucleotide tree. The deprecated arzwa/wgd v1 is replaced by heche-psb/wgd v2.

# Whole Genome Duplication Analysis

**"Are there WGD events in this lineage and when did they occur?"** -> WGD detection combines **Ks distributions** (synonymous-substitution rates between gene paralog pairs, showing peaks at past polyploidy events) and **synteny block analysis** (parallel collinear blocks within a genome). Modern best practice uses **wgd v2** (Chen et al 2024 Bioinformatics 40:btae272) as an integrated pipeline. **KsRates** (Sensalari 2022 Bioinformatics 38:530) is mandatory for cross-lineage comparison because substitution rates vary across the tree -- ignoring this places WGDs incorrectly relative to speciation events. The fundamental tradeoff: Ks plot peaks are visually obvious but biologically ambiguous between (1) small-scale tandem duplications, (2) segmental duplications, and (3) true WGD; combining Ks with synteny anchors disambiguates these.

- CLI: `wgd dmd` and `wgd ksd` -- paranome construction + Ks distribution
- CLI: `wgd syn` -- synteny-anchored WGD signal extraction
- CLI: `ksrates init` then `ksrates wgd-paralogs ortho` -- substitution-rate-corrected positioning
- CLI: `MCScanX -h` then `dupgen_finder` -- duplication-class assignment
- CLI: `mapsR` -- gene-tree-based WGD phylogenetic placement

## Algorithmic Taxonomy

| Tool | Approach | Output | Strength | Fails when |
|------|----------|--------|----------|------------|
| wgd v2 (Chen et al 2024 Bioinformatics 40:btae272) | Integrated paranome + Ks + synteny + WGD dating | Ks distributions, collinearity plots, GMM/ELMM mixture fits, dating | Standard 2024 pipeline; replaces deprecated arzwa/wgd v1 | Saturation at Ks > 2; single-lineage substitution rate variation |
| KsRates (Sensalari 2022 Bioinformatics 38:530) | Substitution-rate correction via outgroup pairs | Adjusted Ks ages of focal-species paralogs vs orthologs | MANDATORY when comparing WGDs across lineages with different rates | Requires at least 2 outgroups for rate calibration |
| DupGen_finder (Qiao 2019 Genome Biol 20:38) | Classifies duplications by genomic context | Per-gene class: tandem, proximal, transposed, dispersed, WGD | Disambiguates duplication type | Class assignment depends on intervening-gene-count windows |
| MAPS (Li 2018) | Phylogenomic placement of WGD via gene-tree topology mapping | WGD position on species tree | Detects WGDs from gene-tree-species-tree discordance | Computationally heavy; requires many gene trees |
| POInT (Conant & Wolfe 2008 Genetics 179:1681) | Order-aware reconstruction of WGD chromosomes | Reconstructed ancestral WGD genome | Strong inference for syntenic-block ages | Lineage-specific tuning required |
| SLEDGe (bioRxiv 2024.01.17.574559) | ML classifier on Ks plot features | WGD vs no-WGD binary call + confidence | Reduces visual-peak-fitting subjectivity | Newer; less validated |
| wgd v1 (arzwa/wgd; DEPRECATED) | Predecessor of v2 | -- | Historical | Use v2 (heche-psb/wgd) |
| Whale.jl (Zwaenepoel & Van de Peer 2019 MBE 36:1384) | Bayesian DL + WGD reconciliation | WGD posterior at species-tree nodes | Native WGD modeling; integrates with [[gene-tree-species-tree-reconciliation]] | Julia ecosystem |
| WGDexploreR (legacy) | Visualize Ks plots | Plots only | Visualization aid | Not for inference |
| McLuster-WGD (custom workflows) | Mixture-model fitting on Ks | GMM / ELMM components | For custom peak fitting | Not a standard tool |
| ksrates web (sensalari 2022) | Web interface to ksrates | Same as CLI | User-friendly | Manual config; not scriptable for genome-wide |
| wgs2pep (Vandepoele/wgs) | Pep-to-WGD ortholog identification | Per-paralog WGD assignment | Plant-focused | Less general |

Methodology evolves; verify the current wgd v2 manual and the Chen & Zwaenepoel 2023 review chapter (in *Polyploidy: Methods and Protocols*) before locking on a single workflow. The 2R vertebrate / 3R teleost / Ss4R salmonid WGDs are well-established; novel WGD claims require concordance across Ks, synteny, and phylogenomic placement.

## Decision Tree by Experimental Scenario

| Scenario | Recommended approach | Why |
|----------|------------------------|-----|
| Plant comparative genomics; suspect WGD | wgd v2 + KsRates | Modern standard pipeline; plants are WGD-prone |
| Vertebrate 2R or 3R WGD analysis | wgd v2 + MAPS phylogenomic placement | Vertebrate-specific; combines Ks + tree topology |
| Salmonid Ss4R WGD | Whale.jl with WGD node in species tree | Native WGD modeling in Bayesian framework |
| Distinguish WGD from sequential small duplications | Ks GMM fit + synteny block analysis (wgd syn) | Ks peak alone insufficient; synteny confirms |
| Date WGD relative to a speciation event | KsRates with outgroup speciation calibration | Required when substitution rates differ |
| Identify duplicates retained vs lost after WGD | DupGen_finder + Ks distribution | Classification + age estimation |
| Detect novel WGD in non-model organism | wgd dmd -> wgd ksd -> visual GMM/ELMM mixture | Standard discovery workflow |
| Reconstruct ancestral WGD genome architecture | POInT | Order-aware ancestral reconstruction |
| Test post-WGD bias in fractionation (dosage-balance) | DupGen_finder + per-gene functional annotation | Compare retained vs lost genes |
| Distinguish recent vs ancient WGD | KsRates + Ks peak location after correction | Ks peak < 0.1 recent; 0.5-1.5 ancient |
| WGD in clade with rapid evolution (e.g. fish) | KsRates mandatory | Without rate correction, Ks peaks displaced |
| ML classification of WGD signal | SLEDGe | Newer ML-based alternative to manual fitting |
| Integrate WGD with DTL inference | Whale.jl OR ALE with WGD branch | See [[gene-tree-species-tree-reconciliation]] |
| Pan-clade WGD survey (e.g. all angiosperms) | wgd v2 batch + ksrates aggregated | Standard for sustained phylogenomic surveys |
| Polyploid genome with subgenomes | DupGen_finder for tandem/transposed + AnchorWave proali for subgenome-aware synteny | Subgenome assignment first |
| Recently diverged species pair, possible recent WGD | minimap2 -x asm5 + SyRI + Ks distribution | High-resolution recent-WGD detection |

## Per-Tool Failure Modes

### Saturation at Ks > 2

**Trigger:** Computing Ks for ancient WGD candidates from distantly related taxa.

**Mechanism:** Synonymous substitutions saturate after Ks ~2; each site has undergone multiple substitutions. Observed Ks underestimates true Ks; the relationship between Ks and time becomes non-monotonic above 1.5. WGD peaks at age 200+ Myr in vertebrates / 100+ Myr in plants are at Ks > 2 and unreliable (Vanneste 2013 MBE 30:177).

**Symptom:** wgd ksd output shows peak at Ks > 1.5 with broad distribution; KsRates rate-corrected Ks even more uncertain; visual fitting yields ambiguous components.

**Fix:** Restrict Ks-based WGD inference to Ks < 1.5; for older WGDs, use phylogenomic methods (MAPS, POInT, Whale.jl) which don't rely on Ks alone. Report Ks-based dating with explicit saturation caveat. For 2R vertebrate WGD (~500 Myr), MAPS / Whale.jl is required because Ks is saturated.

### Substitution-rate variation across lineages

**Trigger:** Comparing WGD position in two lineages with different molecular evolutionary rates.

**Mechanism:** If lineage A evolves twice as fast as lineage B, the same biological time is at twice the Ks in lineage A. A WGD at Ks = 0.5 in lineage A and Ks = 0.25 in lineage B might be the same event biologically.

**Symptom:** WGD claimed at "different times" in different lineages; speciation-vs-WGD relative timing flips depending on which lineage is the focal species.

**Fix:** Always use KsRates (Sensalari 2022) when comparing WGDs across lineages. KsRates uses outgroup-species speciation events to calibrate the relative substitution rates, then rescales Ks to a common scale. Single-lineage Ks dating is unreliable for inter-lineage comparison.

### Tandem duplication masquerading as WGD peak

**Trigger:** Ks distribution shows a peak at low Ks (< 0.5); user concludes "recent WGD."

**Mechanism:** Tandem duplications create paralog pairs with low Ks; these accumulate in clusters (especially in NLR genes in plants, OR genes in mammals). The Ks peak reflects clustered tandem origins, not WGD.

**Symptom:** "WGD" peak Ks-distribution is dominated by paralogs from tandem clusters; synteny analysis shows few cross-chromosome parallel blocks.

**Fix:** Use DupGen_finder to classify each paralog pair as tandem / proximal / transposed / dispersed / WGD. The true WGD signal comes from the WGD-classified pairs. Recompute Ks distribution restricted to WGD-classified pairs (or anchor-pair restricted to synteny blocks). wgd v2 integrates this filtering.

### Synteny block age inconsistency

**Trigger:** Different synteny blocks from the same suspected WGD have different Ks distributions.

**Mechanism:** Real WGD blocks should share a synchronized Ks distribution centered at the WGD age; if blocks have very different ages, the inferred "WGD" was probably a series of segmental duplications.

**Symptom:** Per-block Ks median varies widely; some blocks show Ks ~ 0.3 and others Ks ~ 1.0; not consistent with single WGD.

**Fix:** Compute per-block Ks distribution; require synchronization (interquartile range overlapping across blocks). wgd v2 reports per-block age dispersion. If dispersion is high, downgrade to "potentially WGD-like" or attribute to ancient segmental duplication history.

### Mixture model under/overfitting components

**Trigger:** Fitting GMM (gaussian mixture model) or ELMM (exponential-lognormal mixture model) to Ks distribution.

**Mechanism:** Mixture models with too few components miss real WGD signal; too many components find spurious peaks. BIC-based model selection is standard but sensitive to bin choice in histograms.

**Symptom:** Different runs with different bin counts give different component numbers; visual peaks don't match component means.

**Fix:** Use BIC-based component selection with 5-fold cross-validation; report uncertainty in component count. wgd v2 fits both GMM and ELMM and reports BIC for each model up to 5 components. Visually validate against synteny block analysis.

### Comparing wgd v1 (deprecated) vs v2 outputs

**Trigger:** Mixing scripts written for arzwa/wgd v1 with heche-psb/wgd v2.

**Mechanism:** wgd v1 was deprecated 2023; v2 has different command-line interface, default parameters, and output file structure. Scripts from v1 fail or produce different results in v2.

**Symptom:** Older scripts using `wgd ksd` v1 syntax don't work in v2; output paths differ.

**Fix:** Update all scripts to wgd v2 syntax. The v1 wgd is no longer maintained; v2 is the current standard.

### KsRates failing with insufficient species

**Trigger:** Running KsRates with one focal species and one outgroup.

**Mechanism:** KsRates calibrates substitution-rate variation via at least two outgroup speciation events; one outgroup species provides only one rate point and cannot resolve rate heterogeneity.

**Symptom:** KsRates errors or produces unreliable rate-corrected Ks.

**Fix:** Include >= 2 outgroup species at different phylogenetic distances; for plants, a model angiosperm + gymnosperm pair; for vertebrates, lamprey + invertebrate outgroup. Document outgroup sampling.

### Polyploid genome confusion

**Trigger:** Running wgd v2 on an unassigned-subgenome polyploid (e.g. wheat hexaploid without A/B/D subgenome labels).

**Mechanism:** WGD signal is muddled when subgenomes are not separated; orthologs across subgenomes appear as paralogs, intermixing tandem / segmental / WGD / homeolog signal.

**Symptom:** Ks distribution shows multiple overlapping peaks at varying intensities; component fits are unstable.

**Fix:** Assign subgenomes first using k-mer methods (KMC2 + SubPhaser; Jia 2022 New Phytol 235:801) or synteny-based assignment (GENESPACE; Lovell 2022). Then run wgd v2 on each subgenome separately. Document subgenome assignment.

### Confusion of homeologous (WGD) vs orthologous (speciation) pairs

**Trigger:** Computing Ks across recent WGD species without explicit homeolog labeling.

**Mechanism:** In recent WGD lineages (e.g. salmonid Ss4R), the "ortholog" between species and the "homeolog within species" can have similar Ks; standard ortholog detection (OrthoFinder) lumps both.

**Symptom:** wgd v2 reports Ks distributions but doesn't distinguish homeologs from orthologs; downstream dating confused.

**Fix:** Use synteny-anchored ortholog detection (GENESPACE, ProteinOrtho-synteny) to separate cross-species orthologs from within-species homeologs. Run wgd v2 separately on each class. Report each Ks distribution explicitly.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Ks saturation upper limit | Ks < 1.5 for reliable inference; >= 2 saturated | Vanneste 2013 MBE 30:177 |
| Recent WGD Ks range | Ks 0.1-0.5 | Standard convention |
| Ancient WGD Ks range | Ks 0.5-1.5 | Standard convention |
| WGD synteny block minimum | >= 5 anchors per block | wgd v2 / GENESPACE default |
| Tandem duplicate window for DupGen_finder | 5 genes default; species-tunable | Qiao 2019 |
| Proximal duplicate window | 5-25 genes | Standard |
| Number of mixture components to consider | 1-5 with BIC selection | wgd v2 default |
| Cross-block age synchrony for WGD | per-block Ks IQR overlap | Visual + statistical |
| KsRates minimum outgroups | >= 2 species at different distances | Sensalari 2022 |
| KsRates substitution rate correction valid range | Ks < 1.5 in original; correction can extend slightly | KsRates docs |
| MAPS minimum gene trees | >= 1000 single-copy ortholog trees | Li 2018 |
| Whale.jl WGD detection power | depends on retention rate; > 0.3 retention typically detectable | Zwaenepoel 2019 |
| Vertebrate 2R Ks | saturated; estimated 500-700 Myr | Dehal 2005 |
| Teleost 3R Ks | saturated; estimated 250-350 Myr | Glasauer 2014 |
| Salmonid Ss4R Ks | 80-100 Myr; Ks ~0.1-0.2 | Lien 2016 |
| Plant 1R / 2R | varies clade; core-eudicot gamma paleohexaploidy ~120 Myr | Jiao 2012 (dating); Soltis 2009 (placement) |
| Synonymous codon site count | dS reliable when >= 30 synonymous sites per pair | Yang 2007 PAML |
| Per-pair gene length minimum | >= 300 bp CDS | wgd v2 default |
| Codon-aware MSA aligner | MAFFT --auto or MUSCLE; for distant pairs PRANK | wgd v2 supports all |
| Bootstrap support for MAPS | >= 80 on gene-tree branches | Li 2018 |

## wgd v2 Standard Workflow

**Goal:** Detect and date WGD events from a focal-species proteome and CDS, with synteny-anchored Ks distribution.

**Approach:** Build paranome -> compute Ks distribution -> identify synteny anchors -> mixture model fit -> visualize.

```bash
# Install (Python 3.10+ required)
pip install wgd

# 1. Build paranome (all-vs-all paralog identification)
wgd dmd cds.fasta -o output/paranome.tsv -t 16

# 2. Compute Ks distribution
# Verify exact flags with `wgd ksd --help` (the wgd v2 CLI evolves; --pairwise / --ks-method spelling differs across versions).
wgd ksd output/paranome.tsv cds.fasta -o output/ksd \
    --aligner mafft --n-threads 16

# 3. Synteny anchors (intra-genome)
wgd syn output/paranome.tsv gff.bed cds.fasta -o output/syn \
    --feature gene --gene-attribute Name --min-block-size 5

# 4. Mixture model on synteny-anchored Ks
wgd mix output/ksd/ks_distributions.tsv -o output/mix \
    --model both --components 1 2 3 4 5

# 5. Visualize
wgd viz output/mix/mix_results.tsv -o output/viz \
    --type histogram --bins 50
```

```python
'''Parse wgd v2 outputs and identify WGD peak from Ks distribution.'''
import pandas as pd
from scipy import stats


def load_ks_distribution(ksd_file):
    '''Load wgd ksd output: pair  Ks  Ka  ...'''
    df = pd.read_csv(ksd_file, sep='\t')
    # Filter saturated
    df_filt = df[(df['Ks'] > 0) & (df['Ks'] < 2)]
    return df_filt


def fit_mixture(ks_values, n_components=3):
    '''Fit GMM (gaussian mixture model) on Ks via sklearn.'''
    from sklearn.mixture import GaussianMixture
    gmm = GaussianMixture(n_components=n_components, random_state=42)
    gmm.fit(ks_values.reshape(-1, 1))
    return {
        'means': gmm.means_.flatten(),
        'variances': gmm.covariances_.flatten(),
        'weights': gmm.weights_,
        'bic': gmm.bic(ks_values.reshape(-1, 1))
    }


def identify_wgd_peaks(ks_values, min_components=1, max_components=5):
    '''BIC-based model selection.'''
    results = {}
    for n in range(min_components, max_components + 1):
        results[n] = fit_mixture(ks_values, n)
    best_n = min(results.keys(), key=lambda k: results[k]['bic'])
    return best_n, results[best_n]
```

## KsRates Substitution-Rate-Corrected Workflow

**Goal:** Position a focal-species WGD relative to speciation events with substitution-rate correction.

**Approach:** Define focal species + 2+ outgroups -> compute orthologous Ks (focal vs outgroup) -> compute paralogous Ks (focal-internal) -> rescale via outgroup calibration.

```bash
# KsRates is best driven through its Nextflow pipeline (which orchestrates ortholog Ks,
# paralog Ks, rate correction, and plotting). Subcommand naming differs across releases;
# always verify with `ksrates --help` against the installed version.

# 1. Generate a working config (subcommand spelling varies by release; e.g. `init` in some,
#    `generate-config` in others). Inspect `ksrates --help`.
ksrates init config_ksrates.txt        # OR: ksrates generate-config config_ksrates.txt

# 2. Edit config_ksrates.txt to set focal_species, outgroups, FASTA + GFF paths, tree.

# 3. Run the full pipeline (Nextflow-driven):
ksrates --config config_ksrates.txt --n-threads 16
# Or invoke individual stages (subcommand names: see `ksrates --help`).
```

The output plot shows the rate-corrected focal-species paralog Ks distribution with vertical lines indicating outgroup-species speciation events; WGD peaks before vs after speciation events can be distinguished.

## DupGen_finder for Duplication Class Assignment

**Goal:** Classify each paralog pair as tandem / proximal / transposed / dispersed / WGD by genomic context.

**Approach:** MCScanX collinearity + intervening-gene count -> classify each duplicate by class.

```bash
# Input: MCScanX collinearity file + GFF
git clone https://github.com/qiao-xin/DupGen_finder
cd DupGen_finder

# Run with intervening-gene count
./DupGen_finder.pl \
    -i input_collinearity_file \
    -t species_name \
    -c gene_count_file \
    -o output

# Output: tandem, proximal, transposed, dispersed, wgd duplicate lists
```

```python
'''Aggregate DupGen_finder output for downstream Ks distribution per class.'''
def load_dupgen(class_dir):
    classes = {}
    for cls in ('tandem', 'proximal', 'transposed', 'dispersed', 'wgd'):
        path = f'{class_dir}/{cls}.pairs'
        try:
            classes[cls] = pd.read_csv(path, sep='\t', header=None,
                                       names=['gene1', 'gene2'])
        except FileNotFoundError:
            classes[cls] = pd.DataFrame(columns=['gene1', 'gene2'])
    return classes
```

## MAPS Phylogenomic WGD Placement

**Goal:** Place a WGD event on a species tree using gene-tree-species-tree mapping.

**Approach:** Build many single-copy ortholog gene trees -> map each tree's topology to the species tree -> identify branches with topology consistent with a WGD event.

MAPS is heavyweight; requires CRG database setup and significant compute. See https://bitbucket.org/barker-lab/maps/src for the current pipeline.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| wgd v2 peak at Ks 0.5, MAPS supports WGD on different branch | Rate variation across lineages | KsRates with outgroups; trust rate-corrected position |
| Ks peak prominent, synteny anchors sparse | Tandem-driven peak | DupGen_finder classification; verify WGD class |
| Synteny blocks present, Ks peak diffuse | Old WGD; saturated Ks | Restrict to recent paralogs; expect Ks 0.5-1.5 |
| One outgroup's KsRates says WGD before speciation, other after | Outgroup substitution rate variation | Use multiple outgroups; report ranges; explicit caveat |
| GMM fits 2 components, ELMM fits 3 | Model class differs | Visual inspection; report both; choose by BIC |
| DupGen_finder calls "WGD" but Ks > 2 | Saturation | Ks unreliable; verify via synteny + phylogenomic placement |
| Two recently sequenced sister species disagree on WGD date | Different annotation pipelines | Re-annotate consistently; verify orthology |
| wgd v2 detects WGD; Whale.jl posterior doesn't | Different inference frameworks | Whale.jl is Bayesian and gene-tree-based; trust if MAPS / phylogeny supports |
| Salmonid Ss4R detectable by wgd v2 in young salmonids | Recent WGD; clearer signal | Confirmation, not contradiction |

**Operational rule for publication:** Concordance across Ks distribution (wgd v2), synteny-anchored block analysis (wgd syn / GENESPACE), KsRates rate-corrected positioning, and at least one phylogenomic method (MAPS / Whale.jl / ALE with WGD node) = publication-grade WGD claim. Single-Ks-peak claims should be downgraded to "Ks evidence for possible WGD."

## Cohort Gotchas

- **Plant WGD legacy:** All angiosperms share at least one ancestral WGD (the epsilon event, ~192 Myr); the core-eudicot gamma paleohexaploidy is younger (~120 Myr; Jiao 2012 Genome Biol 13:R3), core-eudicot-specific (Soltis 2009 Am J Bot 96:336); confirm consensus against published plant lineages
- **Vertebrate 2R:** ~500-600 Myr; Ks saturated; use MAPS phylogenomic placement (Dehal & Boore 2005)
- **Teleost 3R:** ~320 Myr; in addition to 2R; doubles ohnologs in fish
- **Salmonid Ss4R:** ~80-100 Myr; recent enough that Ks is informative; ohnologs identifiable
- **Plant polyploids (wheat, Brassica):** recent; subgenomes assignable; subgenome-stratify before wgd v2
- **Allopolyploids vs autopolyploids:** allopolyploids have higher inter-subgenome divergence (easier to assign subgenomes); autopolyploids have similar subgenomes (chimeric assembly risk)
- **Lineage-specific extra duplications post-WGD:** make Ks peak broader; differentiate from sequential WGDs

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Saturation?" | Ks < 1.5 reported; for older WGDs, MAPS or Whale.jl used |
| "Rate variation?" | KsRates applied with 2+ outgroups; rate-corrected positioning |
| "Tandem vs WGD?" | DupGen_finder classification; WGD-class subset reported |
| "Synteny confirmation?" | wgd syn or GENESPACE; per-block Ks synchrony reported |
| "Phylogenomic support?" | MAPS, Whale.jl, or ALE-with-WGD agrees |
| "Mixture model uncertainty?" | BIC-based model selection; 1-5 components tested |
| "Subgenome assignment (polyploid)?" | k-mer-based or synteny-based subgenome assignment first |
| "Why wgd v2 over wgd v1?" | v1 deprecated 2023; v2 (heche-psb/wgd) is current |
| "Comparison to published WGD dates?" | Match published vertebrate 2R / teleost 3R / salmonid Ss4R; cite primary literature |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `wgd ksd` reports few Ks values | CDS sequences not in-frame or short | Verify CDS quality; filter short sequences |
| KsRates "no orthologs found" | Outgroup species names mismatched | Normalize species labels exactly |
| GMM fits with 5 components, all similar means | Overfitting | Use BIC; restrict max components to 3-4 |
| Per-block Ks IQR > 0.5 | Block age dispersion; likely segmental not WGD | Trust dispersion; reclassify as segmental |
| wgd v2 ELMM converges to single component | Insufficient pairs | Reduce filtering; include more paralog pairs |
| MAPS slow / OOM | Many gene trees; large dataset | Cluster; reduce to representative single-copy orthologs |
| Whale.jl Turing fails to mix | NUTS step size; tree dimension | HMC manual tuning; or reduce species tree |
| DupGen_finder produces empty tandem set | Default window inappropriate | Adjust window for genome density |
| Ks distribution has secondary peak at 1.8 | Saturation artifact (not WGD) | Recompute with PRANK or PAML codeml; restrict Ks < 1.5 |
| Polyploid "WGD" appears at Ks 0.05 | Recent polyploidy is ohnologous WGD, expected | Verify with subgenome assignment |
| Plant analysis lacks reference outgroup gymnosperm | KsRates needs gymnosperm + angiosperm | Add Selaginella or moss outgroup |

## Tool Installation Notes

```bash
# wgd v2
pip install wgd
# Or: git clone https://github.com/heche-psb/wgd && cd wgd && pip install .

# KsRates
pip install ksrates

# DupGen_finder (Perl + MCScanX dependency)
git clone https://github.com/qiao-xin/DupGen_finder
# Install MCScanX (Wang 2012): git clone https://github.com/wyp1125/MCScanX && cd MCScanX && make

# MAPS (Python; requires CRG, ete3)
git clone https://bitbucket.org/barker-lab/maps

# Whale.jl (Julia)
julia -e 'using Pkg; Pkg.add("Whale")'

# SLEDGe
git clone https://github.com/SLEDGe-team/SLEDGe

# POInT (C++)
git clone https://github.com/gconant0/PoInT
cd PoInT && make

# PAML for Ks computation (yn00 method)
conda install -c bioconda paml

# DIAMOND / BLAST for paranome
conda install -c bioconda diamond blast

# R packages
install.packages(c('mclust', 'rmixmod'))
```

For new analyses, default to wgd v2 + KsRates as the primary pipeline; MAPS or Whale.jl for confirmation on phylogenomic placement.

## References

- Chen H et al 2024 Bioinformatics 40:btae272 (wgd v2)
- Sensalari C et al 2022 Bioinformatics 38:530 (KsRates)
- Qiao X et al 2019 Genome Biol 20:38 (DupGen_finder)
- Li Z et al 2018 PNAS 115:4713 (MAPS phylogenomic WGD placement)
- Conant GC & Wolfe KH 2008 Genetics 179:1681 (POInT)
- Zwaenepoel A & Van de Peer Y 2019 MBE 36:1384 (Whale.jl)
- Sutherland BL et al 2024 bioRxiv 2024.01.17.574559 (SLEDGe ML classifier)
- Vanneste K et al 2013 MBE 30:177 (Ks saturation)
- Holland PWH et al 1994 Development Suppl:125 (2R hypothesis)
- Dehal P & Boore JL 2005 PLoS Biol 3:e314 (vertebrate 2R confirmation)
- Glasauer SMK & Neuhauss SCF 2014 Mol Genet Genomics 289:1045 (teleost 3R)
- Lien S et al 2016 Nature 533:200 (salmonid Ss4R)
- Soltis DE et al 2009 Am J Bot 96:336 (polyploidy and angiosperm diversification)
- Jiao Y et al 2012 Genome Biol 13:R3 (dates the core-eudicot gamma triplication)
- Birchler JA & Veitia RA 2007 Plant Cell 19:395 (gene balance hypothesis)
- Force A et al 1999 Genetics 151:1531 (subfunctionalization)
- Maere S et al 2005 PNAS 102:5454 (post-WGD retention bias)
- Tang H et al 2008 GR 18:1944 (synteny / MCScan)
- Lovell JT et al 2022 eLife 11:e78526 (GENESPACE)
- Jia K-H et al 2022 New Phytol 235:801 (SubPhaser subgenome assignment)
- Yang Z 2007 PAML manual (yn00 codon Ks)
- Chen H & Zwaenepoel A 2023 Methods Mol Biol 2545:3 (inference of ancient polyploidy from genomic data)

## Related Skills

- comparative-genomics/synteny-analysis - Synteny-anchored Ks (wgd syn / GENESPACE)
- comparative-genomics/ortholog-inference - Ortholog detection feeds DupGen / wgd
- comparative-genomics/gene-tree-species-tree-reconciliation - Whale.jl native WGD modeling; ALE with WGD branch
- comparative-genomics/gene-family-evolution - CAFE5 birth-death often shows post-WGD retention bias
- comparative-genomics/positive-selection - Selection on retained ohnologs (post-WGD diversification)
- comparative-genomics/ancestral-reconstruction - Ancestral pre-WGD gene state
- phylogenetics/divergence-dating - Time-calibrated WGD positioning
- alignment/multiple-alignment - Codon-aware MSA for Ks computation
- alignment/pairwise-alignment - Pairwise Ks via PAML yn00 / codeml
- genome-assembly/assembly-qc - BUSCO / Compleasm before WGD analysis
<!-- END FILE: comparative-genomics/whole-genome-duplication/SKILL.md -->

<!-- END CATEGORY: comparative-genomics -->

