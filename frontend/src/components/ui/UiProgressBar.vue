<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { PROGRESS_MAX } from "./progress";
import { FILL, type Variant } from "./variants";

export interface UiProgressBarProps {
  value?: number;
  variant?: Variant;
}

const { value = 0, variant } = defineProps<UiProgressBarProps>();

const max = inject(PROGRESS_MAX, ref(100));

const width = computed(() => {
  if (max.value <= 0) return "0%";

  return `${Math.min(100, Math.max(0, (value / max.value) * 100))}%`;
});
</script>

<template>
  <div
    role="progressbar"
    class="flex flex-col justify-center overflow-hidden bg-control-accent text-center whitespace-nowrap text-white transition-[width] duration-600 ease-in-out"
    :class="variant && FILL[variant]"
    :style="{ width }"
  >
    <slot />
  </div>
</template>
