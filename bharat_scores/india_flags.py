"""India-specific forensic checks.

These are the tests that a US-derived scoring library does not have and cannot
easily acquire, because the failure modes they catch are specific to how Indian
promoter-controlled companies actually go wrong:

* **Promoter pledge** — a promoter borrowing against his own shareholding. When
  the price falls the lender sells, which drives the price down further. This is
  the single most reliable predictor of a permanent loss of capital in the
  Indian mid-cap universe, and it has no US analogue.
* **Related-party transactions** — the standard route by which cash leaves a
  listed entity for a promoter-owned unlisted one.
* **Contingent liabilities** — routinely larger than net worth in Indian
  infrastructure and capital-goods names, and disclosed only in the notes.
* **Auditor qualification or resignation** — in India, a mid-cycle auditor exit
  is very often the last public signal before a collapse.

Thresholds follow the bands in
``skills/institutional-equity-risk-strategist/references/benchmarks-and-formulas.md``.
"""

from __future__ import annotations

from typing import Optional

from .models import STATUTORY_TAX_RATE, Company
from .result import Check, Flag, ScoreResult


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


def india_red_flags(company: Company) -> ScoreResult:
    """Run the India-specific register. Returns checks plus a veto verdict."""
    res = ScoreResult(name="India red-flag register", unit="int")
    cur, prior = company.latest(), company.prior()

    # -- 1. Earnings quality: does profit become cash? ----------------------
    cfo_pat = _safe_div(cur.cfo, cur.pat)
    res.checks.append(Check(
        name="CFO / PAT",
        value=cfo_pat, unit="x", benchmark="> 0.8",
        flag=Flag.NA if cfo_pat is None else (
            Flag.GREEN if cfo_pat >= 0.8 else (Flag.AMBER if cfo_pat >= 0.5 else Flag.RED)
        ),
        read="profit stuck in receivables, inventory or fiction if persistently below 0.8",
    ))

    # -- 2. Promoter pledge ------------------------------------------------
    pledge = cur.promoter_pledge_pct
    pledge_flag = Flag.NA
    if pledge is not None:
        if pledge == 0:
            pledge_flag = Flag.GREEN
        elif pledge < 10:
            pledge_flag = Flag.AMBER
        else:
            pledge_flag = Flag.RED
    res.checks.append(Check(
        name="Promoter pledge",
        value=pledge, unit="pp",
        benchmark="0% clean · <10% watch · >10% severe",
        flag=pledge_flag,
        read="promoter borrowing against his own stock; forced selling on a drawdown",
    ))

    # Pledge trend matters more than level.
    if prior is not None and None not in (cur.promoter_pledge_pct, prior.promoter_pledge_pct):
        delta = cur.promoter_pledge_pct - prior.promoter_pledge_pct
        res.checks.append(Check(
            name="Pledge trend YoY", value=delta, unit="pp", benchmark="falling or flat",
            flag=Flag.RED if delta > 0 else Flag.GREEN,
            read="a rising pledge is a top-tier veto signal regardless of level",
        ))

    # -- 3. Promoter holding trend -----------------------------------------
    if prior is not None and None not in (cur.promoter_holding_pct, prior.promoter_holding_pct):
        delta = cur.promoter_holding_pct - prior.promoter_holding_pct
        res.checks.append(Check(
            name="Promoter holding trend YoY", value=delta, unit="pp", benchmark="stable or rising",
            flag=Flag.RED if delta < -2 else (Flag.AMBER if delta < 0 else Flag.GREEN),
            read="promoters selling into their own story",
        ))

    # -- 4. Related-party transactions -------------------------------------
    rpt = _safe_div(cur.related_party_txns, cur.revenue)
    res.checks.append(Check(
        name="Related-party txns / revenue", value=rpt, unit="%",
        benchmark="< 5%",
        flag=Flag.NA if rpt is None else (
            Flag.GREEN if rpt < 0.05 else (Flag.AMBER if rpt < 0.15 else Flag.RED)
        ),
        read="the standard route for cash to leave the listed entity",
    ))

    # -- 5. Contingent liabilities -----------------------------------------
    cl = _safe_div(cur.contingent_liabilities, cur.equity)
    res.checks.append(Check(
        name="Contingent liabilities / net worth", value=cl, unit="%",
        benchmark="< 25%",
        flag=Flag.NA if cl is None else (
            Flag.GREEN if cl < 0.25 else (Flag.AMBER if cl < 0.50 else Flag.RED)
        ),
        read="off-balance-sheet exposure disclosed only in the notes",
    ))

    # -- 6. Receivables growth vs revenue growth ---------------------------
    if prior is not None:
        rev_g = _safe_div(cur.revenue, prior.revenue)
        rec_g = _safe_div(cur.receivables, prior.receivables)
        if None not in (rev_g, rec_g):
            ratio = _safe_div(rec_g - 1, rev_g - 1) if rev_g != 1 else None
            res.checks.append(Check(
                name="Receivables growth / revenue growth", value=ratio, unit="x",
                benchmark="< 1.5x",
                flag=Flag.NA if ratio is None else (
                    Flag.GREEN if ratio < 1.5 else (Flag.AMBER if ratio < 2.0 else Flag.RED)
                ),
                read="channel stuffing, pulled-forward revenue, or collection failure",
            ))

    # -- 7. Other income masquerading as operating profit ------------------
    oi = _safe_div(cur.other_income, cur.pbt)
    res.checks.append(Check(
        name="Other income / PBT", value=oi, unit="%",
        benchmark="< 15%",
        flag=Flag.NA if oi is None else (
            Flag.GREEN if oi < 0.15 else (Flag.AMBER if oi < 0.30 else Flag.RED)
        ),
        read="operating earnings dressed up by treasury income or one-offs",
    ))

    # -- 8. Effective tax rate vs statutory --------------------------------
    etr = cur.effective_tax_rate()
    res.checks.append(Check(
        name="Effective tax rate", value=etr, unit="%",
        benchmark=f"near statutory {STATUTORY_TAX_RATE:.1%}",
        flag=Flag.NA if etr is None else (
            Flag.AMBER if etr < STATUTORY_TAX_RATE * 0.6 else Flag.GREEN
        ),
        read="a rate far below statutory implies low-quality or unsustainable earnings",
    ))

    # -- 9. Interest coverage ----------------------------------------------
    cov = _safe_div(cur.ebit, cur.interest)
    res.checks.append(Check(
        name="Interest coverage", value=cov, unit="x",
        benchmark="> 2.5x",
        flag=Flag.NA if cov is None else (
            Flag.GREEN if cov > 2.5 else (Flag.AMBER if cov > 1.5 else Flag.RED)
        ),
        read="a company can post rising EPS while marching toward insolvency",
    ))

    # -- 10. Capital-work-in-progress that never converts ------------------
    cwip = _safe_div(cur.cwip, cur.net_block)
    res.checks.append(Check(
        name="CWIP / net block", value=cwip, unit="%",
        benchmark="< 20%",
        flag=Flag.NA if cwip is None else (
            Flag.GREEN if cwip < 0.20 else (Flag.AMBER if cwip < 0.40 else Flag.RED)
        ),
        read="capex that never becomes revenue — capitalising what should be expensed",
    ))

    # -- 11. Auditor signals ------------------------------------------------
    if cur.auditor_qualified is not None:
        res.checks.append(Check(
            name="Auditor qualification", value=float(cur.auditor_qualified),
            benchmark="none", unit="int",
            flag=Flag.RED if cur.auditor_qualified else Flag.GREEN,
            read="a qualified opinion is the auditor declining to sign off cleanly",
        ))
    if cur.auditor_changed is not None:
        res.checks.append(Check(
            name="Auditor change / resignation", value=float(cur.auditor_changed),
            benchmark="none", unit="int",
            flag=Flag.RED if cur.auditor_changed else Flag.GREEN,
            read="a mid-cycle auditor exit is often the last public signal before a collapse",
        ))

    # -- Verdict ------------------------------------------------------------
    reds = [c for c in res.checks if c.flag is Flag.RED]
    ambers = [c for c in res.checks if c.flag is Flag.AMBER]
    res.missing_inputs = [c.name for c in res.checks if c.missing]

    # Vetoes: certain reds end the analysis on their own, per the desk rule that
    # a failure on earnings quality or pledge cannot be outweighed by anything.
    veto_names = {"CFO / PAT", "Promoter pledge", "Pledge trend YoY",
                  "Auditor qualification", "Auditor change / resignation"}
    vetoes = [c.name for c in reds if c.name in veto_names]

    res.score = float(len(reds))
    if vetoes:
        res.flag = Flag.RED
        res.band = f"IMPAIRED — veto on: {', '.join(vetoes)}"
    elif reds:
        res.flag = Flag.RED
        res.band = f"impaired — {len(reds)} red flag(s)"
    elif ambers:
        res.flag = Flag.AMBER
        res.band = f"watch — {len(ambers)} amber flag(s)"
    else:
        res.flag = Flag.GREEN
        res.band = "clean"
    return res
