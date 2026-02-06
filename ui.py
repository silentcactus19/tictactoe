import tkinter as tk
from tkinter import ttk
from controller import GameController

class TicTacToeUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.resizable(False, False)

        self.controller = GameController(n=3, k=3)

        self.container = ttk.Frame(self, padding=12)
        self.container.grid(row=0, column=0)

        self.start_frame = ttk.Frame(self.container)
        self.game_frame = ttk.Frame(self.container)

        # New: who starts (default X starts - standard rule)
        self.starter_var = tk.StringVar(value="X")

        self._build_start()
        self._show_start()

    def _show_start(self):
        self.game_frame.grid_forget()
        self.start_frame.grid(row=0, column=0)

    def _show_game(self):
        self.start_frame.grid_forget()
        self.game_frame.grid(row=0, column=0)

    def _build_start(self):
        for w in self.start_frame.winfo_children():
            w.destroy()

        ttk.Label(
            self.start_frame,
            text="Choose your symbol",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Who starts dropdown
        ttk.Label(self.start_frame, text="Who starts?").grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.OptionMenu(self.start_frame, self.starter_var, self.starter_var.get(), "X", "O").grid(
            row=1, column=1, sticky="e", pady=(0, 8)
        )

        # Play buttons
        ttk.Button(
            self.start_frame,
            text="Play as X",
            command=lambda: self._start_game("X")
        ).grid(row=2, column=0, padx=6)

        ttk.Button(
            self.start_frame,
            text="Play as O",
            command=lambda: self._start_game("O")
        ).grid(row=2, column=1, padx=6)

    def _start_game(self, human_symbol: str):
        starter = self.starter_var.get()  # "X" or "O"
        result = self.controller.start(human_symbol, starter=starter)

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
        ttk.Button(top, text="Rejouer", command=self._show_start).grid(row=0, column=1, padx=(12, 0))
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
        result = self.controller.human_click(idx)
        self._render()
        self.status_var.set(result.status)
        if result.game_over:
            self._disable_board()

    def _render(self):
        board = self.controller.game.board
        for i, v in enumerate(board):
            self.buttons[i].config(text=v if v else " ")

    def _disable_board(self):
        for b in self.buttons:
            b.state(["disabled"])