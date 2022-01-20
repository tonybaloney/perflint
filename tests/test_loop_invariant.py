import astroid
import perflint.for_loop_checker
import pylint.testutils


class TestUniqueReturnChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = perflint.for_loop_checker.LoopInvariantChecker


    def test_basic_loop_invariant(self):
        for_node = astroid.extract_node("""
        glbl = 1

        def test():
            items = (1,2,3,4)

            for item in list(items): #@
                x = print("There are ", len(items), "items")
                print(glbl)
        """)

        with self.assertAddsMessages("loop-invariant-statement"):
            self.checker.visit_for(for_node)

    def test_global_in_for_loop(self):
        for_node = astroid.extract_node("""
        glbl = 1

        def test():
            items = (1,2,3,4)

            for item in list(items): #@
                glbl
        """)

        with self.assertAddsMessages("loop-invariant-statement"):
            self.checker.visit_for(for_node)