<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "@node_modules/vue";
import { useToast } from "@composables/toast";
import { useI18n } from "@node_modules/vue-i18n";
import axios from "@node_modules/axios";

interface RideTheBusProps {
  balance: number;
}

type GameState =
  | "not_started"
  | "first_round"
  | "second_round"
  | "third_round"
  | "fourth_round"
  | "won"
  | "lost";

interface GameSession {
  sessionId: string;
  state: GameState;
  cards: string[];
  bet: number;
  initialBet: number;
  msLeft: number;
}

const i18n = useI18n();
const { create } = useToast();
const emit = defineEmits({
  balanceChange: null,
});

const { balance } = defineProps<RideTheBusProps>();
const msPerTurn = 10000;

const gameSession = ref<GameSession>({
  sessionId: "",
  state: "not_started",
  cards: ["back", "back", "back", "back"],
  bet: 10,
  initialBet: 10,
  msLeft: msPerTurn,
});
const newGameSession = ref<GameSession | undefined>(undefined);

const waitingForResponse = ref(false);
const areRulesOpen = ref(false);

const cardLoaded = (from_round: GameState) => {
  if (gameSession.value && gameSession.value.state !== from_round) return;

  gameSession.value = newGameSession.value
    ? newGameSession.value
    : gameSession.value;
  waitingForResponse.value = false;

  if (gameSession.value.state === "won")
    emit("balanceChange", gameSession.value["bet"]);
};

const validateBet = computed(() => {
  return (
    gameSession.value["bet"] >= 10 &&
    gameSession.value["bet"] <= 500 &&
    gameSession.value["bet"] <= balance
  );
});

const showToast = (message: string, variant: "success" | "danger") => {
  create({ body: message, variant, position: "bottom-start" });
};

const start = async () => {
  waitingForResponse.value = true;

  axios
    .post(`/games/api/ride-the-bus/start/`, {
      bet: Number(gameSession.value["bet"]),
    })
    .then((response) => {
      const data = response.data;

      emit("balanceChange", -data["initial_bet"]);

      gameSession.value = {
        sessionId: data["session_id"],
        state: "first_round",
        cards: gameSession.value["cards"],
        bet: data["bet"],
        initialBet: data["initial_bet"],
        msLeft: msPerTurn,
      };

      waitingForResponse.value = false;
    })
    .catch((error) => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

type turnType =
  | "red"
  | "black"
  | "higher"
  | "lower"
  | "inside"
  | "outside"
  | "hearts"
  | "diamonds"
  | "spades"
  | "clubs"
  | "leave";

const processTurn = (type: turnType, gameState: GameState) => {
  waitingForResponse.value = true;

  axios
    .post(`/games/api/ride-the-bus/${type}/`, {
      session: gameSession.value["sessionId"],
    })
    .then((response) => {
      const data = response.data;
      const cardIndex = gameSession.value["cards"].findIndex(
        (card) => card === "back",
      );

      gameSession.value["cards"][cardIndex] = data["card"];
      newGameSession.value = {
        sessionId: data["session_id"],
        state: data["bet"] <= 0 ? "lost" : gameState,
        cards: gameSession.value["cards"],
        bet: data["bet"],
        initialBet: data["initial_bet"],
        msLeft: msPerTurn,
      };
    })
    .catch((error) => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

const gameEnd = () => {
  gameSession.value = {
    sessionId: "",
    state: "not_started",
    cards: ["back", "back", "back", "back"],
    bet: gameSession.value["initialBet"],
    initialBet: gameSession.value["initialBet"],
    msLeft: msPerTurn,
  };
  newGameSession.value = undefined;
};

const turnInterval = setInterval(() => {
  if (
    (gameSession.value.state === "first_round" ||
      gameSession.value.state === "second_round" ||
      gameSession.value.state === "third_round" ||
      gameSession.value.state === "fourth_round") &&
    gameSession.value.msLeft > 0 &&
    !waitingForResponse.value
  ) {
    gameSession.value.msLeft -= 50;

    if (gameSession.value.msLeft <= 0) {
      gameSession.value.state = "lost";
      gameSession.value.sessionId = "";
    }
  }
}, 50);

onBeforeUnmount(() => {
  clearInterval(turnInterval);
});
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
        {{ $t("games.game.ride_the_bus.title") }}
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
        <vue-markdown :source="$t('games.game.ride_the_bus.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("games.game.ride_the_bus.title") }}</h2>

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
            gameSession.state === 'not_started' ||
            gameSession.state === 'won' ||
            gameSession.state === 'lost'
          "
        >
          <div
            class="flex w-5/6 shrink-0 flex-col gap-2 rounded-lg bg-dark-gray-600 p-2 md:w-5/12 lg:w-1/3"
          >
            <h1 class="text-center" v-if="gameSession.state !== 'not_started'">
              {{
                gameSession.state === "lost"
                  ? $t("games.game.ride_the_bus.outcomes.lost")
                  : $t("games.game.ride_the_bus.outcomes.won")
              }}
            </h1>

            <UiFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-center">
                {{ $t("games.game.ride_the_bus.bet") }}: {{ gameSession.bet }}
              </span>
              <UiInput
                id="input-2"
                type="range"
                v-model="gameSession.bet"
                min="10"
                :max="balance < 500 ? balance : 500"
                :state="validateBet"
              />
              <UiInvalidFeedback :state="validateBet">
                {{ $t("games.not_enough_tokens") }}
              </UiInvalidFeedback>
            </UiFormGroup>

            <h5
              class="mb-0 flex w-full flex-col gap-2 rounded-lg p-2 text-center"
              :class="
                gameSession.bet - gameSession.initialBet > 0
                  ? 'text-success'
                  : ''
              "
              v-if="gameSession.state === 'won'"
            >
              {{ gameSession.bet - gameSession.initialBet > 0 ? "+" : ""
              }}{{ gameSession.bet - gameSession.initialBet }}
            </h5>

            <UiButton
              variant="primary"
              @click.prevent="gameEnd"
              v-if="gameSession.state !== 'not_started'"
              size="lg"
            >
              {{ $t("games.game.ride_the_bus.actions.play_again") }}
            </UiButton>
            <UiButton
              variant="primary"
              @click.prevent="start"
              v-else
              :disabled="
                !validateBet ||
                waitingForResponse ||
                gameSession.state !== 'not_started'
              "
              size="lg"
            >
              {{ $t("games.game.ride_the_bus.actions.start") }}
            </UiButton>
          </div>
        </div>
      </Transition>

      <div class="flex w-full flex-col gap-2">
        <div class="flex gap-2">
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[0] + '.svg'"
            :alt="gameSession.cards[0]"
            class="h-auto w-1/4 min-w-0 shrink grow basis-0"
            @load="cardLoaded('first_round')"
          />
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[1] + '.svg'"
            :alt="gameSession.cards[1]"
            class="h-auto w-1/4 min-w-0 shrink grow basis-0"
            @load="cardLoaded('second_round')"
          />
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[2] + '.svg'"
            :alt="gameSession.cards[2]"
            class="h-auto w-1/4 min-w-0 shrink grow basis-0"
            @load="cardLoaded('third_round')"
          />
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[3] + '.svg'"
            :alt="gameSession.cards[3]"
            class="h-auto w-1/4 min-w-0 shrink grow basis-0"
            @load="cardLoaded('fourth_round')"
          />
        </div>

        <div class="flex">
          <h3
            class="m-0 flex w-full flex-col gap-2 rounded-lg bg-dark-gray-600/50 p-2 text-center"
          >
            {{ gameSession.state === "not_started" ? 0 : gameSession.bet }}
          </h3>
        </div>

        <div class="flex gap-2">
          <div
            class="flex min-w-0 shrink grow basis-0 flex-col justify-between gap-2 transition-opacity duration-500 ease-in-out"
            :class="
              gameSession.state !== 'first_round' &&
              gameSession.state !== 'not_started'
                ? 'opacity-0'
                : ''
            "
          >
            <div class="flex flex-col gap-2">
              <UiProgress :max="msPerTurn">
                <UiProgressBar :value="gameSession.msLeft">
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </UiProgressBar>
              </UiProgress>
              <UiButton
                variant="danger"
                @click.prevent="processTurn('red', 'second_round')"
                :disabled="
                  gameSession.state !== 'first_round' || waitingForResponse
                "
              >
                <iconify-icon icon="mdi:suit-diamonds" />
                <iconify-icon icon="mdi:suit-hearts" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.red")
                }}</span>
                <iconify-icon
                  icon="mdi:suit-hearts"
                  class="ml-1 hidden md:inline-block"
                />
                <iconify-icon
                  icon="mdi:suit-diamonds"
                  class="hidden md:inline-block"
                />
              </UiButton>
              <UiButton
                variant="primary"
                @click.prevent="processTurn('black', 'second_round')"
                :disabled="
                  gameSession.state !== 'first_round' || waitingForResponse
                "
              >
                <iconify-icon icon="mdi:suit-spades" />
                <iconify-icon icon="mdi:suit-clubs" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.black")
                }}</span>
                <iconify-icon
                  icon="mdi:suit-clubs"
                  class="ml-1 hidden md:inline-block"
                />
                <iconify-icon
                  icon="mdi:suit-spades"
                  class="hidden md:inline-block"
                />
              </UiButton>
            </div>

            <div class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center">
              1:1
            </div>
          </div>

          <div
            class="flex min-w-0 shrink grow basis-0 flex-col justify-between gap-2 transition-opacity duration-500 ease-in-out"
            :class="gameSession.state !== 'second_round' ? 'opacity-0' : ''"
          >
            <div class="flex flex-col gap-2">
              <UiProgress :max="msPerTurn">
                <UiProgressBar
                  :value="
                    gameSession.state === 'second_round'
                      ? gameSession.msLeft
                      : msPerTurn
                  "
                >
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </UiProgressBar>
              </UiProgress>
              <UiButton
                variant="success"
                @click.prevent="processTurn('higher', 'third_round')"
                :disabled="
                  gameSession.state !== 'second_round' || waitingForResponse
                "
              >
                <iconify-icon icon="fa6-solid:arrow-up" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.higher")
                }}</span>
              </UiButton>
              <UiButton
                variant="danger"
                @click.prevent="processTurn('lower', 'third_round')"
                :disabled="
                  gameSession.state !== 'second_round' || waitingForResponse
                "
              >
                <iconify-icon icon="fa6-solid:arrow-down" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.lower")
                }}</span>
              </UiButton>
              <UiButton
                variant="secondary"
                @click.prevent="processTurn('leave', 'won')"
                :disabled="
                  gameSession.state !== 'second_round' || waitingForResponse
                "
              >
                {{ $t("games.game.ride_the_bus.actions.quit") }}
              </UiButton>
            </div>

            <div class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center">
              1:2
            </div>
          </div>

          <div
            class="flex min-w-0 shrink grow basis-0 flex-col justify-between gap-2 transition-opacity duration-500 ease-in-out"
            :class="gameSession.state !== 'third_round' ? 'opacity-0' : ''"
          >
            <div class="flex flex-col gap-2">
              <UiProgress :max="msPerTurn">
                <UiProgressBar
                  :value="
                    gameSession.state === 'third_round'
                      ? gameSession.msLeft
                      : msPerTurn
                  "
                >
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </UiProgressBar>
              </UiProgress>
              <UiButton
                variant="primary"
                @click.prevent="processTurn('inside', 'fourth_round')"
                :disabled="
                  gameSession.state !== 'third_round' || waitingForResponse
                "
              >
                <iconify-icon icon="fa7-solid:sign-in" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.inside")
                }}</span>
              </UiButton>
              <UiButton
                variant="danger"
                @click.prevent="processTurn('outside', 'fourth_round')"
                :disabled="
                  gameSession.state !== 'third_round' || waitingForResponse
                "
              >
                <iconify-icon icon="fa7-solid:sign-out" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.outside")
                }}</span>
              </UiButton>
              <UiButton
                variant="secondary"
                @click.prevent="processTurn('leave', 'won')"
                :disabled="
                  gameSession.state !== 'third_round' || waitingForResponse
                "
              >
                {{ $t("games.game.ride_the_bus.actions.quit") }}
              </UiButton>
            </div>

            <div class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center">
              1:3
            </div>
          </div>

          <div
            class="flex min-w-0 shrink grow basis-0 flex-col justify-between gap-2 transition-opacity duration-500 ease-in-out"
            :class="gameSession.state !== 'fourth_round' ? 'opacity-0' : ''"
          >
            <div class="flex flex-col gap-2">
              <UiProgress :max="msPerTurn">
                <UiProgressBar
                  :value="
                    gameSession.state === 'fourth_round'
                      ? gameSession.msLeft
                      : msPerTurn
                  "
                >
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </UiProgressBar>
              </UiProgress>
              <UiButton
                variant="primary"
                @click.prevent="processTurn('clubs', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <iconify-icon icon="mdi:suit-clubs" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.clubs")
                }}</span>
              </UiButton>
              <UiButton
                variant="danger"
                @click.prevent="processTurn('diamonds', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <iconify-icon icon="mdi:suit-diamonds" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.diamonds")
                }}</span>
              </UiButton>
              <UiButton
                variant="primary"
                @click.prevent="processTurn('spades', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <iconify-icon icon="mdi:suit-spades" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.spades")
                }}</span>
              </UiButton>
              <UiButton
                variant="danger"
                @click.prevent="processTurn('hearts', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <iconify-icon icon="mdi:suit-hearts" class="md:mr-1" />
                <span class="hidden md:inline-block">{{
                  $t("games.game.ride_the_bus.actions.hearts")
                }}</span>
              </UiButton>
              <UiButton
                variant="secondary"
                @click.prevent="processTurn('leave', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                {{ $t("games.game.ride_the_bus.actions.quit") }}
              </UiButton>
            </div>

            <div class="w-full rounded-lg bg-dark-gray-600/50 p-1 text-center">
              1:7
            </div>
          </div>
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

@media (max-width: 576px) {
  .playing-card {
    max-width: 6em;
  }
}
</style>
