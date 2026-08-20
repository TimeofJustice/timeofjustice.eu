from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from itertools import pairwise

from django.db import IntegrityError, transaction
from django.db.models import F, Max
from django.http.response import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from inertia import render

from core.helpers import BodyContent, default_props
from games.decorators import wallet_api_required, wallet_required
from games.wallet import get_wallet
from habits.models import MAX_HABITS_PER_WALLET, MAX_VALUE, SMALLEST, Entry, Habit

# The site did not exist before this. There is no offset at the other end:
# a habit is looked back on, never planned ahead.
FIRST_YEAR = 2020

# Offered in the habit form. Every one of them reads on the dark surface.
COLORS = ("#198754", "#0dcaf0", "#ffc107", "#dc3545", "#d63384", "#6f42c1", "#0d6efd", "#fd7e14")

DEFAULT_COLOR = COLORS[0]

# What a habit with nothing to its name yet reports.
NO_STREAK = {"current": 0, "longest": 0}


def year_bounds():
    """The years the tracker will show, oldest first. It stops at this one."""
    return FIRST_YEAR, timezone.now().date().year


def clamp_year(year):
    first, last = year_bounds()

    return max(first, min(last, year))


def to_decimal(raw):
    """
    Parses a number the way a person writes one, comma included, pinned to two
    decimals. `None` for anything else: `Decimal` parses "nan" quite happily,
    which would poison every comparison.
    """
    try:
        number = Decimal(str(raw).replace(",", ".").strip())
    except (AttributeError, InvalidOperation, TypeError, ValueError):
        return None

    if not number.is_finite():
        return None

    return number.quantize(SMALLEST)


def entries_for(wallet, year):
    """
    Every logged value of one year, as `{habit id: {"YYYY-MM-DD": value}}`.

    One query for the whole page: a year of a dozen habits is a few thousand
    small numbers, which is far cheaper to ship once than to fetch per habit.
    """
    rows = Entry.objects.filter(habit__wallet=wallet, date__year=year).values_list("habit_id", "date", "value")

    entries = {}

    for habit_id, day, value in rows:
        entries.setdefault(str(habit_id), {})[day.isoformat()] = float(value)

    return entries


def streak_of(met, today):
    """The current and the longest run inside a set of goal-met days."""
    # Today is still open, so a streak is not broken until yesterday was missed.
    cursor = today if today in met else today - timedelta(days=1)
    current = 0

    while cursor in met:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0

    for day in met:
        # Each run is walked once, from the day that starts it.
        if day - timedelta(days=1) in met:
            continue

        run = 0
        probe = day

        while probe in met:
            run += 1
            probe += timedelta(days=1)

        longest = max(longest, run)

    return {"current": current, "longest": longest}


def approach_streak(readings, target):
    """
    Runs of readings that did not move away from the target.

    Counted per **reading**, not per day, so a fortnight without a weigh-in is
    no news rather than a broken run. Holding counts. The steps between readings
    are what is counted, so a single reading is a run of nothing.
    """
    distances = [abs(value - target) for value in readings]

    current = 0
    longest = 0

    for previous, distance in pairwise(distances):
        current = current + 1 if distance <= previous else 0
        longest = max(longest, current)

    return {"current": current, "longest": longest}


def streaks_for(wallet, habit=None):
    """
    Runs per habit id: goal-met days for one kind, readings that closed on their
    target for the other. Over all time, not the year on screen, so a run that
    started in December keeps counting while January is being looked at.
    """
    habits = Habit.objects.filter(wallet=wallet)

    if habit is not None:
        habits = habits.filter(id=habit.id)

    streaks = {}
    today = timezone.now().date()

    # Only goal-met days come back, in one query rather than one per habit.
    met = {}

    for habit_id, day in Entry.objects.filter(habit__in=habits, habit__kind=Habit.GOAL, value__gte=F("habit__goal")).values_list("habit_id", "date"):
        met.setdefault(habit_id, set()).add(day)

    for habit_id, days in met.items():
        streaks[habit_id] = streak_of(days, today)

    targets = dict(habits.filter(kind=Habit.MEASURE).values_list("id", "goal"))

    if targets:
        readings = {}

        for habit_id, value in Entry.objects.filter(habit__in=habits, habit__kind=Habit.MEASURE).order_by("date").values_list("habit_id", "value"):
            readings.setdefault(habit_id, []).append(value)

        for habit_id, values in readings.items():
            streaks[habit_id] = approach_streak(values, targets[habit_id])

    return streaks


def with_streak(habit, streaks):
    """The habit as the frontend wants it: its own fields plus its runs."""
    return habit.json() | {"streak": streaks.get(habit.id, NO_STREAK)}


def habit_of(wallet, habit_id):
    return Habit.objects.filter(wallet=wallet, id=habit_id).first()


def read_habit_fields(post_data, habit):
    """
    Applies the fields present in the body to `habit`.

    Returns an error key, or `None` when the habit is ready to be saved. Every
    field is optional, so the same helper serves creating and editing.
    """
    name = post_data.get("name")

    if name is not None:
        name = str(name).strip()

        if not 1 <= len(name) <= 40:
            return "habits.errors.name_invalid"

        habit.name = name

    unit = post_data.get("unit")

    if unit is not None:
        unit = str(unit).strip()

        if len(unit) > 16:
            return "habits.errors.unit_invalid"

        habit.unit = unit

    for field in ("goal", "step"):
        raw = post_data.get(field)

        if raw is None:
            continue

        number = to_decimal(raw)

        # Checked after rounding: 0.001 is a typo, not a goal, and it would
        # otherwise pass as positive and then be stored as zero.
        if number is None or not SMALLEST <= number <= MAX_VALUE:
            return f"habits.errors.{field}_invalid"

        setattr(habit, field, number)

    color = post_data.get("color")

    if color is not None:
        if color not in COLORS:
            return "habits.errors.color_invalid"

        habit.color = color

    kind = post_data.get("kind")

    if kind is not None:
        if kind not in dict(Habit.KINDS):
            return "habits.errors.kind_invalid"

        habit.kind = kind

    wide = post_data.get("wide")

    if wide is not None:
        habit.wide = bool(wide)

    archived = post_data.get("archived")

    if archived is not None:
        habit.archived = bool(archived)

    if not habit.name:
        return "habits.errors.name_invalid"

    return None


@wallet_required
def index(request, year=None):
    wallet = get_wallet(request)
    first, last = year_bounds()
    selected_year = clamp_year(int(year) if year else timezone.now().date().year)
    streaks = streaks_for(wallet)

    page_props = {
        "year": selected_year,
        "firstYear": first,
        "lastYear": last,
        "today": timezone.now().date().isoformat(),
        "colors": list(COLORS),
        "habits": [with_streak(habit, streaks) for habit in Habit.objects.filter(wallet=wallet)],
        "entries": entries_for(wallet, selected_year),
    }

    return render(request, "HabitTrackerPage", props=default_props(page_props, request))


@wallet_api_required
def year(request, year):
    """The entries of another year, so switching years does not reload the page."""
    selected_year = clamp_year(int(year))

    return JsonResponse({"year": selected_year, "entries": entries_for(get_wallet(request), selected_year)})


@wallet_api_required
@require_http_methods(["POST"])
def create(request):
    wallet = get_wallet(request)

    if Habit.objects.filter(wallet=wallet).count() >= MAX_HABITS_PER_WALLET:
        return JsonResponse({"error": "habits.errors.too_many"}, status=400)

    habit = Habit(wallet=wallet, name="", color=DEFAULT_COLOR)
    error = read_habit_fields(BodyContent(request), habit)

    if error:
        return JsonResponse({"error": error}, status=400)

    # New habits land at the bottom of the page, where the form was.
    habit.order = (Habit.objects.filter(wallet=wallet).aggregate(last=Max("order"))["last"] or 0) + 1
    habit.save()

    return JsonResponse({"habit": with_streak(habit, {})})


@wallet_api_required
@require_http_methods(["POST"])
def update(request, habit_id):
    habit = habit_of(get_wallet(request), habit_id)

    if not habit:
        return JsonResponse({"error": "habits.errors.unknown_habit"}, status=404)

    error = read_habit_fields(BodyContent(request), habit)

    if error:
        return JsonResponse({"error": error}, status=400)

    habit.save()

    # Recomputed, not carried over: moving the goal changes which days met it.
    return JsonResponse({"habit": with_streak(habit, streaks_for(habit.wallet, habit))})


@wallet_api_required
@require_http_methods(["POST"])
def layout(request):
    """
    Rewrites the running order of the panels, and which take a whole row.

    Takes the arrangement in full, `[{"id": .., "wide": ..}, ..]`, not a move to
    apply, so a dropped request cannot leave the board half rearranged.
    """
    wallet = get_wallet(request)
    panels = BodyContent(request).get("habits")

    if not isinstance(panels, list):
        return JsonResponse({"error": "habits.errors.invalid_layout"}, status=400)

    habits = {habit.id: habit for habit in Habit.objects.filter(wallet=wallet)}
    ordered = []

    for position, panel in enumerate(panels):
        if not isinstance(panel, dict):
            return JsonResponse({"error": "habits.errors.invalid_layout"}, status=400)

        habit = habits.get(panel.get("id"))

        # A habit that is not this wallet's simply is not in the map, so a
        # forged id rearranges nothing.
        if habit is None:
            return JsonResponse({"error": "habits.errors.unknown_habit"}, status=404)

        habit.order = position
        habit.wide = bool(panel.get("wide"))
        ordered.append(habit)

    Habit.objects.bulk_update(ordered, ("order", "wide"))

    return JsonResponse({"habits": [habit.json() for habit in ordered]})


@wallet_api_required
@require_http_methods(["POST"])
def delete(request, habit_id):
    habit = habit_of(get_wallet(request), habit_id)

    if not habit:
        return JsonResponse({"error": "habits.errors.unknown_habit"}, status=404)

    # The entries go with it, since they mean nothing without their habit.
    habit.delete()

    return JsonResponse({"id": habit_id})


@wallet_api_required
@require_http_methods(["POST"])
def log(request, habit_id):
    """
    Sets one day of one habit to an absolute value.

    Absolute rather than a delta on purpose: the quick-add buttons already know
    the current value, and a retried request must not count twice.
    """
    habit = habit_of(get_wallet(request), habit_id)

    if not habit:
        return JsonResponse({"error": "habits.errors.unknown_habit"}, status=404)

    post_data = BodyContent(request)

    try:
        day = date.fromisoformat(str(post_data.get("date")))
    except (TypeError, ValueError):
        return JsonResponse({"error": "habits.errors.date_invalid"}, status=400)

    first, _ = year_bounds()

    # Only the past can be logged: a day that has not happened yet has nothing
    # to report, and letting it be filled in would make every streak a guess.
    if day.year < first:
        return JsonResponse({"error": "habits.errors.date_invalid"}, status=400)

    if day > timezone.now().date():
        return JsonResponse({"error": "habits.errors.future"}, status=400)

    value = to_decimal(post_data.get("value"))

    if value is None or not 0 <= value <= MAX_VALUE:
        return JsonResponse({"error": "habits.errors.value_invalid"}, status=400)

    if value == 0:
        # An empty day is stored as no row at all, so the grid only ever has to
        # ask "is there an entry?".
        Entry.objects.filter(habit=habit, date=day).delete()
    else:
        try:
            with transaction.atomic():
                Entry.objects.update_or_create(habit=habit, date=day, defaults={"value": value})
        except IntegrityError:
            # Two taps racing for the same untouched day: the loser just writes.
            Entry.objects.filter(habit=habit, date=day).update(value=value)

    return JsonResponse(
        {
            "habitId": habit.id,
            "date": day.isoformat(),
            "value": float(value),
            # Sent back so the flame in the header follows the tap that fed it.
            "streak": streaks_for(habit.wallet, habit).get(habit.id, NO_STREAK),
        },
    )
