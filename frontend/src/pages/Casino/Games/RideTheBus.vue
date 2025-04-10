<script setup lang="ts">
import {
  faArrowDown,
  faArrowRightFromBracket,
  faArrowRightToBracket,
  faArrowUp,
  faClose,
  faCopy,
  faDice,
  faInfo
} from "@node_modules/@fortawesome/free-solid-svg-icons";
import Icon from "@components/Icon.vue";
import { computed, ref } from "@node_modules/vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController/index";
import { useI18n } from "@node_modules/vue-i18n";
import axios from "@node_modules/axios";

interface RideTheBusProps {
  balance: number;
}

type GameState = "not_started" | "first_round" | "second_round" | "third_round" | "fourth_round" | "won" | "lost";

interface GameSession {
  sessionId: string;
  state: GameState;
  cards: string[];
  bet: number;
  initialBet: number;
}

const i18n = useI18n();
const { show } = useToastController();
const emit = defineEmits({
  balanceChange: null
});

const { balance } = defineProps<RideTheBusProps>();

const gameSession = ref<GameSession>({
  sessionId: "",
  state: "not_started",
  cards: ["back", "back", "back", "back"],
  bet: 10,
  initialBet: 10
});
const newGameSession = ref<GameSession | undefined>(undefined);

const waitingForResponse = ref(false);
const areRulesOpen = ref(false);

const cardLoaded = (from_round: GameState) => {
  if (gameSession.value && gameSession.value.state !== from_round) return;

  gameSession.value = newGameSession.value ? newGameSession.value : gameSession.value;
  waitingForResponse.value = false;

  if (gameSession.value.state === "won")
    emit("balanceChange", gameSession.value["bet"]);
};

const validateBet = computed(() => {
  return gameSession.value["bet"] >= 10 && gameSession.value["bet"] <= 500 && gameSession.value["bet"] <= balance;
});

const showToast = (message: string, variant: "success" | "danger") => {
  show?.({
    props: {
      body: message,
      variant: variant,
      interval: 5000,
      pos: "bottom-start"
    }
  });
};

const start = async () => {
  waitingForResponse.value = true;

  axios.post(`/casino/api/ride-the-bus/start/`, {
    bet: Number(gameSession.value["bet"])
  })
    .then(response => {
      const data = response.data;

      emit("balanceChange", -data["initial_bet"]);

      gameSession.value = {
        sessionId: data["session_id"],
        state: "first_round",
        cards: gameSession.value["cards"],
        bet: data["bet"],
        initialBet: data["initial_bet"]
      };

      waitingForResponse.value = false;
    })
    .catch(error => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

type turnType = 'red' | 'black' | 'higher' | 'lower' | 'inside' | 'outside' | 'hearts' | 'diamonds' | 'spades' | 'clubs' | 'leave';

const processTurn = (type: turnType, gameState: GameState) => {
  waitingForResponse.value = true;

  axios.post(`/casino/api/ride-the-bus/${type}/`, {
    session: gameSession.value["sessionId"]
  })
    .then(response => {
      const data = response.data;
      const cardIndex = gameSession.value["cards"].findIndex(card => card === "back");

      gameSession.value["cards"][cardIndex] = data["card"];
      newGameSession.value = {
        sessionId: data["session_id"],
        state: data["bet"] <= 0 ? "lost" : gameState,
        cards: gameSession.value["cards"],
        bet: data["bet"],
        initialBet: data["initial_bet"]
      };
    })
    .catch(error => {
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
    initialBet: gameSession.value["initialBet"]
  };
  newGameSession.value = undefined;
};
</script>

<template>
  <BCard class="bg-grey-100 bg-opacity-50 overflow-hidden" header-class="d-flex align-items-center justify-content-between" body-class="d-flex flex-column p-0">
    <template #header>
      <h4 class="m-0">
        <font-awesome-icon :icon="faDice" />
        {{ $t("casino.game.ride_the_bus.title") }}
      </h4>

      <BButton variant="tertiary" class="btn-square opacity-0">
        <font-awesome-icon :icon="faCopy" />
      </BButton>
    </template>

    <div class="w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 position-relative p-3">
      <BButton class="btn-circle position-absolute top-0 end-0 m-2 z-3" @click="areRulesOpen = true">
        <font-awesome-icon :icon="faInfo" />
      </BButton>

      <BModal data-bs-theme="dark" v-model="areRulesOpen" header-class="justify-content-between align-items-center"
              :hide-footer="true" :no-close-on-backdrop="true" scrollable :no-close-on-esc="true" size="xl" centered>
        <vue-markdown :source="$t('casino.game.ride_the_bus.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("casino.game.ride_the_bus.title") }}</h2>

          <BButton variant="tertiary" class="btn-square text-light" @click="areRulesOpen = false">
            <font-awesome-icon :icon="faClose" />
          </BButton>
        </template>
      </BModal>

      <Transition>
        <div class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 bg-black bg-opacity-50 z-2"
             v-if="gameSession.state === 'not_started' || gameSession.state === 'won' || gameSession.state === 'lost'">
          <div class="d-flex flex-column col-3 bg-grey-100 bg-opacity-100 rounded-3 p-2 gap-2">
            <h1 class="text-white text-center" v-if="gameSession.state !== 'not_started'">
              {{ gameSession.state === "lost" ? $t("casino.game.ride_the_bus.outcomes.lost") : $t("casino.game.ride_the_bus.outcomes.won") }}
            </h1>

            <BFormGroup id="input-group-2" label-for="input-2" v-else>
            <span class="text-white text-center">
              {{ $t("casino.game.ride_the_bus.bet") }}: {{ gameSession.bet }}
            </span>
              <BInput id="input-2" type="range" v-model="gameSession.bet" min="10" :max="balance < 500 ? balance : 500" :state="validateBet" />
              <BFormInvalidFeedback :state="validateBet">
                {{ $t("casino.not_enough_tokens") }}
              </BFormInvalidFeedback>
            </BFormGroup>

            <BButton variant="primary" class="btn-lg" @click.prevent="gameEnd" v-if="gameSession.state !== 'not_started'">
              {{ $t("casino.game.ride_the_bus.actions.play_again") }}
            </BButton>
            <BButton variant="primary" class="btn-lg" @click.prevent="start" v-else :disabled="!validateBet">
              {{ $t("casino.game.ride_the_bus.actions.start") }}
            </BButton>
          </div>
        </div>
      </Transition>

      <div class="d-flex flex-column gap-2">
        <div class="d-flex justify-content-center align-items-center gap-2">
          <img :src="'/files/images/casino/cards/' + gameSession.cards[0] + '.svg'" :alt="gameSession.cards[0]" class="img-fluid" @load="cardLoaded('first_round')" />
          <img :src="'/files/images/casino/cards/' + gameSession.cards[1] + '.svg'" :alt="gameSession.cards[1]" class="img-fluid" @load="cardLoaded('second_round')" />
          <img :src="'/files/images/casino/cards/' + gameSession.cards[2] + '.svg'" :alt="gameSession.cards[2]" class="img-fluid" @load="cardLoaded('third_round')" />
          <img :src="'/files/images/casino/cards/' + gameSession.cards[3] + '.svg'" :alt="gameSession.cards[3]" class="img-fluid" @load="cardLoaded('fourth_round')" />
        </div>

        <div class="d-flex">
          <h3 class="bg-grey-100 rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center m-0">
            {{ gameSession.state === "not_started" ? 0 : gameSession.bet }}
          </h3>
        </div>

        <div class="d-flex gap-2">
          <div class="d-flex flex-column gap-2 w-100 transition-opacity"
               :class="gameSession.state !== 'first_round' && gameSession.state !== 'not_started' ? 'opacity-0' : ''">
            <BButton variant="danger" @click.prevent="processTurn('red', 'second_round')" :disabled="gameSession.state !== 'first_round' || waitingForResponse">
              <Icon icon="diamonds" />
              <Icon icon="hearts" class="me-1" />
              {{ $t("casino.game.ride_the_bus.actions.red") }}
              <Icon icon="hearts" class="ms-1" />
              <Icon icon="diamonds" />
            </BButton>
            <BButton variant="primary" @click.prevent="processTurn('black', 'second_round')" :disabled="gameSession.state !== 'first_round' || waitingForResponse">
              <Icon icon="spades" />
              <Icon icon="clubs" class="me-1" />
              {{ $t("casino.game.ride_the_bus.actions.black") }}
              <Icon icon="clubs" class="ms-1" />
              <Icon icon="spades" />
            </BButton>
          </div>

          <div class="d-flex flex-column gap-2 w-100 transition-opacity" :class="gameSession.state !== 'second_round' ? 'opacity-0' : ''">
            <BButton variant="success" @click.prevent="processTurn('higher', 'third_round')" :disabled="gameSession.state !== 'second_round' || waitingForResponse">
              <font-awesome-icon :icon="faArrowUp" class="me-1" />
              {{ $t("casino.game.ride_the_bus.actions.higher") }}
            </BButton>
            <BButton variant="danger" @click.prevent="processTurn('lower', 'third_round')" :disabled="gameSession.state !== 'second_round' || waitingForResponse">
              <font-awesome-icon :icon="faArrowDown" class="me-1" />
              {{ $t("casino.game.ride_the_bus.actions.lower") }}
            </BButton>
            <BButton variant="secondary" @click.prevent="processTurn('leave', 'won')" :disabled="gameSession.state !== 'second_round' || waitingForResponse">
              {{ $t("casino.game.ride_the_bus.actions.quit") }}
            </BButton>
          </div>

          <div class="d-flex flex-column gap-2 w-100 transition-opacity" :class="gameSession.state !== 'third_round' ? 'opacity-0' : ''">
            <BButton variant="primary" @click.prevent="processTurn('inside', 'fourth_round')" :disabled="gameSession.state !== 'third_round' || waitingForResponse">
              <font-awesome-icon :icon="faArrowRightToBracket" class="me-1" />
              {{ $t("casino.game.ride_the_bus.actions.inside") }}
            </BButton>
            <BButton variant="danger" @click.prevent="processTurn('outside', 'fourth_round')" :disabled="gameSession.state !== 'third_round' || waitingForResponse">
              <font-awesome-icon :icon="faArrowRightFromBracket" class="me-1" />
              {{ $t("casino.game.ride_the_bus.actions.outside") }}
            </BButton>
            <BButton variant="secondary" @click.prevent="processTurn('leave', 'won')" :disabled="gameSession.state !== 'third_round' || waitingForResponse">
              {{ $t("casino.game.ride_the_bus.actions.quit") }}
            </BButton>
          </div>

          <div class="d-flex flex-column gap-2 w-100 transition-opacity" :class="gameSession.state !== 'fourth_round' ? 'opacity-0' : ''">
            <BButton variant="primary" @click.prevent="processTurn('clubs', 'won')" :disabled="gameSession.state !== 'fourth_round' || waitingForResponse">
              <Icon icon="clubs" />
              {{ $t("casino.game.ride_the_bus.actions.clubs") }}
            </BButton>
            <BButton variant="danger" @click.prevent="processTurn('diamonds', 'won')" :disabled="gameSession.state !== 'fourth_round' || waitingForResponse">
              <Icon icon="diamonds" />
              {{ $t("casino.game.ride_the_bus.actions.diamonds") }}
            </BButton>
            <BButton variant="primary" @click.prevent="processTurn('spades', 'won')" :disabled="gameSession.state !== 'fourth_round' || waitingForResponse">
              <Icon icon="spades" />
              {{ $t("casino.game.ride_the_bus.actions.spades") }}
            </BButton>
            <BButton variant="danger" @click.prevent="processTurn('hearts', 'won')" :disabled="gameSession.state !== 'fourth_round' || waitingForResponse">
              <Icon icon="hearts" />
              {{ $t("casino.game.ride_the_bus.actions.hearts") }}
            </BButton>
            <BButton variant="secondary" @click.prevent="processTurn('leave', 'won')" :disabled="gameSession.state !== 'fourth_round' || waitingForResponse">
              {{ $t("casino.game.ride_the_bus.actions.quit") }}
            </BButton>
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
</style>
