"""Tkinter を用いたマインスイーパー"""

import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

class Minesweeper(tk.Frame):
    """簡単なマインスイーパーゲーム"""

    # 難易度ごとの盤面サイズと地雷数
    DIFFICULTIES = {
        'easy': (9, 9, 10),
        'medium': (16, 16, 40),
        'hard': (16, 30, 99)
    }

    BEST_FILE = 'best_times.json'

    def load_best_times(self):
        if os.path.exists(self.BEST_FILE):
            with open(self.BEST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {lvl: [] for lvl in self.DIFFICULTIES}

    def save_best_times(self):
        with open(self.BEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.best_times, f, ensure_ascii=False, indent=2)

    def format_best_times(self):
        times = self.best_times.get(self.level, [])
        if times:
            return 'ベスト: ' + ', '.join(str(t) for t in times[:5])
        return 'ベスト: なし'

    def update_best_label(self):
        self.best_label.config(text=self.format_best_times())

    def __init__(self, master, level='easy'):
        super().__init__(master)
        self.master.title('マインスイーパー')
        self.level = level
        self.rows, self.cols, self.mines = self.DIFFICULTIES[level]
        self.buttons = {}
        self.flags = set()
        self.revealed = set()
        self.values = [[0]*self.cols for _ in range(self.rows)]
        self.game_over = False
        self.start_time = time.time()
        self.used_ai = False
        self.best_times = self.load_best_times()
        self.create_widgets()
        self.place_mines()
        self.calculate_values()
        self.update_timer()

    def create_widgets(self):
        top = tk.Frame(self)
        top.pack()
        self.info = tk.Label(top, text=f'旗: 0/{self.mines}')
        self.info.pack(side=tk.LEFT)
        self.timer_label = tk.Label(top, text='時間: 0秒')
        self.timer_label.pack(side=tk.LEFT, padx=10)
        self.ai_steps = tk.IntVar(value=1)
        tk.OptionMenu(top, self.ai_steps, 1, 3, 5, 10, 0).pack(side=tk.LEFT)
        tk.Button(top, text='AI実行', command=self.start_ai).pack(side=tk.LEFT)
        self.best_label = tk.Label(top, text=self.format_best_times())
        self.best_label.pack(side=tk.LEFT, padx=10)
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack()
        # 旗用の画像を生成
        self.flag_image = tk.PhotoImage(width=16, height=16)
        self.flag_image.put('black', to=(0,2,2,14))  # ポール
        for x in range(3,13):
            height = (x-3)//2 + 1
            self.flag_image.put('red', to=(x,3,x+1,3+height))
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(
                    self.grid_frame,
                    width=2,
                    height=1,
                    bg='light blue',
                    command=lambda r=r, c=c: self.open_cell(r, c))
                btn.bind('<Button-3>', lambda e, r=r, c=c: self.toggle_flag(r, c))
                btn.grid(row=r, column=c)
                self.buttons[(r, c)] = btn
        self.pack()

    def place_mines(self):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        for r, c in random.sample(positions, self.mines):
            self.values[r][c] = 'M'

    def calculate_values(self):
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.values[r][c] == 'M':
                    continue
                count = 0
                for dr, dc in dirs:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and self.values[nr][nc] == 'M':
                        count += 1
                self.values[r][c] = count

    def update_timer(self):
        if not self.game_over:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f'時間: {elapsed}秒')
            self.after(1000, self.update_timer)

    def open_cell(self, r, c):
        if (r, c) in self.revealed or (r, c) in self.flags:
            return
        btn = self.buttons[(r, c)]
        if self.values[r][c] == 'M':
            btn.config(text='*', bg='red')
            self.game_over = True
            elapsed = int(time.time() - self.start_time)
            messagebox.showinfo('ゲームオーバー', f'地雷を踏みました！\n経過時間: {elapsed}秒')
            self.master.destroy()
            return
        self.reveal(r, c)
        self.check_win()

    def reveal(self, r, c):
        if (r, c) in self.revealed or (r, c) in self.flags:
            return
        btn = self.buttons[(r, c)]
        val = self.values[r][c]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED, bg='light gray', text=str(val) if val else '')
        self.revealed.add((r, c))
        if val == 0:
            for nr in range(r-1, r+2):
                for nc in range(c-1, c+2):
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if (nr, nc) != (r, c):
                            self.reveal(nr, nc)

    def toggle_flag(self, r, c):
        if (r, c) in self.revealed:
            return
        btn = self.buttons[(r, c)]
        if (r, c) in self.flags:
            self.flags.remove((r, c))
            btn.config(image='', text='', bg='light blue')
        else:
            self.flags.add((r, c))
            btn.config(image=self.flag_image)
        self.info.config(text=f'旗: {len(self.flags)}/{self.mines}')

    def check_win(self):
        if len(self.revealed) == self.rows*self.cols - self.mines:
            self.game_over = True
            elapsed = int(time.time() - self.start_time)
            if not self.used_ai:
                times = self.best_times.get(self.level, [])
                times.append(elapsed)
                times.sort()
                self.best_times[self.level] = times[:5]
                self.save_best_times()
                self.update_best_label()
            messagebox.showinfo('クリア', f'おめでとう！\n経過時間: {elapsed}秒')
            self.master.destroy()

    def neighbors(self, r, c):
        result = []
        for nr in range(r-1, r+2):
            for nc in range(c-1, c+2):
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) != (r, c):
                        result.append((nr, nc))
        return result

    def start_ai(self):
        self.used_ai = True
        steps = self.ai_steps.get()
        if steps == 0:
            self.run_ai_until_done()
        else:
            self.step_count = steps
            self.run_ai_steps()

    def run_ai_steps(self):
        if self.game_over or self.step_count <= 0:
            return
        self.ai_step()
        self.step_count -= 1
        if self.step_count > 0 and not self.game_over:
            self.after(100, self.run_ai_steps)

    def run_ai_until_done(self):
        if self.game_over:
            return
        self.ai_step()
        if not self.game_over:
            self.after(100, self.run_ai_until_done)

    def ai_step(self):
        explanation = ''
        action_taken = False
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in self.revealed:
                    continue
                val = self.values[r][c]
                neigh = self.neighbors(r, c)
                unopened = [n for n in neigh if n not in self.revealed and n not in self.flags]
                flagged = [n for n in neigh if n in self.flags]
                if val - len(flagged) == len(unopened) and unopened:
                    for n in unopened:
                        self.toggle_flag(*n)
                    explanation = f'{r},{c} の周囲はすべて地雷と判断しました。'
                    action_taken = True
                    break
                if len(flagged) == val and unopened:
                    self.open_cell(*unopened[0])
                    explanation = f'{r},{c} 周辺の条件を満たしたため {unopened[0]} は安全です。'
                    action_taken = True
                    break
            if action_taken:
                break
        if not action_taken:
            unopened = [(r, c) for r in range(self.rows) for c in range(self.cols)
                        if (r, c) not in self.revealed and (r, c) not in self.flags]
            if unopened:
                choice = random.choice(unopened)
                self.open_cell(*choice)
                explanation = f'確定手がないので {choice} をランダムに開けました。'
        if explanation:
            messagebox.showinfo('AI 一手', explanation)

if __name__ == '__main__':
    import sys
    level = 'easy'
    if len(sys.argv) > 1:
        level = sys.argv[1]
    root = tk.Tk()
    game = Minesweeper(root, level)
    root.mainloop()
