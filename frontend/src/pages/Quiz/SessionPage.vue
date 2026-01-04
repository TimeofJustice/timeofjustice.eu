<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { onBeforeUnmount, ref } from "vue";
import { QuizPlayer } from "@/types/Quiz/QuizPlayer";
import LeaderboardScreen from "@/components/Quiz/LeaderboardScreen.vue";
import QuestionScreen from "@/components/Quiz/QuestionScreen.vue";
import AnswerScreen from "@/components/Quiz/AnswerScreen.vue";
import QuizBackground from "@/components/Quiz/QuizBackground.vue";

const gameState = ref<"question" | "answer" | "leaderboard">("question");
const selectedAnswer = ref<number | null>(null);

const handleSelect = (index: number) => {
  selectedAnswer.value = index;
};

const players = ref<QuizPlayer[]>([
  new QuizPlayer(
    0,
    "Boris",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTA2NnF5YWViY25sdDJhb3Q2OTVrdzNmY2ptNnI3YTl2N3Fta2NvaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Dg4TxjYikCpiGd7tYs/giphy.gif",
  ),
  new QuizPlayer(
    1,
    "Doris",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif",
  ),
]);

const answerOnePlayers = ref<QuizPlayer[]>([]);

const addNewPlayer = () => {
  players.value.push(
    new QuizPlayer(
      players.value.length,
      "Jonas",
      "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif",
    ),
  );
};

const msPerTurn = ref(30000);
const msLeft = ref(msPerTurn.value);

const turnInterval = setInterval(() => {
  if (msLeft.value > 0) {
    msLeft.value -= 50;

    if (msLeft.value <= 0) {
      msLeft.value = msPerTurn.value;
    }
  }
}, 50);

onBeforeUnmount(() => {
  clearInterval(turnInterval);
});
</script>

<template>
  <Head :title="$t('quiz.title')" />

  <div
    class="quiz-lobby-page h-100 fullscreen overflow-hidden position-relative d-flex flex-column"
  >
    <QuizBackground
      primary-color="hsl(185, 75%, 50%)"
      secondary-color="hsl(215, 85%, 60%)"
      :timer="Math.ceil(msLeft / 1000)"
    />

    <div class="flex-grow-1 position-relative overflow-hidden">
      <Transition name="screen-slide">
        <div class="container-xxl screen" v-if="gameState == 'question'">
          <QuestionScreen
            :players="answerOnePlayers"
            :selected-answer="selectedAnswer"
            @select="handleSelect"
          />
        </div>

        <div class="container-xxl screen" v-else-if="gameState == 'answer'">
          <AnswerScreen
            :players="answerOnePlayers"
            :selected-answer="selectedAnswer"
            :correctAnswer="2"
          />
        </div>

        <div
          class="container-xxl screen"
          v-else-if="gameState == 'leaderboard'"
        >
          <LeaderboardScreen :players="players" />
        </div>
      </Transition>
    </div>

    <div
      class="d-flex gap-2 justify-content-evenly position-absolute bottom-0 w-100 pb-2"
    >
      <BButton
        @click="
          gameState = 'question';
          answerOnePlayers.push(players[0]);
        "
      >
        Question Screen
      </BButton>
      <BButton @click="gameState = 'answer'"> Answer Screen </BButton>
      <BButton
        @click="
          gameState = 'leaderboard';
          addNewPlayer();
        "
      >
        Leaderboard Screen
      </BButton>
    </div>

    <BProgress :max="msPerTurn" height="0.5rem" animated>
      <BProgressBar :value="msLeft">
        <small style="font-size: 0.5rem"
          >{{ (msLeft / 1000).toFixed(0) }}s</small
        >
      </BProgressBar>
    </BProgress>
  </div>
</template>

<style scoped lang="scss">
.quiz-lobby-page {
  background-color: rgba(7, 28, 57, 1);
}

.screen-slide-enter-active,
.screen-slide-leave-active {
  transition: transform 0.4s ease;
}

.screen-slide-enter-from {
  transform: translateX(100%);
}

.screen-slide-enter-to {
  transform: translateX(0%);
}

.screen-slide-leave-from {
  transform: translateX(0%);
}

.screen-slide-leave-to {
  transform: translateX(-100%);
}

.screen {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  display: flex;
  justify-content: center;
  align-items: center;

  padding: calc(var(--bs-gutter-x) * 0.5);
}
</style>
