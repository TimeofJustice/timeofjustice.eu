from django.contrib import admin

from games.models import Wallet, Vault


# Register your models here.
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('wallet_id', 'name', 'balance', 'created_at', 'last_visit')


@admin.register(Vault)
class VaultAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance', 'last_redemption')
