# ================================================================
#  NOBARO v1  —  features/settings.py
#  Settings window: theme, language, RTL, auto-save, password,
#  daily-quote toggle, last-year toggle, v2 import.
#  Calls back into app via on_apply() so the app can react.
# ================================================================

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Callable

from core.constants import THEME_NAMES, APP_NAME
from core.data import PlayerStore
from core.utils import hash_password
from ui.theme import theme
from assets.lang import lang, STRINGS
from assets.sounds import play_password_ok, play_password_fail


def _qb_btn(parent, text, command=None, fg=None):
    return tk.Button(
        parent, text=text, command=command,
        bg=theme.bg_btn,
        fg=fg or theme.fg,
        activebackground=theme.bg_btn_sel,
        activeforeground=theme.accent,
        font=theme.font_normal(10),
        relief="flat", bd=1,
        padx=8, pady=3,
        cursor="hand2")


def _row(parent, label: str, row: int):
    """Add a label in column 0, return a frame for column 1."""
    tk.Label(parent, text=label,
             bg=theme.bg, fg=theme.fg_dim,
             font=theme.font_normal(10),
             anchor="w").grid(row=row, column=0,
                              sticky="w", padx=(8, 4), pady=5)
    frame = tk.Frame(parent, bg=theme.bg)
    frame.grid(row=row, column=1, sticky="w", padx=(0, 8), pady=5)
    return frame


class SettingsWindow:
    """
    on_apply signature:
        on_apply(new_theme, new_lang, new_rtl, auto_save_secs,
                 show_quote, show_last_year)
    """
    def __init__(self,
                 parent: tk.Widget,
                 player_store: PlayerStore,
                 on_apply: Callable,
                 import_cb: Callable = None):
        self.ps        = player_store
        self.on_apply  = on_apply
        self.import_cb = import_cb
        self._build(parent)

    def _build(self, parent):
        win = tk.Toplevel(parent)
        win.title(lang("settings"))
        win.configure(bg=theme.bg)
        win.geometry("500x480")
        win.resizable(False, False)
        try:
            win.transient(parent)
            win.grab_set()
        except Exception:
            pass

        p = self.ps.player

        # ---- Header ------------------------------------------
        tk.Label(win, text=lang("settings"),
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(13)).pack(pady=(12, 4))
        tk.Frame(win, bg=theme.border, height=1).pack(fill="x",
                                                       padx=12)

        # ---- Grid of options ---------------------------------
        grid = tk.Frame(win, bg=theme.bg)
        grid.pack(fill="both", expand=True, padx=8, pady=8)
        grid.columnconfigure(1, weight=1)

        # Theme
        f = _row(grid, lang("change_theme") + ":", 0)
        theme_var = tk.StringVar(value=p.theme)
        theme_menu = tk.OptionMenu(f, theme_var, *THEME_NAMES)
        theme_menu.configure(
            bg=theme.bg_btn, fg=theme.fg,
            activebackground=theme.bg_btn_sel,
            activeforeground=theme.accent,
            font=theme.font_normal(10),
            relief="flat", bd=0,
            highlightthickness=0, width=20)
        theme_menu["menu"].configure(
            bg=theme.bg_edit, fg=theme.fg,
            font=theme.font_normal(10))
        theme_menu.pack(side="left")

        # Language
        f = _row(grid, "UI Language:", 1)
        lang_names = {"en": "English", "fa": "فارسی (Farsi)"}
        lang_var   = tk.StringVar(value=lang_names.get(p.ui_language, "en"))
        lang_menu  = tk.OptionMenu(f, lang_var,
                                   *lang_names.values())
        lang_menu.configure(
            bg=theme.bg_btn, fg=theme.fg,
            activebackground=theme.bg_btn_sel,
            activeforeground=theme.accent,
            font=theme.font_normal(10),
            relief="flat", bd=0,
            highlightthickness=0, width=20)
        lang_menu["menu"].configure(
            bg=theme.bg_edit, fg=theme.fg,
            font=theme.font_normal(10))
        lang_menu.pack(side="left")

        # Default RTL
        f = _row(grid, "Default text direction:", 2)
        rtl_var = tk.BooleanVar(value=p.default_rtl)
        tk.Radiobutton(f, text="LTR", variable=rtl_var, value=False,
                       bg=theme.bg, fg=theme.fg,
                       selectcolor=theme.bg_btn_sel,
                       activebackground=theme.bg,
                       font=theme.font_normal(10)).pack(side="left", padx=4)
        tk.Radiobutton(f, text="RTL", variable=rtl_var, value=True,
                       bg=theme.bg, fg=theme.fg,
                       selectcolor=theme.bg_btn_sel,
                       activebackground=theme.bg,
                       font=theme.font_normal(10)).pack(side="left", padx=4)

        # Auto-save
        f = _row(grid, lang("auto_save"), 3)
        autosave_var = tk.StringVar(value=str(p.auto_save_secs))
        e = tk.Entry(f, textvariable=autosave_var, width=6,
                     bg=theme.bg_edit, fg=theme.fg,
                     insertbackground=theme.accent,
                     font=theme.font_normal(10),
                     relief="flat", bd=2)
        e.pack(side="left")
        tk.Label(f, text="seconds (0 = off)",
                 bg=theme.bg, fg=theme.fg_dim,
                 font=theme.font_normal(9)).pack(side="left", padx=6)

        # Daily quote
        f = _row(grid, lang("daily_quote") + ":", 4)
        quote_var = tk.BooleanVar(value=p.show_daily_quote)
        tk.Checkbutton(f, text="Show in sidebar",
                       variable=quote_var,
                       bg=theme.bg, fg=theme.fg,
                       selectcolor=theme.bg_btn_sel,
                       activebackground=theme.bg,
                       font=theme.font_normal(10)).pack(side="left")

        # Last year notification
        f = _row(grid, "'This day last year':", 5)
        lastyear_var = tk.BooleanVar(value=p.show_last_year)
        tk.Checkbutton(f, text="Show at startup",
                       variable=lastyear_var,
                       bg=theme.bg, fg=theme.fg,
                       selectcolor=theme.bg_btn_sel,
                       activebackground=theme.bg,
                       font=theme.font_normal(10)).pack(side="left")

        # ---- Password section ---------------------------------
        tk.Frame(win, bg=theme.border, height=1).pack(fill="x",
                                                       padx=12, pady=4)
        pwd_frame = tk.Frame(win, bg=theme.bg)
        pwd_frame.pack(fill="x", padx=12)

        tk.Label(pwd_frame, text="App Password",
                 bg=theme.bg, fg=theme.fg_dim,
                 font=theme.font_normal(9)).pack(side="left")

        def set_password():
            pw1 = simpledialog.askstring(
                lang("settings"), "New password (blank to remove):",
                show="*", parent=win)
            if pw1 is None:
                return
            if pw1 == "":
                p.has_password  = False
                p.password_hash = 0
                messagebox.showinfo(lang("settings"),
                    "Password removed.", parent=win)
                return
            pw2 = simpledialog.askstring(
                lang("settings"), "Confirm password:",
                show="*", parent=win)
            if pw1 != pw2:
                play_password_fail()
                messagebox.showerror(lang("settings"),
                    "Passwords do not match.", parent=win)
                return
            p.has_password  = True
            p.password_hash = hash_password(pw1)
            play_password_ok()
            messagebox.showinfo(lang("settings"),
                lang("password_set"), parent=win)

        _qb_btn(pwd_frame, lang("set_password"),
                set_password).pack(side="right")

        # v2 import
        tk.Frame(win, bg=theme.border, height=1).pack(fill="x",
                                                       padx=12, pady=4)
        imp_frame = tk.Frame(win, bg=theme.bg)
        imp_frame.pack(fill="x", padx=12)
        tk.Label(imp_frame, text="Import from v2:",
                 bg=theme.bg, fg=theme.fg_dim,
                 font=theme.font_normal(9)).pack(side="left")

        def do_import():
            # Trigger import — main app handles note_store
            win.destroy()
            if self.import_cb:
                self.import_cb()
            else:
                messagebox.showinfo(
                    lang("settings"),
                    "Import is not available in this build.",
                    parent=win)

        _qb_btn(imp_frame, lang("import_v2"),
                do_import).pack(side="right")

        # ---- Save & Close ------------------------------------
        tk.Frame(win, bg=theme.border, height=1).pack(fill="x",
                                                       padx=12, pady=4)
        btn_frame = tk.Frame(win, bg=theme.bg, pady=6)
        btn_frame.pack(fill="x", padx=12)

        def apply_and_close():
            # Parse language choice back to code
            lang_code_map = {v: k for k, v in
                             {"en": "English", "fa": "فارسی (Farsi)"}.items()}
            new_lang = lang_code_map.get(lang_var.get(), "en")

            try:
                auto_secs = max(0, int(autosave_var.get()))
            except ValueError:
                auto_secs = 120

            self.on_apply(
                theme_var.get(),
                new_lang,
                rtl_var.get(),
                auto_secs,
                quote_var.get(),
                lastyear_var.get(),
            )
            win.destroy()

        _qb_btn(btn_frame, lang("save_close"),
                apply_and_close,
                fg=theme.accent).pack(side="right", padx=4)
        _qb_btn(btn_frame, lang("cancel"),
                win.destroy).pack(side="right")


def check_password(player_store: PlayerStore,
                   parent: tk.Widget) -> bool:
    """
    Returns True if no password is set, or the entered password is correct.
    Shows a password dialog and plays a sound.
    """
    p = player_store.player
    if not p.has_password:
        return True
    pw = simpledialog.askstring(
        APP_NAME, lang("password_prompt"),
        show="*", parent=parent)
    if not pw:
        return False
    if hash_password(pw) == p.password_hash:
        play_password_ok()
        return True
    play_password_fail()
    messagebox.showerror(APP_NAME, lang("password_wrong"),
                         parent=parent)
    return False
