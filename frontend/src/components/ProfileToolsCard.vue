<script setup lang="ts">
import { Tool } from "@/types/Tool.ts";
import { Vue3Marquee } from "@node_modules/vue3-marquee";

import ProfileToolsCardItem from "@components/ProfileToolsCardItem.vue";

interface ProfileToolsCardProps {
  tools: Tool[];
}

defineProps<ProfileToolsCardProps>();
</script>

<template>
  <UiCard body-class="overflow-hidden p-0 py-2" v-if="tools.length">
    <Vue3Marquee
      class="gradient-marquee h-full overflow-hidden"
      pause-on-hover
      clone
      :duration="tools.length * 3"
    >
      <ProfileToolsCardItem
        :tool="tool"
        class="mx-1"
        v-for="tool in tools"
        :key="tool.alt"
      />
    </Vue3Marquee>
  </UiCard>
</template>

<style scoped>
.gradient-marquee {
  mask-image: linear-gradient(
    90deg,
    rgb(0 0 0 / 0),
    rgb(0 0 0 / 1) 15%,
    rgb(0 0 0 / 1) 85%,
    rgb(0 0 0 / 0)
  );
}
</style>
