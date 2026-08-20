from django.utils import timezone

from core.helpers import get_or_none
from games import models


def get_vault():
    """The single house vault, resetting it if the daily window has passed."""
    vault = get_or_none(models.Vault, id=1)

    if not vault:
        vault = models.Vault.objects.create(id=1, last_redemption=timezone.now().date())

    vault_reset = timezone.datetime.combine(vault.last_redemption, timezone.datetime.min.time()) if vault.last_redemption else timezone.now()
    vault_reset = timezone.make_aware(vault_reset) if timezone.is_naive(vault_reset) else vault_reset
    vault_reset = vault_reset + timezone.timedelta(days=1)

    if vault_reset < timezone.now():
        vault.balance = 0
        vault.last_redemption = timezone.now().date()
        vault.save()

    return vault, vault_reset
