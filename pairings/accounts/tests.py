import logging
import uuid

from accounts.mailing import get_login_link
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from rest_framework import status, test


class SingUpIntegrationTest(test.APITestCase):
    def setUp(self):
        logging.getLogger("django.request").setLevel(logging.ERROR)

    def test_sign_up_sends_mail_login_link(self):
        username = str(uuid.uuid4())
        email = f"{username}@example.com"

        response = self.client.post(
            reverse("user-send-link"),
            {"email": email},
            format="json",
        )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)
        self.assertIn(
            "edh-pairings",
            outbox[0].subject,
        )
        self.assertEqual(outbox[0].to, [email])
        message = str(outbox[0].message())
        # print(outbox[0].message())
        self.assertIn("loginless", message)
        self.assertIn(username, message)

    def test_user_can_change_attributes(self):
        username = "username"
        email = "username@example.com"

        user = User.objects.create(username=username, email=email)
        user_id = user.id

        user = User.objects.get(id=user_id)
        self.assertEqual(username, user.username)
        self.assertEqual(email, user.email)

        response = self.client.put(
            reverse("user-detail", kwargs={"pk": user_id}),
            {"username": username + username, "email": username + email},
            format="json",
        )
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        self.client.force_authenticate(user=user)

        response = self.client.put(
            reverse("user-detail", kwargs={"pk": user_id}),
            {"username": username + username, "email": username + email},
            format="json",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(user_id, response.json()["id"])

        user = User.objects.get(id=user_id)
        self.assertEqual(username + username, user.username)
        self.assertEqual(username + email, user.email)

    def test_login_link_logs_in(self):
        username = "username"
        email = "username@example.com"
        user = User.objects.create(username=username, email=email)

        response = self.client.get(get_login_link(user))
        self.assertEqual(status.HTTP_302_FOUND, response.status_code)
