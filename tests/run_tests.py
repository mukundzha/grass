import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.environ.setdefault("TERM", "xterm-256color")

import test_editor
import test_highlight
import test_main
import test_screen
import test_search


def run_module_tests(module):
    passed = 0
    failed = 0
    for name in dir(module):
        if not name.startswith("test_"):
            continue
        function = getattr(module, name)
        try:
            function()
            passed = passed + 1
            print("ok   " + module.__name__ + "." + name)
        except Exception as error:
            failed = failed + 1
            print("FAIL " + module.__name__ + "." + name + ": " + str(error))
    return passed, failed


def main():
    passed = 0
    failed = 0
    modules = [test_editor, test_highlight, test_main, test_screen, test_search]
    for module in modules:
        module_passed, module_failed = run_module_tests(module)
        passed = passed + module_passed
        failed = failed + module_failed
    print("")
    print(str(passed) + " passed, " + str(failed) + " failed")
    if failed > 0:
        sys.exit(1)


main()
