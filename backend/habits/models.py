from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

# The most a single entry — or a goal — may hold. High enough for step counts
# and millilitres, low enough that the year grid never has to render a novel.
MAX_VALUE = Decimal(1_000_000_000)

# Two decimals, because half an hour of sleep and a quarter of a litre are
# ordinary things to track. `MAX_DIGITS` has to hold `MAX_VALUE` plus them.
DECIMAL_PLACES = 2
MAX_DIGITS = 12

# The smallest thing that is still worth storing, and therefore the floor for a
# goal and for a quick-add step.
SMALLEST = Decimal("0.01")

# One wallet cannot track an unbounded number of habits: the year page loads
# every entry of every habit at once.
MAX_HABITS_PER_WALLET = 20

HEX_COLOR = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Colors are six-digit hex, e.g. #198754.")


class Habit(models.Model):
    """
    Something the owner wants to do every day, with a daily target — "6000
    steps", "30 minutes of reading". Progress is one `Entry` per day.
    """

    id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey("games.Wallet", on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=40)
    # Free text shown next to the numbers ("steps", "min", "pages"). Optional,
    # because "10 pushups" reads fine without one.
    unit = models.CharField(max_length=16, blank=True)
    goal = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        default=Decimal(1),
        validators=[MinValueValidator(SMALLEST), MaxValueValidator(MAX_VALUE)],
    )
    # How much a single tap on the quick-add button adds. 1000 for steps, 1 for
    # glasses of water, 0.5 for half an hour — this is what makes logging a day
    # a one-click affair.
    step = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        default=Decimal(1),
        validators=[MinValueValidator(SMALLEST), MaxValueValidator(MAX_VALUE)],
    )
    color = models.CharField(max_length=7, default="#198754", validators=[HEX_COLOR])
    order = models.IntegerField(default=0)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Habit"
        verbose_name_plural = "Habits"

    def __str__(self):
        return f"{self.name} ({self.wallet_id})"

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "unit": self.unit,
            # Floats on the wire: JSON has no decimal, and two places survive
            # a double intact.
            "goal": float(self.goal),
            "step": float(self.step),
            "color": self.color,
            "order": self.order,
            "archived": self.archived,
            "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class Entry(models.Model):
    """
    How much of a habit happened on one day. Absent means "nothing logged",
    which the grid paints the same as a zero — so a zero is never stored.
    """

    id = models.AutoField(primary_key=True)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="entries")
    date = models.DateField()
    value = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        default=Decimal(0),
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(MAX_VALUE)],
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "  Entry"
        verbose_name_plural = "  Entries"
        constraints = (models.UniqueConstraint(fields=("habit", "date"), name="unique_entry_per_habit_and_day"),)

    def __str__(self):
        return f"{self.habit.name}: {self.value} on {self.date}"
