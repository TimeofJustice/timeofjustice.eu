<script setup lang="ts">
interface GamesDiceProps {
  value: number;
  size?: "sm" | "md" | "lg";
}

const { size = "lg" } = defineProps<GamesDiceProps>();
</script>

<template>
  <div
    class="dice flex items-center justify-center rounded-md bg-red-600"
    :class="`dice-${size}`"
  >
    <div
      class="flex h-full w-full flex-col items-center"
      :class="value !== 1 ? 'justify-between' : 'justify-center'"
    >
      <template v-if="value === 1">
        <iconify-icon icon="fa6-solid:circle" />
      </template>
      <template v-else-if="value === 2">
        <div class="flex w-full justify-end">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
        <div class="flex w-full justify-start">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
      </template>
      <template v-else-if="value === 3">
        <div class="flex w-full justify-end">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
        <div class="flex w-full justify-center">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
        <div class="flex w-full justify-start">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
      </template>
      <template v-else-if="value >= 4">
        <div
          v-for="row in Math.ceil(value / 2)"
          :key="row"
          class="flex w-full"
          :class="
            value === 5 && row === 2 ? 'justify-center' : 'justify-between'
          "
        >
          <iconify-icon icon="fa6-solid:circle" />
          <iconify-icon
            icon="fa6-solid:circle"
            v-if="value !== 5 || row !== 2"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.dice {
  width: var(--dice-size, 4em);
  height: var(--dice-size, 4em);
  padding: var(--dice-padding, 0.75em);
}

.dice :deep(.iconify) {
  font-size: var(--dice-icon-size, 0.75em);
}

.dice-sm {
  --dice-size: 1em;
  --dice-padding: 0.25em;
  --dice-icon-size: 0.125em;
}

.dice-md {
  --dice-size: 2em;
  --dice-padding: 0.5em;
  --dice-icon-size: 0.3em;
}

.dice-lg {
  --dice-size: 4em;
  --dice-padding: 0.75em;
  --dice-icon-size: 0.75em;
}
</style>
