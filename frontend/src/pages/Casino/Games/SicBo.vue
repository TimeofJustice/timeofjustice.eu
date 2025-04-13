<!--Refactoring needed-->

<script setup lang="ts">
import { ref } from "vue";
import { faClose, faCopy, faDice, faInfo, faX } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { computed } from "@node_modules/vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController";
import { useI18n } from "@node_modules/vue-i18n";
import axios from "@node_modules/axios";
import Dice from "@pages/Casino/components/Dice.vue";

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
const { show } = useToastController();
const emit = defineEmits({
  balanceChange: null
});

const { balance } = defineProps<HigherLowerProps>();

const gameSession = ref<GameSession>({
  state: "betting",
  dice: [1, 2, 3],
  bets: {} as Record<turnType, number>,
  bet: 0,
  initialBet: 0,
  possibleWins: []
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
    const value1 = amount1 > 0 ? Math.floor(Math.random() * 6) + 1 : gameSession.value.dice[0];
    const value2 = amount2 > 0 ? Math.floor(Math.random() * 6) + 1 : gameSession.value.dice[1];
    const value3 = amount3 > 0 ? Math.floor(Math.random() * 6) + 1 : gameSession.value.dice[2];

    diceValues.value = [value1, value2, value3];

    if (amount1 > 0 || amount2 > 0 || amount3 > 0)
      rollDice(amount1 - 1, amount2 - 1, amount3 - 1);
    else {
      gameSession.value = newGameSession.value ? newGameSession.value : gameSession.value;
      waitingForResponse.value = false;

      if (gameSession.value.state === "end" && gameSession.value.bet > 0)
        emit("balanceChange", gameSession.value["bet"]);
    }
  }, 100);
};

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

type totalType =
  "small"
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
type doubleType = "double-1" | "double-2" | "double-3" | "double-4" | "double-5" | "double-6";
type tripleType = "triple-any" | "triple-1" | "triple-2" | "triple-3" | "triple-4" | "triple-5" | "triple-6";
type pairType =
  "pair-1-2"
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

  axios.post(`/casino/api/sic-bo/start/`, {
    bets: gameSession.value.bets
  })
    .then(response => {
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
        possibleWins: data["possibleWins"]
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
    state: "betting",
    dice: [1, 2, 3],
    bets: gameSession.value.bets,
    bet: 0,
    initialBet: 0,
    possibleWins: []
  };
  diceValues.value = [1, 2, 3];
  newGameSession.value = undefined;
};

const currentType = ref<turnType | undefined>(undefined);
const currentBet = ref<number>(0);

const getTotalBet = () => {
  let total = 0;

  for (const [_, value] of Object.entries(gameSession.value.bets)) {
    total += Number(value);
  }

  if (currentType.value && gameSession.value.bets[currentType.value] !== undefined) {
    total -= gameSession.value.bets[currentType.value] ?? 0;
  }

  return total;
};

const validateBet = computed(() => {
  return currentBet.value >= 10 && currentBet.value <= 500 && currentBet.value <= balance - getTotalBet();
});

const validateTotalBet = computed(() => {
  const total = getTotalBet() + Number(currentBet.value);

  return total >= 10 && total <= 500 && getTotalBet() <= balance;
});

const startBet = (type: turnType) => {
  if (type in gameSession.value.bets) {
    currentBet.value = Number(gameSession.value.bets[type]) ?? 10;
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
  <BCard class="bg-grey-100 bg-opacity-50 overflow-hidden" header-class="d-flex align-items-center justify-content-between" body-class="d-flex flex-column p-0">
    <template #header>
      <h4 class="m-0">
        <font-awesome-icon :icon="faDice" />
        {{ $t("casino.game.sic_bo.title") }}
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
        <vue-markdown :source="$t('casino.game.sic_bo.rules')" />

        <template #header>
          <h2 class="m-0">{{ $t("casino.game.sic_bo.title") }}</h2>

          <BButton variant="tertiary" class="btn-square text-light" @click="areRulesOpen = false">
            <font-awesome-icon :icon="faClose" />
          </BButton>
        </template>
      </BModal>

      <Transition>
        <div class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 bg-black bg-opacity-50 z-2"
             v-if="gameSession.state !== 'betting' && gameSession.state !== 'playing'">
          <div class="d-flex flex-column col-10 col-md-5 col-lg-4 bg-grey-100 bg-opacity-100 rounded-3 p-2 gap-2">
            <h1 class="text-white text-center" v-if="gameSession.state !== 'settingBet'">
              {{ gameSession.bet - gameSession.initialBet >= 0 ? $t("casino.game.sic_bo.outcomes.won") : $t("casino.game.sic_bo.outcomes.lost") }}
            </h1>

            <h5 class="rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center mb-0"
                :class="gameSession.bet - gameSession.initialBet >= 0 ? 'text-success' : 'text-danger'" v-if="gameSession.state === 'end'">
              {{ gameSession.bet - gameSession.initialBet > 0 ? "+" : "" }}{{ gameSession.bet - gameSession.initialBet }}
            </h5>

            <BFormGroup id="input-group-2" label-for="input-2" v-else>
              <span class="text-white text-center">
                {{ $t("casino.game.sic_bo.bet") }}: {{ currentBet }}
              </span>
              <BInput id="input-2" type="range" v-model="currentBet" min="10" :max="balance - getTotalBet() < 500 ? balance - getTotalBet() : 500"
                      :state="validateBet && validateTotalBet" />
              <BFormInvalidFeedback :state="validateBet || validateTotalBet">
                <span v-if="!validateTotalBet">
                  {{ $t("casino.game.sic_bo.bet_too_high") }}
                </span>
                <span v-else>
                  {{ $t("casino.not_enough_tokens") }}
                </span>
              </BFormInvalidFeedback>
            </BFormGroup>

            <BButton variant="primary" class="btn-lg" @click.prevent="gameEnd" v-if="gameSession.state !== 'settingBet'">
              {{ $t("casino.game.sic_bo.actions.play_again") }}
            </BButton>
            <div v-else class="d-flex gap-2 w-100">
              <BButton variant="primary" class="btn-lg w-100 text-truncate" @click.prevent="setBet" :disabled="!validateBet || !validateTotalBet">
                {{ $t("casino.game.sic_bo.bet") }}
              </BButton>
              <BButton variant="danger" class="btn-lg" @click.prevent="removeBet">
                <font-awesome-icon :icon="faX" />
              </BButton>
            </div>
          </div>
        </div>
      </Transition>

      <div class="d-flex flex-column gap-2 w-100">
        <div class="d-flex justify-content-center align-items-center gap-2 w-100">
          <Dice :value="diceValues[0]" />
          <Dice :value="diceValues[1]" />
          <Dice :value="diceValues[2]" />
        </div>
        <div class="d-flex flex-column gap-2 w-100">
          <div class="d-flex justify-content-between align-items-stretch gap-2 w-100 flex-wrap">
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('small')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['small'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('small') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['small']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["small"] }}
                </div>
                <h3>Small</h3>
                <div>4 - 10</div>
                <div>{{ $t("casino.game.sic_bo.loss_3") }}</div>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:1
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1 align-items-stretch">
              <div class="d-flex gap-2 justify-content-center align-items-stretch w-100 h-100">
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('double-1')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['double-1'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('double-1') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['double-1']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["double-1"] }}
                  </div>
                  <Dice :value="1" size="md" />
                  <Dice :value="1" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('double-2')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['double-2'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('double-2') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['double-2']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["double-2"] }}
                  </div>
                  <Dice :value="2" size="md" />
                  <Dice :value="2" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('double-3')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse" :class="gameSession.bets['double-3'] ? 'border border-warning' : ''">
                  <div v-if="gameSession.bets['double-3']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["double-3"] }}
                  </div>
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
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('triple-1')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['triple-1'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('triple-1') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['triple-1']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["triple-1"] }}
                  </div>
                  <Dice :value="1" size="sm" />
                  <Dice :value="1" size="sm" />
                  <Dice :value="1" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('triple-2')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['triple-2'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('triple-2') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['triple-2']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["triple-2"] }}
                  </div>
                  <Dice :value="2" size="sm" />
                  <Dice :value="2" size="sm" />
                  <Dice :value="2" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('triple-3')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['triple-3'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('triple-3') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['triple-3']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["triple-3"] }}
                  </div>
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
              <BButton class="d-flex flex-column gap-2 p-2 position-relative overflow-hidden" @click="startBet('triple-any')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['triple-any'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('triple-any') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['triple-any']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100 position-relative"
                     style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["triple-any"] }}
                </div>
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
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('triple-4')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['triple-4'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('triple-4') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['triple-4']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["triple-4"] }}
                  </div>
                  <Dice :value="4" size="sm" />
                  <Dice :value="4" size="sm" />
                  <Dice :value="4" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('triple-5')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['triple-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('triple-5') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['triple-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["triple-5"] }}
                  </div>
                  <Dice :value="5" size="sm" />
                  <Dice :value="5" size="sm" />
                  <Dice :value="5" size="sm" />
                </BButton>
                <BButton class="d-flex gap-2 p-2 h-100 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('triple-6')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['triple-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('triple-6') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['triple-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["triple-6"] }}
                  </div>
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
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('double-4')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['double-4'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('double-4') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['double-4']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["double-4"] }}
                  </div>
                  <Dice :value="4" size="md" />
                  <Dice :value="4" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('double-5')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['double-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('double-5') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['double-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["double-5"] }}
                  </div>
                  <Dice :value="5" size="md" />
                  <Dice :value="5" size="md" />
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('double-6')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['double-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('double-6') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['double-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["double-6"] }}
                  </div>
                  <Dice :value="6" size="md" />
                  <Dice :value="6" size="md" />
                </BButton>
              </div>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:11
              </div>
            </div>

            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('big')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['big'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('big') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['big']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["big"] }}
                </div>
                <h3>Big</h3>
                <div>11 - 17</div>
                <div>{{ $t("casino.game.sic_bo.loss_3") }}</div>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:1
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-stretch gap-2 w-100 flex-wrap">
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden" @click="startBet('total-4')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-4'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-4') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-4']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-4"] }}
                </div>
                <h3>4</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:60
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden" @click="startBet('total-5')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-5') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-5"] }}
                </div>
                <h3>5</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:20
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden" @click="startBet('total-6')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-6') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-6"] }}
                </div>
                <h3>6</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:18
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden" @click="startBet('total-7')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-7'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-7') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-7']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-7"] }}
                </div>
                <h3>7</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:12
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden" @click="startBet('total-8')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-8'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-8') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-8']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-8"] }}
                </div>
                <h3>8</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:8
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <div class="d-flex gap-2 justify-content-center align-items-center">
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('total-9')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['total-9'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-9') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['total-9']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["total-9"] }}
                  </div>
                  <h3>9</h3>
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('total-10')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['total-10'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-10') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['total-10']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["total-10"] }}
                  </div>
                  <h3>10</h3>
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('total-11')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['total-11'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-11') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['total-11']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["total-11"] }}
                  </div>
                  <h3>11</h3>
                </BButton>
                <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                         @click="startBet('total-12')"
                         :disabled="gameSession.state !== 'betting' || waitingForResponse"
                         :class="(gameSession.bets['total-12'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-12') ? ' bg-success' : '')">
                  <div v-if="gameSession.bets['total-12']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100"
                       style="border-bottom-left-radius: .5em">
                    {{ gameSession.bets["total-12"] }}
                  </div>
                  <h3>12</h3>
                </BButton>
              </div>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:6
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                       @click="startBet('total-13')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-13'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-13') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-13']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-13"] }}
                </div>
                <h3>13</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:8
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                       @click="startBet('total-14')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-14'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-14') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-14']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-14"] }}
                </div>
                <h3>14</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:12
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                       @click="startBet('total-15')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-15'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-15') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-15']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-15"] }}
                </div>
                <h3>15</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:18
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                       @click="startBet('total-16')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-16'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-16') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-16']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-16"] }}
                </div>
                <h3>16</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:20
              </div>
            </div>
            <div class="d-flex flex-column gap-2 flex-grow-1">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center w-100 position-relative overflow-hidden"
                       @click="startBet('total-17')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['total-17'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('total-17') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['total-17']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["total-17"] }}
                </div>
                <h3>17</h3>
              </BButton>
              <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
                1:60
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-stretch gap-2 w-100 flex-wrap">
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-1-2')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-1-2'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-1-2') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-1-2']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-1-2"] }}
              </div>
              <Dice :value="1" size="md" />
              <Dice :value="2" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-1-3')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-1-3'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-1-3') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-1-3']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets[("pair-1-3")] }}
              </div>
              <Dice :value="1" size="md" />
              <Dice :value="3" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-1-4')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-1-4'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-1-4') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-1-4']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-1-4"] }}
              </div>
              <Dice :value="1" size="md" />
              <Dice :value="4" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-1-5')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-1-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-1-5') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-1-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-1-5"] }}
              </div>
              <Dice :value="1" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-1-6')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-1-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-1-6') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-1-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-1-6"] }}
              </div>
              <Dice :value="1" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-2-3')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-2-3'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-2-3') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-2-3']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-2-3"] }}
              </div>
              <Dice :value="2" size="md" />
              <Dice :value="3" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-2-4')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-2-4'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-2-4') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-2-4']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-2-4"] }}
              </div>
              <Dice :value="2" size="md" />
              <Dice :value="4" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-2-5')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-2-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-2-5') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-2-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-2-5"] }}
              </div>
              <Dice :value="2" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-2-6')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-2-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-2-6') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-2-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-2-6"] }}
              </div>
              <Dice :value="2" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-3-4')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-3-4'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-3-4') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-3-4']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-3-4"] }}
              </div>
              <Dice :value="3" size="md" />
              <Dice :value="4" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-3-5')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-3-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-3-5') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-3-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-3-5"] }}
              </div>
              <Dice :value="3" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-3-6')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-3-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-3-6') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-3-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-3-6"] }}
              </div>
              <Dice :value="3" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-4-5')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-4-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-4-5') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-4-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-4-5"] }}
              </div>
              <Dice :value="4" size="md" />
              <Dice :value="5" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-4-6')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-4-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-4-6') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-4-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-4-6"] }}
              </div>
              <Dice :value="4" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
            <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center position-relative overflow-hidden" @click="startBet('pair-5-6')"
                     :disabled="gameSession.state !== 'betting' || waitingForResponse"
                     :class="(gameSession.bets['pair-5-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('pair-5-6') ? ' bg-success' : '')">
              <div v-if="gameSession.bets['pair-5-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                {{ gameSession.bets["pair-5-6"] }}
              </div>
              <Dice :value="5" size="md" />
              <Dice :value="6" size="md" />
            </BButton>
          </div>

          <div class="bg-grey-100 rounded-3 p-1 text-center w-100">
            1:6
          </div>

          <div class="d-flex flex-column justify-content-between gap-2 w-100">
            <div class="d-flex flex-grow-1 gap-2 flex-wrap">
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('face-1')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['face-1'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('face-1') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['face-1']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["face-1"] }}
                </div>
                <Dice :value="1" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('face-2')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['face-2'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('face-2') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['face-2']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["face-2"] }}
                </div>
                <Dice :value="2" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('face-3')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['face-3'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('face-3') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['face-3']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["face-3"] }}
                </div>
                <Dice :value="3" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('face-4')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['face-4'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('face-4') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['face-4']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["face-4"] }}
                </div>
                <Dice :value="4" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('face-5')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['face-5'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('face-5') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['face-5']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["face-5"] }}
                </div>
                <Dice :value="5" size="md" />
              </BButton>
              <BButton class="d-flex flex-column gap-2 p-2 justify-content-center align-items-center flex-grow-1 position-relative overflow-hidden"
                       @click="startBet('face-6')"
                       :disabled="gameSession.state !== 'betting' || waitingForResponse"
                       :class="(gameSession.bets['face-6'] ? 'border border-warning' : '') + (gameSession.possibleWins.includes('face-6') ? ' bg-success' : '')">
                <div v-if="gameSession.bets['face-6']" class="position-absolute top-0 end-0 p-1 z-3 bg-warning bg-opacity-100" style="border-bottom-left-radius: .5em">
                  {{ gameSession.bets["face-6"] }}
                </div>
                <Dice :value="6" size="md" />
              </BButton>
            </div>
            <div class="d-flex flex-grow-1 rounded-3 overflow-hidden">
              <div class="bg-grey-100 p-1 text-center w-100">
                1:1 {{ $t("casino.game.sic_bo.on_one_die") }}
              </div>
              <div class="bg-grey-100 p-1 text-center w-100">
                1:2 {{ $t("casino.game.sic_bo.on_two_dice") }}
              </div>
              <div class="bg-grey-100 p-1 text-center w-100">
                1:3 {{ $t("casino.game.sic_bo.on_three_dice") }}
              </div>
            </div>
          </div>

          <BButton variant="primary" class="btn-lg" @click.prevent="start"
                   :disabled="gameSession.state !== 'betting' || waitingForResponse || Object.keys(gameSession.bets).length === 0 || !validateTotalBet">
            {{ $t("casino.game.sic_bo.actions.start") }}
          </BButton>
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
