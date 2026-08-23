<script setup lang="ts">
import { computed, ref } from "vue";
import { useMediaQuery } from "@composables/mediaQuery";
import HabitsBoardPanel from "@components/HabitsBoardPanel.vue";
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
 * The board, cut into rows. A `wide` habit takes one to itself, the rest pair up.
 * Below `xl` only one panel fits a row, so the flag makes no difference.
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

/** The zone the pointer is currently over, by key. */
const aimed = ref<string | null>(null);

/**
 * Where a drop would put the panel: the habit it lands in front of, `null` for
 * the very end, and how wide it will sit there.
 *
 * Each zone names the width outright rather than preserving the dragged panel's,
 * which is what gives a wide panel a way back to half a row.
 */
interface Landing {
  before: number | null;
  wide: boolean;
  /** The panel the drop would come to rest beside, if any. */
  partner: number | null;
}

/**
 * Shared, so a habit with nothing logged keeps the same `values` prop from one
 * render to the next. A fresh `{}` would count as a change and rebuild its grid.
 */
const NO_VALUES: Record<string, number> = Object.freeze({});

const valuesOf = (habit: Habit) => entries[String(habit.id)] ?? NO_VALUES;

/**
 * The drag image: a chip naming the habit, instead of the browser's snapshot of
 * the grip button.
 *
 * Built by hand because `setDragImage` only counts during `dragstart` itself,
 * and a node Vue is asked for there does not exist until the tick after. The
 * browser photographs it once, so it waits off-screen and goes on the next frame.
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
  // Firefox abandons a drag whose `dragstart` set no data, though nothing reads
  // it back.
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
  aimed.value = null;
};

// `dragover` fires for every pointer move, and nearly all of them land on the
// zone that is already aimed at.
const aim = (zone: string) => {
  if (!dragged.value || aimed.value === zone) return;

  aimed.value = zone;
};

/** The habit that follows each one in the running order, for the trailing zones. */
const nextIds = computed(() => {
  const map = new Map<number, number | null>();

  habits.forEach((habit, index) =>
    map.set(habit.id, habits[index + 1]?.id ?? null),
  );

  return map;
});

/** Below `xl` a panel owns its row regardless, so its width is left alone. */
const ownRow = computed(() =>
  isWide.value ? true : (dragged.value?.wide ?? false),
);

/**
 * Every zone on the board and what dropping on it would mean, under the keys the
 * template names them by.
 */
const landings = computed(() => {
  const map = new Map<string, Landing>();
  const own = ownRow.value;

  rows.value.forEach((row, index) => {
    map.set(`row-${index}`, { before: row[0].id, wide: own, partner: null });

    row.forEach((habit, position) => {
      map.set(`share-${habit.id}`, {
        before: habit.id,
        wide: false,
        partner: habit.id,
      });

      if (position === row.length - 1) {
        map.set(`end-${index}`, {
          before: nextIds.value.get(habit.id) ?? null,
          wide: false,
          partner: habit.id,
        });
      }
    });
  });

  map.set("row-last", { before: null, wide: own, partner: null });

  return map;
});

/** The board as it would stand if the drag ended on this zone. */
const arrangeWith = (before: number | null, wide: boolean) => {
  const moving = dragged.value;

  if (!moving) return habits;

  // The panel anchors the zones against it, but is filtered out of `rest` below,
  // so the lookup would fail and sweep it to the end of the board. Name the slot
  // by whatever follows instead.
  const anchor =
    before === moving.id ? (nextIds.value.get(moving.id) ?? null) : before;

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
 * The zones that would put the panel back where it already is. Every panel
 * carries zones on both sides, so several always lead nowhere; they render
 * half-lit. Only the panel being dragged decides this, never the pointer, so it
 * is settled once when the drag picks up.
 */
const unchangedZones = computed(() => {
  const idle = new Set<string>();

  if (!dragged.value) return idle;

  for (const [zone, landing] of landings.value) {
    if (settled(arrangeWith(landing.before, landing.wide))) idle.add(zone);
  }

  return idle;
});

const drop = () => {
  const landing = aimed.value ? landings.value.get(aimed.value) : undefined;

  // Before `stop()`, which is what clears `dragged` out from under `arrangeWith`.
  const arranged =
    dragged.value && landing
      ? arrangeWith(landing.before, landing.wide)
      : habits;

  stop();

  // Nothing moved: not worth a request.
  if (!settled(arranged)) emit("arrange", arranged);
};

/** The panel an aimed seam would land beside. It is outlined, to show the pairing. */
const partner = computed(() =>
  dragged.value && aimed.value
    ? (landings.value.get(aimed.value)?.partner ?? null)
    : null,
);

const partnerColor = (habit: Habit) =>
  partner.value === habit.id ? dragged.value?.color : undefined;
</script>

<template>
  <!-- Without this a drag selects text across every year grid it passes over. -->
  <div class="flex flex-col gap-4" :class="dragged && 'select-none'">
    <div
      v-for="(row, index) in rows"
      :key="index"
      class="relative flex flex-col gap-4 xl:flex-row xl:items-start"
    >
      <!-- Straddling the gap above the row: the panel arrives as a row of its own. -->
      <HabitsDropZone
        class="inset-x-0 top-0 -mt-2"
        orientation="row"
        layout="full"
        :active="!!dragged"
        :aimed="aimed === `row-${index}`"
        :unchanged="unchangedZones.has(`row-${index}`)"
        :color="dragged?.color ?? ''"
        :label="$t('habits.drop.own_row')"
        @aim="aim(`row-${index}`)"
        @drop="drop"
      />

      <div
        v-for="(habit, position) in row"
        :key="habit.id"
        class="relative min-w-0 flex-1"
      >
        <!-- Beside every panel, not only between two: this is the way back from
             a whole row to half of one. -->
        <HabitsDropZone
          class="top-0 -left-4 h-full"
          orientation="seam"
          layout="left"
          wide-only
          :active="!!dragged"
          :aimed="aimed === `share-${habit.id}`"
          :unchanged="unchangedZones.has(`share-${habit.id}`)"
          :color="dragged?.color ?? ''"
          :label="$t('habits.drop.share_row')"
          @aim="aim(`share-${habit.id}`)"
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
          :aimed="aimed === `end-${index}`"
          :unchanged="unchangedZones.has(`end-${index}`)"
          :color="dragged?.color ?? ''"
          :label="$t('habits.drop.share_row')"
          @aim="aim(`end-${index}`)"
          @drop="drop"
        />

        <HabitsBoardPanel
          :habit="habit"
          :year="year"
          :values="valuesOf(habit)"
          :today="today"
          :loading="loading"
          :dragging="dragged?.id === habit.id"
          :outline="partnerColor(habit)"
          @edit="emit('edit', habit)"
          @select="emit('select', habit, $event)"
          @dragstart="start($event, habit)"
          @dragend="stop"
        />
      </div>

      <!-- A row of its own at the very bottom, below the last row. -->
      <HabitsDropZone
        v-if="index === rows.length - 1"
        class="inset-x-0 top-full mt-2"
        orientation="row"
        layout="full"
        :active="!!dragged"
        :aimed="aimed === 'row-last'"
        :unchanged="unchangedZones.has('row-last')"
        :color="dragged?.color ?? ''"
        :label="$t('habits.drop.own_row')"
        @aim="aim('row-last')"
        @drop="drop"
      />
    </div>
  </div>
</template>
