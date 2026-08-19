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

/** Tinted surface plus matching border and text, used by alerts. */
export const SUBTLE: Record<Variant, string> = {
  primary: "bg-primary/20 border-primary text-light",
  secondary: "bg-secondary/20 border-secondary text-light",
  tertiary: "bg-tertiary/20 border-tertiary text-light",
  ghost: "bg-transparent border-transparent text-light",
  success:
    "bg-success-subtle border-success-border-subtle text-success-text-emphasis",
  info: "bg-info-subtle border-info-border-subtle text-info-text-emphasis",
  warning:
    "bg-warning-subtle border-warning-border-subtle text-warning-text-emphasis",
  danger:
    "bg-danger-subtle border-danger-border-subtle text-danger-text-emphasis",
  light: "bg-light border-light text-black",
  dark: "bg-dark border-dark text-light",
  aquamarin: "bg-aquamarin/20 border-aquamarin text-light",
  "blue-grey": "bg-blue-grey/20 border-blue-grey text-light",
  brown: "bg-brown/20 border-brown text-light",
  "dark-green": "bg-dark-green/20 border-dark-green text-light",
  "dark-red": "bg-dark-red/20 border-dark-red text-light",
};
