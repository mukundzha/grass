# Grass

A calm, zero-config terminal code editor.

No modes. No config files. Just type.

[![tests](https://github.com/mukundzha/grass/actions/workflows/tests.yml/badge.svg)](https://github.com/mukundzha/grass/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/grass-editor.svg)](https://pypi.org/project/grass-editor/)

![Grass demo](https://raw.githubusercontent.com/mukundzha/grass/17b0c4e/docs/demo.gif)

## Why

Nano starts instantly but stays plain. Vim and Helix are powerful, but they ask
you to learn an editing language first. Grass sits between them: one mode, one
theme, syntax highlighting, and about 1,700 lines of Python you can read in an
afternoon.

It is not a Vim replacement. No plugins, no LSP, no mouse. One file at a time,
on purpose.

## Install

```bash
pipx install grass-editor
```

No pipx? `pip install grass-editor` also works. On Windows, install curses
support first:

```bash
pip install windows-curses
pip install grass-editor
```

Python 3.9 or newer.

## Run

```bash
grass hello.py
```

With no file, `grass` opens the splash. `grass --version` prints the version.

## A look

| Splash | Ctrl-P finder |
| --- | --- |
| ![Grass splash](https://raw.githubusercontent.com/mukundzha/grass/main/docs/splash.png) | ![Grass finder](https://raw.githubusercontent.com/mukundzha/grass/main/docs/finder.png) |

One theme, Meadow: warm off-white text, green keywords, gold functions, a dark
status bar. It assumes a dark 256-color terminal; basic colors fall back.

## Keys

| Key | Action |
| --- | --- |
| type | edit |
| arrows, Home, End, PageUp, PageDown | move |
| Enter | new line, with auto-indent |
| Tab | indent to the next tab stop |
| Backspace, Delete | delete |
| Ctrl-F | find as you type |
| F3 | find next |
| Ctrl-H | replace all (word, then replacement) |
| Ctrl-P | fuzzy file finder |
| Ctrl-O | open by path |
| Ctrl-K | cut line |
| Ctrl-U | paste line |
| Ctrl-S | save (asks for a name if new) |
| Ctrl-Z | undo |
| Ctrl-R | redo |
| Ctrl-Q, Ctrl-C | quit |

| Prompt key | Action |
| --- | --- |
| Enter | confirm or move to the next step |
| Esc | cancel, close, or clear search |
| Up, Down | select a file finder result |
| Y, N | save or discard at the quit prompt |

The replace flow is: `Ctrl-H`, type the word, `Enter`, type the replacement,
`Enter`. Every match is replaced.

## Notes

- Always in typing mode, like nano.
- Saves are atomic: a crash cannot leave the original file truncated.
- Tabs are preserved and shown at 4-column stops.
- A file without a trailing newline stays that way. The status bar says `no newline`.
- Highlighting is limited to the visible area and updates after a short pause, so typing stays fast in large files.
- Highlighting covers C, C++, Perl, JavaScript, TypeScript, Go, Rust, Ruby,
  Java, shell, HTML, CSS, JSON, YAML, Markdown, and other Pygments languages.
- Wide characters (CJK) and long wrapped lines are not fully supported yet.

## Development

```bash
git clone https://github.com/mukundzha/grass.git
cd grass
pip install -e .
python tests/run_tests.py
```

Tests are plain functions with a small custom runner. CI runs on Python 3.9
through 3.13.

## License

MIT. See [LICENSE](https://github.com/mukundzha/grass/blob/main/LICENSE).

Issues and PRs are welcome.
