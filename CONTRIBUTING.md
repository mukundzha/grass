# Contributing to Grass

Thanks for taking a look. Grass stays small on purpose — contributions should keep it that way
(readable, zero-config, one file at a time). Please open an issue before a big change so we can
agree on direction.

## Quick start

```bash
git clone https://github.com/mukundzha/grass.git
cd grass
pip install -e .
python tests/run_tests.py
```

Tests are plain functions named `test_*` in `tests/` and run via `tests/run_tests.py` (no pytest
needed). Each module has a matching `tests/test_<module>.py`. They manipulate the editor
`state` dict directly, so no terminal is required.

## Good first issues

Look for the [`good first issue`](https://github.com/mukundzha/grass/labels/good%20first%20issue)
label. These are intentionally small: a single function, a single test, no architecture decisions.

When fixing one:

1. Fork → branch → make the change.
2. Add or update a test in the matching `tests/test_*.py`.
3. Run `python tests/run_tests.py` and confirm `0 failed`.
4. Open a PR referencing the issue, e.g. `Fixes #12`.

## Style

- ~2,300 lines total by design. Prefer smaller, clearer code over clever code.
- 4-space indent, `snake_case`, no type hints (matching the rest of the codebase).
- Keep changes focused; split unrelated fixes into separate PRs.

## What Grass is *not* looking for

No plugins, no LSP, no config files, no settings, no mouse. If it makes Grass bigger or more
complex, it probably doesn't belong.