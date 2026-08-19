<script setup lang="ts">
import { computed } from "vue";
import BaseLink from "@components/BaseLink.vue";
import { useUi } from "./cn";
import type { Variant } from "./variants";

export interface UiLinkProps {
  /** Inertia target, stays inside the SPA. */
  to?: string;
  /** Plain anchor target. Leaves the SPA unless `external` says otherwise. */
  href?: string;
  external?: boolean;
  target?: string;
  variant?: Variant;
  /** Opens the target in the layout offcanvas instead of a full page visit. */
  offcanvasSource?: string;
}

const { to, href, external, variant } = defineProps<UiLinkProps>();

defineOptions({ inheritAttrs: false });

/** `href` addresses something outside the SPA, so it never routes via Inertia. */
const isExternal = computed(() => external ?? Boolean(href));

const VARIANTS: Partial<Record<Variant, string>> = {
  light: "text-light hover:text-light/80",
  dark: "text-dark hover:text-dark/80",
  info: "text-info hover:text-info/80",
  success: "text-success hover:text-success/80",
  warning: "text-warning hover:text-warning/80",
  danger: "text-danger hover:text-danger/80",
};

const { ui, rest } = useUi(() => variant && VARIANTS[variant]);
</script>

<template>
  <BaseLink
    v-if="to || href"
    :href="(to || href)!"
    :external="isExternal"
    :target="target"
    :offcanvas-source="offcanvasSource"
    :class="ui"
    v-bind="rest"
  >
    <slot />
  </BaseLink>

  <button
    v-else
    type="button"
    class="cursor-pointer text-link underline transition-colors duration-150 hover:text-link-hover"
    :class="ui"
    v-bind="rest"
  >
    <slot />
  </button>
</template>
