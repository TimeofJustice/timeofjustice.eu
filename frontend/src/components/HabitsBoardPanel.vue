<script setup lang="ts">
import HabitsPanel from "@components/HabitsPanel.vue";
import type { Habit } from "@/types/Habit.ts";

interface HabitsBoardPanelProps {
  habit: Habit;
  year: number;
  values: Record<string, number>;
  today: string;
  loading?: boolean;
  /** The panel being dragged, which fades out of the way. */
  dragging?: boolean;
  /** Set when a drop would come to rest beside this panel. */
  outline?: string;
}

const {
  habit,
  year,
  values,
  today,
  loading = false,
  dragging = false,
  outline,
} = defineProps<HabitsBoardPanelProps>();

const emit = defineEmits<{
  edit: [];
  select: [date: string];
  dragstart: [event: DragEvent];
  dragend: [];
}>();
</script>

<!--
  Split out of the board's `v-for` on purpose. A slot written inside one compiles
  to `DYNAMIC_SLOTS`, which has Vue re-render the panel on every render of the
  board, and a drag renders it on every pointer move. Out here the slot is stable
  and only this wrapper follows the drag.
-->
<template>
  <div
    class="transition-[transform,opacity,filter] duration-200"
    :class="dragging && 'scale-[0.98] opacity-30 grayscale'"
    :style="
      outline
        ? { outline: `2px dashed ${outline}`, outlineOffset: '4px' }
        : undefined
    "
  >
    <HabitsPanel
      :habit="habit"
      :year="year"
      :values="values"
      :today="today"
      :loading="loading"
      @edit="emit('edit')"
      @select="emit('select', $event)"
    >
      <template #handle>
        <!-- The span is draggable, not the button inside it: browsers are
             inconsistent about dragging form controls. -->
        <span
          class="relative z-2 inline-flex cursor-grab active:cursor-grabbing"
          draggable="true"
          :title="$t('habits.drag')"
          @dragstart="emit('dragstart', $event)"
          @dragend="emit('dragend')"
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
</template>
