import { onBeforeUnmount, watch, type Ref } from "vue";

/** The app scrolls inside `.content-body`, not on the document. */
const getScrollContainer = (): HTMLElement =>
  document.querySelector(".content-body") ?? document.documentElement;

let locks = 0;

const lock = () => {
  if (locks++ === 0) getScrollContainer().style.overflow = "hidden";
};

const release = () => {
  if (locks > 0 && --locks === 0) getScrollContainer().style.overflow = "";
};

/**
 * Freezes the page behind an overlay for as long as `isOpen` stays true.
 * Nested overlays are counted, so closing one does not unfreeze the others.
 */
export const useScrollLock = (isOpen: Ref<boolean>) => {
  let held = false;

  const sync = (open: boolean) => {
    if (open && !held) {
      lock();
      held = true;
    } else if (!open && held) {
      release();
      held = false;
    }
  };

  watch(isOpen, sync, { immediate: true });

  onBeforeUnmount(() => sync(false));
};
