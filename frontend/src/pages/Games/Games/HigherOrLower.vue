<script setup lang="ts">
import { ref } from "vue";
import {
  faArrowDown,
  faArrowUp,
  faClose,
  faCopy,
  faDice,
  faInfo,
  faMinus,
} from "@node_modules/@fortawesome/free-solid-svg-icons";
import { computed, onBeforeUnmount } from "@node_modules/vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController";
import Icon from "@components/Icon.vue";
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
const { show } = useToastController();
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
  show?.({
    props: {
      body: message,
      variant: variant,
      interval: 5000,
      pos: "bottom-start",
    },
  });
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
  <BCard
    class="blur-box border-0 overflow-hidden"
    header-class="d-flex align-items-center justify-content-between"
    body-class="d-flex flex-column p-0"
  >
    <template #header>
      <h4 class="m-0">
        <font-awesome-icon :icon="faDice" />
        {{ $t("games.game.higher_lower.title") }}
      </h4>

      <BButton variant="tertiary" class="btn-square opacity-0">
        <font-awesome-icon :icon="faCopy" />
      </BButton>
    </template>

    <div
      class="w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 position-relative p-3"
    >
      <BButton
        variant="primary"
        class="btn-circle position-absolute top-0 end-0 m-2 z-3"
        @click="areRulesOpen = true"
      >
        <font-awesome-icon :icon="faInfo" />
      </BButton>

      <BModal
        v-model="areRulesOpen"
        header-class="justify-content-between align-items-center"
        :hide-footer="true"
        scrollable
        size="xl"
        centered
      >
        <vue-markdown :source="$t('games.game.higher_lower.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("games.game.higher_lower.title") }}</h2>

          <BButton
            variant="tertiary"
            class="btn-square text-light"
            @click="areRulesOpen = false"
          >
            <font-awesome-icon :icon="faClose" />
          </BButton>
        </template>
      </BModal>

      <Transition>
        <div
          class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 bg-black bg-opacity-50 z-2"
          v-if="
            gameSession.state !== 'first_round' &&
            gameSession.state !== 'still_playing'
          "
        >
          <div
            class="d-flex flex-column col-10 col-md-5 col-lg-4 bg-dark-gray-600 bg-opacity-100 rounded-3 p-2 gap-2"
          >
            <h1 class="text-center" v-if="gameSession.state !== 'not_started'">
              {{
                gameSession.state === "lost"
                  ? $t("games.game.higher_lower.outcomes.lost")
                  : $t("games.game.higher_lower.outcomes.won")
              }}
            </h1>

            <BFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-center">
                {{ $t("games.game.higher_lower.bet") }}: {{ gameSession.bet }}
              </span>
              <BInput
                id="input-2"
                type="range"
                v-model="gameSession.bet"
                min="10"
                :max="balance < 100 ? balance : 100"
                :state="validateBet"
              />
              <BFormInvalidFeedback :state="validateBet">
                {{ $t("games.not_enough_tokens") }}
              </BFormInvalidFeedback>
            </BFormGroup>

            <h5
              class="rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center mb-0"
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

            <BButton
              variant="primary"
              class="btn-lg"
              @click.prevent="gameEnd"
              v-if="gameSession.state !== 'not_started'"
            >
              {{ $t("games.game.higher_lower.actions.play_again") }}
            </BButton>
            <BButton
              variant="primary"
              class="btn-lg"
              @click.prevent="start"
              v-else
              :disabled="
                !validateBet ||
                waitingForResponse ||
                gameSession.state !== 'not_started'
              "
            >
              {{ $t("games.game.higher_lower.actions.start") }}
            </BButton>
          </div>
        </div>
      </Transition>

      <div class="d-flex flex-column gap-2">
        <div class="d-flex justify-content-center align-items-center gap-2">
          <div class="d-flex flex-column">
            <img
              :src="'/files/images/games/cards/' + gameSession.card + '.svg'"
              :alt="gameSession.card"
              class="img-fluid"
              @load="cardLoaded"
            />
          </div>
          <div class="d-flex flex-column gap-2 col-3">
            <BButton
              variant="success"
              @click.prevent="processTurn('higher', 'still_playing')"
              :disabled="
                (gameSession.state !== 'first_round' &&
                  gameSession.state !== 'still_playing') ||
                waitingForResponse
              "
            >
              <font-awesome-icon :icon="faArrowUp" />
            </BButton>
            <BButton
              variant="warning"
              @click.prevent="processTurn('draw', 'still_playing')"
              :disabled="
                (gameSession.state !== 'first_round' &&
                  gameSession.state !== 'still_playing') ||
                waitingForResponse
              "
            >
              <font-awesome-icon :icon="faMinus" />
            </BButton>
            <BButton
              variant="danger"
              @click.prevent="processTurn('lower', 'still_playing')"
              :disabled="
                (gameSession.state !== 'first_round' &&
                  gameSession.state !== 'still_playing') ||
                waitingForResponse
              "
            >
              <font-awesome-icon :icon="faArrowDown" />
            </BButton>
            <BButton
              variant="primary"
              @click.prevent="processTurn('leave', 'won')"
              :disabled="
                gameSession.state !== 'still_playing' || waitingForResponse
              "
            >
              {{ $t("games.game.higher_lower.actions.quit") }}
            </BButton>
          </div>
        </div>

        <BProgress :max="msPerTurn">
          <BProgressBar :value="gameSession.msLeft">
            <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
          </BProgressBar>
        </BProgress>

        <div class="d-flex gap-2">
          <h3
            class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center mb-0"
          >
            {{ gameSession.state === "not_started" ? 0 : gameSession.bet }}
          </h3>

          <h3
            class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-2 d-flex text-center align-items-center text-light col-3 mb-0"
          >
            <Icon icon="playing-cards" />
            {{ gameSession.leftOverCards }}
          </h3>
        </div>
      </div>
    </div>
  </BCard>
</template>

<style scoped lang="scss">
.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
