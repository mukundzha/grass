from pygments.token import Token

from grass import highlight


def color_at(spans, line_index, column):
    for span in spans[line_index]:
        if span[0] <= column and column < span[0] + span[1]:
            return span[2]
    return None


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


def test_language_name_for_perl_script():
    text = "#!/usr/bin/perl\nuse strict;\nmy $x = 1;\n"
    assert highlight.language_name("example.pl", text) == "Perl"


def test_language_name_for_perl_module():
    text = "package Foo;\nuse strict;\n1;\n"
    assert highlight.language_name("example.pm", text) == "Perl"


def test_language_name_for_perl_test():
    text = "use Test::More;\nok(1);\n"
    assert highlight.language_name("example.t", text) == "Perl"


def test_language_name_for_new_perl_file():
    assert highlight.language_name("example.pl") == "Perl"


def test_language_name_for_prolog():
    text = ":- module(foo, [bar/1]).\nbar(X) :- X = 1.\n"
    assert highlight.language_name("example.pl", text) == "Prolog"


def test_language_name_for_many_files():
    assert highlight.language_name("example.c") == "C"
    assert highlight.language_name("example.cpp") == "C++"
    assert highlight.language_name("example.js") == "JavaScript"
    assert highlight.language_name("example.ts") == "TypeScript"
    assert highlight.language_name("example.go") == "Go"
    assert highlight.language_name("example.rs") == "Rust"
    assert highlight.language_name("example.sh") == "Bash"
    assert highlight.language_name("example.rb") == "Ruby"
    assert highlight.language_name("example.java") == "Java"
    assert highlight.language_name("example.html") == "HTML"
    assert highlight.language_name("example.md") == "Markdown"


def test_language_name_for_cpp_header():
    text = "#include <iostream>\nclass Foo {};\n"
    assert highlight.language_name("example.h", text) == "C++"


def test_c_function_call_color():
    lexer = highlight.pick_lexer("example.c")
    lines = ["int main(void) {", '    printf("hi");', "}"]
    spans = highlight.compute_spans(lines, lexer)
    assert color_at(spans, 1, 4) == "function"


def test_cpp_builtin_color():
    lexer = highlight.pick_lexer("example.cpp")
    lines = ["int main() {", '    std::cout << "hi";', "}"]
    spans = highlight.compute_spans(lines, lexer)
    assert color_at(spans, 1, 4) == "builtin"
    assert color_at(spans, 1, 9) == "builtin"


def test_javascript_function_call_color():
    lexer = highlight.pick_lexer("example.js")
    lines = ["const x = f(1);"]
    spans = highlight.compute_spans(lines, lexer)
    assert color_at(spans, 0, 10) == "function"


def test_go_function_call_color():
    lexer = highlight.pick_lexer("example.go")
    lines = ["    fmt.Println(f(1))"]
    spans = highlight.compute_spans(lines, lexer)
    assert color_at(spans, 0, 8) == "function"
    assert color_at(spans, 0, 16) == "function"


def test_perl_tokens_are_colored():
    lexer = highlight.pick_lexer("example.pl")
    lines = ["use strict;", "my $x = 1;"]
    spans = highlight.compute_spans(lines, lexer)
    assert color_at(spans, 0, 0) == "keyword"
    assert color_at(spans, 1, 3) == "text"


def test_html_tag_color():
    assert highlight.color_for_token(Token.Name.Tag) == "keyword"


def test_yaml_scalar_color():
    assert highlight.color_for_token(Token.Literal.Scalar.Plain) == "string"


def test_markdown_heading_color():
    assert highlight.color_for_token(Token.Generic.Heading) == "keyword"


def test_markdown_strong_is_not_error():
    assert highlight.color_for_token(Token.Generic.Strong) == "text"


def test_preproc_file_color():
    assert highlight.color_for_token(Token.Comment.PreprocFile) == "string"


def test_exception_color():
    assert highlight.color_for_token(Token.Name.Exception) == "classname"


def test_namespace_color():
    assert highlight.color_for_token(Token.Name.Namespace) == "classname"


def test_pick_lexer_is_cached():
    first = highlight.pick_lexer("example.py")
    second = highlight.pick_lexer("example.py")
    assert first is second


def test_cached_spans_hides_stale_highlighting():
    state = {"spans": [[(0, 1, "keyword")]], "spans_version": 1, "version": 2}
    assert highlight.cached_spans(state) == []


def test_cached_spans_returns_current_highlighting():
    spans = [[(0, 1, "keyword")]]
    state = {"spans": spans, "spans_version": 2, "version": 2}
    assert highlight.cached_spans(state) == spans


def test_get_spans_only_fills_requested_window():
    state = {
        "lines": ["x = 1", "if x:", "y = 2", "z = 3"],
        "path": "example.py",
        "version": 1,
        "spans": [],
        "spans_version": -1,
        "spans_top": -1,
        "spans_bottom": 0,
        "top": 0,
    }
    spans = highlight.get_spans(state, 1, 3)
    assert len(spans) == 4
    assert state["spans_top"] == 1
    assert state["spans_bottom"] == 3
    assert spans[0] == []
    assert len(spans[1]) > 0


def test_spans_cover_handles_short_files():
    state = {
        "lines": [""],
        "version": 1,
        "spans_version": 1,
        "top": 0,
        "spans_top": 0,
        "spans_bottom": 1,
    }
    assert highlight.spans_cover(state, 38) is True


def test_spans_cover_rejects_scrolled_view():
    state = {
        "lines": ["a", "b", "c", "d"],
        "version": 1,
        "spans_version": 1,
        "top": 2,
        "spans_top": 0,
        "spans_bottom": 2,
    }
    assert highlight.spans_cover(state, 2) is False
