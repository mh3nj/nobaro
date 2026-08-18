# ================================================================
#  NOBARO v1  —  core/utils.py
#  Date helpers, word count, ID gen, gap detection, streak calc.
#  All pure Python — fully testable without GUI.
# ================================================================

import datetime
import random
import os
import json
import re


# ---- Date helpers --------------------------------------------

def today() -> str:
    return datetime.date.today().isoformat()          # "YYYY-MM-DD"

def now_time() -> str:
    return datetime.datetime.now().strftime("%H:%M")

def yesterday() -> str:
    return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

def last_year_date() -> str:
    d = datetime.date.today()
    try:
        return d.replace(year=d.year - 1).isoformat()
    except ValueError:                                # Feb 29 on non-leap year
        return (d.replace(year=d.year - 1, day=28)).isoformat()

def parse_date(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s)

def add_days(date_str: str, n: int) -> str:
    return (parse_date(date_str) + datetime.timedelta(days=n)).isoformat()

def days_between(a: str, b: str) -> int:
    """Positive if b > a."""
    return (parse_date(b) - parse_date(a)).days

def prev_day(date_str: str) -> str:
    return add_days(date_str, -1)

def next_day(date_str: str) -> str:
    return add_days(date_str, 1)

def friendly_date(date_str: str) -> str:
    if date_str == today():
        return "Today"
    if date_str == yesterday():
        return "Yesterday"
    d = parse_date(date_str)
    return d.strftime("%b %d, %Y")

def month_name(m: int) -> str:
    return datetime.date(2000, m, 1).strftime("%B")

def short_month(m: int) -> str:
    return datetime.date(2000, m, 1).strftime("%b")

def days_in_month(year: int, month: int) -> int:
    if month == 12:
        return (datetime.date(year + 1, 1, 1) - datetime.date(year, 12, 1)).days
    return (datetime.date(year, month + 1, 1) - datetime.date(year, month, 1)).days

def day_of_week_iso(year: int, month: int, day: int) -> int:
    """0=Monday … 6=Sunday  (ISO weekday - 1)"""
    return datetime.date(year, month, day).weekday()


# ---- Streak & gaps -------------------------------------------

def calculate_streak(notes: list) -> int:
    """
    notes: list of dicts with at least {"date": "YYYY-MM-DD", "note_type": str}
    Returns current consecutive-day streak of normal notes.
    """
    normal_dates = {n["date"] for n in notes if n.get("note_type") == "normal"}
    if not normal_dates:
        return 0
    streak    = 0
    check     = datetime.date.today()
    while True:
        if check.isoformat() in normal_dates:
            streak += 1
            check  -= datetime.timedelta(days=1)
        else:
            break
        if streak > 3650:
            break
    return streak

def get_gap_dates(notes: list, max_gaps: int = 90) -> list:
    """Return list of missing date strings between first note and yesterday."""
    normal_dates = {n["date"] for n in notes if n.get("note_type") == "normal"}
    if not normal_dates:
        return []
    earliest = min(parse_date(d) for d in normal_dates)
    yesterday_d = datetime.date.today() - datetime.timedelta(days=1)
    gaps = []
    cur  = earliest
    while cur <= yesterday_d:
        if cur.isoformat() not in normal_dates:
            gaps.append(cur.isoformat())
            if len(gaps) >= max_gaps:
                break
        cur += datetime.timedelta(days=1)
    return gaps


# ---- Note ID generation --------------------------------------

def generate_note_id() -> str:
    """YYYYMMDD-HHMM-XXXX"""
    now  = datetime.datetime.now()
    rand = format(random.randint(0, 0xFFFF), "04X")
    return now.strftime("%Y%m%d-%H%M-") + rand


# ---- Word count ----------------------------------------------

def count_words(text: str) -> int:
    return len(re.findall(r'\S+', text))


# ---- File I/O ------------------------------------------------

def load_json(path: str, default=None):
    if not os.path.isfile(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: str, data) -> bool:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def load_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def save_text(path: str, text: str) -> bool:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except Exception:
        return False


# ---- Ensure data directories exist --------------------------

def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


# ---- Daily quote (same one all day) -------------------------

def daily_quote(quotes: list) -> str:
    if not quotes:
        return ""
    idx = datetime.date.today().toordinal() % len(quotes)
    return quotes[idx]


# ---- Simple XOR cipher (same logic as PureBasic version) ----

def _simple_hash(text: str) -> int:
    h = 5381
    for ch in text:
        h = ((h << 5) + h) + ord(ch)
        h &= 0xFFFFFFFF
    return h

def _xor_raw(text: str, password: str) -> str:
    """Pure XOR — not safe for file storage (may produce non-UTF8)."""
    if not password or not text:
        return text
    klen = len(password)
    return "".join(chr(ord(ch) ^ ord(password[i % klen])) for i, ch in enumerate(text))

def xor_cipher(text: str, password: str) -> str:
    """Encrypt text to hex string (safe for file storage)."""
    raw = _xor_raw(text, password)
    return raw.encode("utf-8", errors="replace").hex()

def xor_decipher(hex_str: str, password: str) -> str:
    """Decrypt hex string back to text."""
    try:
        raw = bytes.fromhex(hex_str).decode("utf-8", errors="replace")
        return _xor_raw(raw, password)
    except Exception:
        return ""

def hash_password(password: str) -> int:
    return _simple_hash(password)


# ---- Detect media type from extension -----------------------

def detect_media_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".ico"}:
        return "image"
    if ext in {".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a"}:
        return "audio"
    if ext in {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"}:
        return "video"
    return "file"
