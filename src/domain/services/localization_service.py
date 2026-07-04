from __future__ import annotations

from src.domain.entities.data_processing_activity import DataProcessingActivity
from src.domain.entities.localization_assessment import LocalizationAssessment
from src.domain.value_objects.localization_status import LocalizationStatus


class LocalizationDomainService:

    @staticmethod
    def evaluate_activity_localization(
        activity: DataProcessingActivity,
        assessment: LocalizationAssessment,
        *,
        strict_mode: bool = True,
    ) -> LocalizationStatus:
        new_status = assessment.evaluate(strict_mode=strict_mode)
        activity.localization_status = new_status
        return new_status

    @staticmethod
    def is_cross_border_blocked(
        activity: DataProcessingActivity,
    ) -> bool:
        return (
            activity.cross_border_transfer
            and activity.localization_status == LocalizationStatus.NON_COMPLIANT
        )
