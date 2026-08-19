<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "@node_modules/vue";
import { useI18n } from "@node_modules/vue-i18n";
import { useToast } from "@composables/toast";
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
const { create } = useToast();
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
  create({ body: message, variant, position: "bottom-start" });
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
  <UiCard
    class="overflow-hidden border-0"
    header-class="flex items-center justify-between"
    body-class="flex flex-col"
    no-padding
  >
    <template #header>
      <h4 class="m-0">
        <iconify-icon icon="fa7-solid:dice" />
        {{ $t("games.game.black_jack.title") }}
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
        <vue-markdown :source="$t('games.game.black_jack.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("games.game.black_jack.title") }}</h2>

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
          v-if="gameSession.state !== 'playing'"
        >
          <div
            class="flex w-5/6 shrink-0 flex-col gap-2 rounded-lg bg-dark-gray-600 p-2 md:w-5/12 lg:w-1/3"
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

            <UiFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-center">
                {{ $t("games.game.black_jack.bet") }}: {{ gameSession.bet }}
              </span>
              <UiInput
                id="input-2"
                type="range"
                v-model="gameSession.bet"
                min="10"
                :max="balance < 1000 ? balance : 1000"
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
              @click.prevent="end"
              v-if="gameSession.state !== 'not_started'"
              size="lg"
            >
              {{ $t("games.game.black_jack.actions.play_again") }}
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
              {{ $t("games.game.black_jack.actions.start") }}
            </UiButton>
          </div>
        </div>
      </Transition>

      <div class="flex w-full shrink-0 flex-col gap-2">
        <div class="flex gap-2 pr-2">
          <h3
            class="flex w-2/3 shrink-0 flex-col gap-2 rounded-lg bg-dark-gray-600/50 p-2 text-center md:w-3/4"
          >
            {{
              gameSession.state === "not_started" ? 0 : gameSession.dealerScore
            }}
          </h3>
        </div>

        <div class="flex items-center justify-center gap-2">
          <div class="flex w-2/3 shrink-0 flex-col gap-2 md:w-3/4">
            <div class="flex justify-center overflow-hidden">
              <div
                class="w-1/12 shrink-0 overflow-hidden"
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
                class="relative overflow-hidden"
                :class="{
                  'w-1/12 shrink-0': index < shownDealerCards.length - 1,
                }"
              >
                <v-lazy-image
                  class="playing-card"
                  :src="'/files/images/games/cards/' + card + '.svg'"
                  src-placeholder="/files/images/games/cards/back.svg"
                  @load="cardLoaded(card)"
                />
              </div>
            </div>

            <div class="flex w-full shrink-0 justify-center overflow-hidden">
              <div
                class="w-1/12 shrink-0 overflow-hidden"
                v-if="shownCards.length < 2"
              >
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
                :class="{ 'w-1/12 shrink-0': index < shownCards.length - 1 }"
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

          <div class="flex w-1/3 shrink-0 flex-col gap-2 md:w-1/4">
            <UiProgress :max="msPerTurn">
              <UiProgressBar :value="gameSession.msLeft">
                <small>{{ (gameSession.msLeft / 1000).toFixed(0) }}s</small>
              </UiProgressBar>
            </UiProgress>
            <UiButton
              variant="success"
              @click.prevent="processTurn('hit')"
              :disabled="gameSession.state !== 'playing' || waitingForResponse"
            >
              <iconify-icon icon="fa7-solid:plus" />
              {{ $t("games.game.black_jack.actions.hit") }}
            </UiButton>
            <UiButton
              variant="danger"
              @click.prevent="processTurn('stand')"
              :disabled="gameSession.state !== 'playing' || waitingForResponse"
            >
              <iconify-icon icon="fa7-solid:hand" />
              {{ $t("games.game.black_jack.actions.stand") }}
            </UiButton>
          </div>
        </div>

        <div class="flex gap-2">
          <h3
            class="mb-0 flex w-full flex-col gap-2 rounded-lg bg-dark-gray-600/50 p-2 text-center"
          >
            {{
              gameSession.state === "not_started" ? 0 : gameSession.cardsScore
            }}
          </h3>

          <h3
            class="mb-0 flex w-1/3 shrink-0 items-center rounded-lg bg-dark-gray-600/50 p-2 text-center text-light md:w-1/4"
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
