import random

import numpy as np

from ai_base import AIStrategy
from ai_strategy.random_strategy import RandomStrategy
from gobang import GoBangGame


class RuleStrategy(AIStrategy):
    """
    基于规则的模型
    (1)当我方有4个棋子相连且一头为空时,落到其中一头
    (2)当对手有4个棋子相连且一头为空时,堵住连珠
    (3)当我方有3个棋子相连且两头为空时,落到其中一头.优先落到连续空位置大于1的一头(例如OOXXXO,X表示棋子,O表示空位置,应该落到左侧),如果都是1个空位置则任选一头
    (4)当对手有3个棋子相连且两头为空,落到其中一头.其中至少有一头的空位置大于1,否则没必要堵住(例如OXXXO)
    (5)不符合上述所有情况,则随机选择位置
    """

    def __init__(self):
        self.board = None
        self.ai_player = None
        self.human_player = None

    def check_boarder(self, point):
        """检查是否在边界内"""
        x, y = point
        return (0 <= x <= len(self.board[0]) - 1) & (0 <= y <= len(self.board[0]) - 1)

    def check_point_empty(self, point):
        """检查当前点是否为空"""
        if self.check_boarder(point) is False:
            return False
        x, y = point
        return self.board[x][y] == 0

    def rule1(self, n=4):
        # 寻找我方四连棋子
        game = GoBangGame()
        winner, con_list = game.check_winner(self.board, self.ai_player, n)
        if winner == self.ai_player:
            new_points = []
            for con_type, (x1, y1), (x2, y2) in con_list:
                if con_type == 1:
                    new_points += [(x1, y1 - 1), (x2, y2 + 1)]
                elif con_type == 2:
                    new_points += [(x1 - 1, y1), (x2 + 1, y2)]
                elif con_type == 3:
                    new_points += [(x1 - 1, y1 - 1), (x2 + 1, y2 + 1)]
                elif con_type == 4:
                    new_points += [(x1 + 1, y1 - 1), (x2 - 1, y2 + 1)]
            for point in new_points:
                if self.check_point_empty(point):
                    return point

    def rule2(self, n=4):
        # 寻找4个相连
        game = GoBangGame()
        winner, con_list = game.check_winner(self.board, self.human_player, n)
        if winner == self.human_player:
            new_points = []
            for con_type, (x1, y1), (x2, y2) in con_list:
                if con_type == 1:
                    new_points += [(x1, y1 - 1), (x2, y2 + 1)]
                elif con_type == 2:
                    new_points += [(x1 - 1, y1), (x2 + 1, y2)]
                elif con_type == 3:
                    new_points += [(x1 - 1, y1 - 1), (x2 + 1, y2 + 1)]
                elif con_type == 4:
                    new_points += [(x1 + 1, y1 - 1), (x2 - 1, y2 + 1)]
            for point in new_points:
                if self.check_point_empty(point):
                    return point

    def rule3(self, n=3):
        # 寻找3个相连
        game = GoBangGame()
        winner, con_list = game.check_winner(self.board, self.ai_player, n)
        if winner == self.ai_player:
            for con_type, (x1, y1), (x2, y2) in con_list:
                point1 = None
                point2 = None
                point1_next = None
                point2_next = None
                if con_type == 1:
                    point1 = (x1, y1 - 1)
                    point2 = (x2, y2 + 1)
                    point1_next = (x1, y1 - 2)
                    point2_next = (x2, y2 + 2)
                elif con_type == 2:
                    point1 = (x1 - 1, y1)
                    point2 = (x2 + 1, y2)
                    point1_next = (x1 - 2, y1)
                    point2_next = (x2 + 2, y2)
                elif con_type == 3:
                    point1 = (x1 - 1, y1 - 1)
                    point2 = (x2 + 1, y2 + 1)
                    point1_next = (x1 - 2, y1 - 2)
                    point2_next = (x2 + 2, y2 + 2)
                elif con_type == 4:
                    point1 = (x1 + 1, y1 - 1)
                    point2 = (x2 - 1, y2 + 1)
                    point1_next = (x1 + 2, y1 - 2)
                    point2_next = (x2 - 2, y2 + 2)
                if self.check_point_empty(point1) and self.check_point_empty(point2):
                    if self.check_point_empty(point1_next):
                        return point1
                    elif self.check_point_empty(point2_next):  # 如果位置2的连续2个空位置则选择位置2
                        return point2
                    else:  # 如果位置1和2均只有1个空位置,则任选一处
                        return random.choice([point1, point2])

    def rule4(self, n=3):
        # 寻找3个相连
        game = GoBangGame()
        winner, con_list = game.check_winner(self.board, self.human_player, n)
        if winner == self.human_player:
            for con_type, (x1, y1), (x2, y2) in con_list:
                point1 = None
                point2 = None
                point1_next = None
                point2_next = None
                if con_type == 1:
                    point1 = (x1, y1 - 1)
                    point2 = (x2, y2 + 1)
                    point1_next = (x1, y1 - 2)
                    point2_next = (x2, y2 + 2)
                elif con_type == 2:
                    point1 = (x1 - 1, y1)
                    point2 = (x2 + 1, y2)
                    point1_next = (x1 - 2, y1)
                    point2_next = (x2 + 2, y2)
                elif con_type == 3:
                    point1 = (x1 - 1, y1 - 1)
                    point2 = (x2 + 1, y2 + 1)
                    point1_next = (x1 - 2, y1 - 2)
                    point2_next = (x2 + 2, y2 + 2)
                elif con_type == 4:
                    point1 = (x1 + 1, y1 - 1)
                    point2 = (x2 - 1, y2 + 1)
                    point1_next = (x1 + 2, y1 - 2)
                    point2_next = (x2 - 2, y2 + 2)
                if self.check_point_empty(point1) and self.check_point_empty(point2):
                    if self.check_point_empty(point1_next) or self.check_point_empty(point2_next):
                        return random.choice([point1, point2])  # 任一头有2个以上空位置才堵住,堵两端都可以

    def rule5(self):
        return RandomStrategy().model(self.board, self.ai_player)

    def model(self, cur_board, ai_player):
        self.board = cur_board
        self.ai_player = ai_player
        self.human_player = 1 if ai_player == 2 else 2
        rule_chain = [self.rule1, self.rule2, self.rule3, self.rule4, self.rule5]
        for rule in rule_chain:
            res = rule()
            if res is not None:
                return res
