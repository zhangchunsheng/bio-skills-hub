---
slug: bio-genome-assembly-integrated
version: 1.0.1
displayName: "基因组组装 / Genome assembly"
name: bio-genome-assembly-integrated
summary: "中文：基因组组装综合技能，整合 9 个相关专题，覆盖基因组组装：k-mer分析、SPAdes/Flye/hifiasm/metaFlye组装、polishing、Hi-C scaffold、QC。 English: Integrated Genome assembly skill covering 9 related topics, including Genome assembly: k-mer profiling, SPAdes/Flye/hifiasm/metaFlye assembly, polishing, Hi-C scaffolding, three-axis QC."
description: "中文：这是一个面向基因组组装的综合生物信息学 Skill，整合当前分类下 9 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：基因组组装：k-mer分析、SPAdes/Flye/hifiasm/metaFlye组装、polishing、Hi-C scaffold、QC。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：CheckM2, Flye, GenomeScope2。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Genome assembly, combining 9 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Genome assembly: k-mer profiling, SPAdes/Flye/hifiasm/metaFlye assembly, polishing, Hi-C scaffolding, three-axis QC. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: CheckM2, Flye, GenomeScope2. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# genome-assembly 分类 Skill 整合版

> 本文件整合同一主分类目录下 9 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: genome-assembly -->

## 子目录：genome-assembly/assembly-polishing

<!-- BEGIN FILE: genome-assembly/assembly-polishing/SKILL.md -->
---
name: bio-genome-assembly-assembly-polishing
description: Decides whether and how to polish a draft genome assembly to raise consensus accuracy (QV) with read-type-matched tools - Racon and medaka (ONT consensus), dorado polish, Polypolish and pypolca (Illumina, repeat-aware), Pilon (legacy short-read), NextPolish/NextPolish2, Hapo-G (haplotype-aware), ntEdit, and DeepPolisher/PEPPER-Margin-DeepVariant for human. Covers the do-not-polish-HiFi rule, the medaka basecaller-model footgun, held-out Merqury QV as the only honest stop signal, and the haplotype-collapse trap. Use when correcting homopolymer indels or residual SNPs in a long-read assembly, deciding if a HiFi assembly needs polishing, or choosing an ONT vs hybrid vs short-read polishing chain.
tool_type: cli
primary_tool: Pilon
---

## Version Compatibility

Reference examples tested with: Racon 1.5+, medaka 2.0+, minimap2 2.26+, bwa 0.7.17+, samtools 1.19+, Polypolish 0.6+, pypolca 0.3+, Pilon 1.24+, Merqury 1.3+, meryl 1.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

The **medaka consensus model** matters more than the medaka binary version: the model must match the basecaller + pore chemistry + caller mode + version (`-m r1041_e82_400bps_sup_v5.0.0`); a mismatched model silently degrades the consensus. List options with `medaka tools list_models`. medaka's status is a moving target - ONT now steers toward `dorado polish` and has deprecated medaka's diploid-variant workflow in favour of Clair3; verify current guidance and the `medaka_consensus` wrapper vs newer subcommands. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Assembly Polishing

**"Polish my genome assembly"** -> Decide whether base-level consensus correction is warranted, then apply a read-type-matched polisher and measure the gain with held-out k-mers - or, for an already-accurate assembly, decline.
- CLI: `racon reads.fq aln.sam draft.fa` then `medaka_consensus -i reads.fq -d draft.fa -o out -m <model>` (ONT); `polypolish polish draft.fa f1.sam f2.sam` + `pypolca run` (hybrid/short); `merqury.sh reads.meryl asm.fa out` (measure QV before/after)

## The Single Most Important Modern Insight -- Polishing Is Being Engineered Out, and Reflexive Polishing Does Net Harm

Polishing exists to fix the characteristic error of *noisy* long reads: indels in homopolymers and low-complexity tracts (the pore/RT stutters on `AAAAAA`) plus residual substitutions. As read accuracy rose (PacBio HiFi ~Q40-50 reads, ONT R10.4.1 + Dorado `sup`/duplex), the assembly consensus is already near-perfect, and a mapping-based polisher's read-pileup step injects more errors than it removes. Two load-bearing rules dominate:

1. **Do NOT polish HiFi assemblies by default.** A hifiasm/HiCanu HiFi assembly starts at ~Q40+; mapping-based polishers (Racon, Pilon, GCpp) routinely *lower* QV and introduce haplotype-switch errors. Only polish HiFi with a tool explicitly built not to overcorrect (NextPolish2, DeepPolisher) and only if Merqury QV says there is a real deficit. For HiFi the burden of proof is on polishing, not against it.
2. **Measure the gain with reference-free, HELD-OUT Merqury k-mers - never the reads polished with, never BUSCO.** A polisher's literal objective is to maximize agreement with its input reads, so scoring it with those same reads is circular and always looks like an improvement. The honest stop signal is a Merqury QV *plateau*, not a fixed iteration count - and polishing can drive QV *down* silently. Polish with one platform, evaluate with another (polish with ONT, measure with Illumina k-mers).

Polishing is transitional infrastructure: indispensable in the CLR/early-ONT error era, shrinking toward irrelevance as raw accuracy climbs upstream (better basecalling, hifiasm's own consensus). The skill's job is to say *when not to polish* as firmly as how to.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| Racon | Vaser 2017 *Genome Res* | POA read-to-assembly consensus; fast workhorse | first-pass ONT/CLR self-polish (1-4 rounds); needs minimap2 SAM/PAF |
| medaka | nanoporetech/medaka (software) | ONT neural-network consensus | one pass *after* Racon; model MUST match basecaller |
| dorado polish | ONT/dorado (software) | modern ONT consensus, owns basecalling context | the emerging medaka replacement; verify current status |
| Polypolish | Wick & Holt 2022 *PLoS Comput Biol* | Illumina polish using ALL alignments (`bwa mem -a`) | repeat-rich long-read assemblies; best-in-class short-read polish |
| pypolca | Bouras 2024 *Microb Genom* (POLCA: Zimin 2020) | fast Illumina SNP/indel correction | pair with Polypolish (modern bacterial practice) |
| Pilon | Walker 2014 *PLoS ONE* | all-in-one SNP/indel/local short-read fix | legacy; small genomes only; mismaps in repeats, ~1 GB heap/Mb |
| NextPolish / NextPolish2 | Hu 2020 *Bioinformatics* / Hu 2024 *GPB* | iterative LR+SR polish / HiFi repeat+phase-aware | NextPolish2 is the HiFi-safe successor |
| Hapo-G | Aury & Istace 2021 *NARGAB* | haplotype-aware short-read polish | heterozygous diploids; preserves both alleles |
| ntEdit | Warren 2019 *Bioinformatics* | Bloom-filter k-mer polish, no mapping | very large (>3 Gb) genomes; scales where alignment can't |
| DeepPolisher | Mastoras 2025 *Genome Res* | transformer correction (PHARAOH ONT phasing) | HiFi/T2T human; halves errors without overcorrection |
| PEPPER-Margin-DeepVariant | Shafin 2021 *Nat Methods* | haplotype-aware ONT consensus via variant calling | human ONT-only polishing |
| DeepConsensus | Baid 2023 *Nat Biotechnol* | improves CCS *reads* UPSTREAM of assembly | NOT a polisher - operates before assembly (common category error) |

## Decision Tree by Scenario

| Scenario (data type) | Recommended | Why |
|----------------------|-------------|-----|
| PacBio HiFi only | **Do NOT polish by default** -> check Merqury QV first | already ~Q40-50; Racon/Pilon lower QV + collapse haplotypes |
| HiFi with a real Merqury QV deficit | NextPolish2 or DeepPolisher | repeat/phase-aware; won't overcorrect het sites |
| ONT-only, noisy (R9 / R10 hac) | Racon (1-4 rounds) -> medaka (1 pass), or dorado polish | canonical ONT chain; neural consensus on the ONT error model |
| ONT-only, human/diploid | PEPPER-Margin-DeepVariant or DeepPolisher | haplotype-aware; preserves both alleles |
| Long-read draft + Illumina (hybrid) | long-read pass, then Polypolish + pypolca | SR fixes residual homopolymer indels Racon/medaka missed |
| Short-read-only assembly (SPAdes) | usually no polishing needed | Illumina is already ~Q40+; structural sins survive anyway |
| HiFi + Illumina | use Illumina k-mers for *evaluation*, not correction | Merqury hybrid QV, not a polishing pass |
| Heterozygous / repeat-rich genome | Polypolish (`-a`), Hapo-G, NextPolish2 - or none | non-haplotype-aware polishers erase het / homogenize paralogs |
| Reads not yet QC'd / wrong basecaller | -> read-qc/quality-reports, -> long-read-sequencing/long-read-alignment | garbage-in or model-mismatch makes polishing worse than skipping |
| Complaint is "fragmented" not "low QV" | -> not polishing (scaffolding/gap-filling) | polishing fixes bases, not contiguity |
| Map reads before polishing | short -> read-alignment/bwa-alignment; long -> long-read-sequencing/long-read-alignment | polishers consume a BAM/SAM/PAF, not raw reads |

## The Canonical ONT Chain: Racon -> medaka

**Racon** does the bulk cheap consensus from the long reads themselves; it is a standalone consensus module and does NOT map - the SAM/PAF is supplied. Re-map every round (1-4 rounds; gains decay fast).

```bash
minimap2 -t 16 -ax map-ont draft.fasta reads.fq.gz > aln.sam   # map-pb for PacBio CLR
racon -t 16 reads.fq.gz aln.sam draft.fasta > racon1.fasta
# re-map reads to racon1.fasta and repeat for round 2... measure QV each round, stop at plateau
```

**medaka** applies an ONT-trained neural model for the final consensus - exactly ONE pass after the Racon rounds (it is not an iterate-many-times tool; running medaka twice is a tell). For medaka mechanics and model tables see long-read-sequencing/medaka-polishing; this skill owns the *strategy*.

```bash
medaka_consensus -i reads.fq.gz -d racon_final.fasta -o medaka_out -t 16 \
  -m r1041_e82_400bps_sup_v5.0.0          # model MUST match basecaller+chemistry+caller+version
```

Recent basecallers embed the model in the FASTQ so medaka auto-selects; if the data was basecalled with an old/unknown caller, pick manually from `medaka tools list_models`, and treat a stale/deprecated model name as a reason to rebasecall rather than proceed.

## Hybrid / Short-Read Polishing: Polypolish + pypolca

**Polypolish** aligns short reads to *all* locations (`bwa mem -a`) so it can disambiguate which repeat copy a read belongs to instead of forcing one placement - this is *how* it beats Pilon in repeats and why it almost never introduces errors.

```bash
bwa index draft.fasta
bwa mem -t 16 -a draft.fasta reads_1.fq.gz > aln_1.sam     # -a = ALL alignments (the whole point)
bwa mem -t 16 -a draft.fasta reads_2.fq.gz > aln_2.sam
polypolish filter --in1 aln_1.sam --in2 aln_2.sam --out1 filt_1.sam --out2 filt_2.sam
polypolish polish draft.fasta filt_1.sam filt_2.sam > polypolish.fasta   # --careful (v0.6+) for low depth
pypolca run -a polypolish.fasta -1 reads_1.fq.gz -2 reads_2.fq.gz -o pypolca_out -t 16 --careful
```

Bouras 2024 depth-tiered bacterial recommendation: depth <5x -> Polypolish `--careful` alone; 5-25x -> Polypolish `--careful` + pypolca `--careful`; >25x -> Polypolish (default) + pypolca `--careful`. Modern bacterial best practice is Polypolish + pypolca, NOT Pilon.

## Pilon (Legacy Short-Read)

```bash
bwa mem -t 16 draft.fasta r1.fq r2.fq | samtools sort -o frags.bam
samtools index frags.bam
java -Xmx16G -jar pilon.jar --genome draft.fasta --frags frags.bam --output pilon --fix all --changes
```

`--fix` modes: `snps`, `indels`, `bases` (=snps+indels), `gaps`, `local`, `all` (**default**), `none`. Pilon needs a sorted+indexed BAM (route mapping to read-alignment/bwa-alignment). It is legacy: it uses best-placement alignments so it *mismaps in repeats* (miscorrects toward paralogs), and its ~1 GB heap per Mb of genome OOMs on large eukaryotes - both reasons Polypolish/pypolca displaced it.

## Measuring the Gain: Held-Out Merqury QV

**Goal:** Decide whether a polish actually helped, without fooling yourself.

**Approach:** Build a meryl k-mer DB from an *independent / different-platform* read set (k from Merqury's `best_k.sh`, not hardcoded), then run Merqury on the pre- and post-polish assemblies and compare QV. A polish that does not raise QV did not help; one that lowers it must be reverted.

```bash
K=$(sh $MERQURY/best_k.sh 5000000 | tail -n1 | awk '{print int($1+0.5)}')   # K from genome size; round float->int
meryl count k=$K output reads.meryl illumina_reads.fq.gz               # eval reads != polishing reads
merqury.sh reads.meryl draft.fasta    qv_before                        # QV of the input
merqury.sh reads.meryl polished.fasta qv_after                         # QV after polishing
```

Use a held-out set or a *different platform* than was polished with (polish with ONT, evaluate with Illumina k-mers); the CHM13 effort triangulated with both HiFi and Illumina k-mers (Mc Cartney 2022). Do NOT use BUSCO as the polishing metric - it measures gene-space completeness and barely moves with the homopolymer-indel QV that polishing changes, so a flat BUSCO masks a silent QV drop. A per-gene internal-stop / frameshift count is a useful secondary readout. See assembly-qc for the full QV/spectra-cn workflow.

## Per-Method Failure Modes

### medaka run with the wrong basecaller model
**Trigger:** specifying or defaulting to a model that does not match the actual basecaller+chemistry+version. **Mechanism:** the network applies corrections calibrated for errors that aren't there and misses the ones that are. **Symptom:** medaka completes with no warning, but Merqury QV is *lower* than the input. **Fix:** let medaka auto-detect from the FASTQ; if manual, derive the model from the real caller and confirm in `medaka tools list_models`; treat a stale model as a reason to rebasecall.

### Polishing a HiFi assembly with a mapping-based polisher
**Trigger:** running Racon/Pilon/GCpp on a hifiasm assembly. **Mechanism:** at het sites the pileup mixes both true alleles; the polisher overwrites toward the majority and homogenizes near-identical paralogs. **Symptom:** lost heterozygosity, haplotype-switch errors, QV unchanged or down. **Fix:** don't; if Merqury shows a real deficit, use NextPolish2/DeepPolisher only.

### Validating with the polishing reads (circularity)
**Trigger:** measuring QV with the same read set used to polish. **Mechanism:** the polisher already maximized agreement with those reads. **Symptom:** every polish "improves QV," monotonically. **Fix:** evaluate with held-out / different-platform k-mers.

### Over-polishing past the plateau
**Trigger:** "a few more rounds to be safe." **Mechanism:** once resolvable errors are fixed, extra rounds flip correct bases at het/repeat sites. **Symptom:** "N changes made" keeps reporting while QV oscillates or falls. **Fix:** track Merqury QV per round; stop at plateau. Treat a large change count on an accurate assembly as a risk signal, not success.

### Pilon mismapping in repeats
**Trigger:** Pilon on a repeat-rich genome. **Mechanism:** best-placement alignment forces a read onto one repeat copy; Pilon corrects that copy toward the wrong one. **Symptom:** repeat copies homogenized, paralog differences erased. **Fix:** Polypolish (`bwa mem -a`, uses all alignments).

### Treating DeepConsensus as a polisher
**Trigger:** running DeepConsensus on the assembly. **Mechanism:** DeepConsensus improves CCS *reads* upstream, before assembly. **Symptom:** tool expects subreads/CCS, not a FASTA. **Fix:** run it in the read-prep stage; for assembly polishing use a post-assembly tool.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| HiFi assembly ~Q40-50 already | HiFi read accuracy | starting point too high for mapping-based polishing to help |
| Racon 1-4 rounds, stop at QV plateau | Vaser 2017 + practice | gains decay after ~1-2; extra rounds flip correct bases |
| medaka exactly 1 pass after Racon | medaka design | trained-model pass, not an iterative tool |
| Polypolish `--careful` <5x; +pypolca 5-25x; default >25x | Bouras 2024 *Microb Genom* | depth-tiered to avoid false-positive repeat edits |
| QV40 (~1 err/10 kb) "reference-grade"; Q50 (~1/100 kb) modern aspiration; CHM13 ~Q73 | field convention; Mc Cartney 2022 | QV = -10*log10(error rate); report measured QV + method |
| Merqury k from `best_k.sh` (k=21 human-scale) | Rhie 2020 *Genome Biol* | wrong k silently degrades QV/completeness |
| Pilon ~1 GB heap per Mb of genome | Walker 2014 | OOM risk on large eukaryotes; set `-Xmx` |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| QV drops after polishing a HiFi assembly | over-polishing an already-accurate assembly | stop; HiFi rarely needs short-read polish |
| medaka output worse than input, no warning | wrong/stale basecaller model | auto-detect or match model exactly; else rebasecall |
| Every polishing round "improves" QV | measured with the polishing reads (circular) | evaluate with held-out / different-platform k-mers |
| Lost heterozygosity / switch errors | non-haplotype-aware polisher on a diploid | Hapo-G / NextPolish2 / Polypolish `-a`, or skip |
| Repeat copies homogenized | Pilon best-placement mismapping | Polypolish with `bwa mem -a` |
| Pilon OOM / crash on large genome | ~1 GB/Mb heap blowup | raise `-Xmx`; prefer Polypolish/ntEdit |
| Polishing didn't fix fragmentation | wrong operation | fragmentation is scaffolding/gap-filling, not polishing |

## References

- Vaser R, Sović I, Nagarajan N, Šikić M. 2017. Fast and accurate de novo genome assembly from long uncorrected reads (Racon). *Genome Res* 27:737-746.
- Walker BJ, et al. 2014. Pilon: an integrated tool for comprehensive microbial variant detection and genome assembly improvement. *PLoS ONE* 9:e112963.
- Wick RR, Holt KE. 2022. Polypolish: short-read polishing of long-read bacterial genome assemblies. *PLoS Comput Biol* 18:e1009802.
- Zimin AV, Salzberg SL. 2020. The genome polishing tool POLCA makes fast and accurate corrections in genome assemblies. *PLoS Comput Biol* 16:e1007981.
- Bouras G, et al. 2024. How low can you go? Short-read polishing of Oxford Nanopore bacterial genome assemblies. *Microb Genom* 10:001254.
- Hu J, et al. 2020. NextPolish: a fast and efficient genome polishing tool for long-read assembly. *Bioinformatics* 36:2253-2255.
- Hu J, et al. 2024. NextPolish2: a repeat-aware polishing tool for genome assemblies with HiFi long reads. *Genomics Proteomics Bioinformatics* 22:qzad009.
- Aury JM, Istace B. 2021. Hapo-G, haplotype-aware polishing of genome assemblies with accurate reads. *NAR Genom Bioinform* 3:lqab034.
- Warren RL, et al. 2019. ntEdit: scalable genome sequence polishing. *Bioinformatics* 35:4430-4432.
- Baid G, et al. 2023. DeepConsensus improves the accuracy of sequences with a gap-aware sequence transformer. *Nat Biotechnol* 41:232-238.
- Shafin K, et al. 2021. Haplotype-aware variant calling with PEPPER-Margin-DeepVariant enables high accuracy in nanopore long-reads. *Nat Methods* 18:1322-1332.
- Mastoras M, et al. 2025. Highly accurate assembly polishing with DeepPolisher. *Genome Res* 35:1595-1608.
- Rhie A, et al. 2020. Merqury: reference-free quality, completeness, and phasing assessment for genome assemblies. *Genome Biol* 21:245.
- Mc Cartney AM, et al. 2022. Chasing perfection: validation and polishing strategies for telomere-to-telomere genome assemblies. *Nat Methods* 19:687-695.

## Related Skills

- long-read-assembly - Produces the contiguous-but-error-prone contigs this skill polishes
- short-read-assembly - Source of Illumina reads for hybrid/short-read polishing
- hifi-assembly - HiFi assemblies that usually should NOT be polished
- assembly-qc - Merqury QV before/after is the polishing stop signal
- read-alignment/bwa-alignment - Map short reads to the draft for Polypolish/Pilon
- long-read-sequencing/long-read-alignment - minimap2 mapping of long reads for Racon
- long-read-sequencing/medaka-polishing - medaka mechanics and model tables; this skill owns the strategy
- workflows/genome-assembly-pipeline - End-to-end QC -> assemble -> polish -> scaffold -> QC
<!-- END FILE: genome-assembly/assembly-polishing/SKILL.md -->

## 子目录：genome-assembly/assembly-qc

<!-- BEGIN FILE: genome-assembly/assembly-qc/SKILL.md -->
---
name: bio-genome-assembly-assembly-qc
description: Evaluates genome assembly quality across the three orthogonal axes - contiguity (QUAST auN/NG50/NGx, not bare N50), completeness (BUSCO/compleasm gene-space plus Merqury k-mer completeness), and correctness (reference-free Merqury QV, Inspector/CRAQ structural errors, asmgene false-duplication/collapse). Covers why N50 is the most-gamed metric, why QV measured on the polishing reads is circular, distinguishing uncollapsed haplotigs from real WGD, and the EBP/VGP 6.C.Q40 standard. Use when judging whether an assembly is good enough to annotate or publish, comparing assemblers, diagnosing a fragmented or duplicated assembly, or assessing a phased diploid assembly.
tool_type: cli
primary_tool: QUAST
---

## Version Compatibility

Reference examples tested with: QUAST 5.2+, BUSCO 5.5+ (and 6.x for odb12 lineages), compleasm 0.2.6+, Merqury 1.3+, meryl 1.4+, minimap2 2.26+, Inspector 1.2+, CRAQ 1.0+, merfin 1.0+, GenomeScope2 2.0+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

Results depend on inputs that outlive the binary version - record them:
- BUSCO/compleasm depend on the **lineage dataset** and OrthoDB generation. `_odb10` (BUSCO 5) and `_odb12` (BUSCO 6 default) gene sets are not comparable across the version boundary; a 99% on the shallow `eukaryota_odb10` (~255 genes) is a different claim from 99% on a deep clade set (~5,500+).
- Merqury QV/completeness depend on the **k-mer size** (from `best_k.sh <genome_size>`, not hardcoded) and the **read set** used for the k-mer DB (use accurate reads; see the circularity warning below).
- NG50/NGx/auNG depend on the **expected genome-size estimate** (GenomeScope2 / flow cytometry / a congener).

If code throws an error, introspect the installed tool and adapt rather than retrying.

# Assembly QC

**"Is my genome assembly any good?"** -> Measure all three orthogonal axes - contiguity, completeness, correctness - with reference-free methods, because no single number (least of all N50) is quality.
- CLI: `quast.py asm.fa --large --eukaryote -o out` (contiguity + reference-based structure), `busco -i asm.fa -m genome -l <lineage>` or `compleasm run -a asm.fa -l <lineage>` (gene completeness), `merqury.sh reads.meryl asm.fa out` (reference-free QV + k-mer completeness), `inspector.py -c asm.fa -r reads.fq` (reference-free structural errors)

## The Single Most Important Modern Insight -- Quality Is Three Orthogonal Axes; N50 Is the Most-Gamed One

Assembly quality is **three genuinely orthogonal axes - contiguity, completeness, correctness - and a single number on any one is not quality.** The axes do not predict each other, and the diagnostic failure modes prove it:

- **Contiguous + wrong:** a single-contig "chromosome" that is three chromosomes misjoined. Perfect N50, catastrophic correctness. Only Hi-C / a same-species reference / read-discordance catches it.
- **Complete + shredded:** BUSCO 99%, but repeats collapsed, segmental duplications merged, intergenic space wrong. BUSCO is gene-space-only and cannot see it.
- **Accurate + incomplete:** QV60 over the 92% that assembled, with the hard 8% (centromeres, rDNA, satellites) simply absent. QV is silent about what is not there.

The field's historical sin is reporting **contiguity alone** because it is cheapest to compute and easiest to game. **N50 is the most-gamed metric in genomics:** it rises when sequence is thrown away (N50 is computed on what survives), when misjoins are *not* broken (a misjoined contig is a long contig), and when haplotigs are retained. A bigger N50 is louder, not better. Three load-bearing moves:

1. **Report auN/NGx, not bare N50.** auN = the area under the Nx curve = length-weighted mean contig length; it integrates the whole curve and is continuous where N50 jumps discontinuously (the small-L50 / T2T regime). NGx/auNG normalize to the **expected genome size**, coupling contiguity to completeness (an assembly that drops half the genome gets a great N50 but a terrible NG50). Always report contig AND scaffold N50 - if scaffold >> contig, the contiguity is glue (Ns), not sequence.
2. **Default to reference-free.** For a *novel* genome there is no trusted reference; QUAST against a divergent relative reports real inversions/SVs as "misassemblies" and real SNPs as "mismatches". Use Merqury QV (accuracy) + Inspector/CRAQ (structure) + asmgene (false dup/collapse). QUAST is the special case "I have a same-organism reference," not the default.
3. **Report a Merqury QV - and never compute it on the polishing reads.** QV is the reference-free accuracy standard reviewers now demand; an assembly paper with no QV is a red flag. But QV from the same reads used for polishing is **circular** - the polisher already made the assembly agree with those reads, so the QV measures convergence, not correctness. Build the k-mer DB from accurate, ideally independent reads (HiFi/Illumina, not noisy ONT).

## Tool Taxonomy

| Tool | Citation | Axis / Role | When |
|------|----------|-------------|------|
| QUAST / calN50 | Gurevich 2013 *Bioinformatics*; auN = Li blog (no journal) | contiguity (auN/NGx, N50/L50) + reference-based structure (NA50, misassemblies) | always for contiguity; structure only vs a same-organism reference |
| BUSCO | Manni 2021 *Mol Biol Evol*; Simão 2015 *Bioinformatics* | gene-space completeness (C/S/D/F/M) | universal; conservative on good genomes |
| compleasm | Huang & Li 2023 *Bioinformatics* | gene-space completeness, miniprot-based | faster + more sensitive; default on HiFi/T2T-era genomes |
| Merqury | Rhie 2020 *Genome Biol* | reference-free QV + k-mer completeness + spectra-cn + phasing | always; the accuracy gold standard |
| merfin | Formenti 2022 *Nat Methods* | multiplicity-corrected QV / polishing | refine QV biased by k-mer multiplicity |
| Inspector | Chen 2021 *Genome Biol* | reference-free structural + base errors (long reads) | novel genomes; can also correct |
| CRAQ | Li 2023 *Nat Commun* | reference-free structural/regional errors (clipped alignments) | novel genomes; flags misjoins to split |
| asmgene | Li (minimap2, no separate journal) | gene collapse / false duplication | high-quality genomes where BUSCO saturates |
| GenomeScope2 | Ranallo-Benavidez 2020 *Nat Commun* | genome size / het / repeat % from k-mers | the size estimate NG50/auNG/spectra-cn need (-> genome-profiling) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Novel genome, no trusted reference | Merqury QV + k-mer completeness + BUSCO/compleasm + auN/NGx + Inspector/CRAQ | reference-free triad; QUAST structure is uninterpretable here |
| Same-species (near-isogenic) reference available | add QUAST `--large --eukaryote -r ref.fa` (NA50, misassemblies) | reference-based structure is trustworthy only vs the same organism |
| High-quality HiFi/T2T-era assembly, BUSCO looks low | compleasm | BUSCO under-reports good genomes (its predictor, not the assembly, misses genes) |
| Contiguity claim must resist gaming | auN/auNG via `calN50.js -L <size>` | N50 is a single unstable order-statistic and is gameable |
| High BUSCO-Duplicated, size > expected | spectra-cn + asmgene + GenomeScope2 size -> purge_dups | distinguish uncollapsed haplotigs (purge) from real WGD (keep) |
| Phased diploid / trio assembly | Merqury hap-mers: switch/hamming error + blob plot | phasing accuracy is the extra axis |
| Need genome size / het before NG50 | -> genome-profiling (GenomeScope2) | NG/auN/spectra-cn all need a size estimate |
| Reads not yet QC'd | -> read-qc/quality-reports | garbage-in caps assembly quality |
| Bacterial isolate / MAG completeness+contamination | -> contamination-detection (CheckM2/GUNC/MIMAG) | marker-gene completeness/contamination is a different problem |

## Contiguity -- auN/NGx (not bare N50)

```bash
k8 calN50.js -L <genome_size> asm.fa       # N50/L50 + NG50/NGx + auN/auNG; -L sets genome size for NG/auNG (ships with minimap2)
quast.py asm.fa --large --eukaryote -t 16 -o quast_out   # N50/L50, GC, # contigs; NG50 only with -r or --est-ref-size; structure only if -r given
```

`--large` implies `--eukaryote --min-contig 3000 --min-alignment 500 --extensive-mis-size 7000`. Report contig AND scaffold N50; a scaffold N50 far above the contig N50 means the contiguity is scaffolding Ns, and every gap is a join hypothesis that could be a misassembly. NA50 (QUAST, contigs broken at misassemblies) far below N50 means the contiguity is partly fictional.

## Completeness -- BUSCO / compleasm + Merqury k-mer completeness

```bash
busco -i asm.fa -m genome -l vertebrata_odb10 -o busco_out -c 16   # metaeuk predictor (default)
busco -i asm.fa -m genome --auto-lineage -o busco_out -c 16        # auto-pick if clade unknown
compleasm run -a asm.fa -l vertebrata -o compleasm_out -t 16        # miniprot-based; faster + more sensitive
```

Reported as `C:[S,D],F,M,n`. **Read C, F, and M together, never C alone:** high Fragmented with high Complete signals a contiguity/base-quality problem hidden behind the headline. Use the **deepest applicable clade dataset** (a 99% on the shallow `eukaryota_odb10` ~255-gene set is trivially easy and not comparable to a deep clade set), and record the lineage + OrthoDB generation. On a high-quality assembly, BUSCO reported ~95.7% complete where compleasm reported ~99.6% on the same human genome (Huang & Li 2023) - the missing ~4% was missing from BUSCO's *predictor*, not the genome - so prefer compleasm on good genomes. Both share gene-space blindness: they say nothing about intergenic/repeat/regulatory sequence. **Merqury k-mer completeness** scores the whole genome (reliable read k-mers found in the assembly / reliable read k-mers in the reads), catching missing sequence BUSCO cannot see; it is blind to structure (a scrambled-but-present genome scores 100%).

## Correctness -- Merqury QV (reference-free) and structural validation

**Goal:** Get a reference-free per-base accuracy (QV) plus a copy-number/false-duplication picture, then structural errors without a reference.

**Approach:** Build a meryl k-mer DB at the `best_k.sh`-derived k from accurate reads, run Merqury for QV + completeness + spectra-cn, and map raw long reads back with Inspector/CRAQ for structural errors. Refine QV with merfin where multiplicity bias matters.

```bash
best_k.sh <genome_size>                          # prints recommended k (NOT hardcoded); ~18-21 for Gbp genomes
meryl count k=21 reads.fastq output reads.meryl  # k from best_k.sh; use ACCURATE reads (HiFi/Illumina)
merqury.sh reads.meryl asm.fa out                # -> out.qv (per-scaffold + overall), out.completeness.stats, spectra-cn

inspector.py -c asm.fa -r reads.fq -o insp_out --datatype hifi -t 16   # reference-free structural + base errors
craq -g asm.fa -sms long_reads.bam -ngs short_reads.bam -o craq_out    # R-AQI/S-AQI; CRE (regional)/CSE (structural)
```

QV: with `E = K_asm-only / K_total`, per-base error `P = 1 - (1 - E)^(1/k)` and `QV = -10*log10(P)` (the `^(1/k)` converts a k-mer error rate to per-base, since one wrong base breaks k overlapping k-mers). QV40 = 1 error/10 kb (the EBP/VGP floor), QV50 strong, ~QV60 = T2T-grade (1/Mb). The **spectra-cn plot** reads completeness and false duplication in one figure: a black "missing" peak at homozygous depth = real content absent; 2-copy k-mers under the 1-copy peak = uncollapsed haplotigs; error k-mers sit far left.

## EBP/VGP standards and phased QC

The EBP minimum is **6.C.Q40**: `x.y.z` where x = log10 of contig NG50 (6 = 1 Mb), y = scaffold level (C = chromosome-scale), z = QV (40 = <1 error/10 kb). It is literally the triad turned into a label, and the bar moves - T2T pushed the achievable frontier to ~Q60/gapless, so bragging about QV40 in 2026 is hitting the floor. Match the bar to the organism (the relaxed "5" tier, >100 kb contig NG50, exists for low-input species). For phased diploid/trio assemblies, Merqury hap-mers (parental k-mers, or Hi-C) give the **switch error** (local haplotype flips within a block) and **hamming error** (global mis-assignment fraction) - report both, and read the hap-mer blob plot (cleanly phased contigs sit on one axis).

## Per-Method Failure Modes

### Leading with N50 (and stopping)
**Trigger:** reporting a single N50 as the quality verdict. **Mechanism:** N50 rises on thrown-away sequence, unbroken misjoins, and retained haplotigs; it is also a single unstable order-statistic. **Symptom:** big N50, unstated QV/completeness/NG50. **Fix:** report auN/NGx + BUSCO/compleasm + Merqury QV; treat N50-only claims as untrustworthy.

### QUAST against a divergent reference
**Trigger:** `quast.py -r congener.fa` on a novel genome. **Mechanism:** real inversions/SVs and SNPs between organism and reference are scored as "misassemblies"/"mismatches"; the count scales with divergence, not error. **Symptom:** "hundreds of misassemblies" on a correct assembly. **Fix:** use reference-free correctness (Inspector/CRAQ/Merqury); reserve QUAST structure for a same-organism reference.

### QV computed on the polishing reads
**Trigger:** QV from the exact reads used to polish. **Mechanism:** the polisher made the assembly agree with those reads by construction. **Symptom:** impressively high QV that rose after polishing with the QV reads. **Fix:** build the k-mer DB from accurate, ideally independent reads; consider merfin for multiplicity-corrected QV.

### High BUSCO-Duplicated read as success
**Trigger:** treating high BUSCO-D as "extra coverage / more complete". **Mechanism:** uncollapsed haplotigs (both alleles kept as separate primary contigs) vs real WGD vs split models. **Symptom:** D in high single digits to tens, assembly size >> GenomeScope2 estimate. **Fix:** triangulate size + spectra-cn 2-copy peak + asmgene false-dup; if no WGD -> purge_dups, then re-QC (watch for over-purge: size dropping below the estimate deletes real segmental duplications).

### QV/BUSCO accepted on an incomplete genome
**Trigger:** QV60 + BUSCO 99% taken as "done". **Mechanism:** QV is measured on what assembled; BUSCO scores the conserved easy core only. **Symptom:** high accuracy and gene-completeness while 8-15% of sequence (repeats/centromeres) is absent. **Fix:** add Merqury k-mer completeness (whole-genome) and inspect read mapping-rate/coverage uniformity.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Merqury QV >= 40 | EBP/VGP minimum (Rhie 2021) | 1 error/10 kb; QV50 strong, ~Q60 T2T-grade; report the actual value |
| QV from polishing reads | circularity trap | always biased high; use independent/accurate reads, prefer merfin |
| BUSCO Complete >= 95%, Fragmented < 5% | field convention | read F+M with C; high F = contiguity/base-quality problem behind a good C% |
| BUSCO Duplicated ~1-3% (clean haploid); >5-8% no WGD | assembly norm | uncollapsed haplotigs -> purge_dups; cross-check size + spectra-cn + asmgene |
| compleasm preferred on good genomes | Huang & Li 2023 | BUSCO under-reports (~95.7% vs ~99.6% on human) due to its predictor |
| k-mer completeness (Merqury) >= 95% | field convention | lower = sequence absent that the BUSCO gene set cannot see |
| Contig NG50 >= 1 Mb (EBP "6") | Rhie 2021 / EBP standards | the 6.C.Q40 contig bar; relaxed "5" (>100 kb) for low-input species |
| Report auN/NGx, not bare N50 | Li (auN blog) | N50 is gameable and a single unstable order-statistic |
| NG/auN need a genome-size estimate | by definition | GenomeScope2/flow cytometry; couples contiguity to completeness |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Big N50, no QV reported | leading with the most-gamed metric | add Merqury QV, k-mer completeness, auN/NGx |
| Hundreds of QUAST "misassemblies" on a novel genome | divergent reference; biology scored as error | reference-free (Inspector/CRAQ); QUAST only vs same organism |
| QV suspiciously high, rose after polishing | QV computed on the polishing reads (circular) | independent/accurate-read k-mer DB; merfin |
| Assembly ~1.5-2x expected size, high BUSCO-D | uncollapsed haplotigs (false duplication) | purge_dups; verify with spectra-cn + asmgene |
| Size drops below GenomeScope2 estimate after purging | over-purged real segmental duplications | back off purge stringency; check asmgene collapse direction |
| BUSCO low-90s on a HiFi/T2T assembly | BUSCO predictor misses present genes | re-run compleasm before concluding incompleteness |
| Scaffold N50 >> contig N50 reported as contiguity | contiguity is gap-Ns, not sequence | report contig N50 too; each gap is a join hypothesis |

## References

- Gurevich A, Saveliev V, Vyahhi N, Tesler G. 2013. QUAST: quality assessment tool for genome assemblies. *Bioinformatics* 29:1072-1075.
- Manni M, et al. 2021. BUSCO update: novel and streamlined workflows along with broader and deeper phylogenetic coverage for scoring of eukaryotic, prokaryotic, and viral genomes. *Mol Biol Evol* 38:4647-4654.
- Simão FA, et al. 2015. BUSCO: assessing genome assembly and annotation completeness with single-copy orthologs. *Bioinformatics* 31:3210-3212.
- Huang N, Li H. 2023. compleasm: a faster and more accurate reimplementation of BUSCO. *Bioinformatics* 39:btad595.
- Rhie A, Walenz BP, Koren S, Phillippy AM. 2020. Merqury: reference-free quality, completeness, and phasing assessment for genome assemblies. *Genome Biol* 21:245.
- Formenti G, et al. 2022. Merfin: improved variant filtering, assembly evaluation and polishing via k-mer validation. *Nat Methods* 19:696-704.
- Chen Y, et al. 2021. Accurate long-read de novo assembly evaluation with Inspector. *Genome Biol* 22:312.
- Li K, et al. 2023. CRAQ: identification of errors in draft genome assemblies at single-nucleotide resolution for quality assessment and improvement. *Nat Commun* 14:6556.
- Ranallo-Benavidez TR, Jaron KS, Schatz MC. 2020. GenomeScope 2.0 and Smudgeplot for reference-free profiling of polyploid genomes. *Nat Commun* 11:1432.
- Rhie A, et al. 2021. Towards complete and error-free genome assemblies of all vertebrate species (VGP). *Nature* 592:737-746.
- Li H. 2020. auN: a new metric to measure assembly contiguity. Blog post (lh3.github.io); auN/asmgene tools ship in minimap2/calN50 (Li 2018 *Bioinformatics* 34:3094-3100).
- Guan D, et al. 2020. Identifying and removing haplotypic duplication in primary genome assemblies (purge_dups). *Bioinformatics* 36:2896-2898.

## Related Skills

- short-read-assembly - Short-read assemblies plateau at the repeat structure; QC shows it
- long-read-assembly - Produces the contiguous-but-error-prone contigs this QC evaluates
- hifi-assembly - Phased diploid output whose false duplication and switch/hamming error this QC checks
- assembly-polishing - Merqury QV plateau is the honest stop signal; never QV on the polishing reads
- scaffolding - Validate chromosome-scale joins (Hi-C/contact map) before trusting scaffold NG50
- contamination-detection - MAG completeness/contamination (CheckM2/GUNC/MIMAG) is a separate problem
- genome-profiling - GenomeScope2 genome-size estimate that NG50/auNG/spectra-cn require
- genome-annotation/annotation-qc - Assembly-side completeness; purge haplotigs before annotating
- workflows/genome-assembly-pipeline - End-to-end QC -> assemble -> polish -> scaffold -> QC
<!-- END FILE: genome-assembly/assembly-qc/SKILL.md -->

## 子目录：genome-assembly/contamination-detection

<!-- BEGIN FILE: genome-assembly/contamination-detection/SKILL.md -->
---
name: bio-genome-assembly-contamination-detection
description: Detects and removes contamination in genome assemblies via two disjoint workflows - foreign-sequence screening of a single-organism (eukaryote/isolate) assembly with NCBI FCS-GX (GenBank-submission-mandatory), FCS-adaptor, and BlobToolKit blob plots; and MAG/bin quality assessment with CheckM2 plus GUNC (chimerism) plus GTDB-Tk taxonomy, judged against MIMAG. Covers why CheckM2 alone is blind to disjoint-marker chimeras, the FCS-GX RAM wall, organelle/NUMT triage, strain heterogeneity, and the HGT-vs-contamination (tardigrade) trap. Use when screening an assembly for foreign contamination before GenBank submission, assessing MAG completeness/contamination/chimerism, deciding which contigs to remove, or distinguishing real HGT from contaminant contigs.
tool_type: cli
primary_tool: CheckM2
---

## Version Compatibility

Reference examples tested with: FCS-GX 0.5+, FCS-adaptor 0.5+, BlobToolKit 4.3+, CheckM2 1.0+, GUNC 1.0+, GTDB-Tk 2.4+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

Database release drives results more than the binary version. Record: the **FCS-GX GX database** release (it grows each release; ~470 GiB and rising), the **CheckM2 DIAMOND DB** version, the **GUNC reference** (proGenomes 2.1 default vs GTDB), and the **GTDB-Tk reference package release** (e.g. R220) - GTDB-Tk fails loudly if the DB release does not match the binary. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Contamination Detection

**"Is my assembly contaminated?"** -> First decide which of two unrelated questions is being asked - "which contigs are not my organism?" (foreign-sequence screen) or "how complete/clean/chimeric is this bin?" (MAG quality) - then run the matching toolset; crossing them returns confidently wrong numbers.
- CLI (foreign): `run_fcsadaptor.sh` then `fcs.py screen genome --fasta asm.fa --gx-db <db> --tax-id <taxid>`, `blobtools create/add/view`
- CLI (MAG): `checkm2 predict -i bins/ -o out/` AND `gunc run -d bins/ -o out/`, `gtdbtk classify_wf`

## The Single Most Important Modern Insight -- "Contamination" Is Two Disjoint Problems With Disjoint Toolsets

There is no single "contamination" measurement. There are two questions that share a word and almost nothing else, and applying one toolset to the other problem runs to completion and prints a plausible, meaningless number.

1. **Foreign sequence in a single-organism assembly** (a eukaryotic nuclear genome or a cultured isolate with bacterial/human/vector contigs in it). The question is *which contigs are not my target organism?* Answer = a **set of contigs to remove, trim, or split out**. Tools: **NCBI FCS-GX** + **FCS-adaptor** (now GenBank-submission-mandatory), **BlobToolKit** (the GC x coverage x taxonomy blob plot). There is no "contamination %".

2. **MAG/bin quality** (a bin recovered from a metagenome). The question is *how complete is this bin and how much is from other organisms?* Answer = a **percentage pair** (completeness %, contamination %) plus a chimerism verdict, judged against **MIMAG**. Tools: **CheckM2** + **GUNC** together, **GTDB-Tk** for taxonomy.

**The cardinal category error:** running CheckM2/CheckM on a eukaryotic nuclear assembly (its bacterial/archaeal marker sets are meaningless for a eukaryote - eukaryote completeness is BUSCO; see assembly-qc), or running FCS-GX on a single MAG and reading the flagged-length fraction as "the MIMAG contamination %". Both wrong applications complete silently and emit a number. The only defense is knowing which question each tool answers.

**The second load-bearing fact - CheckM2 and GUNC are blind to different things, so report the pair, never the % alone.** CheckM2 estimates contamination from **marker-gene redundancy** (a single-copy marker seen twice = contamination signal). A **chimera of two organisms with disjoint marker complements** - organism A contributed markers 1-60, organism B markers 61-120 - shows *no* duplicated markers, so CheckM2 reports low contamination while the bin is biological nonsense. GUNC catches exactly this, because it scores whether taxonomic signal is *consistent across contigs* (clade separation score), not marker counts. Neither is a superset of the other.

## Tool Taxonomy

| Tool | Citation | Role | Problem |
|------|----------|------|---------|
| FCS-adaptor | Astashyn 2024 *Genome Biol* | adaptor/vector screen (VecScreen successor); tiny DB, trivial RAM | foreign (run FIRST) |
| FCS-GX | Astashyn 2024 *Genome Biol* | cross-taxon foreign-sequence screen vs a declared tax-id; GenBank-mandatory | foreign |
| BlobToolKit | Challis 2020 *G3* | GC x coverage x taxonomy blob plot for visual triage; the maintained successor to BlobTools | foreign |
| tiara | Karlicki 2022 *Bioinformatics* | deep-learning euk/prok/organelle/plastid/mito contig classifier (alignment-free) | foreign / organelle partitioning |
| CheckM2 | Chklovski 2023 *Nat Methods* | ML completeness + contamination (lineage-agnostic; handles novel/reduced lineages) | MAG (default) |
| CheckM (legacy) | Parks 2015 *Genome Res* | lineage-specific collocated markers on a placement tree; reports Strain heterogeneity | MAG (legacy; slow, ~40 GB RAM) |
| GUNC | Orakov 2021 *Genome Biol* | taxonomic-chimerism detection via clade separation score (CSS) | MAG (run WITH CheckM2) |
| GTDB-Tk | Chaumeil 2020 *Bioinformatics* | GTDB taxonomic classification of bacterial/archaeal genomes | MAG taxonomy |

BlobTools (Laetsch & Blaxter 2017 *F1000Res*) and CheckM are the legacy predecessors; BlobToolKit and CheckM2 are the maintained defaults. CAT/BAT (contig taxonomy) and MAGpurify (reference-free MAG cleaning) exist but are secondary; RefineM is deprecated by its author (use GUNC + manual curation, or MDMcleaner for SAGs/dark-matter lineages).

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Eukaryotic nuclear assembly headed for GenBank | FCS-adaptor -> FCS-GX (mandatory) -> BlobToolKit for triage | submission bounces without a clean FCS screen |
| Cultured bacterial/archaeal isolate | FCS-GX + FCS-adaptor; CheckM2 as a completeness sanity check | an isolate should be ~100% complete, low contam |
| MAG(s) binned from a metagenome | CheckM2 AND GUNC together; score vs MIMAG; GTDB-Tk for taxonomy | the % pair plus the orthogonal chimerism verdict |
| Unbinned metagenome | bin first (-> metagenome-assembly), THEN CheckM2 + GUNC per bin | CheckM2/GUNC consume bins, do not make them |
| Eukaryotic contigs mixed into a metagenome | tiara / Whokaryote / EukRep to partition euk from prok | CheckM2 markers are prokaryote-only |
| Organellar (mito/chloroplast) contigs in a nuclear assembly | tiara organelle classes + coverage spike -> separate, do NOT delete | organelles are real biology; submit as own record |
| Foreign-looking gene embedded in a host scaffold | investigate integration (-> comparative-genomics) before removing | could be real HGT/endosymbiont, not contamination |
| Read-level host removal before assembly | -> read-qc/contamination-screening, metagenomics/kraken-classification | this skill screens assembled sequence, not reads |
| ANI/species placement of the cleaned genome | -> comparative-genomics/genome-distance-and-species-delineation | taxonomy after decontamination |

## FCS-adaptor (Run First - Cheap and Unambiguous)

```bash
# Adaptor/vector screen; tiny DB, trivial RAM. --euk or --prok for the lineage.
run_fcsadaptor.sh --fasta-input assembly.fa.gz --output-dir ./adaptor_out --euk
```

Adaptor and vector hits are unambiguous - always trim or exclude. Running adaptor first removes the obvious junk and shrinks the input before the expensive GX pass.

## FCS-GX (The GenBank-Mandatory Foreign Screen)

```bash
# Screen against the GX database; --tax-id is the NCBI taxid of the SOURCE organism.
python3 ./fcs.py screen genome --fasta assembly.fa.gz --out-dir ./gx_out/ \
    --gx-db "$GXDB_LOC/gxdb" --tax-id 9606

# Apply ONLY the auto-clean actions (EXCLUDE/TRIM/FIX) to produce a cleaned FASTA.
zcat assembly.fa.gz | python3 ./fcs.py clean genome \
    --action-report ./gx_out/assembly.fa.9606.fcs_gx_report.txt \
    --output clean.fasta --contam-fasta-out contam.fasta
```

The action report (`<name>.<taxid>.fcs_gx_report.txt`, where `<name>` keeps the input name minus only `.gz` - e.g. `assembly.fa.gz` -> `assembly.fa.9606.fcs_gx_report.txt`) assigns each flagged region an action: **EXCLUDE** (drop the whole sequence), **TRIM** (remove a contaminated end), **FIX** (hard-mask an internal span), or **REVIEW** (flagged but NOT auto-cleaned - manual inspection required). A separate **INFO** action specifically marks sequence known to be integrated into host genomes (e.g. endosymbiont insertions). `clean genome` acts on EXCLUDE/TRIM/FIX only; it does **not** touch REVIEW or INFO. Those non-auto-cleaned tiers exist precisely because FCS-GX can flag legitimate HGT/endosymbiont sequence as contaminant - never bulk-delete every flagged contig without reading the report.

**The RAM wall (an operational, cloud-forcing fact).** The GX database is ~470 GiB on disk and the documented sweet spot is a **~512 GiB-RAM** host. Underprovisioned, the run does not fail - it crawls (minutes become days when the DB spills out of RAM). Best practice copies the DB into a tmpfs RAM disk; most labs rent a high-memory cloud VM for the screen. The first question before advising FCS-GX is "is there ~1/2 TB RAM or a cloud budget?".

## BlobToolKit (The Blob Plot - Visual Triage)

```bash
blobtools create --fasta assembly.fasta ./BlobDir
blobtools add --hits diamond.out --taxrule bestsumorder --taxdump /path/taxdump \
    --cov mapping.bam ./BlobDir
blobtools view --remote ./BlobDir   # interactive viewer; GC(x) vs coverage(y), sized by length, colored by taxonomy
```

Each contig is plotted by **GC fraction (x)** vs **coverage (y)**, sized by length, colored by best-hit taxonomy. The target organism forms one tight GC x coverage cloud; a free-living contaminant grows independently and forms its own cloud at a *different* GC *and* a *different* coverage. Inputs: a hit file (BLAST/DIAMOND vs nt/UniProt), a coverage BAM, and an NCBI taxdump. `blobtools filter` can extract or drop by taxon - but see the failure mode below before doing so.

## Merge CheckM2 and GUNC

**Goal:** Produce the joint CheckM2 x GUNC table that is the field standard for MAG QC, so a chimera invisible to CheckM2 is not reported as clean.

**Approach:** Load both reports, join on genome name, and apply MIMAG thresholds AND the GUNC pass flag together; never gate on contamination % alone.

```python
import pandas as pd

CONTAM_HQ = 5      # MIMAG high-quality: contamination < 5% (Bowers 2017); above this, gene-content inference is unreliable
COMPLETE_HQ = 90   # MIMAG high-quality: completeness > 90%
RRS_TRUST = 0.5    # GUNC pass is trustworthy only when reference_representation_score > 0.5; below it 'pass' means 'can't tell'

checkm = pd.read_csv('checkm2_out/quality_report.tsv', sep='\t')
gunc = pd.read_csv('gunc_out/GUNC.progenomes_2.1.maxCSS_level.tsv', sep='\t')
merged = checkm.merge(gunc, left_on='Name', right_on='genome', how='left')

merged['gunc_trustworthy'] = merged['reference_representation_score'] > RRS_TRUST
merged['high_quality'] = ((merged['Completeness'] > COMPLETE_HQ) &
                          (merged['Contamination'] < CONTAM_HQ) &
                          (merged['pass.GUNC'] == True) &
                          merged['gunc_trustworthy'])
merged.to_csv('combined_qc.tsv', sep='\t', index=False)
```

CheckM2 also runs as `checkm2 predict -i bins/ -o checkm2_out --threads 16 -x fa` (downloads its own DIAMOND DB), and GUNC as `gunc run -d bins/ -o gunc_out -t 16 -e .fa` against a downloaded reference (`gunc download_db`). GTDB-Tk taxonomy is `gtdbtk classify_wf --genome_dir bins/ --out_dir gtdbtk_out -x fa --cpus 16`.

## GUNC and the RRS Trap

`pass.GUNC = TRUE` at **CSS <= 0.45** is not a clean bill of health when `reference_representation_score` (RRS) is low. Low RRS means the genome is barely represented in GUNC's reference DB - there is not enough signal to *detect* chimerism, so "pass" degenerates into "can't tell, not clean". For genuinely novel lineages (microbial dark matter), a GUNC pass is weak evidence; trust it only when RRS > 0.5, and otherwise lean on manual contig inspection or MDMcleaner. Read the configurations: CheckM2-high-contam + GUNC-pass = duplicative contamination within one lineage; CheckM2-low-contam + GUNC-fail = the dangerous disjoint-marker chimera; both pass with high RRS = the only "clean" verdict.

## The Tardigrade Lesson (HGT vs Contamination)

Boothby 2015 (*PNAS* 112:15976) reported ~17% of tardigrade genes arrived by horizontal gene transfer; Koutsovoulos 2016 (*PNAS* 113:5053) showed almost all of it was undetected bacterial contamination in the assembly, dropping real HGT to ~1-2%. The original paper was **corrected, not retracted** - it stands as a cautionary monument. A foreign-looking gene has two explanations the *sequence alone cannot distinguish*: a contaminant contig, or a real HGT/endosymbiont gene integrated into the host genome. **The tell is physical integration, not taxonomy.** A real HGT gene sits *on a host contig* (host-gene flanks, host GC, host coverage, host introns); a contaminant sits *on its own contig* (foreign GC, its own coverage cloud, prokaryotic gene structure). Deleting everything that looks bacterial manufactures the opposite of Boothby's error - erasing real biology. Require integration evidence (host flanks, host-typical GC/coverage/introns, long reads spanning the host->foreign junction) before keeping or stripping.

## Organelles and NUMTs (A Third Category)

Mitochondrial and chloroplast sequence is legitimate biology that does not belong in the *nuclear* assembly record - it needs **separation, not deletion**. Deleting it loses the organelle genome (often the most-cited part of a non-model genome paper); leaving it inflates assembly size and creates fake duplicated content. Identify organellar contigs by tiara's plastid/mito classes plus a massive coverage spike and circular topology; assemble/submit them as their own record. The subtle trap: **NUMTs/NUPTs** (nuclear-integrated organellar fragments) are *real nuclear sequence that looks organellar* - do not strip them. Coverage discriminates: free organelle = huge coverage spike; NUMT = nuclear-level coverage.

## Per-Method Failure Modes

### CheckM2 on a eukaryotic nuclear assembly
**Trigger:** running CheckM/CheckM2 on a vertebrate/plant/insect genome. **Mechanism:** the marker sets are bacterial/archaeal single-copy genes; a eukaryote has none of the relevant context. **Symptom:** a plausible Completeness/Contamination pair that is pure noise. **Fix:** use BUSCO for eukaryote completeness (-> assembly-qc); CheckM2 is for prokaryotes/MAGs only.

### CheckM2 contamination read as the whole story (the chimera blind spot)
**Trigger:** "CheckM2 says 3%, the MAG is clean." **Mechanism:** CheckM2 counts marker redundancy and is blind to a chimera of two organisms with disjoint marker sets. **Symptom:** a 50/50 chimeric bin reported as low-contamination. **Fix:** run GUNC too; report the pair; trust a GUNC pass only when RRS > 0.5.

### FCS-GX % read as MIMAG contamination
**Trigger:** running FCS-GX on a single MAG and citing flagged-length as the contamination %. **Mechanism:** FCS-GX answers "foreign vs declared tax-id", not the intra-domain marker-redundancy MIMAG cares about. **Symptom:** a "contamination %" that means something different from CheckM2's. **Fix:** use CheckM2 for the MIMAG %; FCS-GX for foreign-sequence screening of single-organism assemblies.

### Auto-stripping every FCS-GX/blob foreign hit
**Trigger:** running `clean genome` and resubmitting, or `blobtools filter` on a whole taxon cloud, without reading the report. **Mechanism:** the screen flags legitimate HGT/endosymbiont/host genes with conserved-domain hits. **Symptom:** a real biological finding (HGT, symbiont) deleted from the assembly. **Fix:** treat EXCLUDE on near-complete-bacterial-genome contigs as real contamination; treat foreign flags on host-integrated, host-coverage, host-flanked sequence as REVIEW-and-verify.

### Trusting blob-plot taxonomy color over cluster geometry
**Trigger:** filtering out contigs by their BLAST-hit color. **Mechanism:** best-hit taxonomy is the noisiest axis - conserved domains (ribosomal proteins, HSP70) hit foreign taxa, and no-hit != contaminant. **Symptom:** real host genes deleted; large no-hit fractions panic-removed. **Fix:** decide on cluster geometry - off the main cloud on GC *and* coverage *and* consistent foreign taxonomy; coverage is the strongest single signal.

### Strain heterogeneity misread as contamination
**Trigger:** high CheckM contamination on a MAG with co-binned conspecific strains. **Mechanism:** near-identical single-copy markers from multiple strains register as duplicated. **Symptom:** inflated contamination % for what is one species' population. **Fix:** read CheckM's Strain heterogeneity column; high strain-heterogeneity = look closer (not ignore); GUNC + the strain flag disambiguate foreign-mixing from strain-mixing from duplication.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| MIMAG high-quality MAG: completeness > 90% AND contamination < 5% | Bowers 2017 *Nat Biotechnol* | above 5% contam, gene-content/metabolic inference is unreliable |
| MIMAG medium-quality: completeness >= 50% AND contamination < 10% | Bowers 2017 *Nat Biotechnol* | community-standard MQ floor |
| MIMAG HQ also requires 5S/16S/23S rRNA + >= 18 tRNAs | Bowers 2017 *Nat Biotechnol* | binners systematically lose rRNA; the most common reason a >90%/<5% MAG is only MQ |
| GUNC pass: CSS <= 0.45 | Orakov 2021 *Genome Biol* | benchmarked chimera/non-chimera cutoff; orthogonal to the % pair |
| GUNC pass trustworthy only when RRS > 0.5 | Orakov 2021 *Genome Biol* / GUNC docs | low RRS = too poorly represented to judge; pass means "can't tell" |
| Blob-plot contaminant call needs GC AND coverage AND taxonomy agreement | Laetsch & Blaxter 2017; field practice | any single axis alone is a false-positive generator |
| FCS-GX GX DB ~470 GiB, ~512 GiB RAM host | NCBI FCS wiki (grows per release) | underprovisioned = crawls, not fails; cloud-forcing |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| CheckM2 prints a Completeness/Contamination on a eukaryote | wrong tool for the organism | BUSCO for eukaryotes; CheckM2 is prokaryote/MAG only |
| "Clean" MAG (3% contam) is actually a chimera | CheckM2 blind to disjoint-marker chimeras | run GUNC; report the pair |
| GenBank submission bounced | FCS-GX/FCS-adaptor not run before submission | screen with FCS-adaptor then FCS-GX first |
| FCS-GX takes days | GX DB spilled out of RAM | provision ~512 GiB / tmpfs RAM disk / cloud VM |
| GTDB-Tk crashes on startup | DB release does not match the binary | install the reference package matching the GTDB-Tk version |
| Real HGT/symbiont gene deleted | auto-cleaned or taxon-filtered without review | check physical integration (host flanks/GC/coverage) before removal |
| Organelle genome lost | deleted as "contamination" | separate organellar contigs (coverage spike); submit as own record |

## References

- Astashyn A, et al. 2024. Rapid and sensitive detection of genome contamination at scale with FCS-GX. *Genome Biol* 25:60.
- Chklovski A, et al. 2023. CheckM2: a rapid, scalable and accurate tool for assessing microbial genome quality using machine learning. *Nat Methods* 20:1203-1212.
- Parks DH, et al. 2015. CheckM: assessing the quality of microbial genomes recovered from isolates, single cells, and metagenomes. *Genome Res* 25:1043-1055.
- Orakov A, et al. 2021. GUNC: detection of chimerism and contamination in prokaryotic genomes. *Genome Biol* 22:178.
- Bowers RM, et al. 2017. Minimum information about a single amplified genome (MISAG) and a metagenome-assembled genome (MIMAG) of bacteria and archaea. *Nat Biotechnol* 35:725-731.
- Chaumeil PA, et al. 2020. GTDB-Tk: a toolkit to classify genomes with the Genome Taxonomy Database. *Bioinformatics* 36:1925-1927.
- Challis R, et al. 2020. BlobToolKit - interactive quality assessment of genome assemblies. *G3 (Bethesda)* 10:1361-1374.
- Laetsch DR, Blaxter ML. 2017. BlobTools: interrogation of genome assemblies. *F1000Research* 6:1287.
- Karlicki M, Antonowicz S, Karnkowska A. 2022. Tiara: deep learning-based classification system for eukaryotic sequences. *Bioinformatics* 38:344-350.
- Boothby TC, et al. 2015. Evidence for extensive horizontal gene transfer from the draft genome of a tardigrade. *PNAS* 112:15976-15981.
- Koutsovoulos G, et al. 2016. No evidence for extensive horizontal gene transfer in the genome of the tardigrade Hypsibius dujardini. *PNAS* 113:5053-5058.

## Related Skills

- assembly-qc - BUSCO completeness for eukaryotes (not CheckM2) and the QC handoff
- metagenome-assembly - Binning produces the bins this skill scores with CheckM2 + GUNC
- hifi-assembly - False duplications inflate apparent content; distinct from contamination
- long-read-assembly - Produces the contigs screened here for foreign sequence
- metagenomics/kraken-classification - Read/contig taxonomic classification and pre-assembly host screening
- comparative-genomics/genome-distance-and-species-delineation - ANI/species placement after decontamination
- workflows/genome-assembly-pipeline - End-to-end assemble -> QC -> decontaminate
<!-- END FILE: genome-assembly/contamination-detection/SKILL.md -->

## 子目录：genome-assembly/genome-profiling

<!-- BEGIN FILE: genome-assembly/genome-profiling/SKILL.md -->
---
name: bio-genome-assembly-genome-profiling
description: Profiles a genome from raw reads BEFORE assembly with a k-mer spectrum (KMC or Jellyfish histogram), then models it with GenomeScope2 to estimate genome size, heterozygosity, repeat content, and ploidy, and Smudgeplot to infer ploidy from heterozygous k-mer pairs (diploid AB vs triploid AAB vs tetraploid AABB). Covers choosing k via Merqury best_k.sh, the k-mer-coverage vs sequencing-coverage confusion, reading het/repeat/contamination/organelle peaks, why noisy ONT must not be used for counting, and how the estimate becomes the NG50 denominator, the Flye -g value, the hifiasm --hom-cov/purge setting, and the 1.5-2x-too-big haplotig sanity check. Use when starting any de novo assembly, deciding whether short reads can work, estimating genome size for an unknown organism, diagnosing ploidy, or sanity-checking an assembly's size against expectation.
tool_type: cli
primary_tool: GenomeScope2
---

## Version Compatibility

Reference examples tested with: GenomeScope2 2.0+, KMC 3.2+, Jellyfish 2.3+, meryl 1.4+ (Merqury 1.3+), Smudgeplot 0.2.5+, KAT 2.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Smudgeplot changed its backend: classic releases (0.2.x) run `smudgeplot.py hetkmers`/`smudgeplot.py plot` on a KMC dump; newer releases (0.3+) run `smudgeplot hetmers`/`smudgeplot all` on a FastK database. Confirm which interface is installed (`smudgeplot.py --version` or `smudgeplot --version`) before scripting. GenomeScope2 ships as `genomescope2` and as `genomescope.R`; both take the same flags. meryl `best_k.sh` lives in the Merqury install. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Genome Profiling

**"What am I about to assemble, and what should I expect?"** -> Build a k-mer spectrum from raw accurate reads and model it to estimate genome size, heterozygosity, repeat content, and ploidy, which set every downstream assembly expectation and parameter.
- CLI: `kmc -k21 ... reads kmc_db tmp/ && kmc_tools transform kmc_db histogram reads.histo` (count) then `genomescope2 -i reads.histo -o gs_out -k 21 -p 2` (model); `smudgeplot.py hetkmers` / `smudgeplot.py plot` (ploidy)

## The Single Most Important Modern Insight -- Profile the Genome Before Assembling, or the Assembler Guesses For Itself

A k-mer spectrum built from the raw reads -- reference-free, before a single contig exists -- estimates genome size, heterozygosity, repeat content, and ploidy, and those four numbers set the rest of the project: the NG50 denominator (assembly-qc), Flye's `-g`/`--genome-size`, hifiasm's `--hom-cov`/purge level, and whether short reads can produce the assembly being asked for at all. Skipping it leaves the assembler to infer the homozygous-coverage peak itself; when it mis-estimates (heterozygosity, odd ploidy, contamination, a bimodal coverage spectrum) it over- or under-purges, and that is exactly why people publish genomes inflated 1.5-2x by uncollapsed haplotigs. Three load-bearing moves:

1. **The estimate is the denominator AND the sanity check.** NG50 is N50 against the *expected* genome size, not the assembly size, so without the estimate NG50 cannot be reported honestly. After assembly, the same number is the haplotig test: an assembly 1.5-2x the GenomeScope size with high BUSCO-Duplicated is uncollapsed haplotypes, not a big genome -- purge before believing the size (see hifi-assembly, assembly-qc).
2. **The spectrum reads as a diagnostic, not just a size estimate.** A single homozygous peak ~= haploid/inbred; a distinct half-coverage (AB) peak *left* of the homozygous (AA) peak is heterozygous diploid, and the het peak's area gives the heterozygosity rate. A heavy high-multiplicity tail is repeat content; a spike at very high multiplicity is organelle or high-copy repeat; a left-shoulder near multiplicity 1 is sequencing error or a low-coverage contaminant. Read it before trusting any number from it.
3. **Count with accurate reads only.** GenomeScope's negative-binomial mixture model assumes errors are rare and Poisson-like. Noisy ONT (raw/HAC) injects so many unique error k-mers that the error shoulder swamps the real peaks and the fit fails. Count from Illumina or PacBio HiFi; use the ONT reads to *assemble*, never to *profile*.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| KMC | Kokot 2017 *Bioinformatics* | disk-based k-mer counter -> histogram | default counter; frugal on RAM, fast on large genomes |
| Jellyfish | Marcais & Kingsford 2011 *Bioinformatics* | in-memory k-mer counter -> histogram | alternative counter; classic GenomeScope input |
| meryl | Rhie 2020 *Genome Biol* | k-mer counter + `best_k.sh` | derives k from genome size; feeds Merqury QV downstream |
| GenomeScope2 | Ranallo-Benavidez 2020 *Nat Commun* | model: size, het, repeat, ploidy from the histogram | the profiling model for diploids and polyploids |
| Smudgeplot | Ranallo-Benavidez 2020 *Nat Commun* | ploidy from het k-mer-pair coverage ratios | unknown ploidy; cross-check GenomeScope's `-p` |
| KAT | Mapleson 2017 *Bioinformatics* | spectra plots, reads-vs-assembly k-mer comparison | contamination triage; post-assembly completeness/spectra-cn |

## Decision Tree by Scenario

| Scenario | What the profile indicates | Path |
|----------|---------------------------|------|
| Single sharp peak, size ~ expected, low het | haploid/inbred or clonal; clean | proceed -> short-read-assembly or hifi-assembly with default purge |
| Two peaks (AB at ~half AA) | heterozygous diploid; het rate from AB area | HiFi+phasing best; if short reads only, expect haplotigs -> short-read-assembly (Platanus) |
| High het + Illumina only | short-read DBG will fragment and inflate 1.5-2x | get long reads, or plan purge_dups; do not report inflated size |
| GenomeScope `-p 2` fits poorly; Smudgeplot shows AAB/AABB | triploid/tetraploid; ploidy not 2 | re-run GenomeScope with correct `-p`; -> hifi-assembly haplotype expectations |
| Coverage peak < ~15-20x | too shallow for a stable model fit | sequence more, or treat size/het as lower-confidence; -> read-qc/quality-reports |
| Extra peak at odd multiplicity, or bimodal spectrum | contamination / organelle / mixed sample | KAT spectra triage; screen reads -> read-qc/quality-reports before assembling |
| Only noisy ONT available | cannot profile reliably from error-dominated spectrum | assemble first, then estimate size from the assembly + Merqury -> assembly-qc |
| Need the genome-size denominator for QC | GenomeScope haploid length | feed as NG50 expected size and Flye `-g` -> assembly-qc, long-read-assembly |

## Choosing k

**Goal:** Pick a k that is large enough that most k-mers are genomically unique but small enough to keep per-k-mer depth high.

**Approach:** Derive k from the expected genome size with Merqury's `best_k.sh` (formula `k = log4(G(1-p)/p)`, default tolerable collision rate `p=0.001`); a vertebrate-scale ~3 Gb genome returns k=21 (the de facto GenomeScope default), ~1 Gb returns k=20, and a ~12 Mb yeast returns k=17.

```bash
sh $MERQURY/best_k.sh 3100000000          # ~3.1 Gb vertebrate -> k=21 (the common GenomeScope default)
sh $MERQURY/best_k.sh 1000000000          # ~1 Gb -> k=20
sh $MERQURY/best_k.sh 12000000            # ~12 Mb yeast -> k=17
```

Too small a k saturates: nearly every k-mer recurs across the genome by chance, the unique/repeat peaks merge, and size is overestimated. Too large a k loses depth (per-k-mer coverage is `c*(L-k+1)/L`, so it drops as k rises) and the peaks blur into the error shoulder. k=21 is the long-standing default at vertebrate (~3 Gb) scale because it sits in this window; smaller genomes want smaller k (best_k.sh returns ~20 at 1 Gb, ~17 at 12 Mb). Use the SAME k for counting and for the `-k` passed to GenomeScope2.

## Counting K-mers and Running GenomeScope2

```bash
# KMC: -ci1 keeps singletons (the error shoulder GenomeScope models), -cs10000 caps the histogram tail
kmc -k21 -t16 -m64 -ci1 -cs10000 @fastq_list.txt kmc_db tmp/
kmc_tools transform kmc_db histogram reads.histo -cx10000

# GenomeScope2: -p 2 = diploid; raise for known/Smudgeplot-suggested polyploidy
genomescope2 -i reads.histo -o gs_out -k 21 -p 2

# Jellyfish alternative (-C canonical k-mers, mandatory for unstranded WGS)
jellyfish count -C -m 21 -s 4G -t 16 reads_*.fastq -o reads.jf
jellyfish histo -t 16 reads.jf > reads_jf.histo
```

GenomeScope2 writes a model fit (`model.txt`), the linear/log spectrum plots, and a summary with haploid genome length, heterozygosity, and a "% unique" (inverse of repeat content). `-cs10000`/`-cx10000` cap the histogram so a single organelle/repeat spike at multiplicity 100000+ does not dominate the file; raise the cap only for very high-coverage data.

## K-mer Coverage vs Sequencing Coverage (the confusion that breaks the fit)

GenomeScope reports `kmercov` (lambda) -- the mean coverage *per k-mer*, the x-position of the homozygous peak. This is NOT per-base sequencing coverage. They differ by the `(L-k+1)/L` factor: at read length L=150 and k=21, a k-mer is covered `130/150 ~= 0.87x` as often as a base, so a 50x-sequenced genome shows a homozygous peak near multiplicity 43, not 50. Passing the sequencing coverage where GenomeScope expects the k-mer-coverage peak (e.g. as an `-l` initial guess), or reading lambda back as sequencing depth, mis-scales the model and the size estimate. Read the peak off the plot; let GenomeScope estimate lambda unless the fit fails, then seed `-l` with the observed peak position.

## Ploidy with Smudgeplot

```bash
# Classic (0.2.x, KMC backend): pick L/U coverage cutoffs, dump het k-mer pairs, plot
L=$(smudgeplot.py cutoff kmc_db.histo L)     # ~0.5x the haploid peak (errors below)
U=$(smudgeplot.py cutoff kmc_db.histo U)     # ~8.5x the haploid peak (repeats above)
kmc_tools transform kmc_db -ci"$L" -cx"$U" dump -s kmc_L"$L"_U"$U".dump
smudgeplot.py hetkmers -o kmer_pairs < kmc_L"$L"_U"$U".dump
smudgeplot.py plot kmer_pairs_coverages.tsv -o sample
```

Smudgeplot infers ploidy from the coverage RATIO of heterozygous k-mer pairs, independent of GenomeScope's model: a diploid AB pair sits at `CovB/(CovA+CovB) ~= 0.5`, a triploid AAB near 0.33, a tetraploid AABB shows smudges at 0.25 and 0.5. When Smudgeplot's inferred ploidy disagrees with the `-p` that fit GenomeScope best, that disagreement is itself the finding -- re-examine for polyploidy, aneuploidy, or contamination rather than forcing one answer.

## Per-Method Failure Modes

### Profiling from noisy ONT
**Trigger:** counting k-mers from raw/HAC Nanopore reads. **Mechanism:** ~5-10% per-base error makes nearly every error k-mer unique, burying the real peaks under the multiplicity-1 shoulder. **Symptom:** GenomeScope fit fails or returns absurd size/het. **Fix:** count from Illumina or HiFi; profile from the assembly + Merqury if only ONT exists.

### Too-low coverage
**Trigger:** homozygous peak below ~15-20x. **Mechanism:** the error shoulder and the real peak overlap; the negative-binomial mixture cannot separate them. **Symptom:** wide confidence intervals, unstable size, no clean peaks. **Fix:** sequence more depth, or report size/het as low-confidence.

### Reading lambda as sequencing depth
**Trigger:** treating GenomeScope `kmercov` as per-base coverage, or seeding `-l` with sequencing depth. **Mechanism:** k-mer coverage = depth * `(L-k+1)/L` < depth. **Symptom:** mis-scaled model, size off by the `(L-k+1)/L` factor. **Fix:** read lambda off the peak; do not substitute sequencing coverage.

### k too small (saturation)
**Trigger:** k=15-17 on a large/repeat-rich genome. **Mechanism:** most k-mers recur by chance; unique and repeat components merge. **Symptom:** inflated size, blurred peaks. **Fix:** use `best_k.sh` for the expected size (k=21 at vertebrate ~3 Gb scale; smaller for smaller genomes).

### Contamination/organelle distorting the spectrum
**Trigger:** an unexplained extra peak or a spike at very high multiplicity. **Mechanism:** a second organism's k-mers add their own peak; organelle/high-copy DNA spikes the tail. **Symptom:** GenomeScope size too large or a multi-modal spectrum. **Fix:** KAT spectra triage; screen reads (-> read-qc/quality-reports) before assembling.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| k from best_k.sh (21 at ~3 Gb, 20 at ~1 Gb, 17 at ~12 Mb) | best_k.sh `k=log4(G(1-p)/p)`, p=0.001 | balances uniqueness vs per-k-mer depth; k=21 is the common GenomeScope default at vertebrate scale |
| Homozygous peak >= ~15-20x | GenomeScope model stability | below this the error shoulder and real peak cannot be separated |
| AB peak at ~0.5x the AA peak | diploid k-mer theory | heterozygous k-mers are half-covered (one haplotype); het rate from AB area |
| Smudgeplot CovB/(CovA+CovB): 0.5 / 0.33 / 0.25 | k-mer-pair coverage ratio | AB diploid / AAB triploid / AABB tetraploid |
| Assembly size 1.5-2x GenomeScope estimate | haplotig norm | uncollapsed heterozygous haplotypes; purge before reporting size |
| KMC `-cs`/GenomeScope `-cx` cap ~10000 | histogram tail control | prevents an organelle/repeat spike from dominating the file |
| Smudgeplot L ~0.5x, U ~8.5x haploid peak | Smudgeplot guidance | excludes errors (below) and high-copy repeats (above) from pairing |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| GenomeScope size far larger than expected | k too small, contamination, or organelle spike | raise k via best_k.sh; cap the tail; screen reads |
| Model fit fails / "cannot fit" | too-low coverage or ONT error k-mers | more depth; count from Illumina/HiFi, not noisy ONT |
| Histogram peak at multiplicity ~43 for "50x" data | k-mer coverage = depth * (L-k+1)/L, not depth | expected; do not pass sequencing depth as `-l` |
| GenomeScope `-p 2` fits poorly | sample is not diploid | run Smudgeplot; re-run with the correct `-p` |
| Jellyfish histogram looks halved | counted without `-C` (canonical) | recount with `-C`; WGS is unstranded |
| Assembly 1.8x the profiled size | uncollapsed haplotigs | purge_dups / hifiasm purge; report the haploid size |

## References

- Ranallo-Benavidez TR, Jaron KS, Schatz MC. 2020. GenomeScope 2.0 and Smudgeplot for reference-free profiling of polyploid genomes. *Nat Commun* 11:1432.
- Vurture GW, et al. 2017. GenomeScope: fast reference-free genome profiling from short reads. *Bioinformatics* 33:2202-2204.
- Kokot M, Dlugosz M, Deorowicz S. 2017. KMC 3: counting and manipulating k-mer statistics. *Bioinformatics* 33:2759-2761.
- Marcais G, Kingsford C. 2011. A fast, lock-free approach for efficient parallel counting of occurrences of k-mers (Jellyfish). *Bioinformatics* 27:764-770.
- Rhie A, Walenz BP, Koren S, Phillippy AM. 2020. Merqury: reference-free quality, completeness, and phasing assessment for genome assemblies. *Genome Biol* 21:245.
- Mapleson D, et al. 2017. KAT: a K-mer analysis toolkit to quality control NGS datasets and genome assemblies. *Bioinformatics* 33:574-576.

## Related Skills

- short-read-assembly - High het from the profile predicts short-read fragmentation and haplotig inflation
- hifi-assembly - The profiled size/het sets hifiasm --hom-cov and the purge level
- long-read-assembly - The profiled genome size feeds Flye -g and ONT/PacBio expectations
- assembly-qc - The estimate is the NG50 denominator and the 1.5-2x haplotig sanity check
- read-qc/quality-reports - QC and contamination-screen reads before profiling and assembling
- workflows/genome-assembly-pipeline - Profiling is the first step of the end-to-end assembly workflow
<!-- END FILE: genome-assembly/genome-profiling/SKILL.md -->

## 子目录：genome-assembly/hifi-assembly

<!-- BEGIN FILE: genome-assembly/hifi-assembly/SKILL.md -->
---
name: bio-genome-assembly-hifi-assembly
description: Assembles haplotype-resolved diploid and telomere-to-telomere (T2T) genomes from PacBio HiFi reads with hifiasm (HiFi-only, Hi-C, or trio phasing) and verkko (HiFi + ultralong ONT for T2T), extracting contigs from GFA and routing phasing QC to k-mer/trio metrics. Covers why a primary assembly is a haplotype mosaic that exists in no cell, partial-vs-full phasing (the .bp. vs .dip. filename convention), the purge-default trap on inbred samples, the --hom-cov coverage-estimate alarm, and verkko-vs-hifiasm for T2T. Use when assembling a diploid eukaryote from HiFi, phasing haplotypes with parents (trio) or Hi-C, deciding whether to chase T2T, or diagnosing switch errors invisible to N50/BUSCO/QV.
tool_type: cli
primary_tool: hifiasm
---

## Version Compatibility

Reference examples tested with: hifiasm 0.25.0+, yak 0.1+, verkko 2.3+, gfatools 0.5+, meryl 1.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

hifiasm output filenames AND the default purge level are version-dependent: confirm the `.bp.*`/`.dip.*` prefixes and `-l` defaults against `hifiasm --help` and the man page for the installed build before scripting around them. The k-mer-size convention also matters more than the binary version: hifiasm/yak trio uses k=31; verkko/Merqury hap-mers commonly use k=30 - mixing them silently produces garbage hap-mer matching. If a command errors, introspect the installed tool and adapt rather than retrying.

# HiFi Assembly

**"Assemble a diploid genome from HiFi reads"** -> Build two cleanly phased haplotypes (not one mosaic primary) from accurate long reads, choosing the phasing mechanism from the sample type and available data, and validate phasing with k-mer QC the headline metrics cannot see.
- CLI: `hifiasm -o prefix -t 32 reads.hifi.fq.gz` (HiFi-only), `--h1/--h2` (Hi-C), `-1/-2 *.yak` (trio); `verkko --hifi ... --nano ...` (T2T)

## The Single Most Important Modern Insight -- A Primary Assembly Is a Mosaic Chimera, Not a Haplotype

A "primary assembly" is not a genome that exists in any cell. At every heterozygous block the assembler picks one allele, and which one it picks switches arbitrarily from block to block - so the primary is a stitched chimera: maternal here, paternal there, matching no gamete, no parent, no individual. It is a fine *haploid representation* for "roughly where is gene X" and a terrible substrate for anything allele-aware (phased variant calling, allele-specific expression, HLA/KIR typing, compound-heterozygote analysis). HiFi's combination of length AND ~Q30 accuracy made *phased diploid* assembly routine, so the field's deliverable shifted from one collapsed reference to **two phased haplotypes** (and onward to the **pangenome**: each HPRC node is a per-sample phased diploid assembly, Liao 2023 *Nature* 617:312).

**The killer corollary:** the thing that is wrong with a mosaic - that it is a haplotype mix - is exactly the thing none of the metrics people check can see. A switch error does not break a contig (N50 unchanged), delete a gene (BUSCO unchanged), or introduce a wrong base (QV unchanged - both alleles are real sequence, just assigned to the wrong haplotype). **Switch errors and haplotype mosaicism are structurally invisible to N50, BUSCO, and even base-level QV.** Only k-mer/trio QC - Merqury hap-mer blob plots and switch/hamming error against parental k-mers - can see them. "Reported N50 and BUSCO but no switch/hamming or hap-mer plot" means the phasing was never validated. Subtle trap: the HiFi-only `.bp.hap1/hap2` are *partially* phased (locally phased, switch errors between blocks) - "hap1" in a filename does NOT certify global phasing; the phasing *data* supplied (trio or Hi-C) does.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| hifiasm | Cheng 2021 *Nat Methods* | phased string-graph HiFi assembler; built-in purging | the default for diploid HiFi; HiFi-only / Hi-C / trio / `--ul` |
| hifiasm (Hi-C) | Cheng 2022 *Nat Biotechnol* | global phasing from proximity-ligation, no parents | diploid, Hi-C available, parents unavailable (the broad default) |
| yak | (Li, hifiasm suite) | parental haplotype-specific k-mer DBs for trio | feeds hifiasm `-1/-2`; trio gold-standard phasing |
| verkko | Rautiainen 2023 *Nat Biotechnol* | HiFi + ultralong-ONT graph assembler (MBG -> GraphAligner -> rukki) | T2T-grade; trio or Hi-C phasing; reference-quality |
| verkko2 | Antipov 2025 *Genome Res* | adds proximity-ligation phasing into the De Bruijn graph | T2T with Hi-C; ~doubled T2T-scaffold yield |
| HiCanu | Nurk 2020 *Genome Res* | HiFi Canu fork; segmental dups/satellites/allelic variants | legacy/SD-focused; superseded by hifiasm for routine diploid |
| meryl/Merqury | Rhie 2020 *Genome Biol* | hap-mer DBs; k-mer QV, completeness, switch/hamming, blob plots | the only QC that sees phasing (-> assembly-qc) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Sample type/heterozygosity unknown | profile first: k-mer spectrum (GenomeScope) for genome size + heterozygosity | purge setting, n-hap, and whether to phase are all downstream of outbred-vs-inbred |
| Outbred diploid, HiFi only, quick draft | hifiasm default | primary + partially-phased `.bp.hap1/hap2`; partial phasing is the cost of no linkage data |
| Diploid, HiFi + Hi-C, no parents | hifiasm `--h1/--h2` (Cheng 2022) | global phasing from the sample itself; the pragmatic default for the non-human bestiary |
| Diploid, HiFi + both parents | hifiasm trio `-1 pat.yak -2 mat.yak` | gold standard - read-level phasing, no switch ambiguity where parents are informative |
| Inbred / doubled-haploid / mole | hifiasm `-l0` (purging OFF) | nothing to phase; default purging would DELETE real segmental duplications |
| Unbalanced hap1/hap2 size after a run | re-run with `--hom-cov` set to the k-mer peak | the size imbalance is a mis-estimated coverage alarm, not a phasing result |
| T2T-grade reference, have HiFi + ultralong ONT + trio/Hi-C | verkko (or hifiasm `--ul` for speed) | only graph + UL spanning reaches gapless centromeres; T2T is a project, not a flag |
| No ultralong ONT but want a reference | hifiasm-HiFi-only is the sensible stop | neither tool reaches T2T without UL reads to span repeats |
| One of 50 individuals in a diversity panel | phased diploid (primary may suffice) | do NOT chase T2T per-sample; match grade to question |
| Reads not yet QC'd | -> long-read-sequencing/long-read-qc | HiFi length/QV/contamination cap assembly quality |

## hifiasm Invocations (the fragile commands - run as written)

```bash
# HiFi-only (default): primary mosaic + PARTIALLY-phased hap1/hap2
hifiasm -o prefix -t 32 reads.hifi.fq.gz

# Hi-C phased (no parents) - Cheng 2022; global phasing
hifiasm -o prefix -t 32 --h1 hic_R1.fq.gz --h2 hic_R2.fq.gz reads.hifi.fq.gz

# Trio phased (gold standard) - build parental k-mer DBs first (k=31)
yak count -k31 -b37 -t16 -o pat.yak paternal_R1.fq.gz paternal_R2.fq.gz
yak count -k31 -b37 -t16 -o mat.yak maternal_R1.fq.gz maternal_R2.fq.gz
hifiasm -o prefix -t 32 -1 pat.yak -2 mat.yak reads.hifi.fq.gz

# Inbred / homozygous / mole: DISABLE purging or real duplications are deleted
hifiasm -o prefix -t 32 -l0 reads.hifi.fq.gz

# Unbalanced haplotype sizes: pin the homozygous-coverage peak read off the k-mer histogram
hifiasm -o prefix -t 32 --hom-cov 38 reads.hifi.fq.gz

# Ultralong ONT toward T2T (combine with Hi-C or trio for phasing)
hifiasm -o prefix -t 32 --ul ul_ont.fq.gz reads.hifi.fq.gz
```

**Key flags:** `-l` purge level (`0` none, `1` light, `2`/`3` aggressive; **default 3 in HiFi-only, 0 in trio**); `--h1/--h2` Hi-C R1/R2; `-1/-2` paternal/maternal yak DBs; `--ul` ultralong ONT; `--hom-cov INT` force the homozygous-coverage peak; `--n-hap INT` ploidy (default 2); `--primary` emit primary + alternate (`a_ctg`) instead of dual hap1/hap2.

## Output Filenames: the .bp. vs .dip. Convention (read the prefix, it encodes the mode)

The prefix is not cosmetic - it tells how the assembly was phased:
- **`.bp.` ("balanced phasing") = HiFi-only OR Hi-C mode.** `prefix.bp.p_ctg.gfa` (the mosaic primary), `prefix.bp.hap1.p_ctg.gfa`/`prefix.bp.hap2.p_ctg.gfa` (the two haplotypes - *partially* phased in HiFi-only, *fully* phased with Hi-C). Also `prefix.bp.r_utg.gfa`/`p_utg.gfa` (unitig graphs).
- **`.dip.` ("diploid") = trio mode.** `prefix.dip.hap1.p_ctg.gfa` (paternal/hap1), `prefix.dip.hap2.p_ctg.gfa` (maternal/hap2).
- **`--primary` mode:** `prefix.p_ctg.gfa` (primary) + `prefix.a_ctg.gfa` (alternate). The alternate is incomplete by construction (only heterozygous loci produce alt contigs).
- **Reusable binaries** `prefix.ec.bin`/`ovlp.*.bin` let a re-run with different `-l`/phasing skip error-correction.

People grep `hap1.p_ctg` and are confused when a trio run made `dip.hap1.p_ctg` and a Hi-C run made `bp.hap1.p_ctg`. Verify the actual emitted names against the installed version.

## GFA Is Not FASTA (extract S lines before anything downstream)

hifiasm and verkko emit assembly **graphs** (GFA), and downstream tools want FASTA. Contig sequences live in GFA `S` (segment) lines:

```bash
gfatools gfa2fa prefix.bp.hap1.p_ctg.gfa > hap1.fa          # preferred
awk '/^S/{print ">"$2"\n"$3}' prefix.bp.hap1.p_ctg.gfa > hap1.fa   # dependency-free fallback
```

The graph also carries bubbles/alternate paths the FASTA throws away - keep the GFA. Verkko works internally in homopolymer-compressed coordinates (its `.gfa` is HPC); its final `assembly.fasta` is in normal space.

## verkko (T2T, when the goal genuinely needs it)

T2T is a project, not a flag. Reach for verkko only when T2T completeness is the actual goal AND the data exist (deep HiFi PLUS good ultralong ONT N50 PLUS trio or Hi-C). It is slower, heavier (hundreds of CPU-hours, high RAM, Snakemake-orchestrated), and more fragile than hifiasm. CHM13 - the first T2T human - was a hydatidiform mole precisely because a mole is effectively homozygous, decoupling repeat-resolution from phasing (Nurk 2022 *Science* 376:44).

```bash
# Trio-phased T2T: build parental + CHILD meryl DBs (k=30), derive hap-mers, then run.
# --hap-kmers needs HAP-MER DBs (haplotype-specific k-mers), not raw parental count DBs.
meryl count k=30 paternal.fq.gz output pat.meryl
meryl count k=30 maternal.fq.gz output mat.meryl
meryl count k=30 child.fq.gz    output child.meryl
$MERQURY/trio/hapmers.sh mat.meryl pat.meryl child.meryl   # hapmers.sh takes maternal first; emits mat/pat.hapmer.meryl
verkko -d asm_out --hifi hifi.fq.gz --nano ul_ont.fq.gz \
  --hap-kmers pat.hapmer.meryl mat.hapmer.meryl trio       # paternal first -> haplotype1=paternal (matches hifiasm -1 pat)

# Hi-C-phased (no parents)
verkko -d asm_out --hifi hifi.fq.gz --nano ul_ont.fq.gz --hic1 hic_R1.fq.gz --hic2 hic_R2.fq.gz
```

`--hifi` accurate reads; `--nano` ultralong ONT (the *spanning* data, strongly recommended); `--hap-kmers <hap1> <hap2> trio` (argument ORDER sets which becomes haplotype1/haplotype2 - it is not inferred from biology) or `--hic1/--hic2` for phasing. Outputs `assembly.fasta`, `assembly.haplotype1.fasta`, `assembly.haplotype2.fasta`, `assembly.homopolymer-compressed.gfa`. verkko-vs-hifiasm(`--ul`): verkko closes more chromosomes automatically at higher cost; hifiasm `--ul` brings much of the spanning benefit far cheaper but needs more manual finishing. Neither reaches T2T without ultralong reads.

## Per-Method Failure Modes

### Primary assembly used as if it were a haplotype
**Trigger:** running the primary `.bp.p_ctg`/`p_ctg` into an allele-aware analysis. **Mechanism:** the primary is a per-block haplotype mosaic. **Symptom:** garbage phased variant / ASE / HLA results; "best" metrics. **Fix:** use trio/Hi-C-phased hap1/hap2; never the primary for allele-aware work.

### Partial phasing mistaken for full phasing
**Trigger:** treating HiFi-only `.bp.hap1/hap2` as trio-grade haplotypes. **Mechanism:** no linkage data -> locally phased with inter-block switch errors. **Symptom:** phasing breaks at block boundaries; high switch rate vs trio. **Fix:** add Hi-C (`--h1/--h2`) or trio (`-1/-2`) for global phasing; validate with hap-mers.

### Default purging on an inbred/homozygous sample
**Trigger:** running hifiasm at default `-l3` on an inbred line, doubled-haploid, or mole. **Mechanism:** real segmental duplications/paralogs look like duplicate haplotigs in a homozygous genome and get purged. **Symptom:** assembly shrinks below true genome size; real duplications collapsed. **Fix:** `-l0` (purging off) for low-heterozygosity samples.

### Unbalanced hap1/hap2 size read as biology
**Trigger:** one haplotype much larger than the other. **Mechanism:** hifiasm mis-estimated the homozygous-coverage peak (bimodal coverage, odd ploidy, contamination), so it over-/under-purged. **Symptom:** size ratio far from 1. **Fix:** read the peak off the k-mer/coverage histogram (GenomeScope) and set `--hom-cov`.

### Phasing reported without phasing QC
**Trigger:** N50 + BUSCO + QV reported, no switch/hamming or hap-mer blob plot. **Mechanism:** those metrics are structurally blind to mosaicism. **Symptom:** a "great" assembly that is a phasing disaster. **Fix:** Merqury hap-mer blob plot + switch/hamming vs trio/Hi-C hap-mers (-> assembly-qc). No hap-mers (no trio/Hi-C) = phasing unvalidated by construction.

### verkko recommended reflexively / without ultralong reads
**Trigger:** reaching for verkko (or `--ul`) without ultralong ONT or without a T2T goal. **Mechanism:** UL N50 - not HiFi coverage - is the binding T2T constraint; 60x HiFi cannot span a 3 Mb satellite array. **Symptom:** months of compute, no T2T gain. **Fix:** confirm UL N50 (a meaningful fraction >100 kb) and a real T2T need first; else hifiasm-HiFi-only.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| HiFi coverage >=13x per haplotype; ~30-40x diploid sweet spot | hifiasm FAQ + community | below ~13x/hap het bubbles fragment; past ~40x diminishing returns and worse false-dup |
| HiFi >40x is not free quality | community convention | extra coverage can confuse the `--hom-cov` estimate and inflate false duplications |
| Ultralong ONT N50: the longer the better, meaningful fraction >100 kb (T2T targets >100 kb-1 Mb) | T2T practice | UL value is entirely about *spanning* centromeres/satellites; short "long" reads add little |
| `-l` purge: default 3 (HiFi-only), 0 (trio), set 0 for inbred | hifiasm man page | aggressive purging cleans outbred het-dups but deletes real sequence in homozygous samples |
| k=31 (yak/hifiasm trio) vs k=30 (verkko/Merqury hap-mers) | tool conventions | mixing k silently corrupts hap-mer matching - match each tool |
| Assembly QV: HiFi diploid routinely Q40-Q50; T2T reference ~Q60-Q70+ | Merqury practice | base QV is a SEPARATE axis from phasing accuracy (switch/hamming) |
| Do NOT reflexively polish HiFi | over-polishing risk | HiFi is already ~Q30+ at read level; polishing an accurate assembly often lowers QV (-> assembly-polishing) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Downstream tool rejects hifiasm output | GFA, not FASTA | extract `S` lines (`gfatools gfa2fa` or awk) |
| Assembly below expected genome size, real duplications gone | default purging on an inbred/mole sample | re-run with `-l0` |
| hap1 and hap2 wildly different sizes | mis-estimated homozygous-coverage peak | set `--hom-cov` from the k-mer histogram |
| "hap1" file but phasing breaks across blocks | HiFi-only partial phasing | add Hi-C/trio for global phasing |
| Allele-aware analysis (ASE/phased variants) looks wrong | used the primary mosaic | use phased hap1/hap2, not primary |
| QV drops after polishing the HiFi assembly | over-polishing an already-accurate assembly | stop; HiFi rarely needs short-read polish |
| verkko run never reaches T2T | no/short ultralong ONT | UL N50 is the binding constraint; add long UL or stop at hifiasm |
| Trio run produced `dip.*`, scripts expected `bp.*` | mode encodes the prefix | match filename prefix to phasing mode |

## References

- Cheng H, Concepcion GT, Feng X, Zhang H, Li H. 2021. Haplotype-resolved de novo assembly using phased assembly graphs with hifiasm. *Nat Methods* 18:170-175.
- Cheng H, Jarvis ED, Fedrigo O, et al. 2022. Haplotype-resolved assembly of diploid genomes without parental data. *Nat Biotechnol* 40:1332-1335.
- Nurk S, Walenz BP, Rhie A, et al. 2020. HiCanu: accurate assembly of segmental duplications, satellites, and allelic variants from high-fidelity long reads. *Genome Res* 30:1291-1305.
- Koren S, Rhie A, Walenz BP, et al. 2018. De novo assembly of haplotype-resolved genomes with trio binning. *Nat Biotechnol* 36:1174-1182.
- Rautiainen M, Nurk S, Walenz BP, et al. 2023. Telomere-to-telomere assembly of diploid chromosomes with Verkko. *Nat Biotechnol* 41:1474-1482.
- Antipov D, Rautiainen M, Nurk S, et al. 2025. Verkko2 integrates proximity-ligation data with long-read de Bruijn graphs. *Genome Res* 35:1583-1594.
- Nurk S, Koren S, Rhie A, et al. 2022. The complete sequence of a human genome (T2T-CHM13). *Science* 376:44-53.
- Liao WW, Asri M, Ebler J, et al. 2023. A draft human pangenome reference. *Nature* 617:312-324.
- Rhie A, Walenz BP, Koren S, Phillippy AM. 2020. Merqury: reference-free quality, completeness, and phasing assessment for genome assemblies. *Genome Biol* 21:245.

## Related Skills

- genome-profiling - Decide outbred/inbred/ploidy and the homozygous-coverage peak before setting purge level and `--hom-cov`
- assembly-qc - Merqury hap-mer blob plots and switch/hamming are the only QC that sees phasing
- assembly-polishing - HiFi is already accurate; deciding whether to polish at all
- scaffolding - Hi-C used here for phasing; chromosome-scale scaffolding (YaHS/SALSA2) is the adjacent step
- contamination-detection - Screen contigs for foreign sequence after assembly
- long-read-sequencing/long-read-qc - HiFi read length/QV/contamination before assembly
- workflows/genome-assembly-pipeline - End-to-end profile -> assemble -> phase -> QC -> scaffold
<!-- END FILE: genome-assembly/hifi-assembly/SKILL.md -->

## 子目录：genome-assembly/long-read-assembly

<!-- BEGIN FILE: genome-assembly/long-read-assembly/SKILL.md -->
---
name: bio-genome-assembly-long-read-assembly
description: Assembles genomes de novo from noisy long reads (Oxford Nanopore R9/R10/Dorado, PacBio CLR) with Flye (repeat graph), Canu (correct-trim-assemble OLC), NextDenovo, Shasta, Raven, wtdbg2, or miniasm, and reconciles bacterial assemblies into a consensus with Trycycler/Autocycler. Covers matching the input flag to the basecaller era (--nano-hq vs --nano-raw), why a raw long-read assembly is contiguous but low-QV and not finished until polished, haplotig false-duplication and purge_dups, coverage and read-N50 as non-substitutable inputs, and mid-read adapter de-chimerization. Use when assembling a bacterial or eukaryotic genome from ONT or PacBio noisy reads, choosing a long-read assembler, or diagnosing an over-collapsed or duplicated assembly. For PacBio HiFi use hifi-assembly instead.
tool_type: cli
primary_tool: Flye
---

## Version Compatibility

Reference examples tested with: Flye 2.9+, Canu 2.2+, NextDenovo 2.5+, Shasta 0.11+, Raven 1.8+, wtdbg2 2.5+, miniasm 0.3+, minimap2 2.26+, purge_dups 1.2+, Porechop_ABI 0.5+, Trycycler 0.5+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Two behaviors are version-dependent and load-bearing: Flye `--genome-size` became optional (auto-estimated) and `--scaffold` flipped OFF by default in recent releases - confirm against the installed Flye. Shasta `--config` names are dated and chemistry-specific (e.g. `Nanopore-R10-Fast-Nov2022`) - list with `shasta --command listConfigurations` rather than hard-coding one. Canu read-type flag spellings and `correctedErrorRate` defaults changed across major versions. If a command errors, introspect the installed tool and adapt rather than retrying.

# Long-Read Assembly (Noisy Reads)

**"Assemble a genome from Nanopore/PacBio-CLR long reads"** -> Build a contiguous de novo assembly whose input mode matches the basecaller error regime, then hand off to polishing because the raw consensus is contiguous but not yet accurate.
- CLI: `flye --nano-hq reads.fq.gz --out-dir out -t 16` (modern ONT R10/Dorado), `canu -p asm -d out genomeSize=4.6m -nanopore reads.fq.gz` (thorough), `wtdbg2 -x ont -g 4.6m -i reads.fq.gz -fo asm && wtpoa-cns -i asm.ctg.lay.gz -fo asm.fa` (fast draft)

## The Single Most Important Modern Insight -- The Basecaller Era Picks the Flag, and the Assembly Is Only Half-Done Until Polished

Two load-bearing facts no assembler README states:

1. **The basecaller era dictates the input flag, and a mismatch silently wrecks the assembly while the report looks finished.** Noisy long reads are not one error regime: ONT R9.4.1+Guppy is ~5-10% error, ONT R10.4.1+Dorado SUP is Q20+ (~1-2%), PacBio CLR is ~10-15%. Each assembler has separate modes tuned to each (Flye `--nano-raw` / `--nano-hq` / `--pacbio-raw`). The dangerous direction is **telling the assembler the reads are noisier than they are** - feeding R10/Dorado data to `--nano-raw` makes Flye treat real repeat-copy and allele differences as noise and **over-collapse** them. The result is *fewer contigs and a HIGHER N50* as the assembly gets *worse* - the most dangerous failure mode because the headline metric improved and nothing crashes. The chemistry/kit/basecaller model is an assembly *parameter*, not optional metadata; if it is unknown, the flag cannot be chosen and the assembly is uninterpretable - find out, do not guess.

2. **The bottleneck flipped from contiguity to consensus accuracy.** A raw noisy-long-read assembly emits a FASTA with a spectacular N50 that *looks* finished, but per-base accuracy is often Q20-Q30 (one error every ~100-1000 bp). The dominant ONT error is the **indel**, especially in homopolymers, and a single indel frameshifts a protein - so a contiguous assembly can have every gene model broken. Contiguity and correctness are orthogonal axes; N50 is blind to QV. The assembler is the **halfway point**: the deliverable is a *polished* assembly with a *measured* QV (Merqury), not a high-N50 FASTA. Flye does one internal polishing round and stops - that is not "polished." Hand off to assembly-polishing and assembly-qc.

## Tool Taxonomy

| Tool | Citation | Paradigm | When |
|------|----------|----------|------|
| Flye | Kolmogorov 2019 *Nat Biotechnol* | repeat graph (disjointigs -> explicit repeat structure) | the fast general-purpose default; bacteria -> eukaryote |
| Canu | Koren 2017 *Genome Res* | correct -> trim -> assemble (OLC, MHAP) | maximum single-assembler quality; slow, grid-oriented |
| NextDenovo | Hu 2024 *Genome Biol* | correct (NextCorrect) -> string-graph (NextGraph) | large/repetitive plant and animal genomes; contiguity-first |
| Shasta | Shafin 2020 *Nat Biotechnol* | run-length-encoded marker graph | ONT human-scale, speed/cost critical |
| Raven | Vaser & Sikic 2021 *Nat Comput Sci* | OLC string graph, near parameter-free | fast simple draft; common Trycycler input |
| wtdbg2 | Ruan & Li 2020 *Nat Methods* | fuzzy de Bruijn graph (+ mandatory wtpoa-cns) | fastest, lowest RAM; lowest accuracy -> polish hard |
| miniasm | Li 2016 *Bioinformatics* | string-graph layout, NO consensus | layout demo / pipeline component only; output = raw read error |
| Trycycler / Autocycler | Wick 2021 *Genome Biol* / Wick 2025 | consensus of multiple independent assemblies | bacterial reliability; catches single-assembler structural errors |
| purge_dups | Guan 2020 *Bioinformatics* | read-depth + self-alignment | remove haplotig false-duplication from a diploid primary |

PacBio CLR (`--pacbio-raw`) is legacy - superseded by HiFi for all new PacBio work; treat CLR support as maintenance for archival data, do not recommend generating new CLR.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| ONT R10.4.1 / Dorado HAC-SUP, any genome | Flye `--nano-hq` | modern default mode; matches the Q20+ error regime |
| ONT R9.4.1 SUP (Guppy5+/Dorado) | Flye `--nano-hq --read-error 0.05` | hq mode with the error floor raised to R9-SUP |
| ONT R9.4.1 legacy fast/HAC | Flye `--nano-raw` | the genuinely-noisy mode; do not use on R10 |
| PacBio CLR (archival) | Flye `--pacbio-raw` or Canu `-pacbio` | legacy noisy mode; polish hard (arrow/GCpp) |
| Bacterial isolate, want a *correct* finished genome | Trycycler (interactive) / Autocycler (automated) | consensus across assemblers; fixes structural errors polishing can't |
| Large repetitive plant/animal, contiguity-first | NextDenovo | memory-efficient, top contiguity on big genomes |
| ONT human-scale, speed-critical | Shasta `--config <era-matched>` | RLE marker graph; human genomes in days |
| Quick draft / compute is the bottleneck | wtdbg2 or Raven | fastest; accept lower accuracy then polish |
| PacBio HiFi (Q30+, CCS) | -> hifi-assembly | hifiasm phased haplotypes; wrong tool here |
| After assembling (always) | -> assembly-polishing then assembly-qc | raw consensus is low-QV; not finished until polished + QV-measured |
| Reads not yet QC'd / unknown chemistry | -> long-read-sequencing/long-read-qc, long-read-sequencing/basecalling | garbage-in caps the assembly; basecaller model sets the flag |
| Genome size / coverage unknown | GenomeScope2 on accurate short reads (not raw ONT) | k-mer histograms from noisy reads inflate unique k-mers |

## Flye (the default)

```bash
flye --nano-hq reads.fq.gz --out-dir out -t 16                              # ONT R10 / Dorado SUP
flye --nano-hq reads.fq.gz --read-error 0.05 --out-dir out -t 16            # ONT R9 SUP
flye --nano-raw reads.fq.gz --out-dir out -t 16                             # legacy ONT R9 fast/HAC
flye --pacbio-raw reads.fq.gz --out-dir out -t 16                           # PacBio CLR (legacy)
flye --nano-hq reads.fq.gz --genome-size 3g --asm-coverage 40 -o out -t 32  # large genome: use longest 40x for initial assembly
```

`--genome-size` is optional in recent Flye (auto-estimated) but **required when paired with `--asm-coverage`**, which downsamples to the longest N-coverage of reads for the initial disjointig step (cuts runtime/RAM on deep large-genome data; the rest are still used). `--iterations` defaults to 1 polishing round (`0` to skip); `--keep-haplotypes` retains alt bubble paths for diploid awareness; `--meta` is metaFlye for uneven-coverage communities (-> metagenome-assembly). Output: `assembly.fasta`, `assembly_info.txt` (per-contig length/coverage/circularity), `assembly_graph.gfa`.

## Canu (thorough), wtdbg2 / Raven (fast), miniasm (layout only)

```bash
canu -p asm -d out genomeSize=4.6m -nanopore reads.fq.gz useGrid=false maxThreads=16   # correct->trim->assemble
wtdbg2 -x ont -g 4.6m -t 16 -i reads.fq.gz -fo asm && wtpoa-cns -t 16 -i asm.ctg.lay.gz -fo asm.ctg.fa  # consensus step is MANDATORY
raven -t 16 reads.fq.gz > asm.fasta                                                     # near parameter-free
```

Canu's master meta-parameter is `correctedErrorRate` (max expected difference between two corrected reads): defaults ~0.144 (Nanopore) / ~0.045 (PacBio); raise for heterozygosity/divergence, lower for clean high-coverage data. Read-type flags `-nanopore` / `-pacbio` / `-pacbio-hifi` (there is no `-nanopore-hifi`; high-accuracy ONT still uses `-nanopore`); `useGrid=false` forces a single machine. wtdbg2 needs the separate `wtpoa-cns` consensus call - the `-x` preset (`ont`/`sq`/`rs`/`ccs`) is set FIRST, and `-L` discards short reads (default 5000 for `ont`/`sq`). miniasm does **no consensus at all** - its output carries the full raw read error rate and is unusable until polished, so use it only as a fast layout inside a polished pipeline.

## Haplotig False-Duplication and purge_dups

A diploid assembly from noisy reads either collapses heterozygous loci or emits both haplotypes as separate primary contigs (**haplotig duplication**). The diagnostic trifecta: (1) **assembly size 1.5-2x the expected genome size**; (2) a **bimodal read-depth histogram with a half-coverage peak** (haplotigs split reads between two copies); (3) **inflated BUSCO-Duplicated**. Fix with purge_dups (read-depth + self-alignment):

```bash
minimap2 -xmap-ont asm.fa reads.fq.gz | gzip > aln.paf.gz
pbcstat aln.paf.gz && calcuts PB.stat > cutoffs          # INSPECT the coverage histogram before trusting auto-cuts
split_fa asm.fa > asm.split && minimap2 -xasm5 -DP asm.split asm.split | gzip > self.paf.gz
purge_dups -2 -T cutoffs -c PB.base.cov self.paf.gz > dups.bed
get_seqs -e dups.bed asm.fa                              # -> purged.fa (primary) + hap.fa (haplotigs)
```

purge_dups **cannot tell a haplotig from a real recent segmental duplication/paralog** - both look like similar sequence at fractional depth. On a genome with known recent WGD or high SD content (many plants), over-purging deletes real genes; eyeball the histogram and validate against a related assembly. True haplotype-*resolved* assembly is a HiFi capability - do not promise phasing from noisy reads (-> hifi-assembly).

## Pre-Assembly: Mid-Read Adapter De-Chimerization

```bash
porechop_abi -abi -i reads.fq.gz -o trimmed.fq.gz -t 16   # ab initio adapter detection; SPLITS internal-adapter chimeras
```

ONT occasionally sequences two molecules as one read with an **internal adapter** - an untrimmed chimera becomes a structural mis-join (a layout error polishing cannot fix). Porechop_ABI detects adapters ab initio (no fixed DB, which matters because kit adapter sequences change) and splits chimeric reads. Use it, not the original Porechop (unmaintained since 2018, frozen adapter DB). PacBio CLR handles adapter/scrap removal upstream on the instrument, so this is an ONT-specific concern.

## Per-Method Failure Modes

### Flag noisier than reads actually are
**Trigger:** `--nano-raw` (or low-error-rate omission) on R10/Dorado-SUP data. **Mechanism:** assembler treats real repeat-copy and allele differences as noise and over-collapses. **Symptom:** fewer contigs, HIGHER N50, lost repeats/SVs - looks better. **Fix:** match the flag to the basecaller era (`--nano-hq` for R10); record pore+kit+model before assembling.

### "It assembled, so it's done"
**Trigger:** shipping the raw assembler FASTA on its high N50. **Mechanism:** raw consensus is Q20-Q30; indels frameshift genes. **Symptom:** broken gene models, failed variant calling, BLAST misses present genes. **Fix:** polish (long-read Medaka/Racon, model-matched), then *measure* QV with Merqury; an assembly without a stated QV is a draft.

### Trusting polishing to fix a structural error
**Trigger:** expecting polish to repair a mis-resolved repeat, inversion, collapsed tandem array, or dropped plasmid. **Mechanism:** polishers correct per-base consensus (QV) only; they never change contig layout. **Symptom:** a Q50 assembly that is still structurally wrong. **Fix:** catch layout errors with read-back coverage uniformity, multi-assembler consensus (Trycycler/Autocycler), or Hi-C - not QV.

### Haplotig duplication read as completeness
**Trigger:** "my genome is bigger than expected - more complete!" **Mechanism:** both haplotypes kept as primary contigs. **Symptom:** size 1.5-2x expected, half-coverage depth peak, inflated BUSCO-Duplicated. **Fix:** purge_dups (inspect cutoffs); do not over-purge real SDs.

### High coverage from a short-N50 library
**Trigger:** 200x of reads with a 5 kb N50, expecting contiguity. **Mechanism:** reads physically cannot span long repeats; depth buys consensus, not spanning. **Symptom:** fragmented assembly that more depth never fixes. **Fix:** coverage and read-N50 are non-substitutable; spend effort on read length (extraction, size selection) or ultra-long ONT.

### Over-filtering by length
**Trigger:** aggressive Filtlong/chopper length filter to "keep the best reads." **Mechanism:** the longest reads are often not the highest quality; the filter discards the long-but-lower-Q reads that span hard repeats. **Symptom:** lost contiguity. **Fix:** filter conservatively; spanning reads are precious.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Coverage ~30-60x | field convention (approx) | below ~20-30x consensus too thin (per-base accuracy collapses); beyond ~60x more of the *same* reads adds little contiguity and slows overlap |
| `--asm-coverage 40` with `--genome-size` | Flye usage | downsample to longest 40x for the initial assembly on deep large genomes |
| Canu `correctedErrorRate` ~0.144 ONT / ~0.045 PacBio | Canu 2.2 reference | master knob; raise for heterozygosity, lower for clean high-coverage |
| Assembly size 1.5-2x expected = red flag | diploid norm | haplotig false-duplication; confirm with half-coverage peak + BUSCO-Duplicated -> purge_dups |
| Merqury QV40 (~1 error/10 kb), Q50 reference-grade | Rhie 2020 *Genome Biol* | the QV stop signal; report it, never an N50 alone |
| R9 raw ~Q15-17, R10 simplex Q20+, duplex Q30+ | Wick-blog / ONT (approx) | sets the input flag and whether short-read polishing is even needed |
| wtdbg2 `-x ont` `-L` default 5000 | wtdbg2 preset | silently discards reads shorter than 5 kb |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Fewer contigs, higher N50, but lost variation | `--nano-raw` on R10/Dorado data (over-collapse) | use `--nano-hq`; match the basecaller era |
| Gene prediction frameshifts everywhere | unpolished low-QV assembly | polish then measure QV (Merqury); -> assembly-polishing |
| Assembly ~2x expected size, BUSCO-Duplicated high | uncollapsed haplotigs | purge_dups; inspect coverage cutoffs first |
| wtdbg2 output is empty/short | forgot the `wtpoa-cns` consensus step | run `wtpoa-cns` on `.ctg.lay.gz` |
| miniasm assembly full of errors | miniasm does no consensus | polish (Racon/Medaka) or use a consensus assembler |
| Chimeric contigs / structural mis-joins | internal-adapter chimeric reads | de-chimerize with Porechop_ABI before assembly |
| Canu runs for days, huge RAM | normal for the correction stage on large genomes | `useGrid=true` on a cluster, or use Flye |

## References

- Kolmogorov M, Yuan J, Lin Y, Pevzner PA. 2019. Assembly of long, error-prone reads using repeat graphs (Flye). *Nat Biotechnol* 37:540-546.
- Koren S, Walenz BP, Berlin K, Miller JR, Bergman NH, Phillippy AM. 2017. Canu: scalable and accurate long-read assembly via adaptive k-mer weighting and repeat separation. *Genome Res* 27:722-736.
- Hu J, Wang Z, Sun Z, et al. 2024. NextDenovo: an efficient error correction and accurate assembly tool for noisy long reads. *Genome Biol* 25:107.
- Shafin K, Pesout T, Lorig-Roach R, et al. 2020. Nanopore sequencing and the Shasta toolkit enable efficient de novo assembly of eleven human genomes. *Nat Biotechnol* 38:1044-1053.
- Vaser R, Sikic M. 2021. Time- and memory-efficient genome assembly with Raven. *Nat Comput Sci* 1:332-336.
- Ruan J, Li H. 2020. Fast and accurate long-read assembly with wtdbg2. *Nat Methods* 17:155-158.
- Li H. 2016. Minimap and miniasm: fast mapping and de novo assembly for noisy long sequences. *Bioinformatics* 32:2103-2110.
- Guan D, McCarthy SA, Wood J, Howe K, Wang Y, Durbin R. 2020. Identifying and removing haplotypic duplication in primary genome assemblies (purge_dups). *Bioinformatics* 36:2896-2898.
- Wick RR, Judd LM, Cerdeira LT, et al. 2021. Trycycler: consensus long-read assemblies for bacterial genomes. *Genome Biol* 22:266.
- Rhie A, Walenz BP, Koren S, Phillippy AM. 2020. Merqury: reference-free quality, completeness, and phasing assessment for genome assemblies. *Genome Biol* 21:245.

## Related Skills

- genome-profiling - k-mer genome-size estimate feeds Flye `--genome-size` and the haplotig sanity check
- hifi-assembly - PacBio HiFi (Q30+) phased haplotype-resolved assembly with hifiasm; the right tool for accurate reads
- assembly-polishing - Polishes the contiguous-but-low-QV contigs this skill produces; assembly is not finished without it
- assembly-qc - QUAST/BUSCO/Merqury; QV is the deliverable, N50 alone is a vanity metric
- long-read-sequencing/long-read-qc - Read length/quality QC and conservative filtering before assembly
- long-read-sequencing/basecalling - Basecaller era and model that determine the assembler input flag
- read-qc/contamination-screening - Screen reads for host/vector contamination before assembling
- workflows/genome-assembly-pipeline - End-to-end QC -> assemble -> polish -> scaffold -> QC
<!-- END FILE: genome-assembly/long-read-assembly/SKILL.md -->

## 子目录：genome-assembly/metagenome-assembly

<!-- BEGIN FILE: genome-assembly/metagenome-assembly/SKILL.md -->
---
name: bio-genome-assembly-metagenome-assembly
description: Assembles microbial-community sequencing into metagenome-assembled genomes (MAGs) with metaFlye (ONT), metaSPAdes/MEGAHIT (Illumina), and hifiasm-meta/metaMDBG (PacBio HiFi), then recovers genomes via multi-binner consolidation (MetaBAT2, MaxBin2, CONCOCT, SemiBin2, VAMB -> DAS_Tool) and QCs them against MIMAG with CheckM2, GUNC, and GTDB-Tk. Covers why a metagenome is not a genome (uneven coverage, micro-diversity, strain collapse to consensus), differential-coverage binning, co-assembly vs per-sample, the rRNA-operon collapse that fails short-read MAGs, and strain resolution with inStrain. Use when reconstructing genomes from a microbiome, soil, ocean, or gut community, recovering MAGs, or resolving strain-level variation.
tool_type: cli
primary_tool: metaFlye
---

## Version Compatibility

Reference examples tested with: Flye 2.9+, SPAdes 3.15+ (metaSPAdes), MEGAHIT 1.2+, hifiasm-meta 0.3+, metaMDBG 1.0+, MetaBAT2 2.15+, MaxBin 2.2.7+, CONCOCT 1.1+, SemiBin 2.0+, VAMB 4.1+, DAS_Tool 1.1.6+, CheckM2 1.0+, GUNC 1.0+, GTDB-Tk 2.4+, inStrain 1.7+, minimap2 2.26+, samtools 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

GTDB-Tk results track the reference-package RELEASE (e.g. R214 vs R220); the DB release MUST match the GTDB-Tk binary or classification silently fails. CheckM2 and GUNC each download their own DIAMOND DB. SemiBin2's pretrained `--environment` models are versioned. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Metagenome Assembly

**"Assemble genomes from my metagenome"** -> Co-assemble a community at uneven, strain-mixed coverage, then bin the contigs into a set of consensus population genomes (MAGs) and QC each against MIMAG. The deliverable is MAGs, not a single assembly.
- CLI: `flye --meta --nano-hq reads.fq` (ONT), `spades.py --meta -1 R1.fq -2 R2.fq` or `megahit -1 R1.fq -2 R2.fq` (Illumina), `hifiasm_meta`/`metaMDBG` (HiFi); then binners -> `DAS_Tool` -> `checkm2 predict` + `gunc run` + `gtdbtk classify_wf`

## The Single Most Important Modern Insight -- A Metagenome Is Not a Genome; the Assembler Cannot Assume Uniform Coverage

Every isolate assembler is built on the premise that the true sequence sits at roughly one depth, so a coverage drop or spike signals a repeat or an error. In a community that premise is false by construction: an abundant species at 500x and a rare one at 3x are both real. Running plain SPAdes/Unicycler or single-genome Flye on a community treats the abundance spread and strain bubbles as errors to "fix" and produces garbage. Use `--meta` modes. Three consequences cascade:

1. **A MAG is a population consensus, not an organism's genome.** Co-occurring strains differing by <1% ANI become bubbles the assembler collapses into one consensus path -- a sequence that may match no actual cell in the sample. A 99%-complete circular MAG is still the consensus of the dominant strain; minority-strain accessory genome is averaged away. Treat every per-strain, per-allele, or pangenome claim from a single consensus MAG as suspect until read-level microdiversity (inStrain) or strain-aware assembly confirms it.
2. **The deliverable is a community of MAGs, not one assembly -- a community has no N50.** N50 is dominated by whichever few abundant genomes assembled well and says nothing about the community; a "better N50" assembly can have recovered fewer genomes. Report MAG count split by MIMAG tier (HQ/medium/low) and community fraction binned. Bigger total assembly size is not better -- it can mean more chimeras and strain-fragmentation.
3. **Modern practice is multi-binner -> consolidate -> CheckM2 + GUNC -> GTDB-Tk.** Never trust one binner; run several (each weights composition vs coverage differently and recovers a partially-different genome set), reconcile with DAS_Tool, then QC every bin with CheckM2 AND GUNC (completeness lies about chimeras) before classifying against the MIMAG 90%/5% bar. HiFi/long reads are the single biggest quality jump: they span the conserved rRNA operons and strain bubbles short reads shred, yielding complete, circular, genuinely-HQ MAGs.

## Assembler Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| metaFlye | Kolmogorov 2020 *Nat Methods* | repeat-graph long-read meta-assembler (`--meta` mandatory) | ONT/CLR community de novo; polish after |
| metaSPAdes | Nurk 2017 *Genome Res* | strain-aware multi-k de Bruijn (`spades.py --meta`) | Illumina, contiguity priority; ONE paired library only |
| MEGAHIT | Li 2015 *Bioinformatics* | succinct de Bruijn, low-memory | huge/complex Illumina co-assemblies, soil; lower contiguity |
| hifiasm-meta | Feng 2022 *Nat Methods* | strain-resolved HiFi string graph | PacBio HiFi communities; keeps strains apart |
| metaMDBG | Benoit 2024 *Nat Biotechnol* | minimizer de Bruijn for HiFi | HiFi; often ~2x the HQ circular MAGs, low RAM |
| OPERA-MS | Bertrand 2019 *Nat Biotechnol* | short-read meta scaffolded by long reads | hybrid short + long |

## Binner Taxonomy

| Binner | Citation | Signal | When |
|--------|----------|--------|------|
| MetaBAT2 | Kang 2019 *PeerJ* | tetranucleotide freq (TNF) + coverage, parameter-free | fast default workhorse (`-m 1500`) |
| MaxBin2 | Wu 2016 *Bioinformatics* | EM over TNF + marker genes + coverage | single/few samples |
| CONCOCT | Alneberg 2014 *Nat Methods* | GMM on composition+coverage of cut-up contigs | many samples; 4-step pipeline, not one command |
| SemiBin2 | Pan 2023 *Bioinformatics* | self-supervised contrastive deep learning | current SOTA; short + long; pretrained env models |
| VAMB | Nissen 2021 *Nat Biotechnol* | variational autoencoder of coabundance + k-mer | multi-sample; separates close strains |
| DAS_Tool | Sieber 2018 *Nat Microbiol* | dereplicate-aggregate-score across binners (consolidation) | ALWAYS run; non-redundant set beats any single binner |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Illumina, complex/huge/soil, low RAM | MEGAHIT `--presets meta-sensitive` | succinct dBG fits in memory; multi-library |
| Illumina, contiguity priority, tractable size | metaSPAdes (`spades.py --meta`) | strain-aware repeat resolution; merge libraries first (one paired lib only) |
| ONT-only community | metaFlye `--meta --nano-hq` -> polish | repeat-graph meta mode; ONT needs polishing -> assembly-polishing |
| PacBio HiFi community | hifiasm-meta or metaMDBG | complete circular strain-resolved MAGs; fixes rRNA collapse |
| Hybrid short + long | OPERA-MS | short-read meta scaffolded with long reads |
| Recover MAGs (any assembly) | >=2-3 binners -> DAS_Tool -> CheckM2 + GUNC -> GTDB-Tk | ensemble beats one binner; chimera + taxonomy gates |
| Only ONE sample | composition-only binning, expect weak bins | differential coverage needs multiple samples; add samples, not tuning |
| Multiple samples available | map ALL samples to each assembly for binning depth | differential-coverage is the strongest binning signal |
| Strain-level question | -> inStrain on reads mapped to MAGs | consensus MAGs blur strains; needs read-level microdiversity |
| Read-based taxonomy / rare biosphere | -> metagenomics/kraken-classification | assembly is blind below the abundance-detection limit |
| Reads not QC'd / host-contaminated | -> long-read-sequencing/long-read-qc | remove host reads vs a T2T reference before assembly |
| MAG contamination forensics | -> contamination-detection | detailed CheckM2/GUNC interpretation |

## metaFlye (ONT / Long Reads)

```bash
flye --meta --nano-hq ont.fastq.gz --out-dir flye_out -t 32
#   --meta        uneven-coverage metagenome mode (REQUIRED for communities)
#   read-type flag (mutually exclusive): --nano-hq (Guppy5+/Q20) | --nano-raw (older) |
#       --pacbio-hifi | --pacbio-raw (CLR)
# outputs: assembly.fasta, assembly_graph.gfa, assembly_info.txt (circularity flag in col 'circ.')
```
ONT contigs are contiguous but error-prone (indels in homopolymers); polish before downstream use (-> assembly-polishing; medaka needs the matching basecaller model). HiFi usually needs no polishing.

## metaSPAdes / MEGAHIT (Illumina)

```bash
# metaSPAdes -- contiguity priority; exactly ONE paired library
spades.py --meta -1 R1.fastq.gz -2 R2.fastq.gz -o spades_out -t 32 -m 500
#   -m memory cap in GB (SPAdes aborts if exceeded); -k auto by default
# outputs: contigs.fasta, scaffolds.fasta

# MEGAHIT -- huge/low-RAM; accepts comma-separated multiple libraries
megahit -1 a1.fq.gz,b1.fq.gz -2 a2.fq.gz,b2.fq.gz -o megahit_out -t 32 \
        --presets meta-sensitive --min-contig-len 1000
#   --presets meta-sensitive | meta-large (huge complex); raise --min-contig-len to ~1000 for binning
```
metaSPAdes `--meta` supports exactly ONE paired-end library -- a real constraint people miss; concatenate libraries first or use MEGAHIT for many. metaSPAdes is heavier on RAM/time and chokes on soil-scale co-assembly; MEGAHIT assembled a 252 Gbp soil set on one node at the cost of somewhat more fragmentation.

## HiFi (the transformative case)

```bash
hifiasm_meta -t 32 -o asm hifi.fastq.gz
awk '/^S/{print ">"$2"\n"$3}' asm.p_ctg.gfa > asm.p_ctg.fa   # GFA -> FASTA

metaMDBG asm --out-dir mdbg_out --in-hifi hifi.fastq.gz --threads 32   # often ~2x HQ circular MAGs
```

## Coverage for Binning, then Bin

```bash
# Map reads back to the assembly -- per sample for differential coverage
minimap2 -ax map-ont -t 32 contigs.fa reads.fq.gz | samtools sort -@ 32 -o s1.sorted.bam -
samtools index s1.sorted.bam
jgi_summarize_bam_contig_depths --outputDepth depth.txt s1.sorted.bam s2.sorted.bam   # all samples

metabat2 -i contigs.fa -a depth.txt -o metabat/bin -m 1500 -t 32   # -m 1500 = min contig (do not go below ~1000)
run_MaxBin.pl -contig contigs.fa -abund abund1.txt -out maxbin/bin -thread 32 -min_contig_length 1000
SemiBin2 single_easy_bin -i contigs.fa -b s1.sorted.bam -o semibin_out   # add --environment human_gut for a pretrained model
```
CONCOCT is a 4-step pipeline (`cut_up_fasta.py` -> `concoct_coverage_table.py` -> `concoct` -> `merge_cutup_clustering.py` -> `extract_fasta_bins.py`), not one command. Differential-coverage binning needs MULTIPLE samples with abundance variation; with one sample binning collapses to weak composition-only signal -- more samples, not more tuning.

## Consolidate (DAS_Tool), then QC

```bash
# Convert each binner's output to contig2bin tables, then aggregate-and-score
Fasta_to_Contig2Bin.sh -i metabat/ -e fa    > metabat.tsv
Fasta_to_Contig2Bin.sh -i maxbin/  -e fasta > maxbin.tsv               # MaxBin emits .fasta
gunzip -k semibin_out/output_bins/*.gz 2>/dev/null || true             # SemiBin2 bins are gzipped
Fasta_to_Contig2Bin.sh -i semibin_out/output_bins/ -e fa > semibin.tsv
DAS_Tool -i metabat.tsv,maxbin.tsv,semibin.tsv -l metabat,maxbin,semibin \
         -c contigs.fa -o dastool/DAS --write_bins -t 32
# DAS_Tool assumes the SAME contig set across binners -- feeding bins from different assemblies is a silent error

checkm2 predict --input dastool/DAS_DASTool_bins/ -x fa --output-directory checkm2_out -t 32
gunc run --input_dir dastool/DAS_DASTool_bins/ --file_suffix .fa --out_dir gunc_out --threads 32
gtdbtk classify_wf --genome_dir dastool/DAS_DASTool_bins/ -x fa --out_dir gtdbtk_out --cpus 32
```
Run CheckM2 AND GUNC: CheckM2 counts marker copy number (completeness/contamination), GUNC tests whether a genome's genes share one lineage (chimerism). A bin made of two half-genomes can score high completeness, low contamination, and still be a chimera -- GUNC is the orthogonal catch. Dereplicate MAGs across samples (dRep ~95% ANI species, ~99% strain) before reporting counts.

## Strain Resolution

```bash
# Consensus MAGs blur strains; recover read-level microdiversity
inStrain profile sample.sorted.bam mags.fa -o instrain_out -p 16 -g genes.fna
inStrain compare -i instrain_A instrain_B -o instrain_compare   # popANI: shared-strain detection across samples
```

## Per-Method Failure Modes

### Isolate assembler on a community
**Trigger:** plain `spades.py`/`flye` (no `--meta`) on community reads. **Mechanism:** uniform-coverage assumption deletes rare-taxon contigs and mis-resolves strain bubbles as errors. **Symptom:** few short contigs, missing abundant taxa. **Fix:** `--meta` mode for every meta-assembler.

### Single-binner pipeline
**Trigger:** "we used SemiBin2 because it's SOTA," one binner. **Mechanism:** each binner recovers a partially-different genome set. **Symptom:** real MAGs left on the table; lower count than peers. **Fix:** run >=2-3 binners -> DAS_Tool consolidation.

### Single-sample differential-coverage expectation
**Trigger:** MetaBAT2/CONCOCT on one sample, surprised bins are bad. **Mechanism:** one coverage value -> composition (TNF) only, which is weak (related genera share TNF). **Symptom:** poor, split bins. **Fix:** more samples with abundance variation, then map all back; do not retune.

### Short-read MAG reported HQ on 90/5 alone
**Trigger:** calling a 95%-complete/2%-contam short-read MAG "high-quality." **Mechanism:** conserved + multi-copy rRNA operon tangles the short-read graph and stays unbinned. **Symptom:** MAG fails MIMAG HQ for missing 16S/23S/5S despite great completeness. **Fix:** check the FULL MIMAG HQ definition (rRNA + tRNA); use HiFi/long reads to span the operon.

### High CheckM2 completeness read as quality
**Trigger:** trusting completeness/contamination alone. **Mechanism:** non-overlapping markers from two half-genomes score high completeness, low contamination. **Symptom:** "clean" MAG that is a chimera. **Fix:** always pair CheckM2 with GUNC -> contamination-detection.

### Strain claims from a consensus MAG
**Trigger:** per-allele/per-strain interpretation of one MAG. **Mechanism:** the assembler collapsed strains to consensus. **Symptom:** strain findings that read-level data contradict. **Fix:** inStrain popANI or strain-aware (hifiasm-meta) assembly.

### Reading MAG richness as community richness
**Trigger:** "200 MAGs cover 60% of reads" treated as the whole community. **Mechanism:** the rare biosphere never crosses the assembly detection limit. **Symptom:** species richness massively undercounted. **Fix:** complement with read-based profiling -> metagenomics/kraken-classification.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| MIMAG high-quality: completeness >90%, contamination <5%, AND 16S/23S/5S rRNA + >=18 tRNAs | Bowers 2017 *Nat Biotechnol* | rRNA criterion is the silent killer; short-read MAGs fail it |
| MIMAG medium-quality: completeness >=50%, contamination <10% | Bowers 2017 | most short-read MAGs land here |
| Min contig length for binning ~1000-1500 bp | MetaBAT2 default 1500 | shorter contigs have unreliable TNF/coverage -> noise/chimeras |
| Differential-coverage binning needs N >= ~3-5 samples with abundance variation | binning practice | one coverage value cannot separate co-abundant genomes |
| Assembly detection limit ~3-5x coverage | de Bruijn requirement | below this the rare biosphere does not assemble at all |
| MAG dereplication 95% ANI (species), 99% (strain) | dRep/ANI convention | collapse redundant per-sample MAGs before counting |
| metaSPAdes input: exactly ONE paired library | `--meta` constraint | merge libraries or use MEGAHIT for many |
| N50 / contiguity | not a community metric | report MAG count + MIMAG tiers instead |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Few short contigs, missing abundant taxa | isolate mode on a community | add `--meta` |
| metaSPAdes rejects multiple libraries | `--meta` supports one paired library | concatenate, or use MEGAHIT |
| metaSPAdes aborts / out of memory | RAM cap hit on a complex co-assembly | raise `-m`, or switch to MEGAHIT |
| Poor bins from one sample | no differential-coverage signal | add samples; map all back for depth |
| "HQ MAG" lacks rRNA | rRNA-operon collapse in short reads | full MIMAG check; HiFi/long reads |
| Clean CheckM2 but suspect bin | chimera invisible to marker counts | run GUNC alongside CheckM2 |
| GTDB-Tk classify_wf errors | DB release != binary version | match the GTDB reference-package release |
| Strain finding not reproducible | consensus MAG blurs strains | inStrain popANI / strain-aware assembly |

## References

- Nurk S, Meleshko D, Korobeynikov A, Pevzner PA. 2017. metaSPAdes: a new versatile metagenomic assembler. *Genome Res* 27:824-834.
- Li D, Liu CM, Luo R, Sadakane K, Lam TW. 2015. MEGAHIT: an ultra-fast single-node solution for large and complex metagenomics assembly via succinct de Bruijn graph. *Bioinformatics* 31:1674-1676.
- Kolmogorov M, et al. 2020. metaFlye: scalable long-read metagenome assembly using repeat graphs. *Nat Methods* 17:1103-1110.
- Feng X, Cheng H, Portik D, Li H. 2022. Metagenome assembly of high-fidelity long reads with hifiasm-meta. *Nat Methods* 19:671-674.
- Benoit G, et al. 2024. High-quality metagenome assembly from long accurate reads with metaMDBG. *Nat Biotechnol* 42:1378-1383.
- Bertrand D, et al. 2019. Hybrid metagenomic assembly enables high-resolution analysis of resistance determinants and mobile elements in human microbiomes (OPERA-MS). *Nat Biotechnol* 37:937-944.
- Kang DD, et al. 2019. MetaBAT 2: an adaptive binning algorithm for robust and efficient genome reconstruction from metagenome assemblies. *PeerJ* 7:e7359.
- Wu YW, Simmons BA, Singer SW. 2016. MaxBin 2.0: an automated binning algorithm to recover genomes from multiple metagenomic datasets. *Bioinformatics* 32:605-607.
- Alneberg J, et al. 2014. Binning metagenomic contigs by coverage and composition (CONCOCT). *Nat Methods* 11:1144-1146.
- Pan S, Zhao XM, Coelho LP. 2023. SemiBin2: self-supervised contrastive learning leads to better MAGs for short- and long-read sequencing. *Bioinformatics* 39:i21-i29.
- Nissen JN, et al. 2021. Improved metagenome binning and assembly using deep variational autoencoders (VAMB). *Nat Biotechnol* 39:555-560.
- Sieber CMK, et al. 2018. Recovery of genomes from metagenomes via a dereplication, aggregation and scoring strategy (DAS_Tool). *Nat Microbiol* 3:836-843.
- Chklovski A, et al. 2023. CheckM2: a rapid, scalable and accurate tool for assessing microbial genome quality using machine learning. *Nat Methods* 20:1203-1212.
- Orakov A, et al. 2021. GUNC: detection of chimerism and contamination in prokaryotic genomes. *Genome Biol* 22:178.
- Chaumeil PA, Mussig AJ, Hugenholtz P, Parks DH. 2020. GTDB-Tk: a toolkit to classify genomes with the Genome Taxonomy Database. *Bioinformatics* 36:1925-1927.
- Bowers RM, et al. 2017. Minimum information about a single amplified genome (MISAG) and a metagenome-assembled genome (MIMAG) of bacteria and archaea. *Nat Biotechnol* 35:725-731.
- Olm MR, et al. 2021. inStrain profiles population microdiversity from metagenomic data and sensitively detects shared microbial strains. *Nat Biotechnol* 39:727-736.

## Related Skills

- contamination-detection - CheckM2/GUNC interpretation and chimerism forensics for MAGs
- assembly-qc - Isolate-assembly QC; the uniform-coverage assumption metagenomes abandon
- assembly-polishing - Polish ONT/CLR meta-contigs before binning (HiFi usually needs none)
- metagenomics/kraken-classification - Read-based taxonomy; recovers the rare biosphere assembly cannot
- metagenomics/abundance-estimation - Community abundance downstream of recovered MAGs
- metagenomics/functional-profiling - Functional potential complementary to genome recovery
- long-read-sequencing/long-read-qc - Read-level QC and host removal before assembly
<!-- END FILE: genome-assembly/metagenome-assembly/SKILL.md -->

## 子目录：genome-assembly/scaffolding

<!-- BEGIN FILE: genome-assembly/scaffolding/SKILL.md -->
---
name: bio-genome-assembly-scaffolding
description: Orders and orients assembled contigs into chromosome-scale scaffolds from long-range linking data, inserting N-gap spacers (adds no sequence). Covers Hi-C/Omni-C scaffolding (YaHS, SALSA2, 3D-DNA/Juicer), Hi-C read-mapping prerequisites (map each end separately, no mate rescue, dedup, enzyme-aware), reading the contact map for misjoins/inversions/false-duplications, manual curation in Juicebox/PretextView (the VGP/DToL standard), reference-guided scaffolding (RagTag) and its karyotype-erasure hazard, genetic-map (ALLMAPS) and Bionano optical-map integration, chimera-breaking before scaffolding, gap-filling, and telomere/contig-vs-scaffold-N50 QC (tidk). Use when turning contigs into chromosomes with Hi-C, integrating a linkage map or optical map, choosing a scaffolder by available linking data, or judging whether a chromosome-scale assembly is trustworthy.
tool_type: cli
primary_tool: YaHS
---

## Version Compatibility

Reference examples tested with: YaHS 1.2+, SALSA2 2.3+, juicer_tools 1.22/2.0+, bwa 0.7.17+, chromap 0.2+, samtools 1.19+, RagTag 2.1+, tidk 0.2.3+, seqkit 2.6+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

hifiasm output filenames and YaHS/SALSA2 enzyme and resolution defaults have changed across releases; confirm output names and `-e`/`-r` behaviour against the installed version. The Hi-C-mapping flag set (`bwa mem -5SP` vs the Arima/VGP per-end pipeline) varies by vendor (Arima, Dovetail/Omni-C, Phase Genomics) - check the current mapping guide before pasting flags. If a command errors, introspect the tool and adapt rather than retrying.

# Genome Scaffolding

**"Turn my contigs into chromosomes"** -> Order and orient contigs by long-range linking signal, insert N-gap spacers, then curate the contact map - scaffolding adds no sequence, so the output is a draft chromosome structure, not finished sequence.
- CLI: `yahs contigs.fa hic_to_contigs.bam` (Hi-C default), `run_pipeline.py -a contigs.fa -b sorted.bed -m yes` (SALSA2), `ragtag.py scaffold ref.fa contigs.fa` (reference-guided), `allmaps path` (linkage maps)

## The Single Most Important Modern Insight -- Automated Scaffolding Produces a Draft; the Genome Is Trustworthy Only After Manual Curation of the Contact Map

YaHS finishes in minutes and emits a file literally named `_scaffolds_final.agp`. It is **not final**. Hi-C scaffolding is a contact-frequency *inference* - it orders/orients contigs by the polymer-physics signal that contact frequency decays with 1D distance - and it is error-prone exactly at the joins. Every reference-grade pipeline (VGP, Darwin Tree of Life, Earth BioGenome) treats the automated AGP as a *first pass* that a human curator then corrects in PretextView or Juicebox: breaking misjoins, flipping inversions, removing false duplications, assigning chromosomes by eye. Howe 2021 quantified the hidden labor across 111 VGP/DToL assemblies: on average **221 interventions per Gb (67 breaks, 105 joins, 49 false-duplication removals)**. Three load-bearing consequences:

1. **The contact map is the QC, not a decoration.** A correct chromosome shows one bright diagonal with smooth off-diagonal decay; off-diagonal blocks, anti-diagonal "bowties," and bleeding between chromosomes are errors to inspect and break (see Reading the Contact Map). An assembly paper whose methods say "scaffolded with [tool]" but never mention curation/Juicebox/PretextView is shipping a draft - downgrade any claim that depends on large-scale order (synteny, fusions, structural variants).

2. **Scaffold N50 is not contig N50, and conflating them is the classic reviewer catch.** Scaffolding inserts runs of **N** (estimated, often arbitrary length) and adds zero sequence. A genome can post "scaffold N50 = 60 Mb, chromosome-scale!" while its contig N50 is 200 kb - the contiguity is borne by gaps, not finished sequence. Always report contig N50, scaffold N50, gap count, and total N bases separately.

3. **Reordering cannot rescue a bad contig.** Scaffolders take contigs as given; a chimeric contig drags the wrong sequence into the wrong chromosome. Chimeras must be **broken before scaffolding** (see Chimera-Breaking).

## Linking-Data Modality Taxonomy

| Modality | How it links | Scale | Status |
|----------|--------------|-------|--------|
| Hi-C / Omni-C | proximity ligation; contact frequency ~ 1/(1D distance) | chromosome-scale | Dominant modern method. Omni-C is enzyme-free/sequence-agnostic; Arima uses fixed enzyme motifs |
| Bionano optical maps (DLS) | labeled motif patterns aligned to in-silico contig maps | megabase | Resolves large SVs and bridges complex repeats; separate instrument + library (cost decision) |
| 10x linked reads | barcoded short reads from one long molecule | ~10-100 kb | DISCONTINUED by 10x (2020). Legacy data only; Tigmint/ARCS still run, no new data |
| Genetic / linkage maps | marker recombination order = chromosome order | chromosome-scale, low resolution | ALLMAPS integrates multiple maps; orthogonal validation of Hi-C |
| Reference (homology) | align contigs to a related genome, copy its order | as good as synteny | RagTag. Fast, but imposes the reference's karyotype - see hazard below |
| Long reads as linkers | k-mer pairs spanning junctions | read length | LINKS; mostly superseded by assembling with the long reads directly |
| Mate-pair / jumping | large-insert paired short reads | 2-40 kb | Legacy (SSPACE); chimeric-insert artifacts; never recommend today |

## Decision Tree by Available Linking Data

| Available linking data | Use | Why |
|-------------|-----|-----|
| Hi-C/Omni-C, want fast contiguous default | YaHS | community default; fast, high N90, AGP + Juicebox outputs in one command |
| Hi-C, want graph-aware conservative joins + input-error correction | SALSA2 `-m yes` (`-g graph.gfa`) | iterative; breaks chimeric input; uses assembly graph to avoid orientation errors |
| Hi-C, interactive curation central to workflow | 3D-DNA + Juicer + Juicebox (JBAT) | the Aiden-lab `.assembly` <-> Juicebox round-trip is built around hand-editing |
| Hi-C, vertebrate/reference-grade | YaHS or SALSA2 -> PretextView/JBAT curation | VGP/DToL standard: automate then curate |
| Diploid, Hi-C, want both haplotypes as chromosomes | hifiasm `--h1/--h2` to PHASE first, then YaHS to SCAFFOLD each haplotype | same Hi-C, two jobs - phasing picks the homolog, scaffolding orders along it (see Phasing vs Scaffolding) |
| Closely related reference, karyotype NOT a question | RagTag `correct` then `scaffold` | homology ordering in minutes - but never if karyotype is the biology |
| One or more genetic/linkage maps | ALLMAPS | integrates multiple maps; robust to marker errors; validates/anchors Hi-C |
| Bionano optical maps + sequence assembly | Bionano Solve hybrid scaffold (before Hi-C) | megabase maps bridge complex repeats and large SVs |
| 10x linked reads (legacy data) | Tigmint (break) -> ARCS/ARKS (link) | break misassemblies first; no new 10x data exists |
| Contigs not yet QC'd / haplotigs present | -> assembly-qc, purge_dups | scaffolding haplotigs strings them up as fake chromosomes |
| Hi-C contact map for TADs/loops, not chromosomes | -> hi-c-analysis/matrix-operations | different use of the same assay |

**Modern reference-grade recipe (vertebrate/eukaryote):** HiFi -> hifiasm contigs -> (optional Bionano hybrid scaffold) -> Hi-C scaffold (YaHS/SALSA2) -> **manual curation in PretextView/JBAT** -> gap-fill (TGS-GapCloser) -> QC (tidk telomeres, contact-map diagonal, contig-vs-scaffold N50).

## Hi-C Read Mapping (the step people botch)

Hi-C reads are **not** a normal paired-end library: the two ends come from *different* genomic loci ligated together, so standard PE proper-pair/insert-size logic mis-handles them.

```bash
# Map each end SEPARATELY with no mate rescue/pairing; -5 reports the 5' (junction) portion as primary.
bwa index contigs.fa
bwa mem -5SP -T0 -t 16 contigs.fa hic_R1.fq.gz hic_R2.fq.gz | \
    samtools view -@ 8 -b - > aligned.bam
# Mandatory: mark/remove PCR + optical duplicates (Hi-C is duplicate-rich) before scaffolding.
samtools sort -@ 8 -n aligned.bam | samtools fixmate -m - - | \
    samtools sort -@ 8 - | samtools markdup -@ 8 - hic_to_contigs.bam
samtools index hic_to_contigs.bam
```

- **Each end separately, no mate rescue** (`-5SP`): `-5` = 5' portion of a chimeric junction read as primary; `-S`/`-P` skip mate rescue and pairing. The Arima/VGP per-end pipeline (`bwa mem` on R1 and R2 independently, `filter_five_end.pl`, `two_read_bam_combiner.pl`) is the higher-fidelity equivalent.
- **MAPQ filter** at scaffolding (YaHS `-q`, SALSA2 reads MAPQ) to drop repeat-ambiguous reads.
- **Enzyme awareness:** Arima/Dovetail-DpnII cut at fixed motifs (`GATC`); the scaffolder uses `-e` to model legitimate read starts. **Omni-C / DNase Hi-C is enzyme-free** -> omit `-e` in YaHS, use `-e DNASE` in SALSA2.
- **chromap** (Zhang 2021 *Nat Commun* 12:6566) is the fast modern alternative: `chromap --preset hic -r contigs.fa -x index -1 R1 -2 R2 ...` aligns + dedups Hi-C ~10x faster; YaHS accepts its output.

## YaHS (the current default)

```bash
samtools faidx contigs.fa
# Enzyme: -e GATC (DpnII/Dovetail), -e GATC,GANTC (Arima 2-enzyme); OMIT -e for Omni-C/enzyme-free.
yahs -e GATC -o out contigs.fa hic_to_contigs.bam
# Outputs: out_scaffolds_final.agp + out_scaffolds_final.fa, intermediate out_rNN.agp, out.bin
# Contig error-correction is ON by default (--no-contig-ec to disable; usually a mistake to disable).

# Juicebox prep for curation (.hic + .assembly to load in JBAT):
# NOTE: `juicer` here is the small utility BUNDLED with YaHS (operates on the .bin), NOT Aiden-lab Juicer;
# `juicer_tools.jar` below IS the separate Aiden-lab jar. Do not confuse the two.
juicer pre -a -o out_JBAT out.bin out_scaffolds_final.agp contigs.fa.fai 2>tmp_assembly.log
java -Xmx48G -jar juicer_tools.jar pre out_JBAT.txt out_JBAT.hic <(cat tmp_assembly.log | grep PRE_C_SIZE | awk '{print $2" "$3}')
# After hand-editing in Juicebox, export out_JBAT.review.assembly, then:
juicer post -o out_curated out_JBAT.review.assembly out_JBAT.liftover.agp contigs.fa
```

YaHS also accepts a BED (`bamToBed`) or PA5/pairs input. The `_scaffolds_final.agp` is the editable, reviewable object - curation edits the AGP, then regenerates FASTA. `--telo-motif` lets YaHS use telomere signal during scaffolding.

## SALSA2 (graph-aware, iterative, breaks chimeras)

```bash
bamToBed -i aligned.bam > alignment.bed
sort -k4 alignment.bed > sorted.bed                 # MUST sort by read name (column 4)
python run_pipeline.py -a contigs.fa -l contigs.fa.fai -b sorted.bed \
       -e GATC -o salsa_out -m yes -g contigs_graph.gfa -p yes
# -e DNASE for Omni-C/enzyme-free; -m yes enables input-error (chimera) correction; -p yes writes AGP+FASTA per iteration
```

The signature `-m yes` step breaks input contigs where the Hi-C signal contradicts the assembler's join *before* scaffolding. Assembly headers must not contain `:`. `-i` sets iterations (default 3), `-c` min contig length (default 1000).

## Reference-Guided Scaffolding (RagTag) -- Power and Peril

```bash
ragtag.py correct ref.fa contigs.fa                 # break query at putative misassemblies vs reference FIRST
ragtag.py scaffold ref.fa ragtag_output/ragtag.correct.fasta -t 16   # order/orient by homology (minimap2 default)
# Outputs ragtag.scaffold.agp + .fasta; inserts 100 bp N gaps by default; -C collapses unplaced into chr0.
```

**The peril (load-bearing):** RagTag orders contigs *to match the reference*, so by construction the output looks like the reference. Every real biological rearrangement that distinguishes the target organism - a chromosome fusion, fission, translocation, or inversion polymorphism - is silently **erased** and replaced by the reference's structure. **Never reference-scaffold a genome whose karyotype or large-scale structure is a biological question** - the pipeline "discovers" the reference's karyotype because it was imposed (this has happened in the literature). Acceptable uses: a structurally conserved close relative needing only a coordinate system for gene content; a scaffold *hypothesis* to then test/correct against Hi-C (`ragtag.py merge -b hic.bam` lets Hi-C arbitrate). On a genome with interesting structure the honest move is Hi-C + curation, full stop.

## Genetic/Linkage Maps (ALLMAPS) and Optical Maps (Bionano)

ALLMAPS (Tang 2015 *Genome Biol* 16:3) integrates one or more genetic maps to order/orient scaffolds: `allmaps merge map1.csv map2.csv -o maps.bed` then `allmaps path maps.bed contigs.fa`. It is the gold standard for *validating* chromosome assignment and for species where Hi-C is hard; weight multiple maps by quality. Bionano Solve hybrid scaffolding (no journal paper; cite the *Bionano Solve Theory of Operation: Hybrid Scaffold* technical document) aligns DLS optical maps to in-silico contig maps, resolves conflicts, and merges into hybrid scaffolds - run it *before* Hi-C on large/repetitive genomes where megabase maps bridge repeat arrays Hi-C fumbles. The decision is economic (separate instrument + library), not purely technical.

## Reading the Contact Map (the skill nobody writes down)

The map *displays its own errors* to a trained eye - render with PretextMap -> PretextView (interactive, emits a curated AGP), PretextSnapshot (static PNG), or Juicebox/JBAT.

- **Correct chromosome:** one bright diagonal, contacts decaying smoothly off-diagonal; inter-chromosome space dim and uniform.
- **Misjoin:** the diagonal breaks - signal jumps off-diagonal into a separate block at the junction (two diagonals stitched at a corner). Break it.
- **Inversion:** an **anti-diagonal "bowtie"/butterfly** - the gradient runs backwards through the segment. The most common curation fix once recognized; flip it.
- **Translocation / wrong assignment:** off-diagonal bright blocks bleeding between what should be separate chromosomes.
- **False duplication (leaked haplotig):** a faint off-diagonal stripe parallel to the diagonal contacting the same neighborhood. Remove it (49 of the 221 interventions/Gb).
- **Hardest judgment:** the map is noisy near the diagonal even when correct. A *real* weak join is faint but coherent with the right decay shape; *mapping noise* is structureless speckle. Treat ambiguous near-diagonal signal as a flag to inspect, not a number to trust.

## Chimera-Breaking, Gap-Filling, and Phasing-vs-Scaffolding

- **Break, then scaffold:** SALSA2 `-m yes` and YaHS default contig-EC break chimeric input where Hi-C contradicts the join; Tigmint (Jackman 2018 *BMC Bioinformatics* 19:393) breaks before ARCS for linked reads; RagTag `correct` for the reference-based version. Disabling these to "preserve the assembly" is a common self-inflicted wound.
- **Gap-filling is a SEPARATE downstream step** that replaces N-runs with real sequence by bridging long reads across the gap (TGS-GapCloser; LR_Gapcloser). Gaps sit at repeats (that is why the assembler stopped there), so a read can bridge into the *wrong* repeat copy and insert locally-plausible but globally-wrong sequence - worse than an honest N. Gap-fill *after* curation, sanity-check filled lengths against the gap estimate, and report which gaps were closed vs left.
- **Hi-C-for-scaffolding vs Hi-C-for-phasing:** the same library, two jobs. Scaffolding asks *where on the chromosome* (orders collapsed contigs); phasing asks *which homolog* (hifiasm `--h1/--h2` during assembly). When handed "Hi-C, make chromosomes," the first question is *haploid scaffolding or diploid phasing+scaffolding?* - the tools and failure modes differ entirely.

## Per-Method Failure Modes

### Shipping the automated AGP as final
**Trigger:** publishing `_scaffolds_final` without curation. **Mechanism:** automated joins are inferences error-prone at junctions (~221 edits/Gb in VGP/DToL). **Symptom:** misjoins/inversions in the contact map; later-discovered wrong synteny/fusions. **Fix:** curate in PretextView/JBAT before any large-scale-order claim.

### Conflating scaffold N50 with contig N50
**Trigger:** reporting only scaffold N50. **Mechanism:** scaffolding adds N-gaps, not sequence. **Symptom:** spectacular scaffold N50 over a small contig N50 - contiguity is nitrogen. **Fix:** report both N50s, gap count, total N bases separately.

### Reference-scaffolding a structurally interesting genome
**Trigger:** RagTag on a non-model genome whose karyotype is studied. **Mechanism:** ordering to the reference imposes the reference's structure. **Symptom:** fusions/translocations/inversions silently erased; circular "discovery" of the reference karyotype. **Fix:** Hi-C + curation; use RagTag only as a hypothesis to test.

### Scaffolding before breaking chimeras
**Trigger:** scaffolding contigs as given, contig-EC off. **Mechanism:** a chimeric contig drags region B into region A's chromosome; every join to it is wrong. **Symptom:** misjoins the contact map blames on the scaffolder. **Fix:** keep SALSA2 `-m yes` / YaHS contig-EC on; Tigmint for linked reads.

### Treating Hi-C reads as a normal PE library
**Trigger:** `bwa mem` without `-5SP`, no dedup, or proper-pair logic. **Mechanism:** the two ends are different loci; mate rescue and insert-size filtering corrupt placement. **Symptom:** sparse/noisy contact map, weak joins. **Fix:** map each end separately (`-5SP` or per-end pipeline), dedup, MAPQ filter, enzyme-aware.

### Gap-filling across a repeat
**Trigger:** running a gap-closer over the whole assembly to "finish" it. **Mechanism:** a long read bridges into a different copy of the repeat the gap sits in. **Symptom:** filled length far from the gap estimate; locally clean, globally mis-assembled. **Fix:** gap-fill after curation, sanity-check lengths, report closed-vs-left.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| ~221 curation interventions/Gb (67 breaks, 105 joins, 49 false-dup) | Howe 2021 *GigaScience* | expect the automated draft to be substantially editable, not finished |
| Hi-C ~50-100M valid pairs (vertebrate); rule-of-thumb ~1x coverage per ~1 Mb | VGP practice (~approx) | too little -> weak/missing joins, sparse noisy map; depends on genome size/repeats |
| Scaffold N50 / contig N50 > ~10x | curator reflex | contiguity is gap-borne; flag genome as contiguous-on-paper but unfinished |
| T2T chromosome = telomere at BOTH ends + zero internal gaps | T2T convention | tidk both-end recovery with internal Ns = chromosome-scale but not finished |
| RagTag default gap = 100 bp N | Alonge 2022 | placeholder length is arbitrary; never a real distance estimate |
| MAPQ filter on Hi-C reads (e.g. YaHS `-q 10`) | mapping practice | drop repeat-ambiguous reads that create spurious joins |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `_scaffolds_final` looks chromosome-scale but synteny is wrong | shipped uncurated draft | curate the contact map in PretextView/JBAT |
| Huge scaffold N50, small contig N50 | contiguity borne by N-gaps | report both; do not conflate |
| Reference-scaffolded genome "has" the reference's karyotype | RagTag imposed the structure | re-scaffold with Hi-C + curation |
| Sparse/noisy contact map, few joins | Hi-C mapped as normal PE / under-sequenced | remap with `-5SP`+dedup; add Hi-C coverage |
| YaHS makes spurious joins | enzyme/MAPQ misconfigured; chimeric contigs | set correct `-e` (omit for Omni-C), raise `-q`, keep contig-EC on |
| SALSA2 errors on input | `:` in FASTA headers or BED not name-sorted | rename headers; `sort -k4` the BED |
| Filled gaps far from estimated length | gap-filler bridged wrong repeat copy | gap-fill post-curation; sanity-check lengths; report closed-vs-left |

## References

- Zhou C, McCarthy SA, Durbin R. 2023. YaHS: yet another Hi-C scaffolding tool. *Bioinformatics* 39:btac808.
- Ghurye J, et al. 2019. Integrating Hi-C links with assembly graphs for chromosome-scale assembly (SALSA2). *PLoS Comput Biol* 15:e1007273.
- Dudchenko O, et al. 2017. De novo assembly of the Aedes aegypti genome using Hi-C yields chromosome-length scaffolds (3D-DNA). *Science* 356:92-95.
- Durand NC, et al. 2016. Juicer provides a one-click system for analyzing loop-resolution Hi-C experiments. *Cell Syst* 3:95-98.
- Alonge M, et al. 2022. Automated assembly scaffolding using RagTag elevates a new tomato system for high-throughput genome editing. *Genome Biol* 23:258.
- Tang H, et al. 2015. ALLMAPS: robust scaffold ordering based on multiple maps. *Genome Biol* 16:3.
- Yeo S, et al. 2018. ARCS: scaffolding genome drafts with linked reads. *Bioinformatics* 34:725-731.
- Jackman SD, et al. 2018. Tigmint: correcting assembly errors using linked reads from large molecules. *BMC Bioinformatics* 19:393.
- Zhang H, et al. 2021. Fast alignment and preprocessing of chromatin profiles with chromap. *Nat Commun* 12:6566.
- Rhie A, et al. 2021. Towards complete and error-free genome assemblies of all vertebrate species (VGP). *Nature* 592:737-746.
- Howe K, et al. 2021. Significantly improving the quality of genome assemblies through curation. *GigaScience* 10:giaa153.
- Brown MR, Gonzalez de la Rosa PM, Blaxter M. 2025. tidk: a toolkit to rapidly identify telomeric repeats from genomic datasets. *Bioinformatics* 41:btaf049.
- Bionano Genomics. Bionano Solve Theory of Operation: Hybrid Scaffold (technical document) - hybrid scaffolding has no journal paper.

## Related Skills

- long-read-assembly - Produces the contigs this skill orders into chromosomes
- hifi-assembly - hifiasm phases haplotypes (Hi-C `--h1/--h2`) before each is scaffolded
- assembly-polishing - Polish contigs before scaffolding; gaps remain N until gap-filling
- assembly-qc - Contig-vs-scaffold N50, BUSCO, and Merqury QV on the scaffolded result
- hi-c-analysis/hic-data-io - Hi-C read/pairs handling feeding the scaffolder
- comparative-genomics/synteny-analysis - Validate scaffold order/orientation against a related genome
- workflows/genome-assembly-pipeline - End-to-end QC -> assemble -> polish -> scaffold -> curate -> QC
<!-- END FILE: genome-assembly/scaffolding/SKILL.md -->

## 子目录：genome-assembly/short-read-assembly

<!-- BEGIN FILE: genome-assembly/short-read-assembly/SKILL.md -->
---
name: bio-genome-assembly-short-read-assembly
description: Assembles a genome de novo from Illumina short reads with SPAdes (isolate/careful/sc/meta/plasmid/rna modes), MEGAHIT (low-memory, huge datasets), Unicycler (bacterial finishing/hybrid), MaSuRCA (large hybrid), ABySS (Bloom-filter), and Platanus (heterozygous diploids), using multi-k de Bruijn graphs. Covers the repeat-resolution limit, why N50 plateaus at the genome not the depth, GenomeScope2 k-mer profiling first, the heterozygosity/haplotig trap, error-correction erasing rare alleles, GC dropout, and NG50/auN/BUSCO reporting. Use when assembling a bacterial isolate, fungal, small-eukaryotic, single-cell, or metagenome genome from Illumina reads, or when deciding whether short reads can even produce the assembly being asked for.
tool_type: cli
primary_tool: SPAdes
---

## Version Compatibility

Reference examples tested with: SPAdes 4.0+, MEGAHIT 1.2+, Unicycler 0.5+, ABySS 2.3+, GenomeScope2 2.0+, KMC 3.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

SPAdes 4.0 (June 2024) requires Python >=3.8, defaults to GFA v1.2 output with circular-path tags (`TP:Z:circular`), and is stated by the maintainers to be the last major feature release - pin the version in methods, because k auto-selection and the `--isolate`/`--careful` recommendation flipped across 3.x. MEGAHIT preset k-lists (`meta-sensitive`, `meta-large`) have changed across versions - confirm against `megahit -h` before hard-coding. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Short-Read Assembly

**"Assemble a genome from Illumina reads"** -> Build a multi-k de Bruijn graph from short reads and walk it into contigs, knowing the contiguity ceiling is set by the genome's repeat structure, not the depth.
- CLI: `spades.py --isolate -1 R1.fq.gz -2 R2.fq.gz -o out -t 16` (bacterial isolate, the genuine sweet spot)
- CLI: `megahit -1 R1.fq.gz -2 R2.fq.gz -o out -t 16` (huge/low-memory, metagenome)
- CLI: profile first (see below): `genomescope2 -i kmer.hist -o gs -k 21 -p 2` (size/het/repeat before parameters)

## The Single Most Important Modern Insight -- Short Reads Cannot Span Repeats, So Contiguity Is Capped by the Genome, Not the Depth

A short read (~150 bp) or paired insert (~300-600 bp) cannot resolve any repeat longer than itself: the de Bruijn graph enters a repeat from multiple unique flanks, traverses an identical internal path, and the assembler's only safe move is to break the contig at the repeat boundary or collapse the copies. Genomic repeats - rRNA operons (~5 kb), transposons, segmental duplications, satellites - are routinely kilobases to megabases. So a short-read assembly is **structurally fragmented at every long repeat**, and that is biology, not a software defect. Three load-bearing corollaries:

1. **N50 plateaus at the repeat structure, not the sequencing depth.** Past ~50-100x for an isolate (~50-60x for a eukaryote), more Illumina does NOT lengthen contigs - it only adds error-correction signal, and above ~150x it actively hurts by amplifying GC bias and duplicate-driven coverage distortion. The reflex "add more reads to get a better assembly" is wrong: the limit is read length.

2. **The assembler is almost never the bottleneck - the input DNA and the genome's repeat/heterozygosity structure are.** A clean, high-molecular-weight, PCR-free library at the right depth assembles beautifully with defaults; a degraded/contaminated library assembles badly with every setting and every k. The expert's first move on a bad assembly is to look at the k-mer spectrum, GC-vs-coverage, and duplication rate (GenomeScope2 profiling, see the profiling section below), not to swap assemblers or sweep k.

3. **Short reads are no longer the frontier instrument for a finished genome.** For any genome that must be complete or finished, the answer is long reads that span the repeats (`-> long-read-assembly`, `-> hifi-assembly`), with short reads relegated to polishing, k-mer-spectrum QC, and the cheap bacterial-isolate/surveillance workhorse. A skill that lets an agent attempt a de novo short-read assembly of a large, repeat-rich, heterozygous eukaryote and then blame parameters is doing harm.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| SPAdes | Bankevich 2012 *J Comput Biol* | multi-k de Bruijn assembler with mode dispatch | bacterial/fungal/small-euk isolate; the field default |
| MEGAHIT | Li 2015 *Bioinformatics* | succinct (compressed) de Bruijn, ultra-low memory | huge short-read datasets, metagenomes, memory-constrained |
| Unicycler | Wick 2017 *PLoS Comput Biol* | SPAdes wrapper + graph bridging + circularization | bacterial finishing; hybrid Illumina+long-read |
| MaSuRCA | Zimin 2013 *Bioinformatics* | super-reads + mega-reads (hybrid OLC/DBG) | large eukaryotic genomes with mixed data |
| ABySS 2.0 | Jackman 2017 *Genome Res* | Bloom-filter de Bruijn, MPI-parallel | large genomes on memory-constrained HPC |
| Platanus / Platanus-allee | Kajitani 2014 *Genome Res* | bubble-aware DBG for high heterozygosity | highly heterozygous diploids (a real niche) |
| GenomeScope2 / Smudgeplot | Ranallo-Benavidez 2020 *Nat Commun* | k-mer-histogram model: size/het/repeat/ploidy | run FIRST; sets the ceiling reference-free |
| Velvet / SOAPdenovo2 | Zerbino 2008 *Genome Res* / Luo 2012 *GigaScience* | single-k DBG, superseded | reproduce old papers only; do not start new projects |

Every mainstream short-read assembler is a de Bruijn assembler because all-vs-all overlap (OLC) is infeasible for hundreds of millions of short reads. The single most consequential parameter is k: small k over-connects (collapses repeats, chimeras), large k is more unique (resolves repeats up to length k) but demands higher coverage and is error-fragile. No single k is optimal everywhere in a genome, which is exactly why SPAdes and MEGAHIT iterate over a k-series - do NOT hand-pick a single k.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Reads not yet profiled | GenomeScope2 on a k-mer histogram (profiling section below) | the spectrum sets size/het/repeat ceiling before any parameter |
| Reads not yet QC'd | -> read-qc/quality-reports, read-qc/adapter-trimming | over-trimming creates coverage holes that fragment the graph |
| Bacterial/archaeal/viral isolate, Illumina only | SPAdes `--isolate` | multi-k DBG + paired-end repeat resolution; the genuine sweet spot |
| Small bacterial genome, want mismatch/indel cleanup | SPAdes `--careful` (small genomes ONLY) | runs MismatchCorrector; NOT for large eukaryotes; incompatible with --meta/--rna |
| Bacterial isolate, want a finished/circular assembly | Unicycler (short-only or hybrid) | graph bridging + circularization + rotation to dnaA |
| Single-cell / MDA-amplified | SPAdes `--sc` | designed for the wildly uneven MDA coverage |
| Highly heterozygous diploid, short reads | Platanus-allee, then purge | bubble-aware; but consider -> hifi-assembly instead |
| Metagenome (recover MAGs) | -> metagenome-assembly (metaSPAdes / MEGAHIT) | community co-assembly; MAG recovery, not single-genome N50 |
| Huge dataset, RAM-constrained | MEGAHIT | succinct DBG, tiny memory footprint |
| Large/repeat-rich/heterozygous eukaryote, finished genome wanted | -> hifi-assembly or -> long-read-assembly | short reads mathematically cannot span the repeats |
| Assembly built, judging quality | -> assembly-qc (NG50 + auN + BUSCO + Merqury QV) | never report N50 alone; contiguity is not correctness |

## SPAdes -- the dominant short-read assembler (the mode is a graph choice, not a cosmetic flag)

```bash
spades.py --isolate -1 R1.fq.gz -2 R2.fq.gz -o out -t 16 -m 64   # recommended default for isolates; does NOT run MismatchCorrector
spades.py --careful -1 R1.fq.gz -2 R2.fq.gz -o out               # SMALL genomes only; runs MismatchCorrector; NOT eukaryotes; not with --meta/--rna
spades.py --sc      -1 R1.fq.gz -2 R2.fq.gz -o out               # single-cell/MDA (default k 21,33,55)
spades.py --plasmid -1 R1.fq.gz -2 R2.fq.gz -o out              # plasmidSPAdes (coverage-based extraction)
spades.py -1 R1.fq.gz -2 R2.fq.gz -o out -k 21,33,55,77         # explicit multi-k LIST (odd, <= read length) only if overriding
spades.py --only-assembler -1 R1.fq.gz -2 R2.fq.gz -o out       # skip BayesHammer (reads pre-corrected, or het/pooled data)
```

Picking the wrong mode is the most common SPAdes error. `--isolate` and `--careful` solve different problems: modern SPAdes pushes `--isolate` as the isolate default (tuned for high, even coverage), while `--careful` runs BWA-based MismatchCorrector to cut mismatches/short indels on **small** genomes only - it is explicitly slow, memory-heavy, and low-benefit on medium/large eukaryotes, and is incompatible with `--meta` and `--rna`. `--isolate` and `--careful` are mutually exclusive - SPAdes aborts (`cannot specify --careful in isolate mode`) if both are given; pick one. `--meta`, `--rna`, `--bio` dispatch to genuinely different pipelines (metaSPAdes, rnaSPAdes, biosyntheticSPAdes) with different graph models - they are NOT genome assembly. BayesHammer (the built-in Illumina error-corrector) runs by default; `--only-assembler` skips it. Outputs: `contigs.fasta`, `scaffolds.fasta`, `assembly_graph.gfa`. Always report contig metrics, not just scaffold metrics (scaffold gaps are estimated N-runs, not sequence).

## MEGAHIT, Unicycler, and the others

```bash
megahit -1 R1.fq.gz -2 R2.fq.gz -o out -t 16                    # default k 21,29,39,59,79,99,119,141; min-count 2 (drops singleton error k-mers)
megahit -1 R1.fq.gz -2 R2.fq.gz --presets meta-sensitive -o out # min-count 1; verify k-list against megahit -h
unicycler -1 R1.fq.gz -2 R2.fq.gz -o out -t 16                  # short-read-only bacterial finishing
unicycler -1 R1.fq.gz -2 R2.fq.gz -l long.fq.gz -o out          # hybrid (short for accuracy + long to bridge repeats)
abyss-pe name=asm k=96 B=2G in='R1.fq.gz R2.fq.gz'              # B = Bloom-filter size (the 2.0 low-memory mode); single k
```

MEGAHIT's succinct DBG gives a tiny memory footprint at some cost in contiguity/accuracy versus metaSPAdes - the default for huge datasets and a metagenome alternative. Unicycler wraps SPAdes, cleans the graph, bridges repeats, and rotates circular replicons to `dnaA`; hybrid mode (short + ONT/PacBio) is the bacterial finishing standard but a short-only run still cannot beat the repeat limit. ABySS 2.0's Bloom-filter mode enables large-genome assembly on modest hardware but is single-k and niche today.

## Pre-Assembly Genome Profiling (run this FIRST)

```bash
kmc -k21 -t16 -m64 -ci1 -cs10000 @reads.lst kmcdb tmp/         # k=21: long enough to be mostly unique, short enough for k-mer coverage
kmc_tools transform kmcdb histogram kmer.hist -cx10000
genomescope2 -i kmer.hist -o gs_out -k 21 -p 2                 # -p ploidy; estimates size, heterozygosity, repeat content
```

GenomeScope2 fits a model to the k-mer frequency histogram and returns, reference-free and before assembly, the genome size, heterozygosity rate, repeat content, and ploidy. A single histogram peak ~ haploid/homozygous; two peaks (a het peak at ~half the homozygous-peak coverage) ~ a heterozygous diploid that will fragment and inflate a short-read assembly. This is the ceiling check: it predicts whether short reads can even produce the assembly being asked for, and it gives the expected size to report assembly total against (assembly >> estimate = un-purged haplotigs, not a big genome).

## Per-Method Failure Modes

### Adding more coverage to fix contiguity
**Trigger:** re-sequencing deeper because contigs are short. **Mechanism:** contiguity is capped by read length vs repeat length, not depth. **Symptom:** N50 unchanged past ~50-100x; cost wasted. **Fix:** accept the repeat-determined ceiling, or switch to long reads (`-> hifi-assembly`).

### Hand-picking a single large k for highest N50
**Trigger:** "we used k=127 because it gave the best N50". **Mechanism:** large k demands high effective k-mer coverage and is error-fragile; climbing k until N50 peaks is an N50-gaming search that rewards chimeric mega-contigs. **Symptom:** gappy assembly, or a suspiciously contiguous mis-joined one. **Fix:** let multi-k auto-select; if overriding, give a small->large list, never a point.

### `--careful` on a eukaryote
**Trigger:** cargo-culting `--careful` from a bacterial tutorial. **Mechanism:** MismatchCorrector is small-genome-only; on a large genome it is slow, memory-hungry, low-benefit. **Symptom:** the run stalls/OOMs for little quality gain. **Fix:** `--isolate` (no `--careful`) for isolates; defer base accuracy to dedicated polishing (`-> assembly-polishing`).

### Error-correcting heterozygous/pooled/metagenomic data
**Trigger:** running BayesHammer/BFC/Lighter on a diploid, pooled, or community sample. **Mechanism:** k-mer-spectrum correctors assume rare k-mers are errors and edit them toward the consensus - but the minor allele / rare strain IS those rare k-mers. **Symptom:** real low-frequency variation silently flattened before assembly. **Fix:** `--only-assembler` for het/pooled/meta data; correct only clonal isolates.

### Reporting the inflated heterozygous assembly size as the genome size
**Trigger:** assembly total ~1.5-2x the GenomeScope estimate, high BUSCO-Duplicated. **Mechanism:** both haplotypes assembled separately (un-purged haplotigs), not a real duplication. **Symptom:** "genome size" wrong by up to 2x. **Fix:** purge_dups / redundans, or -> hifi-assembly; report size against the profiling estimate.

### Treating a short-read bacterial assembly's contig count as a failure
**Trigger:** "why isn't my isolate one contig?" **Mechanism:** ~7 rRNA operons and IS elements each exceed the insert and force a break - the contig count is roughly a count of long repeats. **Symptom:** 30-100 contigs from a perfect run. **Fix:** accept it for typing/AMR/phylogenetics; for a finished single contig, use Unicycler hybrid or long reads.

### Chasing GC-dropout gaps with more depth
**Trigger:** re-assembling to close a gap whose flanks have normal coverage. **Mechanism:** PCR/chemistry under-represents GC-extreme regions; the bias, not the depth, is the problem. **Symptom:** an interior coverage hole at extreme GC that stays missing at 30x and 300x. **Fix:** upstream (PCR-free prep, alternative polymerase) or different chemistry, not a parameter.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Bacterial isolate coverage ~50-100x | field convention | below ~30x error/true k-mers blur and gaps proliferate; 50-100x = clean correction + strong k-mer peak |
| Above ~100-150x: diminishing/negative | field convention | does not fix repeats; amplifies GC bias; duplicates distort the coverage model and GenomeScope fit |
| Eukaryote short-read coverage ~50-60x | field convention | higher wastes money on unresolvable repeats; lower starves the graph |
| GenomeScope/profiling k = 21 | field convention | long enough to be mostly unique, short enough for adequate k-mer coverage |
| k constraint: odd, <= read length | DBG property | even k can self-loop on palindromes; k > read is impossible |
| Heterozygous assembly inflation ~1.5-2x haploid | het diploid norm | both haplotypes assembled separately; do not report as genome size |
| MEGAHIT min-count default 2 | MEGAHIT default | filters singleton (error) k-mers; presets drop to 1 for low-abundance metagenome members |
| Report NG50 + auN + BUSCO + a reference-free correctness check | reporting convention | N50 alone is gamed by dropping sequence and inflated by mis-joins (auN = sum(L_i^2)/G) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Out of memory | large/complex dataset, high coverage | lower `-m`; use MEGAHIT (succinct DBG) or ABySS Bloom-filter mode |
| Assembly ~2x expected size, high BUSCO-Duplicated | un-purged haplotigs (heterozygosity) | purge_dups/redundans; Platanus-allee; or -> hifi-assembly |
| Many contigs from a clean bacterial isolate | rRNA operons / IS elements exceed the insert (biology) | accept for draft uses; Unicycler hybrid or long reads for a finished genome |
| Extra contigs at odd coverage | contamination/index hopping, not a novel replicon | coverage-vs-GC screen (`-> contamination-detection`) |
| Poor assembly after heavy trimming | over-trimming created coverage holes | trim adapters + bad tails only; keep reads long |
| N50 high but downstream results wrong | mis-join / N50-gaming; high N50 != correct | report NG50 + auN + BUSCO; reference-free correctness (`-> assembly-qc`) |
| `--careful` rejected / errors | used with `--meta` or `--rna` | drop `--careful`; it is small-genome isolate-only |

## References

- Bankevich A, et al. 2012. SPAdes: a new genome assembly algorithm and its applications to single-cell sequencing. *J Comput Biol* 19:455-477.
- Compeau PEC, Pevzner PA, Tesler G. 2011. How to apply de Bruijn graphs to genome assembly. *Nat Biotechnol* 29:987-991.
- Li D, et al. 2015. MEGAHIT: an ultra-fast single-node solution for large and complex metagenomics assembly via succinct de Bruijn graph. *Bioinformatics* 31:1674-1676.
- Wick RR, et al. 2017. Unicycler: resolving bacterial genome assemblies from short and long sequencing reads. *PLoS Comput Biol* 13:e1005595.
- Jackman SD, et al. 2017. ABySS 2.0: resource-efficient assembly of large genomes using a Bloom filter. *Genome Res* 27:768-777.
- Zerbino DR, Birney E. 2008. Velvet: algorithms for de novo short read assembly using de Bruijn graphs. *Genome Res* 18:821-829.
- Luo R, et al. 2012. SOAPdenovo2: an empirically improved memory-efficient short-read de novo assembler. *GigaScience* 1:18.
- Zimin AV, et al. 2013. The MaSuRCA genome assembler. *Bioinformatics* 29:2669-2677.
- Kajitani R, et al. 2014. Efficient de novo assembly of highly heterozygous genomes from whole-genome shotgun short reads (Platanus). *Genome Res* 24:1384-1395.
- Ranallo-Benavidez TR, Jaron KS, Schatz MC. 2020. GenomeScope 2.0 and Smudgeplot for reference-free profiling of polyploid genomes. *Nat Commun* 11:1432.
- Lander ES, Waterman MS. 1988. Genomic mapping by fingerprinting random clones: a mathematical analysis. *Genomics* 2:231-239.

## Related Skills

- genome-profiling - Estimate genome size, heterozygosity, and ploidy from a k-mer spectrum before assembling
- assembly-qc - NG50 + auN + BUSCO + Merqury QV; never report N50 alone
- assembly-polishing - Base-accuracy polishing belongs here, not in `--careful` reflexes
- metagenome-assembly - Community co-assembly and MAG recovery (metaSPAdes/MEGAHIT)
- long-read-assembly - The real fix for repeats short reads cannot span
- hifi-assembly - Phased, repeat-spanning assembly for heterozygous/complex eukaryotes
- read-qc/quality-reports - Garbage-in caps assembly quality; QC reads before assembling
- read-qc/adapter-trimming - Light adapter/quality trimming; over-trimming fragments the graph
- workflows/genome-assembly-pipeline - End-to-end QC -> assemble -> polish -> scaffold -> QC
<!-- END FILE: genome-assembly/short-read-assembly/SKILL.md -->

<!-- END CATEGORY: genome-assembly -->

