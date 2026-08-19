<script setup lang="ts">
export interface UiInvalidFeedbackProps {
  /** Only `false` counts as invalid, `null` means "not validated yet". */
  state?: boolean | null;
}

defineProps<UiInvalidFeedbackProps>();
</script>

<template>
  <div v-if="state === false" class="mt-1 w-full text-[0.875em] text-danger">
    <slot />
  </div>
</template>
