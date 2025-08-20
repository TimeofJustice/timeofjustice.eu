<script setup lang="ts">
import { Tool } from "@/types/Tool.ts";

interface ProfileToolsCardItemProps {
  tool: Tool;
}

defineProps<ProfileToolsCardItemProps>();
</script>

<template>
  <BLink
    class="tool"
    :href="tool.url"
    target="_blank"
    :title="tool.alt"
    v-if="tool.url"
  >
    <iconify-icon :icon="tool.icon" />
  </BLink>
  <div class="tool" :title="tool.alt" v-else>
    <iconify-icon :icon="tool.icon" />
  </div>
</template>

<style scoped lang="scss">
.tool {
  height: 2rem;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
