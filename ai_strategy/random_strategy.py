import random

from ai_base import AIStrategy


class RandomStrategy(AIStrategy):
    """
    随机模型
    """

    def model(self, cur_board, ai_player):
        empty_list = []
        for i in range(len(cur_board)):
            for j in range(len(cur_board)):
                if cur_board[i][j] == 0:
                    empty_list.append([i, j])
        res = random.choice(empty_list)
        return res
