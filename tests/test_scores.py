"""Tests for the scoring engine.

Two things are being protected here:

1. **Arithmetic.** The DuPont identity must close exactly, and Beneish must
   reproduce a hand-worked value. These are the tests that catch a transcription
   error in a coefficient.
2. **The refusal to guess.** A missing input must produce ``None`` and a named
   gap, never a zero that silently becomes a score. Most of the value of a
   forensic tool is that it declines to invent a number.
"""

from __future__ import annotations

import math

import pytest

from bharat_scores import (
    Company,
    FiscalYear,
    Flag,
    altman_z_em,
    beneish_m_score,
    dupont_5step,
    india_red_flags,
    piotroski_f_score,
    to_markdown,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _clean_year(label: str, scale: float = 1.0, **overrides) -> FiscalYear:
    """A healthy, unlevered manufacturer. Scale shifts the whole year."""
    base = dict(
        revenue=10000 * scale,
        cogs=6000 * scale,
        sga=1200 * scale,
        depreciation=400 * scale,
        ebit=2400 * scale,
        interest=100 * scale,
        other_income=150 * scale,
        pbt=2300 * scale,
        tax=580 * scale,
        pat=1720 * scale,
        total_assets=12000 * scale,
        current_assets=5000 * scale,
        current_liabilities=2500 * scale,
        inventory=1200 * scale,
        receivables=1500 * scale,
        net_block=4500 * scale,
        cwip=300 * scale,
        total_liabilities=4000 * scale,
        long_term_debt=1000 * scale,
        short_term_debt=500 * scale,
        equity=8000 * scale,
        reserves=6500 * scale,
        shares_outstanding=2730,
        cfo=1900 * scale,
        promoter_holding_pct=49.0,
        promoter_pledge_pct=0.0,
        related_party_txns=200 * scale,
        contingent_liabilities=800 * scale,
        auditor_qualified=False,
        auditor_changed=False,
    )
    base.update(overrides)
    return FiscalYear(label=label, **base)


@pytest.fixture
def clean_company() -> Company:
    """A genuine compounder: FY25 is operationally better than FY24 on every axis.

    Uniformly scaling a year would leave every margin and ratio unchanged, so
    the four "improving" signals would correctly score zero. A real improving
    business has to be built deliberately.
    """
    prior = _clean_year(
        "FY24",
        revenue=8800, cogs=5500,          # gross margin 37.5% (vs 40.0%)
        ebit=1900, pbt=1800, tax=460, pat=1300,
        total_assets=11500,               # asset turnover 0.765x (vs 0.833x)
        current_assets=4200, current_liabilities=2400,  # current ratio 1.75x (vs 2.0x)
        long_term_debt=1400,              # LTD/assets 12.2% (vs 8.3%)
        cfo=1500,
    )
    return Company(
        name="Clean Compounder Ltd", ticker="CLEAN", sector="Auto",
        years=[prior, _clean_year("FY25")],
    )


@pytest.fixture
def trap_company() -> Company:
    """A value trap: healthy reported profit that never turns into cash.

    The shape that matters is high PAT with collapsed CFO — not low PAT. A
    company with poor profits is merely bad; one reporting good profits it
    cannot collect is the thing that destroys capital.
    """
    prior = _clean_year(
        "FY24",
        ebit=1700, interest=700, other_income=200, pbt=1000, tax=300, pat=700,
        cfo=600,                          # CFO/PAT 0.86 — still fine here
        receivables=1400,
        promoter_pledge_pct=12.0,
        contingent_liabilities=3000,
    )
    cur = _clean_year(
        "FY25",
        ebit=1800, interest=800, other_income=300, pbt=1000, tax=250, pat=750,
        cfo=150,                          # CFO/PAT 0.20 — profit is not cash
        receivables=2600,                 # receivables far outrunning revenue
        promoter_pledge_pct=38.0,         # pledge high AND rising
        promoter_holding_pct=44.0,        # promoters selling down
        contingent_liabilities=6000,      # 75% of net worth
        auditor_qualified=True,
    )
    return Company(name="Trap Industries Ltd", ticker="TRAP",
                   sector="Infrastructure", years=[prior, cur])


# ---------------------------------------------------------------------------
# DuPont — the identity must close
# ---------------------------------------------------------------------------

def test_dupont_identity_closes(clean_company):
    """The five components must multiply back to PAT/Equity exactly."""
    res = dupont_5step(clean_company)
    assert res.computed

    cur = clean_company.latest()
    expected_roe = cur.pat / cur.equity
    assert math.isclose(res.score, expected_roe, rel_tol=1e-9), (
        f"DuPont product {res.score} != ROE {expected_roe}"
    )


def test_dupont_flags_leverage(clean_company):
    res = dupont_5step(clean_company)
    # assets 12000 / equity 8000 = 1.5x — operationally driven
    assert res.flag is Flag.GREEN
    assert "operationally driven" in res.band


def test_dupont_detects_borrowed_roe():
    """High leverage must be called out, not rewarded."""
    y = _clean_year("FY25", equity=1000, total_assets=12000, total_liabilities=11000)
    res = dupont_5step(Company(name="Levered", years=[y]))
    assert res.flag is Flag.RED
    assert "leverage-driven" in res.band


# ---------------------------------------------------------------------------
# Piotroski
# ---------------------------------------------------------------------------

def test_piotroski_healthy_company_scores_well(clean_company):
    res = piotroski_f_score(clean_company)
    assert res.computed
    assert res.score >= 7, f"expected a strong score, got {res.score}: {res.band}"


def test_piotroski_needs_two_years():
    res = piotroski_f_score(Company(name="One Year", years=[_clean_year("FY25")]))
    assert not res.computed
    assert any("prior fiscal year" in m for m in res.missing_inputs)


def test_piotroski_scores_out_of_testable_signals_only():
    """Missing inputs must shrink the denominator, not count as failures."""
    prior = FiscalYear(label="FY24", pat=100, total_assets=1000, cfo=120)
    cur = FiscalYear(label="FY25", pat=150, total_assets=1000, cfo=200)
    res = piotroski_f_score(Company(name="Sparse", years=[prior, cur]))
    assert res.computed
    assert res.max_score is not None and res.max_score < 9
    assert "scored on" in res.band
    assert res.missing_inputs


# ---------------------------------------------------------------------------
# Beneish
# ---------------------------------------------------------------------------

def test_beneish_reproduces_hand_worked_value():
    """All eight indices neutral => M must equal the intercept plus known terms.

    With every ratio identical year on year, DSRI=GMI=AQI=SGI=DEPI=SGAI=LVGI=1
    and TATA=(PAT-CFO)/TA. Constructing PAT==CFO makes TATA=0, so:
        M = -4.84 + 0.92 + 0.528 + 0.404 + 0.892 + 0.115 - 0.172 - 0.327
          = -2.48
    """
    kw = dict(
        revenue=1000, cogs=600, sga=100, depreciation=50, net_block=450,
        receivables=150, total_assets=2000, current_assets=800,
        current_liabilities=400, long_term_debt=300, pat=120, cfo=120,
    )
    prior = FiscalYear(label="FY24", **kw)
    cur = FiscalYear(label="FY25", **kw)
    res = beneish_m_score(Company(name="Flat", years=[prior, cur]))

    assert res.computed
    assert math.isclose(res.score, -2.48, abs_tol=1e-9), res.score
    assert res.flag is Flag.GREEN


def test_beneish_refused_for_banks():
    c = Company(name="A Bank", is_financial=True,
                years=[_clean_year("FY24"), _clean_year("FY25")])
    res = beneish_m_score(c)
    assert not res.computed
    assert any("banks/NBFC" in m for m in res.missing_inputs)


def test_beneish_flags_receivables_blowout(trap_company):
    """Receivables far outrunning sales should push M toward the threshold."""
    res = beneish_m_score(trap_company)
    assert res.computed
    dsri = next(c for c in res.checks if c.name == "DSRI")
    assert dsri.value > 1.4, "receivables/sales should have deteriorated sharply"


# ---------------------------------------------------------------------------
# Altman
# ---------------------------------------------------------------------------

def test_altman_safe_zone(clean_company):
    res = altman_z_em(clean_company)
    assert res.computed
    assert res.score > 5.85
    assert res.flag is Flag.GREEN


def test_altman_distress_zone():
    y = FiscalYear(
        label="FY25", current_assets=500, current_liabilities=2000,
        reserves=-800, ebit=-200, total_assets=5000, equity=200,
        total_liabilities=4800,
    )
    res = altman_z_em(Company(name="Distressed", years=[y]))
    assert res.computed
    assert res.score < 4.15
    assert res.flag is Flag.RED


def test_altman_refused_for_banks():
    c = Company(name="A Bank", is_financial=True, years=[_clean_year("FY25")])
    assert not altman_z_em(c).computed


# ---------------------------------------------------------------------------
# India red-flag register — the differentiating checks
# ---------------------------------------------------------------------------

def test_clean_company_has_no_reds(clean_company):
    res = india_red_flags(clean_company)
    reds = [c for c in res.checks if c.flag is Flag.RED]
    assert not reds, f"unexpected reds: {[c.name for c in reds]}"
    assert res.flag is Flag.GREEN


def test_pledge_triggers_veto(trap_company):
    res = india_red_flags(trap_company)
    assert res.flag is Flag.RED
    assert res.band.startswith("IMPAIRED")
    assert "Promoter pledge" in res.band


def test_rising_pledge_is_a_veto_even_when_low():
    """Trend matters more than level — 2% rising must still veto."""
    prior = _clean_year("FY24", promoter_pledge_pct=0.0)
    cur = _clean_year("FY25", promoter_pledge_pct=2.0)
    res = india_red_flags(Company(name="Creeping", years=[prior, cur]))
    assert "Pledge trend YoY" in res.band


def test_cfo_pat_veto(trap_company):
    res = india_red_flags(trap_company)
    cfo = next(c for c in res.checks if c.name == "CFO / PAT")
    assert cfo.flag is Flag.RED
    assert cfo.value < 0.5


def test_missing_inputs_are_named_not_zeroed():
    """The core honesty guarantee: absent data must never become a number."""
    y = FiscalYear(label="FY25", revenue=1000, pat=100)
    res = india_red_flags(Company(name="Sparse", years=[y]))
    pledge = next(c for c in res.checks if c.name == "Promoter pledge")
    assert pledge.value is None
    assert pledge.flag is Flag.NA
    assert pledge.format_value() == "data not provided"
    assert "Promoter pledge" in res.missing_inputs


def test_contingent_liabilities_above_net_worth_flags_red():
    y = _clean_year("FY25", contingent_liabilities=9000, equity=8000)
    res = india_red_flags(Company(name="Exposed", years=[y]))
    cl = next(c for c in res.checks if c.name == "Contingent liabilities / net worth")
    assert cl.flag is Flag.RED


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def test_markdown_renders_and_discloses_gaps(trap_company):
    md = to_markdown(trap_company)
    assert "Trap Industries Ltd" in md
    assert "TRAP" in md
    assert "Piotroski F-Score" in md
    assert "India red-flag register" in md
    assert "Not investment advice" in md


def test_markdown_states_full_coverage_when_complete(clean_company):
    md = to_markdown(clean_company)
    assert "No values were estimated" in md


def test_bfsi_report_suppresses_inapplicable_scores():
    c = Company(name="Some Bank Ltd", ticker="BANK", is_financial=True,
                years=[_clean_year("FY24"), _clean_year("FY25")])
    md = to_markdown(c)
    assert "BFSI" in md
    assert "not computed" in md
