# Momentum

Keeping something going, and watching something move. It belongs to a
[wallet](../games/wallet.md) — there is still no user model — and it lives at
`/momentum/`.

**The app is `habits`, the product is "Momentum".** The same split `postcard`
has, which is served as "Sendy": the brand is in the route and the UI, the
module and the tables keep the name the data was written under. Renaming the app
would buy nothing and cost a table migration.

## The two models

| Model   | What it is                                                                                     |
| ------- | ---------------------------------------------------------------------------------------------- |
| `Habit` | Name, `goal`, `unit`, `color`, `step`, `kind`, and its place on the board. Owned by a wallet, `CASCADE` on delete. |
| `Entry` | One `value` on one `date` for one habit. Unique per `(habit, date)`.                            |

## The two kinds

One model, two things, because they differ only in how they are read:

| `kind`    | What it is                                | Drawn as        | `goal` means | Streaks |
| --------- | ----------------------------------------- | --------------- | ------------ | ------- |
| `goal`    | A daily target, met or missed. "6000 steps." | A year of squares | The bar to clear | Yes |
| `measure` | A reading tracked *against* a target. "75 kg." | A line          | The target itself | Yes |

Everything else — logging, the day editor, the quick-add, the year API, the
wallet gating — is shared, which is the whole reason they are not two models.

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

## The board

`order` and `wide` are the arrangement: the running order of the panels, and
which of them take a whole row instead of sharing one. `HabitsBoard.vue` cuts
the ordered list into rows — a `wide` habit takes one to itself, the rest pair
up — and below `xl` the flag makes no difference, since only one panel fits a
row anyway.

Panels are dragged by the **grip in the header, never by the panel**: a panel
has a chart and a year of squares in it, and both want the pointer for
themselves. Where a drop lands is read along the axis the row actually runs on —
left/right for two sharing a row, top/bottom for one that owns it. Reading the
wrong axis is what makes a drop feel arbitrary.

Between two panels of a row there is a **seam**, which appears only while
something is being dragged. Landing on it is the one gesture that changes a
panel's *width* rather than its place: it stretches across the whole row.

`POST /momentum/api/layout/` takes the **whole arrangement**, not a move to
apply — dragging produces the finished order anyway, and sending it whole means
a dropped request cannot leave the board in a state nobody arranged. A forged id
returns 404 before anything is written, so it rearranges nothing.

## Streaks

`views.streaks_for()` counts runs of goal-met days, **over all time and not over
the year on screen** — a streak that started in December does not stop counting
because January is being looked at, which is exactly what a frontend holding one
year could never get right. One query brings back only the days that actually
met their goal (`value__gte=F("habit__goal")`), so it costs one round trip for
every habit a wallet has, not one each.

For a `goal`, the current run counts back from today, or from **yesterday while
today is still open**: a streak is not broken until a day has been missed
outright, otherwise every streak would read zero until the evening.

For a `measure`, `approach_streak()` counts the readings that did not move away
from the target — closing on it, or holding. Three things about it are choices
worth knowing:

- It counts **readings, not days**. A weight is not taken daily, and a fortnight
  without a weigh-in is no news rather than a broken run.
- **Holding counts.** Not sliding back is its own kind of progress.
- It counts the *steps between* readings, so one reading alone is a run of
  nothing, and **overshooting ends a run**: with a target of 75, going 75 → 74
  moves away from it. The measure is distance to the target, not "past it".

It rides along on `Habit.json()` via `with_streak()`, and `log` sends the
refreshed run back with the value so the flame in the header follows the tap
that fed it. `update` recomputes rather than carrying the old number over —
moving the goal changes which days ever met it.

In the header both kinds carry the same two figures — a burning run and the best
one there has ever been — and only the wording under them differs. A running
streak burns (`animate-flame`), and when it *is* the longest there has ever been
the trophy sparkles with it (`animate-sparkle`).
Both stand still under `prefers-reduced-motion`, and their periods are
deliberately unequal so nothing on the page falls into step. Each figure carries
a `UiTooltip` saying what it counts.

## Drawing a progression

`HabitsTrendChart.vue` — one series, so no legend box: the card header already
names it. Straight segments between readings (interpolation is the only honest
curve for days nobody measured), no per-point markers at 365 points, a hairline
grid one shade off the surface, and hover snapping to the **nearest reading**
rather than to the day under the pointer — sparse data means most days have
nothing to say.

The target is drawn as a *threshold*, not a second series: a dashed muted rule
labelled on the canvas, by a small inline plugin. **It is always inside the y
window**, however far the readings are from it — a measurement is kept in order
to watch it approach its target, and a chart that cropped the target away would
hide the one relationship the card exists for. The headline figure is what the year
*moved*, and it is the one place the tracker does pass a verdict — because the
target makes one possible. `measureStats().closed` is how much of the gap was
closed, so a falling weight and a rising balance both come out green without the
tracker having to know which it is looking at. The arrow stays factual (which
way it went); only the colour judges.

**The line holds a value on every day up to today.** Between two readings it
*runs from one to the other* — a day in the middle takes its share of the way,
so two weigh-ins a fortnight apart are joined by a steady slope rather than by a
step that drops all at once on the second day. Outside that span there is no
second point to run towards, so the nearest reading is simply held: forward past
the last one, and backwards into the days before the first.

Past today it stops dead: no fill, no line, and no click. A weigh-in says
nothing about a day that has not happened, the year grid draws those days inert
for the same reason, and `log` would refuse them anyway.

What keeps that honest is that the fill never pretends to be a measurement. The
dots are the days actually weighed; the line between them is fill. Every filled
day says on hover where its number comes from — "on the way from 21 June to
21 July", "as measured on 21 July", "before the first measurement, on 21 June" —
so a slope is never mistaken for a run of daily weigh-ins. And **nothing is
stored**: this is presentation, not data.

Hit testing goes through a **custom interaction mode**, `habitDay`, registered on
`Interaction.modes`. A year is 365 days across a few hundred pixels — one day is
about a pixel and a half, so aiming at a particular one is hopeless, and the dots
are what anyone is aiming at anyway. Within 12 pixels of a day that was actually
measured, that reading wins; anywhere else the day under the pointer is taken as
it is, so an empty stretch can still be opened to fill a gap.

The crosshair, the tooltip **and the click** all resolve through that one mode,
so the day that is highlighted and the day that opens can never disagree. That
was the real complaint behind "hard to hit": a click reading the raw pixel while
the highlight read the nearest point could land a day off.

The day editor carries a date field as the exact fallback (on a line there is no
square to aim at), and on an empty day it offers `carriedValue()` as a starting
point, so correcting a gap means nudging a real number instead of typing one
from nothing.

Its height comes from `gridHeight()`, measured against its own width with a
`ResizeObserver`. A ratio cannot express it: the grid's height grows with its
width but carries a fixed month band on top, and stops growing at
`GRID.maxWidth` while the chart panel keeps going — the relationship is affine
and clamped, not proportional. Both read their numbers from `GRID` in
`composables/habits.ts`, and `HabitsYearGrid` spends them as inline style rather
than Tailwind classes for exactly that reason: a hard-coded `gap-[2px]` in that
template is how the two would drift apart.

chart.js is pulled in with `defineAsyncComponent`, so a page of nothing but
daily goals never fetches its 50 kB.

## Painting the squares

The frontend, not the server, decides how full a square is: `levelOf(value,
goal)` in `composables/habits.ts` returns 0–5, and `levelColor()` mixes the
habit's own colour down to match. Level 5 means the goal was met — the server
never sends a level, so changing the scale is a one-file change.

## Routes

| Route                                   | Notes                                                      |
| --------------------------------------- | ---------------------------------------------------------- |
| `GET /momentum/`                        | Current year                                               |
| `GET /momentum/<year>/`                 | Clamped to `views.year_bounds()`, never a 404              |
| `GET /momentum/api/year/<year>/`        | `{year, entries}` — switching years without a page reload  |
| `POST /momentum/api/habit/`             | Create. Capped at `MAX_HABITS_PER_WALLET`                  |
| `POST /momentum/api/layout/`            | `{habits: [{id, wide}]}` — the arrangement, in full        |
| `POST /momentum/api/habit/<id>/`        | Edit; every field optional                                 |
| `POST /momentum/api/habit/<id>/delete/` | Takes the entries with it                                  |
| `POST /momentum/api/habit/<id>/log/`    | `{date, value}` for one day; answers with the fresh streak |

Every JSON endpoint is behind `wallet_api_required` (403, not a redirect), and
each one looks the habit up **through the wallet** — `habit_of(wallet, id)` —
so a foreign id is a 404 rather than someone else's history.

`log` takes an **absolute** value, never a delta: the quick-add buttons already
know the current number, and a retried request must not count twice.

## Frontend

`HabitTrackerPage.vue` holds all the state; the components are dumb.

- `HabitsBoard.vue` — the rows, and the dragging that rearranges them.
- `HabitsPanel.vue` — one habit's card: the figures, the fold, the grid or line.
- `HabitsQuickRow.vue` — today's row per habit, two abreast from `xl` up. The
  fast path: `+step` / `−step`.
- `HabitsYearGrid.vue` — the 53 columns, Monday at the top. Resting on a square
  floats `UiTooltip` over it, after the same 700 ms dwell r/place uses, so
  sweeping across a year stays quiet.
- `HabitsTrendChart.vue` — the line, for `measure`. Lazily loaded.
- `HabitsDayModal.vue` — any day, opened by clicking its square or its reading.
- `HabitsHabitModal.vue` — create, edit, archive, delete.

Entries live in one reactive `{habit id: {date: value}}` map, and `setValue()`
paints before it saves, rolling back on an error. Tapping `+1000` six times in a
row must not wait for six round trips.

Every panel folds away, the same `UiCollapse`-in-a-`no-body`-card pattern the
games page uses. The header keeps the numbers worth seeing while it is folded —
days reached and the longest run — so a page of habits still reads at a glance.

Cards sit two abreast from `xl` up, in explicit rows — which is what makes
"stretch across the row" expressible at all. The board still needs
`useMediaQuery`, because the breakpoint decides how the rows are cut and no CSS
class can tell the template that.

The scroller around the year is `overflow-x-auto overflow-y-hidden` with a
padding ring, and both halves matter: naming one axis `auto` promotes the other
from `visible` to `auto`, so a square swelling under the pointer, or a weekday
label in a row shorter than its own text, would otherwise raise a vertical
scrollbar. The padding is what those overhangs live in.

Each square's **hit area is larger than the square**, through an `after` that
reaches a pixel past the gap on every side. Nine pixels with a two-pixel gap
either side left dead ground between the days: the pointer would sit in a gap,
the neighbouring square would still show as hovered, and the click would land on
nothing. Where two hit areas overlap the later square wins, which is consistent,
and `GRID.padding` is exactly deep enough to hold the outermost ones.

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
- A carried value on the line is never a stored one. If you ever find yourself
  writing the fill back to `Entry`, stop: the whole point is that only real
  weigh-ins are data.
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
