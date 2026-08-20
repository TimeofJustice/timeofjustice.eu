<script setup lang="ts">
import { useUi } from "./cn";

export interface UiFieldErrorProps {
  /** Why the value is wrong. Shown as a tooltip on the icon. */
  message?: string;
}

defineProps<UiFieldErrorProps>();

defineOptions({ inheritAttrs: false });

// Sits inside the field, so it must not swallow the click that focuses it —
// only the icon itself takes the pointer, and only to answer a hover.
const { ui, rest } = useUi(() => [
  "pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2.5 text-danger",
]);
</script>

<template>
  <span :class="ui" v-bind="rest">
    <UiTooltip v-if="message" :text="message" :delay="150" wrap>
      <span
        class="pointer-events-auto flex cursor-help items-center"
        tabindex="0"
        role="img"
        :aria-label="message"
      >
        <iconify-icon icon="fa6-solid:circle-exclamation" />
      </span>
    </UiTooltip>

    <iconify-icon v-else icon="fa6-solid:circle-exclamation" />
  </span>
</template>
