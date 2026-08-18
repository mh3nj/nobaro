# ================================================================
#  NOBARO v1  —  features/templates.py
#  Template browser and creator.
#  .run() blocks and returns {"content": ..., "tags": ...} or None.
# ================================================================

import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime

from core.data import TemplateStore, Template
from core.utils import today, generate_note_id
from ui.theme import theme
from assets.lang import lang


class TemplatesWindow:
    def __init__(self, parent, template_store: TemplateStore):
        self.ts     = template_store
        self.parent = parent
        self.result = None

    def run(self) -> dict | None:
        win = tk.Toplevel(self.parent)
        win.title(lang("templates"))
        win.configure(bg=theme.bg)
        win.geometry("660x460")
        win.resizable(True, True)
        try:
            win.transient(self.parent)
            win.grab_set()
        except Exception:
            pass

        # ---- Layout ------------------------------------------
        left = tk.Frame(win, bg=theme.bg, width=220)
        left.pack(side="left", fill="y", padx=(6, 0), pady=6)
        left.pack_propagate(False)

        right = tk.Frame(win, bg=theme.bg)
        right.pack(side="right", fill="both", expand=True,
                   padx=6, pady=6)

        # ---- Left: template list -----------------------------
        tk.Label(left, text=lang("templates"),
                 bg=theme.bg, fg=theme.accent,
                 font=theme.font_bold(10)).pack(anchor="w")

        lb_frame = tk.Frame(left, bg=theme.bg)
        lb_frame.pack(fill="both", expand=True)

        lb = tk.Listbox(lb_frame,
                        bg=theme.bg_edit, fg=theme.fg,
                        selectbackground=theme.select_bg,
                        selectforeground=theme.select_fg,
                        font=theme.font_normal(10),
                        relief="flat", bd=0,
                        activestyle="none", width=26)
        lb.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(lb_frame, bg=theme.bg_btn,
                          troughcolor=theme.bg,
                          relief="flat", width=8)
        sb.pack(side="right", fill="y")
        lb.configure(yscrollcommand=sb.set)
        sb.configure(command=lb.yview)

        def refresh_list():
            lb.delete(0, "end")
            for t in self.ts.templates:
                lb.insert("end", f"{t.name}  [{t.use_count}]")

        refresh_list()

        # ---- Right: description + preview --------------------
        tk.Label(right, text="Description",
                 bg=theme.bg, fg=theme.fg_dim,
                 font=theme.font_normal(9)).pack(anchor="w")

        lbl_desc = tk.Label(right, text="",
                            bg=theme.bg, fg=theme.fg,
                            font=theme.font_normal(10),
                            wraplength=380, justify="left",
                            anchor="w")
        lbl_desc.pack(fill="x", pady=2)

        lbl_tags = tk.Label(right, text="",
                            bg=theme.bg, fg=theme.accent,
                            font=theme.font_normal(9), anchor="w")
        lbl_tags.pack(fill="x")

        tk.Label(right, text="Preview",
                 bg=theme.bg, fg=theme.fg_dim,
                 font=theme.font_normal(9)).pack(anchor="w", pady=(6, 0))

        preview = tk.Text(right,
                          bg=theme.bg_edit, fg=theme.fg,
                          font=theme.font_normal(10),
                          relief="flat", bd=4,
                          state="disabled", wrap="word")
        preview.pack(fill="both", expand=True)

        def load_preview(event=None):
            sel = lb.curselection()
            if not sel:
                return
            t = self.ts.templates[sel[0]]
            lbl_desc.configure(text=t.description)
            lbl_tags.configure(text=t.tags)
            content = self.ts.get_content(t)
            preview.configure(state="normal")
            preview.delete("1.0", "end")
            preview.insert("1.0", content[:500])  # show first 500 chars
            preview.configure(state="disabled")

        lb.bind("<<ListboxSelect>>", load_preview)

        # ---- Buttons -----------------------------------------
        btn_frame = tk.Frame(win, bg=theme.bg, pady=4)
        btn_frame.pack(fill="x", padx=6)

        def apply_selected():
            sel = lb.curselection()
            if not sel:
                return
            t = self.ts.templates[sel[0]]
            content = self.ts.get_content(t)
            t.use_count += 1
            self.ts.save()
            self.result = {"content": content, "tags": t.tags}
            win.destroy()

        def create_new():
            name = simpledialog.askstring(
                lang("templates"), "Template name:", parent=win)
            if not name:
                return
            desc = simpledialog.askstring(
                lang("templates"), "Short description:", parent=win) or ""
            tags = simpledialog.askstring(
                lang("templates"),
                "Default tags (e.g. #daily):", parent=win) or ""

            # Ask if they want to use a text body
            body = simpledialog.askstring(
                lang("templates"),
                "Template body (use {DATE}, {DAY_OF_WEEK}):\n"
                "(leave blank for description-based):",
                parent=win) or ""

            tmpl = Template(
                id=f"user_{generate_note_id()}",
                name=name,
                description=desc,
                content=body,
                tags=tags,
                use_count=0)
            self.ts.templates.append(tmpl)
            self.ts.save()
            refresh_list()
            lb.selection_set(lb.size() - 1)
            load_preview()

        def delete_selected():
            sel = lb.curselection()
            if not sel:
                return
            t = self.ts.templates[sel[0]]
            if t.id.startswith("builtin_"):
                messagebox.showinfo(
                    lang("templates"),
                    "Cannot delete built-in templates.",
                    parent=win)
                return
            if messagebox.askyesno(
                    lang("templates"),
                    f"Delete '{t.name}'?",
                    parent=win):
                self.ts.templates.remove(t)
                self.ts.save()
                refresh_list()
                lbl_desc.configure(text="")
                lbl_tags.configure(text="")
                preview.configure(state="normal")
                preview.delete("1.0", "end")
                preview.configure(state="disabled")

        def make_btn(text, cmd, fg=None):
            b = tk.Button(
                btn_frame, text=text, command=cmd,
                bg=theme.bg_btn,
                fg=fg or theme.fg,
                activebackground=theme.bg_btn_sel,
                activeforeground=theme.accent,
                font=theme.font_normal(10),
                relief="flat", bd=1, padx=6, pady=2,
                cursor="hand2")
            b.pack(side="left", padx=3)
            return b

        make_btn(lang("template_apply"), apply_selected, fg=theme.accent)
        make_btn(lang("create_new"),     create_new)
        make_btn(lang("delete"),         delete_selected, fg=theme.fg_dim)
        make_btn(lang("close"),          win.destroy)

        if self.ts.templates:
            lb.selection_set(0)
            load_preview()

        win.wait_window()
        return self.result
