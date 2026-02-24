<script setup lang="ts">
import { computed, ref, watch } from "vue";
import TButton from "./TButton.vue";

interface TAlertProps {
  modelValue?: boolean;
  label?: string;
  type?: "info";
}

const { modelValue, type = "info" } = defineProps<TAlertProps>();
const emit = defineEmits<{ (e: "update:modelValue", value: boolean): void }>();

const visible = ref(modelValue ?? true);

watch(
  () => modelValue,
  (val) => {
    if (val !== undefined) visible.value = val;
  },
);

const close = () => {
  visible.value = false;
  emit("update:modelValue", false);
};

const variantClasses = computed(() => {
  const map = {
    info: "bg-info text-info-foreground",
  };

  return map[type ?? "info"];
});
</script>

<template>
  <transition
    name="fade-slide"
    enter-active-class="transition duration-200 ease-out"
    leave-active-class="transition duration-200 ease-in"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="visible"
      :class="[
        'p-3 ps-5 items-center leading-none rounded-2xl flex',
        variantClasses,
      ]"
      role="alert"
    >
      <span
        v-if="label"
        class="flex rounded-full bg-indigo-500 uppercase px-2 py-1 text-xs font-bold mr-3"
      >
        {{ label }}
      </span>

      <span class="text-left flex-auto">
        <slot />
      </span>

      <TButton circular type="tertiary" @click="close">
        <iconify-icon icon="ep:close-bold" />
      </TButton>
    </div>
  </transition>
</template>

<style scoped lang="scss">
/* optional: you could use Tailwind only, but leave scoped in case you want custom tweaks */
</style>
