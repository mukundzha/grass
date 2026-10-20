from pygments import lexers
from pygments.util import ClassNotFound


def pick_lexer(path):
    if path is None:
        return None
    try:
        return lexers.get_lexer_for_filename(path, stripnl=False, ensurenl=False)
    except ClassNotFound:
        return None


def language_name(path):
    lexer = pick_lexer(path)
    if lexer is None:
        return "text"
    return lexer.name


def color_for_token(token_type):
    name = str(token_type)
    if name.startswith("Token.Comment"):
        return "comment"
    if name.startswith("Token.Literal.String.Doc"):
        return "docstring"
    if name.startswith("Token.Literal.String"):
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
    if name.startswith("Token.Name"):
        return "text"
    if name.startswith("Token.Operator"):
        return "operator"
    if name.startswith("Token.Error"):
        return "error"
    if name.startswith("Token.Generic"):
        return "error"
    return "text"


def compute_spans(lines, lexer):
    spans = []
    for line in lines:
        spans.append([])
    text = "\n".join(lines)
    line_index = 0
    column = 0
    for token_type, value in lexer.get_tokens(text):
        color = color_for_token(token_type)
        pieces = value.split("\n")
        part_index = 0
        for piece in pieces:
            if piece != "" and line_index < len(spans):
                spans[line_index].append((column, len(piece), color))
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
    lexer = pick_lexer(state["path"])
    if lexer is None:
        state["spans"] = []
        state["spans_version"] = state["version"]
        return state["spans"]
    state["spans"] = compute_spans(state["lines"], lexer)
    state["spans_version"] = state["version"]
    return state["spans"]
