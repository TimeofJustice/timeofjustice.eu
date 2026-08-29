/** Runs of days that met the goal. Counted over all time, not over one year. */
export interface HabitStreak {
  /** Days in a row up to now. Not broken until a day has been missed outright. */
  current: number;
  /** The best run there has ever been. */
  longest: number;
}

/**
 * `goal` is a daily target, met or missed, drawn as a year of squares.
 * `measure` is a reading drawn as a line, where `goal` is a target to move
 * towards. Both carry streaks.
 */
export type HabitKind = "goal" | "measure";

export interface Habit {
  id: number;
  kind: HabitKind;
  name: string;
  /** Shown next to the numbers ("steps", "min"). May be empty. */
  unit: string;
  /** What counts as a full day. With `goalMax`, the bottom of the zone. */
  goal: number;
  /**
   * The top of the goal zone, or null for the ordinary goal where more is
   * always better. With one, 200 g of protein misses a 120–140 g zone exactly
   * as 100 g does.
   */
  goalMax: number | null;
  /** How much one tap on the quick-add button adds. */
  step: number;
  /** Hex colour the year grid is painted in. */
  color: string;
  /**
   * The weekdays the goal is not asked on, Monday as 0. A standing arrangement
   * rather than a list of dates, so it applies to every week there has been and
   * every week to come.
   */
  restDays: number[];
  order: number;
  /** Takes a whole row on the board rather than sharing one. */
  wide: boolean;
  archived: boolean;
  createdAt: string;
  streak: HabitStreak;
}

/** Logged values of one year: habit id -> "YYYY-MM-DD" -> value. */
export type HabitEntries = Record<string, Record<string, number>>;

/** One cell of the year grid. `date` is null for the padding around the year. */
export interface HabitDay {
  date: string | null;
  value: number;
  level: number;
  /** Marked as a day off: the goal was not asked for. */
  rest: boolean;
  /** Past the top of the goal zone. Full, but not met. */
  over: boolean;
  /** Still to come. Shown, but not tracked: only the past can be logged. */
  future: boolean;
}

/**
 * One habit's share of a recap: the habit itself, plus what it did over the
 * span being looked back on.
 *
 * A field the habit's kind has no answer for is null rather than zero, so
 * "nothing to say" reads differently from "nothing happened": a measurement
 * has no goal-days, and a daily goal has no reading.
 */
export interface HabitRecapEntry extends Habit {
  /** Days of the span that got an entry. */
  logged: number;
  /** Those days' values, "YYYY-MM-DD" -> value. Only the logged ones. */
  values: Record<string, number>;
  /**
   * The last day this habit was logged at all, over all time. Reaches back
   * past the span on purpose: after a long absence everything inside the span
   * is a zero, and this is what is still worth saying.
   */
  lastLogged: string | null;
  /** Goal only: days the goal was met, and how many it was the span before. */
  done: number | null;
  previousDone: number | null;
  /** Goal only: what the span's days add up to. */
  total: number | null;
  /** Measure only: where it stands, how far it moved, and whether that closed
   *  the gap to the target. */
  latest: number | null;
  delta: number | null;
  closed: number | null;
}

/** A span as a whole, counted over the goal habits that are still tracked. */
export interface HabitRecapTotals {
  /** Goal-days met, out of the ones the span had on offer. */
  done: number;
  possible: number;
  /** Days anything at all was logged, and days every goal came in. */
  activeDays: number;
  perfectDays: number;
}

/**
 * The look back the page opens by itself, once, after a week has ended.
 *
 * `recap` is the ordinary one week. `welcome_back` is the same figures over a
 * longer absence, worded as a return rather than as a report.
 */
export interface HabitRecap {
  kind: "recap" | "welcome_back";
  /** The span, inclusive, as "YYYY-MM-DD". */
  start: string;
  end: string;
  days: number;
  weeks: number;
  /** The last day anything was logged, and the days logged over all time. */
  lastActive: string | null;
  trackedDays: number;
  habits: HabitRecapEntry[];
  totals: HabitRecapTotals;
  previousTotals: HabitRecapTotals;
}
