import contextlib
import pylint.testutils


class BaseCheckerTestCase(pylint.testutils.CheckerTestCase):
    """Extends the basic pylint test case with easier helpers."""

    @contextlib.contextmanager
    def assertAddedMessage(self, message):
        """Assert that a msg_id occurred."""
        yield
        got = [msg.msg_id for msg in self.linter.release_messages()]
        got_str = "\n".join(repr(m) for m in got)
        msg = (
            "Expected messages did not match actual.\n"
            f"Got:\n{got_str}\n"
        )
        assert message in got, msg