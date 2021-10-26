from marshmallow import Schema, fields, validates
import numpy as np
from constance import config


class PodSchema(Schema):
    players = fields.List(fields.Str)
    scores = fields.List(fields.List(fields.Int(allow_none=True)))

    @validates("scores")
    def validate_scores(self, scores):
        length = None
        for score in scores:
            if length is None:
                length = len(score)
                continue
            assert length == len(score), scores

    def validate(self, data):
        assert len(data["players"]) == len(data["scores"])


class RoundSchema(Schema):
    pods = fields.Nested(PodSchema, many=True)
    buys = fields.List(fields.Str, required=False)
    drop = fields.List(fields.Str, required=False)


def get_standings_by_round(
    rnd, primary_score_per_buy=None, secondary_score_per_buy=None
):
    """
    Args:
        rnd: RoundSchema
    Returns:
        dict player_name -> array of scores
    """
    if primary_score_per_buy is None:
        primary_score_per_buy = config.PRIMARY_SCORE_PER_BUY
    if secondary_score_per_buy is None:
        secondary_score_per_buy = config.SECONDARY_SCORE_PER_BUY

    score_by_player = {}
    pod_by_player = {}
    for pod_id, pod in enumerate(rnd["pods"]):
        for player_name, player_score in zip(pod["players"], pod["scores"]):
            score_by_player[player_name] = player_score
            pod_by_player[player_name] = pod_id
    for player_name in rnd["buys"]:
        score_by_player[player_name] = [primary_score_per_buy, secondary_score_per_buy]
        pod_by_player[player_name] = None
    return score_by_player, pod_by_player


def get_standings(round_list):
    if round_list is None:
        return []
    round_list = RoundSchema(many=True).load(round_list)

    total_score_by_player = {}
    score_by_player_by_round = {}
    drops = []
    for rnd_id, rnd in enumerate(round_list):
        score_by_player, pod_by_player = get_standings_by_round(rnd)
        if "drop" in rnd and len(rnd["drop"]) != 0:
            drops += rnd["drop"]
        for player_name, score in score_by_player.items():
            # add up the total scores
            if player_name not in total_score_by_player:
                total_score_by_player[player_name] = [0, 0]
            for idx in range(len(score)):
                if score[idx] is not None:
                    total_score_by_player[player_name][idx] += score[idx]
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


def get_rounds(round_list):
    if round_list is None:
        return 0
    round_list = RoundSchema(many=True).load(round_list)

    return {"n_rounds": len(round_list), "rounds": round_list}


def update_result(round_list, player_name, round_id, score):
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
                round_list[round_id]["pods"][pod_id]["scores"][idx] = map(int, score)
                return RoundSchema(many=True).load(round_list)


def new_round(round_list, player_name_list):
    if round_list is None:
        return new_round_random([], player_name_list=player_name_list)
    round_list = RoundSchema(many=True).load(round_list)
    return new_round_with_history(round_list, player_name_list=player_name_list)


def new_round_random(round_list, player_name_list):
    np.random.shuffle(player_name_list)
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
            "buys": list(player_name_list[-(len(player_name_list) % 4) :])
            if len(player_name_list) % 4 != 0
            else [],
            "drop": [],
        }
    )
    return RoundSchema(many=True).load(round_list)


def new_round_with_history(
    round_list, player_name_list=[], w_first=None, w_second=None
):
    if w_first is None:
        w_first = config.PRIMARY_WEIGHT
    if w_second is None:
        w_second = config.SECONDARY_WEIGHT
    round_list = RoundSchema(many=True).load(round_list)

    standings = get_standings(round_list)
    player_name_list = [item["player_name"] for item in standings]
    player_name_set = set(player_name_list)
    exclude_list = [idx for idx, item in enumerate(standings) if item["dropped"]]
    score_list = [
        item["total_score"][0] * w_first + item["total_score"][1] * w_second
        for item in standings
    ]

    pods = get_pods(
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


def get_pods(score_list, exclude_list=[], round_list=[], player_name_list=[]):
    n_players = len(score_list)
    pods = []
    done = set(exclude_list)
    order_by = sorted(range(n_players), key=lambda x: -score_list[x])

    # collect existed pods
    hashbase = "$#"
    existed_pods = set()
    for round in round_list:
        for pod in round["pods"]:
            pod_hash = hashbase.join(sorted(pod["players"]))
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
        pod_hash = hashbase.join(sorted(pod_player_name_list))
        while pod_hash in existed_pods and ix_look_forward + 1 < n_players:
            # swap lowest with the next highest (is possible)
            ix_look_forward += 1
            idx_other = order_by[ix_look_forward]

            done.remove(idxs[-1])
            idxs[-1] = idx_other
            done.add(idx_other)

            # recalculate hash
            pod_player_name_list = [player_name_list[idx] for idx in idxs]
            pod_hash = hashbase.join(sorted(pod_player_name_list))

        pods.append(idxs)

    return pods


def player_set_all_buys(round_list, player_name):
    if round_list is None:
        return
    round_list = RoundSchema(many=True).load(round_list)

    for idx in range(len(round_list)):
        round_list[idx]["buys"].append(player_name)
    return round_list


def drop_player_from_tournament(round_list, player_name):
    if round_list is None:
        return
    round_list = RoundSchema(many=True).load(round_list)

    if "drop" not in round_list[-1]:
        round_list[-1]["drop"] = []
    round_list[-1]["drop"].append(player_name)
    return round_list


def redo_last_round(round_list, player_name_list):
    if len(round_list) == 0:
        return new_round([], player_name_list)

    last_round = round_list[-1]
    if len(round_list) > 1:
        round_list = round_list[:-1]
    else:
        round_list = None

    round_list[-1]["drop"] = last_round["drop"]
    return new_round(round_list, player_name_list)
