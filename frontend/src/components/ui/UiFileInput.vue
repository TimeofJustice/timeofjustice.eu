<script setup lang="ts">
import { useUi } from "./cn";

export interface UiFileInputProps {
  accept?: string;
  /** `true` marks the field valid, `false` invalid, `null` leaves it neutral. */
  state?: boolean | null;
}

const { state = null } = defineProps<UiFileInputProps>();

const model = defineModel<File | null>();

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [
  "block w-full rounded-md border border-[#dee2e6] bg-body bg-clip-padding px-3 py-1.5 text-control leading-normal text-light transition-[border-color,box-shadow] duration-150 placeholder:text-accent focus:border-[#8a8b8c] focus:shadow-[0_0_0_0.25rem_rgb(20_22_25_/_0.25)] focus:outline-none",
  "px-0 py-0 file:mr-3 file:cursor-pointer file:border-0 file:bg-dark-gray-500 file:px-3 file:py-1.5 file:text-light",
  state === true && "border-success",
  state === false && "border-danger",
]);

const onChange = (event: Event) => {
  const { files } = event.target as HTMLInputElement;

  model.value = files?.[0] ?? null;
};
</script>

<template>
  <input
    type="file"
    :accept="accept"
    :class="ui"
    v-bind="rest"
    @change="onChange"
  />
</template>
