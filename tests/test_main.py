import io
import sys

from grass import VERSION
from grass import main as main_module


def run_version_flag():
    old_argv = sys.argv
    old_stdout = sys.stdout
    sys.argv = ["grass", "--version"]
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        main_module.main()
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
    return buffer.getvalue()


def test_version_flag_prints_name_and_version():
    text = run_version_flag()
    assert "grass " + VERSION in text


def test_version_flag_mentions_theme():
    text = run_version_flag()
    assert "Meadow" in text


def test_reset_cursor_restores_default_shape():
    old_stdout = sys.stdout
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        main_module.reset_cursor()
    finally:
        sys.stdout = old_stdout
    assert "\x1b[?25h" in buffer.getvalue()
    assert "\x1b[0 q" in buffer.getvalue()
