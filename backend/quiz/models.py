import secrets
import string

from django.db import models

from backend import settings


def generate_session_id():
    while True:
        session_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        if not Session.objects.filter(id=session_id).exists():
            return session_id

def generate_player_id():
    while True:
        player_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        if not Player.objects.filter(id=player_id).exists():
            return player_id


class PlayerGIF(models.Model):
    id = models.AutoField(primary_key=True)
    gif = models.FileField(upload_to=f"{settings.FILE_DESTINATION}quiz/gifs/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GIF {self.id}"


class Session(models.Model):
    id = models.CharField(
        max_length=6,
        primary_key=True,
        editable=False,
        unique=True,
        default=generate_session_id,
    )
    max_players = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id}"


class Player(models.Model):
    id = models.CharField(
        max_length=16,
        primary_key=True,
        editable=False,
        unique=True,
        default=generate_player_id,
    )
    name = models.CharField(max_length=50)
    gif = models.ForeignKey(PlayerGIF, on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    is_host = models.BooleanField(default=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='players')

    class Meta:
        unique_together = ('name', 'session')

    def __str__(self):
        return f"Player {self.id} in Session {self.session.id}"

    def json(self):
        return {
            "name": self.name,
            "gif": f"{settings.FILE_DESTINATION}images{self.gif.gif.url}" if self.gif else None,
            "is_host": self.is_host,
        }
