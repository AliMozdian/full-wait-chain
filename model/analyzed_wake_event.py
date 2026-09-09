from dataclasses import dataclass

from .wake_event import WakeEvent
from .wake_analysis import WakeAnalysis


@dataclass(frozen=True)
class AnalyzedWakeEvent:
    event: WakeEvent
    analysis: WakeAnalysis
