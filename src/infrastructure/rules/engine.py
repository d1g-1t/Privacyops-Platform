from __future__ import annotations

from src.infrastructure.rules import RuleEngine
from src.infrastructure.rules.consent_rules import ConsentRuleSet
from src.infrastructure.rules.dsr_rules import DSRRuleSet
from src.infrastructure.rules.legal_basis_rules import LegalBasisRuleSet
from src.infrastructure.rules.localization_rules import LocalizationRuleSet
from src.infrastructure.rules.processor_rules import ProcessorRuleSet


def create_rule_engine() -> RuleEngine:
    engine = RuleEngine()
    engine.register(LegalBasisRuleSet())
    engine.register(LocalizationRuleSet())
    engine.register(ConsentRuleSet())
    engine.register(ProcessorRuleSet())
    engine.register(DSRRuleSet())
    return engine
