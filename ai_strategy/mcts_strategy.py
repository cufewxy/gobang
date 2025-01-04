import random
from copy import copy, deepcopy

import numpy as np

from ai_base import AIStrategy
from ai_strategy.rule_strategy import RuleStrategy
from gobang import GoBangGame

random.seed(1)


class Node:
    def __init__(self, player):
        self.player = player
        self.child_node = []
        self.action = []  # 表示下棋的动作,没有在每个节点都保存棋盘,而是从根节点开始往下推演棋盘,否则内存过大
        self.parent_node = None
        self.visit_num = 0  # 访问次数
        self.win_num = 0  # 获胜次数
        self.if_win = None  # 1表示胜利,0表示未胜利,None表示无法判断


class Tree:
    def __init__(self, cur_player):
        self.root_node = Node(cur_player)

    def trim(self, node):
        self.root_node = node
        self.root_node.parent_node = None


class MCTSStrategy(AIStrategy):
    """
    MCTS(蒙特卡洛树搜索)模型

    """
    SIMULATION_DEPTH = 20
    SIMULATION_TIMES = 10
    UCB_C = np.log(2)
    cur_board = None
    tree = None

    def reconstruct_board(self, node):
        """
        从节点往上追溯到根节点,叠加所有动作重建棋盘
        """
        node_list = []
        cur_node = node
        while self.tree.root_node != cur_node:
            node_list.append(node)
            cur_node = cur_node.parent_node
        cur_board = deepcopy(self.cur_board)
        for node in node_list:
            x, y = node.action
            cur_board[x][y] = node.player
        return cur_board

    def ucb(self, v, n, n_parent):
        if n == 0 or n_parent == 0:
            return 999999
        if v == 0:
            return 0
        return v / n + self.UCB_C * np.sqrt(np.log(n_parent) / n)

    def get_child_max_ucb(self, node):
        ucb_list = []
        child_node_list = node.child_node
        if len(child_node_list) == 0:  # 如果当前是叶子节点则停止搜索
            return
        for i, child_node in enumerate(node.child_node):
            visit_num = child_node.visit_num
            if visit_num == 0:
                ucb_list.append(999999)
            else:
                ucb = self.ucb(child_node.win_num, visit_num, node.visit_num)
                ucb_list.append(ucb)
        max_value = max(ucb_list)
        idx_max = np.array(ucb_list) == max_value
        # idx_max = np.array(ucb_list).argmax()
        new_node = random.choice(np.array(child_node_list)[idx_max])
        rank = np.argsort(ucb_list)
        for i in rank[-1:-6:-1]:
            print(f"{child_node_list[i].action}-{ucb_list[i]}")
        return new_node

    def selection(self, node: Node):
        """
        根据UCB选择最佳的节点,直到叶子节点.如果没有子节点则返回自己
        """
        child_node_list = node.child_node
        # 如果没有子节点则跳过
        if len(child_node_list) == 0:
            return node
        # 循环找到叶子节点
        while 1:
            print("-" * 20)
            print("Selection阶段,寻找最优子节点")
            child_node = self.get_child_max_ucb(node)
            print("-" * 20)
            if child_node is None:
                break
            node = child_node
        return node

    def expansion(self, node: Node):
        """
        如果选择的节点不是叶子节点或当前胜负已分则不需要扩展
        遍历棋盘所有空的位置设置为其子节点
        """
        if len(node.child_node) > 0:
            return node
        self.set_node_win(node)
        if node.if_win:
            return node
        # 取当前所有的空位置
        cur_player = node.player
        next_player = 1 if cur_player == 2 else 2
        for i in range(len(self.cur_board)):
            for j in range(len(self.cur_board)):
                if self.cur_board[i][j] == 0:
                    new_node = Node(next_player)
                    new_node.parent_node = node
                    new_node.action = (i, j)
                    node.child_node.append(new_node)
        return random.choice(node.child_node)

    def set_node_win(self, node):
        if node.if_win is not None:
            return
        cur_board = self.reconstruct_board(node)
        g = GoBangGame()
        winner, _ = g.check_winner(cur_board, node.player)
        if winner is None:
            node.if_win = False
        elif winner == 0:
            node.if_win = True
        else:
            node.if_win = True

    def simulation(self, node: Node):
        """
        从扩展的子节点做模拟,直到游戏结束或达到预设的深度
        """
        # 查看当前节点是否获胜
        self.set_node_win(node)
        if node.if_win:
            print(f"当前模拟节点{node.action},已分出胜负,胜者为{node.player}")
            return node.player
        cur_board = self.reconstruct_board(node)
        g = GoBangGame()
        next_player = 1 if node.player == 2 else 2
        run_flag = True
        i = 0
        winner = None

        g.cur_player = next_player
        g.board.position = deepcopy(cur_board)

        while run_flag:
            i += 1
            action = RuleStrategy().model(g.board.position, next_player)
            g.proceed(action)
            # 判断退出条件
            if g.result is not None:
                winner = g.result
                run_flag = False
            if i >= self.SIMULATION_DEPTH:
                run_flag = False
            # 轮换
            next_player = 1 if next_player == 2 else 2
        if winner is None:
            print(f"当前模拟节点{node.action},未分出胜负")
        else:
            print(f"当前模拟节点{node.action},胜者为{winner}")
        return winner

    def backpropagation(self, node: Node, winner):
        """
        将模拟结果反向传播给沿途阶段,包括访问次数和胜利次数
        将沿途节点访问次数加1
        将沿途节点胜利方胜利次数加1
        """
        cur_node = node
        while cur_node is not None:
            cur_node.visit_num += 1
            if winner is not None and winner != 0 and cur_node.player == winner:
                cur_node.win_num += 1
            cur_node = cur_node.parent_node

    def reset(self):
        self.cur_board = None
        self.tree = None

    def receive_human_action(self, board):
        """
        接收人类动作,更新棋盘及树
        """
        diff = np.array(board) - np.array(self.cur_board)
        new_point = None
        for i in range(len(diff)):
            for j in range(len(diff[0])):
                if diff[i][j] > 0:
                    new_point = (i, j)
                    break
        assert new_point is not None
        if len(self.tree.root_node.child_node) == 0:
            # 说明之前的扩展没有扩展到此节点
            cur_player = self.tree.root_node.player
            next_player = 1 if cur_player == 2 else 2
            new_root_node = Node(next_player)
            new_root_node.action = new_point
            new_root_node.parent_node = self.tree.root_node
            self.cur_board = self.reconstruct_board(new_root_node)
            self.tree.trim(new_root_node)
        else:
            for node in self.tree.root_node.child_node:
                if node.action == new_point:
                    self.tree.trim(node)
                    self.cur_board = self.reconstruct_board(node)
                    break

    def model(self, cur_board, ai_player):
        """
        产生一个树,叶子节点的棋盘设置为cur_board.按以下步骤进行迭代
        (1)选择
        第一轮迭代,由于当前树只有1个节点,没有子节点,因此跳过
        后续迭代中,找到所有子节点,计算所有子节点的UCB值,选择UCB值最大的节点
        (2)扩展
        如果选择的节点是非叶子节点或者此节点的胜负关系已分,则不需要扩展
        将剩余所有的下法作为子节点追加到根节点上,并任取其中一个节点作为当前节点
        (3)仿真
        如果选择的节点胜负已分,则不需要仿真
        从当前节点往后仿真对局,可叠加rule_strategy,直到游戏结束或深度超过预设值
        (4)回溯
        根据胜负关系,更新当前节点到根节点的沿途所有节点的win_num和visit_num
        """
        if self.cur_board is None:  # 首次运行
            self.cur_board = deepcopy(cur_board)
            human_player = 1 if ai_player == 2 else 2
            self.tree = Tree(human_player)
        else:  # 对局中,识别树走到哪个节点
            self.receive_human_action(cur_board)
        # 根据规则AI判断下一步动作
        cur_player = self.tree.root_node.player
        next_player = 1 if cur_player == 2 else 2
        rule_strategy = RuleStrategy()
        rule_strategy.board = self.cur_board
        rule_strategy.ai_player = next_player
        rule_strategy.human_player = 1 if rule_strategy.ai_player == 2 else 2
        rule_chain = [rule_strategy.rule1, rule_strategy.rule2, rule_strategy.rule3, rule_strategy.rule4]
        # 匹配到规则, 直接按新的下法剪枝
        for rule in rule_chain:
            res = rule()
            if res is not None:
                new_node = Node(next_player)
                new_node.parent_node = self.tree.root_node
                new_node.action = res
                self.tree.root_node.child_node.append(new_node)
                self.cur_board = self.reconstruct_board(new_node)
                self.tree.trim(new_node)
                print(f"触发规则,直接使用RuleStrategy模型,落点为{res}")
                return new_node.action
        # 未匹配到规则, 使用MCTS算法
        for i in range(self.SIMULATION_TIMES):
            print(f"第{i}次模拟")
            next_node = self.selection(self.tree.root_node)
            next_node = self.expansion(next_node)
            winner = self.simulation(next_node)
            self.backpropagation(next_node, winner)
        print("-" * 20)
        print("决策阶段,寻找最优子节点")
        new_node = self.get_child_max_ucb(self.tree.root_node)
        print("-" * 20)
        self.cur_board = self.reconstruct_board(new_node)
        self.tree.trim(new_node)
        return new_node.action


if __name__ == '__main__':
    s = MCTSStrategy()
    board = [[2, 0, 0, 0, 0, 0],
             [1, 2, 0, 0, 0, 0],
             [1, 0, 2, 0, 0, 0],
             [0, 1, 0, 2, 0, 0],
             [0, 0, 1, 0, 0, 0],
             [0, 0, 0, 0, 0, 0]]
    print(s.model(board, 1))
