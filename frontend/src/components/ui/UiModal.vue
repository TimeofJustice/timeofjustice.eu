<script setup lang="ts">
import { onBeforeUnmount, onMounted } from "vue";
import { useScrollLock } from "@composables/scrollLock";

export interface UiModalProps {
  size?: "sm" | "md" | "lg" | "xl";
  centered?: boolean;
  /** Keeps the dialog inside the viewport and scrolls the body instead. */
  scrollable?: boolean;
  headerClass?: string;
  bodyClass?: string;
  footerClass?: string;
  /** Blocks closing through the backdrop or the escape key. */
  static?: boolean;
}

const { size = "md", static: isStatic = false } = defineProps<UiModalProps>();

const show = defineModel<boolean>({ default: false });

const emit = defineEmits<{ hidden: [] }>();

const SIZES = {
  sm: "max-w-[300px]",
  md: "max-w-[500px]",
  lg: "max-w-[800px]",
  xl: "max-w-[1140px]",
};

const close = () => {
  if (isStatic) return;

  show.value = false;
};

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape" && show.value) close();
};

onMounted(() => document.addEventListener("keydown", onKeydown));
onBeforeUnmount(() => document.removeEventListener("keydown", onKeydown));

useScrollLock(show);
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div v-if="show" class="fixed inset-0 z-1050 bg-black/50" />
    </Transition>

    <Transition
      enter-active-class="transition duration-300 ease-out"
      leave-active-class="transition duration-150 ease-in"
      enter-from-class="-translate-y-12 opacity-0"
      leave-to-class="-translate-y-12 opacity-0"
      @after-leave="emit('hidden')"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-1055 overflow-x-hidden overflow-y-auto"
        @click.self="close"
      >
        <div
          class="mx-auto my-2 w-auto sm:my-7"
          :class="[
            SIZES[size],
            centered &&
              'flex min-h-[calc(100%-1rem)] items-center sm:min-h-[calc(100%-3.5rem)]',
            scrollable && 'h-[calc(100%-1rem)] sm:h-[calc(100%-3.5rem)]',
          ]"
          @click.self="close"
        >
          <div
            class="flex w-full flex-col rounded-lg border border-black/20 bg-dark-gray-600 bg-clip-padding"
            :class="scrollable && 'max-h-full overflow-hidden'"
          >
            <div
              v-if="$slots.header"
              class="flex shrink-0 items-center border-b border-black/17.5 p-4"
              :class="headerClass"
            >
              <slot name="header" />
            </div>

            <div
              class="p-4"
              :class="[bodyClass, scrollable && 'overflow-y-auto']"
            >
              <slot />
            </div>

            <div
              v-if="$slots.footer"
              class="flex shrink-0 items-center justify-end gap-2 border-t border-black/17.5 p-4"
              :class="footerClass"
            >
              <slot name="footer" />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
