from pprint import pprint
import numpy as np
from copy import deepcopy as copy
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from pods.models import Tournament, PlayerName
from pods.judge import (
    new_round_random,
    get_standings,
    get_probability_mat_for_players,
    get_pods,
    new_round_with_history,
)


class IntegrationApiTest(APITestCase):
    def test_add_player_to_tournament(self):
        tour = Tournament.objects.create(name="t1")
        for _ in range(2):
            # loop to assert duplicates not added twice
            data = {"player": {"name": "Fred"}}
            response = self.client.post(
                reverse("api_tournament_add", kwargs={"id": tour.id}),
                data,
                format="json",
            )
            assert response.status_code == 201, response.json()
            assert PlayerName.objects.filter(name="Fred").count() == 1
            assert tour.players.count() == 1


class LogicTest(TestCase):
    def test_new_round_random(self):
        data = [
            {
                "pods": [
                    {
                        "players": ["Albert", "Fred", "George", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Zyra", "Sheldon", "Iffy"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                ],
                "buys": ["Leona"],
            },
            {
                "pods": [
                    {
                        "players": ["Albert", "Zyra", "Iffy", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Fred", "Sheldon", "Leona"],
                        "scores": [[1, 1], [1, 2], [1, 3], [1, 4]],
                    },
                ],
                "buys": ["George"],
            },
        ]
        new_data = new_round_random(
            data,
            [
                "Albert",
                "Fred",
                "George",
                "Sexton",
                "Lily",
                "Zyra",
                "Sheldon",
                "Iffy",
                "Leona",
            ],
        )

        assert len(new_data) == 3
        assert len(new_data[2]["pods"]) == 2
        self.assertDictEqual(get_standings(new_data)[0], get_standings(data)[0])
        assert len(new_data[2]["buys"]) == 1

    def test_get_probability_mat_for_players(self):
        score_list = [2, 2, 2, 2]
        mat = get_probability_mat_for_players(score_list)
        for idx in range(len(score_list)):
            assert mat[idx][idx] == 0, mat

    def test_new_round_prob(self):
        np.printoptions(precision=2)
        data = [
            {
                "pods": [
                    {
                        "players": ["Albert", "Fred", "George", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Zyra", "Sheldon", "Iffy"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                ],
                "buys": ["Leona"],
            },
            {
                "pods": [
                    {
                        "players": ["Albert", "Zyra", "Iffy", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Fred", "Sheldon", "Leona"],
                        "scores": [[1, 1], [1, 2], [1, 3], [1, 4]],
                    },
                ],
                "buys": ["George"],
            },
        ]
        for _ in range(10):
            new_data = new_round_with_history(copy(data))
            assert len(new_data) == 3
            assert len(new_data[2]["pods"]) == 2
            assert "Sexton" in new_data[2]["pods"][0]["players"]
            assert "Sexton" not in new_data[2]["buys"]
            assert "Iffy" not in new_data[2]["buys"]

    def test_get_pods(self):
        score_list = [1, 2, 300, 400, 500, 600]
        pods = get_pods(score_list)
        assert len(pods) == 1
        assert 5 in pods[0]

        score_list = [1, 1, 1, 1, 1]
        pods = get_pods(score_list)
        assert len(pods) == 1
