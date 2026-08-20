<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";
import { useI18n } from "vue-i18n";
import {
  formatNumber,
  habitStats,
  LEVEL_MIX,
  measureStats,
} from "@composables/habits";
import HabitsYearGrid from "@components/HabitsYearGrid.vue";
import type { Habit } from "@/types/Habit.ts";

// chart.js is 50 kB gzipped and only a progression needs it. Loaded on demand,
// so a board of nothing but daily goals never fetches it at all.
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

const stats = computed(() => habitStats(values, habit.goal));
const measures = computed(() => measureStats(values, habit.goal));

/** The run going now is the best there has ever been. */
const atRecord = computed(
  () =>
    habit.streak.current > 0 && habit.streak.current === habit.streak.longest,
);

/** Four ways to say "longest run", by kind and by whether it is the one running. */
const recordKey = computed(() => {
  const measure = isMeasure.value ? "_measure" : "";

  return atRecord.value
    ? `habits.stats.record${measure}`
    : `habits.stats.streak${measure}`;
});

/** A movement reads as a movement only with its sign on it. */
const signed = (delta: number) => `${delta > 0 ? "+" : ""}${format(delta)}`;

/** Which way it went. Whether that is good is the colour's job, not the icon's. */
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

/**
 * What the year moved, and whether that counted as progress.
 *
 * The target is what makes the verdict possible at all: it decides which way is
 * forwards, so a falling weight and a rising balance both read as progress
 * without the tracker having to know which one it is looking at.
 */
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

/** Swatches for the legend, from "nothing" to "goal reached". */
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
    :class="loading && 'opacity-60'"
  >
    <template #header>
      <div class="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
        <span
          class="size-3 shrink-0 rounded-full"
          :style="{ backgroundColor: habit.color }"
        />

        <h2 class="m-0 truncate text-h6">{{ habit.name }}</h2>

        <!-- "6000 steps a day" for a goal, but a target weight is not a
             daily quota — it is the number being moved towards. -->
        <span class="text-sm text-accent">
          {{
            $t(isMeasure ? "habits.trend.target" : "habits.goal_label", {
              goal: format(habit.goal),
              value: format(habit.goal),
              unit: habit.unit,
            })
          }}
        </span>

        <UiBadge v-if="habit.archived" variant="tertiary">
          {{ $t("habits.archived") }}
        </UiBadge>

        <!-- How the habit is doing, up beside its name: days reached this
             year, the run going now, and the best run there has ever been. -->
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

            <!-- What moved this year, and whether that was progress.
                 The arrow is the fact — which way it went — and the
                 colour is the verdict, which only the target can give. -->
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

          <!-- A running streak burns; a broken one is just a number.
               Both kinds have one — days that met their goal, or readings
               that kept closing on their target. -->
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

        <!-- Legend: how full a square is says how close that day came.
               A line needs none — its axis says the same thing. -->
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
