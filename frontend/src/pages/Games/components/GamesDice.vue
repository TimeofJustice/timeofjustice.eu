<script setup lang="ts">
interface DiceProps {
  value: number;
  size?: "sm" | "md" | "lg";
}

withDefaults(defineProps<DiceProps>(), {
  size: "lg",
});
</script>

<template>
  <div
    class="dice rounded bg-red-600 bg-opacity-100 d-flex justify-content-center align-items-center"
    :class="`dice-${size}`"
  >
    <div
      class="d-flex flex-column h-100 w-100 align-items-center"
      :class="
        value !== 1 ? 'justify-content-between' : 'justify-content-center'
      "
    >
      <template v-if="value === 1">
        <iconify-icon icon="fa6-solid:circle" />
      </template>
      <template v-else-if="value === 2">
        <div class="d-flex justify-content-end w-100">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
        <div class="d-flex justify-content-start w-100">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
      </template>
      <template v-else-if="value === 3">
        <div class="d-flex justify-content-end w-100">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
        <div class="d-flex justify-content-center w-100">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
        <div class="d-flex justify-content-start w-100">
          <iconify-icon icon="fa6-solid:circle" />
        </div>
      </template>
      <template v-else-if="value >= 4">
        <div
          v-for="row in Math.ceil(value / 2)"
          :key="row"
          class="d-flex w-100"
          :class="
            value === 5 && row === 2
              ? 'justify-content-center'
              : 'justify-content-between'
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

<style scoped lang="scss">
.dice {
  &-sm {
    width: 1em;
    height: 1em;
    padding: 0.25em;

    .iconify {
      font-size: 0.125em;
    }
  }

  &-md {
    width: 2em;
    height: 2em;
    padding: 0.5em;

    .iconify {
      font-size: 0.3em;
    }
  }

  &-lg {
    width: 4em;
    height: 4em;
    padding: 0.75em;

    .iconify {
      font-size: 0.75em;
    }
  }
}
</style>
