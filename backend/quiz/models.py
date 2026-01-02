import random
import string

from django.db import models


def generate_session_id(length=6):
    """Generiert einen zufälligen 6-stelligen alphanumerischen Hash"""
    chars = string.ascii_uppercase + string.digits  # A-Z + 0-9
    return ''.join(random.choices(chars, k=length)) # noqa: S311

def generate_host_id(length=8):
    """Generiert eine zufällige Host-ID (z.B. 8 Zeichen)"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length)) # noqa: S311


class QuizSession(models.Model):
    """
    Persistente Quiz-Session.
    PK ist ein 6-stelliger Hash.
    Spieler bleiben anonym.
    """
    id = models.CharField(
        max_length=6,
        primary_key=True,
        default=generate_session_id,
        editable=False,
        unique=True,
    )

    # quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    host_id = models.CharField(
        max_length=8,
        default=generate_host_id,
        unique=True,
        editable=False,
    )
    max_players = models.PositiveIntegerField(default=4)
    time_per_question = models.PositiveIntegerField(default=15)
    mode = models.CharField(max_length=50, default="classic")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id}"
