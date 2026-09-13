---
slug: bio-phasing-imputation-integrated
version: 1.0.0
displayName: "单倍型相位与Imputation / Haplotype phasing and genotype imputation"
name: bio-phasing-imputation-integrated
summary: >-
  中文：单倍型相位与Imputation综合技能，整合 4 个相关专题，覆盖单倍型相位与基因型imputation：SHAPEIT5、Beagle、Minimac4、IMPUTE5、GLIMPSE2。 English: Integrated Haplotype phasing and genotype imputation skill covering 4 related topics, including Haplotype phasing and genotype imputation: SHAPEIT5, Beagle, Minimac4, IMPUTE5, GLIMPSE2.
description: >-
  中文：这是一个面向单倍型相位与Imputation的综合生物信息学 Skill，整合当前分类下 4 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：单倍型相位与基因型imputation：SHAPEIT5、Beagle、Minimac4、IMPUTE5、GLIMPSE2。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Beagle, SHAPEIT5, bcftools。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Haplotype phasing and genotype imputation, combining 4 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Haplotype phasing and genotype imputation: SHAPEIT5, Beagle, Minimac4, IMPUTE5, GLIMPSE2. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Beagle, SHAPEIT5, bcftools. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# phasing-imputation 分类 Skill 整合版

> 本文件整合同一主分类目录下 4 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: phasing-imputation -->

## 子目录：phasing-imputation/genotype-imputation

<!-- BEGIN FILE: phasing-imputation/genotype-imputation/SKILL.md -->
---
name: bio-phasing-imputation-genotype-imputation
description: Imputes untyped genotypes against a phased reference panel with Beagle, Minimac4, or IMPUTE5 (array data) or from genotype likelihoods with GLIMPSE2, QUILT2, or STITCH (low-coverage WGS), producing per-variant dosages (DS) with a self-estimated quality (Beagle DR2, Minimac R2, IMPUTE INFO). Covers why the honest output is a dosage posterior not a hard call, why GWAS regresses on DS, why the quality metric is an ESTIMATE of r2 from posterior spread (not validation against truth), the DS/GP/HDS fields, the phasing prerequisite, chunking, chrX ploidy, the Michigan/TOPMed servers (the only access to HRC/TOPMed), and low-coverage WGS as the modern array replacement. Use when increasing variant density for GWAS, harmonizing arrays, inferring untyped variants, or imputing low-coverage sequence. Phase first with haplotype-phasing; prepare the panel with reference-panels; filter with imputation-qc; the GWAS test is population-genetics/association-testing; end-to-end orchestration is workflows/gwas-pipeline.
tool_type: cli
primary_tool: Beagle
---

## Version Compatibility

Reference examples tested with: Beagle 5.4 (22Jul22), Minimac4 4.1+, IMPUTE5 1.2, GLIMPSE2, bcftools 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Minimac4 (4.x) uses POSITIONAL arguments (`minimac4 panel.msav target.vcf.gz`); the old `--refHaps`/`--haps`/`--prefix`/`--cpus` style is Minimac3 and obsolete. Beagle 5.x emits `DR2`, `AF`, and `IMP` only (`AR2` is a legacy 4.x field) and its default `ne=100000` (not 1,000,000). The panel build (GRCh37 vs GRCh38) must match the data; record the panel name, version, and build with every result.

# Genotype Imputation -- Inferring Untyped Genotypes as Dosages

**"Fill in the variants I did not directly measure"** -> Align the (phased or low-coverage) sample to a reference panel of phased haplotypes and infer the untyped alleles via the Li-Stephens HMM - because the output is a posterior over genotypes summarized as a dosage with a self-estimated quality, not a measured call, so the uncertainty must be carried downstream.
- CLI: `java -jar beagle.jar gt=phased.vcf.gz ref=panel.bref3 map=plink.chr20.map out=imputed` (or `minimac4 panel.msav phased.vcf.gz`, or GLIMPSE2 for low-coverage WGS)

Scope: imputing untyped genotypes from a panel (array data) or from genotype likelihoods (low-coverage WGS), the dosage/quality output, chunking, chrX, and the servers. Phasing the input -> haplotype-phasing. Panel selection/preparation/strand -> reference-panels. Quality metrics and filtering thresholds -> imputation-qc. The GWAS test on the dosages -> population-genetics/association-testing. The genotype likelihoods that low-coverage imputation consumes -> variant-calling/vcf-basics. End-to-end orchestration -> workflows/gwas-pipeline.

## The Single Most Important Modern Insight -- An Imputed Genotype Is a Posterior, and the Deliverable Is a Dosage Plus a Self-Estimated Quality, Not a Hard Call

Imputation aligns a sparsely-genotyped (or low-coverage-sequenced) sample to a densely-typed reference panel of phased haplotypes and infers, via a Li-Stephens HMM, the alleles at positions the sample never observed (Browning 2018 *Am J Hum Genet* 103:338). The output at each untyped variant is a distribution, summarized as an expected allelic dosage in [0,2]. Three facts define the field:

1. **Downstream analysis uses dosages, not hard genotypes.** The dosage DS is the conditional expectation E[genotype | data, panel], the minimum-variance summary; hard-calling forces an uncertain 0.5 dosage to 0 or 1, injecting genotype error that attenuates effects and inflates standard errors. GWAS regresses the trait on DS -> population-genetics/association-testing.
2. **The quality metric (Beagle DR2, Minimac R2, IMPUTE INFO) is an ESTIMATE of r2 from the posterior spread, computed without ever seeing the truth.** Poorly-imputed dosages shrink toward the allele-frequency mean 2p, so low posterior variance relative to the binomial expectation 2p(1-p) flags a low-confidence site. This is NOT a validation against held-out genotypes (that is empirical r2 / EmpRsq, a masked-site quantity). Say "DR2/R2/INFO is an estimate of imputation quality," never "the imputation accuracy was 0.9" as if measured. The metric also cannot detect panel-ancestry mismatch -> imputation-qc.
3. **Low-coverage WGS (0.5-4x) plus GLIMPSE2 has become a credible array replacement.** Because it samples the whole genome rather than a fixed ascertained SNP set, it imputes rare variants and under-represented ancestries better than a dense array at comparable cost (Rubinacci 2023 *Nat Genet* 55:1088). The input is genotype likelihoods, not calls; the array-vs-low-coverage-WGS choice is an ascertainment decision (see Array vs Low-Coverage WGS below).

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| Minimac4 | Das 2016 *Nat Genet* 48:1284 | array imputation; msav/m3vcf panel; the server engine; positional-arg CLI | server-style imputation; meta-imputation |
| Beagle 5.x | Browning 2018 *Am J Hum Genet* 103:338 | Java; phases unphased input AND imputes; bref3 panel | one tool for phase + impute, no compile |
| IMPUTE5 | Rubinacci 2020 *PLoS Genet* 16:e1009049 | PBWT pre-selection then LS HMM; sub-linear in panel size | very large reference panels; local speed |
| GLIMPSE2 | Rubinacci 2023 *Nat Genet* 55:1088 | low-coverage WGS imputation from genotype likelihoods; chunk/split/phase/ligate | 0.5-4x WGS with a panel |
| QUILT2 | Davies 2021 *Nat Genet* 53:1104 | low-coverage, panel-based, read-aware | long-read / haplotagged / ancient DNA / cfDNA |
| STITCH | Davies 2016 *Nat Genet* 48:965 | low-coverage, REFERENCE-FREE; learns ancestral haplotypes by EM | no panel exists (non-model organisms) |
| Michigan / TOPMed servers | Das 2016 *Nat Genet* 48:1284 | Eagle2 phasing + Minimac4; the only access to HRC/TOPMed | turnkey, access-controlled panels |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Array data, want HRC/TOPMed and a turnkey pipeline | TOPMed or Michigan Imputation Server | the only sanctioned access to those panels; runs Eagle2 + Minimac4 |
| Array data, local run, very large panel, want speed | IMPUTE5 (PBWT) or Minimac4 | sub-linear scaling in panel size |
| Array data, local, one tool for phase + impute | Beagle 5.x | phases unphased gt= input itself; bref3 panel |
| Low-coverage WGS (0.5-4x), have a panel | GLIMPSE2 (chunk -> split-reference -> phase -> ligate) | the standard; imputes from genotype likelihoods |
| Low-coverage, read-aware / long-read / ancient DNA / cfDNA | QUILT2 | per-read, base-quality-aware |
| Low-coverage, NO reference panel (non-model organism) | STITCH | learns ancestral haplotypes reference-free |
| Need the panel selected/prepared first | -> reference-panels | the panel is the prior |
| Need the input phased first (Minimac4, IMPUTE5) | -> haplotype-phasing | those engines require a phased target |
| Filter the imputed output before analysis | -> imputation-qc | DR2/R2/INFO + MAF floor |
| The GWAS test on the dosages | -> population-genetics/association-testing | downstream |

## Array vs Low-Coverage WGS: the Imputation-Input Fork

The upstream decision is how to generate the genotypes that will be imputed, and it is an ascertainment question, not just an accuracy one. An array assays a fixed, designed SNP set (biased to its design population); low-coverage WGS samples whatever is in the genome.

| | SNP array + pre-phase + impute | Low-coverage WGS (~0.5-4x) + impute from genotype likelihoods |
|---|---|---|
| Input to the HMM | hard genotype calls (array error is tiny) | genotype LIKELIHOODS (PL/GL); a hard call at 1x is mostly noise |
| Ascertainment | FIXED - only the designed SNPs, biased to the design population | UNBIASED - whatever is in the genome is observed |
| Rare variants | limited by the array scaffold and panel | matches or beats dense arrays (Rubinacci 2021 *Nat Genet* 53:120) |
| Under-represented ancestry | poor (no good array, panel-mismatched) | the main route around array/panel bias |
| Tools | Beagle / Minimac4 / IMPUTE5 | GLIMPSE2 (panel) / STITCH (no panel) |

The judgment: common-variant GWAS in a well-paneled ancestry -> array plus imputation is cheap and adequate; rare variants, under-represented ancestry, or a need for unbiased genome-wide ascertainment -> low-coverage WGS plus genotype-likelihood imputation, the direction the field is moving as sequencing costs fall. Low-coverage WGS is only as good as its panel and its likelihoods (bad mapping, contamination, or damage produce garbage GLs that impute garbage).

## Output Formats and Why Dosages

The central object is the posterior genotype distribution; everything else summarizes it. Request the fields up front (Minimac4 `-f GT,DS,HDS,GP`; Beagle `gp=true ap=true`).

| FORMAT | Meaning | Shape |
|--------|---------|-------|
| GP | genotype probabilities P(0/0),P(0/1),P(1/1); the full posterior | 3 values summing to 1 |
| DS | allelic dosage = P(0/1) + 2*P(1/1) = E[genotype]; the GWAS field | 1 value in [0,2] |
| HDS | haploid (phased per-haplotype) dosage; DS = HDS1 + HDS2 (Minimac4/GLIMPSE) | 2 values, each [0,1] |
| AP1/AP2 | Beagle allele probabilities (P(ALT) per haplotype); DS = AP1 + AP2 (with ap=true) | 1 value each [0,1] |
| GT | hard best-guess genotype (argmax); lossy, discards uncertainty | 0/0, 0/1, 1/1 |

GP is the distribution; DS is its mean - two variants with different GP spreads can share a DS. Use DS for association (it propagates the uncertainty); use HDS/AP for phased/allele-specific analyses. Beagle computes GP from allele probabilities assuming Hardy-Weinberg and sets GT from the per-haplotype argmax, so its GT can occasionally disagree with the argmax of its own GP.

## The Phasing Prerequisite

The reference panel is phased haplotypes; the target must align to that haplotype structure two ways:
- **Pre-phase then impute** (Minimac4, IMPUTE5): phase the target FIRST (Eagle2 or SHAPEIT) into haplotypes, then impute. The server default (Eagle2 -> Minimac4) and the fast local pattern -> haplotype-phasing.
- **Phase-and-impute together** (Beagle, GLIMPSE2): the tool phases internally. Low-coverage tools MUST do this, because there is no confident genotype to phase up front; GLIMPSE2 alternates haploid imputation and phasing, and gains accuracy by imputing all target samples jointly.

## Low-Coverage WGS Workflow (GLIMPSE2)

The input is genotype likelihoods (PL/GL), not calls, because at 0.5-4x no genotype is certain. GLIMPSE2 can read BAM/CRAM directly (computing GLs internally) or a GL BCF made with `bcftools mpileup ... -T panel_sites.vcf.gz | bcftools call -Aim -C alleles -T panel_sites.tsv.gz` (the `-C alleles` constraint needs the panel sites supplied to `call` via `-T`; note the two `-T` files differ in format - a VCF for mpileup, a tab-delimited sites file for call). The pipeline:

1. `GLIMPSE2_chunk` defines windows with buffers.
2. `GLIMPSE2_split_reference` precomputes a binary panel per chunk (the speed innovation that made UK Biobank-scale imputation feasible).
3. `GLIMPSE2_phase` imputes and phases per chunk (`--bam-list` or `--input-gl`; `--ne` default 100000).
4. `GLIMPSE2_ligate` stitches chunks using the overlap buffers to keep phase. Output FORMAT: GT, DS, GP, HS plus a per-variant INFO score.

For chrX with GLIMPSE2, declare each sample's ploidy with `--samples-file` (sample and copy number) and run the PAR/nonPAR split as for the array tools (male nonPAR is haploid) -> reference-panels.

## Imputation Servers

The Michigan (now MIS2) and TOPMed servers run Eagle2 phasing + Minimac4 imputation server-side and are the ONLY sanctioned access to HRC and TOPMed (those panels are controlled-access, not downloadable). Upload a per-chromosome VCF, select the panel, build, and population; the server runs allele-frequency QC and strand-flip detection, phases, imputes in chunks, and returns per-chromosome VCFs in GT,DS,GP plus a Minimac info file with R2 and a QC report. Results are encrypted with a one-time password and auto-deleted after a few days. The reproducibility cost: the panel version (HRC r1.1 vs TOPMed r2 vs r3), tool version, and build can change between runs, so record exactly which server/panel/version produced a result.

## Per-Method Failure Modes

### Obsolete Minimac4 syntax
**Trigger:** `minimac4 --refHaps panel.m3vcf --haps study.vcf --prefix out`. **Mechanism:** that is Minimac3; Minimac4 4.x takes positional args. **Symptom:** the command errors or is not recognized. **Fix:** `minimac4 panel.msav target.phased.vcf.gz -o imputed.vcf.gz -f GT,DS,HDS,GP -t 8`; build the panel with `minimac4 --compress-reference`.

### Imputing unphased input to a pre-phase engine
**Trigger:** feeding unphased genotypes to Minimac4 or IMPUTE5. **Mechanism:** those engines assume a phased target aligned to the panel haplotypes. **Symptom:** garbage or refused input. **Fix:** phase first (Eagle2/SHAPEIT) -> haplotype-phasing, or use Beagle/GLIMPSE2 which phase internally.

### Imputing cases and controls separately
**Trigger:** running imputation per batch (cases, then controls, or per cohort). **Mechanism:** batch-differential imputation quality at a variant creates artifactual genotype structure correlated with phenotype. **Symptom:** genome-wide-significant hits that fail to replicate; every single-batch QC metric passes. **Fix:** impute all samples together (or harmonize panels/versions and check that quality does not differ by batch) -> imputation-qc.

### Hard-calling the dosage
**Trigger:** thresholding DS to 0/1/2 for association. **Mechanism:** discards the posterior uncertainty, worst at low-R2 rare variants. **Symptom:** lost power read as a true null. **Fix:** regress on DS (PLINK2 `dosage=DS`, SNPTEST, REGENIE, BOLT-LMM all accept dosages).

### Missing DS field
**Trigger:** a downstream tool cannot find dosages. **Mechanism:** the FORMAT fields were not requested. **Symptom:** only GT or GP present. **Fix:** request `-f GT,DS,HDS,GP` (Minimac4) or `gp=true ap=true` (Beagle) at run time.

### Genome build or strand not aligned to the panel
**Trigger:** GRCh37 data against a GRCh38 panel, or unflipped palindromic SNPs. **Mechanism:** positions/alleles disagree with the panel; the HMM copies wrong templates. **Symptom:** near-zero accuracy across regions, no error. **Fix:** align build and strand before imputing -> reference-panels.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Regress on DS (dosage), not hard GT | Browning 2018 *Am J Hum Genet* 103:338 | DS = E[genotype | data, panel] is the minimum-variance estimator; hard-calling injects error |
| Beagle `ne=100000` (default) | Beagle 5.x default | effective population size for the HMM; not 1,000,000 |
| Beagle `window=40.0` / `overlap=2.0` cM | Beagle 5.x defaults | window must be >= 1.1x overlap; rarely tuned |
| Impute all samples together | Browning 2018 *Am J Hum Genet* 103:338 (framing) | separate case/control imputation manufactures false associations -> imputation-qc |
| Low-coverage sweet spot ~0.5-4x | Rubinacci 2023 *Nat Genet* 55:1088 | GLIMPSE2 accuracy range; ~1x is array-competitive |
| Request DS explicitly (Minimac4 default is GT,DS) | Minimac4 docs | HDS/GP for phased/probabilistic uses must be named |
| Post-imputation R2/DR2/INFO filter (a QC decision, not a default) | -> imputation-qc | the imputer's number is the INPUT to filtering, not a tool default |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `minimac4 --refHaps` not recognized | Minimac3 syntax | use positional args: `minimac4 panel.msav target.vcf.gz -o out` |
| Beagle OutOfMemoryError | JVM heap too small / whole genome one job | raise `-Xmx`; impute per chromosome |
| No DS in output | fields not requested | `-f GT,DS,HDS,GP` (Minimac4) / `gp=true ap=true` (Beagle) |
| Imputation accuracy near zero across a region | build/strand mismatch to the panel | align build and strand first -> reference-panels |
| Hits do not replicate | cases/controls imputed separately, or hard-called | impute together; regress on dosages -> imputation-qc |
| Engine errors on multiallelic sites | non-biallelic input | `bcftools norm -m -any` first -> variant-calling/variant-normalization |
| Cannot download HRC/TOPMed | controlled-access panels | use the imputation server |

## References

- Das S, Forer L, Schonherr S, et al. 2016. Next-generation genotype imputation service and methods. *Nat Genet* 48:1284-1287.
- Browning BL, Zhou Y, Browning SR. 2018. A one-penny imputed genome from next-generation reference panels. *Am J Hum Genet* 103:338-348.
- Browning BL, Tian X, Zhou Y, Browning SR. 2021. Fast two-stage phasing of large-scale sequence data. *Am J Hum Genet* 108:1880-1890.
- Rubinacci S, Delaneau O, Marchini J. 2020. Genotype imputation using the Positional Burrows-Wheeler Transform. *PLoS Genet* 16:e1009049.
- Rubinacci S, Ribeiro DM, Hofmeister RJ, Delaneau O. 2021. Efficient phasing and imputation of low-coverage sequencing data using large reference panels. *Nat Genet* 53:120-126.
- Rubinacci S, Hofmeister RJ, Sousa da Mota B, Delaneau O. 2023. Imputation of low-coverage sequencing data from 150,119 UK Biobank genomes. *Nat Genet* 55:1088-1090.
- Davies RW, Kucka M, Su D, et al. 2021. Rapid genotype imputation from sequence with reference panels. *Nat Genet* 53:1104-1111.
- Davies RW, Flint J, Myers S, Mott R. 2016. Rapid genotype imputation from sequence without reference panels. *Nat Genet* 48:965-969.
- McCarthy S, Das S, Kretzschmar W, et al. 2016. A reference panel of 64,976 haplotypes for genotype imputation. *Nat Genet* 48:1279-1283.
- Taliun D, Harris DN, Kessler MD, et al. 2021. Sequencing of 53,831 diverse genomes from the NHLBI TOPMed Program. *Nature* 590:290-299.

## Related Skills

- haplotype-phasing - Pre-phasing the target (required by Minimac4 and IMPUTE5)
- reference-panels - Select and prepare the panel (the prior) and align build/strand
- imputation-qc - Filter by DR2/R2/INFO and MAF; the metric is an estimate, not truth
- variant-calling/vcf-basics - Genotype likelihoods (PL/GL) for low-coverage imputation
- variant-calling/variant-normalization - Split multiallelics before imputation
- population-genetics/association-testing - GWAS test on the imputed dosages
- clinical-databases/polygenic-risk - Polygenic scores from imputed dosages
- workflows/gwas-pipeline - End-to-end QC -> phase -> impute -> associate
<!-- END FILE: phasing-imputation/genotype-imputation/SKILL.md -->

## 子目录：phasing-imputation/haplotype-phasing

<!-- BEGIN FILE: phasing-imputation/haplotype-phasing/SKILL.md -->
---
name: bio-phasing-imputation-haplotype-phasing
description: Estimates haplotype phase from population linkage disequilibrium with SHAPEIT5, SHAPEIT4, Eagle2, or Beagle - turning unphased genotypes (0/1) into phased haplotypes (0|1) for imputation input, compound-heterozygote calls, HLA typing, or population genetics. Covers why statistical phase is an INFERENCE (not a measurement) whose error concentrates at rare variants, why a genome-wide switch-error rate hides catastrophic rare-variant error and must be reported MAC-stratified, the SHAPEIT5 common-scaffold-then-rare design (phase_common, ligate, phase_rare, switch), reference-based vs within-cohort phasing, the build-matched genetic map, chrX male-haploid handling, and the switch-vs-flip-vs-Hamming distinction. Use when phasing genotypes before imputation, for compound-het/ASE/HLA, or benchmarking against trios. Read-backed / molecular phasing (long reads, Hi-C) is long-read-sequencing/haplotype-phasing; panel choice is reference-panels; imputation is genotype-imputation.
tool_type: cli
primary_tool: SHAPEIT5
---

## Version Compatibility

Reference examples tested with: SHAPEIT5 5.1.1, Eagle 2.4.1, Beagle 5.4 (22Jul22), bcftools 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

SHAPEIT4 to SHAPEIT5 changed the CLI substantially: SHAPEIT5 is a SUITE of binaries (`phase_common`, `phase_rare`, `ligate`, `switch`), not a single `shapeit` command, and `phase_common` is the engine formerly known as SHAPEIT4. The genetic map and the reference panel must match the data's genome build (GRCh37 vs GRCh38); a build-mismatched map silently degrades phasing. PBWT and Ne defaults have drifted between betas; confirm against the installed `--help`.

# Statistical Haplotype Phasing -- Inferring Phase From Population LD

**"Resolve which alleles sit together on each chromosome"** -> Estimate haplotype phase from population linkage disequilibrium via the Li-Stephens HMM - because phase is INFERRED statistically from how haplotypes are shared across a population, not read off the genotype, so a switch error is a model uncertainty (the rate, not zero, is the deliverable), not a typo.
- CLI: `phase_common --input target.bcf --filter-maf 0.001 --map chr20.b38.gmap.gz --region chr20 --output scaffold.bcf` then `ligate` then `phase_rare` (SHAPEIT5), or Eagle2/Beagle for common-variant phasing

Scope: population/statistical phasing of array or sequence genotypes for imputation input, compound-het/ASE/HLA, and population genetics. Read-backed / molecular single-sample phasing (long reads, Hi-C, 10x linked reads) is a PHYSICALLY DIFFERENT signal -> long-read-sequencing/haplotype-phasing (the two are easily conflated; do not run SHAPEIT on long-read evidence or trust statistical phase for a private clinical variant). Panel choice -> reference-panels. Imputation against a panel -> genotype-imputation. The input VCF and biallelic normalization -> variant-calling/variant-normalization. End-to-end orchestration -> workflows/gwas-pipeline.

## The Single Most Important Modern Insight -- A Phased Haplotype Is a Statistical Estimate, and Its Error Concentrates Exactly Where the Biology of Interest Lives

Statistical phasing reconstructs which alleles are on the same chromosome by borrowing LD across many individuals or a reference panel (Delaneau 2019 *Nat Commun* 10:5436). That works beautifully for common variants in LD with their neighbors and fails, by construction, for rare variants - which are young, carried by few people, and in LD with almost nothing. Three facts drive every decision:

1. **The genome-wide switch-error rate lies, because it is dominated by easy common sites.** A headline "switch error rate 0.3%" is averaged over millions of common heterozygous sites and says nothing about the singleton or doubleton that is most likely to be the compound-het, the de-novo, or the pathogenic allele of interest - those are phased at MAC-dependent accuracy an order of magnitude worse, and a true singleton is essentially a coin flip without special machinery (Hofmeister 2023 *Nat Genet* 55:1243). Report accuracy stratified by minor allele count, never as one number.
2. **The deliverable is a switch-error rate against an independent truth set, not the tool name.** "We used SHAPEIT" is not a switch-error rate. A switch error changes which haplotype an allele sits on without changing any genotype, so it is invisible to every per-site genotype QC; for any phase-dependent claim, measure the rate against a trio (Mendelian truth via `switch --pedigree`) or read-backed truth.
3. **The modern arc is the scaffold design, and rare-variant phasing needs biobank scale to work at all.** SHAPEIT5 phases common variants into a fixed, near-perfect scaffold, then places each rare allele onto it by PBWT/IBD haplotype matching - which depends on finding a long shared haplotype, itself a function of cohort size. This is why rare-variant phasing in a small cohort cannot be trusted for a cis/trans call without orthogonal (trio or read-backed) evidence.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| SHAPEIT5 | Hofmeister 2023 *Nat Genet* 55:1243 | suite (phase_common/phase_rare/ligate/switch); scaffold design for rare/singleton phasing; PBWT | biobank-scale WGS/WES; rare-variant phasing |
| SHAPEIT4 (= phase_common engine) | Delaneau 2019 *Nat Commun* 10:5436 | sub-linear common-variant phasing; integrates panels, scaffolds, read-backed phase | common-variant phasing / pre-phasing; legacy |
| Eagle2 | Loh 2016 *Nat Genet* 48:1443 | HMM + PBWT-derived HapHedge; reference-based (`--vcfRef`) and within-cohort | array data; the classic imputation-server phaser |
| Beagle 5.x | Browning 2021 *Am J Hum Genet* 108:1880 | Java; does BOTH phasing (gt=, no ref=) and imputation; two-stage for sequence | one tool for phase and impute; no compile |
| Trio / pedigree phasing | (Mendelian transmission) | deterministic phase where the trio is informative | gold standard; validating other phasers via `switch` |
| WhatsHap (boundary) | Patterson 2015 *J Comput Biol* 22:498 | read-backed phasing (weighted MEC) from aligned reads | -> long-read-sequencing/haplotype-phasing; can seed SHAPEIT as a scaffold |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Array data, small-to-modest cohort, have a panel | Eagle2 `--vcfRef` or phase_common `--reference` | a panel models LD better than a few thousand samples |
| Array data, large cohort, no panel | Eagle2 or phase_common within-cohort | LD is modeled from the cohort; accuracy rises with N |
| WGS/WES, biobank scale, need rare variants phased | SHAPEIT5: phase_common -> ligate -> phase_rare | the scaffold design is the only route to accurate rare-variant phase |
| Pre-phasing as imputation input | Eagle2 or Beagle 5 | small switch errors largely wash out in imputation -> genotype-imputation |
| One tool for phase and impute, no compile | Beagle 5.x (gt= to phase, add ref= to impute) | pragmatic single tool |
| Trio/pedigree available | trio/pedigree phasing; use `switch` to benchmark | deterministic where informative; the truth ruler |
| Long reads on the same sample | -> long-read-sequencing/haplotype-phasing (then seed SHAPEIT as a scaffold) | read-backed phase is local and deterministic; combine, do not replace |
| Common-variant phasing only, modest data | SHAPEIT4 or Beagle | rare-variant machinery is unnecessary overhead |

## The Common-Scaffold-Then-Rare Design (SHAPEIT5)

Rare variants carry too little LD to phase in a joint model, and a joint HMM over millions of rare sites does not scale, so SHAPEIT5 splits the problem. Use the full pipeline when N > ~2,000; below that, `phase_common` alone suffices (too few rare-allele carriers for the rare step to add value).

1. **phase_common** phases the common variants (e.g. `--filter-maf 0.001`) into accurate haplotypes - the scaffold. Run per chunk for large chromosomes, with OVERLAPPING regions.
2. **ligate** stitches the per-chunk common scaffolds into one chromosome; chunks must overlap so ligate can resolve phase across the seam (a non-overlapping seam is a guaranteed switch).
3. **phase_rare** takes the FULL genotypes plus the fixed scaffold and places each rare allele onto the already-phased common haplotypes by IBD matching. Do not filter rare variants out of the phase_rare input - placing them is the whole point.

## Switch Error vs Flip vs Hamming -- the Metrics

A single rate hides the failure mode. Report more than one, and look at the distribution of switch positions.

| Metric | What it counts | Inflates on |
|--------|----------------|-------------|
| Switch error rate (SER) | fraction of consecutive het-site pairs whose phase relationship is wrong | many small local errors; the standard headline |
| Flip error | an isolated het phased wrong then immediately corrected (two switches one site apart) | noisy single sites; double-counts in raw SER |
| Hamming error | fraction of het sites on the wrong haplotype under the best global alignment | a few LARGE block swaps - high Hamming, low switch count |
| Long switch / block flip | a sustained segment on the wrong haplotype | poor long-range LD; ruinous for cis/trans yet only 2 switches |

SER and Hamming measure different sins: many tiny flips give high SER but modest Hamming; one half-chromosome block swap gives catastrophic Hamming but only two switches. Het density matters too - SER is per-het-pair, so sparse het sites mean the same SER spans more bp. Typical magnitudes (order-of-magnitude, dataset-specific): Eagle2 + HRC reference, European array ~1.36%; Eagle2 within-cohort N~5,000 ~1.5%; within-cohort N~150,000 (UK Biobank) ~0.27-0.35%; SHAPEIT5 for a variant in ~1 of 100,000 < ~5%. The pattern: common-variant phasing in a big cohort is sub-1%; rare-variant phasing is single-digit-percent at best and worsens steeply as MAC approaches 1.

## Reference-Based vs Within-Cohort

Reference-based phasing wins when the cohort is small (a few thousand samples cannot model LD as well as a 32k-100k+ haplotype panel); phase against the biggest ancestry-matched panel available (Eagle2 `--vcfRef`). Within-cohort phasing wins when the cohort is large and ancestry-matched to itself, because accuracy rises monotonically with N; by UK-Biobank scale within-cohort is more accurate than any external panel. The crossover is in the tens of thousands. Ancestry match dominates either way - a mismatched panel phases worse than a smaller matched one or within-cohort -> reference-panels.

## Per-Method Failure Modes

### Genome-wide SER trusted for a rare-variant call
**Trigger:** quoting one switch-error rate and treating all haplotypes as equally trustworthy. **Mechanism:** SER is dominated by easy common sites; rare-variant phase is far worse and MAC-dependent. **Symptom:** a confident compound-het (cis/trans) call from a small-cohort statistical phase that is actually near chance. **Fix:** stratify accuracy by MAC; confirm rare-variant cis/trans with a trio or read-backed phase.

### Wrong-build or flat genetic map
**Trigger:** a GRCh37 map on GRCh38 data, or a uniform map "for simplicity". **Mechanism:** the map sets the HMM's recombination (transition) rates; wrong coordinates or a flat rate mis-place where haplotype breaks are expected. **Symptom:** degraded phasing, more long switches, no error message. **Fix:** use the build-matched per-chromosome map shipped with the tool; the default population map is right.

### Non-overlapping ligate seam
**Trigger:** chunking a chromosome with abutting (non-overlapping) regions. **Mechanism:** ligate needs overlap to resolve the phase relationship across the seam. **Symptom:** a guaranteed switch at every chunk boundary. **Fix:** make `--region` / `--input-region` / `--scaffold-region` overlap between adjacent chunks.

### chrX male coded diploid
**Trigger:** phasing male chrX non-PAR as diploid heterozygous. **Mechanism:** males are haploid outside the PARs; a het call there is biologically impossible. **Symptom:** corrupted male chrX phase. **Fix:** pass the male sample list (SHAPEIT5 `--haploids`; Eagle handles mixed ploidy); keep PAR1/PAR2 as separate diploid regions with build-correct coordinates.

### Multiallelic records fed to a phaser
**Trigger:** phasing raw multiallelic sites. **Mechanism:** phasers expect biallelic records; a multiallelic record is undefined behavior. **Symptom:** tool errors or mis-phased sites. **Fix:** `bcftools norm -m -any` to split and left-align first -> variant-calling/variant-normalization.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `--filter-maf 0.001` defines the common/rare scaffold split | SHAPEIT5 docs | common variants build the accurate scaffold; rarer variants are phased onto it |
| Use phase_common -> ligate -> phase_rare when N > ~2,000 | SHAPEIT5 docs | below that, too few rare-allele carriers for the rare step to help |
| Report SER stratified by MAC, not genome-wide | Hofmeister 2023 *Nat Genet* 55:1243 | phasing quality is a steep function of MAC; a single number hides rare-variant failure |
| Eagle2 `--Kpbwt` default 10000 (raise at large N) | Loh 2016 *Nat Genet* 48:1443 | more conditioning haplotypes raise accuracy at biobank scale |
| phase_rare `--effective-size` ~15000 (verify) | SHAPEIT5 docs | Ne sets expected recombination; often tuned per dataset, confirm with --help |
| Genetic map must match the data build | Delaneau 2019 *Nat Commun* 10:5436 | a build-mismatched map mis-assigns recombination rates silently |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Switch at every chunk boundary | non-overlapping ligate seams | overlap adjacent chunk regions |
| Corrupted male chrX phase | male non-PAR coded diploid | pass `--haploids`; split PAR/nonPAR |
| Phaser errors on some sites | multiallelic records | `bcftools norm -m -any` first |
| Rare-variant cis/trans call does not replicate | small-cohort statistical phase of rare variants | use SHAPEIT5 at scale; confirm with trio/read-backed |
| Phasing mysteriously bad in one region | wrong-build or flat genetic map | build-match the map |
| SHAPEIT4 syntax fails under SHAPEIT5 | SHAPEIT5 split into phase_common/phase_rare/ligate | use the suite binaries, not a single `shapeit` |
| Beagle OutOfMemoryError | JVM heap too small / whole genome in one job | raise `-Xmx`; phase per chromosome |

## References

- Hofmeister RJ, Ribeiro DM, Rubinacci S, Delaneau O. 2023. Accurate rare variant phasing of whole-genome and whole-exome sequencing data in the UK Biobank. *Nat Genet* 55:1243-1249.
- Delaneau O, Zagury JF, Robinson MR, Marchini JL, Dermitzakis ET. 2019. Accurate, scalable and integrative haplotype estimation. *Nat Commun* 10:5436.
- Loh PR, Danecek P, Palamara PF, et al. 2016. Reference-based phasing using the Haplotype Reference Consortium panel. *Nat Genet* 48:1443-1448.
- Browning BL, Tian X, Zhou Y, Browning SR. 2021. Fast two-stage phasing of large-scale sequence data. *Am J Hum Genet* 108:1880-1890.
- Durbin R. 2014. Efficient haplotype matching and storage using the positional Burrows-Wheeler transform (PBWT). *Bioinformatics* 30:1266-1272.
- Patterson M, Marschall T, Pisanti N, et al. 2015. WhatsHap: weighted haplotype assembly for future-generation sequencing reads. *J Comput Biol* 22:498-509.
- Li N, Stephens M. 2003. Modeling linkage disequilibrium and identifying recombination hotspots using single-nucleotide polymorphism data. *Genetics* 165:2213-2233.

## Related Skills

- reference-panels - Select the ancestry-matched panel that reference-based phasing copies from
- genotype-imputation - Imputation consumes the phased haplotypes (pre-phasing)
- imputation-qc - Switch-error benchmarking sits alongside imputation quality QC
- long-read-sequencing/haplotype-phasing - Read-backed / molecular single-sample phasing (a different signal)
- variant-calling/variant-normalization - Split multiallelics and left-align before phasing
- causal-genomics/fine-mapping - Phased haplotypes feed haplotype-level fine-mapping
- clinical-databases/hla-typing - HLA typing is a high-stakes consumer of long-range phase
- workflows/gwas-pipeline - End-to-end QC -> phase -> impute -> associate
<!-- END FILE: phasing-imputation/haplotype-phasing/SKILL.md -->

## 子目录：phasing-imputation/imputation-qc

<!-- BEGIN FILE: phasing-imputation/imputation-qc/SKILL.md -->
---
name: bio-phasing-imputation-imputation-qc
description: Assesses and filters phasing/imputation output - the quality metrics (Beagle DR2, Minimac R2 and EmpRsq, IMPUTE/GLIMPSE INFO), MAF-stratified filtering, true accuracy by masking, the differential-imputation confound, dosage-based downstream usage, and phasing switch-error QC. Covers why every routine quality score is an ESTIMATE of r2 from the posterior spread (not validation against truth), why it is confounded with MAF so a flat INFO>=0.3 cutoff is a hidden rare-variant filter, why concordance lies for rare variants while masked dosage-r2 by MAF is the gold standard, why separate case/control imputation manufactures false GWAS hits, and that the field name tells the tool (DR2=Beagle, R2=Minimac, INFO=GLIMPSE/IMPUTE). Use when filtering imputed variants before GWAS, validating accuracy, benchmarking phasing against trios, or diagnosing inflated association. Imputation is genotype-imputation; phasing is haplotype-phasing; panel ancestry is reference-panels; the test is population-genetics/association-testing.
tool_type: mixed
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, cyvcf2 0.31+, pandas 2.2+, numpy 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show cyvcf2 pandas numpy` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The imputation quality field is named differently by each engine: `DR2` (Beagle 5.x; `AR2` is legacy 4.x), `R2` (Minimac4; `ER2`/`EmpRsq` for typed sites), `INFO` (IMPUTE5 and GLIMPSE). `bcftools +fill-tags` computes AF/MAF/HWE but CANNOT produce an imputation Rsq - the quality number comes from the imputer only. Record the engine, panel, and build, because a quality number is only comparable within the same engine and panel.

# Imputation QC -- Filtering on a Self-Estimated Quality, Validating With Masked Truth

**"Filter my imputed genotypes by quality and check the accuracy"** -> Filter on the imputer's per-variant quality field with a MAF floor, and validate true accuracy by masking - because the routine quality score is the model grading its own posterior, it is confounded with allele frequency, and a flat cutoff silently deletes the rare variants of greatest interest.
- CLI: `bcftools view -e 'INFO/DR2<0.3 || INFO/AF<0.01 || INFO/AF>0.99' imputed.vcf.gz` (DR2 for Beagle; R2 for Minimac; INFO for GLIMPSE/IMPUTE; Minimac also emits a MAF tag, Beagle only AF)

Scope: QC of already-produced phasing/imputation output - what the numbers mean, which to trust, how to filter, and how poor QC propagates into false GWAS hits. Running imputation -> genotype-imputation. Phasing -> haplotype-phasing. Panel ancestry (which the metric cannot detect) -> reference-panels. The GWAS test on the filtered dosages -> population-genetics/association-testing. VCF field-parsing mechanics -> variant-calling/vcf-statistics. Read-backed phasing switch QC -> long-read-sequencing/haplotype-phasing.

## The Single Most Important Modern Insight -- The Quality Score Is the Model Grading Its Own Posterior, Confounded With MAF, So a Flat Cutoff Is a Hidden Rare-Variant Filter

Every routine imputation quality score (IMPUTE INFO, Minimac R2/Rsq, Beagle DR2) estimates the same quantity - the squared correlation r2 between the imputed dosage and the unobserved true genotype - from the posterior spread, without ever seeing truth (Marchini & Howie 2010 *Nat Rev Genet* 11:499). It is a self-report of confidence, not a measured accuracy. Three facts organize all of QC:

1. **The metric is structurally confounded with MAF.** The estimator is the fraction of the HWE-expected dosage variance 2p(1-p) the imputed dosages recover; the denominator collapses toward zero as the allele gets rarer, so the estimate is noisier and systematically lower for rare variants. A single flat INFO/R2 >= 0.3 cutoff therefore deletes rare variants far more aggressively than common ones - a hidden MAF filter applied without anyone deciding to. Filter MAF-stratified, or report accuracy per MAF bin.
2. **The only true accuracy comes from masking.** Hide genotypes that are actually known, re-impute them, and compute the real squared correlation against the held-out truth, binned by MAF (the dosage-r2-by-MAF curve). That is the gold standard; the per-variant R2 is a convenient proxy never validated against truth for that variant. Minimac's EmpRsq (masked, measured) vs Rsq (self-estimated) is the only place the two meet, and a gap between them is a QC alarm (panel/strand/ancestry mismatch). Concordance is disqualified for rare variants: a do-nothing imputer that always calls the major homozygote scores ~98% concordance at MAF 1% (0.99^2) while carrying zero information.
3. **The differential-imputation confound manufactures false hits, and every per-group QC metric passes.** Because imputation quality is a function of the data and panel, imputing cases and controls (or batches, or ancestries) separately makes the imputation error differ between groups, and a case-control test cannot distinguish that artifactual allele-frequency difference from real association. The fix is structural (impute together / harmonize), not a filter; the absence of a QC red flag never clears it.

## The Metrics, Precisely

All three estimate r2 (imputed dosage vs true genotype) from the posterior, never from observed truth. The variance-ratio intuition: `estimated r2 = Var(imputed dosage) / [2p(1-p)]`. Under perfect information the dosages equal the true 0/1/2 genotypes and recover the full HWE variance (ratio 1); under no information every dosage collapses to the mean 2p and the variance goes to 0 (ratio 0). The fraction of HWE variance recovered IS the estimate, which is also why it is noisier and lower at low MAF. That `Var(dosage)/2p(1-p)` form is specifically the Minimac/Beagle estimator (the spread of the point dosages across samples); IMPUTE INFO targets the same r2 but computes it differently, averaging each sample's within-individual posterior variance - the mechanistic reason the three numbers are not interchangeable across engines.

| Field | Engine | Meaning |
|-------|--------|---------|
| DR2 | Beagle 5.x | estimated squared correlation between estimated and true allele dose (AR2 is legacy 4.x) |
| R2 (Rsq) | Minimac4 | estimated r2 for all sites, from the dosage variance ratio |
| EmpRsq / ER2 (EmpR) | Minimac4 | empirical r2 from leave-one-out at TYPED sites (masked, measured); a negative EmpR flags a strand/allele flip |
| INFO | IMPUTE5, GLIMPSE | the IMPUTE information measure (posterior-variance ratio), same spirit |

The provenance matters: the field name tells the tool, the numbers are NOT comparable across engines (a Beagle DR2 of 0.8 is not a Minimac R2 of 0.8), and `bcftools +fill-tags` cannot produce any of them.

## The INFO x MAF Interaction and Thresholds

At low MAF there is little dosage variance to predict and few panel copies of the rare haplotype to anchor the estimate, so R2 is intrinsically noisier and downward-biased there - a property of the construction, not a bug. The standard cutoffs and their status:

| Threshold | Source / status | Rationale |
|-----------|-----------------|-----------|
| INFO/R2/DR2 >= 0.3 | the common GWAS cutoff; convention, NOT a theorem | WTCCC/early-IMPUTE-era practice, acknowledged as somewhat arbitrary; acts as a hidden MAF filter |
| INFO/R2 >= 0.8 | stricter, high-confidence analyses | the 0.3 and 0.8 pair are the two established values |
| MAF-stratified INFO | recommended remedy | a flat cutoff differentially deletes rare variants; filter or report per MAF bin |
| GP > 0.9 (or 0.8) hardcall threshold | when forced to hardcall | below this set missing; hardcalling at all loses power vs dosage regression |
| Meta-analysis N_eff = N * INFO | METAL/GWAMA/FinnGen convention | down-weight poorly-imputed variants; not a named theorem |
| EmpRsq vs Rsq large gap | QC alarm | self-estimate not matching measured accuracy = panel/strand/ancestry mismatch |

## True Accuracy by Masking

The accepted accuracy curve is aggregate r2 (squared Pearson correlation between imputed dosage and the masked-then-revealed true genotype) binned by MAF; it decreases monotonically as MAF falls. Workflow: mask typed genotypes (array sites or a held-out set), re-impute from the panel, compute squared correlation vs the withheld truth, bin by MAF. Leave-one-out (one variant at a time) is the per-variant version and is what produces Minimac's EmpRsq for typed sites. Never use concordance as the rare-variant accuracy metric (Ramnarine 2015 *PLoS One* 10:e0137601); it is dominated by the major-homozygote class and inflates rare-variant accuracy.

### MAF-stratified quality summary

**Goal:** Reveal the hidden-MAF-filter effect by reporting imputation quality per MAF bin instead of as one global mean, so the rare-variant tail a flat cutoff would delete is visible.

**Approach:** Parse the imputed VCF for the engine's quality field and allele frequency with cyvcf2, derive MAF, bin it, and report mean quality and the fraction passing a candidate cutoff per bin.

```python
import numpy as np
import pandas as pd
from cyvcf2 import VCF

def quality_by_maf(vcf_path, qual_key='DR2', cutoff=0.3):
    rows = []
    for v in VCF(vcf_path):
        q = v.INFO.get(qual_key)
        af = v.INFO.get('AF')
        if q is None or af is None:
            continue
        af = af[0] if isinstance(af, tuple) else af
        rows.append((min(af, 1 - af), float(q)))
    df = pd.DataFrame(rows, columns=['maf', 'qual'])
    bins = [0, 0.001, 0.01, 0.05, 0.5]   # rare-to-common; the rare bins are where a flat cutoff bites
    df['maf_bin'] = pd.cut(df['maf'], bins=bins)
    summary = df.groupby('maf_bin', observed=True).agg(n=('qual', 'size'), mean_qual=('qual', 'mean'), frac_pass=('qual', lambda q: (q >= cutoff).mean()))
    return summary

quality_by_maf('imputed.vcf.gz', qual_key='DR2', cutoff=0.3)
```

## Phasing QC -- Switch Error Rate

Switch error rate (SER) = switch errors / opportunities, an opportunity being each consecutive heterozygous-site pair, scored against trio/duo/benchmark truth. A flip error is two switches one site apart (an isolated mis-assignment, not a long-range switch); Hamming distance counts overall haplotype differences and inflates on block swaps. Trio-based SER is biased upward by genotype error, which is why SHAPEIT5's `switch` reports SER and a genotyping-error rate jointly. Magnitudes are always MAC- and N-stratified (sub-0.5% common-variant SER for modern tools; single-digit-percent and rising as MAC approaches 1). Tools: `whatshap compare`, `vcftools --diff-switch-error`, SHAPEIT5 `switch`.

## Dosage-Based Downstream Usage

Hardcall thresholding discards imputation uncertainty and sets low-confidence calls missing, losing power versus regression on the expected dosage, especially at low MAF (Huang 2014 *PLoS One* 9:e110679). Carry dosages: PLINK2 (`--vcf file dosage=DS`, `dosage=HDS` for Minimac4 phased, `.pgen`), SNPTEST (`-method expected`/`score`/`em`), REGENIE (BGEN v1.2/PGEN), and BOLT-LMM (BGEN v1.2) all accept dosages. In meta-analysis, INFO enters as a per-study filter and as an effective-N weight.

## Per-Method Failure Modes

### Flat INFO cutoff as a silent rare-variant filter
**Trigger:** applying one INFO/R2 >= 0.3 across all frequencies. **Mechanism:** the metric is confounded with MAF, so the cutoff removes a far higher fraction of rare than common variants. **Symptom:** the rare-variant tail vanishes with no record that a frequency filter was applied. **Fix:** filter MAF-stratified or report accuracy per MAF bin; pair any INFO cutoff with an explicit MAF floor stated in the methods.

### Concordance reported as rare-variant accuracy
**Trigger:** quoting genotype concordance for rare variants. **Mechanism:** concordance is dominated by the major-homozygote class; a do-nothing imputer scores ~98% at MAF 1%. **Symptom:** uniformly high concordance hiding catastrophic rare-variant failure. **Fix:** use masked dosage-r2 binned by MAF; reserve concordance for sanity checks on common variants.

### Cases and controls imputed separately
**Trigger:** imputing batches/groups independently. **Mechanism:** batch-differential imputation quality creates an artifactual allele-frequency difference indistinguishable from association. **Symptom:** genome-wide-significant hits that fail to replicate; every per-group QC passes. **Fix:** impute all samples together, or harmonize panel/version and verify quality does not differ by batch -> reference-panels.

### Filtering on the wrong quality field
**Trigger:** `bcftools view -i 'INFO/R2>0.3'` on a Beagle VCF (which has DR2, not R2). **Mechanism:** the field name is engine-specific. **Symptom:** the filter silently passes everything or errors on a missing tag. **Fix:** use DR2 for Beagle, R2 for Minimac, INFO for GLIMPSE/IMPUTE; confirm with `bcftools view -h`.

### Trusting Rsq where EmpRsq diverges
**Trigger:** reporting a high Rsq while the masked EmpRsq is much lower. **Mechanism:** the self-estimate assumes the model (panel, strand, ancestry) is right; a gap means it is not. **Symptom:** confident Rsq on systematically wrong imputation; a negative EmpR is an outright strand flip. **Fix:** treat the Rsq-EmpRsq gap as an alarm; check strand/build/ancestry -> reference-panels.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| INFO/R2/DR2 >= 0.3 (common), >= 0.8 (strict) | convention (WTCCC/early-IMPUTE era) | the common GWAS cutoffs; not derived, and a hidden MAF filter |
| Always pair the quality cutoff with a MAF floor | Magi 2012 *Genet Epidemiol* 36:785 | rare + low-R2 is the classic false-positive generator |
| Accuracy = masked dosage-r2 binned by MAF | Ramnarine 2015 *PLoS One* 10:e0137601 | concordance inflates rare-variant accuracy; r2 by MAF bin is the gold standard |
| Hardcall GP > 0.9 only when forced | convention | hardcalling loses power vs dosage regression |
| Impute cases and controls together | best-practice consensus | separate imputation manufactures batch-driven false positives |
| Switch-error magnitudes are MAC/N-stratified | Hofmeister 2023 *Nat Genet* 55:1243 | no single universal SER threshold; qualify by MAC bin and validation type |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Filter on INFO/R2 passes all Beagle variants | wrong field name (Beagle uses DR2) | use DR2; confirm with `bcftools view -h` |
| Rare-variant signal disappears after QC | flat INFO cutoff as a hidden MAF filter | filter MAF-stratified; state the MAF floor |
| Uniformly high "accuracy" for rare variants | concordance metric | use masked dosage-r2 by MAF bin |
| Genome-wide-significant hits do not replicate | cases/controls imputed separately, or hardcalled | impute together; regress on dosages |
| `bcftools +fill-tags` did not add an Rsq | fill-tags computes AF/MAF/HWE, not imputation quality | the quality field comes from the imputer |
| Negative Minimac EmpR at a site | strand/allele flip | re-align strand to the panel -> reference-panels |

## References

- Marchini J, Howie B. 2010. Genotype imputation for genome-wide association studies. *Nat Rev Genet* 11:499-511.
- Howie BN, Donnelly P, Marchini J. 2009. A flexible and accurate genotype imputation method for the next generation of genome-wide association studies. *PLoS Genet* 5:e1000529.
- Das S, Forer L, Schonherr S, et al. 2016. Next-generation genotype imputation service and methods. *Nat Genet* 48:1284-1287.
- Browning BL, Zhou Y, Browning SR. 2018. A one-penny imputed genome from next-generation reference panels. *Am J Hum Genet* 103:338-348.
- Ramnarine S, Zhang J, Chen LS, et al. 2015. When does choice of accuracy measure alter imputation accuracy assessments? *PLoS One* 10:e0137601.
- Magi R, Asimit JL, Day-Williams AG, Zeggini E, Morris AP. 2012. Genome-wide association analysis of imputed rare variants: application to seven common complex diseases. *Genet Epidemiol* 36:785-796.
- Hofmeister RJ, Ribeiro DM, Rubinacci S, Delaneau O. 2023. Accurate rare variant phasing of whole-genome and whole-exome sequencing data in the UK Biobank. *Nat Genet* 55:1243-1249.
- Huang KC, Sun W, Wu Y, et al. 2014. Association studies with imputed variants using expectation-maximization likelihood-ratio tests. *PLoS One* 9:e110679.
- Willer CJ, Li Y, Abecasis GR. 2010. METAL: fast and efficient meta-analysis of genomewide association scans. *Bioinformatics* 26:2190-2191.

## Related Skills

- genotype-imputation - Produces the dosages and the quality field this skill filters
- haplotype-phasing - Switch-error benchmarking of the phasing that precedes imputation
- reference-panels - Panel ancestry mismatch, which the quality metric cannot detect
- variant-calling/vcf-statistics - Generic VCF INFO/FORMAT field parsing
- population-genetics/association-testing - Consumes the filtered dosages
- long-read-sequencing/haplotype-phasing - Read-backed phasing switch QC
- workflows/gwas-pipeline - End-to-end QC -> phase -> impute -> associate
<!-- END FILE: phasing-imputation/imputation-qc/SKILL.md -->

## 子目录：phasing-imputation/reference-panels

<!-- BEGIN FILE: phasing-imputation/reference-panels/SKILL.md -->
---
name: bio-phasing-imputation-reference-panels
description: Selects and prepares the reference panel that phasing/imputation copies haplotypes from (1000 Genomes, HRC, TOPMed, HGDP+1kGP/gnomAD, CAAPA), matching panel ancestry to the target, reconciling genome build and chromosome naming, and running the strand/allele harmonization gate. Covers why ancestry-match beats panel size (imputation can only copy haplotypes the panel contains), why palindromic A/T and C/G SNPs flip strand without erroring, why liftover is a strand-flip generator in between-build inverted regions, that HRC is SNP-only and TOPMed is never downloadable (governance can override accuracy), and panel formats (msav, bref3, imp5). Use when choosing a panel for a target ancestry, preparing or converting a panel, aligning study data, or deciding between downloadable and server-only panels. Phasing is haplotype-phasing; imputation is genotype-imputation; PCA for ancestry is population-genetics/population-structure; HLA panels are clinical-databases/hla-typing.
tool_type: cli
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, PLINK 1.9+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

A reference panel is DATA, not a tool: it has a dated release and a fixed genome build (GRCh37 or GRCh38). Record the exact panel name, version, and build with every result; "1000 Genomes" without a version is unreproducible because Phase 3 (GRCh37, low-coverage) and the high-coverage NYGC 3202 release (GRCh38, 30x) are different call sets. HRC and TOPMed are server-only (not downloadable); panel-build tools (Minimac4 `--compress-reference`, `bref3.jar`, `imp5Converter`) and the Will Rayner harmonization check are separate downloads.

# Reference Panels -- Choosing and Preparing the Prior Imputation Copies From

**"Which reference panel should I use, and how do I prepare it?"** -> Match the panel's ancestry to the target population, reconcile build and strand, then convert to the engine's format - because imputation can only copy haplotypes the panel contains, so the panel IS the prior, and a mismatched ancestry or a flipped strand corrupts the result without any error.
- CLI: `bcftools norm -m -any -f ref.fa` then the strand/allele harmonization check against the panel sites, then `minimac4 --compress-reference` / `bref3.jar` / `imp5Converter` to build the engine format

Scope: panel selection (ancestry-match, build, access), strand/allele harmonization, build/liftover, and format conversion. The phasing engine that consumes the panel -> haplotype-phasing. Imputation -> genotype-imputation. PCA to establish the target ancestry -> population-genetics/population-structure. Classical HLA-allele imputation needs a dedicated HLA panel -> clinical-databases/hla-typing. VCF normalization mechanics -> variant-calling/variant-normalization.

## The Single Most Important Modern Insight -- Ancestry Match Beats Panel Size, Because Imputation Copies Haplotypes and a Mismatched Panel Has None Worth Copying

The reflex "TOPMed has 97k samples, HRC has 32k, so use TOPMed" is right for a European cohort and wrong for an ancestry-mismatched one, and the reason is mechanical, not statistical: imputation copies haplotype segments from panel samples that resemble the target, so if no panel sample carries the target population's haplotypes there is nothing to copy, and adding ten thousand more European haplotypes does nothing for an East African sample (Marchini & Howie 2010 *Nat Rev Genet* 11:499). The binding resource is not panel size but how many panel samples share the target's ancestry. Three facts follow:

1. **Ancestry composition often dominates size.** HRC (32k, European-heavy) imputes African-ancestry rare variants poorly while TOPMed lifts them dramatically - not because TOPMed is 3x bigger but because it contains African-American and Hispanic/Latino haplotypes. Admixed samples need a panel with both ancestral components and admixed individuals, because admixed haplotypes are mosaics a single-ancestry panel cannot reconstruct at the switch points. The honest answer is "large AND matched"; where both are not available, which one wins depends on whether the target is common or rare variants (size matters more for rare).
2. **The self-graded INFO/R2 cannot see ancestry mismatch.** When the panel lacks the target's haplotypes the model still finds some template and reports a confident-looking quality about a copy that is systematically wrong (full metric theory -> imputation-qc). High R2 in an under-represented ancestry is not reassurance; validate against masked truth stratified by frequency.
3. **A panel encodes whose haplotypes are trusted to fill the gaps.** HRC is European-heavy because its component cohorts were; TOPMed is diverse because it was designed to be. No panel represents everyone, and the imputation inherits exactly the panel population's representation, including its gaps. This is the central equity problem of imputation, and low-coverage WGS (unbiased ascertainment -> genotype-imputation) is the main route around it.

## The Major Panels

Numbers are routinely misquoted; these are the verified figures. State the exact version and build in any method.

| Panel | Samples | Build | Indels | Diversity | Access |
|-------|---------|-------|--------|-----------|--------|
| 1000G Phase 3 (Auton 2015) | 2,504 | GRCh37 (GRCh38 lift) | yes | 26 pops, broad but shallow | public download |
| 1000G high-cov NYGC (Byrska-Bishop 2022) | 3,202 (incl. 602 trios) | GRCh38 | yes | same 26 pops, 30x | public download |
| HRC r1.1 (McCarthy 2016) | 32,470 (64,940 haps) | GRCh37 only | NO - SNP-only, MAF floor ~5e-4 | European-heavy | server-only (Michigan) |
| TOPMed r2 (Taliun 2021) | 97,256 (~308M sites) | GRCh38 only | yes | very diverse (large AA, Hispanic) | server-only, never downloadable |
| HGDP+1kGP / gnomAD (Koenig 2024) | 4,094 (76-80 pops) | GRCh38 | yes | maximally diverse per-sample | public download |
| CAAPA (Mathias 2016) | 883 African-ancestry | GRCh37 | (SNP) | African / African-American | server-supported |

The "1000G" trap: Phase 3 (Auton 2015, GRCh37, low-coverage) and the high-coverage NYGC 3202 release (Byrska-Bishop 2022, GRCh38, 30x, with 602 trios) are different call sets; the NYGC release is strictly better for rare variants. State which.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Study is GRCh37 | HRC r1.1, 1000G Phase 3, or CAAPA (all GRCh37) | match the build; avoid liftover |
| Study is GRCh38 | TOPMed, 1000G NYGC, or HGDP+1kGP (all GRCh38) | match the build; avoid liftover |
| Build mismatch unavoidable | lift over ONCE, strand-aware, then re-run the harmonization check | liftover flips strand in inverted regions (see failure modes) |
| European cohort, common-variant GWAS | HRC (server) or 1000G | large and European-rich |
| African / admixed / Hispanic / multi-ancestry | TOPMed (server) | diversity wins; contains the matching haplotypes |
| Need a downloadable, diverse, local panel | HGDP+1kGP (gnomAD) | global, jointly-called, and not server-gated |
| Data cannot leave the institution / country | downloadable panels only (1000G, HGDP+1kGP) | governance overrides accuracy (see failure modes) |
| Need indels imputed | 1000G, TOPMed, or HGDP+1kGP | HRC is SNP-only |
| Classical HLA alleles | -> clinical-databases/hla-typing (dedicated HLA panel) | standard SNP panels cannot impute HLA alleles |
| Establish the target ancestry first | -> population-genetics/population-structure | PCA, not a panel operation |

The governing principle: ancestry match beats panel size, and governance (can the data be uploaded to a US server?) often narrows the field before accuracy does.

## The Strand / Allele Harmonization Gate

This is the step that silently corrupts results when skipped. The job: align every study variant's alleles to the panel REF/ALT, fix strand, and drop the variants that cannot be safely resolved. Normalize first (`bcftools norm -m -any -f ref.fa`), because the same indel represented two ways will not match.

The field-standard gate is Will Rayner's check (`HRC-1000G-check-bim.pl` and its bgen/VCF variants): it compares a QC'd PLINK `.bim` plus an allele-frequency file against the panel's sites list and EMITS a `Run-plink.sh` that updates positions, ref/alt, and strand, removes unresolvable SNPs, and splits by chromosome. The check diagnoses; the script fixes - both are required, and a surprising number of pipelines run the check and never execute the script.

The allele-frequency concordance plot (study AF vs panel AF) is the visual gate, not decoration: a tight diagonal is good; points on the `y = 1 - x` anti-diagonal are strand flips; a general smear is sample mislabeling or the wrong panel ancestry. Compare against the ancestry-MATCHED sub-panel's frequencies - an African cohort vs a European panel's AF smears even with perfect strand. Read this plot before uploading, every time.

## Panel Formats and the Genetic-Map Pairing

| Engine | Native format | Build command |
|--------|---------------|---------------|
| Minimac4 | `.msav` (current) or legacy `.m3vcf` | `minimac4 --compress-reference ref.vcf.gz > ref.msav` (legacy: `Minimac3 --processReference`) |
| Beagle 5.x | `.bref3` or plain VCF | `java -jar bref3.jar ref.vcf.gz > ref.bref3` (needs fully phased, non-missing, `|`-separated, per chromosome) |
| IMPUTE5 | `.imp5` or VCF/BCF | `imp5Converter --h ref.vcf.gz --r chr20 --o ref.chr20.imp5` |

A panel is half the input; phasing/imputation also needs a genetic (recombination) map matched to the panel build. A panel VCF comes site-only (the legend, used for the harmonization check) or full (the haplotypes, used to impute) - obtain both. The map is build-specific: an hg19 map with a GRCh38 panel silently mis-places recombination rates.

## chrX and MHC

- **chrX**: split into PAR1 / nonPAR / PAR2 using build-correct coordinates. PAR and female nonPAR are diploid; male nonPAR is HAPLOID and must be coded haploid (a het call there is an error). Mixed ploidy in one file crashes most tools; the Michigan/TOPMed servers split, impute, and re-merge automatically.
- **MHC (chr6 ~28-34 Mb)**: extreme LD and polymorphism. Standard panels impute SNPs there but unreliably and cannot impute classical HLA alleles at all - that needs a dedicated HLA panel and tool -> clinical-databases/hla-typing.

## Per-Method Failure Modes

### Palindromic (A/T, C/G) SNP strand flip
**Trigger:** keeping strand-ambiguous SNPs without a frequency-based strand check. **Mechanism:** A/T and C/G alleles are their own reverse complements, so opposite-strand study and panel still "match" on alleles; the variant passes every join and imputes cleanly while allele-swapped. **Symptom:** flipped effect direction at that locus and everything imputed in LD with it; no error. **Fix:** resolve strand by allele frequency; drop palindromic SNPs with MAF > 0.4 (cannot be disambiguated near 0.5); treat "I kept all palindromic SNPs" as proof strand was never checked.

### Liftover across builds
**Trigger:** running `liftOver` to reach a panel in the other build and imputing without re-checking. **Mechanism:** ~2-5 Mb of the genome is inverted between GRCh37 and GRCh38 (BBIS regions); lifting a variant there changes its strand, and the allele-based check cannot see it on a palindrome (Sheng & Chiang 2023 *HGG Adv* 4:100159). **Symptom:** silent allele-swaps in inverted regions; the TOPMed server's own internal conversion had this bug. **Fix:** prefer a panel native to the study build; if forced, lift once with a strand-aware method, then re-run the harmonization check against the new build.

### Chromosome-naming mismatch
**Trigger:** `1` vs `chr1` between study and panel. **Mechanism:** GRCh38/TOPMed use `chr` prefixes, GRCh37 panels do not, so the join matches nothing. **Symptom:** "0 variants matched" and a wasted day; does not corrupt, just fails. **Fix:** `bcftools annotate --rename-chrs` before any check.

### Expecting a SNP-only or rarity-floored panel to carry a variant
**Trigger:** imputing an indel against HRC, or a variant rarer than the panel floor. **Mechanism:** HRC is SNP-only; its MAC>=5 cutoff means nothing below MAF ~5e-4 is in the panel; un-present variants cannot be imputed at any quality. **Symptom:** the variant is absent or near-zero R2, misread as "imputed poorly." **Fix:** use a panel that contains the variant class (1000G/TOPMed/gnomAD for indels; a WGS panel for rarer variants).

### Server-only panel blocked by governance
**Trigger:** planning to use TOPMed/HRC for data that cannot be uploaded. **Mechanism:** TOPMed is never downloadable and both are server-only; consent/data-residency/IRB rules may forbid uploading participant genotypes to a US server. **Symptom:** the best panel is legally unusable. **Fix:** use a downloadable panel (1000G, HGDP+1kGP) and impute locally.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Drop palindromic (A/T, C/G) SNPs with MAF > 0.4 | Rayner check default | strand unresolvable from alleles and frequency too near 0.5 to disambiguate |
| Allele-frequency concordance flag > 0.2 (stringent 0.1) | Rayner check default | a large study-vs-panel AF gap signals a strand, build, or ancestry problem |
| HRC MAF floor ~5e-4 (MAC>=5 / 32,470) | McCarthy 2016 *Nat Genet* 48:1279 | nothing rarer is in the panel and cannot be imputed |
| Male nonPAR chrX coded haploid | biological ploidy | a het call in male nonPAR is an error and mis-models every male |
| Genetic map must match the panel build | Li & Stephens 2003 *Genetics* 165:2213 | an hg19 map on a GRCh38 panel mis-places recombination silently |
| Match AF comparison to the ancestry-matched sub-panel | Marchini & Howie 2010 *Nat Rev Genet* 11:499 | true frequencies differ by ancestry; a mismatch smears the plot even with perfect strand |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "0 variants matched" the panel | chr naming (`1` vs `chr1`) | `bcftools annotate --rename-chrs` |
| Flipped effect direction at some loci | unresolved palindromic strand | run the harmonization check; drop A/T,C/G MAF>0.4; execute `Run-plink.sh` |
| Indels missing after imputation | HRC is SNP-only | use 1000G/TOPMed/gnomAD |
| AF concordance plot smears off-diagonal | wrong panel ancestry or sample mislabel | compare to the matched sub-panel; check sample labels |
| Cannot download HRC/TOPMed (403) | server-only / access-controlled | use the imputation server, or a downloadable panel |
| Engine errors building bref3 | unphased or missing genotypes in the panel VCF | bref3 needs fully phased, non-missing, `|`-separated input |
| Imputation degraded in one region after liftover | BBIS inverted region strand flip | use a native-build panel; re-check after any liftover |
| Tempted to impute ancestry subgroups of one cohort separately | re-creates the differential-imputation confound (batch-differential quality) | impute all samples together against one large diverse panel (TOPMed or HGDP+1kGP), not per-stratum -> imputation-qc |

## References

- Auton A, Brooks LD, Durbin RM, et al. (1000 Genomes Project Consortium). 2015. A global reference for human genetic variation. *Nature* 526:68-74.
- Byrska-Bishop M, Evani US, Zhao X, et al. 2022. High-coverage whole-genome sequencing of the expanded 1000 Genomes Project cohort including 602 trios. *Cell* 185:3426-3440.
- McCarthy S, Das S, Kretzschmar W, et al. 2016. A reference panel of 64,976 haplotypes for genotype imputation. *Nat Genet* 48:1279-1283.
- Taliun D, Harris DN, Kessler MD, et al. 2021. Sequencing of 53,831 diverse genomes from the NHLBI TOPMed Program. *Nature* 590:290-299.
- Koenig Z, Yohannes MT, Nkambule LL, et al. 2024. A harmonized public resource of deeply sequenced diverse human genomes. *Genome Res* 34:796-809.
- Mathias RA, Taub MA, Gignoux CR, et al. 2016. A continuum of admixture in the Western Hemisphere revealed by the African Diaspora genome. *Nat Commun* 7:12522.
- Marchini J, Howie B. 2010. Genotype imputation for genome-wide association studies. *Nat Rev Genet* 11:499-511.
- Das S, Forer L, Schonherr S, et al. 2016. Next-generation genotype imputation service and methods. *Nat Genet* 48:1284-1287.
- Sheng X, Xia L, Cahoon JL, et al. 2023. Inverted genomic regions between reference genome builds in humans impact imputation accuracy and decrease the power of association testing. *HGG Adv* 4:100159.
- Luo Y, Kanai M, Choi W, et al. 2021. A high-resolution HLA reference panel capturing global population diversity enables multi-ancestry fine-mapping in HIV host response. *Nat Genet* 53:1504-1516.

## Related Skills

- haplotype-phasing - The phasing engine that consumes the panel; the genetic-map pairing
- genotype-imputation - Impute untyped variants once the panel is prepared
- imputation-qc - INFO/R2 quality, which cannot detect ancestry mismatch
- variant-calling/variant-normalization - Split multiallelics and left-align before harmonization
- population-genetics/population-structure - PCA to establish target ancestry for panel choice
- clinical-databases/hla-typing - Classical HLA-allele imputation with a dedicated panel
- workflows/gwas-pipeline - End-to-end QC -> phase -> impute -> associate
<!-- END FILE: phasing-imputation/reference-panels/SKILL.md -->

<!-- END CATEGORY: phasing-imputation -->

