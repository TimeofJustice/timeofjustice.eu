<!--Refactoring needed-->

<script setup lang="ts">
import { ref } from "vue";
import { computed } from "@node_modules/vue";
import { useToast } from "@composables/toast";
import { useI18n } from "@node_modules/vue-i18n";
import axios from "@node_modules/axios";
import GamesDice from "@components/GamesDice.vue";

interface HigherLowerProps {
  balance: number;
}

type GameState = "betting" | "settingBet" | "playing" | "end";

interface GameSession {
  state: GameState;
  dice: number[];
  bets: Record<turnType, number>;
  bet: number;
  initialBet: number;
  possibleWins: turnType[];
}

const i18n = useI18n();
const { create } = useToast();
const emit = defineEmits({
  balanceChange: null,
});

const { balance } = defineProps<HigherLowerProps>();

const gameSession = ref<GameSession>({
  state: "betting",
  dice: [1, 2, 3],
  bets: {} as Record<turnType, number>,
  bet: 0,
  initialBet: 0,
  possibleWins: [],
});
const newGameSession = ref<GameSession | undefined>(undefined);

const waitingForResponse = ref(false);
const areRulesOpen = ref(false);

const diceValues = ref([1, 2, 3]);

const evaluate = () => {
  rollDice(20, 40, 60);
};

const rollDice = (amount1: number, amount2: number, amount3: number) => {
  setTimeout(() => {
    const value1 =
      amount1 > 0
        ? Math.floor(Math.random() * 6) + 1
        : gameSession.value.dice[0];
    const value2 =
      amount2 > 0
        ? Math.floor(Math.random() * 6) + 1
        : gameSession.value.dice[1];
    const value3 =
      amount3 > 0
        ? Math.floor(Math.random() * 6) + 1
        : gameSession.value.dice[2];

    diceValues.value = [value1, value2, value3];

    if (amount1 > 0 || amount2 > 0 || amount3 > 0)
      rollDice(amount1 - 1, amount2 - 1, amount3 - 1);
    else {
      gameSession.value = newGameSession.value
        ? newGameSession.value
        : gameSession.value;
      waitingForResponse.value = false;

      if (gameSession.value.state === "end" && gameSession.value.bet > 0)
        emit("balanceChange", gameSession.value["bet"]);
    }
  }, 100);
};

const showToast = (message: string, variant: "success" | "danger") => {
  create({ body: message, variant, position: "bottom-start" });
};

type totalType =
  | "small"
  | "big"
  | "total-4"
  | "total-5"
  | "total-6"
  | "total-7"
  | "total-8"
  | "total-9"
  | "total-10"
  | "total-11"
  | "total-12"
  | "total-13"
  | "total-14"
  | "total-15"
  | "total-16"
  | "total-17";
type doubleType =
  | "double-1"
  | "double-2"
  | "double-3"
  | "double-4"
  | "double-5"
  | "double-6";
type tripleType =
  | "triple-any"
  | "triple-1"
  | "triple-2"
  | "triple-3"
  | "triple-4"
  | "triple-5"
  | "triple-6";
type pairType =
  | "pair-1-2"
  | "pair-1-3"
  | "pair-1-4"
  | "pair-1-5"
  | "pair-1-6"
  | "pair-2-3"
  | "pair-2-4"
  | "pair-2-5"
  | "pair-2-6"
  | "pair-3-4"
  | "pair-3-5"
  | "pair-3-6"
  | "pair-4-5"
  | "pair-4-6"
  | "pair-5-6";
type faceType = "face-1" | "face-2" | "face-3" | "face-4" | "face-5" | "face-6";
type turnType = totalType | doubleType | tripleType | pairType | faceType;

const start = async () => {
  waitingForResponse.value = true;

  axios
    .post(`/games/api/sic-bo/start/`, {
      bets: gameSession.value.bets,
    })
    .then((response) => {
      const data = response.data;

      emit("balanceChange", -data["initialBet"]);

      gameSession.value.state = "playing";

      gameSession.value.dice = data["dice"];
      newGameSession.value = {
        state: "end",
        dice: data["dice"],
        bets: data["bets"],
        bet: data["bet"],
        initialBet: data["initialBet"],
        possibleWins: data["possibleWins"],
      };

      evaluate();
    })
    .catch((error) => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

const gameEnd = () => {
  gameSession.value = {
    state: "betting",
    dice: [1, 2, 3],
    bets: gameSession.value.bets,
    bet: 0,
    initialBet: 0,
    possibleWins: [],
  };
  diceValues.value = [1, 2, 3];
  newGameSession.value = undefined;
};

const currentType = ref<turnType | undefined>(undefined);
const currentBet = ref<number>(0);

const getTotalBet = () => {
  let total = 0;

  for (const value of Object.values(gameSession.value.bets)) {
    total += Number(value);
  }

  if (
    currentType.value &&
    gameSession.value.bets[currentType.value] !== undefined
  ) {
    total -= gameSession.value.bets[currentType.value] ?? 0;
  }

  return total;
};

const validateBet = computed(() => {
  return (
    currentBet.value >= 10 &&
    currentBet.value <= 500 &&
    currentBet.value <= balance - getTotalBet()
  );
});

const validateTotalBet = computed(() => {
  const total = getTotalBet() + Number(currentBet.value);

  return total >= 10 && total <= 500 && getTotalBet() <= balance;
});

const startBet = (type: turnType) => {
  if (type in gameSession.value.bets) {
    currentBet.value = gameSession.value.bets[type];
  } else {
    currentBet.value = 10;
  }

  gameSession.value.state = "settingBet";
  currentType.value = type;
};

const setBet = () => {
  if (currentType.value && currentBet.value) {
    gameSession.value.bets[currentType.value] = Number(currentBet.value);
  }

  gameSession.value.state = "betting";
  currentType.value = undefined;
  currentBet.value = 0;
};

const removeBet = () => {
  if (currentType.value && currentType.value in gameSession.value.bets) {
    delete gameSession.value.bets[currentType.value];
  }

  gameSession.value.state = "betting";
  currentType.value = undefined;
  currentBet.value = 0;
};
</script>

<template>
  <UiCard
    class="overflow-hidden border-0"
    header-class="flex items-center justify-between"
    body-class="flex flex-col"
    no-padding
  >
    <template #header>
      <h4 class="m-0">
        <iconify-icon icon="fa7-solid:dice" />
        {{ $t("games.game.sic_bo.title") }}
      </h4>

      <UiButton variant="tertiary" class="opacity-0" square>
        <iconify-icon icon="iconamoon:copy-duotone" />
      </UiButton>
    </template>

    <div
      class="relative flex h-full w-full flex-col items-center justify-center gap-2 p-4"
    >
      <UiButton
        variant="primary"
        class="absolute top-0 right-0 z-3 m-2"
        @click="areRulesOpen = true"
        circle
      >
        <iconify-icon icon="fa7-solid:info" />
      </UiButton>

      <UiModal
        v-model="areRulesOpen"
        header-class="justify-between items-center"
        scrollable
        size="xl"
        centered
      >
        <vue-markdown :source="$t('games.game.sic_bo.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("games.game.sic_bo.title") }}</h2>

          <UiButton
            variant="tertiary"
            class="text-light"
            @click="areRulesOpen = false"
            square
          >
            <iconify-icon icon="ep:close-bold" />
          </UiButton>
        </template>
      </UiModal>

      <Transition>
        <div
          class="absolute top-0 left-0 z-2 flex h-full w-full flex-col items-center justify-center gap-2 bg-black/50"
          v-if="
            gameSession.state !== 'betting' && gameSession.state !== 'playing'
          "
        >
          <div
            class="flex w-5/6 shrink-0 flex-col gap-2 rounded-surface border border-hairline bg-surface p-2 shadow-overlay md:w-5/12 lg:w-1/3"
          >
            <h1 class="text-center" v-if="gameSession.state !== 'settingBet'">
              {{
                gameSession.bet - gameSession.initialBet >= 0
                  ? $t("games.game.sic_bo.outcomes.won")
                  : $t("games.game.sic_bo.outcomes.lost")
              }}
            </h1>

            <h5
              class="mb-0 flex w-full flex-col gap-2 rounded-lg p-2 text-center"
              :class="
                gameSession.bet - gameSession.initialBet >= 0
                  ? 'text-success'
                  : 'text-danger'
              "
              v-if="gameSession.state === 'end'"
            >
              {{ gameSession.bet - gameSession.initialBet > 0 ? "+" : ""
              }}{{ gameSession.bet - gameSession.initialBet }}
            </h5>

            <UiFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-center">
                {{ $t("games.game.sic_bo.bet") }}: {{ currentBet }}
              </span>
              <UiInput
                id="input-2"
                type="range"
                v-model="currentBet"
                min="10"
                :max="
                  balance - getTotalBet() < 500 ? balance - getTotalBet() : 500
                "
                :state="validateBet && validateTotalBet"
              />
              <UiInvalidFeedback :state="validateBet || validateTotalBet">
                <span v-if="!validateTotalBet">
                  {{ $t("games.game.sic_bo.bet_too_high") }}
                </span>
                <span v-else>
                  {{ $t("games.not_enough_tokens") }}
                </span>
              </UiInvalidFeedback>
            </UiFormGroup>

            <UiButton
              variant="primary"
              @click.prevent="gameEnd"
              v-if="gameSession.state !== 'settingBet'"
              size="lg"
            >
              {{ $t("games.game.sic_bo.actions.play_again") }}
            </UiButton>
            <div v-else class="flex w-full gap-2">
              <UiButton
                variant="primary"
                class="w-full truncate"
                @click.prevent="setBet"
                :disabled="!validateBet || !validateTotalBet"
                size="lg"
              >
                {{ $t("games.game.sic_bo.bet") }}
              </UiButton>
              <UiButton variant="danger" @click.prevent="removeBet" size="lg">
                <iconify-icon icon="ep:close-bold" />
              </UiButton>
            </div>
          </div>
        </div>
      </Transition>

      <div class="flex w-full flex-col gap-2">
        <div class="flex w-full items-center justify-center gap-2">
          <GamesDice :value="diceValues[0]" />
          <GamesDice :value="diceValues[1]" />
          <GamesDice :value="diceValues[2]" />
        </div>
        <div class="flex w-full flex-col gap-2">
          <div
            class="flex w-full flex-wrap items-stretch justify-between gap-2"
          >
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('small')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['small'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('small')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['small']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["small"] }}
                </div>
                <h3>Small</h3>
                <div>4 - 10</div>
                <div>{{ $t("games.game.sic_bo.loss_3") }}</div>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:1
              </div>
            </div>

            <div class="flex grow flex-col items-stretch gap-2">
              <div
                class="flex h-full w-full items-stretch justify-center gap-2"
              >
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('double-1')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['double-1']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('double-1')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['double-1']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["double-1"] }}
                  </div>
                  <GamesDice :value="1" size="md" />
                  <GamesDice :value="1" size="md" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('double-2')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['double-2']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('double-2')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['double-2']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["double-2"] }}
                  </div>
                  <GamesDice :value="2" size="md" />
                  <GamesDice :value="2" size="md" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('double-3')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    gameSession.bets['double-3'] ? 'border border-warning' : ''
                  "
                >
                  <div
                    v-if="gameSession.bets['double-3']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["double-3"] }}
                  </div>
                  <GamesDice :value="3" size="md" />
                  <GamesDice :value="3" size="md" />
                </UiButton>
              </div>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:11
              </div>
            </div>

            <div class="flex grow flex-col items-stretch gap-2">
              <div
                class="flex h-full w-full flex-col items-stretch justify-center gap-2"
              >
                <UiButton
                  variant="secondary"
                  class="relative flex h-full items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('triple-1')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['triple-1']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('triple-1')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['triple-1']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["triple-1"] }}
                  </div>
                  <GamesDice :value="1" size="sm" />
                  <GamesDice :value="1" size="sm" />
                  <GamesDice :value="1" size="sm" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex h-full items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('triple-2')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['triple-2']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('triple-2')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['triple-2']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["triple-2"] }}
                  </div>
                  <GamesDice :value="2" size="sm" />
                  <GamesDice :value="2" size="sm" />
                  <GamesDice :value="2" size="sm" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex h-full items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('triple-3')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['triple-3']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('triple-3')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['triple-3']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["triple-3"] }}
                  </div>
                  <GamesDice :value="3" size="sm" />
                  <GamesDice :value="3" size="sm" />
                  <GamesDice :value="3" size="sm" />
                </UiButton>
              </div>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:180
              </div>
            </div>

            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex flex-col gap-2 overflow-hidden p-2"
                @click="startBet('triple-any')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['triple-any']
                    ? 'border border-warning'
                    : '') +
                  (gameSession.possibleWins.includes('triple-any')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['triple-any']"
                  class="absolute relative top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["triple-any"] }}
                </div>
                <div class="flex w-full items-center justify-center gap-2">
                  <GamesDice :value="1" size="sm" />
                  <GamesDice :value="1" size="sm" />
                  <GamesDice :value="1" size="sm" />
                </div>
                <div class="flex w-full items-center justify-center gap-2">
                  <GamesDice :value="2" size="sm" />
                  <GamesDice :value="2" size="sm" />
                  <GamesDice :value="2" size="sm" />
                </div>
                <div class="flex w-full items-center justify-center gap-2">
                  <GamesDice :value="3" size="sm" />
                  <GamesDice :value="3" size="sm" />
                  <GamesDice :value="3" size="sm" />
                </div>
                <div class="flex w-full items-center justify-center gap-2">
                  <GamesDice :value="4" size="sm" />
                  <GamesDice :value="4" size="sm" />
                  <GamesDice :value="4" size="sm" />
                </div>
                <div class="flex w-full items-center justify-center gap-2">
                  <GamesDice :value="5" size="sm" />
                  <GamesDice :value="5" size="sm" />
                  <GamesDice :value="5" size="sm" />
                </div>
                <div class="flex w-full items-center justify-center gap-2">
                  <GamesDice :value="6" size="sm" />
                  <GamesDice :value="6" size="sm" />
                  <GamesDice :value="6" size="sm" />
                </div>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:30
              </div>
            </div>

            <div class="flex grow flex-col items-stretch gap-2">
              <div
                class="flex h-full w-full flex-col items-stretch justify-center gap-2"
              >
                <UiButton
                  variant="secondary"
                  class="relative flex h-full items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('triple-4')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['triple-4']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('triple-4')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['triple-4']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["triple-4"] }}
                  </div>
                  <GamesDice :value="4" size="sm" />
                  <GamesDice :value="4" size="sm" />
                  <GamesDice :value="4" size="sm" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex h-full items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('triple-5')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['triple-5']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('triple-5')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['triple-5']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["triple-5"] }}
                  </div>
                  <GamesDice :value="5" size="sm" />
                  <GamesDice :value="5" size="sm" />
                  <GamesDice :value="5" size="sm" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex h-full items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('triple-6')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['triple-6']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('triple-6')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['triple-6']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["triple-6"] }}
                  </div>
                  <GamesDice :value="6" size="sm" />
                  <GamesDice :value="6" size="sm" />
                  <GamesDice :value="6" size="sm" />
                </UiButton>
              </div>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:180
              </div>
            </div>

            <div class="flex grow flex-col items-stretch gap-2">
              <div
                class="flex h-full w-full items-stretch justify-center gap-2"
              >
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('double-4')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['double-4']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('double-4')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['double-4']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["double-4"] }}
                  </div>
                  <GamesDice :value="4" size="md" />
                  <GamesDice :value="4" size="md" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('double-5')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['double-5']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('double-5')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['double-5']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["double-5"] }}
                  </div>
                  <GamesDice :value="5" size="md" />
                  <GamesDice :value="5" size="md" />
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('double-6')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['double-6']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('double-6')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['double-6']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["double-6"] }}
                  </div>
                  <GamesDice :value="6" size="md" />
                  <GamesDice :value="6" size="md" />
                </UiButton>
              </div>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:11
              </div>
            </div>

            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('big')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['big'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('big')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['big']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["big"] }}
                </div>
                <h3>Big</h3>
                <div>11 - 17</div>
                <div>{{ $t("games.game.sic_bo.loss_3") }}</div>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:1
              </div>
            </div>
          </div>

          <div
            class="flex w-full flex-wrap items-stretch justify-between gap-2"
          >
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-4')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-4'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('total-4')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-4']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-4"] }}
                </div>
                <h3>4</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:60
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-5')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-5'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('total-5')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-5']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-5"] }}
                </div>
                <h3>5</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:20
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-6')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-6'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('total-6')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-6']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-6"] }}
                </div>
                <h3>6</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:18
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-7')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-7'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('total-7')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-7']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-7"] }}
                </div>
                <h3>7</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:12
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-8')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-8'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('total-8')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-8']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-8"] }}
                </div>
                <h3>8</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:8
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <div class="flex items-center justify-center gap-2">
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('total-9')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['total-9']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('total-9')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['total-9']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["total-9"] }}
                  </div>
                  <h3>9</h3>
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('total-10')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['total-10']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('total-10')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['total-10']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["total-10"] }}
                  </div>
                  <h3>10</h3>
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('total-11')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['total-11']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('total-11')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['total-11']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["total-11"] }}
                  </div>
                  <h3>11</h3>
                </UiButton>
                <UiButton
                  variant="secondary"
                  class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                  @click="startBet('total-12')"
                  :disabled="
                    gameSession.state !== 'betting' || waitingForResponse
                  "
                  :class="
                    (gameSession.bets['total-12']
                      ? 'border border-warning'
                      : '') +
                    (gameSession.possibleWins.includes('total-12')
                      ? ' bg-success'
                      : '')
                  "
                >
                  <div
                    v-if="gameSession.bets['total-12']"
                    class="absolute top-0 right-0 z-3 bg-warning p-1"
                    style="border-bottom-left-radius: 0.5em"
                  >
                    {{ gameSession.bets["total-12"] }}
                  </div>
                  <h3>12</h3>
                </UiButton>
              </div>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:6
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-13')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-13']
                    ? 'border border-warning'
                    : '') +
                  (gameSession.possibleWins.includes('total-13')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-13']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-13"] }}
                </div>
                <h3>13</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:8
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-14')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-14']
                    ? 'border border-warning'
                    : '') +
                  (gameSession.possibleWins.includes('total-14')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-14']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-14"] }}
                </div>
                <h3>14</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:12
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-15')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-15']
                    ? 'border border-warning'
                    : '') +
                  (gameSession.possibleWins.includes('total-15')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-15']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-15"] }}
                </div>
                <h3>15</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:18
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-16')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-16']
                    ? 'border border-warning'
                    : '') +
                  (gameSession.possibleWins.includes('total-16')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-16']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-16"] }}
                </div>
                <h3>16</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:20
              </div>
            </div>
            <div class="flex grow flex-col gap-2">
              <UiButton
                variant="secondary"
                class="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('total-17')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['total-17']
                    ? 'border border-warning'
                    : '') +
                  (gameSession.possibleWins.includes('total-17')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['total-17']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["total-17"] }}
                </div>
                <h3>17</h3>
              </UiButton>
              <div
                class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center"
              >
                1:60
              </div>
            </div>
          </div>

          <div
            class="flex w-full flex-wrap items-stretch justify-between gap-2"
          >
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-1-2')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-1-2'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-1-2')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-1-2']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-1-2"] }}
              </div>
              <GamesDice :value="1" size="md" />
              <GamesDice :value="2" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-1-3')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-1-3'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-1-3')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-1-3']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-1-3"] }}
              </div>
              <GamesDice :value="1" size="md" />
              <GamesDice :value="3" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-1-4')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-1-4'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-1-4')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-1-4']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-1-4"] }}
              </div>
              <GamesDice :value="1" size="md" />
              <GamesDice :value="4" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-1-5')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-1-5'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-1-5')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-1-5']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-1-5"] }}
              </div>
              <GamesDice :value="1" size="md" />
              <GamesDice :value="5" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-1-6')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-1-6'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-1-6')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-1-6']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-1-6"] }}
              </div>
              <GamesDice :value="1" size="md" />
              <GamesDice :value="6" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-2-3')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-2-3'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-2-3')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-2-3']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-2-3"] }}
              </div>
              <GamesDice :value="2" size="md" />
              <GamesDice :value="3" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-2-4')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-2-4'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-2-4')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-2-4']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-2-4"] }}
              </div>
              <GamesDice :value="2" size="md" />
              <GamesDice :value="4" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-2-5')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-2-5'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-2-5')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-2-5']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-2-5"] }}
              </div>
              <GamesDice :value="2" size="md" />
              <GamesDice :value="5" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-2-6')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-2-6'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-2-6')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-2-6']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-2-6"] }}
              </div>
              <GamesDice :value="2" size="md" />
              <GamesDice :value="6" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-3-4')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-3-4'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-3-4')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-3-4']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-3-4"] }}
              </div>
              <GamesDice :value="3" size="md" />
              <GamesDice :value="4" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-3-5')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-3-5'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-3-5')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-3-5']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-3-5"] }}
              </div>
              <GamesDice :value="3" size="md" />
              <GamesDice :value="5" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-3-6')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-3-6'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-3-6')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-3-6']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-3-6"] }}
              </div>
              <GamesDice :value="3" size="md" />
              <GamesDice :value="6" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-4-5')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-4-5'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-4-5')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-4-5']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-4-5"] }}
              </div>
              <GamesDice :value="4" size="md" />
              <GamesDice :value="5" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-4-6')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-4-6'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-4-6')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-4-6']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-4-6"] }}
              </div>
              <GamesDice :value="4" size="md" />
              <GamesDice :value="6" size="md" />
            </UiButton>
            <UiButton
              variant="secondary"
              class="relative flex flex-col items-center justify-center gap-2 overflow-hidden p-2"
              @click="startBet('pair-5-6')"
              :disabled="gameSession.state !== 'betting' || waitingForResponse"
              :class="
                (gameSession.bets['pair-5-6'] ? 'border border-warning' : '') +
                (gameSession.possibleWins.includes('pair-5-6')
                  ? ' bg-success'
                  : '')
              "
            >
              <div
                v-if="gameSession.bets['pair-5-6']"
                class="absolute top-0 right-0 z-3 bg-warning p-1"
                style="border-bottom-left-radius: 0.5em"
              >
                {{ gameSession.bets["pair-5-6"] }}
              </div>
              <GamesDice :value="5" size="md" />
              <GamesDice :value="6" size="md" />
            </UiButton>
          </div>

          <div class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center">
            1:6
          </div>

          <div class="flex w-full flex-col justify-between gap-2">
            <div class="flex grow flex-wrap gap-2">
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('face-1')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['face-1'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('face-1')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['face-1']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["face-1"] }}
                </div>
                <GamesDice :value="1" size="md" />
              </UiButton>
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('face-2')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['face-2'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('face-2')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['face-2']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["face-2"] }}
                </div>
                <GamesDice :value="2" size="md" />
              </UiButton>
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('face-3')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['face-3'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('face-3')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['face-3']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["face-3"] }}
                </div>
                <GamesDice :value="3" size="md" />
              </UiButton>
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('face-4')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['face-4'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('face-4')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['face-4']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["face-4"] }}
                </div>
                <GamesDice :value="4" size="md" />
              </UiButton>
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('face-5')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['face-5'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('face-5')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['face-5']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["face-5"] }}
                </div>
                <GamesDice :value="5" size="md" />
              </UiButton>
              <UiButton
                variant="secondary"
                class="relative flex grow flex-col items-center justify-center gap-2 overflow-hidden p-2"
                @click="startBet('face-6')"
                :disabled="
                  gameSession.state !== 'betting' || waitingForResponse
                "
                :class="
                  (gameSession.bets['face-6'] ? 'border border-warning' : '') +
                  (gameSession.possibleWins.includes('face-6')
                    ? ' bg-success'
                    : '')
                "
              >
                <div
                  v-if="gameSession.bets['face-6']"
                  class="absolute top-0 right-0 z-3 bg-warning p-1"
                  style="border-bottom-left-radius: 0.5em"
                >
                  {{ gameSession.bets["face-6"] }}
                </div>
                <GamesDice :value="6" size="md" />
              </UiButton>
            </div>
            <div class="flex grow overflow-hidden rounded-lg">
              <div class="w-full bg-dark-gray-600/50 p-1 text-center">
                1:1 {{ $t("games.game.sic_bo.on_one_die") }}
              </div>
              <div class="w-full bg-dark-gray-600/50 p-1 text-center">
                1:2 {{ $t("games.game.sic_bo.on_two_dice") }}
              </div>
              <div class="w-full bg-dark-gray-600/50 p-1 text-center">
                1:3 {{ $t("games.game.sic_bo.on_three_dice") }}
              </div>
            </div>
          </div>

          <UiButton
            variant="primary"
            @click.prevent="start"
            :disabled="
              gameSession.state !== 'betting' ||
              waitingForResponse ||
              Object.keys(gameSession.bets).length === 0 ||
              !validateTotalBet
            "
            size="lg"
          >
            {{ $t("games.game.sic_bo.actions.start") }}
          </UiButton>
        </div>
      </div>
    </div>
  </UiCard>
</template>

<style scoped>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
