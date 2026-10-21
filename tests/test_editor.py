import os
import shutil
import tempfile

from grass import editor


def test_insert_text():
    state = editor.plain_state()
    editor.insert_text(state, "hi")
    assert state["lines"][0] == "hi"
    assert state["cx"] == 2
    assert state["modified"] is True


def test_enter_auto_indent():
    state = editor.plain_state()
    editor.insert_text(state, "    if ready:")
    editor.insert_newline(state)
    assert state["lines"][0] == "    if ready:"
    assert state["lines"][1] == "        "
    assert state["cy"] == 1
    assert state["cx"] == 8


def test_tab_inserts_spaces():
    state = editor.plain_state()
    editor.insert_tab(state)
    assert state["lines"][0] == "    "
    assert state["cx"] == 4


def test_backspace_deletes_character():
    state = editor.plain_state()
    editor.insert_text(state, "abc")
    editor.backspace(state)
    assert state["lines"][0] == "ab"
    assert state["cx"] == 2


def test_backspace_joins_lines():
    state = editor.plain_state()
    editor.insert_text(state, "one")
    editor.insert_newline(state)
    editor.insert_text(state, "two")
    editor.move_home(state)
    editor.backspace(state)
    assert state["lines"] == ["onetwo"]
    assert state["cy"] == 0
    assert state["cx"] == 3


def test_delete_joins_next_line():
    state = editor.plain_state()
    editor.insert_text(state, "one")
    editor.insert_newline(state)
    editor.insert_text(state, "two")
    editor.move_home(state)
    editor.move_up(state)
    state["cx"] = 3
    editor.delete_forward(state)
    assert state["lines"] == ["onetwo"]


def test_undo_restores_text():
    state = editor.plain_state()
    editor.insert_text(state, "hello")
    editor.undo(state)
    assert state["lines"] == [""]
    assert state["cx"] == 0


def test_redo_reapplies_text():
    state = editor.plain_state()
    editor.insert_text(state, "hello")
    editor.undo(state)
    editor.redo(state)
    assert state["lines"] == ["hello"]


def test_move_down_clamps_column():
    state = editor.plain_state()
    editor.insert_text(state, "long line")
    editor.insert_newline(state)
    editor.insert_text(state, "x")
    state["cy"] = 0
    state["cx"] = 9
    editor.move_down(state)
    assert state["cx"] == 1


def test_move_left_wraps_to_previous_line():
    state = editor.plain_state()
    editor.insert_text(state, "one")
    editor.insert_newline(state)
    editor.insert_text(state, "two")
    editor.move_home(state)
    editor.move_left(state)
    assert state["cy"] == 0
    assert state["cx"] == 3


def test_split_lines():
    lines = editor.split_lines("a\nb\n")
    assert lines == ["a", "b"]
    lines = editor.split_lines("")
    assert lines == [""]
    lines = editor.split_lines("a\tb")
    assert lines == ["a    b"]


def test_load_and_save_keep_missing_final_newline():
    root = tempfile.mkdtemp()
    try:
        path = os.path.join(root, "plain.txt")
        handle = open(path, "w")
        handle.write("one\ntwo")
        handle.close()
        state = editor.plain_state()
        editor.load_file(state, path)
        assert state["lines"] == ["one", "two"]
        assert state["final_newline"] is False
        assert state["modified"] is False
        state["cy"] = 1
        state["cx"] = 3
        editor.insert_text(state, "!")
        editor.save_file(state)
        handle = open(path, "r")
        text = handle.read()
        handle.close()
        assert text == "one\ntwo!"
    finally:
        shutil.rmtree(root)


def test_load_and_save_keep_final_newline():
    root = tempfile.mkdtemp()
    try:
        path = os.path.join(root, "plain.txt")
        handle = open(path, "w")
        handle.write("one\ntwo\n")
        handle.close()
        state = editor.plain_state()
        editor.load_file(state, path)
        assert state["final_newline"] is True
        editor.save_file(state)
        handle = open(path, "r")
        text = handle.read()
        handle.close()
        assert text == "one\ntwo\n"
    finally:
        shutil.rmtree(root)


def test_empty_file_roundtrip():
    root = tempfile.mkdtemp()
    try:
        path = os.path.join(root, "empty.txt")
        handle = open(path, "w")
        handle.close()
        state = editor.plain_state()
        editor.load_file(state, path)
        assert state["final_newline"] is False
        editor.save_file(state)
        handle = open(path, "r")
        text = handle.read()
        handle.close()
        assert text == ""
    finally:
        shutil.rmtree(root)


def test_quit_prompt_when_modified():
    state = editor.plain_state()
    state["path"] = "example.py"
    editor.insert_text(state, "x")
    editor.quit_editor(state)
    assert state["prompt"] is not None
    assert state["prompt"]["kind"] == "quit"


def test_quit_prompt_n_discards_and_quits():
    state = editor.plain_state()
    state["path"] = "example.py"
    editor.insert_text(state, "x")
    editor.quit_editor(state)
    editor.handle_key(state, "n")
    assert state["quit"] is True


def test_quit_prompt_y_failure_keeps_editor_open():
    state = editor.plain_state()
    state["path"] = "/no/such/folder/example.py"
    editor.insert_text(state, "x")
    editor.quit_editor(state)
    editor.handle_key(state, "y")
    assert state["quit"] is False
    assert state["modified"] is True


def test_open_prompt_asks_discard_when_modified():
    state = editor.plain_state()
    editor.insert_text(state, "x")
    state["prompt"] = {"kind": "open", "question": "Open: ", "input": "notes.txt"}
    editor.finish_open(state)
    assert state["prompt"] is not None
    assert state["prompt"]["kind"] == "discard_open"


def test_undo_key_restores_text():
    state = editor.plain_state()
    editor.handle_key(state, "a")
    editor.handle_key(state, "b")
    editor.handle_key(state, "c")
    editor.handle_key(state, "\x1a")
    assert state["lines"] == ["ab"]


def test_quit_immediately_when_clean():
    state = editor.plain_state()
    editor.quit_editor(state)
    assert state["quit"] is True


def test_quit_saves_untitled_via_save_as():
    state = editor.plain_state()
    editor.insert_text(state, "x")
    editor.quit_editor(state)
    assert state["prompt"] is not None
    assert state["prompt"]["kind"] == "save_as"
    assert state["prompt"]["then_quit"] is True


def test_save_untitled_opens_save_as_prompt():
    state = editor.plain_state()
    editor.insert_text(state, "x")
    editor.save_file(state)
    assert state["prompt"] is not None
    assert state["prompt"]["kind"] == "save_as"
    assert state["prompt"]["then_quit"] is False


def test_cut_line_removes_line_and_stores_clipboard():
    state = editor.plain_state()
    editor.insert_text(state, "one")
    editor.insert_newline(state)
    editor.insert_text(state, "two")
    state["cy"] = 0
    editor.cut_line(state)
    assert state["lines"] == ["two"]
    assert state["clipboard"] == "one"
    assert state["cy"] == 0


def test_paste_line_inserts_at_cursor():
    state = editor.plain_state()
    editor.insert_text(state, "hello")
    editor.cut_line(state)
    assert state["lines"] == [""]
    editor.paste_line(state)
    assert state["lines"] == ["hello"]
    assert state["cx"] == 5


def test_paste_without_clipboard():
    state = editor.plain_state()
    editor.paste_line(state)
    assert state["message"] == "Nothing to paste"


def test_cut_then_paste_round_trip_through_handle_key():
    state = editor.plain_state()
    editor.insert_text(state, "gone")
    editor.handle_key(state, "\x0b")
    assert state["lines"] == [""]
    editor.handle_key(state, "\x15")
    assert state["lines"] == ["gone"]


def test_search_prompt_prefilled_with_last_term():
    state = editor.plain_state()
    state["search_term"] = "foo"
    editor.start_search_prompt(state)
    assert state["prompt"]["kind"] == "search"
    assert state["prompt"]["input"] == "foo"


def test_ctrl_f_opens_search_prompt():
    state = editor.plain_state()
    editor.handle_key(state, "\x06")
    assert state["prompt"] is not None
    assert state["prompt"]["kind"] == "search"


def test_escape_clears_search():
    state = editor.plain_state()
    state["search_term"] = "foo"
    state["search_version"] = -1
    editor.handle_key(state, "\x1b")
    editor.handle_key(state, "x")
    assert state["search_term"] == ""


def test_normal_mode_arrow_moves_without_editing():
    state = editor.plain_state()
    state["lines"] = ["one", "two"]
    state["cy"] = 1
    state["cx"] = 2
    editor.handle_key(state, "\x1b")
    editor.handle_key(state, "[")
    editor.handle_key(state, "A")
    assert state["cy"] == 0
    assert state["lines"] == ["one", "two"]
    assert state["modified"] is False
    assert state["escape"] is None


def test_key_after_escape_is_typed():
    state = editor.plain_state()
    editor.handle_key(state, "\x1b")
    editor.handle_key(state, "x")
    assert state["lines"][0] == "x"
    assert state["modified"] is True


def test_finish_search_jumps_to_first_match():
    state = editor.plain_state()
    state["lines"] = ["hello world", "world again"]
    state["prompt"] = {"kind": "search", "question": "Find: ", "input": "world"}
    editor.finish_search(state)
    assert state["search_term"] == "world"
    assert state["cy"] == 0
    assert state["cx"] == 6


def test_search_prompt_updates_matches_while_typing():
    state = editor.plain_state()
    state["lines"] = ["alpha", "beta"]
    editor.start_search_prompt(state)
    editor.handle_key(state, "a")
    assert state["search_term"] == "a"
    assert len(state["matches"]) == 3
    editor.handle_key(state, "l")
    assert state["search_term"] == "al"
    assert len(state["matches"]) == 1


def test_search_prompt_backspace_updates_matches():
    state = editor.plain_state()
    state["lines"] = ["alpha", "beta"]
    editor.start_search_prompt(state)
    editor.handle_key(state, "a")
    editor.handle_key(state, "l")
    editor.handle_key(state, 127)
    assert state["search_term"] == "a"
    assert len(state["matches"]) == 3


def test_search_prompt_slides_to_match():
    state = editor.plain_state()
    state["lines"] = ["one", "two foo", "foo three"]
    state["cy"] = 0
    state["cx"] = 0
    editor.start_search_prompt(state)
    editor.handle_key(state, "f")
    assert state["cy"] == 1
    assert state["cx"] == 4
    assert state["prompt"]["kind"] == "search"


def test_search_prompt_returns_to_anchor_without_matches():
    state = editor.plain_state()
    state["lines"] = ["needle", "other"]
    state["cy"] = 1
    state["cx"] = 2
    editor.start_search_prompt(state)
    editor.handle_key(state, "n")
    assert state["cy"] == 0
    assert state["cx"] == 0
    editor.handle_key(state, "z")
    assert state["cy"] == 1
    assert state["cx"] == 2


def test_search_enter_keeps_live_match():
    state = editor.plain_state()
    state["lines"] = ["foo", "foo"]
    editor.start_search_prompt(state)
    editor.handle_key(state, "f")
    assert state["cy"] == 0
    assert state["cx"] == 0
    editor.handle_key(state, "\n")
    assert state["prompt"] is None
    assert state["message"] == "Match 1 of 2"


def test_search_cancel_restores_previous_term():
    state = editor.plain_state()
    state["lines"] = ["alpha", "beta"]
    state["search_term"] = "beta"
    state["search_version"] = -1
    editor.start_search_prompt(state)
    assert state["prompt"]["input"] == "beta"
    editor.handle_key(state, "x")
    assert state["search_term"] == "betax"
    editor.finish_escape(state)
    assert state["prompt"] is None
    assert state["search_term"] == "beta"


def test_search_again_without_term_opens_prompt():
    state = editor.plain_state()
    editor.search_again(state)
    assert state["prompt"]["kind"] == "search"


def test_search_again_with_term_finds_next():
    state = editor.plain_state()
    state["lines"] = ["foo", "foo"]
    state["search_term"] = "foo"
    state["search_version"] = -1
    editor.search_again(state)
    assert state["cy"] == 1
    assert state["cx"] == 0


def test_update_modified_clears_when_text_matches_saved():
    state = editor.plain_state()
    state["lines"] = ["["]
    state["saved_text"] = "["
    state["modified"] = True
    editor.update_modified(state)
    assert state["modified"] is False


def test_update_modified_marks_different_text():
    state = editor.plain_state()
    state["lines"] = ["["]
    state["saved_text"] = "x"
    state["modified"] = False
    editor.update_modified(state)
    assert state["modified"] is True


def test_delete_then_retype_is_clean_again():
    state = editor.plain_state()
    state["lines"] = ["["]
    state["saved_text"] = "["
    state["cx"] = 1
    editor.backspace(state)
    editor.update_modified(state)
    assert state["modified"] is True
    editor.insert_text(state, "[")
    editor.update_modified(state)
    assert state["modified"] is False


def test_fuzzy_filter_keeps_subsequence_matches():
    state = editor.plain_state()
    state["finder_root"] = "/project"
    state["finder_files"] = ["alpha.py", os.path.join("src", "gamma.py"), "beta.txt"]
    state["prompt"] = {"kind": "find_file", "question": "Find file: ", "input": "gma"}
    editor.refresh_finder(state)
    assert state["finder_matches"] == [os.path.join("src", "gamma.py")]
    assert state["finder_selected"] == 0


def test_finder_move_clamps_selection():
    state = editor.plain_state()
    state["finder_matches"] = ["a.py", "b.py"]
    state["finder_selected"] = 0
    editor.finder_move(state, -1)
    assert state["finder_selected"] == 0
    editor.finder_move(state, 9)
    assert state["finder_selected"] == 1


def test_find_project_root_walks_up_to_marker():
    root = tempfile.mkdtemp()
    try:
        handle = open(os.path.join(root, "pyproject.toml"), "w")
        handle.write("")
        handle.close()
        nested = os.path.join(root, "src", "deep")
        os.makedirs(nested)
        assert editor.find_project_root(nested) == os.path.abspath(root)
    finally:
        shutil.rmtree(root)


def test_start_finder_uses_project_root():
    root = tempfile.mkdtemp()
    try:
        handle = open(os.path.join(root, "pyproject.toml"), "w")
        handle.write("")
        handle.close()
        os.mkdir(os.path.join(root, "grass"))
        path = os.path.join(root, "grass", "editor.py")
        handle = open(path, "w")
        handle.write("x\n")
        handle.close()
        state = editor.plain_state()
        state["path"] = path
        editor.start_finder(state)
        assert state["finder_root"] == os.path.abspath(root)
    finally:
        shutil.rmtree(root)


def test_finder_ranks_basename_prefix_first():
    state = editor.plain_state()
    state["finder_root"] = "/project"
    state["finder_files"] = ["README.md", os.path.join("src", "editor.py")]
    state["prompt"] = {"kind": "find_file", "question": "Find file: ", "input": "ed"}
    editor.refresh_finder(state)
    assert state["finder_matches"][0] == os.path.join("src", "editor.py")


def test_collect_project_files_skips_hidden_and_noise():
    root = tempfile.mkdtemp()
    try:
        handle = open(os.path.join(root, "alpha.py"), "w")
        handle.write("a\n")
        handle.close()
        os.mkdir(os.path.join(root, "src"))
        handle = open(os.path.join(root, "src", "gamma.py"), "w")
        handle.write("g\n")
        handle.close()
        os.mkdir(os.path.join(root, ".hidden"))
        handle = open(os.path.join(root, ".hidden", "secret.py"), "w")
        handle.write("s\n")
        handle.close()
        os.mkdir(os.path.join(root, "__pycache__"))
        handle = open(os.path.join(root, "__pycache__", "junk.pyc"), "w")
        handle.write("j\n")
        handle.close()
        files = editor.collect_project_files(root)
        assert "alpha.py" in files
        assert os.path.join("src", "gamma.py") in files
        assert os.path.join(".hidden", "secret.py") not in files
        assert os.path.join("__pycache__", "junk.pyc") not in files
    finally:
        shutil.rmtree(root)


def test_finish_finder_opens_selected_file():
    root = tempfile.mkdtemp()
    try:
        path = os.path.join(root, "target.py")
        handle = open(path, "w")
        handle.write("print(1)\n")
        handle.close()
        state = editor.plain_state()
        state["finder_root"] = root
        state["finder_files"] = ["target.py"]
        state["prompt"] = {"kind": "find_file", "question": "Find file: ", "input": "tar"}
        editor.refresh_finder(state)
        editor.finish_finder(state)
        assert state["path"] == path
        assert state["lines"] == ["print(1)"]
        assert state["modified"] is False
    finally:
        shutil.rmtree(root)


def test_finish_finder_asks_before_discarding():
    state = editor.plain_state()
    state["modified"] = True
    state["finder_root"] = "/project"
    state["finder_matches"] = ["target.py"]
    state["finder_selected"] = 0
    state["prompt"] = {"kind": "find_file", "question": "Find file: ", "input": ""}
    editor.finish_finder(state)
    assert state["prompt"]["kind"] == "discard_open"
    assert state["prompt"]["path"] == os.path.join("/project", "target.py")


def test_ctrl_p_opens_finder():
    root = tempfile.mkdtemp()
    try:
        handle = open(os.path.join(root, "demo.py"), "w")
        handle.write("x\n")
        handle.close()
        state = editor.plain_state()
        state["path"] = os.path.join(root, "demo.py")
        editor.handle_key(state, "\x10")
        assert state["prompt"]["kind"] == "find_file"
        assert "demo.py" in state["finder_matches"]
    finally:
        shutil.rmtree(root)


def test_finish_escape_cancels_prompt():
    state = editor.plain_state()
    state["prompt"] = {"kind": "open", "question": "Open: ", "input": ""}
    state["escape"] = ""
    editor.finish_escape(state)
    assert state["prompt"] is None


def test_finder_arrow_sequence_moves_selection():
    state = editor.plain_state()
    state["finder_matches"] = ["a.py", "b.py"]
    state["finder_selected"] = 0
    state["prompt"] = {"kind": "find_file", "question": "Find file: ", "input": ""}
    editor.handle_key(state, "\x1b")
    editor.handle_key(state, "[")
    editor.handle_key(state, "B")
    assert state["finder_selected"] == 1
    assert state["prompt"]["kind"] == "find_file"
