'''
Tests for task_Ashabokov_Aslan_indenter module
'''
import pytest

from task_Ashabokov_Aslan_indenter import Indenter


DEFAULT_OUT = "hi\n" + ' ' * 4 + "hello\n" + ' ' * 8 + "bonjour\nhey\n"
OUT_WITH_STR = "hi\n--hello\n----bonjour\nhey\n"
OUT_WITH_STR_AND_LEVEL = "--hi\n----hello\n------bonjour\n--hey\n"

@pytest.mark.parametrize(
    "indent_str,indent_level,output",
    [
        (None, None, DEFAULT_OUT),
        ("--", None, OUT_WITH_STR),
        ("--", 1, OUT_WITH_STR_AND_LEVEL),
    ]
)
def test_indenter(indent_str, indent_level, output, capsys):
    """Test Indenter context manager"""

    with Indenter(indent_str, indent_level) as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
            with indent:
                indent.print("bonjour")
        indent.print("hey")

    captured = capsys.readouterr()

    assert captured.out == output, (
        f"Got wrong output: {captured.out}"
    )
