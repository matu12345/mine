# Minesweeper

This repository contains a simple Minesweeper game implemented with Tkinter.

## Usage

Run the game with Python 3. You can choose a difficulty level on the command line:

```bash
python3 minesweeper.py easy   # 9x9 board with 10 mines
python3 minesweeper.py medium # 16x16 board with 40 mines
python3 minesweeper.py hard   # 16x30 board with 99 mines
```

Left click to open a cell and right click to toggle a flag. Use the **AI Step** button to let the built-in solver make a single move. After each AI action a message box will explain the move.
