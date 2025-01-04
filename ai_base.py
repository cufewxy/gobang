import abc


class AIStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def model(self, cur_board, ai_player) -> [int, int]:
        """
        模型
        Args:
            cur_board:

        Returns:
            落子位置
        """
        raise NotImplementedError

    def reset(self):
        pass


