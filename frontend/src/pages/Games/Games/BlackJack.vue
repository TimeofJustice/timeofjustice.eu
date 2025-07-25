<script setup lang="ts">
import {
  faClose,
  faCopy,
  faDice,
  faHand,
  faInfo,
  faPlus,
} from "@node_modules/@fortawesome/free-solid-svg-icons";
import Icon from "@components/Icon.vue";
import { computed, onBeforeUnmount, ref } from "@node_modules/vue";
import { useI18n } from "@node_modules/vue-i18n";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController/index";
import axios from "@node_modules/axios";

interface BlackJackProps {
  balance: number;
}

type GameState = "not_started" | "playing" | "won" | "lost" | "push";

interface GameSession {
  sessionId: string;
  state: GameState;
  dealerCards: string[];
  dealerScore: number;
  cards: string[];
  cardsScore: number;
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

const { balance } = defineProps<BlackJackProps>();
const msPerTurn = 15000;

const gameSession = ref<GameSession>({
  sessionId: "",
  state: "not_started",
  dealerCards: [],
  dealerScore: 0,
  cards: [],
  cardsScore: 0,
  bet: 10,
  initialBet: 10,
  leftOverCards: 52,
  msLeft: msPerTurn,
});
const newGameSession = ref<GameSession | undefined>(undefined);
const loadedImages = ref(0);
const shownCards = ref<string[]>(["back"]);
const currentShownCard = ref(0);
const shownDealerCards = ref<string[]>(["back"]);
const currentShownDealerCard = ref(0);

const waitingForResponse = ref(false);
const areRulesOpen = ref(false);

const cardLoaded = (name: string) => {
  if (name === "back") return;

  loadedImages.value++;

  if (
    loadedImages.value ===
    gameSession.value.cards.length + gameSession.value.dealerCards.length
  ) {
    gameSession.value = newGameSession.value
      ? newGameSession.value
      : gameSession.value;
    waitingForResponse.value = false;
  }

  if (gameSession.value.state === "won" || gameSession.value.state === "push")
    emit("balanceChange", gameSession.value["bet"]);
};

const validateBet = computed(() => {
  return (
    gameSession.value["bet"] >= 10 &&
    gameSession.value["bet"] <= 1000 &&
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
    .post(`/games/api/black-jack/start/`, {
      bet: Number(gameSession.value["bet"]),
    })
    .then((response) => {
      const data = response.data;

      emit("balanceChange", -data["initial_bet"]);

      gameSession.value["sessionId"] = data["session_id"];

      gameSession.value["dealerCards"] = data["dealer_cards"];
      gameSession.value["cards"] = data["cards"];
      gameSession.value["state"] = "playing";
      newGameSession.value = {
        sessionId: data["session_id"],
        state: data["status"],
        dealerCards: data["dealer_cards"],
        dealerScore: data["dealer_score"],
        cards: data["cards"],
        cardsScore: data["cards_score"],
        bet: data["bet"],
        initialBet: data["initial_bet"],
        leftOverCards: data["cards_left"],
        msLeft: msPerTurn,
      };

      shownDealerCards.value = [data["dealer_cards"][0]];
      currentShownDealerCard.value = 1;
      shownCards.value = [data["cards"][0]];
      currentShownCard.value = 1;

      if (
        currentShownDealerCard.value < gameSession.value["dealerCards"].length
      ) {
        setTimeout(() => {
          dealDealerCard();
        }, 500);
      }

      if (currentShownCard.value < gameSession.value["cards"].length) {
        setTimeout(() => {
          dealPlayerCard();
        }, 500);
      }
    })
    .catch((error) => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

type turnType = "hit" | "stand";

const processTurn = (type: turnType) => {
  waitingForResponse.value = true;

  axios
    .post(`/games/api/black-jack/${type}/`, {
      session: gameSession.value["sessionId"],
    })
    .then((response) => {
      const data = response.data;

      gameSession.value["sessionId"] = data["session_id"];

      gameSession.value["dealerCards"] = data["dealer_cards"];
      gameSession.value["cards"] = data["cards"];
      newGameSession.value = {
        sessionId: data["session_id"],
        state: data["status"],
        dealerCards: data["dealer_cards"],
        dealerScore: data["dealer_score"],
        cards: data["cards"],
        cardsScore: data["cards_score"],
        bet: data["bet"],
        initialBet: data["initial_bet"],
        leftOverCards: data["cards_left"],
        msLeft: msPerTurn,
      };

      if (
        currentShownDealerCard.value < gameSession.value["dealerCards"].length
      ) {
        setTimeout(() => {
          dealDealerCard();
        }, 500);
      }

      if (currentShownCard.value < gameSession.value["cards"].length) {
        setTimeout(() => {
          dealPlayerCard();
        }, 500);
      }
    })
    .catch((error) => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

const dealDealerCard = () => {
  if (currentShownDealerCard.value < gameSession.value["dealerCards"].length) {
    shownDealerCards.value[currentShownDealerCard.value] =
      gameSession.value["dealerCards"][currentShownDealerCard.value];
    currentShownDealerCard.value++;

    if (
      currentShownDealerCard.value < gameSession.value["dealerCards"].length
    ) {
      setTimeout(() => {
        dealDealerCard();
      }, 1000);
    }
  }
};

const dealPlayerCard = () => {
  if (currentShownCard.value < gameSession.value["cards"].length) {
    shownCards.value[currentShownCard.value] =
      gameSession.value["cards"][currentShownCard.value];
    currentShownCard.value++;

    if (currentShownCard.value < gameSession.value["cards"].length) {
      setTimeout(() => {
        dealPlayerCard();
      }, 1000);
    }
  }
};

const end = () => {
  gameSession.value = {
    sessionId: "",
    state: "not_started",
    dealerCards: [],
    dealerScore: 0,
    cards: [],
    cardsScore: 0,
    bet: gameSession.value["initialBet"],
    initialBet: gameSession.value["initialBet"],
    leftOverCards: 52,
    msLeft: msPerTurn,
  };
  newGameSession.value = undefined;
  shownCards.value = ["back"];
  shownDealerCards.value = ["back"];
  currentShownCard.value = 0;
  currentShownDealerCard.value = 0;
  loadedImages.value = 0;
};

const turnInterval = setInterval(() => {
  if (
    gameSession.value.state === "playing" &&
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
        {{ $t("games.game.black_jack.title") }}
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
        <vue-markdown :source="$t('games.game.black_jack.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("games.game.black_jack.title") }}</h2>

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
          v-if="gameSession.state !== 'playing'"
        >
          <div
            class="d-flex flex-column col-10 col-md-5 col-lg-4 bg-dark-gray-600 bg-opacity-100 rounded-3 p-2 gap-2"
          >
            <h1 class="text-center" v-if="gameSession.state !== 'not_started'">
              {{
                gameSession.state === "lost"
                  ? $t("games.game.black_jack.outcomes.lost")
                  : gameSession.state === "push"
                    ? $t("games.game.black_jack.outcomes.push")
                    : $t("games.game.black_jack.outcomes.won")
              }}
            </h1>

            <BFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-center">
                {{ $t("games.game.black_jack.bet") }}: {{ gameSession.bet }}
              </span>
              <BInput
                id="input-2"
                type="range"
                v-model="gameSession.bet"
                min="10"
                :max="balance < 1000 ? balance : 1000"
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
              @click.prevent="end"
              v-if="gameSession.state !== 'not_started'"
            >
              {{ $t("games.game.black_jack.actions.play_again") }}
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
              {{ $t("games.game.black_jack.actions.start") }}
            </BButton>
          </div>
        </div>
      </Transition>

      <div class="d-flex flex-column gap-2 col-12">
        <div class="d-flex gap-2 pe-2">
          <h3
            class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-2 d-flex flex-column gap-2 col-8 col-md-9 text-center"
          >
            {{
              gameSession.state === "not_started" ? 0 : gameSession.dealerScore
            }}
          </h3>
        </div>

        <div class="d-flex justify-content-center align-items-center gap-2">
          <div class="d-flex flex-column gap-2 col-8 col-md-9">
            <div class="d-flex overflow-hidden justify-content-center">
              <div
                class="overflow-hidden col-1"
                v-if="shownDealerCards.length < 2"
              >
                <img
                  :src="'/files/images/games/cards/back.svg'"
                  alt="back"
                  class="playing-card"
                />
              </div>
              <div
                v-for="(card, index) in shownDealerCards"
                :key="index"
                class="overflow-hidden position-relative"
                :class="{ 'col-1': index < shownDealerCards.length - 1 }"
              >
                <v-lazy-image
                  class="playing-card"
                  :src="'/files/images/games/cards/' + card + '.svg'"
                  src-placeholder="/files/images/games/cards/back.svg"
                  @load="cardLoaded(card)"
                />
              </div>
            </div>

            <div class="d-flex overflow-hidden justify-content-center col-12">
              <div class="overflow-hidden col-1" v-if="shownCards.length < 2">
                <img
                  :src="'/files/images/games/cards/back.svg'"
                  alt="back"
                  class="playing-card"
                />
              </div>
              <div
                v-for="(card, index) in shownCards"
                :key="index"
                class="overflow-hidden"
                :class="{ 'col-1': index < shownCards.length - 1 }"
              >
                <v-lazy-image
                  class="playing-card"
                  :src="'/files/images/games/cards/' + card + '.svg'"
                  src-placeholder="/files/images/games/cards/back.svg"
                  @load="cardLoaded(card)"
                />
              </div>
            </div>
          </div>

          <div class="d-flex flex-column gap-2 col-4 col-md-3">
            <BProgress :max="msPerTurn">
              <BProgressBar :value="gameSession.msLeft">
                <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
              </BProgressBar>
            </BProgress>
            <BButton
              variant="success"
              @click.prevent="processTurn('hit')"
              :disabled="gameSession.state !== 'playing' || waitingForResponse"
            >
              <font-awesome-icon :icon="faPlus" />
              {{ $t("games.game.black_jack.actions.hit") }}
            </BButton>
            <BButton
              variant="danger"
              @click.prevent="processTurn('stand')"
              :disabled="gameSession.state !== 'playing' || waitingForResponse"
            >
              <font-awesome-icon :icon="faHand" />
              {{ $t("games.game.black_jack.actions.stand") }}
            </BButton>
          </div>
        </div>

        <div class="d-flex gap-2">
          <h3
            class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center mb-0"
          >
            {{
              gameSession.state === "not_started" ? 0 : gameSession.cardsScore
            }}
          </h3>

          <h3
            class="bg-dark-gray-600 bg-opacity-50 rounded-3 p-2 d-flex text-center align-items-center text-light col-4 col-md-3 mb-0"
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

.playing-card {
  max-width: 10em;
}

.v-lazy-image {
  filter: unset;
}

.v-lazy-image-loaded {
  filter: unset;
}

@media (max-width: 576px) {
  .playing-card {
    max-width: 6em;
  }
}
</style>
