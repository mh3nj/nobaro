# Changelog

All notable changes to NOBARO are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-18

### Added
- **ASCII art toolbar button** (`[ART]`) — opens the gallery with one click (F8)
- **Edit ASCII art** — edit your own pieces in a live multi-line editor inside the gallery
- **Search ASCII art** — a live search box in the gallery filters pieces by name as you type
- **Inject** — the gallery's primary action injects the selected art into the active note
  editor on its own new line (double-click also injects)
- **Always-visible navbar** — the gallery's action buttons stay on screen at any window size
- **Branded About dialog** — app logo plus full credits
  (developed by mh3nj/mh3n.com, logo by parsegan.com, sponsored by dahgan.com)
- **App icon from `public/logo.png`** — window icon + in-app logo + exe icon
- GitHub issue templates (bug report, feature request), PR template, `requirements.txt`,
  professional README and CONTRIBUTING guide
- Full rebrand and redesign of the original LifeNote concept (PureBasic → pure Python)

### Fixed
- **About window was a giant empty box** — Tk renders the 6000px source logo blank, so the
  About dialog blew up to 6000×6001px with nothing visible; it now shows a pre-sized logo
  copy (`public/logo_256.png`) in a clean, centered window
- **ASCII gallery buttons rendered off-screen** — actions now live in an always-visible
  navbar; the preview no longer balloons the window to fit the widest art (h-scroll instead)
- **v2 import button in Settings now works** (was previously a dead button)
- **Autosave timer leak** — re-applying settings no longer stacks multiple autosave loops
- **Windowed exe** — PyInstaller build is now `console=False` with the NOBARO icon bundled
- **Portable frozen builds** — data folder is created next to the executable
- Cleaned unused imports, dead code, and invalid escape-sequence warnings

### Desktop features (from the v1 rewrite)
- Unlimited notes per day — write as many entries as you want, any day
- Rich text editor (bold, italic, headings, colors, alignment, RTL), mood tracking,
  XP/levels/achievements, streaks, sealed & unsent letters, templates, media attachments,
  search, stats & annual review, encrypted exports, backups, screensaver, 5 themes,
  English + Farsi UI, v2 import

---

## LifeNote V4 — PureBasic _(archived)_
**Released: ~2024**

The version that inspired the Nobaro rewrite. Feature-complete and stable. This was the peak of the PureBasic line.

- Tabbed note editor
- Rich text formatting (fonts, colors, sizes)
- Mood/tag system with visual indicators
- XP and leveling system
- Achievement tracking
- ASCII art gallery with viewer
- Screensaver mode
- Multiple color themes
- Templates
- Media attachments
- Export to TXT/RTF
- Rainbow text and glow effects
- Backup manager

---

## LifeNote V3 — PureBasic _(archived)_
**Released: ~2023**

Started to feel like a real app. Added the gamification layer that became a signature feature.

- First XP and level system
- Basic achievements
- Mood tracking (simple)
- Tag system for notes
- Search and filter
- Better text editor with formatting
- Theme switching (first 4 themes)

---

## LifeNote V2 — PureBasic _(archived)_
**Released: ~2022**

The first proper PureBasic version. Moved from a proof-of-concept to an actual application.

- Full windowed GUI (PureBasic native controls)
- Note creation, editing, saving as plain text files
- Simple list view for notes
- Basic search
- Import/export to plain text
- No gamification yet — pure note-taking

---

## LifeNote V1 — PureBasic _(archived)_
**Released: ~2021**

The original concept. A tiny, experimental notepad built to see if the idea had legs.

- Console-based or minimal GUI
- Create and save text notes
- One note at a time
- No organization, no search, no frills
- Proved the concept was worth pursuing
