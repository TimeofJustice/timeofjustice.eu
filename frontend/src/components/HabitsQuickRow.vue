<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { formatNumber, levelOf, roundValue } from "@composables/habits";
import type { Habit } from "@/types/Habit.ts";

interface HabitsQuickRowProps {
  habit: Habit;
  /** What is logged for the day this row stands for. */
  value: number;
}

const { habit, value } = defineProps<HabitsQuickRowProps>();

const emit = defineEmits<{ update: [value: number]; open: [] }>();

const i18n = useI18n();

const format = (number: number) => formatNumber(number, i18n.locale.value);

const percentage = computed(() =>
  habit.goal > 0 ? Math.min(100, Math.round((value / habit.goal) * 100)) : 0,
);

const reached = computed(() => levelOf(value, habit.goal) === 5);
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <div class="flex items-center gap-2">
      <span
        class="size-3 shrink-0 rounded-full"
        :style="{ backgroundColor: habit.color }"
      />

      <button
        type="button"
        class="min-w-0 grow cursor-pointer truncate text-left"
        @click="emit('open')"
      >
        {{ habit.name }}
      </button>

      <span class="shrink-0 text-sm whitespace-nowrap text-accent">
        <span :class="reached && 'text-success'">{{ format(value) }}</span>
        / {{ format(habit.goal) }} {{ habit.unit }}
      </span>
    </div>

    <div class="flex items-center gap-2">
      <UiProgress class="h-2 grow">
        <UiProgressBar
          :value="percentage"
          :variant="reached ? 'success' : undefined"
        />
      </UiProgress>

      <!-- One tap is a whole step: this is the fastest way to log a day. -->
      <UiButton
        variant="secondary"
        size="sm"
        square
        :disabled="value <= 0"
        :title="$t('habits.day.subtract', { step: format(habit.step) })"
        @click="emit('update', Math.max(0, roundValue(value - habit.step)))"
      >
        <iconify-icon icon="fa6-solid:minus" />
      </UiButton>

      <UiButton
        variant="success"
        size="sm"
        square
        :title="$t('habits.day.add', { step: format(habit.step) })"
        @click="emit('update', roundValue(value + habit.step))"
      >
        <iconify-icon icon="fa6-solid:plus" />
      </UiButton>

      <UiButton
        variant="tertiary"
        size="sm"
        square
        :title="$t('habits.day.exact_value')"
        @click="emit('open')"
      >
        <iconify-icon icon="fa6-solid:pen" />
      </UiButton>
    </div>
  </div>
</template>
