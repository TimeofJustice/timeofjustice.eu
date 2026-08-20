# Habits

A year of squares per habit, in the spirit of a contribution graph. It belongs
to a [wallet](../games/wallet.md) — there is still no user model — and it is
reachable at `/habits/`.

## The two models

| Model   | What it is                                                                                     |
| ------- | ---------------------------------------------------------------------------------------------- |
| `Habit` | Name, daily `goal`, `unit`, `color`, and a `step`. Owned by a wallet, `CASCADE` on delete.      |
| `Entry` | One `value` on one `date` for one habit. Unique per `(habit, date)`.                            |

`goal`, `step` and `value` are **decimals** with two places — half an hour of
sleep and a quarter litre of water are ordinary things to track. They cross the
wire as floats, since JSON has no decimal type and two places survive a double
intact. `views.to_decimal()` is the only way in: it takes a comma as readily as
a point, rejects `nan`/`inf` (which `Decimal` otherwise parses quite happily),
and rounds before the range is checked — `0.001` is a typo, not a goal, and
unchecked it would pass as positive and then store as zero.

`step` is the whole point of the quick-add buttons: "6000 steps" wants a step of
1000, "3 glasses of water" wants 1. One tap, one step.

**A day with nothing on it has no row.** Writing a value of `0` deletes the
entry instead of storing a zero, so the grid only ever has to ask "is there an
entry?" — and a year of untouched days costs nothing.

`color` has to be one of `views.COLORS`; the model validator only checks that it
is six-digit hex, the view is what pins it to the palette. Both ends read the
same list, which the page ships as the `colors` prop.

## Streaks

`views.streaks_for()` counts runs of goal-met days, **over all time and not over
the year on screen** — a streak that started in December does not stop counting
because January is being looked at, which is exactly what a frontend holding one
year could never get right. One query brings back only the days that actually
met their goal (`value__gte=F("habit__goal")`), so it costs one round trip for
every habit a wallet has, not one each.

The current run counts back from today, or from **yesterday while today is still
open**: a streak is not broken until a day has been missed outright, otherwise
every streak would read zero until the evening.

It rides along on `Habit.json()` via `with_streak()`, and `log` sends the
refreshed run back with the value so the flame in the header follows the tap
that fed it. `update` recomputes rather than carrying the old number over —
moving the goal changes which days ever met it.

In the header a running streak burns (`animate-flame`), and when it *is* the
longest there has ever been the trophy sparkles with it (`animate-sparkle`).
Both stand still under `prefers-reduced-motion`, and their periods are
deliberately unequal so nothing on the page falls into step. Each figure carries
a `UiTooltip` saying what it counts.

## Painting the squares

The frontend, not the server, decides how full a square is: `levelOf(value,
goal)` in `composables/habits.ts` returns 0–5, and `levelColor()` mixes the
habit's own colour down to match. Level 5 means the goal was met — the server
never sends a level, so changing the scale is a one-file change.

## Routes

| Route                                 | Notes                                                      |
| ------------------------------------- | ---------------------------------------------------------- |
| `GET /habits/`                        | Current year                                               |
| `GET /habits/<year>/`                 | Clamped to `views.year_bounds()`, never a 404              |
| `GET /habits/api/year/<year>/`        | `{year, entries}` — switching years without a page reload  |
| `POST /habits/api/habit/`             | Create. Capped at `MAX_HABITS_PER_WALLET`                  |
| `POST /habits/api/habit/<id>/`        | Edit; every field optional                                 |
| `POST /habits/api/habit/<id>/delete/` | Takes the entries with it                                  |
| `POST /habits/api/habit/<id>/log/`    | `{date, value}` for one day; answers with the fresh streak |

Every JSON endpoint is behind `wallet_api_required` (403, not a redirect), and
each one looks the habit up **through the wallet** — `habit_of(wallet, id)` —
so a foreign id is a 404 rather than someone else's history.

`log` takes an **absolute** value, never a delta: the quick-add buttons already
know the current number, and a retried request must not count twice.

## Frontend

`HabitTrackerPage.vue` holds all the state; the components are dumb.

- `HabitsQuickRow.vue` — today's row per habit, two abreast from `xl` up. The
  fast path: `+step` / `−step`.
- `HabitsYearGrid.vue` — the 53 columns, Monday at the top. Resting on a square
  floats `UiTooltip` over it, after the same 700 ms dwell r/place uses, so
  sweeping across a year stays quiet.
- `HabitsDayModal.vue` — any day, opened by clicking its square.
- `HabitsHabitModal.vue` — create, edit, archive, delete.

Entries live in one reactive `{habit id: {date: value}}` map, and `setValue()`
paints before it saves, rolling back on an error. Tapping `+1000` six times in a
row must not wait for six round trips.

Every panel folds away, the same `UiCollapse`-in-a-`no-body`-card pattern the
games page uses. The header keeps the numbers worth seeing while it is folded —
days reached and the longest run — so a page of habits still reads at a glance.

Cards sit two abreast from `xl` up. The columns are **two stacked flex columns,
not a two-column grid**: a grid makes every row as tall as its tallest card, so
folding one away would leave a hole rather than pulling the card below it up.
That is why the page needs `useMediaQuery` — the breakpoint decides which column
a card goes in, and no CSS class can tell the template that.

The scroller around the year is `overflow-x-auto overflow-y-hidden` with a
padding ring, and both halves matter: naming one axis `auto` promotes the other
from `visible` to `auto`, so a square swelling under the pointer, or a weekday
label in a row shorter than its own text, would otherwise raise a vertical
scrollbar. The padding is what those overhangs live in.

The weekday column is a second grid that has to divide exactly the same height
as the squares. It carries `h-0 min-h-0 grow` for that reason: seven lines of
text are taller than seven small squares, and a flex item is never shrunk below
its content unless told to — so without it the labels would set the row height,
spread over a slightly larger pitch, and drift further from their rows with
every one.

The grid **has no fixed square size**. Its columns are `1fr` and its cells are
`aspect-square`, so a year fills whatever width the card gives it — that is what
lets two of them sit side by side. It is capped at 860px so a full-width card
does not blow the squares up, and floored at 420px, below which it scrolls
rather than shrinking into a smudge.

## Things that will bite you

- A value of `0` is a delete, not an update — do not expect a row per day.
- The entry map is keyed by the habit id **as a string**; JSON has no int keys.
- Numbers are decimals. Do arithmetic through `roundValue()`, or `+0.5` twice on
  a 0.1 step puts `0.30000000000000004` on the screen. The goal, step and value
  fields are `type="text"` with `inputmode="decimal"`, because a `number` field
  silently swallows the comma a German keyboard types.
- `entries_for()` loads a whole year in one query on purpose. Keep it that way,
  a query per habit is what it is avoiding.
- Archiving only hides a habit from the quick-add list; its grid stays.
- **Days reached is per displayed year, streaks are all-time.** They sit next to
  each other in the header on purpose — one belongs to the grid below it, the
  other to today. Do not "fix" this by counting streaks in the frontend.
- `UiTooltip` has two modes. Wrapping a trigger is the normal one; the grid uses
  the anchored one and drives a single pill from square to square, because
  wrapping 365 cells would be hundreds of components per habit.
- The chevron's hit area covers the **whole** header (`after:inset-0`), so
  anything in there that needs a hover or a click of its own has to be lifted
  above it with `relative z-2` — the gear and the figures both are. The cost is
  that clicking the figures no longer folds the card; clicking anywhere else in
  the header still does.
- **Only the past is tracked.** `year_bounds()` stops at the current year, and
  `log` refuses anything after today. The grid draws the days still to come as
  faint, inert squares — they have no tooltip and cannot be clicked.
