from bisect import bisect_left, bisect_right


def validate_sorted(values):
    if any(values[i] > values[i + 1] for i in range(len(values) - 1)):
        raise ValueError("Binary search requires a sorted sequence.")


def lower_bound(values, target):
    """Return the first index whose value is >= target."""
    left, right = 0, len(values)

    while left < right:
        mid = left + (right - left) // 2

        if values[mid] < target:
            left = mid + 1
        else:
            right = mid

    return left


def upper_bound(values, target):
    """Return the first index whose value is > target."""
    left, right = 0, len(values)

    while left < right:
        mid = left + (right - left) // 2

        if values[mid] <= target:
            left = mid + 1
        else:
            right = mid

    return left


def first_occurrence(values, target):
    """Return the first index containing target, or -1."""
    index = lower_bound(values, target)

    if index < len(values) and values[index] == target:
        return index

    return -1


def last_occurrence(values, target):
    """Return the last index containing target, or -1."""
    index = upper_bound(values, target) - 1

    if index >= 0 and values[index] == target:
        return index

    return -1


def insertion_position(values, target):
    """Return the position where target can be inserted while preserving order."""
    return lower_bound(values, target)


def occurrence_range(values, target):
    """Return [first, last] for target, or [-1, -1] when absent."""
    first = first_occurrence(values, target)

    if first == -1:
        return [-1, -1]

    return [first, upper_bound(values, target) - 1]


def count_occurrences(values, target):
    """Count duplicates without scanning the duplicate range."""
    return upper_bound(values, target) - lower_bound(values, target)


def exact_search(values, target):
    """Standard binary search returning any matching index."""
    left, right = 0, len(values) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if values[mid] == target:
            return mid
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def demonstrate(values, targets):
    validate_sorted(values)

    print(f"Sorted data: {values}")
    print()

    for target in targets:
        first = first_occurrence(values, target)
        last = last_occurrence(values, target)
        lower = lower_bound(values, target)
        upper = upper_bound(values, target)
        insertion = insertion_position(values, target)
        count = count_occurrences(values, target)

        print(f"Target: {target}")
        print(f"  exact search:       {exact_search(values, target)}")
        print(f"  first occurrence:   {first}")
        print(f"  last occurrence:    {last}")
        print(f"  lower bound:        {lower}")
        print(f"  upper bound:        {upper}")
        print(f"  insertion position: {insertion}")
        print(f"  occurrence range:   {occurrence_range(values, target)}")
        print(f"  duplicate count:    {count}")
        print()


def verify_against_python(values, target):
    """Cross-check custom implementations against Python's bisect module."""
    expected_lower = bisect_left(values, target)
    expected_upper = bisect_right(values, target)

    assert lower_bound(values, target) == expected_lower
    assert upper_bound(values, target) == expected_upper
    assert insertion_position(values, target) == expected_lower
    assert count_occurrences(values, target) == expected_upper - expected_lower

    expected_first = (
        expected_lower if expected_lower < len(values) and values[expected_lower] == target else -1
    )
    expected_last = (
        expected_upper - 1 if expected_upper > 0 and values[expected_upper - 1] == target else -1
    )

    assert first_occurrence(values, target) == expected_first
    assert last_occurrence(values, target) == expected_last


def run_tests():
    cases = [
        ([], [0, 5]),
        ([1], [0, 1, 2]),
        ([1, 1, 1, 1], [0, 1, 2]),
        ([1, 2, 2, 4, 4, 4, 7], [0, 1, 2, 3, 4, 7, 8]),
        ([-10, -5, -5, 0, 3, 9], [-11, -5, 9, 10]),
    ]

    for values, targets in cases:
        validate_sorted(values)

        for target in targets:
            verify_against_python(values, target)

    try:
        validate_sorted([3, 2, 4])
    except ValueError:
        pass
    else:
        raise AssertionError("Unsorted input must be rejected.")

    print("All verification tests passed.")


if __name__ == "__main__":
    data = [1, 2, 2, 2, 4, 4, 7, 9, 9, 12]

    demonstrate(data, [0, 1, 2, 3, 4, 9, 13])
    run_tests()
