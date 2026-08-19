/**
 * Shared motion for the toasts, so a queued one and a standalone one come and
 * go the same way.
 *
 * The classes are handed to `<Transition>` as props rather than living in the
 * components, because `UiToaster` has to append a direction to them.
 */

/**
 * How a toast looks before it enters and after it leaves. Reduced motion keeps
 * the fade and drops everything that moves.
 */
export const TOAST_HIDDEN =
  "scale-95 opacity-0 motion-reduce:translate-none motion-reduce:scale-100";

/** Leaving is quicker than arriving: a toast on its way out is old news. */
export const TOAST_TRANSITION = {
  enterActiveClass: "transition duration-300 ease-out",
  leaveActiveClass: "transition duration-200 ease-in",
  enterFromClass: TOAST_HIDDEN,
  leaveToClass: TOAST_HIDDEN,
};
