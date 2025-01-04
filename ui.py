import random
import time
import tkinter as tk
from tkinter import messagebox

from ai_strategy.mcts_strategy import MCTSStrategy
from ai_strategy.random_strategy import RandomStrategy
from ai_strategy.rule_strategy import RuleStrategy
from gobang import BOARD_SIZE, GoBangGame

PADDING = 30  # 棋盘边距
GRID_SIZE = 20  # 每个格子的大小

AI = "mcts"
if AI == "random":
    ai_strategy = RandomStrategy()
elif AI == "rule":
    ai_strategy = RuleStrategy()
elif AI == "mcts":
    ai_strategy = MCTSStrategy()
else:
    ai_strategy = None


class GoBangUI:
    window = None
    game_frame = None
    canvas = None
    label = None
    g = None
    id_list = []
    human_player = None
    ai_player = None

    def __init__(self, play_mode="pvp", ai_strategy=None):
        """

        Args:
            play_mode: pvp和pve
            ai_strategy: 如果是pve, 需要传入一个ai_strategy
        """
        self.play_mode = play_mode
        self.ai_strategy = ai_strategy
        self.create_window()
        self.create_canvas()
        self.create_label()
        self.pack()

    def create_window(self):
        # 创建窗口
        self.window = tk.Tk()  # 声明窗口
        self.window.title("五子棋")  # 声明窗口标题
        # 根据棋盘格子计算得到窗口的适宜宽高
        self.window.geometry(
            str(BOARD_SIZE * GRID_SIZE + PADDING * 2) + "x" + str(BOARD_SIZE * GRID_SIZE + PADDING * 2 + 40))
        self.window.configure(bg='burlywood')  # 设置窗口背景颜色

        # 创建游戏页面
        self.game_frame = tk.Frame(self.window)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.game_frame, width=BOARD_SIZE * GRID_SIZE + PADDING * 2,
                                height=BOARD_SIZE * GRID_SIZE + PADDING * 2,
                                bg="burlywood")

        self.canvas.pack(pady=PADDING)
        # 绘制棋盘线
        for i in range(BOARD_SIZE):
            self.canvas.create_line(PADDING, i * GRID_SIZE + PADDING, BOARD_SIZE * GRID_SIZE + PADDING - GRID_SIZE,
                                    i * GRID_SIZE + PADDING)
        for i in range(BOARD_SIZE):
            self.canvas.create_line(i * GRID_SIZE + PADDING, PADDING, i * GRID_SIZE + PADDING,
                                    BOARD_SIZE * GRID_SIZE + PADDING - GRID_SIZE)

        # 绘制棋盘上的黑点
        for i in range(3, BOARD_SIZE, 6):
            for j in range(3, BOARD_SIZE, 6):
                self.canvas.create_oval(j * GRID_SIZE + PADDING - 3, i * GRID_SIZE + PADDING - 3,
                                        j * GRID_SIZE + PADDING + 3, i * GRID_SIZE + PADDING + 3, fill="black")
        self.canvas.bind("<Button-1>", self.on_click)  # 左键点击

    def create_label(self):
        self.label = tk.Label(self.window, text="黑子回合", font=("宋体", 14))
        self.label.place(x=PADDING, y=PADDING * 2 + BOARD_SIZE * GRID_SIZE + 10)

    def pack(self):
        self.game_frame.pack()

    def put(self, row, col):
        if self.g.cur_player == 1:  # 黑方玩家
            color = "black"
            self.label.config(text="白子回合")
        else:  # 白方玩家
            color = "white"
            self.label.config(text="黑子回合")
        x = col * GRID_SIZE + PADDING  # 计算棋子中心x坐标
        y = row * GRID_SIZE + PADDING  # 计算棋子中心y坐标
        self.id_list.append(
            self.canvas.create_oval(x - GRID_SIZE // 2, y - GRID_SIZE // 2, x + GRID_SIZE // 2, y + GRID_SIZE // 2,
                                    fill=color))  # 绘制棋子
        self.g.proceed([row, col])

    def ai_put(self):
        time.sleep(0.2)
        row, col = self.ai_strategy.model(self.g.board.position, self.ai_player)
        self.put(row, col)

    def reset_canvas(self):
        for id in self.id_list:
            self.canvas.delete(id)
        self.id_list = []

    def on_click(self, event):
        # 处理鼠标点击事件
        row = round((event.y - PADDING) / GRID_SIZE)  # 计算点击位置的行
        col = round((event.x - PADDING) / GRID_SIZE)  # 计算点击位置的列
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
            # 落子在棋盘外侧
            messagebox.showinfo("提示", "不可以在棋盘外落子！")
            return
        if self.g.board.position[row][col] != 0:
            # 提示落子位置已有棋子
            messagebox.showinfo("提示", "此处已有棋子")
            return

        self.put(row, col)
        if self.g.result is None:
            if self.play_mode == "pve":
                self.ai_put()
        if self.g.result is not None:
            if self.g.result == 1:
                messagebox.showinfo("游戏结束", "黑子获胜")
            elif self.g.result == 2:
                messagebox.showinfo("游戏结束", "白子获胜")
            else:
                messagebox.showinfo("游戏结束", "和棋")
            # window.quit()
            time.sleep(1)
            self.reset_canvas()
            ai_strategy.reset()
            self.start_new_game()

    def start_new_game(self):
        if self.play_mode == "pve":
            self.human_player = random.choice([1, 2])
            self.ai_player = 2 if self.human_player == 1 else 1
        self.g = GoBangGame()

    def run(self):
        self.start_new_game()
        self.window.mainloop()


if __name__ == '__main__':
    # PVP
    g = GoBangUI()
    g.run()
    # PVE
    g = GoBangUI("pve", ai_strategy)
    g.run()
