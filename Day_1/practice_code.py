## List & Dict Comprehensions (Python)
# ------------------------------------------------------------------------------------------------------------
# What is List Comprehension?
# List comprehension is a concise way to create lists in Python. It allows you to generate a new list by applying an expression to each item in an existing iterable (like a list or range).
# The syntax for list comprehension is:
# new_list = [expression for item in iterable if condition]
#------------------------------------------------------------------------------------------------------------
# Example 1: Creating a list of squares of numbers from 0 to 9
squares = [x**2 for x in range(10)]
print("Squares from 0 to 9:", squares)
# Example 2: Creating a list of even numbers from 0 to 19
even_numbers = [x for x in range(20) if x % 2 == 0]
print("Even numbers from 0 to 19:", even_numbers)
# Example 3: Creating a list of uppercase letters from a given string
input_string = "hello world"
uppercase_letters = [char.upper() for char in input_string if char.isalpha()]
print("Uppercase letters in 'hello world':", uppercase_letters)
#------------------------------------------------------------------------------------------------------------
# What is Dictionary Comprehension?
# Dictionary comprehension is a concise way to create dictionaries in Python. It allows you to generate a new dictionary by applying an expression to each item in an existing iterable.
# The syntax for dictionary comprehension is:
# new_dict = {key_expression: value_expression for item in iterable if condition}
#------------------------------------------------------------------------------------------------------------
# Example 1: Creating a dictionary of squares of numbers from 0 to 9
squares_dict = {x: x**2 for x in range(10)}
print("Dictionary of squares from 0 to 9:", squares_dict)
# Example 2: Creating a dictionary of numbers and their cubes for even numbers from 0 to 9
cubes_dict = {x: x**3 for x in range(10) if x % 2 == 0}
print("Dictionary of cubes for even numbers from 0 to 9:", cubes_dict)
# Example 3: Creating a dictionary from two lists
keys = ['a', 'b', 'c']
values = [1, 2, 3]
combined_dict = {keys[i]: values[i] for i in range(len(keys))}
print("Combined dictionary from two lists:", combined_dict)
#------------------------------------------------------------------------------------------------------------
