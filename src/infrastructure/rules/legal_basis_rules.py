"""Legal basis compliance rules under 152-FZ."""

from __future__ import annotations

from typing import Any

from src.infrastructure.rules import RuleFinding, RuleSet, RuleSeverity


class LegalBasisRuleSet(RuleSet):
    def evaluate(self, context: dict[str, Any]) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        activity = context.get("activity")
        legal_bases = context.get("legal_bases", [])

        if not activity:
            return findings

        # R-LB-001: Active activity must have at least one legal basis
        if activity.get("status") == "active" and not legal_bases:
            findings.append(
                RuleFinding(
                    rule_id="R-LB-001",
                    severity=RuleSeverity.VIOLATION,
                    message="Active processing activity has no legal basis",
                    details={"activity_id": activity.get("id")},
                )
            )

        # R-LB-002: Consent-based processing must have active consent
        for basis in legal_bases:
            if basis.get("basis_type") == "consent" and basis.get("active"):
                has_consent = context.get("has_active_consent", False)
                if not has_consent:
                    findings.append(
                        RuleFinding(
                            rule_id="R-LB-002",
                            severity=RuleSeverity.CRITICAL,
                            message="Consent-based activity has no active consent captures",
                            details={
                                "activity_id": activity.get("id"),
                                "basis_id": basis.get("id"),
                            },
                        )
                    )

        # R-LB-003: Every legal basis must have a reference
        for basis in legal_bases:
            if not basis.get("basis_reference"):
                findings.append(
                    RuleFinding(
                        rule_id="R-LB-003",
                        severity=RuleSeverity.WARNING,
                        message="Legal basis has no reference (article/clause)",
                        details={"basis_id": basis.get("id")},
                    )
                )

        return findings
