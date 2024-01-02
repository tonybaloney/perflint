from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from astroid.helpers import safe_infer


class ComprehensionChecker(BaseChecker):
    """
    Check for comprehension usage
    """

    name = "comprehension-checker"
    priority = -1
    msgs = {
        "W8401": (
            "Use a list comprehension instead of a for-loop",
            "use-list-comprehension",
            "",
        ),
        "W8402": (
            "Use a list copy instead of a for-loop",
            "use-list-copy",
            "",
        ),
        "W8403": (
            "Use a dictionary comprehension instead of a for-loop",
            "use-dict-comprehension",
            "",
        ),
    }

    def visit_for(self, node: nodes.For):
        pass

    @checker_utils.only_required_for_messages(
        "use-list-comprehension", "use-dict-comprehension", "use-list-copy"
    )
    def leave_for(self, node: nodes.For):
        if len(node.body) != 1:
            return
        if isinstance(node.body[0], nodes.If) and not node.body[0].orelse:
            # TODO : Support a simple, single else statement
            if isinstance(node.body[0].body[0], nodes.Expr):
                if not isinstance(node.body[0].body[0].value, nodes.Call):
                    return
                # Is append call.
                if not isinstance(node.body[0].body[0].value.func, nodes.Attribute):
                    return
                if not node.body[0].body[0].value.func.attrname in ["append", "insert"]:
                    return
                self.add_message("use-list-comprehension", node=node)
            elif isinstance(node.body[0].body[0], nodes.Assign):
                if len(node.body[0].body[0].targets) != 1:
                    return
                if not isinstance(node.body[0].body[0].targets[0], nodes.Subscript):
                    return
                if not isinstance(node.body[0].body[0].targets[0].value, nodes.Name):
                    return
                inferred_value = safe_infer(node.body[0].body[0].targets[0].value)
                if isinstance(inferred_value, nodes.Dict):
                    self.add_message("use-dict-comprehension", node=node)
        elif isinstance(node.body[0], nodes.Expr):
            if not isinstance(node.body[0].value, nodes.Call):
                return
            # Is append call.
            if not isinstance(node.body[0].value.func, nodes.Attribute):
                return
            if not node.body[0].value.func.attrname in ["append", "insert"]:
                return
            self.add_message("use-list-copy", node=node)
        elif isinstance(node.body[0], nodes.Assign):
            if len(node.body[0].targets) != 1:
                return
            if not isinstance(node.body[0].targets[0], nodes.Subscript):
                return
            if not isinstance(node.body[0].targets[0].value, nodes.Name):
                return
            inferred_value = safe_infer(node.body[0].targets[0].value)
            if isinstance(inferred_value, nodes.Dict):
                self.add_message("use-dict-comprehension", node=node)
