# Grass

A minimal, beautiful, zero-config terminal code editor.

No modes. No config files. Just type.

![Grass demo](https://raw.githubusercontent.com/mukundzha/grass/main/docs/demo.gif)

## Install

```bash
pip install grass-editor
```

On Windows, install curses support first:

```bash
pip install windows-curses
```

## Run

```bash
grass hello.py
```

Or without installing:

```bash
python -m grass hello.py
```

Check the identity:

```bash
grass --version
```

## Theme

Grass ships with one hand-tuned theme: **Meadow**.

A calm, forest-inspired dark palette — warm parchment text, sage-green
keywords, golden function names, aqua class names, and a layered
forest-dark status bar. Comments and docstrings sit quietly in muted
green-gray so code reads like a clearing at dusk.

- A two-tone wordmark splash greets you on launch — meadow green above,
  sage shadow below — over the line `❧ a calm terminal editor`, signed
  `v0.1.1 · Meadow`, and fades the moment you type.
- The status bar keeps the file name on the left and live line,column
  position on the right.
- An amber dot beside the file name marks unsaved changes, then
  disappears the moment you save.
- Your terminal tab lives and breathes with you: `grass · file.py`,
  gaining a ` •` while there are unsaved changes.
- Feedback speaks in color: saves flash leaf green, problems turn
  warm red.
- A floating scrollbar on the right edge tracks your place in the file.
- The cursor line glows softly; the gutter stays a shade darker.
- Search matches glow olive-green, and the match you are on turns warm gold.
- Prompts sit behind a green `❯` marker.

Meadow assumes a dark terminal with 256 colors. Terminals with only
basic colors fall back gracefully.

## Keys

| Key | Action |
| --- | --- |
| type | edit |
| arrows, Home, End, PageUp, PageDown | move |
| Enter | new line, with auto-indent |
| Tab | indent to the next tab stop |
| Backspace, Delete | delete |
| Ctrl-F | find (jumps to matches as you type) |
| Ctrl-P | open a file by fuzzy search |
| Ctrl-K | cut line |
| Ctrl-U | paste line |
| Ctrl-S | save |
| Ctrl-Z | undo |
| Ctrl-R | redo |
| Ctrl-Q | quit |

## Notes

- Grass is always in typing mode, like nano.
- A file without a trailing newline stays that way, and the status bar says `no newline`.
- The theme is designed for dark terminal backgrounds.
- Tabs are preserved and shown at 4-column tab stops.
- Large files re-highlight fully on every edit; normal files stay fast.
- Wide characters (CJK) and long wrapped lines are not fully supported yet.
