<script setup lang="ts">
interface DailyRewardProps {
  day: number;
  reward: number;
  overflow?: boolean;
  status: 'locked' | 'unlocked' | 'claimed';
}

defineProps<DailyRewardProps>();
</script>

<template>
  <div class="d-flex flex-column align-items-center gap-1 rounded-3 p-2" :class="{'col-2': !overflow, 'col-12': overflow, 'bg-grey-500': status === 'locked', 'bg-success': status === 'unlocked', 'bg-green-500': status === 'claimed'}">
    <span class="text-center">{{ $t('general.day') }} {{ day }}{{ overflow ? '+' : '' }}</span>
    <small>{{ reward }}</small>
  </div>
</template>
