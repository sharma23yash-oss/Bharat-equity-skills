"""Input model for a single fiscal year of Indian-listing financials.

All monetary figures are in the same unit (₹ crore by convention). Ratios and
percentages are expressed as decimals unless the field name says otherwise.

Field names follow the vocabulary of an Indian annual report / Screener.in
export rather than US-GAAP shorthand, so numbers can be typed straight off a
statement without translation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Statutory corporate tax rate used as the reference for the effective-tax-rate
# check. India's headline domestic rate under s.115BAA is 22% plus surcharge and
# cess, giving an effective ~25.17%.
STATUTORY_TAX_RATE = 0.2517


@dataclass
class FiscalYear:
    """One year of figures. Only what a check actually needs must be filled in.

    Anything left as ``None`` causes the dependent check to report
    ``data not provided`` rather than silently assuming a value — a fabricated
    ratio is worse than a missing one.
    """

    label: str  # e.g. "FY25"

    # --- Profit & loss -----------------------------------------------------
    revenue: Optional[float] = None
    cogs: Optional[float] = None
    gross_profit: Optional[float] = None
    sga: Optional[float] = None
    ebitda: Optional[float] = None
    depreciation: Optional[float] = None
    ebit: Optional[float] = None
    interest: Optional[float] = None
    other_income: Optional[float] = None
    pbt: Optional[float] = None
    tax: Optional[float] = None
    pat: Optional[float] = None

    # --- Balance sheet -----------------------------------------------------
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    inventory: Optional[float] = None
    receivables: Optional[float] = None
    payables: Optional[float] = None
    net_block: Optional[float] = None  # PPE, net of depreciation
    cwip: Optional[float] = None
    intangibles: Optional[float] = None
    total_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None
    short_term_debt: Optional[float] = None
    equity: Optional[float] = None  # shareholders' funds / net worth
    reserves: Optional[float] = None  # proxy for retained earnings
    shares_outstanding: Optional[float] = None

    # --- Cash flow ---------------------------------------------------------
    cfo: Optional[float] = None

    # --- India-specific governance inputs ----------------------------------
    promoter_holding_pct: Optional[float] = None
    promoter_pledge_pct: Optional[float] = None
    related_party_txns: Optional[float] = None
    contingent_liabilities: Optional[float] = None
    auditor_qualified: Optional[bool] = None
    auditor_changed: Optional[bool] = None

    # --- Market data (optional, for valuation and momentum) ----------------
    price: Optional[float] = None
    market_cap: Optional[float] = None

    # --- Derived -----------------------------------------------------------
    def gross_margin(self) -> Optional[float]:
        gp = self.gross_profit
        if gp is None and None not in (self.revenue, self.cogs):
            gp = self.revenue - self.cogs
        if gp is None or not self.revenue:
            return None
        return gp / self.revenue

    def working_capital(self) -> Optional[float]:
        if None in (self.current_assets, self.current_liabilities):
            return None
        return self.current_assets - self.current_liabilities

    def total_debt(self) -> Optional[float]:
        parts = [d for d in (self.long_term_debt, self.short_term_debt) if d is not None]
        return sum(parts) if parts else None

    def roa(self) -> Optional[float]:
        if None in (self.pat, self.total_assets) or not self.total_assets:
            return None
        return self.pat / self.total_assets

    def asset_turnover(self) -> Optional[float]:
        if None in (self.revenue, self.total_assets) or not self.total_assets:
            return None
        return self.revenue / self.total_assets

    def current_ratio(self) -> Optional[float]:
        if None in (self.current_assets, self.current_liabilities):
            return None
        if not self.current_liabilities:
            return None
        return self.current_assets / self.current_liabilities

    def capital_employed(self) -> Optional[float]:
        if None in (self.total_assets, self.current_liabilities):
            return None
        return self.total_assets - self.current_liabilities

    def effective_tax_rate(self) -> Optional[float]:
        if None in (self.tax, self.pbt) or not self.pbt:
            return None
        return self.tax / self.pbt


@dataclass
class Company:
    """A company and its ordered history, oldest first."""

    name: str
    ticker: str = ""
    sector: str = ""
    is_financial: bool = False  # banks / NBFCs take a different benchmark set
    years: list[FiscalYear] = field(default_factory=list)

    def latest(self) -> FiscalYear:
        if not self.years:
            raise ValueError(f"{self.name}: no fiscal years supplied")
        return self.years[-1]

    def prior(self) -> Optional[FiscalYear]:
        return self.years[-2] if len(self.years) >= 2 else None
