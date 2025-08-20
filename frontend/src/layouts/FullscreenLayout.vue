<script setup lang="ts">
import { usePage } from "@node_modules/@inertiajs/vue3";
import { onUnmounted } from "@node_modules/vue";

const page = usePage();
page.props["navbarSize"] = "small";

const visibilityChangeHandler = () => {
  if (!document.hidden) {
    page.props["navbarSize"] = "small";
  }
};

document.addEventListener("visibilitychange", visibilityChangeHandler);

onUnmounted(() => {
  document.removeEventListener("visibilitychange", visibilityChangeHandler);
});
</script>

<template>
  <div class="h-100 overflow-hidden">
    <slot></slot>
  </div>
</template>

<style scoped lang="scss"></style>
