# ================================================================
#  NOBARO v1  —  assets/sounds.py
#  All QBasic-style Beep melodies.
#  Uses winsound.Beep() on Windows (exact same API as PureBasic).
#  Silently falls back on Linux/macOS so nothing crashes.
# ================================================================

import time
import threading

try:
    import winsound as _ws
    def _beep(freq: int, dur_ms: int):
        _ws.Beep(freq, dur_ms)
    SOUND_AVAILABLE = True
except ImportError:
    def _beep(freq: int, dur_ms: int):
        pass   # Silent fallback — app still works perfectly
    SOUND_AVAILABLE = False


def _note(freq: int, dur_ms: int, gap_ms: int = 15):
    _beep(freq, dur_ms)
    if gap_ms > 0:
        time.sleep(gap_ms / 1000)


def _play(melody_fn):
    """Run melody in a daemon thread so UI never blocks."""
    t = threading.Thread(target=melody_fn, daemon=True)
    t.start()


# ================================================================
#  Melodies
# ================================================================

def _startup():
    # Warm ascending — "loading memories..."
    _note(262, 80);  _note(330, 80);  _note(392, 80);  _note(523, 120)
    time.sleep(0.06)
    _note(523, 60);  _note(587, 60);  _note(659, 180)
    time.sleep(0.08)
    _note(784, 80);  _note(880, 300)

def _quit():
    # Descending, nostalgic — "goodbye little me"
    for freq in [523, 494, 440, 392, 349, 330, 294, 262]:
        _note(freq, 80 if freq > 262 else 300)

def _save():
    _note(660, 60);  _note(880, 100)

def _level_up():
    _note(523, 80);  _note(523, 80);  _note(523, 80)
    time.sleep(0.04)
    _note(523, 80);  _note(415, 80);  _note(466, 80);  _note(523, 200)
    time.sleep(0.06)
    _note(466, 80);  _note(523, 350)

def _achievement():
    _note(659, 60);  _note(784, 60);  _note(1047, 120)
    time.sleep(0.04)
    _note(1047, 60); _note(1175, 200)

def _seal():
    _note(440, 150); _note(415, 150); _note(370, 150); _note(330, 300)
    time.sleep(0.1)
    _note(220, 400)

def _letter_open():
    _note(330, 80);  _note(392, 80)
    time.sleep(0.04)
    _note(523, 80);  _note(659, 80);  _note(784, 80)
    time.sleep(0.06)
    _note(1047, 200)
    time.sleep(0.08)
    _note(784, 80);  _note(1047, 80); _note(1175, 300)

def _burn():
    for freq in [880, 740, 622, 523, 440, 370, 311, 262]:
        _note(freq, 80)
    time.sleep(0.03)
    _note(196, 400)

def _sad():
    _note(330, 200); _note(311, 200); _note(294, 200)
    time.sleep(0.08)
    _note(277, 200); _note(262, 400)

def _gorilla():
    # Gorillas.bas tribute — for the screensaver
    _note(523, 100); _note(523, 100); _note(784, 100); _note(784, 100)
    _note(880, 200)
    time.sleep(0.06)
    _note(784, 300)
    time.sleep(0.06)
    _note(698, 100); _note(698, 100); _note(659, 100); _note(659, 100)
    _note(587, 200)
    time.sleep(0.06)
    _note(523, 300)

def _error():
    _note(440, 80);  _note(330, 80);  _note(220, 200)

def _notify():
    _note(880, 60);  time.sleep(0.03);  _note(1047, 100)

def _attach():
    _note(784, 60);  _note(880, 60);  _note(988, 80)

def _streak(days: int):
    if days >= 30:
        for f in [523, 659, 784, 1047, 1047, 880]:
            _note(f, 60)
        _note(1047, 200); time.sleep(0.06); _note(1175, 400)
    elif days >= 7:
        _note(523, 80);  _note(659, 80);  _note(784, 200)
        time.sleep(0.04); _note(880, 300)
    else:
        _note(659, 80);  _note(784, 80);  _note(880, 150)

def _password_ok():
    _note(440, 60);  _note(660, 60);  _note(880, 100)

def _password_fail():
    _note(440, 80);  _note(415, 80);  _note(370, 150)


# ================================================================
#  Public API — all async (non-blocking)
# ================================================================

def play_startup():      _play(_startup)
def play_quit():         _play(_quit)
def play_save():         _play(_save)
def play_level_up():     _play(_level_up)
def play_achievement():  _play(_achievement)
def play_seal():         _play(_seal)
def play_letter_open():  _play(_letter_open)
def play_burn():         _play(_burn)
def play_sad():          _play(_sad)
def play_gorilla():      _play(_gorilla)
def play_error():        _play(_error)
def play_notify():       _play(_notify)
def play_attach():       _play(_attach)
def play_streak(days):   _play(lambda: _streak(days))
def play_password_ok():  _play(_password_ok)
def play_password_fail():_play(_password_fail)
