import pylint
from pylint.lint import Run as PylintRun
import sys

from perflint.for_loop_checker import ForLoopChecker, LoopInvariantChecker
from perflint.list_checker import ListChecker
from perflint.comprehension_checker import ComprehensionChecker
from perflint.logging_checker import LoggingChecker


pylint.modify_sys_path()

rules = (
    list(ForLoopChecker.msgs.keys())
    + list(LoopInvariantChecker.msgs.keys())
    + list(ListChecker.msgs.keys())
    + list(ComprehensionChecker.msgs.keys())
    + list(LoggingChecker.msgs.keys())
)

args = []
args.append("--load-plugins=perflint")
args.append("--disable=all")
args.append("--enable={0}".format(",".join(rules)))
args.extend(sys.argv[1:])

try:
    PylintRun(args)
except KeyboardInterrupt:
    sys.exit(1)
