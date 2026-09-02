<script setup lang="ts">
import { computed, defineAsyncComponent, ref } from "vue";
import { useI18n } from "vue-i18n";
import {
  formatNumber,
  goalLabel,
  habitStats,
  LEVEL_MIX,
  measureStats,
  roundValue,
  weeklyAverages,
} from "@composables/habits";
import HabitsYearGrid from "@components/HabitsYearGrid.vue";
import type { Habit } from "@/types/Habit.ts";

// 50 kB gzipped, and only a `measure` habit needs it.
const HabitsTrendChart = defineAsyncComponent(
  () => import("@components/HabitsTrendChart.vue"),
);

interface HabitsPanelProps {
  habit: Habit;
  /** The year on screen, and the days logged in it for this habit. */
  year: number;
  values: Record<string, number>;
  today: string;
  /** Dimmed while another year is on its way in. */
  loading?: boolean;
}

const {
  habit,
  year,
  values,
  today,
  loading = false,
} = defineProps<HabitsPanelProps>();

const emit = defineEmits<{ edit: []; select: [date: string] }>();

const i18n = useI18n();

const format = (number: number) => formatNumber(number, i18n.locale.value);

/** A reading whose course is the point, rather than a goal met or missed. */
const isMeasure = computed(() => habit.kind === "measure");

const stats = computed(() => habitStats(values, habit.goal, habit.goalMax));

/** One number, or the two ends of the zone. */
const goalText = computed(() => goalLabel(habit, i18n.locale.value));
const measures = computed(() => measureStats(values, habit.goal));

/**
 * The most recent week that was measured in, and the one measured before it.
 *
 * Not "this week" and "last week": in a year gone by there is no this week, and
 * a fortnight without a weigh-in would leave both empty. The last two weeks
 * that hold anything are what there is to compare.
 */
const weeks = computed(() => {
  const averages = weeklyAverages(values);

  return {
    latest: averages[averages.length - 1] ?? null,
    previous: averages[averages.length - 2] ?? null,
  };
});

/**
 * How the last measured week moved against the one before it. Null when there
 * is only one week to go on, which is a level, not a direction.
 */
const weekDelta = computed(() => {
  const { latest, previous } = weeks.value;

  return latest && previous
    ? roundValue(latest.average - previous.average)
    : null;
});

/** Whether that week closed on the target. The target says which way is forwards. */
const weekClass = computed(() => {
  const { latest, previous } = weeks.value;

  if (!latest || !previous) return "text-accent";

  const closed =
    Math.abs(previous.average - habit.goal) -
    Math.abs(latest.average - habit.goal);

  if (closed > 0) return "text-success";
  if (closed < 0) return "text-danger";

  return "text-accent";
});

/** The run going now is the best there has ever been. */
const atRecord = computed(
  () =>
    habit.streak.current > 0 && habit.streak.current === habit.streak.longest,
);

/** Four wordings, by kind and by whether the record is the run going now. */
const recordKey = computed(() => {
  const measure = isMeasure.value ? "_measure" : "";

  return atRecord.value
    ? `habits.stats.record${measure}`
    : `habits.stats.streak${measure}`;
});

const signed = (delta: number) => `${delta > 0 ? "+" : ""}${format(delta)}`;

/** Which way it went. Whether that is good is the colour's job. */
const trendIcon = (delta: number) => {
  if (delta > 0) return "fa6-solid:arrow-trend-up";
  if (delta < 0) return "fa6-solid:arrow-trend-down";

  return "fa6-solid:minus";
};

const longDate = (date: string) =>
  new Date(`${date}T00:00:00`).toLocaleDateString(i18n.locale.value, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

/** What the year moved, and whether that counted as progress. */
const changeText = computed(() => {
  const { count, delta, closed } = measures.value;

  if (count === 0) return i18n.t("habits.stats.no_readings");

  const values = { delta: signed(delta), unit: habit.unit, year };

  if (closed === 0) return i18n.t("habits.stats.change", values);

  return i18n.t(
    closed > 0 ? "habits.stats.closer" : "habits.stats.further",
    values,
  );
});

const progressClass = computed(() => {
  const { closed } = measures.value;

  if (closed > 0) return "text-success";
  if (closed < 0) return "text-danger";

  return "text-accent";
});

/** The days off, spelled out: "Sa, So". */
const restDayNames = computed(() =>
  habit.restDays.map((day) => i18n.t(`habits.weekdays.${day}`)).join(", "),
);

/**
 * Which of the chart's two lines are drawn. Held here rather than in the chart
 * because the legend that switches them shares the footer row with the grid's
 * own legend, and that row belongs to the panel.
 */
const showReadings = ref(true);
const showWeeks = ref(true);

/** Legend swatches, from "nothing" to "goal reached". */
const legendColors = computed(() =>
  LEVEL_MIX.map((mix) =>
    mix === 0
      ? null
      : `color-mix(in srgb, ${habit.color} ${mix}%, transparent)`,
  ),
);
</script>

<template>
  <UiCard
    no-body
    header-class="flex items-center justify-between gap-2"
    :class="loading && 'busy opacity-65'"
  >
    <template #header>
      <div class="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
        <span
          class="size-3 shrink-0 rounded-full"
          :style="{ backgroundColor: habit.color }"
        />

        <h2 class="m-0 truncate text-h6">{{ habit.name }}</h2>

        <!-- A target weight is not a daily quota, so it is worded differently. -->
        <span class="text-sm text-accent">
          {{
            $t(isMeasure ? "habits.trend.target" : "habits.goal_label", {
              goal: goalText,
              value: format(habit.goal),
              unit: habit.unit,
            })
          }}
        </span>

        <UiBadge v-if="habit.archived" variant="tertiary">
          {{ $t("habits.archived") }}
        </UiBadge>

        <!-- Days reached this year, the run going now, and the best ever. -->
        <div class="flex flex-wrap items-center gap-x-2">
          <!-- A measurement has no streak to run: what matters is where
               it stands, how far it has moved, and how often it was
               taken. -->
          <template v-if="isMeasure">
            <UiTooltip
              :text="
                measures.latestDate
                  ? $t('habits.stats.latest', {
                      date: longDate(measures.latestDate!),
                    })
                  : $t('habits.stats.no_readings')
              "
            >
              <span class="text-sm text-light">
                {{ measures.latest === null ? "—" : format(measures.latest!) }}
                {{ habit.unit }}
              </span>
            </UiTooltip>

            <!-- What the week averaged. A daily weigh-in swings with the salt
                 in yesterday's dinner; the week is what actually moved. -->
            <UiTooltip
              v-if="weeks.latest"
              :text="
                $t('habits.stats.week_average', {
                  date: longDate(weeks.latest.week),
                  value: format(weeks.latest.average),
                  unit: habit.unit,
                  count: weeks.latest.count,
                })
              "
            >
              <span class="flex items-center gap-1 text-sm" :class="weekClass">
                ⌀ {{ format(weeks.latest.average) }}
                <template v-if="weekDelta !== null">
                  ({{ signed(weekDelta) }})
                </template>
              </span>
            </UiTooltip>

            <!-- The arrow is the fact, the colour is the verdict. -->
            <UiTooltip :text="changeText">
              <span
                class="flex items-center gap-1 text-sm"
                :class="progressClass"
              >
                <iconify-icon :icon="trendIcon(measures.delta)" />
                {{ signed(measures.delta) }}
              </span>
            </UiTooltip>
          </template>

          <!-- The weekdays nothing is asked on. Named rather than counted:
               "Sa, So" says what the arrangement is, where "104" would only
               say how often it came up. -->
          <UiTooltip
            v-if="!isMeasure && habit.restDays.length > 0"
            :text="$t('habits.stats.rest_days', { days: restDayNames })"
          >
            <span class="flex items-center gap-1 text-sm text-accent">
              <iconify-icon icon="fa6-solid:mug-hot" />
              {{ restDayNames }}
            </span>
          </UiTooltip>

          <UiTooltip
            v-if="!isMeasure"
            :text="
              $t('habits.stats.done', {
                count: format(stats.done),
                year,
              })
            "
          >
            <span class="flex items-center gap-1 text-sm text-accent">
              <iconify-icon icon="fa6-solid:check" />
              {{ format(stats.done) }}
            </span>
          </UiTooltip>

          <!-- Both kinds have a streak: goal-met days, or readings that kept
               closing on their target. -->
          <UiTooltip
            :text="
              $t(
                isMeasure
                  ? 'habits.stats.current_measure'
                  : 'habits.stats.current',
                { count: format(habit.streak.current) },
              )
            "
          >
            <span
              class="flex items-center gap-1 text-sm"
              :class="habit.streak.current > 0 ? 'text-warning' : 'text-accent'"
            >
              <iconify-icon
                icon="fa6-solid:fire"
                :class="
                  habit.streak.current > 0 &&
                  'animate-flame motion-reduce:animate-none'
                "
              />
              {{ format(habit.streak.current) }}
            </span>
          </UiTooltip>

          <!-- Standing on the record right now: the trophy joins in. -->
          <UiTooltip
            :text="
              $t(recordKey, {
                count: format(habit.streak.longest),
              })
            "
          >
            <span
              class="flex items-center gap-1 text-sm"
              :class="atRecord ? 'text-warning' : 'text-accent'"
            >
              <iconify-icon
                icon="fa6-solid:trophy"
                :class="
                  atRecord && 'animate-sparkle motion-reduce:animate-none'
                "
              />
              {{ format(habit.streak.longest) }}
            </span>
          </UiTooltip>
        </div>
      </div>

      <div class="flex shrink-0 items-center gap-1">
        <!-- The board puts its drag grip here. -->
        <slot name="handle" />

        <UiButton
          variant="tertiary"
          square
          size="sm"
          :title="$t('habits.form.edit_title')"
          @click="emit('edit')"
        >
          <iconify-icon icon="fa6-solid:gear" />
        </UiButton>
      </div>
    </template>

    <UiCardBody class="flex flex-col gap-2">
      <HabitsTrendChart
        v-if="isMeasure"
        :habit="habit"
        :year="year"
        :values="values"
        :today="today"
        :show-readings="showReadings"
        :show-weeks="showWeeks"
        @select="emit('select', $event)"
      />

      <HabitsYearGrid
        v-else
        :habit="habit"
        :year="year"
        :values="values"
        :today="today"
        @select="emit('select', $event)"
      />

      <div
        class="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-sm text-accent"
      >
        <span v-if="isMeasure">
          {{
            measures.count > 0
              ? $t("habits.stats.entries", {
                  count: format(measures.count),
                  year,
                })
              : ""
          }}
        </span>

        <span v-else>
          {{
            $t("habits.stats.total", {
              total: format(stats.total),
              unit: habit.unit,
            })
          }}
        </span>

        <!-- Two lines, and a switch each. In the same row the grid puts
             its own legend in, so a chart panel and a grid panel beside it
             stay exactly as tall as one another. -->
        <div
          v-if="isMeasure && measures.count > 0"
          class="flex flex-wrap items-center gap-3"
        >
          <button
            type="button"
            class="flex cursor-pointer items-center gap-1.5 transition-opacity duration-150"
            :class="!showReadings && 'opacity-40'"
            :aria-pressed="showReadings"
            @click="showReadings = !showReadings"
          >
            <span
              class="h-0.5 w-4 shrink-0 rounded-full"
              :style="{ backgroundColor: habit.color }"
            />
            {{ $t("habits.trend.readings") }}
          </button>

          <button
            type="button"
            class="flex cursor-pointer items-center gap-1.5 transition-opacity duration-150"
            :class="!showWeeks && 'opacity-40'"
            :aria-pressed="showWeeks"
            @click="showWeeks = !showWeeks"
          >
            <span class="h-0.5 w-4 shrink-0 rounded-full bg-light/65" />
            {{ $t("habits.trend.weekly") }}
          </button>
        </div>

        <!-- A line needs no legend; its axis says the same thing. -->
        <div v-if="!isMeasure" class="flex items-center gap-1">
          {{ $t("habits.legend.less") }}
          <span
            v-for="(swatch, level) in legendColors"
            :key="level"
            class="size-2.5 rounded-xs"
            :class="!swatch && 'bg-dark-gray-500/40'"
            :style="{ backgroundColor: swatch ?? undefined }"
          />
          {{ $t("habits.legend.more") }}
        </div>
      </div>
    </UiCardBody>
  </UiCard>
</template>
