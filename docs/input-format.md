# Input format

A company file is JSON with a `years` array, ordered **oldest first**. Two years are needed for the change-based checks (Piotroski, Beneish, all the YoY trends); one year is enough for Altman and DuPont.

```json
{
  "name": "Some Company Ltd",
  "ticker": "SOME",
  "sector": "Auto",
  "is_financial": false,
  "years": [ { "label": "FY24", "...": 0 }, { "label": "FY25", "...": 0 } ]
}
```

Set `is_financial: true` for banks and NBFCs. Beneish and Altman are then suppressed, because neither is defined for a balance sheet where deposits are the liability.

## Conventions

- **One unit throughout.** ₹ crore by convention. Nothing is unit-aware, so consistency is what matters.
- **Percentages as percentage points.** `promoter_pledge_pct: 38.0` means 38%, not 0.38. These are the only fields that work this way, and they are named `_pct`.
- **Omit what you don't have.** A missing field is reported as a gap. Do not put in a zero to make the file look complete — a zero is an assertion.

## Fields

### Profit & loss
`revenue` · `cogs` · `gross_profit` · `sga` · `ebitda` · `depreciation` · `ebit` · `interest` · `other_income` · `pbt` · `tax` · `pat`

`gross_profit` is derived from `revenue - cogs` when absent.

### Balance sheet
`total_assets` · `current_assets` · `current_liabilities` · `inventory` · `receivables` · `payables` · `net_block` · `cwip` · `intangibles` · `total_liabilities` · `long_term_debt` · `short_term_debt` · `equity` · `reserves` · `shares_outstanding`

`net_block` is PPE net of depreciation. `equity` is shareholders' funds / net worth. `reserves` stands in for retained earnings in the Altman X2 term.

### Cash flow
`cfo` — cash from operations. The single most important field in the file: `CFO / PAT` is the first check run and can veto on its own.

### Governance (India-specific)
`promoter_holding_pct` · `promoter_pledge_pct` · `related_party_txns` · `contingent_liabilities` · `auditor_qualified` (bool) · `auditor_changed` (bool)

These come from the shareholding pattern and the notes to accounts, not the face of the statements. They are what the engine exists for — a file without them still runs, but it runs as a generic screen.

## Where the figures come from

- **Screener.in** — the fastest route; the ratios page and the balance-sheet tab cover most fields.
- **Annual report** — the only source for contingent liabilities, related-party detail and the auditor's opinion.
- **Exchange filings (NSE/BSE)** — the shareholding pattern gives promoter holding and pledge, updated quarterly.

Pledge is disclosed as a percentage of promoter holding, not of total equity. Use it as disclosed; the bands assume that convention.
