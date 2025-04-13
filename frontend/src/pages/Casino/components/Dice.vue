<script setup lang="ts">
import { faCircle } from "@node_modules/@fortawesome/free-solid-svg-icons";

interface DiceProps {
  value: number;
  size?: 'sm' | 'md' | 'lg';
}

withDefaults(defineProps<DiceProps>(), {
  size: 'lg',
});
</script>

<template>
  <div class="dice rounded bg-red bg-opacity-100 d-flex justify-content-center align-items-center" :class="`dice-${size}`">
    <div class="d-flex flex-column h-100 w-100" :class="value !== 1 ? 'justify-content-between' : 'justify-content-center'">
      <template v-if="value === 1">
        <font-awesome-icon :icon="faCircle" />
      </template>
      <template v-else-if="value === 2">
        <div class="d-flex justify-content-end w-100">
          <font-awesome-icon :icon="faCircle" />
        </div>
        <div class="d-flex justify-content-start w-100">
          <font-awesome-icon :icon="faCircle" />
        </div>
      </template>
      <template v-else-if="value === 3">
        <div class="d-flex justify-content-end w-100">
          <font-awesome-icon :icon="faCircle" />
        </div>
        <div class="d-flex justify-content-center w-100">
          <font-awesome-icon :icon="faCircle" />
        </div>
        <div class="d-flex justify-content-start w-100">
          <font-awesome-icon :icon="faCircle" />
        </div>
      </template>
      <template v-else-if="value >= 4">
        <div v-for="row in Math.ceil(value / 2)" :key="row" class="d-flex w-100" :class="value === 5 && row === 2 ? 'justify-content-center' : 'justify-content-between'">
          <font-awesome-icon :icon="faCircle" />
          <font-awesome-icon :icon="faCircle" v-if="value !== 5 || row !== 2" />
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
      padding: .25em;

      .fa-circle {
        font-size: .125em;
      }
    }

    &-md {
      width: 2em;
      height: 2em;
      padding: .5em;

      .fa-circle {
        font-size: .3em;
      }
    }

    &-lg {
      width: 4em;
      height: 4em;
      padding: .75em;

      .fa-circle {
        font-size: .75em;
      }
    }
  }
</style>