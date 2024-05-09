
import re
import os
import sys
from typing import List


class ArgProvider:
    def __init__(self, command_line_args: List[str] = None):
        assert isinstance(command_line_args, list), f"Error: Command line args need to be list but is type {type(command_line_args)}."
        self._cla = command_line_args
        self._old_argv = None

    def __enter__(self):
        self._old_argv = sys.argv
        if self._cla:
            # First arg is the script name which will be different during testing anyways.
            sys.argv = ["script.py"] + self._cla

    def __exit__(self, exc_type, exc, exc_tb):
        sys.argv = self._old_argv


def is_executed_in_script_dir():
    """
    Since paths in testcases are hardcoded relative to the test/ directory, this
    method makes sure that the tests are called from the test/ directory and not
    e.g. from the repo's root.
    """

    script_path = sys.argv[0]
    folder_component = os.path.dirname(script_path)
    pwd_in_script_dir = folder_component in ["", "."]
    return pwd_in_script_dir


def remove_newlines_in_parentheses(content: str):
    # Regex to find all contents within parentheses '(' or ')' and replace newlines with space
    content = re.sub(r'\(([^)]*)\)', lambda m: '(' + m.group(1).replace('\n', ' ') + ')', content)
    # Remove multiple consecutive spaces
    content = re.sub(r'\(([^)]*)\)', lambda m: '(' + m.group(1).replace('  ', '') + ')', content)
    return content
