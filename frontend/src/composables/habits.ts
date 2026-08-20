import axios from "axios";
import type {
  Habit,
  HabitDay,
  HabitEntries,
  HabitStreak,
} from "@/types/Habit.ts";

/**
 * How full a day's square is painted, 0 (nothing logged) to 5 (goal reached).
 * Five steps is what makes a half-done day tell itself apart from an almost-
 * done one at a glance.
 */
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

/**
 * The habit's colour, faded to match the level. Level 0 returns null so the
 * caller can fall back to the neutral "nothing here" square.
 */
export const levelColor = (color: string, level: number) => {
  if (level <= 0) return null;

  return `color-mix(in srgb, ${color} ${LEVEL_MIX[level]}%, transparent)`;
};

/** Two decimals, matching what the database stores. */
const PLACES = 100;

/**
 * Reads a number the way a person writes one — "7,5" as readily as "7.5", since
 * a German keyboard puts a comma there. `NaN` for anything that is not one.
 */
export const parseDecimal = (input: string | number | null | undefined) => {
  if (typeof input === "number") return Number.isFinite(input) ? input : NaN;

  const normalised = String(input ?? "")
    .replace(",", ".")
    .trim();

  return normalised === "" ? NaN : Number(normalised);
};

/**
 * Pins a number to the stored precision. Without this, tapping "+0.5" twice on
 * a 0.1 step leaves 0.30000000000000004 on the screen.
 */
export const roundValue = (value: number) =>
  Math.round(value * PLACES) / PLACES;

/** Thousands separators, and at most the two decimals that are stored. */
export const formatNumber = (value: number, locale: string) =>
  value.toLocaleString(locale, { maximumFractionDigits: 2 });

export const toIsoDate = (date: Date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

/**
 * The year laid out as calendar weeks, the way a contribution graph reads:
 * one column per week, Monday at the top. The first and last column are padded
 * with null days so every column holds seven cells.
 */
export const yearWeeks = (
  year: number,
  values: Record<string, number>,
  goal: number,
  today: string,
): HabitDay[][] => {
  const first = new Date(year, 0, 1);
  // Monday-based offset: getDay() has Sunday at 0, which would start the week
  // on the wrong day for a European calendar.
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

      // ISO dates sort like strings, so this is the whole comparison.
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
 * Which column each month starts in, for the labels above the grid. A month
 * whose first day falls late in a column is skipped, its label would sit on
 * top of the previous one.
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
 * Days the goal was met, and the total, for the year on screen.
 *
 * Streaks are deliberately absent: they run past New Year, so only the server —
 * which has every year — can count them.
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

export const api = {
  year: (year: number) =>
    axios
      .get<{ year: number; entries: HabitEntries }>(`/habits/api/year/${year}/`)
      .then((response) => response.data),

  create: (habit: Partial<Habit>) =>
    axios
      .post<{ habit: Habit }>("/habits/api/habit/", habit)
      .then((response) => response.data.habit),

  update: (id: number, habit: Partial<Habit>) =>
    axios
      .post<{ habit: Habit }>(`/habits/api/habit/${id}/`, habit)
      .then((response) => response.data.habit),

  remove: (id: number) => axios.post(`/habits/api/habit/${id}/delete/`),

  log: (id: number, date: string, value: number) =>
    axios
      .post<{
        habitId: number;
        date: string;
        value: number;
        streak: HabitStreak;
      }>(`/habits/api/habit/${id}/log/`, { date, value })
      .then((response) => response.data),
};
