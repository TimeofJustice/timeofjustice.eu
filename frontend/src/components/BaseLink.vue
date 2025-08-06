<script setup lang="ts">
import { Link, InertiaLinkProps } from "@inertiajs/vue3";

export interface BaseLinkProps extends /* @vue-ignore */ InertiaLinkProps {
  href: string;
  external?: boolean;
}

defineProps<BaseLinkProps>();
</script>

<template>
  <component :is="external ? 'a' : Link" :href="href">
    <slot />
  </component>
</template>
