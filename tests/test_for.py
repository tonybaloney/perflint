import astroid
import perflint.for_loop_checker

from base import BaseCheckerTestCase


class TestUniqueReturnChecker(BaseCheckerTestCase):
    CHECKER_CLASS = perflint.for_loop_checker.ForLoopChecker

    def test_bad_list_cast(self):
        for_node = astroid.extract_node("""
        def test():
            items = (1,2,3,4)

            for item in list(items): #@
                pass
        """)

        with self.assertAddedMessage("unnecessary-list-cast"):
            self.checker.visit_for(for_node)

    def test_bad_list_cast_typed(self):
        for_node = astroid.extract_node("""
        def test(items: List[int]):
            for item in list(items): #@
                pass
        """)

        with self.assertAddedMessage("unnecessary-list-cast"):
            self.checker.visit_for(for_node)

    def test_bad_dict_usage_values(self):
        for_node = astroid.extract_node("""
        def test():
            d = {1: 1, 2: 2}

            for _, v in d.items(): #@
                pass
        """)

        with self.assertAddedMessage("incorrect-dictionary-iterator"):
            self.checker.visit_for(for_node)

    def test_bad_dict_usage_keys(self):
        for_node = astroid.extract_node("""
        def test():
            d = {1: 1, 2: 2}

            for k, _ in d.items(): #@
                pass
        """)

        with self.assertAddedMessage("incorrect-dictionary-iterator"):
            self.checker.visit_for(for_node)
