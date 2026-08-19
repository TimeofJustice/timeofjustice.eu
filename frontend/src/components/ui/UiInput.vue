<script setup lang="ts" generic="T extends string | number | null | undefined">
import { computed, useAttrs } from "vue";
import { useUi } from "./cn";
import { RANGE, type Variant } from "./variants";

export interface UiInputProps {
  type?: string;
  /** `true` marks the field valid, `false` invalid, `null` leaves it neutral. */
  state?: boolean | null;
  /** Colour of the thumb and of the filled track. Only a range reads this. */
  variant?: Variant;
}

const {
  type = "text",
  state = null,
  variant = undefined,
} = defineProps<UiInputProps>();

const model = defineModel<T>();

defineOptions({ inheritAttrs: false });

const attrs = useAttrs();

const isRange = computed(() => type === "range");

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
        state === true && "[--range-thumb:var(--color-success)]",
        state === false && "[--range-thumb:var(--color-danger)]",
      ]
    : [
        "block w-full rounded-md border border-[#dee2e6] bg-body bg-clip-padding px-3 py-1.5",
        "text-control leading-normal text-light placeholder:text-accent",
        "transition-[border-color,box-shadow] duration-150",
        "focus:border-[#8a8b8c] focus:shadow-[0_0_0_0.25rem_rgb(20_22_25_/_0.25)] focus:outline-none",
        type === "color" && "h-[calc(1.5em+0.75rem+2px)] w-12 p-1.5",
        state === true && "border-success",
        state === false && "border-danger",
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
  <input
    :type="type"
    :value="model"
    :class="ui"
    v-bind="rest"
    :style="style"
    @input="onInput"
  />
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
