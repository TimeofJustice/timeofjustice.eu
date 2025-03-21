<script setup lang="ts">
  import { Tool } from "@/types/Tool.ts";

  interface ToolProps {
    tool: Tool;
  }

  const { tool } = defineProps<ToolProps>();
  const { icon, alt, url } = tool;
</script>

<template>
  <a class="h-100 mx-1" :href="url" target="_blank" :title="alt" v-if="url !== ''">
    <img class="img-fluid h-100" :src="icon" :alt="alt">
  </a>
  <img class="img-fluid h-100 mx-1" :src="icon" :alt="alt" v-else>
</template>