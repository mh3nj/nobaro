# ================================================================
#  NOBARO v1  —  features/screensaver.py
#  QBasic-style animated screensaver.
#  Renders the NOBARO logo with a star-field, scrolling quote,
#  and blinking cursor on a dark blue canvas.
#  Plays the Gorillas.bas melody in the background.
#  Press any key or click to exit.
# ================================================================

import tkinter as tk
import datetime
import random
import time
import threading

from core.constants import DAILY_QUOTES
from core.utils import daily_quote
from ui.theme import theme
from assets.sounds import play_gorilla


LOGO_LINES = [
"  ██████▒▒▒█████         ▒█████                                ",
" ▒██████ ▒▒███           ▒███                                  ",
" ▒███▒███ ▒███   ██████  ▒███████   ██████   ████████   ██████ ",
" ▒███▒▒███▒███  ███▒▒███ ▒███▒▒███ ▒▒▒▒▒███  ▒███▒▒███ ███▒▒███",
" ▒███ ▒▒██████ ▒███ ▒███ ▒███ ▒███  ███████  ▒███     ▒███ ▒███",
" ▒███  ▒▒█████ ▒███ ▒███ ▒███ ▒███ ███▒▒███  ▒███     ▒███ ▒███",
" ▒████  ▒▒████  ▒██████   ███████  ▒███████  ▒███      ▒██████ ",
" ▒▒▒▒▒▒  ▒▒▒▒▒   ▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒   ▒▒▒       ▒▒▒▒▒▒  "
]

GORILLA = (
    "  \\ //\n"
    "  (o o)\n"
    "  ( V )\n"
    " /|   |\\\n"
    "  |   |\n"
    " GORILLAS.BAS 1991\n"
    " 'press any key to return'"
)


def run_screensaver(parent: tk.Tk):
    win = tk.Toplevel(parent)
    win.title("NOBARO — Screensaver")
    win.configure(bg="#0000AA")
    win.geometry("900x560")
    win.resizable(True, True)
    try:
        win.transient(parent)
        win.grab_set()
    except Exception:
        pass

    canvas = tk.Canvas(win, bg="#0000AA", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # State
    tick       = [0]
    quote_x    = [900]
    quote_text = [daily_quote(DAILY_QUOTES)]
    stars      = [(random.randint(0, 900), random.randint(0, 560),
                   random.choice([".", "·", "✦", "+", "°"]))
                  for _ in range(35)]
    running    = [True]

    def close(*_):
        running[0] = False
        win.destroy()

    win.bind("<Key>",    close)
    win.bind("<Button>", close)

    play_gorilla()

    def frame():
        if not running[0]:
            return
        try:
            cw = canvas.winfo_width()  or 900
            ch = canvas.winfo_height() or 560
        except Exception:
            return

        canvas.delete("all")

        # Background
        canvas.create_rectangle(0, 0, cw, ch, fill="#0000AA", outline="")

        # Star field
        t  = tick[0]
        for sx, sy, sc in stars:
            # Twinkle every ~20 frames
            col = "#FFFFFF" if (t + sx) % 20 < 10 else "#5555FF"
            canvas.create_text(sx % cw, sy % ch,
                               text=sc, fill=col,
                               font=("Courier New", 8))

        # Logo (animated brightness)
        brightness = 160 + int(40 * abs((t % 60) / 30 - 1))
        logo_col   = f"#{0:02X}{brightness:02X}{brightness:02X}"
        logo_y     = ch // 2 - 80
        for i, line in enumerate(LOGO_LINES):
            canvas.create_text(cw // 2, logo_y + i * 16,
                               text=line, fill=logo_col,
                               font=("Courier New", 9),
                               anchor="center")

        # Gorilla ASCII art (bottom-right, dim)
        gorilla_lines = GORILLA.split("\n")
        for i, gl in enumerate(gorilla_lines):
            canvas.create_text(cw - 170, ch - 140 + i * 14,
                               text=gl, fill="#0055AA",
                               font=("Courier New", 9),
                               anchor="w")

        # Scrolling quote
        quote_x[0] -= 2
        if quote_x[0] < -800:
            quote_x[0] = cw + 20
            quote_text[0] = daily_quote(DAILY_QUOTES)
        canvas.create_text(quote_x[0], ch - 30,
                           text=f'"{quote_text[0]}"',
                           fill="#55FFFF",
                           font=("Courier New", 10),
                           anchor="w")

        # Date/time
        now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        canvas.create_text(cw - 10, 10,
                           text=now, fill="#55FFFF",
                           font=("Courier New", 9),
                           anchor="ne")

        # Blinking cursor
        if t % 20 < 10:
            canvas.create_text(40, ch - 30,
                               text="_", fill="#FFFF55",
                               font=("Courier New", 12),
                               anchor="w")

        # Tagline
        canvas.create_text(cw // 2, logo_y + len(LOGO_LINES) * 16 + 12,
                           text="Your Digital Soul  •  No internet required.",
                           fill="#0088AA",
                           font=("Courier New", 9),
                           anchor="center")

        tick[0] += 1

        if running[0]:
            try:
                win.after(33, frame)   # ~30 fps
            except Exception:
                pass

    win.after(50, frame)
    win.focus_set()
    win.wait_window()
