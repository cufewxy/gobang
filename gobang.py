import json
from datetime import datetime

import numpy as np

BOARD_SIZE = 10


class GoBangBoard:
    """
    棋盘
    """

    def __init__(self):
        self.position = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # 当前棋盘位置
        self.round_num = 0  # 已对局轮数

    def put(self, player, position):
        """
        落子
        """
        row, column = position
        assert 0 <= row <= BOARD_SIZE
        assert 0 <= column <= BOARD_SIZE
        if self.position[row][column] != 0:
            raise ValueError(f"{row,column}处已有棋子")
        self.position[row][column] = player
        self.round_num += 1

    def print_board(self):
        """
        打印当前棋盘
        """
        print(np.array(self.position))


class GoBangGame:
    """
    属性:
    board: 棋盘. 可使用ui类将此棋盘通过tkinter展示
    cur_player: 当前需要落子的玩家
    history_actions: 对弈历史动作
    result: None, 1, 2, 0. 分别表示:对局进行中、玩家1胜、玩家2胜、和棋
    start_time: 开始时间

    函数:
    dump: 对局结束后, 将对弈历史动作保存下来. 不考虑和棋
    proceed: 继续对局, 玩家1、2交替进行
    check_end: 判断对局是否结束(获胜或和棋)
    """

    def __init__(self):
        self.start_time = datetime.now().strftime("%Y%m%d%H%M%S")
        self.cur_player = 1
        self.history_actions = []
        self.result = None
        self.board = GoBangBoard()

    def reset(self):
        self.__init__()

    def dump(self):
        """
        将对局保存
        """
        if self.result is None:
            raise ValueError("对局未结束无法保存")
        if self.result == 0:
            return
        with open(f"data/{self.start_time[:8]}", "a") as f:
            f.write(json.dumps(self.history_actions) + ";" + str(self.result) + "\n")
            # json.dump(self.history_actions, f)

    def proceed(self, position: [int, int], is_dump=0):
        """
        Args:
            position: 落子位置

        Returns:

        """
        if self.result is not None:
            raise ValueError("对局已结束, 无法落子")
        self.board.put(self.cur_player, position)
        self.history_actions.append(position)
        self.result, _ = self.check_winner(self.board.position, self.cur_player)
        if self.result is not None:
            print(f"胜者为{self.cur_player}")
            if is_dump:
                self.dump()
            return
        self.cur_player = 1 if self.cur_player == 2 else 2  # 切换玩家

    # @staticmethod
    # def check_end_scan_row(df, n=5):
    #     """
    #     查看每一行有没有连续n个数字重复的情况
    #     """
    #     rolling_sum = df.T.rolling(window=n).sum()
    #     return (rolling_sum == 5).sum().sum() > 0
    #
    # @staticmethod
    # def diagonal_trans(matrix):
    #     """
    #     将矩阵顺时针旋转45度, 每一条斜线上的元素组成新的一行元素
    #     例如原矩阵为
    #     [[1, 2, 3],
    #      [4, 5, 6],
    #      [7, 8, 9]]
    #     新矩阵为
    #     [[1, 0, 0],
    #      [4, 2, 0],
    #      [7, 5, 3],
    #      [8, 6, 0],
    #      [9, 0, 0]]
    #     """
    #     n = len(matrix) * 2 - 1
    #     new_matrix = [[0 for _ in range(n)] for _ in range(n)]
    #     for i in range(len(matrix)):
    #         for j in range(len(matrix[0])):
    #             if i + j < len(matrix):
    #                 col = j
    #             else:
    #                 col = len(matrix) - i - 1
    #             new_matrix[i + j][col] = matrix[i][j]
    #     return new_matrix
    #
    # @classmethod
    # def check_winner(cls, board, player, n=5):
    #     """
    #     判断棋局胜者
    #     (1) 判断横竖斜线是否有连续5个1或者2
    #     (2) 判断当前棋盘是否已满
    #     """
    #     df = pd.DataFrame(board.position)
    #     # 横向判断
    #     df_mask = pd.DataFrame(df == player).astype(int)
    #     check_res = cls.check_end_scan_row(df_mask, n)
    #     if check_res:
    #         return player
    #     # 纵向判断
    #     check_res = cls.check_end_scan_row(df_mask.T, n)
    #     if check_res:
    #         return player
    #     # 左下右上斜向判断
    #     mask_list = df_mask.values.tolist()
    #     df_mask_new = cls.diagonal_trans(mask_list)
    #     check_res = cls.check_end_scan_row(pd.DataFrame(df_mask_new), n)
    #     if check_res:
    #         return player
    #     # 左上右下斜向判断
    #     mask_list_symmetry = [line[::-1] for line in mask_list]  # 对矩阵做对称处理
    #     df_mask_symmetry = cls.diagonal_trans(mask_list_symmetry)
    #     check_res = cls.check_end_scan_row(pd.DataFrame(df_mask_symmetry))
    #     if check_res:
    #         return player
    #     # 棋盘已满判断
    #     if board.round_num == BOARD_SIZE * BOARD_SIZE:
    #         return 0

    @classmethod
    def check_winner(cls, board_position, player, n=5):
        """
        判断是否n个棋子相连
        返回所有连续的位置列表,包括[连续类型,起点坐标,终点坐标]
        其中连续类型取值范围是1-4,分别代表横向,纵向,左上右下斜向,左下右上斜向
        """
        con_list = []
        # 横向类型
        con_type = 1
        a = np.array(board_position)
        for i in range(len(a)):
            for j in range(len(a[0]) - n + 1):
                if np.all(a[i, j:j + n] == player):
                    con_list.append([con_type, [i, j], [i, j + n - 1]])
        # 纵向类型
        con_type = 2
        for i in range(len(a) - n + 1):
            for j in range(len(a[0])):
                if np.all(a[i:i + n, j] == player):
                    con_list.append([con_type, [i, j], [i + n - 1, j]])
        # 左上右下斜向类型
        con_type = 3
        for i in range(len(a)):
            for j in range(len(a[0])):
                begin = a[i, j]
                neighbors = [begin]
                for k in range(1, n):
                    x = i + k
                    y = j + k
                    if x >= len(a[0]) or y >= len(a):
                        break
                    neighbors.append(a[x, y])
                if np.all(np.array(neighbors) == player) and len(neighbors) == n:
                    con_list.append([con_type, [i, j], [i + n - 1, j + n - 1]])
        # 左下右上斜向类型
        con_type = 4
        for i in range(len(a)):
            for j in range(len(a[0])):
                begin = a[i, j]
                neighbors = [begin]
                for k in range(1, n):
                    x = i - k
                    y = j + k
                    if x < 0 or y >= len(a):
                        break
                    neighbors.append(a[x, y])
                if np.all(np.array(neighbors) == player) and len(neighbors) == n:
                    con_list.append([con_type, [i, j], [i - n + 1, j + n - 1]])
        winner = None
        if len(con_list) > 0:
            winner = player
        elif (np.array(board_position) == 0).sum() == 0:
            winner = 0  # 和棋
        return winner, con_list


if __name__ == '__main__':
    # 胜负测试
    game = GoBangGame()
    # 未分出胜负场景
    board = [[1, 0, 0, 0, 1, 0],
             [0, 1, 0, 0, 1, 0],
             [0, 0, 1, 0, 0, 0],
             [0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0]]
    res, _ = game.check_winner(board, 1)
    print(res)
    # 横向五连子
    board = [[2, 2, 2, 2, 2, 0],
             [0, 1, 0, 0, 1, 0],
             [0, 0, 0, 0, 1, 0],
             [0, 0, 0, 1, 1, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0]]
    res, _ = game.check_winner(board, 2)
    print(res)
    # 纵向五连子
    board = [[1, 0, 0, 0, 1, 0],
             [0, 1, 0, 0, 1, 0],
             [0, 0, 0, 0, 1, 0],
             [0, 0, 0, 1, 1, 0],
             [0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0]]
    res, _ = game.check_winner(board, 1)
    print(res)
    # 斜向五连子
    board = [[1, 0, 0, 0, 1, 0],
             [0, 1, 0, 0, 1, 0],
             [0, 0, 1, 0, 0, 0],
             [0, 0, 0, 1, 1, 0],
             [0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0]]
    res, _ = game.check_winner(board, 1)
    print(res)
    # 斜向五连子
    board = [[1, 0, 0, 0, 2, 0],
             [0, 1, 0, 2, 0, 0],
             [0, 0, 2, 0, 0, 0],
             [0, 2, 0, 0, 1, 0],
             [2, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0]]
    res, _ = game.check_winner(board, 2)
    print(res)
    # 对局过程测试
    g = GoBangGame()
    g.proceed([0, 0])
    g.proceed([0, 1])
    g.proceed([1, 1])
    g.proceed([0, 2])
    g.proceed([2, 2])
    g.proceed([0, 3])
    g.proceed([3, 3])
    g.proceed([0, 4])
    g.proceed([4, 4])
    g.board.print_board()
    # 测试结束后无法落子
    # g.proceed([0, 5])
    # 测试无法落同一个位置
    # g = GoBangGame()
    # g.proceed([0, 0])
    # g.proceed([0, 0])
