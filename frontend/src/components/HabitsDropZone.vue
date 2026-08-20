<script setup lang="ts">
import { computed } from "vue";

interface HabitsDropZoneProps {
  /** A lane across the board, or a seam down the side of a panel. */
  orientation: "row" | "seam";
  /** A drag is under way. Zones are only worth showing while one is. */
  active: boolean;
  /** The pointer is over this zone. */
  aimed?: boolean;
  /** Dropping here would leave the board exactly as it stands. */
  unchanged?: boolean;
  /** Only offered from `xl` up, where a row can hold two panels. */
  wideOnly?: boolean;
  /** The dragged habit's colour. The preview is drawn in it. */
  color: string;
  /** The row this drop would make, and which half the panel would take. */
  layout: "full" | "left" | "right";
  label: string;
}

const {
  orientation,
  active,
  aimed = false,
  unchanged = false,
  wideOnly = false,
  color,
  layout,
  label,
} = defineProps<HabitsDropZoneProps>();

const emit = defineEmits<{ aim: []; drop: [] }>();

/**
 * The cursor says "move", not "copy". Firefox in particular shows the copy
 * badge for the whole gesture unless every `dragover` says otherwise.
 */
const over = (event: DragEvent) => {
  if (event.dataTransfer) event.dataTransfer.dropEffect = "move";

  emit("aim");
};

/** Lit only when a drop here would actually move something. */
const lit = computed(() => aimed && !unchanged);

/**
 * Asleep until a drag starts, and half-lit for a zone that leads nowhere — the
 * board says which targets are real before the pointer ever reaches them.
 */
const shade = computed(() => {
  if (!active) return "pointer-events-none opacity-0";

  return unchanged ? "opacity-40" : "opacity-100";
});

/**
 * The rail: a hairline lying in the gap the panel would drop into, which swells
 * and takes the habit's colour once the drop would land there.
 *
 * A lane and a seam are the same object turned ninety degrees, and drawing them
 * that way is what makes the board legible. The rail's own shape says which of
 * the two a drop means — one runs the width of the board, the other stands
 * between two panels — so neither needs a caption to be told apart.
 */
const rail = computed(() =>
  orientation === "row"
    ? ["w-full", lit.value ? "h-2.5" : "h-1.5"]
    : ["h-full", lit.value ? "w-2.5" : "w-1.5"],
);

/**
 * The row the drop would produce, drawn as bars: the dragged panel in its own
 * colour, and whatever it ends up sharing the row with beside it in grey.
 *
 * "Share this row" is a sentence about a layout; two bars are the layout.
 */
const bars = computed(() => {
  if (layout === "full") return [true];

  return layout === "left" ? [true, false] : [false, true];
});
</script>

<template>
  <div
    :class="[
      'absolute z-10 items-center justify-center transition-opacity duration-200',
      wideOnly ? 'hidden xl:flex' : 'flex',
      shade,
      orientation === 'row' ? 'h-10 -translate-y-1/2' : 'w-8',
    ]"
    @dragenter.prevent.stop="over"
    @dragover.prevent.stop="over"
    @drop.prevent.stop="emit('drop')"
  >
    <span
      class="pointer-events-none rounded-full transition-all duration-200 ease-out"
      :class="[rail, !lit && 'bg-light/15']"
      :style="
        lit
          ? { backgroundColor: color, boxShadow: `0 0 14px ${color}` }
          : undefined
      "
    />

    <!-- What the board would look like afterwards, and what to call it. Floated
         over the rail rather than set into it: the rail has to stay a hairline
         to read as a gap, and neither a lane nor a seam is thick enough to
         carry a word. -->
    <div
      v-if="aimed"
      class="pointer-events-none absolute top-1/2 left-1/2 flex w-max -translate-x-1/2 -translate-y-1/2 items-center gap-2 rounded-surface border bg-surface px-2 py-1 text-sm shadow-overlay"
      :class="!lit && 'border-hairline text-accent'"
      :style="lit ? { color, borderColor: color } : undefined"
    >
      <span class="flex h-2.5 w-12 gap-1">
        <span
          v-for="(taken, bar) in bars"
          :key="bar"
          class="flex-1 rounded-xs transition-colors"
          :class="!(taken && lit) && 'bg-light/25'"
          :style="taken && lit ? { backgroundColor: color } : undefined"
        />
      </span>

      <span>{{ unchanged ? $t("habits.drop.unchanged") : label }}</span>
    </div>
  </div>
</template>
