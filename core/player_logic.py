# ================================================================
#  NOBARO v1  —  core/player_logic.py
#  All XP, level-up, achievement-checking logic.
#  Pure functions — no GUI, fully testable.
# ================================================================

import datetime
from core.constants import LEVELS, XP_NORMAL_NOTE, XP_LONG_NOTE, XP_STREAK_BONUS
from core.data import Player, PlayerStore, AchievementStore, NoteStore
from core.utils import today, calculate_streak


def get_level_name(xp: int) -> str:
    name = LEVELS[0][1]
    for threshold, lname in LEVELS:
        if xp >= threshold:
            name = lname
    return name


def get_level_index(xp: int) -> int:
    idx = 0
    for i, (threshold, _) in enumerate(LEVELS):
        if xp >= threshold:
            idx = i
    return idx


def xp_for_next_level(xp: int) -> int:
    for threshold, _ in LEVELS:
        if threshold > xp:
            return threshold
    return 99999


def calc_note_xp(content: str, has_media: bool = False,
                 used_formatting: bool = False) -> int:
    xp = XP_NORMAL_NOTE
    if len(content) >= 500:
        xp += XP_LONG_NOTE
    if has_media:
        xp += 10
    if used_formatting:
        xp += 5
    return xp


def check_achievements(note_store: NoteStore,
                       achiev_store: AchievementStore,
                       player: Player) -> list:
    """
    Check all achievement conditions and unlock any newly earned ones.
    Returns list of newly-unlocked achievement IDs.
    """
    newly = []
    notes = note_store.normal_notes()

    def unlock(aid):
        if achiev_store.unlock(aid):
            newly.append(aid)

    # Note count milestones
    n = len(notes)
    if n >= 1:   unlock("FIRST_NOTE")
    if n >= 10:  unlock("NOTES_10")
    if n >= 100: unlock("NOTES_100")

    # Long note
    if any(len(note.content) >= 500 for note in notes):
        unlock("WROTE_LONG")

    # Media attachment
    if any(note.media for note in notes):
        unlock("MEDIA_STAR")

    # All moods used
    used_moods = {note.mood for note in notes}
    if used_moods >= {":)", ":D", ":|", ":(", ";("}:
        unlock("ALL_MOODS")

    # Streak milestones
    note_dicts = [{"date": n.date, "note_type": n.note_type} for n in notes]
    streak = calculate_streak(note_dicts)
    player.current_streak  = streak
    player.longest_streak  = max(player.longest_streak, streak)
    if streak >= 7:  unlock("STREAK_7")
    if streak >= 30: unlock("STREAK_30")

    # Night owl — writing after 11pm or before 5am
    hour = datetime.datetime.now().hour
    if hour >= 23 or hour < 5:
        unlock("NIGHT_OWL")

    # 7-day mood streaks (last 7 notes)
    last7 = notes[-7:]
    if len(last7) == 7:
        if all(n.mood in {":)", ":D"} for n in last7):
            unlock("HAPPY_WEEK")
        if all(n.mood in {":(", ";("} for n in last7):
            unlock("CRYING_WEEK")

    return newly


def apply_streak_bonus(player_store: PlayerStore) -> int:
    """Add streak XP bonus, return amount added."""
    streak = player_store.player.current_streak
    if streak < 3:
        return 0
    bonus = XP_STREAK_BONUS * (streak // 7 + 1)
    player_store.add_xp(bonus)
    return bonus
