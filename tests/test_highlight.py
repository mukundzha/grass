from pygments.token import Token

from grass import highlight


def test_keyword_color():
    assert highlight.color_for_token(Token.Keyword) == "keyword"
    assert highlight.color_for_token(Token.Keyword.Type) == "keyword"


def test_string_color():
    assert highlight.color_for_token(Token.Literal.String.Double) == "string"


def test_docstring_color():
    assert highlight.color_for_token(Token.Literal.String.Doc) == "docstring"


def test_docstring_in_source():
    lexer = highlight.pick_lexer("example.py")
    lines = ['"""Module docs."""', "x = 1"]
    spans = highlight.compute_spans(lines, lexer)
    found_docstring = False
    for span in spans[0]:
        if span[2] == "docstring":
            found_docstring = True
    assert found_docstring is True


def test_comment_color():
    assert highlight.color_for_token(Token.Comment.Single) == "comment"


def test_number_color():
    assert highlight.color_for_token(Token.Literal.Number.Integer) == "number"


def test_function_color():
    assert highlight.color_for_token(Token.Name.Function) == "function"


def test_unknown_color_is_text():
    assert highlight.color_for_token(Token.Text) == "text"


def test_pick_lexer_none_for_no_path():
    assert highlight.pick_lexer(None) is None


def test_language_name_for_python():
    assert highlight.language_name("example.py") == "Python"


def test_language_name_for_unknown():
    assert highlight.language_name("example.zzz") == "text"


def test_compute_spans_finds_keyword():
    lexer = highlight.pick_lexer("example.py")
    lines = ["x = 1", "if x:"]
    spans = highlight.compute_spans(lines, lexer)
    assert len(spans) >= 2
    found_keyword = False
    for span in spans[1]:
        if span[2] == "keyword":
            found_keyword = True
    assert found_keyword is True


def test_blank_first_line_keeps_alignment():
    lexer = highlight.pick_lexer("example.py")
    lines = ["", "if x:"]
    spans = highlight.compute_spans(lines, lexer)
    assert len(spans) >= 2
    found_keyword = False
    for span in spans[1]:
        if span[2] == "keyword":
            found_keyword = True
    assert found_keyword is True


def test_multiline_string_stays_on_own_lines():
    lexer = highlight.pick_lexer("example.py")
    lines = ['text = """', "hello", '"""']
    spans = highlight.compute_spans(lines, lexer)
    assert len(spans) >= 3
    assert len(spans[1]) > 0
    for span in spans[1]:
        assert span[2] == "string"


def test_span_lengths_fit_lines():
    lexer = highlight.pick_lexer("example.py")
    lines = ["x = 1", "if x:"]
    spans = highlight.compute_spans(lines, lexer)
    index = 0
    while index < len(lines):
        for span in spans[index]:
            assert span[0] + span[1] <= len(lines[index])
        index = index + 1
