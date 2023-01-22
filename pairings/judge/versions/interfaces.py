import abc
from typing import List, Optional, Tuple


class Judge(abc.ABC):
    version: Optional[str] = None

    @abc.abstractmethod
    def new_round(
        self, round_list: List[dict], player_name_list: List[str]
    ) -> List[dict]:
        pass

    @abc.abstractmethod
    def player_set_all_buys(
        self, round_list: List[dict], player_name: str
    ) -> List[dict]:
        pass

    @abc.abstractmethod
    def drop_player_from_tournament(
        self, round_list: List[dict], player_name: str
    ) -> List[dict]:
        pass

    @abc.abstractmethod
    def redo_last_round(
        self, round_list: List[dict], player_name_list: List[str]
    ) -> List[dict]:
        pass

    @abc.abstractmethod
    def get_standings(self, round_list: List[dict]):
        pass

    @abc.abstractmethod
    def get_rounds(self, round_list: List[dict]):
        pass

    @abc.abstractmethod
    def update_result(
        self,
        round_list: List[dict],
        player_name: str,
        round_id: int,
        score: Tuple[int, int],
    ):
        pass
