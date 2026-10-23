import os

from pygments import lexers
from pygments.util import ClassNotFound

LEXER_CACHE = {}

EXTENSION_ALIASES = {
    ".py": "python",
    ".pyw": "python",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".java": "java",
    ".cs": "csharp",
    ".php": "php",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
    ".markdown": "markdown",
    ".rst": "rst",
    ".tex": "tex",
    ".sql": "sql",
    ".lua": "lua",
    ".swift": "swift",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".hs": "haskell",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hrl": "erlang",
    ".clj": "clojure",
    ".cljs": "clojure",
    ".vue": "vue",
    ".txt": "text",
    ".log": "text",
}

CPP_BUILTINS = {
    "std",
    "cout",
    "cin",
    "cerr",
    "clog",
    "endl",
    "string",
    "vector",
    "map",
    "set",
    "pair",
    "make_pair",
    "size_t",
    "nullptr",
}


def looks_like_perl(text):
    if text is None:
        return False
    lower = text.lower()
    if "use strict" in lower:
        return True
    if "use warnings" in lower:
        return True
    if "my $" in lower:
        return True
    if "perl" in lower:
        return True
    return False


def looks_like_prolog(text):
    if text is None:
        return False
    if ":-" in text:
        return True
    if "?-" in text:
        return True
    return False


def looks_like_cpp(text):
    if text is None:
        return False
    lower = text.lower()
    if "std::" in text:
        return True
    if "#include <iostream>" in lower:
        return True
    if "namespace " in lower:
        return True
    if "template<" in lower:
        return True
    if "template <" in lower:
        return True
    if "class " in lower:
        return True
    return False


def looks_like_matlab(text):
    if text is None:
        return False
    lower = text.lower()
    if "#import" in lower:
        return False
    if "@interface" in lower:
        return False
    if "@implementation" in lower:
        return False
    if "function " in lower and "end" in lower:
        return True
    if "disp(" in lower:
        return True
    if "clear all" in lower:
        return True
    if "clc" in lower:
        return True
    return False


def looks_like_objc(text):
    if text is None:
        return False
    if "#import" in text:
        return True
    if "@interface" in text:
        return True
    if "@implementation" in text:
        return True
    if "NSString" in text:
        return True
    if "NSLog" in text:
        return True
    return False


def lexer_mode(path, text):
    lower = path.lower()
    if lower.endswith(".pm"):
        return "perl"
    if lower.endswith(".t"):
        if text is None or looks_like_perl(text) or "test" in text.lower():
            return "perl"
        return ""
    if lower.endswith(".pl"):
        if text is None or not looks_like_prolog(text):
            return "perl"
        return "prolog"
    if lower.endswith(".h") and looks_like_cpp(text):
        return "cpp"
    if lower.endswith(".m"):
        if looks_like_matlab(text):
            return "matlab"
        if looks_like_objc(text):
            return "objc"
    return ""


def lexer_by_name(name):
    try:
        return lexers.get_lexer_by_name(name, stripnl=False, ensurenl=False)
    except ClassNotFound:
        return None


def build_lexer(path, text, mode):
    lower = path.lower()
    if mode == "perl":
        return lexer_by_name("perl")
    if mode == "prolog":
        return lexer_by_name("prolog")
    if mode == "cpp":
        return lexer_by_name("cpp")
    if mode == "matlab":
        return lexer_by_name("matlab")
    if mode == "objc":
        return lexer_by_name("objective-c")
    if lower.endswith(".m") and text is not None:
        try:
            return lexers.guess_lexer_for_filename(path, text, stripnl=False, ensurenl=False)
        except ClassNotFound:
            pass
    extension = os.path.splitext(lower)[1]
    alias = EXTENSION_ALIASES.get(extension)
    if alias is not None:
        lexer = lexer_by_name(alias)
        if lexer is not None:
            return lexer
    try:
        return lexers.get_lexer_for_filename(path, stripnl=False, ensurenl=False)
    except ClassNotFound:
        return None


def pick_lexer(path, text=None):
    if path is None:
        return None
    base = os.path.basename(path).lower()
    mode = lexer_mode(path, text)
    key = (base, mode)
    if key in LEXER_CACHE:
        return LEXER_CACHE[key]
    lexer = build_lexer(path, text, mode)
    if len(LEXER_CACHE) > 256:
        LEXER_CACHE.clear()
    LEXER_CACHE[key] = lexer
    return lexer


def language_name(path, text=None):
    lexer = pick_lexer(path, text)
    if lexer is None:
        return "text"
    return lexer.name


def color_for_token(token_type):
    name = str(token_type)
    if name.startswith("Token.Comment.PreprocFile"):
        return "string"
    if name.startswith("Token.Comment"):
        return "comment"
    if name.startswith("Token.Literal.String.Doc"):
        return "docstring"
    if name.startswith("Token.Literal.String"):
        return "string"
    if name.startswith("Token.Literal.Scalar"):
        return "string"
    if name.startswith("Token.Literal.Number"):
        return "number"
    if name.startswith("Token.Keyword"):
        return "keyword"
    if name.startswith("Token.Name.Decorator"):
        return "decorator"
    if name.startswith("Token.Name.Builtin"):
        return "builtin"
    if name.startswith("Token.Name.Function"):
        return "function"
    if name.startswith("Token.Name.Class"):
        return "classname"
    if name.startswith("Token.Name.Exception"):
        return "classname"
    if name.startswith("Token.Name.Namespace"):
        return "classname"
    if name.startswith("Token.Name.Constant"):
        return "classname"
    if name.startswith("Token.Name.Tag"):
        return "keyword"
    if name.startswith("Token.Name.Entity"):
        return "string"
    if name.startswith("Token.Name"):
        return "text"
    if name.startswith("Token.Operator"):
        return "operator"
    if name.startswith("Token.Generic.Error"):
        return "error"
    if name.startswith("Token.Generic.Traceback"):
        return "error"
    if name.startswith("Token.Generic.Deleted"):
        return "error"
    if name.startswith("Token.Generic.Heading"):
        return "keyword"
    if name.startswith("Token.Generic.Subheading"):
        return "keyword"
    if name.startswith("Token.Generic.Inserted"):
        return "string"
    if name.startswith("Token.Generic"):
        return "text"
    if name.startswith("Token.Error"):
        return "error"
    return "text"


def is_name_token(token_type):
    name = str(token_type)
    if name == "Token.Name":
        return True
    if name == "Token.Name.Other":
        return True
    if name == "Token.Name.Attribute":
        return True
    return False


def next_is_call(lines, line_index, column, length):
    if line_index < 0 or line_index >= len(lines):
        return False
    line = lines[line_index]
    end = column + length
    if end > len(line):
        return False
    rest = line[end:]
    return rest.lstrip().startswith("(")


def compute_spans(lines, lexer):
    spans = []
    for line in lines:
        spans.append([])
    text = "\n".join(lines)
    language = lexer.name
    line_index = 0
    column = 0
    for token_type, value in lexer.get_tokens(text):
        color = color_for_token(token_type)
        pieces = value.split("\n")
        part_index = 0
        for piece in pieces:
            piece_color = color
            if language == "C++" and piece in CPP_BUILTINS and color == "text":
                piece_color = "builtin"
            if piece_color == "text" and is_name_token(token_type):
                if next_is_call(lines, line_index, column, len(piece)):
                    piece_color = "function"
            if piece != "" and line_index < len(spans):
                spans[line_index].append((column, len(piece), piece_color))
            column = column + len(piece)
            if part_index < len(pieces) - 1:
                line_index = line_index + 1
                spans.append([])
                column = 0
            part_index = part_index + 1
    return spans


def cached_spans(state):
    if state["spans_version"] == state["version"]:
        return state["spans"]
    return []


def spans_cover(state, view_rows):
    if state["spans_version"] != state["version"]:
        return False
    if state["top"] < state["spans_top"]:
        return False
    last_visible = state["top"] + view_rows
    if last_visible > len(state["lines"]):
        last_visible = len(state["lines"])
    if last_visible > state["spans_bottom"]:
        return False
    return True


def get_spans(state, first_line=0, last_line=None):
    if last_line is None:
        last_line = len(state["lines"])
    if first_line < 0:
        first_line = 0
    if last_line > len(state["lines"]):
        last_line = len(state["lines"])
    if first_line > last_line:
        first_line = last_line
    if state["spans_version"] == state["version"]:
        if state["spans_top"] <= first_line and state["spans_bottom"] >= last_line:
            return state["spans"]
    window = state["lines"][first_line:last_line]
    text = "\n".join(window)
    lexer = pick_lexer(state["path"], text)
    spans = []
    for line in state["lines"]:
        spans.append([])
    if lexer is None:
        state["spans"] = spans
        state["spans_version"] = state["version"]
        state["spans_top"] = first_line
        state["spans_bottom"] = last_line
        return state["spans"]
    window_spans = compute_spans(window, lexer)
    index = 0
    while index < len(window_spans):
        if first_line + index < len(spans):
            spans[first_line + index] = window_spans[index]
        index = index + 1
    state["spans"] = spans
    state["spans_version"] = state["version"]
    state["spans_top"] = first_line
    state["spans_bottom"] = last_line
    return state["spans"]
