# Generic stack matching engine
from typing import Sequence

from .rule import StackPattern


def _ordered_match(
    stack: Sequence[str],
    sequence: Sequence[str],
) -> bool:
    """
    Check whether sequence occurs in stack in the same order.
    Functions don't have to be adjacent.
    """

    if not sequence:
        return True

    index = 0

    for frame in stack:
        if frame == sequence[index]:
            index += 1

            if index == len(sequence):
                return True

    return False


def matches(
    stack: Sequence[str],
    pattern: StackPattern,
) -> bool:

    stack_set = set(stack)

    # Every required function must exist.
    if not pattern.required.issubset(stack_set):
        return False

    # At least one member of every any_of group.
    for group in pattern.any_of:
        if not stack_set.intersection(group):
            return False

    # Ordered signature.
    if not _ordered_match(stack, pattern.ordered):
        return False

    # Forbidden functions.
    if stack_set.intersection(pattern.forbidden):
        return False

    return True


def evidence(
    stack: Sequence[str],
    pattern: StackPattern,
) -> list[str]:

    stack_set = set(stack)

    result = []

    for function in pattern.required:
        if function in stack_set:
            result.append(function)

    for group in pattern.any_of:
        for function in group:
            if function in stack_set:
                result.append(function)

    for function in pattern.ordered:
        if function in stack_set:
            result.append(function)

    return list(dict.fromkeys(result)) # weird way to remove the duplicate functions in the result
