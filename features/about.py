# ================================================================
#  NOBARO v1  —  features/about.py
#  About window: branded logo, version, credits and links.
# ================================================================

import tkinter as tk

from core.constants import APP_NAME, APP_VERSION, APP_TAGLINE
from ui.theme import theme
from assets.lang import lang


class AboutWindow:
    """
    Shows the NOBARO logo, version, tagline, credits and links.
    logo_loader is a zero-argument callable returning a tk.PhotoImage
    (or None) so the caller controls image lifetime.

    Note: the logo must arrive pre-sized (the caller loads
    public/logo_256.png).  Tk's PhotoImage renders the 6000px source
    logo blank and PhotoImage.subsample() is broken in some Tk builds,
    so we never scale here — we display the image exactly as given.
    """

    def __init__(self, parent: tk.Widget, logo_loader=None):
        self.parent = parent
        win = tk.Toplevel(parent)
        win.title(f"{lang('about')} — {APP_NAME} v{APP_VERSION}")
        win.configure(bg=theme.bg)
        win.resizable(False, False)
        try:
            win.transient(parent)
            win.grab_set()
        except Exception:
            pass

        # ---- Branded logo (pre-sized, shown as-is) ------------
        img = logo_loader() if logo_loader else None
        if img is not None:
            self._logo = img   # keep a reference so it is never GC'd
            tk.Label(win, image=img, bg=theme.bg).pack(pady=(20, 8))

        tk.Label(win,
                 text=f"{APP_NAME} v{APP_VERSION} — {APP_TAGLINE}",
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(14)).pack(pady=(0, 4))

        tk.Label(win,
                 text="A peaceful, offline note engine.\n"
                      "Pure Python + tkinter. No cloud. No ads. No algorithm.",
                 bg=theme.bg, fg=theme.fg,
                 font=theme.font_normal(10),
                 justify="center").pack(pady=(0, 12))

        tk.Frame(win, bg=theme.border, height=1).pack(fill="x", padx=28)

        # ---- Credits ------------------------------------------
        creds = [
            ("Developed by",     "github.com/mh3nj  ·  mh3n.com"),
            ("Logo designed by", "parsegan.com"),
            ("Sponsored by",     "dahgan.com"),
        ]
        for label, value in creds:
            row = tk.Frame(win, bg=theme.bg)
            row.pack(fill="x", padx=32, pady=2)
            tk.Label(row, text=f"{label}:",
                     bg=theme.bg, fg=theme.fg_dim,
                     font=theme.font_normal(10),
                     width=16, anchor="e").pack(side="left")
            tk.Label(row, text=value,
                     bg=theme.bg, fg=theme.fg,
                     font=theme.font_normal(10),
                     anchor="w").pack(side="left", padx=(8, 0))

        tk.Frame(win, bg=theme.border, height=1).pack(fill="x", padx=28)

        tk.Label(win,
                 text="This is a full rebrand and full redesign of the "
                      "original LifeNote —\n"
                      "reborn from PureBasic into pure Python.",
                 bg=theme.bg, fg=theme.fg_dim,
                 font=theme.font_normal(9),
                 justify="center").pack(pady=(12, 4))

        tk.Label(win,
                 text='10 PRINT "you matter"\n20 GOTO 10',
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_normal(11),
                 justify="center").pack(pady=(8, 6))

        tk.Button(win, text=lang("close"), command=win.destroy,
                  bg=theme.bg_btn, fg=theme.fg,
                  activebackground=theme.bg_btn_sel,
                  activeforeground=theme.accent,
                  font=theme.font_normal(10),
                  relief="flat", bd=1, padx=18, pady=4,
                  cursor="hand2").pack(pady=(2, 16))

        # ---- Size & position ----------------------------------
        win.update_idletasks()
        width  = min(win.winfo_reqwidth(), 520)
        height = win.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 3
        win.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")
