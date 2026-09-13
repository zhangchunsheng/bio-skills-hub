---
slug: bio-restriction-analysis-integrated
version: 1.0.0
displayName: "限制性内切酶分析 / Restriction enzyme analysis"
name: bio-restriction-analysis-integrated
summary: >-
  中文：限制性内切酶分析综合技能，整合 5 个相关专题，覆盖限制性内切酶分析：酶切位点查找、限制性图谱、Golden Gate组装设计与验证。 English: Integrated Restriction enzyme analysis skill covering 5 related topics, including Restriction enzyme analysis: enzyme site finding, restriction mapping, Golden Gate assembly design and validation.
description: >-
  中文：这是一个面向限制性内切酶分析的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：限制性内切酶分析：酶切位点查找、限制性图谱、Golden Gate组装设计与验证。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Bio.Restriction。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Restriction enzyme analysis, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Restriction enzyme analysis: enzyme site finding, restriction mapping, Golden Gate assembly design and validation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Bio.Restriction. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# restriction-analysis 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: restriction-analysis -->

## 子目录：restriction-analysis/enzyme-selection

<!-- BEGIN FILE: restriction-analysis/enzyme-selection/SKILL.md -->
---
name: bio-restriction-enzyme-selection
description: Select restriction enzymes for cloning or diagnostics using Biopython Bio.Restriction. Finds enzymes by cut frequency, overhang type, recognition-site length, commercial availability, compatible ends, and methylation sensitivity, and identifies isoschizomers and compatible pairs. Use when choosing which enzymes to use to linearize a vector, drop in an insert, set up a diagnostic digest, or pick a methylation-insensitive enzyme.
tool_type: python
primary_tool: Bio.Restriction
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+ (API verified on 1.86)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Restriction.Analysis)` to confirm method names

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying. The
Analysis cut-count methods were renamed across versions (see Common Errors).

# Restriction Enzyme Selection

**"Pick enzymes to clone my insert into this vector"** -> Search the enzyme database under the constraints that actually matter: cuts the vector once, leaves the insert intact, makes a usable end, is buyable, and is not silenced by methylation.
- Python: `Bio.Restriction.Analysis(CommOnly, seq)` with `with_N_sites`/`without_site`, plus enzyme predicates for overhang and compatibility.

The canonical selection is an intersection, not a single query: an enzyme that **cuts the vector exactly once at the cloning site** AND **does not cut the insert** AND **leaves the intended overhang** AND **is commercially available** AND **is not blocked by the methylation on the source DNA**. Each constraint below is one filter in that intersection; the skill's value is composing them, not running any one alone.

## The Selection Decision Table

| Constraint | What to ask | API / source |
|------------|-------------|--------------|
| Cut frequency | Cut vector once? Leave insert uncut? | `Analysis.with_N_sites(1)`, `Analysis.without_site()` |
| Recognition length | naive 1/4^n spacing: 4-cutter (~256 bp, frequent), 6-cutter (~4 kb, routine cloning), 8-cutter (~65 kb, rare; large constructs, mapping) -- real genomes deviate (see below) | `len(enzyme.site)` |
| Overhang | 5' overhang (most common), 3' overhang, or blunt (non-directional, inefficient ligation) | `is_5overhang()`, `is_3overhang()`, `is_blunt()` |
| Directionality | Two different ends so the insert goes one way and the vector cannot self-ligate | two single-cutters with non-compatible ends |
| Availability | Can it be purchased? | membership in `CommOnly` |
| Methylation | Is the site blocked by Dam/Dcm/CpG on this DNA? | curated table below + REBASE (not the coarse `is_methylable()`) |
| Fidelity | Avoid star activity under forcing conditions | prefer High-Fidelity (HF) enzymes; benchtop, not in BioPython |

Naive cut-frequency intuition (a 6-cutter every 4^6 = 4096 bp) fails on real genomes: vertebrate CpG suppression makes any CpG-containing site -- NotI `GCGGCCGC` above all -- far rarer than 1/4^n, which is exactly why NotI and other 8-cutters are the rare-cutters of choice for large mammalian fragments.

## Find Enzymes By Cut Frequency

**Goal:** Sort candidates into single-cutters (linearize), double-cutters (excise), and non-cutters (safe through the digest).

**Approach:** `Analysis` exposes `with_N_sites(n)` for an exact cut count and `without_site()` for non-cutters. (The older `once_cutters()` / `twice_cutters()` / `only_dont_cut()` / `only_cut()` names do not exist in current BioPython and raise `AttributeError`.)

```python
from Bio import SeqIO
from Bio.Restriction import Analysis, CommOnly

record = SeqIO.read('sequence.fasta', 'fasta')
analysis = Analysis(CommOnly, record.seq)

single_cutters = analysis.with_N_sites(1)   # linearization candidates
double_cutters = analysis.with_N_sites(2)   # excise-an-insert candidates
non_cutters    = analysis.without_site()    # safe to keep in a multi-enzyme digest
all_cutters    = analysis.with_sites()      # any number of sites
print(f'{len(single_cutters)} single-cutters, {len(non_cutters)} non-cutters')
```

## Select A Pair For Directional Cloning

**Goal:** Two enzymes that each cut the vector once, neither cuts the insert, and their ends differ so the ligation is directional and the vector cannot recircularize.

**Approach:** Intersect "cuts vector once" with "does not cut insert", then pair candidates whose ends are mutually INCOMPATIBLE -- that is what makes the cloning directional and stops the vector self-ligating. Two enzymes are an incompatible (directional) pair when neither appears in the other's `compatible_end()`.

```python
from itertools import combinations
from Bio.Restriction import Analysis, CommOnly

def directional_pairs(vector_seq, insert_seq):
    vec_once  = set(Analysis(CommOnly, vector_seq, linear=False).with_N_sites(1))
    ins_clear = set(Analysis(CommOnly, insert_seq).without_site())
    candidates = sorted(vec_once & ins_clear, key=str)
    pairs = []
    for a, b in combinations(candidates, 2):
        if b not in a.compatible_end():          # incompatible ends -> directional, no self-ligation
            pairs.append((a, b))
    return pairs                                  # each pair cuts vector once, leaves insert intact
```

## Find Compatible And Isocaudomer Ends

**Goal:** Identify enzymes whose overhangs ligate together, including enzymes with different recognition sites that leave the same overhang (isocaudomers).

**Approach:** `compatible_end()` returns every enzyme that *can* leave a compatible overhang -- including Type IIS enzymes whose overhang is user-defined, not fixed. For a real ligation partner, filter the result to fixed-overhang Type IIP enzymes (the true isocaudomers, e.g. BamHI/BglII/BclI/Sau3AI all leave 5'-GATC); a Type IIS enzyme listed here is not a drop-in cloning partner.

```python
from Bio.Restriction import BamHI

partners = BamHI.compatible_end()                  # any enzyme that can leave a 5'-GATC end
fixed = [e for e in partners if e.is_palindromic()] # keep Type IIP isocaudomers (BglII, BclI, MboI, Sau3AI...)
print(f'BamHI isocaudomers (fixed overhang): {sorted(str(e) for e in fixed)}')
```

Ligating two different-but-compatible sites usually creates a hybrid junction that **neither enzyme re-cleaves** (BamHI `G^GATCC` + BglII `A^GATCT` -> `GGATCT`/`AGATCC`, which is neither site). This makes the join directional and is used deliberately to destroy one site -- but whether the junction is recut is pair-dependent, so verify the specific pair rather than assuming.

## Filter By Overhang And Recognition Length

```python
from Bio.Restriction import CommOnly, Analysis

cutters = Analysis(CommOnly, record.seq).with_sites()

blunt   = [e for e in cutters if e.is_blunt()]
five_p  = [e for e in cutters if e.is_5overhang()]
three_p = [e for e in cutters if e.is_3overhang()]

six_cutters   = [e for e in CommOnly if len(e.site) == 6]   # routine cloning
eight_cutters = [e for e in CommOnly if len(e.site) == 8]   # rare cutters
```

## Methylation Sensitivity (The Silent-Failure Trap)

Standard E. coli cloning strains (DH5-alpha, JM109, TOP10) are **dam+ dcm+**, so plasmid and insert DNA prepped from them is methylated at GATC (Dam, N6-methyladenine) and CCWGG (Dcm, 5-methylcytosine). An enzyme blocked by that mark will fail or partially cut even though the recognition site is present -- a silent failure. Mammalian genomic DNA additionally carries CpG (5mC) methylation. The fix is to re-propagate the DNA in a **dam- dcm- strain** (GM2163, JM110, INV110) before cutting.

| Site context | Enzyme | Behavior on the methylated site |
|--------------|--------|----------------------------------|
| Dam GATC | DpnI | Cuts ONLY when fully Dam-methylated (methylation-dependent) |
| Dam GATC | DpnII, MboI | Blocked by Dam methylation (cut only unmethylated GATC) |
| Dam GATC | Sau3AI | Insensitive to Dam (cuts methylated or not) |
| CpG CCGG | HpaII | Blocked by CpG methylation of the internal C |
| CpG CCGG | MspI | Cuts regardless of CpG methylation (isoschizomer of HpaII) |
| Dam-overlapping | ClaI `ATCGAT`, XbaI `TCTAGA` | Blocked when flanking bases create an overlapping Dam GATC |

Do NOT rely on BioPython's `enzyme.is_methylable()` to make this decision: it is a coarse REBASE flag (it returns True for Sau3AI, which is actually Dam-insensitive, and for EcoRI), does not distinguish Dam vs Dcm vs CpG, and does not indicate the direction of the effect. Use the curated cases above and consult REBASE for the specific methyltransferase that blocks a given enzyme.

```python
from Bio.Restriction import DpnI, DpnII, Sau3AI, MboI

# Curated, not from is_methylable(): the GATC quartet a cloner must know.
dam_behavior = {
    'DpnI': 'requires Dam methylation to cut',
    'DpnII': 'blocked by Dam methylation',
    'MboI': 'blocked by Dam methylation',
    'Sau3AI': 'insensitive to Dam methylation',
}
for enz in (DpnI, DpnII, MboI, Sau3AI):
    print(f'{enz} ({enz.site}): {dam_behavior[str(enz)]}')
```

## Isoschizomers, Neoschizomers, And Why The Choice Matters

```python
from Bio.Restriction import SmaI, XmaI

print('SmaI isoschizomers:', SmaI.isoschizomers())     # all same-site enzymes (Cfr9I, TspMI, XmaI)
print('SmaI elucidate:', SmaI.elucidate())             # CCC^_GGG  -> blunt
print('XmaI elucidate:', XmaI.elucidate())             # C^CCGG_G  -> 5' overhang
```

- Isoschizomers recognize the same site; pick among them for a different buffer, supplier, or methylation sensitivity (HpaII vs MspI differ only in CpG sensitivity; MboI vs Sau3AI in Dam sensitivity).
- A neoschizomer recognizes the same site but cuts at a different position -- the lever for choosing blunt vs sticky ends from one sequence (SmaI `CCC^GGG` blunt vs XmaI `C^CCGGG` 5' overhang). Note: in current BioPython `neoschizomers()` and `isoschizomers()` overlap (both list all same-site enzymes), so confirm the actual cut difference with `elucidate()` rather than trusting the method name to filter.

## Star Activity And High-Fidelity Enzymes

Under forcing conditions -- >5% glycerol, low ionic strength, high pH (>8), large enzyme excess or over-long incubation, or Mn2+ replacing Mg2+ -- many enzymes relax specificity and cut near-cognate sites ("star activity"; EcoRI* is the classic case). When a clean digest matters, prefer an engineered High-Fidelity (HF) enzyme (e.g. EcoRI-HF), which is selected to show no star activity even in overnight, high-unit digests. This is a benchtop property, not encoded in BioPython; surface it when recommending an enzyme.

## Type IIS / Golden Gate

Type IIS enzymes (BsaI, BsmBI, BbsI, SapI) cut outside their recognition site and enable scarless, directional, one-pot assembly. Selecting and validating them -- including domestication of internal sites and fusion-overhang design -- is its own analysis; route to restriction-analysis/golden-gate-assembly. For plain selection, a part is "Golden Gate ready" for an enzyme when `enzyme.search(seq)` returns no internal sites.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AttributeError: ... 'once_cutters'` / `'only_dont_cut'` / `'only_cut'` | Methods renamed across BioPython versions | `with_N_sites(1)`/`with_N_sites(2)` for exact counts; `without_site()` for non-cutters; `with_sites()` for any cutter |
| `AttributeError: ... 'is_dam_methylable'` / `'is_dcm_methylable'` | These methods do not exist | Use the curated Dam/Dcm table above; consult REBASE for specifics |
| `AttributeError: ... 'fst3cut'` / `'fst5cut'` | Attribute names are `fst3` / `fst5` | Use `enzyme.fst5` / `enzyme.fst3` (Type IIS cut offsets) |
| Chosen enzyme fails to cut a real prep | Site blocked by Dam/Dcm methylation | Re-prep DNA in a dam- dcm- strain, or pick a methylation-insensitive enzyme |
| Recommended enzyme cannot be bought | Searched `AllEnzymes` | Restrict to `CommOnly` |
| Blunt clone has high background / wrong orientation | Blunt ends ligate inefficiently and non-directionally | Prefer two different sticky ends; dephosphorylate the vector (see usage guide) |
| Double digest only partially cuts | The two chosen enzymes share no buffer where both are fully active | Pick a pair compatible in one universal buffer (rCutSmart / FastDigest); otherwise digest sequentially, lower-salt enzyme first (this is a selection criterion when choosing the pair) |

## Related Skills

- restriction-sites - Find where the selected enzymes cut
- restriction-mapping - Map the selected enzyme sites
- fragment-analysis - Predict the fragments a chosen digest produces
- golden-gate-assembly - Select and validate Type IIS enzymes for scarless assembly
- primer-design/primer-basics - Add chosen restriction sites to PCR primer tails

## References

- Roberts RJ, Vincze T, Posfai J, Macelis D. REBASE: a database for DNA restriction and modification: enzymes, genes and genomes. Nucleic Acids Res. 2023;51(D1):D629-D630. doi:10.1093/nar/gkac975
- Waalwijk C, Flavell RA. MspI, an isoschizomer of HpaII which cleaves both unmethylated and methylated HpaII sites. Nucleic Acids Res. 1978;5(9):3231-3236. doi:10.1093/nar/5.9.3231
- Geier GE, Modrich P. Recognition sequence of the dam methylase of Escherichia coli K12 and mode of cleavage of DpnI endonuclease. J Biol Chem. 1979;254(4):1408-1413.
- Wei H, Therrien C, Blanchard A, Guan S, Zhu Z. The Fidelity Index provides a systematic quantitation of star activity of DNA restriction endonucleases. Nucleic Acids Res. 2008;36(9):e50. doi:10.1093/nar/gkn182
<!-- END FILE: restriction-analysis/enzyme-selection/SKILL.md -->

## 子目录：restriction-analysis/fragment-analysis

<!-- BEGIN FILE: restriction-analysis/fragment-analysis/SKILL.md -->
---
name: bio-restriction-fragment-analysis
description: Predict restriction digest fragment sizes and gel patterns using Biopython Bio.Restriction. Computes fragment lengths and sequences for single and double digests on linear or circular DNA, and interprets them against an agarose gel. Use when predicting the fragments from a digest, planning a diagnostic digest to verify a clone, or matching observed gel bands to an expected pattern.
tool_type: python
primary_tool: Bio.Restriction
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+ (API verified on 1.86)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython`, then check the return shape with `from Bio.Restriction import EcoRI; from Bio.Seq import Seq; EcoRI.catalyze(Seq('GAATTCGAATTC'))` (a tuple of fragment Seqs)

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Restriction Fragment Analysis

**"What fragments will this digest produce?"** -> Simulate the cut and return fragment lengths (and sequences), for one enzyme or a double digest, on linear or circular DNA.
- Python: `enzyme.catalyze(seq, linear=...)` returns a tuple of fragment `Seq` objects directly.

Two facts decide whether the prediction is right. First, **`catalyze()` returns the tuple of fragments itself** -- `EcoRI.catalyze(seq)` is `(Seq(...), Seq(...), Seq(...))`. Do NOT write `catalyze(seq)[0]` to "get the fragments": that returns only the first fragment, and iterating it then counts its bases, producing nonsense sizes like `[1, 1, 1, ...]`. Second, **topology sets the fragment count**: a linear molecule with n cuts yields n+1 fragments; a circular molecule with n cuts yields n. Passing the default `linear=True` to a plasmid invents one extra fragment that does not exist on the bench.

## Fragment Count By Topology

| Molecule | n cut sites yields | Why |
|----------|--------------------|-----|
| Linear (PCR product, genomic fragment, lambda) | n + 1 fragments | Cut once -> two pieces |
| Circular (plasmid, many viral genomes) | n fragments | Cut once -> one linearized piece; the origin-spanning fragment wraps |

A plasmid showing three bands on a single-enzyme digest has three sites, not two. Counting plasmid bands as if the molecule were linear is the most common digest-interpretation error.

## Predict Fragment Sizes

**Goal:** Turn a digest into the band sizes a gel would show.

**Approach:** Call `catalyze()` with the correct topology, take the lengths of the returned fragments, sort descending. The summed sizes must equal the molecule length -- a built-in correctness check.

```python
from Bio import SeqIO
from Bio.Restriction import EcoRI

record = SeqIO.read('sequence.fasta', 'fasta')
seq = record.seq

fragments = EcoRI.catalyze(seq, linear=True)   # tuple of Seq; NO [0]
sizes = sorted((len(f) for f in fragments), reverse=True)
assert sum(sizes) == len(seq)                  # fragments must account for the whole molecule
print(f'{len(sizes)} fragments: {sizes}')
```

## Linear vs Circular Digestion

```python
from Bio.Restriction import EcoRI

linear_frags   = EcoRI.catalyze(seq, linear=True)
circular_frags = EcoRI.catalyze(seq, linear=False)   # plasmid: one fewer fragment
print(f'Linear: {len(linear_frags)} fragments; Circular: {len(circular_frags)} fragments')
```

## Double Digest

**Goal:** Predict fragments when two enzymes cut the same molecule.

**Approach:** A double digest cuts at the union of both site sets. The robust way is to build a `RestrictionBatch` and let `Analysis` collect every position, then compute fragments from the sorted positions (this generalizes to any number of enzymes and to circular DNA). Sequential `catalyze` calls also work but are easy to get wrong on circular DNA.

```python
from Bio.Restriction import EcoRI, BamHI, RestrictionBatch, Analysis

def fragments_from_positions(seq_len, positions, linear=True):
    '''Fragment sizes (bp) from a set of 1-based cut positions.'''
    cuts = sorted(set(positions))
    if not cuts:
        return [seq_len]
    spans = [cuts[i + 1] - cuts[i] for i in range(len(cuts) - 1)]
    if linear:
        return [cuts[0]] + spans + [seq_len - cuts[-1]]
    return spans + [(seq_len - cuts[-1]) + cuts[0]]    # circular: wrap-around fragment

batch = RestrictionBatch([EcoRI, BamHI])
positions = [p for sites in Analysis(batch, seq).with_sites().values() for p in sites]
sizes = sorted(fragments_from_positions(len(seq), positions, linear=True), reverse=True)
print(f'Double digest: {len(sizes)} fragments: {sizes}')
assert sum(sizes) == len(seq)
```

## Interpreting The Gel: Size, Resolution, And Topology

Fragment sizes are not what a gel directly reports; migration distance is. The decisions below come from gel physics, not from BioPython, and they determine whether predicted bands are actually resolvable.

| Reality | Consequence for interpretation |
|---------|--------------------------------|
| Migration distance is ~linear in -log10(size) only within a gel's resolving window | Sizing is reliable only against a ladder run on the same gel; never reuse a standard curve across gels |
| Agarose percent sets the window (approximate, buffer- and voltage-dependent: ~0.7% resolves ~0.8-12 kb; ~1% ~0.5-10 kb; ~2% ~0.1-2 kb) | Choose the percent for the bands of interest; small fragments run off a low-percent gel, large fragments pile up on a high-percent one |
| Above ~20-50 kb fragments co-migrate (reptation); resolving them needs pulsed-field (PFGE) | Two large predicted bands may appear as one on a conventional gel |
| Two fragments of similar size co-migrate as one band of doubled intensity (intensity ~ mass) | A "missing" predicted band is often a co-migrating doublet, not an error -- check the sum |
| Uncut plasmid runs as supercoiled (fast, anomalous) + nicked (slow), same molecule | Do not size a supercoiled band off a linear ladder; only a linearized (single-cut) plasmid sizes correctly |

## Simulate A Gel Pattern (Text)

**Goal:** Lay predicted digests next to a ladder to see which bands resolve and which co-migrate.

**Approach:** Pool all band sizes and the ladder, sort descending, and mark each lane. Co-migration shows up as multiple marks at one size.

```python
def simulate_gel(digests, ladder=None):
    '''digests: {lane_name: [sizes]} -> print a text gel against a ladder.'''
    ladder = ladder or [10000, 8000, 6000, 5000, 4000, 3000, 2000, 1500, 1000, 750, 500, 250]
    bands = sorted(set(ladder).union(*[set(s) for s in digests.values()]), reverse=True)
    header = f'{"size":>6} | {"ladder":^6} | ' + ' | '.join(f'{n:^8}' for n in digests)
    print(header); print('-' * len(header))
    for b in bands:
        row = f'{b:>6} | {"---" if b in ladder else "":^6} | '
        row += ' | '.join(f'{"=" * 4 * lane.count(b):^8}' for lane in digests.values())
        print(row)

simulate_gel({'EcoRI': sizes})
```

## Diagnostic Digest Report

**Goal:** Document an expected digest to plan a clone-verification gel.

**Approach:** Report site count, positions, fragment sizes, and the total; flag any pair of fragments too close to resolve.

```python
def fragment_report(seq, enzyme, linear=True, resolution=0.10):
    sites = enzyme.search(seq, linear=linear)
    sizes = sorted((len(f) for f in enzyme.catalyze(seq, linear=linear)), reverse=True)
    print(f'{enzyme} ({enzyme.site}): {len(sites)} site(s) at {sites}')
    print(f'  {len(sizes)} fragments, total {sum(sizes)} bp: {sizes}')
    close = [(a, b) for a, b in zip(sizes, sizes[1:]) if a and (a - b) / a < resolution]
    if close:
        print(f'  WARNING likely co-migrating (<{resolution:.0%} apart): {close}')
    return sizes

fragment_report(seq, EcoRI)
```

## Compare Expected vs Observed Bands

```python
def compare_fragments(expected, observed, tolerance=50):
    '''Match predicted sizes to gel-measured sizes within a tolerance (bp).'''
    obs = list(observed)
    matched, missing = [], []
    for exp in expected:
        hit = next((o for o in obs if abs(exp - o) <= tolerance), None)
        if hit is None:
            missing.append(exp)
        else:
            matched.append((exp, hit)); obs.remove(hit)
    print('matched:', matched)
    if missing: print('missing (predicted, not seen -- co-migration or partial digest?):', missing)
    if obs:     print('extra (seen, not predicted -- star activity, contaminant, or wrong map?):', obs)

compare_fragments(expected=[3000, 2000, 1500, 500], observed=[3050, 2000, 1480, 510, 200])
```

Extra bands and a smeary ladder of intermediate sizes often signal a **partial digest** (not every site cut), which produces sums of adjacent complete-digest fragments. Drive the reaction to completion (more enzyme or time) before concluding the map is wrong.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Fragment sizes are all 1 (or wildly wrong) | `catalyze(seq)[0]` returns the first fragment, then `len(f) for f in it` counts bases | Use `fragments = enzyme.catalyze(seq, linear=...)` with no `[0]` |
| Predicted one fragment too many for a plasmid | Digested a circular molecule with `linear=True` | Pass `linear=False`; circular gives n fragments from n cuts |
| Fragment sizes do not sum to the molecule length | A band was missed or two co-migrate | The `sum(sizes) == len(seq)` check is mandatory; a shortfall means a hidden doublet or run-off fragment |
| Two predicted bands never separate on the gel | Sizes within the gel's resolving limit, or both >20-50 kb | Adjust agarose percent, or use PFGE for very large fragments |

## Related Skills

- restriction-sites - Find the cut positions that drive fragment calculation
- restriction-mapping - Order sites and compute inter-site distances
- enzyme-selection - Choose enzymes that give a resolvable, diagnostic band pattern
- sequence-manipulation/seq-objects - Work with the fragment Seq objects

## References

- Smith HO, Birnstiel ML. A simple method for DNA restriction site mapping. Nucleic Acids Res. 1976;3(9):2387-2398. doi:10.1093/nar/3.9.2387
- Schwartz DC, Cantor CR. Separation of yeast chromosome-sized DNAs by pulsed field gradient gel electrophoresis. Cell. 1984;37(1):67-75. doi:10.1016/0092-8674(84)90301-5
<!-- END FILE: restriction-analysis/fragment-analysis/SKILL.md -->

## 子目录：restriction-analysis/golden-gate-assembly

<!-- BEGIN FILE: restriction-analysis/golden-gate-assembly/SKILL.md -->
---
name: bio-restriction-golden-gate-assembly
description: Design and validate Type IIS scarless DNA assembly (Golden Gate, MoClo) using Biopython Bio.Restriction. Screens parts for internal BsaI/BsmBI/BbsI/SapI sites (domestication), previews the fusion overhangs a digest exposes, and validates a fusion-overhang set for distinctness and fidelity. Use when designing a Golden Gate or MoClo assembly, domesticating a part by removing internal Type IIS sites, or choosing and checking fusion overhangs for one-pot assembly.
tool_type: python
primary_tool: Bio.Restriction
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+ (API verified on 1.86)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Restriction.BsaI.search)` to confirm the search API

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Golden Gate / Type IIS Assembly

**"Design (or check) my Golden Gate assembly"** -> Make each part free of the assembly enzyme's internal sites, and give every junction a distinct, well-behaved fusion overhang, so one tube of enzyme plus ligase builds the construct directionally and scarlessly.
- Python: `Bio.Restriction` to find internal Type IIS sites and read the overhang a cut exposes; the overhang-set rules are sequence logic, not a database call.

The whole method rests on one property: a Type IIS enzyme **cuts outside its recognition sequence**, so the 4-nt overhang it leaves is set by the user's flanking DNA, and the recognition site is placed to be **removed from the final product**. Because the ligated junction no longer contains the site, the enzyme cannot re-cut it, so digestion and ligation run together in one pot. Two design obligations follow, and both are what this skill checks: (1) **domestication** -- no part may contain an internal copy of the assembly enzyme's site, or it will be fragmented during assembly; (2) a set of **distinct, non-palindromic fusion overhangs** -- one per junction -- so parts assemble in exactly one order.

## Choosing The Assembly Enzyme

| Enzyme | Recognition | Overhang | Typical role |
|--------|-------------|----------|--------------|
| BsaI (Eco31I) | GGTCTC(1/5) | 4 nt 5' | The default Golden Gate / MoClo Level 1 enzyme; BsaI-HFv2 for fidelity |
| BsmBI (Esp3I) | CGTCTC(1/5) | 4 nt 5' | MoClo Level 0 / Level 2 (alternates with BsaI between levels) |
| BbsI (BpiI) | GAAGAC(2/6) | 4 nt 5' | Alternative when BsaI/BsmBI sites cannot be domesticated out |
| SapI (LguI) | GCTCTTC(1/4) | 3 nt 5' | 3-nt (codon-length) overhangs for reading-frame-preserving fusions |

Hierarchical systems (MoClo, Golden Braid) **alternate enzymes between levels** so each assembly round removes the previous level's sites: assemble Level 0 -> 1 with one enzyme, 1 -> 2 with the other. Pick the level's enzyme first, then domesticate every part against it.

## Method Context

| | Golden Gate (Type IIS) | Classic restriction-ligation (Type IIP) | Gibson assembly |
|--|------------------------|------------------------------------------|-----------------|
| Junction defined by | user-designed 4-nt overhang (3 for SapI) | the enzyme's fixed overhang | ~20-40 bp designed homology |
| Scar | none (site removed from product) | a restriction-site scar at each junction | none |
| Reaction | one-pot, one-step (37/16 C cycling) | sequential digest -> purify -> ligate | isothermal 50 C |
| Fragments per reaction | many (20-30+, more with optimized sets) | few | several |
| Main constraint | domestication; distinct overhang set | needs available compatible sites | terminal homology only |

Choose Golden Gate when assembling several parts repeatedly from a standardized library; classic digestion for a one-off two-piece clone with convenient sites; Gibson when parts cannot be domesticated or no site layout works.

## Domesticate: Find Internal Sites

**Goal:** Confirm a part carries no internal copy of the assembly enzyme's site (on either strand), and locate any that must be removed.

**Approach:** `enzyme.search(seq)` finds Type IIS sites on both strands (the recognition sequence is asymmetric, so its reverse-complement is detected too). Any hit inside a part is a defect to silently mutate away.

```python
from Bio import SeqIO
from Bio.Restriction import BsaI, BsmBI, BbsI, SapI

record = SeqIO.read('part.fasta', 'fasta')

for enzyme in (BsaI, BsmBI, BbsI, SapI):
    hits = enzyme.search(record.seq)            # both strands; recognition site is asymmetric
    status = 'clean' if not hits else f'{len(hits)} internal site(s) at {hits} -> domesticate'
    print(f'{enzyme} ({enzyme.site}): {status}')
```

## Domesticate: Break A Site By A Silent Mutation

**Goal:** Remove an internal site from a coding part without changing the protein.

**Approach:** Anchor on the recognition sequence itself (on both strands), not the cut position -- a Type IIS enzyme cuts *outside* its site, so mutating the codon at the cut would not touch the site. Walk the codons overlapping each recognition-site occurrence, swap one for a synonymous codon that breaks the site, and assert the protein is unchanged. This needs the reading frame.

```python
from Bio.Data import CodonTable
from Bio.Seq import Seq

def domesticate_cds(cds, enzyme, frame=0):
    '''Remove an enzyme's internal sites from a CDS by synonymous codon swaps (reading frame `frame`).'''
    table = CodonTable.unambiguous_dna_by_id[1]
    syn = {}
    for codon, aa in table.forward_table.items():
        syn.setdefault(aa, []).append(codon)
    s = list(str(cds).upper())
    end = frame + 3 * ((len(s) - frame) // 3)
    protein = str(Seq(''.join(s[frame:end])).translate())
    site = str(enzyme.site)
    motifs = (site, str(Seq(site).reverse_complement()))    # both strands; Type IIS sites are unambiguous
    for _ in range(len(s)):
        seqstr = ''.join(s)
        if not enzyme.search(Seq(seqstr)):
            break
        hit = max(seqstr.find(m) for m in motifs)           # a recognition-site start (either strand)
        for ci in range(((hit - frame) // 3) * 3 + frame, hit + len(site), 3):
            if ci < frame or ci + 3 > len(s):
                continue
            codon = ''.join(s[ci:ci + 3])
            alt = next((a for a in syn.get(table.forward_table.get(codon), ())
                        if a != codon and not enzyme.search(Seq(''.join(s[:ci] + list(a) + s[ci + 3:])))), None)
            if alt:
                s = s[:ci] + list(alt) + s[ci + 3:]
                break
    assert str(Seq(''.join(s[frame:end])).translate()) == protein   # protein unchanged
    return Seq(''.join(s))

# A site that overlaps only Met/Trp codons (no synonyms) is rare but cannot be silently broken;
# always confirm the result is clean: assert not enzyme.search(domesticate_cds(cds, enzyme))
```

## Preview The Fusion Overhangs A Digest Exposes

**Goal:** Read the actual 4-nt overhang each Type IIS cut would leave, to confirm junctions match as designed.

**Approach:** Anchor on the literal forward recognition sequence so only forward-oriented sites are read (a reverse-oriented site cuts on the other side and would otherwise return a misleading overhang). The 5' overhang starts `fst5` bases after the recognition-site start.

```python
from Bio.Restriction import BsaI

def forward_overhangs(seq, enzyme=BsaI, width=4):
    '''4-nt overhangs at FORWARD-oriented Type IIS sites, anchored on the recognition sequence.'''
    s, site, out = str(seq).upper(), str(enzyme.site), []
    i = s.find(site)
    while i >= 0:
        cut = i + enzyme.fst5                  # top-strand cut offset from the site start
        out.append(s[cut:cut + width])
        i = s.find(site, i + 1)
    return out

# Reverse-oriented sites cut on the other side; for a full construct, design the overhangs
# explicitly (below) rather than inferring every one from sequence.
```

## Validate A Fusion-Overhang Set

**Goal:** Check that the overhangs chosen for all junctions assemble uniquely and ligate efficiently.

**Approach:** Apply the design rules: every overhang distinct; none palindromic (self-ligates); no overhang equal to the reverse complement of another (cross-ligates); avoid all-identical bases. High-throughput ligation-fidelity data (Potapov 2018) underlies curated high-fidelity sets used for large assemblies.

```python
from Bio.Seq import Seq

def validate_overhang_set(overhangs):
    issues = []
    if len(set(overhangs)) != len(overhangs):
        issues.append('duplicate overhangs (parts assemble ambiguously)')
    for o in overhangs:
        if o == str(Seq(o).reverse_complement()):
            issues.append(f'{o} is palindromic (self-ligates)')
        if len(set(o)) == 1:
            issues.append(f'{o} is a homopolymer (low ligation fidelity)')
    rc = {o: str(Seq(o).reverse_complement()) for o in overhangs}
    for a in overhangs:
        for b in overhangs:
            if a != b and rc[a] == b:
                issues.append(f'{a} is the reverse complement of {b} (cross-ligates)')
    return issues or ['overhang set OK']

print(validate_overhang_set(['AATG', 'GCTT', 'TACT', 'GGGG']))
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Assembly drops or scrambles a part | An internal Type IIS site fragmented it | Domesticate every part against the level's enzyme before assembly |
| Junctions ligate in the wrong order or orientation | Two junctions share an overhang, or one is the reverse complement of another | Use a distinct, non-self-complementary overhang per junction; check with `validate_overhang_set` |
| Empty or low-efficiency assembly | Palindromic or homopolymer overhang, or wrong enzyme/buffer cycling | Avoid palindromic/homopolymer overhangs; cycle 37/16 C with a Type IIS enzyme + T4 ligase |
| `search()` misses a reverse-oriented site | Site too close to the sequence end so the cut falls off it | Domesticate on the full part in context, not a trimmed fragment |
| Recognition site still present in the product | Site placed so the cut does not remove it | Orient Type IIS sites so cleavage excises them from the assembled junction |

## Related Skills

- enzyme-selection - Choose a classic restriction enzyme when scarless assembly is not needed
- restriction-sites - Find any enzyme's sites in a part
- fragment-analysis - Predict fragments to verify an assembly digest
- genome-engineering/grna-design - Design constructs that this assembly will build
- sequence-manipulation/transcription-translation - Confirm domestication kept the reading frame

## References

- Engler C, Kandzia R, Marillonnet S. A one pot, one step, precision cloning method with high throughput capability. PLoS One. 2008;3(11):e3647. doi:10.1371/journal.pone.0003647
- Engler C, Gruetzner R, Kandzia R, Marillonnet S. Golden gate shuffling: a one-pot DNA shuffling method based on type IIs restriction enzymes. PLoS One. 2009;4(5):e5553. doi:10.1371/journal.pone.0005553
- Weber E, Engler C, Gruetzner R, Werner S, Marillonnet S. A modular cloning system for standardized assembly of multigene constructs. PLoS One. 2011;6(2):e16765. doi:10.1371/journal.pone.0016765
- Potapov V, Ong JL, Kucera RB, et al. Comprehensive profiling of four base overhang ligation fidelity by T4 DNA ligase and application to DNA assembly. ACS Synth Biol. 2018;7(11):2665-2674. doi:10.1021/acssynbio.8b00333
<!-- END FILE: restriction-analysis/golden-gate-assembly/SKILL.md -->

## 子目录：restriction-analysis/restriction-mapping

<!-- BEGIN FILE: restriction-analysis/restriction-mapping/SKILL.md -->
---
name: bio-restriction-mapping
description: Build restriction maps showing enzyme cut positions and inter-site distances along DNA using Biopython Bio.Restriction. Produces text or graphical maps for linear and circular molecules, orders sites from single and double digests, and overlays GenBank features. Use when creating a restriction map of a sequence, ordering cut sites along a plasmid, or relating sites to annotated features.
tool_type: python
primary_tool: Bio.Restriction
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+ (API verified on 1.86), matplotlib 3.7+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Restriction.Analysis.print_as)` to confirm format names

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Restriction Mapping

**"Make a restriction map of my sequence"** -> Place each enzyme's cut sites along the molecule, in order, with the distances between them and (for plasmids) the wrap-around fragment.
- Python: `Bio.Restriction.Analysis(...).print_as('map')` for a quick text map; `search()` positions + `matplotlib` for a graphical one.

A map is more than a list of positions: it is the ordering and spacing of sites, and on a plasmid the ordering is circular. Two things separate a correct map from a wrong one. First, **a circular molecule wraps**: the fragment between the last site and the first crosses the origin, so its length is `(seq_len - last) + first`, not `seq_len - last`. Second, when sites come from a gel rather than a known sequence, **order is deduced, not given** -- single digests give sizes, and only comparing single vs double digests (or partial digests) orders them.

## Choosing The Map Representation

| Need | Representation | How |
|------|----------------|-----|
| Quick look while exploring | Text map | `Analysis.print_as('map')` / `'linear'` |
| Capture to a string/report | Formatted text | `Analysis.format_output()` |
| Publication / slide figure | Graphical map | `search()` positions drawn with matplotlib |
| Sites vs annotated features | Feature overlay | iterate `record.features` against each cut position |
| Ordering sites from a gel | Digest comparison | single vs double (or partial) digest fragment patterns |

## Quick Text Map

```python
from Bio import SeqIO
from Bio.Restriction import EcoRI, BamHI, HindIII, RestrictionBatch, Analysis

record = SeqIO.read('sequence.fasta', 'fasta')
analysis = Analysis(RestrictionBatch([EcoRI, BamHI, HindIII]), record.seq)

analysis.print_as('map'); analysis.print_that()      # visual map to stdout
analysis.print_as('linear'); analysis.print_that()   # linear list
report = analysis.format_output()                    # capture as a string (not format_as)
```

## Ordered Site List With Distances

**Goal:** A single ordered table of every cut, which enzyme made it, and the distance to the next.

**Approach:** Collect `(position, enzyme)` from `Analysis.full()`, sort by position, and walk the list. For circular DNA, close the loop with the wrap-around span.

```python
from Bio.Restriction import RestrictionBatch, Analysis, EcoRI, BamHI, HindIII, XhoI, NotI

seq = record.seq
seq_len = len(seq)
circular = False    # set True for a plasmid (and use linear=not circular below)

analysis = Analysis(RestrictionBatch([EcoRI, BamHI, HindIII, XhoI, NotI]), seq, linear=not circular)
cuts = sorted((pos, str(enz)) for enz, sites in analysis.full().items() for pos in sites)

for i, (pos, enz) in enumerate(cuts):
    nxt = cuts[(i + 1) % len(cuts)][0]
    span = (nxt - pos) if nxt > pos else (seq_len - pos) + nxt   # wrap on circular
    last = (i == len(cuts) - 1)
    dist = span if (circular or not last) else seq_len - pos
    print(f'{pos:6d} bp ({pos / seq_len:5.1%}) {enz:8s} -> next in {dist} bp')
```

## Graphical Map (matplotlib)

**Goal:** A figure with the molecule as an axis and a labeled tick per cut site.

**Approach:** Draw the backbone, place a vertical tick at each `search()` position, and stack enzymes on separate rows. Write the figure only to a path the caller names (so running this does not litter the working directory).

```python
import matplotlib
matplotlib.use('Agg')                  # headless; no display needed
import matplotlib.pyplot as plt
from Bio.Restriction import EcoRI, BamHI, HindIII

def draw_map(seq, enzymes, out_path):
    seq_len = len(seq)
    fig, ax = plt.subplots(figsize=(10, 2 + 0.4 * len(enzymes)))
    ax.hlines(0, 0, seq_len, color='black')
    for row, enz in enumerate(enzymes, start=1):
        for pos in enz.search(seq):
            ax.vlines(pos, row - 0.3, row + 0.3, color='C0')
            ax.text(pos, row + 0.35, str(pos), ha='center', va='bottom', fontsize=7)
        ax.text(-0.02 * seq_len, row, str(enz), ha='right', va='center')
    ax.set_xlim(0, seq_len); ax.set_yticks([]); ax.set_xlabel('position (bp)')
    fig.savefig(out_path, dpi=200, bbox_inches='tight'); plt.close(fig)

# draw_map(record.seq, [EcoRI, BamHI, HindIII], 'my_map.png')   # caller supplies the path
```

## Map Against GenBank Features

```python
from Bio import SeqIO
from Bio.Restriction import RestrictionBatch, Analysis, EcoRI, BamHI

record = SeqIO.read('plasmid.gb', 'genbank')
analysis = Analysis(RestrictionBatch([EcoRI, BamHI]), record.seq, linear=False)

for enzyme, sites in analysis.with_sites().items():
    for pos in sites:
        hits = [f.qualifiers.get('label', f.qualifiers.get('gene', [f.type]))[0]
                for f in record.features
                if int(f.location.start) <= pos <= int(f.location.end)]
        print(f'{enzyme} at {pos}: {", ".join(hits) or "intergenic"}')
```

## Ordering Sites From A Gel (Classical Mapping)

When the sequence is unknown, a map is reconstructed from fragment sizes, not read off positions. The logic, in order of power:

- **Single digest** gives fragment sizes but not their order. A circular molecule cut n times gives n fragments; a linear one gives n+1.
- **Double digest** orders sites: run enzyme A alone, B alone, and A+B together. A single-digest fragment that disappears and is replaced by two smaller ones in the double digest contains a B site, which is thereby located inside that fragment. Iterate, enforcing that all fragment sizes sum to the molecule length. In practice one enzyme pair often admits several orderings consistent with the same band sizes (co-migrating or symmetric fragments); resolving a unique map needs additional enzymes or the partial-digest method below.
- **Partial digest with end labeling** (Smith-Birnstiel) measures positions directly: label one end, cut only a random subset of sites, and each labeled partial runs from the labeled end to one site, so its size is that site's distance from the labeled end. This sidesteps the combinatorial ambiguity of double digests.

Maps from one enzyme pair are often ambiguous (co-migrating or symmetric fragments fit multiple orderings); resolving a unique map needs several enzymes and the sum-of-fragments constraint.

## Circular Fragment Distances

```python
def circular_distances(sites, seq_len):
    '''Fragment sizes around a circle from sorted cut positions.'''
    s = sorted(sites)
    spans = [s[i + 1] - s[i] for i in range(len(s) - 1)]
    return spans + [(seq_len - s[-1]) + s[0]]    # the wrap-around fragment closes the circle

frags = circular_distances(EcoRI.search(record.seq, linear=False), len(record.seq))
assert sum(frags) == len(record.seq)             # the circle must be fully accounted for
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AttributeError: ... 'format_as'` | Method is `format_output` | Use `Analysis.format_output()` to get the text as a string |
| Wrap-around fragment is too short on a plasmid | Used `seq_len - last_site` instead of `(seq_len - last) + first` | Close the circle across the origin |
| Site near the origin missing on a plasmid map | Built the map with `linear=True` | Pass `linear=False` for circular DNA |
| Running a mapping script litters PNG/TXT files | Wrote outputs to a hard-coded filename | Write only to a path the caller supplies (or a temp dir) |
| Two enzymes' sites cannot be ordered from one gel | Single digest gives sizes, not order | Add a double digest (or partial-digest end-labeling) and use the sum check |

## Related Skills

- restriction-sites - Find the cut positions a map is built from
- fragment-analysis - Fragment sizes and gel interpretation behind classical mapping
- enzyme-selection - Choose informative enzymes for a map
- data-visualization/genome-tracks - Richer graphical layouts for annotated maps
- sequence-io/read-sequences - Load FASTA or GenBank input

## References

- Smith HO, Birnstiel ML. A simple method for DNA restriction site mapping. Nucleic Acids Res. 1976;3(9):2387-2398. doi:10.1093/nar/3.9.2387
- Roberts RJ, Vincze T, Posfai J, Macelis D. REBASE: a database for DNA restriction and modification: enzymes, genes and genomes. Nucleic Acids Res. 2023;51(D1):D629-D630. doi:10.1093/nar/gkac975
<!-- END FILE: restriction-analysis/restriction-mapping/SKILL.md -->

## 子目录：restriction-analysis/restriction-sites

<!-- BEGIN FILE: restriction-analysis/restriction-sites/SKILL.md -->
---
name: bio-restriction-sites
description: Find restriction enzyme cut sites in DNA sequences using Biopython Bio.Restriction. Searches single enzymes, batches, or commercial enzyme sets and returns cut positions for linear or circular DNA. Use when locating where one or more restriction enzymes cut a sequence, screening a sequence for the presence or absence of a site, or counting how often an enzyme cuts.
tool_type: python
primary_tool: Bio.Restriction
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+ (API verified on 1.86)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Restriction.Analysis)` to check method names

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying. The
Analysis "cutters" methods in particular were renamed across versions (see Common Errors).

# Finding Restriction Sites

**"Find where this enzyme cuts my DNA"** -> Return the cut positions for one or more restriction enzymes along a linear or circular sequence.
- Python: `enzyme.search(seq, linear=...)` for one enzyme; `Bio.Restriction.Analysis(batch, seq, linear=...).full()` for many.

The one fact that governs every result: `search()` returns a **1-based position equal to the first base of the downstream fragment** (the base immediately 3' of the cut on the top strand), **not** the start of the recognition site. For EcoRI `G^AATTC` whose site starts at position 4, `search` reports 5 (the base after the cut). Confusing the cut position with the recognition-site start is the single most common bug in restriction code, and it propagates silently into fragment sizes and map coordinates.

## The Decisions That Shape A Site Search

| Decision | Options | When to pick which |
|----------|---------|--------------------|
| Enzyme scope | one enzyme / a curated `RestrictionBatch` / `CommOnly` / `AllEnzymes` | A named enzyme when the assay dictates it; a small batch for a cloning panel; `CommOnly` (623 buyable enzymes) when the answer must be an enzyme one can purchase; `AllEnzymes` (1088, includes non-commercial) only for exhaustive in-silico surveys |
| Topology | `linear=True` (default) / `linear=False` | `linear=False` for any plasmid, viral circle, or BAC. A circular molecule lets a site span the origin and changes fragment counts (see fragment-analysis) |
| Question | does it cut? / how often? / where? | `search()` for positions; `Analysis.with_N_sites(n)` for exact cut counts; `bool(search())` for a yes/no screen |

Use `CommOnly` not `AllEnzymes` by default: proposing an enzyme nobody sells wastes a wet-lab cycle. The README's legacy "800+" figure is stale; the installed database holds 1088 enzymes total, 623 commercially available.

## Search With One Enzyme

```python
from Bio import SeqIO
from Bio.Restriction import EcoRI

record = SeqIO.read('sequence.fasta', 'fasta')
seq = record.seq

sites = EcoRI.search(seq)              # list of 1-based cut positions, e.g. [5, 14]
print(f'EcoRI cuts {len(sites)} time(s) at {sites}')
if not sites:
    print('EcoRI does not cut this sequence')
```

## Search With A Batch Of Enzymes

**Goal:** Screen a sequence against several enzymes at once and keep only those that cut.

**Approach:** Build a `RestrictionBatch`, run `Analysis.full()` to get every enzyme's positions, then filter to cutters with `with_sites()`.

```python
from Bio.Restriction import RestrictionBatch, Analysis, EcoRI, BamHI, HindIII, XhoI

batch = RestrictionBatch([EcoRI, BamHI, HindIII, XhoI])
analysis = Analysis(batch, seq, linear=True)

cutters = analysis.with_sites()        # {enzyme: [positions]} only enzymes that cut
for enzyme, positions in cutters.items():
    print(f'{enzyme}: {positions}')
```

## Filter By Cut Count

**Goal:** Separate single-cutters (linearize a plasmid), double-cutters (excise an insert), and non-cutters (safe to carry through a digest).

**Approach:** `Analysis` exposes `with_N_sites(n)` for an exact count and `without_site()` for enzymes with no site. (The older `once_cutters()`/`twice_cutters()`/`only_dont_cut()` names do not exist in current BioPython.)

```python
from Bio.Restriction import Analysis, CommOnly

analysis = Analysis(CommOnly, seq, linear=False)   # circular plasmid

single_cutters = analysis.with_N_sites(1)          # {enzyme: [pos]} good for linearization
double_cutters = analysis.with_N_sites(2)          # {enzyme: [pos, pos]} good for excision
non_cutters    = analysis.without_site()           # {enzyme: []} safe in a multi-step digest
all_cutters    = analysis.with_sites()             # any number of sites

print(f'{len(single_cutters)} single-cutters, {len(non_cutters)} non-cutters')

# Pretty-print a chosen subset
analysis.print_as('map')
analysis.print_that(single_cutters)                # formats the dict you pass it
```

## Built-In Enzyme Collections

```python
from Bio.Restriction import AllEnzymes, CommOnly, Analysis

print(f'{len(AllEnzymes)} known enzymes, {len(CommOnly)} commercially available')

analysis = Analysis(CommOnly, seq)                 # default: only buyable enzymes
for enzyme, positions in analysis.with_sites().items():
    print(f'{enzyme}: {positions}')
```

## Linear vs Circular DNA

```python
from Bio.Restriction import EcoRI

sites_linear   = EcoRI.search(seq, linear=True)    # ends are free; no wrap-around
sites_circular = EcoRI.search(seq, linear=False)   # a site may span the origin
```

A circular search can find a site that straddles position 1, which a linear search misses. Always pass `linear=False` for plasmids; the fragment count and map differ (see restriction-analysis/fragment-analysis).

## Read An Enzyme's Cut Geometry

**Goal:** Know what ends an enzyme leaves before designing a ligation.

**Approach:** `elucidate()` draws the cut unambiguously; the boolean predicates and the signed `ovhg` summarize it. The sign convention is the trap: **negative `ovhg` is a 5' overhang, positive is a 3' overhang, zero is blunt.**

```python
from Bio.Restriction import EcoRI, KpnI, EcoRV

for enz in (EcoRI, KpnI, EcoRV):
    print(enz, enz.elucidate())        # EcoRI G^AATT_C ; KpnI G_GTAC^C ; EcoRV GAT^_ATC
    print(f'  site={enz.site} ovhg={enz.ovhg} ovhgseq={enz.ovhgseq!r}'
          f' 5prime={enz.is_5overhang()} 3prime={enz.is_3overhang()} blunt={enz.is_blunt()}')
# EcoRI.ovhg == -4  -> a 5' overhang (NOT +4). In elucidate, ^ = top-strand cut, _ = bottom-strand cut.
```

## Access Enzymes By Name

```python
from Bio.Restriction import AllEnzymes

if 'EcoRI' in AllEnzymes:
    ecori = AllEnzymes.get('EcoRI')
    sites = ecori.search(seq)
```

## Ambiguous And Interrupted Recognition Sites

Not every enzyme has a fixed 6-bp palindrome. Degenerate sites use IUPAC codes (HincII `GTYRAC`), and interrupted palindromes carry an unspecified N spacer (BstXI `CCANNNNNNTGG`, DraIII `CACNNNGTG`). Note what `is_ambiguous()` actually means in BioPython: it is True when the site or cut is ambiguous -- N-spacer / interrupted sites (BstXI, DraIII) and enzymes that cut outside their site -- but it is **False** for a fully IUPAC-degenerate site whose cut is fixed, such as HincII `GTYRAC` (BioPython reports that as `is_defined()`). So `is_ambiguous()` does not detect IUPAC degeneracy; read `enzyme.site` for the actual letters. Either way, the expected cut frequency for a degenerate or N-containing site is not a clean `1/4^n`, so do not estimate cutter rarity from site length alone for these enzymes.

```python
from Bio.Restriction import HincII, BstXI

for enz in (HincII, BstXI):
    print(enz, enz.site, 'ambiguous=', enz.is_ambiguous())
```

## Search Many Sequences

```python
from Bio import SeqIO
from Bio.Restriction import RestrictionBatch, Analysis, EcoRI, BamHI

batch = RestrictionBatch([EcoRI, BamHI])
for record in SeqIO.parse('sequences.fasta', 'fasta'):
    cutters = Analysis(batch, record.seq).with_sites()
    print(record.id, {str(e): p for e, p in cutters.items()})
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AttributeError: 'Analysis' object has no attribute 'once_cutters'` | Method renamed across BioPython versions | Use `with_N_sites(1)` / `with_N_sites(2)`; `without_site()` for non-cutters; `with_sites()` for any cutter |
| `AttributeError: ... 'print_that_cut'` / `'esite'` | These names do not exist | Use `print_as(...)` + `print_that(dct)`; read the cut with `elucidate()` |
| Fragment sizes or map coordinates off by a few bases | Treated `search()` output as the recognition-site start | The integer is the cut position = first base of the downstream fragment (1-based) |
| Site near the origin missed on a plasmid | Searched with `linear=True` | Pass `linear=False` for circular DNA |
| Reported a 5' overhang as 3' (or vice versa) | Misread the `ovhg` sign | Negative `ovhg` = 5' overhang, positive = 3' overhang, zero = blunt; confirm with `elucidate()` |
| Proposed enzyme cannot be purchased | Searched `AllEnzymes` | Search `CommOnly` when the answer must be a buyable enzyme |

## Related Skills

- restriction-mapping - Order cut sites and draw a map with inter-site distances
- enzyme-selection - Choose enzymes by cut frequency, overhang, methylation sensitivity, or compatible ends
- fragment-analysis - Turn cut positions into fragment sizes and gel patterns
- golden-gate-assembly - Screen a part for internal Type IIS sites before scarless assembly
- sequence-io/read-sequences - Load the FASTA or GenBank sequence to search

## References

- Roberts RJ, Vincze T, Posfai J, Macelis D. REBASE: a database for DNA restriction and modification: enzymes, genes and genomes. Nucleic Acids Res. 2023;51(D1):D629-D630. doi:10.1093/nar/gkac975
- Roberts RJ, Belfort M, Bestor T, et al. A nomenclature for restriction enzymes, DNA methyltransferases, homing endonucleases and their genes. Nucleic Acids Res. 2003;31(7):1805-1812. doi:10.1093/nar/gkg274
<!-- END FILE: restriction-analysis/restriction-sites/SKILL.md -->

<!-- END CATEGORY: restriction-analysis -->

