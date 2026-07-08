"""Unit tests for the deterministic rules engine.

RuleEngine.evaluate() returns list[RuleFinding] dataclass objects.
Use attribute access: finding.rule_id (not dict subscript).
"""

from __future__ import annotations

import pytest

from src.infrastructure.rules.engine import create_rule_engine
from src.infrastructure.rules.legal_basis_rules import LegalBasisRuleSet
from src.infrastructure.rules.localization_rules import LocalizationRuleSet
from src.infrastructure.rules.consent_rules import ConsentRuleSet
from src.infrastructure.rules.processor_rules import ProcessorRuleSet
from src.infrastructure.rules.dsr_rules import DSRRuleSet


def _ids(findings) -> set[str]:
    """Extract rule_id strings from a list of RuleFinding."""
    return {f.rule_id for f in findings}


class TestLegalBasisRules:
    def setup_method(self):
        self.rs = LegalBasisRuleSet()

    def test_no_basis_violation(self):
        # The rule checks context["activity"]["status"] == "active" and no legal_bases
        fact = {
            "activity": {"id": "test-id", "status": "active"},
            "legal_bases": [],
        }
        findings = self.rs.evaluate(fact)
        assert "R-LB-001" in _ids(findings)

    def test_with_basis_no_violation(self):
        fact = {
            "activity": {"id": "test-id", "status": "active"},
            "legal_bases": [{"basis_type": "consent", "active": False}],
        }
        findings = self.rs.evaluate(fact)
        assert "R-LB-001" not in _ids(findings)

    def test_basis_missing_reference(self):
        # R-LB-003: basis without basis_reference
        fact = {
            "activity": {"id": "test-id", "status": "active"},
            "legal_bases": [{"id": "b1", "basis_type": "consent", "active": False}],
        }
        findings = self.rs.evaluate(fact)
        assert "R-LB-003" in _ids(findings)


class TestLocalizationRules:
    def setup_method(self):
        self.rs = LocalizationRuleSet()

    def test_returns_list(self):
        result = self.rs.evaluate({})
        assert isinstance(result, list)

    def test_evaluate_with_empty_context(self):
        # Should not crash — just return empty or some findings
        result = self.rs.evaluate({})
        assert isinstance(result, list)


class TestConsentRules:
    def setup_method(self):
        self.rs = ConsentRuleSet()

    def test_returns_list(self):
        result = self.rs.evaluate({})
        assert isinstance(result, list)


class TestProcessorRules:
    def setup_method(self):
        self.rs = ProcessorRuleSet()

    def test_returns_list(self):
        result = self.rs.evaluate({})
        assert isinstance(result, list)


class TestDSRRules:
    def setup_method(self):
        self.rs = DSRRuleSet()

    def test_returns_list(self):
        result = self.rs.evaluate({})
        assert isinstance(result, list)


class TestRuleEngine:
    def test_factory_creates_engine_with_all_rulesets(self):
        engine = create_rule_engine()
        assert len(engine._rule_sets) == 5

    def test_evaluate_empty_context_returns_list(self):
        engine = create_rule_engine()
        result = engine.evaluate({})
        assert isinstance(result, list)
