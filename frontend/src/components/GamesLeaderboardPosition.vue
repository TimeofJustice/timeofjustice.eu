<script setup lang="ts">
interface GamesLeaderboardPosition {
  index: number;
  name: string;
  balance: number;
  streak: number;
  highlighted?: boolean;
}

defineProps<GamesLeaderboardPosition>();
</script>

<template>
  <div
    class="bg-opacity-50 px-3 py-2 d-flex align-items-center justify-content-between rounded border border-gray-800"
    :class="{ 'bg-blue-400': highlighted, 'bg-gray-900': !highlighted }"
  >
    <span class="fw-bold text-truncate"> {{ index }}. {{ name }} </span>

    <div
      class="d-flex flex-row justify-content-end align-items-center gap-2 flex-grow-1"
    >
      <div
        class="text-end text-warning text-nowrap d-flex align-items-center gap-1"
        v-if="streak > 0"
      >
        {{ streak }}
        <iconify-icon icon="bi:fire" />
      </div>

      <div class="text-end text-nowrap">{{ balance }} TJTs</div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
