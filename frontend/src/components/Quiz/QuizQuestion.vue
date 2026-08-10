<script setup lang="ts">
interface QuizQuestionProps {
  question: string;
}

const { question } = defineProps<QuizQuestionProps>();
</script>

<template>
  <BCard variant="secondary" class="question">
    {{ question }}
  </BCard>
</template>

<style scoped lang="scss">
.question {
  transform: scale(0.99);
}
</style>
