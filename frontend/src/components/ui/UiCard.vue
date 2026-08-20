<script setup lang="ts">
import { useUi } from "./cn";

export interface UiCardProps {
  /** Renders the default slot straight into the card, without a padded body. */
  noBody?: boolean;
  /** Keeps the body wrapper but drops its padding. */
  noPadding?: boolean;
  headerClass?: string;
  bodyClass?: string;
  footerClass?: string;
}

defineProps<UiCardProps>();

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  "relative flex min-w-0 flex-col break-words rounded-surface",
  "bg-card shadow-card backdrop-blur-card",
]);
</script>

<template>
  <div :class="ui" v-bind="rest">
    <div
      v-if="$slots.header"
      class="border-b border-hairline px-4 py-2"
      :class="headerClass"
    >
      <slot name="header" />
    </div>

    <slot v-if="noBody" />
    <div v-else class="grow" :class="[noPadding ? '' : 'p-4', bodyClass]">
      <slot />
    </div>

    <div
      v-if="$slots.footer"
      class="border-t border-hairline px-4 py-2"
      :class="footerClass"
    >
      <slot name="footer" />
    </div>
  </div>
</template>
