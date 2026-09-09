# Main public component
from model.wake_analysis import (
    Classification,
    Confidence,
    WakeAnalysis,
)
from model.wake_event import WakeEvent

from .matcher import matches, evidence
from .rule import ClassificationRule

from .patterns.wake_causes import WAKE_CAUSE_RULES
from .patterns.target_waits import TARGET_WAIT_RULES


class WakeAnalyzer:

    def __init__(
        self,
        wake_cause_rules: list[ClassificationRule] | None = None,
        target_wait_rules: list[ClassificationRule] | None = None,
    ):
        self.wake_cause_rules = sorted(
            wake_cause_rules or WAKE_CAUSE_RULES,
            key=lambda rule: rule.priority,
            reverse=True,
        )

        self.target_wait_rules = sorted(
            target_wait_rules or TARGET_WAIT_RULES,
            key=lambda rule: rule.priority,
            reverse=True,
        )

    # ---------------------------------------------------------------
    # Wake cause
    # ---------------------------------------------------------------

    def classify_wake_cause(self, event: WakeEvent) -> Classification:

        for rule in self.wake_cause_rules:

            if matches(event.waker_stack, rule.pattern):

                return Classification(
                    category=rule.category,
                    description=rule.description,
                    confidence=Confidence(rule.confidence),
                    evidence=evidence(
                        event.waker_stack,
                        rule.pattern,
                    ),
                )

        return Classification(
            category="unknown",
            description=(
                "The available waker stack does not contain enough "
                "information to determine the wake cause."
            ),
            confidence=Confidence.LOW,
            evidence=[], # maybe later I add all the stack to evidence
        )

    # ---------------------------------------------------------------
    # Target wait
    # ---------------------------------------------------------------

    def classify_target_wait(self, event: WakeEvent) -> Classification:

        for rule in self.target_wait_rules:

            if matches(event.target_stack, rule.pattern):

                return Classification(
                    category=rule.category,
                    description=rule.description,
                    confidence=Confidence(rule.confidence),
                    evidence=evidence(
                        event.target_stack,
                        rule.pattern,
                    ),
                )

        return Classification(
            category="unknown",
            description=(
                "The target stack does not match any known waiting "
                "pattern."
            ),
            confidence=Confidence.LOW,
            evidence=[], # maybe later I add all the stack to evidence
        )

    # ---------------------------------------------------------------
    # Complete analysis
    # ---------------------------------------------------------------

    def analyze(self, event: WakeEvent) -> WakeAnalysis:

        return WakeAnalysis(
            wake_cause=self.classify_wake_cause(event),
            target_wait=self.classify_target_wait(event),
        )
