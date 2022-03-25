from typing import Dict, List, Set, Union
from astroid import nodes
from astroid.helpers import safe_infer
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from pylint.interfaces import IAstroidChecker

iterable_types = (nodes.Tuple, nodes.List, nodes.Set, )
iterable_type_names = ("tuple", "list", "set", )

def get_children_recursive(node: nodes.NodeNG):
    """Get children of a node."""
    for child in node.get_children():
        yield child
        yield from get_children_recursive(child)


def local_type(name: nodes.NodeNG) -> Union[None, nodes.Name]:
    if not isinstance(name, nodes.Name):
        return

    if name.name in name.frame().locals:
        vals = name.frame().locals[name.name]
        if len(vals) > 0:
            assigned = vals[0].assign_type()
            if isinstance(assigned, nodes.Arguments):
                for annotation, arg in zip(assigned.annotations, assigned.arguments):
                    if arg.name == name.name:
                        if isinstance(annotation, nodes.Name):
                            return annotation
                        elif isinstance(annotation, nodes.Subscript) and isinstance(annotation.value, nodes.Name):
                            return annotation.value
                        else:
                            return None
    else:
        return

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

            inferred_value = safe_infer(node.iter.args[0])
            if inferred_value:
                if isinstance(inferred_value, iterable_types):
                    self.add_message("unnecessary-list-cast", node=node.iter)
            else:
                loc = local_type(node.iter.args[0])
                if loc and loc.name.lower() in iterable_type_names:
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
            'Consider moving this expression outside of the loop.',
            'loop-invariant-statement',
            'None of the variables referred to in this expression change within the loop.'
        ),
        'W8202': (
            'Lookups of global names within a loop is inefficient, copy to a local variable outside of the loop first.',
            'loop-invariant-global-usage',
            'Global name lookups in Python are slower than local names.'
        ),
        'R8203': (
            'Try..except blocks have an overhead. Avoid using them inside a loop unless you\'re using them for control-flow.',
            'loop-try-except-usage',
            'Avoid using try..except within a loop.'
        ),
        'W8204': (
            'Looped slicing of bytes objects is inefficient. Use a memoryview() instead',
            'memoryview-over-bytes',
            'Avoid using byte slicing in loops.'
        ),
        'W8205': (
            'Importing the "%s" name directly is more efficient in this loop.',
            'dotted-import-in-loop',
            'Dotted global names in loops are inefficient.'
        ),
    }

    def __init__(self, linter=None):
        super().__init__(linter)
        self._loop_level = 0
        self._loop_assignments: List[Set[str]] = []
        self._loop_names: List[List[nodes.Name]] = []
        self._loop_consts: List[List[nodes.Const]] = []
        self._ignore: List[nodes.NodeNG] = []

    @checker_utils.check_messages("loop-invariant-statement")
    def visit_for(self, node: nodes.For) -> None:
        """Visit for loop bodies."""
        self._loop_level += 1
        if isinstance(node.target, nodes.Tuple):
            self._loop_assignments.append(set(el.name for el in node.target.elts))
        elif isinstance(node.target, nodes.AssignName):
            self._loop_assignments.append({node.target.name})
        else:
            self._loop_assignments.append(set())
        self._loop_names.append([])
        self._loop_consts.append([])
        self._ignore.append(node.iter)

    @checker_utils.check_messages("loop-invariant-statement")
    def visit_while(self, node: nodes.While) -> None:
        """Visit while loop bodies."""
        self._loop_level += 1
        self._loop_names.append([])
        self._loop_consts.append([])
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
        unassigned_names = [name_node for name_node in self._loop_names.pop() if name_node.name not in assigned_names]
        used_consts = self._loop_consts.pop()
        FRAGMENT_NODE_TYPES = (nodes.FormattedValue, nodes.Attribute, nodes.Keyword, nodes.Slice, nodes.UnaryOp)
        NAME_NODES = (nodes.Name, nodes.AssignName)
        SIDE_EFFECT_NODES = (nodes.Yield, nodes.YieldFrom, nodes.Return, nodes.Raise)

        visited_nodes: Dict[nodes.NodeNG, bool] = dict()
        for name_node in [*unassigned_names, *used_consts]:
            cur_node = name_node.parent
            invariant_node = None
            while cur_node != node:
                # Walk down parent for variant components.
                is_variant = False
                if cur_node in visited_nodes:
                    is_variant = visited_nodes[cur_node]
                else:
                    if isinstance(cur_node, nodes.Call) and isinstance(cur_node.func, nodes.Name):
                        if cur_node.func in unassigned_names:
                            is_variant = True
                        elif cur_node.func.name == 'print':  # Treat print() as a side-effect
                            is_variant = True
                    elif isinstance(cur_node, SIDE_EFFECT_NODES):
                        is_variant = True
                    if not is_variant:
                        for child in get_children_recursive(cur_node):
                            if isinstance(child, NAME_NODES) and child.name in assigned_names:
                                is_variant = True
                    visited_nodes[cur_node] = is_variant
                if not is_variant:
                    invariant_node = cur_node
                    cur_node = cur_node.parent
                else:
                    break

            if invariant_node and invariant_node not in self._ignore and not isinstance(invariant_node, FRAGMENT_NODE_TYPES):
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
        scope, _ = node.lookup(node.name)
        if not isinstance(scope, nodes.Module):
            return
        if node.name in scope.globals and len(scope.globals[node.name]) > 0 and isinstance(scope.globals[node.name][0], nodes.AssignName):
            if self._loop_level > 0:
                self.add_message("loop-invariant-global-usage", node=node)

    def visit_const(self, node: nodes.Const) -> None:
        if self._loop_level == 0:
            return
        if self._loop_consts:
            self._loop_consts[-1].append(node)

    def visit_call(self, node: nodes.Call) -> None:
        """Look for method calls."""
        if not isinstance(node.func, nodes.Attribute):
            return
        if not self._loop_assignments:
            return # Skip when empty
        if isinstance(node.func.expr, nodes.Name):
            self._loop_assignments[-1].add(node.func.expr.name)

    @checker_utils.check_messages('loop-try-except-usage')
    def visit_tryexcept(self, node: nodes.TryExcept) -> None:
        if self._loop_level > 0:
            self.add_message("loop-try-except-usage", node=node)

    @checker_utils.check_messages('memoryview-over-bytes')
    def visit_subscript(self, node: nodes.Subscript) -> None:
        if self._loop_level == 0:
            return
        inferred_value = safe_infer(node.value)
        if not inferred_value:
            inferred_value = local_type(node.value)
            if isinstance(inferred_value, nodes.Name) and inferred_value.name == 'bytes':
                self.add_message("memoryview-over-bytes", node=node)
        if isinstance(inferred_value, nodes.Const) and isinstance(inferred_value.value, bytes):
            self.add_message("memoryview-over-bytes", node=node)

    @checker_utils.check_messages('dotted-import-in-loop')
    def visit_attribute(self, node: nodes.Attribute) -> None:
        if self._loop_level == 0:
            return
        inferred_value = safe_infer(node.expr)
        if inferred_value and isinstance(inferred_value, nodes.Module):
            if isinstance(node.parent, nodes.Attribute):  # TODO: Go higher in the chain
                self.add_message("dotted-import-in-loop", node=node.parent, args=(node.parent.attrname,))
            self.add_message("dotted-import-in-loop", node=node, args=(node.attrname,))
