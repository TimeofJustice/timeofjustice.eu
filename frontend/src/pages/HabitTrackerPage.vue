<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { computed, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { api, carriedValue } from "@composables/habits";
import HabitsBoard from "@components/HabitsBoard.vue";
import HabitsQuickRow from "@components/HabitsQuickRow.vue";
import HabitsDayModal from "@components/HabitsDayModal.vue";
import HabitsHabitModal from "@components/HabitsHabitModal.vue";
import type { Habit, HabitEntries } from "@/types/Habit.ts";

interface HabitTrackerPageProps {
  year: number;
  firstYear: number;
  lastYear: number;
  /** Today as "YYYY-MM-DD", from the server, so the grid agrees with it. */
  today: string;
  colors: string[];
  habits: Habit[];
  entries: HabitEntries;
}

const { year, firstYear, lastYear, today, colors, habits, entries } =
  defineProps<HabitTrackerPageProps>();

const i18n = useI18n();
const { create } = useToast();

const habitList = ref<Habit[]>([...habits]);
const entryMap = reactive<HabitEntries>({ ...entries });

// Only the quick rows fold; the panels below stay open.
const showToday = ref(true);

const selectedYear = ref(year);
const loadingYear = ref(false);

const editedHabit = ref<Habit | null>(null);
const showHabitModal = ref(false);

const dayHabit = ref<Habit | null>(null);
const dayDate = ref<string | null>(null);
const showDayModal = ref(false);

const activeHabits = computed(() =>
  habitList.value.filter((habit) => !habit.archived),
);

const valuesOf = (habit: Habit) => entryMap[String(habit.id)] ?? {};

const valueOf = (habit: Habit, date: string) => valuesOf(habit)[date] ?? 0;

const dayValue = computed(() =>
  dayHabit.value && dayDate.value ? valueOf(dayHabit.value, dayDate.value) : 0,
);

/** Only a measurement carries a value forward; a missed daily goal is a zero. */
const daySuggestion = computed(() =>
  dayHabit.value && dayDate.value && dayHabit.value.kind === "measure"
    ? carriedValue(valuesOf(dayHabit.value), dayDate.value)
    : null,
);

const firstDate = computed(() => `${firstYear}-01-01`);

const formattedToday = computed(() =>
  new Date(`${today}T00:00:00`).toLocaleDateString(i18n.locale.value, {
    weekday: "long",
    day: "numeric",
    month: "long",
  }),
);

const fail = (error: unknown) => {
  const key =
    (error as { response?: { data?: { error?: string } } })?.response?.data
      ?.error ?? "habits.errors.unknown";

  create({ body: i18n.t(key), variant: "danger", position: "bottom-start" });
};

const setValue = (habitId: number, date: string, value: number) => {
  const key = String(habitId);
  const values = entryMap[key] ?? (entryMap[key] = {});
  const previous = values[date] ?? 0;

  // Painted first, saved second: six taps must not wait for six round trips.
  if (value > 0) values[date] = value;
  else delete values[date];

  api
    .log(habitId, date, value)
    .then((logged) => {
      // Streaks run past New Year, so only the server can count them.
      const habit = habitList.value.find((entry) => entry.id === habitId);

      if (habit) habit.streak = logged.streak;
    })
    .catch((error) => {
      if (previous > 0) values[date] = previous;
      else delete values[date];

      fail(error);
    });
};

const openDay = (habit: Habit, date: string) => {
  dayHabit.value = habit;
  dayDate.value = date;
  showDayModal.value = true;
};

const newHabit = () => {
  editedHabit.value = null;
  showHabitModal.value = true;
};

const editHabit = (habit: Habit) => {
  editedHabit.value = habit;
  showHabitModal.value = true;
};

const onHabitSaved = (saved: Habit) => {
  const index = habitList.value.findIndex((habit) => habit.id === saved.id);

  if (index === -1) habitList.value.push(saved);
  else habitList.value[index] = saved;
};

const onHabitDeleted = (id: number) => {
  habitList.value = habitList.value.filter((habit) => habit.id !== id);
  delete entryMap[String(id)];
};

const selectYear = (next: number) => {
  if (next < firstYear || next > lastYear || loadingYear.value) return;

  loadingYear.value = true;

  api
    .year(next)
    .then((data) => {
      // Replaced, not merged: stale days would paint into the new grid.
      Object.keys(entryMap).forEach((key) => delete entryMap[key]);
      Object.assign(entryMap, data.entries);

      selectedYear.value = data.year;

      // Keeps a reload, and a shared link, on the year being looked at.
      window.history.replaceState({}, "", `/momentum/${data.year}/`);
    })
    .catch(fail)
    .finally(() => {
      loadingYear.value = false;
    });
};

/**
 * Saves what the board hands over. The whole arrangement goes, not a move, so a
 * lost request cannot leave the board half rearranged.
 */
const arrange = (arranged: Habit[]) => {
  const previous = habitList.value;

  habitList.value = arranged;

  api.layout(arranged.map(({ id, wide }) => ({ id, wide }))).catch((error) => {
    habitList.value = previous;

    fail(error);
  });
};
</script>

<template>
  <Head :title="$t('habits.title')" />

  <div class="container-page flex flex-col gap-4 py-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h1 class="m-0 text-h3-fluid">
        <iconify-icon icon="fa6-solid:bolt" />
        {{ $t("habits.title") }}
      </h1>

      <div class="flex items-center gap-2">
        <UiButton
          variant="secondary"
          square
          :disabled="selectedYear <= firstYear || loadingYear"
          :title="$t('habits.previous_year')"
          @click="selectYear(selectedYear - 1)"
        >
          <iconify-icon icon="fa6-solid:chevron-left" />
        </UiButton>

        <span class="w-16 text-center text-control-lg tabular-nums">
          {{ selectedYear }}
        </span>

        <UiButton
          variant="secondary"
          square
          :disabled="selectedYear >= lastYear || loadingYear"
          :title="$t('habits.next_year')"
          @click="selectYear(selectedYear + 1)"
        >
          <iconify-icon icon="fa6-solid:chevron-right" />
        </UiButton>

        <UiButton variant="success" @click="newHabit">
          <iconify-icon icon="fa6-solid:plus" />
          {{ $t("habits.new_habit") }}
        </UiButton>
      </div>
    </div>

    <UiCard
      v-if="habitList.length === 0"
      body-class="flex flex-col gap-3 py-8 text-center"
    >
      <p class="m-0 text-accent">{{ $t("habits.empty") }}</p>

      <div>
        <UiButton variant="success" @click="newHabit">
          {{ $t("habits.new_habit") }}
        </UiButton>
      </div>
    </UiCard>

    <!-- Everything for today in one place, so logging never needs the grid. -->
    <UiCard
      v-if="activeHabits.length > 0"
      no-body
      header-class="flex items-center justify-between gap-2 relative"
    >
      <template #header>
        <h2 class="m-0 truncate text-h6">
          {{ $t("habits.today") }}
          <span class="text-accent">· {{ formattedToday }}</span>
        </h2>

        <UiButton
          variant="tertiary"
          square
          size="sm"
          class="shrink-0 after:absolute after:inset-0 after:z-1 after:content-['']"
          :title="$t('habits.toggle')"
          @click="showToday = !showToday"
        >
          <iconify-icon
            icon="fa6-solid:chevron-up"
            class="transition-transform duration-300 ease-in-out"
            :style="{
              transform: showToday ? 'rotate(0deg)' : 'rotate(180deg)',
            }"
          />
        </UiButton>
      </template>

      <UiCollapse v-model="showToday">
        <!-- Every row is the same height, so a plain grid is enough here. -->
        <UiCardBody class="grid gap-x-6 gap-y-4 xl:grid-cols-2">
          <HabitsQuickRow
            v-for="habit in activeHabits"
            :key="habit.id"
            :habit="habit"
            :value="valueOf(habit, today)"
            @update="setValue(habit.id, today, $event)"
            @open="openDay(habit, today)"
          />
        </UiCardBody>
      </UiCollapse>
    </UiCard>

    <HabitsBoard
      :habits="habitList"
      :entries="entryMap"
      :year="selectedYear"
      :today="today"
      :loading="loadingYear"
      @edit="editHabit"
      @select="openDay"
      @arrange="arrange"
    />
  </div>

  <HabitsHabitModal
    v-model="showHabitModal"
    :habit="editedHabit"
    :colors="colors"
    @saved="onHabitSaved"
    @deleted="onHabitDeleted"
  />

  <HabitsDayModal
    v-model="showDayModal"
    :habit="dayHabit"
    :date="dayDate"
    :value="dayValue"
    :suggestion="daySuggestion"
    :first-date="firstDate"
    :last-date="today"
    @navigate="dayDate = $event"
    @update="dayHabit && dayDate && setValue(dayHabit.id, dayDate, $event)"
  />
</template>
