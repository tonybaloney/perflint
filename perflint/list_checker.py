from typing import Dict, List
from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from pylint.interfaces import IAstroidChecker


class ListChecker(BaseChecker):
    """
    Check for inefficient list usage
    """

    __implements__ = IAstroidChecker

    name = 'list-checker'
    priority = -1
    msgs = {
        'W8301': (
            'Use tuple instead of list for a non-mutated sequence',
            'use-tuple-over-list',
            ''
        ),
    }

    def __init__(self, linter=None):
        super().__init__(linter)
        self._lists_to_watch: List[Dict[str, nodes.AssignName]] = []

    def visit_assign(self, node: nodes.Assign):
        if not isinstance(node.value, nodes.List):
            return
        if len(node.targets) > 1:
            return
        if isinstance(node.targets[0], nodes.AssignName):
            self._lists_to_watch[-1][node.targets[0].name] = node.targets[0]

    def visit_module(self, node: nodes.Module):
        self._lists_to_watch.append({})

    def _raise_for_scope(self):
        _lists = self._lists_to_watch.pop()
        for _assignment in _lists.values():
            self.add_message("use-tuple-over-list", node=_assignment.parent.value)

    @checker_utils.check_messages("use-tuple-over-list")
    def leave_module(self, node: nodes.Module):
        self._raise_for_scope()

    def visit_functiondef(self, node: nodes.FunctionDef):
        self._lists_to_watch.append({})

    @checker_utils.check_messages("use-tuple-over-list")
    def leave_functiondef(self, node: nodes.FunctionDef):
        self._raise_for_scope()

    def visit_call(self, node: nodes.Call) -> None:
        """Look for method calls to list nodes."""
        if not isinstance(node.func, nodes.Attribute):
            return
        if not isinstance(node.func.expr, nodes.Name):
            return
        # TODO : Filter from non-mutation methods
        self._mark_mutated(node.func.expr)

    def _mark_mutated(self, _name: nodes.Name):
        if _name.name in self._lists_to_watch[-1]:
            del self._lists_to_watch[-1][_name.name]
            return
        scope, _ = _name.lookup(_name.name)
        if not isinstance(scope, nodes.Module):
            return
        if _name.name in scope.globals \
            and _name.name in self._lists_to_watch[0]:
            del self._lists_to_watch[0][_name.name]

    def visit_subscript(self, node: nodes.Subscript):
        if not isinstance(node.parent, nodes.Assign):
            return
        if not isinstance(node.value, nodes.Name):
            return
        self._mark_mutated(node.value)
