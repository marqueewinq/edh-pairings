import uuid
from copy import deepcopy as copy

import numpy as np
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from judge.v1.v1 import (
    get_pods,
    get_probability_mat_for_players,
    get_standings,
    new_round_random,
    new_round_with_history,
    redo_last_round,
)
from pods.models import PlayerName, Tournament
from rest_framework import status, test
from rest_framework.authtoken.models import Token


class IntegrationApiTest(test.APITestCase):
    def setUp(self):
        user_data = {"username": "Me", "password": "pwd"}
        self.user = User.objects.create_user(**user_data)
        self.client.force_authenticate(user=self.user)
        self.client.post(reverse("rest_login"), data=user_data, format="json")
        self.token = Token.objects.get(user=self.user).key

    def test_create_tournament(self):
        tournament_name = "Tournament2"
        response = self.client.post(
            reverse("tournament-list"),
            {"name": tournament_name},
            headers={"Authorization": f"Token {self.token}"},
            format="json",
        )
        assert response.status_code == 201, response.json()
        assert Tournament.objects.filter(name=tournament_name).count() == 1
        tour = Tournament.objects.get(name=tournament_name)
        assert tour.owner.pk == self.user.pk

    def test_add_remove_drop_player_to_tournament(self):
        player_name = "Fred"
        n_total_players = 100
        tour = Tournament.objects.create(name="t1")

        data = {"player": {"name": player_name}}
        for _ in range(2):
            # loop to assert duplicates not added twice
            response = self.client.post(
                reverse("tournament-add-player-to-tournament", kwargs={"id": tour.id}),
                data,
                headers={"Authorization": f"Token {self.token}"},
                format="json",
            )
            assert response.status_code == 204, response.json()
            assert PlayerName.objects.filter(name=player_name).count() == 1
            assert tour.players.count() == 1

        # add some other players to the tournament
        last_name: str
        for _ in range(n_total_players - 1):
            last_name = str(uuid.uuid4())
            response = self.client.post(
                reverse("tournament-add-player-to-tournament", kwargs={"id": tour.id}),
                {"player": {"name": last_name}},
                headers={"Authorization": f"Token {self.token}"},
                format="json",
            )
            assert response.status_code == 204, response.json()
        assert tour.players.count() == n_total_players, tour.players.count()

        response = self.client.delete(
            reverse("tournament-add-player-to-tournament", kwargs={"id": tour.id}),
            {"player": {"name": player_name}},
            headers={"Authorization": f"Token {self.token}"},
            format="json",
        )
        assert response.status_code == 204, response.json()
        assert tour.players.count() == n_total_players - 1, tour.players.count()

        # assert dropping players not participating in the tournament raises 409
        response = self.client.post(
            reverse("tournament-drop-player-from-tournament", kwargs={"id": tour.id}),
            {"player": {"name": player_name}},
            headers={"Authorization": f"Token {self.token}"},
            format="json",
        )
        assert response.status_code == 409, response.json()

        # assert players can be dropped from the tournament
        response = self.client.post(
            reverse("tournament-drop-player-from-tournament", kwargs={"id": tour.id}),
            {"player": {"name": last_name}},
            headers={"Authorization": f"Token {self.token}"},
            format="json",
        )
        assert response.status_code == 204, response.json()

    def test_create_new_round_submit_result_to_tournament(self):
        PlayerName.objects.all().delete()

        tour = Tournament.objects.create(name="t1")
        PlayerName.objects.bulk_create(
            [
                PlayerName(name="Alice"),
                PlayerName(name="Bob"),
                PlayerName(name="Cath"),
                PlayerName(name="Danny"),
                PlayerName(name="Eve"),
            ]
        )
        for player_name in PlayerName.objects.all():
            tour.players.add(player_name)

        # create new round
        response = self.client.post(
            reverse(
                "tournament-create-new-round-in-tournament", kwargs={"id": tour.id}
            ),
            headers={"Authorization": f"Token {self.token}"},
        )
        assert response.status_code == 200, response.json()
        buyed_player = Tournament.objects.get(id=tour.id).data[0]["buys"][
            0
        ]  # assert does not fail

        # submit some results
        scores = {
            "Alice": [1, 2],
            "Bob": [3, 4],
            "Cath": [5, 6],
            "Danny": [7, 8],
            "Eve": [9, 0],
        }
        assert buyed_player in scores.keys()
        scores.pop(buyed_player)
        for name in scores.keys():
            response = self.client.post(
                reverse(
                    "tournament-submit-result-to-tournament", kwargs={"id": tour.id}
                ),
                {"player": {"name": name}, "round_id": 0, "score": scores[name]},
                headers={"Authorization": f"Token {self.token}"},
                format="json",
            )
            assert response.status_code == 200, response.json()

        standings = get_standings(Tournament.objects.get(id=tour.id).data)
        for item in standings:
            if item["player_name"] not in scores:
                assert item["player_name"] == buyed_player
            else:
                assert scores[item["player_name"]] == item["total_score"]

    def test_redo_last_round_in_tournament(self):
        PlayerName.objects.all().delete()

        tour = Tournament.objects.create(name="t1")
        PlayerName.objects.bulk_create(
            [
                PlayerName(name="Alice"),
                PlayerName(name="Bob"),
                PlayerName(name="Cath"),
                PlayerName(name="Danny"),
                PlayerName(name="Eve"),
            ]
        )
        for player_name in PlayerName.objects.all():
            tour.players.add(player_name)

        # create new round
        response = self.client.post(
            reverse(
                "tournament-create-new-round-in-tournament", kwargs={"id": tour.id}
            ),
            headers={"Authorization": f"Token {self.token}"},
        )
        assert response.status_code == 200, response.json()
        # redo it several times
        for _ in range(5):
            response = self.client.post(
                reverse(
                    "tournament-redo-last-round-in-tournament", kwargs={"id": tour.id}
                ),
                headers={"Authorization": f"Token {self.token}"},
            )
            assert response.status_code == 200, response.json()

    def test_submit_result_to_tournament_player_not_in_tournament__409(self):
        # tournament-submit-result-to-tournament
        PlayerName.objects.all().delete()

        tour = Tournament.objects.create(name="t1")
        PlayerName.objects.bulk_create(
            [
                PlayerName(name="added_Alice"),
                PlayerName(name="added_Bob"),
                PlayerName(name="added_Cath"),
                PlayerName(name="added_Danny"),
                PlayerName(name="Eve"),
            ]
        )
        for player_name in PlayerName.objects.filter(name__contains="added_"):
            tour.players.add(player_name)

        eve = PlayerName.objects.get(name="Eve")
        assert tour.players.filter(name=eve.name).count() == 0

        response = self.client.post(
            reverse(
                "tournament-create-new-round-in-tournament", kwargs={"id": tour.id}
            ),
            headers={"Authorization": f"Token {self.token}"},
        )
        assert response.status_code == 200, response.json()
        response = self.client.post(
            reverse("tournament-submit-result-to-tournament", kwargs={"id": tour.id}),
            {"player": {"name": eve.name}, "round_id": 0, "score": [3, 1]},
            headers={"Authorization": f"Token {self.token}"},
            format="json",
        )
        assert response.status_code == 400, response


class PermissionTests(test.APITestCase):
    def setUp(self):
        self.user = User.objects.create_user({"username": "user", "password": "user"})
        self.other = User.objects.create_user(
            {"username": "other", "password": "other"}
        )
        self.admin = User.objects.create_user(
            {"username": "admin", "password": "admin"}
        )
        self.admin.is_staff = True
        self.admin.save()

        self.token = ""

        self.user_tournament = Tournament.objects.create(
            name="user",
            owner=self.user,
        )
        self.other_tournament = Tournament.objects.create(
            name="other", owner=self.other
        )
        self.admin_tournament = Tournament.objects.create(
            name="admin", owner=self.admin
        )
        self.legacy_tournament = Tournament.objects.create(
            name="legacy",
            owner=None,
        )

    def _login_as(self, user):
        self.user = user
        self.client.force_authenticate(user=self.user)
        self.client.post(
            reverse("rest_login"),
            data={"username": self.user.username, "password": self.user.username},
            format="json",
        )
        self.token = Token.objects.get(user=self.user).key

    def _logout(self):
        self.client.logout()
        self.token = ""

    def _headers(self):
        if len(self.token) == 0:
            return {}
        return {"Authorization": f"Token {self.token}"}

    def _read_only_api(self):
        yield "tournament-list", self.client.get(
            reverse("tournament-list"), format="json", **self._headers()
        )
        for tournament in [
            self.user_tournament,
            self.other_tournament,
            self.admin_tournament,
            self.legacy_tournament,
        ]:
            yield f"tournament-detail-{tournament.name}", self.client.get(
                reverse("tournament-detail", kwargs={"id": tournament.id}),
                **self._headers(),
            )

    def _write_api(self):
        yield "tournament-list", self.client.post(
            reverse("tournament-list"),
            {"name": "t1"},
            format="json",
            **self._headers(),
        )
        for tournament in [
            self.user_tournament,
            self.other_tournament,
            self.admin_tournament,
            self.legacy_tournament,
        ]:
            yield f"tournament-create-new-round-in-tournament-{tournament.name}", self.client.post(
                reverse(
                    "tournament-create-new-round-in-tournament",
                    kwargs={"id": tournament.id},
                ),
                {},
                format="json",
                **self._headers(),
            )

    def test_access_anonymous(self):
        self._logout()
        for rev, response in self._read_only_api():
            assert status.is_success(response.status_code), (rev, response)

        for rev, response in self._write_api():
            assert status.is_client_error(response.status_code), (rev, response)

    def test_access_regular(self):
        self._login_as(self.user)
        for rev, response in self._read_only_api():
            assert status.is_success(response.status_code), (rev, response)

        expected = [True, True, False, False, True]
        for (rev, response), expected_success in zip(self._write_api(), expected):
            if expected_success:
                assert status.is_success(response.status_code), (rev, response)
            else:
                assert status.is_client_error(response.status_code), (rev, response)

    def test_access_staff(self):
        self._login_as(self.admin)
        for rev, response in self._read_only_api():
            assert status.is_success(response.status_code), (rev, response)

        for rev, response in self._write_api():
            assert status.is_success(response.status_code), (rev, response)


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
