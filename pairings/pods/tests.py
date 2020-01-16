from django.urls import reverse
from rest_framework.test import APITestCase
from pods.models import Tournament, PlayerName


class IntegrationApiTest(APITestCase):
    def test_add_player_to_tournament(self):
        tour = Tournament.objects.create(name="t1")
        for _ in range(2):
            # loop to assert duplicates not added twice
            data = {"player": {"name": "Fred"}}
            response = self.client.post(
                reverse("api_tournament_add", kwargs={"id": tour.id}), data, format="json"
            )
            assert response.status_code == 200, response.json()
            assert PlayerName.objects.filter(name="Fred").count() == 1
            assert tour.players.count() == 1

        

