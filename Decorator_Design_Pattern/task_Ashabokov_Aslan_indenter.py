'''
Indenter context manager
'''
from contextlib import ContextDecorator

class Indenter(ContextDecorator):
    """Indenter context manager"""

    def __init__(self, indent_str: str = None, indent_level: int = None) -> None:
        super().__init__()
        self._indent_str = indent_str or (" " * 4)
        self._indent_level = indent_level or 0
        self._indent_level -= 1

    def __enter__(self) -> None:
        self._indent_level += 1
        return self

    def __exit__(self, *args) -> None:
        self._indent_level -= 1

    def print(self, print_str: str) -> None:
        '''Print print_str with indent string'''
        print(self._indent_str * self._indent_level + print_str)
