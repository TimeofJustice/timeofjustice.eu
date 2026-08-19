<script setup lang="ts">
export interface UiFormGroupProps {
  label?: string;
  labelFor?: string;
  labelClass?: string;
}

defineProps<UiFormGroupProps>();
</script>

<template>
  <div>
    <label
      v-if="label"
      :for="labelFor"
      class="mb-2 inline-block"
      :class="labelClass"
    >
      {{ label }}
    </label>

    <slot />
  </div>
</template>
