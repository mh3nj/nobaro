# ================================================================
#  NOBARO — tools/gui_smoke_test.py
#  Opens the key dialogs against a real Tk root and auto-closes
#  them, so any construction error surfaces immediately.
#  Usage:  python tools/gui_smoke_test.py
# ================================================================

import os
import sys
import tkinter as tk

# Make the project root importable when run directly (python tools/...)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data import PlayerStore, TemplateStore, NoteStore, AchievementStore
from ui.theme import theme


def main():
    root = tk.Tk()
    root.withdraw()

    errors = []

    def step(name, fn):
        try:
            fn()
            print(f"[OK] {name}")
        except Exception as e:
            import traceback
            errors.append((name, e))
            print(f"[FAIL] {name}: {e!r}")
            traceback.print_exc()

    # About dialog (logo + credits) — must be a sane, small window.
    # The 6000px source logo renders blank in Tk, so the 512px copy
    # is used and the requested size must stay well under 1000px.
    def open_about():
        from features.about import AboutWindow
        AboutWindow(root, lambda: tk.PhotoImage(file="public/logo_256.png"))
        root.update_idletasks()
        for child in root.winfo_children():
            if isinstance(child, tk.Toplevel):
                assert child.winfo_reqwidth() < 1000, \
                    f"About window too wide: {child.winfo_reqwidth()}"
                assert child.winfo_reqheight() < 1000, \
                    f"About window too tall: {child.winfo_reqheight()}"

    # ASCII gallery — open, test search filter + filtered inject
    def open_gallery():
        from features.ascii_art import AsciiGallery

        def find_widget(widget, klass):
            if isinstance(widget, klass):
                return widget
            for child in widget.winfo_children():
                found = find_widget(child, klass)
                if found is not None:
                    return found
            return None

        state = {}
        orig = tk.Toplevel.wait_window

        def fake_wait(self):
            def inspect():
                entry = find_widget(self, tk.Entry)
                listbox = find_widget(self, tk.Listbox)
                navbar = self.winfo_children()[0]
                inject_btn = navbar.winfo_children()[0]
                state["total"] = listbox.size()
                entry.delete(0, "end")
                entry.insert(0, "cat")
                self.update_idletasks()
                state["filtered"] = list(listbox.get(0, "end"))
                inject_btn.invoke()
                state["result"] = gallery.result
            self.after(400, inspect)
            orig(self)

        tk.Toplevel.wait_window = fake_wait
        try:
            gallery = AsciiGallery(root)
            gallery.run()
        finally:
            tk.Toplevel.wait_window = orig

        assert state.get("total") == 30, f"expected 30 pieces, got {state.get('total')}"
        assert state.get("filtered") == ["Tiny Cat"], \
            f"search 'cat' should filter to Tiny Cat, got {state.get('filtered')}"
        assert state.get("result"), "Inject should return a result"

    # Settings dialog
    def open_settings():
        from features.settings import SettingsWindow
        SettingsWindow(root, PlayerStore(), lambda *a: None)
        root.update_idletasks()

    # Templates dialog
    def open_templates():
        from features.templates import TemplatesWindow
        ts = TemplateStore()
        ts.load()
        TemplatesWindow(root, ts)
        root.update_idletasks()

    # Stats overview
    def open_stats():
        from features.stats import StatsWindow
        StatsWindow(root, NoteStore(), PlayerStore(), AchievementStore())
        root.update_idletasks()

    # Screensaver (just construct; it animates via after())
    def open_screensaver():
        import features.screensaver as ss
        orig = tk.Toplevel.wait_window

        def fake_wait(self):
            self.after(400, self.destroy)
            orig(self)

        tk.Toplevel.wait_window = fake_wait
        try:
            ss.run_screensaver(root)
        finally:
            tk.Toplevel.wait_window = orig

    step("About dialog", open_about)
    step("ASCII gallery", open_gallery)
    step("Settings", open_settings)
    step("Templates", open_templates)
    step("Stats overview", open_stats)
    step("Screensaver", open_screensaver)

    root.destroy()

    if errors:
        print(f"\n{len(errors)} failure(s): {[n for n, _ in errors]}")
        raise SystemExit(1)
    print("\nAll GUI dialogs constructed successfully.")


if __name__ == "__main__":
    main()
