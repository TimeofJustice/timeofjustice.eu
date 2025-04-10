from django.contrib import admin

from casino.models import Wallet


# Register your models here.
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('wallet_id', 'name', 'balance', 'created_at', 'last_visit')
