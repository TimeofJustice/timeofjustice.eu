from django.db import models
from django.utils import timezone

class Wallet(models.Model):
    wallet_id = models.CharField(primary_key=True, max_length=32, editable=False)
    name = models.CharField(max_length=32, default="Anonymous")
    balance = models.IntegerField(default=100)
    days_played = models.IntegerField(default=0)
    last_visit = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hint_dismissed = models.BooleanField(default=False)

    def __str__(self):
        return self.wallet_id

    def json(self):
        if self.last_visit is None:
            self.last_visit = timezone.now().date()
            self.save()
        elif 2 <= (timezone.now().date() - self.last_visit).days:
            self.days_played = 0
            self.save()

        return {
            "walletId": self.wallet_id,
            "name": self.name,
            "balance": int(self.balance),
            "streak": int(self.days_played),
            "hintDismissed": self.hint_dismissed,
        }

    def public_json(self):
        if self.last_visit is None:
            self.last_visit = timezone.now().date()
            self.save()
        elif 2 <= (timezone.now().date() - self.last_visit).days:
            self.days_played = 0
            self.save()

        return {
            "name": self.name,
            "balance": int(self.balance),
            "streak": int(self.days_played),
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
