from typing import List, Optional, Tuple

__version__ = "v1"

from judge.interfaces import Judge as AbstractJudge

from .v1 import (
    drop_player_from_tournament,
    get_rounds,
    get_standings,
    new_round,
    player_set_all_buys,
    redo_last_round,
    update_result,
)


class Judge(AbstractJudge):
    version: Optional[str] = __version__

    def new_round(
        self, round_list: List[dict], player_name_list: List[str]
    ) -> List[dict]:
        return new_round(round_list, player_name_list)

    def player_set_all_buys(
        self, round_list: List[dict], player_name: str
    ) -> List[dict]:
        return player_set_all_buys(round_list, player_name)

    def drop_player_from_tournament(
        self, round_list: List[dict], player_name: str
    ) -> List[dict]:
        return drop_player_from_tournament(round_list, player_name)

    def redo_last_round(
        self, round_list: List[dict], player_name_list: List[str]
    ) -> List[dict]:
        return redo_last_round(round_list, player_name_list)

    def get_standings(self, round_list: List[dict]):
        return get_standings(round_list)

    def get_rounds(self, round_list: List[dict]):
        return get_rounds(round_list)

    def update_result(
        self,
        round_list: List[dict],
        player_name: str,
        round_id: int,
        score: Tuple[int, int],
    ):
        return update_result(round_list, player_name, round_id, score)
