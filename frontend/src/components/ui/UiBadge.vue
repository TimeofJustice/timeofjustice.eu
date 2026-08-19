<script setup lang="ts">
import { useUi } from "./cn";
import { FILL, type Variant } from "./variants";

export interface UiBadgeProps {
  variant?: Variant;
  /** Renders a bare coloured dot instead of a labelled badge. */
  dot?: boolean;
}

const { variant = "secondary", dot = false } = defineProps<UiBadgeProps>();

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  "inline-flex items-center justify-center gap-1 text-center align-baseline",
  "text-[0.75em] leading-[1.1] font-bold whitespace-nowrap",
  FILL[variant],
  dot ? "rounded-full p-[0.3rem]" : "rounded-md px-[0.65em] py-[0.35em]",
]);
</script>

<template>
  <span :class="ui" v-bind="rest">
    <slot v-if="!dot" />
  </span>
</template>
