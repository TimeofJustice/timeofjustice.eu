from django.contrib import admin

from farming_stats.models import Commodity, Crop


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    pass

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    pass
