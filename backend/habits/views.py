from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from itertools import pairwise

from django.db import IntegrityError, transaction
from django.db.models import F, Max, Q
from django.http.response import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from inertia import render

from core.helpers import BodyContent, default_props
from games.decorators import wallet_api_required, wallet_required
from games.wallet import get_wallet
from habits.models import MAX_HABITS_PER_WALLET, MAX_VALUE, SMALLEST, Entry, Habit, Recap

# The site did not exist before this. There is no offset at the other end:
# a habit is looked back on, never planned ahead.
FIRST_YEAR = 2020

# Offered in the habit form. Every one of them reads on the dark surface.
COLORS = ("#198754", "#0dcaf0", "#ffc107", "#dc3545", "#d63384", "#6f42c1", "#0d6efd", "#fd7e14")

DEFAULT_COLOR = COLORS[0]

# What a habit with nothing to its name yet reports.
NO_STREAK = {"current": 0, "longest": 0}

# Stands for "this field was not in the body at all", which is not the same as
# a field sent as null. Only the nullable ones need to tell the two apart.
KEEP = object()

# Monday as 0, the way the grid reads a week. A habit that rests on every one of
# them would never be asked for anything, so one day always has to remain.
WEEKDAYS = range(7)

# The unit the look back thinks in. A week that has ended is a week that can be
# reported on; the one being lived cannot.
WEEK = timedelta(days=7)

# From this many unseen weeks on, the span stops being a week to go through
# habit by habit and becomes a welcome back instead.
AWAY_WEEKS = 2


def year_bounds():
    """The years the tracker will show, oldest first. It stops at this one."""
    return FIRST_YEAR, timezone.now().date().year


def clamp_year(year):
    first, last = year_bounds()

    return max(first, min(last, year))


def navigable_years(wallet, today):
    """
    The years the arrows may walk through, oldest first.

    A year is in the list because it holds something, plus the current one,
    which is always reachable since it is where logging happens. Empty years
    are left out on purpose: paging back through a decade of blank grids is not
    browsing, and there is nothing there to see.

    Reaching further back is still possible, it is just not done with the
    arrows: the day editor takes any date from `FIRST_YEAR` on, and a year
    joins this list the moment it holds an entry.
    """
    years = {day.year for day in Entry.objects.filter(habit__wallet=wallet).dates("date", "year")}
    years.add(today.year)

    return sorted(years)


def nearest_year(years, requested):
    """
    The reachable year closest to the one asked for.

    A year can be typed into the URL, and it may well be one that was never
    logged in. Rather than showing an empty grid the page lands on the nearest
    year that has something, preferring the older one when it sits between two.
    """
    return min(years, key=lambda year: (abs(year - requested), year))


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


def streak_of(met, rests, today):
    """
    The current and the longest run inside a set of goal-met days.

    `rests` holds the weekdays the goal is not asked on, Monday as 0. Such a day
    is neither a hit nor a miss: it does not break a run and it does not lengthen
    one. The run steps straight over it, which is what a rest day is for.
    """
    current = 0
    cursor = today
    # Nothing older than the oldest met day can add to the run. Stopping there
    # is also what keeps a habit that rests on nearly every weekday from walking
    # backwards through empty years.
    floor = (min(met) if met else today) - timedelta(days=len(WEEKDAYS))

    while cursor >= floor:
        if cursor in met:
            current += 1
        # Today is still open, so it is not a miss until it has been slept on.
        elif cursor.weekday() not in rests and cursor != today:
            break

        cursor -= timedelta(days=1)

    longest = 0
    run = 0
    previous = None

    for day in sorted(met):
        # Two met days belong to the same run when every day between them was
        # one off. Adjacent days have nothing between them, so they always do.
        gap = range(1, (day - previous).days) if previous else ()
        bridged = all((previous + timedelta(days=offset)).weekday() in rests for offset in gap)

        run = run + 1 if previous and bridged else 1
        longest = max(longest, run)
        previous = day

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

    # The zone's upper bound has to be applied here rather than in Python: this
    # is every goal-met day of all time, and the point of one query was not to
    # bring them all back to be sifted. `met_by` says the same thing in one place.
    within = Q(value__gte=F("habit__goal")) & (Q(habit__goal_max__isnull=True) | Q(value__lte=F("habit__goal_max")))

    for habit_id, day in Entry.objects.filter(within, habit__in=habits, habit__kind=Habit.GOAL).values_list("habit_id", "date"):
        met.setdefault(habit_id, set()).add(day)

    # Every daily goal, not only the ones with a day to their name: the rest
    # days come off the habit itself now, and a habit with nothing logged still
    # reports the same run of nothing it always did.
    for habit_id, days in habits.filter(kind=Habit.GOAL).values_list("id", "rest_days"):
        streaks[habit_id] = streak_of(met.get(habit_id, set()), set(days or ()), today)

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

    # A sentinel rather than `None`: null is how the top of the zone is taken
    # off again, and a key that is simply absent has to go on meaning "leave it".
    maximum = post_data.get("goalMax", KEEP)

    if maximum is not KEEP:
        if maximum in (None, ""):
            habit.goal_max = None
        else:
            number = to_decimal(maximum)

            if number is None or not SMALLEST <= number <= MAX_VALUE:
                return "habits.errors.goal_max_invalid"

            # Read after `goal`, so the two are compared as they will be stored
            # even when both arrive in the same request.
            if number < habit.goal:
                return "habits.errors.goal_max_below"

            habit.goal_max = number

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

    # A measurement's goal is a target to move towards, not a bar to clear, so
    # there is no band around it to stay inside. Cleared rather than refused:
    # the field is not on screen for this kind, so an error about it would be
    # about something the owner cannot see.
    if habit.kind == Habit.MEASURE:
        habit.goal_max = None

    weekdays = post_data.get("restDays")

    if weekdays is not None:
        if not isinstance(weekdays, list):
            return "habits.errors.rest_days_invalid"

        try:
            days = {int(day) for day in weekdays}
        except (TypeError, ValueError):
            return "habits.errors.rest_days_invalid"

        # A habit that is never asked for anything is not a habit, and a run
        # counted over nothing but days off would never end.
        if not days <= set(WEEKDAYS) or len(days) >= len(WEEKDAYS):
            return "habits.errors.rest_days_invalid"

        habit.rest_days = sorted(days)

    wide = post_data.get("wide")

    if wide is not None:
        habit.wide = bool(wide)

    archived = post_data.get("archived")

    if archived is not None:
        habit.archived = bool(archived)

    if not habit.name:
        return "habits.errors.name_invalid"

    return None


def monday_of(day):
    return day - timedelta(days=day.weekday())


def entries_between(wallet, start, end):
    """`{habit id: {date: value}}` over a span. Dates stay dates here."""
    entries = {}

    for habit_id, day, value in Entry.objects.filter(habit__wallet=wallet, date__range=(start, end)).values_list("habit_id", "date", "value"):
        entries.setdefault(habit_id, {})[day] = value

    return entries


def days_in(values, start, end):
    """The logged days of one span for one habit, oldest first."""
    return [(day, value) for day, value in sorted(values.items()) if start <= day <= end]


def habit_span(habit, values, start, end, carried):
    """
    What one habit did over a span.

    Both kinds report `logged`, the days that got an entry. Past that they have
    nothing in common: a goal counts the days it was met and what they add up
    to, a measurement reports where it stands and which way it moved. Whatever
    a kind has no answer for stays null rather than zero, so the frontend can
    tell "nothing to say" from "nothing happened".
    """
    logged = days_in(values, start, end)

    if habit.kind == Habit.MEASURE:
        readings = [value for _, value in logged]

        if not readings:
            return {"logged": 0, "values": {}, "done": None, "total": None, "latest": None, "delta": None, "closed": None}

        # The reading in force going into the span is the honest starting
        # point: a week with a single weigh-in has still moved somewhere since
        # the last one, and comparing it against itself would say it had not.
        first = carried if carried is not None else readings[0]

        return {
            "logged": len(readings),
            "values": {day.isoformat(): float(value) for day, value in logged},
            "done": None,
            "total": None,
            "latest": float(readings[-1]),
            "delta": float(readings[-1] - first),
            # How much of the gap to the target was closed. The target decides
            # which way is forwards, so a falling weight and a rising balance
            # both read as progress. Same rule as `measureStats` on the frontend.
            "closed": float(abs(first - habit.goal) - abs(readings[-1] - habit.goal)),
        }

    return {
        "logged": len(logged),
        # Only the days that got an entry, so the frontend can draw the span
        # day by day without the empty ones being shipped as zeroes.
        "values": {day.isoformat(): float(value) for day, value in logged},
        "done": sum(1 for _, value in logged if habit.met_by(value)),
        "total": float(sum(value for _, value in logged)),
        "latest": None,
        "delta": None,
        "closed": None,
    }


def totals_of(goals, entries, start, end):
    """
    The span as a whole: goal-days met out of the ones that were asked for, days
    something was logged at all, and days every goal that was asked for came in.

    A day off is not on offer, so it is not in the total either. That is what
    keeps a week of two rest days from reading as a week two days short.
    """
    days = (end - start).days + 1
    done = 0
    asked = 0
    active = set()
    perfect = 0

    for offset in range(days):
        day = start + timedelta(days=offset)
        met = 0
        owed = 0

        for habit in goals:
            if day.weekday() in habit.rest_days:
                continue

            owed += 1
            value = entries.get(habit.id, {}).get(day)

            if value is not None and habit.met_by(value):
                met += 1

        done += met
        asked += owed

        # A day where everything was excused is a day off, not a perfect one.
        if met > 0 and met == owed:
            perfect += 1

    # A measurement counts as activity too, though never as a goal met.
    for values in entries.values():
        active.update(day for day, _ in days_in(values, start, end))

    return {
        "done": done,
        "possible": asked,
        "activeDays": len(active),
        "perfectDays": perfect,
    }


def recap_for(wallet, today, streaks):
    """
    The look back that is owed, or `None` when there is nothing to open.

    One week ending is one recap. `Recap.last_week` remembers how far the owner
    has been shown, so everything past it is what they have not seen, and the
    dialog opens by itself exactly once per week. A wallet that stayed away
    long enough for several weeks to pile up gets one welcome back over the
    whole span rather than a queue of weekly dialogs.

    The row is also skipped forward without opening anything: a week that ended
    before there was a habit to track has nothing to report, and neither has a
    week nothing was logged in.
    """
    last_week = monday_of(today) - WEEK
    state = Recap.objects.filter(wallet=wallet).first()

    if state is None:
        # First sight. The weeks before now were lived without a recap, so they
        # are marked as seen rather than reported all at once.
        Recap.objects.create(wallet=wallet, last_week=last_week)

        return None

    if state.last_week >= last_week:
        return None

    def catch_up():
        state.last_week = last_week
        state.save()

    habits = list(Habit.objects.filter(wallet=wallet))

    if not habits:
        catch_up()

        return None

    weeks = (last_week - state.last_week).days // 7
    start = state.last_week + WEEK
    end = last_week + timedelta(days=6)
    length = (end - start).days + 1

    # The span before it, of the same length, so a week can say which way it
    # went rather than only where it landed.
    previous_start = start - timedelta(days=length)
    previous_end = start - timedelta(days=1)

    entries = entries_between(wallet, previous_start, end)

    # Where each measurement stood going into the span: the last reading before
    # it, which is the one the ordering leaves behind in the dict.
    carried = dict(
        Entry.objects.filter(habit__wallet=wallet, habit__kind=Habit.MEASURE, date__lt=start).order_by("date").values_list("habit_id", "value"),
    )

    span = {habit.id: habit_span(habit, entries.get(habit.id, {}), start, end, carried.get(habit.id)) for habit in habits}

    # Nothing logged in the whole span is not a week worth a dialog. It is a
    # week the tracker was not used, and saying so helps nobody.
    if not any(part["logged"] for part in span.values()):
        catch_up()

        return None

    previous = {habit.id: habit_span(habit, entries.get(habit.id, {}), previous_start, previous_end, None) for habit in habits}
    goals = [habit for habit in habits if habit.kind == Habit.GOAL and not habit.archived]

    # What is still true of a span that was mostly not used. Everything counted
    # inside such a span is a zero, and a zero is the one thing a return does
    # not need pointing out, so the welcome back is built from these instead:
    # the day each habit was last kept, and how many days were kept in total.
    last_logged = dict(Entry.objects.filter(habit__wallet=wallet).values_list("habit_id").annotate(last=Max("date")))
    tracked_days = Entry.objects.filter(habit__wallet=wallet).values("date").distinct().count()

    return {
        "kind": "welcome_back" if weeks >= AWAY_WEEKS else "recap",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": length,
        "weeks": weeks,
        # The last day anything was logged, and the days that were logged over
        # all time. Both reach back past the span, which is the point of them.
        "lastActive": max(last_logged.values()).isoformat() if last_logged else None,
        "trackedDays": tracked_days,
        "habits": [
            habit.json()
            | span[habit.id]
            | {
                "streak": streaks.get(habit.id, NO_STREAK),
                "previousDone": previous[habit.id]["done"],
                "lastLogged": last_logged[habit.id].isoformat() if habit.id in last_logged else None,
            }
            for habit in habits
            # An archived habit is one the owner has stopped tracking. It stays
            # in the recap only for as long as it was still being logged.
            if not habit.archived or span[habit.id]["logged"]
        ],
        "totals": totals_of(goals, entries, start, end),
        "previousTotals": totals_of(goals, entries, previous_start, previous_end),
    }


@wallet_required
def index(request, year=None):
    wallet = get_wallet(request)
    today = timezone.now().date()
    first, _ = year_bounds()
    years = navigable_years(wallet, today)
    selected_year = nearest_year(years, clamp_year(int(year) if year else today.year))
    streaks = streaks_for(wallet)

    page_props = {
        "year": selected_year,
        # The years the arrows offer, and how far back the day editor reaches.
        # They are not the same: browsing follows the entries, while logging may
        # go back to the beginning to create the first of them.
        "years": years,
        "firstYear": first,
        "today": today.isoformat(),
        "colors": list(COLORS),
        "habits": [with_streak(habit, streaks) for habit in Habit.objects.filter(wallet=wallet)],
        "entries": entries_for(wallet, selected_year),
        # Opened by the page itself, once, on the first visit after a week has
        # ended. Null on every other visit.
        "recap": recap_for(wallet, today, streaks),
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


@wallet_api_required
@require_http_methods(["POST"])
def recap_seen(request):
    """
    Marks the look back as done, up to and including the week that just ended.

    Called when the dialog opens rather than when it is closed: a recap that is
    on the screen has been seen, and a tab closed on it must not bring it back
    a second time, nor count as a week away.
    """
    wallet = get_wallet(request)
    last_week = monday_of(timezone.now().date()) - WEEK

    Recap.objects.update_or_create(wallet=wallet, defaults={"last_week": last_week})

    return JsonResponse({"lastWeek": last_week.isoformat()})
