<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  ref,
  useTemplateRef,
  watch,
} from "vue";

export interface UiTooltipProps {
  /** Text for the pill. The `content` slot wins when both are given. */
  text?: string;
  /** Preferred side. Flips on its own when the window is in the way. */
  placement?: "top" | "bottom";
  /** Milliseconds the pointer has to rest before the pill appears. */
  delay?: number;
  /**
   * Let a long text break across lines instead of stretching the pill into a
   * strip. For labels a single line is right; for a sentence it is not.
   */
  wrap?: boolean;
  /**
   * Anchored mode: the element the pill points at, driven from outside.
   *
   * Leave it out to wrap a trigger with the default slot instead. Anchored mode
   * exists for the case where wrapping is the wrong shape — a grid of hundreds
   * of cells wants one tooltip that moves, not one component per cell.
   */
  anchor?: HTMLElement | null;
}

const {
  text,
  placement = "top",
  delay = 400,
  wrap = false,
  anchor,
} = defineProps<UiTooltipProps>();

/** Distance between the pill and the thing it points at. */
const GAP = 8;
/** How close the pill may get to the edge of the window. */
const EDGE = 8;
/** How close the caret may get to the pill's rounded corners. */
const CARET_INSET = 10;

const anchored = computed(() => anchor !== undefined);

const trigger = useTemplateRef<HTMLElement>("trigger");
const pill = useTemplateRef<HTMLElement>("pill");

const visible = ref(false);
const position = ref({ x: 0, y: 0, caret: 0, below: false });

/**
 * How long a pill lingers after the pointer leaves. Long enough that stepping
 * from one trigger to its neighbour — which fires a leave before the enter —
 * hands the pill over instead of restarting the dwell from nothing.
 */
const LEAVE_GRACE = 120;

let timer: ReturnType<typeof setTimeout> | undefined;

const targetRect = () =>
  (anchored.value ? anchor : trigger.value)?.getBoundingClientRect() ?? null;

/**
 * Puts the pill over its target, then pulls it back inside the window if it
 * would hang off an edge. The caret slides the other way by the same amount, so
 * it keeps pointing at the target rather than at the middle of the pill.
 *
 * Measured only once the pill is rendered, since its width is its content.
 */
const place = async () => {
  await nextTick();

  const box = targetRect();

  if (!pill.value || !box) return;

  const width = pill.value.offsetWidth;
  const half = width / 2;
  // Above by preference, unless the top of the window is in the way.
  const below =
    placement === "bottom" || box.top - pill.value.offsetHeight - GAP < EDGE;

  const centre = box.left + box.width / 2;
  const rightmost = Math.max(half + EDGE, window.innerWidth - half - EDGE);
  const x = Math.min(Math.max(centre, half + EDGE), rightmost);

  position.value = {
    x,
    y: below ? box.bottom + GAP : box.top - GAP,
    caret: Math.min(
      Math.max(centre - x + half, CARET_INSET),
      Math.max(CARET_INSET, width - CARET_INSET),
    ),
    below,
  };
};

/** Drops the pill at once, for when whatever it points at has moved away. */
const hideNow = () => {
  clearTimeout(timer);
  visible.value = false;
};

const hide = () => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    visible.value = false;
  }, LEAVE_GRACE);
};

/**
 * Waits out the dwell before appearing — but only the first time. Once a pill
 * is up, the next one follows the pointer straight away; waiting again for
 * every neighbour would make comparing two things a chore.
 */
const show = () => {
  clearTimeout(timer);

  if (visible.value) {
    place();
    return;
  }

  timer = setTimeout(() => {
    visible.value = true;
  }, delay);
};

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape") hideNow();
};

// A pill is pinned to the window, so anything that scrolls moves out from under
// it. Listened for only while one is actually up.
watch(visible, (open) => {
  if (open) {
    place();
    // Capture, so an inner scroller counts too — a scroll event does not bubble.
    window.addEventListener("scroll", hideNow, true);
    document.addEventListener("keydown", onKeydown);
    return;
  }

  window.removeEventListener("scroll", hideNow, true);
  document.removeEventListener("keydown", onKeydown);
});

watch(
  () => anchor,
  (element) => {
    if (!anchored.value) return;

    if (element) show();
    else hide();
  },
);

onBeforeUnmount(() => {
  clearTimeout(timer);
  window.removeEventListener("scroll", hideNow, true);
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <span
    v-if="!anchored"
    ref="trigger"
    class="inline-flex"
    @mouseenter="show"
    @mouseleave="hide"
    @focusin="show"
    @focusout="hide"
  >
    <slot />
  </span>

  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <span
        v-if="visible"
        ref="pill"
        role="tooltip"
        class="ui-tooltip"
        :class="[position.below && 'below', wrap && 'wrap']"
        :style="{
          left: `${position.x}px`,
          top: `${position.y}px`,
          '--caret': `${position.caret}px`,
        }"
      >
        <slot name="content">{{ text }}</slot>
      </span>
    </Transition>
  </Teleport>
</template>

<style scoped>
.ui-tooltip {
  /* Darker than a panel, because a tooltip is read on top of one. */
  --tooltip-surface: color-mix(
    in srgb,
    var(--color-dark-gray-900) 92%,
    transparent
  );

  position: fixed;
  z-index: 1060;

  display: flex;
  align-items: center;
  gap: 0.25rem;

  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;

  background: var(--tooltip-surface);
  color: var(--color-light);
  font-size: 0.8125rem;
  white-space: nowrap;

  /* Sits above the thing it describes and never eats a click meant for it. */
  box-shadow: var(--shadow-overlay);

  transform: translate(-50%, -100%);
  pointer-events: none;
}

.ui-tooltip.wrap {
  max-width: min(18rem, calc(100vw - 2rem));
  text-align: left;
  white-space: normal;
}

.ui-tooltip::after {
  content: "";

  position: absolute;
  top: 100%;
  left: var(--caret, 50%);

  border: 0.3rem solid transparent;
  border-top-color: var(--tooltip-surface);
  transform: translateX(-50%);
}

.ui-tooltip.below {
  transform: translate(-50%, 0);
}

.ui-tooltip.below::after {
  top: auto;
  bottom: 100%;

  border-top-color: transparent;
  border-bottom-color: var(--tooltip-surface);
}
</style>
