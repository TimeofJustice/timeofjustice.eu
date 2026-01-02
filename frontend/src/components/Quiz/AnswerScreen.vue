<script setup lang="ts">
import QuizAnswer from "./QuizAnswer.vue";
import QuizQuestion from "./QuizQuestion.vue";
import { QuizPlayer } from "@/pages/Quiz/QuizPlayer";

interface AnswerScreenProps {
  players: QuizPlayer[];
  correctAnswer?: number;
}

const { players } = defineProps<AnswerScreenProps>();
</script>

<template>
  <div
    class="d-flex flex-column gap-3 col-12 col-md-8 col-lg-6 inner-screen overflow-hidden overflow-y-auto"
  >
    <!-- Question -->
    <div class="d-flex flex-column gap-2">
      <QuizQuestion
        question="Ich stelle dir die Frage des Lebens? Ich stelle dir die Frage des Lebens? Ich stelle dir die Frage des Lebens?"
      />
    </div>

    <!-- Answers -->
    <div class="d-flex flex-column gap-2">
      <QuizAnswer answer="Ich bin eine Antwort" :correct="correctAnswer == 0">
        <BAvatar
          :text="`+${players.length - 4}`"
          class="p-0 border border-2 border-black"
          v-if="4 < players.length"
        />
        <BAvatar
          class="p-0 border border-2 border-black"
          v-for="player in players.slice(0, 4)"
          :key="player.id"
        >
          <span class="b-avatar-img position-absolute">
            <img :src="player.image" />
          </span>
        </BAvatar>
      </QuizAnswer>

      <QuizAnswer answer="Ich bin eine Antwort" :correct="correctAnswer == 1">
      </QuizAnswer>

      <QuizAnswer answer="Ich bin eine Antwort" :correct="correctAnswer == 2">
      </QuizAnswer>
    </div>
  </div>
</template>

<style scoped lang="scss">
.inner-screen {
  max-height: 100%;
}
</style>
