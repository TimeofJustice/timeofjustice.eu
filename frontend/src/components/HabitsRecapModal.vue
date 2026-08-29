<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import {
  formatNumber,
  levelColor,
  levelOf,
  toIsoDate,
} from "@composables/habits";
import type { HabitRecap, HabitRecapEntry } from "@/types/Habit.ts";

interface HabitsRecapModalProps {
  /** The look back to show. Null on every visit that has none owed. */
  recap: HabitRecap | null;
}

const { recap } = defineProps<HabitsRecapModalProps>();

const show = defineModel<boolean>({ default: false });

const i18n = useI18n();

const format = (number: number) => formatNumber(number, i18n.locale.value);

/** A return after a long absence is not a week to go through habit by habit. */
const isWelcome = computed(() => recap?.kind === "welcome_back");

const shortDate = (date: string) =>
  new Date(`${date}T00:00:00`).toLocaleDateString(i18n.locale.value, {
    day: "numeric",
    month: "long",
  });

const span = computed(() =>
  recap
    ? i18n.t("habits.recap.span", {
        from: shortDate(recap.start),
        to: shortDate(recap.end),
      })
    : "",
);

/** How much of what the span had on offer was actually met, as a percentage. */
const percentage = computed(() => {
  if (!recap || recap.totals.possible === 0) return 0;

  return Math.min(
    100,
    Math.round((recap.totals.done / recap.totals.possible) * 100),
  );
});

/**
 * A word on the week, by how much of it came in. Only a week gets one: after a
 * month away there is nothing to praise or excuse, only a thread to pick up.
 */
const verdict = computed(() => {
  if (!recap || recap.totals.possible === 0) return "habits.recap.lead_any";
  if (percentage.value >= 80) return "habits.recap.lead_strong";
  if (percentage.value >= 40) return "habits.recap.lead_good";

  return "habits.recap.lead_slow";
});

/** Goal-days against the span before, which is what makes a number a trend. */
const trend = computed(() =>
  recap ? recap.totals.done - recap.previousTotals.done : 0,
);

/** Which way it went. Whether that is good is the colour's job. */
const trendIcon = (delta: number) => {
  if (delta > 0) return "fa6-solid:arrow-trend-up";
  if (delta < 0) return "fa6-solid:arrow-trend-down";

  return "fa6-solid:minus";
};

const signed = (delta: number) => `${delta > 0 ? "+" : ""}${format(delta)}`;

/** The colour a change gets wherever more of it is simply better. */
const trendClass = (delta: number) => {
  if (delta > 0) return "text-success";
  if (delta < 0) return "text-danger";

  return "text-accent";
};

/** A daily goal's days against the same number over the span before. */
const goalTrend = (habit: HabitRecapEntry) =>
  (habit.done ?? 0) - (habit.previousDone ?? 0);

/** When anything was last logged. A dash when there is no such day. */
const lastActive = computed(() =>
  recap?.lastActive
    ? new Date(`${recap.lastActive}T00:00:00`).toLocaleDateString(
        i18n.locale.value,
        { day: "numeric", month: "short" },
      )
    : "—",
);

/** The longest run still going, over every habit. What survived the span. */
const bestStreak = computed(() =>
  recap
    ? recap.habits.reduce(
        (best, habit) => Math.max(best, habit.streak.current),
        0,
      )
    : 0,
);

/**
 * The best run there has ever been, over every habit.
 *
 * What a return is shown instead of the one going now, which after weeks away
 * is zero by definition and says nothing except that time passed.
 */
const bestEver = computed(() =>
  recap
    ? recap.habits.reduce(
        (best, habit) => Math.max(best, habit.streak.longest),
        0,
      )
    : 0,
);

/**
 * The span day by day, for the strip beside a daily goal. Only drawn for a
 * single week: a month of absence would be a wall of squares, and the numbers
 * beside it already say the same thing.
 */
const strip = (habit: HabitRecapEntry) => {
  if (!recap) return [];

  const first = new Date(`${recap.start}T00:00:00`);

  return Array.from({ length: recap.days }, (_, offset) => {
    const day = new Date(first);
    day.setDate(first.getDate() + offset);

    const date = toIsoDate(day);
    const value = habit.values[date] ?? 0;

    return {
      date,
      value,
      color: levelColor(habit.color, levelOf(value, habit.goal)),
    };
  });
};

const dayTitle = (habit: HabitRecapEntry, date: string, value: number) =>
  i18n.t("habits.grid.day_title", {
    date: shortDate(date),
    value: format(value),
    goal: format(habit.goal),
    unit: habit.unit,
  });

/** Progress towards a target, where the target decides which way is forwards. */
const measureClass = (closed: number | null) => {
  if (closed === null || closed === 0) return "text-accent";

  return closed > 0 ? "text-success" : "text-danger";
};
</script>

<template>
  <!-- Static: the recap is the one thing on the screen worth reading, and it
       is over in a tap. A stray click on the backdrop should not skip it. -->
  <UiModal
    v-if="recap"
    v-model="show"
    size="lg"
    centered
    scrollable
    static
    header-class="justify-between gap-2"
    body-class="flex flex-col gap-4"
  >
    <template #header>
      <div class="flex min-w-0 items-center gap-3">
        <span
          class="flex size-9 shrink-0 items-center justify-center rounded-full bg-success/20 text-success"
        >
          <iconify-icon
            :icon="
              isWelcome ? 'fa6-solid:hand-sparkles' : 'fa6-solid:calendar-check'
            "
          />
        </span>

        <div class="min-w-0">
          <h2 class="m-0 truncate text-h5">
            {{
              $t(
                isWelcome ? "habits.recap.welcome_title" : "habits.recap.title",
              )
            }}
          </h2>
          <p class="m-0 text-sm text-accent">{{ span }}</p>
        </div>
      </div>
    </template>

    <!-- The headline. One number, and what it is out of. -->
    <div class="rounded-md border border-hairline bg-card p-4">
      <template v-if="isWelcome">
        <div class="flex items-baseline gap-2">
          <span class="text-h2 leading-none tabular-nums">{{
            recap.weeks
          }}</span>
          <span class="text-accent">{{ $t("habits.recap.away") }}</span>
        </div>

        <p class="m-0 mt-2 text-sm text-accent">
          {{ $t("habits.recap.away_lead", { date: shortDate(recap.start) }) }}
        </p>
      </template>

      <template v-else>
        <div
          class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1"
        >
          <div class="flex items-baseline gap-2">
            <span class="text-h2 leading-none tabular-nums">
              {{ format(recap.totals.done) }}
            </span>
            <span class="text-accent">
              {{
                $t("habits.recap.of", { count: format(recap.totals.possible) })
              }}
              {{ $t("habits.recap.goal_days") }}
            </span>
          </div>

          <!-- The arrow is the fact, the colour is the verdict. -->
          <span
            class="flex items-center gap-1 text-sm"
            :class="trendClass(trend)"
          >
            <iconify-icon :icon="trendIcon(trend)" />
            {{
              trend === 0
                ? $t("habits.recap.trend_same")
                : $t("habits.recap.trend", { count: signed(trend) })
            }}
          </span>
        </div>

        <UiProgress class="mt-3">
          <UiProgressBar
            :value="percentage"
            :variant="percentage >= 80 ? 'success' : undefined"
          />
        </UiProgress>

        <p class="m-0 mt-2 text-sm text-accent">{{ $t(verdict) }}</p>
      </template>
    </div>

    <!-- Three numbers about the span, or, on a return, three about what is
         still standing: everything counted inside a span nobody used is a
         zero, and three zeroes are no way to be welcomed back. -->
    <div class="grid grid-cols-3 gap-2">
      <div
        class="flex flex-col items-center gap-1 rounded-md border border-hairline p-2 text-center"
      >
        <span class="text-h5 leading-none tabular-nums">
          {{ isWelcome ? lastActive : recap.totals.activeDays }}
        </span>
        <small class="text-accent">
          {{
            $t(
              isWelcome
                ? "habits.recap.last_active"
                : "habits.recap.active_days",
            )
          }}
        </small>
      </div>

      <div
        class="flex flex-col items-center gap-1 rounded-md border border-hairline p-2 text-center"
      >
        <span class="text-h5 leading-none tabular-nums">
          {{ isWelcome ? recap.trackedDays : recap.totals.perfectDays }}
        </span>
        <small class="text-accent">
          {{
            $t(
              isWelcome
                ? "habits.recap.tracked_days"
                : "habits.recap.perfect_days",
            )
          }}
        </small>
      </div>

      <!-- The run going now, or, after weeks away, the best there has ever
           been: that one is still standing, and it is the number to beat. -->
      <div
        class="flex flex-col items-center gap-1 rounded-md border border-hairline p-2 text-center"
      >
        <span
          v-if="isWelcome"
          class="flex items-center gap-1 text-h5 leading-none tabular-nums"
          :class="bestEver > 0 && 'text-warning'"
        >
          <iconify-icon icon="fa6-solid:trophy" />
          {{ bestEver }}
        </span>

        <span
          v-else
          class="flex items-center gap-1 text-h5 leading-none tabular-nums"
          :class="bestStreak > 0 && 'text-warning'"
        >
          <iconify-icon
            icon="fa6-solid:fire"
            :class="
              bestStreak > 0 && 'animate-flame motion-reduce:animate-none'
            "
          />
          {{ bestStreak }}
        </span>

        <small class="text-accent">
          {{
            $t(
              isWelcome ? "habits.recap.best_ever" : "habits.recap.best_streak",
            )
          }}
        </small>
      </div>
    </div>

    <!-- Habit by habit. A daily goal shows the days it hit, a measurement
         shows where it ended up. -->
    <div class="flex flex-col gap-2">
      <div
        v-for="habit in recap.habits"
        :key="habit.id"
        class="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 rounded-md border border-hairline p-3"
      >
        <div class="flex min-w-0 items-center gap-2">
          <span
            class="size-3 shrink-0 rounded-full"
            :style="{ backgroundColor: habit.color }"
          />
          <span class="truncate">{{ habit.name }}</span>
        </div>

        <!-- After a long absence the span holds nothing worth counting, so
             each habit says when it was last kept and what its record is:
             where to pick it up again, rather than how much was missed. -->
        <div v-if="isWelcome" class="flex items-center gap-3">
          <span class="text-sm whitespace-nowrap text-accent">
            {{
              habit.lastLogged
                ? $t("habits.recap.last_logged", {
                    date: shortDate(habit.lastLogged),
                  })
                : $t("habits.recap.never_logged")
            }}
          </span>

          <span
            v-if="habit.streak.longest > 0"
            class="flex items-center gap-1 text-sm text-accent"
            :title="$t('habits.recap.best_ever')"
          >
            <iconify-icon icon="fa6-solid:trophy" />
            {{ habit.streak.longest }}
          </span>
        </div>

        <div v-else class="flex items-center gap-3">
          <!-- A week fits as squares; a longer span speaks in numbers only. -->
          <div
            v-if="habit.kind === 'goal' && recap.days <= 7"
            class="flex gap-1"
          >
            <span
              v-for="day in strip(habit)"
              :key="day.date"
              class="size-3.5 rounded-xs"
              :class="!day.color && 'bg-dark-gray-500/40'"
              :style="{ backgroundColor: day.color ?? undefined }"
              :title="dayTitle(habit, day.date, day.value)"
            />
          </div>

          <template v-if="habit.kind === 'measure'">
            <span class="text-sm">
              {{ habit.latest === null ? "—" : format(habit.latest) }}
              {{ habit.unit }}
            </span>

            <span
              v-if="habit.delta !== null"
              class="flex items-center gap-1 text-sm"
              :class="measureClass(habit.closed)"
            >
              <iconify-icon :icon="trendIcon(habit.delta)" />
              {{ signed(habit.delta) }}
            </span>
          </template>

          <template v-else>
            <span class="text-sm whitespace-nowrap text-accent">
              {{
                $t("habits.recap.habit_days", {
                  done: format(habit.done ?? 0),
                  days: recap.days,
                })
              }}
            </span>

            <span
              class="flex items-center gap-1 text-sm"
              :class="trendClass(goalTrend(habit))"
            >
              <iconify-icon :icon="trendIcon(goalTrend(habit))" />
              {{ signed(goalTrend(habit)) }}
            </span>
          </template>
        </div>
      </div>
    </div>

    <template #footer>
      <UiButton variant="success" @click="show = false">
        {{ $t(isWelcome ? "habits.recap.resume" : "habits.recap.close") }}
      </UiButton>
    </template>
  </UiModal>
</template>
