from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

# The most a single entry, or a goal, may hold. High enough for step counts
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
    Something the owner tracks a day at a time. Two flavours, one model:

    - `GOAL` is a daily target, met or not. "6000 steps." A year of squares.
    - `MEASURE` is a reading whose *course* is the point. "Weight." A line,
      where `goal` is a target to move towards.

    Logging, the day editor and the quick-add are shared, which is why they are
    one model and not two.
    """

    GOAL = "goal"
    MEASURE = "measure"

    KINDS = (
        (GOAL, "Daily goal"),
        (MEASURE, "Measurement over time"),
    )

    id = models.AutoField(primary_key=True)
    kind = models.CharField(max_length=8, choices=KINDS, default=GOAL)
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
    # The top of the goal zone, where there is one. With it, `goal` stops being
    # a bar to clear and becomes the bottom of a band: 120 to 140 grams of
    # protein, where 200 misses the day exactly as 100 does. Null for the
    # ordinary "as much as you can" goal, which is most of them.
    goal_max = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(SMALLEST), MaxValueValidator(MAX_VALUE)],
    )
    # What one tap on the quick-add button adds: 1000 for steps, 1 for glasses
    # of water, 0.5 for half an hour.
    step = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        default=Decimal(1),
        validators=[MinValueValidator(SMALLEST), MaxValueValidator(MAX_VALUE)],
    )
    color = models.CharField(max_length=7, default="#198754", validators=[HEX_COLOR])
    order = models.IntegerField(default=0)
    # The weekdays the goal is not asked on, Monday as 0, e.g. [5, 6] for a
    # habit that rests at the weekend. A schedule rather than a list of dates:
    # a rest day is usually a standing arrangement ("no running on Sundays"),
    # and one kept as a rule needs no upkeep as the weeks go by.
    #
    # It is worth knowing that this reaches backwards as well as forwards:
    # marking Sundays off excuses every Sunday there has ever been, because the
    # grid and the streaks are all read through the rule as it stands now.
    rest_days = models.JSONField(default=list, blank=True)
    # Whether the panel takes a whole row rather than sharing one. A year of
    # squares reads better wide; a habit with little history does not need it.
    wide = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Habit"
        verbose_name_plural = "Habits"

    def __str__(self):
        return f"{self.name} ({self.wallet_id})"

    def met_by(self, value):
        """
        Whether a day's value counts as the goal reached.

        The one place the rule lives, so a zone cannot mean one thing to the
        streaks and another to the grid.
        """
        return value >= self.goal and (self.goal_max is None or value <= self.goal_max)

    def json(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "unit": self.unit,
            # Floats on the wire: JSON has no decimal, and two places survive
            # a double intact.
            "goal": float(self.goal),
            "goalMax": float(self.goal_max) if self.goal_max is not None else None,
            "step": float(self.step),
            "color": self.color,
            "restDays": list(self.rest_days or ()),
            "order": self.order,
            "wide": self.wide,
            "archived": self.archived,
            "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class Entry(models.Model):
    """
    How much of a habit happened on one day. Absent means "nothing logged",
    which the grid paints the same as a zero, so a zero is never stored.
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


class Recap(models.Model):
    """
    How far a wallet's look back at its own week has got.

    `last_week` is the Monday of the most recent week the owner has been shown.
    A week that has ended and is still ahead of this is one they have not seen,
    which is what makes the recap open by itself exactly once per week, and what
    turns a long absence into a single span rather than a queue of dialogs.
    """

    wallet = models.OneToOneField("games.Wallet", on_delete=models.CASCADE, related_name="habit_recap")
    last_week = models.DateField()

    class Meta:
        verbose_name = " Recap"
        verbose_name_plural = " Recaps"

    def __str__(self):
        return f"{self.wallet_id} through {self.last_week}"
