<script setup lang="ts">
import { computed } from "vue";

interface HabitsDropZoneProps {
  /** A lane across the board, or a seam down the side of a panel. */
  orientation: "row" | "seam";
  /** A drag is under way; zones are invisible otherwise. */
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

// Firefox shows the copy badge for the whole gesture unless every `dragover`
// says otherwise.
const over = (event: DragEvent) => {
  if (event.dataTransfer) event.dataTransfer.dropEffect = "move";

  emit("aim");
};

/** Lit only when a drop here would actually move something. */
const lit = computed(() => aimed && !unchanged);

/** Asleep until a drag starts, half-lit for a zone that leads nowhere. */
const shade = computed(() => {
  if (!active) return "pointer-events-none opacity-0";

  return unchanged ? "opacity-40" : "opacity-100";
});

/**
 * A hairline in the gap the panel would drop into. A lane and a seam are the same
 * rail turned ninety degrees, and that shape is the caption: one runs the width
 * of the board, the other stands between two panels.
 */
const rail = computed(() =>
  orientation === "row"
    ? ["w-full", lit.value ? "h-2.5" : "h-1.5"]
    : ["h-full", lit.value ? "w-2.5" : "w-1.5"],
);

/** The resulting row as bars: the dragged panel coloured, its neighbour grey. */
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

    <!-- Floated over the rail, which stays a hairline and cannot carry a word. -->
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
