import io
import sys

from grass import screen


def test_is_pristine_when_empty_untitled():
    state = {"path": None, "modified": False, "lines": [""]}
    assert screen.is_pristine(state) is True


def test_not_pristine_with_path():
    state = {"path": "a.py", "modified": False, "lines": [""]}
    assert screen.is_pristine(state) is False


def test_not_pristine_with_text():
    state = {"path": None, "modified": False, "lines": ["x"]}
    assert screen.is_pristine(state) is False


def test_not_pristine_when_modified():
    state = {"path": None, "modified": True, "lines": [""]}
    assert screen.is_pristine(state) is False


def test_scrollbar_thumb_starts_at_top():
    start, size = screen.scrollbar_thumb(0, 1000, 40)
    assert start == 0
    assert size >= 1


def test_scrollbar_thumb_reaches_bottom():
    start, size = screen.scrollbar_thumb(960, 1000, 40)
    assert start + size == 40


def test_scrollbar_thumb_never_overflows():
    total = 13
    view_rows = 10
    top = 0
    while top <= total - view_rows:
        start, size = screen.scrollbar_thumb(top, total, view_rows)
        assert start >= 0
        assert start + size <= view_rows
        top = top + 1


def test_splash_shows_version_and_theme():
    texts = []
    for entry in screen.splash_lines(100):
        texts.append(entry[0])
    joined = "\n".join(texts)
    assert "v" + screen.VERSION in joined
    assert "Meadow" in joined


def test_splash_shows_version_in_narrow_terminals():
    texts = []
    for entry in screen.splash_lines(30):
        texts.append(entry[0])
    joined = "\n".join(texts)
    assert "v" + screen.VERSION in joined


def test_splash_wordmark_has_two_tones():
    lines = screen.splash_lines(100)
    assert lines[0][1] == "keyword"
    assert lines[4][1] == "accent"


def test_status_dot_shows_when_modified():
    state = {"modified": True}
    assert screen.status_dot(state) == "●"


def test_status_dot_hides_when_clean():
    state = {"modified": False}
    assert screen.status_dot(state) == ""


def test_window_title_names_the_file():
    state = {"path": "/tmp/demo.py", "modified": False}
    assert screen.window_title(state) == "grass · demo.py"


def test_window_title_marks_unsaved_changes():
    state = {"path": "/tmp/demo.py", "modified": True}
    assert screen.window_title(state) == "grass · demo.py •"


def test_window_title_for_untitled_buffer():
    state = {"path": None, "modified": False}
    assert screen.window_title(state) == "grass · (untitled)"


def test_set_title_writes_terminal_escape():
    old_stdout = sys.stdout
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        screen.set_title("grass · demo.py")
    finally:
        sys.stdout = old_stdout
    assert "\x1b]2;grass · demo.py\x07" in buffer.getvalue()


def test_message_color_for_error():
    assert screen.message_color("Cannot save: disk full") == "error"


def test_message_color_for_success():
    assert screen.message_color("Saved demo.py") == "accent"


def test_message_color_for_plain_message():
    assert screen.message_color("Cut line") == "message"


def test_missing_newline_flag():
    state = {"lines": ["x"], "final_newline": False}
    assert screen.missing_newline(state) is True
    state["final_newline"] = True
    assert screen.missing_newline(state) is False
    state = {"lines": [""], "final_newline": False}
    assert screen.missing_newline(state) is False
    state = {"lines": ["x", ""], "final_newline": False}
    assert screen.missing_newline(state) is False


def test_search_progress_for_replace_prompts():
    state = {"prompt": {"kind": "replace", "input": "foo"}, "matches": [(0, 0, 3)], "cy": 0, "cx": 0}
    assert screen.search_progress(state) == "1 of 1"
    state["prompt"] = {"kind": "replace_with", "input": "", "find": "foo"}
    assert screen.search_progress(state) == "1 of 1"
    state["matches"] = []
    assert screen.search_progress(state) == "no matches"


def test_search_progress_text():
    state = {"prompt": {"kind": "search", "input": "foo"}, "matches": [(0, 0, 3)], "cy": 0, "cx": 0}
    assert screen.search_progress(state) == "1 of 1"
    state["matches"] = [(0, 0, 3), (1, 0, 3)]
    assert screen.search_progress(state) == "1 of 2"
    state["matches"] = []
    assert screen.search_progress(state) == "no matches"
    state["prompt"]["input"] = ""
    assert screen.search_progress(state) == ""
    state["prompt"] = {"kind": "open", "input": "x"}
    assert screen.search_progress(state) == ""
    state["prompt"] = None
    assert screen.search_progress(state) == ""
