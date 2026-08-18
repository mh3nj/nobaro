# ================================================================
#  NOBARO v1  —  ui/theme.py
#  Active theme singleton.  Provides color/font helpers and
#  a single apply() call that re-styles every registered widget.
# ================================================================

from core.constants import THEMES, THEME_NAMES


class Theme:
    """Singleton that holds the currently active theme."""

    def __init__(self, name: str = "QBasic Classic"):
        self._name = name if name in THEMES else THEME_NAMES[0]
        self._t    = THEMES[self._name]

    # ---- Switch theme ----------------------------------------
    def set(self, name: str):
        self._name = name if name in THEMES else THEME_NAMES[0]
        self._t    = THEMES[self._name]

    def cycle(self):
        idx = THEME_NAMES.index(self._name)
        self.set(THEME_NAMES[(idx + 1) % len(THEME_NAMES)])

    # ---- Color accessors ------------------------------------
    @property
    def bg(self)         -> str: return self._t["bg"]
    @property
    def bg_edit(self)    -> str: return self._t["bg_edit"]
    @property
    def bg_header(self)  -> str: return self._t["bg_header"]
    @property
    def bg_btn(self)     -> str: return self._t["bg_btn"]
    @property
    def bg_btn_sel(self) -> str: return self._t["bg_btn_sel"]
    @property
    def fg(self)         -> str: return self._t["fg"]
    @property
    def fg_dim(self)     -> str: return self._t["fg_dim"]
    @property
    def accent(self)     -> str: return self._t["accent"]
    @property
    def border(self)     -> str: return self._t["border"]
    @property
    def select_bg(self)  -> str: return self._t["select_bg"]
    @property
    def select_fg(self)  -> str: return self._t["select_fg"]
    @property
    def font(self)       -> str: return self._t["font"]
    @property
    def name(self)       -> str: return self._name

    # ---- Font tuples for tkinter ----------------------------
    def font_normal(self, size: int = 11) -> tuple:
        return (self.font, size)

    def font_bold(self, size: int = 11) -> tuple:
        return (self.font, size, "bold")

    def font_italic(self, size: int = 11) -> tuple:
        return (self.font, size, "italic")

    def font_bold_italic(self, size: int = 11) -> tuple:
        return (self.font, size, "bold italic")

    # ---- Mood color -----------------------------------------
    def mood_color(self, mood: str) -> str:
        from core.constants import MOOD_COLORS
        return MOOD_COLORS.get(mood, self.fg_dim)

    # ---- Widget styling helpers -----------------------------
    def style_frame(self, widget, bg: str = None):
        widget.configure(bg=bg or self.bg)

    def style_label(self, widget, fg: str = None, bg: str = None,
                    size: int = 11, bold: bool = False):
        widget.configure(
            bg=bg or self.bg,
            fg=fg or self.fg,
            font=self.font_bold(size) if bold else self.font_normal(size),
        )

    def style_button(self, widget, fg: str = None, bg: str = None,
                     size: int = 10, selected: bool = False):
        widget.configure(
            bg=bg or (self.bg_btn_sel if selected else self.bg_btn),
            fg=fg or (self.accent if selected else self.fg),
            activebackground=self.bg_btn_sel,
            activeforeground=self.accent,
            relief="flat",
            bd=0,
            font=self.font_normal(size),
            cursor="hand2",
        )

    def style_entry(self, widget, size: int = 11):
        widget.configure(
            bg=self.bg_edit,
            fg=self.fg,
            insertbackground=self.accent,
            selectbackground=self.select_bg,
            selectforeground=self.select_fg,
            font=self.font_normal(size),
            relief="flat",
            bd=2,
        )

    def style_text(self, widget, size: int = 11):
        widget.configure(
            bg=self.bg_edit,
            fg=self.fg,
            insertbackground=self.accent,
            selectbackground=self.select_bg,
            selectforeground=self.select_fg,
            font=self.font_normal(size),
            relief="flat",
            bd=0,
        )

    def style_listbox(self, widget, size: int = 10):
        widget.configure(
            bg=self.bg_edit,
            fg=self.fg,
            selectbackground=self.select_bg,
            selectforeground=self.select_fg,
            font=self.font_normal(size),
            relief="flat",
            bd=0,
            activestyle="none",
        )

    def style_canvas(self, widget):
        widget.configure(bg=self.bg, highlightthickness=0)

    def style_scrollbar(self, widget):
        widget.configure(
            bg=self.bg_btn,
            troughcolor=self.bg,
            activebackground=self.accent,
            relief="flat",
            bd=0,
            width=10,
        )

    def style_combobox_frame(self, frame, listbox, entry_var, entry_widget):
        """Style a hand-rolled combobox."""
        self.style_frame(frame)
        self.style_entry(entry_widget)
        self.style_listbox(listbox)

    # ---- Text widget tag configuration ----------------------
    def apply_editor_tags(self, text_widget, base_size: int = 11):
        """Configure all rich-text formatting tags on a tk.Text widget."""
        fn = self.font
        # Character formatting
        text_widget.tag_configure("bold",
            font=(fn, base_size, "bold"))
        text_widget.tag_configure("italic",
            font=(fn, base_size, "italic"))
        text_widget.tag_configure("bold_italic",
            font=(fn, base_size, "bold italic"))
        text_widget.tag_configure("underline",
            underline=True)
        text_widget.tag_configure("strikethrough",
            overstrike=True)

        # Headings
        text_widget.tag_configure("h1",
            font=(fn, 28, "bold"), foreground=self.accent)
        text_widget.tag_configure("h2",
            font=(fn, 22, "bold"), foreground=self.fg)
        text_widget.tag_configure("h3",
            font=(fn, 16, "bold"), foreground=self.fg_dim)

        # Alignment (tkinter justify applies per-paragraph)
        text_widget.tag_configure("align_left",   justify="left")
        text_widget.tag_configure("align_center", justify="center")
        text_widget.tag_configure("align_right",  justify="right")

        # Highlight presets
        text_widget.tag_configure("hl_yellow",  background="#FFFF00",
                                                foreground="#000000")
        text_widget.tag_configure("hl_cyan",    background="#00FFFF",
                                                foreground="#000000")
        text_widget.tag_configure("hl_green",   background="#00FF00",
                                                foreground="#000000")
        text_widget.tag_configure("hl_magenta", background="#FF00FF",
                                                foreground="#000000")

        # Foreground color presets
        text_widget.tag_configure("col_accent",  foreground=self.accent)
        text_widget.tag_configure("col_fg",      foreground=self.fg)
        text_widget.tag_configure("col_dim",     foreground=self.fg_dim)
        text_widget.tag_configure("col_red",     foreground="#FF5555")
        text_widget.tag_configure("col_green",   foreground="#55FF55")
        text_widget.tag_configure("col_white",   foreground="#FFFFFF")

        # Monospace block (for ASCII art)
        text_widget.tag_configure("mono",
            font=("Courier New", base_size - 1))

        # Media tag (inline file reference)
        text_widget.tag_configure("media_tag",
            foreground=self.border, underline=True)

        # Selection override so our colors show
        text_widget.tag_configure("sel",
            background=self.select_bg,
            foreground=self.select_fg)

    def all_text_tags(self) -> list:
        """All tag names we define — useful for 'remove all formatting'."""
        return [
            "bold", "italic", "bold_italic", "underline", "strikethrough",
            "h1", "h2", "h3",
            "align_left", "align_center", "align_right",
            "hl_yellow", "hl_cyan", "hl_green", "hl_magenta",
            "col_accent", "col_fg", "col_dim", "col_red", "col_green", "col_white",
            "mono", "media_tag",
        ]


# Module-level singleton
theme = Theme("QBasic Classic")
