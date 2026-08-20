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
/** Where the panel would land: the habit it goes before, and at what width. */
const target = ref<{ id: number | null; wide: boolean } | null>(null);

const valuesOf = (habit: Habit) => entries[String(habit.id)] ?? {};

const start = (habit: Habit) => {
  dragged.value = habit;
};

const stop = () => {
  dragged.value = null;
  target.value = null;
};

/**
 * Marks where a drop would put the panel.
 *
 * Which half of the panel the pointer is over decides before or after — along
 * the axis the panels actually lie on. Two sharing a row are side by side, so
 * there it is left and right; a panel that owns its row is above and below the
 * next one, so there it is top and bottom. Reading the wrong axis is what makes
 * a drop feel arbitrary.
 */
const over = (event: DragEvent, habit: Habit, alongside: boolean) => {
  if (!dragged.value || dragged.value.id === habit.id) return;

  event.preventDefault();

  const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
  const after = alongside
    ? event.clientX > box.left + box.width / 2
    : event.clientY > box.top + box.height / 2;

  const index = habits.findIndex((entry) => entry.id === habit.id);
  const next = habits[index + 1];

  target.value = {
    id: after ? (next?.id ?? null) : habit.id,
    wide: dragged.value.wide,
  };
};

/**
 * The seam between two panels of a row: landing there means "take the whole
 * row". It is the only gesture on the board that changes a panel's width rather
 * than its place.
 */
const overSeam = (event: DragEvent, habit: Habit) => {
  if (!dragged.value || dragged.value.id === habit.id) return;

  event.preventDefault();

  target.value = { id: habit.id, wide: true };
};

const drop = () => {
  const moving = dragged.value;
  const landing = target.value;

  stop();

  if (!moving || !landing) return;

  const rest = habits.filter((habit) => habit.id !== moving.id);
  const at =
    landing.id === null
      ? rest.length
      : rest.findIndex((habit) => habit.id === landing.id);

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

const isTarget = (habit: Habit, wide: boolean) =>
  target.value?.id === habit.id && target.value.wide === wide;
</script>

<template>
  <div class="flex flex-col gap-4">
    <div
      v-for="(row, index) in rows"
      :key="index"
      class="flex flex-col gap-4 xl:flex-row xl:items-start"
    >
      <template v-for="(habit, position) in row" :key="habit.id">
        <!-- The seam between two panels of a row. It only takes a drop while
             something is being dragged, and what it means is "stretch across
             the whole row" — hence the tall bar rather than a thin line. -->
        <div
          v-if="position > 0 && dragged"
          class="hidden w-2 shrink-0 self-stretch rounded-full transition-colors xl:block"
          :class="isTarget(habit, true) ? 'bg-success' : 'bg-light/15'"
          @dragover="overSeam($event, habit)"
          @drop.prevent="drop"
        />

        <div
          class="relative min-w-0 flex-1"
          @dragover="over($event, habit, row.length > 1)"
          @drop.prevent="drop"
        >
          <!-- Where the panel would land, drawn on the edge it would arrive at
               and along the axis its row runs on. Laid over the panel rather
               than pushed between them, so a row does not reflow while the
               pointer is still moving. -->
          <div
            v-if="isTarget(habit, false)"
            class="pointer-events-none absolute rounded-full bg-success"
            :class="
              row.length > 1
                ? 'top-0 bottom-0 -left-2 w-1'
                : '-top-2 right-0 left-0 h-1'
            "
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
              <!-- Only the grip drags. The panel itself has a chart and a year
                   of squares in it, both of which want their own pointer. -->
              <UiButton
                variant="tertiary"
                square
                size="sm"
                class="relative z-2 cursor-grab active:cursor-grabbing"
                draggable="true"
                :title="$t('habits.drag')"
                @dragstart="start(habit)"
                @dragend="stop"
              >
                <iconify-icon icon="fa6-solid:grip-vertical" />
              </UiButton>
            </template>
          </HabitsPanel>
        </div>
      </template>
    </div>

    <!-- Somewhere to drop a panel that belongs at the very end. -->
    <div
      v-if="dragged"
      class="h-8 rounded-surface border border-dashed transition-colors"
      :class="target?.id === null ? 'border-success' : 'border-hairline'"
      @dragover.prevent="target = { id: null, wide: dragged.wide }"
      @drop.prevent="drop"
    />
  </div>
</template>
