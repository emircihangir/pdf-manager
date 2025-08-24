from enum import Enum


class ExceedingIndexError(Exception):
    """
    Raised if the user types an index that
    exceeds the page count in the selected PDF file.

    The *args attribute is a tuple with one element that contains
    the maximum number of pages of the selected file.
    """

class FaultyEndIndexError(Exception):
    """Raised when end <= start"""


class InputIssue(Enum):
    UNCLOSED_PARENTHESES = "Unclosed parentheses detected in the range input."
    NO_DASH_PRESENT = "No dash is present between parentheses."
    EMPTY_INPUT = "Please provide a range input."
    INVALID_CHARACTER_PRESENT = "The range input contains invalid character(s). Only numeric values are allowed."