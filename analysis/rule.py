# Generic rule/pattern definitions
from dataclasses import dataclass, field
from typing import FrozenSet, Sequence
from model.wake_analysis import Confidence


@dataclass(frozen=True)
class StackPattern:
    """
    Declarative description of a stack signature.

    required:
        Every function must exist in the stack.

    any_of:
        At least one function from each group must exist.

    ordered:
        Functions must appear in this order, but do not
        necessarily have to be adjacent.

    forbidden:
        None of these functions may appear.
    """

    required: FrozenSet[str] = frozenset()

    any_of: tuple[FrozenSet[str], ...] = ()

    ordered: tuple[str, ...] = ()

    forbidden: FrozenSet[str] = frozenset()


@dataclass(frozen=True)
class ClassificationRule:
    id: str
    category: str
    description: str
    priority: int
    pattern: StackPattern

    confidence: str = Confidence.HIGH

    target_pattern: StackPattern | None = None

    tags: tuple[str, ...] = field(default_factory=tuple)
