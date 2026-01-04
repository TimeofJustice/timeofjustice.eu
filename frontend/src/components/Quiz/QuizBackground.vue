<script setup lang="ts">
import { ref, watch } from "vue";

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

// Base clip-path points
const baseClipPath = [
  [64, 42],
  [43, 0],
  [83, 83],
  [66, 8],
  [55, 14],
  [27, 55],
  [42, 66],
  [81, 48],
  [4, 78],
  [46, 3],
  [3, 73],
  [81, 95],
  [3, 74],
  [97, 87],
  [71, 67],
  [72, 43],
  [86, 79],
  [31, 28],
  [89, 30],
  [100, 73],
  [53, 24],
  [67, 70],
  [46, 52],
  [95, 43],
  [23, 9],
  [75, 16],
  [80, 100],
  [14, 26],
  [58, 55],
  [25, 92],
  [33, 88],
  [69, 17],
  [91, 15],
  [5, 82],
  [41, 63],
  [68, 48],
  [7, 97],
  [95, 74],
  [33, 32],
  [19, 82],
  [89, 35],
  [13, 87],
  [93, 36],
  [23, 96],
  [10, 42],
  [14, 73],
  [96, 45],
  [20, 40],
  [72, 53],
  [23, 84],
  [29, 59],
  [90, 5],
  [33, 19],
  [88, 96],
  [97, 89],
  [36, 29],
  [91, 56],
  [46, 24],
  [9, 43],
  [23, 19],
  [2, 53],
  [64, 42],
  [16, 98],
  [42, 6],
  [5, 39],
  [0, 6],
  [89, 19],
  [18, 89],
  [28, 0],
  [1, 89],
  [37, 40],
  [61, 85],
  [60, 81],
  [57, 10],
  [23, 25],
  [99, 20],
  [44, 40],
  [12, 63],
  [55, 6],
  [25, 31],
  [28, 72],
];

const subtleRandom = (seed: number, min = -2, max = 2) => {
  // Deterministic pseudo-random for smoothness
  const x = Math.sin(seed) * 10000;
  return min + (x - Math.floor(x)) * (max - min);
};

const getClipPath = (variant: number) => {
  // Slightly perturb each point for a subtle effect
  return baseClipPath
    .map(([x, y], i) => {
      const dx = subtleRandom(variant * 100 + i, -10, 10);
      const dy = subtleRandom(variant * 200 + i, -10, 10);
      return `${x + dx}% ${y + dy}%`;
    })
    .join(",\n    ");
};

const clipPath = ref(getClipPath(0));
let variant = 0;

watch(
  () => timer,
  (newTimer) => {
    if (newTimer < 10) {
      clipPath.value = getClipPath(variant++);
    } else {
      clipPath.value = getClipPath(0);
    }
  },
  { immediate: true },
);
</script>

<template>
  {{ timer }}
  <div
    class="position-absolute top-0 start-0 bottom-0 end-0 blob-blur"
    :style="`--primary-color: ${primaryColor}; --secondary-color: ${secondaryColor}`"
  >
    <div
      class="h-100 blob"
      :class="{ 'blob-variant': timer < 10 }"
      :style="{ clipPath: `polygon(${clipPath})` }"
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
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 1s;
  transition-property: clip-path;
  animation:
    gradientShift 8s ease infinite,
    blobBreath 10s ease infinite;
}

.blob-variant {
  animation:
    blobPulse 6s ease infinite,
    gradientShift 8s ease infinite,
    blobBreath 10s ease infinite;
}

@keyframes blobPulse {
  0% {
    filter: brightness(1) saturate(1.1);
  }
  50% {
    filter: brightness(1.15) saturate(1.3);
  }
  100% {
    filter: brightness(1) saturate(1.1);
  }
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
