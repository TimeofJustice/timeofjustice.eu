<script setup lang="ts">
const show = defineModel<boolean>({ default: false });

/**
 * `height: auto` cannot be transitioned, so the element's measured height is
 * pinned for the duration of the animation and released again afterwards.
 */
const beforeEnter = (element: Element) => {
  (element as HTMLElement).style.height = "0";
};

const enter = (element: Element) => {
  const target = element as HTMLElement;

  target.style.height = `${target.scrollHeight}px`;
};

const afterEnter = (element: Element) => {
  (element as HTMLElement).style.height = "";
};

const beforeLeave = (element: Element) => {
  const target = element as HTMLElement;

  target.style.height = `${target.scrollHeight}px`;
  // Force a reflow so the browser animates from the pinned height.
  void target.offsetHeight;
};

const leave = (element: Element) => {
  (element as HTMLElement).style.height = "0";
};
</script>

<template>
  <Transition
    enter-active-class="overflow-hidden transition-[height] duration-350 ease-in-out"
    leave-active-class="overflow-hidden transition-[height] duration-350 ease-in-out"
    @before-enter="beforeEnter"
    @enter="enter"
    @after-enter="afterEnter"
    @before-leave="beforeLeave"
    @leave="leave"
  >
    <div v-show="show">
      <slot />
    </div>
  </Transition>
</template>
