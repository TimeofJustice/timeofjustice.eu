<script setup lang="ts">
import { ref } from "vue";
import { faArrowDown, faArrowUp, faClose, faCopy, faDice, faInfo, faMinus } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { computed } from "@node_modules/vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController";
import Icon from "@components/Icon.vue";
import { useI18n } from "@node_modules/vue-i18n";

interface GameSession {
  sessionId: string;
  state: 'not_started' | 'first_round' | 'still_playing' | 'won' | 'lost';
  card: string;
  bet: number;
  initialBet: number;
  leftOverCards: number;
}

const gameSession = ref<GameSession>({
  sessionId: '',
  state: 'not_started',
  card: 'back',
  bet: 10,
  initialBet: 10,
  leftOverCards: 52,
});
const newGameSession = ref<GameSession | undefined>(undefined);

const cardLoaded = () => {
  gameSession.value = newGameSession.value? newGameSession.value : gameSession.value;
  waitingForResponse.value = false;

  if (gameSession.value.state === 'won')
    emit('balanceChange', gameSession.value['bet']);
};

interface HigherLowerProps {
  balance: number;
}

const { show } = useToastController()

const { balance } = defineProps<HigherLowerProps>();

const i18n = useI18n();

const waitingForResponse = ref(false);

const emit = defineEmits({
  balanceChange: null,
})

const start = async () => {
  waitingForResponse.value = true;

  const response = await fetch(`/casino/api/higher-lower/start/${gameSession.value['bet']}`);
  if (!response.ok) {
    const body = await response.json();

    show?.({
      props: {
        body: i18n.t(body.error),
        variant: "danger",
        interval: 5000,
        pos: "bottom-start",
      }
    });

    waitingForResponse.value = false;
  }

  const data = await response.json();

  emit('balanceChange', -data["initial_bet"]);

  gameSession.value['card'] = data["card"];
  newGameSession.value = {
    sessionId: data["session_id"],
    state: 'first_round',
    card: data["card"],
    bet: data["bet"],
    initialBet: data["initial_bet"],
    leftOverCards: data["cards_left"],
  };
}

const higher = async () => {
  waitingForResponse.value = true;

  const response = await fetch(`/casino/api/higher-lower/higher/${gameSession.value['sessionId']}`);
  if (!response.ok) {
    const body = await response.json();

    show?.({
      props: {
        body: i18n.t(body.error),
        variant: "danger",
        interval: 5000,
        pos: "bottom-start",
      }
    });

    waitingForResponse.value = false;
  }

  const data = await response.json();

  gameSession.value['card'] = data["card"];
  newGameSession.value = {
    sessionId: data["session_id"],
    state: data["bet"] <= 0 ? 'lost' : 'still_playing',
    card: data["card"],
    bet: data["bet"],
    initialBet: data["initial_bet"],
    leftOverCards: data["cards_left"],
  };
}

const lower = async () => {
  waitingForResponse.value = true;

  const response = await fetch(`/casino/api/higher-lower/lower/${gameSession.value['sessionId']}`);
  if (!response.ok) {
    const body = await response.json();

    show?.({
      props: {
        body: i18n.t(body.error),
        variant: "danger",
        interval: 5000,
        pos: "bottom-start",
      }
    });

    waitingForResponse.value = false;
  }

  const data = await response.json();

  gameSession.value['card'] = data["card"];
  newGameSession.value = {
    sessionId: data["session_id"],
    state: data["bet"] <= 0 ? 'lost' : 'still_playing',
    card: data["card"],
    bet: data["bet"],
    initialBet: data["initial_bet"],
    leftOverCards: data["cards_left"],
  };
}

const draw = async () => {
  waitingForResponse.value = true;

  const response = await fetch(`/casino/api/higher-lower/draw/${gameSession.value['sessionId']}`);
  if (!response.ok) {
    const body = await response.json();

    show?.({
      props: {
        body: i18n.t(body.error),
        variant: "danger",
        interval: 5000,
        pos: "bottom-start",
      }
    });

    waitingForResponse.value = false;
  }

  const data = await response.json();

  gameSession.value['card'] = data["card"];
  newGameSession.value = {
    sessionId: data["session_id"],
    state: data["bet"] <= 0 ? 'lost' : 'still_playing',
    card: data["card"],
    bet: data["bet"],
    initialBet: data["initial_bet"],
    leftOverCards: data["cards_left"],
  };
}

const leave = async () => {
  waitingForResponse.value = true;

  const response = await fetch(`/casino/api/higher-lower/leave/${gameSession.value['sessionId']}`);
  if (!response.ok) {
    const body = await response.json();

    show?.({
      props: {
        body: i18n.t(body.error),
        variant: "danger",
        interval: 5000,
        pos: "bottom-start",
      }
    });

    waitingForResponse.value = false;
  }

  const data = await response.json();

  if (data["cards_left"] > 0) {
    gameSession.value['card'] = data["card"];
    newGameSession.value = {
      sessionId: '',
      state: 'won',
      card: data["card"],
      bet: data["bet"],
      initialBet: data["initial_bet"],
      leftOverCards: data["cards_left"],
    };
  } else {
    gameSession.value = {
      sessionId: '',
      state: 'won',
      card: data["card"],
      bet: data["bet"],
      initialBet: data["initial_bet"],
      leftOverCards: data["cards_left"],
    };
  }
}

const game_end = () => {
  gameSession.value = {
    sessionId: '',
    state: 'not_started',
    card: 'back',
    bet: gameSession.value['initialBet'],
    initialBet: gameSession.value['initialBet'],
    leftOverCards: 52,
  }
  newGameSession.value = undefined;
}

const validation = computed(() => {
  const numericBalance = Number(balance);

  return gameSession.value["bet"] >= 10 && gameSession.value["bet"] <= 100 && gameSession.value["bet"] <= numericBalance;
});

const areRulesOpen = ref(false);
</script>

<template>
  <BCard class="bg-grey-100 bg-opacity-50 overflow-hidden" header-class="d-flex align-items-center justify-content-between" body-class="d-flex flex-column p-0">
    <template #header>
      <h4 class="m-0">
        <font-awesome-icon :icon="faDice"/>
        Higher or Lower
      </h4>

      <BButton variant="tertiary" class="btn-square opacity-0">
        <font-awesome-icon :icon="faCopy" />
      </BButton>
    </template>

    <div class="w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 position-relative p-3">
      <BButton class="btn-circle position-absolute top-0 end-0 m-2 z-3" @click="areRulesOpen = true">
        <font-awesome-icon :icon="faInfo"/>
      </BButton>

      <BModal data-bs-theme="dark" v-model="areRulesOpen" header-class="justify-content-between align-items-center"
              :hide-footer="true" :no-close-on-backdrop="true" scrollable :no-close-on-esc="true" size="xl" centered>
        <vue-markdown :source="$t('casino.game.higher_lower.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t('casino.game.higher_lower.title') }}</h2>

          <BButton variant="tertiary" class="btn-square text-light" @click="areRulesOpen = false">
            <font-awesome-icon :icon="faClose" />
          </BButton>
        </template>
      </BModal>

      <div class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 bg-black bg-opacity-50 z-2" v-if="gameSession.state !== 'first_round' && gameSession.state !== 'still_playing'">
        <div class="d-flex flex-column col-3 bg-grey-100 bg-opacity-100 rounded-3 p-2 gap-2">
          <h1 class="text-white text-center" v-if="gameSession.state !== 'not_started'">
            {{ gameSession.state === 'lost' ? $t('casino.game.higher_lower.outcomes.lost') : $t('casino.game.higher_lower.outcomes.won') }}
          </h1>

          <BFormGroup id="input-group-2" label-for="input-2" v-else>
        <span class="text-white text-center">
          {{ $t('casino.game.higher_lower.bet') }}: {{ gameSession.bet }}
        </span>
            <BInput id="input-2" type="range" v-model="gameSession.bet" min="10" :max="balance < 100 ? balance : 100" :state="validation" />
            <BFormInvalidFeedback :state="validation">
              {{ $t('casino.not_enough_tokens') }}
            </BFormInvalidFeedback>
          </BFormGroup>

          <BButton variant="primary" class="btn-lg" @click.prevent="game_end" v-if="gameSession.state !== 'not_started'">
            {{ $t('casino.game.higher_lower.actions.play_again') }}
          </BButton>
          <BButton variant="primary" class="btn-lg" @click.prevent="start" v-else :disabled="!validation">
            {{ $t('casino.game.higher_lower.actions.start') }}
          </BButton>
        </div>
      </div>

      <div class="d-flex flex-column gap-2">
        <div class="d-flex justify-content-center align-items-center gap-2">
          <div class="d-flex flex-column">
            <img :src="'/files/images/casino/cards/' + gameSession.card + '.svg'" :alt="gameSession.card" class="img-fluid" @load="cardLoaded" />
          </div>
          <div class="d-flex flex-column gap-2 col-3">
            <BButton variant="success" @click.prevent="higher" :disabled="(gameSession.state !== 'first_round' && gameSession.state !== 'still_playing') || waitingForResponse">
              <font-awesome-icon :icon="faArrowUp"/>
            </BButton>
            <BButton variant="warning" @click.prevent="draw" :disabled="(gameSession.state !== 'first_round' && gameSession.state !== 'still_playing') || waitingForResponse">
              <font-awesome-icon :icon="faMinus"/>
            </BButton>
            <BButton variant="danger" @click.prevent="lower" :disabled="(gameSession.state !== 'first_round' && gameSession.state !== 'still_playing') || waitingForResponse">
              <font-awesome-icon :icon="faArrowDown"/>
            </BButton>
            <BButton variant="primary" @click.prevent="leave" :disabled="(gameSession.state !== 'still_playing') || waitingForResponse">
              {{ $t('casino.game.higher_lower.actions.quit') }}
            </BButton>
          </div>
        </div>

        <div class="d-flex gap-2">
          <h3 class="bg-grey-100 rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center">
            {{ gameSession.state === 'not_started' ? 0 : gameSession.bet }}
          </h3>

          <h3 class="bg-grey-100 rounded-3 p-2 d-flex text-center align-items-center text-light col-3">
            <Icon icon="playing-cards"/>
            {{ gameSession.leftOverCards }}
          </h3>
        </div>
      </div>
    </div>
  </BCard>
</template>
