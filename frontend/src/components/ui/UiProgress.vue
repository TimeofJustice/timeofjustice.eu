<script setup lang="ts">
import { provide, toRef } from "vue";
import { PROGRESS_MAX } from "./progress";

export interface UiProgressProps {
  max?: number;
}

const { max = 100 } = defineProps<UiProgressProps>();

provide(
  PROGRESS_MAX,
  toRef(() => max),
);
</script>

<template>
  <div class="flex h-4 overflow-hidden rounded-md bg-dark-gray-600 text-xs">
    <slot />
  </div>
</template>
