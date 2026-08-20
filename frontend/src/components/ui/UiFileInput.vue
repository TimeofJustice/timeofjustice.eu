<script setup lang="ts">
import { useUi } from "./cn";
import { FIELD, fieldState } from "./field";

export interface UiFileInputProps {
  accept?: string;
  /** `false` marks the field invalid; `true` and `null` leave it neutral. */
  state?: boolean | null;
  /** Why the file is wrong. Reaches the reader through the icon's tooltip. */
  error?: string;
}

const { state = null, error = undefined } = defineProps<UiFileInputProps>();

const model = defineModel<File | null>();

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  FIELD,
  // The button is a raised panel sitting in the recessed field.
  "px-0 py-0 file:mr-3 file:cursor-pointer file:border-0 file:bg-surface-raised file:px-3 file:py-1.5 file:text-light file:transition-[filter] file:duration-150 hover:file:brightness-125",
  fieldState(state),
]);

const onChange = (event: Event) => {
  const { files } = event.target as HTMLInputElement;

  model.value = files?.[0] ?? null;
};
</script>

<template>
  <span class="relative block w-full">
    <input
      type="file"
      :accept="accept"
      :class="ui"
      v-bind="rest"
      @change="onChange"
    />

    <UiFieldError v-if="state === false" :message="error" />
  </span>
</template>
