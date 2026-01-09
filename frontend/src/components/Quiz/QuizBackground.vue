<script setup lang="ts">
import { ref, watch, onMounted } from "vue";

// Generate points that covers most of the area
const generateBigClipPath = (numPoints = 12) => {
  const base = [
    [0, 0],
    [100, 0],
    [100, 100],
    [0, 100],
    [50, 0],
    [100, 50],
    [50, 100],
    [0, 50],
  ];

  // Add random points near the edges and center
  while (base.length < numPoints) {
    const angle = Math.random() * 2 * Math.PI;
    const radius = 40 + Math.random() * 60;
    const cx = 50 + Math.cos(angle) * radius;
    const cy = 50 + Math.sin(angle) * radius;

    base.push([
      Math.max(0, Math.min(100, Math.round(cx))),
      Math.max(0, Math.min(100, Math.round(cy))),
    ]);
  }

  return base;
};

// Function to get a subtle random offset based on a seed
const subtleRandom = (seed: number, min = -2, max = 2) => {
  const x = Math.sin(seed) * 10000;
  return min + (x - Math.floor(x)) * (max - min);
};

// Generate clip path string from points with subtle random offsets
const getClipPath = (points: number[][], variant: number) => {
  return points
    .map(([x, y], i) => {
      const dx = subtleRandom(variant * 100 + i, -8, 8);
      const dy = subtleRandom(variant * 200 + i, -8, 8);
      return `${Math.max(0, Math.min(100, x + dx))}% ${Math.max(0, Math.min(100, y + dy))}%`;
    })
    .join(",\n    ");
};

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

const baseClipPoints = ref(generateBigClipPath(20));
const currentClipPath = ref("");
let variant = 0;

onMounted(() => {
  // Generate a random variant and points on mount
  baseClipPoints.value = generateBigClipPath(20);
  currentClipPath.value = getClipPath(baseClipPoints.value, variant);
});

watch(
  () => timer,
  (newTimer) => {
    if (newTimer < 10) {
      currentClipPath.value = getClipPath(baseClipPoints.value, ++variant);
    } else {
      currentClipPath.value = getClipPath(baseClipPoints.value, 0);
    }
  },
  { immediate: true },
);
</script>

<template>
  <div class="position-absolute top-0 start-0 bottom-0 end-0 blob-blur">
    <div
      class="h-100 blob"
      :class="{ 'blob-variant': timer < 10 }"
      :style="{ clipPath: `polygon(${currentClipPath})` }"
    ></div>
  </div>
</template>

<style scoped lang="scss">
.blob-blur {
  filter: blur(100px);
  opacity: 80%;
  user-select: none;
}

.blob {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    120deg,
    v-bind(primaryColor) 30%,
    v-bind(secondaryColor) 70%
  );
  background-size: 200% 200%;

  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 5s;
  transition-property: clip-path;

  animation:
    gradientShift 8s ease infinite,
    blobBreath 10s ease infinite;
}

.blob-variant {
  transition-duration: 0.5s;
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
