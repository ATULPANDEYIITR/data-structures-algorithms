"""
Mathematical Foundations for DSA
================================

A self-contained study and practice script covering:

1. Powers and exponents
2. Logarithms
3. Factorials
4. Permutations
5. Combinations
6. Summations and common series
7. Modular arithmetic
8. Basic probability
9. Counting principles
10. Mathematical reasoning used in algorithm analysis
11. Numerical edge cases and implementation concerns
12. Advanced DSA-oriented applications

The script uses only Python's standard library.

Run:
    python mathematical_foundations_for_dsa.py

The demonstrations are organized from elementary concepts to DSA-oriented
applications. Most functions return values so that they can also be reused
as a reference implementation.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from functools import reduce
from operator import mul
from typing import Iterable, List, Sequence, Tuple


# =============================================================================
# 0. GENERAL UTILITIES
# =============================================================================

def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_subsection(title: str) -> None:
    """Print a subsection heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def demonstrate(name: str, value) -> None:
    """Print a named result in a readable format."""
    print(f"{name:<42}: {value}")


# =============================================================================
# 1. POWERS AND EXPONENTS
# =============================================================================

def power(base: int | float, exponent: int) -> int | float:
    """
    Compute base raised to an integer exponent.

    Python's ** operator uses efficient exponentiation internally.
    For integer exponents, repeated multiplication is the mathematical
    definition, but an algorithm should avoid performing every multiplication
    when exponentiation by squaring can reduce the number of operations.
    """
    return base ** exponent


def fast_power(base: int, exponent: int) -> int:
    """
    Compute base^exponent using exponentiation by squaring.

    Time complexity:
        O(log exponent)

    Space complexity:
        O(1)

    This is important in DSA because the same technique is used for fast
    modular exponentiation.
    """
    if exponent < 0:
        raise ValueError("This implementation expects a non-negative exponent.")

    result = 1
    current = base
    remaining = exponent

    while remaining > 0:
        # If the current binary bit is 1, include this power of the base.
        if remaining & 1:
            result *= current

        # Squaring moves from b^(2^k) to b^(2^(k+1)).
        current *= current
        remaining >>= 1

    return result


def fast_power_mod(base: int, exponent: int, modulus: int) -> int:
    """
    Compute (base^exponent) mod modulus efficiently.

    This avoids constructing the potentially enormous value base^exponent.

    Time complexity:
        O(log exponent)

    This is a fundamental building block for modular arithmetic algorithms.
    """
    if exponent < 0:
        raise ValueError("Exponent must be non-negative.")
    if modulus <= 0:
        raise ValueError("Modulus must be positive.")

    result = 1 % modulus
    current = base % modulus
    remaining = exponent

    while remaining:
        if remaining & 1:
            result = (result * current) % modulus
        current = (current * current) % modulus
        remaining >>= 1

    return result


def demonstrate_powers() -> None:
    print_section("1. POWERS AND EXPONENTS")

    demonstrate("2^5", 2 ** 5)
    demonstrate("10^3", 10 ** 3)
    demonstrate("2^10 using fast power", fast_power(2, 10))
    demonstrate("3^13 using fast power", fast_power(3, 13))

    print_subsection("Exponent Laws")

    # a^m * a^n = a^(m+n)
    demonstrate("2^3 * 2^4", 2**3 * 2**4)
    demonstrate("2^(3+4)", 2**(3 + 4))

    # (a^m)^n = a^(mn)
    demonstrate("(2^3)^4", (2**3) ** 4)
    demonstrate("2^(3*4)", 2 ** (3 * 4))

    # a^0 = 1 for a != 0.
    demonstrate("17^0", 17**0)

    # Negative powers represent reciprocals.
    demonstrate("2^-3", 2**-3)

    print_subsection("Exponentiation by Squaring")

    for exponent in [0, 1, 2, 5, 10, 100]:
        expected = 2**exponent
        actual = fast_power(2, exponent)
        demonstrate(f"2^{exponent}", actual)
        assert actual == expected

    demonstrate("(2^100) mod 1_000_000_007", fast_power_mod(2, 100, 1_000_000_007))


# =============================================================================
# 2. LOGARITHMS
# =============================================================================

def logarithm(value: float, base: float = math.e) -> float:
    """
    Compute log_base(value).

    Conditions:
        value > 0
        base > 0
        base != 1
    """
    if value <= 0:
        raise ValueError("Logarithm input must be positive.")
    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and different from 1.")

    return math.log(value, base)


def integer_log_floor(value: int, base: int = 2) -> int:
    """
    Return floor(log_base(value)) for positive integers.

    Example:
        floor(log_2(17)) = 4

    Because 2^4 <= 17 < 2^5.

    This implementation avoids floating-point precision issues.
    """
    if value <= 0:
        raise ValueError("Value must be positive.")
    if base <= 1:
        raise ValueError("Base must be greater than 1.")

    result = 0
    current = 1

    while current * base <= value:
        current *= base
        result += 1

    return result


def demonstrate_logarithms() -> None:
    print_section("2. LOGARITHMS")

    demonstrate("log_2(8)", logarithm(8, 2))
    demonstrate("log_2(1024)", logarithm(1024, 2))
    demonstrate("log_10(1000)", logarithm(1000, 10))
    demonstrate("ln(e^5)", logarithm(math.exp(5), math.e))

    print_subsection("Integer Floor Logarithm")

    for value in [1, 2, 3, 4, 7, 8, 15, 16, 17, 31, 32]:
        demonstrate(f"floor(log_2({value}))", integer_log_floor(value, 2))

    print_subsection("Why Logarithms Appear in DSA")

    print("Binary search repeatedly halves a search interval.")
    print("After k halvings, the remaining size is approximately n / 2^k.")
    print("The process ends when n / 2^k <= 1, so 2^k >= n.")
    print("Therefore k >= log_2(n), giving O(log n) time.")

    print_subsection("Logarithm Identities")

    x = 64
    demonstrate("log_2(64)", math.log2(x))
    demonstrate("log_4(64)", math.log(64, 4))

    # Change-of-base formula:
    # log_b(x) = ln(x) / ln(b)
    demonstrate("ln(64) / ln(2)", math.log(64) / math.log(2))

    # Important observation:
    # log bases differ only by a constant factor, so O(log_2 n),
    # O(log_10 n), and O(ln n) are asymptotically equivalent.


# =============================================================================
# 3. FACTORIALS
# =============================================================================

def factorial_iterative(n: int) -> int:
    """
    Compute n! iteratively.

    n! = n * (n-1) * ... * 2 * 1

    By definition:
        0! = 1

    Iterative computation avoids recursion-depth limitations.
    """
    if n < 0:
        raise ValueError("Factorial is defined only for non-negative integers.")

    result = 1
    for value in range(2, n + 1):
        result *= value

    return result


def factorial_recursive(n: int) -> int:
    """
    Recursive factorial implementation.

    Educational recurrence:
        n! = n * (n-1)!
        0! = 1

    Complexity:
        Time: O(n)
        Auxiliary call stack: O(n)

    Python's math.factorial is generally preferable for production code.
    """
    if n < 0:
        raise ValueError("Factorial is defined only for non-negative integers.")
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)


def trailing_zeros_in_factorial(n: int) -> int:
    """
    Count trailing zeros in n!.

    A trailing zero is produced by a factor of 10 = 2 * 5.
    There are generally more factors of 2 than 5, so we count factors of 5.

    Formula:
        floor(n/5) + floor(n/25) + floor(n/125) + ...

    Complexity:
        O(log_5 n)
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    count = 0
    divisor = 5

    while divisor <= n:
        count += n // divisor
        divisor *= 5

    return count


def demonstrate_factorials() -> None:
    print_section("3. FACTORIALS")

    for n in range(0, 8):
        demonstrate(f"{n}!", factorial_iterative(n))

    print_subsection("Recursive Versus Iterative")

    for n in [0, 1, 5, 10]:
        assert factorial_iterative(n) == factorial_recursive(n)
        assert factorial_iterative(n) == math.factorial(n)
        demonstrate(f"{n}! verified", factorial_iterative(n))

    print_subsection("Trailing Zeros")

    for n in [5, 10, 20, 25, 50, 100]:
        demonstrate(f"Trailing zeros in {n}!", trailing_zeros_in_factorial(n))

    print_subsection("Factorial Growth")

    print("Factorials grow extremely quickly.")
    print("This is one reason direct factorial computation should not be used")
    print("when only a combination or permutation value is required.")


# =============================================================================
# 4. PERMUTATIONS
# =============================================================================

def permutation(n: int, r: int) -> int:
    """
    Compute nPr.

    nPr = n! / (n-r)!

    Direct factorial division works mathematically, but an iterative product
    avoids constructing the complete n! and (n-r)! separately.

    Conditions:
        0 <= r <= n
    """
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require n >= 0 and 0 <= r <= n.")

    result = 1

    for value in range(n - r + 1, n + 1):
        result *= value

    return result


def permutation_with_repetition(counts: Sequence[int]) -> int:
    """
    Count distinct permutations of a multiset.

    Formula:
        n! / (c1! * c2! * ... * ck!)

    Example:
        "LEVEL" has:
            L = 2
            E = 2
            V = 1

        Distinct permutations = 5! / (2! * 2! * 1!)
    """
    if any(count < 0 for count in counts):
        raise ValueError("Counts cannot be negative.")

    total = sum(counts)
    denominator = 1

    for count in counts:
        denominator *= factorial_iterative(count)

    return factorial_iterative(total) // denominator


def demonstrate_permutations() -> None:
    print_section("4. PERMUTATIONS")

    demonstrate("5P2", permutation(5, 2))
    demonstrate("5P3", permutation(5, 3))
    demonstrate("10P4", permutation(10, 4))

    print_subsection("Interpretation")

    print("nPr counts ordered selections of r objects from n distinct objects.")
    print("Order matters.")

    demonstrate("Arrangements of 3 people from 5", permutation(5, 3))
    demonstrate("Distinct permutations of LEVEL", permutation_with_repetition([2, 2, 1]))

    print_subsection("Permutation Versus Combination")

    demonstrate("5P3: order matters", permutation(5, 3))
    demonstrate("5C3: order does not matter", math.comb(5, 3))


# =============================================================================
# 5. COMBINATIONS
# =============================================================================

def combination_multiplicative(n: int, r: int) -> int:
    """
    Compute nCr using a multiplicative formula.

    nCr = n! / (r!(n-r)!)

    We exploit symmetry:
        nCr = nC(n-r)

    This reduces the number of iterations.
    """
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require n >= 0 and 0 <= r <= n.")

    r = min(r, n - r)

    result = 1

    for i in range(1, r + 1):
        # The division is exact at each step for this recurrence.
        result = result * (n - r + i) // i

    return result


def pascal_triangle(rows: int) -> List[List[int]]:
    """
    Generate Pascal's triangle.

    Each interior element is the sum of the two elements directly above it.

    Row n contains:
        nC0, nC1, ..., nCn

    Space complexity:
        O(rows^2) for storing the complete triangle.
    """
    if rows < 0:
        raise ValueError("rows must be non-negative.")

    triangle: List[List[int]] = []

    for row_index in range(rows):
        row = [1] * (row_index + 1)

        for column in range(1, row_index):
            row[column] = (
                triangle[row_index - 1][column - 1]
                + triangle[row_index - 1][column]
            )

        triangle.append(row)

    return triangle


def demonstrate_combinations() -> None:
    print_section("5. COMBINATIONS")

    for n, r in [(5, 2), (5, 3), (10, 4), (20, 10)]:
        actual = combination_multiplicative(n, r)
        expected = math.comb(n, r)
        assert actual == expected
        demonstrate(f"{n}C{r}", actual)

    print_subsection("Symmetry")

    demonstrate("10C3", combination_multiplicative(10, 3))
    demonstrate("10C7", combination_multiplicative(10, 7))

    print_subsection("Pascal's Triangle")

    triangle = pascal_triangle(7)

    for index, row in enumerate(triangle):
        print(f"Row {index}: {row}")

    print_subsection("Binomial Interpretation")

    # (a + b)^n = sum C(n,k) * a^(n-k) * b^k
    a = 2
    b = 3
    n = 4

    binomial_sum = sum(
        combination_multiplicative(n, k) * a ** (n - k) * b**k
        for k in range(n + 1)
    )

    demonstrate("(2 + 3)^4 via direct power", (a + b) ** n)
    demonstrate("(2 + 3)^4 via binomial theorem", binomial_sum)


# =============================================================================
# 6. SUMMATIONS
# =============================================================================

def arithmetic_sum(n: int) -> int:
    """
    Sum 1 + 2 + ... + n.

    Formula:
        n(n+1)/2

    Time complexity:
        O(1)
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    return n * (n + 1) // 2


def arithmetic_sum_range(first: int, last: int) -> int:
    """
    Sum an arithmetic sequence with difference 1.

    Formula:
        count * (first + last) / 2
    """
    if first > last:
        return 0

    count = last - first + 1
    return count * (first + last) // 2


def geometric_sum(first_term: int | float, ratio: int | float, n: int) -> float:
    """
    Compute:
        a + ar + ar^2 + ... + ar^(n-1)

    For r != 1:
        S_n = a(r^n - 1)/(r - 1)

    For r == 1:
        S_n = an
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    if n == 0:
        return 0

    if ratio == 1:
        return first_term * n

    return first_term * (ratio**n - 1) / (ratio - 1)


def geometric_sum_binary(n: int) -> int:
    """
    Compute:
        1 + 2 + 4 + ... + 2^n

    Closed form:
        2^(n+1) - 1
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    return 2 ** (n + 1) - 1


def nested_sum_operation_count(n: int) -> int:
    """
    Count iterations of:

        for i in range(n):
            for j in range(n):
                ...

    The count is n^2.

    This illustrates how nested loops often produce summations that lead
    directly to asymptotic complexity.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    return n * n


def triangular_nested_operation_count(n: int) -> int:
    """
    Count iterations of:

        for i in range(n):
            for j in range(i + 1):
                ...

    Count:
        1 + 2 + ... + n = n(n+1)/2

    Complexity:
        Theta(n^2)
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    return n * (n + 1) // 2


def harmonic_sum(n: int) -> float:
    """
    Compute H_n = 1 + 1/2 + ... + 1/n.

    There is no elementary exact closed form.

    H_n grows approximately as:
        ln(n) + gamma

    where gamma is Euler's constant.

    Time complexity:
        O(n)
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    return sum(1 / i for i in range(1, n + 1))


def demonstrate_summations() -> None:
    print_section("6. SUMMATIONS")

    demonstrate("1 + ... + 10", arithmetic_sum(10))
    demonstrate("1 + ... + 100", arithmetic_sum(100))
    demonstrate("20 + ... + 30", arithmetic_sum_range(20, 30))

    demonstrate("1 + 2 + 4 + ... + 2^10", geometric_sum(1, 2, 11))
    demonstrate("1 + 2 + 4 + ... + 2^10 closed form", geometric_sum_binary(10))

    demonstrate("Nested n x n operations, n=10", nested_sum_operation_count(10))
    demonstrate("Triangular nested operations, n=10", triangular_nested_operation_count(10))

    demonstrate("H_10", harmonic_sum(10))

    print_subsection("Common DSA Summations")

    print("1 + 2 + ... + n                = Theta(n^2) operations if each term costs Theta(n)")
    print("1 + 1 + ... + 1 (n terms)      = Theta(n)")
    print("1 + 2 + ... + n                = Theta(n^2)")
    print("1 + 2 + 4 + ... + 2^k          = Theta(2^k)")
    print("1 + 1/2 + 1/3 + ... + 1/n      = Theta(log n)")
    print("1 + 1/2 + 1/4 + ...             = O(1) when continued indefinitely")


# =============================================================================
# 7. MODULAR ARITHMETIC
# =============================================================================

def normalized_mod(value: int, modulus: int) -> int:
    """
    Return the canonical non-negative residue.

    Python's % already produces a non-negative result when modulus is positive.
    """
    if modulus <= 0:
        raise ValueError("Modulus must be positive.")

    return value % modulus


def modular_add(a: int, b: int, modulus: int) -> int:
    """Compute (a + b) mod modulus."""
    return (a + b) % modulus


def modular_subtract(a: int, b: int, modulus: int) -> int:
    """Compute (a - b) mod modulus."""
    return (a - b) % modulus


def modular_multiply(a: int, b: int, modulus: int) -> int:
    """Compute (a * b) mod modulus."""
    return (a * b) % modulus


def modular_power(a: int, exponent: int, modulus: int) -> int:
    """Compute a^exponent mod modulus using Python's efficient pow."""
    if exponent < 0:
        raise ValueError("Exponent must be non-negative.")
    if modulus <= 0:
        raise ValueError("Modulus must be positive.")

    return pow(a, exponent, modulus)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean algorithm.

    Returns (g, x, y) such that:
        g = gcd(a, b)
        ax + by = g

    The gcd is always non-negative.
    """
    if b == 0:
        g = abs(a)
        x = 1 if a >= 0 else -1
        return g, x, 0

    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1

    while r != 0:
        quotient = old_r // r

        old_r, r = r, old_r - quotient * r
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y

    if old_r < 0:
        return -old_r, -old_x, -old_y

    return old_r, old_x, old_y


def modular_inverse(a: int, modulus: int) -> int:
    """
    Find x such that:

        a*x ≡ 1 (mod modulus)

    The inverse exists exactly when:
        gcd(a, modulus) = 1

    Uses the extended Euclidean algorithm.
    """
    if modulus <= 1:
        raise ValueError("Modulus must be greater than 1.")

    gcd, x, _ = extended_gcd(a, modulus)

    if gcd != 1:
        raise ValueError(
            f"No modular inverse exists because gcd({a}, {modulus}) = {gcd}."
        )

    return x % modulus


def modular_divide(a: int, b: int, modulus: int) -> int:
    """
    Compute a / b modulo modulus.

    Division is not ordinary integer division.

    We require:
        gcd(b, modulus) = 1

    and calculate:
        a * b^(-1) mod modulus
    """
    inverse = modular_inverse(b, modulus)
    return (a * inverse) % modulus


def demonstrate_modular_arithmetic() -> None:
    print_section("7. MODULAR ARITHMETIC")

    modulus = 7

    demonstrate("(15 + 20) mod 7", modular_add(15, 20, modulus))
    demonstrate("(15 - 20) mod 7", modular_subtract(15, 20, modulus))
    demonstrate("(15 * 20) mod 7", modular_multiply(15, 20, modulus))
    demonstrate("15^20 mod 7", modular_power(15, 20, modulus))

    print_subsection("Congruence")

    print("a ≡ b (mod m) means m divides (a - b).")
    demonstrate("17 mod 5", 17 % 5)
    demonstrate("2 mod 5", 2 % 5)
    demonstrate("17 and 2 congruent modulo 5", 17 % 5 == 2 % 5)

    print_subsection("Modular Inverse")

    inverse = modular_inverse(3, 11)

    demonstrate("Inverse of 3 modulo 11", inverse)
    demonstrate("3 * inverse mod 11", (3 * inverse) % 11)

    print_subsection("Modular Division")

    demonstrate("10 / 3 modulo 11", modular_divide(10, 3, 11))
    demonstrate("10 * inverse(3) modulo 11", (10 * modular_inverse(3, 11)) % 11)

    print_subsection("Extended Euclidean Algorithm")

    gcd, x, y = extended_gcd(30, 18)
    demonstrate("gcd(30, 18)", gcd)
    demonstrate("Coefficient x", x)
    demonstrate("Coefficient y", y)
    demonstrate("30*x + 18*y", 30 * x + 18 * y)

    print_subsection("Negative Values")

    demonstrate("(-1) mod 7", (-1) % 7)
    demonstrate("(-15) mod 7", (-15) % 7)

    print_subsection("Important Warning")

    print("Do not assume a / b modulo m is equivalent to (a // b) % m.")
    print("Modular division requires a multiplicative inverse of b.")


# =============================================================================
# 8. GCD, LCM, PRIME NUMBERS, AND RELATED NUMBER THEORY
# =============================================================================

def gcd_iterative(a: int, b: int) -> int:
    """Compute the greatest common divisor using Euclid's algorithm."""
    a, b = abs(a), abs(b)

    while b:
        a, b = b, a % b

    return a


def lcm(a: int, b: int) -> int:
    """Compute least common multiple safely using gcd."""
    if a == 0 or b == 0:
        return 0

    return abs(a // gcd_iterative(a, b) * b)


def is_prime(n: int) -> bool:
    """
    Determine whether n is prime.

    Only divisors up to sqrt(n) need to be checked.

    Complexity:
        O(sqrt(n)) in the worst case.
    """
    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    divisor = 3

    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2

    return True


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Generate all primes <= limit.

    Time complexity:
        O(n log log n)

    Space complexity:
        O(n)
    """
    if limit < 2:
        return []

    is_prime_table = [True] * (limit + 1)
    is_prime_table[0] = False
    is_prime_table[1] = False

    prime = 2

    while prime * prime <= limit:
        if is_prime_table[prime]:
            for multiple in range(prime * prime, limit + 1, prime):
                is_prime_table[multiple] = False

        prime += 1

    return [
        number
        for number, prime_status in enumerate(is_prime_table)
        if prime_status
    ]


def demonstrate_number_theory() -> None:
    print_section("8. GCD, LCM, PRIMES, AND NUMBER THEORY")

    demonstrate("gcd(48, 18)", gcd_iterative(48, 18))
    demonstrate("lcm(12, 18)", lcm(12, 18))

    for number in [1, 2, 3, 4, 17, 25, 97, 100]:
        demonstrate(f"is_prime({number})", is_prime(number))

    demonstrate("Primes <= 50", sieve_of_eratosthenes(50))

    print_subsection("Euclidean Algorithm Principle")

    print("gcd(a, b) = gcd(b, a mod b)")
    print("This repeatedly reduces the second argument until the remainder is zero.")
    print("Its running time is logarithmic in the magnitude of the inputs.")


# =============================================================================
# 9. COUNTING PRINCIPLES
# =============================================================================

def multiplication_principle(counts: Sequence[int]) -> int:
    """
    If a process consists of independent stages with c1, c2, ..., ck choices,
    then the total number of outcomes is the product of those counts.
    """
    if any(count < 0 for count in counts):
        raise ValueError("Choice counts cannot be negative.")

    result = 1

    for count in counts:
        result *= count

    return result


def addition_principle(counts: Sequence[int]) -> int:
    """
    If mutually exclusive cases have c1, c2, ..., ck choices, total choices
    are the sum.

    This is valid when the cases do not overlap.
    """
    if any(count < 0 for count in counts):
        raise ValueError("Choice counts cannot be negative.")

    return sum(counts)


def demonstrate_counting_principles() -> None:
    print_section("9. COUNTING PRINCIPLES")

    print_subsection("Multiplication Principle")

    # 3 shirts, 2 trousers, 4 pairs of shoes.
    outfits = multiplication_principle([3, 2, 4])
    demonstrate("Possible outfits", outfits)

    print_subsection("Addition Principle")

    # Choose either one of 5 buses or one of 3 trains.
    transport_choices = addition_principle([5, 3])
    demonstrate("Transport choices when cases are exclusive", transport_choices)

    print_subsection("Inclusion-Exclusion")

    # |A union B| = |A| + |B| - |A intersection B|
    set_a = set(range(1, 11))
    set_b = set(range(5, 16))

    union_size = len(set_a) + len(set_b) - len(set_a & set_b)

    demonstrate("|A|", len(set_a))
    demonstrate("|B|", len(set_b))
    demonstrate("|A ∩ B|", len(set_a & set_b))
    demonstrate("|A ∪ B|", union_size)


# =============================================================================
# 10. BASIC PROBABILITY
# =============================================================================

def probability_of_favorable_outcomes(
    favorable: int,
    total: int,
) -> Fraction:
    """
    Compute probability when all elementary outcomes are equally likely.

    P(A) = favorable outcomes / total outcomes
    """
    if total <= 0:
        raise ValueError("Total number of outcomes must be positive.")
    if favorable < 0 or favorable > total:
        raise ValueError("Favorable outcomes must lie between 0 and total.")

    return Fraction(favorable, total)


def complement_probability(probability: Fraction) -> Fraction:
    """
    P(not A) = 1 - P(A)
    """
    if not 0 <= probability <= 1:
        raise ValueError("Probability must lie in [0, 1].")

    return 1 - probability


def conditional_probability(
    intersection: Fraction,
    condition: Fraction,
) -> Fraction:
    """
    P(A | B) = P(A ∩ B) / P(B)
    """
    if condition <= 0:
        raise ValueError("P(B) must be positive.")

    return intersection / condition


def bayes_theorem(
    p_b_given_a: Fraction,
    p_a: Fraction,
    p_b: Fraction,
) -> Fraction:
    """
    Bayes' theorem:

        P(A | B) = P(B | A) P(A) / P(B)
    """
    if p_b <= 0:
        raise ValueError("P(B) must be positive.")

    return p_b_given_a * p_a / p_b


def binomial_probability(
    n: int,
    k: int,
    p: Fraction | float,
) -> Fraction | float:
    """
    Probability of exactly k successes in n independent Bernoulli trials.

        P(X=k) = C(n,k) p^k (1-p)^(n-k)

    p may be a Fraction for exact arithmetic or float for convenience.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")
    if k < 0 or k > n:
        return Fraction(0, 1) if isinstance(p, Fraction) else 0.0
    if not 0 <= p <= 1:
        raise ValueError("p must lie between 0 and 1.")

    coefficient = combination_multiplicative(n, k)
    return coefficient * p**k * (1 - p) ** (n - k)


def expected_value(values: Sequence[float], probabilities: Sequence[float]) -> float:
    """
    Compute E[X] = sum(x_i * p_i).

    Probabilities must sum to approximately 1.
    """
    if len(values) != len(probabilities):
        raise ValueError("Values and probabilities must have equal length.")

    if any(p < 0 for p in probabilities):
        raise ValueError("Probabilities cannot be negative.")

    total_probability = sum(probabilities)

    if not math.isclose(total_probability, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("Probabilities must sum to 1.")

    return sum(value * probability for value, probability in zip(values, probabilities))


def variance(values: Sequence[float], probabilities: Sequence[float]) -> float:
    """Compute the population variance of a discrete random variable."""
    mean = expected_value(values, probabilities)
    return sum(
        probability * (value - mean) ** 2
        for value, probability in zip(values, probabilities)
    )


def demonstrate_probability() -> None:
    print_section("10. BASIC PROBABILITY")

    print_subsection("Classical Probability")

    die_probability = probability_of_favorable_outcomes(3, 6)

    demonstrate("P(rolling an even number)", die_probability)
    demonstrate("P(rolling an odd number)", complement_probability(die_probability))

    print_subsection("Conditional Probability")

    # Example:
    # P(A ∩ B) = 1/6
    # P(B) = 1/2
    # P(A | B) = (1/6)/(1/2) = 1/3
    p_intersection = Fraction(1, 6)
    p_condition = Fraction(1, 2)

    conditional = conditional_probability(p_intersection, p_condition)

    demonstrate("P(A ∩ B)", p_intersection)
    demonstrate("P(B)", p_condition)
    demonstrate("P(A | B)", conditional)

    print_subsection("Bayes' Theorem")

    p_disease = Fraction(1, 100)
    p_positive_given_disease = Fraction(95, 100)
    p_positive = Fraction(995, 10000)

    posterior = bayes_theorem(
        p_positive_given_disease,
        p_disease,
        p_positive,
    )

    demonstrate("P(disease)", p_disease)
    demonstrate("P(positive | disease)", p_positive_given_disease)
    demonstrate("P(disease | positive)", posterior)

    print_subsection("Binomial Probability")

    # Probability of exactly 3 heads in 5 fair coin tosses.
    p_exactly_three_heads = binomial_probability(5, 3, Fraction(1, 2))

    demonstrate("P(exactly 3 heads in 5 fair tosses)", p_exactly_three_heads)

    print_subsection("Expected Value and Variance")

    dice_values = [1, 2, 3, 4, 5, 6]
    dice_probabilities = [1 / 6] * 6

    mean = expected_value(dice_values, dice_probabilities)
    var = variance(dice_values, dice_probabilities)

    demonstrate("Expected value of a fair die", mean)
    demonstrate("Variance of a fair die", var)


# =============================================================================
# 11. RANDOM SIMULATION
# =============================================================================

def simulate_coin_tosses(
    trials: int,
    probability_of_heads: float = 0.5,
    seed: int = 42,
) -> Tuple[int, float]:
    """
    Simulate Bernoulli trials.

    Returns:
        number of heads
        observed proportion of heads

    A fixed seed makes the demonstration reproducible.
    """
    if trials <= 0:
        raise ValueError("trials must be positive.")
    if not 0 <= probability_of_heads <= 1:
        raise ValueError("Probability must lie in [0, 1].")

    generator = random.Random(seed)
    heads = sum(
        generator.random() < probability_of_heads
        for _ in range(trials)
    )

    return heads, heads / trials


def demonstrate_probability_simulation() -> None:
    print_section("11. PROBABILITY SIMULATION")

    for trials in [10, 100, 1_000, 10_000]:
        heads, observed = simulate_coin_tosses(trials)

        demonstrate(
            f"Heads after {trials} tosses",
            f"{heads}, observed proportion={observed:.4f}",
        )

    print("As the number of independent trials increases, the observed")
    print("frequency tends to approach the underlying probability.")


# =============================================================================
# 12. FACTORIAL-BASED COMBINATORICS WITH EXACT ARITHMETIC
# =============================================================================

def multinomial_coefficient(counts: Sequence[int]) -> int:
    """
    Compute the multinomial coefficient:

        (n1 + n2 + ... + nk)! / (n1! n2! ... nk!)

    It counts ways to arrange a multiset with the specified multiplicities.
    """
    if any(count < 0 for count in counts):
        raise ValueError("Counts cannot be negative.")

    total = sum(counts)
    result = factorial_iterative(total)

    for count in counts:
        result //= factorial_iterative(count)

    return result


def number_of_binary_strings_with_k_ones(length: int, ones: int) -> int:
    """
    A binary string of length n with exactly k ones is determined by choosing
    the k positions occupied by ones.

    Answer:
        C(n, k)
    """
    if length < 0:
        raise ValueError("length must be non-negative.")
    if ones < 0 or ones > length:
        return 0

    return combination_multiplicative(length, ones)


def demonstrate_advanced_counting() -> None:
    print_section("12. ADVANCED COUNTING")

    demonstrate(
        "Multinomial coefficient for [2,3,1]",
        multinomial_coefficient([2, 3, 1]),
    )

    demonstrate(
        "Binary strings of length 8 with exactly 3 ones",
        number_of_binary_strings_with_k_ones(8, 3),
    )

    print_subsection("Bit Strings")

    print("There are 2^n binary strings of length n.")

    for n in range(0, 7):
        demonstrate(f"Binary strings of length {n}", 2**n)


# =============================================================================
# 13. MODULAR COMBINATIONS
# =============================================================================

def factorial_mod(n: int, modulus: int) -> int:
    """Compute n! modulo modulus."""
    if n < 0:
        raise ValueError("n must be non-negative.")
    if modulus <= 0:
        raise ValueError("modulus must be positive.")

    result = 1

    for value in range(2, n + 1):
        result = result * value % modulus

    return result


def combination_mod_prime(n: int, r: int, prime_modulus: int) -> int:
    """
    Compute nCr modulo a prime modulus.

    Fermat's little theorem:
        a^(p-1) ≡ 1 (mod p)
    for p prime and p does not divide a.

    Therefore:
        a^(-1) ≡ a^(p-2) (mod p)

    This implementation assumes:
        0 <= r <= n < prime_modulus
        prime_modulus is prime

    It is suitable for the common competitive-programming case where the
    modulus is a large prime such as 1,000,000,007.
    """
    if n < 0 or r < 0 or r > n:
        return 0

    if prime_modulus <= 1:
        raise ValueError("Modulus must be greater than 1.")

    if n >= prime_modulus:
        raise ValueError(
            "This simple factorial-inverse method requires n < prime_modulus."
        )

    r = min(r, n - r)

    numerator = 1
    denominator = 1

    for i in range(1, r + 1):
        numerator = numerator * (n - r + i) % prime_modulus
        denominator = denominator * i % prime_modulus

    inverse_denominator = pow(denominator, prime_modulus - 2, prime_modulus)

    return numerator * inverse_denominator % prime_modulus


def demonstrate_modular_combinations() -> None:
    print_section("13. MODULAR COMBINATIONS")

    prime_modulus = 1_000_000_007

    demonstrate(
        "100C50 exactly",
        combination_multiplicative(100, 50),
    )

    demonstrate(
        "100C50 modulo 1,000,000,007",
        combination_mod_prime(100, 50, prime_modulus),
    )

    demonstrate(
        "1000C500 modulo 1,000,000,007",
        combination_mod_prime(1000, 500, prime_modulus),
    )

    print_subsection("Why Modulo Matters")

    print("Combinatorial values become enormous very quickly.")
    print("Many DSA problems ask for an answer modulo a fixed integer.")
    print("Modular arithmetic keeps intermediate values manageable.")
    print("The exact method depends on the modulus and constraints.")


# =============================================================================
# 14. FIBONACCI AND RECURRENCE CONNECTIONS
# =============================================================================

def fibonacci_iterative(n: int) -> int:
    """
    Compute the nth Fibonacci number.

    F(0) = 0
    F(1) = 1
    F(n) = F(n-1) + F(n-2)

    Time: O(n)
    Space: O(1)
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    previous, current = 0, 1

    for _ in range(n):
        previous, current = current, previous + current

    return previous


def fibonacci_fast_doubling(n: int) -> int:
    """
    Compute Fibonacci numbers in O(log n) arithmetic steps using fast doubling.

    Identities:
        F(2k)   = F(k) * [2F(k+1) - F(k)]
        F(2k+1) = F(k)^2 + F(k+1)^2

    This demonstrates how logarithmic recursion and algebraic identities can
    improve an apparently linear recurrence.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    def pair(index: int) -> Tuple[int, int]:
        if index == 0:
            return 0, 1

        a, b = pair(index // 2)

        c = a * (2 * b - a)
        d = a * a + b * b

        if index % 2 == 0:
            return c, d

        return d, c + d

    return pair(n)[0]


def demonstrate_recurrences() -> None:
    print_section("14. RECURRENCES AND FIBONACCI")

    for n in range(11):
        iterative = fibonacci_iterative(n)
        fast = fibonacci_fast_doubling(n)

        assert iterative == fast

        demonstrate(f"F({n})", iterative)

    print_subsection("Growth")

    print("Fibonacci numbers grow exponentially in n.")
    print("A direct naive recursive implementation has exponential time.")
    print("Memoization reduces it to O(n).")
    print("Fast doubling reduces the number of arithmetic steps to O(log n).")


# =============================================================================
# 15. ASYMPTOTIC GROWTH COMPARISON
# =============================================================================

def growth_values(n: int) -> dict[str, float]:
    """
    Return representative growth functions for comparison.

    These are not all integer-valued because logarithms and roots can be real.
    """
    if n <= 0:
        raise ValueError("n must be positive.")

    return {
        "1": 1,
        "log2(n)": math.log2(n),
        "sqrt(n)": math.sqrt(n),
        "n": n,
        "n log2(n)": n * math.log2(n),
        "n^2": n**2,
        "n^3": n**3,
        "2^n": 2**n,
    }


def demonstrate_growth_rates() -> None:
    print_section("15. ASYMPTOTIC GROWTH")

    n = 20

    for name, value in growth_values(n).items():
        demonstrate(name, value)

    print_subsection("Typical Ordering")

    print("For sufficiently large n:")
    print("1 < log n < sqrt(n) < n < n log n < n^2 < n^3 < 2^n")
    print("This ordering explains why polynomial and logarithmic algorithms")
    print("are generally preferred over exponential algorithms for large inputs.")


# =============================================================================
# 16. BINARY SEARCH AS A LOGARITHMIC EXAMPLE
# =============================================================================

def binary_search(sorted_values: Sequence[int], target: int) -> int:
    """
    Find target in a sorted sequence.

    Returns:
        index of target, or -1 if absent.

    Each iteration approximately halves the search interval.

    Time:
        O(log n)

    Space:
        O(1)
    """
    left = 0
    right = len(sorted_values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if sorted_values[middle] == target:
            return middle

        if sorted_values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_binary_search() -> None:
    print_section("16. BINARY SEARCH")

    values = [2, 4, 7, 11, 16, 21, 29, 35, 42]

    for target in [2, 16, 42, 10]:
        demonstrate(
            f"binary_search(target={target})",
            binary_search(values, target),
        )

    print("The logarithm comes from repeatedly reducing the candidate range by")
    print("approximately a factor of two.")


# =============================================================================
# 17. BIT OPERATIONS AND POWERS OF TWO
# =============================================================================

def is_power_of_two(n: int) -> bool:
    """
    Determine whether n is a positive power of two.

    For n > 0:
        n & (n - 1) == 0

    because a power of two has exactly one set bit.
    """
    return n > 0 and (n & (n - 1)) == 0


def next_power_of_two(n: int) -> int:
    """
    Return the smallest power of two >= n.

    This is useful for capacity sizing and divide-and-conquer structures.
    """
    if n <= 0:
        raise ValueError("n must be positive.")

    if is_power_of_two(n):
        return n

    power_value = 1

    while power_value < n:
        power_value <<= 1

    return power_value


def demonstrate_powers_of_two() -> None:
    print_section("17. POWERS OF TWO AND BIT OPERATIONS")

    for value in [1, 2, 3, 4, 7, 8, 15, 16, 17]:
        demonstrate(f"is_power_of_two({value})", is_power_of_two(value))
        demonstrate(f"next_power_of_two({value})", next_power_of_two(value))


# =============================================================================
# 18. EDGE CASES AND EXCEPTIONS
# =============================================================================

def demonstrate_edge_cases() -> None:
    print_section("18. EDGE CASES AND EXCEPTIONS")

    print_subsection("Factorial")

    for invalid in [-1, -5]:
        try:
            factorial_iterative(invalid)
        except ValueError as error:
            demonstrate(f"factorial({invalid}) error", error)

    print_subsection("Combinations")

    for n, r in [(5, 6), (5, -1), (-1, 2)]:
        try:
            combination_multiplicative(n, r)
        except ValueError as error:
            demonstrate(f"combination({n}, {r}) error", error)

    print_subsection("Logarithms")

    for value, base in [(0, 2), (-1, 2), (10, 1), (10, -2)]:
        try:
            logarithm(value, base)
        except ValueError as error:
            demonstrate(f"log_{base}({value}) error", error)

    print_subsection("Modular Inverse")

    try:
        modular_inverse(6, 15)
    except ValueError as error:
        demonstrate("inverse(6, 15) error", error)

    print_subsection("Probability")

    try:
        probability_of_favorable_outcomes(7, 6)
    except ValueError as error:
        demonstrate("Invalid probability error", error)


# =============================================================================
# 19. EXACT VERSUS FLOATING-POINT ARITHMETIC
# =============================================================================

def demonstrate_exact_arithmetic() -> None:
    print_section("19. EXACT VERSUS FLOATING-POINT ARITHMETIC")

    floating_result = 0.1 + 0.2
    exact_result = Fraction(1, 10) + Fraction(2, 10)

    demonstrate("0.1 + 0.2 using float", floating_result)
    demonstrate("1/10 + 2/10 using Fraction", exact_result)

    print("Floating-point values are approximations in binary.")
    print("Fractions are useful when exact rational probability is required.")

    probability = Fraction(1, 6)

    demonstrate("Exact 1/6", probability)
    demonstrate("Decimal approximation of 1/6", float(probability))


# =============================================================================
# 20. COMPLEXITY OF COMMON MATHEMATICAL OPERATIONS
# =============================================================================

def complexity_reference() -> List[Tuple[str, str, str]]:
    """
    Return a compact complexity reference.

    Complexity can depend on whether arithmetic operations themselves are
    considered constant-time. For very large integers, multiplication and
    division are not O(1) in terms of bit length.
    """
    return [
        ("Addition of fixed-size integers", "O(1)", "Arithmetic model"),
        ("Euclidean GCD", "O(log min(a,b))", "Arithmetic operations"),
        ("Fast exponentiation", "O(log exponent)", "Multiplication count"),
        ("Factorial iterative", "O(n)", "Arithmetic operations"),
        ("Naive factorial recursion", "O(n)", "Calls"),
        ("Binary search", "O(log n)", "Comparisons"),
        ("Sieve of Eratosthenes", "O(n log log n)", "Composite marking"),
        ("Arithmetic series formula", "O(1)", "Fixed-size arithmetic model"),
        ("Combination multiplicative", "O(min(r,n-r))", "Arithmetic steps"),
    ]


def demonstrate_complexity_reference() -> None:
    print_section("20. COMPLEXITY REFERENCE")

    for operation, complexity, basis in complexity_reference():
        print(f"{operation:<35} {complexity:<25} {basis}")


# =============================================================================
# 21. DSA APPLICATION: COUNTING PATHS IN A GRID
# =============================================================================

def grid_paths_combinatorial(rows: int, columns: int) -> int:
    """
    Count paths from the top-left to bottom-right of a rows x columns grid
    when movement is restricted to right and down.

    Number of moves:
        (rows - 1) down
        (columns - 1) right

    Total moves:
        rows + columns - 2

    Choose which moves are down:

        C(rows + columns - 2, rows - 1)
    """
    if rows <= 0 or columns <= 0:
        raise ValueError("Grid dimensions must be positive.")

    return combination_multiplicative(
        rows + columns - 2,
        rows - 1,
    )


def demonstrate_grid_paths() -> None:
    print_section("21. GRID PATHS AND COMBINATIONS")

    for rows, columns in [(1, 1), (2, 2), (3, 3), (3, 4), (5, 5)]:
        demonstrate(
            f"Paths in {rows}x{columns} grid",
            grid_paths_combinatorial(rows, columns),
        )

    print("A seemingly algorithmic grid-counting problem can reduce to a")
    print("combination once its structural constraints are recognized.")


# =============================================================================
# 22. DSA APPLICATION: SUBSETS AND SUBSEQUENCES
# =============================================================================

def count_subsets(n: int) -> int:
    """
    Every element has two choices:
        include
        exclude

    Therefore there are 2^n subsets.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    return 2**n


def count_nonempty_subsets(n: int) -> int:
    """There are 2^n - 1 non-empty subsets."""
    return count_subsets(n) - 1


def demonstrate_subsets() -> None:
    print_section("22. SUBSETS AND SUBSEQUENCES")

    for n in range(0, 8):
        demonstrate(f"Subsets of n={n}", count_subsets(n))

    demonstrate("Non-empty subsets for n=5", count_nonempty_subsets(5))

    print("The exponential 2^n growth explains why exhaustive subset enumeration")
    print("becomes impractical quickly and motivates dynamic programming,")
    print("meet-in-the-middle, pruning, greedy reasoning, or other techniques.")


# =============================================================================
# 23. DSA APPLICATION: PROBABILITY OF COLLISIONS
# =============================================================================

def birthday_collision_probability(group_size: int, days: int = 365) -> float:
    """
    Probability that at least two people share a birthday, assuming:

        * days are equally likely
        * birthdays are independent
        * leap years are ignored

    Complement approach:

        P(no collision) =
            365/365 * 364/365 * ... * (365-n+1)/365

        P(collision) = 1 - P(no collision)
    """
    if group_size < 0:
        raise ValueError("group_size must be non-negative.")
    if days <= 0:
        raise ValueError("days must be positive.")

    if group_size <= 1:
        return 0.0

    if group_size > days:
        return 1.0

    no_collision = 1.0

    for person in range(group_size):
        no_collision *= (days - person) / days

    return 1 - no_collision


def demonstrate_birthday_problem() -> None:
    print_section("23. BIRTHDAY COLLISION PROBABILITY")

    for group_size in [10, 20, 23, 30, 50]:
        probability = birthday_collision_probability(group_size)
        demonstrate(
            f"Collision probability for {group_size} people",
            f"{probability:.6f}",
        )

    print("The calculation illustrates how counting and probability interact.")
    print("The complement event is usually easier to count than the collision event.")


# =============================================================================
# 24. DSA APPLICATION: CATALAN NUMBERS
# =============================================================================

def catalan_number(n: int) -> int:
    """
    Compute the nth Catalan number.

    Closed form:
        C_n = (1 / (n+1)) * C(2n, n)

    Catalan numbers count many structures, including:
        * valid parenthesis sequences
        * binary search tree shapes
        * ways to triangulate a polygon
        * certain lattice paths

    This implementation uses exact integer arithmetic.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    return combination_multiplicative(2 * n, n) // (n + 1)


def demonstrate_catalan_numbers() -> None:
    print_section("24. CATALAN NUMBERS")

    for n in range(10):
        demonstrate(f"Catalan({n})", catalan_number(n))

    print("Catalan numbers are a useful example of how combinations lead to")
    print("important counting sequences in data structures and algorithms.")


# =============================================================================
# 25. DSA APPLICATION: INCLUSION-EXCLUSION
# =============================================================================

def count_multiples_in_range(
    n: int,
    divisors: Sequence[int],
) -> int:
    """
    Count positive integers <= n divisible by at least one divisor.

    Inclusion-exclusion is used.

    For a set of divisors d1, d2, ...:
        count multiples of di       -> add
        count multiples of di*dj   -> subtract
        count multiples of 3 terms -> add
        ...

    Least common multiples are required when divisors are not pairwise coprime.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    clean_divisors = sorted(set(abs(d) for d in divisors if d != 0))

    if not clean_divisors:
        return 0

    result = 0
    divisor_count = len(clean_divisors)

    for mask in range(1, 1 << divisor_count):
        current_lcm = 1
        selected = 0

        for index, divisor in enumerate(clean_divisors):
            if mask & (1 << index):
                selected += 1
                current_lcm = lcm(current_lcm, divisor)

                if current_lcm > n:
                    break
        else:
            contribution = n // current_lcm

            if selected % 2 == 1:
                result += contribution
            else:
                result -= contribution

    return result


def demonstrate_inclusion_exclusion() -> None:
    print_section("25. INCLUSION-EXCLUSION IN DSA")

    demonstrate(
        "Numbers <= 100 divisible by 3 or 5",
        count_multiples_in_range(100, [3, 5]),
    )

    demonstrate(
        "Numbers <= 100 divisible by 2, 3, or 5",
        count_multiples_in_range(100, [2, 3, 5]),
    )

    print("Inclusion-exclusion prevents double-counting when categories overlap.")


# =============================================================================
# 26. MATHEMATICAL IDENTITIES USED IN DSA
# =============================================================================

def verify_core_identities() -> None:
    print_section("26. CORE IDENTITIES USED IN DSA")

    n = 20

    # Sum of first n positive integers.
    lhs = sum(range(1, n + 1))
    rhs = n * (n + 1) // 2

    assert lhs == rhs
    demonstrate("Sum identity verified", lhs)

    # Sum of first n odd integers = n^2.
    odd_sum = sum(2 * k - 1 for k in range(1, n + 1))
    assert odd_sum == n**2
    demonstrate("Sum of first n odd integers", odd_sum)

    # Sum of first n even integers = n(n+1).
    even_sum = sum(2 * k for k in range(1, n + 1))
    assert even_sum == n * (n + 1)
    demonstrate("Sum of first n even integers", even_sum)

    # Combination symmetry.
    assert combination_multiplicative(n, 7) == combination_multiplicative(n, n - 7)
    demonstrate("Combination symmetry C(n,r)=C(n,n-r)", True)

    # Pascal recurrence.
    assert (
        combination_multiplicative(10, 5)
        == combination_multiplicative(9, 4)
        + combination_multiplicative(9, 5)
    )
    demonstrate("Pascal recurrence verified", True)


# =============================================================================
# 27. PROPERTY-BASED STYLE CHECKS WITHOUT EXTERNAL PACKAGES
# =============================================================================

def run_mathematical_invariants() -> None:
    """
    Run deterministic invariant checks.

    These are useful because mathematical functions have strong properties
    that can be tested independently of specific examples.
    """
    print_section("27. MATHEMATICAL INVARIANTS AND TESTS")

    for n in range(0, 15):
        assert factorial_iterative(n) == math.factorial(n)

    for n in range(0, 20):
        for r in range(0, n + 1):
            value = combination_multiplicative(n, r)

            assert value == math.comb(n, r)
            assert value == combination_multiplicative(n, n - r)

    for n in range(1, 100):
        assert arithmetic_sum(n) == sum(range(1, n + 1))

    for a in range(-10, 11):
        for b in range(-10, 11):
            assert gcd_iterative(a, b) == math.gcd(a, b)

    for n in range(0, 50):
        assert fibonacci_iterative(n) == fibonacci_fast_doubling(n)

    print("All deterministic mathematical invariants passed.")


# =============================================================================
# 28. LARGE INTEGER CONSIDERATIONS
# =============================================================================

def demonstrate_large_integer_behavior() -> None:
    print_section("28. LARGE INTEGER CONSIDERATIONS")

    print("Python integers have arbitrary precision, so integer overflow is")
    print("not the same concern it is in fixed-width languages such as C/C++.")
    print("The cost of arithmetic still grows as integers become wider.")

    for n in [10, 50, 100, 500]:
        value = factorial_iterative(n)
        digits = len(str(value))

        demonstrate(f"Digits in {n}!", digits)

    print_subsection("Important Distinction")

    print("O(1) arithmetic is often assumed in introductory complexity analysis.")
    print("For huge integers, addition, multiplication, division, and modulo")
    print("have costs dependent on operand bit lengths.")
    print("Thus algorithmic complexity can be expressed more precisely in a")
    print("bit-complexity model when numerical values become extremely large.")


# =============================================================================
# 29. NUMERICAL AND IMPLEMENTATION PITFALLS
# =============================================================================

def demonstrate_common_mistakes() -> None:
    print_section("29. COMMON MISTAKES")

    print("Mistake 1: Confusing permutations with combinations.")
    demonstrate("5P2", permutation(5, 2))
    demonstrate("5C2", combination_multiplicative(5, 2))

    print("\nMistake 2: Computing huge factorials unnecessarily.")
    demonstrate("20!", factorial_iterative(20))
    demonstrate("20C10 directly", combination_multiplicative(20, 10))

    print("\nMistake 3: Using floating-point logarithms for exact integer decisions.")
    demonstrate("floor(log2(1024))", integer_log_floor(1024, 2))

    print("\nMistake 4: Performing modular division with //.")
    print("Correct modular division requires a multiplicative inverse.")

    print("\nMistake 5: Forgetting that probability values must be in [0,1].")

    print("\nMistake 6: Ignoring overlap when adding category counts.")
    print("Use inclusion-exclusion when events or sets overlap.")

    print("\nMistake 7: Assuming every modulus has an inverse for every number.")
    print("a has an inverse modulo m exactly when gcd(a,m)=1.")


# =============================================================================
# 30. PRACTICAL DSA REFERENCE TABLE
# =============================================================================

def print_dsa_reference_table() -> None:
    print_section("30. DSA MATHEMATICAL REFERENCE")

    rows = [
        ("Power", "a^b", "Fast exponentiation"),
        ("Logarithm", "log_b(n)", "Binary search, balanced trees"),
        ("Factorial", "n!", "Permutations and combinatorics"),
        ("Permutation", "nPr", "Ordered arrangements"),
        ("Combination", "nCr", "Unordered selections"),
        ("Arithmetic sum", "n(n+1)/2", "Loop counting"),
        ("Geometric sum", "a(r^n-1)/(r-1)", "Recursive growth"),
        ("GCD", "gcd(a,b)", "Number theory, modular arithmetic"),
        ("LCM", "|ab|/gcd(a,b)", "Scheduling and cycles"),
        ("Modulo", "a mod m", "Hashing, cyclic behavior"),
        ("Modular inverse", "a^-1 mod m", "Modular division"),
        ("Probability", "favorable/total", "Randomized algorithms"),
        ("Expected value", "Σ xP(x)", "Expected cost and analysis"),
        ("Inclusion-exclusion", "Σ(-1)^(k+1)|intersections|", "Overlapping counts"),
        ("Powers of two", "2^n", "Subsets, bitmasks"),
        ("Catalan", "C(2n,n)/(n+1)", "Trees and valid structures"),
    ]

    print(f"{'Concept':<24} {'Formula':<35} {'Typical DSA use'}")
    print("-" * 90)

    for concept, formula, use in rows:
        print(f"{concept:<24} {formula:<35} {use}")


# =============================================================================
# 31. INTEGRATED EXAMPLE: COMBINATORICS + MODULO
# =============================================================================

def count_k_element_subsets_mod(
    n: int,
    k: int,
    modulus: int,
) -> int:
    """
    Count k-element subsets of n elements modulo modulus.

    For a general modulus, the safest simple educational approach is to compute
    the exact combination and then reduce it.

    For large n, this may be infeasible because the exact combination itself
    can be enormous. A production algorithm must select a modular technique
    appropriate to the modulus and constraints.
    """
    return combination_multiplicative(n, k) % modulus


def demonstrate_integrated_example() -> None:
    print_section("31. INTEGRATED DSA EXAMPLE")

    n = 50
    k = 6
    modulus = 1_000_000_007

    exact = combination_multiplicative(n, k)
    modular = count_k_element_subsets_mod(n, k, modulus)

    demonstrate("Exact number of 6-element subsets of 50", exact)
    demonstrate("Same value modulo 1,000,000,007", modular)

    print("The mathematical model identifies the answer as C(50,6).")
    print("The implementation then chooses an appropriate numerical representation.")


# =============================================================================
# 32. MINI PRACTICE EXAMPLES
# =============================================================================

def mini_practice() -> None:
    print_section("32. MINI PRACTICE EXAMPLES")

    print_subsection("Problem 1: Number of ways to select a team")

    people = 12
    team_size = 4

    demonstrate(
        f"Choose {team_size} people from {people}",
        combination_multiplicative(people, team_size),
    )

    print_subsection("Problem 2: Number of ordered passwords")

    # Four distinct digits selected without repetition.
    demonstrate(
        "4-digit ordered selection from 10 digits",
        permutation(10, 4),
    )

    print_subsection("Problem 3: Number of binary strings")

    length = 10
    demonstrate(
        f"Binary strings of length {length}",
        2**length,
    )

    print_subsection("Problem 4: Exact number of heads")

    probability = binomial_probability(10, 7, Fraction(1, 2))

    demonstrate(
        "Exactly 7 heads in 10 fair tosses",
        probability,
    )

    print_subsection("Problem 5: Grid paths")

    demonstrate(
        "Paths in a 4x5 grid",
        grid_paths_combinatorial(4, 5),
    )

    print_subsection("Problem 6: Divisibility")

    demonstrate(
        "Numbers <= 100 divisible by 4 or 6",
        count_multiples_in_range(100, [4, 6]),
    )


# =============================================================================
# 33. MAIN PROGRAM
# =============================================================================

def main() -> None:
    """
    Run the complete mathematical foundations tutorial.

    The order progresses from elementary numerical concepts to combinatorics,
    modular arithmetic, probability, asymptotic analysis, and DSA applications.
    """
    demonstrate_powers()
    demonstrate_logarithms()
    demonstrate_factorials()
    demonstrate_permutations()
    demonstrate_combinations()
    demonstrate_summations()
    demonstrate_modular_arithmetic()
    demonstrate_number_theory()
    demonstrate_counting_principles()
    demonstrate_probability()
    demonstrate_probability_simulation()
    demonstrate_advanced_counting()
    demonstrate_modular_combinations()
    demonstrate_recurrences()
    demonstrate_growth_rates()
    demonstrate_binary_search()
    demonstrate_powers_of_two()
    demonstrate_edge_cases()
    demonstrate_exact_arithmetic()
    demonstrate_complexity_reference()
    demonstrate_grid_paths()
    demonstrate_subsets()
    demonstrate_birthday_problem()
    demonstrate_catalan_numbers()
    demonstrate_inclusion_exclusion()
    verify_core_identities()
    run_mathematical_invariants()
    demonstrate_large_integer_behavior()
    demonstrate_common_mistakes()
    print_dsa_reference_table()
    demonstrate_integrated_example()
    mini_practice()

    print_section("END OF TUTORIAL")
    print("All demonstrations completed successfully.")


if __name__ == "__main__":
    main()
