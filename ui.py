"""
Tkinter user interface for the Tic-Tac-Toe project.

Implementation notes:
- Uses two screens (start + game) and switches between them without restarting the app.
- Uses custom "pill" toggles (Frame+Label) for reliable colors on macOS.
"""

import tkinter as tk
from tkinter import ttk

from controller import GameController

# UI -> Controller boundary:
# - UI calls controller.start(...) to initialize a new game
# - UI calls controller.click(idx) when the user clicks a cell
# - UI reads controller.game.board to render symbols


class TicTacToeUI(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Tic-Tac-Toe")
        self.geometry("760x650")
        self.resizable(False, False)

        self.controller = GameController()

        # GameController owns the game state and applies all rules.
        # The UI only displays state and forwards user actions.

        # ---------- Colors ----------
        # Central palette: keeping these here makes it easy to tweak the look later.
        self.COL_BG = "#0b1020"
        self.COL_CARD = "#111a33"
        self.COL_CARD_2 = "#0f1730"
        self.COL_TEXT = "#e8edf7"
        self.COL_MUTED = "#a8b3cf"
        self.COL_ACCENT = "#3b82f6"
        self.COL_ACCENT_HOVER = "#60a5fa"
        self.COL_DANGER = "#fb7185"
        self.COL_CELL = "#0a1226"

        # Pill colors (selected/unselected)
        self.PILL_BG = self.COL_CARD_2
        self.PILL_FG = self.COL_TEXT
        self.PILL_BG_ACTIVE = self.COL_ACCENT
        self.PILL_FG_ACTIVE = "white"

        self.configure(bg=self.COL_BG)

        # ttk widgets are used where it makes sense (Combobox/Scrollbar),
        # but the main buttons/pills are custom (Frame+Label) because on macOS
        # native widgets can ignore custom background colors.
        self.ttk_style = ttk.Style(self)
        try:
            self.ttk_style.theme_use("clam")
        except tk.TclError:
            pass

        # ---------- Vars ----------
        # These variables are bound to UI widgets and read when starting a game.
        self.mode_var = tk.StringVar(value="human_vs_computer")  # human_vs_computer / human_vs_human
        self.ai_var = tk.StringVar(value="random")              # random / alphabeta

        self.starter_var = tk.StringVar(value="X")
        self.size_var = tk.IntVar(value=3)                      # slider: 3..6
        # Board size is controlled with a slider (Scale).

        # HVC settings
        self.human_symbol_var = tk.StringVar(value="X")

        # HVH settings
        self.player1_symbol_var = tk.StringVar(value="X")
        self.player2_symbol_var = tk.StringVar(value="O")

        # Error label on start screen (validation feedback)
        self.error_var = tk.StringVar(value="")

        # ---------- Screens ----------
        # We keep two top-level frames and swap them (pack/pack_forget).
        self.start_frame = tk.Frame(self, bg=self.COL_BG)
        self.game_frame = tk.Frame(self, bg=self.COL_BG)

        # Build the start screen once and show it
        self.build_start()
        self.show_start()

    # Navigation
    # Switch between the start screen and the game screen.
    # We use pack_forget/pack instead of destroying the whole window.
    def show_start(self):
        self.game_frame.pack_forget()
        self.start_frame.pack(fill="both", expand=True)

    def show_game(self):
        self.start_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)

    # Small UI helpers
    # Custom clickable label used as a button.
    # We use Label instead of Button so background colors are consistent on macOS.
    def flat_button(self, parent, text, command, *, bg, fg, hover_bg=None, padx=16, pady=10, font=None):
        if font is None:
            font = ("Helvetica", 11, "bold")

        lbl = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            padx=padx,
            pady=pady,
            font=font,
            cursor="hand2"
        )

        # Left click triggers the action
        lbl.bind("<Button-1>", lambda _e: command())

        # Optional hover effect
        if hover_bg:
            lbl.bind("<Enter>", lambda _e: lbl.configure(bg=hover_bg))
            lbl.bind("<Leave>", lambda _e: lbl.configure(bg=bg))

        return lbl

    # Pill toggles
    # Custom toggle controls for options (mode, starter, ...).
    # Implemented as Frame + Label to guarantee color/contrast on macOS.
    # Selected pills are styled in _update_pills().
    def pill(self, parent, text, variable: tk.StringVar, value: str, *, on_change=None):
        """
        A pill toggle implemented as Frame+Label so colors are reliable on macOS.
        """
        wrap = tk.Frame(parent, bg=self.PILL_BG, highlightthickness=0)
        lbl = tk.Label(
            wrap,
            text=text,
            bg=self.PILL_BG,
            fg=self.PILL_FG,
            font=("Helvetica", 11, "bold"),
            padx=16,
            pady=9,
            cursor="hand2",
        )
        lbl.pack()

        # When clicked, set the tk variable and update pill styles.
        def set_value():
            variable.set(value)
            self.update_pills()
            if on_change:
                on_change()

        # Make both the frame and the label clickable
        wrap.bind("<Button-1>", lambda _e: set_value())
        lbl.bind("<Button-1>", lambda _e: set_value())

        # Hover effect only for non-selected pills
        wrap.bind("<Enter>", lambda _e: self.pill_hover(wrap, lbl, True, variable, value))
        wrap.bind("<Leave>", lambda _e: self.pill_hover(wrap, lbl, False, variable, value))
        lbl.bind("<Enter>", lambda _e: self.pill_hover(wrap, lbl, True, variable, value))
        lbl.bind("<Leave>", lambda _e: self.pill_hover(wrap, lbl, False, variable, value))

        # Register the pill so _update_pills() can style it later
        self._pill_registry.append((wrap, lbl, variable, value))
        return wrap

    def pill_hover(self, wrap, lbl, hovering, var, val):
        # Only apply hover to non-selected pills
        if var.get() == val:
            return
        if hovering:
            wrap.configure(bg=self.COL_CARD)
            lbl.configure(bg=self.COL_CARD)
        else:
            wrap.configure(bg=self.PILL_BG)
            lbl.configure(bg=self.PILL_BG)

    def update_pills(self):
        # Apply selected/unselected styles to all pills
        for wrap, lbl, var, val in self._pill_registry:
            if var.get() == val:
                wrap.configure(bg=self.PILL_BG_ACTIVE)
                lbl.configure(bg=self.PILL_BG_ACTIVE, fg=self.PILL_FG_ACTIVE)
            else:
                wrap.configure(bg=self.PILL_BG)
                lbl.configure(bg=self.PILL_BG, fg=self.PILL_FG)

    # Rules popup
    # Modal window describing the game rules.
    # Uses the current board size (N) to display the correct win condition.
    def show_rules_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Rules")
        popup.configure(bg=self.COL_BG)
        popup.resizable(False, False)
        popup.transient(self)   # keep it on top of the main window
        popup.grab_set()        # modal behavior (clicks stay inside popup)

        outer = tk.Frame(popup, bg=self.COL_BG, padx=18, pady=18)
        outer.pack(fill="both", expand=True)

        tk.Label(
            outer,
            text="Tic-Tac-Toe Rules",
            bg=self.COL_BG,
            fg=self.COL_TEXT,
            font=("Helvetica", 22, "bold")
        ).pack(anchor="w", pady=(0, 14))

        # Win condition is "align N" (N = board size)
        n = self.size_var.get()
        rules_text = (
            "Goal\n"
            f"• Align {n} identical symbols in a row, column, or diagonal.\n\n"
            "How to play\n"
            "• Click an empty cell to place your symbol.\n"
            "• Players take turns.\n"
            "• If you align the required number of symbols, you win immediately.\n"
            "• If the board is full and nobody wins, it’s a draw.\n\n"
            "Modes\n"
            "• Vs Computer: the computer plays after you.\n"
            "• 2 Players: Player 1 and Player 2 play locally.\n"
        )

        # Card-like text box (no scrollbar needed; text fits)
        box = tk.Frame(outer, bg=self.COL_CARD, padx=14, pady=14)
        box.pack(fill="both", expand=True)

        text = tk.Text(
            box,
            width=64,
            height=12,
            wrap="word",
            bg=self.COL_CARD,
            fg=self.COL_TEXT,
            insertbackground=self.COL_TEXT,
            relief="flat",
            font=("Helvetica", 15)
        )
        text.insert("1.0", rules_text)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True)

        # Close button
        self.flat_button(
            outer,
            "Close",
            popup.destroy,
            bg=self.COL_ACCENT,
            fg="white",
            hover_bg=self.COL_ACCENT_HOVER,
            padx=18,
            pady=12,
            font=("Helvetica", 13, "bold")
        ).pack(anchor="e", pady=(14, 0))

        # Center the popup over the main window
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 280
        y = self.winfo_y() + (self.winfo_height() // 2) - 200
        popup.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # Start screen
    # Build the settings screen (mode, size, starter, symbols, AI).
    # This is built once; switching mode only refreshes the relevant rows (no flicker).
    def build_start(self):
        for w in self.start_frame.winfo_children():
            w.destroy()

        self.error_var.set("")
        self._pill_registry = []

        # Header (title + rules button)
        top = tk.Frame(self.start_frame, bg=self.COL_BG, padx=18, pady=16)
        top.pack(fill="x")

        tk.Label(
            top, text="Tic-Tac-Toe",
            bg=self.COL_BG, fg=self.COL_TEXT,
            font=("Helvetica", 26, "bold"),
        ).pack(side="left")

        self.flat_button(
            top, "Rules", self.show_rules_popup,
            bg=self.COL_CARD, fg=self.COL_ACCENT, hover_bg=self.COL_CARD_2
        ).pack(side="right")

        tk.Label(
            self.start_frame,
            text="Choose your settings and start a new game.",
            bg=self.COL_BG,
            fg=self.COL_MUTED,
            font=("Helvetica", 12),
        ).pack(anchor="w", padx=18, pady=(0, 12))

        # Centered card container
        card_wrap = tk.Frame(self.start_frame, bg=self.COL_BG)
        card_wrap.pack(fill="both", expand=True)

        self.card = tk.Frame(card_wrap, bg=self.COL_CARD, padx=18, pady=18)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=640, height=480)

        # Two-column grid: text on the left, controls on the right
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_columnconfigure(1, weight=0)

        def section(row, title):
            tk.Label(self.card, text=title, bg=self.COL_CARD, fg=self.COL_TEXT, font=("Helvetica", 14, "bold")).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=(0, 8)
            )

        # Mode selection
        section(0, "Mode")
        mode_row = tk.Frame(self.card, bg=self.COL_CARD)
        mode_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

        # Changing mode only refreshes the "Players" section (no full rebuild)
        self.pill(mode_row, "Vs Computer", self.mode_var, "human_vs_computer", on_change=self.refresh_mode).pack(
            side="left", padx=(0, 10)
        )
        self.pill(mode_row, "2 Players", self.mode_var, "human_vs_human", on_change=self.refresh_mode).pack(
            side="left"
        )

        # Board size + win condition
        section(2, "Board size")
        left = tk.Frame(self.card, bg=self.COL_CARD)
        left.grid(row=3, column=0, sticky="w")

        self.size_label = tk.Label(
            left,
            text=f"{self.size_var.get()} × {self.size_var.get()}",
            bg=self.COL_CARD,
            fg=self.COL_ACCENT,
            font=("Helvetica", 14, "bold"),
        )
        self.size_label.pack(anchor="w")

        tk.Label(
            left,
            text="Win condition: align N",
            bg=self.COL_CARD,
            fg=self.COL_MUTED,
            font=("Helvetica", 11),
        ).pack(anchor="w", pady=(2, 0))

        slider = tk.Scale(
            self.card,
            from_=3, to=6,
            orient="horizontal",
            variable=self.size_var,
            resolution=1,
            showvalue=False,
            length=320,
            bg=self.COL_CARD,
            fg=self.COL_TEXT,
            troughcolor=self.COL_CELL,
            highlightthickness=0,
            bd=0,
            command=self.on_size_change,
        )
        slider.grid(row=3, column=1, sticky="e", pady=(0, 18))

        # Who starts?
        section(4, "Who starts?")
        starter_row = tk.Frame(self.card, bg=self.COL_CARD)
        starter_row.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 18))
        self.pill(starter_row, "X starts", self.starter_var, "X").pack(side="left", padx=(0, 10))
        self.pill(starter_row, "O starts", self.starter_var, "O").pack(side="left")

        # Player-specific settings (rendered dynamically)
        section(6, "Players")

        self.players_form = tk.Frame(self.card, bg=self.COL_CARD)
        self.players_form.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.players_form.grid_columnconfigure(0, weight=1)
        self.players_form.grid_columnconfigure(1, weight=0)

        # Validation errors
        tk.Label(
            self.card,
            textvariable=self.error_var,
            bg=self.COL_CARD,
            fg=self.COL_DANGER,
            font=("Helvetica", 11, "bold"),
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(6, 8))

        # Start button (strong CTA)
        self.start_btn = self.flat_button(
            self.card,
            "Start game",
            self.start_game,
            bg=self.COL_ACCENT,
            fg="white",
            hover_bg=self.COL_ACCENT_HOVER,
            padx=16,
            pady=14,
            font=("Helvetica", 12, "bold"),
        )
        self.start_btn.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # Build initial mode-specific controls
        self.refresh_mode(initial=True)

        # Apply correct selection styling to pills
        self.update_pills()

    # Start screen dynamic section
    # Updates the 'Players' section based on the selected mode.
    # This avoids destroying/recreating the whole start UI (prevents slider flicker).
    def refresh_mode(self, initial=False):
        # Clear previous player rows
        for w in self.players_form.winfo_children():
            w.destroy()

        mode = self.mode_var.get()

        def row(r, label, var, options):
            tk.Label(self.players_form, text=label, bg=self.COL_CARD, fg=self.COL_MUTED, font=("Helvetica", 12)).grid(
                row=r, column=0, sticky="w", pady=8
            )
            cb = ttk.Combobox(self.players_form, textvariable=var, values=options, state="readonly", width=18)
            cb.grid(row=r, column=1, sticky="e", pady=8)
            cb.set(var.get())

        if mode == "human_vs_computer":
            row(0, "Your symbol", self.human_symbol_var, ["X", "O"])
            row(1, "Computer AI", self.ai_var, ["random", "alphabeta"])
        else:
            row(0, "Player 1 symbol", self.player1_symbol_var, ["X", "O"])
            row(1, "Player 2 symbol", self.player2_symbol_var, ["X", "O"])

        self.error_var.set("")  # clear any previous mode-specific error
        self.update_pills()

    def on_size_change(self, _):
        # Update the visible label when the slider moves
        n = int(self.size_var.get())
        self.size_label.config(text=f"{n} × {n}")


    # Start game
    # Validates settings and initializes a new Game through the controller.
    # Then builds the game screen and renders the initial board.
    def start_game(self):
        self.error_var.set("")

        mode = self.mode_var.get()
        n = int(self.size_var.get())
        k = n  # win condition: align N
        starter = self.starter_var.get()

        # Validate and start via controller
        if mode == "human_vs_human":
            p1 = self.player1_symbol_var.get()
            p2 = self.player2_symbol_var.get()
            if p1 == p2:
                self.error_var.set("Player 1 and Player 2 must choose different symbols.")
                return

            result = self.controller.start(
                mode=mode,
                n=n,
                k=k,
                starter=starter,
                player1_symbol=p1,
                player2_symbol=p2,
                ai_type="random",
            )
        else:
            result = self.controller.start(
                mode=mode,
                n=n,
                k=k,
                starter=starter,
                human_symbol=self.human_symbol_var.get(),
                ai_type=self.ai_var.get(),
            )

        # Build and show the game screen
        self.build_game()
        self.render()
        self.status_var.set(result.status)
        self.show_game()

        if result.game_over:
            self.disable_board()

    # Game screen
    # Build the in-game UI: status line, rules/restart actions, and the NxN grid.
    # Cell buttons call controller.click(idx). Rendering happens in _render().
    def build_game(self):
        for w in self.game_frame.winfo_children():
            w.destroy()

        top = tk.Frame(self.game_frame, bg=self.COL_BG, padx=18, pady=14)
        top.pack(fill="x")

        # Status line (whose turn / win / draw)
        self.status_var = tk.StringVar(value="")
        tk.Label(
            top,
            textvariable=self.status_var,
            bg=self.COL_BG,
            fg=self.COL_TEXT,
            font=("Helvetica", 14, "bold"),
        ).pack(side="left")

        # Actions on the right
        right = tk.Frame(top, bg=self.COL_BG)
        right.pack(side="right")

        self.flat_button(
            right, "Rules", self.show_rules_popup,
            bg=self.COL_CARD, fg=self.COL_ACCENT, hover_bg=self.COL_CARD_2
        ).pack(side="left", padx=(0, 10))

        self.flat_button(
            right, "Restart", self.show_start,
            bg=self.COL_CARD_2, fg=self.COL_TEXT, hover_bg=self.COL_CARD
        ).pack(side="left")

        # Grid area
        board_wrap = tk.Frame(self.game_frame, bg=self.COL_BG, padx=18, pady=18)
        board_wrap.pack(fill="both", expand=True)

        n = self.controller.game.n
        grid = tk.Frame(board_wrap, bg=self.COL_BG)
        grid.pack(expand=True)

        self.buttons = []

        # Tile sizing: keep cells readable across multiple board sizes
        if n <= 3:
            pad = 12
            font_size = 34
            ipadx, ipady = 28, 20
        elif n == 4:
            pad = 10
            font_size = 30
            ipadx, ipady = 24, 18
        else:
            pad = 8
            font_size = 26
            ipadx, ipady = 20, 16

        for r in range(n):
            for c in range(n):
                idx = r * n + c
                b = tk.Button(
                    grid,
                    text="",
                    command=lambda i=idx: self.on_cell(i),
                    bg="#0f172a",
                    activebackground="#1e293b",
                    fg=self.COL_TEXT,
                    bd=0,
                    relief="flat",
                    highlightthickness=2,
                    highlightbackground=self.COL_CARD,
                    font=("Helvetica", font_size, "bold"),
                    cursor="hand2",
                    width=2,
                    height=1,
                )
                b.grid(row=r, column=c, padx=pad, pady=pad, ipadx=ipadx, ipady=ipady)
                self.buttons.append(b)

    # User interaction
    # Handle a click on a grid cell, then re-render and update the status label.
    def on_cell(self, idx: int):
        result = self.controller.click(idx)
        self.render()
        self.status_var.set(result.status)
        if result.game_over:
            self.disable_board()

    # Rendering
    # Render controller.game.board into button text/colors.
    # X is blue and O is red for clear contrast.
    def render(self):
        for i, v in enumerate(self.controller.game.board):
            btn = self.buttons[i]

            if v == "X":
                btn.config(
                    text="X",
                    fg="#3b82f6",
                    disabledforeground="#3b82f6"
                )
            elif v == "O":
                btn.config(
                    text="O",
                    fg="#ef4444",
                    disabledforeground="#ef4444"
                )
            else:
                btn.config(text="")

    # End of game
    # Disable all grid buttons once the game ends.
    def disable_board(self):
        for b in self.buttons:
            b.config(state="disabled")