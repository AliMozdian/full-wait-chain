# analysis result models
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Confidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass(frozen=True)
class Classification:
    category: str
    description: str
    confidence: Confidence
    evidence: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class WakeAnalysis:
    wake_cause: Classification
    target_wait: Classification
