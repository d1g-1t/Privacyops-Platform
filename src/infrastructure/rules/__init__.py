"""Rule engine — deterministic compliance checks. LLM is NEVER the source of truth."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any


class RuleSeverity(StrEnum):
    INFO = auto()
    WARNING = auto()
    VIOLATION = auto()
    CRITICAL = auto()


@dataclass(frozen=True)
class RuleFinding:
    rule_id: str
    severity: RuleSeverity
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class RuleEngine:
    """Composes multiple rule sets and runs them against a context dict."""

    def __init__(self) -> None:
        self._rule_sets: list[RuleSet] = []

    def register(self, rule_set: "RuleSet") -> None:
        self._rule_sets.append(rule_set)

    def evaluate(self, context: dict[str, Any]) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for rs in self._rule_sets:
            findings.extend(rs.evaluate(context))
        return findings

    @property
    def has_violations(self) -> bool:
        return False  # Stateless — call evaluate and check findings


class RuleSet:
    """Base class for a group of related rules."""

    def evaluate(self, context: dict[str, Any]) -> list[RuleFinding]:
        raise NotImplementedError
