<script setup lang="ts">
import BaseLink from "@components/BaseLink.vue";
import { useUi } from "./cn";

export interface UiDropdownItemProps {
  /** Renders the item as a link. Without it the item is a plain button. */
  to?: string;
  external?: boolean;
  target?: string;
}

const { to } = defineProps<UiDropdownItemProps>();

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  "block w-full cursor-pointer border-0 bg-transparent px-4 py-1 text-left font-normal",
  "whitespace-nowrap text-dark no-underline",
  "hover:bg-[color-mix(in_srgb,currentColor_20%,transparent)] hover:text-dark",
  "focus:bg-[color-mix(in_srgb,currentColor_20%,transparent)] focus:text-dark",
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
