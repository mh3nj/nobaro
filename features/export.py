# ================================================================
#  NOBARO v1  —  features/export.py
#  Three export modes: plain text, XOR-encrypted (.lne),
#  and annual review.  All pure Python + tkinter file dialogs.
# ================================================================

import os
import sys
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from core.constants import APP_NAME, APP_VERSION, APP_TAGLINE
from core.data import NoteStore
from core.utils import (
    today, now_time, month_name, friendly_date,
    xor_cipher, xor_decipher, hash_password,
)
from assets.lang import lang


# ================================================================
#  Plain text export
# ================================================================
def export_plain_text(parent: tk.Widget, note_store: NoteStore):
    path = filedialog.asksaveasfilename(
        parent=parent,
        title="Export as Plain Text",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if not path:
        return

    normals = sorted(note_store.normal_notes(), key=lambda n: n.date)
    count   = len(normals)

    lines = []
    lines.append("=" * 64)
    lines.append(f"  {APP_NAME} v{APP_VERSION} — {APP_TAGLINE}")
    lines.append(f"  Exported: {today()} at {now_time()}")
    lines.append(f"  Total notes: {count}")
    lines.append("=" * 64)
    lines.append("")

    for note in normals:
        lines.append(f"---[ {note.date} | {note.mood} ]---")
        if note.tags:
            lines.append(f"Tags: {note.tags}")
        lines.append("")
        lines.append(note.content)
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    lines.append(f"[ END — {count} notes exported ]")

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except OSError as e:
        messagebox.showerror(APP_NAME, f"{lang('error_save')}\n{e}",
                             parent=parent)
        return

    messagebox.showinfo(
        APP_NAME,
        f"{count} notes exported to:\n{path}",
        parent=parent)

    _open_file(path)


# ================================================================
#  Encrypted export  (.lne)
# ================================================================
def export_encrypted(parent: tk.Widget, note_store: NoteStore):
    pw1 = simpledialog.askstring(
        APP_NAME, "Encryption password:", show="*", parent=parent)
    if not pw1:
        return
    pw2 = simpledialog.askstring(
        APP_NAME, "Confirm password:", show="*", parent=parent)
    if pw1 != pw2:
        messagebox.showerror(APP_NAME, "Passwords do not match.",
                             parent=parent)
        return

    path = filedialog.asksaveasfilename(
        parent=parent,
        title="Save Encrypted Export",
        defaultextension=".lne",
        filetypes=[("NOBARO Encrypted", "*.lne"),
                   ("All files", "*.*")],
    )
    if not path:
        return

    normals = sorted(note_store.normal_notes(), key=lambda n: n.date)
    count   = len(normals)

    # Build plaintext bundle
    lines = [f"NOBARO_EXPORT_V1|{today()}"]
    for note in normals:
        lines.append("---NOTE---")
        lines.append(note.date)
        lines.append(note.mood)
        lines.append(note.content.replace("\n", "\\n"))
        lines.append(note.tags)
        lines.append("---END---")
    content = "\n".join(lines)

    # Encrypt and write
    pw_hash  = hash_password(pw1)
    ciphered = xor_cipher(content, pw1)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("NOBARO_ENCRYPTED_V1\n")
            f.write(str(pw_hash) + "\n")
            f.write(ciphered)
    except OSError as e:
        messagebox.showerror(APP_NAME, f"{lang('error_save')}\n{e}",
                             parent=parent)
        return

    messagebox.showinfo(
        APP_NAME,
        f"{count} notes encrypted and saved:\n{path}\n\n"
        "Keep your password safe — there is NO recovery.",
        parent=parent)


def decrypt_export(path: str, password: str) -> str | None:
    """Decrypt an .lne file. Returns plaintext or None on wrong password."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            header  = f.readline().strip()
            pw_hash = int(f.readline().strip())
            cipher  = f.read()
    except (OSError, ValueError):
        return None
    if header != "NOBARO_ENCRYPTED_V1":
        return None
    if pw_hash != hash_password(password):
        return None
    return xor_decipher(cipher, password)


# ================================================================
#  Annual Review
# ================================================================
def export_annual_review(parent: tk.Widget, note_store: NoteStore):
    this_year = datetime.date.today().year
    year_str  = simpledialog.askstring(
        APP_NAME,
        "Generate annual review for year:",
        initialvalue=str(this_year - 1),
        parent=parent)
    if not year_str:
        return
    yr = year_str.strip()

    path = filedialog.asksaveasfilename(
        parent=parent,
        title=f"Save Annual Review {yr}",
        defaultextension=".txt",
        initialfile=f"nobaro_review_{yr}.txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if not path:
        return

    # Filter notes to this year
    year_notes = sorted(
        [n for n in note_store.normal_notes()
         if n.date.startswith(yr)],
        key=lambda n: n.date)

    if not year_notes:
        messagebox.showinfo(APP_NAME,
            f"No notes found for {yr}.", parent=parent)
        return

    note_count = len(year_notes)
    word_count = sum(n.word_count for n in year_notes)
    avg_words  = word_count // note_count if note_count else 0

    # Mood breakdown
    from core.constants import MOODS
    mood_counts = {m[0]: 0 for m in MOODS}
    for n in year_notes:
        if n.mood in mood_counts:
            mood_counts[n.mood] += 1

    # Monthly counts
    monthly = {}
    for n in year_notes:
        m = int(n.date[5:7])
        monthly[m] = monthly.get(m, 0) + 1

    # Longest note
    longest = max(year_notes, key=lambda n: n.word_count)

    # Build report
    lines = []
    sep64 = "=" * 64
    sep30 = "-" * 30

    lines += [sep64,
              f"  NOBARO — Annual Review for {yr}",
              sep64, ""]

    lines += ["STATS", sep30,
              f"Total notes:     {note_count}",
              f"Total words:     {word_count:,}",
              f"Avg words/note:  {avg_words}",
              ""]

    lines += ["MOOD BREAKDOWN", sep30]
    mood_names = {m[0]: m[1] for m in MOODS}
    for symbol, name, _ in MOODS:
        cnt = mood_counts.get(symbol, 0)
        pct = cnt * 100 // note_count if note_count else 0
        bar = "*" * min(cnt, 30)
        lines.append(f"{name:<12} {symbol}: {cnt:3d} ({pct:2d}%)  {bar}")
    lines.append("")

    lines += ["ENTRIES BY MONTH", sep30]
    for m in range(1, 13):
        cnt = monthly.get(m, 0)
        bar = "*" * min(cnt, 40)
        lines.append(f"{month_name(m):<12} {cnt:3d}  {bar}")
    lines.append("")

    lines += ["RECORDS", sep30,
              f"Longest note: {longest.word_count} words on "
              f"{friendly_date(longest.date)}",
              ""]

    lines += [sep64,
              "FULL ENTRIES",
              sep64, ""]

    for note in year_notes:
        lines.append(f"[ {note.date} | {note.mood} ]")
        if note.tags:
            lines.append(f"  {note.tags}")
        lines.append(note.content)
        lines.append("-" * 40)
        lines.append("")

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except OSError as e:
        messagebox.showerror(APP_NAME, f"{lang('error_save')}\n{e}",
                             parent=parent)
        return

    messagebox.showinfo(
        APP_NAME,
        f"Annual review for {yr} saved!\n{path}",
        parent=parent)
    _open_file(path)


# ================================================================
#  v2 Import (plain-text NOBARO_NOTES.TXT)
# ================================================================
def import_v2(parent: tk.Widget, note_store: NoteStore) -> int:
    """
    Import notes from old NOBARO_NOTES.TXT format.
    Returns count of notes imported.
    """
    from core.constants import IMPORT_V2_FILE
    if not os.path.isfile(IMPORT_V2_FILE):
        messagebox.showinfo(APP_NAME,
            f"File not found:\n{IMPORT_V2_FILE}", parent=parent)
        return 0

    imported = 0
    try:
        with open(IMPORT_V2_FILE, "r", encoding="utf-8",
                  errors="replace") as f:
            lines = f.read().splitlines()
    except OSError as e:
        messagebox.showerror(APP_NAME, str(e), parent=parent)
        return 0

    i = 0
    from core.data import Note
    from core.utils import generate_note_id, count_words
    existing_dates = {n.date for n in note_store.normal_notes()}

    while i < len(lines) - 6:
        date   = lines[i].strip()
        mood   = lines[i+1].strip()
        text   = lines[i+2].strip()
        tags   = lines[i+3].strip()
        ntype  = lines[i+4].strip()
        sealed = lines[i+5].strip()
        xp_str = lines[i+6].strip() if i+6 < len(lines) else "0"
        i += 7

        if not date or date in existing_dates:
            continue

        note = Note(
            id=generate_note_id(),
            date=date,
            time_written="00:00",
            mood=mood,
            content=text,
            tags=tags,
            note_type=ntype,
            sealed_until=sealed,
            xp_earned=int(xp_str) if xp_str.isdigit() else 0,
            word_count=count_words(text),
        )
        note_store.save_note(note)
        note_store.notes.append(note)
        existing_dates.add(date)
        imported += 1

    note_store.notes.sort(key=lambda n: n.date)
    if imported:
        messagebox.showinfo(APP_NAME,
            f"Imported {imported} notes from v2!", parent=parent)
    else:
        messagebox.showinfo(APP_NAME,
            "No new notes to import.", parent=parent)
    return imported


# ================================================================
#  Open file with system default app
# ================================================================
def _open_file(path: str):
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            import subprocess
            subprocess.run(["open", path], check=False)
        else:
            import subprocess
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass
