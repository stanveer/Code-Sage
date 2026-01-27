"""Example Python file with various issues for testing Code Sage."""

import os
import sys

# TODO: Refactor this module
# FIXME: This function has issues

# Hardcoded password (Security Issue)
PASSWORD = "super_secret_123"
API_KEY = "sk_test_1234567890abcdefghijklmnop"


def function_with_mutable_default(items=[]):
    """Function with mutable default argument (Bug)."""
    items.append(1)
    return items


def bare_except_example():
    """Function with bare except (Best Practice Violation)."""
    try:
        risky_operation()
    except:  # Should catch specific exceptions
        pass


def long_complex_function(x, y, z):
    """Function with high complexity."""
    if x > 0:
        if y > 0:
            if z > 0:
                if x > y:
                    if y > z:
                        if x > z:
                            return "complex"
                        return "very complex"
                    return "medium complex"
                return "somewhat complex"
            return "not complex"
        return "less complex"
    return "negative"


def sql_injection_example(user_input):
    """SQL injection vulnerability."""
    query = "SELECT * FROM users WHERE id = " + user_input
    return query


def identity_check_with_literal(x):
    """Identity check with literal (Bug)."""
    if x is 5:  # Should use == for value comparison
        return True
    return False


# Wildcard import (Best Practice Violation)
from os import *


def function_with_many_parameters(a, b, c, d, e, f, g):
    """Function with too many parameters."""
    return a + b + c + d + e + f + g


# Unused imports
import json
import re


# Print statement (Code Smell)
print("Debug: This should be logged properly")


class ExampleClass:
    """Example class."""

    def __init__(self):
        """Initialize."""
        pass

    def method_that_does_nothing(self):
        """Empty method."""
        pass


if __name__ == "__main__":
    # Using eval (Security Risk)
    user_code = input("Enter code: ")
    result = eval(user_code)
    print(result)
