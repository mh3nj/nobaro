#!/usr/bin/env python3
# ================================================================
#  NOBARO v1  —  main.py
#  Entry point.  Full tkinter GUI with QBasic soul.
#  Requires Python 3.9+ with tkinter (ships with Python on Windows).
#
#  10 PRINT "you matter"
#  20 GOTO 10
# ================================================================

import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, colorchooser
import datetime
import shutil
import subprocess

# ---- Our modules
from core.constants import (
    APP_NAME, APP_VERSION, APP_TAGLINE,
    BASE_DIR, DATA_DIR, NOTES_DIR, MEDIA_DIR, ASCII_DIR, BACKUP_DIR,
    PLAYER_FILE, ACHIEVS_FILE, LETTERS_FILE,
    THEME_NAMES, MOODS, MOOD_SYMBOLS, MOOD_COLORS,
    DAILY_QUOTES, XP_ASCII_CREATE, XP_TEMPLATE_USE,
    XP_FUTURE_LETTER, FS_H1, FS_H2, FS_H3,
)
from core.utils import (
    today, yesterday, now_time, last_year_date, friendly_date,
    month_name, short_month, day_of_week_iso, days_in_month,
    add_days, days_between, calculate_streak, get_gap_dates,
    generate_note_id, count_words, daily_quote,
    load_json, save_json, load_text, save_text, ensure_dirs,
    detect_media_type, xor_cipher, xor_decipher, hash_password,
)
from core.data import (
    Note, Player, Achievement, Letter, Template,
    NoteStore, PlayerStore, AchievementStore, LetterStore, TemplateStore,
    MediaRef,
)
from core.player_logic import (
    get_level_name, get_level_index, xp_for_next_level,
    calc_note_xp, check_achievements, apply_streak_bonus,
)
from ui.theme import theme
from assets.lang import lang
from assets.sounds import (
    play_startup, play_quit, play_save, play_level_up,
    play_achievement, play_seal, play_letter_open, play_burn,
    play_sad, play_gorilla, play_error, play_notify, play_attach,
    play_streak, play_password_ok, play_password_fail,
)


# ================================================================
#  Global stores (initialized in App.__init__)
# ================================================================
note_store    = NoteStore()
player_store  = PlayerStore()
achiev_store  = AchievementStore()
letter_store  = LetterStore()
template_store= TemplateStore()


# ================================================================
#  Helper: QB-styled Toplevel window
# ================================================================
def qb_window(parent, title: str, width: int = 600,
               height: int = 400) -> tk.Toplevel:
    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=theme.bg)
    win.geometry(f"{width}x{height}")
    win.resizable(True, True)
    try:
        win.transient(parent)
        win.grab_set()
    except Exception:
        pass
    return win


def qb_btn(parent, text: str, command=None,
           width: int = 0, fg: str = None, selected: bool = False) -> tk.Button:
    b = tk.Button(parent, text=text, command=command,
                  bg=theme.bg_btn_sel if selected else theme.bg_btn,
                  fg=fg or (theme.accent if selected else theme.fg),
                  activebackground=theme.bg_btn_sel,
                  activeforeground=theme.accent,
                  font=theme.font_normal(10),
                  relief="flat", bd=1,
                  padx=6, pady=2,
                  cursor="hand2")
    if width:
        b.configure(width=width)
    return b


def qb_label(parent, text: str = "", fg: str = None,
             bg: str = None, size: int = 10,
             bold: bool = False, anchor: str = "w") -> tk.Label:
    return tk.Label(parent, text=text,
                    fg=fg or theme.fg,
                    bg=bg or theme.bg,
                    font=theme.font_bold(size) if bold else theme.font_normal(size),
                    anchor=anchor)


def qb_entry(parent, textvariable=None, width: int = 20) -> tk.Entry:
    e = tk.Entry(parent,
                 textvariable=textvariable,
                 bg=theme.bg_edit, fg=theme.fg,
                 insertbackground=theme.accent,
                 selectbackground=theme.select_bg,
                 selectforeground=theme.select_fg,
                 font=theme.font_normal(10),
                 relief="flat", bd=2,
                 width=width)
    return e


def qb_scrolled_text(parent, **kwargs) -> tk.Text:
    t = tk.Text(parent,
                bg=theme.bg_edit, fg=theme.fg,
                insertbackground=theme.accent,
                selectbackground=theme.select_bg,
                selectforeground=theme.select_fg,
                font=theme.font_normal(11),
                relief="flat", bd=0,
                wrap="word",
                undo=True, maxundo=100,
                **kwargs)
    return t


def qb_listbox(parent, **kwargs) -> tk.Listbox:
    lb = tk.Listbox(parent,
                    bg=theme.bg_edit, fg=theme.fg,
                    selectbackground=theme.select_bg,
                    selectforeground=theme.select_fg,
                    font=theme.font_normal(10),
                    relief="flat", bd=0,
                    activestyle="none",
                    **kwargs)
    return lb


def add_scrollbar(parent, widget, side="right", fill="y") -> tk.Scrollbar:
    sb = tk.Scrollbar(parent, bg=theme.bg_btn,
                      troughcolor=theme.bg,
                      activebackground=theme.accent,
                      relief="flat", bd=0, width=10)
    sb.pack(side=side, fill=fill)
    widget.configure(yscrollcommand=sb.set)
    sb.configure(command=widget.yview)
    return sb


# ================================================================
#  ASCII art logo (for header and screensaver)
# ================================================================
LOGO_SMALL = (
    " ███╗   ██╗ ██████╗ ██████╗  █████╗ ██████╗  ██████╗ \n"
    " ████╗  ██║██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██╔═══██╗\n"
    " ██╔██╗ ██║██║   ██║██████╔╝███████║██████╔╝██║   ██║\n"
    " ██║ ╚████║╚██████╔╝██████╔╝██║  ██║██║  ██║╚██████╔╝\n"
    " ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ "
)


# ================================================================
#  Rich-text formatting helpers for the editor
# ================================================================
def apply_formatting_to_widget(text_widget: tk.Text, spans: list):
    """Apply saved formatting spans to a freshly-loaded Text widget."""
    text_widget.tag_remove("sel", "1.0", "end")
    for span in spans:
        try:
            for tag in span.get("tags", []):
                text_widget.tag_add(tag, span["start"], span["end"])
        except Exception:
            pass


def extract_formatting_from_widget(text_widget: tk.Text,
                                   tag_names: list) -> list:
    """Collect all tag ranges from the Text widget into serialisable spans."""
    spans = []
    for tag in tag_names:
        ranges = text_widget.tag_ranges(tag)
        for i in range(0, len(ranges), 2):
            spans.append({
                "start": str(ranges[i]),
                "end":   str(ranges[i + 1]),
                "tags":  [tag],
            })
    return spans


# ================================================================
#  Mood-graph canvas drawing (shared by sidebar and stats)
# ================================================================
def draw_mood_bar(canvas: tk.Canvas, notes: list,
                  days: int = 60, width: int = 200, height: int = 30):
    canvas.delete("all")
    canvas.configure(bg=theme.bg_edit)
    slot_w = max(2, (width - 4) // days)
    t = datetime.date.today()
    date_set = {n.date: n.mood
                for n in notes if n.note_type == "normal"}
    for i in range(days):
        ds = (t - datetime.timedelta(days=days - 1 - i)).isoformat()
        mood = date_set.get(ds, "")
        x = 2 + i * slot_w
        if mood:
            col = MOOD_COLORS.get(mood, theme.fg_dim)
            vals = {":D": 1.0, ":)": 0.8, ":|": 0.5, ":(": 0.3, ";(": 0.15}
            bh  = int(height * vals.get(mood, 0.5))
            canvas.create_rectangle(x, height - bh, x + slot_w - 1,
                                    height, fill=col, outline="")
        else:
            canvas.create_rectangle(x, height - 2, x + slot_w - 1,
                                    height, fill=theme.bg_btn, outline="")
    # Today marker
    canvas.create_line(width - slot_w - 1, 0,
                       width - slot_w - 1, height,
                       fill=theme.accent, width=1)


# ================================================================
#  ┌──────────────────────────────────────────────────────────────┐
#  │                    MAIN APPLICATION                          │
#  └──────────────────────────────────────────────────────────────┘
# ================================================================
class App:
    def __init__(self):
        ensure_dirs(DATA_DIR, NOTES_DIR, MEDIA_DIR,
                    ASCII_DIR, BACKUP_DIR)

        # Load all data
        player_store.load()
        note_store.load_all()
        achiev_store.load()
        letter_store.load()
        template_store.load()

        # Apply saved theme and language
        theme.set(player_store.player.theme)
        lang.set(player_store.player.ui_language)

        # Current editing state
        self.current_note:    Note | None = None
        self.is_modified:     bool        = False
        self.auto_save_id:    str | None  = None
        self._status_restore: str | None  = None
        self._gap_date:       str | None  = None

        # Build the root window
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION} — {APP_TAGLINE}")
        self.root.configure(bg=theme.bg)
        self.root.geometry("1100x700")
        self.root.minsize(860, 560)

        # Icon — prefer the branded public/logo.png, fall back to icon.ico
        self._set_app_icon()

        self._build_ui()
        self._build_menu()
        self._bind_keys()
        self._start_autosave()
        self._post_init()

    # ============================================================
    #  App icon (logo.png → window icon + in-app logo)
    # ============================================================
    def _logo_candidates(self) -> list:
        """
        Possible locations of the branded logo (source + frozen builds).
        The 256px copy is preferred: Tk's PhotoImage renders the 6000px
        source logo blank, so it must never be loaded directly.
        """
        meipass = getattr(sys, "_MEIPASS", None)
        cands = [os.path.join(BASE_DIR, "public", "logo_256.png"),
                 os.path.join(BASE_DIR, "public", "logo_512.png"),
                 os.path.join(BASE_DIR, "public", "logo.png")]
        if meipass:
            cands.append(os.path.join(meipass, "public", "logo_256.png"))
            cands.append(os.path.join(meipass, "public", "logo_512.png"))
            cands.append(os.path.join(meipass, "public", "logo.png"))
        return cands

    def _set_app_icon(self):
        for logo_path in self._logo_candidates():
            try:
                img = tk.PhotoImage(file=logo_path)
                self.root.iconphoto(True, img)
                self._app_logo = img   # keep a reference so it is not GC'd
                return
            except Exception:
                continue
        try:
            self.root.iconbitmap(default=os.path.join(BASE_DIR, "icon.ico"))
        except Exception:
            pass

    def _app_logo_image(self):
        """Return a PhotoImage of the branded logo for dialogs, or None."""
        for logo_path in self._logo_candidates():
            try:
                return tk.PhotoImage(file=logo_path)
            except Exception:
                continue
        return None

    # ============================================================
    #  UI Construction
    # ============================================================
    def _build_ui(self):
        # ---- Top toolbar row ---------------------------------
        self.toolbar = tk.Frame(self.root, bg=theme.bg,
                                pady=3, padx=4)
        self.toolbar.pack(side="top", fill="x")
        self._build_toolbar()

        # ---- Thin separator line ----------------------------
        tk.Frame(self.root, bg=theme.border, height=1).pack(
            side="top", fill="x")

        # ---- Main content area (sidebar + editor) -----------
        self.main_pane = tk.PanedWindow(self.root,
                                        orient="horizontal",
                                        bg=theme.bg,
                                        sashwidth=4,
                                        sashrelief="flat")
        self.main_pane.pack(side="top", fill="both", expand=True)

        # Left sidebar
        self.sidebar_frame = tk.Frame(self.main_pane,
                                      bg=theme.bg, width=220)
        self.main_pane.add(self.sidebar_frame, minsize=180)
        self._build_sidebar()

        # Right: header + editor
        self.editor_area = tk.Frame(self.main_pane, bg=theme.bg)
        self.main_pane.add(self.editor_area, minsize=400)
        self._build_editor_area()

        # ---- Status bar ------------------------------------
        self.statusbar = tk.Label(
            self.root, text="", anchor="w",
            bg=theme.bg_header, fg=theme.fg_dim,
            font=theme.font_normal(9),
            relief="flat", bd=0, padx=6, pady=2)
        self.statusbar.pack(side="bottom", fill="x")

    # ---- Toolbar --------------------------------------------
    def _build_toolbar(self):
        # Row 1: formatting
        r1 = tk.Frame(self.toolbar, bg=theme.bg)
        r1.pack(side="top", fill="x")

        self.tb_buttons = {}

        def tb(key, text, cmd, row=r1, toggle=False):
            b = qb_btn(row, text, cmd)
            b.pack(side="left", padx=1)
            self.tb_buttons[key] = b
            return b

        def sep(row=r1):
            tk.Frame(row, bg=theme.border, width=1,
                     height=18).pack(side="left", padx=4)

        tb("bold",      "B",    self._fmt_bold)
        tb("italic",    "I",    self._fmt_italic)
        tb("underline", "U",    self._fmt_underline)
        tb("strike",    "S~",   self._fmt_strike)
        sep()
        tb("highlight", "HL",   self._fmt_highlight)
        tb("color",     "A/",   self._fmt_color)
        sep()

        # Font family combo
        qb_label(r1, "Font:", size=9).pack(side="left")
        self.font_var = tk.StringVar(value=player_store.player.default_font)
        fonts = ["Courier New", "Consolas", "Georgia", "Arial",
                 "Times New Roman", "Segoe UI", "Verdana",
                 "Calibri", "Comic Sans MS"]
        self.font_combo = tk.OptionMenu(r1, self.font_var,
                                        *fonts,
                                        command=self._fmt_font)
        self.font_combo.configure(
            bg=theme.bg_btn, fg=theme.fg,
            activebackground=theme.bg_btn_sel,
            activeforeground=theme.accent,
            font=theme.font_normal(9),
            relief="flat", bd=0, highlightthickness=0, padx=2)
        self.font_combo["menu"].configure(
            bg=theme.bg_edit, fg=theme.fg,
            font=theme.font_normal(9))
        self.font_combo.pack(side="left", padx=2)

        # Font size combo
        qb_label(r1, "Pt:", size=9).pack(side="left")
        self.size_var = tk.StringVar(value="11")
        sizes = ["8", "9", "10", "11", "12", "14",
                 "16", "18", "22", "26", "30"]
        self.size_combo = tk.OptionMenu(r1, self.size_var,
                                        *sizes,
                                        command=self._fmt_size)
        self.size_combo.configure(
            bg=theme.bg_btn, fg=theme.fg,
            activebackground=theme.bg_btn_sel,
            activeforeground=theme.accent,
            font=theme.font_normal(9),
            relief="flat", bd=0, highlightthickness=0, padx=2,
            width=3)
        self.size_combo["menu"].configure(
            bg=theme.bg_edit, fg=theme.fg,
            font=theme.font_normal(9))
        self.size_combo.pack(side="left", padx=2)

        sep()
        tb("h1",  "H1", self._fmt_h1)
        tb("h2",  "H2", self._fmt_h2)
        tb("h3",  "H3", self._fmt_h3)

        # Row 2: alignment, direction, media, actions
        r2 = tk.Frame(self.toolbar, bg=theme.bg)
        r2.pack(side="top", fill="x", pady=(2, 0))

        tb("al_left",   "◀=",  self._align_left,   row=r2)
        tb("al_center", " = ", self._align_center, row=r2)
        tb("al_right",  "=▶",  self._align_right,  row=r2)
        sep(r2)
        tb("ltr",   "LTR",    self._dir_ltr,        row=r2)
        tb("rtl",   "RTL",    self._dir_rtl,        row=r2)
        sep(r2)
        tb("img",   "[IMG]",  lambda: self._attach("image"), row=r2)
        tb("audio", "[SND]",  lambda: self._attach("audio"), row=r2)
        tb("video", "[VID]",  lambda: self._attach("video"), row=r2)
        tb("file",  "[FILE]", lambda: self._attach("file"),  row=r2)
        tb("ascii", "[ART]",  self.show_ascii_gallery,        row=r2)
        sep(r2)
        tb("save", "[ SAVE ]", self.save_note, row=r2)
        tb("new",  "[ NEW ]",  self.new_note,  row=r2)
        self.tb_buttons["save"].configure(fg=theme.accent)
        self.tb_buttons["new"].configure(fg=theme.fg)

    # ---- Sidebar --------------------------------------------
    def _build_sidebar(self):
        sb = self.sidebar_frame
        # Header buttons
        btn_frame = tk.Frame(sb, bg=theme.bg)
        btn_frame.pack(fill="x", padx=4, pady=(6, 2))
        new_btn = qb_btn(btn_frame, f"+ {lang('new_note')}",
                         self.new_note)
        new_btn.configure(fg=theme.accent, width=22)
        new_btn.pack(fill="x")

        # Level / XP
        self.lbl_level = qb_label(sb, size=9, bold=True,
                                   fg=theme.accent)
        self.lbl_level.pack(fill="x", padx=6, pady=(6, 0))
        self.lbl_xp = qb_label(sb, size=8, fg=theme.fg_dim)
        self.lbl_xp.pack(fill="x", padx=6)

        # Streak
        self.lbl_streak = qb_label(sb, size=9, fg=theme.accent)
        self.lbl_streak.pack(fill="x", padx=6, pady=(2, 4))

        # Separator
        tk.Frame(sb, bg=theme.border, height=1).pack(fill="x", padx=4)

        # Mood bar canvas (60-day mini graph)
        self.mood_canvas = tk.Canvas(sb, height=24,
                                     bg=theme.bg_edit,
                                     highlightthickness=0)
        self.mood_canvas.pack(fill="x", padx=4, pady=4)

        # Separator
        tk.Frame(sb, bg=theme.border, height=1).pack(fill="x", padx=4)

        # Entry list
        list_frame = tk.Frame(sb, bg=theme.bg)
        list_frame.pack(fill="both", expand=True,
                        padx=4, pady=4)
        self.entry_list = qb_listbox(list_frame, width=26)
        self.entry_list.pack(side="left", fill="both", expand=True)
        add_scrollbar(list_frame, self.entry_list)
        self.entry_list.bind("<<ListboxSelect>>",
                             self._on_list_select)

        # Daily quote
        tk.Frame(sb, bg=theme.border, height=1).pack(fill="x", padx=4)
        self.lbl_quote = qb_label(sb, size=8, fg=theme.fg_dim,
                                   anchor="center")
        self.lbl_quote.configure(wraplength=190, justify="center")
        self.lbl_quote.pack(fill="x", padx=4, pady=4)

    # ---- Editor area ----------------------------------------
    def _build_editor_area(self):
        ea = self.editor_area

        # Entry header bar
        hdr = tk.Frame(ea, bg=theme.bg_header, pady=4)
        hdr.pack(fill="x")

        self.lbl_date = qb_label(hdr, size=11, bold=True,
                                  fg=theme.accent,
                                  bg=theme.bg_header)
        self.lbl_date.pack(side="left", padx=8)

        # Mood dropdown
        self.mood_var = tk.StringVar(value=MOOD_SYMBOLS[0])
        mood_opts = [f"{s} {n}" for s, n in zip(MOOD_SYMBOLS, [m[1] for m in MOODS])]
        self.mood_menu = tk.OptionMenu(
            hdr, self.mood_var, *mood_opts,
            command=lambda _: self._mark_modified())
        self.mood_menu.configure(
            bg=theme.bg_btn, fg=theme.fg,
            activebackground=theme.bg_btn_sel,
            activeforeground=theme.accent,
            font=theme.font_normal(10),
            relief="flat", bd=0, highlightthickness=0)
        self.mood_menu["menu"].configure(
            bg=theme.bg_edit, fg=theme.fg,
            font=theme.font_normal(10))
        self.mood_menu.pack(side="left", padx=4)

        # Tags entry
        self.tags_var = tk.StringVar()
        self.tags_entry = qb_entry(hdr, textvariable=self.tags_var, width=28)
        self.tags_entry.pack(side="left", padx=4)
        self.tags_entry.insert(0, lang("tags_hint"))
        self.tags_entry.configure(fg=theme.fg_dim)
        self.tags_entry.bind("<FocusIn>",  self._tags_focus_in)
        self.tags_entry.bind("<FocusOut>", self._tags_focus_out)
        self.tags_var.trace_add("write", lambda *_: self._mark_modified())

        # Seal button
        seal_btn = qb_btn(hdr, "[SEAL]", self._seal_note)
        seal_btn.pack(side="right", padx=8)

        # Media bar (shown when note has attachments)
        self.media_frame = tk.Frame(ea, bg=theme.bg_header)
        # (not packed until a note with media is loaded)

        # Main text editor
        editor_frame = tk.Frame(ea, bg=theme.bg_edit)
        editor_frame.pack(fill="both", expand=True)

        self.editor = tk.Text(
            editor_frame,
            bg=theme.bg_edit,
            fg=theme.fg,
            insertbackground=theme.accent,
            selectbackground=theme.select_bg,
            selectforeground=theme.select_fg,
            font=theme.font_normal(11),
            relief="flat", bd=8,
            wrap="word",
            undo=True, maxundo=200,
            spacing1=2, spacing3=2,
        )
        self.editor.pack(side="left", fill="both", expand=True)
        add_scrollbar(editor_frame, self.editor)

        # Apply rich-text tags
        theme.apply_editor_tags(self.editor)

        # Track changes
        self.editor.bind("<<Modified>>", self._on_editor_modified)

        # Word-count update on key release
        self.editor.bind("<KeyRelease>", self._update_wordcount)

    # ============================================================
    #  Menu bar
    # ============================================================
    def _build_menu(self):
        mb = tk.Menu(self.root,
                     bg=theme.bg, fg=theme.fg,
                     activebackground=theme.select_bg,
                     activeforeground=theme.select_fg,
                     font=theme.font_normal(10),
                     relief="flat", bd=0)
        self.root.configure(menu=mb)

        def submenu():
            return tk.Menu(mb, tearoff=0,
                           bg=theme.bg_edit, fg=theme.fg,
                           activebackground=theme.select_bg,
                           activeforeground=theme.select_fg,
                           font=theme.font_normal(10))

        # File
        m = submenu()
        mb.add_cascade(label="File", menu=m)
        m.add_command(label=f"{lang('new_note')}  Ctrl+N",
                      command=self.new_note)
        m.add_command(label=f"{lang('save_note')}  Ctrl+S",
                      command=self.save_note)
        m.add_separator()
        m.add_command(label=lang("burn_note"),     command=self.burn_note)
        m.add_separator()
        em = submenu()
        m.add_cascade(label=lang("export"), menu=em)
        em.add_command(label="Plain Text",  command=self.export_plain)
        em.add_command(label="Encrypted",   command=self.export_encrypted)
        em.add_command(label=lang("annual_review"), command=self.annual_review)
        m.add_separator()
        m.add_command(label=f"{lang('quit')}  Alt+F4",
                      command=self._on_close)

        # View
        m = submenu()
        mb.add_cascade(label="View", menu=m)
        m.add_command(label=lang("history"),     command=self.show_history)
        m.add_command(label=f"{lang('cozy_mode')}  F5",
                      command=self.show_cozy)
        m.add_separator()
        m.add_command(label=f"{lang('stats')}  F6",
                      command=self.show_stats)
        m.add_command(label=f"{lang('calendar')}  F7",
                      command=self.show_calendar)
        m.add_command(label=lang("mood_graph"),  command=self.show_mood_graph)
        m.add_command(label=lang("word_freq"),   command=self.show_word_freq)
        m.add_command(label=lang("month_view"),  command=self.show_month_view)

        # Tools
        m = submenu()
        mb.add_cascade(label="Tools", menu=m)
        m.add_command(label=f"{lang('grep')}  Ctrl+F",
                      command=self.show_grep)
        m.add_separator()
        m.add_command(label=lang("future_letter"), command=self.write_future_letter)
        m.add_command(label=lang("unsent_letter"), command=self.write_unsent_letter)
        m.add_separator()
        m.add_command(label=f"{lang('ascii_art')}  F8",
                      command=self.show_ascii_gallery)
        m.add_command(label=f"{lang('templates')}  F9",
                      command=self.show_templates)
        m.add_command(label="Screensaver  F10",
                      command=self.run_screensaver)
        m.add_separator()
        m.add_command(label=f"{lang('settings')}  F12",
                      command=self.show_settings)
        m.add_command(label=lang("about"),  command=self.show_about)

    # ============================================================
    #  Keyboard shortcuts
    # ============================================================
    def _bind_keys(self):
        self.root.bind("<Control-n>", lambda e: self.new_note())
        self.root.bind("<Control-N>", lambda e: self.new_note())
        self.root.bind("<Control-s>", lambda e: self.save_note())
        self.root.bind("<Control-S>", lambda e: self.save_note())
        self.root.bind("<Control-f>", lambda e: self.show_grep())
        self.root.bind("<Control-F>", lambda e: self.show_grep())
        self.root.bind("<Control-b>", lambda e: self._fmt_bold())
        self.root.bind("<Control-B>", lambda e: self._fmt_bold())
        self.root.bind("<Control-i>", lambda e: self._fmt_italic())
        self.root.bind("<Control-I>", lambda e: self._fmt_italic())
        self.root.bind("<Control-u>", lambda e: self._fmt_underline())
        self.root.bind("<Control-U>", lambda e: self._fmt_underline())
        self.root.bind("<F5>",  lambda e: self.show_cozy())
        self.root.bind("<F6>",  lambda e: self.show_stats())
        self.root.bind("<F7>",  lambda e: self.show_calendar())
        self.root.bind("<F8>",  lambda e: self.show_ascii_gallery())
        self.root.bind("<F9>",  lambda e: self.show_templates())
        self.root.bind("<F10>", lambda e: self.run_screensaver())
        self.root.bind("<F12>", lambda e: self.show_settings())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ============================================================
    #  Post-init (called after mainloop starts via after())
    # ============================================================
    def _post_init(self):
        self.root.after(200, self._startup_sequence)

    def _startup_sequence(self):
        play_startup()
        self._refresh_sidebar()
        self._update_sidebar_labels()

        # A day can hold as many notes as you want now, so every
        # launch opens onto a fresh blank page — today's earlier
        # entries (if any) are still one click away in the sidebar.
        self._setup_new_note()

        # First-run welcome
        if not player_store.player.last_open:
            self.root.after(600, self._show_welcome)

        # Check sealed letters
        self.root.after(800, self._check_letters)

        # "This day last year"
        if player_store.player.show_last_year:
            self.root.after(1000, self._check_last_year)

        # Gap detection
        self.root.after(1200, self._check_gaps)

        player_store.player.last_open = today()
        player_store.save()

    def _show_welcome(self):
        messagebox.showinfo(
            f"{APP_NAME} v{APP_VERSION}",
            "Welcome.\n\n"
            "This is your space.\n"
            "No internet. No cloud. No ads. No algorithm.\n\n"
            "Just you and the blue screen.\n\n"
            '10 PRINT "you matter"\n'
            "20 GOTO 10"
        )

    # ============================================================
    #  Auto-save
    # ============================================================
    def _start_autosave(self):
        # Cancel any pending timer first so re-applying settings never
        # stacks multiple autosave loops.
        if getattr(self, "auto_save_id", None):
            try:
                self.root.after_cancel(self.auto_save_id)
            except Exception:
                pass
            self.auto_save_id = None
        secs = player_store.player.auto_save_secs
        if secs > 0:
            self.auto_save_id = self.root.after(
                secs * 1000, self._do_autosave)

    def _do_autosave(self):
        if self.is_modified:
            self.save_note(silent=True)
        self._start_autosave()

    # ============================================================
    #  Note state
    # ============================================================
    def _mark_modified(self, *_):
        if not self.is_modified:
            self.is_modified = True
            t = self.root.title()
            if not t.endswith(" *"):
                self.root.title(t + " *")

    def _on_editor_modified(self, event=None):
        if self.editor.edit_modified():
            self._mark_modified()
            self.editor.edit_modified(False)

    def _update_wordcount(self, *_):
        text = self.editor.get("1.0", "end-1c")
        wc   = count_words(text)
        self._set_status(f"  {wc} {lang('words')}")

    def _set_status(self, msg: str, duration_ms: int = 0):
        self.statusbar.configure(text=msg)
        if duration_ms:
            self.root.after(duration_ms, self._restore_status)

    def _restore_status(self):
        player = player_store.player
        lvl    = get_level_name(player.xp)
        streak = player.current_streak
        xp     = player.xp
        msg    = (f"  {lvl}  |  XP: {xp}  |  "
                  f"Streak: {streak}d  |  {theme.name}")
        self.statusbar.configure(text=msg)

    # ============================================================
    #  Sidebar refresh
    # ============================================================
    def _refresh_sidebar(self):
        self.entry_list.delete(0, "end")
        normals = sorted(note_store.normal_notes(),
                         key=lambda n: (n.date, n.time_written),
                         reverse=True)
        self._sidebar_notes = normals
        # A day can hold many notes now, so only show the time
        # alongside the date when that date has more than one entry.
        date_counts = {}
        for n in normals:
            date_counts[n.date] = date_counts.get(n.date, 0) + 1
        for n in normals:
            mood  = n.mood
            if date_counts[n.date] > 1:
                label = f"{friendly_date(n.date)}  {n.time_written}  {mood}"
            else:
                label = f"{friendly_date(n.date)}  {mood}"
            self.entry_list.insert("end", label)
            # Color the row by mood
            idx = self.entry_list.size() - 1
            self.entry_list.itemconfigure(
                idx,
                foreground=MOOD_COLORS.get(mood, theme.fg))

    def _update_sidebar_labels(self):
        player = player_store.player
        lvl    = get_level_name(player.xp)
        nxt    = xp_for_next_level(player.xp)
        streak = player.current_streak

        self.lbl_level.configure(
            text=f"{lang('level')}: {lvl}")
        self.lbl_xp.configure(
            text=f"{lang('xp')}: {player.xp} / {nxt}")
        streak_txt = (f"🔥 {lang('streak')}: {streak}d"
                      if streak >= 3
                      else f"{lang('streak')}: {streak}d")
        self.lbl_streak.configure(text=streak_txt)

        # Daily quote
        if player.show_daily_quote:
            q = daily_quote(DAILY_QUOTES)
            self.lbl_quote.configure(text=f'"{q}"')
        else:
            self.lbl_quote.configure(text="")

        # Mood bar
        cw = self.mood_canvas.winfo_reqwidth() or 200
        draw_mood_bar(self.mood_canvas,
                      note_store.normal_notes(),
                      days=60, width=cw, height=24)

    def _select_sidebar_for_note(self, note: Note):
        for i, n in enumerate(self._sidebar_notes):
            if n.id == note.id:
                self.entry_list.selection_clear(0, "end")
                self.entry_list.selection_set(i)
                self.entry_list.see(i)
                break

    def _on_list_select(self, event=None):
        sel = self.entry_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._sidebar_notes):
            return
        note = self._sidebar_notes[idx]
        if self.is_modified:
            if messagebox.askyesno(APP_NAME,
                lang("unsaved_warn")):
                self.save_note(silent=True)
        self._load_note(note)

    # ============================================================
    #  Note operations
    # ============================================================
    def _get_mood_symbol(self) -> str:
        val = self.mood_var.get()
        return val.split()[0] if val else ":|"

    def _set_mood_symbol(self, symbol: str):
        for s, n in zip(MOOD_SYMBOLS, [m[1] for m in MOODS]):
            if s == symbol:
                self.mood_var.set(f"{s} {n}")
                return
        self.mood_var.set(f":| Neutral")

    def _setup_new_note(self):
        self.current_note = None
        self.is_modified  = False
        self._gap_date    = None
        self.editor.delete("1.0", "end")
        self.editor.edit_reset()
        self.editor.edit_modified(False)
        self.lbl_date.configure(text=friendly_date(today()))
        self._set_mood_symbol(":)")
        self._clear_tags_hint()
        self.root.title(f"{APP_NAME} v{APP_VERSION} — {lang('new_note')}")
        self._hide_media_bar()
        self.editor.focus_set()

        # Apply default direction
        if player_store.player.default_rtl:
            self._dir_rtl()

    def new_note(self):
        if self.is_modified:
            if messagebox.askyesno(APP_NAME, lang("unsaved_warn")):
                self.save_note(silent=True)
        # Always starts a fresh entry — a day is no longer limited
        # to one note, so "New Note" never silently reopens an old one.
        self._setup_new_note()

    def _load_note(self, note: Note):
        self.current_note = note
        self.is_modified  = False
        self.editor.configure(state="normal")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", note.content)
        # Re-apply saved formatting
        if note.formatting:
            apply_formatting_to_widget(self.editor, note.formatting)
        self.editor.edit_modified(False)
        self.editor.edit_reset()
        self.lbl_date.configure(text=friendly_date(note.date))
        self._set_mood_symbol(note.mood)
        tags_text = note.tags or ""
        self.tags_entry.configure(fg=theme.fg)
        self.tags_entry.delete(0, "end")
        self.tags_entry.insert(0, tags_text)
        self.root.title(
            f"{APP_NAME} v{APP_VERSION} — {friendly_date(note.date)}")
        # Media bar
        if note.media:
            self._show_media_bar(note)
        else:
            self._hide_media_bar()
        self._select_sidebar_for_note(note)
        self.editor.focus_set()
        self._update_wordcount()

    def save_note(self, silent: bool = False):
        content    = self.editor.get("1.0", "end-1c")
        mood       = self._get_mood_symbol()
        tags       = self.tags_var.get().strip()
        if tags == lang("tags_hint"):
            tags = ""
        formatting = extract_formatting_from_widget(
            self.editor, theme.all_text_tags())
        is_new     = self.current_note is None

        if not content.strip() and is_new:
            if not silent:
                self._set_status(f"  (empty note not saved)",
                                 duration_ms=2000)
            return

        # Determine note date — a gap-fill note (started from the
        # "missing days" prompt) keeps its earlier date instead of today.
        note_date = today()
        if self.current_note:
            note_date = self.current_note.date
        elif self._gap_date:
            note_date = self._gap_date
        self._gap_date = None

        if is_new:
            note = Note(
                id=generate_note_id(),
                date=note_date,
                time_written=now_time(),
                mood=mood, content=content,
                tags=tags, note_type="normal",
                formatting=formatting,
            )
        else:
            note = self.current_note
            note.mood        = mood
            note.content     = content
            note.tags        = tags
            note.formatting  = formatting
            note.time_written = now_time()

        # XP on new notes
        if is_new:
            xp = calc_note_xp(
                content,
                has_media=bool(note.media),
                used_formatting=bool(formatting))
            note.xp_earned = xp
            levelled = player_store.add_xp(xp)
            if levelled:
                self.root.after(100, self._on_level_up)

        note_store.save_note(note)
        if is_new:
            note_store.notes.append(note)
            note_store.notes.sort(key=lambda n: n.date)
        self.current_note = note
        self.is_modified  = False
        self.editor.edit_modified(False)
        self.root.title(
            f"{APP_NAME} v{APP_VERSION} — {friendly_date(note.date)}")

        # Post-save
        player_store.player.total_words += note.word_count
        newly = check_achievements(note_store, achiev_store,
                                   player_store.player)
        if newly:
            achiev_store.save()
            self.root.after(200, lambda: self._show_achievements(newly))

        streak = player_store.player.current_streak
        if is_new and streak >= 3:
            bonus = apply_streak_bonus(player_store)
            if bonus > 0:
                play_streak(streak)

        player_store.save()
        self._refresh_sidebar()
        self._update_sidebar_labels()

        if not silent:
            play_save()
            self._set_status(f"  ✓ {lang('save_ok')} — "
                             f"{friendly_date(note.date)}",
                             duration_ms=2000)
        self.root.after(2100, self._restore_status)

    def _on_level_up(self):
        play_level_up()
        lvl = get_level_name(player_store.player.xp)
        messagebox.showinfo(APP_NAME,
            f"LEVEL UP!\n\nYou are now:\n{lvl}\n\n"
            f"Total XP: {player_store.player.xp}")
        self._update_sidebar_labels()

    def _show_achievements(self, newly: list):
        play_achievement()
        names = "\n".join(
            Achievement.NAMES.get(aid, aid) for aid in newly)
        messagebox.showinfo(APP_NAME,
            f"ACHIEVEMENT UNLOCKED!\n\n{names}")

    def burn_note(self):
        if not self.current_note:
            messagebox.showinfo(APP_NAME, "No note loaded.")
            return
        answer = simpledialog.askstring(
            APP_NAME,
            lang("confirm_burn"))
        if answer and answer.strip().upper() == "YES":
            note_store.delete_note(self.current_note)
            achiev_store.unlock("BURNED_NOTE")
            achiev_store.save()
            play_burn()
            self._setup_new_note()
            self._refresh_sidebar()
            self._update_sidebar_labels()

    # ============================================================
    #  Formatting ops
    # ============================================================
    def _toggle_tag(self, tag: str):
        try:
            sel_start = self.editor.index("sel.first")
            sel_end   = self.editor.index("sel.last")
        except tk.TclError:
            return   # no selection
        # Check if tag already fully covers selection
        ranges = self.editor.tag_ranges(tag)
        covered = any(
            self.editor.compare(str(ranges[i]),   "<=", sel_start) and
            self.editor.compare(str(ranges[i+1]), ">=", sel_end)
            for i in range(0, len(ranges), 2))
        if covered:
            self.editor.tag_remove(tag, sel_start, sel_end)
        else:
            self.editor.tag_add(tag, sel_start, sel_end)
        self._mark_modified()
        achiev_store.unlock("RICH_TEXT")

    def _fmt_bold(self):        self._toggle_tag("bold")
    def _fmt_italic(self):      self._toggle_tag("italic")
    def _fmt_underline(self):   self._toggle_tag("underline")
    def _fmt_strike(self):      self._toggle_tag("strikethrough")

    def _fmt_highlight(self):
        # Cycle through highlight colors
        tags   = ["hl_yellow", "hl_cyan", "hl_green", "hl_magenta"]
        try:
            sel_start = self.editor.index("sel.first")
            sel_end   = self.editor.index("sel.last")
        except tk.TclError:
            return
        # Remove existing highlight, apply next
        current = None
        for t in tags:
            ranges = self.editor.tag_ranges(t)
            if any(self.editor.compare(str(ranges[i]), "<=", sel_start)
                   for i in range(0, len(ranges), 2)):
                current = t
                break
        next_tag = tags[(tags.index(current) + 1) % len(tags)] \
                   if current else tags[0]
        for t in tags:
            self.editor.tag_remove(t, sel_start, sel_end)
        self.editor.tag_add(next_tag, sel_start, sel_end)
        self._mark_modified()

    def _fmt_color(self):
        color = colorchooser.askcolor(
            color=theme.fg, title="Text color",
            parent=self.root)[1]
        if not color:
            return
        try:
            sel_start = self.editor.index("sel.first")
            sel_end   = self.editor.index("sel.last")
        except tk.TclError:
            return
        # Create a unique tag for this color
        tag = f"col_{color.replace('#','')}"
        self.editor.tag_configure(tag, foreground=color)
        self.editor.tag_add(tag, sel_start, sel_end)
        self._mark_modified()

    def _fmt_font(self, font_name: str):
        try:
            sel_start = self.editor.index("sel.first")
            sel_end   = self.editor.index("sel.last")
        except tk.TclError:
            return
        size = int(self.size_var.get() or 11)
        tag  = f"font_{font_name.replace(' ','_')}_{size}"
        self.editor.tag_configure(
            tag, font=(font_name, size))
        self.editor.tag_add(tag, sel_start, sel_end)
        self._mark_modified()

    def _fmt_size(self, size_str: str):
        try:
            sel_start = self.editor.index("sel.first")
            sel_end   = self.editor.index("sel.last")
        except tk.TclError:
            return
        size = int(size_str)
        font = self.font_var.get() or theme.font
        tag  = f"size_{size}"
        self.editor.tag_configure(
            tag, font=(font, size))
        self.editor.tag_add(tag, sel_start, sel_end)
        self._mark_modified()

    def _fmt_heading(self, tag: str):
        # Apply to current line if no selection
        try:
            sel_start = self.editor.index("sel.first")
            sel_end   = self.editor.index("sel.last")
        except tk.TclError:
            cur       = self.editor.index("insert")
            sel_start = self.editor.index(f"{cur} linestart")
            sel_end   = self.editor.index(f"{cur} lineend")
        for h in ("h1", "h2", "h3"):
            self.editor.tag_remove(h, sel_start, sel_end)
        self.editor.tag_add(tag, sel_start, sel_end)
        self._mark_modified()

    def _fmt_h1(self): self._fmt_heading("h1")
    def _fmt_h2(self): self._fmt_heading("h2")
    def _fmt_h3(self): self._fmt_heading("h3")

    def _align_left(self):   self._toggle_tag("align_left")
    def _align_center(self): self._toggle_tag("align_center")
    def _align_right(self):  self._toggle_tag("align_right")

    def _dir_ltr(self):
        self.editor.configure(
            xscrollcommand=None)   # LTR is tk default
        # In tk there's no true BiDi — we set entry direction
        self.tags_entry.configure(justify="left")

    def _dir_rtl(self):
        # tkinter doesn't support true RTL but we signal it via
        # right-justify so at minimum Farsi/Arabic reads naturally
        self.tags_entry.configure(justify="right")

    # ============================================================
    #  Tags entry helpers
    # ============================================================
    def _tags_focus_in(self, *_):
        if self.tags_entry.get() == lang("tags_hint"):
            self.tags_entry.delete(0, "end")
            self.tags_entry.configure(fg=theme.fg)

    def _tags_focus_out(self, *_):
        if not self.tags_entry.get():
            self.tags_entry.insert(0, lang("tags_hint"))
            self.tags_entry.configure(fg=theme.fg_dim)

    def _clear_tags_hint(self):
        self.tags_entry.delete(0, "end")
        self.tags_entry.configure(fg=theme.fg_dim)
        self.tags_entry.insert(0, lang("tags_hint"))

    # ============================================================
    #  Media bar
    # ============================================================
    def _show_media_bar(self, note: Note):
        self._hide_media_bar()
        self.media_frame = tk.Frame(
            self.editor_area, bg=theme.bg_header, pady=2)
        self.media_frame.pack(fill="x", before=self.editor.master)
        for m in note.media:
            icon = {"image": "[IMG]", "audio": "[SND]",
                    "video": "[VID]", "file": "[FILE]"}.get(
                        m.media_type, "[FILE]")
            b = qb_btn(
                self.media_frame,
                f"{icon} {m.caption[:18]}",
                lambda path=m.path: self._open_media(path),
            )
            b.pack(side="left", padx=2)

    def _hide_media_bar(self):
        if hasattr(self, "media_frame") and self.media_frame.winfo_exists():
            self.media_frame.destroy()

    def _open_media(self, rel_path: str):
        full = os.path.join(DATA_DIR, rel_path)
        if not os.path.isfile(full):
            messagebox.showerror(APP_NAME, f"File not found:\n{full}")
            return
        # Open with system default app
        try:
            if sys.platform == "win32":
                os.startfile(full)
            elif sys.platform == "darwin":
                subprocess.run(["open", full])
            else:
                subprocess.run(["xdg-open", full])
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    def _attach(self, media_type: str):
        filters = {
            "image": [("Images","*.png *.jpg *.jpeg *.bmp *.gif"),("All","*.*")],
            "audio": [("Audio","*.mp3 *.wav *.ogg *.flac"),("All","*.*")],
            "video": [("Video","*.mp4 *.avi *.mkv *.mov"),("All","*.*")],
            "file":  [("All files","*.*")],
        }
        path = filedialog.askopenfilename(
            title=f"Attach {media_type}",
            filetypes=filters.get(media_type, [("All","*.*")]),
            parent=self.root)
        if not path:
            return
        # Copy into data/media/
        ts    = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        base  = os.path.splitext(os.path.basename(path))
        fname = f"{base[0][:40]}_{ts}{base[1]}"
        dest  = os.path.join(MEDIA_DIR, fname)
        try:
            shutil.copy2(path, dest)
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))
            return

        # Save note first to get an ID
        if not self.current_note:
            self.save_note(silent=True)
        if not self.current_note:
            return

        # Add MediaRef to note
        ref = MediaRef(
            path=os.path.join("media", fname),
            media_type=media_type,
            caption=os.path.basename(path))
        self.current_note.media.append(ref)
        note_store.save_note(self.current_note)

        # Insert inline tag
        icon = {"image":"[IMG]","audio":"[SND]",
                "video":"[VID]","file":"[FILE]"}.get(media_type,"[FILE]")
        tag_text = f" {icon} {os.path.basename(path)} "
        self.editor.tag_configure(
            "media_tag", foreground=theme.border, underline=True)
        self.editor.insert("insert", tag_text, "media_tag")

        # Show media bar
        self._show_media_bar(self.current_note)
        player_store.add_xp(10)
        achiev_store.unlock("MEDIA_STAR")
        achiev_store.save()
        play_attach()
        self._mark_modified()

    # ============================================================
    #  Future / Unsent Letters
    # ============================================================
    def _seal_note(self):
        content = self.editor.get("1.0", "end-1c").strip()
        if not content:
            return
        unlock_date = simpledialog.askstring(
            APP_NAME,
            "Seal until date (YYYY-MM-DD):",
            parent=self.root)
        if not unlock_date:
            return
        try:
            datetime.date.fromisoformat(unlock_date)
        except ValueError:
            messagebox.showerror(APP_NAME, "Invalid date format.")
            return
        if unlock_date <= today():
            messagebox.showerror(APP_NAME,
                "Seal date must be in the future.")
            return
        to_name = simpledialog.askstring(
            APP_NAME,
            "Letter to (blank = Future Me):",
            parent=self.root) or "Future Me"
        letter = Letter(
            written_date=today(),
            unlock_date=unlock_date,
            to_name=to_name,
            content=content,
            letter_type="future")
        letter_store.add(letter)
        player_store.add_xp(XP_FUTURE_LETTER)
        achiev_store.unlock("FUTURE_LETTER")
        achiev_store.save()
        player_store.save()
        play_seal()
        messagebox.showinfo(APP_NAME,
            f"{lang('future_sealed')} {unlock_date}\n\n"
            "Past-you will be waiting there.")
        self.new_note()

    def write_future_letter(self):
        messagebox.showinfo(APP_NAME,
            "LETTER TO FUTURE ME\n\n"
            "Write your letter in the editor,\n"
            "then press [SEAL] to lock it until your chosen date.")
        self._setup_new_note()
        self.lbl_date.configure(
            text=f"Future Letter — {today()}")

    def write_unsent_letter(self):
        to_name = simpledialog.askstring(
            APP_NAME, "Unsent letter to:",
            parent=self.root) or ""
        self._setup_new_note()
        header = (f"Dear {to_name},\n\n" if to_name
                  else "To whom it may concern,\n\n")
        self.editor.insert("1.0", header)
        self.editor.tag_add("bold", "1.0", "1.end")
        self.lbl_date.configure(
            text=f"Unsent Letter — {today()}")
        self.tags_entry.delete(0, "end")
        self.tags_entry.insert(0, "#unsent #letter")
        self.tags_entry.configure(fg=theme.fg)
        play_sad()

    def _check_letters(self):
        due = letter_store.due_letters()
        if not due:
            return
        play_letter_open()
        if messagebox.askyesno(APP_NAME,
            f"{lang('letter_opened')}\n\n"
            f"{len(due)} letter(s) from past-you are ready.\n"
            "Read them now?"):
            for letter in due:
                self._show_letter(letter)
                letter.is_read = True
            letter_store.save()

    def _show_letter(self, letter: Letter):
        win = qb_window(self.root,
            f"LETTER TO {letter.to_name.upper()} "
            f"— Written {letter.written_date}",
            width=680, height=500)
        tk.Label(win,
                 text=f"[ {letter.written_date} → {letter.unlock_date} ]"
                      f"\nDear {letter.to_name}...",
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(11),
                 justify="center").pack(fill="x", pady=8)
        tf = tk.Frame(win, bg=theme.bg_edit)
        tf.pack(fill="both", expand=True, padx=8)
        txt = qb_scrolled_text(tf, state="disabled")
        txt.pack(side="left", fill="both", expand=True)
        add_scrollbar(tf, txt)
        txt.configure(state="normal")
        txt.insert("1.0", letter.content)
        txt.configure(state="disabled")
        qb_btn(win, "Close — and carry this forward",
               win.destroy).pack(pady=8)

    # ============================================================
    #  Startup checks
    # ============================================================
    def _check_last_year(self):
        ly    = last_year_date()
        found = note_store.find_by_date(ly)
        if not found:
            return
        play_notify()
        if messagebox.askyesno(APP_NAME,
            f"{lang('last_year')}\n({ly})\n\n"
            "Would you like to read it?"):
            self._show_read_only_note(found, lang("last_year"))

    def _check_gaps(self):
        note_dicts = [{"date": n.date, "note_type": n.note_type}
                      for n in note_store.notes]
        gaps = get_gap_dates(note_dicts)
        if not gaps:
            return
        if messagebox.askyesno(APP_NAME,
            f"{lang('fill_gaps')}\n\n"
            f"Earliest gap: {gaps[0]}"):
            # Set up editor for that date
            self._setup_new_note()
            self.lbl_date.configure(text=friendly_date(gaps[0]))
            # Store the gap date for saving
            self._gap_date = gaps[0]

    def _show_read_only_note(self, note: Note, title: str = ""):
        win = qb_window(self.root, title or friendly_date(note.date),
                        width=640, height=440)
        tk.Label(win,
                 text=f"{friendly_date(note.date)}  {note.mood}  {note.tags}",
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(10)).pack(fill="x", padx=8, pady=4)
        tf = tk.Frame(win, bg=theme.bg_edit)
        tf.pack(fill="both", expand=True, padx=8)
        txt = qb_scrolled_text(tf, state="disabled")
        txt.pack(side="left", fill="both", expand=True)
        add_scrollbar(tf, txt)
        txt.configure(state="normal")
        txt.insert("1.0", note.content)
        if note.formatting:
            apply_formatting_to_widget(txt, note.formatting)
        txt.configure(state="disabled")
        qb_btn(win, lang("close"), win.destroy).pack(pady=6)

    # ============================================================
    #  History window
    # ============================================================
    def show_history(self):
        normals = sorted(note_store.normal_notes(),
                         key=lambda n: n.date, reverse=True)
        if not normals:
            messagebox.showinfo(APP_NAME, lang("no_notes"))
            return
        win = qb_window(self.root, lang("history"),
                        width=700, height=480)
        tk.Label(win, text=lang("history"),
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(12)).pack(pady=6)
        fr = tk.Frame(win, bg=theme.bg)
        fr.pack(fill="both", expand=True, padx=8)
        lb = qb_listbox(fr, width=70)
        lb.pack(side="left", fill="both", expand=True)
        add_scrollbar(fr, lb)
        for n in normals:
            preview = n.content[:60].replace("\n", " ")
            lb.insert("end", f"{friendly_date(n.date)}  {n.mood}  {preview}")
            lb.itemconfigure(lb.size()-1,
                foreground=MOOD_COLORS.get(n.mood, theme.fg))
        def open_sel():
            sel = lb.curselection()
            if not sel:
                return
            note = normals[sel[0]]
            win.destroy()
            if self.is_modified:
                if messagebox.askyesno(APP_NAME, lang("unsaved_warn")):
                    self.save_note(silent=True)
            self._load_note(note)
        qb_btn(win, lang("open_selected"), open_sel).pack(pady=6)

    # ============================================================
    #  Cozy reading mode
    # ============================================================
    def show_cozy(self):
        normals = sorted(note_store.normal_notes(),
                         key=lambda n: n.date, reverse=True)
        if not normals:
            messagebox.showinfo(APP_NAME, lang("no_notes"))
            return
        win = qb_window(self.root, lang("cozy_mode"),
                        width=860, height=620)
        idx = tk.IntVar(value=0)

        lbl_hdr = tk.Label(win, text="", bg=theme.bg, fg=theme.accent,
                           font=theme.font_bold(11))
        lbl_hdr.pack(fill="x", padx=8, pady=4)

        tf  = tk.Frame(win, bg=theme.bg_edit)
        tf.pack(fill="both", expand=True, padx=8)
        txt = qb_scrolled_text(tf, state="disabled")
        txt.pack(side="left", fill="both", expand=True)
        add_scrollbar(tf, txt)
        theme.apply_editor_tags(txt)

        lbl_num = tk.Label(win, text="", bg=theme.bg, fg=theme.fg_dim,
                           font=theme.font_normal(9))
        lbl_num.pack()

        def load(i: int):
            i = max(0, min(i, len(normals) - 1))
            idx.set(i)
            note = normals[i]
            lbl_hdr.configure(
                text=f"{friendly_date(note.date)}   {note.mood}   {note.tags}")
            lbl_num.configure(
                text=f"Note {i+1} of {len(normals)}")
            txt.configure(state="normal")
            txt.delete("1.0", "end")
            txt.insert("1.0", note.content)
            if note.formatting:
                apply_formatting_to_widget(txt, note.formatting)
            txt.configure(state="disabled")

        nav = tk.Frame(win, bg=theme.bg)
        nav.pack(fill="x", pady=4)
        qb_btn(nav, lang("prev"),
               lambda: load(idx.get() + 1)).pack(side="left", padx=8)
        qb_btn(nav, lang("next"),
               lambda: load(idx.get() - 1)).pack(side="right", padx=8)
        qb_btn(nav, lang("close"), win.destroy).pack(side="right", padx=4)
        load(0)
        win.bind("<Left>",  lambda e: load(idx.get() + 1))
        win.bind("<Right>", lambda e: load(idx.get() - 1))

    # ============================================================
    #  Grep / Search
    # ============================================================
    def show_grep(self):
        win = qb_window(self.root, lang("grep"),
                        width=680, height=480)
        tk.Label(win, text=lang("grep_prompt"),
                 bg=theme.bg, fg=theme.fg,
                 font=theme.font_normal(10)).pack(pady=4)
        sv = tk.StringVar()
        qb_entry(win, textvariable=sv, width=50).pack(pady=2)
        results_frame = tk.Frame(win, bg=theme.bg)
        results_frame.pack(fill="both", expand=True, padx=8, pady=4)
        lb = qb_listbox(results_frame, width=70)
        lb.pack(side="left", fill="both", expand=True)
        add_scrollbar(results_frame, lb)
        lbl_count = qb_label(win, size=9, fg=theme.fg_dim)
        lbl_count.pack()
        _results = []

        def do_search(*_):
            term = sv.get().strip().lower()
            if not term:
                return
            achiev_store.unlock("GREP_USED")
            found = note_store.search(term)
            _results.clear()
            lb.delete(0, "end")
            for n in sorted(found, key=lambda x: x.date, reverse=True):
                preview = n.content[:60].replace("\n", " ")
                lb.insert("end",
                    f"{friendly_date(n.date)}  {n.mood}  {preview}")
                lb.itemconfigure(lb.size()-1,
                    foreground=MOOD_COLORS.get(n.mood, theme.fg))
                _results.append(n)
            lbl_count.configure(
                text=(f"{len(found)} {lang('grep_results')}: \"{term}\""
                      if found else
                      f"{lang('grep_none')} \"{term}\""))

        def open_sel():
            sel = lb.curselection()
            if not sel or sel[0] >= len(_results):
                return
            note = _results[sel[0]]
            win.destroy()
            if self.is_modified:
                if messagebox.askyesno(APP_NAME, lang("unsaved_warn")):
                    self.save_note(silent=True)
            self._load_note(note)

        sv.trace_add("write", do_search)
        qb_btn(win, lang("open_selected"), open_sel).pack(pady=4)
        qb_btn(win, lang("close"), win.destroy).pack()

    # ============================================================
    #  Stats
    # ============================================================
    def show_stats(self):
        from features.stats import StatsWindow
        StatsWindow(self.root, note_store, player_store, achiev_store)

    def show_calendar(self):
        from features.stats import CalendarWindow
        CalendarWindow(self.root, note_store)

    def show_mood_graph(self):
        from features.stats import MoodGraphWindow
        MoodGraphWindow(self.root, note_store)

    def show_word_freq(self):
        from features.stats import WordFreqWindow
        WordFreqWindow(self.root, note_store)

    def show_month_view(self):
        from features.stats import MonthViewWindow
        MonthViewWindow(self.root, note_store)

    # ============================================================
    #  ASCII Art Gallery
    # ============================================================
    def show_ascii_gallery(self):
        from features.ascii_art import AsciiGallery
        gallery = AsciiGallery(self.root)
        result  = gallery.run()
        if result:
            # Inject on its own fresh line: only add a leading newline
            # when the cursor is not already at the start of a line.
            cur = self.editor.index("insert")
            if not self.editor.compare(cur, "==",
                                       self.editor.index(f"{cur} linestart")):
                prefix = "\n"
            else:
                prefix = ""
            self.editor.insert("insert", f"{prefix}{result}\n", "mono")
            self._mark_modified()
            achiev_store.unlock("ASCII_ARTIST")
            player_store.add_xp(XP_ASCII_CREATE)
            player_store.save()
            achiev_store.save()

    # ============================================================
    #  Templates
    # ============================================================
    def show_templates(self):
        from features.templates import TemplatesWindow
        result = TemplatesWindow(self.root, template_store).run()
        if result:
            if self.is_modified:
                if not messagebox.askyesno(APP_NAME,
                    "Replace current content with template?"):
                    return
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", result["content"])
            if result.get("tags"):
                self.tags_entry.delete(0, "end")
                self.tags_entry.insert(0, result["tags"])
                self.tags_entry.configure(fg=theme.fg)
            self._mark_modified()
            achiev_store.unlock("TEMPLATE_USER")
            player_store.add_xp(XP_TEMPLATE_USE)
            player_store.save()
            achiev_store.save()

    # ============================================================
    #  Screensaver
    # ============================================================
    def run_screensaver(self):
        from features.screensaver import run_screensaver
        run_screensaver(self.root)

    # ============================================================
    #  Export
    # ============================================================
    def export_plain(self):
        from features.export import export_plain_text
        export_plain_text(self.root, note_store)

    def export_encrypted(self):
        from features.export import export_encrypted
        export_encrypted(self.root, note_store)

    def annual_review(self):
        from features.export import export_annual_review
        export_annual_review(self.root, note_store)

    # ============================================================
    #  Settings
    # ============================================================
    def show_settings(self):
        from features.settings import SettingsWindow
        from features.export import import_v2
        SettingsWindow(
            self.root, player_store, self._apply_settings,
            import_cb=lambda: import_v2(self.root, note_store))

    def _apply_settings(self, new_theme: str, new_lang: str,
                         new_rtl: bool, auto_save: int,
                         show_quote: bool, show_lastyear: bool):
        player = player_store.player
        if new_theme != player.theme:
            player.theme = new_theme
            theme.set(new_theme)
            # Full re-style would require re-building UI;
            # for now update key colors and prompt restart
            messagebox.showinfo(APP_NAME,
                "Theme will fully apply on next launch.")
        if new_lang != player.ui_language:
            player.ui_language = new_lang
            lang.set(new_lang)
        player.default_rtl      = new_rtl
        player.auto_save_secs   = auto_save
        player.show_daily_quote = show_quote
        player.show_last_year   = show_lastyear
        player_store.save()
        self._update_sidebar_labels()
        self._start_autosave()

    # ============================================================
    #  About
    # ============================================================
    def show_about(self):
        from features.about import AboutWindow
        AboutWindow(self.root, self._app_logo_image)
        

    # ============================================================
    #  Close
    # ============================================================
    def _on_close(self):
        if self.is_modified:
            if not messagebox.askyesno(APP_NAME, lang("confirm_quit")):
                return
        # Save and backup
        player_store.save()
        note_store.backup()
        play_quit()
        self.root.after(800, self.root.destroy)

    # ============================================================
    #  Run
    # ============================================================
    def run(self):
        self.root.mainloop()


# ================================================================
#  Entry point
# ================================================================
if __name__ == "__main__":
    app = App()
    app.run()
