from typing import List, Set, Union
from astroid import nodes
from astroid.inference import infer_name
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from pylint.interfaces import IAstroidChecker

iterable_types = (nodes.Tuple, nodes.List, nodes.Set, )

def get_children_recursive(node: nodes.NodeNG):
    """Get children of a node."""
    for child in node.get_children():
        yield child
        yield from get_children_recursive(child)


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
            'Incorrect iterator method for dictionary, use %s.',
            'incorrect-dictionary-iterator',
            'Incorrect use of .items() when not unpacking key and value.'
        )
    }

    @checker_utils.check_messages("unnecessary-list-cast", "incorrect-dictionary-iterator")
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
            if isinstance(node.target.elts[0], nodes.AssignName) and node.target.elts[0].name == '_':
                self.add_message("incorrect-dictionary-iterator", node=node.iter, args=('values()', ))
            if isinstance(node.target.elts[1], nodes.AssignName) and node.target.elts[1].name == '_':
                self.add_message("incorrect-dictionary-iterator", node=node.iter, args=('keys()', ))

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
            'Consider moving this statement outside of the loop.',
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
        self._loop_assignments: List[Set[str]] = []
        self._loop_names: List[List[nodes.Name]] = []
        self._ignore: List[nodes.NodeNG] = []

    @checker_utils.check_messages("loop-invariant-statement")
    def visit_for(self, node: nodes.For) -> None:
        """Visit for loop bodies."""
        self._loop_level += 1
        if isinstance(node.target, nodes.Tuple):
            self._loop_assignments.append(set(el.name for el in node.target.elts))
        elif isinstance(node.target, nodes.AssignName):
            self._loop_assignments.append({node.target.name})
        self._loop_names.append([])

    @checker_utils.check_messages("loop-invariant-statement")
    def visit_while(self, node: nodes.While) -> None:
        """Visit while loop bodies."""
        self._loop_level += 1
        self._loop_names.append([])
        self._loop_assignments.append(set())
        self._ignore.append(node.test)

    @checker_utils.check_messages("loop-invariant-statement")
    def leave_for(self, node: nodes.For) -> None:
        self._leave_loop(node)

    @checker_utils.check_messages("loop-invariant-statement")
    def leave_while(self, node: nodes.While) -> None:
        self._leave_loop(node)

    def _leave_loop(self, node: Union[nodes.For, nodes.While]) -> None:
        """Drop loop level."""
        self._loop_level -= 1
        assigned_names = self._loop_assignments.pop()
        used_names = self._loop_names.pop()
        for name_node in used_names:
            if name_node.name not in assigned_names:
                cur_node = name_node.parent
                invariant_node = None
                while cur_node != node:
                    # Walk down parent for variant components.
                    is_variant = False
                    for child in get_children_recursive(cur_node):
                        if isinstance(child, nodes.Name) and child.name in assigned_names:
                            is_variant = True
                    if not is_variant:
                        invariant_node = cur_node
                        cur_node = cur_node.parent
                    else:
                        break

                if invariant_node and invariant_node not in self._ignore:
                    self.add_message("loop-invariant-statement", node=invariant_node)


    def visit_assign(self, node: nodes.Assign) -> None:
        """Track assignments in loops."""
        # we don't handle multiple assignment nor slice assignment
        if not self._loop_assignments:
            return # Skip when empty

        target = node.targets[0]
        if isinstance(target, nodes.AssignName):
            self._loop_assignments[-1].add(target.name)

    def visit_augassign(self, node: nodes.AugAssign) -> None:
        """Track assignments in loops."""
        # we don't handle multiple assignment nor slice assignment
        if not self._loop_assignments:
            return # Skip when empty

        if isinstance(node.target, nodes.AssignName):
            self._loop_assignments[-1].add(node.target.name)

    @checker_utils.check_messages("loop-invariant-global-usage")
    def visit_name(self, node: nodes.Name) -> None:
        """Look for global names"""
        if self._loop_names:
            if not checker_utils.is_builtin(node.name) and node.name != "self":
                self._loop_names[-1].append(node)

        if checker_utils.is_builtin(node.name):
            return
        scope, stmts = node.lookup(node.name)
        if not isinstance(scope, nodes.Module):
            return
        if node.name in scope.globals and isinstance(scope.globals[node.name], nodes.AssignName):
            if self._loop_level > 0:
                self.add_message("loop-invariant-global-usage", node=node)

    def visit_call(self, node: nodes.Call) -> None:
        """Look for method calls."""
        if not isinstance(node.func, nodes.Attribute):
            return
        if not self._loop_assignments:
            return # Skip when empty
        if isinstance(node.func.expr, nodes.Name):
            self._loop_assignments[-1].add(node.func.expr.name)
