from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from pods.models import Tournament, PlayerName
from pods.judge import new_round_random, get_standings


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
                ]
            },
            {
                "pods": [
                    {
                        "players": ["Albert", "Zyra", "Iffy", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Fred", "Sheldon", "George"],
                        "scores": [[1, 1], [1, 2], [1, 3], [1, 4]],
                    },
                ]
            },
        ]
        new_data = new_round_random(
            data,
            ["Albert", "Fred", "George", "Sexton", "Lily", "Zyra", "Sheldon", "Iffy"],
        )

        assert len(new_data) == 3
        assert len(new_data[2]["pods"]) == 2
        self.assertDictEqual(get_standings(new_data)[0], get_standings(data)[0])
        assert len(new_data[2]["buys"]) == 0
