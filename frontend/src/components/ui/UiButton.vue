<script setup lang="ts">
import BaseLink from "@components/BaseLink.vue";
import { useUi } from "./cn";
import { BUTTON, BUTTON_ACTIVE, type Size, type Variant } from "./variants";

export interface UiButtonProps {
  variant?: Variant;
  size?: Exclude<Size, "md">;
  /** Fixed 36px box, for icon-only buttons. */
  square?: boolean;
  /** Like `square`, but round. Grows to 50px together with `size="lg"`. */
  circle?: boolean;
  active?: boolean;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
  /** Renders the button as a link to the given target. */
  to?: string;
  /** Leaves the SPA instead of navigating through Inertia. */
  external?: boolean;
  target?: string;
  /** Opens the target in the layout offcanvas instead of a full page visit. */
  offcanvasSource?: string;
  /** Drops every look-and-feel class so the caller can style the button itself. */
  unstyled?: boolean;
}

const {
  variant = "primary",
  size,
  square = false,
  circle = false,
  active = false,
  disabled = false,
  unstyled = false,
  type = "button",
  to,
} = defineProps<UiButtonProps>();

defineOptions({ inheritAttrs: false });

const RESET =
  "cursor-pointer text-center align-middle no-underline select-none disabled:pointer-events-none disabled:opacity-65 aria-disabled:pointer-events-none aria-disabled:opacity-65";

const { ui, rest } = useUi(() =>
  unstyled
    ? RESET
    : [
        RESET,
        "inline-block rounded-md border border-transparent px-3 py-1.5 text-control leading-normal",
        "transition-[color,background-color,border-color,box-shadow] duration-150",
        BUTTON[variant],
        active && BUTTON_ACTIVE[variant],

        size === "lg" && "rounded-lg px-4 py-2 text-control-lg",
        size === "sm" && "rounded-sm px-2 py-1 text-control-sm",

        // Icon-only buttons collapse to a fixed square, ignoring the padding above.
        (square || circle) &&
          "flex size-9 shrink-0 items-center justify-center p-0",
        circle && "rounded-full",
        circle && size === "lg" && "size-[50px] text-2xl",
      ],
);
</script>

<template>
  <BaseLink
    v-if="to"
    :href="to"
    :external="external"
    :target="target"
    :offcanvas-source="offcanvasSource"
    :aria-disabled="disabled || undefined"
    :class="ui"
    v-bind="rest"
  >
    <slot />
  </BaseLink>

  <button v-else :type="type" :disabled="disabled" :class="ui" v-bind="rest">
    <slot />
  </button>
</template>
