<script setup lang="ts">
import { Tool } from "@/types/Tool.ts";

interface ProfileToolsCardItemProps {
  tool: Tool;
}

defineProps<ProfileToolsCardItemProps>();
</script>

<template>
  <UiLink
    class="tool flex h-8 items-center justify-center text-[2rem]"
    :href="tool.url"
    target="_blank"
    external
    :title="tool.alt"
    v-if="tool.url"
  >
    <iconify-icon :icon="tool.icon" />
  </UiLink>
  <div
    class="tool flex h-8 items-center justify-center text-[2rem]"
    :title="tool.alt"
    v-else
  >
    <iconify-icon :icon="tool.icon" />
  </div>
</template>
