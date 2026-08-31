"""Shared result types.

Every check returns a ``Check`` rather than a bare number, because on a real
desk the number without its band and its mechanism is not actionable — and a
check whose inputs are missing must say so out loud instead of defaulting to
zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Flag(str, Enum):
    """Triage severity. Mirrors the 🟢/🟡/🔴 register in the skill notes."""

    GREEN = "green"
    AMBER = "amber"
    RED = "red"
    NA = "n/a"

    @property
    def symbol(self) -> str:
        return {"green": "🟢", "amber": "🟡", "red": "🔴", "n/a": "⚪"}[self.value]


@dataclass
class Check:
    """One forensic or factor check."""

    name: str
    value: Optional[float] = None
    flag: Flag = Flag.NA
    benchmark: str = ""
    read: str = ""  # the mechanism — what management would be doing for this to look like this
    unit: str = ""

    @property
    def missing(self) -> bool:
        return self.value is None

    def format_value(self) -> str:
        if self.value is None:
            return "data not provided"
        if self.unit == "%":
            return f"{self.value * 100:.1f}%"
        if self.unit == "pp":
            return f"{self.value:+.1f} pp" if self.value else "0.0 pp"
        if self.unit == "x":
            return f"{self.value:.2f}x"
        if self.unit == "days":
            return f"{self.value:.0f} days"
        if self.unit == "int":
            return f"{self.value:.0f}"
        return f"{self.value:.2f}"


@dataclass
class ScoreResult:
    """A composite score plus the checks that produced it."""

    name: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    band: str = ""
    flag: Flag = Flag.NA
    unit: str = ""
    checks: list[Check] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)

    @property
    def computed(self) -> bool:
        return self.score is not None

    def format_score(self) -> str:
        if self.score is None:
            return "not computed"
        if self.max_score:
            return f"{self.score:.0f} / {self.max_score:.0f}"
        if self.unit == "%":
            return f"{self.score * 100:.1f}%"
        if self.unit == "int":
            return f"{self.score:.0f}"
        return f"{self.score:.2f}"
