<script setup lang="ts">
import {
  faArrowDown,
  faArrowRightFromBracket,
  faArrowRightToBracket,
  faArrowUp,
  faClose,
  faCopy,
  faDice,
  faInfo,
} from "@node_modules/@fortawesome/free-solid-svg-icons";
import Icon from "@components/Icon.vue";
import { computed, onBeforeUnmount, ref } from "@node_modules/vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController/index";
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
const { show } = useToastController();
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
  <BCard
    class="blur-box border-0 overflow-hidden"
    header-class="d-flex align-items-center justify-content-between"
    body-class="d-flex flex-column p-0"
  >
    <template #header>
      <h4 class="m-0">
        <font-awesome-icon :icon="faDice" />
        {{ $t("games.game.ride_the_bus.title") }}
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
        <vue-markdown :source="$t('games.game.ride_the_bus.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("games.game.ride_the_bus.title") }}</h2>

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
            gameSession.state === 'not_started' ||
            gameSession.state === 'won' ||
            gameSession.state === 'lost'
          "
        >
          <div
            class="d-flex flex-column col-10 col-md-5 col-lg-4 bg-dark-gray-600 rounded-3 p-2 gap-2"
          >
            <h1 class="text-center" v-if="gameSession.state !== 'not_started'">
              {{
                gameSession.state === "lost"
                  ? $t("games.game.ride_the_bus.outcomes.lost")
                  : $t("games.game.ride_the_bus.outcomes.won")
              }}
            </h1>

            <BFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-center">
                {{ $t("games.game.ride_the_bus.bet") }}: {{ gameSession.bet }}
              </span>
              <BInput
                id="input-2"
                type="range"
                v-model="gameSession.bet"
                min="10"
                :max="balance < 500 ? balance : 500"
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
              {{ $t("games.game.ride_the_bus.actions.play_again") }}
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
              {{ $t("games.game.ride_the_bus.actions.start") }}
            </BButton>
          </div>
        </div>
      </Transition>

      <div class="d-flex flex-column gap-2 w-100">
        <div class="row gx-2">
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[0] + '.svg'"
            :alt="gameSession.cards[0]"
            class="img-fluid col-3"
            @load="cardLoaded('first_round')"
          />
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[1] + '.svg'"
            :alt="gameSession.cards[1]"
            class="img-fluid col-3"
            @load="cardLoaded('second_round')"
          />
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[2] + '.svg'"
            :alt="gameSession.cards[2]"
            class="img-fluid col-3"
            @load="cardLoaded('third_round')"
          />
          <img
            :src="'/files/images/games/cards/' + gameSession.cards[3] + '.svg'"
            :alt="gameSession.cards[3]"
            class="img-fluid col-3"
            @load="cardLoaded('fourth_round')"
          />
        </div>

        <div class="d-flex">
          <h3
            class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center m-0"
          >
            {{ gameSession.state === "not_started" ? 0 : gameSession.bet }}
          </h3>
        </div>

        <div class="row gx-2">
          <div
            class="d-flex flex-column gap-2 col-3 transition-opacity justify-content-between"
            :class="
              gameSession.state !== 'first_round' &&
              gameSession.state !== 'not_started'
                ? 'opacity-0'
                : ''
            "
          >
            <div class="d-flex flex-column gap-2">
              <BProgress :max="msPerTurn">
                <BProgressBar :value="gameSession.msLeft">
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </BProgressBar>
              </BProgress>
              <BButton
                variant="danger"
                @click.prevent="processTurn('red', 'second_round')"
                :disabled="
                  gameSession.state !== 'first_round' || waitingForResponse
                "
              >
                <Icon icon="diamonds" />
                <Icon icon="hearts" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.red")
                }}</span>
                <Icon icon="hearts" class="ms-1 d-none d-md-inline-block" />
                <Icon icon="diamonds" class="d-none d-md-inline-block" />
              </BButton>
              <BButton
                variant="primary"
                @click.prevent="processTurn('black', 'second_round')"
                :disabled="
                  gameSession.state !== 'first_round' || waitingForResponse
                "
              >
                <Icon icon="spades" />
                <Icon icon="clubs" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.black")
                }}</span>
                <Icon icon="clubs" class="ms-1 d-none d-md-inline-block" />
                <Icon icon="spades" class="d-none d-md-inline-block" />
              </BButton>
            </div>

            <div
              class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-1 text-center w-100"
            >
              1:1
            </div>
          </div>

          <div
            class="d-flex flex-column gap-2 col-3 transition-opacity justify-content-between"
            :class="gameSession.state !== 'second_round' ? 'opacity-0' : ''"
          >
            <div class="d-flex flex-column gap-2">
              <BProgress :max="msPerTurn">
                <BProgressBar
                  :value="
                    gameSession.state === 'second_round'
                      ? gameSession.msLeft
                      : msPerTurn
                  "
                >
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </BProgressBar>
              </BProgress>
              <BButton
                variant="success"
                @click.prevent="processTurn('higher', 'third_round')"
                :disabled="
                  gameSession.state !== 'second_round' || waitingForResponse
                "
              >
                <font-awesome-icon :icon="faArrowUp" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.higher")
                }}</span>
              </BButton>
              <BButton
                variant="danger"
                @click.prevent="processTurn('lower', 'third_round')"
                :disabled="
                  gameSession.state !== 'second_round' || waitingForResponse
                "
              >
                <font-awesome-icon :icon="faArrowDown" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.lower")
                }}</span>
              </BButton>
              <BButton
                variant="secondary"
                @click.prevent="processTurn('leave', 'won')"
                :disabled="
                  gameSession.state !== 'second_round' || waitingForResponse
                "
              >
                {{ $t("games.game.ride_the_bus.actions.quit") }}
              </BButton>
            </div>

            <div
              class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-1 text-center w-100"
            >
              1:2
            </div>
          </div>

          <div
            class="d-flex flex-column gap-2 col-3 transition-opacity justify-content-between"
            :class="gameSession.state !== 'third_round' ? 'opacity-0' : ''"
          >
            <div class="d-flex flex-column gap-2">
              <BProgress :max="msPerTurn">
                <BProgressBar
                  :value="
                    gameSession.state === 'third_round'
                      ? gameSession.msLeft
                      : msPerTurn
                  "
                >
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </BProgressBar>
              </BProgress>
              <BButton
                variant="primary"
                @click.prevent="processTurn('inside', 'fourth_round')"
                :disabled="
                  gameSession.state !== 'third_round' || waitingForResponse
                "
              >
                <font-awesome-icon
                  :icon="faArrowRightToBracket"
                  class="me-md-1"
                />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.inside")
                }}</span>
              </BButton>
              <BButton
                variant="danger"
                @click.prevent="processTurn('outside', 'fourth_round')"
                :disabled="
                  gameSession.state !== 'third_round' || waitingForResponse
                "
              >
                <font-awesome-icon
                  :icon="faArrowRightFromBracket"
                  class="me-md-1"
                />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.outside")
                }}</span>
              </BButton>
              <BButton
                variant="secondary"
                @click.prevent="processTurn('leave', 'won')"
                :disabled="
                  gameSession.state !== 'third_round' || waitingForResponse
                "
              >
                {{ $t("games.game.ride_the_bus.actions.quit") }}
              </BButton>
            </div>

            <div
              class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-1 text-center w-100"
            >
              1:3
            </div>
          </div>

          <div
            class="d-flex flex-column gap-2 col-3 transition-opacity justify-content-between"
            :class="gameSession.state !== 'fourth_round' ? 'opacity-0' : ''"
          >
            <div class="d-flex flex-column gap-2">
              <BProgress :max="msPerTurn">
                <BProgressBar
                  :value="
                    gameSession.state === 'fourth_round'
                      ? gameSession.msLeft
                      : msPerTurn
                  "
                >
                  <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
                </BProgressBar>
              </BProgress>
              <BButton
                variant="primary"
                @click.prevent="processTurn('clubs', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <Icon icon="clubs" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.clubs")
                }}</span>
              </BButton>
              <BButton
                variant="danger"
                @click.prevent="processTurn('diamonds', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <Icon icon="diamonds" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.diamonds")
                }}</span>
              </BButton>
              <BButton
                variant="primary"
                @click.prevent="processTurn('spades', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <Icon icon="spades" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.spades")
                }}</span>
              </BButton>
              <BButton
                variant="danger"
                @click.prevent="processTurn('hearts', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                <Icon icon="hearts" class="me-md-1" />
                <span class="d-none d-md-inline-block">{{
                  $t("games.game.ride_the_bus.actions.hearts")
                }}</span>
              </BButton>
              <BButton
                variant="secondary"
                @click.prevent="processTurn('leave', 'won')"
                :disabled="
                  gameSession.state !== 'fourth_round' || waitingForResponse
                "
              >
                {{ $t("games.game.ride_the_bus.actions.quit") }}
              </BButton>
            </div>

            <div
              class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-1 text-center w-100"
            >
              1:7
            </div>
          </div>
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

.transition-opacity {
  transition: opacity 0.5s ease;
}

@media (max-width: 576px) {
  .playing-card {
    max-width: 6em;
  }
}
</style>
