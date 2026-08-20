<script setup lang="ts">
import { computed, ref } from "vue";
import { useMediaQuery } from "@composables/mediaQuery";
import HabitsPanel from "@components/HabitsPanel.vue";
import HabitsDropZone from "@components/HabitsDropZone.vue";
import type { Habit, HabitEntries } from "@/types/Habit.ts";

interface HabitsBoardProps {
  /** In the order they are laid out; `wide` decides who gets a whole row. */
  habits: Habit[];
  entries: HabitEntries;
  year: number;
  today: string;
  loading?: boolean;
}

const {
  habits,
  entries,
  year,
  today,
  loading = false,
} = defineProps<HabitsBoardProps>();

const emit = defineEmits<{
  edit: [habit: Habit];
  select: [habit: Habit, date: string];
  /** The finished arrangement, ready to be saved. */
  arrange: [habits: Habit[]];
}>();

/** The `xl` breakpoint, where two panels can share a row. */
const isWide = useMediaQuery("(min-width: 1200px)");

/**
 * The board, cut into rows.
 *
 * A `wide` habit takes a row to itself; the rest pair up. Below `xl` there is
 * only ever one panel to a row, so the flag makes no difference there.
 */
const rows = computed(() => {
  if (!isWide.value) return habits.map((habit) => [habit]);

  const laid: Habit[][] = [];
  let row: Habit[] = [];

  for (const habit of habits) {
    if (habit.wide) {
      if (row.length > 0) laid.push(row);

      laid.push([habit]);
      row = [];
      continue;
    }

    row.push(habit);

    if (row.length === 2) {
      laid.push(row);
      row = [];
    }
  }

  if (row.length > 0) laid.push(row);

  return laid;
});

const dragged = ref<Habit | null>(null);

/**
 * Where a drop would put the panel: the habit it lands in front of — `null` for
 * the very end — and how it will sit there.
 *
 * Every zone names both outright instead of it being worked out from which half
 * of a panel the pointer happens to be over. That is what makes the board
 * readable while dragging: each zone means one thing, and it is the thing it
 * looks like. It is also what gives a wide panel its way back to half a row,
 * which a gesture that preserved the width could never do.
 */
interface Landing {
  zone: string;
  before: number | null;
  wide: boolean;
  /** The panel the drop would come to rest beside, if any. */
  partner: number | null;
}

const target = ref<Landing | null>(null);

const valuesOf = (habit: Habit) => entries[String(habit.id)] ?? {};

/**
 * What follows the cursor: a chip naming the habit, rather than the browser's
 * snapshot of the grip — which is a picture of a grip, and says nothing about
 * what is being carried.
 *
 * Built by hand rather than rendered by Vue, because `setDragImage` only counts
 * during `dragstart` itself and a node Vue is asked for there does not exist
 * until the tick after. The browser photographs it once and never looks again,
 * so it waits off-screen and is cleared up on the next frame.
 */
const chipFor = (habit: Habit) => {
  const chip = document.createElement("div");

  chip.textContent = habit.name;
  chip.style.cssText = `
    position: fixed; top: -1000px; left: -1000px;
    padding: 0.35rem 0.85rem 0.35rem 1.85rem;
    border: 1px solid ${habit.color};
    border-radius: 9999px;
    background: var(--color-surface);
    color: var(--color-light);
    font: 500 0.875rem/1.3 Inter, sans-serif;
    white-space: nowrap;
    box-shadow: var(--shadow-overlay);
  `;

  const dot = document.createElement("span");

  dot.style.cssText = `
    position: absolute; left: 0.7rem; top: 50%;
    width: 0.7rem; height: 0.7rem; margin-top: -0.35rem;
    border-radius: 9999px; background: ${habit.color};
  `;

  chip.append(dot);
  document.body.append(chip);

  return chip;
};

const start = (event: DragEvent, habit: Habit) => {
  // Firefox abandons a drag whose `dragstart` set no data at all, so this is
  // not optional even though nothing ever reads it back.
  event.dataTransfer?.setData("text/plain", String(habit.id));

  if (event.dataTransfer) {
    const chip = chipFor(habit);

    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setDragImage(chip, 24, 18);

    requestAnimationFrame(() => chip.remove());
  }

  dragged.value = habit;
};

const stop = () => {
  dragged.value = null;
  target.value = null;
};

const aim = (
  zone: string,
  before: number | null,
  wide: boolean,
  partner: number | null,
) => {
  if (!dragged.value) return;

  target.value = { zone, before, wide, partner };
};

const isAimed = (zone: string) => target.value?.zone === zone;

/** The habit that follows this one in the running order, for a trailing zone. */
const after = (habit: Habit) => {
  const index = habits.findIndex((entry) => entry.id === habit.id);

  return habits[index + 1]?.id ?? null;
};

/**
 * Below `xl` a panel owns its row whatever the flag says, so there is nothing
 * to choose there and the width it already has is left alone.
 */
const ownRow = computed(() =>
  isWide.value ? true : (dragged.value?.wide ?? false),
);

/** The board as it would stand if the drag ended on this zone. */
const arrangeWith = (before: number | null, wide: boolean) => {
  const moving = dragged.value;

  if (!moving) return habits;

  // The panel is its own anchor for the zones that sit against it — its own
  // lane, its own left seam. Once it is lifted out it can no longer be found
  // there, so the slot it was holding is named by whatever came next instead.
  // Without this the search fails and the panel is swept to the end of the
  // board, which is the one place the reader was not pointing at.
  const anchor = before === moving.id ? after(moving) : before;

  const rest = habits.filter((habit) => habit.id !== moving.id);
  const at =
    anchor === null
      ? rest.length
      : rest.findIndex((habit) => habit.id === anchor);

  const arranged = [...rest];

  arranged.splice(at === -1 ? rest.length : at, 0, { ...moving, wide });

  return arranged;
};

/** Whether an arrangement is the one already on screen. */
const settled = (arranged: Habit[]) =>
  arranged.every(
    (habit, index) =>
      habit.id === habits[index].id && habit.wide === habits[index].wide,
  );

/**
 * A zone that would put the panel back exactly where it already is.
 *
 * Every panel carries zones on both sides, so a few of them always lead
 * nowhere. Saying so up front — half-lit, and never lighting up — is what stops
 * the board offering a dozen targets when only some of them mean anything.
 */
const isUnchanged = (before: number | null, wide: boolean) =>
  settled(arrangeWith(before, wide));

const drop = () => {
  const landing = target.value;

  // Worked out while the drag is still standing: `arrangeWith` needs to know
  // what is being carried, and `stop` is what puts it down.
  const arranged =
    dragged.value && landing
      ? arrangeWith(landing.before, landing.wide)
      : habits;

  stop();

  // Nothing moved: not worth a request.
  if (!settled(arranged)) emit("arrange", arranged);
};

/**
 * The panel a drop would come to rest beside, outlined in the dragged habit's
 * colour while that seam is aimed at — so "share this row" points at the row it
 * means instead of leaving the reader to work out which two panels pair up.
 */
const partnerStyle = (habit: Habit) => {
  if (target.value?.partner !== habit.id || !dragged.value) return undefined;

  return {
    outline: `2px dashed ${dragged.value.color}`,
    outlineOffset: "4px",
  };
};
</script>

<template>
  <!-- A drag across a board of year grids selects text everywhere it passes,
       and the selection then hangs about after the drop. Nothing here is worth
       selecting mid-gesture. -->
  <div class="flex flex-col gap-4" :class="dragged && 'select-none'">
    <div
      v-for="(row, index) in rows"
      :key="index"
      class="relative flex flex-col gap-4 xl:flex-row xl:items-start"
    >
      <!-- Straddling the gap above the row: the panel arrives as a row of its
           own. The label earns its space — a bare bar would leave the reader
           guessing which of the two things a drop here means. -->
      <HabitsDropZone
        class="inset-x-0 top-0 -mt-2"
        orientation="row"
        layout="full"
        :active="!!dragged"
        :aimed="isAimed(`row-${index}`)"
        :unchanged="isUnchanged(row[0].id, ownRow)"
        :color="dragged?.color ?? ''"
        :label="$t('habits.drop.own_row')"
        @aim="aim(`row-${index}`, row[0].id, ownRow, null)"
        @drop="drop"
      />

      <div
        v-for="(habit, position) in row"
        :key="habit.id"
        class="relative min-w-0 flex-1"
      >
        <!-- Down the left edge of every panel: the dragged one takes a place in
             this row and shares its width. This is the way back from a whole
             row to half of one, which is why it stands beside every panel and
             not only between two. -->
        <HabitsDropZone
          class="top-0 -left-4 h-full"
          orientation="seam"
          layout="left"
          wide-only
          :active="!!dragged"
          :aimed="isAimed(`share-${habit.id}`)"
          :unchanged="isUnchanged(habit.id, false)"
          :color="dragged?.color ?? ''"
          :label="$t('habits.drop.share_row')"
          @aim="aim(`share-${habit.id}`, habit.id, false, habit.id)"
          @drop="drop"
        />

        <!-- And down the right edge of the last one, so a row can be joined
             from that side too. -->
        <HabitsDropZone
          v-if="position === row.length - 1"
          class="top-0 -right-4 h-full"
          orientation="seam"
          layout="right"
          wide-only
          :active="!!dragged"
          :aimed="isAimed(`end-${index}`)"
          :unchanged="isUnchanged(after(habit), false)"
          :color="dragged?.color ?? ''"
          :label="$t('habits.drop.share_row')"
          @aim="aim(`end-${index}`, after(habit), false, habit.id)"
          @drop="drop"
        />

        <HabitsPanel
          :habit="habit"
          :year="year"
          :values="valuesOf(habit)"
          :today="today"
          :loading="loading"
          class="transition-all duration-200"
          :class="
            dragged?.id === habit.id && 'scale-[0.98] opacity-30 grayscale'
          "
          :style="partnerStyle(habit)"
          @edit="emit('edit', habit)"
          @select="emit('select', habit, $event)"
        >
          <template #handle>
            <!-- Only the grip drags: the panel has a chart and a year of squares
                 in it, and both want their own pointer.

                 The draggable element is this span and not the button inside
                 it. A `<button>` is a form control, and browsers are inconsistent
                 about letting one be dragged at all however plainly it is
                 marked; a span has no such history. The button keeps the look
                 and stays out of the way of the pointer. -->
            <span
              class="relative z-2 inline-flex cursor-grab active:cursor-grabbing"
              draggable="true"
              :title="$t('habits.drag')"
              @dragstart="start($event, habit)"
              @dragend="stop"
            >
              <UiButton
                variant="tertiary"
                square
                size="sm"
                class="pointer-events-none"
                tabindex="-1"
                aria-hidden="true"
              >
                <iconify-icon icon="fa6-solid:grip-vertical" />
              </UiButton>
            </span>
          </template>
        </HabitsPanel>
      </div>

      <!-- A row of its own at the very bottom, below the last row. -->
      <HabitsDropZone
        v-if="index === rows.length - 1"
        class="inset-x-0 top-full mt-2"
        orientation="row"
        layout="full"
        :active="!!dragged"
        :aimed="isAimed('row-last')"
        :unchanged="isUnchanged(null, ownRow)"
        :color="dragged?.color ?? ''"
        :label="$t('habits.drop.own_row')"
        @aim="aim('row-last', null, ownRow, null)"
        @drop="drop"
      />
    </div>
  </div>
</template>
