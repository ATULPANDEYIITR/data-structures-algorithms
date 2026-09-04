# Big-O Notation

Big-O notation is a mathematical way of describing how the amount of work performed by an algorithm grows as the size of its input increases.

The main purpose of Big-O analysis is to understand scalability. An algorithm that works well for ten elements may become extremely slow when the input contains one million elements. Big-O helps identify how quickly the computational requirements grow.

Big-O does not normally tell us the exact execution time in seconds. The actual execution time depends on the computer, programming language, implementation, memory, processor, operating system, and many other factors. Instead, Big-O describes the growth pattern of an algorithm.

For example, an algorithm that performs approximately n operations has linear complexity, written as O(n). An algorithm that performs approximately n squared operations has quadratic complexity, written as O(n²).

The major complexity classes covered in this topic are:

O(1)  
O(log n)  
O(n)  
O(n log n)  
O(n²)  
O(n³)  
O(2ⁿ)  
O(n!)

They represent increasingly rapid growth.

---

# Input Size

Complexity analysis usually begins by identifying the size of the input.

The variable n is commonly used to represent input size.

For a list containing 1,000 elements:

n = 1,000

For a string containing 500 characters:

n = 500

For a graph, n may represent the number of vertices while another variable, such as m, may represent the number of edges.

The correct definition of input size depends on the problem being analyzed.

For an algorithm operating on two independent collections, it may be necessary to use two variables.

For example, if one collection contains n elements and another contains m elements, an operation that processes both independently may have complexity O(n + m).

If every element of the first collection is combined with every element of the second collection, the complexity may be O(nm).

---

# Time Complexity

Time complexity describes how the amount of computational work grows as the input size increases.

Consider an operation that examines every element of a list.

If the list contains n elements, the operation is performed n times.

Therefore, the complexity is O(n).

Time complexity should not be interpreted literally as a number of seconds.

An O(n) algorithm may take one millisecond on one machine and several milliseconds on another. The important point is that when n increases, the amount of work increases proportionally.

For example, if an algorithm performs approximately n operations:

n = 10 means approximately 10 units of work.

n = 1,000 means approximately 1,000 units of work.

n = 1,000,000 means approximately 1,000,000 units of work.

The growth remains linear.

---

# Space Complexity

Space complexity describes how the memory requirements of an algorithm grow with input size.

An algorithm that uses only a fixed number of variables has constant auxiliary space.

Its space complexity is O(1).

For example, calculating the sum of all values in a list can be performed using a single accumulator variable.

The list may contain millions of elements, but the algorithm itself does not need to create another data structure proportional to the input size.

Therefore, its auxiliary space is O(1).

If an algorithm creates a new list containing one item for every input element, its additional memory grows with n.

That algorithm requires O(n) additional space.

Time complexity and space complexity are separate concepts. An algorithm can use more memory to reduce its running time.

---

# Understanding Big-O

Suppose an algorithm performs:

3n + 7

operations.

The exact expression contains both a linear term and a constant term.

As n becomes very large, the 3n term dominates the constant 7.

Therefore:

3n + 7 is O(n).

Similarly:

5n² + 2n + 100 is O(n²).

The quadratic term grows faster than the linear term and the constant term.

This leads to two important simplification rules.

Constant multipliers are ignored.

Lower-order terms are ignored.

For example:

O(2n) becomes O(n).

O(50n) becomes O(n).

O(n² + n) becomes O(n²).

O(n³ + n² + n) becomes O(n³).

The purpose is to identify the dominant growth pattern.

---

# Constant Complexity: O(1)

O(1) represents constant complexity.

An operation has constant complexity when the amount of work does not grow with the input size.

A typical example is accessing an element of an array by its index.

If the operation is:

data[0]

the number of elements in the list does not determine how many operations are required to access that indexed position.

Whether the list contains ten elements or ten million elements, the operation remains independent of the overall list size.

Therefore:

O(1)

Constant complexity does not mean zero time.

It means that the amount of work is bounded independently of n.

Examples of operations that can commonly be considered O(1) include fixed-size arithmetic, variable assignment, direct indexed access, and other operations whose cost does not grow with input size.

---

# Logarithmic Complexity: O(log n)

Logarithmic complexity occurs when the amount of remaining work is repeatedly reduced by a constant factor.

Binary search is the classic example.

Suppose a sorted list contains 1,024 elements.

Binary search examines the middle of the list and eliminates approximately half of the remaining search space after each comparison.

The search space therefore changes approximately as follows:

1,024

512

256

128

64

32

16

8

4

2

1

The number of reductions is approximately log₂(1,024), which is 10.

Therefore, binary search has O(log n) time complexity.

The important characteristic is not that the value is divided specifically by two. Division by any fixed constant produces logarithmic growth.

Repeated division by two, three, five, ten, or another fixed value is still logarithmic.

The base of the logarithm is generally ignored in Big-O notation because different logarithm bases differ only by a constant factor.

---

# Recognizing Logarithmic Loops

A common logarithmic pattern is a loop in which the variable grows or decreases multiplicatively.

For example, suppose a variable starts at 1 and is repeatedly multiplied by 2.

The sequence is:

1

2

4

8

16

32

64

and so on.

After k iterations, the value is approximately 2 raised to the power of k.

The loop reaches n when:

2ᵏ is approximately equal to n.

Solving for k gives:

k is approximately log₂(n).

Therefore, the loop is O(log n).

Similarly, repeatedly dividing n by two produces O(log n).

This pattern is extremely important when analyzing algorithms.

---

# Linear Complexity: O(n)

Linear complexity occurs when the amount of work grows directly with input size.

A simple example is scanning every element of a list.

If the list contains n elements and each element is examined once, the algorithm performs approximately n operations.

Therefore:

O(n).

Linear search is a common example.

If the desired element is the first element, the algorithm can finish immediately.

That is the best case and takes O(1) time.

If the desired element is the final element, or if it is not present, the algorithm may have to examine all n elements.

That is O(n).

Therefore, linear search has O(n) worst-case complexity.

---

# Linearithmic Complexity: O(n log n)

Linearithmic complexity is written as:

O(n log n).

It is one of the most important complexity classes in algorithm design.

It frequently appears in divide-and-conquer algorithms.

Merge sort is a standard example.

Merge sort repeatedly divides the input into smaller pieces.

At each level of the recursion, the total amount of merging work is proportional to n.

The number of levels is approximately log n.

Therefore:

n multiplied by log n

produces:

O(n log n).

This is considerably more efficient than O(n²) for large inputs.

Many efficient comparison-based sorting algorithms have O(n log n) complexity.

---

# Understanding Merge Sort Through Complexity

Suppose an input contains n elements.

The first division produces two subproblems of approximately n/2 elements.

The next division produces four subproblems of approximately n/4 elements.

This continues until the individual pieces contain one element.

The number of division levels is approximately log₂(n).

At every level, the algorithm processes approximately n total elements.

Therefore:

O(n) work per level

multiplied by

O(log n) levels

produces:

O(n log n).

The important point is that the recursive division itself is not the entire explanation. The amount of work performed at each level must also be considered.

---

# Quadratic Complexity: O(n²)

Quadratic complexity occurs when work grows approximately with the square of the input size.

A common pattern is two nested loops where both depend on n.

For example, the outer loop executes n times and the inner loop executes n times for every outer iteration.

The total number of executions is:

n multiplied by n.

Therefore:

n².

The complexity is:

O(n²).

Quadratic complexity is common in algorithms that compare every element with every other element.

Simple comparison-based approaches to duplicate detection and some elementary sorting algorithms can have quadratic complexity.

---

# Triangular Nested Loops

Not every nested loop executes exactly n times.

Consider an outer loop that runs n times and an inner loop that runs only up to the current value of the outer loop.

The total work becomes:

0 + 1 + 2 + 3 + ... + (n - 1).

This is an arithmetic series.

Its total is:

n(n - 1) / 2.

Expanding the expression gives:

(n² - n) / 2.

After removing the constant factor and lower-order term, the result is:

O(n²).

This illustrates why nested loops must be analyzed based on their actual number of iterations rather than simply counting how many loops appear in the source code.

---

# Cubic Complexity: O(n³)

Cubic complexity occurs when work grows proportionally to the cube of the input size.

A typical example is three nested loops where every loop depends on n.

The total work is:

n multiplied by n multiplied by n.

Therefore:

n³.

The complexity is:

O(n³).

The growth is much faster than quadratic growth.

For example:

n = 10 gives 1,000 operations.

n = 100 gives 1,000,000 operations.

n = 1,000 gives 1,000,000,000 operations.

This demonstrates why higher-degree polynomial algorithms can become expensive quickly.

---

# Exponential Complexity: O(2ⁿ)

Exponential complexity occurs when the amount of work grows exponentially with input size.

A common example involves algorithms that repeatedly branch into two possibilities.

Consider generating every subset of a set.

For every element, there are two possibilities:

The element is included.

The element is excluded.

With one element, there are 2 possible subsets.

With two elements, there are 4.

With three elements, there are 8.

With n elements, there are:

2ⁿ

possible subsets.

Therefore, an algorithm that explicitly generates all subsets requires at least exponential output-related work.

Examples of growth include:

n = 10 gives 1,024.

n = 20 gives 1,048,576.

n = 30 gives 1,073,741,824.

Increasing n by one doubles the number of possibilities.

This is fundamentally different from polynomial growth.

---

# Factorial Complexity: O(n!)

Factorial complexity grows even faster than exponential complexity.

The number of permutations of n distinct elements is:

n!

For example:

1! = 1

2! = 2

3! = 6

4! = 24

5! = 120

10! = 3,628,800.

Algorithms that examine every possible ordering of elements can therefore have factorial complexity.

Factorial growth becomes impractical extremely quickly.

The common growth ordering places factorial complexity beyond ordinary exponential complexity:

O(1)

O(log n)

O(n)

O(n log n)

O(n²)

O(n³)

O(2ⁿ)

O(n!).

---

# Comparing Complexity Classes

The standard ordering from slower growth to faster growth is:

O(1)

O(log n)

O(n)

O(n log n)

O(n²)

O(n³)

O(2ⁿ)

O(n!).

This ordering is based on asymptotic growth.

For sufficiently large input sizes, an O(log n) algorithm grows much more slowly than an O(n) algorithm.

An O(n) algorithm grows more slowly than O(n log n).

O(n log n) grows more slowly than O(n²).

O(n²) grows more slowly than O(n³).

Polynomial functions such as n² and n³ eventually grow more slowly than exponential functions such as 2ⁿ.

Factorial growth is even more aggressive.

---

# Best Case, Average Case, and Worst Case

An algorithm may have different behavior depending on the input.

The best case represents the most favorable input.

The worst case represents the least favorable input.

The average case represents expected behavior across an appropriate collection of inputs.

Linear search demonstrates this clearly.

Suppose the target is the first element.

Only one comparison is needed.

Best-case complexity:

O(1).

If the target is at the last position, or does not exist, all elements may need to be examined.

Worst-case complexity:

O(n).

The average case is also generally O(n).

When a complexity is given without qualification, worst-case complexity is often intended, although the exact convention depends on the context.

---

# Consecutive Operations

When operations occur sequentially, their complexities are generally added.

Suppose an algorithm performs one O(n) operation followed by another O(n) operation.

The total is:

O(n) + O(n)

which becomes:

O(2n).

After ignoring the constant factor:

O(n).

Now suppose an algorithm performs:

O(n)

followed by:

O(n²).

The combined complexity is:

O(n + n²).

The quadratic term dominates.

Therefore:

O(n²).

This is why sequential loops should normally be added rather than multiplied.

---

# Conditional Statements

Consider an algorithm with two mutually exclusive branches.

One branch takes O(n).

The other takes O(n²).

Only one branch executes during a single execution.

For worst-case analysis, the more expensive branch is considered.

Therefore, the overall worst-case complexity is:

O(n²).

The branches are not multiplied because they do not execute one after another.

---

# Nested Loops

Nested loops require careful analysis.

Two nested loops do not automatically mean O(n²).

Consider an outer loop that executes n times and an inner loop that always executes exactly 10 times.

The total work is:

10n.

After ignoring the constant 10:

O(n).

Now consider an inner loop that executes n times for every outer iteration.

That produces:

n × n

and therefore:

O(n²).

If the inner loop repeatedly doubles a variable until it reaches n, it contributes O(log n).

An outer O(n) loop combined with an inner O(log n) loop produces:

O(n log n).

The correct complexity comes from analyzing the iteration count of each loop.

---

# Dependent Nested Loops

Consider:

for i from 1 to n:

    for j from 1 to i:

        perform an operation

The inner loop does not execute n times during every iteration.

Instead, its execution count increases with i.

The total work is approximately:

1 + 2 + 3 + ... + n.

This is approximately:

n² / 2.

Therefore:

O(n²).

This pattern occurs frequently in algorithm analysis.

---

# Multiple Input Sizes

Suppose an algorithm receives two lists.

The first list has n elements.

The second list has m elements.

If the algorithm scans the first list and then scans the second list, the complexity is:

O(n + m).

It should not automatically be simplified to O(n), because n and m may have completely different sizes.

If every element of the first list is paired with every element of the second list, the complexity becomes:

O(nm).

The number of independent input dimensions must be preserved when analyzing the algorithm.

---

# Recursion and Big-O

Recursive algorithms require a slightly different style of analysis.

The main questions are:

How much work does each call perform?

How many recursive calls does each call create?

How quickly does the input size decrease?

Consider a recursive function that reduces n by one each time.

Its recurrence can be represented as:

T(n) = T(n - 1) + O(1).

There are approximately n recursive calls.

Therefore:

O(n).

Now consider a recursive function that reduces the problem by half:

T(n) = T(n/2) + O(1).

The number of recursive levels is logarithmic.

Therefore:

O(log n).

When each call creates multiple recursive branches, the complexity can become exponential.

---

# Naive Recursive Fibonacci

Naive recursive Fibonacci is a classic example of exponential growth.

The recursive definition creates two major recursive branches:

F(n) = F(n - 1) + F(n - 2).

The same smaller Fibonacci values are repeatedly calculated.

For example, calculating a value for a larger n may calculate the same smaller Fibonacci values many times.

The recursion tree therefore grows exponentially.

This makes naive recursive Fibonacci computationally inefficient for larger values of n.

---

# Memoization

Memoization stores previously calculated results.

Instead of calculating the same Fibonacci value repeatedly, the algorithm calculates each required value once and stores it.

With memoization, the number of distinct Fibonacci states is proportional to n.

The time complexity becomes:

O(n).

The memory used by the cache is also:

O(n).

This demonstrates an important relationship between time and space complexity.

Additional memory can sometimes be used to avoid repeated computation and improve time complexity.

---

# Recursive Space Complexity

Recursive algorithms consume stack memory.

A recursive algorithm with n levels of recursion can require O(n) stack space.

A recursive algorithm that repeatedly halves the input may require O(log n) stack space.

For example:

T(n) = T(n - 1) + O(1)

can create a recursion depth proportional to n.

A recursion that repeatedly halves the input creates a recursion depth proportional to log n.

Time complexity and recursion depth are separate measurements and should not be confused.

---

# Amortized Complexity

Some operations are occasionally expensive but inexpensive when considered across a long sequence of operations.

Dynamic arrays provide a useful conceptual example.

Most append operations can be performed in amortized O(1) time.

Occasionally, the underlying storage becomes full and a larger storage area must be allocated.

Existing elements may then need to be copied.

That individual resizing operation can require O(n) work.

Despite this occasional expensive operation, the average cost across a long sequence of append operations can remain amortized O(1).

Amortized analysis is therefore different from simply asking for the worst cost of one individual operation.

---

# Python Data Structures and Complexity

Understanding Big-O in Python also requires understanding common data structures.

List indexing is typically O(1).

For example:

data[index]

can directly access an indexed position.

Searching for a value in a list is typically O(n) because the elements may need to be examined sequentially.

Set membership is typically O(1) on average because sets use hash-based lookup.

Dictionary lookup is also typically O(1) on average.

Sorting a collection is generally O(n log n).

These complexities explain why choosing the appropriate data structure can have a major impact on algorithm performance.

---

# List Membership and Set Membership

Consider the question:

Does this value exist in the collection?

If the collection is a list, membership testing is generally:

O(n).

The list may need to be scanned from beginning to end.

If the collection is a set, membership testing is typically:

O(1) average case.

The trade-off is that creating the set requires processing the input.

Converting a list of n elements into a set generally requires:

O(n).

Therefore, when analyzing a complete algorithm, preprocessing costs must be included.

A set becomes particularly useful when many membership queries are performed against the same collection.

---

# Duplicate Detection

Duplicate detection provides a useful comparison of algorithmic strategies.

A pairwise approach compares every element with every other element.

Its time complexity is:

O(n²).

Its additional space can be:

O(1).

A hash-based approach stores previously observed values in a set.

Its average time complexity is:

O(n).

Its additional space complexity is:

O(n).

A sorting-based approach first sorts the data and then scans adjacent elements.

Sorting takes:

O(n log n).

The subsequent scan takes:

O(n).

The combined complexity is:

O(n log n + n).

The dominant term is:

O(n log n).

This demonstrates the time-space trade-off involved in algorithm design.

---

# Sorting and Complexity

Sorting is one of the most common contexts in which Big-O notation appears.

An inefficient comparison-based sorting algorithm may require:

O(n²).

More efficient general comparison-based sorting algorithms can achieve:

O(n log n).

Merge sort has O(n log n) worst-case time complexity.

Heap sort also has O(n log n) worst-case time complexity.

The distinction between O(n²) and O(n log n) becomes extremely important as n grows.

For small inputs, the practical difference may not always be large.

For large inputs, the difference can become substantial.

---

# Space-Time Trade-Off

An algorithm may use additional memory to reduce execution time.

A hash set is a simple example.

Searching repeatedly through a list may require O(n) work per lookup.

Constructing a set requires additional memory and preprocessing time, but subsequent average-case membership operations are typically O(1).

Memoization provides another example.

Without caching, a recursive algorithm may repeatedly calculate the same results.

With caching, results are stored and reused.

The algorithm consumes additional memory but can reduce the amount of computation dramatically.

There is no universal rule that an algorithm must minimize either time or memory. The appropriate balance depends on the problem and system constraints.

---

# Big-O and Exact Runtime

Big-O describes asymptotic growth rather than exact runtime.

Suppose two algorithms are both O(n).

One might perform:

n operations.

The other might perform:

1,000n operations.

Both are O(n).

They have the same asymptotic growth but may have very different practical runtimes.

Similarly, an O(n²) algorithm may be faster than an O(n) algorithm for a small input if the O(n) algorithm has a very large constant factor.

As n grows sufficiently large, the asymptotic behavior becomes increasingly important.

This is why algorithm analysis and practical benchmarking serve different purposes.

---

# Asymptotic Analysis

Big-O focuses on what happens as n becomes very large.

This is called asymptotic analysis.

Finite input sizes can sometimes produce behavior that differs from the long-term trend.

For example:

1000n

and:

n

have the same Big-O complexity:

O(n).

The ratio between them remains a constant.

By contrast:

n

and:

n²

do not have the same asymptotic growth.

As n increases, n² grows increasingly faster than n.

This distinction is the mathematical foundation of complexity classification.

---

# Big-O, Big-Omega, and Big-Theta

Big-O is part of a larger family of asymptotic notations.

Big-O, written as O(f(n)), represents an asymptotic upper bound.

Big-Omega, written as Ω(f(n)), represents an asymptotic lower bound.

Big-Theta, written as Θ(f(n)), represents a tight asymptotic bound when both the upper and lower bounds have the same growth rate.

For example, an algorithm performing approximately:

3n + 2

operations has:

O(n)

upper-bound growth,

Ω(n)

lower-bound growth, and

Θ(n)

tight asymptotic growth.

In informal programming conversations, people frequently use Big-O to refer generally to algorithmic complexity. In mathematical analysis, distinguishing O, Ω, and Θ can provide more precision.

---

# Formal Definition of Big-O

A function f(n) is O(g(n)) if there are positive constants c and n₀ such that:

0 ≤ f(n) ≤ c × g(n)

for every n greater than or equal to n₀.

The important idea is that beyond some sufficiently large input size, f(n) is bounded above by a constant multiple of g(n).

For example:

f(n) = 3n + 7.

For sufficiently large n, this function can be bounded by a constant multiple of n.

Therefore:

3n + 7 is O(n).

The exact values of the constants are usually not the focus of ordinary algorithm analysis. The growth relationship is the main concern.

---

# Polynomial Growth

Polynomial complexity includes expressions such as:

O(n)

O(n²)

O(n³)

O(n⁴)

and more generally:

O(nᵏ)

where k is a fixed constant.

Polynomial algorithms can still become expensive.

For example, O(n³) is much more expensive than O(n), even though both are polynomial.

The degree of the polynomial matters.

As the degree increases, the growth becomes increasingly rapid.

---

# Exponential Growth

Exponential complexity includes expressions such as:

O(2ⁿ)

O(3ⁿ)

O(4ⁿ)

and generally:

O(cⁿ)

where c is a constant greater than 1.

Exponential growth is fundamentally faster than any fixed polynomial growth.

For sufficiently large n:

2ⁿ grows faster than n³.

2ⁿ grows faster than n¹⁰.

2ⁿ eventually grows faster than nᵏ for any fixed k.

This is one reason exponential algorithms become difficult to use as input sizes increase.

---

# Output Size and Complexity

Output size can place a lower bound on the time required by an algorithm.

Suppose an algorithm must explicitly generate all subsets of n elements.

There are:

2ⁿ

subsets.

Even if generating each subset were extremely efficient, the algorithm still has to produce an exponential number of outputs.

Therefore, an algorithm whose required output itself is exponential cannot generally have polynomial total output-generation time.

This is an important distinction when analyzing algorithms that enumerate combinations, subsets, permutations, or other large result spaces.

---

# Common Big-O Patterns

The following patterns are useful when recognizing complexity.

A single operation independent of n:

O(1).

A loop that runs once for every element:

O(n).

A loop that repeatedly halves or doubles its search space:

O(log n).

A linear amount of work performed at every logarithmic level:

O(n log n).

Two independent n-sized loops nested together:

O(n²).

Three independent n-sized loops nested together:

O(n³).

A recursive process that branches into approximately two possibilities at every level:

O(2ⁿ).

Generating every ordering of n elements:

O(n!).

Recognizing these structural patterns makes complexity analysis much faster.

---

# Complexity of Common Algorithmic Structures

A direct indexed lookup commonly has O(1) complexity.

A sequential search commonly has O(n) worst-case complexity.

Binary search has O(log n) time complexity when the required ordering and data structure support it.

Merge sort has O(n log n) time complexity.

Pairwise comparison algorithms commonly have O(n²) complexity.

Algorithms with three independent nested dimensions commonly have O(n³) complexity.

Subset enumeration commonly has O(2ⁿ) output-related complexity.

Permutation enumeration commonly has O(n!) output-related complexity.

These are patterns rather than universal rules. The exact algorithm and implementation must still be examined.

---

# Important Complexity Analysis Rules

When analyzing an algorithm, first identify the input size.

Then identify the operations that depend on that input size.

Count how frequently those operations execute.

For consecutive sections, add their costs.

For nested operations, determine whether one operation executes for every iteration of another.

For conditional branches, consider the appropriate execution path, usually the worst case when analyzing worst-case complexity.

For recursion, identify the recurrence and recursion depth.

Remove constant factors.

Remove lower-order terms.

Keep the dominant growth term.

For multiple independent input sizes, retain separate variables when necessary.

For algorithms using additional data structures, analyze the additional memory separately.

---

# Example of Complete Complexity Analysis

Consider an algorithm that:

First copies an input list.

Then sorts the copy.

Then scans the sorted result to identify duplicates.

Copying the list requires:

O(n).

Sorting requires:

O(n log n).

Scanning requires:

O(n).

The total is:

O(n) + O(n log n) + O(n).

This simplifies to:

O(n log n).

The sorting stage dominates the other stages.

This is an example of how a complete algorithm can contain several different complexity classes while still having one dominant final complexity.

---

# Why Big-O Matters in Algorithm Design

Two algorithms can solve exactly the same problem while having very different complexity.

One algorithm might use pairwise comparisons and require O(n²) time.

Another might use a hash-based data structure and require O(n) average time.

Both produce the same logical result.

The difference lies in how the problem is approached and what data structures are used.

Big-O provides a systematic way to reason about these choices.

It allows algorithm designers to identify approaches that scale poorly and replace them with more efficient strategies when appropriate.

---

# Complexity and Data Structure Choice

The same logical operation can have different complexity depending on the underlying data structure.

Searching an unsorted list:

O(n).

Searching sorted data using binary search:

O(log n).

Searching a hash-based set:

O(1) average case.

The operation is conceptually similar in all three cases:

Determine whether a value exists.

The difference comes from the representation of the data and the algorithm used to search it.

This is one of the most important practical applications of Big-O analysis.

---

# Complexity Is About Growth

The central idea behind Big-O is growth.

For example:

O(1) remains essentially constant as n increases.

O(log n) grows very slowly.

O(n) grows proportionally to n.

O(n log n) grows slightly faster than linear.

O(n²) grows quadratically.

O(n³) grows cubically.

O(2ⁿ) grows exponentially.

O(n!) grows factorially.

The larger the input becomes, the more significant these differences become.

Big-O notation therefore provides a mathematical language for discussing the scalability of algorithms without depending on a particular computer or exact execution time.
