"""bharat-scores — forensic accounting scores for Indian listed companies.

Piotroski, Beneish, Altman (emerging-market variant), five-step DuPont, and an
India-specific red-flag register covering promoter pledge, related-party
transactions, contingent liabilities and auditor signals.

Designed to be paired with the Claude Skills in ``skills/``: this package
computes what is arithmetic, the skills reason about what is not.

    >>> from bharat_scores import Company, FiscalYear, to_markdown
    >>> print(to_markdown(company))
"""

from .india_flags import india_red_flags
from .models import STATUTORY_TAX_RATE, Company, FiscalYear
from .report import run_all, to_markdown, verdict_flag
from .result import Check, Flag, ScoreResult
from .scores import altman_z_em, beneish_m_score, dupont_5step, piotroski_f_score

__version__ = "0.1.0"

__all__ = [
    "Company",
    "FiscalYear",
    "STATUTORY_TAX_RATE",
    "Check",
    "Flag",
    "ScoreResult",
    "piotroski_f_score",
    "beneish_m_score",
    "altman_z_em",
    "dupont_5step",
    "india_red_flags",
    "run_all",
    "to_markdown",
    "verdict_flag",
]
