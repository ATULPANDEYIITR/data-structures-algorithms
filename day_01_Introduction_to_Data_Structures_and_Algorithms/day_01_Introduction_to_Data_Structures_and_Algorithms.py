# ============================================================

# INTRODUCTION TO DATA STRUCTURES AND ALGORITHMS

# Comprehensive Python Learning Program

# ============================================================

"""
DATA STRUCTURES AND ALGORITHMS (DSA)

Data Structures:
A data structure is a way of organizing, storing, and managing data
so that it can be accessed and modified efficiently.

Algorithms:
An algorithm is a finite, step-by-step set of instructions used to
solve a problem or perform a specific task.

DSA combines both concepts:

```
DATA + ORGANIZATION + ALGORITHM = EFFICIENT PROBLEM SOLVING
```

This program introduces:

1. What data structures are
2. What algorithms are
3. Why DSA is important
4. Linear data structures
5. Non-linear data structures
6. Common Python data structures
7. Searching algorithms
8. Sorting algorithms
9. Algorithm complexity
10. Time complexity
11. Space complexity
12. Brute-force vs optimized solutions
13. Basic problem-solving methodology
    """

# ============================================================

# 1. PROGRAM INTRODUCTION

# ============================================================

print("=" * 70)
print("INTRODUCTION TO DATA STRUCTURES AND ALGORITHMS")
print("=" * 70)

print("\nData Structures organize data.")
print("Algorithms process data and solve problems.")
print("Together, they help us build efficient programs.")

# ============================================================

# 2. WHAT IS DATA?

# ============================================================

print("\n" + "=" * 70)
print("1. WHAT IS DATA?")
print("=" * 70)

"""
Data is raw information that can be stored and processed.

Examples:

* Student names
* Employee salaries
* Product prices
* User IDs
* Examination marks
* Locations

A computer program must organize this data efficiently.
The method used to organize data is called a DATA STRUCTURE.
"""

student_name = "Atul"
student_age = 30
student_marks = 85.5

print("Student Name:", student_name)
print("Student Age:", student_age)
print("Student Marks:", student_marks)

# ============================================================

# 3. WHAT IS A DATA STRUCTURE?

# ============================================================

print("\n" + "=" * 70)
print("2. WHAT IS A DATA STRUCTURE?")
print("=" * 70)

"""
A Data Structure is a method of storing and organizing data.

The choice of a data structure affects:

1. Speed of accessing data
2. Speed of inserting data
3. Speed of deleting data
4. Memory usage
5. Overall program performance

Examples of common data structures:

LINEAR DATA STRUCTURES:

* Array
* List
* Stack
* Queue
* Linked List

NON-LINEAR DATA STRUCTURES:

* Tree
* Graph
* Heap
* Trie

SPECIAL DATA STRUCTURES:

* Hash Table
* Set
* Dictionary
  """

# ============================================================

# 4. PYTHON LIST AS AN ARRAY-LIKE DATA STRUCTURE

# ============================================================

print("\n" + "=" * 70)
print("3. LIST / ARRAY EXAMPLE")
print("=" * 70)

numbers = [10, 20, 30, 40, 50]

print("Original List:", numbers)

# Accessing an element

print("First Element:", numbers[0])

# Updating an element

numbers[1] = 25

print("After Updating:", numbers)

# Adding an element

numbers.append(60)

print("After Adding:", numbers)

# Removing an element

numbers.remove(30)

print("After Removing:", numbers)

# ============================================================

# 5. DATA STRUCTURE OPERATIONS

# ============================================================

print("\n" + "=" * 70)
print("4. COMMON DATA STRUCTURE OPERATIONS")
print("=" * 70)

"""
Most data structures support operations such as:

1. Traversal
2. Insertion
3. Deletion
4. Searching
5. Sorting
6. Updating
   """

data = [5, 10, 15, 20, 25]

# Traversal

print("\nTraversal:")

for item in data:
print(item)

# Insertion

data.append(30)

print("\nAfter Insertion:", data)

# Updating

data[0] = 100

print("After Updating:", data)

# Deletion

data.remove(15)

print("After Deletion:", data)

# ============================================================

# 6. WHAT IS AN ALGORITHM?

# ============================================================

print("\n" + "=" * 70)
print("5. WHAT IS AN ALGORITHM?")
print("=" * 70)

"""
An algorithm is a finite sequence of logical steps used to solve
a problem.

A good algorithm should have:

1. Input
   It may accept zero or more inputs.

2. Output
   It should produce at least one meaningful result.

3. Definiteness
   Every step should be clear and unambiguous.

4. Finiteness
   The algorithm must eventually stop.

5. Effectiveness
   Each step should be practical and executable.
   """

# Example Algorithm:

# Find the largest number in a list.

numbers = [45, 12, 78, 23, 90, 34]

largest = numbers[0]

for number in numbers:

```
if number > largest:
    largest = number
```

print("Numbers:", numbers)
print("Largest Number:", largest)

# ============================================================

# 7. ALGORITHM DESIGN PROCESS

# ============================================================

print("\n" + "=" * 70)
print("6. HOW TO DESIGN AN ALGORITHM")
print("=" * 70)

"""
A structured approach to problem solving:

STEP 1:
Understand the problem.

STEP 2:
Identify the input.

STEP 3:
Identify the expected output.

STEP 4:
Understand constraints.

STEP 5:
Create simple examples.

STEP 6:
Think about a brute-force solution.

STEP 7:
Identify inefficiencies.

STEP 8:
Optimize the solution.

STEP 9:
Test edge cases.

STEP 10:
Analyze time and space complexity.
"""

# ============================================================

# 8. BRUTE-FORCE APPROACH

# ============================================================

print("\n" + "=" * 70)
print("7. BRUTE-FORCE ALGORITHM")
print("=" * 70)

"""
A brute-force algorithm tries possible solutions directly.

Example:
Find whether a number exists in a list.
"""

def brute_force_search(numbers, target):

```
for index in range(len(numbers)):

    if numbers[index] == target:
        return index

return -1
```

numbers = [10, 25, 40, 55, 70]
target = 40

result = brute_force_search(numbers, target)

if result != -1:
print("Target found at index:", result)

else:
print("Target not found")

# ============================================================

# 9. SEARCHING ALGORITHMS

# ============================================================

print("\n" + "=" * 70)
print("8. SEARCHING ALGORITHMS")
print("=" * 70)

"""
Searching means finding a specific element in a collection.

Two important searching algorithms:

1. Linear Search
2. Binary Search
   """

# ============================================================

# 10. LINEAR SEARCH

# ============================================================

print("\nLINEAR SEARCH")

"""
Linear Search checks elements one by one.

Example:

[10, 20, 30, 40, 50]

To find 40:

Check 10
Check 20
Check 30
Check 40 -> Found
"""

def linear_search(data, target):

```
for index in range(len(data)):

    if data[index] == target:
        return index

return -1
```

numbers = [10, 20, 30, 40, 50]

target = 40

position = linear_search(numbers, target)

print("List:", numbers)
print("Target:", target)

if position != -1:
print("Target found at index:", position)

else:
print("Target not found")

# ============================================================

# 11. BINARY SEARCH

# ============================================================

print("\n" + "=" * 70)
print("BINARY SEARCH")
print("=" * 70)

"""
Binary Search works only on SORTED data.

It repeatedly divides the search area into two parts.

Example:

[10, 20, 30, 40, 50, 60, 70]

Find 50.

Step 1:
Check middle element.

Step 2:
If target is larger, search right half.

Step 3:
If target is smaller, search left half.

Binary Search is generally faster than Linear Search
for large sorted collections.
"""

def binary_search(data, target):

```
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
```

numbers = [10, 20, 30, 40, 50, 60, 70]

target = 50

position = binary_search(numbers, target)

print("Sorted List:", numbers)
print("Target:", target)

if position != -1:
print("Target found at index:", position)

else:
print("Target not found")

# ============================================================

# 12. INTRODUCTION TO SORTING

# ============================================================

print("\n" + "=" * 70)
print("9. SORTING ALGORITHMS")
print("=" * 70)

"""
Sorting means arranging data in a particular order.

Examples:

Ascending:
[10, 20, 30, 40, 50]

Descending:
[50, 40, 30, 20, 10]

Sorting is important because it can make searching,
data processing, and analysis more efficient.
"""

# ============================================================

# 13. BUBBLE SORT

# ============================================================

print("\nBUBBLE SORT")

"""
Bubble Sort repeatedly compares adjacent elements.

If they are in the wrong order, they are swapped.

Example:

[5, 2, 4, 1]

Compare 5 and 2 -> Swap
Compare 5 and 4 -> Swap
Compare 5 and 1 -> Swap

This process continues until the list is sorted.
"""

def bubble_sort(data):

```
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
```

numbers = [64, 34, 25, 12, 22, 11, 90]

sorted_numbers = bubble_sort(numbers)

print("Original:", numbers)
print("Sorted:", sorted_numbers)

# ============================================================

# 14. SELECTION SORT

# ============================================================

print("\n" + "=" * 70)
print("SELECTION SORT")
print("=" * 70)

"""
Selection Sort repeatedly finds the smallest element
and places it in the correct position.
"""

def selection_sort(data):

```
result = data.copy()

n = len(result)

for i in range(n):

    minimum_index = i

    for j in range(i + 1, n):

        if result[j] < result[minimum_index]:
            minimum_index = j

    result[i], result[minimum_index] = (
        result[minimum_index],
        result[i]
    )

return result
```

numbers = [29, 10, 14, 37, 13]

sorted_numbers = selection_sort(numbers)

print("Original:", numbers)
print("Sorted:", sorted_numbers)

# ============================================================

# 15. INSERTION SORT

# ============================================================

print("\n" + "=" * 70)
print("INSERTION SORT")
print("=" * 70)

"""
Insertion Sort builds a sorted section of the list.

It takes one element at a time and inserts it
into its correct position.
"""

def insertion_sort(data):

```
result = data.copy()

for i in range(1, len(result)):

    current_value = result[i]

    position = i - 1

    while position >= 0 and result[position] > current_value:

        result[position + 1] = result[position]

        position -= 1

    result[position + 1] = current_value

return result
```

numbers = [12, 11, 13, 5, 6]

sorted_numbers = insertion_sort(numbers)

print("Original:", numbers)
print("Sorted:", sorted_numbers)

# ============================================================

# 16. INTRODUCTION TO STACK

# ============================================================

print("\n" + "=" * 70)
print("10. STACK DATA STRUCTURE")
print("=" * 70)

"""
A Stack follows:

LIFO

Last In, First Out

Example:

Push:
10
20
30

Stack:

Top -> 30
20
10

Pop removes 30 first.
"""

stack = []

# Push

stack.append(10)
stack.append(20)
stack.append(30)

print("Stack:", stack)

# Pop

removed_item = stack.pop()

print("Removed:", removed_item)

print("Stack After Pop:", stack)

# ============================================================

# 17. INTRODUCTION TO QUEUE

# ============================================================

print("\n" + "=" * 70)
print("11. QUEUE DATA STRUCTURE")
print("=" * 70)

"""
A Queue follows:

FIFO

First In, First Out

Example:

Front -> 10, 20, 30 <- Rear

The first element is removed first.
"""

from collections import deque

queue = deque()

# Enqueue

queue.append(10)
queue.append(20)
queue.append(30)

print("Queue:", list(queue))

# Dequeue

removed_item = queue.popleft()

print("Removed:", removed_item)

print("Queue After Dequeue:", list(queue))

# ============================================================

# 18. HASH TABLE / DICTIONARY

# ============================================================

print("\n" + "=" * 70)
print("12. HASH TABLE / DICTIONARY")
print("=" * 70)

"""
A hash table stores data using key-value pairs.

Python Dictionary is implemented using hashing.

Example:

Name -> Marks

Atul -> 90
Rahul -> 85
"""

student_marks = {
"Atul": 90,
"Rahul": 85,
"Priya": 92
}

print("Student Marks:", student_marks)

print("Atul's Marks:", student_marks["Atul"])

student_marks["Aman"] = 88

print("After Adding Aman:", student_marks)

# ============================================================

# 19. SET DATA STRUCTURE

# ============================================================

print("\n" + "=" * 70)
print("13. SET DATA STRUCTURE")
print("=" * 70)

"""
A Set stores unique values.

Duplicate values are automatically removed.
"""

numbers = {10, 20, 30, 20, 10, 40}

print("Set:", numbers)

numbers.add(50)

print("After Adding:", numbers)

# ============================================================

# 20. INTRODUCTION TO TREES

# ============================================================

print("\n" + "=" * 70)
print("14. TREE DATA STRUCTURE")
print("=" * 70)

"""
A Tree is a non-linear hierarchical data structure.

Example:

```
    10
   /  \
  5    15
 / \
3   7
```

Important terms:

Root:
The top node.

Parent:
A node with children.

Child:
A node connected below another node.

Leaf:
A node without children.

Subtree:
A smaller tree inside a larger tree.
"""

class TreeNode:

```
def __init__(self, value):

    self.value = value

    self.left = None

    self.right = None
```

root = TreeNode(10)

root.left = TreeNode(5)

root.right = TreeNode(15)

root.left.left = TreeNode(3)

root.left.right = TreeNode(7)

print("Root:", root.value)

print("Left Child:", root.left.value)

print("Right Child:", root.right.value)

# ============================================================

# 21. INTRODUCTION TO GRAPHS

# ============================================================

print("\n" + "=" * 70)
print("15. GRAPH DATA STRUCTURE")
print("=" * 70)

"""
A Graph consists of:

Vertices (Nodes)
Edges (Connections)

Example:

A ----- B
|       |
|       |
C ----- D

Graphs are used in:

* Social networks
* Maps
* GPS navigation
* Computer networks
* Recommendation systems
* Web links
  """

graph = {

```
"A": ["B", "C"],

"B": ["A", "D"],

"C": ["A", "D"],

"D": ["B", "C"]
```

}

print("Graph Representation:")

for node in graph:

```
print(node, "->", graph[node])
```

# ============================================================

# 22. BREADTH-FIRST SEARCH INTRODUCTION

# ============================================================

print("\n" + "=" * 70)
print("16. BREADTH-FIRST SEARCH")
print("=" * 70)

"""
Breadth-First Search (BFS) explores nodes level by level.

BFS commonly uses a Queue.
"""

def breadth_first_search(graph, start):

```
visited = set()

queue = deque([start])

visited.add(start)

while queue:

    current_node = queue.popleft()

    print(current_node, end=" ")

    for neighbor in graph[current_node]:

        if neighbor not in visited:

            visited.add(neighbor)

            queue.append(neighbor)
```

print("BFS Traversal:")

breadth_first_search(graph, "A")

print()

# ============================================================

# 23. DEPTH-FIRST SEARCH INTRODUCTION

# ============================================================

print("\n" + "=" * 70)
print("17. DEPTH-FIRST SEARCH")
print("=" * 70)

"""
Depth-First Search (DFS) explores deeply before
returning to explore other branches.

DFS can be implemented using:

1. Recursion
2. Stack
   """

def depth_first_search(graph, node, visited=None):

```
if visited is None:

    visited = set()

visited.add(node)

print(node, end=" ")

for neighbor in graph[node]:

    if neighbor not in visited:

        depth_first_search(
            graph,
            neighbor,
            visited
        )
```

print("DFS Traversal:")

depth_first_search(graph, "A")

print()

# ============================================================

# 24. TIME COMPLEXITY

# ============================================================

print("\n" + "=" * 70)
print("18. TIME COMPLEXITY")
print("=" * 70)

"""
Time Complexity describes how the running time of an
algorithm grows as the input size increases.

Common complexities:

O(1)       Constant Time
O(log n)   Logarithmic Time
O(n)       Linear Time
O(n log n) Linearithmic Time
O(n^2)     Quadratic Time
O(2^n)     Exponential Time
O(n!)      Factorial Time
"""

# O(1) EXAMPLE

def constant_time_example(data):

```
return data[0]
```

numbers = [10, 20, 30, 40]

print("O(1) Example:", constant_time_example(numbers))

# O(n) EXAMPLE

def linear_time_example(data):

```
total = 0

for number in data:

    total += number

return total
```

print("O(n) Example:", linear_time_example(numbers))

# O(n^2) EXAMPLE

def quadratic_time_example(data):

```
for first in data:

    for second in data:

        pass
```

print("O(n^2) Example Executed")

# ============================================================

# 25. SPACE COMPLEXITY

# ============================================================

print("\n" + "=" * 70)
print("19. SPACE COMPLEXITY")
print("=" * 70)

"""
Space Complexity describes how much additional memory
an algorithm requires.

Example:

O(1):
Uses a fixed amount of extra memory.

O(n):
Uses additional memory proportional to input size.
"""

def constant_space_example(numbers):

```
maximum = numbers[0]

for number in numbers:

    if number > maximum:

        maximum = number

return maximum
```

def linear_space_example(numbers):

```
copied_numbers = []

for number in numbers:

    copied_numbers.append(number)

return copied_numbers
```

numbers = [10, 20, 30, 40, 50]

print(
"Constant Space Result:",
constant_space_example(numbers)
)

print(
"Linear Space Result:",
linear_space_example(numbers)
)

# ============================================================

# 26. BRUTE-FORCE VS OPTIMIZED APPROACH

# ============================================================

print("\n" + "=" * 70)
print("20. BRUTE-FORCE VS OPTIMIZED ALGORITHM")
print("=" * 70)

"""
PROBLEM:

Determine whether a list contains duplicate elements.
"""

# BRUTE-FORCE APPROACH

# Time Complexity: O(n^2)

def contains_duplicate_brute_force(numbers):

```
for i in range(len(numbers)):

    for j in range(i + 1, len(numbers)):

        if numbers[i] == numbers[j]:

            return True

return False
```

# OPTIMIZED APPROACH

# Average Time Complexity: O(n)

def contains_duplicate_optimized(numbers):

```
seen = set()

for number in numbers:

    if number in seen:

        return True

    seen.add(number)

return False
```

numbers = [10, 20, 30, 40, 20]

print(
"Brute Force Duplicate Check:",
contains_duplicate_brute_force(numbers)
)

print(
"Optimized Duplicate Check:",
contains_duplicate_optimized(numbers)
)

# ============================================================

# 27. DATA STRUCTURE SELECTION

# ============================================================

print("\n" + "=" * 70)
print("21. CHOOSING THE RIGHT DATA STRUCTURE")
print("=" * 70)

"""
Different problems require different data structures.

LIST / ARRAY:
Use when ordered data and indexing are important.

STACK:
Use when the most recent item should be processed first.

QUEUE:
Use when the oldest item should be processed first.

HASH TABLE:
Use when fast lookup using keys is required.

SET:
Use when uniqueness is important.

TREE:
Use when data has a hierarchical structure.

GRAPH:
Use when entities have relationships or connections.

HEAP:
Use when repeatedly accessing minimum or maximum values
is important.
"""

# ============================================================

# 28. COMPLETE PRACTICAL EXAMPLE

# ============================================================

print("\n" + "=" * 70)
print("22. PRACTICAL DSA EXAMPLE")
print("=" * 70)

"""
Problem:

Given a list of student marks:

1. Find the highest mark.
2. Find the lowest mark.
3. Calculate the average.
4. Search for a specific mark.
5. Sort the marks.
   """

marks = [78, 92, 65, 88, 95, 72, 84]

print("Original Marks:", marks)

# Find maximum

highest_mark = max(marks)

print("Highest Mark:", highest_mark)

# Find minimum

lowest_mark = min(marks)

print("Lowest Mark:", lowest_mark)

# Calculate average

average_mark = sum(marks) / len(marks)

print("Average Mark:", average_mark)

# Search

target_mark = 88

position = linear_search(
marks,
target_mark
)

print(
"Position of Target Mark:",
position
)

# Sort

sorted_marks = bubble_sort(marks)

print("Sorted Marks:", sorted_marks)

# ============================================================

# 29. IMPORTANT DSA PROBLEM-SOLVING CHECKLIST

# ============================================================

print("\n" + "=" * 70)
print("23. DSA PROBLEM-SOLVING CHECKLIST")
print("=" * 70)

checklist = [

```
"Understand the problem completely",

"Identify input and output",

"Understand constraints",

"Create examples",

"Identify edge cases",

"Develop a brute-force solution",

"Calculate time complexity",

"Calculate space complexity",

"Identify bottlenecks",

"Select an appropriate data structure",

"Optimize the algorithm",

"Test the solution",

"Write clean and readable code"
```

]

for number, item in enumerate(checklist, start=1):

```
print(f"{number}. {item}")
```

# ============================================================

# 30. IMPORTANT DATA STRUCTURES

# ============================================================

print("\n" + "=" * 70)
print("24. IMPORTANT DATA STRUCTURES TO LEARN")
print("=" * 70)

data_structures = [

```
"Arrays",

"Strings",

"Linked Lists",

"Stacks",

"Queues",

"Hash Tables",

"Sets",

"Trees",

"Binary Search Trees",

"Heaps",

"Tries",

"Graphs",

"Disjoint Set Union",

"Segment Trees",

"Fenwick Trees"
```

]

for number, structure in enumerate(
data_structures,
start=1
):

```
print(
    f"{number}. {structure}"
)
```

# ============================================================

# 31. IMPORTANT ALGORITHMS

# ============================================================

print("\n" + "=" * 70)
print("25. IMPORTANT ALGORITHMS TO LEARN")
print("=" * 70)

algorithms = [

```
"Linear Search",

"Binary Search",

"Bubble Sort",

"Selection Sort",

"Insertion Sort",

"Merge Sort",

"Quick Sort",

"Heap Sort",

"Breadth-First Search",

"Depth-First Search",

"Dijkstra's Algorithm",

"Dynamic Programming",

"Greedy Algorithms",

"Backtracking",

"Divide and Conquer",

"String Matching Algorithms"
```

]

for number, algorithm in enumerate(
algorithms,
start=1
):

```
print(
    f"{number}. {algorithm}"
)
```

# ============================================================

# 32. FINAL SUMMARY

# ============================================================

print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print("""
Data Structures and Algorithms are fundamental to
computer science and software development.

Data Structures help us organize and store information.

Algorithms help us process information and solve problems.

The efficiency of a program depends heavily on:

1. Choosing the right data structure.
2. Designing an efficient algorithm.
3. Understanding time complexity.
4. Understanding space complexity.
5. Identifying opportunities for optimization.

A strong DSA foundation helps in:

* Writing efficient programs
* Solving complex problems
* Technical interviews
* Competitive programming
* Software engineering
* System design
* Artificial Intelligence
* Machine Learning
* Data Processing
* Database systems
* Cybersecurity

The journey through Data Structures and Algorithms begins
with understanding basic concepts and gradually progresses
towards advanced problem-solving techniques.
""")

print("=" * 70)
print("END OF INTRODUCTION TO DATA STRUCTURES AND ALGORITHMS")
print("=" * 70)
