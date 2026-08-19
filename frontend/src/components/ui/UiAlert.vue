<script setup lang="ts">
import { useUi } from "./cn";
import { SUBTLE, type Variant } from "./variants";

export interface UiAlertProps {
  variant?: Variant;
  dismissible?: boolean;
}

const { variant = "secondary", dismissible = false } =
  defineProps<UiAlertProps>();

const show = defineModel<boolean>({ default: true });

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  "relative mb-4 rounded-md border p-4",
  "[&_p]:m-0 [&_a]:text-info",
  SUBTLE[variant],
  dismissible && "pr-12",
]);
</script>

<template>
  <div v-if="show" role="alert" :class="ui" v-bind="rest">
    <slot />

    <UiButton
      v-if="dismissible"
      variant="tertiary"
      square
      class="absolute top-2 right-2"
      @click="show = false"
    >
      <slot name="close">&times;</slot>
    </UiButton>
  </div>
</template>
