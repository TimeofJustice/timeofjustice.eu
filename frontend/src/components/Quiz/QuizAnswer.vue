<script setup lang="ts">
import { BaseColorVariant } from "bootstrap-vue-next";
import { computed } from "vue";

interface QuizAnswerProps {
  answer: string;
  correct?: boolean;
  selected?: boolean;
  selectable?: boolean;
}

const {
  correct = false,
  selected = false,
  selectable = false,
} = defineProps<QuizAnswerProps>();

const emit = defineEmits<{
  (e: "select"): void;
}>();

const handleClick = () => {
  if (selectable) emit("select");
};

const answerVariant = computed<keyof BaseColorVariant | null>(() => {
  if (correct) return "success";
  if (selected) return "primary";
  return null;
});
</script>

<template>
  <BCard
    :variant="answerVariant"
    :class="{ answer: selectable }"
    @click="handleClick"
  >
    {{ answer }}

    <div class="position-absolute top-0 w-100 translate-middle-y pe-4">
      <BAvatarGroup size="2.3rem" overlap="0.4" class="reverse hover-focus">
        <slot />
      </BAvatarGroup>
    </div>
  </BCard>
</template>

<style scoped lang="scss">
.answer {
  cursor: pointer;
  transition:
    transform 0.15s ease,
    background 0.3s ease;

  &:hover {
    transform: scale(1.01);
  }
}
</style>
