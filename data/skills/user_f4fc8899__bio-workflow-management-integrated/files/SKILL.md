---
slug: bio-workflow-management-integrated
version: 1.0.0
displayName: "工作流管理 / Workflow management"
name: bio-workflow-management-integrated
summary: >-
  中文：工作流管理综合技能，整合 5 个相关专题，覆盖工作流管理：Snakemake、Nextflow、WDL、CWL、nf-core流程部署与执行。 English: Integrated Workflow management skill covering 5 related topics, including Workflow management: Snakemake, Nextflow, WDL, CWL, nf-core pipeline deployment and execution.
description: >-
  中文：这是一个面向工作流管理的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：工作流管理：Snakemake、Nextflow、WDL、CWL、nf-core流程部署与执行。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Nextflow, Snakemake, cromwell。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Workflow management, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Workflow management: Snakemake, Nextflow, WDL, CWL, nf-core pipeline deployment and execution. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Nextflow, Snakemake, cromwell. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# workflow-management 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: workflow-management -->

## 子目录：workflow-management/cwl-workflows

<!-- BEGIN FILE: workflow-management/cwl-workflows/SKILL.md -->
---
name: bio-workflow-management-cwl-workflows
description: Authors portable, strongly-typed bioinformatics pipelines in the Common Workflow Language (CWL v1.2) as CommandLineTool/Workflow/ExpressionTool documents, validated with cwltool and run at scale on Toil/Arvados/Calrissian. Use when deciding CWL (portability/provenance/regulated) vs Nextflow/WDL/Snakemake; declaring secondaryFiles for indexed companions (.bai/.fai/.dict/.tbi and the caret rule); putting resources/containers under requirements (must-hold) vs hints (advisory) to avoid silent OOM; choosing scatterMethod (dotproduct vs flat_/nested_crossproduct); preferring $(...) parameter refs over ${...} JavaScript for portability; pinning DockerRequirement images; or emitting a CWLProv provenance object for audited/clinical settings.
tool_type: cli
primary_tool: cwltool
---

## Version Compatibility

Reference examples tested with: cwltool 3.1+, CWL spec v1.2, Docker 24+ (or Singularity/Apptainer 3.8+)

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: target `cwlVersion: v1.2` for genomics (the record-form secondaryFiles with `required:` needs it). cwltool is the REFERENCE runner - correct, local, single-node, deliberately slow - NOT the spec; run Toil/Arvados/Calrissian at scale. In v1.2, ExpressionTool outputs are NOT type-checked (a known reference-impl gap, fix planned for v1.3), so do not lean on ExpressionTool for type safety.

# CWL Workflows

**"Write a portable pipeline that runs the same everywhere and proves what it ran"** -> Describe each tool and their wiring as strongly-typed, machine-checkable CWL documents that any conforming runner honors identically, validate the contract before any compute, then execute locally (cwltool) or at scale (Toil/Arvados/Calrissian).
- CLI: `cwltool --validate wf.cwl`, `cwltool wf.cwl job.yml`, `cwltool --provenance ro/ wf.cwl job.yml`
- YAML: `class: CommandLineTool` (wrap a tool) and `class: Workflow` (wire tools) at `cwlVersion: v1.2`

## The governing principle: CWL is a SPECIFICATION, not an engine

CWL deliberately splits the workflow DESCRIPTION (a portable, declarative, strongly-typed YAML/JSON document) from its EXECUTION (performed by any conforming runner). Nextflow and Snakemake are engines that happen to have a DSL; WDL is a language with a dominant engine (Cromwell). CWL alone is a community-governed open standard with multiple independent implementations and a formal conformance test suite (Crusoe 2022 *Commun ACM* 65(6):54-63). The whole value proposition - portability, auditability, vendor-neutrality, provenance, regulatory fit - is a consequence of "spec not engine." The correct frame: the author writes a portable, machine-checkable CONTRACT for a computation that any conforming platform must honor identically. That contract is why CWL is the most VERBOSE and most EXPLICIT of the four systems - the verbosity buys static analyzability and portability.

The most common conceptual error is conflating CWL with cwltool. cwltool is the reference implementation: correct, single-node, and slow by design (it prioritizes spec-conformance over speed). "CWL is slow" or "CWL can't scale" almost always means "I ran cwltool" - at scale the same unchanged document runs on Toil (HPC/cloud batch), Arvados (clinical/enterprise data management), or Calrissian (Kubernetes). Never equate a runner's limits with the spec's.

Adopting CWL buys reproducible workflow LOGIC and nothing else automatically. A clean typed DAG over unpinned tools is NOT reproducible - pin the software environment (containers by digest, not a moving `:latest`), the reference data and seeds, and control arch/thread/locale leaks separately. The type system closes the wiring-error layer; the author still owns the rest.

## Decision: choose CWL vs the other engines

| Dimension | CWL | Nextflow | WDL | Snakemake |
|-----------|-----|----------|-----|-----------|
| Nature | open SPEC, many engines | engine + Groovy DSL | language + Cromwell/miniwdl | engine + Python DSL |
| Typing | strong static (File/Dir/record/enum/optional) | dynamic | moderate | weak (paths/strings) |
| Index companions | `secondaryFiles` = File type property | manual channel/tuple wiring | manual per-input | manual |
| Provenance | CWLProv RO out of the box | report/trace/DAG | via platform | report/plugins |
| Verbosity | HIGHEST (deliberate) | terse | moderate | moderate |
| New-author mindshare | DECLINING | ASCENDANT (nf-core) | strong on Terra | strong in academia |
| Sweet spot | multi-platform, provenance-critical, regulated/clinical, standards-driven | fast authoring, curated catalog | Terra/GATK ecosystem | single-lab Python/HPC |

Choose CWL when vendor-neutral portability across multiple platforms, a standardized provenance artifact for a regulated/audited setting, static type-checking before compute, or publishing to a multi-runner registry (Dockstore) drives the decision. Be honest about mindshare: for NEW pipeline authoring CWL has been losing ground to Nextflow/nf-core and WDL/Terra for years (they win on authoring speed and community momentum). CWL retains and deepens its hold where the SPEC is the point - not as a neutral default. Prefer Nextflow/WDL when authoring speed, an existing curated catalog (nf-core), or a specific hosted platform (Terra) dominates.

## Decision: which runner

| Engine | For | Runtime model | Notes |
|--------|-----|---------------|-------|
| cwltool | authoring, `--validate`, `--pack`, `--provenance`, CI, local dev | local, single-node | the conformance yardstick; slow by design - do NOT read its limits as CWL's |
| Toil | HPC and cloud batch scale | Python; Slurm/Kubernetes/AWS/Grid Engine | `toil-cwl-runner`; the workhorse for large CWL |
| Arvados | enterprise/clinical data management + execution | cluster + content-addressed storage | `arvados-cwl-runner`; strong data provenance; regulated settings |
| Calrissian | CWL on Kubernetes | one k8s pod per step | needs `ReadWriteMany` volumes; cloud-native parallelism |
| Cromwell | primarily WDL, PARTIAL CWL | JVM | runs a subset only; do not rely on it for full CWL conformance |

## Decision: requirements vs hints (get this wrong and jobs silently OOM)

`requirements` MUST be satisfied - if the runner cannot honor one, execution FAILS loudly (correctly). `hints` are advisory: the runner MAY honor or ignore them without error. The canonical failure is putting `ResourceRequirement: {ramMin: 32000}` under `hints` on a memory-hungry step - a runner is free to ignore a hint and schedule it on a small node, giving intermittent OOM kills. Anything whose absence would corrupt results or crash (the container, minimum RAM/cores, a required input layout, an env var a tool depends on) goes under `requirements`. Both inherit Workflow -> step -> tool with the INNERMOST declaration winning, so set a default `DockerRequirement`/`ResourceRequirement` at workflow scope and override per-step where a tool needs a different image or more RAM. A surprising container at a step is usually a forgotten override.

## Decision: scatterMethod

`scatter` runs a step once per array element; when scattering over MULTIPLE inputs, `scatterMethod` decides how they combine. This is the most misunderstood CWL construct.

| scatterMethod | Combines by | Jobs | Output shape | Use when |
|---------------|-------------|------|--------------|----------|
| `dotproduct` | position-aligned zip | N (arrays MUST be equal length) | flat array of N | paired arrays that correspond 1:1 (R1[i] with R2[i]) |
| `flat_crossproduct` | every combination | N x M | FLAT array of N x M | all pairs, want a flat result list |
| `nested_crossproduct` | every combination | N x M | NESTED array (N of M) | all pairs, preserve the 2-D grid |

`dotproduct` requires equal-length arrays (unequal is an error, not truncation). The two cross-products run the SAME N x M jobs and differ only in output nesting - choosing `flat_` vs `nested_` wrong gives the right computations with a mis-shaped output that then mis-wires a downstream `File[]` step. `ScatterFeatureRequirement` must be declared regardless of scatterMethod.

## CommandLineTool: wrap one tool

A CommandLineTool binds typed inputs to the command line (`inputBinding`) and captures outputs (`outputBinding.glob` or `stdout`). Tool outputs use `outputBinding`; workflow outputs use `outputSource` - mixing them is a validation error.

```yaml
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [bwa, mem]
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/bwa:0.7.17--he4a0461_11   # digest-pin in production; :latest breaks reproducibility
  ResourceRequirement:            # under requirements: must hold, or the runner fails loudly (a hint could be ignored -> OOM)
    coresMin: 8
    ramMin: 16000                 # MB; bwa-mem index residency + reads, empirical floor for a human genome
inputs:
  reference:
    type: File
    secondaryFiles:               # the .amb/.ann/.bwt/.pac/.sa BWA index files are STAGED next to the fasta
      [.amb, .ann, .bwt, .pac, .sa]
    inputBinding: {position: 2}
  reads_1: {type: File, inputBinding: {position: 3}}
  reads_2: {type: File?, inputBinding: {position: 4}}   # File? is optional: [null, File]
  threads: {type: int, default: 8, inputBinding: {prefix: -t, position: 1}}
stdout: aligned.sam
outputs:
  sam: {type: stdout}
```

## Workflow: wire tools by explicit typed connections

CWL is PULL/goal-oriented and fully declarative: dataflow is wired explicitly through `source`/`outputSource`, never through implicit channels (Nextflow) or filename wildcards (Snakemake). `--validate` type-checks every connection statically, before a byte of data moves.

```yaml
cwlVersion: v1.2
class: Workflow
requirements:
  ScatterFeatureRequirement: {}
inputs:
  fastq_1: File
  fastq_2: File
  salmon_index: Directory
outputs:
  quant_results:
    type: Directory
    outputSource: salmon/quant_dir     # workflow output wires with outputSource (NOT outputBinding)
steps:
  fastp:
    run: fastp.cwl
    in: {reads_1: fastq_1, reads_2: fastq_2}
    out: [trimmed_1, trimmed_2, json_report]
  salmon:
    run: salmon_quant.cwl
    in: {index: salmon_index, reads_1: fastp/trimmed_1, reads_2: fastp/trimmed_2}   # source: other_step/output
    out: [quant_dir]
```

## secondaryFiles: index and companion files as a type property

Genomics tools demand companion files that must sit next to the primary with a derived name: `.bam` needs `.bai`, `.fasta` needs `.fai` and `.dict`, `.vcf.gz` needs `.tbi`. CWL makes the companion a PROPERTY of the File type, so every conforming runner is OBLIGATED to co-stage them - the other engines leave this to hand-wiring. This is the single most genomics-relevant CWL feature and the strongest reason to target v1.2.

```yaml
inputs:
  bam:
    type: File
    secondaryFiles: [.bai]         # append: sample.bam -> sample.bam.bai staged alongside
  reference:
    type: File
    secondaryFiles:                # v1.2 record form makes required-ness explicit
      - {pattern: .fai, required: true}
      - {pattern: ^.dict, required: false}   # caret ^ STRIPS one extension: genome.fasta -> genome.dict (NOT genome.fasta.dict)
```

The caret `^` removes one extension from the basename before appending; each leading `^` strips one more - the classic `.dict` gotcha. In v1.0/v1.1 a bare string pattern is required-by-default; only the v1.2 record `{pattern, required}` form can mark an index optional (a `.tbi` that may be absent). secondaryFiles are declared on OUTPUT File parameters too, so a produced BAM carries its `.bai` to the next step; on inputs required defaults true, on outputs the index is collected if present.

## Expressions: $(...) is portable, ${...} is a portability debt

Parameter references `$(...)` are a restricted, safe subset - property/index access into `inputs`, `self`, `runtime` (e.g. `$(inputs.reads.nameroot)`, `$(runtime.outdir)`). They need NO JavaScript engine, are statically analyzable, and are portable - prefer them. Full JavaScript `${ return ...; }` runs only when `InlineJavascriptRequirement` is present; it is powerful but (a) needs a node engine wherever the workflow runs, (b) is opaque to static analysis, (c) is the leading cause of "works on my runner, breaks on theirs." Reach for `${...}` only when a parameter reference genuinely cannot express the need, and treat every `InlineJavascriptRequirement` as a portability debt taken on knowingly. `valueFrom` transforms a step input before it reaches the tool (needs `StepInputExpressionRequirement` for expressions at step scope).

## Portability leaks: "run anywhere" is real but DISCIPLINED

The promise is genuine for disciplined CWL, but it leaks - name the leaks. `InlineJavascriptRequirement` needs a JS engine (node). `DockerRequirement` carries arch/registry assumptions (an amd64-only image fails on arm64 Apple Silicon/Graviton; a private-registry image needs credentials the target may lack; `:latest` is not reproducible). Engine-specific extensions under custom namespaces (`cwltool:`, `arv:`) are portable only among runners that understand them - they live under `hints` so a naive runner can ignore them, but a workflow that DEPENDS on their behavior has forfeited portability. Conformance is graded (a coverage percentage per implementation), not binary - "valid CWL" does not guarantee "runs identically on engine X." The disciplined recipe: target v1.2; containerize every tool with a digest-pinned multi-arch image; minimize `${...}` in favor of `$(...)`; keep `cwltool:`/`arv:` items under `hints` and never depend on them for correctness; in the input (job) object prefer `location:` URIs over a local `path:` (a `path:` binds the job to one machine's filesystem); validate, then exercise the real target engine before trusting portability.

## Provenance: CWL's high ground for regulated/clinical settings

`cwltool --provenance ro/ wf.cwl job.yml` produces a CWLProv Research Object (a W3C PROV + RO-Crate/BagIt bundle) capturing the workflow, the exact input object, all outputs, intermediates, container images, and the enactment trace (Khan 2019 *GigaScience* 8(11):giz095). No other mainstream system ships a standardized retrospective-provenance artifact out of the box - this is the concrete reason CWL wins in regulated/audited genomics: hand an auditor one object that answers "exactly what ran, on what inputs, in what containers, producing what outputs." CWL is also a first-class GA4GH citizen: TRS (Tool Registry Service, implemented by Dockstore) standardizes discovery, WES standardizes cross-platform execution - the strongest reproducibility+portability+provenance story of the four systems.

## Run commands

```bash
cwltool --validate wf.cwl                     # static type-check the contract; no compute
cwltool wf.cwl job.yml                         # run locally (reference runner)
cwltool --singularity wf.cwl job.yml           # swap container runtime (Apptainer is Singularity-compatible)
cwltool --pack wf.cwl > packed.cwl             # bundle a multi-file workflow into one shareable JSON
cwltool --provenance ro/ wf.cwl job.yml        # emit a CWLProv Research Object
toil-cwl-runner --batchSystem slurm wf.cwl job.yml   # same document, at HPC scale
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "CWL is slow / can't scale" | ran cwltool (reference runner, single-node, slow by design) | run the same document on Toil/Arvados/Calrissian; do not equate runner limits with the spec |
| "index not found" at runtime (e.g. no `.bai`/`.fai`) | secondaryFiles not declared, so the runner staged the primary but not its index | declare `secondaryFiles` on the indexed File input (and output) |
| `genome.fasta.dict` produced instead of `genome.dict` | forgot the caret; `.dict` appends, `^.dict` strips one extension | use `^.dict` (each `^` strips one extension) |
| Intermittent OOM / undersized node on a heavy step | `ResourceRequirement` placed under `hints` (advisory, may be ignored) | move anything that MUST hold under `requirements` |
| Validation error on a workflow output | used `outputBinding.glob` on a workflow output | workflow outputs wire via `outputSource: step/out`; only tool outputs use `outputBinding` |
| Scatter runs but produces N x M or wrong-shaped output | wrong scatterMethod (dotproduct vs flat_/nested_crossproduct) | pick deliberately: dotproduct=zip, flat_/nested_=all pairs (flat vs nested output) |
| Works on cwltool, fails/differs on another engine | `${...}` JS or `cwltool:`/`arv:` extension the target lacks; graded conformance | prefer `$(...)`; keep engine extensions in hints; test the real target |
| "ScatterFeatureRequirement not specified" | used `scatter:` without the feature flag | add `requirements: [ScatterFeatureRequirement]` |
| Non-reproducible result across time | mutable `:latest` container tag | pin `DockerRequirement` by `@sha256:` digest |

## Related Skills

- workflow-management/wdl-workflows - WDL/Cromwell alternative for the Terra/GATK ecosystem
- workflow-management/nextflow-pipelines - reactive-dataflow alternative with the nf-core catalog
- workflow-management/snakemake-workflows - Python/file-pattern alternative for single-lab HPC
- workflows/fastq-to-variants - an end-to-end variant-calling pipeline these engines orchestrate

## References

- Crusoe MR, Abeln S, Iosup A, et al. 2022. Methods Included: Standardizing Computational Reuse and Portability with the Common Workflow Language. *Commun ACM* 65(6):54-63. DOI 10.1145/3486897.
- Amstutz P, Crusoe MR, Tijanic N, et al. 2016. Common Workflow Language, v1.0. figshare. DOI 10.6084/m9.figshare.3115156.v2.
- Khan FZ, Soiland-Reyes S, Sinnott RO, Lonie A, Goble C, Crusoe MR. 2019. Sharing interoperable workflow provenance: a review of best practices and their practical application in CWLProv. *GigaScience* 8(11):giz095. DOI 10.1093/gigascience/giz095.
- Wratten L, Wilm A, Göke J. 2021. Reproducible, scalable, and shareable analysis pipelines with bioinformatics workflow managers. *Nat Methods* 18:1161-1168. DOI 10.1038/s41592-021-01254-9.
<!-- END FILE: workflow-management/cwl-workflows/SKILL.md -->

## 子目录：workflow-management/nextflow-pipelines

<!-- BEGIN FILE: workflow-management/nextflow-pipelines/SKILL.md -->
---
name: bio-workflow-management-nextflow-pipelines
description: Authors reproducible Nextflow DSL2 pipelines built on reactive dataflow, where processes communicate only through channels and execution order is not guaranteed. Use when deciding channel/dataflow (Nextflow) vs rule-based (Snakemake) authoring; wiring queue vs value channels and fixing shared-reference exhaustion with .first(); composing DSL2 modules and subworkflows with take/main/emit; selecting container/conda profiles and pinning images by digest for portability across local/SLURM/LSF/AWS Batch/Google Batch/Kubernetes executors; diagnosing why -resume misses the cache (nondeterministic input order, mtime on network filesystems, mutable :latest tags) with cache 'lenient' and -dump-hashes; managing work/ vs publishDir and dynamic retry escalation; and choosing whether to adopt an nf-core community pipeline or author from scratch.
tool_type: cli
primary_tool: Nextflow
---

## Version Compatibility

Reference examples tested with: Nextflow 24.04+, fastp 0.23+, Salmon 1.10+, MultiQC 1.21+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: Nextflow is DSL2-only (DSL1 was removed in 22.12) and calendar-versioned (24.x/25.x), so any single-script DSL1 tutorial is dead. The `nf-validation` plugin is deprecated in favor of `nf-schema`. A strict, statically-analyzable syntax (VS Code language server) is opt-in now and default in a later release; writing to it future-proofs a pipeline. Pin container images by immutable digest (`@sha256:`), never a moving tag such as `:latest`, or both reproducibility and `-resume` break.

# Nextflow Pipelines

**"Build a scalable, reproducible pipeline with Nextflow"** -> Wire containerized processes together with asynchronous channels (reactive dataflow), so the engine fires each task as soon as its inputs are ready, caches completed tasks for `-resume`, and moves unchanged across executors by swapping a profile.
- CLI: `nextflow run main.nf -profile docker -resume`
- Groovy: DSL2 `process` / `workflow` / channel-operator syntax

## The governing principle: Nextflow is reactive dataflow - processes talk ONLY through channels, execution order is NOT guaranteed

Nextflow is push-model dataflow: processes are pure functions wired together by asynchronous channels, every channel item is a future, and a process fires a task the instant a complete set of inputs is available on ALL its input channels. There is no target file, no backward DAG, no filename-to-rule matching. This is the opposite of Snakemake/CWL/WDL, which are pull/goal-oriented (name a target output, the engine walks a dependency DAG backward to decide what runs). Almost every downstream trap traces back to this one axis:

- The model ENABLES truly dynamic pipelines: a process emits N files computed at runtime, the next process fans out over all N, with no DAG known in advance. Pull engines need a checkpoint/scatter escape hatch for this.
- The COST is that "what will run" is not knowable by reading the script top-to-bottom. Independent branches interleave nondeterministically, so `SAMPLE_A` may finish after `SAMPLE_Z`. Never write logic that assumes order; carry an explicit sample key through the tuple instead.
- "Why did only the first sample run?" and "why did `-resume` re-run everything?" are the two most common support questions, and both are direct symptoms of the dataflow model (see queue-vs-value channels and cache-miss diagnosis below).

A second principle sits above the engine: the DAG buys reproducibility of workflow LOGIC and nothing else automatically (Wratten et al. 2021 *Nat Methods* 18:1161-1168). A clean pipeline over unpinned tools is NOT reproducible. Pin the software environment (container by digest, conda by lockfile), the reference data and params, and control thread/locale/arch leaks (Grüning et al. 2018 *Cell Syst* 6:631-635). The engine gives one layer; the author pins the rest.

## Decision: Nextflow vs the other engines

| Axis | Nextflow (DSL2) | Snakemake | WDL (Cromwell/miniwdl) | CWL |
|------|-----------------|-----------|------------------------|-----|
| Model | reactive dataflow (push, no target) | pull/goal (target -> backward DAG) | pull/goal (declared outputs) | pull/goal (typed, declared) |
| Dynamic DAG (shape depends on runtime data) | native, trivial | `checkpoints` (bolted on) | `scatter` (static-ish) | limited |
| Cloud/executor portability | best-in-class (swap by profile) | good (v8 plugins, catching up) | strong on GCP/Terra | via Toil/Arvados |
| Community pipelines | nf-core (largest, curated) | Workflow Catalog (smaller) | WARP (Broad) | limited |
| Best when | cloud/production, dynamic pipelines, want nf-core | Python shop, HPC, file-pattern logic | Terra/AnVIL, GATK best practices | vendor-neutral portability, regulated |

Honest take: Nextflow wins on executor portability, nf-core, and dynamic pipelines; Snakemake wins on approachability for Python users. Pick by the ecosystem to integrate with, not by benchmarks.

## Decision: queue vs value channel (THE #1 footgun)

| Need | Channel type | Create with | Exhaustion behavior |
|------|--------------|-------------|---------------------|
| One item consumed by one task (per-sample reads) | queue | `Channel.of`, `.fromPath`, `.fromFilePairs`, `.splitCsv` | consumed once, then empty forever |
| A shared value reused on EVERY task (a reference/index) | value (singleton) | `Channel.value(x)`, `.first()`, `.collect()`, or a bare param | read unlimited times, never exhausted |

The firing rule to memorize: a process launches a new task only when EVERY input channel can supply an item; when a queue input drains, no more tasks fire even if other inputs still have items. So a shared reference passed as a queue channel is consumed by the first sample and every later sample silently never runs (exit 0, no error). Corollary: if all of a process's inputs are value channels its outputs are value channels too; if any input is a queue channel the outputs are queue channels.

## Decision: operator selection (and the silent-data-loss traps)

| Operator | Does | Trap / when-wrong |
|----------|------|-------------------|
| `map` | transform each item | pure only; no I/O side effects |
| `collect` | ALL items -> one list item (queue -> value) | blocks until upstream closes; gathers inputs for one aggregating task (MultiQC) |
| `groupTuple` | group by key into `[key, [items]]` | bare form WAITS for the whole channel to close (serialization/deadlock); pass `size: N` or `groupKey(key, n)`; SORT the grouped list or resume breaks |
| `join` | inner-join two channels by key | SILENTLY DROPS non-matching keys by default; use `remainder: true` or `failOnMismatch: true` |
| `combine` | Cartesian product (optional `by:`) | intentional all-vs-all; distinct from `join` (1:1 merge) |
| `mix` | interleave channels into one | order not preserved; pool outputs before a `collect` |
| `branch` | route items to named sub-channels | the DSL2 idiom for conditional routing (single_end vs paired) |
| `first` | first item as a VALUE channel | THE queue -> value fix for shared references |
| `ifEmpty` | supply a default if empty | guards the "empty branch silently vanishes" trap |

## Decision: executor (the portability payoff)

| Target | `executor` | Best when | Watch |
|--------|-----------|-----------|-------|
| Laptop/dev | `local` | development, tiny data, `-stub` wiring tests | one machine only |
| On-prem HPC | `slurm`, `lsf`, `sge`, `pbs` | shared cluster, on-prem data | tune `queueSize`/`submitRateLimit`; `scratch true` on slow shared FS |
| Cloud batch | `awsbatch`, `google-batch`, `azurebatch` | elastic scale, no on-prem HPC | input localization copy dominates cost/time; Wave + Fusion cut it |
| Kubernetes | `k8s` | already running K8s | more setup overhead |

Never bake the executor into pipeline code; always set it in a profile so the same code moves across all of them.

## Process and DSL2 modules (take / main / emit)

A DSL2 module wraps one tool as a `process` and can be `include`d and called multiple times (aliased), which DSL1 could not. Subworkflows compose modules with named inputs/outputs.

```groovy
// modules/fastqc.nf -- one tool, reusable, tested in isolation
process FASTQC {
    tag "${meta.id}"                                   // meta map threads sample identity through every operator
    container 'quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0'  // pin an immutable tag/digest, never :latest
    label 'process_low'                                // maps to central resource config, decoupled from module code

    input:
    tuple val(meta), path(reads)                       // nf-core convention: [ meta, files ], meta = [id:'x', single_end:false]

    output:
    tuple val(meta), path('*.zip'), emit: zip          // meta round-trips so downstream always knows the sample

    script:
    """
    fastqc -t ${task.cpus} ${reads}
    """
}
```

```groovy
// subworkflows/qc.nf -- take/main/emit names the interface
include { FASTQC } from '../modules/fastqc'
include { MULTIQC } from '../modules/multiqc'

workflow QC {
    take:
    reads

    main:
    FASTQC(reads)
    MULTIQC(FASTQC.out.zip.collect())                  // collect() gathers all samples' zips into ONE aggregating task

    emit:
    report = MULTIQC.out.report                        // access as QC.out.report from the caller
}
```

## Channels: the shared-reference fix, explained

```groovy
workflow {
    reads_ch = Channel.fromFilePairs(params.reads)     // queue: [id, [r1, r2]] per sample -- consumed once each
    index_ch = Channel.fromPath(params.index)          // queue: ONE item, the shared index

    // BUG if written ALIGN(reads_ch, index_ch): the index is consumed by sample 1,
    // its queue is then empty, and samples 2..N silently never fire (exit 0, no error).
    // .first() converts the queue to a VALUE channel, reusable on every task invocation.
    ALIGN(reads_ch, index_ch.first())
}
```

## Resume: the task hash, and diagnosing a cache miss

`-resume` reuses a task only on an EXACT hit of the task hash, computed from the input file identities, the resolved `script` text, the container reference, and input values/params. A single-bit change in any component busts the cache and re-runs the task. The notorious silent causes:

- Nondeterministic input ordering (`collect`/`groupTuple`/glob expansion) -> the ordered list is part of the hash. Fix: `toSortedList()` or `.map{ k, v -> [k, v.sort()] }`.
- Mutable container tags (`:latest`, or a re-pushed version) -> pin by digest.
- mtime hashing on network filesystems (Lustre/NFS) -> `-resume` works locally but misses on the cluster. Fix: `cache 'lenient'` (hashes size + path, ignores mtime).
- Absolute paths, dates, `$RANDOM`, or `hostname` baked into the `script` string -> the script hash changes every run.
- A deleted or moved `work/` -> the hash hits the DB but the task dir is gone, forcing a re-run.

```groovy
process ALIGN {
    // 'lenient' skips mtime -- the single most useful resume fix on HPC/cloud shared filesystems.
    // 'deep' hashes full file CONTENT (slower, robust when metadata lies); 'false' never caches.
    cache 'lenient'
    // ...
}
```

Definitive diagnosis: run both executions with `-dump-hashes` and diff which hash component differed, or `nextflow log <run_name> -f hash,name,status,workdir` to compare per-task hashes across runs. Everything else is guessing.

## work/ is truth; publishDir is a side effect

Every task runs in an isolated `work/<hash>/` dir holding the real outputs plus the forensic trail (`.command.sh` resolved script, `.command.log`, `.exitcode`). That directory IS the pipeline's output store and the ONLY thing `-resume` reads. `publishDir` merely copies or symlinks SELECTED outputs to a human-friendly location, and its failure can be SILENT because the task itself exited 0 in `work/`. Consequences:

- `mode: 'symlink'` (default) breaks if `work/` is later deleted; `mode: 'copy'` is safe to delete afterward; `mode: 'move'` breaks `-resume` (the output leaves `work/`), so use it only for terminal outputs.
- Never `rm -rf work/` if a resume might be wanted; use `nextflow clean` (which prunes the cache DB consistently). "Outputs missing but the pipeline succeeded" almost always means looking in `publishDir` instead of `work/<hash>/`.

## Resources: dynamic retry escalation

```groovy
process BIG {
    // 137=SIGKILL/OOM, 143=SIGTERM (SLURM wall-time kill); the 130..145 signal band + 104 (transient I/O) retry, fail fast otherwise.
    errorStrategy { task.exitStatus in ((130..145) + 104) ? 'retry' : 'terminate' }
    maxRetries 3
    memory { 8.GB * task.attempt }                     // task.attempt is 1-based; escalates 8 -> 16 -> 24 -> 32 GB
    time   { 4.h  * task.attempt }                     // a transient OOM auto-escalates instead of killing the run

    script:
    """
    memory_intensive_command
    """
}
```

`errorStrategy` values are `'terminate'` (default), `'retry'`, `'ignore'` (drop the failed task's outputs and continue over survivors), and `'finish'` (graceful drain). The nf-core `process.resourceLimits` directive (Nextflow 24.04+, which replaced the pre-3.0 `check_max` pattern) clamps the escalated request to the machine/queue ceiling so `8.GB * task.attempt` never asks for more than a node has.

## Executors and profiles: portability

```groovy
// nextflow.config -- executor lives in a profile, never in the pipeline code
profiles {
    docker      { docker.enabled = true }
    singularity { singularity.enabled = true }
    slurm {
        process.executor = 'slurm'
        executor { queueSize = 100; submitRateLimit = '10/1min' }   // avoid hammering the scheduler
    }
    awsbatch {
        process.executor = 'awsbatch'
        aws.region = 'us-east-1'
    }
}

process {
    cpus = 2; memory = '4 GB'; time = '1h'             // sane defaults
    withLabel: 'process_high' { cpus = 16; memory = '64 GB'; time = '12h' }  // labels centralize per-tier tuning
}
```

Run with `-profile slurm,singularity` (comma-separated, NO spaces; later profiles override earlier).

## Adopt an nf-core pipeline before authoring

For any mainstream analysis (RNA-seq, variant calling, ATAC, methylation, amplicon), a curated `nf-core/<pipeline>` already encodes years of QC, containerized modules, nf-test regression tests, and institutional configs. Reinventing it is months of work and worse QC. Pin the revision: `nextflow run nf-core/rnaseq -r 3.14.0 -profile test,docker --outdir results`. DIY is justified only for genuinely novel logic. See workflow-management/nf-core-pipelines for running, configuring, and building samplesheets against community pipelines; this skill covers AUTHORING.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Only the first sample processed, exit 0, no error | shared reference on a queue channel, exhausted after task 1 | `.first()` / `Channel.value` on the reference |
| Pipeline hangs at a grouping step | `groupTuple` with no size on a channel that never closes | `size: N` or `groupKey(key, n)` |
| Some samples silently disappear mid-pipeline | `join` dropped non-matching keys | `remainder: true` or `failOnMismatch: true` |
| `-resume` re-runs everything | nondeterministic input order, or `:latest` tag, or mtime on network FS | sort inputs; pin container digest; `cache 'lenient'` |
| Resume works locally, misses on the cluster | mtime unreliable on Lustre/NFS | `cache 'lenient'` |
| Outputs missing but the pipeline "succeeded" | publishDir failed silently, or looked in publishDir not work/ | check `work/<hash>/`; use `mode: 'copy'` |
| Resume broken after cleanup | deleted `work/` | never `rm -rf work/`; use `nextflow clean` |
| OOM kills a long run near the end | fixed memory, no escalation | `memory { 8.GB * task.attempt }` + conditional retry |
| Wrong result, no error, after a base image update | mutable tag served a stale cache hit | pin by digest; `cache 'deep'` for critical inputs |
| Huge cloud bill / slow S3 pipeline | explicit stage-in/out copies of large files | Wave + Fusion (POSIX over object store) |
| `-profile test docker` ignores docker | space instead of comma | `-profile test,docker` |

## Related Skills

- workflow-management/nf-core-pipelines - Run and configure community pipelines (the RUNNING counterpart to this authoring skill)
- workflow-management/snakemake-workflows - Pull/goal-oriented alternative for Python shops and file-pattern logic
- workflows/rnaseq-to-de - End-to-end RNA-seq quantification to differential expression
- read-qc/quality-reports - QC steps a pipeline orchestrates (FastQC/MultiQC)

## References

- Di Tommaso P, Chatzou M, Floden EW, Prieto Barja P, Palumbo E, Notredame C. 2017. Nextflow enables reproducible computational workflows. *Nat Biotechnol* 35(4):316-319.
- Ewels PA, Peltzer A, Fillinger S, Patel H, Alneberg J, Wilm A, Garcia MU, Di Tommaso P, Nahnsen S. 2020. The nf-core framework for community-curated bioinformatics pipelines. *Nat Biotechnol* 38(3):276-278.
- Wratten L, Wilm A, Göke J. 2021. Reproducible, scalable, and shareable analysis pipelines with bioinformatics workflow managers. *Nat Methods* 18:1161-1168.
- Grüning B, Chilton J, Köster J, et al. 2018. Practical computational reproducibility in the life sciences. *Cell Syst* 6(6):631-635.
<!-- END FILE: workflow-management/nextflow-pipelines/SKILL.md -->

## 子目录：workflow-management/nf-core-pipelines

<!-- BEGIN FILE: workflow-management/nf-core-pipelines/SKILL.md -->
---
name: bio-workflow-management-nf-core-pipelines
description: Runs and configures curated nf-core community Nextflow pipelines (rnaseq, sarek, atacseq, methylseq, ampliseq, taxprofiler, fetchngs) reproducibly, pinning the pipeline revision with -r and selecting a container engine and institutional config via -profile. Use when deciding to adopt a community pipeline versus author one from scratch; picking a pipeline and pinning its -r revision; selecting -profile test/docker/singularity/conda plus an institutional config from nf-core/configs; building and validating a samplesheet CSV against the pipeline schema (nf-schema); choosing --genome/iGenomes versus custom references; configuring resources and max_memory for SLURM/AWS Batch; using -resume and -stub; and reading MultiQC outputs.
tool_type: cli
primary_tool: nf-core
---

## Version Compatibility

Reference examples tested with: Nextflow 24.04+, nf-core/tools 3.0+, Docker 24+ or Singularity 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `-r <tag>` pins the pipeline to an immutable release; without it `nextflow run nf-core/<pipe>` pulls whatever the mutable default branch is today, so results are not reproducible. Pin the container engine too (a pipeline release ships digest-pinned images; `-profile docker` uses them, `:latest` does not). Schema validation moved from the deprecated nf-validation plugin to nf-schema; a current pipeline uses nf-schema, so validate samplesheets against the pipeline's shipped schema, not a hand-written one.

# nf-core Pipelines

**"Run a curated community pipeline on my samples"** -> Select a versioned nf-core pipeline, pin its release, choose a container profile, validate a samplesheet against the pipeline schema, point it at references, and run it, reading the aggregated MultiQC report at the end.
- CLI: `nextflow run nf-core/<pipeline> -r <version> -profile <container>,<institution> --input samplesheet.csv --outdir results -resume`
- CLI: `nf-core pipelines list` / `nf-core pipelines download` (browse and cache pipelines)

## The governing principle: ADOPT a community pipeline before authoring a new one

For any mainstream analysis - RNA-seq, germline/somatic variant calling, ATAC-seq, ChIP-seq, methylation, amplicon/metagenomics, single-cell - a curated nf-core pipeline already encodes years of QC, edge-case handling, CI/nf-test regression tests, institutional configs for hundreds of HPCs, a standardized samplesheet+schema, and MultiQC reporting (Ewels 2020 *Nat Biotechnol* 38:276-278). Reinventing that in hand-written Nextflow is months of work and worse QC: the community pipeline has already found the bugs a bespoke version will rediscover, and it is maintained across every future tool update and reference build. The decision every biologist should default toward is ADOPT, not BUILD.

The corollary trap is treating "adopt" as "run once and trust the number". A community pipeline is only reproducible if the RUN is pinned: `-r` pins the pipeline version, the release's digest-pinned containers pin the software, `--genome`/reference URIs pin the reference data (Wratten et al. 2021 *Nat Methods* 18:1161-1168; Grüning et al. 2018 *Cell Syst* 6:631-635). An unpinned `nextflow run nf-core/rnaseq` on the default branch with a `:latest` engine is exactly as irreproducible as a hand-rolled script - the curation buys nothing if the invocation is loose. Author from scratch only for genuinely novel logic with no community pipeline, an unsupported combination of steps, or an institutional constraint no config can express (see workflow-management/nextflow-pipelines).

## Decision: adopt an nf-core pipeline vs author a new one

| Situation | Verdict | Why |
|-----------|---------|-----|
| Mainstream analysis with an existing nf-core pipeline (rnaseq, sarek, atacseq, ...) | ADOPT | Curated, CI-tested, institutional configs, MultiQC; DIY is worse QC |
| A supported pipeline plus a few extra params/references | ADOPT + configure | `-c custom.config`, `-params-file`, `--genome`; no authoring needed |
| Genuinely novel method, no community pipeline exists | BUILD | Author in Nextflow; still install tested nf-core modules, do not hand-write wrappers |
| An unsupported ORDER/combination of otherwise-standard steps | BUILD (or fork) | Scaffold with `nf-core pipelines create`; reuse `nf-core modules install` |
| One-off, few linear steps, single sample, single machine | Neither | A plain script is honest; a workflow manager is overhead below this threshold |

## Decision: which container profile by platform

| Platform | Profile | Why |
|----------|---------|-----|
| Laptop / workstation with Docker | `-profile docker` | Simplest; needs root/daemon; digest-pinned images from the release |
| Shared HPC (no root, has Singularity/Apptainer) | `-profile singularity` | Rootless; the default on most academic clusters |
| Cluster allowing Podman | `-profile podman` | Rootless Docker-compatible alternative |
| No container engine available at all | `-profile conda` | Last resort; slower, less reproducible than a pinned image |
| Named institution in nf-core/configs (uppmax, crick, ...) | `-profile singularity,<institution>` | Institutional config sets executor, queues, `max_memory`; comma, no space |
| Smoke test before real data | `-profile test,docker` | Ships a tiny public dataset; proves the install end-to-end in minutes |

Profiles are comma-separated with NO spaces and applied left-to-right (later overrides earlier), so `-profile test,docker` runs the test dataset under Docker, and `-profile singularity,uppmax` layers the institutional config over Singularity.

## Decision: --genome/iGenomes vs custom references

| Reference source | Use when | Caveat |
|------------------|----------|--------|
| `--genome GRCh38` (iGenomes) | A standard build suffices and convenience matters | iGenomes builds are frozen/aging; the annotation may lag current releases |
| Explicit `--fasta` + `--gtf` (+ `--gff`) | A specific build/patch or a non-model organism is needed | Pin the exact reference version; record its URI for provenance |
| Pipeline builds its own index vs `--<tool>_index` | Reusing an index across runs saves hours | A stale index built from a different FASTA silently corrupts results |

The reference layer is a reproducibility layer in its own right: `--genome GRCh38` without a recorded iGenomes snapshot pins less than an explicit `--fasta`/`--gtf` URI pair. Prefer explicit references and record their source when the result must be reproduced.

## The run pattern (pin everything)

```bash
# Smoke test first: tiny public dataset proves the install + engine end to end.
nextflow run nf-core/rnaseq -r 3.14.0 -profile test,docker --outdir results_test

# Real run: -r pins the release, -profile picks the engine, --input is the samplesheet.
nextflow run nf-core/rnaseq -r 3.14.0 \
    -profile singularity \
    --input samplesheet.csv \
    --genome GRCh38 \
    --outdir results \
    -resume
```

- `-r 3.14.0` is the pipeline REVISION (a git tag). It is MANDATORY: without it the run tracks the mutable default branch and is not reproducible.
- `-profile singularity` selects the container engine (comma-add an institutional config: `-profile singularity,uppmax`).
- Single-dash options (`-r`, `-profile`, `-resume`, `-c`, `-params-file`) are NEXTFLOW options; double-dash options (`--input`, `--genome`, `--outdir`, `--max_memory`) are PIPELINE parameters. Mixing up the dash count is the most common invocation error.
- Config precedence, low to high: the pipeline's built-in `nextflow.config` -> `conf/base.config` -> selected profiles -> `-c custom.config` -> `-params-file params.yaml` -> a `--param` on the command line. A later source overrides an earlier one.

Parameters can be supplied in a YAML/JSON file instead of long command lines, which is the reproducible-provenance form:

```yaml
# params.yaml  (nextflow run nf-core/rnaseq -r 3.14.0 -profile singularity -params-file params.yaml)
input: samplesheet.csv
genome: GRCh38
outdir: results
aligner: star_salmon
```

## The samplesheet and schema validation

Every nf-core pipeline reads a CSV samplesheet whose exact columns are defined by the pipeline's shipped schema (`assets/schema_input.json`) and validated by the nf-schema plugin at launch, before any compute is spent. Wrong or misordered columns fail fast with a schema error rather than hours in.

```csv
sample,fastq_1,fastq_2,strandedness
CONTROL_REP1,/data/ctrl1_R1.fastq.gz,/data/ctrl1_R2.fastq.gz,auto
CONTROL_REP2,/data/ctrl2_R1.fastq.gz,/data/ctrl2_R2.fastq.gz,auto
TREAT_REP1,/data/treat1_R1.fastq.gz,/data/treat1_R2.fastq.gz,auto
```

- Column names are pipeline-specific: nf-core/rnaseq uses `sample,fastq_1,fastq_2,strandedness`; nf-core/sarek uses `patient,sample,lane,fastq_1,fastq_2`. Read the pipeline's `docs/usage.md` for the exact schema, never guess.
- A single-end sample leaves `fastq_2` empty; multiple rows sharing one `sample` value are merged (technical replicates / multiple lanes), which is how the pipeline knows to concatenate them.
- Absolute paths or URLs are safest; relative paths resolve against the launch directory.

Threading columns into the pipeline is handled by the META MAP convention (worth understanding when reading logs or outputs): each sample flows internally as a tuple `[ meta, files ]` where `meta` is a map like `[ id:'CONTROL_REP1', single_end:false ]`. The samplesheet columns become `meta` keys, so sample identity and pairing travel WITH the files through every step - which is why outputs and the MultiQC report are labelled by the `sample` value from the sheet.

## Institutional configs and resource limits

nf-core/configs supplies ready-made profiles for hundreds of clusters (executor, queues, module system, resource ceilings). Use a named one when it exists; otherwise write a small custom config.

```groovy
// custom.config  (nextflow run ... -c custom.config)
process {
    executor = 'slurm'
    queue    = 'normal'
    // Clamp per-process resource escalation to the real node ceiling, so an auto-retry that
    // doubles memory never requests more than a node has. resourceLimits is the nf-core/tools 3.0+
    // form (Nextflow 24.04+); it replaced the deprecated params.max_cpus/max_memory/max_time + check_max().
    resourceLimits = [ cpus: 32, memory: 128.GB, time: 48.h ]
}
```

- nf-core pipelines escalate resources on retry (a task that OOM-kills retries with more memory); `process.resourceLimits` caps that escalation so a request stays schedulable. A pipeline built on the pre-3.0 template instead reads `params.max_cpus`/`max_memory`/`max_time` (the `check_max()` pattern, deprecated and removed from the template in tools 3.0) - match whichever the pinned `-r` release ships. Set the ceiling to the real node/queue limits either way.
- Do not edit the pipeline's own `conf/base.config`; layer overrides through `-c custom.config` so the pipeline stays a clean, updatable checkout.

## Resume, stub, and previewing the plan

```bash
# -resume reuses cached tasks whose inputs+script+container hash is unchanged.
nextflow run nf-core/rnaseq -r 3.14.0 -profile singularity --input samplesheet.csv --outdir results -resume

# -stub runs each process's stub block (touch fake outputs) to validate wiring in seconds.
nextflow run nf-core/rnaseq -r 3.14.0 -profile test,docker --outdir results -stub
```

- `-resume` keys on a hash of each task's inputs, resolved script, and container reference. On a network filesystem (Lustre/NFS) unreliable mtimes cause spurious cache misses; the standard fix is `cache 'lenient'` in a custom config. Deleting `work/` destroys the resume cache - a re-run then recomputes everything.
- `-stub` validates that the samplesheet, profile, and channel wiring are correct without running any tool, which is the fast pre-flight before committing an HPC allocation.

## Building a new pipeline (only when adoption does not fit)

```bash
# Scaffold a standardized pipeline (template, CI, lint, nf-test) - current tools syntax.
nf-core pipelines create

# Install a pre-written, tested module instead of hand-writing a tool wrapper.
nf-core modules install fastqc
nf-core subworkflows install bam_sort_stats_samtools

# Lint against the template and run the module's nf-test snapshot tests.
nf-core pipelines lint
nf-core modules test fastqc
```

Even when building, reuse the community's tested modules rather than hand-writing bwa/samtools/fastqc wrappers. Authoring mechanics (channels, DSL2, resume internals) live in workflow-management/nextflow-pipelines.

## Interpreting MultiQC output

Every nf-core run aggregates per-tool QC into a single `multiqc_report.html` under the output directory (plus parsed `multiqc_data/` tables). Read it before trusting any downstream result:

- The General Statistics table is per-sample; scan for an outlier column (low aligned %, high duplication, skewed GC, adapter content) that flags a failed library BEFORE it contaminates differential analysis.
- Section order mirrors the pipeline steps (e.g. FastQC -> trimming -> alignment -> quantification for rnaseq); a section missing for one sample means that sample failed a step - cross-check the Nextflow log.
- MultiQC reports what the tools measured; it does not decide pass/fail. Set thresholds from the assay, and treat the report as the triage surface, not the verdict (read-qc/quality-reports).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Results differ between runs / cannot reproduce a published run | no `-r`, so the mutable default branch was used | always pin `-r <version>`; record it alongside results |
| `Unknown configuration profile` or only one profile applied | `-profile test docker` with a space | use a comma, no space: `-profile test,docker` |
| Launch fails immediately with a schema/validation error | samplesheet columns wrong, misordered, or misnamed for this pipeline | match the pipeline's `assets/schema_input.json` / `docs/usage.md` exactly |
| `--input` or `--genome` "is not a valid parameter" | used a single dash (`-input`) - that is a Nextflow option namespace | pipeline params take double dash; Nextflow options (`-r`, `-profile`, `-resume`) take single |
| `-resume` re-runs everything on the cluster | mtime-based cache misses on a network filesystem | add `cache 'lenient'` via `-c custom.config`; never delete `work/` |
| Container/tool "command not found" at runtime | no container engine profile selected (bare `nextflow run`) | add `-profile docker`/`singularity`/`conda` |
| Task unschedulable, requests more memory than any node | retry escalation exceeded the node ceiling | set `process.resourceLimits = [cpus:, memory:, time:]` (pre-3.0 pipelines: `params.max_memory`/`max_cpus`/`max_time`) |
| Wrong/aging annotation with `--genome` | iGenomes builds are frozen and can lag current releases | supply explicit `--fasta`/`--gtf` for a specific build and record the URI |

## Related Skills

- workflow-management/nextflow-pipelines - Author a Nextflow pipeline from scratch when no community pipeline fits
- workflow-management/snakemake-workflows - Rule-based alternative engine for pipeline authoring
- workflows/rnaseq-to-de - Take an nf-core/rnaseq count matrix into differential expression
- read-qc/quality-reports - Interpret the FastQC/MultiQC QC surface a pipeline emits

## References

- Ewels PA, Peltzer A, Fillinger S, Patel H, Alneberg J, Wilm A, Garcia MU, Di Tommaso P, Nahnsen S. 2020. The nf-core framework for community-curated bioinformatics pipelines. *Nat Biotechnol* 38(3):276-278.
- Di Tommaso P, Chatzou M, Floden EW, Prieto Barja P, Palumbo E, Notredame C. 2017. Nextflow enables reproducible computational workflows. *Nat Biotechnol* 35(4):316-319.
- Wratten L, Wilm A, Göke J. 2021. Reproducible, scalable, and shareable analysis pipelines with bioinformatics workflow managers. *Nat Methods* 18:1161-1168.
- Grüning B, Chilton J, Köster J, et al. 2018. Practical computational reproducibility in the life sciences. *Cell Syst* 6(6):631-635.
<!-- END FILE: workflow-management/nf-core-pipelines/SKILL.md -->

## 子目录：workflow-management/snakemake-workflows

<!-- BEGIN FILE: workflow-management/snakemake-workflows/SKILL.md -->
---
name: bio-workflow-management-snakemake-workflows
description: Authors reproducible bioinformatics pipelines with Snakemake - rules wired by output-file pattern, wildcards and expand() for sample fan-out, checkpoints for runtime-unknown outputs, resource/retry escalation, and conda/container software deployment on HPC and cloud. Use when deciding rule-based (Snakemake) vs channel/dataflow (Nextflow) authoring; wiring rules by OUTPUT-file pattern rather than imperative order; using wildcards + expand() for sample fan-out and constraining them to stop silent mis-routing; adding checkpoints when the set of outputs is unknown until a step runs (dynamic DAG); diagnosing why a job reran (or did not) under the mtime-plus-provenance trigger set; escalating memory on retry for OOM-killed jobs; and porting a Snakemake 7 `--cluster`/remote-provider command to the Snakemake 8+ executor-plugin and storage-plugin model (snakemake-executor-plugin-slurm) with `--software-deployment-method`.
tool_type: python
primary_tool: Snakemake
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: Snakemake 8.0+, Python 3.11+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: Snakemake 8 (Jan 2024) removed `--cluster`, `--drmaa`, and the `*RemoteProvider` classes from core and moved them to pip-installable EXECUTOR plugins (`--executor slurm`, package `snakemake-executor-plugin-slurm`) and STORAGE plugins (`storage.s3(...)`, `snakemake-storage-plugin-s3`). `--use-conda`/`--use-singularity` became `--software-deployment-method` / `--sdm conda apptainer`. A Snakemake 7 command line does not run unchanged on 8/9. Run `snakemake --version` FIRST and branch all execution guidance on 7 vs 8/9.

# Snakemake Workflows

**"Build a reproducible bioinformatics pipeline with Snakemake"** -> Declare each step as a rule that says "a file matching THIS output pattern is produced FROM those inputs", let the engine resolve the DAG backward from requested targets, fan out over samples with wildcards, and pin the software environment so the result reproduces next year.
- Python: Snakefile `rule`/`checkpoint` blocks with `expand()`, `wildcards`, `config`, `resources`, and `conda:`/`container:` (Snakemake)

## The governing principle: Snakemake is pull/goal-oriented - it builds a STATIC DAG backward from requested target files

Snakemake is a pull, make-like engine. An author does NOT describe a forward flow of data. Each `rule` is a pattern-matched recipe ("a file that looks like THIS can be produced FROM that"), and the engine takes the requested target files and works BACKWARD, unifying wildcards by string-matching output filename patterns, until it reaches files already on disk. The whole plan - a static DAG - is computed at parse time, before a single job runs (Köster & Rahmann 2012 *Bioinformatics* 28:2520-2522). Almost every Snakemake bug a biologist hits is a downstream consequence of this one model:

- Rules are wired by OUTPUT-FILE PATTERN, not call order. A missing or typo'd output path silently drops a rule from the DAG - there is no error, the job just never runs. Debugging "why didn't it run" means tracing the backward dependency from the target, not reading top-to-bottom.
- Because the plan is fully known up front, `snakemake -n` (dry run), `--dag`, and `--report` are first-class. This is the payoff of the static model. Nextflow's reactive-dataflow model (processes connected by asynchronous channels, DAG emerges at runtime) has no true dry-run - hold both models in mind and most "why did/didn't it run" questions answer themselves.
- Data-dependent branching is impossible in the base model. If the NUMBER or identity of outputs is unknown until a step runs (split into one file per detected cluster, scatter over however many contigs an assembler emits), the static DAG cannot represent it -> that is exactly what CHECKPOINTS exist for. A biologist who thinks "the pipeline decides at runtime how many chunks" is fighting the paradigm and needs a checkpoint, not a clever `run:` block.
- A workflow manager buys reproducible LOGIC and nothing else automatically. The DAG being deterministic says nothing about tool versions. A rule with no `conda:`/`container:` runs against whatever is on `$PATH`; "reproducible" is unearned until the software environment is pinned (Grüning et al. 2018 *Cell Syst* 6:631-635). Pin containers by DIGEST and conda by LOCKFILE - see Software Deployment below.

## Decision: Snakemake vs Nextflow (pick by team and infrastructure, not benchmarks)

| Dimension | Snakemake | Nextflow | Best when |
|-----------|-----------|----------|-----------|
| Model | pull/make, static DAG at parse time | push/reactive dataflow, dynamic DAG | Snakemake: the plan must be visible before committing an allocation |
| Language | Python DSL (real Python + pandas in the Snakefile) | Groovy DSL | Snakemake: Python-native lab, file-pattern logic |
| Dry run / DAG viz | first-class (`-n`, `--dag`, `--report`) | no true dry-run (`-stub`/`-preview` check wiring only) | Snakemake: HPC where a bad plan is expensive |
| Data-dependent branching | needs checkpoints (escape hatch) | native (channels) | Nextflow: shape depends on runtime data |
| Community pipelines | Workflow Catalog / wrappers (smaller) | nf-core (large, curated) | Nextflow: run a maintained pipeline as-is |
| Sweet spot | single-lab reproducible research, HPC, tight Python integration | cloud/production, multi-institution, nf-core stacks | choose by the ecosystem to integrate with |

Reuse before authoring: for a mainstream analysis (RNA-seq, variant calling, ATAC-seq), a curated community pipeline already encodes years of QC and edge cases. Adopting one means RUNNING it (e.g. nf-core/rnaseq via workflow-management/nf-core-pipelines), not authoring Groovy - so a Python-shop preference for Snakemake only decides the authoring case, not whether to build at all. Author from scratch only for a novel method or an unsupported combination of steps.

## Decision: rerun triggers - why a job reran, or did not

Since Snakemake 7.8 the default is NOT pure mtime. A rerun fires on a SET of triggers: `{mtime, params, input, code, software-env}` (Mölder et al. 2021 *F1000Research* 10:33). This surprises everyone upgrading from old Snakemake.

| Want | Use |
|------|-----|
| classic Make behavior, minimize surprise reruns | `--rerun-triggers mtime` |
| max reproducibility (default) | all five triggers |
| ignore a stable reference's timestamp | `ancient("ref.fa")` on that input |
| mark results current without recompute | `--touch` |
| force specific rules | `--forcerun rule` / `-R` |
| see what WOULD rerun and why | `snakemake -n -R` / `--list-changes code` |

The `code` trigger catches shell/script/run body changes - reformatting whitespace or editing a comment counts as a code change and reruns the job. On very large DAGs or multi-TB inputs the provenance triggers add a hashing/stat storm; `--rerun-triggers mtime` skips it.

## Decision: run vs script vs shell vs notebook vs wrapper

| Situation | Pick | Why |
|-----------|------|-----|
| call a CLI tool (samtools, bwa) | `shell:` | subprocess, conda/container-isolated |
| reusable Python/R analysis needing isolation | `script:` | separate process, `snakemake` object injected |
| standard tool, do not want to write shell | `wrapper:` (PINNED tag) | maintained, ships its own env |
| exploratory, want a re-runnable notebook | `notebook:` | params injected, `--edit-notebook` |
| trivial in-Snakefile glue only | `run:` | NEVER heavy work |

`run:` executes IN the main Snakemake process - it shares the interpreter and GIL, cannot be conda/container-isolated (the `conda:` directive is disallowed with `run:`), blocks the scheduler, and an OOM in it takes down the whole workflow. Move anything beyond trivial glue to `script:`.

## Decision: execution backend (Snakemake 8/9)

| Target | Command |
|--------|---------|
| laptop/workstation | `snakemake --cores N --sdm conda` |
| SLURM (native) | `pip install snakemake-executor-plugin-slurm` then `--executor slurm --jobs N --default-resources` |
| SLURM (legacy sbatch string) | `pip install snakemake-executor-plugin-cluster-generic` then `--executor cluster-generic --cluster-generic-submit-cmd "sbatch ..."` |
| S3/GCS I/O | `pip install snakemake-storage-plugin-s3` then `--default-storage-provider s3 --default-storage-prefix s3://.../` |
| thousands of tiny jobs | add `group:` / `--group-components` to collapse scheduler overhead |

Porting a v7 `--cluster "sbatch --account=X --partition=Y --mem=Z --time=T"` command: for the native `slurm` executor, map those sbatch flags to resource keys (`slurm_account`, `slurm_partition`, `mem_mb`, `runtime` in minutes) set per-rule in `resources:` or globally via `--default-resources`; for a drop-in port keep the old string under `cluster-generic` (its own plugin, above). `--cores` = local cores; `--jobs`/`-j` = number of concurrent cluster/cloud jobs (in v8 these are separate). Profiles are versioned: the file is `config/config.v8+.yaml`, every long option becomes a YAML key.

## Rules, wildcards, and expand

`expand()` returns a LIST of strings by combinatorial substitution - it does NOT touch the filesystem. Use it to enumerate targets in `rule all`.

```python
configfile: 'config/config.yaml'
SAMPLES = config['samples']

rule all:                                              # the requested targets; the DAG is built backward from here
    input:
        expand('results/{sample}.bam', sample=SAMPLES)

rule align:
    input:
        r1 = 'data/{sample}_R1.fq.gz',
        r2 = 'data/{sample}_R2.fq.gz',
        index = 'ref/genome.fa'
    output:
        bam = 'aligned/{sample}.bam'                   # this OUTPUT PATTERN, matched against the target, wires the rule in
    threads: 8
    log:
        'logs/align/{sample}.log'
    shell:
        'bwa mem -t {threads} {input.index} {input.r1} {input.r2} | '
        'samtools sort -@ {threads} -o {output.bam} 2> {log}'
```

## Wildcard constraints - stop silent mis-routing

Wildcards are greedy regex string-unification (`{sample}` compiles to `.+`), not typed parameters. An unconstrained wildcard swallows path separators and adjacent tokens: `data/{sample}.txt` matches `data/a/b.txt` as `sample=a/b`, and `{a}.{b}.txt` on `101.B.normal.txt` has no unique parse. The failure is silent mis-routing, not an error. Constrain whenever a value can contain `/`, `.`, or `_`, or a filename has multiple variable tokens.

```python
wildcard_constraints:
    sample = '[^/]+',                                  # no path separators
    chrom = r'\d+|X|Y|MT'                              # only real chromosome tokens

# two rules whose output patterns can both produce a requested file raise AmbiguousRuleException;
# prefer non-overlapping constraints to disambiguate, and fall back to `ruleorder: a > b` only if needed.
```

## Checkpoints - the ONLY data-dependent-DAG mechanism

**Goal:** produce downstream jobs for a set of files whose number and identity are unknown until a step runs (split a FASTA into one file per detected cluster; scatter over an assembler's contigs).

**Approach:** declare the producing step a `checkpoint` with a `directory()` output; in an input function on the AGGREGATING rule, call `checkpoints.<name>.get(**wildcards)` FIRST - its exception is what forces the engine to run the checkpoint and RE-EVALUATE the DAG - then `glob_wildcards` the checkpoint's declared output dir and `expand()` the real targets.

```python
checkpoint split_fasta:
    input:
        'data/all.fasta'
    output:
        directory('split/{sample}')                    # directory() because the file set is unknowable at parse time
    shell:
        'split_by_cluster.py {input} split/{wildcards.sample}'

def gather_clusters(wildcards):
    # .get() RAISES until the checkpoint has run; that exception drives DAG re-evaluation.
    # Omitting it globs at parse time (empty), so the aggregation silently gets zero inputs - the classic bug.
    ckpt_dir = checkpoints.split_fasta.get(**wildcards).output[0]
    ids = glob_wildcards(f'{ckpt_dir}/{{id}}.fasta').id
    return expand('processed/{sample}/{id}.done', sample=wildcards.sample, id=ids)

rule aggregate:                                         # the input function MUST be attached to the rule that consumes the set
    input:
        gather_clusters
    output:
        'results/{sample}_summary.txt'
    shell:
        'cat {input} > {output}'
```

Point `glob_wildcards` at the checkpoint's declared `directory()` output (a fresh dir) so stale files do not leak into the glob. Prefer one scatter->gather to chains of nested checkpoints.

## Resources, escalating retries, and grouping

Resource callables differ by directive: `resources` is `callable(wildcards [, input] [, threads] [, attempt])`; `threads` is `callable(wildcards [, input])` only; getting the signature wrong is a top error source. `runtime` is in MINUTES. `attempt` starts at 1 and increments per retry - the canonical fix for OOM-killed jobs.

```python
rule call_variants:
    input:
        bam = 'aligned/{sample}.bam'
    output:
        'results/{sample}.vcf'
    threads: 4
    retries: 3                                          # or global --retries 3
    resources:
        mem_mb = lambda wildcards, attempt: 8000 * attempt,   # 8 GB, doubling to 16/24 on OOM restart
        runtime = 240                                   # MINUTES, not seconds; SLURM wall-time
    log:
        'logs/call/{sample}.log'
    shell:
        'variant_caller --threads {threads} {input.bam} > {output} 2> {log}'
```

For thousands of tiny jobs on HPC, per-job scheduler latency dominates: assign rules a `group:` (or `--group-components rule=N`) so they submit as one job. `temp('x.bam')` deletes an intermediate once all consumers are done (huge for disk); `ancient('ref.fa')` excludes an input from mtime-based rerun decisions.

## Software deployment - the layer that makes it reproducible

A clean DAG over unpinned tools is not reproducible. The engine gives layer 1 (logic); the author must pin the software environment. Declare `conda:` (a pinnable file) or `container:` per rule, and activate deployment at run time.

```python
rule fastqc:
    input:
        'data/{sample}.fq.gz'
    output:
        'qc/{sample}_fastqc.html'
    conda:
        'envs/qc.yaml'                                  # a FILE (pinnable), not a bare named env
    container:
        # PIN BY DIGEST, never a mutable tag - :latest or a re-pushed :0.7.17 silently changes the tool and busts the cache
        'docker://quay.io/biocontainers/fastqc@sha256:<digest>'
    shell:
        'fastqc {input} -o qc/'
```

```bash
snakemake --sdm conda --cores 8                         # build per-rule conda envs (was --use-conda in v7)
snakemake --sdm apptainer --cores 8                     # run each rule in its container (was --use-singularity)
snakemake --sdm conda apptainer --cores 8               # containerized conda: build the env INSIDE the pinned image
```

A bare `environment.yml` with `samtools` (no version) resolves differently over time; pin exact builds with a lockfile (conda-lock) for bit-reproducibility. `--containerize` auto-generates a Dockerfile baking all conda envs into one image. Between-workflow caching (`cache: True` + `SNAKEMAKE_OUTPUT_CACHE`) reuses results across workflows but ONLY for deterministic rules - a nondeterministic tool poisons the shared cache with wrong results silently.

## Modularization and reuse

`include: 'rules/x.smk'` is textual inclusion sharing one namespace. For genuine composition of published workflows, use the module system (`module other: snakefile: '...'; use rule * from other as other_*`), which can import, prefix, and override rules. `wrapper: 'v5.0.2/bio/bwa/mem'` pulls a maintained, conda-shipping wrapper - PIN the leading version tag; an unpinned wrapper drifts silently.

```python
include: 'rules/qc.smk'
include: 'rules/align.smk'

rule all:
    input:
        rules.qc_all.input,
        rules.call_all.input
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| A rule silently never runs | its output pattern does not match any requested target (typo/path); the DAG dropped it | trace backward from `rule all`; run `snakemake -n` and inspect the DAG; fix the output path |
| Wildcard captures too much / wrong sample | unconstrained greedy `.+` swallowed a delimiter or path separator | add `wildcard_constraints` (e.g. `sample='[^/]+'`) |
| Aggregation after a split has zero inputs | forgot `checkpoints.X.get()`, or globbed at parse time, or input function on the wrong rule | call `.get(**wildcards)` first, glob the checkpoint's `directory()` output, attach the function to the consumer |
| Everything reruns after a cosmetic edit | the `code` trigger - editing the shell/script body (even whitespace) counts | expected under provenance triggers; use `--rerun-triggers mtime` to opt out |
| Expected a rerun, got none | old mtime mental model, or output is newer than input | check triggers; `--forcerun rule` / `-R` |
| `--cluster`/`S3RemoteProvider` errors on v8 | removed from core in Snakemake 8 | install the executor/storage plugin; use `--executor slurm` and `storage.s3(...)` |
| OOM-killed job (exit 137) | static `mem_mb` too low for the largest sample | `retries` + `mem_mb=lambda wildcards, attempt: base*attempt` |
| Per-job scheduler meltdown on HPC | thousands of tiny jobs, submission overhead dominates | `group:` / `--group-components` to batch into one submission |
| `MissingOutputException` on NFS/Lustre | networked filesystem lags after a job finishes | raise `--latency-wait` |
| Workflow refuses to continue after a killed job ("Incomplete files") | a job died mid-write (SLURM kill, node crash), so its outputs are flagged incomplete | re-run with `--rerun-incomplete` (`--ri`); this is Snakemake's crash-resume, distinct from the rerun triggers |
| Heavy `run:` block hangs the workflow | runs in the main process, shares the GIL, no isolation | move to `script:` |
| "Reproducible" but results differ on a colleague's cluster | no `--sdm`, or a mutable `:latest` container tag | declare `conda:`/`container:`, pin by digest + conda lockfile |

## Related Skills

- workflow-management/nextflow-pipelines - The reactive-dataflow alternative; author here when the DAG must emerge from runtime data
- workflow-management/nf-core-pipelines - Run a curated community Nextflow pipeline instead of authoring from scratch
- workflows/rnaseq-to-de - End-to-end RNA-seq-to-differential-expression pipeline this engine can orchestrate
- read-qc/quality-reports - The QC step a pipeline wraps as an early rule
- read-alignment/bwa-alignment - The alignment tool invoked inside a Snakemake `shell:` rule

## References

- Köster J, Rahmann S. 2012. Snakemake - a scalable bioinformatics workflow engine. *Bioinformatics* 28(19):2520-2522.
- Mölder F, Jablonski KP, Letcher B, et al. 2021. Sustainable data analysis with Snakemake. *F1000Research* 10:33.
- Grüning B, Chilton J, Köster J, et al. 2018. Practical computational reproducibility in the life sciences. *Cell Systems* 6(6):631-635.
- Di Tommaso P, Chatzou M, Floden EW, et al. 2017. Nextflow enables reproducible computational workflows. *Nature Biotechnology* 35(4):316-319.
<!-- END FILE: workflow-management/snakemake-workflows/SKILL.md -->

## 子目录：workflow-management/wdl-workflows

<!-- BEGIN FILE: workflow-management/wdl-workflows/SKILL.md -->
---
name: bio-workflow-management-wdl-workflows
description: Authors bioinformatics pipelines in WDL (Workflow Description Language) run by Cromwell or miniwdl, targeting the GATK/Broad and Terra/AnVIL/BioData Catalyst cloud ecosystem, with tasks, workflows, scatter-gather parallelism, structs, and a runtime block that sizes the cloud VM. Use when deciding to target Terra/AnVIL/GATK/WARP (chosen for the ecosystem, not the language); sizing runtime disks dynamically for a fresh-per-task cloud VM (ceil(size(f)*factor)+buffer); choosing preemptible vs on-demand VMs by task length and idempotency; picking Cromwell (production, cloud, call-caching) vs miniwdl (local dev, miniwdl check linting, readable errors); enabling and debugging call-caching silent-miss modes; pinning Docker by digest for reproducibility and cache stability; or scattering an array for parallel fan-out.
tool_type: cli
primary_tool: cromwell
---

## Version Compatibility

Reference examples tested with: Cromwell 87+, miniwdl 1.12+, WDL spec 1.0/1.1/1.2

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: every WDL file must open with a `version 1.0`/`1.1`/`1.2` header; omitting it selects the old draft-2 dialect with no `~{}` interpolation. The first-class `Directory` type is a 1.2 feature, NOT 1.1; `min`/`max`/`None` arrived in 1.1. Cromwell is the JVM production engine that powers Terra; miniwdl is the Python engine used for local dev, static linting (`miniwdl check`), and readable errors. Pin every `docker:` by `@sha256:` digest, never a floating tag.

# WDL Workflows

**"Build a WDL pipeline for Terra/AnVIL or a GATK best-practices run"** -> Declare `task`s (a containerized command with typed inputs/outputs and a runtime block) and wire them in a `workflow`, then run on Cromwell (cloud/Terra) or miniwdl (local).
- CLI: `womtool validate` / `womtool inputs` (Cromwell toolkit), `miniwdl check` (static lint + ShellCheck), `cromwell run` / `miniwdl run` (execute)
- WDL: `version` header, `task`/`workflow`/`call`, `scatter` fan-out, `runtime { docker, cpu, memory, disks }`

## The governing principle: the runtime block is a cost + reliability CONTRACT

WDL is not chosen on language merits; it is the language of a gravitational system - GATK Best Practices -> Cromwell -> Terra/AnVIL/BioData Catalyst -> Dockstore -> WARP (Van der Auwera & O'Connor 2020). One targets WDL because the data or the collaborators already live in that NIH-cloud ecosystem, and to run vetted GATK pipelines without reinventing them. The design bet is human readability over expressive power. The corollary that governs every real decision: on a cloud backend the engine spins up a FRESH VM per task, so the author must declare its CPU, memory, and disk. The `runtime` block is therefore a cost-and-reliability contract, not decoration, and three traps follow from it:

- Localization dominates cost and wall-time. The engine COPIES (localizes) every input `File` from object storage onto the VM's local disk before the command runs, then delocalizes outputs back. A 30 GB CRAM's transfer can dwarf the compute. Disk math, call caching, and preemptibles all exist to manage bytes moved - subset early and avoid re-localizing the same reference into every scatter shard.
- Under-sized `disks` kills the job LATE. A static `disks: "local-disk 100 HDD"` fails on the one sample bigger than guessed, after an hour of localization, with a cryptic "No space left on device". Size disk dynamically from `size()`.
- A pipeline without pinned containers is not reproducible. `docker: "gatk:latest"` silently breaks reproducibility AND busts call caching, because the cache key hashes the resolved image identity. Pin by `@sha256:` digest.

A clean WDL over unpinned tools is not reproducible: the engine pins step order (layer 1); the author must still pin the container by digest, the reference build, and the parameters.

## Decision: choose WDL, and choose its engine

| Author picks WDL when... | Fails / friction when... |
|--------------------------|--------------------------|
| Controlled-access data is in AnVIL/Terra/BioData Catalyst | The pipeline is dynamic/streaming (WDL has no channels; use nextflow-pipelines) |
| Running GATK Best Practices at population scale | Maximum vendor-neutral portability across institutions is the goal (use cwl-workflows) |
| A WARP/Dockstore pipeline already encodes the analysis | Tight Python/pandas HPC integration is wanted (use snakemake-workflows) |

| Engine | Runtime | Reach for it when | Weakness |
|--------|---------|-------------------|----------|
| Cromwell | Scala/JVM | Production cloud, Terra, robust call caching at scale | Cryptic JVM errors; needs MySQL/Postgres for persistent cache; slow startup |
| miniwdl | Python | Local dev, CI, debugging; `miniwdl check` static lint + ShellCheck; readable errors | Not the Terra engine; smaller cloud story |
| womtool | JVM utility | `validate`, generate the inputs JSON skeleton, `graph` the DAG | Not an executor - validation only |

Practical loop: author and lint with `miniwdl check` locally -> validate and scaffold inputs with `womtool` -> run at scale on Cromwell/Terra. When Cromwell throws a JVM stack trace, reproduce under `miniwdl run` for a message that points at the WDL line.

| Factor | Preemptible / spot (`preemptible: N`) | On-demand |
|--------|---------------------------------------|-----------|
| Cost | ~60-91% cheaper | full price |
| Interruption | reclaimable any second, work discarded | stable |
| Fit | short (<~2-4h), idempotent, restart-safe, scatter shards | long, stateful, near-deadline, non-idempotent |
| Anti-pattern | long non-idempotent task -> retry thrash, can cost MORE than on-demand | over-paying for a trivially restartable 20-min task |

`preemptible: 3` is an Int (retry on a preemptible VM up to 3 times, then fall back to on-demand), NOT a Boolean.

## Task and workflow: the reference shape

A `task` bundles a container, typed inputs, a heredoc command with `~{}` placeholders, typed outputs, and a runtime block. A `workflow` `call`s tasks and passes one call's output to the next by name.

```wdl
version 1.0

task fastp {
    input {
        String sample_id
        File reads_1
        File reads_2
        Int threads = 4
    }
    # ~{} is the WDL-idiomatic placeholder; ${} collides with bash parameter expansion.
    command <<<
        fastp -i ~{reads_1} -I ~{reads_2} \
            -o ~{sample_id}_R1.fq.gz -O ~{sample_id}_R2.fq.gz \
            --json ~{sample_id}.json --thread ~{threads}
    >>>
    output {
        File trimmed_1 = "~{sample_id}_R1.fq.gz"
        File trimmed_2 = "~{sample_id}_R2.fq.gz"
    }
    runtime {
        docker: "quay.io/biocontainers/fastp@sha256:<digest>"   # digest, not :latest
        cpu: threads
        memory: "4 GB"
    }
}

workflow trim {
    input { String sample_id; File r1; File r2 }
    call fastp { input: sample_id = sample_id, reads_1 = r1, reads_2 = r2 }
    output { File out_1 = fastp.trimmed_1 }
}
```

## Scatter: explicit parallel fan-out (no channels)

WDL parallelism is explicit: build an `Array`, `scatter` over it (implicitly parallel), and the engine auto-gathers each shard's output into an `Array` in input order. There is no lazy channel to drain.

```wdl
scatter (idx in range(length(sample_ids))) {
    call align {
        input: sample_id = sample_ids[idx], reads = fastq_files[idx], reference = reference
    }
}
# align.bam outside the scatter is an Array[File], gathered in input order.
output { Array[File] bams = align.bam }
```

Bundle per-sample fields into a `struct` (`struct SampleData { String id; File bam }`) and scatter over `Array[SampleData]` to avoid parallel-array index bugs; see usage-guide.md.

## Runtime as a cost contract + dynamic disk sizing

**Goal:** Size the fresh cloud VM so the task neither fails on disk nor over-pays.

**Approach:** Compute disk from actual input size with a multiplier for outputs/intermediates plus headroom, round UP with `ceil()`, and make it overridable.

```wdl
task bwa_mem {
    input { File reads_1; File reads_2; File reference; Int? override_disk_gb }
    # size(f,"GiB") is binary GiB (be consistent); *2.5 covers input+output+intermediates,
    # +20 is headroom. ceil() always rounds UP - disk must never under-size.
    Int disk_gb = select_first([override_disk_gb,
                  ceil((size(reads_1, "GiB") + size(reads_2, "GiB") + size(reference, "GiB")) * 2.5) + 20])
    command <<< bwa mem ~{reference} ~{reads_1} ~{reads_2} > aligned.sam >>>
    output { File sam = "aligned.sam" }
    runtime {
        docker: "quay.io/biocontainers/bwa@sha256:<digest>"
        cpu: 8
        memory: "16 GB"
        disks: "local-disk ~{disk_gb} HDD"   # mount, GB Int, type; HDD cheap/slow, SSD fast/pricey
        bootDiskSizeGb: 20                    # boot disk holds the image; raise for large images
        preemptible: 3                        # Int = # attempts, then on-demand fallback
        maxRetries: 1                         # retries on ANY failure (distinct from preemptible)
    }
}
```

## Call caching: the `-resume` analog, and how it silently misses

Cromwell hashes each call from its command template, input values (including file CONTENT hashes), Docker image identity, and runtime attributes; on a rerun an identical hash reuses prior outputs. Unlike Nextflow's `-resume`, it is NOT on by default: the in-memory HSQLDB loses the cache on restart, so a persistent DB plus config is required (Terra manages this behind a checkbox).

```
call-caching { enabled = true, invalidate-bad-cache-results = true }
# plus a MySQL/PostgreSQL database stanza - the default HSQLDB does not persist the cache.
```

Silent-miss modes: a floating `:latest` tag resolves to a new digest -> new hash -> miss (pin by digest); a touched/re-staged input whose content or mtime changed busts the cache; a path-based hashing strategy misconfigured on a container backend disables caching; and any whitespace change in the `command` block changes the hash.

## Validate, generate inputs, run

```bash
miniwdl check workflow.wdl              # static lint + ShellCheck (add --strict to gate CI)
womtool validate workflow.wdl          # Cromwell-side structural validation
womtool inputs workflow.wdl > inputs.json   # scaffold the namespaced input JSON
miniwdl run workflow.wdl -i inputs.json     # local run, readable errors
java -jar cromwell.jar run workflow.wdl -i inputs.json   # one-off; `cromwell server` = REST (Terra mode)
```

Input JSON keys are fully namespaced `Workflow.[subworkflow.]call_alias.input_name`, e.g. `{"rnaseq.fastp.threads": 8}`; optional inputs may be omitted. See usage-guide.md for structs, subworkflows, and the full namespacing rules.

Do not hand-roll joint genotyping or CRAM->GVCF: WARP publishes production-vetted, cost-tuned WDL to imitate for disk and preemptible discipline (WARP team 2025).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Task dies late with "No space left on device" | static under-sized `disks` | dynamic `ceil(size(f,"GiB")*factor)+buffer` |
| Job cost balloons; wall-time is mostly "waiting" | localizing huge inputs to every scatter shard | subset early; co-locate data + compute zones; reuse the reference where the backend caches it |
| Reruns recompute everything | call caching off, no persistent DB, or a floating docker tag | enable caching + MySQL/Postgres + digest-pin docker |
| Preemptible task never finishes, costs more than on-demand | long non-idempotent task on `preemptible: N` | move to on-demand or shorten/checkpoint the task |
| VM fails to boot | Docker image larger than the boot disk | raise `bootDiskSizeGb` |
| "Works on my Cromwell, not on Terra" | env drift not baked into the container; unpinned tag | bake everything into a digest-pinned image |
| Cryptic JVM stack trace from Cromwell | engine surfacing an internal error | reproduce under `miniwdl run` for a legible, line-pointing message |
| `${VAR}` in a command expands wrong or breaks | `${}` collides with bash parameter expansion | use `~{}` for WDL interpolation inside `command <<< >>>` |
| Engine rejects `Directory` under `version 1.1` | first-class `Directory` is a 1.2 feature | move the header to `version 1.2` (or `version development` on old engines) |

## Related Skills

- workflow-management/cwl-workflows - Vendor-neutral portable spec; choose it over WDL when handing a pipeline across institutions
- workflow-management/nextflow-pipelines - Channel/dataflow engine + nf-core; choose it for dynamic/streaming cloud pipelines
- workflow-management/snakemake-workflows - Python-native pull engine for HPC and file-pattern logic
- workflows/fastq-to-variants - The end-to-end variant-calling analysis a GATK WDL orchestrates
- variant-calling/gatk-variant-calling - The GATK Best Practices steps WDL encodes for Terra/WARP

## References

- Van der Auwera GA, Carneiro MO, Hartl C, et al. 2013. From FastQ data to high-confidence variant calls: the Genome Analysis Toolkit best practices pipeline. *Curr Protoc Bioinformatics* 43:11.10.1-11.10.33.
- Voss K, Gentry J, Van der Auwera G. 2017. Full-stack genomics pipelining with GATK4 + WDL + Cromwell. *F1000Research* 6:1379 (ISCB Comm J, poster).
- Van der Auwera GA, O'Connor BD. 2020. *Genomics in the Cloud: Using Docker, GATK, and WDL in Terra.* O'Reilly Media. ISBN 9781491975190.
- WARP team (Broad Institute). 2025. WARP analysis research pipelines: cloud-optimized workflows for biological data processing and reproducible analysis. *Bioinformatics* 41(10):btaf494.
- OpenWDL specification. github.com/openwdl/wdl - versioned SPEC on branches wdl-1.0, wdl-1.1 (1.1.3), wdl-1.2; docs at docs.openwdl.org.
<!-- END FILE: workflow-management/wdl-workflows/SKILL.md -->

<!-- END CATEGORY: workflow-management -->

