---
slug: bio-structural-biology-integrated
version: 1.0.0
displayName: "结构生物学 / Protein structure analysis"
name: bio-structural-biology-integrated
summary: >-
  中文：结构生物学综合技能，整合 10 个相关专题，覆盖蛋白质结构分析：PDB/mmCIF读取、SMCRA导航、几何分析、结合位点检测、AlphaFold/ESMFold预测。 English: Integrated Protein structure analysis skill covering 10 related topics, including Protein structure analysis: PDB/mmCIF reading, SMCRA navigation, geometric analysis, binding site detection, AlphaFold/ESMFold prediction.
description: >-
  中文：这是一个面向结构生物学的综合生物信息学 Skill，整合当前分类下 10 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：蛋白质结构分析：PDB/mmCIF读取、SMCRA导航、几何分析、结合位点检测、AlphaFold/ESMFold预测。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Bio.PDB, ESMFold, PDBFixer。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Protein structure analysis, combining 10 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Protein structure analysis: PDB/mmCIF reading, SMCRA navigation, geometric analysis, binding site detection, AlphaFold/ESMFold prediction. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Bio.PDB, ESMFold, PDBFixer. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# structural-biology 分类 Skill 整合版

> 本文件整合同一主分类目录下 10 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: structural-biology -->

## 子目录：structural-biology/alphafold-predictions

<!-- BEGIN FILE: structural-biology/alphafold-predictions/SKILL.md -->
---
name: bio-structural-biology-alphafold-predictions
description: Retrieves and interprets AlphaFold Protein Structure Database (AFDB) models by UniProt accession, reading pLDDT and PAE confidence correctly. Use when treating pLDDT as PER-RESIDUE confidence (not global accuracy) and recognizing a long low-pLDDT stretch as an intrinsically disordered region rather than a modeling error; reading PAE to segment confident domains and judge inter-domain/relative-position confidence that high mean pLDDT cannot certify; recognizing a static AFDB model carries NO ligands, ions, cofactors, PTMs, quaternary assembly, or alternative conformations (pLDDT sits in the B-factor column with opposite polarity to thermal motion); and deciding an AFDB entry vs re-running prediction. Keywords AlphaFold DB, pLDDT, PAE, B-factor column, intrinsic disorder, UniProt, Foldseek.
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: biopython 1.83+, numpy 1.26+, requests 2.31+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# AlphaFold Predictions

**"Get the AlphaFold model for my protein and tell me which parts to believe"** -> Fetch the precomputed AFDB entry by UniProt accession, then read its confidence files (pLDDT per-residue, PAE per-residue-pair) to decide which regions and which geometry are trustworthy.
- Python: `requests.get(f'https://alphafold.ebi.ac.uk/api/prediction/{accession}')` returns metadata with `cifUrl`/`pdbUrl`/`paeDocUrl` download links.

## Governing Principle

An AFDB entry is ONE AlphaFold2 prediction of a SINGLE UniProt sequence modeled as an isolated chain in vacuum - a per-chain hypothesis of a dominant fold, not an experimental structure and not a biological state. It carries NO ligands, ions, cofactors, metals, or substrates (the pocket is apo even when the protein only folds around a cofactor), NO post-translational modifications, NO quaternary structure or biological assembly (it is a monomer even for obligate oligomers), NO alternative conformations (one static snapshot - kinases render in one activation state, transporters in one gate state), and NO membrane context. The cardinal error is using an AFDB coordinate file as an experimental holo complex instead of as a scored guess whose own confidence files tell the reader which parts to believe.

Three confidence traps ride on top of this. First, pLDDT is written into the B-FACTOR COLUMN but is per-residue CONFIDENCE (0-100, higher=better) with OPPOSITE polarity to a real B-factor - any tool that reads that column as thermal motion inverts the meaning, and feeding raw pLDDT-as-B into crystallographic refinement mis-weights it. Second, a long low-pLDDT stretch is usually a genuine INTRINSICALLY DISORDERED REGION (pLDDT is competitive with dedicated IDR predictors; Akdel 2022 *Nat Struct Mol Biol* 29:1056; Piovesan 2022 *Protein Sci* 31:e4466), not a modeling failure - trimming it as "junk" discards real biology. Third, pLDDT is LOCAL and per-residue: high mean pLDDT does NOT certify inter-domain placement. Two rigid domains can each be 95 pLDDT yet float at an unknown relative orientation - reading that is PAE's job. "Confident" bounds the structural self-consistency of the prediction, NOT its biological correctness.

## Decision: pLDDT confidence bands

| pLDDT | Band | Operational meaning | Trust for |
|-------|------|---------------------|-----------|
| > 90 | Very high | Backbone AND well-oriented side chains | Side-chain detail, catalytic-geometry hypotheses, MR core |
| 70-90 | Confident | Backbone generally correct | Fold, domain topology, backbone-level MR; be wary of side chains |
| 50-70 | Low | Backbone uncertain, cautionary zone | Coarse topology at best; never trust details |
| < 50 | Very low | Ribbon is a placeholder; frequently an IDR | Disorder signal, NOT a conformation |

Band cutoffs 90/70/50 are the AFDB-defined thresholds (Jumper 2021 *Nature* 596:583). A very-low band is a disorder SIGNAL, not proof of error - a conditionally-folded binding region looks disordered in AFDB yet folds on binding a partner AFDB never sees.

## Decision: downstream-use suitability

| Use | AFDB monomer suitability | Key caveat |
|-----|--------------------------|------------|
| Remote-homology / fold search (Foldseek) | Excellent | Feed the confident core; a match is a hypothesis |
| Molecular replacement | Very good after processing | Trim + pLDDT->pseudo-B + PAE domain split first |
| Fold / domain-architecture analysis | Good | Segment by PAE, not the stitched cartoon |
| Disorder / IDR annotation | Good (pLDDT as predictor) | Low pLDDT = disorder signal, not error |
| Ligand docking / virtual screening | Poor to moderate | Apo pocket, unreliable rotamers, wrong gate/state, absent cofactor |
| Mechanism / catalytic geometry | Poor without holo | No ligands/metals/PTMs; wrong-state risk |
| Quaternary structure / interfaces | Not applicable | Monomer only - run AF3 / AF-Multimer |
| Conformational ensembles / allostery | Not applicable | Single static state |

Foldseek structure search over AFDB (van Kempen 2024 *Nat Biotechnol* 42:243) is the transformative use - it encodes backbone into the 3Di alphabet and finds structural homologs invisible to sequence search (see alignment/structural-alignment). Molecular replacement needs the model PROCESSED first: `phenix.process_predicted_model` (Oeffner 2022 *Acta Cryst D* 78:1303) reads pLDDT from the B column, converts pLDDT->pseudo-B, trims below ~0.7 fractional pLDDT, and splits into PAE-defined domains. Docking into an AFDB pocket gives confidently wrong poses when the backbone is confident but the rotamers, gate state, or cofactor are not.

## Decision: use the AFDB entry vs run a new prediction

| Situation | Use AFDB | Run a new prediction |
|-----------|----------|----------------------|
| Single well-covered UniProt monomer, fold-level question | Yes | No |
| Need a complex, assembly, or interface | No (monomer only) | Yes - AF3 / AF-Multimer |
| Need ligand / ion / cofactor / PTM context | No | AF3 or dock into experimental |
| Designed or mutant sequence not in UniProt | No | Yes |
| Want deeper / custom MSA depth | No (MSA is fixed) | Yes |
| Want a specific alternative conformation | No (single state) | Yes (subsampled MSA) - still hard |
| Very long non-human protein (> 2700 aa) | Often absent | Yes (domain-wise) or ESM Atlas |

Anything needing complexes, ligands, mutants, custom MSA depth, or a specific state points to modern-structure-prediction. AFDB is monomer-only and FIXED at deposition - a newer method or deeper MSA is not reflected.

## Fetch the AFDB entry via REST metadata

**Goal:** Download the coordinate file and PAE for a UniProt accession without hard-coding a version suffix.

**Approach:** Query the prediction metadata endpoint, which returns the current download URLs (`cifUrl`, `pdbUrl`, `paeDocUrl`); the version token drifts (v4 -> v6 as of 2025) so the URLs are discovered, never assembled by hand.

```python
import requests

def afdb_metadata(accession):
    url = f'https://alphafold.ebi.ac.uk/api/prediction/{accession}'
    r = requests.get(url)
    r.raise_for_status()
    return r.json()  # list; one object per fragment/isoform, empty if no model exists

def fetch_afdb(accession, out_dir='.'):
    entries = afdb_metadata(accession)
    if not entries:
        return None  # >2700-aa non-human proteins and non-UniProt sequences are often absent
    entry = entries[0]
    cif_text = requests.get(entry['cifUrl']).text
    pae_json = requests.get(entry['paeDocUrl']).json()
    cif_path = f"{out_dir}/AF-{accession}.cif"
    with open(cif_path, 'w') as f:
        f.write(cif_text)
    return cif_path, pae_json

result = fetch_afdb('P04637')  # human p53
```

Long proteins split into fragments `AF-{accession}-F1-...`, `-F2-...` (human > 2700 aa, ~1400-aa windows shifted by 200); `afdb_metadata` returns one entry per fragment. Relative placement ACROSS fragments is independent and must not be trusted.

## Read pLDDT from the B-factor column

**Goal:** Extract per-residue confidence and classify each residue into a band.

**Approach:** Parse the model, read the B-factor field of the CA atom (that is where AFDB stores pLDDT), and map the score through the 90/70/50 cutoffs.

```python
from Bio.PDB import MMCIFParser

def extract_plddt(cif_file):
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure('af', cif_file)
    plddt = {}
    for residue in structure[0].get_residues():
        if residue.id[0] == ' ' and 'CA' in residue:
            # pLDDT rides in the B-factor column but is CONFIDENCE (0-100, higher=better),
            # opposite polarity to a thermal B-factor - never read it as motion
            plddt[residue.id[1]] = residue['CA'].get_bfactor()
    return plddt

def plddt_band(score):
    if score > 90:                       # 90: side-chain-trustworthy core (AFDB very-high cut)
        return 'very_high'
    if score >= 70:                      # 70: backbone-reliable fold (AFDB confident cut)
        return 'confident'
    if score >= 50:                      # 50: coarse topology only below this
        return 'low'
    return 'very_low'                    # <50: usually an intrinsically disordered region

plddt = extract_plddt('AF-P04637.cif')
mean_plddt = sum(plddt.values()) / len(plddt)
disordered = [res for res, s in plddt.items() if s < 50]  # candidate IDR, not error
```

A high mean does not license inter-domain claims - a globally 90-pLDDT model can still have two domains at an unconstrained orientation. Check PAE before measuring any inter-domain distance.

## Read PAE to segment domains and judge relative orientation

**Goal:** Decide which residue pairs have a confident relative position and where to split the model into independent rigid bodies.

**Approach:** Load the compact PAE matrix; low off-diagonal blocks mark domains whose relative orientation is confident, bright (high) inter-block regions mark independently-placed domains to segment.

```python
import numpy as np

def load_pae(pae_json):
    entry = pae_json[0] if isinstance(pae_json, list) else pae_json
    # Compact format (2023+): 2D num_res x num_res array (values rounded to integer).
    # Legacy 1D 'distance'/'residue1'/'residue2' fields were removed - do not read them.
    return np.array(entry['predicted_aligned_error'])

def interdomain_confidence(pae, domain_a, domain_b):
    # PAE is asymmetric (aligning on i vs j differs); average both off-diagonal blocks.
    block = np.concatenate([pae[np.ix_(domain_a, domain_b)].ravel(),
                            pae[np.ix_(domain_b, domain_a)].ravel()])
    return block.mean()  # low (roughly < 5 A) = confident relative placement; high = a guess

pae = load_pae(fetch_afdb('P04637')[1])
```

Confident low-PAE squares along the diagonal define the confidently-predicted DOMAINS; a bright inter-block region means "these two domains are correctly folded individually but their relative arrangement is unconstrained - treat them as separate rigid bodies." This is exactly how AFDB defines predicted domains and how MR pipelines split a search model.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Model "colored by flexibility" looks inverted | Read the B-factor column as thermal motion | It is pLDDT (confidence, higher=better); color by pLDDT bands |
| Low-pLDDT tail deleted, then a known IDR/linker is missing | Treated low pLDDT as "wrong" | Low pLDDT usually = disorder; keep and annotate as IDR, cross-check a sequence disorder predictor |
| Confident domains, but inter-domain distance is nonsense | Trusted the stitched cartoon on high mean pLDDT | pLDDT is local; read PAE - high off-diagonal PAE = unconstrained relative placement |
| Docking scores look great but validate poorly | Docked into an apo AFDB pocket | Pocket lacks the ligand/cofactor and has unreliable rotamers; use a holo structure or flexible docking |
| Catalytic-geometry conclusion contradicts experiment | AFDB has no metals/ligands/PTMs and one static state | Do not read mechanism from a monomer apo model; get a holo structure |
| 404 / empty metadata list for a large protein | > 2700-aa non-human proteins are excluded; non-UniProt sequences absent | Run a new prediction (domain-wise) or query the ESM Metagenomic Atlas |
| Only residues 1-1400 returned for a long human protein | The model is fragmented (F1, F2 ...) | Iterate all metadata entries; never trust placement across fragments |
| `KeyError: 'distance'` loading PAE | Code written for the legacy 1D PAE JSON | Read the 2D `predicted_aligned_error` array from the compact format |
| Hard-coded `..._v4.cif` URL 404s | The version suffix advanced (v6 as of 2025) | Discover URLs from `/api/prediction/{accession}` metadata, do not assemble them |
| pLDDT looks fine but the biological state is wrong | Modeled the wrong assembly/conformation confidently | Confidence bounds self-consistency, not biological correctness; ask what context AFDB could not see |
| Foldseek hits are noisy or low-quality | Fed the low-pLDDT spaghetti into the search | 3Di is backbone geometry; search the confident core only |

## Related Skills

- structural-biology/modern-structure-prediction - run a new prediction when a complex, ligand, mutant, or specific state is needed
- structural-biology/structure-io - parse and convert the downloaded PDB/mmCIF
- structural-biology/geometric-analysis - RMSD, superposition, and per-residue deviation against an experimental structure
- structural-biology/structure-modification - trim low-pLDDT regions or write pLDDT into the B-factor column for coloring
- structural-biology/structure-preparation - add hydrogens and protonation states before docking or MD on the model
- structural-biology/binding-site-detection - find pockets on the predicted model (apo, unreliable rotamers)
- alignment/structural-alignment - Foldseek 3Di search over AFDB for remote-homology detection
- database-access/uniprot-access - resolve gene names and sequences to the UniProt accession AFDB is keyed on
- database-access/remote-homology - sequence-level homology search to complement structure search

## References

- Jumper J, et al. (2021) Highly accurate protein structure prediction with AlphaFold. *Nature* 596:583-589.
- Tunyasuvunakool K, et al. (2021) Highly accurate protein structure prediction for the human proteome. *Nature* 596:590-596.
- Varadi M, et al. (2022) AlphaFold Protein Structure Database: massively expanding the structural coverage of protein-sequence space with high-accuracy models. *Nucleic Acids Res* 50:D439-D444.
- Varadi M, et al. (2024) AlphaFold Protein Structure Database in 2024: providing structure coverage for over 214 million protein sequences. *Nucleic Acids Res* 52:D368-D375.
- Akdel M, et al. (2022) A structural biology community assessment of AlphaFold2 applications. *Nat Struct Mol Biol* 29:1056-1067.
- Piovesan D, Monzon AM, Tosatto SCE (2022) Intrinsic protein disorder and conditional folding in AlphaFoldDB. *Protein Sci* 31:e4466.
- van Kempen M, et al. (2024) Fast and accurate protein structure search with Foldseek. *Nat Biotechnol* 42:243-246.
- Oeffner RD, et al. (2022) Putting AlphaFold models to work with phenix.process_predicted_model and ISOLDE. *Acta Cryst D* 78:1303-1314.
- Terwilliger TC, et al. (2024) AlphaFold predictions are valuable hypotheses and accelerate but do not replace experimental structure determination. *Nat Methods* 21:110-116.
<!-- END FILE: structural-biology/alphafold-predictions/SKILL.md -->

## 子目录：structural-biology/binding-site-detection

<!-- BEGIN FILE: structural-biology/binding-site-detection/SKILL.md -->
---
name: bio-structural-biology-binding-site-detection
description: Detects putative ligand-binding pockets and druggable cavities de novo on an apo protein structure with fpocket, P2Rank, CASTp, and DoGSiteScorer, ranking them by druggability/ligandability score. Use when detecting cavities on an apo structure with no bound ligand; choosing geometric pocket enumeration (fpocket alpha-spheres, CASTp) vs ML ligandability scoring (P2Rank, DoGSiteScorer); recognizing that a geometric cavity is a hypothesis, not automatically a functional or druggable site (may be a crystal-additive or non-functional cleft); knowing druggability scores were trained on holo sets and under-detect apo, shallow, and cryptic pockets; detecting cryptic or transient pockets over an MD or conformational ensemble (mdpocket); and detecting on a predicted model whose pocket-lining rotamers are the least reliable atoms. Keywords binding site, pocket, cavity, druggability, ligandability, fpocket, P2Rank, CASTp, DoGSiteScorer, apo, cryptic pocket, alpha sphere, mdpocket.
tool_type: mixed
primary_tool: fpocket
---

## Version Compatibility

Reference examples tested with: fpocket 4.1+, P2Rank 2.4+, biopython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Binding Site Detection

**"Find the pockets / druggable cavities on my apo structure"** -> Enumerate surface concavities de novo and rank them by a ligandability or druggability score.
- CLI: `fpocket -f protein.pdb` (alpha-sphere / Voronoi) or `prank predict -f protein.pdb` (ML ligandability)

**"Where could a ligand bind, and how druggable is each site?"** -> Detect candidate pockets, then score each for the likelihood of binding a drug-like molecule.
- CLI: fpocket druggability score (per pocket) or P2Rank probability; CASTp / DoGSiteScorer web servers for surface area and SVM druggability

**"Detect a cryptic pocket that is not open in this single snapshot"** -> Track pocket opening across a conformational ensemble, not one static file.
- CLI: `mdpocket --trajectory_file traj.xtc --trajectory_format xtc -f topology.pdb` over an MD trajectory or NMR ensemble

## Governing Principle

A geometric cavity is NOT automatically a functional or druggable site. Pure geometry - fpocket alpha-spheres (Le Guilloux 2009 *BMC Bioinformatics* 10:168), CASTp surface topology (Tian 2018 *Nucleic Acids Res* 46:W363) - finds ALL concavities on the surface, including crystallization-additive sites (a sulfate, glycerol, or PEG cleft), non-functional surface pockets, and inter-domain crevices. A ranked pocket list is therefore a HYPOTHESIS, not a binding site. The single most reliable site is one that is already occupied: if the structure is holo (a ligand is bound), map the residues around that ligand directly - that is interface-analysis, not de-novo detection.

Druggability and ligandability SCORES (the fpocket druggability score, P2Rank probability, DoGSiteScorer SVM) rank pockets, but the ranking is not function and not a guarantee. These models were trained largely on holo, druggable reference sets (Schmidtke 2010 *J Med Chem* 53:5858; Volkamer 2012 *J Chem Inf Model* 52:360), so they systematically UNDER-detect and under-score apo, shallow, allosteric, and protein-protein-interface pockets, and they cannot see a CRYPTIC pocket at all - a cryptic site forms a pocket in the holo structure but is closed in the apo structure (Cimermancic 2016 *J Mol Biol* 428:709), so it only appears across an MD or conformational ensemble, never in one static apo snapshot.

Detecting on a PREDICTED model (AlphaFold, ESMFold) inherits that model's pocket-conformation unreliability. The model is usually an apo-like ground state that carries no ligand, cofactor, or metal that would shape the real site, and the side-chain rotamers lining a pocket are the LEAST reliable atoms even when the backbone pLDDT is high (see alphafold-predictions) - so a "confident" backbone can present a confidently wrong pocket. Validate and prepare the model first (structure-validation, structure-preparation). Whatever the input, state the method used and remember: ranking is not function, and the top pocket is a starting hypothesis to corroborate. The orthogonal corroboration signals are an independent detector, evolutionary conservation of the lining residues (a functional site is usually conserved, an additive/crystal cleft usually is not), hot-spot or mixed-solvent mapping (FTMap, mixed-solvent MD), a homolog holo structure, and known biology - not the geometric rank alone.

## Decision: method by question

| Question / situation | Method | Best when | Fails / misleads when |
|---|---|---|---|
| Enumerate every geometric concavity, fast | fpocket (alpha-sphere/Voronoi) or CASTp (surface topology) | Apo or holo, whole-surface scan, ranked candidate list | Reports additive sites, crystal clefts, and non-functional pockets as pockets; ranking != function |
| Rank pockets by ligandability / druggability | P2Rank (ML probability), fpocket druggability score, DoGSiteScorer (SVM) | Prioritizing among many cavities on a folded globular domain | Trained on holo/druggable sets -> under-scores apo, shallow, allosteric, and PPI sites |
| Detect a cryptic or transient pocket | mdpocket over an MD trajectory or conformational ensemble | Site opens only on binding / not present in a single apo snapshot | A single static structure - a cryptic site is invisible without conformational sampling |
| A ligand is already bound (holo structure) | interface-analysis (residues around the bound ligand) | The real binding site is known - map it, do not re-detect | Running de-novo detection when the answer is already in the file |
| Surface area / volume of a defined pocket | CASTp (analytic surface + volume) or fpocket descriptors | Quantifying a known pocket's size | Treating a large computed cavity as evidence of function |

The one-line rule: geometry enumerates concavities, scores rank them, an ensemble reveals cryptic ones, and a bound ligand settles it. Reach for the cheapest method that answers the actual question.

## Decision: structure state and what a pocket result means

| Structure state | What a detected pocket reveals | What it cannot reveal |
|---|---|---|
| Holo (ligand bound) | The real, occupied site - highest reliability; map it directly | Whether other detected pockets are functional (still hypotheses) |
| Apo experimental | Open, ligand-accessible pockets present in THIS conformation | Cryptic sites closed in this snapshot; induced-fit geometry |
| Predicted model (AlphaFold/ESMFold) | Candidate fold and gross concavities | Reliable pocket rotamers (least reliable atoms), cofactor/metal-shaped sites; validate first |
| MD / NMR ensemble | Transient and cryptic pockets, pocket dynamics/persistence | Which opening is biologically relevant (do not over-read rare openings) |

Apo detection answers "what could open here in this state", holo answers "what is actually bound", a predicted model answers "what might a pocket look like in the ground state", and an ensemble answers "what transiently opens". Match the claim to the state.

## Detect and rank pockets with fpocket

**Goal:** Enumerate candidate pockets on an apo structure and rank them by druggability, keeping the result explicitly a hypothesis list.

**Approach:** Run fpocket, which writes a `<stem>_out/` directory beside the input containing a `<stem>_info.txt` descriptor file and per-pocket `pockets/pocketN_atm.pdb` files. Parse the info file into per-pocket descriptors and sort by the druggability score. The 0.5 druggability cutoff is a rule-of-thumb triage line, not a law (Schmidtke 2010): above it a drug-like molecule is plausible, below it the pocket is likely undruggable by conventional small molecules, but apo and cryptic sites routinely fall below it while still being real.

```python
import subprocess
from pathlib import Path

def run_fpocket(pdb_path):
    subprocess.run(['fpocket', '-f', pdb_path], check=True)
    stem = Path(pdb_path).stem
    return Path(pdb_path).with_name(f'{stem}_out')  # fpocket writes <stem>_out/ beside the input

def parse_fpocket_info(out_dir):
    info = next(Path(out_dir).glob('*_info.txt'))
    pockets, current = [], None
    for raw in info.read_text().splitlines():
        line = raw.strip()
        if line.startswith('Pocket'):
            current = {'pocket': int(line.split()[1])}
            pockets.append(current)
        elif ':' in line and current is not None:
            key, val = (part.strip() for part in line.split(':', 1))
            current[key] = float(val)
    return pockets

out_dir = run_fpocket('protein.pdb')
pockets = sorted(parse_fpocket_info(out_dir),
                 key=lambda p: p['Druggability Score'], reverse=True)
druggable = [p for p in pockets if p['Druggability Score'] >= 0.5]  # 0.5 = triage, not a law
for p in pockets[:5]:
    print(f"pocket {p['pocket']}: drug={p['Druggability Score']:.2f} score={p['Score']:.2f}")
```

The pocket `Score` ranks how likely the cavity binds a small molecule; the `Druggability Score` (0-1) estimates likelihood of binding a DRUG-LIKE molecule specifically. A high-scoring pocket that coincides with a bound additive in the deposited file is a crystallization site, not a target - cross-check the pocket atoms against any HETATM in the input (structure-navigation).

## Score ligandability with P2Rank

**Goal:** Get a template-free, machine-learned ligandability ranking that does not depend on alpha-sphere geometry alone.

**Approach:** Run P2Rank, which scores points on the solvent-accessible surface and clusters them into ranked pockets, writing `<inputname>_predictions.csv`. Parse the calibrated `probability` per pocket. P2Rank is ML-based and template-free (Krivak 2018 *J Cheminform* 10:39), so it complements fpocket's pure geometry - agreement between the two on the same top pocket raises confidence; disagreement flags a site to scrutinize.

```python
import csv
import subprocess
from pathlib import Path

def run_p2rank(pdb_path, out_dir='p2rank_out'):
    subprocess.run(['prank', 'predict', '-f', pdb_path, '-o', out_dir], check=True)
    return Path(out_dir) / f'{Path(pdb_path).name}_predictions.csv'  # keeps the input extension

def parse_p2rank(csv_path):
    with open(csv_path) as fh:
        reader = csv.DictReader(fh, skipinitialspace=True)  # P2Rank pads columns with spaces
        rows = [{k.strip(): v.strip() for k, v in row.items()} for row in reader]
    return [{'rank': int(r['rank']), 'score': float(r['score']),
             'probability': float(r['probability'])} for r in rows]

predictions = parse_p2rank(run_p2rank('protein.pdb'))
top = predictions[0]  # rows are already ordered by rank
print(f"top pocket: probability={top['probability']:.2f} score={top['score']:.2f}")
```

P2Rank ranks pockets even when every probability is modest; a low top probability on an apo or PPI target is expected, not a failure to find a site.

## Surface topology and SVM druggability servers

CASTp 3.0 (Tian 2018 *Nucleic Acids Res* 46:W363, http://sts.bioe.uic.edu/castp/) is a web server that delineates pockets, interior cavities, and channels analytically and reports each one's molecular surface AREA and VOLUME - use it when the question is pocket geometry (size, mouth, buried volume) rather than a druggability call. DoGSiteScorer, on the ProteinsPlus server (Volkamer 2012 *J Chem Inf Model* 52:360, https://proteins.plus/), predicts pockets by a difference-of-Gaussians grid and returns an SVM druggability score trained on a druggable/undruggable set - a second, independent druggability opinion to compare against fpocket. Both are servers with no Python binding; submit a structure and parse the returned table. Treat a server druggability number the same way as fpocket's: trained on holo/druggable data, so it under-scores apo and cryptic sites.

## Cryptic pockets over an ensemble

**Goal:** Find a site that is closed in the single apo structure but opens on binding.

**Approach:** A cryptic pocket does not exist in one static snapshot, so run pocket detection over a conformational ENSEMBLE - an MD trajectory, an NMR ensemble, or frames from enhanced sampling that is designed to open cryptic sites (mixed-solvent MD / SWISH, accelerated MD) - and track pocket persistence and opening frequency. Generating that ensemble is the real upstream step; mdpocket (Schmidtke 2011 *Bioinformatics* 27:3276) then analyzes it, building a pocket-frequency grid across frames, and the `-S` flag adds a per-snapshot drug score so a druggable pocket that only appears transiently is visible.

```python
import subprocess

def run_mdpocket(topology_pdb, trajectory, fmt='xtc'):
    # -S adds the per-snapshot drug score so a transiently druggable pocket is flagged
    subprocess.run(['mdpocket', '--trajectory_file', trajectory,
                    '--trajectory_format', fmt, '-f', topology_pdb, '-S'], check=True)
```

Do not over-read a pocket that opens in a handful of frames - a rare, short-lived opening is a weaker hypothesis than a persistent one, and enhanced sampling can manufacture openings that are not physiologically populated. Once a cryptic site is chosen, the bound-state geometry (not the closed apo structure) is what a docking run needs.

## Once a site is chosen

A detected, ranked pocket is the INPUT to structure-based drug discovery, not the endpoint. Hand the chosen pocket (its center and lining residues) to chemoinformatics/virtual-screening to dock a library into it, and to chemoinformatics/ml-docking-rescoring to rescore poses - both of those presuppose a known site, which is exactly what this skill produces. Carry the caveat forward: docking into an apo or predicted pocket with unreliable rotamers gives confidently wrong poses unless the pocket is prepared and, ideally, cross-checked against a holo conformation.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Top-ranked pocket is a surface additive site | Geometry finds all concavities, including where a sulfate/glycerol/PEG sat | Cross-check pocket atoms against HETATM/additives in the input; strip additives first (structure-modification) |
| A known binding site is missed entirely | Site is cryptic - closed in the single apo snapshot | Run mdpocket over an MD/NMR ensemble, not one static structure |
| Druggability scores all low on a real target | Score trained on holo/druggable sets under-scores apo, shallow, allosteric, PPI sites | Low score is not "no site"; corroborate with an independent method (P2Rank/DoGSiteScorer), evolutionary conservation of the lining residues (ConSurf), hot-spot / mixed-solvent mapping (FTMap), homolog holo structures, and known biology |
| fpocket finds no `_info.txt` | Parsed the wrong directory or fpocket failed silently | fpocket writes `<stem>_out/` beside the input; check the run completed and the stem matches |
| P2Rank parse gives KeyError on column | The CSV has a space after each comma so header keys carry a leading space (` probability`) | Use `csv.DictReader(skipinitialspace=True)` and strip keys before indexing |
| Pockets differ between apo and holo of the same protein | Induced fit - the pocket reshapes on binding | Expected; detect on the state that matches the question, do not average them |
| "Confident" AlphaFold pocket docks poorly | Pocket-lining rotamers are the least reliable atoms; model is apo-like | Validate/prepare the model (structure-validation); prefer a holo experimental structure |
| Same pocket, different rank from two tools | fpocket geometry vs P2Rank ML weight features differently | Agreement raises confidence; treat disagreement as a flag to inspect, not a tie-break |
| Reported "N druggable pockets" as a finding | Ranking treated as function | State it as a ranked hypothesis list; a score is not a validated site |
| mdpocket pocket appears in few frames trusted as real | Over-reading a rare, short-lived opening | Weight by opening frequency/persistence; rare openings are weak hypotheses |
| Detection on the asymmetric unit misses an interface pocket | Functional pocket sits across a symmetry-generated interface | Detect on the biological assembly (structure-io) when the site may be inter-chain |

## Related Skills

- structural-biology/interface-analysis - map residues around an ALREADY-BOUND ligand (holo); the complement of de-novo detection
- structural-biology/structure-validation - judge whether a structure or predicted model is trustworthy before detecting on it
- structural-biology/structure-preparation - clean, protonate, and fix the structure before pocket detection (especially a predicted model)
- structural-biology/structure-modification - strip crystallization additives and resolve altlocs before pocket detection
- structural-biology/alphafold-predictions - the apo-pocket and unreliable-rotamer caveats for detecting on a predicted model
- structural-biology/structure-navigation - select chains and HETATM ligands to cross-check pockets against additives
- structural-biology/structure-io - download the biological assembly (not just the asymmetric unit) for inter-chain pockets
- chemoinformatics/virtual-screening - dock a library into a chosen pocket (presupposes a known site)
- chemoinformatics/ml-docking-rescoring - rescore docked poses in the detected site

## References

- Le Guilloux V, Schmidtke P, Tuffery P (2009) Fpocket: an open source platform for ligand pocket detection. *BMC Bioinformatics* 10:168. (fpocket; Voronoi tessellation and alpha spheres)
- Schmidtke P, Barril X (2010) Understanding and predicting druggability. A high-throughput method for detection of drug binding sites. *J Med Chem* 53(15):5858-5867. (fpocket druggability score; trained on druggable/undruggable cavities)
- Krivak R, Hoksza D (2018) P2Rank: machine learning based tool for rapid and accurate prediction of ligand binding sites from protein structure. *J Cheminform* 10:39. (P2Rank; template-free ML ligandability)
- Tian W, Chen C, Lei X, Zhao J, Liang J (2018) CASTp 3.0: computed atlas of surface topography of proteins. *Nucleic Acids Res* 46(W1):W363-W367. (surface pockets, cavities, channels; area and volume)
- Volkamer A, Kuhn D, Grombacher T, Rippmann F, Rarey M (2012) Combining global and local measures for structure-based druggability predictions. *J Chem Inf Model* 52(2):360-372. (DoGSiteScorer; SVM druggability)
- Cimermancic P, et al. (2016) CryptoSite: expanding the druggable proteome by characterization and prediction of cryptic binding sites. *J Mol Biol* 428(4):709-719. (cryptic site = pocket in holo but not apo)
- Schmidtke P, Bidon-Chanal A, Luque FJ, Barril X (2011) MDpocket: open-source cavity detection and characterization on molecular dynamics trajectories. *Bioinformatics* 27(23):3276-3285. (pocket tracking over an ensemble; cryptic/transient pockets)
<!-- END FILE: structural-biology/binding-site-detection/SKILL.md -->

## 子目录：structural-biology/geometric-analysis

<!-- BEGIN FILE: structural-biology/geometric-analysis/SKILL.md -->
---
name: bio-structural-biology-geometric-analysis
description: Measures geometric properties of protein structures with Biopython Bio.PDB - interatomic distances, distance matrices, bond and dihedral angles (phi/psi/chi, Ramachandran), superposition and RMSD, center of mass, radius of gyration, and solvent accessible surface area (SASA). Use when deciding that RMSD depends on BOTH the superposition and the atom selection (a global all-atom RMSD is dominated by flexible loops and hinge motion and is NOT a cross-protein similarity metric); choosing the metric that matches the question (RMSD for same-molecule displacement, TM-score for same-fold, lDDT for superposition-free local model quality - the quantity pLDDT predicts); recognizing Superimposer needs an equal-length ordered atom-to-atom correspondence; and reporting SASA only alongside its probe radius (1.4A water, Shrake-Rupley) with a preference for relative SASA. Keywords RMSD, TM-score, lDDT, SASA, Shrake-Rupley, superposition, Kabsch, dihedral, Ramachandran, radius of gyration.
tool_type: python
primary_tool: Bio.PDB
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: biopython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Geometric Analysis

**"Calculate the RMSD between two conformations"** -> superimpose on a defined atom correspondence, then report deviation.
- Python: `Bio.PDB.Superimposer` (SVD/Kabsch); `Bio.PDB.qcprot` for speed in tight loops
**"How buried is this residue?"** -> compute solvent accessible surface area and normalize to a per-residue maximum.
- Python: `Bio.PDB.SASA.ShrakeRupley`, then relative SASA against a max-ASA scale

## Governing Principle: the metric IS the question

RMSD is NOT a property of two structures. It is a property of two structures GIVEN a superposition AND an atom selection - change either and the number changes. Report what was aligned (CA-only? a defined core? all-atom?) or the number is uninterpretable.

Global all-atom RMSD is a mean of SQUARED per-atom deviations after a least-squares rigid-body fit, so it is dominated by the worst-fitting atoms. A structure whose 150-residue core is essentially identical but whose 10-residue loop or a hinge-rotated domain swings out by 15A reports a "bad" whole-molecule RMSD (often 4-8A) that hides a near-perfect core. RMSD is also length-dependent (longer proteins accumulate larger RMSD for the same local quality) and is NOT a cross-protein similarity metric - it is only meaningful when a genuine 1:1 correspondence exists (same protein, two states; a model vs its native).

`Superimposer` requires an equal-length, ORDERED atom-to-atom correspondence. Feeding it mismatched or unequal atom lists is the classic error; it computes the optimal fit (Kabsch via SVD), it does NOT solve which atom maps to which. Structures with different sequences need a structure-based alignment FIRST to establish the correspondence (see alignment/structural-alignment), then superposition.

SASA depends on the PROBE RADIUS (1.4A water is a convention, not a constant of nature), the algorithm (Bio.PDB `ShrakeRupley` is Shrake-Rupley only; `freesasa` offers Lee-Richards and LCPO), and whether hydrogens are present. A SASA number without its probe radius is meaningless, and absolute SASA in A^2 is not portable across tools. Prefer RELATIVE SASA (residue SASA / max-ASA of that residue type) using the Tien et al 2013 max-ASA scale.

Backbone phi/psi and omega/cis-peptides are a VALIDATION signal, not a description: a residue in a sterically disallowed Ramachandran region usually means a modeling error, not exotic biology. This skill computes the angles; interpreting outliers as quality flags belongs to structural-biology/structure-validation.

### Decision: which comparison metric

| Metric | Answers (use for) | Caveat | Who reports it |
|---|---|---|---|
| RMSD on a defined core | same molecule, how far did it move after best-fit | needs a real 1:1 correspondence; outlier-dominated (squared mean); length- and selection-dependent; NOT cross-protein | Bio.PDB `Superimposer.rms` |
| TM-score (>0.5 = same fold) | different proteins - same fold? fold recognition | length-normalized and outlier-resistant, but asymmetric (state the reference chain); needs an alignment first | TM-align / US-align (alignment/structural-alignment) |
| GDT-TS / GDT-HA | CASP-style full-model accuracy vs native | superposition-based but fraction-within-cutoff, not a squared mean | LGA / CASP assessors |
| lDDT (0-100; pLDDT for AlphaFold models) | local model quality, multi-domain, without picking a superposition | superposition-free, immune to domain motion; the quantity pLDDT predicts | OpenStructure lDDT / AlphaFold pLDDT |

For cross-protein or fold-similarity work, do not stretch RMSD - route to alignment/structural-alignment (TM-align / Foldseek / DALI). For Ramachandran/omega as a quality gate, route to structural-biology/structure-validation.

## Distance Between Atoms

```python
from Bio.PDB import PDBParser
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

chain = structure[0]['A']
atom1, atom2 = chain[100]['CA'], chain[200]['CA']

distance = atom1 - atom2                              # Atom subtraction returns the distance directly
print(f'Distance: {distance:.2f} A')
print(np.linalg.norm(atom1.coord - atom2.coord))     # Equivalent via numpy on the .coord arrays
```

## Distance Matrix

```python
import numpy as np
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

ca_atoms = [r['CA'] for r in structure.get_residues() if r.has_id('CA') and r.id[0] == ' ']  # id[0]==' ' drops waters/hetero
n = len(ca_atoms)

dist = np.zeros((n, n))
for i in range(n):
    for j in range(i + 1, n):
        dist[i, j] = dist[j, i] = ca_atoms[i] - ca_atoms[j]
print(f'Distance matrix: {dist.shape}')
```

## Bond Angle

```python
import numpy as np
from Bio.PDB import PDBParser, calc_angle

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

res = structure[0]['A'][100]
angle = calc_angle(res['N'].get_vector(), res['CA'].get_vector(), res['C'].get_vector())  # calc_angle needs Vector, not .coord
print(f'N-CA-C angle: {np.degrees(angle):.1f} deg')
```

## Backbone Dihedrals (phi / psi)

```python
import numpy as np
from Bio.PDB import PDBParser, calc_dihedral

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')
chain = structure[0]['A']

prev, curr, nxt = chain[99], chain[100], chain[101]
phi = calc_dihedral(prev['C'].get_vector(), curr['N'].get_vector(), curr['CA'].get_vector(), curr['C'].get_vector())
psi = calc_dihedral(curr['N'].get_vector(), curr['CA'].get_vector(), curr['C'].get_vector(), nxt['N'].get_vector())
print(f'phi={np.degrees(phi):.1f}  psi={np.degrees(psi):.1f}')
```

## Ramachandran Angles for All Residues

```python
import numpy as np
from Bio.PDB import PDBParser, PPBuilder

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

ppb = PPBuilder()                                    # PPBuilder builds peptides from connectivity, so chain breaks split them
rama = []
for pp in ppb.build_peptides(structure):
    for res, (phi, psi) in zip(pp, pp.get_phi_psi_list()):
        if phi is not None and psi is not None:      # None at termini and chain breaks by design - skip, do not fabricate
            rama.append((res.resname, np.degrees(phi), np.degrees(psi)))
print(f'{len(rama)} residues with phi/psi')
```

Outliers in disallowed regions are usually refinement errors, not biology - interpret them as a quality gate in structural-biology/structure-validation.

## Chi Angles (Sidechain Dihedrals)

```python
import numpy as np
from Bio.PDB import PDBParser, calc_dihedral

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')
res = structure[0]['A'][100]

if res.has_id('CB') and res.has_id('CG'):            # Gly/Ala lack CB/CG; chi atom quartets are residue-type specific
    chi1 = calc_dihedral(res['N'].get_vector(), res['CA'].get_vector(), res['CB'].get_vector(), res['CG'].get_vector())
    print(f'Chi1: {np.degrees(chi1):.1f} deg')
```

## Superimposing Structures and RMSD

```python
from Bio.PDB import PDBParser, Superimposer

parser = PDBParser(QUIET=True)
ref = parser.get_structure('ref', 'reference.pdb')
mob = parser.get_structure('mobile', 'mobile.pdb')

ref_ca = [r['CA'] for r in ref.get_residues() if r.has_id('CA') and r.id[0] == ' ']
mob_ca = [r['CA'] for r in mob.get_residues() if r.has_id('CA') and r.id[0] == ' ']
n = min(len(ref_ca), len(mob_ca))                    # Superimposer needs EQUAL-LENGTH ORDERED lists; it does NOT solve correspondence
ref_ca, mob_ca = ref_ca[:n], mob_ca[:n]              # Naive truncation is only valid when residues already correspond 1:1

sup = Superimposer()
sup.set_atoms(ref_ca, mob_ca)                        # Optimal rigid-body fit via SVD/Kabsch
print(f'RMSD (CA): {sup.rms:.2f} A')
rotation, translation = sup.rotran                   # The fitted transform, for reuse on other atoms
sup.apply(mob.get_atoms())                           # Mutates mob in place - copy first if the originals are still needed
```

QCP alternative for speed in tight loops (MD, all-vs-all): `from Bio.PDB.qcprot import QCPSuperimposer` (module `Bio.PDB.qcprot`; historically `Bio.PDB.QCPSuperimposer`), same `set_atoms` / `.rms` / `.rotran` / `apply` interface and identical optimum.

## Per-Residue Deviation After Superposition

Fitting minimizes the squared mean, so a global scalar hides where the structures actually differ. A per-residue deviation plot exposes the outlier domination directly.

```python
import numpy as np
from Bio.PDB import PDBParser, Superimposer

parser = PDBParser(QUIET=True)
ref = parser.get_structure('ref', 'reference.pdb')
mob = parser.get_structure('mobile', 'mobile.pdb')

ref_ca = [r['CA'] for r in ref.get_residues() if r.has_id('CA') and r.id[0] == ' ']
mob_ca = [r['CA'] for r in mob.get_residues() if r.has_id('CA') and r.id[0] == ' ']
n = min(len(ref_ca), len(mob_ca))
ref_ca, mob_ca = ref_ca[:n], mob_ca[:n]

sup = Superimposer()
sup.set_atoms(ref_ca, mob_ca)
sup.apply([a for a in mob_ca])                        # Move only the paired CA set into the fitted frame
deviation = np.array([r - m for r, m in zip(ref_ca, mob_ca)])
print(f'core (<2A) residues: {(deviation < 2.0).sum()} / {n}')   # 2A is a common rigid-core cutoff, not a law
print(f'max deviation: {deviation.max():.2f} A at index {deviation.argmax()}')
```

## Center of Mass and Radius of Gyration

```python
import numpy as np
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

atoms = list(structure.get_atoms())
coords = np.array([a.coord for a in atoms])
masses = np.array([{'C': 12.0, 'N': 14.0, 'O': 16.0, 'S': 32.0, 'H': 1.0}.get(a.element, 12.0) for a in atoms])

com = (masses[:, None] * coords).sum(axis=0) / masses.sum()
print(f'Center of mass: {com}')

rg = np.sqrt(np.mean(np.sum((coords - coords.mean(axis=0)) ** 2, axis=1)))  # Unweighted radius of gyration
print(f'Radius of gyration: {rg:.2f} A')
```

## Vector Operations

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

v1 = structure[0]['A'][100]['CA'].get_vector()
v2 = structure[0]['A'][101]['CA'].get_vector()

diff = v2 - v1
print(f'length: {diff.norm():.2f}  unit: {diff.normalized()}')
cross = v1 ** v2                                      # ** is cross product on Vector objects
dot = v1 * v2                                         # * is dot product on Vector objects
```

## Solvent Accessible Surface Area (SASA)

```python
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

sr = ShrakeRupley(probe_radius=1.40, n_points=100)   # 1.4A = water radius (convention); a SASA number is meaningless without its probe radius
sr.compute(structure, level='R')                     # level R attaches .sasa on each residue; children sum to parents
print(f'total SASA: {sum(r.sasa for r in structure.get_residues() if hasattr(r, "sasa")):.1f} A^2')
```

## Relative SASA and Burial

Absolute SASA is not portable across tools. For burial, normalize to a per-residue maximum (Tien et al 2013 theoretical Gly-X-Gly max-ASA).

```python
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

MAX_ASA = {'ALA': 129.0, 'ARG': 274.0, 'ASN': 195.0, 'ASP': 193.0, 'CYS': 167.0, 'GLU': 223.0, 'GLN': 225.0, 'GLY': 104.0, 'HIS': 224.0, 'ILE': 197.0, 'LEU': 201.0, 'LYS': 236.0, 'MET': 224.0, 'PHE': 240.0, 'PRO': 159.0, 'SER': 155.0, 'THR': 172.0, 'TRP': 285.0, 'TYR': 263.0, 'VAL': 174.0}

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')
ShrakeRupley().compute(structure, level='R')

buried = 0
for res in structure.get_residues():
    if res.resname in MAX_ASA and hasattr(res, 'sasa'):
        rsa = res.sasa / MAX_ASA[res.resname]
        if rsa < 0.20:                               # RSA < 0.20 is the common buried heuristic (a rule of thumb, not a law)
            buried += 1
print(f'buried residues (RSA < 0.20): {buried}')
```

## Secondary-Structure Assignment (DSSP)

Secondary structure is an INTERPRETATION, not a value stored in the file: DSSP, STRIDE, and P-SEA legitimately disagree by 1-2 residues at helix and strand termini, so name the tool and version and never mix assignments from two tools in one analysis. DSSP places the backbone amide hydrogen itself and scores an electrostatic H-bond energy, so it needs no explicit hydrogens, and it processes only the FIRST model of an ensemble. The binary was renamed `dssp` -> `mkdssp` (v4) and must be installed separately.

```python
from Bio.PDB import PDBParser, DSSP

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')
model = structure[0]                                  # DSSP runs on ONE model only

dssp = DSSP(model, 'protein.pdb', dssp='mkdssp')      # pass the current binary name explicitly
codes = [dssp[k][2] for k in dssp.keys()]             # 8-state: H G I helix, E B strand, T S P - other
helix = sum(c in 'HGI' for c in codes)
strand = sum(c in 'EB' for c in codes)
print(f'helix {helix}, strand {strand}, other {len(codes) - helix - strand} of {len(codes)}')
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| `Superimposer` errors on differing list sizes | atom lists unequal length; it needs a 1:1 ordered correspondence | match residues by id, or for sequence-different structures align first (alignment/structural-alignment) |
| DSSP helix/strand counts differ from another tool | DSSP, STRIDE, P-SEA disagree at element termini; no ground truth | name the tool+version; never mix assignments; compare like-for-like |
| RMSD is 4-8A for structures that clearly share a fold | global fit dominated by flexible loops/termini/hinge; mean of SQUARED deviations | fit on a defined rigid core, report core vs mobile separately; or use per-residue deviation / TM-score |
| RMSD differs between runs on the "same" pair | different atom selection (CA vs all-atom) or superposition | state the correspondence and fit selection explicitly and hold it constant |
| Ranking models of different length by RMSD | RMSD is length-dependent and not a cross-protein metric | use TM-score (length-normalized) or lDDT (superposition-free) |
| `calc_angle`/`calc_dihedral` AttributeError | passed numpy arrays (`.coord`) not `Vector` objects | pass `atom.get_vector()` |
| phi/psi is `None` at chain ends | terminal residues lack a preceding C or following N | skip `None`; `get_phi_psi_list` returns `None` at breaks/termini by design |
| SASA disagrees with a published value | different probe radius, radii set, algorithm, or H atoms present | recompute all structures like-for-like in one tool; report probe_radius; prefer relative SASA |
| `.sasa` attribute missing on residues | `compute()` run at the wrong level or read before it | call `sr.compute(entity, level='R')` then read `residue.sasa` |
| Distance matrix polluted by waters/heteroatoms | iterating residues without filtering the hetflag | filter `residue.id[0] == ' '` |
| Chi1 computed for Gly/Ala | those residues have no CB/CG | guard `has_id('CB') and has_id('CG')`; chi quartets are residue-type specific |
| Two crystal forms called "different states" at 2A RMSD | difference within coordinate uncertainty / ensemble spread | compare against B-factors, resolution, and NMR ensemble spread before claiming a state change |
| Calling a predicted model "wrong" where it deviates from a crystal structure | the deviating region may be low-pLDDT, a PAE-uncertain inter-domain float, or the crystal is a different (holo/packing) state | overlay pLDDT/PAE on the deviation before judging (alphafold-predictions); confirm it is not just a state difference |
| Original coordinates changed unexpectedly | `Superimposer.apply` and `atom.transform` mutate in place | copy the structure first if the untransformed coordinates are still needed |

## Related Skills

- structure-io - Parse and write PDB/mmCIF structure files
- structure-navigation - Walk chains, residues, atoms; handle altlocs and disordered residues
- structure-modification - Transform coordinates and edit structures in place
- structural-biology/interface-analysis - Residue contacts, contact maps, and buried-surface interface analysis (NeighborSearch)
- structural-biology/structure-validation - Ramachandran and omega/cis-peptide outliers as a quality gate
- structural-biology/alphafold-predictions - overlay pLDDT/PAE when a compared structure is a predicted model
- structural-biology/modern-structure-prediction - reconcile predicted models via pLDDT/PAE/pTM before RMSD claims
- alignment/structural-alignment - Cross-protein fold comparison and correspondence (TM-align, Foldseek, DALI)

## References

- Cock PJA, et al. (2009) Biopython. *Bioinformatics* 25(11):1422-1423.
- Kabsch W (1976) A solution for the best rotation to relate two sets of vectors. *Acta Crystallogr A* 32:922-923.
- Theobald DL (2005) Rapid calculation of RMSDs using a quaternion-based characteristic polynomial. *Acta Crystallogr A* 61(4):478-480.
- Zhang Y, Skolnick J (2004) Scoring function for automated assessment of protein structure template quality. *Proteins* 57(4):702-710.
- Xu J, Zhang Y (2010) How significant is a protein structure similarity with TM-score = 0.5? *Bioinformatics* 26(7):889-895.
- Mariani V, Biasini M, Barbato A, Schwede T (2013) lDDT: a local superposition-free score for comparing protein structures and models. *Bioinformatics* 29(21):2722-2728.
- Shrake A, Rupley JA (1973) Environment and exposure to solvent of protein atoms. Lysozyme and insulin. *J Mol Biol* 79(2):351-371.
- Tien MZ, Meyer AG, Sydykova DK, Spielman SJ, Wilke CO (2013) Maximum allowed solvent accessibilities of residues in proteins. *PLoS ONE* 8(11):e80635.
<!-- END FILE: structural-biology/geometric-analysis/SKILL.md -->

## 子目录：structural-biology/interface-analysis

<!-- BEGIN FILE: structural-biology/interface-analysis/SKILL.md -->
---
name: bio-structural-biology-interface-analysis
description: Maps protein-protein and protein-ligand interfaces with Bio.PDB, computing contact residues and buried surface area (BSA). Use when choosing a contact cutoff and stating its rationale (heavy-atom 4-5A vs CA-CA 8A vs a SASA-based definition); deciding a contact list is not an interface and computing buried surface area (dSASA/BSA) instead; distinguishing a genuine biological interface from a crystal-packing artifact; identifying ligand-contact or epitope residues; and computing on the biological assembly rather than the asymmetric unit. Keywords interface, buried surface area, BSA, contacts, NeighborSearch, PISA, crystal packing, epitope, binding site, ShrakeRupley.
tool_type: python
primary_tool: Bio.PDB
---

## Version Compatibility

Reference examples tested with: biopython 1.83+, numpy 1.26+, freesasa 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Interface Analysis

**"Which residues contact the ligand / the partner chain?"** -> Threshold interatomic distances and collect residues within a cutoff.
- Python: `Bio.PDB.NeighborSearch(atoms).search_all(cutoff, level='R')` or `.search(center, cutoff, level='R')`

**"Compute the buried surface area of this interface"** -> Subtract complex SASA from the summed SASA of the isolated partners.
- Python: `Bio.PDB.SASA.ShrakeRupley().compute(entity)`, then `BSA = SASA_A + SASA_B - SASA_complex`

**"Is this interface biological or a crystal-packing artifact?"** -> Score interface size and chemistry on the biological assembly, and treat the assignment as a hypothesis.
- Python: Bio.PDB for BSA / H-bonds; PDBePISA for the assembly call (external service)

## Governing Principle

A "contact" is not a physical fact, it is a thresholded distance, and the residue count changes with the cutoff. Heavy-atom pairs within 4-5A capture direct van der Waals contact; CA-CA within 8A captures topological proximity (contact maps, coevolution features) but says nothing about side-chain interaction; 3.5-4.0A heavy-atom is the H-bond / salt-bridge regime. Changing 4A to 5A can shift the contact count substantially, so a contact result is meaningless without its atom set and cutoff stated explicitly (Chakrabarti & Janin 2002 *Proteins* 47:334-343). The trap is reporting "N interface residues" or "N contacts" as if the number were intrinsic.

A contact list is not an interface. The physical interface measure is BURIED SURFACE AREA (BSA, also dSASA): BSA = SASA(part A alone) + SASA(part B alone) - SASA(complex), conventionally halved to report the area buried per partner. All three SASA terms must be computed with identical parameters (same probe radius, radii set, algorithm) or the subtraction is garbage (see geometric-analysis for SASA fundamentals). SASA itself depends on the probe radius (1.4A water default) and the algorithm, so an absolute BSA is only comparable to another BSA computed the same way. Because heavy-atom contacts and BSA are both defined on non-hydrogen atoms, hydrogens are NOT required for either - add them (structure-preparation) only for H-bond/salt-bridge angle geometry, and if H are present keep them consistent across all three SASA terms.

The deepest trap: an interface seen in the deposited ASYMMETRIC UNIT may be a CRYSTAL-PACKING ARTIFACT, not biology. The asymmetric unit is a crystallographic bookkeeping object; the functional molecule is the BIOLOGICAL ASSEMBLY, which may be a subset of the ASU or built from several ASUs by symmetry. Compute interfaces on the biological assembly, not blindly on the ASU (see structure-io for downloading the assembly). PDBePISA (Krissinel & Henrick 2007 *J Mol Biol* 372:774-797) predicts the biological assembly and scores interface stability, but it recovers the correct assembly only ~80-90% of the time and has known false positives, so "biological interface" is a HYPOTHESIS. Larger BSA, more H-bonds and salt bridges, shape complementarity, and evolutionary conservation of interface residues each raise confidence, but each is probabilistic, not proof (Levy 2010 *J Mol Biol* 403:660-670). Corroborate anything load-bearing with solution data (SEC-MALS, SAXS, native MS).

## Decision: contact / interface definition

| Definition | What it captures | Best when | Fails / misleads when |
|---|---|---|---|
| Heavy-atom (non-H) <= 4-5A | Direct physical / vdW contact | Interface residue lists, ligand-contact residues, epitopes | Cutoff unstated; H atoms present shift the count |
| CA-CA <= 8A | Topological proximity of backbones | Contact maps, coevolution / ML features, fold fingerprint | Read as "side chains interact" - it does not imply that |
| Heavy-atom 3.5-4.0A + angle | H-bonds / salt bridges | Chemistry of the interface | Definitions are loose and tool-dependent (state exact criteria) |
| BSA / dSASA (SASA-based) | Physical extent of the interface (area) | Quantifying interface size, biological-vs-crystal | Terms computed with mismatched SASA parameters |

The one-line rule: heavy-atom 4-5A answers "who touches"; CA-CA 8A answers "who is near"; BSA answers "how big is the interface". State the atom set and cutoff every time.

## Decision: biological interface vs crystal contact

| Signal | Biological interface tends to | Crystal contact tends to | Caveat |
|---|---|---|---|
| Buried surface area (per side) | Larger, often > ~800-1000 A^2 | Small, often < ~400 A^2 | Wide overlap; not a hard cutoff |
| H-bonds / salt bridges | More, specific | Few, incidental | Definition-dependent counts |
| Shape complementarity | High | Lower | Not diagnostic alone |
| Interface residue conservation | Conserved across homologs | Not conserved | Needs an alignment / ortholog set |
| PDBePISA assignment | Called stable (CSS toward 1.0) | Called unstable | ~80-90% accurate; known false positives |
| Recurs across crystal forms | Yes | No (packing-specific) | Requires multiple depositions |

Every row is probabilistic. Interface size (BSA) is the single most-used signal, but small biological interfaces (transient/weak complexes) and large crystal contacts both exist, so no one number settles it.

## Contact residues between two chains

**Goal:** List the residues of chain A and chain B that form the interface, under an explicit cutoff.

**Approach:** Build one KD-tree over the interface atoms, query all close pairs at residue level, and keep pairs whose two residues belong to different chains. Heavy-atom cutoff 4.5A (midpoint of the 4-5A vdW-contact regime; excludes H so it is robust to whether H atoms were modeled).

```python
from Bio.PDB import PDBParser, NeighborSearch, Selection

parser = PDBParser(QUIET=True)
structure = parser.get_structure('complex', 'complex.pdb')
model = structure[0]

cutoff = 4.5  # heavy-atom contact; 4-5A captures direct vdW contact, state it always
atoms = [a for a in model.get_atoms() if a.element != 'H']
ns = NeighborSearch(atoms)

interface_a, interface_b = set(), set()
for res1, res2 in ns.search_all(cutoff, level='R'):
    c1, c2 = res1.get_parent().id, res2.get_parent().id
    if c1 == 'A' and c2 == 'B':
        interface_a.add(res1); interface_b.add(res2)
    elif c1 == 'B' and c2 == 'A':
        interface_b.add(res1); interface_a.add(res2)

print(f'Chain A interface residues ({cutoff}A): {len(interface_a)}')
print(f'Chain B interface residues ({cutoff}A): {len(interface_b)}')
```

## Ligand-contact (binding-site / epitope) residues

**Goal:** Identify the protein residues lining a bound ligand or the residues an antibody contacts (structural epitope).

**Approach:** Select the ligand atoms (a HETATM group, hetflag starts with 'H_'), search protein atoms within the cutoff of each, collect unique parent residues. The same pattern with two protein chains yields a structural epitope.

```python
from Bio.PDB import PDBParser, NeighborSearch

parser = PDBParser(QUIET=True)
structure = parser.get_structure('complex', 'complex.pdb')
model = structure[0]

ligand_resname = 'ATP'  # target HETATM group
cutoff = 4.5

ligand_atoms = [a for r in model.get_residues() if r.resname == ligand_resname
                for a in r if a.element != 'H']
protein_atoms = [a for a in model.get_atoms()
                 if a.element != 'H' and a.get_parent().id[0] == ' ']
ns = NeighborSearch(protein_atoms)

pocket = set()
for a in ligand_atoms:
    for res in ns.search(a.coord, cutoff, level='R'):
        pocket.add((res.get_parent().id, res.id[1], res.resname))

for chain, num, name in sorted(pocket):
    print(f'{chain} {name}{num}')
```

## Buried surface area (BSA / dSASA)

**Goal:** Quantify the physical size of a two-chain interface as area buried on complex formation.

**Approach:** Compute SASA on the intact complex, then on each chain in isolation (same ShrakeRupley settings), and take BSA = SASA_A + SASA_B - SASA_complex. Halve for per-partner area. Probe radius 1.4A models a water molecule; keep it identical across all three computations or the subtraction is meaningless.

```python
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

parser = PDBParser(QUIET=True)
sr = ShrakeRupley(probe_radius=1.4)  # 1.4A ~ water; MUST match across all three terms

def chain_sasa(path, keep_chains):
    structure = parser.get_structure('s', path)
    model = structure[0]
    for chain in list(model):
        if chain.id not in keep_chains:
            model.detach_child(chain.id)
    sr.compute(model, level='C')
    return sum(chain.sasa for chain in model)

sasa_complex = chain_sasa('complex.pdb', {'A', 'B'})
sasa_a = chain_sasa('complex.pdb', {'A'})
sasa_b = chain_sasa('complex.pdb', {'B'})

bsa_total = sasa_a + sasa_b - sasa_complex
print(f'Total buried surface area: {bsa_total:.0f} A^2')
print(f'Per partner: {bsa_total / 2:.0f} A^2')  # convention: split half to each side
```

For Lee-Richards SASA or full control of the radii set and probe, use `freesasa` instead of ShrakeRupley (Mitternacht 2016 *F1000Research* 5:189); Bio.PDB provides only Shrake-Rupley. Compute all three terms in the same tool.

## H-bonds and salt bridges (geometric heuristics)

**Goal:** Estimate the specific polar interactions across an interface.

**Approach:** Salt bridge = an acidic side-chain oxygen (Asp/Glu OD/OE) within ~4A of a basic side-chain nitrogen (Arg/Lys/His NZ/NH/NE/ND). These definitions are loose and tool-dependent; state the exact distance (and any angle) used. Without modeled hydrogens, a true H-bond angle cannot be checked, so the distance-only result is an upper bound.

```python
from Bio.PDB import PDBParser, NeighborSearch

parser = PDBParser(QUIET=True)
model = parser.get_structure('c', 'complex.pdb')[0]

acidic = {('ASP', 'OD1'), ('ASP', 'OD2'), ('GLU', 'OE1'), ('GLU', 'OE2')}
basic = {('ARG', 'NH1'), ('ARG', 'NH2'), ('ARG', 'NE'),
         ('LYS', 'NZ'), ('HIS', 'ND1'), ('HIS', 'NE2')}
salt_cutoff = 4.0  # common salt-bridge distance; literature ranges 3.2-5.0A, report the choice

ns = NeighborSearch(list(model.get_atoms()))
bridges = []
for a1, a2 in ns.search_all(salt_cutoff, level='A'):
    k1 = (a1.get_parent().resname, a1.name)
    k2 = (a2.get_parent().resname, a2.name)
    cross = a1.get_parent().get_parent().id != a2.get_parent().get_parent().id
    if cross and ((k1 in acidic and k2 in basic) or (k1 in basic and k2 in acidic)):
        bridges.append((a1.get_parent(), a2.get_parent()))

print(f'Candidate interchain salt bridges (<= {salt_cutoff}A): {len(bridges)}')
```

## PDBePISA for the biological assembly

PDBePISA computes interfaces and predicts the biological assembly from the crystal, reporting interface area, an interface solvation free energy of assembly, the number of H-bonds and salt bridges, and a Complexation Significance Score (CSS, 0-1) ranking each interface by how much it drives assembly. It is a web service (https://www.ebi.ac.uk/pdbe/pisa/) with per-entry results; there is no Bio.PDB binding. Use it to get the assembly call and interface energetics, then treat the assignment as a hypothesis to corroborate (see the biological-vs-crystal table). Do not report the PISA assembly as ground truth.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Contact count changes between runs / papers | Cutoff or atom set not stated or not matched | Fix and report the cutoff and whether H atoms are included |
| "Interface" that vanishes in solution | Computed on the asymmetric unit, not the biological assembly | Download and compute on the biological assembly (structure-io) |
| BSA comes out near zero or negative | SASA terms computed with different parameters or on different files | Use identical ShrakeRupley settings for complex and each isolated part |
| Huge BSA but no biology | Large crystal contact misread as biological | Cross-check H-bonds, conservation, PISA CSS, recurrence across crystal forms |
| Ligand-contact residues missing | Ligand skipped because it is a HETATM, filtered out with waters | Select the ligand by resname/hetflag before filtering standard residues |
| Doubled / impossible contacts at one residue | Alternate conformations (altloc) both counted | Select one altloc before contact search (structure-modification) |
| Interface residues span a chain gap oddly | Missing/disordered residues modeled as absent | Reconcile against SEQRES; missing loops are disorder, not a real gap |
| H-bond angles cannot be computed | No hydrogens modeled in the file | Report distance-only heuristics as an upper bound, or add H first |
| Salt-bridge count disagrees with another tool | Distance/angle definition differs between tools | State exact criteria; definitions are not standardized |
| CA-CA 8A "interface" implies side-chain contact | 8A is topological proximity, not physical contact | Use heavy-atom 4-5A for physical contact claims |
| SASA / BSA not comparable to a literature value | Different probe radius, radii set, or algorithm | Recompute both like-for-like in one tool |
| PISA assembly taken as fact | PISA is ~80-90% accurate with known false positives | Treat as a hypothesis; corroborate with solution data |

## Related Skills

- geometric-analysis - SASA fundamentals, NeighborSearch, distances that this skill builds on
- structure-io - download the biological assembly (not just the asymmetric unit) before interface analysis
- structure-modification - resolve altlocs and strip waters/additives before contact detection
- structure-navigation - select chains, residues, and HETATM ligands by identity
- structure-validation - check the region of interest is well-fit before trusting an interface
- structure-preparation - add hydrogens before checking H-bond/salt-bridge geometry at an interface
- binding-site-detection - de-novo cavity/pocket detection on apo structures (complement to mapping a bound ligand)
- immunoinformatics/epitope-prediction - structural epitope mapping from antibody-antigen complexes
- chemoinformatics/virtual-screening - binding-site definition for docking
- alignment/structural-alignment - superpose complexes before comparing interfaces

## References

- Krissinel E, Henrick K (2007) Inference of macromolecular assemblies from crystalline state. *J Mol Biol* 372(3):774-797. (PISA / PDBePISA; biological-assembly prediction and its failure modes)
- Chakrabarti P, Janin J (2002) Dissecting protein-protein recognition sites. *Proteins* 47(3):334-343. (interface core/rim dissection; contact-definition dependence)
- Levy ED (2010) A simple definition of structural regions in proteins and its use in analyzing interface evolution. *J Mol Biol* 403(4):660-670. (core-rim-support model; 25% RSA burial threshold)
- Shrake A, Rupley JA (1973) Environment and exposure to solvent of protein atoms. Lysozyme and insulin. *J Mol Biol* 79(2):351-371. (Shrake-Rupley SASA underlying BSA)
- Tien MZ, Meyer AG, Sydykova DK, Spielman SJ, Wilke CO (2013) Maximum allowed solvent accessibilities of residues in proteins. *PLoS ONE* 8(11):e80635. (max-ASA scale for relative burial of interface residues)
- Mitternacht S (2016) FreeSASA: an open source C library for solvent accessible surface area calculations. *F1000Research* 5:189. (Lee-Richards alternative to ShrakeRupley)
- Cock PJA, et al. (2009) Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics* 25(11):1422-1423. (Bio.PDB toolkit)
<!-- END FILE: structural-biology/interface-analysis/SKILL.md -->

## 子目录：structural-biology/modern-structure-prediction

<!-- BEGIN FILE: structural-biology/modern-structure-prediction/SKILL.md -->
---
name: bio-structural-biology-modern-structure-prediction
description: Predicts protein and complex structures with deep-learning models (ESMFold, AlphaFold2/ColabFold, AlphaFold3, Chai-1, Boltz-1/2) and reconciles them with confidence metrics. Use when choosing a predictor by input and question rather than novelty (ESMFold single-chain, no-MSA, fast, metagenomic-scale vs AlphaFold3/Chai-1/Boltz for complexes, ligands, nucleic acids, ions, PTMs); recognizing that MSA depth is the dominant accuracy determinant so ESMFold trades accuracy for speed and degrades on orphan proteins; gating a complex on ipTM plus inter-chain PAE, not per-chain pLDDT; reading pLDDT as local confidence, PAE as inter-domain/inter-chain positioning, pTM as global fold; knowing a single prediction is one dominant conformer not an ensemble (no apo/holo, allosteric, or fold-switch states), that these are not variant-effect/ddG/affinity engines, and that a confident prediction is a hypothesis, not an experiment. Keywords ESMFold, AlphaFold3, Chai-1, Boltz-1, ColabFold, ipTM, PAE, pLDDT, MSA depth.
tool_type: python
primary_tool: ESMFold
---

## Version Compatibility

Reference examples tested with: fair-esm 2.0+, biopython 1.83+, numpy 1.26+, requests 2.31+, chai_lab 0.6+, boltz 2.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Modern Structure Prediction

**"Predict the structure of my protein"** -> Map an amino-acid (and optionally ligand/nucleic-acid) sequence to a single 3D model plus per-residue and pairwise confidence.
- Python: ESMFold local via `esm.pretrained.esmfold_v1()` (no MSA); ColabFold/AlphaFold via MMseqs2 MSA; AlphaFold3/Chai-1/Boltz for complexes and ligands.

## Governing Principle: a prediction is a hypothesis, and the predictor is chosen by the input and the question

The trap is treating a prediction as an answer and picking a model by novelty. Two facts govern every decision here. First, MSA depth is the dominant accuracy determinant for the coevolution-based models (AlphaFold2/3, Chai-1, Boltz): quality tracks how well-represented the sequence's family is, not how hard the biology is, so these models excel on deep-MSA families and degrade on orphan, fast-evolving, viral, or de-novo-designed sequences (Jumper 2021 *Nature* 596:583; Lin 2023 *Science* 379:1123). ESMFold is single-sequence with no MSA, so it is fast enough for metagenomic scale but is lower-accuracy on average and degrades hardest exactly where evolutionary signal is thin. Second, a default prediction is ONE dominant conformer, not an ensemble: it does not give apo vs holo, allosteric states, or fold switches, and it carries no Boltzmann populations. MSA subsampling and AF-Cluster sample some alternate states but are unreliable, seed-sensitive hypotheses (Wayment-Steele 2024 *Nature* 625:832), a generality directly challenged by a Matters Arising (Schafer & Porter 2025 *Nature* 638:E8-E12).

Three category errors follow and must be avoided. (1) These are not variant-effect, ddG, or stability engines: a single point mutation barely changes a deep MSA, so wild-type vs mutant predictions come back near-identical with near-identical pLDDT, and the model is insensitive to the mutation by construction (Buel & Walters 2022 *Nat Struct Mol Biol* 29:1; Pak 2023 *PLoS ONE* 18:e0282689). Use AlphaMissense, FoldX/Rosetta ddG, or ESM/EVE variant scores instead. (2) No co-folder gives a trustworthy Kd from geometry: a plausible complex or ligand pose is not evidence of binding or affinity, and CASP16 assessors found co-fold affinity ranking essentially unreliable; Boltz-2's affinity module is a screening prior only, not a measured constant. (3) AF3-class diffusion models can hallucinate confident-looking order in genuinely disordered regions and have measurable chirality violations (~4.4% on PoseBusters) and atom clashes (Abramson 2024 *Nature* 630:493), so every ligand pose needs a physical-validity check. A confident prediction is a starting hypothesis with spatially varying reliability; validate it against experiment before believing any part of it.

## Decision: which predictor for the job

| Job | Preferred | Why / caveat |
|---|---|---|
| Single-domain monomer, MAX accuracy | AlphaFold2 (LocalColabFold) or AlphaFold3 | Deep MSA = best accuracy; AF2 mature and well-understood |
| Monomer, deep MSA, fast and free | ColabFold (MMseqs2 MSA) | 40-60x faster search, near-AF2 accuracy (Mirdita 2022) |
| Metagenomic / genome-scale / triage | ESMFold | Fastest (no MSA); lower accuracy, weak on large/low-family proteins |
| Single-sequence when no homologs exist | ESMFold or Chai-1 (single-seq mode) | Both skip MSA; expect reduced accuracy, sanity-check hard |
| Protein-protein COMPLEX | AF-Multimer / AF3 / Boltz / Chai-1 | Gate on ipTM + inter-chain PAE, NOT per-chain pLDDT |
| Complex WITH ligand/ion/nucleic acid/PTM | AF3, Boltz-1/2, or Chai-1 | Co-folders; validate the POSE (PoseBusters), NOT affinity |
| Binding-affinity PRIOR for screening | Boltz-2 (affinity module) | Screening prior only; a relative affinity score, not a trusted Kd |
| Commercial / on-prem deployment | Boltz-1/2 or Chai-1 (both Apache-2.0/MIT, commercial OK) | AF3 weights are non-commercial (Google terms) |
| Alternative conformational states | AF2 + MSA subsampling / AF-Cluster | UNRELIABLE; hypotheses only, not ensembles or populations |
| Variant effect / stability / pathogenicity | NOT these tools | Insensitive to point mutations; use AlphaMissense/FoldX/ESM |

Licenses drift; verify before deploying. AF2 code Apache-2.0, weights CC-BY-4.0 (permissive). AF3 code Apache-2.0, weights under the non-commercial "AlphaFold 3 Model Parameters Terms of Use", granted on request to non-commercial orgs and received directly from Google (open, not open-source). Boltz-1 and Boltz-2 are MIT (code + weights, commercial use permitted). Chai-1 was relicensed to Apache-2.0 for both code and weights in November 2024 (commercial use, including drug discovery, permitted; it launched Sept 2024 under a restrictive non-commercial license, so older notes may say otherwise - verify terms). ESMFold code/weights are MIT.

## Decision: which confidence metric answers which question

| Metric | Scope | Answers | Read it for |
|---|---|---|---|
| pLDDT (0-100) | Per-residue, LOCAL | How well-placed is this residue's local environment | Trimming; a long <50 stretch usually flags an intrinsically disordered region, not an error |
| PAE (Angstrom) | Residue-pair | Expected error at j when aligned on i | Domain packing, linker geometry, inter-chain arrangement |
| pTM (0-1) | Whole model, GLOBAL | Estimated TM-score of the overall fold | Is the topology plausible (>~0.5) |
| ipTM (0-1) | Interface | Accuracy of relative subunit positioning | Complex interface reliability (>~0.8 likely, <~0.6 unreliable) |

The load-bearing reads: high per-residue pLDDT with a high inter-domain PAE block means each domain is confident internally but their relative arrangement is unknown - do not trust the linker or domain-domain interface. For a complex, judge the interface on ipTM plus the inter-chain PAE block; a complex can have high pLDDT on both chains and still be a garbage interface. AF-Multimer ranks models by 0.8*ipTM + 0.2*pTM, deliberately weighting the interface. All these metrics are self-reported and can be confidently wrong together on out-of-distribution inputs.

## Predict a monomer with ESMFold (fast, no MSA)

**Goal:** Get a single-chain model in seconds without building an MSA, and read pLDDT off the B-factor column.

**Approach:** Run ESMFold locally with `esm.pretrained.esmfold_v1()`; the hosted esmatlas API is intermittently down (SSL/internal-server errors) so local is the reliable path. pLDDT rides in the B-factor column but is confidence, not a temperature factor.

```python
import torch
import esm

model = esm.pretrained.esmfold_v1().eval().to('cuda')  # needs ~16 GB GPU for typical proteins

sequence = 'MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH'
with torch.no_grad():
    pdb_text = model.infer_pdb(sequence)  # returns a PDB string with pLDDT in B-factor column
with open('esmfold.pdb', 'w') as f:
    f.write(pdb_text)
```

Hosted-API fallback (only when no GPU and the endpoint is up):

```python
import requests

url = 'https://api.esmatlas.com/foldSequence/v1/pdb/'
resp = requests.post(url, data=sequence, timeout=300)  # 300 s: long sequences take minutes
resp.raise_for_status()
pdb_text = resp.text
```

## Read per-residue confidence

**Goal:** Summarize where a prediction is trustworthy so downstream use is restricted to confident cores.

**Approach:** pLDDT sits in the B-factor column of every prediction (ESMFold, AlphaFold, co-folders). Band it into the standard cutoffs; a contiguous very-low band usually marks a disordered region, not a failure.

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('pred', 'esmfold.pdb')
plddt = {res.id[1]: res['CA'].get_bfactor() for res in structure[0].get_residues() if 'CA' in res}

# Bands from the AlphaFold/EBI convention: >90 very high, 70-90 confident, 50-70 low, <50 very low.
very_high = [r for r, s in plddt.items() if s > 90]
confident = [r for r, s in plddt.items() if 70 <= s <= 90]
very_low = [r for r, s in plddt.items() if s < 50]  # likely intrinsically disordered, not wrong
print(f'mean pLDDT {sum(plddt.values())/len(plddt):.1f}; {len(very_low)} very-low residues')
```

## Predict a complex and gate on the interface

**Goal:** Model a protein-protein or protein-ligand complex and decide whether to believe the interface.

**Approach:** Use a co-folder (Chai-1 or Boltz), then accept the interface only if ipTM and the inter-chain PAE block agree. Chai-1 and Boltz run from the CLI; both default to no MSA and can call an MSA server. Verify the exact CLI with `--help` since these packages evolve fast.

```python
import subprocess

# Chai-1: one FASTA with a header per chain; '--use-msa-server' fetches an MSA (improves accuracy).
# Reference invocation - confirm with `chai-lab fold --help`.
subprocess.run(['chai-lab', 'fold', '--use-msa-server', 'complex.fasta', 'chai_out/'], check=True)

# Boltz: FASTA or YAML input; YAML is required to request the Boltz-2 affinity module.
# Reference invocation - confirm with `boltz predict --help`.
subprocess.run(['boltz', 'predict', 'complex.fasta', '--use_msa_server'], check=True)
```

**Goal:** Gate the predicted interface before trusting any cross-chain distance.

**Approach:** Read ipTM and pTM from the confidence JSON the co-folder writes, and band the interface on ipTM. Below ~0.6 the interface is unreliable or the chains likely do not interact; 0.6-0.8 is uncertain and the inter-chain PAE block decides; a confident interface wants ipTM > ~0.8.

```python
import json

with open('chai_out/scores.model_idx_0.json') as f:  # exact filename varies by tool/version
    conf = json.load(f)
iptm = conf.get('iptm')
ptm = conf.get('ptm')
if iptm is None or iptm < 0.6:        # <0.6: unreliable or chains likely do not interact
    print(f'interface NOT reliable (ipTM={iptm}); inspect inter-chain PAE before any claim')
elif iptm < 0.8:                      # 0.6-0.8: uncertain - the inter-chain PAE block decides
    print(f'interface UNCERTAIN (ipTM={iptm:.2f}); gate on the inter-chain PAE block')
else:
    ptm_str = f'{ptm:.2f}' if ptm is not None else 'NA'  # some score files omit pTM
    print(f'interface confident (ipTM={iptm:.2f}, pTM={ptm_str}); still confirm with inter-chain PAE')
```

## Prepare an AlphaFold3 server job

**Goal:** Submit a monomer or complex to the AlphaFold Server without local weights.

**Approach:** The server takes a JSON job listing entities and seeds; multiple seeds sample the diffusion head, so request several and inspect the spread rather than trusting one sample.

```python
import json

def af3_job(sequences, name='prediction', seeds=(1, 2, 3)):
    entities = [{'proteinChain': {'sequence': s, 'count': 1}} for s in sequences]
    return json.dumps([{'name': name, 'modelSeeds': list(seeds), 'sequences': entities}], indent=2)

job_json = af3_job(['MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH'])
```

## Reconcile multiple predictions

**Goal:** Compare models from different predictors and locate the regions they agree on.

**Approach:** Superimpose on a fixed CA correspondence and report pairwise RMSD, but treat RMSD as fold-agreement only where the aligned selection is stated; prefer a length-normalized fold metric (TM-score) for cross-method fold claims. See geometric-analysis for TM-score and superposition caveats.

```python
from Bio.PDB import PDBParser, Superimposer

def ca_rmsd(pdb_a, pdb_b):
    parser = PDBParser(QUIET=True)
    a = [r['CA'] for r in parser.get_structure('a', pdb_a)[0].get_residues() if 'CA' in r]
    b = [r['CA'] for r in parser.get_structure('b', pdb_b)[0].get_residues() if 'CA' in r]
    n = min(len(a), len(b))  # Superimposer needs an equal-length ordered atom correspondence
    sup = Superimposer()
    sup.set_atoms(a[:n], b[:n])
    return sup.rms

print(f'ESMFold vs AF3 CA-RMSD: {ca_rmsd("esmfold.pdb", "af3.pdb"):.2f} Angstrom')
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Mutant and wild-type predictions look identical | A point mutation barely changes a deep MSA; the model is insensitive to it | Do not read structure/pLDDT deltas as variant effect; use AlphaMissense, FoldX, or ESM |
| Confident model but wrong in the lab | Prediction is one dominant conformer, not an ensemble; no apo/holo/allosteric states | Treat as a hypothesis; sample states cautiously (MSA subsampling) and validate experimentally |
| Complex accepted on high per-chain pLDDT | pLDDT is intra-chain local confidence, blind to the interface | Gate on ipTM + inter-chain PAE block; reject interface if ipTM < ~0.6 (0.6-0.8 uncertain) |
| Long low-pLDDT stretch treated as an error | Low pLDDT correlates with intrinsic disorder | Read <50 regions as likely IDRs (biologically real flexibility), not modeling failures |
| Two domains confident but arrangement wrong | High intra-domain pLDDT with high inter-domain PAE | Trust each domain, not the relative orientation or linker; split at high-PAE hinges |
| ESMFold much worse than AlphaFold on an orphan | ESMFold is single-sequence and degrades where evolutionary signal is thin | Use MSA-based ColabFold/AF for orphan/de-novo proteins; keep ESMFold for scale |
| Ligand pose has wrong chirality or clashes | AF3-class diffusion can violate stereochemistry (~4.4% chirality) | Run PoseBusters/validity checks on every pose; do not assume physical plausibility |
| Reported Kd from a co-fold pose | Co-folders give geometry, not affinity; CASP16 found affinity ranking unreliable | Use Boltz-2 affinity only as a screening prior; confirm with FEP or experiment |
| esmatlas API returns SSL / internal-server error | The hosted ESMFold endpoint is intermittently down | Run ESMFold locally via `esm.pretrained.esmfold_v1()` |
| Two predictions "disagree" but were run differently | Different MSA depth/source, recycles, seeds, or templates change the answer | Report the MSA pipeline and settings; two predictions are not comparable if these differ |
| RMSD between predictions looks huge for the same fold | Global all-atom RMSD is dominated by flexible loops and needs a stated selection | Superimpose on CA/core and report the selection; use TM-score for fold agreement |

## Related Skills

- alphafold-predictions - Retrieve precomputed AlphaFold DB models and read their pLDDT/PAE
- structure-io - Parse and write predicted PDB/mmCIF files
- geometric-analysis - RMSD, superposition, and TM-score caveats for comparing models
- structure-navigation - Walk chains/residues/atoms in a predicted structure
- structure-preparation - Trim, add hydrogens, and protonate a predicted model before docking or MD
- binding-site-detection - Detect pockets on a predicted model (inherits apo/rotamer uncertainty)
- alignment/structural-alignment - Structure-based alignment before comparing sequence-different models
- chemoinformatics/virtual-screening - Dock into a predicted pocket (inherits predicted rotamer/backbone error)
- chemoinformatics/ml-docking-rescoring - Rescore co-folded poses; co-fold geometry is not affinity

## References

Jumper J, et al. Highly accurate protein structure prediction with AlphaFold. Nature 596:583-589 (2021). doi:10.1038/s41586-021-03819-2.
Abramson J, et al. Accurate structure prediction of biomolecular interactions with AlphaFold 3. Nature 630:493-500 (2024). doi:10.1038/s41586-024-07487-w.
Lin Z, et al. Evolutionary-scale prediction of atomic-level protein structure with a language model. Science 379:1123-1130 (2023). doi:10.1126/science.ade2574.
Evans R, et al. Protein complex prediction with AlphaFold-Multimer. bioRxiv 2021.10.04.463034 (2021, preprint). doi:10.1101/2021.10.04.463034.
Baek M, et al. Accurate prediction of protein structures and interactions using a three-track neural network. Science 373:871-876 (2021). doi:10.1126/science.abj8754.
Mirdita M, et al. ColabFold: making protein folding accessible to all. Nat Methods 19:679-682 (2022). doi:10.1038/s41592-022-01488-1.
Wayment-Steele HK, et al. Predicting multiple conformations via sequence clustering and AlphaFold2. Nature 625:832-839 (2024). doi:10.1038/s41586-023-06832-9.
Schafer JW, ..., Porter LL (2025) Sequence clustering confounds AlphaFold2 (Matters Arising). *Nature* 638:E8-E12. doi:10.1038/s41586-024-08267-2.
Buel GR, Walters KJ. Can AlphaFold2 predict the impact of missense mutations on structure? Nat Struct Mol Biol 29:1-2 (2022). doi:10.1038/s41594-021-00714-2.
Pak MA, et al. Using AlphaFold to predict the impact of single mutations on protein stability and function. PLoS ONE 18:e0282689 (2023). doi:10.1371/journal.pone.0282689.
Wohlwend J, et al. Boltz-1: democratizing biomolecular interaction modeling. bioRxiv 2024.11.19.624167 (2024, preprint). doi:10.1101/2024.11.19.624167.
Chai Discovery. Chai-1: decoding the molecular interactions of life. bioRxiv 2024.10.10.615955 (2024, preprint). doi:10.1101/2024.10.10.615955.
<!-- END FILE: structural-biology/modern-structure-prediction/SKILL.md -->

## 子目录：structural-biology/structure-io

<!-- BEGIN FILE: structural-biology/structure-io/SKILL.md -->
---
name: bio-structural-biology-structure-io
description: Reads, writes, downloads, and converts macromolecular structures with Biopython Bio.PDB. Use when choosing a format (mmCIF/PDBx vs legacy PDB vs BinaryCIF) for a structure that may exceed PDB's ~62-chain / 99,999-atom limits; when residue numbers do not match the paper because of auth_* vs label_* numbering (MMCIFParser defaults auth_residues=True); when metadata (resolution, method, R-free) is missing because Bio.PDB drops it and MMCIF2Dict is needed; when the deposited coordinates are the asymmetric unit and the biological assembly must be downloaded separately; when downloading from RCSB (files.rcsb.org, PDBList); and when a legacy MMTF path is dead (RCSB retired MMTF July 2024, use BinaryCIF).
tool_type: python
primary_tool: Bio.PDB
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: biopython 1.85+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure I/O

**"Read a structure file"** -> Parse a deposited coordinate file into an in-memory SMCRA tree, or fetch it from a wwPDB mirror.
- Python: `Bio.PDB.MMCIFParser().get_structure('id', 'file.cif')`, `Bio.PDB.PDBParser()`, `Bio.PDB.PDBList()`

## Governing Principle

mmCIF (PDBx) is the canonical modern format; the legacy fixed-column PDB format is a frozen, lossy container, and a "parse everything as PDB" reflex silently truncates or fails on anything large. The PDB format was frozen in 2012 and cannot physically exceed 99,999 atoms (5-digit serial), ~62 chains (single alphanumeric chain id), or 9,999 residues per chain (wwPDB file-format documentation; the PDB archive itself is Berman et al. 2000 *Nucleic Acids Res* 28:235-242). Large assemblies (ribosomes, capsids, spliceosomes, most big cryo-EM structures) therefore exist ONLY as mmCIF, and converting a big mmCIF down to PDB renames multi-character chains and overflows serial numbers, silently corrupting any downstream tool that keys on chain id. mmCIF has been the wwPDB archive standard since 2014 and mandatory for crystallographic depositions since July 2019.

Two further traps compound this. First, Bio.PDB is PERMISSIVE by design: it reads malformed files, and it silently drops anisotropic B-factors (ANISOU), collapses each disordered atom to its highest-occupancy alternate, and never models most metadata (resolution, method, R-free, entity graph, assembly operators). Parse-success is not data integrity. Second, the deposited coordinates for an X-ray entry are usually the ASYMMETRIC UNIT, a crystallographic bookkeeping object that is frequently NOT the biologically functional oligomer -- so any interface, oligomeric-state, or buried-surface question must first obtain the biological assembly (Krissinel & Henrick 2007 *J Mol Biol* 372:774). "One chain in the file" is never evidence of a monomer.

The escape hatch for all three ceilings (assembly generation, very large structures, full mmCIF fidelity) is gemmi (Wojdyr 2022 *JOSS* 7:4200); Bio.PDB cannot apply the assembly operators itself. Prefer Bio.PDB for teaching, small structures, and hierarchy walks; reach for gemmi when the questions above appear.

## Decision: which format

| Format | Best when | Fails when | Hard limits |
|--------|-----------|------------|-------------|
| mmCIF / PDBx (`.cif`, `.cif.gz`) | Any modern default; large assemblies; full metadata; auth+label numbering; ANISOU/entities | A legacy tool only reads fixed-column PDB | None |
| Legacy PDB (`.pdb`, `.ent`) | Small structure feeding an old tool that demands PDB columns | Structure exceeds the format's limits (silently truncates/renames) | 99,999 atoms, ~62 chains, 9,999 resseq/chain, single-char chain id |
| BinaryCIF (`.bcif`, `.bcif.gz`) | Compact binary transport at bandwidth/scale; the current binary format | An ecosystem still expects the retired MMTF | None (lossless mmCIF encoding) |
| MMTF (`.mmtf`) | Nothing new -- RCSB stopped serving MMTF on 2 July 2024 | Any live download (the endpoint is decommissioned); treat as read-only-legacy | Retired upstream |

## Decision: Bio.PDB vs gemmi

| Task | Tool | Why |
|------|------|-----|
| Hierarchy walk, small X-ray/NMR structure, teaching | Bio.PDB | Readable SMCRA tree, pure Python, ubiquitous |
| Read metadata Bio.PDB drops (resolution, method, R-free, assembly ops) | Bio.PDB `MMCIF2Dict` | Raw category access without object-model loss |
| Generate the biological assembly from deposited coords | gemmi | Applies `_pdbx_struct_oper_list`; Bio.PDB has no operator-application code |
| Very large structure (>100k atoms), many structures, fast neighbor search | gemmi | C++ core scales; Bio.PDB's pure-Python tree is slow/memory-heavy |
| mmCIF round-trip without data loss (entities, label scheme, ANISOU) | gemmi | Full PDBx data model; writes hybrid-36 serials when >99,999 |

## Required Imports

```python
from Bio.PDB import PDBParser, MMCIFParser, PDBIO, MMCIFIO, PDBList, Select
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.binary_cif import BinaryCIFParser
```

## Parse an mmCIF File (the modern default)

```python
from Bio.PDB import MMCIFParser

# auth_residues/auth_chains default to True: numbering matches the paper/UniProt.
parser = MMCIFParser(QUIET=True)
structure = parser.get_structure('4hhb', '4hhb.cif')

# label numbering is contiguous 1..N with no insertion codes -- a DIFFERENT scheme.
label_parser = MMCIFParser(QUIET=True, auth_residues=False, auth_chains=False)
label_structure = label_parser.get_structure('4hhb', '4hhb.cif')
```

Setting `auth_residues=False` renumbers to the mmCIF internal label scheme, so residue 100 in one parse is a different residue in the other. This is the single most common "my selection points at the wrong residue" bug. auth is what matches the literature and sequence databases; label is gap-free internal bookkeeping. Pick one scheme and stay in it.

## Parse a Legacy PDB File

```python
from Bio.PDB import PDBParser

# QUIET=True suppresses PDBConstructionWarning (discontinuous chains, missing occupancy).
parser = PDBParser(QUIET=True)
structure = parser.get_structure('1crn', '1crn.pdb')
```

## Parse a BinaryCIF File (compact binary, replaces MMTF)

```python
from Bio.PDB.binary_cif import BinaryCIFParser

# .get_structure(id, source); gz is handled transparently.
parser = BinaryCIFParser()
structure = parser.get_structure('1gbt', '1gbt.bcif.gz')
```

MMTF is intentionally absent here. RCSB retired it on 2 July 2024 and `MMTFParser.get_structure_from_url` targets a decommissioned service; BinaryCIF is the replacement.

## Read Metadata Bio.PDB Drops (MMCIF2Dict)

```python
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

# MMCIF2Dict returns category -> list[str]; index [0] and cast yourself.
meta = MMCIF2Dict('4hhb.cif')
resolution = meta.get('_refine.ls_d_res_high', ['NA'])[0]
method = meta.get('_exptl.method', ['NA'])[0]
r_free = meta.get('_refine.ls_R_factor_R_free', ['NA'])[0]
r_work = meta.get('_refine.ls_R_factor_R_work', ['NA'])[0]
```

The parser's thin `structure.header` omits resolution/R-free for many files; the dict reaches anything in the mmCIF, including assembly operators the object model never builds.

## Download from RCSB (PDBList)

```python
from Bio.PDB import PDBList

pdbl = PDBList()

# pdir=None writes into a two-char divided subdirectory tree (e.g. hh/4hhb.cif),
# NOT the current directory; pass pdir='.' to control the location.
path = pdbl.retrieve_pdb_file('4HHB', pdir='.', file_format='mmCif')

# file_format 'pdb' fetches legacy PDB only when the entry fits the format.
legacy_path = pdbl.retrieve_pdb_file('4HHB', pdir='.', file_format='pdb')
```

`file_format='mmCif'` (that exact casing) is the current default recommendation. `retrieve_pdb_file` has no `assembly_num` parameter in current Biopython -- download the assembly directly (below).

## Download the Biological Assembly (Bio.PDB cannot build it)

```python
import gzip, shutil, urllib.request

# The ASU is often not the functional oligomer; RCSB pre-applies the operators
# in the -assemblyN file, so downloading it is safer than regenerating.
pdb_id = '1abc'
url = f'https://files.rcsb.org/download/{pdb_id.upper()}-assembly1.cif.gz'
urllib.request.urlretrieve(url, f'{pdb_id}-assembly1.cif.gz')
with gzip.open(f'{pdb_id}-assembly1.cif.gz', 'rb') as fin, open(f'{pdb_id}-assembly1.cif', 'wb') as fout:
    shutil.copyfileobj(fin, fout)
```

Bio.PDB has no operator-application code, so if only the deposited ASU is on disk it cannot construct the assembly -- use the RCSB assembly file or gemmi's `transform_to_assembly`.

## Write a Structure

```python
from Bio.PDB import PDBParser, MMCIFIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1crn', '1crn.pdb')

# Writing mmCIF preserves multi-char chains and >99,999 serials; PDB cannot.
io = MMCIFIO()
io.set_structure(structure)
io.save('1crn_out.cif')
```

## Write a Subset with the Select Class

```python
from Bio.PDB import PDBParser, PDBIO, Select

class ProteinChainSelect(Select):
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def accept_chain(self, chain):
        return chain.id == self.chain_id

    def accept_residue(self, residue):
        # id[0] is the hetflag: ' ' standard, 'W' water, 'H_XXX' hetero.
        return residue.id[0] == ' '

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1crn', '1crn.pdb')

io = PDBIO()
io.set_structure(structure)
io.save('chain_A_protein.pdb', ProteinChainSelect('A'))
```

Override any of `accept_model`, `accept_chain`, `accept_residue`, `accept_atom` to return truthy to keep. Writing a large mmCIF back out as PDB through PDBIO is where multi-character chains and serial overflow silently corrupt the output.

## Capture Warnings for an Unfamiliar File

```python
from Bio.PDB import PDBParser
import warnings

# QUIET=True is the reflex, but it hides 'chain is discontinuous' -- the warning
# that flags a numbering gap or a merge the parser should not have made.
parser = PDBParser(QUIET=False)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    structure = parser.get_structure('unknown', 'unknown.pdb')
    for w in caught:
        print(w.message)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Residue numbers do not match the paper / a UniProt mapping | Parsed with `auth_residues=False`, so numbering is the label scheme | Use the default `auth_residues=True`; only switch to label for gap-free internal indexing, never mix schemes |
| `resolution`/`R-free` is `None` from `structure.header` | Bio.PDB's header dict is thin and omits refinement metadata | Read `_refine.ls_d_res_high`, `_refine.ls_R_factor_R_free`, `_exptl.method` via `MMCIF2Dict` |
| `TypeError: retrieve_pdb_file() got an unexpected keyword 'assembly_num'` | Current Biopython `PDBList` has no `assembly_num` parameter | Download `...-assembly1.cif.gz` from files.rcsb.org directly (or use gemmi) |
| Downloaded file is not in the current directory | `pdir=None` writes a two-char divided subdirectory tree (`hh/4hhb.cif`) | Pass an explicit `pdir='.'` (or the target dir) to `retrieve_pdb_file` |
| MMTF download 404s / connection fails | RCSB retired MMTF on 2 July 2024; the endpoint is gone | Use BinaryCIF (`.bcif`) or mmCIF; treat MMTF files as read-only-legacy |
| Chains renamed and atom serials wrong after PDB output | A large mmCIF exceeded PDB's ~62-chain / 99,999-atom limits on write | Stay in mmCIF (`MMCIFIO`), or use gemmi's hybrid-36 writer |
| Analyzing a "monomer" that is really half a dimer | Computed on the deposited ASU, not the biological assembly | Fetch the `-assembly1` file (or generate with gemmi) before any interface/oligomer analysis |
| Download URL 404s for a newly deposited entry | The 4-char id space is being exhausted (~2028) and RCSB is phasing in extended 12-char ids (`pdb_00006uv8`) | Use the full extended id in the `files.rcsb.org` path; a hard-coded 4-char assumption breaks once extended ids arrive |
| Anisotropic B-factors (ANISOU) lost after a Bio.PDB round-trip | ANISOU is parsed but not reliably written back | Preserve the original file, or round-trip through gemmi when ANISOU matters |
| Distances/clashes look wrong at a partially disordered site | A disordered atom silently forwards to its highest-occupancy altloc | Enumerate altlocs with `atom.disordered_get_list()` and set an explicit altloc policy (see structure-navigation) |
| `KeyError` fetching a residue by integer, e.g. `chain[100]` | Residue id is the tuple `(hetflag, resseq, icode)`; insertion codes and hetero break the bare-int path | Key on the full 3-tuple, e.g. `chain[(' ', 100, ' ')]` |
| `BinaryCIFParser` import fails from `Bio.PDB` | It lives in the submodule `Bio.PDB.binary_cif`, not the top-level package | `from Bio.PDB.binary_cif import BinaryCIFParser` |
| Silent wrong results on a malformed file that "parsed fine" | Bio.PDB is permissive; parse-success is not data integrity | Parse with `QUIET=False` and inspect `PDBConstructionWarning`s for unfamiliar files |

## Related Skills

- structure-navigation - Walk the SMCRA tree, handle altlocs/insertion codes, extract observed vs SEQRES sequence
- structure-modification - Transform coordinates, strip waters/hetero safely, edit B-factors before writing
- geometric-analysis - Measure distances, angles, SASA, and superimpose once the correct assembly is loaded
- interface-analysis - Analyze the interfaces that only exist in the biological assembly, not the ASU
- structure-validation - Read resolution/R-free/clashscore to judge whether the loaded model is trustworthy
- structure-preparation - Add hydrogens/protonation and fill atoms on the loaded assembly before docking or MD
- alignment/structural-alignment - Superpose sequence-different structures that Bio.PDB's ordered correspondence cannot handle
- database-access/uniprot-access - Map structure residues back to a UniProt reference sequence

## References

- Berman HM, Westbrook J, Feng Z, Gilliland G, Bhat TN, Weissig H, Shindyalov IN, Bourne PE (2000). The Protein Data Bank. *Nucleic Acids Res* 28(1):235-242. DOI 10.1093/nar/28.1.235.
- Cock PJA, Antao T, Chang JT, Chapman BA, Cox CJ, Dalke A, Friedberg I, Hamelryck T, Kauff F, Wilczynski B, de Hoon MJL (2009). Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics* 25(11):1422-1423. DOI 10.1093/bioinformatics/btp163.
- Hamelryck T, Manderick B (2003). PDB file parser and structure class implemented in Python. *Bioinformatics* 19(17):2308-2310. DOI 10.1093/bioinformatics/btg332.
- Wojdyr M (2022). GEMMI: A library for structural biology. *Journal of Open Source Software* 7(73):4200. DOI 10.21105/joss.04200.
- Kunzmann P, Hamacher K (2018). Biotite: a unifying open source computational biology framework in Python. *BMC Bioinformatics* 19:346. DOI 10.1186/s12859-018-2367-z.
- Kim H, Mirdita M, Steinegger M (2023). Foldcomp: a library and format for compressing and indexing large protein structure sets. *Bioinformatics* 39(4):btad153. DOI 10.1093/bioinformatics/btad153.
- Krissinel E, Henrick K (2007). Inference of macromolecular assemblies from crystalline state. *J Mol Biol* 372(3):774-797. DOI 10.1016/j.jmb.2007.05.022.
- RCSB PDB (2024). Switch from MMTF to BinaryCIF: RCSB ceased serving MMTF on 2 July 2024. https://www.rcsb.org/news/65a1af31c76ca3abcc925d0c
- wwPDB. File formats and the PDB (legacy format frozen 2012; mmCIF archive standard 2014; 99,999-atom / 62-chain limits; large entries mmCIF-only). https://www.wwpdb.org/documentation/file-formats-and-the-pdb
<!-- END FILE: structural-biology/structure-io/SKILL.md -->

## 子目录：structural-biology/structure-modification

<!-- BEGIN FILE: structural-biology/structure-modification/SKILL.md -->
---
name: bio-structural-biology-structure-modification
description: Modifies protein structures in place with Biopython Bio.PDB - transforms coordinates, strips waters/heteroatoms, overloads the B-factor column, renumbers, and builds entities. Use when applying a rotation matrix and needing to know whether it is row-convention (Entity.transform, Superimposer) or column-convention (REMARK 350 / _pdbx_struct_oper_list assembly operators) so geometry is not silently mirrored; when overloading B-factors with pLDDT/conservation for coloring and needing to preserve the destroyed originals; when stripping solvent by HETFLAG (r.id[0]) rather than residue name so catalytic metals and cofactors survive; and when building or copying entities through StructureBuilder/Select without breaking SMCRA parent-child links or the (hetflag, resseq, icode) id tuple. Keywords transform, rotation matrix, occupancy, assembly operators.
tool_type: python
primary_tool: Bio.PDB
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: biopython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure Modification

**"Move this chain onto that one and strip the waters"** -> mutate coordinates and the entity tree in place, then write a new file.
- Python: `Entity.transform(rot, tran)` for coordinates, `detach_child` / `PDBIO(select=...)` for filtering, `StructureBuilder` for building

## Governing Principle: every edit mutates in place, and the rotation convention is the load-bearing trap

Bio.PDB has no immutable copy semantics. `atom.coord = ...`, `residue.id = ...`, `chain.detach_child(...)`, and `Entity.transform(...)` all mutate the parsed object directly, so the moment a downstream step still needs the original, a `copy.deepcopy` must be taken first (a plain reference is not a copy).

The trap that silently corrupts geometry is the rotation convention. Bio.PDB `Superimposer`, `SVDSuperimposer`, and `Entity.transform(rot, tran)` apply the transform as `dot(coords, rot) + tran` - coordinates are treated as ROW vectors post-multiplied by `rot`, so the `rot` these classes hand back is the TRANSPOSE of the textbook rotation matrix. Biological-assembly operators are the opposite: REMARK 350 and mmCIF `_pdbx_struct_oper_list` matrices are COLUMN-convention (`R @ x + t`). Feeding a column-convention `R` straight into `Entity.transform` (or writing `np.dot(R, atom.coord)` against a row-convention source) applies the transpose and yields a mirrored or wrongly-rotated structure that still looks plausible. Prefer `Entity.transform` / `atom.transform` (which own the row convention) over hand-rolled `np.dot`, and transpose any column-convention operator before passing it in.

Three more edits destroy data quietly: overloading the B-factor column with a per-residue scalar (pLDDT, conservation) DESTRUCTIVELY overwrites the real temperature factors - and for AlphaFold models the column already IS pLDDT, so overwrite it and the confidence signal is gone; save the originals first. Stripping solvent by residue NAME instead of the HETFLAG (`r.id[0]`) deletes functional metals, cofactors, and modified residues (MSE) mid-chain. And building or copying entities without wiring the SMCRA parent-child links, or renumbering without carrying the full `(hetflag, resseq, icode)` id tuple, makes the writer emit broken or collided records.

## Decision: which transform path

| Matrix source | Convention | Apply as | Failure if mixed |
|---|---|---|---|
| `Superimposer.rotran` / `SVDSuperimposer.get_rotran` | row (`coords @ rot`) | `Entity.transform(rot, tran)` | none - same convention |
| `Entity.transform` / `atom.transform` | row (`coords @ rot`) | pass `rot` as-is | none |
| REMARK 350 / `_pdbx_struct_oper_list` assembly operators | column (`R @ x + t`) | `Entity.transform(R.T, t)` | column `R` applied row -> mirrored/rotated wrong |
| `Bio.PDB.vectors.rotaxis(theta, Vector)` | row (built for `.transform`) | `Entity.transform(rot, tran)` | none |
| Raw math / textbook `R` via `np.dot` | column (`R @ x`) | `R @ coord + t` explicitly, consistently | inconsistent left/right multiply |

## Decision: how to strip solvent and hetero

| Strategy | Filter | Deletes | Use when |
|---|---|---|---|
| By HETFLAG, water only | `r.id[0] == 'W'` | ordered/crystallographic waters | safe default before docking/MD prep |
| By explicit deny-list | `r.resname in {'HOH','SO4','GOL','EDO','PEG'}` | named solvent/cryoprotectant only | keeping ligands and metals |
| By blanket HETFLAG | `r.id[0] != ' '` | ALL hetero incl. Zn/Mg/heme/FAD/MSE | almost never - breaks binding sites |
| By residue name (naive) | `r.resname == 'HOH'` | misses `'W'`-flagged waters, keeps some | avoid - HETFLAG is authoritative |

## Transforming Coordinates

```python
from Bio.PDB import PDBParser, PDBIO
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Entity.transform applies coords @ rot + tran (row convention) to every atom in place.
identity = np.identity(3)
translation = np.array([10.0, 0.0, 0.0])
structure.transform(identity, translation)

io = PDBIO()
io.set_structure(structure)
io.save('translated.pdb')
```

## Rotation Around an Axis

```python
from Bio.PDB import PDBParser
from Bio.PDB.vectors import rotaxis, Vector
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# rotaxis returns a row-convention matrix intended for Entity/atom.transform.
rot = rotaxis(np.radians(90), Vector(0, 0, 1))

# Rotate about the center of mass: pick tran so the center is the fixed point of coords @ rot + tran.
center = np.array([a.coord for a in structure.get_atoms()]).mean(axis=0)
tran = center - center @ rot
structure.transform(rot, tran)
```

## Applying an External / Assembly Operator

```python
from Bio.PDB import PDBParser
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# REMARK 350 / _pdbx_struct_oper_list operators are column-convention: newcoord = R @ coord + t.
R = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
t = np.array([25.0, 0.0, 0.0])

# Entity.transform expects the row convention, so transpose the column-convention R first.
structure.transform(R.T, t)
```

## Center Structure at Origin

```python
from Bio.PDB import PDBParser
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

center = np.array([a.coord for a in structure.get_atoms()]).mean(axis=0)
structure.transform(np.identity(3), -center)
```

## Removing Atoms, Residues, and Chains

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')
model = structure[0]

# Detach hydrogens; collect ids first so the child dict is not mutated mid-iteration.
for residue in model.get_residues():
    for atom_id in [a.id for a in residue if a.element == 'H']:
        residue.detach_child(atom_id)

# Detach whole chains by id.
if model.has_id('B'):
    model.detach_child('B')

io = PDBIO()
io.set_structure(structure)
io.save('cleaned.pdb')
```

## Stripping Solvent by HETFLAG

**Goal:** Remove crystallographic water without deleting functional heteroatoms.

**Approach:** Filter on the residue-id HETFLAG (`r.id[0]`), which is `'W'` for water and `'H_<name>'` for other hetero groups - not on the residue name, which silently keeps `'W'`-flagged waters and cannot distinguish a catalytic metal from a buffer ion.

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# 'W' HETFLAG isolates water; a blanket r.id[0] != ' ' would also delete Zn/Mg/heme/FAD and MSE.
for chain in structure[0]:
    for res_id in [r.id for r in chain if r.id[0] == 'W']:
        chain.detach_child(res_id)

io = PDBIO()
io.set_structure(structure)
io.save('no_water.pdb')
```

## Extracting a Selection with PDBIO Select

```python
from Bio.PDB import PDBParser, PDBIO, Select

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Select writes a filtered copy without mutating the parsed tree.
class CoreChain(Select):
    def accept_chain(self, chain):
        return chain.id == 'A'
    def accept_residue(self, residue):
        return residue.id[0] == ' ' and 50 <= residue.id[1] <= 100

io = PDBIO()
io.set_structure(structure)
io.save('coreA_50_100.pdb', CoreChain())
```

## Overloading the B-factor Column (Destructive)

**Goal:** Paint a per-residue scalar (conservation, pLDDT) into the B-factor column for viewer coloring.

**Approach:** Overwriting `atom.bfactor` DESTROYS the real temperature factors (and for AlphaFold models overwrites the pLDDT already stored there), so snapshot the originals before writing, set the score on EVERY atom of the residue, and let the viewer autoscale rather than hand-scaling.

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Snapshot originals: this column is a real temperature factor (or AlphaFold pLDDT) until overwritten.
original_bfactors = {atom.get_full_id(): atom.bfactor for atom in structure.get_atoms()}

conservation = {100: 9.0, 101: 5.0, 102: 3.0}
for residue in structure.get_residues():
    score = conservation.get(residue.id[1])
    if score is None:
        continue
    for atom in residue:
        atom.bfactor = score  # set on all atoms so per-atom coloring is not patchy

io = PDBIO()
io.set_structure(structure)
io.save('colored.pdb')  # do not feed this file back to refinement/validation
```

## Modifying Occupancy

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Occupancy must stay consistent with altlocs: complementary altlocs should sum to <= 1.
for atom in structure[0]['A'].get_atoms():
    atom.occupancy = 1.0

io = PDBIO()
io.set_structure(structure)
io.save('occupancy_set.pdb')
```

## Renumbering Residues

A sequential renumber like the one below is safe ONLY for internal bookkeeping. To renumber a structure so it matches the UniProt CANONICAL numbering (for figures or mutation mapping), a sequential or fixed-offset renumber SILENTLY MISALIGNS wherever the construct has an expression tag, an unresolved N-terminus, an engineered mutation, or a missing-density loop - which is almost always. Map residue-by-residue through SIFTS / the author `auth_seq_id` scheme instead (see structure-navigation for the observed-vs-SEQRES-vs-UniProt distinction and database-access/uniprot-access for the SIFTS mapping); never assume position N in the file is UniProt residue N.

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')
chain = structure[0]['A']

# Preserve the (hetflag, ..., icode) tuple; only the resseq middle field changes.
# Assign into a temporary range first to avoid colliding with existing ids mid-loop.
for offset, residue in enumerate(list(chain)):
    hetflag, _, icode = residue.id
    residue.id = (hetflag, offset + 10000, icode)
for new_seq, residue in enumerate(list(chain), start=1):
    hetflag, _, icode = residue.id
    residue.id = (hetflag, new_seq, icode)

io = PDBIO()
io.set_structure(structure)
io.save('renumbered.pdb')
```

## Building a Structure with StructureBuilder

**Goal:** Construct a valid SMCRA tree from coordinates alone.

**Approach:** `StructureBuilder` wires the Structure > Model > Chain > Residue > Atom parent-child links automatically, which is why the writer emits valid records - hand-assembling `Atom` objects without `add` leaves orphans.

```python
from Bio.PDB import StructureBuilder, PDBIO
import numpy as np

sb = StructureBuilder.StructureBuilder()
sb.init_structure('built')
sb.init_model(0)
sb.init_chain('A')
sb.init_seg(' ')
sb.init_residue('ALA', ' ', 1, ' ')
sb.init_atom('N', np.array([-1.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'N', 1, 'N')
sb.init_atom('CA', np.array([0.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'CA', 2, 'C')
sb.init_atom('C', np.array([1.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'C', 3, 'C')
sb.init_atom('O', np.array([1.5, 1.0, 0.0]), 20.0, 1.0, ' ', 'O', 4, 'O')

io = PDBIO()
io.set_structure(sb.get_structure())
io.save('built_structure.pdb')
```

## Copying a Chain (Preserving SMCRA Links)

```python
from Bio.PDB import PDBParser, PDBIO
import copy

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# deepcopy carries the whole subtree with intact parent-child links; reassign id and detach the old parent.
new_chain = copy.deepcopy(structure[0]['A'])
new_chain.id = 'B'
new_chain.detach_parent()
structure[0].add(new_chain)

io = PDBIO()
io.set_structure(structure)
io.save('duplicated_chain.pdb')
```

## Merging Two Structures Without ID Collisions

```python
from Bio.PDB import PDBParser, PDBIO
import copy

parser = PDBParser(QUIET=True)
struct1 = parser.get_structure('s1', 'structure1.pdb')
struct2 = parser.get_structure('s2', 'structure2.pdb')

# Assign explicit non-colliding ids from a free pool; chr(ord(id)+10) breaks on multi-char/adjacent ids.
used = {c.id for c in struct1[0]}
free = (c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c not in used)
for chain in list(struct2[0]):
    moved = copy.deepcopy(chain)
    moved.id = next(free)
    moved.detach_parent()
    struct1[0].add(moved)

io = PDBIO()
io.set_structure(struct1)
io.save('merged.pdb')
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Rotated structure looks mirrored or points the wrong way | Column-convention operator (REMARK 350 / `_pdbx_struct_oper_list`) applied with the row-convention `Entity.transform` | Transpose first: `structure.transform(R.T, t)`; or apply `R @ coord + t` explicitly |
| Superimposer rotation gives garbage when reused via `np.dot(rot, coord)` | `Superimposer.rotran` is row-convention (`coords @ rot`); `np.dot(rot, coord)` applies the transpose | Use `Entity.transform(rot, tran)` or `coord @ rot + tran` |
| Original structure changed after a transform | All edits mutate in place; a reference is not a copy | `copy.deepcopy(structure)` before modifying |
| B-factors lost / AlphaFold confidence gone after coloring | Writing a scalar into `atom.bfactor` overwrites the temperature factor (or pLDDT) | Snapshot originals first; never send the overloaded file to refinement |
| Catalytic metal or cofactor missing after "removing hetero" | Stripped by `r.id[0] != ' '` or by residue name, deleting Zn/Mg/heme/MSE | Strip water only (`r.id[0] == 'W'`) or use an explicit deny-list |
| `RuntimeError: dictionary changed size during iteration` | Detaching children while iterating the parent | Collect ids into a list first, then `detach_child` |
| `KeyError` when accessing a renumbered residue | Reduced id to `id[1]`, dropping the `(hetflag, ..., icode)` tuple | Key on the full tuple; only display `id[1]` |
| Writer emits truncated or duplicate records | Renumber/merge produced a colliding `(hetflag, resseq, icode)` or chain id | Renumber via a temporary offset; assign ids from a checked free pool |
| Built structure writes an empty or broken file | `Atom`/`Residue` objects created without `add`, leaving SMCRA links unset | Use `StructureBuilder` or wire `add` at every level |
| Only one alternate conformer written after occupancy edit | Altloc/occupancy edited independently so occupancies no longer sum to <= 1 | Keep complementary altlocs consistent as a pair |
| Chain-merge crashes on multi-character chain ids | `chr(ord(chain.id) + 10)` assumes single adjacent characters | Assign explicit ids from a free-id pool |
| mmCIF metadata or anisotropic B-factors dropped after a Bio.PDB round-trip | Bio.PDB does not round-trip ANISOU or the full mmCIF model | For mmCIF-fidelity edits use gemmi; keep Bio.PDB for PDB-scale work |

## Related Skills

- structure-io - Parse and write structure files; mmCIF vs PDB format ceilings
- structure-navigation - Walk chains/residues/atoms and the SMCRA id tuple; observed-vs-SEQRES-vs-UniProt numbering before renumbering
- database-access/uniprot-access - SIFTS mapping of structure residues to UniProt canonical numbering (do not renumber sequentially)
- geometric-analysis - Superimpose structures and read back the row-convention rotation
- interface-analysis - Analyze interfaces after generating the biological assembly
- structure-preparation - Add hydrogens, protonation states, and missing atoms (this skill only removes/edits)
- sequence-manipulation/seq-objects - Generate sequences from modified structures

## References

- Hamelryck T, Manderick B. 2003. PDB file parser and structure class implemented in Python. *Bioinformatics* 19(17):2308-2310. doi:10.1093/bioinformatics/btg332
- Cock PJA, Antao T, Chang JT, et al. 2009. Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics* 25(11):1422-1423. doi:10.1093/bioinformatics/btp163
- Berman HM, Westbrook J, Feng Z, et al. 2000. The Protein Data Bank. *Nucleic Acids Res* 28(1):235-242. doi:10.1093/nar/28.1.235
- wwPDB / RCSB PDB. Biological assembly operators (REMARK 350; `_pdbx_struct_assembly_gen` and `_pdbx_struct_oper_list`). https://www.rcsb.org/docs/programmatic-access/file-download-services
<!-- END FILE: structural-biology/structure-modification/SKILL.md -->

## 子目录：structural-biology/structure-navigation

<!-- BEGIN FILE: structural-biology/structure-navigation/SKILL.md -->
---
name: bio-structural-biology-structure-navigation
description: Navigate the Bio.PDB SMCRA hierarchy (Structure-Model-Chain-Residue-Atom) safely, surfacing the heterogeneity it hides by default. Use when deciding how to handle altloc/DisorderedAtom conformers before a distance or RMSD, indexing residues insertion-code-safe with the full (hetflag, resseq, icode) tuple, choosing the ATOM/observed vs SEQRES/canonical vs UniProt sequence, selecting the right Model for an NMR ensemble, filtering waters/hetero/metals correctly, and reconciling auth vs label numbering. Keywords SMCRA, altloc, DisorderedAtom, insertion code, SEQRES, PPBuilder, auth_seq_id.
tool_type: python
primary_tool: Bio.PDB
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: biopython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure Navigation

**"Walk the chains, residues, and atoms; pull out the sequence"** -> Traverse the Structure-Model-Chain-Residue-Atom (SMCRA) tree, but treat every level as a lossy projection that hides heterogeneity unless asked otherwise.
- Python: `structure[0]['A'][(' ', 100, ' ')]['CA'].coord` for full-tuple direct access

## Governing Principle: SMCRA is a convenient tree that HIDES heterogeneity by default

The SMCRA model (Structure > Model > Chain > Residue > Atom) is a readable in-memory tree, but its defaults quietly collapse the very heterogeneity that changes the answer. Five traps recur, and none of them raises an error - the code runs and returns a plausible-looking number computed on the wrong thing.

1. A `DisorderedAtom` silently forwards every uncaught call to ONE child - the HIGHEST-OCCUPANCY altloc, not literally altloc 'A'. So `get_atoms()`, `.coord`, distances, clashes, and RMSDs all use a single conformer, invisibly, even when the active site is 60/40 disordered. This is the #1 correctness trap. Enumerate with `is_disordered()` and `disordered_get_list()`; never let both altlocs of one atom enter the same geometric calculation.
2. The residue id is a 3-tuple `(hetflag, resseq, icode)`. Naive `residue.id[1]` drops both the hetero flag and the INSERTION CODE, so antibody residues 100, 100A, 100B collapse onto one key; `chain[100]` works only until an insertion code, a hetero residue, or an altloc residue exists at that number, then raises a KeyError that looks like the residue is missing. Key on the full tuple; reduce to `id[1]` only for display.
3. The sequence PPBuilder extracts is the OBSERVED (ATOM-record) sequence with missing-density gaps silently concatenated away - it is NOT the SEQRES/construct/UniProt canonical sequence. A disordered 12-residue loop becomes 12 vanished characters with no marker, so mapping conservation or alignment columns by string position is off-by-many after the first gap. Map through residue NUMBERS (auth_seq_id) or SIFTS, never by string index.
4. NMR and multi-state files have multiple `Model` objects. Iterating chains without first selecting a model conflates conformers; `structure[0]` silently picks one NMR member and over-claims precision. Ask "how many models and why" first.
5. mmCIF carries two numbering schemes: auth (matches the paper, has insertion codes, can be negative/gapped) and label (gapless 1..N, no icodes). `MMCIFParser` defaults to auth; flip `auth_residues=False` and residue 100 becomes a different residue. Pick one scheme and stay in it.

## Decision: which sequence source

These three "sequences" are routinely conflated; each answers a different question and the wrong one silently misindexes everything downstream.

| Source | What it is | Get it via | Use when | Fails when |
|--------|-----------|------------|----------|------------|
| ATOM / observed | Only residues with modeled coordinates; gaps concatenated away | `PPBuilder().build_peptides()` then `pp.get_sequence()` | Per-atom geometry, contacts, extracting exactly what was resolved | Aligning to UniProt/MSA by string position (gaps shift the frame) |
| SEQRES / declared | Full sequence the depositor says is in the crystal, including unresolved residues | `SeqIO.parse(file, 'pdb-seqres')` or `'cif-seqres'` | Knowing the true construct length, locating missing loops | Assuming every SEQRES residue has coordinates (it does not) |
| UniProt / canonical | The reference biological sequence (no tags, no engineered mutations) | `database-access/uniprot-access` + SIFTS residue mapping | Mapping conservation/domains/mutations onto structure positions | Assuming construct == canonical (tags, point mutations, chimeras differ) |

## Decision: residue selection idiom

Filter on the hetflag (`id[0]`), not the residue name, and know exactly what each idiom keeps and drops.

| Goal | Idiom | Keeps / drops correctly? |
|------|-------|--------------------------|
| Standard amino acids only | `r.id[0] == ' '` | Correct; drops water, ligands, and modified residues |
| Water | `r.id[0] == 'W'` | Correct; water hetflag is `'W'`, NOT `'H_'` - a `startswith('H_')` water strip MISSES water |
| Ligands and hetero groups | `r.id[0].startswith('H_')` | Also catches modified residues (MSE, SEP, PTR) mid-chain - not just free ligands |
| Strip hetero blindly | `r.id[0] != ' '` | DANGEROUS - deletes catalytic metals, cofactors, AND selenomethionine (MSE) out of the chain |
| A specific residue type | `r.resname == 'ARG'` | Fine for type queries; never use resname to classify water vs ligand vs standard |

## Required Imports

```python
from Bio.PDB import PDBParser, MMCIFParser, PPBuilder, CaPPBuilder, Selection
from Bio.Data.PDBData import protein_letters_3to1, protein_letters_3to1_extended
```

## Accessing Hierarchy Levels

```python
parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

model = structure[0]                       # first model (see NMR caveat below)
chain = model['A']
residue = chain[(' ', 100, ' ')]           # full id tuple - insertion-code and hetero safe
residue_bare = chain[100]                   # convenience path; breaks on icode/hetero/altloc at 100
atom = residue['CA']
```

## Iterating Over Structure

```python
for model in structure:
    for chain in model:
        for residue in chain:
            hetflag, resseq, icode = residue.id   # keep the whole tuple, not resseq alone
            for atom in residue:
                print(f'{chain.id}:{resseq}{icode}:{atom.name}')

for chain in structure.get_chains():
    print(f'Chain: {chain.id}')
```

## Enumerating Disordered Atoms (the highest-value pattern)

```python
# A DisorderedAtom forwards uncaught calls to its highest-occupancy child by default,
# so plain iteration measures ONE conformer. Enumerate every altloc explicitly.
for atom in residue:
    if atom.is_disordered():
        for alt in atom.disordered_get_list():   # each alt is a real Atom with its own coord/occupancy
            print(f'{atom.name} altloc {alt.altloc}: occ={alt.occupancy} coord={alt.coord}')
    else:
        print(f'{atom.name}: coord={atom.coord}')

# disordered_select(altloc) mutates the active child GLOBALLY - reset it when done
if atom.is_disordered():
    atom.disordered_select(atom.disordered_get_id_list()[0])
```

## Disordered Residues (microheterogeneity / point mutation at one site)

```python
# Residue.is_disordered() returns 1 for a NORMAL residue that merely holds altloc atoms and 2 for a
# true DisorderedResidue (two resnames at one position); disordered_get_id_list/disordered_select
# exist ONLY on the latter, so gate on == 2 (or isinstance DisorderedResidue) or this AttributeErrors.
if residue.is_disordered() == 2:
    names = residue.disordered_get_id_list()      # alternative resnames at this position
    residue.disordered_select('ALA')              # pick one by resname before any geometry
```

## Extracting the Observed Sequence (know it has silent gaps)

```python
# PPBuilder builds peptides from OBSERVED atoms via a C-N distance criterion and breaks at gaps;
# the returned Seq has missing-density loops concatenated away with no gap marker.
ppb = PPBuilder()
for pp in ppb.build_peptides(structure):
    print(f'observed segment len={len(pp.get_sequence())}: {pp.get_sequence()}')

# CaPPBuilder connects residues whose CA atoms are within ~4.3 Angstroms, so it bridges
# small backbone breaks - useful for CA-only/broken chains, but it can mis-join true gaps.
ca_ppb = CaPPBuilder()
segments = ca_ppb.build_peptides(structure)
```

## Reading the Declared (SEQRES) Sequence and Locating Gaps

```python
from Bio import SeqIO

# SEQRES = the full declared sequence, including residues with no coordinates.
for record in SeqIO.parse('protein.pdb', 'pdb-seqres'):
    print(f'{record.id} declared length {len(record.seq)}')

# header['missing_residues'] (populated when get_header=True) lists unmodeled residues -
# the difference between SEQRES and observed. Reconcile before mapping to UniProt.
parser = PDBParser(QUIET=True, get_header=True)
structure = parser.get_structure('protein', 'protein.pdb')
missing = structure.header.get('missing_residues', [])
```

## Converting Residue Names (modified residues map to X or drop)

```python
# protein_letters_3to1 is the strict 20-aa map (unknown resname -> KeyError, so use .get).
# protein_letters_3to1_extended additionally maps modified residues (MSE->M, SEP->S, PTR->Y).
seq = ''
for residue in chain:
    if residue.id[0] == ' ' or residue.resname in protein_letters_3to1_extended:
        seq += protein_letters_3to1_extended.get(residue.resname, 'X')
```

## Selecting Entities and Full Identifiers

```python
residues = Selection.unfold_entities(structure, 'R')   # S/M/C/R/A level codes
atoms = Selection.unfold_entities(chain, 'A')

atom = structure[0]['A'][(' ', 100, ' ')]['CA']
print(atom.get_full_id())   # ('protein', 0, 'A', (' ', 100, ' '), ('CA', ' '))
```

## Working with NMR Ensembles (do not conflate models)

```python
n_models = len(structure)                  # NMR = conformer ensemble, X-ray/cryo-EM usually 1
if n_models > 1:
    # Compute per-model and report the distribution; never average coordinates across models.
    for model in structure:
        ca = [r['CA'].coord for r in model.get_residues() if r.has_id('CA')]
        print(f'model {model.id}: {len(ca)} CA atoms')
```

## Reading mmCIF with an Explicit Numbering Scheme

```python
# MMCIFParser defaults to auth numbering (matches the paper, has insertion codes).
# label numbering is gapless 1..N with no icodes - a different residue at the same number.
cif_parser = MMCIFParser(QUIET=True, auth_residues=True)   # keep auth for literature/UniProt cross-ref
structure = cif_parser.get_structure('protein', 'protein.cif')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Distance/RMSD subtly off on a disordered site | `get_atoms()` returned only the highest-occupancy altloc of a DisorderedAtom | Enumerate `disordered_get_list()`; pick one altloc consistently before geometry |
| Impossibly close contacts / inflated atom count | Both altlocs of one atom entered the same calculation | Select a single altloc per site; never mix conformers |
| KeyError on `chain[100]` for a residue that is clearly present | Residue has an insertion code, hetero flag, or altloc, so the bare-int path misses it | Index with the full tuple `chain[(' ', 100, ' ')]` or iterate and match `id[1]`/`id[2]` |
| Antibody CDR residues 100/100A/100B collapse to one | Keyed on `residue.id[1]` (resseq) and dropped `id[2]` (icode) | Key on the full `(hetflag, resseq, icode)` tuple |
| Structure sequence one residue shorter than expected after each loop | PPBuilder returns the observed sequence with missing-density gaps concatenated away | Use SEQRES (`pdb-seqres`) for length; map to UniProt by residue number or SIFTS, not string index |
| Selenomethionine protein reads full of X or has holes in the chain | MSE is a hetero (`H_MSE`) residue; strict `protein_letters_3to1` returns X or a blanket hetero strip deleted it | Use `protein_letters_3to1_extended` (MSE->M); filter hetero by explicit allow/deny list |
| Water strip leaves waters behind | Filtered with `startswith('H_')`; water hetflag is `'W'` | Strip water with `r.id[0] == 'W'` |
| Stripping hetero removed a catalytic metal or cofactor | Blanket `r.id[0] != ' '` deletes metals, heme, FAD, ions, and mid-chain MSE | Remove only water/buffer by explicit list; keep ligands and metals |
| NMR metric multiplied ~20x or averaged to nonsense | Iterated all models, or averaged coordinates across the ensemble | Select one representative model, or compute per-model and report the spread |
| mmCIF residue numbers do not match the paper | Read label numbering instead of auth (or mixed a label index into an auth structure) | Set `auth_residues=True` (default) and stay in one scheme |
| Missing loop treated as a covalent chain break | Gap in coordinates is unmodeled disorder, not a real break | Reconcile against `header['missing_residues']`/SEQRES; flag gaps as disorder |
| Silent atom drops / merged chains on a messy file | `PDBParser(QUIET=True)` suppressed the discontinuous-chain warnings | For unfamiliar files parse without QUIET (or capture warnings) first |

## Related Skills

- structure-io - Parse and write PDB/mmCIF; auth vs label numbering at the I/O layer
- geometric-analysis - Distances, angles, RMSD, SASA once heterogeneity is resolved
- structure-modification - Strip waters/hetero, edit coordinates and B-factors safely
- interface-analysis - Requires the biological assembly, not the deposited asymmetric unit
- sequence-manipulation/seq-objects - Work with the extracted Seq objects
- alignment/msa-parsing - Map SEQRES/ATOM sequences onto alignment columns
- database-access/uniprot-access - Fetch the canonical sequence for SIFTS-based mapping

## References

- Hamelryck T, Manderick B (2003). PDB file parser and structure class implemented in Python. *Bioinformatics* 19(17):2308-2310. DOI 10.1093/bioinformatics/btg332.
- Cock PJA, Antao T, Chang JT, et al. (2009). Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics* 25(11):1422-1423. DOI 10.1093/bioinformatics/btp163.
- Berman HM, Westbrook J, Feng Z, et al. (2000). The Protein Data Bank. *Nucleic Acids Research* 28(1):235-242. DOI 10.1093/nar/28.1.235.
- Velankar S, Dana JM, Jacobsen J, et al. (2013). SIFTS: Structure Integration with Function, Taxonomy and Sequences resource. *Nucleic Acids Research* 41(D1):D483-D489. DOI 10.1093/nar/gks1258.
<!-- END FILE: structural-biology/structure-navigation/SKILL.md -->

## 子目录：structural-biology/structure-preparation

<!-- BEGIN FILE: structural-biology/structure-preparation/SKILL.md -->
---
name: bio-structural-biology-structure-preparation
description: Prepares a deposited or predicted structure for docking, molecular dynamics, or electrostatics by adding hydrogens, assigning protonation and tautomer states, and filling missing atoms and short loops with PDBFixer, reduce, PROPKA, and PDB2PQR. Use when adding hydrogens an X-ray model never resolved; assigning His HID/HIE/HIP tautomers, Asn/Gln/His 180-degree flips, and Cys/Lys/Asp/Glu pKa-shifted protonation at a stated pH and microenvironment rather than trusting standard pKa 7; filling missing side-chain atoms and modeling short missing loops as disorder hypotheses; making a receptor docking- or MD-ready and recording what was built; preparing a predicted model after trimming low-pLDDT regions; and writing a PQR for Poisson-Boltzmann electrostatics. Keywords PDBFixer, reduce, PROPKA, PDB2PQR, protonation, tautomer, missing atoms, hydrogens, pKa, docking prep, MD prep.
tool_type: python
primary_tool: PDBFixer
---

## Version Compatibility

Reference examples tested with: pdbfixer 1.9+, openmm 8.1+

reduce/Reduce2, propka3, and pdb2pqr30 are external command-line tools installed separately (`conda install -c conda-forge reduce propka pdb2pqr` or their own pip/binary packages); the code calls them via subprocess.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure Preparation

**"Make this receptor simulation-ready - add hydrogens and fix the protonation"** -> add the atoms the experiment never resolved, assign pH- and environment-dependent protonation/tautomer states, and fill modeled-absent atoms and short loops.
- Python: `pdbfixer.PDBFixer` for missing atoms/residues + hydrogens at a stated pH; `openmm.app.Modeller.addHydrogens` for force-field-ready H with explicit variants
- CLI: `reduce`/`mmtbx.reduce2` for H-bond-network flip and His tautomer optimization; `propka3` for pKa prediction; `pdb2pqr30 --with-ph --ff=AMBER --titration-state-method propka` for pKa + PQR

## Governing Principle

A deposited or predicted structure is NOT simulation-ready, and "preparing" it stacks a second layer of inference on top of a model that was already inferred from data. Every atom added, every proton placed, and every loop built is a hypothesis, not a measurement - so the prepared file is a distinct object from the deposited one, and the assumptions (pH, protonation model, what was built) must travel with it or downstream H-bond, salt-bridge, interface, and docking results become unreproducible.

Hydrogens are the first trap. X-ray crystallography rarely resolves them: a hydrogen carries ~1 electron and only becomes visible in density at roughly sub-1.2 Angstrom resolution, so almost every crystal structure arrives with zero (or only polar) hydrogens. They must be ADDED, and where a hydrogen goes is decided by the PROTONATION and TAUTOMER state of its residue, which crystallographic density alone frequently cannot distinguish. His has three relevant states (HID/HIE/HIP: proton on ND1, on NE2, or both/charged); Asn, Gln, and His side-chain amide/ring groups each have a 180-degree FLIP that swaps look-alike atoms (O for N, N for C) that density at typical resolution cannot tell apart (Word et al. 1999 *J Mol Biol* 285:1735). Placing a proton "at standard pKa 7" is wrong for any residue whose microenvironment shifts its pKa: a buried Asp/Glu can stay protonated well above pH 7, a Cys in a catalytic or metal site can be a deprotonated thiolate, a Lys buried near acidic residues can lose its charge. Use a pKa predictor (PROPKA, H++) for titratable residues and an all-atom H-bond-network optimizer (reduce) for flips and His tautomers - never trust the standard state for anything not freely solvated.

Missing atoms and short missing LOOPS are the second trap. A residue truncated to Cbeta, or a chain that jumps 45 -> 58, almost always means the region was DISORDERED (too mobile to model into density), not deleted - the atoms exist in reality (see structure-navigation, structure-validation). Building them back is legitimate for making a system topologically complete, but a built side chain or loop is a GUESS among many possible conformations, must be flagged as such, and must never be reported as experimental. Long gaps, terminal extensions, and anything spanning a domain are beyond what a preparation tool should invent - hand those to a modeling method, not PDBFixer.

## Decision: tool by preparation task

| Task | Tool | Best when | Fails / misleads when |
|---|---|---|---|
| Fill missing heavy atoms, short internal loops, terminals | PDBFixer (`findMissingResidues`/`findMissingAtoms`/`addMissingAtoms`) | Truncated side chains, 1-few-residue gaps flanked by modeled residues | Long/terminal gaps, domain-scale missing regions - it builds implausible geometry |
| Add hydrogens at a pH, replace nonstandard residues (MSE, PTR) | PDBFixer `addMissingHydrogens(pH)` / `replaceNonstandardResidues` | Fast, one-call prep; standard residues in bulk-like environments | Ignores microenvironment pKa shifts and does not optimize flips/tautomers |
| Optimize Asn/Gln/His flips and His tautomer/protonation | reduce / Reduce2 (`-build` / `-FLIP`) | Resolving amide/ring orientation ambiguity by all-atom H-bond network | Treated as a pKa predictor - it optimizes geometry, not titration equilibria |
| Predict residue pKa / pH-dependent protonation | PROPKA (`propka3`), H++ | Deciding which titratable residues deviate from standard states | Reported as exact experimental pKa; empirical model, not measurement |
| Assign states + write PQR (charges/radii) for electrostatics | PDB2PQR (`pdb2pqr30 --with-ph --ff --titration-state-method propka`) | Setting up APBS/Poisson-Boltzmann; consistent charge+radius assignment | Used as a general H-adder for MD without matching the target force field |
| Add force-field-consistent H with explicit protonation variants | OpenMM `Modeller.addHydrogens(forcefield, pH, variants)` | Building an MD-ready system in a specific force field | Variants left default when a residue needs a non-standard state |
| Full MD system (solvate, neutralize, box) | OpenMM / MD prep (pointer) | After protonation is settled | Run before protonation/flips are correct - re-solvating is expensive |

## Decision: standard protonation state vs pKa predictor

| Residue / situation | Standard state at pH 7 usually fine | Use a pKa predictor + H-bond optimizer |
|---|---|---|
| Surface Asp/Glu, freely solvated | Deprotonated (-1) | Only if near a metal or H-bond partner |
| Buried or salt-bridged Asp/Glu | -- | pKa can rise several units -> may be neutral/protonated |
| Lys/Arg on the surface | Protonated (+1) | Buried Lys near acidic residues can be neutral |
| His anywhere | Ambiguous by default | Almost always: pick HID vs HIE vs HIP by local H-bonds and metal coordination |
| Cys, free | Neutral thiol | Catalytic/metal-coordinating Cys is often thiolate |
| Cys in a disulfide | No H on S (CYX) | Detect the SS bond first; do not protonate |
| Any active-site or interface residue | -- | Microenvironment dominates - predict, do not assume |

The one-line rule: standard states are defensible only for residues in a bulk-solvent-like environment; any titratable residue that is buried, charged-clustered, metal-adjacent, or in a pocket needs a predictor (PROPKA/H++) and an H-bond-network pass (reduce), with the chosen pH stated.

## PDBFixer preparation pipeline

**Goal:** Turn a raw PDB/mmCIF into a hydrogen-complete, gap-filled structure at a chosen pH, recording what was added.

**Approach:** Call the PDBFixer finders in their required order (missing residues, then nonstandard, then missing atoms) so `addMissingAtoms` sees both sets; strip crystallization heterogens while keeping (or dropping) water deliberately; then add hydrogens at an explicitly chosen pH. The order matters - hydrogens are added last, after heavy atoms exist.

```python
from pdbfixer import PDBFixer
from openmm.app import PDBFile

fixer = PDBFixer(filename='receptor.pdb')  # or PDBFixer(pdbid='1VII') to fetch from RCSB

fixer.findMissingResidues()          # short internal gaps + terminals, from SEQRES vs modeled
fixer.findNonstandardResidues()      # e.g. MSE (selenomethionine), modified residues
fixer.replaceNonstandardResidues()   # map them back to standard parents
fixer.removeHeterogens(keepWater=False)  # drop buffer ions/cryoprotectants; keepWater=True to retain
fixer.findMissingAtoms()             # truncated side chains + the residues found above
fixer.addMissingAtoms()              # build heavy atoms; built loops are HYPOTHESES, log them

# pH 7.0 is a CHOICE, not a safe default - state it and match the experimental/biological condition.
# addMissingHydrogens detects existing disulfides and leaves those Cys as CYX (no SG hydrogen).
fixer.addMissingHydrogens(pH=7.0)

with open('receptor_prepared.pdb', 'w') as out:
    PDBFile.writeFile(fixer.topology, fixer.positions, out, keepIds=True)

# missingResidues is a dict {(chain_index, residue_index): [resname, ...]} - flatten it for provenance.
built = [(ci, pos, name) for (ci, pos), names in fixer.missingResidues.items() for name in names]
print(f'built {len(fixer.missingResidues)} missing-residue segment(s), {len(built)} residue(s); pH=7.0')
```

## Optimize flips and His tautomers with reduce

**Goal:** Resolve Asn/Gln/His amide and ring orientations and His protonation by all-atom H-bond-network scoring, which density at typical resolution cannot settle.

**Approach:** Run reduce with building enabled so it adds hydrogens AND evaluates the 180-degree flip of each Asn/Gln/His plus His NH placement, choosing the orientation that optimizes the local hydrogen-bond network and minimizes clashes. reduce optimizes GEOMETRY, not titration - pair it with a pKa predictor for charge states.

```python
import subprocess

# -build runs -OH -ROTEXOH -HIS -FLIP: adds H and optimizes OH/His rotation plus Asn/Gln/His flips
# (a superset of -FLIP, not an alias). reduce scores orientation by small-probe all-atom contacts (Word 1999).
with open('receptor_reduced.pdb', 'w') as out:
    subprocess.run(['reduce', '-build', 'receptor_prepared.pdb'], stdout=out, check=True)

# Reduce2 (CCTBX/Phenix) is the maintained successor: mmtbx.reduce2 receptor_prepared.pdb
```

## Predict pKa and write a PQR for electrostatics

**Goal:** Decide which titratable residues deviate from standard states at a target pH, and emit charges+radii for Poisson-Boltzmann electrostatics.

**Approach:** PROPKA predicts per-residue pKa from the 3D environment; PDB2PQR wraps PROPKA to assign protonation at `--with-ph`, add hydrogens for the chosen force field, and write a PQR. Feed the PQR to APBS for the electrostatic potential (a separate downstream step; see the electrostatics note below).

```python
import subprocess

# propka3 writes receptor_prepared.pka; the SUMMARY lists predicted pKa vs model (standard) pKa.
subprocess.run(['propka3', 'receptor_prepared.pdb'], check=True)

# PDB2PQR assigns states at pH via PROPKA and writes charges/radii for the named force field.
# --ff must MATCH the downstream force field; --with-ph 7.0 is the stated titration condition.
subprocess.run([
    'pdb2pqr30', '--ff=AMBER', '--with-ph', '7.0',
    '--titration-state-method', 'propka', '--keep-chain',
    'receptor_prepared.pdb', 'receptor.pqr',
], check=True)
```

Electrostatics note: the PQR is the input to APBS (Jurrus et al. 2018 *Protein Sci* 27:112) for the Poisson-Boltzmann potential/surface; PDB2PQR can emit an APBS input file. Keep force field, pH, and radii set identical between preparation and the APBS run.

## Force-field-ready hydrogens with OpenMM Modeller

**Goal:** Add hydrogens consistent with a specific MD force field, forcing non-standard protonation where the environment demands it.

**Approach:** `Modeller.addHydrogens` picks the most common state per residue at the given pH and detects disulfides for Cys, but it does NOT know microenvironment pKa shifts - override with an explicit `variants` list (ASH/GLH for protonated acids, LYN for neutral Lys, HID/HIE/HIP for His) derived from a PROPKA/reduce pass. Solvation and box setup follow, at a pointer level.

```python
from openmm.app import PDBFile, Modeller, ForceField

pdb = PDBFile('receptor_prepared.pdb')
forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
modeller = Modeller(pdb.topology, pdb.positions)

# variants: None per residue = let OpenMM pick at pH; override where PROPKA/reduce said otherwise.
# Set the entry for a given His to 'HID'/'HIE'/'HIP', an acid to 'ASH'/'GLH', a buried Lys to 'LYN'.
variants = modeller.addHydrogens(forcefield, pH=7.0)  # returns the chosen variant per residue

# Downstream (pointer, not this skill): modeller.addSolvent(forcefield, model='tip3p', padding=1.0*nanometer)
with open('receptor_ff_ready.pdb', 'w') as out:
    PDBFile.writeFile(modeller.topology, modeller.positions, out)
```

## Preparing a predicted (AlphaFold/ESMFold) model

**Goal:** Make a predicted model docking/MD-ready without carrying its low-confidence regions into the physics.

**Approach:** A predicted model has NO experimental hydrogens and its low-pLDDT stretches are unreliable guesses (often intrinsically disordered), so TRIM low-confidence regions FIRST, then add hydrogens/protonation. pLDDT rides in the B-factor column (opposite polarity to a real B-factor); use it to cut, not to color as mobility (see alphafold-predictions). Pocket rotamers are the least reliable atoms even where backbone pLDDT is high, so verify the binding site before docking.

```python
from pdbfixer import PDBFixer
from openmm.app import PDBFile

# 1) Trim low-pLDDT residues (pLDDT<50-70 = unreliable) BEFORE preparation; phenix.process_predicted_model
#    does this + a PAE domain split for MR. Here: a minimal B-factor(=pLDDT) filter as illustration.
# 2) Then run the PDBFixer pipeline above on the trimmed model to add H and any missing side-chain atoms.
fixer = PDBFixer(filename='af_model_trimmed.pdb')
fixer.findMissingAtoms()
fixer.addMissingAtoms()
fixer.addMissingHydrogens(pH=7.0)  # predicted models never carry experimental hydrogens
with open('af_model_prepared.pdb', 'w') as out:
    PDBFile.writeFile(fixer.topology, fixer.positions, out, keepIds=True)
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Prepared file has no hydrogens | X-ray models rarely resolve H; parsing does not add them | Run `addMissingHydrogens(pH=...)` or `Modeller.addHydrogens` explicitly |
| His H-bonds/metal coordination look wrong | Default HIE/HID guessed without the local network; wrong tautomer | Let reduce pick the neutral tautomer (HID vs HIE) by H-bond network; use PROPKA only to decide the CHARGE state (HIP vs neutral) - they answer different questions, so reconcile rather than pick one |
| Buried Asp/Glu deprotonated but should be neutral | Standard pKa 7 assumed; buried pKa is shifted up | Predict pKa (PROPKA/H++); protonate the residue (ASH/GLH) |
| Catalytic Cys modeled as neutral thiol | Standard state assumed in a metal/active site | Predict pKa / check metal coordination; set thiolate or CYX for disulfides |
| Asn/Gln side chain H-bonds backwards | 180-degree amide flip not resolved (O/N indistinguishable in density) | Run reduce with flips enabled before analysis |
| `addMissingAtoms` builds a wild loop | A long/terminal gap handed to a gap-filler that only does short loops | Do not build long gaps here; use a loop/homology modeler and flag it |
| Catalytic metal or cofactor gone after prep | `removeHeterogens()` stripped all non-water heterogens | Keep needed heterogens: filter deliberately, do not blanket-remove |
| Missing residues not built | `findMissingAtoms` called before `findMissingResidues` | Call finders in order: residues, nonstandard, then atoms |
| pKa/protonation differs from a paper | Different pH or predictor; states are pH- and method-dependent | State the pH and tool; treat predicted pKa as a model, not a measurement |
| Predicted pKa sits close to the working pH | The protonation state is genuinely ambiguous, and empirical predictors are weakest at metal and strongly-coupled active sites | Test both states (or run constant-pH MD); at metal/catalytic sites treat the predicted pKa as a weak prior and cross-check coordination geometry/literature |
| Downstream results not reproducible | Prepared file shipped without its assumptions | Record pH, protonation model, and every built atom/loop as provenance |
| APBS charges look wrong | PDB2PQR `--ff` did not match the downstream force field/radii | Match `--ff` and radii set across preparation and APBS |
| Predicted model docks into a garbage pocket | Low-pLDDT/rotamer-unreliable region kept, or wrong apo/holo state | Trim by pLDDT first; verify the pocket conformation before docking |

## Related Skills

- structure-validation - check resolution, altlocs, and the region of interest before adding inference on top
- structure-navigation - identify missing residues, disorder, altlocs, and the (hetflag, resseq, icode) id tuple
- structure-modification - strip solvent by HETFLAG and resolve altlocs before preparation; never overwrite pLDDT-in-B
- interface-analysis - add hydrogens here first so H-bond and salt-bridge geometry across an interface is meaningful
- alphafold-predictions - read pLDDT/PAE and trim low-confidence regions before preparing a predicted model
- structure-io - download the biological assembly and convert PDB/mmCIF before preparation
- chemoinformatics/virtual-screening - dock into the prepared, protonated receptor

## References

- Eastman P, Swails J, Chodera JD, et al. 2017. OpenMM 7: rapid development of high performance algorithms for molecular dynamics. *PLoS Comput Biol* 13(7):e1005659. doi:10.1371/journal.pcbi.1005659 (PDBFixer ships with OpenMM)
- Word JM, Lovell SC, Richardson JS, Richardson DC. 1999. Asparagine and glutamine: using hydrogen atom contacts in the choice of side-chain amide orientation. *J Mol Biol* 285(4):1735-1747. doi:10.1006/jmbi.1998.2401 (reduce Asn/Gln/His flips)
- Olsson MHM, Sondergaard CR, Rostkowski M, Jensen JH. 2011. PROPKA3: consistent treatment of internal and surface residues in empirical pKa predictions. *J Chem Theory Comput* 7(2):525-537. doi:10.1021/ct100578z
- Sondergaard CR, Olsson MHM, Rostkowski M, Jensen JH. 2011. Improved treatment of ligands and coupling effects in empirical calculation and rationalization of pKa values. *J Chem Theory Comput* 7(7):2284-2295. doi:10.1021/ct200133y
- Dolinsky TJ, Nielsen JE, McCammon JA, Baker NA. 2004. PDB2PQR: an automated pipeline for the setup of Poisson-Boltzmann electrostatics calculations. *Nucleic Acids Res* 32:W665-W667. doi:10.1093/nar/gkh381
- Jurrus E, Engel D, Star K, et al. 2018. Improvements to the APBS biomolecular solvation software suite. *Protein Sci* 27(1):112-128. doi:10.1002/pro.3280
- Anandakrishnan R, Aguilar B, Onufriev AV. 2012. H++ 3.0: automating pK prediction and the preparation of biomolecular structures for atomistic molecular modeling and simulations. *Nucleic Acids Res* 40:W537-W541. doi:10.1093/nar/gks375
<!-- END FILE: structural-biology/structure-preparation/SKILL.md -->

## 子目录：structural-biology/structure-validation

<!-- BEGIN FILE: structural-biology/structure-validation/SKILL.md -->
---
name: bio-structural-biology-structure-validation
description: Judges whether a macromolecular model (or a region of it) is reliable enough to build on, using resolution, R-free, B-factors, MolProbity geometry, and predicted-model confidence with Bio.PDB. Use when deciding if a structure or a specific region is trustworthy before docking/mechanism/measurement; reading resolution, R-work vs R-free and the R-free-minus-R-work overfitting gap; sanity-checking per-residue and mean B-factors; flagging clashscore, Ramachandran and rotamer outliers and cis non-proline peptides; validating a PREDICTED (AlphaFold/ESMFold) model via pLDDT bands and PAE before docking or molecular replacement; and interpreting cryo-EM global-vs-local resolution (FSC 0.143 half-map vs 0.5 map-model) or an NMR ensemble spread. Keywords validation, resolution, R-free, B-factor, MolProbity, clashscore, Ramachandran, rotamer, pLDDT, PAE, wwPDB, cryo-EM local resolution.
tool_type: python
primary_tool: Bio.PDB
---

## Version Compatibility

Reference examples tested with: biopython 1.85+, numpy 1.26+

MolProbity, phenix (`phenix.molprobity`, `phenix.process_predicted_model`), and DSSP (`mkdssp`) are external CLI tools invoked via `subprocess`, not pip packages; install them separately and confirm they are on PATH before use.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure Validation

**"Is this structure good enough to build on?"** -> Read the data-quality metadata, run geometry validation, and decide per-region rather than per-file.
- Python: `Bio.PDB.MMCIF2Dict` (resolution/R-free), `Bio.PDB.calc_dihedral` (phi/psi/omega), `subprocess` -> `phenix.molprobity` (clashscore, rotamer, Ramachandran).

## Governing Principle

A coordinate file is an INTERPRETED MODEL fit to experimental data, not the data and not ground truth, and its reliability varies PER-ATOM within one file. The single global resolution is a DATA CEILING on what the map can resolve, never a per-region quality certificate: a 1.5 Angstrom structure can still carry a guesswork surface loop, and a 3.2 Angstrom structure can have a rigid, locally excellent active site. The number that answers "can I trust THIS region" is the LOCAL signal - the per-residue B-factor and the real-space fit (RSRZ) for the residues actually used - not the headline resolution. Validate before any geometric interpretation: clashscore, Ramachandran and rotamer outliers, cis-peptides, and bond/angle deviations tell whether the model is even self-consistent before a distance or an angle computed on it means anything.

R-free, not R-work, is the cross-validation statistic. R-work is computed on the reflections used in refinement and can be driven down by adding parameters (waters, alt-confs, loose restraints) that fit noise; R-free is the same metric on a held-out test set that never entered refinement (Brunger 1992 *Nature* 355:472-475). The R-free-MINUS-R-work GAP is the overfitting flag - a gap much larger than expected for the resolution signals a model fitting its own noise, and a suspiciously small gap signals test-set leakage (Kleywegt & Brunger 1996 *Structure* 4:897-904). B-factors conflate genuine thermal motion, static disorder, and MODEL ERROR into one number, so they are a within-structure relative signal ("which atoms are least certain here"), NOT a portable cross-structure dynamics readout; normalize before comparing across structures and exclude high-B atoms (say >60-80 Angstrom^2 at moderate resolution) from precise geometric claims.

For a PREDICTED model the confidence scores bound SELF-CONSISTENCY, NOT correctness. pLDDT is per-residue and PAE is inter-residue confidence in the model's OWN frame (Jumper et al. 2021 *Nature* 596:583-589); a confident model can be confidently wrong when AlphaFold modeled a monomer/apo state where the truth is a complex/holo/alternative state. Trim low-pLDDT residues and split by PAE-defined domains before docking or molecular replacement (Oeffner et al. 2022 *Acta Crystallogr D* 78:1303-1314). Cryo-EM has GLOBAL vs LOCAL resolution - flexible peripheries in a big map are often docked hypotheses at 6-8 Angstrom local resolution inside a "2.5 Angstrom" map - and TWO different FSC thresholds: 0.143 on the gold-standard half-map FSC for the resolution claim, 0.5 for map-vs-model agreement (Rosenthal & Henderson 2003 *J Mol Biol* 333:721-745). An NMR deposit is an ENSEMBLE of models; validate per-model and report the per-residue spread - never average coordinates, which produces a physically impossible structure with distorted bonds and clashes (Montelione et al. 2013 *Structure* 21:1563-1570).

## Decision: what the resolution buys (X-ray / cryo-EM global)

| Resolution (A) | Reliably resolvable | Do NOT over-read |
|---|---|---|
| < 1.2 (atomic) | Individual atoms, H atoms, anisotropic ADPs, alt-confs | - |
| 1.2-1.8 | Side-chain rotamers, ordered waters, alt-confs | Surface/loop atoms with high B still uncertain |
| 1.8-2.5 (typical) | Backbone plus most side chains; fold solid | Long polar rotamers, water networks, weak ligand density are model-dependent |
| 2.5-3.5 | Backbone trace, secondary structure, domain arrangement | Side-chain conformations, exact ligand pose, H-bond geometry are interpretive |
| > 3.5 | Overall fold, gross assembly | Individual side chains largely placed by geometry; treat atomic detail as hypothesis |

## Decision: R-free and the overfitting gap

| Resolution | Typical R-work | Typical R-free | Concern if gap (R-free - R-work) exceeds ~ |
|---|---|---|---|
| ~1.5 A | 0.13-0.17 | 0.15-0.19 | 0.03-0.04 |
| ~2.0 A | 0.16-0.20 | 0.19-0.24 | 0.04-0.05 |
| ~2.5-3.0 A | 0.18-0.24 | 0.23-0.29 | 0.05-0.06 |

Absolute R rises with resolution (weaker high-angle reflections are noisier); a gap wider than the row's threshold flags overfitting, a near-zero gap flags work/test contamination. These are heuristics - verify against contemporaneous PDB statistics for the resolution.

## Decision: geometry validation targets (MolProbity)

| Metric | Measures | Target (goal) | Concern | Source |
|---|---|---|---|---|
| Clashscore | Serious all-atom overlaps (>0.4 A) per 1000 atoms | low, high same-resolution percentile | high vs same-resolution peers | Chen 2010 |
| Ramachandran favored | % residues in favored phi/psi basins | > 98% | < 95% | Williams 2018 |
| Ramachandran outliers | % residues in disallowed phi/psi | < 0.2% (goal 0) | > 0.5% | Williams 2018 |
| Poor rotamers | % side chains in disallowed rotamers | < 0.3% | > 1.5% | Williams 2018 |
| RSRZ outliers (X-ray) | Residues poorly fitting local density (RSRZ > 2) | few, dispersed | many, or clustered in the region of interest | Gore 2017 |
| MolProbity score | Composite mapped to a resolution-equivalent | <= deposited resolution | >> deposited resolution | Chen 2010 |

The poor-rotamer target tightened from ~1.0% to 0.3% with the updated reference distributions (Williams 2018). Read the wwPDB report's PERCENTILE sliders alongside the raw numbers: they rank an entry against the whole archive AND against same-resolution entries (Gore et al. 2017 *Structure* 25:1916-1927).

## Decision: how to validate this model (experimental vs predicted fork)

| The model is | Trust question | What to read | Authoritative route |
|---|---|---|---|
| X-ray | Is the region well-determined? | resolution + local B + RSRZ; R-free and its gap | wwPDB report + `phenix.molprobity` |
| Cryo-EM | Is the region rigid or a docked guess? | LOCAL resolution map, not global; map-model FSC (0.5) | EMDB local-resolution + map-model FSC |
| NMR | How wide is the conformational spread? | per-residue RMSD across all models | validate each model; report spread |
| Predicted (AlphaFold/ESMFold) | Is it self-consistent AND in the right biological context? | pLDDT bands + PAE blocks; is it apo/monomer where truth is holo/complex? | `phenix.process_predicted_model` (trim + PAE split) |

## Read Validation Metadata From the mmCIF Header

**Goal:** Pull resolution, R-work, R-free, and method from a deposited entry and flag the overfitting gap - the numbers Bio.PDB's thin `structure.header` omits.

**Approach:** Read the raw mmCIF categories with `MMCIF2Dict` (which reaches anything in the file), cast the strings, and compare the R-free-minus-R-work gap against a resolution-scaled expectation.

```python
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

def read_refinement_metadata(cif_path):
    meta = MMCIF2Dict(cif_path)
    def first(key):
        val = meta.get(key, ['NA'])[0]
        try:
            return float(val)
        except ValueError:
            return val
    method = meta.get('_exptl.method', ['NA'])[0]
    resolution = first('_refine.ls_d_res_high')
    r_work = first('_refine.ls_R_factor_R_work')
    r_free = first('_refine.ls_R_factor_R_free')
    gap = r_free - r_work if isinstance(r_free, float) and isinstance(r_work, float) else None
    # A gap wider than ~0.05 flags overfitting at typical (~2 A) resolution (Kleywegt & Brunger 1996).
    overfit_flag = gap is not None and gap > 0.05
    return {'method': method, 'resolution': resolution, 'r_work': r_work, 'r_free': r_free, 'gap': gap, 'overfit_flag': overfit_flag}
```

## Sanity-Check B-factors Within One Structure

**Goal:** Locate the least-certain atoms of THIS model so precise-distance claims avoid them - a relative, within-structure read, never a cross-structure comparison.

**Approach:** Collect per-residue mean B for a chain, then flag residues whose B sits far above the structure's own median as low-confidence.

```python
import numpy as np
from Bio.PDB import PDBParser

def bfactor_outliers(structure, chain_id, z_cut=2.0):
    residue_b = {}
    for residue in structure[0][chain_id]:
        if residue.id[0] != ' ':  # skip hetero/water; validate the polymer only
            continue
        residue_b[residue.id] = np.mean([a.get_bfactor() for a in residue])
    vals = np.array(list(residue_b.values()))
    median, mad = np.median(vals), np.median(np.abs(vals - np.median(vals))) + 1e-9
    # Robust z on B: |B - median| / (1.4826*MAD); high B marks disorder/model error, not portable dynamics.
    return {rid: b for rid, b in residue_b.items() if (b - median) / (1.4826 * mad) > z_cut}
```

## Flag Ramachandran Outliers and cis Non-Proline Peptides

**Goal:** Catch backbone geometry that is almost always a modeling error - residues in disallowed phi/psi and cis peptide bonds that are not proline.

**Approach:** Get per-residue phi/psi from `PPBuilder`, coarsely classify against the canonical basins, and compute omega (Ca-C-N-Ca) directly to find cis bonds; a cis assignment at a non-proline is a validation flag until proven by density.

```python
import numpy as np
from Bio.PDB import PDBParser, PPBuilder, calc_dihedral

# Coarse general-allowed basins (deg): alpha, beta/PPII, left-handed. Authoritative
# favored/allowed/outlier percentages need MolProbity's rama8000 contours (Williams 2018);
# this only screens gross outliers to decide whether to run MolProbity.
_BASINS = [(-160, -40, -80, 30), (-180, -40, 90, 180), (30, 90, -30, 90)]

def is_rama_allowed(phi, psi):
    d = np.degrees([phi, psi])
    return any(lo_p <= d[0] <= hi_p and lo_s <= d[1] <= hi_s for lo_p, hi_p, lo_s, hi_s in _BASINS)

def geometry_flags(structure):
    outliers, cis_nonpro = [], []
    ppb = PPBuilder()
    for pp in ppb.build_peptides(structure[0]):
        for residue, (phi, psi) in zip(pp, pp.get_phi_psi_list()):
            if phi is not None and psi is not None and not is_rama_allowed(phi, psi):
                outliers.append((residue.get_parent().id, residue.id[1], residue.resname))
        residues = list(pp)
        for prev, curr in zip(residues, residues[1:]):
            omega = calc_dihedral(prev['CA'].get_vector(), prev['C'].get_vector(), curr['N'].get_vector(), curr['CA'].get_vector())
            # omega ~180 = trans, ~0 = cis; |omega| < 30 deg is cis. cis at non-Pro is rare and usually an error.
            if abs(np.degrees(omega)) < 30 and curr.resname != 'PRO':
                cis_nonpro.append((curr.get_parent().id, curr.id[1], curr.resname))
    return {'rama_outliers': outliers, 'cis_nonproline': cis_nonpro}
```

## Run MolProbity for Authoritative Geometry (the real answer)

**Goal:** Get archive-calibrated clashscore, rotamer, and Ramachandran outlier percentages rather than the coarse Python screen above.

**Approach:** Shell out to `phenix.molprobity` (or the MolProbity web service / `molprobity.molprobity`), which carries the reference contour and rotamer distributions the Python screen cannot reproduce.

```python
import subprocess

def run_molprobity(model_path):
    # phenix.molprobity writes molprobity.out with clashscore, rotamer_outliers,
    # ramachandran_outliers, ramachandran_favored, molprobity_score. Parse that file.
    result = subprocess.run(['phenix.molprobity', model_path], capture_output=True, text=True)
    return result.stdout
```

The coarse Python screen decides WHETHER to run MolProbity; MolProbity (Chen et al. 2010 *Acta Crystallogr D* 66:12-21; Williams et al. 2018 *Protein Sci* 27:293-315) gives the numbers to report. For a deposited entry, prefer the pre-computed wwPDB validation report (`https://files.rcsb.org/pub/pdb/validation_reports/<xy>/<id>/<id>_validation.xml.gz`) - it already carries the percentile sliders and per-residue RSRZ.

## Validate a Predicted Model Before Docking or MR

**Goal:** Turn an AlphaFold/ESMFold model into a trustworthy input by trimming low-confidence residues and reading inter-domain confidence - because pLDDT/PAE bound self-consistency, not correctness.

**Approach:** Read pLDDT from the B-factor column into bands, read the PAE matrix for domain segmentation, then hand the raw file to `phenix.process_predicted_model` (which converts pLDDT to a pseudo-B, trims, and splits by PAE-defined domains).

```python
import json
import numpy as np
import subprocess
from Bio.PDB import MMCIFParser

_PLDDT_BANDS = [(90, 'very_high'), (70, 'confident'), (50, 'low'), (0, 'very_low')]

def plddt_bands(cif_path):
    # pLDDT rides in the B-factor column but is confidence (high = good), OPPOSITE polarity to a real B-factor.
    structure = MMCIFParser(QUIET=True).get_structure('pred', cif_path)
    counts = {label: 0 for _, label in _PLDDT_BANDS}
    for residue in structure[0].get_residues():
        if 'CA' not in residue:
            continue
        score = residue['CA'].get_bfactor()
        counts[next(label for cut, label in _PLDDT_BANDS if score >= cut)] += 1
    return counts  # a long very_low run usually flags an intrinsically disordered region, not an error

def pae_interdomain_confident(pae_json, block_a, block_b, cutoff=5.0):
    # Off-diagonal PAE (A) between two domain blocks; low = relative orientation trusted, high = independent guess.
    pae = np.array(json.load(open(pae_json))[0]['predicted_aligned_error'])
    return pae[np.ix_(block_a, block_b)].mean() < cutoff

def process_for_mr(model_path):
    # Trims below ~0.7 fractional pLDDT, converts pLDDT->pseudo-B, splits into PAE-defined domains (Oeffner 2022).
    return subprocess.run(['phenix.process_predicted_model', model_path], capture_output=True, text=True).stdout
```

## Report an NMR Ensemble Spread (never average coordinates)

**Goal:** Turn a multi-model NMR deposit into a per-residue uncertainty map instead of over-claiming precision from model 1.

**Approach:** Superpose all models on a reference and report per-residue Ca RMSD across the ensemble; wide spread marks flexible or under-restrained regions.

```python
import numpy as np
from Bio.PDB import PDBParser

def ensemble_ca_spread(structure, chain_id):
    coords = []
    for model in structure:
        coords.append(np.array([res['CA'].get_coord() for res in model[chain_id] if 'CA' in res]))
    stack = np.stack(coords)  # (n_models, n_residues, 3); assumes consistent residue set across models
    # Per-residue spread = mean distance of each model's Ca from the ensemble mean position.
    return np.linalg.norm(stack - stack.mean(axis=0), axis=2).mean(axis=0)
```

Secondary-structure validation (DSSP, `Bio.PDB.DSSP(model, path, dssp='mkdssp')`) needs backbone geometry to place the amide H and computes its own H-bond energy; it processes only the first model and its output drifts across the dssp->mkdssp v2->v4 rewrites, so name the version (Kabsch & Sander 1983 *Biopolymers* 22:2577-2637). See geometric-analysis for dihedral and DSSP mechanics.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| "It is a 1.5 A structure so every atom is accurate" | Global resolution read as per-region quality | Read the local B-factor and RSRZ for the specific residues used; resolution is a data ceiling |
| Low R-work reported as proof of a good model | R-work is fit on refinement reflections and rewards overfitting | Report R-free (held-out) and the R-free-minus-R-work gap; a wide gap flags overfitting |
| B-factors of two structures compared at face value | B conflates thermal motion, disorder, and model error and is not portable | Compare within one structure only; normalize (z/percentile) before any cross-structure claim |
| Coloring an AlphaFold model "by B-factor" to infer flexibility | pLDDT rides in the B-factor column with OPPOSITE polarity (high = confident) | Read the column as pLDDT bands; high value means high confidence, not high motion |
| Deleting all low-pLDDT residues as junk | Low pLDDT often marks a real intrinsically disordered region | Distinguish disorder (keep, annotate) from misfold; trim only for MR/geometry pipelines |
| Docking straight into an AlphaFold pocket | Pocket is apo, side-chain rotamers are the least reliable atoms, may be wrong state | Prefer an experimental holo structure; if using the model, ensemble/flexible-side-chain dock and treat hits as hypotheses |
| Confident predicted model trusted for a complex | pLDDT/PAE bound self-consistency, not biological correctness | Ask what context AF could not see (partner, ligand, PTM); a monomer/apo model can be confidently wrong |
| Cryo-EM peripheral domain trusted at the headline resolution | Global resolution hides a low-local-resolution flexible arm | Consult the EMDB local-resolution map; treat low-local-res regions as docked hypotheses |
| Quoting FSC 0.5 as the cryo-EM resolution | 0.143 is the half-map criterion; 0.5 is the map-vs-model curve | Use gold-standard half-map FSC at 0.143 for resolution; 0.5 for checking the model against the map |
| Averaging NMR model coordinates into one structure | The mean of two valid conformers is physically impossible (distorted bonds, clashes) | Compute on each model and report the spread, or pick a representative/medoid model |
| cis peptide flagged everywhere, or missed entirely | omega near 0 (cis) vs 180 (trans) not checked; cis-Pro is common but cis non-Pro is rare | Compute omega; treat cis non-proline as a validation flag pending density, cis-Pro as plausible |
| Python Ramachandran percentages reported as authoritative | Coarse basin boxes are not MolProbity's rama8000 contours | Use the screen to decide whether to run `phenix.molprobity`; report MolProbity's numbers |
| `resolution`/`R-free` come back `None` from `structure.header` | Bio.PDB's header dict is thin | Read `_refine.ls_d_res_high`, `_refine.ls_R_factor_R_free`, `_exptl.method` via `MMCIF2Dict` |

## Related Skills

- structure-io - Read resolution/R-free via MMCIF2Dict and fetch the biological assembly the validation applies to
- structure-navigation - Resolve altlocs, insertion codes, and multi-model NMR files before validating per-model
- geometric-analysis - Compute the dihedrals and DSSP secondary structure this skill validates; measure only after validation passes
- structure-modification - Trim low-pLDDT residues or edit B-factors once a predicted model is validated
- structure-preparation - Add hydrogens, protonation, and missing atoms after validation and before docking/MD
- alphafold-predictions - Download the AlphaFold model plus its PAE JSON that this skill reads for confidence
- modern-structure-prediction - Reconcile a re-run prediction with pLDDT/PAE/pTM when the AFDB entry is untrustworthy
- interface-analysis - Validate the assembly before interpreting an interface that only exists in it
- database-access/uniprot-access - Map validated residues back to a UniProt reference sequence

## References

- Ramachandran GN, Ramakrishnan C, Sasisekharan V (1963). Stereochemistry of polypeptide chain configurations. *J Mol Biol* 7:95-99. DOI 10.1016/S0022-2836(63)80023-6.
- Brunger AT (1992). Free R value: a novel statistical quantity for assessing the accuracy of crystal structures. *Nature* 355(6359):472-475. DOI 10.1038/355472a0.
- Kabsch W, Sander C (1983). Dictionary of protein secondary structure: pattern recognition of hydrogen-bonded and geometrical features. *Biopolymers* 22(12):2577-2637. DOI 10.1002/bip.360221211.
- Kleywegt GJ, Brunger AT (1996). Checking your imagination: applications of the free R value. *Structure* 4(8):897-904. DOI 10.1016/S0969-2126(96)00097-4.
- Rosenthal PB, Henderson R (2003). Optimal determination of particle orientation, absolute hand, and contrast loss in single-particle electron cryomicroscopy. *J Mol Biol* 333(4):721-745. DOI 10.1016/j.jmb.2003.07.013.
- Chen VB, Arendall WB III, Headd JJ, Keedy DA, Immormino RM, Kapral GJ, Murray LW, Richardson JS, Richardson DC (2010). MolProbity: all-atom structure validation for macromolecular crystallography. *Acta Crystallogr D* 66(1):12-21. DOI 10.1107/S0907444909042073.
- Read RJ, Adams PD, Arendall WB III, Brunger AT, Emsley P, Joosten RP, Kleywegt GJ, Krissinel EB, Luetteke T, Otwinowski Z, Perrakis A, Richardson JS, Sheffler WH, Smith JL, Tickle IJ, Vriend G, Zwart PH (2011). A new generation of crystallographic validation tools for the Protein Data Bank. *Structure* 19(10):1395-1412. DOI 10.1016/j.str.2011.08.006.
- Gore S, Sanz Garcia E, Hendrickx PMS, Gutmanas A, Westbrook JD, Yang H, Feng Z, Baskaran K, Berrisford JM, et al. (2017). Validation of structures in the Protein Data Bank. *Structure* 25(12):1916-1927. DOI 10.1016/j.str.2017.10.009.
- Williams CJ, Headd JJ, Moriarty NW, Prisant MG, Videau LL, Deis LN, Verma V, Keedy DA, Hintze BJ, Chen VB, Jain S, Lewis SM, Arendall WB III, Snoeyink J, Adams PD, Lovell SC, Richardson JS, Richardson DC (2018). MolProbity: more and better reference data for improved all-atom structure validation. *Protein Sci* 27(1):293-315. DOI 10.1002/pro.3330.
- Jumper J, Evans R, Pritzel A, et al. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature* 596(7873):583-589. DOI 10.1038/s41586-021-03819-2.
- Oeffner RD, Croll TI, Millan C, Poon BK, Schlicksup CJ, Read RJ, Terwilliger TC (2022). Putting AlphaFold models to work with phenix.process_predicted_model and ISOLDE. *Acta Crystallogr D* 78(11):1303-1314. DOI 10.1107/S2059798322010026.
- Montelione GT, Nilges M, Bax A, et al. (2013). Recommendations of the wwPDB NMR Validation Task Force. *Structure* 21(9):1563-1570. DOI 10.1016/j.str.2013.07.021.
<!-- END FILE: structural-biology/structure-validation/SKILL.md -->

<!-- END CATEGORY: structural-biology -->

