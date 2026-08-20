/**
 * The keyboard-focus ring.
 *
 * One ring for every interactive component — button, link, field, menu item —
 * because focus that changes shape as it moves through a page is focus that is
 * hard to follow. `focus-visible` keeps it off the pointer: a click leaves no
 * halo behind, a Tab always does.
 */
export const FOCUS_RING =
  "focus-visible:outline-none focus-visible:shadow-[0_0_0_0.2rem_var(--color-focus-ring)]";
