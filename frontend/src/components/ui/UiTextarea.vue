<script setup lang="ts">
import { useUi } from "./cn";

export interface UiTextareaProps {
  rows?: number | string;
  /** `true` marks the field valid, `false` invalid, `null` leaves it neutral. */
  state?: boolean | null;
}

const { rows = 3, state = null } = defineProps<UiTextareaProps>();

const model = defineModel<string>();

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  "block w-full rounded-md border border-[#dee2e6] bg-body bg-clip-padding px-3 py-1.5 text-control leading-normal text-light transition-[border-color,box-shadow] duration-150 placeholder:text-accent focus:border-[#8a8b8c] focus:shadow-[0_0_0_0.25rem_rgb(20_22_25_/_0.25)] focus:outline-none",
  state === true && "border-success",
  state === false && "border-danger",
]);
</script>

<template>
  <textarea v-model="model" :rows="rows" :class="ui" v-bind="rest" />
</template>
