import type { ClassNameValue } from "tailwind-merge";

/** The shared look of input, textarea and file input. */
export const FIELD: ClassNameValue = [
  "block w-full rounded-md border border-field-edge bg-field bg-clip-padding px-3 py-1.5",
  "text-control leading-normal text-light placeholder:text-accent",
  "transition-[border-color,box-shadow] duration-150",
  "hover:border-field-edge-hover",
  "focus:border-field-edge-focus focus:shadow-[0_0_0_0.2rem_var(--color-focus-ring)] focus:outline-none",
  // A field that cannot be typed in does not react to being pointed at either.
  "disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:border-field-edge",
];

/**
 * What validity paints. Only a wrong value gets colour; a correct one keeps the
 * neutral edge. `padded` leaves room for the icon that explains the failure, so
 * controls without one pass `false`.
 */
export const fieldState = (
  state: boolean | null,
  padded = true,
): ClassNameValue =>
  state === false && [
    "border-danger hover:border-danger focus:border-danger",
    "focus:shadow-[0_0_0_0.2rem_var(--color-focus-ring-danger)]",
    padded && "pr-9",
  ];
