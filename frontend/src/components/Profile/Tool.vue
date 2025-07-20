<script setup lang="ts">
  import { Tool } from "@/types/Tool.ts";

  interface ToolProps {
    tool: Tool;
  }

  const { tool } = defineProps<ToolProps>();
  const { icon, alt, url } = tool;
</script>

<template>
  <a class="mx-1" style="height: 2rem;" :href="url" target="_blank" :title="alt" v-if="url">
    <img class="h-100" :src="icon" :alt="alt">
  </a>
  <img class="mx-1" style="height: 2rem;" :src="icon" :alt="alt" v-else>
</template>