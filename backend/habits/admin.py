from django.contrib import admin

from habits.models import Entry, Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "wallet", "goal", "unit", "step", "archived")
    list_filter = ("archived",)
    search_fields = ("name", "wallet__public_id", "wallet__name")


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("id", "habit", "date", "value")
    list_filter = ("date",)
    search_fields = ("habit__name",)
