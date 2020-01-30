from pprint import pprint
import numpy as np
from copy import deepcopy as copy
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from pods.models import Tournament, PlayerName
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from pods.judge import (
    new_round_random,
    get_standings,
    get_probability_mat_for_players,
    get_pods,
    new_round_with_history,
    redo_last_round,
)


class IntegrationApiTest(APITestCase):
    def setUp(self):
        user_data = {"username":"Me", "password": "pwd"}
        self.user = User.objects.create_user(**user_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("rest_login"), data = user_data, format = "json")
        self.token = Token.objects.get(user = self.user).key

    def test_add_player_to_tournament(self):
        tour = Tournament.objects.create(name="t1")
        for _ in range(2):
            # loop to assert duplicates not added twice
            data = {"player": {"name": "Fred"}}
            response = self.client.post(
                reverse("api_tournament_add", kwargs={"id": tour.id}),
                data,
                headers = {"Authorization": f"Token {self.token}"},
                format = "json",
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

    def test_get_pods_with_exclude(self):
        score_list = [1, 2, 300, 400, 500, 600]
        pods = get_pods(score_list, exclude_list=[4, 5])
        assert len(pods) == 1
        assert 5 not in pods[0]
        assert 4 not in pods[0]
        assert 3 in pods[0]

    def test_redo_last_round(self):
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
                "drop": [],
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
                "drop": ["George"],
            },
        ]
        new_data = redo_last_round(
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

        assert new_data[-1]["drop"] == ["George"]
        assert new_data[-1]["buys"] == ["George"]
