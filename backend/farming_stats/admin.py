from django.contrib import admin

# Register your models here.
from .models import Commodity, Crop

admin.site.register(Crop)
admin.site.register(Commodity)
