from advanced_arrays.algorithms import (
    apply_permutation,
    find_duplicate,
    find_majority_element,
    find_missing_number,
    longest_consecutive_sequence,
    max_subarray_sum,
    merge_intervals,
    product_except_self,
    rearrange_alternating,
    rotate_array,
    three_sum,
)


def test_max_subarray_with_mixed_values() -> None:
    assert max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6


def test_max_subarray_all_negative() -> None:
    assert max_subarray_sum([-8, -3, -6, -2, -5, -4]) == -2


def test_max_subarray_rejects_empty() -> None:
    try:
        max_subarray_sum([])
    except ValueError:
        pass
    else:
        raise AssertionError("empty input should raise ValueError")


def test_majority_exists() -> None:
    assert find_majority_element([2, 2, 1, 1, 1, 2, 2]) == 2


def test_majority_does_not_exist() -> None:
    assert find_majority_element([1, 2, 3, 4]) is None


def test_missing_number() -> None:
    assert find_missing_number([3, 0, 1]) == 2


def test_missing_zero() -> None:
    assert find_missing_number([1, 2, 3]) == 0


def test_duplicate() -> None:
    assert find_duplicate([1, 3, 4, 2, 2]) == 2


def test_rotation() -> None:
    assert rotate_array([1, 2, 3, 4, 5, 6, 7], 3) == [5, 6, 7, 1, 2, 3, 4]


def test_rotation_larger_than_length() -> None:
    assert rotate_array([1, 2, 3], 8) == [2, 3, 1]


def test_product_except_self_without_zero() -> None:
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]


def test_product_except_self_with_one_zero() -> None:
    assert product_except_self([1, 2, 0, 4]) == [0, 0, 8, 0]


def test_product_except_self_with_two_zeros() -> None:
    assert product_except_self([1, 0, 3, 0]) == [0, 0, 0, 0]


def test_alternating_signs() -> None:
    result = rearrange_alternating([1, 2, -3, -4, -5])
    assert result == [1, -3, 2, -4, -5]


def test_longest_consecutive() -> None:
    assert longest_consecutive_sequence([100, 4, 200, 1, 3, 2]) == 4


def test_three_sum_removes_duplicates() -> None:
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [(-1, -1, 2), (-1, 0, 1)]


def test_three_sum_custom_target() -> None:
    assert three_sum([1, 2, 3, 4, 5], 9) == [(1, 3, 5), (2, 3, 4)]


def test_merge_intervals() -> None:
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [9, 12]]) == [
        [1, 6],
        [8, 12],
    ]


def test_merge_intervals_nested() -> None:
    assert merge_intervals([[1, 10], [2, 3], [4, 8]]) == [[1, 10]]


def test_apply_permutation() -> None:
    assert apply_permutation([10, 20, 30], [2, 0, 1]) == [20, 30, 10]


def test_invalid_duplicate_range() -> None:
    try:
        find_duplicate([1, 2, 4, 2])
    except ValueError:
        pass
    else:
        raise AssertionError("invalid duplicate input should raise ValueError")
