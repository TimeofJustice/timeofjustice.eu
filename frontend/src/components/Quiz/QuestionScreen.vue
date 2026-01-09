<script setup lang="ts">
import QuizAnswer from "./QuizAnswer.vue";
import QuizQuestion from "./QuizQuestion.vue";

interface QuestionScreenProps {
  selectedAnswer: number | null;
}

defineProps<QuestionScreenProps>();

const emit = defineEmits<{
  (e: "select", index: number): void;
}>();
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
      <QuizAnswer
        answer="Ich bin eine Antwort"
        selectable
        :selected="selectedAnswer == 0"
        @select="emit('select', 0)"
      />

      <QuizAnswer
        answer="Ich bin eine Antwort"
        selectable
        :selected="selectedAnswer == 1"
        @select="emit('select', 1)"
      />

      <QuizAnswer
        answer="Ich bin eine Antwort"
        selectable
        :selected="selectedAnswer == 2"
        @select="emit('select', 2)"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.inner-screen {
  max-height: 100%;
}
</style>
