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
    assert state["search_term"] == ""


def test_finish_search_jumps_to_first_match():
    state = editor.plain_state()
    state["lines"] = ["hello world", "world again"]
    state["prompt"] = {"kind": "search", "question": "Find: ", "input": "world"}
    editor.finish_search(state)
    assert state["search_term"] == "world"
    assert state["cy"] == 0
    assert state["cx"] == 6


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
