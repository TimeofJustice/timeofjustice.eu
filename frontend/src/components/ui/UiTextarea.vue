<script setup lang="ts">
import { useUi } from "./cn";
import { FIELD, fieldState } from "./field";

export interface UiTextareaProps {
  rows?: number | string;
  /** `false` marks the field invalid; `true` and `null` leave it neutral. */
  state?: boolean | null;
  /** Why the value is wrong. Reaches the reader through the icon's tooltip. */
  error?: string;
}

const {
  rows = 3,
  state = null,
  error = undefined,
} = defineProps<UiTextareaProps>();

const model = defineModel<string>();

defineOptions({ inheritAttrs: false });

const { ui, rest } = useUi(() => [FIELD, fieldState(state)]);
</script>

<template>
  <!-- Wrapped like the input, and for the same reason: the icon needs somewhere
       to hang, and the field must not be re-created when it turns invalid. -->
  <span class="relative block w-full">
    <textarea v-model="model" :rows="rows" :class="ui" v-bind="rest" />

    <!-- A textarea is tall; the icon rides at the top rather than floating in
         the middle of the text. -->
    <UiFieldError
      v-if="state === false"
      :message="error"
      class="items-start pt-2"
    />
  </span>
</template>
