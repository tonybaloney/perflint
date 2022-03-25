from typing import Dict, List
from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from pylint.interfaces import IAstroidChecker


class ComprehensionChecker(BaseChecker):
    """
    Check for comprehension usage
    """

    __implements__ = IAstroidChecker

    name = "comprehension-checker"
    priority = -1
    msgs = {
        "W8401": (
            "Use a list comprehension instead of a for-loop",
            "use-list-comprehension",
            "",
        ),
        "W8402": (
            "Use a list copy() instead of a for-loop",
            "use-list-copy",
            "",
        ),
    }

    def visit_for(self, node: nodes.For):
        pass

    @checker_utils.check_messages("use-list-comprehension")
    def leave_for(self, node: nodes.For):
        if len(node.body) != 1:
            return
        if isinstance(node.body[0], nodes.If):
            if not isinstance(node.body[0].body[0], nodes.Expr):
                return
            if not isinstance(node.body[0].body[0].value, nodes.Call):
                return
            # Is append call.
            if not isinstance(node.body[0].body[0].value.func, nodes.Attribute):
                return
            if not node.body[0].body[0].value.func.attrname in ["append", "insert"]:
                return
            self.add_message("use-list-comprehension", node=node)
        elif isinstance(node.body[0], nodes.Expr):
            if not isinstance(node.body[0].value, nodes.Call):
                return
            # Is append call.
            if not isinstance(node.body[0].value.func, nodes.Attribute):
                return
            if not node.body[0].value.func.attrname in ["append", "insert"]:
                return
            self.add_message("use-list-copy", node=node)
