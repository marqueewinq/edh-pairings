import datetime as dt
import typing as ty
import urllib.parse as urlparse

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now
from rest_framework.reverse import reverse


def create_token(user: User) -> str:
    encoded = jwt.encode(
        payload={
            "user_id": user.id,
            "expires_at": (now() + dt.timedelta(days=1)).isoformat(),
        },
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return ty.cast(str, encoded)


def validate_token(token: str) -> ty.Optional[User]:
    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
    expires_at = dt.datetime.fromisoformat(payload["expires_at"])
    if now() > expires_at:
        return None
    return User.objects.filter(id=payload["user_id"], is_active=True).first()


def get_login_link(user: User) -> str:
    return urlparse.urljoin(
        settings.BASE_URL,
        reverse("user-loginless", kwargs={"token": create_token(user)}),
    )
