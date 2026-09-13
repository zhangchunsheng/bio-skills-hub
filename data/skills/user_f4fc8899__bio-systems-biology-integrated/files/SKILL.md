---
slug: bio-systems-biology-integrated
version: 1.0.0
displayName: "系统生物学 / Systems biology"
name: bio-systems-biology-integrated
summary: >-
  中文：系统生物学综合技能，整合 7 个相关专题，覆盖系统生物学：基因组尺度代谢模型（COBRApy）、FBA/FVA、基因必需性、菌株设计、社区代谢模型。 English: Integrated Systems biology skill covering 7 related topics, including Systems biology: genome-scale metabolic models (COBRApy), FBA/FVA, gene essentiality, strain design, community metabolic models.
description: >-
  中文：这是一个面向系统生物学的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：系统生物学：基因组尺度代谢模型（COBRApy）、FBA/FVA、基因必需性、菌株设计、社区代谢模型。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：CarveMe, cobrapy, memote。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Systems biology, combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Systems biology: genome-scale metabolic models (COBRApy), FBA/FVA, gene essentiality, strain design, community metabolic models. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: CarveMe, cobrapy, memote. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# systems-biology 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: systems-biology -->

## 子目录：systems-biology/community-metabolic-modeling

<!-- BEGIN FILE: systems-biology/community-metabolic-modeling/SKILL.md -->
---
name: bio-systems-biology-community-metabolic-modeling
description: Builds and simulates multi-species metabolic community models from member genome-scale models, using MICOM for abundance-weighted steady-state community FBA and cooperative tradeoff, SMETANA for cross-feeding and competition scoring, and SteadyCom/COMETS for common-growth-rate and dynamic simulation. Use when modeling a microbiome or co-culture, predicting cross-feeding and competition, abundance-weighting members from metagenomics, choosing steady-state vs dynamic community modeling, avoiding the compartment-pooling artifact, or judging how member-model quality and namespace propagate into community predictions.
tool_type: python
primary_tool: micom
---

## Version Compatibility

Reference examples tested with: MICOM 0.33+, COBRApy 0.29+, Python 3.10+ (SMETANA and COMETS are separate installs)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: community FBA needs a QP solver for MICOM's cooperative tradeoff (HiGHS/CPLEX/Gurobi). Member models must share a namespace (BiGG vs ModelSEED), reconciled via MetaNetX before combining. SMETANA is a separate CLI (github.com/cdanielmachado/smetana); COMETS uses the cometspy toolbox.

# Community Metabolic Modeling

**"Model the metabolism of my microbial community"** -> Combine member genome-scale models into a community, then predict community growth, individual growth rates, and metabolite exchange (cross-feeding and competition) under a shared medium.
- Python: `micom.Community(taxonomy).cooperative_tradeoff()` (steady-state, abundance-weighted); SMETANA (cross-feeding scores); COMETS (dynamic)

## The governing principle: a community model inherits every member's errors, and the shared space is a modeling choice

Two things dominate whether a community prediction means anything:

- Reference-model quality propagates. A community model is only as good as its member reconstructions - a wrong biomass, a missing pathway, or an energy-generating cycle in one member distorts the whole community's exchange predictions. Curate members (systems-biology/model-curation) before combining, and confirm they share a namespace (BiGG vs ModelSEED); a namespace mismatch silently breaks metabolite sharing.
- How the shared space is modeled is the central design decision, and the classic trap is compartment pooling. Modeling a community as one giant "bag" with a single shared metabolite pool is fast but biologically wrong: it lets any member use any other member's INTERNAL metabolites directly, inventing cross-feeding that requires no secretion. The correct structure gives each member its own compartments and connects them only through a shared EXTRACELLULAR medium with explicit exchange. Pooling artifacts are a recurring reviewer catch. MICOM and SteadyCom implement the compartmentalized structure correctly; hand-merging models by prefix usually does not.

A further modeling fork: steady-state community FBA (SteadyCom, MICOM) assumes a stable coexistence with a common community growth rate, while dynamic simulation (COMETS, BacArena) resolves the time course and spatial structure but is expensive and parameter-hungry. Neither predicts the other's regime.

## Decision: which community method

| Goal | Tool | Approach / trade-off |
|------|------|----------------------|
| Metagenome-scale gut community, abundance-weighted, steady state | MICOM (Python) | community FBA with cooperative tradeoff (community vs individual growth); scales to many taxa from abundances |
| Cross-feeding / competition SCORES between members | SMETANA (CLI) | MRO (resource overlap = competition), MIP (interaction potential = cooperation), per-metabolite scores; pairs with CarveMe |
| Coexistence at a common community growth rate | SteadyCom | enforces one shared growth rate; elegant steady-state coexistence model |
| Time course / spatial dynamics, diffusion | COMETS / BacArena | dynamic (COMETS) or individual-based spatial (BacArena) FBA; realistic but expensive/parameter-hungry |

Do not model a community as one pooled "bag" model; use a tool that keeps members compartmentalized and connects them through a shared extracellular medium.

## Build and Simulate a Community with MICOM

**Goal:** Combine member models (weighted by their metagenomic abundance) and predict community and per-member growth under a medium.

**Approach:** Assemble a taxonomy table (one row per taxon with an `id`, a model `file`, and an `abundance`), build the `Community` (which compartmentalizes members correctly), and solve with cooperative tradeoff - which finds a community growth optimum while spreading growth across members rather than letting one taxon dominate. Reserve the `fraction` argument to trade community optimum against individual growth.

```python
from micom import Community
from micom.data import test_taxonomy

# taxonomy: columns id, file (per-taxon SBML), and abundance (from metagenomics). test_taxonomy()
# ships a ready E. coli example community.
taxonomy = test_taxonomy()

community = Community(taxonomy)            # builds the compartmentalized multi-species model
solution = community.cooperative_tradeoff(fraction=1.0)   # QP; needs HiGHS/CPLEX/Gurobi
print('community growth rate:', solution.growth_rate)
print(solution.members[['growth_rate']])  # per-taxon growth; NaN row is the shared medium
```

## Cross-Feeding and Competition (SMETANA)

```bash
# SMETANA (separate install) scores interactions between member models built by CarveMe:
#   pip install smetana   # then:
# smetana model1.xml model2.xml -o community --flavor bigg
# Outputs: MRO (metabolic resource overlap = competition for shared nutrients),
#          MIP (metabolic interaction potential = potential cooperation/cross-feeding),
#          and per-metabolite SMETANA scores (who feeds whom). A high MIP with low MRO
#          suggests cooperative cross-feeding; high MRO suggests competition.
```

## Dynamic and Spatial Simulation (COMETS)

```python
# For the time course rather than a steady state, COMETS (cometspy) runs dynamic FBA on a lattice
# with metabolite diffusion. Use when the QUESTION is temporal (succession, diauxie, spatial
# structure), not a coexistence steady state. It is far more expensive and needs kinetic parameters
# (uptake Vmax/Km, initial biomass, diffusion constants) that a steady-state model does not.
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cross-feeding predicted that needs no secretion | compartment pooling (single shared internal pool) | use MICOM/SteadyCom (compartmentalized); connect members only via a shared extracellular medium |
| Members will not exchange metabolites | namespace mismatch (BiGG vs ModelSEED IDs) | reconcile member models via MetaNetX before combining |
| Community growth nonsensical | a member model is broken (bad biomass, energy cycle) | curate each member first; a bad member poisons the community |
| `cooperative_tradeoff` errors on solver | it is a QP and GLPK cannot solve it | use HiGHS (bundled), CPLEX, or Gurobi |
| One taxon takes all the growth | plain community-max FBA has alternate optima | use cooperative tradeoff (spreads growth) and set abundances from data |
| Dynamic run is impossibly slow | COMETS/BacArena are expensive and parameter-hungry | use a steady-state method unless the question is genuinely temporal/spatial |

## Related Skills

- systems-biology/metabolic-reconstruction - Build the member models (CarveMe pairs with SMETANA)
- systems-biology/model-curation - Curate members before combining; errors propagate to the community
- systems-biology/flux-balance-analysis - Single-organism FBA underlying each member
- metagenomics/abundance-estimation - Member abundances to weight the community
- metagenomics/functional-profiling - Community-level metabolic potential from metagenomes

## References

- Diener C, Gibbons SM, Resendis-Antonio O. 2020. MICOM: metagenome-scale modeling to infer metabolic interactions in the gut microbiota. *mSystems* 5(1):e00606-19.
- Zelezniak A, Andrejev S, Ponomarova O, et al. 2015. Metabolic dependencies drive species co-occurrence in diverse microbial communities. *PNAS* 112(20):6449-6454. (SMETANA)
- Chan SHJ, Simons MN, Maranas CD. 2017. SteadyCom: predicting microbial abundances while ensuring community stability. *PLoS Comput Biol* 13(5):e1005539.
- Zomorrodi AR, Maranas CD. 2012. OptCom: a multi-level optimization framework for the metabolic modeling and analysis of microbial communities. *PLoS Comput Biol* 8(2):e1002363.
- Harcombe WR, Riehl WJ, Dukovski I, et al. 2014. Metabolic resource allocation in individual microbes determines ecosystem interactions and spatial dynamics. *Cell Rep* 7(4):1104-1115. (COMETS)
- Dukovski I, Bajic D, Chacon JM, et al. 2021. A metabolic modeling platform for the computation of microbial ecosystems in time and space (COMETS). *Nat Protoc* 16(11):5030-5082.
- Bauer E, Zimmermann J, Baldini F, Thiele I, Kaleta C. 2017. BacArena: individual-based metabolic modeling of heterogeneous microbes in complex communities. *PLoS Comput Biol* 13(5):e1005544.
- Machado D, Andrejev S, Tramontano M, Patil KR. 2018. Fast automated reconstruction of genome-scale metabolic models for microbial species and communities. *Nucleic Acids Res* 46(15):7542-7553.
<!-- END FILE: systems-biology/community-metabolic-modeling/SKILL.md -->

## 子目录：systems-biology/context-specific-models

<!-- BEGIN FILE: systems-biology/context-specific-models/SKILL.md -->
---
name: bio-systems-biology-context-specific-models
description: Builds tissue-, cell-type-, and condition-specific metabolic models by integrating transcriptomic or proteomic data into a generic genome-scale model, using extraction algorithms (GIMME, iMAT, INIT/tINIT, MADE, E-Flux, CORDA, FASTCORE) via troppo and corda in Python or the COBRA Toolbox/RAVEN in MATLAB. Use when pruning a generic model to a context, choosing an extraction method and expression threshold, mapping expression through GPR rules to reactions, deciding whether an objective is required (GIMME vs iMAT), avoiding the growth-objective trap for non-proliferating tissue, or judging how much of a context-specific model is real signal versus an artifact of the threshold and method.
tool_type: python
primary_tool: cobrapy
---

## Version Compatibility

Reference examples tested with: COBRApy 0.29+, corda 0.5+, numpy 1.26+, pandas 2.2+, Python 3.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: COBRApy core does NOT implement GIMME/iMAT/INIT. Real Python implementations live in `troppo` (multi-method) and `corda` (CORDA); the reference multi-method implementations are the MATLAB COBRA Toolbox `createTissueSpecificModel` and RAVEN (INIT/tINIT). Do not expect a `cobra.flux_analysis.gimme()`; it does not exist.

# Context-Specific Models

**"Build a liver-specific metabolic model from my expression data"** -> Prune/constrain a generic genome-scale model to the reactions an extraction algorithm judges active in that context, given omics data mapped through GPR rules and a threshold.
- Python: `corda.CORDA` (CORDA), `troppo` (GIMME/iMAT/tINIT/FASTCORE/CORDA); MATLAB: COBRA Toolbox `createTissueSpecificModel`, RAVEN (COBRApy for downstream FBA)

## The governing principle: the threshold and method are the experiment, not the data

Two facts govern every context-specific model:

- Expression is NOT flux. A highly transcribed gene need not carry high flux (post-transcriptional regulation, allostery, kinetics decouple mRNA from enzyme activity), and an absent transcript does not prove its reaction is off. Absence is a moderately strong constraint; presence is a weak one. mRNA -> enzyme -> flux is a lossy chain, and every extraction method encodes a DIFFERENT guess about that chain.
- Method choice and thresholding dominate the result more than the biology does. Systematic evaluations found that no extraction method reliably beats the others, and that expression-integration methods often fail to beat parsimonious FBA, which uses NO expression at all; the choice of method x threshold x objective changes the model content MORE than the input data does (Machado & Herrgard 2014; Opdam 2017; Richelle 2019). The single on/off threshold is the highest-leverage hidden decision. Consequence: report the method, the threshold strategy, and the objective as first-class methods, and treat a reaction whose inclusion flips with a plausible threshold change as a hypothesis, not a finding.

A corollary trap: GIMME-family methods require a protected objective (usually biomass). For a differentiated, non-proliferating tissue (hepatocyte, neuron), forcing a growth objective is a category error - those cells are not making copies of themselves. Use an objective-free method (iMAT) or a task-based one (tINIT) for non-growing tissue, or define a genuine maintenance/functional task instead of biomass.

## Decision: which extraction method

| Method | Objective/task required? | Expression handling | Best implementation | When |
|--------|--------------------------|---------------------|---------------------|------|
| GIMME (Becker & Palsson 2008) | Yes (biomass/task) | discrete threshold; penalize below-threshold flux | troppo (Py); COBRA Toolbox (MATLAB) | proliferating cells with a real objective |
| iMAT (Shlomi 2008; Zur 2010) | No | discrete high/low buckets (MILP) | troppo (Py); COBRA Toolbox (MATLAB) | non-growing human tissue; the common default |
| INIT / tINIT (Agren 2012/2014) | tINIT: metabolic TASKS | protein/HPA evidence + net accumulation | RAVEN (MATLAB) | task-guaranteed, functional tissue models |
| MADE (Jensen & Papin 2011) | No | differential significance, no absolute threshold; needs >=2 conditions | MATLAB (TIGER) | comparative/time-course designs |
| E-Flux (Colijn 2009) | No | expression sets continuous flux BOUNDS (no discretization) | custom (simple) | quick continuous constraint; no on/off decision |
| CORDA (Schultz & Qutub 2016) | No | 5 confidence classes; dependency-rescued | corda (Python, turnkey) | cancer/tissue models; "concise not minimal" |
| FASTCORE (Vlassis 2014) | core reaction set | core + minimal consistent extension | troppo (Py); COBRA Toolbox | fast, compact, given a trusted core |

Honest tooling reality: the most complete, best-validated implementations are MATLAB (COBRA Toolbox / RAVEN). In Python, `troppo` is the multi-method option and `corda` is the most turnkey native implementation. Steering a user to "just use COBRApy" for iMAT/GIMME sends them into reimplementing an algorithm.

## Map Expression Through GPR Rules

**Goal:** Convert per-gene expression into a per-reaction activity score that respects enzyme logic.

**Approach:** Evaluate the GPR with min for AND (a complex is limited by its scarcest subunit) and max for OR (any isozyme suffices). This min/max convention is standard but lossy - it discards the quantitative contribution of all but the limiting/dominant gene.

```python
def reaction_activity(rxn, gene_expr, default=0.0):
    '''Aggregate gene expression to a reaction score: min over AND (complex), max over OR (isozyme).'''
    if not rxn.genes:
        return default
    values = [gene_expr.get(g.id, default) for g in rxn.genes]
    return max(values)   # simplified OR; a full parser applies min within each AND-clause first
```

## CORDA in Python (a real, turnkey extraction method)

**Goal:** Reconstruct a context-specific model that keeps as many high-confidence reactions as possible while excluding absent ones, rescuing reactions that high-confidence ones depend on.

**Approach:** Translate expression into CORDA's five confidence classes (-1 absent, 0 unknown, 1 low, 2 medium, 3 high) via the GPR, then let CORDA build a "concise but not minimal" model.

```python
from corda import CORDA, reaction_confidence

# gene_conf maps gene id -> confidence in {-1, 0, 1, 2, 3}; derive it from expression quantiles.
gene_conf = {g.id: 2 for g in model.genes}
rxn_conf = {r.id: reaction_confidence(r, gene_conf) for r in model.reactions}   # pass the Reaction, not its GPR string

opt = CORDA(model, rxn_conf)
opt.build()
context_model = opt.cobra_model('liver')   # verify the exact accessor for the installed corda version
```

## Conceptual GIMME-Style Constraint (illustration only)

**Goal:** Show the objective-protected pruning idea GIMME encodes, for teaching - not as a substitute for a validated implementation.

**Approach:** Require the objective to stay above a floor, then penalize/limit flux through reactions whose genes are all below the expression threshold. A faithful GIMME solves a single LP with an inconsistency score; this stub only illustrates the shape and must not be reported as GIMME output.

```python
import numpy as np

def gimme_style_stub(model, gene_expr, low_quantile=0.25, growth_floor=0.1):
    '''Illustrative only. For real GIMME/iMAT use troppo or the COBRA Toolbox.'''
    cutoff = np.quantile(list(gene_expr.values()), low_quantile)
    low = {g for g, v in gene_expr.items() if v < cutoff}
    ctx = model.copy()
    biomass = str(model.objective.expression).split('*')[1].split()[0]
    ctx.reactions.get_by_id(biomass).lower_bound = growth_floor   # protect the objective
    for rxn in ctx.reactions:
        genes = {g.id for g in rxn.genes}
        if genes and genes <= low:
            rxn.bounds = (max(rxn.lower_bound, -1.0), min(rxn.upper_bound, 1.0))
    return ctx
```

## Thresholding: the make-or-break decision

```python
# The single on/off threshold moves the model more than the algorithm does. Options:
#  - Global: one cutoff across all genes/samples (simple; ignores gene-specific expression ranges).
#  - Local: a per-gene cutoff (e.g. a gene is "on" relative to its own distribution across samples).
#  - StanDep (Joshi 2020): clusters genes by expression pattern and thresholds per cluster; captures
#    housekeeping vs peaky genes that a single global cutoff mishandles.
# Always run a sensitivity check: rebuild at 2-3 thresholds and report which reactions/pathways are
# stable vs threshold-dependent. Report proteomics-derived scores separately; protein is closer to
# flux capacity than mRNA but still not flux.
#  - Single-cell input: scRNA-seq zeros are dominated by technical DROPOUT, which inverts the
#    "absence is a strong constraint" logic (a zero may be an unobserved, not an absent, transcript).
#    Aggregate to pseudobulk or metacells PER CELL TYPE before extraction (or use a single-cell-native
#    method); do not threshold individual cells. See single-cell/cell-annotation.
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AttributeError: cobra.flux_analysis has no gimme` | COBRApy ships no GIMME/iMAT/INIT | use troppo/corda (Python) or COBRA Toolbox/RAVEN (MATLAB) |
| Context model of a neuron/hepatocyte cannot satisfy biomass | GIMME-family objective forced on non-proliferating tissue | use iMAT (objective-free) or tINIT (task-based); do not protect biomass |
| Two analysts get different tissue models from the same data | threshold/method/objective differ | fix and report all three; run a threshold sensitivity sweep |
| Reaction present in data but pruned out | presence is a weak signal; the method judged it inactive in context | expected; do not over-trust presence, and check the GPR aggregation |
| Absent transcript but reaction kept | absence is only a moderate constraint; a dependency rescued it (CORDA) | inspect `opt.redundancies`/dependency rescue; decide if the rescue is justified |
| Model predicts overflow/Warburg poorly | expression pruning has no enzyme-capacity budget | use enzyme-constrained models (GECKO/sMOMENT) with proteomics |

## Related Skills

- systems-biology/flux-balance-analysis - Run FBA/FVA on the extracted context model
- systems-biology/gene-essentiality - Context-specific essentiality on the tissue model
- systems-biology/metabolic-reconstruction - The generic model these methods prune
- differential-expression/de-results - Expression input (bulk) for extraction
- single-cell/cell-annotation - Cell-type expression for cell-type-specific models

## References

- Becker SA, Palsson BO. 2008. Context-specific metabolic networks are consistent with experiments. *PLoS Comput Biol* 4(5):e1000082. (GIMME)
- Shlomi T, Cabili MN, Herrgard MJ, Palsson BO, Ruppin E. 2008. Network-based prediction of human tissue-specific metabolism. *Nat Biotechnol* 26(9):1003-1010. (iMAT method)
- Zur H, Ruppin E, Shlomi T. 2010. iMAT: an integrative metabolic analysis tool. *Bioinformatics* 26(24):3140-3142.
- Colijn C, Brandes A, Zucker J, et al. 2009. Interpreting expression data with metabolic flux models. *PLoS Comput Biol* 5(8):e1000489. (E-Flux)
- Jensen PA, Papin JA. 2011. Functional integration of a metabolic network model and expression data without arbitrary thresholding. *Bioinformatics* 27(4):541-547. (MADE)
- Agren R, Bordel S, Mardinoglu A, et al. 2012. Reconstruction of genome-scale active metabolic networks for 69 human cell types using INIT. *PLoS Comput Biol* 8(5):e1002518. (INIT; tINIT: Agren 2014 *Mol Syst Biol* 10:721)
- Schultz A, Qutub AA. 2016. Reconstruction of tissue-specific metabolic networks using CORDA. *PLoS Comput Biol* 12(3):e1004808. (CORDA)
- Vlassis N, Pacheco MP, Sauter T. 2014. Fast reconstruction of compact context-specific metabolic network models. *PLoS Comput Biol* 10(1):e1003424. (FASTCORE)
- Machado D, Herrgard M. 2014. Systematic evaluation of methods for integration of transcriptomic data into constraint-based models of metabolism. *PLoS Comput Biol* 10(4):e1003580.
- Opdam S, Richelle A, Kellman B, et al. 2017. A systematic evaluation of methods for tailoring genome-scale metabolic models. *Cell Syst* 4(3):318-329.
- Richelle A, Joshi C, Lewis NE. 2019. Assessing key decisions for transcriptomic data integration in biochemical networks. *PLoS Comput Biol* 15(7):e1007185.
- Joshi CJ, Schinn SM, Richelle A, et al. 2020. StanDep: capturing transcriptomic variability improves context-specific metabolic models. *PLoS Comput Biol* 16(5):e1007764.
<!-- END FILE: systems-biology/context-specific-models/SKILL.md -->

## 子目录：systems-biology/flux-balance-analysis

<!-- BEGIN FILE: systems-biology/flux-balance-analysis/SKILL.md -->
---
name: bio-systems-biology-flux-balance-analysis
description: Performs flux balance analysis (FBA), flux variability analysis (FVA), parsimonious FBA (pFBA), loopless FBA, flux sampling, and production envelopes on genome-scale metabolic models with COBRApy, solving the biomass-maximization linear program under a defined medium. Use when predicting growth rate on a carbon source, computing flux ranges and alternative optima (FVA), setting exchange bounds and minimal media, distinguishing a real growth phenotype from an under-constrained model, sampling the flux solution space, or choosing between FBA, pFBA, loopless FBA, and sampling for a flux distribution.
tool_type: python
primary_tool: cobrapy
---

## Version Compatibility

Reference examples tested with: COBRApy 0.29+, Python 3.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: the objective LP is solved by a backend solver. GLPK (the COBRApy default) can return degenerate or marginally-infeasible answers on large or ill-conditioned models; prefer HiGHS (if available in the installed cobra/optlang build) or a free academic CPLEX/Gurobi for genome-scale work and any MILP/QP method (loopless, MOMA). Set with `model.solver = 'glpk'|'highs'|'gurobi'|'cplex'`.

# Flux Balance Analysis

**"Predict growth rate and metabolic fluxes for my organism"** -> Solve a linear program over a genome-scale metabolic model that maximizes a biomass (or custom) objective subject to steady-state mass balance and exchange bounds, then quantify how much of that solution is actually determined.
- Python: `model.optimize()`, `cobra.flux_analysis.flux_variability_analysis()`, `pfba()`, `cobra.sampling.sample()` (COBRApy)

## The governing principle: FBA is an under-determined LP, so one solution is not "the" flux distribution

FBA imposes steady state (S*v = 0) plus bounds and maximizes an objective. The steady-state constraint is a pseudo-steady-state on fast-turnover metabolite POOLS, not on the organism. Critically, the optimal objective is usually reached on a whole FACE of the solution polytope, not a single point: many different internal flux vectors give the identical maximal growth. `model.optimize()` returns ONE arbitrary vertex of that face. Consequences that govern every downstream decision:

- The biomass/objective VALUE is typically robust and reproducible; individual internal FLUXES are often NOT. Never report a single `solution.fluxes[rxn]` as "the" flux without FVA (the range) or pFBA (a parsimonious representative) or sampling (the distribution).
- A nonzero growth rate is only as meaningful as the MEDIUM and the biomass reaction. An open or under-constrained exchange set inflates growth; a copied/generic biomass reaction encodes another organism's composition. "It grows" is often an artifact of an open exchange, not biology (see Common Errors).
- FBA predicts YIELDS and growth/essentiality well but internal flux magnitudes poorly. To validate actual intracellular fluxes, 13C metabolic flux analysis MEASURES them (metabolomics/isotope-tracing) - FBA does not.

## Decision: which analysis for which question

| Question | Method | Why |
|----------|--------|-----|
| Max growth rate / yield on a medium | FBA `model.optimize()` | single LP; objective value is the robust output |
| Is a reaction's flux determined, or free to vary? | FVA `flux_variability_analysis` | reports min/max flux at (near-)optimal growth; exposes alternate optima |
| One realistic representative flux vector | pFBA `pfba` | among optima, the one minimizing total flux (proxy for minimal enzyme cost) |
| Remove thermodynamically infeasible internal cycles | loopless (`loopless_solution`, or FVA `loopless=True`) | strips net flux around closed loops with no driving force |
| Full uncertainty / flux DISTRIBUTIONS, no objective needed | sampling `cobra.sampling.sample` | uniformly samples the solution space; use when the objective is unknown or confidence intervals are needed |
| Growth-vs-byproduct tradeoff for engineering | `production_envelope` | Pareto frontier of growth vs product secretion |
| Immediate knockout mutant flux (not re-optimized) | MOMA/ROOM -> gene-essentiality | minimal-adjustment, not re-optimization; see systems-biology/gene-essentiality |
| Overflow metabolism (acetate/Crabtree) missing | enzyme-constrained model (GECKO/sMOMENT) | plain FBA has no proteome budget; needs capacity constraints |

## Load Models

```python
import cobra

model = cobra.io.load_model('textbook')   # E. coli core (e_coli_core), 95 reactions, ships with cobra
model = cobra.io.load_model('iJO1366')    # genome-scale E. coli, 2583 reactions

model = cobra.io.read_sbml_model('model.xml')   # SBML (the standard exchange format)
model = cobra.io.load_json_model('model.json')  # COBRA JSON

# Curated genome-scale models: http://bigg.ucsd.edu/models (King 2016). Record the model
# version; predictions are only comparable within the same model release.
```

## Basic FBA and honest growth interpretation

**Goal:** Predict the maximum growth rate and a flux distribution under a defined medium, and judge whether the number is biological.

**Approach:** Load a model, confirm the objective is the intended biomass reaction, solve the LP, then read the objective value while treating individual fluxes as provisional until FVA/sampling confirms them.

```python
import cobra

model = cobra.io.load_model('textbook')

solution = model.optimize()
print(f'Objective (growth): {solution.objective_value:.4f} /h  status: {solution.status}')
print('Objective reaction:', str(model.objective.expression).split('*')[1].split()[0])

# A growth rate is interpretable ONLY against a stated medium and biomass reaction.
# Compare to a measured doubling time (mu = ln2 / t_double) rather than to a fixed
# "fast/slow" scale; absolute values are organism- and biomass-definition-specific.
```

## Set Medium (exchange bounds; uptake is a NEGATIVE lower bound)

**Goal:** Impose a defined nutrient environment so growth reflects the intended condition, not leftover open exchanges.

**Approach:** Close every exchange, then open only the intended uptakes. By COBRApy convention an exchange `EX_x_e` has flux < 0 for uptake and > 0 for secretion, so uptake is set through the lower bound. The `model.medium` dict is the concise idiom (its values are uptake magnitudes, positive).

```python
def set_minimal_medium(model, carbon_source='EX_glc__D_e', carbon_uptake=10):
    '''Close all uptake, then open a defined minimal medium.

    carbon_uptake in mmol/gDW/h; 10 is the standard E. coli aerobic glucose rate (iJO1366).
    '''
    for rxn in model.exchanges:
        rxn.lower_bound = 0

    minimal = {'EX_o2_e': 1000, 'EX_h2o_e': 1000, 'EX_h_e': 1000, 'EX_nh4_e': 1000,
               'EX_pi_e': 1000, 'EX_so4_e': 1000, 'EX_k_e': 1000, 'EX_mg2_e': 1000}
    for ex_id, uptake in minimal.items():
        if ex_id in model.reactions:
            model.reactions.get_by_id(ex_id).lower_bound = -uptake
    if carbon_source in model.reactions:
        model.reactions.get_by_id(carbon_source).lower_bound = -carbon_uptake
    return model

# The with-block reverts all bound changes on exit, so comparisons never leak state.
for cs in ['EX_glc__D_e', 'EX_ac_e', 'EX_succ_e']:
    with model:
        set_minimal_medium(model, carbon_source=cs)
        print(f'{cs}: growth = {model.slim_optimize():.4f}')   # slim_optimize returns the objective float only (fast)
```

## Flux Variability Analysis (FVA): expose alternate optima

```python
from cobra.flux_analysis import flux_variability_analysis

# Range each reaction can carry while holding the objective at (fraction_of_optimum) of the max.
fva = flux_variability_analysis(model, fraction_of_optimum=1.0)

# fraction_of_optimum < 1 relaxes the objective and reveals the alternative-optima span.
fva90 = flux_variability_analysis(model, fraction_of_optimum=0.9)

# loopless=True removes thermodynamically infeasible internal loops from the ranges (slower).
fva_ll = flux_variability_analysis(model, loopless=True)

# A reaction with maximum == minimum is fully determined; a wide range means the single
# FBA value for it was arbitrary. Blocked reactions have min == max == 0.
fva['range'] = fva['maximum'] - fva['minimum']
fva['blocked'] = fva['range'].abs() < 1e-9
```

## Parsimonious FBA (pFBA): one realistic representative

```python
from cobra.flux_analysis import pfba

# Among all optima, pFBA returns the flux vector minimizing the sum of absolute fluxes,
# an Occam's-razor proxy for minimal total enzyme cost (Lewis 2010). It is a principled
# single representative of the optimal face; it is NOT more "true" than the face itself,
# and it hugs the polytope boundary (a min-flux vertex), so report the FVA range alongside it
# when the internal flux values matter.
pfba_solution = pfba(model)
print(f'FBA total flux : {model.optimize().fluxes.abs().sum():.1f}')
print(f'pFBA total flux: {pfba_solution.fluxes.abs().sum():.1f}')
```

## Loopless FBA

```python
from cobra.flux_analysis import loopless_solution

# Projects an FBA solution onto a loopless one: no net flux around a closed cycle that
# lacks a thermodynamic driving force (Schellenberger 2011). Internal cycles are a common
# artifact of reversible reactions and gap-filling and inflate apparent flux magnitudes.
loopless = loopless_solution(model)
```

## Flux Sampling: the distribution, without choosing an objective

**Goal:** Characterize the whole space of feasible steady-state fluxes rather than one optimum, giving each reaction a distribution and confidence interval.

**Approach:** Uniformly sample the (optionally objective-constrained) solution polytope with a Markov-chain sampler (OptGP or ACHR). Use when there is no clear objective, when the objective face is large, or when uncertainty on internal fluxes matters more than an optimum.

```python
from cobra.sampling import sample

# n samples; method 'optgp' (parallel) or 'achr'. Thinning reduces autocorrelation.
samples = sample(model, n=1000, method='optgp', thinning=100, seed=1)
print(samples['PFK'].describe())   # per-reaction distribution, e.g. median and IQR

# To sample only high-growth states, constrain the objective first (e.g. biomass >= 0.9*max)
# inside a `with model:` block, then sample. Check mixing before trusting the distribution
# (multiple chains/seeds should agree); short chains give correlated, misleading samples.
```

## Production Envelope (growth vs product tradeoff)

```python
from cobra.flux_analysis import production_envelope

# Pareto frontier of growth against a secreted product; the design space for strain engineering.
# objective defaults to the model's objective (the biomass reaction) when omitted.
env = production_envelope(model, reactions=['EX_ac_e'])
# To actually DESIGN knockouts that couple product to growth, see systems-biology/strain-design.
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Growth is 0 / status 'infeasible' | medium closed, or an essential exchange left at lb=0, or a biomass precursor unproducible | check `model.medium`; open the minimal exchange set; confirm biomass precursors have a route |
| Suspiciously high growth on "minimal" media | an exchange left open to uptake (rich carbon, or all exchanges default-open) | close all exchange lower bounds to 0, then open only the intended set; audit `model.medium` |
| A reaction's flux changes every run / disagrees between tools | alternate optima - the value was one arbitrary vertex | report the FVA range or a pFBA/sampling value, not a single `optimize()` flux |
| Implausibly large internal fluxes | thermodynamically infeasible internal cycle | use `loopless_solution` or FVA `loopless=True` |
| Model predicts no acetate overflow at high glucose | plain FBA has no proteome/enzyme budget | use an enzyme-constrained model (GECKO/sMOMENT); FBA cannot see overflow |
| `phenotype_phase_plane(...)` raises TypeError | it is now a module, not a callable, in modern COBRApy | use `production_envelope` instead |
| Solver returns tiny nonzero "fluxes" that should be 0 | GLPK feasibility tolerance / degeneracy | switch to HiGHS or CPLEX/Gurobi; threshold fluxes at ~1e-6 |

## Related Skills

- systems-biology/gene-essentiality - Knockout screens, MOMA/ROOM for non-re-optimized mutants
- systems-biology/context-specific-models - Constrain FBA with expression data
- systems-biology/strain-design - Design knockouts from the production envelope
- systems-biology/community-metabolic-modeling - FBA over multi-species communities
- metabolomics/isotope-tracing - 13C-MFA to measure (not predict) intracellular fluxes
- metabolomics/pathway-mapping - Map measured metabolites onto model reactions

## References

- Orth JD, Thiele I, Palsson BO. 2010. What is flux balance analysis? *Nat Biotechnol* 28(3):245-248.
- Ebrahim A, Lerman JA, Palsson BO, Hyduke DR. 2013. COBRApy: constraint-based reconstruction and analysis for Python. *BMC Syst Biol* 7:74.
- Mahadevan R, Schilling CH. 2003. The effects of alternate optimal solutions in constraint-based genome-scale metabolic models. *Metab Eng* 5(4):264-276.
- Lewis NE, Hixson KK, Conrad TM, et al. 2010. Omic data from evolved E. coli are consistent with computed optimal growth from genome-scale models. *Mol Syst Biol* 6:390. (pFBA)
- Schellenberger J, Lewis NE, Palsson BO. 2011. Elimination of thermodynamically infeasible loops in steady-state metabolic models. *Biophys J* 100(3):544-553. (loopless)
- Megchelenbrink W, Huynen M, Marchiori E. 2014. optGpSampler: an improved tool for uniformly sampling the solution-space of genome-scale metabolic networks. *PLoS One* 9(2):e86587.
- Schuetz R, Kuepfer L, Sauer U. 2007. Systematic evaluation of objective functions for predicting intracellular fluxes in E. coli. *Mol Syst Biol* 3:119. (objective choice)
- Ibarra RU, Edwards JS, Palsson BO. 2002. Escherichia coli K-12 undergoes adaptive evolution to achieve in silico predicted optimal growth. *Nature* 420(6912):186-189.
- King ZA, Lu JS, Drager A, et al. 2016. BiGG Models: a platform for integrating, standardizing and sharing genome-scale models. *Nucleic Acids Res* 44(D1):D515-D522.
<!-- END FILE: systems-biology/flux-balance-analysis/SKILL.md -->

## 子目录：systems-biology/gene-essentiality

<!-- BEGIN FILE: systems-biology/gene-essentiality/SKILL.md -->
---
name: bio-systems-biology-gene-essentiality
description: Performs in-silico single and double gene deletions, condition-dependent essentiality, and synthetic-lethality screens on genome-scale metabolic models with COBRApy, evaluating gene-protein-reaction rules and comparing FBA re-optimization against MOMA/ROOM minimal-adjustment. Use when predicting essential genes, finding synthetic-lethal pairs for drug targets, choosing a growth cutoff, deciding FBA vs MOMA vs ROOM for a knockout, making essentiality medium-specific to match an experiment, or validating predictions against Keio/Tn-seq/CRISPR screens with MCC.
tool_type: python
primary_tool: cobrapy
---

## Version Compatibility

Reference examples tested with: COBRApy 0.29+, Python 3.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `single_gene_deletion` / `double_gene_deletion` spawn worker processes, so call them inside `if __name__ == '__main__':` (or pass `processes=1`) or a spawn platform will recurse. `delete_model_genes` is deprecated since 0.25; use `knock_out_model_genes` / `remove_genes`.

# Gene Essentiality Analysis

**"Which genes are essential for growth in my organism?"** -> Delete each gene (via its GPR rule), re-solve the model, and call a gene essential when its knockout drops predicted growth below a chosen cutoff - always relative to a specific model and medium.
- Python: `cobra.flux_analysis.single_gene_deletion()`, `double_gene_deletion()`, `moma()`, `room()` (COBRApy)

## The governing principle: essentiality is a model-and-medium prediction, not a gene property

An in-silico knockout answers "can THIS network still make biomass on THIS medium after this perturbation?" Everything else follows from taking that literally:

- A gene knockout is NOT a reaction knockout. Genes map to reactions through the gene-protein-reaction (GPR) rule: AND = protein complex (all subunits needed), OR = isozymes (any one suffices). A gene in an OR with a viable partner does nothing when deleted - isozyme masking is the dominant source of false non-essential calls and the reason synthetic lethals exist. Always delete GENES and let the GPR decide which reactions close; deleting reactions directly is a different, usually wrong, analysis.
- The essential/non-essential CUTOFF is a policy choice, not a library default. COBRApy returns raw knockout growth rates; there is no `growth_cutoff` argument. The cutoff (commonly <1-10% of wild type) moves the essential set in the "sick but alive" tail. It should be reported and swept (1/2/5/10%); genes whose call flips are low-confidence hypotheses.
- Essentiality is medium-dependent. Rich vs minimal media give different essential sets (a gene for a biosynthetic pathway is essential on minimal medium but dispensable when the product is supplied). To compare to an experiment, set the SAME medium the experiment used (LB vs M9), or the comparison is meaningless.
- Predictions have a ceiling (~85-93% accuracy on E. coli metabolic genes). False essentials come from a missing bypass/isozyme in the model; false non-essentials come from biology FBA cannot see (regulation, toxicity, essential non-metabolic or structural roles). Report MCC, not accuracy - essential genes are the minority class, so accuracy is inflated by the true-negative pile.

## Decision: which knockout method, which order

| Goal | Method | Assumption / when |
|------|--------|-------------------|
| Essential genes, evolved/adapted strain, or only hard lethality | FBA `single_gene_deletion` | mutant re-optimizes to max growth; cheapest; lethality calls agree with MOMA anyway |
| Immediate/fresh transposon or CRISPR mutant (one growth cycle) | MOMA `moma` | mutant stays closest in flux space to wild type (QP); fits fresh-mutant fluxes better |
| Fresh mutant where response is a few regulatory on/off switches | ROOM `room` | minimizes the NUMBER of significantly changed fluxes (MILP); recovers short bypasses |
| Synthetic-lethal PAIRS | `double_gene_deletion` on viable singles | both single KOs viable, double lethal; O(n^2), restrict the gene list |
| Higher-order lethal sets (triples/quads) | Fast-SL (flux-support pruning) | brute-force O(n^3+) infeasible; Fast-SL prunes by flux support |
| Condition/medium contrast | per-medium `single_gene_deletion` in `with model:` | essentiality re-computed under each defined medium |

MOMA/ROOM classify lethality similarly to FBA; they differ mainly on the quantitative growth of sick-but-alive mutants. Match the method to the timescale of the actual experiment.

## Single-Gene Deletion Screen

**Goal:** Rank every gene by the growth defect of its knockout and flag essential and growth-reducing genes.

**Approach:** Take wild-type growth once, then `single_gene_deletion` clamps each gene's reactions to zero through the GPR, re-optimizes, and returns a DataFrame with columns `ids` (a set holding the deleted gene id(s)), `growth`, and `status`. The caller applies the cutoff.

```python
import cobra
from cobra.flux_analysis import single_gene_deletion

model = cobra.io.load_model('textbook')
wt_growth = model.slim_optimize()

results = single_gene_deletion(model)          # DataFrame: ids (set of gene ids), growth, status
results['gene'] = results['ids'].apply(lambda s: list(s)[0])   # ids elements are gene-id STRINGS
results['relative'] = results['growth'] / wt_growth

ESSENTIAL_CUTOFF = 0.01                          # KO grows < 1% of WT -> essential (policy, not a default)
essential = results[results['relative'] < ESSENTIAL_CUTOFF]
print(f'Essential genes: {len(essential)} / {len(model.genes)} on this medium')
```

## Classify with a threshold sweep (report low-confidence calls)

```python
def classify_essentiality(results, wt_growth, cutoffs=(0.01, 0.02, 0.05, 0.10)):
    '''Classify genes and report how many calls flip across cutoffs (the sick-tail sensitivity).'''
    rel = results['growth'] / wt_growth
    calls = {c: set(results.loc[rel < c, 'gene']) for c in cutoffs}
    core = set.intersection(*calls.values())     # essential at every cutoff -> high confidence
    boundary = set.union(*calls.values()) - core # call depends on the cutoff -> low confidence
    return core, boundary
```

## MOMA / ROOM: the immediate, non-re-optimized mutant

```python
from cobra.flux_analysis import moma, room

# FBA assumes the mutant re-optimizes; a fresh knockout has not re-wired its regulation yet.
# MOMA keeps mutant flux closest (Euclidean) to wild type; ROOM minimizes the count of changed
# fluxes. Both need a wild-type reference solution and a QP/MILP-capable solver.
from cobra.util.solver import linear_reaction_coefficients
biomass = list(linear_reaction_coefficients(model))[0]   # the objective (biomass) reaction
wt = model.optimize()
with model:
    model.genes.get_by_id('b2276').knock_out()   # context-aware; reverts on block exit
    moma_sol = moma(model, solution=wt, linear=True)      # linear=True = fast LP approximation (lMOMA)
    # moma_sol.objective_value is the MINIMIZED ADJUSTMENT, not growth; read the biomass flux.
    print('MOMA mutant growth:', moma_sol.fluxes[biomass.id])
```

## Synthetic Lethality (double deletions + epistasis)

**Goal:** Find gene PAIRS that are viable singly but lethal together - redundant pathways and isozymes, and candidate combination drug targets.

**Approach:** Restrict to genes whose single knockout is viable (a synthetic lethal requires both singles viable), run pairwise `double_gene_deletion`, and keep pairs whose double-KO growth falls below the cutoff. Cost is O(n^2), so subset the gene list. Score interactions against the multiplicative neutral expectation (independent effects on an exponential growth rate).

```python
from cobra.flux_analysis import double_gene_deletion

viable = list(results.loc[results['relative'] > ESSENTIAL_CUTOFF, 'gene'])[:60]   # cap the O(n^2) sweep
dbl = double_gene_deletion(model, gene_list1=viable, gene_list2=viable)
dbl['n'] = dbl['ids'].apply(len)
sl_pairs = dbl[(dbl['n'] == 2) & (dbl['growth'] / wt_growth < ESSENTIAL_CUTOFF)]
print(f'Synthetic-lethal pairs: {len(sl_pairs)}')
# Genome-scale and higher-order (triple/quad) sets: use Fast-SL flux-support pruning (Pratapa 2015),
# not brute force.
```

## Condition-Specific Essentiality (match the experiment's medium)

**Goal:** Compare essential-gene sets across defined media to separate core-essential genes from condition-specific ones.

**Approach:** Apply each medium inside a `with model:` block (so it reverts), run the deletion screen, and take intersections/differences of the essential sets. Define media with real functions, not lambdas (a lambda cannot contain an assignment).

```python
def aerobic(m):
    m.reactions.EX_o2_e.lower_bound = -20

def anaerobic(m):
    m.reactions.EX_o2_e.lower_bound = 0

def essential_set(model, setup):
    with model:
        setup(model)
        wt = model.slim_optimize()
        res = single_gene_deletion(model)
        return set(res.loc[res['growth'] / wt < ESSENTIAL_CUTOFF, 'ids'].apply(lambda s: list(s)[0]))

sets = {name: essential_set(model, fn) for name, fn in [('aerobic', aerobic), ('anaerobic', anaerobic)]}
core = set.intersection(*sets.values())
condition_specific = {k: v - core for k, v in sets.items()}
```

## Validate against experiment (MCC, matched medium)

```python
# Compare predicted essentials to an experimental set (Keio single-KO, Tn-seq, or CRISPR fitness),
# on the SAME medium. Use MCC, not accuracy: essential genes are a minority class, so accuracy is
# inflated by the large true-negative pile.
from sklearn.metrics import matthews_corrcoef

def score(predicted_essential, experimental_essential, all_genes):
    y_pred = [g in predicted_essential for g in all_genes]
    y_true = [g in experimental_essential for g in all_genes]
    return matthews_corrcoef(y_true, y_pred)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Central gene predicted non-essential | it has an isozyme (OR in the GPR) that stays open | expected; that gene is a synthetic-lethal candidate, not truly dispensable |
| Deleting a reaction gives different results than deleting its gene | reaction KO ignores GPR; a gene may map to several reactions or share them | delete GENES (`single_gene_deletion` / `gene.knock_out()`), not reactions |
| `TypeError: 'set' object ... .id` | `ids` column holds sets of gene-id STRINGS, not gene objects | `list(s)[0]` gives the id string directly; no `.id` |
| Essential set disagrees with the paper | medium mismatch (LB vs M9) or a different cutoff | set the experiment's medium; report and sweep the cutoff |
| Script recurses / spawns endlessly | deletion functions parallelize; no `__main__` guard | wrap in `if __name__ == '__main__':` or pass `processes=1` |
| `AttributeError: delete_model_genes` | deprecated since cobra 0.25 | use `knock_out_model_genes` / `remove_genes`, or `gene.knock_out()` |
| High accuracy but poor agreement on real essentials | accuracy inflated by true negatives (minority class) | report MCC and sensitivity, not accuracy |

## Related Skills

- systems-biology/flux-balance-analysis - The FBA/medium/objective foundation these knockouts rest on
- systems-biology/model-curation - Missing isozymes/bypasses cause false essentials; curate before trusting calls
- systems-biology/strain-design - Growth-coupling designs build on knockout logic
- crispr-screens/hit-calling - Experimental essentiality screens to validate predictions
- pathway-analysis/go-enrichment - Functional enrichment of predicted essential-gene sets

## References

- Orth JD, Thiele I, Palsson BO. 2010. What is flux balance analysis? *Nat Biotechnol* 28(3):245-248.
- Segre D, Vitkup D, Church GM. 2002. Analysis of optimality in natural and perturbed metabolic networks. *PNAS* 99(23):15112-15117. (MOMA)
- Shlomi T, Berkman O, Ruppin E. 2005. Regulatory on/off minimization of metabolic flux changes after genetic perturbations. *PNAS* 102(21):7695-7700. (ROOM)
- Segre D, DeLuna A, Church GM, Kishony R. 2005. Modular epistasis in yeast metabolism. *Nat Genet* 37(1):77-83. (epistasis scoring, multiplicative expectation)
- Pratapa A, Balachandran S, Raman K. 2015. Fast-SL: an efficient algorithm to identify synthetic lethal sets in metabolic networks. *Bioinformatics* 31(20):3299-3305.
- Baba T, Ara T, Hasegawa M, et al. 2006. Construction of Escherichia coli K-12 in-frame, single-gene knockout mutants: the Keio collection. *Mol Syst Biol* 2:2006.0008.
- Monk JM, Lloyd CJ, Brunk E, et al. 2017. iML1515, a knowledgebase that computes Escherichia coli traits. *Nat Biotechnol* 35(10):904-908.
<!-- END FILE: systems-biology/gene-essentiality/SKILL.md -->

## 子目录：systems-biology/metabolic-reconstruction

<!-- BEGIN FILE: systems-biology/metabolic-reconstruction/SKILL.md -->
---
name: bio-systems-biology-metabolic-reconstruction
description: Builds draft genome-scale metabolic models from an annotated genome using CarveMe (top-down carving of a BiGG universal model) or gapseq (bottom-up pathway-evidence reconstruction), then loads and sanity-checks the draft in COBRApy. Use when creating a model for an organism without one, choosing between CarveMe and gapseq, gap-filling to a target medium, understanding why a draft that grows is still only a hypothesis, handling BiGG-vs-ModelSEED namespace mismatch, or preparing a draft for curation and community modeling.
tool_type: cli
primary_tool: CarveMe
---

## Version Compatibility

Reference examples tested with: CarveMe 1.6+, gapseq 1.2+, COBRApy 0.29+, DIAMOND 2.1+, Python 3.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: CarveMe needs an LP solver (academic CPLEX/Gurobi; SCIP is a slow open-source fallback) and a DIAMOND install, and its universal model is BiGG-derived so the BiGG-model release matters. gapseq is cloned from GitHub (not pip-installable), emits ModelSEED-namespace models, and its reference DB version matters. Model predictions are only comparable within the same tool, DB, and namespace.

# Metabolic Reconstruction

**"Build a metabolic model from my organism's genome"** -> Map the annotated proteome/genome to reactions in a reference database, assemble a draft network with a biomass reaction, and gap-fill so it can grow on a chosen medium.
- CLI: `carve genome.faa -o model.xml` (CarveMe, top-down); `gapseq doall genome.fna` (gapseq, bottom-up)

## The governing principle: a draft is a hypothesis, and "it grows" is guaranteed by construction

Automated reconstruction produces a DRAFT, not a finished model. The single most misleading signal is growth: CarveMe and gapseq GAP-FILL specifically to force biomass production on a chosen medium, so a draft that grows proves nothing biological - it was made to grow. Consequences:

- Gap-filled reactions are the least-evidenced part of the model (added to close a hole, not because homology supports them), and the gap-fill medium determines what gets added. Gap-filling on the wrong medium bakes in the wrong reactions. Flag gap-filled reactions as low-confidence and record the medium.
- Draft quality is bounded by the annotation and the reference database. CarveMe can only ever include reactions in the BiGG universe (biased toward well-studied organisms); gapseq's homology thresholds and pathway logic set its floor. Peripheral/novel metabolism is systematically underrepresented.
- The draft is the START of curation, not the end. Different tools produce markedly different models from the same genome, and successive models of the same organism (iJR904 -> iJO1366 -> iML1515) give different predictions. Reconstruction feeds model-curation, never bypasses it.

## Decision: CarveMe vs gapseq vs ModelSEED

| Goal | Tool | Why / trade-off |
|------|------|-----------------|
| Fast draft(s) for well-studied bacteria; batch/community | CarveMe (`carve`) | top-down MILP carving of a curated BiGG universe; minutes; universe is simulation-ready but BiGG-centric; universal biomass; weak transporters |
| Non-model/environmental clade; carbon-source & fermentation phenotypes | gapseq | bottom-up homology + pathway-completeness; slower, more transparent; better SCFA/carbon-use recovery; ModelSEED namespace complicates merging |
| Fully-automated web pipeline (RAST annotation) | ModelSEED/KBase | template-based; convenient; template biomass and aggressive gap-fill can force implausible reactions |
| Eukaryotes / fungi / actinomycetes | RAVEN (MATLAB) | KEGG/MetaCyc-based, template or de novo; MATLAB license; the eukaryote-capable option |

Do NOT treat "CarveMe and gapseq do the same thing, pick the faster one" as true: different philosophies, namespaces (BiGG vs ModelSEED), and failure modes. The choice is scientific. No single tool dominates - which is why consensus/ensemble reconstruction exists.

## CarveMe (top-down)

```bash
pip install carveme          # also needs DIAMOND and an LP solver (CPLEX/Gurobi; SCIP fallback)

# Draft from a PROTEIN FASTA (default input). Raw/GenBank genomes are NOT accepted.
carve genome.faa -o model.xml

# Gram type and universe are VALUES of -u/--universe, NOT --grampos/--gramneg flags.
carve genome.faa -o model.xml -u grampos    # {bacteria (default), grampos, gramneg, archaea, cyanobacteria}

# Gap-fill to force growth on a medium (opt-in; records what was added for that medium).
carve genome.faa -o model.xml --gapfill M9
carve genome.faa -o model.xml -u gramneg --gapfill M9,LB   # multiple media

# Nucleotide input instead of protein, or download by accession:
carve genome.fna --dna -o model.xml
```

Community reconstruction uses a SEPARATE `merge_community` command (not `carve`); see systems-biology/community-metabolic-modeling.

## gapseq (bottom-up, pathway-evidence)

```bash
git clone https://github.com/jotech/gapseq && cd gapseq && ./gapseq test   # cloned, not pip; check deps

# One-shot: find + find-transport + draft + fill
./gapseq doall genome.fna

# Or the explicit steps (note find-transport is its OWN subcommand, not `find -t`):
./gapseq find -p all genome.fna          # -> genome-all-Reactions.tbl, genome-all-Pathways.tbl
./gapseq find-transport genome.fna       # -> genome-Transporter.tbl  (singular)
./gapseq draft -r genome-all-Reactions.tbl -t genome-Transporter.tbl \
               -p genome-all-Pathways.tbl -c genome.fna   # -> genome-draft.RDS, genome-rxnWeights.RDS
./gapseq fill -m genome-draft.RDS -n dat/media/M9.csv \
              -c genome-rxnWeights.RDS -g genome-rxnXgenes.RDS   # -> genome.xml / genome.RDS
```

## Load and Sanity-Check the Draft

**Goal:** Read the draft, confirm it grows on the gap-fill medium, and inventory the parts most likely to be wrong.

**Approach:** Load the SBML into COBRApy, report network size and gene coverage, test growth, and count orphan (gene-less) reactions and exchanges - the draft's soft spots before curation.

```python
import cobra

model = cobra.io.read_sbml_model('model.xml')
print(f'reactions={len(model.reactions)} metabolites={len(model.metabolites)} genes={len(model.genes)}')
print(f'grows on gap-fill medium: {model.slim_optimize() > 1e-3}')   # true by construction if gap-filled
orphans = [r for r in model.reactions if not r.genes]   # no GPR: gap-filled, spontaneous, or transport
print(f'orphan (gene-less) reactions: {len(orphans)}  exchanges: {len(model.exchanges)}')
# Typical bacterial draft: ~1000-2500 reactions. Far outside that range flags an annotation problem.
```

## Namespaces (the silent killer of model comparison)

```python
# Reaction/metabolite IDs come from the tool's reference DB: CarveMe = BiGG, gapseq/ModelSEED =
# ModelSEED (seed.*), RAVEN = KEGG/MetaCyc. Two models in different namespaces cannot be merged or
# compared directly. Reconcile through MetaNetX/MNXref (MNXM* metabolites, MNXR* reactions) BEFORE
# any cross-tool merge or community build. This BiGG-vs-ModelSEED split is exactly why community
# modeling of CarveMe + gapseq outputs breaks without reconciliation.
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `carve` errors on a genome file | GenBank/nucleotide passed where protein FASTA expected | supply a protein FASTA, or add `--dna` for nucleotide |
| `--grampos`/`--gramneg` not recognized | those are `-u/--universe` VALUES, not flags | `carve ... -u grampos` |
| Draft cannot grow at all | no gap-filling requested, or wrong medium | add `--gapfill <medium>`; confirm the medium supplies biomass precursors |
| Draft grows on everything / implausibly | gap-fill forced reactions for the chosen medium | flag gap-filled reactions low-confidence; re-gap-fill on the correct medium; curate |
| Two models will not merge / IDs mismatch | different namespaces (BiGG vs ModelSEED) | reconcile via MetaNetX/MNXref before merging |
| gapseq `find -t` fails | transport is the `find-transport` subcommand | use `./gapseq find-transport genome.fna` |
| Very few genes / tiny network | poor annotation or wrong input file | check the proteome/annotation; verify gene IDs |

## Related Skills

- systems-biology/model-curation - Curate, gap-fill deliberately, and validate the draft (the required next step)
- systems-biology/flux-balance-analysis - Predict growth/flux once the model is trustworthy
- systems-biology/community-metabolic-modeling - Combine reconstructions into a community model
- genome-annotation/prokaryotic-annotation - Produce the annotated protein FASTA CarveMe/gapseq consume
- database-access/ncbi-datasets-cli - Fetch genome/proteome inputs

## References

- Machado D, Andrejev S, Tramontano M, Patil KR. 2018. Fast automated reconstruction of genome-scale metabolic models for microbial species and communities. *Nucleic Acids Res* 46(15):7542-7553. (CarveMe)
- Zimmermann J, Kaleta C, Waschina S. 2021. gapseq: informed prediction of bacterial metabolic pathways and reconstruction of accurate metabolic models. *Genome Biol* 22(1):81.
- Henry CS, DeJongh M, Best AA, et al. 2010. High-throughput generation, optimization and analysis of genome-scale metabolic models. *Nat Biotechnol* 28(9):977-982. (ModelSEED)
- Wang H, Marcisauskas S, Sanchez BJ, et al. 2018. RAVEN 2.0: a versatile toolbox for metabolic network reconstruction. *PLoS Comput Biol* 14(10):e1006541.
- Thiele I, Palsson BO. 2010. A protocol for generating a high-quality genome-scale metabolic reconstruction. *Nat Protoc* 5(1):93-121.
- Mendoza SN, Olivier BG, Molenaar D, Teusink B. 2019. A systematic assessment of current genome-scale metabolic reconstruction tools. *Genome Biol* 20(1):158.
- Moretti S, Tran VDT, Mehl F, et al. 2021. MetaNetX/MNXref: unified namespace for metabolites and biochemical reactions. *Nucleic Acids Res* 49(D1):D570-D574.
- Feist AM, Palsson BO. 2010. The biomass objective function. *Curr Opin Microbiol* 13(3):344-349.
- Monk JM, Lloyd CJ, Brunk E, et al. 2017. iML1515, a knowledgebase that computes Escherichia coli traits. *Nat Biotechnol* 35(10):904-908.
<!-- END FILE: systems-biology/metabolic-reconstruction/SKILL.md -->

## 子目录：systems-biology/model-curation

<!-- BEGIN FILE: systems-biology/model-curation/SKILL.md -->
---
name: bio-systems-biology-model-curation
description: Validates, gap-fills, and standardizes genome-scale metabolic models using memote for consistency and annotation scoring and COBRApy for manual curation, including mass/charge balance, energy-generating-cycle detection, dead-end resolution, GPR fixes, and SBML/SBO/MIRIAM annotation. Use when improving a draft model, gap-filling to a target medium, detecting erroneous ATP-from-nothing cycles, interpreting a memote score correctly (consistency vs biological validity), validating predictions against measured growth/essentiality, or preparing a model for publication.
tool_type: python
primary_tool: memote
---

## Version Compatibility

Reference examples tested with: memote 0.17+, COBRApy 0.29+, Python 3.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: a memote SCORE is comparable only within a memote version (the test suite evolves). The Python entry points are `memote.suite.api.test_model` / `snapshot_report` (not `run`/`snapshot`), and `cobra.flux_analysis.gapfill` has no `demand` argument (it gap-fills toward the model's objective).

# Model Curation

**"Validate and improve the quality of my metabolic model"** -> Score the model for consistency and annotation with memote, then use COBRApy to fix mass/charge imbalances, remove energy-generating cycles, gap-fill deliberately, and validate predictions against data.
- CLI: `memote report snapshot model.xml --filename report.html`
- Python: `cobra.flux_analysis.gapfill()`, mass/charge balance and energy-cycle checks (COBRApy)

## The governing principle: memote scores consistency, not biological correctness

The most common misconception in the field is that a high memote score means a good model. memote's scored total is a weighted sum of stoichiometric consistency, mass/charge balance, annotation coverage (KEGG/ChEBI/BiGG), SBO-term presence, and SBML/FBC conformance. All of that is HYGIENE - it measures whether the model is well-formed and well-annotated, NOT whether it predicts biology. A model can score 90% and mispredict every knockout and every growth phenotype. Optimizing the score for its own sake is Goodhart's law made concrete.

Curation therefore has two separable axes, and both must be reported:

1. Syntactic/consistency (what memote measures): mass and charge balance, no stoichiometric leaks, annotation, SBO terms, no blocked reactions, and - the one predictive-adjacent test - no erroneous energy-generating cycles.
2. Predictive validity (what memote does NOT measure): does the model reproduce measured growth rates, carbon-source usage (Biolog), and gene essentiality on the matched medium? This is the step that separates a curated model from a merely tidy one, and it lives outside memote.

The single most dangerous defect a high score can hide is an energy-generating cycle: a set of reactions that produces ATP/NADH from nothing. It arises from reversible reactions and blind gap-filling, passes mass balance, inflates growth, and invalidates every flux prediction. Test for it explicitly.

## Decision: which curation action for which symptom

| Symptom | Action | Tool |
|---------|--------|------|
| Model cannot grow on the target medium | gap-fill toward the objective, from a universal DB | `cobra.flux_analysis.gapfill` |
| Growth is implausibly high / ATP from nothing | detect and break energy-generating cycles | max-ATP-with-no-uptake test; constrain directionality |
| Reactions unbalanced | fix mass/charge (usually protons at pH 7) | per-reaction element/charge sum |
| Metabolite never produced or never consumed | resolve dead-end (add reaction or fix stoichiometry) | connectivity scan |
| Low annotation / SBO score | add MIRIAM annotations and SBO terms | memote report + manual/annotation tools |
| Predictions wrong despite high score | validate against measured growth/essentiality | separate experimental comparison (not memote) |

## memote: score consistency, then read the report, not just the number

```bash
pip install memote

memote run model.xml                                              # run the test suite (pytest-based)
memote report snapshot model.xml --filename report.html          # human-readable HTML report
```

```python
# Programmatic entry points (verify against the installed memote version):
from memote.suite.api import test_model, snapshot_report

code, result = test_model(model, results=True)   # result is a MemoteResult (the raw test outcomes)
html = snapshot_report(result, html=True)         # render the same report programmatically
# Read WHICH tests fail (consistency, energy cycles, unbalanced reactions) -- the total % is not
# a measure of biological correctness.
```

## Detect Energy-Generating Cycles (the defect a high score hides)

**Goal:** Prove the model cannot manufacture any energy currency (ATP, NADH, NADPH, FADH2, ...) from nothing.

**Approach:** Close every exchange so no nutrients enter and zero the ATP-maintenance lower bound (its NGAM floor would otherwise make a closed model infeasible for the wrong reason). Then, for EACH energy currency, add a moiety-conserving dissipation reaction (charged -> discharged) and maximize it. A result of 0 (or infeasible) per currency is correct; any positive finite flux is an erroneous energy-generating cycle to trace and fix by constraining reaction directionality. EGCs are not ATP-only, so the sweep must cover every currency present (Fritzemeier 2017); proton-motive-force cycles are subtler and are handled by memote's dedicated EGC test.

```python
# Dissipation stoichiometry per currency (BiGG ids); genome-scale models also test GTP/CTP/UTP/q8h2.
DISSIPATION = {'atp': {'atp_c': -1, 'h2o_c': -1, 'adp_c': 1, 'pi_c': 1, 'h_c': 1},
               'nadh': {'nadh_c': -1, 'nad_c': 1, 'h_c': 1},
               'nadph': {'nadph_c': -1, 'nadp_c': 1, 'h_c': 1}}

def energy_generating_cycles(model, dissipations=DISSIPATION):
    '''Max free-charging flux per currency with ALL uptake closed; >0 => energy-generating cycle.'''
    out = {}
    with model:
        for ex in model.exchanges:
            ex.lower_bound = 0                                   # no nutrients at all
        if 'ATPM' in model.reactions:
            model.reactions.get_by_id('ATPM').lower_bound = 0    # remove the NGAM floor before testing
        for name, stoich in dissipations.items():
            if any(m not in model.metabolites for m in stoich):
                continue                                         # currency absent from this model
            with model:
                r = cobra.Reaction(f'EGC_{name}')
                r.add_metabolites({model.metabolites.get_by_id(m): c for m, c in stoich.items()})
                r.bounds = (0, 1000)
                model.add_reactions([r])
                model.objective = r
                out[name] = model.slim_optimize()   # 0/infeasible = OK; positive finite = cycle
    return out
```

## Gap-Fill Toward the Objective (deliberately, on a stated medium)

**Goal:** Add the fewest reactions from a universal database that let the model grow on a defined medium.

**Approach:** Set the medium and the biomass objective, then call `gapfill` (which minimizes added reactions to reach the objective at `lower_bound`). There is no `demand` argument; `demand_reactions=False` avoids adding demand reactions for every metabolite. Record and low-confidence-flag every added reaction.

```python
from cobra.flux_analysis import gapfill

universal = cobra.io.read_sbml_model('universal_model.xml')   # e.g. a BiGG universal model
solutions = gapfill(model, universal, lower_bound=0.05, demand_reactions=False, iterations=3)
for i, rxns in enumerate(solutions):
    print(f'solution {i+1}: {[r.id for r in rxns]}')          # alternative gap-fill sets
# Adding these forces growth; that is not evidence they are biologically present. Flag them.
```

## Mass and Charge Balance

```python
def imbalance(reaction):
    '''Return the element and charge imbalance of a reaction (empty dict + 0 charge if balanced).'''
    mass = {}
    charge = 0
    for met, coef in reaction.metabolites.items():
        if met.formula:
            for element, n in met.elements.items():
                mass[element] = mass.get(element, 0) + coef * n
        if met.charge is not None:
            charge += coef * met.charge
    return {e: v for e, v in mass.items() if abs(v) > 1e-6}, charge

# This is a PER-REACTION element/charge check. It is distinct from stoichiometric CONSISTENCY --
# a whole-network LP (Gevorgyan 2008, what memote tests) that finds mass leaks without needing
# formulas. "All reactions mass-balanced" does not imply the network is stoichiometrically consistent.
# Exchange/demand/sink AND the biomass pseudo-reaction are intentionally imbalanced; skip them.
# Proton (H) imbalance at pH 7 is the most common real fix.
from cobra.util.solver import linear_reaction_coefficients
pseudo = set(model.boundary) | set(linear_reaction_coefficients(model))   # boundary + objective (biomass)
unbalanced = [(r.id, imbalance(r)) for r in model.reactions
              if r not in pseudo and (imbalance(r)[0] or abs(imbalance(r)[1]) > 1e-6)]
```

## Dead-End Metabolites

```python
def dead_ends(model):
    '''Metabolites that can only be produced or only consumed (a network gap or wrong stoichiometry).'''
    out = []
    for met in model.metabolites:
        produced = any(r.metabolites[met] > 0 for r in met.reactions)
        consumed = any(r.metabolites[met] < 0 for r in met.reactions)
        if not (produced and consumed):
            out.append(met.id)
    return out
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "High memote score, so the model is good" | score measures consistency/annotation, not prediction | validate against measured growth/essentiality separately |
| Growth is huge; ATP looks free | erroneous energy-generating cycle | run the max-ATP-with-no-uptake test; constrain the offending reactions' directionality |
| `gapfill(... demand=...)` TypeError | there is no `demand` argument | set the objective and use `lower_bound=`/`demand_reactions=False` |
| `memote.suite.api.run`/`snapshot` AttributeError | wrong names | use `test_model` / `snapshot_report` |
| Many reactions flagged unbalanced | protons/charge at pH 7, or exchange reactions counted | skip exchange/sink/demand; fix H and charge first |
| Model still mispredicts after high score | consistency fixed, biology not validated | compare to Biolog carbon sources and an essentiality screen on the matched medium |

## Related Skills

- systems-biology/metabolic-reconstruction - Produces the draft this skill curates
- systems-biology/flux-balance-analysis - Test the curated model's predictions
- systems-biology/gene-essentiality - Validate curation against measured essentiality
- pathway-analysis/kegg-pathways - Source KEGG annotations for reactions/metabolites
- database-access/uniprot-access - Cross-reference gene/protein annotations

## References

- Lieven C, Beber ME, Olivier BG, et al. 2020. MEMOTE for standardized genome-scale metabolic model testing. *Nat Biotechnol* 38(3):272-276.
- Fritzemeier CJ, Hartleb D, Szappanos B, Papp B, Lercher MJ. 2017. Erroneous energy-generating cycles in published genome-scale metabolic networks: identification and removal. *PLoS Comput Biol* 13(4):e1005494.
- Noor E, Haraldsdottir HS, Milo R, Fleming RMT. 2013. Consistent estimation of Gibbs energy using component contributions. *PLoS Comput Biol* 9(7):e1003098. (thermodynamic directionality)
- Thiele I, Palsson BO. 2010. A protocol for generating a high-quality genome-scale metabolic reconstruction. *Nat Protoc* 5(1):93-121.
- Orth JD, Palsson BO. 2010. Systematizing the generation of missing metabolic knowledge. *Biotechnol Bioeng* 107(3):403-412. (gap analysis)
- Ebrahim A, Lerman JA, Palsson BO, Hyduke DR. 2013. COBRApy: constraint-based reconstruction and analysis for Python. *BMC Syst Biol* 7:74.
<!-- END FILE: systems-biology/model-curation/SKILL.md -->

## 子目录：systems-biology/strain-design

<!-- BEGIN FILE: systems-biology/strain-design/SKILL.md -->
---
name: bio-systems-biology-strain-design
description: Computes metabolic-engineering strain designs on genome-scale models with StrainDesign (OptKnock, RobustKnock, minimal cut sets, OptCouple) and cameo (heuristic knockout and FSEOF over/under-expression targets), finding gene/reaction interventions that couple product formation to growth. Use when designing knockouts to overproduce a target chemical, choosing between OptKnock and RobustKnock, growth-coupling a product so evolution maintains it, computing minimal cut sets, finding amplification targets with FSEOF, or understanding why MILP strain design needs a strong solver and why a design is only a hypothesis.
tool_type: python
primary_tool: straindesign
---

## Version Compatibility

Reference examples tested with: StrainDesign 1.15+, COBRApy 0.29+, Python 3.10+ (cameo optional)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: OptKnock/RobustKnock/MCS are MILP problems and are far harder than plain FBA; StrainDesign supports GLPK/SCIP (open source) and CPLEX/Gurobi (academic, much faster and more robust for genome-scale). Set a `time_limit`. Reaction-based designs must be translated back to gene knockouts via GPRs.

# Strain Design

**"Design knockouts to make my organism overproduce a chemical"** -> Search for a set of gene/reaction interventions that couples product formation to growth, so the engineered strain cannot grow well without secreting the target.
- Python: `straindesign.compute_strain_designs(model, sd_modules=[SDModule(model, OPTKNOCK, ...)])`; cameo for heuristics/FSEOF

## The governing principle: growth-coupling makes evolution enforce the design

The core idea of computational strain design is growth-coupling. A naive "just delete the competing pathways" design is fragile: the cell will find an alternate flux route, or evolution in the bioreactor will erode production because making product costs the cell resources. A growth-COUPLED design instead makes product secretion obligatory for growth - the cell physically cannot reach high growth without also secreting the target, so selection maintains production instead of eroding it. This is why OptKnock is a BILEVEL optimization: the inner problem is the cell maximizing its own growth, the outer problem is the engineer maximizing product AT that inner optimum. Consequences:

- OptKnock is optimistic: it assumes the cell, among its growth-optimal states, picks the one best for the engineer. The cell need not. RobustKnock fixes this by maximizing product in the WORST-case inner optimum - a more conservative, more trustworthy design.
- A design is a HYPOTHESIS about a model, not a strain. FBA has no regulation, no enzyme kinetics, no toxicity, no genetic stability; a computationally growth-coupled design can fail in construction or in the bioreactor. Validate with the production envelope, then in the lab.
- MILP strain design is combinatorially hard. Bound the intervention set (`max_cost`), cap solutions, set a time limit, and use a strong solver (CPLEX/Gurobi for genome-scale). Reaction knockouts must be mapped back to gene deletions through the GPR to be realizable.

## Decision: which strain-design method

| Goal | Method | Trade-off |
|------|--------|-----------|
| Growth-coupled knockouts, optimistic | OptKnock (Burgard 2003) | bilevel; assumes the cell cooperates at its growth optimum |
| Growth-coupled knockouts, conservative | RobustKnock (Tepper & Shlomi 2010) | guarantees product in the worst-case inner optimum; harder |
| Guaranteed intervention sets, enumerate all minimal | Minimal Cut Sets (von Kamp & Klamt 2014) | strong guarantees; enumerates smallest intervention sets |
| Strong growth-coupling (obligatory) | OptCouple | maximizes the growth-coupling potential directly |
| Over/under-EXPRESSION targets, not just knockouts | FSEOF (Choi 2010) / cameo | scans fluxes that rise with enforced product; amplification targets |
| Heuristic/evolutionary search when MILP is intractable | OptGene / cameo | fast approximate designs; no optimality guarantee |

Prefer RobustKnock or MCS over plain OptKnock when the design must be trustworthy; OptKnock's optimism is a well-known way to overstate a design.

## Growth-Coupled Knockouts with StrainDesign (OptKnock)

**Goal:** Find a small set of reaction knockouts that couples secretion of a target product to growth.

**Approach:** Build an OptKnock `SDModule` with the cell's growth as the inner objective and product secretion as the outer objective, plus a minimum-growth constraint so the design keeps the strain viable, then call `compute_strain_designs` with an intervention budget and solver. Translate the returned reaction knockouts back to gene deletions via the GPR.

```python
import cobra
import straindesign as sd

model = cobra.io.load_model('textbook')
biomass = 'Biomass_Ecoli_core'   # the model's actual biomass reaction id (verify per model)

optknock = sd.SDModule(
    model, sd.OPTKNOCK,
    inner_objective=biomass,            # the cell maximizes growth
    outer_objective='EX_ac_e',          # the engineer maximizes acetate secretion
    constraints=[f'{biomass} >= 0.3'],  # keep the strain viable
)

solutions = sd.compute_strain_designs(
    model, sd_modules=[optknock],
    max_cost=3,          # at most 3 interventions
    max_solutions=3,
    solver='glpk',       # use 'cplex'/'gurobi' for genome-scale models
    time_limit=120,
)
# solutions.reaction_sd is a list of intervention dicts {reaction_id: marker}; a knockout is
# marked -1.0 (not 0). Verify this marker for the installed StrainDesign version -- a wrong marker
# silently yields empty designs. For a knockout-only OptKnock module every entry is a knockout.
for design in solutions.reaction_sd:
    print('knockouts:', [rid for rid, mark in design.items() if mark == -1.0])
```

## Verify Growth-Coupling with the Production Envelope

```python
from cobra.flux_analysis import production_envelope

# A genuinely growth-coupled design shows a NONZERO minimum product flux across the growth range:
# the strain cannot grow without secreting product. Apply the design's knockouts, then:
env = production_envelope(model, reactions=['EX_ac_e'])   # objective defaults to biomass
# Inspect the lower bound of product at each growth level; if it can be zero at max growth, the
# coupling is weak (the OptKnock-optimism problem) -- consider RobustKnock. See flux-balance-analysis.
```

## Over-Expression Targets (FSEOF, cameo)

```python
# Knockouts are not the only lever. FSEOF (flux scanning with enforced objective flux) finds
# reactions whose flux RISES as product formation is enforced -- candidate amplification/over-
# expression targets. cameo implements FSEOF and heuristic (evolutionary) design search:
#   from cameo.strain_design import OptGene           # heuristic knockout search
#   from cameo.strain_design.deterministic import FSEOF
# Use FSEOF/over-expression when the bottleneck is low flux through an existing pathway rather than
# a competing drain that a knockout would remove.
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `compute_strain_designs` never finishes | MILP is hard and GLPK is slow on genome-scale | set `time_limit`, lower `max_cost`, use CPLEX/Gurobi |
| Design gives zero product when built | OptKnock optimism: the cell chose a different growth-optimal state | use RobustKnock, or check the production envelope's lower bound |
| Constraint parser rejects the biomass id | wrong reaction id string for this model | look up the actual objective reaction id (`linear_reaction_coefficients`) |
| Design not realizable in the lab | reaction knockouts have no clean gene mapping, or hit an essential gene | translate reaction KOs to gene KOs via GPR; exclude essential genes |
| Predicted overproduction never materializes | FBA has no regulation/kinetics/toxicity/stability | treat the design as a hypothesis; validate the envelope, then in vivo |
| No feasible design found | growth constraint too tight or product infeasible on the medium | relax the minimum-growth constraint; confirm the product can be made on the medium |

## Related Skills

- systems-biology/flux-balance-analysis - Production envelope and the FBA/medium foundation
- systems-biology/gene-essentiality - Avoid designing knockouts of essential genes; GPR mapping
- systems-biology/model-curation - A curated model is a prerequisite for a trustworthy design
- systems-biology/context-specific-models - Constrain the chassis to a condition before designing
- metabolomics/pathway-mapping - Interpret the affected pathways of a design

## References

- Burgard AP, Pharkya P, Maranas CD. 2003. OptKnock: a bilevel programming framework for identifying gene knockout strategies for microbial strain optimization. *Biotechnol Bioeng* 84(6):647-657.
- Schneider P, Bekiaris PS, von Kamp A, Klamt S. 2022. StrainDesign: a comprehensive Python package for computational design of metabolic networks. *Bioinformatics* 38(21):4981-4983.
- Tepper N, Shlomi T. 2010. Predicting metabolic engineering knockout strategies for chemical production: accounting for competing pathways. *Bioinformatics* 26(4):536-543. (RobustKnock)
- von Kamp A, Klamt S. 2014. Enumeration of smallest intervention strategies in genome-scale metabolic networks. *PLoS Comput Biol* 10(1):e1003378. (minimal cut sets)
- Choi HS, Lee SY, Kim TY, Woo HM. 2010. In silico identification of gene amplification targets for improvement of lycopene production. *Appl Environ Microbiol* 76(10):3097-3105. (FSEOF)
- Cardoso JGR, Jensen K, Lieven C, et al. 2018. Cameo: a Python library for computer-aided metabolic engineering and optimization of cell factories. *ACS Synth Biol* 7(4):1163-1166.
<!-- END FILE: systems-biology/strain-design/SKILL.md -->

<!-- END CATEGORY: systems-biology -->

