import { computed, useAttrs, type ComputedRef } from "vue";
import { extendTailwindMerge, type ClassNameValue } from "tailwind-merge";

/**
 * `tailwind-merge`, taught about the type scale in `theme.css`. Without this it
 * would read `text-h5` or `text-control-lg` as a colour and let it sit next to
 * a real font size instead of replacing it.
 */
export const cn = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [
        {
          text: [
            "base",
            "control",
            "control-sm",
            "control-lg",
            "h1",
            "h1-fluid",
            "h2",
            "h2-fluid",
            "h3",
            "h3-fluid",
            "h4",
            "h4-fluid",
            "h5",
            "h6",
            "display-1",
            "display-1-fluid",
          ],
        },
      ],
    },
  },
});

/**
 * Splits the incoming attributes so a component can merge its own styling with
 * whatever the caller passed: later classes win, and conflicting ones are
 * dropped rather than left to fight it out in the cascade.
 *
 * Components using this must set `inheritAttrs: false` and spread `rest`
 * themselves, otherwise the caller's `class` would be applied twice.
 */
export const useUi = (
  base: () => ClassNameValue,
): {
  ui: ComputedRef<string>;
  rest: ComputedRef<Record<string, unknown>>;
} => {
  const attrs = useAttrs();

  return {
    ui: computed(() => cn(base(), attrs.class as ClassNameValue)),
    rest: computed(() => {
      const { class: _ignored, ...rest } = attrs;
      return rest;
    }),
  };
};
