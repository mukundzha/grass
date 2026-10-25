<h1 align="center">🌱 Grass</h1>

<p align="center">
  <b>The terminal editor you already know how to use.</b><br>
  Syntax highlighting, fuzzy finder, find-as-you-type. No modes, no config, no learning curve.
</p>

<p align="center">
  <a href="https://pypi.org/project/grass-editor/"><img alt="PyPI" src="https://img.shields.io/pypi/v/grass-editor.svg"></a>
  <img alt="Python" src="https://img.shields.io/pypi/pyversions/grass-editor.svg">
  <a href="https://github.com/mukundzha/grass/actions/workflows/tests.yml"><img alt="tests" src="https://github.com/mukundzha/grass/actions/workflows/tests.yml/badge.svg"></a>
  <a href="https://github.com/mukundzha/grass/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/github/license/mukundzha/grass.svg"></a>
</p>

<p align="center">
  <b>If Grass saved you a keystroke, a ⭐ helps others find it.</b>
</p>

<p align="center">
  <img alt="Grass demo" src="https://raw.githubusercontent.com/mukundzha/grass/main/docs/demo.gif" width="760">
</p>

### Install

```bash
pipx install grass-editor
```

<sub>No pipx? `pip install grass-editor` works too. Python 3.9+. <a href="#windows">Windows notes</a>.</sub>

---

## Sound familiar?

- You SSH into a box and `nano` feels bare, but `vim` feels like a test.
- You don't want to spend a weekend on dotfiles just to edit a file.
- You want highlighting and a fast file jump, not a whole IDE in your terminal.

**Grass is for that moment.** Open a file and type. Everything else is one `Ctrl` key away.

## What you get

| | |
|---|---|
| **Just type** | One mode, like nano. Nothing to memorize before your first edit. |
| **Looks good by default** | Syntax highlighting with Meadow, a calm warm theme. No theme hunting. Assumes a dark 256-color terminal; basic colors fall back gracefully. |
| **`Ctrl-P` fuzzy finder** | Jump to any file by typing a few letters. |
| **`Ctrl-F` live search** | Results update as you type. |
| **Safe with your files** | Atomic saves. Tabs preserved. A missing trailing newline stays missing, and the status bar tells you. |
| **Language coverage** | C, C++, Rust, Go, JavaScript, TypeScript, Python, Ruby, Java, shell, HTML, CSS, JSON, YAML, Markdown, and more via Pygments. |
| **CJK ready** | Chinese, Japanese, and Korean text renders, edits, and scrolls at the correct width. |
| **Zero config** | No config file exists. Nothing can break. |
| **Readable source** | About 2,300 lines of Python. Read it in an afternoon, change it in an evening. |

## Why not just use...?

| | Setup needed | Learn first? | Fuzzy finder | Source you can read in a day |
|---|---|---|---|---|
| **Grass** | none | no | built in | yes (~2,300 lines) |
| nano | none | no | no | no |
| micro | none | little | no | no |
| vim / Helix | some to a lot | yes (modal) | plugin / built in | no |

Grass is **not** trying to replace Vim or micro. It has no plugins, no LSP, and no mouse, on purpose. If you want those, use them. If you want an editor that gets out of the way, you're in the right place.

## The whole keyboard

| Key | Action |
|---|---|
| `Ctrl-S` | save (asks for a name if new) |
| `Ctrl-Q` / `Ctrl-C` | quit |
| `Ctrl-P` | fuzzy file finder |
| `Ctrl-F` / `F3` | find as you type / find next |
| `Ctrl-H` | replace all (word, then replacement) |
| `Ctrl-O` | open by path |
| `Ctrl-Z` / `Ctrl-R` | undo / redo |
| `Ctrl-K` / `Ctrl-U` | cut line / paste line |

Arrows, Home, End, PageUp, PageDown, Enter (auto-indent), Tab, Backspace and Delete do what you expect.

In prompts, `Enter` confirms, `Esc` cancels, `Up`/`Down` select, and `Y`/`N` answer save/discard. The replace flow is: `Ctrl-H`, type the word, `Enter`, type the replacement, `Enter`.

## FAQ

<details>
<summary><b>Does it support plugins, LSP, or multiple files?</b></summary>

No, and that's the point. One file at a time, no plugins, no LSP, no mouse. Grass stays small so it stays calm.
</details>

<details>
<summary><b>Will it handle my big files?</b></summary>

Normal files are fast. Highlighting only covers the visible area and updates after a short pause, so very large files stay usable, but can still feel slower than small ones.
</details>

<details>
<summary><b>Does it handle Chinese, Japanese, or Korean text?</b></summary>

Yes. Wide characters render, edit, and scroll at the correct terminal width.
</details>

<details>
<summary><b>What about very long lines?</b></summary>

Lines don't wrap yet. Scroll horizontally instead.
</details>

<details>
<summary id="windows"><b>How do I install on Windows?</b></summary>

```bash
py -m pip install windows-curses grass-editor
```

Then run `grass hello.py` from the same Python environment. Using `pipx`? Run `pipx inject grass-editor windows-curses` after installing.
</details>

## Hack on it

Grass is small enough to understand completely.

- `grass/editor.py`: text buffer, undo/redo, prompts, atomic saves
- `grass/highlight.py`: Pygments lexing and Meadow colors
- `grass/screen.py`: curses rendering, splash, finder, status bar
- `grass/search.py`: find matching and match tracking
- `grass/tabs.py`: tab widths and display columns

```bash
git clone https://github.com/mukundzha/grass.git
cd grass
pip install -e .
python tests/run_tests.py
```

CI runs on Python 3.9 through 3.13. New here? Look for [`good first issue`](https://github.com/mukundzha/grass/labels/good%20first%20issue).

## Roadmap

- [ ] Line wrapping for long lines
- [ ] Faster highlighting for very large files
- [ ] Light theme

Ideas and bug reports are welcome: [open an issue](https://github.com/mukundzha/grass/issues).

## License

MIT. See [LICENSE](https://github.com/mukundzha/grass/blob/main/LICENSE).

---

<p align="center">
  <b>Grass saved you a few keystrokes?</b> Give it a ⭐ so other people can find it.
</p>
