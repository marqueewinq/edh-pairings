from marshmallow import Schema, fields, validates
import numpy as np


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
    buys = fields.List(fields.Str, required = False)


def get_standings_by_round(rnd):
    """
        Args:
            rnd: RoundSchema
        Returns:
            dict player_name -> array of scores
    """
    score_by_player = {}
    pod_by_player = {}
    for pod_id, pod in enumerate(rnd["pods"]):
        for player_name, player_score in zip(pod["players"], pod["scores"]):
            score_by_player[player_name] = player_score
            pod_by_player[player_name] = pod_id
    return score_by_player, pod_by_player


def get_standings(round_list):
    if round_list is None:
        return []
    round_list = RoundSchema(many=True).load(round_list)

    total_score_by_player = {}
    score_by_player_by_round = {}
    for rnd_id, rnd in enumerate(round_list):
        score_by_player, pod_by_player = get_standings_by_round(rnd)
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
                round_list[round_id]["pods"][pod_id]["scores"][idx] = score
                return RoundSchema(many=True).load(round_list)


def new_round(round_list, player_name_list):
    print(player_name_list)
    if round_list is None:
        return new_round_random(round_list, player_name_list)
    round_list = RoundSchema(many=True).load(round_list)
    #return new_round_with_history(round_list)
    return new_round_random(round_list, player_name_list)


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
            ],
            "buys": list(player_name_list[:-(len(player_name_list) % 4)]),
        }
    )
    return RoundSchema(many=True).load(round_list)


def new_round_with_history(round_list):
    standings = get_standings(round_list)
    player_name_list = [item["player_name"] for item in standings]
    score_list = [item["total_score"] for item in standings]
    n_players = len(player_name_list)

    prob_mat = np.zeros(shape=(0,))
