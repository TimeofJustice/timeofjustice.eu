<script setup lang="ts">
import { Route } from "@/types/Route.ts";
import BaseLink from "@components/BaseLink.vue";
import { FOCUS_RING } from "@components/ui/focus";

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
      class="nav-link relative block rounded-md px-2 py-2 text-light no-underline transition-colors duration-150 hover:text-accent"
      :class="FOCUS_RING"
    >
      <div class="flex items-center whitespace-nowrap">
        <iconify-icon :icon="route.icon" />
        <!-- The space in front of a title belongs to the title: in the collapsed
             navbar the two go away together. -->
        <div class="link-title ml-1">{{ $t(route.name) }}</div>
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
