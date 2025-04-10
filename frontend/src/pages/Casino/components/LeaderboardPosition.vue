<script setup lang="ts">
interface LeaderboardPosition {
  index: number;
  name: string;
  balance: number;
  highlighted?: boolean;
}

defineProps<LeaderboardPosition>();
</script>

<template>
  <div class="bg-grey-200 bg-opacity-50 px-3 py-2 d-flex align-items-center justify-content-between rounded border border-grey-100" :class="{ 'bg-primary text-white': highlighted }">
    <span class="fw-bold text-truncate">
      {{ index }}. {{ name }}
    </span>

    <div class="col-4 text-end">
      {{ balance }} TJTs
    </div>
  </div>
</template>
