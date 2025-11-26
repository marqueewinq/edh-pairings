import typing as ty

import numpy as np
from judge.versions.schemas import RoundSchema
from judge.versions.v1 import Judge as JudgeV1

__version__ = "deterministic"


class Judge(JudgeV1):
    version: ty.Optional[str] = __version__

    def get_pods(self, score_list, exclude_list=[], round_list=[], player_name_list=[]):
        shuffle_seats = self.config["shuffle_seats"]

        n_players = len(score_list)
        pods = []
        done = set(exclude_list)
        order_by = sorted(range(n_players), key=lambda x: -score_list[x])

        # collect existed pods
        existed_pods = set()
        for rnd in round_list:
            for pod in rnd["pods"]:
                pod_hash = tuple(sorted(pod["players"]))
                existed_pods.add(pod_hash)

        for ix_order, idx_first in enumerate(order_by):
            if idx_first in done:
                continue
            if n_players - len(done) < 4:
                # only buys remain
                break
            idxs = [idx_first]
            done.add(idx_first)

            ix_look_forward = ix_order
            while len(idxs) < 4:
                ix_look_forward += 1
                idx_other = order_by[ix_look_forward]
                if idx_other in done:
                    # skip buys
                    continue
                idxs.append(idx_other)
                done.add(idx_other)

            # check pod never existed
            pod_player_name_list = [player_name_list[idx] for idx in idxs]
            pod_hash = tuple(sorted(pod_player_name_list))
            while pod_hash in existed_pods and ix_look_forward + 1 < n_players:
                # swap lowest with the next highest (is possible)
                ix_look_forward += 1
                idx_other = order_by[ix_look_forward]

                done.remove(idxs[-1])
                idxs[-1] = idx_other
                done.add(idx_other)

                # recalculate hash
                pod_player_name_list = [player_name_list[idx] for idx in idxs]
                pod_hash = tuple(sorted(pod_player_name_list))

            if shuffle_seats:
                np.random.shuffle(idxs)
            pods.append(idxs)

        return pods

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

        pods = self.get_pods(
            score_list,
            exclude_list=exclude_list,
            round_list=round_list,
            player_name_list=player_name_list,
        )
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
