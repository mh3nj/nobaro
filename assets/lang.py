# ================================================================
#  NOBARO v1  —  assets/lang.py
#  All user-visible strings.  English default, Farsi included.
# ================================================================

STRINGS = {
    "en": {
        # App
        "app_name":       "NOBARO",
        "app_tagline":    "Your Digital Soul",

        # Menu / actions
        "new_note":       "New Note",
        "save_note":      "Save Note",
        "burn_note":      "Burn a Note",
        "history":        "Past Notes",
        "cozy_mode":      "Cozy Reading Mode",
        "grep":           "Search Memories",
        "stats":          "Stats & Achievements",
        "calendar":       "Calendar View",
        "word_freq":      "Word Frequency",
        "mood_graph":     "Mood Graph",
        "month_view":     "This Month in History",
        "future_letter":  "Letter to Future Me",
        "unsent_letter":  "Unsent Letter",
        "ascii_art":      "ASCII Art Gallery",
        "templates":      "Templates",
        "settings":       "Settings",
        "export":         "Export",
        "quit":           "Quit",
        "about":          "About",
        "annual_review":  "Annual Review",

        # Formatting toolbar
        "bold":           "Bold (Ctrl+B)",
        "italic":         "Italic (Ctrl+I)",
        "underline":      "Underline (Ctrl+U)",
        "strikethrough":  "Strikethrough",
        "highlight":      "Highlight text",
        "font_color":     "Text color",
        "align_left":     "Align Left",
        "align_center":   "Align Center",
        "align_right":    "Align Right",
        "dir_ltr":        "Left-to-Right",
        "dir_rtl":        "Right-to-Left",
        "insert_image":   "Insert Image",
        "insert_audio":   "Insert Audio",
        "insert_video":   "Insert Video",
        "insert_file":    "Attach File",

        # Status / feedback
        "save_ok":        "Note saved!",
        "no_notes":       "No notes yet. Write your life first!",
        "unsaved_warn":   "Unsaved changes. Save before continuing?",
        "confirm_burn":   "BURN THIS MEMORY FOREVER?\nType YES to confirm:",
        "confirm_quit":   "You have unsaved changes. Quit anyway?",
        "error_save":     "Could not save note. Check disk space.",
        "error_load":     "Could not load notes.",
        "backup_ok":      "Backup complete.",

        # Sidebar
        "streak":         "Streak",
        "level":          "Level",
        "xp":             "XP",
        "today":          "Today",
        "yesterday":      "Yesterday",
        "words":          "words",
        "daily_quote":    "Daily Quote",

        # Moods
        "mood_happy":     "Happy :)",
        "mood_laugh":     "Laughing :D",
        "mood_neutral":   "Neutral :|",
        "mood_sad":       "Sad :(",
        "mood_crying":    "Crying ;(",

        # Tags
        "tags_hint":      "#tag1 #tag2 ...",

        # Letters
        "sealed_until":   "Sealed until:",
        "letter_opened":  "A SEALED LETTER HAS OPENED",
        "last_year":      "A MESSAGE FROM PAST YOU (one year ago today)",
        "on_this_month":  "THIS MONTH IN YOUR HISTORY",
        "future_sealed":  "Your letter is sealed until:",

        # Search
        "grep_prompt":    "Search your memories:",
        "grep_results":   "results matched",
        "grep_none":      "No notes found for:",

        # Settings
        "change_theme":   "Change Theme",
        "auto_save":      "Auto-save interval (seconds, 0=off):",
        "set_password":   "Set / Change Password",
        "import_v2":      "Import v2 notes (NOBARO_NOTES.TXT)",
        "password_prompt":"Enter password:",
        "password_wrong": "Wrong password.",
        "password_set":   "Password set.",

        # Misc
        "fill_gaps":      "Missing days detected! Write a catch-up note?",
        "template_apply": "Apply Template",
        "achievements":   "Achievements",
        "open_selected":  "Open Selected Note",
        "insert_note":    "Insert into Note",
        "inject":         "Inject",
        "create_new":     "Create New",
        "edit":           "Edit",
        "save":           "Save",
        "close":          "Close",
        "cancel":         "Cancel",
        "yes":            "Yes",
        "no":             "No",
        "delete":         "Delete",
        "save_close":     "Save & Close",
        "prev":           "< Prev",
        "next":           "Next >",

        # About
        "about_text": (
            "NOBARO v1\n"
            "A peaceful offline note engine.\n"
            "Built with Python + tkinter. No internet required.\n\n"
            "10 PRINT \"you matter\"\n"
            "20 GOTO 10"
        ),
    },

    "fa": {
        "app_name":       "نوبارو",
        "app_tagline":    "روح دیجیتال تو",
        "new_note":       "یادداشت جدید",
        "save_note":      "ذخیره",
        "burn_note":      "سوزاندن یادداشت",
        "history":        "یادداشت‌های گذشته",
        "cozy_mode":      "حالت مطالعه آرام",
        "grep":           "جستجو در خاطرات",
        "stats":          "آمار و دستاوردها",
        "calendar":       "نمای تقویم",
        "word_freq":      "فراوانی کلمات",
        "mood_graph":     "نمودار حال",
        "month_view":     "این ماه در تاریخچه",
        "future_letter":  "نامه به آینده‌ام",
        "unsent_letter":  "نامه نفرستاده",
        "ascii_art":      "گالری ASCII",
        "templates":      "قالب‌ها",
        "settings":       "تنظیمات",
        "export":         "خروجی",
        "quit":           "خروج",
        "about":          "درباره",
        "annual_review":  "مرور سالانه",
        "bold":           "ضخیم (Ctrl+B)",
        "italic":         "کج (Ctrl+I)",
        "underline":      "زیرخط (Ctrl+U)",
        "strikethrough":  "خط‌خورده",
        "highlight":      "هایلایت",
        "font_color":     "رنگ متن",
        "align_left":     "تراز چپ",
        "align_center":   "تراز وسط",
        "align_right":    "تراز راست",
        "dir_ltr":        "چپ به راست",
        "dir_rtl":        "راست به چپ",
        "insert_image":   "درج تصویر",
        "insert_audio":   "درج صدا",
        "insert_video":   "درج ویدیو",
        "insert_file":    "پیوست فایل",
        "save_ok":        "ذخیره شد!",
        "no_notes":       "هنوز یادداشتی نیست.",
        "unsaved_warn":   "تغییرات ذخیره نشده. ذخیره شود؟",
        "confirm_burn":   "این خاطره را برای همیشه بسوزانید؟\nYES بنویسید:",
        "confirm_quit":   "تغییرات ذخیره نشده. خروج؟",
        "error_save":     "خطا در ذخیره. فضای دیسک را بررسی کنید.",
        "error_load":     "خطا در بارگذاری.",
        "backup_ok":      "پشتیبان‌گیری انجام شد.",
        "streak":         "روزهای متوالی",
        "level":          "سطح",
        "xp":             "امتیاز",
        "today":          "امروز",
        "yesterday":      "دیروز",
        "words":          "کلمه",
        "daily_quote":    "نقل‌قول روز",
        "mood_happy":     "شاد :)",
        "mood_laugh":     "خندان :D",
        "mood_neutral":   "خنثی :|",
        "mood_sad":       "غمگین :(",
        "mood_crying":    "گریان ;(",
        "tags_hint":      "#برچسب ...",
        "sealed_until":   "مهر شده تا:",
        "letter_opened":  "یک نامه مهر شده باز شد",
        "last_year":      "پیامی از گذشته (یک سال پیش)",
        "on_this_month":  "این ماه در تاریخچه شما",
        "future_sealed":  "نامه تا این تاریخ مهر شده است:",
        "grep_prompt":    "جستجو در خاطرات:",
        "grep_results":   "نتیجه پیدا شد",
        "grep_none":      "یادداشتی یافت نشد:",
        "change_theme":   "تغییر پوسته",
        "auto_save":      "فاصله ذخیره خودکار (ثانیه):",
        "set_password":   "تنظیم رمز عبور",
        "import_v2":      "وارد کردن یادداشت‌های نسخه ۲",
        "password_prompt":"رمز عبور:",
        "password_wrong": "رمز اشتباه است.",
        "password_set":   "رمز تنظیم شد.",
        "fill_gaps":      "روزهای از دست رفته! یادداشت جبرانی بنویسید؟",
        "template_apply": "اعمال قالب",
        "achievements":   "دستاوردها",
        "open_selected":  "باز کردن یادداشت انتخابی",
        "insert_note":    "درج در یادداشت",
        "inject":         "درج",
        "create_new":     "ایجاد جدید",
        "edit":           "ویرایش",
        "save":           "ذخیره",
        "close":          "بستن",
        "cancel":         "انصراف",
        "yes":            "بله",
        "no":             "خیر",
        "delete":         "حذف",
        "save_close":     "ذخیره و بستن",
        "prev":           "< قبلی",
        "next":           "بعدی >",
        "about_text": (
            "نوبارو نسخه ۱\n"
            "یک موتور یادداشت‌نویسی آفلاین و آرام.\n\n"
            "10 PRINT \"تو مهمی\"\n"
            "20 GOTO 10"
        ),
    },
}


class Lang:
    def __init__(self, language: str = "en"):
        self._lang = language if language in STRINGS else "en"
        self._d    = STRINGS[self._lang]

    def set(self, language: str):
        self._lang = language if language in STRINGS else "en"
        self._d    = STRINGS[self._lang]

    def __call__(self, key: str) -> str:
        return self._d.get(key, STRINGS["en"].get(key, key))

    def language(self) -> str:
        return self._lang


# Module-level singleton
lang = Lang("en")
