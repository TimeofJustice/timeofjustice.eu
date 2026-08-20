<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import {
  formatNumber,
  levelOf,
  parseDecimal,
  roundValue,
} from "@composables/habits";
import type { Habit } from "@/types/Habit.ts";

interface HabitsDayModalProps {
  habit: Habit | null;
  /** The day being edited, as "YYYY-MM-DD". */
  date: string | null;
  /** Currently logged value, kept in sync with the page's optimistic state. */
  value: number;
}

const { habit, date, value } = defineProps<HabitsDayModalProps>();

const show = defineModel<boolean>({ default: false });

const emit = defineEmits<{ update: [value: number] }>();

const i18n = useI18n();

// Mirrors `value` so the field can be typed in freely; committed on change,
// while the +/- buttons commit straight away. Held as text, not as a number, so
// a half-typed "7," survives long enough to become "7,5".
const draft = ref(String(value));

watch(
  () => value,
  (incoming) => {
    draft.value = String(incoming);
  },
);

/** Thousands separators make a step count readable at a glance. */
const format = (number: number) => formatNumber(number, i18n.locale.value);

const formattedDate = computed(() =>
  date
    ? new Date(`${date}T00:00:00`).toLocaleDateString(i18n.locale.value, {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "",
);

const percentage = computed(() =>
  habit && habit.goal > 0
    ? Math.min(100, Math.round((value / habit.goal) * 100))
    : 0,
);

const reached = computed(() => !!habit && levelOf(value, habit.goal) === 5);

const commit = (next: number) => {
  const clamped = Math.max(0, roundValue(next));

  draft.value = String(clamped);

  if (clamped !== value) emit("update", clamped);
};

/** Takes the typed text, or puts the current value back if it is not a number. */
const commitDraft = () => {
  const typed = parseDecimal(draft.value);

  if (Number.isNaN(typed)) {
    draft.value = String(value);
    return;
  }

  commit(typed);
};

const bump = (direction: number) => {
  if (!habit) return;

  commit(value + direction * habit.step);
};
</script>

<template>
  <UiModal v-if="habit" v-model="show" size="sm" centered>
    <template #header>
      <div class="flex min-w-0 items-center gap-2">
        <span
          class="size-3 shrink-0 rounded-full"
          :style="{ backgroundColor: habit.color }"
        />
        <div class="min-w-0">
          <h2 class="m-0 truncate text-h6">{{ habit.name }}</h2>
          <p class="m-0 text-sm text-accent">{{ formattedDate }}</p>
        </div>
      </div>
    </template>

    <div class="flex flex-col gap-3">
      <div class="text-center">
        <span class="text-h3 leading-none" :class="reached && 'text-success'">
          {{ format(value) }}
        </span>
        <span class="text-accent">
          / {{ format(habit.goal) }} {{ habit.unit }}
        </span>
      </div>

      <UiProgress>
        <UiProgressBar
          :value="percentage"
          :variant="reached ? 'success' : undefined"
        />
      </UiProgress>

      <!-- The fast path: one tap per step, no keyboard, no saving. -->
      <div class="flex items-center gap-2">
        <UiButton
          variant="secondary"
          class="grow"
          :disabled="value <= 0"
          @click="bump(-1)"
        >
          −{{ format(habit.step) }}
        </UiButton>

        <UiButton variant="success" class="grow" @click="bump(1)">
          +{{ format(habit.step) }}
        </UiButton>
      </div>

      <div class="flex items-center gap-2">
        <!-- Text, not `number`: a comma is what a German keyboard types, and a
             number field silently throws it away. -->
        <UiInput
          v-model="draft"
          type="text"
          inputmode="decimal"
          :aria-label="$t('habits.day.exact_value')"
          @change="commitDraft"
          @keyup.enter="commitDraft"
        />

        <UiButton
          variant="tertiary"
          :disabled="value <= 0"
          :title="$t('habits.day.clear')"
          @click="commit(0)"
        >
          <iconify-icon icon="fa6-solid:eraser" />
        </UiButton>
      </div>

      <UiButton variant="secondary" @click="show = false">
        {{ $t("general.close") }}
      </UiButton>
    </div>
  </UiModal>
</template>
