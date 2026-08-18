# ================================================================
#  NOBARO v1  —  features/stats.py
#  Stats windows: Overview, Calendar, Mood Graph, Word Freq,
#  Month View.  All drawn on tk.Canvas with QBasic colors.
# ================================================================

import tkinter as tk
from tkinter import messagebox
import datetime
import re

from core.constants import MOOD_COLORS, MOODS, DAILY_QUOTES
from core.utils import (
    friendly_date, month_name, short_month, day_of_week_iso,
    days_in_month, add_days, today, daily_quote,
)
from core.data import NoteStore, PlayerStore, AchievementStore
from core.player_logic import get_level_name, xp_for_next_level
from ui.theme import theme
from assets.lang import lang


# ---- Shared helpers ------------------------------------------

def qb_win(parent, title, w=720, h=520):
    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=theme.bg)
    win.geometry(f"{w}x{h}")
    win.resizable(True, True)
    try:
        win.transient(parent)
        win.grab_set()
    except Exception:
        pass
    return win


def qb_btn(parent, text, command=None):
    return tk.Button(
        parent, text=text, command=command,
        bg=theme.bg_btn, fg=theme.fg,
        activebackground=theme.bg_btn_sel,
        activeforeground=theme.accent,
        font=theme.font_normal(10),
        relief="flat", bd=1, padx=6, pady=2,
        cursor="hand2")


def draw_text(canvas, x, y, text, fill, anchor="nw",
              font=None, size=10, bold=False):
    f = font or (theme.font, size, "bold" if bold else "")
    canvas.create_text(x, y, text=text, fill=fill,
                       anchor=anchor, font=f)


# ================================================================
#  Stats Overview Window
# ================================================================
class StatsWindow:
    def __init__(self, parent, note_store: NoteStore,
                 player_store: PlayerStore,
                 achiev_store: AchievementStore):
        self.ns = note_store
        self.ps = player_store
        self.ac = achiev_store
        self.win = qb_win(parent, lang("stats"), 760, 540)
        self._build()

    def _build(self):
        win = self.win
        # Tab selector (simple buttons at top)
        tab_frame = tk.Frame(win, bg=theme.bg_header, pady=4)
        tab_frame.pack(fill="x")

        self.canvas = tk.Canvas(win, bg=theme.bg,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=4)

        tabs = [
            ("Overview",     self._draw_overview),
            ("Achievements", self._draw_achievements),
        ]
        self._current_tab = 0
        self._tab_fns = [fn for _, fn in tabs]

        for i, (label, fn) in enumerate(tabs):
            b = qb_btn(tab_frame, label,
                       command=lambda i=i: self._switch(i))
            b.pack(side="left", padx=4)

        qb_btn(tab_frame, lang("close"),
               win.destroy).pack(side="right", padx=8)

        win.bind("<Configure>", lambda e: self._redraw())
        self._draw_overview()

    def _switch(self, idx):
        self._current_tab = idx
        self._redraw()

    def _redraw(self):
        self._tab_fns[self._current_tab]()

    def _draw_overview(self):
        c  = self.canvas
        c.delete("all")
        cw = c.winfo_width()  or 700
        ch = c.winfo_height() or 480

        normals     = self.ns.normal_notes()
        total_notes = len(normals)
        total_words = sum(n.word_count for n in normals)
        avg_words   = total_words // total_notes if total_notes else 0
        player      = self.ps.player
        streak      = player.current_streak
        longest     = player.longest_streak
        level       = get_level_name(player.xp)
        xp          = player.xp
        xp_next     = xp_for_next_level(player.xp)

        # Mood counts
        mood_counts = {m[0]: 0 for m in MOODS}
        for n in normals:
            if n.mood in mood_counts:
                mood_counts[n.mood] += 1

        # Longest note
        longest_note = max((n.word_count for n in normals), default=0)
        longest_date = next((n.date for n in normals
                            if n.word_count == longest_note), "")

        y  = 20
        lh = 26
        x1 = 30
        x2 = cw // 2 + 20

        def row(label, value, col=x1, fg=None):
            nonlocal y
            draw_text(c, col, y, label, theme.fg_dim, size=10)
            draw_text(c, col + 200, y, str(value),
                      fg or theme.fg, size=10, bold=True)
            y += lh

        # Left column
        draw_text(c, x1, y, "[ OVERVIEW ]",
                  theme.accent, size=11, bold=True)
        y += lh + 4
        row("Total notes:",    total_notes)
        row("Total words:",    f"{total_words:,}")
        row("Avg words/note:", avg_words)
        row("Current streak:", f"{streak} days",
            fg=theme.accent if streak >= 3 else theme.fg)
        row("Longest streak:", f"{longest} days")
        row("Level:",          level, fg=theme.accent)
        row("XP:",             f"{xp} / {xp_next}")
        if longest_date:
            row("Longest note:", f"{longest_note} words on {friendly_date(longest_date)}")

        # Right column — mood bar chart
        y2 = 20
        draw_text(c, x2, y2, "[ MOOD BREAKDOWN ]",
                  theme.accent, size=11, bold=True)
        y2 += lh + 4

        bar_max_w = min(200, cw - x2 - 80)
        for symbol, name, color in MOODS:
            count = mood_counts.get(symbol, 0)
            pct   = count * 100 // total_notes if total_notes else 0
            bar_w = bar_max_w * count // max(1, max(mood_counts.values()))
            # Bar
            c.create_rectangle(x2, y2 + 4, x2 + bar_w, y2 + lh - 4,
                                fill=color, outline="")
            draw_text(c, x2 + bar_w + 6, y2,
                      f"{name}: {count} ({pct}%)",
                      color, size=9)
            y2 += lh

        # XP progress bar
        y2 += 10
        draw_text(c, x2, y2, "XP Progress", theme.fg_dim, size=9)
        y2 += 18
        bar_w2 = min(200, cw - x2 - 40)
        c.create_rectangle(x2, y2, x2 + bar_w2, y2 + 12,
                           fill=theme.bg_btn, outline=theme.border)
        fill_w = int(bar_w2 * min(xp, xp_next) / max(1, xp_next))
        c.create_rectangle(x2, y2, x2 + fill_w, y2 + 12,
                           fill=theme.accent, outline="")
        draw_text(c, x2, y2 + 16,
                  f"{xp}/{xp_next} → {level}",
                  theme.fg_dim, size=9)

    def _draw_achievements(self):
        c  = self.canvas
        c.delete("all")
        cw = c.winfo_width()  or 700
        y  = 16
        lh = 22

        from core.data import Achievement
        draw_text(c, 20, y, "[ ACHIEVEMENTS ]",
                  theme.accent, size=11, bold=True)
        y += lh + 8

        unlocked_count = 0
        total          = len(self.ac.achievements)
        for a in self.ac.achievements:
            if a.unlocked:
                col  = theme.accent
                name = a.display_name()
                date = f"  {a.unlocked_date}"
                unlocked_count += 1
            else:
                col  = theme.fg_dim
                name = "[ ] ???"
                date = ""
            draw_text(c, 20, y, name, col, size=10)
            if date:
                draw_text(c, cw - 100, y, date, theme.fg_dim, size=9)
            y += lh
            if y > c.winfo_height() - 30:
                break

        y = c.winfo_height() - 20
        draw_text(c, 20, y,
                  f"Unlocked: {unlocked_count} / {total}",
                  theme.fg_dim, size=9)


# ================================================================
#  Calendar Window
# ================================================================
class CalendarWindow:
    def __init__(self, parent, note_store: NoteStore):
        self.ns  = note_store
        self.win = qb_win(parent, lang("calendar"), 540, 460)
        t = datetime.date.today()
        self.year  = t.year
        self.month = t.month
        self._build()

    def _build(self):
        win = self.win
        nav = tk.Frame(win, bg=theme.bg, pady=4)
        nav.pack(fill="x")
        qb_btn(nav, lang("prev"),    self._prev).pack(side="left",  padx=8)
        qb_btn(nav, lang("next"),    self._next).pack(side="right", padx=8)
        qb_btn(nav, lang("close"), win.destroy).pack(side="right", padx=4)

        self.canvas = tk.Canvas(win, bg=theme.bg,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        win.bind("<Configure>", lambda e: self._draw())
        self._draw()

    def _prev(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12; self.year -= 1
        self._draw()

    def _next(self):
        self.month += 1
        if self.month > 12:
            self.month = 1; self.year += 1
        self._draw()

    def _draw(self):
        c  = self.canvas
        c.delete("all")
        cw = c.winfo_width()  or 500
        ch = c.winfo_height() or 400

        cell_w = (cw - 20) // 7
        cell_h = max(20, (ch - 60) // 7)
        start  = day_of_week_iso(self.year, self.month, 1)
        days   = days_in_month(self.year, self.month)
        t_str  = today()
        date_mood = {n.date: n.mood
                     for n in self.ns.normal_notes()}

        # Month/year heading
        draw_text(c, 10, 6,
                  f"{month_name(self.month)} {self.year}",
                  theme.accent, size=12, bold=True)

        # Day-of-week headers
        dow = ["Mo","Tu","We","Th","Fr","Sa","Su"]
        for i, d in enumerate(dow):
            draw_text(c, 10 + i * cell_w + cell_w//2, 28,
                      d, theme.fg_dim, anchor="n", size=9)

        # Day cells
        day = 1
        row_ = 0
        col_ = start
        while day <= days:
            cx = 10 + col_ * cell_w
            cy = 48 + row_ * cell_h
            ds = f"{self.year:04d}-{self.month:02d}-{day:02d}"
            mood = date_mood.get(ds, "")

            # Cell background (mood-colored)
            if mood:
                col_hex = MOOD_COLORS.get(mood, theme.fg_dim)
                # darken by mixing with bg
                c.create_rectangle(cx, cy,
                                   cx + cell_w - 2, cy + cell_h - 2,
                                   fill=theme.bg_btn, outline="")
                c.create_rectangle(cx, cy + cell_h - 4,
                                   cx + cell_w - 2, cy + cell_h - 2,
                                   fill=col_hex, outline="")

            # Today outline
            if ds == t_str:
                c.create_rectangle(cx, cy,
                                   cx + cell_w - 2, cy + cell_h - 2,
                                   outline=theme.accent, width=2, fill="")

            # Day number
            fg = MOOD_COLORS.get(mood, theme.fg_dim) if mood else theme.fg_dim
            draw_text(c, cx + 3, cy + 2, str(day), fg, size=9)
            if mood:
                draw_text(c, cx + 3, cy + 14, mood, fg, size=8)

            col_ += 1
            if col_ > 6:
                col_ = 0; row_ += 1
            day += 1


# ================================================================
#  Mood Graph Window
# ================================================================
class MoodGraphWindow:
    def __init__(self, parent, note_store: NoteStore):
        self.ns  = note_store
        self.win = qb_win(parent, lang("mood_graph"), 760, 420)
        self._build()

    def _build(self):
        win = self.win
        tk.Label(win, text=lang("mood_graph"),
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(11)).pack(pady=4)
        self.canvas = tk.Canvas(win, bg=theme.bg,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=4)
        qb_btn(win, lang("close"), win.destroy).pack(pady=4)
        win.bind("<Configure>", lambda e: self._draw())
        self._draw()

    def _draw(self):
        c  = self.canvas
        c.delete("all")
        cw = c.winfo_width()  or 720
        ch = c.winfo_height() or 340
        days  = 60
        pad_l = 36
        pad_b = 30
        pad_t = 20

        slot_w   = max(2, (cw - pad_l - 10) // days)
        bar_maxh = ch - pad_b - pad_t
        t        = datetime.date.today()
        date_mood = {n.date: n.mood
                     for n in self.ns.normal_notes()}

        mood_val = {":D": 1.0, ":)": 0.8, ":|": 0.5,
                    ":(": 0.25, ";(": 0.1}

        # Grid lines
        for i in range(5):
            gy = pad_t + i * bar_maxh // 4
            c.create_line(pad_l, gy, cw - 10, gy,
                          fill=theme.bg_btn, dash=(2, 4))

        # Y-axis labels
        for label, frac in [(":D", 0.0), (":|", 0.5), (";(", 1.0)]:
            gy = pad_t + int(frac * bar_maxh)
            draw_text(c, 2, gy - 7, label, theme.fg_dim, size=8)

        # Bars
        for i in range(days):
            ds   = (t - datetime.timedelta(days=days-1-i)).isoformat()
            mood = date_mood.get(ds, "")
            bx   = pad_l + i * slot_w
            if mood:
                val  = mood_val.get(mood, 0.5)
                bh   = int(bar_maxh * val)
                col  = MOOD_COLORS.get(mood, theme.fg_dim)
                c.create_rectangle(bx, pad_t + bar_maxh - bh,
                                   bx + slot_w - 1, pad_t + bar_maxh,
                                   fill=col, outline="")
            else:
                c.create_rectangle(bx, pad_t + bar_maxh - 2,
                                   bx + slot_w - 1, pad_t + bar_maxh,
                                   fill=theme.bg_btn, outline="")

        # X-axis date labels
        oldest = (t - datetime.timedelta(days=days-1)).strftime("%b %d")
        newest = t.strftime("%b %d")
        draw_text(c, pad_l, ch - 18, oldest, theme.fg_dim, size=8)
        draw_text(c, cw - 60, ch - 18, newest, theme.fg_dim, size=8)

        # Today marker
        c.create_line(cw - slot_w - 10, pad_t,
                      cw - slot_w - 10, pad_t + bar_maxh,
                      fill=theme.accent, width=1, dash=(3, 3))

        draw_text(c, cw // 2 - 80, 4,
                  "Mood Graph — Last 60 Days",
                  theme.accent, size=10, bold=True)


# ================================================================
#  Word Frequency Window
# ================================================================
class WordFreqWindow:
    def __init__(self, parent, note_store: NoteStore):
        self.ns  = note_store
        self.win = qb_win(parent, lang("word_freq"), 640, 460)
        self._build()

    def _build(self):
        win = self.win
        tk.Label(win, text="Top Words You Use",
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(11)).pack(pady=4)
        self.canvas = tk.Canvas(win, bg=theme.bg,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=4)
        qb_btn(win, lang("close"), win.destroy).pack(pady=4)
        win.bind("<Configure>", lambda e: self._draw())
        self._draw()

    def _count_words(self):
        STOPS = {
            "i","a","the","and","to","of","in","is","it","was","that",
            "my","me","he","she","we","you","they","this","on","at","for",
            "with","are","be","as","had","so","but","not","or","an","his",
            "her","have","has","do","did","from","by","up","if","just",
            "like","one","all","can","get","out","no","its","about","into",
            "then","s","t","re","ve","ll","m","d",
        }
        counts: dict[str, int] = {}
        for note in self.ns.normal_notes():
            for w in re.findall(r"[a-zA-Z]{3,}", note.content.lower()):
                if w not in STOPS:
                    counts[w] = counts.get(w, 0) + 1
        return sorted(counts.items(), key=lambda x: -x[1])[:20]

    def _draw(self):
        c  = self.canvas
        c.delete("all")
        cw = c.winfo_width()  or 600
        ch = c.winfo_height() or 400
        top = self._count_words()
        if not top:
            draw_text(c, cw//2, ch//2,
                      "Write more notes to see your top words!",
                      theme.fg_dim, anchor="center", size=10)
            return
        bar_area = cw - 160
        max_cnt  = top[0][1]
        lh       = max(14, (ch - 20) // max(1, len(top)))

        for i, (word, cnt) in enumerate(top):
            y  = 10 + i * lh
            bw = int(bar_area * cnt / max(1, max_cnt))
            draw_text(c, 4, y,
                      f"{i+1:2d}. {word}", theme.fg, size=9)
            c.create_rectangle(120, y + 2, 120 + bw, y + lh - 2,
                               fill=theme.border, outline="")
            draw_text(c, 124 + bw, y, str(cnt),
                      theme.fg_dim, size=8)


# ================================================================
#  Month View Window — "this month across all years"
# ================================================================
class MonthViewWindow:
    def __init__(self, parent, note_store: NoteStore):
        self.ns  = note_store
        self.win = qb_win(parent, lang("month_view"), 640, 480)
        self._build()

    def _build(self):
        import datetime
        win = self.win
        cur_m = datetime.date.today().month
        tk.Label(win,
                 text=f"{lang('on_this_month')} ({month_name(cur_m)})",
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(11)).pack(pady=6)

        frame = tk.Frame(win, bg=theme.bg)
        frame.pack(fill="both", expand=True, padx=8)

        lb = tk.Listbox(frame, bg=theme.bg_edit, fg=theme.fg,
                        selectbackground=theme.select_bg,
                        selectforeground=theme.select_fg,
                        font=theme.font_normal(10),
                        relief="flat", bd=0,
                        activestyle="none")
        lb.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(frame, bg=theme.bg_btn,
                          troughcolor=theme.bg,
                          relief="flat", width=10)
        sb.pack(side="right", fill="y")
        lb.configure(yscrollcommand=sb.set)
        sb.configure(command=lb.yview)

        notes = sorted([n for n in self.ns.normal_notes()
                        if int(n.date[5:7]) == cur_m],
                       key=lambda n: n.date, reverse=True)
        for n in notes:
            preview = n.content[:55].replace("\n", " ")
            lb.insert("end",
                      f"{friendly_date(n.date)}  {n.mood}  {preview}")
            lb.itemconfigure(lb.size()-1,
                foreground=MOOD_COLORS.get(n.mood, theme.fg))

        self._notes = notes
        self._lb    = lb

        btn_frame = tk.Frame(win, bg=theme.bg)
        btn_frame.pack(pady=4)

        def open_sel():
            sel = lb.curselection()
            if not sel:
                return
            note = notes[sel[0]]
            win.destroy()
            # Bubble up — caller handles load
            self._selected = note

        qb_btn(btn_frame, lang("open_selected"), open_sel).pack(side="left", padx=4)
        qb_btn(btn_frame, lang("close"), win.destroy).pack(side="left", padx=4)

        tk.Label(win,
                 text=f"{len(notes)} note(s) in {month_name(cur_m)} across all years",
                 bg=theme.bg, fg=theme.fg_dim,
                 font=theme.font_normal(9)).pack(pady=2)
