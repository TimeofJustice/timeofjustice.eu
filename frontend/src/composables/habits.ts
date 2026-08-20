import axios from "axios";
import type {
  Habit,
  HabitDay,
  HabitEntries,
  HabitStreak,
} from "@/types/Habit.ts";

/** How full a day's square is painted, 0 (nothing logged) to 5 (goal reached). */
export const levelOf = (value: number, goal: number) => {
  if (value <= 0) return 0;

  const ratio = goal > 0 ? value / goal : 1;

  if (ratio >= 1) return 5;
  if (ratio >= 0.75) return 4;
  if (ratio >= 0.5) return 3;
  if (ratio >= 0.25) return 2;

  return 1;
};

/** Opacity of each level, as a percentage of the habit's colour. */
export const LEVEL_MIX = [0, 22, 40, 58, 76, 100];

/** The habit's colour faded to the level. Null at 0, for the neutral square. */
export const levelColor = (color: string, level: number) => {
  if (level <= 0) return null;

  return `color-mix(in srgb, ${color} ${LEVEL_MIX[level]}%, transparent)`;
};

/** Two decimals, matching what the database stores. */
const PLACES = 100;

/** Takes a comma as readily as a point, since a German keyboard types one. */
export const parseDecimal = (input: string | number | null | undefined) => {
  if (typeof input === "number") return Number.isFinite(input) ? input : NaN;

  const normalised = String(input ?? "")
    .replace(",", ".")
    .trim();

  return normalised === "" ? NaN : Number(normalised);
};

/**
 * Pins a number to the stored precision. Without it, "+0.5" twice on a 0.1 step
 * leaves 0.30000000000000004 on the screen.
 */
export const roundValue = (value: number) =>
  Math.round(value * PLACES) / PLACES;

/** Thousands separators, and at most the two decimals that are stored. */
export const formatNumber = (value: number, locale: string) =>
  value.toLocaleString(locale, { maximumFractionDigits: 2 });

/**
 * The year grid's geometry, in pixels. `HabitsYearGrid` builds itself from these
 * and `gridHeight()` computes from the same numbers, which is how a chart beside
 * a grid ends up exactly as tall. Hard-code one in a template and they drift.
 */
export const GRID = {
  columns: 53,
  rows: 7,
  /** Between squares, and between the weekday rows that line up with them. */
  gap: 2,
  /** The month band above the squares. */
  header: 17,
  /** The weekday column, and its distance from the first square. */
  labelWidth: 18,
  labelGap: 4,
  /** The ring the scroller keeps for hover growth and label overhang. */
  padding: 4,
  /** Below this it scrolls rather than shrinking; above it, it stops growing. */
  minWidth: 420,
  maxWidth: 860,
};

/** How tall a year of squares stands inside a panel of the given width. */
export const gridHeight = (available: number) => {
  const inner = Math.min(
    GRID.maxWidth,
    Math.max(GRID.minWidth, available - GRID.padding * 2),
  );

  const square =
    (inner - GRID.labelWidth - GRID.labelGap - (GRID.columns - 1) * GRID.gap) /
    GRID.columns;

  return (
    GRID.padding * 2 +
    GRID.header +
    GRID.rows * square +
    (GRID.rows - 1) * GRID.gap
  );
};

export const toIsoDate = (date: Date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

/**
 * One column per week, Monday at the top. The first and last column are padded
 * with null days so every column holds seven cells.
 */
export const yearWeeks = (
  year: number,
  values: Record<string, number>,
  goal: number,
  today: string,
): HabitDay[][] => {
  const first = new Date(year, 0, 1);
  // Monday-based: getDay() puts Sunday at 0.
  const offset = (first.getDay() + 6) % 7;
  const dayCount =
    (new Date(year + 1, 0, 1).getTime() - first.getTime()) / 86400000;

  const weeks: HabitDay[][] = [];
  let week: HabitDay[] = [];

  for (let cell = 0; cell < offset + dayCount; cell++) {
    const dayOfYear = cell - offset;

    if (dayOfYear < 0) {
      week.push({ date: null, value: 0, level: 0, future: false });
    } else {
      const date = toIsoDate(new Date(year, 0, 1 + dayOfYear));
      const value = values[date] ?? 0;

      // ISO dates sort like strings.
      week.push({
        date,
        value,
        level: levelOf(value, goal),
        future: date > today,
      });
    }

    if (week.length === 7) {
      weeks.push(week);
      week = [];
    }
  }

  // Trailing days of the final, incomplete week.
  while (week.length > 0 && week.length < 7) {
    week.push({ date: null, value: 0, level: 0, future: false });
  }

  if (week.length > 0) weeks.push(week);

  return weeks;
};

/**
 * Which column each month's label goes above. A month starting late in a column
 * is skipped, or its label would sit on top of the previous one.
 */
export const monthColumns = (weeks: HabitDay[][]) => {
  const columns: { month: number; column: number }[] = [];

  weeks.forEach((week, column) => {
    const firstDay = week.find((day) => day.date !== null);

    if (!firstDay?.date) return;

    const date = new Date(`${firstDay.date}T00:00:00`);

    if (date.getDate() > 7) return;
    if (columns[columns.length - 1]?.month === date.getMonth()) return;

    columns.push({ month: date.getMonth(), column });
  });

  return columns;
};

/**
 * Days the goal was met, and the total, for the year on screen. Streaks are
 * absent on purpose: they run past New Year, so only the server can count them.
 */
export const habitStats = (values: Record<string, number>, goal: number) => {
  let done = 0;
  let total = 0;

  for (const value of Object.values(values)) {
    total += value;

    if (value >= goal) done += 1;
  }

  // Summed as floats, so the total needs pinning back to two decimals.
  return { done, total: roundValue(total) };
};

/** What a measurement's year says. `toTarget` is signed, never judged. */
export const measureStats = (
  values: Record<string, number>,
  target: number,
) => {
  const dates = Object.keys(values).sort();

  if (dates.length === 0) {
    return {
      count: 0,
      latest: null,
      latestDate: null,
      delta: 0,
      toTarget: null,
      closed: 0,
      min: 0,
      max: 0,
    };
  }

  const readings = dates.map((date) => values[date]);
  const latestDate = dates[dates.length - 1];
  const latest = values[latestDate];

  return {
    count: dates.length,
    latest,
    latestDate,
    delta: roundValue(latest - readings[0]),
    toTarget: roundValue(latest - target),
    // How much of the gap to the target was closed; positive means nearer.
    // The target is what decides which way is forwards, so a falling weight
    // and a rising balance both read as progress without a special case.
    closed: roundValue(
      Math.abs(readings[0] - target) - Math.abs(latest - target),
    ),
    min: Math.min(...readings),
    max: Math.max(...readings),
  };
};

/**
 * The reading in force on a day: the last one at or before it, else the first
 * one after. Only *offered* by the day editor; nothing is stored in between.
 */
export const carriedValue = (values: Record<string, number>, date: string) => {
  const dates = Object.keys(values).sort();

  let carried: number | null = null;

  for (const day of dates) {
    if (day <= date) carried = values[day];
    else break;
  }

  return carried ?? (dates.length > 0 ? values[dates[0]] : null);
};

export const api = {
  year: (year: number) =>
    axios
      .get<{
        year: number;
        entries: HabitEntries;
      }>(`/momentum/api/year/${year}/`)
      .then((response) => response.data),

  create: (habit: Partial<Habit>) =>
    axios
      .post<{ habit: Habit }>("/momentum/api/habit/", habit)
      .then((response) => response.data.habit),

  update: (id: number, habit: Partial<Habit>) =>
    axios
      .post<{ habit: Habit }>(`/momentum/api/habit/${id}/`, habit)
      .then((response) => response.data.habit),

  remove: (id: number) => axios.post(`/momentum/api/habit/${id}/delete/`),

  /** Saves the whole arrangement, not a move. See the view's docstring. */
  layout: (habits: { id: number; wide: boolean }[]) =>
    axios
      .post<{ habits: Habit[] }>("/momentum/api/layout/", { habits })
      .then((response) => response.data.habits),

  log: (id: number, date: string, value: number) =>
    axios
      .post<{
        habitId: number;
        date: string;
        value: number;
        streak: HabitStreak;
      }>(`/momentum/api/habit/${id}/log/`, { date, value })
      .then((response) => response.data),
};
