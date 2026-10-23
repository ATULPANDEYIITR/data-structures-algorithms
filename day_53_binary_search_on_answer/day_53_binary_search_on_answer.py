from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


class ValidationError(ValueError):
    """Raised when an optimization problem has invalid input."""


def validate_positive_integers(values: Iterable[int], name: str) -> list[int]:
    result = list(values)
    if not result:
        raise ValidationError(f"{name} must not be empty")
    if any(not isinstance(x, int) or isinstance(x, bool) or x <= 0 for x in result):
        raise ValidationError(f"{name} must contain positive integers")
    return result


def binary_search_first_true(
    low: int,
    high: int,
    feasible: Callable[[int], bool],
) -> int | None:
    """
    Searches a monotonic boolean answer space.

    The predicate must have the form:
        False False False True True True
    over [low, high].
    """
    if low > high:
        return None

    answer = None
    while low <= high:
        mid = low + (high - low) // 2

        if feasible(mid):
            answer = mid
            high = mid - 1
        else:
            low = mid + 1

    return answer


def binary_search_last_true(
    low: int,
    high: int,
    feasible: Callable[[int], bool],
) -> int | None:
    """
    Searches a monotonic boolean answer space.

    The predicate must have the form:
        True True True False False False
    over [low, high].
    """
    if low > high:
        return None

    answer = None
    while low <= high:
        mid = low + (high - low) // 2

        if feasible(mid):
            answer = mid
            low = mid + 1
        else:
            high = mid - 1

    return answer


def minimum_ship_capacity(weights: list[int], days: int) -> int:
    """
    Minimum ship capacity needed to deliver all packages in order
    within the given number of days.
    """
    weights = validate_positive_integers(weights, "weights")

    if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
        raise ValidationError("days must be a positive integer")

    if days > len(weights):
        days = len(weights)

    def can_ship(capacity: int) -> bool:
        used_days = 1
        current_load = 0

        for weight in weights:
            if weight > capacity:
                return False

            if current_load + weight <= capacity:
                current_load += weight
            else:
                used_days += 1
                current_load = weight

        return used_days <= days

    return binary_search_first_true(
        max(weights),
        sum(weights),
        can_ship,
    )  # type: ignore[return-value]


def minimum_eating_speed(piles: list[int], hours: int) -> int:
    """Minimum integer eating speed that finishes all piles within hours."""
    piles = validate_positive_integers(piles, "piles")

    if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
        raise ValidationError("hours must be a positive integer")

    def can_finish(speed: int) -> bool:
        required_hours = 0

        for pile in piles:
            required_hours += (pile + speed - 1) // speed
            if required_hours > hours:
                return False

        return True

    return binary_search_first_true(1, max(piles), can_finish)  # type: ignore[return-value]


def aggressive_cows_max_distance(stalls: list[int], cows: int) -> int:
    """
    Maximum possible minimum distance between any two placed cows.
    """
    stalls = validate_positive_integers(stalls, "stalls")

    if len(stalls) < 2:
        raise ValidationError("at least two stalls are required")

    if not isinstance(cows, int) or isinstance(cows, bool):
        raise ValidationError("cows must be an integer")

    if cows < 2 or cows > len(stalls):
        raise ValidationError("cows must be between 2 and the number of stalls")

    stalls = sorted(stalls)

    def can_place(min_distance: int) -> bool:
        placed = 1
        last_position = stalls[0]

        for position in stalls[1:]:
            if position - last_position >= min_distance:
                placed += 1
                last_position = position

                if placed >= cows:
                    return True

        return False

    return binary_search_last_true(
        0,
        stalls[-1] - stalls[0],
        can_place,
    )  # type: ignore[return-value]


def minimum_partition_largest_sum(numbers: list[int], parts: int) -> int:
    """
    Split the array into at most 'parts' contiguous groups while
    minimizing the largest group sum.
    """
    numbers = validate_positive_integers(numbers, "numbers")

    if not isinstance(parts, int) or isinstance(parts, bool) or parts <= 0:
        raise ValidationError("parts must be a positive integer")

    parts = min(parts, len(numbers))

    def can_partition(limit: int) -> bool:
        groups = 1
        current_sum = 0

        for value in numbers:
            if value > limit:
                return False

            if current_sum + value <= limit:
                current_sum += value
            else:
                groups += 1
                current_sum = value

                if groups > parts:
                    return False

        return True

    return binary_search_first_true(
        max(numbers),
        sum(numbers),
        can_partition,
    )  # type: ignore[return-value]


def maximum_minimum_allocation(
    pages: list[int],
    students: int,
) -> int:
    """
    Allocate contiguous books to students and maximize the minimum
    pages assigned to any student.

    This is the dual form of a binary-search-on-answer problem:
    search the largest feasible minimum value.
    """
    pages = validate_positive_integers(pages, "pages")

    if not isinstance(students, int) or isinstance(students, bool):
        raise ValidationError("students must be an integer")

    if students <= 0 or students > len(pages):
        raise ValidationError(
            "students must be between 1 and the number of books"
        )

    def can_allocate(minimum_pages: int) -> bool:
        assigned_students = 1
        current_pages = 0

        for book_pages in pages:
            if current_pages + book_pages <= minimum_pages:
                current_pages += book_pages
            else:
                assigned_students += 1
                current_pages = book_pages

                if assigned_students > students:
                    return False

        return True

    # A minimum allocation is feasible for small values and becomes
    # infeasible after the maximum feasible threshold.
    return binary_search_last_true(
        0,
        sum(pages) // students,
        can_allocate,
    )  # type: ignore[return-value]


@dataclass(frozen=True)
class OptimizationCase:
    name: str
    answer: int


def run_examples() -> None:
    cases = [
        OptimizationCase(
            "Ship packages",
            minimum_ship_capacity([1, 2, 3, 1, 1, 1, 1], 4),
        ),
        OptimizationCase(
            "Eating speed",
            minimum_eating_speed([3, 6, 7, 11], 8),
        ),
        OptimizationCase(
            "Aggressive cows",
            aggressive_cows_max_distance([1, 2, 4, 8, 9], 3),
        ),
        OptimizationCase(
            "Minimize largest partition sum",
            minimum_partition_largest_sum([7, 2, 5, 10, 8], 2),
        ),
        OptimizationCase(
            "Maximize minimum allocation",
            maximum_minimum_allocation([10, 20, 30, 40], 2),
        ),
    ]

    for case in cases:
        print(f"{case.name}: {case.answer}")


def run_edge_case_checks() -> None:
    assert minimum_ship_capacity([5], 1) == 5
    assert minimum_eating_speed([1], 1) == 1
    assert aggressive_cows_max_distance([1, 2], 2) == 1
    assert minimum_partition_largest_sum([10, 20], 1) == 30
    assert maximum_minimum_allocation([10, 20], 2) == 10

    for invalid_call in (
        lambda: minimum_ship_capacity([], 2),
        lambda: minimum_eating_speed([1, 2], 0),
        lambda: aggressive_cows_max_distance([1], 2),
        lambda: minimum_partition_largest_sum([1, 2], 0),
        lambda: maximum_minimum_allocation([1, 2], 3),
    ):
        try:
            invalid_call()
        except ValidationError:
            pass
        else:
            raise AssertionError("Expected ValidationError")


if __name__ == "__main__":
    run_examples()
    run_edge_case_checks()
