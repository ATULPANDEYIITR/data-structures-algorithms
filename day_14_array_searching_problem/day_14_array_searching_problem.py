"""
Array Searching Problems
=========================

A comprehensive study script for linear search and searching-related array problems.

Topics covered:
1. Linear search fundamentals
2. First occurrence
3. Last occurrence
4. All occurrences
5. Duplicate detection
6. Counting occurrences
7. Searching under conditions
8. First/last element satisfying a condition
9. Search in unsorted arrays
10. Search with custom predicates
11. Index-based searching
12. Searching multiple targets
13. Searching pairs and combinations
14. Search-related array transformations
15. Edge cases and exceptions
16. Complexity analysis
17. Recursive linear search
18. Sentinel-style search
19. Generic searching with predicates
20. Search in strings and nested arrays
21. Testing and validation
22. Practical problem-solving patterns
23. Performance considerations
24. Advanced reusable search utilities

The script uses only Python's standard library.
"""


# ============================================================
# 1. INTRODUCTION TO ARRAY SEARCHING
# ============================================================

print("=" * 70)
print("ARRAY SEARCHING PROBLEMS")
print("=" * 70)

print("""
Array searching means locating an element, position, occurrence,
or group of elements inside a sequence.

Python uses the list data structure for most array-like tasks.

Example:
    numbers = [10, 20, 30, 40, 50]

A search problem may ask:
- Does a value exist?
- Where does it occur first?
- Where does it occur last?
- How many times does it occur?
- What are all its positions?
- What is the first value satisfying a condition?
- What is the last value satisfying a condition?
- Does the array contain duplicates?
- Can two elements satisfy a target condition?

Linear search is the fundamental searching technique for an
unsorted array.
""")

numbers = [10, 20, 30, 40, 50]

print("Example array:", numbers)
print("Searching for 30 using Python's membership operator:", 30 in numbers)


# ============================================================
# 2. BASIC LINEAR SEARCH
# ============================================================

print("\n" + "=" * 70)
print("2. BASIC LINEAR SEARCH")
print("=" * 70)

print("""
Linear search examines elements one by one from left to right.

For:
    [10, 20, 30, 40, 50]

Searching for 40 means:
    compare 40 with 10
    compare 40 with 20
    compare 40 with 30
    compare 40 with 40 -> found

The algorithm does not require the array to be sorted.
""")


def linear_search(array, target):
    """
    Return the index of target's first occurrence.

    Return -1 when target does not exist.

    Time complexity:
        Best case: O(1)
        Average case: O(n)
        Worst case: O(n)

    Space complexity:
        O(1)
    """
    for index, value in enumerate(array):
        if value == target:
            return index

    return -1


numbers = [10, 20, 30, 40, 50]

print("Array:", numbers)
print("Index of 30:", linear_search(numbers, 30))
print("Index of 99:", linear_search(numbers, 99))


# ============================================================
# 3. RETURNING A BOOLEAN
# ============================================================

print("\n" + "=" * 70)
print("3. SEARCHING FOR EXISTENCE")
print("=" * 70)


def contains_value(array, target):
    """Return True if target exists, otherwise False."""
    for value in array:
        if value == target:
            return True

    return False


numbers = [4, 8, 15, 16, 23, 42]

print("Array:", numbers)
print("Contains 15:", contains_value(numbers, 15))
print("Contains 100:", contains_value(numbers, 100))


# ============================================================
# 4. FIRST OCCURRENCE
# ============================================================

print("\n" + "=" * 70)
print("4. FIRST OCCURRENCE")
print("=" * 70)

print("""
When duplicates exist, ordinary linear search naturally returns
the first occurrence because the array is scanned from left to right.
""")


def first_occurrence(array, target):
    """
    Return the index of the first occurrence of target.

    Return -1 when target does not exist.
    """
    for index, value in enumerate(array):
        if value == target:
            return index

    return -1


numbers = [5, 2, 8, 2, 9, 2, 1]

print("Array:", numbers)
print("First occurrence of 2:", first_occurrence(numbers, 2))
print("First occurrence of 9:", first_occurrence(numbers, 9))
print("First occurrence of 100:", first_occurrence(numbers, 100))


# ============================================================
# 5. LAST OCCURRENCE
# ============================================================

print("\n" + "=" * 70)
print("5. LAST OCCURRENCE")
print("=" * 70)

print("""
To find the last occurrence, continue scanning after every match
and remember the most recent matching index.
""")


def last_occurrence(array, target):
    """
    Return the index of the last occurrence of target.

    Return -1 when target does not exist.
    """
    last_index = -1

    for index, value in enumerate(array):
        if value == target:
            last_index = index

    return last_index


numbers = [5, 2, 8, 2, 9, 2, 1]

print("Array:", numbers)
print("Last occurrence of 2:", last_occurrence(numbers, 2))
print("Last occurrence of 9:", last_occurrence(numbers, 9))
print("Last occurrence of 100:", last_occurrence(numbers, 100))


# ============================================================
# 6. ALL OCCURRENCES
# ============================================================

print("\n" + "=" * 70)
print("6. ALL OCCURRENCES")
print("=" * 70)


def all_occurrences(array, target):
    """
    Return a list containing every index where target occurs.
    """
    positions = []

    for index, value in enumerate(array):
        if value == target:
            positions.append(index)

    return positions


numbers = [7, 3, 7, 1, 7, 9, 3]

print("Array:", numbers)
print("All positions of 7:", all_occurrences(numbers, 7))
print("All positions of 3:", all_occurrences(numbers, 3))
print("All positions of 100:", all_occurrences(numbers, 100))


# ============================================================
# 7. COUNTING OCCURRENCES
# ============================================================

print("\n" + "=" * 70)
print("7. COUNTING OCCURRENCES")
print("=" * 70)


def count_occurrences(array, target):
    """Count how many times target appears in the array."""
    count = 0

    for value in array:
        if value == target:
            count += 1

    return count


numbers = [4, 4, 2, 7, 4, 9, 2]

print("Array:", numbers)
print("Count of 4:", count_occurrences(numbers, 4))
print("Count of 2:", count_occurrences(numbers, 2))
print("Count of 100:", count_occurrences(numbers, 100))


# ============================================================
# 8. FIRST MATCH AFTER A GIVEN INDEX
# ============================================================

print("\n" + "=" * 70)
print("8. SEARCHING FROM A GIVEN START INDEX")
print("=" * 70)


def find_from_index(array, target, start_index=0):
    """
    Find target starting from start_index.

    Negative starting indexes are treated as zero.
    If start_index is beyond the array, -1 is returned.
    """
    if start_index < 0:
        start_index = 0

    for index in range(start_index, len(array)):
        if array[index] == target:
            return index

    return -1


numbers = [10, 20, 30, 20, 40, 20]

print("Array:", numbers)
print("Search 20 from index 0:", find_from_index(numbers, 20, 0))
print("Search 20 from index 2:", find_from_index(numbers, 20, 2))
print("Search 20 from index 4:", find_from_index(numbers, 20, 4))
print("Search 20 from index 20:", find_from_index(numbers, 20, 20))


# ============================================================
# 9. SEARCHING WITHIN A RANGE
# ============================================================

print("\n" + "=" * 70)
print("9. SEARCHING WITHIN A RANGE")
print("=" * 70)


def search_range(array, target, start, end):
    """
    Search for target in the inclusive range [start, end].

    Invalid or empty ranges return -1.
    """
    if not array:
        return -1

    if start < 0:
        start = 0

    if end >= len(array):
        end = len(array) - 1

    if start > end:
        return -1

    for index in range(start, end + 1):
        if array[index] == target:
            return index

    return -1


numbers = [10, 20, 30, 40, 50, 60, 70]

print("Array:", numbers)
print("Search 50 from index 2 to 5:", search_range(numbers, 50, 2, 5))
print("Search 20 from index 2 to 5:", search_range(numbers, 20, 2, 5))
print("Search 70 from index -5 to 20:", search_range(numbers, 70, -5, 20))


# ============================================================
# 10. FIRST ELEMENT SATISFYING A CONDITION
# ============================================================

print("\n" + "=" * 70)
print("10. FIRST ELEMENT SATISFYING A CONDITION")
print("=" * 70)

print("""
Many searching problems do not ask for an exact value.

Examples:
- first even number
- first negative number
- first number greater than 100
- first string longer than five characters

A predicate is a function that returns True or False.
""")


def first_matching(array, condition):
    """
    Return (index, value) for the first element satisfying condition.

    Return (-1, None) if no element matches.
    """
    for index, value in enumerate(array):
        if condition(value):
            return index, value

    return -1, None


numbers = [11, 13, 17, 22, 25, 30]

print("Array:", numbers)
print("First even number:", first_matching(numbers, lambda x: x % 2 == 0))
print(
    "First number greater than 20:",
    first_matching(numbers, lambda x: x > 20),
)
print(
    "First negative number:",
    first_matching(numbers, lambda x: x < 0),
)


# ============================================================
# 11. LAST ELEMENT SATISFYING A CONDITION
# ============================================================

print("\n" + "=" * 70)
print("11. LAST ELEMENT SATISFYING A CONDITION")
print("=" * 70)


def last_matching(array, condition):
    """
    Return (index, value) for the last element satisfying condition.
    """
    last_match = (-1, None)

    for index, value in enumerate(array):
        if condition(value):
            last_match = (index, value)

    return last_match


numbers = [11, 22, 13, 40, 17, 60]

print("Array:", numbers)
print(
    "Last even number:",
    last_matching(numbers, lambda x: x % 2 == 0),
)
print(
    "Last number greater than 30:",
    last_matching(numbers, lambda x: x > 30),
)


# ============================================================
# 12. ALL ELEMENTS SATISFYING A CONDITION
# ============================================================

print("\n" + "=" * 70)
print("12. ALL MATCHES UNDER A CONDITION")
print("=" * 70)


def all_matching(array, condition):
    """Return (index, value) pairs for every matching element."""
    matches = []

    for index, value in enumerate(array):
        if condition(value):
            matches.append((index, value))

    return matches


numbers = [3, 10, 15, 22, 27, 30, 41]

print("Array:", numbers)
print(
    "All even values:",
    all_matching(numbers, lambda x: x % 2 == 0),
)
print(
    "All values greater than 20:",
    all_matching(numbers, lambda x: x > 20),
)


# ============================================================
# 13. SEARCHING FOR A NEGATIVE NUMBER
# ============================================================

print("\n" + "=" * 70)
print("13. SEARCHING FOR NEGATIVE VALUES")
print("=" * 70)


def first_negative(array):
    """Return the index of the first negative number."""
    for index, value in enumerate(array):
        if value < 0:
            return index

    return -1


numbers = [10, 20, 5, -3, 7, -10]

print("Array:", numbers)
print("First negative index:", first_negative(numbers))


# ============================================================
# 14. SEARCHING FOR AN EVEN NUMBER
# ============================================================

print("\n" + "=" * 70)
print("14. SEARCHING FOR EVEN VALUES")
print("=" * 70)


def first_even(array):
    """Return the first even value and its index."""
    for index, value in enumerate(array):
        if value % 2 == 0:
            return index, value

    return -1, None


numbers = [3, 5, 7, 11, 14, 19]

print("Array:", numbers)
print("First even value:", first_even(numbers))


# ============================================================
# 15. SEARCHING FOR THE FIRST VALUE GREATER THAN A THRESHOLD
# ============================================================

print("\n" + "=" * 70)
print("15. FIRST VALUE GREATER THAN A THRESHOLD")
print("=" * 70)


def first_greater_than(array, threshold):
    """Return the first value greater than threshold."""
    for index, value in enumerate(array):
        if value > threshold:
            return index, value

    return -1, None


numbers = [12, 18, 25, 9, 31, 44]

print("Array:", numbers)
print("First value greater than 20:", first_greater_than(numbers, 20))
print("First value greater than 50:", first_greater_than(numbers, 50))


# ============================================================
# 16. SEARCHING FOR THE FIRST VALUE WITHIN AN INTERVAL
# ============================================================

print("\n" + "=" * 70)
print("16. SEARCHING WITHIN AN INTERVAL")
print("=" * 70)


def first_in_interval(array, minimum, maximum):
    """
    Return the first value satisfying:
        minimum <= value <= maximum
    """
    for index, value in enumerate(array):
        if minimum <= value <= maximum:
            return index, value

    return -1, None


numbers = [5, 90, 12, 47, 63, 8]

print("Array:", numbers)
print(
    "First value from 40 through 60:",
    first_in_interval(numbers, 40, 60),
)


# ============================================================
# 17. SEARCHING FOR A MAXIMUM VALUE
# ============================================================

print("\n" + "=" * 70)
print("17. SEARCHING FOR A MAXIMUM")
print("=" * 70)

print("""
Finding a maximum is also a search problem.

Instead of searching for a known target, we search for an element
that satisfies the property "greater than every previously examined
element."
""")


def find_maximum(array):
    """
    Return (index, value) of the maximum element.

    Raise ValueError for an empty array.
    """
    if not array:
        raise ValueError("Cannot find a maximum in an empty array.")

    maximum_index = 0

    for index in range(1, len(array)):
        if array[index] > array[maximum_index]:
            maximum_index = index

    return maximum_index, array[maximum_index]


numbers = [18, 5, 92, 31, 76]

print("Array:", numbers)
print("Maximum:", find_maximum(numbers))

try:
    print(find_maximum([]))
except ValueError as error:
    print("Expected error:", error)


# ============================================================
# 18. SEARCHING FOR A MINIMUM
# ============================================================

print("\n" + "=" * 70)
print("18. SEARCHING FOR A MINIMUM")
print("=" * 70)


def find_minimum(array):
    """
    Return (index, value) of the minimum element.

    Raise ValueError for an empty array.
    """
    if not array:
        raise ValueError("Cannot find a minimum in an empty array.")

    minimum_index = 0

    for index in range(1, len(array)):
        if array[index] < array[minimum_index]:
            minimum_index = index

    return minimum_index, array[minimum_index]


numbers = [18, 5, 92, 31, 76]

print("Array:", numbers)
print("Minimum:", find_minimum(numbers))


# ============================================================
# 19. DUPLICATE DETECTION
# ============================================================

print("\n" + "=" * 70)
print("19. DUPLICATE DETECTION")
print("=" * 70)

print("""
A duplicate exists when a value occurs at least twice.

A direct nested-loop approach demonstrates the idea but has O(n^2)
time complexity.
""")


def contains_duplicate_brute_force(array):
    """
    Detect duplicates using pairwise comparison.

    Time complexity: O(n^2)
    Space complexity: O(1)
    """
    for first_index in range(len(array)):
        for second_index in range(first_index + 1, len(array)):
            if array[first_index] == array[second_index]:
                return True

    return False


numbers = [3, 7, 1, 9, 3]

print("Array:", numbers)
print(
    "Contains duplicate using pairwise search:",
    contains_duplicate_brute_force(numbers),
)


# ============================================================
# 20. DUPLICATE DETECTION USING A SET
# ============================================================

print("\n" + "=" * 70)
print("20. DUPLICATE DETECTION USING A SET")
print("=" * 70)

print("""
A set provides average O(1) membership checks.

This reduces duplicate detection to O(n) average time at the cost
of O(n) additional memory.
""")


def contains_duplicate(array):
    """
    Detect duplicates using a set.

    Average time: O(n)
    Extra space: O(n)
    """
    seen = set()

    for value in array:
        if value in seen:
            return True

        seen.add(value)

    return False


print("Contains duplicate:", contains_duplicate([1, 2, 3, 4]))
print("Contains duplicate:", contains_duplicate([1, 2, 3, 2]))


# ============================================================
# 21. FINDING THE FIRST DUPLICATE
# ============================================================

print("\n" + "=" * 70)
print("21. FIRST DUPLICATE")
print("=" * 70)


def first_duplicate(array):
    """
    Return the first value encountered whose previous occurrence
    has already been seen.

    Return None when there is no duplicate.
    """
    seen = set()

    for value in array:
        if value in seen:
            return value

        seen.add(value)

    return None


numbers = [5, 3, 7, 3, 9, 5]

print("Array:", numbers)
print("First duplicate encountered:", first_duplicate(numbers))


# ============================================================
# 22. FINDING ALL DUPLICATE VALUES
# ============================================================

print("\n" + "=" * 70)
print("22. ALL DUPLICATE VALUES")
print("=" * 70)


def all_duplicate_values(array):
    """
    Return unique values that occur more than once.

    The order corresponds to the first time each duplicate is detected.
    """
    seen = set()
    duplicates = []
    duplicate_set = set()

    for value in array:
        if value in seen and value not in duplicate_set:
            duplicates.append(value)
            duplicate_set.add(value)
        else:
            seen.add(value)

    return duplicates


numbers = [4, 2, 4, 7, 2, 8, 4, 9, 7]

print("Array:", numbers)
print("Duplicate values:", all_duplicate_values(numbers))


# ============================================================
# 23. FREQUENCY-BASED SEARCH
# ============================================================

print("\n" + "=" * 70)
print("23. FREQUENCY-BASED SEARCH")
print("=" * 70)


def build_frequency_map(array):
    """Build a dictionary containing the frequency of each value."""
    frequencies = {}

    for value in array:
        frequencies[value] = frequencies.get(value, 0) + 1

    return frequencies


numbers = [4, 4, 2, 7, 4, 2, 9, 7]

frequencies = build_frequency_map(numbers)

print("Array:", numbers)
print("Frequency map:", frequencies)


def find_values_with_frequency(array, required_frequency):
    """
    Return values occurring exactly required_frequency times.
    """
    frequencies = build_frequency_map(array)

    return [
        value
        for value, frequency in frequencies.items()
        if frequency == required_frequency
    ]


print("Values occurring exactly twice:",
      find_values_with_frequency(numbers, 2))


# ============================================================
# 24. FIRST NON-REPEATING ELEMENT
# ============================================================

print("\n" + "=" * 70)
print("24. FIRST NON-REPEATING ELEMENT")
print("=" * 70)


def first_non_repeating(array):
    """
    Return (index, value) for the first value whose frequency is one.

    Time: O(n) average
    Space: O(n)
    """
    frequencies = build_frequency_map(array)

    for index, value in enumerate(array):
        if frequencies[value] == 1:
            return index, value

    return -1, None


numbers = [4, 5, 4, 7, 5, 9, 7, 10]

print("Array:", numbers)
print("First non-repeating value:", first_non_repeating(numbers))


# ============================================================
# 25. FIRST REPEATING ELEMENT
# ============================================================

print("\n" + "=" * 70)
print("25. FIRST REPEATING ELEMENT")
print("=" * 70)


def first_repeating_by_frequency(array):
    """
    Find the first element from left to right whose total frequency
    is greater than one.
    """
    frequencies = build_frequency_map(array)

    for index, value in enumerate(array):
        if frequencies[value] > 1:
            return index, value

    return -1, None


numbers = [10, 5, 7, 5, 8, 10]

print("Array:", numbers)
print(
    "First value that repeats:",
    first_repeating_by_frequency(numbers),
)


# ============================================================
# 26. SEARCHING FOR A PAIR WITH A TARGET SUM
# ============================================================

print("\n" + "=" * 70)
print("26. SEARCHING FOR A PAIR WITH A TARGET SUM")
print("=" * 70)

print("""
This problem searches for two different array positions whose
values add up to a target.

A nested-loop solution takes O(n^2).
A hash-set solution takes O(n) average time.
""")


def two_sum_brute_force(array, target):
    """
    Return indices of a pair whose values sum to target.

    Return None when no pair exists.

    Time: O(n^2)
    Space: O(1)
    """
    for first_index in range(len(array)):
        for second_index in range(first_index + 1, len(array)):
            if array[first_index] + array[second_index] == target:
                return first_index, second_index

    return None


def two_sum_hash_set(array, target):
    """
    Return indices of a pair whose values sum to target.

    Time: O(n) average
    Space: O(n)
    """
    seen = {}

    for index, value in enumerate(array):
        required = target - value

        if required in seen:
            return seen[required], index

        seen[value] = index

    return None


numbers = [2, 7, 11, 15]

print("Array:", numbers)
print("Target:", 9)
print("Brute force:", two_sum_brute_force(numbers, 9))
print("Hash-set approach:", two_sum_hash_set(numbers, 9))


# ============================================================
# 27. ALL PAIRS WITH A TARGET SUM
# ============================================================

print("\n" + "=" * 70)
print("27. ALL PAIRS WITH A TARGET SUM")
print("=" * 70)


def all_two_sum_pairs(array, target):
    """
    Return all index pairs whose values add to target.

    Each pair uses two distinct positions.
    """
    pairs = []

    for first_index in range(len(array)):
        for second_index in range(first_index + 1, len(array)):
            if array[first_index] + array[second_index] == target:
                pairs.append((first_index, second_index))

    return pairs


numbers = [2, 7, 11, 2, 9, 0, 7]

print("Array:", numbers)
print("All index pairs summing to 9:", all_two_sum_pairs(numbers, 9))


# ============================================================
# 28. SEARCHING FOR A TRIPLET WITH TARGET SUM
# ============================================================

print("\n" + "=" * 70)
print("28. SEARCHING FOR A TRIPLET WITH TARGET SUM")
print("=" * 70)


def three_sum_brute_force(array, target):
    """
    Return one triplet of indices whose values sum to target.

    Time: O(n^3)
    Space: O(1)
    """
    for first_index in range(len(array)):
        for second_index in range(first_index + 1, len(array)):
            for third_index in range(second_index + 1, len(array)):
                total = (
                    array[first_index]
                    + array[second_index]
                    + array[third_index]
                )

                if total == target:
                    return first_index, second_index, third_index

    return None


numbers = [1, 4, 6, 8, 10]

print("Array:", numbers)
print("Triplet for target 15:", three_sum_brute_force(numbers, 15))


# ============================================================
# 29. SEARCHING FOR TWO EQUAL VALUES
# ============================================================

print("\n" + "=" * 70)
print("29. SEARCHING FOR TWO EQUAL VALUES")
print("=" * 70)


def find_duplicate_pair(array):
    """
    Return indices of the first duplicate pair found using a set.
    """
    seen = {}

    for index, value in enumerate(array):
        if value in seen:
            return seen[value], index

        seen[value] = index

    return None


numbers = [8, 3, 5, 8, 2]

print("Array:", numbers)
print("Duplicate pair indices:", find_duplicate_pair(numbers))


# ============================================================
# 30. SEARCHING IN A STRING
# ============================================================

print("\n" + "=" * 70)
print("30. SEARCHING IN A STRING")
print("=" * 70)

print("""
A string is a sequence, so many array-searching ideas apply to it.
""")


def first_character_index(text, target):
    """Return the first index of target character."""
    for index, character in enumerate(text):
        if character == target:
            return index

    return -1


text = "programming"

print("Text:", text)
print("First 'g':", first_character_index(text, "g"))
print("First 'z':", first_character_index(text, "z"))


# ============================================================
# 31. CASE-INSENSITIVE SEARCH
# ============================================================

print("\n" + "=" * 70)
print("31. CASE-INSENSITIVE SEARCH")
print("=" * 70)


def case_insensitive_search(words, target):
    """
    Search strings without considering letter case.

    The original index is returned.
    """
    normalized_target = target.casefold()

    for index, word in enumerate(words):
        if word.casefold() == normalized_target:
            return index

    return -1


words = ["Python", "Java", "JavaScript", "C++"]

print("Words:", words)
print(
    "Search for 'python':",
    case_insensitive_search(words, "python"),
)
print(
    "Search for 'JAVASCRIPT':",
    case_insensitive_search(words, "JAVASCRIPT"),
)


# ============================================================
# 32. SEARCHING OBJECTS BY AN ATTRIBUTE
# ============================================================

print("\n" + "=" * 70)
print("32. SEARCHING OBJECTS BY AN ATTRIBUTE")
print("=" * 70)


class Student:
    """Represent a student for object-based searching."""

    def __init__(self, roll_number, name, score):
        self.roll_number = roll_number
        self.name = name
        self.score = score

    def __repr__(self):
        return (
            f"Student("
            f"roll_number={self.roll_number}, "
            f"name={self.name!r}, "
            f"score={self.score}"
            f")"
        )


students = [
    Student(101, "Asha", 88),
    Student(102, "Ravi", 76),
    Student(103, "Meera", 94),
    Student(104, "Karan", 81),
]


def find_student_by_roll_number(students, roll_number):
    """Search student objects by roll number."""
    for student in students:
        if student.roll_number == roll_number:
            return student

    return None


print("Students:", students)
print(
    "Student with roll number 103:",
    find_student_by_roll_number(students, 103),
)


# ============================================================
# 33. SEARCHING OBJECTS USING A PREDICATE
# ============================================================

print("\n" + "=" * 70)
print("33. SEARCHING OBJECTS USING A PREDICATE")
print("=" * 70)


def first_student_with_score_at_least(students, minimum_score):
    """
    Return the first student whose score meets the threshold.
    """
    for student in students:
        if student.score >= minimum_score:
            return student

    return None


print(
    "First student with score >= 90:",
    first_student_with_score_at_least(students, 90),
)


# ============================================================
# 34. SEARCHING NESTED ARRAYS
# ============================================================

print("\n" + "=" * 70)
print("34. SEARCHING NESTED ARRAYS")
print("=" * 70)


def search_nested_array(matrix, target):
    """
    Search a two-dimensional list.

    Return (row, column), or (-1, -1) if absent.
    """
    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if value == target:
                return row_index, column_index

    return -1, -1


matrix = [
    [10, 20, 30],
    [40, 50, 60],
    [70, 80, 90],
]

print("Matrix:", matrix)
print("Position of 60:", search_nested_array(matrix, 60))
print("Position of 100:", search_nested_array(matrix, 100))


# ============================================================
# 35. SEARCHING A MATRIX FOR ALL OCCURRENCES
# ============================================================

print("\n" + "=" * 70)
print("35. ALL MATCHES IN A MATRIX")
print("=" * 70)


def all_nested_occurrences(matrix, target):
    """Return every (row, column) position containing target."""
    positions = []

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if value == target:
                positions.append((row_index, column_index))

    return positions


matrix = [
    [1, 2, 3],
    [2, 4, 2],
    [5, 2, 6],
]

print("Matrix:", matrix)
print("All positions of 2:", all_nested_occurrences(matrix, 2))


# ============================================================
# 36. RECURSIVE LINEAR SEARCH
# ============================================================

print("\n" + "=" * 70)
print("36. RECURSIVE LINEAR SEARCH")
print("=" * 70)

print("""
Recursion can express linear search by checking one position and
then searching the remaining suffix.

It is educational but generally less practical than iteration in
Python because recursion adds function-call overhead and Python
has a recursion-depth limit.
""")


def recursive_linear_search(array, target, index=0):
    """
    Recursive first-occurrence search.

    Return -1 when target is absent.
    """
    if index >= len(array):
        return -1

    if array[index] == target:
        return index

    return recursive_linear_search(array, target, index + 1)


numbers = [10, 20, 30, 40]

print("Recursive search for 30:",
      recursive_linear_search(numbers, 30))
print("Recursive search for 99:",
      recursive_linear_search(numbers, 99))


# ============================================================
# 37. RECURSIVE LAST OCCURRENCE
# ============================================================

print("\n" + "=" * 70)
print("37. RECURSIVE LAST OCCURRENCE")
print("=" * 70)


def recursive_last_occurrence(array, target, index=0):
    """
    Recursively find the last occurrence.

    The suffix is searched first, and the current index is used only
    when no later occurrence exists.
    """
    if index >= len(array):
        return -1

    later_index = recursive_last_occurrence(array, target, index + 1)

    if later_index != -1:
        return later_index

    if array[index] == target:
        return index

    return -1


numbers = [4, 7, 4, 9, 4]

print(
    "Last occurrence of 4:",
    recursive_last_occurrence(numbers, 4),
)


# ============================================================
# 38. SENTINEL LINEAR SEARCH
# ============================================================

print("\n" + "=" * 70)
print("38. SENTINEL LINEAR SEARCH")
print("=" * 70)

print("""
Sentinel search places the target temporarily at the end of a
mutable array so the loop can avoid checking the boundary on every
iteration.

This technique is mainly useful for understanding low-level search
optimizations. Python's normal loop is usually clearer and the
performance benefit is rarely important.
""")


def sentinel_search(array, target):
    """
    Perform sentinel-style linear search.

    A copy is used so the caller's list is never modified.
    """
    if not array:
        return -1

    working = list(array)
    working.append(target)

    index = 0

    while working[index] != target:
        index += 1

    if index == len(array):
        return -1

    return index


numbers = [12, 25, 38, 41]

print("Sentinel search for 38:", sentinel_search(numbers, 38))
print("Sentinel search for 99:", sentinel_search(numbers, 99))
print("Original array remains:", numbers)


# ============================================================
# 39. CUSTOM EQUALITY RULE
# ============================================================

print("\n" + "=" * 70)
print("39. CUSTOM EQUALITY RULE")
print("=" * 70)

print("""
Sometimes ordinary == is not the desired matching rule.

For example:
- strings should be compared without case
- numbers may be compared after rounding
- objects may be compared by an identifier
""")


def find_by_key(array, target, key_function):
    """
    Search using a transformed comparison key.

    Both the array value and target are passed through key_function.
    """
    target_key = key_function(target)

    for index, value in enumerate(array):
        if key_function(value) == target_key:
            return index

    return -1


words = ["Python", "JAVA", "Ruby", "JavaScript"]

print(
    "Case-insensitive search for 'java':",
    find_by_key(words, "java", str.casefold),
)


# ============================================================
# 40. FINDING THE CLOSEST VALUE
# ============================================================

print("\n" + "=" * 70)
print("40. SEARCHING FOR THE CLOSEST VALUE")
print("=" * 70)


def closest_value(array, target):
    """
    Return the index and value closest to target.

    In case of equal distance, the earlier element wins.
    """
    if not array:
        raise ValueError("Cannot search an empty array.")

    best_index = 0
    best_distance = abs(array[0] - target)

    for index in range(1, len(array)):
        distance = abs(array[index] - target)

        if distance < best_distance:
            best_distance = distance
            best_index = index

    return best_index, array[best_index]


numbers = [10, 18, 25, 31, 42]

print("Array:", numbers)
print("Closest to 27:", closest_value(numbers, 27))
print("Closest to 20:", closest_value(numbers, 20))


# ============================================================
# 41. FIRST VALUE ABOVE AN AVERAGE
# ============================================================

print("\n" + "=" * 70)
print("41. SEARCHING RELATIVE TO AN ARRAY PROPERTY")
print("=" * 70)


def first_above_average(array):
    """
    Find the first value greater than the arithmetic mean.
    """
    if not array:
        return -1, None

    average = sum(array) / len(array)

    for index, value in enumerate(array):
        if value > average:
            return index, value

    return -1, None


numbers = [10, 20, 30, 40, 50]

print("Array:", numbers)
print("First value above average:", first_above_average(numbers))


# ============================================================
# 42. SEARCHING FOR A LOCAL PEAK
# ============================================================

print("\n" + "=" * 70)
print("42. SEARCHING FOR A LOCAL PEAK")
print("=" * 70)

print("""
A local peak is an element greater than its immediate neighbors.

Boundary elements require a separate rule because they have only
one neighbor.
""")


def find_first_local_peak(array):
    """
    Find the first interior local peak.

    Only elements having both neighbors are considered.
    """
    for index in range(1, len(array) - 1):
        if array[index] > array[index - 1] and array[index] > array[index + 1]:
            return index, array[index]

    return -1, None


numbers = [1, 3, 7, 5, 4, 8, 2]

print("Array:", numbers)
print("First interior local peak:", find_first_local_peak(numbers))


# ============================================================
# 43. SEARCHING FOR A VALLEY
# ============================================================

print("\n" + "=" * 70)
print("43. SEARCHING FOR A LOCAL VALLEY")
print("=" * 70)


def find_first_local_valley(array):
    """Find the first interior value smaller than both neighbors."""
    for index in range(1, len(array) - 1):
        if array[index] < array[index - 1] and array[index] < array[index + 1]:
            return index, array[index]

    return -1, None


numbers = [8, 5, 9, 4, 7, 10]

print("Array:", numbers)
print("First local valley:", find_first_local_valley(numbers))


# ============================================================
# 44. SEARCHING FOR A TRANSITION
# ============================================================

print("\n" + "=" * 70)
print("44. SEARCHING FOR A TRANSITION")
print("=" * 70)

print("""
A transition occurs when a condition changes between adjacent
elements.

Example:
    [False, False, False, True, True]

The first True is the transition point.
""")


def first_true(array):
    """Return the first index containing a truthy value."""
    for index, value in enumerate(array):
        if value:
            return index

    return -1


conditions = [False, False, False, True, True]

print("Conditions:", conditions)
print("First True:", first_true(conditions))


# ============================================================
# 45. SEARCHING FOR A CHANGE BETWEEN ADJACENT ELEMENTS
# ============================================================

print("\n" + "=" * 70)
print("45. SEARCHING FOR AN ADJACENT CHANGE")
print("=" * 70)


def first_change(array):
    """
    Return the first index i where array[i] differs from array[i - 1].
    """
    for index in range(1, len(array)):
        if array[index] != array[index - 1]:
            return index, array[index - 1], array[index]

    return -1, None, None


numbers = [5, 5, 5, 8, 8, 10]

print("Array:", numbers)
print("First change:", first_change(numbers))


# ============================================================
# 46. SEARCHING FOR A MISSING VALUE
# ============================================================

print("\n" + "=" * 70)
print("46. SEARCHING FOR A MISSING VALUE")
print("=" * 70)

print("""
For an array containing numbers from 1 through n with one missing
value, the missing value can be identified through a search over the
expected range.

A set makes membership checking efficient.
""")


def find_missing_value(array, n):
    """
    Find the missing value from 1 through n.

    Assumes exactly one value is missing and all other values are
    distinct and within the expected range.
    """
    present = set(array)

    for value in range(1, n + 1):
        if value not in present:
            return value

    return None


numbers = [1, 2, 3, 5, 6]

print("Array:", numbers)
print("Missing value from 1..6:", find_missing_value(numbers, 6))


# ============================================================
# 47. SEARCHING FOR VALUES NOT IN A SECOND ARRAY
# ============================================================

print("\n" + "=" * 70)
print("47. SEARCHING FOR VALUES ABSENT FROM ANOTHER ARRAY")
print("=" * 70)


def values_not_in_second_array(first_array, second_array):
    """
    Return values from first_array that do not occur in second_array.

    Membership in a set gives average O(1) lookup.
    """
    second_set = set(second_array)
    result = []

    for value in first_array:
        if value not in second_set:
            result.append(value)

    return result


first = [1, 2, 3, 4, 5]
second = [2, 4, 6]

print(
    "Values only in first array:",
    values_not_in_second_array(first, second),
)


# ============================================================
# 48. SEARCHING FOR INTERSECTION
# ============================================================

print("\n" + "=" * 70)
print("48. SEARCHING FOR COMMON VALUES")
print("=" * 70)


def common_values(first_array, second_array):
    """
    Return unique values appearing in both arrays.

    Order follows the first occurrence in first_array.
    """
    second_set = set(second_array)
    found = set()
    result = []

    for value in first_array:
        if value in second_set and value not in found:
            result.append(value)
            found.add(value)

    return result


first = [1, 2, 2, 3, 4, 5]
second = [2, 4, 4, 6]

print("Common values:", common_values(first, second))


# ============================================================
# 49. SEARCHING FOR THE SECOND LARGEST DISTINCT VALUE
# ============================================================

print("\n" + "=" * 70)
print("49. SECOND LARGEST DISTINCT VALUE")
print("=" * 70)


def second_largest_distinct(array):
    """
    Find the second largest distinct value using a single scan.

    Raise ValueError when fewer than two distinct values exist.
    """
    largest = None
    second_largest = None

    for value in array:
        if largest is None or value > largest:
            if largest != value:
                second_largest = largest
                largest = value

        elif value != largest and (
            second_largest is None or value > second_largest
        ):
            second_largest = value

    if second_largest is None:
        raise ValueError(
            "At least two distinct values are required."
        )

    return second_largest


numbers = [10, 20, 20, 5, 30, 30, 25]

print("Array:", numbers)
print("Second largest distinct value:", second_largest_distinct(numbers))


# ============================================================
# 50. SEARCHING FOR TOP TWO VALUES
# ============================================================

print("\n" + "=" * 70)
print("50. TOP TWO DISTINCT VALUES")
print("=" * 70)


def top_two_distinct(array):
    """
    Return the two largest distinct values.

    Raise ValueError if fewer than two distinct values exist.
    """
    largest = None
    second = None

    for value in array:
        if value == largest or value == second:
            continue

        if largest is None or value > largest:
            second = largest
            largest = value

        elif second is None or value > second:
            second = value

    if largest is None or second is None:
        raise ValueError(
            "At least two distinct values are required."
        )

    return largest, second


numbers = [12, 4, 27, 27, 19, 8, 31]

print("Top two distinct values:", top_two_distinct(numbers))


# ============================================================
# 51. SEARCHING FOR THE FIRST VALUE MEETING MULTIPLE CONDITIONS
# ============================================================

print("\n" + "=" * 70)
print("51. MULTIPLE SEARCH CONDITIONS")
print("=" * 70)


def first_even_and_greater_than(array, threshold):
    """Find the first even value greater than threshold."""
    for index, value in enumerate(array):
        if value % 2 == 0 and value > threshold:
            return index, value

    return -1, None


numbers = [5, 12, 17, 22, 31, 40]

print(
    "First even number greater than 20:",
    first_even_and_greater_than(numbers, 20),
)


# ============================================================
# 52. SEARCHING WITH OR CONDITIONS
# ============================================================

print("\n" + "=" * 70)
print("52. SEARCHING WITH OR CONDITIONS")
print("=" * 70)


def first_negative_or_zero(array):
    """Find the first value that is negative or zero."""
    for index, value in enumerate(array):
        if value <= 0:
            return index, value

    return -1, None


numbers = [8, 5, 3, 0, -2, 7]

print(
    "First non-positive value:",
    first_negative_or_zero(numbers),
)


# ============================================================
# 53. GENERALIZED SEARCH USING A PREDICATE
# ============================================================

print("\n" + "=" * 70)
print("53. GENERALIZED SEARCH")
print("=" * 70)


def search_with_predicate(array, predicate):
    """
    General-purpose linear search.

    The predicate receives each value and decides whether it matches.
    """
    for index, value in enumerate(array):
        if predicate(value):
            return index, value

    return -1, None


numbers = [3, 7, 12, 18, 25]

print(
    "First value divisible by 6:",
    search_with_predicate(numbers, lambda x: x % 6 == 0),
)

print(
    "First value ending in 5:",
    search_with_predicate(numbers, lambda x: x % 5 == 0),
)


# ============================================================
# 54. GENERALIZED SEARCH WITH INDEX
# ============================================================

print("\n" + "=" * 70)
print("54. GENERALIZED SEARCH WITH INDEX-AWARE PREDICATE")
print("=" * 70)


def search_with_index_predicate(array, predicate):
    """
    Generalized search where predicate receives both index and value.
    """
    for index, value in enumerate(array):
        if predicate(index, value):
            return index, value

    return -1, None


numbers = [10, 20, 30, 40, 50]

print(
    "First value greater than index * 10:",
    search_with_index_predicate(
        numbers,
        lambda index, value: value > index * 10,
    ),
)

print(
    "First even-indexed value divisible by 20:",
    search_with_index_predicate(
        numbers,
        lambda index, value: index % 2 == 0 and value % 20 == 0,
    ),
)


# ============================================================
# 55. SEARCHING WITH A CUSTOM KEY
# ============================================================

print("\n" + "=" * 70)
print("55. KEY-BASED SEARCH")
print("=" * 70)


def first_by_key(array, target, key):
    """
    Search objects or values using a derived key.
    """
    target_key = key(target)

    for index, value in enumerate(array):
        if key(value) == target_key:
            return index, value

    return -1, None


students = [
    Student(1, "Asha", 82),
    Student(2, "Ravi", 91),
    Student(3, "Meera", 88),
]

target_student = Student(2, "Unknown", 0)

print(
    "Search student by roll number:",
    first_by_key(students, target_student, lambda student: student.roll_number),
)


# ============================================================
# 56. SEARCHING FOR A SUBARRAY
# ============================================================

print("\n" + "=" * 70)
print("56. SUBARRAY SEARCH")
print("=" * 70)

print("""
Searching for a complete pattern inside an array is more complex
than searching for one value.

The following direct implementation compares each possible starting
position with the entire pattern.
""")


def find_subarray(array, pattern):
    """
    Return the first starting index where pattern occurs.

    Return -1 if pattern does not occur.

    This is a straightforward comparison algorithm.
    """
    if not pattern:
        return 0

    if len(pattern) > len(array):
        return -1

    last_start = len(array) - len(pattern)

    for start in range(last_start + 1):
        match = True

        for offset in range(len(pattern)):
            if array[start + offset] != pattern[offset]:
                match = False
                break

        if match:
            return start

    return -1


numbers = [1, 3, 5, 7, 9, 3, 5]

print("Array:", numbers)
print("Pattern [7, 9, 3]:", find_subarray(numbers, [7, 9, 3]))
print("Pattern [9, 5]:", find_subarray(numbers, [9, 5]))
print("Empty pattern:", find_subarray(numbers, []))


# ============================================================
# 57. COUNTING SUBARRAY OCCURRENCES
# ============================================================

print("\n" + "=" * 70)
print("57. COUNTING SUBARRAY OCCURRENCES")
print("=" * 70)


def count_subarray_occurrences(array, pattern):
    """
    Count pattern occurrences, including overlapping occurrences.

    Example:
        array = [1, 1, 1]
        pattern = [1, 1]

    Result:
        2
    """
    if not pattern:
        return 1

    if len(pattern) > len(array):
        return 0

    count = 0

    for start in range(len(array) - len(pattern) + 1):
        if array[start:start + len(pattern)] == pattern:
            count += 1

    return count


print(
    "Occurrences of [1, 1] in [1, 1, 1]:",
    count_subarray_occurrences([1, 1, 1], [1, 1]),
)

print(
    "Occurrences of [2, 3] in [1, 2, 3, 2, 3]:",
    count_subarray_occurrences([1, 2, 3, 2, 3], [2, 3]),
)


# ============================================================
# 58. SEARCHING IN A ROTATED ARRAY WITH LINEAR SEARCH
# ============================================================

print("\n" + "=" * 70)
print("58. SEARCHING A ROTATED ARRAY")
print("=" * 70)

print("""
A rotated array such as:
    [40, 50, 60, 10, 20, 30]

is not globally sorted.

Linear search remains valid because it does not require sorted data.
""")


def linear_search_rotated(array, target):
    """Search a rotated array using ordinary linear search."""
    return linear_search(array, target)


rotated = [40, 50, 60, 10, 20, 30]

print("Rotated array:", rotated)
print("Search 20:", linear_search_rotated(rotated, 20))
print("Search 70:", linear_search_rotated(rotated, 70))


# ============================================================
# 59. LINEAR SEARCH VS BINARY SEARCH
# ============================================================

print("\n" + "=" * 70)
print("59. LINEAR SEARCH VS BINARY SEARCH")
print("=" * 70)

print("""
Linear search:
    - Works on unsorted data.
    - Simple implementation.
    - O(n) worst-case time.
    - O(1) auxiliary space.
    - Useful for small or unsorted collections.

Binary search:
    - Requires sorted data under its normal assumptions.
    - O(log n) search time.
    - More suitable for repeated searches in ordered data.
    - Maintaining sorted order can itself have a cost.

The topic here focuses on linear search because it is the fundamental
solution for arbitrary unsorted arrays.
""")


def binary_search(sorted_array, target):
    """
    Iterative binary search for a sorted array.

    Return the index of one matching occurrence, or -1.
    """
    left = 0
    right = len(sorted_array) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if sorted_array[middle] == target:
            return middle

        if sorted_array[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


sorted_numbers = [10, 20, 30, 40, 50, 60]

print("Sorted array:", sorted_numbers)
print("Binary search for 40:", binary_search(sorted_numbers, 40))


# ============================================================
# 60. FIRST AND LAST OCCURRENCE WITH LINEAR SEARCH
# ============================================================

print("\n" + "=" * 70)
print("60. RANGE OF OCCURRENCES")
print("=" * 70)


def occurrence_range(array, target):
    """
    Return (first_index, last_index).

    Return (-1, -1) if target is absent.
    """
    first = -1
    last = -1

    for index, value in enumerate(array):
        if value == target:
            if first == -1:
                first = index

            last = index

    return first, last


numbers = [2, 4, 6, 4, 8, 4, 10]

print("Array:", numbers)
print("Occurrence range for 4:", occurrence_range(numbers, 4))
print("Occurrence range for 7:", occurrence_range(numbers, 7))


# ============================================================
# 61. FIRST AND LAST MATCH IN ONE PASS
# ============================================================

print("\n" + "=" * 70)
print("61. ONE-PASS SEARCH")
print("=" * 70)

print("""
If both first and last occurrence are required, one traversal is
enough.

This is preferable to performing two independent full scans.
""")


def first_and_last_occurrence(array, target):
    """
    Find first and last occurrence in one traversal.
    """
    first = -1
    last = -1

    for index, value in enumerate(array):
        if value == target:
            if first == -1:
                first = index

            last = index

    return first, last


numbers = [1, 3, 5, 3, 7, 3, 9]

print(
    "First and last occurrence of 3:",
    first_and_last_occurrence(numbers, 3),
)


# ============================================================
# 62. SEARCHING FROM RIGHT TO LEFT
# ============================================================

print("\n" + "=" * 70)
print("62. RIGHT-TO-LEFT SEARCH")
print("=" * 70)


def reverse_linear_search(array, target):
    """
    Search from right to left.

    The first match encountered is the last occurrence in normal
    left-to-right indexing.
    """
    for index in range(len(array) - 1, -1, -1):
        if array[index] == target:
            return index

    return -1


numbers = [4, 8, 4, 9, 4, 7]

print("Array:", numbers)
print("Right-to-left search for 4:", reverse_linear_search(numbers, 4))


# ============================================================
# 63. SEARCHING FROM BOTH ENDS
# ============================================================

print("\n" + "=" * 70)
print("63. SEARCHING FROM BOTH ENDS")
print("=" * 70)

print("""
Two-ended scanning can be useful when the problem asks whether
a condition is satisfied near either boundary.

For exact-value search, it does not improve worst-case asymptotic
complexity, which remains O(n).
""")


def search_from_both_ends(array, target):
    """
    Search simultaneously from the left and right.

    Return the first matching index encountered by this two-ended
    procedure. The exact returned index depends on which side matches.
    """
    left = 0
    right = len(array) - 1

    while left <= right:
        if array[left] == target:
            return left

        if array[right] == target:
            return right

        left += 1
        right -= 1

    return -1


numbers = [1, 2, 3, 4, 5, 6, 7]

print("Search from both ends for 6:", search_from_both_ends(numbers, 6))


# ============================================================
# 64. SEARCHING WITH A MAXIMUM NUMBER OF CHECKS
# ============================================================

print("\n" + "=" * 70)
print("64. BOUNDED LINEAR SEARCH")
print("=" * 70)


def bounded_search(array, target, maximum_checks):
    """
    Search only the first maximum_checks elements.

    Return -1 if the target is not found within the allowed checks.
    """
    if maximum_checks <= 0:
        return -1

    limit = min(len(array), maximum_checks)

    for index in range(limit):
        if array[index] == target:
            return index

    return -1


numbers = [10, 20, 30, 40, 50]

print("Search 40 with 3 checks:", bounded_search(numbers, 40, 3))
print("Search 40 with 4 checks:", bounded_search(numbers, 40, 4))


# ============================================================
# 65. SEARCHING WITH A DEFAULT VALUE
# ============================================================

print("\n" + "=" * 70)
print("65. SEARCH RESULT WITH DEFAULT")
print("=" * 70)


def search_or_default(array, target, default=None):
    """
    Return the matching index or a caller-provided default.
    """
    index = linear_search(array, target)

    if index == -1:
        return default

    return index


numbers = [10, 20, 30]

print("Search 20:", search_or_default(numbers, 20))
print("Search 99:", search_or_default(numbers, 99, "not found"))


# ============================================================
# 66. SEARCHING WITH EXPLICIT ERROR HANDLING
# ============================================================

print("\n" + "=" * 70)
print("66. SEARCH RESULT AS AN EXCEPTION")
print("=" * 70)


def require_index(array, target):
    """
    Return the target index.

    Raise LookupError if the target is absent.
    """
    index = linear_search(array, target)

    if index == -1:
        raise LookupError(f"Value {target!r} was not found.")

    return index


numbers = [10, 20, 30]

print("Required index for 20:", require_index(numbers, 20))

try:
    require_index(numbers, 99)
except LookupError as error:
    print("Expected lookup error:", error)


# ============================================================
# 67. EDGE CASES
# ============================================================

print("\n" + "=" * 70)
print("67. EDGE CASES")
print("=" * 70)

print("""
Important cases:
1. Empty array
2. One-element array
3. Target at first position
4. Target at last position
5. Target absent
6. All values identical
7. Many duplicates
8. Negative values
9. Zero
10. Mixed data types when comparisons are meaningful
""")


edge_cases = [
    ("empty", [], 10),
    ("one element found", [10], 10),
    ("one element absent", [10], 20),
    ("first element", [10, 20, 30], 10),
    ("last element", [10, 20, 30], 30),
    ("absent", [10, 20, 30], 99),
    ("all duplicates", [5, 5, 5, 5], 5),
    ("negative value", [-5, -2, 0, 3], -2),
    ("zero", [-5, -2, 0, 3], 0),
]

for name, array, target in edge_cases:
    print(
        f"{name:20} -> "
        f"first={first_occurrence(array, target)}, "
        f"last={last_occurrence(array, target)}, "
        f"all={all_occurrences(array, target)}"
    )


# ============================================================
# 68. NONE AS A SEARCH TARGET
# ============================================================

print("\n" + "=" * 70)
print("68. SEARCHING FOR NONE")
print("=" * 70)

print("""
None is a legitimate Python value and may itself be the target.

A sentinel such as -1 is returned as the index, so searching for
None remains unambiguous.
""")


values = [10, None, 20, None]

print("Array:", values)
print("First None:", first_occurrence(values, None))
print("All None positions:", all_occurrences(values, None))


# ============================================================
# 69. BOOLEAN VALUES AND INTEGER VALUES
# ============================================================

print("\n" + "=" * 70)
print("69. BOOLEAN AND INTEGER COMPARISON")
print("=" * 70)

print("""
Python's bool type is a subclass of int:
    True == 1
    False == 0

Therefore a search using == can treat True and 1 as equal.

This is an important language-specific edge case.
""")


values = [0, 1, True, False, 2]

print("Array:", values)
print("Search for True:", first_occurrence(values, True))
print("Search for 1:", first_occurrence(values, 1))


# ============================================================
# 70. FLOATING-POINT SEARCH
# ============================================================

print("\n" + "=" * 70)
print("70. FLOATING-POINT SEARCH")
print("=" * 70)

print("""
Exact equality can be problematic for floating-point calculations.

For numerical tolerance-based searching, compare the absolute
difference with a chosen tolerance.
""")


def find_approximately(array, target, tolerance=1e-9):
    """
    Find the first floating-point value within tolerance of target.
    """
    if tolerance < 0:
        raise ValueError("Tolerance must be non-negative.")

    for index, value in enumerate(array):
        if abs(value - target) <= tolerance:
            return index, value

    return -1, None


values = [0.1 + 0.2, 0.5, 0.7]

print("Values:", values)
print("Exact search for 0.3:", first_occurrence(values, 0.3))
print(
    "Approximate search for 0.3:",
    find_approximately(values, 0.3, tolerance=1e-9),
)


# ============================================================
# 71. SEARCHING NAN
# ============================================================

print("\n" + "=" * 70)
print("71. SEARCHING FOR NaN")
print("=" * 70)

print("""
IEEE floating-point NaN has unusual equality behavior:
    NaN != NaN

Therefore an ordinary equality search may not find NaN even when
NaN is present.

Use math.isnan for NaN-aware searching.
""")


import math


def find_nan(array):
    """Return the first index containing a floating-point NaN."""
    for index, value in enumerate(array):
        if isinstance(value, float) and math.isnan(value):
            return index

    return -1


values = [1.0, float("nan"), 3.0]

print("NaN-aware search:", find_nan(values))


# ============================================================
# 72. SEARCHING BY TYPE
# ============================================================

print("\n" + "=" * 70)
print("72. SEARCHING BY TYPE")
print("=" * 70)


def first_instance_of(array, data_type):
    """Find the first element that is an instance of data_type."""
    for index, value in enumerate(array):
        if isinstance(value, data_type):
            return index, value

    return -1, None


values = [10, "Python", 3.14, "SQL", 42]

print("First string:", first_instance_of(values, str))
print("First float:", first_instance_of(values, float))


# ============================================================
# 73. SEARCHING DICTIONARIES IN AN ARRAY
# ============================================================

print("\n" + "=" * 70)
print("73. SEARCHING RECORDS")
print("=" * 70)


records = [
    {"id": 101, "name": "Asha", "department": "Finance"},
    {"id": 102, "name": "Ravi", "department": "Technology"},
    {"id": 103, "name": "Meera", "department": "Finance"},
]


def find_record_by_id(records, record_id):
    """Find the first dictionary record with a matching ID."""
    for index, record in enumerate(records):
        if record.get("id") == record_id:
            return index, record

    return -1, None


print("Record 102:", find_record_by_id(records, 102))
print("Record 999:", find_record_by_id(records, 999))


# ============================================================
# 74. SEARCHING RECORDS BY MULTIPLE CONDITIONS
# ============================================================


def find_finance_record(records):
    """Find the first record belonging to the Finance department."""
    return search_with_predicate(
        records,
        lambda record: record.get("department") == "Finance",
    )


print(
    "First Finance record:",
    find_finance_record(records),
)


# ============================================================
# 75. SEARCHING WITH SHORT-CIRCUITING
# ============================================================

print("\n" + "=" * 70)
print("75. SHORT-CIRCUITING")
print("=" * 70)

print("""
A search should usually stop as soon as its required answer is known.

For first occurrence:
    stop at the first match.

For existence:
    stop at the first match.

For last occurrence:
    the complete scan is normally required unless the array is
    scanned from right to left.

Stopping early is an important practical performance optimization.
""")


# ============================================================
# 76. COMPARISON COUNT
# ============================================================

print("\n" + "=" * 70)
print("76. COUNTING COMPARISONS")
print("=" * 70)


def linear_search_with_comparison_count(array, target):
    """
    Return (index, number_of_comparisons).
    """
    comparisons = 0

    for index, value in enumerate(array):
        comparisons += 1

        if value == target:
            return index, comparisons

    return -1, comparisons


numbers = [10, 20, 30, 40, 50]

print(
    "Search first element:",
    linear_search_with_comparison_count(numbers, 10),
)

print(
    "Search last element:",
    linear_search_with_comparison_count(numbers, 50),
)

print(
    "Search absent element:",
    linear_search_with_comparison_count(numbers, 99),
)


# ============================================================
# 77. BEST, AVERAGE, AND WORST CASE
# ============================================================

print("\n" + "=" * 70)
print("77. COMPLEXITY")
print("=" * 70)

print("""
For an array containing n elements:

Best case:
    O(1)
    The target is the first element.

Worst case:
    O(n)
    The target is the last element or absent.

Average case:
    O(n)
    For a uniformly distributed successful search, approximately
    (n + 1) / 2 comparisons are needed.

Space:
    O(1)
    Standard iterative linear search requires constant auxiliary space.
""")


# ============================================================
# 78. SEARCHING LARGE DATA
# ============================================================

print("\n" + "=" * 70)
print("78. PERFORMANCE CONSIDERATIONS")
print("=" * 70)

print("""
Linear search is often appropriate when:
- the collection is small
- the collection is unsorted
- searches are infrequent
- implementation simplicity matters
- data changes frequently and maintaining sorted order is expensive

Linear search becomes less attractive when:
- the collection is very large
- the same collection is searched repeatedly
- fast repeated membership queries are required
- the data can efficiently be indexed or hashed
- the data is sorted and binary search is applicable
""")


# ============================================================
# 79. SEARCHING WITH A PRECOMPUTED INDEX
# ============================================================

print("\n" + "=" * 70)
print("79. PRECOMPUTED SEARCH INDEX")
print("=" * 70)


def build_index(array):
    """
    Build a mapping from value to its first occurrence.

    Average construction time: O(n)
    Lookup after construction: O(1) average
    """
    index_map = {}

    for index, value in enumerate(array):
        if value not in index_map:
            index_map[value] = index

    return index_map


numbers = [10, 20, 10, 30, 20, 40]

index_map = build_index(numbers)

print("Array:", numbers)
print("First-occurrence index:", index_map)
print("Index of 30:", index_map.get(30))
print("Index of 99:", index_map.get(99))


# ============================================================
# 80. PRECOMPUTED ALL-OCCURRENCE INDEX
# ============================================================

print("\n" + "=" * 70)
print("80. INDEX OF ALL OCCURRENCES")
print("=" * 70)


def build_occurrence_index(array):
    """
    Build a dictionary mapping each value to all its positions.

    Average construction time: O(n)
    """
    occurrence_index = {}

    for index, value in enumerate(array):
        occurrence_index.setdefault(value, []).append(index)

    return occurrence_index


numbers = [10, 20, 10, 30, 20, 10]

occurrence_index = build_occurrence_index(numbers)

print("Occurrence index:", occurrence_index)
print("Positions of 10:", occurrence_index.get(10, []))


# ============================================================
# 81. SEARCHING MULTIPLE TARGETS
# ============================================================

print("\n" + "=" * 70)
print("81. SEARCHING FOR MULTIPLE TARGETS")
print("=" * 70)


def find_first_positions(array, targets):
    """
    Return a dictionary mapping each target to its first position.

    A target absent from the array maps to -1.
    """
    target_set = set(targets)
    result = {target: -1 for target in targets}

    for index, value in enumerate(array):
        if value in target_set and result[value] == -1:
            result[value] = index

    return result


numbers = [4, 8, 15, 16, 23, 42]

print(
    "First positions:",
    find_first_positions(numbers, [8, 23, 99]),
)


# ============================================================
# 82. SEARCHING MULTIPLE TARGETS IN ONE PASS
# ============================================================

print("\n" + "=" * 70)
print("82. ONE-PASS MULTI-TARGET SEARCH")
print("=" * 70)


def find_all_target_positions(array, targets):
    """
    Return all positions for requested targets.

    The array is traversed only once.
    """
    target_set = set(targets)
    result = {target: [] for target in targets}

    for index, value in enumerate(array):
        if value in target_set:
            result[value].append(index)

    return result


numbers = [2, 5, 2, 7, 5, 2, 9]

print(
    "Requested target positions:",
    find_all_target_positions(numbers, [2, 5, 9]),
)


# ============================================================
# 83. SEARCHING FOR THE FIRST UNIQUE VALUE
# ============================================================

print("\n" + "=" * 70)
print("83. FIRST UNIQUE VALUE")
print("=" * 70)


def first_unique(array):
    """
    Find the first value that appears exactly once.
    """
    frequencies = build_frequency_map(array)

    for index, value in enumerate(array):
        if frequencies[value] == 1:
            return index, value

    return -1, None


numbers = [2, 3, 2, 4, 3, 5, 4]

print("First unique value:", first_unique(numbers))


# ============================================================
# 84. SEARCHING FOR MAJORITY ELEMENT
# ============================================================

print("\n" + "=" * 70)
print("84. MAJORITY ELEMENT")
print("=" * 70)

print("""
A majority element appears more than n/2 times.

A frequency-map implementation makes the condition explicit.
""")


def majority_element(array):
    """
    Return the majority element if one exists.

    Return None otherwise.
    """
    if not array:
        return None

    frequencies = build_frequency_map(array)
    threshold = len(array) // 2

    for value, frequency in frequencies.items():
        if frequency > threshold:
            return value

    return None


numbers = [2, 2, 1, 2, 3, 2, 2]

print("Majority element:", majority_element(numbers))


# ============================================================
# 85. SEARCHING FOR A VALUE WITH EXACT FREQUENCY
# ============================================================

print("\n" + "=" * 70)
print("85. EXACT FREQUENCY SEARCH")
print("=" * 70)


def first_value_with_frequency(array, required_frequency):
    """
    Return the first value whose total frequency equals the requested
    frequency.
    """
    if required_frequency < 0:
        raise ValueError("Frequency cannot be negative.")

    frequencies = build_frequency_map(array)

    for index, value in enumerate(array):
        if frequencies[value] == required_frequency:
            return index, value

    return -1, None


numbers = [4, 7, 4, 8, 7, 9, 7]

print(
    "First value occurring exactly 3 times:",
    first_value_with_frequency(numbers, 3),
)


# ============================================================
# 86. SEARCHING FOR A PAIR OF INDICES WITH A DIFFERENCE
# ============================================================

print("\n" + "=" * 70)
print("86. PAIR WITH A TARGET DIFFERENCE")
print("=" * 70)


def pair_with_difference(array, difference):
    """
    Return indices i, j where:
        array[j] - array[i] == difference

    Uses a dictionary of previously seen values.
    """
    seen = {}

    for index, value in enumerate(array):
        required = value - difference

        if required in seen:
            return seen[required], index

        if value not in seen:
            seen[value] = index

    return None


numbers = [8, 1, 5, 12, 7]

print("Array:", numbers)
print("Pair with difference 4:", pair_with_difference(numbers, 4))


# ============================================================
# 87. SEARCHING FOR AN ELEMENT WITHIN DISTANCE
# ============================================================

print("\n" + "=" * 70)
print("87. SEARCHING WITH A DISTANCE CONDITION")
print("=" * 70)


def first_within_distance(array, target, maximum_distance):
    """
    Find the first value whose absolute difference from target
    is at most maximum_distance.
    """
    if maximum_distance < 0:
        raise ValueError("Maximum distance cannot be negative.")

    for index, value in enumerate(array):
        if abs(value - target) <= maximum_distance:
            return index, value

    return -1, None


numbers = [100, 120, 145, 180]

print(
    "First value within 20 of 130:",
    first_within_distance(numbers, 130, 20),
)


# ============================================================
# 88. SEARCHING FOR A PLATEAU
# ============================================================

print("\n" + "=" * 70)
print("88. SEARCHING FOR A PLATEAU")
print("=" * 70)

print("""
A plateau is a consecutive run of equal values.

This example returns the first plateau having at least a requested
length.
""")


def first_plateau(array, minimum_length):
    """
    Return (start, end, value) for the first run of equal values
    having at least minimum_length elements.
    """
    if minimum_length <= 0:
        raise ValueError("Minimum length must be positive.")

    if not array:
        return None

    start = 0

    for index in range(1, len(array) + 1):
        if index == len(array) or array[index] != array[start]:
            length = index - start

            if length >= minimum_length:
                return start, index - 1, array[start]

            start = index

    return None


numbers = [1, 1, 2, 3, 3, 3, 4, 5]

print(
    "First plateau of length >= 3:",
    first_plateau(numbers, 3),
)


# ============================================================
# 89. SEARCHING FOR CONSECUTIVE EQUAL ELEMENTS
# ============================================================

print("\n" + "=" * 70)
print("89. CONSECUTIVE DUPLICATES")
print("=" * 70)


def first_consecutive_duplicate(array):
    """
    Return the index of the second element in the first equal pair.
    """
    for index in range(1, len(array)):
        if array[index] == array[index - 1]:
            return index

    return -1


numbers = [1, 2, 3, 3, 4, 5]

print(
    "Second index of first consecutive duplicate:",
    first_consecutive_duplicate(numbers),
)


# ============================================================
# 90. SEARCHING FOR SORT ORDER VIOLATION
# ============================================================

print("\n" + "=" * 70)
print("90. SEARCHING FOR SORT ORDER VIOLATION")
print("=" * 70)


def first_ascending_violation(array):
    """
    Return the first index i where array[i] < array[i - 1].

    This identifies the first violation of non-decreasing order.
    """
    for index in range(1, len(array)):
        if array[index] < array[index - 1]:
            return index

    return -1


numbers = [10, 20, 20, 30, 25, 40]

print(
    "First ascending-order violation:",
    first_ascending_violation(numbers),
)


# ============================================================
# 91. SEARCHING FOR DESCENDING ORDER VIOLATION
# ============================================================


def first_descending_violation(array):
    """
    Return the first index i where array[i] > array[i - 1].
    """
    for index in range(1, len(array)):
        if array[index] > array[index - 1]:
            return index

    return -1


numbers = [50, 40, 30, 35, 20]

print(
    "First descending-order violation:",
    first_descending_violation(numbers),
)


# ============================================================
# 92. SEARCHING FOR THE FIRST POSITIVE NUMBER
# ============================================================

print("\n" + "=" * 70)
print("92. SIMPLE CONDITION SEARCHES")
print("=" * 70)


def first_positive(array):
    """Return the first positive number."""
    for index, value in enumerate(array):
        if value > 0:
            return index, value

    return -1, None


def first_zero(array):
    """Return the first zero."""
    for index, value in enumerate(array):
        if value == 0:
            return index, value

    return -1, None


def first_odd(array):
    """Return the first odd number."""
    for index, value in enumerate(array):
        if value % 2 != 0:
            return index, value

    return -1, None


numbers = [-5, -2, 0, 4, 7, 10]

print("First positive:", first_positive(numbers))
print("First zero:", first_zero(numbers))
print("First odd:", first_odd(numbers))


# ============================================================
# 93. SEARCHING FOR THE LAST MATCHING CONDITION
# ============================================================

print("\n" + "=" * 70)
print("93. LAST CONDITION MATCH")
print("=" * 70)


def last_positive(array):
    """Return the last positive number."""
    return last_matching(array, lambda value: value > 0)


numbers = [-5, 10, 3, -2, 8, 0]

print("Last positive:", last_positive(numbers))


# ============================================================
# 94. SEARCHING FOR THE FIRST STRING WITH A PROPERTY
# ============================================================

print("\n" + "=" * 70)
print("94. STRING CONDITION SEARCH")
print("=" * 70)


def first_long_word(words, minimum_length):
    """Find the first word having at least minimum_length characters."""
    if minimum_length < 0:
        raise ValueError("Minimum length cannot be negative.")

    for index, word in enumerate(words):
        if len(word) >= minimum_length:
            return index, word

    return -1, None


words = ["SQL", "Python", "Data", "Programming", "AI"]

print(
    "First word with at least 8 characters:",
    first_long_word(words, 8),
)


# ============================================================
# 95. SEARCHING FOR A PREFIX
# ============================================================


def first_with_prefix(words, prefix):
    """Find the first string beginning with prefix."""
    for index, word in enumerate(words):
        if word.startswith(prefix):
            return index, word

    return -1, None


words = ["apple", "banana", "application", "orange"]

print("First word beginning with 'app':",
      first_with_prefix(words, "app"))


# ============================================================
# 96. SEARCHING FOR A SUFFIX
# ============================================================


def first_with_suffix(words, suffix):
    """Find the first string ending with suffix."""
    for index, word in enumerate(words):
        if word.endswith(suffix):
            return index, word

    return -1, None


words = ["report.csv", "image.png", "data.csv", "notes.txt"]

print("First .csv file:", first_with_suffix(words, ".csv"))


# ============================================================
# 97. SEARCHING FOR AN EMPTY VALUE
# ============================================================

print("\n" + "=" * 70)
print("97. SEARCHING FOR EMPTY VALUES")
print("=" * 70)


def first_empty_string(strings):
    """Find the first empty string."""
    return first_occurrence(strings, "")


strings = ["Python", "SQL", "", "GitHub"]

print("First empty string:", first_empty_string(strings))


# ============================================================
# 98. VALIDATING SEARCH INPUT
# ============================================================

print("\n" + "=" * 70)
print("98. INPUT VALIDATION")
print("=" * 70)


def validated_linear_search(array, target):
    """
    Linear search with explicit validation.

    The function accepts list or tuple input.
    """
    if not isinstance(array, (list, tuple)):
        raise TypeError("array must be a list or tuple.")

    return linear_search(array, target)


print(
    "Validated search:",
    validated_linear_search([1, 2, 3], 2),
)

try:
    validated_linear_search("123", "2")
except TypeError as error:
    print("Expected validation error:", error)


# ============================================================
# 99. SEARCHING IMMUTABLE SEQUENCES
# ============================================================

print("\n" + "=" * 70)
print("99. SEARCHING TUPLES")
print("=" * 70)

numbers_tuple = (10, 20, 30, 20)

print(
    "Tuple:",
    numbers_tuple,
)

print(
    "First 20:",
    first_occurrence(numbers_tuple, 20),
)

print(
    "All 20 positions:",
    all_occurrences(numbers_tuple, 20),
)


# ============================================================
# 100. SEARCHING A RANGE OBJECT
# ============================================================

print("\n" + "=" * 70)
print("100. SEARCHING A RANGE")
print("=" * 70)

numbers_range = range(0, 20, 2)

print("Range:", numbers_range)
print("First occurrence of 10:", first_occurrence(numbers_range, 10))
print("First occurrence of 11:", first_occurrence(numbers_range, 11))


# ============================================================
# 101. SEARCHING WITH ENUMERATE
# ============================================================

print("\n" + "=" * 70)
print("101. ENUMERATE FOR INDEX-AWARE SEARCH")
print("=" * 70)

print("""
enumerate() is often the clearest Python mechanism when a search
needs both the index and the value.
""")


def search_using_enumerate(array, target):
    """Demonstrate idiomatic index-aware linear search."""
    for index, value in enumerate(array):
        if value == target:
            return index

    return -1


print(
    "Search using enumerate:",
    search_using_enumerate([10, 20, 30], 30),
)


# ============================================================
# 102. SEARCHING WITHOUT ENUMERATE
# ============================================================

print("\n" + "=" * 70)
print("102. INDEX-BASED LOOP")
print("=" * 70)


def search_using_index(array, target):
    """Demonstrate an explicit index-based search."""
    for index in range(len(array)):
        if array[index] == target:
            return index

    return -1


print(
    "Index-based search:",
    search_using_index([10, 20, 30], 20),
)


# ============================================================
# 103. SEARCHING WITH A WHILE LOOP
# ============================================================

print("\n" + "=" * 70)
print("103. WHILE-LOOP LINEAR SEARCH")
print("=" * 70)


def while_linear_search(array, target):
    """Linear search implemented with a while loop."""
    index = 0

    while index < len(array):
        if array[index] == target:
            return index

        index += 1

    return -1


print(
    "While-loop search:",
    while_linear_search([5, 10, 15, 20], 15),
)


# ============================================================
# 104. SEARCHING WITH A FOR-ELSE CONSTRUCT
# ============================================================

print("\n" + "=" * 70)
print("104. FOR-ELSE SEARCH")
print("=" * 70)

print("""
Python's for-else syntax can express a search cleanly.

The else block executes only when the loop finishes normally,
meaning no break occurred.
""")


def search_with_for_else(array, target):
    """Return index using Python's for-else construct."""
    for index, value in enumerate(array):
        if value == target:
            return index
    else:
        return -1


print(
    "For-else search:",
    search_with_for_else([10, 20, 30], 20),
)


# ============================================================
# 105. SEARCHING WITH NEXT
# ============================================================

print("\n" + "=" * 70)
print("105. SEARCHING WITH next()")
print("=" * 70)


def first_matching_value(array, predicate, default=None):
    """
    Return the first value satisfying predicate.

    next() stops iteration as soon as a match is found.
    """
    return next(
        (value for value in array if predicate(value)),
        default,
    )


numbers = [3, 7, 10, 15, 22]

print(
    "First even value:",
    first_matching_value(numbers, lambda x: x % 2 == 0),
)


# ============================================================
# 106. SEARCHING INDEX WITH NEXT
# ============================================================


def first_matching_index(array, predicate, default=-1):
    """
    Return the first matching index using a generator expression.
    """
    return next(
        (
            index
            for index, value in enumerate(array)
            if predicate(value)
        ),
        default,
    )


print(
    "First index of a value greater than 10:",
    first_matching_index(numbers, lambda x: x > 10),
)


# ============================================================
# 107. SEARCHING AND PRESERVING ORDER
# ============================================================

print("\n" + "=" * 70)
print("107. ORDER-PRESERVING SEARCH")
print("=" * 70)

print("""
Sets and dictionaries are useful for membership-based searching,
but search problems often require preserving the original order.

When order matters, record indexes or iterate through the original
array rather than relying only on an unordered conceptual model.
""")


# ============================================================
# 108. SEARCHING FOR UNIQUE VALUES WHILE PRESERVING ORDER
# ============================================================


def unique_values_in_order(array):
    """Return unique values in order of first appearance."""
    seen = set()
    result = []

    for value in array:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


numbers = [4, 2, 4, 7, 2, 9, 7]

print("Unique values in order:", unique_values_in_order(numbers))


# ============================================================
# 109. SEARCHING FOR THE FIRST VALUE APPEARING TWICE
# ============================================================


def first_value_appearing_twice(array):
    """
    Return the first value that reaches a count of two during scanning.
    """
    counts = {}

    for value in array:
        counts[value] = counts.get(value, 0) + 1

        if counts[value] == 2:
            return value

    return None


numbers = [5, 7, 9, 5, 7]

print(
    "First value appearing twice:",
    first_value_appearing_twice(numbers),
)


# ============================================================
# 110. SEARCHING FOR THE FIRST INDEX WITH A DUPLICATE LATER
# ============================================================


def first_index_with_duplicate_later(array):
    """
    Return the earliest index whose value occurs again later.
    """
    seen_after = set()

    for index in range(len(array) - 1, -1, -1):
        if array[index] in seen_after:
            continue

        seen_after.add(array[index])

    seen = set()

    for index, value in enumerate(array):
        if value in seen:
            return index - 1 if False else index

        if value in array[index + 1:]:
            return index

        seen.add(value)

    return -1


numbers = [10, 20, 30, 20, 40]

print(
    "First index whose value appears later:",
    first_index_with_duplicate_later(numbers),
)


# ============================================================
# 111. SEARCHING FOR A VALUE OCCURRING AT LEAST K TIMES
# ============================================================


def first_value_occurring_at_least_k_times(array, k):
    """
    Return the first value whose running count reaches k.

    This differs from checking its total frequency.
    """
    if k <= 0:
        raise ValueError("k must be positive.")

    counts = {}

    for index, value in enumerate(array):
        counts[value] = counts.get(value, 0) + 1

        if counts[value] >= k:
            return index, value

    return -1, None


numbers = [4, 2, 4, 7, 4, 2]

print(
    "First value reaching frequency 3:",
    first_value_occurring_at_least_k_times(numbers, 3),
)


# ============================================================
# 112. SEARCHING FOR THE FIRST INDEX WHERE PREFIX SUM EXCEEDS TARGET
# ============================================================

print("\n" + "=" * 70)
print("112. PREFIX-BASED SEARCH")
print("=" * 70)


def first_prefix_sum_exceeding(array, target):
    """
    Find the first index where cumulative sum becomes greater than target.
    """
    running_sum = 0

    for index, value in enumerate(array):
        running_sum += value

        if running_sum > target:
            return index, running_sum

    return -1, None


numbers = [5, 8, 10, 20]

print(
    "First prefix sum exceeding 18:",
    first_prefix_sum_exceeding(numbers, 18),
)


# ============================================================
# 113. SEARCHING FOR THE FIRST CUMULATIVE PRODUCT ABOVE TARGET
# ============================================================


def first_product_exceeding(array, target):
    """
    Find the first index where cumulative product exceeds target.

    Assumes multiplication semantics are meaningful for the values.
    """
    product = 1

    for index, value in enumerate(array):
        product *= value

        if product > target:
            return index, product

    return -1, None


numbers = [2, 3, 2, 5]

print(
    "First cumulative product exceeding 20:",
    first_product_exceeding(numbers, 20),
)


# ============================================================
# 114. SEARCHING WITH A LIMIT ON ARRAY ACCESS
# ============================================================


def search_with_limit(array, target, end_exclusive):
    """
    Search only indexes [0, end_exclusive).

    This is useful when a problem specifies a logical prefix.
    """
    if end_exclusive < 0:
        return -1

    end_exclusive = min(end_exclusive, len(array))

    for index in range(end_exclusive):
        if array[index] == target:
            return index

    return -1


numbers = [10, 20, 30, 40, 50]

print(
    "Search 40 in first four elements:",
    search_with_limit(numbers, 40, 4),
)


# ============================================================
# 115. SEARCHING A PREFIX
# ============================================================


def search_prefix(array, target, prefix_length):
    """Search only the first prefix_length elements."""
    return search_with_limit(array, target, prefix_length)


print(
    "Search 30 in prefix of length 3:",
    search_prefix(numbers, 30, 3),
)


# ============================================================
# 116. SEARCHING A SUFFIX
# ============================================================


def search_suffix(array, target, suffix_length):
    """Search only the final suffix_length elements."""
    if suffix_length <= 0:
        return -1

    start = max(0, len(array) - suffix_length)

    for index in range(start, len(array)):
        if array[index] == target:
            return index

    return -1


numbers = [10, 20, 30, 40, 50]

print(
    "Search 20 in last two elements:",
    search_suffix(numbers, 20, 2),
)

print(
    "Search 40 in last two elements:",
    search_suffix(numbers, 40, 2),
)


# ============================================================
# 117. SEARCHING WITH A STEP
# ============================================================


def search_with_step(array, target, start=0, step=1):
    """
    Search indexes start, start+step, start+2*step, ...

    Negative steps allow right-to-left traversal.
    """
    if step == 0:
        raise ValueError("step cannot be zero.")

    if not array:
        return -1

    if step > 0:
        if start < 0:
            start = 0

        if start >= len(array):
            return -1

        indexes = range(start, len(array), step)

    else:
        if start >= len(array):
            start = len(array) - 1

        if start < 0:
            return -1

        indexes = range(start, -1, step)

    for index in indexes:
        if array[index] == target:
            return index

    return -1


numbers = [10, 20, 30, 40, 50, 60]

print(
    "Search 50 at even indexes:",
    search_with_step(numbers, 50, start=0, step=2),
)

print(
    "Search 20 from right with step -2:",
    search_with_step(numbers, 20, start=5, step=-2),
)


# ============================================================
# 118. SEARCHING FOR A PAIR WITH EQUAL SUMS
# ============================================================

print("\n" + "=" * 70)
print("118. SEARCHING FOR EQUAL-SUM PAIRS")
print("=" * 70)


def equal_sum_pair(array, target):
    """
    Search for a pair summing to target.

    This is an alias-style wrapper demonstrating reuse of a tested
    searching primitive.
    """
    return two_sum_hash_set(array, target)


print(
    "Pair summing to 13:",
    equal_sum_pair([2, 4, 7, 9, 11], 13),
)


# ============================================================
# 119. SEARCHING FOR THE NEAREST PAIR SUM
# ============================================================


def closest_pair_sum(array, target):
    """
    Find two indices whose sum is closest to target.

    This direct solution checks every pair.

    Time: O(n^2)
    Space: O(1)
    """
    if len(array) < 2:
        raise ValueError("At least two elements are required.")

    best_pair = (0, 1)
    best_difference = abs(array[0] + array[1] - target)

    for first_index in range(len(array)):
        for second_index in range(first_index + 1, len(array)):
            difference = abs(
                array[first_index] + array[second_index] - target
            )

            if difference < best_difference:
                best_difference = difference
                best_pair = first_index, second_index

    return best_pair, (
        array[best_pair[0]] + array[best_pair[1]]
    )


numbers = [2, 8, 15, 21]

print(
    "Closest pair sum to 20:",
    closest_pair_sum(numbers, 20),
)


# ============================================================
# 120. TESTING SEARCH FUNCTIONS
# ============================================================

print("\n" + "=" * 70)
print("120. TESTING")
print("=" * 70)


def run_search_tests():
    """Run assertions covering normal cases and edge cases."""
    assert linear_search([1, 2, 3], 2) == 1
    assert linear_search([1, 2, 3], 9) == -1
    assert linear_search([], 1) == -1

    assert first_occurrence([1, 2, 2, 3], 2) == 1
    assert last_occurrence([1, 2, 2, 3], 2) == 2
    assert all_occurrences([1, 2, 2, 3, 2], 2) == [1, 2, 4]
    assert count_occurrences([1, 2, 2, 3, 2], 2) == 3

    assert contains_duplicate([1, 2, 3]) is False
    assert contains_duplicate([1, 2, 1]) is True

    assert first_even([1, 3, 8, 10]) == (2, 8)
    assert first_even([1, 3, 5]) == (-1, None)

    assert two_sum_hash_set([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum_hash_set([1, 2, 3], 100) is None

    assert find_subarray([1, 2, 3, 4], [2, 3]) == 1
    assert find_subarray([1, 2, 3, 4], [3, 5]) == -1

    assert search_nested_array([[1, 2], [3, 4]], 4) == (1, 1)

    assert find_approximately([0.3], 0.3) == (0, 0.3)

    assert first_prefix_sum_exceeding([5, 10, 20], 12) == (2, 35)

    print("All search tests passed.")


run_search_tests()


# ============================================================
# 121. PROPERTY-STYLE CROSS-CHECKING
# ============================================================

print("\n" + "=" * 70)
print("121. CROSS-CHECKING AGAINST PYTHON BEHAVIOR")
print("=" * 70)


def cross_check_search(array, target):
    """
    Compare our implementation with Python's list.index behavior.

    list.index raises ValueError when absent, while our function returns -1.
    """
    custom_result = linear_search(array, target)

    try:
        python_result = array.index(target)
    except ValueError:
        python_result = -1

    return custom_result == python_result


test_arrays = [
    [],
    [1],
    [1, 2, 3],
    [2, 2, 2],
    [-1, 0, 1, 2],
]

for array in test_arrays:
    for target in [-1, 0, 1, 2, 3]:
        assert cross_check_search(array, target)

print("Cross-checks passed.")


# ============================================================
# 122. SEARCHING COMPLEXITY TABLE
# ============================================================

print("\n" + "=" * 70)
print("122. COMPLEXITY REFERENCE")
print("=" * 70)

complexity_table = [
    ("Linear search", "O(1)", "O(n)", "O(n)", "O(1)"),
    ("First occurrence", "O(1)", "O(n)", "O(n)", "O(1)"),
    ("Last occurrence", "O(n)", "O(n)", "O(n)", "O(1)"),
    ("All occurrences", "O(n)", "O(n)", "O(n)", "O(k) output"),
    ("Set duplicate check", "O(1)", "O(n)", "O(n)", "O(n)"),
    ("Hash two-sum", "O(1)", "O(n)", "O(n)", "O(n)"),
    ("Binary search", "O(1)", "O(log n)", "O(log n)", "O(1)"),
]

print(
    f"{'Algorithm':25} {'Best':8} {'Average':10} "
    f"{'Worst':8} {'Space':12}"
)

for name, best, average, worst, space in complexity_table:
    print(
        f"{name:25} {best:8} {average:10} "
        f"{worst:8} {space:12}"
    )


# ============================================================
# 123. PRACTICAL SEARCHING WORKFLOW
# ============================================================

print("\n" + "=" * 70)
print("123. PRACTICAL SEARCHING WORKFLOW")
print("=" * 70)

print("""
When solving a searching problem:

1. Identify exactly what must be returned.
   - Boolean?
   - Index?
   - Value?
   - All indexes?
   - Count?
   - Pair?
   - Range?

2. Determine whether the array is sorted.
   - Unsorted -> linear search is a natural choice.
   - Sorted -> binary search or another ordered technique may be better.

3. Identify duplicate behavior.
   - First occurrence?
   - Last occurrence?
   - Every occurrence?
   - Unique values?

4. Identify the condition.
   - Exact equality?
   - Greater than?
   - Even?
   - Range?
   - Custom property?

5. Decide whether early termination is possible.

6. Consider whether repeated searches justify an index structure.

7. Handle empty input and absent targets explicitly.

8. Analyze time and auxiliary-space complexity.

9. Test boundary cases.
""")


# ============================================================
# 124. COMMON MISTAKES
# ============================================================

print("\n" + "=" * 70)
print("124. COMMON MISTAKES")
print("=" * 70)

print("""
Common mistakes in array searching:

1. Forgetting that indexes begin at zero.
2. Returning the value when the problem asks for the index.
3. Returning the first occurrence when the last occurrence is required.
4. Stopping too early when all occurrences are required.
5. Forgetting the target-absent case.
6. Accessing array[index + 1] at the final index.
7. Assuming the array is sorted when it is not.
8. Using O(n^2) nested loops when a set or dictionary can reduce the
   problem to O(n) average time.
9. Using exact floating-point equality when tolerance is required.
10. Ignoring special values such as NaN.
11. Mutating the original array unnecessarily.
12. Using recursion for very large arrays in Python.
13. Building an index without considering the memory cost.
14. Ignoring whether duplicate values must be preserved.
""")


# ============================================================
# 125. PRODUCTION CONSIDERATIONS
# ============================================================

print("\n" + "=" * 70)
print("125. PRODUCTION CONSIDERATIONS")
print("=" * 70)

print("""
For production code:

- Define the expected input type.
- Decide how absence is represented.
- Validate parameters where invalid values could cause ambiguity.
- Prefer clear iteration over clever micro-optimizations.
- Use an index or dictionary when repeated lookups justify the memory.
- Preserve ordering when the business requirement depends on it.
- Avoid modifying caller-owned arrays unless mutation is explicitly
  part of the API contract.
- Document duplicate behavior.
- Test empty arrays and boundary positions.
- Measure performance on realistic data before optimizing.
- For external or untrusted data, validate values before performing
  operations that assume a particular type or structure.
""")


# ============================================================
# 126. FINAL INTEGRATED SEARCH EXAMPLE
# ============================================================

print("\n" + "=" * 70)
print("126. INTEGRATED SEARCH EXAMPLE")
print("=" * 70)


def analyze_target(array, target):
    """
    Produce a complete search analysis for one target.

    Returned fields:
        exists
        first_index
        last_index
        positions
        count
    """
    first = -1
    last = -1
    positions = []

    for index, value in enumerate(array):
        if value == target:
            if first == -1:
                first = index

            last = index
            positions.append(index)

    return {
        "exists": first != -1,
        "first_index": first,
        "last_index": last,
        "positions": positions,
        "count": len(positions),
    }


numbers = [12, 7, 4, 7, 9, 7, 2, 4]

print("Array:", numbers)
print("Analysis for target 7:")
print(analyze_target(numbers, 7))

print("\nAnalysis for absent target 100:")
print(analyze_target(numbers, 100))


# ============================================================
# 127. FINAL DEMONSTRATION
# ============================================================

print("\n" + "=" * 70)
print("127. FINAL DEMONSTRATION")
print("=" * 70)

demo_array = [15, 8, 22, 8, 31, 8, 4, 19]

print("Input array:", demo_array)
print("Target: 8")
print("First occurrence:", first_occurrence(demo_array, 8))
print("Last occurrence:", last_occurrence(demo_array, 8))
print("All occurrences:", all_occurrences(demo_array, 8))
print("Count:", count_occurrences(demo_array, 8))
print("Contains duplicate:", contains_duplicate(demo_array))
print(
    "First value greater than 20:",
    first_greater_than(demo_array, 20),
)
print(
    "First even value:",
    first_even(demo_array),
)
print(
    "Maximum:",
    find_maximum(demo_array),
)
print(
    "Minimum:",
    find_minimum(demo_array),
)
print(
    "First non-repeating value:",
    first_non_repeating(demo_array),
)

print("\n" + "=" * 70)
print("END OF ARRAY SEARCHING STUDY SCRIPT")
print("=" * 70)
