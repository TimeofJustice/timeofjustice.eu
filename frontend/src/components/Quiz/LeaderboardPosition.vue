<script setup lang="ts">
import { ref, watch } from "vue";

interface LeaderboardPositionProps {
  name: string;
  url: string;
  score?: number;
}

const { score = 0 } = defineProps<LeaderboardPositionProps>();

const animatedScore = ref(score);
const duration = 500;

watch(
  () => score,
  (newScore) => {
    const start = animatedScore.value;
    const diff = newScore - start;
    const startTime = performance.now();

    function animate(now: number) {
      const progress = Math.min((now - startTime) / duration, 1);
      animatedScore.value = Math.round(start + diff * easeOutCubic(progress));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    }

    requestAnimationFrame(animate);
  },
);

function easeOutCubic(t: number) {
  return 1 - Math.pow(1 - t, 3);
}
</script>

<template>
  <div class="item">
    <BCard body-class="p-2 d-flex align-items-center gap-2" class="w-100">
      <BAvatar class="p-0 border border-2 border-black">
        <span class="b-avatar-img position-absolute">
          <img :src="url" />
        </span>
      </BAvatar>
      <div class="d-flex flex-grow-1 justify-content-between">
        <span>{{ name }}</span>
        <span>{{ animatedScore }}</span>
      </div>
    </BCard>
  </div>
</template>

<style scoped lang="scss"></style>
