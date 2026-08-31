# bharat-equity-skills

**Forensic equity research for Indian listed companies — a Python scoring engine plus seven Claude Skills.**

Piotroski, Beneish and Altman were fitted on US companies. They do not know what a promoter pledge is. This repository adds the checks that actually predict permanent loss of capital in the Indian market, and pairs them with research skills that reason about the output.

---

## The problem, in one example

Here is a company that passes almost every standard academic screen:

| Score | Result | Verdict |
| --- | ---: | --- |
| Piotroski F-Score | **8 / 9** | 🟢 strong |
| Altman Z''-Score (EM) | **9.49** | 🟢 safe zone |
| Beneish M-Score | -1.61 | 🔴 likely manipulator |
| **India red-flag register** | **10 flags** | 🔴 **IMPAIRED** |

A US-derived screen would put this in your portfolio. Here is what the India register saw:

| Check | Value | Benchmark | Flag |
| --- | ---: | --- | :---: |
| CFO / PAT | 0.20x | > 0.8 | 🔴 |
| Promoter pledge | +38.0 pp | 0% clean · >10% severe | 🔴 |
| Pledge trend YoY | +26.0 pp | falling or flat | 🔴 |
| Promoter holding trend YoY | -3.0 pp | stable or rising | 🔴 |
| Related-party txns / revenue | 18.0% | < 5% | 🔴 |
| Contingent liabilities / net worth | 75.0% | < 25% | 🔴 |
| Receivables growth / revenue growth | 6.29x | < 1.5x | 🔴 |
| Auditor qualification | yes | none | 🔴 |

Profit that never became cash, a promoter pledging a fast-rising share of his own stock, cash leaving through related parties, and an auditor who declined to sign off cleanly. **Piotroski cannot see any of it.**

That gap is what this repository exists to close.

Reproduce the above:

```bash
python -m bharat_scores examples/data/synthetic-value-trap.json
```

---

## Quickstart

```bash
git clone https://github.com/sharma23yash-oss/bharat-equity-skills.git
cd bharat-equity-skills
python -m bharat_scores examples/data/synthetic-value-trap.json
```

No dependencies. Pure standard library, Python 3.10+.

To score your own company, copy `examples/data/synthetic-clean-compounder.json`, replace the figures from a Screener.in export or the annual report, and run it. Field reference: [`docs/input-format.md`](docs/input-format.md).

```python
from bharat_scores import Company, FiscalYear, to_markdown

company = Company(name="Some Company Ltd", ticker="SOME", years=[fy24, fy25])
print(to_markdown(company))
```

---

## What's in the box

### 1. The scoring engine — `bharat_scores/`

| Score | What it catches | Notes |
| --- | --- | --- |
| **India red-flag register** | Pledge, related-party transactions, contingent liabilities, auditor signals, earnings quality | The differentiating set. No US library has these. |
| **Piotroski F-Score** | Fundamental momentum across 9 binary signals | Scored only on signals the data supports |
| **Beneish M-Score** | Earnings manipulation, 8 variables | Refused for banks/NBFCs by design |
| **Altman Z''-Score** | Bankruptcy risk | Emerging-market variant — the right one for Indian listings |
| **DuPont, 5-step** | Whether ROE is earned or borrowed | Flags leverage-manufactured returns |

Two design decisions worth knowing about:

**It refuses to guess.** A missing input produces `data not provided` and a named gap in the report — never a zero that quietly becomes a score. Scores are reported out of the number of checks that could actually be run. A verdict built on invented numbers is the one thing that ends careers.

**It refuses to misapply.** Beneish and Altman are suppressed for banks and NBFCs, because neither model is defined for a balance sheet where deposits are the liability. The report says so rather than printing a meaningless number.

### 2. The skills — `skills/`

Seven [Claude Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) that take the engine's output and produce the judgement it cannot:

| Skill | Purpose |
| --- | --- |
| `institutional-equity-risk-strategist` | Full desk note: forensic → DuPont → smart beta → BUY/HOLD/SELL with invalidation triggers |
| `institutional-moat-governance-guardrail` | Durability of competitive advantage and governance quality |
| `corporate-governance-fraud-detector` | Promoter integrity, accounting manipulation, value-trap detection |
| `indian-equity-research-analyst` | Company research from annual reports, filings and earnings calls |
| `multibagger-hunter-opportunity-scanner` | Long-horizon compounder screening |
| `quantitative-stock-analysis-lab` | Factor and statistical work |
| `quarterly-results-breakdown` | Fast post-results teardown |
| `annual-report-redflag-analysis` | Red flags from the annual report itself |

Install by copying into your skills directory:

```bash
cp -r skills/* ~/.claude/skills/
```

The division of labour is the whole design: **Python computes what is arithmetic, the skills reason about what is not.** A ratio is a calculation. Whether a 38% promoter pledge is survivable given the company's refinancing calendar is a judgement.

---

## Worked examples

| File | What it demonstrates |
| --- | --- |
| [`examples/trap.md`](examples/trap.md) | A value trap that passes Piotroski and Altman |
| [`examples/clean.md`](examples/clean.md) | A genuine compounder: 9/9, clean register, 21.5% ROE, operationally driven |

**These are synthetic teaching fixtures, not real companies.** They are constructed to exercise every code path and to show what each failure mode looks like in numbers. Real figures belong to whoever pulls them — bring your own from Screener.in, the annual report, or an exchange filing.

---

## Why the India-specific checks matter

**Promoter pledge** has no US analogue. A promoter borrows against his own shareholding; when the price falls the lender sells; the selling drives the price down further and triggers more margin calls. It is the most reliable predictor of permanent capital loss in the Indian mid-cap universe, and the *trend* matters more than the level — a pledge rising from 0% to 2% is a signal, which is why this engine vetoes on it.

**Related-party transactions** are the standard route by which cash leaves a listed entity for a promoter-owned unlisted one.

**Contingent liabilities** are routinely larger than net worth in Indian infrastructure and capital-goods names, and are disclosed only in the notes to accounts.

**Auditor qualification or resignation** is, in India, very often the last public signal before a collapse.

More on the accounting particulars: [`docs/indian-accounting-notes.md`](docs/indian-accounting-notes.md).

---

## Development

```bash
pip install pytest
python -m pytest tests/ -q
```

21 tests, covering the DuPont identity closing exactly, Beneish reproducing a hand-worked value, band boundaries, the BFSI refusals, and — most importantly — that missing inputs are named rather than zeroed.

Contributions welcome, especially additional India-specific checks and sector benchmark sets. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Who built this

**Yash Sharma** — MBA Finance (MANIT / NIT Bhopal), previously equity research and DCF modelling at Trinity Financial Services. Writes at [YGL Pulse](https://www.linkedin.com/) and teaches the NISM Series-XV syllabus on YouTube.

The frameworks here are the ones I use on live names, not a textbook transcription.

---

## Licence and disclaimer

MIT — see [LICENSE](LICENSE).

**This is analytical tooling, not investment advice.** Nothing here is a recommendation to buy or sell any security. The scores are arithmetic on figures you supply; their quality depends entirely on the quality of those figures. Verify against primary sources — the annual report and exchange filings — before acting on anything. The author is not a SEBI-registered investment adviser.
