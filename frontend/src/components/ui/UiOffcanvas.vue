<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from "vue";
import { useScrollLock } from "@composables/scrollLock";

export interface UiOffcanvasProps {
  placement?: "start" | "end";
  headerClass?: string;
  bodyClass?: string;
  /** Renders in place instead of teleporting to the document body. */
  teleportDisabled?: boolean;
}

const { placement = "start", teleportDisabled = false } =
  defineProps<UiOffcanvasProps>();

const show = defineModel<boolean>({ default: false });

const emit = defineEmits<{ hidden: [] }>();

defineOptions({ inheritAttrs: false });

const enterFrom = computed(() =>
  placement === "end" ? "translate-x-full" : "-translate-x-full",
);

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape" && show.value) show.value = false;
};

onMounted(() => document.addEventListener("keydown", onKeydown));
onBeforeUnmount(() => document.removeEventListener("keydown", onKeydown));

useScrollLock(show);
</script>

<template>
  <Teleport to="body" :disabled="teleportDisabled">
    <Transition
      enter-active-class="transition-opacity duration-300"
      leave-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-1040 bg-black/50"
        @click="show = false"
      />
    </Transition>

    <Transition
      enter-active-class="transition-transform duration-300 ease-in-out"
      leave-active-class="transition-transform duration-300 ease-in-out"
      :enter-from-class="enterFrom"
      :leave-to-class="enterFrom"
      @after-leave="emit('hidden')"
    >
      <div
        v-if="show"
        class="fixed top-0 bottom-0 z-1045 flex max-w-full flex-col bg-surface bg-clip-padding shadow-overlay outline-none"
        :class="
          placement === 'end'
            ? 'right-0 border-l border-hairline'
            : 'left-0 border-r border-hairline'
        "
        v-bind="$attrs"
      >
        <div
          v-if="$slots.header"
          class="flex items-center justify-between border-b border-hairline p-3 pr-4"
          :class="headerClass"
        >
          <slot name="header" />
        </div>

        <div class="grow overflow-y-auto p-3 pr-4" :class="bodyClass">
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
