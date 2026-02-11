"""
Enforcement layer: validation and business rules.
Python enforces invariants - LLM never controls this logic.
"""
from typing import Tuple
from .schemas import BlockClassification


def check_confidence_threshold(
    classification: BlockClassification,
    threshold: float = 0.7
) -> bool:
    """
    Check if classification meets minimum confidence threshold.

    Args:
        classification: Validated BlockClassification object
        threshold: Minimum confidence required (0.0-1.0)

    Returns:
        True if confidence >= threshold, False otherwise
    """
    return classification.confidence >= threshold


def should_save(
    classification: BlockClassification,
    confidence_threshold: float = 0.7
) -> Tuple[bool, str]:
    """
    Determine if a classification should be saved to the database.

    Args:
        classification: Validated BlockClassification object
        confidence_threshold: Minimum confidence required

    Returns:
        Tuple of (should_save: bool, reason: str)

    Examples:
        >>> (True, "passed_threshold")
        >>> (False, "confidence_too_low")
    """
    # Check confidence threshold
    if not check_confidence_threshold(classification, confidence_threshold):
        return False, f"confidence_too_low ({classification.confidence} < {confidence_threshold})"

    # Pydantic already validated required fields
    # Could add more business rules here if needed

    return True, "passed_all_checks"
