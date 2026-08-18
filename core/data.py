# ================================================================
#  NOBARO v1  —  core/data.py
#  Data models and persistence.  Pure Python, no GUI.
#  Notes stored as individual JSON files in data/notes/.
# ================================================================

from __future__ import annotations
import os
import shutil
import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from core.constants import (
    NOTES_DIR, PLAYER_FILE, ACHIEVS_FILE, TEMPLATES_FILE,
    LETTERS_FILE, BACKUP_DIR, ACHIEVEMENT_IDS,
    LEVELS, THEME_NAMES
)
from core.utils import (
    load_json, save_json, ensure_dirs, generate_note_id,
    today, count_words
)


# ================================================================
#  Data models
# ================================================================

@dataclass
class MediaRef:
    path:       str = ""       # relative path inside data/media/
    media_type: str = "file"   # "image" | "audio" | "video" | "file"
    caption:    str = ""

@dataclass
class Note:
    id:          str = ""
    date:        str = ""
    time_written:str = ""
    mood:        str = ":|"
    content:     str = ""      # plain text (the actual diary text)
    tags:        str = ""
    note_type:   str = "normal"  # "normal" | "future" | "unsent"
    sealed_until:str = ""
    xp_earned:   int = 0
    word_count:  int = 0
    # Rich-text formatting stored as a list of tag spans
    # Each span: {"start": "1.0", "end": "1.5", "tags": ["bold","cyan"]}
    formatting:  List[dict] = field(default_factory=list)
    media:       List[MediaRef] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "date":         self.date,
            "time_written": self.time_written,
            "mood":         self.mood,
            "content":      self.content,
            "tags":         self.tags,
            "note_type":    self.note_type,
            "sealed_until": self.sealed_until,
            "xp_earned":    self.xp_earned,
            "word_count":   self.word_count,
            "formatting":   self.formatting,
            "media":        [{"path": m.path,
                              "media_type": m.media_type,
                              "caption": m.caption}
                             for m in self.media],
        }

    @staticmethod
    def from_dict(d: dict) -> "Note":
        media = [MediaRef(**m) for m in d.get("media", [])]
        return Note(
            id           = d.get("id", ""),
            date         = d.get("date", ""),
            time_written = d.get("time_written", ""),
            mood         = d.get("mood", ":|"),
            content      = d.get("content", ""),
            tags         = d.get("tags", ""),
            note_type    = d.get("note_type", "normal"),
            sealed_until = d.get("sealed_until", ""),
            xp_earned    = d.get("xp_earned", 0),
            word_count   = d.get("word_count", 0),
            formatting   = d.get("formatting", []),
            media        = media,
        )

    def note_path(self) -> str:
        return os.path.join(NOTES_DIR, self.id + ".json")


@dataclass
class Player:
    xp:               int  = 0
    level:            int  = 0
    has_password:     bool = False
    password_hash:    int  = 0
    theme:            str  = "QBasic Classic"
    default_font:     str  = "Courier New"
    default_font_size:int  = 11
    last_open:        str  = ""
    total_words:      int  = 0
    longest_streak:   int  = 0
    current_streak:   int  = 0
    auto_save_secs:   int  = 120
    show_daily_quote: bool = True
    show_last_year:   bool = True
    ui_language:      str  = "en"
    default_rtl:      bool = False

    def level_name(self) -> str:
        for threshold, name in reversed(LEVELS):
            if self.xp >= threshold:
                return name
        return LEVELS[0][1]

    def xp_for_next(self) -> int:
        for threshold, _ in LEVELS:
            if threshold > self.xp:
                return threshold
        return 99999

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Player":
        p = Player()
        for k, v in d.items():
            if hasattr(p, k):
                setattr(p, k, v)
        # Validate theme
        if p.theme not in THEME_NAMES:
            p.theme = THEME_NAMES[0]
        return p


@dataclass
class Achievement:
    id:            str  = ""
    unlocked:      bool = False
    unlocked_date: str  = ""

    NAMES = {
        "FIRST_NOTE":    "[*] First Note — you wrote your first entry!",
        "STREAK_7":      "[FIRE] 7-Day Streak — a whole week of memories!",
        "STREAK_30":     "[FLAME] 30-Day Streak — a month of dedication!",
        "NOTES_10":      "[10] Ten Notes — getting into the habit!",
        "NOTES_100":     "[100] One Hundred Notes — true chronicler!",
        "CRYING_WEEK":   "[RAIN] Crying Week — seven sad days. You survived.",
        "HAPPY_WEEK":    "[SUN] Happy Week — seven days of smiling!",
        "ALL_MOODS":     "[RAINBOW] All Moods — you felt everything.",
        "BURNED_NOTE":   "[ASH] Burned Note — some memories are ash.",
        "FUTURE_LETTER": "[CLOCK] Future Letter — wrote to future-you!",
        "WROTE_LONG":    "[SCROLL] Long Note — 500+ chars in one entry!",
        "GREP_USED":     "[LENS] Grep Master — searched your memories.",
        "NIGHT_OWL":     "[OWL] Night Owl — writing after midnight!",
        "RICH_TEXT":     "[PEN] Rich Text Master — used formatting!",
        "MEDIA_STAR":    "[STAR] Media Star — attached a file to a note!",
        "ASCII_ARTIST":  "[ART] ASCII Artist — created ASCII art!",
        "TEMPLATE_USER": "[TMPL] Template User — applied a template!",
    }

    def display_name(self) -> str:
        return self.NAMES.get(self.id, f"[?] {self.id}")


@dataclass
class Letter:
    id:           str  = ""
    written_date: str  = ""
    unlock_date:  str  = ""
    to_name:      str  = "Future Me"
    content:      str  = ""
    is_read:      bool = False
    letter_type:  str  = "future"   # "future" | "unsent"

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Letter":
        l = Letter()
        for k, v in d.items():
            if hasattr(l, k):
                setattr(l, k, v)
        return l


@dataclass
class Template:
    id:          str = ""
    name:        str = ""
    description: str = ""
    content:     str = ""
    tags:        str = ""
    use_count:   int = 0

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Template":
        t = Template()
        for k, v in d.items():
            if hasattr(t, k):
                setattr(t, k, v)
        return t


# ================================================================
#  NoteStore — load/save all notes
# ================================================================

class NoteStore:
    def __init__(self):
        self.notes: List[Note] = []
        ensure_dirs(NOTES_DIR)

    def load_all(self):
        self.notes = []
        for fn in os.listdir(NOTES_DIR):
            if fn.endswith(".json"):
                path = os.path.join(NOTES_DIR, fn)
                d = load_json(path)
                if d:
                    try:
                        self.notes.append(Note.from_dict(d))
                    except Exception:
                        pass
        self.notes.sort(key=lambda n: n.date)

    def save_note(self, note: Note) -> bool:
        if not note.id:
            note.id = generate_note_id()
        if not note.date:
            note.date = today()
        note.word_count = count_words(note.content)
        return save_json(note.note_path(), note.to_dict())

    def delete_note(self, note: Note) -> bool:
        path = note.note_path()
        if os.path.isfile(path):
            os.remove(path)
        if note in self.notes:
            self.notes.remove(note)
        return True

    def find_by_date(self, date: str, note_type: str = "normal") -> Optional[Note]:
        """Returns the first match only. Kept for single-note lookups
        (letters, 'this day last year', gap-fill checks) where any one
        note for that date is enough. For the full list of a day's
        entries — since a day can hold many now — use find_all_by_date().
        """
        for n in self.notes:
            if n.date == date and n.note_type == note_type:
                return n
        return None

    def find_all_by_date(self, date: str, note_type: str = "normal") -> List[Note]:
        """All notes for a given date. A day is no longer capped at one
        entry, so this can return zero, one, or many notes."""
        return [n for n in self.notes
                if n.date == date and n.note_type == note_type]

    def find_by_id(self, note_id: str) -> Optional[Note]:
        for n in self.notes:
            if n.id == note_id:
                return n
        return None

    def normal_notes(self) -> List[Note]:
        return [n for n in self.notes if n.note_type == "normal"]

    def search(self, term: str) -> List[Note]:
        term = term.lower()
        return [n for n in self.normal_notes()
                if term in n.content.lower() or term in n.tags.lower()]

    def backup(self):
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        dest = os.path.join(BACKUP_DIR, f"backup_{ts}")
        os.makedirs(dest, exist_ok=True)
        for fn in os.listdir(NOTES_DIR):
            if fn.endswith(".json"):
                shutil.copy(os.path.join(NOTES_DIR, fn), dest)
        for fp in (PLAYER_FILE, ACHIEVS_FILE):
            if os.path.isfile(fp):
                shutil.copy(fp, dest)


# ================================================================
#  PlayerStore
# ================================================================

class PlayerStore:
    def __init__(self):
        self.player = Player()

    def load(self):
        d = load_json(PLAYER_FILE)
        if d:
            self.player = Player.from_dict(d)

    def save(self):
        save_json(PLAYER_FILE, self.player.to_dict())

    def add_xp(self, amount: int) -> bool:
        """Returns True if levelled up."""
        old_level = self.player.level
        self.player.xp += amount
        new_level = 0
        for i, (threshold, _) in enumerate(LEVELS):
            if self.player.xp >= threshold:
                new_level = i
        levelled_up = new_level > old_level
        self.player.level = new_level
        return levelled_up


# ================================================================
#  AchievementStore
# ================================================================

class AchievementStore:
    def __init__(self):
        self.achievements: List[Achievement] = []
        self._init()

    def _init(self):
        self.achievements = [Achievement(id=aid) for aid in ACHIEVEMENT_IDS]

    def load(self):
        data = load_json(ACHIEVS_FILE, [])
        id_map = {a["id"]: a for a in data if "id" in a}
        for a in self.achievements:
            if a.id in id_map:
                a.unlocked      = id_map[a.id].get("unlocked", False)
                a.unlocked_date = id_map[a.id].get("unlocked_date", "")

    def save(self):
        data = [{"id": a.id, "unlocked": a.unlocked,
                 "unlocked_date": a.unlocked_date}
                for a in self.achievements]
        save_json(ACHIEVS_FILE, data)

    def unlock(self, aid: str) -> bool:
        """Returns True if newly unlocked (wasn't before)."""
        for a in self.achievements:
            if a.id == aid and not a.unlocked:
                a.unlocked      = True
                a.unlocked_date = today()
                return True
        return False

    def is_unlocked(self, aid: str) -> bool:
        for a in self.achievements:
            if a.id == aid:
                return a.unlocked
        return False


# ================================================================
#  LetterStore
# ================================================================

class LetterStore:
    def __init__(self):
        self.letters: List[Letter] = []

    def load(self):
        data = load_json(LETTERS_FILE, [])
        self.letters = [Letter.from_dict(d) for d in data]

    def save(self):
        save_json(LETTERS_FILE, [l.to_dict() for l in self.letters])

    def add(self, letter: Letter):
        if not letter.id:
            letter.id = generate_note_id()
        self.letters.append(letter)
        self.save()

    def due_letters(self) -> List[Letter]:
        t = today()
        return [l for l in self.letters
                if not l.is_read and l.letter_type == "future"
                and l.unlock_date <= t]


# ================================================================
#  TemplateStore
# ================================================================

BUILTIN_TEMPLATES = [
    Template(
        id="builtin_daily", name="Daily Check-In",
        description="3 questions to ground you in the day",
        tags="#daily #checkin",
    ),
    Template(
        id="builtin_gratitude", name="Gratitude Log",
        description="Three things you are grateful for today",
        tags="#gratitude #positivity",
    ),
    Template(
        id="builtin_weekly", name="Weekly Reflection",
        description="Review your week — wins, struggles, lessons",
        tags="#weekly #reflection",
    ),
    Template(
        id="builtin_letter", name="Letter to Self",
        description="Start with 'Dear me...'",
        tags="#letter #self",
    ),
]

class TemplateStore:
    def __init__(self):
        self.templates: List[Template] = list(BUILTIN_TEMPLATES)

    def load(self):
        data = load_json(TEMPLATES_FILE, [])
        user = [Template.from_dict(d) for d in data
                if not d.get("id","").startswith("builtin_")]
        self.templates = list(BUILTIN_TEMPLATES) + user

    def save(self):
        user = [t.to_dict() for t in self.templates
                if not t.id.startswith("builtin_")]
        save_json(TEMPLATES_FILE, user)

    def get_content(self, template: Template) -> str:
        """Expand a template to its full text content."""
        import datetime as dt
        t = today()
        dow = dt.date.today().strftime("%A")
        if template.id == "builtin_daily":
            return (f"Daily Check-In — {t} ({dow})\n\n"
                    "How am I feeling right now?\n\n\n"
                    "What happened today that matters?\n\n\n"
                    "What do I want to remember from this day?\n\n")
        if template.id == "builtin_gratitude":
            return (f"Gratitude Log — {t}\n\n"
                    "1. I am grateful for...\n\n\n"
                    "2. Something small that made me smile...\n\n\n"
                    "3. A person I appreciate today...\n\n")
        if template.id == "builtin_weekly":
            return (f"Weekly Reflection — Week of {t}\n\n"
                    "WINS this week:\n\n\n"
                    "STRUGGLES this week:\n\n\n"
                    "What I learned:\n\n\n"
                    "What I carry into next week:\n\n")
        if template.id == "builtin_letter":
            return (f"Dear me,\n\n"
                    f"Today is {t} and I want you to know...\n\n\n"
                    "What scares me right now:\n\n\n"
                    "What excites me right now:\n\n\n"
                    f"Love,\nPast you ({t})")
        # User template — replace placeholders
        content = template.content
        content = content.replace("{DATE}", t)
        content = content.replace("{DAY_OF_WEEK}", dow)
        return content
