from astroid import nodes
from astroid.bases import BoundMethod
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from astroid.helpers import safe_infer


def _is_string_concat(node: nodes.NodeNG) -> bool:
    """Return True if `node` is a string concatenation.

    E.g. `"a" + [... +] "z"`.
    """
    if not (isinstance(node, nodes.BinOp) and node.op == "+"):
        return False

    return _is_string(node.left) and _is_string(node.right)


def _is_string(node: nodes.NodeNG) -> bool:
    """Return True if `node` is a string literal/f-string/concatenated string."""
    return (
        (isinstance(node, nodes.Const) and isinstance(node.value, str))
        or isinstance(node, nodes.JoinedStr)
        or _is_string_concat(node)
    )


def _is_bound_str_join(node: nodes.Call) -> bool:
    """Return True if `node` is a call on the bound `str.join` method.

    E.g. `join = " ".join; join(iterable)`.
    """
    if not isinstance(node.func, nodes.Name):
        return False

    bm = next((r for r in node.func.infer() if isinstance(r, BoundMethod)), None)
    return (
        bm is not None and getattr(bm, "name", None) == "join" and _is_string(bm.bound)
    )


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
        "W8404": (
            "Pass a list comprehension to str.join instead of a generator expression",
            "use-list-comprehension-str-join",
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

    @checker_utils.only_required_for_messages("use-list-comprehension-str-join")
    def visit_generatorexp(self, node: nodes.GeneratorExp):
        if not isinstance(node.parent, nodes.Call):
            return
        func = node.parent.func
        if not (
            # "".join(iterable)
            (
                isinstance(func, nodes.Attribute)
                and func.attrname == "join"
                and _is_string(func.expr)
            )
            or
            # join = "".join; join(iterable)
            _is_bound_str_join(node.parent)
        ):
            return
        self.add_message("use-list-comprehension-str-join", node=node)
