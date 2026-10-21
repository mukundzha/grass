import os
import curses

from grass.highlight import language_name
from grass.screen import apply_window_title, draw, setup_screen
from grass.search import find_next, first_match_index, index_at_cursor, update_matches
from grass.tabs import TAB_WIDTH, char_index_at_column, display_column

MAX_UNDO = 200
MAX_FINDER_FILES = 5000
FINDER_SKIP_DIRS = ("__pycache__", "node_modules", "venv", "env", "dist", "build")
PROJECT_MARKERS = (".git", "pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml", "go.mod", "Makefile")


def plain_state():
    state = {
        "lines": [""],
        "path": None,
        "language": "text",
        "modified": False,
        "cx": 0,
        "cy": 0,
        "top": 0,
        "left": 0,
        "message": "",
        "prompt": None,
        "saved_text": "",
        "final_newline": False,
        "undo_stack": [],
        "redo_stack": [],
        "version": 0,
        "spans": [],
        "spans_version": -1,
        "search_term": "",
        "matches": [],
        "search_version": -1,
        "clipboard": None,
        "escape": None,
        "finder_files": [],
        "finder_matches": [],
        "finder_selected": 0,
        "finder_root": "",
        "title": None,
        "quit": False,
    }
    return state


def current_text(state):
    text = "\n".join(state["lines"])
    if state["final_newline"]:
        text = text + "\n"
    return text


def update_modified(state):
    if current_text(state) == state["saved_text"]:
        state["modified"] = False
    else:
        state["modified"] = True


def push_undo(state):
    record = (list(state["lines"]), state["cx"], state["cy"])
    state["undo_stack"].append(record)
    if len(state["undo_stack"]) > MAX_UNDO:
        state["undo_stack"].pop(0)
    state["redo_stack"] = []
    state["modified"] = True
    state["version"] = state["version"] + 1


def undo(state):
    if len(state["undo_stack"]) == 0:
        state["message"] = "Nothing to undo"
        return
    current = (list(state["lines"]), state["cx"], state["cy"])
    state["redo_stack"].append(current)
    record = state["undo_stack"].pop()
    state["lines"] = record[0]
    state["cx"] = record[1]
    state["cy"] = record[2]
    state["modified"] = True
    state["version"] = state["version"] + 1
    state["message"] = "Undo"


def redo(state):
    if len(state["redo_stack"]) == 0:
        state["message"] = "Nothing to redo"
        return
    current = (list(state["lines"]), state["cx"], state["cy"])
    state["undo_stack"].append(current)
    record = state["redo_stack"].pop()
    state["lines"] = record[0]
    state["cx"] = record[1]
    state["cy"] = record[2]
    state["modified"] = True
    state["version"] = state["version"] + 1
    state["message"] = "Redo"


def insert_text(state, text):
    push_undo(state)
    line = state["lines"][state["cy"]]
    before = line[:state["cx"]]
    after = line[state["cx"]:]
    state["lines"][state["cy"]] = before + text + after
    state["cx"] = state["cx"] + len(text)


def insert_tab(state):
    line = state["lines"][state["cy"]]
    indent = leading_indent(line)
    if indent.startswith("\t"):
        insert_text(state, "\t")
        return
    column = display_column(line, state["cx"])
    spaces = TAB_WIDTH - (column % TAB_WIDTH)
    insert_text(state, " " * spaces)


def leading_indent(text):
    result = ""
    for character in text:
        if character == " " or character == "\t":
            result = result + character
        else:
            break
    return result


def indent_unit(indent):
    if "\t" in indent:
        return "\t"
    return " " * TAB_WIDTH


def insert_newline(state):
    push_undo(state)
    line = state["lines"][state["cy"]]
    before = line[:state["cx"]]
    after = line[state["cx"]:]
    indent = leading_indent(line)
    if before.rstrip().endswith(":"):
        indent = indent + indent_unit(indent)
    state["lines"][state["cy"]] = before
    state["lines"].insert(state["cy"] + 1, indent + after)
    state["cy"] = state["cy"] + 1
    state["cx"] = len(indent)


def backspace(state):
    line = state["lines"][state["cy"]]
    if state["cx"] > 0:
        push_undo(state)
        before = line[:state["cx"] - 1]
        after = line[state["cx"]:]
        state["lines"][state["cy"]] = before + after
        state["cx"] = state["cx"] - 1
        return
    if state["cy"] > 0:
        push_undo(state)
        previous = state["lines"][state["cy"] - 1]
        state["lines"][state["cy"] - 1] = previous + line
        del state["lines"][state["cy"]]
        state["cy"] = state["cy"] - 1
        state["cx"] = len(previous)


def delete_forward(state):
    line = state["lines"][state["cy"]]
    if state["cx"] < len(line):
        push_undo(state)
        before = line[:state["cx"]]
        after = line[state["cx"] + 1:]
        state["lines"][state["cy"]] = before + after
        return
    if state["cy"] < len(state["lines"]) - 1:
        push_undo(state)
        next_line = state["lines"][state["cy"] + 1]
        state["lines"][state["cy"]] = line + next_line
        del state["lines"][state["cy"] + 1]


def cut_line(state):
    push_undo(state)
    state["clipboard"] = state["lines"][state["cy"]]
    del state["lines"][state["cy"]]
    if len(state["lines"]) == 0:
        state["lines"].append("")
    if state["cy"] >= len(state["lines"]):
        state["cy"] = len(state["lines"]) - 1
    clamp_column(state)
    state["message"] = "Cut line"


def paste_line(state):
    if state["clipboard"] is None:
        state["message"] = "Nothing to paste"
        return
    push_undo(state)
    if len(state["lines"]) == 1 and state["lines"][0] == "":
        state["lines"][0] = state["clipboard"]
    else:
        state["lines"].insert(state["cy"], state["clipboard"])
    state["cx"] = len(state["clipboard"])
    state["message"] = "Pasted line"


def clamp_column(state):
    line = state["lines"][state["cy"]]
    if state["cx"] > len(line):
        state["cx"] = len(line)


def move_left(state):
    if state["cx"] > 0:
        state["cx"] = state["cx"] - 1
        return
    if state["cy"] > 0:
        state["cy"] = state["cy"] - 1
        state["cx"] = len(state["lines"][state["cy"]])


def move_right(state):
    line = state["lines"][state["cy"]]
    if state["cx"] < len(line):
        state["cx"] = state["cx"] + 1
        return
    if state["cy"] < len(state["lines"]) - 1:
        state["cy"] = state["cy"] + 1
        state["cx"] = 0


def move_to_line(state, line_index):
    target = display_column(state["lines"][state["cy"]], state["cx"])
    state["cy"] = line_index
    state["cx"] = char_index_at_column(state["lines"][line_index], target)


def move_up(state):
    if state["cy"] > 0:
        move_to_line(state, state["cy"] - 1)


def move_down(state):
    if state["cy"] < len(state["lines"]) - 1:
        move_to_line(state, state["cy"] + 1)


def move_home(state):
    state["cx"] = 0


def move_end(state):
    state["cx"] = len(state["lines"][state["cy"]])


def view_rows():
    rows = curses.LINES - 2
    if rows < 1:
        rows = 1
    return rows


def page_up(state):
    line_index = state["cy"] - view_rows()
    if line_index < 0:
        line_index = 0
    move_to_line(state, line_index)


def page_down(state):
    line_index = state["cy"] + view_rows()
    last = len(state["lines"]) - 1
    if line_index > last:
        line_index = last
    move_to_line(state, line_index)


def folder_exists(path):
    folder = os.path.dirname(path)
    if folder == "":
        folder = "."
    return os.path.isdir(folder)


def split_lines(text):
    lines = text.splitlines()
    if len(lines) == 0:
        lines = [""]
    return lines


def reset_buffer(state):
    state["lines"] = [""]
    state["final_newline"] = False
    state["cx"] = 0
    state["cy"] = 0
    state["top"] = 0
    state["left"] = 0
    state["modified"] = False
    state["saved_text"] = ""
    state["undo_stack"] = []
    state["redo_stack"] = []
    state["version"] = state["version"] + 1


def load_file(state, path):
    if os.path.isdir(path):
        state["message"] = "Cannot open: that is a folder"
        return
    if os.path.exists(path):
        try:
            handle = open(path, "r", encoding="utf-8")
            text = handle.read()
            handle.close()
        except OSError as error:
            state["message"] = "Cannot open: " + str(error)
            return
        except UnicodeError:
            state["message"] = "Cannot open: not a text file"
            return
        reset_buffer(state)
        state["lines"] = split_lines(text)
        state["final_newline"] = text.endswith("\n")
        state["saved_text"] = current_text(state)
        state["path"] = path
        state["language"] = language_name(path)
        state["message"] = "Opened " + path
        return
    reset_buffer(state)
    state["path"] = path
    state["language"] = language_name(path)
    state["message"] = "New file: press Ctrl-S to save"


def save_file(state):
    path = state["path"]
    if path is None:
        start_save_as_prompt(state, False)
        return
    if not folder_exists(path):
        state["message"] = "Cannot save: folder does not exist"
        return
    text = current_text(state)
    try:
        handle = open(path, "w", encoding="utf-8")
        handle.write(text)
        handle.close()
    except OSError as error:
        state["message"] = "Cannot save: " + str(error)
        return
    state["modified"] = False
    state["saved_text"] = current_text(state)
    state["message"] = "Saved " + path


def start_open_prompt(state):
    state["prompt"] = {
        "kind": "open",
        "question": "Open: ",
        "input": "",
    }


def collect_project_files(root):
    files = []
    for walk_root, dirs, names in os.walk(root):
        kept = []
        for name in dirs:
            if name.startswith("."):
                continue
            if name in FINDER_SKIP_DIRS:
                continue
            if name.endswith(".egg-info"):
                continue
            kept.append(name)
        dirs[:] = kept
        for name in names:
            if name.startswith("."):
                continue
            full = os.path.join(walk_root, name)
            files.append(os.path.relpath(full, root))
            if len(files) >= MAX_FINDER_FILES:
                return files
    return files


def is_subsequence(text, query):
    position = 0
    for character in query:
        found = text.find(character, position)
        if found == -1:
            return False
        position = found + 1
    return True


def find_project_root(start):
    current = os.path.abspath(start)
    while True:
        for marker in PROJECT_MARKERS:
            if os.path.exists(os.path.join(current, marker)):
                return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start)
        current = parent


def fuzzy_score(path, query):
    name = os.path.basename(path)
    if name.startswith(query):
        return 0
    if query in name:
        return 1
    if is_subsequence(name, query):
        return 2
    if query in path:
        return 3
    if is_subsequence(path, query):
        return 4
    return None


def refresh_finder(state):
    query = state["prompt"]["input"].lower()
    matches = []
    for path in state["finder_files"]:
        score = fuzzy_score(path.lower(), query)
        if score is None:
            continue
        matches.append((score, len(path), path))
    matches.sort()
    state["finder_matches"] = []
    for entry in matches:
        state["finder_matches"].append(entry[2])
    state["finder_selected"] = 0


def start_finder(state):
    path = state["path"]
    if path is None:
        base = os.getcwd()
    else:
        base = os.path.dirname(os.path.abspath(path))
    root = find_project_root(base)
    state["finder_root"] = root
    state["finder_files"] = collect_project_files(root)
    state["prompt"] = {
        "kind": "find_file",
        "question": "Find file: ",
        "input": "",
    }
    refresh_finder(state)


def finder_move(state, delta):
    count = len(state["finder_matches"])
    if count == 0:
        return
    selected = state["finder_selected"] + delta
    if selected < 0:
        selected = 0
    if selected >= count:
        selected = count - 1
    state["finder_selected"] = selected


def finish_finder(state):
    matches = state["finder_matches"]
    if len(matches) == 0:
        state["prompt"] = None
        state["message"] = "No files"
        return
    selected = state["finder_selected"]
    path = os.path.join(state["finder_root"], matches[selected])
    state["prompt"] = {"kind": "open", "question": "Open: ", "input": path}
    finish_open(state)


def start_save_as_prompt(state, then_quit):
    guessed = state["path"]
    if guessed is None:
        guessed = ""
    state["prompt"] = {
        "kind": "save_as",
        "question": "Save as: ",
        "input": guessed,
        "then_quit": then_quit,
    }


def quit_editor(state):
    if not state["modified"]:
        state["quit"] = True
        return
    if state["path"] is None:
        start_save_as_prompt(state, True)
        return
    state["prompt"] = {
        "kind": "quit",
        "question": "Save changes before quitting? (y = save, n = discard) ",
        "input": "",
    }


def finish_open(state):
    prompt = state["prompt"]
    typed = prompt["input"].strip()
    state["prompt"] = None
    if typed == "":
        state["message"] = "Cancelled"
        return
    path = os.path.expanduser(typed)
    if state["modified"]:
        state["prompt"] = {
            "kind": "discard_open",
            "question": "Discard unsaved changes? (y/n) ",
            "input": "",
            "path": path,
        }
        return
    load_file(state, path)


def finish_save_as(state):
    prompt = state["prompt"]
    typed = prompt["input"].strip()
    state["prompt"] = None
    if typed == "":
        state["message"] = "Cancelled"
        return
    path = os.path.expanduser(typed)
    if os.path.isdir(path):
        state["message"] = "Cannot save: that is a folder"
        return
    if not folder_exists(path):
        state["message"] = "Cannot save: folder does not exist"
        return
    state["path"] = path
    state["language"] = language_name(path)
    save_file(state)
    if prompt["then_quit"] and not state["modified"]:
        state["quit"] = True


def start_search_prompt(state):
    state["prompt"] = {
        "kind": "search",
        "question": "Find: ",
        "input": state["search_term"],
        "original_term": state["search_term"],
        "anchor_cy": state["cy"],
        "anchor_cx": state["cx"],
    }


def restore_search(state, prompt):
    state["search_term"] = prompt.get("original_term", "")
    state["search_version"] = -1
    if "anchor_cy" in prompt:
        state["cy"] = prompt["anchor_cy"]
        state["cx"] = prompt["anchor_cx"]


def update_search_prompt(state):
    prompt = state["prompt"]
    if prompt is None or prompt["kind"] != "search":
        return
    state["search_term"] = prompt["input"]
    state["search_version"] = -1
    update_matches(state)
    anchor_cy = prompt["anchor_cy"]
    anchor_cx = prompt["anchor_cx"]
    if len(state["matches"]) == 0:
        state["cy"] = anchor_cy
        state["cx"] = anchor_cx
        return
    index = first_match_index(state["matches"], anchor_cy, anchor_cx)
    match = state["matches"][index]
    state["cy"] = match[0]
    state["cx"] = match[1]


def finish_search(state):
    prompt = state["prompt"]
    typed = prompt["input"].strip()
    state["prompt"] = None
    if typed == "":
        restore_search(state, prompt)
        state["message"] = "Cancelled"
        return
    state["search_term"] = typed
    state["search_version"] = -1
    update_matches(state)
    index = index_at_cursor(state)
    if index == -1:
        find_next(state)
        return
    state["message"] = "Match " + str(index + 1) + " of " + str(len(state["matches"]))


def search_again(state):
    if state["search_term"] == "":
        start_search_prompt(state)
        return
    find_next(state)


def clear_search(state):
    if state["search_term"] == "":
        return
    state["search_term"] = ""
    state["search_version"] = -1
    state["message"] = "Search cleared"


def answer_yes(state, prompt):
    kind = prompt["kind"]
    state["prompt"] = None
    if kind == "quit":
        save_file(state)
        if not state["modified"]:
            state["quit"] = True
        return
    if kind == "discard_open":
        load_file(state, prompt["path"])


def answer_no(state, prompt):
    kind = prompt["kind"]
    state["prompt"] = None
    if kind == "quit":
        state["quit"] = True
        return
    state["message"] = "Cancelled"


def finish_prompt(state):
    kind = state["prompt"]["kind"]
    if kind == "open":
        finish_open(state)
        return
    if kind == "save_as":
        finish_save_as(state)
        return
    if kind == "search":
        finish_search(state)
        return
    if kind == "find_file":
        finish_finder(state)


def handle_prompt_control(state, prompt, key):
    if prompt["kind"] == "find_file":
        if key == curses.KEY_UP:
            finder_move(state, -1)
            return
        if key == curses.KEY_DOWN:
            finder_move(state, 1)
            return
    if key == 27:
        if prompt["kind"] == "search":
            restore_search(state, prompt)
        state["prompt"] = None
        state["message"] = "Cancelled"
        return
    if key == 10 or key == 13 or key == curses.KEY_ENTER:
        finish_prompt(state)
        return
    if key == curses.KEY_BACKSPACE or key == 8 or key == 127:
        text = prompt["input"]
        if len(text) > 0:
            prompt["input"] = text[:-1]
            if prompt["kind"] == "find_file":
                refresh_finder(state)
            if prompt["kind"] == "search":
                update_search_prompt(state)


def handle_prompt_key(state, key):
    prompt = state["prompt"]
    if isinstance(key, int):
        handle_prompt_control(state, prompt, key)
        return
    if not isinstance(key, str):
        return
    if len(key) == 1:
        code = ord(key)
        if code < 32 or code == 127:
            handle_prompt_control(state, prompt, code)
            return
    kind = prompt["kind"]
    if kind == "open" or kind == "save_as":
        prompt["input"] = prompt["input"] + key
        return
    if kind == "search":
        prompt["input"] = prompt["input"] + key
        update_search_prompt(state)
        return
    if kind == "find_file":
        prompt["input"] = prompt["input"] + key
        refresh_finder(state)
        return
    if kind == "quit" or kind == "discard_open":
        if key == "y" or key == "Y":
            answer_yes(state, prompt)
            return
        if key == "n" or key == "N":
            answer_no(state, prompt)


HANDLERS = {
    3: quit_editor,
    6: start_search_prompt,
    8: backspace,
    9: insert_tab,
    10: insert_newline,
    11: cut_line,
    13: insert_newline,
    15: start_open_prompt,
    16: start_finder,
    17: quit_editor,
    18: redo,
    19: save_file,
    21: paste_line,
    26: undo,
    127: backspace,
    curses.KEY_BACKSPACE: backspace,
    curses.KEY_DC: delete_forward,
    curses.KEY_LEFT: move_left,
    curses.KEY_RIGHT: move_right,
    curses.KEY_UP: move_up,
    curses.KEY_DOWN: move_down,
    curses.KEY_HOME: move_home,
    curses.KEY_END: move_end,
    curses.KEY_PPAGE: page_up,
    curses.KEY_NPAGE: page_down,
    curses.KEY_ENTER: insert_newline,
    curses.KEY_F3: search_again,
}

ESCAPE_SEQUENCES = {
    "[A": curses.KEY_UP,
    "[B": curses.KEY_DOWN,
    "[C": curses.KEY_RIGHT,
    "[D": curses.KEY_LEFT,
    "OA": curses.KEY_UP,
    "OB": curses.KEY_DOWN,
    "OC": curses.KEY_RIGHT,
    "OD": curses.KEY_LEFT,
    "[H": curses.KEY_HOME,
    "[F": curses.KEY_END,
    "OH": curses.KEY_HOME,
    "OF": curses.KEY_END,
    "[1~": curses.KEY_HOME,
    "[4~": curses.KEY_END,
    "[3~": curses.KEY_DC,
    "[5~": curses.KEY_PPAGE,
    "[6~": curses.KEY_NPAGE,
}


def escape_is_prefix(buffer):
    for sequence in ESCAPE_SEQUENCES:
        if sequence.startswith(buffer):
            return True
    return False


def finish_escape(state):
    state["escape"] = None
    prompt = state["prompt"]
    if prompt is not None:
        if prompt["kind"] == "search":
            restore_search(state, prompt)
        state["prompt"] = None
        state["message"] = "Cancelled"
        return
    clear_search(state)


def handle_escape_key(state, key):
    prefix = state["escape"]
    if not isinstance(key, str) or len(key) != 1:
        finish_escape(state)
        return
    buffer = prefix + key
    if buffer in ESCAPE_SEQUENCES:
        state["escape"] = None
        handle_key(state, ESCAPE_SEQUENCES[buffer])
        return
    if escape_is_prefix(buffer):
        state["escape"] = buffer
        return
    finish_escape(state)
    handle_key(state, key)


def handle_key(state, key):
    if state["escape"] is not None:
        handle_escape_key(state, key)
        return
    if isinstance(key, int):
        if key == 27:
            state["escape"] = ""
            return
    if isinstance(key, str) and len(key) == 1:
        if ord(key) == 27:
            state["escape"] = ""
            return
    if state["prompt"] is not None:
        handle_prompt_key(state, key)
        return
    if isinstance(key, int):
        handler = HANDLERS.get(key)
        if handler is not None:
            handler(state)
        return
    if not isinstance(key, str):
        return
    if len(key) == 1:
        code = ord(key)
        if code < 32 or code == 127:
            handler = HANDLERS.get(code)
            if handler is not None:
                handler(state)
            return
    insert_text(state, key)


def run(screen, path):
    setup_screen(screen)
    state = plain_state()
    if path is not None:
        load_file(state, path)
    while not state["quit"]:
        apply_window_title(state)
        draw(screen, state)
        if state["escape"] is None:
            screen.timeout(-1)
        else:
            screen.timeout(25)
        try:
            key = screen.get_wch()
        except curses.error:
            if state["escape"] is not None:
                finish_escape(state)
            continue
        state["message"] = ""
        handle_key(state, key)
        update_modified(state)
