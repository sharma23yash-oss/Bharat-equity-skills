# Benchmarks, Formulas & Scoring Rubrics

Read this at the start of any analysis. These are the precise definitions, default threshold bands, scoring rubrics, and sector substitutions referenced by SKILL.md. **Bands are heuristics for context, not hard rules** — adjust for sector, cycle, and business model, and say so when you do.

## Contents
1. Minimum data set to run a full analysis
2. Forensic accounting — formulas & flag bands
3. Distress & manipulation scores (Altman Z, Beneish M, Piotroski F)
4. DuPont — formulas
5. Smart Beta — factor formulas & bands
6. Valuation — formulas
7. Sector substitution map (when the standard metrics don't apply)

---

## 1. Minimum data set to run a full analysis

If the user gives only a name and no data, request these before producing a verdict (don't fabricate them):
- 3–5 years of: Revenue, EBITDA, EBIT, PBT, PAT, CFO
- Balance sheet: Total Assets, Equity, Total Debt, Receivables, Inventory, Payables, Current Liabilities
- Interest expense, Other Income, Tax expense
- Share count / EPS, Book Value per Share
- Current price, 50/100/200-DMA (or enough price history to derive them)
- For Indian names: promoter holding %, pledge %, contingent liabilities
- Sector / industry label

Partial data is fine — run every check the data supports, then list what's missing and what it would change.

---

## 2. Forensic accounting — formulas & flag bands

| Metric | Formula | 🟢 Green | 🟡 Amber | 🔴 Red |
|---|---|---|---|---|
| Earnings quality | Σ CFO ÷ Σ PAT (3–5 yr) | ≥ 0.9 | 0.7–0.9 | < 0.7 |
| DSO (Debtor Days) | (Receivables ÷ Revenue) × 365 | falling / stable | rising mildly | rising fast vs sales |
| Receivables vs sales | Receivables growth ÷ Revenue growth | ≤ 1.0× | 1.0–1.5× | > 1.5× |
| DIO (Inventory Days) | (Inventory ÷ COGS) × 365 | stable | rising | rising vs sales |
| DPO (Payable Days) | (Payables ÷ COGS) × 365 | — | — | abnormal stretch |
| Cash Conversion Cycle | DSO + DIO − DPO | falling / stable | rising | rising vs flat sales |
| Interest Coverage | EBIT ÷ Interest | > 4 | 2.5–4 | < 2.5 (<1.5 distress) |
| Net leverage | Net Debt ÷ EBITDA | < 1.5 | 1.5–3 | > 3 |
| Other-income reliance | Other Income ÷ PBT | < 10% | 10–25% | > 25% |
| Effective tax rate | Tax ÷ PBT | near statutory | mild gap | far below statutory |
| Promoter pledge (India) | Pledged ÷ promoter holding | 0% | < 25% | ≥ 25% or rising |
| Contingent liabilities | Contingent liab ÷ Net worth | < 25% | 25–50% | > 50% |

Capital Employed = Total Assets − Current Liabilities (or Equity + Total Debt — state which you used).

Auditor resignation, qualification, or change, and material related-party loans/advances, are standalone 🔴 regardless of ratios.

---

## 3. Distress & manipulation scores

**Altman Z-score (manufacturing, non-financial):**
Z = 1.2·(WC/TA) + 1.4·(RE/TA) + 3.3·(EBIT/TA) + 0.6·(MktCap/Total Liab) + 1.0·(Sales/TA)
- Z > 2.99 = safe · 1.81–2.99 = grey · < 1.81 = distress
- For emerging-market / non-manufacturing, use the Z″ variant (drop the sales term) and note the caveat.

**Piotroski F-Score (0–9, one point each):**
Profitability: positive ROA; positive CFO; ROA improving YoY; CFO > Net Income (accruals).
Leverage/liquidity: lower long-term debt ratio YoY; higher current ratio YoY; no new shares issued.
Efficiency: higher gross margin YoY; higher asset turnover YoY.
- 7–9 = strong quality · 4–6 = neutral · 0–3 = weak. Report the score and which tests failed.

**Beneish M-score (manipulation likelihood):** conceptual flag. If the granular inputs (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA) aren't available, say so and rely on the earnings-quality and receivables tests instead of computing a false number.

---

## 4. DuPont — formulas

**3-step:** ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
= (PAT/Sales) × (Sales/Total Assets) × (Total Assets/Equity)

**5-step (use this as default):**
ROE = (EBIT/Sales) × (Sales/Total Assets) × (PBT/EBIT) × (PAT/PBT) × (Total Assets/Equity)
= Operating Margin × Asset Turnover × Interest Burden × Tax Burden × Financial Leverage

- Operating Margin × Asset Turnover = operating engine.
- Interest Burden < 1 quantifies the drag from debt; Tax Burden < 1 the drag from tax.
- Financial Leverage rising while ROE rises = leverage-manufactured return.

**ROCE = EBIT ÷ Capital Employed.** Value created only if ROCE > WACC. If WACC isn't given, use a reasonable proxy band (Indian large-cap equity cost ~11–13%) and label it an assumption.

---

## 5. Smart Beta — factor formulas & bands

**Quality:** Piotroski (above); margin consistency (std-dev of EBITDA margin across years — lower is better); ROE & ROCE each consistently above ~15% is a quality marker; low accruals (CFO ≥ PAT).

**Value (judge vs sector median AND own 5-yr history):**
- EV/EBITDA = (MktCap + Net Debt) ÷ EBITDA
- PEG = P/E ÷ earnings growth %  (≈1 fair, <1 cheap-for-growth, >2 rich)
- P/B = Price ÷ Book Value per Share
- Graham Number = √(22.5 × EPS × BVPS) — price below it is the Graham "defensive value" zone
- Earnings Yield = EBIT ÷ EV
- FCF Yield = FCF ÷ MktCap

**Momentum:**
- DMA trend: price vs 50/100/200-DMA
- Golden cross = 50-DMA crosses above 200-DMA (bullish); death cross = the reverse
- Price momentum ≈ 12-month return excluding the most recent month
- Earnings acceleration = change in YoY growth rate QoQ (is the growth rate itself rising?)
- RSI: >70 overbought, <30 oversold — context only

---

## 6. Valuation — formulas

- EV = Market Cap + Total Debt − Cash & equivalents
- FCF = CFO − Capex
- Fair-value framing: triangulate (EV/EBITDA × sector multiple), (P/E × normalised EPS), and Graham Number into a **range**. State every assumption. Never present a single-point price as certainty.

---

## 7. Sector substitution map

When the standard non-financial toolkit doesn't fit, swap in the right metrics and explicitly note that CCC / EV-EBITDA / standard DuPont don't apply as usual.

**Banks:** Net Interest Margin (NIM), GNPA / NNPA, Provision Coverage Ratio, CASA ratio, Cost-to-Income, Credit cost, ROA (lead metric — target >1%), ROE, CAR / Tier-1, Slippage ratio. Value on **P/B** and P/ABV, not EV/EBITDA. DuPont for banks is ROA-based (NII + other income − opex − provisions − tax, all / assets) × leverage.

**NBFCs:** all of the above plus Net Interest Spread, ALM / liability mix, GNPA, Capital Adequacy, leverage (Debt/Equity is structurally high — judge against peers, not a generic cap).

**Insurance:** VNB & VNB margin, APE, Embedded Value, persistency, combined ratio (general), solvency ratio. Value on P/EV.

**FMCG / Consumer:** gross & EBITDA margin and their stability, volume vs value growth, working-capital intensity (often negative — a strength), ROCE, cash conversion, A&P spend. Premium multiples are normal — judge vs own history and peers.

**IT services:** revenue growth (CC), EBIT margin, attrition, utilisation, deal TCV / book-to-bill, USD realisation, cash conversion (typically high). Net-cash balance sheets — leverage tests are largely n/a.

**Capital goods / infra / EPC:** order book & book-to-bill, execution cycle, working-capital intensity, debtor days (watch closely — often the red flag), interest coverage, ROCE through the cycle.

**Commodities / cyclicals:** judge margins and ROCE across a full cycle, not a single peak/trough year; net debt through the cycle; replacement-cost / EV-per-tonne style metrics.

**Pharma:** R&D as % of sales, US vs domestic mix, USFDA observation status (a forensic/risk item), gross margin, ANDA pipeline.

If a sector isn't listed, reason from first principles about what drives its economics and risk, and state the metrics you're using and why.
