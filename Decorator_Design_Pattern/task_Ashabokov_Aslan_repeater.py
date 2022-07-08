'''
Decorator module

- verbose - add output text before and afetr function call
- repeater(count: int) - call function 'count' times
- verbose-context - verbose context manager
'''

from contextlib import ContextDecorator
from functools import wraps


def verbose(function):
    """Verbose decorator"""
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("before function call")
        outcome = function(*args, **kwargs)
        print("after function call")
        return outcome
    return wrapper

def repeater(count: int) -> callable:
    """Repeater decorator. Calls function 'count' times"""
    def decorator(function: callable):
        @wraps(function)
        def wrapper(*args, **kwargs):
            outcome = []

            for _ in range(count):
                outcome.append(function(*args, **kwargs))

            return outcome
        return wrapper
    return decorator

class verbose_context(ContextDecorator):
    """Verbose context decorator"""

    def __enter__(self):
        """Start context"""
        print("class: before function call")

    def __exit__(self, *exc):
        """End context"""
        print("class: after function call")
