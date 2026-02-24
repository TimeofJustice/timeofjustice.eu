<script setup lang="ts">
import { computed } from "vue";

interface TButtonProps {
  label?: string;
  squared?: boolean;
  circular?: boolean;
  type?: "primary" | "secondary" | "tertiary";
}

const { type = "primary" } = defineProps<TButtonProps>();

const variantClasses = computed(() => {
  const map = {
    primary:
      "bg-primary hover:bg-primary-hover active:bg-primary-active text-primary-foreground",
    secondary:
      "bg-secondary hover:bg-secondary-hover active:bg-secondary-active text-secondary-foreground",
    tertiary:
      "bg-tertiary hover:bg-tertiary-hover active:bg-tertiary-active text-tertiary-foreground",
  };

  return map[type ?? "primary"];
});
</script>

<template>
  <button
    :class="[
      'py-2 px-4 rounded transition-colors duration-200',
      squared ? 'btn-square' : '',
      circular ? 'btn-square btn-circular' : '',
      variantClasses,
    ]"
  >
    <slot>
      {{ label }}
    </slot>
  </button>
</template>

<style scoped lang="scss">
.btn-square {
  min-width: 36px;
  max-width: 36px;
  min-height: 36px;
  max-height: 36px;

  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-circular {
  border-radius: 50%;
}
</style>
