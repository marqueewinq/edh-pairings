import typing as ty

import numpy as np
from judge.versions.interfaces import Judge as AbstractJudge
from judge.versions.schemas import RoundSchema
from scipy.spatial import distance_matrix

__version__ = "soft_random"


class Judge(AbstractJudge):
    version: ty.Optional[str] = __version__

    def __init__(self, config: dict):
        from judge.schemas import JudgeSchema

        self.config = JudgeSchema().load(config)

    @staticmethod
    def _get_probability_mat_for_players(score_list):
        n_players = len(score_list)
        score_list = np.asarray(score_list)
        score_list = score_list.reshape(-1, 1)

        eps = 1e-3
        mat = distance_matrix(score_list, score_list)
        # reverse dependency
        mat = 1.0 / (mat + eps)
        eye = np.ones_like(mat) - np.eye(n_players)
        mat = mat * eye
        # normalize
        mat = mat / np.sum(mat, axis=1)[:, None]
        return mat

    def get_pods(self, score_list, exclude_list=[], round_list=[], player_name_list=[]):
        shuffle_seats = self.config["shuffle_seats"]

        n_players = len(score_list)
        prob_mat = self._get_probability_mat_for_players(score_list)
        pods = []
        done = set(exclude_list)
        order_by = sorted(range(n_players), key=lambda x: -score_list[x])
        for idx_first in order_by:
            if idx_first in done:
                continue
            if n_players - len(done) < 4:
                # only buys remain
                break
            done.add(idx_first)

            # dropping done choices
            probs = prob_mat[idx_first]
            for idx in done:
                probs[idx] = 0
            probs = probs / np.sum(probs)

            idxs = np.random.choice(range(n_players), p=probs, size=(3,), replace=False)
            for idx in idxs:
                done.add(idx)

            idxs = [idx_first] + idxs.tolist()
            if shuffle_seats:
                np.random.shuffle(idxs)
            pods.append(idxs)

        return pods

    def new_round(
        self, round_list: ty.Optional[ty.List[dict]], player_name_list: ty.List[str]
    ) -> ty.List[dict]:
        if round_list is None:
            return self.new_round_random([], player_name_list=player_name_list)
        round_list = RoundSchema(many=True).load(round_list)
        return self.new_round_with_history(
            round_list, player_name_list=player_name_list
        )

    def new_round_random(
        self, round_list: ty.List[dict], player_name_list: ty.List[str]
    ) -> ty.List[dict]:
        np.random.shuffle(player_name_list)

        drop = round_list[-1].get("drop", []) if len(round_list) > 0 else []
        player_name_list = [name for name in player_name_list if name not in drop]
        buys = drop + (
            list(player_name_list[-(len(player_name_list) % 4) :])
            if len(player_name_list) % 4 != 0
            else []
        )
        round_list.append(
            {
                "pods": [
                    {
                        "players": list(player_name_list[idx : idx + 4]),
                        "scores": [[0, 0] for _ in range(4)],
                    }
                    for idx in range(0, len(player_name_list), 4)
                    if idx + 4 <= len(player_name_list)
                ],
                "buys": buys,
                "drop": drop,
            }
        )
        return RoundSchema(many=True).load(round_list)

    def new_round_with_history(
        self, round_list, player_name_list=[], w_first=None, w_second=None
    ) -> ty.List[dict]:
        if w_first is None:
            w_first = self.config["judge_primary_weight"]
        if w_second is None:
            w_second = self.config["judge_secondary_weight"]
        round_list = RoundSchema(many=True).load(round_list)

        standings = self.get_standings(round_list)
        player_name_list = [item["player_name"] for item in standings]
        player_name_set = set(player_name_list)
        exclude_list = [idx for idx, item in enumerate(standings) if item["dropped"]]
        score_list = [
            item["total_score"][0] * w_first + item["total_score"][1] * w_second
            for item in standings
        ]

        pods = self.get_pods(score_list, exclude_list=exclude_list)
        for pod in pods:
            for pod_player in pod:
                player_name_set.remove(player_name_list[pod_player])
        buys = list(player_name_set)
        drop = round_list[-1].get("drop", []) if len(round_list) > 0 else []

        round_list.append(
            {
                "pods": [
                    {
                        "players": [player_name_list[pod_player] for pod_player in pod],
                        "scores": [[0, 0] for _ in range(4)],
                    }
                    for pod in pods
                ],
                "buys": buys,
                "drop": drop,
            }
        )
        return RoundSchema(many=True).load(round_list)

    def player_set_all_buys(
        self, round_list: ty.List[dict], player_name: str
    ) -> ty.List[dict]:
        if round_list is None:
            return
        round_list = RoundSchema(many=True).load(round_list)

        for idx in range(len(round_list)):
            round_list[idx]["buys"].append(player_name)
        return round_list

    def drop_player_from_tournament(
        self, round_list: ty.List[dict], player_name: str
    ) -> ty.List[dict]:
        if round_list is None:
            return
        round_list = RoundSchema(many=True).load(round_list)

        if "drop" not in round_list[-1]:
            round_list[-1]["drop"] = []
        round_list[-1]["drop"].append(player_name)
        return round_list

    def redo_last_round(
        self, round_list: ty.Optional[ty.List[dict]], player_name_list: ty.List[str]
    ) -> ty.List[dict]:
        if round_list is None or len(round_list) == 0:
            return self.new_round([], player_name_list)

        last_round = round_list[-1]
        if len(round_list) > 1:
            round_list = round_list[:-1]
            round_list[-1]["drop"] = last_round["drop"]
        else:
            round_list = None

        return self.new_round(round_list, player_name_list)

    def get_standings_by_round(
        self,
        rnd: dict,
        primary_score_per_buy=None,
        secondary_score_per_buy=None,
    ):
        """
        Args:
            rnd: RoundSchema
        Returns:
            dict player_name -> array of scores
        """
        if primary_score_per_buy is None:
            primary_score_per_buy = self.config["buy_primary_score"]
        if secondary_score_per_buy is None:
            secondary_score_per_buy = self.config["buy_secondary_score"]

        score_by_player: ty.Dict[str, ty.Tuple[int, int]] = {}
        pod_by_player: ty.Dict[str, ty.Optional[int]] = {}
        for pod_id, pod in enumerate(rnd["pods"]):
            for player_name, player_score in zip(pod["players"], pod["scores"]):
                score_by_player[player_name] = player_score
                pod_by_player[player_name] = pod_id
        dropped_list = rnd.get("drop", [])
        for player_name in rnd["buys"]:
            if player_name in dropped_list:
                score = (0, 0)
            else:
                score = (
                    primary_score_per_buy,
                    secondary_score_per_buy,
                )
            score_by_player[player_name] = score
            pod_by_player[player_name] = None
        return score_by_player, pod_by_player

    def get_standings(self, round_list: ty.List[dict]):
        if round_list is None:
            return []
        round_list = RoundSchema(many=True).load(round_list)

        total_score_by_player: ty.Dict[str, ty.Tuple[int, int]] = {}
        score_by_player_by_round: ty.Dict[str, ty.List[dict]] = {}
        drops = []
        for rnd_id, rnd in enumerate(round_list):
            score_by_player, pod_by_player = self.get_standings_by_round(rnd)
            if "drop" in rnd and len(rnd["drop"]) != 0:
                drops += rnd["drop"]
            for player_name, score in score_by_player.items():
                # add up the total scores
                if player_name not in total_score_by_player:
                    total_score_by_player[player_name] = (0, 0)

                total_player_score = list(total_score_by_player[player_name])
                for idx in range(len(score)):
                    if score[idx] is not None:
                        total_player_score[idx] += score[idx]
                total_score_by_player[player_name] = (
                    total_player_score[0],
                    total_player_score[1],
                )

                # write per-round results
                if player_name not in score_by_player_by_round:
                    score_by_player_by_round[player_name] = []
                score_by_player_by_round[player_name].append(
                    {"score": score, "pod_id": pod_by_player[player_name]}
                )

        results = []
        for player_name in total_score_by_player:
            results.append(
                {
                    "player_name": player_name,
                    "total_score": total_score_by_player[player_name],
                    "rounds": score_by_player_by_round[player_name],
                    "dropped": bool(player_name in drops),
                }
            )
        return sorted(results, key=lambda item: item["total_score"], reverse=True)

    def get_rounds(self, round_list: ty.List[dict]) -> dict:
        if round_list is None:
            return 0
        round_list = RoundSchema(many=True).load(round_list)
        return {"n_rounds": len(round_list), "rounds": round_list}

    def update_result(
        self,
        round_list: ty.List[dict],
        player_name: str,
        round_id: int,
        score: ty.Tuple[int, int],
    ):
        if round_list is None:
            return
        round_list = RoundSchema(many=True).load(round_list)
        assert round_id < len(round_list)

        for pod_id, pod in enumerate(round_list[round_id]["pods"]):
            for idx, player_name_in_pod in enumerate(pod["players"]):
                if player_name == player_name_in_pod:
                    # replace None in new score with old values
                    old_score = round_list[round_id]["pods"][pod_id]["scores"][idx]
                    for idx_rplc, (new_value, old_value) in enumerate(
                        zip(score, old_score)
                    ):
                        if new_value is None:
                            score[idx_rplc] = old_score[idx_rplc]
                    # rewrite values
                    round_list[round_id]["pods"][pod_id]["scores"][idx] = map(
                        int, score
                    )
                    return RoundSchema(many=True).load(round_list)
