<script setup lang="ts">
import { useUi } from "./cn";
import { FILL, type Variant } from "./variants";

export interface UiToastProps {
  variant?: Variant;
  bodyClass?: string;
}

const { variant = "secondary" } = defineProps<UiToastProps>();

const show = defineModel<boolean>({ default: true });

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  "w-[350px] max-w-full rounded-surface border border-hairline bg-clip-padding",
  "text-sm shadow-overlay",
  FILL[variant],
]);
</script>

<template>
  <div v-if="show" role="alert" :class="ui" v-bind="rest">
    <div class="p-3 wrap-break-word" :class="bodyClass">
      <slot />
    </div>
  </div>
</template>
