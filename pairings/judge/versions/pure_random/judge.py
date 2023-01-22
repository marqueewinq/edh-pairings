import typing as ty

from judge.versions.v2 import Judge as JudgeV2

__version__ = "pure_random"


class Judge(JudgeV2):
    version: ty.Optional[str] = __version__

    def new_round(
        self, round_list: ty.Optional[ty.List[dict]], player_name_list: ty.List[str]
    ) -> ty.List[dict]:
        round_list = round_list if round_list is not None else []
        return self.new_round_random(round_list, player_name_list=player_name_list)
