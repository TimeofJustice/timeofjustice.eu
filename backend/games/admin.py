from django.contrib import admin

from games.models import Avatar, Vault, Wallet


# Register your models here.
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("wallet_id", "name", "avatar", "balance", "created_at", "last_visit")
    list_filter = ("avatar",)
    search_fields = ("wallet_id", "name")


@admin.register(Vault)
class VaultAdmin(admin.ModelAdmin):
    list_display = ("id", "balance", "last_redemption")


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image", "order")
    ordering = ("order", "id")
