<script setup lang="ts">
import { FontAwesomeIcon } from "@node_modules/@fortawesome/vue-fontawesome";
import { Route } from "../types/Route.ts";

interface INavbarLink {
  route: Route;
}

defineProps<INavbarLink>();
</script>

<template>
  <BNavItem
    :key="route.name"
    :to="route.path"
    link-class="d-flex align-items-center position-relative"
    :class="{ active: route.activeComponents.includes($page.component) }"
  >
    <FontAwesomeIcon :icon="route.icon" />
    <div class="text-nowrap ms-1 link-title">{{ $t(route.name) }}</div>
    <BBadge
      variant="danger"
      class="position-absolute top-0 start-100 translate-middle mt-2 me-1 border-0 pulse"
      dot-indicator
      v-if="route.isHighlighted"
    />
  </BNavItem>
</template>

<style scoped lang="scss"></style>
