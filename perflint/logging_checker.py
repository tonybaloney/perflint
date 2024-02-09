from astroid import nodes
from astroid.bases import Instance
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils


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


def _is_old_style_formatted_string(node: nodes.NodeNG) -> bool:
    """Return True if `node` is an old-style formatted string.
    
    E.g. `"%s" % value`."""
    return isinstance(node, nodes.BinOp) and node.op == "%"


def _is_new_style_formatted_string(node: nodes.NodeNG) -> bool:
    """Return True if `node` is a new-style formatted string.

    E.g. `"foo: {}".format(foo))` or `"foo: {bar}".format_map({"bar": 1})`.
    """
    return (
        isinstance(node, nodes.Call)
        and isinstance(node.func, nodes.Attribute)
        and node.func.attrname in ("format", "format_map")
        and _is_string(node.func.expr)
    )


def _is_fstring(node: nodes.NodeNG) -> bool:
    """Return True if `node` is an f-string with at least one placeholder.

    E.g. `f"foo: {foo}"`.
    """
    return isinstance(node, nodes.JoinedStr) and any(
        isinstance(v, nodes.FormattedValue) for v in node.values
    )


def _is_string_and_var_concat(node: nodes.NodeNG) -> bool:
    """Return True if `node` is a concatenation of a string literal and a
       variable/attribute.

    E.g.: `"foo: " + string_var_or_attr [+ ...]`.
    """
    if not (isinstance(node, nodes.BinOp) and node.op == "+"):
        return False

    if _is_string(node.left):
        return isinstance(
            node.right, (nodes.Name, nodes.Attribute)
        ) or _is_string_and_var_concat(node.right)
    elif _is_string(node.right):
        return isinstance(
            node.left, (nodes.Name, nodes.Attribute)
        ) or _is_string_and_var_concat(node.left)

    return False


class LoggingChecker(BaseChecker):
    """
    Check for already formatted strings being passed to logger methods
    """

    name = "logging-checker"
    msgs = {
        "W8501": (
            "Delegate message string formatting to the logger",
            "use-logger-formatting",
            "String formatting done by the logger is lazy, i.e. "
            "it will not be performed if the logger level is not enabled.",
        ),
    }

    @checker_utils.only_required_for_messages("logging-checker")
    def visit_call(self, node: nodes.Call):
        # It is a call to a logging method.
        if not isinstance(node.func, nodes.Attribute):
            return
        func_name = node.func.attrname
        if func_name not in (
            "debug",
            "info",
            "warning",
            "warn",
            "error",
            "exception",
            "critical",
            "fatal",
            "log",
        ):
            return

        # The method call is on a logger or on the `logging` module.
        if not any(
            (
                # log.info
                (
                    isinstance(expr_type, Instance)
                    and expr_type.pytype() in ("logging.Logger", "logging.RootLogger")
                )
                or
                # logging.info
                (isinstance(expr_type, nodes.Module) and expr_type.name == "logging")
            )
            for expr_type in node.func.expr.infer()
        ):
            return

        # .info(message) or .log(level, message)
        nargs = 2 if func_name == "log" else 1
        # If there are more than `nargs` arguments then formatting is left to the logger.
        if len(node.args) != nargs:
            return

        last_arg = node.args[nargs - 1]
        if (
            _is_old_style_formatted_string(last_arg)
            or _is_new_style_formatted_string(last_arg)
            or _is_fstring(last_arg)
            or _is_string_and_var_concat(last_arg)
        ):
            self.add_message("use-logger-formatting", node=last_arg)
