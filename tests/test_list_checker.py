import astroid
import perflint.list_checker

from base import BaseCheckerTestCase


class TestListMutationChecker(BaseCheckerTestCase):
    CHECKER_CLASS = perflint.list_checker.ListChecker

    def test_const_list_should_be_tuple(self):
        test_func = astroid.extract_node("""
        def test(): #@
            items = [1,2,3,4]
        """)

        with self.assertAddedMessage("use-tuple-over-list"):
            self.walk(test_func)

    def test_mutated_list_by_method(self):
        test_func = astroid.extract_node("""
        def test(): #@
            items = [1,2,3,4]
            items.clear()
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_mutated_list_by_index(self):
        test_func = astroid.extract_node("""
        def test(): #@
            items = [1,2,3,4]
            items[0] = 0
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_mutated_global_list_by_index(self):
        test_func = astroid.extract_node("""
        items = [1,2,3,4]
        def test(): #@
            items[0] = 0
        """)

        with self.assertNoMessages():
            self.walk(test_func)
    
    def test_mutated_global_list_by_method(self):
        test_func = astroid.extract_node("""
        items = [1,2,3,4]
        def test(): #@
            items.append(5)
        """)

        with self.assertNoMessages():
            self.walk(test_func)