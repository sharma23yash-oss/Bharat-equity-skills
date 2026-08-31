# Contributing

The most valuable contributions to this repository are **new India-specific checks** and **sector benchmark sets** — the things a US-derived library cannot supply.

## What's wanted

- **Additional red flags.** Anything in the SEBI/LODR disclosure regime, the notes to accounts, or the shareholding pattern that reliably precedes a loss of capital. Auditor-related, promoter-related and off-balance-sheet signals are the richest seams.
- **Sector benchmark sets.** The current thresholds are generalist. A capital-goods company and an FMCG company should not be judged against the same cash-conversion-cycle band.
- **BFSI asset-quality scoring.** Banks and NBFCs currently have Beneish and Altman suppressed with nothing offered in their place. GNPA, NNPA, PCR, CAR, NIM and slippage ratios belong in a dedicated register.
- **Screener.in / Tijori import adapters.** Anything that removes hand-typing from the workflow.

## Ground rules for a new check

1. **Never invent a number.** If an input is missing, the check must return `None` and name itself in `missing_inputs`. A zero that silently becomes a score is worse than no score.
2. **State the mechanism.** Every check carries a `read` explaining what management would be doing for the number to look that way. A flag without a mechanism is not actionable.
3. **Cite the band.** Thresholds go in the docstring with a reason. "Below 0.8" needs to be defensible.
4. **Refuse where the model doesn't apply.** If a check is meaningless for banks, say so explicitly rather than printing a number.
5. **Add a test.** Especially one proving the check reports a gap rather than a default when its input is absent.

## Running the suite

```bash
pip install pytest
python -m pytest tests/ -q
```

## Skills

Skills in `skills/` are Claude Agent Skills. If you're adding one, keep the frontmatter `description` specific enough that it fires on the right requests and not on adjacent ones, and keep the prose reasoning-first — a skill that only executes a checklist produces worse research than one that explains why each test exists.
