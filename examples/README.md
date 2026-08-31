# Worked examples

| File | Demonstrates |
| --- | --- |
| [`trap.md`](trap.md) | A value trap that scores 8/9 on Piotroski and lands in Altman's safe zone, while the India register vetoes it four times over |
| [`clean.md`](clean.md) | A genuine compounder: 9/9, clean register, 21.5% ROE, operationally driven rather than borrowed |

Regenerate both:

```bash
python -m bharat_scores examples/data/*.json --out examples/
```

## These are synthetic

The two fixtures in `data/` are **constructed teaching cases, not real companies.** They exist to exercise every code path and to show what each failure mode looks like in numbers.

They are not disguised real companies, and no figure here should be attributed to any listed entity.

For real analysis, bring real figures: copy a fixture, replace the numbers from a Screener.in export or the annual report, and run it. See [`../docs/input-format.md`](../docs/input-format.md).

## What the contrast is for

`trap.md` is the argument for this repository's existence. Every score in it that comes from the US academic literature says the company is fine:

- Piotroski 8/9 — "strong"
- Altman Z'' 9.49 — "safe zone"
- DuPont — "operationally driven"

And the India-specific register says: profit is not converting to cash, the promoter has pledged 38% of his holding and added 26 points in a year while selling down his stake, 18% of revenue runs through related parties, contingent liabilities are three-quarters of net worth, and the auditor has qualified the opinion.

Both readings are computed from the same file. Only one of them would have kept you out.
