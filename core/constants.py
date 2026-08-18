# ================================================================
#  NOBARO v1  —  core/constants.py
#  All constants: QBasic colors, themes, paths, XP, moods.
# ================================================================

import os
import sys

# ---- Paths ---------------------------------------------------
# When frozen with PyInstaller, keep all data next to the executable
# so the app stays fully portable (no writes into the install dir).
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
NOTES_DIR  = os.path.join(DATA_DIR, "notes")
MEDIA_DIR  = os.path.join(DATA_DIR, "media")
ASCII_DIR  = os.path.join(DATA_DIR, "ascii")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")
PLAYER_FILE    = os.path.join(DATA_DIR, "player.json")
ACHIEVS_FILE   = os.path.join(DATA_DIR, "achievements.json")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")
LETTERS_FILE   = os.path.join(DATA_DIR, "letters.json")
IMPORT_V2_FILE = os.path.join(BASE_DIR, "NOBARO_NOTES.TXT")

# ---- App info ------------------------------------------------
APP_NAME    = "NOBARO"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Your Digital Soul"

# ---- Themes --------------------------------------------------
THEMES = {
    "QBasic Classic": {
        "bg":         "#0000AA",
        "bg_edit":    "#000088",
        "bg_header":  "#0000CC",
        "bg_btn":     "#000099",
        "bg_btn_sel": "#000066",
        "fg":         "#55FFFF",
        "fg_dim":     "#0088AA",
        "accent":     "#FFFF55",
        "border":     "#5555FF",
        "select_bg":  "#5555FF",
        "select_fg":  "#FFFFFF",
        "font":       "Courier New",
    },
    "Green Phosphor": {
        "bg":         "#001400",
        "bg_edit":    "#000A00",
        "bg_header":  "#001E00",
        "bg_btn":     "#001900",
        "bg_btn_sel": "#000800",
        "fg":         "#00FF00",
        "fg_dim":     "#008C00",
        "accent":     "#96FF96",
        "border":     "#006400",
        "select_bg":  "#006400",
        "select_fg":  "#00FF00",
        "font":       "Courier New",
    },
    "Amber Phosphor": {
        "bg":         "#140800",
        "bg_edit":    "#0C0400",
        "bg_header":  "#1C0C00",
        "bg_btn":     "#180A00",
        "bg_btn_sel": "#0A0400",
        "fg":         "#FFB000",
        "fg_dim":     "#AA6400",
        "accent":     "#FFDC50",
        "border":     "#783C00",
        "select_bg":  "#783C00",
        "select_fg":  "#FFB000",
        "font":       "Courier New",
    },
    "Midnight": {
        "bg":         "#0F0520",
        "bg_edit":    "#080212",
        "bg_header":  "#16082D",
        "bg_btn":     "#140828",
        "bg_btn_sel": "#08020F",
        "fg":         "#C8B4FF",
        "fg_dim":     "#7864B4",
        "accent":     "#FF78FF",
        "border":     "#502878",
        "select_bg":  "#502878",
        "select_fg":  "#C8B4FF",
        "font":       "Courier New",
    },
    "Paper": {
        "bg":         "#F5EBD2",
        "bg_edit":    "#FFF8E6",
        "bg_header":  "#EBDCBE",
        "bg_btn":     "#DCCDB0",
        "bg_btn_sel": "#B4A078",
        "fg":         "#3C2814",
        "fg_dim":     "#78583C",
        "accent":     "#A03C00",
        "border":     "#B4966E",
        "select_bg":  "#A03C00",
        "select_fg":  "#FFF8E6",
        "font":       "Georgia",
    },
}
THEME_NAMES = list(THEMES.keys())

# ---- Moods ---------------------------------------------------
MOODS = [
    (":)",  "Happy",    "#55FF55"),
    (":D",  "Laughing", "#FFFF55"),
    (":|",  "Neutral",  "#AAAAAA"),
    (":(",  "Sad",      "#FF5555"),
    (";(",  "Crying",   "#5555FF"),
]
MOOD_SYMBOLS = [m[0] for m in MOODS]
MOOD_NAMES   = [m[1] for m in MOODS]
MOOD_COLORS  = {m[0]: m[2] for m in MOODS}

# ---- XP & Levels ---------------------------------------------
LEVELS = [
    (0,     "BEGINNER"),
    (50,    "APPRENTICE"),
    (150,   "EXPLORER"),
    (350,   "CHRONICLER"),
    (700,   "HISTORIAN"),
    (1200,  "ARCHIVIST"),
    (2000,  "SAGE"),
    (3000,  "ORACLE"),
    (4500,  "LEGEND"),
    (6500,  "MYTHIC"),
    (99999, "TRANSCENDENT"),
]
XP_NORMAL_NOTE  = 25
XP_LONG_NOTE    = 50
XP_FUTURE_LETTER = 50
XP_STREAK_BONUS = 10
XP_TEMPLATE_USE = 5
XP_MEDIA_ATTACH = 10
XP_ASCII_CREATE = 15

# ---- Achievement IDs ----------------------------------------
ACHIEVEMENT_IDS = [
    "FIRST_NOTE", "STREAK_7", "STREAK_30", "NOTES_10", "NOTES_100",
    "CRYING_WEEK", "HAPPY_WEEK", "ALL_MOODS", "BURNED_NOTE",
    "FUTURE_LETTER", "WROTE_LONG", "GREP_USED", "NIGHT_OWL",
    "RICH_TEXT", "MEDIA_STAR", "ASCII_ARTIST", "TEMPLATE_USER",
]

# ---- Font sizes (points) ------------------------------------
FS_SMALL  = 9
FS_NORMAL = 11
FS_MEDIUM = 13
FS_H3     = 16
FS_H2     = 22
FS_H1     = 28

# ---- File filters -------------------------------------------
FILTER_IMG   = [("Images",    "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("All files", "*.*")]
FILTER_AUDIO = [("Audio",     "*.mp3 *.wav *.ogg *.flac *.aac *.m4a"),
                ("All files", "*.*")]
FILTER_VIDEO = [("Video",     "*.mp4 *.avi *.mkv *.mov *.wmv *.webm"),
                ("All files", "*.*")]
FILTER_ALL   = [("All files", "*.*")]

# ---- Daily quotes -------------------------------------------
DAILY_QUOTES = [
    "Code is poetry that runs.",
    "One note = one memory saved.",
    "Future you will thank present you for this line.",
    "Blue screen = safe place.",
    "Beep beep! You're doing great.",
    "PRINT 'Hello World' to yourself today.",
    "Every day deserves a line of text.",
    "No internet needed for this feeling.",
    "QBasic taught us: we can create anything.",
    "This note is a gift to future you.",
    "The screen glows because you do.",
    "Your story compiles without errors.",
    "Even GOTO was a step forward.",
    "10 PRINT 'you matter' : 20 GOTO 10",
    "The best diary is the one you actually write.",
    "Yesterday is a note you already saved.",
    "Feelings are just data with feelings.",
    "Write it. Even badly. Especially badly.",
    "Gorillas.bas never judged anyone.",
    "In a world of streams, be a note file.",
]
