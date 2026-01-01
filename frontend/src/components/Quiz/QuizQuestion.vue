<script setup lang="ts">
interface QuizQuestionProps {
  question: string;
}

const { question } = defineProps<QuizQuestionProps>();
</script>

<template>
  <BCard variant="secondary">
    {{ question }}
  </BCard>
</template>

<style scoped lang="scss"></style>
