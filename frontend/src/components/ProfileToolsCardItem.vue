<script setup lang="ts">
import { Tool } from "@/types/Tool.ts";

interface ProfileToolsCardItemProps {
  tool: Tool;
}

defineProps<ProfileToolsCardItemProps>();
</script>

<template>
  <BLink
    class="mx-1"
    style="height: 2rem"
    :href="tool.url"
    target="_blank"
    :title="tool.alt"
    v-if="tool.url"
  >
    <img class="h-100" :src="tool.icon" :alt="tool.alt" />
  </BLink>
  <img
    class="mx-1"
    style="height: 2rem"
    :src="tool.icon"
    :alt="tool.alt"
    v-else
  />
</template>

<style scoped lang="scss"></style>
