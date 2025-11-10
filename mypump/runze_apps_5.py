import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkFont
from PIL import Image, ImageTk
import threading, time, os, json
from runze6 import mypump

pump = mypump()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.running = True
        # Window settings
        self.title("Raspberry Pi GUI - Recipes")
        self.geometry("800x480")
        self.resizable(False, False)
        # self.tk.call('tk', 'scaling', 0.9)

        # Data
        # recipe_stages: list of stages, each stage is {"name": str, "blocks": [block dicts]}
        # block dict: {"name","direction","volume","flow","valve","pause","syringe"}
        self.recipe_stages = []
        self.cycles = []  # list of {"start": int, "end": int, "count": int}
        self.recipe_dir = "recipes"
        os.makedirs(self.recipe_dir, exist_ok=True)

        # Settings
        self.settings_file = "settings.json"
        self.theme = "Light"
        # default_font = tkFont.nametofont("Verdana")
        # default_font.configure(family=self.font_family)
        # text_font = tkFont.nametofont("Verdana")
        # text_font.configure(family=self.font_family)
        self.font_family = "Times New Roman"
        self.bg_color = "white"
        self.load_settings()
        self.apply_theme()

        # UI frames
        self.top_frame = tk.Frame(self, bg=self.bg_color, height=48)
        self.top_frame.pack(fill="x", side="top")

        self.time_label = tk.Label(self.top_frame, text="", font=(self.font_family, 14, "bold"), bg=self.bg_color)
        self.time_label.pack(side="right", padx=12)
        threading.Thread(target=self._update_time, daemon=True).start()

        self.main_frame = tk.Frame(self, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        self.bottom_frame = tk.Frame(self, bg=self.bg_color, height=80, relief="solid", bd=3)
        self.bottom_frame.pack(fill="x", side="bottom")

        # Default bottom nav
        self.default_nav_buttons = [
            ("🏠 Главный экран", self.show_main),
            ("📘 Задать рецепт", self.show_recipe_stages),
            ("📂 Сохранённые \n"
             "рецепты", self.show_saved_recipes),
            ("✋ Ручное \n"
             "управление", self.show_manual_control_page),
            ("⚙️ Настройки", lambda: self.show_page("settings")),
        ]
        self.render_bottom_nav(self.default_nav_buttons)

        # Keyboard window holder
        self.keyboard_window = None

        # default image
        self.default_image_path = "default.jpg"

        # start
        self.show_main()

        # override close without confirmation (user requested)
        self.protocol("WM_DELETE_WINDOW", self._on_close_no_confirm)

    # ---------------------- helpers ----------------------
    def _update_time(self):
        while True:
            try:
                self.time_label.config(text=time.strftime("%H:%M:%S"))
            except tk.TclError:
                return
            time.sleep(1)

    def clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def clear_bottom(self):
        for w in self.bottom_frame.winfo_children():
            w.destroy()

    def render_bottom_nav(self, buttons):
        """Render main bottom navigation (global). Replaces bottom_frame contents."""
        self.clear_bottom()
        for text, cmd in buttons:
            b = tk.Button(self.bottom_frame, text=text, font=(self.font_family, 12),
                          command=cmd, width=15, height=3, bg="white", relief="solid", bd=2)
            b.pack(side="left", expand=True, fill="both", padx=2, pady=6)

    # ---------------------- main screens ----------------------
    def show_main(self):
        self.clear_main()
        self.render_bottom_nav(self.default_nav_buttons)
        if os.path.exists(self.default_image_path):
            img = Image.open(self.default_image_path)
            img.thumbnail((800, 480))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.main_frame, image=photo, bg=self.bg_color)
            lbl.image = photo
            lbl.place(relx=0.5, rely=0.5, anchor="center")
        else:
            tk.Label(self.main_frame, text="Главный экран",
                     font=(self.font_family, 20, "bold"), bg=self.bg_color).place(relx=0.5, rely=0.5, anchor="center")

    # ---------------------- recipe stages screen ----------------------
    def show_recipe_stages(self):
        """Shows list of stages (blocks at top), with bottom panel replaced as requested."""
        self.clear_main()

        # Bottom panel replacement for recipe page:
        # ⬅ Главный экран | ⚙️ Инициализация | 💾 Сохранить рецепт | ⏹ Остановить | ⏸ Пауза | ▶️ Продолжить
        self.clear_bottom()
        # Left: main navigation
        b_home = tk.Button(self.bottom_frame, text="🏠 Главный экран", font=(self.font_family, 12),
                           command=self.show_main, width=12, height=3, bg="white")
        b_home.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_init = tk.Button(self.bottom_frame, text="⚙️ Инициализация", font=(self.font_family, 12),
                           command=self.init_pump, width=12, height=3, bg="white")
        b_init.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_start_recipe = tk.Button(self.bottom_frame, text="▶️ Запуск", font=(self.font_family, 12),
                           command=self.start_recipe, width=12, height=3, bg="white")
        b_start_recipe.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_save_recipe = tk.Button(self.bottom_frame, text="💾 Сохранить рецепт", font=(self.font_family, 12),
                                  command=self.save_recipe, width=12, height=3, bg="white")
        b_save_recipe.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_stop = tk.Button(self.bottom_frame, text="⏹ Остановить", font=(self.font_family, 12),
                           command=self.stop_pump, width=12, height=3, bg="white")
        b_stop.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        # Standard style for pause/resume to match other buttons (light)
        b_pause = tk.Button(self.bottom_frame, text="⏸ Пауза", font=(self.font_family, 12),
                            command=getattr(pump, "pause_transfer", lambda: None), width=12, height=3, bg="white")
        b_pause.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_resume = tk.Button(self.bottom_frame, text="▶️ Продолжить", font=(self.font_family, 12),
                             command=getattr(pump, "resume_transfer", lambda: None), width=12, height=3, bg="white")
        b_resume.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        # Header
        header = tk.Label(self.main_frame, text="📘 Этапы рецепта", font=(self.font_family, 18, "bold"), bg=self.bg_color)
        header.pack(pady=6)

        # Container for columns
        container = tk.Frame(self.main_frame, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=8, pady=4)

        # columns frame
        cols_frame = tk.Frame(container, bg=self.bg_color)
        cols_frame.pack(anchor="nw", fill="both", expand=True)

        per_col = 20
        total = len(self.recipe_stages)
        cols_needed = (total + per_col - 1) // per_col if total else 1

        col_frames = []
        for c in range(cols_needed):
            f = tk.Frame(cols_frame, bg=self.bg_color)
            f.pack(side="left", padx=6, pady=4, anchor="n")
            col_frames.append(f)

        for idx, stage in enumerate(self.recipe_stages):
            col = idx // per_col
            # block style: larger, bold, centered
            f = tk.Frame(col_frames[col], bg="white", relief="flat", bd=2, width=100, height=30)
            f.pack_propagate(False)
            f.pack(pady=4, anchor="n")
            lbl = tk.Label(f, text=stage.get("name", f"Этап {idx+1}"), font=(self.font_family, 11, "bold"),
                           bg="white", anchor="center", justify="center")
            lbl.pack(fill="both", expand=True)
            f.bind("<Button-1>", lambda e, i=idx: self.open_stage_editor(idx))
            # f.bind("<ButtonRelease-1>", lambda e, i=idx: self.open_stage_editor(idx))
            lbl.bind("<Button-1>", lambda e, i=idx: self.open_stage_editor(i))

        # add/remove stage rectangular buttons under columns
        btns_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        btns_frame.pack(pady=8)
        tk.Button(btns_frame, text="➕ Добавить этап", font=(self.font_family, 13), bg="#c2f0c2",
                  width=14, height=1, command=self.add_stage).pack(side="left", padx=8)
        tk.Button(btns_frame, text="➖ Убрать этап", font=(self.font_family, 13), bg="#f5b7b1",
                  width=14, height=1, command=self.remove_stage).pack(side="left", padx=8)

        if not hasattr(self, "_recipe_timer_label") or not self._recipe_timer_label.winfo_exists():
            self._recipe_timer_label = tk.Label(
                self.main_frame,
                text="⏱ Время выполнения: 00:00:00",
                font=(self.font_family, 10, "bold"),
                bg=self.bg_color,
                fg="#333"
            )
            self._recipe_timer_label.pack(pady=4)

        def _update_local_timer():
            if getattr(self, "_update_timer_running", False):
                elapsed = int(time.time() - getattr(self, "start_time", time.time()))
                h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                self._recipe_timer_label.config(text=f"⏱ Время выполнения: {h:02}:{m:02}:{s:02}")
                self.after(1000, _update_local_timer)
            else:
                self._recipe_timer_label.config(text="⏱ Время выполнения: 00:00:00")

        _update_local_timer()

        # cycles area
        cycle_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        cycle_frame.pack(pady=6, fill="x")
        tk.Label(cycle_frame, text="Циклы выполнения:", font=(self.font_family, 12), bg=self.bg_color).pack(side="left", padx=6)
        tk.Button(cycle_frame, text="Добавить цикл", font=(self.font_family, 12), bg="#d6eaf8", command=self.add_cycle_dialog).pack(side="left", padx=6)
        tk.Button(cycle_frame, text="Очистить циклы", font=(self.font_family, 12), bg="#f5b7b1", command=self.clear_cycles).pack(side="left", padx=6)
        if self.cycles:
            cycles_text = "Текущее: " + "; ".join([f"{c['start']+1}-{c['end']+1} x{c['count']}" for c in self.cycles])
            tk.Label(self.main_frame, text=cycles_text, font=(self.font_family, 11), bg=self.bg_color).pack(pady=6)

    # ---------------------- stage management ----------------------
    def add_stage(self):
        """Добавляет этап через кастомный диалог с встроенной экранной клавиатурой (QWERTY)."""
        dlg = tk.Toplevel(self)
        dlg.title("Новый этап")
        dlg.geometry("700x400")
        dlg.configure(bg=self.bg_color)
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="Введите название этапа:", font=(self.font_family, 12), bg=self.bg_color).pack(pady=8)
        name_entry = tk.Entry(dlg, font=(self.font_family, 14), width=20)
        name_entry.pack(pady=6)
        name_entry.focus_set()

        # --- встроенная клавиатура в окне диалога ---
        kb_frame = tk.Frame(dlg, bg=self.bg_color)
        kb_frame.pack(pady=6)

        rows = [
            "1234567890",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm-_."
        ]

        def insert_char(ch):
            name_entry.insert(tk.END, ch)
            name_entry.focus_set()

        def backspace():
            s = name_entry.get()
            if s:
                name_entry.delete(len(s) - 1, tk.END)
            name_entry.focus_set()

        for row in rows:
            rowf = tk.Frame(kb_frame, bg=self.bg_color)
            rowf.pack(pady=2)
            for ch in row:
                btn = tk.Button(rowf, text=ch, width=4, height=2, font=(self.font_family, 9),
                                command=lambda c=ch: insert_char(c))
                btn.pack(side="left", padx=2)
            # add backspace on last row
        last_row = tk.Frame(kb_frame, bg=self.bg_color)
        last_row.pack(pady=4)
        tk.Button(last_row, text="←", width=6, height=2, font=(self.font_family, 11), command=backspace).pack(
            side="left", padx=6)
        tk.Button(last_row, text="Очистить", width=8, height=2, font=(self.font_family, 11),
                  command=lambda: (name_entry.delete(0, tk.END), name_entry.focus_set())).pack(side="left", padx=6)

        # --- кнопки OK / Отмена ---
        btn_frame = tk.Frame(dlg, bg=self.bg_color)
        btn_frame.pack(pady=8)

        def on_ok():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Ошибка", "Имя не может быть пустым.", parent=dlg)
                return
            self.recipe_stages.append({"name": name, "blocks": []})
            dlg.grab_release()
            dlg.destroy()
            self.show_recipe_stages()

        def on_cancel():
            dlg.grab_release()
            dlg.destroy()

        tk.Button(btn_frame, text="OK", command=on_ok, width=12, bg="#c2f0c2", font=(self.font_family, 12)).pack(
            side="left", padx=8)
        tk.Button(btn_frame, text="Отмена", command=on_cancel, width=12, bg="#f2cccc",
                  font=(self.font_family, 12)).pack(side="left", padx=8)

    def edit_stage_name_dialog(self, stage_index):
        """Диалог для редактирования названия этапа с встроенной клавиатурой."""
        if stage_index < 0 or stage_index >= len(self.recipe_stages):
            return
        stage = self.recipe_stages[stage_index]

        dlg = tk.Toplevel(self)
        dlg.title("Изменить название этапа")
        dlg.geometry("480x400")
        dlg.configure(bg=self.bg_color)
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="Название этапа:", font=(self.font_family, 12), bg=self.bg_color).pack(pady=8)
        name_entry = tk.Entry(dlg, font=(self.font_family, 14), width=28)
        name_entry.insert(0, stage.get("name", ""))
        name_entry.pack(pady=6)
        name_entry.focus_set()

        # --- встроенная клавиатура ---
        kb_frame = tk.Frame(dlg, bg=self.bg_color)
        kb_frame.pack(pady=6)

        rows = [
            "1234567890",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm-_."
        ]

        def insert_char(ch):
            name_entry.insert(tk.END, ch)
            name_entry.focus_set()

        def backspace():
            s = name_entry.get()
            if s:
                name_entry.delete(len(s) - 1, tk.END)
            name_entry.focus_set()

        for row in rows:
            rowf = tk.Frame(kb_frame, bg=self.bg_color)
            rowf.pack(pady=2)
            for ch in row:
                btn = tk.Button(rowf, text=ch, width=4, height=2, font=(self.font_family, 11),
                                command=lambda c=ch: insert_char(c))
                btn.pack(side="left", padx=2)

        last_row = tk.Frame(kb_frame, bg=self.bg_color)
        last_row.pack(pady=4)
        tk.Button(last_row, text="←", width=6, height=2, font=(self.font_family, 11), command=backspace).pack(
            side="left", padx=6)
        tk.Button(last_row, text="Очистить", width=8, height=2, font=(self.font_family, 11),
                  command=lambda: (name_entry.delete(0, tk.END), name_entry.focus_set())).pack(side="left", padx=6)

        # --- кнопки ---
        btn_frame = tk.Frame(dlg, bg=self.bg_color)
        btn_frame.pack(pady=8)

        def on_save():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Ошибка", "Имя не может быть пустым.", parent=dlg)
                return
            self.recipe_stages[stage_index]["name"] = new_name
            dlg.grab_release()
            dlg.destroy()
            self.show_recipe_stages()

        def on_cancel():
            dlg.grab_release()
            dlg.destroy()

        tk.Button(btn_frame, text="Сохранить", command=on_save, width=12, bg="#c2f0c2",
                  font=(self.font_family, 12)).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Отмена", command=on_cancel, width=12, bg="#f2cccc",
                  font=(self.font_family, 12)).pack(side="left", padx=8)

    def remove_stage(self):
        if not self.recipe_stages:
            messagebox.showinfo("Удаление", "Нет этапов для удаления.")
            return
        if messagebox.askyesno("Подтверждение", "Удалить последний этап?"):
            self.recipe_stages.pop()
            self.show_recipe_stages()

    # ---------------------- stage editor ----------------------
    def open_stage_editor(self, stage_index):
        """Open page to edit a stage: show its blocks and editing controls.
           Bottom panel here will be: ⬅ Назад | ➕ Добавить шаг | ➖ Убрать шаг | 💾 Сохранить (stage blocks)
        """
        self.clear_main()

        stage = self.recipe_stages[stage_index]
        header = tk.Label(self.main_frame, text=f"⚙️ Редактирование этапа: {stage.get('name')}",
                          font=(self.font_family, 16, "bold"), bg=self.bg_color)
        header.pack(pady=6)

        self.stage_blocks_container = tk.Frame(self.main_frame, bg=self.bg_color)
        self.stage_blocks_container.pack(fill="both", expand=True, padx=8, pady=4)

        # render blocks in this stage
        self._render_stage_blocks(stage_index)

        # bottom controls for this editor (as requested - a dedicated bottom panel for stage editor)
        # We will temporarily override bottom_frame with editor controls
        self.clear_bottom()
        b_back = tk.Button(self.bottom_frame, text="⬅ Назад", font=(self.font_family, 12),
                           command=self.show_recipe_stages, width=18, height=2, bg="white")
        b_back.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_add = tk.Button(self.bottom_frame, text="➕ Добавить шаг", font=(self.font_family, 12),
                          command=lambda idx=stage_index: self.add_block_to_stage(idx), width=18, height=2, bg="white")
        b_add.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_remove = tk.Button(self.bottom_frame, text="➖ Убрать шаг", font=(self.font_family, 12),
                             command=lambda idx=stage_index: self.remove_last_block_in_stage(idx), width=18, height=2, bg="white")
        b_remove.pack(side="left", padx=2, pady=6, expand=True, fill="both")

        b_save_stage = tk.Button(self.bottom_frame, text="💾 Сохранить", font=(self.font_family, 12),
                                 command=lambda idx=stage_index: self.save_stage(idx), width=18, height=2, bg="white")
        b_save_stage.pack(side="left", padx=2, pady=6, expand=True, fill="both")

    def _render_stage_blocks(self, stage_index):
        for w in self.stage_blocks_container.winfo_children():
            w.destroy()
        stage = self.recipe_stages[stage_index]
        blocks = stage.get("blocks", [])
        if not blocks:
            tk.Label(self.stage_blocks_container, text="В этом этапе ещё нет шагов.", font=(self.font_family, 12),
                     bg=self.bg_color).pack(pady=10)
            return
        for i, block in enumerate(blocks):
            # Ensure each param on its own line (as requested)
            f = tk.LabelFrame(self.stage_blocks_container, text=block.get("name", f"Шаг {i+1}"),
                              font=(self.font_family, 10, "bold"), bg="white",
                              padx=6, pady=4, width=300, height=100, relief="groove")
            f.pack_propagate(False)
            f.pack(padx=8, pady=6, anchor="nw")
            # each parameter on a new line
            txt_lines = [
                f"Шприц: {block.get('syringe','') } мкл",
                f"Направление: {block.get('direction','')}",
                f"Объём: {block.get('volume','') } мкл",
                f"Расход: {block.get('flow','') } мкл/мин",
                f"Клапан: {block.get('valve','') }",
                f"Пауза: {block.get('pause','—') } мин"
            ]
            for line in txt_lines:
                tk.Label(f, text=line, justify="left", anchor="w", bg="white", font=(self.font_family, 10)).pack(anchor="w")
            f.bind("<Button-1>", lambda e, s_idx=stage_index, b_idx=i: self.open_block_editor(s_idx, b_idx))

    def add_block_to_stage(self, stage_index):
        """Append a default block and open its editor."""
        new_block = {
            "name": f"Шаг {len(self.recipe_stages[stage_index]['blocks']) + 1}",
            "direction": "Вперёд",
            "volume": "",
            "flow": "",
            "valve": "",
            "pause": "",
            "syringe": 125
        }
        self.recipe_stages[stage_index]["blocks"].append(new_block)
        self._render_stage_blocks(stage_index)
        # open editor for new block
        self.open_block_editor(stage_index, len(self.recipe_stages[stage_index]["blocks"]) - 1)

    def remove_last_block_in_stage(self, stage_index):
        blocks = self.recipe_stages[stage_index]["blocks"]
        if not blocks:
            messagebox.showinfo("Удаление", "Нет шагов для удаления.")
            return
        if messagebox.askyesno("Подтверждение", "Удалить последний шаг в этапе?"):
            blocks.pop()
            self._render_stage_blocks(stage_index)

    def open_block_editor(self, stage_index, block_index):
        """Editor Toplevel for a block inside a stage. Fields on separate lines and keyboard bindings."""
        data = self.recipe_stages[stage_index]["blocks"][block_index]
        win = tk.Toplevel(self)
        win.title(f"Редактирование шага: {data.get('name','')}")
        win.geometry("520x720")
        win.configure(bg=self.bg_color)

        container = tk.Frame(win, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=10, pady=8)

        # syringe at top
        tk.Label(container, text="Объём шприца (мкл):", bg=self.bg_color, font=(self.font_family, 12)).pack(pady=4)
        syringe_var = tk.IntVar(value=data.get("syringe", 125))
        syringe_box = ttk.Combobox(container, textvariable=syringe_var, values=[125, 500], font=(self.font_family, 12), width=18)
        syringe_box.pack(pady=4)

        # Fields
        labels = [
            ("name", "Название шага:"),
            ("direction", "Направление потока:"),
            ("volume", "Объём (мкл):"),
            ("flow", "Расход (мкл/мин):"),
            ("valve", "Клапан:"),
            ("pause", "Пауза (мин):")
        ]
        fields = {}
        direction_var = tk.StringVar(value=data.get("direction", "Вперёд"))

        for key, label_text in labels:
            tk.Label(container, text=label_text, bg=self.bg_color, font=(self.font_family, 12)).pack(pady=3)
            if key == "direction":
                entry = ttk.Combobox(container, textvariable=direction_var, values=["Вперёд", "Назад"], font=(self.font_family, 12), width=18)
                entry.set(data.get("direction", "Вперёд"))
            else:
                entry = tk.Entry(container, font=(self.font_family, 12), width=28)
                entry.insert(0, str(data.get(key, "")))
                numeric = key in ("volume", "flow", "valve", "pause")
                entry.bind("<Button-1>", lambda e, ent=entry, num=numeric: self.show_keyboard(ent, numeric=num))
            entry.pack(pady=3)
            fields[key] = entry

        # Save/delete/close buttons
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(pady=12)

        def save_block():
            try:
                new_data = {
                    "name": fields["name"].get(),
                    "direction": direction_var.get(),
                    "volume": fields["volume"].get(),
                    "flow": fields["flow"].get(),
                    "valve": fields["valve"].get(),
                    "pause": fields["pause"].get(),
                    "syringe": syringe_var.get()
                }
                self.recipe_stages[stage_index]["blocks"][block_index] = new_data
                self._render_stage_blocks(stage_index)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        def delete_block():
            if messagebox.askyesno("Подтверждение", "Удалить этот шаг?"):
                self.recipe_stages[stage_index]["blocks"].pop(block_index)
                self._render_stage_blocks(stage_index)
                win.destroy()

        tk.Button(btn_frame, text="Сохранить", command=save_block, font=(self.font_family, 12),
                  bg="#c2f0c2", width=10).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Удалить", command=delete_block, font=(self.font_family, 12),
                  bg="#f5b7b1", width=10).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Закрыть", command=win.destroy, font=(self.font_family, 12),
                  bg="#f2cccc", width=10).pack(side="left", padx=6)

    def save_stage(self, stage_index):
        """Save stage changes (already written to memory by editors), show feedback."""
        messagebox.showinfo("Сохранено", f"Этап '{self.recipe_stages[stage_index]['name']}' сохранён.")
        # keep showing editor of the same stage
        self.open_stage_editor(stage_index)

    # ---------------------- cycles ----------------------
    def add_cycle_dialog(self):
        if not self.recipe_stages:
            messagebox.showinfo("Циклы", "Добавьте сначала этапы.")
            return
        dlg = tk.Toplevel(self)
        dlg.title("Добавить цикл")
        dlg.geometry("380x220")
        dlg.configure(bg=self.bg_color)

        tk.Label(dlg, text="Начальный этап (номер, с 1):", bg=self.bg_color).pack(pady=6)
        start_e = tk.Entry(dlg); start_e.pack(pady=4)
        start_e.bind("<Button-1>", lambda e, ent=start_e: self.show_keyboard(ent, numeric=True))

        tk.Label(dlg, text="Конечный этап (номер, с 1):", bg=self.bg_color).pack(pady=6)
        end_e = tk.Entry(dlg); end_e.pack(pady=4)
        end_e.bind("<Button-1>", lambda e, ent=end_e: self.show_keyboard(ent, numeric=True))

        tk.Label(dlg, text="Количество повторов:", bg=self.bg_color).pack(pady=6)
        count_e = tk.Entry(dlg); count_e.pack(pady=4)
        count_e.bind("<Button-1>", lambda e, ent=count_e: self.show_keyboard(ent, numeric=True))

        def add_cycle():
            try:
                s = int(start_e.get()) - 1
                e_i = int(end_e.get()) - 1
                cnt = int(count_e.get())
                if s < 0 or e_i < s or e_i >= len(self.recipe_stages):
                    messagebox.showerror("Ошибка", "Неверный диапазон этапов.")
                    return
                self.cycles.append({"start": s, "end": e_i, "count": cnt})
                dlg.destroy()
                self.show_recipe_stages()
            except Exception as ex:
                messagebox.showerror("Ошибка", str(ex))
        tk.Button(dlg, text="Добавить", bg="#c2f0c2", command=add_cycle).pack(pady=10)
        tk.Button(dlg, text="Отмена", bg="#f2cccc", command=dlg.destroy).pack()

    def clear_cycles(self):
        self.cycles = []
        self.show_recipe_stages()

    # ---------------------- saved recipes ----------------------
    def save_recipe(self):
        if not self.recipe_stages:
            messagebox.showwarning("Пусто", "Нет этапов для сохранения.")
            return
        name = simpledialog.askstring("Сохранение рецепта", "Введите имя рецепта:")
        if not name:
            return
        data = {
            "stages": self.recipe_stages,
            "cycles": self.cycles
        }
        path = os.path.join(self.recipe_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Сохранено", f"Рецепт '{name}' сохранён!")



    def show_saved_recipes(self):
        self.clear_main()
        self.render_bottom_nav(self.default_nav_buttons)  # keep main nav on bottom here
        tk.Label(self.main_frame, text="📂 Сохранённые рецепты", font=(self.font_family, 16, "bold"), bg=self.bg_color).pack(pady=8)
        files = [f for f in os.listdir(self.recipe_dir) if f.endswith(".json")]
        if not files:
            tk.Label(self.main_frame, text="Нет сохранённых рецептов.", font=(self.font_family, 12), bg=self.bg_color).pack(pady=10)
            return
        listbox = tk.Listbox(self.main_frame, font=(self.font_family, 12), height=12)
        for f in files:
            listbox.insert(tk.END, f)
        listbox.pack(pady=8)

        def load_selected():
            sel = listbox.curselection()
            if not sel:
                return
            filename = listbox.get(sel[0])
            path = os.path.join(self.recipe_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as fr:
                    data = json.load(fr)
                # backward compatibility: if file was old style (list), handle both cases
                if isinstance(data, dict) and "stages" in data:
                    self.recipe_stages = data.get("stages", [])
                    self.cycles = data.get("cycles", [])
                elif isinstance(data, list):
                    self.recipe_stages = data
                    self.cycles = []
                else:
                    # unexpected format
                    messagebox.showerror("Ошибка", "Неверный формат файла рецепта.")
                    return
                messagebox.showinfo("Загрузка", f"Рецепт '{filename}' загружен.")
                self.show_recipe_stages()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        def delete_selected():
            sel = listbox.curselection()
            if not sel:
                return
            filename = listbox.get(sel[0])
            path = os.path.join(self.recipe_dir, filename)
            if messagebox.askyesno("Подтверждение", f"Удалить рецепт '{filename}'?"):
                os.remove(path)
                listbox.delete(sel[0])
                messagebox.showinfo("Удалено", f"Рецепт '{filename}' удалён.")

        btns = tk.Frame(self.main_frame, bg=self.bg_color)
        btns.pack(pady=6)
        tk.Button(btns, text="Загрузить рецепт", bg="#c2f0c2", font=(self.font_family, 12), command=load_selected, width=16).pack(side="left", padx=6)
        tk.Button(btns, text="🗑 Удалить рецепт", bg="#f5b7b1", font=(self.font_family, 12), command=delete_selected, width=16).pack(side="left", padx=6)

    # ---------------------- run recipe ----------------------
    def start_recipe(self):
        if not self.recipe_stages:
            messagebox.showwarning("Нет данных", "Добавьте хотя бы один этап.")
            return

        def run_seq():
            # execute cycles first
            for cycle in self.cycles:
                start = cycle["start"]
                end = cycle["end"]
                count = cycle["count"]
                for rep in range(count):
                    self.update_status(f"🔁 Цикл {start+1}-{end+1}, прогон {rep+1}/{count}")
                    for idx in range(start, end + 1):
                        if idx >= len(self.recipe_stages):
                            break
                        self._execute_stage_once(idx)
                        time.sleep(0.2)
            # execute remaining stages not in any cycle
            covered = set()
            for c in self.cycles:
                covered.update(range(c["start"], c["end"] + 1))
            for i in range(len(self.recipe_stages)):
                if i in covered:
                    continue
                self.update_status(f"▶️ Выполняется этап {i+1}: {self.recipe_stages[i]['name']}")
                self._execute_stage_once(i)
                time.sleep(0.2)
            self.update_status("✅ Выполнено!")
            self._update_timer_running = False

        self.start_time = time.time()
        self._update_timer_running = True
        self._update_recipe_timer_live()
        threading.Thread(target=self._update_recipe_timer_live, daemon=True).start()
        threading.Thread(target=run_seq, daemon=True).start()

    def _execute_stage_once(self, stage_idx):
        stage = self.recipe_stages[stage_idx]
        for b_idx, block in enumerate(stage.get("blocks", [])):
            try:
                self.update_status(f"▶️ Выполняется этап {stage_idx+1} - шаг {b_idx+1}: {block.get('name','')}")
                pump.set_volume(int(block.get("syringe", 125)))
                if block.get("direction", "Вперёд") == "Вперёд":
                    pump.refill(float(block.get("volume", 0)), float(block.get("flow", 0)), int(block.get("valve", 0)))
                else:
                    pump.infuse(float(block.get("volume", 0)), float(block.get("flow", 0)), int(block.get("valve", 0)))
                vol = pump.report_volume()
                self.update_status(f"💧 Объём: {vol} мкл")
                # pause using pump.pause() (assumed to take minutes)
                p = block.get("pause")
                if p:
                    try:
                        self.update_status(f"⏸ Пауза {p} мин...")
                        pump.pause(float(p))
                    except Exception:
                        # fallback: sleep minutes
                        try:
                            time.sleep(float(p) * 60)
                        except:
                            pass
            except Exception as e:
                self.update_status(f"⚠️ Ошибка: {e}")
                return

    # ---------------------- manual control ----------------------
    def show_manual_control_page(self):
        self.clear_main()
        self.render_bottom_nav(self.default_nav_buttons)
        tk.Label(
            self.main_frame, text="✋ Ручное управление",
            font=("Arial", 18, "bold"), bg="white"
        ).pack(pady=2)

        form = tk.Frame(self.main_frame, bg="white")
        form.pack(pady=2)

        labels = {
            "syringe": "Объём шприца (мкл):",
            "direction": "Направление потока:",
            "volume": "Объём (мкл):",
            "flow": "Расход (мкл/мин):",
            "valve": "Клапан:",
        }

        self.manual_direction = tk.StringVar(value="Вперёд")
        self.manual_syringe = tk.IntVar(value=125)
        self.manual_fields = {}

        for key, text in labels.items():
            tk.Label(form, text=text, bg="white", font=("Arial", 11)).pack(pady=1)
            if key == "direction":
                entry = ttk.Combobox(form, textvariable=self.manual_direction,
                                     values=["Вперёд", "Назад"], font=("Arial", 11), width=12)
            elif key == "syringe":
                entry = ttk.Combobox(form, textvariable=self.manual_syringe,
                                     values=[125, 500], font=("Arial", 11), width=12)
            else:
                entry = tk.Entry(form, font=("Arial", 11), width=12)
            entry.pack(pady=1)
            self.manual_fields[key] = entry

        button_frame = tk.Frame(self.main_frame, bg="white")
        button_frame.pack(pady=6)

        tk.Button(button_frame, text="⚙️ Инициализация", font=("Arial", 11),
                  width=12, bg="#e0e0e0", command=self.init_pump).pack(side="left", padx=6)
        tk.Button(button_frame, text="▶️ Запуск", font=("Arial", 11),
                  width=12, bg="#c8e6c9", command=self.manual_start).pack(side="left", padx=6)
        tk.Button(button_frame, text="⏹ Остановка", font=("Arial", 11),
                  width=12, bg="#ffcdd2", command=self.manual_stop).pack(side="left", padx=6)

        self.manual_status = tk.Label(self.main_frame, text="", font=(self.font_family, 11), bg=self.bg_color)
        self.manual_status.pack(pady=4)

    def manual_start(self):
        def run_manual():
            try:
                direction = self.manual_direction.get()
                syringe = int(self.manual_syringe.get())
                volume = float(self.manual_fields["volume"].get())
                flow = float(self.manual_fields["flow"].get())
                valve = int(self.manual_fields["valve"].get())

                pump.set_volume(syringe)
                if direction == "Вперёд":
                    pump.refill(volume, flow, valve)
                else:
                    pump.infuse(volume, flow, valve)

                vol = pump.report_volume()
                self.update_status(f"✅ Операция выполнена. 💧 Текущий объём: {vol} мкл")
            except Exception as e:
                self.update_status(f"❌ Ошибка: {e}")

        threading.Thread(target=run_manual, daemon=True).start()

    def manual_stop(self):
        try:
            pump.stop_device()
            self._update_timer_running = False
            self.update_status("⏹ Насос остановлен.")
        except Exception as e:
            self.update_status(f"❌ Ошибка остановки: {e}")

    def _manual_start_from_fields(self, e_volume, e_flow, e_valve):
        try:
            volume = float(e_volume.get())
            flow = float(e_flow.get())
            valve = int(e_valve.get())
            syringe = int(self.manual_syringe.get())
            pump.set_volume(syringe)
            if self.manual_direction.get() == "Вперёд":
                pump.refill(volume, flow, valve)
            else:
                pump.infuse(volume, flow, valve)
            vol = pump.report_volume()
            self.update_status(f"✅ Операция выполнена. 💧 Текущий объём: {vol} мкл")
        except Exception as e:
            self.update_status(f"❌ Ошибка: {e}")

    # ---------------------- keyboard ----------------------
    def show_keyboard(self, entry_widget, numeric=False):
        """Display on-screen keyboard. Closes only with OK."""
        # prevent opening multiple keyboards
        if self.keyboard_window and getattr(self.keyboard_window, "winfo_exists", lambda: False)():
            return
        kb = tk.Toplevel(self)
        self.keyboard_window = kb
        kb.title("Клавиатура")
        kb.geometry("800x300")
        kb.configure(bg=self.bg_color)
        # place roughly at bottom center
        self.update_idletasks()
        x = self.winfo_rootx() + 110
        y = self.winfo_rooty() + 240
        kb.geometry(f"+{x}+{y}")

        def insert(ch):
            entry_widget.insert(tk.END, ch)

        def backspace():
            s = entry_widget.get()
            if s:
                entry_widget.delete(len(s) - 1, tk.END)

        def clear():
            entry_widget.delete(0, tk.END)

        def close():
            try:
                kb.destroy()
            except:
                pass
            self.keyboard_window = None

        if numeric:
            keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], [".", "0", "←"]]
        else:
            keys = [
                list("1234567890"),
                list("qwertyuiop"),
                list("asdfghjkl"),
                list("zxcvbnm")
            ]

        for row in keys:
            rowf = tk.Frame(kb, bg=self.bg_color)
            rowf.pack(pady=3)
            for ch in row:
                if ch == "←":
                    btn = tk.Button(rowf, text="←", width=5, height=2, font=(self.font_family, 12), command=backspace)
                else:
                    btn = tk.Button(rowf, text=ch, width=5, height=2, font=(self.font_family, 12), command=lambda c=ch: insert(c))
                btn.pack(side="left", padx=2)

        cf = tk.Frame(kb, bg=self.bg_color)
        cf.pack(pady=8)
        tk.Button(cf, text="Очистить", bg="#f5b7b1", font=(self.font_family, 12), command=clear, width=12).pack(side="left", padx=8)
        tk.Button(cf, text="OK", bg="#c2f0c2", font=(self.font_family, 12), command=close, width=12).pack(side="left", padx=8)
        kb.protocol("WM_DELETE_WINDOW", lambda: None)

    def init_pump(self):
        try:
            self.update_status("⚙️ Инициализация насоса...")
            pump.init()
            self.update_status("✅ Инициализация завершена.")
        except Exception as e:
            self.update_status(f"❌ Ошибка инициализации: {e}")

    def stop_pump(self):
        try:
            self.running = False
            pump.stop_device()
            self.update_status("⏹ Экстренная остановка.")
        except Exception as e:
            self.update_status(f"❌ Ошибка остановки: {e}")

    # ---------------------- settings ----------------------
    def show_page(self, name):
        self.clear_main()
        self.render_bottom_nav(self.default_nav_buttons)
        if name == "settings":
            tk.Label(self.main_frame, text="⚙️ Настройки", font=(self.font_family, 16, "bold"), bg=self.bg_color).pack(pady=8)
            frame = tk.Frame(self.main_frame, bg=self.bg_color)
            frame.pack(pady=6)

            tk.Label(frame, text="Тема:", font=(self.font_family, 12), bg=self.bg_color).grid(row=0, column=0, sticky="w", pady=4)
            theme_var = tk.StringVar(value=self.theme)
            ttk.Combobox(frame, textvariable=theme_var, values=["Light", "Dark"], width=12).grid(row=0, column=1, padx=8, pady=4)

            tk.Label(frame, text="Шрифт:", font=(self.font_family, 12), bg=self.bg_color).grid(row=1, column=0, sticky="w", pady=4)
            font_var = tk.StringVar(value=self.font_family)
            ttk.Combobox(frame, textvariable=font_var, values=["Arial", "Verdana", "Courier New"], width=16).grid(row=1, column=1, padx=8, pady=4)

            def apply_settings():
                self.theme = theme_var.get()
                self.font_family = font_var.get()
                self.save_settings()
                self.apply_theme()
                messagebox.showinfo("Настройки", "Настройки сохранены и применены.")

            tk.Button(self.main_frame, text="Сохранить настройки", bg="#c2f0c2", font=(self.font_family, 12), command=apply_settings, width=18).pack(pady=10)
        else:
            tk.Label(self.main_frame, text=name, font=(self.font_family, 16, "bold"), bg=self.bg_color).place(relx=0.5, rely=0.5, anchor="center")

    def save_settings(self):
        data = {"theme": self.theme, "font_family": self.font_family}
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theme = data.get("theme", "Light")
                    self.font_family = data.get("font_family", "Arial")
            except:
                pass

    def apply_theme(self):
        if self.theme == "Dark":
            self.bg_color = "#2b2b2b"
        else:
            self.bg_color = "white"
        self.configure(bg=self.bg_color)
        if hasattr(self, "top_frame"):
            self.top_frame.configure(bg=self.bg_color)
        if hasattr(self, "main_frame"):
            self.main_frame.configure(bg=self.bg_color)
        if hasattr(self, "bottom_frame"):
            self.bottom_frame.configure(bg=self.bg_color)

    # ---------------------- utilities ----------------------
    def update_status(self, text):
        if not hasattr(self, "_status_label") or not self._status_label.winfo_exists():
            self._status_label = tk.Label(self.main_frame, text=text, font=(self.font_family, 12), bg=self.bg_color, fg="#333")
            self._status_label.pack(pady=6)
        else:
            self._status_label.config(text=text)
        self.update_idletasks()

    def _on_close_no_confirm(self):
        try:
            getattr(pump, "stop", lambda: None)()
        except:
            pass
        try:
            self.destroy()
        except:
            pass

    def _update_recipe_timer_live(self):
        """Живое обновление таймера выполнения рецепта (видимый снизу под кнопками)."""
        if not hasattr(self, "_recipe_timer_label") or not self._recipe_timer_label.winfo_exists():
            return

        if getattr(self, "_update_timer_running", False):
            elapsed = int(time.time() - self.start_time)
            h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
            self._recipe_timer_label.config(text=f"⏱ Время выполнения: {h:02}:{m:02}:{s:02}")
            self.after(1000, self._update_recipe_timer_live)
        else:
            self._recipe_timer_label.config(text="⏱ Время выполнения: 00:00:00")


# ---------------------- run ----------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()