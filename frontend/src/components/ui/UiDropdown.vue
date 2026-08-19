<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, useTemplateRef } from "vue";
import type { Size, Variant } from "./variants";

export interface UiDropdownProps {
  variant?: Variant;
  size?: Exclude<Size, "md">;
  /** Which edge of the toggle the menu lines up with. */
  align?: "start" | "end";
  /** Gap between toggle and menu, in pixels. */
  offset?: number | string;
  toggleClass?: string;
  menuClass?: string;
  /** Drops the toggle's look-and-feel classes in favour of `toggleClass`. */
  unstyled?: boolean;
}

const {
  variant = "secondary",
  align = "start",
  offset = 4,
} = defineProps<UiDropdownProps>();

const isOpen = ref(false);
const root = useTemplateRef<HTMLElement>("root");

const onDocumentPointerDown = (event: MouseEvent) => {
  if (!isOpen.value) return;
  if (root.value?.contains(event.target as Node)) return;

  isOpen.value = false;
};

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape") isOpen.value = false;
};

onMounted(() => {
  document.addEventListener("pointerdown", onDocumentPointerDown);
  document.addEventListener("keydown", onKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", onDocumentPointerDown);
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div ref="root" class="relative inline-block">
    <UiButton
      :variant="variant"
      :size="size"
      :unstyled="unstyled"
      class="whitespace-nowrap after:ml-[0.255em] after:inline-block after:border-t-[0.3em] after:border-r-[0.3em] after:border-b-0 after:border-l-[0.3em] after:border-t-current after:border-r-transparent after:border-l-transparent after:align-[0.255em] after:content-['']"
      :class="toggleClass"
      :aria-expanded="isOpen"
      @click="isOpen = !isOpen"
    >
      <slot name="button-content" />
    </UiButton>

    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="absolute top-full z-1000 min-w-40 rounded-md border border-black/15 bg-light bg-clip-padding py-2 text-left text-control text-dark"
        :class="[align === 'end' ? 'right-0' : 'left-0', menuClass]"
        :style="{ marginTop: `${offset}px` }"
        @click="isOpen = false"
      >
        <slot />
      </div>
    </Transition>
  </div>
</template>
