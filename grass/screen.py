import curses
import os
import sys

from grass import VERSION
from grass.highlight import cached_spans
from grass.search import index_at_cursor, update_matches
from grass.tabs import display_column, expand_tabs

STRIP_BACKGROUND = 236
STATUS_BACKGROUND = 237
FINDER_ROWS = 8

REVERSE_NAMES = ("status", "status_name", "status_dim", "status_modified", "match", "match_current")

PROMPT_PREFIX = "❯ "

SPLASH_ART = [
    " ██████╗ ██████╗  █████╗ ███████╗███████╗",
    "██╔════╝ ██╔══██╗██╔══██╗██╔════╝██╔════╝",
    "██║  ███╗██████╔╝███████║███████╗███████╗",
    "╚██████╔╝██╔══██╗██╔══██║╚════██║╚════██║",
    " ╚═════╝ ██║  ██║██║  ██║███████║███████║",
]

PALETTE = [
    ("text", 187, -1),
    ("gutter", 243, STRIP_BACKGROUND),
    ("gutter_current", 108, -1),
    ("comment", 243, -1),
    ("docstring", 108, -1),
    ("string", 180, -1),
    ("number", 216, -1),
    ("keyword", 150, -1),
    ("function", 222, -1),
    ("classname", 109, -1),
    ("builtin", 110, -1),
    ("decorator", 139, -1),
    ("operator", 245, -1),
    ("error", 167, -1),
    ("message", 245, -1),
    ("prompt", 253, -1),
    ("status", 187, STATUS_BACKGROUND),
    ("status_name", 150, STATUS_BACKGROUND),
    ("status_dim", 245, STATUS_BACKGROUND),
    ("status_modified", 216, STATUS_BACKGROUND),
    ("strip", 187, STRIP_BACKGROUND),
    ("accent", 108, -1),
    ("match", 187, 58),
    ("match_current", 236, 180),
]

BASIC_FOREGROUNDS = {
    "text": curses.COLOR_WHITE,
    "gutter": curses.COLOR_BLUE,
    "gutter_current": curses.COLOR_GREEN,
    "comment": curses.COLOR_CYAN,
    "docstring": curses.COLOR_CYAN,
    "string": curses.COLOR_YELLOW,
    "number": curses.COLOR_MAGENTA,
    "keyword": curses.COLOR_GREEN,
    "function": curses.COLOR_YELLOW,
    "classname": curses.COLOR_CYAN,
    "builtin": curses.COLOR_BLUE,
    "decorator": curses.COLOR_MAGENTA,
    "operator": curses.COLOR_WHITE,
    "error": curses.COLOR_RED,
    "message": curses.COLOR_WHITE,
    "prompt": curses.COLOR_WHITE,
    "status": curses.COLOR_GREEN,
    "status_name": curses.COLOR_GREEN,
    "status_dim": curses.COLOR_CYAN,
    "status_modified": curses.COLOR_YELLOW,
    "strip": curses.COLOR_WHITE,
    "accent": curses.COLOR_GREEN,
    "match": curses.COLOR_YELLOW,
    "match_current": curses.COLOR_YELLOW,
}

ATTRS = {}
CURRENT_ATTRS = {}


def setup_screen(screen):
    try:
        curses.raw()
    except curses.error:
        pass
    screen.keypad(True)
    try:
        curses.set_escdelay(25)
    except AttributeError:
        pass
    except curses.error:
        pass
    try:
        curses.curs_set(1)
    except curses.error:
        pass
    try:
        sys.stdout.write("\x1b[r\x1b[?7l\x1b[5 q")
        sys.stdout.flush()
    except OSError:
        pass
    setup_colors()


def setup_colors():
    ATTRS.clear()
    CURRENT_ATTRS.clear()
    if not curses.has_colors():
        setup_plain_colors()
        return
    curses.start_color()
    try:
        curses.use_default_colors()
        background = -1
    except curses.error:
        background = curses.COLOR_BLACK
    if curses.COLORS >= 256:
        setup_256_colors(background)
    else:
        setup_basic_colors(background)


def setup_plain_colors():
    for entry in PALETTE:
        name = entry[0]
        ATTRS[name] = curses.A_NORMAL
        CURRENT_ATTRS[name] = curses.A_UNDERLINE
    for name in REVERSE_NAMES:
        ATTRS[name] = curses.A_REVERSE
        CURRENT_ATTRS[name] = curses.A_REVERSE


def setup_256_colors(background):
    number = 1
    for entry in PALETTE:
        name = entry[0]
        foreground = entry[1]
        pair_background = entry[2]
        if pair_background == -1:
            pair_background = background
        curses.init_pair(number, foreground, pair_background)
        ATTRS[name] = curses.color_pair(number)
        number = number + 1
    for entry in PALETTE:
        name = entry[0]
        foreground = entry[1]
        curses.init_pair(number, foreground, STRIP_BACKGROUND)
        CURRENT_ATTRS[name] = curses.color_pair(number)
        number = number + 1


def setup_basic_colors(background):
    number = 1
    for entry in PALETTE:
        name = entry[0]
        foreground = BASIC_FOREGROUNDS[name]
        curses.init_pair(number, foreground, background)
        normal = curses.color_pair(number)
        if name in REVERSE_NAMES:
            normal = normal | curses.A_REVERSE
        ATTRS[name] = normal
        CURRENT_ATTRS[name] = normal | curses.A_UNDERLINE
        number = number + 1


def attr(name):
    return ATTRS[name]


def attr_current(name):
    return CURRENT_ATTRS[name]


def safe_addstr(screen, row, column, text, style):
    height, width = screen.getmaxyx()
    if row < 0 or row >= height:
        return
    if column >= width:
        return
    if column < 0:
        cut = -column
        text = text[cut:]
        column = 0
    if text == "":
        return
    room = width - column
    if len(text) > room:
        text = text[:room]
    try:
        screen.addstr(row, column, text, style)
    except curses.error:
        pass


def fill_row(screen, row, width, color_name):
    try:
        screen.addstr(row, 0, " " * width, attr(color_name))
    except curses.error:
        pass


def gutter_width(state):
    count = len(state["lines"])
    digits = len(str(count))
    if digits < 2:
        digits = 2
    return digits + 1


def text_area_width(state, width):
    text_width = width - gutter_width(state) - 1
    if text_width < 1:
        text_width = 1
    return text_width


def is_pristine(state):
    if state["path"] is not None:
        return False
    if state["modified"]:
        return False
    if len(state["lines"]) != 1:
        return False
    if state["lines"][0] != "":
        return False
    return True


def window_title(state):
    name = state["path"]
    if name is None:
        name = "(untitled)"
    else:
        name = os.path.basename(name)
    title = "grass · " + name
    if state["modified"]:
        title = title + " •"
    return title


def set_title(title):
    try:
        sys.stdout.write("\x1b]2;" + title + "\x07")
        sys.stdout.flush()
    except OSError:
        pass


def apply_window_title(state):
    title = window_title(state)
    if state["title"] == title:
        return
    state["title"] = title
    set_title(title)


def message_color(text):
    if text.startswith("Cannot") or text.startswith("Not found"):
        return "error"
    if text.startswith("Saved"):
        return "accent"
    return "message"


def splash_lines(width):
    lines = []
    if width >= 46:
        index = 1
        for row in SPLASH_ART:
            if index <= 3:
                lines.append((row, "keyword"))
            else:
                lines.append((row, "accent"))
            index = index + 1
    else:
        lines.append(("grass", "keyword"))
    lines.append(("", "text"))
    lines.append(("❧ a calm terminal editor", "docstring"))
    lines.append(("v" + VERSION + " · Meadow", "comment"))
    lines.append(("", "text"))
    if width >= 46:
        lines.append(("Ctrl-S save    Ctrl-O open    Ctrl-F find    Ctrl-Q quit", "comment"))
    else:
        lines.append(("Ctrl-S save  Ctrl-O open  Ctrl-F find", "comment"))
    return lines


def draw_splash(screen, state, height, width):
    view_rows = height - 2
    lines = splash_lines(width)
    start_row = (view_rows - len(lines)) // 2
    if start_row < 0:
        start_row = 0
    row_index = 0
    for entry in lines:
        text = entry[0]
        color = entry[1]
        row = start_row + row_index
        if text != "" and row < view_rows:
            column = (width - len(text)) // 2
            if column < 0:
                column = 0
            safe_addstr(screen, row, column, text, attr(color))
        row_index = row_index + 1


def scrollbar_thumb(top, total, view_rows):
    thumb_size = view_rows * view_rows // total
    if thumb_size < 1:
        thumb_size = 1
    travel = view_rows - thumb_size
    max_top = total - view_rows
    start = 0
    if max_top > 0 and travel > 0:
        start = top * travel // max_top
    return start, thumb_size


def draw_scrollbar(screen, state, height, width):
    view_rows = height - 2
    total = len(state["lines"])
    if total <= view_rows:
        return
    if view_rows < 1:
        return
    thumb = scrollbar_thumb(state["top"], total, view_rows)
    thumb_start = thumb[0]
    thumb_size = thumb[1]
    column = width - 1
    row = 0
    while row < view_rows:
        if row >= thumb_start and row < thumb_start + thumb_size:
            safe_addstr(screen, row, column, "│", attr("accent"))
        row = row + 1


def sync_scroll(state, height, width):
    view_rows = height - 2
    if view_rows < 1:
        view_rows = 1
    if state["cy"] < state["top"]:
        state["top"] = state["cy"]
    if state["cy"] >= state["top"] + view_rows:
        state["top"] = state["cy"] - view_rows + 1
    text_width = text_area_width(state, width)
    cursor_column = display_column(state["lines"][state["cy"]], state["cx"])
    if cursor_column < state["left"]:
        state["left"] = cursor_column
    if cursor_column >= state["left"] + text_width:
        state["left"] = cursor_column - text_width + 1


def draw(screen, state):
    height, width = screen.getmaxyx()
    screen.erase()
    if height >= 3 and width >= 4:
        sync_scroll(state, height, width)
        update_matches(state)
        if is_pristine(state):
            draw_splash(screen, state, height, width)
        else:
            draw_text_area(screen, state, height, width)
            draw_scrollbar(screen, state, height, width)
        draw_finder(screen, state, height, width)
        draw_message_bar(screen, state, height, width)
        draw_status_bar(screen, state, height, width)
        place_cursor(screen, state, height, width)
    try:
        screen.refresh()
    except curses.error:
        pass


def draw_text_area(screen, state, height, width):
    gutter = gutter_width(state)
    text_width = text_area_width(state, width)
    view_rows = height - 2
    row = 0
    while row < view_rows:
        line_index = state["top"] + row
        if line_index >= len(state["lines"]):
            break
        draw_text_row(screen, state, row, line_index, gutter, text_width, width)
        row = row + 1


def draw_text_row(screen, state, row, line_index, gutter, text_width, width):
    on_cursor = False
    if line_index == state["cy"]:
        on_cursor = True
    if on_cursor:
        fill_row(screen, row, width, "strip")
    number_text = str(line_index + 1).rjust(gutter - 1)
    if on_cursor:
        safe_addstr(screen, row, 0, number_text + " ", attr_current("gutter_current"))
    else:
        safe_addstr(screen, row, 0, number_text + " ", attr("gutter"))
    draw_highlights(screen, state, row, line_index, gutter, text_width, on_cursor)


def draw_highlights(screen, state, row, line_index, gutter, text_width, on_cursor):
    line = state["lines"][line_index]
    expanded = expand_tabs(line)
    spans = cached_spans(state)
    line_spans = []
    if line_index < len(spans):
        line_spans = spans[line_index]
    left = state["left"]
    visible_end = left + text_width
    if len(line_spans) == 0:
        visible = expanded[left:visible_end]
        if on_cursor:
            safe_addstr(screen, row, gutter, visible, attr_current("text"))
        else:
            safe_addstr(screen, row, gutter, visible, attr("text"))
    else:
        for span in line_spans:
            start = display_column(line, span[0])
            end = display_column(line, span[0] + span[1])
            color = span[2]
            if end <= left:
                continue
            if start >= visible_end:
                continue
            take_start = start
            if take_start < left:
                take_start = left
            take_end = end
            if take_end > visible_end:
                take_end = visible_end
            piece = expanded[take_start:take_end]
            column = gutter + (take_start - left)
            if on_cursor:
                safe_addstr(screen, row, column, piece, attr_current(color))
            else:
                safe_addstr(screen, row, column, piece, attr(color))
    draw_matches(screen, state, row, line_index, gutter, text_width)


def draw_matches(screen, state, row, line_index, gutter, text_width):
    matches = state["matches"]
    if len(matches) == 0:
        return
    line = state["lines"][line_index]
    expanded = expand_tabs(line)
    left = state["left"]
    visible_end = left + text_width
    for match in matches:
        if match[0] != line_index:
            continue
        start = display_column(line, match[1])
        end = display_column(line, match[1] + match[2])
        if end <= left:
            continue
        if start >= visible_end:
            continue
        take_start = start
        if take_start < left:
            take_start = left
        take_end = end
        if take_end > visible_end:
            take_end = visible_end
        color = "match"
        if line_index == state["cy"] and state["cx"] >= match[1] and state["cx"] < match[1] + match[2]:
            color = "match_current"
        piece = expanded[take_start:take_end]
        column = gutter + (take_start - left)
        safe_addstr(screen, row, column, piece, attr(color))


def draw_finder(screen, state, height, width):
    prompt = state["prompt"]
    if prompt is None or prompt["kind"] != "find_file":
        return
    matches = state["finder_matches"]
    selected = state["finder_selected"]
    start = selected - FINDER_ROWS + 1
    if start < 0:
        start = 0
    row = height - 3
    stop = height - 3 - FINDER_ROWS
    while row > stop and row >= 0:
        fill_row(screen, row, width, "strip")
        row = row - 1
    index = start
    row = height - 3
    while index < len(matches) and row >= 0:
        if index == selected:
            fill_row(screen, row, width, "status")
            safe_addstr(screen, row, 2, matches[index], attr("status"))
        else:
            safe_addstr(screen, row, 2, matches[index], attr("message"))
        index = index + 1
        row = row - 1


def draw_message_bar(screen, state, height, width):
    row = height - 2
    prompt = state["prompt"]
    if prompt is not None:
        fill_row(screen, row, width, "strip")
        question = prompt["question"]
        safe_addstr(screen, row, 0, PROMPT_PREFIX, attr("accent"))
        safe_addstr(screen, row, len(PROMPT_PREFIX), question, attr("message"))
        input_column = len(PROMPT_PREFIX) + len(question)
        safe_addstr(screen, row, input_column, prompt["input"], attr("prompt"))
        return
    if state["message"] != "":
        safe_addstr(screen, row, 1, state["message"], attr(message_color(state["message"])))


def search_progress(state):
    prompt = state["prompt"]
    if prompt is None:
        return ""
    kind = prompt["kind"]
    term = None
    if kind == "search" or kind == "replace":
        term = prompt["input"]
    if kind == "replace_with":
        term = prompt["find"]
    if term is None or term == "":
        return ""
    count = len(state["matches"])
    if count == 0:
        return "no matches"
    index = index_at_cursor(state)
    if index == -1:
        if count == 1:
            return "1 match"
        return str(count) + " matches"
    return str(index + 1) + " of " + str(count)


def status_dot(state):
    if state["modified"]:
        return "●"
    return ""


def missing_newline(state):
    if state["final_newline"]:
        return False
    if state["lines"][-1] == "":
        return False
    return True


def draw_status_bar(screen, state, height, width):
    row = height - 1
    fill_row(screen, row, width - 1, "status")
    name = state["path"]
    if name is None:
        name = "(untitled)"
    base = os.path.basename(name)
    column = 2
    safe_addstr(screen, row, column, base, attr("status_name"))
    dot = status_dot(state)
    if dot != "":
        dot_column = column + len(base) + 1
        safe_addstr(screen, row, dot_column, dot, attr("status_modified"))
    cursor_column = display_column(state["lines"][state["cy"]], state["cx"]) + 1
    right = str(state["cy"] + 1) + "," + str(cursor_column)
    right_column = width - len(right) - 2
    left_limit = column + len(base) + 1
    marker_column = right_column
    progress = search_progress(state)
    if progress != "":
        marker_column = right_column - len(progress) - 2
        if marker_column > left_limit:
            safe_addstr(screen, row, marker_column, progress, attr("status_dim"))
    if missing_newline(state):
        marker = "no newline"
        no_newline_column = marker_column - len(marker) - 2
        if no_newline_column > left_limit:
            safe_addstr(screen, row, no_newline_column, marker, attr("status_dim"))
    safe_addstr(screen, row, right_column, right, attr("status_dim"))


def place_cursor(screen, state, height, width):
    prompt = state["prompt"]
    if prompt is not None:
        row = height - 2
        column = len(PROMPT_PREFIX) + len(prompt["question"]) + len(prompt["input"])
    else:
        row = state["cy"] - state["top"]
        line = state["lines"][state["cy"]]
        column = gutter_width(state) + display_column(line, state["cx"]) - state["left"]
    if row < 0:
        row = 0
    if row >= height:
        row = height - 1
    if column < 0:
        column = 0
    if column >= width:
        column = width - 1
    try:
        screen.move(row, column)
    except curses.error:
        pass
