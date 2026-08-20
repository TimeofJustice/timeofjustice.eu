/**
 * Shared colour vocabulary for the UI components.
 *
 * The values mirror the palette the site used before the Tailwind migration, so
 * every `variant="..."` keeps rendering the same colour it always did.
 */

export type Variant =
  | "primary"
  | "secondary"
  | "tertiary"
  | "ghost"
  | "success"
  | "info"
  | "warning"
  | "danger"
  | "light"
  | "dark"
  | "aquamarin"
  | "blue-grey"
  | "brown"
  | "dark-green"
  | "dark-red";

export type Size = "sm" | "md" | "lg";

/** Solid fill plus the text colour that reads on top of it. */
export const FILL: Record<Variant, string> = {
  primary: "bg-primary text-white",
  secondary: "bg-secondary text-white",
  tertiary: "bg-tertiary text-white",
  ghost: "bg-transparent text-light",
  success: "bg-success text-white",
  info: "bg-info text-black",
  warning: "bg-warning text-black",
  danger: "bg-danger text-white",
  light: "bg-light text-black",
  dark: "bg-dark text-white",
  aquamarin: "bg-aquamarin text-white",
  "blue-grey": "bg-blue-grey text-white",
  brown: "bg-brown text-white",
  "dark-green": "bg-dark-green text-white",
  "dark-red": "bg-dark-red text-white",
};

/** Idle, hover and pressed appearance of a button. */
export const BUTTON: Record<Variant, string> = {
  primary:
    "bg-primary text-white hover:bg-dark-gray-700 hover:text-white active:bg-dark-gray-900",
  secondary:
    "bg-secondary text-white hover:bg-dark hover:text-white active:bg-dark-gray-700",
  // Takes its colour from the surrounding text and only tints on interaction.
  tertiary:
    "border-0 bg-transparent text-inherit hover:bg-[color-mix(in_srgb,currentColor_12%,transparent)] active:bg-[color-mix(in_srgb,currentColor_20%,transparent)]",
  ghost: "bg-transparent text-light hover:text-accent active:text-light",
  success:
    "bg-success text-white hover:bg-success-hover hover:text-white active:bg-success-active",
  info: "bg-info text-black hover:bg-info-hover hover:text-black active:bg-info-active",
  warning:
    "bg-warning text-black hover:bg-warning-hover hover:text-black active:bg-warning-active",
  danger:
    "bg-danger text-white hover:bg-danger-hover hover:text-white active:bg-danger-active",
  light:
    "bg-light text-black hover:bg-light-hover hover:text-black active:bg-light-active",
  dark: "bg-dark text-white hover:bg-dark-hover hover:text-white active:bg-dark-active",
  aquamarin: "bg-aquamarin text-white hover:brightness-90 active:brightness-75",
  "blue-grey":
    "bg-blue-grey text-white hover:brightness-90 active:brightness-75",
  brown: "bg-brown text-white hover:brightness-90 active:brightness-75",
  "dark-green":
    "bg-dark-green text-white hover:brightness-90 active:brightness-75",
  "dark-red": "bg-dark-red text-white hover:brightness-90 active:brightness-75",
};

/** Pressed appearance, applied when a button is explicitly marked active. */
export const BUTTON_ACTIVE: Record<Variant, string> = {
  primary: "bg-dark-gray-900",
  secondary: "bg-dark-gray-700",
  tertiary: "bg-[color-mix(in_srgb,currentColor_20%,transparent)]",
  ghost: "text-light",
  success: "bg-success-active",
  info: "bg-info-active",
  warning: "bg-warning-active",
  danger: "bg-danger-active",
  light: "bg-light-active",
  dark: "bg-dark-active",
  aquamarin: "brightness-75",
  "blue-grey": "brightness-75",
  brown: "brightness-75",
  "dark-green": "brightness-75",
  "dark-red": "brightness-75",
};

/**
 * Colour of a range input's thumb and of the filled part of its track. The
 * pressed and focused shades are derived from it, so one variable is enough.
 */
export const RANGE: Record<Variant, string> = {
  primary: "[--range-thumb:var(--color-primary)]",
  secondary: "[--range-thumb:var(--color-secondary)]",
  tertiary: "[--range-thumb:var(--color-tertiary)]",
  ghost: "[--range-thumb:var(--color-accent)]",
  success: "[--range-thumb:var(--color-success)]",
  info: "[--range-thumb:var(--color-info)]",
  warning: "[--range-thumb:var(--color-warning)]",
  danger: "[--range-thumb:var(--color-danger)]",
  light: "[--range-thumb:var(--color-light)]",
  dark: "[--range-thumb:var(--color-dark)]",
  aquamarin: "[--range-thumb:var(--color-aquamarin)]",
  "blue-grey": "[--range-thumb:var(--color-blue-grey)]",
  brown: "[--range-thumb:var(--color-brown)]",
  "dark-green": "[--range-thumb:var(--color-dark-green)]",
  "dark-red": "[--range-thumb:var(--color-dark-red)]",
};

/**
 * Tinted surface plus matching border, used by alerts.
 *
 * Everything here is translucent: an alert is a note laid over the page, not a
 * second page. The colour lives in the border and in a wash of the fill, while
 * the text stays the same light the rest of the site is set in — a pale blue
 * box with near-black type would be the one bright rectangle on a dark site.
 */
export const SUBTLE: Record<Variant, string> = {
  primary: "border-hairline bg-primary/60 text-light",
  secondary: "border-hairline bg-secondary/50 text-light",
  tertiary: "border-hairline bg-tertiary/50 text-light",
  ghost: "border-transparent bg-transparent text-light",
  success: "border-success/40 bg-success/15 text-light",
  info: "border-info/40 bg-info/15 text-light",
  warning: "border-warning/40 bg-warning/15 text-light",
  danger: "border-danger/40 bg-danger/15 text-light",
  light: "border-light/40 bg-light/15 text-light",
  dark: "border-hairline bg-dark/70 text-light",
  aquamarin: "border-aquamarin/40 bg-aquamarin/20 text-light",
  "blue-grey": "border-blue-grey/40 bg-blue-grey/20 text-light",
  brown: "border-brown/40 bg-brown/20 text-light",
  "dark-green": "border-dark-green/40 bg-dark-green/20 text-light",
  "dark-red": "border-dark-red/40 bg-dark-red/20 text-light",
};
