from astroid import nodes
from astroid.inference import infer_name
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from pylint.interfaces import IAstroidChecker

iterable_types = (nodes.Tuple, nodes.List, nodes.Set, )

class ForLoopChecker(BaseChecker):
    """
    Check for poor for-loop usage.
    """

    __implements__ = IAstroidChecker

    name = 'for-loop-checker'
    priority = -1
    msgs = {
        'W8101': (
            'Unnecessary using of list() on an already iterable type.',
            'unnecessary-list-cast',
            'Eager iteration of an iterable is inefficient.'
        ),
        'W8102': (
            'Incorrect iterator method for dictionary, use .keys() or .values().',
            'incorrect-dictionary-iterator',
            'Use keys() or values() instead of items() when not unpacking both.'
        )
    }

    @checker_utils.check_messages("unnecessary-list-cast")
    def visit_for(self, node: nodes.For) -> None:
        """Visit for loops."""
        if not node.iter:
            return
        if not isinstance(node.iter, nodes.Call):
            return
        if not node.iter.func:
            return

        # We have multiple types of checkers, function call, or method calls
        if isinstance(node.iter.func, nodes.Name):
            if not node.iter.args:
                return
            if node.iter.func.name != 'list':
                return

            # Work out the value
            inferred_values = list(infer_name(node.iter.args[0]))
            if len(inferred_values) != 1:
                return  # can't have >1 or 0 assigned values
            inferred_value = inferred_values[0]
            if isinstance(inferred_value, iterable_types):
                self.add_message("unnecessary-list-cast", node=node.iter)

        elif isinstance(node.iter.func, nodes.Attribute):
            if node.iter.args:  # items() never has a list of arguments!
                return
            if node.iter.func.attrname != 'items':
                return
            if not isinstance(node.target, nodes.Tuple):
                return
            if not len(node.target.elts) == 2:
                return
            if any(el.name == '_' for el in node.target.elts if isinstance(el, nodes.AssignName)):
                self.add_message("incorrect-dictionary-iterator", node=node.iter)

        else:
            return



class LoopInvariantChecker(BaseChecker):
    """
    Check for poor for-loop usage.
    """

    __implements__ = IAstroidChecker

    name = 'loop-invariant-checker'
    priority = -1
    msgs = {
        'W8201': (
            'Consider moving this statement outside of the for-loop.',
            'loop-invariant-statement',
            'Eager iteration of an iterable is inefficient.'
        ),
        'W8202': (
            'Lookups of global names within a loop is inefficient, copy to a local variable outside of the loop first.',
            'loop-invariant-global-usage',
            'Eager iteration of an iterable is inefficient.'
        ),
    }

    def __init__(self, linter=None):
        super().__init__(linter)
        self._loop_level = 0

    @checker_utils.check_messages("loop-invariant-statement")
    def visit_for(self, node: nodes.For) -> None:
        """Visit for loop bodies."""
        self._loop_level += 1

    def leave_for(self, node: nodes.For) -> None:
        """Drop loop level."""
        self._loop_level -= 1

    @checker_utils.check_messages("loop-invariant-global-usage")
    def visit_name(self, node: nodes.Name) -> None:
        """Look for global names"""
        if checker_utils.is_builtin(node.name):
            return
        scope, stmts = node.lookup(node.name)
        if not isinstance(scope, nodes.Module):
            return
        if node.name in scope.globals:
            if self._loop_level > 0:
                self.add_message("loop-invariant-global-usage", node=node)
