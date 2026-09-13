# Science and Mathematics Verification Rules

## Chemical Equations

### The hard rule

No chemical equation goes into output without being run through the balance checker script (`scripts/balance_equation.py`). If the script reports that atoms do not balance, the equation is wrong and must be fixed before delivery.

### What to verify

1. **Atom balance.** Count atoms of each element on both sides. They must be equal.
2. **Charge balance.** For ionic equations, total charge must be equal on both sides.
3. **Reaction conditions.** Temperature, catalyst, solvent, pressure — include if known and relevant. If you do not know the conditions, do not invent them.
4. **Product correctness.** The products must be chemically plausible. Balancing a wrong equation gives a balanced but incorrect result. Verify products against a textbook or reputable source (e.g., PubChem, IUPAC Gold Book, established textbook).
5. **State symbols.** Include (s), (l), (g), (aq) when relevant and known. Do not guess if unsure.

### Common errors

- Forgetting diatomic elements (H₂, O₂, N₂, F₂, Cl₂, Br₂, I₂)
- Incorrect formulas for common compounds (e.g., writing NaCl₂ instead of NaCl)
- Balancing redox reactions without considering half-reactions
- Mixing up combustion products (complete vs. incomplete combustion)
- Forgetting that some reactions are reversible (⇌ vs →)

### Source hierarchy

| Tier | Source | Use for |
|---|---|---|
| 1 | IUPAC publications, NIST Chemistry WebBook, PubChem | Compound properties, CAS numbers, reaction data |
| 2 | Established textbooks (e.g., Clayden, Atkins, Vollhardt) | Reaction mechanisms, standard conditions |
| 3 | Peer-reviewed papers | Specific reactions, novel compounds |
| 4 | Reputable educational sites (Khan Academy, LibreTexts) | General chemistry, cross-checking |
| 5 | Unvetted websites, forums, AI-generated content | Never as sole source |

## Physical Constants

Physical constants must be stated with their CODATA value and year. Do not use memorized approximate values when precision matters.

| Constant | CODATA source |
|---|---|
| Speed of light c | 299,792,458 m/s (exact) |
| Planck constant h | 6.62607015 × 10⁻³⁴ J·s (exact, post-2019 SI) |
| Boltzmann constant k | 1.380649 × 10⁻²³ J/K (exact) |
| Avogadro constant Nₐ | 6.02214076 × 10²³ mol⁻¹ (exact) |
| Gravitational constant G | 6.67430 × 10⁻¹¹ N·m²/kg² (CODATA 2018, with uncertainty) |
| Electron mass mₑ | 9.1093837015 × 10⁻³¹ kg (CODATA 2018) |
| Gas constant R | 8.314462618 J/(mol·K) (exact) |

Rules:
- For constants with exact values (post-2019 SI redefinition), state "exact".
- For constants with measurement uncertainty, state the value and the uncertainty or cite the CODATA year.
- Do not mix values from different CODATA years.
- When a calculation uses a constant, note which value was used.

## Mathematical Calculations

### The hard rule

All numerical calculations in output must be performed by code. Mental arithmetic is not permitted for:
- Arithmetic beyond single-digit operations
- Percentages, ratios, proportions
- Weighted averages
- Currency or unit conversions
- Financial calculations (NPV, IRR, WACC, DCF)
- Statistical calculations (mean, standard deviation, regression)
- Any result where an error would change the conclusion

### How to calculate

Use `scripts/calc.py` or any code execution tool. Show:
1. The formula used
2. The input values with units
3. The result with appropriate precision

```
Example:
WACC = (E/V) × Re + (D/V) × Rd × (1-T)
E = 500B, D = 100B, V = 600B
Re = 10.5%, Rd = 5%, T = 21%
WACC = (500/600)(0.105) + (100/600)(0.05)(0.79)
     = 0.0875 + 0.00658
     = 9.41%
```

### Precision rules

- Match precision to input quality. An estimate from rough inputs does not get four decimal places.
- When propagating significant figures, the result should have no more significant figures than the least precise input.
- Round only the final result. Keep full precision during intermediate steps.
- If a result is sensitive to an input (e.g., DCF terminal value), show a sensitivity range rather than a single number.

### Formula verification

- State every formula before applying it.
- Define every variable.
- If a formula has multiple forms (e.g., different WACC conventions), state which one you are using and why.
- If the formula is domain-specific (e.g., Black-Scholes), cite the source textbook or paper.

## Statistical Claims

When reporting statistical results, verify and state:

1. **Sample size (n).** A result without n is uninterpretable.
2. **Effect size.** Not just p-values. Cohen's d, r, odds ratio, or equivalent.
3. **Confidence interval or standard error.**
4. **Test used.** t-test, ANOVA, chi-square, etc.
5. **One-tailed vs two-tailed.**
6. **Whether the result is from the source or calculated by you.**
7. **Multiple comparison corrections** if applicable.

Do not state "X is significantly higher than Y" without the supporting statistics. Do not interpret p > 0.05 as "no effect" — it means the study did not find evidence of an effect at that threshold.

## Biological and Medical Claims

Biology and medicine have particularly high stakes and particularly common errors.

1. **Distinguish evidence levels:**
   - Meta-analysis / systematic review of RCTs
   - Individual RCT
   - Cohort / case-control study
   - Cross-sectional survey
   - In vitro / animal study
   - Case report / expert opinion
   State the evidence level. Do not present an animal study result as a clinical finding.

2. **Do not conflate association with causation.** "X is associated with Y" from an observational study is not "X causes Y."

3. **Sample and population matter.** A result in one population (e.g., adult males in Europe) may not generalize to another (e.g., children in Asia).

4. **Drug names and doses.** Verify both the generic name and the dose. Distinguish mg from mL. Verify the route of administration. Do not recommend doses — state what the study used.

5. **Mechanism claims.** "X inhibits enzyme Y" requires direct biochemical evidence, not just correlation with a downstream effect.

6. **Primary source.** For medical claims, find the original clinical study or review article. Press releases and news articles are not primary sources.

## Source Hierarchy for Science

| Tier | Source |
|---|---|
| 1 | NIST, IUPAC, CODATA, official standards bodies |
| 2 | Peer-reviewed papers in reputable journals (Nature, Science, Cell, PNAS, discipline-specific journals) |
| 3 | Established textbooks and reference works |
| 4 | Reputable scientific organizations (WHO, CDC, NIH, NHS, professional societies) |
| 5 | Reputable science journalism (Nature News, Science News, well-edited popular science) |
| 6 | General news media |
| 7 | Blogs, social media, unsourced websites |

Tier 1-2 sources are required for specific numerical claims. Tier 3-4 may be used for context and cross-checking. Tier 5-7 are not acceptable as sole sources for factual claims.
