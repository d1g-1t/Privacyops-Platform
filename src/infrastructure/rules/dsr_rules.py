from __future__ import annotations

from typing import Any

from src.infrastructure.rules import RuleFinding, RuleSet, RuleSeverity


class DSRRuleSet(RuleSet):
    def evaluate(self, context: dict[str, Any]) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        dsr = context.get("dsr")

        if not dsr:
            return findings

        days_remaining = dsr.get("days_remaining", 999)
        status = dsr.get("status", "")

        if status not in ("completed", "rejected") and days_remaining <= 0:
            findings.append(
                RuleFinding(
                    rule_id="R-DSR-001",
                    severity=RuleSeverity.CRITICAL,
                    message="Data subject request is OVERDUE",
                    details={"dsr_id": dsr.get("id"), "days_remaining": days_remaining},
                )
            )

        elif status not in ("completed", "rejected") and days_remaining <= 3:
            findings.append(
                RuleFinding(
                    rule_id="R-DSR-002",
                    severity=RuleSeverity.WARNING,
                    message=f"DSR due in {days_remaining} day(s)",
                    details={"dsr_id": dsr.get("id"), "days_remaining": days_remaining},
                )
            )

        if status == "open" and not dsr.get("assigned_user_id"):
            findings.append(
                RuleFinding(
                    rule_id="R-DSR-003",
                    severity=RuleSeverity.WARNING,
                    message="DSR is open but not assigned to anyone",
                    details={"dsr_id": dsr.get("id")},
                )
            )

        return findings
