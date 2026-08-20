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
  /** What counts as a full day. */
  goal: number;
  /** How much one tap on the quick-add button adds. */
  step: number;
  /** Hex colour the year grid is painted in. */
  color: string;
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
  /** Still to come. Shown, but not tracked: only the past can be logged. */
  future: boolean;
}
