<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { computed, onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { api, carriedValue } from "@composables/habits";
import { useRefreshOnReturn } from "@composables/refresh";
import HabitsBoard from "@components/HabitsBoard.vue";
import HabitsQuickRow from "@components/HabitsQuickRow.vue";
import HabitsDayModal from "@components/HabitsDayModal.vue";
import HabitsHabitModal from "@components/HabitsHabitModal.vue";
import HabitsRecapModal from "@components/HabitsRecapModal.vue";
import type { Habit, HabitEntries, HabitRecap } from "@/types/Habit.ts";

interface HabitTrackerPageProps {
  year: number;
  /**
   * The years the arrows walk through, oldest first: the ones that hold
   * entries, plus the current one. An empty year is not worth paging to, and
   * the day editor is what reaches further back than this.
   */
  years: number[];
  firstYear: number;
  /** Today as "YYYY-MM-DD", from the server, so the grid agrees with it. */
  today: string;
  colors: string[];
  habits: Habit[];
  entries: HabitEntries;
  /**
   * The week that has ended since the last visit, or the span of a longer
   * absence. Null whenever there is nothing owed, which is most visits.
   */
  recap: HabitRecap | null;
}

const { year, years, firstYear, today, colors, habits, entries, recap } =
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

/**
 * The look back currently on screen. A copy, not the prop: the prop is null
 * again the moment the server is told the recap has been seen, and the dialog
 * would empty out from under the reader.
 */
const shownRecap = ref<HabitRecap | null>(null);
const showRecap = ref(false);

/**
 * Opens the look back the server says is owed, and tells it straight away that
 * it has been seen: a recap on the screen has been read, and a tab closed on it
 * must not bring the same week back, nor count as a week away.
 *
 * Run again after every refresh, not only on mount, because a tab left open
 * over a Sunday is exactly where the next week's recap falls due. The span it
 * ends on is what keeps it from opening twice for the same week.
 */
const takeRecap = () => {
  if (!recap || shownRecap.value?.end === recap.end) return;

  shownRecap.value = recap;
  showRecap.value = true;

  // A failed mark costs nothing worth a toast: at worst the same recap opens
  // once more on the next visit.
  api.recapSeen().catch(() => {});
};

onMounted(takeRecap);

/**
 * A tab left open past midnight is drawing yesterday's grid: `today` comes from
 * the server, and so does every streak counted against it. Coming back to the
 * tab asks again.
 *
 * The page keeps its own copies of the habits and the entries, because both are
 * written to optimistically while logging, and `reload` leaves the component
 * mounted. So the copies are taken again here, or the fresh props would sit
 * behind stale local state.
 */
useRefreshOnReturn({
  paused: () => showDayModal.value || showHabitModal.value || showRecap.value,
  onRefreshed: () => {
    habitList.value = [...habits];

    Object.keys(entryMap).forEach((key) => delete entryMap[key]);
    Object.assign(entryMap, entries);

    selectedYear.value = year;

    takeRecap();
  },
});

const activeHabits = computed(() =>
  habitList.value.filter((habit) => !habit.archived),
);

/** Where the year on screen sits in the years there are to walk through. */
const yearIndex = computed(() => years.indexOf(selectedYear.value));

/**
 * Whether the grid is showing the year that is being lived.
 *
 * The quick rows log today, and today is only on the screen in this year. In a
 * past one they would be a row of buttons that quietly write somewhere else,
 * so they are not offered at all; the grid and the day editor are how a past
 * year is corrected.
 */
const showingThisYear = computed(
  () => selectedYear.value === Number(today.slice(0, 4)),
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
  if (!years.includes(next) || loadingYear.value) return;

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

/** One year along the list, which is not always one year along the calendar. */
const stepYear = (direction: number) => {
  const next = years[yearIndex.value + direction];

  if (next !== undefined) selectYear(next);
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
          :disabled="yearIndex <= 0 || loadingYear"
          :title="$t('habits.previous_year')"
          @click="stepYear(-1)"
        >
          <iconify-icon icon="fa6-solid:chevron-left" />
        </UiButton>

        <span class="w-16 text-center text-control-lg tabular-nums">
          {{ selectedYear }}
        </span>

        <UiButton
          variant="secondary"
          square
          :disabled="yearIndex >= years.length - 1 || loadingYear"
          :title="$t('habits.next_year')"
          @click="stepYear(1)"
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

    <!-- Everything for today in one place, so logging never needs the grid.
         Gone while a past year is on screen: today is not in it. -->
    <UiCard
      v-if="activeHabits.length > 0 && showingThisYear"
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

  <HabitsRecapModal v-model="showRecap" :recap="shownRecap" />

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
