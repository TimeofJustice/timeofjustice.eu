<script setup lang="ts">
import { InertiaLinkProps, Link } from "@inertiajs/vue3";

export interface BaseLinkProps extends /* @vue-ignore */ InertiaLinkProps {
  href: string;
  external?: boolean;
  offcanvasSource?: string;
}

defineProps<BaseLinkProps>();
</script>

<template>
  <component
    :is="external ? 'a' : Link"
    :href="href"
    v-bind="$attrs"
    :headers="
      offcanvasSource ? { 'X-Offcanvas-Source': offcanvasSource } : undefined
    "
    :only="offcanvasSource ? ['offcanvasState'] : undefined"
    :preserve-state="offcanvasSource ? true : undefined"
    :preserve-scroll="offcanvasSource ? true : undefined"
  >
    <slot />
  </component>
</template>
