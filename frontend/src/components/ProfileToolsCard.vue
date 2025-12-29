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
  <BCard body-class="p-0 py-2 overflow-hidden" v-if="tools.length">
    <Vue3Marquee
      class="gradient-marquee h-100 overflow-hidden"
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
  </BCard>
</template>

<style scoped lang="scss">
.gradient-marquee {
  mask-image: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0),
    rgba(0, 0, 0, 1) 15%,
    rgba(0, 0, 0, 1) 85%,
    rgba(0, 0, 0, 0)
  );
}
</style>
