from __future__ import annotations

from typing import Any

from src.infrastructure.rules import RuleFinding, RuleSet, RuleSeverity


class ProcessorRuleSet(RuleSet):
    def evaluate(self, context: dict[str, Any]) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        vendor = context.get("vendor")
        reviews = context.get("reviews", [])

        if not vendor:
            return findings

        if vendor.get("hosts_personal_data"):
            has_dpa = any(r.get("dpa_present") for r in reviews)
            if not has_dpa:
                findings.append(
                    RuleFinding(
                        rule_id="R-PROC-001",
                        severity=RuleSeverity.VIOLATION,
                        message="Processor hosts PD but has no DPA on file",
                        details={"vendor_id": vendor.get("id")},
                    )
                )

        for review in reviews:
            score = review.get("risk_score", 0)
            if score >= 80:
                findings.append(
                    RuleFinding(
                        rule_id="R-PROC-002",
                        severity=RuleSeverity.CRITICAL,
                        message=f"Processor risk score {score} exceeds rejection threshold",
                        details={"review_id": review.get("id"), "score": score},
                    )
                )
            elif score >= 50:
                findings.append(
                    RuleFinding(
                        rule_id="R-PROC-002",
                        severity=RuleSeverity.WARNING,
                        message=f"Processor risk score {score} is elevated",
                        details={"review_id": review.get("id"), "score": score},
                    )
                )

        if vendor.get("subprocessors_used"):
            findings.append(
                RuleFinding(
                    rule_id="R-PROC-003",
                    severity=RuleSeverity.INFO,
                    message="Vendor uses subprocessors — verify chain compliance",
                    details={"vendor_id": vendor.get("id")},
                )
            )

        return findings
