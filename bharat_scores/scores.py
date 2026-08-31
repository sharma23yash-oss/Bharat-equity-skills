"""The four quantitative scores: Piotroski, Beneish, Altman (EM), DuPont.

Every function takes a :class:`~bharat_scores.models.Company` and returns a
:class:`~bharat_scores.result.ScoreResult`. Where an input is missing the check
is skipped and named in ``missing_inputs`` — the score is then reported out of
the number of checks that could actually be run, and never silently inflated.
"""

from __future__ import annotations

from typing import Optional

from .models import Company, FiscalYear
from .result import Check, Flag, ScoreResult


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


# ---------------------------------------------------------------------------
# Piotroski F-Score
# ---------------------------------------------------------------------------

def piotroski_f_score(company: Company) -> ScoreResult:
    """Piotroski (2000) F-Score, 9 binary signals across three dimensions.

    Bands: 8–9 strong, 5–7 middling, 0–4 weak.
    """
    res = ScoreResult(name="Piotroski F-Score", max_score=9)
    cur, prior = company.latest(), company.prior()

    if prior is None:
        res.missing_inputs.append("a prior fiscal year (F-Score needs two)")
        return res

    signals: list[tuple[str, Optional[bool], str]] = []

    roa_cur, roa_prior = cur.roa(), prior.roa()
    signals.append(("ROA positive", (roa_cur > 0) if roa_cur is not None else None,
                    "profitable on assets"))
    signals.append(("CFO positive", (cur.cfo > 0) if cur.cfo is not None else None,
                    "operations generate cash"))
    signals.append(("ROA improving",
                    (roa_cur > roa_prior) if None not in (roa_cur, roa_prior) else None,
                    "returns trending up"))

    # Accruals: CFO should exceed PAT. When it doesn't, profit is sitting in
    # working capital rather than the bank — the single most telling signal here.
    accrual_ok = None
    if None not in (cur.cfo, cur.pat):
        accrual_ok = cur.cfo > cur.pat
    signals.append(("CFO > PAT (accruals)", accrual_ok, "profit converts to cash"))

    # Leverage: long-term debt to assets should fall.
    ltd_cur = _safe_div(cur.long_term_debt, cur.total_assets)
    ltd_prior = _safe_div(prior.long_term_debt, prior.total_assets)
    signals.append(("Leverage falling",
                    (ltd_cur <= ltd_prior) if None not in (ltd_cur, ltd_prior) else None,
                    "not funding growth with debt"))

    cr_cur, cr_prior = cur.current_ratio(), prior.current_ratio()
    signals.append(("Current ratio improving",
                    (cr_cur > cr_prior) if None not in (cr_cur, cr_prior) else None,
                    "short-term liquidity better"))

    dilution = None
    if None not in (cur.shares_outstanding, prior.shares_outstanding):
        # A 0.5% tolerance absorbs ESOP noise without excusing a real raise.
        dilution = cur.shares_outstanding <= prior.shares_outstanding * 1.005
    signals.append(("No equity dilution", dilution, "growth self-funded"))

    gm_cur, gm_prior = cur.gross_margin(), prior.gross_margin()
    signals.append(("Gross margin improving",
                    (gm_cur > gm_prior) if None not in (gm_cur, gm_prior) else None,
                    "pricing power or mix improving"))

    at_cur, at_prior = cur.asset_turnover(), prior.asset_turnover()
    signals.append(("Asset turnover improving",
                    (at_cur > at_prior) if None not in (at_cur, at_prior) else None,
                    "sweating assets harder"))

    scored = 0
    testable = 0
    for label, passed, read in signals:
        if passed is None:
            res.checks.append(Check(name=label, flag=Flag.NA, read="input missing"))
            res.missing_inputs.append(label)
            continue
        testable += 1
        scored += int(passed)
        res.checks.append(Check(
            name=label,
            value=float(passed),
            flag=Flag.GREEN if passed else Flag.RED,
            benchmark="pass",
            read=read,
            unit="int",
        ))

    if testable == 0:
        return res

    res.score = scored
    res.max_score = testable
    pct = scored / testable
    if pct >= 8 / 9:
        res.band, res.flag = "strong", Flag.GREEN
    elif pct >= 5 / 9:
        res.band, res.flag = "middling", Flag.AMBER
    else:
        res.band, res.flag = "weak", Flag.RED
    if testable < 9:
        res.band += f" (scored on {testable} of 9 signals)"
    return res


# ---------------------------------------------------------------------------
# Beneish M-Score
# ---------------------------------------------------------------------------

BENEISH_COEFFS = {
    "intercept": -4.84,
    "DSRI": 0.920,
    "GMI": 0.528,
    "AQI": 0.404,
    "SGI": 0.892,
    "DEPI": 0.115,
    "SGAI": -0.172,
    "TATA": 4.679,
    "LVGI": -0.327,
}

BENEISH_THRESHOLD = -1.78  # above this, manipulation is statistically likely


def beneish_m_score(company: Company) -> ScoreResult:
    """Beneish (1999) 8-variable earnings-manipulation model.

    M > -1.78 flags a company as a likely manipulator. The model was fitted on
    US non-financials; treat the output for an Indian financial as indicative
    only, which is why banks and NBFCs are refused outright below.
    """
    res = ScoreResult(name="Beneish M-Score")
    cur, prior = company.latest(), company.prior()

    if company.is_financial:
        res.missing_inputs.append(
            "Beneish is not defined for banks/NBFCs — use the BFSI asset-quality set instead"
        )
        return res
    if prior is None:
        res.missing_inputs.append("a prior fiscal year (M-Score needs two)")
        return res

    idx: dict[str, Optional[float]] = {}

    # DSRI — receivables growing faster than sales is the channel-stuffing tell.
    idx["DSRI"] = _safe_div(
        _safe_div(cur.receivables, cur.revenue),
        _safe_div(prior.receivables, prior.revenue),
    )
    # GMI — deteriorating gross margin raises the incentive to manipulate.
    idx["GMI"] = _safe_div(prior.gross_margin(), cur.gross_margin())
    # AQI — a rising share of soft assets suggests capitalised costs.
    aqi_cur = _safe_div(
        (cur.total_assets - (cur.current_assets or 0) - (cur.net_block or 0))
        if cur.total_assets is not None else None,
        cur.total_assets,
    )
    aqi_prior = _safe_div(
        (prior.total_assets - (prior.current_assets or 0) - (prior.net_block or 0))
        if prior.total_assets is not None else None,
        prior.total_assets,
    )
    idx["AQI"] = _safe_div(aqi_cur, aqi_prior)
    # SGI — high growth is itself a manipulation risk factor.
    idx["SGI"] = _safe_div(cur.revenue, prior.revenue)
    # DEPI — a slowing depreciation rate inflates reported profit.
    dep_rate_cur = _safe_div(cur.depreciation,
                             (cur.depreciation + cur.net_block)
                             if None not in (cur.depreciation, cur.net_block) else None)
    dep_rate_prior = _safe_div(prior.depreciation,
                               (prior.depreciation + prior.net_block)
                               if None not in (prior.depreciation, prior.net_block) else None)
    idx["DEPI"] = _safe_div(dep_rate_prior, dep_rate_cur)
    # SGAI — SG&A rising faster than sales signals loss of operating control.
    idx["SGAI"] = _safe_div(
        _safe_div(cur.sga, cur.revenue),
        _safe_div(prior.sga, prior.revenue),
    )
    # TATA — total accruals to total assets. The heaviest-weighted term.
    idx["TATA"] = _safe_div(
        (cur.pat - cur.cfo) if None not in (cur.pat, cur.cfo) else None,
        cur.total_assets,
    )
    # LVGI — rising leverage increases covenant pressure.
    lev_cur = _safe_div(
        ((cur.current_liabilities or 0) + (cur.long_term_debt or 0))
        if cur.total_assets is not None else None,
        cur.total_assets,
    )
    lev_prior = _safe_div(
        ((prior.current_liabilities or 0) + (prior.long_term_debt or 0))
        if prior.total_assets is not None else None,
        prior.total_assets,
    )
    idx["LVGI"] = _safe_div(lev_cur, lev_prior)

    reads = {
        "DSRI": "receivables vs sales — channel stuffing / revenue pulled forward",
        "GMI": "margin deterioration — motive to manipulate",
        "AQI": "soft assets rising — costs being capitalised",
        "SGI": "growth pressure — high growth raises manipulation odds",
        "DEPI": "depreciation slowing — profit flattered",
        "SGAI": "overheads outrunning sales",
        "TATA": "accruals vs assets — profit not backed by cash",
        "LVGI": "leverage rising — covenant pressure",
    }

    missing = [k for k, v in idx.items() if v is None]
    for key, val in idx.items():
        if val is None:
            res.checks.append(Check(name=key, flag=Flag.NA, read="input missing"))
        else:
            # Each index is neutral at 1.0 (TATA at 0). Flag the direction that
            # increases M.
            neutral = 0.0 if key == "TATA" else 1.0
            worse = val > neutral if BENEISH_COEFFS[key] > 0 else val < neutral
            res.checks.append(Check(
                name=key, value=val, unit="x" if key != "TATA" else "",
                flag=Flag.AMBER if worse else Flag.GREEN,
                benchmark=f"neutral {neutral:g}", read=reads[key],
            ))

    if missing:
        res.missing_inputs = [f"Beneish {m}" for m in missing]
        return res

    m = BENEISH_COEFFS["intercept"] + sum(
        BENEISH_COEFFS[k] * idx[k] for k in idx  # type: ignore[operator]
    )
    res.score = m
    if m > BENEISH_THRESHOLD:
        res.band, res.flag = "likely manipulator", Flag.RED
    elif m > -2.22:
        res.band, res.flag = "grey zone", Flag.AMBER
    else:
        res.band, res.flag = "unlikely manipulator", Flag.GREEN
    return res


# ---------------------------------------------------------------------------
# Altman Z-Score — emerging-markets variant
# ---------------------------------------------------------------------------

def altman_z_em(company: Company) -> ScoreResult:
    """Altman Z''-Score, emerging-market variant.

    Z'' = 3.25 + 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4

    The EM variant is the right one for Indian listings: it drops the
    sales/assets term (which distorts across the asset-intensity range of an
    Indian industrial universe) and uses book equity over total liabilities
    rather than market cap, so it works for thinly-traded small caps too.

    Bands: > 5.85 safe · 4.15–5.85 grey · < 4.15 distress.
    """
    res = ScoreResult(name="Altman Z''-Score (EM)")
    cur = company.latest()

    if company.is_financial:
        res.missing_inputs.append(
            "Altman is not meaningful for banks/NBFCs — use CAR, GNPA and PCR instead"
        )
        return res

    x1 = _safe_div(cur.working_capital(), cur.total_assets)
    x2 = _safe_div(cur.reserves, cur.total_assets)
    x3 = _safe_div(cur.ebit, cur.total_assets)
    x4 = _safe_div(cur.equity, cur.total_liabilities)

    parts = {
        "X1 working capital / assets": (x1, 6.56, "short-term liquidity buffer"),
        "X2 reserves / assets": (x2, 3.26, "cumulative retained profitability"),
        "X3 EBIT / assets": (x3, 6.72, "core operating earning power"),
        "X4 equity / total liabilities": (x4, 1.05, "solvency cushion"),
    }
    for label, (val, _w, read) in parts.items():
        res.checks.append(Check(
            name=label, value=val, unit="x",
            flag=Flag.NA if val is None else (Flag.GREEN if val > 0 else Flag.RED),
            read=read,
        ))

    missing = [k for k, (v, _, _) in parts.items() if v is None]
    if missing:
        res.missing_inputs = missing
        return res

    z = 3.25 + 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4  # type: ignore[operator]
    res.score = z
    if z > 5.85:
        res.band, res.flag = "safe zone", Flag.GREEN
    elif z >= 4.15:
        res.band, res.flag = "grey zone", Flag.AMBER
    else:
        res.band, res.flag = "distress zone", Flag.RED
    return res


# ---------------------------------------------------------------------------
# Extended (5-step) DuPont
# ---------------------------------------------------------------------------

def dupont_5step(company: Company) -> ScoreResult:
    """Five-step DuPont decomposition.

    ROE = Tax Burden × Interest Burden × Operating Margin × Asset Turnover × Leverage

    The point is attribution, not the ROE itself: a return manufactured by
    leverage and one earned by margin have opposite risk profiles, and the
    headline number cannot tell them apart.
    """
    res = ScoreResult(name="DuPont (5-step)", unit="%")
    cur = company.latest()

    tax_burden = _safe_div(cur.pat, cur.pbt)
    interest_burden = _safe_div(cur.pbt, cur.ebit)
    op_margin = _safe_div(cur.ebit, cur.revenue)
    asset_turn = _safe_div(cur.revenue, cur.total_assets)
    leverage = _safe_div(cur.total_assets, cur.equity)

    components = {
        "Tax burden (PAT/PBT)": (tax_burden, "higher is better; very high implies tax breaks that may lapse"),
        "Interest burden (PBT/EBIT)": (interest_burden, "below ~0.7 means debt is eating operating profit"),
        "Operating margin (EBIT/Sales)": (op_margin, "the operational half of the return"),
        "Asset turnover (Sales/Assets)": (asset_turn, "how hard the balance sheet works"),
        "Financial leverage (Assets/Equity)": (leverage, "above ~3x, ROE is substantially borrowed"),
    }
    for label, (val, read) in components.items():
        res.checks.append(Check(
            name=label, value=val, unit="x",
            flag=Flag.NA if val is None else Flag.GREEN, read=read,
        ))

    missing = [k for k, (v, _) in components.items() if v is None]
    if missing:
        res.missing_inputs = missing
        return res

    roe = tax_burden * interest_burden * op_margin * asset_turn * leverage  # type: ignore[operator]
    res.score = roe

    # Attribution: is the return operational or borrowed?
    roce = _safe_div(cur.ebit, cur.capital_employed())
    if roce is not None:
        res.checks.append(Check(
            name="ROCE (EBIT/Capital employed)", value=roce, unit="%",
            flag=Flag.GREEN if roce > 0.15 else (Flag.AMBER if roce > 0.10 else Flag.RED),
            benchmark="> 15% good, < 10% weak",
            read="the return before financing effects — the honest one",
        ))

    if leverage > 3.0:
        res.band, res.flag = "leverage-driven — fragile", Flag.RED
    elif leverage > 2.0:
        res.band, res.flag = "partly leverage-driven", Flag.AMBER
    else:
        res.band, res.flag = "operationally driven", Flag.GREEN

    if roce is not None and roe > roce * 1.5:
        res.band += f"; ROE ({roe:.1%}) far above ROCE ({roce:.1%}) — the gap is borrowed"
    return res
