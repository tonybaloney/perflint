import astroid
import perflint.checker
import pylint.testutils


class TestUniqueReturnChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = perflint.checker.ForLoopChecker


    def test_bad_list_cast(self):
        for_node = astroid.extract_node("""
        def test():
            items = (1,2,3,4)

            for item in list(items): #@
                pass
        """)

        with self.assertAddsMessages("unnecessary-list-cast"):
            self.checker.visit_for(for_node)
