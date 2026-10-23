from pygments import lexers
from pygments.util import ClassNotFound

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


def perl_lexer():
    try:
        return lexers.get_lexer_by_name("perl", stripnl=False, ensurenl=False)
    except ClassNotFound:
        return None


def pick_lexer(path, text=None):
    if path is None:
        return None
    lower = path.lower()
    if lower.endswith(".pm"):
        lexer = perl_lexer()
        if lexer is not None:
            return lexer
    if lower.endswith(".t"):
        if text is None or looks_like_perl(text) or "test" in text.lower():
            lexer = perl_lexer()
            if lexer is not None:
                return lexer
    if lower.endswith(".pl"):
        if text is None or not looks_like_prolog(text):
            lexer = perl_lexer()
            if lexer is not None:
                return lexer
    if lower.endswith(".h"):
        if looks_like_cpp(text):
            try:
                return lexers.get_lexer_by_name("cpp", stripnl=False, ensurenl=False)
            except ClassNotFound:
                pass
    if text is not None:
        try:
            return lexers.guess_lexer_for_filename(path, text, stripnl=False, ensurenl=False)
        except ClassNotFound:
            pass
    try:
        return lexers.get_lexer_for_filename(path, stripnl=False, ensurenl=False)
    except ClassNotFound:
        return None


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


def get_spans(state):
    if state["spans_version"] == state["version"]:
        return state["spans"]
    text = "\n".join(state["lines"])
    lexer = pick_lexer(state["path"], text)
    if lexer is None:
        state["spans"] = []
        state["spans_version"] = state["version"]
        return state["spans"]
    state["spans"] = compute_spans(state["lines"], lexer)
    state["spans_version"] = state["version"]
    return state["spans"]
