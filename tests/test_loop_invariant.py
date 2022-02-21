import astroid
import perflint.for_loop_checker
from base import BaseCheckerTestCase


class TestUniqueReturnChecker(BaseCheckerTestCase):
    CHECKER_CLASS = perflint.for_loop_checker.LoopInvariantChecker

    def test_basic_loop_invariant(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = (1,2,3,4)

            for item in list(items):
                x = print("There are ", len(items), "items")
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_node)

    def test_basic_loop_invariant_while(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = (1,2,3,4)
            i = 0
            while i < len(items):
                x = print("There are ", len(items), "items")
                i += 1
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_node)

    def test_basic_loop_variant_while(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = (1,2,3,4)
            i = 0
            while i < len(items):
                i += 1
                print(i)
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_node)



    def test_basic_loop_variant_by_method(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = [1,2,3,4]

            for item in items:
                x = print("There are ", len(items), "items")
                items.clear()
        """)

        with self.assertNoMessages():
            self.walk(test_node)

    def test_global_in_for_loop(self):
        test_func = astroid.extract_node("""
        glbl = 1

        def test(): #@
            items = (1,2,3,4)

            for item in list(items):
                glbl
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_func)
