<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { api, parseDecimal } from "@composables/habits";
import type { Habit } from "@/types/Habit.ts";

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
      <UiFormGroup
        id="habit-name-group"
        label-for="habit-name"
        :label="$t('habits.form.name')"
      >
        <UiInput
          id="habit-name"
          v-model="form.name"
          :placeholder="$t('habits.form.name_placeholder')"
          :state="nameState"
          maxlength="40"
          required
        />
      </UiFormGroup>

      <div class="flex gap-3">
        <UiFormGroup
          class="grow"
          label-for="habit-goal"
          :label="$t('habits.form.goal')"
        >
          <!-- Text, not `number`: a comma is what a German keyboard types, and
               a number field silently throws it away. -->
          <UiInput
            id="habit-goal"
            v-model="form.goal"
            type="text"
            inputmode="decimal"
            :state="goalState"
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
            :placeholder="$t('habits.form.unit_placeholder')"
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
            :class="
              form.color === option &&
              'ring-2 ring-light ring-offset-2 ring-offset-dark-gray-600'
            "
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
