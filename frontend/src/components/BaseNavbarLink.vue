<script setup lang="ts">
import { Route } from "@/types/Route.ts";

interface INavbarLink {
  route: Route;
}

defineProps<INavbarLink>();
</script>

<template>
  <BNavItem
    :key="route.name"
    :to="route.path"
    link-class="position-relative"
    :class="{ active: route.activeComponents.includes($page.component) }"
  >
    <div class="text-nowrap d-flex align-items-center">
      <iconify-icon :icon="route.icon" class="me-1" />
      <div class="link-title">{{ $t(route.name) }}</div>
    </div>
    <BBadge
      variant="danger"
      class="position-absolute top-0 start-100 translate-middle mt-2 me-1 border-0 pulse"
      dot-indicator
      v-if="route.isHighlighted"
    />
  </BNavItem>
</template>

<style scoped lang="scss"></style>
