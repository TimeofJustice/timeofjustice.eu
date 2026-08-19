<script setup lang="ts">
import { ref } from "vue";
import { computed, onBeforeUnmount } from "@node_modules/vue";
import { useToast } from "@composables/toast";
import { useI18n } from "@node_modules/vue-i18n";
import axios from "@node_modules/axios";

interface HigherLowerProps {
  balance: number;
}

type GameState =
  | "not_started"
  | "first_round"
  | "still_playing"
  | "won"
  | "lost";

interface GameSession {
  sessionId: string;
  state: GameState;
  card: string;
  bet: number;
  initialBet: number;
  leftOverCards: number;
  msLeft: number;
}

const i18n = useI18n();
const { create } = useToast();
const emit = defineEmits({
  balanceChange: null,
});

const { balance } = defineProps<HigherLowerProps>();
const msPerTurn = 8000;

const gameSession = ref<GameSession>({
  sessionId: "",
  state: "not_started",
  card: "back",
  bet: 10,
  initialBet: 10,
  leftOverCards: 52,
  msLeft: msPerTurn,
});
const newGameSession = ref<GameSession | undefined>(undefined);

const waitingForResponse = ref(false);
const areRulesOpen = ref(false);

const cardLoaded = () => {
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
    gameSession.value["bet"] <= 100 &&
    gameSession.value["bet"] <= balance
  );
});

const showToast = (message: string, variant: "success" | "danger") => {
  create({ body: message, variant, position: "bottom-start" });
};

const start = async () => {
  waitingForResponse.value = true;

  axios
    .post(`/games/api/higher-lower/start/`, {
      bet: Number(gameSession.value["bet"]),
    })
    .then((response) => {
      const data = response.data;

      emit("balanceChange", -data["initial_bet"]);

      gameSession.value["card"] = data["card"];
      newGameSession.value = {
        sessionId: data["session_id"],
        state: "first_round",
        card: data["card"],
        bet: data["bet"],
        initialBet: data["initial_bet"],
        leftOverCards: data["cards_left"],
        msLeft: msPerTurn,
      };
    })
    .catch((error) => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

type turnType = "higher" | "draw" | "lower" | "leave";

const processTurn = (type: turnType, gameState: GameState) => {
  waitingForResponse.value = true;

  axios
    .post(`/games/api/higher-lower/${type}/`, {
      session: gameSession.value["sessionId"],
    })
    .then((response) => {
      const data = response.data;

      if (data["cards_left"] <= 0 && type === "leave") {
        gameSession.value = {
          sessionId: "",
          state: "won",
          card: data["card"],
          bet: data["bet"],
          initialBet: data["initial_bet"],
          leftOverCards: data["cards_left"],
          msLeft: msPerTurn,
        };
      } else {
        gameSession.value["card"] = data["card"];
        newGameSession.value = {
          sessionId: data["session_id"],
          state: data["bet"] <= 0 ? "lost" : gameState,
          card: data["card"],
          bet: data["bet"],
          initialBet: data["initial_bet"],
          leftOverCards: data["cards_left"],
          msLeft: msPerTurn,
        };
      }
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
    card: "back",
    bet: gameSession.value["initialBet"],
    initialBet: gameSession.value["initialBet"],
    leftOverCards: 52,
    msLeft: msPerTurn,
  };
  newGameSession.value = undefined;
};

const turnInterval = setInterval(() => {
  if (
    (gameSession.value.state === "first_round" ||
      gameSession.value.state === "still_playing") &&
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
    class="border-0 overflow-hidden"
    header-class="flex items-center justify-between"
    body-class="flex flex-col"
    no-padding
  >
    <template #header>
      <h4 class="m-0">
        <iconify-icon icon="fa7-solid:dice" />
        {{ $t("games.game.higher_lower.title") }}
      </h4>

      <UiButton variant="tertiary" class="opacity-0" square>
        <iconify-icon icon="iconamoon:copy-duotone" />
      </UiButton>
    </template>

    <div
      class="w-full h-full flex flex-col justify-center items-center gap-2 relative p-4"
    >
      <UiButton
        variant="primary"
        class="absolute top-0 right-0 m-2 z-3"
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
        <vue-markdown :source="$t('games.game.higher_lower.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("games.game.higher_lower.title") }}</h2>

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
          class="absolute top-0 left-0 w-full h-full flex flex-col justify-center items-center gap-2 bg-black/50 z-2"
          v-if="
            gameSession.state !== 'first_round' &&
            gameSession.state !== 'still_playing'
          "
        >
          <div
            class="flex flex-col w-5/6 shrink-0 md:w-5/12 lg:w-1/3 bg-dark-gray-600 rounded-lg p-2 gap-2"
          >
            <h1 class="text-center" v-if="gameSession.state !== 'not_started'">
              {{
                gameSession.state === "lost"
                  ? $t("games.game.higher_lower.outcomes.lost")
                  : $t("games.game.higher_lower.outcomes.won")
              }}
            </h1>

            <UiFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-center">
                {{ $t("games.game.higher_lower.bet") }}: {{ gameSession.bet }}
              </span>
              <UiInput
                id="input-2"
                type="range"
                v-model="gameSession.bet"
                min="10"
                :max="balance < 100 ? balance : 100"
                :state="validateBet"
              />
              <UiInvalidFeedback :state="validateBet">
                {{ $t("games.not_enough_tokens") }}
              </UiInvalidFeedback>
            </UiFormGroup>

            <h5
              class="rounded-lg p-2 flex flex-col gap-2 w-full text-center mb-0"
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
              {{ $t("games.game.higher_lower.actions.play_again") }}
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
              {{ $t("games.game.higher_lower.actions.start") }}
            </UiButton>
          </div>
        </div>
      </Transition>

      <div class="flex flex-col gap-2">
        <div class="flex justify-center items-center gap-2">
          <div class="flex flex-col">
            <img
              :src="'/files/images/games/cards/' + gameSession.card + '.svg'"
              :alt="gameSession.card"
              class="max-w-full h-auto"
              @load="cardLoaded"
            />
          </div>
          <div class="flex flex-col gap-2 w-1/4 shrink-0">
            <UiButton
              variant="success"
              @click.prevent="processTurn('higher', 'still_playing')"
              :disabled="
                (gameSession.state !== 'first_round' &&
                  gameSession.state !== 'still_playing') ||
                waitingForResponse
              "
            >
              <iconify-icon icon="fa6-solid:arrow-up" />
            </UiButton>
            <UiButton
              variant="warning"
              @click.prevent="processTurn('draw', 'still_playing')"
              :disabled="
                (gameSession.state !== 'first_round' &&
                  gameSession.state !== 'still_playing') ||
                waitingForResponse
              "
            >
              <iconify-icon icon="fa7-solid:minus" />
            </UiButton>
            <UiButton
              variant="danger"
              @click.prevent="processTurn('lower', 'still_playing')"
              :disabled="
                (gameSession.state !== 'first_round' &&
                  gameSession.state !== 'still_playing') ||
                waitingForResponse
              "
            >
              <iconify-icon icon="fa6-solid:arrow-down" />
            </UiButton>
            <UiButton
              variant="primary"
              @click.prevent="processTurn('leave', 'won')"
              :disabled="
                gameSession.state !== 'still_playing' || waitingForResponse
              "
            >
              {{ $t("games.game.higher_lower.actions.quit") }}
            </UiButton>
          </div>
        </div>

        <UiProgress :max="msPerTurn">
          <UiProgressBar :value="gameSession.msLeft">
            <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
          </UiProgressBar>
        </UiProgress>

        <div class="flex gap-2">
          <h3
            class="bg-dark-gray-600/50 rounded-lg p-2 flex flex-col gap-2 w-full text-center mb-0"
          >
            {{ gameSession.state === "not_started" ? 0 : gameSession.bet }}
          </h3>

          <h3
            class="bg-dark-gray-600/50 rounded-lg p-2 flex text-center items-center text-light w-1/4 shrink-0 mb-0"
          >
            <iconify-icon icon="mdi:cards-playing-heart-multiple" />
            {{ gameSession.leftOverCards }}
          </h3>
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
