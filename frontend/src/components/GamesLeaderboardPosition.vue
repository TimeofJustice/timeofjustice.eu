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
    class="flex items-center justify-between rounded-md border border-hairline px-4 py-2"
    :class="highlighted ? 'bg-blue-grey/40' : 'bg-card'"
  >
    <span class="truncate font-bold"> {{ index }}. {{ name }} </span>

    <div class="flex grow flex-row items-center justify-end gap-2">
      <div
        class="flex items-center gap-1 text-right whitespace-nowrap text-warning"
        v-if="streak > 0"
      >
        {{ streak }}
        <iconify-icon icon="bi:fire" />
      </div>

      <div class="text-right whitespace-nowrap">{{ balance }} TJTs</div>
    </div>
  </div>
</template>
