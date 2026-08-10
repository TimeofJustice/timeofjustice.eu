<script setup lang="ts">
import { computed, ref } from "vue";

interface CircleProgressbarProps {
  max: number;
  value: number;
  stroke?: number;
}

const { max, value, stroke = 8 } = defineProps<CircleProgressbarProps>();

const radius = ref(48 - (stroke - 5) / 2);
const circumference = computed(() => 2 * Math.PI * radius.value);
const dashOffset = computed(() => circumference.value * (1 - value / max));
</script>

<template>
  <div class="circle-progressbar">
    <svg width="100%" height="100%" viewBox="-2 -2 104 104">
      <defs>
        <linearGradient id="gradient" x1="1" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="hsl(185, 75%, 50%)" />
          <stop offset="100%" stop-color="hsl(215, 85%, 60%)" />
        </linearGradient>
      </defs>
      <circle
        class="circle-bg"
        :cx="50"
        :cy="50"
        :r="radius"
        fill="none"
        :stroke-width="stroke"
      />
      <circle
        class="circle-bar"
        cx="50"
        cy="50"
        :r="radius"
        fill="none"
        :stroke-width="stroke"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        stroke-linecap="round"
        transform="rotate(-90 50 50)"
      />
      <text
        x="50"
        y="50"
        text-anchor="middle"
        dominant-baseline="middle"
        class="circle-text"
      >
        <tspan>
          <slot />
        </tspan>
      </text>
    </svg>
  </div>
</template>

<style scoped>
.circle-progressbar {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  user-select: none;
}

.circle-bg {
  stroke: var(--bs-primary);
  opacity: 0.3;
}

.circle-bar {
  stroke: url(#gradient);
  transition: stroke-dashoffset 0.3s linear;
}

.circle-text {
  font-weight: 600;
  fill: var(--bs-body-color);
}
</style>
