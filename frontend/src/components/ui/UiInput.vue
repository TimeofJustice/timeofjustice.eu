<script setup lang="ts" generic="T extends string | number | null | undefined">
import { computed, useAttrs } from "vue";
import { useUi } from "./cn";
import { FIELD, fieldState } from "./field";
import { RANGE, type Variant } from "./variants";

export interface UiInputProps {
  type?: string;
  /** `false` marks the field invalid; `true` and `null` leave it neutral. */
  state?: boolean | null;
  /** Why the value is wrong. Reaches the reader through the icon's tooltip. */
  error?: string;
  /** Colour of the thumb and of the filled track. Only a range reads this. */
  variant?: Variant;
}

const {
  type = "text",
  state = null,
  error = undefined,
  variant = undefined,
} = defineProps<UiInputProps>();

const model = defineModel<T>();

defineOptions({ inheritAttrs: false });

const attrs = useAttrs();

const isRange = computed(() => type === "range");

/**
 * A swatch is too small to hold an icon and a slider has no box to put one in,
 * so those two say "wrong" with colour alone.
 */
const boxed = computed(() => !isRange.value && type !== "color");

/**
 * How far along the track the value sits, as a 0…1 fraction. The track paints
 * its filled part from this, so the fill follows the thumb.
 */
const progress = computed(() => {
  const min = Number(attrs.min ?? 0);
  const max = Number(attrs.max ?? 100);
  const span = max - min;

  if (!Number.isFinite(span) || span <= 0) return 0;

  const ratio = (Number(model.value ?? min) - min) / span;

  return Number.isFinite(ratio) ? Math.min(Math.max(ratio, 0), 1) : 0;
});

const style = computed(() =>
  isRange.value ? { "--range-progress": String(progress.value) } : undefined,
);

const { ui, rest } = useUi(() =>
  isRange.value
    ? [
        // A slider is not a boxed field: it has no frame of its own, and its
        // colours live on the thumb and the track styled below.
        "range inline-block h-6 w-full appearance-none bg-transparent p-0 focus:outline-none",
        "[--range-thumb:var(--color-control-accent)]",
        variant && RANGE[variant],
        // Validity outranks the variant, an invalid slider has to read as one.
        state === false && "[--range-thumb:var(--color-danger)]",
      ]
    : [
        FIELD,
        type === "color" &&
          "h-[calc(1.5em+0.75rem+2px)] w-12 cursor-pointer p-1.5",
        fieldState(state, boxed.value),
      ],
);

const onInput = (event: Event) => {
  const { value } = event.target as HTMLInputElement;

  model.value = (
    isRange.value || type === "number" ? Number(value) : value
  ) as T;
};
</script>

<template>
  <!-- The wrapper is what the error icon hangs off. It is there whether or not
       the field is currently wrong, so turning invalid does not re-create the
       input and steal the focus from whoever is typing in it. -->
  <span class="relative block" :class="type === 'color' ? 'w-fit' : 'w-full'">
    <input
      :type="type"
      :value="model"
      :class="ui"
      v-bind="rest"
      :style="style"
      @input="onInput"
    />

    <UiFieldError v-if="boxed && state === false" :message="error" />
  </span>
</template>

<style scoped>
input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
}

input[type="color"]::-webkit-color-swatch {
  border: 0;
  border-radius: inherit;
}

input[type="color"]::-moz-color-swatch {
  border: 0;
  border-radius: inherit;
}

/* `--range-thumb` comes from the class list, so a variant can override it. */
.range {
  --range-thumb-active: color-mix(in srgb, var(--range-thumb) 30%, white);

  /*
   * Where the fill ends: the centre of the thumb, so the two line up instead of
   * the fill running ahead of it at one end and behind it at the other.
   */
  --range-fill-end: calc(0.5rem + (100% - 1rem) * var(--range-progress, 0));
}

.range:disabled {
  cursor: default;
  --range-thumb: var(--color-accent);
}

.range::-webkit-slider-thumb {
  width: 1rem;
  height: 1rem;
  margin-top: -0.25rem;

  appearance: none;
  background-color: var(--range-thumb);
  border: 0;
  border-radius: 1rem;

  transition:
    background-color 0.15s ease-in-out,
    box-shadow 0.15s ease-in-out;
}

.range::-moz-range-thumb {
  width: 1rem;
  height: 1rem;

  appearance: none;
  background-color: var(--range-thumb);
  border: 0;
  border-radius: 1rem;

  transition:
    background-color 0.15s ease-in-out,
    box-shadow 0.15s ease-in-out;
}

.range:active::-webkit-slider-thumb {
  background-color: var(--range-thumb-active);
}

.range:active::-moz-range-thumb {
  background-color: var(--range-thumb-active);
}

/* The slider keeps no outline, so the focus ring rides on the thumb. */
.range:focus-visible::-webkit-slider-thumb {
  box-shadow: 0 0 0 0.25rem
    color-mix(in srgb, var(--range-thumb) 30%, transparent);
}

.range:focus-visible::-moz-range-thumb {
  box-shadow: 0 0 0 0.25rem
    color-mix(in srgb, var(--range-thumb) 30%, transparent);
}

.range::-webkit-slider-runnable-track {
  width: 100%;
  height: 0.5rem;

  color: transparent;
  cursor: pointer;
  background-color: var(--color-track);
  background-image: linear-gradient(
    to right,
    var(--range-thumb) var(--range-fill-end),
    transparent var(--range-fill-end)
  );
  border-color: transparent;
  border-radius: 1rem;
}

.range::-moz-range-track {
  width: 100%;
  height: 0.5rem;

  color: transparent;
  cursor: pointer;
  background-color: var(--color-track);
  background-image: linear-gradient(
    to right,
    var(--range-thumb) var(--range-fill-end),
    transparent var(--range-fill-end)
  );
  border-color: transparent;
  border-radius: 1rem;
}
</style>
