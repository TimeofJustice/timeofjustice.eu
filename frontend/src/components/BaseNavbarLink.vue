<script setup lang="ts">
import { Route } from "@/types/Route.ts";
import BaseLink from "@components/BaseLink.vue";

interface INavbarLink {
  route: Route;
}

defineProps<INavbarLink>();
</script>

<template>
  <div
    :class="{
      'font-medium underline': route.activeComponents.includes($page.component),
    }"
  >
    <BaseLink
      :href="route.path"
      class="relative block px-2 py-2 text-light no-underline transition-colors duration-150 hover:text-accent"
    >
      <div class="flex items-center whitespace-nowrap">
        <iconify-icon :icon="route.icon" class="mr-1" />
        <div class="link-title">{{ $t(route.name) }}</div>
      </div>

      <UiBadge
        variant="danger"
        dot
        class="absolute top-0 left-full mt-2 -translate-x-1/2 -translate-y-1/2 animate-badge-pulse"
        v-if="route.isHighlighted"
      />
    </BaseLink>
  </div>
</template>
