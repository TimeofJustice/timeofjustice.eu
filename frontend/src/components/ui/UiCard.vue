<script setup lang="ts">
import { computed, provide, useSlots } from "vue";
import { useUi } from "./cn";
import { CARD_HAS_HEADER } from "./card";

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

const slots = useSlots();

// Read by `UiCardBody`, which stands in for the body slot below whenever the
// caller needs the body inside something of its own.
const hasHeader = computed(() => Boolean(slots.header));

provide(CARD_HAS_HEADER, hasHeader);

const { ui, rest } = useUi(() => [
  "relative flex min-w-0 flex-col break-words rounded-surface",
  "bg-card shadow-card backdrop-blur-card",
]);
</script>

<template>
  <div :class="ui" v-bind="rest">
    <div v-if="$slots.header" class="px-4 py-2" :class="headerClass">
      <slot name="header" />
    </div>

    <slot v-if="noBody" />
    <div
      v-else
      class="grow"
      :class="[
        hasHeader && 'border-t border-hairline',
        noPadding ? '' : 'p-4',
        bodyClass,
      ]"
    >
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
