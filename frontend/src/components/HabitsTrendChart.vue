<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useTemplateRef } from "vue";
import { useI18n } from "vue-i18n";
import { Line } from "vue-chartjs";
import {
  CategoryScale,
  Chart,
  Filler,
  Interaction,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
  type Chart as ChartType,
  type ChartOptions,
  type InteractionModeFunction,
  type Plugin,
  type ScriptableContext,
} from "chart.js";
import { getRelativePosition } from "chart.js/helpers";
import {
  formatNumber,
  gridHeight,
  roundValue,
  toIsoDate,
} from "@composables/habits";
import { useMediaQuery } from "@composables/mediaQuery";
import type { Habit } from "@/types/Habit.ts";

// Only the pieces a single line needs; the rest of chart.js stays out of the
// bundle.
Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
);

/**
 * How near the pointer has to come to a real reading for that reading to win,
 * in pixels.
 */
const SNAP = 12;

declare module "chart.js" {
  interface InteractionModeMap {
    habitDay: InteractionModeFunction;
  }
}

/**
 * Hit testing that prefers a day that was actually measured.
 *
 * A year is 365 days across a few hundred pixels, so one day is barely a pixel
 * and a half wide — aiming at a particular one is hopeless, and the dots are
 * what anyone is aiming at anyway. Within `SNAP` pixels of a reading, that
 * reading wins; anywhere else the day under the pointer is taken as it is, so
 * an empty stretch can still be opened to fill a gap.
 *
 * The crosshair, the tooltip and the click all resolve through here, so what is
 * highlighted is always exactly what a click will open.
 */
Interaction.modes.habitDay = (chart, event) => {
  const position = getRelativePosition(event, chart as never);
  const scale = chart.scales.x;
  const raw = scale.getValueForPixel(position.x);

  if (raw === undefined) return [];

  const meta = chart.getDatasetMeta(0);
  const last = meta.data.length - 1;
  const day = Math.min(Math.max(Math.round(raw), 0), last);

  const measured =
    (chart.data.datasets[0] as unknown as { measured?: number[] }).measured ??
    [];

  let index = day;
  let nearest = SNAP;

  for (const mark of measured) {
    const distance = Math.abs(scale.getPixelForValue(mark) - position.x);

    if (distance <= nearest) {
      nearest = distance;
      index = mark;
    }
  }

  // Days past today hold nothing and are drawn skipped: no highlight, and
  // nothing for a click to open.
  const element = meta.data[index] as (typeof meta.data)[number] & {
    skip?: boolean;
  };

  return element && !element.skip ? [{ element, datasetIndex: 0, index }] : [];
};

interface HabitsTrendChartProps {
  habit: Habit;
  year: number;
  /** "YYYY-MM-DD" -> value, for this habit and this year only. */
  values: Record<string, number>;
  /** Today's date. Nothing is drawn or opened past it. */
  today: string;
}

const { habit, year, values, today } = defineProps<HabitsTrendChartProps>();

const emit = defineEmits<{ select: [date: string] }>();

const i18n = useI18n();

const reducedMotion = useMediaQuery("(prefers-reduced-motion: reduce)");

/** Recessive chrome: one shade off the surface, never competing with the line. */
const GRID = "rgb(248 249 250 / 0.07)";
const INK = "#adb5bd";
/** The pill the rest of the page uses, so the tooltip is the same object. */
const PILL = "rgb(0 0 0 / 0.75)";

const format = (value: number) => formatNumber(value, i18n.locale.value);

/** Every day of the year, so the spacing is real time and not "per reading". */
const days = computed(() => {
  const first = new Date(year, 0, 1);
  const count =
    (new Date(year + 1, 0, 1).getTime() - first.getTime()) / 86400000;

  return Array.from({ length: count }, (_, index) =>
    toIsoDate(new Date(year, 0, 1 + index)),
  );
});

/** The days that were actually measured. Everything else is derived from these. */
const readings = computed(() => days.value.map((day) => values[day] ?? null));

/**
 * A value for every day up to today, built around the days actually measured.
 *
 * Between two readings the line **runs from one to the other**: a day in the
 * middle takes its share of the way, so two weigh-ins a fortnight apart are
 * joined by a steady slope rather than by a step that drops all at once on the
 * second day. Outside that span there is nothing to run towards, so the nearest
 * reading is simply held — forward past the last one, and backwards into the
 * days before the first.
 *
 * None of this is stored. Every filled day says on hover where its number comes
 * from, so a slope is never mistaken for a run of daily weigh-ins.
 */
const series = computed(() => {
  const marks = days.value
    .map((day, index) => ({ day, index, value: values[day] }))
    .filter(
      (mark): mark is { day: string; index: number; value: number } =>
        mark.value !== undefined,
    );

  const blank = {
    value: null as number | null,
    measured: false,
    before: false,
    from: null as string | null,
    to: null as string | null,
  };

  if (marks.length === 0) return days.value.map(() => ({ ...blank }));

  // Walks along with the days, so each one knows the readings either side of it.
  let next = 0;

  return days.value.map((day, index) => {
    // The future is never filled: a weigh-in says nothing about a day that has
    // not happened, and the year grid leaves those days inert too.
    if (day > today) return { ...blank };

    while (next < marks.length && marks[next].index < index) next += 1;

    const ahead = marks[next] ?? null;
    const behind = next > 0 ? marks[next - 1] : null;

    if (ahead?.index === index) {
      return {
        value: ahead.value,
        measured: true,
        before: false,
        from: day,
        to: null,
      };
    }

    // Before the first reading, and after the last: one point is not a trend.
    if (!behind) {
      return {
        value: marks[0].value,
        measured: false,
        before: true,
        from: marks[0].day,
        to: null,
      };
    }

    if (!ahead) {
      return {
        value: behind.value,
        measured: false,
        before: false,
        from: behind.day,
        to: null,
      };
    }

    const share = (index - behind.index) / (ahead.index - behind.index);

    return {
      value: roundValue(behind.value + (ahead.value - behind.value) * share),
      measured: false,
      before: false,
      from: behind.day,
      to: ahead.day,
    };
  });
});

const shortDate = (day: string) =>
  new Date(`${day}T00:00:00`).toLocaleDateString(i18n.locale.value, {
    day: "numeric",
    month: "long",
  });

/**
 * The window the line lives in, padded so it never touches the frame.
 *
 * The target is always in it, however far off the readings are: a measurement
 * is tracked *against* its target, and a chart that cropped it away would hide
 * the one relationship the whole card is about.
 */
const bounds = computed(() => {
  const points = readings.value.filter(
    (value): value is number => value !== null,
  );

  points.push(habit.goal);

  const low = Math.min(...points);
  const high = Math.max(...points);
  // A single reading sitting on its target still needs a window, or the axis
  // collapses to nothing.
  const padding = (high - low || Math.abs(high) || 1) * 0.15;

  return { min: low - padding, max: high + padding };
});

/**
 * The target, as a threshold rather than a second series: dashed, muted, and
 * labelled on the canvas, so no legend has to explain a line that is chrome.
 */
const targetLine: Plugin<"line"> = {
  id: "habit-target",
  afterDatasetsDraw(chart) {
    const { ctx, chartArea, scales } = chart;
    const y = scales.y.getPixelForValue(habit.goal);

    ctx.save();
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = GRID;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(chartArea.left, y);
    ctx.lineTo(chartArea.right, y);
    ctx.stroke();

    ctx.setLineDash([]);
    ctx.fillStyle = INK;
    ctx.font = "10px Inter, sans-serif";
    ctx.textAlign = "right";
    ctx.textBaseline = "bottom";
    ctx.fillText(
      i18n.t("habits.trend.target", {
        value: format(habit.goal),
        unit: habit.unit,
      }),
      chartArea.right,
      y - 3,
    );
    ctx.restore();
  },
};

/** A hairline down from the reading under the pointer, so the date is unambiguous. */
const crosshair: Plugin<"line"> = {
  id: "habit-crosshair",
  afterDatasetsDraw(chart) {
    const active = chart.getActiveElements();

    if (active.length === 0) return;

    const { ctx, chartArea } = chart;

    ctx.save();
    ctx.strokeStyle = "rgb(248 249 250 / 0.25)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(active[0].element.x, chartArea.top);
    ctx.lineTo(active[0].element.x, chartArea.bottom);
    ctx.stroke();
    ctx.restore();
  },
};

const chartData = computed(() => ({
  labels: days.value,
  datasets: [
    {
      data: series.value.map((point) => point.value),
      // The indices the hit test is allowed to snap to.
      measured: series.value.flatMap((point, index) =>
        point.measured ? [index] : [],
      ),
      borderColor: habit.color,
      borderWidth: 2,
      // Straight between readings: interpolation is the only honest curve when
      // the days in between were never measured.
      tension: 0,
      spanGaps: true,
      // The dots are the measurements; the line between them is the value
      // carried forward. One glance says which days were actually weighed.
      pointRadius: (context: ScriptableContext<"line">) =>
        series.value[context.dataIndex]?.measured ? 3 : 0,
      pointBackgroundColor: habit.color,
      pointHoverRadius: (context: ScriptableContext<"line">) =>
        series.value[context.dataIndex]?.measured ? 5 : 4,
      pointHoverBackgroundColor: habit.color,
      // The 2px ring that keeps a marker off whatever it overlaps.
      pointHoverBorderColor: "#252525",
      pointHoverBorderWidth: 2,
      fill: true,
      backgroundColor: (context: ScriptableContext<"line">) => {
        const { ctx, chartArea } = context.chart;

        if (!chartArea) return "transparent";

        const gradient = ctx.createLinearGradient(
          0,
          chartArea.top,
          0,
          chartArea.bottom,
        );

        gradient.addColorStop(
          0,
          `color-mix(in srgb, ${habit.color} 28%, transparent)`,
        );
        gradient.addColorStop(1, "transparent");

        return gradient;
      },
    },
  ],
}));

const options = computed<ChartOptions<"line">>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: reducedMotion.value ? false : { duration: 400 },
  interaction: { mode: "habitDay", intersect: false },
  // Straight off what the crosshair is showing. `habitDay` resolved it, so the
  // day that was highlighted and the day that opens can never disagree — which
  // is the whole reason a click used to feel like it missed.
  onClick: (_event, elements) => {
    const day = days.value[elements[0]?.index ?? -1];

    if (day) emit("select", day);
  },
  scales: {
    x: {
      grid: { display: false },
      border: { color: GRID },
      ticks: {
        color: INK,
        font: { size: 10 },
        autoSkip: false,
        maxRotation: 0,
        // One label per month, on its first day. Anything denser is unreadable
        // at 53 weeks wide, and anything automatic lands on arbitrary dates.
        callback(_value, index) {
          const day = days.value[index];

          if (!day?.endsWith("-01")) return null;

          return i18n.t(`habits.months.${Number(day.slice(5, 7)) - 1}`);
        },
      },
    },
    y: {
      min: bounds.value.min,
      max: bounds.value.max,
      grid: { color: GRID },
      border: { display: false },
      ticks: { color: INK, font: { size: 10 }, maxTicksLimit: 5 },
    },
  },
  plugins: {
    // One series: the card header already names it, so a legend box would only
    // repeat the title.
    legend: { display: false },
    tooltip: {
      backgroundColor: PILL,
      titleColor: "#f8f9fa",
      bodyColor: "#f8f9fa",
      cornerRadius: 6,
      padding: 8,
      displayColors: false,
      titleFont: { size: 13, weight: "normal" },
      bodyFont: { size: 13, weight: "bold" },
      // Before the first reading of the year there is nothing to say, and a
      // zero would be a lie. With every item dropped, no tooltip appears.
      filter: (item) => item.parsed.y !== null,
      callbacks: {
        title: (items) => shortDate(days.value[items[0].dataIndex]),
        label: (item) => `${format(item.parsed.y ?? 0)} ${habit.unit}`.trim(),
        // A day that was not measured names the day it takes its value from, so
        // a flat stretch is never mistaken for a run of identical weigh-ins.
        footer: (items) => {
          const point = series.value[items[0].dataIndex];

          if (!point || point.measured || !point.from) return "";

          if (point.before) {
            return i18n.t("habits.trend.before", {
              date: shortDate(point.from),
            });
          }

          if (point.to) {
            return i18n.t("habits.trend.between", {
              from: shortDate(point.from),
              to: shortDate(point.to),
            });
          }

          return i18n.t("habits.trend.carried", {
            date: shortDate(point.from),
          });
        },
      },
      footerColor: "#adb5bd",
      footerFont: { size: 12, weight: "normal" },
    },
  },
}));

const plugins = [targetLine, crosshair];

const wrapper = useTemplateRef<HTMLElement>("wrapper");
const available = ref(0);

/**
 * The panel stands exactly as tall as a year of squares would in its place.
 *
 * A ratio cannot express it: the grid's height grows with its width but carries
 * a fixed month band on top, and stops growing at `GRID.maxWidth` while this
 * panel keeps going. So it is measured and computed from the same geometry the
 * grid is built from.
 */
const height = computed(() => `${gridHeight(available.value)}px`);

let observer: ResizeObserver | undefined;

onMounted(() => {
  if (!wrapper.value) return;

  observer = new ResizeObserver(([entry]) => {
    available.value = entry.contentRect.width;
  });

  observer.observe(wrapper.value);
});

onBeforeUnmount(() => observer?.disconnect());

const hasReadings = computed(() =>
  readings.value.some((value) => value !== null),
);

/** Chart.js keeps a canvas alive per key; the year is what invalidates it. */
const chartKey = computed(() => `${habit.id}-${year}`);

defineExpose({ hasReadings });
</script>

<template>
  <div ref="wrapper" class="w-full" :style="{ height }">
    <Line
      v-if="hasReadings"
      :key="chartKey"
      :data="chartData as ChartType<'line'>['data']"
      :options="options"
      :plugins="plugins"
    />

    <p
      v-else
      class="m-0 flex h-full items-center justify-center text-center text-sm text-accent"
    >
      {{ $t("habits.trend.empty", { year }) }}
    </p>
  </div>
</template>
