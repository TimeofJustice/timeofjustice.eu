<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import {
  formatNumber,
  GRID,
  levelColor,
  monthColumns,
  yearWeeks,
} from "@composables/habits";
import type { Habit, HabitDay } from "@/types/Habit.ts";

interface HabitsYearGridProps {
  habit: Habit;
  year: number;
  /** "YYYY-MM-DD" -> value, for this habit and this year only. */
  values: Record<string, number>;
  /** Today's date, so the current day can be marked and later ones ruled out. */
  today: string;
}

const { habit, year, values, today } = defineProps<HabitsYearGridProps>();

const emit = defineEmits<{ select: [date: string] }>();

const i18n = useI18n();

const weeks = computed(() => yearWeeks(year, values, habit.goal, today));
const months = computed(() => monthColumns(weeks.value));

// Every other row. At this pitch, seven labels would touch.
const WEEKDAY_ROWS = [0, 2, 4, 6];

/** The same dwell r/place uses. Every one of 365 squares is a trigger. */
const HOVER_DELAY = 700;

const format = (number: number) => formatNumber(number, i18n.locale.value);

const label = (date: string, value: number) =>
  i18n.t("habits.grid.day_title", {
    date: new Date(`${date}T00:00:00`).toLocaleDateString(i18n.locale.value),
    value,
    goal: habit.goal,
    unit: habit.unit,
  });

/**
 * No fixed square size, which is what lets two habits sit side by side. Rows are
 * `auto`, so an `aspect-square` cell makes its own row as tall as it is wide.
 */
const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(${weeks.value.length}, minmax(0, 1fr))`,
  gridTemplateRows: `repeat(${GRID.rows}, auto)`,
  gap: `${GRID.gap}px`,
}));

/** Inline style, not Tailwind: a chart beside this one reads the same `GRID`. */
const frameStyle = computed(() => ({
  minWidth: `${GRID.minWidth}px`,
  maxWidth: `${GRID.maxWidth}px`,
  gap: `${GRID.labelGap}px`,
}));

const labelStyle = computed(() => ({
  gridTemplateRows: `repeat(${GRID.rows}, minmax(0, 1fr))`,
  gap: `${GRID.gap}px`,
}));

// One tooltip moved from square to square; 365 wrapped ones would be hundreds
// of components per habit.
const hovered = ref<HabitDay | null>(null);
const hoveredSquare = ref<HTMLElement | null>(null);

const hoveredDate = computed(() =>
  hovered.value?.date
    ? new Date(`${hovered.value.date}T00:00:00`).toLocaleDateString(
        i18n.locale.value,
        { weekday: "short", day: "numeric", month: "long", year: "numeric" },
      )
    : "",
);

const enter = (event: Event, day: HabitDay) => {
  hovered.value = day;
  hoveredSquare.value = event.currentTarget as HTMLElement;
};

const leave = () => {
  // The day stays, so the pill keeps its text while it fades out.
  hoveredSquare.value = null;
};
</script>

<template>
  <div class="relative">
    <!-- `overflow-y-hidden` is load-bearing: naming one axis `auto` promotes the
         other from `visible` to `auto`, so a square swelling under the pointer
         would raise a scrollbar. The padding is where those overhangs live. -->
    <div
      class="overflow-x-auto overflow-y-hidden"
      :style="{ padding: `${GRID.padding}px` }"
      @scroll="leave"
    >
      <div class="flex items-stretch" :style="frameStyle">
        <div
          class="flex shrink-0 flex-col text-[0.6rem] text-accent"
          :style="{ width: `${GRID.labelWidth}px` }"
        >
          <!-- Lines the weekdays up under the month row next to them. -->
          <div :style="{ height: `${GRID.header}px` }" />

          <!-- `h-0 min-h-0` keeps these in step with the squares. Seven lines of
               text are taller than seven small squares, and a flex item is never
               shrunk below its content unless told to, so without it the labels
               would set the row height and drift from their rows. -->
          <div class="grid h-0 min-h-0 grow" :style="labelStyle">
            <div
              v-for="row in GRID.rows"
              :key="row"
              class="flex items-center leading-none"
            >
              {{
                WEEKDAY_ROWS.includes(row - 1)
                  ? $t(`habits.weekdays.${row - 1}`)
                  : ""
              }}
            </div>
          </div>
        </div>

        <div class="min-w-0 grow">
          <div
            class="grid text-[0.6rem] text-accent"
            :style="{ ...gridStyle, height: `${GRID.header}px` }"
          >
            <div
              v-for="month in months"
              :key="month.month"
              class="whitespace-nowrap"
              :style="{ gridColumn: month.column + 1 }"
            >
              {{ $t(`habits.months.${month.month}`) }}
            </div>
          </div>

          <div class="grid grid-flow-col" :style="gridStyle">
            <template v-for="(week, column) in weeks" :key="column">
              <template v-for="(day, row) in week" :key="row">
                <!-- Padding around the year keeps the columns aligned. -->
                <div v-if="!day.date" class="aspect-square" />

                <!-- Drawn, but nothing to log on them and nothing to say. -->
                <div
                  v-else-if="day.future"
                  class="aspect-square rounded-xs bg-dark-gray-500/15"
                />

                <!-- The `after` hit area is larger than its square. A day is
                     about nine pixels wide, and the two-pixel gaps either side
                     were dead ground: the pointer sat in one, the neighbour
                     showed as hovered, and the click landed on nothing. -->
                <button
                  v-else
                  type="button"
                  class="relative aspect-square cursor-pointer rounded-xs transition-transform duration-100 after:absolute after:-inset-1 after:content-[''] hover:scale-125 focus:outline-none focus-visible:ring-2 focus-visible:ring-light"
                  :class="[
                    day.level === 0 && 'bg-dark-gray-500/40',
                    day.date === today && 'ring-1 ring-light/70',
                  ]"
                  :style="{
                    backgroundColor:
                      levelColor(habit.color, day.level) ?? undefined,
                  }"
                  :aria-label="label(day.date, day.value)"
                  @mouseenter="enter($event, day)"
                  @focus="enter($event, day)"
                  @mouseleave="leave"
                  @blur="leave"
                  @click="emit('select', day.date)"
                />
              </template>
            </template>
          </div>
        </div>
      </div>
    </div>

    <UiTooltip :anchor="hoveredSquare" :delay="HOVER_DELAY">
      <template #content>
        <template v-if="hovered">
          {{ hoveredDate }}
          <span class="opacity-60">·</span>
          <span :class="hovered.level === 5 && 'text-success'">
            {{ format(hovered.value) }}
          </span>
          <span class="opacity-60">
            / {{ format(habit.goal) }} {{ habit.unit }}
          </span>
        </template>
      </template>
    </UiTooltip>
  </div>
</template>
