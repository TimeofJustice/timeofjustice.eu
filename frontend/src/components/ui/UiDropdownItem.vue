<script setup lang="ts">
import BaseLink from "@components/BaseLink.vue";
import { useUi } from "./cn";
import { FOCUS_RING } from "./focus";

export interface UiDropdownItemProps {
  /** Renders the item as a link. Without it the item is a plain button. */
  to?: string;
  external?: boolean;
  target?: string;
}

const { to } = defineProps<UiDropdownItemProps>();

defineOptions({ inheritAttrs: false });

// The tint is mixed from the item's own colour, so a red entry highlights red
// instead of borrowing the neutral grey of the ones above it.
const { ui, rest } = useUi(() => [
  "block w-full cursor-pointer border-0 bg-transparent px-4 py-1.5 text-left font-normal",
  "whitespace-nowrap text-light no-underline transition-colors duration-150",
  "hover:bg-[color-mix(in_srgb,currentColor_15%,transparent)] hover:text-light",
  "focus-visible:bg-[color-mix(in_srgb,currentColor_15%,transparent)]",
  FOCUS_RING,
]);
</script>

<template>
  <BaseLink
    v-if="to"
    :href="to"
    :external="external"
    :target="target"
    :class="ui"
    v-bind="rest"
  >
    <slot />
  </BaseLink>

  <button v-else type="button" :class="ui" v-bind="rest">
    <slot />
  </button>
</template>
