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
    class="d-flex flex-column align-items-center gap-1 rounded-3 p-2"
    :class="{
      'col-2': !overflow,
      'col-12': overflow,
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

<style scoped lang="scss"></style>
