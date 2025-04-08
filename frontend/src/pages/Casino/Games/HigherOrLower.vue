<script setup lang="ts">
import { ref } from "vue";
import { faArrowDown, faArrowUp, faMinus } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { computed } from "@node_modules/vue";

const gameState = ref<'not_started' | 'first_round' | 'still_playing' | 'won' | 'lost'>('not_started');
const card = ref('back');
const bet = ref(10);
const initialBet = ref(10);
const leftOverCards = ref(52);
const sessionId = ref('');

interface HigherLowerProps {
  balance: number;
}

const { balance } = defineProps<HigherLowerProps>();

const emit = defineEmits({
  tokens_won: null,
  tokens_lost: null,
})

const start = async () => {
  const response = await fetch(`/casino/api/higher-lower/start/${bet.value}`);
  if (!response.ok) {
    throw new Error("Failed to load project");
  }

  const data = await response.json();

  emit('tokens_lost', data["initial_bet"]);

  card.value = data["card"];
  bet.value = data["bet"];
  initialBet.value = data["initial_bet"];
  leftOverCards.value = data["cards_left"];
  sessionId.value = data["session_id"];

  gameState.value = 'first_round';
}

const higher = async () => {
  const response = await fetch(`/casino/api/higher-lower/higher/${sessionId.value}`);
  if (!response.ok) {
    throw new Error("Failed to load project");
  }

  const data = await response.json();

  card.value = data["card"];
  bet.value = data["bet"];
  leftOverCards.value = data["cards_left"];
  gameState.value = 'still_playing';

  if (data["bet"] <= 0)
    return game_lost();
}

const lower = async () => {
  const response = await fetch(`/casino/api/higher-lower/lower/${sessionId.value}`);
  if (!response.ok) {
    throw new Error("Failed to load project");
  }

  const data = await response.json();

  card.value = data["card"];
  bet.value = data["bet"];
  leftOverCards.value = data["cards_left"];
  gameState.value = 'still_playing';

  if (data["bet"] <= 0)
    return game_lost();
}

const draw = async () => {
  const response = await fetch(`/casino/api/higher-lower/draw/${sessionId.value}`);
  if (!response.ok) {
    throw new Error("Failed to load project");
  }

  const data = await response.json();

  card.value = data["card"];
  bet.value = data["bet"];
  leftOverCards.value = data["cards_left"];
  gameState.value = 'still_playing';

  if (data["bet"] <= 0)
    return game_lost();
}

const leave = async () => {
  const response = await fetch(`/casino/api/higher-lower/leave/${sessionId.value}`);
  if (!response.ok) {
    throw new Error("Failed to load project");
  }

  const data = await response.json();

  emit('tokens_won', data["bet"]);

  return game_won();
}

const game_won = () => {
  gameState.value = 'won';
  sessionId.value = '';
}

const game_lost = () => {
  gameState.value = 'lost';
  sessionId.value = '';
}

const game_end = () => {
  gameState.value = 'not_started';
  card.value = 'back';
  bet.value = initialBet.value;
  leftOverCards.value = 52;
  sessionId.value = '';
}

const validation = computed(() => {
  const numericBalance = Number(balance);

  return bet.value >= 10 && bet.value <= 100 && bet.value <= numericBalance;
});
</script>

<template>
<div class="w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 position-relative">
  <div class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center gap-2 bg-black bg-opacity-50 z-3" v-if="gameState !== 'first_round' && gameState !== 'still_playing'">
    <div class="d-flex flex-column col-3 bg-grey-100 bg-opacity-100 rounded-3 p-2 gap-2">
      <h1 class="text-white text-center" v-if="gameState !== 'not_started'">
        {{ gameState === 'lost' ? $t('casino.game.higher_lower.outcomes.lost') : $t('casino.game.higher_lower.outcomes.won') }}
      </h1>

      <BFormGroup id="input-group-2" label-for="input-2" v-else>
        <span class="text-white text-center">
          {{ $t('casino.game.higher_lower.bet') }}: {{ bet }}
        </span>
        <BInput id="input-2" type="range" v-model="bet" min="10" :max="balance < 100 ? balance : 100" :state="validation" />
        <BFormInvalidFeedback :state="validation">
          {{ $t('casino.not_enough_tokens') }}
        </BFormInvalidFeedback>
      </BFormGroup>

      <BButton variant="primary" class="btn-lg" @click.prevent="game_end" v-if="gameState !== 'not_started'">
        {{ $t('casino.game.higher_lower.actions.play_again') }}
      </BButton>
      <BButton variant="primary" class="btn-lg" @click.prevent="start" v-else :disabled="!validation">
        {{ $t('casino.game.higher_lower.actions.start') }}
      </BButton>
    </div>
  </div>

  <div class="d-flex flex-column gap-2">
    <div class="d-flex justify-content-center align-items-center gap-2">
      <img :src="'/files/images/casino/cards/' + card + '.svg'" :alt="card" class="img-fluid" />

      <div class="d-flex flex-column gap-2">
        <BButton variant="success" @click.prevent="higher" :disabled="gameState !== 'first_round' && gameState !== 'still_playing'">
          <font-awesome-icon :icon="faArrowUp"/>
        </BButton>
        <BButton variant="warning" @click.prevent="draw" :disabled="gameState !== 'first_round' && gameState !== 'still_playing'">
          <font-awesome-icon :icon="faMinus"/>
        </BButton>
        <BButton variant="danger" @click.prevent="lower" :disabled="gameState !== 'first_round' && gameState !== 'still_playing'">
          <font-awesome-icon :icon="faArrowDown"/>
        </BButton>
        <BButton variant="primary" @click.prevent="leave" :disabled="gameState !== 'still_playing'">
          {{ $t('casino.game.higher_lower.actions.quit') }}
        </BButton>
      </div>
    </div>

    <h3 class="bg-grey-100 rounded-3 p-2 d-flex flex-column gap-2 w-100 text-center">
      {{ gameState === 'not_started' ? 0 : bet }}
    </h3>
  </div>
</div>
</template>

<style scoped lang="scss">

</style>