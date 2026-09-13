# Financial Data Verification Rules

## Source Hierarchy

Use the most authoritative source available. When sources conflict, the higher-tier source wins.

| Tier | Sources | Use for |
|---|---|---|
| 1 (Primary) | Company 10-K/10-Q/8-K, annual reports, quarterly reports, exchange filings, official press releases on company IR sites | Financial statement line items, guidance, share counts, corporate actions |
| 2 (Regulatory/official) | SEC EDGAR, exchange websites (NYSE/NASDAQ/HKEX), central bank statistics, government statistics agencies, IMF/World Bank | Regulatory filings, macroeconomic data, official statistics |
| 3 (Reputable data aggregators) | Bloomberg, Reuters, FactSet, Wind, Yahoo Finance, Google Finance, S&P Capital IQ | Real-time prices, market cap, consensus estimates, multiples |
| 4 (Secondary) | Financial press (WSJ, FT, Nikkei, Caixin), reputable industry reports, sell-side research | Context, analyst estimates, industry data — always cross-check with Tier 1-3 |
| 5 (Unreliable) | Social media, blogs, forums, unsourced data aggregators | Never use as sole source for a numerical claim |

**Rule:** Every financial figure in the output must be traceable to at least one Tier 1-3 source. Tier 4 requires cross-checking against Tier 1-3.

## What Must Be Verified

Every item below requires a source lookup at the time of writing. None of these may come from training data memory:

### Company Financials
- Revenue, net income, operating income, EPS (GAAP and non-GAAP)
- Revenue growth rates (YoY, QoQ)
- Margins (gross, operating, net)
- Balance sheet items (cash, debt, total assets, equity)
- Cash flow items (OCF, capex, FCF)
- Segment revenue and operating income
- Guidance (forward revenue, EPS, margins)
- Share count (basic and diluted)

### Market Data
- Current and recent stock prices (with timestamp)
- Market capitalization
- Trading multiples (P/E, EV/EBITDA, P/B, P/S) — specify TTM or NTM
- 52-week high/low
- Trading volume
- Short interest
- Dividend yield, payout ratio

### Valuation Inputs
- Beta
- Risk-free rate (specify which bond, what date)
- Equity risk premium (specify source and date)
- WACC components
- Comparable company multiples (each company's figures must be sourced)

### Macro Data
- GDP growth, CPI, PPI, PMI, unemployment
- Interest rates (central bank policy rate, bond yields)
- Exchange rates (with timestamp)
- Money supply (M2, etc.)
- Trade data

## Verification Process

### For company financials:

1. Search for the company's most recent filing or earnings release on its investor relations site or SEC EDGAR / HKEX / relevant exchange.
2. Locate the specific figure in the filing. Do not rely on a screenshot or a secondary source's summary if you can access the primary.
3. Record: figure, period (e.g., "FY2025 Q3"), reporting currency, source (filing type + date), and URL if available.
4. If using non-GAAP figures, note the reconciliation to GAAP. Companies report non-GAAP differently; do not compare non-GAAP across companies without checking their definitions.

### For market data:

1. Fetch current data from a Tier 3 source (Yahoo Finance, Google Finance, Wind).
2. Record the timestamp. Market data changes during trading hours. "As of 2026-08-24 16:00 ET" is required.
3. For multiples, specify the basis: TTM (trailing twelve months) or NTM (next twelve months / consensus). A P/E of "15x" without TTM/NTM is meaningless.
4. Cross-check market cap against share count × price if precision matters.

### For macro data:

1. Use the official source (central bank, statistics agency) for the most recent release.
2. Note whether the figure is preliminary, revised, or final.
3. For forecasts or consensus, label them as forecasts and attribute the source.

## Cross-Checking Rules

High-stakes figures require two independent sources:

- **Always cross-check:** Revenue, net income, EPS, market cap, current stock price, any figure used in valuation
- **Cross-check method:** Find the figure in the primary filing (Tier 1), then confirm it against a data aggregator (Tier 3). If they disagree, use the filing.
- **When sources disagree:** Report both figures and identify which you used and why. Example: "Company reports Q3 revenue of $23.5B (10-Q filed 2025-10-28); Yahoo Finance lists $23.4B, likely due to rounding or restatement. This analysis uses the filing figure."

## Currency and Units

- Always state the reporting currency: RMB, USD, HKD, EUR.
- When comparing across companies or converting, state the exchange rate and date used.
- Be explicit about units: million, billion, trillion. "Revenue 23.5B" without a currency marker is incomplete.
- For Chinese companies, distinguish RMB-reported figures from USD-reported figures (e.g., Alibaba reports in RMB; ADR price is in USD). Do not mix without conversion.

## Time Period Labels

- Fiscal year vs. calendar year: Many companies have non-calendar fiscal years. "FY2025" may end March 2025, June 2025, or December 2025 depending on the company. Always specify the period end date.
- Quarter labels: "Q3" is ambiguous. Use "Q3 FY2025 (ending September 30, 2025)" or the exact date range.
- TTM: Specify the ending date. "TTM as of 2025-09-30."
- "Current" or "latest": Always replace with the actual date.

## Common Pitfalls

1. **Restated figures.** Companies restate prior periods. If comparing year-over-year, use the restated prior-period figure from the most recent filing, not the originally reported figure.
2. **Non-GAAP vs GAAP.** A company may report "adjusted EPS" that excludes stock-based compensation. Do not present non-GAAP as GAAP.
3. **Seasonality.** Q4 retail revenue is not comparable to Q1 without noting seasonality.
4. **Currency fluctuation.** A company reporting in EUR may show USD revenue changes that reflect FX rather than operations. Note constant-currency growth if available.
5. **Consensus estimates.** "Consensus expects revenue of $24B" requires a source (e.g., "Bloomberg consensus as of 2025-10-25, n=18 analysts"). Do not state consensus without attribution.
6. **Market cap changes.** If using a market cap from a screener, note that it changes with price and share count. For valuation, calculate it from current price × diluted shares outstanding.
