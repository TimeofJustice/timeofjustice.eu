<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { computed, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { useMediaQuery } from "@composables/mediaQuery";
import { api, formatNumber, habitStats, LEVEL_MIX } from "@composables/habits";
import HabitsYearGrid from "@components/HabitsYearGrid.vue";
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

// Which cards are unfolded. Everything starts open; folding one away is for
// getting a long list of habits back onto one screen.
const expanded = reactive<Record<number, boolean>>(
  Object.fromEntries(habits.map((habit) => [habit.id, true])),
);

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

/** The `xl` breakpoint, where the cards go two abreast. */
const isWide = useMediaQuery("(min-width: 1200px)");

/**
 * The cards, already split into the columns they are laid out in.
 *
 * Two stacked flex columns rather than one two-column grid: in a grid every row
 * is as tall as its tallest card, so folding one away leaves a hole instead of
 * pulling the card below it up.
 */
const columns = computed(() => {
  if (!isWide.value) return [habitList.value];

  const left: Habit[] = [];
  const right: Habit[] = [];

  habitList.value.forEach((habit, index) => {
    (index % 2 === 0 ? left : right).push(habit);
  });

  return [left, right];
});

const valuesOf = (habit: Habit) => entryMap[String(habit.id)] ?? {};

const valueOf = (habit: Habit, date: string) => valuesOf(habit)[date] ?? 0;

const dayValue = computed(() =>
  dayHabit.value && dayDate.value ? valueOf(dayHabit.value, dayDate.value) : 0,
);

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

  // Painted first, saved second: tapping "+1000" six times in a row must not
  // wait for six round trips to show what it did.
  if (value > 0) values[date] = value;
  else delete values[date];

  api
    .log(habitId, date, value)
    .then((logged) => {
      // The server counts streaks, because they run past New Year and the page
      // only holds one year. So the flame follows the tap that fed it.
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

  expanded[saved.id] ??= true;
};

const onHabitDeleted = (id: number) => {
  habitList.value = habitList.value.filter((habit) => habit.id !== id);
  delete entryMap[String(id)];
  delete expanded[id];
};

const selectYear = (next: number) => {
  if (next < firstYear || next > lastYear || loadingYear.value) return;

  loadingYear.value = true;

  api
    .year(next)
    .then((data) => {
      // Replaced rather than merged: only one year is ever on screen, and stale
      // days from the previous one would paint themselves into the new grid.
      Object.keys(entryMap).forEach((key) => delete entryMap[key]);
      Object.assign(entryMap, data.entries);

      selectedYear.value = data.year;

      // Keeps a reload — and a shared link — on the year being looked at.
      window.history.replaceState({}, "", `/habits/${data.year}/`);
    })
    .catch(fail)
    .finally(() => {
      loadingYear.value = false;
    });
};

const statsOf = (habit: Habit) => habitStats(valuesOf(habit), habit.goal);

/** The run going now is the best there has ever been. */
const atRecord = (habit: Habit) =>
  habit.streak.current > 0 && habit.streak.current === habit.streak.longest;

const format = (number: number) => formatNumber(number, i18n.locale.value);

/** Swatches for the legend, from "nothing" to "goal reached". */
const legendColors = (color: string) =>
  LEVEL_MIX.map((mix) =>
    mix === 0 ? null : `color-mix(in srgb, ${color} ${mix}%, transparent)`,
  );
</script>

<template>
  <Head :title="$t('habits.title')" />

  <div class="container-page flex flex-col gap-4 py-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h1 class="m-0 text-h3-fluid">
        <iconify-icon icon="fa6-solid:calendar-check" />
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
          <span class="text-accent">— {{ formattedToday }}</span>
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
        <!-- Every row is the same height, so a plain grid does here what the
             panels below need stacked columns for. -->
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

    <!-- Two habits abreast once there is room for it; the year inside a card
         shrinks to fit rather than scrolling. Each column stacks on its own, so
         folding one card away pulls everything under it straight up. -->
    <div class="flex flex-col gap-4 xl:flex-row xl:items-start">
      <div
        v-for="(column, index) in columns"
        :key="index"
        class="flex min-w-0 flex-1 flex-col gap-4"
      >
        <UiCard
          v-for="habit in column"
          :key="habit.id"
          no-body
          header-class="flex items-center justify-between gap-2 relative"
          :class="loadingYear && 'opacity-60'"
        >
          <template #header>
            <div class="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
              <span
                class="size-3 shrink-0 rounded-full"
                :style="{ backgroundColor: habit.color }"
              />

              <h2 class="m-0 truncate text-h6">{{ habit.name }}</h2>

              <span class="text-sm text-accent">
                {{
                  $t("habits.goal_label", {
                    goal: format(habit.goal),
                    unit: habit.unit,
                  })
                }}
              </span>

              <UiBadge v-if="habit.archived" variant="tertiary">
                {{ $t("habits.archived") }}
              </UiBadge>

              <!-- Kept in the header so a folded-away habit still says how it
                   is doing: days reached this year, the run going now, and the
                   best run there has ever been.

                   Lifted above the chevron's full-header hit area, which lies
                   over everything here and would otherwise swallow the hover —
                   and with it every one of these tooltips. -->
              <div class="relative z-2 flex flex-wrap items-center gap-x-2">
                <UiTooltip
                  :text="
                    $t('habits.stats.done', {
                      count: format(statsOf(habit).done),
                      year: selectedYear,
                    })
                  "
                >
                  <span class="flex items-center gap-1 text-sm text-accent">
                    <iconify-icon icon="fa6-solid:check" />
                    {{ format(statsOf(habit).done) }}
                  </span>
                </UiTooltip>

                <!-- A running streak burns; a broken one is just a number. -->
                <UiTooltip
                  :text="
                    $t('habits.stats.current', {
                      count: format(habit.streak.current),
                    })
                  "
                >
                  <span
                    class="flex items-center gap-1 text-sm"
                    :class="
                      habit.streak.current > 0 ? 'text-warning' : 'text-accent'
                    "
                  >
                    <iconify-icon
                      icon="fa6-solid:fire"
                      :class="
                        habit.streak.current > 0 &&
                        'animate-flame motion-reduce:animate-none'
                      "
                    />
                    {{ format(habit.streak.current) }}
                  </span>
                </UiTooltip>

                <!-- Standing on the record right now: the trophy joins in. -->
                <UiTooltip
                  :text="
                    atRecord(habit)
                      ? $t('habits.stats.record', {
                          count: format(habit.streak.longest),
                        })
                      : $t('habits.stats.streak', {
                          count: format(habit.streak.longest),
                        })
                  "
                >
                  <span
                    class="flex items-center gap-1 text-sm"
                    :class="atRecord(habit) ? 'text-warning' : 'text-accent'"
                  >
                    <iconify-icon
                      icon="fa6-solid:trophy"
                      :class="
                        atRecord(habit) &&
                        'animate-sparkle motion-reduce:animate-none'
                      "
                    />
                    {{ format(habit.streak.longest) }}
                  </span>
                </UiTooltip>
              </div>
            </div>

            <div class="flex shrink-0 items-center gap-1">
              <!-- Above the chevron's full-header hit area, which would swallow it. -->
              <UiButton
                variant="tertiary"
                square
                size="sm"
                class="relative z-2"
                :title="$t('habits.form.edit_title')"
                @click="editHabit(habit)"
              >
                <iconify-icon icon="fa6-solid:gear" />
              </UiButton>

              <UiButton
                variant="tertiary"
                square
                size="sm"
                class="after:absolute after:inset-0 after:z-1 after:content-['']"
                :title="$t('habits.toggle')"
                @click="expanded[habit.id] = !expanded[habit.id]"
              >
                <iconify-icon
                  icon="fa6-solid:chevron-up"
                  class="transition-transform duration-300 ease-in-out"
                  :style="{
                    transform: expanded[habit.id]
                      ? 'rotate(0deg)'
                      : 'rotate(180deg)',
                  }"
                />
              </UiButton>
            </div>
          </template>

          <UiCollapse v-model="expanded[habit.id]">
            <UiCardBody class="flex flex-col gap-2">
              <HabitsYearGrid
                :habit="habit"
                :year="selectedYear"
                :values="valuesOf(habit)"
                :today="today"
                @select="openDay(habit, $event)"
              />

              <div
                class="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-sm text-accent"
              >
                <span>
                  {{
                    $t("habits.stats.total", {
                      total: format(statsOf(habit).total),
                      unit: habit.unit,
                    })
                  }}
                </span>

                <!-- Legend: how full a square is says how close that day came. -->
                <div class="flex items-center gap-1">
                  {{ $t("habits.legend.less") }}
                  <span
                    v-for="(swatch, level) in legendColors(habit.color)"
                    :key="level"
                    class="size-2.5 rounded-xs"
                    :class="!swatch && 'bg-dark-gray-500/40'"
                    :style="{ backgroundColor: swatch ?? undefined }"
                  />
                  {{ $t("habits.legend.more") }}
                </div>
              </div>
            </UiCardBody>
          </UiCollapse>
        </UiCard>
      </div>
    </div>
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
    @update="dayHabit && dayDate && setValue(dayHabit.id, dayDate, $event)"
  />
</template>
