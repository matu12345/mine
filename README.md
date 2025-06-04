# マインスイーパー

このリポジトリには Tkinter を用いた簡単なマインスイーパーゲームが含まれています。

## 使い方

Python 3 で実行します。コマンドラインから難易度を指定できます。

```bash
python3 minesweeper.py easy   # 初級  9x9 マス / 地雷 10 個
python3 minesweeper.py medium # 中級 16x16 マス / 地雷 40 個
python3 minesweeper.py hard   # 上級 16x30 マス / 地雷 99 個
```

左クリックでマスを開き、右クリックで旗を立てます。**AI 一手**ボタンを押すと AI が一手だけ考えて行動し、その理由をメッセージ表示します。
