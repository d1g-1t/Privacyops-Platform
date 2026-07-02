from __future__ import annotations

from typing import Any

from src.infrastructure.rules import RuleFinding, RuleSet, RuleSeverity


class ConsentRuleSet(RuleSet):
    def evaluate(self, context: dict[str, Any]) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        consents = context.get("consents", [])

        for consent in consents:
            if consent.get("status") == "withdrawn" and consent.get("activity_id"):
                findings.append(
                    RuleFinding(
                        rule_id="R-CON-001",
                        severity=RuleSeverity.WARNING,
                        message="Consent withdrawn — dependent activity may lose legal basis",
                        details={
                            "capture_id": consent.get("id"),
                            "activity_id": consent.get("activity_id"),
                        },
                    )
                )

        expiring = context.get("expiring_consents", [])
        for consent in expiring:
            findings.append(
                RuleFinding(
                    rule_id="R-CON-002",
                    severity=RuleSeverity.INFO,
                    message="Consent is approaching expiry",
                    details={"capture_id": consent.get("id")},
                )
            )

        return findings
