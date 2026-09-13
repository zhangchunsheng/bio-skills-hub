---
slug: bio-chemoinformatics-integrated
version: 1.0.1
displayName: "化学信息学 / Chemoinformatics"
name: bio-chemoinformatics-integrated
summary: "中文：化学信息学综合技能，整合 20 个相关专题，覆盖化学信息学：RDKit分子描述符、相似性搜索、pharmacophore、对接、ADMET、生成式设计、QSAR。 English: Integrated Chemoinformatics skill covering 20 related topics, including Chemoinformatics: RDKit molecular descriptors, similarity/shape search, pharmacophore modeling, docking, ADMET, generative design, QSAR."
description: "中文：这是一个面向化学信息学的综合生物信息学 Skill，整合当前分类下 20 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：化学信息学：RDKit分子描述符、相似性搜索、pharmacophore、对接、ADMET、生成式设计、QSAR。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ADMETlab, AiZynthFinder, AutoDock Vina。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Chemoinformatics, combining 20 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Chemoinformatics: RDKit molecular descriptors, similarity/shape search, pharmacophore modeling, docking, ADMET, generative design, QSAR. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ADMETlab, AiZynthFinder, AutoDock Vina. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# chemoinformatics 分类 Skill 整合版

> 本文件整合同一主分类目录下 20 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: chemoinformatics -->

## 子目录：chemoinformatics/admet-prediction

<!-- BEGIN FILE: chemoinformatics/admet-prediction/SKILL.md -->
---
name: bio-admet-prediction
description: Predicts ADMET properties using ADMETlab 3.0 (119 platform features, including 77 prediction models with modeled-endpoint uncertainty), ADMET-AI, DeepChem MolNet, and chemprop D-MPNN with explicit handling of OECD QSAR principles, applicability domain assessment, calibration, hERG/CYP/AMES endpoints, and PAINS / Lipinski / Ro5 / Veber / BBB druglikeness filters. Use when filtering compounds for drug-likeness, prioritizing leads by predicted safety, or building an in-house ADMET QSAR model.
tool_type: python
primary_tool: ADMETlab
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, requests 2.31+, DeepChem 2.8+, chemprop 2.0+ (note major API change from 1.x), admet-ai 1.3+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ADMET Prediction

Predict absorption, distribution, metabolism, excretion, and toxicity properties of drug candidates. ADMET prediction underpins lead selection and de-risking; calibrated, applicability-domain-aware predictions distinguish a working filter from a costly false-confidence rejection. Modern best practice combines online services (ADMETlab 3.0 with uncertainty estimates), open-source models (chemprop D-MPNN), and rule-based filters (Lipinski / Veber / BBB heuristics) -- each with known failure modes.

For PAINS / Brenk / structural alerts, see `chemoinformatics/substructure-search`. For QSAR model building from in-house data, see `chemoinformatics/qsar-modeling`.

## ADMET Model Taxonomy

| Tool | Endpoints | Architecture | Uncertainty | Access | Fails when |
|------|-----------|--------------|-------------|--------|------------|
| ADMETlab 3.0 | 119 reported features: 77 prediction models, 34 computed properties, 8 rules | Multi-task DMPNN + descriptors for modeled endpoints | Evidential uncertainty for modeled endpoints | Web service; hosted API documented by the authors | Outside training distribution; metals; macrocycles |
| ADMET-AI | TDC-derived ADMET tasks; inspect installed model metadata | Chemprop D-MPNN | Inspect version-specific outputs; do not assume calibrated uncertainty | Python package | v2 package predictions differ from the v1 paper/server |
| DeepChem MolNet | Dataset-dependent tasks including Tox21, ToxCast, and ClinTox | Model-dependent | Model-dependent | Python package | Coverage and uncertainty depend on the selected dataset/model |
| pkCSM | Service-defined ADMET endpoints | Graph signatures + ML | Inspect current service output | Web service | Applicability domain and service contract must be checked |
| SwissADME | Physchem, pharmacokinetics, drug-likeness, and medchem outputs | Published models and rules | None advertised | Web service (no public API) | Automated access is restricted by its terms |
| ProTox-3.0 | 61 toxicity models/endpoints | RF/DNN + fingerprints, similarity, and pharmacophore methods | Confidence score | Web service / sample API | Toxicity only; reports LD50 and toxicity class |
| ADMETpredictor (Simulations Plus) | ~140 | Proprietary | Per-prediction | Commercial | License cost |
| FAF-Drugs4 | filters | Rule-based | None | Web | Static rules |
| chemprop (in-house) | User-defined | D-MPNN ± descriptors | Ensemble and other estimators; optional calibration | Python package | Requires suitable training and calibration data |

**Decision:** For batch screening with no in-house data, **ADMETlab 3.0** provides 119 reported platform features and uncertainty for modeled endpoints through its web service and hosted API; verify the live API documentation before automating access. For a sufficiently large, relevant in-house endpoint dataset, benchmark a **chemprop D-MPNN**, descriptors, and simpler baselines under a deployment-relevant split rather than assuming a universal sample-size threshold. Shan et al. (2022) reported an AUC of 0.956 for a D-MPNN combined with 206 MOE descriptors on their random-split hERG benchmark.

## Decision Tree by Scenario

| Scenario | Workflow | Reasoning |
|----------|----------|-----------|
| Library triage, no in-house data | ADMETlab 3.0 API batch | Broad platform coverage plus modeled-endpoint uncertainty |
| Single endpoint, adequate in-house data | Benchmark chemprop D-MPNN, descriptors, and simpler baselines | Select by prospective or deployment-relevant validation |
| Need calibrated probabilities | chemprop with ensemble + Platt | Native deep learning rarely calibrated |
| FDA / regulatory submission | OECD-compliant QSAR with AD | See OECD principles below |
| Quick annotation for VS | Lipinski, Veber, and QED reported separately | Rank or annotate; do not impose a universal QED gate |
| BBB penetration | Simple screen: TPSA <= 90, MW <= 500, HBD <= 3 | Repository heuristic; not the six-factor CNS MPO |
| Cardiotox liability | ADMETlab hERG + ProTox-3.0 cardiotoxicity + literature check | Both hosted endpoints model hERG blockade; compare applicability domains and assay definitions |
| Drug-drug interaction (CYP) | CYP1A2/2C9/2C19/2D6/3A4 inhibitor + substrate | Standard set of 5 CYPs |

## OECD QSAR Principles (5 Pillars)

For regulatory-grade ADMET QSAR (REACH, ECHA, FDA submissions), models must satisfy:

1. **Defined endpoint** -- specific bioassay, units, conditions
2. **Unambiguous algorithm** -- reproducible model + code
3. **Defined applicability domain (AD)** -- where the model is valid
4. **Appropriate statistical validation** -- external test set, cross-validation
5. **Mechanistic interpretation** -- biological / chemical rationale

For non-regulatory work, AD assessment is still critical. The OECD's *applicability domain* is the workhorse: predictions outside the AD are unreliable, but operational AD measures (leverage, kNN, conformal prediction) often disagree.

## Applicability Domain Methods

| Method | Definition | Flags out-of-AD when |
|--------|-----------|----------------------|
| kNN distance | Mean distance to k nearest neighbors in training set | > training-set distribution P95 |
| Leverage (Williams) | Hat-matrix diagonal | > 3p/n (p = features, n = compounds) |
| Density (KDE on PCA) | Density in feature space | < density of training set P5 |
| Conformal prediction | Per-prediction confidence interval | Interval > tolerance |
| Bayesian variance | Ensemble or MC-dropout variance | > training-set variance P95 |

For deep-learning ADMET, **conformal prediction** can provide calibrated prediction sets or intervals when its exchangeability and calibration assumptions are appropriate (McShane et al. 2024).

## ADMETlab 3.0 API

ADMETlab 3.0 reports 119 platform features: 77 prediction models, 34 computed physicochemical properties, and 8 medicinal-chemistry rules. The modeled endpoints include prediction uncertainty; do not imply that computed properties and rules have model uncertainty.

**Goal:** Obtain the platform's 119 features for a batch of SMILES, including uncertainty for the 77 modeled endpoints, using the hosted service.

**Approach:** Follow the live ADMETlab 3.0 API tutorial to wash molecules, submit batch predictions, and retrieve the returned results. The 2024 paper documents API/batch support and modeled-endpoint uncertainty. Obtain current rate limits, routes, payloads, task identifiers, and output contracts from the live official documentation rather than attributing them to the paper or hard-coding an unofficial example.

```python
import pandas as pd

# After submitting with the current official API example, load its CSV output.
results = pd.read_csv('admetlab3_results.csv')
# Preserve the uncertainty columns and task identifier in downstream reports.
```

ADMETlab 3.0 endpoints (sample):
- Absorption: Caco-2 permeability (logPapp), HIA (%), Pgp inhibitor/substrate, MDCK
- Distribution: BBB+, PPB (%), VDss (L/kg), Fu (fraction unbound)
- Metabolism: CYP1A2/2C9/2C19/2D6/3A4 inhibitor / substrate
- Excretion: CL (mL/min/kg), T1/2 (h)
- Toxicity: hERG, AMES, hepatotoxicity (DILI), carcinogenicity, immunotoxicity, mutagenicity, respiratory, skin, eye, cardiotoxicity, mitochondrial, NR-AR, NR-ER, SR-MMP
- Drug-likeness: Lipinski, Veber, Ghose, Egan, Muegge, QED, SAscore

## chemprop D-MPNN for Custom Endpoints

When in-house data is available, train a target-specific model. chemprop provides a widely used open-source D-MPNN architecture with atom/bond features and optional molecular descriptors; benchmark it against appropriate baselines on the project's data.

**Goal:** Train a target-specific ADMET classifier or regressor on in-house bioassay data.

**Approach:** Use the installed Chemprop 2.x CLI with a scaffold split, a release-supported descriptor featurizer, replicated models, and an explicit prediction-time uncertainty/calibration workflow.

```python
# Chemprop 2.2 CLI; verify flags against the installed release.
# chemprop train --data-path data.csv --task-type classification \
#                --save-dir model_dir --split-type scaffold_balanced \
#                --molecule-featurizers v1_rdkit_2d_normalized \
#                --num-replicates 5 --ensemble-size 5
# chemprop predict --test-path test.csv --model-paths model_dir \
#                  --uncertainty-method ensemble --preds-path predictions.csv

# Or chemprop 2.x programmatic API (full programmatic API documented at chemprop.readthedocs.io)
# See chemoinformatics/qsar-modeling for the full chemprop 2.x training pipeline.
```

**Key:** Replicates and an ensemble estimator produce an uncertainty estimate, not automatic calibration. Fit and evaluate a documented calibrator on a separate calibration set when calibrated probabilities or intervals are required. Descriptor benefit must be demonstrated on the intended endpoint.

## hERG Cardiotoxicity Endpoint

hERG (KCNH2) blockade can contribute to QT prolongation and Torsades de Pointes and is an important non-clinical cardiac-safety endpoint. Follow the current ICH S7B/E14 and regulator-specific guidance applicable to the program rather than treating one model output as a regulatory conclusion.

| Model | Architecture | Training data | AUC | Reference |
|-------|--------------|---------------|-----|-----------|
| Shan et al. D-MPNN + MOE | D-MPNN + 206 MOE descriptors | 7,889 compounds | 0.956 (random split) | Shan 2022 |
| CardioTox-net | Five DL base representations + neural meta-ensemble | BindingDB, ChEMBL, and literature | 0.930 (10-fold meta-validation) | Karim 2021 |
| ADMETlab 3.0 hERG | DMPNN multi-task | Internal | 0.92 (reported) | Fu 2024 |
| ProTox-3.0 cardiotoxicity | RF-based classifier | 5,252 ChEMBL compounds with hERG IC50/Ki | 0.86 CV; 0.95 external | Banerjee 2024 |

**Interpretation:** A single-model probability > 0.5 is NOT a kill signal. Triangulate multiple hERG-specific models and a literature search. ProTox-3.0 calls the endpoint cardiotoxicity, but its model specifically predicts small-molecule hERG blockers; it should not be treated as an independent non-hERG mechanism. Consider exposure relative to measured hERG potency and confirm important decisions experimentally rather than applying a universal safe/unsafe IC50 cutoff.

## CYP Inhibition (DDI Risk)

5 CYP isoforms cover most clinically relevant DDIs:

| CYP | Substrates (drugs) | Inhibitor flag if predicted prob | Action |
|-----|--------------------|-----------------------------------|--------|
| CYP3A4 | many drug classes | Model-specific threshold | Interpret inhibitor and substrate assays separately |
| CYP2D6 | beta-blockers, antidepressants | Model-specific threshold | Include polymorphism and exposure context |
| CYP2C9 | warfarin, NSAIDs | Model-specific threshold | Evaluate clinical substrate/exposure context |
| CYP2C19 | PPIs, clopidogrel | Model-specific threshold | Include polymorphism and assay context |
| CYP1A2 | caffeine, theophylline | Model-specific threshold | Include induction, diet, and smoking context |

## PAINS, BRENK, REOS Filters

ADMET prediction is separate from structural alerts; combine. See `chemoinformatics/substructure-search` for PAINS/BRENK/REOS pattern catalogs.

```python
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

def alerts(mol, catalogs=('PAINS_A', 'BRENK', 'ZINC')):
    params = FilterCatalogParams()
    for cat in catalogs:
        params.AddCatalog(getattr(FilterCatalogParams.FilterCatalogs, cat))
    catalog = FilterCatalog(params)
    hits = catalog.GetMatches(mol)
    return [h.GetDescription() for h in hits]
```

## Lipinski / Veber / Drug-Likeness

See `chemoinformatics/molecular-descriptors` for full physchem table. Quick filter:

```python
from rdkit.Chem import Descriptors, Lipinski, QED

def druglike_score(mol):
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rotbonds = Lipinski.NumRotatableBonds(mol)
    qed = QED.qed(mol)

    lipinski_violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
    veber_pass = rotbonds <= 10 and tpsa <= 140
    bbb_simple_screen = tpsa <= 90 and mw <= 500 and hbd <= 3

    return {'MW': mw, 'LogP': logp, 'HBD': hbd, 'HBA': hba,
            'TPSA': tpsa, 'RotBonds': rotbonds, 'QED': qed,
            'Lipinski_violations': lipinski_violations,
            'Veber_pass': veber_pass, 'BBB_simple_screen': bbb_simple_screen}
```

## Per-Tool Failure Modes

### ADMETlab 3.0 -- out-of-distribution prediction

**Trigger:** Chemistry materially unlike the service's documented training/applicability domain, such as metal-containing complexes, many peptides, PROTACs, or unusual macrocycles.

**Mechanism:** ADMETlab training set is drug-like organic molecules. Predictions on PROTACs, macrocycles, peptides extrapolate.

**Symptom:** High reported uncertainty, disagreement with neighbors or orthogonal models, or unstable conclusions under reasonable preprocessing.

**Fix:** Check uncertainty band; if interval is broad, do not trust point estimate. For PROTACs / macrocycles, prefer literature-derived experimental data.

### hERG D-MPNN -- training data bias

**Trigger:** Compound is novel chemotype not in training set (drug-like but in unexplored region).

**Mechanism:** D-MPNN learns local chemical features; for genuinely new scaffolds, extrapolation is unreliable.

**Symptom:** Model predicts hERG- (false negative) for compound that experimentally inhibits.

**Fix:** Use ensemble + applicability-domain assessment (kNN distance, ensemble variance). If kNN distance to training set > P95, treat prediction as low-confidence.

### CYP3A4 inhibitor + substrate ambiguity

**Trigger:** Model trained on either inhibitor OR substrate; predictions confused.

**Mechanism:** CYP3A4 inhibitors and substrates have similar SAR; many compounds are both.

**Symptom:** Both classes report > 0.5.

**Fix:** Two separate models (inhibitor model, substrate model); compounds that score high in both are flagged for in vitro confirmation.

### SwissADME -- no API

**Trigger:** Wanting to batch programmatically.

**Mechanism:** SwissADME's terms restrict automated crawler/data-retrieval access, and no public API is documented.

**Symptom:** No programmatic access; manual web upload only.

**Fix:** Use a currently documented programmatic service and follow its access policy; for ADMETlab 3.0, verify the live API tutorial before writing a client.

### PAINS as a kill filter

**Trigger:** Treating PAINS_A match as a categorical exclusion.

**Mechanism:** PAINS is calibrated against HTS assay-interference; matches do NOT predict failed drug development.

**Symptom:** Library purged of valid leads (curcumin analogs, polyphenol natural products).

**Fix:** Flag PAINS for orthogonal-assay confirmation; do not exclude pre-emptively. See substructure-search for details.

### Class-imbalanced AMES dataset

**Trigger:** Training/predicting AMES mutagenicity.

**Mechanism:** Public AMES datasets can be imbalanced and differ in assay definition and curation; aggregate accuracy can therefore be misleading.

**Symptom:** Model reports high accuracy but predicts negative for all.

**Fix:** Report class balance and use suitable metrics such as PR-AUC, ROC-AUC, MCC, or balanced accuracy. Compare class weighting or resampling inside training folds without leaking validation/test data.

## Reconciliation Across Models

When ADMETlab, ProTox-3.0, and an independently trained chemprop model disagree on hERG:
- All predict hERG+ -> higher concern; plan in vitro patch-clamp
- Results disagree -> inspect applicability domains, activity thresholds, and assay definitions before deciding
- All predict hERG- -> lower concern, but still consider in vitro screening for clinical candidates and novel chemotypes
- Do not count correlated models as independent evidence merely because they are hosted by different services

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| ADMETlab API timeout | Service load, payload, or current quota | Follow live batch limits; retry with backoff and record failures |
| chemprop training overfits | Random split | Use scaffold split (`--split scaffold_balanced`) |
| hERG prediction 50/50 | Out-of-distribution | Check applicability domain |
| QED calculation fails | Molecule is missing, unsanitized, or unsupported | Reject parse failures; sanitize inputs and handle calculation exceptions |
| ProTox endpoints missing | Web scrape uses CSS selector | Use formal API |
| BBB+ true but TPSA > 90 | Different BBB model | Use the simple physicochemical screen as an orthogonal heuristic |
| Predictions inconsistent across runs | Random seed for chemprop ensemble | `--seed 42` and reuse model |
| Calibration mismatch | DL native probabilities not calibrated | Apply Platt scaling on validation set |

## References

- Fu et al., *Nucleic Acids Res.* 52:W422-W431 (2024) -- ADMETlab 3.0 (DOI 10.1093/nar/gkae236).
- Shan M, Jiang C, Chen J, Qin L-P, Qin J-J, Cheng G. *RSC Adv.* 12:3423-3430 (2022) -- D-MPNN/MOE hERG benchmark (DOI 10.1039/D1RA07956E).
- Karim A, Lee M, Balle T, Sattar A. *J. Cheminformatics* 13:60 (2021) -- CardioTox-net (DOI 10.1186/s13321-021-00541-z).
- Banerjee P, Kemmler E, Dunkel M, Preissner R. *Nucleic Acids Res.* 52:W513-W520 (2024) -- ProTox-3.0 (DOI 10.1093/nar/gkae303).
- McShane SA et al. *J. Cheminformatics* 16:75 (2024) -- conformal prediction for molecular-property models (DOI 10.1186/s13321-024-00870-9).
- Heid E et al., *J. Chem. Inf. Model.* 64:9-17 (2024) -- Chemprop redesign (DOI 10.1021/acs.jcim.3c01250).
- Chemprop documentation, training, descriptors, and uncertainty: https://chemprop.readthedocs.io/
- ADMET-AI official repository and version notes: https://github.com/swansonk14/admet_ai
- SwissADME Terms of Use: https://www.swissadme.ch/termsofuse.php
- OECD, "Principles for the Validation, for Regulatory Purposes, of (Q)SAR Models" (agreed 2004).
- OECD, *Guidance Document on the Validation of (Q)SAR Models*, OECD Series on Testing and Assessment No. 69 (2007).
- OECD, "(Q)SAR Assessment Framework" (2023).
- Capuzzi et al., *J. Chem. Inf. Model.* 57:417 (2017) -- PAINS reality check.
- Wager et al., *ACS Chem. Neurosci.* 1:435 (2010) -- Pfizer CNS MPO.
- Bickerton et al., *Nat. Chem.* 4:90 (2012) -- QED.

## Related Skills

- chemoinformatics/molecular-descriptors - Compute drug-likeness physchem
- chemoinformatics/substructure-search - PAINS / BRENK / REOS filter
- chemoinformatics/qsar-modeling - Build custom QSAR for in-house data
- chemoinformatics/molecular-standardization - Canonicalize before prediction
- machine-learning/biomarker-discovery - Adjacent ML approaches
- clinical-databases/pharmacogenomics - Patient genotype overlay
<!-- END FILE: chemoinformatics/admet-prediction/SKILL.md -->

## 子目录：chemoinformatics/conformer-generation

<!-- BEGIN FILE: chemoinformatics/conformer-generation/SKILL.md -->
---
name: bio-conformer-generation
description: Generates 3D conformer ensembles using RDKit ETKDGv3 with knowledge-enhanced distance geometry, MMFF94/UFF force-field optimization, CREST + GFN2-xTB semi-empirical refinement, and macrocycle-aware torsion preferences. Provides explicit decision rules for single vs ensemble conformer use, RMSD pruning, energy windows, conformer count, and force-field choice. Use when preparing 3D ligands for docking, generating descriptor input for 3D QSAR, or sampling macrocycle/peptide conformational ensembles.
tool_type: mixed
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, xtb 6.7+, CREST 3.0+, OpenMM 8.1+ for follow-up MD.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `xtb --version`; `crest --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Conformer Generation

Generate 3D conformer ensembles for molecules from 2D structures. The choice of method depends on molecule size, flexibility, and downstream use: ETKDG (Riniker & Landrum 2015) and its ETKDGv3 macrocycle update (Wang et al. 2020) are modern defaults for drug-like molecules, MMFF94/UFF provide fast energy minimization, and CREST + GFN2-xTB provide higher-cost semi-empirical sampling. A single conformer may be insufficient when the downstream result is conformation-sensitive; determine ensemble size by convergence of the downstream descriptor, alignment, or docking result.

For docking pose validation, see `chemoinformatics/pose-validation`. For free-energy methods (which require ensemble sampling), see `chemoinformatics/free-energy-calculations`.

## Conformer Method Taxonomy

| Method | Cost / mol | Quality | Use case | Fails when |
|--------|-----------|---------|----------|------------|
| ETKDGv3 + MMFF94 | Benchmark on actual molecules/hardware | Useful for many drug-like organics | Initial docking/descriptors | Difficult macrocycles, peptides, unsupported chemistry |
| ETKDGv3 + UFF | Fast | Different parameter coverage from MMFF94 | Fallback only after checking UFF parameters | Unsupported atom types; coordination chemistry |
| Omega (OpenEye) | Benchmark licensed workflow | Commercial conformer generator | Commercial pipelines | License cost and configured limits |
| Confab (Open Babel) | Benchmark on intended chemistry | Systematic torsion search | Alternative enumeration | Combinatorial growth and force-field dependence |
| RDKit ETKDGv3 + macrocycle preferences | Molecule-dependent | Macrocycle-aware embedding | Macrocyclic starting ensembles | Coverage remains molecule-dependent |
| CREST + GFN2-xTB | Molecule/settings-dependent | Semiempirical conformational sampling | Difficult flexible molecules | Computational cost; special chemistry |
| CREST + GFN-FF | Lower cost than GFN2-xTB | Force-field-level sampling | Exploratory sampling | Validate coverage and ordering for the chemistry |
| GeoMol (Ganea 2021) | Hardware/model-dependent | Learned conformer generation | Large-library research workflow | Training distribution and released-model coverage |
| TorsionNet (Gogineni 2020) | Hardware/model-dependent | Learned torsional search | Research workflow | Training distribution and implementation availability |
| MD sampling (OpenMM) | System/protocol-dependent | Dynamic sampling | Free energy, induced fit | Computational cost and convergence |

**Decision:** Start drug-like organic molecules with **ETKDGv3** and a parameter-checked MMFF94/MMFF94s optimization. Escalate difficult macrocycles, peptides, or highly flexible molecules to a validated CREST workflow when downstream convergence is inadequate. Benchmark ML generators on the intended chemistry before using them at scale.

## Decision Tree by Scenario

| Scenario | Starting method | Sampling and filtering decision |
|----------|-----------------|---------------------------------|
| Single initial 3D structure | ETKDGv3 + checked force field | Confirm embedding and minimization; downstream relaxation may still be required |
| Multi-conformer docking | ETKDGv3 ensemble | Increase sampling until pose recovery or enrichment is stable |
| 3D descriptors / pharmacophores | ETKDGv3 ensemble | Converge the reported statistic; justify energy/RMSD filters |
| Macrocycle / peptide | Macrocycle-aware ETKDG, then CREST if needed | Compare coverage against known conformers or downstream convergence |
| FEP input | Bound-pose-informed preparation and MD | Do not select solely by isolated-molecule conformer energy |
| Shape search | Query- and library-specific ensemble | Converge retrieval performance on a reference set |

## ETKDGv3 (Modern Default)

ETKDGv3 (Wang et al. 2020), building on the original ETKDG method (Riniker & Landrum 2015), incorporates experimental torsion preferences and updated macrocycle handling into distance geometry.

**Goal:** Generate an ensemble of 3D conformers from a SMILES with the modern default embedding algorithm.

**Approach:** Add explicit hydrogens, configure ETKDGv3 parameters (random seed, maximum embedding iterations, random coordinates), and embed multiple conformers via `EmbedMultipleConfs`.

```python
from rdkit import Chem
from rdkit.Chem import AllChem

def gen_conformers(smiles, n_conf=20, seed=42):
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.useRandomCoords = True
    params.maxIterations = 1000
    ids = AllChem.EmbedMultipleConfs(mol, numConfs=n_conf, params=params)
    return mol, list(ids)
```

`useRandomCoords=True` can improve convergence for macrocycles and highly flexible molecules. On an `EmbedParameters` object the documented limit is `maxIterations`; `maxAttempts` is only present in legacy positional overloads.

## Force-Field Optimization

After embedding, minimize each conformer to a local minimum.

**Goal:** Reduce strain in each embedded conformer to a stable local minimum and record the resulting energies.

**Approach:** Build MMFF94s force-field parameters, minimize each conformer in place, and collect energies; fall back to UFF when MMFF94 cannot parameterize the molecule.

```python
def optimize_conformers(mol, conf_ids, force_field='mmff94'):
    results = []
    if force_field == 'mmff94':
        mmff_props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant='MMFF94s')
        if mmff_props is not None:
            for cid in conf_ids:
                ff = AllChem.MMFFGetMoleculeForceField(mol, mmff_props, confId=cid)
                if ff is None:
                    results.append({'conf_id': cid, 'status': 'force_field_failed'})
                    continue
                status = ff.Minimize(maxIts=1000)
                results.append({'conf_id': cid, 'energy': ff.CalcEnergy(),
                                'converged': status == 0, 'force_field': 'MMFF94s'})
            return results
        force_field = 'uff'
    if force_field == 'uff':
        if not AllChem.UFFHasAllMoleculeParams(mol):
            raise ValueError('Neither MMFF94s nor UFF covers this molecule')
        for cid in conf_ids:
            ff = AllChem.UFFGetMoleculeForceField(mol, confId=cid)
            if ff is None:
                results.append({'conf_id': cid, 'status': 'force_field_failed'})
                continue
            status = ff.Minimize(maxIts=1000)
            results.append({'conf_id': cid, 'energy': ff.CalcEnergy(),
                            'converged': status == 0, 'force_field': 'UFF'})
        return results
    raise ValueError(f'Unsupported force field: {force_field}')
```

**MMFF94 vs MMFF94s:** MMFF94s is the static-structure variant, with modified out-of-plane and torsional terms intended to preserve planarity in selected functional groups. It is useful for geometry optimization, but it is not a universally preferred replacement for MMFF94; record which variant was used and validate it for the downstream task.

**UFF (Universal Force Field):** UFF has different and often broader parameter coverage than MMFF94, but RDKit does not guarantee coverage for every molecule and generic UFF does not validate metal coordination chemistry. Call `UFFHasAllMoleculeParams` before use and use a chemistry-appropriate method for metal complexes.

## RMSD Pruning

Remove near-duplicate conformers within a chosen RMSD cutoff to keep the ensemble diverse:

```python
import numpy as np

def prune_conformers_rmsd(mol, conf_ids, rmsd_cutoff=0.5):
    n = len(conf_ids)
    keep = []
    for i, cid in enumerate(conf_ids):
        is_unique = True
        for kept_cid in keep:
            rmsd = AllChem.GetBestRMS(mol, mol, cid, kept_cid)
            if rmsd < rmsd_cutoff:
                is_unique = False
                break
        if is_unique:
            keep.append(cid)
    return keep
```

**Typical RMSD cutoff (Source / Rationale):**

| Cutoff | Use case | Source |
|--------|----------|--------|
| 0.5 Å | Drug-like ensemble for descriptors / docking | Repository clustering heuristic; validate for the downstream task |
| 1.0 Å | Drug-like ensemble for pharmacophore | Standard ROCS / pharmacophore practice |
| 1.5-2.0 Å | Macrocycles / peptides | Repository clustering heuristic for higher conformational freedom |
| 2.0+ Å | Cluster-centroid representative ensembles | Coarse representative sampling |

## Energy Window Filtering

Remove conformers above a project-justified energy cutoff only when the energy model and downstream purpose support that choice. Bound conformers can be strained relative to an isolated-molecule minimum.

```python
def filter_by_energy(mol, conf_ids, energies, window_kcal=10.0):
    min_e = min(energies)
    keep = []
    for cid, e in zip(conf_ids, energies):
        if e - min_e <= window_kcal:
            keep.append(cid)
    return keep
```

Treat any numerical energy window as a starting parameter. Calibrate it against conformer recovery or downstream metric convergence and record the energy method, solvent treatment, protonation state, and temperature assumptions.

## Macrocycle Handling

Macrocycles (>=12 atom rings) have distinct conformational issues: ETKDGv3 default knowledge base under-samples macrocycle torsions. Use macrocycle-specific torsion preferences:

```python
from rdkit.Chem import AllChem

def macrocycle_conformers(smiles, n_conf=200, seed=42):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f'Invalid SMILES: {smiles!r}')
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.useRandomCoords = True
    params.useMacrocycleTorsions = True
    params.useSmallRingTorsions = True
    params.maxIterations = 5000
    ids = list(AllChem.EmbedMultipleConfs(mol, numConfs=n_conf, params=params))
    if not ids:
        raise RuntimeError(f'No macrocycle conformers embedded for {smiles!r}')
    return mol, ids
```

For difficult macrocycles, CREST + GFN2-xTB is a useful higher-cost option; validate coverage against experimental or downstream evidence rather than treating one method as universally definitive.

## CREST + GFN2-xTB for High-Quality Sampling

CREST (Pracht et al. 2024) performs iterative meta-dynamics + GFN2-xTB optimization for conformer sampling.

**Goal:** Sample high-quality conformer ensembles for macrocycles, peptides, or molecules where ETKDGv3 + MMFF94 is inadequate.

**Approach:** Start from an RDKit-generated MMFF94-relaxed conformer, write to XYZ, and run CREST with GFN2-xTB driver to perform iterative meta-dynamics + reoptimization.

```bash
xtb mol.xyz --opt extreme
crest xtbopt.xyz --gfn2 --T 12 --ewin 6
```

**`--gfn2`**: use GFN2-xTB; validate its coverage and energy ordering for the chemistry of interest.
**`--gfn-ff`**: use GFN-FF; it can reduce computational cost, but benchmark its coverage and energy ordering for the intended molecules.
**`-ewin 6`**: 6 kcal/mol energy window above global min.
**`-T 12`**: use 12 CPU threads.

Output: `crest_conformers.xyz` with sampled ensemble.

**Workflow:** Start from RDKit ETKDGv3 + MMFF94 (cheap initial structure) -> save as XYZ -> CREST refinement.

```python
from rdkit import Chem
from rdkit.Chem import AllChem
import subprocess
from pathlib import Path

def crest_workflow(smiles, out_dir='crest_out'):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f'Invalid SMILES: {smiles!r}')
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.useRandomCoords = True
    if AllChem.EmbedMolecule(mol, params) == -1:
        raise RuntimeError(f'Initial 3D embedding failed for {smiles!r}')
    if not AllChem.MMFFHasAllMoleculeParams(mol):
        raise ValueError(f'MMFF parameters are unavailable for {smiles!r}')
    status = AllChem.MMFFOptimizeMolecule(
        mol, mmffVariant='MMFF94s', maxIters=1000
    )
    if status != 0:
        raise RuntimeError(f'Initial MMFF optimization did not converge (status {status})')

    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    input_path = out_dir / 'input.xyz'
    input_path.write_text(Chem.MolToXYZBlock(mol))
    # Because cwd is out_dir, pass the coordinate filename rather than out_dir/input.xyz.
    subprocess.run(['crest', input_path.name, '--gfn2', '-T', '12'],
                   cwd=out_dir, check=True)
    output_path = out_dir / 'crest_conformers.xyz'
    if not output_path.exists():
        raise FileNotFoundError(f'CREST did not produce {output_path}')
    return output_path
```

## Boltzmann Averaging of Properties

For ensemble descriptors (3D shape, dipole moment, polar surface area in 3D), Boltzmann-weight by energy:

```python
import numpy as np

def boltzmann_weights(energies, T=300.0):
    energies = np.array(energies)
    kt = 0.001987 * T  # kcal/mol at 300K
    rel = energies - energies.min()
    w = np.exp(-rel / kt)
    return w / w.sum()

def boltzmann_average(values, energies, T=300.0):
    w = boltzmann_weights(energies, T)
    return float(np.sum(np.array(values) * w))
```

Boltzmann populations require energies that approximate the relevant thermodynamic state, including conformer degeneracy and environmental effects where important. Raw gas-phase MMFF/UFF minima are exploratory surrogates, not generally validated populations.

## ML-Based Conformer Generation and Search

Research methods such as GeoMol generate molecular conformations directly, while TorsionNet uses reinforcement learning to search torsional conformational space. They are distinct approaches and should not be presented as interchangeable drop-in generators.

```python
# Pseudo-code for GeoMol-style ML conformer generation
# (Requires pre-trained model + dependencies)
# from geomol import generate_conformers
# conformers = generate_conformers(smiles, n_conformers=10)
```

**Trade-off:** Performance and coverage depend on the released model, training distribution, conformer definition, and benchmark. Verify the maintained implementation and benchmark it against ETKDGv3 or CREST on the intended chemistry before using it operationally; do not infer broad macrocycle or organometallic coverage from drug-like benchmarks.

## Per-Tool Failure Modes

### ETKDGv3 -- failed embedding

**Trigger:** Macrocycle, highly constrained polycyclic, or sterically crowded molecule.

**Mechanism:** Distance geometry cannot find a consistent 3D structure within the configured embedding iterations.

**Symptom:** `EmbedMolecule` returns -1; `EmbedMultipleConfs` returns empty list.

**Fix:** Set `useRandomCoords=True`, increase `maxIterations`; for macrocycles, set `useMacrocycleTorsions=True`. As fallback, use CREST.

### MMFF94 -- parameter missing

**Trigger:** Molecule contains element not parameterized (transition metals, certain S+ species).

**Mechanism:** MMFF94 only covers H, C, N, O, F, Si, P, S, Cl, Br, I + select cations.

**Symptom:** `MMFFGetMoleculeProperties` returns None; optimization silently no-ops.

**Fix:** Fall back to UFF; or for metals, use GFN2-xTB.

### Conformer ensemble too small

**Trigger:** `n_conf=10` for a flexible molecule (>5 rotatable bonds).

**Mechanism:** A fixed small ensemble can miss relevant minima for flexible molecules.

**Symptom:** New conformers continue to change cluster populations or the downstream result.

**Fix:** As a repository starting heuristic, use n_conf = max(10, 5 * NumRotatableBonds + 10), then increase sampling until the ensemble is stable for the downstream metric.

### Single-conformer 3D descriptor

**Trigger:** Calculating 3D descriptors from a single conformer.

**Mechanism:** Some 3D descriptors vary materially across conformers.

**Symptom:** Same molecule produces different 3D descriptors on rerun.

**Fix:** Converge the descriptor over an ensemble and report the chosen summary. Use Boltzmann weighting only with a justified population model.

### CREST -- timeout on flexible molecule

**Trigger:** Cyclosporin or large peptide.

**Mechanism:** CREST metadynamics scales poorly with rotational complexity.

**Symptom:** Hours of CPU time per molecule; incomplete sampling.

**Fix:** Use `--gfn-ff` for an exploratory lower-cost run or shorten metadynamics with the documented `--mdlen`/`--len` option. `--noopt` disables input pre-optimization; it does not skip metadynamics.

### GFN2-xTB conformer reordering

**Trigger:** Comparing conformer energies between GFN2-xTB and DFT.

**Mechanism:** GFN2-xTB is parameterized for energies; relative conformer ordering can differ from DFT by 1-2 kcal/mol.

**Symptom:** "Wrong" conformer reported as global minimum vs DFT reference.

**Fix:** For high-stakes work, re-rank top GFN2-xTB conformers with DFT single-points (e.g., r2SCAN-3c).

## Reconciliation: ETKDGv3 vs CREST

| Use case | ETKDGv3 | CREST |
|----------|---------|-------|
| Drug-like organic molecule | Efficient starting point | Higher-cost comparison when convergence fails |
| Highly flexible molecule | Increase and convergence-test sampling | Useful alternative sampling strategy |
| Macrocycle or peptide | Try macrocycle-aware settings and validate | Often useful, but not automatically sufficient |
| Population-weighted descriptors | Requires justified energy/population model | Higher-level energy still requires thermodynamic validation |
| FEP input | Useful for initial coordinates | Does not replace bound-pose and MD preparation |

For ETKDGv3 ensembles, compare a representative subset with an orthogonal method or experimental conformers and judge adequacy using the downstream metric; no single cross-method RMSD establishes completeness.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `EmbedMolecule` returns -1 | Embed failed | Set `useRandomCoords=True`; raise `params.maxIterations` |
| MMFFOptimize no-op | MMFF parameters missing | Use UFF fallback |
| All conformers identical | Stiff molecule | OK; molecule is rigid |
| Conformers physically wrong | Stereochemistry lost | Re-add explicit stereo before embedding |
| 3D descriptors differ per run | Random seed not set | `params.randomSeed = 42` |
| CREST out-of-memory | Search/ensemble too large | Reduce `--T`, shorten documented sampling, or lower `--ewin` to retain fewer structures |
| Macrocycle ring inverted | Default torsion preferences wrong | Set `useMacrocycleTorsions=True` |
| AddHs not called | Implicit H not embedded | `mol = Chem.AddHs(mol)` before EmbedMolecule |

## References

- Hawkins et al., *J. Chem. Inf. Model.* 50:572-584 (2010) -- OMEGA conformer sampling (DOI 10.1021/ci100031x).
- Riniker & Landrum, *J. Chem. Inf. Model.* 55:2562-2574 (2015) -- original ETKDG method (DOI 10.1021/acs.jcim.5b00654).
- Wang S, Witek J, Landrum GA, Riniker S. *J. Chem. Inf. Model.* 60:2044-2058 (2020) -- ETKDGv3 macrocycle update (DOI 10.1021/acs.jcim.0c00025).
- Halgren TA, *J. Comput. Chem.* 17:490-519 (1996) -- MMFF94 force field (DOI 10.1002/(SICI)1096-987X(199604)17:5/6%3C490::AID-JCC1%3E3.0.CO;2-P).
- Rappe AK et al., *J. Am. Chem. Soc.* 114:10024-10035 (1992) -- UFF (DOI 10.1021/ja00051a040).
- Pracht P et al., *J. Chem. Phys.* 160:114110 (2024) -- CREST 3.0 (DOI 10.1063/5.0197592).
- Bannwarth C, Ehlert S, Grimme S. *J. Chem. Theory Comput.* 15:1652-1671 (2019) -- GFN2-xTB (DOI 10.1021/acs.jctc.8b01176).
- RDKit force-field API: https://www.rdkit.org/docs/source/rdkit.Chem.rdForceFieldHelpers.html
- CREST command-line documentation: https://crest-lab.github.io/crest-docs/page/documentation/keywords.html
- xTB documentation: https://xtb-docs.readthedocs.io/
- Ganea et al., *NeurIPS* (2021) -- GeoMol ML conformer generation.
- Gogineni T et al., *NeurIPS* 33 (2020) -- TorsionNet learned conformational search.

## Related Skills

- chemoinformatics/molecular-io - Parse molecules
- chemoinformatics/molecular-standardization - Standardize before embedding
- chemoinformatics/molecular-descriptors - 3D descriptors from ensembles
- chemoinformatics/shape-similarity - Multi-conformer 3D shape matching
- chemoinformatics/virtual-screening - Generate 3D ligands for docking
- chemoinformatics/free-energy-calculations - Sample conformers for MD setup
- chemoinformatics/pharmacophore-modeling - 3D pharmacophore from ensembles
<!-- END FILE: chemoinformatics/conformer-generation/SKILL.md -->

## 子目录：chemoinformatics/covalent-design

<!-- BEGIN FILE: chemoinformatics/covalent-design/SKILL.md -->
---
name: bio-covalent-design
description: Designs covalent inhibitors and warheads targeting cysteine, lysine, serine, threonine, tyrosine, and aspartate residues, with explicit handling of warhead reactivity (acrylamide, chloroacetamide, vinyl sulfone, sulfonyl fluoride, fluorosulfate, aldehyde, boronate, nitrile), reversibility (kinact/Ki, t_residence), glutathione (GSH) stability, intrinsic reactivity assays, and covalent docking (DOCKovalent, GOLD, HCovDock). Use when designing covalent inhibitors for targeted covalent inhibition (TCI), KRAS G12C-style approaches, or rationalizing covalent SAR.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, OpenEye / AutoDock Vina 1.2+ (for covalent extensions), GOLD (commercial), DOCKovalent (web service), HCovDock 1.0+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show rdkit` then `help(rdkit.Chem)` to check signatures
- CLI: check version output of each docking tool

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Covalent Inhibitor Design

Design molecules that form covalent bonds with target protein residues. Clinically validated targeted covalent inhibitors include KRAS G12C inhibitors (sotorasib, adagrasib), BTK inhibitors (ibrutinib), and EGFR inhibitors (osimertinib). Covalent design requires balancing **intrinsic reactivity** (must form bond) vs **selectivity** (only the intended residue), **reversibility** (irreversible vs reversible covalent), and **drug-likeness** (warheads can hurt PK).

For warhead substructure filtering (in non-covalent contexts), see `chemoinformatics/substructure-search`. For non-covalent docking, see `chemoinformatics/virtual-screening`. For pose validation, see `chemoinformatics/pose-validation`.

## Reactive Residue Taxonomy

| Residue | Nucleophile | Example compatible warheads | Design note |
|---------|-------------|-----------------------------|-------------|
| Cysteine | Thiol / thiolate | Acrylamide, haloacetamide, nitrile | Commonly targeted; local pKa and geometry control reactivity |
| Lysine | Amine | Sulfonyl fluoride, aldehyde | Aldehydes can form reversible imines with amines |
| Serine | Alcohol / alkoxide | β-lactam, boronate | Often requires catalytic activation |
| Threonine | Alcohol / alkoxide | Boronate | Context-dependent and less commonly targeted |
| Tyrosine | Phenol / phenolate | Sulfonyl fluoride, fluorosulfate | Local environment strongly affects reaction |
| Aspartate/Glutamate | Carboxylate | Residue-specific electrophiles require experimental validation | Do not infer aldehyde Schiff-base formation with carboxylates |

Cysteine is frequently targeted because its thiol/thiolate can be nucleophilic and its local environment can support selective proximity-driven reaction. GSH and off-target cysteines are competing thiols, not intrinsically distinguishable from the target by the warhead alone; the complete ligand's recognition, exposure, and intrinsic reactivity determine selectivity.

## Warhead Chemistry

| Warhead | SMARTS pattern | Reactivity | Reversibility | Cys-selective |
|---------|----------------|------------|---------------|----------------|
| Acrylamide | `[CX3](=[OX1])([NX3])[CX3]=[CX3]` | Moderate (Michael acceptor) | Usually irreversible | Often Cys-directed |
| Chloroacetamide | `[CX3](=[OX1])([NX3])[CH2]Cl` | High (SN2) | Irreversible | Often Cys-directed |
| α-haloketone | `[CX3](=O)C[F,Cl,Br]` | Very high | Irreversible | Yes (but reactive) |
| Vinyl sulfone | `S(=O)(=O)C=C` | Moderate (Michael) | Irreversible | Yes |
| Sulfonyl fluoride | `S(=O)(=O)F` | Moderate | Irreversible | Lys/Tyr/Ser |
| Fluorosulfate (SuFEx) | `OS(=O)(=O)F` | Moderate | Irreversible | Tyr/Lys |
| Aldehyde | `[CX3H1](=O)` | Variable | Often reversible (covalent equilibrium) | Context-dependent Cys/Lys/Ser chemistry |
| Boronate (B-OH or B(OH)2) | `B(O)O` | Moderate | Reversible | Ser/Thr |
| Nitrile | `C#N` | Low | Reversible (Cys-S adduct) | Cys |
| Epoxide | `C1OC1` | High | Irreversible | Cys/Lys/Asp |
| α,β-unsaturated ketone | `[CX3](=O)C=C` | Moderate (Michael) | Irreversible | Cys |
| Isothiocyanate | `N=C=S` | High | Irreversible | Cys/Lys |
| Maleimide | `O=C1N(C(=O)C=C1)` | Often high | Commonly irreversible under assay conditions | Often Cys-directed |
| Cysteine-selective heterocycle | various | Moderate | Variable | Yes (designed) |

**Practical hierarchy:** Acrylamides are common attenuated electrophiles in cysteine-directed TCIs, including KRAS G12C, EGFR, and BTK programs. Haloacetamides are generally more intrinsically reactive, but actual selectivity must be measured for the complete molecule and target context.

## Decision Tree by Scenario

| Goal | Warhead choice | Reactivity tier |
|------|----------------|-----------------|
| Cysteine TCI program | Acrylamide is one common starting class | Measure complete-compound target and intrinsic reactivity |
| Cysteine probe program | Haloacetamides are one common class | Higher intrinsic reactivity can aid labeling but requires selectivity profiling |
| Lysine TCI (uncommon) | Sulfonyl fluoride | Moderate |
| Tyrosine TCI | Fluorosulfate (SuFEx) | Moderate |
| Reversible covalent | Warhead with demonstrated reversible adduct chemistry, such as selected cyanoacrylamides, aldehydes, nitriles, or boronates | Confirm reversibility experimentally |
| Activity-based protein profiling (ABPP) | Iodoacetamide / chloroacetamide | Very high |
| Boronic acid inhibitor (proteasome) | Boronate | Reversible |
| Aldehyde inhibitor (calpain) | Aldehyde | Reversible covalent |

## Kinetics: kinact / Ki

Covalent inhibition kinetics:
- **Ki**: reversible binding affinity (initial, like non-covalent IC50)
- **kinact**: rate of covalent bond formation (sec^-1)
- **kinact/Ki**: second-order rate constant, "covalent efficiency" (M^-1 s^-1)

For irreversible two-step inhibition that follows the corresponding kinetic model, report fitted `kinact`, `Ki`, and `kinact/Ki` rather than only a time-dependent IC50. Two compounds with the same IC50 can have different kinetic components:
- Low Ki, low kinact: tight binding, slow covalent bond
- High Ki, high kinact: loose binding, fast covalent bond

Because `kinact/Ki` depends on the target, construct, assay conditions, and kinetic model, compare values within a matched assay series and alongside exposure, intrinsic reactivity, target engagement, and selectivity. Reversible-covalent systems may require different mechanistic models and residence-time or washout measurements.

## Intrinsic Reactivity Assays

Before committing to a warhead, measure intrinsic reactivity (off-target risk):

```python
# Generic GSH stability assay readout - measure half-life of warhead with 10 mM GSH
# kinact_GSH from time-course of warhead disappearance
```

Do not assign a universal GSH half-life from the warhead name alone. Substitution, electronics, ionization, solubility, and assay conditions can change the observed rate. Report the GSH concentration, buffer, temperature, analytical method, and fitted half-life or second-order rate constant for the complete compound.

## Covalent Docking Tools

| Tool | Approach | Strength | Fails when |
|------|----------|----------|------------|
| DOCKovalent (London et al 2014 Nat Chem Biol 10:1066) | Constraint-based DOCK | Free, well-validated | Browser-based; small library |
| GOLD covalent (CCDC) | GOLD with covalent constraint | Commercial; selectivity | License cost |
| AutoDock 4 covalent | AD4 with covalent bond | Open source | Slower than Vina |
| CovDock (Schrödinger) | Glide-based + covalent | Commercial two-stage covalent docking workflow | License cost |
| MOE covalent | Triposite Discovery | Commercial | License cost |
| HCovDock (Wu Q, Huang S-Y 2023 Briefings Bioinform 24:bbac559) | Hierarchical fragment + covalent | Open; supports many residues | Newer, less validated |
| ICM-Pro covalent | Active site grid + covalent | Commercial; metal centers | License cost |

For open-source covalent docking, **HCovDock** (2023) is the modern alternative; **DOCKovalent** is the longstanding standard.

## Example: KRAS G12C Inhibitor Design Workflow

**Goal:** Decorate a co-crystal scaffold with a cysteine-targeting warhead and rank candidates by covalent efficiency.

**Approach:** Load scaffold SMILES, enumerate acrylamide-bearing analogs, filter by reactivity selectivity, dock under covalent constraint, and rank by kinact/Ki surrogates.

```python
from rdkit import Chem

# Step 1: scaffold from co-crystal (4LRW or AMG510)
scaffold_smi = 'c1ccc(C(=O)NCC)cc1'  # generic valid scaffold for code illustration
scaffold = Chem.MolFromSmiles(scaffold_smi)

# Step 2: enumerate analogs with acrylamide warhead
def add_acrylamide(scaffold, attachment_atom_idx):
    """Project hook: attach a mapped acrylamide with an audited reaction."""
    raise NotImplementedError(
        'Provide a project-specific mapped reaction and validate atom mapping, '
        'valence, regioisomer identity, and product sanitization.'
    )

# Step 3: filter for reactive group selectivity
# Step 4: dock with DOCKovalent / GOLD covalent / HCovDock
# Step 5: rank by kinact/Ki surrogate (compute reactive Michael acceptor reactivity)
```

## Reactivity Surrogates (computed without experiment)

For ranking warheads without wet-lab data:

| Descriptor | Use case |
|------------|----------|
| LUMO energy (DFT) | Michael acceptor reactivity (lower LUMO = more reactive) |
| Electrophile partial charge | SN2 reactivity |
| RDKit `rdMolDescriptors.CalcLabuteASA` | Steric accessibility |
| Experimentally supported binding pose or validated docking model | Geometric fit to reactive residue |

**Goal:** Record alpha-carbon substitution as a structural feature for an acrylamide series.

**Approach:** Parse the SMILES, locate the acrylamide substructure, and count neighbors on the alpha carbon outside the matched warhead. This count is not a LUMO estimate or a stand-alone reactivity prediction; substituent electronics and the rest of the molecule must be considered, and reactivity should be measured.

```python
def acrylamide_alpha_substitution_count(smi):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    acryl_pat = Chem.MolFromSmarts(
        '[CX3:1](=[OX1:2])([NX3:3])[CX3:4]=[CX3:5]'
    )
    matches = mol.GetSubstructMatches(acryl_pat, uniquify=True)
    if not matches:
        return None
    alpha_query_idx = next(
        atom.GetIdx() for atom in acryl_pat.GetAtoms()
        if atom.GetAtomMapNum() == 4
    )
    alpha_c = mol.GetAtomWithIdx(matches[0][alpha_query_idx])
    n_subs = len([n for n in alpha_c.GetNeighbors() if n.GetIdx() not in matches[0]])
    return n_subs
```

For a reactivity model, use experimentally measured rates or a validated quantum-chemical workflow; a single frontier-orbital energy is not sufficient on its own.

## Per-Tool Failure Modes

### Wrong warhead for residue

**Trigger:** A warhead/residue pairing is assumed from a broad class label.

**Mechanism:** Reaction depends on the residue microenvironment, electrophile, binding pose, and catalytic assistance; a class label does not establish residue selectivity.

**Symptom:** No covalent adduct observed despite docking pose.

**Fix:** Use literature-supported residue/warhead chemistry as a hypothesis, then verify site-specific adduct formation and competing reactivity experimentally.

### Excessive reactivity (off-target)

**Trigger:** Chloroacetamide in drug-candidate context.

**Mechanism:** Excess intrinsic electrophile reactivity can increase reaction with GSH and off-target nucleophiles.

**Symptom:** Toxicity in cell-based assays; non-specific binding signal.

**Fix:** Test a less intrinsically reactive electrophile and measure its GSH and target-reaction kinetics; alpha substitution can tune behavior but does not guarantee selectivity or stability.

### Geometric mismatch

**Trigger:** The ligand's reactive atom is poorly positioned relative to the target nucleophile.

**Mechanism:** Covalent reaction requires warhead-specific distance and approach geometry between the electrophilic atom and the nucleophilic atom (Cys Sγ for cysteine).

**Symptom:** No covalent labeling in mass spec despite predicted docking.

**Fix:** Identify the reaction atoms, inspect the pre-reaction Sγ-to-electrophile distance and reaction-specific angles, and use a docking protocol parameterized for that reaction. Do not substitute Cβ distance for the reacting sulfur.

### Reversibility unintended

**Trigger:** Designed irreversible TCI but warhead is reversible.

**Mechanism:** Reversibility depends on the complete electrophile, adduct chemistry, protein environment, and assay timescale; class-level labels are only hypotheses.

**Symptom:** Activity wanes after substrate washout in cellular assays.

**Fix:** Select chemistry with demonstrated behavior in the intended context and verify reversibility by dilution, washout, intact-protein MS, or another suitable experiment.

### kinact/Ki conflation

**Trigger:** Optimizing for IC50 instead of kinact/Ki.

**Mechanism:** Compounds with same IC50 differ in covalent efficiency.

**Symptom:** Compounds with similar endpoint IC50 values show different time-dependent target engagement or pharmacodynamic duration.

**Fix:** Fit a mechanistically appropriate kinetic model. Use `kinact/Ki` for qualifying irreversible two-step systems; use equilibrium, residence-time, or washout measurements where appropriate for reversible covalent systems.

### DOCKovalent over-prediction

**Trigger:** Default DOCKovalent run.

**Mechanism:** Covalent constraint forces docking; many ligands "succeed" but are unrealistic.

**Symptom:** Many compounds pass docking; few label in vitro.

**Fix:** Review measured/validated reactivity, reaction-atom geometry (Cys Sγ for cysteine), non-covalent recognition, strain, and site-specific experimental labeling.

## Reconciliation: Irreversible vs Reversible Covalent

| Aspect | Irreversible | Reversible covalent |
|--------|--------------|---------------------|
| Examples | KRAS G12C (acrylamide), BTK (ibrutinib) | Boronate (bortezomib), aldehyde (calpain inhibitors) |
| Toxicity profile | Off-target Cys labeling potential | Off-target equilibrium |
| Resistance mechanism | Mutation of reactive Cys | Mutation reduces affinity |
| Design decision | Consider duration of target engagement, safety, exposure, and resistance | Consider equilibrium, residence time, and recovery after washout |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Warhead not matching SMARTS | Different stereochemistry or charged | Use canonicalized + neutral SMARTS |
| DOCKovalent rejects ligand | No suitable Cys in pocket | Re-check residue accessibility |
| GSH adduct dominates | Warhead too reactive | Use less reactive warhead; or alpha-substitute |
| Off-target labeling in cells | Promiscuous warhead | Iterate warhead reactivity vs selectivity |
| Docking pose but no labeling | Geometric mismatch | Distance check; rotamer search |
| Intended irreversible inhibitor shows recovery after washout | Adduct chemistry is reversible or covalent reaction is incomplete | Re-evaluate the mechanism and fit the appropriate kinetic model |
| HCovDock fails on PROTAC | Tool optimized for monomer covalent | Use specialized tools for bivalent |

## References

- Lonsdale & Ward, *Chem. Soc. Rev.* 47:3816-3830 (2018) -- irreversible-inhibitor discovery, optimization, and kinetics (DOI 10.1039/C7CS00720C).
- Singh J, Petter RC, Baillie TA, Whitty A. *Nat. Rev. Drug Discov.* 10:307-317 (2011) -- TCI design principles (DOI 10.1038/nrd3410).
- London N et al., *Nat. Chem. Biol.* 10:1066-1072 (2014) -- DOCKovalent (DOI 10.1038/nchembio.1666).
- Wu Q et al., *Brief. Bioinform.* 24:bbac559 (2023) -- HCovDock (DOI 10.1093/bib/bbac559).
- Yu W, Weber DJ, MacKerell AD Jr. *J. Chem. Theory Comput.* 19:3007-3021 (2023) -- SILCS-Covalent and Cys-sulfur/reactive-atom geometry (DOI 10.1021/acs.jctc.3c00232).
- Backus et al., *Nature* 534:570-574 (2016) -- proteome-wide covalent ligand discovery (DOI 10.1038/nature18002).
- Pettinger et al., *Angew. Chem. Int. Ed.* 56:15200-15209 (2017) -- lysine-targeting covalent inhibitors (DOI 10.1002/anie.201707630).
- Ostrem et al., *Nature* 503:548-551 (2013) -- KRAS G12C disulfide-tethered fragments (DOI 10.1038/nature12796).

## Related Skills

- chemoinformatics/molecular-io - Parse warhead SMILES
- chemoinformatics/substructure-search - Warhead SMARTS detection
- chemoinformatics/virtual-screening - Pre-dock candidate non-covalent fit
- chemoinformatics/pose-validation - Validate covalent docking
- chemoinformatics/conformer-generation - Warhead conformer ensembles
- chemoinformatics/admet-prediction - ADMET of covalent leads
- chemoinformatics/molecular-descriptors - Reactivity surrogate descriptors
<!-- END FILE: chemoinformatics/covalent-design/SKILL.md -->

## 子目录：chemoinformatics/free-energy-calculations

<!-- BEGIN FILE: chemoinformatics/free-energy-calculations/SKILL.md -->
---
name: bio-free-energy-calculations
description: Performs alchemical free-energy calculations including relative binding free energy (RBFE / FEP+) and absolute binding free energy (ABFE) via OpenFE, FEP+, GROMACS, AMBER pmemd, and OpenMM with explicit lambda scheduling, soft-core potentials, MBAR/BAR analysis, cycle-closure validation, and protocol-appropriate enhanced sampling. Compares ML alternatives (Boltz-2 affinity, DeepDock). Use when ranking analogs by binding affinity beyond docking accuracy, performing prospective lead optimization, or validating SAR predictions.
tool_type: mixed
primary_tool: OpenFE
---

## Version Compatibility

Reference examples tested with: OpenFE 1.7+, OpenMM 8.1+, GROMACS 2024+, AMBER pmemd 22+, alchemlyb 2.1+, pymbar 4.0+, RDKit 2024.09+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `openfe --version`; `gmx --version`; `pmemd.cuda --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Free Energy Calculations

Predict binding free-energy differences (RBFE) or standard binding free energies (ABFE) using alchemical methods. FEP+ is a commercial workflow and OpenFE is an open-source framework. Accuracy and cost vary substantially with system, perturbation, force field, setup, sampling, and evaluation design; report the protocol and benchmark relevant to the intended decision. The Boltz-2 report includes benchmark-specific comparisons with FEP methods but does not replace prospective validation on the project chemistry.

For docking input poses, see `chemoinformatics/virtual-screening`. For pose validation before FEP, see `chemoinformatics/pose-validation`. For ML alternatives, see `chemoinformatics/ml-docking-rescoring`.

## FEP Method Taxonomy

| Method | Cost / pair | Accuracy | Use case | Fails when |
|--------|-------------|----------|----------|------------|
| FEP+ (Schrödinger) | System- and protocol-dependent GPU cost | Published commercial RBFE workflow | Commercial lead optimization | License and reproducibility constraints |
| OpenFE RBFE | System- and protocol-dependent GPU cost | Open-source RBFE with documented protocols | Open-source campaigns | Mapping/setup/sampling require review |
| OpenFE ABFE | Generally more setup and sampling than one RBFE edge | Standard binding free energy | No congeneric reference ligand required | Restraints and end-state corrections |
| GROMACS / AMBER RBFE | Implementation-dependent | Custom alchemical workflows | Expert-controlled setup | Manual validation burden |
| FEP-SPell-ABFE | Protocol/system-dependent | Automated ABFE workflow | Evaluate published and project benchmarks | Limited adoption |
| QligFEP v2.1 | Protocol/system-dependent | Q-based ligand FEP | Evaluate published and project benchmarks | Different approximations/tooling |
| MM/PBSA / MM/GBSA | Lower-cost endpoint analysis | Approximate endpoint score | Exploratory within-series comparison | Entropy, sampling, and model dependence |
| Boltz-2 affinity | seconds GPU | 0.66 Pearson on reported FEP benchmark subset | ML alternative; reported >=1000x lower cost | Novel chemotypes |
| ALEPB / EE-AMBER | Protocol/system-dependent | Specialized methods | Evaluate matched evidence | Limited tooling |

**Decision:** For congeneric lead-optimization questions, evaluate a validated RBFE protocol and perturbation network. Use endpoint methods only for decisions supported by a project-specific benchmark. Candidate counts and escalation gates should follow compute budget, uncertainty, and prospective validation rather than a universal top-N rule.

## Decision Tree by Scenario

| Scenario | Recommended workflow |
|----------|---------------------|
| Rank close analogs (R-group SAR) | RBFE via OpenFE (cycle: lig1↔lig2↔lig3) |
| Cross-scaffold ranking | ABFE per ligand; or coordinated RBFE with star network |
| Congeneric lead-optimization set | RBFE with a connected, redundancy-aware perturbation graph |
| Single ligand affinity | ABFE (no reference needed) |
| Lower-cost exploratory ranking | A project-validated endpoint or ML method, followed by orthogonal confirmation |
| Novel scaffold prospective | Treat ML affinity as triage; validate selected decisions prospectively |
| Selectivity (target vs off-target) | RBFE on both proteins; report delta-delta-G |
| Allosteric vs orthosteric | ABFE comparable; check pose stability with MD |
| Ions / metal centers | Specialized force field (ZAFF, MCPB.py); not standard FEP |

## Relative Binding Free Energy (RBFE) Setup

**Goal:** Calculate delta-delta-G between two ligands (lig1 -> lig2) in pocket.

**Approach:** Alchemical transformation lig1 -> lig2 in both bound state (pocket + ligand + water) and unbound state (ligand + water alone). Thermodynamic cycle:

```
delta(delta-G_binding) = (delta-G_lig1->lig2 in pocket) - (delta-G_lig1->lig2 in solvent)
```

```python
# OpenFE simplified setup (real usage requires complete protocol setup)
from openfe import SmallMoleculeComponent, ProteinComponent, SolventComponent
from openfe.protocols.openmm_rfe import RelativeHybridTopologyProtocol

protein = ProteinComponent.from_pdb_file('receptor.pdb')
ligA = SmallMoleculeComponent.from_sdf_file('ligand_A.sdf')
ligB = SmallMoleculeComponent.from_sdf_file('ligand_B.sdf')
solvent = SolventComponent()

protocol = RelativeHybridTopologyProtocol(
    RelativeHybridTopologyProtocol.default_settings()
)
```

The protocol object does not itself choose an atom mapping or define a simulation. Create or inspect a mapping (Kartograf is the OpenFE 1.7 CLI default; LOMAP is also supported), construct bound and solvent `Transformation` objects, create their protocol DAGs, and run them through `openfe quickrun` or the documented Python execution interface. Always inspect the selected mapping before running.

## Lambda Window Scheduling

| Stage | Lambda values | Purpose |
|-------|---------------|---------|
| Decoupling (vdW) | 0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0 | Turn off ligand vdW |
| Charging (Coulomb) | 0.0, 0.25, 0.5, 0.75, 1.0 | Turn off ligand partial charges |
| Restraint (ABFE only) | 0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0 | Boresch-style restraints |

The 12-20 windows and 5-20 ns per-window ranges are repository starting ranges, not universal prescriptions. Select and extend them from overlap, exchange, and replicate-convergence diagnostics for the system; total cost therefore varies substantially.

## Enhanced Sampling

REST2 (Replica Exchange with Solute Tempering) is one enhanced-sampling approach used in some FEP workflows. It scales selected interactions to improve barrier crossing, but suitability and implementation are engine- and protocol-specific.

In FEP+, REST2 region typically includes:
- The entire ligand
- Flexible binding-site loops
- Catalytic / ionic residues with high pKa shift potential

FEP+ can use a configured REST2 region. OpenFE's `RelativeHybridTopologyProtocol` uses Hamiltonian replica exchange across its lambda states by default; that is not the same as REST2, and OpenFE does not automatically apply REST2. Use only enhanced-sampling modes supported and documented by the selected protocol and version.

## MBAR/BAR Analysis

After production simulation, extract delta-G via MBAR (Multistate Bennett Acceptance Ratio) or BAR (Bennett Acceptance Ratio). MBAR uses data from all windows simultaneously; BAR uses adjacent windows.

```python
from alchemlyb import concat
from alchemlyb.parsing import gmx
from alchemlyb.estimators import MBAR
from alchemlyb.postprocessors.units import to_kcalmol

u_nks = []
for window in range(12):
    df = gmx.extract_u_nk(f'window_{window}.xvg', T=300)
    u_nks.append(df)

u_nk = concat(u_nks)
mbar = MBAR().fit(u_nk)
delta_g = to_kcalmol(mbar.delta_f_).iloc[0, -1]
d_delta_g = to_kcalmol(mbar.d_delta_f_).iloc[0, -1]
print(f'delta-G: {delta_g:.2f} +/- {d_delta_g:.2f} kcal/mol')
```

`MBAR.delta_f_` and `d_delta_f_` are dimensionless (in kT) until explicitly converted. The parser shown above reads GROMACS XVG files. For other engines, use the engine-specific parser supported by the installed alchemlyb version.

## Cycle Closure Analysis

For a single directed thermodynamic cycle, the signed closure residual is the sum of its edges and should be consistent with zero within uncertainty. An RMS closure statistic requires residuals from multiple cycles and a stated aggregation convention.

```python
def cycle_closure_residual(cycle):
    # cycle is list of edges, each (lig_i, lig_j, delta_g, sd)
    total = sum(d_g for _, _, d_g, _ in cycle)
    total_var = sum(sd**2 for _, _, _, sd in cycle)
    return total, total_var ** 0.5
```

Interpret each closure residual relative to propagated edge uncertainties, replicate behavior, shared-edge correlations, network topology, and the decision supported. If reporting RMS across cycles, state which cycles were included and avoid treating correlated cycles as independent observations.

## Absolute Binding Free Energy (ABFE)

ABFE computes delta-G of binding for a single ligand (no reference compound).

**Goal:** Estimate the standard binding free energy of a single ligand prospectively. Conversion to an equilibrium dissociation constant requires an explicit standard-state convention; ABFE does not generically predict an assay `Ki`.

**Approach:** Decouple ligand from solvated state and from pocket-bound state separately; correction terms for analytical end states.

Use OpenFE's documented `AbsoluteBindingProtocol` workflow: construct the ligand and complex chemical systems, select and inspect the restraint setup, create the corresponding `Transformation` objects, serialize them with `Transformation.to_json()`, and execute each transformation with `openfe quickrun`. Do not substitute an ad hoc `absolute-free-energy` CLI; OpenFE does not provide that command.

ABFE is harder than RBFE: requires Boresch-style restraints to keep ligand near pocket during decoupling. Restraint contribution must be analytically corrected.

ABFE cost relative to RBFE depends on the protocols, number of legs/windows/repeats, and convergence requirements; estimate it from the explicit campaign plan.

## MM/PBSA, MM/GBSA Endpoint Methods

Lower-cost endpoint alternatives whose usefulness must be established on a matched benchmark:

```bash
# MM/GBSA via AMBER MMPBSA.py
MMPBSA.py -i input.in -cp complex.parm7 -rp receptor.parm7 \
          -lp ligand.parm7 -y trajectory.nc
```

Sample input:
```
&general
  startframe = 100, endframe = 1000, interval = 10
/
&gb
  igb = 5
/
&pb
  istrng = 0.150
/
```

**Use case:** Exploratory ranking when a matched retrospective benchmark shows the endpoint method supports the intended decision. Do not transfer generic correlation ranges across targets or protocols.

## Force Field Selection

| Force field | Use for | Notes |
|-------------|---------|-------|
| OPLS4 (Schrödinger) | FEP+ default | Commercial; well-tested |
| OpenFF 2.1.1 (Sage) | OpenFE 1.7 documented default | Inspect serialized settings; newer OpenFE releases use different defaults |
| GAFF2 | AMBER FEP | Use for ligand only; protein FF14SB |
| GAFF | Legacy | Replaced by GAFF2 |
| CGenFF | CHARMM-style FEP | CHARMM force-field family |
| ANI-2x | Mixed QM/MM | Experimental for FEP |
| MACE-OFF | Modern ML force field | Promising for FEP, limited tooling |

For OpenFE 1.7, the versioned documentation shows OpenFF 2.1.1 for the ligand and Amber-family protein/water XMLs including ff14SB and TIP3P. Inspect and serialize the actual protocol settings because defaults change between releases.

## Per-Tool Failure Modes

### Insufficient sampling

**Trigger:** Production length is insufficient for a slow ligand or protein degree of freedom.

**Mechanism:** Replica exchange improves state mixing but is not a panacea; some conformational changes remain slow.

**Symptom:** Replicates, time-sliced estimates, overlap/exchange diagnostics, or closure residuals are inconsistent with the reported uncertainty.

**Fix:** Increase sampling, inspect exchange and state overlap, run independent repeats, and investigate slow protein/ligand degrees of freedom. Use only protocol-supported enhanced sampling; check whether the pose is genuinely stable.

### Force-field artifacts

**Trigger:** Charged ligand or charged pocket residue.

**Mechanism:** GAFF2/SAGE may misparameterize unusual functional groups (perfluoro, charged sulfonate near Asp/Glu).

**Symptom:** A transformation is an outlier relative to experiment, replicates, or network consistency.

**Fix:** Visual inspection; check ligand topology with rdkit; consider non-bonded fix or fragment-specific parameters.

### Mapping ambiguity

**Trigger:** Two ligands differ in scaffold (not just R-groups).

**Mechanism:** LOMAP atom mapping may not find good correspondence; results from ambiguous mappings unreliable.

**Symptom:** Mapping score low; large dummy-atom count; cycle closure errors.

**Fix:** Manual mapping using OpenFE's editor; or use ABFE per ligand instead of RBFE.

### Restraint contribution wrong (ABFE)

**Trigger:** Boresch restraint applied to flexible region of ligand.

**Mechanism:** Analytical restraint correction assumes harmonic potential at well-defined minimum.

**Symptom:** ABFE shows a systematic offset or strong sensitivity to restraint choices.

**Fix:** Choose Boresch restraint atoms from rigid ligand core; not flexible side chains.

### MM/GBSA -- bias from entropy missing

**Trigger:** Comparing ligands of very different size.

**Mechanism:** MM/GBSA misses entropy contribution; larger ligands appear more favorable.

**Symptom:** Larger ligands always rank higher.

**Fix:** Use MM/GBSA only for within-series ranking; supplement with FEP for cross-size.

### Boltz-2 affinity -- chemotype OOD

**Trigger:** Novel chemotype outside training distribution.

**Mechanism:** Boltz-2 affinity training uses standardized public biochemical-assay data, including PubChem and ChEMBL sources, alongside its structural training. Novel targets, chemotypes, and assay contexts can still extrapolate.

**Symptom:** Boltz-2 affinity and FEP affinity disagree.

**Fix:** Use Boltz-2 as a benchmarked triage model and validate selected candidates with orthogonal computation and experiment. Do not interpret structure-confidence outputs as calibrated affinity intervals.

## Reconciliation: FEP+ vs OpenFE

| Aspect | FEP+ | OpenFE |
|--------|------|--------|
| Force field | OPLS4 (proprietary) | OpenFF 2.1.1 in versioned OpenFE 1.7 defaults; inspect serialized settings |
| Workflow | Schrödinger GUI | Python CLI/API |
| Atom mapping | Product workflow | Kartograf CLI default in OpenFE 1.7; LOMAP also supported |
| Reported accuracy | Benchmark-dependent | Benchmark-dependent; compare matched protocols and systems |
| Cost | Schrödinger license | Free + compute time |
| Decision | Commercial team default | Open-source / academic / cost-sensitive |

Choose OpenFE or a commercial workflow according to validated performance, auditability, available expertise, licensing, and integration requirements.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Lambda window simulation diverges | Bad initial pose | Re-relax pose with MM minimization first |
| Closure residual is inconsistent with propagated uncertainty or independent repeats | Sampling, mapping, force-field, or correlated-edge issue | Inspect signed residuals, overlap, mapping, and independent repeats before extending sampling |
| MBAR returns NaN | Insufficient overlap between windows | Add intermediate lambda windows |
| Restraint contribution wrong | Boresch atoms on flexible region | Choose 3 atoms on rigid ligand core |
| Slow binding-site rearrangement | Standard sampling does not cross the barrier | Increase sampling/repeats and use only engine- and protocol-documented enhanced sampling |
| ABFE systematic offset | Restraint, standard-state, sampling, or force-field issue | Inspect the protocol's documented restraint/free-energy terms and signs; do not invent an ad hoc correction variable |
| MM/GBSA rmsd doesn't match docking | Different trajectory frames | Compute MM/GBSA on MD-relaxed pose |

## References

- Mey ASJS et al., *Living J. Comput. Mol. Sci.* 2:18378 (2020) -- alchemical free-energy best practices (DOI 10.33011/livecoms.2.1.18378).
- Wang L et al., *J. Am. Chem. Soc.* 137:2695-2703 (2015) -- FEP+ method (DOI 10.1021/ja512751q).
- Open Free Energy developers. *OpenFE* software, Zenodo (2023-present) -- open-source alchemical free-energy framework (DOI 10.5281/zenodo.8344247).
- Cournia Z et al., *J. Chem. Inf. Model.* 60:4153-4169 (2020) -- rigorous ABFE as a final stage in virtual screening (DOI 10.1021/acs.jcim.0c00116).
- Aldeghi M, Bluck JP, Biggin PC. *Methods Mol. Biol.* 1762:199-232 (2018) -- beginner's guide to absolute alchemical ligand-binding free energies (DOI 10.1007/978-1-4939-7756-7_11).
- Passaro S et al. *bioRxiv* (2025) -- Boltz-2 affinity prediction preprint (DOI 10.1101/2025.06.14.659707).
- Shirts MR, Chodera JD. *J. Chem. Phys.* 129:124105 (2008) -- MBAR (DOI 10.1063/1.2978177).
- Bennett CH. *J. Comput. Phys.* 22:245-268 (1976) -- BAR (DOI 10.1016/0021-9991(76)90078-4).
- OpenFE 1.7 documentation: https://docs.openfree.energy/en/v1.7.0/
- alchemlyb documentation: https://alchemlyb.readthedocs.io/

## Related Skills

- chemoinformatics/virtual-screening - Source poses for FEP input
- chemoinformatics/pose-validation - PoseBusters-validate before FEP
- chemoinformatics/conformer-generation - Generate ligand 3D for FEP setup
- chemoinformatics/molecular-standardization - Standardize ligand before FEP
- chemoinformatics/ml-docking-rescoring - Boltz-2 affinity as alternative
- chemoinformatics/qsar-modeling - Surrogate models for high-throughput
<!-- END FILE: chemoinformatics/free-energy-calculations/SKILL.md -->

## 子目录：chemoinformatics/generative-design

<!-- BEGIN FILE: chemoinformatics/generative-design/SKILL.md -->
---
name: bio-generative-design
description: Designs novel molecules using REINVENT 4 (de novo, scaffold decoration, linker design, R-group, molecular optimization), MolMIM, Diffusion-based generators (DiGress, DiffSMol), and JT-VAE with explicit handling of multi-parameter optimization (MPO), goal-directed scoring functions, transfer/reinforcement/curriculum learning, synthetic accessibility scoring, and chemical space exploration vs exploitation. Use when designing new chemical matter against a target, decorating a scaffold, linking fragments, or optimizing a hit for multiple ADMET / activity properties simultaneously.
tool_type: python
primary_tool: REINVENT
---

## Version Compatibility

Reference examples tested with: REINVENT 4.0+, RDKit 2024.09+, PyTorch 2.1+, MolMIM (NVIDIA BioNeMo), chemprop 2.0+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Generative Molecular Design

Generate novel molecules biased toward desired properties using deep generative models. REINVENT 4 (Loeffler et al. 2024, AstraZeneca) provides four generator families: Reinvent (de novo), Libinvent (scaffold decoration and library design), Linkinvent (linker design), and Mol2Mol (similarity-constrained molecular optimization). These support design tasks including R-group replacement and scaffold hopping and can be used with transfer learning, reinforcement learning, and curriculum learning. For specific niches: MolMIM (NVIDIA BioNeMo) for latent-space property optimization, DiffSMol / DiGress for diffusion-based generation, and JT-VAE for latent-space optimization. The art of generative design is in the **scoring function**: poorly-designed scoring rewards uninteresting molecules, while well-designed scoring captures both activity and developability.

For QSAR/scoring models that feed generative design, see `chemoinformatics/qsar-modeling`. For synthetic feasibility, see `chemoinformatics/retrosynthesis`. For library enumeration as alternative, see `chemoinformatics/reaction-enumeration`.

## Generator Mode Taxonomy

| Mode | Input | Output | Use case | Fails when |
|------|-------|--------|----------|------------|
| De novo | Empty seed or training set | Novel molecules | Wide chemical space exploration | Synthetic feasibility weak |
| Scaffold decoration | Scaffold + attachment points | Decorated molecules | Series expansion | Generation diversity limited by scaffold |
| Linker design | 2 fragments | Linker molecules | PROTAC, ternary complex | Few linker geometric options |
| R-group replacement | Scaffold + existing R-groups | New R-group set | Optimize one position | Single-position only |
| Molecular optimization | Lead molecule | Improved analogs | Lead optimization | Improvement window narrow |
| Constrained generation | Hard constraints (MW, fragments) | Compliant molecules | Patent / IP design | Constraints overly restrictive |

## Learning Algorithm Taxonomy

| Algorithm | Use | Pro | Con |
|-----------|-----|-----|-----|
| Transfer learning (TL) | Adapt prior model to focused training set | Stable, simple | Limited optimization power |
| Reinforcement learning (RL) | Reward-driven generation | Powerful for MPO | Reward hacking risk |
| Curriculum learning (CL) | Gradual constraint introduction | Better convergence | Slower; tuning sensitive |

## Decision Tree by Scenario

| Scenario | Generator | Algorithm | Scoring |
|----------|-----------|-----------|---------|
| New target, no SAR | De novo | Benchmark RL against simpler search | Validated target evidence + developability objectives |
| Series expansion | Scaffold decoration | TL on series + RL | QSAR ensemble + QED |
| PROTAC linker | Linker design | Project-specific constrained workflow | Validated geometry/ternary-complex evidence; no generic DC50 surrogate |
| Lead optimization MPO | Molecular optimization | CL with staged constraints | Multi-task: activity + ADMET |
| Diverse hit set | De novo with diversity bonus | RL + Tanimoto distance to known | Activity + diversity |
| Patent space carve-out | Constrained de novo | RL + structural constraints | Activity + novelty |
| Hit-to-lead | R-group replacement | TL on lead + RL | Activity + Lipinski |
| ADMET-aware design | De novo or optimization | RL | hERG + CYP + AMES + QED |

## REINVENT 4 Setup

REINVENT 4 uses a TOML configuration file specifying generator, algorithm, prior model, and scoring functions.

**Goal:** Configure a reinforcement-learning REINVENT 4 run with a prior, agent, sampling parameters, and a QED scoring component.

**Approach:** Build a release-matched REINVENT 4 staged-learning TOML config with `[parameters]` for the prior/agent checkpoints, `[[stage]]` blocks, and one or more `[[stage.scoring.component]]` blocks. Validate the config with the installed release because component parameters evolve between versions.

```toml
run_type = "staged_learning"
device = "cuda:0"

[parameters]
prior_file = "priors/reinvent.prior"
agent_file = "priors/reinvent.prior"
batch_size = 64
unique_sequences = true

[[stage]]
termination = "simple"
min_steps = 25
max_steps = 500

[stage.scoring]
type = "geometric_mean"

[[stage.scoring.component]]
[stage.scoring.component.QED]

[[stage.scoring.component.QED.endpoint]]
name = "QED"
weight = 1
```

```bash
# The REINVENT 4 CLI binary is `reinvent` (not `reinvent4`).
reinvent -l logfile.log config.toml
```

Output: a live stage CSV using `summary_csv_prefix`, plus the configured `chkpt_file` at stage termination or graceful interruption. Post-process the CSV to select molecules; REINVENT does not emit a checkpoint and SMILES file at every iteration by default.

## Scoring Function Design (Most Important Part)

A good scoring function:
- Returns 0-1 (normalized)
- Combines multiple endpoints
- Penalizes pathological generations (PAINS, unstable, unsynthesizable)

**Goal:** Build a multi-component generative reward that balances predicted activity, drug-likeness, synthesizability, and novelty.

**Approach:** Combine a QSAR sigmoid on pIC50, QED, SA-score reverse-sigmoid, and Tanimoto-similarity reverse-sigmoid via geometric mean so any zero component zeroes the total.

In REINVENT 4, define these under the active stage's `[stage.scoring]` section, with each component using the exact component and endpoint tables from the installed release's configuration examples. Do not reuse REINVENT 3 `[scoring_function]` or `[[scoring_function.components]]` syntax in a REINVENT 4 config. The accompanying example is deliberately limited to built-in, documented component structure; add predictive-property endpoints only after validating their release-specific model-container parameters.

`geometric_mean` ensures all components must be reasonably high (one zero -> zero total). `arithmetic_mean` allows compensation.

## Multi-Parameter Optimization (MPO)

Lead optimization commonly involves multiple objectives. The following component types illustrate a project-specific scoring design; weights and transforms must be fit to the actual assays and decision context.

| Component | Weight | Transformation |
|-----------|--------|----------------|
| Target activity (predicted pIC50) | 0.3 | sigmoid 5-8 |
| Selectivity (off-target ratio) | 0.2 | sigmoid 1-100 |
| QED | 0.1 | identity |
| Synthetic accessibility (SA score) | 0.1 | reverse sigmoid 1-4 |
| hERG predicted prob | 0.1 | reverse sigmoid 0.3-0.7 |
| AMES predicted prob | 0.1 | reverse sigmoid 0.3-0.7 |
| Tanimoto novelty vs known | 0.1 | reverse sigmoid 0.4-0.6 |

The weights and transformation bounds above are repository starting examples only. Normalize weights as required by the selected aggregation and tune every bound against project assay distributions and prospective behavior.

## Reward Hacking (Production Pitfall)

RL agents will find ways to maximize reward without learning the intended behavior:
- Trivial scaffolds that score high on QED
- Repeat structural motifs that game similarity scoring
- Out-of-distribution molecules that exploit QSAR overconfidence
- Trivial SMILES (e.g., "CCC...C") that match generic scoring

**Mitigations:**
- Include one or more synthesis-aware signals when they have been validated for the project; SA score alone does not establish route feasibility
- Use ensemble QSAR with uncertainty (penalize high-uncertainty predictions)
- Include diversity bonus (Tanimoto to reference)
- Add fingerprint similarity penalty within batch (prevent mode collapse)
- Validate generated samples on held-out QSAR test set

## Synthetic Accessibility Scoring

`sa_score` (Ertl 2009) measures synthetic accessibility: 1 (easy) to 10 (very hard).

```python
from rdkit.Contrib.SA_Score import sascorer
from rdkit import Chem

def sa_score(smi):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    return sascorer.calculateScore(mol)
```

`sascorer` is shipped in RDKit Contrib in current RDKit distributions. Use the namespaced import above; do not install an unrelated top-level package.

The score is a 1-to-10 heuristic derived from fragment contributions and molecular complexity, with lower values intended to indicate easier synthesis. It is not a route planner, cost estimate, or calibrated feasibility probability. Use it as one audited reward component or annotation, never as an absolute filter.

## Diffusion-Based Generation (Modern Alternatives)

| Tool | Approach | Strength | Status |
|------|----------|----------|--------|
| DiGress (Vignac 2023) | Discrete diffusion on graphs | Conditional generation | Public |
| DiffSMol (Chen 2025) | Equivariant diffusion | 3D molecule generation | Public |
| MolDiff (Peng 2023) | Full-atom diffusion | Joint atom/bond generation | Public |
| TargetDiff (Guan 2023) | Pocket-conditioned equivariant diffusion | Structure-based design | Public |

Diffusion models iteratively denoise molecular representations, whereas REINVENT generators autoregressively construct SMILES. Diversity, validity, and drug-likeness depend on the model, training data, conditioning, and evaluation protocol; compare them on a matched benchmark for the intended task.

## Constrained / Goal-Directed Generation

**Goal:** Enforce hard structural requirements (e.g., must contain hydroxyl) and exclude PAINS without letting constraint satisfaction game the reward.

**Approach:** Stage transfer learning then RL. In REINVENT 4, `CustomAlerts` is a global structural-alert filter: a match produces zero and it is applied before score aggregation. `MatchingSubstructure` is a scoring component (1 for a match and 0.5 otherwise), so it is a soft penalty rather than a hard inclusion constraint. Apply a separate post-generation SMARTS validation step when presence of a feature is mandatory.

```toml
[[stage.scoring.component]]
[stage.scoring.component.CustomAlerts]

[[stage.scoring.component.CustomAlerts.endpoint]]
name = "Unwanted SMARTS"
params.smarts = ["PAINS_SMARTS_1", "BRENK_SMARTS_1"]

[[stage.scoring.component]]
[stage.scoring.component.MatchingSubstructure]

[[stage.scoring.component.MatchingSubstructure.endpoint]]
name = "Hydroxyl preference"
weight = 0.1
params.smarts = ["[OX2H]"]
```

There is no REINVENT 4 `filter_only` option for these components. Treat structural alerts as triage flags where appropriate, and separately verify any true hard inclusion or exclusion rule on the generated structures.

## MolMIM (NVIDIA BioNeMo)

MolMIM encodes SMILES into a learned latent space, uses gradient-free CMA-ES to optimize a user-defined property objective, and decodes candidate molecules.

```python
# Pseudo-code; requires NVIDIA NIM access
# from bionemo.molmim import MolMIMOptimizer
# optimizer = MolMIMOptimizer(model="molmim-property-optimizer")
# optimized = optimizer.optimize(seed_smiles, target_property="logp", target_value=2.0)
```

Tradeoffs against REINVENT depend on the oracle budget, objective, and implementation; benchmark both under matched constraints when selecting a generator.

## Per-Tool Failure Modes

### REINVENT RL -- mode collapse

**Trigger:** The reward, learning strategy, or diversity control favors a narrow chemotype.

**Mechanism:** Agent finds a high-scoring local maximum and stops exploring.

**Symptom:** Diversity and scaffold coverage collapse relative to a project-defined baseline while reward continues to rise.

**Fix:** Add diversity bonus to scoring; reduce sigma; reset agent if collapsed.

### REINVENT TL -- overfitting

**Trigger:** Transfer learning data are too small or homogeneous for the intended generalization task.

**Mechanism:** Generator memorizes training set; no generalization.

**Symptom:** Generated molecules near-identical to training set actives.

**Fix:** Use larger training set; mix with diverse external sample; apply RL after TL.

### Generated molecule unsynthesizable

**Trigger:** SA score missing from reward.

**Mechanism:** The reward omits synthesis evidence, allowing candidates with no plausible validated route to score well.

**Symptom:** AiZynthFinder cannot solve route; medchem rejects.

**Fix:** Combine audited synthesis-aware annotations with reaction- or route-based validation for selected candidates.

### PAINS in generation

**Trigger:** No structural alerts in scoring.

**Mechanism:** Curcumin / rhodanine / quinone scaffolds optimize for activity (false positives in training data).

**Symptom:** Generated molecules match PAINS_A.

**Fix:** Flag relevant structural alerts for orthogonal assay review or apply a project-justified penalty; never reward a PAINS match.

### Diffusion model OOD

**Trigger:** Pocket-conditioned diffusion on novel target family.

**Mechanism:** Training distribution covered specific protein families; novel targets extrapolate.

**Symptom:** Generated molecules look like training distribution, not optimized for target.

**Fix:** Validate on target-family-held-out evaluation; supplement with classical methods.

### Validation set leakage

**Trigger:** Same molecules in training generators and downstream QSAR.

**Mechanism:** Scoring model has seen the molecule; predictions optimistic.

**Symptom:** Held-out QSAR validation fails on top generated.

**Fix:** Use scaffold-split QSAR; ensure scoring model trained on a held-out set vs generation samples.

## Reconciliation: REINVENT vs Diffusion

| Aspect | REINVENT 4 | Diffusion |
|--------|------------|-----------|
| Speed | Implementation-, hardware-, and oracle-dependent | Implementation-, hardware-, and sampling-step-dependent |
| Output diversity | Model/training/reward-dependent | Model/training/conditioning-dependent |
| Drug-likeness of output | Training- and reward-dependent | Training- and conditioning-dependent |
| Scoring flexibility | Excellent (TOML config) | Method-specific |
| Production maturity | High | Emerging |
| When to use | When its priors and scoring system validate well for the task | When a matched benchmark supports the selected diffusion model |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| REINVENT generates invalid SMILES | Prior/tokenization/model mismatch or sampling issue | Inspect invalid-token logs, prior compatibility, and release-matched sampling settings; sigma is not a token sampling rate |
| QSAR score all 0.0 | Out-of-domain molecules | Ensemble + uncertainty; reject high-uncertainty |
| All generations duplicates | `unique_sequences=False` | Set `unique_sequences=true` |
| Generated SMILES too long | Prior/model sequence behavior | Use a release-documented sampling constraint or post-generation project rule; do not invent a staged-learning `max_length` field |
| Reward stuck at 0.5 | Constraints conflict | Inspect scoring components; reduce constraint count |
| Diffusion model crashes | Input violates model-specific pocket/size contract | Follow that model release's documented preprocessing and limits |
| MolMIM cold-start slow | Latent search exhaustiveness | Reduce search budget |
| Optimization converges trivially | Reward gradient dominated by one term | Use geometric_mean; rebalance weights |

## References

- Loeffler et al., *J. Cheminformatics* 16:20 (2024) -- REINVENT 4 framework and four generator families (DOI 10.1186/s13321-024-00812-5).
- Olivecrona M et al., *J. Cheminformatics* 9:48 (2017) -- REINVENT original (DOI 10.1186/s13321-017-0235-x).
- Vignac et al., *ICLR* (2023) -- DiGress discrete diffusion.
- Chen H et al., *Nat. Mach. Intell.* 7:758-770 (2025) -- DiffSMol structure-based 3D molecular generation (DOI 10.1038/s42256-025-01030-w).
- Peng X, Guan J, Liu Q, Ma J. *Proc. ICML*, PMLR 202:27611-27629 (2023) -- MolDiff full-atom molecular diffusion.
- Guan J et al., *ICLR* (2023) -- TargetDiff pocket-conditioned 3D equivariant diffusion (OpenReview: kJqXEPXMsE0).
- Reidenbach D, Livne M, Ilango RK, Gill M, Israeli J. *MLDD Workshop at ICLR* (2023) -- MolMIM and CMA-ES latent-space optimization (OpenReview: iOJlwUTUyrN).
- Jin W, Barzilay R, Jaakkola T. *Proc. ICML*, PMLR 80:2323-2332 (2018) -- JT-VAE junction-tree.
- Ertl P, Schuffenhauer A. *J. Cheminformatics* 1:8 (2009) -- SA score (DOI 10.1186/1758-2946-1-8).
- REINVENT 4 official repository and release-matched configs: https://github.com/MolecularAI/REINVENT4
- RDKit SA-score implementation: https://github.com/rdkit/rdkit/tree/master/Contrib/SA_Score

## Related Skills

- chemoinformatics/qsar-modeling - Build scoring models for generative
- chemoinformatics/retrosynthesis - Validate synthetic feasibility post-generation
- chemoinformatics/molecular-standardization - Standardize generated SMILES
- chemoinformatics/admet-prediction - ADMET in scoring components
- chemoinformatics/substructure-search - PAINS / BRENK filter for generation
- chemoinformatics/scaffold-analysis - Scaffold-aware generation control
- chemoinformatics/reaction-enumeration - Alternative to generative for combinatorial
- chemoinformatics/virtual-screening - Validate generated against target
<!-- END FILE: chemoinformatics/generative-design/SKILL.md -->

## 子目录：chemoinformatics/ml-docking-rescoring

<!-- BEGIN FILE: chemoinformatics/ml-docking-rescoring/SKILL.md -->
---
name: bio-ml-docking-rescoring
description: Performs ML-based protein-ligand pose prediction and scoring using DiffDock-L (diffusion-based), Boltz-1 / Boltz-2 (foundation model with affinity), Chai-1, AlphaFold3 ligand, EquiBind, TANKBind, NeuralPLexer, and hybrid workflows (DiffDock pose + GNINA rescore + PoseBusters QC). Explicit handling of when ML beats classical docking, when classical beats ML, the PB-invalid pose problem, and rescoring as the standard production hybrid. Use when modern docking is needed: foundation-model ligand-pose prediction, AI rescoring of classical poses, or scaffold-hopping in cross-docking scenarios.
tool_type: python
primary_tool: DiffDock
---

## Version Compatibility

Reference examples tested with: DiffDock-L (Corso et al. 2024), Boltz-1 1.0+, Boltz-2 (Passaro et al. 2025), Chai-1 0.4+, AlphaFold 3 (DeepMind), EquiBind, TANKBind, GNINA 1.1+, and PoseBusters 0.6+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `diffdock --version`; `boltz --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ML Docking and Rescoring

Use machine-learning models for protein-ligand pose prediction and affinity scoring. Foundation models such as AlphaFold 3, Boltz, and Chai-1 handle protein-ligand complex prediction, while DiffDock-L extends the original DiffDock method for ligand-pose sampling (Corso et al. 2023, 2024). Boltz-2 reports affinity prediction approaching physics-based free-energy methods on its evaluated benchmarks at substantially lower computational cost. Physical plausibility remains a separate requirement: on the PoseBusters Benchmark, the original DiffDock produced a correct and physically valid pose for 12% of complexes, compared with 58% for Vina and 55% for GOLD (Buttenschoen et al. 2024). Use ML sampling with independent scoring and physical validation rather than treating model confidence as sufficient.

For classical docking, see `chemoinformatics/virtual-screening`. For pose validation (PoseBusters), see `chemoinformatics/pose-validation`. For free-energy calculations (post-docking), see `chemoinformatics/free-energy-calculations`. For PROTAC ternary complex prediction, see `chemoinformatics/protac-degraders`.

## ML Docking Method Taxonomy

| Tool | Approach | Speed | Strength | Fails when |
|------|----------|-------|----------|------------|
| DiffDock-L (Corso et al. 2024) | Equivariant diffusion | GPU; hardware-dependent | Diverse pose sampling for cross-docking | Requires physical validation; OOD risk |
| Boltz-1 (Wohlwend et al. 2024) | AlphaFold-style foundation | GPU; hardware-dependent | Full complex prediction | Confidence is not affinity or physical validation |
| Boltz-2 (Passaro et al. 2025) | Boltz-1 + affinity module | GPU; hardware-dependent | Joint pose and affinity triage | Benchmark- and chemotype-dependent accuracy |
| Chai-1 (Chai Discovery 2024) | AlphaFold-style + language model | GPU; hardware-dependent | Open-weight complex prediction | Validate ligands and cofactors independently |
| AlphaFold 3 (Abramson et al. 2024) | Foundation model | Local code/weights or public server | Complex prediction with proteins and ligands | Server and local distributions have different terms and limits |
| EquiBind | Equivariant single-shot | <1s GPU | Fast pose | Lowest accuracy on PoseBusters |
| TANKBind | Distance + classifier | <1s GPU | Fast pose + score | Geometric inconsistency |
| NeuralPLexer | E3-equivariant generative model | GPU; hardware-dependent | Protein-ligand structure prediction | Validate geometry and confidence on the target domain |
| Glide (Schrödinger) | Grid-based docking and empirical scoring | License and hardware-dependent | Commercial docking workflow | License cost |
| GNINA 1.1 CNN | Classical sampling + CNN scoring | GPU; hardware-dependent | CNN-assisted pose ranking | Validate transfer to the target and chemotype |

**Decision:** For pose prediction when the complex structure must also be predicted, benchmark an open model such as Boltz or Chai-1 on target-relevant controls. For a known holo receptor, DiffDock-L sampling followed by GNINA rescoring and PoseBusters checks is one auditable hybrid option. Compare it with an appropriate classical-docking baseline rather than assuming one workflow is universally superior.

## Candidate Workflows to Benchmark by Scenario

| Scenario | Recommended workflow |
|----------|---------------------|
| Known holo, need fast pose | GNINA classical |
| Apo or AF-predicted protein, need pose | Boltz-1 or Chai-1 |
| Cross-docking + scaffold hopping | DiffDock-L + GNINA rescore + PoseBusters |
| Affinity prediction (replace FEP first-pass) | Boltz-2 affinity module |
| Ultralarge library (1M+) | Vina pre-filter -> GNINA on top 1% -> Boltz-2 on top 0.1% |
| Novel target family | Boltz-1 / Chai-1 (uses MSA flexibility) |
| Cofactor / metal binding | Use a model/interface that explicitly supports the component; validate coordination geometry independently |
| PROTAC / bivalent | Boltz-1 / Chai-1 with multimer + constraints |
| Production with auditable poses | GNINA classical + Boltz-2 score |

The library fractions in this table are repository starting heuristics. Calibrate stage cutoffs using target-relevant controls, measured throughput, and chemotype-retention analysis.

## PoseBusters Problem (Critical)

The PoseBusters paper evaluated DeepDock, DiffDock, EquiBind, TankBind, Uni-Mol, Vina, and GOLD. It did **not** benchmark DiffDock-L, GNINA, AlphaFold 3, Chai-1, Boltz-1, or Boltz-2. On the 308-complex PoseBusters Benchmark, the reported fraction of predictions that were both within 2 Å RMSD and physically valid was:

| Tool/version evaluated in the paper | RMSD <= 2 Å and PB-valid |
|-------------------------------------|------------------------------|
| Vina | 58% |
| GOLD | 55% |
| DiffDock | 12% |

**Conclusion:** Pose accuracy and chemical plausibility are different axes. Require PoseBusters-style checks for generated poses; calculate RMSD only when a reference pose is available. Do not transfer these percentages to newer model versions without a matched benchmark.

## DiffDock-L + GNINA Hybrid Workflow

**Goal:** Evaluate DiffDock-L pose sampling, GNINA CNN rescoring, and PoseBusters checks as separate stages whose contributions can be audited.

```bash
# Step 1: run from the official DiffDock checkout.
# --ligand accepts one SMILES or ligand file; use --protein_ligand_csv for batches.
cd /path/to/DiffDock
python -m inference \
    --config default_inference_args.yaml \
    --protein_path receptor.pdb \
    --ligand 'CC(=O)c1ccccc1' \
    --out_dir diffdock_out/ \
    --samples_per_complex 40 \
    --inference_steps 20

# Step 2: GNINA CNN rescoring
# DiffDock writes rank*.sdf files inside a per-complex output directory.
gnina -r receptor.pdb -l diffdock_out/<complex_name>/rank1.sdf \
      --cnn_scoring rescore \
      -o rescored.sdf \
      --score_only

# Step 3: PoseBusters validation
bust rescored.sdf -p receptor.pdb --outfmt=csv > pb_results.csv
```

```python
import pandas as pd
pb_df = pd.read_csv('pb_results.csv')
bool_cols = pb_df.select_dtypes(include='bool').columns
pb_df['pb_valid'] = pb_df[bool_cols].all(axis=1)
valid_poses = pb_df[pb_df['pb_valid']]
```

## Boltz-2 for Affinity (Modern Alternative to FEP First-Pass)

Use the official Boltz input schema and `boltz predict` CLI for the installed release; do not rely on an invented `Boltz2.from_pretrained()` Python interface. The Boltz-2 paper reports affinity accuracy approaching FEP on its evaluated benchmarks and at least a 1,000-fold speed advantage, but those results are benchmark-specific and do not establish a universal RMSE or correlation for arbitrary ChEMBL data.

**When to use Boltz-2:** Use `affinity_probability_binary` for hit-discovery triage and `affinity_pred_value` for comparing binders during hit-to-lead or lead optimization, following the official output semantics. Benchmark both heads on target-relevant controls, and reserve FEP or experiment for decisions that require higher confidence.

**When not to rely on Boltz-2 alone:** Novel chemotypes or modalities outside the demonstrated training/benchmark domain, or production decisions without target-relevant validation.

## AlphaFold3 Ligand Prediction

AlphaFold 3 supports ligand-aware complex prediction. It can be run with the official local code after obtaining model parameters, or through the public AlphaFold Server under its separate terms and limits.

```bash
# From the official alphafold3 checkout; request.json follows its input schema.
python run_alphafold.py \
    --json_path=request.json \
    --model_dir=/path/to/af3_models \
    --output_dir=af3_out
```

AlphaFold3 strengths:
- Supports complexes containing proteins, nucleic acids, ligands, ions, and modified residues under its documented input schema
- Multiple diffusion samples per seed (five by default in the official local implementation), with all samples retained and a top-ranked prediction copied to the job root
- Official local implementation and a public web server

AlphaFold3 limitations:
- Cannot dock without protein sequence (no template-based)
- Public-server features and throughput differ from local execution
- Local weights require an approved access request and substantial compute

## Chai-1 (Open Alternative to AlphaFold3)

Chai-1 (Chai Discovery 2024) provides open code and model weights for biomolecular complex prediction. Validate performance on target-relevant controls rather than assuming equivalence to another model.

```python
from pathlib import Path
from chai_lab.chai1 import run_inference

# Chai represents every entity, including a SMILES ligand, in the input FASTA.
fasta_file = Path('target.fasta')
fasta_file.write_text(
    '>protein|name=target\nMSEQUENCE...\n'
    '>ligand|name=ligand\nCC(=O)c1ccccc1\n'
)
result = run_inference(
    fasta_file=fasta_file,
    output_dir=Path('chai_out'),
    num_trunk_recycles=3,
    num_diffn_timesteps=200,
    seed=42,
    device='cuda:0',
    use_esm_embeddings=True,
)
```

Chai-1 advantages:
- Apache-2.0 code and model weights permit academic and commercial use
- Local execution avoids public-server rate limits
- Single-sequence mode (no MSA required, faster)

## ML Docking Failure Modes by Tool

### DiffDock-L -- PB-invalid poses

**Trigger:** Default DiffDock-L on any input.

**Mechanism:** Diffusion generates poses without physical-validity loss.

**Symptom:** Some poses fail PoseBusters through distorted geometry or van der Waals clashes even when model confidence is high.

**Fix:** Filter all output through PoseBusters; rerun with smaller diffusion temperature; use as pose sampler not final ranker.

### EquiBind -- implausible intermediate or output geometry

**Trigger:** EquiBind single-shot prediction.

**Mechanism:** EquiBind's uncorrected predicted point cloud is not guaranteed to satisfy local geometry. Its final ligand-fitting stage is designed to change rotatable-bond torsions while keeping local atomic structure, including bond lengths and adjacent bond angles, fixed.

**Symptom:** An uncorrected intermediate or a failed/misapplied post-processing workflow contains implausible local geometry.

**Fix:** Use the released ligand-fitting/post-processing path, then validate the resulting pose with PoseBusters. If additional relaxation is used, constrain it deliberately and recheck stereochemistry and local geometry.

### TANKBind -- vdW overlap with protein

**Trigger:** TANKBind on tight pocket.

**Mechanism:** Distance prediction not constrained to vdW exclusion.

**Symptom:** Ligand overlaps protein.

**Fix:** Constrained energy minimization with frozen protein.

### Boltz-2 affinity -- novel chemotype error

**Trigger:** PROTAC, macrocycle, peptide.

**Mechanism:** A novel scaffold may fall outside the model's demonstrated benchmark domain.

**Symptom:** Predicted affinity disagrees with FEP / experiment.

**Fix:** Use as triage; validate top 1% with FEP. Check applicability domain (Tanimoto to training).

### AlphaFold3 / Boltz-1 -- novel target

**Trigger:** Target protein with limited MSA evidence.

**Mechanism:** Foundation models depend on MSA / homologs for confidence.

**Symptom:** Low or inconsistent model confidence. For AlphaFold 3, ligand-atom pLDDT only measures ligand-to-polymer local-distance confidence; inspect the full ranking score and ligand-relevant chain/interface confidence rather than applying a universal pLDDT cutoff.

**Fix:** Use single-sequence mode (Chai-1); validate experimentally before downstream.

### Hybrid workflow -- pose / score mismatch

**Trigger:** DiffDock pose + Boltz-2 affinity disagree.

**Mechanism:** Pose-prediction model and affinity-prediction model trained differently.

**Symptom:** Top pose by DiffDock has low Boltz-2 affinity.

**Fix:** Retain DiffDock confidence, GNINA score, Boltz-2 affinity, and physical-validity results as separate columns; prioritize consensus and inspect disagreements. RMSD is available only when a reference pose exists.

## Reconciliation: ML vs Classical

| Scenario | Practical comparison |
|----------|----------------------|
| Self-dock with a known holo receptor | Compare redocking recovery, geometry, and runtime for classical and ML workflows |
| Cross-dock or uncertain receptor conformation | Compare ML sampling, ensemble docking, and classical controls on related complexes |
| Novel chemotype or target family | Treat all model scores as extrapolative until target-relevant controls are available |
| Ultralarge screening | Use a fast first stage and reserve expensive rescoring for a documented subset |
| Production validation | Preserve sampler confidence, independent scores, and physical-validity checks as separate evidence |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| DiffDock-L generates invalid poses | Default behavior | Filter via PoseBusters; expected |
| Boltz-1 prediction takes hours | CPU instead of GPU | Use a supported accelerator; for the current CLI check `--accelerator gpu` |
| AlphaFold Server job limit reached | Public-server limit | Use approved local AlphaFold 3 weights or an open local alternative such as Chai-1 |
| Chai-1 setup complex | Multi-dependency | Use Tamarind Bio web service |
| PoseBusters PB-invalid for known active | Edge case | Sometimes valid; manual review |
| GNINA rescore changes ranking | Different scoring | Preserve both rankings and inspect disagreements on validated controls |
| OOM on small molecule | Wrong batch size | Reduce batch_size=1 |
| Boltz-2 affinity all 0 | Input format wrong | Check SMILES validity; standardize first |

## References

- Corso et al., *ICLR* (2023) -- original DiffDock. https://arxiv.org/abs/2210.01776
- Corso et al., *ICLR* (2024) -- DiffDock-L. https://proceedings.iclr.cc/paper_files/paper/2024/file/db334db287337b2a365120b524300ef3-Paper-Conference.pdf
- Buttenschoen et al., *Chem. Sci.* 15:3130-3139 (2024) -- PoseBusters benchmark. https://doi.org/10.1039/D3SC04185A
- Wohlwend et al., bioRxiv (2024) -- Boltz-1. https://doi.org/10.1101/2024.11.19.624167
- Passaro et al., bioRxiv (2025) -- Boltz-2 with affinity module. https://doi.org/10.1101/2025.06.14.659707
- Boltz, official repository -- affinity-output semantics and current prediction interface. https://github.com/jwohlwend/boltz
- Chai Discovery, *Chai-1 Technical Report* (2024). https://doi.org/10.1101/2024.10.10.615955
- Chai Discovery, Chai-1 official repository -- code and model-weight licensing. https://github.com/chaidiscovery/chai-lab
- Abramson et al., *Nature* 630:493-500 (2024) -- AlphaFold 3. https://doi.org/10.1038/s41586-024-07487-w
- Google DeepMind, AlphaFold 3 official repository -- local code and model-parameter access. https://github.com/google-deepmind/alphafold3
- McNutt et al., *J. Cheminformatics* 13:43 (2021) -- GNINA 1.0. https://doi.org/10.1186/s13321-021-00522-2
- Stärk et al., *ICML* (2022) -- EquiBind. https://proceedings.mlr.press/v162/stark22b.html
- Lu et al., *NeurIPS* 35 (2022) -- TANKBind. https://proceedings.neurips.cc/paper_files/paper/2022/hash/2f89a23a19d1617e7fb16d4f7a049ce2-Abstract-Conference.html
- Qiao et al., *Nat. Mach. Intell.* 6:195-208 (2024) -- NeuralPLexer. https://doi.org/10.1038/s42256-024-00792-z

## Related Skills

- chemoinformatics/virtual-screening - Classical docking foundation
- chemoinformatics/pose-validation - PoseBusters QC (mandatory after ML docking)
- chemoinformatics/free-energy-calculations - Boltz-2 as FEP first-pass
- chemoinformatics/molecular-io - Format conversion for tool inputs
- chemoinformatics/conformer-generation - Pre-conformer for some ML tools
- chemoinformatics/admet-prediction - ADMET on ML-docked hits
- structural-biology/modern-structure-prediction - Protein structure prediction
- structural-biology/structure-io - PDB / mmCIF handling
<!-- END FILE: chemoinformatics/ml-docking-rescoring/SKILL.md -->

## 子目录：chemoinformatics/molecular-descriptors

<!-- BEGIN FILE: chemoinformatics/molecular-descriptors/SKILL.md -->
---
name: bio-molecular-descriptors
description: Calculates molecular fingerprints (ECFP/Morgan, FCFP, MACCS, RDKit, AtomPair, TopologicalTorsion, Avalon, MAP4, MHFP6) and physicochemical descriptors (Lipinski, QED, TPSA, Crippen LogP, 3D shape) with explicit choice tables, bit vs count semantics, and partial-charge model selection. Use when featurizing molecules for similarity, QSAR, virtual screening, or ML, or selecting the correct fingerprint for a chemotype-aware task.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, numpy 1.26+, pandas 2.2+, map4 1.1+ (MAP4), mhfp 1.9+. Use `mapchiral` separately when the stereochemistry-aware MAP4C fingerprint is intended.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Molecular Descriptors

Featurize molecules for similarity search, QSAR, virtual screening, or ML. Fingerprint performance is **dataset- and objective-dependent**: ECFP4 is a strong drug-like baseline, atom-pair and topological-torsion fingerprints expose longer-range topology, MAP4/MHFP6 target broader chemical-space searches, and 3D conformer-based descriptors are needed when shape and stereochemistry matter.

For canonicalization before featurization, see `chemoinformatics/molecular-standardization`. For 3D-only descriptors, see `chemoinformatics/conformer-generation`.

## Fingerprint Taxonomy

| Fingerprint | Type | Radius/Path | Bits | Use case | Fails when |
|-------------|------|-------------|------|----------|------------|
| Morgan (ECFP) | Circular | r=2 (ECFP4), r=3 (ECFP6) | 2048 typical | Drug-like similarity, ML default | Loses long-range topology; bit collisions at low nBits |
| FCFP | Functional Morgan | r=2 default | 2048 | Pharmacophore-aware similarity | Same caveats as ECFP; less specific |
| MACCS | Substructure key | 166 fixed bits | 167 | Quick fingerprint, drug-likeness | Too sparse for large diverse libraries |
| RDKit FP | Path/subgraph-based | paths and branched subgraphs up to 7 bonds by default | 2048 | RDKit-native ECFP alternative | Drug-like only; not optimal for scaffold hopping |
| AtomPair | Pair + topological distance | All atom pairs | 2048 | Long-range topological similarity | Slower than ECFP; harder to interpret |
| TopologicalTorsion | 4-atom torsion | All TT | 2048 | Path-pattern similarity | Like AP, slower than ECFP |
| Avalon | Substructure + atom pairs | Mixed | 512/1024 | Fast similarity | Less standard; older |
| MAP4 (MinHashed atom-pair) | MinHash atom-pair | r=1,2 | 1024/2048 | Biological + metabolite diversity | `map4` library required; slower hash |
| MHFP6 (MinHash) | MinHash ECFP-like | r=3 (diam 6) | 2048 | Large-library nearest-neighbor with a compatible MinHash/LSH index | Different distance semantics from folded-bit Tanimoto |
| Pharm2D | 2D pharmacophore | feature pairs/triplets | sparse | Pharmacophore search | Sparse, slower |

**Decision:** For drug-like similarity ranking, start with **ECFP4 2048 bit** because it is fast and well characterized. MHFP6 outperformed ECFP4 for analog recovery in the benchmark reported by Probst and Reymond (2018), making it a candidate for large, diverse libraries. For scaffold hopping, benchmark ECFP4, AtomPair, TopologicalTorsion, and pharmacophore fingerprints on target-relevant actives and decoys; published comparisons do not support a universal AtomPair advantage (Gardiner et al. 2011; Riniker & Landrum 2013).

## Bit vs Count Vectors

| Form | Use | Library impact |
|------|-----|----------------|
| Bit (0/1) | Tanimoto similarity, BulkTanimotoSimilarity, RDKit fingerprint folding | Standard for similarity |
| Count (integer) | Some ML methods, RF on counts, neural fingerprints | Loses bit-level fast operations; richer signal |
| Sparse (dict) | Direct chemical interpretation (which fragments at which atoms) | Use for SHAP / atomic attribution |

```python
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator

mol = Chem.MolFromSmiles('CCO')

morgan = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
ecfp4_bit = morgan.GetFingerprint(mol)
ecfp4_count = morgan.GetCountFingerprint(mol)
ecfp4_sparse = morgan.GetSparseCountFingerprint(mol)
```

## Morgan / ECFP Radius Math

ECFP-X notation: X is the **diameter** in bonds. RDKit's `radius` parameter is half of X.

| Notation | RDKit radius | Diameter | Captures |
|----------|--------------|----------|----------|
| ECFP0 | 0 | 0 | Atom identity only |
| ECFP2 | 1 | 2 | Atom + immediate neighbors |
| ECFP4 | 2 | 4 | Atom + 2-bond environment |
| ECFP6 | 3 | 6 | Atom + 3-bond environment |

**Trade-off:** Larger radius captures more specific local environments but increases collisions at fixed `nBits`. **ECFP4 2048** is a common baseline (Rogers & Hahn 2010; Wu et al. 2018). O'Boyle and Sayle (2016) showed that increasing folded-fingerprint length can improve virtual-screening performance, but they did not establish a universal 4096-bit setting or a 1-5% collision rate. Measure collision occupancy and model performance for the dataset; increase `nBits` or use an unhashed sparse representation when needed.

## FCFP vs ECFP

FCFP (Functional-Class) uses RDKit's Morgan feature invariants (donor, acceptor, aromatic, halogen, basic, and acidic) instead of atom identity. Hydrophobe is a family in `BaseFeatures.fdef`, but it is not one of the default Morgan feature-invariant classes. FCFP trades atom-specificity for functional-equivalence.

```python
ecfp_generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
feature_invariants = rdFingerprintGenerator.GetMorganFeatureAtomInvGen()
fcfp_generator = rdFingerprintGenerator.GetMorganGenerator(
    radius=2, fpSize=2048, atomInvariantsGenerator=feature_invariants)
ecfp4 = ecfp_generator.GetFingerprint(mol)
fcfp4 = fcfp_generator.GetFingerprint(mol)
```

**When to use FCFP4:** Scaffold-hopping campaigns, pharmacophore-driven similarity, cross-target activity prediction.

**When to use ECFP4:** Within-series QSAR, lead optimization, when chemotype identity matters.

## 3D Descriptors and Conformer Dependence

Conformer-dependent descriptors (asphericity, eccentricity, principal moments of inertia, RDF) require a generated 3D structure. A single conformer may be unrepresentative when the molecule is flexible; measure descriptor variation across a conformer ensemble when the downstream conclusion depends on 3D shape.

**Goal:** Compute 3D shape descriptors over a conformer ensemble rather than from a single (possibly unrepresentative) conformer.

**Approach:** Add explicit hydrogens, embed N conformers with ETKDGv3, MMFF-optimize them all, then evaluate the descriptor across each conformer for downstream averaging.

```python
from rdkit.Chem import AllChem, Descriptors3D

mol = Chem.MolFromSmiles('CCCCO')
mol = Chem.AddHs(mol)

params = AllChem.ETKDGv3()
params.randomSeed = 42
conf_ids = AllChem.EmbedMultipleConfs(mol, numConfs=20, params=params)
if not conf_ids:
    raise RuntimeError('ETKDGv3 failed to generate any conformers')
if not AllChem.MMFFHasAllMoleculeParams(mol):
    raise ValueError('MMFF94 parameters are unavailable for this molecule')
optimization_results = AllChem.MMFFOptimizeMoleculeConfs(mol)
if any(status != 0 for status, _ in optimization_results):
    raise RuntimeError('MMFF94 optimization did not converge for every conformer')

asphericities = [Descriptors3D.Asphericity(mol, confId=c) for c in conf_ids]
```

**Decision:** For QSAR / ML, choose and document the conformer count using a convergence check on representative molecules. Report the aggregation rule, such as a simple mean or a Boltzmann-weighted average, and the energy model used for any weights.

## Partial Charge Methods

| Method | Software | Cost | Accuracy | Use for |
|--------|----------|------|----------|---------|
| Gasteiger-Marsili | RDKit, Open Babel | Fast | Empirical, rough | Charge-aware preparation or models that explicitly require Gasteiger charges; Vina/Vinardo scoring itself does not require assigned atom charges |
| MMFF94 | RDKit | 0.1s/mol | Force-field consistent | MMFF energy, conformer ranking |
| AM1-BCC | antechamber (AmberTools) | ~10s/mol | Semi-empirical | MD setup, FEP, GAFF |
| RESP | psi4, Gaussian | minutes/mol | Restrained fit to a quantum-mechanical ESP; protocol-specific | Force-field workflows parameterized for that RESP protocol |
| OpenFF Recharge | openff-recharge | Workflow-dependent | Framework for generating/retrieving QC ESP data and fitting library charges, BCCs, RESP charges, or virtual sites | Developing or evaluating charge models; it is not one charge-assignment method |

```python
from rdkit.Chem import AllChem

AllChem.ComputeGasteigerCharges(mol)
for atom in mol.GetAtoms():
    print(atom.GetIdx(), atom.GetPropsAsDict().get('_GasteigerCharge', None))
```

**Critical:** Charge method must match downstream. Gasteiger charges in an AMBER MD run violate the assumptions of the protein force field.

## MAP4 and MHFP6 for Diverse Libraries

For libraries spanning drug-like molecules, natural products, peptides, and metabolites, compare ECFP4 with MAP4 or MHFP6 on task-relevant retrieval benchmarks. MAP4 and MHFP6 use MinHash with atom-pair or circular-substructure shingles, but no universal pairwise-similarity range establishes that ECFP4 is saturated for every mixed library.

```python
from mhfp.encoder import MHFPEncoder

encoder = MHFPEncoder(2048)
mhfp6 = encoder.encode_mol(mol, radius=3)
```

MHFP6 distance is Jaccard on MinHash, not standard Tanimoto. Use `MHFPEncoder.distance(fp1, fp2)`.

## Physicochemical Descriptors

| Descriptor | Source | Range | Drug-like cutoff |
|------------|--------|-------|-------------------|
| MolWt | RDKit `Descriptors.MolWt` | ~50-2000 Da | <=500 (Lipinski) |
| MolLogP (Crippen) | RDKit `Descriptors.MolLogP` | -5 to 8 | <=5 (Lipinski) |
| HBD | `Lipinski.NumHDonors` | 0-10 | <=5 (Lipinski) |
| HBA | `Lipinski.NumHAcceptors` | 0-15 | <=10 (Lipinski) |
| TPSA | `Descriptors.TPSA` (Ertl) | 0-200 A^2 | <=140 (Veber oral); <=90 (BBB+) |
| RotBonds | `Lipinski.NumRotatableBonds` | 0-15 | <=10 (Veber) |
| AromaticRings | `Lipinski.NumAromaticRings` | 0-6 | <=3-4 (Ritchie-Macdonald aromatic ring count) |
| HeavyAtoms | `Descriptors.HeavyAtomCount` | <=50 (lead-like) | |
| FractionCSP3 | `Descriptors.FractionCSP3` | 0-1 | Descriptive; higher sp3 character was associated with clinical progression by Lovering et al. (2009), without a universal cutoff |
| QED | `QED.qed` | 0-1 | Higher is more similar to the reference property distributions; a project may use >=0.5 as a triage heuristic |
| SAscore | `sascorer.calculateScore` (external) | 1-10 | Lower is easier by the model; project cutoffs such as <=4 or >6 require dataset calibration |

**Goal:** Compute a standard physicochemical descriptor panel for drug-likeness filtering and QSAR features.

**Approach:** Combine RDKit `Descriptors`, `Lipinski`, and `QED` calls into a single dict so the caller gets MW, LogP, HBD/HBA, TPSA, rotatable bonds, aromatic rings, fraction sp3, and QED in one pass.

```python
from rdkit.Chem import Descriptors, Lipinski, QED

def physchem(mol):
    return {
        'MolWt': Descriptors.MolWt(mol),
        'MolLogP': Descriptors.MolLogP(mol),
        'HBD': Lipinski.NumHDonors(mol),
        'HBA': Lipinski.NumHAcceptors(mol),
        'TPSA': Descriptors.TPSA(mol),
        'RotBonds': Lipinski.NumRotatableBonds(mol),
        'AromRings': Lipinski.NumAromaticRings(mol),
        'FractionCSP3': Descriptors.FractionCSP3(mol),
        'QED': QED.qed(mol),
    }
```

## Drug-Likeness Rule Sets

| Rule | Constraints | Source |
|------|-------------|--------|
| Lipinski Ro5 | MW<=500, LogP<=5, HBD<=5, HBA<=10 | Lipinski 1997 |
| Veber | RotBonds<=10, TPSA<=140 | Veber 2002 (oral) |
| Ghose | 160<=MW<=480, -0.4<=LogP<=5.6, 40<=MR<=130, 20<=atoms<=70 | Ghose 1999 |
| Egan | LogP<=5.88, TPSA<=131.6 | Egan 2000 |
| Muegge | 200<=MW<=600, -2<=LogP<=5, TPSA<=150, rings<=7, C>4, heteroatoms>1, RotBonds<=15, HBD<=5, HBA<=10 | Muegge 2001 |
| Lead-like | MW<=350, LogP<=3 | Teague 1999 |
| Fragment Ro3 | MW<=300, LogP<=3, HBD<=3, HBA<=3, RotBonds<=3, TPSA<=60 A^2 | Congreve 2003 |
| Pfizer CNS MPO | Six desirability functions: ClogP, ClogD, MW, TPSA, HBD, and pKa | Wager 2010 |

**Use case:** Treat Ro5 and Veber criteria as risk indicators rather than universal hard cutoffs. Doak et al. (2014) analyze orally bioavailable drugs and candidates beyond the Rule of 5, but do not support the claim that approximately 30% of marketed oral drugs violate at least one rule. For CNS prioritization, implement the six-property Wager MPO desirability score rather than replacing it with three hard thresholds.

## QED (Weighted Drug-Likeness)

QED (Bickerton 2012) is a single-number drug-likeness measure (0-1) combining 8 properties (MW, LogP, HBD, HBA, PSA, RotBonds, AromaticRings, structural alerts) via desirability functions.

**Caveat:** QED summarizes desirability functions derived from property distributions of marketed oral drugs; it is not a supervised predictor trained specifically on FDA-approved drugs. It can under-rank fragment-like or natural-product-like molecules, so do not use it as the sole filter for those libraries.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Fingerprint changes between runs | Random seed not set for canonicalization | RDKit Morgan is deterministic; check if input differs (stereo, charges) |
| MACCS bit count != 166 | RDKit MACCS returns 167 bits (bit 0 unused) | Slice `[1:]` if comparing to literature 166-bit |
| Crippen LogP differs from XLogP | Different model | Use `Descriptors.MolLogP` for Crippen; `XLogP3` requires external lib |
| 3D descriptor differs between calls | Different conformer | Set `confId=0` explicitly; or average over ensemble |
| QED returns nan | Charged species or non-standard atom | Standardize (uncharge) before QED |
| Count-vector similarity differs from bit-vector similarity | Count multiplicities change the generalized Tanimoto calculation | RDKit supports Tanimoto on sparse count vectors; record the vector type and do not compare its threshold directly with a folded-bit threshold |
| MolWt off by ~1 from PubChem | Implicit H counted differently | Use `Descriptors.ExactMolWt` for monoisotopic; PubChem reports average |

## References

- Rogers & Hahn, *J. Chem. Inf. Model.* 50:742-754 (2010) -- ECFP fingerprints. https://doi.org/10.1021/ci100050t
- Probst & Reymond, *J. Cheminformatics* 10:66 (2018) -- MHFP6 fingerprint. https://doi.org/10.1186/s13321-018-0321-8
- Capecchi et al., *J. Cheminformatics* 12:43 (2020) -- MAP4 fingerprint. https://doi.org/10.1186/s13321-020-00445-4
- MAP4, official package -- installation and current Python interface. https://pypi.org/project/map4/
- OpenFF Recharge, official documentation -- supported charge-model generation and fitting workflows. https://docs.openforcefield.org/projects/recharge/en/stable/
- AutoDock Vina, official documentation -- Vina/Vinardo charge semantics. https://autodock-vina.readthedocs.io/en/stable/
- Gardiner et al., *Future Med. Chem.* 3:405-414 (2011) -- scaffold-hopping fingerprint comparison. https://doi.org/10.4155/fmc.11.4
- Riniker & Landrum, *J. Cheminformatics* 5:26 (2013) -- fingerprint benchmarking. https://doi.org/10.1186/1758-2946-5-26
- O'Boyle & Sayle, *J. Cheminformatics* 8:36 (2016) -- fingerprint folding and virtual-screening performance. https://doi.org/10.1186/s13321-016-0148-0
- Wu et al., *Chem. Sci.* 9:513-530 (2018) -- MoleculeNet benchmarks. https://doi.org/10.1039/C7SC02664A
- Bickerton et al., *Nat. Chem.* 4:90-98 (2012) -- QED weighted drug-likeness. https://doi.org/10.1038/nchem.1243
- Lipinski et al., *Adv. Drug Deliv. Rev.* 23:3-25 (1997) -- Rule of 5. https://doi.org/10.1016/S0169-409X(96)00423-1
- Veber et al., *J. Med. Chem.* 45:2615-2623 (2002) -- oral bioavailability criteria. https://doi.org/10.1021/jm020017n
- Ghose et al., *J. Comb. Chem.* 1:55-68 (1999) -- physicochemical property ranges. https://doi.org/10.1021/cc9800071
- Egan et al., *J. Med. Chem.* 43:3867-3877 (2000) -- absorption model. https://doi.org/10.1021/jm000292e
- Muegge et al., *J. Med. Chem.* 44:1841-1846 (2001) -- drug-like property filters. https://doi.org/10.1021/jm015507e
- Teague et al., *Angew. Chem. Int. Ed.* 38:3743-3748 (1999) -- lead-like libraries. https://doi.org/10.1002/%28SICI%291521-3773%2819991216%2938%3A24%3C3743%3A%3AAID-ANIE3743%3E3.0.CO%3B2-U
- Congreve et al., *Drug Discov. Today* 8:876-877 (2003) -- Rule of 3. https://doi.org/10.1016/S1359-6446(03)02831-9
- Lovering et al., *J. Med. Chem.* 52:6752-6756 (2009) -- fraction sp3 and clinical progression. https://doi.org/10.1021/jm901241e
- Ritchie & Macdonald, *Drug Discov. Today* 14:1011-1020 (2009) -- aromatic ring count and developability. https://doi.org/10.1016/j.drudis.2009.07.014
- Ertl & Schuffenhauer, *J. Cheminformatics* 1:8 (2009) -- synthetic accessibility score. https://doi.org/10.1186/1758-2946-1-8
- Wager et al., *ACS Chem. Neurosci.* 1:435-449 (2010) -- CNS multiparameter optimization. https://doi.org/10.1021/cn100008c
- Doak et al., *Chem. Biol.* 21:1115-1142 (2014) -- orally bioavailable drugs beyond the Rule of 5. https://doi.org/10.1016/j.chembiol.2014.08.013

## Related Skills

- chemoinformatics/molecular-io - Parse molecules before featurization
- chemoinformatics/molecular-standardization - Canonicalize before fingerprinting
- chemoinformatics/conformer-generation - Generate 3D for conformer-dependent descriptors
- chemoinformatics/similarity-searching - Use fingerprints for similarity ranking
- chemoinformatics/qsar-modeling - ML using these descriptors as features
- chemoinformatics/admet-prediction - Filter by drug-likeness criteria
- machine-learning/biomarker-discovery - ML on molecular features
<!-- END FILE: chemoinformatics/molecular-descriptors/SKILL.md -->

## 子目录：chemoinformatics/molecular-io

<!-- BEGIN FILE: chemoinformatics/molecular-io/SKILL.md -->
---
name: bio-molecular-io
description: Reads, writes, and converts molecular file formats (SMILES, InChI, SDF V2000/V3000, MOL2, PDB, and BinaryCIF) using RDKit and Open Babel with rigorous handling of aromaticity perception, stereochemistry, implicit/explicit hydrogens, kekulization, and salt/fragment separation. Use when loading chemical libraries, debugging parse failures, or preparing molecules for downstream standardization, descriptor calculation, or docking.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, Open Babel 3.1.1+, ChEMBL structure_pipeline 1.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `obabel -V`; `obabel -L formats`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Molecular I/O

Parse, write, and convert molecular file formats. Most downstream errors trace back to silent I/O issues: incorrect aromaticity perception, lost stereochemistry, mishandled charges, dropped stereo bonds, or non-canonical tautomers. This skill enumerates each format's failure modes and prescribes the correct toolchain for each scenario.

For full standardization (canonicalization, salt stripping, tautomer enumeration) see `chemoinformatics/molecular-standardization`. For generating 3D conformers from parsed 2D molecules, see `chemoinformatics/conformer-generation`.

## Format Taxonomy

| Format | Dim | Stereo | Charges | Strength | Fails when |
|--------|-----|--------|---------|----------|------------|
| SMILES | 2D | Atom chirality `@/@@`; double-bond `/` and `\` | Atom-local formal charges | Compact, web-friendly, fast parse | Loses absolute coordinates; aromatic perception ambiguous across toolkits; tautomers not canonical |
| InChI | 2D | `/b`, `/t`, `/m`, `/s` stereo sublayers | `/q` charge and `/p` added/removed-proton sublayers; `/p` is not a pH model | Canonical by construction; cross-toolkit identity | Standard InChI normalizes mobile-H forms; limited organometallic stereo; large molecules may require special handling |
| SDF V2000 | 2D/3D | Wedge bonds | M CHG line | Industry default; metadata via tags | 999-atom limit; cannot encode multi-component reactions; query atoms ambiguous |
| SDF V3000 | 2D/3D | Wedge + stereo flag | Inline charge | No atom limit; query support; rich properties | Some software (legacy) cannot read; verbose |
| MOL2 (Tripos) | 3D | Common records rely on 3D coordinates and toolkit perception; no portable explicit stereo field | Per-atom partial | SYBYL atom types preserved for docking | Atom-type dialects diverge (SYBYL vs Corina); RDKit MOL2 parser brittle |
| PDB | 3D | None | None standard | Universal protein format | No bond orders; aromatic perception lost; ligand names truncated to 3 chars |
| PDBQT | 3D | None | Gasteiger / AD4 | AutoDock-ready; torsion tree encoded | Specific to docking; no aromaticity layer |
| BinaryCIF (MMTF retired) | 3D | Encoded | Encoded | BinaryCIF (`.bcif`) is the current compact structural format; RCSB stopped serving MMTF files on July 2, 2024 and recommends BinaryCIF (RCSB PDB 2024) | Not all toolkits parse; binary format |
| CDX/CDXML | 2D | Drawing | Drawing | ChemDraw native | Not a structural format; converts unreliably |
| InChIKey | Hash | Stereo layer | n/a | Database key, fast lookup | Collision probability depends on key block and collection size; cannot recover structure |

## Aromaticity Perception (most common silent error)

Different toolkits perceive aromaticity differently. The same SMILES round-tripped between toolkits may produce different canonical strings and different fingerprints.

| Model | Toolkit | Rule | Symptom of mismatch |
|-------|---------|------|---------------------|
| Daylight | OpenEye, Daylight | 4n+2 π on planar ring | Furan, thiophene aromatic |
| RDKit default | RDKit | Daylight-like with extensions for fused / N-containing | Compatible with Daylight for drug-like molecules |
| MDL | Available in several toolkits, including RDKit as `AROMATICITY_MDL` | Five-membered rings are not aromatic unless part of a fused aromatic system; only C/N and one-electron donors qualify; exocyclic double bonds exclude an atom | Five-membered heteroaromatics and exocyclic-bond systems may differ from the default RDKit model |
| OpenEye | OEAroModel | Several modes | Charged thiophene non-aromatic in MDL but aromatic in OpenEye |

**Fix:** Always re-canonicalize via the toolkit doing analysis. If aromaticity must be reassigned explicitly in RDKit, use a concrete model, for example `Chem.SetAromaticity(mol, Chem.AromaticityModel.AROMATICITY_RDKIT)`, after the molecule is in an appropriate sanitized or kekulized state.

## Stereochemistry Layers

Stereo loss is the second most common silent error. Each format encodes stereo differently:

- SMILES: `@/@@` for tetrahedral, `/` and `\` for cis/trans double bonds
- InChI: `/b` for double-bond stereo, `/t` for tetrahedral stereo, and `/m` plus `/s` for inversion/overall stereo type
- SDF: wedge/hash bond + parity 0/1/2; cis/trans encoded via bond direction
- MOL2: common Tripos records provide 3D coordinates but no portable wedge or explicit stereo field; verify toolkit perception by round trip

**Round-trip tests:** If `Chem.MolToSmiles(Chem.MolFromSmiles(smi), isomericSmiles=True)` does not preserve the represented stereochemistry, inspect whether the source contained stereo markers and whether any step called `Chem.RemoveStereochemistry()` or discarded stereochemical coordinates/bond directions. Sanitization alone does not intentionally remove valid stereochemistry. If `MolFromMolFile` returns a molecule missing wedge bonds, inspect the source's coordinates, bond directions, and parity encoding.

## Reading SMILES with Stereo Preservation

**Goal:** Parse SMILES while preserving stereo and aromatic-flag consistency.

**Approach:** Use `Chem.MolFromSmiles(smi)` with sanitization on, verify with round-trip canonicalization, and set explicit stereochemistry where the toolkit's perception missed it.

```python
from rdkit import Chem
from rdkit.Chem import AllChem

def parse_smiles_safe(smi):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None, 'parse_failure'
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    canon = Chem.MolToSmiles(mol)
    round_trip = Chem.MolFromSmiles(canon)
    if Chem.MolToSmiles(round_trip) != canon:
        return mol, 'round_trip_unstable'
    return mol, 'ok'
```

## Reading SDF with Property Carryover

**Goal:** Load a multi-record SDF preserving per-molecule properties (Name, ID, IC50, etc.) used by downstream filtering and ML labeling.

**Approach:** Iterate via `SDMolSupplier(removeHs=False, sanitize=True)`, filter `None` (parse failures), and capture properties via `mol.GetPropsAsDict()`.

```python
from rdkit import Chem

supplier = Chem.SDMolSupplier('library.sdf', removeHs=False, sanitize=True)
mols = []
fails = []
for i, mol in enumerate(supplier):
    if mol is None:
        fails.append(i)
        continue
    props = mol.GetPropsAsDict()
    mols.append((mol, props))
print(f'parsed: {len(mols)}; failed: {len(fails)}')
```

If a large fraction fails, try `sanitize=False` then `Chem.SanitizeMol(mol, catchErrors=True)` to identify per-step failures (kekulization, valence, aromaticity).

## Open Babel for MOL2 / PDBQT

RDKit's MOL2 parser is incomplete (SYBYL atom-type sets differ). Open Babel is more robust for MOL2 and PDBQT.

```python
from openbabel import pybel

mols = list(pybel.readfile('mol2', 'ligands.mol2'))
for mol in mols:
    smi = mol.write('smi').strip().split()[0]
    inchi = mol.write('inchi').strip()
```

For docking output PDBQT, use Open Babel rather than RDKit:
```python
import subprocess
subprocess.run(['obabel', 'docked.pdbqt', '-O', 'docked.sdf'], check=True)
```

## InChI for Canonical Identity

InChI is a standardized, canonical structure identifier designed for cross-database and cross-toolkit interoperability (Heller et al. 2015; O'Boyle 2012). Standard InChI normalizes many mobile-hydrogen tautomers and has limitations for some metal stereochemistry; non-standard options such as `/FixedH` can distinguish additional representations. InChIKey is a fixed-length hash, so use full InChI or standardized structures when a suspected collision must be resolved (InChI Trust technical FAQ).

```python
from rdkit.Chem.inchi import MolToInchi, MolToInchiKey, InchiToInchiKey

mol = Chem.MolFromSmiles('c1ccc2c(c1)cccc2')
inchi = MolToInchi(mol)
key = MolToInchiKey(mol)

inchi_fixedH, aux_info = Chem.MolToInchiAndAuxInfo(mol, options='/FixedH')
```

**Caveat:** Two molecules with identical std InChI may be different tautomers. Use `/FixedH` for tautomer-distinguishing InChI when needed.

## Per-Format Failure Modes

### SMILES -- ambiguous aromaticity

**Trigger:** Input from non-RDKit source (ChemAxon, OpenEye, Daylight) round-tripping into RDKit.

**Mechanism:** RDKit perceives aromaticity on input. Aromatic flags from origin toolkit are overwritten.

**Symptom:** Fingerprints differ between toolkits for "identical" molecules; database joins by canonical SMILES miss records.

**Fix:** Always re-canonicalize within the analysis toolkit. For cross-toolkit identity, use InChIKey not canonical SMILES.

### SDF V2000 -- atom count >999

**Trigger:** Large molecules (peptides, oligonucleotides, dendrimers).

**Mechanism:** V2000 header uses fixed 3-character atom count field.

**Symptom:** Truncated atom block; parse failure with cryptic error.

**Fix:** Switch to V3000. RDKit auto-detects V3000 on read; explicitly request it on the writer:

```python
writer = Chem.SDWriter('out.sdf')
writer.SetForceV3000(True)
writer.write(mol)
writer.close()
```

### SDF -- wedge bond orientation lost

**Trigger:** SDF written by tools that use parity flags only (older ISIS-Draw, some pipeline tools).

**Mechanism:** Parity alone is ambiguous without geometric coordinates; RDKit reads parity but cannot re-render wedges.

**Symptom:** Drawn molecule shows undefined stereo despite SDF carrying parity bits.

**Fix:** After read, `Chem.AssignStereochemistryFrom3D(mol)` if 3D coords present; otherwise stereo must be re-derived from SMILES with wedges.

### PDB ligand -- no bond orders

**Trigger:** Parsing ligand from PDB entry (e.g., extracting co-crystal ligand).

**Mechanism:** PDB stores only atoms + CONECT; bond orders inferred by RDKit's `AssignBondOrdersFromTemplate` which requires a template molecule.

**Symptom:** All bonds single; aromatic rings non-aromatic; valences wrong.

**Fix:** Use `AllChem.AssignBondOrdersFromTemplate(template, ligand)` where `template` is a SMILES-derived mol of the expected ligand structure. Or use the PDB Ligand Expo SDF.

### MOL2 -- SYBYL atom type dialect

**Trigger:** MOL2 produced by Corina, MOE, or Schrodinger.

**Mechanism:** SYBYL atom types are not perfectly standardized across vendors; RDKit's parser handles canonical SYBYL.

**Symptom:** Mol returns as `None` or with wrong atom types (`Cl` vs `Cl.O` peroxide-style).

**Fix:** Convert via Open Babel as intermediate: `obabel input.mol2 -O temp.sdf` then read SDF.

### Open Babel pybel -- import path

**Trigger:** Code written for Open Babel 2.x.

**Mechanism:** OB 3.x reorganized: `import pybel` no longer works.

**Symptom:** `ModuleNotFoundError: No module named 'pybel'`.

**Fix:** `from openbabel import pybel`.

## Charge Models on I/O

| Source | Charges in file | Use for |
|--------|-----------------|---------|
| Parsed SMILES | Atom-local formal charges; no partial-charge model | Storage, similarity, ML training |
| Parsed PDB | Atomic charges typically absent | Always re-assign for downstream |
| `obabel --partialcharge gasteiger` | Gasteiger-Marsili partial charges (empirical) | Workflows that explicitly require Gasteiger charges; Vina/Vinardo scoring itself does not require assigned atom charges |
| AM1-BCC (AmberTools antechamber) | Semi-empirical | MD, FEP setup |
| RESP (psi4, Gaussian) | Restrained fit to a quantum-mechanical ESP; protocol-specific | Force-field workflows parameterized for that RESP protocol |

The charge model **must** match the downstream method. Mixing AM1-BCC ligand charges with TIP3P water + AMBER protein is valid; Gasteiger charges are unsuitable for MD.

## Drawing for QC

Always draw a random subset of parsed molecules. Wrong stereo, missing rings, and broken aromaticity show immediately.

```python
from rdkit.Chem.Draw import rdMolDraw2D

def draw_grid(mols, fname, mols_per_row=5, sub_img_size=(250, 200)):
    from rdkit.Chem.Draw import MolsToGridImage
    img = MolsToGridImage(mols[:25], molsPerRow=mols_per_row, subImgSize=sub_img_size,
                          legends=[m.GetProp('_Name') if m.HasProp('_Name') else ''
                                   for m in mols[:25]])
    img.save(fname)
```

`MolsToGridImage` returns PIL image; for headless servers use `MolDraw2DCairo` directly.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Chem.MolFromSmiles` returns None | Invalid SMILES, bad parentheses, ring not closed | Try `sanitize=False`, inspect with `Chem.MolFromSmiles(smi, sanitize=False)` |
| Round-trip SMILES changes | Aromaticity perception drift | Always canonicalize within analysis toolkit |
| All bonds single in PDB ligand | PDB has no bond orders | `AllChem.AssignBondOrdersFromTemplate(template, mol)` |
| Stereo lost on SDF write | Stereo was absent, removed, or not represented by coordinates/bond directions | Verify assigned chiral tags and bond stereo before writing; preserve suitable 2D/3D coordinates and inspect the round trip |
| MOL2 parse returns None | RDKit MOL2 parser incomplete for vendor dialects | Convert via Open Babel intermediate |
| InChI differs for "same" molecule | Different tautomers, charges, or stereo | Use `/FixedH` to retain tautomer; compare without standardization |
| Fingerprints differ across toolkits | Aromaticity model difference | Use InChIKey for identity; re-canonicalize for similarity |

## References

- Heller et al., *J. Cheminformatics* 7:23 (2015) -- InChI design, layout, and algorithms; software version 1.04. https://doi.org/10.1186/s13321-015-0068-4
- O'Boyle, *J. Cheminformatics* 4:22 (2012) -- Universal SMILES representation based on InChI. https://doi.org/10.1186/1758-2946-4-22
- InChI Trust, "Technical FAQ" -- InChIKey layout and collision estimates. https://www.inchi-trust.org/technical-faq/
- Daylight Chemical Information Systems, SMILES theory -- atom-local formal-charge and stereochemical syntax. https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html
- RDKit Book, "Aromaticity" -- RDKit and MDL aromaticity-model rules. https://www.rdkit.org/docs/RDKit_Book.html#aromaticity
- RCSB PDB (2024), "Removal of MMTF files from RCSB PDB." https://www.rcsb.org/news/6661c73362451e4e35915f7b

## Related Skills

- chemoinformatics/molecular-standardization - Salt stripping, tautomer canonicalization, neutralization
- chemoinformatics/molecular-descriptors - Calculate fingerprints and properties from parsed molecules
- chemoinformatics/conformer-generation - Generate 3D coordinates from 2D inputs
- chemoinformatics/virtual-screening - Prepare ligands for docking
- structural-biology/structure-io - Protein structure handling (PDB, mmCIF)
<!-- END FILE: chemoinformatics/molecular-io/SKILL.md -->

## 子目录：chemoinformatics/molecular-standardization

<!-- BEGIN FILE: chemoinformatics/molecular-standardization/SKILL.md -->
---
name: bio-molecular-standardization
description: Standardizes molecular structures using the ChEMBL structure pipeline for normalization and parent selection plus RDKit rdMolStandardize for explicit custom steps such as tautomer canonicalization, salt/solvent stripping, charge handling, stereochemistry handling, mixture selection, and isotope normalization. Explicitly compares ChEMBL, canSARchem, RDKit, and PubChem standardization choices. Use when preparing libraries for QSAR training, joining datasets across sources, deduplicating compound collections, or building canonical compound registries.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+ and chembl_structure_pipeline 1.2+. MolVS 0.1.1 is a legacy package; use RDKit's maintained `rdMolStandardize` module for custom pipelines.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Molecular Standardization

Convert raw molecular structures into a consistent form for ML training data, deduplication, registry, and cross-database joining. Skipping standardization can create data leakage when alternate representations of one compound enter different splits, distort QSAR inputs, and cause database join misses. The ChEMBL structure pipeline (Bento et al. 2020) is built on RDKit and applies ChEMBL-specific normalization and parent-selection rules. canSARchem (Dolciami et al. 2022) adds canonical-tautomer selection before parent extraction. RDKit's maintained `rdMolStandardize` module provides primitives for building an explicit custom pipeline.

For format-level I/O and aromaticity perception, see `chemoinformatics/molecular-io`. For descriptor calculation after standardization, see `chemoinformatics/molecular-descriptors`.

## Standardization Pipeline Stages

| Stage | RDKit Tool | Operation | Common errors caught |
|-------|-----------|-----------|----------------------|
| 1. Sanitization | `Chem.SanitizeMol` | Kekulize, assign aromaticity, fix valences | Wrong valence on N/O |
| 2. Salt stripping | `rdMolStandardize.FragmentRemover` or `LargestFragmentChooser` | Remove counterions | Cl-, Na+, K+, OH- |
| 3. Mixture choice | `LargestFragmentChooser` | Pick parent fragment | Co-crystals, hydrates |
| 4. Charge neutralization | `Uncharger` | Neutralize while preserving net charge | Permanent charges preserved (quaternary N+) |
| 5. Tautomer canonicalization | `TautomerEnumerator.Canonicalize` | Pick canonical tautomer | Keto/enol; amide/imidate |
| 6. Stereo standardization | `Chem.AssignStereochemistry` | Consistent stereo descriptors | Lost wedges, ambiguous R/S |
| 7. Isotope normalization | Explicitly set selected atom isotope labels to 0 | Remove 13C, 2H labels | Tracer studies; preserve labels when scientifically meaningful |
| 8. Output canonicalization | `Chem.MolToSmiles(canonical=True)` | Canonical SMILES + InChIKey | Round-trip stability |

## Pipeline Reconciliation

| Pipeline | Origin | Tautomer canonicalization | Salt definition | Use case |
|----------|--------|---------------------------|-----------------|----------|
| ChEMBL pipeline | EBI ChEMBL | Not performed by `standardize_mol` or `get_parent_mol` | ChEMBL salt list (extensive) | ChEMBL-compatible registration |
| canSARchem | ICR Cancer Research UK | Canonical tautomer BEFORE parent extraction | Extended salt list | Cancer drug discovery |
| PubChem (OpenEye) | NIH NCBI | OpenEye QUACPAC tautomer | PubChem salt list | Bioassay data, large-scale |
| RDKit rdMolStandardize default | Greg Landrum | RDKit TautomerEnumerator | RDKit default | General purpose, open source |

**Key difference (canSARchem vs ChEMBL):**
- ChEMBL standardizes the representation and extracts a parent, but does not canonicalize tautomers.
- canSARchem canonicalizes the tautomer before parent extraction.

This difference matters when alternate tautomeric inputs must be registered as one parent. Do not describe ChEMBL output as tautomer-canonical unless an explicit tautomer step is added and documented.

## ChEMBL Structure Pipeline (Reference Implementation)

ChEMBL's standardization is the most widely-used reference. The Python package `chembl_structure_pipeline` exposes the validated pipeline.

**Goal:** Apply the industry-reference ChEMBL standardization pipeline to a SMILES.

**Approach:** Parse SMILES with RDKit, run `standardize_mol` (sanitize, normalize, and standardize charges), then `get_parent_mol` (strip salts/counter-ions), and emit canonical SMILES. Add `rdMolStandardize.TautomerEnumerator` separately only when the project requires tautomer canonicalization.

```python
from chembl_structure_pipeline import standardize_mol, get_parent_mol
from rdkit import Chem

def chembl_pipeline(smi):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None, 'parse_failure'
    standardized = standardize_mol(mol)
    parent, exclude = get_parent_mol(standardized)
    if exclude:
        return None, 'excluded_by_chembl'
    return Chem.MolToSmiles(parent), 'ok'
```

**`standardize_mol`:** sanitize, normalize functional groups, and standardize charges; returns one RDKit molecule.

**`get_parent_mol`:** strip salts/counter-ions and choose the parent; returns `(parent_mol, exclude_flag)`.

Output: canonical SMILES of the selected parent after the ChEMBL transformations, or an explicit `excluded_by_chembl` status when the parent carries ChEMBL's exclusion flag. Neutralizable acid/base sites may be normalized, but permanent or otherwise non-removable charges can remain; do not assume every emitted parent is neutral.

## Full Standardization with rdMolStandardize

For more granular control or non-ChEMBL workflows.

**Goal:** Execute each standardization step explicitly to control salt stripping, charge handling, tautomer canonicalization, and isotope normalization.

**Approach:** Run the 8-stage pipeline (sanitize, largest fragment, normalize, uncharge, tautomer canonicalize, isotope strip, stereo standardize, canonical SMILES) sequentially with `rdMolStandardize` primitives.

```python
from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize

def full_standardize(smi, keep_isotopes=False):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None

    Chem.SanitizeMol(mol)

    largest = rdMolStandardize.LargestFragmentChooser(preferOrganic=True)
    mol = largest.choose(mol)

    normalizer = rdMolStandardize.Normalizer()
    mol = normalizer.normalize(mol)

    uncharger = rdMolStandardize.Uncharger(canonicalOrder=True)
    mol = uncharger.uncharge(mol)

    enumerator = rdMolStandardize.TautomerEnumerator()
    mol = enumerator.Canonicalize(mol)

    if not keep_isotopes:
        for atom in mol.GetAtoms():
            atom.SetIsotope(0)

    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    return Chem.MolToSmiles(mol)
```

**`canonicalOrder=True`** makes the uncharger choose neutralization sites in canonical order when more than one equivalent site is available. It does not itself decide whether a permanent charge is retained; inspect charge-sensitive structures and keep `force=False` unless a documented policy requires otherwise.

## Salt Stripping Edge Cases

| Salt form | Action | Example |
|-----------|--------|---------|
| Mono-salt | Strip counter-ion | `[Na+].CC(=O)[O-]` -> `CC(=O)O` |
| Di-salt | Strip both | `[Na+].[Na+].CC(=O)[O-].CC(=O)[O-]` -> `CC(=O)O` |
| Mixed salt | Largest organic fragment | `CCO.CC(=O)O` -> `CCO` (or CC(=O)O depending on rule) |
| Co-crystal | Hardest case | `CC(=O)O.CCOC(C)=O` -- both organic; default returns largest |
| Hydrate | Strip waters | `CC(=O)O.O` -> `CC(=O)O` |
| Solvate | Strip solvents | `CC(=O)O.CO` -> `CC(=O)O` |
| Quaternary ammonium | Preserve charge | `[N+](C)(C)(C)C` (permanent charge; do NOT neutralize) |

**`LargestFragmentChooser(preferOrganic=True)`** prefers organic fragments over inorganic counter-ions even if smaller; for co-crystals, default rule picks largest organic fragment.

## Tautomer Canonicalization (debated)

Tautomer canonicalization is the most controversial standardization step. There is no universally-correct canonical tautomer for many drug-like molecules.

| Tautomer pair | Why the policy matters |
|---------------|------------------------|
| Keto/enol | Canonicalization can select a representation different from the experimentally relevant bound or solution form |
| Lactam/lactim | Heterocycle scoring rules and toolkit versions may choose different representatives |
| Amidine/iminol | Proton placement changes donor/acceptor annotations and downstream matching |
| Phenol/keto (e.g., naphthol/naphthalenone) | Aromaticity and functional-group perception can change with the selected representation |
| 2H-pyrazole / 1H-pyrazole | Nitrogen identity and donor/acceptor assignments depend on proton placement |

Treat the enumerator's canonical result as a reproducible representation chosen by its configured scoring rules, not as a prediction of the dominant tautomer in vivo. Record the RDKit version and any custom transforms or scoring changes.

**Practical rules:**
- Always apply consistent canonicalization across train + test for ML
- For prospective prediction, predict for both tautomers if disagreement could matter
- For library deduplication, canonical tautomer is the standard answer
- For docking, use an ionization-aware preparation workflow. For Open Babel, the documented CLI is `obabel input.sdf -O output.sdf -p 7.4`; validate generated states because its rule-based protonation is not a substitute for project-specific pKa analysis.

```python
from rdkit.Chem.MolStandardize import rdMolStandardize

def canonical_tautomer(smi):
    mol = Chem.MolFromSmiles(smi)
    enumerator = rdMolStandardize.TautomerEnumerator()
    canon = enumerator.Canonicalize(mol)
    return Chem.MolToSmiles(canon)
```

## Stereochemistry Standardization

```python
from rdkit import Chem

def standardize_stereo(mol, remove_undefined=False):
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    if remove_undefined:
        Chem.RemoveStereochemistry(mol)
    return mol
```

**Cases:**
- Explicit stereo with `@` / `\` / `/` -> preserved
- Wedge bonds in SDF -> re-perceived from 3D coords if present
- Ambiguous stereo (no markers) -> left as-is, marked as undefined
- Racemic (explicit "rac") -> keep as racemate

For ML, remove stereochemistry only when the endpoint, data curation, and model representation justify treating stereoisomers as equivalent; record that policy and test its effect. For docking and FEP, preserve the intended stereoisomer and reject unintended stereo changes.

## Standardization for ML Training (avoiding data leakage)

**Goal:** Build a standardized + deduplicated training set with replicate-averaged activity for QSAR or ADMET model training.

**Approach:** Standardize every SMILES through the ChEMBL pipeline, compute InChIKey as canonical identity, group by InChIKey, and mean-aggregate activities; report replicate count for confidence weighting.

```python
import pandas as pd
from chembl_structure_pipeline import standardize_mol, get_parent_mol

def prepare_qsar_data(df, smiles_col='smiles', activity_col='pIC50'):
    standardized = []
    for i, row in df.iterrows():
        mol = Chem.MolFromSmiles(row[smiles_col])
        if mol is None:
            continue
        try:
            mol = standardize_mol(mol)
            mol, exclude = get_parent_mol(mol)
            if exclude:
                continue
            standardized.append({
                'smiles': Chem.MolToSmiles(mol),
                'inchikey': Chem.MolToInchiKey(mol),
                'activity': row[activity_col],
            })
        except Exception:
            continue

    df_std = pd.DataFrame(standardized)
    if df_std.empty:
        return pd.DataFrame(columns=['inchikey', 'smiles', 'activity', 'n_replicates'])
    df_std = df_std.groupby('inchikey').agg(
        smiles=('smiles', 'first'),
        activity=('activity', 'mean'),
        n_replicates=('activity', 'count'),
    ).reset_index()
    return df_std
```

Standard InChIKey may collapse some mobile-hydrogen tautomer representations, but this is not a substitute for an explicitly chosen tautomer policy. Replicate count signals measurement reliability.

## Per-Tool Failure Modes

### ChEMBL pipeline -- inorganic salt fails

**Trigger:** Molecule is genuinely an inorganic salt (e.g., NaCl, K2SO4).

**Mechanism:** `get_parent_mol` chooses largest organic; falls back to largest fragment for fully inorganic.

**Symptom:** Returns the salt itself (not a drug).

**Fix:** Pre-filter to compounds with ≥1 carbon atom.

### Uncharger -- charge-state policy mismatch

**Trigger:** A molecule combines a non-removable charge, such as quaternary ammonium, with other neutralizable sites, or the desired physiological ionization state differs from a structure-normalization rule.

**Mechanism:** `Uncharger` adds or removes hydrogens from neutralizable acids and bases. It cannot remove a permanent charge that has no corresponding hydrogen edit; by default it may preserve an opposite neutralizable charge when a non-removable charge is present so that the total charge remains balanced. `force=True` instead neutralizes all sites that can be neutralized even if the remaining permanent charge leaves a nonzero total charge.

**Symptom:** The permanent charge remains, but other sites or the total charge differ from the protonation state intended for docking or modeling.

**Fix:** Choose `force` according to the documented total-charge policy, keep `force=False` when balanced countercharges should be preserved, and inspect/prepare physiological protonation states separately.

### Tautomer enumerator -- combinatorial explosion

**Trigger:** Molecule with many tautomerizable groups (polyhydroxylated heterocycle).

**Mechanism:** `TautomerEnumerator.Enumerate` generates all possible tautomers; can produce thousands.

**Symptom:** OOM or hour-long compute on single molecule.

**Fix:** Use `Canonicalize` when only the configured canonical representation is needed. Before `Enumerate`, call `enumerator.SetMaxTransforms(limit)` (and, when appropriate, `SetMaxTautomers(limit)`) to cap the search.

### Legacy MolVS -- import or compatibility failure

**Trigger:** Code still using legacy `from molvs import Standardizer`.

**Mechanism:** The standalone MolVS package is legacy and may not support current Python/RDKit versions. RDKit's maintained `rdMolStandardize` module remains available.

**Symptom:** ImportError or AttributeError on newer RDKit.

**Fix:** Migrate deliberately to `from rdkit.Chem.MolStandardize import rdMolStandardize`; compare outputs because RDKit functions are not drop-in aliases for every MolVS workflow.

### Round-trip InChIKey mismatch

**Trigger:** Records were processed with different standardization settings or entered in different salt, charge, isotope, stereo, or tautomer forms.

**Mechanism:** The pipelines did not apply the same explicitly versioned transformations before identity generation.

**Symptom:** Apparently equivalent records produce different InChIKeys, or an expected database join fails.

**Fix:** Record and apply the same toolkit version, standardization stages, tautomer policy, and InChI options to both datasets; compare full standardized structures when results still differ.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| ImportError from standalone `molvs` | Legacy package incompatible with current environment | Use maintained `rdkit.Chem.MolStandardize.rdMolStandardize` APIs and validate output |
| `standardize_mol` raises or input parsing returns `None` | Invalid or unsanitizable input | Capture the exception/input index and inspect sanitization deliberately; do not silently accept a partially sanitized structure |
| Stripped wrong fragment | LargestFragmentChooser ambiguity | Manually inspect; consider custom logic |
| Tautomer differs between datasets | Different tautomer rules or toolkit versions | Pin and record the same `TautomerEnumerator` settings and version |
| Unexpected charge distribution with permanent ions | `Uncharger` total-charge policy does not match the intended protonation workflow | Review non-removable and neutralizable sites; choose `force` deliberately and prepare physiological states separately |
| Same InChIKey for apparently different records | Standard-InChI normalization or a rare hash collision | Compare full InChI and standardized structures; InChIKey has no longer form |
| Pipeline slow on large library | Per-molecule Python overhead | Process independent molecules in validated chunks or worker processes; `chembl_structure_pipeline` itself is a per-molecule API |

## References

- Bento et al., *J. Cheminformatics* 12:51 (2020) -- ChEMBL structure pipeline. https://doi.org/10.1186/s13321-020-00456-1
- Dolciami et al., *J. Cheminformatics* 14:28 (2022) -- canSARchem registration pipeline. https://doi.org/10.1186/s13321-022-00606-7
- Hähnke et al., *J. Cheminformatics* 10:36 (2018) -- PubChem standardization. https://doi.org/10.1186/s13321-018-0293-8
- RDKit, `rdkit.Chem.MolStandardize.rdMolStandardize` API documentation. https://www.rdkit.org/docs/source/rdkit.Chem.MolStandardize.rdMolStandardize.html
- Open Babel, official `obabel` documentation -- pH-dependent hydrogen-addition CLI. https://openbabel.org/docs/Command-line_tools/babel.html

## Related Skills

- chemoinformatics/molecular-io - Parse molecules before standardizing
- chemoinformatics/molecular-descriptors - Apply descriptors to standardized molecules
- chemoinformatics/similarity-searching - Standardize before comparing
- chemoinformatics/substructure-search - Standardize before SMARTS matching
- chemoinformatics/qsar-modeling - Mandatory upstream for QSAR
<!-- END FILE: chemoinformatics/molecular-standardization/SKILL.md -->

## 子目录：chemoinformatics/pharmacophore-modeling

<!-- BEGIN FILE: chemoinformatics/pharmacophore-modeling/SKILL.md -->
---
name: bio-pharmacophore-modeling
description: Builds and applies 3D pharmacophore models using RDKit Pharm3D, the apo2ph4 receptor-based workflow (Heider et al. 2023), Pharmer / Pharmit for search, and PharmacoForge for protein-pocket-conditioned pharmacophore generation (Flynn et al. 2025), covering ligand-based pharmacophores from active-set alignment and receptor-based pharmacophores from binding-pocket geometry. Explicitly handles feature types, geometric tolerances, partial matching, and pharmacophore-based virtual screening. Use when identifying scaffold-hopping candidates, building shape-and-feature search queries, or transferring SAR across chemotypes.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, Pharmit web service, and PLIP 2.4+ (interaction analysis). Verify the deployed Pharmit/Pharmer interface and query format before automation.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show rdkit` then `help(rdkit.Chem.Pharm3D)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Pharmacophore Modeling

Build 3D pharmacophore queries that capture the essential interaction features of a ligand-target binding event. A pharmacophore is the *spatial arrangement of pharmacophore features* (donor, acceptor, hydrophobe, aromatic, charged) sufficient for activity, abstracted from any specific chemotype. Use pharmacophores for scaffold hopping, virtual-screening prefilters, and cross-target SAR transfer. Derive interaction features directly from a co-crystal when available, use apo2ph4 to derive models from an apo pocket (Heider et al. 2023), or align known actives for a ligand-based model. PharmacoForge generates candidate 3D pharmacophores conditioned on a protein pocket; those pharmacophores can then retrieve matching molecules from a library (Flynn et al. 2025).

For 2D scaffold-based searches, see `chemoinformatics/scaffold-analysis`. For 3D shape similarity, see `chemoinformatics/shape-similarity`. For protein-ligand interaction analysis, see `chemoinformatics/virtual-screening`.

## Pharmacophore Feature Types

| Feature | Common shorthand | Definition | Geometric tolerance |
|---------|------------|------------|----------------------|
| H-bond donor | D | -OH, -NH | 1.0-1.5 Å |
| H-bond acceptor | A | sp2 O / N (lone pair) | 1.0-1.5 Å |
| Hydrophobe | H | sp3 C / aromatic ring centroid | 1.5-2.0 Å |
| Aromatic ring | R | Aromatic ring centroid + normal | 1.0-1.5 Å |
| Positive ionizable | P | -NH3+, -NR3+ | 1.0-1.5 Å |
| Negative ionizable | N | -COO-, -SO3- | 1.0-1.5 Å |
| Halogen | X | Cl, Br, I (halogen bond donor) | 1.0-1.5 Å |
| Metal coordination | M | sp/sp2 N/O near metal | 0.5-1.0 Å |

Tolerances are pharmacophore-feature distance windows in the search. Tighter tolerances = fewer hits but more specific.

The ranges in this table are repository starting heuristics, not universal feature tolerances. Set final bounds from aligned-feature variability, coordinate uncertainty, and retrospective validation for the selected search engine.

The one-letter labels above are human-readable shorthand, not RDKit API codes. RDKit's shipped `BaseFeatures.fdef` uses family names such as `Donor`, `Acceptor`, `Hydrophobe`, `Aromatic`, `PosIonizable`, and `NegIonizable`. Its default feature definitions do not provide every halogen-bond or metal-coordination model; add and validate project-specific feature definitions when those interactions matter.

## Method Taxonomy

| Method | Origin | Use case | Fails when |
|--------|--------|----------|------------|
| Ligand-based (LBP) | Catalyst, MOE, RDKit Pharm3D | Multiple actives, no crystal | <3 actives; flexible actives |
| Receptor-based (RBP) | apo2ph4, LigandScout, PLIP | Co-crystal or a defined apo pocket | Uncertain pocket conformation |
| Common pharmacophore | Validated alignment/feature-consensus workflow; RDKit can represent and query the resulting model | Consensus from active set | Diverse actives or uncertain bioactive conformers confound alignment |
| Pocket-conditioned generation (PharmacoForge) | Flynn et al. 2025 | Generate candidate pharmacophores from a protein pocket | Does not directly generate molecules; pretrained model required |
| Active learning pharmacophore | Catalyst variant | Iterative refinement | Custom; not standard |

## Decision Tree by Scenario

| Scenario | Method | Tools |
|----------|--------|-------|
| Co-crystal structure available | Interaction-derived receptor model | PLIP or LigandScout + Pharmit |
| Apo structure with a defined pocket | Apo receptor model | apo2ph4; export LigandScout PML |
| Multiple active compounds, no crystal | Ligand-based common pharmacophore | Alignment plus consensus-feature derivation in validated custom or external tooling; RDKit Pharm3D can apply the resulting model |
| Single active compound | Single-conformer pharmacophore | RDKit Pharm3D from bioactive conformer |
| Scaffold hopping prospective | Receptor-based + shape filter | apo2ph4 or interaction-derived model + shape search |
| Cross-target SAR transfer | Common pharmacophore across targets | Manual + LigandScout |
| Generate pocket-conditioned pharmacophores | PharmacoForge | Diffusion model followed by library retrieval |
| Library pre-filtering | Pharmacophore screen | Pharmit search |

## Ligand-Based Pharmacophore (RDKit Pharm3D)

**Goal:** Derive a common pharmacophore from aligned bioactive conformers, then apply that established model to candidate molecules.

**Approach:** Consensus derivation is a separate modeling step: select or generate plausible bioactive conformers, align them using a documented method, identify conserved feature correspondences, and estimate distance bounds or tolerances. RDKit does not provide a single `EmbedPharmacophore` call that performs those steps. `EmbedPharmacophore` instead generates conformations of a molecule that satisfy an already defined pharmacophore.

```python
from rdkit import Chem, Geometry
from rdkit.Chem import ChemicalFeatures
from rdkit.Chem.Pharm3D import EmbedLib, Pharmacophore
from rdkit.RDPaths import RDDataDir
import os

fdef_file = os.path.join(RDDataDir, 'BaseFeatures.fdef')
factory = ChemicalFeatures.BuildFeatureFactory(fdef_file)

# This is an already defined model. Coordinates and bounds must come from a
# validated consensus-derivation workflow or another justified source. RDKit
# requires FreeChemicalFeature objects, not feature-family strings.
query_features = [
    ChemicalFeatures.FreeChemicalFeature(
        'Aromatic', Geometry.Point3D(0.0, 0.0, 0.0)),
    ChemicalFeatures.FreeChemicalFeature(
        'Donor', Geometry.Point3D(4.0, 0.0, 0.0)),
]
pharmacophore = Pharmacophore.Pharmacophore(query_features)
pharmacophore.setLowerBound(0, 1, 3.5)
pharmacophore.setUpperBound(0, 1, 5.0)

target = Chem.AddHs(Chem.MolFromSmiles('c1ccc(cc1)CCN'))
can_match, feature_matches = EmbedLib.MatchPharmacophoreToMol(
    target, factory, pharmacophore)
if can_match:
    atom_match = tuple(tuple(matches[0].GetAtomIds())
                       for matches in feature_matches)
    _, embeddings, n_failed = EmbedLib.EmbedPharmacophore(
        target, atom_match, pharmacophore, randomSeed=23, silent=True)
```

`BaseFeatures.fdef` (RDKit-shipped) defines feature SMARTS and is a useful starting feature taxonomy. The code above demonstrates applying an existing two-feature model; it does not infer a consensus model from active compounds.

## Receptor-Based Pharmacophore (apo2ph4 workflow)

**Goal:** Derive a pharmacophore from a protein binding-pocket structure without requiring a bound ligand.

**Approach:** Identify donor, acceptor, and hydrophobic hot spots from apo-pocket geometry, cluster them, and assemble candidate pharmacophores. Heider et al. describe apo2ph4 in *J. Chem. Inf. Model.* 63:101-110 (2023). Use the source release's documented scripts and environment rather than assuming a packaged `apo2ph4` command: the published workflow writes LigandScout PML output, not a generic `.ph4` file. Treat conversion to Pharmit, Pharmer, MOE, or Phase as a separate, explicitly validated step because pharmacophore formats are not interchangeable.

When a co-crystal ligand is available, **derive pharmacophore directly from the ligand binding pose**: each ligand feature in contact with a complementary protein residue is part of the pharmacophore.

```python
from plip.basic import config
from plip.structure.preparation import PDBComplex

mol_complex = PDBComplex()
mol_complex.load_pdb('complex.pdb')
mol_complex.analyze()

for site in mol_complex.interaction_sets.values():
    for interaction in site.all_itypes:
        # Objects are interaction-class-specific. Inspect the documented fields
        # for HydrophobicContact, HydrogenBond, PiStacking, SaltBridge, etc.;
        # there is no universal `.type` or `.ligatom.coords` interface.
        interaction_class = type(interaction).__name__
        print(interaction_class, interaction)
```

PLIP exposes typed interaction records with class-specific ligand/protein atoms and coordinates. Map those records to pharmacophore features explicitly and retain the interaction class and source atom identifiers.

## Pharmacophore Search (Pharmit / Pharmer)

For library screening, configure feature types, centers, radii, and optional shape constraints in Pharmit, or use a Pharmer database and query produced in the format required by the installed release. Do not pass LigandScout PML or a vendor `.ph4` file directly unless the selected interface documents that import path. Pharmit reported searching millions of conformers in seconds to minutes; actual runtime depends on query selectivity, database size, and deployment (Sunseri & Koes 2016).

## Pharmacophore Quality Validation

Evaluate a pharmacophore by:

1. **Retrospective enrichment**: a stated metric on target-relevant actives and inactives/decoys. DUD-E can provide a benchmark with known decoy-construction biases; COCONUT is a natural-products collection, not a target-specific active/decoy benchmark.
2. **Geometric tightness**: feature distance variance across actives
3. **Selectivity**: false positives in inactive set should be low
4. **Specific consistency**: pharmacophore matches each active's bioactive conformer

```python
def pharmacophore_enrichment(query_pharmacophore, actives, inactives,
                             matches_pharmacophore):
    """Return active/inactive match-rate enrichment for a supplied matcher."""
    if not actives or not inactives:
        raise ValueError('actives and inactives must both be non-empty')
    n_active_match = sum(
        bool(matches_pharmacophore(mol, query_pharmacophore))
        for mol in actives)
    n_inactive_match = sum(
        bool(matches_pharmacophore(mol, query_pharmacophore))
        for mol in inactives)
    active_rate = n_active_match / len(actives)
    inactive_rate = n_inactive_match / len(inactives)
    return float('inf') if inactive_rate == 0 else active_rate / inactive_rate
```

For this repository, enrichment >=5x may be used as a starting triage heuristic only after the active/decoy construction and matching policy are documented. Report the full metric and uncertainty, and calibrate the acceptance threshold on the project dataset.

## Pocket-Conditioned Pharmacophore Generation (PharmacoForge)

PharmacoForge (Flynn et al. 2025) applies a diffusion model to a protein pocket and generates candidate 3D pharmacophores. It does **not** directly generate molecular structures from an input pharmacophore. The validated workflow is:

1. Prepare the protein pocket in the representation required by the published PharmacoForge release.
2. Sample and rank pocket-conditioned pharmacophores.
3. Convert a selected pharmacophore into the query representation used by the search engine.
4. Retrieve matching, purchasable compounds and evaluate them with docking, strain, and physical-validity checks.

The paper compares pharmacophore and downstream retrieval performance with other pocket-based approaches; it does not support a drug-likeness or novelty comparison with REINVENT.

## Pharmacophore vs Shape vs 2D Fingerprint

| Method | Captures | Best for |
|--------|----------|----------|
| ECFP4 Tanimoto | Local atom environments | Lead optimization (same series) |
| FCFP4 Tanimoto | Pharmacophore-equivalent atoms | Loose similarity in series |
| Shape similarity (ROCS) | 3D shape volume | Scaffold hopping by shape |
| Pharmacophore | Discrete features in space | Scaffold hopping with feature specificity |
| Combined (Tanimoto + shape) | Multi-objective | Production VS |

Pharmacophore is more *interpretable* than shape: a hit explains why it matched (donor at position X, hydrophobe at position Y).

## Per-Tool Failure Modes

### Ligand-based -- diverse actives confound

**Trigger:** Active set spans multiple scaffolds with different bound conformations.

**Mechanism:** No common pharmacophore exists; algorithm forces non-consensus features.

**Symptom:** Pharmacophore matches no actives in retrospective.

**Fix:** Cluster actives by scaffold first; derive per-cluster pharmacophore.

### Receptor-based -- apo structure

**Trigger:** Protein in apo form (no bound ligand).

**Mechanism:** Side-chain rotamers differ between apo and holo; "binding site" geometry is wrong.

**Symptom:** Pharmacophore inferred from apo doesn't match holo experimental data.

**Fix:** Use AlphaFold3 / Boltz-1 to predict holo conformation; derive pharmacophore from predicted holo.

### Pharmacophore -- single conformer bias

**Trigger:** Active aligned to its first generated conformer, not bioactive conformer.

**Mechanism:** Crystal structure not available; generated conformer may not be the bound one.

**Symptom:** Pharmacophore inconsistent across runs (different starting conformer chosen).

**Fix:** Use conformer ensemble; align all to common scaffold; choose conformer most consistent with other actives.

### Tolerance too tight

**Trigger:** Default geometric tolerance < 0.5 Å.

**Mechanism:** Real bioactive conformers have flexibility; rigid pharmacophore filters most molecules out.

**Symptom:** Search returns zero hits.

**Fix:** Use tolerance 1.0-1.5 Å for drug-like; up to 2 Å for flexible peptide-like.

### Pharmacophore search misses bioisostere

**Trigger:** Bioisostere replacement (e.g., -COOH replaced by tetrazole).

**Mechanism:** Tetrazole functions as acid bioisostere but RDKit features may not classify identically.

**Symptom:** Known bioisosteric active not found.

**Fix:** Use ChemAxon-style bioisosteric feature equivalence; or pharmacophore feature class expansion (acid generic vs -COOH specific).

### PLIP -- water bridge absent from output

**Trigger:** Bridging water between ligand donor and protein acceptor.

**Mechanism:** PLIP can report water bridges, but the required crystallographic water must be present in the input and satisfy its geometric criteria.

**Symptom:** Pharmacophore missing critical H-bond feature.

**Fix:** Retain relevant crystallographic waters, inspect PLIP water-bridge output, and review borderline geometry manually.

## Reconciliation: Ligand-Based vs Receptor-Based

| Aspect | Ligand-based | Receptor-based |
|--------|--------------|----------------|
| Data needed | Multiple actives with defensible conformers/alignment | A defined pocket, optionally with a co-crystal ligand |
| Main bias | Known active chemotypes, conformer choice, and alignment | Pocket structure, protonation, retained waters, and interaction-detection/modeling rules |
| Hit-set behavior | Depends on feature abstraction and tolerances | Depends on selected pocket interactions, excluded volumes, and tolerances |
| Confidence evidence | Retrospective recovery across held-out actives/inactives | Recovery of known interaction geometry and retrospective or prospective validation |

Choose between ligand- and receptor-based models using the available structural/activity evidence and target-relevant validation. Neither approach is universally more reliable, diverse, or suitable for scaffold hopping.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Pharm3D.EmbedPharmacophore` fails | Bounds matrix infeasible | Review/loosen justified bounds and, when more attempts are warranted, increase the documented `count` argument; inspect `n_failed` |
| Pharmacophore matches everything | Too few features | Add features; tighten tolerances |
| Pharmacophore matches nothing | Too many features or tight bounds | Reduce feature count; loosen tolerances |
| BaseFeatures.fdef not found | RDKit installation issue | Check `from rdkit.RDPaths import RDDataDir` |
| Pharmacophore-conformer mismatch | Wrong conformer used | Use bioactive conformer from crystal |
| Pharmit search timeout | Library too large | Pre-filter by 2D fingerprint Tanimoto |
| apo2ph4 PML has no useful model | No robust pocket hot spots at selected settings | Recheck pocket definition and documented thresholds; inspect alternative models |

## References

- Wolber & Langer, *J. Chem. Inf. Model.* 45:160-169 (2005) -- LigandScout pharmacophores. https://doi.org/10.1021/ci049885e
- Heider et al., *J. Chem. Inf. Model.* 63:101-110 (2023; published online 2022) -- apo2ph4. https://doi.org/10.1021/acs.jcim.2c00814
- Flynn EL, Shah R, Dunn I, Aggarwal R, Koes DR, *Front. Bioinform.* 5:1628800 (2025) -- PharmacoForge. https://doi.org/10.3389/fbinf.2025.1628800
- RDKit, `Chem.Pharm3D` API documentation. https://www.rdkit.org/docs/source/rdkit.Chem.Pharm3D.html
- RDKit, `EmbedPharmacophore` API documentation -- embedding molecules against an existing pharmacophore. https://www.rdkit.org/docs/source/rdkit.Chem.Pharm3D.EmbedLib.html#rdkit.Chem.Pharm3D.EmbedLib.EmbedPharmacophore
- COCONUT, official resource -- open natural-products collection. https://coconut.naturalproducts.net/
- Adasme et al., *Nucleic Acids Res.* 49:W530-W534 (2021) -- PLIP interaction profiler. https://doi.org/10.1093/nar/gkab294
- Sunseri & Koes, *Nucleic Acids Res.* 44:W442-W448 (2016) -- Pharmit interactive search. https://doi.org/10.1093/nar/gkw287

## Related Skills

- chemoinformatics/molecular-io - Parse molecules
- chemoinformatics/conformer-generation - Generate 3D for pharmacophore
- chemoinformatics/shape-similarity - 3D shape adjacent to pharmacophore
- chemoinformatics/virtual-screening - Pharmacophore as docking pre-filter
- chemoinformatics/scaffold-analysis - 2D scaffold-hopping context
- chemoinformatics/generative-design - Generate or optimize molecules after pharmacophore-based retrieval
- structural-biology/structure-io - PDB handling
<!-- END FILE: chemoinformatics/pharmacophore-modeling/SKILL.md -->

## 子目录：chemoinformatics/pose-validation

<!-- BEGIN FILE: chemoinformatics/pose-validation/SKILL.md -->
---
name: bio-pose-validation
description: Validates docked / generated protein-ligand poses using PoseBusters physical-validity tests, strain energy quantification, geometric checks (planarity, vdW overlap, bond/angle distortion), and pose-energy reasonableness. Use when QC-ing docking results, comparing classical vs ML docking outputs, or filtering pose lists before SAR analysis.
tool_type: python
primary_tool: PoseBusters
---

## Version Compatibility

Reference examples tested with: PoseBusters 0.6+, RDKit 2024.09+, pandas 2.2+, posecheck 0.5+ (optional).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Pose Validation

Test docked or AI-generated protein-ligand poses for physical plausibility. PoseBusters (Buttenschoen et al. 2024) provides geometric, chemical, and energetic checks that flag implausible poses, including non-planar aromatic rings, van der Waals clashes, broken bonds, altered stereochemistry, and unfavorable internal energies. On the Astex Diverse Set, DiffDock achieved 72% RMSD success but only 47% combined RMSD-and-PB-valid success; the size of this gap is dataset- and method-dependent. PB-valid status complements RMSD for downstream SAR, FEP setup, or generative-model training.

For docking, see `chemoinformatics/virtual-screening`. For ML docking specifically, see `chemoinformatics/ml-docking-rescoring`.

## PoseBusters Test Suite

PoseBusters runs ~20 individual checks grouped into:

The thresholds below are the benchmark criteria reported by Buttenschoen et al. (2024). Installed PoseBusters defaults may differ by version and configuration, so record the package version and resolved configuration.

| Check group | What it tests | 2024 benchmark criterion |
|-------------|---------------|-----------|
| Sanity | Ligand chemical sanity | RDKit sanitization passes |
| Bond lengths | Bond lengths within reference | 0.75–1.25 times RDKit distance-geometry bounds |
| Bond angles | 1–3 distances within reference | 0.75–1.25 times RDKit distance-geometry bounds |
| Internal steric | No intra-ligand clash | Pair distance > 0.70 times the RDKit lower bound |
| Aromatic ring planarity | Aromatic rings planar | Maximum deviation from fitted plane <= 0.25 Å |
| Double-bond stereo | Z/E preserved | Match input SMILES |
| Internal energy | Energy relative to generated conformers | UFF energy ratio <= 100 versus the mean of 50 generated, relaxed conformers |
| Volume overlap | vdW overlap with protein | < 7.5% of ligand vdW volume |
| Minimum distance | No severe protein-ligand clash | Distance >= 0.75 times the sum of vdW radii |
| Chirality | R/S preserved from input | Match input SMILES |

A pose passing ALL tests is "PB-valid". Combined PB-valid + RMSD <= 2 Å is the modern criterion.

## When to Apply PoseBusters

| Workflow | PoseBusters use | Action |
|----------|-----------------|--------|
| Self-docking (validating method) | Required | Compare PB-valid + RMSD <= 2A |
| Cross-docking | Required | PB-valid + RMSD <= 2A; account for protein flexibility |
| Virtual screening top hits | Required | Filter to PB-valid before MM/GBSA / FEP |
| AI docking (DiffDock, etc.) | Required for a fair benchmark | Report the dataset-specific PB-valid and combined success rates |
| Generated ligand poses | Recommended | Measure chemical and geometric validity rather than assuming it |
| Boltz-2 / AlphaFold3 ligand poses | Recommended | Benchmark validity on the relevant complexes; do not infer a failure frequency from DiffDock |
| Production FEP setup | Required | Inspect pose validity and ligand strain before system preparation |

## PoseBusters Usage

```python
from posebusters import PoseBusters

bust = PoseBusters(config='redock')

results = bust.bust(
    mol_pred='predicted.sdf',
    mol_true='reference.sdf',
    mol_cond='receptor.pdb',
)
```

Common configurations and their included checks are:

| Config | Includes | When to use |
|--------|----------|-------------|
| `redock` | All checks + RMSD vs reference + protein vdW overlap | Self-docking benchmarks, retrospective validation |
| `dock` | All checks except RMSD reference | Blind docking, prospective virtual screening |
| `mol` | Intra-ligand only (sanity, bonds, angles, rings, stereo, energy) | Conformer QC; no protein context |

PoseBusters also ships additional and faster configurations in some releases. Treat the table as a workflow guide, not an exhaustive registry, and inspect the configurations available in the installed version.

Output: a DataFrame with one row per pose, metadata columns, and boolean pass/fail columns for the checks enabled by the selected configuration. Reference-dependent fields such as RMSD and the exact check-column names vary by configuration and version; inspect `results.columns` rather than relying on a fixed exhaustive list.

## Python Library API

**Goal:** Programmatically validate a docked-pose SDF against a receptor PDB and produce a PB-valid filter.

**Approach:** Instantiate `PoseBusters(config='dock')`, call `bust()` on the SDF + PDB pair, and AND-aggregate all boolean check columns into a single `pb_valid` flag.

```python
from posebusters import PoseBusters
import pandas as pd

bust = PoseBusters(config='dock')

results = bust.bust(
    mol_pred='/path/to/docked_poses.sdf',
    mol_cond='/path/to/receptor.pdb',
)

check_cols = [
    col for col in results.select_dtypes(include='bool').columns
    if not col.lower().startswith('rmsd')
]
results['pb_valid'] = results[check_cols].all(axis=1)
valid = results[results['pb_valid']]
print(f'{len(valid)} / {len(results)} poses are PB-valid')
```

## Strain Energy Quantification

Beyond binary PB-valid, quantitative strain energy distinguishes "marginal" from "egregious" poses.

**Goal:** Quantify how far each docked pose is from its lowest-energy free conformer in MMFF94 energy units.

**Approach:** Generate a reference conformer ensemble (ETKDGv3 + MMFF94), make the docked and reference molecules chemically consistent by adding explicit hydrogens to both, relax only the added docked-pose hydrogens while fixing all heavy atoms, take the lowest sampled reference energy as baseline, and report `docked_energy - min_ref_energy` as a relative strain diagnostic. This is not a rigorous solution-phase conformational free energy.

```python
from rdkit import Chem
from rdkit.Chem import AllChem

def ligand_strain(docked_sdf, n_ref=20):
    suppl = Chem.SDMolSupplier(docked_sdf, removeHs=False)
    strains = []
    for docked in suppl:
        if docked is None:
            continue

        smi = Chem.MolToSmiles(docked)
        ref = Chem.MolFromSmiles(smi)
        if ref is None:
            strains.append({'strain': None, 'note': 'reference_parse_failed'})
            continue
        ref = Chem.AddHs(ref)
        props_ref = AllChem.MMFFGetMoleculeProperties(ref)
        if props_ref is None:
            strains.append({'strain': None, 'note': 'no_reference_mmff_parameters'})
            continue
        conf_ids = list(AllChem.EmbedMultipleConfs(
            ref, numConfs=n_ref, params=AllChem.ETKDGv3()
        ))
        if not conf_ids:
            strains.append({'strain': None, 'note': 'reference_embedding_failed'})
            continue
        AllChem.MMFFOptimizeMoleculeConfs(ref)

        ref_energies = []
        for c in conf_ids:
            ff = AllChem.MMFFGetMoleculeForceField(
                ref, props_ref, confId=c
            )
            if ff is not None:
                ref_energies.append(ff.CalcEnergy())
        if not ref_energies:
            strains.append({'strain': None, 'note': 'reference_force_field_failed'})
            continue
        min_ref = min(ref_energies)

        # MMFF energies are comparable only for the same explicit atom system.
        # Add any missing H coordinates, then relax H atoms while preserving the
        # docked heavy-atom pose.
        docked_h = Chem.AddHs(Chem.Mol(docked), addCoords=True)
        if docked_h.GetNumAtoms() != ref.GetNumAtoms():
            strains.append({'strain': None, 'note': 'atom_system_mismatch'})
            continue
        props_docked = AllChem.MMFFGetMoleculeProperties(docked_h)
        docked_ff = AllChem.MMFFGetMoleculeForceField(
            docked_h, props_docked
        ) if props_docked is not None else None
        if docked_ff is not None:
            for atom in docked_h.GetAtoms():
                if atom.GetAtomicNum() != 1:
                    docked_ff.AddFixedPoint(atom.GetIdx())
            docked_ff.Minimize(maxIts=200)
        docked_e = docked_ff.CalcEnergy() if docked_ff else None

        strains.append({
            'min_ref_energy': min_ref,
            'docked_energy': docked_e,
            'strain': docked_e - min_ref if docked_e is not None else None,
            'note': 'ok' if docked_e is not None else 'docked_force_field_failed',
        })
    return strains
```

Interpret relative MMFF strain in the context of ligand chemistry, conformer-sampling coverage, and force-field support. Boström et al. (1998) found a conformational energy penalty of no more than 3 kcal/mol for about 70% of 33 protein-bound ligands; that result does not establish a universal acceptance cutoff. Treat unusually high values as a prompt for inspection or use a project-defined threshold validated for the series.

## vdW Overlap with Protein

The 2024 benchmark criterion limits protein-ligand overlap to 7.5% of the ligand vdW volume, using protein radii scaled by 0.8. PoseBusters' `bust(...)` computes this check; do not substitute an unvalidated pairwise-distance sketch for its volume calculation.

## Aromatic Ring Planarity

```python
import numpy as np

def aromatic_planarity(mol):
    deviations = []
    for ring in mol.GetRingInfo().AtomRings():
        ring_atoms = [mol.GetAtomWithIdx(i) for i in ring]
        if not all(a.GetIsAromatic() for a in ring_atoms):
            continue
        coords = np.array([mol.GetConformer().GetAtomPosition(i)
                          for i in ring])
        centroid = coords.mean(axis=0)
        centered = coords - centroid
        _, s, vh = np.linalg.svd(centered)
        normal = vh[-1]
        deviation = np.abs(centered @ normal).max()
        deviations.append(deviation)
    return max(deviations) if deviations else 0
```

Aromatic ring deviation > 0.25 Å is implausible; flag.

## Model-Specific Failure Diagnosis

Do not assign a mechanism from the model name or a failed PoseBusters column alone. For DiffDock-L, EquiBind, TANKBind, Boltz, AlphaFold3, or another pose generator, report the observed failed checks on the evaluated dataset, inspect the structures, and compare against the method's documented constraints. A chirality, planarity, bond-geometry, or clash failure may justify filtering or a validated constrained-relaxation protocol, but relaxation must be checked for displacement of the binding mode.

### High strain after Vina docking

**Trigger:** Highly constrained pocket; flexible ligand.

**Symptom:** Relative strain is an outlier for the chemical series even though the pose passes the enabled geometric checks.

**Fix:** Inspect conformer-sampling coverage and force-field support. Compare additional docking or constrained-relaxation settings under a project-validated protocol rather than applying a universal strain or exhaustiveness cutoff.

## Reconciliation: PoseBusters vs RMSD

| RMSD <= 2A | PB-valid | Action |
|------------|----------|--------|
| Yes | Yes | Physically plausible and close to the reference; still validate suitability for the downstream task |
| Yes | No | Close to the reference but fails an enabled plausibility check; inspect the failure and any validated relaxation |
| No | Yes | Physically plausible but different from the reference; investigate alignment, protein state, and alternative binding modes |
| No | No | Different from the reference and fails an enabled plausibility check; inspect both causes before deciding whether to reject |

On the Astex Diverse Set reported by Buttenschoen et al. (2024), DiffDock's top-pose success fell from 72% by RMSD <= 2 Å alone to 47% when PB-validity was also required: a 25-percentage-point gap. Do not generalize that result to a fixed failure rate on other datasets.

## Integration into VS Pipeline

```python
import pandas as pd
from posebusters import PoseBusters

def pose_qc_pipeline(docked_sdfs, receptor_pdb):
    bust = PoseBusters(config='dock')
    all_results = []
    for sdf in docked_sdfs:
        r = bust.bust(mol_pred=sdf, mol_cond=receptor_pdb)
        check_cols = [
            col for col in r.select_dtypes(include='bool').columns
            if not col.lower().startswith('rmsd')
        ]
        r['pb_valid'] = r[check_cols].all(axis=1)
        r['source'] = sdf
        all_results.append(r)
    df = pd.concat(all_results)

    df['rank'] = df.groupby('source')['pb_valid'].cumsum()
    valid_top = df[df['pb_valid']].groupby('source').head(1)
    return valid_top
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Rows or expected checks are missing | Input loading failed or the selected configuration omits those checks | Inspect the returned DataFrame, loading-status columns, input format, and installed configuration |
| RMSD not computed | No reference provided | Pass `mol_true` parameter |
| All checks pass for invalid pose | Wrong receptor file format | Use PDB with hydrogens; PDBQT may not work |
| vdW overlap false positive on covalent | Covalent bond counted as clash | Use covalent docking-specific validation |
| Strain calculation slow | Too many reference conformers | Reduce `n_ref` to 5-10 |
| PoseBusters config error | Wrong or version-incompatible config name | Inspect the installed configuration registry; `redock`, `dock`, and `mol` are common configurations |
| posecheck unavailable | Different tool, similar purpose | `pip install posecheck` for alternative |

## References

- Buttenschoen M, Morris GM, Deane CM. "PoseBusters: AI-based docking methods fail to generate physically valid poses or generalise to novel sequences." *Chem. Sci.* 15:3130–3139 (2024). DOI: 10.1039/D3SC04185A.
- Boström J, Norrby PO, Liljefors T. "Conformational energy penalties of protein-bound ligands." *J. Comput.-Aided Mol. Des.* 12:383–396 (1998). DOI: 10.1023/A:1008007507641.
- Corso G et al. "DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking." *ICLR* (2023). OpenReview: https://openreview.net/forum?id=kKF8_K-mBbS.
- Stärk H et al. "EquiBind: Geometric Deep Learning for Drug Binding Structure Prediction." *PMLR* 162:20503–20521 (2022). https://proceedings.mlr.press/v162/stark22b.html.
- Lu W et al. "TankBind: Trigonometry-Aware Neural NetworKs for Drug-Protein Binding Structure Prediction." *NeurIPS* 35 (2022). Official repository: https://github.com/luwei0917/TankBind.
- Abramson J et al. "Accurate structure prediction of biomolecular interactions with AlphaFold 3." *Nature* 630:493–500 (2024). DOI: 10.1038/s41586-024-07487-w.
- Boltz official repository and documentation: https://github.com/jwohlwend/boltz.
- PoseBusters documentation, Python API: https://posebusters.readthedocs.io/en/latest/api.html.

## Related Skills

- chemoinformatics/virtual-screening - Source of poses to validate
- chemoinformatics/ml-docking-rescoring - DiffDock, EquiBind, TANKBind validation
- chemoinformatics/molecular-io - SDF format handling
- chemoinformatics/conformer-generation - Generate reference conformer ensemble for strain
- chemoinformatics/free-energy-calculations - PoseBusters-valid poses for FEP input
- chemoinformatics/covalent-design - Covalent pose validation
<!-- END FILE: chemoinformatics/pose-validation/SKILL.md -->

## 子目录：chemoinformatics/protac-degraders

<!-- BEGIN FILE: chemoinformatics/protac-degraders/SKILL.md -->
---
name: bio-protac-degraders
description: Designs PROTACs, molecular glues, and bivalent degraders with explicit handling of E3 ligase choice (VHL, CRBN, IAP, MDM2, KEAP1), linker design (length, composition, rigidity), ternary complex prediction (PRosettaC, DeepTernary, AlphaFold3), cooperativity (alpha), DC50 / Dmax characterization, hook effect, and prediction-experiment reconciliation. Use when designing targeted protein degraders, planning linker SAR, predicting ternary complex stability, or building generative degrader workflows.
tool_type: python
primary_tool: PRosettaC
---

## Version Compatibility

Reference examples tested with: PRosettaC (web service), DeepTernary research code, AlphaFold3, Boltz-1 / Boltz-2, RDKit 2024.09+, OpenMM 8.1+ (for ternary MD).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# PROTAC and Bivalent Degrader Design

Design bifunctional molecules (PROTACs) that recruit an E3 ubiquitin ligase to a target protein, inducing target ubiquitination and proteasomal degradation. PROTACs differ from traditional drugs: a productive **ternary complex** (target + PROTAC + E3) is required, not just target binding. The modality has produced clinical programs, but their development and regulatory status changes rapidly and must be checked from current sources. PROTAC design balances **target ligand binding**, **E3 ligand binding**, **linker geometry** (length, rigidity, chemistry), **cooperativity**, **dose-dependent ternary-complex formation**, and **cell permeability**. Negative cooperativity and the high-concentration hook effect are distinct phenomena, although cooperativity can influence the dose-response profile.

For target ligand design, see `chemoinformatics/virtual-screening` and `chemoinformatics/admet-prediction`. For linker-only enumeration, see `chemoinformatics/reaction-enumeration`. For generative linker design, see `chemoinformatics/generative-design`.

## E3 Ligase Choice

| Recruited UPS component | Ligand series | Published design context | Limitations |
|-----------|---------------|---------|-------------|
| VHL | VL-269 (Gechijian et al. 2018) | Published VHL-recruiting degraders | Expression and productive geometry are system-dependent |
| CRBN (cereblon) | thalidomide, pomalidomide | Extensively used recruiter series | Neosubstrate liabilities depend on recruiter and context |
| IAP (XIAP, cIAP1) | SMAC-mimetic-derived recruiters | Published IAP-recruiting degraders | Target scope and cellular effects require validation |
| MDM2 | nutlin-derived recruiters | Published MDM2-recruiting degraders | Target diversity and pathway effects require validation |
| KEAP1 | KEAP1-directed recruiters | CUL3-KEAP1 recruitment studies | Specialized use and limited comparative validation |
| DCAF15 | Aryl sulfonamides such as E7820 | DDB1-CUL4 / DCAF15 systems | Molecular-glue and degrader mechanisms require careful distinction |
| RNF114 | Nimbolide, EN219 | Covalent RNF114 recruitment | Limited tooling |
| RNF4 | CCW16 | Covalent RNF4 recruitment | Limited tooling |
| UBE2D (E2, not E3) | EN450 | Covalent molecular-glue mechanism involving NFKB1 | Do not classify as an E3-ligase recruiter |

**Decision:** Select an E3 recruiter using evidence for ligand availability, target/E3 geometry, cellular expression, neosubstrate liabilities, and the intended biological system. CRBN and VHL are common starting points with extensive published examples, but neither is a universal first choice.

## Linker Design Principles

Linkers tune ternary complex geometry and stability. The ranges below are exploratory starting points, not validated acceptance criteria:

| Property | Range | Effect |
|----------|-------|--------|
| Linker length | Project-defined enumerated series | Critical; geometry-dependent |
| Linker rigidity | Flexible (PEG) vs rigid (piperazine, pyridine) | Changes the accessible conformational ensemble |
| Linker chemistry | PEG, alkyl, piperazine, triazole, ether, amide | PEG common; rigid for tighter binding |
| Click chemistry compatibility | Triazole-forming routes are one option | Requires route- and attachment-specific synthesis review |
| Molecular size and polarity | Measure across the designed series | Permeability, solubility, and exposure depend on the complete molecule and its conformations |

**Critical:** The "Goldilocks linker length" is target-specific. Too short can create a ternary clash; too long can impose an unfavorable entropic cost or permit unproductive geometries. Enumerate a series around the geometry supported by the binary structures rather than assuming a universal optimal range.

## Decision Tree by Scenario

| Goal | E3 / linker | Tools |
|------|-------------|-------|
| Initial degrader series | Compare supported recruiter and linker variants | PRosettaC for ternary hypotheses |
| Reduce recruiter-specific liabilities | Compare alternative E3 recruiters and linker geometries | Structural hypotheses + cellular selectivity validation |
| Target with prior recruiter-specific evidence | Reproduce the supported recruiter context, then vary deliberately | Match the published and intended biological systems |
| Targeted protein degradation program | Select E3 using geometry, expression, and liabilities | Structural and experimental validation track |
| Novel target without an established ternary model | Multiple E3 / linker variants | Combinatorial design + PRosettaC |
| Molecular glue (non-PROTAC) | Use a glue-specific discovery strategy | Distinct mechanism; do not treat as linker design |
| Characterize cooperativity | Structural hypotheses plus experiment | ITC or SPR/BLI with matched binary and ternary measurements |
| Cell-active candidate | Standard development | PK + degradation cellular assays |

## Ternary Complex Prediction Tools

| Tool | Approach | Strength | Fails when |
|------|----------|----------|------------|
| PRosettaC | Constrained PatchDock, RosettaDock refinement, PROTAC conformer generation, repacking, and clustering | PROTAC-specific published workflow | Performance varies by complex; Rosetta/service requirements |
| DeepTernary | Equivariant deep learning | Fast; SE(3) | OOD chemistry |
| AlphaFold3 | Unrestrained whole-complex prediction | Accepts proteins and ligands | No arbitrary user distance-restraint interface; benchmark PROTAC use |
| Boltz-1 / Boltz-2 | Unrestrained whole-complex prediction | Open local models | Limited PROTAC-specific validation |
| HADDOCK | Information-driven, restraint-guided docking | Mature integrative docking framework | Manual restraint specification |

**Decision:** Use a PROTAC-specific method such as **PRosettaC** for first-pass ternary modeling. AlphaFold3 or Boltz can provide unrestrained whole-complex predictions, but should be benchmarked on relevant ternary complexes. **DeepTernary** is released research code rather than a hosted API; validate it against relevant structures before prospective ranking.

## Cooperativity (Alpha)

Cooperativity quantifies how the ternary complex stabilizes (or destabilizes) the binary binding:

```
alpha = (Kd_binary,target) / (Kd_ternary,target)
```

- alpha > 1: positive cooperativity (ternary stronger than binary)
- alpha = 1: no cooperativity (independent binding)
- alpha < 1: negative cooperativity (mutual destabilization)

Positive cooperativity can favor ternary-complex formation, but the preferred alpha is system- and assay-dependent and does not alone establish degradation efficacy. Alpha must be measured from binary and ternary binding experiments; a predicted structure does not directly provide it.

Measure with ITC (isothermal titration calorimetry) or SPR/BLI titrations of binary vs ternary.

## DC50 / Dmax Characterization

In cellular assays:
- **DC50**: PROTAC concentration for 50% degradation (analogous to IC50)
- **Dmax**: maximum fraction degraded at any concentration

| Property | What to report | Interpretation |
|----------|----------------|----------------|
| DC50 | Concentration producing 50% of the assay's fitted maximal degradation | Compare only across matched assay conditions; no universal clinical cutoff |
| Dmax | Maximum observed or fitted degradation and uncertainty | Required depletion is target- and phenotype-dependent |
| Hook effect | Full concentration-response range and concentration of any downturn | A high-concentration effect; its location is system- and assay-dependent |
| Cooperativity | Alpha from matched binary and ternary binding experiments | Distinct from the hook effect and insufficient by itself to predict degradation |

**Hook effect**: at high PROTAC concentrations, binary complexes (PROTAC-target alone, PROTAC-E3 alone) dominate, and ternary complex formation drops. Dose-response curves are bell-shaped.

## Ternary Complex Modeling Workflow

**Goal:** Predict 3D structure of target-PROTAC-E3 ternary complex.

**Approach:**
1. Start with binary co-crystals: target + target-ligand pose; E3 + E3-ligand pose
2. Connect via linker enumeration (combinatorial)
3. Score by geometric feasibility (linker length, no clashes)
4. Refine with energy minimization

```python
# Pseudo-code workflow
def predict_ternary(target_pdb, target_ligand_sdf,
                    e3_pdb, e3_ligand_sdf, linker_smiles):
    # 1. Place binary complexes in same coordinate frame
    # 2. Enumerate linker connectivity from target-ligand exit vector to e3-ligand entry vector
    # 3. Score by total linker length, RMSD to expected geometry
    # 4. Apply a documented refinement protocol and test convergence
    return ternary_poses
```

For a production workflow, use PRosettaC or provide both proteins and the complete PROTAC as components of an unrestrained AlphaFold3 input. AlphaFold3 does not expose arbitrary chain-chain distance restraints; compare predicted interfaces and confidence with known complexes or a PROTAC-specific method.

## Linker Geometry Assessment

```python
from rdkit import Chem
from rdkit.Chem import AllChem

def attachment_distance(target_ligand, e3_ligand,
                        target_attachment_idx, e3_attachment_idx):
    """
    Measure an attachment-point distance after both ligands have been placed in
    the same ternary-complex coordinate frame.
    """
    p1 = target_ligand.GetConformer().GetAtomPosition(target_attachment_idx)
    p2 = e3_ligand.GetConformer().GetAtomPosition(e3_attachment_idx)
    return p1.Distance(p2)
```

An attachment-point distance does not map uniquely to a linker atom count: bond geometry, rigidity, branching, solvation, and the relative protein orientation all matter. Enumerate chemically synthesizable linker candidates, sample their conformers in the ternary geometry, and retain candidates that can connect without severe strain or clashes.

## Generative Linker Design

REINVENT 4 can generate linkers, but it does not provide the `ternary_score` / `deepternary` interface shown in some informal examples. Export generated candidates, run an installed and validated ternary-prediction workflow separately, and then join the structural scores back to the candidates. Do not assume DeepTernary is a web API or a built-in REINVENT scoring component.

## Per-Tool Failure Modes

### PRosettaC -- inaccessible E3 in selected ligase

**Trigger:** Target's known binding mode incompatible with E3 ligase orientation.

**Mechanism:** The selected binary poses, exit vectors, linker conformations, or protein orientation may not support a compatible ternary geometry.

**Symptom:** Low ternary complex scores; high RMSD across replicates.

**Fix:** Try a different E3 such as CRBN or VHL and compare against experimentally resolved ternary complexes with compatible exit-vector geometry.

### DeepTernary -- novel chemotype

**Trigger:** Target ligand or E3 ligand outside training distribution.

**Mechanism:** A ligand, linker, target, or E3 outside the method's validated domain may require extrapolation.

**Symptom:** Predicted ternary complex unrealistic.

**Fix:** Compare with an independently configured structural method and relevant known complexes; validate prospective ranking experimentally.

### Hook effect at high PROTAC concentration

**Trigger:** PROTAC concentration becomes high enough that separate target-PROTAC and E3-PROTAC binary complexes compete with productive ternary-complex formation.

**Mechanism:** Saturation by binary complexes reduces the population of productive ternary complex. Negative cooperativity can worsen ternary formation but is not the definition of the hook effect.

**Symptom:** Degradation increases and then decreases across a sufficiently broad concentration-response experiment.

**Fix:** Confirm the downturn experimentally over a broad dose range, then optimize ternary-complex geometry, cooperativity, exposure, and dosing without assuming that linker shortening alone will solve it.

### Insufficient cell permeability

**Trigger:** Measured permeability or cellular exposure is poor relative to biochemical activity.

**Mechanism:** Size, exposed polarity, conformation, ionization, or efflux may limit intracellular exposure.

**Symptom:** Cellular degradation potency is substantially worse than biochemical ternary-complex or binding measurements.

**Fix:** Optimize linker and exposed polarity using measured permeability, solubility, and intracellular exposure across the series. Do not impose a universal MW or TPSA cutoff.

### E3-target distance miscalculation

**Trigger:** Computing linker length from binary models without ternary refinement.

**Mechanism:** A distance from separately positioned binary structures does not determine the accessible ternary geometry or linker conformational ensemble.

**Symptom:** PROTACs synthesized at wrong linker length; no degradation.

**Fix:** Use a ternary structural hypothesis to define a chemically diverse linker series, then compare conformational feasibility and experimental degradation across that series.

### Molecular glue vs PROTAC confusion

**Trigger:** Designing as PROTAC when target lacks defined ligand.

**Mechanism:** A molecular glue stabilizes or induces a protein-protein interaction without the two-ligand-plus-linker architecture assumed by a PROTAC workflow.

**Symptom:** Design too rigid; no degradation despite ternary prediction.

**Fix:** For targets without known ligand, consider molecular glue discovery instead.

## Reconciliation: PRosettaC vs AlphaFold3

| Aspect | PRosettaC | AlphaFold3 |
|--------|-----------|------------|
| Approach | PROTAC-specific Rosetta sampling | Unrestrained foundation-model prediction |
| Accuracy | Higher average DockQ in one 36-structure comparison, but only 25 complexes were modeled and most predictions were low quality | Limited PROTAC-specific validation |
| Speed | Measure for the installed workflow and hardware | Measure for the selected service or local hardware |
| Access | Web service | AlphaFold Server or local installation, subject to their terms and limits |
| Restraints | Method-specific setup | No arbitrary user distance restraints |
| Decision | Use as a PROTAC-specific structural hypothesis | Use as an independently benchmarked structural hypothesis |

Use PRosettaC or another benchmarked structural method to generate hypotheses, then measure ternary binding/cooperativity and cellular degradation experimentally. Do not treat any one modeling method as a validated universal ranker.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| PRosettaC fails to converge | Input geometry, sampling, or service/configuration problem | Inspect inputs and logs; compare justified recruiter/linker hypotheses |
| DeepTernary returns clashing pose | Prediction outside a validated domain or incorrect interface | Inspect confidence and clashes; compare an independent method and known structures |
| AlphaFold3 ternary unrealistic | Unrestrained prediction has a low-confidence or incorrect interface | Inspect confidence and compare with PRosettaC or known ternary structures |
| Cellular phenotype disagrees with target-degradation assays | Exposure, off-target degradation, assay timing, or pathway effects | Measure target engagement/degradation and use proteome-wide selectivity assays where appropriate |
| Degradation decreases at high PROTAC concentration | Hook effect from competing binary complexes | Confirm with a broad dose range; optimize ternary geometry and exposure |
| Synthesis is impractical | Proposed connectivity lacks a credible route | Obtain medicinal-chemistry review and redesign attachment chemistry or linker |
| Poor permeability or intracellular exposure | Size, exposed polarity, conformation, or efflux | Measure the bottleneck and optimize the series; avoid a universal size cutoff |

## References

- Békés M, Langley DR, Crews CM. "PROTAC targeted protein degraders: the past is prologue." *Nat. Rev. Drug Discov.* 21:181–200 (2022). DOI: 10.1038/s41573-021-00371-6.
- Drummond ML, Williams CI. "In Silico Modeling of PROTAC-Mediated Ternary Complexes: Validation and Application." *J. Chem. Inf. Model.* 59:1634–1644 (2019). DOI: 10.1021/acs.jcim.8b00992.
- Schapira M, Calabrese MF, Bullock AN, Crews CM. "Targeted protein degradation: expanding the toolbox." *Nat. Rev. Drug Discov.* 18:949–963 (2019). DOI: 10.1038/s41573-019-0047-y.
- Gechijian LN et al. "Functional TRIM24 degrader via conjugation of ineffectual bromodomain and VHL ligands." *Nat. Chem. Biol.* 14:405–412 (2018). DOI: 10.1038/s41589-018-0010-y.
- Zaidman D, Prilusky J, London N. "PRosettaC: Rosetta Based Modeling of PROTAC Mediated Ternary Complexes." *J. Chem. Inf. Model.* 60:4894–4903 (2020). DOI: 10.1021/acs.jcim.0c00589.
- Xue F, Zhang M, Li S et al. "SE(3)-equivariant ternary complex prediction towards target protein degradation." *Nat. Commun.* 16:5514 (2025). DOI: 10.1038/s41467-025-61272-5.
- Schulz JM, Schürer SI, Reynolds RC, Schürer SC. "PRosettaC outperforms AlphaFold3 for modeling PROTAC ternary complexes." *Sci. Rep.* 15:37620 (2025). DOI: 10.1038/s41598-025-21502-8.
- Bondeson DP et al. "Catalytic in vivo protein knockdown by small-molecule PROTACs." *Nat. Chem. Biol.* 11:611–617 (2015). DOI: 10.1038/nchembio.1858.
- Ward CC et al. "Covalent Ligand Screening Uncovers a RNF4 E3 Ligase Recruiter for Targeted Protein Degradation Applications." *ACS Chem. Biol.* 14:2430–2440 (2019). DOI: 10.1021/acschembio.8b01083.
- Luo M et al. "Chemoproteomics-enabled discovery of covalent RNF114-based degraders that mimic natural product function." *Cell Chem. Biol.* 28:559–566.e15 (2021). DOI: 10.1016/j.chembiol.2021.01.005.
- King EA et al. "Chemoproteomics-enabled discovery of a covalent molecular glue degrader targeting NF-kappaB." *Cell Chem. Biol.* 30:394–402.e9 (2023). DOI: 10.1016/j.chembiol.2023.02.008.
- Abramson J et al. "Accurate structure prediction of biomolecular interactions with AlphaFold 3." *Nature* 630:493–500 (2024). DOI: 10.1038/s41586-024-07487-w.
- REINVENT 4 official repository and installation documentation: https://github.com/MolecularAI/REINVENT4.
- HADDOCK3 official documentation: https://www.bonvinlab.org/haddock3/.
- Boltz official repository and documentation: https://github.com/jwohlwend/boltz.

## Related Skills

- chemoinformatics/molecular-io - Parse linker and ligand SMILES
- chemoinformatics/reaction-enumeration - Linker enumeration combinatorial
- chemoinformatics/generative-design - REINVENT linker mode
- chemoinformatics/conformer-generation - Ternary conformer sampling
- chemoinformatics/virtual-screening - Validate target ligand binding
- chemoinformatics/free-energy-calculations - Ternary ABFE / cooperativity
- chemoinformatics/admet-prediction - PROTAC ADMET specific challenges
- structural-biology/structure-io - PDB / mmCIF for ternary complex
<!-- END FILE: chemoinformatics/protac-degraders/SKILL.md -->

## 子目录：chemoinformatics/qsar-modeling

<!-- BEGIN FILE: chemoinformatics/qsar-modeling/SKILL.md -->
---
name: bio-qsar-modeling
description: Builds QSAR / QSPR models using chemprop D-MPNN, MolFormer, Uni-Mol, ChemBERTa, random forest baselines, and Gaussian processes with explicit handling of OECD 5 principles, applicability domain (kNN, leverage, conformal prediction, Mahalanobis), scaffold-balanced splits, ensemble uncertainty, calibration (Platt, isotonic), feature importance (SHAP, atomic attribution), and prospective validation. Use when building target-specific predictive models from in-house bioassay data, ADMET endpoints, or selectivity profiles.
tool_type: python
primary_tool: chemprop
---

## Version Compatibility

Reference examples target: chemprop 2.2.x (major API change from 1.x), RDKit 2024.09+, scikit-learn >=1.4,<1.6, MAPIE >=0.8,<1.0 for the `MapieRegressor` example, shap 0.44+, and pytorch 2.1+. Recheck examples before widening these bounds because Chemprop, scikit-learn calibration, and MAPIE interfaces evolve independently.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `chemprop train --help` (chemprop 2.x); `chemprop_train --help` (1.x legacy)

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# QSAR Modeling

Build quantitative structure-activity relationship models from molecular structure inputs. The choice of model, featurization, and split strategy determines whether the model captures transferable chemical signal or memorizes the training data. chemprop D-MPNN with optional Morgan / RDKit descriptors is a useful open-source approach; transformer-based methods (MolFormer, Uni-Mol, ChemBERTa) should be compared on the same split and endpoint. The OECD validation principles support transparent documentation and evaluation of (Q)SAR models, but following them does not by itself confer regulatory acceptance.

For descriptor/fingerprint choices, see `chemoinformatics/molecular-descriptors`. For ADMET-specific QSAR, see `chemoinformatics/admet-prediction`. For molecular standardization (critical upstream), see `chemoinformatics/molecular-standardization`.

## Model Taxonomy

| Model | Architecture | Use case | Fails when |
|-------|--------------|----------|------------|
| Random Forest + ECFP4 | Classical baseline | Small-data comparison, interpretability | May miss signal not represented by the fingerprint |
| chemprop D-MPNN | Directed message passing | Graph-learning candidate to benchmark | Can overfit when data are sparse or biased |
| chemprop D-MPNN + RDKit 2D | Hybrid graph + descriptors | Useful hybrid baseline; compare on the same split | Diminishing returns at large data |
| MolFormer | SMILES transformer | Large public training data benefit | Compute overhead; OOD risk |
| Uni-Mol | 3D-aware transformer | 3D-relevant endpoints (binding) | Requires 3D conformers |
| ChemBERTa-2 | SMILES transformer pretrained on up to 77M molecules | SMILES language-model baseline | Fine-tuning benefit is endpoint- and split-dependent |
| Gaussian Process + ECFP4 | Probabilistic | Active learning; uncertainty | O(N^3) scaling |
| MultiTask DNN | Joint training | Multiple endpoints | Data must overlap |

**Decision:** Compare a fingerprint-based baseline with chemprop under the same split and endpoint. Add a pretrained transformer or 3D model only when its representation, compute cost, and validation design fit the deployment question; dataset size alone does not determine the winner.

## Decision Tree by Scenario

| Dataset context | Endpoint type | Model to benchmark |
|--------------|---------------|-------|
| Sparse labels or few independent series | Regression / classification | Regularized fingerprint baseline; quantify instability and avoid unsupported deployment |
| Multiple scaffold groups with adequate labels | Regression / classification | Fingerprint baseline plus chemprop on identical splits |
| Large public or internal training collection | Regression / classification | Benchmark chemprop and a relevant pretrained representation |
| Multi-task | Related endpoints (CYP3A4, CYP2D6, etc.) | chemprop MultiTask |
| 3D-relevant | Binding, conformer-dependent | Uni-Mol with conformer ensemble |

## OECD 5 Principles

The OECD principles were agreed in 2004; the 2007 guidance explains their application:

1. **Defined endpoint**: specific bioassay, units, threshold definitions
2. **Unambiguous algorithm**: reproducible code, fixed random seeds, version-pinned dependencies
3. **Defined applicability domain (AD)**: where the model is valid
4. **Appropriate measures of goodness-of-fit, robustness, and predictivity**: external test set and suitable validation
5. **Mechanistic interpretation, if possible**: biological/chemical rationale where available

For non-regulatory QSAR, all 5 still good practice; especially **AD definition** is critical.

## Applicability Domain Methods

| Method | Definition | Pro | Con |
|--------|-----------|-----|-----|
| **Ensemble variance** | Std across N-model ensemble predictions | Supported by `chemprop predict --uncertainty-method ensemble` when multiple model paths are supplied | Assumes useful ensemble diversity; not calibrated coverage |
| kNN distance | Mean Tanimoto to k nearest in training | Easy to interpret | Doesn't account for label distribution |
| Leverage | Hat matrix diagonal | Statistical | Linear assumptions |
| KDE on PCA | Density in feature space | Captures multivariate structure | Density choice subjective |
| Mahalanobis distance | Covariance-aware distance | Theoretically motivated | High-dim instability |
| Conformal prediction | Per-prediction interval or set | Finite-sample marginal coverage under exchangeability | Requires a calibration design and compatible predictor |
| Bayesian / MC-dropout | Posterior or dropout variance | Direct uncertainty | Computational cost |
| Tanimoto coverage | At least 1 NN within threshold | Practical | Threshold subjective |

Ensemble disagreement is one useful uncertainty diagnostic, not a formally defined applicability domain or calibrated coverage guarantee. If using a threshold such as a training-distribution percentile, label it as a project-defined heuristic and validate it prospectively.

## chemprop 2.x Training (CLI)

**Goal:** Train five replicated chemprop runs, each containing a five-model D-MPNN ensemble with RDKit 2D descriptor features and a scaffold-balanced train/validation/test split.

**Approach:** For current chemprop 2.x, invoke `chemprop train` with `--molecule-featurizers rdkit_2d`, `--num-replicates 5`, `--ensemble-size 5`, and `--split scaffold_balanced`. Replicates repeat splitting/training with incremented seeds; they are not five-fold cross-validation. Confirm the exact flags with `chemprop train --help` because the v2 CLI continues to evolve.

```bash
# chemprop 2.x CLI (current): use 'chemprop train' (space; dashes not underscores)
chemprop train \
    --data-path data.csv \
    --task-type classification \
    --save-dir model_dir \
    --molecule-featurizers rdkit_2d \
    --num-replicates 5 \
    --ensemble-size 5 \
    --epochs 50 \
    --batch-size 128 \
    --split scaffold_balanced \
    --split-sizes 0.8 0.1 0.1 \
    --metric roc

# chemprop 1.x legacy CLI (for backwards reference):
# chemprop_train --data_path data.csv --dataset_type classification ...
```

Key flags (chemprop 2.x):
- `--molecule-featurizers rdkit_2d`: include current v2 RDKit descriptors, which are scaled by default (the legacy v1-normalized generator is `v1_rdkit_2d_normalized`)
- `--num-replicates 5`: repeat the split/training workflow with successive seeds; this replaced `--num-folds` in chemprop 2.1
- `--ensemble-size 5`: train five models per replicate for an ensemble prediction
- `--split scaffold_balanced`: prevent scaffold leakage (was `--split_type` in 1.x)
- `--split-sizes 0.8 0.1 0.1`: 80/10/10 train/val/test

Total models: 25 (5 replicates x 5 ensemble members). Report which predictions are being aggregated and treat ensemble standard deviation as an uncertainty diagnostic, not a calibrated guarantee.

At prediction time, uncertainty output is opt-in and requires the actual saved model paths:

```bash
chemprop predict --test-path test.csv \
    --model-paths path/to/model_1.ckpt path/to/model_2.ckpt \
    --uncertainty-method ensemble \
    --preds-path predictions.csv
```

## Scaffold-Balanced Split

**Goal:** Partition a SMILES dataset into train/val/test such that no Bemis-Murcko scaffold appears in more than one split (prevents chemotype leakage).

**Approach:** Group compounds by scaffold and assign whole scaffold groups to train, validation, or test. chemprop's `--split scaffold_balanced` implements a scaffold-based allocation; `--class-balance` is a separate training option and does not make this split outcome-stratified. The chemprop default split is random, so request scaffold-balanced explicitly when it matches the deployment question.

`scaffold_balanced` assigns each scaffold group to one of train / validation / test, reducing direct scaffold leakage. It is not universally the correct validation design: time splits, externally defined series, grouped cross-validation, and prospective tests may better represent a particular deployment setting.

Choose and document the primary split before model selection. A random split can answer an interpolation question but often shares close analogues across partitions; a scaffold split tests transfer across scaffold groups; a time or prospective split tests the historical deployment process. If several splits are reported, interpret their differences as split-specific sensitivity rather than a universal "true generalization gap."

## Conformal Prediction for Calibrated Uncertainty

Use conformal prediction when calibrated marginal coverage under the stated exchangeability assumptions matters. Ensemble variance is simpler, but it is not a substitute for a conformal guarantee.

```python
# MAPIE expects a scikit-learn-compatible estimator (.fit / .predict / .predict_proba).
# chemprop 2.x is NOT scikit-learn-compatible out of the box -- either wrap chemprop
# in a thin sklearn estimator class or use MAPIE only with the sklearn baseline.
from mapie.regression import MapieRegressor
from sklearn.ensemble import RandomForestRegressor

base = RandomForestRegressor(n_estimators=500, random_state=42)
mapie = MapieRegressor(estimator=base, method='plus', cv=5)
mapie.fit(X_train, y_train)
y_pred, y_intervals = mapie.predict(X_test, alpha=0.1)  # alpha=0.1 -> 90% coverage
```

Alpha 0.05 targets 95% marginal coverage and alpha 0.10 targets 90%, subject to the conformal method's assumptions. MAPIE supports the sklearn baseline directly; integrating chemprop requires a separately implemented and tested compatible wrapper.

## SHAP / Atomic Attribution

For mechanistic interpretation:

For a scikit-learn-style model (e.g., Random Forest baseline on ECFP4), SHAP integrates directly:

```python
import shap
from sklearn.ensemble import RandomForestClassifier

# X_train / X_test are Morgan fingerprint arrays (n_samples, n_bits)
model = RandomForestClassifier(n_estimators=500, random_state=42).fit(X_train, y_train)
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Per-bit contribution; for atomic interpretation, map bits back to
# generating atoms via AllChem.GetMorganFingerprintAsBitVect(mol, ..., bitInfo=bi)
# and aggregate SHAP across all bits triggered by each atom.
```

For chemprop D-MPNN, SHAP requires a custom wrapper (chemprop is not sklearn-compatible). A PyTorch attribution method must be adapted to the model's graph inputs and validated; the chemprop 2.x CLI does not provide the `--uncertainty-method classification` atom-attribution interface. Use directly supported fingerprint SHAP for the classical baseline unless a tested graph-attribution implementation is available.

## Bayesian Optimization for Active Learning

```python
import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF

gp = GaussianProcessRegressor(kernel=RBF(length_scale=1.0), random_state=42)
gp.fit(X_train, y_train)
mu, sigma = gp.predict(X_pool, return_std=True)

# Expected Improvement
def expected_improvement(mu, sigma, y_best, xi=0.01):
    improvement = mu - y_best - xi
    ei = np.zeros_like(mu, dtype=float)
    nonzero = sigma > 0
    z = improvement[nonzero] / sigma[nonzero]
    ei[nonzero] = (
        improvement[nonzero] * norm.cdf(z)
        + sigma[nonzero] * norm.pdf(z)
    )
    return ei

ei = expected_improvement(mu, sigma, y_train.max())
next_to_test = X_pool[ei.argmax()]
```

For chemprop + active learning, replace GP with chemprop ensemble + ensemble variance.

## Calibration (Platt / Isotonic)

Deep learning probabilities are not guaranteed to be calibrated. Use Platt (logistic) or isotonic calibration for binary probabilities, choosing the method with a held-out calibration set. `--metric roc` evaluates ranking and does not automatically calibrate chemprop probabilities; export validation probabilities and fit the calibrator externally:

```python
from sklearn.isotonic import IsotonicRegression
iso = IsotonicRegression(out_of_bounds='clip').fit(val_chemprop_probs, val_true)
test_calibrated = iso.predict(test_chemprop_probs)
```

## Multi-Task QSAR

Train multiple related endpoints jointly:

```python
df = pd.DataFrame({
    'smiles': [...],
    'CYP1A2_inhibition': [...],
    'CYP2D6_inhibition': [...],
    'CYP3A4_inhibition': [...],
})
df.to_csv('multitask.csv', index=False)
```

```bash
chemprop train --data-path multitask.csv --task-type classification \
               --target-columns CYP1A2_inhibition CYP2D6_inhibition CYP3A4_inhibition \
               --save-dir multitask_model
```

Multitask learning can help when endpoints share predictive signal or data, but negative transfer is also possible. Compare single-task and multitask models under identical splits rather than assuming improvement from endpoint relatedness.

## Per-Tool Failure Modes

### Random split for QSAR

**Trigger:** Default sklearn `train_test_split`.

**Mechanism:** Compounds from same scaffold scatter across train/test; performance optimistic.

**Symptom:** Performance drops substantially from random splits to scaffold, time, external-series, or prospective evaluation.

**Fix:** Use `--split scaffold_balanced` in chemprop 2.x (or `--split_type scaffold_balanced` in chemprop 1.x legacy); or `scaffold_split` from `chemoinformatics/scaffold-analysis`.

### Class imbalance not handled

**Trigger:** 10:1 negative:positive ratio in dataset.

**Mechanism:** Default loss treats classes equally; model learns majority class.

**Symptom:** High accuracy but precision/recall on minority class poor.

**Fix:** Class-weighted loss; SMOTE; or report AUC/F1 not accuracy.

### Over-engineered features

**Trigger:** Including hundreds of descriptors (e.g., `rdkit_2d` not normalized).

**Mechanism:** Some descriptors dominate scaling; model overfits.

**Symptom:** Validation performance differs widely across runs; high feature importance noise.

**Fix:** In current chemprop 2.x use `rdkit_2d`, which is scaled by default, or supply a documented descriptor set with preprocessing fit only on the training data.

### Missing AD assessment

**Trigger:** Predicting on novel chemotypes without AD check.

**Mechanism:** Model extrapolates; predictions unreliable.

**Symptom:** Confident predictions but actual values different.

**Fix:** Predefine and validate one or more domain/uncertainty diagnostics, such as neighborhood similarity, ensemble disagreement, or conformal output, and report what each diagnostic does and does not guarantee.

### chemprop 1.x vs 2.x confusion

**Trigger:** Code/tutorial from before late 2024.

**Mechanism:** Major API change: `chemprop_train` -> `chemprop train`; Python API redesigned.

**Symptom:** ImportError or different keyword arguments.

**Fix:** Use `chemprop --version`; check 2.x documentation; migrate APIs.

### Pretrained Transformer overhead without data benefit

**Trigger:** Adding a pretrained transformer without a matched baseline and deployment-relevant validation.

**Mechanism:** The pretrained representation, fine-tuning design, and endpoint may not provide additional transferable signal.

**Symptom:** No improvement over chemprop; slower training.

**Fix:** Compare against fingerprint and chemprop baselines on the same split, and retain the transformer only when the measured benefit justifies its cost.

### Validation leakage via standardization

**Trigger:** Standardization rules or learned preprocessing parameters are chosen or fit using validation/test data.

**Mechanism:** Test-set information influences representations, feature selection, scaling, or deduplication decisions.

**Symptom:** Re-fitting preprocessing on training data alone reduces held-out performance or changes membership across splits.

**Fix:** Freeze chemistry rules before evaluation and fit learned preprocessing on training data only. Apply the frozen pipeline to validation, test, and prospective compounds while preserving endpoint-relevant stereochemistry.

## Reconciliation: Classical RF vs chemprop vs Transformer

| Aspect | RF + ECFP4 | chemprop D-MPNN | MolFormer |
|--------|-----------|-----------------|-----------|
| Data regime | Useful baseline across sizes; especially important in small data | Compare when graph learning is plausible | Compare when pretrained representations and compute are justified |
| Interpretability | Fingerprint importance or SHAP, with bit-to-atom mapping caveats | Graph attribution requires a custom, validated implementation | Model-specific attribution requires validation |
| Uncertainty | Bootstrap or conformal wrapper | Ensemble disagreement; calibrate separately when needed | Method-dependent; validate empirically |
| Hardware | CPU | CPU or GPU depending on scale | Usually GPU for fine-tuning |
| OOD performance | Benchmark on the intended split/domain | Benchmark on the intended split/domain | Benchmark on the intended split/domain |
| Production deployment | Version-pinned sklearn artifact or service | Version-pinned native checkpoint/service; do not assume ONNX support | Version-pinned framework artifact/service |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| chemprop hangs at start | GPU OOM | Reduce batch_size; check CUDA |
| All predictions same value | Constant target | Standardize labels |
| AUC mismatched across folds | Random seed not set | `--seed 42` |
| Test AUC = train AUC | No held-out data | Use scaffold_balanced split |
| Ensemble variance always small | Ensemble members insufficiently diverse | Check the documented seed behavior and training randomness for each replicate/member |
| SHAP fails on D-MPNN | Graph inputs are not compatible with the tree-model interface | Use a tested graph-attribution implementation or report the fingerprint baseline attribution |
| MolFormer fine-tune slow | All parameters trained | Use LoRA or freeze early layers |
| Calibration degrades held-out results | Calibrator overfit or distribution shifted | Refit on a proper calibration split and report uncalibrated and calibrated metrics |

## References

- Yang K et al. "Analyzing Learned Molecular Representations for Property Prediction." *J. Chem. Inf. Model.* 59:3370–3388 (2019). DOI: 10.1021/acs.jcim.9b00237.
- Heid E et al. "Chemprop: A Machine Learning Package for Chemical Property Prediction." *J. Chem. Inf. Model.* 64:9–17 (2024). DOI: 10.1021/acs.jcim.3c01250.
- Wu Z et al. "MoleculeNet: a benchmark for molecular machine learning." *Chem. Sci.* 9:513–530 (2018). DOI: 10.1039/C7SC02664A.
- Ross J, Belgodere B, Chenthamarakshan V, Padhi I, Mroueh Y, Das P. "Large-scale chemical language representations capture molecular structure and properties." *Nat. Mach. Intell.* 4:1256–1264 (2022). DOI: 10.1038/s42256-022-00580-7.
- Zhou G, Gao Z, Ding Q et al. "Uni-Mol: A Universal 3D Molecular Representation Learning Framework." *ICLR* (2023). OpenReview: https://openreview.net/forum?id=6K2RM6wVqKu.
- Ahmad W, Simon E, Chithrananda S, Grand G, Ramsundar B. "ChemBERTa-2: Towards Chemical Foundation Models." arXiv:2209.01712 (2022). DOI: 10.48550/arXiv.2209.01712.
- OECD. "The OECD Principles for the Validation, for Regulatory Purposes, of (Q)SAR Models" (agreed 2004); *Guidance Document on the Validation of (Quantitative) Structure-Activity Relationship [(Q)SAR] Models*, No. 69 (2007). DOI: 10.1787/9789264085442-en.
- Cortés-Ciriano I, Bender A. "Concepts and Applications of Conformal Prediction in Computational Drug Discovery." arXiv:1908.03569 (2019). DOI: 10.48550/arXiv.1908.03569.
- Svensson F et al. "Conformal Regression for Quantitative Structure–Activity Relationship Modeling—Quantifying Prediction Uncertainty." *J. Chem. Inf. Model.* 58:1132–1140 (2018). DOI: 10.1021/acs.jcim.8b00054.
- Chemprop 2.x CLI documentation, training and prediction: https://chemprop.readthedocs.io/en/latest/tutorial/cli/.
- MAPIE 0.8 documentation for the version-bounded `MapieRegressor` interface: https://mapie.readthedocs.io/en/v0.8.6/.

## Related Skills

- chemoinformatics/molecular-descriptors - Featurization choices
- chemoinformatics/molecular-standardization - Mandatory upstream
- chemoinformatics/scaffold-analysis - Bemis-Murcko split implementation
- chemoinformatics/admet-prediction - ADMET-specific QSAR
- chemoinformatics/generative-design - QSAR as scoring component
- machine-learning/model-validation - General ML validation principles
- machine-learning/biomarker-discovery - Adjacent ML approaches
<!-- END FILE: chemoinformatics/qsar-modeling/SKILL.md -->

## 子目录：chemoinformatics/reaction-enumeration

<!-- BEGIN FILE: chemoinformatics/reaction-enumeration/SKILL.md -->
---
name: bio-reaction-enumeration
description: Enumerates virtual chemical libraries via reaction SMARTS transformations using RDKit and reaction templates, with explicit handling of atom mapping, RDChiral template extraction, product validation, RECAP/BRICS fragmentation, R-group decomposition, matched molecular pair analysis (MMPA), and Free-Wilson analysis. Use when generating combinatorial libraries from building blocks, enumerating analog series, deriving structure-activity rules, or extracting transformations from reaction data.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, RDChiral 1.1+, mmpdb 3.1+, scikit-learn 1.4+, numpy 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Reaction Enumeration

Generate virtual libraries by applying reaction SMARTS to building blocks, enumerate analog series via matched molecular pairs, decompose into R-groups for SAR modeling, or extract transformations from reaction data. Reaction enumeration sits at the intersection of medicinal chemistry, lead optimization, and de novo design; DOGS is one published example of reaction-driven de novo design (Hartenfeller et al. 2012). The two key operations are **transform** (apply known reactions to make new compounds) and **mine** (extract rules from observed analog series). RDKit's reaction SMARTS handles the former; mmpdb / Free-Wilson handle analog-series analysis, while mapped-reaction template extraction requires separate tooling such as RDChiral.

For retrosynthetic planning (target-to-starting-material decomposition), see `chemoinformatics/retrosynthesis`. For ML-driven design, see `chemoinformatics/generative-design`. For scaffold-based design, see `chemoinformatics/scaffold-analysis`.

## Operation Taxonomy

| Operation | Goal | Tool | Fails when |
|-----------|------|------|------------|
| Forward enumeration | Apply reaction to building blocks -> products | RDKit `ReactionFromSmarts` + `RunReactants` | Wrong atom mapping; missing connectivity |
| Reverse enumeration (retrosynthesis) | Product -> starting materials | AiZynthFinder, Chemformer | See retrosynthesis skill |
| Template mining | Reaction database -> reaction SMARTS templates | RXNMapper + RDChiral | Atom mapping ambiguous; mechanism unclear |
| RECAP fragmentation | Molecule -> retro-synthetic fragments | RDKit `Chem.Recap` | Inflexible bond rules |
| BRICS fragmentation | Molecule -> retro-synthetic fragments | RDKit `BRICS` module | Many false fragments |
| R-group decomposition | Set of mols + scaffold -> R-group table | RDKit `Chem.rdRGroupDecomposition` | Multiple scaffolds; ambiguous attachment |
| Matched Molecular Pairs (MMPA) | Set of mols -> transformation rules | mmpdb | Sparse or context-confounded matched pairs |
| Free-Wilson | Compounds + activities -> additive R-group contributions | scikit-learn linear regression | Strict additivity assumption |

## Reaction SMARTS Basics

A reaction SMARTS is `reactants >> products` with atom maps `[atom:idx]` tracking atoms through the transformation:

```python
from rdkit import Chem
from rdkit.Chem import AllChem

amide = AllChem.ReactionFromSmarts(
    '[C:1](=[O:2])O.[N:3]>>[C:1](=[O:2])[N:3]'
)

errors = amide.Validate()
print(errors)
```

**Atom mapping rules:**
- Atoms with the same map index `[C:1]` in both reactant and product are tracked
- Maps must be unique within each reactant/product
- Atoms present in a reactant template but absent from the product template are removed; atoms present only in the product template are created
- Atoms outside the matched reaction-center template are generally carried through with their reactant molecule
- Bond orders may change; map index preserves identity

**Common error:** Missing or inconsistent maps for atoms intended to survive within the reaction center can delete atoms, create duplicates, or obscure which reactant atom a product atom represents. Mapping alone does not define the transformation; the reactant and product templates do.

## Common Reaction Templates

```python
REACTIONS = {
    'amide_coupling': '[C:1](=[O:2])O.[N:3]>>[C:1](=[O:2])[N:3]',
    'reductive_amination': '[C:1](=O).[NH2:2]>>[CH:1][NH:2]',
    'suzuki': '[c:1][Br].[c:2][B](O)O>>[c:1][c:2]',
    'buchwald_hartwig': '[c:1][Br].[NH:2]>>[c:1][N:2]',
    'sn2_substitution': '[CH:1][Br].[N:2]>>[CH:1][N:2]',
    'sonogashira': '[c:1][Br].[CH:2]#[C:3]>>[c:1][C:2]#[C:3]',
    'click_chemistry': '[N-:1]=[N+:2]=[N:3][CH2:4].[CH:5]#[C:6]>>[N:3]1[N:2]=[N:1][C:6]=[C:5]1[CH2:4]',
    'esterification': '[C:1](=[O:2])O.[OH:3][C:4]>>[C:1](=[O:2])[O:3][C:4]',
    'urea_formation': '[N:1]=C=O.[NH:2]>>[N:1]C(=O)[N:2]',
    'sulfonamide': '[S:1](=O)(=O)Cl.[NH:2]>>[S:1](=O)(=O)[N:2]',
}
```

These are illustrative templates; real reactions need stereo, protecting-group, and chemoselectivity considerations. For production library enumeration, use a separately curated and validated template collection, such as a vendor catalog. RXNMapper maps atoms in reaction records; it does not by itself supply or validate reaction templates.

## Combinatorial Library Enumeration

**Goal:** Generate every (R1, R2, ..., Rn) product combination from sets of building blocks.

**Approach:** Cartesian product of reactant lists; apply reaction SMARTS; sanitize + deduplicate.

```python
from itertools import product
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

def enumerate_library(rxn_smarts, reactant_lists, mw_max=600):
    rxn = AllChem.ReactionFromSmarts(rxn_smarts)
    num_warnings, num_errors = rxn.Validate()
    if num_errors:
        raise ValueError(f'Invalid reaction: {rxn_smarts}')

    seen = set()
    products = []
    for combo in product(*reactant_lists):
        mols = [Chem.MolFromSmiles(s) for s in combo]
        if None in mols:
            continue

        for prod_tuple in rxn.RunReactants(tuple(mols)):
            for prod in prod_tuple:
                try:
                    Chem.SanitizeMol(prod)
                    smi = Chem.MolToSmiles(prod)
                    if smi in seen:
                        continue
                    if Descriptors.MolWt(prod) > mw_max:
                        continue
                    seen.add(smi)
                    products.append(smi)
                except Exception:
                    continue
    return products
```

**Scaling:** For a 100x100x100 enumeration (1M products), parallelize with multiprocessing. For 1k x 1k x 1k (1B products), use a streaming approach + filter before materializing.

## RECAP Fragmentation

RECAP (Lewell 1998) breaks molecules at retrosynthetically reasonable bonds into reusable fragments.

```python
from rdkit.Chem import Recap

mol = Chem.MolFromSmiles('c1ccc(C(=O)Nc2ccc(F)cc2)cc1')
hier = Recap.RecapDecompose(mol)
fragments = list(hier.GetLeaves().keys())
```

RDKit's current `Recap.reactionDefs` contains 12 cleavage definitions. Inspect the installed definitions when exact coverage matters instead of relying on a shortened functional-group list. Use cases include building-block library generation and scaffold-decoration enumeration.

## BRICS Fragmentation

BRICS (Degen 2008) is an extension of RECAP with more bond types. Better fragment coverage; more fragments per molecule.

```python
from itertools import islice
from rdkit.Chem import BRICS

mol = Chem.MolFromSmiles('CCN(CC)c1ccc(C(=O)NC2CCCC2)cc1')
fragments = BRICS.BRICSDecompose(mol)

builder = BRICS.BRICSBuild([Chem.MolFromSmiles(f) for f in fragments])
new_mols = list(islice(builder, 10))
```

`BRICSDecompose` produces SMILES with isotope/environment-labeled dummy atoms such as `[1*]`, `[5*]`, and `[16*]`; `BRICSBuild` uses those labels when recombining compatible fragments.

## R-Group Decomposition

**Goal:** Given a set of compounds sharing a scaffold, extract the R-group at each attachment point into a tabular SAR matrix.

**Approach:** Define scaffold with `[*:1]`, `[*:2]` placeholders; RDKit matches each compound and extracts R-groups.

```python
from rdkit.Chem import rdRGroupDecomposition as rgd
from rdkit import Chem

scaffold = Chem.MolFromSmiles('c1ccc(-[*:1])cc1-[*:2]')

mols = [Chem.MolFromSmiles(smi) for smi in [
    'c1ccc(C)cc1F',
    'c1ccc(CC)cc1Cl',
    'c1ccc(CCC)cc1Br',
]]

decomp, _ = rgd.RGroupDecompose([scaffold], mols, asSmiles=True)
```

`decomp` is a list of dicts such as `{'Core': scaffold_smi, 'R1': r1_smi, 'R2': r2_smi}`. It does not contain assay values. Preserve compound identifiers and explicitly join the decomposition to the activity table before Free-Wilson analysis:

```python
import pandas as pd

compound_ids = ['cmpd-1', 'cmpd-2', 'cmpd-3']
activities = pd.DataFrame({
    'compound_id': compound_ids,
    'pIC50': [6.2, 6.8, 7.1],  # example measurements
})
decomp, unmatched = rgd.RGroupDecompose([scaffold], mols, asSmiles=True)
unmatched = set(unmatched)
matched_ids = [cid for i, cid in enumerate(compound_ids) if i not in unmatched]
decomp_df = pd.DataFrame(decomp)
decomp_df.insert(0, 'compound_id', matched_ids)
sar_table = decomp_df.merge(
    activities, on='compound_id', how='inner', validate='one_to_one'
)
```

## Matched Molecular Pairs Analysis (MMPA)

MMPA (Hussain & Rea 2010) extracts SAR rules from compound pairs differing by a single transformation.

```bash
mmpdb fragment data.smi -o data.fragments
mmpdb index data.fragments -o data.mmpdb
mmpdb transform --smiles 'COc1ccccc1' data.mmpdb
```

`mmpdb` produces a database of transformations + statistics on activity changes. The values below are synthetic examples showing the output schema; they are not observations from a cited dataset.

| Transformation | Avg delta(pIC50) | N pairs | Confidence |
|----------------|-------------------|---------|------------|
| Me -> F | +0.5 | 152 | high |
| OMe -> OH | -0.3 | 89 | moderate |
| Ph -> 4-pyridine | +1.2 | 23 | moderate |

**Use case:** Lead optimization. Given a hit, ask "what transformations have improved similar series?" Apply top-ranked transformations to generate analog suggestions.

**Context-based MMPA** conditions transformation statistics on local chemical context (for example, "Me -> F adjacent to an amide"). Raut and Dixit (2025) applied this approach to identify transformations associated with reduced CYP1A2 inhibition; that endpoint-specific result should not be generalized as universal superiority over classical MMPA.

## Free-Wilson Analysis

**Goal:** Decompose activity into additive R-group contributions.

**Approach:** Linear regression with R-group identity as binary features.

```python
import pandas as pd
from sklearn.linear_model import Ridge

def free_wilson(decomp_results, activity_col='pIC50'):
    df = pd.DataFrame(decomp_results)
    r_groups = pd.get_dummies(df[['R1', 'R2']], prefix=['R1', 'R2'])
    X = r_groups.values
    y = df[activity_col].values
    model = Ridge(alpha=0.1).fit(X, y)
    contributions = dict(zip(r_groups.columns, model.coef_))
    return contributions, model.intercept_
```

**Trade-off:** Free-Wilson assumes additivity (R1 contribution independent of R2). Real SAR has interactions; Free-Wilson predictions for un-synthesized combinations are biased when synergy exists. Use as a *first-pass model* for analog prioritization; validate with QSAR.

## Template Extraction from Reaction Data

**Goal:** Given an atom-mapped reaction SMILES, extract a generalizable SMARTS template.

**Approach:** Use `rxnmapper` (Schwaller et al. 2021) for atom mapping, then a template extractor such as RDChiral (Coley et al. 2019).

```python
from rxnmapper import RXNMapper

mapper = RXNMapper()
rxns = ['CCO.OC(=O)c1ccccc1>>CCOC(=O)c1ccccc1']
results = mapper.get_attention_guided_atom_maps(rxns)
mapped_smiles = results[0]['mapped_rxn']
```

RDKit does not provide a `ChemicalReaction.GetReactionTemplateFromMappedReaction` method. Pass the mapped reaction to RDChiral's published template-extraction workflow, checking the installed package's interface and expected reaction-record schema, or use a separately implemented and validated extractor.

## Per-Tool Failure Modes

### Reaction SMARTS -- atom mapping mismatch

**Trigger:** An atom intended to survive the reaction center is absent from, or inconsistently mapped in, the product template.

**Mechanism:** RDKit constructs products from the reaction templates. Reactant-template atoms omitted from the product template are deleted, product-only atoms are created, and inconsistent maps can prevent intended atom identity from being carried across the transformation.

**Symptom:** Products missing expected atoms; valences wrong; sanitize fails.

**Fix:** Validate with `rxn.Validate()`, inspect warnings separately from errors, and manually verify that every reaction-center atom intended to survive has one consistent map number on both sides.

### RECAP/BRICS -- over-fragmentation

**Trigger:** Highly substituted molecule with many breakable bonds.

**Mechanism:** Default bond list breaks at every retrosynthetic position; one molecule yields tens of fragments.

**Symptom:** Building-block enumeration explodes; many small irrelevant fragments.

**Fix:** Filter fragments by MW (>=80 Da), heavy atom count (>=4); use only meaningful fragments downstream.

### MMPA -- insufficient pair count

**Trigger:** The dataset yields few matched pairs for a transformation in the relevant chemical context.

**Mechanism:** Sparse or heterogeneous pairs give imprecise, context-confounded estimates. There is no universal minimum dataset size or pair count that guarantees a meaningful effect.

**Symptom:** Transformations report with N=1-3 pairs; effect sizes erratic.

**Fix:** Report pair counts and uncertainty, examine local contexts, use a project-justified precision threshold, and supplement with experimental or literature SAR knowledge.

### Free-Wilson -- non-additive interactions

**Trigger:** R1 and R2 interact through hydrogen bonding, steric clash, or electronic effects.

**Mechanism:** Free-Wilson is purely additive; cannot capture R1+R2 synergy.

**Symptom:** Predicted activities for un-synthesized combinations are biased low for synergistic pairs.

**Fix:** Use Free-Wilson as first-pass screen; validate predictions with QSAR (random forest, chemprop) which captures interactions.

### R-group decomposition -- multiple scaffolds

**Trigger:** Compound matches multiple scaffold templates.

**Mechanism:** RDKit accepts cores ordered from most to least specific and exposes parameters for multi-core matching and alignment. Ambiguous or inconsistently specified cores can change the resulting labels and SAR table.

**Symptom:** Same compound's R-groups differ between runs.

**Fix:** Order cores from most to least specific, label attachment points explicitly, inspect unmatched compounds, and keep a compound only when its selected core assignment matches the intended SAR series.

### Reaction enumeration -- combinatorial explosion

**Trigger:** Large building-block sets (1k x 1k = 1M products).

**Mechanism:** Cartesian product * RunReactants is O(N^d) where d is reactant count.

**Symptom:** Memory blowup, multi-hour runtime.

**Fix:** Pre-filter building blocks; stream products to file rather than list; use mmpdb-style sparse enumeration only for valid pairings.

## Reconciliation: Free-Wilson vs MMPA

Both methods derive R-group rules but from different perspectives:
- Free-Wilson: linear regression on assembled SAR table; gives R-group contributions
- MMPA: transformation-based; gives delta(activity) for each substitution

If they agree on direction (Me->F improves activity), high confidence. If they disagree, investigate non-additive interactions or look for context dependence in MMPA.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `rxn.Validate()` reports a nonzero error count | Bad atom mapping or invalid SMARTS | Unpack `(num_warnings, num_errors)` and reject on `num_errors`; inspect warnings separately |
| Products contain unexpected fragments | Reactants matched in unintended way | Use more specific SMARTS; constrain with explicit ring members |
| Sanitize fails on products | Reaction breaks valence | Filter via `Chem.SanitizeMol(prod, catchErrors=True)` |
| Duplicate products | Same product from different reactant orientations | Deduplicate by canonical SMILES |
| RECAP produces single fragment | Molecule has no retrosynthetic bonds | Try BRICS for more aggressive fragmentation |
| mmpdb empty output | No pairs satisfy the fragmentation, property, and context criteria | Inspect input parsing and fragmentation output; relax justified filters or obtain relevant analogues |
| R-group decomposition wrong R | Scaffold dummy not aligned | Re-check `[*:1]` / `[*:2]` placement |

## References

- Hartenfeller M et al. "DOGS: Reaction-Driven de novo Design of Bioactive Compounds." *PLoS Comput. Biol.* 8:e1002380 (2012). DOI: 10.1371/journal.pcbi.1002380.
- Lewell XQ, Judd DB, Watson SP, Hann MM. "RECAP—Retrosynthetic Combinatorial Analysis Procedure." *J. Chem. Inf. Comput. Sci.* 38:511–522 (1998). DOI: 10.1021/ci970429i.
- Degen J, Wegscheid-Gerlach C, Zaliani A, Rarey M. "On the Art of Compiling and Using 'Drug-Like' Chemical Fragment Spaces." *ChemMedChem* 3:1503–1507 (2008). DOI: 10.1002/cmdc.200800178.
- Hussain J, Rea C. "Computationally Efficient Algorithm to Identify Matched Molecular Pairs (MMPs) in Large Data Sets." *J. Chem. Inf. Model.* 50:339–348 (2010). DOI: 10.1021/ci900450m.
- Dossetter AG, Griffen EJ, Leach AG. "Matched molecular pair analysis in drug discovery." *Drug Discov. Today* 18:724–731 (2013). DOI: 10.1016/j.drudis.2013.03.003.
- Free SM, Wilson JW. "A Mathematical Contribution to Structure-Activity Studies." *J. Med. Chem.* 7:395–399 (1964). DOI: 10.1021/jm00334a001.
- Schwaller P et al. "Unsupervised attention-guided atom-mapping." *Sci. Adv.* 7:eabe4166 (2021). DOI: 10.1126/sciadv.abe4166.
- Raut JA, Dixit VA. "A context-based matched molecular pair analysis identifies structural transformations that reduce CYP1A2 inhibition." *RSC Med. Chem.* 16:3281–3290 (2025). DOI: 10.1039/D4MD01012D.
- Coley CW, Green WH, Jensen KF. "RDChiral: An RDKit Wrapper for Handling Stereochemistry in Retrosynthetic Template Extraction and Application." *J. Chem. Inf. Model.* 59:2529–2537 (2019). DOI: 10.1021/acs.jcim.9b00286.
- Dalke A, Hert J, Kramer C. "mmpdb: An Open-Source Matched Molecular Pair Platform for Large Multiproperty Data Sets." *J. Chem. Inf. Model.* 58:902–910 (2018). DOI: 10.1021/acs.jcim.8b00173.
- RDKit Book, reaction SMARTS and reaction handling: https://www.rdkit.org/docs/RDKit_Book.html.
- RDKit R-group decomposition API: https://www.rdkit.org/docs/source/rdkit.Chem.rdRGroupDecomposition.html.

## Related Skills

- chemoinformatics/molecular-io - Read/write reaction SMILES
- chemoinformatics/substructure-search - SMARTS pattern matching
- chemoinformatics/scaffold-analysis - Bemis-Murcko scaffolds for R-decomp
- chemoinformatics/molecular-descriptors - Featurize products
- chemoinformatics/admet-prediction - Filter enumerated products
- chemoinformatics/retrosynthesis - Reverse direction (target -> starting materials)
- chemoinformatics/generative-design - Generative alternatives to template enumeration
- chemoinformatics/qsar-modeling - Validate Free-Wilson predictions
<!-- END FILE: chemoinformatics/reaction-enumeration/SKILL.md -->

## 子目录：chemoinformatics/retrosynthesis

<!-- BEGIN FILE: chemoinformatics/retrosynthesis/SKILL.md -->
---
name: bio-retrosynthesis
description: Performs retrosynthetic planning using AiZynthFinder (template-based MCTS), maintained or version-pinned template-free models, ASKCOS, and emerging RetroSynFormer with explicit handling of route scoring, configurable MCTS rewards, building-block availability, and forward-prediction checks. Use when assessing synthetic feasibility of generated or selected molecules, planning multi-step syntheses, building synthesis-aware design pipelines, or screening libraries for retro-route feasibility.
tool_type: python
primary_tool: AiZynthFinder
---

## Version Compatibility

Reference examples tested with: AiZynthFinder 4.4+, RDKit 2024.09+, RDChiral 1.1+, and ASKCOS Lite 0.5+. Chemformer is archived legacy research code; if reproducing it, pin an exact repository commit, checkpoint, and configuration rather than assuming a current pip package or stable Python API.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `aizynthcli --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Retrosynthesis

Plan synthetic routes from a target molecule back to commercially available building blocks. AiZynthFinder combines Monte Carlo Tree Search (MCTS), template-based expansion, configurable search rewards, and route scorers (Saigiridharan et al. 2024). Chemformer is a published template-free transformer baseline whose official repository is now archived; use its exact historical environment for reproduction or select a maintained model with a documented interface. ASKCOS is another open-source synthesis-planning platform. A useful workflow combines retrosynthesis with building-block availability and an independently configured forward-prediction check, while recognizing that a round-trip model match is not experimental validation.

For generative design pipelines that need synthetic feasibility, see `chemoinformatics/generative-design`. For reaction enumeration (forward direction), see `chemoinformatics/reaction-enumeration`.

## Retrosynthesis Method Taxonomy

| Tool | Approach | Strength | Fails when |
|------|----------|----------|------------|
| AiZynthFinder 4.4+ | Template-based MCTS | Maintained, configurable open-source planner | Beyond selected policy coverage |
| Chemformer (archived) | Template-free transformer | Reproducing the published baseline | Archived code and checkpoint/config coupling |
| ASKCOS | Template-based + neural | Open-source synthesis-planning platform | Setup complexity |
| Molecular Transformer | Forward + retro transformer | Single SMILES-to-SMILES | Less robust to non-training distribution |
| RetroSynFormer | Decision transformer | Modern method | Limited adoption |

**Decision:** For most users, **AiZynthFinder with its documented public USPTO expansion policy and a current stock** is a practical open-source starting point. For high-stakes routes, apply expert review and an independently configured forward-prediction check; neither model agreement nor a solved search route is experimental validation.

## Decision Tree by Scenario

| Scenario | Tool | Notes |
|----------|------|-------|
| Standard medchem target | AiZynthFinder configured expansion policy | Record the public USPTO policy or licensed template source actually loaded |
| Novel chemotype | AiZynthFinder + maintained or exactly version-pinned template-free comparison | Validate each route independently |
| Generated molecules (REINVENT output) | AiZynthFinder batch | Filter to feasible routes |
| Multi-step synthesis planning | AiZynthFinder + manual review | Top-K routes |
| Validate generated route | Molecular Transformer forward | Check round-trip |
| Cost-aware synthesis | AiZynthFinder + custom building-block pricing | Score weight |
| Disconnection-aware design (DAD) | AiZynthFinder MCTS + verified rewards or post-search reranking | Compare route objectives explicitly |
| Patent-aware routes | Custom template exclusion | Specialized |

## AiZynthFinder Setup

**Goal:** Configure AiZynthFinder with USPTO templates + a building-block stock and run MCTS retrosynthesis planning on a target SMILES.

**Approach:** Create a version-appropriate YAML configuration with the expansion policy and stock, instantiate `AiZynthFinder` from that file, set the target SMILES, then call `tree_search()` followed by `build_routes()`. Use the schema documented for the installed release rather than copying legacy `policy` / `finder` dictionaries.

```python
from aizynthfinder.aizynthfinder import AiZynthFinder

finder = AiZynthFinder(configfile='config.yml')
finder.expansion_policy.select('uspto')  # key defined in config.yml
finder.stock.select('zinc')              # key defined in config.yml
# finder.filter_policy.select('uspto')   # optional configured filter
finder.target_smiles = 'CC(=O)Nc1ccc(C(=O)Nc2cccc(C(F)(F)F)c2)cc1'
finder.tree_search()
finder.build_routes()
```

Output: `finder.routes`, a `RouteCollection` containing ranked `reaction_trees`, initial `scores`, serialized route dictionaries, and route metadata.

## Route Output Analysis

```python
for tree, score in zip(finder.routes.reaction_trees, finder.routes.scores):
    leaves = list(tree.leafs())
    n_steps = len(list(tree.reactions()))
    print(f'Steps: {n_steps}, Score: {score}, Solved: {tree.is_solved}')
    print(f'In-stock: {sum(tree.in_stock(node) for node in leaves)} / {len(leaves)}')
    print(f'Building blocks: {[node.smiles for node in leaves]}')
```

Critical metrics:
- **Number of reactions**: count `tree.reactions()`; do not assume graph depth and reaction count are interchangeable for branched routes
- **Score**: interpret according to the configured scorer; scale and direction are scorer-specific
- **In-stock**: how many leaf nodes are commercially available
- **Solved state**: `tree.is_solved` is true only when all leaf nodes satisfy the configured stock criterion
- **Stock origin**: record the selected stock name, source snapshot, and access date

## Search Rewards and Route Scoring

AiZynthFinder retains the `mcts` search algorithm. It can combine configured search rewards through `search.algorithm_config.search_rewards` and corresponding weights, and it can rank completed routes with loaded scorers. There is no built-in `mo_mcts` algorithm or `finder.mo_mcts` configuration block. Available scorer names depend on the installed version, configuration, and plugins, so inspect the loaded scorers and use only documented names. If the desired objective is not available during search, export routes and rerank them explicitly after search.

## Building Block Stocks

| Stock source | Use | Required provenance |
|--------------|-----|---------------------|
| ZINC-derived snapshot | Publicly reproducible stock baseline | Download/source URL, filters, and snapshot date |
| Vendor building blocks | Purchase-oriented route termination | Vendor catalog version, region, and availability date |
| Make-on-demand catalog | Broader route termination | Catalog release, synthesis/lead-time assumptions, and access date |
| Custom internal stock | Organization-specific availability | Inclusion rules, identifiers, prices, and refresh date |

AiZynthFinder accepts HDF5 stocks built from plain-text SMILES with its documented `smiles2stock` command:
```bash
smiles2stock --files zinc_building_blocks.smi --output zinc.hdf5
```

## Forward Validation with Molecular Transformer

AiZynthFinder predicts retrosynthesis (target -> precursors), while a forward model predicts products from reactants. For each proposed reaction step, serialize reactants and reagents in the format expected by the installed forward model, request its ranked product predictions, and compare standardized product structures with the planned product. The Molecular Transformer literature does not define a universal `molecular_transformer.predict_forward` Python function, so use the documented interface of the chosen implementation. Report the observed top-k round-trip match rate for the model, reaction representation, and dataset; no universal 30–50% pass rate is established by the AiZynthFinder 4.0 paper.

## Template-Free with Chemformer

Chemformer uses a BART-style transformer trained on USPTO reactions for SMILES-to-SMILES prediction. Its official repository is archived and does not expose the `Chemformer.load_pretrained(...).predict(...)` convenience API sometimes shown in informal examples. To reproduce the published model, use the inference entry point, Hydra configuration, tokenizer, and checkpoint bundled with one pinned archived commit, and record that environment. For new work, prefer a maintained template-free implementation with a documented inference interface and benchmark it on the intended reaction domain.

**Trade-off:** A template-free model can propose disconnections outside a fixed template library, but its outputs require syntax checks, atom/reaction consistency checks, route-level review, and prospective validation. Treat it as a comparison or complementary hypothesis generator rather than assuming that merging its routes with AiZynthFinder is always superior.

## Disconnection-Aware Design (DAD)

Modify generative design to also score retrosynthetic feasibility with AiZynthFinder batch mode.

**Goal:** Add retrosynthetic feasibility scoring to generative design pipelines for hundreds-to-thousands of candidate molecules.

**Approach:** Batch-process generated SMILES through `aizynthcli`, use the reported solved state and number of reactions for each route, and feed a documented feasibility definition back into the generative scoring function.

```bash
aizynthcli --smiles compounds.smi --output routes.json \
           --config config.yaml --policy uspto --stocks zinc
```

For each compound, returns top-K routes. Score-feasibility for generative design:
- "Solved" = at least one extracted route has all leaves in the configured stock
- "Short solved route" = a solved route whose reaction count is below a project-defined threshold
- "Unsolved" = no extracted route is solved under the search budget and stock; this does not prove that the target is unsynthesizable

## Cost-Aware Synthesis

Add building-block pricing as objective:

```python
from rdkit import Chem

def route_cost(route, price_db):
    total = 0
    for leaf in route.leafs():
        smi = Chem.CanonSmiles(leaf.smiles)
        if smi not in price_db:
            raise KeyError(f'No observed building-block price for {smi}')
        total += price_db[smi]
    return total
```

Combine observed building-block prices with a project-specific reaction-cost model that documents labor, scale, yield, purification, and vendor assumptions. Do not apply a universal per-step cost.

## Per-Tool Failure Modes

### AiZynthFinder -- template coverage gap

**Trigger:** Target molecule uses bond formation not in training reactions.

**Mechanism:** USPTO templates are biased toward common transformations; novel chemistry (organometallics, exotic heterocycles) missing.

**Symptom:** No solved route or route uses unsuitable simplifications.

**Fix:** Use appropriately licensed additional templates, compare a maintained or exactly version-pinned template-free model, and perform manual review.

### Chemformer -- non-canonical SMILES output

**Trigger:** Default Chemformer output.

**Mechanism:** Transformer can produce non-canonical SMILES variants.

**Symptom:** SMILES round-trip fails; validation tools confused.

**Fix:** Canonicalize Chemformer output via RDKit before comparing.

### Route uses non-stock building block

**Trigger:** Leaf node not in stock database.

**Mechanism:** AiZynthFinder tree may end on non-purchasable molecules.

**Symptom:** Route "complete" but route has non-stock leaves.

**Fix:** Select routes whose `ReactionTree.is_solved` value is true, or explicitly require `tree.in_stock(leaf)` for every leaf. Expand the stock only when the additional availability definition is justified and versioned.

### MCTS iteration limit too low

**Trigger:** Complex target requiring deep tree search.

**Mechanism:** MCTS may not find route in default 100 iterations.

**Symptom:** No routes returned despite plausible target.

**Fix:** Increase and record the iteration or time budget in a controlled sensitivity analysis, inspect policy coverage and stock termination, and stop when additional search no longer changes the route conclusions. No fixed budget is universally adequate.

### Forward validation fails

**Trigger:** Retro route uses chemistry that doesn't actually work in forward.

**Mechanism:** Template-based retro lacks reaction conditions / catalysts; forward prediction more conservative.

**Symptom:** Forward predicts different product than target.

**Fix:** Use as confidence signal, not rejection; many routes don't round-trip but are still valid synthesis-wise.

### Building block stock obsolete

**Trigger:** Old ZINC catalog used; building blocks no longer purchasable.

**Mechanism:** Commercial catalogs and regional availability change over time.

**Symptom:** Routes recommend unavailable building blocks.

**Fix:** Refresh and date the selected stock snapshot, and verify vendor availability before synthesis.

## Reconciliation: AiZynthFinder vs Chemformer

| Aspect | AiZynthFinder | Chemformer |
|--------|---------------|------------|
| Approach | Templates + MCTS | Transformer encoder-decoder |
| Speed | Fast for shallow trees | Single-pass per target |
| Interpretability | High (template + atom mapping) | Low (black box) |
| Novel disconnections | Limited by selected templates | Can emit hypotheses outside a fixed template library, with no guarantee of validity |
| Production maturity | Maintained open-source package | Official repository archived; reproduce only with a pinned environment |
| Cost | CPU | GPU recommended |

If comparing both, standardize and validate their outputs independently before combining route hypotheses.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `tree_search()` returns no routes | Search budget, policy coverage, or stock criterion | Inspect each factor; compare a maintained or exactly version-pinned alternative |
| All extracted routes contain many reactions | Complex target or unsuitable disconnections | Compare scorer values and alternatives; review manually |
| Route appears solved but stock status is unclear | Reading node attributes instead of the route API, or stale stock provenance | Check `tree.is_solved` and `tree.in_stock(leaf)`; record the stock snapshot |
| Building block price not found | Compound not in pricing DB | Use Enamine quote or vendor inquiry |
| Chemformer truncates SMILES | Token limit | Increase max_length |
| Forward prediction wrong | Out-of-distribution reaction | Use as confidence signal only |
| MCTS slow on simple target | Default config | Reduce time_limit; use smaller template set |

## References

- Saigiridharan L, Hassen AK, Lai J, Torren-Peraire P, Engkvist O, Genheden S. "AiZynthFinder 4.0: developments based on learnings from 3 years of industrial application." *J. Cheminform.* 16:57 (2024). DOI: 10.1186/s13321-024-00860-x.
- Irwin R et al. "Chemformer: a pre-trained transformer for computational chemistry." *Mach. Learn.: Sci. Technol.* 3:015022 (2022). DOI: 10.1088/2632-2153/ac3ffb.
- Schwaller P et al. "Molecular Transformer: A Model for Uncertainty-Calibrated Chemical Reaction Prediction." *ACS Cent. Sci.* 5:1572–1583 (2019). DOI: 10.1021/acscentsci.9b00576.
- Tu Z et al. "ASKCOS: Open-Source, Data-Driven Synthesis Planning." *Acc. Chem. Res.* 58:1764–1775 (2025). DOI: 10.1021/acs.accounts.5c00155.
- Granqvist E, Mercado R, Genheden S. "Retrosynformer: planning multi-step chemical synthesis routes via a decision transformer." *Digital Discovery* 5:348–362 (2026). DOI: 10.1039/D5DD00153F.
- AiZynthFinder 4.4 Python interface and policy/stock selection: https://molecularai.github.io/aizynthfinder/python_interface.html.
- AiZynthFinder configuration documentation: https://molecularai.github.io/aizynthfinder/configuration.html.
- Chemformer official archived repository: https://github.com/MolecularAI/Chemformer.

## Related Skills

- chemoinformatics/molecular-io - Parse target and route SMILES
- chemoinformatics/molecular-standardization - Standardize before retrosynthesis
- chemoinformatics/generative-design - Add synthetic feasibility to scoring
- chemoinformatics/reaction-enumeration - Forward direction (template enumeration)
- chemoinformatics/admet-prediction - Filter targets before retrosynthesis
<!-- END FILE: chemoinformatics/retrosynthesis/SKILL.md -->

## 子目录：chemoinformatics/scaffold-analysis

<!-- BEGIN FILE: chemoinformatics/scaffold-analysis/SKILL.md -->
---
name: bio-scaffold-analysis
description: Analyzes chemical libraries by scaffold using Bemis-Murcko scaffolds, generic frameworks, cyclic skeletons, matched molecular pair (MMP) analysis via mmpdb, R-group decomposition, Free-Wilson analysis, scaffold hopping, and chemotype-aware ML train/test splits. Use when identifying chemotype clusters in a library, deriving SAR transformation rules, decomposing series into R-groups, performing scaffold-balanced QSAR splits, or planning analog campaigns.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, mmpdb 3.1+, scikit-learn 1.4+, datamol 0.12+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Scaffold Analysis

Analyze chemical libraries by their underlying scaffolds. Bemis-Murcko (1996) is the canonical scaffold decomposition: ring systems + linkers, with all R-groups stripped. Generic framework + cyclic skeleton are progressively-more-abstract views. Scaffold analysis underpins QSAR train/test splits (preventing data leakage), library diversity assessment, chemotype clustering, R-group decomposition for SAR modeling, and matched molecular pair analysis (MMPA). The choice of scaffold representation determines whether two compounds are "the same series" -- a critical decision for medicinal chemistry workflows.

For reaction-based enumeration and Free-Wilson, see `chemoinformatics/reaction-enumeration`. For scaffold-hopping via fingerprints, see `chemoinformatics/similarity-searching`. For 3D shape-based scaffold hopping, see `chemoinformatics/shape-similarity`.

## Scaffold Representation Taxonomy

| Representation | Origin | Definition | Use case | Fails when |
|----------------|--------|------------|----------|------------|
| Bemis-Murcko scaffold | Bemis & Murcko 1996 | Ring systems + linkers, R-groups stripped | Default chemotype identifier | Linear molecules (no rings) -> empty scaffold |
| Generic framework | Bemis & Murcko 1996 | Bemis-Murcko with all atoms set to C, all bonds single | Topology comparison | Loses heteroatom info |
| Cyclic skeleton (CSK) | Custom RDKit transformation | Ring atoms only, all C, all single | Pure ring-topology view | Loses linker info; not a built-in Murcko option |
| Murcko atom indices | Derived by matching the scaffold to the parent | Parent-molecule atom indices | Programmatic operations | Symmetry can yield multiple equivalent matches |

```python
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold

def all_scaffold_views(smi):
    mol = Chem.MolFromSmiles(smi)
    bm = MurckoScaffold.GetScaffoldForMol(mol)
    bm_smi = Chem.MolToSmiles(bm)

    generic = MurckoScaffold.MakeScaffoldGeneric(bm)
    generic_smi = Chem.MolToSmiles(generic)

    return {
        'bemis_murcko': bm_smi,
        'generic_framework': generic_smi,
    }
```

Example: `Cc1ccc(C(=O)NCC2CCCC2)cc1` -> Bemis-Murcko `c1ccc(C(=O)NCC2CCCC2)cc1`; generic `C1CCC(C(C)CCC2CCCC2)CC1` in current RDKit.

## Library Chemotype Clustering

**Goal:** Group compounds by shared Bemis-Murcko scaffold.

**Approach:** Compute scaffold for each compound; group by scaffold SMILES.

```python
from collections import defaultdict

def scaffold_clusters(smiles_list):
    clusters = defaultdict(list)
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        scaffold = MurckoScaffold.GetScaffoldForMol(mol)
        scaffold_smi = Chem.MolToSmiles(scaffold)
        clusters[scaffold_smi].append(smi)
    return clusters
```

Output: dict {scaffold_smiles: [compound_smiles, ...]}. Cluster sizes inform library diversity.

## Bemis-Murcko Scaffold Split (ML)

For QSAR / ML, random train/test split causes data leakage: compounds from the same chemotype (analogs in same series) end up in both. Bemis-Murcko split puts entire scaffolds in train or test, never both.

```python
from rdkit.Chem.Scaffolds import MurckoScaffold

def scaffold_split(df, smiles_col='smiles', train_frac=0.8, seed=42):
    import random
    rng = random.Random(seed)

    scaffolds = defaultdict(list)
    invalid_positions = []
    for pos, smi in enumerate(df[smiles_col].tolist()):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            invalid_positions.append(pos)
            continue
        scaff = Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(mol))
        scaffolds[scaff].append(pos)

    if invalid_positions:
        raise ValueError(f'Invalid SMILES at row positions: {invalid_positions}')

    scaffold_sets = list(scaffolds.values())
    rng.shuffle(scaffold_sets)
    scaffold_sets.sort(key=lambda x: len(x), reverse=True)

    n_total = sum(len(s) for s in scaffold_sets)
    n_train = int(n_total * train_frac)
    if len(scaffold_sets) < 2:
        raise ValueError('A scaffold split requires at least two scaffolds')
    train_idx = list(scaffold_sets[0])
    test_idx = []
    for i, scaff_set in enumerate(scaffold_sets[1:], start=1):
        if not test_idx and i == len(scaffold_sets) - 1:
            test_idx.extend(scaff_set)
        elif abs(len(train_idx) + len(scaff_set) - n_train) < abs(len(train_idx) - n_train):
            train_idx.extend(scaff_set)
        else:
            test_idx.extend(scaff_set)

    return df.iloc[train_idx], df.iloc[test_idx]
```

**Effect on benchmark metrics:** A scaffold split often produces different performance from a random split because it tests transfer across scaffold groups. The size and meaning of the gap are dataset- and deployment-dependent; it is not a direct universal measure of memorization.

**Caveat:** Bemis-Murcko split is *one* scaffold-split; for production ML, consider time split (newer compounds in test) or activity-cliff-balanced split.

**Class-imbalanced datasets:** Scaffold-only assignment can yield skewed class distributions. Chemprop's `scaffold_balanced` split balances scaffold-group sizes; it is not label-stratified. If both group isolation and label balance are required, use a validated group-aware stratification procedure such as `StratifiedGroupKFold` where its assumptions fit, then audit every fold for scaffold overlap and endpoint balance.

## R-Group Decomposition

**Goal:** Given a defined scaffold and a set of analog compounds, extract the R-group at each numbered attachment point into a tabular SAR matrix.

```python
from rdkit.Chem import rdRGroupDecomposition as rgd

def decompose_series(compounds, scaffold_smiles_with_R):
    scaffold = Chem.MolFromSmiles(scaffold_smiles_with_R)
    if scaffold is None:
        raise ValueError('Invalid scaffold SMARTS/SMILES')
    parsed = [(i, Chem.MolFromSmiles(s)) for i, s in enumerate(compounds)]
    invalid = [i for i, mol in parsed if mol is None]
    if invalid:
        raise ValueError(f'Invalid compound SMILES at positions: {invalid}')
    mols = [mol for _, mol in parsed]
    decomp, unmatched = rgd.RGroupDecompose([scaffold], mols, asSmiles=True)
    unmatched_set = set(unmatched)
    matched_positions = [i for i in range(len(mols)) if i not in unmatched_set]
    return decomp, matched_positions, list(unmatched)

scaffold = 'c1ccc(C(=O)N[*:1])cc1-[*:2]'
compounds = ['c1ccc(C(=O)NCC)cc1F', 'c1ccc(C(=O)NCCC)cc1Cl']
table = decompose_series(compounds, scaffold)
```

Output: list of {'Core': scaffold, 'R1': r1_smiles, 'R2': r2_smiles} dicts. Used for Free-Wilson analysis (see reaction-enumeration skill).

## Matched Molecular Pair Analysis (MMPA) via mmpdb

**Goal:** Mine a SAR dataset for substructure transformations and their associated activity changes.

**Approach:** Fragment all compounds into core + variable side; index pairs differing by one transformation; report delta(activity) per transformation.

```bash
mmpdb fragment data.smi -o data.fragments
mmpdb index data.fragments -o data.mmpdb
mmpdb transform --smiles 'COc1ccccc1' --property pIC50 data.mmpdb
```

Output: ranked transformations with delta(pIC50), N pairs, confidence.

Interpret transformation effects from pair count, chemical-context diversity, dependence among pairs, uncertainty intervals, and prospective validation. Do not convert a universal pair-count/effect-size table into reliability labels.

## Context-Based MMPA

Classical MMPA: "Me -> F always +0.5 log units."
Context-based MMPA: "Me -> F adjacent to amide is +0.5; Me -> F adjacent to ester is -0.1."

Matched-pair effects can depend strongly on the local chemical environment, so report the transformation together with its attachment-point context rather than treating a global mean as universal (Raut & Dixit 2025). Use mmpdb's stored environments or a custom stratified analysis to compare context-specific effects.

## Scaffold Hopping

**Goal:** Find compounds with different scaffold but similar 3D shape / pharmacophore / activity.

| Method | Approach | Tools |
|--------|----------|-------|
| 2D similarity with FCFP4 | Functional-class fingerprint Tanimoto | similarity-searching skill |
| 3D shape (ROCS) | Tanimoto on shape + color volumes | shape-similarity skill |
| Pharmacophore | Common pharmacophore features | pharmacophore-modeling skill |
| Maximum Common Substructure (MCS) | Largest shared substructure | similarity-searching skill (rdFMCS) |
| Deep scaffold hopping | Conditional molecular generation | DeepHop (Zheng et al. 2021) |

For systematic scaffold-hop discovery, combine:
1. Find target's bioactive series
2. Compute 3D pharmacophore from bound conformer
3. ROCS / pharmacophore search against vendor catalogs
4. Filter to compounds with Bemis-Murcko scaffold NOT in training data

## Series Detection

**Goal:** Identify "analog series" within a library -- compounds sharing a scaffold + co-varying R-groups.

```python
def detect_series(smiles_list, min_size=3):
    clusters = scaffold_clusters(smiles_list)
    series = {scaff: cmpds for scaff, cmpds in clusters.items()
              if len(cmpds) >= min_size}
    return series
```

Series counts depend on library provenance, standardization, scaffold definition, and minimum size. Report the observed distribution and use series as one possible unit for SAR analysis.

## Per-Tool Failure Modes

### Bemis-Murcko -- linear molecule yields empty

**Trigger:** Compound has no rings (e.g., fatty acid, simple amine).

**Mechanism:** Bemis-Murcko strips R-groups; no rings = nothing remains.

**Symptom:** Scaffold is empty string; molecules cluster together as "no scaffold".

**Fix:** For linear-rich libraries, augment with linear chain length / functional group features.

### Bemis-Murcko -- spiro / bridged ring confusion

**Trigger:** Compound has spiro or bridged ring system.

**Mechanism:** All ring atoms included; result is the entire ring system without R-groups.

**Symptom:** Apparently different drugs share a "scaffold" because of common spiro center.

**Fix:** Validate visually; use generic framework for topology-only comparison.

### Generic framework -- loses heteroatom info

**Trigger:** Distinguishing pyridine vs benzene scaffolds.

**Mechanism:** `MakeScaffoldGeneric` sets all atoms to C.

**Symptom:** Pyridine and benzene scaffolds reported as identical.

**Fix:** Use Bemis-Murcko (heteroatoms preserved); generic framework for topology only.

### Scaffold split -- imbalanced classes

**Trigger:** Library has many singletons + few large scaffolds.

**Mechanism:** Large scaffolds dominate; greedy assignment puts them in train.

**Symptom:** Test set is mostly singleton scaffolds; metrics misleading.

**Fix:** Use stratified scaffold split (balance test classes); or scaffold-balanced cross-validation.

### MMPA -- low pair count for novel transformations

**Trigger:** Transformation rare in dataset.

**Mechanism:** Need enough pairs to estimate delta(activity).

**Symptom:** Transformation reports N=2 with very large delta.

**Fix:** Report uncertainty and context diversity, avoid overinterpreting sparse transformations, and seek additional matched evidence where appropriate.

### R-group decomposition -- ambiguous match

**Trigger:** Multiple positions in scaffold could match same R-group.

**Mechanism:** Multiple core embeddings, symmetry, and unlabeled attachment choices can yield assignments that differ from the medicinal-chemistry convention.

**Symptom:** R1/R2 columns mixed up.

**Fix:** Specify labeled attachment points, inspect the returned rows and unmatched indices, and use `RGroupDecompositionParameters` for the intended matching/alignment behavior.

## Reconciliation: Scaffold Definition Disagreements

| Concept | Definition A | Definition B | Pick which |
|---------|--------------|--------------|------------|
| Bemis-Murcko scaffold | Atoms in rings + linkers | Same | RDKit default |
| Generic framework | All C, all single bonds | All C, original bonds | `MakeScaffoldGeneric` implements the first; preserve bond orders with an explicit custom transformation |
| Cyclic skeleton | Only ring atoms | Only ring atoms, generic | Implement explicitly; it is not an RDKit Murcko flag |
| "Series" | Same Bemis-Murcko | Tanimoto > 0.8 + same MW | Bemis-Murcko for SAR; Tanimoto for screening |

For ML splits: Bemis-Murcko. For library diversity: Bemis-Murcko + cluster size. For series detection: Bemis-Murcko + R-group decomposition.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Murcko scaffold includes unexpected linker atoms | Bemis-Murcko linkers connect ring systems by definition | Inspect the definition; for hierarchical networks use `rdScaffoldNetwork.ScaffoldNetworkParams` with `CreateScaffoldNetwork` |
| Singleton scaffolds dominate library | Aggressive standardization | Check for tautomer-induced scaffold variation; canonicalize first |
| R-group decomposition empty | Mol doesn't match scaffold | Use FMCS to find actual shared core |
| mmpdb missing transformations | Cores too restrictive | Try smaller core requirement |
| Scaffold split gives all to train | Few scaffolds; large clusters | Add singleton-spread strategy; use Murcko-and-Linker variant |
| Generic framework same for different drugs | Stripped heteroatom info | Use Bemis-Murcko (preserves heteroatoms) |
| MakeScaffoldGeneric error | RDKit version issue | RDKit 2024.09+ uses `Chem.Scaffolds.MurckoScaffold` |

## References

- Bemis GW, Murcko MA. *J. Med. Chem.* 39:2887-2893 (1996) -- original scaffold framework (DOI 10.1021/jm9602928).
- Hu, Stumpfe & Bajorath, *J. Med. Chem.* 60:1238-1246 (2017), DOI 10.1021/acs.jmedchem.6b01437 -- modern scaffold hopping review.
- Hussain J, Rea C. *J. Chem. Inf. Model.* 50:339-348 (2010) -- MMPA core method (DOI 10.1021/ci900450m).
- Raut & Dixit, *RSC Med. Chem.* 16:3281-3290 (2025), DOI 10.1039/D4MD01012D -- local-environment effects in matched molecular pairs.
- Zheng et al., *J. Cheminformatics* 13:87 (2021), DOI 10.1186/s13321-021-00565-5 -- DeepHop conditional scaffold hopping.
- Yang K et al., *J. Chem. Inf. Model.* 59:3370-3388 (2019) -- Chemprop molecular-property prediction (DOI 10.1021/acs.jcim.9b00237).
- RDKit R-group decomposition API: https://www.rdkit.org/docs/source/rdkit.Chem.rdRGroupDecomposition.html
- Chemprop splitting documentation: https://chemprop.readthedocs.io/en/main/tutorial/python/data/splitting.html

## Related Skills

- chemoinformatics/molecular-io - Parse compounds
- chemoinformatics/molecular-standardization - Standardize before scaffold extraction
- chemoinformatics/reaction-enumeration - Free-Wilson analysis on R-decomposition
- chemoinformatics/similarity-searching - 2D scaffold-hopping (FCFP4, AtomPair)
- chemoinformatics/shape-similarity - 3D scaffold-hopping
- chemoinformatics/qsar-modeling - Scaffold-aware splitting for QSAR
- chemoinformatics/generative-design - Scaffold-decoration generative tasks
<!-- END FILE: chemoinformatics/scaffold-analysis/SKILL.md -->

## 子目录：chemoinformatics/shape-similarity

<!-- BEGIN FILE: chemoinformatics/shape-similarity/SKILL.md -->
---
name: bio-shape-similarity
description: Performs 3D shape-based similarity searching using ROCS (OpenEye), USRCAT (ultra-fast), Open3DAlign (RDKit), ESPSim (electrostatic), and ShaEP with explicit handling of Tanimoto-Combo (shape + color), shape vs ECFP4 complementarity, conformer-ensemble searching, alignment optimization, and scaffold hopping. Use when searching for shape-mimicking compounds with different scaffolds, identifying bioisosteric replacements, prospective scaffold hopping, or expanding hit series beyond 2D similarity.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+ (Open3DAlign and USRCAT); official ShaEP syntax checked against ShaEP 1.4.2; ROCS/FastROCS/ROCS X are commercial OpenEye products.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Shape Similarity

Search for compounds with similar 3D shape (and optionally chemical features) to a query molecule. Shape-based screening complements 2D fingerprint search: it can find scaffold-hopped compounds that ECFP4 misses (different scaffolds with similar shape). ROCS (OpenEye) is the industry-standard commercial tool; Open3DAlign (RDKit), USRCAT (Schreyer & Blundell 2012), and ShaEP are open-source alternatives. Modern best practice combines shape with color (chemical-feature similarity) via Tanimoto-Combo: matches share both shape and pharmacophore feature distribution.

For 2D fingerprint similarity, see `chemoinformatics/similarity-searching`. For pharmacophore search (discrete feature constraints), see `chemoinformatics/pharmacophore-modeling`. For 3D conformer generation, see `chemoinformatics/conformer-generation`.

## Shape Method Taxonomy

| Tool | Speed | Approach | Open-source | Fails when |
|------|-------|----------|-------------|------------|
| ROCS / FastROCS (OpenEye) | Hardware/database/conformer-dependent; vendor reports millions of conformers/s for FastROCS | Gaussian shape + color | No | License and prepared database |
| ROCS X | Trillion-scale reaction/synthon space on Orion | FastROCS plus Bayesian-bandit sampling | No | Commercial cloud workflow |
| USRCAT | Very fast alignment-free descriptor comparison | Moment-based + atom types | Yes | Coarse approximation |
| Open3DAlign (RDKit) | Medium | MMFF atom-type/charge-weighted alignment | Yes | Requires compatible typed 3D structures |
| ShaEP | Benchmark on actual conformers/hardware | Field-based (shape + ESP) | Free binary; inspect license | Requires valid 3D structures and charges for ESP |
| ESPSim | Benchmark on actual workload | Electrostatic + shape | Yes | Limited public benchmarks |
| Phase-Shape (Schrödinger) | commercial | Shape + pharmacophore | No | Commercial |
| USR (original) | Very fast alignment-free comparison | Moment-based only | Yes | No atom-type information |

**Decision:** Select a shape method by matched retrieval/enrichment performance, conformer preparation, throughput, licensing, and score semantics. USRCAT is useful as a fast prefilter; Open3DAlign provides an open alignment method; ROCS/FastROCS provide commercial shape/color workflows.

## Decision Tree by Scenario

| Scenario | Method | Notes |
|----------|--------|-------|
| Large prepared library | USRCAT pre-filter + Open3DAlign rescore | Choose rescore budget from measured retrieval saturation |
| Production VS for scaffold hop | ROCS + color (commercial) | Industry standard |
| Scaffold hopping prospective | Open3DAlign with conformer ensemble | Shape + flexibility |
| Bioisostere replacement | ROCS color with neutral scoring | Pharmacophore-equivalent matches |
| Patent space carve-out | Shape constraint + 2D dissimilarity | Combine shape + dissimilar scaffold |
| Library diversity assessment | USRCAT k-nearest neighbor | Fast |
| Crystal-bound conformer template | Open3DAlign starting from co-crystal pose | Bioactive shape |
| Cross-target screening | Shape + pharmacophore feature | Combined screen |

## Tanimoto-Combo Scoring (ROCS Standard)

TanimotoCombo = Tanimoto_shape + Tanimoto_color

- Tanimoto_shape: volume overlap normalized
- Tanimoto_color: pharmacophore feature overlap

Each component is normalized from 0 to 1, so TanimotoCombo ranges from 0 to 2. It is a sum, not an average. Select follow-up thresholds from a relevant benchmark or enrichment study; a single cutoff is not portable across query preparation, color-force-field settings, and library composition.

## USRCAT (Ultra-Fast Shape Recognition + Atom Types)

USRCAT (Schreyer & Blundell 2012) extends Ultrafast Shape Recognition (USR) with atom-type information. Each molecule is represented as a 60-dimensional moment vector (12 moments × 5 atom types).

**Goal:** Encode a molecule into the 60-D USRCAT moment vector and score similarity against another molecule for alignment-free shape search.

**Approach:** Parse the SMILES, add hydrogens, generate one 3D conformer with ETKDGv3, compute RDKit USRCAT descriptors, and compare descriptor vectors with RDKit's USR score.

```python
from rdkit.Chem import rdMolDescriptors

mol = Chem.MolFromSmiles('CCO')
mol = Chem.AddHs(mol)
AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())

descriptors = rdMolDescriptors.GetUSRCAT(mol)
# Returns numpy array of 60 floats: 12 USR moments x 5 atom types
# (all atoms, hydrophobic, aromatic, acceptor, donor)

similarity = rdMolDescriptors.GetUSRScore(desc1, desc2)
```

**Speed:** Descriptor calculation is linear in atoms and comparison is fixed-length, without pairwise alignment. Benchmark end-to-end throughput on the prepared conformer library before choosing a scale cutoff.

**Limit:** USRCAT is a coarse approximation. Predictive for analog identification; less precise for scaffold hopping.

## Open3DAlign (RDKit)

Open3DAlign uses MMFF atom types and partial charges to find an atom-based 3D alignment:

**Goal:** Align a target molecule onto a query in 3D and score volume overlap with Open3DAlign.

**Approach:** Build 3D structures for query and target, run `GetO3A`, and call `Align()` to transform the probe in place. `Score()` is the unnormalized O3A objective, not a shape Tanimoto or ROCS TanimotoCombo. If a normalized shape similarity is required, compute `1 - rdShapeHelpers.ShapeTanimotoDist(...)` after alignment.

```python
from rdkit.Chem import rdMolAlign, rdShapeHelpers

query = Chem.MolFromSmiles('CCC(=O)Nc1ccccc1')
query = Chem.AddHs(query)
AllChem.EmbedMolecule(query, AllChem.ETKDGv3())

target = Chem.MolFromSmiles('CCC(=O)Nc1ccc(F)cc1')
target = Chem.AddHs(target)
AllChem.EmbedMolecule(target, AllChem.ETKDGv3())

O3A = rdMolAlign.GetO3A(target, query)
rmsd = O3A.Align()  # aligns target to query in place
o3a_score = O3A.Score()
shape_tanimoto = 1.0 - rdShapeHelpers.ShapeTanimotoDist(target, query)
```

`GetO3A` finds an alignment between conformers; `Align()` applies it and returns RMSD. Keep `o3a_score` and normalized `shape_tanimoto` distinct in outputs.

**Open3DAlign vs ROCS:** Open3DAlign is open-source and competitive on small benchmarks; slower than ROCS at scale.

## Conformer-Ensemble Shape Searching

For each library molecule, generate ensemble of conformers; pick best-shape conformer:

**Goal:** Run shape-similarity search over a conformer ensemble per library molecule so bound-conformer-like shapes are recovered.

**Approach:** For each library molecule, add hydrogens, embed n_conf conformers with ETKDGv3, MMFF-optimize, score each conformer against the query with Open3DAlign, and keep the best score per molecule.

```python
def shape_search_ensemble(query_mol, library_mols, n_conf=20):
    hits = []
    for target in library_mols:
        target = Chem.AddHs(target)
        ids = list(AllChem.EmbedMultipleConfs(target, numConfs=n_conf,
                                               params=AllChem.ETKDGv3()))
        if not ids:
            continue
        if not AllChem.MMFFHasAllMoleculeParams(target):
            continue
        optimization = AllChem.MMFFOptimizeMoleculeConfs(target)
        if any(status != 0 for status, _ in optimization):
            continue

        scores = []
        for c in range(target.GetNumConformers()):
            O3A = rdMolAlign.GetO3A(target, query_mol, prbCid=c)
            O3A.Align()
            scores.append(1.0 - rdShapeHelpers.ShapeTanimotoDist(
                target, query_mol, confId1=c,
            ))
        if scores:
            hits.append((target, max(scores)))
    return sorted(hits, key=lambda x: x[1], reverse=True)
```

**Critical:** Results depend on conformer coverage. Use an ensemble sized and validated for the library and query rather than assuming one conformer is representative.

## ESP Similarity (Electrostatic)

ShaEP and ESPSim extend shape with electrostatic surface potential overlap. For ESP-relevant pharmacophores (binding pockets with strong electrostatics):

```bash
shaep -q query.mol2 target.mol2 -s aligned_hits.sdf similarity.txt
```

ESP scoring catches electrostatic-equivalent bioisosteres that pure shape misses (carboxylate vs tetrazole same charge).

## Shape vs ECFP4 Complementarity

| Shape result | ECFP4 result | Interpretation |
|--------------|--------------|----------------|
| High | High | Close analog candidate |
| High | Low | Scaffold-hop candidate |
| Low | High | Similar 2D chemotype in a different sampled shape |
| Low | Low | Unrelated by these representations |

Calibrate “high” and “low” on a task-relevant reference set; do not treat the illustrative function defaults below as universal scientific cutoffs.

The shape >> ECFP4 quadrant is the scaffold-hopping gold:

**Goal:** Identify scaffold-hop candidates that are 3D-shape-similar but 2D-chemotype-dissimilar to the query.

**Approach:** Run the conformer-ensemble shape search, keep hits above a shape Tanimoto cutoff, then retain only those whose ECFP4 Tanimoto to the query is below an ECFP4 dissimilarity cutoff.

```python
# These thresholds are repository starting defaults only; calibrate both on a
# task-relevant active/decoy or retrieval benchmark before making decisions.
def scaffold_hop_candidates(query_mol, library, shape_threshold=0.7,
                            ecfp_threshold=0.5):
    shape_hits = shape_search_ensemble(query_mol, library)
    candidates = []
    for target, shape_score in shape_hits:
        if shape_score >= shape_threshold:
            ecfp_sim = ecfp_tanimoto(query_mol, target)
            if ecfp_sim < ecfp_threshold:
                candidates.append((target, shape_score, ecfp_sim))
    return candidates
```

## Per-Tool Failure Modes

### USRCAT -- false positive on small molecules

**Trigger:** Library has many fragment-sized compounds.

**Mechanism:** USRCAT moments dominated by overall shape; small molecules look "similar" if shape resemble.

**Symptom:** Many fragment hits; not pharmacophore-relevant.

**Fix:** Calibrate size/property filters on the retrieval task and rescore selected hits with an alignment or feature-aware method.

### Open3DAlign -- slow on large library

**Trigger:** Million-compound library, full alignment.

**Mechanism:** Open3DAlign is iterative; O(N) per molecule.

**Symptom:** Hours of compute.

**Fix:** Pre-filter with USRCAT and choose the rescore budget from measured throughput and retrieval saturation.

### Shape only -- wrong stereochemistry match

**Trigger:** Mirror-image of correct binder.

**Mechanism:** Shape-only scoring may insufficiently penalize stereochemical alternatives even though a rigid rotational overlay is not generally invariant to mirror reflection.

**Symptom:** Enantiomer of inactive scores as hit.

**Fix:** Validate hits by 3D pose; check stereochemistry.

### ROCS color -- bioisostere missed

**Trigger:** -COOH replaced by -SO3H or tetrazole.

**Mechanism:** Default color types may not equate these bioisosteres.

**Symptom:** Known bioisostere doesn't score high.

**Fix:** Validate the color-force-field treatment for the bioisostere and compare shape, color, and pharmacophore evidence separately.

### Conformer not bioactive

**Trigger:** Library compound generated conformer is not the bound conformation.

**Mechanism:** ETKDGv3 generates plausible conformers; bound conformer may be higher energy.

**Symptom:** Known active doesn't shape-match query.

**Fix:** Use larger conformer ensemble; weight by Boltzmann; or use CREST + GFN2-xTB for high-quality sampling.

### Field-based methods slower

**Trigger:** ShaEP or ESPSim on production library.

**Mechanism:** Field-based methods compute Gaussian fields per molecule.

**Symptom:** Field calculation or alignment dominates runtime on the prepared library.

**Fix:** Use as second-stage rescore; not primary screen.

## Reconciliation: Shape vs Pharmacophore

| Aspect | Shape | Pharmacophore |
|--------|-------|----------------|
| Representation | Volume distribution | Discrete features in space |
| Captures | Overall bulk | Interaction-relevant features |
| Speed | Fast (USRCAT) to medium (Open3DAlign) | Fast |
| Specificity | Task- and query-dependent | Task- and feature-definition-dependent |
| False positive rate | Measure on a matched benchmark | Measure on a matched benchmark |
| Best for | Scaffold hopping initial | Scaffold hopping refinement |

Shape and pharmacophore searches make different approximations. Compare them alone and in sequence on a matched active/decoy or retrieval benchmark before assigning recall/precision roles.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Open3DAlign RMSD is near 0 | Near-exact O3A alignment | Treat as a successful alignment; evaluate the O3A and shape scores separately |
| USRCAT vector all zeros | Mol has no 3D coords | Generate conformer first |
| Shape Tanimoto > 1 | Raw O3A or TanimotoCombo mislabeled as shape Tanimoto | Shape Tanimoto is 0-1; O3A is unnormalized and ROCS TanimotoCombo is 0-2 |
| ROCS very slow | Sequential processing | Use parallel batching |
| Shape match but no docking pose | Wrong binding pose | Use docking on top shape hits, not shape alone |
| Missing co-crystal template | Apo or AlphaFold-only structure | Use ligand-based pharmacophore + shape |
| ShaEP returns no hits | Strict tolerance | Loosen overlap thresholds |

## References

- Hawkins et al., *J. Med. Chem.* 50:74-82 (2007), DOI 10.1021/jm0603365 -- ROCS virtual-screening comparison.
- Schreyer AM, Blundell T. *J. Cheminformatics* 4:27 (2012) -- USRCAT (DOI 10.1186/1758-2946-4-27).
- Vainio, Puranen & Johnson, *J. Chem. Inf. Model.* 49:492-502 (2009), DOI 10.1021/ci800315d -- ShaEP.
- Tosco, Balle & Shiri, *J. Comput. Aided Mol. Des.* 25:777-783 (2011), DOI 10.1007/s10822-011-9462-9 -- Open3DALIGN.
- RDKit O3A API: https://www.rdkit.org/docs/source/rdkit.Chem.rdMolAlign.html
- RDKit shape API: https://www.rdkit.org/docs/source/rdkit.Chem.rdShapeHelpers.html
- ShaEP official documentation/examples: https://cheminformatics.fi/
- OpenEye ROCS X product documentation: https://www.eyesopen.com/rocsx

## Related Skills

- chemoinformatics/molecular-io - Parse query and library
- chemoinformatics/conformer-generation - Generate 3D conformer ensembles
- chemoinformatics/similarity-searching - 2D similarity comparison
- chemoinformatics/pharmacophore-modeling - Pharmacophore alternative
- chemoinformatics/scaffold-analysis - 2D scaffold analysis
- chemoinformatics/virtual-screening - Shape as pre-filter to docking
<!-- END FILE: chemoinformatics/shape-similarity/SKILL.md -->

## 子目录：chemoinformatics/similarity-searching

<!-- BEGIN FILE: chemoinformatics/similarity-searching/SKILL.md -->
---
name: bio-similarity-searching
description: Performs molecular similarity searching using Tanimoto, Tversky, Dice, and cosine coefficients on bit/count fingerprints with explicit choice rules for symmetric vs asymmetric measures, scaffold-hopping vs lead-optimization regimes, activity-cliff diagnosis, and large-library nearest-neighbor methods (BulkTanimoto, MHFP6 LSH forest, USRCAT). Use when ranking compounds by structural resemblance to a query, clustering libraries, finding analogs, or diagnosing activity cliffs.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+, scikit-learn 1.4+, mhfp 1.9+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Similarity Searching

Find structurally similar compounds and cluster libraries by similarity. The choice of similarity coefficient and fingerprint is **task-aware**: Tanimoto for symmetric similarity in lead optimization, Tversky for asymmetric "substructure-like" queries, Dice for higher sensitivity in low-similarity regimes, and MaxCommon Substructure (MCS) for scaffold-hopping. Tanimoto similarity above 0.7 is not a guarantee of activity preservation; activity cliffs (similar molecules with dissimilar activities) are common (Maggiora 2014).

For fingerprint choice, see `chemoinformatics/molecular-descriptors`. For 3D shape similarity, see `chemoinformatics/shape-similarity`.

## Similarity Coefficient Taxonomy

| Coefficient | Formula | Range | Symmetric | Use case | Fails when |
|-------------|---------|-------|-----------|----------|------------|
| Tanimoto | c / (a + b - c) | 0-1 | Yes | Default for ECFP4 similarity, ranking analogs | Saturates at low similarity (drug vs natural product) |
| Dice | 2c / (a + b) | 0-1 | Yes | Bit or nonnegative sparse-count vectors when Dice semantics are intended | Thresholds depend on vector type; analog choice subjective |
| Cosine (Ochiai) | c / sqrt(a*b) | 0-1 | Yes | Count vectors, weighted similarity | Not standard for bit vectors |
| Tversky alpha,beta | c / (alpha*(a-c) + beta*(b-c) + c) | 0-1 | No when alpha != beta | Asymmetric "is A a substructure of B" queries | Parameter choice subjective; alpha=1,beta=0 = substructure-like |
| Hamming | (a + b - 2c) / nBits | 0-1 | Yes | Binary bit vectors when bit-wise disagreement matters | Does not preserve count magnitude |
| Russell-Rao | c / nBits | 0-1 | Yes | Sparse fingerprints | Biased by fingerprint density |
| Kulczynski | (c/a + c/b) / 2 | 0-1 | Yes | When fingerprints have very different bit-density | Less standard |

Where a = set bits in fp1, b = set bits in fp2, c = bits in common.

## When to Use Which Coefficient

| Scenario | Coefficient | Why |
|----------|-------------|-----|
| Standard analog search (drug-like, ECFP4) | Tanimoto, start near 0.7 | Repository starting heuristic; calibrate against project actives and analog judgments |
| Sensitive search at lower similarity | Dice, threshold 0.45 | Dice is roughly 2*Tanimoto/(1+Tanimoto); more sensitive in middle range |
| Substructure-like ranking | Tversky alpha=1, beta=0 | Asymmetric: rewards compounds containing query features |
| Count fingerprints (neural, atom-environment) | Cosine | Bit-vector Tanimoto loses information |
| Activity-cliff diagnosis | Tanimoto + property difference | Detect ECFP4>=0.85 but |delta(activity)|>=2 log units |
| Cross-target / scaffold-hopping | FCFP4 Tanimoto OR AtomPair Tanimoto | Pharmacophore-equivalent matches different scaffolds |
| Metabolomics / natural products | MHFP6 Jaccard | ECFP4 saturates near 0.2 across diverse classes |
| 3D shape | Tanimoto on shape volume overlap | See shape-similarity skill |

## Tanimoto Thresholds (Repository Starting Heuristics)

| Threshold | Interpretation | Caveat |
|-----------|----------------|--------|
| >=0.85 | Likely same scaffold + close analog | Activity cliffs still possible |
| 0.70-0.85 | Same series, R-group variation | Standard "similar" threshold |
| 0.55-0.70 | Related chemotype, different decoration | Useful for series expansion |
| 0.35-0.55 | Distant analog, possible scaffold hop | Many false positives |
| <0.35 | Mostly noise; use 3D shape or pharmacophore instead | ECFP4 not informative |

These bands are working defaults for ECFP4-like fingerprints, not transferable calibration. Inspect the target dataset's similarity distribution and known series before setting a cutoff. Maggiora's similarity principle states "similar molecules tend to have similar activity" -- but **activity cliffs** (Stumpfe & Bajorath 2012) violate this. Treat high ECFP4 similarity as a prioritization signal, not evidence that activity will be preserved.

## Decision Tree by Scenario

| Goal | Workflow | Tools |
|------|----------|-------|
| Find analogs of a hit (lead opt) | ECFP4 Tanimoto >=0.7 search | RDKit `BulkTanimotoSimilarity` |
| Find scaffold hops | FCFP4 OR AtomPair Tanimoto >=0.5 + filter MCS | RDKit + rdFMCS |
| Cluster library by chemotype | Butina clustering at Tanimoto 0.6 cutoff | RDKit `Butina.ClusterData` |
| Diversity sampling | MaxMin selection on Tanimoto | RDKit `rdSimDivPickers.MaxMinPicker` |
| Nearest neighbors in >1M library | LSH forest with MHFP6 | `mhfp.lsh_forest.LSHForestHelper` |
| Activity cliff diagnosis | Tanimoto + pIC50 delta scatter | Custom analysis |
| 3D similarity (shape) | USRCAT / Open3DAlign / ROCS | shape-similarity skill |

## Tanimoto Similarity (single query, large library)

**Goal:** Rank a library by ECFP4 Tanimoto similarity to a query molecule, returning hits above a threshold.

**Approach:** Generate ECFP4 fingerprints for all molecules once, then use `BulkTanimotoSimilarity` for O(N) lookup.

```python
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

def precompute_fps(smiles_list, radius=2, nBits=2048):
    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=radius, fpSize=nBits)
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            fps.append(None)
        else:
            fps.append(generator.GetFingerprint(mol))
    return fps

def search(query_smi, library_fps, threshold=0.7):
    qmol = Chem.MolFromSmiles(query_smi)
    if qmol is None:
        raise ValueError('invalid query SMILES')
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    qfp = generator.GetFingerprint(qmol)
    valid = [(i, fp) for i, fp in enumerate(library_fps) if fp is not None]
    sims = DataStructs.BulkTanimotoSimilarity(qfp, [fp for _, fp in valid])
    return [(source_i, sim) for (source_i, _), sim in zip(valid, sims)
            if sim >= threshold]
```

## Tversky for Asymmetric Substructure-Like Search

**Goal:** Rank a library by how much each compound "contains" the features of the query (asymmetric).

**Approach:** Tversky with alpha=1, beta=0 rewards compounds containing query bits (substructure-like) while ignoring extra bits in the compound.

```python
from rdkit import DataStructs

def tversky_substructure_like(qfp, lib_fps, alpha=1.0, beta=0.0):
    return [DataStructs.TverskySimilarity(qfp, f, alpha, beta) for f in lib_fps if f]
```

Use case: identifying analogs that extend a pharmacophore vs. exact-similarity ranking.

## Butina Clustering

**Goal:** Group a library around Taylor-Butina centroids whose assigned neighbors are within the selected distance cutoff.

**Approach:** Compute upper-triangle distance matrix, apply Taylor-Butina with chosen distance cutoff.

```python
from rdkit.ML.Cluster import Butina

def cluster(mols, cutoff=0.4):
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [generator.GetFingerprint(m) for m in mols]
    n = len(fps)
    dists = []
    for i in range(1, n):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
        dists.extend([1 - s for s in sims])
    return Butina.ClusterData(dists, n, cutoff, isDistData=True)
```

`cutoff=0.4` means each assigned member was a neighbor of its selected centroid at Tanimoto >= 0.6. It does **not** guarantee that every pair of non-centroid members has Tanimoto >= 0.6. The first molecule in each returned cluster is the cluster centroid.

**Trade-off:** Butina materializes O(N^2) pairwise distances. Benchmark memory and runtime on the actual library; for much larger collections, use an approximate method such as an MHFP6 LSH forest.

## Diversity Selection (MaxMin)

**Goal:** Select N diverse compounds from a library by maximizing the minimum pairwise distance.

```python
from rdkit.SimDivFilters import rdSimDivPickers

picker = rdSimDivPickers.MaxMinPicker()
n_pick = 100
n_lib = len(fps)
selected = picker.LazyBitVectorPick(fps, n_lib, n_pick, seed=42)
```

`LazyBitVectorPick` is memory-efficient (does not materialize full distance matrix).

## Maximum Common Substructure

**Goal:** Find the largest substructure shared across a set of molecules.

**Approach:** `rdFMCS.FindMCS` with parameters controlling atom/bond equivalence.

```python
from rdkit.Chem import rdFMCS

def mcs_smarts(mols, timeout=60, ring_match='strict', atom_match='elements'):
    params = rdFMCS.MCSParameters()
    params.Timeout = timeout
    if ring_match == 'strict':
        params.BondCompareParameters.MatchFusedRings = True
        params.BondCompareParameters.MatchFusedRingsStrict = True
        params.BondCompareParameters.RingMatchesRingOnly = True
    if atom_match == 'elements':
        params.AtomCompareParameters.MatchValences = False
    result = rdFMCS.FindMCS(mols, params)
    return result.smartsString, result.numAtoms, result.numBonds
```

Use cases: identify scaffold across a series, build scaffold hopping queries, generate consensus pharmacophore.

**Limit:** MCS search can become combinatorial as input count, size, and structural divergence grow. Set a finite timeout, inspect `result.canceled`, and consider pre-clustering or reducing the comparison set; no molecule-count or atom-count boundary guarantees tractability.

## Activity Cliff Diagnosis

**Goal:** Detect pairs of similar molecules with dissimilar activities (cliffs).

**Approach:** Compute pairwise ECFP4 Tanimoto + pIC50 delta. Flag pairs with high similarity and large activity gap.

```python
def activity_cliffs(df, sim_threshold=0.85, activity_gap=2.0, activity_col='pIC50'):
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    mols = [Chem.MolFromSmiles(s) for s in df['smiles']]
    if any(mol is None for mol in mols):
        raise ValueError('activity-cliff input contains invalid SMILES')
    fps = [generator.GetFingerprint(mol) for mol in mols]
    cliffs = []
    for i in range(len(fps)):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[i+1:])
        for j_off, sim in enumerate(sims):
            j = i + 1 + j_off
            if sim >= sim_threshold:
                gap = abs(df[activity_col].iloc[i] - df[activity_col].iloc[j])
                if gap >= activity_gap:
                    cliffs.append((i, j, sim, gap))
    return cliffs
```

Activity cliffs flag (a) measurement noise, (b) cryptic SAR (e.g. ring-flip changing dihedral), (c) protein conformational selection, or (d) actually informative SAR. Cliffs are an opportunity for medchem investigation, not necessarily an error.

## Large-Library Nearest Neighbor (MHFP6 + LSH Forest)

For large libraries, direct all-pairs comparison becomes expensive. The `mhfp` package provides an LSH-forest helper for approximate nearest-neighbor retrieval over MHFP6 fingerprints. Measure recall and latency against an exact subset for the project dataset.

```python
from mhfp.encoder import MHFPEncoder
from mhfp.lsh_forest import LSHForestHelper

encoder = MHFPEncoder(2048)

def build_index(smiles_list):
    forest = LSHForestHelper()
    fingerprints = []
    for i, smiles in enumerate(smiles_list):
        fp = encoder.encode(smiles, radius=3)
        fingerprints.append(fp)
        forest.add(i, fp)
    forest.index()
    return forest, fingerprints

def query_index(forest, qmol, fingerprints, k=10):
    qfp = encoder.encode_mol(qmol, radius=3)
    return forest.query(qfp, k=k, data=fingerprints)
```

The returned neighbors are approximate in MHFP6 space. Benchmark them against an exact MHFP-distance search on a representative subset before choosing LSH parameters.

## Per-Tool Failure Modes

### ECFP4 Tanimoto -- saturation in diverse libraries

**Trigger:** Library spans drug-like + natural products + peptides + metabolites.

**Mechanism:** A local circular fingerprint may not preserve the distinctions needed for a particular mixed-modality retrieval task.

**Symptom:** Known relevant neighbors are not enriched above background, or retrieval metrics and neighborhood stability are poor on target-relevant controls. A low mean pairwise similarity alone is not a universal saturation test.

**Fix:** Benchmark ECFP4 against alternatives such as MHFP6 or MAP4 using held-out analog recovery, scaffold-aware retrieval, or another task-aligned metric. Do not transfer raw-score thresholds between fingerprint families.

### Butina clustering -- O(N^2) memory blowup

**Trigger:** Library >100k molecules.

**Mechanism:** Butina requires upper-triangle distance matrix, ~5e9 floats for 100k compounds.

**Symptom:** OOM error or hours of CPU.

**Fix:** Use approximate clustering (HDBSCAN on UMAP-reduced fingerprints) or LSH-based clustering on MHFP6.

### MCS -- exponential timeout

**Trigger:** Mol set with low overlap, large molecules, or many input mols.

**Mechanism:** MCS search is NP-hard; algorithm tries every atom-mapping permutation within timeout.

**Symptom:** Returns small partial MCS or empty result.

**Fix:** Raise `timeout`; reduce input mol count; pre-cluster by Tanimoto first then MCS within clusters.

### Tanimoto = 1.0 != same molecule

**Trigger:** Comparing fingerprints between two molecules that hash to the same bits.

**Mechanism:** A folded hashed fingerprint can map distinct atom environments to the same bits; collision frequency depends on molecule size, radius, and fingerprint length.

**Symptom:** Two structurally different molecules report Tanimoto 1.0.

**Fix:** For exact identity, compare canonical SMILES or InChIKey, not fingerprint. Use unhashed sparse fingerprint to disambiguate.

### Similarity threshold transfer fails

**Trigger:** Threshold tuned on ECFP4 applied to RDKit FP, AtomPair, or MACCS.

**Mechanism:** Bit-density and fragment-resolution differ; Tanimoto distributions shift.

**Symptom:** "Similar" set is much larger or smaller than expected.

**Fix:** Re-tune the threshold per fingerprint and dataset. AtomPair ~0.55, MACCS ~0.85, ECFP4 ~0.7, and FCFP4 ~0.6 are repository starting heuristics, not universal equivalents.

## Reconciliation: Cliffs Across Methods

If a pair flags as an activity cliff under one representation but not another, treat that as representation sensitivity. Inspect atom mappings, fingerprint environments, assay uncertainty, and the exact structural change; disagreement alone does not establish which substituent caused the activity difference.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `BulkTanimotoSimilarity` output is treated as bit counts | The API returns similarity values, normally floats | Keep the returned values as similarities; inspect input vector types if the output is unexpected |
| Reported similarity > 1 | Custom formula, malformed data, negative features, or an incorrectly normalized external implementation | Verify the coefficient definition and inputs; standard nonnegative RDKit Tanimoto and Tversky similarities are bounded by 1 |
| Cluster centroids change when input order changes | Taylor-Butina tie handling and assignment are order-sensitive | Standardize and sort inputs by a stable identifier before clustering; record `reordering` and the input order |
| MaxMinPicker returns first N inputs | All-zero initial similarity matrix | Seed picker explicitly: `picker.LazyBitVectorPick(fps, n_lib, n_pick, seed=42)` |
| Activity cliff "false positives" | Bit-collisions inflate similarity | Use sparse Morgan or compare canonical SMILES for exact ID |
| Diverse subset has duplicates | Standardization not applied | Canonicalize via `chemoinformatics/molecular-standardization` first |
| Tanimoto incompatible with neural fingerprint | Continuous-valued fingerprint | Use cosine or sklearn `cdist` with `'cosine'` metric |

## References

- Bajorath, *Nat. Rev. Drug Discov.* 1:882-894 (2002) -- integration of virtual and high-throughput screening. https://doi.org/10.1038/nrd941
- Maggiora et al., *J. Med. Chem.* 57:3186-3204 (2014) -- molecular similarity in drug discovery. https://doi.org/10.1021/jm401411z
- Stumpfe & Bajorath, *J. Med. Chem.* 55:2932-2942 (2012) -- activity cliffs. https://doi.org/10.1021/jm201706b
- Tversky, *Psychol. Rev.* 84:327-352 (1977) -- features of similarity (Tversky coefficient). https://doi.org/10.1037/0033-295X.84.4.327
- Probst & Reymond, *J. Cheminformatics* 10:66 (2018) -- MHFP6 MinHash fingerprint. https://doi.org/10.1186/s13321-018-0321-8
- O'Boyle & Sayle, *J. Cheminformatics* 8:36 (2016) -- fingerprint similarity benchmark. https://doi.org/10.1186/s13321-016-0148-0
- Butina, *J. Chem. Inf. Comput. Sci.* 39:747-750 (1999) -- Taylor-Butina clustering. https://doi.org/10.1021/ci9803381
- RDKit, `rdFMCS` API documentation -- MCS ring-comparison parameter names and semantics. https://www.rdkit.org/docs/source/rdkit.Chem.rdFMCS.html

## Related Skills

- chemoinformatics/molecular-descriptors - Generate fingerprints for similarity
- chemoinformatics/molecular-standardization - Canonicalize before comparing
- chemoinformatics/substructure-search - SMARTS pattern-based searching
- chemoinformatics/scaffold-analysis - Scaffold-based similarity (Bemis-Murcko, MMPA)
- chemoinformatics/shape-similarity - 3D shape similarity (USRCAT, ROCS)
- machine-learning/biomarker-discovery - ML on similarity features
<!-- END FILE: chemoinformatics/similarity-searching/SKILL.md -->

## 子目录：chemoinformatics/substructure-search

<!-- BEGIN FILE: chemoinformatics/substructure-search/SKILL.md -->
---
name: bio-substructure-search
description: Searches molecular libraries for substructure matches using SMARTS patterns with explicit handling of recursive SMARTS, ring membership, aromaticity dialect, vector binding, atom map indices, and reactive/PAINS/REOS/Brenk filter catalogs. Use when filtering compounds by pharmacophore features, functional groups, scaffold matches, or screening for assay-interference / structural alerts.
tool_type: python
primary_tool: RDKit
---

## Version Compatibility

Reference examples tested with: RDKit 2024.09+. SMARTS dialect follows Daylight specification with RDKit extensions.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show rdkit` then `help(rdkit.Chem.MolFromSmarts)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Substructure Search

Search molecular collections for structural patterns using SMARTS. The choice of SMARTS dialect, atom/bond matching mode, and structural-alert catalog determines whether the search is correctly capturing the intended chemistry. PAINS (Baell & Holloway 2010) is the most-cited but most-misunderstood filter -- it identifies patterns of assay interference, not "bad molecules". Knowing when to apply each catalog and how to interpret hits is essential.

For SMARTS-based reactions (transforming matched substructures), see `chemoinformatics/reaction-enumeration`. For 3D pharmacophore matching, see `chemoinformatics/pharmacophore-modeling`.

## SMARTS Grammar Essentials

| Token | Meaning | Example |
|-------|---------|---------|
| `[#6]` | Atom by atomic number | `[#6]` carbon (any hybridization) |
| `c` | Lowercase = aromatic | `c1ccccc1` benzene aromatic |
| `C` | Uppercase = aliphatic only | `C(=O)O` carboxylic acid carbon |
| `[CX4]` | Atom + connection count X | `[CX4]` sp3 carbon (4 connections) |
| `[CX3]=O` | Carbonyl (CX3 = sp2 with 3 bonds) | matches ketone, aldehyde, ester C |
| `[#6;R]` | Atom in ring | `[#6;R]` ring carbon |
| `[#6;!R]` | Atom not in ring | `[#6;!R]` acyclic carbon |
| `[#6;r6]` | Atom in 6-membered ring | `[#6;r6]` six-ring carbon |
| `[a]` | Any aromatic atom | `[a]` |
| `[!#1]` | Anything except H | `[!#1]` heavy atom |
| `[N;H2]` | N with exactly 2 H; neighboring chemistry unconstrained | `[NH2]` also matches non-amine `NH2` environments unless context is added |
| `[N+]` | Positively charged N | `[N+](=O)[O-]` nitro |
| `[$(...)]` | Recursive SMARTS | `[$(c1ccccc1)]` aromatic 6-ring atom |
| `[c]([F,Cl,Br,I])` | OR within brackets | aryl halide |
| `~` | Any bond type | `c~c` any aromatic-aromatic bond |
| `@` | Ring bond | `c@c` requires the matched bond to be in a ring |
| `-` | Single bond explicit | `C-C` |
| `=` | Double bond | `C=O` |
| `:` | Aromatic bond explicit | |

## Common SMARTS Patterns

| Pattern | SMARTS | Notes |
|---------|--------|-------|
| Hydroxyl (alcohol + phenol) | `[OX2H]` | OX2H avoids matching O- in OH- |
| Phenol only | `[OX2H][c]` | OH attached to aromatic carbon |
| Aliphatic OH only | `[OX2H][CX4]` | OH attached to sp3 C |
| Carboxylic acid | `[CX3](=O)[OX2H1]` | C(=O)OH |
| Carboxylate | `[CX3](=O)[O-]` | C(=O)O- (deprotonated) |
| Ester | `[CX3](=O)[OX2][!H]` | C(=O)O-R |
| Amide | `[CX3](=[OX1])[NX3]` | C(=O)N-R |
| Primary amine attached to carbon (excluding common amide-like N) | `[NX3;H2;$(N-[#6]);!$(N-[C,S,P]=[O,S,N])]` | Carbon-substituted -NH2; extend the exclusions for a project-specific amine definition |
| Secondary amine attached to two carbons | `[NX3;H1;$(N(-[#6])-[#6]);!$(N-[C,S,P]=[O,S,N])]` | Carbon-substituted -NH- excluding common amide-like N |
| Neutral tertiary amine attached to three carbons | `[NX3;H0;+0;$(N(-[#6])(-[#6])-[#6]);!$(N-[C,S,P]=[O,S,N])]` | Carbon-substituted -NR2 excluding common amide-like N |
| Quaternary amine | `[NX4+]` | -NR4+ |
| Nitro | `[N+](=O)[O-]` | -NO2 |
| Nitrile | `[CX2]#[NX1]` | -C#N |
| Sulfonamide | `[SX4](=[OX1])(=[OX1])[NX3]` | -S(=O)(=O)N |
| Aryl halide | `[c][F,Cl,Br,I]` | halogen on aromatic |
| Aliphatic halide | `[CX4][F,Cl,Br,I]` | halogen on sp3 C |
| Hydrogen bond donor | Use a named feature definition such as RDKit `BaseFeatures.fdef` or `Lipinski.NumHDonors` | `[#7,#8;!H0]` is only a simplified N/O-H query and is not a universal HBD model |
| Hydrogen bond acceptor | Use a named feature definition such as RDKit `BaseFeatures.fdef` or `Lipinski.NumHAcceptors` | No short universal SMARTS correctly captures every accepted HBA chemistry model |
| Michael acceptor | `[CX3]=[CX3][CX3]=O` | enone, acrylamide warhead |
| Aldehyde | `[CX3H1](=O)` | -CHO |
| Ketone | `[CX3;H0](=[OX1])([#6])[#6]` | Carbonyl carbon has two carbon substituents and no hydrogen |

## Basic Substructure Match

**Goal:** Test whether a molecule contains a SMARTS pattern and enumerate the matching atom indices.

**Approach:** Parse the molecule with `MolFromSmiles` and the pattern with `MolFromSmarts`, gate with `HasSubstructMatch`, then call `GetSubstructMatches` and map each atom index back to the molecule for inspection.

```python
from rdkit import Chem

mol = Chem.MolFromSmiles('c1ccc(O)cc1CCO')
pattern = Chem.MolFromSmarts('[OX2H]')

if mol.HasSubstructMatch(pattern):
    matches = mol.GetSubstructMatches(pattern)
    for match in matches:
        atoms = [mol.GetAtomWithIdx(i).GetSymbol() for i in match]
```

`HasSubstructMatch` returns bool, `GetSubstructMatches` returns tuple of tuples of atom indices.

## Recursive SMARTS for Context-Aware Patterns

`[$(pattern)]` matches an atom that *also* matches the entire pattern starting from itself. Critical for context-aware matching.

```python
# Aromatic carbon attached to a carbonyl
pat = Chem.MolFromSmarts('[$(c[C](=O))]')

# Aniline-type N (aromatic carbon-N-H)
pat = Chem.MolFromSmarts('[$([NX3;H2][c])]')

# Neutral tertiary amine with three sp3-carbon neighbors
pat = Chem.MolFromSmarts('[$([NX3]([CX4])([CX4])[CX4])]')

# H-bond donor (per Lipinski, exclude quaternary)
hbd = Chem.MolFromSmarts('[#7,#8;!H0;!$([NX3+])]')

# For H-bond acceptors, use RDKit's maintained Lipinski/feature definitions
# instead of an ad hoc universal SMARTS.
from rdkit.Chem import Lipinski
n_acceptors = Lipinski.NumHAcceptors(mol)
```

## Structural-Alert Filter Catalogs

| Filter | Origin | Patterns | Use case | Failure mode |
|--------|--------|----------|----------|--------------|
| PAINS_A | Baell & Holloway 2010 | 16 | Most populated source-data patterns (>=150 analogues per pattern) | Many false positives in primary screens; legitimate medicines flagged |
| PAINS_B | Baell & Holloway 2010 | 55 | Intermediate source-data population (15-149 analogues per pattern) | Similar |
| PAINS_C | Baell & Holloway 2010 | 409 | Least populated source-data patterns (1-14 analogues per pattern) | Most permissive |
| BRENK | Brenk 2008 (DDS unsuitable) | 105 | Reactive / toxicity / undesirable | Useful for fragment / virtual library |
| NIH | NIH MLSMR | 180 in RDKit 2024.09 | Reactive groups, unstable | Legacy filter; verify count after toolkit upgrades |
| ZINC | ZINC clean-leads | 50 in RDKit 2024.09 | Drug-like cleanup | Verify definitions after toolkit upgrades |
| Glaxo / Eli Lilly | Vendor lists | varies | Internal "ugly" filters | Often unpublished |
| REOS | Walters & Murcko 2002 | property + structural | Drug-likeness combined filter | Hand-curated thresholds |

The PAINS A/B/C families encode pattern population in the original screening dataset, not increasing or decreasing external evidence strength.

## When to Apply Each Filter

| Scenario | Catalog | Reason |
|----------|---------|--------|
| Hit validation from biochemical screen | PAINS_A | Identify assay-interference candidates |
| Library prep for HTS | PAINS_A + Brenk + ZINC | Remove clearly bad |
| Fragment library design | Brenk + ZINC | Remove reactive; PAINS less critical at fragments |
| Lead optimization | None mandatory | Filters can exclude valid leads |
| Natural product analog | None | Filters trained on synthetic chemistry |
| Covalent inhibitor design | Skip warhead filter | Warheads ARE the design |

**Critical:** Capuzzi et al. (2017) found PAINS alerts in 87 FDA-approved small-molecule drugs. PAINS is a *flag for assay validation*, not a *killing filter*.

## PAINS Filter

**Goal:** Split a molecule list into PAINS-flagged and PAINS-clean sets using one or more PAINS catalog tiers.

**Approach:** Configure `FilterCatalogParams` with the requested catalog enums, build a `FilterCatalog` once, and for each molecule use `GetFirstMatch` to either bucket it as clean or record the matching pattern description.

```python
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

def pains_filter(mols, catalogs=('PAINS_A',)):
    params = FilterCatalogParams()
    for cat in catalogs:
        params.AddCatalog(getattr(FilterCatalogParams.FilterCatalogs, cat))
    catalog = FilterCatalog(params)

    flagged = []
    clean = []
    for mol in mols:
        if mol is None:
            continue
        entry = catalog.GetFirstMatch(mol)
        if entry is None:
            clean.append(mol)
        else:
            flagged.append((mol, entry.GetDescription()))
    return clean, flagged
```

Available catalog names: `PAINS_A`, `PAINS_B`, `PAINS_C`, `PAINS` (all), `BRENK`, `NIH`, `ZINC`, `ALL`.

## Reaction-Reactive Group Filter (custom)

For HTS triage, filter electrophilic warheads (acrylamide, chloroacetamide, etc.) unless designing covalent inhibitors.

**Goal:** Flag molecules containing electrophilic warheads or other reactive functional groups that would interfere with biochemical HTS.

**Approach:** Maintain a named SMARTS dictionary of reactive groups (acid halides, epoxides, Michael acceptors, etc.), then per molecule scan each pattern with `HasSubstructMatch` and return the first matching warhead name.

```python
REACTIVE_SMARTS = {
    'acid_anhydride': '[CX3](=O)O[CX3](=O)',
    'acid_halide': '[CX3](=O)[F,Cl,Br,I]',
    'alpha_halo_carbonyl': '[CX3](=O)C([F,Cl,Br,I])',
    'aldehyde_reactive': '[CX3H1](=O)[#6;X4]',  # aliphatic aldehydes
    'epoxide': 'C1OC1',
    'aziridine': 'C1NC1',
    'isocyanate': '[NX2]=C=[OX1]',
    'isothiocyanate': '[NX2]=C=[SX1]',
    'beta_lactam': 'C1(=O)NCC1',
    'sulfonyl_halide': '[SX4](=O)(=O)[F,Cl,Br,I]',
    'Michael_acceptor': '[CX3]=[CX3][CX3]=O',
    'vinyl_sulfone': '[SX4](=O)(=O)C=C',
}

def reactive_filter(mol, exclude_warheads=True):
    if not exclude_warheads:
        return False, None
    for name, smarts in REACTIVE_SMARTS.items():
        if mol.HasSubstructMatch(Chem.MolFromSmarts(smarts)):
            return True, name
    return False, None
```

For covalent-inhibitor design, see `chemoinformatics/covalent-design`; these warheads are the desired chemistry, not noise to filter.

## Library Filtering with Multiple Patterns

**Goal:** Reduce a molecule library to those that match all required SMARTS patterns and none of the excluded ones.

**Approach:** Start from the full molecule list, iteratively intersect with each `include` SMARTS using `HasSubstructMatch`, then subtract any molecule matching an `exclude` SMARTS.

```python
def filter_library(mols, include=None, exclude=None):
    keep = list(mols)
    if include:
        for s in include:
            p = Chem.MolFromSmarts(s)
            keep = [m for m in keep if m and m.HasSubstructMatch(p)]
    if exclude:
        for s in exclude:
            p = Chem.MolFromSmarts(s)
            keep = [m for m in keep if m and not m.HasSubstructMatch(p)]
    return keep
```

## Atom Map Indices in SMARTS

Atom maps `[C:1]` track atoms through transformations. Used in reactions (`reaction-enumeration` skill) but also for substructure-based extraction:

```python
# Find amide N with attached aryl
pat = Chem.MolFromSmarts('[CX3:1](=O)[NX3:2][c:3]')
match = mol.GetSubstructMatch(pat)

amide_C, amide_N, aryl_C = match
```

## Per-Tool Failure Modes

### PAINS -- false positive on natural product

**Trigger:** Library contains natural products, polyphenols, flavonoids, quinones.

**Mechanism:** PAINS_A patterns target rhodanines, curcumins, polyhydroxylated polyphenols -- legitimate scaffolds in natural-product chemistry.

**Symptom:** Library hits flagged as PAINS but trace back to validated natural products with confirmed activity.

**Fix:** Use PAINS as a *flag* not a *delete*. Cross-check flagged compounds for orthogonal-assay confirmation (label-free e.g. SPR, ITC).

### Aromaticity dialect mismatch

**Trigger:** SMARTS pattern with `c` (aromatic) for a heteroatom-rich ring; molecule parsed with different aromaticity model.

**Mechanism:** RDKit, OpenEye, ChemAxon differ on whether furan, thiazole, tropone, etc. are aromatic.

**Symptom:** Same pattern matches in one toolkit, not in another.

**Fix:** Re-canonicalize molecules within RDKit before applying SMARTS. Or use `[#6]:[#6]` instead of `c:c` (explicit element + bond type).

### Tautomer-sensitive pattern miss

**Trigger:** SMARTS targets keto form `C(=O)` but molecule is enol `C(O)=C`.

**Mechanism:** Default canonical form differs by toolkit + standardization choice.

**Symptom:** Known matching molecule reports no match.

**Fix:** Use tautomer-aware match: enumerate tautomers and OR-match. Or canonicalize first via `chemoinformatics/molecular-standardization`. Or expand pattern with `[$(C(=O)),$(C(O)=C)]`.

### Stereochemistry ignored

**Trigger:** SMARTS without `/\@` stereo markers applied to mol with explicit stereo.

**Mechanism:** SMARTS matching is stereo-agnostic by default.

**Symptom:** Wrong stereoisomer is matched as well as right one.

**Fix:** `mol.GetSubstructMatches(pattern, useChirality=True)` to require chirality match.

### Ring closure / fused-ring specificity

**Trigger:** A query must distinguish an isolated benzene ring from a six-membered aromatic ring embedded in a fused system.

**Mechanism:** `c1ccccc1` matches six-membered aromatic cycles and therefore does match benzene cycles within naphthalene. Extra ring-membership or fusion constraints are required to exclude fused systems.

**Symptom:** A nominal "benzene" query returns fused polyaromatics that the project intended to exclude.

**Fix:** Keep `c1ccccc1` when any aromatic six-cycle is desired. When an isolated ring is required, add explicit ring-degree/fusion constraints and test the query against benzene, naphthalene, indole, and representative substituted controls.

### Recursive SMARTS performance

**Trigger:** Deeply nested recursive SMARTS over a large library.

**Mechanism:** Each `[$()]` re-evaluates the inner pattern for every candidate atom.

**Symptom:** Search 10x-100x slower than expected.

**Fix:** Flatten recursion where possible; pre-filter with simpler pattern, then re-test with the recursive one.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Chem.MolFromSmarts` returns None | Invalid SMARTS grammar | Validate with `Chem.MolFromSmarts(smi, mergeHs=False)`; check parens, brackets |
| `[OH]` gives unexpected hydroxyl matches | Query does not state the intended valence/connectivity model | Use `[OX2H]` for neutral alcohol/phenol oxygen or a more specific context-aware pattern |
| Pattern matches but library is "empty" | Mol failed sanitize | Try `Chem.SDMolSupplier(sanitize=False)` then catch errors |
| Multiple matches per molecule | Single-match query expected | `GetSubstructMatch` returns first; `GetSubstructMatches` returns all |
| Match indices but no fragment | Match returns atom indices in pattern order | Map to original mol via `mol.GetAtomWithIdx(i)` |
| PAINS catalog initialization slow | Loading 1000+ patterns on every call | Build catalog once, reuse for batch |
| Stereo SMARTS not matching | `useChirality=False` (default) | `mol.GetSubstructMatches(p, useChirality=True)` |

## References

- Baell & Holloway, *J. Med. Chem.* 53:2719-2740 (2010) -- original PAINS filter and tier evidence. https://doi.org/10.1021/jm901137j
- Capuzzi et al., *J. Chem. Inf. Model.* 57:417-427 (2017) -- PAINS reality check (FDA drug overlap). https://doi.org/10.1021/acs.jcim.6b00465
- Brenk et al., *ChemMedChem* 3:435-444 (2008) -- structural alerts (BRENK filter). https://doi.org/10.1002/cmdc.200700139
- Walters & Murcko, *Adv. Drug Deliv. Rev.* 54:255-271 (2002) -- drug-likeness filtering, including REOS. https://doi.org/10.1016/S0169-409X(02)00003-0
- Bruns & Watson, *J. Med. Chem.* 55:9763-9772 (2012) -- Eli Lilly medchem rules. https://doi.org/10.1021/jm301008n
- Daylight Chemical Information Systems, SMARTS theory documentation -- complete grammar reference. https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html

## Related Skills

- chemoinformatics/molecular-io - Parse molecules before searching
- chemoinformatics/molecular-standardization - Canonicalize tautomers before SMARTS
- chemoinformatics/similarity-searching - Fingerprint-based fuzzy matching
- chemoinformatics/scaffold-analysis - Scaffold-based pattern derivation
- chemoinformatics/reaction-enumeration - SMARTS for chemical transformations
- chemoinformatics/admet-prediction - PAINS as ADMET filter
- chemoinformatics/covalent-design - Warhead chemistry
<!-- END FILE: chemoinformatics/substructure-search/SKILL.md -->

## 子目录：chemoinformatics/virtual-screening

<!-- BEGIN FILE: chemoinformatics/virtual-screening/SKILL.md -->
---
name: bio-virtual-screening
description: Performs structure-based virtual screening using AutoDock Vina, SMINA, GNINA (CNN scoring), and DiffDock-L hybrid workflows with explicit choice rules across rigid vs flexible docking, cross-docking vs self-docking, binding-site detection (P2Rank, fpocket), receptor preparation (PDB2PQR, PROPKA), ligand preparation (meeko, OpenBabel), and ultralarge-library screening (ZINC22, Enamine REAL). Use when screening chemical libraries against a protein target to find candidate binders, ranking docking poses, or selecting a docking workflow for a specific scenario.
tool_type: python
primary_tool: AutoDock Vina
---

## Version Compatibility

Reference examples tested with: AutoDock Vina 1.2.5+, SMINA 2020-12+, GNINA 1.1+ for `rescore` (GNINA 1.3+ for the six-mode interface documented below), RDKit 2024.09+, meeko 0.5+, P2Rank 2.4+, ProDy 2.4+, pdb2pqr 3.6+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `vina --version`; `gnina --version`; `smina --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Virtual Screening

Screen chemical libraries against protein targets via molecular docking. Vina is the de-facto default, SMINA adds flexibility (Vinardo scoring, custom scoring), and GNINA adds CNN-based pose scoring (Top-1 redock 58%->73% over Vina, cross-dock 27%->37%). Deep-learning docking (DiffDock-L, EquiBind, NeuralPLexer) competes in pose accuracy, but physical validity is method- and dataset-dependent; the workflow therefore combines ML pose sampling with classical scoring and explicit geometry checks. For ultralarge libraries (>1M), library preparation, hierarchical filtering, and HPC orchestration become the limiting steps.

For pose physical-validity QC, see `chemoinformatics/pose-validation`. For ML-driven docking + rescoring, see `chemoinformatics/ml-docking-rescoring`. For covalent docking, see `chemoinformatics/covalent-design`. For affinity calculations (FEP), see `chemoinformatics/free-energy-calculations`.

## Docking Tool Taxonomy

| Tool | Scoring | Speed (sec/lig) | Best at | Fails when |
|------|---------|-----------------|---------|------------|
| AutoDock Vina 1.2 | Vina (empirical) | Hardware- and settings-dependent | Open, well-characterized baseline | Cross-dock; cryptic pockets; metal centers |
| SMINA | Vina + flexible + custom | Hardware- and settings-dependent | Custom scoring; flexible side chains | Same Vina-scoring caveats |
| Vinardo | Modified Vina scoring | Hardware- and settings-dependent | Alternative empirical score | Validate on target-relevant controls |
| GNINA 1.1 | CNN or Vina scoring | GPU- and settings-dependent | CNN-assisted pose ranking | Validate transfer to the target and chemotype |
| AutoDock 4 | AD4 + grid maps | Hardware- and settings-dependent | Legacy reference | More setup than Vina |
| DOCK 6/7 | DOCK + Amber | Hardware- and settings-dependent | UCSF DOCK ecosystem | Steep learning curve |
| Glide (Schrodinger) | GlideScore | License and hardware-dependent | Commercial docking workflow | License cost |
| GOLD (CCDC) | GOLDScore / ChemScore | License and hardware-dependent | Commercial workflow; metal options | License cost |
| FlexX (BioSolveIT) | FlexX | License and hardware-dependent | Fragment-based placement | License cost |
| rDock | rDock | Hardware- and settings-dependent | Open-source alternative | Validate maintenance and target fit |
| DiffDock-L | Diffusion-generative | GPU- and settings-dependent | Pose sampling for cross-docking | Validate geometry with PoseBusters; see ml-docking-rescoring |
| EquiBind | Equivariant NN | GPU- and settings-dependent | Single-shot pose generation | Requires independent geometry and ranking checks |
| Boltz-2 + GNINA rescore | Foundation model + CNN | GPU- and settings-dependent | Experimental multi-model workflow | Benchmark each evidence stream independently |

**Decision:** Use Vina as an open baseline and consider GNINA CNN rescoring when target-relevant redocking or cross-docking controls support it. For large libraries, calibrate a hierarchical Vina -> GNINA -> higher-cost follow-up workflow on measured enrichment, throughput, and retained chemotype diversity.

## Decision Tree by Scenario

| Scenario | Recommended workflow |
|----------|---------------------|
| Self-dock against known ligand pocket | GNINA `gnina --cnn_scoring rescore` |
| Cross-dock to apo or related-target structure | DiffDock-L pose + GNINA rescore + PoseBusters |
| Ultralarge library (10M+) | Calibrated hierarchical screen: property/alert triage -> Vina -> measured top fraction to GNINA -> higher-cost follow-up |
| Cryptic pocket / induced fit | Receptor-ensemble docking and, where appropriate, a separately validated complex-prediction model |
| Allosteric / undefined site | P2Rank for pocket detection -> ensemble dock all pockets |
| Metal-coordinated ligand | GOLD (commercial) or manually parameterize Vina metal scoring |
| Covalent inhibitor | See `chemoinformatics/covalent-design`: DOCKovalent, HCovDock |
| Fragment screen (<300 Da) | rDock or constrained Vina with seed atoms |
| Hit-to-lead refinement | Use co-crystal structure if available; MD-relaxed receptor; FEP for affinity |

## Receptor Preparation

**Goal:** Convert a protein PDB into a docking-ready format with correct protonation, missing atoms, and removed waters.

**Approach:** Decide which ligands, cofactors, metals, and structural waters to retain -> fill missing heavy atoms with a structure-repair tool such as PDBFixer -> use PROPKA/PDB2PQR plus manual review to assign pH-dependent protonation -> assign the charge model required by the docking workflow -> prepare receptor PDBQT with a documented AutoDock-compatible tool.

```python
import subprocess
from pathlib import Path

def prepare_receptor(repaired_pdb, pdbqt_out, pH=7.4):
    # Decide which waters/cofactors/metals to retain before this function.
    base = str(Path(repaired_pdb).with_suffix(''))
    pqr_file = f'{base}_pH{pH}.pqr'
    subprocess.run(['pdb2pqr', '--ff=AMBER', f'--with-ph={pH}',
                    repaired_pdb, pqr_file], check=True)
    output_basename = str(Path(pdbqt_out).with_suffix(''))
    subprocess.run(['mk_prepare_receptor.py', '--read_pqr', pqr_file,
                    '-o', output_basename, '-p'], check=True)
    return pdbqt_out
```

**Common pitfall:** Forgetting to add hydrogens at protein pH (7.4) but using pH 7.0 ligand charges. Hist mistakenly protonated. Use PROPKA + manual review of catalytic residues.

## Ligand Preparation

**Goal:** Generate a 3D, docking-ready ligand file from SMILES with appropriate protonation and conformation.

**Approach:** Supply a documented protomer/tautomer state generated by an appropriate pKa/protomer workflow -> parse it with RDKit -> embed 3D with ETKDGv3 -> minimize with MMFF94 -> write PDBQT with Meeko. `MolFromSmiles` parses the supplied state and `Uncharger` neutralizes formal charges; neither predicts protonation at pH 7.4.

```python
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy

def prepare_ligand(smiles, pdbqt_out):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f'invalid SMILES: {smiles}')
    mol = Chem.AddHs(mol)
    embed_status = AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    if embed_status != 0:
        raise RuntimeError('ETKDGv3 failed to generate a ligand conformer')
    if not AllChem.MMFFHasAllMoleculeParams(mol):
        raise ValueError('MMFF94 parameters are unavailable for this ligand')
    optimization_status = AllChem.MMFFOptimizeMolecule(mol)
    if optimization_status != 0:
        raise RuntimeError('MMFF94 ligand optimization did not converge')

    # meeko 0.5+ API: prepare() returns a list of MoleculeSetup objects;
    # use PDBQTWriterLegacy.write_string() to materialize the PDBQT block.
    mk_prep = MoleculePreparation()
    setups = mk_prep.prepare(mol)
    pdbqt_text, is_ok, err = PDBQTWriterLegacy.write_string(setups[0])
    if not is_ok:
        raise RuntimeError(f'meeko PDBQT export failed: {err}')
    with open(pdbqt_out, 'w') as f:
        f.write(pdbqt_text)
    return pdbqt_out
```

`meeko` (AutoDock developers' tool) handles torsion tree creation, rotamer flagging, and PDBQT writing -- preferred over Open Babel's PDBQT writer. Note: meeko 0.5+ separated the writer (`PDBQTWriterLegacy`) from `MoleculePreparation`; older code using `prep.write_pdbqt_file()` is deprecated.

## Binding Site Detection

When the binding pocket is not known (apo target, novel allosteric site):

| Tool | Approach | Output |
|------|----------|--------|
| P2Rank (Krivak 2018) | ML on protein surface descriptors | Ranked pocket list with center coords |
| fpocket (Le Guilloux 2009) | Voronoi tessellation | Pocket descriptor list |
| DoGSiteScorer | Geometric + drugability | Pocket list with score |
| AutoSite (Vina) | Affinity map clustering | Pocket centers |
| AlphaFill | Transplant ligands/cofactors from homologous experimental structures into AlphaFold models | Plausible binding-site components for review |

```bash
prank predict -f receptor.pdb -o pockets/
```

P2Rank output `<receptor>_predictions.csv` lists pocket centers with scores. The highest model score does not identify a pocket as orthosteric or biologically relevant; verify ranked pockets against co-crystal, mutagenesis, SAR, or other structural evidence.

## Vina Docking (Single Ligand)

```python
# AutoDock Vina Python API requires Vina 1.2+; for Vina 1.1 use subprocess CLI:
# subprocess.run(['vina', '--receptor', ..., '--ligand', ..., '--center_x', ...], check=True)
from vina import Vina

def dock_single(receptor_pdbqt, ligand_pdbqt, center, box_size,
                exhaustiveness=8, n_poses=10):
    v = Vina(sf_name='vina')
    v.set_receptor(receptor_pdbqt)
    v.set_ligand_from_file(ligand_pdbqt)
    v.compute_vina_maps(center=center, box_size=box_size)
    v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)
    return v.energies(), v.poses()
```

**Exhaustiveness:** `8` is the Vina default. Increasing it increases search effort, but runtime and pose recovery depend on hardware, ligand flexibility, box size, and software version. Benchmark settings such as 8, 16, 32, and 64 on target-relevant controls instead of assigning universal timing or quality labels.

Vina's `rmsd_lb` and `rmsd_ub` are lower and upper heavy-atom RMSD bounds between a reported mode and the best-scoring mode; the bounds differ in how symmetry-equivalent atoms are handled. They are not pose-versus-experimental-reference RMSDs. Use an external symmetry-aware RMSD to a reference pose for accuracy QC.

## GNINA with CNN Scoring (modern default)

```bash
gnina -r receptor.pdb -l ligand.sdf \
      --autobox_ligand reference_ligand.sdf \
      --cnn_scoring rescore \
      -o poses.sdf.gz \
      --num_modes 9 --exhaustiveness 8
```

`--cnn_scoring`:
- `none`: no CNN; use the selected empirical scoring function throughout
- `rescore` (default): use empirical scoring during the search, then CNN-rerank the final poses; least computationally expensive CNN option
- `refinement`: use the CNN to refine poses after Monte Carlo chains and to rank the final poses; approximately 10 times slower than `rescore` on a GPU in the official documentation
- `metrorescore`: use CNN scoring in the Metropolis search and rescore the resulting poses
- `metrorefine`: use CNN scoring in the Metropolis search and refine the resulting poses
- `all`: use the CNN scoring function throughout; the official documentation describes this as extremely computationally intensive and not recommended

The six choices above are from GNINA 1.3. Earlier releases expose a smaller set; check `gnina --help` for the installed executable rather than assuming every mode is available.

`--autobox_ligand`: define box from reference ligand SDF/PDB. Otherwise specify `--center_x/y/z` + `--size_x/y/z`.

**Critical:** GNINA distributions include multiple named CNN models/ensembles rather than one universally described "PDBbind 2019" model. Record the selected model or ensemble and validate it with known co-crystal redocking and, when relevant, cross-docking controls.

## Virtual Screening Pipeline (Hierarchical)

**Goal:** Screen 10M-compound library down to top-1k candidates for follow-up.

**Approach:** Three-stage filter. The 1% and top-1000 selections below are repository starting heuristics; choose production cutoffs from target-relevant enrichment, diversity, and throughput measurements.

Pseudo-code skeleton (orchestrator). Each helper function delegates to a dedicated skill: drug-likeness filter to `chemoinformatics/admet-prediction`, single-ligand Vina/GNINA to `dock_single` defined earlier in this skill, PoseBusters QC to `chemoinformatics/pose-validation`.

```python
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# Stub helpers to be implemented per project; see the cross-referenced skills.
def drug_like_filter(df):
    raise NotImplementedError('Implement via chemoinformatics/admet-prediction (Lipinski+Veber+PAINS)')
def vina_dock(smi, receptor_pdbqt, center, box):
    raise NotImplementedError('Wrap dock_single() above; return best affinity')
def gnina_rescore(smi, receptor_pdbqt, center, box):
    raise NotImplementedError('Wrap gnina --cnn_scoring rescore subprocess call')
def pose_validate(df):
    raise NotImplementedError('Implement via chemoinformatics/pose-validation (PoseBusters)')

def vs_pipeline(library_smi, receptor_pdbqt, center, box, output_dir, n_workers=16):
    df = pd.read_csv(library_smi)
    df_stage1 = drug_like_filter(df)

    worker = partial(vina_dock, receptor_pdbqt=receptor_pdbqt,
                     center=center, box=box)
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        affinities = list(ex.map(worker, df_stage1['smiles']))
    df_stage1['vina_affinity'] = affinities
    df_stage2 = df_stage1.nsmallest(int(len(df_stage1) * 0.01), 'vina_affinity')

    df_stage2['gnina_affinity'] = df_stage2['smiles'].apply(
        lambda smi: gnina_rescore(smi, receptor_pdbqt, center, box))
    df_stage3 = df_stage2.nsmallest(1000, 'gnina_affinity')

    return pose_validate(df_stage3)
```

For very large libraries, use a restartable scheduler-backed workflow and measure throughput on a representative tranche. Record hardware, software version, box dimensions, ligand flexibility, and failure rate with every throughput estimate.

## Ultralarge Library Screening (ZINC22, Enamine REAL)

| Library | Scope | Typical access | Verification requirement |
|---------|-------|----------------|--------------------------|
| ZINC22 | Purchasable and make-on-demand compounds | Tranche/download interfaces | Record the tranche query and retrieval date |
| Enamine REAL | Make-on-demand compounds | Provider files or search interface | Record product-space release and retrieval date |
| Enamine HTS | Screening collection | Provider files | Confirm current stock/version with the provider |
| Mcule | Aggregated purchasable compounds | Provider search/export | Record filters and retrieval date |
| ChEMBL | Curated compounds and bioactivities | Versioned database release | Record ChEMBL release and extraction query |

Library sizes and availability change frequently. Obtain counts from the provider or versioned database at execution time rather than copying a static total into a workflow.

For ultralarge VS, the following percentages and thresholds are repository starting heuristics that must be calibrated for the target and library:
1. Apply a documented property/alert policy while retaining flagged and rejected counts
2. If known actives exist, test a permissive 2D-similarity prefilter such as ECFP4 Tanimoto >=0.4 and measure active/chemotype retention
3. Vina dock the filtered subset
4. Rescore top 1% with GNINA
5. Rescore top 0.1% with MM/GBSA or FEP

Lyu et al. (2019) screened 170 million make-on-demand compounds against AmpC and the D4 dopamine receptor. Of 549 D4 candidates synthesized and tested, 81 were new active chemotypes and 30 had submicromolar activity.

## Per-Tool Failure Modes

### Vina -- cross-dock failure

**Trigger:** Receptor structure not the holo (co-crystal with ligand from another binder).

**Mechanism:** Cross-docking introduces receptor-conformation mismatch, so pose recovery can be substantially worse than self-docking; the size of the decrease is benchmark- and target-dependent.

**Symptom:** Top-ranked pose makes no geometric sense; key contacts missing.

**Fix:** GNINA CNN scoring or ensemble docking. For genuine apo, predict holo with AlphaFold3 / Boltz-1 then dock.

### GNINA CNN -- novel chemotype out-of-distribution

**Trigger:** Ligand chemotype not in PDBbind training.

**Mechanism:** CNN scoring overfits to PDBbind chemotypes; novel macrocycle / peptide / PROTAC scores poorly.

**Symptom:** Affinity prediction far worse than Vina alone.

**Fix:** Use `--cnn_scoring rescore` (sampling still by Vina) rather than CNN sampling. Validate against co-crystal of close analog.

### Box too small

**Trigger:** Binding box defined tightly around small ligand reference.

**Mechanism:** Vina explores only within the box; large analogs cannot fit.

**Symptom:** Many ligands report "no valid pose"; chemotype-biased hits.

**Fix:** Derive the box from the reference ligand or known pocket and add enough explicit padding for the largest intended ligands to translate and rotate. Then verify containment and redocking/search convergence on controls. There is no universal padding value or 25 A cube that fits every ligand series.

### Multi-pocket protein -- wrong site

**Trigger:** Protein has multiple binding sites (orthosteric + allosteric).

**Mechanism:** P2Rank or AutoBox picks the most "drugable" pocket; not always the desired one.

**Symptom:** Hits dock in wrong pocket; SAR confusing.

**Fix:** Verify pocket from co-crystal data; explicitly set `center_x/y/z` from known ligand centroid.

### DiffDock-L -- PoseBusters invalid

**Trigger:** Default DiffDock-L output for any receptor.

**Mechanism:** Diffusion-generated poses are not guaranteed to satisfy every bond-geometry, stereochemistry, and intermolecular-clash check; failure rates vary by method and benchmark.

**Symptom:** Poses look reasonable but fail PoseBusters checks.

**Fix:** Filter to PB-valid (PoseBusters); rescore with GNINA. See `chemoinformatics/pose-validation`.

### Wrong ionization state

**Trigger:** Ligand or receptor residues protonated incorrectly at pH 7.4.

**Mechanism:** Aspartate/glutamate/histidine protonation depends on local environment; default protonation may be wrong.

**Symptom:** Salt bridges missing; poses misranked.

**Fix:** Run PROPKA on the receptor to estimate residue pKas; for catalytic histidines, manually inspect protonation and tautomer state in the local environment.

## Reconciliation: Vina vs GNINA Disagreement

| Vina top pose | GNINA top pose | Action |
|---------------|----------------|--------|
| Same pose, similar score | Same pose, similar score | Treat agreement as supporting evidence; still run physical-validity checks |
| Vina top pose ≠ GNINA top pose | Same pocket, different orientation | Retain both and compare against target-relevant controls or interaction evidence |
| Vina excellent, GNINA mediocre | Different pose, very different score | Inspect both poses; do not infer which method is correct from score disagreement alone |
| Both poor scores | Many ligands score similarly poor | Wrong pocket / protein conformation; reconsider receptor |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Vina segfault | PDBQT corrupted (atom names) | Re-prep with meeko |
| GNINA hangs | GPU OOM | Reduce concurrent work and, if fewer output poses are acceptable, use `--num_modes 5` |
| All affinities very poor (-3 to -5) | Wrong protonation; ligand too large for box | Re-check pKa; expand box |
| Identical affinity across ligands | Receptor grid not computed | Call `v.compute_vina_maps()` before dock |
| Pose poses make no sense | Receptor and ligand in different frames | Ensure same coordinate origin |
| Metal-coordination pose is wrong | The selected scoring/preparation protocol lacks a validated model for that metal geometry | Use a metal-specific validated workflow; the Vina executable can use AutoDock4Zn maps with `--scoring ad4` for zinc, while other metals require separately supported parameters/protocols |
| GPU mode slow | Vina is CPU-only; only GNINA is GPU | Use GNINA for GPU; Vina is multi-core CPU |

## References

- Trott & Olson, *J. Comput. Chem.* 31:455-461 (2010) -- AutoDock Vina. https://doi.org/10.1002/jcc.21334
- Eberhardt et al., *J. Chem. Inf. Model.* 61:3891-3898 (2021) -- Vina 1.2 features. https://doi.org/10.1021/acs.jcim.1c00203
- AutoDock Vina, official manual -- result-field and CLI semantics. https://vina.scripps.edu/manual/
- AutoDock Vina, official zinc-metalloprotein tutorial -- AutoDock4Zn maps through the Vina executable. https://autodock-vina.readthedocs.io/en/latest/docking_zinc.html
- Quiroga & Villarreal, *PLoS ONE* 11:e0155183 (2016) -- Vinardo scoring. https://doi.org/10.1371/journal.pone.0155183
- McNutt et al., *J. Cheminformatics* 13:43 (2021) -- GNINA 1.0 CNN docking. https://doi.org/10.1186/s13321-021-00522-2
- GNINA, official repository -- current CLI modes and named CNN ensembles. https://github.com/gnina/gnina
- Buttenschoen et al., *Chem. Sci.* 15:3130-3139 (2024) -- PoseBusters benchmark. https://doi.org/10.1039/D3SC04185A
- Lyu et al., *Nature* 566:224-229 (2019) -- ultralarge virtual-screening proof of concept. https://doi.org/10.1038/s41586-019-0917-9
- Krivak & Hoksza, *J. Cheminformatics* 10:39 (2018) -- P2Rank. https://doi.org/10.1186/s13321-018-0285-8
- Forli et al., *Nat. Protoc.* 11:905-919 (2016) -- AutoDock suite and AutoDockTools. https://doi.org/10.1038/nprot.2016.051
- Le Guilloux, Schmidtke & Tuffery, *BMC Bioinformatics* 10:168 (2009) -- fpocket. https://doi.org/10.1186/1471-2105-10-168
- Meeko, official documentation -- ligand/receptor PDBQT preparation and export interfaces. https://meeko.readthedocs.io/
- Dolinsky et al., *Nucleic Acids Res.* 35:W522-W525 (2007) -- PDB2PQR. https://doi.org/10.1093/nar/gkm276
- Olsson et al., *J. Chem. Theory Comput.* 7:525-537 (2011) -- PROPKA 3. https://doi.org/10.1021/ct100578z
- PDBFixer, official repository -- missing-residue/atom repair interface. https://github.com/openmm/pdbfixer
- Corso et al., *ICLR* (2024) -- DiffDock-L. https://proceedings.iclr.cc/paper_files/paper/2024/file/db334db287337b2a365120b524300ef3-Paper-Conference.pdf
- Stärk et al., *ICML* (2022) -- EquiBind. https://proceedings.mlr.press/v162/stark22b.html
- Qiao et al., *Nat. Mach. Intell.* 6:195-208 (2024) -- NeuralPLexer. https://doi.org/10.1038/s42256-024-00792-z
- Passaro et al., bioRxiv (2025) -- Boltz-2. https://doi.org/10.1101/2025.06.14.659707
- Abramson et al., *Nature* 630:493-500 (2024) -- AlphaFold 3. https://doi.org/10.1038/s41586-024-07487-w
- ZINC22, official resource. https://zinc22.docking.org/
- Enamine REAL, official resource. https://enamine.net/compound-collections/real-compounds
- ChEMBL, official versioned database. https://www.ebi.ac.uk/chembl/

## Related Skills

- chemoinformatics/molecular-io - Parse ligands
- chemoinformatics/conformer-generation - Generate 3D for ligand prep
- chemoinformatics/molecular-standardization - Canonicalize before docking
- chemoinformatics/pose-validation - PoseBusters physical-validity QC
- chemoinformatics/ml-docking-rescoring - DiffDock-L + GNINA hybrid
- chemoinformatics/covalent-design - Covalent docking
- chemoinformatics/free-energy-calculations - FEP for refined affinity
- chemoinformatics/admet-prediction - Filter library before docking
- structural-biology/structure-io - PDB / mmCIF handling
- structural-biology/modern-structure-prediction - AlphaFold3 / Boltz-1 for apo receptors
<!-- END FILE: chemoinformatics/virtual-screening/SKILL.md -->

<!-- END CATEGORY: chemoinformatics -->

