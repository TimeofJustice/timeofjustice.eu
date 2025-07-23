<script setup lang="ts">
import { faFire } from "@fortawesome/free-solid-svg-icons";

interface LeaderboardPosition {
  index: number;
  name: string;
  balance: number;
  streak: number;
  highlighted?: boolean;
}

defineProps<LeaderboardPosition>();
</script>

<template>
  <div
    class="bg-grey-200 bg-opacity-50 px-3 py-2 d-flex align-items-center justify-content-between rounded border border-grey-100"
    :class="{ 'bg-primary text-white': highlighted }"
  >
    <span class="fw-bold text-truncate"> {{ index }}. {{ name }} </span>

    <div
      class="d-flex flex-row justify-content-end align-items-center gap-2 flex-grow-1"
    >
      <div class="text-end text-warning text-nowrap" v-if="streak > 0">
        {{ streak }}
        <font-awesome-icon :icon="faFire" />
      </div>

      <div class="text-end text-nowrap">{{ balance }} TJTs</div>
    </div>
  </div>
</template>
