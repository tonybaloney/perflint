import astroid
import perflint.for_loop_checker
import pylint.testutils
import contextlib


class TestUniqueReturnChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = perflint.for_loop_checker.LoopInvariantChecker


    @contextlib.contextmanager
    def assertAddedMessage(self, message):
        yield
        got = [msg.msg_id for msg in self.linter.release_messages()]
        got_str = "\n".join(repr(m) for m in got)
        msg = (
            "Expected messages did not match actual.\n"
            f"Got:\n{got_str}\n"
        )
        assert message in got, msg

    def test_basic_loop_invariant(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = (1,2,3,4)

            for item in list(items):
                x = print("There are ", len(items), "items")
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

        with self.assertAddedMessage("loop-invariant-statement"):
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