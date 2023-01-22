from accounts.auth import get_login_link
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail


def send_mail_login_link(user: User) -> int:
    template = """
    <p>Hi, {username}! Thank you for using our service. </p>
    <br>
    <p>Here's the <a href="{login_link}">login link</a> for you. </p>
    <p>Or copy-paste this link to your browser: </p>
    <pre>
    {login_link}
    </pre>
    <br>
    <p>Make sure that your link stays safe. Do not share it unless you want others
    to be able to log in to your account.</p>
    <br>
    <p>This link will expire in the next 24 hours.</p>
    <br>
    <p>Yours, edh-pairings team. ^.^ </p>
    """
    sent = send_mail(
        subject="Log in to edh-pairings",
        message="",
        from_email=settings.EMAIL_FROM,
        recipient_list=[user.email],
        html_message=template.format(
            login_link=get_login_link(user), username=user.username
        ),
    )
    return sent
