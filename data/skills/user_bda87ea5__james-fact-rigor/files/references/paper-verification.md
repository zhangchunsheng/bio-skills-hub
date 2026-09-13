# Paper and ML Model Verification Rules

## Core Principle

When describing a machine learning model, its architecture, training setup, or results, the original paper or official technical report is the primary source. Blog posts, tutorials, YouTube explanations, and secondhand summaries are useful for understanding but not for verifying specific claims. If the paper and a tutorial disagree, the paper wins. If the paper is silent on a detail, do not fill it in from a tutorial without labeling the source.

## What Must Be Verified

Every item below requires checking against the original paper or an official source:

### Architecture
- Model type (encoder-only, decoder-only, encoder-decoder, MoE, etc.)
- Number of layers (encoder layers, decoder layers)
- Hidden size / model dimension (d_model)
- Number of attention heads
- Feed-forward dimension (d_ff)
- Vocabulary size
- Context window / maximum sequence length
- Positional encoding method (learned, sinusoidal, RoPE, ALiBi)
- Normalization (LayerNorm, RMSNorm, pre-norm vs post-norm)
- Activation function (GELU, SwiGLU, ReLU)
- Attention type (MHA, MQA, GQA)
- Any architectural variants (e.g., flash attention, parallel residual)

### Scale
- Parameter count (total, and per sub-component if relevant)
- Number of layers by variant (Base/Large/XL, 7B/13B/70B)
- Training tokens
- Training compute (FLOPs)
- Model size variants and their naming

### Training
- Training dataset name and composition
- Batch size (and whether global or per-device)
- Optimizer and learning rate schedule
- Number of training steps
- Hardware used
- Training duration
- Pre-training objectives (MLM, CLM, RLHF, DPO, etc.)
- Fine-tuning methods if relevant

### Results
- Benchmark names and scores
- Evaluation methodology (few-shot, fine-tuned, zero-shot)
- Comparison baselines and their reported numbers
- Whether results are from the paper, reproduced, or from a leaderboard

### Provenance
- Paper title, authors, venue, year
- arXiv ID or DOI
- Whether the paper is peer-reviewed or a preprint
- Version differences (v1/v2/v3 on arXiv)
- Whether later papers have corrected or updated the results

## Verification Process

### Step 1: Locate the original paper

Search by paper title or model name on:
- arXiv (arxiv.org)
- Semantic Scholar (semanticscholar.org)
- Google Scholar
- Official conference proceedings (NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, CVPR, etc.)
- The model's official GitHub repository or tech report

If you cannot locate the original paper, do not describe the model's architecture in specific detail. State that the paper could not be found and provide only general information clearly labeled as unverified.

### Step 2: Read the relevant sections

For architecture claims, read:
- The architecture section (usually Section 2 or 3)
- The model configuration table (often in the appendix or experiments section)
- Any tables listing hyperparameters

For training claims, read:
- The training setup / experimental setup section
- Hyperparameter tables

For results, read:
- The evaluation section
- Results tables
- Appendix for additional results

### Step 3: Cross-check each claim

Create a verification table:

| Claim | Your initial value | Paper value | Match? |
|---|---|---|---|
| BERT-Base layers | "12" | 12 (Table 1) | ✅ |
| BERT-Base params | "~100M" | 110M (Table 1) | ⚠️ Imprecise — use 110M |
| BERT-Base heads | "12" | 12 (Table 1) | ✅ |
| BERT training steps | "1M" | 1,000,000 (Section 3.1) | ✅ |

If your initial value differs from the paper, the paper is correct. If the paper gives a range or "approximately", use the paper's language rather than inventing precision.

### Step 4: Handle version confusion

Many models have multiple versions. Before verifying, identify which version you are describing:

| Model | Common version confusion |
|---|---|
| BERT | BERT-Base (110M, 12 layers) vs BERT-Large (340M, 24 layers) |
| GPT | GPT-1 (117M) vs GPT-2 (1.5B) vs GPT-3 (175B) vs GPT-3.5 vs GPT-4 |
| LLaMA | LLaMA 1 (2048 context) vs LLaMA 2 (4096 context) vs LLaMA 3 (8192 context); 7B/13B/33B/65B vs 7B/13B/70B vs 8B/70B/400B |
| T5 | T5-Small/Base/Large/XL/XXL (different parameter counts) |
| Mistral | Mistral 7B vs Mixtral 8x7B vs Mixtral 8x22B |
| Qwen | Qwen 1.0 vs Qwen 1.5 vs Qwen 2 vs Qwen 2.5; 0.5B through 72B+ |

Always state the full version name. "LLaMA has a 4K context window" is wrong for LLaMA 1 (2K) and LLaMA 3 (8K+). "LLaMA 2 has a 4096-token context window" is correct and specific.

### Step 5: Benchmark scores

Benchmark scores are particularly error-prone because:
- Different papers use different evaluation protocols (zero-shot vs few-shot vs fine-tuned)
- Scores are updated in later versions or erratum
- Leaderboards change over time
- Models may be evaluated with different prompts or frameworks

Rules:
- State which paper or leaderboard the score comes from, and the date
- State the evaluation setting (e.g., "5-shot accuracy as reported in Table 3")
- If you find conflicting scores from the same paper (e.g., v1 vs v2), use the latest version and note the change
- If comparing models, ensure the same evaluation setting. A zero-shot score is not comparable to a 5-shot score.
- Do not average scores across different evaluation settings.

## Common Pitfalls

1. **Attributing later improvements to the original paper.** Flash Attention 2 was not in the original Transformer paper. GQA was not in the original GPT-3 paper. Do not anachronistically assign techniques to earlier models.

2. **Confusing parameter counts across variants.** "BERT has 340M parameters" is true for BERT-Large but false for BERT-Base. Always specify the variant.

3. **Reporting approximate parameter counts as exact.** "GPT-3 has 175B parameters" is well-established. But for newer models where the official count is "approximately 70B" or has not been disclosed, do not state a precise figure as fact.

4. **Confusing training tokens across versions.** LLaMA 1 trained on 1.4T tokens; LLaMA 2 trained on 2T tokens. These are not interchangeable.

5. **Relying on blog post diagrams.** Architecture diagrams in blog posts sometimes simplify or introduce errors. For specific dimensions and counts, go to the paper's tables.

6. **Ignoring erratum.** Some papers have later versions with corrected numbers. Check arXiv for version history.

7. **Conflating open and closed models.** For closed models (GPT-4, Claude, Gemini), many architecture details are not publicly disclosed. Do not present rumored or leaked details as confirmed. State what is officially confirmed and what is unconfirmed.

8. **Misattributing authorship.** Verify the author list and institutional affiliation. A paper from a research group is not necessarily authored by the person who popularized it.

## Output Format for Model Descriptions

When describing a verified model, include:

```
**[Model Name]** ([Paper title], [authors], [venue] [year])
- Architecture: [type], [N] layers, d_model=[X], [H] attention heads
- Parameters: [exact count from paper]
- Context window: [value] tokens
- Training: [dataset], [tokens] tokens, [optimizer]
- Key results: [benchmark score with setting and source table]
- Source: [arXiv ID or DOI], accessed [date]
```

For any field where the paper does not provide information, write "not specified in paper" rather than guessing.
