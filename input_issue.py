from enum import Enum


class InputIssue(Enum):
    UNCLOSED_PARENTHESES = "Unclosed parentheses detected in the range input."
    NO_DASH_PRESENT = "No dash is present between parentheses."
    EMPTY_INPUT = "Please provide a range input."