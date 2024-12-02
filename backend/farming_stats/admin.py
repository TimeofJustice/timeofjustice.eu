from django.contrib import admin

# Register your models here.
from .models import Crop, Commodity

admin.site.register(Crop)
admin.site.register(Commodity)