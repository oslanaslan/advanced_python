'''
Tests for task_Ashabokov_Aslan_repeater module

'''
from unittest import mock

import pytest

from task_Ashabokov_Aslan_repeater import repeater, verbose, verbose_context

@pytest.mark.parametrize(
    "count",
    [
        (0),
        (1),
        (5),
    ]
)
def test_repeater(count: int):
    '''Test repeater decorator'''
    mock_function = mock.MagicMock(name='function')
    mock_function.return_value = 1

    @repeater(count)
    def function():
        """Function docstring"""
        return mock_function()

    function()
    assert mock_function.call_count == count, (
        f"{mock_function.call_count}"
    )
    assert function.__name__ == 'function', (
        f"Name of wrapped function has been changed: {function.__name__}"
    )
    assert function.__doc__ == 'Function docstring', (
        f"Docstring of function has been changed: {function.__doc__}"
    )

def test_verbose(capsys):
    """Test verbose decorator"""

    @verbose
    def function():
        """Function docstring"""
        print("Inner function")

    function()

    captured = capsys.readouterr()
    expected_res = "before function call\nInner function\nafter function call\n"
    assert expected_res == captured.out
    assert function.__name__ == 'function', (
        f"Name of wrapped function has been changed: {function.__name__}"
    )
    assert function.__doc__ == 'Function docstring', (
        f"Docstring of function has been changed: {function.__doc__}"
    )

def test_verbose_context_as_decorator(capsys):
    """Test verbose_context decorator as decorator"""

    @verbose_context()
    def function():
        """Function docstring"""
        print("Inner function")

    function()

    captured = capsys.readouterr()
    expected_res = "class: before function call\nInner function\nclass: after function call\n"
    assert expected_res == captured.out
    assert function.__name__ == 'function', (
        f"Name of wrapped function has been changed: {function.__name__}"
    )
    assert function.__doc__ == 'Function docstring', (
        f"Docstring of function has been changed: {function.__doc__}"
    )

def test_verbose_context_as_context_manager(capsys):
    """Test verbose_context decorator as context manager"""

    with verbose_context():
        print("Inner output")

    captured = capsys.readouterr()
    expected_res = "class: before function call\nInner output\nclass: after function call\n"
    assert expected_res == captured.out

@pytest.mark.parametrize(
    "call_count",
    [
        (1),
        (3),
        (5),
    ]
)
def test_all_decorators(call_count):
    """Test all decorators"""

    mock_function = mock.MagicMock(name='function')
    mock_function.return_value = 1

    @verbose
    @repeater(call_count)
    @verbose_context()
    def function():
        """Function docstring"""
        return mock_function()

    function()
    assert mock_function.call_count == call_count, (
        f"{mock_function.call_count}"
    )
    assert function.__name__ == 'function', (
        f"Name of wrapped function has been changed: {function.__name__}"
    )
    assert function.__doc__ == 'Function docstring', (
        f"Docstring of function has been changed: {function.__doc__}"
    )
