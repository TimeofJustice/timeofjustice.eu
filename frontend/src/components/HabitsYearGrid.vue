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

// Every other row — Monday, Wednesday, Friday, Sunday. Labelling all seven
// leaves no space for the squares themselves, and at this pitch the text of two
// neighbouring rows would touch.
const WEEKDAY_ROWS = [0, 2, 4, 6];

/**
 * The same dwell r/place uses for the pixel it has selected. A year is a lot of
 * squares to sweep a pointer across, and every one of them is a trigger.
 */
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
 * The squares size themselves to whatever width the card gives them, rather
 * than to a fixed pixel size — that is what lets two habits sit side by side.
 * Rows are `auto`, so an `aspect-square` cell makes its own row as tall as it
 * is wide.
 */
const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(${weeks.value.length}, minmax(0, 1fr))`,
  gridTemplateRows: `repeat(${GRID.rows}, auto)`,
  gap: `${GRID.gap}px`,
}));

/**
 * Everything a chart beside this one has to agree with lives in `GRID`, so it
 * is spent here as inline style rather than as Tailwind classes — a hard-coded
 * `gap-[2px]` in this template is exactly how the two would drift apart.
 */
const frameStyle = computed(() => ({
  minWidth: `${GRID.minWidth}px`,
  maxWidth: `${GRID.maxWidth}px`,
  gap: `${GRID.labelGap}px`,
}));

const labelStyle = computed(() => ({
  gridTemplateRows: `repeat(${GRID.rows}, minmax(0, 1fr))`,
  gap: `${GRID.gap}px`,
}));

// One tooltip for the whole year, moved from square to square. Wrapping each of
// the 365 cells in its own would be hundreds of components per habit.
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
  // Only the anchor is dropped: the day is left in place so the pill keeps its
  // text while it fades out instead of emptying itself first.
  hoveredSquare.value = null;
};
</script>

<template>
  <div class="relative">
    <!-- A year is 53 columns wide. It stretches to fill the card and only
         starts scrolling once even the smallest readable square stops fitting.

         `overflow-y-hidden` is not decoration: naming one axis `auto` promotes
         the other from `visible` to `auto` as well, so anything reaching past
         an edge — a square swelling under the pointer, the Sunday label in a
         row shorter than its own text — would raise a scrollbar. The padding
         gives both of them the room they need instead of clipping them. -->
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

          <!-- `h-0 min-h-0` before `grow` is what keeps these in step with the
               squares. Left to itself this grid is seven lines of text tall,
               which is more than the squares are when they are small — and a
               flex item is never shrunk below its content unless told to. It
               would then set the height of the whole row, spread its seven
               rows over a slightly larger pitch than the squares next to it,
               and the two would drift further apart with every row. At a base
               height of zero the squares decide, and both grids divide exactly
               the same space. -->
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

                <!-- Days still to come are drawn, but there is nothing to log
                     on them and nothing to say about them. -->
                <div
                  v-else-if="day.future"
                  class="aspect-square rounded-xs bg-dark-gray-500/15"
                />

                <!-- The `after` is the hit area, and it is deliberately larger
                     than the square it belongs to. A day is only about nine
                     pixels wide with a two-pixel gap either side, and those gaps
                     were dead: the pointer would sit in one, the neighbouring
                     square would still show as hovered, and the click would land
                     on nothing. Reaching a pixel past the gap leaves no dead
                     ground at all — where two hit areas overlap the later square
                     wins, which is consistent, and the ring of scroller padding
                     is exactly deep enough to hold the outermost ones. -->
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
