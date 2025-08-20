from django.contrib import admin

from postcard.models import Design, Postcard


# Register your models here.
@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'page_color',
        'background_color',
        'stamp_color',
        'accent_color',
        'text_color',
        'icon',
    )


@admin.register(Postcard)
class PostcardAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message',
        'greetings',
        'design',
        'amount_reports',
        'showcased',
        'created_at',
    )
