<script setup lang="ts">
import { ref } from "vue";
import { faClose, faCopy, faDice, faInfo } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { computed } from "@node_modules/vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController";
import { useI18n } from "@node_modules/vue-i18n";
import axios from "@node_modules/axios";
import Dice from "@pages/Casino/components/Dice.vue";

interface HigherLowerProps {
  balance: number;
}

type GameState = 'not_started' | 'playing' | 'won' | 'lost';

interface GameSession {
  sessionId: string;
  state: GameState;
  dice: number[];
  bet: number;
  initialBet: number;
}

const i18n = useI18n();
const { show } = useToastController();
const emit = defineEmits({
  balanceChange: null,
});

const { balance } = defineProps<HigherLowerProps>();

const gameSession = ref<GameSession>({
  sessionId: '',
  state: 'not_started',
  dice: [1, 2, 3],
  bet: 10,
  initialBet: 10,
});
const newGameSession = ref<GameSession | undefined>(undefined);

const waitingForResponse = ref(false);
const areRulesOpen = ref(false);

const diceValues = ref([1, 2, 3]);

const evaluate = () => {
  rollDice(20, 40, 60)
}

const rollDice = (amount1: number, amount2: number, amount3: number) => {
  setTimeout(() => {
    const value1 = amount1 > 0 ? Math.floor(Math.random() * 6) + 1 : gameSession.value.dice[0];
    const value2 = amount2 > 0 ? Math.floor(Math.random() * 6) + 1 : gameSession.value.dice[1];
    const value3 = amount3 > 0 ? Math.floor(Math.random() * 6) + 1 : gameSession.value.dice[2];

    diceValues.value = [value1, value2, value3];

    if (amount1 > 0 || amount2 > 0 || amount3 > 0)
      rollDice(amount1 - 1, amount2 - 1, amount3 - 1);
    else {
      gameSession.value = newGameSession.value? newGameSession.value : gameSession.value;
      waitingForResponse.value = false;

      if (gameSession.value.state === 'won')
        emit('balanceChange', gameSession.value['bet']);
    }
  }, 100)
}

const validateBet = computed(() => {
  return gameSession.value["bet"] >= 10 && gameSession.value["bet"] <= 100 && gameSession.value["bet"] <= balance;
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

  axios.post(`/casino/api/sic-bo/start/`, {
    bet: Number(gameSession.value["bet"])
  })
    .then(response => {
      const data = response.data;

      emit("balanceChange", -data["initial_bet"]);

      gameSession.value.sessionId = data["session_id"];
      gameSession.value.state = 'playing';
      gameSession.value.bet = data["bet"];
      gameSession.value.initialBet = data["initial_bet"];

      waitingForResponse.value = false;
    })
    .catch(error => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
}

type totalType = 'small' | 'big' | 'total-4' | 'total-5' | 'total-6' | 'total-7' | 'total-8' | 'total-9' | 'total-10' | 'total-11' | 'total-12' | 'total-13' | 'total-14' | 'total-15' | 'total-16' | 'total-17';
type doubleType = 'double-1' | 'double-2' | 'double-3' | 'double-4' | 'double-5' | 'double-6';
type tripleType = 'triple-any' | 'triple-1' | 'triple-2' | 'triple-3' | 'triple-4' | 'triple-5' | 'triple-6';
type pairType = 'pair-1-2' | 'pair-1-3' | 'pair-1-4' | 'pair-1-5' | 'pair-1-6' | 'pair-2-3' | 'pair-2-4' | 'pair-2-5' | 'pair-2-6' | 'pair-3-4' | 'pair-3-5' | 'pair-3-6' | 'pair-4-5' | 'pair-4-6' | 'pair-5-6';
type faceType = 'face-1' | 'face-2' | 'face-3' | 'face-4' | 'face-5' | 'face-6';

const processTurn = (type: totalType | doubleType | tripleType | pairType | faceType) => {
  waitingForResponse.value = true;

  axios.post(`/casino/api/sic-bo/${type}/`, {
    session: gameSession.value["sessionId"]
  })
    .then(response => {
      const data = response.data;

      gameSession.value.dice = data["dice"];
      newGameSession.value = {
        sessionId: data["session_id"],
        state: data['bet'] === 0 ? 'lost' : 'won',
        dice: data["dice"],
        bet: data["bet"],
        initialBet: data["initial_bet"],
      };

      evaluate();
    })
    .catch(error => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

const gameEnd = () => {
  gameSession.value = {
    sessionId: '',
    state: 'not_started',
    dice: [],
    bet: gameSession.value['initialBet'],
    initialBet: gameSession.value['initialBet'],
  }
  diceValues.value = [1, 2, 3];
  newGameSession.value = undefined;
}
</script>

<template>
  <BCard class="bg-grey-100 bg-opacity-50 overflow-hidden" header-class="d-flex align-items-center justify-content-between" body-class="d-flex flex-column p-0">
    <template #header>
      <h4 class="m-0">
        <font-awesome-icon :icon="faDice"/>
        {{ $t("casino.game.sic_bo.title") }}
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
        <vue-markdown :source="$t('casino.game.sic_bo.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t('casino.game.sic_bo.title') }}</h2>

          <BButton variant="tertiary" class="btn-square text-light" @click="areRulesOpen = false">
            <font-awesome-icon :icon="faClose" />
          </BButton>
        </template>
      </BModal>

      <Transition>
        <div class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 bg-black bg-opacity-50 z-2" v-if="gameSession.state !== 'playing'">
          <div class="d-flex flex-column col-10 col-md-5 col-lg-4 bg-grey-100 bg-opacity-100 rounded-3 p-2 gap-2">
            <h1 class="text-white text-center" v-if="gameSession.state !== 'not_started'">
              {{ gameSession.state === 'lost' ? $t('casino.game.sic_bo.outcomes.lost') : $t('casino.game.sic_bo.outcomes.won') }}
            </h1>

            <BFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-white text-center">
                {{ $t('casino.game.sic_bo.bet') }}: {{ gameSession.bet }}
              </span>
              <BInput id="input-2" type="range" v-model="gameSession.bet" min="10" :max="balance < 100 ? balance : 100" :state="validateBet" />
              <BFormInvalidFeedback :state="validateBet">
                {{ $t('casino.not_enough_tokens') }}
              </BFormInvalidFeedback>
            </BFormGroup>

            <h5 class="rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center mb-0"
                :class="gameSession.bet - gameSession.initialBet > 0 ? 'text-success' : ''" v-if="gameSession.state === 'won'">
              {{ gameSession.bet - gameSession.initialBet > 0 ? "+" : "" }}{{ gameSession.bet - gameSession.initialBet }}
            </h5>

            <BButton variant="primary" class="btn-lg" @click.prevent="gameEnd" v-if="gameSession.state !== 'not_started'">
              {{ $t('casino.game.sic_bo.actions.play_again') }}
            </BButton>
            <BButton variant="primary" class="btn-lg" @click.prevent="start" v-else :disabled="!validateBet">
              {{ $t('casino.game.sic_bo.actions.start') }}
            </BButton>
          </div>
        </div>
      </Transition>

      <div class="d-flex flex-column gap-2 w-100">
        <div class="d-flex justify-content-center align-items-center gap-2 w-100">
          <Dice :value="diceValues[0]" />
          <Dice :value="diceValues[1]" />
          <Dice :value="diceValues[2]" />
        </div>

        <div class="d-flex gap-2">
          <h3 class="bg-grey-100 rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center mb-0">
            {{ gameSession.state === 'not_started' ? 0 : gameSession.bet }}
          </h3>
        </div>

        <div class="d-flex flex-column gap-2 w-100">
          <div class="d-flex justify-content-between align-items-stretch gap-2 w-100 flex-wrap">
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('small')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>Small</h3>
                <div>4 - 10</div>
                <div>{{ $t('casino.game.sic_bo.loss_3') }}</div>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:1
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1 align-items-stretch">
              <div class="d-flex gap-2 justify-content-center align-items-stretch w-100 h-100">
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('double-1')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="1" size="md" />
                  <Dice :value="1" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('double-2')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="2" size="md" />
                  <Dice :value="2" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('double-3')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="3" size="md" />
                  <Dice :value="3" size="md" />
                </BButton>
              </div>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:11
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1 align-items-stretch">
              <div class="d-flex flex-column gap-2 justify-content-center align-items-stretch w-100 h-100">
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center" @click="processTurn('triple-1')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="1" size="sm" />
                  <Dice :value="1" size="sm" />
                  <Dice :value="1" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center" @click="processTurn('triple-2')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="2" size="sm" />
                  <Dice :value="2" size="sm" />
                  <Dice :value="2" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center" @click="processTurn('triple-3')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="3" size="sm" />
                  <Dice :value="3" size="sm" />
                  <Dice :value="3" size="sm" />
                </BButton>
              </div>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:180
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2" @click="processTurn('triple-any')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <div class="d-flex gap-2 justify-content-center align-items-center w-100">
                  <Dice :value="1" size="sm" />
                  <Dice :value="1" size="sm" />
                  <Dice :value="1" size="sm" />
                </div>
                <div class="d-flex gap-2 justify-content-center align-items-center w-100">
                  <Dice :value="2" size="sm" />
                  <Dice :value="2" size="sm" />
                  <Dice :value="2" size="sm" />
                </div>
                <div class="d-flex gap-2 justify-content-center align-items-center w-100">
                  <Dice :value="3" size="sm" />
                  <Dice :value="3" size="sm" />
                  <Dice :value="3" size="sm" />
                </div>
                <div class="d-flex gap-2 justify-content-center align-items-center w-100">
                  <Dice :value="4" size="sm" />
                  <Dice :value="4" size="sm" />
                  <Dice :value="4" size="sm" />
                </div>
                <div class="d-flex gap-2 justify-content-center align-items-center w-100">
                  <Dice :value="5" size="sm" />
                  <Dice :value="5" size="sm" />
                  <Dice :value="5" size="sm" />
                </div>
                <div class="d-flex gap-2 justify-content-center align-items-center w-100">
                  <Dice :value="6" size="sm" />
                  <Dice :value="6" size="sm" />
                  <Dice :value="6" size="sm" />
                </div>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:30
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1 align-items-stretch">
              <div class="d-flex flex-column gap-2 justify-content-center align-items-stretch w-100 h-100">
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center" @click="processTurn('triple-4')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="4" size="sm" />
                  <Dice :value="4" size="sm" />
                  <Dice :value="4" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center" @click="processTurn('triple-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="5" size="sm" />
                  <Dice :value="5" size="sm" />
                  <Dice :value="5" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center" @click="processTurn('triple-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="6" size="sm" />
                  <Dice :value="6" size="sm" />
                  <Dice :value="6" size="sm" />
                </BButton>
              </div>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:180
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1 align-items-stretch">
              <div class="d-flex gap-2 justify-content-center align-items-stretch w-100 h-100">
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('double-4')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="4" size="md" />
                  <Dice :value="4" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('double-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="5" size="md" />
                  <Dice :value="5" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('double-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <Dice :value="6" size="md" />
                  <Dice :value="6" size="md" />
                </BButton>
              </div>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:11
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('big')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>Big</h3>
                <div>11 - 17</div>
                <div>{{ $t('casino.game.sic_bo.loss_3') }}</div>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:1
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-stretch gap-2 w-100 flex-wrap">
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-4')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>4</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:60
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>5</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:20
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>6</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:18
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-7')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>7</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:12
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-8')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>8</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:8
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <div class="d-flex gap-2 justify-content-center align-items-center">
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-9')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <h3>9</h3>
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-10')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <h3>10</h3>
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-11')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <h3>11</h3>
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-12')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                  <h3>12</h3>
                </BButton>
              </div>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:6
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-13')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>13</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:8
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-14')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>14</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:12
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-15')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>15</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:18
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-16')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>16</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:20
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100" @click="processTurn('total-17')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <h3>17</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:60
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-stretch gap-2 w-100 flex-wrap">
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-1-2')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="1" size="md" />
              <Dice :value="2" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-1-3')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="1" size="md" />
              <Dice :value="3" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-1-4')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="1" size="md" />
              <Dice :value="4" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-1-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="1" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-1-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="1" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-2-3')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="2" size="md" />
              <Dice :value="3" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-2-4')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="2" size="md" />
              <Dice :value="4" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-2-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="2" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-2-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="2" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-3-4')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="3" size="md" />
              <Dice :value="4" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-3-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="3" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-3-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="3" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-4-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="4" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-4-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="4" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center" @click="processTurn('pair-5-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
              <Dice :value="5" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
          </div>

          <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
            1:6
          </div>

          <div class="d-flex flex-column justify-content-between gap-2 w-100">
            <div class="d-flex flex-grow-1 gap-2 flex-wrap">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('face-1')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <Dice :value="1" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('face-2')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <Dice :value="2" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('face-3')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <Dice :value="3" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('face-4')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <Dice :value="4" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('face-5')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <Dice :value="5" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1" @click="processTurn('face-6')" :disabled="gameSession.state !== 'playing' || waitingForResponse">
                <Dice :value="6" size="md" />
              </BButton>
            </div>
            <div class="d-flex flex-grow-1 rounded-3 overflow-hidden">
              <div class="bg-grey-100 p-1 text-center w-100">
                1:1 {{ $t('casino.game.sic_bo.on_one_die') }}
              </div>
              <div class="bg-grey-100 p-1 text-center w-100">
                1:2 {{ $t('casino.game.sic_bo.on_two_dice') }}
              </div>
              <div class="bg-grey-100 p-1 text-center w-100">
                1:3 {{ $t('casino.game.sic_bo.on_three_dice') }}
              </div>
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
</style>
