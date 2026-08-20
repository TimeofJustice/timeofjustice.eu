<script setup lang="ts">
import { computed, ref } from "vue";
import { useMediaQuery } from "@composables/mediaQuery";
import HabitsPanel from "@components/HabitsPanel.vue";
import type { Habit, HabitEntries } from "@/types/Habit.ts";

interface HabitsBoardProps {
  /** In the order they are laid out; `wide` decides who gets a whole row. */
  habits: Habit[];
  entries: HabitEntries;
  year: number;
  today: string;
  loading?: boolean;
  /** Which panels are unfolded, keyed by habit id. */
  expanded: Record<number, boolean>;
}

const {
  habits,
  entries,
  year,
  today,
  loading = false,
  expanded,
} = defineProps<HabitsBoardProps>();

const emit = defineEmits<{
  edit: [habit: Habit];
  select: [habit: Habit, date: string];
  toggle: [id: number, open: boolean];
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
const target = ref<{
  zone: string;
  before: number | null;
  wide: boolean;
} | null>(null);

const valuesOf = (habit: Habit) => entries[String(habit.id)] ?? {};

const start = (event: DragEvent, habit: Habit) => {
  // Firefox abandons a drag whose `dragstart` set no data at all, so this is
  // not optional even though nothing ever reads it back.
  event.dataTransfer?.setData("text/plain", String(habit.id));

  if (event.dataTransfer) event.dataTransfer.effectAllowed = "move";

  dragged.value = habit;
};

const stop = () => {
  dragged.value = null;
  target.value = null;
};

const aim = (
  event: DragEvent,
  zone: string,
  before: number | null,
  wide: boolean,
) => {
  if (!dragged.value) return;

  if (event.dataTransfer) event.dataTransfer.dropEffect = "move";

  target.value = { zone, before, wide };
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

const drop = () => {
  const moving = dragged.value;
  const landing = target.value;

  stop();

  if (!moving || !landing) return;

  const rest = habits.filter((habit) => habit.id !== moving.id);
  const at =
    landing.before === null
      ? rest.length
      : rest.findIndex((habit) => habit.id === landing.before);

  const arranged = [...rest];

  arranged.splice(at === -1 ? rest.length : at, 0, {
    ...moving,
    wide: landing.wide,
  });

  // Nothing moved: not worth a request.
  const unchanged =
    arranged.length === habits.length &&
    arranged.every(
      (habit, index) =>
        habit.id === habits[index].id && habit.wide === habits[index].wide,
    );

  if (!unchanged) emit("arrange", arranged);
};

/**
 * Zones are in the page at all times and only *light up* while dragging, rather
 * than being created when a drag begins.
 *
 * Two reasons. They are laid over the gaps instead of sitting in them, so the
 * board does not jump the instant a panel is picked up — which used to move
 * every target out from under the pointer. And a drop target that appears
 * mid-gesture is exactly the kind of thing a browser is entitled to ignore.
 */
const ZONE = "absolute z-10 transition-all duration-150";
const SLEEPING = "pointer-events-none opacity-0";
</script>

<template>
  <div class="flex flex-col gap-4">
    <div
      v-for="(row, index) in rows"
      :key="index"
      class="relative flex flex-col gap-4 xl:flex-row xl:items-start"
    >
      <!-- Straddling the gap above the row: the panel arrives as a row of its
           own. The label earns its space — a bare bar would leave the reader
           guessing which of the two things a drop here means. -->
      <div
        :class="[
          ZONE,
          'inset-x-0 -top-5 flex h-8 items-center justify-center rounded-surface border border-dashed text-sm',
          dragged ? 'opacity-100' : SLEEPING,
          isAimed(`row-${index}`)
            ? 'border-success bg-success/20 text-success'
            : 'border-hairline bg-surface text-accent',
        ]"
        @dragover.prevent.stop="aim($event, `row-${index}`, row[0].id, ownRow)"
        @drop.prevent.stop="drop"
      >
        {{ $t("habits.drop.own_row") }}
      </div>

      <div
        v-for="(habit, position) in row"
        :key="habit.id"
        class="relative min-w-0 flex-1"
      >
        <!-- Down the left edge of every panel: the dragged one takes a place in
             this row and shares its width. This is the way back from a whole
             row to half of one, which is why it stands beside every panel and
             not only between two. -->
        <div
          :class="[
            ZONE,
            'top-0 -left-3 hidden w-6 rounded-full xl:block',
            'h-full',
            dragged ? 'opacity-100' : SLEEPING,
            isAimed(`share-${habit.id}`) ? 'bg-success' : 'bg-light/15',
          ]"
          :title="$t('habits.drop.share_row')"
          @dragover.prevent.stop="
            aim($event, `share-${habit.id}`, habit.id, false)
          "
          @drop.prevent.stop="drop"
        />

        <!-- And down the right edge of the last one, so a row can be joined
             from that side too. -->
        <div
          v-if="position === row.length - 1"
          :class="[
            ZONE,
            'top-0 -right-3 hidden h-full w-6 rounded-full xl:block',
            dragged ? 'opacity-100' : SLEEPING,
            isAimed(`end-${index}`) ? 'bg-success' : 'bg-light/15',
          ]"
          :title="$t('habits.drop.share_row')"
          @dragover.prevent.stop="
            aim($event, `end-${index}`, after(habit), false)
          "
          @drop.prevent.stop="drop"
        />

        <HabitsPanel
          :habit="habit"
          :year="year"
          :values="valuesOf(habit)"
          :today="today"
          :loading="loading"
          :expanded="expanded[habit.id] ?? true"
          :class="dragged?.id === habit.id && 'opacity-40'"
          @update:expanded="emit('toggle', habit.id, $event)"
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
      <div
        v-if="index === rows.length - 1"
        :class="[
          ZONE,
          'inset-x-0 -bottom-5 flex h-8 items-center justify-center rounded-surface border border-dashed text-sm',
          dragged ? 'opacity-100' : SLEEPING,
          isAimed('row-last')
            ? 'border-success bg-success/20 text-success'
            : 'border-hairline bg-surface text-accent',
        ]"
        @dragover.prevent.stop="aim($event, 'row-last', null, ownRow)"
        @drop.prevent.stop="drop"
      >
        {{ $t("habits.drop.own_row") }}
      </div>
    </div>
  </div>
</template>
