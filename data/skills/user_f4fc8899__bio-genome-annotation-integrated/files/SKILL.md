---
slug: bio-genome-annotation-integrated
version: 1.0.1
displayName: "基因组注释 / Genome annotation"
name: bio-genome-annotation-integrated
summary: "中文：基因组注释综合技能，整合 7 个相关专题，覆盖基因组注释：Bakta prokaryotic、BRAKER3 eukaryotic、ncRNA注释、功能注释、QC（BUSCO/CheckM2）。 English: Integrated Genome annotation skill covering 7 related topics, including Genome annotation: Bakta prokaryotic, BRAKER3 eukaryotic, ncRNA annotation, functional assignment, QC with BUSCO/CheckM2."
description: "中文：这是一个面向基因组注释的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：基因组注释：Bakta prokaryotic、BRAKER3 eukaryotic、ncRNA注释、功能注释、QC（BUSCO/CheckM2）。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：BRAKER3, BUSCO, Bakta。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Genome annotation, combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Genome annotation: Bakta prokaryotic, BRAKER3 eukaryotic, ncRNA annotation, functional assignment, QC with BUSCO/CheckM2. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: BRAKER3, BUSCO, Bakta. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# genome-annotation 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: genome-annotation -->

## 子目录：genome-annotation/annotation-qc

<!-- BEGIN FILE: genome-annotation/annotation-qc/SKILL.md -->
---
name: bio-genome-annotation-annotation-qc
description: Assesses the quality and completeness of a genome annotation with BUSCO (conserved single-copy ortholog recovery), OMArk (proteome completeness, consistency, and contamination), CheckM2 (prokaryotic completeness/contamination), and a gene-set sanity panel (gene count, mono-exonic fraction, protein-length distribution, mRNA:gene ratio, coding density). Covers the assembly-BUSCO-vs-proteome-BUSCO diagnostic, what BUSCO-Duplicated really means, why gene count is a vanity metric, and the QC of transferred annotations. Use when judging whether an annotation is good enough to publish or submit, diagnosing a suspect annotation, or comparing annotation completeness across pipelines.
tool_type: cli
primary_tool: BUSCO
---

## Version Compatibility

Reference examples tested with: BUSCO 5.5+, OMArk 0.3+, CheckM2 1.0+, compleasm 0.2.6+, gffutils 0.12+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

BUSCO results depend on the **lineage dataset** (e.g. `vertebrata_odb10` vs the shallow `eukaryota_odb10`) and the OrthoDB version - record them; a 99% on a shallow ~255-gene set and a 99% on a deep ~5,500-gene clade set are very different claims. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Annotation QC

**"Is my genome annotation any good?"** -> Measure conserved-gene completeness, proteome consistency/contamination, and gene-set sanity, and decide whether the limiting factor is the assembly or the predictor.
- CLI: `busco -i proteins.faa -m proteins -l <lineage>_odb10` (proteome) and `busco -i genome.fa -m genome -l <lineage>_odb10` (assembly), `omark`, `checkm2 predict` (prokaryotes)

## The Single Most Important Modern Insight -- BUSCO Measures the Easy 10%; the Diagnostic Is Genome-vs-Proteome

BUSCO completeness measures recovery of the ~1,000-5,500 most conserved single-copy orthologs - the most conserved, highly expressed, intron-stable genes any half-broken pipeline will find. A 98%-complete BUSCO confirms the housekeeping core is intact; it says **nothing** about whether the other ~20,000 models are chimeric, fragmented, frame-shifted, fused, or hallucinated from TEs. BUSCO is a smoke detector in one room of a burning house. Three load-bearing moves:

1. **Run assembly-BUSCO vs proteome-BUSCO on the same assembly - the diagnostic almost nobody runs.** `-m genome` does its own gene-finding; `-m proteins` scores the delivered proteome. If assembly is 98% and proteome is 85%, the genes are physically present and the *predictor* missed them - a training/evidence/masking problem, fixable without touching the assembly. If both are low, the genes aren't in the assembly - stop annotating and fix the assembly. This single fork redirects more wasted effort than any other check. (Always run BUSCO on the *delivered proteome*, `-m proteins`, not genome mode reported as if it described the annotation.)
2. **Gene count is a vanity metric.** The *same* assembly annotated by two pipelines routinely differs 20-40% in gene count, and a higher count is as likely to mean spurious TE ORFs and split models as more real genes. The diagnostic signal is in the **mono-exonic fraction, protein-length distribution, mean exons/gene, and mRNA:gene ratio** - not the headline count.
3. **Complement BUSCO with OMArk.** BUSCO's single-copy-ortholog lens is blind to over-prediction, chimeras, and contamination; OMArk assesses the *whole* proteome for completeness AND consistency (are genes consistent with their homologs?) and detects contaminant species. Use both.

## Tool Taxonomy

| Tool | Citation | Measures | Domain |
|------|----------|----------|--------|
| BUSCO | Manni 2021 *Mol Biol Evol* | conserved single-copy ortholog recovery (C/D/F/M) | euk + prok + viral; proteome/genome/transcriptome modes |
| OMArk | Nevers 2025 *Nat Biotechnol* | proteome completeness + consistency + contamination | eukaryotic proteomes; catches over-prediction BUSCO misses |
| compleasm | Huang 2023 | faster miniprot-based BUSCO-compatible completeness | euk; genome mode |
| CheckM2 | Chklovski 2023 *Nat Methods* | completeness + contamination (ML, lineage-agnostic) | bacteria/archaea, isolates + MAGs |
| Gene-set sanity panel | (gffutils) | gene count, mono-exonic %, protein length, mRNA:gene, coding density | any; the panel BUSCO can't provide |
| LAI | Ou 2018 *NAR* | LTR-RT assembly resolution (repeat-space contiguity) | LTR-rich genomes; assembly-side QC |

## Decision Tree by Scenario

| Scenario | QC to run | Why |
|----------|-----------|-----|
| Prokaryotic genome/MAG | CheckM2 (completeness/contamination) + coding density + tRNA/rRNA counts | CheckM2 is the field-standard completeness call; BUSCO is conservative on prokaryotes |
| Eukaryotic annotation | BUSCO `-m proteins` AND `-m genome` + OMArk + gene-set sanity panel | the genome-vs-proteome fork + over-prediction/contamination |
| Suspect high gene count | mono-exonic fraction + protein-length + BUSCO-Duplicated | distinguish haplotigs / unmasked TEs / split models |
| High BUSCO-Duplicated | check synteny + clade ploidy | uncollapsed haplotigs (purge) vs real WGD (keep) |
| Transferred annotation | BUSCO on the lifted set vs reference + ORF integrity | quantify silently lost conserved genes |
| Low proteome-BUSCO, high genome-BUSCO | fix evidence/masking/training | the genes are present; the predictor missed them |
| Both BUSCO low | -> genome-assembly/assembly-qc (purge_dups, more data) | the limit is the assembly |

## BUSCO and How to Read It

```bash
busco -i proteins.faa -m proteins -l vertebrata_odb10 -o busco_prot -c 16   # the delivered proteome
busco -i genome.fa    -m genome   -l vertebrata_odb10 -o busco_genome -c 16 # the assembly
```

Reported as `C:[S,D],F,M`: **Complete** (full-length match), **Duplicated** (subset of Complete, found ≥2x), **Fragmented** (partial), **Missing**. Use the **deepest applicable clade dataset**, not the shallow `eukaryota_odb10` (a 99% on a 255-gene set is trivially easy and not comparable to a 99% on a 5,500-gene clade set). **High Duplicated is the most-misread signal** - three causes, opposite responses: uncollapsed haplotigs (genome-wide, heterozygosity-scaled, non-syntenic -> purge_dups *before* annotating), real recent WGD (syntenic, ploidy-consistent, Ks duplication peak -> keep), or split models from a fragmented assembly. A clean haploid annotation runs ~1-3% Duplicated; >5-8% with no known WGD screams purge_dups first. compleasm is a faster miniprot-based alternative that often reports higher completeness than BUSCO's metaeuk path.

## OMArk (Proteome Consistency and Contamination)

```bash
omamer search --db LUCA.h5 --query proteins.faa --out proteins.omamer
omark -f proteins.omamer -d LUCA.h5 -o omark_out
```

OMArk catches what BUSCO's single-copy lens misses: it classifies the *whole* proteome as consistent / inconsistent (a gene whose structure conflicts with its homologs - a chimera or fragment) / unknown, and detects **contaminant species** mixed into the proteome. A high "inconsistent" fraction flags over-prediction or fused/split models even when BUSCO is green.

## CheckM2 (Prokaryotic Completeness/Contamination)

```bash
checkm2 predict --input genome.fna --output-directory checkm2_out --threads 16
```

For bacteria/archaea, CheckM2's lineage-agnostic ML model is the standard completeness/contamination call (handles reduced/novel lineages where marker sets fail). Gate annotation on it: **contamination >5%** mixes two organisms' genes into a chimeric set; **completeness <90% with contamination >5-10%** makes gene count, coding density, and hypothetical fraction uninterpretable - fix the assembly/binning first.

## Gene-Set Sanity Panel with Python

**Goal:** Compute the triage panel that reveals annotation health where gene count and BUSCO cannot.

**Approach:** Load the GFF3 into gffutils; compute the mRNA:gene ratio (1.00 = isoform/UTR-naive), the mono-exonic fraction, and the protein-length distribution; flag clade-anomalous values.

```python
import gffutils

MONOEXONIC_FLAG = 0.30   # >30% single-exon in a vertebrate suggests unmasked TEs/pseudogenes/fragments (calibrate per clade; fungi run higher)

def sanity_panel(gff_file):
    db = gffutils.create_db(gff_file, ':memory:', merge_strategy='merge')
    genes = list(db.features_of_type('gene'))
    mrnas = list(db.features_of_type(['mRNA', 'transcript']))
    exon_counts = [len(list(db.children(tx, featuretype='exon'))) for tx in mrnas]
    mono_frac = sum(1 for e in exon_counts if e == 1) / len(exon_counts) if exon_counts else 0
    mrna_per_gene = len(mrnas) / len(genes) if genes else 0
    if mrna_per_gene <= 1.001:
        print('WARNING: mRNA:gene == 1.00 -- isoform/UTR-naive; AS/3-prime-tag scRNA-seq analyses untrustworthy')
    if mono_frac > MONOEXONIC_FLAG:
        print(f'WARNING: mono-exonic fraction {mono_frac:.1%} high -- check masking/contamination')
    return {'genes': len(genes), 'mrna_per_gene': mrna_per_gene, 'mono_exonic_fraction': mono_frac}
```

Read gene count against the *nearest well-annotated relative* and the species' ploidy, never in isolation (1.5-2x with no WGD = haplotigs/over-prediction; ~0.5x = over-masking/under-training). A healthy protein-length distribution is unimodal near the clade-typical ~300-450 aa; a sub-100-aa spike = spurious/fragmented calls; a fat left tail = partials from a fragmented assembly.

## Per-Method Failure Modes

### Reporting genome-mode BUSCO as the annotation's score
**Trigger:** running BUSCO `-m genome` and citing it as annotation quality. **Mechanism:** genome mode does its own gene-finding, often better than the author's pipeline on the conserved core. **Symptom:** reported BUSCO higher than the real proteome BUSCO. **Fix:** run `-m proteins` on the delivered proteome; report both and compare.

### High Duplicated read as success
**Trigger:** treating high BUSCO-D as good. **Mechanism:** uncollapsed haplotigs vs real WGD vs split models. **Symptom:** inflated gene count. **Fix:** plot duplicated pairs against synteny + clade ploidy; if no WGD and D>5-8%, purge_dups the assembly first.

### Shallow lineage dataset
**Trigger:** `eukaryota_odb10` (~255 genes) instead of the deep clade set. **Mechanism:** a small, conserved set is trivially easy to hit 99%. **Symptom:** misleadingly high completeness. **Fix:** use the deepest applicable clade dataset; record it.

### BUSCO alone, no OMArk
**Trigger:** judging a proteome by BUSCO completeness only. **Mechanism:** the single-copy-ortholog lens misses over-prediction, chimeras, and contamination. **Symptom:** green BUSCO on a proteome full of fused/fragmented or contaminant models. **Fix:** add OMArk for consistency + contamination.

### Annotating before the QC gate (prokaryote)
**Trigger:** Bakta/Prokka before CheckM2. **Mechanism:** contamination mixes organisms; low completeness truncates. **Symptom:** chimeric/inflated gene set, uninterpretable coding density. **Fix:** CheckM2 first; contamination >5% -> decontaminate.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Assembly-BUSCO vs proteome-BUSCO gap | the diagnostic fork | large gap = predictor missed present genes; both low = fix assembly |
| BUSCO-Duplicated ~1-3% (clean haploid); >5-8% no WGD | assembly norm | purge_dups before annotating |
| Use deepest applicable clade `_odb10` | BUSCO guidance | shallow sets trivially hit 99% |
| Mono-exonic ~10-20% (vertebrate); >25-30% flag | clade norm | unmasked TEs/pseudogenes/fragments; fungi legitimately higher |
| Protein length unimodal ~300-450 aa | eukaryote norm | sub-100-aa spike = spurious; fat left tail = partials |
| mRNA:gene ratio == 1.00 | annotation structure | isoform/UTR-naive |
| CheckM2 contamination ≤5%, completeness ≥90% | MIMAG-aligned | above/below -> prokaryotic QC numbers uninterpretable |
| Prokaryotic coding density ~88-90% | bacterial norm | <85% wrong table/fragmentation; >93% over-calling |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| BUSCO high, annotation still bad | BUSCO measures only the conserved core | add OMArk + sanity panel; inspect mono-exonic models |
| Proteome-BUSCO < genome-BUSCO | predictor missed present genes | fix evidence/masking/training, not the assembly |
| High Duplicated | haplotigs vs WGD vs split models | synteny + ploidy check; purge_dups if no WGD |
| 99% completeness looks too good | shallow lineage dataset | rerun with the deep clade set |
| Cross-pipeline gene counts disagree | gene count is not a quality metric | compare sanity panels, not counts |
| CheckM2 high contamination | mixed organisms / poor binning | decontaminate before annotation |

## References

- Manni M, et al. 2021. BUSCO update: novel and streamlined workflows along with broader and deeper phylogenetic coverage for scoring of eukaryotic, prokaryotic, and viral genomes. *Mol Biol Evol* 38:4647-4654.
- Simão FA, et al. 2015. BUSCO: assessing genome assembly and annotation completeness with single-copy orthologs. *Bioinformatics* 31:3210-3212.
- Nevers Y, et al. 2025. Quality assessment of gene repertoire annotations with OMArk. *Nat Biotechnol* 43:124-133.
- Chklovski A, et al. 2023. CheckM2: a rapid, scalable and accurate tool for assessing microbial genome quality using machine learning. *Nat Methods* 20:1203-1212.
- Huang N, Li H. 2023. compleasm: a faster and more accurate reimplementation of BUSCO. *Bioinformatics* 39:btad595.
- Guan D, et al. 2020. Identifying and removing haplotypic duplication in primary genome assemblies (purge_dups). *Bioinformatics* 36:2896-2898.
- Ou S, Chen J, Jiang N. 2018. Assessing genome assembly quality using the LTR Assembly Index (LAI). *Nucleic Acids Res* 46:e126.

## Related Skills

- eukaryotic-gene-prediction - The annotation whose proteome/gene-set this QC evaluates
- prokaryotic-annotation - CheckM2 gate and coding-density sanity for prokaryotes
- annotation-transfer - BUSCO on a lifted set quantifies silently lost conserved genes
- repeat-annotation - LAI and over-masking diagnosis in the assembly-to-annotation handoff
- genome-assembly/assembly-qc - Assembly-side completeness; purge haplotigs before annotating
<!-- END FILE: genome-annotation/annotation-qc/SKILL.md -->

## 子目录：genome-annotation/annotation-transfer

<!-- BEGIN FILE: genome-annotation/annotation-transfer/SKILL.md -->
---
name: bio-genome-annotation-annotation-transfer
description: Transfers gene annotations between genome assemblies via coordinate liftover (UCSC liftOver, CrossMap for same-species version updates) or feature/sequence projection (Liftoff for same/close species, miniprot for protein-level cross-species, TOGA/GeMoMa/CAT for distant clades). Covers the coordinate-vs-projection decision by divergence, why a successful lift is not biological confirmation, reference bias, the silent-dropping of unmapped features, build/PAR/MHC/inversion hazards, and transfer-vs-de-novo validation. Use when annotating a new assembly of a species with an existing reference, harmonizing coordinates across builds, or mapping annotations across related species.
tool_type: cli
primary_tool: Liftoff
---

## Version Compatibility

Reference examples tested with: Liftoff 1.6.3+, LiftoffTools 0.4+, miniprot 0.13+, CrossMap 0.7+, UCSC liftOver (current), BioPython 1.83+, gffutils 0.12+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

The **chain file must match the exact assembly pair** (build and patch); the **source and target build must be recorded** with every coordinate (a coordinate without a build is unusable). If code throws an error, introspect the installed tool and adapt rather than retrying.

# Annotation Transfer

**"Transfer annotations from a reference to my new assembly"** -> Map gene models from a well-annotated reference onto a target, by coordinate liftover (same-species, fast) or by re-aligning the actual gene sequence (cross-assembly/species, structure-aware), then validate against the target.
- CLI: `liftoff -g ref.gff3 -o out.gff3 -u unmapped.txt target.fa reference.fa` (note: target before reference), `liftOver in.bed map.chain out.bed unmapped` (intervals)

## The Single Most Important Modern Insight -- A Lift Is Geometry, Not Biology

Coordinate liftover and feature projection answer different questions, and choosing the wrong one is the dominant failure mode:

- **Coordinate liftover** (liftOver/CrossMap, on pre-computed chains) answers *"where does this interval sit in the other assembly's coordinate system?"* It moves numbers; it never re-examines the sequence.
- **Feature projection** (Liftoff/miniprot/TOGA) answers *"where is this gene, with its exon-intron structure intact, and is it still a functional gene?"* It re-aligns the biological sequence.

Three load-bearing consequences:

1. **A successful lift is not biological confirmation.** liftOver can place a gene at perfectly valid target coordinates that land in a pseudogenized, frameshifted, or collapsed-duplication region - the coordinate is right and the gene is dead, and the tool has no vocabulary to flag it. The output GFF inherits the reference's `gene`/`CDS` feature types verbatim. The "it mapped, ship it" culture is how a lifted GFF acquires the social status of a validated annotation while no one ever re-derived a model from sequence. Treat every lifted annotation as a hypothesis until target evidence (intact ORF, identity distribution, BUSCO, RNA-seq) has touched it.
2. **Transfer is reference-biased: it can only reproduce what the reference annotated.** Lineage-specific genes, target-specific expansions, novel isoforms, and orphan genes are *structurally invisible* - the new assembly's actual novelty (the reason it is interesting) is exactly what transfer cannot see. Always pair transfer with de novo + evidence; TOGA can call gene *loss* but is constitutionally incapable of calling gene *gain*.
3. **Read and classify the unmapped file - it is the most information-rich output.** liftOver writes failures to a side file, exits 0, and prints a clean shorter GFF with no visual tell; entire gene families can vanish silently. "Deleted in new" vs "Split in new" vs "Duplicated in new" are biologically distinct diagnoses (chain gap / rearrangement breakpoint / segmental duplication or gene family).

## Two Paradigms

| Paradigm | Tools | Operates on | Right for |
|----------|-------|-------------|-----------|
| A. Coordinate liftover | UCSC liftOver, CrossMap, segment_liftover, paftools | pre-computed chains; intervals (BED/GFF/VCF/BAM) | same-species version updates (hg19<->hg38, mm10<->mm39); variant/peak/CNV harmonization |
| B. Feature/sequence projection | Liftoff (nt), miniprot (protein), GeMoMa, TOGA, CAT, LiftOn | re-aligned gene sequence | cross-assembly/species; full gene models; polyploid/duplicated; no reliable chain |

## Decision Tree by Divergence

| Divergence | Recommended | Why |
|------------|-------------|-----|
| Same species, transfer intervals | liftOver / CrossMap | chain is dense; geometry suffices for variants/peaks |
| Same species, transfer gene models | Liftoff (`-chroms`) | structure-aware; per-interval liftOver fragments transcripts |
| Same genus (a few % divergence) | Liftoff + miniprot rescue for the divergent tail | nucleotide alignment robust; protein for the rest |
| Same family/order (tens-hundreds My) | TOGA or GeMoMa (multi-reference) | nucleotide saturates; orthology + gene-loss reasoning |
| Beyond family / lineage-specific content / heavy rearrangement | -> eukaryotic-gene-prediction (de novo) + transfer as evidence | reference too far; only de novo sees target-specific biology |
| Pan-genome / multi-haplotype | `vg annotate` onto the graph | avoids single-reference bias (tooling still maturing) |

Cross-species *coordinate* liftover is a methodological error (synteny fragments into thousands of short chains; most genes drop silently) - it is the wrong paradigm, not a tuning problem.

## Liftoff (Same / Close Species, Nucleotide)

```bash
liftoff -g reference.gff3 -o lifted.gff3 -u unmapped.txt -p 16 \
    -chroms chrom_map.txt -polish target.fasta reference.fasta
```

Positional args are **target first, then reference** (commonly swapped - a silent error). Liftoff extracts each gene's exon sequence, aligns with minimap2, and chooses the placement maximizing identity while preserving exon-intron structure. Key flags: `-a` (alignment coverage, default 0.5), `-s` (sequence identity, default 0.5), `-copies`/`-sc` (search for extra gene copies - a per-family decision, not a default), `-polish` (re-align to restore intact start/stop/splice, writes `*_polished.gff3`), `-exclude_partial`, `-chroms` (ordered chromosome mapping; reduces false cross-chromosome placements). LiftoffTools QCs the result (variants, synteny, copy-number changes). Same-species version updates should lift ≥99% - a 97% rate is a four-alarm signal of the wrong chain or coordinate-convention mismatch, not "pretty good."

## miniprot (Cross-Species, Protein)

```bash
miniprot -t 16 -d target.mpi target.fasta            # optional index
miniprot -Iut 16 --gff target.mpi proteins.faa > out.gff
```

Protein conserves far deeper than nucleotide (synonymous sites saturate), so miniprot works across species where Liftoff's nucleotide alignment fails. `-I` auto-sets max intron from genome length; `--gff` emits GFF3. **Frameshift and in-frame-stop tags in the output are the signal that the "gene" is pseudogenized in the target, not a clean ortholog** - inspect them; do not treat a miniprot hit as a functional gene by default. For a polished multi-reference, intron-aware annotation use GeMoMa (which reasons about intron-position conservation); for the DNA+protein hybrid use LiftOn.

## TOGA (Distant Species, Orthology + Gene Loss)

TOGA consumes a genome-alignment chain + reference BED12 and uses ML on chain features (including intronic/intergenic flanks - orthologs share flanking context, paralogs/retrocopies do not) to classify orthology (one2one ... one2zero) and **gene-loss/intactness** (intact / partially intact / lost / missing). It exists *precisely because* across deep time an inactivated gene still aligns - a coordinate lift reports the corpse as "present." Use TOGA for whole-clade ortholog projection; it does not discover target-specific novel genes (the reference-bias caveat of all of Paradigm B).

## Validating a Transfer with Python

**Goal:** Quantify transfer quality and, critically, check that lifted CDS are biologically intact, not just placed.

**Approach:** Compare gene counts for a transfer rate, then translate each lifted CDS from the target and check for a valid start, a single terminal stop, and correct length - coordinate success is not intactness.

```python
import gffutils
from Bio import SeqIO

def orf_integrity(lifted_gff, target_fasta):
    genome = SeqIO.to_dict(SeqIO.parse(target_fasta, 'fasta'))
    db = gffutils.create_db(lifted_gff, ':memory:', merge_strategy='merge')
    valid = total = 0
    for cds in db.features_of_type('CDS'):
        total += 1
        seq = genome[cds.seqid].seq[cds.start - 1:cds.end]
        if cds.strand == '-':
            seq = seq.reverse_complement()
        prot = seq.translate()
        if prot.startswith('M') and prot.endswith('*') and prot.count('*') == 1:
            valid += 1
    print(f'Intact ORFs: {valid}/{total} ({valid/total:.1%}) -- a clean lift can still land in a pseudogene')
    return valid, total
```

Also: read and **classify** the unmapped file (not just count it); run BUSCO on the *lifted protein set* and compare to the reference (a drop quantifies silently lost conserved genes); compare to a de novo annotation to expose reference bias.

## Hazards and the 1% That Matters

- **The 1% that does not lift trivially is enriched for the interesting parts.** ~99% of the human genome lifts hg19<->hg38 (liftOver ~99.99% over ~1.57M ClinVar variants), but failures concentrate in indels/large duplications (a pathogenic 8.1 kb *LDLR* duplication failed all three tools), PAR (double-maps), MHC, segmental duplications, centromeres/telomeres, and regions inverted between GRCh37/GRCh38 where coordinate conversion silently corrupts palindromic SNVs and imputation (the chr10 *MSMB*/rs10993994 prostate-cancer signal dropped p=2.86e-7 to 0.0011 across ~20,000 individuals; Sheng 2022). A lift touching any of these is suspect until validated.
- **Coordinate conventions and build identity bite.** BED is 0-based half-open; GFF/GTF/VCF are 1-based closed - a conversion at a format boundary shifts every start by 1 (passes smell tests, corrupts splice/start bases). VCF lifts must update the REF allele (CrossMap does; naive shifting does not). hg19 chrM (NC_001807) is *not* rCRS (NC_012920) - two files both labeled "hg19" can have incompatible mitochondrial coordinates.
- **Accumulation without revalidation.** Annotations get lifted v1->v2->v3 forever; a model wrong in 2009 stays byte-for-byte wrong in 2024 because lifting copies models without re-examining them. Re-run de novo + evidence at major assembly upgrades and reconcile.

## Per-Method Failure Modes

### Cross-species coordinate liftover
**Trigger:** liftOver/CrossMap to transfer genes between species. **Mechanism:** synteny fragments into short chains; most genes have no co-linear counterpart. **Symptom:** plausible-looking output that silently dropped most genes. **Fix:** miniprot/TOGA/GeMoMa (sequence/orthology), not chains.

### Not reading the unmapped file
**Trigger:** reporting a transfer complete from the success file alone. **Mechanism:** failures go to a side file; exit code 0. **Symptom:** a clean GFF missing entire gene families. **Fix:** read and classify unmapped (deletion/split/duplicated).

### Coordinate success treated as intactness
**Trigger:** trusting a lifted gene because it placed. **Mechanism:** the locus can be pseudogenized/frameshifted. **Symptom:** RNA-seq quantified against a gene with an internal stop at residue 40. **Fix:** `-polish` + ORF check; miniprot frameshift tags; TOGA intactness class.

### Swapped Liftoff positional args
**Trigger:** `liftoff ... reference.fa target.fa`. **Mechanism:** Liftoff is `target reference`. **Symptom:** nonsense mapping. **Fix:** target first, reference last.

### Loosening `-a`/`-s` to "rescue" features
**Trigger:** lowering coverage/identity to clear the unmapped pile. **Mechanism:** a 35%-coverage hit is usually a paralog/pseudogene/repeat match. **Symptom:** low-confidence placements laundered into the success file. **Fix:** treat default-threshold failures as signal; loosen only with a biological hypothesis and validate rescues individually.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Same-species mapping rate ≥99% | Liftoff/ClinVar studies | a 97% rate signals wrong chain / convention mismatch |
| Liftoff `-a`/`-s` default 0.5 | Liftoff | loosening manufactures false placements; failure is often signal |
| liftOver `-minMatch` default 0.95 (per-feature) | UCSC | a long feature with one chain gap fails silently |
| BUSCO on lifted set vs reference | completeness audit | a drop quantifies silently lost conserved genes |
| Divergence rule: species->liftOver/Liftoff; genus->+miniprot; family->TOGA/GeMoMa; beyond->de novo | lab convention | matches paradigm to where the chain/identity breaks |
| Every coordinate carries its build | reproducibility | a coordinate without a build is unusable |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Many unmapped features (same species) | wrong/patch-mismatched chain; contig naming (`chr1` vs `1`) | use the exact-pair chain; harmonize names |
| Mass gene loss, clean GFF | silent dropping | read/classify the unmapped file |
| Lifted genes with internal stops | landed in pseudogene/frameshift | `-polish`; ORF check; re-predict de novo in problem loci |
| Paralog/copy collapse or swap | no `-copies`, or mapped to the paralog | `-copies`/`-sc` per family; TOGA orthology graph |
| Most genes lost cross-species | coordinate liftover used across species | switch to miniprot/TOGA |
| mtDNA coordinates don't match | hg19 chrM != rCRS | record the exact MT record, not just "hg19" |

## References

- Shumate A, Salzberg SL. 2021. Liftoff: accurate mapping of gene annotations. *Bioinformatics* 37:1639-1643.
- Shumate A, Salzberg SL. 2024. LiftoffTools: a toolkit for comparing gene annotations mapped between genome assemblies. *F1000Research* 11:1230.
- Li H. 2023. Protein-to-genome alignment with miniprot. *Bioinformatics* 39:btad014.
- Zhao H, et al. 2014. CrossMap: a versatile tool for coordinate conversion between genome assemblies. *Bioinformatics* 30:1006-1007.
- Hinrichs AS, et al. 2006. The UCSC Genome Browser Database: update 2006. *Nucleic Acids Res* 34:D590-D598.
- Kent WJ, et al. 2003. Evolution's cauldron: duplication, deletion, and rearrangement in the mouse and human genomes (chains and nets). *PNAS* 100:11484-11489.
- Keilwagen J, et al. 2016. Using intron position conservation for homology-based gene prediction (GeMoMa). *Nucleic Acids Res* 44:e89.
- Otto TD, et al. 2011. RATT: Rapid Annotation Transfer Tool. *Nucleic Acids Res* 39:e57.
- Kirilenko BM, et al. 2023. Integrating gene annotation with orthology inference at scale (TOGA). *Science* 380:eabn3107.
- Fiddes IT, et al. 2018. Comparative Annotation Toolkit (CAT): simultaneous clade and personal genome annotation. *Genome Res* 28:1029-1038.
- Chao KH, et al. 2025. Combining DNA and protein alignments to improve genome annotation with LiftOn. *Genome Res* 35:311-325.
- Sheng X, Xia L, Cahoon JL, Conti DV, Haiman CA, Kachuri L, Chiang CWK. 2022. Inverted genomic regions between reference genome builds in humans impact imputation accuracy and decrease the power of association testing. *HGG Adv* 4:100159.

## Related Skills

- eukaryotic-gene-prediction - De novo annotation; the complement that captures target-specific genes
- annotation-qc - BUSCO on the lifted set and gene-structure integrity checks
- comparative-genomics/ortholog-inference - Orthology relationships across species
- comparative-genomics/synteny-analysis - Synteny context that validates or refutes a transfer
- genome-intervals/gtf-gff-handling - Parse and manipulate transferred annotations
<!-- END FILE: genome-annotation/annotation-transfer/SKILL.md -->

## 子目录：genome-annotation/eukaryotic-gene-prediction

<!-- BEGIN FILE: genome-annotation/eukaryotic-gene-prediction/SKILL.md -->
---
name: bio-genome-annotation-eukaryotic-gene-prediction
description: Predicts protein-coding gene structures (exons, introns, UTRs) in eukaryotic genomes with BRAKER3 (RNA-seq + protein evidence), BRAKER1/BRAKER2, GALBA (protein-only), Funannotate (fungi), GeMoMa (homology projection), or Helixer/Tiberius (deep-learning ab initio). Covers the evidence-first tool decision, mandatory soft-masking, the training-set-quality-dominates principle, OrthoDB clade-partition selection, the one-isoform-per-locus and missing-UTR traps, merge/split errors, and reference bias against orphan genes. Use when annotating a newly assembled eukaryotic genome, choosing a gene-prediction pipeline based on available evidence, or diagnosing a poor annotation.
tool_type: cli
primary_tool: BRAKER3
---

## Version Compatibility

Reference examples tested with: BRAKER 3.0+, GALBA 1.0.11+, AUGUSTUS 3.5+, Funannotate 1.8+, HISAT2 2.2.1+, STAR 2.7.11+, BUSCO 5.5+, samtools 1.19+, gffutils 0.12+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

Reproducibility is engineered, not assumed: run BRAKER/GALBA/Funannotate from their official containers, and pin the **OrthoDB partition version** (v11 vs v12 give different hints -> different models), the repeat library, and the Dfam release. GeneMark (inside BRAKER) historically required an expiring academic `.gm_key`; the requirement has relaxed in recent versions but check the installed version's docs. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Eukaryotic Gene Prediction

**"Predict genes in my eukaryotic genome"** -> Identify protein-coding gene structures from a soft-masked assembly using RNA-seq and/or protein evidence to train and guide a gene finder.
- CLI: `braker.pl --genome=masked.fa --prot_seq=orthodb_clade.fa --rnaseq_sets_ids=SRR... --softmasking` (BRAKER3)

## The Single Most Important Modern Insight -- Training-Set Quality and Evidence Dominate, Not the Algorithm

Gene-prediction accuracy is governed by the quality of the **training set** and the **extrinsic evidence**, not by which gene-finder is chosen. A 2024-era HMM (AUGUSTUS) trained on a clean, evidence-validated gene set beats a fancier model trained on garbage. This reframes every decision:

- BRAKER3's accuracy jump is **not** a better HMM and **not** the TSEBRA combiner (the common misattribution). It is GeneMark-ETP's method of mining a **high-confidence training set** from loci where RNA-seq-assembled transcripts AND protein homology independently agree, then training AUGUSTUS on that (Brůna 2024 *Genome Res* 34:757; Gabriel 2024 *Genome Res* 34:769). BRAKER3 beats BRAKER1/2 because it learns from loci it has two reasons to trust.
- Therefore the **first** question is "what evidence do I have, and is it from the right clade?" - not "which tool?" Soft-masking and OrthoDB-partition choice are upstream of, and more consequential than, the predictor.
- **The #1 silent killer is training on a bad assembly.** A finder trained on a contaminated, fragmented, or repeat-polluted assembly produces confidently wrong models *genome-wide* that are syntactically valid, BUSCO-complete, and undetectable from the GFF3. Decontaminate and check assembly contiguity/BUSCO **before** any self-trainer touches the genome.
- The 2025-2026 deep-learning twist: Tiberius/Helixer can match BRAKER3's evidence-based accuracy with **no evidence at all** on well-represented clades (vertebrates) - but they degrade on under-represented lineages and are isoform/UTR-naive. The field is mid-transition; do not present DL as universally superior.

## Tool Taxonomy

| Pipeline | Citation | Evidence used | When |
|----------|----------|---------------|------|
| BRAKER3 | Gabriel 2024 *Genome Res* | RNA-seq + protein (OrthoDB) | **Default when both exist**; HC-training-set method |
| BRAKER1 | Hoff 2016 *Bioinformatics* | RNA-seq only | spliced-read intron hints train GeneMark-ET |
| BRAKER2 | Brůna 2021 *NAR Genom Bioinform* | protein only (broad OrthoDB) | ProtHint mines hints from a remote protein DB |
| GALBA | Brůna 2023 *BMC Bioinformatics* | protein only (close relatives) | beats BRAKER2 on large vertebrate genomes with good close proteomes |
| GeMoMa | Keilwagen 2018 *BMC Bioinformatics* | reference annotation + intron-position conservation | project an existing close-relative annotation |
| Funannotate | Palmer & Stajich 2020 (Zenodo) | any | **fungal de facto standard**; train->predict(EVM)->update(PASA) |
| MAKER2 / EVM | Holt 2011; Haas 2008 | many tracks | combiner / build-it-yourself route; transparent evidence weighting |
| Helixer / Tiberius | Stiehler 2020; Gabriel 2024 | none (ab initio, DL) | evidence-poor genomes in well-represented clades |
| AUGUSTUS / GeneMark-ES | Stanke 2006; Lomsadze | hints / self-train | components; standalone ab initio is the last resort |

OrthoDB rule: BRAKER2/3 want a **clade partition** (pick the smallest partition that still contains the target clade - Vertebrata for a fish, not all Metazoa). GALBA wants a few **close-relative proteomes**, not a broad clade.

## Decision Tree by Scenario

| Evidence / scenario | Recommended | Why |
|---------------------|-------------|-----|
| RNA-seq + protein DB | BRAKER3 | state-of-the-art at all genome sizes |
| RNA-seq only | BRAKER1 | intron hints from spliced reads |
| Protein only, close relatives | GALBA | miniprot-aligned close proteomes train AUGUSTUS |
| Protein only, broad/distant | BRAKER2 | ProtHint mines a remote OrthoDB clade |
| No evidence, represented clade | Tiberius or Helixer | DL ab initio now matches evidence-based on vertebrates |
| Reference annotation of a close relative | GeMoMa | homology + intron-position projection |
| Fungus (any evidence) | Funannotate | tiny-intron-aware; bundled EVM + PASA update |
| Need isoforms + UTRs | add PASA / Iso-Seq update step | predictors emit one CDS-only model per locus |
| Genome not yet masked | -> repeat-annotation (soft-mask first) | mandatory prerequisite |
| Want to assess the result | -> annotation-qc | BUSCO genome-vs-proteome, OMArk, sanity metrics |

## Soft-Masking Is Mandatory (Prerequisite)

Run repeat-annotation to **soft-mask** (repeats -> lowercase) before prediction. Unmasked TEs contain ORFs and pseudo-splice-sites; the predictor calls thousands of spurious genes inside repeats (catastrophic in plants where >80% of the genome can be TE) and TE domains pollute training. Pass `--softmasking` so BRAKER honors lowercase as a soft penalty (a real gene can still span a repeat). **Hard-masking (repeats -> N) destroys sequence and truncates real repeat-overlapping genes - avoid it for prediction.** But over-aggressive masking with an uncurated library deletes real multi-copy families (NLR/R-genes, zinc-fingers): filter the repeat library against a protein DB and confirm conserved families survive.

## BRAKER3 (RNA-seq + Protein)

```bash
# Align RNA-seq with a splice-aware aligner; output sorted BAM
hisat2-build masked.fasta idx
hisat2 -x idx -1 R1.fq.gz -2 R2.fq.gz --dta -p 16 | samtools sort -@4 -o rnaseq.bam
samtools index rnaseq.bam

# BRAKER3: protein = an OrthoDB clade partition (smallest that contains the clade)
braker.pl --genome=masked.fasta --prot_seq=Vertebrata.fa \
    --bam=rnaseq.bam --softmasking --threads=16 --species=my_species \
    --gff3 --workingdir=braker3_out
```

`--rnaseq_sets_ids=SRR...,SRR... --rnaseq_sets_dirs=/fastq/` auto-downloads/aligns reads in place of `--bam`. Outputs: `braker.gtf`/`braker.gff3` (TSEBRA-combined), `braker.codingseq`, `braker.aa`.

## GALBA (Protein-Only, Close Relatives)

```bash
galba.pl --genome=masked.fasta --prot_seq=close_relatives.faa \
    --species=my_species --threads=16
```

Prefer BRAKER3 whenever RNA-seq exists - intron evidence substantially improves splice-site accuracy.

## Funannotate (Fungi)

```bash
funannotate mask -i assembly.fa -o masked.fa --cpus 16
funannotate train -i masked.fa -o out -l R1.fq -r R2.fq --species "Genus species"
funannotate predict -i masked.fa -o out -s "Genus species" \
    --transcript_evidence transcripts.fa --protein_evidence proteins.fa
funannotate update -i out --cpus 16     # PASA adds UTRs and isoforms
```

## Gene-Model Sanity Statistics with Python

**Goal:** Compute the triage panel that reveals annotation health where gene count and BUSCO cannot - the isoform ratio, mono-exonic fraction, and protein-length distribution.

**Approach:** Load the GFF3 into gffutils; compute the mRNA:gene ratio (1.00 = isoform-naive), the single-exon fraction, and CDS-length stats; flag clade-anomalous values.

```python
import gffutils

MONOEXONIC_FLAG = 0.30   # >30% single-exon in a vertebrate suggests unmasked TEs/pseudogenes/fragments (calibrate per clade)

def gene_model_stats(gff_file):
    db = gffutils.create_db(gff_file, ':memory:', merge_strategy='merge')
    genes = list(db.features_of_type('gene'))
    mrnas = list(db.features_of_type(['mRNA', 'transcript']))
    exon_counts = [len(list(db.children(tx, featuretype='exon'))) for tx in mrnas]
    mono_frac = sum(1 for e in exon_counts if e == 1) / len(exon_counts) if exon_counts else 0
    mrna_per_gene = len(mrnas) / len(genes) if genes else 0
    if mrna_per_gene <= 1.001:
        print('WARNING: one isoform per locus (mRNA:gene == 1.00) -- isoform/UTR-naive; AS analyses untrustworthy')
    if mono_frac > MONOEXONIC_FLAG:
        print(f'WARNING: mono-exonic fraction {mono_frac:.1%} high -- check masking/contamination')
    return {'genes': len(genes), 'mrna_per_gene': mrna_per_gene, 'mono_exonic_fraction': mono_frac}
```

## Hard Biology the Pipeline Gets Wrong

- **One isoform per locus, no UTRs.** Almost every de novo annotation ships a single CDS-only model per gene (mRNA:gene == 1.00). This silently breaks downstream alternative-splicing/isoform-switching analysis (a switch the reference doesn't contain cannot be detected), and missing 3' UTRs break 3'-tag scRNA-seq (10x reads land "intergenic" and are discarded), APA, and miRNA-target work. The only fix is a transcript-evidence update (PASA, or Iso-Seq via `funannotate update`). Human GENCODE has ~4-5 isoforms/gene; a fresh annotation has one.
- **Merge/split errors are invisible to automated QC.** Tandem arrays (NLR clusters, immune loci) fuse into one elongated model; genes split across contig breaks become two partials; read-through transcription fuses two genes (evidence-supported, so especially nasty); a long intron read as intergenic splits one gene in two. Long-read Iso-Seq + a contiguous assembly prevent these; they hide in the length/exon-count tails otherwise.
- **Reference bias against orphan genes.** Protein-evidence pulls models toward known genes and away from lineage-specific/fast-evolving/orphan genes - exactly the novel biology. Apparent "lineage-specific" genes are often just homology-detection failure (Weisman 2020 *PLoS Biol* 18:e3000862). Keep well-supported ab initio/DL calls in repeat-free RNA-seq-supported regions rather than filtering to "evidence-supported only," which amputates the orphan set.
- **Protists break the spliceosome.** Alternative genetic codes (ciliate UAA/UAG -> Gln), trans-splicing (kinetoplastids, nematodes), and polycistronic transcription mean generic eukaryote models truncate or mis-call. Set the correct translation table and know the RNA-processing biology before trusting any predictor.

## Per-Method Failure Modes

### Unmasked or hard-masked genome
**Trigger:** running BRAKER without soft-masking, or hard-masking. **Mechanism:** TE ORFs become genes / masked sequence truncates real genes. **Symptom:** 2x inflated gene count, high mono-exonic fraction, or fragmented models. **Fix:** soft-mask with a curated library; pass `--softmasking`.

### Training on a bad assembly
**Trigger:** annotating a contaminated/fragmented assembly. **Mechanism:** self-trainer learns contaminant/truncated gene structure and applies it genome-wide. **Symptom:** confidently wrong, BUSCO-green models. **Fix:** decontaminate (FCS-GX/BlobTools) and check assembly BUSCO/N50 first.

### Wrong AUGUSTUS species / OrthoDB partition
**Trigger:** a "close enough" pre-trained species or wrong clade partition. **Mechanism:** splice-site/intron-length params or protein hints mismatched. **Symptom:** systematically mis-placed exon boundaries; clean-looking GFF3. **Fix:** train on the target (BRAKER does this); pick the smallest correct OrthoDB clade.

### Expecting isoforms/UTRs from a one-model pipeline
**Trigger:** AS/3'-tag/APA analysis against a de novo annotation. **Mechanism:** one CDS-only model per locus. **Symptom:** discarded scRNA-seq reads; empty AS results. **Fix:** add a PASA/Iso-Seq update step; check mRNA:gene ratio.

### High BUSCO-Duplicated read as success
**Trigger:** treating high D as good. **Mechanism:** uncollapsed haplotigs vs real WGD vs split models. **Symptom:** inflated gene count. **Fix:** if no known WGD and D>5-8%, purge_dups the assembly first; if known polyploid, confirm via synteny/Ks and keep.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Soft-mask before prediction | universal | unmasked TEs inflate spurious genes |
| Gene count vs nearest relative (±, reconcile with ploidy) | clade norm | 1.5-2x with no WGD = haplotigs/over-prediction; ~0.5x = over-masking/under-training |
| Mono-exonic fraction ~10-20% (vertebrate) | clade norm | >25-30% = unmasked TEs/pseudogenes/fragments; fungi legitimately higher |
| Protein length unimodal ~300-450 aa | eukaryote norm | sub-100-aa spike = spurious/fragmented; fat left tail = partials |
| BUSCO-Duplicated ~1-3% (clean haploid) | assembly norm | >5-8% with no WGD -> purge_dups before annotating |
| mRNA:gene ratio | annotation structure | == 1.00 means isoform/UTR-naive |
| Pick smallest OrthoDB partition containing the clade | BRAKER guidance | broader = noisier hints, slower |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Thousands of extra short genes | unmasked repeats | soft-mask; `--softmasking` |
| BRAKER fails mid-run | expired GeneMark key / special chars in FASTA headers | use the container; `sed 's/ .*//' genome.fa` |
| Many single-exon genes | unmasked TEs / contamination / fragmented assembly | verify masking; decontaminate; check N50 |
| Low protein-BUSCO, high genome-BUSCO | predictor missed present genes (training/evidence) | fix evidence/masking, not the assembly |
| AS analysis returns nothing | one-isoform annotation | run PASA/Iso-Seq update |
| Suspiciously few NLR/ZNF genes | over-masked with uncurated library | filter repeat library against a protein DB |

## References

- Stanke M, et al. 2006. Gene prediction with a hidden Markov model and a new intron submodel (AUGUSTUS). *BMC Bioinformatics* 7:62.
- Hoff KJ, et al. 2016. BRAKER1: unsupervised RNA-Seq-based genome annotation with GeneMark-ET and AUGUSTUS. *Bioinformatics* 32:767-769.
- Brůna T, et al. 2021. BRAKER2: automatic eukaryotic genome annotation with GeneMark-EP+ and AUGUSTUS supported by a protein database. *NAR Genom Bioinform* 3:lqaa108.
- Gabriel L, et al. 2024. BRAKER3: fully automated genome annotation using RNA-seq and protein evidence with GeneMark-ETP, AUGUSTUS, and TSEBRA. *Genome Res* 34:769-777.
- Brůna T, et al. 2024. GeneMark-ETP significantly improves the accuracy of automatic annotation of large eukaryotic genomes. *Genome Res* 34:757-768.
- Gabriel L, et al. 2021. TSEBRA: transcript selector for BRAKER. *BMC Bioinformatics* 22:566.
- Brůna T, et al. 2023. GALBA: genome annotation with miniprot and AUGUSTUS. *BMC Bioinformatics* 24:327.
- Keilwagen J, et al. 2018. Combining RNA-seq data and homology-based gene prediction for plants, animals and fungi (GeMoMa). *BMC Bioinformatics* 19:189.
- Haas BJ, et al. 2008. Automated eukaryotic gene structure annotation using EVidenceModeler. *Genome Biol* 9:R7.
- Haas BJ, et al. 2003. Improving the Arabidopsis genome annotation using maximal transcript alignment assemblies (PASA). *Nucleic Acids Res* 31:5654-5666.
- Gabriel L, et al. 2024. Tiberius: end-to-end deep learning with an HMM for gene prediction. *Bioinformatics* 40:btae685.
- Stiehler F, et al. 2020. Helixer: cross-species gene annotation of large eukaryotic genomes using deep learning. *Bioinformatics* 36:5291-5298.
- Manni M, et al. 2021. BUSCO update. *Mol Biol Evol* 38:4647-4654.
- Weisman CM, et al. 2020. Many, but not all, lineage-specific genes can be explained by homology detection failure. *PLoS Biol* 18:e3000862.
- Palmer JM, Stajich J. 2020. Funannotate v1.8: eukaryotic genome annotation. Zenodo. doi:10.5281/zenodo.4054262.

## Related Skills

- repeat-annotation - PREREQUISITE: soft-mask repeats before prediction
- functional-annotation - Add GO/KEGG/Pfam to predicted proteins
- annotation-qc - BUSCO genome-vs-proteome, OMArk, gene-set sanity metrics
- ncrna-annotation - ncRNAs are not found by protein-coding prediction
- read-alignment/star-alignment - Splice-aware RNA-seq alignment for evidence
- genome-assembly/assembly-qc - Verify assembly quality and purge haplotigs before prediction
<!-- END FILE: genome-annotation/eukaryotic-gene-prediction/SKILL.md -->

## 子目录：genome-annotation/functional-annotation

<!-- BEGIN FILE: genome-annotation/functional-annotation/SKILL.md -->
---
name: bio-genome-annotation-functional-annotation
description: Assigns GO terms, Pfam/InterPro domains, KEGG orthologs, EC numbers, and product names to predicted proteins using eggNOG-mapper (orthology), InterProScan (domain signatures), and KofamScan (KEGG), routing specialized functions to dbCAN/antiSMASH/AMRFinderPlus/SignalP. Covers the orthology-vs-domain-vs-homology paradigms, the annotation-error percolation cascade, domain-presence-is-not-function, GO IEA circularity in enrichment, evidence tiering, and bit-score/coverage thresholds. Use when adding functional annotation to predicted genes, choosing between eggNOG-mapper and InterProScan, or judging how much to trust a functional label.
tool_type: cli
primary_tool: eggNOG-mapper
---

## Version Compatibility

Reference examples tested with: eggNOG-mapper 2.1.15 (pin for reproducibility), InterProScan 5.66+, KofamScan 1.3+, pandas 2.2+, AGAT 1.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

Annotation content tracks **database release**: record the eggNOG DB version, InterPro/Pfam release, and KEGG/KofamScan profile date, and note whether InterProScan used the EBI precalculated lookup service. eggNOG-mapper v3 is under testing (not production) - pin v2.1.15. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Functional Annotation

**"Functionally annotate my predicted proteins"** -> Transfer GO/KEGG/Pfam/EC/product labels from characterized proteins by orthology and domain signatures, attaching a confidence tier and provenance to each.
- CLI: `emapper.py -i proteins.faa --itype proteins -m diamond` (eggNOG-mapper), `interproscan.sh -i proteins.faa -f TSV,GFF3 -goterms -pa` (InterProScan)

## The Single Most Important Modern Insight -- Annotation Is a Propagated Hypothesis, Not a Measurement

Almost every label on a new genome is *transferred* by homology/orthology/ML from a small island of experimentally characterized proteins. The transfer chain is lossy and self-reinforcing - it behaves like a **percolation cascade** (Gilks 2002 *Bioinformatics* 18:1641): an over-specific name assigned in year 0, deposited with **no record that it was transferred**, becomes the nearest hit for the next genome, whose label becomes evidence for the next. By the time a query reaches NR, "number of hits agreeing" measures *how far an error spread*, not correctness. Schnoes 2009 (*PLoS Comput Biol* 5:e1000605) found misannotation reaching ~80% in bulk databases (TrEMBL/NR) and near-zero in curated Swiss-Prot - the gap *is* the curation. Three load-bearing consequences:

1. **The goal is not "maximally annotated" - it is "honestly tiered."** A genome that is 40% "hypothetical protein" with the rest correctly tiered by evidence is a better scientific object than one 95% named with half the names wrong. Prefer curated/orthology donors (Swiss-Prot, eggNOG OG consensus) over best-hits, and **demote specificity as identity/coverage fall** (full EC -> partial `1.1.1.-`; specific name -> superfamily; whole-protein -> per-domain). PI/reviewer pressure to "annotate everything" manufactures the next genome's percolating error.
2. **"Domain present" and "function known" are different claims.** A Pfam hit reports architecture, not activity - ~10% of the human kinome are catalytically dead pseudokinases that carry a confident "protein kinase" domain. Moonlighting (GAPDH), promiscuity, and mechanistically-diverse superfamilies (enolase, amidohydrolase, HAD, TIM-barrel: shared fold, divergent substrate) make this a first-order effect. **Fold conservation != function conservation** any more than sequence does - so structure-based transfer (Foldseek) inherits the same trap with *higher* false confidence.
3. **Record provenance on every label** (method, donor, donor evidence code, identity/coverage/bitscore, DB version). That is the only thing that stops the provenance-amnesia step that turns a transfer into a "fact."

## Tool Taxonomy

| Paradigm | Tool | Mechanism | Failure mode |
|----------|------|-----------|--------------|
| Orthology | eggNOG-mapper | seed-ortholog -> orthologous group -> consensus transfer | tax-scope sensitive; HGT/xenologs break the orthology assumption |
| Domain/signature | InterProScan | profile HMMs/matrices -> integrated InterPro entries | a domain implies a capability, not the substrate; broad families uninformative |
| KEGG ortholog | KofamScan | per-KO HMMs + adaptive thresholds | KO assignment, not pathway proof |
| Homology best-hit | DIAMOND vs Swiss-Prot | top-hit similarity, transfer label | best-hit != ortholog; transitive error propagation |
| ML / structure | DeepGO, DeepFRI, Foldseek | learned sequence/structure -> GO | low precision; ontology terms not products; reaches twilight zone only |

**Default workhorse pair:** eggNOG-mapper + InterProScan (orthogonal evidence: orthology vs signatures), reconciled afterward. Add KofamScan if KEGG pathway reconstruction is the goal (its adaptive per-KO thresholds are stricter than eggNOG's `KEGG_ko`). DIAMOND-vs-Swiss-Prot is the cheap product-name layer; never use it alone for GO.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Bacterial isolate | Bakta/PGAP product names + eggNOG-mapper + InterProScan | structural pipeline first, then orthology + domains |
| Eukaryotic proteome | InterProScan (domains+GO+pathways) + eggNOG-mapper | orthogonal evidence, reconcile |
| Metagenome / MAG | eggNOG-mapper `--itype metagenome` (+ KofamScan, dbCAN) | built-in gene calling; KEGG modules |
| Twilight-zone / ORFan (no homolog) | ML (DeepGOPlus) or structure (ESMFold -> Foldseek -> DeepFRI) | only handle on the homology-free fraction; low-confidence leads |
| CAZymes / BGCs / AMR / signal peptides | -> dbCAN / antiSMASH / AMRFinderPlus / SignalP6 | a generic Pfam hit gives no substrate/phenotype/cluster |
| GO enrichment downstream | -> pathway-analysis/go-enrichment (mind IEA circularity) | enrichment on IEA partly tests the pipeline against itself |

## eggNOG-mapper

```bash
download_eggnog_data.py --data_dir db/ -y               # ~44 GB (DIAMOND DB installed by default; -D skips it)
emapper.py -i proteins.faa --itype proteins -m diamond \
    --tax_scope auto --data_dir db/ --cpu 16 -o annot --output_dir out/
```

Three stages: (1) **seed-ortholog search** (DIAMOND/MMseqs2/HMMER) anchors the query - this is a best-hit and is *not* the annotation; (2) **orthology assignment** retrieves the seed's fine-grained orthologs within the chosen taxonomic scope; (3) **functional transfer** pools terms across the *set of orthologs* (which damps single-entry misannotation - this is why eggNOG-mapper beats raw DIAMOND-vs-NR). `--tax_scope` is **the single most consequential parameter**: too broad gathers distant orthologs and over-generalizes function; `auto` lets each seed take its most-informative phylogenetic ceiling. `--itype {proteins,CDS,genome,metagenome}` (genome/metagenome runs Prodigal first). Output `.emapper.annotations` columns include `seed_ortholog`, `eggNOG_OGs`, `COG_category`, `Description`, `Preferred_name`, `GOs`, `EC`, `KEGG_ko`, `PFAMs` (read the actual header; `-` = empty).

## InterProScan

```bash
interproscan.sh -i proteins.faa -f TSV,GFF3 -goterms -pa -cpu 16
```

Runs member-database scanners (Pfam, PANTHER, NCBIfam, SUPERFAMILY, CDD, SMART, Gene3D, Hamap, PROSITE, ...) and **integrates overlapping signatures into InterPro entries** (stable IPRxxxxxx, with a type: Family/Domain/Repeat/Site/Homologous Superfamily). **Report at the InterPro-entry level** - it is the consensus that survives one member DB being wrong. `-goterms` adds the interpro2go mapping (these GO are IEA/electronic); `-pa` maps Reactome/MetaCyc. By default it queries the EBI precalculated lookup service (fast, MD5-keyed); `-dp` forces local compute (novel/confidential sequences, reproducibility). Java 11+ and a tens-of-GB data bundle required; for millions of proteins, chunk the FASTA into array jobs.

## Reconciling Multi-Tool Output with Python

**Goal:** Merge eggNOG and InterProScan per protein while preserving provenance, so a curated name is never silently overwritten by a generic domain.

**Approach:** Parse each tool's table, keep source namespaces separate, union GO with source tags, and prefer the orthology `Preferred_name`/`Description` for the human-readable product.

```python
import pandas as pd

def parse_eggnog(path):
    df = pd.read_csv(path, sep='\t', comment='#', header=None)
    cols = ['query', 'seed_ortholog', 'evalue', 'score', 'eggNOG_OGs', 'max_annot_lvl',
            'COG_category', 'Description', 'Preferred_name', 'GOs', 'EC', 'KEGG_ko']
    df.columns = (cols + [f'c{i}' for i in range(len(df.columns) - len(cols))])[:len(df.columns)]
    return df

def best_product_name(row):
    name = row.get('Preferred_name', '-')
    return name if name not in ('-', '', None) else 'hypothetical protein'   # honest default, not a forced guess
```

Use AGAT (`agat_sp_manage_functional_annotation.pl`) to graft BLAST/InterProScan results onto a GFF3 (it handles the spec edge cases). For GO deliverables use GAF (carries the evidence code); keep each tool in its own `Dbxref` namespace.

## Ontology Rigor and the IEA Circularity

- **GO MF vs BP transfer with different reliability.** Molecular Function ("DNA helicase activity") is local/chemical and transfers with the fold; Biological Process ("DNA replication") is systemic context and does *not* transfer reliably - CAFA confirmed BLAST beats naive baselines for MF but not BP (Radivojac 2013 *Nat Methods* 10:221). Weight MF over BP when evidence is limited; never let a transferred BP term drive a conclusion alone.
- **Essentially all genome-derived GO is IEA** (Inferred from Electronic Annotation, never curator-reviewed). Running GO enrichment on IEA against an IEA background **partly tests the pipeline against itself** - if interpro2go maps a common domain to a term, every genome with that domain looks "enriched." Compounded by annotation bias (58% of human GO covers 16% of genes; Haynes 2018 *Sci Rep* 8:1362) and True-Path-Rule inflation of shallow terms. Pin versions, match background to foreground pipeline, prefer non-IEA where it exists, and state that the result is annotation-derived.
- **EC numbers are not stable.** Deleted/transferred numbers are tombstones (never reused); a partial EC `1.1.1.-` is a valid statement of ignorance (the EC equivalent of "hypothetical"). Demand orthology or a curated rule before asserting a full four-level EC.
- **KEGG bulk access is paywalled.** Free routes: KofamScan/KofamKOALA (local HMMs + adaptive per-KO thresholds; an `*` marks above-threshold hits) or eggNOG's `KEGG_ko`. A "complete module" is a reconstruction (a gap can be non-orthologous gene displacement; a filled step can be a paralog doing something else), not proof of flux.

## Per-Method Failure Modes

### Best-hit-as-ortholog
**Trigger:** transferring a specific function from one DIAMOND/BLAST top hit (esp. TrEMBL/NR). **Mechanism:** best-hit != ortholog; the bulk-DB hit is likely itself an auto-annotation. **Symptom:** confident specific names with no provenance. **Fix:** orthology consensus + Swiss-Prot donors.

### Over-specific transfer
**Trigger:** copying the exact substrate/EC of a characterized homolog onto a distant relative. **Mechanism:** mechanistically-diverse superfamilies share fold, not substrate. **Symptom:** a "muconate cycloisomerase" that does something else. **Fix:** demote to superfamily / partial EC as identity and coverage fall.

### Wrong eggNOG tax_scope
**Trigger:** leaving scope too broad/narrow or unpinned. **Mechanism:** distant orthologs over-generalize, or no informative orthologs. **Symptom:** vague or missing function. **Fix:** `auto`, or pin the known clade.

### Circular GO enrichment
**Trigger:** enriching IEA annotations against a mismatched background. **Mechanism:** measures the mapping table and study popularity, not biology. **Symptom:** "enriched" for whatever well-studied genes are annotated for. **Fix:** non-IEA where possible; matched background; pin versions; caveat the result.

### Reading specialized function from a generic hit
**Trigger:** inferring CAZyme substrate / AMR phenotype / BGC product from a plain Pfam domain. **Mechanism:** the substrate/phenotype/cluster signal is not in a generic domain. **Symptom:** wrong substrate or phenotype call. **Fix:** route to dbCAN / AMRFinderPlus / antiSMASH.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Reason in bits-per-residue, not raw e-value | alignment statistics | e-value scales with DB size (a database-size artifact); bits/residue is density |
| Bidirectional coverage ≥50-70% query and subject | transfer practice | one-domain coverage justifies only a domain-level claim |
| ~40% identity over full length (well-behaved families only) | soft floor | no safe identity in mechanistically-diverse superfamilies; demote specificity instead |
| Named fraction "too high for the taxon" (>90% on a novel isolate) | over-annotation smell test | loose thresholds manufacturing names; expect 20-50% hypothetical |
| eggNOG `--tax_scope auto` | eggNOG-mapper | per-seed informative ceiling |
| KofamScan adaptive per-KO threshold (`*`) | Aramaki 2020 | a single global e-value misfires across KO families |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Low annotation rate | fragmented ORFs / narrow scope | check protein quality; `--tax_scope auto`; run both tools and merge |
| Specific name on a distant homolog | over-specific transfer | demote to superfamily / partial EC; record identity |
| eggNOG DB errors | DB/version mismatch | re-download; pin emapper 2.1.15 |
| InterProScan memory/time | full proteome at once | chunk FASTA; keep lookup service on; drop PANTHER/Gene3D if not needed |
| Enrichment "too clean" | IEA circularity / study bias | matched background; pin GO release; caveat |
| Multidomain protein mislabeled | named by first/best domain | report all domains with coordinates |

## References

- Cantalapiedra CP, et al. 2021. eggNOG-mapper v2: functional annotation, orthology assignments, and domain prediction at the metagenomic scale. *Mol Biol Evol* 38:5825-5829.
- Huerta-Cepas J, et al. 2019. eggNOG 5.0: a hierarchical, functionally and phylogenetically annotated orthology resource. *Nucleic Acids Res* 47:D309-D314.
- Jones P, et al. 2014. InterProScan 5: genome-scale protein function classification. *Bioinformatics* 30:1236-1240.
- Blum M, et al. 2025. InterPro: the protein sequence classification resource in 2025. *Nucleic Acids Res* 53:D444-D456.
- Schnoes AM, et al. 2009. Annotation error in public databases: misannotation of molecular function in enzyme superfamilies. *PLoS Comput Biol* 5:e1000605.
- Gilks WR, et al. 2002. Modeling the percolation of annotation errors in a database of protein sequences. *Bioinformatics* 18:1641-1649.
- Aramaki T, et al. 2020. KofamKOALA: KEGG ortholog assignment based on profile HMM and adaptive score threshold. *Bioinformatics* 36:2251-2252.
- Zheng J, et al. 2023. dbCAN3: automated carbohydrate-active enzyme and substrate annotation. *Nucleic Acids Res* 51:W115-W121.
- Teufel F, et al. 2022. SignalP 6.0 predicts all five types of signal peptides using protein language models. *Nat Biotechnol* 40:1023-1025.
- Feldgarden M, et al. 2021. AMRFinderPlus and the Reference Gene Catalog facilitate examination of the genomic links among antimicrobial resistance, stress response, and virulence. *Sci Rep* 11:12728.
- Blin K, et al. 2023. antiSMASH 7.0: new and improved predictions for detection, regulation, chemical structures and visualisation. *Nucleic Acids Res* 51:W46-W50.
- Radivojac P, et al. 2013. A large-scale evaluation of computational protein function prediction (CAFA). *Nat Methods* 10:221-227.
- Haynes WA, et al. 2018. Gene annotation bias impedes biomedical research. *Sci Rep* 8:1362.

## Related Skills

- prokaryotic-annotation - Bakta/PGAP product names + locus tags before functional layers
- eukaryotic-gene-prediction - Produces the protein FASTA to annotate
- annotation-qc - Annotation-coverage and hypothetical-fraction sanity
- pathway-analysis/go-enrichment - Enrichment using GO annotations (mind IEA circularity)
- pathway-analysis/kegg-pathways - Pathway mapping with KEGG orthologs
- epidemiological-genomics/amr-surveillance - AMRFinderPlus/CARD for resistance genes and point mutations
<!-- END FILE: genome-annotation/functional-annotation/SKILL.md -->

## 子目录：genome-annotation/ncrna-annotation

<!-- BEGIN FILE: genome-annotation/ncrna-annotation/SKILL.md -->
---
name: bio-genome-annotation-ncrna-annotation
description: Identifies non-coding RNAs (tRNA, rRNA, snoRNA, snRNA, riboswitches, sRNAs) using Infernal covariance-model search against Rfam, tRNAscan-SE 2.0 for tRNA, barrnap for rRNA, and ARAGORN for tmRNA, plus the small-RNA-seq boundary for miRNA and the transcript-assembly boundary for lncRNA. Covers the structure-conserved-not-sequence-conserved principle (why BLAST fails), GA-threshold and clan-competition correctness, tRNAscan-SE domain modes and pseudogene flags, rDNA copy-number collapse, and why homology annotation is a recall floor. Use when performing genome-wide ncRNA annotation, choosing the right tool for an RNA class, or interpreting ncRNA counts.
tool_type: cli
primary_tool: Infernal
---

## Version Compatibility

Reference examples tested with: Infernal 1.1.4+, Rfam 15+ (CM library), tRNAscan-SE 2.0.12+, barrnap 0.9+, ARAGORN 1.2+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

The **Rfam release version** drives results (Rfam 15 has ~4,200+ families); record it. The downloaded `Rfam.cm` ships pre-calibrated, so only `cmpress` is needed before `cmscan`. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Non-Coding RNA Annotation

**"Find non-coding RNAs in my genome"** -> Scan an assembly for structured ncRNA families using covariance models (sequence + secondary structure jointly), with specialist detectors for tRNA and the expression boundary for miRNA/lncRNA.
- CLI: `cmscan --cut_ga --rfam --nohmmonly --fmt 2 --clanin Rfam.clanin Rfam.cm genome.fa` (Infernal), `tRNAscan-SE -B genome.fa`

## The Single Most Important Modern Insight -- ncRNA Homology Is Structure-Conserved, Not Sequence-Conserved

Protein annotation rides on sequence/ORF signal; structured-ncRNA annotation rides on **base-pairing covariation**. A G-C pair can become A-U across evolution while the *structure* is preserved - both positions mutate together (compensatory substitution). To a sequence-only tool these look like two mismatches; to a covariance model (a profile SCFG, the Rfam/Infernal engine) the *correlated* change is the strongest possible evidence of homology. Three consequences:

1. **BLAST is categorically the wrong tool for structured ncRNA.** Two RNase P RNAs may share <60% identity (BLAST sees noise) yet have unmistakable shared structure. Use Infernal covariance models, not BLAST. R-scape (Rivas 2017 *Nat Methods* 14:45) is the statistical test for whether a structure is *actually* conserved - it found no significant covariation support for the proposed structures of HOTAIR, SRA, and Xist-RepA.
2. **A homology-based annotation is a recall floor, never a count.** A CM can only exist for a family whose structure is conserved across enough divergent sequences to seed a model - so fast-evolving and lineage-specific ncRNAs are invisible *by design*, and the floor drops further for organisms far from the curation spotlight. Report "at least N conserved-family loci," never "the genome has N ncRNAs."
3. **Whole classes need expression evidence, not genomic search.** miRNAs are hypotheses until small-RNA-seq confirms the Dicer processing signature; lncRNAs are not annotatable by homology at all (no conserved structure) - they are transcript catalogs. Use specialist tools where the biology has a sharper signal (tRNAscan-SE, miRDeep2-with-reads).

## Tool Taxonomy

| RNA class | Tool | Citation | Method |
|-----------|------|----------|--------|
| tRNA | tRNAscan-SE 2.0 | Chan 2021 *NAR* | isotype-specific Infernal CMs + pseudogene/high-confidence logic |
| rRNA (fast) | barrnap | Seemann (software) | nhmmer HMM profiles; kingdom flag; prokaryotic-pipeline default |
| rRNA (structure-aware) | Infernal + Rfam SSU/LSU | Nawrocki 2013 | CM; better boundaries / unusual taxa |
| tmRNA (+ bacterial tRNA) | ARAGORN | Laslett 2004 | heuristic cloverleaf + tmRNA models |
| miRNA | miRDeep2 (+ small-RNA-seq) | Friedländer 2012 | Dicer-processing model on read pileups |
| C/D, H/ACA snoRNA | snoscan / snoReport | Lowe 1999 | guide-target complementarity / SVM |
| Everything else structured | Infernal `cmscan` vs Rfam | Nawrocki 2013 | covariance models; the general engine |
| lncRNA | StringTie + CPC2/CPAT/FEELnc | - | transcript assembly + coding-potential, NOT CM search |

RNAmmer is the legacy rRNA tool (license-encumbered, HMMER2) - use barrnap instead unless reproducing old annotations.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Prokaryote, fast complete annotation | barrnap + tRNAscan-SE `-B`/ARAGORN + Infernal/Rfam | what Bakta/Prokka/PGAP wrap |
| tRNA is the question | always tRNAscan-SE 2.0 (not Rfam's generic tRNA model) | isotype, pseudogene, intron, high-confidence logic |
| rRNA, speed matters | barrnap | seconds per genome |
| Broad ncRNA sweep of a new genome | Infernal `cmscan` vs full Rfam.cm (GA + clan competition) | structure-aware, family-typed |
| miRNA | demand small-RNA-seq; miRDeep2 | genomic hairpin prediction is unreliable |
| lncRNA | transcript assembly + coding-potential | not structurally conserved; no CM |
| Claim a conserved structure | R-scape covariation test (report power) | thermodynamic fold != selected structure |
| Bacterial AMR/CRISPR arrays | -> prokaryotic-annotation / CRISPRCasFinder | array detection is a separate tool class |

## Infernal / cmscan (the General ncRNA Engine)

```bash
# Rfam ships pre-calibrated; press it once, then scan (cmscan = many models vs one genome)
cmpress Rfam.cm
cmscan -Z <dbsize_Mb> --cut_ga --rfam --nohmmonly \
       --tblout out.tblout --fmt 2 --clanin Rfam.clanin \
       Rfam.cm genome.fa > out.cmscan
grep -v " = " out.tblout > out.deoverlapped.tblout   # drop within-clan overlaps
```

- `--cut_ga` (gathering threshold): the single most important correctness flag. Each family has a curator-set, per-family bit-score threshold; a fixed E-value would treat a 70-nt tRNA model and a 2,900-nt LSU model identically, which is wrong. **Overriding GA to "find more" imports the false positives the curator deliberately excluded.**
- `--nohmmonly` forces full CM (structure-aware) scoring so scores are GA-comparable.
- `-Z <dbsize_Mb>` = total_residues x 2 / 1e6 (both strands), making E-values run-comparable.
- `--fmt 2 --clanin Rfam.clanin` + the `grep -v " = "` deoverlap step is **mandatory, not a nicety**: clans group related families (the tRNA models, SSU/LSU rRNA), so one locus hits several models and the raw table double-counts (a 16S locus becomes "several rRNA genes").

## tRNAscan-SE 2.0

```bash
tRNAscan-SE -B -o trna.out -f trna.ss -m trna.stats --gff trna.gff3 genome.fa   # bacterial
```

Modes: `-E` eukaryotic (default), `-B` bacterial, `-A` archaeal, `-G` general (mixed/metagenome), `-M mammal`/`-M vert` mitochondrial, `-O` organellar (disables pseudogene checking). **Domain choice is not cosmetic** - the wrong mode mis-scores and miscalls isotypes; there is no auto-detect. Report the **high-confidence set**, not raw hits (raw counts include pseudogenes/SINEs and can be 2-10x inflated in eukaryotes). The pseudogene flag is reliable in eukaryotic nuclear genomes but false-positive-prone in organelles/odd mito-tRNAs (truncated arms read as "decayed") - hence `-O`/`-D`.

## barrnap (rRNA)

```bash
barrnap --kingdom bac genome.fa > rrna.gff3   # bac | arc | euk | mito
```

Reports partial rRNA at contig edges as `(partial)`. **rDNA copy number from an assembly is essentially always wrong** - near-identical rRNA arrays collapse in short-read assemblies, so the annotated count is a floor (off by orders of magnitude in eukaryotes); use long reads or read depth for true copy number.

## Parsing and Combining ncRNA Calls with Python

**Goal:** Merge Infernal and tRNAscan-SE into one ncRNA annotation, preferring the specialist for tRNA.

**Approach:** Parse the deoverlapped Infernal table, drop its tRNA rows (tRNAscan-SE is the authority for tRNA), and combine with the tRNAscan-SE high-confidence set; keep evidence provenance per class.

```python
import pandas as pd

def parse_infernal_tbl(tbl_file):
    rows = []
    with open(tbl_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            p = line.split()
            if len(p) < 18:
                continue
            rows.append({'rfam_name': p[1], 'seqid': p[3], 'strand': p[11],
                         'score': float(p[16]), 'evalue': float(p[17])})
    df = pd.DataFrame(rows)
    return df[~df['rfam_name'].str.contains('tRNA', case=False, na=False)]   # tRNAscan-SE owns tRNA
```

## The miRNA Disaster and lncRNA Non-Annotatability

- **Most computationally predicted miRNAs are false positives, and much of miRBase is contaminated.** Any genome folds into astronomically many hairpins; foldability is not evidence of a miRNA. The discriminating signal - a precise homogeneous 5' end, a detectable star strand, a ~22 nt mode - is visible only in small-RNA-seq read pileups (miRDeep2 scores this geometry). Fromm 2015 found <1/3 of human and ~16% of metazoan miRBase entries are bona fide; closely related species differing by >1,000 miRNAs in miRBase is annotation noise, not biology. Animal-trained tools mis-call **plant** miRNAs (DCL1 biogenesis, 21/24 nt) - use plant-specific tools. Report homology-only hits as "miRNA candidates," never genes.
- **lncRNAs are not annotatable by homology in principle** - no conserved structure (R-scape), poor sequence conservation. "lncRNA annotation" is transcript cataloguing (assemble RNA-seq, subtract coding potential), inheriting every transcript-assembly pathology, so catalog size tracks sequencing depth and filter policy. The same human genome "has" ~16,000 to >100,000 lncRNAs depending only on the annotation source (RefSeq vs GENCODE vs NONCODE) - these encode different answers to the transcription-vs-selection function debate (Graur 2013), not different biology. Never quote a bare lncRNA count without source + version.

## Per-Method Failure Modes

### BLAST for structured ncRNA
**Trigger:** using BLAST to find ncRNA homologs. **Mechanism:** BLAST scores sequence identity, blind to covariation. **Symptom:** misses structure-conserved homologs; ranks pseudogenes above real homologs. **Fix:** Infernal/Rfam covariance models.

### Missing GA / clan competition
**Trigger:** `cmscan` without `--cut_ga`/`--nohmmonly`, or without `--clanin`/`--fmt 2` deoverlap. **Mechanism:** wrong thresholds; HMM-only scores not GA-comparable; within-clan overlaps uncollapsed. **Symptom:** inflated/redundant family calls (one locus counted several times). **Fix:** the full canonical command + `grep -v " = "`.

### Wrong tRNAscan-SE domain mode
**Trigger:** `-E` on a bacterium, or default on a metagenome. **Mechanism:** domain CMs differ; no auto-detect. **Symptom:** mis-scored/miscalled isotypes. **Fix:** `-B`/`-A`/`-G` per source; report the high-confidence set.

### Counting raw tRNA/rRNA hits
**Trigger:** reporting raw tRNAscan-SE hits or genomic rRNA as copy number. **Mechanism:** SINEs/pseudogenes/NUMTs inflate tRNA; rDNA arrays collapse. **Symptom:** 150+ bacterial "tRNAs"; "5 copies of 18S". **Fix:** high-confidence set; treat copy numbers as floors; flag NUMT-type organellar tRNAs in the nucleus.

### miRNA/lncRNA from genome alone
**Trigger:** calling miRNAs from hairpins or lncRNAs from CM search. **Mechanism:** no genomic signal suffices. **Symptom:** false-positive "genes". **Fix:** small-RNA-seq (miRNA); transcript assembly + coding-potential (lncRNA); label homology-only as candidates.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `--cut_ga` per-family GA threshold | Rfam curation | family-specific noise floor; never override genome-wide |
| `-Z` = residues x 2 / 1e6 | Infernal | run-comparable E-values (both strands) |
| Bacterial tRNA ~28-90 (E. coli ~89; symbionts ~28-35) | GtRNAdb | 150+ implies fragments/pseudogenes |
| Eukaryotic tRNA ~170-570 (amplified) | tRNA literature | raw hits far higher (SINEs/pseudogenes); use high-confidence set |
| Bacterial rRNA operons 1-15 (E. coli ~7) | copy-number norm | annotated count is a floor (rDNA collapse) |
| miRNA needs small-RNA-seq Dicer signature | Fromm 2015 | foldability is not a miRNA; >1/3 miRBase is artifact |
| R-scape covariation + power before claiming structure | Rivas 2017/2020 | thermodynamic fold != selected structure |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| cmscan slow | full Rfam scan | `--rfam` preset; split genome; parallelize |
| Redundant overlapping calls | no clan competition | `--fmt 2 --clanin`; `grep -v " = "` |
| Missing expected ncRNAs | stale Rfam / cmpress not run | check Rfam version; verify `.i1{f,i,m,p}` files |
| Too many tRNA "pseudogenes" | normal in eukaryotes; false-positive in organelles | high-confidence set; `-O`/`-D` for organelles |
| Implausible rRNA copy number | rDNA array collapse | report as floor; use read depth/long reads |
| Two species differ by 1000s of miRNAs | miRBase contamination | use MirGeneDB; demand processing evidence |

## References

- Nawrocki EP, Eddy SR. 2013. Infernal 1.1: 100-fold faster RNA homology searches. *Bioinformatics* 29:2933-2935.
- Ontiveros-Palacios N, et al. 2025. Rfam 15: RNA families database in 2025. *Nucleic Acids Res* 53:D258-D267.
- Chan PP, et al. 2021. tRNAscan-SE 2.0: improved detection and functional classification of transfer RNA genes. *Nucleic Acids Res* 49:9077-9096.
- Lowe TM, Eddy SR. 1997. tRNAscan-SE: a program for improved detection of transfer RNA genes in genomic sequence. *Nucleic Acids Res* 25:955-964.
- Laslett D, Canback B. 2004. ARAGORN, a program to detect tRNA genes and tmRNA genes in nucleotide sequences. *Nucleic Acids Res* 32:11-16.
- Lagesen K, et al. 2007. RNAmmer: consistent and rapid annotation of ribosomal RNA genes. *Nucleic Acids Res* 35:3100-3108.
- Friedländer MR, et al. 2012. miRDeep2 accurately identifies known and hundreds of novel microRNA genes in seven animal clades. *Nucleic Acids Res* 40:37-52.
- Lowe TM, Eddy SR. 1999. A computational screen for methylation guide snoRNAs in yeast (snoscan). *Science* 283:1168-1171.
- Fromm B, et al. 2015. A uniform system for the annotation of vertebrate microRNA genes and the evolution of the human microRNAome (MirGeneDB). *Annu Rev Genet* 49:213-242.
- Rivas E, Clements J, Eddy SR. 2017. A statistical test for conserved RNA structure shows lack of evidence for structure in lncRNAs (R-scape). *Nat Methods* 14:45-48.
- Graur D, et al. 2013. On the immortality of television sets: "function" in the human genome according to the evolution-free gospel of ENCODE. *Genome Biol Evol* 5:578-590.

## Related Skills

- prokaryotic-annotation - Bakta/Prokka wrap barrnap + tRNAscan-SE + Infernal for prokaryotic ncRNA
- eukaryotic-gene-prediction - Protein-coding prediction does not find ncRNAs
- annotation-qc - tRNA/rRNA count sanity in the annotation QC panel
- rna-structure/ncrna-search - Targeted covariance-model homology searches
- rna-structure/secondary-structure-prediction - Fold and visualize an annotated ncRNA
<!-- END FILE: genome-annotation/ncrna-annotation/SKILL.md -->

## 子目录：genome-annotation/prokaryotic-annotation

<!-- BEGIN FILE: genome-annotation/prokaryotic-annotation/SKILL.md -->
---
name: bio-genome-annotation-prokaryotic-annotation
description: Annotates bacterial and archaeal genomes (isolates, MAGs, plasmids) with Bakta (active versioned databases, NCBI-compliant output) or Prokka (legacy), producing GFF3/GenBank/EMBL/FASTA with INSDC locus tags. Covers Bakta-vs-Prokka-vs-PGAP-vs-DFAST choice, light-vs-full database tiers, translation-table selection (11/4/25), archaeal and leaderless-gene caveats, the small-ORF blind spot, pseudogene-vs-phase-variation, the pangenome re-annotation trap, and submission compliance. Use when annotating a newly assembled prokaryotic genome, choosing an annotation tool, re-annotating a collection for pangenomics, or preparing annotations for NCBI/DDBJ submission.
tool_type: cli
primary_tool: Bakta
---

## Version Compatibility

Reference examples tested with: Bakta 1.9+, Prokka 1.14.6 (legacy), tRNAscan-SE 2.0+, CheckM2 1.0+, gffutils 0.12+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

Annotation content tracks the **database version**, not just the binary: a Bakta full DB (schema v5+, ~30 GB zipped) and a Bakta light DB give different functional calls, and two runs months apart can differ purely from DB updates. Record the Bakta DB version in methods. Prokka's bundled databases are frozen (~2019-2021). If code throws an error, introspect the installed tool and adapt rather than retrying.

# Prokaryotic Genome Annotation

**"Annotate my bacterial genome"** -> Call protein-coding genes, tRNAs/rRNAs/ncRNAs, and other features, then assign function by database identity, and emit submission-ready files.
- CLI: `bakta --db db/ assembly.fa` (default), `prokka --outdir out assembly.fa` (legacy), NCBI PGAP (submission/RefSeq-grade)

## The Single Most Important Modern Insight -- Gene Calling Is Near-Solved; Function Is Not, and Wrong Labels Propagate

For a typical isolate, Prodigal/Pyrodigal recovers >95-99% of true coding genes. The unsolved problems are the **start codon** (translation initiation site), the **small/overlapping/recoded ORFs**, and above all the **function**. Three consequences a postdoc must internalize:

1. **A confidently wrong product name is worse than "hypothetical protein."** Names assigned by loose homology transfer across distant lineages and *self-amplify* through databases - there is no mechanism to retract a correction once it spreads, so annotation accuracy has gone *down*, not up, as sequencing scaled (Salzberg 2019 *Genome Biol* 20:92). Bakta's design counters this: gene-level identity only via exact (MD5/UniRef100) match, falling back to cluster level, then "hypothetical" rather than guessing. 25-50% hypothetical is healthy for a non-model organism; near 0% means over-confident transfer.

2. **Comparing gene counts across tools/versions/DBs is invalid.** Tool agreement is "highly dependent on the organism of study" and biased toward model organisms (Dimonaco 2022 *Bioinformatics* 38:1198) - there is no universal best tool. Differences between two annotations are mostly tool artifacts, not biology. For any collection (pangenomics), **re-annotate every assembly from FASTA with one pipeline + one pinned DB**; merging published annotations inflates the accessory genome ~10× (Tonkin-Hill 2020 *Genome Biol* 21:180).

3. **Annotation completeness ≠ assembly completeness.** A fragmented/contaminated assembly produces truncated partial CDS at every contig break, inflated counts, and missing rRNA operons. Run CheckM2 *before* trusting any annotation QC number.

## Tool Taxonomy

| Tool | Maintained | Database approach | Output | When |
|------|-----------|-------------------|--------|------|
| Bakta | Yes (active) | Curated, **versioned**, alignment-free (UniRef + AMRFinderPlus + expert systems) | GFF3/GBFF/EMBL/FASTA/TSV/JSON + plot | **Default for new work**; reproducible, MAG-aware |
| Prokka | Frozen ~2021 | BLAST hierarchy vs frozen UniProt/RefSeq + HMM | GFF3/GBK/FAA + tbl | Legacy only; pangenome pipelines (Roary) expect Prokka GFF |
| NCBI PGAP | Yes (NCBI) | RefSeq protein-family models + ProSplign | ASN.1/GenBank, submission-ready | **GenBank/RefSeq submission**; best pseudogene/frameshift/selenoprotein handling |
| DFAST | Yes (DDBJ) | DFAST reference DBs + swappable refs | INSDC files | DDBJ submission; fast, flexible reference swap |
| RAST / BV-BRC | Yes | SEED subsystems | GenBank/GFF + subsystems | Subsystem/metabolic framing; web; not for direct INSDC submission |

Prokka uses Aragorn (tRNA) + barrnap (rRNA); Bakta uses tRNAscan-SE 2.0 (tRNA, domain-specific) + Infernal/Rfam (rRNA/ncRNA) + PILER-CR (CRISPR arrays) + DeepSig (signal peptides). Bakta is deliberately conservative on naming, so it reports "hypothetical" where Prokka confidently (sometimes wrongly) names a gene - Bakta looking "less annotated" is it being honest.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Routine isolate, reproducible | Bakta, full DB | standardized, versioned, current functional calls |
| Submitting to GenBank/RefSeq | PGAP | RefSeq re-annotates with PGAP regardless; best pseudogene handling |
| Submitting to DDBJ | DFAST | INSDC-ready, DDBJ-aligned |
| MAG / metagenome bin | Bakta `--meta` + CheckM2 gate | anonymous-mode calling; QC before trust |
| Mycoplasma / Mollicutes | Bakta `--translation-table 4` | UGA=Trp; table 11 splits genes at every UGA |
| Archaeon | Bakta + verify tRNAscan-SE archaeal model; PGAP if N-termini matter | leaderless mRNAs degrade Prodigal TIS |
| Inherited Prokka pangenome pipeline | pin Prokka version, or re-call all in Bakta | tool consistency vs current biology |
| Subsystem/metabolic view | RAST / BV-BRC | SEED subsystem categories |
| Genome not yet assembled / poor QC | -> genome-assembly/assembly-qc | fix assembly before annotating |
| AMR for clinical report | -> run AMRFinderPlus/CARD-RGI directly | `--organism` context, point mutations, partials matter |

## Bakta (Default)

```bash
# Database (record the version): full ~30 GB for publishable annotation; light for triage/CI
bakta_db download --output db/ --type full

bakta --db db/ --output bakta_out --prefix ecoli_k12 \
    --genus Escherichia --species coli --strain K-12 \
    --locus-tag ECK12 --gram - --complete --threads 16 \
    assembly.fasta
```

Key flags: `--translation-table {11,4,25}` (default 11), `--gram {+,-,?}` (gates DeepSig signal-peptide calls; default `?`), `--complete` (all sequences are finished replicons; enables oriC detection - do NOT use on draft contigs), `--meta` (metagenome/MAG mode), `--compliant` (enforce INSDC structure), `--keep-contig-headers`, `--proteins <faa>` (trusted-protein transfer). Set `--genus`/`--species` from a GTDB-Tk classification, not a guess. Primary outputs: `.gff3`, `.gbff`, `.faa`, `.ffn`, `.fna`, `.tsv`, plus `.hypotheticals.tsv` and `.inference.tsv` (open the inference column to ask *why* a product was assigned).

## Prokka (Legacy)

```bash
prokka --outdir prokka_out --prefix my_genome --locustag MYORG \
    --genus Escherichia --species coli --cpus 8 --rfam assembly.fasta
```

Use only for tool-chain consistency with an existing Prokka-based pangenome workflow, and pin the version. Its bundled databases are frozen: a gene family characterized after ~2019 is "hypothetical" in Prokka but named by current Bakta/PGAP, so the *same gene* flips core/accessory purely on DB vintage.

## Coding Density and CDS Extraction with Python

**Goal:** Load Bakta/Prokka GFF3 into a queryable database and compute coding density, the first sanity number.

**Approach:** Build a gffutils database, sum CDS lengths, divide by genome length; flag values outside the expected band.

```python
import gffutils

CODING_DENSITY_LOW = 0.85   # <0.85 in a free-living bacterium suggests wrong table, fragmentation, or heavy pseudogenization
CODING_DENSITY_HIGH = 0.93  # >0.93 suggests ORF over-calling (spurious short hypotheticals)

def coding_density(gff_file, genome_length):
    db = gffutils.create_db(gff_file, ':memory:', merge_strategy='merge')
    coding_bp = sum(c.end - c.start + 1 for c in db.features_of_type('CDS'))
    density = coding_bp / genome_length
    if density < CODING_DENSITY_LOW or density > CODING_DENSITY_HIGH:
        print(f'WARNING: coding density {density:.1%} outside expected 85-93%')
    return density
```

## Hard Cases the Caller Gets Wrong

- **Wrong genetic code is silent and looks like fragmentation.** A Mycoplasma run under table 11 yields anomalously low coding density + many short "hypothetical" fragments because every internal UGA split a gene. Confirm the table from taxonomy (GTDB-Tk), never a guess. Table 4 (UGA=Trp, Mollicutes), table 25 (UGA=Gly, Gracilibacteria/SR1).
- **Pseudogene over-calling in reductive genomes is real biology.** *Mycobacterium leprae* has ~1,116 pseudogenes vs ~1,604 intact CDS (Cole 2001 *Nature* 409:1007) - high pseudogene fraction in a symbiont/host-restricted pathogen (*Rickettsia*, *Sodalis*) is a lifestyle signal, not a defect. PGAP (ProSplign aligns *through* frameshifts, emits `/pseudo`) is the best automated arbiter.
- **Phase variation is not a pseudogene.** A frameshift inside a homopolymer/SSR tract in a contingency locus (*Neisseria* ~65 candidate loci, *Haemophilus*, *Campylobacter* poly-G tracts) means the assembled cell was in the OFF phase - do NOT "correct" or polish it away. This confounds with ONT homopolymer indel error: a pseudogene spike is ambiguous between reductive biology, phase variation, and basecalling error; disambiguate with orthogonal (short-read/HiFi) data.
- **Programmed frameshifts make one gene look like two.** `prfB`/RF2 (a **+1** frameshift at a slippery `CTTT` + internal SD), `dnaX` (−1), and IS-element transposases encode one protein across two frames; naive callers emit two short ORFs. PGAP recognizes a curated set.
- **Small ORFs (<~50 aa) are systematically missed** - callers impose a ~30 aa minimum because short ORFs arise by chance and coding statistics are unreliable there. *E. coli* K-12 was missing dozens of 16-50 aa proteins. Treat the gene count as a lower bound on the small proteome; for sORF biology use a dedicated caller (smORFer, smORFinder) and, ideally, Ribo-seq (the experimental arbiter of translation).
- **Archaea and Actinobacteria use leaderless mRNAs** (no 5' UTR, no Shine-Dalgarno) - Prodigal's RBS-first scoring degrades TIS placement; GeneMarkS-2 (and PGAP) model leaderless transcription. Use tRNAscan-SE's archaeal model for archaeal intron-containing tRNAs.

## Per-Method Failure Modes

### Cross-tool gene-count comparison
**Trigger:** comparing counts from Bakta vs Prokka vs old RefSeq, or mixed-vintage records. **Mechanism:** tool/DB differences dominate biological differences. **Symptom:** "novel genes" or accessory-genome inflation. **Fix:** re-annotate every genome from FASTA with one pipeline + pinned DB.

### Wrong translation table
**Trigger:** table 11 on a Mollicute. **Mechanism:** UGA read as stop. **Symptom:** low coding density, doubled short gene count, high hypothetical fraction. **Fix:** `--translation-table 4`; confirm from GTDB-Tk.

### Annotating an unvetted assembly
**Trigger:** running Bakta before CheckM2. **Mechanism:** contig breaks truncate CDS; contamination mixes organisms. **Symptom:** partial CDS at ends, inflated/chimeric gene set, missing rRNA operons. **Fix:** CheckM2 first; contamination >5% -> decontaminate.

### Trusting an over-specific product name
**Trigger:** reading the product column as ground truth. **Mechanism:** loose-homology transfer below ~40% identity is unreliable, especially for promiscuous folds. **Symptom:** a "histidine-kinase expansion" that is one over-called domain. **Fix:** open `.inference.tsv`; prefer InterPro/Pfam architecture over free-text product when they conflict.

### Single-mode calling on a metagenome or tiny replicon
**Trigger:** Prodigal single mode on a MAG/plasmid/phage. **Mechanism:** self-training needs a full single-organism genome. **Symptom:** poor calls on short/mixed input. **Fix:** Bakta `--meta` (anonymous mode).

### Missing signal peptides on macOS
**Trigger:** Bakta on macOS. **Mechanism:** DeepSig was dropped from the default mac conda env (~v1.9.4). **Symptom:** silently absent signal-peptide calls. **Fix:** verify the run log; run on Linux if SPs matter.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Coding density ~88-90% (band 85-93%) | bacterial genome norm | <85% = wrong table/fragmentation/decay; >93% = over-calling |
| ~850-1,000 genes/Mb (~1 gene/kb) | bacterial gene density | far higher = over-call; far lower = under-call/wrong table |
| Hypothetical 25-50% | annotation norm | ~0% = over-confident transfer; >60-70% = novel lineage or wrong tool/table |
| tRNA count ≥ ~20 (often 40-60) | one isoacceptor set minimum | far fewer = fragmented assembly broke tRNA regions |
| rRNA operons ~1-15 (e.g. ~7 in *E. coli*) | copy-number norm | zero/fractional in a "complete" genome = short-read repeat collapse |
| Prodigal minimum ~30 aa / 90 nt | caller default | shorter ORFs need a dedicated sORF caller + Ribo-seq |
| CheckM2 contamination ≤5%, completeness ≥90% | MIMAG-aligned | above/below -> annotation QC numbers uninterpretable, fix assembly first |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Genes split, low coding density | wrong translation table | `--translation-table 4/25`; confirm from GTDB-Tk |
| Many hypothetical proteins | novel organism / light DB | full Bakta DB; add InterProScan/eggNOG; normal if 25-50% |
| Low gene / tRNA count, missing rRNA | fragmented assembly | CheckM2; prefer long-read/complete assembly |
| RefSeq record differs from the local GFF | RefSeq is PGAP, GenBank keeps the submitter's annotation | report WP_ accession + locus_tag; expect divergence |
| Pseudogene spike | ONT homopolymer indels vs real decay vs phase variation | check homopolymer context; corroborate with short-read/HiFi |
| Submission rejected on locus tags | invented prefix | register the prefix via BioSample (3-12 alnum, starts with a letter) |

## References

- Schwengers O, et al. 2021. Bakta: rapid and standardized annotation of bacterial genomes via alignment-free sequence identification. *Microb Genom* 7:000685.
- Seemann T. 2014. Prokka: rapid prokaryotic genome annotation. *Bioinformatics* 30:2068-2069.
- Hyatt D, et al. 2010. Prodigal: prokaryotic gene recognition and translation initiation site identification. *BMC Bioinformatics* 11:119.
- Larralde M. 2022. Pyrodigal: Python bindings and interface to Prodigal. *J Open Source Softw* 7:4296.
- Lomsadze A, et al. 2018. Modeling leaderless transcription and atypical genes results in more accurate gene prediction in prokaryotes (GeneMarkS-2). *Genome Res* 28:1079-1089.
- Tatusova T, et al. 2016. NCBI prokaryotic genome annotation pipeline. *Nucleic Acids Res* 44:6614-6624.
- Li W, et al. 2021. RefSeq: expanding the Prokaryotic Genome Annotation Pipeline reach with protein family model curation. *Nucleic Acids Res* 49:D1020-D1028.
- Tanizawa Y, et al. 2018. DFAST: a flexible prokaryotic genome annotation pipeline for faster genome publication. *Bioinformatics* 34:1037-1039.
- Chan PP, et al. 2021. tRNAscan-SE 2.0: improved detection and functional classification of transfer RNA genes. *Nucleic Acids Res* 49:9077-9096.
- Chklovski A, et al. 2023. CheckM2: a rapid, scalable and accurate tool for assessing microbial genome quality using machine learning. *Nat Methods* 20:1203-1212.
- Dimonaco NJ, et al. 2022. No one tool to rule them all: prokaryotic gene prediction tool annotations are highly dependent on the organism of study. *Bioinformatics* 38:1198-1207.
- Tonkin-Hill G, et al. 2020. Producing polished prokaryotic pangenomes with the Panaroo pipeline. *Genome Biol* 21:180.
- Salzberg SL. 2019. Next-generation genome annotation: we still struggle to get it right. *Genome Biol* 20:92.
- Cole ST, et al. 2001. Massive gene decay in the leprosy bacillus. *Nature* 409:1007-1011.

## Related Skills

- functional-annotation - Add GO/KEGG/Pfam to hypothetical proteins with eggNOG-mapper/InterProScan
- ncrna-annotation - Detailed ncRNA identification with Infernal/Rfam beyond the built-in callers
- annotation-qc - CheckM2 completeness/contamination gate and gene-set sanity metrics
- genome-assembly/assembly-qc - Assess assembly quality before annotation
- genome-intervals/gtf-gff-handling - Parse and manipulate GFF3 output
- comparative-genomics/pangenome-analysis - Uniform re-annotation before pangenome clustering
<!-- END FILE: genome-annotation/prokaryotic-annotation/SKILL.md -->

## 子目录：genome-annotation/repeat-annotation

<!-- BEGIN FILE: genome-annotation/repeat-annotation/SKILL.md -->
---
name: bio-genome-annotation-repeat-annotation
description: Discovers, classifies, and masks repetitive elements and transposable elements with RepeatModeler2 (de novo family library), RepeatMasker (masking against a library), EDTA (plant/structural TEs), or EarlGrey (auto-curating wrapper), and quantifies TE expression from RNA-seq with TEtranscripts/SQuIRE. Covers de-novo-library-as-curation-project, soft-vs-hard masking, the domesticated-gene over-masking massacre, Dfam-vs-RepBase, TE classification (Class I/II, family-vs-copy), Kimura repeat landscapes, LAI, and the RNA-seq multimapping problem. Use when masking repeats before gene prediction, building a TE library for a non-model genome, or analyzing transposable-element content or expression.
tool_type: cli
primary_tool: RepeatMasker
---

## Version Compatibility

Reference examples tested with: RepeatModeler 2.0.5+, RepeatMasker 4.1.5+, EDTA 2.1+, EarlGrey 4.0+, TEtranscripts 2.2+, matplotlib 3.8+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

The **library database version matters as much as the binary**: RepeatMasker now ships with Dfam (open); RepBase has been paywalled since May 2019, so any pipeline that "requires RepBase" is a reproducibility/access hazard - record the Dfam release and library provenance. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Repeat and Transposable Element Annotation

**"Mask repeats in my genome assembly"** -> Build a de novo repeat-family library, annotate copies genome-wide, and soft-mask them as a prerequisite for gene prediction.
- CLI: `RepeatModeler -database mydb -LTRStruct` (library), `RepeatMasker -lib lib.fa -xsmall assembly.fa` (soft-mask), or `EarlGrey`/`EDTA.pl` (wrappers)

## The Single Most Important Modern Insight -- The Library Is the Experiment, and the Assembly Caps It

Two load-bearing truths the masker hides:

1. **De novo library construction is a curation research project, not a button.** A RepeatModeler2 run emits `mydb-families.fa` overnight - a *draft of a draft*: consensi are routinely 5'-truncated (L1 looks 1.5 kb when the active element is 6 kb), boundary-bled into flanking unique sequence, chimeric (two families merged), and 30-60% "Unknown" on a non-model genome. The dominant error in published TE annotations is the *library*, not the masker engine. Crucially, **masking percentage is robust to a bad library** (a chimeric consensus still masks roughly the right real estate), so the headline number survives while everything downstream rots: inflated family counts, wrong classification, distorted age landscapes, and - the killer - host-gene-contaminated consensi that silently mask real genes. Masking + gross % can use an automated library; any *per-family biological claim* (this family is young/active/novel) needs curation (Goubert 2022 *Mob DNA* 13:7; TE-Aid; MCHelper).

2. **Annotation quality is capped by assembly quality.** Short-read de Bruijn assemblers *collapse* near-identical TE copies and *drop* the youngest (most identical, most biologically active) ones, so short-read assemblies systematically under-count TEs and bias the age distribution toward "old" - which masquerades as the real signal "this lineage has no recent activity." Software cannot recover what the assembler threw away. Always ask what assembly a "% repeat" came from; HiFi/T2T raised the ceiling (LAI measures it) but T2T satellite/centromere repeats still exceed what the standard TE toolchain can annotate.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| RepeatModeler2 | Flynn 2020 *PNAS* | de novo family discovery -> consensus library | discover genome-specific families (run `-LTRStruct`) |
| RepeatMasker | Smit/Hubley/Green (software) | annotate/mask a genome **against** a library | the masking step; does not discover families |
| EarlGrey | Baril 2024 *MBE* | wraps RepeatModeler2 + auto consensus-elongation + RepeatMasker + plots | **non-model default**; minimal hand-work |
| EDTA | Ou 2019 *Genome Biol* | structural LTR/TIR/Helitron discovery + filtering | **plant / structurally-rich** genomes |
| LTR_retriever | Ou & Jiang 2018 *Plant Physiol* | isolate intact LTR-RTs; feeds LAI | LTR focus / assembly-quality (LAI) |
| TRF | Benson 1999 *NAR* | tandem/satellite repeats | a different algorithm class from TE maskers |
| RepeatClassifier / DeepTE / TERL | Flynn 2020; Yan 2020 | classify unknown consensi | attack the "Unknown" fraction (validate; can mislabel) |

Dfam (open) vs RepBase (paywalled since 2019) is the database schism - modern open pipelines build on Dfam + de novo. Engine `-e`: `rmblast` (default, consensus FASTA) vs `nhmmer` (Dfam profile HMMs, more sensitive for ancient repeats, slower) - the same genome reads a higher % with HMM detection.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Non-model eukaryote, defensible answer, minimal hand-work | EarlGrey | RepeatModeler2 + auto-curation + clean outputs |
| Plant / structurally-rich TE genome | EDTA | best-in-class LTR/TIR/Helitron structural annotation + host-gene filtering |
| Well-covered vertebrate, just need masking | RepeatMasker `-species` against Dfam | curated families already exist |
| Mask before gene prediction | RepeatMasker `-xsmall` (soft) + decontaminated library | predictors need soft-masking |
| Publication-grade TE biology claim | de novo -> manual curation (Goubert protocol, TE-Aid) | automated library is the start, not the end |
| Tandem/satellite/centromeric repeats | TRF + satellite tools (not RepeatMasker) | library-based TE tools don't see tandem arrays |
| TE expression from RNA-seq | -> TEtranscripts/SQuIRE (EM multimapper handling) | see expression section |
| TE insertion polymorphisms from reads | -> variant-calling (MELT/TEPID) | out of scope here |

## RepeatModeler2 -> RepeatMasker (the canonical pair)

```bash
# 1. De novo family discovery -> mydb-families.fa
BuildDatabase -name mydb assembly.fa
RepeatModeler -database mydb -threads 16 -LTRStruct   # -LTRStruct enables the LTR structural pipeline

# 2. (Recommended) decontaminate the library against host proteins, then UNION with Dfam clade
#    -> pull any consensus whose best hit is a host gene with no transposase/RT/integrase domain

# 3. Soft-mask against (custom library) for gene prediction
RepeatMasker -lib mydb-families.fa -xsmall -gff -e rmblast -pa 16 -dir rm_out assembly.fa
```

`-xsmall` = **soft-mask (lowercase)** - the key flag, the one people get wrong. Default `.masked` output hard-masks with N; `-x` masks with X. `-nolow` skips low-complexity/simple repeats (often wanted before gene prediction - see below). Outputs: `.masked`, `.out`, `.tbl` (summary %), `.align` (needed for the landscape).

## Soft vs Hard Masking (Critical, and the Over-Masking Massacre)

- **Gene prediction needs SOFT-masking.** Modern predictors (AUGUSTUS/GeneMark/BRAKER) avoid *nucleating* models in lowercase but let exons extend into repeats - real genes have TE-derived exons and TE-filled introns. **Hard-masking (N) destroys sequence**: any gene overlapping a repeat is truncated or never called, and the predictor reports nothing - no error, no log. The gene is simply absent.
- **Over-aggressive soft-masking is also a failure.** A gene whose promoter sits in an LTR, or a young gene inside a recent TE burst, gets suppressed because the predictor won't start a model in a heavily-lowercased locus. Before gene prediction, soft-mask *interspersed repeats only* and skip low-complexity (`-nolow`) - simple repeats overlap real coding microsatellites and low-complexity protein domains.
- **The domesticated-gene massacre.** A de novo library contains fragments of real multicopy gene families because they *look* repetitive - and masking them deletes the genome's most interesting genes. Named casualties: **RAG1/RAG2** (domesticated Transib transposase; V(D)J recombination), **syncytins** (captured retroviral env; placentation), **SETMAR/Metnase** (Hsmar1 mariner + SET domain; DNA repair), **CENP-B** (pogo transposase; centromere), and the **KRAB-ZNF arrays** (~350+ primate zinc-finger genes that exist *to repress TEs* - masking them deletes the genome's anti-TE machinery). Defense: **decontaminate the library against a protein DB before masking** (EDTA does a version; RepeatModeler2 does not by default). Treat any gene model falling entirely inside a masked "TE" as a flag to investigate, not a finished call.

## TE Classification (Wicker-compatible)

- **Class I (retrotransposons, copy-and-paste via RNA + RT):** LTR-RTs (Ty3/Gypsy, Ty1/Copia - dominate large plant genomes), LINEs (autonomous, often 5'-truncated), SINEs (non-autonomous, e.g. Alu).
- **Class II (DNA transposons, mostly cut-and-paste):** TIR superfamilies (hAT, Tc1/Mariner, CACTA, PIF/Harbinger, Mutator), Helitrons (rolling-circle, can capture host genes), MITEs (non-autonomous TIR derivatives, EDTA reclassifies ≤600 bp).
- **Family vs copy:** a *family* is one consensus in the library (~thousands); a *copy/insertion* is one genomic locus matching it (millions). "% genome masked" counts copies; classification is family-level; "10,000 TEs" is ambiguous between the two.
- **Full-length vs decayed:** most copies are dead, truncated, point-mutated relics; only a tiny fraction are intact. **Solo-LTR : full-length ratio** is real biology (recombinational LTR-RT removal rate), measurable only if the assembly resolved full-length elements. Wicker 2007 *Nat Rev Genet* is the reference scheme; present Gypsy/Copia and the ICTV Metaviridae/Pseudoviridae names both.

## Repeat Statistics and Age Landscape with Python

**Goal:** Summarize masked content by class and plot the Kimura-divergence landscape (a relative within-genome age readout).

**Approach:** Parse the RepeatMasker `.out` file, group by class for bp and genome fraction, then histogram percent divergence stratified by major TE class (x = divergence-from-consensus ~ relative age).

```python
import pandas as pd

def parse_repeatmasker_out(out_file):
    records = []
    with open(out_file) as f:
        for i, line in enumerate(f):
            if i < 3:
                continue
            parts = line.split()
            if len(parts) < 15:
                continue
            records.append({'perc_div': float(parts[1]), 'seqid': parts[4],
                            'repeat_class': parts[10], 'length': int(parts[6]) - int(parts[5]) + 1})
    return pd.DataFrame(records)

def repeat_summary(rm_df, genome_size):
    by_class = rm_df.groupby('repeat_class')['length'].sum().sort_values(ascending=False)
    total = rm_df['length'].sum()
    print(f'Total masked: {total/genome_size:.1%} of genome (a LOWER bound; ancient copies decay past detection)')
    return by_class / genome_size * 100
```

The landscape is **right-censored** - the most ancient TEs decayed past alignment detection, so "no old activity" can mean "old activity is invisible." A sharp left (low-divergence) peak is a recent/ongoing burst; treat *presence* of a recent peak as informative and *absence* of an old hump cautiously. A truncated/chimeric consensus distorts the whole x-axis (another reason curation matters); never compare landscapes across genomes annotated with different libraries.

## TE Expression from RNA-seq (the Multimapping Minefield)

A read from a young high-copy family maps equally to hundreds of near-identical loci. **Unique-only mapping** (standard RNA-seq QC) discards most TE signal and biases toward old, uniquely-mappable copies - measuring the *least* active elements. Use EM/probabilistic reassignment: **TEtranscripts/TElocal** (Jin 2015), **SQuIRE** (Yang 2019), **Telescope** (Bendall 2019). Subfamily-level (TEtranscripts: "L1 went up", high power, no locus) vs locus-level (SQuIRE/TElocal/Telescope: "this HERV-K on chr7 is on", noisy, mappability-sensitive) changes the conclusion, not just the resolution. The dominant false positive: **a TE in an intron or downstream of an expressed gene is not "expressed"** - read-through/intron-retention piles reads on it; distinguish autonomous transcription from passenger signal by strand and continuity (TEspeX filters embedded-TE reads). Be skeptical of any "TEs reactivated in disease/aging" headline that used unique-only mapping.

## Per-Method Failure Modes

### Hard-masking before gene prediction
**Trigger:** running RepeatMasker without `-xsmall` (default hard-masks with N). **Mechanism:** masked sequence is destroyed. **Symptom:** genes overlapping repeats silently absent from the GFF. **Fix:** `-xsmall`; hand a soft-masked genome to the predictor.

### Host-gene-contaminated library
**Trigger:** masking with an uncurated de novo library. **Mechanism:** multicopy gene families look repetitive and enter the library. **Symptom:** suspiciously few NLR/ZNF/OR genes; domesticated genes (RAG1, CENP-B) missing. **Fix:** BLAST the library against a protein DB; drop consensi hitting host genes with no TE domain.

### Trusting % repeat from a short-read assembly
**Trigger:** comparing TE content across studies/assemblies. **Mechanism:** short reads collapse/drop young copies; % depends on library+engine+assembly. **Symptom:** "low TE, all ancient" or non-comparable cross-study tables. **Fix:** check LAI/assembly type; report method + assembly with every number; never compare published % across papers.

### Discarding multimappers in TE RNA-seq
**Trigger:** unique-only TE quantification. **Mechanism:** young high-copy families are not uniquely mappable. **Symptom:** most TE signal lost, bias to old elements. **Fix:** EM tools (TEtranscripts/SQuIRE/Telescope); separate read-through from autonomous transcription.

### "Unknown" passed off as a result
**Trigger:** shipping a 40%-Unknown library without inspection. **Mechanism:** classification is the hardest, last, most-skipped step. **Symptom:** weak biological annotation; possible gene-family contamination hiding in Unknown. **Fix:** RepeatClassifier/DeepTE to triage; curate; note DB-coverage limits.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `-xsmall` soft-mask before gene prediction | predictor requirement | hard-mask truncates repeat-overlapping genes |
| TE content scales with genome size (human ~50%, maize ~85%, Arabidopsis ~20-25%, fungi ~1-20%) | clade norms (approx) | main driver of the C-value enigma; sanity-check vs genome size |
| "Unknown" ~<15% (mammal) vs 30-50% (non-model) | DB coverage | high Unknown bounds biological claims; very low on non-model = over-assignment |
| LAI <10 draft / 10-20 reference / >20 gold | Ou 2018 *NAR* | LTR-RT-resolution metric; only valid for LTR-rich genomes |
| Report library + engine + assembly with any % | reproducibility | % masked is non-comparable across methods |
| 80-80-80 (≥80% id over ≥80% length over ≥80 bp) | Wicker lineage | dereplication threshold, NOT a quality check |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Gene prediction finds too few genes | hard-masked, or over-masked low-complexity | `-xsmall`; `-nolow` before gene prediction |
| Suspiciously few NLR/ZNF/OR genes | uncurated library masked gene families | decontaminate library against a protein DB |
| Low masking percentage | novel repeats absent from DB | run RepeatModeler2 first; union de novo + Dfam |
| RepeatModeler very slow | normal for large genomes | `-threads`; consider EDTA (plants) or EarlGrey |
| "TE re-activated" result looks too clean | unique-only mapping / read-through | EM tools; check strand + continuity from neighbor |
| Cross-study % repeat disagree | different library/engine/assembly | re-annotate uniformly; report method |

## References

- Flynn JM, et al. 2020. RepeatModeler2 for automated genomic discovery of transposable element families. *PNAS* 117:9451-9457.
- Storer J, et al. 2021. The Dfam community resource of transposable element families, sequence models, and genome annotations. *Mob DNA* 12:2.
- Ou S, et al. 2019. Benchmarking transposable element annotation methods for creation of a streamlined, comprehensive pipeline (EDTA). *Genome Biol* 20:275.
- Ou S, Jiang N. 2018. LTR_retriever: a highly accurate and sensitive program for identification of long terminal repeat retrotransposons. *Plant Physiol* 176:1410-1422.
- Ou S, Chen J, Jiang N. 2018. Assessing genome assembly quality using the LTR Assembly Index (LAI). *Nucleic Acids Res* 46:e126.
- Wicker T, et al. 2007. A unified classification system for eukaryotic transposable elements. *Nat Rev Genet* 8:973-982.
- Baril T, Galbraith J, Hayward A. 2024. Earl Grey: a fully automated user-friendly transposable element annotation and analysis pipeline. *Mol Biol Evol* 41:msae068.
- Goubert C, et al. 2022. A beginner's guide to manual curation of transposable elements. *Mob DNA* 13:7.
- Jin Y, et al. 2015. TEtranscripts: a package for including transposable elements in differential expression analysis of RNA-seq datasets. *Bioinformatics* 31:3593-3599.
- Yang WR, et al. 2019. SQuIRE reveals locus-specific regulation of interspersed repeat expression. *Nucleic Acids Res* 47:e27.
- Bendall ML, et al. 2019. Telescope: characterization of the retrotranscriptome by accurate estimation of transposable element expression. *PLoS Comput Biol* 15:e1006453.
- Benson G. 1999. Tandem repeats finder: a program to analyze DNA sequences. *Nucleic Acids Res* 27:573-580.

## Related Skills

- eukaryotic-gene-prediction - Receives the soft-masked genome; over-masking is a shared failure
- annotation-qc - LAI and repeat-content sanity in the assembly-to-annotation handoff
- genome-assembly/assembly-qc - Assembly type sets the TE-annotation ceiling (LAI)
- differential-expression/deseq2-basics - Differential TE expression from TEtranscripts/SQuIRE counts
- copy-number/recurrent-cnv - Segmental duplications, a distinct phenomenon from interspersed repeats
<!-- END FILE: genome-annotation/repeat-annotation/SKILL.md -->

<!-- END CATEGORY: genome-annotation -->

