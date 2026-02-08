# Tic-Tac-Toe (Python / Tkinter)

This project is a Tic-Tac-Toe application developed in Python with a graphical interface using Tkinter.

The objective of this project is to demonstrate:
- clean architecture and separation of concerns
- scalable game logic
- readable and maintainable code
- ability to evolve both UI and technical components with minimal changes

---

## Features

- **Game modes**
  - Human vs Computer
    - Random AI (baseline, required)
    - Smart AI using Alpha–Beta pruning (optional)
  - Human vs Human (local two-player mode)

- **Board configuration**
  - Board size selectable from 3×3 up to 6×6
  - Win condition: align N symbols (N = board size)
  - Restart a game without restarting the application

- **User Interface**
  - Graphical interface built with Tkinter
  - Start screen with full configuration (mode, board size, symbols, AI)
  - In-game controls (restart, rules popup)
  - Clear visual contrast for moves (X and O)

---

## Project structure

```text
.
├── main.py
├── ui.py
├── controller.py
├── game.py
├── ai.py
├── requirements.txt
└── README.md
```


---

## Architecture overview

- **game.py**
  - Contains only the game state and rules
  - Generic implementation for any N×N board and win condition K
  - No UI, no AI logic

- **ai.py**
  - Random AI (baseline implementation)
  - Smart AI using alpha–beta pruning with:
    - heuristic evaluation
    - move ordering
    - time-bounded search
  - Works for different board sizes

- **controller.py**
  - Central orchestration layer
  - Handles game flow, turns, and AI triggering
  - Acts as the interface between UI and game logic

- **ui.py**
  - Handles all rendering and user interaction
  - Contains no game rules or AI logic
  - Communicates only with the controller

This separation allows fast evolution of the interface or game logic with minimal modifications.

---

## Requirements
This project uses only the Python standard library
Requires Python 3.10 or newer

---

## How to run

After installing the requirements, run:

```bash
python main.py



