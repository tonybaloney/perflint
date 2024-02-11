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

    def test_complex_list_filter(self):
        test_func = astroid.extract_node(
            """
        def test(): #@
            items = [1,2,3,4]
            result = []
            for i in items:
                if i % 2:
                    result.append(i)
                elif i % 2:
                    result.append(i)
                else:
                    result.append(i)
        """
        )

        with self.assertNoMessages():
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

    def test_complex_filtered_dict_assignment(self):
        test_func = astroid.extract_node(
            """
        def test(): #@
            result = {}
            fruit = ["apple", "pear", "orange"]
            for idx, name in enumerate(fruit):
                if idx % 2:
                    result[idx] = name
                elif idx % 3:
                    result[idx] = name
                else:
                    result[idx] = name
        """
        )

        with self.assertNoMessages():
            self.walk(test_func)

    def test_complex_filtered_dict_assignment2(self):
        test_func = astroid.extract_node(
            """
        def test(): #@
            result = {}
            fruit = ["apple", "pear", "orange"]
            for idx, name in enumerate(fruit):
                if idx % 2:
                    result[idx] = name
                else:
                    result[idx] = name
        """
        )

        with self.assertNoMessages():
            self.walk(test_func)

    def test_str_join_on_gen_exp(self):
        test_func = astroid.extract_node(
            """
        def test():
            return " ".join(str(i) for i in range(10))
        """
        )

        with self.assertAddedMessage("use-list-comprehension-str-join"):
            self.walk(test_func)

    def test_str_join_on_parenthesized_gen_exp(self):
        test_func = astroid.extract_node(
            """
        def test():
            return " ".join((str(i) for i in range(10)))
        """
        )

        with self.assertAddedMessage("use-list-comprehension-str-join"):
            self.walk(test_func)

    def test_str_join_parenthesized_string_on_gen_exp(self):
        test_func = astroid.extract_node(
            """
        def test():
            return (" ").join(str(i) for i in range(10))
        """
        )

        with self.assertAddedMessage("use-list-comprehension-str-join"):
            self.walk(test_func)

    def test_str_join_parenthesized_concatenated_string_on_gen_exp(self):
        test_func = astroid.extract_node(
            """
        def test():
            return (" " + "-" + " ").join(str(i) for i in range(10))
        """
        )

        with self.assertAddedMessage("use-list-comprehension-str-join"):
            self.walk(test_func)

    def test_str_join_fstring_on_gen_exp(self):
        test_func = astroid.extract_node(
            """
        def test():
            sep = " "
            return f"{sep}".join(str(i) for i in range(10))
        """
        )

        with self.assertAddedMessage("use-list-comprehension-str-join"):
            self.walk(test_func)

    def test_str_join_local_var_on_gen_exp(self):
        test_func = astroid.extract_node(
            """
        def test():
            space_join = " ".join
            return space_join(str(i) for i in range(10))
        """
        )

        with self.assertAddedMessage("use-list-comprehension-str-join"):
            self.walk(test_func)
