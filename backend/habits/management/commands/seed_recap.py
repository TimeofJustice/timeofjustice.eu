"""
Two demo wallets for looking at the Momentum recap without waiting a week.

One is a fortnight behind, so the weekly look back opens. The other has been
away for a month, so the same figures arrive as a welcome back. Both are built
from a fixed seed and keyed on a fixed phrase, which is what makes them worth
having: the command can be run again and again and the same two wallets come
back in the same state, ready to be opened once more.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from games.models import Wallet
from games.wallet import hash_wallet_phrase, normalise_wallet_phrase
from habits.models import Entry, Habit, Recap
from habits.views import monday_of

# Fixed, and therefore reusable: these are the phrases to sign in with, and a
# second run rebuilds whatever the first one left behind.
RECAP_PHRASE = "momentum-demo-recap-week"
WELCOME_PHRASE = "momentum-demo-welcome-back"

# Crockford base32, like every other public id: no I, L, O or U.
RECAP_ID = "DEMOR1"
WELCOME_ID = "DEMOW1"

# How far back the days are filled, so a demo wallet has a year panel worth
# looking at rather than a single lit week.
HISTORY_DAYS = 120

# Anything built from this lands in exactly the same place every run.
SEED = 20260829

HABITS = (
    {"name": "Spazieren", "unit": "Schritte", "goal": 6000, "step": 1000, "color": "#198754", "chance": 0.75, "wide": True},
    {"name": "Wasser", "unit": "Gläser", "goal": 8, "step": 1, "color": "#0dcaf0", "chance": 0.65, "wide": False},
    {"name": "Lesen", "unit": "min", "goal": 30, "step": 10, "color": "#6f42c1", "chance": 0.5, "wide": False},
    {"name": "Gewicht", "unit": "kg", "goal": 72, "step": 0.5, "color": "#fd7e14", "kind": Habit.MEASURE, "wide": False},
)


class Command(BaseCommand):
    help = "Builds two demo wallets for the Momentum recap: one week to look back on, and one return after a month away."

    def add_arguments(self, parser):
        parser.add_argument("--away", type=int, default=4, help="Weeks the welcome-back wallet has been gone (2 or more). Default: 4.")
        parser.add_argument("--remove", action="store_true", help="Deletes the two demo wallets and everything on them.")
        parser.add_argument("--force", action="store_true", help="Runs outside DEBUG. Demo data does not belong in a real database.")

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError("Refusing to seed demo wallets outside DEBUG. Pass --force if this really is what you want.")

        if options["remove"]:
            deleted, _ = Wallet.objects.filter(public_id__in=(RECAP_ID, WELCOME_ID)).delete()

            self.stdout.write(self.style.SUCCESS(f"Demo wallets removed ({deleted} rows)."))

            return

        away = options["away"]

        if away < 2:
            raise CommandError("A welcome back needs at least two weeks away; below that it is an ordinary weekly recap.")

        self.today = timezone.now().date()
        # The last week that has ended, which is the one a recap reports on.
        self.last_week = monday_of(self.today) - timedelta(days=7)

        with transaction.atomic():
            recap = self.build_recap_wallet()
            welcome = self.build_welcome_wallet(away)

        self.report(recap, welcome, away)

    def build_recap_wallet(self):
        """
        A wallet that was last here a fortnight ago: one week has ended unseen,
        so the ordinary weekly look back is what it opens.

        The week being reported on is deliberately the better of the two, so the
        comparison against the week before has something to say.
        """
        wallet = self.blank_wallet(RECAP_ID, "Recap Demo", RECAP_PHRASE)

        self.quiet_from = None
        # The week that is being lived is dealt the same good hand as the one
        # being reported on, so the demo also has a streak running today.
        self.strong_weeks = {self.last_week, monday_of(self.today)}
        self.weak_week = self.last_week - timedelta(days=7)

        self.build_habits(wallet)

        # A week behind: everything up to the week before last has been seen.
        Recap.objects.create(wallet=wallet, last_week=self.weak_week)

        return wallet

    def build_welcome_wallet(self, away):
        """
        A wallet that kept it up for months and then stopped.

        The span it comes back to holds a couple of entries at its very start
        and nothing after, which is both what a fade-out looks like and what
        keeps the recap from passing the span over as never used.
        """
        wallet = self.blank_wallet(WELCOME_ID, "Welcome Back Demo", WELCOME_PHRASE)
        span_start = self.last_week - timedelta(days=7 * (away - 1))

        # Logging thins out a few days into the span and stops for good.
        self.quiet_from = span_start + timedelta(days=4)
        self.strong_weeks = set()
        self.weak_week = None

        self.build_habits(wallet)

        Recap.objects.create(wallet=wallet, last_week=span_start - timedelta(days=7))

        return wallet

    def blank_wallet(self, public_id, name, phrase):
        """The wallet as it stands before any habit: made, or wiped and reused."""
        wallet, _ = Wallet.objects.update_or_create(
            public_id=public_id,
            defaults={
                "phrase_hash": hash_wallet_phrase(normalise_wallet_phrase(phrase)),
                "name": name,
                "balance": 500,
                "last_visit": self.today,
            },
        )

        # The entries go with the habits, and the recap state has to go too, or
        # a second run would find the wallet already caught up.
        wallet.habits.all().delete()
        Recap.objects.filter(wallet=wallet).delete()

        return wallet

    def build_habits(self, wallet):
        """
        Fills the wallet with the four demo habits and a few months of days.

        The shape of those days is whatever the caller has just set up: the day
        logging stopped, and the two weeks that are dealt a fixed hand.
        """
        self.rng = random.Random(SEED)  # noqa: S311 - demo data, not a secret
        self.start = self.today - timedelta(days=HISTORY_DAYS)

        for order, spec in enumerate(HABITS):
            habit = Habit.objects.create(
                wallet=wallet,
                kind=spec.get("kind", Habit.GOAL),
                name=spec["name"],
                unit=spec["unit"],
                goal=Decimal(str(spec["goal"])),
                step=Decimal(str(spec["step"])),
                color=spec["color"],
                order=order,
                wide=spec["wide"],
            )

            measured = habit.kind == Habit.MEASURE

            Entry.objects.bulk_create(self.measure_entries(habit) if measured else self.goal_entries(habit, spec))

    def days(self):
        """Every day of the filled history, stopping where logging stopped."""
        for offset in range((self.today - self.start).days + 1):
            day = self.start + timedelta(days=offset)

            if self.quiet_from and day >= self.quiet_from:
                return

            yield day

    def goal_entries(self, habit, spec):
        """
        A day either happened or it did not, and a day that happened usually,
        though not always, made the goal. The two named weeks are dealt a fixed
        hand instead, so the recap's comparison is the same on every run.
        """
        goal = float(habit.goal)
        entries = []

        for day in self.days():
            week = monday_of(day)
            weekday = day.weekday()

            if week in self.strong_weeks:
                # Six days on, one off, and every one of them over the goal.
                if weekday == 6:
                    continue

                value = goal * self.rng.uniform(1.0, 1.4)
            elif week == self.weak_week:
                # Half the week, and the later half of those short of it.
                if weekday % 2:
                    continue

                value = goal * (self.rng.uniform(1.0, 1.2) if weekday < 3 else self.rng.uniform(0.3, 0.8))
            else:
                if self.rng.random() > spec["chance"]:
                    continue

                value = goal * (self.rng.uniform(1.0, 1.5) if self.rng.random() < 0.7 else self.rng.uniform(0.2, 0.9))

            entries.append(Entry(habit=habit, date=day, value=Decimal(str(round(value, 2)))))

        return entries

    def measure_entries(self, habit):
        """
        A reading every few days, wandering towards the target and never quite
        arriving. Nothing in between: a measurement is taken, not missed.
        """
        target = float(habit.goal)
        value = target + 6.5
        entries = []
        day = self.start

        while day <= self.today:
            if self.quiet_from and day >= self.quiet_from:
                break

            # Each reading closes a slice of what is left, so the line eases in
            # on the target and then hovers around it instead of sailing past.
            value -= (value - target) * self.rng.uniform(0.03, 0.09)
            value += self.rng.uniform(-0.25, 0.25)
            entries.append(Entry(habit=habit, date=day, value=Decimal(str(round(value, 2)))))

            day += timedelta(days=self.rng.choice((2, 3, 4)))

        return entries

    def report(self, recap, welcome, away):
        """What to type where, since the phrase is the whole of a wallet's key."""
        self.stdout.write(self.style.SUCCESS("Two demo wallets are ready. Sign in at /login/ with the phrase, then open /momentum/."))
        self.stdout.write("")
        self.stdout.write(f"  Weekly recap    {recap.name} (#{recap.public_id})")
        self.stdout.write(self.style.HTTP_INFO(f"    {RECAP_PHRASE}"))
        self.stdout.write("    One week ended unseen, and it went better than the one before it.")
        self.stdout.write("")
        self.stdout.write(f"  Welcome back    {welcome.name} (#{welcome.public_id})")
        self.stdout.write(self.style.HTTP_INFO(f"    {WELCOME_PHRASE}"))
        self.stdout.write(f"    Gone for {away} weeks, having stopped logging a few days in.")
        self.stdout.write("")
        self.stdout.write("Each dialog opens once and is then marked as seen. Run this command again to get both back.")
