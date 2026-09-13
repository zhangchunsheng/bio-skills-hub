---
slug: bio-epidemiological-genomics-integrated
version: 1.0.1
displayName: "流行病基因组学 / Epidemiological genomics"
name: bio-epidemiological-genomics-integrated
summary: "中文：流行病基因组学综合技能，整合 5 个相关专题，覆盖流行病基因组学：病原体分型（MLST/cgMLST）、AMR监测、系统发育动力学、传播推断。 English: Integrated Epidemiological genomics skill covering 5 related topics, including Epidemiological genomics: pathogen typing (MLST/cgMLST), AMR surveillance, phylodynamics, transmission inference."
description: "中文：这是一个面向流行病基因组学的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：流行病基因组学：病原体分型（MLST/cgMLST）、AMR监测、系统发育动力学、传播推断。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：AMRFinderPlus, BEAST2, Pangolin。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Epidemiological genomics, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Epidemiological genomics: pathogen typing (MLST/cgMLST), AMR surveillance, phylodynamics, transmission inference. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: AMRFinderPlus, BEAST2, Pangolin. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# epidemiological-genomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: epidemiological-genomics -->

## 子目录：epidemiological-genomics/amr-surveillance

<!-- BEGIN FILE: epidemiological-genomics/amr-surveillance/SKILL.md -->
---
name: bio-epidemiological-genomics-amr-surveillance
description: Detects acquired antimicrobial-resistance determinants and chromosomal point-mutation resistance in bacterial assemblies using AMRFinderPlus, ResFinder 4.0 (acquired + PointFinder), CARD-RGI, abritAMR, staramr, and species-specific callers (TB-Profiler, Mykrobe). Harmonises cross-tool output via hAMRonization, contextualises determinants with mobile-genetic-element annotation (MOB-suite, PlasmidFinder, MobileElementFinder, ICEberg), predicts phenotype against EUCAST or CLSI breakpoints, and translates calls into WHO GLASS reporting categories. Use when screening clinical or surveillance isolates for AMR, distinguishing acquired vs intrinsic vs point-mutation resistance, calling rpoB / katG / pncA / gyrA / mgrB mutations, reconciling AMRFinderPlus vs RGI vs ResFinder disagreement, contextualising carbapenemases or mcr alleles on plasmids, predicting susceptibility from genotype against the WHO Mtb 2nd-edition catalogue, or building a hAMRonized multi-lab AMR surveillance pipeline.
tool_type: mixed
primary_tool: AMRFinderPlus
---

## Version Compatibility

Reference examples tested with: ncbi-amrfinderplus 4.0+, resfinder 4.5+, rgi 6.0+ (CARD 3.3+), abritamr 1.0.14+, staramr 0.10+, hamronization 1.1+, tb-profiler 6.2+, mykrobe 0.13+, mob_suite 3.1+, plasmidfinder 2.1+, MobileElementFinder 1.0+, pandas 2.2+, BioPython 1.84+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- AMRFinderPlus: `amrfinder --list_organisms` for the current `--organism` catalogue
- WHO Mtb catalogue: `tb-profiler list_db` and verify the bundled WHO edition
- AMR database freshness: `amrfinder -u` (NCBI ReferenceGeneCatalog) and `tb-profiler update_tbdb`

If a flag or column name does not match (`--species` vs `--organism`, `barcode_build` vs `barcode-build`), introspect the installed package rather than retrying. AMRFinderPlus, RGI, and ResFinder all renamed columns between major releases.

# AMR Surveillance

**"What antibiotic-resistance determinants are in this assembly, and what susceptibility do they imply?"** -> Combine acquired-gene detection, chromosomal point-mutation calling, mobile-element context, and curated phenotype mapping into a single per-isolate report fit for surveillance or clinical handover. Tool choice is determined by species (Mtb needs TB-Profiler, not AMRFinderPlus), reporting standard (WHO GLASS vs CARD vs in-house), and whether mobility matters (carbapenemase outbreak: yes; routine ESBL screen: less so).

- CLI: `amrfinder -n assembly.fa --organism Klebsiella_pneumoniae --plus` -- acquired + intrinsic-aware point mutations
- CLI: `tb-profiler profile -1 r1.fq.gz -2 r2.fq.gz -p sample` -- TB drug-resistance against WHO 2nd-edition catalogue
- CLI: `hamronize amrfinderplus --analysis_software_version 4.0.3 --reference_database_version 2025-02-01.1 in.tsv > out.tsv` -- normalise output across tools
- Python: `pandas` to join AMRFinderPlus + RGI + ResFinder + MOB-suite per-isolate for a single decision table

## The Single Most Important Modern Insight -- Acquired AMR detection is not species-agnostic

A pan-species AMRFinderPlus run misses chromosomal point-mutation resistance because the point-mutation panels are species-specific and activated only when `--organism` is set. Running `amrfinder -n mtb.fa` without `--organism` returns "no AMR detected" on an XDR-TB genome because AMRFinderPlus has no Mtb organism mode -- the user must switch tools (TB-Profiler or Mykrobe + WHO 2nd-edition catalogue). Similarly, *Salmonella* gyrA T83I, *Klebsiella* mgrB inactivation, and *E. coli* QRDR mutations are silent without `--organism Salmonella` / `Klebsiella_pneumoniae` / `Escherichia`. For any cross-tool surveillance pipeline, AMRFinderPlus with `--organism` MUST be paired with a species-specific second tool (TB-Profiler for Mtb; ResFinder 4.0 with `-s 'species'` for PointFinder coverage; hAMRonization to merge). Andersson et al. *Nat Rev Microbiol* 17:479 (2019) further notes that heteroresistance at 0.1-1% allele frequency is widespread and invisible to default variant callers, compounding the failure mode for any single-tool workflow.

## Algorithmic Taxonomy

| Tool | Mechanism | Inputs | Output | Strength | Fails when |
|------|-----------|--------|--------|----------|------------|
| AMRFinderPlus (Feldgarden 2021 *Sci Rep* 11:12728) | Curated HMM + BLAST against NCBI ReferenceGeneCatalog; per-gene cutoffs | assembly or protein | gene + class + element-type | Gene-family-aware (catches divergent variants); built-in species point-mutation panels | No Mtb mode; reports intrinsic genes unless `--organism` set |
| ResFinder 4.0 (Bortolaia 2020 *J Antimicrob Chemother* 75:3491) | BLAST against ResFinder DB (acquired) + PointFinder DB (chromosomal mutations) per species | assembly or reads | gene + predicted phenotype (S/I/R) | Phenotype prediction tied to CLSI/EUCAST | Requires explicit `-s 'species'` for PointFinder; default 90/60 cutoffs hide divergent variants |
| CARD-RGI (Alcock 2023 *NAR* 51:D690) | BLAST + HMM against CARD; tiers Perfect / Strict / Loose | assembly or protein | ARO ontology term, model-type (homolog / variant / overexpression / knockout / rRNA) | Mechanism-resolved (operons modelled); ARO ontology is curated | Loose tier produces many false positives; default Strict+Perfect misses real variants in non-model organisms |
| abritAMR (Sherry 2023 *Nat Commun* 14:60) | AMRFinderPlus wrapper + drug-class classifier; ISO-certified for clinical use | assembly | gene + drug class | First ISO-certified AMR pipeline; accredited reporting categories | Limited to AMRFinderPlus's underlying gene panel |
| staramr | ResFinder + PointFinder + PlasmidFinder + MLST in one pipeline | assembly | combined report | One-shot Salmonella / E. coli / Campylobacter surveillance | Default organism handling can hide point mutations; verify each component version |
| TB-Profiler (Phelan 2019 *Genome Med* 11:41) | Maps reads or assembly against H37Rv + WHO catalogue + Coll/Napier lineage barcode | reads or assembly | per-drug R/R-interim/Uncertain/S + lineage | WHO 2nd-edition catalogue integration; lineage call; heteroresistance from allele frequency | Hardcoded to MTBC; older bundled DB may predate current WHO edition |
| Mykrobe (Hunt 2019 *Wellcome Open Res* 4:191) | k-mer presence/absence against curated panel | reads | species + AMR per drug | k-mer-fast; cross-checks TB-Profiler; supports Mtb, S. aureus, Salmonella, gonorrhoea | Panel may lag WHO catalogue; check `--panel` |
| hAMRonization (PHA4GE) | Format converter to PHA4GE schema | per-tool TSV | unified TSV/JSON | Cross-tool comparison; surveillance harmonisation | Mandatory metadata fields differ per tool subparser |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| Routine screen of an *E. coli* / *Klebsiella* / *Salmonella* assembly for acquired AMR + point mutations | AMRFinderPlus with `--organism Escherichia` / `Klebsiella_pneumoniae` / `Salmonella` + `--plus` | Without `--organism`: no PointFinder panel, fluoroquinolone QRDR mutations missed; intrinsic-gene noise in Klebsiella |
| *M. tuberculosis* drug-resistance prediction | TB-Profiler interpreted via WHO 2nd-edition catalogue, Mykrobe as cross-check on R/XDR isolates | AMRFinderPlus has no Mtb organism mode; ResFinder PointFinder lacks the full WHO catalogue; tool defaults silently call Group 3 mutations as "susceptible" |
| Predict S/I/R phenotype, not gene presence | ResFinder 4.0 OR abritAMR; document EUCAST or CLSI breakpoint year | AMRFinderPlus reports presence only; mapping presence -> phenotype needs curated rules |
| Carbapenemase outbreak: is the gene mobile? | AMRFinderPlus -> MOB-suite (`mob_recon` + `mob_typer`) -> cross-reference; long-read or hybrid assembly recommended | PlasmidFinder alone gives replicon type but not gene-plasmid linkage; short-read draft assemblies fragment plasmid contigs and lose context |
| Cross-laboratory surveillance reporting | Pass per-tool output through hAMRonization to PHA4GE schema; populate `analysis_software_version` and `reference_database_version` | Raw cross-tool comparison is meaningless (CARD ARO vs ResFinder name vs NCBI ReferenceGeneCatalog) |
| Novel-variant surveillance (emergence) | AMRFinderPlus (HMM, gene-family-aware) OR CARD-RGI with Loose-tier manual review | abricate's 80/80 defaults reject divergent family members; pure-BLAST defaults silently miss novel mcr / OXA sub-variants |
| Quantitative AMR from metagenomic reads | AMRPlusPlus / DeepARG / ARGs-OAP normalised to 16S; report "ARG abundance" NOT "resistance" | Assembly-based tools fail on short reads; reporting environmental ARG counts as "resistance" inherits the environmental-resistome critique that homolog presence is not phenotypic resistance |
| Colistin resistance in *Klebsiella* / *Enterobacter* / *Salmonella* | mcr-1 to mcr-10 acquired (AMRFinderPlus; mcr-1 originally Liu 2016 *Lancet Infect Dis* 16:161) + mgrB / pmrAB / phoPQ point mutations (`--organism Klebsiella_pneumoniae`) + phenotypic confirmation for mcr-9/10 | mcr-9 / mcr-10 frequently report without elevated MIC; treating mcr presence as "colistin-R" triggers infection control unnecessarily |
| WHO GLASS submission | hAMRonization -> drug-class mapping -> EUCAST/CLSI breakpoint interpretation; record breakpoint year | Gene-level reporting without class mapping cannot populate GLASS categories |

Methodology evolves rapidly; before a high-stakes outbreak report, web-search "AMRFinderPlus organism modes 2026" and confirm the WHO Mtb catalogue edition currently bundled in TB-Profiler.

## AMRFinderPlus With Species Mode

**Goal:** Produce a per-isolate AMR report including acquired genes, species-specific chromosomal point mutations, stress/virulence elements, and per-hit method and coverage metadata for downstream harmonisation.

**Approach:** Run `amrfinder` with `-n` for nucleotide assembly, `--organism` to activate the species-specific point-mutation panel, `--plus` to include stress / virulence / heat / metal, and `--report_all` when truncated-gene visibility matters. Pin the database via `amrfinder -u` -> verify `--db` matches a recorded date.

```bash
DB=$(amrfinder -V | grep -i database | awk '{print $NF}')

amrfinder \
    -n assembly.fa \
    --organism Klebsiella_pneumoniae \
    --plus \
    --threads 8 \
    -o sample.amrfinder.tsv

echo "DB version: ${DB}" >> sample.amrfinder.tsv
```

Column semantics worth inspecting: `Element type` (AMR / POINT / VIRULENCE / STRESS / etc.), `Method` (EXACTX / PARTIAL_CONTIG_END / HMM / etc. -- partial-contig hits flag assembly fragmentation), `% Coverage of reference sequence`, `% Identity to reference sequence`, `Class` / `Subclass` (drug-class summary). `Method = PARTIAL_CONTIG_END` is the smoking gun for plasmid-context fragmentation -- consider long-read confirmation.

## TB-Specific Workflow

**Goal:** Generate a WHO-catalogue-aligned drug-resistance report for *M. tuberculosis* covering all 13 first-line + second-line + new/repurposed drugs, with lineage assignment via the Coll/Napier MTBC barcode (90-SNP version) and explicit handling of Group 3 (Uncertain) mutations.

**Approach:** TB-Profiler primary (it bundles the WHO catalogue and reports the Walker 2022 / 2023 association grouping); Mykrobe as an orthogonal cross-check on any R / XDR call that will drive treatment. NEVER collapse Group 3 mutations to "susceptible" -- the WHO catalogue's tiered scoring is load-bearing for clinical handover.

```bash
tb-profiler update_tbdb

tb-profiler profile \
    -1 reads_R1.fq.gz \
    -2 reads_R2.fq.gz \
    -p sample \
    --txt --csv --pdf \
    --dir tbprofiler_out

mykrobe predict \
    --sample sample \
    --species tb \
    --output sample.mykrobe.json \
    --format json \
    reads_R1.fq.gz reads_R2.fq.gz
```

Allix-Béguec et al. (CRyPTIC) *NEJM* 379:1403 (2018) established >99% negative predictive value for first-line drugs and is the basis for WGS-only DST policies; the same study showed sensitivity remains lower for bedaquiline, delamanid, linezolid, and clofazimine, so phenotypic DST is still required for second-line and new/repurposed agents in MDR/XDR-TB workups. The WHO 2023 catalogue (Walker et al. *Lancet Microbe* 3:e265, 2022 for the 2021 edition methodology; 2023 second edition data) grades each mutation **Group 1** / **Group 2** (Associated -- interim) / **Group 3** (Uncertain) / **Group 4** (Not Associated -- interim) / **Group 5** (Not Associated). Reporting Group 3 as "S" actively misleads clinicians.

## hAMRonization for Cross-Tool Reporting

**Goal:** Convert per-tool AMR output (AMRFinderPlus, ResFinder, RGI, abricate, staramr, ARIBA, TB-Profiler, Mykrobe) to the PHA4GE schema so a multi-laboratory or multi-tool surveillance dataset is comparable.

**Approach:** Invoke `hamronize <tool>` per input with mandatory provenance metadata (`--analysis_software_version`, `--reference_database_version`, `--input_file_name`), then `hamronize summarize` to merge.

```bash
hamronize amrfinderplus \
    --analysis_software_version 4.0.3 \
    --reference_database_version 2025-02-01.1 \
    --input_file_name sample.amrfinder.tsv \
    sample.amrfinder.tsv > sample.hamr.tsv

hamronize resfinder \
    --analysis_software_version 4.5.0 \
    --reference_database_version 2024-12-15 \
    --input_file_name sample.resfinder.json \
    sample.resfinder.json > sample.resfinder.hamr.tsv

hamronize summarize -t tsv -o cohort.hamr.tsv per_sample_hamr/*.tsv
```

Default reporting ontology for public-health output is NCBI ReferenceGeneCatalog. Two consequences: (1) CARD ARO terms need translation; (2) any custom gene additions need a corresponding NCBI accession before they appear in the harmonised stream.

## Mobile-Genetic-Element Context

**Goal:** Determine whether a clinically actionable AMR gene (carbapenemase, mcr, ESBL) sits on a chromosome, a plasmid (and which incompatibility group / cluster), an integrative-conjugative element, or a transposon -- because "gene present" tells the infection-control team nothing about transmissibility.

**Approach:** Reconstruct plasmids from the assembly with MOB-suite `mob_recon`; type each plasmid with `mob_typer`; cross-reference AMR-gene coordinates against the plasmid contig list; annotate IS elements / integrons with MobileElementFinder. For surveillance-grade plasmid resolution, prefer long-read (R10.4.1 Q20+) or hybrid assemblies -- short-read draft assemblies routinely fragment plasmid contigs.

```bash
mob_recon \
    --infile assembly.fa \
    --outdir mob_out/ \
    --num_threads 4

mob_typer \
    --infile mob_out/plasmid_AA001.fasta \
    --out_file mob_out/plasmid_AA001.typed.tsv

mefinder find \
    --contig assembly.fa \
    --out mef_out/sample \
    --threads 4
```

Document MOB-suite version explicitly: v2 and v3 cluster codes are non-interoperable, and v3.1+ adds MGE reporting. Across longitudinal surveillance crossing the v2 -> v3 boundary, the same plasmid receives different cluster IDs and appears spuriously "novel".

## Per-Method Failure Modes

### AMRFinderPlus run pan-species on a *Mycobacterium tuberculosis* assembly

**Trigger:** `amrfinder -n mtb.fa` without `--organism`; AMRFinderPlus has no Mtb organism mode in any v4.x release.

**Mechanism:** The species-specific point-mutation panels are activated only when a recognised `--organism` is passed. Mtb resistance is overwhelmingly chromosomal point mutation (rpoB / katG / inhA / pncA / embB / gyrA / rrs). With no panel active, none of these are called.

**Symptom:** Empty AMR table on a phenotypically MDR/XDR isolate; lineage barcode not reported (AMRFinderPlus does not call MTBC lineage).

**Fix:** Switch tools. Use TB-Profiler (preferred -- bundles WHO catalogue + Coll/Napier barcode) or Mykrobe; the AMRFinderPlus catalogue does not cover MTBC.

### OXA-48-like family collapsed to a single bucket

**Trigger:** Default per-isolate summarisers report the gene family (`bla_OXA-48-like`) rather than the allele (`bla_OXA-244`).

**Mechanism:** OXA-48 (potent carbapenemase), OXA-181 (Thr213Ala -- similar activity, different plasmid), OXA-232 (Arg214Ser -- reduced carbapenemase activity), and OXA-244 (Arg214Gly -- weakest, often phenotypically susceptible to ertapenem) share >95% identity. Pipelines that report family-level summary erase the clinically actionable variant identity.

**Symptom:** Surveillance report says "OXA-48-like detected", phenotype is borderline ertapenem-susceptible / meropenem-susceptible, clinical team is confused about whether ceftazidime-avibactam is needed.

**Fix:** Report the allele explicitly; never collapse to family. AMRFinderPlus reports the allele in `Gene symbol` -- preserve it through hAMRonization rather than summarising.

### IS-element-mediated derepression invisible to gene-presence pipelines

**Trigger:** Phenotypic high-level AmpC hyperproduction in *Enterobacter cloacae* complex / *Citrobacter freundii*; or KPC over-expression on Tn4401b (100-bp promoter deletion).

**Mechanism:** Resistance is mediated by IS*Ecp1* / IS*26* / IS*10* insertion upstream of the ampC promoter producing a strong hybrid promoter, or by Tn4401 variant. Gene presence is unchanged. Short-read assemblies fragment IS elements and collapse repeats; promoter context is lost. AMRFinderPlus / RGI / ResFinder report the gene; the regulatory configuration is not annotated.

**Symptom:** AMR pipeline output identical for wild-type ampC carrier and the hyperproducer; clinical phenotype is divergent.

**Fix:** Long-read (Nanopore R10.4.1 Q20+ or PacBio HiFi) or hybrid assembly with explicit promoter-context inspection. For Tn4401 variant typing, manual blast of the transposon region. Tools that automate this are emerging but not yet a default in surveillance pipelines.

### Heteroresistance below default variant-caller thresholds

**Trigger:** Routine Illumina WGS-AMR pipeline on a clinical isolate; resistance variant appears at 1-5% allele frequency.

**Mechanism:** Heteroresistance -- clonal subpopulations carrying resistance at 0.1-1% (Andersson, Nicoloff, Hjort *Nat Rev Microbiol* 17:479, 2019) -- is widespread and clinically meaningful (treatment failure under antibiotic pressure). Default variant callers (`bcftools`, `lofreq` default `-q 20`, GATK HaplotypeCaller) require minor-allele frequency of typically 10-20% to call. Assembly-based pipelines (AMRFinderPlus on assembly) collapse minor variants entirely.

**Symptom:** Surveillance pipeline calls "S" but clinical failure under therapy; subsequent sampling reveals high-level resistance.

**Fix:** For clinically critical drugs, supplement assembly-based AMR with deep-read variant calling at lower MAF thresholds (`lofreq` with `-q 13 -a 0.01`), or use targeted deep-amplicon sequencing. TB-Profiler reports allele frequency for resistance calls -- inspect for heteroresistance routinely.

### WHO Mtb Group 3 mutations silently called "susceptible"

**Trigger:** TB-Profiler / Mykrobe run on an Mtb isolate carrying a mutation graded Group 3 (Uncertain) in the WHO catalogue.

**Mechanism:** Tools translate Group 3 calls to "no resistance prediction" in their summary; downstream summarisers and clinical handover forms collapse "no prediction" to "S". The Walker 2022 *Lancet Microbe* catalogue methodology explicitly separates Group 3 (Uncertain) from Group 4/5 (Not Associated) for exactly this reason.

**Symptom:** Patient treated as drug-susceptible; clinical failure; retrospective inspection finds Group 3 mutation that should have triggered phenotypic DST.

**Fix:** Read TB-Profiler JSON output, NOT the simplified TSV. Report Group 3 mutations explicitly with "uncertain significance -- phenotypic DST recommended". This is widely under-communicated in surveillance pipelines.

### fosA / efflux-regulator hits overcalled as resistance

**Trigger:** Chromosomal fosA in *Klebsiella pneumoniae* / *Enterobacter* / *Serratia* reported as "fosfomycin resistant" by ResFinder / AMRFinderPlus.

**Mechanism:** Chromosomal fosA confers low-level fosfomycin resistance below the EUCAST clinical breakpoint (32 mg/L for urinary isolates). Treating chromosomal-fosA *E. coli* as fosfomycin-resistant withholds an oral option for uncomplicated UTI unnecessarily.

**Symptom:** All *K. pneumoniae* isolates flagged "fosfomycin-R" regardless of plasmid context or phenotype.

**Fix:** AMRFinderPlus with `--organism Klebsiella_pneumoniae` suppresses the intrinsic fosA report; verify the suppression worked. Cross-reference fosA hits with MOB-suite to determine plasmid context; only plasmid-borne or upregulated fosA should be reported as resistance.

## Reconciliation: When AMR Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| AMRFinderPlus calls `bla_NDM-5`; ResFinder calls `bla_NDM-1` | Allele assignment differs by reference database (NCBI ReferenceGeneCatalog vs ResFinder DB); both are within the NDM family | Report the family + flag the allele discordance; for clinical handover prefer NCBI nomenclature, for legacy comparability prefer ResFinder |
| RGI calls `mecA` "Strict"; AMRFinderPlus calls "EXACTX" | Tier semantics differ; both real hits | Concordant resistance call -- harmonise via hAMRonization, use NCBI ReferenceGeneCatalog nomenclature |
| ResFinder reports a gene at 88% identity; AMRFinderPlus omits | ResFinder default 90/60; AMRFinderPlus HMM cutoff stricter for that family | Manual review; for novel-variant surveillance, AMRFinderPlus + Loose-tier RGI catches more |
| TB-Profiler and Mykrobe disagree on isoniazid | Different curated panels; one may predate WHO 2nd edition | Defer to TB-Profiler interpreted against WHO catalogue; manual blast of katG / inhA / fabG1 |
| mcr-9 detected; phenotypic colistin MIC susceptible | Expected -- mcr-9 frequently silent without IqrR / induction | Report mcr-9 detection + susceptibility; do NOT trigger infection-control as if MCR-1 |
| AMRFinderPlus `Method=PARTIAL_CONTIG_END` for a carbapenemase | Assembly fragmentation at the plasmid edge | Re-assemble with long reads or hybrid before reporting; the gene may be present in full |
| RGI calls a long list of "Loose" hits | Non-model organism or distant lineage | Manual curation of Loose hits -- discard generic homologs, retain those near canonical AMR-active residues |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| AMRFinderPlus default %identity | per-gene curated (typically 90% global) | Feldgarden 2021 *Sci Rep* 11:12728; HMM cutoff is gene-family-aware |
| AMRFinderPlus default %coverage | 50% (alignment coverage) | NCBI Reference; `--report_all` exposes partial hits |
| ResFinder default %id / %coverage | 90% / 60% | CGE convention; tighter than abricate |
| abricate default %id / %coverage | 80% / 80% | Too permissive for novel-variant surveillance |
| WHO Mtb Group 1 (Associated with R) | High-confidence resistance call | Walker 2022 *Lancet Microbe* 3:e265 |
| WHO Mtb Group 3 (Uncertain) | NOT "susceptible" -- phenotypic DST recommended | Walker 2022 *Lancet Microbe* 3:e265; 2023 2nd edition data |
| Heteroresistance MAF | 0.1-1% (deep amplicon detection) | Andersson 2019 *Nat Rev Microbiol* 17:479 |
| EUCAST fosfomycin urinary breakpoint | 32 mg/L | EUCAST clinical breakpoint tables (year-specific) |
| Variant MAF for routine WGS-AMR calling | 10% (`lofreq` default), 20% (GATK default) | Tool defaults; document per-pipeline |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| AMRFinderPlus empty on TB assembly | No Mtb `--organism` mode | Switch to TB-Profiler / Mykrobe |
| AMRFinderPlus calls intrinsic fosA on Klebsiella | `--organism` not set; intrinsic suppression off | Always pass `--organism` for the species |
| `--species` flag rejected | AMRFinderPlus uses `--organism`, not `--species` | Use `--organism Klebsiella_pneumoniae` |
| Different gene names for same determinant across tools | CARD ARO vs ResFinder vs NCBI ReferenceGeneCatalog | Pass through `hamronize` |
| `Method=PARTIAL_CONTIG_END` on a clinically critical gene | Assembly fragmentation | Re-assemble with long reads / hybrid |
| `hamronize` rejects input as missing metadata | `--analysis_software_version` not supplied | Populate all mandatory PHA4GE fields per tool subparser |
| MOB-suite cluster codes don't match published outbreak paper | v2 vs v3 incompatibility | Re-run with matched MOB-suite version; document |
| Point-mutation panel coverage list flips between AMRFinderPlus minor releases | DB schema change | `amrfinder --list_organisms` and record the version |
| TB-Profiler bundled DB predates WHO 2nd edition | DB not updated | `tb-profiler update_tbdb` and verify catalogue edition |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why AMRFinderPlus, not RGI?" | AMRFinderPlus uses gene-family HMMs and NCBI-curated cutoffs that catch divergent novel variants without producing the Loose-tier noise of RGI; both are valid and `hamronize` lets the reviewer compare |
| "How were Group 3 WHO Mtb mutations handled?" | Reported as "Uncertain significance -- phenotypic DST recommended"; not collapsed to S |
| "What about heteroresistance?" | Read-based deep variant calling supplements assembly-based AMR for clinically critical drugs; report MAF |
| "Why not just trust ResFinder phenotype prediction?" | EUCAST/CLSI breakpoint year must be documented; rule-based phenotype prediction inherits its curation as a hidden dependency. Pair with explicit gene + class reporting |
| "Why long-read assembly for AMR?" | Short-read drafts fragment plasmid contigs and lose MGE / promoter context (e.g., IS*Ecp1* upstream of ampC; Tn4401 variants); long-read or hybrid is mandatory for any mobility / regulatory claim |
| "Why hAMRonization rather than tool-native outputs?" | Cross-tool comparison requires schema unification; PHA4GE is the public-health consensus |
| "Was the intrinsic vs acquired distinction considered?" | Yes -- `--organism` activates suppression of clinically inert intrinsic genes; reported separately |

## References

- Feldgarden M, Brover V, Haft DH et al (2021) AMRFinderPlus and the Reference Gene Catalog facilitate examination of the genomic links among antimicrobial resistance, stress response, and virulence. *Sci Rep* 11:12728. doi:10.1038/s41598-021-91456-0
- Bortolaia V, Kaas RS, Ruppe E et al (2020) ResFinder 4.0 for predictions of phenotypes from genotypes. *J Antimicrob Chemother* 75(12):3491-3500. doi:10.1093/jac/dkaa345
- Alcock BP, Huynh W, Chalil R et al (2023) CARD 2023: expanded curation, support for machine learning, and resistome prediction at the Comprehensive Antibiotic Resistance Database. *Nucleic Acids Res* 51(D1):D690-D699. doi:10.1093/nar/gkac920
- Phelan JE, O'Sullivan DM, Machado D et al (2019) Integrating informatics tools and portable sequencing technology for rapid detection of resistance to anti-tuberculous drugs. *Genome Med* 11:41. doi:10.1186/s13073-019-0650-x
- Hunt M, Bradley P, Lapierre SG et al (2019) Antibiotic resistance prediction for Mycobacterium tuberculosis from genome sequence data with Mykrobe. *Wellcome Open Res* 4:191. doi:10.12688/wellcomeopenres.15603.1
- Walker TM et al (CRyPTIC / WHO) (2022) The 2021 WHO catalogue of Mycobacterium tuberculosis complex mutations associated with drug resistance: a genotypic analysis. *Lancet Microbe* 3(4):e265-e273. doi:10.1016/S2666-5247(21)00301-3
- Allix-Béguec C et al (CRyPTIC) (2018) Prediction of susceptibility to first-line tuberculosis drugs by DNA sequencing. *N Engl J Med* 379(15):1403-1415. doi:10.1056/NEJMoa1800474
- Robertson J, Nash JHE (2018) MOB-suite: software tools for clustering, reconstruction and typing of plasmids from draft assemblies. *Microb Genom* 4(8):e000206. doi:10.1099/mgen.0.000206
- Carattoli A, Zankari E, García-Fernández A et al (2014) In silico detection and typing of plasmids using PlasmidFinder and plasmid multilocus sequence typing. *Antimicrob Agents Chemother* 58(7):3895-3903. doi:10.1128/AAC.02412-14
- Johansson MHK, Bortolaia V, Tansirichaiya S et al (2021) Detection of mobile genetic elements associated with antibiotic resistance in Salmonella enterica using a newly developed web tool: MobileElementFinder. *J Antimicrob Chemother* 76(1):101-109. doi:10.1093/jac/dkaa390
- Sherry NL, Horan KA, Ballard SA et al (2023) An ISO-certified genomics workflow for identification and surveillance of antimicrobial resistance. *Nat Commun* 14:60. doi:10.1038/s41467-022-35713-4
- Andersson DI, Nicoloff H, Hjort K (2019) Mechanisms and clinical relevance of bacterial heteroresistance. *Nat Rev Microbiol* 17(8):479-496. doi:10.1038/s41579-019-0218-1
- Liu YY, Wang Y, Walsh TR et al (2016) Emergence of plasmid-mediated colistin resistance mechanism MCR-1 in animals and human beings in China. *Lancet Infect Dis* 16(2):161-168. doi:10.1016/S1473-3099(15)00424-7

## Related Skills

- pathogen-typing - Strain context for AMR (Kleborate, MLST, cgMLST) feeds clonal interpretation of resistance dissemination
- transmission-inference - Outbreak transmission inference for resistant clones uses AMR + cgMLST jointly
- variant-surveillance - Lineage-level AMR-prevalence tracking for SARS-CoV-2-style surveillance (drug-resistance mutations in antiviral context)
- metagenomics/amr-detection - Community AMR / ARG quantification (NOT isolate-focused)
- variant-calling/variant-calling - Per-isolate SNP calling that feeds point-mutation panels
- variant-calling/filtering-best-practices - MAF threshold discipline for heteroresistance detection
- long-read-sequencing/long-read-alignment - Plasmid / promoter-context resolution for MGE-aware AMR
- comparative-genomics/whole-genome-alignment - Reference-based coordinate handling for point mutations
- clinical-databases/pharmacogenomics - Adjacent (host-side) pharmacogenetics, distinct from pathogen AMR
- workflows/somatic-variant-pipeline - End-to-end orchestration patterns (analogous to outbreak-pipeline workflows)
<!-- END FILE: epidemiological-genomics/amr-surveillance/SKILL.md -->

## 子目录：epidemiological-genomics/pathogen-typing

<!-- BEGIN FILE: epidemiological-genomics/pathogen-typing/SKILL.md -->
---
name: bio-epidemiological-genomics-pathogen-typing
description: Assigns isolate identity at the right resolution for the question -- ANI/Mash species triage, 7-locus MLST historical comparability, cgMLST/wgMLST outbreak resolution (chewBBACA, BIGSdb, Ridom SeqSphere, EnteroBase HierCC), in-silico serotyping (SISTR/SeqSero2 Salmonella, SerotypeFinder E. coli, Kaptive Klebsiella, SeroBA pneumococcus, spa+SCCmec S. aureus), and lineage callers (TB-Profiler/Mykrobe barcode for MTBC, Pangolin + Nextclade for SARS-CoV-2, PopPUNK GPSC for S. pneumoniae). Use when typing bacterial isolates for surveillance or outbreak investigation, choosing between cgMLST allele distance and core-SNP distance for cluster definition, harmonising calls across schemas/database versions, assigning MTBC lineage with the Napier 90-SNP barcode, calling Salmonella serovar via SISTR with monophasic Typhimurium awareness, running Pangolin UShER mode with pangolin-data version pinning, or selecting a typing resolution to match the surveillance question.
tool_type: mixed
primary_tool: chewBBACA
---

## Version Compatibility

Reference examples tested with: mlst 2.23+, chewBBACA 3.3+, SISTR 1.1+, SeqSero2 1.3+, SerotypeFinder 2.0+, Kleborate 3.0+, Kaptive 3.0+, SeroBA 1.0+, PopPUNK 2.7+, pangolin 4.3+ (pangolin-data 1.30+), nextclade 3.8+, tb-profiler 6.2+, mykrobe 0.13+, mash 2.3+, skani 0.2+, snippy 4.6+, snp-dists 0.8+, pandas 2.2+, BioPython 1.84+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Pangolin: `pangolin --all-versions` records pangolin + pangolin-data + scorpio + constellations
- Nextclade dataset: `nextclade dataset list --tag latest sars-cov-2`
- chewBBACA schema: schemas are versioned independently; record the schema source AND the schema-fetch date for any published call
- TB-Profiler bundled DB: `tb-profiler list_db` for the WHO catalogue edition currently bundled

If a tool reports an unexpected serovar / lineage / ST, the schema or barcode version is the first thing to check; introspect the installed package and database date before re-running.

# Pathogen Typing

**"What is this isolate, and is it the same as that one?"** -> Pick a typing resolution that matches the epidemiological question, then run the appropriate caller and report the call with explicit schema / database / lineage-barcode versions. Resolution mismatch is the single most common typing error -- using 7-locus MLST to investigate a 20-isolate outbreak (multiple unrelated isolates share an ST) and using cgMLST to track decade-long lineage trends (allele drift obscures the lineage signal) are equally wrong, in opposite directions.

- CLI: `mlst assembly.fa` -- 7-locus MLST via Seemann's mlst with PubMLST schemas
- CLI: `chewBBACA.py AlleleCall -i assemblies/ -g schema/ -o alleles/ --cpu 8` -- cgMLST allele profile
- CLI: `pangolin sequences.fasta --analysis-mode usher --all-versions` -- SARS-CoV-2 Pango lineage with version provenance
- CLI: `tb-profiler profile -1 r1.fq.gz -2 r2.fq.gz -p sample` -- MTBC lineage (Coll/Napier barcode) plus DR call
- Python: `pandas` + `snp-dists` for cluster definition with pathogen-specific thresholds

## The Single Most Important Modern Insight -- cgMLST and core-SNP distance answer different questions

cgMLST counts allele changes (one wobble within a 1-kb locus = 1 allelic difference, regardless of how many SNPs sit inside that allele) and is robust to small assembly artifacts; core-SNP counts every position and is sensitive to alignment / mapping artifacts but recovers higher resolution. The EFSA harmonised foodborne approach uses cgMLST for *Salmonella* / *Listeria* / *E. coli* (Salm cgMLST <=5 alleles = cluster; PulseNet *Listeria* <=4 alleles); UK / EU TB outbreak literature uses core-SNP with recombination masking (Walker 2013: <=12 SNPs = likely transmission; <=5 = recent). Mixing the two yields incompatible cluster definitions: the same 50-isolate outbreak under cgMLST may cluster as 1 group at threshold 5, under core-SNP as 3 groups at threshold 12. The output of pathogen-typing is not a single distance -- it is a distance metric, a threshold derived from a specific population, and a schema or reference version. All three must travel with the call.

## Algorithmic Taxonomy

| Method | Mechanism | Resolution | Strength | Fails when |
|--------|-----------|-----------|----------|------------|
| ANI / fastANI / skani | Pairwise nucleotide identity over orthologous regions | Species (>=95% ANI = same species) | Species-level QC; cross-genus is non-metric for Mash | Species below ~80% ANI; Mash distance violates triangle inequality |
| Mash (Ondov 2016 *Genome Biol* 17:132) | MinHash sketches; fast pairwise distances | Species triage | Seconds per pair; the rapid screening standard | Distance non-metric at low identity; ANI <80% unreliable |
| 7-locus MLST (Maiden 2013 *Nat Rev Microbiol* 11:728; Seemann mlst tool) | PubMLST allele lookup at 7 housekeeping loci | Sequence type | Historical comparability across decades | Insufficient resolution for outbreaks; multiple unrelated isolates may share ST |
| cgMLST (chewBBACA; BIGSdb; Ridom SeqSphere) | Allele lookup across ~1000-3000 core loci | Outbreak / multi-country surveillance | Allele-distance is robust to small mapping errors | Schema-version-dependent; cross-schema NON-comparable; missing-locus handling matters |
| wgMLST | Allele lookup across all genes including accessory | Highest typing resolution | Maximum resolution within schema | Even more schema-dependent than cgMLST |
| Core-SNP typing (snippy + snp-dists; Parsnp; Lyve-SET) | Reference-based SNP calling on core genome | Single-SNP resolution | Highest resolution; underlies most Mtb work | Reference-dependent; recombination must be masked for bacteria |
| HierCC (Zhou 2021 *Bioinformatics* 37:3645) | Hierarchical clustering on cgMLST at multiple thresholds (HC5, HC10, HC50, etc.) | Stable nomenclature across schema updates | Cross-schema-update stability for EnteroBase pathogens | Limited to EnteroBase organisms |
| PopPUNK GPSC (Lees 2019 *Genome Res* 29:304) | k-mer-based clustering with Gaussian mixture on core+accessory distance | Population cluster | Stable IDs across additions; scales to >100k genomes | Cluster membership of an individual isolate can shift as model is refined |
| Pangolin (O'Toole 2021 *Virus Evol* 7:veab064) | Phylogenetic placement (UShER) or ML classifier (pangoLEARN) | SARS-CoV-2 Pango lineage | Curated dynamic nomenclature; recombinant X-prefix designations | pangoLEARN deprecated mid-2023; lab-to-lab version skew silently flips lineage calls |
| Nextclade (Aksamentov 2021 *JOSS* 6:3773) | Reference-tree placement + clade calling + QC | Clade nomenclature + mutations + QC | Mutation reports + QC integrated; multi-pathogen datasets | Dataset version drift changes which mutations count as "lineage-defining" |
| TB-Profiler + Coll/Napier barcode (Phelan 2019; Coll 2014; Napier 2020) | Reference-based SNP call against H37Rv + barcode SNP set | MTBC lineage 1-9 + drug resistance | Integrated lineage + DST; supports Napier 90-SNP barcode covering lineages 7-9 | Pre-Napier 2020 barcodes miscall lineage 7-9 isolates |
| Mykrobe (Hunt 2019 *Wellcome Open Res* 4:191) | k-mer presence/absence panels | Species + AMR for TB / S. aureus / Salmonella | Fast; cross-check for TB-Profiler | Panel may lag WHO catalogue |
| SISTR (Yoshida 2016 *PLoS ONE* 11:e0147101) | cgMLST + ribosomal MLST + serovar inference | Salmonella serovar + antigenic formula | ~94% concordance with traditional sero-typing; monophasic-aware | Novel/rare serovars without reference panel; antigen-cluster regulatory mutations are silent |
| SeqSero2 (Zhang 2019 *AEM* 85:e01746-19) | k-mer + targeted-assembly for Salmonella | Salmonella serovar | Designed for low-coverage / fragmented data | Slightly different output schema than SISTR |
| SerotypeFinder (Joensen 2015 *J Clin Microbiol* 53:2410) | BLAST against O- and H-antigen biosynthesis genes | E. coli O:H | Standard for E. coli serotyping | Misses novel O / H types; fimH typing is separate |
| Kleborate + Kaptive (Lam 2021 *Nat Commun* 12:4188) | Integrated MLST + K/O typing + virulence (ICEKp / iuc / ybt / clb / iro) + AMR | Klebsiella surveillance | Hypervirulence vs classical distinction; K/O loci typed by Kaptive | Kaptive K-locus DB versioned; KL calls can flip between Kaptive v1 / v2 / v3 |
| spa + SCCmec (Harmsen 2003 *J Clin Microbiol* 41:5442; Kaya 2018 *mSphere* 3:e00612-17) | spa repeat-region typing + SCCmec cassette typing | S. aureus typing | Historical comparability; clinical surveillance | spa repeat array fragments at borderline read length; assembler-dependent |
| SeroBA (Epping 2018 *Microb Genom* 4:e000186) | k-mer-based serotyping from raw reads | S. pneumoniae serotype | 98% concordance; no assembly needed; runs on >=15x coverage | Vaccine replacement makes serotype the load-bearing surveillance unit |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| "Is this strain even what we think it is?" | Mash / skani ANI triage; ANI >=95% confirms species | 7-locus MLST cannot answer species; cgMLST schema may not load on wrong species |
| Routine *Salmonella* serotyping | SISTR (assembled) or SeqSero2 (low coverage / fragmented); flag monophasic 1,4,[5],12:i:- explicitly | Single tool without monophasic awareness; reporting Typhimurium when the antigen cluster is deleted |
| *Klebsiella* surveillance | Kleborate (integrates MLST + K/O via Kaptive + ICEKp virulence + AMR via AMRFinderPlus) | MLST + Kaptive + AMR run separately and not integrated -- missing hypervirulence call |
| *S. pneumoniae* surveillance | SeroBA serotype + PopPUNK GPSC; vaccine-replacement is the central post-PCV story | Reporting MLST ST without serotype (serotype IS the vaccine-actionable surveillance unit) |
| *S. aureus* typing | spa (Ridom) + SCCmec (SCCmecFinder) + MLST + clonal complex; flag CC8 USA300 / CC22 EMRSA-15 / CC30 EMRSA-16 / CC398 livestock | Just spa without CC; spa repeat assembly artifacts unflagged |
| *M. tuberculosis* lineage | TB-Profiler primary (Coll/Napier barcode) + Mykrobe cross-check; verify Napier 2020 90-SNP barcode (covers lineages 7-9) | Pre-Napier barcodes miscall L7-9; MIRU-VNTR is obsolete for new surveillance |
| SARS-CoV-2 lineage | Pangolin with `--analysis-mode usher` (UShER default since v4; pangoLEARN deprecated mid-2023) + Nextclade cross-check; document pangolin-data version | pangoLEARN alone; reporting lineage without pangolin-data version pin |
| Define outbreak cluster | cgMLST allele-distance with pathogen-tuned threshold (Salm <=5; *Listeria* PulseNet <=4; TB <=12 SNPs core; *C. difficile* <=2 SNPs core); cite the threshold's source population | Universal SNP threshold across pathogens (10x variation across taxa); applying Walker 2013 UK thresholds in high-transmission settings |
| Reproducible nomenclature across years | PopPUNK GPSC (S. pneumoniae) / Pangolin (SARS-CoV-2) / HierCC (EnteroBase pathogens) / SISTR serovar -- curated stable IDs | Raw cgMLST allele profile as the surveillance unit -- not stable across schema updates |
| Multi-lab cross-comparison | Same schema source AND same schema version AND same tool version; Pathogenwatch / EnteroBase shared platform | Locally computed cgMLST profiles compared across labs without schema versioning |

Methodology evolves; before any high-stakes typing report, verify Pangolin's current default analysis-mode and the Napier barcode currently bundled in TB-Profiler.

## Running 7-Locus MLST and cgMLST

**Goal:** Produce reproducible ST and cgMLST allele-distance calls for a cohort of bacterial isolates, with schema versioning preserved for cross-lab comparison.

**Approach:** Run Seemann's `mlst` for the 7-locus baseline (uses bundled PubMLST schemas); for cgMLST, fetch the schema explicitly with `chewBBACA.py DownloadSchema` (records the source and date), then `AlleleCall`, then `ExtractCgMLST` with the per-organism missing-locus threshold; compute allele distances on the pairwise-complete intersection of called loci.

```bash
mlst --threads 8 assemblies/*.fa > cohort.mlst.tsv

chewBBACA.py DownloadSchema \
    -sp "Salmonella enterica" \
    -sc cgMLST \
    -o schema_dir
SCHEMA_DATE=$(date -u +%Y-%m-%d)

chewBBACA.py AlleleCall \
    -i assemblies/ \
    -g schema_dir/cgMLST \
    -o alleles_out/ \
    --cpu 8

chewBBACA.py ExtractCgMLST \
    -i alleles_out/results_alleles.tsv \
    -o cgmlst_profile.tsv \
    --threshold 0.95

echo "schema_source: chewBBACA SalmonellaEnterica cgMLST" > cgmlst_profile.metadata
echo "schema_fetched: ${SCHEMA_DATE}" >> cgmlst_profile.metadata
```

`AlleleCall` output uses special codes: `LNF` (locus not found), `PLOT` (truncated), `NIPH` (non-informative paralog), `ASM` (allele small/short), `ALM` (allele large), and asterisk (new allele). These are MISSING DATA. Counting "0" or "-" against another "0" or "-" as 1 allelic difference is a quiet correctness bug that affects most cgMLST cluster definitions outside specialist labs.

## SNP-Based Outbreak Cluster Definition

**Goal:** Identify isolates within an outbreak threshold using core-SNP distances on a recombination-aware alignment, with the pathogen-specific threshold cited from its source population.

**Approach:** Snippy against a high-quality reference; `snippy-core` to extract core SNPs; for bacteria, Gubbins to mask recombinant tracts before counting (otherwise apparent SNP distance is inflated by recombination); `snp-dists` for pairwise distance matrix; apply the published pathogen-specific threshold (citing Walker 2013 for TB, Eyre 2013 for *C. difficile*, EFSA convention for *Salmonella*).

```bash
for r1 in reads/*_R1.fq.gz; do
    sample=$(basename "${r1}" _R1.fq.gz)
    r2="reads/${sample}_R2.fq.gz"
    snippy --outdir snippy_out/${sample} --R1 "${r1}" --R2 "${r2}" --reference reference.fa --cpus 8
done

snippy-core --ref reference.fa --prefix core snippy_out/*

run_gubbins.py --prefix gubbins core.full.aln

snp-dists -c gubbins.filtered_polymorphic_sites.fasta > cohort.snp_dists.csv
```

`run_gubbins.py` input MUST be `core.full.aln` (full-position alignment with reference). Passing `core.aln` (variable positions only) produces wrong recombination calls because Gubbins cannot estimate background SNP density without invariant positions.

## Lineage Calling for Mtb and SARS-CoV-2

**Goal:** Assign MTBC lineage via the Napier 2020 barcode or SARS-CoV-2 Pango lineage via UShER placement, with explicit version pinning so the call is reproducible.

**Approach:** TB-Profiler bundles the Coll 2014 + Napier 2020 barcode and reports lineage 1-9 (Napier 2020 added lineages 7-9 that older 62-SNP barcodes miss); Pangolin with `--analysis-mode usher` performs phylogenetic placement on the daily-updated UShER tree and is preferred over pangoLEARN since v4 (Pongmoragot 2024 *Virus Evol* 10:vead085); always record `pangolin --all-versions` output alongside the lineage call.

```bash
tb-profiler profile -1 reads_R1.fq.gz -2 reads_R2.fq.gz -p sample --dir tbp_out
mykrobe predict --sample sample --species tb --output sample.mykrobe.json --format json reads_R1.fq.gz reads_R2.fq.gz

pangolin sequences.fasta --analysis-mode usher --outfile lineage_report.csv
pangolin --all-versions > pangolin_versions.txt

nextclade dataset get --name sars-cov-2 --output-dir nc_dataset/sars-cov-2
NC_DATASET_TAG=$(jq -r '.tag' nc_dataset/sars-cov-2/pathogen.json)

nextclade run \
    --input-dataset nc_dataset/sars-cov-2 \
    --output-tsv nextclade.tsv \
    --output-json nextclade.json \
    sequences.fasta

echo "nextclade_dataset_tag: ${NC_DATASET_TAG}" > nextclade.metadata
```

## Per-Method Failure Modes

### chewBBACA missing-locus codes counted as allelic differences

**Trigger:** A naive cgMLST distance computation that treats LNF / PLOT / NIPH / ASM / ALM / "0" / "-" as integer alleles and counts them against other missing codes.

**Mechanism:** chewBBACA output uses special codes for missing or paralogous loci. The pairwise allele distance must be computed on the intersection of called loci, not the union. Treating two LNFs as "same allele" (=0 difference) or as "different alleles" (=1 difference) are both wrong; the locus must be excluded from the comparison.

**Symptom:** Outbreak cluster definition flips depending on completeness of the assemblies; samples with more missing data appear artificially close to each other (if missing-vs-missing counts 0) or far from everyone (if missing-vs-allele counts 1).

**Fix:** Use chewBBACA's `ExtractCgMLST` with a `--threshold` (typically 0.95) to drop loci called in fewer than that fraction of samples; for the pairwise distance, restrict to loci called in BOTH samples (pairwise-complete) and report the number of loci compared alongside the distance.

### Pangolin lineage call flips between lab A (older pangolin-data) and lab B (current)

**Trigger:** Two labs submit the same consensus genome to Pangolin with different pangolin-data versions; the lineage call differs (e.g., BA.2 vs BA.2.86 vs JN.1).

**Mechanism:** Lineage designation happens through pango-designation GitHub issues -- community-driven, often days-to-weeks before pangolin-data releases include the lineage. During this window, the same genome is callable as the parent lineage (older pangolin-data) or the child (current pangolin-data). pangolin-data is updated weekly; lab-to-lab version skew is routine.

**Symptom:** Cross-lab lineage prevalence comparisons over time show implausible jumps that coincide with pangolin-data release dates rather than biology.

**Fix:** Pin pangolin-data version explicitly with `pangolin --all-versions` recorded alongside every call. For published or regulatory output, re-run the WHOLE archive against a single pangolin-data version before reporting. Comparing today's BA.2.86 call to last month's "Unassigned" call is invalid.

### MTBC lineage 7-9 miscalled by pre-Napier barcode

**Trigger:** TB-Profiler / Mykrobe running an older bundled barcode (Coll 2014 62-SNP, pre-2020 builds); isolate is from Ethiopia, Rwanda, or East Africa.

**Mechanism:** The Coll 2014 62-SNP barcode covers lineages 1-7 but predates the formal designation of lineages 8 (Rwanda) and 9. The Napier 2020 90-SNP barcode (Napier *Genome Med* 12:114) adds these and refines L4 sublineages. An older bundled barcode silently maps lineage 8 / 9 isolates to "unknown" or to a nearest-barcode-match L4 sub-lineage based on partial SNPs.

**Symptom:** Cross-lab Mtb surveillance dataset shows Ethiopia / Rwanda isolates as a mix of "unknown" and unexpected L4 sublineages.

**Fix:** Verify the bundled barcode version (`tb-profiler list_db`); update to the Napier 2020 barcode or later before any lineage-stratified analysis. Re-run historical Mtb data against the current barcode whenever the barcode is updated.

### Beijing-lineage Mtb literature based on spoligotype, not WGS sublineage

**Trigger:** Citing pre-2014 "Beijing family" findings (hypervirulence claims, vaccine-escape claims, faster-evolution claims) as if they apply to a single modern WGS sublineage.

**Mechanism:** Pre-WGS, the *Mtb* "Beijing" family was defined by spoligotype pattern (absence of DR spacers 1-34, presence of 35-43). WGS revealed Beijing is a paraphyletic grouping containing multiple sublineages with distinct phenotypes (modern Beijing = lineage 2.2.1.1; ancestral Beijing = 2.2.1.2; proto-Beijing = 2.1). Much of the pre-2014 Beijing literature was based on the spoligotype-defined paraphyletic group.

**Symptom:** Beijing-as-a-monolith conclusions inappropriately applied to modern WGS-typed isolates that may fall in different sublineages of L2.

**Fix:** Always specify the WGS sublineage (e.g., "2.2.1.1 modern Beijing", "2.2.1.2 ancestral Beijing") rather than "Beijing". Treat pre-2014 Beijing claims as hypotheses to be re-validated on WGS-typed cohorts.

### Mash distance used to cluster genomes below 80% ANI

**Trigger:** Mash-distance hierarchical clustering of distantly related genomes (multi-genus or low-identity comparisons).

**Mechanism:** Mash distance (Ondov 2016 *Genome Biol* 17:132) is a Jaccard-derived estimator of mutation rate, validated for ANI >=80% (the Mash docs state 95% confidence at ANI >=90%). Below that, the Mash distance becomes non-metric -- A-B + B-C can be < A-C -- and clustering algorithms that assume metric distances produce undefined output.

**Symptom:** Cross-genus or low-identity comparison clusters do not match phylogenetic expectations; the same cluster definition is unstable to addition of new genomes.

**Fix:** Use Mash only within the validated ANI range (>=80%, ideally >=90%). For cross-genus or low-identity comparisons use AAI or ANI-from-alignment (`skani`, `pyani`). Document the ANI range of the cohort before computing any Mash-based distance.

### Cross-schema cgMLST distances pooled as if comparable

**Trigger:** Combining cgMLST distances from a chewBBACA local schema with distances from a Ridom SeqSphere schema in the same outbreak comparison.

**Mechanism:** Ridom SeqSphere, chewBBACA-built schemas, and EnteroBase schemas are independently curated and use different locus sets and different allele numbering. A "cgMLST distance of 5" between two isolates does NOT equal a "cgMLST distance of 5" under a different schema.

**Symptom:** Multi-country outbreak comparison reports irreconcilable cluster definitions; the same isolate pair appears in-cluster in one lab and out-of-cluster in another.

**Fix:** Document schema source AND schema-fetch date for every cgMLST profile; do not pool distances across schema sources. For multi-country collaboration, agree on a single schema (typically EnteroBase HierCC for *Salmonella* / *E. coli* / *Listeria*) at the outset.

### K-locus typing flips between Kaptive versions

**Trigger:** Comparing *K. pneumoniae* K-locus prevalence between studies that used different Kaptive database versions.

**Mechanism:** The Kaptive K-locus DB has been versioned multiple times since release; K-locus calls have flipped (KL1 / KL2 boundary refinements; KL149+ additions) between Kaptive v1 and v2. Kaptive v3 (2024) added O-locus typing and an L-locus scheme.

**Symptom:** Longitudinal K-locus prevalence trend has implausible jumps coinciding with Kaptive release dates rather than biology.

**Fix:** Document Kleborate AND Kaptive version with every K/O call. For longitudinal trend analysis, re-run all historical assemblies against a single Kaptive version.

## Reconciliation: When Typing Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Pangolin "BA.2.86", Nextclade clade "23I" | Equivalent at different resolutions -- BA.2.86 is within 23I | Report both; Pango lineage for sub-clade resolution |
| Pangolin "BA.5.2", Nextclade "Unassigned" | Nextclade dataset older than pangolin-data; OR Nextclade QC failed | Update Nextclade dataset; re-run; inspect QC fields |
| Pangolin UShER and pangoLEARN disagree | pangoLEARN is the deprecated decision-tree classifier (deprecated mid-2023) | Trust UShER call |
| SISTR "monophasic Typhimurium 1,4,[5],12:i:-", slide agglutination "Typhimurium" | fljB gene deleted in monophasic variant; slide agglutination cannot detect | Trust genome call; flag for confirmatory testing if surveillance requires |
| cgMLST cluster definition flips between two schemas | Different locus sets; non-comparable | Pick one schema for the entire analysis; document |
| TB lineage call differs between TB-Profiler and Mykrobe | Different bundled barcode versions; one may predate Napier 2020 | Update both; if disagreement persists, manual barcode SNP inspection |
| Two consecutive pangolin-data releases call the same consensus differently | Lineage definitions revised between releases | Pin pangolin-data; re-run whole archive on dataset update |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| Mash / ANI species boundary | >=95% ANI | ANI species-delineation convention |
| Mash distance validity range | >=80% ANI (>=90% for 95% confidence) | Ondov 2016 *Genome Biol* 17:132 |
| cgMLST cluster -- *Salmonella* (chewBBACA Salm scheme) | <=5 allelic differences | EFSA harmonised approach |
| cgMLST cluster -- *Listeria monocytogenes* (PulseNet) | <=4 allelic differences | PulseNet protocol convention |
| cgMLST cluster -- *E. coli* (EnteroBase) | <=10 allelic differences (STEC outbreak) | EnteroBase convention |
| Core SNP -- *M. tuberculosis* | <=5 SNPs (recent transmission); <=12 SNPs (likely transmission) | Walker 2013 *Lancet Infect Dis* 13:137 (UK low-transmission setting) |
| Core SNP -- *Staphylococcus aureus* | <=15 SNPs (within hospital outbreak); <=40 SNPs (broader temporal cluster) | Coll 2017 *Clin Infect Dis* 65:1781 |
| Core SNP -- *Klebsiella pneumoniae* (KPC outbreak) | <=21 SNPs | Snitkin 2012 *Sci Transl Med* 4:148ra116 |
| Core SNP -- *Clostridioides difficile* (recombination-masked) | <=2 SNPs (likely direct transmission); <=10 (plausible within 6 months) | Eyre 2013 *NEJM* 369:1195 |
| Core SNP -- *Neisseria gonorrhoeae* | <=25 SNPs (transmission) | UKHSA STI framework |
| SARS-CoV-2 cluster definition | NOT defined by SNP alone; combine 0-2 SNPs + epi link + sampling window | SARS-CoV-2 within-host diversity literature |
| chewBBACA cgMLST extraction completeness | 0.95 (drop loci called in <95% of samples) | chewBBACA convention |
| SeroBA minimum coverage | >=15x | Epping 2018 *Microb Genom* 4:e000186 |

CRITICAL: a number from one pathogen does NOT transfer to another. Substitution rate, recombination, host range, generation interval, and within-host diversity vary by 100x across pathogens. Always cite the threshold's source population, especially for Walker 2013 (UK low-transmission setting) which routinely inflates apparent recent-transmission rates by 2-5x in high-burden settings.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Outbreak split into spurious clusters | cgMLST missing-locus codes counted as allelic differences | Restrict to pairwise-complete loci |
| Lineage prevalence shows implausible jump | pangolin-data version drift | Pin pangolin-data; re-run archive |
| Mtb lineage call "unknown" for East African isolate | Pre-Napier barcode | Update to Napier 2020 |
| Salmonella sample called "Typhimurium" when antigen cluster deleted | Tool did not flag monophasic variant | Use SISTR or SeqSero2 with explicit monophasic check |
| `nextclade run --input-dataset` rejected | v2 syntax in v3 | v3 uses `--input-dataset` for pre-downloaded folder; verify `nextclade --version` |
| `pangolin --inference usher` not recognised | Flag is `--analysis-mode usher` | Use `--analysis-mode usher` |
| chewBBACA fails on assembly with broken loci | Schema BSR cutoff too strict; assembly too fragmented | Document quality; consider re-assembly with long reads |
| GPSC cluster differs between studies | PopPUNK model updated; individual cluster membership can shift | Re-run PopPUNK against current reference DB before comparison |
| Mash hierarchical clustering unstable | Cohort spans wide ANI range; below validity threshold | Use ANI-from-alignment (skani / pyANI) for cross-genus comparisons |
| MOB-suite plasmid context conflicts with cgMLST cluster | cgMLST is chromosome-focused; plasmid distance is independent | Report both with framing |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why cgMLST and not core-SNP?" | EFSA harmonised foodborne uses cgMLST; cross-lab comparability via shared schema. For outbreak-internal who-infected-whom, core-SNP supplements |
| "What threshold was used, and on what population?" | Cite Walker 2013 / Eyre 2013 / EFSA per pathogen; caveat the population for non-universal thresholds |
| "How were missing cgMLST loci handled?" | Pairwise-complete distance; locus must be called in BOTH samples to count |
| "Pangolin version?" | `pangolin --all-versions` recorded; re-run on dataset update |
| "Why TB-Profiler over Mykrobe?" | TB-Profiler is primary (WHO catalogue integration + Napier barcode); Mykrobe is cross-check on R/XDR calls |
| "Was the Napier 2020 barcode checked?" | Verified `tb-profiler list_db`; lineage 7-9 callable |
| "Was the Beijing-as-monolith literature cited?" | Disaggregated to WGS sublineage (2.2.1.1 modern / 2.2.1.2 ancestral); pre-2014 Beijing claims treated as hypotheses |
| "Multi-country outbreak: harmonised schema?" | EnteroBase HierCC for *Salmonella* / *E. coli* / *Listeria*; documented schema source + date |

## References

- Maiden MCJ, van Rensburg MJJ, Bray JE et al (2013) MLST revisited: the gene-by-gene approach to bacterial genomics. *Nat Rev Microbiol* 11(10):728-736. doi:10.1038/nrmicro3093
- Silva M, Machado MP, Silva DN et al (2018) chewBBACA: A complete suite for gene-by-gene schema creation and strain identification. *Microb Genom* 4(3):e000166. doi:10.1099/mgen.0.000166
- Zhou Z, Charlesworth J, Achtman M (2021) HierCC: a multi-level clustering scheme for population assignments based on core genome MLST. *Bioinformatics* 37(20):3645-3646. doi:10.1093/bioinformatics/btab234
- Yoshida CE, Kruczkiewicz P, Laing CR et al (2016) The Salmonella In Silico Typing Resource (SISTR). *PLoS ONE* 11(1):e0147101. doi:10.1371/journal.pone.0147101
- Zhang S, den Bakker HC, Li S et al (2019) SeqSero2: rapid and improved Salmonella serotype determination using whole-genome sequencing data. *Appl Environ Microbiol* 85(23):e01746-19. doi:10.1128/AEM.01746-19
- Joensen KG, Tetzschner AMM, Iguchi A et al (2015) Rapid and easy in silico serotyping of Escherichia coli isolates by use of whole-genome sequencing data. *J Clin Microbiol* 53(8):2410-2426. doi:10.1128/JCM.00008-15
- Lam MMC, Wick RR, Watts SC et al (2021) A genomic surveillance framework and genotyping tool for Klebsiella pneumoniae and its related species complex. *Nat Commun* 12:4188. doi:10.1038/s41467-021-24448-3
- Lees JA, Harris SR, Tonkin-Hill G et al (2019) Fast and flexible bacterial genomic epidemiology with PopPUNK. *Genome Res* 29(2):304-316. doi:10.1101/gr.241455.118
- Epping L, van Tonder AJ, Gladstone RA et al (2018) SeroBA: rapid high-throughput serotyping of Streptococcus pneumoniae from whole genome sequence data. *Microb Genom* 4(7):e000186. doi:10.1099/mgen.0.000186
- Harmsen D, Claus H, Witte W et al (2003) Typing of methicillin-resistant Staphylococcus aureus in a university hospital setting by using novel software for spa repeat determination and database management. *J Clin Microbiol* 41(12):5442-5448. doi:10.1128/JCM.41.12.5442-5448.2003
- Kaya H, Hasman H, Larsen J et al (2018) SCCmecFinder, a web-based tool for typing of staphylococcal cassette chromosome mec in Staphylococcus aureus using whole-genome sequence data. *mSphere* 3(1):e00612-17. doi:10.1128/mSphere.00612-17
- Coll F, McNerney R, Guerra-Assunção JA et al (2014) A robust SNP barcode for typing Mycobacterium tuberculosis complex strains. *Nat Commun* 5:4812. doi:10.1038/ncomms5812
- Coll F, Harrison EM, Toleman MS et al (2017) Longitudinal genomic surveillance of MRSA in the UK reveals transmission patterns in hospitals and the community. *Clin Infect Dis* 65(11):1781-1789. doi:10.1093/cid/cix645
- Snitkin ES, Zelazny AM, Thomas PJ et al (2012) Tracking a hospital outbreak of carbapenem-resistant Klebsiella pneumoniae with whole-genome sequencing. *Sci Transl Med* 4(148):148ra116. doi:10.1126/scitranslmed.3004129
- Napier G, Campino S, Merid Y et al (2020) Robust barcoding and identification of Mycobacterium tuberculosis lineages for epidemiological and clinical studies. *Genome Med* 12(1):114. doi:10.1186/s13073-020-00817-3
- Phelan JE, O'Sullivan DM, Machado D et al (2019) Integrating informatics tools and portable sequencing technology for rapid detection of resistance to anti-tuberculous drugs. *Genome Med* 11:41. doi:10.1186/s13073-019-0650-x
- Hunt M, Bradley P, Lapierre SG et al (2019) Antibiotic resistance prediction for Mycobacterium tuberculosis from genome sequence data with Mykrobe. *Wellcome Open Res* 4:191. doi:10.12688/wellcomeopenres.15603.1
- Walker TM, Ip CLC, Harrell RH et al (2013) Whole-genome sequencing to delineate Mycobacterium tuberculosis outbreaks: a retrospective observational study. *Lancet Infect Dis* 13(2):137-146. doi:10.1016/S1473-3099(12)70277-3
- Eyre DW, Cule ML, Wilson DJ et al (2013) Diverse sources of C. difficile infection identified on whole-genome sequencing. *N Engl J Med* 369(13):1195-1205. doi:10.1056/NEJMoa1216064
- Ondov BD, Treangen TJ, Melsted P et al (2016) Mash: fast genome and metagenome distance estimation using MinHash. *Genome Biol* 17:132. doi:10.1186/s13059-016-0997-x
- O'Toole Á, Scher E, Underwood A et al (2021) Assignment of epidemiological lineages in an emerging pandemic using the pangolin tool. *Virus Evol* 7(2):veab064. doi:10.1093/ve/veab064
- Aksamentov I, Roemer C, Hodcroft EB, Neher RA (2021) Nextclade: clade assignment, mutation calling and quality control for viral genomes. *J Open Source Softw* 6(67):3773. doi:10.21105/joss.03773
- Pongmoragot J, Pearson C, Borg ML et al (2024) Comparison of UShER-based and pangoLEARN-based Pangolin lineage assignments for SARS-CoV-2 sequences. *Virus Evol* 10(1):vead085. doi:10.1093/ve/vead085

## Related Skills

- amr-surveillance - Strain context complements AMR; Kleborate integrates typing + AMR for Klebsiella
- transmission-inference - SNP-cluster definition from cgMLST or core-SNP feeds outbreak transmission inference
- phylodynamics - Time-scaled tree from typed isolates for R_e estimation
- variant-surveillance - SARS-CoV-2 Pango / Nextclade lineage assignment overlaps; this skill owns the typing call, variant-surveillance owns longitudinal frequency tracking
- comparative-genomics/pangenome-analysis - Core / accessory genome partitioning underlies cgMLST schema design
- comparative-genomics/whole-genome-alignment - Core-genome alignment for SNP-typing
- variant-calling/vcf-basics - Per-isolate VCF for SNP-typing
- variant-calling/variant-calling - Per-isolate variant calling that feeds cgMLST and SNP-typing
- read-alignment/bwa-alignment - Read mapping upstream of variant calling and snippy
- alignment/multiple-alignment - Multiple sequence alignment for core SNP extraction
- database-access/entrez-fetch - Reference genome retrieval for snippy / Snippy-core
- metagenomics/strain-tracking - Community strain tracking via Kraken2 / StrainPhlAn (NOT isolate-focused)
<!-- END FILE: epidemiological-genomics/pathogen-typing/SKILL.md -->

## 子目录：epidemiological-genomics/phylodynamics

<!-- BEGIN FILE: epidemiological-genomics/phylodynamics/SKILL.md -->
---
name: bio-epidemiological-genomics-phylodynamics
description: Estimates time-scaled phylogenies, molecular-clock rates, effective reproduction number R_e, and population dynamics from dated pathogen genomes using TreeTime (maximum-likelihood) and BEAST2 (Bayesian; strict/relaxed clocks; coalescent, Bayesian-Skyline, Skygrid, Birth-Death-Skyline, and sampled-ancestor priors; structured coalescent via MASCOT). Covers root-to-tip clock QC via TempEst, date-randomisation tests, recombination masking via Gubbins/ClonalFrameML before clock inference for recombining bacteria, BDSKY origin-vs-rootHeight pitfalls, sampling-bias correction, multi-chain convergence diagnostics, and reconciling phylodynamic R_e with case-based R_t. Use when dating outbreak origins, estimating substitution rates, inferring R_e through time, building time-calibrated Nextstrain Augur trees, choosing between strict and relaxed clocks, fitting Birth-Death-Skyline models, diagnosing temporal-signal failure, running MASCOT for structured-population analyses, or using UShER for pandemic-scale placement.
tool_type: mixed
primary_tool: BEAST2
---

## Version Compatibility

Reference examples tested with: BEAST 2.7.6+, BDSKY 1.5+, BEASTLabs 2.0+, feast 9.5+, ORC 1.1.2+, MASCOT 3.0+, BEAGLE 4.0+, TreeTime 0.11+, IQ-TREE 2.3.6+, Gubbins 3.3+, ClonalFrameML 1.13+, UShER 0.6+, matUtils 0.6+, BactDating 1.1+ (R), bdskytools 1.1+ (R), coda 0.19+ (R), ape 5.8+ (R), ggplot2 3.5+, BioPython 1.84+, dendropy 4.6+, baltic 0.2+.

Before using code patterns, verify installed versions match. If versions differ:
- BEAST: `beast -version`; `packagemanager -list` for BEAST2 packages and versions
- Python: `pip show treetime`; `help(treetime.TreeTime)`
- R: `packageVersion('bdskytools')`; `?bdskytools::bdskytools_plot`
- CLI: `gubbins --version`; `iqtree --version`; `clonalframeml --version`

If BEAST2 throws `IllegalArgumentException` on XML load, the BDSKY / feast / BEASTLabs minor version probably moved; check the XML against the installed package's example XML in `~/beast/examples/`. BEAST2 XML is NOT robust across minor releases; pin the BEAST package version in any published analysis.

# Phylodynamics

**"How fast is this outbreak growing, and when did it start?"** -> Combine a dated set of pathogen genomes with a molecular-clock model to time-scale the phylogeny, then fit a population-dynamic model (constant / exponential / Bayesian Skyline / BICEPS / Birth-Death-Skyline) to read off R_e, growth rate, and origin date. Choice of clock (strict vs UCLN vs ORC) and tree prior (BSP coalescent vs BICEPS vs BDSKY birth-death) is load-bearing; the same data can yield different R_e under different priors. For bacterial pathogens, recombination MUST be masked first; running BEAST on a *Streptococcus pneumoniae* or *E. coli* core-genome alignment without Gubbins / ClonalFrameML inflates the clock rate 2-5x and the date-randomisation test is NOT a sufficient guard.

- CLI: `treetime --tree raw.nwk --aln aln.fasta --dates dates.tsv --coalescent skyline --clock-filter 4` -- fast ML phylodynamics
- Java/CLI: BEAST2 with BDSKY XML (BEAUti-generated) -- full Bayesian birth-death-skyline with R_e per epoch
- CLI: `gubbins --prefix gubbins core.full.aln` -- recombination masking before bacterial clock inference
- R: `bdskytools::bdskytools_plot` for BDSKY post-processing; `BactDating` for fast Bayesian dating after Gubbins

## The Single Most Important Modern Insight -- Recombination passed unmasked into clock inference inflates the clock rate 2-5x and breaks every downstream estimate

The date-randomisation test is NOT a guard against unmasked recombination. For any recombining bacterium (*S. pneumoniae*, *N. gonorrhoeae*, *E. coli*, *Klebsiella pneumoniae*, *Campylobacter*, *Helicobacter pylori*), run Gubbins (Croucher 2015 *NAR* 43:e15) or ClonalFrameML (Didelot & Wilson 2015 *PLoS Comput Biol* 11:e1004041) on the core-SNP alignment FIRST, rebuild the tree on the recombination-masked alignment, THEN run TreeTime / BEAST. Only *M. tuberculosis* and a handful of clonal pathogens are exempt -- and even those benefit from a recombination check on cross-lineage analyses. The Mostowy 2017 *Mol Biol Evol* 34:1167 fastGEAR paper documents the limits of mask-based approaches for highly recombinogenic species; for those (*N. gonorrhoeae*, *S. pneumoniae* lineages with strong recombination), residual signal persists post-masking and biases downstream R_e estimates downward. Second-order insight: Volz & Frost 2014 *J R Soc Interface* 11:20140945 showed that BEAST coalescent priors are biased under realistic preferential sampling; BDSKY models the sampling proportion explicitly and is the correct tool when sampling rate varies; MASCOT-Skyline / MASCOT-GLM (Müller 2018 *Bioinformatics* 34:3843) further correct for sampling-deme covariation. Third-order insight: Featherstone & Duchêne 2023 *Mol Biol Evol* 40:msad132 quantified that for shallow trees with many samples, sampling times dominate over sequence information for R_e inference -- biased sampling drives biased R_e estimates regardless of how much sequence data is added.

## Algorithmic Taxonomy

| Tool / model | Mechanism | Outputs | Strength | Fails when |
|--------------|-----------|---------|----------|------------|
| TreeTime ML (Sagulenko 2018 *Virus Evol* 4:vex042) | ML joint optimisation of clock + dates with optional coalescent skyline prior | Time-scaled tree + clock rate + root-to-tip regression | 100-1000x faster than BEAST; ideal for outbreak-scale data | Strict-clock assumption; no posterior; no R_e directly |
| BEAST2 + BICEPS (Bouckaert 2022 *Syst Biol* 71:1549) | Bayesian skyline with analytic Ne integration per epoch and new tree-flexing operators | Ne(t) posterior | Modern default skyline; weeks-of-BSP becomes hours | Replaces BSP for many use cases; check current BEAST2 tutorials |
| BEAST2 + BDSKY (Stadler 2013 *PNAS* 110:228) | Birth-death-skyline with explicit sampling | R_e(t), become-uninfectious rate, sampling proportion | Direct R_e estimation | `origin` vs `rootHeight` confusion; rho-and-turnover unidentifiability with flat priors (Legried & Terhorst 2022 *PNAS* 119:e2119513119) |
| BEAST2 + MASCOT (Müller 2018 *Bioinformatics* 34:3843) | Marginal-approximation structured coalescent | Per-deme Ne + migration | Correct for structured sampling; replaces biased DTA (De Maio 2015 *PLoS Genet* 11:e1005421) | Migration unidentifiable with <20 sequences per deme |
| BEAST2 + MASCOT-Skyline / MASCOT-GLM | Time-varying migration with covariates | Migration-rate trajectories tied to predictors | Sampling-aware; addresses Volz & Frost 2014 sampling bias | ~10x slower than DTA; many users still default to DTA |
| BEAST2 + Sampled-Ancestor BDSKY | BDSKY with internal-node sampling | R_e + ancestral / longitudinal samples | Right for ancient-DNA, within-host longitudinal sampling | Specialist parameterisation |
| BactDating (Didelot 2018 *NAR* 46:e134) | Bayesian Poisson / mixedgamma / relaxedgamma clock on a fixed tree | Time-scaled tree + clock rate posterior | Fast Bayesian dating after Gubbins; right for large bacterial trees | `mixedgamma` mixes poorly; `poisson` is the cleaner default |
| Gubbins (Croucher 2015 *NAR* 43:e15) | Sliding-window elevated SNP density detection | Recombination-masked alignment + recombination GFF | Standard for clonal bacterial alignments | Cannot detect ancient recombination; mis-masks mutation hotspots |
| ClonalFrameML (Didelot & Wilson 2015 *PLoS Comput Biol* 11:e1004041) | Coalescent-with-recombination model on a fixed tree | Recombination-masked alignment + r/m | Model-based alternative to Gubbins | Slow on large trees |
| UShER + matUtils (Turakhia 2021 *Nat Genet* 53:809) | Parsimony placement on a daily-updated mutation-annotated tree | Subtrees, lineage assignments, RIPPLES recombination calls | Pandemic-scale (millions of genomes) | Parsimony branch lengths systematically shorter than ML; re-estimate branch lengths before downstream R_e |
| TempEst (Rambaut 2016 *Virus Evol* 2:vew007) | Root-to-tip linear regression | Clock signal R^2 | First-line temporal-signal diagnostic | Slope can be artificially good with biased sampling |
| Date randomisation (Ramsden 2009 *Mol Biol Evol* 26:143; Duchêne 2015 *Mol Biol Evol* 32:1895) | Shuffle dates, compare clock-rate estimate | Pass / fail | Detects spurious clock signal | Can "pass" with narrow sampling windows (false negative) |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| "Estimate Ne(t) for this virus" | BEAST2 + BICEPS (or Skygrid if BICEPS unavailable) | Constant coalescent without checking flatness; BSP if BICEPS available (BSP mixes poorly) |
| "Estimate R_e from sequences" | BEAST2 + BDSKY with sampling-process explicit; document sampling proportion per epoch | BSP-style Ne -> R_e conversion via Wallinga-Lipsitch loses sampling information |
| "Multi-deme analysis with migration" | BEAST2 + MASCOT for <=10 demes with >=20 sequences each | Exact structured coalescent (intractable >5 demes); BEAST DTA (Lemey 2009) is sampling-biased |
| "Pandemic-scale (>10k sequences)" | UShER + matUtils for placement; TreeTime for dates; BDSKY on lineage-specific subsets | Full BEAST on full dataset is intractable; using UShER branch lengths directly biases R_e |
| "Date a bacterial tree" | Snippy -> Gubbins -> IQ-TREE -> BactDating OR BEAST2; recombination mask FIRST | Skipping recombination masking inflates the clock rate 2-5x |
| "Date a fast-evolving virus" | TreeTime (Nextstrain pipeline) for routine; BEAST2 + UCLN for headline analyses | Strict clock by default underestimates rate variation on shallow trees |
| "Test for temporal signal" | TempEst root-to-tip first (R^2 >= 0.3 minimum); date-randomisation as secondary check | Skipping the diagnostic; trusting date-randomisation alone (can pass with narrow window) |
| "Reconcile phylodynamic R_e with case R_t" | Report both with explicit assumptions; investigate disagreement (sampling bias, lineage-specific signal) | Reporting one as "the" R_e |
| "Bacterial outbreak phylogenetics start-to-finish" | snippy + snippy-core -> Gubbins (on `core.full.aln`) -> IQ-TREE -> BactDating or BEAST2 + BDSKY | Skipping Gubbins; running Gubbins on `core.aln` instead of `core.full.aln` |
| "Migration / phylogeography source-attribution" | MASCOT or MASCOT-GLM (sampling-aware); never BEAST DTA for attribution claims | BEAST DTA inherits Lemey 2009 sampling bias; published source-attribution remains biased toward heavily-sampled locations |

Methodology evolves; before any high-stakes phylodynamic analysis, web-search "BEAST2 BDSKY tutorial 2025" and "MASCOT-Skyline benchmark" for current best practice.

## Time-Scaling With TreeTime

**Goal:** Produce a time-scaled phylogeny with per-node date estimates and a global clock rate, ready for downstream R_e estimation or visualisation -- in minutes rather than hours.

**Approach:** Build the raw topology with IQ-TREE 2 (Minh 2020 *Mol Biol Evol* 37:1530) for outbreak-scale data (RAxML-NG for larger trees); pass to TreeTime jointly optimising the molecular clock and date assignments with a coalescent skyline prior; inspect `root_to_tip_regression.pdf` BEFORE trusting any downstream output; apply `--clock-filter 4` to drop tips with root-to-tip residuals exceeding 4 SDs.

```bash
iqtree -s aln.fasta -m GTR+G -B 1000 -T AUTO -pre raw_tree

treetime \
    --tree raw_tree.treefile \
    --aln aln.fasta \
    --dates dates.tsv \
    --coalescent skyline \
    --clock-filter 4 \
    --confidence \
    --reroot best \
    --outdir timetree

treetime clock \
    --tree raw_tree.treefile \
    --dates dates.tsv \
    --reassign-dates \
    --outdir date_randomisation
```

Outputs: `timetree.nexus` is the time-scaled tree; `dates.tsv` records per-tip filter status; `root_to_tip_regression.pdf` is the temporal-signal diagnostic. If R^2 < 0.3, the data do not support time-scaled inference; report uncertainty and consider extending the sampling window. For published clock rates, run the date-randomisation analysis (Duchêne 2015 *Mol Biol Evol* 32:1895) and report the clock-rate distribution under shuffled dates.

## BDSKY in BEAST2 With Recombination Masking First

**Goal:** Estimate R_e through time from a bacterial outbreak alignment with explicit handling of recombination, sampling proportion, and convergence diagnostics.

**Approach:** Snippy + snippy-core to build the core-genome alignment; Gubbins on `core.full.aln` (full positions including invariant) to mask recombinant tracts; IQ-TREE on the masked alignment; BEAUti to set up BDSKY XML in BEAST 2 (Bouckaert 2019 *PLoS Comput Biol* 15:e1006650 for BEAST 2.5+) with origin -- NOT rootHeight; sampling proportion per epoch; become-uninfectious rate fixed from epi knowledge; run with 3-4 independent chains from different seeds; combine chains only after marginal posteriors overlap.

```bash
snippy-core --ref reference.fa --prefix core snippy_out/*

run_gubbins.py --prefix gubbins core.full.aln

iqtree -s gubbins.filtered_polymorphic_sites.fasta -m GTR+G+ASC -B 1000 -T AUTO -pre masked_tree

beast -threads 4 -beagle -seed 42 bdsky_analysis.xml
beast -threads 4 -beagle -seed 17 bdsky_analysis.xml
beast -threads 4 -beagle -seed 99 bdsky_analysis.xml
beast -threads 4 -beagle -seed 7 bdsky_analysis.xml

logcombiner -log run_42.log -log run_17.log -log run_99.log -log run_7.log -burnin 10 -o combined.log
logcombiner -log run_42.trees -log run_17.trees -log run_99.trees -log run_7.trees -burnin 10 -o combined.trees -decimalPlaces 6
loganalyser -burnin 10 combined.log
```

`run_gubbins.py` input MUST be `core.full.aln` (full alignment with reference). Passing `core.aln` (variable-only) gives wrong recombination calls because Gubbins cannot estimate background SNP density without invariant positions. IQ-TREE `+ASC` is the ascertainment-bias correction required for SNP-only input.

## MASCOT Structured Coalescent

**Goal:** Infer per-deme effective population size and migration rates from sequences sampled in multiple subpopulations (countries, hospitals, ward types) without inheriting the Lemey 2009 BEAST DTA sampling bias.

**Approach:** BEAUti -> MASCOT template; one trait per deme; require >=20 sequences per deme for migration identifiability; consider MASCOT-GLM if migration rates plausibly depend on observable covariates (travel volume, geographic distance); pre-2024 default is MASCOT, but MASCOT-Skyline / MASCOT-GLM is preferred when sampling intensity varies over time.

```bash
beast -threads 4 -beagle -seed 42 mascot_analysis.xml
loganalyser -burnin 10 mascot.log
```

## Per-Method Failure Modes

### Recombination passed unmasked into clock inference

**Trigger:** BEAST2 or TreeTime run on a core-genome alignment of a recombining bacterium (S. pneumoniae, N. gonorrhoeae, E. coli, Klebsiella, Campylobacter, Helicobacter pylori).

**Mechanism:** Recombination imports SNPs from a divergent donor lineage in a single event. The clock model interprets these as accumulated point mutations across the branch, inflating the apparent clock rate and distorting node-date estimates. Recombination is non-clocklike, so date-randomisation tests may still pass -- the problem is silent.

**Symptom:** Estimated clock rate is 2-5x the literature consensus for the species (S. pneumoniae core clock ~1.5e-6 subs/site/year per literature; rates >5e-6 indicate unmasked recombination). Per-branch dN/dS profile is wildly heterogeneous. Some branches show implausibly recent divergence dates.

**Fix:** Mask recombinant regions before clock inference. Build initial tree with IQ-TREE on the core-SNP alignment; run Gubbins or ClonalFrameML to detect recombinant tracts; rebuild tree on the recombination-masked alignment; THEN run TreeTime or BEAST. For *M. tuberculosis* (rare recombination), masking is optional but defensible for cross-lineage analyses.

### Date-randomisation test passes despite no real temporal signal

**Trigger:** Outbreak with narrow sampling window (e.g. all isolates collected within 3 months of a year-long outbreak).

**Mechanism:** Date randomisation (Ramsden 2009 *Mol Biol Evol* 26:143; Duchêne 2015 *Mol Biol Evol* 32:1895) tests whether shuffling dates degrades the clock-rate estimate. With insufficient temporal sampling, the true clock estimate is also poorly informed, so randomised and true estimates overlap by chance.

**Symptom:** TempEst root-to-tip regression R^2 < 0.1; date-randomisation test still "passes" (HPD overlap); 95% HPD on clock rate spans an order of magnitude.

**Fix:** Inspect root-to-tip regression FIRST (TempEst). If R^2 < 0.3 and there is no strong a-priori clock-rate prior from the literature, the data do not support time-scaled inference. Options: (1) use a strong informative prior on clock rate from outside data; (2) extend the sampling window before re-running; (3) report a tree without time-scaling and discuss uncertainty.

### BDSKY origin specified as the root height

**Trigger:** BEAST2 BDSKY XML where `origin` is set to the same value as `rootHeight` (often because the user inferred from the tutorial that "origin = tree depth").

**Mechanism:** Stadler 2013 *PNAS* 110:228 defines `origin` as the time from the start of the epidemic to the most recent sample -- strictly larger than the tree root height (tMRCA). Setting `origin = tMRCA` causes the MCMC to start in an inconsistent state and systematically biases R_e estimates upward (because turnover is forced into a shorter time window).

**Symptom:** R_e estimates implausibly high in early epochs; chains mix poorly; origin-date estimate clusters at the lower bound of the prior.

**Fix:** Initialise `origin` to (tMRCA + 0.1*tMRCA) or use prior knowledge (e.g., for SARS-CoV-2 within a country, the documented import date). BEAUti default is sensible; hand-edited XML often gets this wrong.

### BSP / BDSKY ESS < 200 reported as a result

**Trigger:** Single BEAST chain reaching the planned MCMC length; some parameters with ESS in the 50-150 range; user reports the posterior anyway.

**Mechanism:** Tracer's ESS calculation is a single-chain effective sample size. For phylogenetic posteriors, parameters may be "mixed within chain" but "unmixed across chains" -- multiple independent chains can converge to different parts of the posterior. ESS > 200 is necessary but not sufficient.

**Symptom:** Reported HPD intervals from a single chain; reviewers from Stadler / Bouckaert / Suchard schools reject the analysis.

**Fix:** Run >=3-4 chains from different starting trees / seeds; examine marginal posteriors per chain; only after they overlap can chains be combined (`logcombiner`). Report Gelman-Rubin diagnostic via R `coda::gelman.diag` on the per-chain log files.

### MASCOT migration with too few sequences per deme

**Trigger:** MASCOT analysis with <20 sequences per deme; user reports migration-rate posterior.

**Mechanism:** MASCOT migration rates are jointly identifiable only with sufficient sequences per deme to inform within-deme coalescent. With few sequences, migration rate and Ne become confounded; the posterior reflects the prior more than the data.

**Symptom:** Migration-rate 95% HPD spans 2+ orders of magnitude; estimates implausibly extreme.

**Fix:** Pool nearby demes; accept wide HPD intervals; report MASCOT-GLM if covariates are available; cite Müller 2018 for the identifiability requirement.

### DTA used for phylogeography source-attribution

**Trigger:** BEAST DTA (Lemey 2009 *PLoS Comput Biol* 5:e1000520) used to claim a geographic source for an outbreak.

**Mechanism:** De Maio 2015 *PLoS Genet* 11:e1005421 demonstrated DTA is biased toward heavily-sampled locations; the example was Ebola DTA implausibly concluding humans seeded outbreaks (truth: sylvatic reservoir spillover). DTA treats sampling as random; in reality, source-attribution-relevant locations are often the most under-sampled.

**Symptom:** Inferred "source" is the heavily-sampled location; conclusion is sensitive to sub-sampling; reviewers familiar with MASCOT push back.

**Fix:** Use MASCOT or MASCOT-Skyline / MASCOT-GLM for source-attribution claims; if infeasible, frame results as "consistent with" rather than "demonstrates" and quantify sampling bias.

### UShER branch lengths used directly for R_e estimation

**Trigger:** Downstream BDSKY analysis on a UShER-placed subtree using UShER's parsimony branch lengths.

**Mechanism:** Turakhia 2021 *Nat Genet* 53:809 UShER places sequences on the MAT via parsimony; branch lengths under parsimony are systematically shorter than maximum-likelihood or Bayesian branch lengths (because parsimony minimises substitutions). R_e estimates that use UShER branch lengths directly are biased.

**Symptom:** Implausibly high R_e from a UShER-derived subtree; estimates inconsistent with case-based R_t.

**Fix:** Use UShER for placement only; re-estimate branch lengths with TreeTime or BEAST before downstream R_e estimation. This caveat is in the UShER documentation but routinely ignored.

### R_e reported as R_0

**Trigger:** Phylodynamic R_e estimate (current immunity / intervention context) described in text as R_0 (fully susceptible population).

**Mechanism:** Phylodynamic methods estimate the *effective* reproduction number R_e (or R_t), not the basic reproduction number R_0. The two diverge substantially: R_0 for ancestral SARS-CoV-2 was ~5-8; R_e during Omicron waves was 1.0-1.4.

**Symptom:** Figure legends say R_e; discussion text says R_0; readers conflate the two; comparisons to non-phylodynamic R_0 estimates inappropriate.

**Fix:** Use R_e (or R_t) consistently. Explicit footnote: "R_e estimated in the current epidemic context; the basic reproduction number R_0 was higher and is not what BDSKY estimates."

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Phylodynamic R_e and case-based R_t disagree | Sampling bias on one side; lineage-specific signal in phylodynamic; under-ascertainment in case data | Report both with explicit assumptions; investigate sampling profile |
| TreeTime R^2 = 0.5 but BEAST clock rate confidence wide | TreeTime point estimate vs Bayesian posterior with prior; informative prior may collapse | Compare BEAST clock to literature; check for prior dominance |
| BDSKY R_e implausibly high in early epochs | `origin` mis-specified; sampling proportion too high for early epoch | Re-check `origin` definition; allow sampling proportion to vary per epoch |
| Gubbins and ClonalFrameML give different recombination masks | Different model assumptions; both approximate | Either is defensible; run sensitivity by re-doing clock inference with the alternate mask |
| MASCOT and BEAST DTA disagree on migration | DTA is sampling-biased; MASCOT is sampling-aware | Trust MASCOT; report DTA only with caveat |
| UShER MAT subtree vs full BEAST disagree on TMRCA | Parsimony branch lengths shorter than ML | Re-estimate branch lengths on the UShER subtree with TreeTime before downstream |
| BICEPS Ne(t) trajectory differs from BSP on the same data | BICEPS analytic Ne integration vs BSP segment uniform | Trust BICEPS; BSP suffered from edge artifacts and slow mixing |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| TempEst root-to-tip R^2 minimum | >=0.3 | Rambaut 2016 *Virus Evol* 2:vew007 convention |
| BEAST ESS per parameter (single chain) | >=200 | Standard convention; necessary but not sufficient |
| BEAST burn-in | 10% of chain length | Convention; visually verify trace |
| MASCOT minimum sequences per deme | >=20 | Müller 2018 *Bioinformatics* 34:3843 identifiability requirement |
| BDSKY MCMC length (>=100 tips) | 10^7-10^8 states | Stadler 2013 *PNAS* 110:228; BDSKY mixes slowly |
| TreeTime `--clock-filter` default | 4 (SD multiplier on root-to-tip residual) | TreeTime convention; tighter for outlier-sensitive analyses |
| Gubbins input | `core.full.aln` (full positions, NOT `core.aln`) | Cannot estimate background SNP density from variable positions only |
| IQ-TREE ascertainment bias correction | `+ASC` for SNP-only alignment | IQ-TREE convention |
| S. pneumoniae core clock (recombination-masked) | ~1.5e-6 subs/site/year | Croucher et al *Science* 2013 literature; >5e-6 indicates unmasked recombination |
| SARS-CoV-2 clock rate (ancestral) | ~8e-4 subs/site/year | SARS-CoV-2 substitution-rate literature (varies by lineage) |
| M. tuberculosis clock rate | ~0.3-0.5 SNPs/genome/year | Walker 2013 *Lancet Infect Dis* 13:137 literature (varies by lineage) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Clock rate 3-5x literature | Unmasked recombination | Run Gubbins / ClonalFrameML first |
| BEAST chain stuck at single tree topology | Operator-weight imbalance or extreme prior | Check operator schedule; relax prior |
| `treetime --clock-filter False` rejected | `--clock-filter` takes a numeric SD multiplier | Pass a number (typically 4) or omit |
| `beast --threads 4` rejected | BEAST uses single-dash flags | `-threads 4` |
| BDSKY origin same as rootHeight | Tutorial confusion | Set `origin > rootHeight` per Stadler 2013 |
| MASCOT migration HPD spans 2+ orders | <20 seqs per deme | Pool demes; accept uncertainty |
| Single-chain ESS reported as proof of convergence | ESS necessary but not sufficient | Run multi-chain; combine post-overlap |
| `run_gubbins.py core.aln` (not `core.full.aln`) | Variable-only alignment | Use `core.full.aln`; cite Croucher 2015 |
| UShER branch lengths fed directly to BDSKY | Parsimony branch lengths biased low | Re-estimate via TreeTime or BEAST first |
| BEAST2 XML breaks on minor-release upgrade | XML fragile across versions | Pin BEAST + every BEAST2 package version |
| `--reroot best` produces implausible root | Sampling-biased outliers | Cross-check with TempEst; consider `--reroot oldest` or manual root |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Was temporal signal checked?" | TempEst R^2 reported; date-randomisation test run; both interpreted (date-randomisation can pass with narrow windows) |
| "Was recombination masked?" | Gubbins on `core.full.aln`; rebuilt tree on masked alignment; cite Croucher 2015 |
| "Why BDSKY and not BSP?" | BICEPS / BDSKY model sampling explicitly; BSP / Skygrid assume uniform sampling, biased under preferential surveillance |
| "How many BEAST chains?" | 3-4 independent chains; marginal posterior overlap checked; logcombiner only after agreement |
| "Was MASCOT or DTA used for migration?" | MASCOT (or MASCOT-GLM with covariates); DTA inherits Lemey 2009 sampling bias for source attribution |
| "BDSKY origin vs rootHeight?" | `origin > rootHeight` by Stadler 2013 convention; documented |
| "Is the clock rate consistent with the literature?" | Compared to species-specific reference; recombination-masked S. pneumoniae expected ~1.5e-6 |
| "Was the case-based R_t reconciled?" | Reported both; disagreement attributed to sampling bias (phylodynamic is lineage-specific; case data is population mean) |

## References

- Stadler T, Kühnert D, Bonhoeffer S, Drummond AJ (2013) Birth-death skyline plot reveals temporal changes of epidemic spread in HIV and hepatitis C virus (HCV). *Proc Natl Acad Sci USA* 110(1):228-233. doi:10.1073/pnas.1207965110
- Sagulenko P, Puller V, Neher RA (2018) TreeTime: maximum-likelihood phylodynamic analysis. *Virus Evol* 4(1):vex042. doi:10.1093/ve/vex042
- Rambaut A, Lam TT, Carvalho LM, Pybus OG (2016) Exploring the temporal structure of heterochronous sequences using TempEst (formerly Path-O-Gen). *Virus Evol* 2(1):vew007. doi:10.1093/ve/vew007
- Duchêne S, Duchêne D, Holmes EC, Ho SY (2015) The performance of the date-randomization test in phylogenetic analyses of time-structured virus data. *Mol Biol Evol* 32(7):1895-1906. doi:10.1093/molbev/msv056
- Ramsden C, Holmes EC, Charleston MA (2009) Hantavirus evolution in relation to its rodent and insectivore hosts: no evidence for codivergence. *Mol Biol Evol* 26(1):143-153. doi:10.1093/molbev/msn234
- Bouckaert R, Vaughan TG, Barido-Sottani J et al (2019) BEAST 2.5: An advanced software platform for Bayesian evolutionary analysis. *PLoS Comput Biol* 15(4):e1006650. doi:10.1371/journal.pcbi.1006650
- Bouckaert RR (2022) An Efficient Coalescent Epoch Model for Bayesian Phylogenetic Inference. *Syst Biol* 71(6):1549-1560. doi:10.1093/sysbio/syac015
- Müller NF, Rasmussen DA, Stadler T (2018) MASCOT: parameter and state inference under the marginal structured coalescent approximation. *Bioinformatics* 34(22):3843-3848. doi:10.1093/bioinformatics/bty406
- Lemey P, Rambaut A, Drummond AJ, Suchard MA (2009) Bayesian phylogeography finds its roots. *PLoS Comput Biol* 5(9):e1000520. doi:10.1371/journal.pcbi.1000520
- De Maio N, Wu CH, O'Reilly KM, Wilson D (2015) New routes to phylogeography: A Bayesian structured coalescent approximation. *PLoS Genet* 11(8):e1005421. doi:10.1371/journal.pgen.1005421
- Volz EM, Frost SDW (2014) Sampling through time and phylodynamic inference with coalescent and birth-death models. *J R Soc Interface* 11(101):20140945. doi:10.1098/rsif.2014.0945
- Croucher NJ, Page AJ, Connor TR et al (2015) Rapid phylogenetic analysis of large samples of recombinant bacterial whole genome sequences using Gubbins. *Nucleic Acids Res* 43(3):e15. doi:10.1093/nar/gku1196
- Didelot X, Wilson DJ (2015) ClonalFrameML: Efficient inference of recombination in whole bacterial genomes. *PLoS Comput Biol* 11(2):e1004041. doi:10.1371/journal.pcbi.1004041
- Mostowy R, Croucher NJ, Andam CP et al (2017) Efficient inference of recent and ancestral recombination within bacterial populations. *Mol Biol Evol* 34(5):1167-1182. doi:10.1093/molbev/msx066
- Didelot X, Croucher NJ, Bentley SD, Harris SR, Wilson DJ (2018) Bayesian inference of ancestral dates on bacterial phylogenetic trees. *Nucleic Acids Res* 46(22):e134. doi:10.1093/nar/gky783
- Turakhia Y, Thornlow B, Hinrichs AS et al (2021) Ultrafast Sample placement on Existing tRees (UShER) enables real-time phylogenetics for the SARS-CoV-2 pandemic. *Nat Genet* 53(6):809-816. doi:10.1038/s41588-021-00862-7
- Minh BQ, Schmidt HA, Chernomor O et al (2020) IQ-TREE 2: New models and efficient methods for phylogenetic inference in the genomic era. *Mol Biol Evol* 37(5):1530-1534. doi:10.1093/molbev/msaa015
- Legried B, Terhorst J (2022) A class of identifiable phylogenetic birth-death models. *Proc Natl Acad Sci USA* 119(35):e2119513119. doi:10.1073/pnas.2119513119
- Featherstone LA, Duchêne S (2023) Decoding the fundamental drivers of phylodynamic inference. *Mol Biol Evol* 40(6):msad132. doi:10.1093/molbev/msad132
- Walker TM, Ip CLC, Harrell RH et al (2013) Whole-genome sequencing to delineate Mycobacterium tuberculosis outbreaks: a retrospective observational study. *Lancet Infect Dis* 13(2):137-146. doi:10.1016/S1473-3099(12)70277-3

## Related Skills

- pathogen-typing - Defines isolates and clusters that feed phylodynamic inference
- transmission-inference - Phylodynamic R_e + transmission tree are complementary
- variant-surveillance - Lineage assignment runs upstream of skygrid / BDSKY by lineage
- phylogenetics/divergence-dating - Calibrated trees for non-pathogen contexts; deeper review of clock models
- phylogenetics/bayesian-inference - BEAST / RevBayes / MrBayes details beyond BDSKY
- phylogenetics/modern-tree-inference - IQ-TREE / RAxML topology before time-scaling
- phylogenetics/tree-io - Tree parsing and format conversion
- comparative-genomics/whole-genome-alignment - Core-genome alignment input for bacterial phylodynamics
- variant-calling/vcf-basics - Per-isolate variant calls feeding core-SNP alignment
- read-alignment/bwa-alignment - Read mapping upstream of variant calling
- data-visualization/multipanel-figures - Skyline / R_e trajectory plotting
- workflows/somatic-variant-pipeline - End-to-end orchestration patterns
<!-- END FILE: epidemiological-genomics/phylodynamics/SKILL.md -->

## 子目录：epidemiological-genomics/transmission-inference

<!-- BEGIN FILE: epidemiological-genomics/transmission-inference/SKILL.md -->
---
name: bio-epidemiological-genomics-transmission-inference
description: Infers person-to-person transmission from pathogen genomes using outbreaker2, TransPhylo, phybreak, BadTrIP, SCOTTI, BEASTLIER, and SNP-distance / cluster-picker approaches (HIV-TRACE for HIV; transcluster). Defines outbreak clusters using pathogen-specific SNP thresholds (NOT a universal cutoff -- TB <=12 SNPs; MRSA <=15; C. difficile <=2; Klebsiella <=21), models within-host diversity and transmission bottlenecks, integrates contact-tracing data, distinguishes generation from serial interval, and attributes source via Bayesian source attribution (islandR). Use when investigating outbreaks for who-infected-whom, defining SNP-cluster outbreak definitions, accounting for unsampled intermediates, choosing between outbreaker2 (rich epi data) and TransPhylo (genomic-only after a dated phylogeny), running source attribution between host populations, calling HIV-TRACE thresholds appropriate to the local subtype, or distinguishing recent transmission from reactivation in TB or chronic HIV.
tool_type: mixed
primary_tool: TransPhylo
---

## Version Compatibility

Reference examples tested with: TransPhylo 1.4+ (R), outbreaker2 1.2+ (R), phybreak 0.5+ (R), BadTrIP via BEAST 2.7+ package manager, BEASTLIER via BEAST 1.10+, transcluster 1.0+ (R), HIV-TRACE 1.5+, snp-dists 0.8+, ape 5.8+ (R), igraph 1.6+ (R), TreeTime 0.11+, BactDating 1.1+ (R), BEAST 2.7.6+, lofreq 2.1+, deepSNV via Bioconductor 3.18+, pandas 2.2+, BioPython 1.84+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('TransPhylo')`; `?inferTTree` to confirm arg names
- R: `packageVersion('outbreaker2')`; `?create_config` -- iteration count is set via `n_iter` in the `config` object, NOT as `iters` to `outbreaker()`
- Python: `pip show lofreq`; check whether deep variant calling supports the target MAF
- CLI: `snp-dists --help`; `hiv-trace --help`

If R rejects an argument, the function signature changed between minor releases; `?function_name` is authoritative.

# Transmission Inference

**"Who infected whom in this outbreak, and is this even an outbreak?"** -> Pick the question first (cluster definition vs WIWS who-infected-whom vs source attribution), then the method that fits the data (rich epi + dense sampling -> outbreaker2; sparse sampling + good dated tree -> TransPhylo; longitudinal within-host samples -> BEASTLIER / BadTrIP; rapid surveillance triage -> SNP-distance with pathogen-tuned threshold). Genomic distance is necessary but not sufficient for direction: two isolates 3 SNPs apart could be A->B, B->A, A->Unknown->B, or two-from-one common source. Direction inference requires temporal data, within-host diversity, contact-tracing data, or all three.

- R: `outbreaker2::outbreaker(data=outbreaker_data(dates=..., dna=..., w_dens=..., f_dens=..., ctd=...), config=create_config(n_iter=1e6))` -- dense outbreak with contact data
- R: `TransPhylo::inferTTree(ptree, mcmcIterations=1e5, w.shape=1.3, w.scale=10)` -- sparse outbreak from a dated tree
- CLI: `snp-dists -c gubbins.filtered_polymorphic_sites.fasta > pairwise.csv` -- pairwise SNP for cluster triage
- CLI: `hiv-trace --threshold 0.015` -- HIV cluster definition at the US-CDC default (subtype B); reconsider for non-B subtypes

## The Single Most Important Modern Insight -- There is no universal SNP cutoff for transmission

The pathogen-specific SNP threshold varies by 10x across taxa (TB <=12 SNPs, *C. difficile* <=2, MRSA <=15, *Salmonella* cgMLST <=5, *Klebsiella* <=21, SARS-CoV-2 not defined by SNP alone). Substitution rate, recombination, generation time, within-host diversity, and (for Mpox) APOBEC3 editing all vary by 100x. Walker 2013 *Lancet Infect Dis* 13:137 derived the TB <=12 SNP cutoff from UK Oxfordshire (low-transmission, contact-traced, household settings); applying the same threshold in Cape Town or Mumbai inflates apparent recent-transmission rates 2-5x because clonal isolates linked through long-past common ancestors get pooled with truly recent transmissions. Worby, Lipsitch & Hanage 2014 *PLoS Comput Biol* 10:e1003549 formally showed that within-host bacterial diversity puts an irreducible upper bound on the resolution of SNP-distance transmission-network reconstruction even with repeated sampling. Always cite the pathogen-specific source AND its derivation population; never apply a threshold outside its validated context without an explicit caveat. For TB / HIV / chronic infections, naive SNP cutoffs fail because of reactivation and within-host coalescence -- use TransPhylo or outbreaker2 with within-host-aware priors.

## Algorithmic Taxonomy

| Tool | Mechanism | Inputs | Output | Strength | Fails when |
|------|-----------|--------|--------|----------|------------|
| Pairwise SNP threshold (snp-dists; cluster picker) | Count SNPs between pairs; threshold + linkage | Core-SNP alignment | Adjacency at threshold | Fast; intuitive; standard for surveillance triage | Pathogen-specific cutoff; convergent evolution and recombination violate distance assumptions |
| HIV-TRACE (Kosakovsky Pond 2018 *Mol Biol Evol* 35:1812) | TN93 pairwise distance + threshold (default 1.5%) | HIV-1 pol or other gene | Cluster membership | CDC standard for US HIV surveillance | 1.5% threshold is US-CDC subtype B specific; under-clusters subtype C in southern Africa |
| outbreaker2 (Campbell 2018 *BMC Bioinformatics* 19:363) | MCMC; sequence + generation-interval + sampling-time + contact-tracing | Dated genomes + epi data | Posterior WIWS + unsampled intermediates + R_e | Integrates epi data explicitly; modular likelihood | ~100-200 cases practical limit; assumes one infection event per case (no within-host populations) |
| TransPhylo (Didelot 2017 *Mol Biol Evol* 34:997) | Coalescent within-host + birth-death between-host; colours a dated tree | Time-scaled tree + sampling dates | Posterior transmission tree + R_t + unsampled cases | Works from a tree, not raw genomes; scales to ~1000 tips; explicit within-host coalescence | Sensitive to within-host effective population size prior; requires good dated phylogeny |
| phybreak (Klinkenberg 2017 *PLoS Comput Biol* 13:e1005495) | Joint phylogeny + transmission inference via MCMC | Dated genomes | Posterior transmission tree | Proper within-host handling; fast for small outbreaks | <=100 cases; less benchmarked than outbreaker2/TransPhylo |
| BadTrIP (De Maio 2018 *PLoS Comput Biol* 14:e1006117) | Bayesian; explicit handling of multi-strain infections | Dated genomes | Posterior transmission tree with strain-level resolution | Handles within-host diversity / mixed infections (TB, HIV) | Slow; specialist tool |
| SCOTTI (De Maio 2016 *PLoS Comput Biol* 12:e1005130) | Structured-coalescent transmission inference (BEAST 2 package) | Dated genomes | Posterior transmission tree under structured coalescent | Sampling-aware; correctly models unsampled intermediates | Computationally heavy; specialist setup |
| BEASTLIER (Hall 2015 *PLoS Comput Biol* 11:e1004613) | Joint phylogeny + transmission partitioning | Dated genomes; ideally with multiple isolates per host | Posterior transmission tree with within-host partition | Postdoc-grade identifiability with within-host samples | Single-isolate-per-host data is under-identified |
| transcluster (Stimson 2019 *Mol Biol Evol* 36:587) | Per-pair posterior probability under SNP + time prior | Dated genomes | Per-pair cluster membership probability | Probabilistic; pathogen-tuned priors | Pair-level only; no full transmission tree |
| Sobel Leonard 2017 *J Virol* 91:e00171-17 beta-binomial bottleneck | Estimate transmission bottleneck size from donor-recipient deep sequencing | Donor + recipient deep-sequence allele frequencies | Bottleneck Nb posterior | Estimates an otherwise unobservable quantity | Requires deep-sequenced donor-recipient pairs |
| islandR / Bayesian source attribution (Mather 2013 *Science* 341:1514) | Bayesian per-population allele-frequency model | Reference collections per host source + query genome | Per-source posterior probability | Standard in Salmonella / Campylobacter food-safety surveillance | Source-attribution circularity: trained-on-distribution reproduces that distribution |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why wrong choices fail |
|----------|----------------------|------------------------|
| "Is this even an outbreak?" routine surveillance triage | `snp-dists` after Gubbins; pathogen-tuned threshold (Walker 2013 for TB, Eyre 2013 for C. diff, EFSA cgMLST <=5 for Salmonella); cross-check cgMLST distance | Universal SNP threshold across pathogens (10x variation) |
| Densely sampled outbreak with contact-tracing data | outbreaker2 with `ctd` contact matrix + generation-time prior + sampling-time prior | TransPhylo without epi data (loses information from contacts); naive SNP threshold (ignores within-host diversity) |
| Sparsely sampled, longer-time-scale outbreak | TransPhylo on a BactDating-derived dated tree | outbreaker2 (sampling-completeness assumption broken); SNP threshold inflates clusters with unsampled intermediates |
| TB outbreak with possible reactivation | TransPhylo + transcluster with TB-tuned priors; long within-host coalescent matters | SNP cutoff insufficient -- reactivation can have 0 SNPs from years-old strains |
| Hospital outbreak with possible mixed infection | BadTrIP / SCOTTI | Consensus-only methods (SNP distance, outbreaker2) ambiguous on mixed-strain |
| Multi-site outbreak with import suspected | TransPhylo + MASCOT-derived migration; source-attribution as separate analysis | Source attribution needs phylogeographic component beyond TransPhylo alone |
| Food-vehicle / environmental source attribution | islandR / Bayesian source attribution (Mather 2013 framework); manual cluster + phylogeographic plot | Naive phylogenetic placement loses the per-source priors |
| Sub-sampled outbreak (<50% cases sequenced) | outbreaker2 (handles unsampled cases explicitly with `pi` sampling parameter) | Raw SNP cutoff -- unsampled intermediates break SNP-distance reasoning |
| Recombining pathogen (S. pneumo, E. coli STEC, K. pneumoniae) | Gubbins / ClonalFrameML mask FIRST; then any of the above | Recombination inflates apparent SNP distance and creates false convergent transmission inference |
| HIV cluster definition | HIV-TRACE 1.5% for subtype B (US-CDC standard); reconsider for non-B subtypes | Applying 1.5% threshold globally without subtype caveat |
| Estimate transmission bottleneck | Sobel Leonard 2017 beta-binomial on deep-sequenced donor-recipient pairs | Consensus-only sequences cannot quantify bottleneck size |

Methodology evolves; before any high-stakes who-infected-whom claim, web-search "outbreak transmission inference benchmark <pathogen> 2025" for current best practice.

## outbreaker2 With Contact Data

**Goal:** Infer who-infected-whom posterior for a densely sampled outbreak with epi metadata, jointly estimating generation interval and unsampled-case proportion.

**Approach:** Build `outbreaker_data` with sampling dates, DNA alignment, generation-time density `w_dens`, sampling-time density `f_dens`, and contact-tracing matrix `ctd`; configure MCMC via `create_config(n_iter=N)`; run; summarise posterior over WIWS.

```r
library(outbreaker2)
library(ape)

dna <- read.dna('alignment.fasta', format='fasta')
dates <- read.csv('sampling_dates.csv')
ctd_matrix <- as.matrix(read.csv('contact_matrix.csv', row.names=1))

w_dens <- dgamma(1:30, shape=2.5, scale=2)  # generation time prior
f_dens <- dgamma(1:30, shape=2, scale=3)    # sampling-time prior

data <- outbreaker_data(dates=dates$collection_date, dna=dna,
                        w_dens=w_dens, f_dens=f_dens, ctd=ctd_matrix)

cfg <- create_config(n_iter=1e6, sample_every=200, find_import=TRUE)

res <- outbreaker(data=data, config=cfg)
summary(res)
```

`w_dens` is the generation-time distribution (time from infection of A to infection of B) -- NOT the serial interval (time between symptom onsets); using one in place of the other biases inference. Britton & Scalia Tomba *J R Soc Interface* 16:20180670 (2019) formalised the bias for emerging epidemics; for SARS-CoV-2 with substantial pre-symptomatic transmission (Ali 2020 *Science* 369:1106), the serial interval shortened from 7.8 to 2.2 days under NPI, and naive SI-based inference was biased.

## TransPhylo From a Dated Tree

**Goal:** Infer transmission tree posterior from a time-scaled phylogeny when raw genomes are not directly usable or when the outbreak is too large for outbreaker2 (>200 cases).

**Approach:** Time-scale the tree first (BactDating after Gubbins for bacteria; BEAST or TreeTime for viruses); convert to TransPhylo `ptree` with `ptreeFromPhylo`; run `inferTTree` with generation-time prior and within-host effective population size prior; summarise via `medTTree` (medoid transmission tree) and posterior probabilities per WIWS pair.

```r
library(TransPhylo)
library(ape)

tree <- read.nexus('dated_tree.nexus')
date_last_sample <- 2024.95

ptree <- ptreeFromPhylo(tree, dateLastSample=date_last_sample)

w.shape <- 1.3
w.scale <- 10
ws.shape <- 1.1
ws.scale <- 7
neg <- 0.5

res <- inferTTree(ptree, mcmcIterations=1e5,
                  w.shape=w.shape, w.scale=w.scale,
                  ws.shape=ws.shape, ws.scale=ws.scale,
                  startNeg=neg, dateT=date_last_sample + 0.1)

med_tree <- medTTree(res)
pairs <- extractTTree(med_tree)$ttree
```

`w.*` is the generation-time Gamma prior; `ws.*` is the sampling-time Gamma prior. Both must reflect the pathogen's biology (e.g., TB w.scale = months; SARS-CoV-2 w.scale = days). Wrong priors silently bias the transmission-tree posterior.

## SNP-Cluster Definition With Pathogen-Specific Thresholds

**Goal:** Define outbreak clusters from a recombination-masked core-SNP alignment using the published pathogen-specific threshold, with the threshold's source population caveated.

**Approach:** Snippy -> snippy-core -> Gubbins on `core.full.aln` for bacteria -> snp-dists -> single-linkage clustering at the pathogen-specific threshold; cite Walker 2013 (TB), Eyre 2013 (C. diff), Coll 2017 (MRSA), Snitkin 2012 (Klebsiella) per organism; flag any extrapolation outside the threshold's validation population.

```bash
snippy-core --ref reference.fa --prefix core snippy_out/*
run_gubbins.py --prefix gubbins core.full.aln
snp-dists -c gubbins.filtered_polymorphic_sites.fasta > pairwise.csv
```

```python
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

dist = pd.read_csv('pairwise.csv', index_col=0)
condensed = dist.values[np.triu_indices(len(dist), k=1)]

THRESHOLD_TB = 12   # Walker 2013 Lancet Infect Dis 13:137 -- UK low-transmission
THRESHOLD_MRSA = 15  # Coll 2017 Clin Infect Dis 65:1781
THRESHOLD_CDIFF = 2  # Eyre 2013 NEJM 369:1195
THRESHOLD_KPNEUMO = 21  # Snitkin 2012 Sci Transl Med 4:148ra116

linkage_matrix = linkage(condensed, method='single')
clusters = fcluster(linkage_matrix, t=THRESHOLD_TB, criterion='distance')
```

## Per-Method Failure Modes

### Pairwise SNP threshold applied outside its validation population

**Trigger:** Walker 2013 UK 5/12-SNP TB threshold applied to Cape Town or Mumbai high-transmission settings.

**Mechanism:** Walker 2013 *Lancet Infect Dis* 13:137 calibrated the 5/12 SNP threshold on Oxfordshire community / household contact-traced data (low-transmission). In high-prevalence settings, clonal isolates linked through long-past common ancestors fall within the threshold without recent direct transmission.

**Symptom:** Country-level Mtb genomic-epi report shows 60-80% of cases in "transmission clusters", far exceeding clinical contact-tracing rates.

**Fix:** Cite the threshold's source population; for high-prevalence settings, derive a local threshold from epidemiologically-anchored case pairs in the local cohort rather than importing a UK-low-transmission cutoff. For transmission-direction claims, supplement with TransPhylo / outbreaker2.

### Direction of transmission asserted from pairwise SNP distance alone

**Trigger:** Outbreak report concluding "A -> B" because A has earlier sampling date and 3 SNPs from B.

**Mechanism:** A 3-SNP pairwise difference is consistent with A->B, B->A, Unknown->both, or A->Unknown->B. Worby, Lipsitch & Hanage 2014 *PLoS Comput Biol* 10:e1003549 formalised the irreducible uncertainty. Earlier sampling date does not establish earlier infection date because of within-host evolution and asymptomatic carriage.

**Symptom:** Outbreak conclusions claim directionality without within-host data or contact tracing; reviewers from the Didelot / Worby groups push back.

**Fix:** Use "transmission consistent with genomics" not "transmission demonstrated". For direction claims, require within-host samples (BEASTLIER), contact-tracing data (outbreaker2 with `ctd`), or both. Cite Worby 2014 as the upper bound on what SNP distance can establish.

### Unsampled intermediates collapsed into A->B direct links

**Trigger:** Outbreak with <50% sequencing coverage; transmission inference assumes all cases sampled.

**Mechanism:** When sampling is incomplete, inferred A->B "direct" transmissions are routinely A->Unknown->B chains. This systematically inflates inferred R_e (longer chains compressed), underestimates generation interval, and biases topology toward bushy trees.

**Symptom:** Inferred R_e is implausibly high (each "tip" appears to spawn extra children once unsampled intermediates collapse into apparent direct links); generation interval estimate is implausibly short; topology appears bushier than expected.

**Fix:** Use outbreaker2 with explicit `pi` (sampling proportion) parameter, or TransPhylo / SCOTTI which model unsampled intermediates explicitly. Cite the unsampled-intermediates caveat in every transmission-inference report.

### Narrow transmission bottleneck makes consensus-only inference WORSE than coalescent intuition predicts

**Trigger:** Consensus-genome transmission-pair inference for a pathogen with documented narrow bottleneck (influenza 1-2 virions per McCrone 2018 *eLife* 7:e35962; SARS-CoV-2 <10 virions per Lythgoe 2021 *Science* 372:eabg0821).

**Mechanism:** When the transmission bottleneck is narrow, donor and recipient consensus genomes are near-identical *by default* -- the bottleneck strips most within-host diversity. Near-identity therefore does NOT discriminate direct transmission from infection by an unsampled intermediate or from a shared common source. Naive coalescent intuition predicts that "more transmissions = more divergence"; the opposite is true under a narrow bottleneck.

**Symptom:** Most pairs in a dense outbreak appear identical or 1 SNP apart; SNP-distance-based cluster definitions become uninformative; transmission-direction claims based on consensus difference are unfalsifiable.

**Fix:** For narrow-bottleneck pathogens, supplement consensus-based methods with deep within-host variant calling (lofreq / deepSNV / VarScan2 at MAF >= 1%) on donor-recipient pairs; estimate bottleneck size explicitly via Sobel Leonard 2017 *J Virol* 91:e00171-17 beta-binomial estimator; report transmission claims as "consistent with" rather than "demonstrated by" consensus identity. Pair-level resolution requires within-host data; without it, claim only cluster membership, not direction.

### Generation interval and serial interval used interchangeably

**Trigger:** outbreaker2 / EpiNow2 / similar tools fed the serial-interval distribution (`w_dens` set from symptom-to-symptom data) when the model wants generation-interval (infection-to-infection).

**Mechanism:** Generation interval = time from infection of A to infection of B; serial interval = time from symptom onset of A to symptom onset of B. They differ when incubation periods vary or pre-symptomatic transmission is substantial. Britton & Scalia Tomba 2019 *J R Soc Interface* 16:20180670 formalised the bias for emerging epidemics; Ali 2020 *Science* 369:1106 showed for SARS-CoV-2 the SI shortened from 7.8 to 2.2 days under NPI.

**Symptom:** Inferred R_e is biased; comparison to case-based R_t (also often SI-based) shows compounding bias.

**Fix:** Document which distribution `w_dens` actually encodes. For SARS-CoV-2 with substantial pre-symptomatic transmission, generation interval is ~5 days in the ancestral-strain literature; serial interval was ~4-5 days early but shortened to 2-3 under NPI. Cite Britton 2019.

### HIV-TRACE 1.5% threshold applied to non-subtype-B HIV

**Trigger:** HIV-TRACE run on subtype C sequences from southern Africa with the default 1.5% TN93 threshold.

**Mechanism:** Kosakovsky Pond et al 2018 *Mol Biol Evol* 35:1812 documented HIV-TRACE methodology; the 1.5% threshold is the US-CDC default tuned for subtype B in MSM cohorts. Subtype C in southern Africa has higher diversity per unit time and more recent epidemics; the 1.5% threshold under-clusters there.

**Symptom:** Cluster definitions in southern African subtype C HIV surveillance under-detect transmission; comparison to US surveillance literature shows incompatible cluster sizes.

**Fix:** Tune threshold for the local subtype and population; cite the local validation. UKHSA / ECDC use different thresholds; document which.

### Source attribution circularity

**Trigger:** Bayesian source attribution model (Mather 2013 *Science* 341:1514 framework) trained on a reference collection that over-represents one host population.

**Mechanism:** Source-attribution models reproduce the host-distribution of their training data unless explicitly corrected. If 80% of training isolates are from cattle, the model will tend to attribute new isolates to cattle even when the true source is poultry.

**Symptom:** Source attribution reproduces the sampling intensity of the reference collection; conclusions are circular.

**Fix:** Weight by inverse sampling intensity per source category; use rarefied reference collections; report attribution alongside the reference-collection composition as a caveat.

### Primer-scheme dropout misread as real divergence

**Trigger:** SARS-CoV-2 outbreak comparison across samples sequenced with different ARTIC primer schemes (V3 / V4 / V4.1 / V5.3.2); "differences" concentrated in one amplicon are interpreted as real SNPs.

**Mechanism:** ARTIC primer dropouts produce N's or reference-derived consensus calls in failed amplicons (Itokawa 2020 *PLoS ONE* 15:e0239403); these LOOK LIKE deletions or reference matches in downstream analysis but are missing data. Cross-scheme comparison without masking failed amplicons produces spurious transmission differences.

**Symptom:** Cluster definitions differ implausibly between ARTIC-V3 and ARTIC-V4.1 samples; "differences" cluster in known dropout amplicons (V4.1 amplicons 64, 76, 88-90).

**Fix:** Mask failed amplicons per sample (samtools depth + per-amplicon coverage); document primer scheme version per isolate; for transmission inference, exclude positions in any sample's dropout regions.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| outbreaker2 and TransPhylo disagree on WIWS | Different sampling-completeness assumptions; outbreaker2 expects ~dense sampling, TransPhylo handles sparse | Pick the method whose assumption matches the data; cite the choice |
| SNP threshold cluster and outbreaker2 cluster differ | SNP threshold ignores temporal data and contacts | Trust outbreaker2 (integrates more evidence); SNP cluster is triage only |
| Two consecutive Pangolin versions give different lineage for a "transmission pair" | Lineage definitions revised | Re-run both samples against a single Pango / pangolin-data version |
| TB cluster definition flips between 5 and 12 SNP threshold | Walker 2013 ambiguous range | Run TransPhylo for transmission-direction posterior; report SNP-distance with cluster picker certainty |
| HIV cluster differs between HIV-TRACE 1.5% and 2.0% | Threshold sensitivity at boundary | Subtype-specific calibration; cite the chosen threshold's validation |
| Source attribution differs between islandR runs with different reference panels | Sampling-intensity bias | Re-run with rarefied or inverse-weighted reference; report multiple scenarios |

## Quantitative Thresholds

| Pathogen | "Outbreak cluster" threshold | Source / rationale |
|----------|------------------------------|--------------------|
| *Mycobacterium tuberculosis* (whole-genome core SNP) | <=12 SNPs (likely transmission); <=5 SNPs (recent transmission) | Walker 2013 *Lancet Infect Dis* 13:137 (UK low-transmission setting) |
| *Staphylococcus aureus* (core genome) | <=15 SNPs (within hospital outbreak); <=40 SNPs (broader temporal cluster) | Coll 2017 *Clin Infect Dis* 65:1781 |
| *Klebsiella pneumoniae* (KPC outbreak) | <=21 SNPs | Snitkin 2012 *Sci Transl Med* 4:148ra116 |
| *Salmonella enterica* (cgMLST EnteroBase) | <=5 allelic differences (cluster); <=7 (extended cluster) | EnteroBase / EFSA harmonised |
| *Listeria monocytogenes* (PulseNet cgMLST) | <=4 allelic differences | PulseNet protocol convention |
| *E. coli* (cgMLST, EnteroBase) | <=10 allelic differences (STEC outbreak) | EnteroBase convention |
| *Neisseria gonorrhoeae* | <=25 core SNPs (transmission) | UKHSA STI framework |
| *Clostridioides difficile* (core SNP, recombination-masked) | <=2 SNPs (likely direct); <=10 (plausible within 6 months) | Eyre 2013 *NEJM* 369:1195 |
| SARS-CoV-2 (whole-genome) | No fixed cutoff; 0-2 SNPs + epi link + sampling window | Lythgoe 2021 *Science* 372:eabg0821 |
| HIV-1 subtype B (TN93 distance) | 1.5% genetic distance (HIV-TRACE default; US-CDC standard) | Kosakovsky Pond 2018 *Mol Biol Evol* 35:1812 |
| Mpox clade IIb | <=2 SNPs cluster threshold; APOBEC3 editing inflates apparent distance | Mpox 2022 outbreak APOBEC3-editing literature |
| Transmission bottleneck -- influenza | ~1-2 virions (narrow) | McCrone 2018 *eLife* 7:e35962 |
| Transmission bottleneck -- SARS-CoV-2 | <10 virions (tight) | Lythgoe 2021 *Science* 372:eabg0821 |
| Generation interval -- SARS-CoV-2 ancestral | ~5 days | SARS-CoV-2 ancestral-strain literature |

CRITICAL: a number from one pathogen does NOT transfer to another. Always cite the source population.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| outbreaker2 rejects `iters` arg | Iterations set via `n_iter` in the `config` object | `create_config(n_iter=N)` |
| TransPhylo MCMC fails to converge | Within-host Ne prior misspecified; bad input tree | Tune `startNeg`; verify tree dating quality |
| Cluster definition flips between linkage methods | Single-linkage vs complete-linkage on borderline pairs | Document; sensitivity analysis |
| outbreaker2 estimates implausible R_e | Sampling proportion mis-specified | Set `pi` based on epi knowledge or estimate within outbreaker2 |
| Transmission inferred between two distant lineages | Recombination unmasked | Run Gubbins on `core.full.aln` first |
| HIV-TRACE clusters incompatible across labs | Different subtype calibration | Document subtype; use locally validated threshold |
| Source attribution always pointing at one host | Reference-collection bias | Re-weight or rarify reference panel |
| `snp-dists -t` rejected | `-t` flag doesn't exist; default IS tab; `-c` for CSV | Use `-c` for CSV; default for TSV |
| Snippy outputs disagree across samples | Different reference; reference mismatch silently shifts SNP coordinates | Always document reference; use same reference cross-lab |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "What SNP threshold and on what population?" | Cite Walker 2013 / Eyre 2013 / Coll 2017 per pathogen; caveat the population if extrapolating |
| "Were unsampled intermediates handled?" | outbreaker2 `pi` parameter or TransPhylo / SCOTTI explicit modelling; never a raw SNP-distance method on sub-sampled data |
| "Direction of transmission inference?" | Within-host samples + contact tracing required for direction; otherwise "consistent with" phrasing |
| "Generation interval vs serial interval?" | Documented `w_dens` source; cite Britton 2019 if SI used as approximation for GI |
| "Why TransPhylo / outbreaker2 / phybreak?" | Decision tree based on sampling completeness, dataset size, contact-tracing availability |
| "Was within-host diversity considered?" | TransPhylo's within-host coalescent OR BadTrIP for mixed-strain; bottleneck size from Sobel Leonard 2017 if relevant |
| "HIV-TRACE 1.5% threshold outside subtype B?" | Acknowledged US-CDC subtype B origin; either use locally validated threshold or document caveat |
| "Source attribution sampling-intensity bias?" | Re-weighted reference collection or rarified; cite Mather 2013 limitation |
| "Was forward simulation run as a sanity check?" | SLiM / FAVITES / SEEDY if claims are high-stakes; routinely under-done in published transmission inference |

## References

- Worby CJ, Lipsitch M, Hanage WP (2014) Within-host bacterial diversity hinders accurate reconstruction of transmission networks from genomic distance data. *PLoS Comput Biol* 10(3):e1003549. doi:10.1371/journal.pcbi.1003549
- Campbell F, Didelot X, Fitzjohn R, Ferguson N, Cori A, Jombart T (2018) outbreaker2: a modular platform for outbreak reconstruction. *BMC Bioinformatics* 19(Suppl 11):363. doi:10.1186/s12859-018-2330-z
- Didelot X, Fraser C, Gardy J, Colijn C (2017) Genomic infectious disease epidemiology in partially sampled and ongoing outbreaks. *Mol Biol Evol* 34(4):997-1007. doi:10.1093/molbev/msw275
- Klinkenberg D, Backer JA, Didelot X, Colijn C, Wallinga J (2017) Simultaneous inference of phylogenetic and transmission trees in infectious disease outbreaks. *PLoS Comput Biol* 13(5):e1005495. doi:10.1371/journal.pcbi.1005495
- De Maio N, Worby CJ, Wilson DJ, Stoesser N (2018) Bayesian reconstruction of transmission within outbreaks using genomic variants. *PLoS Comput Biol* 14(4):e1006117. doi:10.1371/journal.pcbi.1006117
- De Maio N, Wu CH, Wilson DJ (2016) SCOTTI: efficient reconstruction of transmission within outbreaks with the structured coalescent. *PLoS Comput Biol* 12(9):e1005130. doi:10.1371/journal.pcbi.1005130
- Hall M, Woolhouse M, Rambaut A (2015) Epidemic reconstruction in a phylogenetics framework: transmission trees as partitions of the node set. *PLoS Comput Biol* 11(12):e1004613. doi:10.1371/journal.pcbi.1004613
- Stimson J, Gardy J, Mathema B et al (2019) Beyond the SNP threshold: identifying outbreak clusters using inferred transmissions. *Mol Biol Evol* 36(3):587-603. doi:10.1093/molbev/msy242
- Walker TM, Ip CLC, Harrell RH et al (2013) Whole-genome sequencing to delineate Mycobacterium tuberculosis outbreaks: a retrospective observational study. *Lancet Infect Dis* 13(2):137-146. doi:10.1016/S1473-3099(12)70277-3
- Coll F, Harrison EM, Toleman MS et al (2017) Longitudinal genomic surveillance of MRSA in the UK reveals transmission patterns in hospitals and the community. *Clin Infect Dis* 65(11):1781-1789. doi:10.1093/cid/cix645
- Eyre DW, Cule ML, Wilson DJ et al (2013) Diverse sources of C. difficile infection identified on whole-genome sequencing. *N Engl J Med* 369(13):1195-1205. doi:10.1056/NEJMoa1216064
- Snitkin ES, Zelazny AM, Thomas PJ et al (2012) Tracking a hospital outbreak of carbapenem-resistant Klebsiella pneumoniae with whole-genome sequencing. *Sci Transl Med* 4(148):148ra116. doi:10.1126/scitranslmed.3004129
- Lythgoe KA, Hall M, Ferretti L et al (2021) SARS-CoV-2 within-host diversity and transmission. *Science* 372(6539):eabg0821. doi:10.1126/science.abg0821
- McCrone JT, Woods RJ, Martin ET et al (2018) Stochastic processes constrain the within and between host evolution of influenza virus. *eLife* 7:e35962. doi:10.7554/eLife.35962
- Sobel Leonard A, Weissman DB, Greenbaum B, Ghedin E, Koelle K (2017) Transmission bottleneck size estimation from pathogen deep-sequencing data, with an application to human influenza A virus. *J Virol* 91(14):e00171-17. doi:10.1128/JVI.00171-17
- Britton T, Scalia Tomba G (2019) Estimation in emerging epidemics: biases and remedies. *J R Soc Interface* 16(150):20180670. doi:10.1098/rsif.2018.0670
- Ali ST, Wang L, Lau EHY et al (2020) Serial interval of SARS-CoV-2 was shortened over time by nonpharmaceutical interventions. *Science* 369(6507):1106-1109. doi:10.1126/science.abc9004
- Kosakovsky Pond SL, Weaver S, Leigh Brown AJ, Wertheim JO (2018) HIV-TRACE (TRAnsmission Cluster Engine): A tool for large-scale molecular epidemiology of HIV-1 and other rapidly evolving pathogens. *Mol Biol Evol* 35(7):1812-1819. doi:10.1093/molbev/msy016
- Mather AE, Reid SWJ, Maskell DJ et al (2013) Distinguishable epidemics of multidrug-resistant Salmonella Typhimurium DT104 in different hosts. *Science* 341(6153):1514-1517. doi:10.1126/science.1240578
- Itokawa K, Sekizuka T, Hashino M, Tanaka R, Kuroda M (2020) Disentangling primer interactions improves SARS-CoV-2 genome sequencing by multiplex tiling PCR. *PLoS ONE* 15(9):e0239403. doi:10.1371/journal.pone.0239403

## Related Skills

- pathogen-typing - SNP-cluster / cgMLST cluster definition feeds transmission inference
- phylodynamics - Time-scaled tree from BactDating / BEAST / TreeTime feeds TransPhylo
- amr-surveillance - Resistant-clone outbreak inference combines AMR + transmission
- variant-surveillance - Lineage assignment cross-checks transmission cluster boundaries
- phylogenetics/divergence-dating - Calibrated trees for non-pathogen contexts
- phylogenetics/bayesian-inference - BEAST mechanics beyond outbreak phylodynamics
- comparative-genomics/whole-genome-alignment - Core-genome alignment for SNP-typing
- variant-calling/vcf-basics - Per-isolate variant calls for SNP-typing
- variant-calling/variant-calling - SNP calling that feeds snp-dists
- read-alignment/bwa-alignment - Read mapping upstream
- data-visualization/network-visualization - Transmission tree visualisation
- workflows/somatic-variant-pipeline - End-to-end orchestration patterns
<!-- END FILE: epidemiological-genomics/transmission-inference/SKILL.md -->

## 子目录：epidemiological-genomics/variant-surveillance

<!-- BEGIN FILE: epidemiological-genomics/variant-surveillance/SKILL.md -->
---
name: bio-epidemiological-genomics-variant-surveillance
description: Assigns pathogen lineages (SARS-CoV-2 Pangolin UShER mode; Nextclade clade + QC; pango-designation alias resolution) and tracks variant frequencies over time using Nextstrain (Augur + Auspice), wastewater deconvolution (Freyja, COJAC, alcov, lineagespot), lineage-fitness modelling (multinomial logistic), and recombinant detection (3SEQ, RDP4, Bolotie). Covers Pangolin pangolin-data and Nextclade dataset version pinning (mandatory; lineage-defining mutations change with dataset), Freyja barcode forward-only date constraint, ARTIC primer scheme churn (V3/V4/V4.1/V5.3.2/Midnight) with dropout regions, and recombinant X-prefix designation lag. Use when assigning Pango lineages and Nextclade clades to viral consensus sequences, building Nextstrain Augur surveillance pipelines, deconvolving wastewater into lineage frequencies with Freyja, tracking lineage frequencies over time, handling ARTIC primer dropouts, or running surveillance for SARS-CoV-2/influenza/Mpox/RSV/H5N1/measles.
tool_type: mixed
primary_tool: Pangolin
---

## Version Compatibility

Reference examples tested with: pangolin 4.3+ (pangolin-data 1.30+), nextclade 3.8+, augur 24.0+, freyja 1.4+, cojac 0.9+, lineagespot 1.6+ (Bioconductor), usher 0.6+, matUtils 0.6+, samtools 1.20+, lofreq 2.1+, ivar 1.4+, ARTIC pipeline 1.3+, snakemake 8.5+, pandas 2.2+, BioPython 1.84+, jq 1.7+.

Before using code patterns, verify installed versions match. If versions differ:
- `pangolin --all-versions` -- prints pangolin + pangolin-data + scorpio + constellations versions
- `nextclade dataset list --tag latest sars-cov-2` -- list current dataset tags
- `freyja --version`; `freyja barcode-build --help` (note: HYPHEN, not underscore; some legacy docs show `barcode_build`)
- `nextclade run --help` -- v3+ syntax replaced v2; old `nextclade` invocation no longer works
- `augur --version`; `augur refine --help` for current root-strategy flags

If `pangolin --inference usher` is rejected, the flag is `--analysis-mode usher` (no `--inference`). If `nextclade --input-dataset DIR` works, the installed version may be v2; v3 accepts both but `--dataset NAME` is the modern form for built-in datasets. Pangolin and Nextclade output column names differ between major releases -- introspect rather than retry.

# Variant Surveillance

**"Which lineages are circulating, and how fast are they growing?"** -> Assign consensus or wastewater samples to a curated lineage / clade nomenclature, then track frequencies over time with explicit version pinning. The lineage assignment is NOT a stable property of the sequence; it is a property of the sequence interpreted by a specific pangolin-data / Nextclade-dataset version. Two labs running the same Pangolin binary with different pangolin-data versions can produce different calls on the same genome. For published or regulatory output, pin BOTH the executable AND the dataset version (`pangolin --all-versions`; `nextclade dataset list --tag latest`), and re-run the whole archive after every dataset update -- comparing today's BA.2.86 call to last month's "Unassigned" call is invalid.

- CLI: `pangolin sequences.fasta --analysis-mode usher --outfile lineage_report.csv` -- UShER mode is the default since v4 (pangoLEARN deprecated mid-2023)
- CLI: `nextclade run --input-dataset nc_dataset/sars-cov-2 --output-tsv nc.tsv sequences.fasta` -- clade + Pango + QC + mutations
- CLI: `freyja variants sample.bam --variants sample.variants.tsv --depths sample.depths.tsv --ref reference.fa` then `freyja demix sample.variants.tsv sample.depths.tsv --output sample.demix.tsv` -- wastewater lineage deconvolution
- CLI: `augur refine --tree tree.nwk --alignment aln.fasta --metadata meta.tsv --output-tree refined.nwk --root oldest --timetree` -- Nextstrain time-scaling

## The Single Most Important Modern Insight -- Lineage assignment is dataset-version-dependent

A SARS-CoV-2 sequence called BA.5 today might be called BA.5.2.1 next week and KP.3 a month after that. pangolin-data and nextclade-dataset are updated weekly; lineage definitions evolve through pango-designation GitHub issues, often days-to-weeks before pangolin-data releases include the lineage. During the lag window, the same genome submitted in lab A (older pangolin-data) and lab B (current) gets different calls. The cross-lab "different lineage" result is then misread as biology. For any report, pin BOTH the executable AND the dataset version with `pangolin --all-versions` and `nextclade dataset list --tag latest` recorded alongside the call. For longitudinal studies, re-run the WHOLE archive after every dataset update -- comparing today's BA.2.86 call against last month's "Unassigned" call is invalid. Second-order insight: Pangolin's pangoLEARN mode was officially deprecated mid-2023 in favour of UShER mode (Pongmoragot 2024 *Virus Evol* 10:vead085); cross-study comparison of XBB sub-lineage prevalence from 2022 - mid-2023 is contaminated by the pangoLEARN -> UShER mode switch even when the same pangolin-data version is used.

## Algorithmic Taxonomy

| Tool | Mechanism | Inputs | Output | Strength | Fails when |
|------|-----------|--------|--------|----------|------------|
| Pangolin UShER mode (O'Toole 2021 *Virus Evol* 7:veab064; Pongmoragot 2024 *Virus Evol* 10:vead085) | Parsimony placement on daily-updated UShER mutation-annotated tree | SARS-CoV-2 consensus | Pango lineage call | UShER is the default since v4; more accurate than pangoLEARN for recent / divergent lineages | Designation lag for emerging lineages; recombinants require manual Pango-X designation |
| Pangolin pangoLEARN mode | Random-forest classifier trained on pangolin-data | SARS-CoV-2 consensus | Pango lineage call | Fast | DEPRECATED mid-2023; less accurate than UShER for novel sub-lineages |
| Nextclade (Aksamentov 2021 *JOSS* 6:3773) | Reference-tree placement + clade assignment + mutation calling + QC | Viral consensus (multi-pathogen) | Clade + Pango + QC + mutations | Integrated alignment QC; mutation outliers; recombination indicators | Dataset version drift changes lineage-defining mutations |
| Nextstrain Augur (Huddleston 2021 *JOSS* 6:2906) | Python CLI for subsampling + alignment + tree + ancestral-trait + time-tree | Genomes + metadata + sampling config | Auspice JSON for visualization | End-to-end pipeline for curated surveillance builds | Subsampling configuration drives results more than data; nextstrain.org subsamples ~3000-5000 of millions |
| UShER + matUtils + matOptimize + RIPPLES (Turakhia 2021 *Nat Genet* 53:809) | Parsimony placement on daily MAT; SPR refinement; recombination detection | New consensus + existing MAT | Updated MAT, subtrees, recombinant calls | Pandemic-scale (millions of genomes) | Parsimony branch lengths systematically shorter than ML; re-estimate before downstream R_e |
| Freyja (Karthikeyan 2022 *Nature* 609:101) | Depth-weighted LAD regression on barcode-matrix mutation frequencies | Wastewater BAM + barcode | Per-lineage abundance | Recovers expected abundances down to ~5%; quantitative | Lineages absent from barcode invisible; barcode is forward-only -- cannot deconvolve lineages designated after barcode date |
| COJAC (Jahn 2022 *Nat Microbiol* 7:1151) | Co-occurrence of signature mutations on the same read pair | Wastewater BAM | Per-lineage presence / absence | More robust than per-site frequencies; detected Alpha 13 days before clinical | Single-read amplicons (no co-occurrence) cannot resolve; requires paired-end or long-read |
| alcov | Lineage deconvolution similar paradigm to Freyja | Wastewater BAM | Per-lineage abundance | Alternative to Freyja | Less benchmarked |
| lineagespot (Pechlivanis 2022 *Sci Rep* 12:2659) | R/Bioconductor lineage deconvolution from VCF + signature mutations | VCF + reference lineage mutations | Per-lineage abundance | R / Bioconductor integration | Less ML-driven; smaller community |
| Wenseleers / Bedford-Figgins multinomial logistic (Abousamra, Figgins, Bedford 2024 *PLoS Comput Biol* 20:e1012443) | Multinomial logistic regression on lineage frequencies over time | Lineage frequencies + dates | Growth advantage per lineage with 95% CI | Standard for outbreak.info / cov-lineages.org | Marginal CI for one lineage hides covariance with all others; early estimates inflated |
| 3SEQ (Boni 2007 *Genetics* 176:1035) | Triplet-based recombination detection | Aligned sequences | Recombinant candidates | General-purpose | High false-positive rate at low divergence |
| RDP4 / RDP5 (Martin 2015 *Virus Evol* 1:vev003) | Multiple-method recombination detection | Aligned sequences | Recombinant candidates | Multi-method consensus | Slow; parameter-sensitive |
| Bolotie (Varabyou 2021 *Bioinformatics* 37:2298) | SARS-CoV-2-specific recombination detection | SARS-CoV-2 consensus | Recombinant candidates | Tuned for SARS-CoV-2 sub-lineage divergence | Specialist tool |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| Assign lineage to a SARS-CoV-2 consensus | Pangolin with `--analysis-mode usher` (UShER default since v4) + Nextclade cross-check; pin pangolin-data and Nextclade dataset versions | pangoLEARN alone (deprecated); not pinning version (cross-lab calls diverge) |
| Detect emerging variants in wastewater | COJAC for early detection (co-occurrence on amplicon) + Freyja for quantitative tracking; pin Freyja barcode version | Naive site-frequency aggregation; comparing across barcode versions |
| Track lineage frequencies over time | Multinomial logistic regression (Wenseleers / Bedford-Figgins) OR Bayesian renewal equation; report covariance among lineages | Plotting raw counts without CI; reporting single-lineage growth advantage without covariance |
| Build a regional surveillance phylogeny | Nextstrain Augur pipeline; subsample to manageable size; TreeTime for dates; document subsampling | BEAST on raw 10k+ samples (intractable); not documenting subsampling |
| Compare wastewater results across labs | Same primer scheme + same Freyja barcode + same Pangolin / Nextclade version | Mixing primer schemes; mixing barcode versions; comparing across pangolin-data versions |
| QC a new SARS-CoV-2 genome | Nextclade (alignment QC; mutation outliers; recombination indicators) | Pangolin alone (passes confidently on bad genomes) |
| Detect recombinant lineages | Trust Pango-designation X-prefix assignments; for novel candidates use RDP5 / 3SEQ / Bolotie + manual review | Manual eyeballing of mutation patterns; ignoring designation lag |
| Phylogenetic context for outbreak | UShER + matUtils subtree extraction; re-estimate branch lengths via TreeTime for downstream R_e | Re-treeing from scratch every time |
| Estimate vaccine-escape risk | Lab assays (neutralisation, escape mutants) + structural prediction; genomic surveillance flags candidates | Pure genomic prediction without lab validation |
| Wastewater-to-cases conversion | Variant-specific shedding rate (Omicron BA.1 shed less per case than Delta); pin barcode + report uncertainty | Fixed RNA-to-cases ratio across variants is wrong; variant-specific shedding has been documented in the wastewater literature |

Methodology evolves; before any high-stakes lineage report, verify Pangolin's current default analysis-mode and Nextclade's bundled dataset against pango-designation issues for any emerging lineage.

## Pangolin Lineage Assignment With Version Pinning

**Goal:** Assign Pango lineages to SARS-CoV-2 consensus sequences using UShER mode (the default since v4; pangoLEARN deprecated mid-2023), with full pangolin-data version provenance preserved for reproducibility.

**Approach:** Always pass `--analysis-mode usher`; record `pangolin --all-versions` output alongside every lineage call; for published or regulatory output, pin pangolin-data to a specific release tag and re-run the whole archive whenever the version is updated.

```bash
pangolin sequences.fasta --analysis-mode usher --outfile lineage_report.csv
pangolin --all-versions > pangolin_versions.txt
```

`pangolin --all-versions` prints: pangolin executable version, pangolin-data version (weekly updated; mandatory pin for reproducibility), scorpio version, and constellations version. All four are version-sensitive; in published surveillance reports, pin all four.

## Nextclade With Dataset Pinning

**Goal:** Assign Nextstrain clade, Pango lineage, mutations, and QC flags to SARS-CoV-2 consensus sequences with explicit dataset version provenance.

**Approach:** Fetch the current dataset with `nextclade dataset get --name sars-cov-2 --output-dir nc_dataset/sars-cov-2`; record the `pathogen.json` tag / commit hash; run `nextclade run --input-dataset` on the pre-downloaded folder so the dataset version is locked in for the analysis.

```bash
nextclade dataset get --name sars-cov-2 --output-dir nc_dataset/sars-cov-2
NC_DATASET_TAG=$(jq -r '.tag // .version' nc_dataset/sars-cov-2/pathogen.json)

nextclade run \
    --input-dataset nc_dataset/sars-cov-2 \
    --output-tsv nextclade.tsv \
    --output-json nextclade.json \
    sequences.fasta

echo "nextclade_dataset_tag: ${NC_DATASET_TAG}" > nextclade.metadata
```

Different dataset versions assign different mutations as "lineage-defining" because internal-node placement can shift as the tree grows. Cross-version comparison of mutation reports is therefore method-dependent.

## Wastewater Lineage Deconvolution With Freyja

**Goal:** Estimate per-lineage abundance in a wastewater pooled sample with explicit handling of the barcode forward-only date constraint, primer-scheme awareness, and residual mass interpretation.

**Approach:** Confirm barcode date postdates sample collection; if not, `freyja barcode-build` from the current UShER tree; variant call with `freyja variants` then deconvolve with `freyja demix`; inspect the `resid` column (residual mass NOT assigned to known lineages; high resid indicates a novel lineage is invisible); apply primer-scheme-aware coverage masking; report variant-specific uncertainty.

```bash
freyja update

freyja variants \
    sample.bam \
    --variants sample.variants.tsv \
    --depths sample.depths.tsv \
    --ref reference.fa

freyja demix \
    sample.variants.tsv \
    sample.depths.tsv \
    --output sample.demix.tsv
```

The Freyja `--barcodes` (or default bundled) date MUST postdate the sample collection date. Lineages designated after the barcode date cannot be detected -- the demixing silently fails and presents as elevated abundance of the closest parent lineage. For samples potentially containing emerging lineages, regenerate barcodes:

```bash
freyja barcode-build \
    --pb-and-meta usher_tree.pb \
    --output-dir custom_barcodes
```

Subsequent methodological extensions to Karthikeyan have appeared in the wastewater literature, and recent benchmarks comparing the major deconvolution tools (Freyja, COJAC, alcov, lineagespot, LCS) confirm Freyja and COJAC consistently perform well, with performance degrading at low coverage and for divergent lineages.

## COJAC for Co-Occurrence Detection

**Goal:** Detect emerging variants in wastewater earlier than per-site frequency methods by requiring co-occurrence of two signature mutations on the same amplicon (read pair).

**Approach:** COJAC checks read pairs for joint occurrence of variant-defining mutations; the inferential leap is more robust because a single site can have shared mutations across lineages, but two signature mutations on the same read pair strongly imply a single lineage. Detected Alpha 13 days before clinical samples in Swiss data (Jahn 2022 *Nat Microbiol* 7:1151).

```bash
cojac cooc-mutbamscan \
    -a primer_scheme.bed \
    -m variants_definitions.yaml \
    -b sample.bam \
    -o sample.cooc.tsv
```

## Nextstrain Augur Pipeline

**Goal:** Build a curated regional surveillance phylogeny with subsampling, alignment, tree, ancestral-trait inference, and time-scaling -- in Auspice-visualisable format. The Nextstrain platform was introduced by Hadfield 2018 *Bioinformatics* 34:4121; Augur is the Python CLI (Huddleston 2021 *JOSS* 6:2906).

**Approach:** Pull the latest official pathogen build from github.com/nextstrain/<pathogen>; subsample to manageable size (typically 3000-5000 genomes per global build; smaller regional); document subsampling configuration explicitly (it drives the result more than the underlying data per Hodcroft 2021).

```bash
augur align --sequences seqs.fasta --reference-sequence ref.gb --output aligned.fasta
augur tree --alignment aligned.fasta --output tree.nwk
augur refine \
    --tree tree.nwk \
    --alignment aligned.fasta \
    --metadata meta.tsv \
    --output-tree refined.nwk \
    --output-node-data branch_lengths.json \
    --timetree \
    --root oldest \
    --coalescent skyline
augur ancestral --tree refined.nwk --alignment aligned.fasta --output-node-data nt_muts.json
augur translate --tree refined.nwk --ancestral-sequences nt_muts.json --reference-sequence ref.gb --output-node-data aa_muts.json
augur traits --tree refined.nwk --metadata meta.tsv --columns country region --output-node-data traits.json
augur export v2 \
    --tree refined.nwk \
    --metadata meta.tsv \
    --node-data branch_lengths.json nt_muts.json aa_muts.json traits.json \
    --output auspice.json
```

Hodcroft 2021 *Nature* 591:30 documented that Nextstrain subsampling configurations drive lineage-time estimates more than the underlying data. Two researchers using the official pipeline with different subsampling can get different MRCA dates and migration patterns from the same raw genomes.

## Per-Method Failure Modes

### pangolin-data version skew between labs

**Trigger:** Two labs submit the same consensus genome to Pangolin with different pangolin-data versions; the lineage call differs.

**Mechanism:** Lineage designation happens through pango-designation GitHub issues -- days-to-weeks before pangolin-data releases include the lineage. During the lag, the same genome is callable as the parent (older pangolin-data) or the child (current). pangolin-data is updated weekly.

**Symptom:** Cross-lab lineage prevalence comparisons over time show implausible jumps coinciding with pangolin-data release dates rather than biology.

**Fix:** Pin pangolin-data version explicitly with `pangolin --all-versions` recorded alongside every call. For published or regulatory output, re-run the WHOLE archive against a single pangolin-data version before reporting.

### Freyja barcode predates the sample collection date

**Trigger:** Wastewater sample collected after a new lineage was designated; Freyja barcode built before that designation.

**Mechanism:** Freyja barcodes are built from the UShER tree at a specific date; lineages designated AFTER the barcode date cannot be detected. The demixing silently fails -- the new lineage's signal is misassigned to its closest parent.

**Symptom:** Wastewater sample shows implausibly high abundance of a single parent lineage; new lineage that should be present is reported as 0%.

**Fix:** Run `freyja update` regularly; for samples potentially containing emerging lineages, regenerate barcodes with `freyja barcode-build` from the current UShER tree. Report `resid` (residual mass not assigned to known lineages); high resid indicates a novel lineage is being missed.

### ARTIC primer dropout misread as deletion

**Trigger:** SARS-CoV-2 surveillance using ARTIC V4.1 amplicons; new variant has mutation at primer site; amplicons 64 / 76 / 88-90 silently drop out.

**Mechanism:** When a primer fails to bind, the amplicon doesn't amplify; consensus calling produces N's or reference-derived calls in that region. This LOOKS LIKE a deletion in downstream analysis but is actually missing data. Itokawa 2020 *PLoS ONE* 15:e0239403 documented primer interactions specifically.

**Symptom:** "Deletion" calls cluster in known dropout amplicons; Pangolin / Nextclade lineage call shifts when masked positions are filled with reference.

**Fix:** Inspect per-amplicon coverage with `samtools depth -aa`; mask consensus positions in dropped amplicons (use Ns -- Pangolin and Nextclade handle Ns gracefully). Document primer scheme version (V3 / V4 / V4.1 / V5.3.2 / Midnight) per isolate.

### Recombinant assigned to one parent lineage

**Trigger:** A SARS-CoV-2 recombinant (e.g., XEC = KS.1.1 x KP.3.3) emerges; pango-designation has not yet issued the X-prefix designation; Pangolin assigns to one of the parents.

**Mechanism:** Pangolin in either mode assigns a recombinant to one parent lineage if no Pango-X designation exists yet. Identifying recombinants requires breakpoint detection (3SEQ, Bolotie, RDP4) and manual designation through pango-designation; the designation can lag emergence by weeks-to-months for novel recombinants.

**Symptom:** Outbreak interpretation conflates a recombinant lineage with its parent; transmissibility / immune-escape claims are wrong.

**Fix:** For any candidate emerging lineage with unusual mutations, run Bolotie or 3SEQ for recombination detection; cross-check Pangolin vs Nextclade lineage call; submit candidate recombinants to cov-lineages issue tracker if novel.

### pangoLEARN result reported as authoritative

**Trigger:** Pangolin run with `--analysis-mode pangolearn` (or via legacy Docker image that defaults to pangoLEARN); user reports the call.

**Mechanism:** Pongmoragot 2024 *Virus Evol* 10:vead085 demonstrated UShER mode is significantly more accurate for recent / divergent lineages. pangoLEARN was officially deprecated mid-2023.

**Symptom:** Cross-lab comparison reveals one lab using pangoLEARN (legacy) and another using UShER; calls differ at borderline lineages.

**Fix:** Switch to `--analysis-mode usher` (default since v4). For longitudinal datasets crossing the mid-2023 mode-switch, re-run the historical archive against UShER mode.

### Freyja barcode-build vs barcode_build flag

**Trigger:** Script written from older Freyja documentation using `freyja barcode_build` (underscore).

**Mechanism:** Current Freyja versions use `barcode-build` (hyphen); the underscore form may not be recognised.

**Symptom:** Subprocess fails with "unrecognized command".

**Fix:** Use `freyja barcode-build` (hyphen). Verify with `freyja --help`.

### Wenseleers / Bedford lineage-growth CI hides covariance

**Trigger:** Reporting a single lineage's growth advantage 95% CI from a multinomial logistic regression.

**Mechanism:** The CI for any single lineage is conditional on all other lineages being held at their estimated growth rates; the marginal CI hides covariance among lineages. Early growth-advantage estimates are systematically too large; they shrink as more time passes (alternative explanations become identifiable).

**Symptom:** Initial published growth advantage > later refined estimate; "outlier-fast" lineages later moderated.

**Fix:** Report the full multinomial covariance matrix or at minimum the rank-ordered growth advantages with simultaneous CIs. Cite Abousamra 2024 *PLoS Comput Biol* 20:e1012443.

### Nextstrain subsampling drives the result

**Trigger:** Nextstrain Augur build with default subsampling at 3000-5000 genomes from millions; user interprets the tree topology as authoritative.

**Mechanism:** Hodcroft 2021 *Nature* 591:30 commented that subsampling decisions drive lineage-time estimates more than the underlying data. Two researchers using the official Nextstrain pipeline with different subsampling configurations get different MRCA dates and migration patterns from the same raw genomes.

**Symptom:** Published Nextstrain tree differs from another analysis on the same raw data; conclusions sensitive to subsampling.

**Fix:** Document subsampling configuration explicitly in any Nextstrain build; run sensitivity analysis with alternative subsampling; treat MRCA dates and migration calls with appropriate uncertainty.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Pangolin "BA.2.86", Nextclade clade "23I" | Equivalent at different resolutions -- BA.2.86 is within 23I | Report both; Pango lineage for sub-clade resolution |
| Pangolin "BA.5.2", Nextclade "Unassigned" | Nextclade dataset older than pangolin-data; OR Nextclade QC failed | Update Nextclade dataset; re-run; inspect QC fields |
| Pangolin UShER and pangoLEARN disagree | pangoLEARN is the deprecated decision-tree classifier | Trust UShER call |
| Freyja shows 0% of expected lineage | Lineage absent from current barcode (post-dates barcode) | Rebuild barcodes (`freyja barcode-build`); confirm lineage is in the UShER tree the barcode is built from |
| Freyja confidence < 0.7 on dominant lineage | Sub-100x coverage OR amplicon dropout | Inspect per-amplicon coverage; consider re-sequencing; report as indeterminate |
| Nextclade and Pangolin disagree on recombinant | Recombinants inherently ambiguous; depends on which parent's SNPs dominate | Report as recombinant candidate; submit to cov-lineages if novel |
| Two consecutive pangolin-data releases call the same consensus differently | Lineage definitions revised between releases | Pin pangolin-data; record version + date alongside lineage |
| COJAC detects a variant Freyja does not | COJAC's co-occurrence requirement more sensitive at low abundance | Trust COJAC for early detection; Freyja for quantitative tracking |
| Wastewater Freyja result conflicts with clinical lineage prevalence | Barcode staleness; primer dropout in wastewater; faecal shedding rate varies by variant | Update barcode; check per-amplicon coverage; flag variant-specific shedding |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| Pangolin min coverage for lineage call | >=50% genome coverage (~14kb) | Pangolin convention |
| Nextclade QC stop-codon threshold | Per dataset; check `pathogen.json` | Nextclade dataset-specific |
| Freyja minimum coverage per site | >=10x typical | Freyja convention; per-site weighting accounts for variance |
| Freyja `resid` flag threshold | Project-specific; >0.1 typically indicates novel lineage missed | Freyja documentation |
| COJAC early-detection lead time vs clinical | Up to 13 days in Swiss data | Jahn 2022 *Nat Microbiol* 7:1151 |
| Karthikeyan 2022 wastewater Omicron lead | 11 days before clinical detection (San Diego) | Most-favourable configuration; subsequent retrospective analyses produced detection lags ranging from -5 to +3 days |
| ARTIC V4.1 known chronic dropouts | Amplicons 64, 76, 88-90 | Itokawa 2020 / community documentation |
| Augur subsampling typical | 3000-5000 genomes per global build | Nextstrain convention; document explicitly |
| Multinomial logistic growth-advantage early estimate inflation | Systematically too large; shrinks over time | Abousamra 2024 *PLoS Comput Biol* 20:e1012443 |
| GISAID 2024-2025 weekly submission rate | ~5,000-20,000/week (down from ~500,000/week peak early 2022) | Community-documented; emerging-lineage detection lag increased |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `pangolin --inference usher` rejected | Flag is `--analysis-mode usher` | `--analysis-mode usher` |
| `nextclade run --input-dataset DIR` rejected on v2 | v2 used `--input-dataset` differently | Verify `nextclade --version`; v3+ accepts pre-downloaded dataset folder |
| `freyja barcode_build` rejected | Current is `barcode-build` (hyphen) | Use hyphen form |
| Pangolin output column not present | Column names changed between major releases | Introspect output schema; `pangolin --all-versions` |
| Freyja silently misassigns new lineage | Barcode predates lineage designation | Rebuild barcodes; check `resid` |
| Nextclade and Pangolin disagree | Different versions; recombinant; QC | Update both; reconcile per table |
| ARTIC consensus has Ns clustered in one region | Primer dropout in that amplicon | Mask the amplicon; document scheme version |
| Lineage frequency shows implausible jump | pangolin-data version drift | Pin version; re-run archive |
| Augur tree topology changes between runs | Subsampling randomness | Pin random seed; document subsampling |
| Augur `refine` requires `--root` | Shallow tree without explicit root strategy | `--root best` / `oldest` / `residual` |
| Wastewater Freyja result differs from clinical | Barcode staleness or primer-scheme mismatch | Update barcode; document scheme; check coverage |
| COJAC misses a known variant | Single-read amplicons (no co-occurrence) | Re-sequence with paired-end or long-read |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Pangolin version?" | `pangolin --all-versions` recorded; pinned for the analysis; archive re-run on dataset update |
| "Nextclade dataset version?" | Dataset tag from `pathogen.json` recorded; pre-downloaded folder used to lock the version |
| "Why UShER not pangoLEARN?" | pangoLEARN deprecated mid-2023 (Pongmoragot 2024); UShER default since v4 |
| "How were ARTIC dropouts handled?" | Per-amplicon coverage checked; failed amplicons masked; primer scheme documented per isolate |
| "Were recombinants checked for?" | Bolotie / 3SEQ run on candidates; cross-checked Pangolin vs Nextclade; submitted to cov-lineages for novel candidates |
| "Wastewater barcode date?" | Barcode date postdates sample collection; `freyja barcode-build` from current UShER tree if needed |
| "Wastewater-to-cases conversion?" | Variant-specific shedding rate flagged in the wastewater literature; not assumed constant |
| "Lineage growth-advantage CI?" | Multinomial covariance reported; early estimates noted as inflated (Abousamra 2024) |
| "Nextstrain subsampling?" | Configuration explicit; sensitivity analysis run; MRCA / migration treated with uncertainty (Hodcroft 2021) |

## References

- O'Toole Á, Scher E, Underwood A et al (2021) Assignment of epidemiological lineages in an emerging pandemic using the pangolin tool. *Virus Evol* 7(2):veab064. doi:10.1093/ve/veab064
- Aksamentov I, Roemer C, Hodcroft EB, Neher RA (2021) Nextclade: clade assignment, mutation calling and quality control for viral genomes. *J Open Source Softw* 6(67):3773. doi:10.21105/joss.03773
- Karthikeyan S, Levy JI, De Hoff P et al (2022) Wastewater sequencing reveals early cryptic SARS-CoV-2 variant transmission. *Nature* 609(7925):101-108. doi:10.1038/s41586-022-05049-6
- Hadfield J, Megill C, Bell SM et al (2018) Nextstrain: real-time tracking of pathogen evolution. *Bioinformatics* 34(23):4121-4123. doi:10.1093/bioinformatics/bty407
- Huddleston J, Hadfield J, Sibley TR et al (2021) Augur: a bioinformatics toolkit for phylogenetic analyses of human pathogens. *J Open Source Softw* 6(57):2906. doi:10.21105/joss.02906
- Turakhia Y, Thornlow B, Hinrichs AS et al (2021) Ultrafast Sample placement on Existing tRees (UShER) enables real-time phylogenetics for the SARS-CoV-2 pandemic. *Nat Genet* 53(6):809-816. doi:10.1038/s41588-021-00862-7
- Pongmoragot J, Pearson C, Borg ML et al (2024) Comparison of UShER-based and pangoLEARN-based Pangolin lineage assignments for SARS-CoV-2 sequences. *Virus Evol* 10(1):vead085. doi:10.1093/ve/vead085
- Jahn K, Dreifuss D, Topolsky I et al (2022) Early detection and surveillance of SARS-CoV-2 genomic variants in wastewater using COJAC. *Nat Microbiol* 7(8):1151-1160. doi:10.1038/s41564-022-01185-x
- Pechlivanis N, Tsagiopoulou M, Maniou MC et al (2022) Detecting SARS-CoV-2 lineages and mutational load in municipal wastewater and a use-case in the metropolitan area of Thessaloniki, Greece. *Sci Rep* 12:2659. doi:10.1038/s41598-022-06625-6
- Itokawa K, Sekizuka T, Hashino M, Tanaka R, Kuroda M (2020) Disentangling primer interactions improves SARS-CoV-2 genome sequencing by multiplex tiling PCR. *PLoS ONE* 15(9):e0239403. doi:10.1371/journal.pone.0239403
- Hodcroft EB, De Maio N, Lanfear R et al (2021) Want to track pandemic variants faster? Fix the bioinformatics bottleneck. *Nature* 591(7848):30-33. doi:10.1038/d41586-021-00525-x
- Abousamra E, Figgins M, Bedford T (2024) Fitness models provide accurate short-term forecasts of SARS-CoV-2 variant frequency. *PLoS Comput Biol* 20(9):e1012443. doi:10.1371/journal.pcbi.1012443
- Boni MF, Posada D, Feldman MW (2007) An exact nonparametric method for inferring mosaic structure in sequence triplets. *Genetics* 176(2):1035-1047. doi:10.1534/genetics.106.068874
- Martin DP, Murrell B, Golden M, Khoosal A, Muhire B (2015) RDP4: detection and analysis of recombination patterns in virus genomes. *Virus Evol* 1(1):vev003. doi:10.1093/ve/vev003
- Varabyou A, Pockrandt C, Salzberg SL, Pertea M (2021) Rapid detection of inter-clade recombination in SARS-CoV-2 with Bolotie. *Bioinformatics* 37(15):2298-2300. doi:10.1093/bioinformatics/btab080

## Related Skills

- pathogen-typing - Lineage assignment overlaps with typing; this skill owns longitudinal frequency tracking and wastewater deconvolution
- phylodynamics - Lineage-stratified BDSKY / BICEPS R_e estimation runs downstream of lineage assignment
- transmission-inference - SARS-CoV-2 cluster definition combines lineage + 0-2 SNPs + epi link
- amr-surveillance - Antiviral drug-resistance mutation tracking is the variant-surveillance analogue for AMR
- phylogenetics/modern-tree-inference - IQ-TREE / RAxML for non-UShER topology
- phylogenetics/tree-io - Tree parsing and format conversion for Augur output
- comparative-genomics/whole-genome-alignment - Reference-based alignment for SNP calling
- variant-calling/vcf-basics - VCF for lineage-defining mutations
- variant-calling/variant-calling - Variant calling for wastewater (lofreq, ivar)
- variant-calling/filtering-best-practices - Per-amplicon coverage filtering for ARTIC
- read-alignment/bwa-alignment - Read mapping upstream
- read-alignment/minimap2-alignment - Long-read alignment for ARTIC-Midnight 1200
- read-qc/quality-reports - Sequencing QC upstream
- database-access/sra-data - SRA / INSDC retrieval; GISAID is a separate restricted-access source
- data-visualization/multipanel-figures - Lineage frequency / wastewater plotting
- workflows/somatic-variant-pipeline - End-to-end orchestration patterns
<!-- END FILE: epidemiological-genomics/variant-surveillance/SKILL.md -->

<!-- END CATEGORY: epidemiological-genomics -->

