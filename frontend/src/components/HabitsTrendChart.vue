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
  type ChartType as ChartKind,
  type InteractionModeFunction,
  type Plugin,
  type ScriptableContext,
} from "chart.js";
import { getRelativePosition } from "chart.js/helpers";
import {
  formatNumber,
  gridHeight,
  mondayOf,
  roundValue,
  toIsoDate,
  weeklyAverages,
} from "@composables/habits";
import { useMediaQuery } from "@composables/mediaQuery";
import type { Habit } from "@/types/Habit.ts";

// Only the pieces a line chart needs; the rest of chart.js stays out of the bundle.
Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
);

declare module "chart.js" {
  interface InteractionModeMap {
    habitDay: InteractionModeFunction;
  }

  /**
   * `weekMarks` takes its switch through the chart options rather than off a
   * variable it closes over. The canvas is only repainted when the data or the
   * options change, and a flag held anywhere else would flip without anything
   * asking the chart to draw itself again.
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars -- the parameter is unused here but has to match chart.js's own declaration exactly
  interface PluginOptionsByType<TType extends ChartKind> {
    "habit-weeks"?: { show: boolean };
  }
}

/**
 * Hit testing that takes the day under the pointer, measured or not. Snapping to
 * the nearest reading was tried and does not work here: a day is about a pixel
 * and a half wide at 365 to a panel, so any snap worth the name swallows the
 * fortnight around every reading, and those empty days are the ones worth
 * clicking.
 *
 * Crosshair, tooltip and click all resolve through here so they cannot disagree.
 */
Interaction.modes.habitDay = (chart, event) => {
  // Nothing to point at while the readings are hidden: the crosshair, the
  // tooltip and the click that opens a day all resolve through here.
  if (!chart.isDatasetVisible(0)) return [];

  const position = getRelativePosition(event, chart as never);
  const scale = chart.scales.x;
  const raw = scale.getValueForPixel(position.x);

  if (raw === undefined) return [];

  const meta = chart.getDatasetMeta(0);
  const last = meta.data.length - 1;
  const day = Math.min(Math.max(Math.round(raw), 0), last);

  const dataset = chart.data.datasets[0] as unknown as {
    selectable?: number;
  };

  // Past today the projection answers instead. Readable, but `onClick` ignores
  // it: a day that has not happened cannot be logged.
  if (day > (dataset.selectable ?? last)) {
    const projected = chart.getDatasetMeta(1).data[day] as
      | ((typeof meta.data)[number] & { skip?: boolean })
      | undefined;

    return projected && !projected.skip
      ? [{ element: projected, datasetIndex: 1, index: day }]
      : [];
  }

  // Days past today hold nothing and are drawn skipped: no highlight, and
  // nothing for a click to open.
  const element = meta.data[day] as (typeof meta.data)[number] & {
    skip?: boolean;
  };

  return element && !element.skip
    ? [{ element, datasetIndex: 0, index: day }]
    : [];
};

interface HabitsTrendChartProps {
  habit: Habit;
  year: number;
  /** "YYYY-MM-DD" -> value, for this habit and this year only. */
  values: Record<string, number>;
  /** Today's date. Nothing is drawn or opened past it. */
  today: string;
  /**
   * Which of the two lines to draw. The panel holds these and draws the legend
   * that switches them, because the legend has to sit in the same footer row a
   * year grid puts its own in: a row of its own here would make a chart panel
   * taller than the grid panel beside it.
   */
  showReadings?: boolean;
  showWeeks?: boolean;
}

const {
  habit,
  year,
  values,
  today,
  showReadings = true,
  showWeeks = true,
} = defineProps<HabitsTrendChartProps>();

const emit = defineEmits<{ select: [date: string] }>();

const i18n = useI18n();

const reducedMotion = useMediaQuery("(prefers-reduced-motion: reduce)");

const GRID = "rgb(248 249 250 / 0.07)";
/** The weekly average: light, so it reads over the habit's own colour. */
const WEEK_INK = "rgb(248 249 250 / 0.65)";
/** Where one week gives way to the next. Fainter than the grid: there are 52. */
const WEEK_RULE = "rgb(248 249 250 / 0.05)";
const INK = "#adb5bd";
/** Matches `UiTooltip`, so the two read as the same object. */
const PILL = "rgb(0 0 0 / 0.75)";

const format = (value: number) => formatNumber(value, i18n.locale.value);

/** Every day of the year, so the x axis is time and not "per reading". */
const days = computed(() => {
  const first = new Date(year, 0, 1);
  const count =
    (new Date(year + 1, 0, 1).getTime() - first.getTime()) / 86400000;

  return Array.from({ length: count }, (_, index) =>
    toIsoDate(new Date(year, 0, 1 + index)),
  );
});

const readings = computed(() => days.value.map((day) => values[day] ?? null));

const hasReadings = computed(() =>
  readings.value.some((value) => value !== null),
);

/** The last day that can be pointed at. A year gone by is live to its end. */
const lastLive = computed(() => {
  const future = days.value.findIndex((day) => day > today);

  return future === -1 ? days.value.length - 1 : future - 1;
});

/** The measured days, in order, with their place in the year. */
const marks = computed(() =>
  days.value
    .map((day, index) => ({ day, index, value: values[day] }))
    .filter(
      (mark): mark is { day: string; index: number; value: number } =>
        mark.value !== undefined,
    ),
);

/**
 * A value for every day up to today. Days between two readings are interpolated;
 * outside that span the nearest reading is held.
 *
 * None of it is stored, and every filled day says on hover where its number came
 * from, so a slope is not mistaken for a run of daily weigh-ins.
 */
const series = computed(() => {
  const points = marks.value;

  const blank = {
    value: null as number | null,
    measured: false,
    before: false,
    from: null as string | null,
    to: null as string | null,
  };

  // An empty year gets a flat zero baseline instead, and unlike everything else
  // here it runs past today: bounded at today it would be two days long every
  // January. Dashed, and its tooltip says it is not a reading.
  if (points.length === 0)
    return days.value.map(() => ({ ...blank, value: 0 }));

  // Walks along with the days, so each knows the readings either side of it.
  let next = 0;

  return days.value.map((day, index) => {
    if (day > today) return { ...blank };

    while (next < points.length && points[next].index < index) next += 1;

    const ahead = points[next] ?? null;
    const behind = next > 0 ? points[next - 1] : null;

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
        value: points[0].value,
        measured: false,
        before: true,
        from: points[0].day,
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

/**
 * How much the readings move per day, by least squares over the year. Fewer than
 * two readings, or all of them equal, is a level rather than a direction: flat.
 */
const slope = computed(() => {
  const points = marks.value;

  if (points.length < 2) return 0;

  const meanDay =
    points.reduce((sum, point) => sum + point.index, 0) / points.length;
  const meanValue =
    points.reduce((sum, point) => sum + point.value, 0) / points.length;

  let product = 0;
  let spread = 0;

  for (const point of points) {
    product += (point.index - meanDay) * (point.value - meanValue);
    spread += (point.index - meanDay) ** 2;
  }

  return spread === 0 ? 0 : product / spread;
});

/** Where the readings are heading, to New Year and through the target. */
const projection = computed(() => {
  const last = marks.value[marks.value.length - 1];
  const start = lastLive.value;
  const end = days.value.length - 1;

  // Nothing measured, or no year left to run into.
  if (!last || start < 0 || end <= start) return null;

  const line: (number | null)[] = days.value.map(() => null);

  // Anchored on the last reading, which the solid line holds forward to today,
  // so the two meet without a step.
  line[start] = last.value;

  for (let index = start + 1; index <= end; index += 1) {
    line[index] = roundValue(last.value + slope.value * (index - start));
  }

  return line;
});

/**
 * The year cut into weeks: where each one starts and ends among the days, and
 * what it averaged.
 *
 * This is the answer to the daily line's noise. A weight that swings a kilo
 * with the salt in yesterday's dinner still has a week that plainly went one
 * way, and a flat bar across the week says so without pretending to know what
 * happened on the days nobody stepped on the scales.
 *
 * A week runs to today and no further: the bar over the week being lived covers
 * the days it has had, not the ones it has yet to get. Weeks with nothing
 * measured keep their separator and get no bar at all.
 */
const weekBands = computed(() => {
  const averages = new Map(
    weeklyAverages(values).map((week) => [week.week, week.average]),
  );

  const bands: {
    monday: string;
    start: number;
    end: number;
    average: number | null;
  }[] = [];

  days.value.forEach((day, index) => {
    const monday = mondayOf(day);
    const open = bands[bands.length - 1];

    if (open?.monday === monday) open.end = index;
    else
      bands.push({
        monday,
        start: index,
        end: index,
        average: averages.get(monday) ?? null,
      });
  });

  return bands;
});

/** Which band each day belongs to, so the tooltip can name its week's average. */
const bandOfDay = computed(() => {
  const index: (number | null)[] = days.value.map(() => null);

  weekBands.value.forEach((band, position) => {
    for (let day = band.start; day <= band.end; day += 1) {
      index[day] = position;
    }
  });

  return index;
});

/** What the week under the pointer averaged, for the tooltip. */
const weekAt = (index: number) => {
  const band = bandOfDay.value[index];

  return band === null ? null : weekBands.value[band].average;
};

/**
 * Where one day gives way to the next, in pixels: halfway between their two
 * points. The scale puts a day on a point rather than in a slot, so a boundary
 * is between two of them and the ends of the year are the frame itself.
 */
const edgeAt = (chart: ChartType<"line">, index: number) => {
  const { chartArea, scales } = chart;

  if (index <= 0) return chartArea.left;
  if (index >= days.value.length) return chartArea.right;

  return (
    (scales.x.getPixelForValue(index - 1) + scales.x.getPixelForValue(index)) /
    2
  );
};

const shortDate = (day: string) =>
  new Date(`${day}T00:00:00`).toLocaleDateString(i18n.locale.value, {
    day: "numeric",
    month: "long",
  });

/**
 * The y window, padded so the line never touches the frame. The target is always
 * inside it: a measurement is tracked *against* its target, and cropping it away
 * would hide the one relationship the card exists for.
 */
const bounds = computed(() => {
  const points = readings.value.filter(
    (value): value is number => value !== null,
  );

  points.push(habit.goal);

  // Both are drawn, so both are framed: the empty year's zero baseline, and the
  // projection, whose far end is the thing being read off the axis.
  if (!hasReadings.value) points.push(0);

  for (const value of projection.value ?? []) {
    if (value !== null) points.push(value);
  }

  const low = Math.min(...points);
  const high = Math.max(...points);
  // A single reading sitting on its target would otherwise collapse the axis.
  const padding = (high - low || Math.abs(high) || 1) * 0.15;

  return { min: low - padding, max: high + padding };
});

/** The target as a threshold, labelled on the canvas because there is no legend. */
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

/**
 * Names the projection at its far end. Both labels are pinned to the right edge,
 * so this one steps below its line when it would collide with the target's.
 */
const trendLabel: Plugin<"line"> = {
  id: "habit-trend",
  afterDatasetsDraw(chart) {
    if (chart.data.datasets.length < 2) return;

    const points = chart.getDatasetMeta(1).data as unknown as {
      x: number;
      y: number;
      skip?: boolean;
    }[];

    // The last day the line reaches; past it are nulls the renderer skipped.
    let end: (typeof points)[number] | undefined;

    for (const point of points) if (!point.skip) end = point;

    if (!end) return;

    const { ctx, scales } = chart;
    const clash = Math.abs(end.y - scales.y.getPixelForValue(habit.goal)) < 14;

    ctx.save();
    ctx.fillStyle = INK;
    ctx.font = "10px Inter, sans-serif";
    ctx.textAlign = "right";
    ctx.textBaseline = clash ? "top" : "bottom";
    ctx.fillText(
      i18n.t("habits.trend.projected"),
      end.x,
      clash ? end.y + 5 : end.y - 5,
    );
    ctx.restore();
  },
};

/**
 * The weeks: a hairline where each one begins, and a bar across it at what it
 * averaged.
 *
 * Drawn rather than plotted, because neither is a series. The separators go
 * under the readings, where the rest of the grid lives, and the bars go over
 * them, because a bar hidden behind the line it is summarising would be no use.
 */
const weekMarks: Plugin<"line"> = {
  id: "habit-weeks",

  beforeDatasetsDraw(chart, _args, options) {
    // An empty year is a dashed baseline and nothing else. Ruling it into weeks
    // would be drawing a calendar over the fact that nothing was measured.
    if (!options.show || !hasReadings.value) return;

    const { ctx, chartArea } = chart;

    ctx.save();
    ctx.strokeStyle = WEEK_RULE;
    ctx.lineWidth = 1;

    // Not the first: the axis is already drawn there.
    for (const band of weekBands.value.slice(1)) {
      // Halfway between the Sunday and the Monday, so the line falls between
      // two days rather than through one of them.
      const x = Math.round(edgeAt(chart, band.start)) + 0.5;

      ctx.beginPath();
      ctx.moveTo(x, chartArea.top);
      ctx.lineTo(x, chartArea.bottom);
      ctx.stroke();
    }

    ctx.restore();
  },

  afterDatasetsDraw(chart, _args, options) {
    if (!options.show) return;

    const { ctx, scales } = chart;

    ctx.save();
    ctx.strokeStyle = WEEK_INK;
    ctx.lineWidth = 2;
    ctx.lineCap = "butt";

    for (const band of weekBands.value) {
      // A week with nothing measured has no average, and a week still to come
      // has nothing to average yet.
      if (band.average === null || band.start > lastLive.value) continue;

      const y = scales.y.getPixelForValue(band.average);
      // Stops at today, so the week being lived does not draw across days it
      // has not had.
      const right = edgeAt(chart, Math.min(band.end, lastLive.value) + 1);

      ctx.beginPath();
      ctx.moveTo(edgeAt(chart, band.start), y);
      ctx.lineTo(right, y);
      ctx.stroke();
    }

    ctx.restore();
  },
};

/** A hairline down from the reading under the pointer. */
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

const projectionSet = computed(() =>
  projection.value
    ? [
        {
          data: projection.value,
          // Drawn from the readings, so it goes when they do.
          hidden: !showReadings,
          // Faded and dashed like the target: a line nobody measured.
          borderColor: `color-mix(in srgb, ${habit.color} 55%, transparent)`,
          borderWidth: 2,
          borderDash: [5, 5],
          tension: 0,
          // The nulls before today are a gap, not something to bridge.
          spanGaps: false,
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHoverBackgroundColor: `color-mix(in srgb, ${habit.color} 55%, transparent)`,
          pointHoverBorderColor: "#252525",
          pointHoverBorderWidth: 2,
          fill: false,
        },
      ]
    : [],
);

const chartData = computed(() => ({
  labels: days.value,
  datasets: [
    {
      data: series.value.map((point) => point.value),
      hidden: !showReadings,
      // Read by `habitDay`: how far into the year it may resolve.
      selectable: lastLive.value,
      // An empty year's baseline is dashed and faded, so it is not read as a
      // year of zero weigh-ins.
      borderColor: hasReadings.value
        ? habit.color
        : `color-mix(in srgb, ${habit.color} 45%, transparent)`,
      borderDash: hasReadings.value ? [] : [5, 5],
      borderWidth: 2,
      // Straight between readings: a curve would invent days nobody measured.
      tension: 0,
      spanGaps: true,
      // Nothing but the line, until the pointer names a day. A year of daily
      // weigh-ins is 365 dots two pixels apart, which reads as a fat band.
      pointRadius: 0,
      pointBackgroundColor: habit.color,
      pointHoverRadius: (context: ScriptableContext<"line">) =>
        series.value[context.dataIndex]?.measured ? 5 : 4,
      pointHoverBackgroundColor: habit.color,
      pointHoverBorderColor: "#252525",
      pointHoverBorderWidth: 2,
      // The tinted area says how much was measured, so a baseline gets none.
      fill: hasReadings.value,
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
    ...projectionSet.value,
  ],
}));

const options = computed<ChartOptions<"line">>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: reducedMotion.value ? false : { duration: 400 },
  interaction: { mode: "habitDay", intersect: false },
  // Straight off what the crosshair is showing, so the day highlighted and the
  // day that opens cannot disagree.
  onClick: (_event, elements) => {
    // The projection resolves through the same hit test, but is not editable.
    if (elements[0]?.datasetIndex !== 0) return;

    const day = days.value[elements[0].index];

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
        // One label per month. Anything automatic lands on arbitrary dates.
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
    // Read by `weekMarks`. Here rather than closed over, so that switching the
    // weeks off is a change to the options and the chart repaints by itself.
    "habit-weeks": { show: showWeeks },
    // One series, and the card header already names it.
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
      // Dropping every item is what suppresses the tooltip on an unfilled day.
      filter: (item) => item.parsed.y !== null,
      callbacks: {
        title: (items) => shortDate(days.value[items[0].dataIndex]),
        // "0 kg" would be a lie on an empty year: the line is a baseline.
        label: (item) =>
          hasReadings.value
            ? `${format(item.parsed.y ?? 0)} ${habit.unit}`.trim()
            : i18n.t("habits.trend.no_reading"),
        // An unmeasured day names where its value came from, so a flat stretch
        // is not mistaken for a run of identical weigh-ins.
        footer: (items) => {
          if (items[0].datasetIndex === 1) {
            return i18n.t("habits.trend.projected");
          }

          const point = series.value[items[0].dataIndex];
          const lines: string[] = [];

          // Where the number came from, when nobody measured this day.
          if (point && !point.measured && point.from) {
            if (point.before) {
              lines.push(
                i18n.t("habits.trend.before", { date: shortDate(point.from) }),
              );
            } else if (point.to) {
              lines.push(
                i18n.t("habits.trend.between", {
                  from: shortDate(point.from),
                  to: shortDate(point.to),
                }),
              );
            } else {
              lines.push(
                i18n.t("habits.trend.carried", { date: shortDate(point.from) }),
              );
            }
          }

          // What the week around it averaged, which is the line drawn over it.
          const average = weekAt(items[0].dataIndex);

          if (average !== null && average !== undefined) {
            lines.push(
              i18n.t("habits.trend.week_average", {
                value: format(average),
                unit: habit.unit,
              }),
            );
          }

          return lines;
        },
      },
      footerColor: "#adb5bd",
      footerFont: { size: 12, weight: "normal" },
    },
  },
}));

const plugins = [weekMarks, targetLine, trendLabel, crosshair];

const wrapper = useTemplateRef<HTMLElement>("wrapper");
const available = ref(0);

/**
 * As tall as a year of squares would be in its place. No CSS ratio expresses it:
 * the grid carries a fixed month band and stops growing at `GRID.maxWidth` while
 * this panel keeps going, so the relationship is affine and clamped.
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

/** Chart.js keeps one canvas per key; the year is what invalidates it. */
const chartKey = computed(() => `${habit.id}-${year}`);

defineExpose({ hasReadings });
</script>

<template>
  <div ref="wrapper" class="w-full" :style="{ height }">
    <Line
      :key="chartKey"
      :data="chartData as ChartType<'line'>['data']"
      :options="options"
      :plugins="plugins"
    />
  </div>
</template>
