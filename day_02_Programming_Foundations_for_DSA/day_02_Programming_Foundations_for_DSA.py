"""
PROGRAMMING FOUNDATIONS FOR DATA STRUCTURES AND ALGORITHMS (DSA)

This script explains and demonstrates the programming foundations required
before studying Data Structures and Algorithms in depth.

The focus is on understanding how programs work, how data is represented,
how control flows through a program, how functions communicate, how memory
is conceptually used, and how to write programs in a way that supports
algorithmic thinking.

The script covers:

1. Programming and algorithmic thinking
2. Variables and memory concepts
3. Data types
4. Operators and expressions
5. Input and output
6. Conditional statements
7. Loops and iteration
8. Functions
9. Scope and variable lifetime
10. Recursion
11. Strings
12. Lists and mutable sequences
13. Tuples and immutability
14. Sets
15. Dictionaries and key-value mapping
16. References, objects, mutability, and copying
17. Basic error handling
18. Debugging and tracing
19. Complexity foundations
20. Searching foundations
21. Sorting foundations
22. Problem decomposition
23. Edge cases
24. Invariants
25. State changes
26. Common programming mistakes in DSA
27. Writing DSA-oriented programs
"""

# ============================================================
# 1. PROGRAMMING AND ALGORITHMIC THINKING
# ============================================================

print("\n" + "=" * 70)
print("1. PROGRAMMING AND ALGORITHMIC THINKING")
print("=" * 70)

"""
Programming is the process of expressing instructions in a precise form
that a computer can execute.

An algorithm is a finite sequence of well-defined steps used to solve
a problem.

A program is often an implementation of one or more algorithms.

Example problem:

Find the largest number in a collection.

Informal algorithm:

1. Assume the first number is the largest.
2. Compare every remaining number with the current largest.
3. If a larger number is found, update the largest.
4. Return the final largest number.
"""

numbers = [14, 7, 29, 3, 18, 42, 11]

largest = numbers[0]

for number in numbers[1:]:
    if number > largest:
        largest = number

print("Numbers:", numbers)
print("Largest:", largest)


# ============================================================
# 2. VARIABLES AND MEMORY CONCEPTS
# ============================================================

print("\n" + "=" * 70)
print("2. VARIABLES AND MEMORY CONCEPTS")
print("=" * 70)

"""
A variable is a name associated with a value.

In Python, variables are names that refer to objects.

Example:

x = 10

The name x refers to an integer object representing 10.

Later:

x = 20

Now x refers to another integer object representing 20.

Variables are therefore useful for representing program state.
"""

score = 10
print("Initial score:", score)

score = score + 5
print("Updated score:", score)


"""
Assignment evaluates the expression on the right-hand side first,
then associates the result with the name on the left-hand side.
"""

x = 5
x = x + 1

print("x after x = x + 1:", x)


# ============================================================
# 3. DATA TYPES
# ============================================================

print("\n" + "=" * 70)
print("3. DATA TYPES")
print("=" * 70)

"""
A data type determines the nature of a value and the operations that
can be meaningfully performed on it.

Common Python data types:

int     -> integers
float   -> decimal numbers
bool    -> True or False
str     -> text
list    -> ordered mutable collection
tuple   -> ordered immutable collection
set     -> collection of unique elements
dict    -> key-value mapping
None    -> absence of a meaningful value
"""

integer_value = 25
float_value = 3.14
boolean_value = True
string_value = "DSA"
none_value = None

print(type(integer_value))
print(type(float_value))
print(type(boolean_value))
print(type(string_value))
print(type(none_value))


# ============================================================
# 4. OPERATORS AND EXPRESSIONS
# ============================================================

print("\n" + "=" * 70)
print("4. OPERATORS AND EXPRESSIONS")
print("=" * 70)

"""
Operators perform operations on values.

Arithmetic operators:

+ addition
- subtraction
* multiplication
/ division
// floor division
% remainder
** exponentiation
"""

a = 17
b = 5

print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
print("Floor division:", a // b)
print("Remainder:", a % b)
print("Exponentiation:", a ** b)


"""
Comparison operators produce Boolean values.

== equal to
!= not equal to
> greater than
< less than
>= greater than or equal to
<= less than or equal to
"""

print("17 > 5:", a > b)
print("17 == 5:", a == b)
print("17 != 5:", a != b)


"""
Logical operators combine Boolean expressions.

and
or
not
"""

age = 22
has_id = True

can_enter = age >= 18 and has_id

print("Can enter:", can_enter)


# ============================================================
# 5. INPUT AND OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("5. INPUT AND OUTPUT")
print("=" * 70)

"""
Output communicates information from a program.

Python commonly uses print().
"""

name = "Student"

print("Name:", name)


"""
Input allows external data to enter a program.

Example:

user_number = int(input("Enter a number: "))

For automated demonstrations, input statements are not executed here.
"""


# ============================================================
# 6. CONDITIONAL STATEMENTS
# ============================================================

print("\n" + "=" * 70)
print("6. CONDITIONAL STATEMENTS")
print("=" * 70)

"""
Conditional statements allow a program to select between different
execution paths.

Basic structure:

if condition:
    execute this block

elif another_condition:
    execute this block

else:
    execute this block
"""

number = -8

if number > 0:
    print(number, "is positive")
elif number < 0:
    print(number, "is negative")
else:
    print(number, "is zero")


"""
Nested conditions are possible, but deeply nested code can become difficult
to understand and debug.
"""

value = 12

if value > 0:
    if value % 2 == 0:
        print(value, "is a positive even number")
    else:
        print(value, "is a positive odd number")


# ============================================================
# 7. LOOPS AND ITERATION
# ============================================================

print("\n" + "=" * 70)
print("7. LOOPS AND ITERATION")
print("=" * 70)

"""
Loops repeat operations.

The two major loop styles in Python are:

for loops
while loops
"""


# ------------------------------------------------------------
# FOR LOOP
# ------------------------------------------------------------

print("\nFOR LOOP:")

for i in range(5):
    print("Iteration:", i)


"""
range(5) produces values:

0, 1, 2, 3, 4

This zero-based indexing convention is important in DSA.
"""


# ------------------------------------------------------------
# WHILE LOOP
# ------------------------------------------------------------

print("\nWHILE LOOP:")

count = 0

while count < 5:
    print("Count:", count)
    count += 1


"""
A while loop is particularly useful when the number of iterations is
determined dynamically.

Examples in DSA include:

- traversing linked structures
- binary search
- two-pointer algorithms
- repeatedly reducing a problem
"""


# ============================================================
# 8. LOOP CONTROL STATEMENTS
# ============================================================

print("\n" + "=" * 70)
print("8. LOOP CONTROL STATEMENTS")
print("=" * 70)

"""
break

Immediately terminates the nearest loop.
"""

values = [4, 7, 11, 15, 20]

for value in values:
    if value == 11:
        print("Found:", value)
        break


"""
continue

Skips the current iteration.
"""

for value in range(1, 8):
    if value % 2 == 0:
        continue

    print("Odd value:", value)


# ============================================================
# 9. FUNCTIONS
# ============================================================

print("\n" + "=" * 70)
print("9. FUNCTIONS")
print("=" * 70)

"""
A function is a reusable unit of logic.

Functions improve:

- readability
- modularity
- reuse
- testing
- debugging

A DSA solution is often easiest to understand when complex logic is
divided into small functions.
"""


def add(x, y):
    return x + y


result = add(10, 20)

print("Function result:", result)


"""
Parameters are variables defined in the function definition.

Arguments are values supplied when the function is called.
"""


def multiply(first, second):
    return first * second


print(multiply(4, 6))


# ============================================================
# 10. RETURN VALUES
# ============================================================

print("\n" + "=" * 70)
print("10. RETURN VALUES")
print("=" * 70)

"""
A return statement sends a value back to the caller.

Functions that do not explicitly return a value return None.
"""


def maximum(x, y):
    if x > y:
        return x
    return y


print("Maximum:", maximum(14, 9))


def display_message():
    print("This function prints but does not explicitly return.")


returned_value = display_message()

print("Returned value:", returned_value)


# ============================================================
# 11. SCOPE
# ============================================================

print("\n" + "=" * 70)
print("11. VARIABLE SCOPE")
print("=" * 70)

"""
Scope determines where a variable name can be accessed.

Local variables exist inside functions.
"""


def demonstrate_scope():
    local_value = 100
    print("Local value:", local_value)


demonstrate_scope()


"""
Global variables are defined outside functions.

They can be accessed inside functions, but unnecessary modification of
global state can make programs harder to reason about.
"""

global_value = 50


def read_global():
    print("Global value:", global_value)


read_global()


# ============================================================
# 12. RECURSION
# ============================================================

print("\n" + "=" * 70)
print("12. RECURSION")
print("=" * 70)

"""
Recursion occurs when a function calls itself.

A recursive solution requires:

1. Base case
2. Recursive case

The base case stops further recursive calls.
The recursive case reduces the problem toward the base case.
"""


def factorial(n):
    if n == 0:
        return 1

    return n * factorial(n - 1)


print("Factorial of 5:", factorial(5))


"""
factorial(5)

5 * factorial(4)
5 * 4 * factorial(3)
5 * 4 * 3 * factorial(2)
5 * 4 * 3 * 2 * factorial(1)
5 * 4 * 3 * 2 * 1 * factorial(0)
"""


# ============================================================
# 13. RECURSION AND CALL STACK CONCEPTS
# ============================================================

print("\n" + "=" * 70)
print("13. RECURSION AND CALL STACK CONCEPTS")
print("=" * 70)

"""
Each function call creates an execution context.

During recursion, multiple calls may remain active simultaneously.

Conceptually:

recursive_function(3)
    recursive_function(2)
        recursive_function(1)
            recursive_function(0)

The calls return in reverse order.

This behavior is closely related to the stack data structure.
"""


def count_down(n):
    if n == 0:
        print("Finished")
        return

    print(n)
    count_down(n - 1)


count_down(5)


# ============================================================
# 14. STRINGS
# ============================================================

print("\n" + "=" * 70)
print("14. STRINGS")
print("=" * 70)

"""
A string is an ordered sequence of characters.

Strings are immutable.

This means individual characters cannot be changed directly.
"""

text = "algorithm"

print("First character:", text[0])
print("Last character:", text[-1])
print("Length:", len(text))


"""
String slicing:

text[start:end]

The end position is excluded.
"""

print("First four characters:", text[0:4])


"""
Common DSA string operations include:

- traversal
- character comparison
- frequency counting
- reversal
- substring analysis
"""


for character in text:
    print(character)


# ============================================================
# 15. LISTS
# ============================================================

print("\n" + "=" * 70)
print("15. LISTS")
print("=" * 70)

"""
A list is an ordered mutable collection.

Lists support:

- indexing
- iteration
- modification
- appending
- removal

Lists are commonly used to represent arrays in Python.
"""

array = [10, 20, 30, 40]

print("Array:", array)
print("First element:", array[0])

array[1] = 25

print("Modified array:", array)


array.append(50)

print("After append:", array)


"""
Important distinction:

Index refers to a position.

Value refers to the data stored at that position.
"""

for index in range(len(array)):
    print("Index:", index, "Value:", array[index])


# ============================================================
# 16. LIST TRAVERSAL
# ============================================================

print("\n" + "=" * 70)
print("16. LIST TRAVERSAL")
print("=" * 70)

"""
Traversal means visiting elements of a collection.
"""


numbers = [3, 6, 9, 12]

for number in numbers:
    print("Value:", number)


"""
Index-based traversal is useful when positions matter.
"""

for index in range(len(numbers)):
    print(index, numbers[index])


# ============================================================
# 17. TUPLES
# ============================================================

print("\n" + "=" * 70)
print("17. TUPLES")
print("=" * 70)

"""
Tuples are ordered collections similar to lists.

The primary difference is immutability.
"""

coordinates = (10, 20)

print("Coordinates:", coordinates)


"""
Tuple unpacking:
"""

x_coordinate, y_coordinate = coordinates

print("X:", x_coordinate)
print("Y:", y_coordinate)


# ============================================================
# 18. SETS
# ============================================================

print("\n" + "=" * 70)
print("18. SETS")
print("=" * 70)

"""
A set stores unique values.

Sets are useful for:

- removing duplicates
- membership testing
- mathematical set operations
"""

values = [1, 2, 2, 3, 3, 3, 4]

unique_values = set(values)

print("Original values:", values)
print("Unique values:", unique_values)


"""
Membership testing is conceptually one of the important applications
of sets.
"""

target = 3

if target in unique_values:
    print(target, "exists in the set")


# ============================================================
# 19. DICTIONARIES
# ============================================================

print("\n" + "=" * 70)
print("19. DICTIONARIES")
print("=" * 70)

"""
A dictionary maps keys to values.

Dictionaries are fundamental in DSA for:

- frequency counting
- indexing
- caching
- lookup tables
- graph representations
"""


student = {
    "name": "Alex",
    "score": 92
}

print(student)
print("Name:", student["name"])


"""
Frequency counting is a particularly important DSA technique.
"""

data = [1, 2, 1, 3, 2, 1]

frequency = {}

for value in data:
    if value not in frequency:
        frequency[value] = 0

    frequency[value] += 1


print("Frequency map:", frequency)


# ============================================================
# 20. MUTABILITY
# ============================================================

print("\n" + "=" * 70)
print("20. MUTABILITY")
print("=" * 70)

"""
Mutable objects can be changed after creation.

Examples:

list
set
dictionary

Immutable objects include:

int
float
bool
str
tuple
"""


numbers = [1, 2, 3]

numbers.append(4)

print("Mutable list:", numbers)


text = "hello"

text = text + " world"

print("New string value:", text)


# ============================================================
# 21. REFERENCES AND ALIASING
# ============================================================

print("\n" + "=" * 70)
print("21. REFERENCES AND ALIASING")
print("=" * 70)

"""
Two variables can refer to the same mutable object.
"""

first = [1, 2, 3]
second = first

second.append(4)

print("First:", first)
print("Second:", second)


"""
Both names refer to the same list.

This is called aliasing.

Aliasing can produce unexpected behavior in algorithms when collections
are modified unintentionally.
"""


# ============================================================
# 22. COPYING
# ============================================================

print("\n" + "=" * 70)
print("22. COPYING")
print("=" * 70)

"""
A shallow copy creates a new outer object.
"""

original = [1, 2, 3]
copied = original.copy()

copied.append(4)

print("Original:", original)
print("Copied:", copied)


# ============================================================
# 23. BASIC ERROR HANDLING
# ============================================================

print("\n" + "=" * 70)
print("23. BASIC ERROR HANDLING")
print("=" * 70)

"""
Programs can fail when unexpected conditions occur.

Examples:

- invalid indexing
- division by zero
- invalid type conversion
- missing dictionary keys
"""


try:
    value = 10 / 0
except ZeroDivisionError:
    print("Division by zero is not allowed.")


# ============================================================
# 24. DEBUGGING THROUGH TRACE TABLES
# ============================================================

print("\n" + "=" * 70)
print("24. DEBUGGING THROUGH TRACE TABLES")
print("=" * 70)

"""
Tracing means manually following how variables change.

Example algorithm:

sum all values in a list.
"""

numbers = [2, 4, 6, 8]

total = 0

for value in numbers:
    total += value
    print("Current value:", value, "Running total:", total)


"""
Trace reasoning:

Before loop:
total = 0

After processing 2:
total = 2

After processing 4:
total = 6

After processing 6:
total = 12

After processing 8:
total = 20
"""


# ============================================================
# 25. STATE
# ============================================================

print("\n" + "=" * 70)
print("25. PROGRAM STATE")
print("=" * 70)

"""
State represents the current values of relevant variables.

Algorithms often maintain state.

Examples:

current maximum
current minimum
running sum
current index
left pointer
right pointer
visited elements
"""


values = [8, 3, 14, 6, 20]

current_maximum = values[0]

for value in values[1:]:
    if value > current_maximum:
        current_maximum = value

print("Maximum:", current_maximum)


# ============================================================
# 26. ACCUMULATOR PATTERN
# ============================================================

print("\n" + "=" * 70)
print("26. ACCUMULATOR PATTERN")
print("=" * 70)

"""
An accumulator stores progressively updated information.

Common accumulators include:

sum
count
maximum
minimum
frequency
"""


numbers = [5, 10, 15, 20]

total = 0
count = 0

for number in numbers:
    total += number
    count += 1

average = total / count

print("Total:", total)
print("Count:", count)
print("Average:", average)


# ============================================================
# 27. SEARCHING FOUNDATIONS
# ============================================================

print("\n" + "=" * 70)
print("27. SEARCHING FOUNDATIONS")
print("=" * 70)

"""
Searching determines whether a target exists and, in many cases,
where it exists.

The simplest approach is linear search.
"""


def linear_search(data, target):

    for index in range(len(data)):

        if data[index] == target:
            return index

    return -1


data = [12, 7, 19, 4, 25]

target = 19

index = linear_search(data, target)

print("Target index:", index)


# ============================================================
# 28. BINARY SEARCH FOUNDATION
# ============================================================

print("\n" + "=" * 70)
print("28. BINARY SEARCH FOUNDATION")
print("=" * 70)

"""
Binary search works on sorted data.

It repeatedly reduces the search space.
"""


def binary_search(data, target):

    left = 0
    right = len(data) - 1

    while left <= right:

        middle = (left + right) // 2

        if data[middle] == target:
            return middle

        elif data[middle] < target:
            left = middle + 1

        else:
            right = middle - 1

    return -1


sorted_data = [2, 5, 8, 11, 14, 18, 23, 27]

print("Binary search result:", binary_search(sorted_data, 18))


# ============================================================
# 29. SORTING FOUNDATIONS
# ============================================================

print("\n" + "=" * 70)
print("29. SORTING FOUNDATIONS")
print("=" * 70)

"""
Sorting arranges data according to an ordering rule.

Understanding basic sorting algorithms is useful because they demonstrate:

- nested loops
- comparisons
- swaps
- shrinking problem regions
"""


def bubble_sort(data):

    result = data.copy()

    n = len(result)

    for i in range(n):

        for j in range(0, n - i - 1):

            if result[j] > result[j + 1]:

                result[j], result[j + 1] = (
                    result[j + 1],
                    result[j]
                )

    return result


unsorted = [8, 3, 1, 7, 0, 10, 2]

print("Sorted:", bubble_sort(unsorted))


# ============================================================
# 30. NESTED LOOPS
# ============================================================

print("\n" + "=" * 70)
print("30. NESTED LOOPS")
print("=" * 70)

"""
A nested loop contains another loop.

Nested loops are frequently encountered when:

- comparing pairs
- processing matrices
- brute-force searching
- sorting
"""


values = [1, 2, 3]

for i in range(len(values)):
    for j in range(len(values)):
        print("Pair:", values[i], values[j])


# ============================================================
# 31. BASIC COMPLEXITY CONCEPTS
# ============================================================

print("\n" + "=" * 70)
print("31. BASIC COMPLEXITY CONCEPTS")
print("=" * 70)

"""
Time complexity describes how the amount of computational work grows
as input size grows.

Common patterns:

O(1)     constant
O(log n) logarithmic
O(n)     linear
O(n log n)
O(n^2)   quadratic
O(2^n)   exponential
"""


def constant_example(data):

    if len(data) == 0:
        return None

    return data[0]


def linear_example(data):

    total = 0

    for value in data:
        total += value

    return total


def quadratic_example(data):

    count = 0

    for first in data:
        for second in data:
            count += 1

    return count


# ============================================================
# 32. SPACE COMPLEXITY FOUNDATION
# ============================================================

print("\n" + "=" * 70)
print("32. SPACE COMPLEXITY FOUNDATION")
print("=" * 70)

"""
Space complexity concerns additional memory used by an algorithm.

Example:

An algorithm that stores another list proportional to input size
may require O(n) additional space.
"""


def create_squares(data):

    result = []

    for value in data:
        result.append(value * value)

    return result


print(create_squares([1, 2, 3, 4]))


# ============================================================
# 33. PROBLEM DECOMPOSITION
# ============================================================

print("\n" + "=" * 70)
print("33. PROBLEM DECOMPOSITION")
print("=" * 70)

"""
Complex problems are easier to solve when divided into smaller tasks.

Example problem:

Determine whether a list contains duplicate values.

Possible decomposition:

1. Inspect each value.
2. Remember previously seen values.
3. If a value has already been seen, return True.
4. Otherwise record it.
5. Return False after processing all values.
"""


def contains_duplicate(data):

    seen = set()

    for value in data:

        if value in seen:
            return True

        seen.add(value)

    return False


print("Contains duplicate:", contains_duplicate([1, 2, 3, 2]))


# ============================================================
# 34. EDGE CASES
# ============================================================

print("\n" + "=" * 70)
print("34. EDGE CASES")
print("=" * 70)

"""
An edge case is an unusual or boundary input that can expose errors.

Common DSA edge cases:

- empty collection
- single element
- duplicate elements
- negative values
- already sorted input
- reverse sorted input
- very large values
"""


def find_maximum(data):

    if len(data) == 0:
        return None

    maximum_value = data[0]

    for value in data[1:]:

        if value > maximum_value:
            maximum_value = value

    return maximum_value


print(find_maximum([]))
print(find_maximum([7]))
print(find_maximum([3, 9, 2, 15]))


# ============================================================
# 35. INVARIANTS
# ============================================================

print("\n" + "=" * 70)
print("35. ALGORITHM INVARIANTS")
print("=" * 70)

"""
An invariant is a condition that remains true at a particular stage
of an algorithm.

Example:

During maximum search:

After processing the first k elements,
current_maximum is the largest among those k elements.
"""

values = [4, 9, 2, 15, 7]

current_maximum = values[0]

for value in values[1:]:

    if value > current_maximum:
        current_maximum = value

    print("Invariant state: maximum seen so far =", current_maximum)


# ============================================================
# 36. TWO-POINTER THINKING
# ============================================================

print("\n" + "=" * 70)
print("36. TWO-POINTER THINKING")
print("=" * 70)

"""
Two-pointer algorithms maintain two positions in a sequence.

Pointers may:

- move toward each other
- move in the same direction
- represent boundaries of a range
"""


def reverse_list(data):

    result = data.copy()

    left = 0
    right = len(result) - 1

    while left < right:

        result[left], result[right] = (
            result[right],
            result[left]
        )

        left += 1
        right -= 1

    return result


print(reverse_list([1, 2, 3, 4, 5]))


# ============================================================
# 37. FREQUENCY-BASED THINKING
# ============================================================

print("\n" + "=" * 70)
print("37. FREQUENCY-BASED THINKING")
print("=" * 70)

"""
Many DSA problems can be simplified by counting occurrences.
"""


def character_frequency(text):

    frequency = {}

    for character in text:

        if character not in frequency:
            frequency[character] = 0

        frequency[character] += 1

    return frequency


print(character_frequency("programming"))


# ============================================================
# 38. FUNCTIONAL CORRECTNESS
# ============================================================

print("\n" + "=" * 70)
print("38. FUNCTIONAL CORRECTNESS")
print("=" * 70)

"""
A correct algorithm should produce the expected output for valid inputs.

A useful reasoning structure is:

Input
Process
Output

For every function, identify:

1. What inputs are expected?
2. What assumptions are made?
3. How does state change?
4. What output is guaranteed?
"""


def sum_of_even_numbers(data):

    total = 0

    for value in data:

        if value % 2 == 0:
            total += value

    return total


print(sum_of_even_numbers([1, 2, 3, 4, 5, 6]))


# ============================================================
# 39. COMMON DSA PROGRAMMING MISTAKES
# ============================================================

print("\n" + "=" * 70)
print("39. COMMON DSA PROGRAMMING MISTAKES")
print("=" * 70)

"""
Common mistakes include:

1. Off-by-one errors
2. Incorrect loop boundaries
3. Modifying collections unexpectedly
4. Forgetting base cases in recursion
5. Ignoring empty input
6. Confusing indexes and values
7. Incorrect pointer movement
8. Returning too early
9. Updating state in the wrong order
10. Forgetting duplicate cases
"""


# Off-by-one example demonstration

data = [10, 20, 30]

for index in range(len(data)):
    print("Valid index:", index)


# ============================================================
# 40. DSA-ORIENTED PROGRAM DESIGN
# ============================================================

print("\n" + "=" * 70)
print("40. DSA-ORIENTED PROGRAM DESIGN")
print("=" * 70)

"""
A disciplined approach to solving DSA problems:

1. Understand the input.
2. Understand the required output.
3. Identify constraints.
4. Write examples manually.
5. Identify the simplest correct solution.
6. Trace the solution.
7. Identify repeated operations.
8. Estimate time complexity.
9. Estimate additional space usage.
10. Test edge cases.
"""


def find_second_largest(data):

    """
    Returns the second distinct largest value.

    Returns None if fewer than two distinct values exist.
    """

    unique_values = set(data)

    if len(unique_values) < 2:
        return None

    largest = None
    second_largest = None

    for value in unique_values:

        if largest is None or value > largest:

            second_largest = largest
            largest = value

        elif value != largest and (
            second_largest is None or value > second_largest
        ):

            second_largest = value

    return second_largest


print(
    "Second largest:",
    find_second_largest([10, 4, 15, 7, 15, 12])
)


# ============================================================
# 41. COMBINING PROGRAMMING FOUNDATIONS
# ============================================================

print("\n" + "=" * 70)
print("41. COMBINING PROGRAMMING FOUNDATIONS")
print("=" * 70)

"""
This example combines:

- functions
- lists
- loops
- dictionaries
- conditions
- state
- edge-case handling
"""


def analyze_numbers(data):

    if len(data) == 0:
        return {
            "count": 0,
            "sum": 0,
            "minimum": None,
            "maximum": None,
            "even_count": 0,
            "odd_count": 0
        }

    total = 0
    minimum_value = data[0]
    maximum_value = data[0]

    even_count = 0
    odd_count = 0

    for value in data:

        total += value

        if value < minimum_value:
            minimum_value = value

        if value > maximum_value:
            maximum_value = value

        if value % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    return {
        "count": len(data),
        "sum": total,
        "minimum": minimum_value,
        "maximum": maximum_value,
        "even_count": even_count,
        "odd_count": odd_count
    }


analysis = analyze_numbers([5, 12, 7, 20, 3, 8])

for key, value in analysis.items():
    print(key, ":", value)


# ============================================================
# 42. PROGRAM EXECUTION AS A SEQUENCE OF STATE TRANSITIONS
# ============================================================

print("\n" + "=" * 70)
print("42. PROGRAM EXECUTION AS STATE TRANSITIONS")
print("=" * 70)

"""
A useful DSA mindset is to view an algorithm as a sequence of state changes.

Example:

data = [3, 1, 4]

state initially:

index = 0
sum = 0

After processing 3:

index = 1
sum = 3

After processing 1:

index = 2
sum = 4

After processing 4:

index = 3
sum = 8

Many algorithms can be understood by carefully tracking state variables.
"""


def demonstrate_state_transitions(data):

    total = 0

    for index, value in enumerate(data):

        total += value

        print(
            "Index:",
            index,
            "| Value:",
            value,
            "| Total:",
            total
        )


demonstrate_state_transitions([3, 1, 4])


# ============================================================
# 43. CAREFUL USE OF BUILT-IN OPERATIONS
# ============================================================

print("\n" + "=" * 70)
print("43. CAREFUL USE OF BUILT-IN OPERATIONS")
print("=" * 70)

"""
Python provides convenient built-in operations.

Examples:

len()
sum()
min()
max()
sorted()

For DSA learning, it is useful to understand the underlying algorithmic
idea before relying entirely on built-in functionality.
"""

data = [8, 2, 14, 5]

print("Length:", len(data))
print("Sum:", sum(data))
print("Minimum:", min(data))
print("Maximum:", max(data))
print("Sorted:", sorted(data))


# ============================================================
# 44. READING AND REASONING ABOUT CODE
# ============================================================

print("\n" + "=" * 70)
print("44. READING AND REASONING ABOUT CODE")
print("=" * 70)

"""
To understand unfamiliar DSA code:

1. Identify the input.
2. Identify important variables.
3. Determine initial values.
4. Trace loop conditions.
5. Observe state updates.
6. Identify stopping conditions.
7. Determine the returned result.
"""


def mystery(data):

    result = []

    for value in data:

        if value not in result:
            result.append(value)

    return result


print("Result:", mystery([1, 2, 1, 3, 2, 4]))


"""
The function removes duplicates while preserving the first occurrence order.

Notice that understanding the code requires observing:

- initialization
- membership testing
- conditional execution
- mutation
- return value
"""


# ============================================================
# 45. FOUNDATIONAL PROBLEM-SOLVING PATTERNS
# ============================================================

print("\n" + "=" * 70)
print("45. FOUNDATIONAL PROBLEM-SOLVING PATTERNS")
print("=" * 70)

"""
Several patterns repeatedly appear in DSA:

Traversal
    Visit each element.

Accumulation
    Build a result progressively.

Counting
    Track occurrences.

Searching
    Locate a target.

Comparison
    Determine relationships between values.

Two pointers
    Maintain two positions.

Frequency mapping
    Associate values with occurrence counts.

Recursion
    Solve a problem through smaller versions of itself.

These are programming patterns that form the operational foundation for
more specialized data structures and algorithms.
"""


def count_positive_numbers(data):

    count = 0

    for value in data:

        if value > 0:
            count += 1

    return count


print(
    "Positive count:",
    count_positive_numbers([-2, 5, 0, 7, -1, 9])
)


# ============================================================
# END OF PROGRAM
# ============================================================
