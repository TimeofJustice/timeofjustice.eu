import uuid

from django.db import models

# Create your models here.
class Wallet(models.Model):
    wallet_id = models.CharField(primary_key=True, default=uuid.uuid4().hex, max_length=32, editable=False)
    name = models.CharField(max_length=32, default="Anonymous")
    balance = models.DecimalField(max_digits=20, decimal_places=0, default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet_id

    def json(self):
        return {
            "walletId": self.wallet_id,
            "name": self.name,
            "balance": int(self.balance),
        }

    def public_json(self):
        return {
            "name": self.name,
            "balance": int(self.balance),
        }
