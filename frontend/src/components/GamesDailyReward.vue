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
  <div
    class="flex shrink-0 flex-col items-center gap-1 rounded-lg p-2"
    :class="{
      'w-1/6': !overflow,
      'w-full': overflow,
      'bg-dark-gray-800': status === 'locked',
      'bg-green-400': status === 'unlocked',
      'bg-green-700': status === 'claimed',
    }"
  >
    <span class="text-center">
      {{ $t("general.day") }} {{ day }}{{ overflow ? "+" : "" }}
    </span>
    <small>{{ reward }}</small>
  </div>
</template>
