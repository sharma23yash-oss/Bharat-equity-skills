"""Assemble the scores into the desk note the skills expect as input.

The output is deliberately Markdown: it is meant to be pasted straight into a
Claude session running one of the skills in ``skills/``, which then supplies the
narrative judgement the numbers cannot. The split is the whole design — Python
computes what is arithmetic, the skill reasons about what is not.
"""

from __future__ import annotations

from .india_flags import india_red_flags
from .models import Company
from .result import Flag, ScoreResult
from .scores import altman_z_em, beneish_m_score, dupont_5step, piotroski_f_score


def run_all(company: Company) -> list[ScoreResult]:
    return [
        india_red_flags(company),
        piotroski_f_score(company),
        beneish_m_score(company),
        altman_z_em(company),
        dupont_5step(company),
    ]


def _table(result: ScoreResult) -> list[str]:
    if not result.checks:
        return []
    lines = ["", "| Check | Value | Benchmark | Flag | Read |",
             "| --- | ---: | --- | :---: | --- |"]
    for c in result.checks:
        lines.append(
            f"| {c.name} | {c.format_value()} | {c.benchmark or '—'} | "
            f"{c.flag.symbol} | {c.read or '—'} |"
        )
    return lines


def to_markdown(company: Company) -> str:
    """Render a full scorecard for ``company``."""
    results = run_all(company)
    out: list[str] = []

    header = f"# {company.name}"
    if company.ticker:
        header += f" ({company.ticker})"
    header += " — Quantitative Scorecard"
    out.append(header)

    meta = []
    if company.sector:
        meta.append(f"Sector: {company.sector}")
    if company.years:
        meta.append(f"Period: {company.years[0].label} → {company.years[-1].label}")
    if company.is_financial:
        meta.append("BFSI — Beneish and Altman suppressed by design")
    if meta:
        out.append(f"*{' · '.join(meta)}*")

    # Headline strip
    out.append("")
    out.append("## Headline")
    out.append("")
    out.append("| Score | Result | Band |")
    out.append("| --- | ---: | --- |")
    for r in results:
        out.append(f"| {r.name} | {r.format_score()} | {r.flag.symbol} {r.band or '—'} |")

    # Detail
    for r in results:
        out.append("")
        out.append(f"## {r.name}")
        if r.band:
            out.append("")
            out.append(f"**{r.flag.symbol} {r.band}**")
        out.extend(_table(r))
        if r.missing_inputs:
            out.append("")
            out.append("**Missing inputs — these checks were not run:**")
            for m in r.missing_inputs:
                out.append(f"- {m}")

    # The honesty footer. A verdict built on invented numbers is the one thing
    # that ends careers, so the note states its own coverage.
    total_missing = sum(len(r.missing_inputs) for r in results)
    out.append("")
    out.append("---")
    out.append("")
    if total_missing:
        out.append(
            f"*{total_missing} check(s) could not be run for want of data. "
            "No value has been estimated or interpolated. Supply the missing "
            "line items to close the gaps.*"
        )
    else:
        out.append("*All checks ran on supplied data. No values were estimated.*")
    out.append("")
    out.append(
        "*Quantitative output only. Not investment advice; not a recommendation "
        "to buy or sell any security.*"
    )
    return "\n".join(out)


def verdict_flag(company: Company) -> Flag:
    """The worst flag across all scores — the desk's triage colour."""
    order = {Flag.RED: 3, Flag.AMBER: 2, Flag.GREEN: 1, Flag.NA: 0}
    return max((r.flag for r in run_all(company)), key=lambda f: order[f])
