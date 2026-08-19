<script setup lang="ts">
import { computed } from "vue";
import { useToast, type ToastPosition } from "@composables/toast";
import { TOAST_HIDDEN, TOAST_TRANSITION } from "./transitions";

const { toasts, remove } = useToast();

const POSITIONS: Record<ToastPosition, string> = {
  "top-start": "top-0 left-0 items-start",
  "top-center": "top-0 left-1/2 -translate-x-1/2 items-center",
  "top-end": "top-0 right-0 items-end",
  "middle-start": "top-1/2 left-0 -translate-y-1/2 items-start",
  "middle-center":
    "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 items-center",
  "middle-end": "top-1/2 right-0 -translate-y-1/2 items-end",
  "bottom-start": "bottom-0 left-0 items-start",
  "bottom-center": "bottom-0 left-1/2 -translate-x-1/2 items-center",
  "bottom-end": "bottom-0 right-0 items-end",
};

/**
 * The edge a toast travels from, and back out to. The ones pinned to a side
 * slide in horizontally; the ones centred on an edge come from that edge, and
 * the one in the middle of the screen has nowhere to come from and only fades.
 */
const OFFSETS: Record<ToastPosition, string> = {
  "top-start": "-translate-x-6",
  "top-center": "-translate-y-6",
  "top-end": "translate-x-6",
  "middle-start": "-translate-x-6",
  "middle-center": "",
  "middle-end": "translate-x-6",
  "bottom-start": "-translate-x-6",
  "bottom-center": "translate-y-6",
  "bottom-end": "translate-x-6",
};

/**
 * One stack per position, so toasts never overlap each other.
 *
 * Every position stays mounted, empty ones included: dropping them would take
 * the `TransitionGroup` with them, and a toast cannot animate in while its own
 * container is being created around it, nor animate out of one that is already
 * gone. An empty stack is a childless fixed box that nothing can click.
 */
const stacks = computed(() =>
  Object.keys(POSITIONS).map((position) => ({
    position: position as ToastPosition,
    toasts: toasts.filter((toast) => toast.position === position),
  })),
);
</script>

<template>
  <Teleport to="body">
    <div
      v-for="stack in stacks"
      :key="stack.position"
      class="pointer-events-none fixed z-1090 flex flex-col gap-2 p-3"
      :class="POSITIONS[stack.position]"
    >
      <TransitionGroup
        v-bind="TOAST_TRANSITION"
        :enter-from-class="`${TOAST_HIDDEN} ${OFFSETS[stack.position]}`"
        :leave-to-class="`${TOAST_HIDDEN} ${OFFSETS[stack.position]}`"
        move-class="transition-transform duration-300 ease-out"
      >
        <UiToast
          v-for="toast in stack.toasts"
          :key="toast.id"
          :variant="toast.variant"
          class="pointer-events-auto cursor-pointer transition duration-150 hover:brightness-110"
          @click="remove(toast.id)"
        >
          {{ toast.body }}
        </UiToast>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
