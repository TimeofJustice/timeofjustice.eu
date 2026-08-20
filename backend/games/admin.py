from django.contrib import admin, messages

from games.models import Avatar, Vault, Wallet
from games.wallet import assign_wallet_phrase


# Register your models here.
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("public_id", "name", "avatar", "balance", "created_at", "last_visit")
    list_filter = ("avatar",)
    search_fields = ("public_id", "name")
    actions = ("issue_wallet_phrase",)

    @admin.action(description="Issue a new wallet phrase (the old one stops working)")
    def issue_wallet_phrase(self, request, queryset):
        """
        Phrases are stored only as a keyed hash, so there is no way to look one
        up — the replacement is shown here once and has to be passed on by hand.
        """
        for wallet in queryset:
            phrase = assign_wallet_phrase(wallet)

            self.message_user(
                request,
                f"{wallet.public_id} ({wallet.name}) — new wallet phrase: {phrase}",
                messages.WARNING,
            )


@admin.register(Vault)
class VaultAdmin(admin.ModelAdmin):
    list_display = ("id", "balance", "last_redemption")


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image", "order")
    ordering = ("order", "id")
