import astroid
import perflint.comprehension_checker

from base import BaseCheckerTestCase


class TestComprehensionChecker(BaseCheckerTestCase):
    CHECKER_CLASS = perflint.comprehension_checker.ComprehensionChecker

    def test_simple_list_filter(self):
        test_func = astroid.extract_node(
            """
        def test(): #@
            items = [1,2,3,4]
            result = []
            for i in items:
                if i % 2:
                    result.append(i)
        """
        )

        with self.assertAddedMessage("use-list-comprehension"):
            self.walk(test_func)

    def test_simple_list_copy(self):
        test_func = astroid.extract_node(
            """
        def test(): #@
            items = [1,2,3,4]
            result = []
            for i in items:
                result.append(i)
        """
        )

        with self.assertAddedMessage("use-list-copy"):
            self.walk(test_func)

    def test_simple_dict_assignment(self):
        test_func = astroid.extract_node(
            """
        def test(): #@
            result = {}
            fruit = ["apple", "pear", "orange"]
            for idx, name in enumerate(fruit):
                result[idx] = name
        """
        )

        with self.assertAddedMessage("use-dict-comprehension"):
            self.walk(test_func)

    def test_filtered_dict_assignment(self):
        test_func = astroid.extract_node(
            """
        def test(): #@
            result = {}
            fruit = ["apple", "pear", "orange"]
            for idx, name in enumerate(fruit):
                if idx % 2:
                    result[idx] = name
        """
        )

        with self.assertAddedMessage("use-dict-comprehension"):
            self.walk(test_func)
