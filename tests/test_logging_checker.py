import astroid
import perflint.logging_checker

from base import BaseCheckerTestCase


class TestLoggingChecker(BaseCheckerTestCase):
    CHECKER_CLASS = perflint.logging_checker.LoggingChecker

    def test_message_is_old_style_formatted_string(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("The number is %d" % 1)
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_old_style_formatted_string_w_multiple_values(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("The number is %d, the string is: %s" % (1, "bar"))
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_old_style_formatted_string_w_dict(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info(
                "The number %(foo)d, the string is: %(string)s" % {
                    "number": 1,
                    "string": "bar",
                },
            )
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_old_style_formatted_fstring(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            foo = 1
            logger.info(f"The value of `foo` is {foo}, `bar` is %d" % 2)
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_string_and_variable_concatenation(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            foo = "Foo"
            logger.info("The value of `foo` is " + foo)
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_string_and_variable_concatenation_in_the_middle(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            foo = "Foo"
            logger.info("The value of `foo` is " + foo + ".")
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_string_and_attribute_concatenation(self):
        test_func = astroid.extract_node("""
        import logging
        import os
        logger = logging.getLogger(__name__)

        def test():
            logger.info("Current OS is " + os.name)
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_variable_and_string_concatenation(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            foo = "Foo"
            logger.info(foo + " is the value of `foo`")
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_string_concatenation_is_ignored(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("Using " + "string concatenation")
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_message_is_adjacent_string_concatenation_is_ignored(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("Using " "adjacent string concatenation")
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_message_is_parenthesized_string_concatenation_is_ignored(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info(("Using ") + ("parenthesized string concatenation"))
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_message_is_new_style_formatted_string(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("The value of `foo` is {}".format(1))
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_new_style_formatted_string_with_format_map(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("The value of `foo` is {foo}".format_map({"foo": 1}))
        """)

    def test_message_is_new_style_formatted_fstring(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            foo = 1
            logger.info(f"The value of `foo` is {foo}, `bar` is {{bar}}".format_map({"bar": w}))
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_fstring(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            foo = 1
            logger.info(f"The value of `foo` is {foo}")
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_fstring_wo_placeholders_is_ignored(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info(f"This f-string contains no placeholders")
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_message_is_old_style_formatted_string_w_log_method(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.log(logging.INFO, "The value of `foo` is %d" % 1)
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_message_is_old_style_formatted_string_w_module_function(self):
        test_func = astroid.extract_node("""
        import logging

        def test():
            logging.info("The value of `foo` is %d" % 1)
        """)

        with self.assertAddedMessage("use-logger-formatting"):
            self.walk(test_func)

    def test_formatting_left_to_logger_is_ignored(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("The value of `foo` is %d", 1)
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_static_message_string_is_ignored(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            logger.info("This message does not use formatting")
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_message_string_var_is_ignored(self):
        test_func = astroid.extract_node("""
        import logging
        logger = logging.getLogger(__name__)

        def test():
            message = "This message does not use formatting"
            logger.info(message)
        """)

        with self.assertNoMessages():
            self.walk(test_func)
