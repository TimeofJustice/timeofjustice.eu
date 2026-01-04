<script setup lang="ts">
interface QuizBackgroundProps {
  primaryColor?: string;
  secondaryColor?: string;
  timer?: number;
}

const {
  primaryColor = "hsl(185, 75%, 50%)",
  secondaryColor = "hsl(215, 85%, 60%)",
  timer = 30,
} = defineProps<QuizBackgroundProps>();

import { ref, watch, onUnmounted } from "vue";

const blobVariant = ref(0);
let intervalId: number | undefined;

watch(
  () => timer,
  (newTimer) => {
    if (newTimer < 10) {
      if (!intervalId) {
        intervalId = window.setInterval(() => {
          blobVariant.value = (blobVariant.value + 1) % 2;
        }, 1000);
      }
    } else {
      blobVariant.value = 0;
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = undefined;
      }
    }
  },
  { immediate: true },
);

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});
</script>

<template>
  {{ timer }}
  <div
    class="position-absolute top-0 start-0 bottom-0 end-0 blob-blur"
    :style="`--primary-color: ${primaryColor}; --secondary-color: ${secondaryColor}`"
  >
    <div
      class="h-100 blob"
      :class="{ 'blob-variant': timer < 10 && blobVariant === 1 }"
    ></div>
  </div>
</template>

<style scoped lang="scss">
.blob-blur {
  filter: blur(100px);
  opacity: 80%;
  transition: transform 0.1s ease-out;
  user-select: none;
}

.blob {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    120deg,
    var(--primary-color) 30%,
    var(--secondary-color) 70%
  );
  background-size: 200% 200%;
  clip-path: polygon(
    64% 42%,
    43% 0%,
    83% 83%,
    66% 8%,
    55% 14%,
    27% 55%,
    42% 66%,
    81% 48%,
    4% 78%,
    46% 3%,
    3% 73%,
    81% 95%,
    3% 74%,
    97% 87%,
    71% 67%,
    72% 43%,
    86% 79%,
    31% 28%,
    89% 30%,
    100% 73%,
    53% 24%,
    67% 70%,
    46% 52%,
    95% 43%,
    23% 9%,
    75% 16%,
    80% 100%,
    14% 26%,
    58% 55%,
    25% 92%,
    33% 88%,
    69% 17%,
    91% 15%,
    5% 82%,
    41% 63%,
    68% 48%,
    7% 97%,
    95% 74%,
    33% 32%,
    19% 82%,
    89% 35%,
    13% 87%,
    93% 36%,
    23% 96%,
    10% 42%,
    14% 73%,
    96% 45%,
    20% 40%,
    72% 53%,
    23% 84%,
    29% 59%,
    90% 5%,
    33% 19%,
    88% 96%,
    97% 89%,
    36% 29%,
    91% 56%,
    46% 24%,
    9% 43%,
    23% 19%,
    2% 53%,
    64% 42%,
    16% 98%,
    42% 6%,
    5% 39%,
    0% 6%,
    89% 19%,
    18% 89%,
    28% 0%,
    1% 89%,
    37% 40%,
    61% 85%,
    60% 81%,
    57% 10%,
    23% 25%,
    99% 20%,
    44% 40%,
    12% 63%,
    55% 6%,
    25% 31%,
    28% 72%
  );
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 2.5s;
  transition-property: clip-path;
  animation:
    gradientShift 8s ease infinite,
    blobBreath 10s ease infinite;
}

.blob-variant {
  clip-path: polygon(
    68% 86%,
    53% 46%,
    83% 83%,
    100% 60%,
    18% 8%,
    33% 20%,
    42% 66%,
    78% 18%,
    44% 95%,
    53% 17%,
    61% 2%,
    44% 64%,
    77% 94%,
    24% 79%,
    8% 54%,
    72% 43%,
    61% 50%,
    27% 95%,
    12% 33%,
    100% 73%,
    41% 84%,
    67% 70%,
    78% 98%,
    87% 61%,
    19% 83%,
    0% 16%,
    40% 37%,
    54% 46%,
    58% 55%,
    2% 11%,
    98% 39%,
    64% 24%,
    91% 15%,
    20% 96%,
    79% 12%,
    41% 81%,
    79% 66%,
    60% 51%,
    16% 79%,
    18% 21%,
    89% 35%,
    60% 50%,
    19% 93%,
    48% 53%,
    10% 42%,
    70% 89%,
    82% 27%,
    82% 55%,
    23% 33%,
    95% 43%,
    29% 59%,
    17% 80%,
    46% 11%,
    22% 13%,
    82% 37%,
    59% 80%,
    85% 70%,
    45% 46%,
    9% 43%,
    31% 68%,
    64% 28%,
    64% 42%,
    36% 56%,
    37% 7%,
    90% 93%,
    63% 40%,
    40% 79%,
    18% 73%,
    86% 17%,
    64% 58%,
    51% 22%,
    61% 85%,
    56% 50%,
    99% 15%,
    52% 83%,
    99% 20%,
    80% 15%,
    78% 41%,
    55% 6%,
    89% 17%,
    28% 72%
  );
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes blobBreath {
  0% {
    transform: scale(1) rotate(0deg);
  }
  50% {
    transform: scale(1.04) rotate(3deg);
  }
  100% {
    transform: scale(1) rotate(0deg);
  }
}
</style>
