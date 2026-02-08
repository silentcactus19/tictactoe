import tkinter as tk
from tkinter import ttk

from controller import GameController


class TicTacToeUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.resizable(False, False)

        self.controller = GameController()

        self.container = ttk.Frame(self, padding=12)
        self.container.grid(row=0, column=0)

        self.start_frame = ttk.Frame(self.container)
        self.game_frame = ttk.Frame(self.container)

        # Settings
        self.mode_var = tk.StringVar(value="human_vs_computer")
        self.size_var = tk.IntVar(value=3)
        self.starter_var = tk.StringVar(value="X")

        # HVC
        self.human_symbol_var = tk.StringVar(value="X")
        self.ai_var = tk.StringVar(value="random")  # "random" or "alphabeta"

        # HVH
        self.player1_symbol_var = tk.StringVar(value="X")
        self.player2_symbol_var = tk.StringVar(value="O")

        self.error_var = tk.StringVar(value="")

        self._build_start()
        self._show_start()

    def _show_start(self):
        self.game_frame.grid_forget()
        self.start_frame.grid(row=0, column=0)

    def _show_game(self):
        self.start_frame.grid_forget()
        self.game_frame.grid(row=0, column=0)

    def _on_mode_change(self, *_):
        self.error_var.set("")
        self._build_start()

    def _build_start(self):
        for w in self.start_frame.winfo_children():
            w.destroy()

        self.error_var.set("")

        ttk.Label(self.start_frame, text="Tic-Tac-Toe", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        ttk.Label(self.start_frame, text="Game mode:").grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.OptionMenu(
            self.start_frame,
            self.mode_var,
            self.mode_var.get(),
            "human_vs_computer",
            "human_vs_human",
            command=self._on_mode_change,
        ).grid(row=1, column=1, sticky="e", pady=(0, 8))

        ttk.Label(self.start_frame, text="Board size (N×N):").grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.OptionMenu(self.start_frame, self.size_var, self.size_var.get(), 3, 4, 5, 6).grid(
            row=2, column=1, sticky="e", pady=(0, 8)
        )

        ttk.Label(self.start_frame, text="Who starts:").grid(row=3, column=0, sticky="w", pady=(0, 8))
        ttk.OptionMenu(self.start_frame, self.starter_var, self.starter_var.get(), "X", "O").grid(
            row=3, column=1, sticky="e", pady=(0, 8)
        )

        mode = self.mode_var.get()

        if mode == "human_vs_computer":
            ttk.Label(self.start_frame, text="Your symbol:").grid(row=4, column=0, sticky="w", pady=(0, 8))
            ttk.OptionMenu(self.start_frame, self.human_symbol_var, self.human_symbol_var.get(), "X", "O").grid(
                row=4, column=1, sticky="e", pady=(0, 8)
            )

            ttk.Label(self.start_frame, text="Computer AI:").grid(row=5, column=0, sticky="w", pady=(0, 8))
            ttk.OptionMenu(self.start_frame, self.ai_var, self.ai_var.get(), "random", "alphabeta").grid(
                row=5, column=1, sticky="e", pady=(0, 8)
            )

            next_row = 6
        else:
            ttk.Label(self.start_frame, text="Player 1 symbol:").grid(row=4, column=0, sticky="w", pady=(0, 8))
            ttk.OptionMenu(self.start_frame, self.player1_symbol_var, self.player1_symbol_var.get(), "X", "O").grid(
                row=4, column=1, sticky="e", pady=(0, 8)
            )

            ttk.Label(self.start_frame, text="Player 2 symbol:").grid(row=5, column=0, sticky="w", pady=(0, 8))
            ttk.OptionMenu(self.start_frame, self.player2_symbol_var, self.player2_symbol_var.get(), "X", "O").grid(
                row=5, column=1, sticky="e", pady=(0, 8)
            )

            next_row = 6

        ttk.Label(self.start_frame, textvariable=self.error_var, foreground="red").grid(
            row=next_row, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )

        ttk.Button(self.start_frame, text="Start game", command=self._start_game).grid(
            row=next_row + 1, column=0, columnspan=2, pady=(10, 0)
        )

    def _start_game(self):
        self.error_var.set("")

        mode = self.mode_var.get()
        n = int(self.size_var.get())
        k = n
        starter = self.starter_var.get()

        if mode == "human_vs_human":
            p1 = self.player1_symbol_var.get()
            p2 = self.player2_symbol_var.get()
            if p1 == p2:
                self.error_var.set("Error: Player 1 and Player 2 must choose different symbols.")
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
            human_symbol = self.human_symbol_var.get()
            ai_type = self.ai_var.get()

            result = self.controller.start(
                mode=mode,
                n=n,
                k=k,
                starter=starter,
                human_symbol=human_symbol,
                ai_type=ai_type,
            )

        self._build_board()
        self._render()
        self.status_var.set(result.status)
        self._show_game()

        if result.game_over:
            self._disable_board()

    def _build_board(self):
        for w in self.game_frame.winfo_children():
            w.destroy()

        top = ttk.Frame(self.game_frame)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.status_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        ttk.Button(top, text="Restart", command=self._show_start).grid(row=0, column=1, padx=(12, 0))
        top.columnconfigure(0, weight=1)

        grid = ttk.Frame(self.game_frame)
        grid.grid(row=1, column=0)

        n = self.controller.game.n
        self.buttons = []
        for r in range(n):
            for c in range(n):
                idx = r * n + c
                b = ttk.Button(grid, text=" ", width=4, command=lambda i=idx: self._on_cell(i))
                b.grid(row=r, column=c, padx=2, pady=2)
                self.buttons.append(b)

    def _on_cell(self, idx: int):
        result = self.controller.click(idx)
        self._render()
        self.status_var.set(result.status)
        if result.game_over:
            self._disable_board()

    def _render(self):
        for i, v in enumerate(self.controller.game.board):
            self.buttons[i].config(text=v if v else " ")

    def _disable_board(self):
        for b in self.buttons:
            b.state(["disabled"])