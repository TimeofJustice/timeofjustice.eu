<script setup lang="ts">
interface GamesDailyRewardProps {
  day: number;
  reward: number;
  overflow?: boolean;
  status: "locked" | "unlocked" | "claimed";
}

defineProps<GamesDailyRewardProps>();
</script>

<template>
  <!-- Three states, one scale of brightness: a locked day is dim, the one that
       can be claimed is lit, and a claimed one keeps a trace of the colour. -->
  <div
    class="flex shrink-0 flex-col items-center gap-1 rounded-md border border-hairline p-2"
    :class="{
      'w-1/6': !overflow,
      'w-full': overflow,
      'bg-card text-accent': status === 'locked',
      'bg-success text-white': status === 'unlocked',
      'bg-success/25': status === 'claimed',
    }"
  >
    <span class="text-center">
      {{ $t("general.day") }} {{ day }}{{ overflow ? "+" : "" }}
    </span>
    <small>{{ reward }}</small>
  </div>
</template>
