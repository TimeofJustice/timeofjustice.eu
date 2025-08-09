<script setup lang="ts">
import { InertiaLinkProps, Link } from "@inertiajs/vue3";

export interface BaseLinkProps extends /* @vue-ignore */ InertiaLinkProps {
  href: string;
  external?: boolean;
  offcanvasSource?: string;
}

const { href, external, offcanvasSource } = defineProps<BaseLinkProps>();

import { router } from "@inertiajs/vue3";

function handleClick(event: MouseEvent) {
  if (!external && offcanvasSource) {
    event.preventDefault();

    router.visit(href, {
      headers: {
        "X-Offcanvas-Source": offcanvasSource,
      },
      only: ["offcanvasComponent", "offcanvasProps", "offcanvasSource"],
      preserveState: true,
      preserveScroll: true,
      replace: true,
    });
  }
}
</script>

<template>
  <component
    :is="external || offcanvasSource ? 'a' : Link"
    :href="href"
    v-bind="$attrs"
    @click="handleClick"
  >
    <slot />
  </component>
</template>
