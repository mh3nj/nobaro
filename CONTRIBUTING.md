# Contributing to NOBARO

First off — thank you for taking the time to contribute. ❤️

NOBARO is a small, passion-driven project. Whether you're fixing a typo, reporting a bug, proposing a feature, or writing code, every contribution matters.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Writing Code](#writing-code)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Guidelines](#commit-guidelines)
- [Release Process](#release-process)

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the maintainers.

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:

1. **Search existing issues** — your bug may already be reported (and possibly fixed).
2. **Check the latest release** — the bug may already be resolved on `main`.
3. **Reproduce the bug** — try to find the smallest, most reliable way to trigger it.

Then open an issue using our [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml). A great bug report includes:

- Your **OS** and **Python version** (or whether you're using the prebuilt `.exe`)
- The **steps to reproduce**
- What you **expected** to happen vs. what **actually** happened
- Any **error messages**, tracebacks, or screenshots
- Whether the problem happens on a fresh data folder or an existing one

> ⚠️ **Please do not include personal diary data in bug reports.** If a note is involved, reproduce with a dummy note.

### Suggesting Features

Open a [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml) and tell us:

- **What** you want to happen
- **Why** — the problem it solves for you
- **How** it could fit NOBARO's philosophy (offline, private, simple, QBasic-souled)

Big ideas are welcome — but please be ready to discuss design before we write code.

### Writing Code

Unsure where to start? Look for issues labelled `good first issue` or `help wanted`. If you want to work on something, **comment on the issue first** so we don't duplicate effort.

---

## Development Setup

```bash
git clone https://github.com/mh3nj/nobaro.git
cd nobaro

# Python 3.9+ required (tkinter included)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Runtime needs nothing extra — the app runs on the standard library.
# Optional extras for development / builds:
pip install pillow pyinstaller

python main.py                   # run the app
```

---

## Code Style

Match the existing code. When in doubt, follow these rules:

- **Python**: PEP 8, but pragmatic — keep lines readable, not necessarily ≤ 79 chars
- **Naming**: `snake_case` for functions/variables, `CamelCase` for classes, `SCREAMING_SNAKE` for constants
- **Comments**: explain *why*, not *what*. Skip obvious comments entirely.
- **Strings**: all user-visible strings go in `assets/lang.py` (English + Farsi). Never hardcode UI text in features.
- **Theme**: never hardcode colors or fonts in a feature — use the `theme` singleton from `ui/theme.py`.
- **GUI separation**: pure logic (dates, XP, streaks, storage) belongs in `core/` with **no** tkinter imports, so it stays testable. GUI code lives in `features/`.
- **Keep it simple.** NOBARO's soul is a blue screen and a cursor — not a dependency tree.

---

## Project Structure

```
core/        Pure-Python logic — data models, stores, utils, XP (no GUI)
ui/          Theme singleton and widget styling
features/    One window/dialog per file (ascii_art, stats, export, ...)
assets/      Language strings and sound effects
main.py      Application shell — window, toolbar, menus, key bindings
```

New features go in `features/` as a self-contained window class with a `run()` method returning a result — see `features/templates.py` for a clean example.

---

## Testing

NOBARO doesn't have a formal test suite yet — **help us build one!** Until then:

1. Run the syntax check on everything:

   ```bash
   python -m compileall main.py core ui features assets
   ```

2. Smoke-test the app:

   ```bash
   python main.py
   ```

3. Exercise the feature you touched: create data, save, reload, and confirm nothing crashes.

If you add pure logic to `core/`, consider a small `tests/` module — pure functions like the ones in `core/utils.py` and `core/player_logic.py` are perfect candidates for unit tests.

---

## Pull Request Process

1. **Fork** the repo and create your branch from `main`:
   ```bash
   git checkout -b fix/describe-the-fix
   ```
2. **Commit** your changes with a clear message (see [Commit Guidelines](#commit-guidelines)).
3. **Test** — run the compile check and a manual smoke test.
4. **Push** and open a PR against `main`, using the [Pull Request template](.github/PULL_REQUEST_TEMPLATE.md).
5. A maintainer will review. Be patient — it's a small project run by real humans.

### PR Checklist

- [ ] My code follows the project's code style
- [ ] I added a `CHANGELOG.md` entry (under "Unreleased")
- [ ] I tested the change manually (`python main.py`)
- [ ] User-visible strings are in `assets/lang.py` (both languages)
- [ ] I updated the README if the change affects usage
- [ ] My PR description references the related issue

---

## Commit Guidelines

- Write concise, descriptive commit messages: *what* changed and *why*
- One logical change per commit
- Use the present tense ("Add", "Fix", not "Added", "Fixed")
- Example: `Fix streak counter resetting after midnight`

---

## Release Process

Maintainers only:

1. Bump `APP_VERSION` in `core/constants.py` and add a `CHANGELOG.md` entry
2. Run `python tools/make_icon.py` to refresh the icon
3. Build: `pyinstaller main.spec`
4. Write a `RELEASE_NOTES.md` for the tag
5. Zip `dist/nobaro/` with the release notes and upload to GitHub Releases

---

## Thank You

NOBARO is built in the open, for the love of it. Every issue filed, every PR merged, every kind word — it all matters.

`10 PRINT "you matter"`
`20 GOTO 10`
