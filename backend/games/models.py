from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone


class Avatar(models.Model):
    """
    A picture players can pick for their wallet, managed in the Django admin.

    The upload is deliberately stored untouched — the lazy/compress helpers in
    core.models re-encode through Pillow, which would drop the animation of an
    animated GIF.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=f"{settings.FILE_DESTINATION}images/games/avatars/", max_length=1000)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": f"/{settings.FILE_DESTINATION}images/games/avatars/{Path(self.image.name).name}",
        }


class Wallet(models.Model):
    # Public and safe to show: it tells two players called "Jonas" apart, and it
    # is what the r/place cells point at. Crockford base32, so no I/L/O/U.
    public_id = models.CharField(primary_key=True, max_length=6, editable=False)
    # The wallet phrase itself is never stored — only this keyed hash of it.
    phrase_hash = models.CharField(max_length=64, unique=True, editable=False)
    # Keyed hash of the pre-phrase hex id. Good for exactly one sign-in, which
    # issues a phrase and clears this. Null once used, and for new wallets.
    legacy_id_hash = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)
    name = models.CharField(max_length=32, default="Anonymous")
    balance = models.IntegerField(default=100)
    days_played = models.IntegerField(default=0)
    last_visit = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hint_dismissed = models.BooleanField(default=False)
    avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name}#{self.public_id}"

    def refresh_streak(self):
        """
        Brings the daily streak up to date and returns the number of days since
        the last visit. A gap of two days or more breaks the streak.
        """
        today = timezone.now().date()

        if self.last_visit is None:
            self.last_visit = today
            self.save()
        elif (today - self.last_visit).days >= 2:
            self.days_played = 0
            self.save()

        return (today - self.last_visit).days

    def public_json(self):
        """The fields that are safe to show to everyone, e.g. on the leaderboard."""
        self.refresh_streak()

        return {
            "publicId": self.public_id,
            "name": self.name,
            "balance": int(self.balance),
            "streak": int(self.days_played),
            "avatar": self.avatar.json() if self.avatar else None,
        }

    def needs_setup(self):
        """
        True while the wallet is still wearing its defaults, so the frontend can
        walk the owner through the settings once.
        """
        return self.name == self._meta.get_field("name").default or self.avatar is None

    def json(self):
        """The full wallet, only ever sent to its own owner."""
        return {
            **self.public_json(),
            # The phrase is deliberately absent: it is the credential, and it is
            # served once, by its own endpoint, during first-time setup.
            "needsSetup": self.needs_setup(),
        }


class Vault(models.Model):
    id = models.AutoField(primary_key=True)
    balance = models.IntegerField(default=0)
    last_redemption = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def json(self):
        return {
            "id": self.id,
            "balance": int(self.balance),
            "vaultRedemption": self.last_redemption.strftime("%Y-%m-%dT%H:%M:%SZ") if self.last_redemption else None,
        }
