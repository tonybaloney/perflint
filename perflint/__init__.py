"""Pylint extension with performance anti-patterns"""
from typing import TYPE_CHECKING

from perflint.checker import ForLoopChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter

__version__ = "0.0.1"


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """

    linter.register_checker(ForLoopChecker(linter))
