# ============================================================
# DAY 00: PROGRAMMING FUNDAMENTALS
# ============================================================

# Programming is the process of giving instructions to a computer.
# Python executes these instructions step by step.


# ============================================================
# 1. DISPLAYING OUTPUT
# ============================================================

print("DAY 01 - PROGRAMMING FUNDAMENTALS")

print("\nWelcome to the Programming Fundamentals Learning Journey.")

print("\nProgramming is the process of writing instructions")
print("that tell a computer what to do.")


# ============================================================
# 2. COMMENTS
# ============================================================

# Comments are used to explain code.
# Python ignores comments while running the program.

print("\n2. COMMENTS")
print("Comments help programmers understand and explain code.")


# ============================================================
# 3. VARIABLES
# ============================================================

print("\n3. VARIABLES")

# A variable stores information.

name = "Atul"
age = 33

print("Name:", name)
print("Age:", age)


# ============================================================
# 4. BASIC DATA TYPES
# ============================================================

print("\n4. BASIC DATA TYPES")

# String
course = "Programming Fundamentals"

# Integer
day = 1

# Float
progress = 10.5

# Boolean
learning = True

print("Course:", course)
print("Day:", day)
print("Progress:", progress)
print("Learning:", learning)


# ============================================================
# 5. CHECKING DATA TYPES
# ============================================================

print("\n5. CHECKING DATA TYPES")

print("Type of course:", type(course))
print("Type of day:", type(day))
print("Type of progress:", type(progress))
print("Type of learning:", type(learning))


# ============================================================
# 6. ARITHMETIC OPERATORS
# ============================================================

print("\n6. ARITHMETIC OPERATORS")

a = 10
b = 5

print("a =", a)
print("b =", b)

print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
print("Floor Division:", a // b)
print("Remainder:", a % b)
print("Power:", a ** b)


# ============================================================
# 7. STRING OPERATIONS
# ============================================================

print("\n7. STRING OPERATIONS")

first_name = "Atul"
last_name = "Pandey"

full_name = first_name + " " + last_name

print("Full Name:", full_name)

print("Uppercase:", full_name.upper())
print("Lowercase:", full_name.lower())

print("Number of characters:", len(full_name))


# ============================================================
# 8. TAKING USER INPUT
# ============================================================

print("\n8. USER INPUT")

user_name = input("Enter your name: ")

print("Hello,", user_name)
print("Welcome to Programming Fundamentals!")


# ============================================================
# 9. TYPE CONVERSION
# ============================================================

print("\n9. TYPE CONVERSION")

number_as_text = "10"

number = int(number_as_text)

result = number + 5

print("Original value:", number_as_text)
print("Converted value:", number)
print("Result after adding 5:", result)


# ============================================================
# 10. COMPARISON OPERATORS
# ============================================================

print("\n10. COMPARISON OPERATORS")

x = 10
y = 5

print("x =", x)
print("y =", y)

print("x == y:", x == y)
print("x != y:", x != y)
print("x > y:", x > y)
print("x < y:", x < y)
print("x >= y:", x >= y)
print("x <= y:", x <= y)


# ============================================================
# 11. BASIC PROGRAM FLOW
# ============================================================

print("\n11. BASIC PROGRAM FLOW")

print("Python generally executes code from top to bottom.")

print("Step 1: Read the instruction")
print("Step 2: Execute the instruction")
print("Step 3: Move to the next instruction")


# ============================================================
# DAY 01 SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DAY 01 COMPLETED")
print("=" * 60)

print("""
Today you learned:

1. What programming is
2. Displaying output
3. Comments
4. Variables
5. Basic data types
6. Checking data types
7. Arithmetic operators
8. String operations
9. User input
10. Type conversion
11. Comparison operators
12. Basic program flow

These concepts form the foundation of programming.
""")
