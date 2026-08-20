<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { api, formatNumber, parseDecimal } from "@composables/habits";
import type { Habit, HabitKind } from "@/types/Habit.ts";
import { FOCUS_RING } from "@components/ui/focus";

interface HabitsHabitModalProps {
  /** The habit being edited, or null to create a new one. */
  habit: Habit | null;
  /** The colours the backend accepts; anything else is rejected there. */
  colors: string[];
}

const { habit, colors } = defineProps<HabitsHabitModalProps>();

const show = defineModel<boolean>({ default: false });

const emit = defineEmits<{ saved: [habit: Habit]; deleted: [id: number] }>();

const i18n = useI18n();
const { create } = useToast();

// `goal` and `step` are held as text so a half-typed "0," survives; they are
// turned into numbers once, on submit.
const form = reactive({
  kind: "goal" as HabitKind,
  name: "",
  unit: "",
  goal: "1",
  step: "1",
  color: colors[0],
  archived: false,
});

/** The largest number the backend will take. */
const MAX_VALUE = 1_000_000_000;

const pending = ref(false);
const confirmingDelete = ref(false);

// Reset on every opening: the same dialog serves "new" and "edit", and a
// leftover name from the previous habit would be worse than an empty field.
watch(show, (open) => {
  if (!open) return;

  confirmingDelete.value = false;

  Object.assign(form, {
    kind: habit?.kind ?? "goal",
    name: habit?.name ?? "",
    unit: habit?.unit ?? "",
    goal: String(habit?.goal ?? 1),
    step: String(habit?.step ?? 1),
    color: habit?.color ?? colors[0],
    archived: habit?.archived ?? false,
  });
});

const nameState = computed(() =>
  form.name.length === 0 ? null : form.name.trim().length > 0,
);

const isMeasure = computed(() => form.kind === "measure");

/** Both kinds ask for the same numbers; only the words around them change. */
const KINDS: HabitKind[] = ["goal", "measure"];

const isPositive = (input: string) => {
  const number = parseDecimal(input);

  // 0.01 is the floor the backend rounds to; below it a goal stores as zero.
  return !Number.isNaN(number) && number >= 0.01 && number <= MAX_VALUE;
};

const goalState = computed(() =>
  form.goal.length === 0 ? null : isPositive(form.goal),
);

const stepState = computed(() =>
  form.step.length === 0 ? null : isPositive(form.step),
);

/** What the number fields ask for, spelled out for the tooltip. */
const numberError = computed(() =>
  i18n.t("habits.form.number_invalid", {
    min: formatNumber(0.01, i18n.locale.value),
    max: formatNumber(MAX_VALUE, i18n.locale.value),
  }),
);

const isValid = computed(
  () =>
    form.name.trim().length > 0 &&
    isPositive(form.goal) &&
    isPositive(form.step) &&
    form.unit.length <= 16,
);

const fail = (error: unknown) => {
  const key =
    (error as { response?: { data?: { error?: string } } })?.response?.data
      ?.error ?? "habits.errors.unknown";

  create({ body: i18n.t(key), variant: "danger", position: "bottom-start" });
};

const submit = () => {
  if (!isValid.value || pending.value) return;

  pending.value = true;

  const payload = {
    ...form,
    name: form.name.trim(),
    unit: form.unit.trim(),
    goal: parseDecimal(form.goal),
    step: parseDecimal(form.step),
  };
  const request = habit ? api.update(habit.id, payload) : api.create(payload);

  request
    .then((saved) => {
      emit("saved", saved);
      show.value = false;
    })
    .catch(fail)
    .finally(() => {
      pending.value = false;
    });
};

const remove = () => {
  if (!habit || pending.value) return;

  // Two clicks: deleting a habit takes its whole history with it.
  if (!confirmingDelete.value) {
    confirmingDelete.value = true;
    return;
  }

  pending.value = true;

  api
    .remove(habit.id)
    .then(() => {
      emit("deleted", habit.id);
      show.value = false;
    })
    .catch(fail)
    .finally(() => {
      pending.value = false;
    });
};
</script>

<template>
  <UiModal v-model="show" centered body-class="flex flex-col gap-3">
    <template #header>
      <h2 class="m-0 text-h5">
        {{ habit ? $t("habits.form.edit_title") : $t("habits.form.new_title") }}
      </h2>
    </template>

    <form class="flex flex-col gap-3" @submit.prevent="submit">
      <!-- The one choice that decides what the card becomes: a year of squares,
           or a line. Everything below reads slightly differently for each. -->
      <UiFormGroup :label="$t('habits.form.kind')">
        <div class="grid gap-2 sm:grid-cols-2">
          <UiButton
            v-for="option in KINDS"
            :key="option"
            variant="secondary"
            :active="form.kind === option"
            class="flex flex-col items-start gap-0.5 text-left"
            @click="form.kind = option"
          >
            <span class="flex items-center gap-2">
              <iconify-icon
                :icon="
                  option === 'goal'
                    ? 'fa6-solid:table-cells'
                    : 'fa6-solid:chart-line'
                "
              />
              {{ $t(`habits.form.kind_${option}`) }}
            </span>
            <span class="text-sm opacity-75">
              {{ $t(`habits.form.kind_${option}_hint`) }}
            </span>
          </UiButton>
        </div>
      </UiFormGroup>

      <UiFormGroup
        id="habit-name-group"
        label-for="habit-name"
        :label="$t('habits.form.name')"
      >
        <UiInput
          id="habit-name"
          v-model="form.name"
          :placeholder="
            $t(
              isMeasure
                ? 'habits.form.name_placeholder_measure'
                : 'habits.form.name_placeholder',
            )
          "
          :state="nameState"
          :error="$t('habits.form.name_invalid')"
          maxlength="40"
          required
        />
      </UiFormGroup>

      <div class="flex gap-3">
        <UiFormGroup
          class="grow"
          label-for="habit-goal"
          :label="$t(isMeasure ? 'habits.form.target' : 'habits.form.goal')"
        >
          <!-- Text, not `number`: a comma is what a German keyboard types, and
               a number field silently throws it away. -->
          <UiInput
            id="habit-goal"
            v-model="form.goal"
            type="text"
            inputmode="decimal"
            :state="goalState"
            :error="numberError"
          />
        </UiFormGroup>

        <UiFormGroup
          class="grow"
          label-for="habit-unit"
          :label="$t('habits.form.unit')"
        >
          <UiInput
            id="habit-unit"
            v-model="form.unit"
            :placeholder="
              $t(
                isMeasure
                  ? 'habits.form.unit_placeholder_measure'
                  : 'habits.form.unit_placeholder',
              )
            "
            maxlength="16"
          />
        </UiFormGroup>
      </div>

      <UiFormGroup label-for="habit-step" :label="$t('habits.form.step')">
        <UiInput
          id="habit-step"
          v-model="form.step"
          type="text"
          inputmode="decimal"
          :state="stepState"
          :error="numberError"
        />
        <p class="mt-1 mb-0 text-sm text-accent">
          {{ $t("habits.form.step_hint") }}
        </p>
      </UiFormGroup>

      <UiFormGroup :label="$t('habits.form.color')">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="option in colors"
            :key="option"
            type="button"
            class="size-8 cursor-pointer rounded-md transition-transform duration-100 hover:scale-110"
            :class="[
              FOCUS_RING,
              form.color === option &&
                'ring-2 ring-light ring-offset-2 ring-offset-surface',
            ]"
            :style="{ backgroundColor: option }"
            :aria-label="option"
            :aria-pressed="form.color === option"
            @click="form.color = option"
          />
        </div>
      </UiFormGroup>

      <label v-if="habit" class="flex items-center gap-2">
        <input v-model="form.archived" type="checkbox" class="size-4" />
        {{ $t("habits.form.archived") }}
      </label>
    </form>

    <template #footer>
      <UiButton
        v-if="habit"
        :variant="confirmingDelete ? 'danger' : 'tertiary'"
        class="mr-auto"
        :disabled="pending"
        @click="remove"
      >
        {{
          confirmingDelete
            ? $t("habits.form.delete_confirm")
            : $t("habits.form.delete")
        }}
      </UiButton>

      <UiButton variant="secondary" :disabled="pending" @click="show = false">
        {{ $t("general.close") }}
      </UiButton>

      <UiButton
        variant="success"
        :disabled="!isValid || pending"
        @click="submit"
      >
        {{ $t("general.save") }}
      </UiButton>
    </template>
  </UiModal>
</template>
